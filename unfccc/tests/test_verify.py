"""The no-model check of records returned by the helper agents. No network: every web
address is answered by httpx.MockTransport."""

import json
from pathlib import Path

import httpx

from lookup import codebook, verify

QUOTE = "Nordgas supplies natural gas to homes in Hamburg."
URL = "https://nordgas.example/about"
LABELS = {"version": "1.0", "label_field": "link",
          "fields": {"link": ["own_operations", "none_established", "unknown"],
                     "state_ownership": ["majority_state", "not_applicable", "unknown"],
                     "identity_confidence": ["high", "low"]},
          "rules": ["F1", "N1"], "negative_labels": ["none_established"],
          "confidence_by_level": {}, "status_by_confidence": {},
          "unknown_reasons": ["nothing found"]}
CB = codebook.Codebook(path=Path("codebook.md"), text="", labels=LABELS)


def _http():
    def handler(request):
        if str(request.url) == URL:
            return httpx.Response(200, headers={"content-type": "text/html"},
                                  text=f"<html><body><p>{QUOTE}</p></body></html>")
        return httpx.Response(404)
    return httpx.Client(transport=httpx.MockTransport(handler))


def _evidence(quote=QUOTE):
    return {"status": "confident", "searches": [{"query": "Nordgas", "language": "en"}],
            "evidence": [{"source_url": URL, "page": "About", "quote": quote,
                          "date": "2026-11-25", "level": 3, "source_type": "self-description"}]}


def _classified(**link):
    a = {"label": "own_operations", "rule": "F1", "source_url": URL, "quote": QUOTE} | link
    return {"codebook_version": "1.0", "attributes": {
        "link": a,
        "state_ownership": {"label": "unknown", "rule": None, "unknown_reason": "nothing found"},
        "identity_confidence": {"label": "high"}}}


def test_allows_a_quote_that_is_on_its_page():
    assert verify.evidence_problems(_evidence(), _http()) == []


def test_blocks_a_quote_that_is_not_on_its_page():
    problems = verify.evidence_problems(_evidence("Nordgas mines coal."), _http())
    assert problems == [f"{URL}: the quote is not on the page as fetched"]


def test_allows_a_record_whose_labels_and_sources_hold():
    assert verify.classified_problems(_classified(), _evidence(), CB) == []


def test_blocks_a_label_with_a_source_that_is_not_in_the_evidence():
    rec = _classified(source_url="https://elsewhere.example/")
    assert verify.classified_problems(rec, _evidence(), CB) == [
        "link: its source and quote are not in the evidence record"]


def test_blocks_an_unknown_without_a_listed_reason_and_a_label_not_allowed():
    rec = _classified(label="fossil")
    rec["attributes"]["state_ownership"]["unknown_reason"] = "felt unsure"
    assert verify.classified_problems(rec, _evidence(), CB) == [
        "link: label 'fossil' is not allowed",
        "state_ownership: unknown without a reason from the codebook's list"]


def test_flags_a_record_made_under_another_codebook_version():
    rec = _classified() | {"codebook_version": "0.9"}
    assert verify.classified_problems(rec, _evidence(), CB) == [
        "made under codebook 0.9, the codebook is now 1.0"]


def test_verify_reads_both_folders_and_changes_no_record(tmp_path):
    ev, cl = tmp_path / "evidence", tmp_path / "classified"
    ev.mkdir(), cl.mkdir()
    (ev / "C01.json").write_text(json.dumps(_evidence()))
    (cl / "C01.json").write_text(json.dumps(_classified()))
    (ev / "C02.json").write_text(json.dumps(_evidence()))
    before = (ev / "C01.json").read_text()
    out = verify.verify(ev, cl, CB, _http())
    assert out == {"C01": {"evidence": [], "classified": [], "could_not_check": [],
                           "outcome": "passed"},
                   "C02": {"evidence": [], "classified": ["no classification record"],
                           "could_not_check": [], "outcome": "failed"}}
    assert (ev / "C01.json").read_text() == before


# --- added 2026-11-25: robust to bad shapes; strict negatives; inferred values ----------

LABELS_N = LABELS | {"rules": ["F1", "N1", "P1", "P2"]}
CB_N = codebook.Codebook(path=Path("codebook.md"), text="", labels=LABELS_N)


def test_a_string_value_is_reported_not_a_crash():
    rec = _classified()
    rec["attributes"]["link"] = "own_operations (F1)"
    assert verify.classified_problems(rec, _evidence(), CB) == [
        "link: value is not a record with a label (got str)"]


def test_missing_attributes_block_is_reported():
    assert verify.classified_problems({"codebook_version": "1.0"}, _evidence(), CB) == [
        "no attributes record: the output is not in the codebook's format"]


