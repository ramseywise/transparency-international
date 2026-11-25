"""Inputs for the person lookups of one case (rule 8, codebook 0.14 draft rule I5 step 3).

One file per delegate under the case, written to the test folder's `person-lookup/inputs/`
(inside `data/`, which is never in git or served). The files name people; nothing here prints
a name. Delegates listed as youth delegates are not looked up (decision of 2026-11-25) and
are counted instead.

usage: python -m analysis.person_inputs <country slug> <case> <first lookup number>
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys

from analysis import country_test as ct
from analysis import list_context as lc

YOUTH = ("youth", "jugend", "young delegate")
FIELDS = ("Name", "Functional title", "Department", "Home organization", "Relation")


def is_youth(row: dict) -> bool:
    text = " ".join(row.get(c, "") for c in ("Functional title", "Department", "Relation"))
    return any(w in text.casefold() for w in YOUTH)


def row_id(row: dict, occurrence: int) -> str:
    """Stable id of a raw row: sheet and field values, plus a counter for exact repeats."""
    base = "|".join([row.get("sheet", "")] + [row.get(c, "") for c in FIELDS])
    return f"r_{hashlib.sha1(base.encode()).hexdigest()[:12]}_{occurrence}"


def inputs(rows: list[dict], country: ct.Country, case: str, first: int) -> tuple[list[dict], int]:
    """The lookup inputs for the rows of one case, and how many rows were left out as youth."""
    out, seen, skipped = [], {}, 0
    for r in rows:
        if is_youth(r):
            skipped += 1
            continue
        rid = row_id(r, 0)
        seen[rid] = seen.get(rid, -1) + 1
        out.append({"case": f"P{country.prefix}{first + len(out)}", "org_case": case,
                    "row_id": row_id(r, seen[rid]), "badge_type": r["sheet"],
                    "country": country.name, "name": r["Name"],
                    "functional_title": r["Functional title"], "department": r["Department"],
                    "entry_as_written": r["Home organization"], "relation": r["Relation"]})
    return out, skipped


def main(slug: str, case: str, first: int) -> None:
    country = ct.COUNTRIES[slug]
    raw = list(csv.DictReader(open(ct.RAW, encoding="utf-8-sig")))
    column = lc.ENTRY_COLUMN.get(slug, lc.DEFAULT_ENTRY_COLUMN)
    rows = lc.entry_rows(raw, country.name, column, lc.spellings_of(country, case))
    made, skipped = inputs(rows, country, case, first)
    folder = country.test / "person-lookup" / "inputs"
    folder.mkdir(parents=True, exist_ok=True)
    for m in made:
        path = folder / f"{m['case']}.json"
        if path.exists():
            raise FileExistsError(path.name)
        path.write_text(json.dumps(m, ensure_ascii=False, indent=1))
    by_badge = {b: sum(m["badge_type"] == b for m in made) for b in sorted({m["badge_type"] for m in made})}
    print({"case": case, "rows": len(rows), "inputs": len(made), "left_out_as_youth": skipped,
           "by_badge": by_badge, "first": made[0]["case"] if made else None,
           "last": made[-1]["case"] if made else None})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
