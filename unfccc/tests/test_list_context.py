"""The list's own context for one entry (codebook I4): counts only, never a name."""
from analysis import list_context as lc


def _row(sheet="Parties", country="X", entry="Abc", title="Adviser", name="A Person"):
    return {"Nominated by": country, "sheet": sheet, "Department": entry, "Name": name,
            "Functional title": title, "Home organization": "", "Relation": "",
            "Type of home organization": "", "Funding source": "", "Type of funding source": ""}


def test_entry_rows_match_without_case_or_outer_spaces_and_skip_other_sheets():
    raw = [_row(entry=" ABC "), _row(entry="abc", sheet="Party overflow"),
           _row(entry="abc", sheet="Observers"), _row(entry="abc", country="Y"),
           _row(entry="abcd")]
    rows = lc.entry_rows(raw, "X", "Department", {"Abc"})
    assert [r["sheet"] for r in rows] == ["Parties", "Party overflow"]


def test_counts_fold_single_values_and_never_carry_a_name():
    rows = [_row(title="Adviser"), _row(title=" adviser "), _row(title="Engineer"),
            _row(title="", sheet="Party overflow")]
    out = lc.counts(rows)
    assert out["delegates"] == 4
    assert out["badges"] == {"party": 3, "overflow": 1}
    assert out["columns"]["Functional title"] == {"adviser": 2, lc.SINGLE: 2}
    assert out["columns"]["Relation"] == {lc.BLANK: 4}
    assert "Name" not in out["columns"]
    assert "a person" not in str(out).casefold()


def test_counts_of_each_column_sum_to_the_delegates():
    rows = [_row(title=t) for t in ("a", "a", "b", "c", "c", "c")]
    out = lc.counts(rows)
    assert all(sum(col.values()) == 6 for col in out["columns"].values())
