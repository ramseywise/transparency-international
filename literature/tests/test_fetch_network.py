"""Offline tests for Fetcher's network path. Every request goes to an httpx.MockTransport."""

import json

import httpx
import pytest

from rag import paths
from rag import fetch as fetch_mod
from rag.fetch import Fetcher

HTML = b"<!doctype html><html><head><title>t</title></head><body><p>hello</p></body></html>"
PDF = b"%PDF-1.4\n%fake pdf body\n"
ROBOTS_ALLOW = httpx.Response(200, text="User-agent: *\nDisallow: /private/\n")


class Site:
    """A fake web: maps path -> Response (or callable or exception) and records requests."""

    def __init__(self, routes=None, robots=None):
        self.routes = routes or {}
        self.robots = robots if robots is not None else httpx.Response(404)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.path == "/robots.txt":
            return self._resolve(self.robots, request)
        if request.url.path not in self.routes:
            return httpx.Response(404)
        return self._resolve(self.routes[request.url.path], request)

    @staticmethod
    def _resolve(item, request):
        if isinstance(item, Exception):
            raise item
        return item(request) if callable(item) else item

    @property
    def paths(self):
        return [r.url.path for r in self.requests]


@pytest.fixture
def sleeps(monkeypatch):
    calls: list[float] = []
    monkeypatch.setattr(fetch_mod.time, "sleep", calls.append)
    return calls


@pytest.fixture
def make(tmp_path, sleeps):
    made = []

    def _make(site: Site, delay=0.0):
        f = Fetcher(tmp_path, delay=delay, transport=httpx.MockTransport(site))
        made.append(f)
        return f

    yield _make
    for f in made:
        f.close()


def log_lines(f):
    return [json.loads(l) for l in f.log_path.read_text().splitlines()]


def html_resp(body=HTML, ctype="text/html; charset=utf-8"):
    return httpx.Response(200, content=body, headers={"content-type": ctype})


def test_html_saved_under_pages_and_logged(make, tmp_path):
    site = Site({"/a": html_resp()})
    f = make(site)
    rec = f.fetch("https://example.org/a", "a-1")
    assert rec.ok and rec.kind == "html" and rec.status == 200
    assert rec.path == str(tmp_path / paths.PAGES / "a-1.html")
    assert (tmp_path / paths.PAGES / "a-1.html").read_bytes() == HTML
    assert rec.bytes == len(HTML) and len(rec.sha256) == 64
    assert rec.content_type == "text/html"
    log = log_lines(f)
    assert len(log) == 1 and log[0]["id"] == "a-1" and log[0]["path"] == rec.path


def test_pdf_saved_under_pdfs(make, tmp_path):
    f = make(Site({"/r.pdf": httpx.Response(200, content=PDF, headers={"content-type": "application/pdf"})}))
    rec = f.fetch("https://example.org/r.pdf", "r-1")
    assert rec.ok and rec.kind == "pdf"
    assert (tmp_path / paths.PDFS / "r-1.pdf").read_bytes() == PDF


def test_pdf_recognised_by_magic_bytes_despite_wrong_content_type(make, tmp_path):
    f = make(Site({"/r": httpx.Response(200, content=PDF, headers={"content-type": "application/octet-stream"})}))
    rec = f.fetch("https://example.org/r", "r-2")
    assert rec.ok and rec.kind == "pdf" and (tmp_path / paths.PDFS / "r-2.pdf").exists()


def test_html_recognised_by_sniffing_when_content_type_missing(make, tmp_path):
    f = make(Site({"/h": httpx.Response(200, content=HTML, headers={"content-type": "application/octet-stream"})}))
    rec = f.fetch("https://example.org/h", "h-1")
    assert rec.ok and rec.kind == "html"


@pytest.mark.parametrize("status", [404, 500, 403, 429])
def test_non_200_fails_and_is_logged_without_file(make, tmp_path, status):
    f = make(Site({"/x": httpx.Response(status, content=b"nope", headers={"content-type": "text/html"})}))
    rec = f.fetch("https://example.org/x", "x-1")
    assert not rec.ok and rec.status == status and rec.note == f"HTTP {status}"
    assert rec.path is None
    assert not (tmp_path / paths.PAGES).exists()
    assert log_lines(f)[0]["status"] == status


