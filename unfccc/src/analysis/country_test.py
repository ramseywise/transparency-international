"""Country tests of the draft codebook 0.13: the same counts for any country. PROVISIONAL.

For each country: the draw (one row per spelling), the stored classification records, and
the counts that answer the brief's two questions, before and after the person lookups.
Germany's rules stay in analysis.germany_test; this module reuses its functions unchanged.

Saudi Arabia is outside the brief (EU and its members). It is a test of the method on a
delegation where fossil links are expected (Ramsey's instruction, 2026-11-25). Its draw is
made from the raw list, with the "Department" column as the organisation field.

The largest entries that stayed unidentified were searched a second time under codebook 0.14
(rules I4 to I6). Those records are laid over the 0.13 ones; the file names keep "0.13",
the version of every other record.

Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.country_test
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

from analysis import germany_test as G
from cleaning.orgs import split_acting_for

STUDY = G.STUDY
BASE = STUDY / "data" / "processed" / "draft-codebook"
OUT = STUDY / "outputs" / "draft-codebook"
RAW = STUDY / "data" / "raw" / "unfcc-2026.csv"

KINDS = ("public_sector", "civil_society_and_other_non_state", "business_and_commercial")
KIND_ORDER = KINDS + ("other", "not_identified")
NO_ORGANISATION = "no organisation written"
# Entries searched a second time under codebook 0.14 (search order I5, list context I4).
RESEARCHED = "classified-0.14"

# Saudi Arabia: spelling of the Department field (lower case) -> case code. Spellings of one
# word are joined; nothing else is.
SAUDI_CASES = {
    "moen": "S01", "moens": "S01",
    "meraj": "S02", "miraj": "S02", "miraje": "S02", "merag": "S02",
    "meraj company": "S02", "miraj company": "S02",
    "acwa": "S03", "mewa": "S04", "mofa": "S05", "embassy": "S06", "kacst": "S07",
    "kaust": "S08", "kasut": "S08", "mgi": "S09", "mof": "S10", "gaca": "S11",
    "media": "S12", "coffee": "S13", "abeer": "S14", "office of the ceo": "S15", "-": "S16",
}


@dataclass(frozen=True)
class Country:
    slug: str
    name: str
    prefix: str
    variants: dict = field(default_factory=dict)      # case -> (org_key, reason)
    unresolved: dict = field(default_factory=dict)    # case -> reason
    no_organisation: tuple = (0, 0)                   # (party, overflow) with nothing written
    lookups: dict = field(default_factory=dict)       # lookup case -> org_key of the employer

    @property
    def test(self) -> Path:
        return BASE / f"{self.slug}-test"

    @property
    def stem(self) -> str:
        return self.slug.replace("-", "_")


_NO_EVIDENCE = "no evidence found"
COUNTRIES = {
    "germany": Country(
        "germany", "Germany", "G", G.VARIANTS, G.UNRESOLVED,
        # PG1's employer is the body already classified as G07; PG5 was not found.
        # PG6 to PG39 are the delegates under G02: one employer found (PG34).
        lookups={"PG1": "G07", "PG2": "GP2", "PG3": "GP3", "PG4": "GP4", "PG34": "GP34"}),
    "luxembourg": Country(
        "luxembourg", "Luxembourg", "L",
        unresolved={c: _NO_EVIDENCE for c in ("L11", "L20", "L23", "L26", "L27", "L32")},
        no_organisation=(2, 0),
        # PL1 found an internship only; whether that is an affiliation is the lead
        # researcher's call, so the delegate is not moved. PL2 was not found.
        lookups={}),
    "saudi-arabia": Country(
        "saudi-arabia", "Saudi Arabia", "S",
        # S01 is not listed: its record of the second search (codebook I4) decides it.
        unresolved={"S02": "could be several entities, none chosen (two searches)",
                    "S06": "generic text", "S12": "generic text", "S13": "generic text",
                    "S14": "not an organisation", "S15": "not an organisation",
                    "S16": "not an organisation"}),
}


def saudi_draw(raw_rows: list[dict]) -> list[dict]:
    """One row per case from the raw list: Party and overflow rows nominated by Saudi Arabia."""
    cases: dict[str, dict] = {}
    for r in raw_rows:
        if r["Nominated by"] != "Saudi Arabia" or r["sheet"] not in ("Parties", "Party overflow"):
            continue
        text = r["Department"].strip()
        code = SAUDI_CASES.get(text.casefold())
        if code is None:
            raise ValueError(f"spelling with no case code: {text!r}")
        row = cases.setdefault(code, {"case": code, "org_id": "", "spellings": {},
                                      "delegates": 0, "party": 0, "overflow": 0})
        row["spellings"][text] = row["spellings"].get(text, 0) + 1
        row["delegates"] += 1
        row["party" if r["sheet"] == "Parties" else "overflow"] += 1
    out = []
    for code in sorted(cases):
        row = cases[code]
        spellings = sorted(row.pop("spellings").items(), key=lambda x: (-x[1], x[0]))
        out.append({"case": code, "org_id": "", "org_canonical_name": spellings[0][0],
                    "delegates": row["delegates"], "party": row["party"],
                    "overflow": row["overflow"], "raw": " | ".join(s for s, _ in spellings),
                    "country_context": "Saudi Arabia"})
    return out


def case_table(draw_rows: list[dict], country: Country) -> list[dict]:
    """The draw with the organisation each spelling belongs to, or why it has none."""
    out = []
    for r in draw_rows:
        employer, acting_for = split_acting_for(r["raw"])
        case = r["case"]
        if case in country.unresolved:
            key, why = None, country.unresolved[case]
        elif employer is None:
            key, why = None, "not an organisation"
        elif case in country.variants:
            key, why = country.variants[case]
        else:
            key, why = case, "own spelling"
        out.append({**r, "employer": employer, "acting_for": acting_for, "org_key": key,
                    "join_reason": why})
    party, overflow = country.no_organisation
    if party or overflow:
        out.append({**{k: "" for k in out[0]}, "case": f"{country.prefix}00",
                    "delegates": party + overflow, "party": party, "overflow": overflow,
                    "country_context": country.name, "org_key": None,
                    "join_reason": NO_ORGANISATION})
    return out


def apply_lookups(cases: list[dict], lookups: list[dict], employer_keys: dict,
                  prefix: str) -> list[dict]:
    """The case table after the person lookups: each delegate whose employer was found moves
    to that employer's record, as a row of its own. The first table is left as it was."""
    out = [dict(c) for c in cases]
    by_case = {c["case"]: c for c in out}
    for lk in lookups:
        target = employer_keys.get(lk["case"])
        if lk.get("status") != "found" or not target:
            continue
        origin = by_case[lk.get("org_case") or f"{prefix}00"]
        col = "overflow" if "overflow" in lk["badge_type"].lower() else "party"
        if int(origin[col]) < 1:
            raise ValueError(f"{lk['case']}: no {col} delegate left in {origin['case']}")
        origin[col] = int(origin[col]) - 1
        origin["delegates"] = int(origin["delegates"]) - 1
        out.append({**{k: "" for k in origin}, "case": lk["case"], "delegates": 1,
                    "party": int(col == "party"), "overflow": int(col == "overflow"),
                    "country_context": origin["country_context"], "org_key": target,
                    "join_reason": f"person lookup (from {origin['case']})"})
    return [c for c in out if int(c["delegates"]) > 0]


