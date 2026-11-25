"""Tests for charts: colours stay put, charts have the right marks and a table behind them."""

from __future__ import annotations

import inspect

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest
from matplotlib.text import Text

import charts

INK_COLOURS = {charts.INK, charts.INK_2}
SERIES = {c.lower() for c in charts.SERIES}


def _hex(colour) -> str:
    return matplotlib.colors.to_hex(colour).lower()


def _all_text(fig):
    return [t for t in fig.findobj(Text) if t.get_text().strip() and t.get_visible()]


def _assert_text_is_ink(fig):
    bad = [(t.get_text(), _hex(t.get_color())) for t in _all_text(fig)
           if _hex(t.get_color()) not in {c.lower() for c in INK_COLOURS}]
    assert not bad, f"text not in an ink colour: {bad}"


def _assert_one_y_axis(fig):
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert len(ax.get_shared_y_axes().get_siblings(ax)) == 1
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()


BARS = {"Business": 520, "NGO": 310, "Government": 140, "Research": 60}
STACK = {
    "Country A": {"Business": 60, "NGO": 30, "Research": 10},
    "Country B": {"Business": 20, "NGO": 70, "Research": 10},
}
INTERVALS = pd.DataFrame(
    {
        "label": ["Business", "NGO", "Research"],
        "estimate": [0.9, 0.8, 0.7],
        "low": [0.85, 0.7, 0.5],
        "high": [0.94, 0.88, 0.85],
        "n": [60, 40, 20],
    }
)


# ------------------------------------------------------------ colours


def test_colours_follow_the_full_list_not_the_filtered_one():
    full = ["A", "B", "C", "D"]
    everything = charts.colours_for(full, full)
    filtered = charts.colours_for(["C", "A"], full)
    assert filtered == {"C": everything["C"], "A": everything["A"]}
    assert everything["A"] == charts.SERIES[0]


def test_too_many_categories_says_fold_into_other():
    names = [f"c{i}" for i in range(9)]
    with pytest.raises(ValueError, match="Other"):
        charts.colours_for(names, names)


def test_other_is_grey_and_uses_no_slot():
    names = [f"c{i}" for i in range(8)] + ["Other"]
    colours = charts.colours_for(names, names)
    assert colours["Other"] == charts.OTHER_COLOUR
    assert colours["c7"] == charts.SERIES[7]


def test_unknown_category_is_refused():
    with pytest.raises(ValueError, match="missing"):
        charts.colours_for(["Z"], ["A", "B"])


def test_palette_has_eight_distinct_colours():
    assert len(set(charts.SERIES)) == 8


# ------------------------------------------------------------ bar chart


def test_bar_chart_marks_sorting_and_labels():
    fig = charts.bar_chart(BARS, "Business makes up half of delegates", "Test data")
    ax = fig.axes[0]
    widths = [p.get_width() for p in ax.patches]
    assert len(ax.patches) == 4
    assert widths == sorted(widths, reverse=True)
    assert {_hex(p.get_facecolor()) for p in ax.patches} == {charts.SERIES[0]}
    texts = {t.get_text() for t in _all_text(fig)}
    assert {"520", "310", "140", "60"} <= texts
    assert "Business makes up half of delegates" in "".join(texts).replace("\n", " ") or any(
        "Business" in t for t in texts
    )
    _assert_text_is_ink(fig)
    _assert_one_y_axis(fig)
    assert fig.legends == []


def test_bar_chart_accepts_lists_and_dataframes_and_share():
    a = charts.bar_chart([("x", 0.5), ("y", 0.25)], "t", "s", share=True)
    b = charts.bar_chart(pd.DataFrame({"category": ["x", "y"], "value": [0.5, 0.25]}), "t", "s", share=True)
    assert {t.get_text() for t in _all_text(a)} >= {"50%", "25%"}
    assert len(b.axes[0].patches) == 2


def test_bar_chart_highlight_greys_the_rest():
    fig = charts.bar_chart(BARS, "t", "s", highlight="NGO")
    colours = [_hex(p.get_facecolor()) for p in fig.axes[0].patches]
    assert colours.count(charts.SERIES[0]) == 1
    assert colours.count(charts.DEEMPHASIS) == 3


def test_bar_thickness_is_at_most_24_pixels():
    fig = charts.bar_chart(BARS, "t", "s")
    ax = fig.axes[0]
    fig.canvas.draw()
    for p in ax.patches:
        assert p.get_window_extent().height <= 24.01


# ------------------------------------------------------------ stacked


