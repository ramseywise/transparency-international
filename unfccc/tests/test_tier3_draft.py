"""The draft Tier 3 comparison with a published bank table: whole names only, no guessing."""
from analysis import tier3_draft as t

TABLE = [{"bank": "Northfield Bank", "sector": "upstream"},
         {"bank": "Northfield Bank", "sector": "midstream"},
         {"bank": "ING", "sector": "upstream"}]


def _org(key, business="financial_institution", line="established"):
    return {"org_key": key, "delegates": 3, "party": 1, "overflow": 2, "business_type": business,
            "business_type_line": line, "tier_3": "unknown"}


def test_tokens_drop_punctuation_and_legal_forms():
    assert t.tokens("Northfield Bank S.A. (Luxembourg)") == ("northfield", "bank", "luxembourg")
    assert t.tokens(None) == ()


def test_a_bank_name_matches_whole_words_only():
    assert t.contains(t.tokens("Northfield Bank Europe SA"), t.tokens("Northfield Bank"))
    assert not t.contains(t.tokens("Bank of Northfield"), t.tokens("Northfield Bank"))
    assert not t.contains(t.tokens("Training Institute"), t.tokens("ING"))
    assert not t.contains(t.tokens("anything"), ())


def test_compare_marks_a_match_as_draft_and_leaves_the_strict_label():
    recs = {"A": {"matched_entity": "Northfield Bank Europe SA, Luxembourg", "name": "x"},
            "B": {"matched_entity": "Halden Insurance", "name": "y"}}
    rows = t.compare([_org("A"), _org("B"), _org("C", business="energy")], recs, TABLE, "X")
    by = {r["org_key"]: r for r in rows}
    assert set(by) == {"A", "B"}
    assert (by["A"]["on_table"], by["A"]["table_rows"]) == ("yes", 2)
    assert "not approved" in by["A"]["draft_tier_3A"]
    assert by["B"]["on_table"] == "no" and by["B"]["draft_tier_3A"].startswith("unknown")
    assert all(r["strict_tier_3"] == "unknown" for r in rows)


def test_output_holds_no_name_and_no_amount():
    recs = {"A": {"matched_entity": "Northfield Bank", "name": "Northfield Bank"}}
    row = t.compare([_org("A")], recs, TABLE, "X")[0]
    assert "northfield" not in str(row).casefold()
    assert not any(k.startswith("usd") for k in row)


def test_the_number_of_banks_is_counted_from_the_table():
    recs = {"A": {"matched_entity": "Nobody Bank", "name": "A"}}
    row = t.compare([_org("A")], recs, TABLE, "X")[0]
    banks = len({r["bank"] for r in TABLE})
    assert row["banks_in_table"] == banks
    assert f"{banks} banks" in row["draft_tier_3A"]


# --- The run rule (codebook 0.16, section 9) -----------------------------------------------

SCALE = {
    "JPMorgan Chase": {"usd_bn_2021_2025_three_sectors": 150.0, "bank_rank_in_table": 1,
                       "banks_in_table": 65, "bank_quarter_of_table": "top quarter",
                       "in_report_top_12_2021_2025": "yes"},
    "Deutsche Bank": {"usd_bn_2021_2025_three_sectors": 20.0, "bank_rank_in_table": 30,
                      "banks_in_table": 65, "bank_quarter_of_table": "second quarter",
                      "in_report_top_12_2021_2025": "no"},
}


def _rec(name, btype="financial_institution", kind="business_and_commercial", hard="company"):
    lab = lambda v: {"label": v}  # noqa: E731
    return {"name": name, "matched_entity": name,
            "attributes": {"business_type": lab(btype), "kind": lab(kind), "hard_case": lab(hard)}}


def test_one_of_the_twelve_is_met_and_waits_for_a_person():
    r = t.tier3_run(_rec("JPMorgan Chase & Co."), SCALE)
    assert (r["label"], r["rule"], r["step"], r["confidence"]) == ("met", "F4", 1, "medium")
    assert r["counted_twelve"] and r["counted_all_banks"] and r["to_confirm"]


