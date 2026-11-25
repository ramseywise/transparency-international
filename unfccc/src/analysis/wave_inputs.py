"""The inputs for one wave of the batch run (batch-run-plan.md, version 3): one row per new
organisation, in batches of ten, with what evidence-finder is given.

For each organisation: a case code (W<wave>-<nnn>), the canonical name and the other spellings
from the organisation table, the nominating delegation(s), delegates by badge, a match on the
UNFCCC list of admitted NGOs (a registration fact, never evidence of a fossil link, rule G2),
and the list's own context (codebook I4) as counts only. No personal name is read: the Name
column is never touched, and list_context.counts folds any value written by fewer than two
delegates into "(single values)".

The output holds organisation names, so it is written under data/processed/ (never served by the
MCP server) and never printed. Chat and the decision log use the case codes.

Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.wave_inputs 1
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import pandas as pd

from analysis import batch_plan as bp
from analysis import list_context as lc

STUDY = bp.STUDY
ORGS = STUDY / "data" / "processed" / "organisations_eu.parquet"
NGOS = STUDY / "data" / "processed" / "admitted_ngos.csv"
BASE = STUDY / "data" / "processed" / "draft-codebook"
CONTEXT_COLUMNS = ("Functional title", "Department", "Home organization", "Relation")


def delegates() -> pd.DataFrame:
    d = pd.read_parquet(bp.DELEGATES)
    return d[d["counted_once"]]


def new_org_ids(d: pd.DataFrame, wave: int) -> list[str]:
    """The organisations first searched in this wave, in the same way as batch_plan.waves."""
    w = bp.wave_of(bp.by_delegation(d))
    seen = set(d.loc[d["nominated_by_clean"].isin(bp.DONE), "org_id"].dropna())
    for k in sorted(set(w.values())):
        part = d[d["nominated_by_clean"].map(w) == k]
        new = set(part["org_id"].dropna()) - seen
        if k == wave:
            return sorted(new)
        seen |= new
    raise ValueError(f"no wave {wave}")


def _norm(s: str) -> str:
    return " ".join((s or "").casefold().split())


def ngo_index() -> dict[str, dict]:
    """Admitted NGOs by normalised official name and by the acronym in brackets, if any.
    The contact person column is not read."""
    out: dict[str, dict] = {}
    for r in csv.DictReader(open(NGOS, encoding="utf-8")):
        row = {k: r[k] for k in ("official_name", "website", "city", "country", "constituency")}
        name = r["official_name"]
        out.setdefault(_norm(name), row)
        if "(" in name and name.endswith(")"):
            out.setdefault(_norm(name[: name.rfind("(")]), row)
            out.setdefault(_norm(name[name.rfind("(") + 1 : -1]), row)
    return out


def ngo_match(spellings: list[str], index: dict[str, dict]) -> dict | None:
    """An exact match (case and spacing aside) of any spelling on the admitted-NGO list."""
    for s in spellings:
        hit = index.get(_norm(s))
        if hit:
            return {**hit, "matched_spelling": s}
    return None


def context_of(rows: pd.DataFrame) -> dict:
    recs = [{"sheet": r["badge_type"],
             **{c: r[c] if isinstance(r[c], str) else "" for c in CONTEXT_COLUMNS}}
            for _, r in rows.iterrows()]
    return lc.counts(recs)


def build(wave: int) -> list[dict]:
    d = delegates()
    orgs = pd.read_parquet(ORGS).set_index("org_id")
    index = ngo_index()
    w = bp.wave_of(bp.by_delegation(d))
    out = []
    for i, oid in enumerate(new_org_ids(d, wave), start=1):
        o = orgs.loc[oid]
        rows = d[d["org_id"] == oid]
        spellings = sorted({*list(o["raw_spellings"]), *list(o["clean_spellings"])})
        delegations = sorted(rows["nominated_by_clean"].unique())
        out.append({
            "case": f"W{wave}-{i:03d}",
            "org_id": oid,
            "batch": math.ceil(i / bp.BATCH),
            "name": o["canonical_name"],
            "other_spellings": [s for s in spellings if s != o["canonical_name"]],
            "nominated_by": delegations,
            "wave_delegations": [n for n in delegations if w.get(n) == wave],
            "country_context": o["country_context"],
            "delegates": len(rows),
            "party": int((rows["badge_type"] == "Party").sum()),
            "overflow": int((rows["badge_type"] == "Party overflow").sum()),
            "admitted_ngo": ngo_match([o["canonical_name"], *spellings], index),
            "list_context": context_of(rows),
        })
    return out


def no_organisation_rows(wave: int) -> list[dict]:
    """Rows of the wave's delegations with no organisation: whether a person lookup could work
    (a title or department that can confirm who the person is). Counts only, no names."""
    d = delegates()
    w = bp.wave_of(bp.by_delegation(d))
    part = d[(d["nominated_by_clean"].map(w) == wave) & d["org_id"].isna()]
    out = []
    for n, (_, r) in enumerate(part.iterrows(), start=1):
        text = lambda v: _norm(v) if isinstance(v, str) else ""  # noqa: E731
        has = bool(text(r["title_clean"]) or text(r["department_clean"]))
        out.append({"case": f"W{wave}-P{n:02d}", "row_id": r["row_id"],
                    "nominated_by": r["nominated_by_clean"], "badge_type": r["badge_type"],
                    "no_org_reason": r["no_org_reason"],
                    "lookup": "eligible" if has else "not identifiable from the list"})
    return out


def main() -> None:
    wave = int(sys.argv[1])
    folder = BASE / f"wave{wave}"
    folder.mkdir(parents=True, exist_ok=True)
    rows = build(wave)
    (folder / "inputs.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1, default=str))
    people = no_organisation_rows(wave)
    (folder / "no_organisation.json").write_text(json.dumps(people, indent=1, default=str))
    batches = max(r["batch"] for r in rows)
    ngo = sum(r["admitted_ngo"] is not None for r in rows)
    print(f"wave {wave}: {len(rows)} organisations, {batches} batches, "
          f"{ngo} on the admitted-NGO list; {len(people)} rows with no organisation "
          f"({sum(p['lookup'] == 'eligible' for p in people)} eligible for a person lookup)")


if __name__ == "__main__":
    main()
