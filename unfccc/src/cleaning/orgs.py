"""Organisation matching.

Pass 1: exact match after normalisation (case, diacritics, punctuation, legal suffixes).
Pass 2: similar names within the same nominating country, with rapidfuzz. Proposed merges carry a
score; only very high-confidence, guarded pairs are applied automatically.

Wrongly merging two entities is worse than leaving one entity as two, so every rule here errs
towards keeping entities apart.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter

import pandas as pd
from rapidfuzz import fuzz, process

from cleaning.clean import ascii_fold

# --- Pass 1: normalisation -----------------------------------------------------------------

# Legal forms, matched as trailing token sequences (tokens are already lower-case, dots removed).
LEGAL_SUFFIXES: tuple[tuple[str, ...], ...] = tuple(
    tuple(s.split())
    for s in [
        "ltd", "limited", "llc", "llp", "lp", "plc", "inc", "incorporated", "corp", "corporation", "co",
        "company", "gmbh", "ag", "kg", "ug", "ohg", "mbh", "gmbh co kg", "e v", "ev", "eg",
        "sa", "s a", "sas", "sarl", "s a r l", "sl", "slu", "sau", "sgps", "spa", "s p a", "srl", "s r l",
        "snc", "sc", "scpa", "bv", "b v", "nv", "n v", "vof", "cv", "as", "a s", "asa", "ab", "aps", "a p s",
        "oy", "oyj", "ay", "sp z o o", "spzoo", "sp z oo", "zoo", "sro", "s r o", "spol s r o", "as", "kft",
        "zrt", "nyrt", "doo", "d o o", "dd", "d d", "ood", "ead", "eood", "ou", "uab", "sia", "ltda", "lda", "unipessoal lda",
        "sociedade anonima", "societe anonyme", "aktiengesellschaft",
    ]
)
_SUFFIX_SET = sorted(set(LEGAL_SUFFIXES), key=len, reverse=True)
_LEADING_STOP = {"the"}

_DOTTED_ABBR = re.compile(r"(?<![^\W_])(?:[^\W\d_]\.){2,}")  # s.p.a. / s.a. / b.v.
_A_SLASH_S = re.compile(r"\ba\s*/\s*s\b", re.IGNORECASE)


def _collapse_dotted(m: re.Match) -> str:
    return m.group(0).replace(".", "")


def normalise_org_name(raw: str | None, *, strip_legal: bool = True) -> str:
    """Matching key: ASCII-folded, lower-case, punctuation removed, trailing legal forms dropped.

    The key is for matching only; it is never shown as a name. Returns "" if nothing is left.
    If stripping a legal suffix would empty the key, the suffix is kept.
    """
    if not raw:
        return ""
    s = ascii_fold(raw).casefold()
    s = _A_SLASH_S.sub("as", s)
    s = _DOTTED_ABBR.sub(_collapse_dotted, s)
    s = s.replace("&", " and ")
    s = re.sub(r"[^\w\s]|_", " ", s)
    tokens = s.split()
    if tokens and tokens[0] in _LEADING_STOP and len(tokens) > 1:
        tokens = tokens[1:]
    if strip_legal:
        changed = True
        while changed and len(tokens) > 1:
            changed = False
            for suf in _SUFFIX_SET:
                n = len(suf)
                if len(tokens) > n and tuple(tokens[-n:]) == suf:
                    tokens = tokens[:-n]
                    changed = True
                    break
    return " ".join(tokens)


# --- Values that are not organisations -----------------------------------------------------

REASON_BLANK = "blank"
REASON_PLACEHOLDER = "placeholder"
REASON_GENERIC = "generic"
REASON_COUNTRY = "country_name"
REASON_PERSON_TITLE = "person_or_title"
NO_ORG_REASONS = (REASON_BLANK, REASON_PLACEHOLDER, REASON_GENERIC, REASON_COUNTRY, REASON_PERSON_TITLE)

GENERIC_KEYS = frozenset(
    normalise_org_name(x, strip_legal=False)
    for x in [
        "private", "private sector", "private company", "private business", "privat", "secteur prive",
        "self", "self employed", "selfemployed", "self-employed", "individual", "freelance", "freelancer",
        "independent", "independent consultant", "student", "consultant", "consultancy", "consulting",
        "media", "press", "journalist", "ngo", "ong", "civil society", "government", "gouvernement",
        "gobierno", "regierung", "governo", "business", "industry", "company", "unemployed", "retired",
        "other", "others", "delegate", "delegation", "party", "member", "observer", "no affiliation",
        "no organisation", "no organization", "none", "not affiliated", "n a",
    ]
)

# A person's job title typed where an organisation belongs.
_TITLE = re.compile(
    r"^(?:minister|ambassador|director|head|state secretary|secretary|deputy|counsell?or|attach[eé]|"
    r"professor|prof|dr|mr|mrs|ms|mme|herr|frau|ceo|cto|cfo|president|chair|chairman|chairwoman|chief|"
    r"officer|advis[eo]r|manager|senior|junior|expert|coordinator|spokesperson|negotiator)\b",
    re.IGNORECASE,
)


_INSTITUTION = re.compile(r"\b(?:school|university|college|institute|academy|hospital|foundation|centre|center)\b", re.IGNORECASE)


def no_org_reason(cleaned: str | None, raw: str | None, country_keys: frozenset[str] | set[str]) -> str | None:
    """Reason code if the value is not an organisation, else None.

    `cleaned` is the output of clean_text (None when blank/placeholder); `raw` is the original.
    `country_keys` are normalised names of Parties, for the "a country name" check.
    """
    if isinstance(cleaned, float) and pd.isna(cleaned):
        cleaned = None
    if cleaned is None:
        if raw is None or (isinstance(raw, float) and pd.isna(raw)) or not str(raw).strip():
            return REASON_BLANK
        return REASON_PLACEHOLDER
    key = normalise_org_name(cleaned, strip_legal=False)
    if not key:
        return REASON_PLACEHOLDER
    if key in GENERIC_KEYS:
        return REASON_GENERIC
    if key in country_keys:
        return REASON_COUNTRY
    if _TITLE.match(cleaned) and not _INSTITUTION.search(cleaned):
        return REASON_PERSON_TITLE
    return None


# --- Country scoping -----------------------------------------------------------------------

# Names of government bodies repeat across countries ("Ministry of Finance"), and short acronyms
# (BMF in Germany and Austria) collide. Such keys are only matched within one nominating country.
_GOV = re.compile(
    r"minist|ministr|ministerio|ministere|ministero|ministerium|bundesministerium|embass|ambassad|embajada|"
    r"botschaft|ambasciata|ambassade|consulat|konsulat|government|gouvernement|gobierno|regierung|governo|"
    r"parliament|parlament|bundestag|bundesrat|senate|department|agency|agentur|agence|municipal|city of|"
    r"county|region|kommun|gemeente|prefectur|council|permanent representation|representation|"
    r"ministry|ministerie|ministerstvo|ministarstvo|ministeri|ministrstvo|ministerul|ministerstwo|"
    r"ufficio|office|delegation|commission nationale|national"
)


_SUPRANATIONAL = re.compile(r"^(?:european|eu|united nations|un|international|world|global)\b")


def is_country_scoped(key: str) -> bool:
    """True if this key must not be matched across nominating countries."""
    if not key:
        return True
    if _SUPRANATIONAL.match(key):  # "European Parliament" is one body whoever nominated its staff
        return False
    if " " not in key and len(key) <= 6:  # short single-token acronym
        return True
    return bool(_GOV.search(key))


def make_org_id(key: str, scope: str) -> str:
    """Stable id from the matching key and its scope ('*' or the nominating country)."""
    return "org_" + hashlib.sha1(f"{key}|{scope}".encode()).hexdigest()[:12]


def pass1_assign(keys: pd.Series, nominators: pd.Series) -> pd.DataFrame:
    """Pass 1 for rows that do have an organisation key. Returns org_key, org_scope, org_id."""
    scoped = keys.map(is_country_scoped)
    scope = nominators.where(scoped, "*")
    ids = pd.Series([make_org_id(k, s) for k, s in zip(keys, scope)], index=keys.index)
    return pd.DataFrame({"org_key": keys, "org_scope": scope, "org_id": ids})


def is_acronym_like(name: str) -> bool:
    """Short all-capital single token, e.g. BMUKN. Candidates for acronym resolution (pass 3)."""
    return " " not in name and 2 <= len(name) <= 8 and name.upper() == name and any(c.isalpha() for c in name)


# --- Pass 2: similar names within one nominating country -----------------------------------

PROPOSE_CUTOFF = 88.0
# Chosen after inspecting scored pairs on the real data (see cleaning-log.md): only pairs this
# similar AND passing every guard below were verified, by eye, to be the same entity.
AUTO_THRESHOLD = 96.0

_DIGITS = re.compile(r"\d+")


def _tokens(key: str) -> list[str]:
    return key.split()


def _guards(a: str, b: str) -> tuple[bool, str]:
    """Return (ok_for_auto_merge, reason_if_not). Guards block look-alikes that differ by meaning."""
    if _DIGITS.findall(a) != _DIGITS.findall(b):
        return False, "numbers differ"
    ta, tb = _tokens(a), _tokens(b)
    if len(ta) != len(tb):
        return False, "different word count"
    diff = [(x, y) for x, y in zip(ta, tb) if x != y]
    if len(diff) != 1:
        return False, "more than one word differs" if diff else "identical tokens"
    x, y = diff[0]
    # The single differing word must be a near-identical spelling of the same word: long enough
    # that one edit is a typo, not a different word (Finland/Poland, north/south are short or far).
    if min(len(x), len(y)) < 6:
        return False, "differing word too short to be sure"
    if fuzz.ratio(x, y) < 85:
        return False, "differing word not a close spelling"
    return True, ""


def propose_merges(orgs: pd.DataFrame, cutoff: float = PROPOSE_CUTOFF, auto_threshold: float = AUTO_THRESHOLD) -> pd.DataFrame:
    """Score name pairs within each nominating country.

    `orgs` needs: org_id, org_key, canonical_name, countries (list of nominators), n_delegates.
    Returns one row per pair with a score and `decision` in {"auto", "propose"}.
    """
    by_country: dict[str, list[int]] = {}
    for i, countries in enumerate(orgs["countries"]):
        for c in countries:
            by_country.setdefault(c, []).append(i)

    keys = orgs["org_key"].tolist()
    seen: dict[tuple[str, str], dict] = {}
    for country, idxs in by_country.items():
        if len(idxs) < 2:
            continue
        sub = [keys[i] for i in idxs]
        ratio = process.cdist(sub, sub, scorer=fuzz.ratio, score_cutoff=cutoff, workers=1)
        tsort = process.cdist(sub, sub, scorer=fuzz.token_sort_ratio, score_cutoff=cutoff, workers=1)
        for a in range(len(sub)):
            for b in range(a + 1, len(sub)):
                s_ratio, s_sort = float(ratio[a][b]), float(tsort[a][b])
                score = max(s_ratio, s_sort)
                if score < cutoff:
                    continue
                ia, ib = idxs[a], idxs[b]
                id_a, id_b = orgs.iloc[ia]["org_id"], orgs.iloc[ib]["org_id"]
                pair = (id_a, id_b) if id_a < id_b else (id_b, id_a)
                if pair in seen:
                    continue
                ok, why = _guards(keys[ia], keys[ib])
                auto = ok and s_ratio >= auto_threshold  # plain ratio only: word-order swaps are never automatic
                seen[pair] = {
                    "country": country,
                    "org_id_a": id_a, "name_a": orgs.iloc[ia]["canonical_name"], "n_a": int(orgs.iloc[ia]["n_delegates"]),
                    "org_id_b": id_b, "name_b": orgs.iloc[ib]["canonical_name"], "n_b": int(orgs.iloc[ib]["n_delegates"]),
                    "score": round(score, 1), "score_ratio": round(s_ratio, 1), "score_token_sort": round(s_sort, 1),
                    "decision": "auto" if auto else "propose",
                    "note": "" if auto else (why or "below auto threshold"),
                }
    cols = ["country", "org_id_a", "name_a", "n_a", "org_id_b", "name_b", "n_b", "score", "score_ratio", "score_token_sort", "decision", "note"]
    out = pd.DataFrame(list(seen.values()), columns=cols)
    return out.sort_values(["decision", "score", "country", "name_a"], ascending=[True, False, True, True], ignore_index=True)


def resolve_auto_merges(pairs: pd.DataFrame, sizes: dict[str, int]) -> dict[str, str]:
    """Map merged org_id -> surviving org_id using only `auto` pairs.

    A connected group is merged only if every two members are themselves an auto pair (a clique),
    so chains A~B, B~C with A and C dissimilar are left for review. The survivor is the member
    with the most delegates (ties: smallest id).
    """
    auto = pairs[pairs["decision"] == "auto"]
    adj: dict[str, set[str]] = {}
    for a, b in zip(auto["org_id_a"], auto["org_id_b"]):
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    mapping: dict[str, str] = {}
    visited: set[str] = set()
    for start in sorted(adj):
        if start in visited:
            continue
        comp, stack = set(), [start]
        while stack:
            n = stack.pop()
            if n in comp:
                continue
            comp.add(n)
            stack.extend(adj[n] - comp)
        visited |= comp
        if all(comp - {m} <= adj[m] for m in comp):
            survivor = sorted(comp, key=lambda m: (-sizes.get(m, 0), m))[0]
            for m in comp:
                if m != survivor:
                    mapping[m] = survivor
        else:
            pairs.loc[pairs["org_id_a"].isin(comp) & pairs["org_id_b"].isin(comp) & (pairs["decision"] == "auto"), ["decision", "note"]] = ["propose", "group not fully similar (chain)"]
    return mapping


def canonical_name(spellings: Counter) -> str:
    """Most common raw spelling; ties go to the one with most letters, then alphabetical."""
    return sorted(spellings.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0]))[0][0]


# --- "i.A." (im Auftrag, on behalf of) -----------------------------------------------------

# "UBA i.A. BMUKN" = a delegate employed by UBA, attending on behalf of BMUKN. The employer is
# the organisation; the body acted for is kept apart. Matches "i.A.", "i.A", "i. A." between
# words, case-insensitive, and nothing inside a word (so "Via" or "Asia" are untouched).
_IA = re.compile(r"(?:^|\s)i\.\s?a\.?(?=\s)\s*", re.IGNORECASE)


def split_acting_for(value: str | None) -> tuple[str | None, str | None]:
    """Split "<employer> i.A. <principal>" into (employer, principal).

    A bare "i.A. <principal>" gives (None, principal): the employer is not given, so the
    organisation is unresolved; it must not be read as the principal. Values without "i.A."
    come back unchanged with principal None.
    """
    if not value:
        return value, None
    m = _IA.search(value)
    if not m:
        return value, None
    employer = value[: m.start()].strip(" -,;/") or None
    principal = value[m.end():].strip(" -,;/") or None
    return employer, principal