def test_robots_disallow_blocks_page_request(make):
    site = Site({"/private/p": html_resp()}, robots=ROBOTS_ALLOW)
    f = make(site)
    rec = f.fetch("https://example.org/private/p", "p-1")
    assert not rec.ok and "robots.txt" in rec.note and rec.status is None
    assert "/private/p" not in site.paths  # never requested
    assert log_lines(f)[0]["note"] == rec.note


def test_robots_allows_other_paths(make):
    site = Site({"/open": html_resp()}, robots=ROBOTS_ALLOW)
    rec = make(site).fetch("https://example.org/open", "o-1")
    assert rec.ok


def test_robots_missing_404_allows_everything(make):
    site = Site({"/a": html_resp()}, robots=httpx.Response(404))
    assert make(site).fetch("https://example.org/a", "a").ok


@pytest.mark.parametrize("status", [401, 403, 500, 503])
def test_robots_forbidden_or_server_error_blocks_everything(make, status):
    site = Site({"/a": html_resp()}, robots=httpx.Response(status))
    rec = make(site).fetch("https://example.org/a", "a")
    assert not rec.ok and "robots.txt" in rec.note
    assert "/a" not in site.paths


def test_robots_connection_error_blocks_everything(make):
    site = Site({"/a": html_resp()}, robots=httpx.ConnectError("down"))
    rec = make(site).fetch("https://example.org/a", "a")
    assert not rec.ok and "robots.txt" in rec.note and "/a" not in site.paths


def test_robots_fetched_once_per_origin(make):
    site = Site({"/a": html_resp(), "/b": html_resp()}, robots=httpx.Response(404))
    f = make(site)
    f.fetch("https://example.org/a", "a")
    f.fetch("https://example.org/b", "b")
    assert site.paths.count("/robots.txt") == 1


def test_robots_cached_per_origin_separately(make):
    site = Site({"/a": html_resp()}, robots=httpx.Response(404))
    f = make(site)
    f.robots("https://example.org/a")
    f.robots("https://other.org/a")
    f.robots("https://example.org/zzz")
    assert [r.url.host for r in site.requests] == ["example.org", "other.org"]


def test_timeout_is_a_logged_failure(make):
    f = make(Site({"/slow": httpx.ReadTimeout("slow")}))
    rec = f.fetch("https://example.org/slow", "s-1")
    assert not rec.ok and rec.note == "request failed: ReadTimeout" and rec.status is None
    assert log_lines(f)[0]["path"] is None


def test_connection_error_is_a_logged_failure(make):
    f = make(Site({"/c": httpx.ConnectError("refused")}))
    rec = f.fetch("https://example.org/c", "c-1")
    assert not rec.ok and rec.note == "request failed: ConnectError"


def test_oversized_response_rejected(make, monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_mod, "MAX_BYTES", 50)
    f = make(Site({"/big": httpx.Response(200, content=b"<html>" + b"x" * 100, headers={"content-type": "text/html"})}))
    rec = f.fetch("https://example.org/big", "big")
    assert not rec.ok and rec.note == "file larger than 60 MB" and rec.status == 200
    assert not (tmp_path / paths.PAGES).exists()


def test_body_exactly_at_limit_is_accepted(make, monkeypatch):
    monkeypatch.setattr(fetch_mod, "MAX_BYTES", len(HTML))
    assert make(Site({"/ok": html_resp()})).fetch("https://example.org/ok", "ok").ok


def test_unsupported_content_type(make, tmp_path):
    f = make(Site({"/i.png": httpx.Response(200, content=b"\x89PNG\r\n", headers={"content-type": "image/png"})}))
    rec = f.fetch("https://example.org/i.png", "img")
    assert not rec.ok and rec.note == "unsupported content type image/png" and rec.status == 200
    assert not (tmp_path / paths.PAGES).exists() and not (tmp_path / paths.PDFS).exists()


