"""Measuring how accurate the classifier is, from the expert's checked sample.

Everything here assumes the sample came from ``analysis.sampling.stratified_sample``
(or any design with the same shape): the records were split into groups
("strata"), a random number were drawn from each, and some groups were sampled
more heavily than others. A plain average over the sample would therefore be
wrong, because heavily sampled groups would count for too much. Instead each
group's result is weighted by how many records the group really holds
(``N_h``), and the uncertainty is worked out from how many were checked
(``n_h``).

Terms:

* ``N_h``: size of group h in the full set of ~1,250 records.
* ``n_h``: how many of group h the expert checked.
* 95% confidence interval: a range built so that, if we repeated the whole
  sampling exercise many times, about 95 in 100 of the ranges would contain the
  true figure. Wide interval = we do not know the figure precisely.
* Finite population correction (FPC): checking a large share of a small group
  tells you almost everything about it, so the uncertainty shrinks by
  ``(1 - n_h / N_h)``. A group checked completely has no sampling uncertainty.

Only pandas, numpy and the standard library are used (the normal quantile comes
from ``statistics.NormalDist``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd

__all__ = [
    "RecallNotEstimable",
    "wilson_interval",
    "stratified_proportion",
    "accuracy_by_group",
    "precision_recall_by_category",
    "weighted_confusion_table",
    "agreement",
]


class RecallNotEstimable(ValueError):
    """Raised when recall cannot be estimated because no predicted-negatives
    (records predicted to be some *other* category) were checked."""


def _z(conf: float) -> float:
    if not 0 < conf < 1:
        raise ValueError("conf must be between 0 and 1")
    return NormalDist().inv_cdf(0.5 + conf / 2.0)


# ---------------------------------------------------------------- Wilson


def wilson_interval(successes: float, n: float, conf: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for a proportion: ``successes`` right out of ``n`` checked.

    Use this for a simple, unweighted count ("37 of 40 were correct"). Unlike
    the textbook ``p +/- 1.96 * sqrt(p(1-p)/n)`` interval it behaves sensibly
    for small ``n`` and for proportions near 0 or 1: it never leaves [0, 1],
    and 40 out of 40 correct still gives a lower limit well below 100%, because
    40 checks cannot prove perfection.

    ``n`` may be fractional (the stratified estimator passes an "effective"
    sample size). With ``n == 0`` nothing is known and ``(0.0, 1.0)`` is
    returned. Returns ``(low, high)``.
    """
    if n < 0 or successes < 0 or successes > n + 1e-9:
        raise ValueError("need 0 <= successes <= n")
    if n == 0:
        return 0.0, 1.0
    z = _z(conf)
    p = successes / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return float(max(0.0, centre - half)), float(min(1.0, centre + half))


# ------------------------------------------------- stratified estimation


def _population_map(
    sample: pd.DataFrame, stratum_col: str, population: Mapping[Any, int] | pd.Series | None
) -> pd.Series:
    """Population size N_h per stratum, from ``population`` or the ``N_h`` column."""
    if population is None:
        if "N_h" not in sample.columns:
            raise ValueError("give `population` (stratum -> N_h) or include an 'N_h' column")
        pop = sample.groupby(stratum_col)["N_h"].agg(["min", "max"])
        if (pop["min"] != pop["max"]).any():
            raise ValueError("N_h is not constant within a stratum")
        return pop["min"].astype(float)
    pop = pd.Series(dict(population), dtype=float)
    unknown = set(sample[stratum_col]) - set(pop.index)
    if unknown:
        raise ValueError(f"sampled strata missing from population: {sorted(unknown, key=str)}")
    return pop


def _check_sizes(N: pd.Series, n: pd.Series) -> None:
    if (N <= 0).any():
        raise ValueError("population sizes N_h must be positive")
    over = n.reindex(N.index).fillna(0) > N
    if over.any():
        raise ValueError(f"sample larger than population in strata {list(N.index[over])}")


