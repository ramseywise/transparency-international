"""Feasibility test of the look-up and classification method (a demonstration).

Not the pilot, not a codebook. See the decision log row of 2026-11-24 "Feasibility
test" and `unfccc/docs/working/old/feasibility-scheme-draft.md`. Results are provisional.

What this module does, with no model and no web access:

* reads what the participant list itself says about each organisation: the name's
  own cues (a government word, a company legal form, an acronym), and the fields
  its delegates filled in (badge, relation to the delegation, words in their titles
  and departments);
* draws the seeded, stratified sample of 20 organisations, by the name cue;
* writes the batch files the look-up agents are given, and later reads back the
  stored agent records into one table.

No person's name leaves this module: only organisation names and counts.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

STUDY = Path(__file__).resolve().parents[2]
DERIVED = STUDY / "data" / "derived"
FEAS = DERIVED / "feasibility"
SCHEME = STUDY / "docs" / "old" / "feasibility-scheme-draft.md"
SCHEME_VERSION = "feasibility-draft-0.1"

SEED = 20261124
# drawn per stratum; decided before any look-up (decision log, 2026-11-24)
PER_STRATUM = {"government word": 3, "company legal form": 7, "acronym-like": 4, "other": 6}

# Words in the name that point to a public body, in the EU's main languages.
GOVERNMENT = re.compile(
    r"\b(minist\w*|bundesminister\w*|departe?ment\w*|department|agenc\w*|agentur|agence|agencia|"
    r"agenzia|office|amt|beh[oö]rde|bundesamt|government|gouvernement|regierung|governo|gobierno|"
    r"rz[aą]d|parliament|parlement|parlament\w*|embassy|ambassade|botschaft|permanent representation|"
    r"repr[ée]sentation permanente|st[äa]ndige vertretung|presidency|pr[ée]sidence|chancellery|"
    r"kanzleramt|state secretariat|secretaria de estado|ministerie|ministero|ministerio|ministère|"
    r"ministerstvo|ministerstwo|minisztérium|ministeriet|ministeri[oö]|valdība|vyriausyb\w*|"
    r"european commission|commission européenne|council of the european union|european parliament|"
    r"city of|ville de|stadt|municipality|gemeente|comune|region|province|land \w+)\b",
    re.IGNORECASE,
)
# Company legal forms, as written at the end of a name or between words.
LEGAL_FORM = re.compile(
    r"(\b(gmbh|ag|se|sa|s\.a\.|spa|s\.p\.a\.|srl|s\.r\.l\.|sas|sarl|ltd|limited|plc|llc|inc|corp|"
    r"bv|b\.v\.|nv|n\.v\.|ab|oy|oyj|as|a/s|asa|aps|kft|zrt|nyrt|s\.r\.o\.|a\.s\.|d\.o\.o\.|d\.d\.|"
    r"sp\. z o\.o\.|s\.a\.s\.|kg|ohg|ug|e\.k\.|lda|ead|ad|oü|uab|sia|ehf|s\.l\.|sl|sae|sca)\b"
    r"|&\s*co\b|\bgroup\b|\bgroupe\b|\bkonzern\b)",
    re.IGNORECASE,
)
# Words in delegates' titles or departments that point to a company role.
COMPANY_ROLE = re.compile(
    r"\b(?:ceo|cfo|coo|cto|chief|managing director|vice president|head of sustainability|"
    r"head of public affairs|government affairs|public affairs|regulatory affairs|esg|"
    r"business development|sales|investor relations|chairman of the board|board member|partner)\b",
    re.IGNORECASE,
)
GOVERNMENT_ROLE = re.compile(
    r"\b(?:minister|state secretary|ambassador|negotiator|head of delegation|desk officer|"
    r"policy officer|attaché|attache|civil servant|counsellor|counselor|diplomat|"
    r"director[- ]general|deputy director)\b",
    re.IGNORECASE,
)


def load(derived: Path = DERIVED) -> tuple[pd.DataFrame, pd.DataFrame]:
    orgs = pd.read_parquet(derived / "organisations_eu.parquet")
    delegates = pd.read_parquet(derived / "delegates_eu.parquet")
    return orgs, delegates


def name_cue(name: str, acronym_like: bool) -> str:
    """What the name on the list shows, before any look-up. One cue per name, in order."""
    if GOVERNMENT.search(name):
        return "government word"
    if LEGAL_FORM.search(name):
        return "company legal form"
    if acronym_like:
        return "acronym-like"
    return "other"


def list_fields(orgs: pd.DataFrame, delegates: pd.DataFrame) -> pd.DataFrame:
    """Per organisation, what its delegates' rows say. Counts only, no names or titles."""
    d = delegates.dropna(subset=["org_id"]).copy()
    text = (d["title_clean"].fillna("") + " | " + d["department_clean"].fillna("")).astype(str)
    d["company_role"] = text.str.contains(COMPANY_ROLE)
    d["government_role"] = text.str.contains(GOVERNMENT_ROLE)
    d["guest"] = d["relation_clean"].eq("Guest")
    d["paid_by_delegation"] = d["relation_clean"].eq("Paid by the delegation")
    d["relation_other_or_blank"] = ~(d["guest"] | d["paid_by_delegation"])
    d["overflow"] = d["badge_type"].astype(str).str.contains("overflow", case=False)
    agg = d.groupby("org_id").agg(
        delegates=("row_id", "size"),
        overflow=("overflow", "sum"),
        guest=("guest", "sum"),
        paid_by_delegation=("paid_by_delegation", "sum"),
        relation_other_or_blank=("relation_other_or_blank", "sum"),
        company_role=("company_role", "sum"),
        government_role=("government_role", "sum"),
    )
    out = orgs[["org_id", "canonical_name", "country_context", "acronym_like"]].merge(
        agg, left_on="org_id", right_index=True, how="left"
    )
    out["name_cue"] = [name_cue(n, a) for n, a in zip(out["canonical_name"], out["acronym_like"])]
    out["list_reading"] = out.apply(_list_reading, axis=1)
    return out


