#!/usr/bin/env python3
"""Keep the eval cases, the planted answers, the scorer and the fingerprints out of
the reach of an agent under test.

Runs before Edit, Write and NotebookEdit. When the call comes from a subagent
(the hook input then carries "agent_id"), it blocks any change to, or new file in,
the run-evals skill (.claude/skills/run-evals/): cases/, scripts/score.py,
scripts/fingerprint.py, scripts/fingerprints.json, and any expected.json. The main
session is not blocked: it changes a case on purpose and then re-fingerprints
(.claude/skills/run-evals/reference/spec.md).

It does not cover shell commands, and it does not stop a file being read.
"""
import json
import os
import sys

try:
    payload = json.load(sys.stdin)
except ValueError:
    sys.exit(0)

if not payload.get("agent_id"):
    sys.exit(0)

tool_input = payload.get("tool_input") or {}
path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
if not path:
    sys.exit(0)

parts = os.path.abspath(path).split(os.sep)
skill = [i for i in range(1, len(parts)) if parts[i - 1 : i + 1] == ["skills", "run-evals"]]
if not skill:
    sys.exit(0)
inside = parts[skill[-1] + 1 :]  # what follows .../skills/run-evals/

scripts = [["scripts", name] for name in ("score.py", "fingerprint.py", "fingerprints.json")]
protected = (
    inside[:1] == ["cases"]
    or inside in scripts
    or inside[-1:] == ["expected.json"]
)
if protected:
    print(
        f"Blocked: {path} is part of the tests of the assistant (a case, a planted "
        "answer, the scorer or the fingerprints). An agent cannot change it. "
        "Report what you wanted to change instead.",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)