def _stratified_core(
    N: np.ndarray, n: np.ndarray, x: np.ndarray, conf: float, empty_strata: str
) -> dict:
    """Weighted proportion + interval from per-stratum arrays (see public docstring)."""
    if empty_strata not in ("raise", "bound"):
        raise ValueError("empty_strata must be 'raise' or 'bound'")
    W = N / N.sum()
    empty = n == 0
    obs = ~empty
    notes: list[str] = []
    if empty.any() and empty_strata == "raise":
        raise ValueError(
            f"{int(empty.sum())} stratum/strata hold records but none were "
            f"checked (n_h = 0), carrying {W[empty].sum():.1%} of the population. "
            "Draw at least one record per stratum, or pass "
            "empty_strata='bound' to get worst-case bounds instead of an estimate."
        )
    if (n == 1).any():
        notes.append(
            f"{int((n == 1).sum())} stratum/strata have n_h = 1: their spread is "
            "unmeasurable from one record, so a worst-case-leaning variance is used"
        )

    p_h = np.zeros(len(N))
    p_h[obs] = x[obs] / n[obs]
    # Shrunk proportion, used ONLY for the variance, so that a stratum that
    # happened to be 5/5 or 0/5 is not treated as having zero uncertainty.
    p_t = np.zeros(len(N))
    p_t[obs] = (x[obs] + 1.0) / (n[obs] + 2.0)
    fpc = np.zeros(len(N))
    fpc[obs] = 1 - n[obs] / N[obs]
    var_h = np.zeros(len(N))
    var_h[obs] = fpc[obs] * p_t[obs] * (1 - p_t[obs]) / n[obs]

    def interval(p_hat: float, pbar: float, var: float) -> tuple[float, float, float]:
        se = float(np.sqrt(var))
        if var <= 0:
            return p_hat, p_hat, se
        # Wilson interval with the "effective sample size" implied by the
        # stratified variance: n_eff = p(1-p)/variance. This keeps the interval
        # inside [0, 1] and honest near 0 or 1.
        n_eff = pbar * (1 - pbar) / var
        lo, hi = wilson_interval(p_hat * n_eff, n_eff, conf)
        return lo, hi, se

    var = float(np.sum(W**2 * var_h))
    if not empty.any():
        p_hat = float(np.sum(W * p_h))
        pbar = float(np.sum(W * p_t))
        lo, hi, se = interval(p_hat, pbar, var)
        return dict(estimate=p_hat, ci_low=lo, ci_high=hi, se=se, unobserved_weight=0.0, notes=notes)

    # empty_strata == "bound": unobserved strata are set to all-wrong (lower
    # scenario) and all-right (upper scenario); their variance is taken as 0
    # because the bound is deterministic.
    w_empty = float(W[empty].sum())
    base = float(np.sum(W[obs] * p_h[obs]))
    pbar_obs = float(np.sum(W[obs] * p_t[obs]))
    lo, _, se = interval(base, pbar_obs, var)
    _, hi, _ = interval(base + w_empty, min(pbar_obs + w_empty, 1.0), var)
    notes.append(
        f"{int(empty.sum())} stratum/strata unobserved ({w_empty:.1%} of the "
        "population): estimate withheld, interval spans all-wrong to all-right for them"
    )
    return dict(estimate=float("nan"), ci_low=lo, ci_high=hi, se=se, unobserved_weight=w_empty, notes=notes)


