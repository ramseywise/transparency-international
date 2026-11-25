"""Checks on the Claude setup: agents, skills, the workspace instructions, the raw-file guard.

These need no model. They catch the setup drifting apart: a skill that names an
agent that no longer exists, a model table that disagrees with an agent file, an
instruction that points at a file that has moved.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
CLAUDE = ROOT / ".claude"
INSTRUCTIONS = (ROOT / "CLAUDE.md").read_text()
AGENTS = sorted((CLAUDE / "agents").glob("*.md"))
SKILLS = sorted(p for p in (CLAUDE / "skills").iterdir() if p.is_dir())
HOOK = CLAUDE / "hooks" / "protect_raw.py"

# Named in the instructions but made by a later stage of the study.
MADE_LATER = {
    "unfccc/docs/codebook.md",
    "unfccc/outputs/",
    "unfccc/report/",
}


# Named only as the place something used to be.
MOVED_AWAY = {"unfccc/src/rag/"}


def frontmatter(path: Path) -> dict:
    head = path.read_text().split("---")[1]
    return dict(re.findall(r"^([a-z_-]+):\s*(.+)$", head, flags=re.M))


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_file_is_complete(path):
    meta = frontmatter(path)
    assert meta["name"] == path.stem
    assert len(meta["description"]) > 20
    assert meta["tools"]
    assert meta["model"] in {"haiku", "sonnet", "opus"}


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_model_matches_the_table_in_the_instructions(path):
    row = re.search(rf"^\|[^\n]*\| `{path.stem}` \| (\w+) \|", INSTRUCTIONS, flags=re.M)
    assert row, f"{path.stem} is missing from the model table in CLAUDE.md"
    assert row.group(1) == frontmatter(path)["model"]


def test_model_table_names_no_agent_without_a_file():
    in_table = set(re.findall(r"^\|[^\n|]*\| `([a-z-]+)` \| \w+ \|", INSTRUCTIONS, flags=re.M))
    assert in_table == {p.stem for p in AGENTS}


@pytest.mark.parametrize("folder", SKILLS, ids=lambda p: p.name)
def test_skill_is_complete(folder):
    meta = frontmatter(folder / "SKILL.md")
    assert meta["name"] == folder.name
    assert len(meta["description"]) > 20


def test_stages_table_and_skill_folders_agree():
    in_table = set(re.findall(r"^\| `/([a-z-]+)` \|", INSTRUCTIONS, flags=re.M))
    assert in_table == {p.name for p in SKILLS}


def test_skills_name_only_agents_and_skills_that_exist():
    agents = {p.stem for p in AGENTS}
    skills = {p.name for p in SKILLS}
    for folder in SKILLS:
        text = (folder / "SKILL.md").read_text()
        roles = "checker|reader|researcher|reviewer|finder|classifier"
        for name in re.findall(rf"`([a-z]+-(?:{roles}))`", text):
            assert name in agents, f"/{folder.name} names the agent {name}, which has no file"
        for name in re.findall(r"`/([a-z]+(?:-[a-z]+)*)`", text):
            assert name in skills, f"/{folder.name} names the skill /{name}, which does not exist"


def paths_named(text: str) -> set[str]:
    tops = r"literature|style|evals|unfccc|templates|mcp_server|\.claude"
    found = re.findall(rf"`((?:{tops})/[^`\s]*)`", text)
    return {p.rstrip(".,;:") for p in found if not re.search(r"[<>*|{}$]|\.\.\.", p)}


def test_paths_named_in_the_setup_exist():
    files = [ROOT / "CLAUDE.md", *AGENTS, *(f / "SKILL.md" for f in SKILLS)]
    missing = {
        f"{f.relative_to(ROOT)} -> {p}"
        for f in files
        for p in paths_named(f.read_text())
        if p not in MADE_LATER | MOVED_AWAY and not (ROOT / p).exists()
    }
    assert not missing, "\n".join(sorted(missing))


def test_literature_commands_in_the_instructions_exist():
    listed = re.search(r"-m rag ([a-z|-]+)`", INSTRUCTIONS).group(1).split("|")
    out = subprocess.run(
        [sys.executable, "-I", "-m", "rag", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    offered = set(re.search(r"\{([a-z,-]+)\}", out).group(1).split(","))
    assert set(listed) == offered


# ---- the guard on raw files ----


def run_hook(
    path: Path, key: str = "file_path", hook: Path = HOOK, **more
) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": "Edit", "tool_input": {key: str(path)}} | more)
    return subprocess.run(
        [sys.executable, str(hook)], input=payload, capture_output=True, text=True
    )


def make(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x")
    return path


@pytest.mark.parametrize(
    "rel",
    [
        "unfccc/data/raw/list.xlsx",
        "literature/unfccc/data/raw/pdfs/a.pdf",
        "literature/unfccc/data/raw/pages/a.html",
        "literature/other/data/raw/pdfs/deep/er/a.pdf",
        "otherstudy/data/raw/deep/er/file.csv",
    ],
)
def test_guard_blocks_changes_to_existing_raw_files(tmp_path, rel):
    result = run_hook(make(tmp_path / rel))
    assert result.returncode == 2
    assert "Blocked" in result.stderr


def test_guard_blocks_notebook_edits_too(tmp_path):
    assert run_hook(make(tmp_path / "unfccc/data/raw/n.ipynb"), "notebook_path").returncode == 2


@pytest.mark.parametrize(
    "rel",
    [
        "unfccc/data/processed/table.csv",
        "literature/unfccc/data/processed/text/a.json",
        "literature/unfccc/data/processed/index/meta.json",
        "literature/unfccc/reports/search-log.md",
        "literature/unfccc/records/a.json",
        "unfccc/docs/raw-notes.md",
    ],
)
def test_guard_allows_everything_else(tmp_path, rel):
    assert run_hook(make(tmp_path / rel)).returncode == 0


def test_guard_allows_a_new_download(tmp_path):
    assert run_hook(tmp_path / "literature/unfccc/data/raw/pdfs/not-there-yet.pdf").returncode == 0


def test_guard_is_switched_on_in_the_settings():
    settings = json.loads((CLAUDE / "settings.json").read_text())
    entries = settings["hooks"]["PreToolUse"]
    commands = [h["command"] for e in entries for h in e["hooks"]]
    assert any("protect_raw.py" in c for c in commands)
    matcher = next(
        e["matcher"] for e in entries if any("protect_raw.py" in h["command"] for h in e["hooks"])
    )
    assert {"Edit", "Write", "NotebookEdit"} <= set(matcher.split("|"))
    assert HOOK.exists()


# ---- the guard on the test cases ----

EVALS_HOOK = CLAUDE / "hooks" / "protect_evals.py"
SUBAGENT = {"agent_id": "a1b2c3", "agent_type": "citation-checker"}
OUT_OF_REACH = [
    ".claude/skills/run-evals/cases/citation-checker/document.md",
    ".claude/skills/run-evals/cases/citation-checker/expected.json",
    ".claude/skills/run-evals/cases/org-classifier/evidence/K1.json",
    ".claude/skills/run-evals/cases/a-new-case/hint.md",
    ".claude/skills/run-evals/scripts/fingerprints.json",
    ".claude/skills/run-evals/scripts/fingerprint.py",
    ".claude/skills/run-evals/scripts/score.py",
    ".claude/skills/run-evals/runs/2026-11-24/expected.json",
]


@pytest.mark.parametrize("rel", OUT_OF_REACH)
def test_evals_guard_blocks_an_agent(tmp_path, rel):
    """Existing files and new ones alike: an agent must not add a file to a case either."""
    for path in (make(tmp_path / rel), tmp_path / "not-made" / rel):
        result = run_hook(path, hook=EVALS_HOOK, **SUBAGENT)
        assert result.returncode == 2 and "Blocked" in result.stderr


def test_evals_guard_blocks_an_agent_editing_a_notebook(tmp_path):
    path = make(tmp_path / ".claude/skills/run-evals/cases/x/n.ipynb")
    assert run_hook(path, "notebook_path", hook=EVALS_HOOK, **SUBAGENT).returncode == 2


@pytest.mark.parametrize("rel", OUT_OF_REACH)
def test_evals_guard_allows_the_main_session(tmp_path, rel):
    """No agent_id: the main session, which changes a case on purpose and re-fingerprints."""
    assert run_hook(make(tmp_path / rel), hook=EVALS_HOOK).returncode == 0


@pytest.mark.parametrize(
    "rel",
    [
        ".claude/skills/run-evals/runs/2026-11-24c/citation-checker.json",
        ".claude/skills/run-evals/reference/spec.md",
        ".claude/skills/run-evals/tests/test_score.py",
        "unfccc/data/processed/evidence/org-0001.json",
        "literature/records/a.json",
        "unfccc/docs/cases/score.py",
        ".claude/skills/codebook/cases/example.md",
    ],
)
def test_evals_guard_allows_an_agent_everything_else(tmp_path, rel):
    assert run_hook(make(tmp_path / rel), hook=EVALS_HOOK, **SUBAGENT).returncode == 0


def test_evals_guard_is_switched_on_in_the_settings():
    settings = json.loads((CLAUDE / "settings.json").read_text())
    entries = [
        e
        for e in settings["hooks"]["PreToolUse"]
        if any("protect_evals.py" in h["command"] for h in e["hooks"])
    ]
    assert entries and EVALS_HOOK.exists()
    assert {"Edit", "Write", "NotebookEdit"} <= set(entries[0]["matcher"].split("|"))


def test_no_agent_or_skill_hands_over_the_planted_answers():
    """No agent file names an expected.json. A skill may name one only to say it must
    not be opened, or (run-evals) to take the organisation names from it."""
    for path in AGENTS:
        assert "expected.json" not in path.read_text(), path.name
    for folder in SKILLS:
        for line in (folder / "SKILL.md").read_text().splitlines():
            if "expected.json" in line:
                assert folder.name == "run-evals", folder.name
                assert "must not open" in line or "evidence-finder" in line, line
