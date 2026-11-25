"""The literature counts written in a study's numbers file equal what the library gives.

A rule a machine can decide: every figure in the "Literature counts regenerated"
table of <study>/docs/archived/numbers.md that can be computed from
literature/<study>/data/processed/screening.json (and the quotation check) is computed here and compared.
Two rows cannot be computed from the library and stay with the written rules:
"Sources this draft rests on" and "Supplied by hand and read".

Skipped when the library is not there (a fresh copy of the workspace).
"""

import json
import re
from pathlib import Path

import pytest
from rag import paths

ROOT = Path(__file__).resolve().parents[2]
LIT = ROOT / "literature"
HEADING = "## Literature counts regenerated"
NOT_COMPUTED = ("Sources this draft rests on", "Supplied by hand and read")



def computed(study: str) -> dict[str, str]:
    """Each figure of the study's own library, keyed by the start of its row label in the table."""
    LIB = LIT / study
    from rag.quotes import check_all

    sources = json.loads((LIB / paths.SCREENING).read_text())["sources"]

    def n(test) -> int:
        return sum(1 for s in sources if test(s))

    def screened_in(s, outcome=None) -> bool:
        return s["decision"] == "in" and outcome in (None, s["outcome"])

    not_judged = n(lambda s: s["decision"] == "candidate")
    search = n(lambda s: s["decision"] == "candidate" and s["signals"].get("found_by_search"))
    quotes = check_all(root=str(LIB))
    figures = {
        "Sources and references considered": len(sources),
        "Screened in and not read": n(screened_in) - n(lambda s: screened_in(s, "read")),
        "Screened in": n(screened_in),
        "Screened out": n(lambda s: s["decision"] == "out"),
        "Not yet judged": not_judged,
        "of which from search 3": search,
        "remainder": not_judged - search,
        "Read into a record": n(lambda s: screened_in(s, "read")),
        "Held, not yet read": n(lambda s: screened_in(s, "held")),
        "of which a landing page": n(lambda s: screened_in(s, "held") and s["thin"]),
        "Could not be obtained": n(lambda s: screened_in(s, "download failed")),
        "No web address": n(lambda s: screened_in(s, "no web address")),
    }
    out = {k: f"{v:,}" for k, v in figures.items()}
    return out | {"Quotations checked and found": f"{quotes['ok']:,} of {quotes['quotes']:,}"}


def table_rows(text: str) -> dict[str, str]:
    """Label and value of each row of the regenerated table."""
    section = text.partition(HEADING)[2].partition("\n## ")[0]
    rows = re.findall(r"^\| ([^|\n]+?) \| ([^|\n]+?) \|", section, flags=re.M)
    return {label: value for label, value in rows if label != "Figure" and set(label) != {"-"}}


def differences(text: str, figures: dict[str, str]) -> list[str]:
    """Rows whose written value is not the computed one, and rows that nothing checks."""
    problems = []
    rows = table_rows(text)
    for label, value in rows.items():
        if label.startswith(NOT_COMPUTED):
            continue
        # the longest key that starts the label, so "Screened in and not read" is not "Screened in"
        key = max((k for k in figures if label.startswith(k)), key=len, default=None)
        if key is None:
            problems.append(f"{label}: no rule computes this row")
        elif value != figures[key]:
            problems.append(f"{label}: written {value}, the library gives {figures[key]}")
    missing = [k for k in figures if not any(label.startswith(k) for label in rows)]
    return problems + [f"{k}: row missing from the table" for k in missing]


def numbers_files() -> list[Path]:
    """Numbers files with the table, for studies whose library is in this copy."""
    return [p for p in sorted(ROOT.glob("*/docs/archived/numbers.md"))
            if HEADING in p.read_text() and (LIT / p.parents[2].name / paths.SCREENING).exists()]


@pytest.mark.parametrize("path", numbers_files(), ids=lambda p: p.parents[2].name)
def test_allows_the_written_literature_counts_when_they_match_the_library(path):
    assert differences(path.read_text(), computed(path.parents[2].name)) == []


@pytest.mark.skipif(not any(LIT.glob("*/" + str(paths.SCREENING))), reason="no literature library here")
def test_at_least_one_numbers_file_is_checked():
    assert numbers_files(), "no numbers file holds the regenerated literature table"


# The same comparison on an invented table, to show that it blocks and that it allows.
INVENTED = {"Screened in and not read": "4", "Screened in": "9", "Screened out": "1,200"}
TABLE = """# Numbers

## Literature counts regenerated (invented)

| Figure | Value | Was | Where in the proposal |
|---|---|---|---|
| Screened in | 9 | 8 | section 2 |
| Screened out | 1,200 | 1,150 | section 2 |
| Screened in and not read (9 less 5) | 4 | 3 | section 2 |
| Sources this draft rests on | 5 | 5 | section 2 |

## Next section

| Screened in | 99 | 99 | not part of the table |
"""


def test_allows_a_table_whose_figures_all_match():
    assert differences(TABLE, INVENTED) == []


def test_blocks_a_figure_that_differs_from_the_library():
    wrong = TABLE.replace("| Screened in | 9 |", "| Screened in | 10 |")
    assert differences(wrong, INVENTED) == ["Screened in: written 10, the library gives 9"]


def test_blocks_a_row_that_nothing_checks_and_a_row_removed():
    new_row = "| Sources rejected twice | 4 | 4 | nowhere |\n"
    extra = TABLE.replace("| Screened out |", new_row + "| Screened out |")
    assert differences(extra, INVENTED) == ["Sources rejected twice: no rule computes this row"]
    kept = (line for line in TABLE.splitlines() if not line.startswith("| Screened out |"))
    removed = "\n".join(kept)
    assert differences(removed, INVENTED) == ["Screened out: row missing from the table"]