def stratified_proportion(
    sample: pd.DataFrame,
    stratum_col: str,
    outcome_col: str,
    population: Mapping[Any, int] | pd.Series | None = None,
    conf: float = 0.95,
    empty_strata: str = "raise",
) -> dict:
    """Estimate a population proportion (e.g. share correct) from a stratified sample.

    ``outcome_col`` is True/False (or 1/0): did this checked record have the
    property (e.g. "classifier was right")? The estimate is
    ``sum_h W_h * p_h`` where ``p_h`` is the share of group h that had the
    property and ``W_h = N_h / N`` is the group's true share of the population.

    ``population`` maps stratum -> ``N_h``. If omitted, the sample's ``N_h``
    column (written by ``stratified_sample``) is used. Pass it explicitly when
    some strata have no sampled rows at all, otherwise they are invisible.

    Interval: the variance is ``sum_h W_h^2 (1 - n_h/N_h) p~_h (1 - p~_h) / n_h``
    (the standard stratified formula including the finite population
    correction). It is turned into a 95% interval by a Wilson score interval
    using the matching "effective sample size". Why: the plain
    estimate +/- 1.96 se interval can fall outside 0-100% and is too narrow when
    the figure is near the edges, which is exactly where a good classifier sits.

    Small strata, handled explicitly (nothing is dropped):

    * ``n_h = 1``: one record says nothing about spread. For the *variance only*
      every stratum uses the shrunk proportion ``p~_h = (x_h + 1) / (n_h + 2)``,
      so a stratum with 1 of 1 correct is treated as "probably around 2/3 with
      real uncertainty", not "certainly 100%". The point estimate still uses the
      raw ``x_h / n_h``. A note is added to the result.
    * ``n_h = 0`` (the group holds records but none were checked): the group's
      accuracy is unknown, and guessing would hide that. With
      ``empty_strata='raise'`` (default) an error is raised. With
      ``empty_strata='bound'`` the estimate is withheld (NaN) and the interval
      runs from "all unchecked records wrong" to "all right", so the
      width shows how much is unknown. Strata with ``n_h = N_h`` (everything
      checked) contribute no sampling uncertainty.

    Returns a dict: ``estimate``, ``ci_low``, ``ci_high``, ``se``, ``n`` (records
    checked), ``N`` (population), ``n_strata``, ``unobserved_weight`` (share of
    the population in unchecked strata) and ``notes``.
    """
    if outcome_col not in sample.columns or stratum_col not in sample.columns:
        raise KeyError("sample is missing the stratum or outcome column")
    if sample[outcome_col].isna().any():
        raise ValueError(f"'{outcome_col}' has missing values; resolve them before estimating")
    pop = _population_map(sample, stratum_col, population)
    outcome = sample[outcome_col].astype(float)
    if not outcome.isin([0.0, 1.0]).all():
        raise ValueError(f"'{outcome_col}' must be True/False or 1/0")
    g = outcome.groupby(sample[stratum_col])
    n = g.size().reindex(pop.index).fillna(0)
    x = g.sum().reindex(pop.index).fillna(0)
    _check_sizes(pop, n)
    res = _stratified_core(pop.to_numpy(), n.to_numpy(float), x.to_numpy(float), conf, empty_strata)
    res.update(n=int(n.sum()), N=int(pop.sum()), n_strata=int(len(pop)))
    return res


