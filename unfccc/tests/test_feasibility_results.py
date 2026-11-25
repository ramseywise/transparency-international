"""Feasibility results (notebook 05): agreement maths, table shapes, no names returned."""

from __future__ import annotations

import pandas as pd
import pytest

from analysis import feasibility_results as R
from analysis.feasibility import FEAS


def test_kappa_perfect_and_chance():
    a = pd.Series(["yes", "no", "yes", "no"])
    assert R.cohen_kappa(a, a) == pytest.approx(1.0)
    # agreement no better than chance gives 0
    b = pd.Series(["yes", "yes", "no", "no"])
    assert R.cohen_kappa(a, b) == pytest.approx(0.0)


def test_kappa_constant_labels_is_none():
    a = pd.Series(["unknown"] * 5)
    assert R.cohen_kappa(a, a) is None


def test_kappa_treats_missing_as_a_label():
    a = pd.Series(["yes", None, "no"])
    b = pd.Series(["yes", None, "no"])
    assert R.cohen_kappa(a, b) == pytest.approx(1.0)


@pytest.fixture(scope="module")
def have_runs():
    if not (FEAS / "classification_run2").exists():
        pytest.skip("feasibility runs not present")


def test_agreement_shape(have_runs):
    ag = R.agreement()
    assert list(ag.attribute) == list(R.ATTRS)
    assert (ag["of"] == 20).all()
    assert ((ag.agree >= 0) & (ag.agree <= ag["of"])).all()


def test_proxies_cover_every_rule_and_case(have_runs):
    p = R.proxies()
    for run, d in p.groupby("run"):
        assert list(d.rule) == list(R.PROXIES)
        assert d.cases.sum() == 20
    # case codes are never given for "unknown"
    assert (p.loc[p.rule == "R7.7", "case_codes"] == "").all()


def test_case_table_has_no_name_column(have_runs):
    ct = R.case_table()
    assert len(ct) == 20
    assert not any("name" in c and c != "name_cue" for c in ct.columns)
