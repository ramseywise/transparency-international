"""Counts for the batch-run plan (docs/batch-run-plan.md): organisations per delegation and
the waves in which the remaining delegations would be searched. Provisional: a planning aid,
not a research result. The usage figure is an estimate, not a measurement.

Run from unfccc/ with PYTHONPATH=src:  uv run python -I -m analysis.batch_plan
"""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

STUDY = Path(__file__).resolve().parents[2]
DELEGATES = STUDY / "data" / "processed" / "delegates_eu.parquet"
OUT = STUDY / "outputs" / "draft-codebook" / "batch-plan"

DONE = ("Germany", "Luxembourg")      # searched already, as tests of the draft codebook
SMALL_MAX = 26                        # wave 1: delegations with this many organisations or fewer
OWN_WAVE = {"France": 2, "Italy": 3}   # the two largest, one wave each
MEDIUM_WAVES = (4, 5)                 # the rest, in two waves of about equal size
                                      # (order and split: Ramsey's instruction, 2026-11-25)
BATCH = 10                            # organisations per batch (classify skill)
TOKENS_PER_ORG = 42_000               # estimate: about 52 million for about 1,250 (decisions.md)


def by_delegation(d: pd.DataFrame) -> pd.DataFrame:
    """One row per delegation: delegates, overflow badges, rows with no organisation, and
    distinct organisations."""
    g = d.groupby("nominated_by_clean")
    t = pd.DataFrame({
        "delegates": g.size(),
        "overflow": g["badge_type"].apply(lambda s: int((s == "Party overflow").sum())),
        "no_organisation": g["org_id"].apply(lambda s: int(s.isna().sum())),
        "organisations": g["org_id"].nunique(),
    })
    return t.sort_values(["organisations", "delegates"], ascending=False).reset_index()


def wave_of(t: pd.DataFrame) -> dict[str, int]:
    """The wave of each delegation not yet searched: 1 small ones, 2 France, 3 Italy, 4 and 5
    the medium ones. The medium ones are taken largest first, each going to whichever of the
    two waves holds fewer organisations so far (the first on a tie)."""
    out = {}
    load = dict.fromkeys(MEDIUM_WAVES, 0)
    t = t.sort_values(["organisations", "delegates", "nominated_by_clean"],
                      ascending=[False, False, True])
    for name, n in zip(t["nominated_by_clean"], t["organisations"]):
        if name in DONE:
            continue
        if name in OWN_WAVE:
            out[name] = OWN_WAVE[name]
        elif n <= SMALL_MAX:
            out[name] = 1
        else:
            k = min(MEDIUM_WAVES, key=lambda w: (load[w], w))
            load[k] += n
            out[name] = k
    return out


def waves(d: pd.DataFrame) -> pd.DataFrame:
    """One row per wave. An organisation in several delegations is counted once, in the
    earliest wave, and not at all if a finished delegation already holds it."""
    w = wave_of(by_delegation(d))
    seen = set(d.loc[d["nominated_by_clean"].isin(DONE), "org_id"].dropna())
    rows = []
    for k in sorted(set(w.values())):
        part = d[d["nominated_by_clean"].map(w) == k]
        new = set(part["org_id"].dropna()) - seen
        seen |= new
        rows.append({
            "wave": k,
            "delegations": part["nominated_by_clean"].nunique(),
            "delegates": len(part),
            "overflow": int((part["badge_type"] == "Party overflow").sum()),
            "no_organisation_rows": int(part["org_id"].isna().sum()),
            "organisations_to_search": len(new),
            "batches_of_10": math.ceil(len(new) / BATCH),
            "tokens_millions_at_42k": round(len(new) * TOKENS_PER_ORG / 1e6, 1),
        })
    return pd.DataFrame(rows)


def main() -> None:
    d = pd.read_parquet(DELEGATES)
    d = d[d["counted_once"]]
    OUT.mkdir(parents=True, exist_ok=True)
    by_delegation(d).to_csv(OUT / "organisations_by_country_PROVISIONAL.csv", index=False)
    w = waves(d)
    w.to_csv(OUT / "waves_PROVISIONAL.csv", index=False)
    print(w.to_string(index=False))
    print("total", int(w["delegates"].sum()), "delegates,", int(w["organisations_to_search"].sum()),
          "organisations,", round(w["tokens_millions_at_42k"].sum(), 1), "million tokens (estimate)")


if __name__ == "__main__":
    main()
