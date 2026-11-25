"""Checks on the reader of the UNFCCC admitted NGO table (made-up organisations only)."""

import pytest

from cleaning.admitted_ngos import check, decode


def reply(items, dicts=None):
    select = [
        "ngo.Official Name", "ngo.URL", "ngo.Person", "ngo.City",
        "ngo.Country", "ngo.Constituency", "ngo.Business Role Name",
    ]
    shape = {"PH": [{"DM0": items}], "ValueDicts": dicts or {}}
    return {"results": [{"result": {"data": {
        "descriptor": {"Select": [{"Name": n, "Value": f"G{i}"} for i, n in enumerate(select)]},
        "dsr": {"DS": [shape]},
    }}}]}


SCHEMA = [{"N": f"G{i}", "T": 1, "DN": f"D{i}"} for i in range(7)]


def test_decode_handles_lists_repeats_and_empty_values():
    items = [
        {"S": SCHEMA, "C": ["Alpha Institute", "alpha.example", "A. Person", "Oslo", 0, 1, 0]},
        # R = 0b1110000: country, constituency and role repeat; Ø = 0b0000010: no website
        {"C": ["Beta Forum", "B. Person", "Bergen"], "R": 0b1110000, "Ø": 0b0000010},
    ]
    dicts = {"D4": ["Norway"], "D5": ["Youth", "Environmental"], "D6": ["NGO DCP"]}
    rows = decode(reply(items, dicts))
    assert rows[0]["country"] == "Norway" and rows[0]["constituency"] == "Environmental"
    assert rows[1] == {
        "official_name": "Beta Forum", "website": None, "contact_person": "B. Person",
        "city": "Bergen", "country": "Norway", "constituency": "Environmental", "role": "NGO DCP",
    }
    assert check(rows) == []


def test_decode_refuses_a_row_with_too_many_values():
    items = [{"S": SCHEMA, "C": ["A", "b", "c", "d", "e", "f", "g", "extra"]}]
    with pytest.raises(ValueError):
        decode(reply(items))


def test_check_reports_identical_rows_and_missing_names():
    row = dict.fromkeys(["official_name", "website", "contact_person", "city", "country", "constituency", "role"], "x")
    assert "two rows are identical" in check([row, dict(row)])
    assert "a row has no organisation name" in check([{**row, "official_name": None}])
