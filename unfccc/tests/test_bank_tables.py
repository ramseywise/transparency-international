"""Checks on reading the Banking on Climate Chaos sector league tables."""

import pytest

from cleaning.bank_tables import PDF, SECTORS, check, clean_name, parse_number, read_tables


@pytest.mark.parametrize(
    "cell, value",
    [
        ("$3 6\n.", 3.6),
        ("$243 3\n.", 243.3),
        ("+$1 1 B\n.", 1.1),
        ("$1 0 B\n- .", -1.0),
        ("32 6%\n.", 32.6),
        ("12 5%\n- .", -12.5),
        ("12%\n-", -12.0),
        ("103%", 103.0),
        ("-", None),
        (None, None),
    ],
)
def test_parse_number(cell, value):
    assert parse_number(cell) == value


def test_parse_number_refuses_what_it_cannot_read():
    with pytest.raises(ValueError):
        parse_number("n/a")


def test_clean_name_joins_cut_words_and_keeps_real_spaces():
    assert clean_name("Toronto-Dominio\nn Bank") == "Toronto-Dominion Bank"
    assert clean_name("Bank of\nCommunication\ns") == "Bank of Communications"
    assert clean_name("Industrial and\nCommercial Bank\nof China") == "Industrial and Commercial Bank of China"


@pytest.mark.skipif(not PDF.exists(), reason="the source PDF is not in this checkout")
def test_tables_agree_with_their_own_totals():
    rows, totals = read_tables()
    assert check(rows, totals) == []
    assert {r["sector"] for r in rows} == set(SECTORS)
    assert len(rows) == 3 * 65


def test_check_reports_a_row_that_does_not_add_up():
    row = {"sector": SECTORS[0], "rank_2025": 1, "bank": "Example Bank", "usd_bn_total_2021_2025": 9.0}
    row.update({f"usd_bn_{y}": 1.0 for y in ("2021", "2022", "2023", "2024", "2025")})
    assert any("do not add up" in p for p in check([row], []))