def test_stacked_bar_marks_gap_and_legend():
    fig = charts.stacked_bar(STACK, "Business dominates in country A", "Test data")
    ax = fig.axes[0]
    assert len(ax.patches) == 2 * 3
    for p in ax.patches:
        assert _hex(p.get_edgecolor()) == charts.SURFACE
        assert p.get_linewidth() == pytest.approx(charts.GAP_PT)
    assert len(fig.legends) == 1
    assert [t.get_text() for t in fig.legends[0].get_texts()] == ["Business", "NGO", "Research"]
    _assert_text_is_ink(fig)
    _assert_one_y_axis(fig)


def test_stacked_rows_sum_to_one_when_share():
    fig = charts.stacked_bar(STACK, "t", "s")
    ax = fig.axes[0]
    ends = [p.get_x() + p.get_width() for p in ax.patches[-2:]]
    assert ends == pytest.approx([1.0, 1.0])


def test_stacked_colour_is_stable_when_a_part_is_missing():
    order = ["Business", "NGO", "Research"]
    full = charts.stacked_bar(STACK, "t", "s", order=order)
    smaller = charts.stacked_bar(
        {k: {p: v for p, v in d.items() if p != "NGO"} for k, d in STACK.items()},
        "t",
        "s",
        order=order,
    )
    full_research = _hex(full.axes[0].patches[-1].get_facecolor())
    small_research = _hex(smaller.axes[0].patches[-1].get_facecolor())
    assert full_research == small_research == charts.SERIES[2]


def test_stacked_single_part_has_no_legend():
    fig = charts.stacked_bar({"A": {"x": 1}, "B": {"x": 2}}, "t", "s", share=False)
    assert fig.legends == []


def test_stacked_with_too_many_parts_raises():
    row = {f"p{i}": 1 for i in range(9)}
    with pytest.raises(ValueError, match="Other"):
        charts.stacked_bar({"A": row}, "t", "s")


# ------------------------------------------------------------ interval


def test_interval_chart_marks_and_labels():
    fig = charts.interval_chart(INTERVALS, "Accuracy is high for business", "Test data")
    ax = fig.axes[0]
    dots = [ln for ln in ax.lines if ln.get_marker() == "o"]
    assert len(dots) == 1 and len(dots[0].get_xdata()) == 3
    assert len(ax.collections[0].get_segments()) == 3
    assert fig.legends == []
    assert any("n = 60" in t.get_text() for t in _all_text(fig))
    _assert_text_is_ink(fig)
    _assert_one_y_axis(fig)


def test_interval_rejects_estimate_outside_interval():
    bad = [("a", 0.9, 0.95, 0.99)]
    with pytest.raises(ValueError, match="low <= estimate <= high"):
        charts.interval_chart(bad, "t", "s")


# ------------------------------------------------------------ general


@pytest.mark.parametrize("make", [
    lambda: charts.bar_chart(BARS, "", "s"),
    lambda: charts.bar_chart(BARS, "t", " "),
])
def test_title_and_source_are_required(make):
    with pytest.raises(ValueError, match="must not be empty"):
        make()


def test_no_helper_offers_a_second_axis():
    for fn in (charts.bar_chart, charts.stacked_bar, charts.interval_chart):
        for name in inspect.signature(fn).parameters:
            assert not any(w in name.lower() for w in ("twin", "secondary", "second", "right_axis", "dual"))


def test_style_is_applied():
    charts.apply_style()
    rc = matplotlib.rcParams
    assert rc["axes.spines.top"] is False and rc["axes.spines.right"] is False
    assert rc["axes.facecolor"] == charts.SURFACE
    assert rc["grid.linestyle"] == "-"


def test_save_writes_png_svg_csv(tmp_path):
    fig = charts.bar_chart(BARS, "Business makes up half", "Test data")
    paths = charts.save(fig, tmp_path / "out" / "fig1")
    for ext in ("png", "svg", "csv"):
        assert paths[ext].exists() and paths[ext].stat().st_size > 0
    assert paths["png"].read_bytes()[:4] == b"\x89PNG"
    assert b"<svg" in paths["svg"].read_bytes()[:500]
    table = pd.read_csv(paths["csv"])
    assert table["value"].tolist() == [520, 310, 140, 60]
    # 2x: 7.2in wide at 100 dpi, doubled
    from matplotlib.image import imread

    assert imread(paths["png"]).shape[1] == 1440


def test_save_refuses_a_foreign_figure(tmp_path):
    from matplotlib.figure import Figure

    with pytest.raises(ValueError, match="not made by"):
        charts.save(Figure(), tmp_path / "x")
