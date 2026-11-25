"""A test of the draft Tier 3 rule on one published table (codebook section 9). PROVISIONAL.

Code, not the classifier, compares each organisation classified as a financial institution
with the bank names in the sector tables of Banking on Climate Chaos 2026 (library id
bankingonclimatechaos-sector-tables-2026: the 65 largest banks, by their financing of
companies expanding oil and gas).

What the result means, and does not mean:
- "on the table" would meet DRAFT tier 3A. The draft is not approved. Nothing here changes a
  label, and nothing here is added to a tier count.
- "not on the table" shows nothing: the table covers 65 banks and no insurer or asset
  manager. The organisation stays "unknown" on tier 3.
- A match is made on the name and needs a person to confirm it is the same legal entity.

The output carries case codes and counts only: no organisation name and no amount.

Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.tier3_draft
The run rule of codebook 0.16 (section 9, steps 0 to 4) on a wave's classified records:
    PYTHONPATH=src uv run python -I -m analysis.tier3_draft wave 1
"""
from __future__ import annotations

import csv
import json
import re

from analysis import country_test as C
from analysis import germany_test as G
from cleaning import bank_tables
from cleaning.badges import OWN_NAME, find_bank_kind

TABLE = C.STUDY.parent / bank_tables.OUT
OUT = C.OUT / "comparison" / "tier3_draft_PROVISIONAL.csv"
FINANCIAL = "financial_institution"
# Words that say what legal form a body has, not which body it is.
LEGAL_FORMS = frozenset("""ag sa se plc nv bv ltd limited inc corp corporation co company group
    holding holdings gmbh spa sarl kgaa asa ab oyj llc lp the and of""".split())


def tokens(name: str) -> tuple[str, ...]:
    """A name as lower-case words, without punctuation and without legal-form words."""
    # "S.A." is read as "sa": full stops are dropped before the words are split.
    words = re.findall(r"[^\W_]+", (name or "").casefold().replace(".", ""))
    return tuple(w for w in words if w not in LEGAL_FORMS)