def kind_group(value: str, line: str) -> str:
    """The chart group of an organisation's kind. An inferred kind counts; no kind does not."""
    if line == "unknown":
        return "not_identified"
    return value if value in KINDS else "other"


def organisations(cases: list[dict], records: dict[str, dict]) -> list[dict]:
    """germany_test.by_organisation, plus the kind group and the type of business."""
    orgs = G.by_organisation(cases, records)
    for o in orgs:
        rec = records.get(o["org_key"]) if G.has_record(o["identity"]) else None
        entry = ((rec or {}).get("attributes") or {}).get("business_type")
        line, value = G.line_of(entry) if rec else ("unknown", "identity unresolved")
        o["business_type"], o["business_type_line"] = value, line
        o["kind_group"] = kind_group(o["kind"], o["kind_line"])
    return orgs


def _tally(orgs: list[dict], key) -> dict:
    out: dict = {}
    for o in orgs:
        t = out.setdefault(key(o), [0, 0, 0, 0])
        t[0] += 1; t[1] += o["delegates"]; t[2] += o["party"]; t[3] += o["overflow"]
    return out


def summary(country: str, view: str, orgs: list[dict]) -> list[dict]:
    """Long table: delegates by kind, by type of business, and by fossil headline (for all
    delegates and for business only), with Party and overflow apart. No names."""
    total = sum(o["delegates"] for o in orgs)
    business = [o for o in orgs if o["kind_group"] == "business_and_commercial"]
    rows = []

    def add(measure, tally, order, base):
        for value in sorted(tally, key=order):
            n, d, p, ov = tally[value]
            label, line = value if isinstance(value, tuple) else (value, "")
            rows.append({"country": country, "view": view, "measure": measure, "value": label,
                         "line": line, "organisations": n, "delegates": d, "party": p,
                         "overflow": ov, "base": base,
                         "share": round(100 * d / base, 1) if base else ""})

    add("kind", _tally(orgs, lambda o: o["kind_group"]), KIND_ORDER.index, total)
    add("business_type", _tally(business, lambda o: (o["business_type"] if
        o["business_type_line"] != "unknown" else "unknown", o["business_type_line"])),
        lambda v: v, sum(o["delegates"] for o in business))
    head = lambda v: (G.HEADLINE_ORDER.index(v[0]), G.LINES.index(v[1]))  # noqa: E731
    add("headline_all", _tally(orgs, lambda o: (o["headline"], o["headline_line"])), head, total)
    add("headline_business", _tally(business, lambda o: (o["headline"], o["headline_line"])),
        head, sum(o["delegates"] for o in business))
    return rows


