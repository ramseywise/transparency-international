"""Read the codebook, and the machine-readable list of labels inside it.

The codebook is written for people. For the script it also holds one fenced JSON
block, under the heading "Labels for the script", that lists what code needs to
check a result without reading the prose:

    {"version": "1.0",
     "label_field": "category",
     "fields": {"category": ["...", "unknown"], "sector": ["...", null]},
     "rules": ["R1", "R2"],
     "negative_labels": ["no_fossil_link"],
     "confidence_by_level": {"1": {"confident": "high", "uncertain": "medium"}},
     "status_by_confidence": {"high": "confident", "medium": "uncertain", "low": "uncertain"},
     "unknown_reasons": ["could be several entities", "nothing found", ...]}

`confidence_by_level` maps the level of the evidence item relied on (1 is the highest)
and the status of the evidence record to a confidence. A pair that is not listed has
no allowed confidence, and a result that uses it fails the check.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

REQUIRED = ("version", "label_field", "fields", "rules", "negative_labels",
            "confidence_by_level", "status_by_confidence", "unknown_reasons")
# Reasons the script itself sets, whatever the codebook lists.
SCRIPT_REASONS = {"lookup failed", "not covered by the codebook", "nothing found",
                  "could be several entities"}


@dataclass
class Codebook:
    path: Path
    text: str
    labels: dict

    @property
    def version(self) -> str:
        return str(self.labels["version"])

    @property
    def label_field(self) -> str:
        return self.labels["label_field"]

    def allowed(self, field: str) -> list:
        return self.labels["fields"][field]

    def confidence(self, level: int, evidence_status: str) -> str | None:
        return self.labels["confidence_by_level"].get(str(level), {}).get(evidence_status)

    def status_for(self, confidence: str) -> str | None:
        return self.labels["status_by_confidence"].get(confidence)

    @property
    def unknown_reasons(self) -> set[str]:
        return set(self.labels["unknown_reasons"]) | SCRIPT_REASONS


def labels_block(text: str) -> dict:
    """The JSON block that has a `fields` key. Raises if there is none, or it is incomplete."""
    for block in re.findall(r"```json\s*\n(.*?)\n```", text, flags=re.S):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "fields" in data:
            missing = [k for k in REQUIRED if k not in data]
            if missing:
                raise ValueError(f"The codebook's labels block lacks: {', '.join(missing)}.")
            if data["label_field"] not in data["fields"]:
                raise ValueError("The labels block's label_field is not one of its fields.")
            if "unknown" not in data["fields"][data["label_field"]]:
                raise ValueError("The label field must allow 'unknown'.")
            return data
    raise ValueError("The codebook has no labels block (a ```json block with a 'fields' key, "
                     "under 'Labels for the script'). The codebook skill says how to write it.")


def major(version: str) -> int:
    m = re.match(r"\s*(\d+)", str(version))
    return int(m.group(1)) if m else 0


def load(path: Path | str, draft: bool = False) -> Codebook:
    """The codebook at `path`. A version below 1.0 is a draft, refused unless `draft`."""
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"No codebook at {path}. The codebook must be written and approved "
                         "before classification (/codebook).")
    text = path.read_text()
    labels = labels_block(text)
    if major(labels["version"]) < 1 and not draft:
        raise SystemExit(f"The codebook is version {labels['version']}, a draft. Classification "
                         "needs an approved version 1.0 or later. Use --draft only for the "
                         "codebook's own test on 20 organisations; its results go to a "
                         "separate folder.")
    return Codebook(path=path, text=text, labels=labels)
