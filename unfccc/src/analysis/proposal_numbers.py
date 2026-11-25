"""The figures behind research proposal v2, recomputed from the cleaned tables.

The proposal may only print numbers that come from a file in ``outputs/``. This
module writes that file, ``outputs/proposal_v2_numbers.csv``. Nothing here uses
a language model and nothing is typed in by hand: each figure is counted from
the cleaned tables in ``data/processed/`` or worked out with the sampling and
statistics code that the validation will use later.

Five groups of figures:

* ``merges``: the pairs of organisation names that look alike and that a person
  still has to accept or reject. How many organisations and delegates stand
  behind them, each organisation counted once even if it appears in several
  pairs, and how far the number of organisations could fall if every pair were
  accepted.
* ``acronyms``: organisations written only as a short run of capitals. The rule
  is applied again here to the organisation names, and compared with the flag
  stored by the cleaning step.
* ``duplicates``: people listed on both the Party sheet and the Party overflow
  sheet for the same nominating country, and people listed twice on one sheet.
  Counted again from the delegate table.
* ``overlap``: how far the two open questions about names (pairs that look
  alike, and names that are only an acronym) concern the same organisations,
  and how they spread across the nominating delegations.
* ``sample_design``: arithmetic for the expert's checking sample. No
  organisation has been classified, so the size of each group ("stratum") is
  not known. The figures are therefore given as a function of how many
  organisations are checked per group, never for an assumed population.

Terms:

* stratum: a group of organisations the sample is drawn from separately.
* margin of error: half the width of the 95% range around a measured share.
  "Worst case" means the true share is 50%, which gives the widest range.
* ceiling: the margin when the group is very large compared with the number
  checked. A small group that is checked almost completely has a smaller
  margin; a group checked completely has none.
* Wilson interval: the 95% range around an observed share such as "27 correct
  out of 30". It is the interval the validation code reports.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from analysis.sampling import expected_margin_of_error
from analysis.stats import wilson_interval
from cleaning.orgs import is_acronym_like

__all__ = [
    "V1_CATEGORIES",
    "V1_CONFIDENCE_LEVELS",
    "V1_MIN_PER_GROUP",
    "V1_SAMPLE_SIZE",
    "V2_STRATA",
    "V2_CENSUS_STRATA",
    "SIZES",
    "merge_numbers",
    "acronym_numbers",
    "duplicate_numbers",
    "overlap_numbers",
    "sample_design_numbers",
    "build_table",
    "main",
]

# Draft v1, section 6.5: groups defined by category and confidence level.
V1_CATEGORIES = 5
V1_CONFIDENCE_LEVELS = 3
V1_MIN_PER_GROUP = 30
V1_SAMPLE_SIZE = 250

# Draft v2: groups defined by what the classifier predicted.
V2_STRATA = (
    "predicted business, no tier",
    "predicted tier 1",
    "predicted tier 2",
    "predicted tier 3",
    "predicted not business",
    "low confidence or unknown",
)
# Organisations placed in a tier are all reviewed by the expert (a census), so
# these three groups cost their full, still unknown, size and have no sampling margin.
V2_CENSUS_STRATA = ("predicted tier 1", "predicted tier 2", "predicted tier 3")

SIZES = (20, 30, 50)
OBSERVED_ACCURACY = 0.90  # the threshold proposed for the main categories
_VERY_LARGE = 10**9  # stands for "group much larger than the sample"

_ROOT = Path(__file__).resolve().parents[2]
DERIVED = _ROOT / "data" / "processed"
OUTPUT = _ROOT / "outputs" / "proposal_v2_numbers.csv"


def _row(section: str, measure: str, value: float | int, note: str) -> dict:
    return {"section": section, "measure": measure, "value": value, "note": note}


# ------------------------------------------------------------------ merges


def _pair_ids(orgs: pd.DataFrame, merges: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """The two organisation ids of every pair awaiting review, as they stand now.

    An id that was folded into another organisation by an automatic merge is
    followed to the organisation that now holds it.
    """
    pairs = merges[merges["decision"] == "propose"]
    current = {}
    for org_id, merged in zip(orgs["org_id"], orgs["pass1_ids_merged"]):
        current[org_id] = org_id
        for old in merged if merged is not None else []:
            current[old] = org_id
    a = pairs["org_id_a"].map(current)
    b = pairs["org_id_b"].map(current)
    if a.isna().any() or b.isna().any():
        raise ValueError("a proposed pair names an organisation that is not in the organisation table")
    return a, b


def merge_numbers(orgs: pd.DataFrame, merges: pd.DataFrame) -> list[dict]:
    """Organisations and delegates behind the name pairs still awaiting review.

    A pair names two organisation ids. An id that was folded into another
    organisation by an automatic merge is followed to the organisation that now
    holds it, so every delegate is counted, and counted once.
    """
    pairs = merges[merges["decision"] == "propose"]
    a, b = _pair_ids(orgs, merges)

    # Groups of organisations chained together by pairs (A~B and B~C is one group of three).
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for x, y in zip(a, b):
        parent[find(x)] = find(y)
    involved = sorted(parent)
    groups = {find(x) for x in involved}

    sub = orgs[orgs["org_id"].isin(involved)]
    n_orgs = len(orgs)
    after = n_orgs - (len(involved) - len(groups))
    total = int(orgs["n_delegates"].sum())
    n_del = int(sub["n_delegates"].sum())
    smaller = pd.concat(
        [a.rename("a"), b.rename("b")], axis=1
    ).apply(lambda r: min(_delegates(orgs, r["a"]), _delegates(orgs, r["b"])), axis=1)
    return [
        _row("merges", "pairs_awaiting_review", len(pairs), "rows with decision 'propose'"),
        _row("merges", "organisations_in_pairs", len(involved), "each organisation counted once"),
        _row("merges", "delegates_in_pairs", n_del, "delegates of those organisations, each organisation once"),
        _row("merges", "delegates_in_pairs_party", int(sub["n_delegates_party"].sum()), "Party badge"),
        _row(
            "merges",
            "delegates_in_pairs_party_overflow",
            int(sub["n_delegates_party_overflow"].sum()),
            "Party overflow badge",
        ),
        _row("merges", "delegates_with_organisation", total, "all delegates that name an organisation"),
        _row(
            "merges",
            "share_of_delegates_in_pairs_pct",
            round(100 * n_del / total, 1),
            "delegates_in_pairs / delegates_with_organisation",
        ),
        _row("merges", "organisations_now", n_orgs, "organisations after cleaning"),
        _row("merges", "organisations_if_all_pairs_accepted", after, "lowest possible count; if none is accepted the count stays"),
        _row("merges", "organisations_removed_if_all_accepted", n_orgs - after, "organisations_now minus the line above"),
        _row(
            "merges",
            "delegates_that_would_change_organisation",
            int(smaller.sum()),
            "sum over pairs of the smaller organisation's delegates; an upper figure, since an organisation in two pairs is counted in both",
        ),
    ]


def _delegates(orgs: pd.DataFrame, org_id: str) -> int:
    return int(orgs.loc[orgs["org_id"] == org_id, "n_delegates"].iloc[0])


# ---------------------------------------------------------------- acronyms


def acronym_numbers(orgs: pd.DataFrame) -> list[dict]:
    """Apply the acronym rule to the organisation names again and count."""
    flag = orgs["canonical_name"].map(is_acronym_like)
    sub = orgs[flag]
    rows = [
        _row("acronyms", "organisations_acronym_like", int(flag.sum()), "rule applied again to canonical_name"),
        _row("acronyms", "delegates_of_acronym_like", int(sub["n_delegates"].sum()), "their delegates"),
        _row("acronyms", "delegates_of_acronym_like_party", int(sub["n_delegates_party"].sum()), "Party badge"),
        _row(
            "acronyms",
            "delegates_of_acronym_like_party_overflow",
            int(sub["n_delegates_party_overflow"].sum()),
            "Party overflow badge",
        ),
        _row(
            "acronyms",
            "share_of_delegates_acronym_like_pct",
            round(100 * sub["n_delegates"].sum() / orgs["n_delegates"].sum(), 1),
            "of all delegates that name an organisation",
        ),
    ]
    if "acronym_like" in orgs.columns:
        rows.append(
            _row(
                "acronyms",
                "disagreements_with_stored_flag",
                int((flag != orgs["acronym_like"]).sum()),
                "0 means the stored flag and the re-derived one agree for every organisation",
            )
        )
    return rows


# -------------------------------------------------------------- duplicates


def duplicate_numbers(delegates: pd.DataFrame) -> list[dict]:
    """People listed on both sheets for one country, and twice on one sheet."""
    per_person = delegates.groupby(["nominated_by_clean", "person_key"])["badge_type"].nunique()
    within = delegates.groupby(["nominated_by_clean", "person_key", "badge_type"]).size()
    return [
        _row("duplicates", "delegate_rows", len(delegates), "rows in the delegate table"),
        _row(
            "duplicates",
            "persons_on_both_sheets_same_country",
            int((per_person > 1).sum()),
            "same name key and nominating country on Party and Party overflow; counted again here",
        ),
        _row(
            "duplicates",
            "rows_flagged_dup_on_party_badge",
            int(delegates["dup_on_party_badge"].sum()),
            "flag stored by the cleaning step",
        ),
        _row(
            "duplicates",
            "persons_twice_on_one_sheet",
            int((within > 1).sum()),
            "same name key, country and sheet more than once; counted again here",
        ),
        _row(
            "duplicates",
            "rows_flagged_dup_within_sheet",
            int(delegates["dup_within_sheet"].sum()),
            "flag stored by the cleaning step (every row of such a pair is flagged)",
        ),
        _row("duplicates", "rows_counted_once", int(delegates["counted_once"].sum()), "rows kept in the count"),
    ]


# ----------------------------------------------------------------- overlap


def overlap_numbers(orgs: pd.DataFrame, delegates: pd.DataFrame, merges: pd.DataFrame) -> list[dict]:
    """Do the similar-name pairs and the acronym-like names concern the same organisations?

    Also how both sets spread over the nominating delegations, counted from the
    delegate table (a delegate belongs to the delegation that nominated them).
    """
    s = "overlap"
    a, b = _pair_ids(orgs, merges)
    in_pairs = set(a) | set(b)
    acronym = set(orgs.loc[orgs["canonical_name"].map(is_acronym_like), "org_id"])
    both, either = in_pairs & acronym, in_pairs | acronym
    n = orgs.set_index("org_id")["n_delegates"]
    total = int(n.sum())

    def count(ids: set) -> int:
        return int(n.reindex(sorted(ids)).sum())

    rows = [
        _row(s, "organisations_in_pairs_and_acronym_like", len(both), "in a pair awaiting review and named only by something like an acronym"),
        _row(s, "delegates_in_pairs_and_acronym_like", count(both), "their delegates"),
        _row(s, "organisations_in_pairs_or_acronym_like", len(either), "in either set, each organisation counted once"),
        _row(s, "delegates_in_pairs_or_acronym_like", count(either), "their delegates, each counted once"),
        _row(
            s,
            "share_of_delegates_in_pairs_or_acronym_like_pct",
            round(100 * count(either) / total, 1),
            "of all delegates that name an organisation",
        ),
    ]
    named = delegates[delegates["org_id"].notna()]
    per_delegation = named.groupby("nominated_by_clean").size()
    rows.append(_row(s, "delegations", int(per_delegation.size), "nominating delegations with at least one delegate that names an organisation"))
    for label, ids in (("pairs", in_pairs), ("acronym_like", acronym), ("pairs_or_acronym_like", either)):
        hit = named[named["org_id"].isin(ids)].groupby("nominated_by_clean").size()
        share = (hit / per_delegation).dropna()
        rows += [
            _row(s, f"delegations_with_{label}", int(hit.size), "delegations with at least one such delegate"),
            _row(
                s,
                f"largest_delegation_share_of_{label}_delegates_pct",
                round(100 * hit.max() / hit.sum(), 1) if hit.size else 0.0,
                "share of all such delegates that come from the one delegation with the most",
            ),
            _row(
                s,
                f"highest_share_within_a_delegation_{label}_pct",
                round(100 * share.max(), 1) if share.size else 0.0,
                "highest share of one delegation's own delegates (those naming an organisation) that are in the set",
            ),
            _row(
                s,
                f"median_share_within_a_delegation_{label}_pct",
                round(100 * (hit / per_delegation).fillna(0).median(), 1),
                "median over all delegations, a delegation with none counting as 0",
            ),
        ]
    return rows


# ----------------------------------------------------------- sample design


def _ceiling_margin(n: int) -> float:
    """Worst-case margin for one group of n checked, when the group is very large."""
    table = expected_margin_of_error(pd.DataFrame({"stratum": ["x"], "N_h": [_VERY_LARGE], "n_h": [n]}))
    return float(table.loc[table["stratum"] == "x", "margin_of_error"].iloc[0])


def sample_design_numbers(sizes: tuple[int, ...] = SIZES) -> list[dict]:
    """Arithmetic for the expert sample, as a function of organisations checked per group."""
    s = "sample_design"
    v1_groups = V1_CATEGORIES * V1_CONFIDENCE_LEVELS
    v1_need = v1_groups * V1_MIN_PER_GROUP
    n_strata = len(V2_STRATA)
    n_sampled = n_strata - len(V2_CENSUS_STRATA)
    rows = [
        _row(s, "v1_groups", v1_groups, f"{V1_CATEGORIES} categories x {V1_CONFIDENCE_LEVELS} confidence levels"),
        _row(s, "v1_minimum_needed", v1_need, f"v1_groups x {V1_MIN_PER_GROUP}"),
        _row(s, "v1_sample_size", V1_SAMPLE_SIZE, "size stated in draft v1"),
        _row(s, "v1_shortfall", v1_need - V1_SAMPLE_SIZE, "needed minus stated; upper figure, some groups may be empty or smaller than the minimum"),
        _row(s, "v2_strata", n_strata, "; ".join(V2_STRATA)),
        _row(s, "v2_strata_reviewed_in_full", len(V2_CENSUS_STRATA), "the three tier groups: every organisation reviewed, no sampling margin"),
        _row(s, "v2_strata_sampled", n_sampled, "groups from which a random sample is drawn"),
    ]
    for n in sizes:
        m = _ceiling_margin(n)
        lo, hi = wilson_interval(round(OBSERVED_ACCURACY * n), n)
        rows += [
            _row(s, f"margin_ceiling_pct_points_n{n}", round(100 * m, 1), "worst case (share 50%), group much larger than the sample, 95%"),
            _row(s, f"correct_at_90pct_n{n}", round(OBSERVED_ACCURACY * n), f"organisations correct if 90% of {n} are"),
            _row(s, f"wilson_low_pct_at_90pct_n{n}", round(100 * lo, 1), "lower end of the 95% interval when 90% of those checked are correct"),
            _row(s, f"wilson_high_pct_at_90pct_n{n}", round(100 * hi, 1), "upper end of the same interval"),
            _row(s, f"cost_all_six_strata_n{n}", n_strata * n, "if every group were sampled at this size"),
            _row(s, f"cost_sampled_strata_n{n}", n_sampled * n, "random part only; the tier groups, reviewed in full, come on top and their size is not yet known"),
        ]
    for label, k in (("six", n_strata), ("three", n_sampled)):
        per = V1_SAMPLE_SIZE // k
        rows += [
            _row(s, f"per_stratum_if_250_over_{label}", per, f"{V1_SAMPLE_SIZE} divided equally over {k} groups, rounded down"),
            _row(s, f"margin_ceiling_pct_points_250_over_{label}", round(100 * _ceiling_margin(per), 1), "worst case at that size, 95%"),
        ]
        correct = round(OBSERVED_ACCURACY * per)
        lo, hi = wilson_interval(correct, per)
        rows += [
            _row(s, f"correct_nearest_90pct_250_over_{label}", correct, f"whole number of organisations nearest to 90% of {per}"),
            _row(s, f"wilson_low_pct_250_over_{label}", round(100 * lo, 1), f"lower end of the 95% interval when {correct} of {per} are correct"),
            _row(s, f"wilson_high_pct_250_over_{label}", round(100 * hi, 1), "upper end of the same interval"),
        ]
    return rows


# ------------------------------------------------------------------- build


def build_table(orgs: pd.DataFrame, delegates: pd.DataFrame, merges: pd.DataFrame) -> pd.DataFrame:
    """All figures in one long table: section, measure, value, note."""
    from analysis.organisation_signals import signal_numbers  # imported here: that module imports this one

    rows = (
        merge_numbers(orgs, merges)
        + acronym_numbers(orgs)
        + duplicate_numbers(delegates)
        + overlap_numbers(orgs, delegates, merges)
        + sample_design_numbers()
        + signal_numbers(orgs, delegates)
    )
    return pd.DataFrame(rows, columns=["section", "measure", "value", "note"])


def main(derived: Path = DERIVED, output: Path = OUTPUT) -> pd.DataFrame:
    """Read the cleaned tables, write the output file, return the table."""
    table = build_table(
        pd.read_parquet(derived / "organisations_eu.parquet"),
        pd.read_parquet(derived / "delegates_eu.parquet"),
        pd.read_csv(derived / "proposed_merges_eu.csv"),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)
    return table


if __name__ == "__main__":
    print(main().to_string(index=False))
