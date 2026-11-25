"""Feasibility test inputs: the name cues, the strata add up, the draw is reproducible."""

from __future__ import annotations

import pandas as pd
import pytest

from analysis import feasibility as f


@pytest.fixture(scope="module")
def table():
    if not (f.DERIVED / "delegates_eu.parquet").exists():
        pytest.skip("cleaned tables not present")
    orgs, dels = f.load()
    return f.list_fields(orgs, dels)


def test_name_cue_order():
    assert f.name_cue("Ministry of Finance", False) == "government word"
    assert f.name_cue("Example Group S.p.A.", False) == "company legal form"
    assert f.name_cue("XYZ", True) == "acronym-like"
    assert f.name_cue("Centre for Studies", False) == "other"


def test_strata_cover_every_organisation(table):
    assert len(table) == table["org_id"].nunique()
    assert table["name_cue"].value_counts().sum() == len(table)
    assert set(table["name_cue"]) <= set(f.PER_STRATUM)


def test_draw_is_reproducible_and_sized(table):
    a, b = f.draw_sample(table), f.draw_sample(table)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == sum(f.PER_STRATUM.values())
    assert a.groupby("name_cue").size().to_dict() == f.PER_STRATUM
    assert list(a["case"]) == [f"F{i:02d}" for i in range(1, len(a) + 1)]


def test_stored_sample_matches_the_draw(table):
    stored = f.FEAS / "sample.csv"
    if not stored.exists():
        pytest.skip("sample not written")
    s = pd.read_csv(stored)
    assert list(s["org_id"]) == list(f.draw_sample(table)["org_id"])
