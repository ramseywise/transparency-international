"""Write the screening of candidate sources as one JSON file.

The ledger holds every link ever seen. This export keeps the sources that were
considered for reading (anything ranked into a tier, screened, or held) and puts
beside each one the signals used to rank it and the decision taken, so a person
can review or re-tier the list without reading code.
"""

from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from pathlib import Path

from rag import paths
from rag import rank
from rag.ledger import Ledger

CRITERIA = {
    "screened_in_if": [
        "it defines or counts business or fossil fuel presence at UNFCCC meetings (Q1, Q2)",
        "it describes a method for classifying organisations or delegates, or for checking such a classification",
        "it gives rules or context the study relies on: badges, registration, conflicts of interest, lobbying standards",
    ],
    "screened_out_if": [
        "navigation, social media, donation or contact links",
        "a duplicate of a source already held",
        "off topic for the study's questions",
    ],
    "note": "Tiers order the reading; they do not decide inclusion. Citation counts measure attention, not fit. "
            "citations_worldwide comes from OpenAlex and is empty where the source has no DOI there.",
}


def _outcome(row: dict, root: Path) -> str:
    reason = row.get("reason") or ""
    if (root / paths.RECORDS / f"{row['id']}.json").exists():
        return "read"
    if row.get("file"):
        return "held"
    if "duplicate" in reason:
        return "duplicate"
    if "download failed" in reason:
        return "download failed"
    if "no web address" in reason:
        return "no web address"
    return "not downloaded"


def _words(row: dict, root: Path) -> int | None:
    path = root / paths.TEXT / f"{row['id']}.json"
    if not path.exists():
        return None
    return (json.loads(path.read_text()).get("counts") or {}).get("words")


def build(root: Path | str = "literature") -> dict:
    root = Path(root)
    ledger = Ledger(root)
    rank.rank(ledger.rows)  # fills tier and tier_reason on cited rows; not saved here
    # Every row with a decision is listed, so a screened-out link stays visible even
    # when no held source mentions it any more. An undecided, unmentioned link is not.
    rows = [r for r in ledger.rows
            if r["status"] != "candidate" or r.get("file") or r.get("tier")]
    sources = []
    for r in rows:
        outcome = _outcome(r, root)
        words = _words(r, root)
        sources.append({
            "id": r["id"],
            "title": r.get("title") or r.get("anchor"),
            "authors": r.get("authors"),
            "year": r.get("year"),
            "address": r.get("doi_or_url"),
            "tier": r.get("tier"),
            "tier_name": rank.TIER_NAMES.get(r.get("tier")),
            "tier_reason": r.get("tier_reason"),
            "signals": {
                "mentions_in_our_sources": len(r.get("found_via") or []),
                "cited_by": rank.citing_sources(r),
                "found_by_search": r.get("found_by_search") or [],
                "source_type": r.get("source_type") or (rank.source_type(r["doi_or_url"]) if r.get("doi_or_url") else None),
                "peer_reviewed": r.get("peer_reviewed"),
                "citations_worldwide": r.get("cited_by_count"),
            },
            "decision": r["status"],
            "reason": r.get("reason"),
            "question": r.get("question"),
            "outcome": outcome,
            "words_held": words,
            "thin": bool(outcome in ("held", "read") and words is not None and words < 400),
        })
    sources.sort(key=lambda s: (s["tier"] or 9, -s["signals"]["mentions_in_our_sources"],
                                -(s["signals"]["citations_worldwide"] or 0), s["id"]))
    return {
        "generated": dt.date.today().isoformat(),
        "ledger_rows": len(ledger.rows),
        "criteria": CRITERIA,
        "tiers": {str(k): v for k, v in rank.TIER_NAMES.items()},
        "counts": {
            "considered": len(sources),
            "by_decision": dict(Counter(s["decision"] for s in sources)),
            "by_tier": dict(sorted(Counter(str(s["tier"]) for s in sources).items())),
            "by_outcome": dict(Counter(s["outcome"] for s in sources)),
            "thin": sum(s["thin"] for s in sources),
        },
        "sources": sources,
    }


def write(root: Path | str = "literature") -> dict:
    data = build(root)
    path = Path(root) / paths.SCREENING
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    return data["counts"]
