"""Offline tests for the pure parts of rag.fetch. No network."""

import json

from rag import paths
from rag.fetch import Fetched, Fetcher, Robots, has_secret, normalise_url, redact_url


def test_normalise_lowercases_scheme_and_host_and_fills_path():
    assert normalise_url("HTTPS://Example.ORG") == "https://example.org/"
    assert normalise_url("  https://Example.org/Path/A  ") == "https://example.org/Path/A"


def test_normalise_drops_fragment_and_tracking_params():
    url = "https://example.org/a?utm_source=x&id=3&fbclid=zz&utm_medium=m#frag"
    assert normalise_url(url) == "https://example.org/a?id=3"


def test_normalise_keeps_trailing_slash_and_blank_values():
    assert normalise_url("https://example.org/a/") != normalise_url("https://example.org/a")
    assert normalise_url("https://example.org/a?q=") == "https://example.org/a?q="


def test_normalise_does_not_strip_secrets():
    # By design redact_url does that; normalise_url alone leaves tokens in.
    assert "token=abc" in normalise_url("https://example.org/a?token=abc")


def test_redact_removes_secret_params_only():
    url = "https://example.org/a?x-craft-preview=SECRET&token=t&access_token=a&key=k&id=3&q=hello world"
    out = redact_url(url)
    assert "SECRET" not in out and "token" not in out and "key=" not in out
    assert "id=3" in out and "q=hello+world" in out


def test_redact_drops_fragment_and_keeps_scheme_host_case():
    assert redact_url("https://Example.org/a#frag") == "https://Example.org/a"


def test_redact_clean_url_unchanged():
    assert redact_url("https://example.org/a?id=3") == "https://example.org/a?id=3"


def test_has_secret():
    assert has_secret("https://example.org/a?token=abc")
    assert has_secret("https://example.org/a?id=1&x-craft-preview=abc")
    assert not has_secret("https://example.org/a?id=1")
    assert not has_secret("https://example.org/a")


def test_redacted_url_has_no_secret():
    assert not has_secret(redact_url("https://example.org/a?key=1&token=2"))


# --- Robots ---------------------------------------------------------------

def test_robots_no_text_follows_allow_all():
    assert Robots(None).allowed("https://x.org/anything")
    assert not Robots(None, allow_all=False).allowed("https://x.org/anything")


def test_robots_disallow_and_longer_allow_wins():
    r = Robots("User-agent: *\nDisallow: /private/\nAllow: /private/open\n")
    assert not r.allowed("https://x.org/private/secret")
    assert r.allowed("https://x.org/private/open/page")
    assert r.allowed("https://x.org/public")


def test_robots_wildcard_and_end_anchor():
    r = Robots("User-agent: *\nDisallow: /*.pdf$\n")
    assert not r.allowed("https://x.org/a/b.pdf")
    assert r.allowed("https://x.org/a/b.pdf?page=2")
    assert r.allowed("https://x.org/a/b.html")


def test_robots_disallow_everything_and_empty_disallow():
    assert not Robots("User-agent: *\nDisallow: /\n").allowed("https://x.org/")
    assert Robots("User-agent: *\nDisallow:\n").allowed("https://x.org/a")


def test_robots_own_group_beats_star_and_comments_ignored():
    text = (
        "User-agent: *  # everyone\nDisallow: /\n\n"
        "User-agent: foo\nUser-agent: research-crawler\nDisallow: /secret\n"
    )
    r = Robots(text)
    assert r.allowed("https://x.org/open")
    assert not r.allowed("https://x.org/secret/a")


def test_robots_query_is_part_of_the_match_target():
    r = Robots("User-agent: *\nDisallow: /search?\n")
    assert not r.allowed("https://x.org/search?q=1")
    assert r.allowed("https://x.org/search")


# --- Fetched / Fetcher without network ------------------------------------

def test_fetched_ok_depends_on_path():
    base = dict(id="a", url="u", final_url="u", status=200, kind="html", content_type="text/html",
                sha256="x", bytes=1, retrieved="2026-01-01")
    assert Fetched(path="p.html", **base).ok
    assert not Fetched(path=None, **base).ok


def test_fetch_non_web_scheme_fails_without_network_and_is_logged(tmp_path):
    f = Fetcher(tmp_path, delay=0)
    try:
        rec = f.fetch("ftp://example.org/file", "ftp-1")
    finally:
        f.close()
    assert not rec.ok and rec.note == "not a web address"
    logged = [json.loads(l) for l in f.log_path.read_text().splitlines()]
    assert logged[0]["id"] == "ftp-1" and logged[0]["path"] is None


def test_fetch_malformed_address_fails_without_network(tmp_path):
    f = Fetcher(tmp_path, delay=0)
    try:
        rec = f.fetch("https://doi:10.1088/1748-9326/aa815f", "bad-1")
    finally:
        f.close()
    assert not rec.ok and rec.note == "not a valid web address"


def test_fetch_secret_is_redacted_in_failure_record(tmp_path):
    f = Fetcher(tmp_path, delay=0)
    try:
        rec = f.fetch("ftp://example.org/f?token=SECRET", "x")
    finally:
        f.close()
    assert "SECRET" not in rec.url and "SECRET" not in f.log_path.read_text()


def test_existing_returns_latest_logged_download_whose_file_exists(tmp_path):
    f = Fetcher(tmp_path, delay=0)
    try:
        assert f.existing("a") is None
        page = tmp_path / paths.PAGES / "a.html"
        page.parent.mkdir(parents=True)
        page.write_text("<html></html>")
        base = dict(url="u", final_url="u", status=200, kind="html", content_type="text/html",
                    sha256="x", bytes=13, retrieved="2026-01-01", note="")
        recs = [
            dict(id="a", path=str(page), **base),
            dict(id="a", path=str(tmp_path / "missing.html"), **base),  # file gone: ignored
            dict(id="b", path=None, **base),
        ]
        f.log_path.write_text("".join(json.dumps(r) + "\n" for r in recs))
        got = f.existing("a")
        assert got is not None and got.path == str(page)
        assert f.existing("b") is None
        # fetch() on a known id returns the earlier file and touches no network
        again = f.fetch("https://example.org/a", "a")
        assert again.ok and "already downloaded" in again.note
    finally:
        f.close()
