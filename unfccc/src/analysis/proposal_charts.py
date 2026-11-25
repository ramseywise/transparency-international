"""Descriptive charts of the EU delegate data for section 5 of research proposal v2.

These charts describe the list as it was prepared for classification. They show
no result: nothing here says whether an organisation is a business or linked to
fossil fuels, because nothing has been classified yet.

Three charts, written to ``outputs/charts/`` as PNG, SVG and a CSV of the drawn
numbers (``charts.save``):

* ``delegation_size``: delegates nominated by each of the 28 EU nominating
  bodies, split by badge (Party, Party overflow).
* ``unresolved_names_by_delegation``: for each delegation, the share of its
  delegates (those naming an organisation) whose organisation is in a pair of
  similar names awaiting review or is named only by something like an acronym.
  The sets are the same as in ``proposal_numbers.overlap_numbers``.
* ``organisation_size``: organisations by how many delegates they have.

Every total drawn here is also a figure in ``proposal_v2_numbers.csv``; the
tests check that they agree. No personal name is read into a chart or its CSV.

Run with ``uv run python -m analysis.proposal_charts``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import charts
from analysis.proposal_numbers import DERIVED, _pair_ids
from cleaning.orgs import is_acronym_like

__all__ = [
    "SOURCE",
    "SIZE_BANDS",
    "delegation_size_table",
    "unresolved_share_table",
    "organisation_size_table",
    "build_charts",
    "main",
]

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "charts"

SOURCE = (
    "Source: UNFCCC COP31 participant list, Party and Party overflow badges, "
    "EU and 27 Member States. Registered, not necessarily attended. "
    "Transparency International analysis."
)

# Bands of delegates per organisation: (label, lowest, highest).
SIZE_BANDS = (
    ("1 delegate", 1, 1),
    ("2 delegates", 2, 2),
    ("3 to 5 delegates", 3, 5),
    ("6 to 10 delegates", 6, 10),
    ("11 to 25 delegates", 11, 25),
    ("26 or more delegates", 26, None),
)

BADGES = ("Party", "Party overflow")


def delegation_size_table(delegates: pd.DataFrame) -> pd.DataFrame:
    """Delegates per nominating body and badge, largest delegation first."""
    t = (
        delegates.groupby(["nominated_by_clean", "badge_type"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=list(BADGES), fill_value=0)
    )
    order = t.sum(axis=1).sort_values(ascending=False, kind="stable").index
    t = t.loc[order]
    t.index.name = "row"
    return t


def unresolved_share_table(
    orgs: pd.DataFrame, delegates: pd.DataFrame, merges: pd.DataFrame
) -> pd.DataFrame:
    """Per delegation: delegates naming an organisation, how many are unresolved, the share."""
    a, b = _pair_ids(orgs, merges)
    acronym = set(orgs.loc[orgs["canonical_name"].map(is_acronym_like), "org_id"])
    either = set(a) | set(b) | acronym
    named = delegates[delegates["org_id"].notna()]
    total = named.groupby("nominated_by_clean").size()
    hit = named[named["org_id"].isin(either)].groupby("nominated_by_clean").size()
    t = pd.DataFrame({"named": total, "unresolved": hit.reindex(total.index, fill_value=0)})
    t["share"] = t["unresolved"] / t["named"]
    t.index.name = "delegation"
    return t.sort_values("share", ascending=False, kind="stable")


def organisation_size_table(orgs: pd.DataFrame) -> pd.DataFrame:
    """Organisations and their delegates in each band of delegates per organisation."""
    rows = []
    n = orgs["n_delegates"]
    for label, lo, hi in SIZE_BANDS:
        mask = (n >= lo) & (n <= hi) if hi is not None else (n >= lo)
        rows.append({"band": label, "organisations": int(mask.sum()), "delegates": int(n[mask].sum())})
    t = pd.DataFrame(rows)
    if t["organisations"].sum() != len(orgs):
        raise ValueError("some organisations fall outside every band")
    return t


def build_charts(orgs: pd.DataFrame, delegates: pd.DataFrame, merges: pd.DataFrame) -> dict:
    """The three figures, keyed by file name."""
    size = delegation_size_table(delegates)
    total = int(size.to_numpy().sum())
    overflow = int(size["Party overflow"].sum())
    totals = size.sum(axis=1)
    fig_size = charts.stacked_bar(
        size,
        f"EU delegations range from {int(totals.min())} to {int(totals.max())} delegates; "
        f"{round(100 * overflow / total)}% of the {total:,} hold overflow badges",
        SOURCE,
        order=list(BADGES),
        share=False,
        x_label="Delegates registered",
    )

    share = unresolved_share_table(orgs, delegates, merges)
    labelled = pd.DataFrame(
        {
            "category": [f"{d} ({n})" for d, n in zip(share.index, share["named"])],
            "value": share["share"].to_numpy(),
        }
    )
    overall = share["unresolved"].sum() / share["named"].sum()
    fig_share = charts.bar_chart(
        labelled,
        f"Organisation names still to be settled: {100 * overall:.0f}% of delegates overall, "
        f"up to {100 * share['share'].max():.0f}% in one delegation",
        SOURCE + " Delegates naming an organisation in brackets. Unsettled: in a similar-name "
        "pair awaiting review, or named only by an acronym-like string.",
        share=True,
        sort=False,
        x_label="Share of the delegation's delegates",
    )

    bands = organisation_size_table(orgs)
    single = int(bands.loc[bands["band"] == SIZE_BANDS[0][0], "organisations"].iloc[0])
    fig_orgs = charts.bar_chart(
        bands[["band", "organisations"]],
        f"{single:,} of the {len(orgs):,} organisations have a single delegate",
        SOURCE,
        sort=False,
        x_label="Number of organisations",
    )
    return {
        "delegation_size": fig_size,
        "unresolved_names_by_delegation": fig_share,
        "organisation_size": fig_orgs,
    }


def main(derived: Path = DERIVED, output_dir: Path = OUTPUT_DIR) -> dict:
    """Read the cleaned tables, write each chart's PNG, SVG and CSV, return the paths."""
    figs = build_charts(
        pd.read_parquet(derived / "organisations_eu.parquet"),
        pd.read_parquet(derived / "delegates_eu.parquet"),
        pd.read_csv(derived / "proposed_merges_eu.csv"),
    )
    return {name: charts.save(fig, output_dir / name) for name, fig in figs.items()}


if __name__ == "__main__":
    for name, paths in main().items():
        print(name, paths["png"])
