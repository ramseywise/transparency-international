import pandas as pd

from analysis import pilot


def table(n=300):
    names = []
    kinds = ["Stadtwerke X{}", "Bundesverband Y{}", "Ministry of Z{}", "Acme{} GmbH",
             "Stiftung Q{}", "Chamber of Commerce R{}", "Some Body {}", "Trade Union U{}"]
    for i in range(n):
        names.append(kinds[i % len(kinds)].format(i))
    t = pd.DataFrame({
        "org_id": [f"o{i:04d}" for i in range(n)],
        "canonical_name": names,
        "country_context": "DE",
        "name_cue": ["other" if i % 2 else "company legal form" for i in range(n)],
    })
    t["hard_case_cue"] = [pilot.hard_case_cue(x) for x in t["canonical_name"]]
    return t


def test_hard_case_cues():
    assert pilot.hard_case_cue("Stadtwerke München") == "municipal_utility"
    assert pilot.hard_case_cue("KfW Development Bank") == "public_development_bank"
    assert pilot.hard_case_cue("Deutscher Bundestag") == "parliament"
    assert pilot.hard_case_cue("Chamber of Commerce Vienna") == "private_law_chamber"
    assert pilot.hard_case_cue("Landwirtschaftskammer NRW") == "public_law_chamber"
    assert pilot.hard_case_cue("Acme GmbH") == "none"
    assert pilot.hard_case_cue("") == "none"


def test_pilot_draw_is_seeded_and_disjoint():
    t = table()
    tests = pilot.test_set_candidates(t, exclude=set())
    a, rec = pilot.draw_pilot(t, exclude=set(tests["org_id"]))
    b, _ = pilot.draw_pilot(t, exclude=set(tests["org_id"]))
    assert a.equals(b)
    assert not set(a["org_id"]) & set(tests["org_id"])
    assert a["org_id"].is_unique
    assert (a["part"] == "random").sum() == 50
    assert rec["hard_cases"] <= 25 and rec["random"] == 50
    assert rec["excluded"] == len(tests)
    assert (a.loc[a["part"] != "random", "hard_case_cue"] != "none").all()


def test_test_set_size_and_spread():
    t = table()
    tests = pilot.test_set_candidates(t, exclude={"o0000"})
    assert len(tests) <= 50 and tests["org_id"].is_unique
    assert "o0000" not in set(tests["org_id"])
    assert tests["why"].str.startswith("hard case").any()
    assert tests["why"].str.startswith("name cue").any()


def test_hard_cases_capped_per_cue():
    t = table()
    p, rec = pilot.draw_pilot(t, exclude=set())
    assert max(rec["hard_cases_by_cue"].values()) <= pilot.HARD_PER_CUE