def accuracy_by_group(
    sample: pd.DataFrame,
    group_col: str,
    correct_col: str,
    stratum_col: str = "stratum",
    population: Mapping[Any, int] | pd.Series | None = None,
    conf: float = 0.95,
    empty_strata: str = "raise",
) -> pd.DataFrame:
    """Accuracy (share of records the classifier got right) for each group.

    ``group_col`` is typically the confidence level. ``correct_col`` is
    True/False: does the predicted label equal the expert's label? Each group's
    accuracy is a weighted, stratified estimate (see ``stratified_proportion``),
    so a group's figure is correct even if some of its strata were
    over-sampled.

    Requirement: each stratum must lie wholly inside one group (true when
    strata are predicted-category x confidence and the group is confidence, or
    the group is the stratum itself). If not, the groups would be "domains"
    cutting across strata, which needs a different estimator, and an error is
    raised rather than a wrong number.

    Returns one row per group plus a final row ``ALL``: ``n_checked``,
    ``N_population``, ``accuracy``, ``ci_low``, ``ci_high``, ``margin`` (half the
    interval width, a rough "plus or minus"), ``notes``.
    """
    if group_col not in sample.columns:
        raise KeyError(group_col)
    spread = sample.groupby(stratum_col)[group_col].nunique()
    if (spread > 1).any():
        raise ValueError(
            f"strata {list(spread.index[spread > 1])} span more than one value of "
            f"'{group_col}'; accuracy by group needs strata nested inside groups"
        )
    pop_all = _population_map(sample, stratum_col, population)
    stratum_group = sample.groupby(stratum_col)[group_col].first()
    # strata with no sampled rows have unknown group; they cannot be assigned
    unassigned = [s for s in pop_all.index if s not in stratum_group.index]
    if unassigned:
        raise ValueError(
            f"strata {unassigned} have no sampled rows, so their {group_col} is unknown; "
            "sample at least one record from each"
        )
    rows = []
    for grp in sorted(stratum_group.unique(), key=str):
        sub = sample[sample[group_col] == grp]
        pop = pop_all[stratum_group[stratum_group == grp].index]
        rows.append((grp, stratified_proportion(sub, stratum_col, correct_col, pop, conf, empty_strata)))
    rows.append(("ALL", stratified_proportion(sample, stratum_col, correct_col, pop_all, conf, empty_strata)))
    out = pd.DataFrame(
        {
            group_col: [g for g, _ in rows],
            "n_checked": [r["n"] for _, r in rows],
            "N_population": [r["N"] for _, r in rows],
            "accuracy": [r["estimate"] for _, r in rows],
            "ci_low": [r["ci_low"] for _, r in rows],
            "ci_high": [r["ci_high"] for _, r in rows],
            "notes": ["; ".join(r["notes"]) for _, r in rows],
        }
    )
    out["margin"] = (out["ci_high"] - out["ci_low"]) / 2
    return out[[group_col, "n_checked", "N_population", "accuracy", "ci_low", "ci_high", "margin", "notes"]]


# ----------------------------------------------- precision and recall


