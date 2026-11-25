"""The data figures in a study's numbers file are found in the generated file they name (S10).

Rule 6: a number in a proposal or report comes from a generated output. Every table in
<study>/docs/archived/numbers.md whose third column is headed "Measure..." lists, per row, the
number as written and the measures it comes from. The file is the last `*.csv` path named
before the table ("Same file" keeps the one before). Each row is checked both ways:

- every measure named is in the file (a `*` matches by pattern; `_x` is short for the first
  measure of the row with `_x` in place of its last part, or added to it);
- every number written equals one of the row's measures, rounded to the decimals written;
- every measure's value is among the numbers written.

Not covered here: that the number in the numbers file is the number in the proposal text,
and that a number labelled provisional stays out of a formal output.
"""

import csv
import re
from fnmatch import fnmatch
from pathlib import Path

import pytest
from rag import paths

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = re.compile(r"`([^`]+\.csv)`")
NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def numbers_in(cell: str) -> list[str]:
    """The numbers written in a cell, as written: "529 (295 / 234)" gives three."""
    return [n.replace(",", "") for n in NUMBER.findall(cell)]


def shape(part: str) -> str:
    return re.sub(r"\d+", "#", part)


def expand(names: list[str], values: dict[str, float]) -> tuple[list[str], list[str]]:
    """The full measure names of a row, and the names not found in the file."""
    full, unknown = [], []
    base = next((n for n in names if not n.startswith("_")), None)
    for name in names:
        if name.startswith("_") and base:
            head, sep, last = base.rpartition("_")
            name = head + name if sep and shape("_" + last) == shape(name) else base + name
        if "*" in name:
            hits = sorted(m for m in values if fnmatch(m, name))
            full += hits
            if not hits:
                unknown.append(name)
        elif name in values:
            full.append(name)
        else:
            unknown.append(name)
    return full, unknown


def matches(written: str, value: float) -> bool:
    decimals = len(written.partition(".")[2])
    return round(value, decimals) == float(written)


def measure_tables(text: str) -> list[tuple[str | None, list[list[str]]]]:
    """Each "Measure" table: the file it names, and its rows split into cells."""
    tables, current, csv_file = [], None, None
    for line in text.splitlines():
        if not line.startswith("|"):
            current = None
            found = CSV_PATH.findall(line)
            if found:
                csv_file = found[-1]
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if current is not None:
            if set("".join(cells)) - set("-: "):
                current.append(cells)
        elif len(cells) >= 3 and cells[2].startswith("Measure"):
            current = []
            tables.append((csv_file, current))
    return tables


def load(path: Path) -> dict[str, float]:
    with path.open(newline="") as f:
        return {row["measure"]: float(row["value"]) for row in csv.DictReader(f)}


def differences(text: str, root: Path) -> list[str]:
    problems = []
    for csv_file, rows in measure_tables(text):
        if csv_file is None or not (root / csv_file).exists():
            problems.append(f"{csv_file or 'no file named'}: not found; regenerate it")
            continue
        values = load(root / csv_file)
        for cells in rows:
            written, names = numbers_in(cells[0]), re.findall(r"`([^`]+)`", cells[2])
            full, unknown = expand(names, values)
            problems += [f"{cells[0]}: `{n}` is not in {csv_file}" for n in unknown]
            if not full:
                continue
            for n in written:
                if not any(matches(n, values[m]) for m in full):
                    problems.append(f"{cells[0]}: {n} is not the value of any measure named")
            for m in full:
                if not any(matches(n, values[m]) for n in written):
                    problems.append(f"{cells[0]}: `{m}` is {values[m]:g}, which is not written")
    return problems


def numbers_files() -> list[Path]:
    return [p for p in sorted(ROOT.glob("*/docs/archived/numbers.md")) if measure_tables(p.read_text())]


@pytest.mark.parametrize("path", numbers_files(), ids=lambda p: p.parent.parent.name)
def test_every_data_figure_is_in_the_generated_file_it_names(path):
    assert differences(path.read_text(), ROOT) == []


def test_at_least_one_numbers_file_is_checked():
    assert numbers_files(), "no numbers file holds a table of measures"


# The same check on an invented file and table, to show that it blocks and that it allows.
INVENTED_CSV = """section,measure,value,note
a,pairs,108.0,
a,delegates,529.0,
a,delegates_party,295.0,
a,delegates_party_overflow,234.0,
a,share_pct,13.9,
b,margin_n20,21.9,
b,margin_n30,17.9,
b,low_n20,69.9,
b,low_n30,74.4,
b,named,3799.0,
"""
TABLE = """# Numbers

All from `out/numbers.csv`.

| Number | What | Measure in the file |
|---|---|---|
| 108 | pairs | `pairs` |
| 529 (295 / 234) | delegates | `delegates`, `_party`, `_party_overflow` |
| 13.9 per cent | share | `share_pct` |
| 3,799 | named | `named` |

Same file.

| Number | What | Measure |
|---|---|---|
| 21.9, 17.9 | margins | `margin_n20`, `_n30` |
| 69.9 to 74.4 | lows | `low_n*` |

| Number | What | File |
|---|---|---|
| 1,291 | not a measure table | `literature/unfccc/data/processed/screening.json` |
"""


@pytest.fixture
def invented(tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "numbers.csv").write_text(INVENTED_CSV)
    return tmp_path


def test_allows_a_table_whose_figures_are_all_in_the_file(invented):
    assert differences(TABLE, invented) == []


def test_blocks_a_number_that_is_not_in_the_file(invented):
    wrong = TABLE.replace("| 13.9 per cent |", "| 14.0 per cent |")
    assert differences(wrong, invented) == [
        "14.0 per cent: 14.0 is not the value of any measure named",
        "14.0 per cent: `share_pct` is 13.9, which is not written",
    ]


def test_blocks_a_measure_that_is_not_in_the_file(invented):
    wrong = TABLE.replace("`share_pct`", "`share_percent`")
    assert differences(wrong, invented) == [
        "13.9 per cent: `share_percent` is not in out/numbers.csv"
    ]


def test_blocks_a_measure_left_unwritten(invented):
    wrong = TABLE.replace("| 529 (295 / 234) |", "| 529 (295) |")
    assert differences(wrong, invented) == [
        "529 (295): `delegates_party_overflow` is 234, which is not written"
    ]


def test_blocks_a_table_whose_file_is_missing(tmp_path):
    # once per table that names it
    assert differences(TABLE, tmp_path) == ["out/numbers.csv: not found; regenerate it"] * 2
