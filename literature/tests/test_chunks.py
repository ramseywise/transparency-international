"""Chunk selection gives the reader the passages a reading record needs, and says what it left out."""

import json

from rag import paths
from rag import chunks

FILLER = "The weather in the region was mild and the harvest was ordinary that year. " * 6


def pdf(pages: list[str]) -> dict:
    return {"id": "src1", "title": "A report", "kind": "pdf", "url": "https://example.org/r.pdf",
            "page_count": len(pages),
            "pages": [{"page": i + 1, "blocks": [t]} for i, t in enumerate(pages)]}


def long_doc() -> dict:
    pages = [FILLER] * 60
    pages[0] = "Title page. This report examines lobbying at climate conferences. " * 6
    pages[30] = ("We define a fossil fuel company as one whose revenue share from coal oil and gas "
                 "exceeds the threshold. This definition follows the published list. ") * 3
    pages[45] = ("A limitation of this method is that it cannot identify subsidiaries and may "
                 "underestimate the number of delegates. ") * 3
    return pdf(pages)


def test_short_source_is_given_whole():
    sel = chunks.select(pdf(["Short. " * 30, "Also short. " * 30]))
    assert sel["coverage"]["mode"] == "whole"
    assert sel["coverage"]["passages_given"] == sel["coverage"]["passages_total"]
    assert sel["coverage"]["note"].startswith("whole source")


def test_long_source_keeps_the_opening_and_the_field_passages_within_budget():
    sel = chunks.select(long_doc(), budget=600)
    pages = {p["loc"] for p in sel["passages"]}
    assert {"p.1", "p.31", "p.46"} <= pages
    assert sel["coverage"]["words_given"] <= 600
    assert sel["coverage"]["mode"] == "selected"
    why = {p["loc"]: p["why"] for p in sel["passages"]}
    assert "opening" in why["p.1"] and "definitions" in why["p.31"]
    assert "limitations" in why["p.46"]


def test_coverage_note_says_what_was_not_read():
    note = chunks.select(long_doc(), budget=600)["coverage"]["note"]
    assert note.startswith("selected by code") and "of 60" in note and "not read" in note


def test_passages_come_in_document_order():
    sel = chunks.select(long_doc(), budget=600)
    order = [p["chunk"] for p in sel["passages"]]
    assert order == sorted(order)


def test_same_input_gives_same_selection():
    assert chunks.select(long_doc(), budget=600) == chunks.select(long_doc(), budget=600)


def test_study_terms_raise_passages_that_use_them():
    doc = long_doc()
    doc["pages"][20]["blocks"] = ["Delegates from lobbyist groups attended the session. " * 6]
    plain = {p["loc"] for p in chunks.select(doc, budget=400)["passages"]}
    with_terms = {p["loc"] for p in chunks.select(doc, terms=["lobbyist"], budget=400)["passages"]}
    assert "p.21" in with_terms and "p.21" not in plain


def test_ranges():
    assert chunks._ranges([1, 2, 3, 7, 9, 10]) == "1-3, 7, 9-10"


def test_write_saves_one_file_per_source(tmp_path):
    (tmp_path / paths.TEXT).mkdir(parents=True)
    (tmp_path / paths.TEXT / "src1.json").write_text(json.dumps(long_doc()))
    report = chunks.write(["src1"], root=tmp_path, budget=600)
    saved = json.loads((tmp_path / paths.READER_PICKS / "src1.json").read_text())
    assert report[0]["id"] == "src1" and saved["coverage"]["mode"] == "selected"
