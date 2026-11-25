"""Offline tests for rag.crawl.crawl, using a mock transport in place of the network."""

import json

import httpx
import pytest

from rag import paths
from rag import crawl as crawl_mod
from rag.fetch import Fetcher
from rag.ledger import Ledger

HOME = """<html><head><title>Home</title></head><body><main><h1>Home page</h1>
<p>Our work builds on <a href="https://other.org/study">a study</a> and on the
<a href="/about">about page</a> and the <a href="/files/report.pdf">full report</a>.</p>
<p>Also see <a href="/broken">a broken page</a> and <a href="/second">second</a>.</p>
</main></body></html>"""


def page(title, body="<p>Plain text here.</p>"):
    return f"<html><head><title>{title}</title></head><body><main><h1>{title}</h1>{body}</main></body></html>"


class Web:
    def __init__(self, pages):
        self.pages = pages
        self.requests = []

    def __call__(self, request):
        self.requests.append(str(request.url))
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(404)
        if path not in self.pages:
            return httpx.Response(404)
        item = self.pages[path]
        if isinstance(item, int):
            return httpx.Response(item)
        return httpx.Response(200, text=item, headers={"content-type": "text/html"})

    def fetched(self):
        return [u for u in self.requests if not u.endswith("/robots.txt")]


@pytest.fixture
def web(monkeypatch):
    def install(pages):
        w = Web(pages)
        monkeypatch.setattr(
            crawl_mod, "Fetcher",
            lambda root: Fetcher(root, delay=0, transport=httpx.MockTransport(w)),
        )
        return w

    return install


def rows_by_url(root):
    return {r["doi_or_url"]: r for r in Ledger(root).rows}


def test_depth_zero_downloads_only_given_pages(web, tmp_path):
    w = web({"/": HOME, "/about": page("About"), "/second": page("Second")})
    logs = []
    results = crawl_mod.crawl([("https://example.org/", "home")], tmp_path, log=logs.append)
    assert w.fetched() == ["https://example.org/"]
    assert len(results) == 1 and results[0]["ok"] and results[0]["id"] == "home" and results[0]["depth"] == 0
    assert (tmp_path / paths.PAGES / "home.html").exists()
    assert (tmp_path / paths.TEXT / "home.json").exists()
    assert not (tmp_path / paths.PAGES / "about.html").exists()
    assert logs  # progress was reported


def test_depth_zero_registers_links_as_candidates_with_metadata(web, tmp_path):
    web({"/": HOME})
    crawl_mod.crawl([("https://example.org/", "home")], tmp_path)
    rows = rows_by_url(tmp_path)

    home = rows["https://example.org/"]
    assert home["status"] == "in" and home["reason"] == "supplied by the researcher"
    assert home["file"] == str(tmp_path / paths.PAGES / "home.html")
    assert home["title"] == "Home page"

    study = rows["https://other.org/study"]
    assert study["status"] == "candidate"
    assert study["link_kind"] == "external"
    assert study["anchor"] == "a study"
    assert "builds on" in study["context"]
    assert study["found_via"] == ["home (para 1)"]

    assert rows["https://example.org/about"]["link_kind"] == "internal"
    assert rows["https://example.org/files/report.pdf"]["link_kind"] == "download"
    assert rows["https://example.org/second"]["found_via"] == ["home (para 2)"]


def test_depth_one_follows_internal_links_only(web, tmp_path):
    w = web({
        "/": HOME,
        "/about": page("About"),
        "/second": page("Second"),
        "/broken": 500,
    })
    results = crawl_mod.crawl([("https://example.org/", "home")], tmp_path, depth=1, follow=("internal",),
                              log=lambda *_: None)
    fetched = w.fetched()
    assert "https://other.org/study" not in fetched  # external: never followed
    assert not any(u.endswith("report.pdf") for u in fetched)  # download: not in follow
    assert "https://example.org/about" in fetched and "https://example.org/second" in fetched
    assert {r["depth"] for r in results} == {0, 1}
    # followed pages: not auto-screened in, and linked back to the page that cited them
    rows = rows_by_url(tmp_path)
    about = rows["https://example.org/about"]
    assert about["status"] == "candidate" and about["file"]
    assert about["found_via"] and about["found_via"][0].startswith("home")
    assert (tmp_path / paths.PAGES / f"{about['id']}.html").exists()


