"""Map the two reference tables onto the study's sample: the organisations on EU party badges.

Reads
- unfccc/data/processed/organisations_eu.parquet   the sample (one row per organisation)
- unfccc/data/processed/admitted_ngos.csv          the UNFCCC list of admitted observer organisations
- literature/unfccc/data/processed/tables/bankingonclimatechaos-sector-tables-2026.csv
                                                   65 banks, financing of oil and gas expansion
- literature/unfccc/data/processed/tables/bankingonclimatechaos-top12-2026.csv
                                                   the report's own group of the twelve largest
                                                   financiers of all fossil fuels, 2021 to 2025

Writes
- unfccc/data/processed/sample_references.csv         one row per sample organisation
- unfccc/data/processed/sample_references_stats.json  the counts printed at the end

Every spelling of an organisation (as written and as cleaned) is compared with both tables,
with the same name rules as `cleaning.badges`. The added columns are name matches, made by
code. They are provisional and they are not classifications:
- being on the admitted list, and the constituency chosen, are registration facts and no
  evidence of a fossil fuel link (codebook rule G2);
- a bank in the financing table is not classified: its financing, its rank among the banks of
  the table and its quarter are shown as a description of scale, with no threshold (codebook
  section 9, recommendation of 2026-11-25, not approved); the report's one named group, its
  twelve largest financiers, is a ranking and is shown as the report gives it; the three sector
  tables overlap, so their sum is larger than a bank's expansion financing and is no total;
  a name that merely contains a bank's name needs a person to check it;
- no match shows nothing: the table covers 65 banks and no insurer or asset manager.

The file is at organisation level and holds no person's name.

Run from the workspace root:
    uv run python -I -m cleaning.sample_references
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from cleaning.badges import ADMITTED, BANKS, CONTAINS, OWN_NAME, UNCONFIRMED, find_bank_kind, org_key, words

SAMPLE = Path("unfccc/data/processed/organisations_eu.parquet")
OUT = Path("unfccc/data/processed/sample_references.csv")
OUT_STATS = Path("unfccc/data/processed/sample_references_stats.json")
TOP12 = Path("literature/unfccc/data/processed/tables/bankingonclimatechaos-top12-2026.csv")

_KIND_ORDER = [OWN_NAME, CONTAINS, UNCONFIRMED]


def spellings(row: pd.Series) -> list[str]:
    """Every distinct spelling of one organisation, the canonical name first."""
    names = [row["canonical_name"], *list(row["raw_spellings"]), *list(row["clean_spellings"])]
    return list(dict.fromkeys(n for n in names if isinstance(n, str) and n.strip()))


def admitted_index(admitted: pd.DataFrame) -> tuple[dict, dict]:
    """Admitted rows by exact name key and by the key that ignores brackets."""
    exact: dict[str, list[int]] = {}
    loose: dict[str, list[int]] = {}
    for i, name in enumerate(admitted["official_name"]):
        if words(name):
            exact.setdefault(words(name), []).append(i)
        if org_key(name):
            loose.setdefault(org_key(name), []).append(i)
    return exact, loose


QUARTERS = ["top quarter", "second quarter", "third quarter", "bottom quarter"]


def bank_scale(figures: pd.DataFrame, top12: pd.DataFrame | None = None) -> pd.DataFrame:
    """The size of each bank's financing, as the table gives it and beside the other banks in it.

    One row per bank: the 2021 to 2025 total in each sector, their sum, the bank's rank on that
    sum among the banks of the table (1 is the largest) and the quarter of the table it falls in.
    This describes scale; it sets no threshold and classifies nothing (codebook section 9).
    The sector tables overlap: over all banks they add up to more than the report's figure for
    all expansion financing, so the sum is a measure for ranking and not a total.

    With `top12` (the report's table of its twelve largest financiers of all fossil fuels), each
    bank also gets "yes" or "no" for being in that group, and the report's own figure if it is.
    """
    wide = figures.pivot(index="bank", columns="sector", values="usd_bn_total_2021_2025")
    wide.columns = [f"usd_bn_2021_2025_{c}" for c in wide.columns]
    total = wide.sum(axis=1).round(1)
    rank = total.rank(ascending=False, method="min").astype(int)
    n = len(wide)
    wide["usd_bn_2021_2025_three_sectors"] = total
    wide["bank_rank_in_table"] = rank
    wide["banks_in_table"] = n
    wide["bank_quarter_of_table"] = [QUARTERS[min(3, (r - 1) * 4 // n)] for r in rank]
    wide = wide.reset_index()
    if top12 is not None:
        missing = set(top12["bank"]) - set(wide["bank"])
        if missing:
            raise ValueError(f"banks of the top-twelve table not in the sector table: {sorted(missing)}")
        own = top12.set_index("bank")["usd_bn_all_fossil_2021_2025"]
        wide["in_report_top_12_2021_2025"] = wide["bank"].map(lambda b: "yes" if b in own.index else "no")
        wide["usd_bn_all_fossil_2021_2025_top_12_only"] = wide["bank"].map(own)
    return wide


def map_sample(sample: pd.DataFrame, admitted: pd.DataFrame, figures: pd.DataFrame,
               top12: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per sample organisation, with the admitted-list and bank-table matches beside it."""
    exact, loose = admitted_index(admitted)
    out = []
    for _, row in sample.iterrows():
        names = spellings(row)
        rec = {
            "org_id": row["org_id"],
            "canonical_name": row["canonical_name"],
            "n_delegates": row["n_delegates"],
            "admitted_match": "none", "admitted_official_name": "", "admitted_constituency": "",
            "admitted_country": "", "admitted_rows_with_this_name": 0, "admitted_matched_spelling": "",
            "bank": "", "bank_match_kind": "", "bank_matched_term": "", "bank_matched_spelling": "",
        }
        for label, index, key in (("name", exact, words), ("name ignoring brackets", loose, org_key)):
            hit = next((n for n in names if key(n) in index), None)
            if hit:
                rows = admitted.iloc[index[key(hit)]]
                rec.update(
                    admitted_match=label,
                    admitted_official_name="; ".join(dict.fromkeys(rows["official_name"])),
                    admitted_constituency="; ".join(dict.fromkeys(rows["constituency"].fillna(""))),
                    admitted_country="; ".join(dict.fromkeys(rows["country"].fillna(""))),
                    admitted_rows_with_this_name=len(rows),
                    admitted_matched_spelling=hit,
                )
                break
        # the strongest kind of bank match over all spellings
        found = [(n, *find_bank_kind(n)) for n in names]
        found = sorted((f for f in found if f[1]), key=lambda f: _KIND_ORDER.index(f[3]))
        if found:
            n, bank, term, kind = found[0]
            rec.update(bank=bank, bank_match_kind=kind, bank_matched_term=term, bank_matched_spelling=n)
        out.append(rec)
    result = pd.DataFrame(out)
    result = result.merge(bank_scale(figures, top12), on="bank", how="left")
    if top12 is not None:
        result["in_report_top_12_2021_2025"] = result["in_report_top_12_2021_2025"].fillna("")
    result["figures_source_id"] = result["bank"].map(lambda b: figures["source_id"].iloc[0] if b else "")
    return result


def main() -> int:
    sample = pd.read_parquet(SAMPLE)
    admitted = pd.read_csv(ADMITTED, dtype=str)
    figures = pd.read_csv(BANKS)
    result = map_sample(sample, admitted, figures, pd.read_csv(TOP12))
    if len(result) != len(sample) or result["org_id"].duplicated().any():
        print("PROBLEM: the result does not have exactly one row per sample organisation. Nothing written.")
        return 1
    result.to_csv(OUT, index=False, encoding="utf-8")
    on_list = result[result["admitted_match"] != "none"]
    banks = result[result["bank"] != ""]
    stats = {
        "status": "provisional name matches, not classifications; not independently checked",
        "sample_organisations": len(result),
        "sample_badges": int(result["n_delegates"].sum()),
        "on_admitted_list": {
            "organisations": len(on_list),
            "badges": int(on_list["n_delegates"].sum()),
            "by_kind_of_match": on_list["admitted_match"].value_counts().to_dict(),
            "name_shared_by_two_or_more_admitted_rows": int((on_list["admitted_rows_with_this_name"] > 1).sum()),
            "organisations_by_constituency": on_list["admitted_constituency"].value_counts().to_dict(),
        },
        "bank_table": {
            "organisations": len(banks),
            "badges": int(banks["n_delegates"].sum()),
            "distinct_banks": int(banks["bank"].nunique()),
            "all_banks_three_sector_sum_usd_bn": round(float(figures["usd_bn_total_2021_2025"].sum()), 1),
            "scale_of_each_bank_found": {
                b: {"usd_bn_2021_2025_three_sectors": float(g["usd_bn_2021_2025_three_sectors"].iloc[0]),
                    "rank_in_table": int(g["bank_rank_in_table"].iloc[0]),
                    "banks_in_table": int(g["banks_in_table"].iloc[0]),
                    "quarter": g["bank_quarter_of_table"].iloc[0],
                    "in_report_top_12_2021_2025": g["in_report_top_12_2021_2025"].iloc[0],
                    "found_as": sorted(set(g["bank_match_kind"]))}
                for b, g in banks.sort_values("bank_rank_in_table").groupby("bank", sort=False)
            },
            "by_kind_of_match": {
                k: {"organisations": int(len(g)), "badges": int(g["n_delegates"].sum()), "banks": int(g["bank"].nunique())}
                for k, g in banks.groupby("bank_match_kind")
            },
        },
        "on_both": int(((result["admitted_match"] != "none") & (result["bank"] != "")).sum()),
    }
    OUT_STATS.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print("written:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