def load(folder: Path) -> dict[str, dict]:
    return G.load_records(folder) if folder.exists() else {}


def employer_records(folder: Path) -> dict[str, dict]:
    """Records of the employers found by person lookup. One classified under codebook 0.14
    is laid over a 0.13 one with the same key."""
    return {**load(folder / "classified-0.13"), **load(folder / RESEARCHED)}


def run(country: Country) -> tuple[list[dict], dict]:
    """Write the country's tables; return its summary rows, before and after the person
    lookups, and the count of lookups."""
    draw_path = country.test / f"{country.stem}_test_draw.csv"
    if country.slug == "saudi-arabia":
        G._write(draw_path, saudi_draw(list(csv.DictReader(open(RAW, encoding="utf-8-sig")))))
    cases = case_table(list(csv.DictReader(open(draw_path))), country)
    # Records of the 0.13 run, with the entries searched again under codebook 0.14 laid over
    # them. A 0.14 record replaces the 0.13 one for the same case; no record is relabelled.
    records = {**load(country.test / "classified-0.13"), **load(country.test / RESEARCHED)}
    lookups = [json.loads(f.read_text())
               for f in sorted((country.test / "person-lookup").glob("P*.json"))]
    after_cases = apply_lookups(cases, lookups, country.lookups, country.prefix)
    after_records = {**records, **employer_records(country.test / "person-lookup")}
    rows = []
    for view, c, recs in (("organisation search", cases, records),
                          ("with person lookups", after_cases, after_records)):
        orgs = organisations(c, recs)
        tag = "" if view == "organisation search" else "_with_lookups"
        G._write(country.test / f"{country.stem}_by_organisation{tag}_0.13_PROVISIONAL.csv", orgs)
        rows += summary(country.name, view, orgs)
    G._write(OUT / f"{country.slug}-test" / f"{country.stem}_summary_PROVISIONAL.csv", rows)
    moved = sum(c["join_reason"].startswith("person lookup") for c in after_cases)
    return rows, {"country": country.name, "lookups_run": len(lookups),
                  "employer_found": sum(lk.get("status") == "found" for lk in lookups),
                  "moved_to_a_record": moved}


def main() -> None:
    rows, lookups = [], []
    for country in COUNTRIES.values():
        r, lk = run(country)
        rows += r
        lookups.append(lk)
    G._write(OUT / "comparison" / "country_comparison_PROVISIONAL.csv", rows)
    G._write(OUT / "comparison" / "person_lookups_PROVISIONAL.csv", lookups)
    print(lookups)
    for r in rows:
        if r["measure"] in ("kind", "headline_all") and r["view"] == "organisation search":
            print(f"{r['country']:13s} {r['measure']:13s} {r['value']:34s} {r['line']:17s}"
                  f" {r['delegates']:4d} (P {r['party']}, O {r['overflow']}) {r['share']}%")


if __name__ == "__main__":
    main()
