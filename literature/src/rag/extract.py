"""Turn a raw web page or PDF into structured, searchable JSON.

The output keeps three things apart: the text (by section and paragraph, or by
page), the document's own metadata, and every outgoing link with the sentence
it sat in. On web pages the links are the reference list.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from rag.fetch import normalise_url, redact_url

DOWNLOAD_EXT = (".pdf", ".xlsx", ".xls", ".csv", ".docx", ".doc", ".zip", ".pptx")
DOWNLOAD_HOSTS = {"files.transparencycdn.org"}
SHARE_PATTERNS = (
    "facebook.com/sharer", "twitter.com/intent", "x.com/intent", "twitter.com/share",
    "api.whatsapp.com", "wa.me/", "linkedin.com/share", "linkedin.com/sharing",
    "t.me/share", "bsky.app/intent",
)
SOCIAL_HOSTS = {
    "facebook.com", "twitter.com", "x.com", "instagram.com", "linkedin.com", "youtube.com",
    "tiktok.com", "bsky.app", "threads.net", "threads.com",
}
# Page furniture removed before reading. Generic first, then site-specific.
DROP_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "form", "svg", "button"]
DROP_SELECTORS = [
    "article.bg-light-grey-300",  # transparency.org: related-article cards
    "div.taxonomies",             # transparency.org: tag lists
    "div.no-llm",                 # transparency.org: video embed block
    "[class*=share]", "[class*=social]", "[class*=newsletter]", "[class*=cookie]", "[class*=breadcrumb]",
]
TEXT_TAGS = ["p", "li", "blockquote", "td", "th", "figcaption"]


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace(" ", " ")).strip()


def _host(url: str) -> str:
    h = urlsplit(url).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def classify_link(url: str, page_url: str) -> str:
    """internal | download | external | boilerplate"""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return "boilerplate"
    low = url.lower()
    if any(p in low for p in SHARE_PATTERNS):
        return "boilerplate"
    host, page_host = _host(url), _host(page_url)
    if host in SOCIAL_HOSTS:
        return "boilerplate"
    if parts.path.lower().endswith(DOWNLOAD_EXT) or host in DOWNLOAD_HOSTS:
        return "download"
    site = ".".join(page_host.split(".")[-2:]) if page_host else ""
    if site and (host == site or host.endswith("." + site)):
        same_path = urlsplit(url).path.rstrip("/") == urlsplit(page_url).path.rstrip("/")
        if host == page_host and same_path:
            return "boilerplate"  # link to the page itself
        return "internal"
    return "external"


def _ld_json(soup: BeautifulSoup) -> dict:
    out: dict = {}
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (ValueError, TypeError):
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            for key in ("datePublished", "dateModified", "headline"):
                if item.get(key) and key not in out:
                    out[key] = item[key]
            author = item.get("author")
            if author and "author" not in out:
                authors = author if isinstance(author, list) else [author]
                out["author"] = [a.get("name") if isinstance(a, dict) else str(a) for a in authors]
    return out


def _meta(soup: BeautifulSoup, *names: str) -> str | None:
    for n in names:
        tag = soup.find("meta", attrs={"property": n}) or soup.find("meta", attrs={"name": n})
        if tag and tag.get("content"):
            return _clean(tag["content"])
    return None


def extract_html(html: str | bytes, url: str, source_id: str | None = None) -> dict:
    soup = BeautifulSoup(html, "lxml")
    ld = _ld_json(soup)
    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical["href"] if canonical and canonical.get("href") else redact_url(url)
    h1 = soup.find("h1")
    title = (
        (_clean(h1.get_text()) if h1 else "") or ld.get("headline") or _meta(soup, "og:title")
        or _clean(soup.title.string if soup.title and soup.title.string else "")
    )
    authors = ld.get("author") or [_meta(soup, "author")]
    published = ld.get("datePublished") or _meta(soup, "article:published_time", "date", "citation_publication_date")
    doc = {
        "id": source_id,
        "kind": "html",
        "url": redact_url(url),
        "canonical_url": canonical_url,
        "title": title,
        "description": _meta(soup, "og:description", "description"),
        "site": _meta(soup, "og:site_name") or _host(url),
        "authors": [a for a in authors if a],
        "published": published[:10] if published else None,
        "modified": (ld.get("dateModified") or "")[:10] or None,
        "language": (soup.html.get("lang") if soup.html else None),
    }

    # The body is everything in <main> (or <article>, or the page) once the
    # furniture is removed. Summary and call-out boxes inside it are kept:
    # they carry references too.
    main = soup.find("main") or soup.find(attrs={"role": "main"})
    scope = main or soup.find("article") or soup.body or soup
    for tag in scope.find_all(DROP_TAGS + ([] if main else ["aside"])):
        tag.decompose()
    for sel in DROP_SELECTORS:
        for tag in scope.select(sel):
            tag.decompose()
    for tag in scope.find_all("section"):  # e.g. "Related" blocks left with only a heading
        if not tag.decomposed and not tag.find(TEXT_TAGS) and not tag.find("iframe"):
            tag.decompose()
    for br in scope.find_all("br"):
        br.replace_with(" ")

    sections: list[dict] = [{"heading": None, "level": 0, "paragraphs": []}]
    links: list[dict] = []
    figures: list[dict] = []
    n = 0
    text_tags = TEXT_TAGS
    for el in scope.find_all(["h1", "h2", "h3", "h4", "iframe", *text_tags]):
        if el.name in ("h1", "h2", "h3", "h4"):
            heading = _clean(el.get_text())
            if el.name == "h1" or not heading:
                continue
            sections.append({"heading": heading, "level": int(el.name[1]), "paragraphs": []})
            continue
        if el.name == "iframe":
            src = el.get("src") or el.get("data-src")
            if src:
                figures.append({
                    "src": urljoin(url, src), "title": el.get("title"),
                    "section": sections[-1]["heading"],
                    "note": "embedded chart or media; its data is not in the page text",
                })
            continue
        if el.find(text_tags):
            continue  # a container of smaller text blocks
        # No separator: inline tags can split a word ("T<span>he</span>").
        text = _clean(el.get_text())
        if not text:
            continue
        n += 1
        sections[-1]["paragraphs"].append({"n": n, "text": text})
        wrapping = el.find_parent("a", href=True)  # a linked card: <a><p>…</p></a>
        for a in ([wrapping] if wrapping else []) + el.find_all("a", href=True):
            href = urljoin(url, a["href"])
            kind = classify_link(href, url)
            if kind == "boilerplate":
                continue
            links.append({
                "url": normalise_url(href), "host": _host(href), "kind": kind,
                "anchor": _clean(a.get_text()), "paragraph": n,
                "section": sections[-1]["heading"], "context": text[:600],
            })

    # Links that stand beside the text rather than in it, e.g. a call-out box
    # with a title and a "read more" arrow. The box's own text is the context.
    seen = {l["url"] for l in links}
    for a in scope.find_all("a", href=True):
        if a.find_parent(TEXT_TAGS) or a.find(TEXT_TAGS):
            continue
        href = urljoin(url, a["href"])
        kind = classify_link(href, url)
        if kind == "boilerplate" or normalise_url(href) in seen:
            continue
        seen.add(normalise_url(href))
        box = a.find_parent(["div", "aside", "section", "figure"]) or a
        heading = a.find_previous(["h2", "h3", "h4"])
        links.append({
            "url": normalise_url(href), "host": _host(href), "kind": kind,
            "anchor": _clean(a.get_text()), "paragraph": None,
            "section": _clean(heading.get_text()) if heading else None,
            "context": _clean(box.get_text(" "))[:600],
        })

    doc["sections"] = [s for s in sections if s["paragraphs"] or s["heading"]]
    doc["links"] = links
    doc["figures"] = figures
    doc["counts"] = {
        "paragraphs": n,
        "words": sum(len(p["text"].split()) for s in sections for p in s["paragraphs"]),
        "links": len(links),
        "links_by_kind": dict(Counter(l["kind"] for l in links)),
        "figures": len(figures),
    }
    return doc


# Prefixes that are normally written with a hyphen before the word they modify.
HYPHEN_PREFIXES = {
    "non", "pre", "post", "sub", "mid", "anti", "co", "self", "semi", "multi", "inter", "intra",
    "pro", "quasi", "cross", "ex", "vice", "well", "long", "short", "high", "low",
}
BULLETS = "•▪◦●■‣∙"
_WORD = r"[^\W\d_]+"


def _hyphen_fixer(raw: str):
    """Decide, for each word broken over a line with a hyphen, whether the
    hyphen belongs to the word ("fuel-\nlinked") or only marks the break
    ("vulnera-\nble"). The document's own vocabulary is the evidence: how the
    word is written where it is not broken. Returns a function for re.sub.
    """
    unbroken = re.sub(r"\w+-\n\w+", " ", raw)
    words = {w.lower() for w in re.findall(_WORD, unbroken)}
    hyphenated = {w.lower() for w in re.findall(rf"{_WORD}(?:-{_WORD})+", unbroken)}

    def fix(m: re.Match) -> str:
        left, right = m.group(1), m.group(2)
        l, r = left.lower(), right.lower()
        l_last, r_first = re.split(r"[\W\d_]", l)[-1], re.split(r"[\W\d_]", r)[0]
        if l_last + r_first in words:
            return left + right
        if f"{l_last}-{r_first}" in hyphenated:
            return f"{left}-{right}"
        if l_last in words and r_first in words and len(r_first) >= 3:
            return f"{left}-{right}"
        if l_last in HYPHEN_PREFIXES or not right[0].islower() or not left[-1].isalpha():
            return f"{left}-{right}"
        return left + right

    return fix


def _join_lines(text: str, fix=None) -> str:
    """One paragraph from its lines. `fix` comes from _hyphen_fixer; without
    it a hyphen at a line break is kept, which never loses a real one."""
    text = re.sub(r"(\w+)-\n(\w+)", fix or (lambda m: f"{m.group(1)}-{m.group(2)}"), text)
    # Letter-spaced headings ("T A B L E   O F") stored as single letters.
    text = re.sub(
        r"(?<!\S)(?:\S ){3,}\S(?!\S)",
        lambda m: m.group(0).replace(" ", "") if all(len(t) == 1 for t in m.group(0).split(" ")) else m.group(0),
        text,
    )
    return _clean(text)


def _order_blocks(blocks: list[tuple], width: float) -> list[tuple]:
    """Reading order. On a two-column page a block that spans both columns
    (a heading, a wide figure caption) divides the page into bands; inside a
    band the left column is read before the right. Other pages: top to bottom.
    """
    middle = width / 2

    def side(b) -> str:
        if b[2] <= middle + 5:
            return "left"
        if b[0] >= middle - 5:
            return "right"
        return "full"

    sides = [side(b) for b in blocks]
    words = lambda want: sum(len(b[4].split()) for b, s in zip(blocks, sides) if s == want)
    if min(words("left"), words("right")) < 40:  # not a two-column page
        return sorted(blocks, key=lambda b: (round(b[1]), b[0]))
    top_down = sorted(zip(blocks, sides), key=lambda bs: (round(bs[0][1]), bs[0][0]))
    out, band = [], []

    def flush():
        out.extend(b for b, s in band if s == "left")
        out.extend(b for b, s in band if s == "right")
        band.clear()

    for b, s in top_down:
        if s == "full":
            flush()
            out.append(b)
        else:
            band.append((b, s))
    flush()
    return out


def _page_blocks(page) -> list[tuple]:
    """Text blocks of a page as (x0, y0, x1, y1, text), in reading order.

    A PDF may store its lines in any order (some layouts store a column bottom
    to top), so lines are re-sorted by position inside each block. A block
    holding several bullet points is split into one block per bullet.
    """
    blocks = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        lines = sorted(b["lines"], key=lambda l: (round(l["bbox"][1]), l["bbox"][0]))
        pieces: list[dict] = []
        last_y = None
        for line in lines:
            text = "".join(s["text"] for s in line["spans"])
            y = round(line["bbox"][1])
            new_row = y != last_y
            if not pieces or (new_row and text.lstrip()[:1] in BULLETS and text.strip()):
                pieces.append({"text": "", "boxes": []})
            pieces[-1]["text"] += ("\n" if new_row else " ") + text
            pieces[-1]["boxes"].append(line["bbox"])
            last_y = y
        for piece in pieces:
            text = piece["text"].strip("\n")
            if not text.strip():
                continue
            xs0, ys0, xs1, ys1 = zip(*piece["boxes"])
            box = b["bbox"] if len(pieces) == 1 else (min(xs0), min(ys0), max(xs1), max(ys1))
            blocks.append((*box, text))
    return _order_blocks(blocks, page.rect.width)


def _merge_broken_paragraphs(kept: list[dict]) -> list[dict]:
    """A paragraph the PDF stores as two blocks: the first stops without closing
    punctuation and the next starts in lower case. Joined back into one."""
    out: list[dict] = []
    for k in kept:
        prev = out[-1] if out else None
        if (prev and prev["text"][-1:].isalnum() or prev and prev["text"][-1:] == ",") \
                and k["text"][:1].islower() and len(prev["text"].split()) >= 8 \
                and prev["text"][:1] not in BULLETS + "0123456789":
            x0, y0, x1, y1 = prev["bbox"]
            a0, b0, a1, b1 = k["bbox"]
            prev["text"] += " " + k["text"]
            prev["bbox"] = [min(x0, a0), min(y0, b0), max(x1, a1), max(y1, b1)]
        else:
            out.append(dict(k))
    return out


def _page_tables(page) -> list[dict]:
    """Tables as rows of cells, kept beside the page text (which still holds
    the same words in reading order) so a reader can see which figure belongs
    to which row and column."""
    try:
        found = page.find_tables().tables
    except Exception:  # table detection is a heuristic; the page text is unaffected
        return []
    tables = []
    for t in found:
        rows = [[_clean(c or "") for c in row] for row in t.extract()]
        cells = [c for row in rows for c in row]
        if len(rows) < 2 or t.col_count < 2 or sum(bool(c) for c in cells) < len(cells) / 2:
            continue
        tables.append({"bbox": [round(v, 1) for v in t.bbox], "rows": rows})
    return tables


def extract_pdf(path: str | Path, url: str | None = None, source_id: str | None = None) -> dict:
    import pymupdf

    pdf = pymupdf.open(str(path))
    meta = {k: v for k, v in (pdf.metadata or {}).items() if v}
    raw_pages = [_page_blocks(page) for page in pdf]
    fix = _hyphen_fixer("\n".join(b[4] for blocks in raw_pages for b in blocks))

    # Running heads and page numbers: short text repeated on many pages.
    seen = Counter()
    for blocks in raw_pages:
        for t in {_join_lines(b[4], fix) for b in blocks}:
            if len(t) < 60:
                seen[re.sub(r"\d+", "#", t)] += 1
    furniture = {t for t, c in seen.items() if c >= max(4, pdf.page_count // 5)}

    pages, links = [], []
    for i, (page, blocks) in enumerate(zip(pdf, raw_pages), start=1):
        kept = []
        for b in blocks:
            text = _join_lines(b[4], fix)
            if not text or re.sub(r"\d+", "#", text) in furniture or text.isdigit():
                continue
            kept.append({"bbox": [round(v, 1) for v in b[:4]], "text": text})
        kept = _merge_broken_paragraphs(kept)
        pages.append({"page": i, "blocks": [k["text"] for k in kept], "tables": _page_tables(page)})
        for link in page.get_links():
            uri = link.get("uri")
            if not uri or not uri.startswith(("http://", "https://")):
                continue
            rect = link["from"]
            context = next(
                (k["text"] for k in kept if pymupdf.Rect(k["bbox"]).intersects(rect)), ""
            )
            kind = classify_link(uri, url or "https://invalid.example/")
            if kind == "boilerplate":
                continue
            links.append({
                "url": normalise_url(uri), "host": _host(uri), "kind": kind,
                "anchor": _join_lines(page.get_textbox(rect), fix), "page": i, "context": context[:600],
            })

    # A wrapped link is several rectangles with one address: keep one per page.
    unique, seen_links = [], set()
    for l in links:
        key = (l["url"], l["page"])
        if key not in seen_links:
            seen_links.add(key)
            unique.append(l)

    first_lines = [b for b in pages[0]["blocks"]] if pages else []
    words = sum(len(b.split()) for p in pages for b in p["blocks"])
    return {
        "id": source_id,
        "kind": "pdf",
        "url": redact_url(url) if url else None,
        "file": str(path),
        "title": meta.get("title") or " ".join(first_lines)[:200] or None,
        "authors": [meta["author"]] if meta.get("author") else [],
        "published": _pdf_date(meta.get("creationDate")),
        "modified": _pdf_date(meta.get("modDate")),
        "page_count": pdf.page_count,
        "pages": pages,
        "links": unique,
        "counts": {
            "pages": pdf.page_count, "words": words, "links": len(unique),
            "links_by_kind": dict(Counter(l["kind"] for l in unique)),
            "tables": sum(len(p["tables"]) for p in pages),
            "pages_without_text": [p["page"] for p in pages if not p["blocks"]],
        },
    }


def _pdf_date(value: str | None) -> str | None:
    m = re.match(r"D:(\d{4})(\d{2})(\d{2})", value or "")
    return f"{m[1]}-{m[2]}-{m[3]}" if m else None


def extract_file(path: str | Path, url: str | None = None, source_id: str | None = None) -> dict:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return extract_pdf(path, url, source_id)
    doc = extract_html(path.read_bytes(), url or f"file://{path}", source_id)
    doc["file"] = str(path)
    return doc
