"""Synthetic-string tests for cleaning.clean. No real data."""

import pandas as pd

from cleaning.clean import (
    add_row_ids,
    ascii_fold,
    clean_series_steps,
    clean_text,
    collapse_whitespace,
    is_placeholder,
    normalise_unicode,
    person_key,
)


def test_unicode_and_whitespace():
    assert collapse_whitespace("  a   b\t c ") == "a b c"
    assert normalise_unicode("Café​") == "Café"
    assert clean_text("  Acme  Corp ") == "Acme Corp"


def test_placeholders_become_empty():
    for v in ["-", "//", "n/a", "N/A", "", "   ", None]:
        assert clean_text(v) is None
    assert not is_placeholder("Acme")


def test_ascii_fold():
    assert ascii_fold("Ångström") == "Angstrom"


def test_series_steps_columns():
    out = clean_series_steps(pd.Series([" A  b ", "-", None]))
    assert {"unicode", "whitespace", "final"} <= set(out.columns)
    assert out["final"].iloc[0] == "A b"
    assert pd.isna(out["final"].iloc[1]) and pd.isna(out["final"].iloc[2])


def test_person_key_is_opaque_and_order_insensitive():
    k = person_key("Jane Q Example", "Utopia")
    assert "example" not in str(k).lower()
    assert k == person_key("Example Jane Q", "Utopia")
    assert k != person_key("Jane Q Example", "Elsewhere")


def test_row_ids_unique_for_identical_rows():
    df = pd.DataFrame({"a": ["x", "x", "y"], "badge_type": ["Party"] * 3})
    out = add_row_ids(df, ["a"])
    assert out["row_id"].is_unique
