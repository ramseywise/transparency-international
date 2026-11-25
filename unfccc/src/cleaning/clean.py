"""Clean the EU scope of the UNFCCC participant list (requirements D4-D8).

Run from the workspace root:

    uv run python -m cleaning.clean        clean the list and build the organisation table
    uv run python -m cleaning.clean csv    copy the raw workbook into one viewable CSV

The first part of this file holds the helpers: text normalisation, placeholders, sheet
loading, stable row ids. The second part is the cleaning run itself and its log.

Everything is deterministic. The raw workbook is opened read-only; original values are never
overwritten (cleaned columns sit beside them); output goes only to unfccc/data/processed/, the
cleaning log, and the viewable CSV. Individuals' names are never printed or logged.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

# Values that mean "nothing was entered" (compared after normalisation, case-insensitive).
PLACEHOLDERS = frozenset(
    {
        "", "-", "--", "---", ".", "..", "...", ",", "/", "//", "?", "??", "x", "xx",
        "n/a", "n.a.", "n.a", "na", "n a", "none", "nil", "null", "not applicable",
        "not available", "unknown", "tbc", "tbd", "to be confirmed", "to be determined",
    }
)

_QUOTES = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'", "´": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
}
_QUOTE_TABLE = str.maketrans(_QUOTES)
# Zero-width and invisible characters, soft hyphen, BOM, bidi marks.
_INVISIBLE = re.compile("[​‌‍⁠﻿­‎‏‪-‮]")
_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
_SPACES = re.compile(r"\s+")


def normalise_unicode(value: str) -> str:
    """NFKC, drop invisible/control characters, straighten curly quotes and dashes."""
    s = unicodedata.normalize("NFKC", value)
    s = _INVISIBLE.sub("", s)
    s = _CONTROL.sub(" ", s)
    return s.translate(_QUOTE_TABLE)


def collapse_whitespace(value: str) -> str:
    """Turn every run of whitespace (including non-breaking spaces) into one space and trim."""
    return _SPACES.sub(" ", value.replace("\xa0", " ")).strip()


def is_placeholder(value: str | None) -> bool:
    """True if the value is empty, a known placeholder, or has no letter or digit at all."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return True
    v = collapse_whitespace(str(value)).casefold()
    if v in PLACEHOLDERS:
        return True
    return not any(ch.isalnum() for ch in v)