def test_unsupported_json_without_content_type(make):
    f = make(Site({"/j": httpx.Response(200, content=b'{"a": 1}')}))
    rec = f.fetch("https://example.org/j", "j")
    assert not rec.ok and "unsupported content type" in rec.note


def test_redirect_followed_and_final_url_recorded(make, tmp_path):
    site = Site({
        "/old": httpx.Response(301, headers={"location": "https://example.org/new?token=SECRET&id=1"}),
        "/new": html_resp(),
    })
    f = make(site)
    rec = f.fetch("https://example.org/old", "r")
    assert rec.ok
    assert rec.url == "https://example.org/old"
    assert rec.final_url == "https://example.org/new?id=1"
    assert "SECRET" not in f.log_path.read_text()


def test_redirect_loop_is_a_logged_failure(make):
    site = Site({"/a": httpx.Response(302, headers={"location": "/a"})})
    rec = make(site).fetch("https://example.org/a", "loop")
    assert not rec.ok and rec.note.startswith("request failed")


def test_already_downloaded_is_not_fetched_again(make):
    site = Site({"/a": html_resp()})
    f = make(site)
    first = f.fetch("https://example.org/a", "a")
    n = len(site.requests)
    again = f.fetch("https://example.org/a", "a")
    assert len(site.requests) == n
    assert again.ok and again.path == first.path and "already downloaded" in again.note
    assert len(log_lines(f)) == 1  # nothing new logged


def test_existing_file_not_in_log_is_not_overwritten(make, tmp_path):
    page = tmp_path / paths.PAGES / "a.html"
    page.parent.mkdir(parents=True)
    page.write_bytes(b"ORIGINAL")
    f = make(Site({"/a": html_resp()}))
    rec = f.fetch("https://example.org/a", "a")
    assert not rec.ok and "not overwritten" in rec.note
    assert page.read_bytes() == b"ORIGINAL"


def test_failed_earlier_attempt_is_retried(make):
    responses = iter([httpx.Response(500), html_resp()])
    f = make(Site({"/a": lambda req: next(responses)}))
    assert not f.fetch("https://example.org/a", "a").ok
    assert f.fetch("https://example.org/a", "a").ok
    assert len(log_lines(f)) == 2


def test_secret_query_not_in_log_record_or_file_names(make, tmp_path):
    site = Site({"/a": html_resp()})
    f = make(site)
    rec = f.fetch("https://example.org/a?x-craft-preview=SECRET1&token=SECRET2&id=7", "a")
    assert rec.ok
    # the token was sent on the wire ...
    assert "SECRET1" in str(site.requests[-1].url)
    # ... but is not stored anywhere
    blob = f.log_path.read_text() + json.dumps(rec.__dict__)
    assert "SECRET1" not in blob and "SECRET2" not in blob
    assert rec.url == "https://example.org/a?id=7"
    assert rec.note == "fetched with an access token that is not stored"
    for p in tmp_path.rglob("*"):
        assert "SECRET" not in p.name


def test_secret_not_logged_on_failure_either(make):
    f = make(Site({"/a": httpx.Response(500)}))
    rec = f.fetch("https://example.org/a?token=SECRET", "a")
    assert not rec.ok
    assert "SECRET" not in f.log_path.read_text()


def test_user_agent_sent(make):
    site = Site({"/a": html_resp()})
    make(site).fetch("https://example.org/a", "a")
    assert all(r.headers["user-agent"] == fetch_mod.USER_AGENT for r in site.requests)


# --- delay between requests ---------------------------------------------

def test_delay_requested_between_requests_to_same_host(make, sleeps):
    f = make(Site({"/a": html_resp(), "/b": html_resp()}), delay=2.0)
    f.fetch("https://example.org/a", "a")
    first = list(sleeps)
    f.fetch("https://example.org/b", "b")
    assert len(sleeps) > len(first)  # a wait was asked for before the next request
    assert all(0 < s <= 2.0 for s in sleeps)


