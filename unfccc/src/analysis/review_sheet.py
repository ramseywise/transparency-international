"""The review sheet: one row per organisation, for a person to confirm or correct.

Columns, left to right:

* the organisation as it is on the list (the original columns of the organisation table);
* what was inferred: the overall status and reason, then for each attribute its value,
  confidence, reason for "unknown", source address, place in the source and quote;
* empty columns for the reviewer: beside each attribute a ``*_review`` column (write "ok",
  or the corrected value), then ``review_notes``, ``reviewer`` and ``review_date``.

Inferred values sit beside the original, never over it (rule 5). The reviewer's columns are
never filled by code. The sheet names organisations beside their labels: it is a working
file for review and stays in ``data/derived/``; it is not an output for publication.

Run for the feasibility test (provisional, 20 organisations):
    uv run python -I -m analysis.review_sheet
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

STUDY = Path(__file__).resolve().parents[2]
DERIVED = STUDY / "data" / "derived"

ORIGINAL = ["org_id", "canonical_name", "raw_spellings", "countries",
            "n_delegates", "n_delegates_party", "n_delegates_party_overflow"]
FIELDS = ["confidence", "unknown_reason", "source_url", "page", "quote"]
REVIEW_END = ["review_identity", "review_notes", "reviewer", "review_date"]


def _text(v) -> str:
    """A cell as text: lists joined with ' | ', nothing as an empty cell."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (list, tuple)) or hasattr(v, "tolist"):
        return " | ".join(str(x) for x in list(v))
    return str(v)


def _name(attr: str) -> str:
    """R4_business -> business."""
    head, _, tail = attr.partition("_")
    return tail if head[:1] == "R" and head[1:].isdigit() and tail else attr


def row(org: dict, evidence: dict, classified: dict) -> dict:
    """One line of the sheet from the list entry, the evidence record and the classification."""
    out = {c: _text(org.get(c)) for c in ORIGINAL}
    out["matched_entity"] = _text(evidence.get("matched_entity"))
    out["evidence_status"] = _text(evidence.get("status"))
    out["evidence_status_reason"] = _text(evidence.get("status_reason"))
    out["status"] = _text(classified.get("status"))
    out["reason"] = _text(classified.get("reasoning"))
    for attr, val in classified.get("attributes", {}).items():
        name = _name(attr)
        out[name] = _text(val.get("label", val.get("labels")))
        out[f"{name}_rule"] = _text(val.get("rule"))
        for f in FIELDS:
            out[f"{name}_{f}"] = _text(val.get(f))
        out[f"{name}_review"] = ""
    for c in REVIEW_END:
        out[c] = ""
    return out


def build(orgs: pd.DataFrame, cases: pd.DataFrame, evidence_dir: Path,
          classified_dir: Path) -> pd.DataFrame:
    """The sheet for the cases given. ``cases`` has the columns ``case`` and ``org_id``."""
    by_id = orgs.set_index("org_id")
    rows = []
    for case, org_id in zip(cases["case"], cases["org_id"]):
        org = {"org_id": org_id, **by_id.loc[org_id].to_dict()}
        ev = json.loads((evidence_dir / f"{case}.json").read_text())
        cl = json.loads((classified_dir / f"{case}.json").read_text())
        rows.append({"case": case, **row(org, ev, cl)})
    return pd.DataFrame(rows).fillna("")


def main(derived: Path = DERIVED) -> Path:
    feas = derived / "feasibility"
    sheet = build(pd.read_parquet(derived / "organisations_eu.parquet"),
                  pd.read_csv(feas / "sample.csv"), feas / "evidence",
                  feas / "classification_run1")
    out = feas / "review_sheet_PROVISIONAL.csv"
    sheet.to_csv(out, index=False, encoding="utf-8-sig")  # opens cleanly in Excel
    print(f"{out}: {len(sheet)} organisations, {sheet.shape[1]} columns")
    return out


def codebook_test_main(derived: Path = DERIVED) -> Path:
    """The same sheet for the 20 organisations the draft codebook was tested on."""
    base = derived / "draft-codebook"
    test = base / "codebook-test"
    sheet = build(pd.read_parquet(derived / "organisations_eu.parquet"),
                  pd.read_csv(base / "codebook_test_draw.csv"), test / "evidence",
                  test / "classified")
    out = test / "review_sheet_PROVISIONAL.csv"
    sheet.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"{out}: {len(sheet)} organisations, {sheet.shape[1]} columns")
    return out


if __name__ == "__main__":
    import sys
    codebook_test_main() if "--codebook-test" in sys.argv else main()
