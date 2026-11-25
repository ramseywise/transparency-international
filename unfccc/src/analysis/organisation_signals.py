"""What the EU delegate list already says about organisations and affiliations, before any lookup.

Nothing here is a classification. The four columns in which the UNFCCC form
asks for the type of organisation and its funding ("Type of home organization",
"Funding source", "Type of funding source", "Alignment ...") are empty for every
row on the Party and Party overflow sheets, so no organisation in scope has a
declared type. What the list does hold:

* **Relation**: how each delegate says they relate to the nominating
  delegation. It is filled for all 3,821 rows. Six answers are the form's own
  options: across the whole file each is used by 300 or more nominating bodies,
  while every other value is used by fewer than 35 (``form_options_in_raw``
  shows this). Other text that delegations typed in is grouped as "Other".
* **Delegation to organisation links**: which organisations each delegation's
  delegates come from (the first layer of the proposed graph, requirement 4.8,
  not yet approved). Built in memory here; nothing is written to
  ``outputs/graph/``.
* **What is missing**: delegates with no usable organisation, and why; names
  still to be settled; organisation type, missing for all.

Charts (``build_charts``), written to ``outputs/charts/`` by ``main``:

* ``relation_by_badge``: the six answers and "Other", Party and overflow badges.
* ``relation_by_delegation``: the same for each of the 28 delegations.

No personal name is read into a table or chart. Run with
``uv run python -m analysis.organisation_signals``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import charts
from analysis.proposal_charts import BADGES, OUTPUT_DIR, SOURCE
from analysis.proposal_numbers import DERIVED, _pair_ids
from cleaning.orgs import is_acronym_like

__all__ = [
    "RELATION_OPTIONS",
    "RELATION_ORDER",
    "DECLARED_COLUMNS",
    "relation_group",
    "relation_by_badge",
    "relation_by_delegation",
    "single_answer_delegations",
    "form_options_in_raw",
    "delegation_org_edges",
    "shared_organisations",
    "delegate_status",
    "missing_information",
    "build_charts",
    "main",
]

RAW_CSV = Path(__file__).resolve().parents[2] / "data" / "raw" / "unfcc-2026.csv"

# The form's six answers, as written in the file, with the short label used in charts.
RELATION_OPTIONS: dict[str, str] = {
    "Paid relationship/contract with the nominating entity": "Paid by the delegation",
    "Paid relationship/contract with an affiliate/member of the nominating entity": "Paid by an affiliate or member",
    "Partner/sponsorship of the nominating entity": "Partner or sponsor",
    "Unpaid advisory capacity": "Unpaid adviser",
    "Guest of the nominating entity": "Guest",
    "Choose not to disclose": "Chose not to disclose",
}
RELATION_ORDER: list[str] = [*RELATION_OPTIONS.values(), charts.OTHER_NAME]

# Form columns that would declare an organisation's type; empty for every Party row.
DECLARED_COLUMNS = (
    "Type of home organization",
    "Funding source",
    "Type of funding source",
    "Alignment with the objective of UNFCCC, the goal and principles of the Kyoto Protocol and the Paris Agreement",
)


def relation_group(relation: pd.Series) -> pd.Series:
    """Short label for each of the six form answers; any other text becomes "Other"."""
    return relation.map(RELATION_OPTIONS).fillna(charts.OTHER_NAME)


def _relation_counts(delegates: pd.DataFrame, by: str) -> pd.DataFrame:
    t = pd.crosstab(delegates[by], relation_group(delegates["relation_clean"]))
    return t.reindex(columns=RELATION_ORDER, fill_value=0)


def relation_by_badge(delegates: pd.DataFrame) -> pd.DataFrame:
    """Delegates by answer, one row per badge (counts)."""
    t = _relation_counts(delegates, "badge_type").reindex(list(BADGES))
    t.index.name = "row"
    return t


def relation_by_delegation(delegates: pd.DataFrame) -> pd.DataFrame:
    """Delegates by answer, one row per delegation (counts), most "paid" first."""
    t = _relation_counts(delegates, "nominated_by_clean")
    paid = t[["Paid by the delegation", "Paid by an affiliate or member"]].sum(axis=1) / t.sum(axis=1)
    t = t.loc[paid.sort_values(ascending=False, kind="stable").index]
    t.index.name = "row"
    return t


def single_answer_delegations(by_delegation: pd.DataFrame) -> pd.Series:
    """Delegations in which every delegate has the same answer, with that answer."""
    one = by_delegation[(by_delegation > 0).sum(axis=1) == 1]
    return one.idxmax(axis=1)


def form_options_in_raw(raw_csv: Path = RAW_CSV) -> pd.DataFrame:
    """Each relation value in the whole raw file: rows, nominating bodies, sheets.

    Read-only. Shows why the six options are treated as the form's own answers.
    """
    raw = pd.read_csv(raw_csv, usecols=["sheet", "Nominated by", "Relation"], dtype=str)
    t = raw.groupby("Relation").agg(
        rows=("sheet", "size"), nominators=("Nominated by", "nunique"), sheets=("sheet", "nunique")
    )
    t["form_option"] = t.index.isin(list(RELATION_OPTIONS))
    return t.sort_values("nominators", ascending=False)


def delegation_org_edges(delegates: pd.DataFrame) -> pd.DataFrame:
    """One row per delegation and organisation, with delegates on each badge (graph layer G2)."""
    named = delegates[delegates["org_id"].notna()]
    t = (
        named.groupby(["nominated_by_clean", "org_id", "badge_type"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=list(BADGES), fill_value=0)
        .reset_index()
    )
    t["delegates"] = t[list(BADGES)].sum(axis=1)
    return t.rename(columns={"nominated_by_clean": "delegation"})


def shared_organisations(orgs: pd.DataFrame) -> pd.DataFrame:
    """Organisations whose delegates come with more than one delegation."""
    n = orgs["countries"].map(len)
    t = orgs.loc[n > 1, ["org_id", "canonical_name", "n_delegates"]].copy()
    t["delegations"] = n[n > 1]
    t["delegation_names"] = orgs.loc[n > 1, "countries"].map(lambda c: ", ".join(sorted(c)))
    return t.sort_values(["delegations", "n_delegates"], ascending=False, kind="stable")


def delegate_status(orgs: pd.DataFrame, delegates: pd.DataFrame, merges: pd.DataFrame) -> pd.Series:
    """For each delegate: what is known about their organisation before any lookup.

    ``no organisation: <reason>`` when the field cannot be used (C4 reasons a to c);
    ``name to settle`` when the organisation is in a similar-name pair awaiting
    review or is named only by an acronym-like string (C4 reason d, possibly);
    ``named`` otherwise. Organisation type is unknown for all three.
    """
    a, b = _pair_ids(orgs, merges)
    acronym = set(orgs.loc[orgs["canonical_name"].map(is_acronym_like), "org_id"])
    unsettled = set(a) | set(b) | acronym
    status = pd.Series("named", index=delegates.index)
    status[delegates["org_id"].isin(unsettled)] = "name to settle"
    none = delegates["org_id"].isna()
    status[none] = "no organisation: " + delegates.loc[none, "no_org_reason"].fillna("unrecorded")
    return status


def missing_information(orgs: pd.DataFrame, delegates: pd.DataFrame, merges: pd.DataFrame) -> pd.DataFrame:
    """Each gap, how many it affects, how the plan would fill it, and how that is measured.

    Status and accuracy are "not run" and "unknown" for every row: no lookup,
    imputation or classification has been done.
    """
    status = delegate_status(orgs, delegates, merges)
    no_org = int(status.str.startswith("no organisation").sum())
    settle = int((status == "name to settle").sum())
    a, b = _pair_ids(orgs, merges)
    acronym = int(orgs["canonical_name"].map(is_acronym_like).sum())
    rows = [
        {
            "gap": "No usable organisation (blank, placeholder, generic, a place, a person or title)",
            "unit": "delegates",
            "affected": no_org,
            "how it would be filled": "Search the person's public pages for the employer; employer and source only, "
            "in a separate inferred column (C6, D5). Needs approval (proposal 6.3).",
            "how accuracy is measured": "Each found employer has a source and quote checked automatically (V1); "
            "those in the expert sample are checked by hand (V4 to V6).",
        },
        {
            "gap": "Similar names awaiting review (possible duplicates)",
            "unit": "organisation pairs",
            "affected": int(len(a)),
            "how it would be filled": "A person decides each pair; decisions are logged, merged ids kept beside the "
            "originals (D8).",
            "how accuracy is measured": "Not a model step: every pair is decided by a person.",
        },
        {
            "gap": "Named only by an acronym-like string",
            "unit": "organisations",
            "affected": acronym,
            "how it would be filled": "Resolved with the delegation's country as context, source recorded (D8); "
            "if several bodies fit, 'unknown, reason d' (C4).",
            "how accuracy is measured": "Part of the evidence record; checked by V1 and in the expert sample.",
        },
        {
            "gap": "Delegates whose organisation is in either of the two rows above",
            "unit": "delegates",
            "affected": settle,
            "how it would be filled": "As above.",
            "how accuracy is measured": "As above.",
        },
        {
            "gap": "Organisation type, sector and fossil fuel link (the research question)",
            "unit": "organisations",
            "affected": int(len(orgs)),
            "how it would be filled": "Rules for obvious government bodies, then approved published lists, then "
            "evidence search and classification against the codebook (C5, C2).",
            "how accuracy is measured": "Second independent run on 10% (V2); known answers from published lists (V3); "
            "expert sample of about 250, blind to the model's label, with accuracy per confidence level and "
            "precision and recall with margins of error (V4 to V6).",
        },
    ]
    t = pd.DataFrame(rows)
    t["status"] = "not run"
    t["accuracy"] = "unknown: not run"
    return t


def signal_numbers(orgs: pd.DataFrame, delegates: pd.DataFrame, raw_csv: Path = RAW_CSV) -> list[dict]:
    """The figures above as rows for ``proposal_v2_numbers.csv`` (section ``organisation_signals``)."""
    sec = "organisation_signals"

    def row(measure, value, note):
        return {"section": sec, "measure": measure, "value": value, "note": note}

    badge = relation_by_badge(delegates).reindex(
        index=["Party", "Party overflow"], columns=["Guest", "Paid by the delegation"], fill_value=0
    ).join(relation_by_badge(delegates).sum(axis=1).rename("total")).fillna(0)
    share = 100 * badge.div(badge["total"].where(badge["total"] > 0), axis=0)
    by_del = relation_by_delegation(delegates)
    shared = shared_organisations(orgs)
    edges = delegation_org_edges(delegates)
    rows = []
    for b, key in (("Party", "party"), ("Party overflow", "party_overflow")):
        for label, short in (("Guest", "guest"), ("Paid by the delegation", "paid_by_delegation")):
            rows.append(row(f"relation_{short}_{key}", int(badge.loc[b, label]), f"delegates, {b} badge"))
            if badge.loc[b, "total"] > 0:
                rows.append(row(f"relation_{short}_share_{key}_pct", round(float(share.loc[b, label]), 1), f"per cent of {b} badge"))
    rows += [
        row("relation_delegations", int(len(by_del)), "delegations"),
        row("relation_delegations_single_answer", int(len(single_answer_delegations(by_del))), "every delegate gives the same relation answer"),
        row("organisations_shared_across_delegations", int(len(shared)), "organisations whose delegates come with more than one delegation"),
        row("delegates_of_shared_organisations", int(shared["n_delegates"].sum()), "their delegates"),
        row("delegation_organisation_links", int(len(edges)), "pairs of delegation and organisation with at least one delegate"),
    ]
    if raw_csv.exists():
        raw = pd.read_csv(raw_csv, usecols=["sheet", "Nominated by", *DECLARED_COLUMNS], dtype=str)
        scope = raw[raw["Nominated by"].isin(set(delegates["Nominated by"])) & raw["sheet"].isin(["Parties", "Party overflow"])]
        filled = int(scope[list(DECLARED_COLUMNS)].notna().any(axis=1).sum())
        rows.append(row("declared_type_rows_checked", int(len(scope)), "in-scope rows of the raw list (Parties and Party overflow sheets)"))
        rows.append(row("declared_type_rows_filled", filled, "in-scope rows with any of the four declared-type columns filled"))
    return rows


def build_charts(delegates: pd.DataFrame) -> dict:
    """The two relation charts, keyed by file name."""
    badge = relation_by_badge(delegates)
    share = badge.div(badge.sum(axis=1), axis=0)
    guest_over = share.loc["Party overflow", "Guest"]
    guest_party = share.loc["Party", "Guest"]
    fig_badge = charts.stacked_bar(
        badge,
        f"Guests are {100 * guest_over:.0f}% of overflow delegates but "
        f"{100 * guest_party:.0f}% of Party delegates",
        SOURCE + " Relation as stated in the list. Other: text typed in instead of one of the form's six answers.",
        order=RELATION_ORDER,
        x_label="Share of delegates",
    )

    by_del = relation_by_delegation(delegates)
    single = single_answer_delegations(by_del)
    labelled = by_del.copy()
    labelled.index = [f"{d} ({n})" for d, n in zip(by_del.index, by_del.sum(axis=1))]
    labelled.index.name = "row"
    fig_del = charts.stacked_bar(
        labelled,
        f"Delegations answer the relation question very differently: in {len(single)} of "
        f"{len(by_del)}, every delegate gives the same answer",
        SOURCE + " Delegates in brackets. Ordered by the share paid by the delegation or an affiliate. "
        "Other: text typed in instead of one of the form's six answers.",
        order=RELATION_ORDER,
        x_label="Share of the delegation's delegates",
    )
    return {"relation_by_badge": fig_badge, "relation_by_delegation": fig_del}


def main(derived: Path = DERIVED, output_dir: Path = OUTPUT_DIR) -> dict:
    """Read the delegate table, write each chart's PNG, SVG and CSV, return the paths."""
    figs = build_charts(pd.read_parquet(derived / "delegates_eu.parquet"))
    return {name: charts.save(fig, output_dir / name) for name, fig in figs.items()}


if __name__ == "__main__":
    for name, paths in main().items():
        print(name, paths["png"])