def test_robots_and_page_request_are_spaced(make, sleeps):
    f = make(Site({"/a": html_resp()}), delay=2.0)
    f.fetch("https://example.org/a", "a")
    # robots.txt then the page, same host: the page waits (almost the full delay)
    assert len(sleeps) == 1 and sleeps[0] == pytest.approx(2.0, abs=0.5)


def test_no_sleep_for_different_hosts(make, sleeps):
    f = make(Site({"/a": html_resp()}), delay=2.0)
    f.robots("https://one.org/a")
    f.robots("https://two.org/a")
    assert sleeps == []


def test_zero_delay_never_sleeps(make, sleeps):
    f = make(Site({"/a": html_resp(), "/b": html_resp()}), delay=0)
    f.fetch("https://example.org/a", "a")
    f.fetch("https://example.org/b", "b")
    assert sleeps == []


def test_default_delay_is_at_least_two_seconds():
    assert fetch_mod.MIN_DELAY_SECONDS >= 2.0
    f = Fetcher("unused-root-never-written")
    try:
        assert f.delay == fetch_mod.MIN_DELAY_SECONDS
    finally:
        f.close()


def test_failure_records_have_all_log_fields(make):
    f = make(Site({"/a": httpx.Response(404)}))
    f.fetch("https://example.org/a", "a")
    rec = log_lines(f)[0]
    assert set(rec) == {"id", "url", "final_url", "status", "kind", "content_type", "path",
                        "sha256", "bytes", "retrieved", "note", "duplicate_of"}


# --- "do we already hold this?" checks ---------------------------------------

def test_match_key_ignores_scheme_www_and_trailing_slash():
    k = fetch_mod.match_key
    assert k("http://www.Example.org/a/") == k("https://example.org/a")
    assert k("https://example.org/a?utm_source=x") == k("https://example.org/a")
    assert k("https://example.org/a") != k("https://example.org/b")
    assert k("https://example.org/a?id=1") != k("https://example.org/a?id=2")
    assert k("https://doi.org/10.1000/ABC") == k("http://dx.doi.org/10.1000/abc")


def test_same_address_under_another_id_is_not_requested(make):
    site = Site({"/a": html_resp()})
    f = make(site)
    first = f.fetch("https://example.org/a", "a")
    before = len(site.requests)
    again = f.fetch("http://www.example.org/a/", "b")
    assert len(site.requests) == before  # nothing went to the network
    assert not again.ok and again.duplicate_of == "a" and again.path == first.path
    assert log_lines(f)[-1]["duplicate_of"] == "a"


def test_redirect_to_a_held_document_is_not_stored_twice(make, tmp_path):
    site = Site({
        "/a": html_resp(),
        "/old": httpx.Response(301, headers={"location": "https://example.org/a"}),
    })
    f = make(site)
    f.fetch("https://example.org/a", "a")
    got = f.fetch("https://example.org/old", "old")
    assert got.duplicate_of == "a"
    assert not (tmp_path / paths.PAGES / "old.html").exists()


def test_identical_bytes_at_a_different_address_are_not_stored_twice(make, tmp_path):
    site = Site({"/a.pdf": httpx.Response(200, content=PDF, headers={"content-type": "application/pdf"}),
                 "/mirror.pdf": httpx.Response(200, content=PDF, headers={"content-type": "application/pdf"})})
    f = make(site)
    f.fetch("https://example.org/a.pdf", "a")
    got = f.fetch("https://example.org/mirror.pdf", "m")
    assert got.duplicate_of == "a" and not (tmp_path / paths.PDFS / "m.pdf").exists()


def test_a_duplicate_record_is_never_itself_treated_as_the_held_copy(make):
    site = Site({"/a": html_resp()})
    f = make(site)
    f.fetch("https://example.org/a", "a")
    f.fetch("https://www.example.org/a", "b")
    assert f.fetch("https://example.org/a/", "c").duplicate_of == "a"
