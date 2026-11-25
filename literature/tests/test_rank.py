"""Tests for tiering of cited sources and for re-extraction not inflating citation counts."""

import pytest

from rag import rank
from rag.crawl import register_links
from rag.ledger import Ledger


@pytest.mark.parametrize("url,expected", [
    ("https://doi.org/10.1162/glep_a_00660", "scholarly"),
    ("https://unfccc.int/documents/653224", "official"),
    ("https://legalinstruments.oecd.org/public/doc/256/256.en.pdf", "official"),
    ("https://lobbymap.org/Benchmarks", "data"),
    ("https://cop.influencemap.org/index.html", "data"),
    ("https://www.transparency.org/en/publications/x", "ti"),
    ("https://knowledgehub.transparency.org/assets/a.pdf", "ti"),
    ("https://www.theguardian.com/environment/2025/x", "news"),
    ("https://globalwitness.org/en/campaigns/x", "report"),
    ("https://www.rsc.org.uk/kyoto", "other"),
    ("https://notunfccc.int/x", "other"),
    (None, "other"),
])
def test_source_type(url, expected):
    assert rank.source_type(url) == expected


def row(url, via, **extra):
    return {"id": url or "ref", "doi_or_url": url, "found_via": via, "status": "candidate", **extra}


def test_cited_by_two_sources_is_primary():
    t, why = rank.tier(row("https://www.theguardian.com/a", ["s1 (para 2)", "s2 (p.4)"]))
    assert t == 1 and "2 of our sources" in why


def test_three_mentions_in_one_source_is_primary():
    t, why = rank.tier(row("https://globalwitness.org/a", ["s1 (p.1)", "s1 (note 5)", "s1 (note 9)"]))
    assert t == 1 and "3 times" in why


@pytest.mark.parametrize("url,expected", [
    ("https://doi.org/10.1/x", 2), ("https://unfccc.int/documents/1", 2), ("https://lobbymap.org/", 2),
    ("https://www.transparency.org/en/publications/x", 3), ("https://globalwitness.org/a", 3),
    ("https://www.bbc.com/news/1", 4), ("https://www.rsc.org.uk/kyoto", 5),
])
def test_tier_by_source_type_when_cited_once(url, expected):
    assert rank.tier(row(url, ["s1 (p.1)"]))[0] == expected


def test_home_page_is_low_signal_however_often_cited():
    assert rank.tier(row("http://transparency.org/", ["s1 (p.1)", "s2 (p.1)"]))[0] == 5


def test_hand_set_source_type_wins_for_a_reference_without_a_url():
    assert rank.tier(row(None, ["s1 (note 7)"], source_type="scholarly"))[0] == 2


def test_rank_orders_by_tier_then_citations_and_skips_uncited_rows():
    rows = [
        row("https://www.bbc.com/news/1", ["s1 (p.1)"]),
        row("https://doi.org/10.1/x", ["s1 (p.1)"]),
        row("https://doi.org/10.1/y", ["s1 (p.1)", "s1 (p.2)"]),
        row("https://globalwitness.org/a", ["s1 (p.1)", "s2 (p.1)"]),
        row("https://seed.org/page", []),
    ]
    out = rank.rank(rows)
    assert [r["doi_or_url"] for r in out] == [
        "https://globalwitness.org/a", "https://doi.org/10.1/y", "https://doi.org/10.1/x",
        "https://www.bbc.com/news/1"]
    assert out[0]["tier"] == 1 and out[0]["source_type"] == "report" and out[0]["tier_reason"]
    assert "tier" not in rows[4]


def _doc(para, context):
    return {"id": "s1", "links": [{"url": "https://other.org/a", "kind": "external", "paragraph": para,
                                   "anchor": "a", "context": context}]}


def test_extracting_again_replaces_mentions_and_context(tmp_path):
    ledger = Ledger(tmp_path)
    register_links(_doc(3, "bro ken text"), ledger)
    r = ledger.by_url("https://other.org/a")
    r["found_via"].append("s1 (note 12)")  # added by hand
    register_links(_doc(5, "fixed text"), ledger)
    assert sorted(r["found_via"]) == ["s1 (note 12)", "s1 (para 5)"]
    register_links(_doc(5, "fixed text"), ledger)
    assert len(r["found_via"]) == 2


def test_context_refreshed_when_this_document_is_the_first_mention(tmp_path):
    ledger = Ledger(tmp_path)
    register_links(_doc(3, "bro ken text"), ledger)
    register_links(_doc(3, "fixed text"), ledger)
    assert ledger.by_url("https://other.org/a")["context"] == "fixed text"
