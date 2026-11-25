#!/usr/bin/env python3
"""Block edits to raw data and downloaded sources.

Runs before Edit, Write and NotebookEdit. A file is protected when it already
exists and sits anywhere under a data/raw/ folder: a study's (unfccc/data/raw/)
or a study's literature library's (literature/unfccc/data/raw/pdfs/<topic>/ and pages/<topic>/).
New files and anything outside data/raw/ are allowed.
"""
import json
import os
import sys

try:
    payload = json.load(sys.stdin)
except ValueError:
    sys.exit(0)

tool_input = payload.get("tool_input") or {}
path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
if not path or not os.path.exists(path):
    sys.exit(0)

parts = os.path.abspath(path).split(os.sep)
if ("data", "raw") in zip(parts, parts[1:]):
    print(
        f"Blocked: {path} is a raw file and must not be changed. "
        "Write what is made from it to the data folder beside data/raw/ instead "
        "(a study's data/processed/, a library's data/processed/).",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)
