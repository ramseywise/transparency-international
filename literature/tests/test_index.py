"""Offline tests for rag.index. Never loads the embedding model."""

import json

import pytest

from rag import paths
from rag.index import build, passages, search


def _words(prefix: str, n: int) -> str:
    return " ".join(f"{prefix}{i}" for i in range(n))


def _html_doc(id_="d1", sections=None):
    return {"id": id_, "kind": "html", "title": "Title " + id_, "sections": sections or []}


def test_passages_html_groups_paragraphs_and_keeps_section_and_ids():
    doc = _html_doc(sections=[
        {"heading": None, "level": 0, "paragraphs": [{"n": 1, "text": _words("a", 70)}]},
        {"heading": "Methods", "level": 2, "paragraphs": [
            {"n": 2, "text": _words("b", 40)},
            {"n": 3, "text": _words("c", 40)},
            {"n": 4, "text": _words("d", 8)},
        ]},
    ])
    out = passages(doc)
    assert [p["loc"] for p in out] == ["para 1", "paras 2-3", "para 4"]
    assert [p["section"] for p in out] == [None, "Methods", "Methods"]
    assert all(p["source_id"] == "d1" and p["title"] == "Title d1" for p in out)
    assert [p["chunk"] for p in out] == [0, 1, 2]


def test_passages_drop_tiny_fragments():
    doc = _html_doc(sections=[{"heading": "H", "level": 2, "paragraphs": [{"n": 1, "text": "too short"}]}])
    assert passages(doc) == []


def test_passages_pdf_cuts_long_block_and_keeps_page_loc():
    doc = {"id": "p1", "kind": "pdf", "title": None, "pages": [
        {"page": 1, "blocks": [_words("w", 250)]},
        {"page": 2, "blocks": ["one two three four five six", "short", _words("x", 70)]},
    ]}
    out = passages(doc)
    assert all(p["source_id"] == "p1" for p in out)
    page1 = [p for p in out if p["loc"] == "p.1"]
    assert len(page1) == 2
    assert len(page1[0]["text"].split()) == 220 and len(page1[1]["text"].split()) == 30
    page2 = [p for p in out if p["loc"] == "p.2"]
    assert len(page2) == 1  # the 6 + 1 + 70 word blocks reach 60 words together
    assert "one two three" in page2[0]["text"]
    assert all(p["section"] is None for p in out)


def _write_text(root, doc, status="in"):
    d = root / paths.TEXT
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{doc['id']}.json").write_text(json.dumps(doc))
    row = {"id": doc["id"], "status": status, "text": f"literature/{paths.TEXT}/{doc['id']}.json"}
    with open(root / paths.LEDGER, "a") as fh:
        fh.write(json.dumps(row) + "\n")


@pytest.fixture
def root(tmp_path):
    _write_text(tmp_path, _html_doc("lobby", [{"heading": "Rules", "level": 2, "paragraphs": [
        {"n": 1, "text": "Lobbying disclosure rules for climate policy require public registers of meetings."},
    ]}]))
    _write_text(tmp_path, _html_doc("sport", [{"heading": None, "level": 0, "paragraphs": [
        {"n": 1, "text": "Football results from the weekend league matches were announced today."},
        {"n": 2, "text": "The climate was warm during the football match on Sunday afternoon."},
    ]}]))
    return tmp_path


def test_build_without_embedding_writes_index_and_meta(root):
    meta = build(root, embed=False)
    assert meta["sources"] == 2 and meta["passages"] == 2
    assert meta["embedding_model"] is None
    assert (root / paths.PASSAGES).exists()
    assert not (root / paths.VECTORS).exists()
    assert json.loads((root / paths.INDEX_META).read_text())["passages"] == 2


def test_search_ranks_matching_passage_first_with_source_and_loc(root):
    build(root, embed=False)
    hits = search("lobbying climate registers", root, k=5)
    assert hits[0]["source_id"] == "lobby"
    assert hits[0]["loc"] == "para 1"
    assert "Lobbying" in hits[0]["text"]
    assert hits[0]["keyword"] > 0
    assert len(hits) == 2

    hits = search("football league", root)
    assert hits[0]["source_id"] == "sport"


def test_search_source_filter_and_k(root):
    build(root, embed=False)
    hits = search("climate", root, source="sport")
    assert {h["source_id"] for h in hits} == {"sport"}
    assert len(search("climate", root, k=1)) == 1


def test_build_indexes_only_sources_screened_in(root):
    _write_text(root, _html_doc("dropped", [{"heading": None, "level": 0, "paragraphs": [
        {"n": 1, "text": "Lobbying registers were screened out of this study for being off topic entirely."},
    ]}]), status="out")
    meta = build(root, embed=False)
    assert meta["sources"] == 2 and meta["text_files_not_screened_in"] == 1
    assert meta["screened_in_without_passages"] == []


def test_build_names_sources_screened_in_whose_text_gives_no_passage(root):
    _write_text(root, _html_doc("shell", [{"heading": None, "level": 0, "paragraphs": [{"n": 1, "text": "Loading"}]}]))
    assert build(root, embed=False)["screened_in_without_passages"] == ["shell"]
    assert "dropped" not in {h["source_id"] for h in search("lobbying registers", root, k=10)}


def test_build_removes_stale_vectors_when_not_embedding(root):
    build(root, embed=False)
    (root / paths.VECTORS).write_bytes(b"stale")
    build(root, embed=False)
    assert not (root / paths.VECTORS).exists()


def test_build_with_nothing_to_index_exits(tmp_path):
    with pytest.raises(SystemExit):
        build(tmp_path, embed=False)


def test_search_without_index_exits(tmp_path):
    with pytest.raises(SystemExit):
        search("anything", tmp_path)