def _list_reading(r: pd.Series) -> str:
    """The guess the list alone supports. Shown only to compare with the evidence."""
    if r["name_cue"] == "government word":
        return "public body"
    if r["name_cue"] == "company legal form":
        return "business"
    if r["company_role"] > 0 and r["government_role"] == 0:
        return "business"
    if r["government_role"] > 0 and r["company_role"] == 0:
        return "public body"
    return "cannot tell"


def draw_sample(table: pd.DataFrame, per_stratum: dict = PER_STRATUM, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    parts = []
    for cue in sorted(per_stratum):  # sorted, so the draw is stable
        pool = table[table["name_cue"] == cue].sort_values("org_id")
        idx = rng.choice(len(pool), size=min(per_stratum[cue], len(pool)), replace=False)
        part = pool.iloc[np.sort(idx)].copy()
        part["N_h"], part["n_h"] = len(pool), len(part)
        parts.append(part)
    sample = pd.concat(parts, ignore_index=True)
    sample.insert(0, "case", [f"F{i + 1:02d}" for i in range(len(sample))])
    return sample


def other_spellings(orgs: pd.DataFrame, org_id: str) -> list[str]:
    row = orgs.loc[orgs["org_id"] == org_id].iloc[0]
    name = row["canonical_name"]
    return sorted({s for s in row["raw_spellings"] if s and s.strip().lower() != name.strip().lower()})


def write_inputs(feas: Path = FEAS, derived: Path = DERIVED) -> pd.DataFrame:
    """Writes the strata counts, the sample and the look-up inputs (name, country, spellings)."""
    orgs, delegates = load(derived)
    table = list_fields(orgs, delegates)
    sample = draw_sample(table)
    feas.mkdir(parents=True, exist_ok=True)
    table.groupby("name_cue").agg(organisations=("org_id", "size"), delegates=("delegates", "sum")).to_csv(
        feas / "strata.csv"
    )
    sample.to_csv(feas / "sample.csv", index=False)
    inputs = [
        {
            "case": r.case,
            "name_as_written": r.canonical_name,
            "country": r.country_context,
            "other_spellings": other_spellings(orgs, r.org_id),
        }
        for r in sample.itertuples()
    ]
    (feas / "lookup_inputs.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=1))
    return sample


def split_batch(batch: Path, out_dir: Path) -> list[str]:
    """Writes each record of a returned batch (a JSON array with a "case" field) to <case>.json.

    The batch file itself is kept unchanged beside them, as returned by the agent.
    """
    records = json.loads(batch.read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    for r in records:
        (out_dir / f"{r['case']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    return [r["case"] for r in records]


def read_records(feas: Path = FEAS) -> dict[str, pd.DataFrame]:
    """The stored agent records as tables: evidence, and classification runs 1 and 2."""
    out = {}
    ev = [json.loads(p.read_text()) for p in sorted((feas / "evidence").glob("F*.json"))]
    out["evidence"] = pd.DataFrame(
        {
            "case": e["case"],
            "status": e["status"],
            "status_reason": e.get("status_reason"),
            "n_searches": len(e.get("searches", [])),
            "n_evidence": len(e.get("evidence", [])),
            "best_level": min((i["level"] for i in e.get("evidence", [])), default=None),
            "levels": sorted({i["level"] for i in e.get("evidence", [])}),
            "instructions_found": bool(e.get("instructions_found_in_pages")),
        }
        for e in ev
    )
    for run in (1, 2):
        recs = [json.loads(p.read_text()) for p in sorted((feas / f"classification_run{run}").glob("F*.json"))]
        out[f"run{run}"] = pd.json_normalize(recs) if recs else pd.DataFrame()
    return out


if __name__ == "__main__":
    s = write_inputs()
    print(s[["case", "name_cue", "N_h", "n_h", "list_reading"]].to_string(index=False))
