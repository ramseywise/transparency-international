"""Choose the passages of one source that a reader needs, so it does not read the whole text.

A reading record asks for the same things from every source: what it set out to do,
its definitions, the indicators it used, its data and method, its findings and its
limitations. Most of a long report is none of these. This module splits a source
into the same passages as the search index, scores each passage for each of those
fields by keyword (BM25, no model, same answer every time), and keeps the best ones
up to a word budget. A source shorter than the budget is given whole.

What the reader gets is a file with the chosen passages in document order, each
with its page or paragraph, and a coverage line saying how much of the source that
is and which pages it comes from. The reader copies the coverage line into
`pages_read`, so a record always says what was not read. Quotes are still checked
against the full text by `check-quotes`, and the rest of the source stays
searchable with `search --source <id>`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .index import _bm25, _tokens, passages
from rag import paths

# Measured on 2026-11-24 against the quotes in the existing reading records (made from
# full reads), for the sources longer than the budget: 4,000 words gave 29% of the text
# and kept 60% of the quotes; 6,000 words gave 40% and kept 69%. Adding meaning-based
# (embedding) ranking changed this by one point, so selection stays keyword-only.
BUDGET_WORDS = 6000
FRONT_PASSAGES = 3  # title page, abstract or opening: who wrote it and what it set out to do

# One query per field of the reading record. English with the commonest German and
# French forms, since some sources are in those languages.
FIELD_QUERIES = {
    "definitions": "define defined definition definitions means refers term terms category "
                   "categories criteria classify classified classification glossary "
                   "definiert bezeichnet définition désigne",
    "proxies": "indicator indicators proxy measure measured identified identify threshold "
               "revenue share list listed membership member code codes criterion "
               "affiliation affiliated",
    "method": "method methods methodology approach data dataset database sample coded coding "
              "collected source sources compiled analysis analysed analyzed manual matched "
              "methode méthode daten données",
    "findings": "find found finding findings result results show shows showed evidence "
                "percent per cent share increase rose number largest most",
    "limitations": "limitation limitations caveat caveats bias biased however cannot unable "
                   "incomplete underestimate overestimate uncertain uncertainty not possible "
                   "missing excluded",
    "lists_and_datasets": "dataset database list register registry published available "
                          "compiled maintained open access download",
}
HEADING_CUES = {
    "definitions": r"defin|glossar|terminolog|begriff",
    "method": r"method|data|approach|sample|annex|appendix|anhang|méthod",
    "limitations": r"limitation|caveat|discussion|einschränk",
    "findings": r"result|finding|conclusion|summary|ergebnis|fazit",
}


def _words(text: str) -> int:
    return len(text.split())


def _page_of(loc: str) -> int | None:
    m = re.match(r"p\.(\d+)$", loc)
    return int(m.group(1)) if m else None


def _ranges(nums: list[int]) -> str:
    """[1, 2, 3, 7, 9, 10] -> '1-3, 7, 9-10'"""
    out, start, prev = [], None, None
    for n in sorted(set(nums)):
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append(f"{start}" if start == prev else f"{start}-{prev}")
            start = prev = n
    if start is not None:
        out.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ", ".join(out)


def select(doc: dict, terms: list[str] | None = None, budget: int = BUDGET_WORDS,
           per_field: int | None = None) -> dict:
    """The passages of `doc` a reader needs, with a statement of coverage.

    `terms` are the study's key terms (for example "fossil fuel", "lobbyist"): they are
    added to every field's query, so passages that use them rank higher.
    """
    rows = passages(doc)
    total_words = sum(_words(r["text"]) for r in rows)
    pages_total = doc.get("page_count") or len(doc.get("pages") or []) or None
    why: dict[int, set[str]] = {}

    if total_words <= budget:
        why = {i: {"whole source"} for i in range(len(rows))}
        mode = "whole"
    else:
        mode = "selected"
        extra = " ".join(terms or [])
        toks = [_tokens(r["text"]) for r in rows]
        for i in range(min(FRONT_PASSAGES, len(rows))):
            why.setdefault(i, set()).add("opening")
        ranked: list[tuple[float, int, str]] = []
        for field, query in FIELD_QUERIES.items():
            scores = _bm25(f"{query} {extra}", toks)
            cue = HEADING_CUES.get(field)
            for i, r in enumerate(rows):
                if cue and r.get("section") and re.search(cue, r["section"], flags=re.I):
                    scores[i] += scores.max() * 0.5 + 1  # under a heading for this field
            top = sorted(range(len(rows)), key=lambda i: -scores[i])[:per_field]
            # interleave the fields: each field's best passage before any field's second best
            ranked += [(rank, i, field) for rank, i in enumerate(top) if scores[i] > 0]
        used = sum(_words(rows[i]["text"]) for i in why)
        for _, i, field in sorted(ranked):
            if i in why:
                why[i].add(field)
                continue
            n = _words(rows[i]["text"])
            if used + n > budget:
                continue
            why[i] = {field}
            used += n

    chosen = sorted(why)
    given_words = sum(_words(rows[i]["text"]) for i in chosen)
    pages = [p for i in chosen if (p := _page_of(rows[i]["loc"])) is not None]
    if mode == "whole":
        note = f"whole source ({total_words} words)"
    else:
        where = f"pages {_ranges(pages)}" if pages else "sections listed in the passages"
        note = (f"selected by code: {len(chosen)} of {len(rows)} passages, {given_words} of "
                f"{total_words} words, from {where}"
                + (f" of {pages_total}" if pages and pages_total else "")
                + "; chosen for definitions, indicators, method, findings and limitations;"
                " the rest was not read")
    return {
        "id": doc["id"],
        "title": doc.get("title"),
        "kind": doc["kind"],
        "url": doc.get("url"),
        "coverage": {"mode": mode, "passages_given": len(chosen), "passages_total": len(rows),
                     "words_given": given_words, "words_total": total_words,
                     "pages_given": sorted(set(pages)), "pages_total": pages_total,
                     "note": note},
        "passages": [{"chunk": rows[i]["chunk"], "loc": rows[i]["loc"],
                      "section": rows[i].get("section"), "why": sorted(why[i]),
                      "text": rows[i]["text"]} for i in chosen],
    }


def write(ids: list[str], root: Path | str = "literature", terms: list[str] | None = None,
          budget: int = BUDGET_WORDS) -> list[dict]:
    """Write `data/processed/reader-picks/<id>.json` for each source and return their coverage."""
    root = Path(root)
    out = root / paths.READER_PICKS
    out.mkdir(parents=True, exist_ok=True)
    report = []
    for sid in ids:
        path = root / paths.TEXT / f"{sid}.json"
        if not path.exists():
            raise SystemExit(f"No extracted text for {sid}: run extract or fetch first.")
        sel = select(json.loads(path.read_text()), terms=terms, budget=budget)
        (out / f"{sid}.json").write_text(json.dumps(sel, indent=1, ensure_ascii=False))
        report.append({"id": sid, **sel["coverage"]})
    return report
