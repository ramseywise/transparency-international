"""Make the test draw for one delegation: one case per organisation, with delegate counts by badge.

Writes data/processed/draft-codebook/<country>-test/<country>_test_draw.csv with the same columns as
the Germany draw. Hand joins of spellings the cleaning step left apart are listed in JOINS with the
reason; entries with no organisation get no case and are counted in the notebook as "no organisation
given". Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.country_draw Luxembourg L
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DELEGATES = ROOT / "data" / "processed" / "delegates_eu.parquet"
# org_id kept -> org_id folded into it, and why. Decided from the names alone, before any evidence.
JOINS = {
    "Luxembourg": {
        "org_1ee4901cecb1": ("org_985ffa8a546b", "same name with a typing error (Inverstment)"),
        "org_a0502bf1a195": ("org_3ed340d9abed", "the General Secretariat is the Benelux Union's own office"),
        "org_e8fb4d371e86": ("org_134a89d096cb", "same ministry, one word left out"),
    },
}


def draw(delegates: pd.DataFrame, country: str, prefix: str) -> pd.DataFrame:
    d = delegates[(delegates["nominated_by_clean"] == country) & delegates["org_id"].notna()].copy()
    fold = {src: keep for keep, (src, _) in JOINS.get(country, {}).items()}
    names = d.groupby("org_id")["org_canonical_name"].first()
    d["org_id"] = d["org_id"].replace(fold)
    d["org_canonical_name"] = d["org_id"].map(names)
    g = d.groupby(["org_id", "org_canonical_name"]).agg(
        delegates=("row_id", "size"),
        party=("badge_type", lambda s: int((s == "Party").sum())),
        overflow=("badge_type", lambda s: int((s == "Party overflow").sum())),
        raw=("Home organization", lambda s: " | ".join(sorted(set(map(str, s))))),
    ).reset_index().sort_values(["delegates", "org_canonical_name"], ascending=[False, True], kind="stable")
    g.insert(0, "case", [f"{prefix}{i:02d}" for i in range(1, len(g) + 1)])
    g["country_context"] = country
    return g.reset_index(drop=True)


def main() -> None:
    country, prefix = sys.argv[1], sys.argv[2]
    out = ROOT / "data" / "processed" / "draft-codebook" / f"{country.lower()}-test"
    out.mkdir(parents=True, exist_ok=True)
    g = draw(pd.read_parquet(DELEGATES), country, prefix)
    g.to_csv(out / f"{country.lower()}_test_draw.csv", index=False)
    print(len(g), "cases;", int(g["delegates"].sum()), "delegates;", out)


if __name__ == "__main__":
    main()
