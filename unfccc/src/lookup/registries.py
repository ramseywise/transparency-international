"""Look an organisation up in open registers before searching the web.

Two free, public sources are asked by name only (never a person, never the delegate
list): Wikidata, which records for many organisations what they are, their industry,
parent and owner; and GLEIF, the global register of legal entities (LEI codes), which
records legal names, legal form, country and status. Each hit becomes a "page" with an
address and a flat text, so it is quoted and checked like any other page. Whether it
counts as a register, and at which level of evidence, is for the codebook to say.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import httpx

from .pages import USER_AGENT, today

WIKIDATA = "https://www.wikidata.org/w/api.php"
GLEIF = "https://api.gleif.org/api/v1"
PROPS = {"P31": "instance of", "P452": "industry", "P17": "country",
         "P749": "parent organization", "P127": "owned by", "P856": "official website"}
MAX_HITS = 3


def client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=20.0)


def _cached(cache: Path | None, key: str, make):
    if cache is None:
        return make()
    path = cache / f"{hashlib.sha256(key.encode()).hexdigest()[:24]}.json"
    if path.exists():
        return json.loads(path.read_text())
    value = make()
    cache.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False))
    return value


def _claim_values(entity: dict, prop: str) -> list:
    out = []
    for c in entity.get("claims", {}).get(prop, []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(v, dict) and "id" in v:
            out.append(v["id"])
        elif isinstance(v, str):
            out.append(v)
    return out


def wikidata(name: str, http: httpx.Client, language: str = "en") -> list[dict]:
    r = http.get(WIKIDATA, params={"action": "wbsearchentities", "search": name,
                                   "language": language, "uselang": "en", "type": "item",
                                   "limit": MAX_HITS, "format": "json"})
    r.raise_for_status()
    ids = [h["id"] for h in r.json().get("search", [])]
    if not ids:
        return []
    r = http.get(WIKIDATA, params={"action": "wbgetentities", "ids": "|".join(ids),
                                   "props": "labels|descriptions|claims", "languages": "en",
                                   "format": "json"})
    r.raise_for_status()
    ents = r.json().get("entities", {})
    linked = sorted({v for e in ents.values() for p in PROPS if p != "P856"
                     for v in _claim_values(e, p)})
    names: dict[str, str] = {}
    for i in range(0, len(linked), 50):
        r = http.get(WIKIDATA, params={"action": "wbgetentities", "ids": "|".join(linked[i:i + 50]),
                                       "props": "labels", "languages": "en", "format": "json"})
        r.raise_for_status()
        for k, e in r.json().get("entities", {}).items():
            names[k] = e.get("labels", {}).get("en", {}).get("value", k)
    pages = []
    for qid in ids:
        e = ents.get(qid, {})
        label = e.get("labels", {}).get("en", {}).get("value", qid)
        desc = e.get("descriptions", {}).get("en", {}).get("value")
        lines = [f"Wikidata item {qid}: {label}" + (f" - {desc}" if desc else "")]
        for p, what in PROPS.items():
            vals = [names.get(v, v) for v in _claim_values(e, p)]
            if vals:
                lines.append(f"{what}: {'; '.join(vals)}")
        pages.append({"url": f"https://www.wikidata.org/wiki/{qid}", "final_url":
                      f"https://www.wikidata.org/wiki/{qid}", "kind": "registry:wikidata",
                      "title": label, "text": "\n".join(lines), "fetched": today(), "ok": True,
                      "error": None,
                      "websites": _claim_values(e, "P856")})
    return pages


def gleif(name: str, http: httpx.Client) -> list[dict]:
    r = http.get(f"{GLEIF}/fuzzycompletions", params={"field": "entity.legalName", "q": name})
    r.raise_for_status()
    leis = []
    for d in r.json().get("data", []):
        rel = d.get("relationships", {}).get("lei-records", {}).get("data", {})
        if rel.get("id") and rel["id"] not in leis:
            leis.append(rel["id"])
    pages = []
    for lei in leis[:MAX_HITS]:
        r = http.get(f"{GLEIF}/lei-records/{lei}")
        r.raise_for_status()
        a = r.json().get("data", {}).get("attributes", {})
        ent = a.get("entity", {})
        addr = ent.get("legalAddress", {})
        lines = [f"LEI record {lei}: {ent.get('legalName', {}).get('name')}",
                 f"legal form: {(ent.get('legalForm') or {}).get('id')}",
                 f"category: {ent.get('category')}",
                 f"jurisdiction: {ent.get('jurisdiction')}",
                 f"legal address: {addr.get('city')}, {addr.get('country')}",
                 f"entity status: {ent.get('status')}"]
        others = [o.get("name") for o in ent.get("otherNames", []) if o.get("name")]
        if others:
            lines.append("other names: " + "; ".join(others))
        url = f"{GLEIF}/lei-records/{lei}"
        pages.append({"url": url, "final_url": url, "kind": "registry:gleif",
                      "title": ent.get("legalName", {}).get("name"), "text": "\n".join(lines),
                      "fetched": today(), "ok": True, "error": None, "websites": []})
    return pages


def lookup(name: str, http: httpx.Client, cache: Path | None = None) -> tuple[list[dict], list]:
    """Register pages for `name`, and the problems met (a register that could not be reached
    is noted, not fatal: the web search still runs)."""
    pages, problems = [], []
    for source, fn in (("wikidata", wikidata), ("gleif", gleif)):
        try:
            pages += _cached(cache, f"{source}:{name}", lambda fn=fn: fn(name, http))
        except (httpx.HTTPError, ValueError) as e:
            problems.append(f"{source} could not be reached ({type(e).__name__})")
    return pages, problems
