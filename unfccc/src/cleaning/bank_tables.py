"""Read the Banking on Climate Chaos 2026 expansion sector league tables into one CSV.

Source: literature/unfccc/data/raw/pdfs/method/bankingonclimatechaos-sector-tables-2026.pdf
(library id bankingonclimatechaos-sector-tables-2026). The raw file is never changed.

The PDF holds three league tables of the 65 largest banks, by financing (lending and
underwriting, in billion US dollars) to companies expanding oil and gas: upstream,
midstream and gas power. Each table ends with a "Grand Total" row, which is used here
as a check and not written to the CSV.

The table is a reference list of banks. It is not a classification: whether a bank on it
counts as fossil fuel-linked is the lead researcher's decision (codebook section 9, tier 3).

Run from the workspace root:
    uv run python -I -m cleaning.bank_tables
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

SOURCE_ID = "bankingonclimatechaos-sector-tables-2026"
PDF = Path("literature/unfccc/data/raw/pdfs/method") / f"{SOURCE_ID}.pdf"
OUT = Path("literature/unfccc/data/processed/tables") / f"{SOURCE_ID}.csv"

# In the order the tables appear in the document.
SECTORS = ["upstream_oil_gas_expansion", "midstream_oil_gas_expansion", "gas_power_expansion"]
YEARS = ["2021", "2022", "2023", "2024", "2025"]
FIELDS = (
    ["sector", "rank_2025", "bank"]
    + [f"usd_bn_{y}" for y in YEARS]
    + ["usd_bn_total_2021_2025", "change_2024_2025_usd_bn", "pct_change_2024_2025", "source_id", "page"]
)


def parse_number(cell: str | None) -> float | None:
    """Turn a table cell into a number, or None where the source prints "-" (no value).

    The PDF stores the decimal point and the minus sign on a second line of the cell:
    "$3 6\\n." is $3.6, "$1 0 B\\n- ." is -$1.0 B, "12%\\n-" is -12%, "103%" is 103%.
    """
    if cell is None:
        return None
    lines = cell.strip().split("\n")
    main, marks = lines[0].strip(), " ".join(lines[1:])
    if main in ("", "-"):
        return None
    if "." in marks:
        main, n = re.subn(r"(\d) (\d)", r"\1.\2", main, count=1)
        if n != 1:
            raise ValueError(f"decimal point with no place to put it: {cell!r}")
    digits = re.sub(r"[$+%B, ]", "", main)
    if not re.fullmatch(r"\d+(\.\d+)?", digits):
        raise ValueError(f"not a number: {cell!r}")
    value = float(digits)
    return -value if "-" in marks else value


def clean_name(cell: str) -> str:
    """Join a bank name that the PDF wraps over lines.

    A line that is a single lower-case letter is the end of a word cut by the column
    width ("Toronto-Dominio\\nn Bank", "Communication\\ns"); other breaks are spaces.
    """
    parts = cell.strip().split("\n")
    name = parts[0]
    for part in parts[1:]:
        cut_word = re.match(r"[a-z]( |$)", part) is not None
        name += part if cut_word else " " + part
    return name


def read_tables(pdf_path: Path = PDF) -> tuple[list[dict], list[dict]]:
    """Return (bank rows, grand total rows) from the PDF."""
    import pymupdf

    rows, totals, sector = [], [], 0
    with pymupdf.open(pdf_path) as doc:
        for page_no, page in enumerate(doc, start=1):
            for table in page.find_tables().tables:
                for cells in table.extract():
                    first = (cells[0] or "").strip()
                    if "rank" in first.lower():
                        continue
                    numbers = [parse_number(c) for c in cells[2:10]]
                    record = dict(zip(FIELDS[3:11], numbers))
                    record.update(sector=SECTORS[sector], source_id=SOURCE_ID, page=page_no)
                    if first.lower().startswith("grand total"):
                        totals.append(record)
                        sector += 1
                    else:
                        record.update(rank_2025=int(first), bank=clean_name(cells[1]))
                        rows.append(record)
    return rows, totals


def check(rows: list[dict], totals: list[dict]) -> list[str]:
    """Problems found when the table is checked against itself. Empty means none."""
    problems = []
    if len(totals) != len(SECTORS):
        problems.append(f"expected {len(SECTORS)} grand total rows, found {len(totals)}")
    for s, sector in enumerate(SECTORS):
        part = [r for r in rows if r["sector"] == sector]
        if [r["rank_2025"] for r in part] != list(range(1, len(part) + 1)):
            problems.append(f"{sector}: ranks are not 1 to {len(part)} in order")
        for r in part:
            years = [r[f"usd_bn_{y}"] for y in YEARS]
            if None in years or r["usd_bn_total_2021_2025"] is None:
                problems.append(f"{sector}: {r['bank']} has a missing figure")
            # each figure is rounded to 0.1, so five of them can differ from the total by 0.3
            elif abs(sum(years) - r["usd_bn_total_2021_2025"]) > 0.3:
                problems.append(f"{sector}: {r['bank']} years do not add up to its total")
        if s < len(totals):
            for col in FIELDS[3:9]:
                printed, summed = totals[s][col], sum(r[col] or 0 for r in part)
                # rounding of up to 0.05 per bank
                if printed is None or abs(printed - summed) > 0.05 * len(part) + 0.1:
                    problems.append(f"{sector}: {col} sums to {summed:.1f}, grand total says {printed}")
    return problems


def main() -> int:
    rows, totals = read_tables()
    problems = check(rows, totals)
    for p in problems:
        print("PROBLEM:", p)
    if problems:
        print("Nothing written.")
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    for sector in SECTORS:
        print(sector, sum(r["sector"] == sector for r in rows), "banks")
    print("distinct banks:", len({r["bank"] for r in rows}))
    print("written:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
