from analysis import country_test as ct
from analysis import person_inputs as pi


def _row(name, title="", sheet="Party overflow"):
    return {"sheet": sheet, "Name": name, "Functional title": title, "Department": "",
            "Home organization": "An entry", "Relation": ""}


def test_youth_delegates_are_left_out_and_counted():
    rows = [_row("A"), _row("B", "Youth Delegate"), _row("C", "Jugenddelegierte")]
    made, skipped = pi.inputs(rows, ct.COUNTRIES["germany"], "G02", 6)
    assert (len(made), skipped) == (1, 2)


def test_cases_are_numbered_from_the_first_and_keep_the_origin_and_badge():
    made, _ = pi.inputs([_row("A"), _row("B", sheet="Parties")], ct.COUNTRIES["germany"], "G02", 6)
    assert [m["case"] for m in made] == ["PG6", "PG7"]
    assert {m["org_case"] for m in made} == {"G02"}
    assert [m["badge_type"] for m in made] == ["Party overflow", "Parties"]


def test_exact_repeats_get_different_row_ids():
    made, _ = pi.inputs([_row("A"), _row("A")], ct.COUNTRIES["germany"], "G02", 1)
    assert made[0]["row_id"] != made[1]["row_id"]
