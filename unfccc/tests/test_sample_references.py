"""Checks on the mapping of the reference tables onto the sample (made-up organisations, real bank names)."""

import pandas as pd

from cleaning.badges import CONTAINS, OWN_NAME
from cleaning.sample_references import bank_scale, map_sample


def test_map_sample_keeps_one_row_per_organisation_and_uses_every_spelling():
    sample = pd.DataFrame({
        "org_id": ["o1", "o2", "o3", "o4"],
        "canonical_name": ["Alpha Inst.", "HSBC", "Fondation BNP Paribas", "Ministry of Examples"],
        "raw_spellings": [["Alpha Inst.", "Alpha Institute"], ["HSBC Bank plc"], ["Fondation BNP Paribas"], ["MoE"]],
        "clean_spellings": [["Alpha Institute"], ["HSBC"], ["Fondation BNP Paribas"], ["MoE"]],
        "n_delegates": [3, 2, 1, 9],
    })
    admitted = pd.DataFrame({
        "official_name": ["Alpha Institute", "Beta Forum (BF)"],
        "constituency": ["Youth", "Environmental"],
        "country": ["Norway", "Peru"],
    })
    figures = pd.DataFrame({
        "bank": ["HSBC", "HSBC", "BNP Paribas"],
        "sector": ["upstream_oil_gas_expansion", "gas_power_expansion", "upstream_oil_gas_expansion"],
        "usd_bn_total_2021_2025": [1.5, 2.5, 3.0],
        "source_id": ["made-up-table"] * 3,
    })
    out = map_sample(sample, admitted, figures).set_index("org_id")
    assert len(out) == 4
    assert out.loc["o1", "admitted_match"] == "name"                      # found through a second spelling
    assert out.loc["o1", "admitted_constituency"] == "Youth"
    assert out.loc["o1", "bank"] == ""
    assert out.loc["o2", "bank_match_kind"] == OWN_NAME
    assert out.loc["o2", "usd_bn_2021_2025_gas_power_expansion"] == 2.5
    assert out.loc["o3", "bank"] == "BNP Paribas" and out.loc["o3", "bank_match_kind"] == CONTAINS
    assert out.loc["o4", "admitted_match"] == "none" and out.loc["o4", "bank"] == ""
    assert pd.isna(out.loc["o4", "usd_bn_2021_2025_upstream_oil_gas_expansion"])
    assert out.loc["o4", "figures_source_id"] == ""


def test_bank_scale_ranks_on_the_sum_of_sectors_and_sets_no_threshold():
    figures = pd.DataFrame({
        "bank": [b for b in "ABCDEFGH" for _ in range(2)],
        "sector": ["s1", "s2"] * 8,
        "usd_bn_total_2021_2025": [40, 40, 30, 30, 20, 20, 10, 10, 5, 5, 2, 2, 1, 1, 0, 0],
    })
    scale = bank_scale(figures).set_index("bank")
    assert len(scale) == 8                                             # every bank kept, the zero one too
    assert scale.loc["A", "usd_bn_2021_2025_three_sectors"] == 80
    assert list(scale["bank_rank_in_table"]) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert scale.loc["B", "bank_quarter_of_table"] == "top quarter"
    assert scale.loc["C", "bank_quarter_of_table"] == "second quarter"
    assert scale.loc["H", "bank_quarter_of_table"] == "bottom quarter"
    assert set(scale["banks_in_table"]) == {8}


def test_bank_scale_marks_the_reports_top_twelve_and_refuses_an_unknown_bank():
    import pytest

    figures = pd.DataFrame({"bank": ["A", "B"], "sector": ["s1", "s1"], "usd_bn_total_2021_2025": [9.0, 1.0]})
    top12 = pd.DataFrame({"bank": ["A"], "usd_bn_all_fossil_2021_2025": [50.0]})
    scale = bank_scale(figures, top12).set_index("bank")
    assert scale.loc["A", "in_report_top_12_2021_2025"] == "yes"
    assert scale.loc["A", "usd_bn_all_fossil_2021_2025_top_12_only"] == 50.0
    assert scale.loc["B", "in_report_top_12_2021_2025"] == "no"       # "no" is the report's ranking, not a finding
    assert pd.isna(scale.loc["B", "usd_bn_all_fossil_2021_2025_top_12_only"])
    with pytest.raises(ValueError):
        bank_scale(figures, pd.DataFrame({"bank": ["Z"], "usd_bn_all_fossil_2021_2025": [1.0]}))
