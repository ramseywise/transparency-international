"""The eval trigger picks the right cases for a change, and the number of runs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import what_to_run as w  # noqa: E402


def base() -> dict:
    now = w.current()
    return {"files": dict(now["files"]), "models": dict(now["models"]),
            "cases_and_scorer": now["cases_and_scorer"]}


def changed(**files) -> dict:
    now = base()
    now["files"].update(files)
    return now


def test_nothing_changed_needs_no_run():
    p = w.plan(w.current(), base())
    assert p["runs"] == 0 and p["cases"] == []


def test_agent_file_runs_that_agents_cases_once():
    p = w.plan(changed(**{".claude/agents/source-reader.md": "x"}), base())
    assert p["cases"] == ["source-reader", "source-reader-chunks"] and p["runs"] == 1


def test_methods_reviewer_runs_all_three_of_its_cases():
    p = w.plan(changed(**{".claude/agents/methods-reviewer.md": "x"}), base())
    assert p["cases"] == ["methods-reviewer", "methods-reviewer-proposal", "methods-reviewer-v1"]


def test_claude_md_runs_everything_three_times():
    p = w.plan(changed(**{"CLAUDE.md": "x"}), base())
    assert p["cases"] == w.ALL and p["runs"] == 3


def test_model_change_needs_three_runs_of_that_agent():
    now = base()
    old = base()
    was = now["models"]["org-classifier"]
    old["models"]["org-classifier"] = "opus" if was != "opus" else "haiku"
    p = w.plan(now, old)
    assert p["cases"] == ["org-classifier"] and p["runs"] == 3


def test_changed_cases_run_everything_three_times():
    old = base()
    old["cases_and_scorer"] = "old"
    p = w.plan(w.current(), old)
    assert p["cases"] == w.ALL and p["runs"] == 3


def test_skill_and_prompt_and_chunks_map_to_their_agents():
    assert w.cases_for(".claude/skills/classify/SKILL.md") == ["evidence-finder", "org-classifier"]
    assert w.cases_for(f"{w.PROMPTS}/classify.md") == ["evidence-finder", "org-classifier"]
    assert w.cases_for("literature/src/rag/chunks.py") == ["source-reader"]
    assert w.cases_for(".claude/skills/house-style/SKILL.md") == []


def test_file_missing_from_baseline_counts_as_changed():
    old = base()
    del old["files"]["CLAUDE.md"]
    assert "CLAUDE.md" in w.plan(w.current(), old)["changed"]


def test_before_full_run_forces_all_cases_three_times():
    p = w.plan(w.current(), base(), before_full_run=True)
    assert p["cases"] == w.ALL and p["runs"] == 3


def test_no_baseline_runs_everything():
    assert w.plan(w.current(), None)["cases"] == w.ALL


def test_every_agent_with_cases_is_known_to_the_scorer():
    for agent, cases in w.CASES.items():
        assert agent in w.AGENTS
        assert all(w.CASE_AGENT.get(c, c) == agent for c in cases)