def test_external_never_followed_even_when_not_listed(web, tmp_path):
    w = web({"/": HOME})
    crawl_mod.crawl([("https://example.org/", "home")], tmp_path, depth=1, follow=("internal",),
                    log=lambda *_: None)
    assert all("other.org" not in u for u in w.requests)


def test_follow_download_adds_downloads(web, tmp_path):
    w = web({"/": HOME})
    crawl_mod.crawl([("https://example.org/", "home")], tmp_path, depth=1, follow=("download",),
                    log=lambda *_: None)
    assert "https://example.org/files/report.pdf" in w.fetched()
    assert "https://example.org/about" not in w.fetched()


def test_depth_one_does_not_go_to_depth_two(web, tmp_path):
    deeper = page("About", '<p>See <a href="/deep">deep</a>.</p>')
    w = web({"/": HOME, "/about": deeper, "/second": page("S"), "/broken": 404, "/deep": page("Deep")})
    crawl_mod.crawl([("https://example.org/", "home")], tmp_path, depth=1, log=lambda *_: None)
    assert "https://example.org/deep" not in w.fetched()
    # but the deeper link is still recorded as a candidate
    assert "https://example.org/deep" in rows_by_url(tmp_path)


def test_max_pages_is_respected(web, tmp_path):
    w = web({"/": HOME, "/about": page("A"), "/second": page("S"), "/broken": page("B")})
    results = crawl_mod.crawl([("https://example.org/", "home")], tmp_path, depth=1, max_pages=2,
                              log=lambda *_: None)
    assert len(results) == 2
    assert len(w.fetched()) == 2


def test_max_pages_counts_failures(web, tmp_path):
    w = web({"/a": 404, "/b": page("B"), "/c": page("C")})
    starts = [(f"https://example.org/{x}", None) for x in "abc"]
    results = crawl_mod.crawl(starts, tmp_path, max_pages=2, log=lambda *_: None)
    assert len(results) == 2 and len(w.fetched()) == 2


def test_one_failing_page_does_not_stop_the_others_and_is_reported(web, tmp_path):
    web({"/bad": 500, "/good": page("Good")})
    logs = []
    starts = [("https://example.org/bad", "bad"), ("https://example.org/good", "good")]
    results = crawl_mod.crawl(starts, tmp_path, log=logs.append)
    by_id = {r["id"]: r for r in results}
    assert not by_id["bad"]["ok"] and by_id["bad"]["note"] == "HTTP 500"
    assert by_id["good"]["ok"]
    assert any("FAILED bad" in l for l in logs)
    rows = rows_by_url(tmp_path)
    assert "download failed: HTTP 500" in rows["https://example.org/bad"]["reason"]
    assert rows["https://example.org/good"]["status"] == "in"
    assert (tmp_path / paths.PAGES / "good.html").exists()


def test_failure_in_followed_page_does_not_stop_crawl(web, tmp_path):
    web({"/": HOME, "/about": page("About"), "/broken": 500, "/second": page("Second")})
    results = crawl_mod.crawl([("https://example.org/", "home")], tmp_path, depth=1, log=lambda *_: None)
    ok = [r["ok"] for r in results]
    assert ok.count(False) == 1 and ok.count(True) == 3


def test_same_page_twice_is_fetched_once(web, tmp_path):
    w = web({"/a": page("A")})
    starts = [("https://example.org/a", None), ("https://example.org/a?utm_source=x", None)]
    results = crawl_mod.crawl(starts, tmp_path, log=lambda *_: None)
    assert len(results) == 1 and len(w.fetched()) == 1


def test_secret_preview_link_is_not_stored(web, tmp_path):
    web({"/p": page("Preview")})
    crawl_mod.crawl([("https://example.org/p?x-craft-preview=SECRET", "p")], tmp_path, log=lambda *_: None)
    for f in tmp_path.rglob("*"):
        if f.is_file():
            assert "SECRET" not in f.read_text(errors="ignore"), f
    row = Ledger(tmp_path).get("p")
    assert row["reason"] == "supplied by the researcher as an unpublished preview link"


def test_ledger_and_fetch_log_written_even_when_everything_fails(web, tmp_path):
    web({})
    crawl_mod.crawl([("https://example.org/missing", "m")], tmp_path, log=lambda *_: None)
    assert (tmp_path / "ledger.jsonl").exists()
    log = [json.loads(l) for l in (tmp_path / "fetch-log.jsonl").read_text().splitlines()]
    assert log and log[0]["status"] == 404
