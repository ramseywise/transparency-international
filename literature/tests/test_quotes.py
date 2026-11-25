"""The quote check: every quote in a reading record must be in the source text."""

import json

from rag import paths
from rag import cli as lit
from rag.quotes import check_all, check_quote, check_record, normalise, source_text

PDF = {"pages": [
    {"page": 1, "blocks": ["Fossil fuel interests are defined as people and organisations.", "The first page ends with a"],
     "tables": [{"rows": [["Badge", "Delegates"], ["Party overflow", "2,440"]]}]},
    {"page": 2, "blocks": ["sentence that runs over the break.", "Undue influence is “not defined” – anywhere."], "tables": []},
    {"page": 3, "blocks": ["A closing remark."], "tables": []},
]}
WEB = {"title": "A web page", "description": "About badges",
       "sections": [{"heading": "Method", "level": 2,
                     "paragraphs": [{"n": 1, "text": "Every line was checked by hand."}]}],
       "figures": []}


def _check(quote, page, doc=PDF):
    whole, pages = source_text(doc)
    return check_quote(quote, page, whole, pages)


def test_normalise_plain_quotes_dashes_spaces_case():
    assert normalise("“Not defined” –  anywhere") == '"not defined" - anywhere'


def test_zero_width_characters_in_the_source_are_ignored():
    z = chr(0x200B)  # zero-width space, written as a number so the test file has no invisible character
    doc = {"pages": [{"page": 1, "blocks": [f"{z}Below is a list{z} {z}of the 859 companies{z}"], "tables": []}]}
    assert z in doc["pages"][0]["blocks"][0]
    assert _check("Below is a list of the 859 companies", 1, doc) == "ok"
    assert _check("Below is a list of the 858 companies", 1, doc) == "not_found"


def test_found_on_the_page_given():
    assert _check("Fossil fuel interests are defined as people", 1) == "ok"
    assert _check("A closing remark.", "p. 3") == "ok"


def test_found_on_another_page_is_wrong_page():
    assert _check("A closing remark", 1) == "wrong_page"


def test_changed_wording_is_not_found():
    assert _check("Fossil fuel interests are defined as companies", 1) == "not_found"
    assert _check("", 1) == "not_found"


def test_quote_over_a_page_break_counts_for_the_first_page():
    assert _check("The first page ends with a sentence that runs over the break.", 1) == "ok"


def test_ellipsis_is_checked_piece_by_piece():
    assert _check("Fossil fuel interests [...] people and organisations", 1) == "ok"
    assert _check("Fossil fuel interests … lobbyists and organisations", 1) == "not_found"


def test_curly_and_straight_quotes_match():
    assert _check('Undue influence is "not defined" - anywhere', 2) == "ok"


def test_table_cells_count_as_page_text():
    assert _check("Party overflow 2,440", 1) == "ok"


def test_web_page_has_no_page_check():
    assert _check("Every line was checked by hand", "para 1", WEB) == "ok"
    assert _check("A web page", None, WEB) == "ok"
    assert _check("Every line was checked by machine", None, WEB) == "not_found"


def test_check_record_reads_the_four_quote_fields():
    record = {"id": "s", "definitions": [{"quote": "A closing remark.", "page": 3}],
              "findings": [{"quote": "invented", "page": 1}, {"note": "no quote here"}],
              "summary": "A closing remark that is never checked."}
    out = check_record(record, PDF)
    assert [(r["field"], r["result"]) for r in out] == [("definitions", "ok"), ("findings", "not_found")]


def _library(tmp_path):
    root = tmp_path / "lit"
    (root / "records").mkdir(parents=True)
    (root / paths.TEXT).mkdir(parents=True)
    (root / paths.TEXT / "good.json").write_text(json.dumps(PDF))
    (root / "records" / "good.json").write_text(json.dumps({"findings": [{"quote": "A closing remark.", "page": 3}]}))
    return root


def test_check_all_tally_and_problems(tmp_path):
    root = _library(tmp_path)
    (root / "records" / "broken.json").write_text("{not json")
    (root / "records" / "orphan.json").write_text(json.dumps({"findings": [{"quote": "x y z", "page": 1}]}))
    res = check_all(root)
    assert (res["records"], res["quotes"], res["ok"], res["share_ok"]) == (1, 1, 1, 1.0)
    assert {p["id"] for p in res["problems"]} == {"broken", "orphan"}
    assert check_all(root, ids=["good"])["problems"] == []


def test_cli_exits_with_an_error_only_when_a_quote_fails(tmp_path, capsys):
    root = _library(tmp_path)
    lit.main(["--root", str(root), "check-quotes"])
    assert "1 quotes in 1 records: 1 found" in capsys.readouterr().out
    (root / "records" / "good.json").write_text(json.dumps({"findings": [{"quote": "made up words", "page": 3}]}))
    try:
        lit.main(["--root", str(root), "check-quotes"])
    except SystemExit as e:
        assert e.code == 1
    else:
        raise AssertionError("a failed quote must stop the command")
    assert "NOT_FOUND good findings[0]" in capsys.readouterr().out
