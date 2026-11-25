"""Offline tests for rag.extract with synthetic pages and a tiny generated PDF."""

import pymupdf
import pytest

from rag.extract import classify_link, extract_html, extract_pdf

PAGE = "https://www.example.org/news/post"


@pytest.mark.parametrize("url,expected", [
    ("https://www.example.org/other", "internal"),
    ("https://blog.example.org/x", "internal"),
    ("https://example.org/x?y=1", "internal"),
    ("https://example.org/files/report.PDF", "download"),
    ("https://other.org/data.xlsx", "download"),
    ("https://files.transparencycdn.org/images/pic", "download"),
    ("https://other.com/study", "external"),
    ("mailto:a@example.org", "boilerplate"),
    ("tel:+4912345", "boilerplate"),
    ("https://twitter.com/intent/tweet?url=x", "boilerplate"),
    ("https://www.facebook.com/sharer/sharer.php?u=x", "boilerplate"),
    ("https://wa.me/123", "boilerplate"),
    ("https://www.linkedin.com/company/example", "boilerplate"),
    ("https://www.youtube.com/watch?v=1", "boilerplate"),
    ("https://www.example.org/news/post", "boilerplate"),
    ("https://www.example.org/news/post?utm_source=x#top", "boilerplate"),
])
def test_classify_link(url, expected):
    assert classify_link(url, PAGE) == expected


def test_classify_link_to_self_ignores_www():
    assert classify_link("https://example.org/news/post", PAGE) == "boilerplate"


HTML = """<html lang="en"><head><title>Tab title</title>
<meta property="og:site_name" content="Example Site">
<script type="application/ld+json">
{"@type":"Article","headline":"LD headline","datePublished":"2024-05-06T10:00:00+00:00",
 "dateModified":"2024-06-01T00:00:00+00:00","author":{"name":"Jane Doe"}}
</script></head><body>
<header><p>Header junk words</p></header>
<nav><p>Nav junk words</p></nav>
<main>
<h1>Real   Title</h1>
<p>T<span>he</span> first paragraph has <a href="https://other.org/study">a study</a> inside.</p>
<h2>Section Two</h2>
<p>Second paragraph with <a href="/internal/page">internal</a> and <a href="mailto:a@b.c">mail</a>.</p>
<a href="https://linked.org/card"><p>Card paragraph text</p></a>
<div class="callout"><p>Callout title text</p><a href="https://callout.org/more"><svg></svg>Read more</a></div>
<aside><p>Aside kept text</p></aside>
<div class="taxonomies"><ul><li>TagOne</li></ul></div>
<article class="bg-light-grey-300"><p>Related card text</p><a href="https://related.org/x">r</a></article>
<iframe src="/embed/chart" title="A chart"></iframe>
</main>
<footer><p>Footer junk words</p></footer></body></html>"""


@pytest.fixture(scope="module")
def doc():
    return extract_html(HTML, PAGE, "src-1")


def _texts(doc):
    return [p["text"] for s in doc["sections"] for p in s["paragraphs"]]


def test_metadata(doc):
    assert doc["id"] == "src-1" and doc["kind"] == "html"
    assert doc["title"] == "Real Title"  # h1 beats ld+json headline and <title>
    assert doc["published"] == "2024-05-06"
    assert doc["modified"] == "2024-06-01"
    assert doc["authors"] == ["Jane Doe"]
    assert doc["site"] == "Example Site"
    assert doc["language"] == "en"


def test_title_falls_back_to_ld_json_then_title_tag():
    no_h1 = '<html><head><title>Tab</title><script type="application/ld+json">{"headline":"LD"}</script></head><body><main><p>Some text here for you.</p></main></body></html>'
    assert extract_html(no_h1, PAGE)["title"] == "LD"
    only_tab = "<html><head><title>Tab</title></head><body><main><p>Some text.</p></main></body></html>"
    assert extract_html(only_tab, PAGE)["title"] == "Tab"


def test_body_text_kept_and_furniture_dropped(doc):
    texts = _texts(doc)
    joined = " ".join(texts)
    assert "The first paragraph has a study inside." in texts  # inline tags do not split words
    assert "Card paragraph text" in texts
    assert "Callout title text" in texts
    for junk in ("Header junk", "Nav junk", "Footer junk", "TagOne", "Related card"):
        assert junk not in joined


def test_aside_inside_main_is_kept(doc):
    assert "Aside kept text" in _texts(doc)


