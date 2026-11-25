import numpy as np
import pandas as pd
import pytest

from analysis.sampling import stratified_sample
from analysis.stats import (
    RecallNotEstimable,
    accuracy_by_group,
    agreement,
    precision_recall_by_category,
    stratified_proportion,
    weighted_confusion_table,
    wilson_interval,
)

# ------------------------------------------------------------ Wilson


def test_wilson_known_values():
    lo, hi = wilson_interval(5, 10)
    assert lo == pytest.approx(0.2366, abs=5e-4)
    assert hi == pytest.approx(0.7634, abs=5e-4)
    lo, hi = wilson_interval(0, 10)
    assert lo == 0.0
    assert hi == pytest.approx(3.8416 / 13.8416, abs=1e-3)  # 0.2775
    lo, hi = wilson_interval(81, 263)  # textbook example (Wikipedia/Wilson)
    assert (lo, hi) == pytest.approx((0.2553, 0.3662), abs=1e-3)


def test_wilson_edges():
    lo, hi = wilson_interval(40, 40)
    assert hi == pytest.approx(1.0) and 0.89 < lo < 0.93
    assert wilson_interval(0, 0) == (0.0, 1.0)
    with pytest.raises(ValueError):
        wilson_interval(5, 3)


# ------------------------------------------------ stratified estimate


def test_stratified_proportion_known_case():
    # two strata, N = 100 and 300; 8/10 and 3/10 correct
    rows = [("a", 1)] * 8 + [("a", 0)] * 2 + [("b", 1)] * 3 + [("b", 0)] * 7
    s = pd.DataFrame(rows, columns=["stratum", "ok"])
    r = stratified_proportion(s, "stratum", "ok", {"a": 100, "b": 300})
    assert r["estimate"] == pytest.approx(0.25 * 0.8 + 0.75 * 0.3)
    assert 0 <= r["ci_low"] < r["estimate"] < r["ci_high"] <= 1
    # unweighted pooled share would be 0.55, clearly different
    assert abs(r["estimate"] - 0.55) > 0.1


def test_census_stratum_has_no_uncertainty():
    s = pd.DataFrame({"stratum": ["a"] * 5, "ok": [1, 1, 0, 1, 1]})
    r = stratified_proportion(s, "stratum", "ok", {"a": 5})
    assert r["estimate"] == 0.8 and r["ci_low"] == r["ci_high"] == 0.8


def test_n_equals_one_is_explicit_and_not_zero_variance():
    s = pd.DataFrame({"stratum": ["a", "a", "a", "a", "b"], "ok": [1, 1, 1, 1, 1]})
    r = stratified_proportion(s, "stratum", "ok", {"a": 100, "b": 100})
    assert r["estimate"] == 1.0
    assert r["ci_low"] < 0.95  # one record cannot prove stratum b is perfect
    assert any("n_h = 1" in n for n in r["notes"])


def test_empty_stratum_raises_or_bounds():
    s = pd.DataFrame({"stratum": ["a"] * 4, "ok": [1, 1, 0, 1]})
    pop = {"a": 100, "b": 100}
    with pytest.raises(ValueError, match="none were checked"):
        stratified_proportion(s, "stratum", "ok", pop)
    r = stratified_proportion(s, "stratum", "ok", pop, empty_strata="bound")
    assert np.isnan(r["estimate"])
    assert r["unobserved_weight"] == pytest.approx(0.5)
    assert r["ci_low"] < 0.4 and r["ci_high"] > 0.85
    assert any("unobserved" in n for n in r["notes"])


def test_bad_inputs():
    s = pd.DataFrame({"stratum": ["a", "a"], "ok": [1, 2]})
    with pytest.raises(ValueError, match="True/False"):
        stratified_proportion(s, "stratum", "ok", {"a": 10})
    s = pd.DataFrame({"stratum": ["a", "a", "a"], "ok": [1, 0, 1]})
    with pytest.raises(ValueError, match="larger than population"):
        stratified_proportion(s, "stratum", "ok", {"a": 2})


# --------------------------------------------- accuracy by group


def build_population(seed=11):
    """Synthetic population: predicted category x confidence, with a hidden truth."""
    rng = np.random.default_rng(seed)
    spec = {  # (pred, conf): (N, P(prediction right), P(truth is 'business' | wrong))
        ("business", "high"): (300, 0.95),
        ("business", "medium"): (150, 0.80),
        ("business", "low"): (60, 0.55),
        ("other", "high"): (400, 0.97),
        ("other", "medium"): (200, 0.85),
        ("other", "low"): (90, 0.60),
        ("none", "low"): (50, 0.90),
    }
    rows = []
    for (pred, conf), (n, acc) in spec.items():
        for _ in range(n):
            right = rng.random() < acc
            if right:
                truth = pred
            else:
                truth = rng.choice([c for c in ("business", "other", "none") if c != pred])
            rows.append((pred, conf, truth))
    df = pd.DataFrame(rows, columns=["pred", "conf", "truth"])
    df["correct"] = df["pred"] == df["truth"]
    return df


