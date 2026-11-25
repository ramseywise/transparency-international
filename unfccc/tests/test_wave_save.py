"""Saving agent records from transcripts, and the input helpers for a wave. Invented data only."""
import json

import pandas as pd

from analysis import wave_inputs as wi
from analysis.wave_save import check_evidence, final_text, parse, tokens


def _line(content, usage=None, mid="m1"):
    msg = {"role": "assistant", "content": content, "id": mid}
    if usage:
        msg["usage"] = usage
    return json.dumps({"message": msg})


def test_final_text_prefers_handback():
    lines = [_line([{"type": "text", "text": "draft"}]),
             _line([{"type": "tool_use", "name": "SubagentHandback", "input": {"message": "final"}}])]
    assert final_text(lines) == "final"


def test_final_text_last_text_reply():
    lines = [_line([{"type": "text", "text": "first"}]), _line([{"type": "text", "text": "last"}]),
             json.dumps({"message": {"role": "user", "content": "x"}})]
    assert final_text(lines) == "last"


def test_parse_strips_fence_and_prose():
    assert parse('Here:\n```json\n{"a": 1}\n```') == {"a": 1}


def test_tokens_counts_each_message_once():
    u = {"input_tokens": 10, "output_tokens": 5}
    lines = [_line([], u, "a"), _line([], u, "a"), _line([], {"input_tokens": 20}, "b")]
    assert tokens(lines) == {"context_at_end": 20, "processed_incl_cache_reads": 35}


def _rec(**kw):
    base = {"parent": {}, "fossil_checks": {}, "status_note": None, "pages_opened": [],
            "activity": {"text": None, "source_url": None},
            "fossil_search": {"queries": ["x oil"], "result": "no mention found"}}
    return base | kw


def test_reason_with_explanation_is_split():
    r = _rec(status="abstained", status_reason="Nothing found. Three searches returned no page.")
    flags = check_evidence(r)
    assert r["status_reason"] == "nothing found"
    assert r["status_note"] == "Three searches returned no page."
    assert flags == ["status_reason split: explanation moved to status_note"]


def test_split_keeps_existing_note():
    r = _rec(status="abstained", status_reason="could be several entities: two bodies",
             status_note="see searches")
    check_evidence(r)
    assert r["status_note"] == "two bodies see searches"


def test_exact_reason_unchanged():
    r = _rec(status="uncertain", status_reason="match in doubt")
    assert check_evidence(r) == [] and r["status_reason"] == "match in doubt"


def test_unknown_reason_flagged_not_changed():
    r = _rec(status="failed", status_reason="the site was slow")
    assert check_evidence(r) == ["status_reason not in the fixed list"]
    assert r["status_reason"] == "the site was slow"


def test_reason_on_confident_flagged():
    assert check_evidence(_rec(status="confident", status_reason="x")) == [
        "status_reason given for status 'confident'"]


def test_missing_fields_flagged_not_filled():
    r = {"status": "confident", "status_reason": None}
    flags = check_evidence(r)
    assert "missing field: parent" in flags and "missing field: pages_opened" in flags
    assert "parent" not in r


def test_ngo_match_by_acronym():
    index = {wi._norm("Example Forum"): {"official_name": "Example Forum (EXF)"},
             wi._norm("EXF"): {"official_name": "Example Forum (EXF)"}}
    assert wi.ngo_match(["nobody", " exf "], index)["matched_spelling"] == " exf "
    assert wi.ngo_match(["nobody"], index) is None


def test_new_org_ids_excludes_earlier_waves(monkeypatch):
    d = pd.DataFrame({"nominated_by_clean": ["A", "B", "B", "C"],
                      "org_id": ["o1", "o1", "o2", "o3"]})
    monkeypatch.setattr(wi.bp, "DONE", {"A"})
    monkeypatch.setattr(wi.bp, "by_delegation", lambda d: d)
    monkeypatch.setattr(wi.bp, "wave_of", lambda _: {"B": 1, "C": 2})
    assert wi.new_org_ids(d, 1) == ["o2"]
    assert wi.new_org_ids(d, 2) == ["o3"]


def test_fossil_search_needs_queries_and_a_fixed_result():
    r = _rec(status="confident", status_reason=None,
             fossil_search={"queries": [], "result": "none"})
    assert check_evidence(r) == ["fossil_search: no queries recorded",
                                 "fossil_search: result not in the fixed list"]


def test_activity_code_needs_a_known_system_and_a_page():
    ok = {"text": "t", "source_url": "u", "register_id": "123456789",
          "code": {"system": "NAF", "value": "35.11Z", "source_url": "r"}}
    assert check_evidence(_rec(status="confident", status_reason=None, activity=ok)) == []
    bad = ok | {"code": {"system": "SIC", "value": "4911", "source_url": None}}
    assert check_evidence(_rec(status="confident", status_reason=None, activity=bad)) == [
        "activity.code: system not in the fixed list", "activity.code: no source page"]
    empty = ok | {"code": {"system": "NACE | NAF | ATECO | WZ", "value": None, "source_url": None}}
    assert check_evidence(_rec(status="confident", status_reason=None, activity=empty)) == []


def test_fossil_search_not_checked_when_abstained():
    r = _rec(status="abstained", status_reason="nothing found",
             fossil_search={"queries": [], "result": None})
    assert check_evidence(r) == []
