"""The codebook test draw: repeatable, the right size, and apart from every other draw."""

import pandas as pd

from analysis import pilot


def _table(n=60):
    names = [f"Body {i}" for i in range(n)]
    names[:8] = ["North Stadtwerke", "South Stadtwerke", "Daily News", "Evening Press",
                 "Plains University", "Hill University", "Policy Institute", "Law Advisors LLP"]
    return pd.DataFrame({"org_id": [f"org_{i:03d}" for i in range(n)], "canonical_name": names})


def test_draw_is_repeatable_and_leaves_out_the_excluded():
    t = _table()
    a = pilot.codebook_test_draw(t, exclude={"org_000"})
    b = pilot.codebook_test_draw(t, exclude={"org_000"})
    assert list(a["org_id"]) == list(b["org_id"])
    assert "org_000" not in set(a["org_id"])
    assert len(a) <= pilot.CODEBOOK_TEST_SIZE
    assert (a["test_cue"] != "none").all()


def test_every_cue_present_is_covered_before_any_is_doubled():
    a = pilot.codebook_test_draw(_table(), exclude=set())
    cues = list(a["test_cue"])
    assert set(cues[:len(set(cues))]) == set(cues)