def precision_recall_by_category(
    sample: pd.DataFrame,
    pred_col: str,
    truth_col: str,
    stratum_col: str = "stratum",
    population: Mapping[Any, int] | pd.Series | None = None,
    categories: Sequence[Any] | None = None,
    conf: float = 0.95,
    n_boot: int = 2000,
    seed: int = 0,
) -> pd.DataFrame:
    """Precision and recall for each category, with confidence intervals.

    * Precision for category X: of the records the classifier labelled X, what
      share does the expert also label X? Answers "can I trust an X label?".
    * Recall for category X: of all records that truly are X (per the expert),
      what share did the classifier label X? Answers "how many X did it miss?".

    The design must be stratified by *predicted* category (strata may be finer,
    e.g. predicted category x confidence, but each stratum must sit inside one
    predicted category). Precision only needs the records predicted X. Recall
    needs the whole population: the true X's the classifier missed sit among
    records it labelled something else, and can only be counted if some of
    those were checked. So recall is
    ``sum over strata of N_h * (share of the stratum that is truly X and predicted X)``
    divided by ``sum over strata of N_h * (share that is truly X)``.

    Refusal: if no records predicted as anything other than X were checked (no
    "predicted negatives"), or any stratum holding such records was left
    unchecked, recall cannot be estimated and ``RecallNotEstimable`` is raised.
    Reporting 100% recall in that case would be an artefact of the sample, not
    a fact. If you only need precision, call ``stratified_proportion`` directly.

    Interval methods and why:

    * Precision: the stratified Wilson interval of ``stratified_proportion``
      (analytic, with finite population correction, stays within 0-1).
    * Recall: it is a ratio of two estimated totals, with no simple formula
      that stays correct under unequal sampling. A **seeded stratified
      bootstrap** is used: within each stratum the checked records are
      resampled with replacement (``n_h`` per stratum, so the design is
      respected), the ratio is recomputed ``n_boot`` times, and the 2.5th and
      97.5th percentiles form the interval. It is slightly conservative
      because it ignores the finite population correction. Its weakness: with
      very few checked records of a true X (or strata of 1-2 records) the
      resampled values barely vary and the interval can be too narrow or
      degenerate; the ``notes`` column flags when fewer than 10 true X were
      checked. The same seed always gives the same interval.

    Returns one row per category: ``precision``, ``precision_low``,
    ``precision_high``, ``recall``, ``recall_low``, ``recall_high``,
    ``n_predicted_checked`` (checked records predicted X), ``n_true_checked``
    (checked records the expert calls X), ``est_true_total`` (estimated number
    of true X in the whole population) and ``notes``.
    """
    for c in (pred_col, truth_col, stratum_col):
        if c not in sample.columns:
            raise KeyError(c)
    if sample[[pred_col, truth_col]].isna().any().any():
        raise ValueError("prediction or expert label has missing values; resolve them first")
    pop = _population_map(sample, stratum_col, population)
    per = sample.groupby(stratum_col)[pred_col].nunique()
    if (per > 1).any():
        raise ValueError(
            f"strata {list(per.index[per > 1])} contain more than one predicted "
            "category; stratify by predicted category (optionally x confidence)"
        )
    pred_of = sample.groupby(stratum_col)[pred_col].first().reindex(pop.index)
    n_h = sample.groupby(stratum_col).size().reindex(pop.index).fillna(0)
    _check_sizes(pop, n_h)
    cats = list(categories) if categories is not None else sorted(
        set(sample[pred_col]) | set(sample[truth_col]), key=str
    )
    rng = np.random.default_rng(seed)
    N = pop.to_numpy()
    n = n_h.to_numpy(float)
    rows = []
    for c in cats:
        is_pred = (pred_of == c).to_numpy()
        # ---- precision
        sub = sample[sample[pred_col] == c]
        notes: list[str] = []
        prec = dict(estimate=np.nan, ci_low=np.nan, ci_high=np.nan)
        if len(sub):
            flag = (sub[truth_col] == c)
            tmp = sub.assign(_hit=flag)
            prec = stratified_proportion(tmp, stratum_col, "_hit", pop[pop.index[is_pred]], conf)
            notes += prec["notes"]
        else:
            notes.append("no records predicted as this category were checked: precision unknown")
        # ---- recall (refuse without predicted negatives)
        neg_strata = ~is_pred
        if n[neg_strata].sum() == 0:
            raise RecallNotEstimable(
                f"cannot estimate recall for {c!r}: no records predicted as anything "
                "other than this category were checked, so missed cases cannot be "
                "counted. Include predicted-negatives in the sample."
            )
        if (n[neg_strata] == 0).any():
            bad = list(pop.index[neg_strata & (n == 0)])
            raise RecallNotEstimable(
                f"cannot estimate recall for {c!r}: predicted-negative strata {bad} "
                "hold records but none were checked"
            )
        if (n[is_pred] == 0).any():
            raise RecallNotEstimable(
                f"cannot estimate recall for {c!r}: strata predicted {c!r} were not checked"
            )
        hit = sample[truth_col].eq(c).astype(float).groupby(sample[stratum_col]).sum()
        x = hit.reindex(pop.index).fillna(0).to_numpy()
        share = x / n
        t_hat = float(np.sum(N * share))
        tp_hat = float(np.sum(N[is_pred] * share[is_pred]))
        n_true = int(x.sum())
        if t_hat <= 0:
            rec = rlo = rhi = np.nan
            notes.append("no true members of this category were found in the sample: recall undefined")
        else:
            rec = tp_hat / t_hat
            boot_x = rng.binomial(n[:, None].astype(int), share[:, None], size=(len(N), n_boot))
            boot_share = boot_x / n[:, None]
            t_b = (N[:, None] * boot_share).sum(axis=0)
            tp_b = (N[is_pred, None] * boot_share[is_pred]).sum(axis=0)
            ok = t_b > 0
            ratios = tp_b[ok] / t_b[ok]
            alpha = (1 - conf) / 2
            rlo, rhi = (float(v) for v in np.quantile(ratios, [alpha, 1 - alpha]))
            if n_true < 10:
                notes.append(f"only {n_true} true members checked: recall interval is unreliable")
            if (n == 1).any():
                notes.append("strata with n_h = 1 add no resampling variation to the recall interval")
        rows.append(
            dict(
                category=c,
                precision=prec["estimate"],
                precision_low=prec["ci_low"],
                precision_high=prec["ci_high"],
                recall=rec,
                recall_low=rlo,
                recall_high=rhi,
                n_predicted_checked=int(len(sub)),
                n_true_checked=n_true,
                est_true_total=t_hat,
                notes="; ".join(notes),
            )
        )
    return pd.DataFrame(rows)


