"""The review sheet keeps the original beside the inferred, and leaves the review columns empty."""

import json

import pandas as pd

from analysis import review_sheet as rs


def _write(tmp_path):
    orgs = pd.DataFrame([{
        "org_id": "org_1", "canonical_name": "Example Works", "raw_spellings": ["Example Works", "EW"],
        "countries": ["Atlantis"], "n_delegates": 3, "n_delegates_party": 1,
        "n_delegates_party_overflow": 2,
    }])
    cases = pd.DataFrame([{"case": "T01", "org_id": "org_1"}])
    ev, cl = tmp_path / "evidence", tmp_path / "classified"
    ev.mkdir()
    cl.mkdir()
    (ev / "T01.json").write_text(json.dumps({
        "matched_entity": "Example Works Ltd", "status": "confident", "status_reason": "register entry"}))
    (cl / "T01.json").write_text(json.dumps({
        "status": "uncertain", "reasoning": "one register entry",
        "attributes": {
            "R4_business": {"label": "yes", "rule": "R4", "confidence": "high", "unknown_reason": None,
                            "source_url": "https://example.org/r", "page": "entry", "quote": "Ltd"},
            "R7_fossil_link": {"labels": ["unknown"], "rule": "R7.7", "confidence": None,
                               "unknown_reason": "nothing found", "source_url": None, "page": None,
                               "quote": None},
        }}))
    return rs.build(orgs, cases, ev, cl)


def test_original_columns_are_kept_unchanged(tmp_path):
    r = _write(tmp_path).iloc[0]
    assert r["canonical_name"] == "Example Works"
    assert r["raw_spellings"] == "Example Works | EW"
    assert r["n_delegates"] == "3"


def test_inferred_values_carry_confidence_reason_and_source(tmp_path):
    r = _write(tmp_path).iloc[0]
    assert (r["business"], r["business_confidence"]) == ("yes", "high")
    assert r["business_source_url"] == "https://example.org/r"
    assert r["business_quote"] == "Ltd"
    assert r["reason"] == "one register entry"


def test_unknown_stays_unknown_with_its_reason(tmp_path):
    r = _write(tmp_path).iloc[0]
    assert r["fossil_link"] == "unknown"
    assert r["fossil_link_unknown_reason"] == "nothing found"
    assert r["fossil_link_source_url"] == ""


def test_review_columns_exist_and_are_empty(tmp_path):
    sheet = _write(tmp_path)
    review = [c for c in sheet.columns if c.endswith("_review")] + rs.REVIEW_END
    assert {"business_review", "fossil_link_review", "review_notes"} <= set(review)
    assert (sheet[review] == "").all().all()
