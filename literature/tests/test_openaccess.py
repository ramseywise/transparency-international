"""Finding legal open copies (OpenAlex) and code or data links (the library's own text).

Why this exists (rule 14): most screened-in papers fail to download because the
publisher's page refuses automated access, while a legal open copy (a repository
or the author's manuscript) often exists. The researcher was finding these by hand
on ResearchGate. The same lookup is useful to any study, so it is a shared tool.
Every request here goes to an httpx.MockTransport.
"""

import json

import httpx

from rag import paths
from rag import cli as lit
from rag import codelinks, openalex
from rag.fetch import Fetcher
from rag.ledger import Ledger

OA_WORK = {
    "doi": "https://doi.org/10.1000/OPEN", "title": "Lobbyists at the talks",
    "open_access": {"is_oa": True, "oa_status": "green"},
    "best_oa_location": {"is_oa": True, "landing_page_url": "https://repo.example.org/item/1",
                         "pdf_url": None, "version": "acceptedVersion", "license": None,
                         "source": {"display_name": "University repository"}},
    "locations": [
        {"is_oa": False, "landing_page_url": "https://publisher.example.com/x", "pdf_url": None},
        {"is_oa": True, "landing_page_url": "https://repo.example.org/item/1",
         "pdf_url": "https://repo.example.org/item/1.pdf", "version": "acceptedVersion",
         "license": "cc-by", "source": {"display_name": "University repository"}},
        {"is_oa": True, "landing_page_url": "https://arxiv.org/abs/1", "pdf_url": "https://arxiv.org/pdf/1",
         "version": "submittedVersion", "license": None, "source": {"display_name": "arXiv"}},
    ],
}
CLOSED_WORK = {"doi": "https://doi.org/10.1000/closed", "title": "Behind the paywall",
               "open_access": {"is_oa": False, "oa_status": "closed"}, "best_oa_location": None,
               "locations": [{"is_oa": False, "landing_page_url": "https://publisher.example.com/y"}]}
TITLE_WORK = {"doi": "https://doi.org/10.1000/titled", "title": "Who Gets a Badge at the Climate Talks?",
              "open_access": {"is_oa": True, "oa_status": "gold"},
              "best_oa_location": {"is_oa": True, "pdf_url": "https://journal.example.org/t.pdf",
                                   "landing_page_url": "https://journal.example.org/t",
                                   "version": "publishedVersion", "license": "cc-by",
                                   "source": {"display_name": "Open Journal"}},
              "locations": []}


def _openalex(seen):
    def handler(request):
        seen.append(request)
        f = request.url.params.get("filter", "")
        if f.startswith("doi:"):
            return httpx.Response(200, json={"results": [OA_WORK, CLOSED_WORK]})
        if f.startswith("title.search:"):
            near = dict(TITLE_WORK, doi="https://doi.org/10.1000/near", title="Who gets a badge")
            return httpx.Response(200, json={"results": [near, TITLE_WORK]})
        return httpx.Response(400)
    return httpx.MockTransport(handler)


def test_open_access_sends_only_dois_and_ranks_pdf_copies_first():
    seen = []
    with openalex.client(_openalex(seen)) as c:
        got = openalex.open_access(["10.1000/open", "10.1000/closed", "10.1000/unknown"], c)
    assert set(got) == {"10.1000/open", "10.1000/closed"}  # unknown is left out, not called closed
    copies = got["10.1000/open"]["copies"]
    assert [c["pdf"] for c in copies] == ["https://repo.example.org/item/1.pdf", "https://arxiv.org/pdf/1"]
    assert copies[0]["version"] == "acceptedVersion" and copies[0]["license"] == "cc-by"
    assert got["10.1000/closed"] == {"is_oa": False, "oa_status": "closed", "copies": []}
    req = seen[0]
    assert set(req.url.params.keys()) == {"filter", "per-page", "select"}
    assert req.headers["user-agent"] == "research-crawler/0.1" and "mailto" not in str(req.url)


def test_title_lookup_takes_only_an_exact_title():
    with openalex.client(_openalex([])) as c:
        hit = openalex.open_access_by_title("Who gets a badge at the climate talks", c)
        assert hit["doi"] == "10.1000/titled" and hit["copies"][0]["version"] == "publishedVersion"
        assert openalex.open_access_by_title("Who gets a badge at the climate summit", c) is None
        assert openalex.open_access_by_title("Badges", c) is None  # too short to identify a work