# --------------------------------------------------- confusion table


def weighted_confusion_table(
    sample: pd.DataFrame,
    pred_col: str,
    truth_col: str,
    stratum_col: str = "stratum",
    population: Mapping[Any, int] | pd.Series | None = None,
    normalize: str | None = None,
) -> pd.DataFrame:
    """Estimated confusion table for the whole population.

    Rows are what the classifier predicted, columns what the expert said. Each
    cell is the *estimated number of records in the full population* with that
    combination: every checked record counts ``N_h / n_h`` times (the number of
    records in its group it stands for). Cell estimates add up to the total
    population. These are estimates, not counts: a cell built from one or two
    checked records is very uncertain.

    ``normalize='row'`` instead gives, for each predicted category, the share
    that the expert put in each category (rows add to 1). Strata holding records
    but with no checked records raise an error, because their records could not
    be placed in the table.
    """
    for c in (pred_col, truth_col, stratum_col):
        if c not in sample.columns:
            raise KeyError(c)
    if sample[[pred_col, truth_col]].isna().any().any():
        raise ValueError("prediction or expert label has missing values; resolve them first")
    pop = _population_map(sample, stratum_col, population)
    n_h = sample.groupby(stratum_col).size().reindex(pop.index).fillna(0)
    _check_sizes(pop, n_h)
    if (n_h == 0).any():
        raise ValueError(f"strata {list(pop.index[n_h == 0])} have no checked records")
    w = (pop / n_h).reindex(sample[stratum_col]).to_numpy()
    tab = pd.crosstab(
        sample[pred_col], sample[truth_col], values=w, aggfunc="sum"
    ).fillna(0.0)
    labels = sorted(set(tab.index) | set(tab.columns), key=str)
    tab = tab.reindex(index=labels, columns=labels, fill_value=0.0)
    tab.index.name, tab.columns.name = "predicted", "expert"
    if normalize is None:
        return tab
    if normalize == "row":
        sums = tab.sum(axis=1).replace(0, np.nan)
        return tab.div(sums, axis=0)
    raise ValueError("normalize must be None or 'row'")


# ------------------------------------------------------- agreement


def agreement(a: Sequence[Any], b: Sequence[Any]) -> dict:
    """How much two sets of labels for the same records agree.

    Use for two classification runs, or the model against the expert, when the
    records were *not* sampled with unequal probabilities (for weighted
    agreement, weight the data first).

    * ``observed``: raw agreement, the share of records given the same label
      both times.
    * ``expected``: the agreement two labellers would reach by chance, given
      how often each used each label.
    * ``kappa`` (Cohen's kappa) = ``(observed - expected) / (1 - expected)``.
      1 means perfect agreement, 0 means no better than chance, negative means
      worse than chance. Raw agreement flatters when one label dominates;
      kappa corrects for that. If both labellers used a single, identical
      label throughout, chance agreement is 1 and kappa is undefined (NaN).
    * ``n``: number of records compared.
    """
    a = pd.Series(list(a))
    b = pd.Series(list(b))
    if len(a) != len(b):
        raise ValueError("the two label lists must have the same length")
    if len(a) == 0:
        raise ValueError("no records to compare")
    if a.isna().any() or b.isna().any():
        raise ValueError("labels contain missing values; resolve them first")
    n = len(a)
    observed = float((a.values == b.values).mean())
    pa = a.value_counts(normalize=True)
    pb = b.value_counts(normalize=True)
    expected = float(sum(pa.get(k, 0.0) * pb.get(k, 0.0) for k in set(pa.index) | set(pb.index)))
    kappa = float("nan") if np.isclose(expected, 1.0) else (observed - expected) / (1 - expected)
    return dict(n=n, observed=observed, expected=expected, kappa=kappa)
