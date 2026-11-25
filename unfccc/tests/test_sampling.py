import numpy as np
import pandas as pd
import pytest

from analysis.sampling import expected_margin_of_error, stratified_sample


def make_population(seed=1):
    rng = np.random.default_rng(seed)
    sizes = {
        ("business", "high"): 300,
        ("business", "medium"): 150,
        ("business", "low"): 60,
        ("other", "high"): 400,
        ("other", "medium"): 200,
        ("other", "low"): 90,
        ("unknown", "low"): 50,
    }
    rows = []
    for (cat, conf), n in sizes.items():
        rows += [(cat, conf)] * n
    df = pd.DataFrame(rows, columns=["pred", "conf"])
    df["id"] = np.arange(len(df))
    return df.sample(frac=1, random_state=rng.integers(1e6)).reset_index(drop=True)


def test_sizes_sum_and_never_exceed_stratum():
    pop = make_population()
    sample, alloc = stratified_sample(pop, ["pred", "conf"], 250, seed=7, min_per_stratum=10)
    assert len(sample) == 250
    assert alloc["n_h"].sum() == 250
    assert (alloc["n_h"] <= alloc["N_h"]).all()
    assert (alloc["n_h"] >= 10).all()
    # table agrees with the sample rows
    assert sample.groupby("stratum").size().to_dict() == dict(zip(alloc["stratum"], alloc["n_h"]))
    assert sample["N_h"].eq(sample["stratum"].map(dict(zip(alloc["stratum"], alloc["N_h"])))).all()
    assert sample["id"].is_unique


def test_proportional_when_no_floor_binds():
    pop = make_population()
    _, alloc = stratified_sample(pop, ["pred", "conf"], 250, seed=1, min_per_stratum=0)
    expected = 250 * alloc["N_h"] / alloc["N_h"].sum()
    assert (alloc["n_h"] - expected).abs().max() < 1.0


def test_floor_lifts_small_strata():
    pop = make_population()
    _, alloc = stratified_sample(pop, ["pred", "conf"], 100, seed=1, min_per_stratum=12)
    assert alloc.set_index("stratum").loc["unknown|low", "n_h"] >= 12
    assert alloc["n_h"].sum() == 100


def test_small_stratum_taken_whole_and_capped():
    pop = make_population().iloc[:0]
    pop = pd.DataFrame({"g": ["a"] * 100 + ["b"] * 3})
    sample, alloc = stratified_sample(pop, ["g"], 20, seed=2, min_per_stratum=5)
    b = alloc.set_index("stratum").loc["b"]
    assert b["n_h"] == 3 and b["N_h"] == 3
    assert alloc["n_h"].sum() == 20


def test_oversample_raises_share():
    pop = make_population()
    _, base = stratified_sample(pop, ["pred", "conf"], 250, seed=3, min_per_stratum=5)
    _, over = stratified_sample(
        pop, ["pred", "conf"], 250, seed=3, min_per_stratum=5,
        oversample={("business", "low"): 4, "other|low": 3},
    )
    b = base.set_index("stratum")["n_h"]
    o = over.set_index("stratum")["n_h"]
    assert o["business|low"] > b["business|low"]
    assert o["other|low"] > b["other|low"]
    assert o.sum() == 250


def test_oversample_unknown_key_errors():
    pop = make_population()
    with pytest.raises(ValueError, match="matches no stratum"):
        stratified_sample(pop, ["pred", "conf"], 100, seed=1, oversample={"nope|high": 2})


def test_impossible_requests_error():
    pop = pd.DataFrame({"g": ["a"] * 10 + ["b"] * 10})
    with pytest.raises(ValueError):
        stratified_sample(pop, ["g"], 25, seed=1)  # more than population
    with pytest.raises(ValueError):
        stratified_sample(pop, ["g"], 5, seed=1, min_per_stratum=5)  # floors exceed total


def test_missing_strata_values_refused():
    pop = pd.DataFrame({"g": ["a", None, "b"]})
    with pytest.raises(ValueError, match="missing"):
        stratified_sample(pop, ["g"], 2, seed=1)


def test_reproducible_same_seed_different_seed_differs():
    pop = make_population()
    s1, a1 = stratified_sample(pop, ["pred", "conf"], 250, seed=42)
    s2, a2 = stratified_sample(pop, ["pred", "conf"], 250, seed=42)
    s3, _ = stratified_sample(pop, ["pred", "conf"], 250, seed=43)
    pd.testing.assert_frame_equal(s1, s2)
    pd.testing.assert_frame_equal(a1, a2)
    assert set(s1["id"]) != set(s3["id"])


def test_input_not_modified():
    pop = make_population()
    before = pop.copy()
    stratified_sample(pop, ["pred", "conf"], 100, seed=1)
    pd.testing.assert_frame_equal(pop, before)


def test_margin_of_error_known_values():
    # one stratum, N=1000, n=250: 1.96*sqrt(.25/250*(1-.25)) = 0.0536
    alloc = pd.DataFrame({"stratum": ["a"], "N_h": [1000], "n_h": [250]})
    moe = expected_margin_of_error(alloc)
    assert moe.loc[0, "margin_of_error"] == pytest.approx(1.959964 * np.sqrt(0.25 / 250 * 0.75), rel=1e-5)
    assert moe.loc[1, "stratum"] == "ALL"
    assert moe.loc[1, "margin_of_error"] == pytest.approx(moe.loc[0, "margin_of_error"])


def test_margin_of_error_census_and_empty():
    alloc = pd.DataFrame({"stratum": ["a", "b"], "N_h": [10, 20], "n_h": [10, 0]})
    moe = expected_margin_of_error(alloc).set_index("stratum")["margin_of_error"]
    assert moe["a"] == 0.0
    assert np.isinf(moe["b"]) and np.isinf(moe["ALL"])


def test_margin_of_error_design_report():
    pop = make_population()
    _, alloc = stratified_sample(pop, ["pred", "conf"], 250, seed=1, min_per_stratum=10)
    moe = expected_margin_of_error(alloc)
    assert len(moe) == len(alloc) + 1
    overall = moe.iloc[-1]["margin_of_error"]
    assert 0 < overall < 0.06  # about +/-4% for ~250 of 1250
    assert (moe.iloc[:-1]["margin_of_error"] > overall).all()
