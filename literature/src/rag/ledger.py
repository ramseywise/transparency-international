"""The literature ledger: one line per source considered, and its status.

status: candidate (found, not yet screened) | in | out | read
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

from rag import paths
from rag.fetch import match_key, redact_url, tidy_url

FIELDS = [
    "id", "title", "authors", "year", "type", "peer_reviewed", "doi_or_url",
    "found_via", "status", "reason", "file", "text", "link_kind", "anchor", "context",
    "source_type", "tier", "tier_reason", "question", "found_by_search", "cited_by_count",
    # written by `rag openaccess`: legal open copies known to OpenAlex, and code or data
    # links printed in the source's own text
    "open_access", "code_links",
]


def slug_id(url: str) -> str:
    """A readable id for a link whose author and year are not yet known."""
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    if host in ("doi.org", "dx.doi.org"):
        base = "doi-" + parts.path.strip("/")
    else:
        site = host.split(".")[-2] if host.count(".") else host
        if host.endswith((".co.uk", ".org.uk", ".com.br", ".gov.uk", ".com.au")):
            site = host.split(".")[-3]
        tail = [s for s in parts.path.split("/") if re.search(r"[A-Za-z0-9]", s)]
        last = re.sub(r"\.(html?|pdf|php|aspx?)$", "", tail[-1]) if tail else "home"
        base = f"{site}-{last}"
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:70].strip("-")
    if parts.query:
        base += "-" + hashlib.sha1(parts.query.encode()).hexdigest()[:6]
    return base


class Ledger:
    def __init__(self, root: Path | str = "literature"):
        if Path(root) == paths.BASE:
            # literature/ holds the tools and one library per study; it is not itself a library
            raise ValueError(f"name the library folder, for example {paths.BASE}/<study>, not {paths.BASE}/")
        self.path = Path(root) / paths.LEDGER
        self.rows: list[dict] = []
        if self.path.exists():
            self.rows = [json.loads(l) for l in self.path.read_text().splitlines() if l.strip()]
            for r in self.rows:  # rows written before a field was added
                for k in FIELDS:
                    r.setdefault(k, None)
        self._by_id = {r["id"]: r for r in self.rows}
        self._by_url = {}
        for r in self.rows:  # the first row for an address keeps it
            if r.get("doi_or_url"):
                self._by_url.setdefault(match_key(r["doi_or_url"]), r)

    def get(self, id: str) -> dict | None:
        return self._by_id.get(id)

    def by_url(self, url: str) -> dict | None:
        return self._by_url.get(match_key(url))

    def add(self, url: str | None, id: str | None = None, **fields) -> dict:
        """Add a source, or return the existing entry for the same URL or id."""
        url = tidy_url(redact_url(url)) if url else None
        row = (self.by_url(url) if url else None) or (self._by_id.get(id) if id else None)
        if row is None:
            new_id = id or slug_id(url)
            n, base = 2, new_id
            while new_id in self._by_id:
                new_id, n = f"{base}-{n}", n + 1
            row = {k: None for k in FIELDS}
            row.update(id=new_id, doi_or_url=url, found_via=[], status="candidate")
            self.rows.append(row)
            self._by_id[new_id] = row
            if url:
                self._by_url.setdefault(match_key(url), row)
        via = fields.pop("found_via", None)
        if via and via not in row["found_via"]:
            row["found_via"].append(via)
        query = fields.pop("found_by_search", None)
        if query:
            row["found_by_search"] = row.get("found_by_search") or []
            if query not in row["found_by_search"]:
                row["found_by_search"].append(query)
        for k, v in fields.items():
            if v is not None and (row.get(k) is None
                                  or k in ("status", "reason", "file", "text", "question", "cited_by_count")):
                row[k] = v
        return row

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in self.rows))
        os.replace(tmp, self.path)
