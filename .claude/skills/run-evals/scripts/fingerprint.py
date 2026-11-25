"""Fingerprint the eval cases and the scorer, so that a change cannot pass unseen.

    uv run python -I .claude/skills/run-evals/scripts/fingerprint.py           check; lists what differs, exit 1 if any
    uv run python -I .claude/skills/run-evals/scripts/fingerprint.py --write   re-fingerprint, on purpose

A fingerprint is a short code computed from a file's contents (SHA-256); any change
to the file changes it. .claude/skills/run-evals/scripts/fingerprints.json holds one for every file under
.claude/skills/run-evals/cases/ and for .claude/skills/run-evals/scripts/score.py. A changed case is a new case: results from
before the change do not carry over to it. Re-fingerprint only deliberately, and
record the reason in the study's decision log.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
STORE = ROOT / ".claude" / "skills" / "run-evals" / "scripts" / "fingerprints.json"
SKIP = {".DS_Store"}


def current(root: Path = ROOT) -> dict[str, str]:
    cases = root / ".claude" / "skills" / "run-evals" / "cases"
    files = [p for p in cases.rglob("*") if p.is_file() and p.name not in SKIP]
    files.append(root / ".claude" / "skills" / "run-evals" / "scripts" / "score.py")
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)
        if p.exists()
    }


def compare(saved: dict[str, str], now: dict[str, str]) -> dict[str, list[str]]:
    return {
        "changed": sorted(k for k in saved.keys() & now.keys() if saved[k] != now[k]),
        "added": sorted(now.keys() - saved.keys()),
        "removed": sorted(saved.keys() - now.keys()),
    }


def check(root: Path = ROOT, store: Path = STORE) -> dict[str, list[str]]:
    saved = json.loads(store.read_text())["files"] if store.exists() else {}
    return compare(saved, current(root))


def write(root: Path = ROOT, store: Path = STORE) -> int:
    files = current(root)
    store.write_text(json.dumps({"files": files}, indent=1) + "\n")
    return len(files)


def main() -> int:
    if "--write" in sys.argv[1:]:
        print(f"{write()} files fingerprinted in {STORE.relative_to(ROOT)}")
        return 0
    found = check()
    for kind, names in found.items():
        for name in names:
            print(f"{kind}: {name}")
    if any(found.values()):
        print(
            "The cases or the scorer differ from their fingerprints. See .claude/skills/run-evals/reference/spec.md."
        )
        return 1
    print("The cases and the scorer match their fingerprints.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