def test_code_links_found_and_own_code_told_apart():
    doc = {"links": [{"url": "https://github.com/contact/report-content", "page": 1}],
           "pages": [{"page": 4, "blocks": [
               "5Code available here: https://github.com/someone/our-tool/tree/main/src.",
               "We used the classifier at https://huggingface.co/org/model and github.com/other/lib.",
               "Replication data: https://dx.doi.org/10.7910/DVN/ABC123",
               "Statistics at https://zenodo.org/help/statistics and https://github.com/someone",
           ]}]}
    got = {l["url"]: l for l in codelinks.find(doc)}
    assert set(got) == {"https://github.com/someone/our-tool", "https://huggingface.co/org/model",
                        "https://github.com/other/lib", "https://doi.org/10.7910/DVN/ABC123"}
    assert got["https://github.com/someone/our-tool"]["own"] and got["https://github.com/someone/our-tool"]["page"] == 4
    assert got["https://doi.org/10.7910/DVN/ABC123"]["kind"] == "data" and got["https://doi.org/10.7910/DVN/ABC123"]["own"]
    assert not got["https://github.com/other/lib"]["own"]


def _library(tmp_path):
    root = tmp_path / "lit"
    led = Ledger(root)
    led.add("https://doi.org/10.1000/open", id="open", status="in", title="Lobbyists at the talks")
    led.add("https://doi.org/10.1000/closed", id="closed", status="in", title="Behind the paywall")
    led.add("https://scholar.google.com/scholar?q=x", id="scholar", status="in",
            title="Who gets a badge at the climate talks")
    led.add("https://www.example.org/report", id="report", status="in", title="A grey report")
    led.add("https://doi.org/10.1000/held", id="held", status="read", file="pdfs/held.pdf")
    led.add("https://doi.org/10.1000/cand", id="cand", title="Not screened")
    led.save()
    (root / paths.TEXT).mkdir(parents=True)
    (root / paths.TEXT / "held.json").write_text(json.dumps({"pages": [{"page": 2, "blocks": [
        "Our code is available at https://github.com/a/b"]}]}))
    return root


def test_openaccess_command_records_copies_and_writes_the_report(tmp_path, capsys, monkeypatch):
    root = _library(tmp_path)
    seen = []
    monkeypatch.setattr(openalex, "client", lambda transport=None, _c=openalex.client: _c(_openalex(seen)))
    lit.main(["--root", str(root), "openaccess"])
    out = capsys.readouterr().out
    assert "4 sources wanted" in out and "open PDF found for 2" in out
    led = Ledger(root)
    assert led.get("open")["open_access"]["copies"][0]["pdf"] == "https://repo.example.org/item/1.pdf"
    assert led.get("closed")["open_access"]["copies"] == []
    assert led.get("scholar")["open_access"]["via"] == "OpenAlex, exact title match"
    assert led.get("report")["open_access"] is None  # a grey report with its own address: not looked up
    assert led.get("cand")["open_access"] is None    # not screened in: not wanted
    assert led.get("held")["code_links"][0]["url"] == "https://github.com/a/b"
    # nothing about the study went out: only DOIs and the one title
    assert all(set(r.url.params) == {"filter", "per-page", "select"} for r in seen)
    report = (root / paths.OPEN_ACCESS).read_text()
    assert "repo.example.org/item/1.pdf" in report and "author's accepted manuscript" in report
    assert "Behind the paywall" in report and "scholar.google.com/scholar?q=%22Behind" in report
    assert "researchgate.net/search/publication?q=Behind" in report
    assert "github.com/a/b" in report


def test_fetch_tries_the_open_copy_first_and_notes_the_version(tmp_path, monkeypatch):
    root = _library(tmp_path)
    led = Ledger(root)
    led.get("open")["open_access"] = openalex._open_access(OA_WORK)
    led.save()
    asked = []

    def site(request):
        asked.append(str(request.url))
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        if request.url.host == "repo.example.org":
            return httpx.Response(403)  # the first open copy refuses
        if request.url.host == "arxiv.org":
            return httpx.Response(200, content=b"%PDF-1.4 x", headers={"content-type": "application/pdf"})
        return httpx.Response(500)

    monkeypatch.setattr(lit, "Fetcher", lambda r: Fetcher(r, delay=0, transport=httpx.MockTransport(site)))
    monkeypatch.setattr(lit.crawl_mod, "process", lambda id, path, url, root, ledger: {"counts": {}})
    lit.main(["--root", str(root), "fetch", "open"])
    pages = [u for u in asked if not u.endswith("/robots.txt")]
    assert pages == ["https://repo.example.org/item/1.pdf", "https://arxiv.org/pdf/1"]  # never the publisher
    assert (root / paths.PDFS / "open.pdf").read_bytes().startswith(b"%PDF")
    assert "open copy: submittedVersion, from arXiv" in Ledger(root).get("open")["reason"]
