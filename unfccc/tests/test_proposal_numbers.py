import numpy as np
import pandas as pd
import pytest

from analysis.proposal_numbers import (
    acronym_numbers,
    build_table,
    duplicate_numbers,
    merge_numbers,
    overlap_numbers,
    sample_design_numbers,
)


def values(rows):
    return {r["measure"]: r["value"] for r in rows}


def make_orgs():
    return pd.DataFrame(
        {
            "org_id": ["a", "b", "c", "d", "e"],
            "canonical_name": ["Ministry of Energy", "Ministry of Energie", "MoE", "BMUKN", "Bank X"],
            "n_delegates": [10, 3, 2, 4, 1],
            "n_delegates_party": [6, 1, 2, 0, 1],
            "n_delegates_party_overflow": [4, 2, 0, 4, 0],
            # "old" was folded into "c" by an automatic merge
            "pass1_ids_merged": [np.array(["a"]), np.array(["b"]), np.array(["c", "old"]), np.array(["d"]), None],
            "acronym_like": [False, False, False, True, False],
            "countries": [np.array(["FR"]), np.array(["FR"]), np.array(["DE"]), np.array(["DE", "IT"]), np.array(["IT"])],
        }
    )


def make_merges():
    return pd.DataFrame(
        {
            "org_id_a": ["a", "a", "d", "a"],
            "org_id_b": ["b", "old", "e", "e"],
            "decision": ["propose", "propose", "auto", "propose"],
        }
    )


def test_merges_count_each_organisation_once_and_follow_merged_ids():
    v = values(merge_numbers(make_orgs(), make_merges()))
    assert v["pairs_awaiting_review"] == 3
    # a, b, c (through "old") and e; "a" is in three pairs but counted once; d is only in an auto pair
    assert v["organisations_in_pairs"] == 4
    assert v["delegates_in_pairs"] == 10 + 3 + 2 + 1
    assert v["delegates_in_pairs_party"] + v["delegates_in_pairs_party_overflow"] == v["delegates_in_pairs"]
    # one chained group of four organisations becomes one
    assert v["organisations_if_all_pairs_accepted"] == 5 - 3
    assert v["organisations_removed_if_all_accepted"] == 3
    assert v["delegates_that_would_change_organisation"] == 3 + 2 + 1


def test_merges_fail_on_unknown_organisation():
    merges = pd.DataFrame({"org_id_a": ["a"], "org_id_b": ["nowhere"], "decision": ["propose"]})
    with pytest.raises(ValueError):
        merge_numbers(make_orgs(), merges)


def test_acronyms_are_rederived_from_the_name():
    orgs = make_orgs()
    orgs["acronym_like"] = False  # a wrong stored flag must not change the count
    v = values(acronym_numbers(orgs))
    assert v["organisations_acronym_like"] == 1  # BMUKN; "MoE" has a lower-case letter
    assert v["delegates_of_acronym_like"] == 4
    assert v["delegates_of_acronym_like_party_overflow"] == 4
    assert v["disagreements_with_stored_flag"] == 1


def test_duplicates_across_and_within_sheets():
    d = pd.DataFrame(
        {
            "nominated_by_clean": ["FR", "FR", "FR", "FR", "DE", "FR"],
            "person_key": ["p1", "p1", "p2", "p2", "p1", "p3"],
            "badge_type": ["Party", "Party overflow", "Party", "Party", "Party overflow", "Party"],
            "dup_on_party_badge": [False, True, False, False, False, False],
            "dup_within_sheet": [False, False, True, True, False, False],
            "counted_once": [True, False, True, False, True, True],
        }
    )
    v = values(duplicate_numbers(d))
    assert v["persons_on_both_sheets_same_country"] == 1  # p1 for FR; p1 for DE is another country
    assert v["persons_twice_on_one_sheet"] == 1
    assert v["rows_flagged_dup_on_party_badge"] == 1
    assert v["rows_counted_once"] == 4


