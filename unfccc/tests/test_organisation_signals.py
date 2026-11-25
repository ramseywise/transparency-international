"""Pre-lookup organisation signals: totals reconcile, the six relation options are the form's, no names."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

from analysis import organisation_signals as s
from analysis.proposal_numbers import DERIVED


@pytest.fixture(scope="module")
def tables():
    if not (DERIVED / "delegates_eu.parquet").exists():
        pytest.skip("cleaned tables not present")
    orgs = pd.read_parquet(DERIVED / "organisations_eu.parquet")
    dels = pd.read_parquet(DERIVED / "delegates_eu.parquet")
    merges = pd.read_csv(DERIVED / "proposed_merges_eu.csv")
    return orgs, dels, merges


def test_relation_group_keeps_six_options_and_folds_the_rest():
    raw = pd.Series([*s.RELATION_OPTIONS, "Party Overflow", None])
    out = s.relation_group(raw)
    assert list(out[:6]) == list(s.RELATION_OPTIONS.values())
    assert set(out[6:]) == {"Other"}


def test_relation_tables_reconcile(tables):
    _, dels, _ = tables
    badge = s.relation_by_badge(dels)
    by_del = s.relation_by_delegation(dels)
    assert list(badge.columns) == s.RELATION_ORDER
    assert int(badge.to_numpy().sum()) == int(by_del.to_numpy().sum()) == len(dels) == 3821
    assert len(by_del) == 28
    shares = by_del.div(by_del.sum(axis=1), axis=0).sum(axis=1)
    assert (shares.round(9) == 1).all()


def test_single_answer_delegations(tables):
    _, dels, _ = tables
    single = s.single_answer_delegations(s.relation_by_delegation(dels))
    assert set(single.index) == {"Spain", "Cyprus", "Portugal", "Slovakia"}


def test_six_options_are_the_forms_own(tables):
    if not s.RAW_CSV.exists():
        pytest.skip("raw file not present")
    t = s.form_options_in_raw()
    assert (t.loc[t["form_option"], "nominators"] >= 300).all()
    assert (t.loc[~t["form_option"], "nominators"] < 35).all()
    assert int(t["form_option"].sum()) == 6


def test_declared_type_columns_empty_for_party_sheets():
    if not s.RAW_CSV.exists():
        pytest.skip("raw file not present")
    raw = pd.read_csv(s.RAW_CSV, usecols=["sheet", "Nominated by", *s.DECLARED_COLUMNS], dtype=str)
    dels = pd.read_parquet(DERIVED / "delegates_eu.parquet", columns=["Nominated by"])
    eu = raw[raw["Nominated by"].isin(set(dels["Nominated by"]))]
    party = eu[eu["sheet"].isin(["Parties", "Party overflow"])]
    assert len(party) == 3821
    assert party[list(s.DECLARED_COLUMNS)].isna().all().all()


def test_graph_layer_and_shared_organisations(tables):
    orgs, dels, _ = tables
    edges = s.delegation_org_edges(dels)
    assert len(edges) == 1518
    assert int(edges["delegates"].sum()) == int(dels["org_id"].notna().sum())
    shared = s.shared_organisations(orgs)
    assert len(shared) == 16
    assert int(shared["n_delegates"].sum()) == 108


def test_missing_information_counts_and_status(tables):
    orgs, dels, merges = tables
    status = s.delegate_status(orgs, dels, merges)
    assert len(status) == len(dels)
    assert int(status.str.startswith("no organisation").sum()) == int(dels["org_id"].isna().sum()) == 22
    t = s.missing_information(orgs, dels, merges)
    assert t.loc[t["gap"].str.startswith("Organisation type"), "affected"].item() == len(orgs)
    assert set(t["status"]) == {"not run"}
    assert t["accuracy"].str.startswith("unknown").all()


def test_chart_data_has_no_personal_names(tables):
    _, dels, _ = tables
    figs = s.build_charts(dels)
    names = set(dels["Name"].dropna().astype(str))
    for fig in figs.values():
        text = fig.chart_data.to_csv()
        assert not any(n in text for n in names if len(n) > 4)


def test_signal_numbers_on_the_cleaned_tables(tables):
    orgs, dels, _ = tables
    v = {r["measure"]: r["value"] for r in s.signal_numbers(orgs, dels)}
    assert v["relation_guest_party_overflow"] + v["relation_paid_by_delegation_party_overflow"] <= 2440
    assert v["relation_delegations"] == 28
    assert v["relation_delegations_single_answer"] == 4
    assert v["organisations_shared_across_delegations"] == 16
    assert v["delegation_organisation_links"] == len(s.delegation_org_edges(dels))
    if "declared_type_rows_checked" in v:
        assert v["declared_type_rows_checked"] == len(dels)
        assert v["declared_type_rows_filled"] == 0
