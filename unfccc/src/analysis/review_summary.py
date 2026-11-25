"""Summary of the two review sheets (notebook 06). PROVISIONAL, 20 organisations each.

Reads the review sheet of the feasibility test and of the codebook test, and
the feasibility run log, and returns counts. No function returns an
organisation's name beside a label; ``browse`` is for the notebook only.

    uv run python -I -m analysis.review_summary     writes outputs/review_sheets_summary_PROVISIONAL.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

STUDY = Path(__file__).resolve().parents[2]
PROCESSED = STUDY / "data" / "processed"
SHEETS = {
    "feasibility test": PROCESSED / "feasibility" / "review_sheet_PROVISIONAL.csv",
    "codebook test": PROCESSED / "draft-codebook" / "codebook-test" / "review_sheet_PROVISIONAL.csv",
}
# the column that holds each headline answer, by sheet
HEADLINE = {
    "feasibility test": {"business": "business", "fossil fuel link": "fossil_link",
                         "state ownership": "state_ownership", "kind": "kind"},
    "codebook test": {"business": "business_status", "fossil fuel link": "fossil_link_kind",
                      "state ownership": "state_ownership", "kind": "kind"},
}
SUFFIXES = ("_rule", "_confidence", "_unknown_reason", "_source_url", "_page", "_quote", "_review")
OUT = STUDY / "outputs" / "review_sheets_summary_PROVISIONAL.csv"
MAX_UNKNOWN = 0.20  # proposal v7, section 8: no more than 20 per cent of the pilot unknown


def load(name: str, sheets: dict = SHEETS) -> pd.DataFrame:
    return pd.read_csv(sheets[name], encoding="utf-8-sig", dtype=str).fillna("")


def attributes(sheet: pd.DataFrame) -> list[str]:
    return [c[: -len("_rule")] for c in sheet.columns if c.endswith("_rule")]


def browse(sheet: pd.DataFrame, attribute: str | None = None, names: bool = False) -> pd.DataFrame:
    """Every label, or one attribute in full. By case code unless ``names`` is set:
    with names the table puts an organisation beside its labels, so it is for
    working review only and is never saved in a tracked notebook or pasted
    elsewhere. Without names the source, page and quote are left out too, since
    they identify the organisation."""
    front = ["case", "countries", "n_delegates", "evidence_status", "status"]
    if names:
        front[1:1] = ["canonical_name", "matched_entity"]
    if attribute is None:
        return sheet[front + attributes(sheet)]
    detail = [s for s in SUFFIXES if names or s not in ("_source_url", "_page", "_quote")]
    return sheet[front + [attribute] + [attribute + s for s in detail]]


def reasons(sheet: pd.DataFrame, names: bool = False) -> pd.DataFrame:
    """Each case's two statuses; with ``names``, also the written reasons, which name the organisation."""
    cols = ["case", "evidence_status", "status"]
    if names:
        cols = ["case", "evidence_status", "evidence_status_reason", "status", "reason"]
    return sheet[cols]


def counts(sheet: pd.DataFrame, column: str) -> pd.Series:
    return sheet[column].replace("", "(blank)").value_counts()


def summary(sheets: dict = SHEETS) -> pd.DataFrame:
    """One row per sheet and measure: n, of how many, and the share."""
    rows = []
    for name in sheets:
        d = load(name, sheets)
        n = len(d)

        def add(measure, k):
            rows.append({"sheet": name, "measure": measure, "n": int(k), "of": n,
                         "share": round(int(k) / n, 2)})

        for v, k in counts(d, "evidence_status").items():
            add(f"evidence status: {v}", k)
        for v, k in counts(d, "status").items():
            add(f"record status: {v}", k)
        for label, col in HEADLINE[name].items():
            add(f"{label}: unknown", (d[col] == "unknown").sum())
            answered = ~d[col].isin(["unknown", ""])
            add(f"{label}: answered", answered.sum())
            # a label worked out by rule from other labels has no source of its own
            add(f"{label}: answered with its own source", (answered & (d[col + "_source_url"] != "")).sum())
            for v, k in counts(d[d[col] == "unknown"], col + "_unknown_reason").items():
                add(f"{label}: unknown because {v}", k)
        add("organisation identified", (d["matched_entity"] != "").sum())
    return pd.DataFrame(rows)


def against_standard(sheets: dict = SHEETS) -> pd.DataFrame:
    """The share unknown for business and for the fossil fuel link, beside the pilot's limit."""
    s = summary(sheets)
    t = s[s.measure.isin(["business: unknown", "fossil fuel link: unknown"])].copy()
    t["limit"] = MAX_UNKNOWN
    t["within limit"] = t.share <= MAX_UNKNOWN
    return t.reset_index(drop=True)


def cost(processed: Path = PROCESSED) -> pd.DataFrame:
    """Tokens and time per step of the feasibility test, in total and per organisation."""
    log = pd.read_csv(processed / "feasibility" / "run_log.csv")
    log["n_cases"] = log.cases.str.count(r"\|") + 1
    t = log.groupby("step").agg(batches=("batch", "count"), organisations=("n_cases", "sum"),
                                tokens=("tokens", "sum"), seconds=("duration_ms", lambda x: x.sum() / 1000))
    t["tokens_per_organisation"] = (t.tokens / t.organisations).round(0).astype(int)
    t["seconds_per_organisation"] = (t.seconds / t.organisations).round(1)
    t["seconds"] = t.seconds.round(0).astype(int)
    return t


def agreement(processed: Path = PROCESSED) -> pd.DataFrame:
    """Agreement between the two classification runs of the feasibility test."""
    return pd.read_csv(processed / "feasibility" / "charts" / "agreement_runs.csv")


def main(out: Path = OUT) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    summary().to_csv(out, index=False)
    return out


if __name__ == "__main__":
    print(main())
