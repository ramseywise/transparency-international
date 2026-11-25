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


def _blind():
    orgs = pd.DataFrame([{
        "org_id": "org_1", "canonical_name": "Example Works", "raw_spellings": ["Example Works", "EW"],
        "countries": ["Atlantis"], "n_delegates": 3, "n_delegates_party": 1,
        "n_delegates_party_overflow": 2,
    }])
    fields = {"business_status": ["business", "not_business", "unknown"], "tier_3": ["unknown"],
              "tier_1": ["met", "not_met", "unknown"], "rule_confidence": ["high", "low"],
              "unknown_class": ["none", "technical"]}
    return rs.blind(orgs, pd.DataFrame([{"case": "P01", "org_id": "org_1"}]), fields)


def test_blind_sheet_keeps_the_original_and_asks_only_for_fields_with_a_choice():
    sheet = _blind()
    assert sheet.iloc[0]["raw_spellings"] == "Example Works | EW"
    asked = [c for c in sheet.columns if c.endswith("_expert")]
    assert asked == ["business_status_expert", "tier_1_expert"]
    assert (sheet[asked + rs.BLIND_END] == "").all().all()


def test_blind_sheet_holds_nothing_the_model_produced():
    """Proposal 6.5: the expert labels without seeing the model's answers."""
    cols = set(_blind().columns)
    model_made = {"matched_entity", "evidence_status", "evidence_status_reason", "status", "reason"}
    assert not cols & model_made
    assert not [c for c in cols if c.endswith(("_rule", "_confidence", "_quote", "_source_url",
                                               "_unknown_reason", "_review"))]
    import inspect
    src = inspect.getsource(rs.blind)
    assert "evidence_dir" not in src and "classified" not in src


def test_every_column_has_a_group_and_the_groups_are_right(tmp_path):
    sheet = _write(tmp_path)
    g = {c: rs.group(c) for c in sheet.columns}
    assert g["raw_spellings"] == "given" and g["canonical_name"] == "cleaned"
    assert g["n_delegates_party"] == "counted" and g["business"] == "inferred"
    assert g["business_source_url"] == "inferred" and g["business_review"] == "review"
    assert g["review_notes"] == "review" and g["case"] == "reference"
    guide = rs.column_guide(sheet.columns)
    assert list(guide["column"]) == list(sheet.columns) and guide["group"].notna().all()


def test_simple_sheet_copies_the_headline_answers_and_leaves_review_empty(tmp_path):
    sheet = _write(tmp_path)
    s = rs.simple(sheet)
    assert s.loc[0, "business"] == "yes" and s.loc[0, "business_confidence"] == "high"
    assert s.loc[0, "business_source"] == "https://example.org/r"
    assert s.loc[0, "fossil_link"] == "unknown" and s.loc[0, "fossil_link_reason"] == "nothing found"
    assert s.loc[0, "raw_spellings"] == sheet.loc[0, "raw_spellings"]
    assert (s[[c for c in s.columns if rs.group(c) == "review"]] == "").all().all()


def test_workbook_has_the_four_tabs_and_names_the_groups(tmp_path):
    from openpyxl import load_workbook

    path = rs.workbook(_write(tmp_path), tmp_path / "w.xlsx")
    wb = load_workbook(path)
    assert wb.sheetnames == ["How to review", "Review", "All detail", "Columns"]
    top = [c.value for c in wb["Review"][1]]
    assert "From the Excel (given)" in top and "Your review (fill in)" in top
