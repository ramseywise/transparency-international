"""Check by code the records that the helper agents returned. No language model, no key.

When classification runs in a conversation (the `evidence-finder` and `org-classifier`
agents), nothing has yet checked their records the way the script checks its own. This
does: it opens each cited address again, looks for the quote on the page, and checks each
label, rule and reason against the codebook's list. It changes no record. It writes what
it found to `verify.json` beside the records, for a person to read.

    uv run python -I -m lookup.verify --evidence <folder> [--classified <folder>]
                                      [--codebook unfccc/docs/codebook.md]

A record is one JSON file per organisation, the same file name in both folders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

from . import checks, codebook, pages, registries
from .pages import normalise

# Labels that state no fact about the organisation, so need no source of their own.
NO_SOURCE_NEEDED = {"unknown", "not_applicable", "none"}
# Fields set by rule from the evidence as a whole, not from one quote.
SET_BY_RULE = ("_confidence", "unknown_class")


def _empty(v) -> bool:
    return v is None or str(v).strip() in ("", "None", "null")


def evidence_problems(rec: dict, http: httpx.Client, cache: Path | None = None) -> list[str]:
    """Problems with one evidence record, each cited page opened again and the quote looked for."""
    return evidence_outcome(rec, http, cache)[0]


def evidence_outcome(rec: dict, http: httpx.Client,
                     cache: Path | None = None) -> tuple[list[str], list[str]]:
    """(failed, could_not_check) for one evidence record. A page that cannot be opened again
    now (blocked, timed out, a PDF that will not read) is not a failure of the record: its
    quote is listed as "could not check", for a person or citation-checker to open."""
    urls = {i.get("source_url") for i in rec.get("evidence") or [] if i.get("source_url")}
    fetched = {u: pages.fetch(u, http, cache) for u in sorted(urls)}
    unread = {u: p.get("error") or "no text" for u, p in fetched.items() if not p.get("ok")}
    walled = {u: why for u, p in fetched.items() if p.get("ok") and (why := pages.needs_browser(p))}
    failed, could_not = [], []
    for p in checks.check_evidence(rec, fetched):
        url = p.split(": ", 1)[0]
        if url in unread and p.endswith("not a page that was opened in this look-up"):
            could_not.append(f"{url}: the page could not be opened again ({unread[url]})")
        elif url in walled and p.endswith("not on the page as fetched"):
            could_not.append(f"{url}: the quote could not be checked ({walled[url]})")
        else:
            failed.append(p)
    return failed, could_not


# Inferred values sit beside the strict label, never over it (rule 5). Each basis has a ceiling.
INFERENCE_BASES = {"limited_evidence": "medium", "proxy": "low"}
CONFIDENCE_ORDER = ["low", "medium", "high"]
# A negative on the strict line needs a level A or B source (script levels 1 and 2).
NEGATIVE_MAX_LEVEL = 2


def _inferred_problems(name: str, inf, strict: str, allowed: list, cb, items: dict) -> list[str]:
    if not isinstance(inf, dict):
        return [f"{name}: inferred is not a record"]
    out = []
    if strict != "unknown":
        out.append(f"{name}: an inferred value is given although the strict label is {strict!r}")
    basis = inf.get("basis")
    if basis not in INFERENCE_BASES:
        return out + [f"{name}: inferred basis {basis!r} is not limited_evidence or proxy"]
    if inf.get("label") not in allowed or inf.get("label") == "unknown":
        out.append(f"{name}: inferred label {inf.get('label')!r} is not allowed")
    if inf.get("rule") not in cb.labels["rules"]:
        out.append(f"{name}: inferred rule {inf.get('rule')!r} is not in the codebook's list")
    conf = inf.get("confidence")
    if conf not in CONFIDENCE_ORDER or CONFIDENCE_ORDER.index(conf) > CONFIDENCE_ORDER.index(INFERENCE_BASES[basis]):
        out.append(f"{name}: inferred confidence {conf!r} is above the {basis} ceiling "
                   f"({INFERENCE_BASES[basis]})")
    if not _empty(inf.get("from_attribute")) and basis == "proxy":
        return out  # a proxy from another attribute of the same record (e.g. kind) needs no quote
    if _empty(inf.get("source_url")) or _empty(inf.get("quote")):
        out.append(f"{name}: inferred value has no source and quote")
    elif (inf["source_url"], normalise(inf["quote"])) not in items:
        out.append(f"{name}: inferred source and quote are not in the evidence record")
    return out


# Each hard-case rule names one case (codebook section 4). A hard_case label given under a B
# rule must be that rule's case, so a slipped code (B1 on a public body) is caught.
HARD_CASE_RULES = {
    "B1": "company", "B2": "trade_association", "B3": "mixed_association",
    "B4": "private_law_chamber", "B5": "public_law_chamber", "B6": "cooperative",
    "B7": "public_development_bank", "B8": "development_agency", "B9": "company_foundation",
    "B10": "municipal_utility", "B11": "consultancy_or_law_firm", "B12": "self_employed_consultant",
    "B13": "trade_union", "B14": "parliament", "B15": "media_company", "B16": "university",
    "B17": "think_tank", "B18": "coordination_body", "B19": "public_investment_fund",
}


def _consistency_problems(attrs: dict, cb: codebook.Codebook) -> list[str]:
    """Checks across attributes: the hard case matches its B rule, and unknown_class "none"
    is given only where the headline label is not unknown (and the reverse)."""
    problems = []
    hc = attrs.get("hard_case")
    if isinstance(hc, dict) and str(hc.get("rule") or "").startswith("B"):
        want = HARD_CASE_RULES.get(hc["rule"])
        if want and hc.get("label") != want:
            problems.append(f"hard_case: rule {hc['rule']} is the case {want!r}, "
                            f"not {hc.get('label')!r}")
    head, uc = attrs.get(cb.labels.get("label_field")), attrs.get("unknown_class")
    if isinstance(head, dict) and isinstance(uc, dict):
        if head.get("label") == "unknown" and uc.get("label") == "none":
            problems.append("unknown_class: 'none' although the headline label is unknown")
        if head.get("label") not in ("unknown", None) and uc.get("label") not in ("none", None):
            problems.append(f"unknown_class: {uc.get('label')!r} although the headline label is known")
    return problems


def classified_problems(rec: dict, evidence: dict, cb: codebook.Codebook) -> list[str]:
    """Problems with one classification record that holds several attributes.

    Each attribute: a field and label the codebook allows, a rule it lists, and either a
    reason for "unknown" from its list or a source and quote that are in the evidence record.
    A strict negative must cite a level 1-2 item. An `inferred` block beside an unknown is
    checked for its basis, rule, confidence ceiling and source. A value that is not a record
    is reported, never a crash.
    """
    problems = []
    fields = cb.labels["fields"]
    negatives = set(cb.labels.get("negative_labels") or [])
    items = {(i.get("source_url"), normalise(i.get("quote") or "")): i.get("level")
             for i in evidence.get("evidence") or []}
    if str(rec.get("codebook_version")) != cb.version:
        problems.append(f"made under codebook {rec.get('codebook_version')}, "
                        f"the codebook is now {cb.version}")
    attrs = rec.get("attributes")
    if not isinstance(attrs, dict):
        return problems + ["no attributes record: the output is not in the codebook's format"]
    for name, a in attrs.items():
        if name not in fields:
            problems.append(f"{name}: not a field of the codebook")
            continue
        if not isinstance(a, dict):
            problems.append(f"{name}: value is not a record with a label (got {type(a).__name__})")
            continue
        label = a.get("label")
        if label not in fields[name]:
            problems.append(f"{name}: label {label!r} is not allowed")
            continue
        if name.endswith(SET_BY_RULE[0]) or name == SET_BY_RULE[1]:
            continue
        if not _empty(a.get("rule")) and a["rule"] not in cb.labels["rules"]:
            problems.append(f"{name}: rule {a['rule']!r} is not in the codebook's list")
        if label == "unknown":
            if a.get("unknown_reason") not in cb.unknown_reasons:
                problems.append(f"{name}: unknown without a reason from the codebook's list")
        elif label not in NO_SOURCE_NEEDED:
            if _empty(a.get("source_url")) or _empty(a.get("quote")):
                problems.append(f"{name}: label {label!r} has no source and quote")
            elif (a["source_url"], normalise(a["quote"])) not in items:
                problems.append(f"{name}: its source and quote are not in the evidence record")
            elif label in negatives:
                level = items[(a["source_url"], normalise(a["quote"]))]
                if not isinstance(level, int) or level > NEGATIVE_MAX_LEVEL:
                    problems.append(f"{name}: negative {label!r} cites a level {level} source; "
                                    f"the strict line needs level 1 or 2")
        if a.get("inferred") is not None:
            problems += _inferred_problems(name, a["inferred"], label, fields[name], cb, items)
    return problems + _consistency_problems(attrs, cb)


def verify(evidence_dir: Path, classified_dir: Path | None, cb: codebook.Codebook | None,
           http: httpx.Client, cache: Path | None = None) -> dict:
    """Every record in the folder(s): {case: {"evidence": [...], "classified": [...],
    "could_not_check": [...], "outcome": passed | failed | could not check}}.

    Three outcomes, so that a page that is down is never counted as a record that is wrong:
    failed if any real problem was found; otherwise could not check if some quote's page could
    not be opened again; otherwise passed."""
    out = {}
    for path in sorted(Path(evidence_dir).glob("*.json")):
        ev = json.loads(path.read_text())
        failed, could_not = evidence_outcome(ev, http, cache)
        found = {"evidence": failed}
        if classified_dir is not None and cb is not None:
            cl = Path(classified_dir) / path.name
            found["classified"] = (classified_problems(json.loads(cl.read_text()), ev, cb)
                                   if cl.exists() else ["no classification record"])
        found["could_not_check"] = could_not
        found["outcome"] = outcome(found)
        out[path.stem] = found
    return out


OUTCOMES = ("passed", "failed", "could not check")


def outcome(found: dict) -> str:
    if found.get("evidence") or found.get("classified"):
        return "failed"
    return "could not check" if found.get("could_not_check") else "passed"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lookup.verify")
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--classified", type=Path)
    ap.add_argument("--codebook", type=Path)
    a = ap.parse_args(argv)
    cb = codebook.load(a.codebook, draft=True) if a.codebook else None
    with registries.client() as http:
        result = verify(a.evidence, a.classified if cb else None, cb, http,
                        cache=a.evidence.parent / "pages")
    out = a.evidence.parent / "verify.json"
    out.write_text(json.dumps({"checked": pages.today(), "records": result}, indent=1,
                              ensure_ascii=False))
    n = {k: sum(r["outcome"] == k for r in result.values()) for k in OUTCOMES}
    print(f"{len(result)} records checked: {n['passed']} passed, {n['failed']} failed, "
          f"{n['could not check']} could not check. See {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