def test_aside_dropped_when_there_is_no_main():
    html = "<html><body><article><p>Body text is here.</p><aside><p>Side junk text</p></aside></article></body></html>"
    texts = _texts(extract_html(html, PAGE))
    assert texts == ["Body text is here."]


def test_sections_and_paragraph_numbers(doc):
    heads = [s["heading"] for s in doc["sections"]]
    assert heads == [None, "Section Two"]
    nums = [p["n"] for s in doc["sections"] for p in s["paragraphs"]]
    assert nums == [1, 2, 3, 4, 5]


def test_inline_paragraph_links(doc):
    by_url = {l["url"]: l for l in doc["links"]}
    study = by_url["https://other.org/study"]
    assert (study["kind"], study["paragraph"], study["section"], study["anchor"]) == ("external", 1, None, "a study")
    assert study["context"] == "The first paragraph has a study inside."
    internal = by_url["https://www.example.org/internal/page"]
    assert (internal["kind"], internal["paragraph"], internal["section"]) == ("internal", 2, "Section Two")
    assert "Second paragraph" in internal["context"]
    assert not any(u.startswith("mailto") for u in by_url)


def test_link_wrapping_a_paragraph_is_captured(doc):
    card = next(l for l in doc["links"] if l["url"] == "https://linked.org/card")
    assert card["paragraph"] == 3
    assert card["anchor"] == "Card paragraph text"
    assert card["section"] == "Section Two"


def test_standalone_callout_link_captured_once_with_box_context(doc):
    hits = [l for l in doc["links"] if l["url"] == "https://callout.org/more"]
    assert len(hits) == 1
    link = hits[0]
    assert link["paragraph"] is None
    assert link["anchor"] == "Read more"
    assert "Callout title text" in link["context"]
    assert link["section"] == "Section Two"


def test_dropped_related_links_not_listed(doc):
    assert not any("related.org" in l["url"] for l in doc["links"])
    assert len(doc["links"]) == 4


def test_iframe_recorded_as_figure(doc):
    assert len(doc["figures"]) == 1
    fig = doc["figures"][0]
    assert fig["src"] == "https://www.example.org/embed/chart"
    assert fig["title"] == "A chart"
    assert fig["section"] == "Section Two"


def test_counts_consistent_with_lists(doc):
    c = doc["counts"]
    paras = [p for s in doc["sections"] for p in s["paragraphs"]]
    assert c["paragraphs"] == len(paras) == 5
    assert c["words"] == sum(len(p["text"].split()) for p in paras)
    assert c["links"] == len(doc["links"])
    assert c["links_by_kind"] == {"external": 3, "internal": 1}
    assert sum(c["links_by_kind"].values()) == c["links"]
    assert c["figures"] == len(doc["figures"])


def test_secret_token_not_kept_in_url():
    out = extract_html("<html><body><main><p>Some text here.</p></main></body></html>",
                       "https://www.example.org/a?x-craft-preview=SECRET&id=1")
    assert "SECRET" not in out["url"] and "SECRET" not in out["canonical_url"]


# --- PDF -----------------------------------------------------------------

@pytest.fixture
def pdf_path(tmp_path):
    pdf = pymupdf.open()
    p1 = pdf.new_page()
    p1.insert_text((72, 100), "Carbon budget overview for the sector", fontsize=12)
    # a wrapped link: two rectangles, one address
    for rect in (pymupdf.Rect(72, 88, 300, 104), pymupdf.Rect(72, 106, 150, 120)):
        p1.insert_link({"kind": pymupdf.LINK_URI, "from": rect, "uri": "https://other.org/report"})
    p1.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(72, 200, 150, 215),
                    "uri": "https://twitter.com/intent/tweet?text=x"})  # boilerplate: skipped
    p2 = pdf.new_page()
    p2.insert_text((72, 100), "Second page about lobbying registers", fontsize=12)
    p2.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(72, 88, 300, 104), "uri": "https://other.org/report"})
    p2.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(72, 300, 150, 315), "uri": "https://www.example.org/page"})
    path = tmp_path / "tiny.pdf"
    pdf.save(str(path))
    pdf.close()
    return path


