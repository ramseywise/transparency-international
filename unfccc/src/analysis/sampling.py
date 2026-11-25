"""Drawing the expert's checking sample, and saying how precise it will be.

The idea: we have about 1,250 organisations, each with a predicted category and
a confidence level. An expert can only check about 250. Instead of picking 250
at random from everything (which would hardly ever hit the small groups we care
about), we split the records into groups ("strata", for example "business x low
confidence") and draw from each group. Because some groups are deliberately
sampled more heavily than their size warrants, every sampled row must remember
how big its group is (``N_h``) and how many were drawn from it (``n_h``). Those
two numbers are what ``analysis.stats`` uses to weight the groups back to their
true size.

Vocabulary used below:

* stratum / ``h``: one group, e.g. the records predicted "business" with "low"
  confidence.
* ``N_h``: how many records the group holds in the full population.
* ``n_h``: how many of them are in the expert's sample.
* margin of error: half the width of a 95% confidence interval. "+/- 0.07"
  means that, if the sample is a fair draw, the true figure is probably within
  7 percentage points of our estimate.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd

STRATUM_COL = "stratum"
POP_COL = "N_h"
SAMPLE_COL = "n_h"

__all__ = [
    "STRATUM_COL",
    "POP_COL",
    "SAMPLE_COL",
    "stratum_labels",
    "stratified_sample",
    "expected_margin_of_error",
]


def _z(conf: float) -> float:
    return NormalDist().inv_cdf(0.5 + conf / 2.0)


def _label(values: Any) -> str:
    if isinstance(values, tuple):
        return "|".join(str(v) for v in values)
    return str(values)


def stratum_labels(df: pd.DataFrame, strata_cols: Sequence[str]) -> pd.Series:
    """Return one text label per row naming its stratum.

    A stratum made from several columns is written with ``|`` between the
    values, for example ``"business|low"``. Missing values are refused: a record
    with no category or no confidence must be given one (for example
    "unknown") before sampling, otherwise it would silently never be sampled.
    """
    cols = list(strata_cols)
    if not cols:
        raise ValueError("strata_cols must name at least one column")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"columns not found: {missing}")
    if df[cols].isna().any().any():
        raise ValueError(
            "strata columns contain missing values; fill them (e.g. with "
            "'unknown') so every record belongs to a stratum"
        )
    return df[cols].astype(str).agg("|".join, axis=1)


def _allocate(
    pop: np.ndarray, weight: np.ndarray, n_total: int, floor: int
) -> np.ndarray:
    """Whole-number sample sizes: proportional to pop*weight, with a floor,
    capped at pop, summing to n_total."""
    k = len(pop)
    floors = np.minimum(floor, pop).astype(int)
    if floors.sum() > n_total:
        raise ValueError(
            f"min_per_stratum={floor} over {k} strata needs at least "
            f"{floors.sum()} records but n_total is {n_total}"
        )
    if n_total > pop.sum():
        raise ValueError(
            f"n_total={n_total} is larger than the whole population "
            f"({int(pop.sum())})"
        )
    target = pop * weight
    fixed = np.zeros(k, dtype=bool)
    alloc = np.zeros(k, dtype=float)
    while True:
        free = ~fixed
        if not free.any():
            break
        budget = n_total - alloc[fixed].sum()
        share = np.zeros(k)
        share[free] = budget * target[free] / target[free].sum()
        too_big = free & (share > pop)
        if too_big.any():
            alloc[too_big] = pop[too_big]
            fixed |= too_big
            continue
        too_small = free & (share < floors)
        if too_small.any():
            alloc[too_small] = floors[too_small]
            fixed |= too_small
            continue
        alloc[free] = share[free]
        break

    out = np.floor(alloc + 1e-9).astype(int)
    out = np.maximum(out, floors)
    out = np.minimum(out, pop.astype(int))
    # largest-remainder rounding, then repair any remaining difference
    frac = alloc - np.floor(alloc + 1e-9)
    diff = n_total - out.sum()
    order = np.argsort(-frac, kind="stable")
    while diff > 0:
        moved = False
        for i in order:
            if diff > 0 and out[i] < pop[i]:
                out[i] += 1
                diff -= 1
                moved = True
        if not moved:
            break
    order_rev = np.argsort(frac, kind="stable")
    while diff < 0:
        moved = False
        for i in order_rev:
            if diff < 0 and out[i] > floors[i]:
                out[i] -= 1
                diff += 1
                moved = True
        if not moved:
            break
    return out


def stratified_sample(
    df: pd.DataFrame,
    strata_cols: Sequence[str],
    n_total: int,
    seed: int,
    min_per_stratum: int = 5,
    oversample: Mapping[Any, float] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Draw a reproducible stratified random sample.

    How the sample sizes are chosen:

    1. Each stratum starts with a share of ``n_total`` proportional to its size
       ``N_h`` times its over-sampling weight (default 1, i.e. plain
       proportional allocation).
    2. Every stratum gets at least ``min_per_stratum`` records, so small groups
       (for example predicted negatives) are never missed. This is what makes
       it possible to estimate what the classifier missed.
    3. No stratum is asked for more than it holds; a stratum smaller than the
       floor is taken whole (a census of that group).
    4. The remaining places are shared out again among the other strata, and
       the whole-number sizes add up to exactly ``n_total``.

    Parameters
    ----------
    df: the full population, one row per record.
    strata_cols: columns that define the strata, e.g.
        ``["predicted_category", "confidence"]``.
    n_total: sample size wanted (about 250).
    seed: random seed. The same ``df`` (same rows in the same order), the same
        arguments and the same seed always give the same sample. Record the
        seed in the validation plan.
    min_per_stratum: floor per stratum (see step 2).
    oversample: optional ``{stratum: weight}``. A weight of 2 means "sample this
        group at twice the rate it would get proportionally". The key is the
        stratum label as ``stratum_labels`` writes it (``"business|low"``), a
        tuple of values (``("business", "low")``) or, with one strata column,
        the bare value. Unknown keys raise an error so typos are not ignored.

    Returns
    -------
    sample: the sampled rows (original index and columns kept, original row
        order) plus ``stratum``, ``N_h`` and ``n_h``. The estimation weight of
        each row is ``N_h / n_h``.
    allocation: one row per stratum with the strata columns, ``stratum``,
        ``N_h``, ``weight`` (over-sampling weight used), ``n_h`` and
        ``sampling_fraction`` (n_h / N_h).

    The input ``df`` is not modified. Rows are shown to the expert in shuffled
    order by a separate step; this function does not shuffle.
    """
    if n_total <= 0:
        raise ValueError("n_total must be positive")
    if min_per_stratum < 0:
        raise ValueError("min_per_stratum must be >= 0")
    strata_cols = list(strata_cols)
    labels = stratum_labels(df, strata_cols)
    counts = labels.value_counts().sort_index()
    keys = list(counts.index)
    pop = counts.to_numpy(dtype=float)

    weights = np.ones(len(keys))
    if oversample:
        for raw_key, w in oversample.items():
            key = _label(raw_key)
            if key not in counts.index:
                raise ValueError(
                    f"oversample key {raw_key!r} matches no stratum; "
                    f"strata are {keys}"
                )
            if w <= 0:
                raise ValueError("oversample weights must be positive")
            weights[keys.index(key)] = float(w)

    n_h = _allocate(pop, weights, int(n_total), int(min_per_stratum))

    rng = np.random.default_rng(seed)
    chosen: list[np.ndarray] = []
    label_values = labels.to_numpy()
    for key, n in zip(keys, n_h):  # keys are sorted, so the draw is stable
        positions = np.flatnonzero(label_values == key)
        chosen.append(rng.choice(positions, size=int(n), replace=False))
    picked = np.sort(np.concatenate(chosen)) if chosen else np.array([], int)

    n_map = dict(zip(keys, n_h))
    N_map = dict(zip(keys, counts.astype(int)))
    sample = df.iloc[picked].copy()
    sample[STRATUM_COL] = labels.iloc[picked].to_numpy()
    sample[POP_COL] = sample[STRATUM_COL].map(N_map).astype(int)
    sample[SAMPLE_COL] = sample[STRATUM_COL].map(n_map).astype(int)

    first = (
        df.assign(**{STRATUM_COL: labels})
        .drop_duplicates(STRATUM_COL)
        .set_index(STRATUM_COL)[strata_cols]
    )
    allocation = first.loc[keys].reset_index()
    allocation[POP_COL] = [int(N_map[k]) for k in keys]
    allocation["weight"] = weights
    allocation[SAMPLE_COL] = [int(n_map[k]) for k in keys]
    allocation["sampling_fraction"] = allocation[SAMPLE_COL] / allocation[POP_COL]
    return sample, allocation


