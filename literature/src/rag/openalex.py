"""Search OpenAlex, an open catalogue of scholarly work, for related research.

Used for two things: finding work our sources do not cite, and reading how
often a source is cited worldwide. A hit is only a candidate; it is screened
like any other link before anything is downloaded.

Nothing about the researcher or the study is sent: only the search words or
the DOIs, under the same generic client name as the crawler. No key is used,
so the daily allowance is small and shared (about 100 searches).
"""

from __future__ import annotations

import re

import httpx

from rag.fetch import USER_AGENT

API = "https://api.openalex.org/works"
SELECT = "id,doi,title,publication_year,cited_by_count,type,authorships,primary_location"
_DOI = re.compile(r"(?:doi\.org/|^doi:)?(10\.\d{4,9}/\S+)$", re.I)


def client(transport=None) -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=40, transport=transport)


def doi_of(url: str | None) -> str | None:
    """The bare DOI in lower case, or None if the address is not a DOI."""
    m = _DOI.search((url or "").strip())
    return m.group(1).lower() if m else None


def _work(w: dict) -> dict | None:
    source = ((w.get("primary_location") or {}).get("source") or {})
    url = w.get("doi") or (w.get("primary_location") or {}).get("landing_page_url")
    if not url or not w.get("title"):
        return None
    return {
        "url": url,
        "title": w["title"],
        "authors": [a["author"]["display_name"] for a in w.get("authorships") or [] if a.get("author")][:12],
        "year": w.get("publication_year"),
        # OpenAlex does not say whether a work was peer reviewed, so that field is left empty
        "type": w.get("type"),
        "context": source.get("display_name"),
        "cited_by_count": w.get("cited_by_count"),
    }


def search(query: str, since: int = 2015, n: int = 25, c: httpx.Client | None = None) -> tuple[int, list[dict]]:
    """(number of matches, the n best matches) for works published since a year."""
    own = c is None
    c = c or client()
    try:
        r = c.get(API, params={"search": query, "filter": f"from_publication_date:{since}-01-01",
                               "per-page": min(n, 200), "select": SELECT})
        r.raise_for_status()
        data = r.json()
    finally:
        if own:
            c.close()
    works = [w for w in map(_work, data.get("results") or []) if w]
    return (data.get("meta") or {}).get("count", len(works)), works


def citation_counts(dois: list[str], c: httpx.Client | None = None) -> dict[str, int]:
    """{doi: times cited worldwide} for the DOIs that OpenAlex knows."""
    own = c is None
    c = c or client()
    out: dict[str, int] = {}
    try:
        for i in range(0, len(dois), 40):
            batch = dois[i:i + 40]
            r = c.get(API, params={"filter": "doi:" + "|".join(batch), "per-page": 200,
                                   "select": "doi,cited_by_count"})
            r.raise_for_status()
            for w in r.json().get("results") or []:
                doi = doi_of(w.get("doi"))
                if doi:
                    out[doi] = w.get("cited_by_count")
    finally:
        if own:
            c.close()
    return out


OA_SELECT = "doi,title,open_access,best_oa_location,locations"


def _copy(loc: dict | None) -> dict | None:
    """One legal open copy: where it is, which version, under which licence."""
    if not loc or not (loc.get("pdf_url") or loc.get("landing_page_url")):
        return None
    return {
        "pdf": loc.get("pdf_url"),
        "landing": loc.get("landing_page_url"),
        # publishedVersion, acceptedVersion (author's final manuscript) or submittedVersion (preprint)
        "version": loc.get("version"),
        "license": loc.get("license"),
        "host": ((loc.get("source") or {}).get("display_name")),
    }


def _open_access(w: dict) -> dict:
    oa = w.get("open_access") or {}
    copies = [c for c in map(_copy, [w.get("best_oa_location")] + [
        l for l in w.get("locations") or [] if l.get("is_oa")]) if c]
    by_key: dict[str, dict] = {}  # one entry per copy; the same page with a PDF link wins
    for c in copies:
        key = c["landing"] or c["pdf"]
        if key not in by_key or (c["pdf"] and not by_key[key]["pdf"]):
            by_key[key] = c
    unique = list(by_key.values())
    # a copy with a direct PDF first, the published version before a manuscript
    rank = {"publishedVersion": 0, "acceptedVersion": 1, "submittedVersion": 2}
    unique.sort(key=lambda c: (c["pdf"] is None, rank.get(c["version"], 3)))
    return {"is_oa": bool(oa.get("is_oa")), "oa_status": oa.get("oa_status"), "copies": unique}


def open_access(dois: list[str], c: httpx.Client | None = None) -> dict[str, dict]:
    """{doi: {is_oa, oa_status, copies}} for the DOIs OpenAlex knows. A DOI that is
    missing from the result is unknown to OpenAlex, which is not the same as closed."""
    own = c is None
    c = c or client()
    out: dict[str, dict] = {}
    try:
        for i in range(0, len(dois), 40):
            r = c.get(API, params={"filter": "doi:" + "|".join(dois[i:i + 40]), "per-page": 200,
                                   "select": OA_SELECT})
            r.raise_for_status()
            for w in r.json().get("results") or []:
                doi = doi_of(w.get("doi"))
                if doi:
                    out[doi] = _open_access(w)
    finally:
        if own:
            c.close()
    return out


def norm_title(t: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def open_access_by_title(title: str, c: httpx.Client | None = None) -> dict | None:
    """The open-access record of the one work whose title matches exactly (ignoring
    case and punctuation), or None. A near match is never taken: a wrong paper is
    worse than none."""
    want = norm_title(title)
    if len(want.split()) < 4:  # too short to identify one work
        return None
    own = c is None
    c = c or client()
    try:
        r = c.get(API, params={"filter": "title.search:" + want, "per-page": 10,
                               "select": OA_SELECT})
        r.raise_for_status()
        hits = [w for w in r.json().get("results") or [] if norm_title(w.get("title")) == want]
    finally:
        if own:
            c.close()
    if len({doi_of(w.get("doi")) or w.get("title") for w in hits}) != 1:
        return None  # none, or several different works with the same title
    return _open_access(hits[0]) | {"doi": doi_of(hits[0].get("doi"))}
