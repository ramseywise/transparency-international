"""Three extra tables for the country comparison (codebook 0.13 draft). PROVISIONAL.

  kind_from_list_alone   what the raw list itself states about the kind of each delegate's
                         organisation, before any search (its "Type of home organization" column)
  cannot_say_reasons     why delegates are "insufficient evidence" on the fossil question, and
                         what could settle each group
  business_activity      business delegates by a provisional activity group

The activity groups are NOT the sector rule, which is not yet defined. They were assigned by
hand from one stored evidence item per organisation (rule 5: kept beside the records, in
data/processed/draft-codebook/comparison/business_activity_as_found_PROVISIONAL.csv).

Run from unfccc/ after analysis.country_test:
  PYTHONPATH=src uv run python -I -m analysis.country_insights
"""
from __future__ import annotations

import csv

from analysis import country_test as C
from analysis import germany_test as G

OUT = C.OUT / "comparison"
ACTIVITY_TABLE = C.BASE / "comparison" / "business_activity_as_found_PROVISIONAL.csv"
TYPE_COLUMN = "Type of home organization"
SHEETS = {"Parties": "party", "Party overflow": "overflow"}

# What could settle a "cannot say" group.
DECISION = "A decision would settle it"
SEARCH = "More searching could settle it"
PERSON = "Only a person lookup or the delegation could settle it"
ROUTES = (DECISION, SEARCH, PERSON)
NOT_GROUPED = "Not grouped"

# Unresolved identity: text in the reason -> (label, route). First match wins.
_UNRESOLVED = (
    ("acronym not confirmed", "Abbreviation not confirmed by a source", DECISION),
    ("generic text", "Entry is generic text", PERSON),
    ("not an organisation", "Entry is not an organisation", PERSON),
    ("no organisation written", "No organisation written", PERSON),
    ("several entities", "Could be several bodies", PERSON),
    ("no evidence found", "No evidence found for the name", PERSON),
)
F4 = "fossil rule not yet defined (F4)"
# The tier 3 run rule (codebook 0.16, analysis.tier3_draft.tier3_run): reason -> (label, route).
_TIER3 = (
    ("for review: on the bank table", "Bank on the table, for the researcher's review", DECISION),
    ("not covered by the bank table", "Financial institution not covered by the bank table", SEARCH),
)


def list_alone(raw_rows: list[dict], country: str) -> list[dict]:
    """Party and overflow delegates of one country by whether the list states a type of
    organisation. No kind is read from the organisation's name: that would be a new rule."""
    counts = {"stated": [0, 0], "not stated": [0, 0]}
    for r in raw_rows:
        if r["Nominated by"] != country or r["sheet"] not in SHEETS:
            continue
        key = "stated" if (r.get(TYPE_COLUMN) or "").strip() else "not stated"
        counts[key][list(SHEETS).index(r["sheet"])] += 1
    return [{"country": country, "value": k, "delegates": p + o, "party": p, "overflow": o}
            for k, (p, o) in counts.items()]


def reason_of(org: dict) -> tuple[str, str]:
    """(reason, route) for one organisation whose fossil headline is "insufficient evidence"."""
    identity = org["identity"]
    if identity == "resolved":
        why = f'{org.get("tier3_reason", "")} {org.get("review_reasons", "")}'
        for text, label, route in _TIER3:
            if text in why:
                return label, route
        if F4 in org.get("review_reasons", ""):
            return "Finance rule (Tier 3) not defined", DECISION
        return "Organisation found, fossil evidence incomplete", SEARCH
    if identity == G.I4_IDENTITY:
        return "Body known from the list's context only", PERSON
    for text, label, route in _UNRESOLVED:
        if text in identity:
            return label, route
    raise ValueError(f"no reason group for identity {identity!r}")


def cannot_say(orgs: list[dict], country: str) -> list[dict]:
    """Delegates with "insufficient evidence", by reason and by what could settle it."""
    tally: dict = {}
    for o in orgs:
        if o["headline"] != "insufficient evidence":
            continue
        t = tally.setdefault(reason_of(o), [0, 0, 0, 0])
        for i, col in enumerate(("delegates", "party", "overflow")):
            t[i + 1] += int(o[col])
        t[0] += 1
    return [{"country": country, "route": route, "reason": reason, "organisations": n,
             "delegates": d, "party": p, "overflow": ov}
            for (reason, route), (n, d, p, ov) in
            sorted(tally.items(), key=lambda x: (ROUTES.index(x[0][1]), -x[1][1], x[0][0]))]


def activity(orgs: list[dict], table: list[dict], country: str) -> list[dict]:
    """Business delegates by provisional activity group, with the fossil headline beside it.
    A business organisation with no row in the table is "Not grouped", never guessed."""
    groups = {t["org_key"]: t["provisional_group"] for t in table if t["country"] == country}
    tally: dict = {}
    for o in orgs:
        if o["kind_group"] != "business_and_commercial":
            continue
        key = (groups.get(o["org_key"], NOT_GROUPED), o["headline"], o["headline_line"])
        t = tally.setdefault(key, [0, 0, 0, 0, []])
        for i, col in enumerate(("delegates", "party", "overflow")):
            t[i + 1] += int(o[col])
        t[0] += 1
        t[4].append(o["org_key"])
    return [{"country": country, "provisional_group": g, "headline": h, "line": line,
             "organisations": n, "delegates": d, "party": p, "overflow": ov,
             "cases": " ".join(sorted(cases))}
            for (g, h, line), (n, d, p, ov, cases) in
            sorted(tally.items(), key=lambda x: (-x[1][1], x[0]))]


def main() -> None:
    raw = list(csv.DictReader(open(C.RAW, encoding="utf-8-sig")))
    table = list(csv.DictReader(open(ACTIVITY_TABLE)))
    alone, reasons, groups = [], [], []
    for country in C.COUNTRIES.values():
        orgs = list(csv.DictReader(open(
            country.test / f"{country.stem}_by_organisation_0.13_PROVISIONAL.csv")))
        alone += list_alone(raw, country.name)
        reasons += cannot_say(orgs, country.name)
        groups += activity(orgs, table, country.name)
    G._write(OUT / "kind_from_list_alone_PROVISIONAL.csv", alone)
    G._write(OUT / "cannot_say_reasons_PROVISIONAL.csv", reasons)
    G._write(OUT / "business_activity_PROVISIONAL.csv", groups)
    for r in alone + reasons + groups:
        print(r)


if __name__ == "__main__":
    main()
