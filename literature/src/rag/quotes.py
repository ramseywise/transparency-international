"""Check that every quote in a reading record really is in the source.

A reading record is written by a language model. This check uses no model: each
quote is looked up in the text extracted from the source. A quote that cannot be
found is either a misquote or an invented one, and must be fixed or removed before
the record is used.

Results per quote:
  ok            found, and on the page the record gives (PDF) or anywhere (web page)
  wrong_page    found, but on a different page from the one given
  not_found     not in the source text
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from rag import paths

QUOTE_FIELDS = ("definitions", "proxies", "findings", "limitations")
_ELLIPSIS = re.compile(r"\s*(?:\[\s*(?:\.\.\.|…)\s*\]|\(\s*(?:\.\.\.|…)\s*\)|\.\.\.|…)\s*")
_TRANSLATE = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
    "–": "-", "—": "-", "‐": "-", "‑": "-", "−": "-", "­": "", " ": " ",
})


# zero-width space, non-joiner, joiner, word joiner, byte-order mark: written as numbers so
# that no invisible character sits in this file
_ZERO_WIDTH = dict.fromkeys((0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF))


def normalise(text: str) -> str:
    """Lower case, plain quotes and dashes, single spaces. Wording is not touched."""
    text = unicodedata.normalize("NFKC", text or "").translate(_TRANSLATE)
    # invisible zero-width characters (some PDF exports put one round every word) are not wording
    text = text.translate(_ZERO_WIDTH)
    return re.sub(r"\s+", " ", text).strip().lower()


def _strings(node) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [s for v in node.values() for s in _strings(v)]
    if isinstance(node, list):
        return [s for v in node for s in _strings(v)]
    return []


def source_text(doc: dict) -> tuple[str, dict[int, tuple[str, str]]]:
    """The whole text of an extracted source, and the text of each page if it has pages."""
    if doc.get("pages"):
        # running text and table cells are kept apart, so that a table at the foot of a
        # page does not sit between the two halves of a sentence that crosses the page break
        pages = {p["page"]: (normalise(" ".join(_strings(p.get("blocks")))),
                             normalise(" ".join(_strings(p.get("tables")))))
                 for p in doc["pages"]}
        whole = " ".join([t for t, _ in pages.values()] + [t for _, t in pages.values()])
        return whole, pages
    parts = [doc.get("title") or "", doc.get("description") or ""]
    parts += _strings(doc.get("sections")) + _strings(doc.get("figures"))
    return normalise(" ".join(parts)), {}


def _segments(quote: str) -> list[str]:
    """A quote with an ellipsis is checked piece by piece."""
    quote = quote.strip().strip('"“”')
    return [s for s in (normalise(p).strip(" .,;:") for p in _ELLIPSIS.split(quote)) if len(s) >= 3]


def _page_number(page) -> int | None:
    if isinstance(page, int):
        return page
    m = re.fullmatch(r"\s*(?:pp?\.?\s*)?(\d+)\s*", str(page or ""))
    return int(m.group(1)) if m else None


def check_quote(quote: str, page, whole: str, pages: dict) -> str:
    segs = _segments(quote)
    if not segs or not all(s in whole for s in segs):
        return "not_found"
    n = _page_number(page)
    if pages and n is not None:
        # a quote may run over a page break, so the next page counts as well
        (text, tables), (next_text, next_tables) = pages.get(n, ("", "")), pages.get(n + 1, ("", ""))
        here = " ".join((text, next_text, tables, next_tables))
        if not all(s in here for s in segs):
            return "wrong_page"
    return "ok"


def check_record(record: dict, doc: dict) -> list[dict]:
    whole, pages = source_text(doc)
    out = []
    for field in QUOTE_FIELDS:
        for i, item in enumerate(record.get(field) or []):
            quote = (item or {}).get("quote")
            if not quote:
                continue
            out.append({"id": record.get("id"), "field": field, "item": i, "page": item.get("page"),
                        "quote": quote, "result": check_quote(quote, item.get("page"), whole, pages)})
    return out


def check_all(root: Path | str = "literature", ids: list[str] | None = None) -> dict:
    """Check every reading record under root/records against root/data/processed/text."""
    root = Path(root)
    results, problems = [], []
    for path in sorted((root / paths.RECORDS).glob("*.json")):
        if ids and path.stem not in ids:
            continue
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            problems.append({"id": path.stem, "problem": f"the record is not valid JSON: {e}"})
            continue
        text = root / paths.TEXT / f"{path.stem}.json"
        if not text.exists():
            problems.append({"id": path.stem, "problem": "no extracted text to check against"})
            continue
        results += check_record(record | {"id": path.stem}, json.loads(text.read_text()))
    tally = {k: sum(r["result"] == k for r in results) for k in ("ok", "wrong_page", "not_found")}
    return {
        "records": len({r["id"] for r in results}),
        "quotes": len(results),
        **tally,
        "share_ok": round(tally["ok"] / len(results), 3) if results else None,
        "problems": problems,
        "failures": [r for r in results if r["result"] != "ok"],
    }
