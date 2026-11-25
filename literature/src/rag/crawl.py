"""Download pages, extract them, and list what they link to.

The crawler does not wander. By default it downloads only the pages it is
given. Every link found in the body of a page is written to the ledger as a
candidate, with the sentence it appeared in, so that screening decides what is
downloaded next. With depth 1 it also follows links of the kinds named in
`follow` (by default pages on the same site), one step and no further.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from rag import paths
from rag.extract import extract_file
from rag.fetch import Fetcher, has_secret, normalise_url, redact_url
from rag.ledger import Ledger


def write_text(doc: dict, root: Path) -> Path:
    out = root / paths.TEXT / f"{doc['id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    return out


def register_links(doc: dict, ledger: Ledger) -> list[dict]:
    """Add each outgoing link of a document to the ledger as a candidate."""
    # Extracting a document again must replace what it said before, not add to it:
    # otherwise citation counts double. Entries added by hand (such as "note 12") stay.
    mine = (f"{doc['id']} (para ", f"{doc['id']} (p.")
    for r in ledger.rows:
        r["found_via"] = [v for v in r["found_via"] if not v.startswith(mine)]
    rows = []
    for link in doc.get("links", []):
        where = f"p.{link['page']}" if "page" in link else f"para {link.get('paragraph')}"
        via = f"{doc['id']} ({where})"
        row = ledger.add(
            link["url"], found_via=via,
            link_kind=link["kind"], anchor=link["anchor"] or None, context=link["context"] or None,
        )
        if row["found_via"][0] == via:  # the first mention supplies the anchor and sentence
            row["anchor"], row["context"] = link["anchor"] or None, link["context"] or None
        rows.append(row)
    return rows


def process(id: str, path: str, url: str | None, root: Path, ledger: Ledger, **entry) -> dict:
    """Extract one raw file, save its text, and record it and its links."""
    doc = extract_file(path, url, id)
    out = write_text(doc, root)
    year = (doc.get("published") or "")[:4]
    fields = {
        "title": doc.get("title"), "authors": doc.get("authors") or None,
        "year": int(year) if year.isdigit() else None,
    }
    fields.update({k: v for k, v in entry.items() if v is not None})  # what the researcher gave wins
    ledger.add(doc.get("canonical_url") or url, id=id, file=str(path), text=str(out), **fields)
    register_links(doc, ledger)
    return doc


def crawl(
    starts: list[tuple[str, str | None]],
    root: Path | str = "literature",
    depth: int = 0,
    follow: tuple[str, ...] = ("internal",),
    max_pages: int = 25,
    log=print,
) -> list[dict]:
    """starts: (url, id or None). Returns one summary per page attempted."""
    root = Path(root)
    ledger, fetcher = Ledger(root), Fetcher(root)
    queue = deque((url, id, 0, "seed") for url, id in starts)
    done: set[str] = set()
    results = []
    try:
        while queue and len(results) < max_pages:
            url, id, level, via = queue.popleft()
            key = normalise_url(redact_url(url))
            if key in done:
                continue
            done.add(key)
            row = ledger.add(url, id=id, found_via=via if level else None)
            got = fetcher.fetch(url, row["id"])
            summary = {"id": row["id"], "url": got.url, "depth": level, "ok": got.ok, "note": got.note}
            if not got.ok:
                ledger.add(url, id=row["id"], reason=f"download failed: {got.note}")
                log(f"  FAILED {row['id']}: {got.note}")
                results.append(summary)
                continue
            entry = {"status": "in", "reason": "supplied by the researcher"} if level == 0 else {}
            if has_secret(url):
                entry["reason"] = "supplied by the researcher as an unpublished preview link"
            doc = process(row["id"], got.path, url, root, ledger, **entry)
            summary.update(title=doc.get("title"), counts=doc["counts"], file=got.path)
            results.append(summary)
            log(f"  {row['id']}: {doc['counts']}")
            if level < depth:
                for link in doc["links"]:
                    if link["kind"] in follow:
                        queue.append((link["url"], None, level + 1, row["id"]))
            ledger.save()
    finally:
        ledger.save()
        fetcher.close()
    return results