def test_accuracy_by_group_matches_manual_weighting():
    pop = build_population()
    sample, alloc = stratified_sample(pop, ["pred", "conf"], 250, seed=5, min_per_stratum=10)
    res = accuracy_by_group(sample, "conf", "correct").set_index("conf")
    # manual: weight each stratum's sample accuracy by N_h within the group
    for conf in ("high", "medium", "low"):
        sub = sample[sample["conf"] == conf]
        per = sub.groupby("stratum").agg(p=("correct", "mean"), N=("N_h", "first"))
        assert res.loc[conf, "accuracy"] == pytest.approx((per.p * per.N).sum() / per.N.sum())
    assert res.loc["ALL", "n_checked"] == 250
    assert res.loc["ALL", "N_population"] == len(pop)
    assert (res["ci_low"] <= res["accuracy"]).all() and (res["accuracy"] <= res["ci_high"]).all()
    # high confidence is truly more accurate and the estimate reflects that
    assert res.loc["high", "accuracy"] > res.loc["low", "accuracy"]


def test_accuracy_by_group_rejects_cross_cutting_groups():
    pop = build_population()
    sample, _ = stratified_sample(pop, ["pred", "conf"], 250, seed=5)
    with pytest.raises(ValueError, match="nested"):
        accuracy_by_group(sample, "truth", "correct")


# ----------------------------------------- precision and recall


def test_precision_recall_known_values_census():
    # Full census (n_h == N_h) so the answers are exact and checkable by hand.
    # predicted A: 10 records, 8 truly A, 2 truly B.  predicted B: 10 records, 1 truly A, 9 truly B.
    rows = (
        [("A", "A")] * 8 + [("A", "B")] * 2 + [("B", "A")] * 1 + [("B", "B")] * 9
    )
    s = pd.DataFrame(rows, columns=["pred", "truth"])
    s["stratum"] = s["pred"]
    res = precision_recall_by_category(s, "pred", "truth", population={"A": 10, "B": 10}).set_index("category")
    assert res.loc["A", "precision"] == pytest.approx(8 / 10)
    assert res.loc["A", "recall"] == pytest.approx(8 / 9)  # 9 true A, 8 found
    assert res.loc["B", "precision"] == pytest.approx(9 / 10)
    assert res.loc["B", "recall"] == pytest.approx(9 / 11)
    assert res.loc["A", "est_true_total"] == pytest.approx(9)


def test_recall_weights_predicted_negatives_by_population():
    # predicted A: 20 records (all checked, 20 truly A). predicted B: 1000 records,
    # 10 checked, 1 truly A -> about 100 missed A's. Recall A ~ 20/120.
    rows = [("A", "A")] * 20 + [("B", "A")] * 1 + [("B", "B")] * 9
    s = pd.DataFrame(rows, columns=["pred", "truth"])
    s["stratum"] = s["pred"]
    res = precision_recall_by_category(
        s, "pred", "truth", population={"A": 20, "B": 1000}, n_boot=500, seed=1
    ).set_index("category")
    assert res.loc["A", "recall"] == pytest.approx(20 / 120)
    assert res.loc["A", "recall_low"] < res.loc["A", "recall"] < res.loc["A", "recall_high"]


def test_recall_refused_without_predicted_negatives():
    s = pd.DataFrame({"pred": ["A"] * 6, "truth": ["A"] * 5 + ["B"]})
    s["stratum"] = "A"
    with pytest.raises(RecallNotEstimable, match="predicted-negatives"):
        precision_recall_by_category(s, "pred", "truth", population={"A": 6, "B": 50})


def test_recall_refused_when_a_negative_stratum_unchecked():
    s = pd.DataFrame({"pred": ["A"] * 4 + ["B"] * 4, "truth": ["A"] * 4 + ["B"] * 4})
    s["stratum"] = s["pred"]
    with pytest.raises(RecallNotEstimable):
        precision_recall_by_category(s, "pred", "truth", population={"A": 10, "B": 10, "C": 30})


def test_precision_recall_seeded_and_interval_reproducible():
    pop = build_population()
    sample, _ = stratified_sample(pop, ["pred"], 200, seed=9, min_per_stratum=20)
    r1 = precision_recall_by_category(sample, "pred", "truth", n_boot=400, seed=3)
    r2 = precision_recall_by_category(sample, "pred", "truth", n_boot=400, seed=3)
    r3 = precision_recall_by_category(sample, "pred", "truth", n_boot=400, seed=4)
    pd.testing.assert_frame_equal(r1, r2)
    assert not r1["recall_low"].equals(r3["recall_low"])


def test_stratified_by_confidence_too():
    pop = build_population()
    sample, _ = stratified_sample(pop, ["pred", "conf"], 250, seed=9, min_per_stratum=8)
    res = precision_recall_by_category(sample, "pred", "truth", n_boot=300, seed=1)
    assert res["precision"].between(0, 1).all() and res["recall"].between(0, 1).all()
    assert ((res["precision_low"] <= res["precision"]) & (res["precision"] <= res["precision_high"])).all()


