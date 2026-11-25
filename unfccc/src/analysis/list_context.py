"""The list's own context for one entry (codebook rule I4): counts of what the delegates under
it wrote in the other columns. Counts only: the Name column is never read into the result, and
a value written by fewer than MIN_COUNT delegates is folded into "(single values)", so that no
line of the result describes one person.

Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.list_context saudi-arabia S01
"""
import csv
import json
import sys

from analysis import country_test as ct

MIN_COUNT = 2
SINGLE = "(single values)"
BLANK = "(blank)"
COLUMNS = ("Functional title", "Department", "Home organization", "Relation",
           "Type of home organization", "Funding source", "Type of funding source")
SHEETS = {"Parties": "party", "Party overflow": "overflow"}
# The column that holds the entry, per delegation (see country_draw and country_test).
ENTRY_COLUMN = {"saudi-arabia": "Department"}
DEFAULT_ENTRY_COLUMN = "Home organization"


def counts(rows: list[dict], min_count: int = MIN_COUNT) -> dict:
    """Counts per column over all the rows given, most frequent first. Spellings are compared
    without case or outer spaces. Values below min_count are summed under SINGLE."""
    out: dict = {"delegates": len(rows), "badges": {}, "columns": {}}
    for r in rows:
        badge = SHEETS.get(r.get("sheet", ""), "other")
        out["badges"][badge] = out["badges"].get(badge, 0) + 1
    for col in COLUMNS:
        tally: dict[str, int] = {}
        for r in rows:
            value = (r.get(col) or "").strip().casefold() or BLANK
            tally[value] = tally.get(value, 0) + 1
        kept = {v: n for v, n in sorted(tally.items(), key=lambda x: (-x[1], x[0]))
                if n >= min_count}
        single = sum(n for n in tally.values() if n < min_count)
        if single:
            kept[SINGLE] = single
        out["columns"][col] = kept
    return out


def entry_rows(raw_rows: list[dict], country_name: str, column: str,
               spellings: set[str]) -> list[dict]:
    """The Party and overflow rows of one delegation whose entry is one of the spellings."""
    wanted = {s.strip().casefold() for s in spellings}
    return [r for r in raw_rows
            if r["Nominated by"] == country_name and r["sheet"] in SHEETS
            and r[column].strip().casefold() in wanted]


def spellings_of(country: ct.Country, case: str) -> set[str]:
    if country.slug == "saudi-arabia":
        return {s for s, code in ct.SAUDI_CASES.items() if code == case}
    draw = csv.DictReader(open(country.test / f"{country.stem}_test_draw.csv"))
    return {s for r in draw if r["case"] == case for s in r["raw"].split(" | ")}


def for_case(slug: str, case: str, raw_rows: list[dict] | None = None) -> dict:
    country = ct.COUNTRIES[slug]
    if raw_rows is None:
        raw_rows = list(csv.DictReader(open(ct.RAW, encoding="utf-8-sig")))
    column = ENTRY_COLUMN.get(slug, DEFAULT_ENTRY_COLUMN)
    rows = entry_rows(raw_rows, country.name, column, spellings_of(country, case))
    return {"case": case, "entry_column": column, **counts(rows)}


if __name__ == "__main__":
    print(json.dumps(for_case(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=1))
