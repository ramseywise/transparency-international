"""Offline tests for the rag subcommands that need no network, and for extract_file."""

import json

import pymupdf
import pytest

from rag import paths
from rag import cli as lit
from rag.extract import extract_file
from rag.ledger import Ledger

URL = "https://www.example.org/news/post"

HTML = """<html lang="en"><head><title>Tab</title></head><body><main>
<h1>Post Title</h1>
<p>First paragraph cites <a href="https://other.org/study">a study</a> and
<a href="/internal/page">an internal page</a>.</p>
<p>Second paragraph links to <a href="https://example.org/files/data.xlsx">the data</a>
and <a href="https://third.com/x">third</a>.</p>
</main></body></html>"""


@pytest.fixture
def html_file(tmp_path):
    p = tmp_path / "src" / "post.html"
    p.parent.mkdir()
    p.write_text(HTML)
    return p


@pytest.fixture
def pdf_file(tmp_path):
    pdf = pymupdf.open()
    pg = pdf.new_page()
    pg.insert_text((72, 100), "Lobbying disclosure in practice", fontsize=12)
    pg.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(72, 88, 300, 104), "uri": "https://other.org/report"})
    p = tmp_path / "src" / "doc.pdf"
    p.parent.mkdir(exist_ok=True)
    pdf.save(str(p))
    pdf.close()
    return p


@pytest.fixture
def root(tmp_path):
    return tmp_path / "lit"


def run(root, *args):
    lit.main(["--root", str(root), *args])


# --- extract_file ---------------------------------------------------------

def test_extract_file_html(html_file):
    doc = extract_file(html_file, URL, "post-1")
    assert doc["kind"] == "html" and doc["id"] == "post-1"
    assert doc["title"] == "Post Title"
    assert doc["file"] == str(html_file)
    assert doc["counts"]["paragraphs"] == 2
    kinds = {l["url"]: l["kind"] for l in doc["links"]}
    assert kinds["https://other.org/study"] == "external"
    assert kinds["https://www.example.org/internal/page"] == "internal"
    assert kinds["https://example.org/files/data.xlsx"] == "download"


def test_extract_file_html_without_url_uses_file_url(html_file):
    doc = extract_file(html_file)
    assert doc["url"] == f"file://{html_file}"


def test_extract_file_pdf(pdf_file):
    doc = extract_file(pdf_file, "https://example.org/doc.pdf", "doc-1")
    assert doc["kind"] == "pdf" and doc["id"] == "doc-1" and doc["page_count"] == 1
    assert "Lobbying disclosure" in " ".join(doc["pages"][0]["blocks"])
    assert [l["url"] for l in doc["links"]] == ["https://other.org/report"]


def test_extract_file_pdf_suffix_case_insensitive(pdf_file, tmp_path):
    upper = tmp_path / "src" / "UP.PDF"
    upper.write_bytes(pdf_file.read_bytes())
    assert extract_file(upper)["kind"] == "pdf"


def test_extract_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_file(tmp_path / "nope.html")


# --- add ------------------------------------------------------------------

def test_add_local_html_file(root, html_file, capsys):
    run(root, "add", str(html_file), "--id", "post", "--url", URL, "--title", "My title", "--type", "report")
    out = capsys.readouterr().out
    assert out.startswith("post: ") and "paragraphs" in out
    row = Ledger(root).get("post")
    assert row["status"] == "in" and row["reason"] == "supplied by the researcher"
    assert row["title"] == "My title"  # the researcher's title wins over the page's
    assert row["type"] == "report"
    assert row["doi_or_url"] == URL
    assert row["file"] == str(html_file)
    text = json.loads((root / paths.TEXT / "post.json").read_text())
    assert text["title"] == "Post Title" and text["id"] == "post"


def test_add_registers_links_as_candidates(root, html_file):
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    rows = {r["doi_or_url"]: r for r in Ledger(root).rows}
    study = rows["https://other.org/study"]
    assert study["status"] == "candidate" and study["link_kind"] == "external"
    assert study["anchor"] == "a study" and "First paragraph" in study["context"]
    assert study["found_via"] == ["post (para 1)"]
    assert rows["https://example.org/files/data.xlsx"]["found_via"] == ["post (para 2)"]