def test_extract_pdf_pages_text_and_links(pdf_path):
    out = extract_pdf(pdf_path, "https://www.example.org/tiny.pdf", "pdf-1")
    assert out["kind"] == "pdf" and out["id"] == "pdf-1"
    assert out["page_count"] == 2 and len(out["pages"]) == 2
    assert out["counts"]["pages"] == 2

    page_text = [" ".join(p["blocks"]) for p in out["pages"]]
    assert "Carbon budget overview" in page_text[0]
    assert "lobbying registers" in page_text[1]

    ext = [l for l in out["links"] if l["url"] == "https://other.org/report"]
    assert sorted(l["page"] for l in ext) == [1, 2]  # one per page, wrapped rectangles merged
    assert all(l["kind"] == "external" for l in ext)
    internal = [l for l in out["links"] if l["url"] == "https://www.example.org/page"]
    assert len(internal) == 1 and internal[0]["kind"] == "internal" and internal[0]["page"] == 2
    assert not any("twitter" in l["url"] for l in out["links"])
    assert out["counts"]["links"] == len(out["links"]) == 3


# --- PDF: line breaks, columns, broken paragraphs ---------------------------

from rag.extract import _hyphen_fixer, _join_lines, _merge_broken_paragraphs, _order_blocks


def test_hyphen_at_a_line_break_follows_the_documents_own_spelling():
    raw = ("The most vulnerable states spoke.\nA fossil fuel-linked firm.\n"
           "vulnera-\nble and fuel-\nlinked and non-\nstate and COP-\n29 and Nether-\nlands")
    out = _join_lines(raw, _hyphen_fixer(raw))
    assert "vulnerable and fuel-linked and non-state and COP-29 and Netherlands" in out


def test_without_a_fixer_the_hyphen_is_kept():
    assert _join_lines("vulnera-\nble") == "vulnera-ble"


def test_letter_spaced_heading_is_joined():
    assert _join_lines("T A B L E of contents") == "TABLE of contents"
    assert _join_lines("a b c") == "a b c"  # three letters are not a heading


def _b(x0, y0, x1, text):
    return (x0, y0, x1, y0 + 10, text)


def test_two_column_page_reads_left_column_first_inside_each_band():
    words = " ".join(["word"] * 30)
    blocks = [
        _b(320, 100, 560, "R1 " + words), _b(40, 100, 280, "L1 " + words),
        _b(40, 300, 560, "HEADING across both columns"),
        _b(320, 400, 560, "R2 " + words), _b(40, 420, 280, "L2 " + words),
        _b(40, 200, 280, "L1b " + words),
    ]
    order = [b[4].split()[0] for b in _order_blocks(blocks, 600)]
    assert order == ["L1", "L1b", "R1", "HEADING", "L2", "R2"]


def test_single_column_page_reads_top_to_bottom():
    blocks = [_b(40, 300, 560, "third"), _b(40, 100, 560, "first"), _b(40, 200, 250, "second")]
    assert [b[4] for b in _order_blocks(blocks, 600)] == ["first", "second", "third"]


def test_paragraph_split_in_two_blocks_is_joined():
    kept = [{"bbox": [40, 100, 280, 150], "text": "The report finds that most delegates on overflow badges came from"},
            {"bbox": [40, 160, 280, 200], "text": "the private sector and from state firms."},
            {"bbox": [40, 210, 280, 220], "text": "A new paragraph."}]
    out = _merge_broken_paragraphs(kept)
    assert [o["text"] for o in out][0].endswith("came from the private sector and from state firms.")
    assert len(out) == 2 and out[0]["bbox"] == [40, 100, 280, 200]


def test_short_heading_and_bullets_are_not_joined_to_what_follows():
    kept = [{"bbox": [0, 0, 1, 1], "text": "Key findings"}, {"bbox": [0, 2, 1, 3], "text": "delegates were counted."},
            {"bbox": [0, 4, 1, 5], "text": "• one two three four five six seven eight nine"},
            {"bbox": [0, 6, 1, 7], "text": "another line"}]
    assert len(_merge_broken_paragraphs(kept)) == 4


def test_pdf_table_kept_beside_the_text(tmp_path):
    pdf = pymupdf.open()
    page = pdf.new_page()
    rows = [("Badge", "Delegates"), ("Party", "1381"), ("Overflow", "2440")]
    for i, (a, b) in enumerate(rows):
        y = 100 + 20 * i
        page.insert_text((75, y + 14), a, fontsize=10)
        page.insert_text((205, y + 14), b, fontsize=10)
        for x0, x1 in ((72, 200), (200, 330)):
            page.draw_rect(pymupdf.Rect(x0, y, x1, y + 20))
    path = tmp_path / "table.pdf"
    pdf.save(str(path))
    pdf.close()
    out = extract_pdf(path, None, "t")
    assert out["counts"]["tables"] == 1
    got = [[c for c in row if c] for row in out["pages"][0]["tables"][0]["rows"]]
    assert got == [list(r) for r in rows]
    assert "Overflow" in " ".join(out["pages"][0]["blocks"])
