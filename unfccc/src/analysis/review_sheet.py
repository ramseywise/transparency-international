"""The review sheet: one row per organisation, for a person to confirm or correct.

Columns, left to right:

* the organisation as it is on the list (the original columns of the organisation table);
* what was inferred: the overall status and reason, then for each attribute its value,
  confidence, reason for "unknown", source address, place in the source and quote;
* empty columns for the reviewer: beside each attribute a ``*_review`` column (write "ok",
  or the corrected value), then ``review_notes``, ``reviewer`` and ``review_date``.

Inferred values sit beside the original, never over it (rule 5). The reviewer's columns are
never filled by code. The sheet names organisations beside their labels: it is a working
file for review and stays in ``data/processed/``; it is not an output for publication.

Run for the feasibility test (provisional, 20 organisations):
    uv run python -I -m analysis.review_sheet

The review workbook is the same sheet made simple, as an Excel file: the headline answers
only, the column groups in colour (given, counted, cleaned, found and inferred, your review),
with the full sheet and a guide to every column on further tabs.
    uv run python -I -m analysis.review_sheet --workbook

The blind sheet is a different thing: for the expert who labels the pilot without seeing
the model's answers (proposal 6.5). It holds the organisation as listed and empty columns,
one per codebook field, and nothing the model found or decided.
    uv run python -I -m analysis.review_sheet --blind
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

STUDY = Path(__file__).resolve().parents[2]
DERIVED = STUDY / "data" / "processed"  # the folder was renamed from derived, 2026-11-25

ORIGINAL = ["org_id", "canonical_name", "raw_spellings", "countries",
            "n_delegates", "n_delegates_party", "n_delegates_party_overflow"]
FIELDS = ["confidence", "unknown_reason", "source_url", "page", "quote"]
REVIEW_END = ["review_identity", "review_notes", "reviewer", "review_date"]
BLIND_END = ["expert_entity", "expert_source", "expert_notes", "expert_minutes", "reviewer",
             "review_date"]


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


# The column groups: where each column comes from, and what a reviewer does with it.
GROUPS = {
    "reference": ("Reference", "D9D9D9", "A code we added so that rows can be found again.",
                  "nothing to approve"),
    "given": ("From the Excel (given)", "BDD7EE",
              "The organisation exactly as written on the participant list.", "nothing to approve"),
    "counted": ("Counted from the Excel", "DDEBF7",
                "Counted from the list with no judgement: delegations and badges.",
                "nothing to approve"),
    "cleaned": ("Cleaned by us", "FFE699",
                "One name chosen for spellings we took to be the same organisation.",
                "the merges of spellings need approval"),
    "inferred": ("Found and inferred (to confirm)", "F8CBAD",
                 "Not in the Excel. Found on the web and decided by the codebook's rules, "
                 "each with confidence, reason and source.",
                 "confirm or change each value; the rules themselves are approved in the codebook"),
    "review": ("Your review (fill in)", "C6E0B4", "Empty. Only the reviewer writes here.",
               "this is where the approval is given"),
}
# The answers the two research questions need, by the names used in either test.
HEADLINES = [("business", ("business_status", "business")), ("sector", ("sector",)),
             ("state_ownership", ("state_ownership",)),
             ("fossil_link", ("fossil_link_kind", "fossil_link"))]
TIERS = ("tier_1", "tier_2A", "tier_2B_O", "tier_2B_S", "tier_3")
HOW_TO = [
    "PROVISIONAL test of 20 organisations. Nothing here is a result of the study.",
    "",
    "1. Work on the tab 'Review'. One row is one organisation.",
    "2. Blue columns are from the participant list. Yellow is the name we cleaned.",
    "3. Orange columns are what was found and inferred: the answer, how sure, why, and the source.",
    "4. In each green '_review' column write ok, or the value it should be.",
    "   'unknown' is a valid answer: write ok if you would also not know from these sources.",
    "5. Put anything else in review_notes: a wrong organisation matched, a better source, a rule that seems wrong.",
    "6. Add your name and the date. Send the file back; nothing is changed until your answers are read in.",
    "",
    "The tab 'All detail' has every attribute with its rule, page and quote.",
    "The tab 'Columns' says where each column comes from and what needs approval.",
]


def group(column: str) -> str:
    """The group a column of the sheet belongs to."""
    if column.endswith("_review") or column in REVIEW_END:
        return "review"
    if column in ("case", "org_id"):
        return "reference"
    if column == "raw_spellings":
        return "given"
    if column == "canonical_name":
        return "cleaned"
    if column == "countries" or column.startswith("n_delegates"):
        return "counted"
    return "inferred"


def column_guide(columns) -> pd.DataFrame:
    """One line per column: its group, what the group is, and what needs approval."""
    return pd.DataFrame([{"column": c, "group": GROUPS[group(c)][0],
                          "what it is": GROUPS[group(c)][2],
                          "what needs approval": GROUPS[group(c)][3]} for c in columns])


def simple(sheet: pd.DataFrame) -> pd.DataFrame:
    """The headline answers only: value, confidence, reason and source, and a review column.

    Values are copied from the full sheet, never recomputed. The tiers are shown side by
    side in one cell where the sheet holds one column per tier.
    """
    out = sheet[["case"] + [c for c in ORIGINAL if c != "org_id"] + ["matched_entity"]].copy()
    for name, candidates in HEADLINES:
        col = next((c for c in candidates if c in sheet), None)
        if col is None:
            continue
        out[name] = sheet[col]
        out[f"{name}_confidence"] = sheet[f"{col}_confidence"]
        out[f"{name}_reason"] = sheet[f"{col}_unknown_reason"]
        out[f"{name}_source"] = sheet[f"{col}_source_url"]
        out[f"{name}_review"] = ""
    if "tier" in sheet:
        out["tier"] = sheet["tier"]
    else:
        tiers = [c for c in TIERS if c in sheet]
        out["tier"] = [" | ".join(f"{c[5:]}: {r[c]}" for c in tiers) for _, r in sheet.iterrows()]
    out["tier_review"] = ""
    out["why"] = sheet["reason"]
    for c in REVIEW_END:
        out[c] = ""
    return out


def workbook(sheet: pd.DataFrame, path: Path) -> Path:
    """The review workbook: how to review, the simple sheet in colour, all detail, the guide."""
    from openpyxl.styles import Alignment, Font, PatternFill

    review = simple(sheet)
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        pd.DataFrame({"How to review": HOW_TO}).to_excel(xl, sheet_name="How to review", index=False)
        review.to_excel(xl, sheet_name="Review", index=False, startrow=1)
        sheet.to_excel(xl, sheet_name="All detail", index=False, startrow=1)
        guide = pd.concat([column_guide(review.columns).assign(tab="Review"),
                           column_guide(sheet.columns).assign(tab="All detail")])
        guide.to_excel(xl, sheet_name="Columns", index=False)
        xl.sheets["How to review"].column_dimensions["A"].width = 110
        for tab, frame in (("Review", review), ("All detail", sheet)):
            ws = xl.sheets[tab]
            for i, col in enumerate(frame.columns, start=1):
                label, colour, _, _ = GROUPS[group(col)]
                fill = PatternFill("solid", start_color=colour)
                top = ws.cell(row=1, column=i, value=label)
                for cell in (top, ws.cell(row=2, column=i)):
                    cell.fill, cell.font = fill, Font(bold=True)
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
                ws.column_dimensions[top.column_letter].width = 22
            ws.freeze_panes = "C3"
    return path


def workbook_main(derived: Path = DERIVED) -> list[Path]:
    """A workbook beside each of the two provisional review sheets."""
    made = []
    for folder in (derived / "feasibility", derived / "draft-codebook" / "codebook-test"):
        sheet = pd.read_csv(folder / "review_sheet_PROVISIONAL.csv", encoding="utf-8-sig",
                            dtype=str).fillna("")
        made.append(workbook(sheet, folder / "review_workbook_PROVISIONAL.xlsx"))
        print(f"{made[-1]}: {len(sheet)} organisations")
    return made


def expert_fields(fields: dict) -> dict:
    """The codebook fields an expert fills in: those with a real choice of values.

    Left out: the confidence fields and the class of an unknown (set by rule from the
    evidence, not judged), and a field whose only allowed value is "unknown".
    """
    return {f: v for f, v in fields.items()
            if not f.endswith("_confidence") and f != "unknown_class" and len(v) > 1}


def blind(orgs: pd.DataFrame, cases: pd.DataFrame, fields: dict) -> pd.DataFrame:
    """The blind sheet: the organisation as listed, and one empty column per field.

    Built from the organisation table and the draw only. It never reads an evidence
    record or a classification, so nothing of the model's can reach the expert.
    """
    by_id = orgs.set_index("org_id")
    rows = []
    for case, org_id in zip(cases["case"], cases["org_id"]):
        org = {"org_id": org_id, **by_id.loc[org_id].to_dict()}
        out = {"case": case, **{c: _text(org.get(c)) for c in ORIGINAL}}
        out.update({f"{f}_expert": "" for f in expert_fields(fields)})
        out.update({c: "" for c in BLIND_END})
        rows.append(out)
    return pd.DataFrame(rows).fillna("")


def blind_main(derived: Path = DERIVED, codebook_path: Path = STUDY / "docs" / "codebook.md") -> Path:
    """The blind sheet for the pilot draw, with the allowed values in a second file."""
    from lookup import codebook

    cb = codebook.load(codebook_path, draft=True)
    base = derived / "draft-codebook"
    fields = expert_fields(cb.labels["fields"])
    sheet = blind(pd.read_parquet(derived / "organisations_eu.parquet"),
                  pd.read_csv(base / "pilot_draw.csv"), cb.labels["fields"])
    out = base / "pilot_blind_sheet_DRAFT.csv"
    sheet.to_csv(out, index=False, encoding="utf-8-sig")
    pd.DataFrame([{"column": f"{f}_expert", "allowed_values": " | ".join(v),
                   "codebook_version": cb.version} for f, v in fields.items()]
                 ).to_csv(base / "pilot_blind_sheet_values_DRAFT.csv", index=False,
                          encoding="utf-8-sig")
    print(f"{out}: {len(sheet)} organisations, {sheet.shape[1]} columns, codebook {cb.version}")
    return out


if __name__ == "__main__":
    import sys
    if "--workbook" in sys.argv:
        workbook_main()
    elif "--blind" in sys.argv:
        blind_main()
    elif "--codebook-test" in sys.argv:
        codebook_test_main()
    else:
        main()