def test_strict_negative_on_a_level_3_source_is_flagged():
    rec = _classified(label="none_established", rule="N1")
    assert verify.classified_problems(rec, _evidence(), CB_N) == [
        "link: negative 'none_established' cites a level 3 source; the strict line needs level 1 or 2"]


def _unknown_with(inferred):
    rec = _classified(label="unknown", rule=None, unknown_reason="nothing found",
                      source_url=None, quote=None, inferred=inferred)
    return rec


def test_limited_evidence_inference_with_its_quote_passes():
    inf = {"label": "none_established", "basis": "limited_evidence", "rule": "P1",
           "confidence": "medium", "source_url": URL, "quote": QUOTE}
    assert verify.classified_problems(_unknown_with(inf), _evidence(), CB_N) == []


def test_proxy_above_low_is_flagged():
    inf = {"label": "none_established", "basis": "proxy", "rule": "P2",
           "confidence": "medium", "from_attribute": "kind"}
    assert verify.classified_problems(_unknown_with(inf), _evidence(), CB_N) == [
        "link: inferred confidence 'medium' is above the proxy ceiling (low)"]


def test_inferred_beside_a_known_label_is_flagged():
    rec = _classified(inferred={"label": "none_established", "basis": "proxy", "rule": "P2",
                                "confidence": "low", "from_attribute": "kind"})
    assert verify.classified_problems(rec, _evidence(), CB_N) == [
        "link: an inferred value is given although the strict label is 'own_operations'"]


# --- added 2026-11-25: three outcomes (passed, failed, could not check) -------------------

def test_a_page_that_cannot_be_opened_is_could_not_check_not_failed(tmp_path):
    ev = tmp_path / "evidence"
    ev.mkdir()
    down = _evidence()
    down["evidence"][0]["source_url"] = "https://nordgas.example/down"
    (ev / "C01.json").write_text(json.dumps(down))
    wrong = _evidence(quote="Nordgas drills for oil.")
    (ev / "C02.json").write_text(json.dumps(wrong))
    out = verify.verify(ev, None, None, _http())
    assert out["C01"]["outcome"] == "could not check"
    assert out["C01"]["evidence"] == []
    assert "HTTP 404" in out["C01"]["could_not_check"][0]
    assert out["C02"]["outcome"] == "failed"


def test_a_real_problem_beside_an_unread_page_is_still_failed():
    assert verify.outcome({"evidence": ["x: no page number"], "could_not_check": ["y"]}) == "failed"
    assert verify.outcome({"evidence": [], "classified": [], "could_not_check": []}) == "passed"


def test_a_cookie_screen_or_empty_shell_is_could_not_check_not_failed():
    from lookup import pages
    assert pages.needs_browser({"kind": "html", "title": "RIS - Bundesrecht",
                                "text": "RIS - Bundesrecht"})
    assert pages.needs_browser({"kind": "html", "text": "Short register entry: value"}) is None
    assert pages.needs_browser({"kind": "html", "text": "Title\nWe use cookies. " + "word " * 100})
    assert pages.needs_browser({"kind": "html", "text": "A real register entry " * 20}) is None
    assert pages.needs_browser({"kind": "data", "text": "ico: 123"}) is None
    assert pages.needs_browser({"kind": "html", "title": "About us | Example",
                                "text": "About us | Example\nSkip to main content"})


def test_quote_matches_across_encyclopaedia_footnote_markers():
    from lookup import pages
    page = "The Example Party ( EP ) is a social democratic [ 5 ] [ 6 ] European political party . [ 7 ]"
    assert pages.quote_on_page("The Example Party (EP) is a social democratic European political party.", page)
    assert not pages.quote_on_page("The Example Party (EP) is a liberal European political party.", page)


def test_a_hard_case_label_that_does_not_match_its_b_rule_is_flagged():
    attrs = {"hard_case": {"label": "public_development_bank", "rule": "B1"}}
    assert verify._consistency_problems(attrs, CB) == [
        "hard_case: rule B1 is the case 'company', not 'public_development_bank'"]
    attrs["hard_case"]["rule"] = "B7"
    assert verify._consistency_problems(attrs, CB) == []
    attrs["hard_case"] = {"label": "unknown", "rule": "U1"}  # not a B rule: not checked
    assert verify._consistency_problems(attrs, CB) == []


def test_unknown_class_none_beside_an_unknown_headline_is_flagged():
    attrs = {"link": {"label": "unknown"}, "unknown_class": {"label": "none"}}
    assert verify._consistency_problems(attrs, CB) == [
        "unknown_class: 'none' although the headline label is unknown"]
    attrs = {"link": {"label": "own_operations"}, "unknown_class": {"label": "none"}}
    assert verify._consistency_problems(attrs, CB) == []
    attrs["unknown_class"]["label"] = "U1"
    assert len(verify._consistency_problems(attrs, CB)) == 1
