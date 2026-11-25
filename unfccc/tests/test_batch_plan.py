import pandas as pd

from analysis import batch_plan as B


def _delegates() -> pd.DataFrame:
    rows = []

    def add(country, org, n=1, badge="Party"):
        rows.extend({"nominated_by_clean": country, "org_id": org, "badge_type": badge}
                    for _ in range(n))

    add("Germany", "shared-with-germany")
    add("Malta", "shared-with-germany")          # already searched: not counted again
    add("Malta", "m1", n=2, badge="Party overflow")
    add("Malta", None)                           # a row with no organisation
    for i in range(B.SMALL_MAX + 1):             # one more than the small limit: medium
        add("Belgium", f"b{i}")
    add("Belgium", "m1")                         # met in wave 1 first
    for i in range(B.SMALL_MAX + 3):             # medium, and the largest: first medium wave
        add("Portugal", f"p{i}")
    for i in range(B.SMALL_MAX + 1):             # medium, smallest: joins the lighter wave
        add("Denmark", f"d{i}", n=1)
    add("France", "f1")
    add("France", "b0")                          # met here first, before Belgium
    add("Italy", "i1")
    add("Italy", "f1")                           # met in wave 2 first
    return pd.DataFrame(rows)


def test_by_delegation_counts_rows_and_distinct_organisations():
    t = B.by_delegation(_delegates()).set_index("nominated_by_clean")
    assert t.loc["Malta"].to_dict() == {"delegates": 4, "overflow": 2, "no_organisation": 1,
                                        "organisations": 2}


def test_wave_of_leaves_out_finished_delegations_and_orders_the_rest():
    w = B.wave_of(B.by_delegation(_delegates()))
    assert w == {"Malta": 1, "France": 2, "Italy": 3, "Portugal": 4, "Belgium": 5, "Denmark": 5}


def test_waves_count_a_shared_organisation_once_in_the_earliest_wave():
    w = B.waves(_delegates()).set_index("wave")
    assert w["organisations_to_search"].to_dict() == {
        1: 1, 2: 2, 3: 1, 4: B.SMALL_MAX + 3, 5: 2 * B.SMALL_MAX + 1}
    assert w.loc[1, "delegates"] == 4 and w.loc[1, "no_organisation_rows"] == 1
    assert w.loc[4, "batches_of_10"] == 3