def test_add_local_pdf_file(root, pdf_file, capsys):
    run(root, "add", str(pdf_file), "--id", "doc", "--url", "https://example.org/doc.pdf")
    assert "doc: " in capsys.readouterr().out
    rows = {r["doi_or_url"]: r for r in Ledger(root).rows}
    assert rows["https://other.org/report"]["found_via"] == ["doc (p.1)"]
    assert Ledger(root).get("doc")["status"] == "in"


def test_add_is_repeatable_without_duplicating_rows(root, html_file):
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    n = len(Ledger(root).rows)
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    rows = Ledger(root).rows
    assert len(rows) == n
    study = next(r for r in rows if r["doi_or_url"] == "https://other.org/study")
    assert study["found_via"] == ["post (para 1)"]


def test_add_requires_id():
    with pytest.raises(SystemExit):
        lit.main(["add", "x.html"])


def test_add_missing_file_fails_and_writes_no_ledger(root, tmp_path):
    with pytest.raises(FileNotFoundError):
        run(root, "add", str(tmp_path / "nope.html"), "--id", "x")
    assert not (root / "ledger.jsonl").exists()


def test_add_does_not_modify_the_source_file(root, html_file):
    before = html_file.read_bytes()
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    assert html_file.read_bytes() == before


# --- extract --------------------------------------------------------------

def test_extract_rebuilds_text_for_rows_with_files(root, html_file, capsys):
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    (root / paths.TEXT / "post.json").unlink()
    capsys.readouterr()
    run(root, "extract")
    assert "post: " in capsys.readouterr().out
    assert (root / paths.TEXT / "post.json").exists()


def test_extract_with_ids_only_does_those(root, html_file, pdf_file, capsys):
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    run(root, "add", str(pdf_file), "--id", "doc", "--url", "https://example.org/doc.pdf")
    for f in (root / paths.TEXT).glob("*.json"):
        f.unlink()
    capsys.readouterr()
    run(root, "extract", "doc")
    out = capsys.readouterr().out
    assert "doc:" in out and "post:" not in out
    assert [p.name for p in (root / paths.TEXT).glob("*.json")] == ["doc.json"]


def test_extract_skips_rows_without_file(root, html_file, capsys):
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    capsys.readouterr()
    run(root, "extract")
    out = capsys.readouterr().out
    # the link candidates have no file, so only "post" is re-read
    assert out.count("\n") == 1 and "post:" in out


def test_extract_on_empty_root_is_a_noop(root, capsys):
    run(root, "extract")
    assert capsys.readouterr().out == ""


def test_extract_keeps_researcher_status(root, html_file):
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    ledger = Ledger(root)
    ledger.get("post")["status"] = "read"
    ledger.save()
    run(root, "extract")
    assert Ledger(root).get("post")["status"] == "read"


# --- links ----------------------------------------------------------------

@pytest.fixture
def populated(root, html_file, pdf_file):
    run(root, "add", str(html_file), "--id", "post", "--url", URL)
    run(root, "add", str(pdf_file), "--id", "doc", "--url", "https://example.org/doc.pdf")
    return root


def links_json(root, capsys, *args):
    capsys.readouterr()
    run(root, "links", "--json", *args)
    return json.loads(capsys.readouterr().out)


def test_links_json_lists_only_link_rows(populated, capsys):
    rows = links_json(populated, capsys)
    assert rows and all(r["link_kind"] for r in rows)
    assert {r["id"] for r in rows}.isdisjoint({"post", "doc"})
    assert {"https://other.org/study", "https://other.org/report"} <= {r["doi_or_url"] for r in rows}


def test_links_filter_kind(populated, capsys):
    rows = links_json(populated, capsys, "--kind", "download")
    assert [r["doi_or_url"] for r in rows] == ["https://example.org/files/data.xlsx"]
    assert {r["link_kind"] for r in links_json(populated, capsys, "--kind", "external")} == {"external"}


