"""Turn the UNFCCC list of admitted NGOs, as retrieved from its public data feed, into a CSV.

Source page: https://unfccc.int/process/parties-non-party-stakeholders/non-party-stakeholders/admitted-ngos/list-of-admitted-ngos
The table on that page is a Microsoft Power BI report published for anonymous viewing. The raw
file is the reply of the report's public data feed to one request for the whole "ngo" table
(columns: Official Name, URL, Person, City, Country, Constituency, Business Role Name; phone, fax
and email were not requested). The raw file is never changed.

The feed sends the table compressed: a value that repeats the row above is left out (bit mask
"R"), an empty value is left out (bit mask "Ø"), and frequent values are sent as a position in
a per-column list ("ValueDicts"). `decode` undoes this.

Admission as an observer, and the constituency an organisation chose, are registration facts.
They are not evidence of a fossil fuel link (codebook rule G2).

The contact person column names real people (workspace rule 8): it is kept for matching only
and is never printed in a report or a chat reply.

Run from the workspace root:
    uv run python -I -m cleaning.admitted_ngos
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

RAW = Path("unfccc/data/raw/unfccc-admitted-ngos-2026-11-25.json")
OUT = Path("unfccc/data/processed/admitted_ngos.csv")

# feed column -> CSV column, in the order requested
COLUMNS = {
    "ngo.Official Name": "official_name",
    "ngo.URL": "website",
    "ngo.Person": "contact_person",
    "ngo.City": "city",
    "ngo.Country": "country",
    "ngo.Constituency": "constituency",
    "ngo.Business Role Name": "role",
}


def decode(reply: dict) -> list[dict]:
    """Return the table rows held in one reply of the data feed."""
    data = reply["results"][0]["result"]["data"]
    names = [COLUMNS[s["Name"]] for s in data["descriptor"]["Select"]]
    shape = data["dsr"]["DS"][0]
    dicts = shape.get("ValueDicts", {})
    rows, schema, previous = [], None, [None] * len(names)
    for item in shape["PH"][0]["DM0"]:
        schema = item.get("S", schema)
        repeat, empty, sent = item.get("R", 0), item.get("Ø", 0), iter(item["C"])
        current = []
        for i, column in enumerate(schema):
            if repeat >> i & 1:
                value = previous[i]
            elif empty >> i & 1:
                value = None
            else:
                value = next(sent)
                # every column is text, so a number is a position in that column's list
                if isinstance(value, int) and "DN" in column:
                    value = dicts[column["DN"]][value]
            current.append(value)
        if next(sent, None) is not None:
            raise ValueError(f"row {len(rows) + 1} has more values than columns")
        rows.append(dict(zip(names, current)))
        previous = current
    return rows


def tidy(value: str | None) -> str:
    return " ".join(value.split()) if value else ""


def check(rows: list[dict]) -> list[str]:
    """Problems found in the decoded table. Empty means none."""
    problems = []
    if any(not r["official_name"] for r in rows):
        problems.append("a row has no organisation name")
    if any(not isinstance(v, (str, type(None))) for r in rows for v in r.values()):
        problems.append("a value is not text")
    if len({tuple(r.values()) for r in rows}) != len(rows):
        problems.append("two rows are identical")
    return problems


def main() -> int:
    rows = decode(json.loads(RAW.read_text(encoding="utf-8")))
    problems = check(rows)
    for p in problems:
        print("PROBLEM:", p)
    if problems:
        print("Nothing written.")
        return 1
    fields = [c for c in COLUMNS.values() if c != "role"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows({k: tidy(v) for k, v in r.items()} for r in rows)
    print("rows:", len(rows))
    print("distinct organisation names:", len({tidy(r["official_name"]) for r in rows}))
    print("written:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
