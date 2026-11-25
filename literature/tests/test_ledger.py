"""Offline tests for rag.ledger."""

import hashlib

from rag.ledger import Ledger, slug_id


def test_slug_doi():
    assert slug_id("https://doi.org/10.1234/ABC.5") == "doi-10-1234-abc-5"
    assert slug_id("https://dx.doi.org/10.1/x") == "doi-10-1-x"


def test_slug_normal_url():
    assert slug_id("https://www.example.org/reports/Annual-Report.pdf") == "example-annual-report"
    assert slug_id("https://example.org/") == "example-home"
    assert slug_id("https://news.example.co.uk/a/story.html") == "example-story"


def test_slug_query_adds_stable_hash():
    s = slug_id("https://example.org/page?id=3")
    assert s == "example-page-" + hashlib.sha1(b"id=3").hexdigest()[:6]
    assert s != slug_id("https://example.org/page?id=4")
    assert s == slug_id("https://example.org/page?id=3")


def test_slug_is_truncated():
    assert len(slug_id("https://example.org/" + "a" * 200)) <= 70


def test_add_new_row_defaults(tmp_path):
    led = Ledger(tmp_path)
    row = led.add("https://example.org/a", title="T")
    assert row["id"] == "example-a"
    assert row["status"] == "candidate"
    assert row["found_via"] == []
    assert row["title"] == "T"
    assert row["doi_or_url"] == "https://example.org/a"


def test_add_same_url_after_normalisation_returns_same_row(tmp_path):
    led = Ledger(tmp_path)
    a = led.add("https://example.org/a")
    b = led.add("HTTPS://Example.org/a?utm_source=x#frag")
    assert a is b
    assert len(led.rows) == 1
    assert led.by_url("https://example.org/a?fbclid=1") is a


def test_add_redacts_secret_in_stored_url(tmp_path):
    led = Ledger(tmp_path)
    row = led.add("https://example.org/a?token=SECRET&id=1")
    assert "SECRET" not in row["doi_or_url"]
    assert led.add("https://example.org/a?id=1") is row


def test_found_via_appended_without_duplicates(tmp_path):
    led = Ledger(tmp_path)
    led.add("https://example.org/a", found_via="s1 (para 1)")
    led.add("https://example.org/a", found_via="s1 (para 1)")
    row = led.add("https://example.org/a", found_via="s2 (p.3)")
    assert row["found_via"] == ["s1 (para 1)", "s2 (p.3)"]


def test_fields_fill_only_when_empty_except_overwrite_set(tmp_path):
    led = Ledger(tmp_path)
    led.add("https://example.org/a", title="First", year=2020, status="in", reason="r1", file="f1", text="t1")
    row = led.add(
        "https://example.org/a", title="Second", year=2021, anchor="anch",
        status="out", reason="r2", file="f2", text="t2",
    )
    assert row["title"] == "First" and row["year"] == 2020
    assert row["anchor"] == "anch"  # was empty, so filled
    assert (row["status"], row["reason"], row["file"], row["text"]) == ("out", "r2", "f2", "t2")


def test_none_never_overwrites(tmp_path):
    led = Ledger(tmp_path)
    led.add("https://example.org/a", title="T", status="in", reason="why")
    row = led.add("https://example.org/a", title=None, status=None, reason=None)
    assert (row["title"], row["status"], row["reason"]) == ("T", "in", "why")


def test_id_collision_gets_suffix(tmp_path):
    led = Ledger(tmp_path)
    a = led.add("https://example.org/a/page")
    b = led.add("https://www.example.com/b/page")
    c = led.add("https://example.net/c/page")
    assert a["id"] == "example-page"
    assert b["id"] == "example-page-2"
    assert c["id"] == "example-page-3"
    assert led.get("example-page-2") is b


def test_add_by_id_returns_existing_row(tmp_path):
    led = Ledger(tmp_path)
    a = led.add("https://example.org/a", id="mine")
    assert led.add(None, id="mine", title="X") is a
    assert a["title"] == "X"


def test_add_without_url(tmp_path):
    led = Ledger(tmp_path)
    row = led.add(None, id="no-url", title="Manual entry")
    assert row["doi_or_url"] is None and row["id"] == "no-url"


def test_save_and_reload_round_trip(tmp_path):
    led = Ledger(tmp_path)
    led.add("https://example.org/a", title="Café société", found_via="s (para 2)", year=2022)
    led.add("https://doi.org/10.1/x", status="in")
    led.save()
    assert (tmp_path / "ledger.jsonl").exists()
    assert not list(tmp_path.glob("*.tmp"))

    again = Ledger(tmp_path)
    assert again.rows == led.rows
    assert again.get("example-a")["title"] == "Café société"
    assert again.by_url("https://EXAMPLE.org/a?utm_x=1") is again.get("example-a")
    # adding again after reload does not duplicate
    again.add("https://example.org/a", found_via="s (para 2)")
    assert len(again.rows) == 2
    assert again.get("example-a")["found_via"] == ["s (para 2)"]


def test_save_creates_missing_folder(tmp_path):
    led = Ledger(tmp_path / "new" / "dir")
    led.add("https://example.org/a")
    led.save()
    assert (tmp_path / "new" / "dir" / "ledger.jsonl").exists()


def test_a_full_stop_printed_after_a_link_is_not_part_of_the_address(tmp_path):
    """A reference list prints "https://site.org/a/report/." - the same document as without the stop."""
    assert slug_id("https://www.example.org/campaigns/some-report/.") == "example-some-report"
    led = Ledger(tmp_path)
    first = led.add("https://www.example.org/campaigns/some-report/")
    again = led.add("https://www.example.org/campaigns/some-report/.", found_via="book (p.3)")
    assert again is first and len(led.rows) == 1
    new = led.add("https://other.example.org/x/y.pdf.")
    assert new["doi_or_url"] == "https://other.example.org/x/y.pdf"
    assert led.add("https://doi.org/10.1044/1058-0360(2002/007)")["doi_or_url"].endswith("(2002/007)")