def make_delegates():
    # delegates per organisation as in make_orgs: a 10, b 3, c 2, d 4, e 1; one row names no organisation
    org = ["a"] * 10 + ["b"] * 3 + ["c"] * 2 + ["d"] * 4 + ["e"] + [None]
    country = ["FR"] * 10 + ["FR"] * 3 + ["DE"] * 2 + ["DE"] * 4 + ["IT"] + ["IT"]
    n = len(org)
    return pd.DataFrame(
        {
            "nominated_by_clean": country,
            "Nominated by": country,
            "relation_clean": ["Guest"] * 5 + ["Paid by the delegation"] * (n - 5),
            "person_key": [f"p{i}" for i in range(n)],
            "badge_type": ["Party"] * n,
            "dup_on_party_badge": [False] * n,
            "dup_within_sheet": [False] * n,
            "counted_once": [True] * n,
            "org_id": org,
        }
    )


def test_overlap_counts_each_organisation_once_and_spreads_by_delegation():
    orgs = make_orgs()
    orgs.loc[orgs["org_id"] == "e", "canonical_name"] = "EIB"  # in a pair and acronym-like
    v = values(overlap_numbers(orgs, make_delegates(), make_merges()))
    assert v["organisations_in_pairs_and_acronym_like"] == 1  # e
    assert v["delegates_in_pairs_and_acronym_like"] == 1
    assert v["organisations_in_pairs_or_acronym_like"] == 5  # a, b, c, e in pairs; d and e acronyms
    assert v["delegates_in_pairs_or_acronym_like"] == 20
    assert v["share_of_delegates_in_pairs_or_acronym_like_pct"] == 100.0
    assert v["delegations"] == 3
    assert v["delegations_with_pairs"] == 3 and v["delegations_with_acronym_like"] == 2
    # pairs: FR 13, DE 2, IT 1 of 16
    assert v["largest_delegation_share_of_pairs_delegates_pct"] == pytest.approx(100 * 13 / 16, abs=0.06)
    # acronyms: DE 4 of 6 delegates, IT 1 of 1, FR 0 of 13
    assert v["highest_share_within_a_delegation_acronym_like_pct"] == 100.0
    assert v["median_share_within_a_delegation_acronym_like_pct"] == pytest.approx(100 * 4 / 6, abs=0.06)


def test_sample_design_arithmetic():
    v = values(sample_design_numbers((20, 30, 50)))
    assert v["v1_groups"] == 15
    assert v["v1_minimum_needed"] == 450
    assert v["v1_shortfall"] == 200
    assert v["v2_strata"] == 6 and v["v2_strata_sampled"] == 3
    assert v["cost_all_six_strata_n30"] == 180
    assert v["cost_sampled_strata_n50"] == 150
    # worst case, no finite population correction: 1.96 * sqrt(0.25 / n)
    for n in (20, 30, 50):
        assert v[f"margin_ceiling_pct_points_n{n}"] == pytest.approx(100 * 1.959964 * (0.25 / n) ** 0.5, abs=0.06)
    assert v["margin_ceiling_pct_points_n20"] > v["margin_ceiling_pct_points_n30"] > v["margin_ceiling_pct_points_n50"]
    assert v["wilson_low_pct_at_90pct_n30"] < 90 < v["wilson_high_pct_at_90pct_n30"]
    assert v["per_stratum_if_250_over_six"] == 41 and v["per_stratum_if_250_over_three"] == 83
    assert v["correct_nearest_90pct_250_over_three"] == 75
    assert v["wilson_low_pct_250_over_three"] < 100 * 75 / 83 < v["wilson_high_pct_250_over_three"]


def test_build_table_shape():
    t = build_table(make_orgs(), make_delegates(), make_merges())
    assert list(t.columns) == ["section", "measure", "value", "note"]
    assert set(t["section"]) == {"merges", "acronyms", "duplicates", "overlap", "sample_design", "organisation_signals"}
    assert t["measure"].is_unique