# ------------------------------------------------ confusion table


def test_weighted_confusion_table():
    rows = [("A", "A")] * 3 + [("A", "B")] * 1 + [("B", "B")] * 2
    s = pd.DataFrame(rows, columns=["pred", "truth"])
    s["stratum"] = s["pred"]
    t = weighted_confusion_table(s, "pred", "truth", population={"A": 40, "B": 100})
    assert t.loc["A", "A"] == pytest.approx(30)
    assert t.loc["A", "B"] == pytest.approx(10)
    assert t.loc["B", "B"] == pytest.approx(100)
    assert t.values.sum() == pytest.approx(140)
    rn = weighted_confusion_table(s, "pred", "truth", population={"A": 40, "B": 100}, normalize="row")
    assert rn.loc["A", "A"] == pytest.approx(0.75)
    with pytest.raises(ValueError, match="no checked"):
        weighted_confusion_table(s, "pred", "truth", population={"A": 40, "B": 100, "C": 5})


# ----------------------------------------------------- agreement


def test_kappa_hand_computed():
    # 2x2: both yes 20, a yes/b no 5, a no/b yes 10, both no 15. n=50
    # observed = 35/50 = .7; a yes = 25, b yes = 30 -> expected = .5*.6 + .5*.4 = .5
    # kappa = (.7-.5)/(1-.5) = 0.4
    a = ["y"] * 20 + ["y"] * 5 + ["n"] * 10 + ["n"] * 15
    b = ["y"] * 20 + ["n"] * 5 + ["y"] * 10 + ["n"] * 15
    r = agreement(a, b)
    assert r["n"] == 50
    assert r["observed"] == pytest.approx(0.7)
    assert r["expected"] == pytest.approx(0.5)
    assert r["kappa"] == pytest.approx(0.4)


def test_kappa_extremes():
    assert agreement(list("abab"), list("abab"))["kappa"] == pytest.approx(1.0)
    assert agreement(list("aabb"), list("bbaa"))["kappa"] == pytest.approx(-1.0)
    assert np.isnan(agreement(["x"] * 4, ["x"] * 4)["kappa"])
    with pytest.raises(ValueError):
        agreement([1, 2], [1])


def test_kappa_multiclass():
    # 3 labels; hand check: a=[x,x,y,z], b=[x,y,y,z]; po=3/4
    # pa: x.5,y.25,z.25; pb: x.25,y.5,z.25; pe=.125+.125+.0625=.3125
    r = agreement(list("xxyz"), list("xyyz"))
    assert r["expected"] == pytest.approx(0.3125)
    assert r["kappa"] == pytest.approx((0.75 - 0.3125) / (1 - 0.3125))


# -------------------------------------------------- simulation


def test_interval_coverage_simulation():
    """Over repeated sampling, the 95% interval should contain the true accuracy ~95% of the time."""
    pop = build_population(seed=21)
    true_acc = pop["correct"].mean()
    hits = 0
    reps = 400
    for seed in range(reps):
        sample, _ = stratified_sample(
            pop, ["pred", "conf"], 250, seed=seed, min_per_stratum=10,
            oversample={("business", "low"): 3, ("other", "low"): 2},
        )
        r = stratified_proportion(sample, "stratum", "correct")
        hits += r["ci_low"] <= true_acc <= r["ci_high"]
    coverage = hits / reps
    print(f"\nMEASURED overall coverage: {coverage:.3f} over {reps} reps")
    assert 0.92 <= coverage <= 0.99


def test_interval_coverage_by_group_simulation():
    pop = build_population(seed=22)
    truth = pop.groupby("conf")["correct"].mean()
    hits = {k: 0 for k in truth.index}
    reps = 250
    for seed in range(reps):
        sample, _ = stratified_sample(pop, ["pred", "conf"], 250, seed=1000 + seed, min_per_stratum=10)
        res = accuracy_by_group(sample, "conf", "correct").set_index("conf")
        for k in truth.index:
            hits[k] += res.loc[k, "ci_low"] <= truth[k] <= res.loc[k, "ci_high"]
    cov = {k: v / reps for k, v in hits.items()}
    print(f"\nMEASURED by-confidence coverage over {reps} reps: {cov}")
    assert all(c >= 0.90 for c in cov.values())


def test_recall_bootstrap_coverage_simulation():
    pop = build_population(seed=23)
    cat = "business"
    true_recall = ((pop["pred"] == cat) & (pop["truth"] == cat)).sum() / (pop["truth"] == cat).sum()
    hits, reps = 0, 120
    for seed in range(reps):
        sample, _ = stratified_sample(pop, ["pred"], 250, seed=2000 + seed, min_per_stratum=20)
        r = precision_recall_by_category(sample, "pred", "truth", categories=[cat], n_boot=300, seed=seed)
        hits += r.loc[0, "recall_low"] <= true_recall <= r.loc[0, "recall_high"]
    cov = hits / reps
    print(f"\nMEASURED recall (bootstrap) coverage: {cov:.3f} over {reps} reps")
    assert cov >= 0.88
