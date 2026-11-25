"""Rank candidate sources into tiers, so screening and reading start with the ones that matter most.

The tier says how central a source is to the literature we already hold. It is
computed from facts in the ledger only: how often our sources cite it, how many
of our sources cite it, and what kind of publisher it comes from. It does not
say whether the source is relevant to the study's questions. That is a
judgement, made at screening and recorded in `status`, `reason` and `question`.

Tier 1  primary     cited by two or more of our sources, or three or more times
Tier 2  core        peer-reviewed or scholarly, an official body, or a dataset or method page
Tier 3  supporting  reports by Transparency International and other organisations
Tier 4  news        press and media coverage
Tier 5  low signal  everything else (home pages, pages of unknown kind)

Citation counts measure attention, not fit: a tier 4 article can still be the
only source for a fact, and a tier 1 source can be out of scope.
"""

from __future__ import annotations

from urllib.parse import urlsplit

TIER_NAMES = {1: "primary", 2: "core", 3: "supporting", 4: "news", 5: "low signal"}
PRIMARY_SOURCES, PRIMARY_MENTIONS = 2, 3

SCHOLARLY = ("doi.org", "global.oup.com", "academic.oup.com", "sites.uef.fi")
OFFICIAL = ("unfccc.int", "un.org", "ipcc.ch", "oecd.org", "unep.org", "cop30.br", "europa.eu",
            "unglobalcompact.org")
DATA = ("lobbymap.org", "influencemap.org", "influencemap.net", "zerotracker.net", "edcdn.com",
        "bankingonclimatechaos.org")
TI = ("transparency.org", "transparencycdn.org", "transparency.eu")
NEWS = ("theguardian.com", "reuters.com", "bloomberg.com", "bbc.com", "bbc.co.uk", "france24.com",
        "climatechangenews.com", "carbonbrief.org", "eenews.net", "grist.org", "theintercept.com",
        "hbr.org", "desmog.com", "politico.eu", "ft.com", "nytimes.com")
REPORT = ("globalwitness.org", "kickbigpollutersout.org", "fossilfreepolitics.org", "newclimate.org",
          "corporateaccountability.org", "caad.info", "forestdeclaration.org", "ecbi.org", "ucs.org",
          "opecfund.org")
TYPE_TIER = {"scholarly": 2, "official": 2, "data": 2, "ti": 3, "report": 3, "news": 4, "other": 5}


def _host(url: str) -> str:
    return urlsplit(url).netloc.lower().removeprefix("www.")


def _on(host: str, sites: tuple[str, ...]) -> bool:
    return any(host == s or host.endswith("." + s) for s in sites)


def source_type(url: str | None) -> str:
    """The kind of publisher, judged from the web address alone."""
    if not url:
        return "other"
    host = _host(url)
    for name, sites in (("scholarly", SCHOLARLY), ("official", OFFICIAL), ("data", DATA),
                        ("ti", TI), ("news", NEWS), ("report", REPORT)):
        if _on(host, sites):
            return name
    return "other"


def citing_sources(row: dict) -> list[str]:
    """The ids of our sources that cite this one, from entries like 'some-id (p.3)'."""
    return sorted({v.split(" (")[0] for v in row.get("found_via") or []})


def tier(row: dict) -> tuple[int, str]:
    """(tier, reason). A source type set by hand on the row wins over the web address."""
    stype = row.get("source_type") or source_type(row.get("doi_or_url"))
    mentions, sources = len(row.get("found_via") or []), len(citing_sources(row))
    path = urlsplit(row.get("doi_or_url") or "").path.strip("/")
    is_home = bool(row.get("doi_or_url")) and path in ("", "index.html") and stype not in ("data",)
    if is_home:
        return 5, "a home page, not a document"
    if sources >= PRIMARY_SOURCES:
        return 1, f"cited by {sources} of our sources ({mentions} times)"
    if mentions >= PRIMARY_MENTIONS:
        return 1, f"cited {mentions} times in one of our sources"
    if not mentions and row.get("found_by_search"):
        return TYPE_TIER[stype], f"{stype}; found by search, not cited by our sources"
    return TYPE_TIER[stype], f"{stype}; cited {mentions} time{'s' if mentions != 1 else ''}"


def rank(rows: list[dict]) -> list[dict]:
    """Write source_type, tier and tier_reason on every row found by citation or by search.

    Returns those rows in reading order: tier, then most cited by our sources,
    then most cited worldwide.
    """
    cited = [r for r in rows if r.get("found_via") or r.get("found_by_search")]
    for r in cited:
        r["source_type"] = r.get("source_type") or source_type(r.get("doi_or_url"))
        r["tier"], r["tier_reason"] = tier(r)
    return sorted(cited, key=lambda r: (r["tier"], -len(citing_sources(r)), -len(r.get("found_via") or []),
                                        -(r.get("cited_by_count") or 0), r["id"]))
