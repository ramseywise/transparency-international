"""The screening export, the search for related work, and the tiers of search finds."""

import json

import httpx

from rag import paths
from rag import cli as lit
from rag import openalex, rank, screening
from rag.ledger import Ledger


def _library(tmp_path):
    root = tmp_path / "lit"
    led = Ledger(root)
    led.add("https://doi.org/10.1000/abc", id="read-one", status="read", file="pdfs/a.pdf",
            found_via="seed (p.1)", question="Q2")
    led.add("https://doi.org/10.1000/abc", found_via="other (p.4)")
    led.add("https://www.transparency.org/en/news/x", id="held-thin", status="in", file="pages/x.html",
            found_via="seed (p.2)")
    led.add("https://example.org/gone", id="failed", status="in", reason="download failed: HTTP 403",
            found_via="seed (p.3)")
    led.add("https://example.org/twin", id="twin", status="out", reason="duplicate: already held",
            found_via="seed (p.3)")
    led.add(None, id="book", status="in", reason="no web address on record", found_via="seed (p.5)")
    led.add("https://www.reuters.com/a", id="cand", found_via="seed (p.6)")
    led.add("https://example.org/never-cited", id="untouched")
    led.save()
    for sub in (paths.RECORDS, paths.TEXT):
        (root / sub).mkdir(parents=True)
    (root / "records" / "read-one.json").write_text("{}")
    (root / paths.TEXT / "read-one.json").write_text(json.dumps({"counts": {"words": 5000}}))
    (root / paths.TEXT / "held-thin.json").write_text(json.dumps({"counts": {"words": 120}}))
    return root


def test_export_shape_outcomes_and_counts(tmp_path):
    root = _library(tmp_path)
    data = screening.build(root)
    by_id = {s["id"]: s for s in data["sources"]}
    assert "untouched" not in by_id  # never cited, never screened, not held
    assert {i: s["outcome"] for i, s in by_id.items()} == {
        "read-one": "read", "held-thin": "held", "failed": "download failed", "twin": "duplicate",
        "book": "no web address", "cand": "not downloaded"}
    one = by_id["read-one"]
    assert (one["tier"], one["tier_name"]) == (1, "primary")
    assert one["signals"]["cited_by"] == ["other", "seed"] and one["signals"]["mentions_in_our_sources"] == 2
    assert one["words_held"] == 5000 and one["thin"] is False and one["question"] == "Q2"
    assert by_id["held-thin"]["thin"] is True and by_id["failed"]["thin"] is False
    assert by_id["cand"]["tier_name"] == "news"
    assert data["sources"][0]["id"] == "read-one"  # tier 1 first
    c = data["counts"]
    assert c["considered"] == 6 and c["thin"] == 1 and data["ledger_rows"] == 7
    assert c["by_decision"] == {"read": 1, "in": 3, "out": 1, "candidate": 1}
    assert sum(c["by_tier"].values()) == sum(c["by_outcome"].values()) == 6


def test_export_lists_a_screened_link_that_no_source_mentions(tmp_path):
    root = _library(tmp_path)
    led = Ledger(root)
    led.add(None, id="untouched", status="out", reason="navigation or non-source link")
    led.save()
    data = screening.build(root)
    assert "untouched" in {s["id"] for s in data["sources"]}
    assert data["counts"]["considered"] == data["ledger_rows"] == 7


def test_export_writes_the_file_and_leaves_the_ledger_alone(tmp_path, capsys):
    root = _library(tmp_path)
    before = (root / "ledger.jsonl").read_bytes()
    lit.main(["--root", str(root), "export"])
    assert json.loads(capsys.readouterr().out)["considered"] == 6
    assert json.loads((root / paths.SCREENING).read_text())["criteria"]["screened_in_if"]
    assert (root / "ledger.jsonl").read_bytes() == before


# --- search for related work ------------------------------------------------

