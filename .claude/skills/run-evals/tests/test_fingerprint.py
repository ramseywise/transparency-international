"""The eval cases and the scorer are the ones that were fingerprinted.

If this fails, a case, a planted answer or the scorer was changed (or added, or
removed) without re-fingerprinting. A changed case is a new case: see .claude/skills/run-evals/reference/spec.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import fingerprint  # noqa: E402


def test_cases_and_scorer_match_their_fingerprints():
    found = fingerprint.check()
    assert not any(found.values()), found


def test_fingerprints_cover_the_planted_answers_and_the_scorer():
    now = fingerprint.current()
    assert ".claude/skills/run-evals/scripts/score.py" in now
    planted = sorted((fingerprint.ROOT / ".claude" / "skills" / "run-evals" / "cases").glob("*/expected.json"))
    assert planted and all(p.relative_to(fingerprint.ROOT).as_posix() in now for p in planted)


def workspace(tmp_path: Path) -> tuple[Path, Path]:
    case = tmp_path / ".claude" / "skills" / "run-evals" / "cases" / "one"
    case.mkdir(parents=True)
    (case / "text.md").write_text("ten statements")
    (case / "expected.json").write_text("{}")
    scripts = tmp_path / ".claude" / "skills" / "run-evals" / "scripts"
    scripts.mkdir()
    (scripts / "score.py").write_text("rules")
    store = tmp_path / ".claude" / "skills" / "run-evals" / "scripts" / "fingerprints.json"
    assert fingerprint.write(tmp_path, store) == 3
    return tmp_path, store


def test_allows_files_that_have_not_changed(tmp_path):
    root, store = workspace(tmp_path)
    assert fingerprint.check(root, store) == {"changed": [], "added": [], "removed": []}


def test_blocks_a_changed_case_a_changed_answer_and_a_changed_scorer(tmp_path):
    root, store = workspace(tmp_path)
    (root / ".claude/skills/run-evals/cases/one/text.md").write_text("nine statements")
    (root / ".claude/skills/run-evals/cases/one/expected.json").write_text('{"planted": []}')
    (root / ".claude/skills/run-evals/scripts/score.py").write_text("easier rules")
    assert fingerprint.check(root, store)["changed"] == [
        ".claude/skills/run-evals/cases/one/expected.json",
        ".claude/skills/run-evals/cases/one/text.md",
        ".claude/skills/run-evals/scripts/score.py",
    ]


def test_blocks_an_added_and_a_removed_file(tmp_path):
    root, store = workspace(tmp_path)
    (root / ".claude/skills/run-evals/cases/one/hint.md").write_text("the answers")
    (root / ".claude/skills/run-evals/cases/one/text.md").unlink()
    found = fingerprint.check(root, store)
    assert found["added"] == [".claude/skills/run-evals/cases/one/hint.md"]
    assert found["removed"] == [".claude/skills/run-evals/cases/one/text.md"]


def test_with_no_fingerprint_file_every_file_counts_as_added(tmp_path):
    root, store = workspace(tmp_path)
    store.unlink()
    assert len(fingerprint.check(root, store)["added"]) == 3