def contains(haystack: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    """True if the words of needle appear in haystack, whole, together and in order."""
    n = len(needle)
    return n > 0 and any(haystack[i:i + n] == needle for i in range(len(haystack) - n + 1))


def table_rows(names: list[str], table: list[dict]) -> list[dict]:
    """The rows of the bank table whose bank name appears whole in any of the names."""
    have = [tokens(n) for n in names if n]
    return [r for r in table if any(contains(h, tokens(r["bank"])) for h in have)]


def compare(orgs: list[dict], records: dict[str, dict], table: list[dict],
            country: str) -> list[dict]:
    """One row per organisation whose type of business is "financial institution", on either
    line. Organisations of any other type, or of no known type, are not compared."""
    out = []
    banks = len({r["bank"] for r in table})
    for o in orgs:
        if o.get("business_type") != FINANCIAL:
            continue
        rec = records.get(o["org_key"]) or {}
        hits = table_rows([rec.get("matched_entity"), rec.get("name")], table)
        out.append({
            "country": country, "org_key": o["org_key"],
            "delegates": int(o["delegates"]), "party": int(o["party"]),
            "overflow": int(o["overflow"]),
            "financial_institution_line": o.get("business_type_line", ""),
            "on_table": "yes" if hits else "no",
            "table_rows": len(hits),
            "sectors": "; ".join(sorted({r["sector"] for r in hits})),
            "draft_tier_3A": ("would be met (draft, not approved)" if hits
                              else f"unknown (the table covers {banks} banks only)"),
            "strict_tier_3": o.get("tier_3", "unknown"),
            "banks_in_table": banks,
            "source_id": bank_tables.SOURCE_ID,
        })
    return out


# --- The tier 3 run rule (codebook 0.16, section 9, steps 0 to 4). PROVISIONAL. -------------
# Applied by code to every classified record, so the line is the same for every organisation.
# The result is kept beside the classifier's record (rule 5), never written over it.

TOP12 = C.STUDY.parent / "literature/unfccc/data/processed/tables/bankingonclimatechaos-top12-2026.csv"
TOP12_SOURCE = "bankingonclimatechaos-executive-summary-2026"
NOT_FINANCIAL = frozenset({"company", "trade_or_industry_association", "consultancy", "law_firm",
                           "not_business"})
# Bodies whose main business is banking, insurance or investing others' money are in scope even
# when they are not business (codebook 0.17, section 9 step 0): public development banks (B7),
# public pension and sovereign wealth funds (B19).
LENDING_HARD_CASES = frozenset({"public_development_bank", "public_investment_fund"})
FOR_REVIEW = "for review: on the bank table"
NOT_COVERED = "not covered by the bank table"
SCALE_COLUMNS = ("usd_bn_2021_2025_gas_power_expansion", "usd_bn_2021_2025_midstream_oil_gas_expansion",
                 "usd_bn_2021_2025_upstream_oil_gas_expansion", "usd_bn_2021_2025_three_sectors",
                 "bank_rank_in_table", "banks_in_table", "bank_quarter_of_table",
                 "in_report_top_12_2021_2025")


def _label(attributes: dict, field: str) -> str:
    a = attributes.get(field) or {}
    return (a.get("label") if isinstance(a, dict) else a) or "unknown"


def load_scale() -> dict[str, dict]:
    """Each bank of the table of 65 with its scale, as cleaning.sample_references gives it."""
    import pandas as pd
    from cleaning.sample_references import bank_scale
    figures = pd.read_csv(TABLE)
    scale = bank_scale(figures, pd.read_csv(TOP12))
    return {r["bank"]: {k: r[k] for k in SCALE_COLUMNS} for r in scale.to_dict("records")}


def tier3_run(record: dict, scale: dict[str, dict], parent: str | None = None) -> dict:
    """The tier 3 result for one classified record. Returns the attribute (label, rule,
    confidence, source, unknown reason) plus how it was reached and, for a bank on the table, its
    scale. `counted_twelve` and `counted_all_banks` say which of the two counts it enters.
    `parent` is the parent company the evidence record names, with its source, if any: a
    parent on the table makes the organisation a unit of a bank (step 4)."""
    attrs = record.get("attributes") or {}
    btype, kind = _label(attrs, "business_type"), _label(attrs, "kind")
    out = {"label": "unknown", "rule": "F4", "confidence": None, "source_url": "", "quote": "",
           "unknown_reason": None, "inferred": None, "step": None, "bank_match": None,
           "figures": None, "figures_basis": None, "to_confirm": None,
           "counted_twelve": False, "counted_all_banks": False, "set_by": "analysis.tier3_draft.tier3_run"}
    financial = btype == "financial_institution" or _label(attrs, "hard_case") in LENDING_HARD_CASES
    if not financial:
        if btype in NOT_FINANCIAL:
            return {**out, "label": "not_applicable", "step": 0, "unknown_reason": None}
        return {**out, "step": 0, "unknown_reason": "description partial"}
    found = [find_bank_kind(n) for n in (record.get("matched_entity"), record.get("name")) if n]
    found = [f for f in found if f[0] and f[0] in scale]
    via_parent = find_bank_kind(parent) if parent and not found else ("", "", "")
    if via_parent[0] in scale:
        found = [(via_parent[0], via_parent[1], "parent named in the evidence record")]
    if not found:
        return {**out, "step": 3, "unknown_reason": NOT_COVERED}
    own = [f for f in found if f[2] == OWN_NAME]
    bank, _, how = (own or found)[0]
    fig = scale[bank]
    out.update(bank_match=how, figures=fig, figures_basis="the bank's own figures",
               source_url=bank_tables.SOURCE_ID)
    if how != OWN_NAME:
        # Step 4: a unit, branch or relative of a bank is shown with its parent's figures and
        # is not counted until the lead researcher decides whether it takes the parent's place.
        return {**out, "step": 4, "unknown_reason": FOR_REVIEW, "figures_basis": "parent's figures",
                "to_confirm": "a unit of the bank: whether it takes its parent's place"}
    if fig.get("in_report_top_12_2021_2025") == "yes":
        return {**out, "label": "met", "step": 1, "confidence": "medium", "source_url": TOP12_SOURCE,
                "quote": "", "to_confirm": "the same legal entity as the bank in the report",
                "counted_twelve": True, "counted_all_banks": True}
    return {**out, "step": 2, "unknown_reason": FOR_REVIEW, "counted_all_banks": True}


def counts_both_ways(results: dict[str, dict], delegates: dict[str, int] | None = None) -> dict:
    """Tier 3 counted twice (codebook section 9): the twelve only, and every bank on the table.
    Units of a bank are in neither; they are shown apart. Delegates too, where given."""
    d = delegates or {}
    def tally(pred):
        keys = [k for k, r in results.items() if pred(r)]
        return {"organisations": len(keys), "delegates": sum(int(d.get(k, 0)) for k in keys)}
    return {
        "the_twelve_only": tally(lambda r: r["counted_twelve"]),
        "every_bank_on_the_table": tally(lambda r: r["counted_all_banks"]),
        "unit_of_a_bank_not_counted": tally(lambda r: r["step"] == 4),
        "financial_not_covered": tally(lambda r: r["step"] == 3),
        "not_applicable": tally(lambda r: r["label"] == "not_applicable"),
        "unknown_not_settled_if_financial": tally(lambda r: r["step"] == 0 and r["label"] == "unknown"),
    }


def run_wave(wave: int) -> dict:
    """Apply the run rule to every classified record of a wave; write tier3_run.json beside them."""
    folder = C.BASE / f"wave{wave}"
    scale = load_scale()
    results = {}
    for f in sorted((folder / "classified").glob("*.json")):
        rec = json.loads(f.read_text())
        ev = folder / "evidence" / f.name
        parent = (json.loads(ev.read_text()).get("parent") or {}) if ev.exists() else {}
        name = parent.get("name") if isinstance(parent, dict) else parent
        results[rec.get("case", f.stem)] = tier3_run(rec, scale, name)
    inputs = {r["case"]: r["delegates"] for r in json.loads((folder / "inputs.json").read_text())}
    summary = counts_both_ways(results, inputs)
    (folder / "tier3_run.json").write_text(json.dumps(
        {"codebook_version": "0.16", "results": results, "counts": summary}, indent=1, default=str))
    return summary


def main() -> None:
    table = list(csv.DictReader(open(TABLE, encoding="utf-8")))
    rows, compared = [], 0
    for country in C.COUNTRIES.values():
        path = country.test / f"{country.stem}_by_organisation_with_lookups_0.13_PROVISIONAL.csv"
        orgs = list(csv.DictReader(open(path)))
        records = {**C.load(country.test / "classified-0.13"),
                   **C.load(country.test / C.RESEARCHED),
                   **C.load(country.test / "person-lookup" / "classified-0.13")}
        found = compare(orgs, records, table, country.name)
        rows += found
        compared += len(orgs)
    if rows:
        G._write(OUT, rows)
    print(json.dumps({
        "organisations_in_the_tests": compared, "financial_institutions_compared": len(rows),
        "on_table": sum(r["on_table"] == "yes" for r in rows),
        "delegates_on_table": sum(r["delegates"] for r in rows if r["on_table"] == "yes"),
        "banks_in_table": len({r["bank"] for r in table})}, indent=1))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "wave":
        print(json.dumps(run_wave(int(sys.argv[2])), indent=1))
    else:
        main()