WORKS = {"meta": {"count": 133}, "results": [
    {"doi": "https://doi.org/10.1000/NEW", "title": "Lobbyists at the talks", "publication_year": 2024,
     "cited_by_count": 31, "type": "article",
     "authorships": [{"author": {"display_name": "A. Author"}}],
     "primary_location": {"source": {"display_name": "Global Environmental Politics"}}},
    {"doi": "https://doi.org/10.1000/abc", "title": "Already held", "publication_year": 2020,
     "cited_by_count": 7, "type": "article", "authorships": [], "primary_location": None},
    {"doi": None, "title": None},
]}


def _transport(seen):
    def handler(request):
        seen.append(request)
        if "doi:" in request.url.params.get("filter", ""):
            return httpx.Response(200, json={"results": [{"doi": "https://doi.org/10.1000/ABC", "cited_by_count": 7}]})
        return httpx.Response(200, json=WORKS)
    return httpx.MockTransport(handler)


def test_doi_of():
    assert openalex.doi_of("https://doi.org/10.1038/S41558-025-02254-9") == "10.1038/s41558-025-02254-9"
    assert openalex.doi_of("https://www.transparency.org/en/news/x") is None and openalex.doi_of(None) is None


def test_search_sends_only_the_query_and_a_generic_client_name():
    seen = []
    with openalex.client(_transport(seen)) as c:
        total, works = openalex.search("lobbyists UNFCCC", 2015, 25, c)
    assert total == 133 and [w["title"] for w in works] == ["Lobbyists at the talks", "Already held"]
    assert works[0]["cited_by_count"] == 31 and works[0]["context"] == "Global Environmental Politics"
    req = seen[0]
    assert req.headers["user-agent"] == "research-crawler/0.1"
    assert set(req.url.params.keys()) == {"search", "filter", "per-page", "select"}
    assert "mailto" not in str(req.url) and "api_key" not in str(req.url)


def test_related_adds_candidates_and_citations_fills_counts(tmp_path, capsys, monkeypatch):
    root = _library(tmp_path)
    seen = []
    monkeypatch.setattr(openalex, "client", lambda transport=None, _c=openalex.client: _c(_transport(seen)))
    lit.main(["--root", str(root), "related", "lobbyists UNFCCC"])
    assert "133 matches, top 2 looked at, 1 new candidates" in capsys.readouterr().out
    led = Ledger(root)
    new = led.by_url("https://doi.org/10.1000/new")
    assert new["status"] == "candidate" and new["found_by_search"] == ["lobbyists UNFCCC"]
    assert new["cited_by_count"] == 31 and new["year"] == 2024 and new["peer_reviewed"] is None
    held = led.get("read-one")
    assert held["status"] == "read" and held["found_by_search"] == ["lobbyists UNFCCC"]  # not downgraded
    lit.main(["--root", str(root), "citations"])
    assert "citation count found for 1" in capsys.readouterr().out
    assert Ledger(root).get("read-one")["cited_by_count"] == 7


def test_a_search_find_is_tiered_by_publisher_and_never_primary():
    row = {"id": "x", "doi_or_url": "https://doi.org/10.1000/new", "found_via": [],
           "found_by_search": ["q"], "cited_by_count": 900}
    plain = {"id": "y", "doi_or_url": "https://doi.org/10.1000/old", "found_via": []}
    ranked = rank.rank([row, plain])
    assert ranked == [row] and row["tier"] == 2 and "found by search" in row["tier_reason"]
    assert "tier" not in plain


def test_related_with_json_prints_only_json(tmp_path, capsys, monkeypatch):
    root = _library(tmp_path)
    monkeypatch.setattr(openalex, "client", lambda transport=None, _c=openalex.client: _c(_transport([])))
    lit.main(["--root", str(root), "related", "lobbyists UNFCCC", "--json"])
    out = capsys.readouterr()
    assert json.loads(out.out) == [{"query": "lobbyists UNFCCC", "since": 2015, "matches": 133,
                                    "looked_at": 2, "new": 1}]
    assert "new candidates" in out.err
