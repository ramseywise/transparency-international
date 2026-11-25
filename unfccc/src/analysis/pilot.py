"""Draft draws for the codebook test: candidates for the fixed test set, and the pilot sample.

Written before the proposal is approved, at Ramsey's request (decisions.md, 2026-11-24,
"Draft work before the proposal is approved"). Nothing here is approved; the outputs go to
data/processed/draft-codebook/ and do not enter the proposal, the report or numbers.md.

* hard_case_cue: what an organisation's name suggests about the hard cases of codebook
  section 4, from the name alone, before any look-up. A cue picks cases to look at; it is
  never a label.
* test_set_candidates: up to 50 organisations for the fixed test set (decisions 28 and 39),
  spread over the hard-case cues and the name cues, for the expert to approve or replace.
* draw_pilot: the pilot of decision 40. 50 drawn at random from the EU and Member State
  delegations, with the draw recorded, plus up to 25 hard-case candidates, reported apart.
  Test-set candidates and the 20 feasibility organisations are kept out of both.

Run: uv run python -I -m analysis.pilot
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import feasibility

STUDY = Path(__file__).resolve().parents[2]
DERIVED = STUDY / "data" / "processed"
OUT = DERIVED / "draft-codebook"

SEED = 20261125  # a new seed, not the feasibility test's
PILOT_RANDOM = 50
PILOT_HARD_MAX = 25
HARD_PER_CUE = 3  # at most this many hard cases of one kind in the pilot
TEST_SET_SIZE = 50
TEST_PER_HARD_CUE = 3

# Name cues for the hard cases of codebook section 4, in the order they are tried. Several
# languages, because the lists are. Order matters: "development bank" before "bank".
HARD_CASE_CUES: dict[str, re.Pattern] = {
    "parliament": re.compile(
        r"\b(parliament|parlament|bundestag|bundesrat|assembl[ée]e nationale|s[ée]nat|senate|"
        r"tweede kamer|eerste kamer|sejm|riksdag|folketing|eduskunta|camera dei deputati|"
        r"congreso de los diputados|oireachtas|european parliament)\b", re.I),
    "trade_union": re.compile(
        r"\b(trade union|union of workers|gewerkschaft|syndicat|sindacato|sindicato|"
        r"vakbond|fagforbund|confederation of trade unions|\bdgb\b|\betuc\b|\bituc\b)", re.I),
    "public_law_chamber": re.compile(
        r"\b(chamber of agriculture|landwirtschaftskammer|arbeiterkammer|chamber of labour|"
        r"wirtschaftskammer|chambre d'agriculture|chambre des m[ée]tiers|handwerkskammer)\b", re.I),
    "private_law_chamber": re.compile(
        r"\b(chamber of commerce|handelskammer|chambre de commerce|camera di commercio|"
        r"c[áa]mara de comercio|ihk|kamer van koophandel)\b", re.I),
    "public_development_bank": re.compile(
        r"\b(development bank|investment bank|f[öo]rderbank|kfw|\beib\b|\bebrd\b|"
        r"banque publique d'investissement|bpifrance|cassa depositi)\b", re.I),
    "development_agency": re.compile(
        r"\b(development agency|agence fran[çc]aise de d[ée]veloppement|\bgiz\b|\bafd\b|"
        r"enabel|\bsida\b|cooperation agency|entwicklungsagentur)\b", re.I),
    "municipal_utility": re.compile(
        r"\b(stadtwerke|municipal utility|utility company|regie|waterschap|"
        r"municipal energy|gemeindewerke)\b", re.I),
    "cooperative": re.compile(
        r"\b(co-?operative|cooperativa|coop[ée]rative|genossenschaft|co[öo]peratie|"
        r"osuuskunta|andelsselskab)\b", re.I),
    "company_foundation": re.compile(
        r"\b(foundation|stiftung|fondation|fondazione|fundaci[óo]n|stichting|fundacja)\b", re.I),
    "trade_association": re.compile(
        r"\b(association|federation|f[ée]d[ée]ration|verband|bundesverband|confederation|"
        r"council of|alliance|vereniging|asociaci[óo]n|associazione|industry body|"
        r"business ?europe|eurelectric|eurogas)\b", re.I),
    "consultancy_or_law_firm": re.compile(
        r"\b(consult\w*|advisory|advisors?|advisers?|law firm|llp|rechtsanw[äa]lte|avocats|"
        r"attorneys|solicitors|partners)\b", re.I),
}


def hard_case_cue(name: str) -> str:
    """The first hard-case cue the name matches, or 'none'. From the name only."""
    for cue, pattern in HARD_CASE_CUES.items():
        if pattern.search(name or ""):
            return cue
    return "none"


def build_table(orgs: pd.DataFrame, delegates: pd.DataFrame) -> pd.DataFrame:
    table = feasibility.list_fields(orgs, delegates)
    table["hard_case_cue"] = [hard_case_cue(n) for n in table["canonical_name"]]
    return table.sort_values("org_id").reset_index(drop=True)


def feasibility_ids(table: pd.DataFrame) -> set[str]:
    """The 20 organisations of the feasibility test, redrawn from its recorded seed."""
    return set(feasibility.draw_sample(table)["org_id"])


def _pick(pool: pd.DataFrame, k: int, rng: np.random.Generator) -> pd.DataFrame:
    pool = pool.sort_values("org_id")
    idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
    return pool.iloc[np.sort(idx)]


def test_set_candidates(table: pd.DataFrame, exclude: set[str], seed: int = SEED,
                        size: int = TEST_SET_SIZE, per_hard_cue: int = TEST_PER_HARD_CUE
                        ) -> pd.DataFrame:
    """Up to `size` candidates: `per_hard_cue` for each hard-case cue, then the rest spread
    evenly over the name cues among organisations with no hard-case cue."""
    rng = np.random.default_rng(seed)
    pool = table[~table["org_id"].isin(exclude)]
    parts = []
    for cue in sorted(HARD_CASE_CUES):
        part = _pick(pool[pool["hard_case_cue"] == cue], per_hard_cue, rng).copy()
        part["why"] = "hard case: " + cue
        parts.append(part)
    chosen = pd.concat(parts)
    rest = pool[(pool["hard_case_cue"] == "none") & ~pool["org_id"].isin(chosen["org_id"])]
    cues = sorted(rest["name_cue"].unique())
    left = max(size - len(chosen), 0)
    for i, cue in enumerate(cues):
        k = left // len(cues) + (1 if i < left % len(cues) else 0)
        part = _pick(rest[rest["name_cue"] == cue], k, rng).copy()
        part["why"] = "name cue: " + cue
        parts.append(part)
    out = pd.concat(parts, ignore_index=True).head(size)
    out.insert(0, "case", [f"T{i + 1:02d}" for i in range(len(out))])
    return out


def draw_pilot(table: pd.DataFrame, exclude: set[str], seed: int = SEED,
               n_random: int = PILOT_RANDOM, hard_max: int = PILOT_HARD_MAX,
               per_cue: int = HARD_PER_CUE) -> tuple[pd.DataFrame, dict]:
    """The random 50 and up to 25 hard-case candidates, and a record of the draw."""
    rng = np.random.default_rng(seed + 1)  # its own stream, so the test set does not move it
    frame = table[~table["org_id"].isin(exclude)].sort_values("org_id")
    random_part = _pick(frame, n_random, rng).copy()
    random_part["part"] = "random"
    rest = frame[~frame["org_id"].isin(random_part["org_id"]) & (frame["hard_case_cue"] != "none")]
    hard = []
    for cue in sorted(HARD_CASE_CUES):
        hard.append(_pick(rest[rest["hard_case_cue"] == cue], per_cue, rng))
    hard_part = pd.concat(hard).sort_values(["hard_case_cue", "org_id"]).head(hard_max).copy()
    hard_part["part"] = "hard case (reported apart)"
    pilot = pd.concat([random_part, hard_part], ignore_index=True)
    pilot.insert(0, "case", [f"P{i + 1:02d}" for i in range(len(pilot))])
    record = {
        "drawn": date.today().isoformat(),
        "seed": seed,
        "rng": "numpy default_rng(seed + 1), choice without replacement, frame sorted by org_id",
        "frame": "organisations_eu.parquet: organisations on the EU and Member State delegations",
        "frame_size": int(len(table)),
        "excluded": int(len(table) - len(frame)),
        "excluded_why": "fixed test set candidates and the 20 feasibility organisations",
        "random": int(len(random_part)),
        "hard_cases": int(len(hard_part)),
        "hard_cases_by_cue": {k: int(v) for k, v in hard_part["hard_case_cue"].value_counts().sort_index().items()},
        "status": "draft; binds nothing; the lead researcher may replace the hard cases",
    }
    return pilot, record


COLUMNS = ["case", "org_id", "canonical_name", "country_context", "name_cue", "hard_case_cue"]


def main(derived: Path = DERIVED, out: Path = OUT) -> dict:
    orgs, delegates = feasibility.load(derived)
    table = build_table(orgs, delegates)
    feas = feasibility_ids(table)
    tests = test_set_candidates(table, exclude=feas)
    pilot, record = draw_pilot(table, exclude=feas | set(tests["org_id"]))
    out.mkdir(parents=True, exist_ok=True)
    tests[COLUMNS + ["why"]].to_csv(out / "test_set_candidates.csv", index=False)
    pilot[COLUMNS + ["part"]].to_csv(out / "pilot_draw.csv", index=False)
    (out / "pilot_draw.json").write_text(json.dumps(record, indent=1))
    return {"test_set_candidates": len(tests), **record}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))


# --- The codebook's own test (codebook skill, step 2) --------------------------------------
# 20 organisations chosen to be awkward, used to find rules that give no clear answer. They
# are drawn from outside the feasibility test, the test-set candidates and the pilot draw, so
# none of those is touched. Results go to data/processed/draft-codebook/ and are not findings.

EXTRA_CUES = {  # the hard cases added in proposal v7 (codebook B15 to B17); names only
    "media_company": re.compile(
        r"\b(media|news|press|television|\btv\b|radio|broadcast\w*|rundfunk|zeitung|journal|"
        r"magazine|newspaper)\b", re.I),
    "university": re.compile(
        r"\b(universit\w*|hochschule|college|polytechni\w*|\bécole\b|school of)\b", re.I),
    "think_tank": re.compile(
        r"\b(institute|institut|instituto|think tank|policy cent(re|er)|forum)\b", re.I),
}
CODEBOOK_TEST_SIZE = 20


def test_cue(name: str) -> str:
    """The cue used to pick the codebook test: a hard-case cue, else one of EXTRA_CUES."""
    cue = hard_case_cue(name)
    if cue != "none":
        return cue
    for extra, pattern in EXTRA_CUES.items():
        if pattern.search(name or ""):
            return extra
    return "none"


def codebook_test_draw(table: pd.DataFrame, exclude: set[str], seed: int = SEED,
                       size: int = CODEBOOK_TEST_SIZE) -> pd.DataFrame:
    """One organisation per cue, then a second per cue in cue order, then companies, until `size`."""
    rng = np.random.default_rng(seed + 2)  # its own stream
    pool = table[~table["org_id"].isin(exclude)].copy()
    pool["test_cue"] = [test_cue(n) for n in pool["canonical_name"]]
    picks = {cue: _pick(pool[pool["test_cue"] == cue], 2, rng)
             for cue in sorted(set(pool["test_cue"]) - {"none"})}
    first = [p.iloc[:1] for p in picks.values()]
    second = [p.iloc[1:] for p in picks.values()]
    out = pd.concat(first + second, ignore_index=True).head(size)
    if len(out) < size and "name_cue" in pool:  # fill with companies, which test the tier rules
        firms = pool[(pool["test_cue"] == "none") & (pool["name_cue"] == "company legal form")]
        fill = _pick(firms, size - len(out), rng).assign(test_cue="company")
        out = pd.concat([out, fill], ignore_index=True)
    out.insert(0, "case", [f"C{i + 1:02d}" for i in range(len(out))])
    return out


def codebook_test_main(derived: Path = DERIVED, out: Path = OUT) -> pd.DataFrame:
    orgs, delegates = feasibility.load(derived)
    table = build_table(orgs, delegates)
    tests = pd.read_csv(out / "test_set_candidates.csv")
    pilot = pd.read_csv(out / "pilot_draw.csv")
    exclude = feasibility_ids(table) | set(tests["org_id"]) | set(pilot["org_id"])
    draw = codebook_test_draw(table, exclude)
    draw[COLUMNS[:4] + ["test_cue"]].to_csv(out / "codebook_test_draw.csv", index=False)
    return draw
