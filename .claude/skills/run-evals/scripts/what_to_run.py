"""Which eval cases a change needs, and whether they need three runs. Costs nothing.

    uv run python -I .claude/skills/run-evals/scripts/what_to_run.py                       # what changed, what to run
    uv run python -I .claude/skills/run-evals/scripts/what_to_run.py --save .claude/skills/run-evals/runs/<date>/run1

It compares the files that shape the agents' answers (agent files, skills, CLAUDE.md,
the prompts of the organisation look-up, the literature chunk selection) and the
agents' models with the last tested point. That point is `.claude/skills/run-evals/last-tested.json`,
written by `--save` after a run passed; before the first save it is the newest
`run-record.json`, which holds only the agent files, two instruction files and the
cases. A file the saved point does not hold counts as changed, so nothing new goes
untested.

What a change touches:

    an agent file or its model       that agent's cases
    CLAUDE.md, run-evals, the cases  every case, three runs
    classify skill, lookup prompts   evidence-finder, org-classifier
    find-sources, literature-review  source-reader, citation-checker
    check-work skill                 citation-checker, numbers-checker, methods-reviewer
    chunk selection                  source-reader
    any other skill                  no agent case (pytest checks the skill's wiring)

Three runs (E3) are needed for a model change, a change to CLAUDE.md or to the
cases, or before the full classification run (`--before-full-run`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import AGENTS, CASE_AGENT, ROOT, _sha, agent_model, fixed_parts  # noqa: E402

SAVED = ROOT / ".claude" / "skills" / "run-evals" / "last-tested.json"
ALL = "all"
# The cases of each agent, under the names the scorer and the run-evals skill use.
CASES = {a: [a, *(c for c, of in CASE_AGENT.items() if of == a)] for a in AGENTS}
SKILL_CASES = {
    "run-evals": ALL,
    "classify": ["evidence-finder", "org-classifier"],
    "find-sources": ["source-reader", "citation-checker"],
    "literature-review": ["source-reader", "citation-checker"],
    "check-work": ["citation-checker", "numbers-checker", "methods-reviewer"],
}
EXTRA = {
    "literature/src/rag/chunks.py": ["source-reader"],
}
PROMPTS = "unfccc/src/lookup/prompts"


def tracked_files() -> list[Path]:
    files = sorted((ROOT / ".claude" / "agents").glob("*.md"))
    files += sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    files += [ROOT / "CLAUDE.md"]
    files += sorted(p for p in (ROOT / PROMPTS).glob("*") if p.is_file())
    files += [ROOT / p for p in EXTRA if (ROOT / p).exists()]
    return files


def current() -> dict:
    return {
        "files": {p.relative_to(ROOT).as_posix(): _sha(p) for p in tracked_files()},
        "models": {a: agent_model(a) for a in AGENTS},
        "cases_and_scorer": fixed_parts()["cases_and_scorer"],
    }


def newest_run_record() -> Path | None:
    recs = sorted((ROOT / ".claude" / "skills" / "run-evals" / "runs").glob("**/run-record.json"))
    return max(recs, key=lambda p: (json.loads(p.read_text()).get("date", ""), str(p)),
               default=None)


def baseline() -> tuple[dict | None, str]:
    if SAVED.exists():
        saved = json.loads(SAVED.read_text())
        return saved, f"last tested point ({saved.get('run', '?')}, saved {saved.get('saved')})"
    rec = newest_run_record()
    if rec is None:
        return None, "no tested run"
    r = json.loads(rec.read_text())
    base = {"files": r.get("instructions", {}), "models": r.get("models", {}),
            "cases_and_scorer": r.get("cases_and_scorer")}
    return base, f"run record {rec.relative_to(ROOT).as_posix()} (agent files and CLAUDE.md only)"


def cases_for(path: str) -> str | list[str]:
    if path == "CLAUDE.md":
        return ALL
    if path.startswith(".claude/agents/"):
        agent = Path(path).stem
        return CASES.get(agent, [])
    if path.startswith(".claude/skills/"):
        return SKILL_CASES.get(Path(path).parent.name, [])
    if path.startswith(PROMPTS + "/"):
        return SKILL_CASES["classify"]
    return EXTRA.get(path, [])


def plan(now: dict, base: dict | None, before_full_run: bool = False) -> dict:
    """What changed since `base`, which cases that needs and how many runs."""
    if base is None:
        return {"changed": ["(nothing tested yet)"], "cases": ALL, "runs": 3,
                "why_three": ["no run has been tested yet"]}
    old = base.get("files", {})
    changed = sorted(p for p, h in now["files"].items() if old.get(p) != h)
    removed = sorted(p for p in old if p not in now["files"])
    models = sorted(a for a, m in now["models"].items()
                    if base.get("models", {}).get(a) not in (None, m))
    cases_changed = base.get("cases_and_scorer") != now["cases_and_scorer"]

    need: set[str] = set()
    every = False
    for p in changed + removed:
        c = cases_for(p)
        if c == ALL:
            every = True
        else:
            need.update(c)
    for a in models:
        need.update(CASES[a])
    if cases_changed:
        every = True

    why_three = []
    if models:
        why_three.append("model changed: " + ", ".join(
            f"{a} {base['models'][a]} -> {now['models'][a]}" for a in models))
    if "CLAUDE.md" in changed:
        why_three.append("CLAUDE.md changed")
    if cases_changed:
        why_three.append("the cases or the scorer changed")
    if before_full_run:
        why_three.append("before the full classification run")
        every = True

    all_cases = [c for a in AGENTS for c in CASES[a]]
    return {
        "changed": changed + [f"{p} (removed)" for p in removed]
        + [f"model of {a}" for a in models]
        + (["the cases or the scorer"] if cases_changed else []),
        "cases": ALL if every else [c for c in all_cases if c in need],
        "runs": 3 if why_three else (1 if every or need else 0),
        "why_three": why_three,
    }


def save(run: str) -> Path:
    import datetime as dt

    folder = ROOT / run if not Path(run).is_absolute() else Path(run)
    if not (folder / "run-record.json").exists():
        raise SystemExit(f"{run} has no run-record.json: save only a scored run.")
    SAVED.write_text(json.dumps({"run": run, "saved": dt.date.today().isoformat()} | current(),
                                indent=1) + "\n")
    return SAVED


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--save", metavar="RUN_FOLDER", help="mark the current files as tested")
    ap.add_argument("--before-full-run", action="store_true",
                    help="the full classification run is next: all cases, three runs")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.save:
        print(f"Saved the tested point to {save(a.save).relative_to(ROOT)}.")
        return 0
    base, label = baseline()
    p = plan(current(), base, a.before_full_run)
    if a.json:
        print(json.dumps(p | {"compared_with": label}, indent=1))
        return 0
    print(f"Compared with: {label}")
    if not p["runs"]:
        print("Nothing that the agent cases test has changed. No eval run is needed; "
              "pytest still runs.")
        return 0
    print("Changed:\n  " + "\n  ".join(p["changed"]))
    cases = "all cases" if p["cases"] == ALL else ", ".join(p["cases"])
    print(f"Run: {cases}")
    print(f"Runs: {p['runs']}" + (f" ({'; '.join(p['why_three'])})" if p["why_three"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
