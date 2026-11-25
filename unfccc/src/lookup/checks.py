"""The checks done by code, on every evidence record and every classified record.

These are the parts of the agents' rules that can be decided without judgement. A
record that fails one is either repaired by code (a bad evidence item is dropped) or
sent back to the model once with the problems listed; it is never passed on unchecked.
"""

from __future__ import annotations

import datetime as dt
import re

from .codebook import Codebook
from .pages import normalise, quote_on_page

STATUSES = ("confident", "uncertain", "abstained", "confirmed negative", "failed")
SOURCE_TYPES = ("registry", "published list", "independent", "self-description")
INJECTION = re.compile(
    r"(ignore (all |any )?(previous|prior|above) instructions|disregard (the|your) "
    r"(instructions|rules)|you are (now )?(an?|the) (ai|assistant|language model)|"
    r"system prompt|classify (this|us|it) as|do not (report|flag) this)", re.I)


def iso_date(s) -> bool:
    try:
        dt.date.fromisoformat(str(s))
        return True
    except ValueError:
        return False


def injection_phrases(text: str) -> list[str]:
    """Phrases in a page that read as instructions to an AI, for `instructions_found_in_pages`."""
    return sorted({m.group(0) for m in INJECTION.finditer(text)})


def check_item(item: dict, pages: dict[str, dict]) -> list[str]:
    """Problems with one evidence item, against the pages that were actually fetched."""
    problems = []
    url = item.get("source_url")
    page = pages.get(url)
    if page is None or not page.get("ok"):
        problems.append(f"{url}: not a page that was opened in this look-up")
    elif not quote_on_page(item.get("quote") or "", page["text"]):
        problems.append(f"{url}: the quote is not on the page as fetched")
    level = item.get("level")
    if not isinstance(level, int) or isinstance(level, bool) or level < 1:
        problems.append(f"{url}: the level must be a whole number, 1 or more")
    if item.get("source_type") not in SOURCE_TYPES:
        problems.append(f"{url}: source_type must be one of {', '.join(SOURCE_TYPES)}")
    if not iso_date(item.get("date")):
        problems.append(f"{url}: the date must be YYYY-MM-DD")
    if not (item.get("page") or "").strip():
        problems.append(f"{url}: no page number or section heading")
    return problems


def check_evidence(rec: dict, pages: dict[str, dict]) -> list[str]:
    """Problems with a whole evidence record."""
    problems = []
    status = rec.get("status")
    if status not in STATUSES:
        problems.append(f"status {status!r} is not one of {', '.join(STATUSES)}")
    if status != "failed" and not rec.get("searches"):
        problems.append("no searches recorded: a look-up that ran must list what it searched")
    ev = rec.get("evidence") or []
    if status in ("confident", "uncertain", "confirmed negative") and not ev:
        problems.append(f"status {status!r} needs at least one item of evidence")
    if status == "abstained" and not (rec.get("status_reason") or "").strip():
        problems.append("an abstained record must give its reason")
    if status == "failed" and not (rec.get("status_reason") or "").strip():
        problems.append("a failed record must say what failed")
    for item in ev:
        problems += check_item(item, pages)
    return problems


def repair_evidence(rec: dict, pages: dict[str, dict]) -> tuple[dict, list[str]]:
    """Drop the items that fail their check. If none is left where some were needed, the
    record becomes `failed`: the look-up did not produce evidence that can be checked."""
    kept, dropped = [], []
    for item in rec.get("evidence") or []:
        p = check_item(item, pages)
        (dropped if p else kept).append((item, p))
    notes = [q for _, ps in dropped for q in ps]
    rec = dict(rec, evidence=[i for i, _ in kept])
    if dropped and not kept and rec.get("status") in ("confident", "uncertain",
                                                     "confirmed negative"):
        rec["status"] = "failed"
        rec["status_reason"] = "quotes could not be verified on the fetched pages"
    if dropped:
        rec["dropped_items"] = len(dropped)
    return rec, notes


def expected_confidence(cb: Codebook, item: dict | None, evidence_status: str):
    if item is None:
        return None
    return cb.confidence(item.get("level"), evidence_status)


def check_classified(rec: dict, evidence: dict, cb: Codebook) -> list[str]:
    """Problems with a classified record, against its evidence record and the codebook."""
    problems = []
    for f, allowed in cb.labels["fields"].items():
        if f in rec and rec[f] not in allowed:
            problems.append(f"{f} {rec[f]!r} is not in the codebook's list")
    label = rec.get(cb.label_field)
    ev_status = evidence.get("status")
    if label == "unknown":
        if rec.get("unknown_reason") not in cb.unknown_reasons:
            reason = rec.get("unknown_reason")
            problems.append(f"unknown needs a reason from the codebook: {reason!r}")
        return problems
    if rec.get("rule") not in cb.labels["rules"]:
        problems.append(f"rule {rec.get('rule')!r} is not a rule in the codebook")
    if ev_status in ("failed", "abstained"):
        problems.append(f"the evidence is {ev_status}, so the label must be unknown")
    negative = set(cb.labels["negative_labels"])
    says_no_link = any(rec.get(f) in negative for f in cb.labels["fields"])
    if says_no_link and ev_status != "confirmed negative":
        problems.append("a 'no link' label needs evidence with status 'confirmed negative'")
    items = evidence.get("evidence") or []
    match = [i for i in items if i.get("source_url") == rec.get("source_url")
             and normalise(i.get("quote") or "") == normalise(rec.get("quote") or "")]
    if not match:
        problems.append("source_url and quote are not copied from one stored evidence item")
    else:
        want = expected_confidence(cb, match[0], ev_status)
        if want is None:
            problems.append(f"the codebook gives no confidence for level {match[0].get('level')} "
                            f"with evidence status {ev_status!r}")
        elif rec.get("confidence") != want:
            problems.append(f"confidence should be {want!r} by the codebook's rule")
        elif rec.get("status") != expected_status(cb, rec, want):
            problems.append(f"status should be {expected_status(cb, rec, want)!r}")
    return problems


def expected_status(cb: Codebook, rec: dict, confidence: str):
    """A 'no link' label keeps the status 'confirmed negative'; otherwise the codebook maps
    confidence to status."""
    negative = set(cb.labels["negative_labels"])
    if any(rec.get(f) in negative for f in cb.labels["fields"]):
        return "confirmed negative"
    return cb.status_for(confidence)
