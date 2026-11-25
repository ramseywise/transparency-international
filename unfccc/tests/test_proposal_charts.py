"""The proposal charts draw the same totals as proposal_v2_numbers, and no personal names."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

from analysis import proposal_charts as pc
from analysis.proposal_numbers import DERIVED, build_table


@pytest.fixture(scope="module")
def tables():
    if not (DERIVED / "delegates_eu.parquet").exists():
        pytest.skip("cleaned tables not present")
    orgs = pd.read_parquet(DERIVED / "organisations_eu.parquet")
    dels = pd.read_parquet(DERIVED / "delegates_eu.parquet")
    merges = pd.read_csv(DERIVED / "proposed_merges_eu.csv")
    nums = build_table(orgs, dels, merges).set_index("measure")["value"]
    return orgs, dels, merges, nums


def test_delegation_size_matches_numbers(tables):
    _, dels, _, nums = tables
    t = pc.delegation_size_table(dels)
    assert len(t) == 28
    assert int(t.to_numpy().sum()) == nums["delegate_rows"] == len(dels)
    assert int(t["Party"].sum()) == int((dels["badge_type"] == "Party").sum())


def test_unresolved_share_matches_numbers(tables):
    orgs, dels, merges, nums = tables
    t = pc.unresolved_share_table(orgs, dels, merges)
    assert int(t["unresolved"].sum()) == nums["delegates_in_pairs_or_acronym_like"]
    assert int(t["named"].sum()) == nums["delegates_with_organisation"]
    assert int((t["unresolved"] > 0).sum()) == nums["delegations_with_pairs_or_acronym_like"]
    assert round(100 * t["share"].max(), 1) == nums["highest_share_within_a_delegation_pairs_or_acronym_like_pct"]
    assert round(100 * t["share"].median(), 1) == nums["median_share_within_a_delegation_pairs_or_acronym_like_pct"]


def test_organisation_size_covers_every_organisation(tables):
    orgs, *_ = tables
    t = pc.organisation_size_table(orgs)
    assert t["organisations"].sum() == len(orgs)
    assert t["delegates"].sum() == orgs["n_delegates"].sum()


def test_chart_tables_hold_no_personal_names(tables):
    orgs, dels, merges, _ = tables
    names = set(dels["Name"].dropna().astype(str)) if "Name" in dels.columns else set()
    for fig in pc.build_charts(orgs, dels, merges).values():
        cells = set(fig.chart_data.astype(str).to_numpy().ravel())
        assert not (cells & names)