def test_another_bank_on_the_table_is_for_review_with_its_scale():
    r = t.tier3_run(_rec("Deutsche Bank AG"), SCALE)
    assert (r["label"], r["unknown_reason"], r["step"]) == ("unknown", t.FOR_REVIEW, 2)
    assert r["figures"]["bank_rank_in_table"] == 30
    assert r["figures"]["bank_quarter_of_table"] == "second quarter"
    assert "usd_bn_2021_2025_three_sectors" in r["figures"]
    assert r["counted_all_banks"] and not r["counted_twelve"]


def test_a_financial_institution_off_the_table_is_not_covered():
    r = t.tier3_run(_rec("Halden Mutual Insurance"), SCALE)
    assert (r["label"], r["unknown_reason"], r["step"]) == ("unknown", t.NOT_COVERED, 3)
    assert not r["counted_all_banks"]


def test_a_unit_of_a_bank_has_its_parents_figures_and_is_not_counted():
    by_name = t.tier3_run(_rec("Deutsche Bank Foundation"), SCALE)
    by_parent = t.tier3_run(_rec("Northfield Asset Management"), SCALE, parent="JPMorgan Chase & Co.")
    for r in (by_name, by_parent):
        assert (r["label"], r["step"], r["figures_basis"]) == ("unknown", 4, "parent's figures")
        assert r["unknown_reason"] == t.FOR_REVIEW
        assert not r["counted_twelve"] and not r["counted_all_banks"]
    assert by_parent["figures"]["in_report_top_12_2021_2025"] == "yes"


def test_non_financial_bodies_are_not_applicable_and_unsettled_ones_unknown():
    assert t.tier3_run(_rec("Gemeente Utrecht", "not_business", "public_sector", "none"), SCALE)["label"] == "not_applicable"
    assert t.tier3_run(_rec("JPMorgan Chase", "company"), SCALE)["label"] == "not_applicable"
    r = t.tier3_run(_rec("Something", "unknown", "unknown", "unknown"), SCALE)
    assert (r["label"], r["unknown_reason"]) == ("unknown", "description partial")


def test_a_public_development_bank_is_treated_as_financial():
    r = t.tier3_run(_rec("Halden Development Bank", "not_business", "public_sector",
                         "public_development_bank"), SCALE)
    assert r["unknown_reason"] == t.NOT_COVERED


def test_counts_are_given_both_ways():
    res = {"A": t.tier3_run(_rec("JPMorgan Chase"), SCALE),
           "B": t.tier3_run(_rec("Deutsche Bank"), SCALE),
           "C": t.tier3_run(_rec("Deutsche Bank Foundation"), SCALE),
           "D": t.tier3_run(_rec("Gemeente", "not_business"), SCALE)}
    c = t.counts_both_ways(res, {"A": 2, "B": 3, "C": 1, "D": 5})
    assert c["the_twelve_only"] == {"organisations": 1, "delegates": 2}
    assert c["every_bank_on_the_table"] == {"organisations": 2, "delegates": 5}
    assert c["unit_of_a_bank_not_counted"]["organisations"] == 1
    assert c["not_applicable"]["delegates"] == 5


def test_the_real_scale_holds_the_twelve():
    scale = t.load_scale()
    assert len(scale) == 65
    assert sum(v["in_report_top_12_2021_2025"] == "yes" for v in scale.values()) == 12


def test_a_public_pension_or_sovereign_fund_is_treated_as_financial():
    # codebook 0.17: B19 bodies are in tier 3 scope (Ramsey's instruction, for the lead
    # researcher to confirm)
    r = t.tier3_run(_rec("Halden Pension Fund", "not_business", "public_sector",
                         "public_investment_fund"), SCALE)
    assert r["unknown_reason"] == t.NOT_COVERED