def expected_margin_of_error(
    allocation: pd.DataFrame, conf: float = 0.95
) -> pd.DataFrame:
    """Margin of error to expect from a design, before any expert answers.

    Worst case: we assume the true proportion being estimated is 0.5 (the case
    with the widest interval), so the figures are a ceiling on what a
    percentage will look like. They include the finite-population correction:
    sampling most of a small group leaves little uncertainty, and a group
    sampled completely has none.

    * Per stratum: ``z * sqrt(0.25 / n_h * (1 - n_h / N_h))``, with z = 1.96
      for 95%. It answers "if we measured accuracy inside this group alone,
      how far off might we be?". A stratum with ``n_h = 0`` gets ``inf``.
    * Overall (the last row, ``stratum == "ALL"``): the margin for a
      population-wide proportion, combining strata weighted by ``N_h / N``:
      ``z * sqrt(sum_h W_h^2 * 0.25 / n_h * (1 - n_h / N_h))``. Over-sampling
      small strata usually costs little here and buys much tighter figures for
      them.

    ``allocation`` is the table returned by ``stratified_sample`` (needs
    columns ``stratum``, ``N_h``, ``n_h``). Returns a table with those columns
    plus ``margin_of_error``.
    """
    for c in (STRATUM_COL, POP_COL, SAMPLE_COL):
        if c not in allocation.columns:
            raise KeyError(f"allocation needs a '{c}' column")
    z = _z(conf)
    N = allocation[POP_COL].to_numpy(float)
    n = allocation[SAMPLE_COL].to_numpy(float)
    if (n > N).any():
        raise ValueError("n_h exceeds N_h in some stratum")
    with np.errstate(divide="ignore", invalid="ignore"):
        var = np.where(n > 0, 0.25 / n * (1 - n / N), np.inf)
    out = allocation[[STRATUM_COL, POP_COL, SAMPLE_COL]].copy()
    out["margin_of_error"] = z * np.sqrt(var)
    W = N / N.sum()
    with np.errstate(invalid="ignore"):
        overall_var = np.sum(np.where(np.isinf(var), np.inf, W**2 * var))
    # a stratum with zero weight in W and inf var cannot occur (N_h >= 1)
    total = pd.DataFrame(
        {
            STRATUM_COL: ["ALL"],
            POP_COL: [int(N.sum())],
            SAMPLE_COL: [int(n.sum())],
            "margin_of_error": [z * np.sqrt(overall_var)],
        }
    )
    return pd.concat([out, total], ignore_index=True)