def test_links_filter_host(populated, capsys):
    rows = links_json(populated, capsys, "--host", "third.com")
    assert [r["doi_or_url"] for r in rows] == ["https://third.com/x"]


def test_links_filter_via(populated, capsys):
    rows = links_json(populated, capsys, "--via", "doc")
    assert "https://other.org/report" in [r["doi_or_url"] for r in rows]
    assert all(any(v.startswith("doc ") for v in r["found_via"]) for r in rows)
    assert not any(r["doi_or_url"] == "https://third.com/x" for r in rows)


def test_links_via_matches_whole_id_not_prefix(populated, capsys):
    assert links_json(populated, capsys, "--via", "pos") == []


def test_links_filter_status(populated, capsys):
    assert len(links_json(populated, capsys, "--status", "candidate")) == len(links_json(populated, capsys))
    assert links_json(populated, capsys, "--status", "out") == []


def test_links_filters_combine(populated, capsys):
    rows = links_json(populated, capsys, "--kind", "external", "--via", "post", "--host", "other.org")
    assert [r["doi_or_url"] for r in rows] == ["https://other.org/study"]


def test_links_text_output(populated, capsys):
    capsys.readouterr()
    run(populated, "links", "--kind", "external")
    out = capsys.readouterr().out
    assert "links. By kind: {'external':" in out
    assert "https://other.org/study" in out and "anchor: a study" in out
    assert "[candidate]" in out and "cited 1x" in out


def test_links_cited_count_across_sources(populated, root, capsys):
    # the same address cited from two documents is one row, cited twice
    ledger = Ledger(root)
    ledger.add("https://other.org/report", found_via="post (para 1)")
    ledger.save()
    rows = links_json(root, capsys, "--host", "other.org/report")
    assert len(rows) == 1 and len(rows[0]["found_via"]) == 2


def test_links_on_empty_root(root, capsys):
    run(root, "links")
    assert capsys.readouterr().out.startswith("0 links. By kind: {}")
    run(root, "links", "--json")
    assert json.loads(capsys.readouterr().out) == []


def test_links_rejects_unknown_kind():
    with pytest.raises(SystemExit):
        lit.main(["links", "--kind", "bogus"])


def test_links_does_not_write_ledger(populated):
    before = (populated / "ledger.jsonl").read_bytes()
    run(populated, "links", "--json")
    assert (populated / "ledger.jsonl").read_bytes() == before


def test_unknown_subcommand_and_missing_subcommand_exit():
    with pytest.raises(SystemExit):
        lit.main(["nope"])
    with pytest.raises(SystemExit):
        lit.main([])


# --- fetch: only screened-in sources, and only those with an address ----------

def _ledger_with(root, **rows):
    from rag.ledger import Ledger
    led = Ledger(root)
    for id, (url, status) in rows.items():
        led.add(url, id=id, status=status)
    led.save()


def test_fetch_refuses_sources_not_screened_in(root, capsys, monkeypatch):
    _ledger_with(root, cand=("https://example.org/c", "candidate"), gone=("https://example.org/o", "out"))
    monkeypatch.setattr(lit.Fetcher, "fetch", lambda *a, **k: pytest.fail("must not download"))
    lit.main(["--root", str(root), "fetch", "cand", "gone", "missing-id"])
    out = capsys.readouterr().out
    assert out.count("SKIPPED") == 3 and "not screened in" in out and "not in the ledger" in out


def test_fetch_skips_screened_in_source_without_address(root, capsys, monkeypatch):
    _ledger_with(root, book=(None, "in"))
    monkeypatch.setattr(lit.Fetcher, "fetch", lambda *a, **k: pytest.fail("must not download"))
    lit.main(["--root", str(root), "fetch", "--screened-in"])
    assert "no web address" in capsys.readouterr().out


def test_fetch_with_nothing_to_do_says_so(root):
    with pytest.raises(SystemExit):
        lit.main(["--root", str(root), "fetch"])
