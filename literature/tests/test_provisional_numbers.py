"""Provisional numbers stay out of formal outputs unless labelled (S10, the provisional half).

Rule 6: exploratory numbers are labelled provisional and must not silently enter a formal
output. Each study may keep a register, <study>/docs/archived/provisional-numbers.md, with a
table: the figure as written, the file it comes from, where in the file, and why it is
provisional. Checked here:

- every `*_PROVISIONAL.csv` in the study's outputs/ is named in the register;
- every figure in the register is in its file (a value in it, or "sum of <column>");
- the proposal, the codebook and each report draft that writes a registered figure, or cites a
  provisional file, says "provisional" in its first five lines.

Not covered: a provisional number reworded (for example "two hundred and fifty-three") or
not registered. The register is kept by hand; the first check makes a new provisional file
impossible to forget, not each figure in it.
"""

import csv
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTER = "docs/archived/provisional-numbers.md"
LABEL = re.compile(r"(?<![\w/-])provisional(?!\w|\.\w)", re.IGNORECASE)  # the word, not a file name
COMPANIONS = {"numbers.md", "named-organisations.md"}  # records beside a report draft, not the draft


def register_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 3 and not set(cells[0]) <= set("-") and cells[0] != "Figure as written":
            rows.append(cells)
    return rows


def phrase_pattern(figure: str) -> re.Pattern:
    """The figure as written, allowing a thousands comma or none, and any spacing."""
    parts = []
    for token in re.split(r"(\d+(?:\.\d+)?)", figure.replace(",", "")):
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            whole, dot, dec = token.partition(".")
            parts.append(re.sub(r"\B(?=(\d{3})+$)", ",?", whole) + (r"\." + dec if dot else ""))
        elif token:
            parts.append(r"\s*" + r"\s+".join(re.escape(w) for w in token.split()) + r"\s*")
    return re.compile(r"(?<![\d.,])" + "".join(parts) + r"(?![\d])", re.IGNORECASE)


def in_file(where: str, path: Path) -> bool:
    with path.open(newline="") as f:
        return any(v.strip() == where for row in csv.DictReader(f) for v in row.values() if v)


def summed(figure: str, where: str, path: Path) -> bool:
    column = where.removeprefix("sum of ").strip()
    with path.open(newline="") as f:
        total = sum(float(r[column]) for r in csv.DictReader(f) if r.get(column))
    number = float(re.search(r"\d+(?:\.\d+)?", figure.replace(",", "")).group())
    return abs(total - number) < 1e-9


def formal_documents(study: Path) -> list[Path]:
    docs = [study / "docs" / "research-proposal.md", study / "docs" / "codebook.md"]
    docs += [p for p in sorted((study / "report").glob("*.md")) if p.name not in COMPANIONS]
    return [p for p in docs if p.exists()]


def labelled(text: str) -> bool:
    head = [line for line in text.splitlines() if line.strip()][:5]
    return any(LABEL.search(line) for line in head)


def problems(study: Path, root: Path) -> list[str]:
    found = []
    register = study / REGISTER
    rows = register_rows(register.read_text()) if register.exists() else []
    named = {r[1].strip("`") for r in rows}
    for path in sorted((study / "outputs").rglob("*_PROVISIONAL.csv")):
        if str(path.relative_to(root)) not in named:
            found.append(f"{path.relative_to(root)} is provisional and not in {REGISTER}")
    for figure, file, where, *_ in rows:
        path = root / file.strip("`")
        if not path.exists():
            found.append(f"{figure}: {file} does not exist")
        elif where.startswith("sum of "):
            if not summed(figure, where, path):
                found.append(f"{figure}: not the {where} in {file}")
        elif not in_file(where, path):
            found.append(f"{figure}: {where} is not a value in {file}")
    patterns = [(r[0], phrase_pattern(r[0])) for r in rows]
    for doc in formal_documents(study):
        text = doc.read_text()
        if labelled(text):
            continue
        hits = [fig for fig, pat in patterns if pat.search(text)]
        if "_PROVISIONAL" in text:
            hits.append("a provisional file")
        for hit in hits:
            found.append(f"{doc.relative_to(root)} writes {hit} and is not labelled provisional")
    return found


def studies() -> list[Path]:
    return sorted(p.parent.parent.parent for p in ROOT.glob(f"*/{REGISTER}"))


@pytest.mark.parametrize("study", studies(), ids=lambda p: p.name)
def test_provisional_numbers_stay_out_of_unlabelled_formal_outputs(study):
    assert problems(study, ROOT) == []


def test_at_least_one_register_is_checked():
    assert studies(), f"no study has {REGISTER}"


# The same check on an invented study, to show that it blocks and that it allows.


@pytest.fixture
def invented(tmp_path):
    study = tmp_path / "harbour"
    (study / "outputs").mkdir(parents=True)
    (study / "docs" / "archived").mkdir(parents=True)
    (study / "report").mkdir()
    (study / "outputs" / "test_PROVISIONAL.csv").write_text("line,delegates\na,1200\nb,34\n")
    (study / REGISTER).write_text(
        "| Figure as written | File | Where in the file | Why provisional |\n|---|---|---|---|\n"
        "| 1,234 delegates | `harbour/outputs/test_PROVISIONAL.csv` | sum of delegates | test |\n"
        "| 34 delegates | `harbour/outputs/test_PROVISIONAL.csv` | 34 | test |\n"
    )
    (study / "docs" / "research-proposal.md").write_text("# Proposal\n\nWe will count delegates.\n")
    return study


def test_allows_a_clean_proposal_and_a_labelled_draft(invented):
    (invented / "report" / "draft.md").write_text("# Draft\n\n*PROVISIONAL. Not for publication.*\n\n1234 delegates.\n")
    (invented / "report" / "numbers.md").write_text("# Numbers\n\n`test_PROVISIONAL.csv`\n")
    assert problems(invented, invented.parent) == []


def test_blocks_a_registered_figure_in_an_unlabelled_proposal(invented):
    (invented / "docs" / "research-proposal.md").write_text("# Proposal\n\nA test found 1,234  Delegates.\n")
    assert problems(invented, invented.parent) == [
        "harbour/docs/research-proposal.md writes 1,234 delegates and is not labelled provisional"
    ]


def test_does_not_match_a_longer_number(invented):
    (invented / "docs" / "research-proposal.md").write_text("# Proposal\n\nThere were 134 delegates.\n")
    assert problems(invented, invented.parent) == []


def test_blocks_an_unlabelled_draft_citing_a_provisional_file(invented):
    (invented / "report" / "draft.md").write_text("# Draft\n\nFrom `test_PROVISIONAL.csv`.\n")
    assert len(problems(invented, invented.parent)) == 1


def test_blocks_an_unregistered_provisional_file(invented):
    (invented / "outputs" / "other_PROVISIONAL.csv").write_text("a\n1\n")
    assert problems(invented, invented.parent) == [
        "harbour/outputs/other_PROVISIONAL.csv is provisional and not in docs/archived/provisional-numbers.md"
    ]


def test_blocks_a_figure_not_in_its_file(invented):
    reg = invented / REGISTER
    reg.write_text(reg.read_text().replace("| 34 |", "| 35 |"))
    assert problems(invented, invented.parent) == [
        "34 delegates: 35 is not a value in `harbour/outputs/test_PROVISIONAL.csv`"
    ]