def clean_text(value: str | None) -> str | None:
    """Full cleaning of one value: Unicode, whitespace, placeholder to None."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = collapse_whitespace(normalise_unicode(str(value)))
    return None if is_placeholder(s) else s


def clean_series_steps(raw: pd.Series) -> pd.DataFrame:
    """Apply the rules one at a time so each rule's effect can be counted.

    Returns columns: unicode, whitespace, final (placeholder applied). Missing stays missing.
    """
    present = raw.notna()
    step1 = raw.where(~present, raw.map(lambda v: normalise_unicode(v) if isinstance(v, str) else v))
    step2 = step1.where(~present, step1.map(lambda v: collapse_whitespace(v) if isinstance(v, str) else v))
    final = step2.map(lambda v: None if (isinstance(v, str) and is_placeholder(v)) else v)
    return pd.DataFrame({"unicode": step1, "whitespace": step2, "final": final})


def ascii_fold(value: str) -> str:
    """Remove diacritics (NFKD, drop combining marks). Keeps letters otherwise unchanged."""
    s = unicodedata.normalize("NFKD", value)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # Letters NFKD does not decompose.
    return s.translate(str.maketrans({"ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "đ": "d", "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "ı": "i"}))


_HONORIFICS = re.compile(
    r"^(?:(?:h\.?\s?e\.?|s\.?\s?e\.?|hon|mr|mrs|ms|miss|mme|mlle|m|dr|prof|sr|sra|srta|herr|frau|dott|dra|ing|dipl)\b\.?\s*)+",
    re.IGNORECASE,
)


def person_key(name: str | None, nominator: str | None) -> str | None:
    """Opaque hash used only to spot the same person twice. The name itself is never stored."""
    if not name:
        return None
    s = ascii_fold(normalise_unicode(name)).casefold()
    s = _HONORIFICS.sub("", s)
    tokens = sorted(t for t in re.split(r"[^a-z0-9]+", s) if t)
    if not tokens:
        return None
    payload = (nominator or "") + "|" + " ".join(tokens)
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


# --- Loading -------------------------------------------------------------------------------

RAW_COLUMNS = ["Nominated by", "Name", "Functional title", "Department", "Home organization", "Relation"]
SCOPE_SHEETS = ("Parties", "Party overflow")
BADGE_TYPES = {"Parties": "Party", "Party overflow": "Party overflow"}


def load_party_sheets(path: str | Path) -> pd.DataFrame:
    """Read the Parties and Party overflow sheets as strings, add `badge_type` and `sheet_row`.

    `sheet_row` is the 1-based position within the sheet's data rows (Excel row = sheet_row + 1).
    The workbook is opened read-only and never written.
    """
    sheets = pd.read_excel(path, sheet_name=list(SCOPE_SHEETS), dtype=str)
    frames = []
    for sheet in SCOPE_SHEETS:
        d = sheets[sheet]
        missing = [c for c in RAW_COLUMNS if c not in d.columns]
        if missing:
            raise ValueError(f"sheet {sheet!r} lacks columns {missing}")
        d = d[RAW_COLUMNS].copy()
        d.insert(0, "badge_type", BADGE_TYPES[sheet])
        d.insert(1, "sheet_row", range(1, len(d) + 1))
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


# --- Stable row id -------------------------------------------------------------------------


def add_row_ids(df: pd.DataFrame, columns: list[str], badge_col: str = "badge_type") -> pd.DataFrame:
    """Add `row_id`: hash of badge type + the raw field values + an occurrence counter.

    The id does not depend on row order or on cleaning rules, so it survives re-runs and
    re-sorting. Rows that are exact copies of each other get counters 0, 1, 2... in file order.
    """
    parts = df[badge_col].astype(str)
    for c in columns:
        parts = parts + "\x1f" + df[c].fillna("\x00").astype(str)
    base = parts.map(lambda p: hashlib.sha1(p.encode()).hexdigest()[:12])
    occurrence = base.groupby(base).cumcount()
    out = df.copy()
    out.insert(0, "row_id", "r_" + base + "_" + occurrence.astype(str))
    if not out["row_id"].is_unique:  # pragma: no cover - cannot happen given the counter
        raise AssertionError("row_id not unique")
    return out


# === The cleaning run ======================================================================

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "unfccc" / "data" / "raw" / "Physical%20LOP%20%28all%20registered%29.xlsx"
OUT = ROOT / "unfccc" / "data" / "processed"
CSV_OUT = ROOT / "unfccc" / "data" / "raw" / "unfcc-2026.csv"
LOG = ROOT / "unfccc" / "docs" / "working" / "cleaning-log.md"

# D7: the fixed list of 28 nominators, as spelled in the file.
EU27 = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia", "Finland",
        "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
        "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"]
EU_SCOPE = EU27 + ["European Union"]
# Extra spellings of country names that people type as an "organisation".
COUNTRY_ALIASES = ["Czech Republic", "Turkey", "Russia", "Korea", "South Korea", "UK", "USA", "United States",
                   "United States of America", "The Netherlands", "Holland", "Deutschland", "Italia", "Espana", "Polska"]
NOTEBOOK = {"total": 3821, "Party": 1381, "Party overflow": 2440}
TEXT_COLS = {"Nominated by": "nominated_by_clean", "Functional title": "title_clean", "Department": "department_clean",
             "Home organization": "home_org_clean", "Relation": "relation_clean"}


def examples(before: pd.Series, after: pd.Series, n: int = 3) -> list[tuple[str, str]]:
    """Up to n distinct (before, after) pairs where they differ, spread across the sorted list."""
    m = before.notna() & (before != after)
    pairs = sorted(set(zip(before[m], after[m].fillna("(empty)"))))
    if not pairs:
        return []
    step = max(1, len(pairs) // n)
    return pairs[::step][:n]


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def run_cleaning() -> None:
    """Clean the EU scope, build the organisation table, write the tables and the log."""
    # Imported here, not at the top: cleaning.orgs itself imports from this module.
    from cleaning.orgs import (
        AUTO_THRESHOLD,
        NO_ORG_REASONS,
        PROPOSE_CUTOFF,
        canonical_name,
        is_acronym_like,
        no_org_reason,
        normalise_org_name,
        pass1_assign,
        propose_merges,
        resolve_auto_merges,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    stats: dict = {}

    # ---- Load -------------------------------------------------------------------------------
    full = load_party_sheets(RAW)
    stats["rows_in_by_sheet"] = full["badge_type"].value_counts().to_dict()
    stats["rows_in"] = len(full)

    # Raw-file reconciliation reference, before any cleaning: trimmed nominator spelling only for matching.
    nominators_all = set(full["Nominated by"].dropna().str.strip())
    missing = [n for n in EU_SCOPE if n not in nominators_all]
    if missing:
        raise SystemExit(f"D7 failed: nominators missing from the file: {missing}")
    full["nominated_by_clean"] = clean_series_steps(full["Nominated by"])["final"]
    in_scope = full["nominated_by_clean"].isin(EU_SCOPE)
    df = full[in_scope].reset_index(drop=True)
    stats["rows_out_of_scope"] = int((~in_scope).sum())
    stats["rows_scoped"] = len(df)
    raw_counts = full[full["Nominated by"].isin(EU_SCOPE)].groupby(["Nominated by", "badge_type"]).size().unstack(fill_value=0)

    # ---- Row ids (from raw values, before cleaning) ----------------------------------------
    df = add_row_ids(df, RAW_COLUMNS)

    # ---- Text cleaning, rule by rule -----------------------------------------------------------
    rule_counts, ex = {}, {}
    for col, new in TEXT_COLS.items():
        steps = clean_series_steps(df[col])
        raw = df[col]
        rule_counts[col] = {
            "unicode": int((raw.notna() & (raw != steps["unicode"])).sum()),
            "whitespace": int((steps["unicode"].notna() & (steps["unicode"] != steps["whitespace"])).sum()),
            "placeholder_or_blank_to_empty": int((steps["whitespace"].notna() & steps["final"].isna()).sum()),
            "already_blank": int(raw.isna().sum()),
        }
        df[new] = steps["final"]
        if col == "Home organization":
            ex["unicode"] = examples(raw, steps["unicode"])
            ex["whitespace"] = examples(steps["unicode"], steps["whitespace"])
            ex["placeholder"] = examples(steps["whitespace"], steps["final"])
    stats["text_rules"] = rule_counts

    # ---- D6 duplicates (flag, never delete) --------------------------------------------------
    df["person_key"] = [person_key(n, c) for n, c in zip(df["Name"], df["nominated_by_clean"])]
    party_keys = set(df.loc[df["badge_type"] == "Party", "person_key"].dropna())
    df["dup_on_party_badge"] = (df["badge_type"] == "Party overflow") & df["person_key"].isin(party_keys)
    grp = df.groupby(["badge_type", "person_key"])["row_id"].transform("size")
    df["dup_within_sheet"] = df["person_key"].notna() & (grp > 1)
    df["counted_once"] = ~df["dup_on_party_badge"]
    stats["dup_on_party_badge"] = int(df["dup_on_party_badge"].sum())
    stats["dup_within_sheet"] = int(df["dup_within_sheet"].sum())
    stats["no_name_key"] = int(df["person_key"].isna().sum())

    # ---- Organisations, pass 1 ---------------------------------------------------------------
    country_keys = {normalise_org_name(x, strip_legal=False) for x in set(full["Nominated by"].dropna()) | set(COUNTRY_ALIASES)}
    df["no_org_reason"] = [no_org_reason(c, r, country_keys) for c, r in zip(df["home_org_clean"], df["Home organization"])]
    has_org = df["no_org_reason"].isna()
    df["org_key"] = pd.Series(pd.NA, index=df.index, dtype="object")
    df["org_scope"] = pd.Series(pd.NA, index=df.index, dtype="object")
    df["org_id"] = pd.Series(pd.NA, index=df.index, dtype="object")
    keys = df.loc[has_org, "home_org_clean"].map(normalise_org_name)
    if (keys == "").any():  # cannot happen: such values were coded as placeholders
        raise AssertionError("empty key for a value coded as an organisation")
    p1 = pass1_assign(keys, df.loc[has_org, "nominated_by_clean"])
    df.loc[has_org, ["org_key", "org_scope", "org_id"]] = p1
    stats["delegates_with_org"] = int(has_org.sum())
    stats["distinct_org_strings_clean"] = int(df.loc[has_org, "home_org_clean"].nunique())
    stats["distinct_org_strings_raw"] = int(df["Home organization"].nunique())
    stats["orgs_pass1"] = int(df["org_id"].nunique())
    stats["keys_pass1"] = int(df["org_key"].nunique())

    # Cleaned-name and legal-suffix rule counts (home org, distinct strings and rows)
    nosuf = df.loc[has_org, "home_org_clean"].map(lambda s: normalise_org_name(s, strip_legal=False))
    stats["rows_key_differs_from_name_nolegal"] = int((nosuf != keys).sum())
    ex["legal"] = examples(df.loc[has_org, "home_org_clean"].where(nosuf != keys), keys.where(nosuf != keys))

    # ---- Pass 1 org table ----------------------------------------------------------------------
    org_rows = df[has_org]
    g = org_rows.groupby("org_id")
    orgs = pd.DataFrame({
        "org_key": g["org_key"].first(),
        "org_scope": g["org_scope"].first(),
        "countries": g["nominated_by_clean"].agg(lambda s: sorted(set(s))),
        "spellings": g["home_org_clean"].agg(lambda s: Counter(s)),
        "raw_spellings": g["Home organization"].agg(lambda s: sorted(set(s))),
        "n_party": g["badge_type"].agg(lambda s: int((s == "Party").sum())),
        "n_party_overflow": g["badge_type"].agg(lambda s: int((s == "Party overflow").sum())),
    }).reset_index()
    orgs["canonical_name"] = orgs["spellings"].map(canonical_name)
    orgs["n_delegates"] = orgs["n_party"] + orgs["n_party_overflow"]
    ex["pass1"] = []
    multi = orgs[orgs["spellings"].map(len) > 1].sort_values("n_delegates", ascending=False)
    stats["pass1_orgs_with_several_spellings"] = len(multi)
    stats["pass1_spellings_collapsed"] = int(multi["spellings"].map(len).sum() - len(multi))
    for _, r in multi.iloc[[0, len(multi) // 2, len(multi) - 1]].iterrows() if len(multi) >= 3 else []:
        ex["pass1"].append((" / ".join(sorted(r["spellings"])), r["canonical_name"]))

    # ---- Pass 2 ------------------------------------------------------------------------------------
    pairs = propose_merges(orgs, PROPOSE_CUTOFF, AUTO_THRESHOLD)
    sizes = dict(zip(orgs["org_id"], orgs["n_delegates"]))
    mapping = resolve_auto_merges(pairs, sizes)
    stats["pairs_scored"] = len(pairs)
    stats["auto_merges"] = len(mapping)
    stats["proposed_left"] = int((pairs["decision"] == "propose").sum())
    df["org_id_pass1"] = df["org_id"]
    df["org_id"] = df["org_id"].map(lambda i: mapping.get(i, i) if isinstance(i, str) else i)
    df["org_merge_pass"] = df["org_id_pass1"].map(lambda i: "pass2_auto" if isinstance(i, str) and i in mapping else ("pass1" if isinstance(i, str) else None))
    stats["orgs_final"] = int(df["org_id"].nunique())

    # Final organisation table
    org_rows = df[df["org_id"].notna()]
    g = org_rows.groupby("org_id")
    final = pd.DataFrame({
        "countries": g["nominated_by_clean"].agg(lambda s: sorted(set(s))),
        "spellings": g["home_org_clean"].agg(lambda s: Counter(s)),
        "raw_spellings": g["Home organization"].agg(lambda s: sorted(set(s))),
        "n_delegates_party": g["badge_type"].agg(lambda s: int((s == "Party").sum())),
        "n_delegates_party_overflow": g["badge_type"].agg(lambda s: int((s == "Party overflow").sum())),
        "pass1_ids_merged": g["org_id_pass1"].agg(lambda s: sorted(set(s))),
        "scope": g["org_scope"].first(),
    }).reset_index()
    final["canonical_name"] = final["spellings"].map(canonical_name)
    final["n_delegates"] = final["n_delegates_party"] + final["n_delegates_party_overflow"]
    final["country_context"] = [c[0] if len(c) == 1 else "; ".join(c) for c in final["countries"]]
    final["country_scoped"] = final["scope"] != "*"
    final["merged_in_pass2"] = final["pass1_ids_merged"].map(len) > 1
    final["acronym_like"] = final["canonical_name"].map(is_acronym_like)
    final["clean_spellings"] = final["spellings"].map(lambda c: sorted(c))
    final["raw_spellings"] = final["raw_spellings"].map(list)
    out_orgs = final[["org_id", "canonical_name", "country_context", "countries", "country_scoped", "raw_spellings",
                      "clean_spellings", "n_delegates", "n_delegates_party", "n_delegates_party_overflow",
                      "pass1_ids_merged", "merged_in_pass2", "acronym_like"]].sort_values(["n_delegates", "canonical_name"], ascending=[False, True], ignore_index=True)
    stats["orgs_single_delegate"] = int((out_orgs["n_delegates"] == 1).sum())
    stats["orgs_acronym_like"] = int(out_orgs["acronym_like"].sum())

    # Auto-merge examples (organisation names only)
    nm = dict(zip(orgs["org_id"], orgs["canonical_name"]))
    auto_pairs = pairs[pairs["decision"] == "auto"].sort_values("score", ascending=False)
    ex["auto"] = [(f"{r.name_a} ({r.country})", f"{r.name_b}", r.score) for r in auto_pairs.itertuples()]

    # ---- Write outputs -------------------------------------------------------------------------------
    delegates = df.drop(columns=["org_scope", "org_id_pass1"]).rename(columns={"org_key": "org_key"})
    delegates.insert(delegates.columns.get_loc("org_id") + 1, "org_canonical_name",
                     delegates["org_id"].map(dict(zip(out_orgs["org_id"], out_orgs["canonical_name"]))))
    delegates.to_parquet(OUT / "delegates_eu.parquet", index=False)
    out_orgs.to_parquet(OUT / "organisations_eu.parquet", index=False)
    pairs.to_csv(OUT / "proposed_merges_eu.csv", index=False)

    # ---- Reconciliation --------------------------------------------------------------------------------
    rec = raw_counts.copy()
    out_counts = delegates.groupby(["nominated_by_clean", "badge_type"]).size().unstack(fill_value=0)
    rec = rec.reindex(EU_SCOPE).fillna(0).astype(int)
    out_counts = out_counts.reindex(EU_SCOPE).fillna(0).astype(int)
    for b in ("Party", "Party overflow"):
        for c in (rec, out_counts):
            if b not in c:
                c[b] = 0
    mismatch = int((rec[["Party", "Party overflow"]] != out_counts[["Party", "Party overflow"]]).sum().sum())
    stats["reconciliation_mismatches"] = mismatch
    if mismatch:
        raise SystemExit("per-delegation counts differ from the raw file")
    recon = pd.DataFrame({
        "Delegation": EU_SCOPE,
        "Raw Party": rec["Party"].values, "Out Party": out_counts["Party"].values,
        "Raw overflow": rec["Party overflow"].values, "Out overflow": out_counts["Party overflow"].values,
        "Counted once (D6)": delegates.groupby("nominated_by_clean")["counted_once"].sum().reindex(EU_SCOPE).fillna(0).astype(int).values,
    })
    recon.loc[len(recon)] = ["Total", recon["Raw Party"].sum(), recon["Out Party"].sum(), recon["Raw overflow"].sum(),
                             recon["Out overflow"].sum(), recon["Counted once (D6)"].sum()]
    stats["eu_total"] = int(len(delegates))
    stats["eu_by_badge"] = delegates["badge_type"].value_counts().to_dict()

    reasons = delegates["no_org_reason"].value_counts().reindex(list(NO_ORG_REASONS)).fillna(0).astype(int)
    stats["no_org_by_reason"] = reasons.to_dict()
    by_deleg = (delegates[delegates["no_org_reason"].notna()].groupby(["nominated_by_clean", "no_org_reason"]).size()
                .unstack(fill_value=0).reindex(EU_SCOPE).fillna(0).astype(int))
    for r in NO_ORG_REASONS:
        if r not in by_deleg:
            by_deleg[r] = 0
    by_deleg = by_deleg[list(NO_ORG_REASONS)]
    by_deleg["Total"] = by_deleg.sum(axis=1)
    by_deleg.insert(0, "Delegation", by_deleg.index)

    # Items that are organisation-like but unresolved (for the log): acronyms and country-scoped names
    acr = out_orgs[out_orgs["acronym_like"]]
    stats["acronym_delegates"] = int(acr["n_delegates"].sum())
    titled = delegates.loc[delegates["no_org_reason"].isin(["person_or_title", "generic", "country_name"]), ["home_org_clean", "no_org_reason"]]
    ex["no_org_values"] = sorted(set(zip(titled["no_org_reason"], titled["home_org_clean"])))

    write_log(stats, ex, recon, by_deleg, reasons, pairs, out_orgs)
    (OUT / "cleaning_stats.json").write_text(json.dumps(stats, indent=2, default=str))
    print(json.dumps({k: v for k, v in stats.items() if k != "text_rules"}, indent=1, default=str))


def fmt_ex(items: list, empty: str = "none in this data") -> str:
    if not items:
        return f"- {empty}\n"
    return "".join(f"- `{b}` -> `{a}`\n" for b, a in items)


def write_log(stats, ex, recon, by_deleg, reasons, pairs, out_orgs) -> None:
    from cleaning.orgs import AUTO_THRESHOLD, PROPOSE_CUTOFF

    tr = stats["text_rules"]
    ho = tr["Home organization"]
    auto = pairs[pairs["decision"] == "auto"]
    prop = pairs[pairs["decision"] == "propose"]
    lines = [
        "# Cleaning log: EU scope, Parties and Party overflow",
        "",
        "Generated by `unfccc/src/cleaning/clean.py`; re-running the script regenerates this file and the tables in `unfccc/data/processed/`. "
        "Requirement group D4 to D8. Raw file: `unfccc/data/raw/Physical%20LOP%20%28all%20registered%29.xlsx`, opened read-only. "
        "Pass 3 (web lookups for acronyms and translations) was not run.",
        "",
        "## Scope",
        "",
        f"- Sheets read: Parties and Party overflow, {stats['rows_in']:,} rows ({stats['rows_in_by_sheet'].get('Party', 0):,} and {stats['rows_in_by_sheet'].get('Party overflow', 0):,}).",
        f"- Scope rule (D7): `Nominated by` is one of the 27 EU member states or `European Union` (28 nominators). All 28 are present in the file (checked by the script, which stops if one is missing). Slovenia has no row on the overflow sheet; Romania has one.",
        f"- Rows outside the scope: {stats['rows_out_of_scope']:,}. Rows kept: {stats['rows_scoped']:,}.",
        "",
        "## Rules and what they changed",
        "",
        "Counts are rows of the in-scope table. Examples use organisation names only. Original columns are kept untouched; cleaned values sit in `*_clean` columns.",
        "",
        "| Rule | Applies to | Rows changed |",
        "|---|---|---|",
    ]
    for col in TEXT_COLS:
        t = tr[col]
        lines.append(f"| R1 Unicode: NFKC, remove invisible/control characters, straighten curly quotes and dashes | {col} | {t['unicode']:,} |")
        lines.append(f"| R2 Whitespace: non-breaking spaces to spaces, collapse runs, trim | {col} | {t['whitespace']:,} |")
        lines.append(f"| R3 Placeholder to empty (\"-\", \"//\", \"n/a\", no letters or digits ...) | {col} | {t['placeholder_or_blank_to_empty']:,} |")
    lines += [
        f"| (already empty in the raw file) | Home organization | {ho['already_blank']:,} |",
        f"| R4 Matching key: remove diacritics, case, punctuation; drop trailing legal forms (Ltd, GmbH, S.A., S.p.A., A/S ...) | Home organization (rows where the legal-form step alone changed the key) | {stats['rows_key_differs_from_name_nolegal']:,} |",
        f"| R5 Organisation id, pass 1: identical key = one organisation (government-body names and short acronyms only within the same nominating country) | delegates with an organisation | {stats['delegates_with_org']:,} rows into {stats['orgs_pass1']:,} organisations |",
        f"| R6 Pass 2 auto-merge (see below) | organisations | {stats['auto_merges']} organisations merged away |",
        f"| R7 Not an organisation: reason code, no id | Home organization | {int(reasons.sum()):,} rows |",
        f"| R8 Duplicate person flags (D6): same person on Party overflow and Party for the same nominator; flagged, not removed | delegates | {stats['dup_on_party_badge']:,} flagged; {stats['dup_within_sheet']:,} rows share a person within one sheet |",
        "",
        "### Before and after, organisation names only",
        "",
        "R1 Unicode (home organisation)", fmt_ex(ex["unicode"]).rstrip(),
        "",
        "R2 Whitespace", fmt_ex(ex["whitespace"]).rstrip(),
        "",
        "R3 Placeholder to empty", fmt_ex(ex["placeholder"]).rstrip(),
        "",
        "R4 Matching key (legal form dropped; keys are for matching, not display)", fmt_ex(ex["legal"]).rstrip(),
        "",
        "R5 Pass 1: spellings that share a key become one organisation (spellings -> canonical name)", fmt_ex(ex["pass1"]).rstrip(),
        "",
        "R6 Pass 2 auto-merges: see the list under Pass 2.",
        "",
        "R7: values coded as not an organisation (reason, value):",
        "".join(f"- {r}: `{v}`\n" for r, v in ex["no_org_values"][:200]).rstrip(),
        "",
        "## Reconciliation",
        "",
        f"Rows in (both sheets, all delegations): {stats['rows_in']:,}. Rows dropped as out of scope: {stats['rows_out_of_scope']:,} (nominator not among the 28). Rows out: {stats['eu_total']:,}. "
        f"No in-scope row was dropped by any rule; D6 duplicates are flagged in `dup_on_party_badge` and kept, so `counted_once` is False for {stats['dup_on_party_badge']:,} rows.",
        "",
        f"Comparison with the profile notebook: total {stats['eu_total']:,} (notebook 3,821), Party {stats['eu_by_badge'].get('Party')} (1,381), Party overflow {stats['eu_by_badge'].get('Party overflow')} (2,440).",
        f"The notebook's \"about 1,559 distinct organisation strings\" is its own normalised count; this script counts {stats['distinct_org_strings_raw']:,} distinct strings as typed and {stats['distinct_org_strings_clean']:,} after R1 to R3 (among rows with an organisation), and {stats['keys_pass1']:,} distinct matching keys after R4.",
        "",
        "Per delegation, raw file versus output (the script stops if any cell differs):",
        "",
        md_table(recon),
        "",
        "## Organisations",
        "",
        f"- Delegates with a usable organisation: {stats['delegates_with_org']:,} of {stats['eu_total']:,}.",
        f"- Organisations after pass 1: {stats['orgs_pass1']:,}. After pass 2 auto-merges: {stats['orgs_final']:,}. Organisations with a single delegate: {stats['orgs_single_delegate']:,}.",
        f"- Pass 1 collapsed {stats['pass1_spellings_collapsed']:,} spellings into {stats['pass1_orgs_with_several_spellings']:,} organisations that had several.",
        "- Matching across countries: keys are merged across nominating countries unless they name a government body (ministry, embassy, agency, parliament, office, region, council ...) or are a short single-word acronym such as BMF, which means different bodies in different countries. Those are matched only within one nominating country. Names starting European / EU / United Nations / International / World / Global are treated as one body whoever nominated the delegate.",
        "",
        "## Pass 2: similar names within the same nominating country",
        "",
        f"rapidfuzz `ratio` and `token_sort_ratio` on matching keys, pairs scored {PROPOSE_CUTOFF:.0f} or more within each country: {stats['pairs_scored']:,} pairs. "
        f"Auto-merge only when the plain `ratio` is at least {AUTO_THRESHOLD:.0f} and all guards pass: same numbers, same word count, exactly one word differs, that word has at least 6 letters and is a close spelling of the other. "
        "Word-order swaps are never automatic. A group is merged only if every pair in it passes (no chains). The threshold was set by reading the scored pairs: at and above it the pairs were typos, singular/plural and accent variants of the same body; below it, pairs began to include different entities (different ministries or institutes with similar names).",
        "",
        f"Auto-merged: {len(auto)} pairs. Left for review: {len(prop)} pairs, in `unfccc/data/processed/proposed_merges_eu.csv` with the score and a note on why each was not automatic.",
        "",
        "Auto-merges applied (score, name kept first; the second is merged into the organisation with more delegates):",
        "",
        "".join(f"- {s}: `{a}` and `{b}`\n" for a, b, s in ex["auto"]).rstrip() if ex["auto"] else "- none",
        "",
        "## Delegates with no usable organisation",
        "",
        "Reason codes: `blank` (empty in the raw file), `placeholder` (only punctuation or a placeholder word), `generic` (e.g. \"Independent\"), `country_name` (a country typed as the organisation), `person_or_title` (a job title typed instead of an organisation). No organisation is inferred from other fields in this pass.",
        "",
        md_table(pd.DataFrame({"Reason": reasons.index, "Delegates": reasons.values}).pipe(lambda d: pd.concat([d, pd.DataFrame({"Reason": ["Total"], "Delegates": [int(reasons.sum())]})]))),
        "",
        "By delegation:",
        "",
        md_table(by_deleg.reset_index(drop=True)),
        "",
        "## What could not be resolved",
        "",
        f"- {stats['orgs_acronym_like']:,} organisations are short all-capital names (for example ministry acronyms) covering {stats['acronym_delegates']:,} delegates. They are kept as typed and flagged `acronym_like` in the organisation table. Resolving them needs pass 3 (web lookups with the country as context), which was skipped.",
        "- Non-English and abbreviated spellings of one body (for example a ministry typed in the local language, in English and as an acronym) stay separate organisations. Pass 2 only catches near-identical spellings.",
        "- Generic body names such as an embassy or ministry with no country in the name are kept as organisations scoped to the nominating country. The country of the embassy itself is not known.",
        f"- {len(prop):,} proposed merges await a researcher's decision.",
        "- D6: the person key uses the normalised name (honorifics removed, word order ignored) plus the nominator. It cannot tell two different people with the same name from one person; flagged rows should be read as probable duplicates, not certain ones.",
        "- Delegates with a usable organisation string may still name a person's employer loosely (for example a contractor working for a ministry). Not inferred here.",
        "",
    ]
    LOG.write_text("\n".join(lines))


def workbook_to_csv() -> None:
    """Stack every sheet of the raw workbook into one viewable CSV.

    A `sheet` column records which sheet each row came from. Columns that a sheet lacks are
    left blank. Cell values are copied as text, unchanged.
    """
    sheets = pd.read_excel(RAW, sheet_name=None, dtype=str, keep_default_na=False)
    frames = []
    for name, df in sheets.items():
        df.insert(0, "sheet", name)
        frames.append(df)
        print(f"{name}: {len(df)} rows")
    combined = pd.concat(frames, ignore_index=True).fillna("")
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig so Excel shows accented names correctly
    combined.to_csv(CSV_OUT, index=False, encoding="utf-8-sig")
    print(f"total: {len(combined)} rows, {combined.shape[1]} columns -> {CSV_OUT.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if args == ["csv"]:
        workbook_to_csv()
    elif not args:
        run_cleaning()
    else:
        raise SystemExit("usage: python -m cleaning.clean [csv]")


if __name__ == "__main__":
    main()
