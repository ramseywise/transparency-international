"""One look for every chart in every study.

The aim: a chart made for the climate-conference study and a chart made for a
later study look like they belong to the same report, and a reader with
colour-blindness or a black-and-white printout can still read them.

What is fixed here, so nobody has to decide it chart by chart:

* a palette of eight category colours in a fixed order (the order is what keeps
  neighbouring colours distinguishable, so it never changes);
* one blue ramp for "how much", and a blue-to-red pair with a grey middle for
  "which side of a baseline" (use them only for those jobs);
* text is always dark grey or black, never in a series colour; the colour of a
  bar sits in the bar, or in the small swatch of the legend;
* thin bars, hairline grid, no top or right frame line;
* no chart with two vertical scales. Two quantities of different size need two
  charts. There is deliberately no option for a second axis.

Every helper takes a title that states the finding (for example "Business
groups make up half of the delegates", not "Delegates by type"), a source note,
and returns a matplotlib ``Figure``. ``save`` writes the PNG for the report,
the SVG for the web article, and a CSV of the plotted numbers, so every chart
has a table behind it.

Colours were checked with the dataviz palette checker (light background). The
eight-colour order passes for bars, stacks and lines, where only neighbours
touch. It does NOT pass for scatter plots or maps, where any two colours can
touch: use at most three categories there. There is no dark-mode version.
"""

from __future__ import annotations

import io
import math
import textwrap
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import pandas as pd
from cycler import cycler
from matplotlib import rcParams
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator

__all__ = [
    "SURFACE",
    "INK",
    "INK_2",
    "MUTED",
    "GRID",
    "AXIS",
    "SERIES",
    "OTHER_NAME",
    "OTHER_COLOUR",
    "DEEMPHASIS",
    "SEQUENTIAL",
    "DIVERGING_LOW",
    "DIVERGING_MID",
    "DIVERGING_HIGH",
    "apply_style",
    "colours_for",
    "bar_chart",
    "stacked_bar",
    "interval_chart",
    "save",
]

# ---------------------------------------------------------------- palette

SURFACE = "#fcfcfb"  # chart background
INK = "#0b0b0b"  # titles, value labels
INK_2 = "#52514e"  # axis text, legend text, source note
MUTED = "#898781"  # decoration only, never used for small text
GRID = "#e1e0d9"  # hairline grid
AXIS = "#c3c2b7"  # baseline

# Fixed order: blue, orange, aqua, yellow, magenta, green, violet, red.
SERIES: tuple[str, ...] = (
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#6250d6",
    "#e34948",
)

OTHER_NAME = "Other"
OTHER_COLOUR = MUTED  # the "Other" bucket is always grey, whatever else is shown
DEEMPHASIS = AXIS  # the grey for "everything except the one we are talking about"

# One hue, light (little) to dark (a lot). Steps of the blue ramp.
SEQUENTIAL: tuple[str, ...] = (
    "#cde2fb",
    "#9ec5f4",
    "#6da7ec",
    "#3987e5",
    "#256abf",
    "#184f95",
    "#0d366b",
)

# Two opposite poles with a neutral grey between them (nothing / no difference).
DIVERGING_LOW = "#2a78d6"
DIVERGING_MID = "#f0efec"
DIVERGING_HIGH = "#e34948"

# ---------------------------------------------------------------- sizes

DPI = 100  # on-screen size; saved PNGs are written at twice this
WIDTH_IN = 7.2
GAP_PT = 2 * 72 / DPI  # a 2-pixel gap, in points
HAIRLINE_PT = 72 / DPI  # 1 pixel
_ROW_PITCH_IN = 0.42  # one bar per row; bars are 23 px thick (limit 24)
_BAR_THICKNESS = 0.55
_FONT = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


def apply_style() -> None:
    """Set matplotlib's defaults to the house look (called by every helper)."""
    rcParams.update(
        {
            "figure.dpi": DPI,
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "savefig.edgecolor": SURFACE,
            "font.family": "sans-serif",
            "font.sans-serif": _FONT,
            "text.color": INK,
            "font.size": 10,
            "axes.edgecolor": AXIS,
            "axes.linewidth": HAIRLINE_PT,
            "axes.labelcolor": INK_2,
            "axes.labelsize": 9.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.bottom": False,
            "axes.grid": True,
            "axes.grid.axis": "x",
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": HAIRLINE_PT,
            "grid.linestyle": "-",
            "xtick.color": INK_2,
            "ytick.color": INK_2,
            "xtick.labelcolor": INK_2,
            "ytick.labelcolor": INK_2,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 10,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "xtick.major.pad": 6,
            "ytick.major.pad": 6,
            "axes.prop_cycle": cycler(color=list(SERIES)),
            "lines.linewidth": 2 * 72 / DPI,
            "legend.frameon": False,
            "legend.labelcolor": INK_2,
            "legend.fontsize": 9.5,
            "svg.fonttype": "path",
        }
    )


# ---------------------------------------------------------------- colours


def colours_for(categories: Sequence[str], order: Sequence[str] | None = None) -> dict[str, str]:
    """Give each category its colour, the same every time.

    ``order`` is the full list of every category the study ever shows, in the
    order you want them coloured. A colour belongs to a category's place in that
    list, not to its place on this chart, so filtering out a category never
    repaints the others. If ``order`` is left out, ``categories`` is taken as the
    full list.

    A category called "Other" is always grey and does not use up a slot. If
    there are more than eight other categories, an error asks you to fold the
    small ones into "Other" (adding more colours would make them
    indistinguishable).
    """
    full = list(order) if order is not None else list(categories)
    if len(set(full)) != len(full):
        raise ValueError("the ordered list of categories contains a repeated name")
    named = [c for c in full if c != OTHER_NAME]
    if len(named) > len(SERIES):
        raise ValueError(
            f"{len(named)} categories but only {len(SERIES)} colours can be told apart. "
            f"Fold the smallest into a single '{OTHER_NAME}' category "
            "(or split the chart into several) before charting."
        )
    colour_of = {c: SERIES[i] for i, c in enumerate(named)}
    colour_of[OTHER_NAME] = OTHER_COLOUR
    missing = [c for c in categories if c not in colour_of]
    if missing:
        raise ValueError(f"categories missing from the ordered list: {missing}")
    return {c: colour_of[c] for c in categories}


# ---------------------------------------------------------------- layout


def _new_figure() -> Figure:
    apply_style()
    fig = Figure(figsize=(WIDTH_IN, 3), dpi=DPI, facecolor=SURFACE)
    FigureCanvasAgg(fig)

    def _repr_png_() -> bytes:  # so notebooks show the chart without pyplot
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=DPI * 2)
        return buf.getvalue()

    fig._repr_png_ = _repr_png_  # type: ignore[attr-defined]
    return fig


def _width_in(fig: Figure, text: str, size: float, weight: str = "normal") -> float:
    t = fig.text(0, 0, text, fontsize=size, fontweight=weight)
    w = t.get_window_extent(fig.canvas.get_renderer()).width / fig.dpi
    t.remove()
    return w


def _need(text: str, name: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{name} must not be empty: every chart needs one")
    return text.strip()


def _frame(
    title: str,
    source: str,
    labels: Sequence[str],
    legend: Sequence[tuple[str, str]],
    right_pad_in: float,
    x_label: str | None,
):
    """Build the figure and its one axes. Returns ``(fig, ax, wrapped_labels)``."""
    title = _need(title, "title")
    source = _need(source, "source")
    if not source.lower().startswith("source"):
        source = "Source: " + source
    fig = _new_figure()
    wrapped = [textwrap.fill(str(s), 30) for s in labels]
    left_in = min(3.2, max(_width_in(fig, s, 10) for ln in wrapped for s in ln.split("\n")) + 0.3)
    left_in = max(left_in, 0.5)
    margin = 0.3
    text_w = WIDTH_IN - 2 * margin

    title_lines = textwrap.wrap(title, 62) or [title]
    source_lines = textwrap.wrap(source, 105)
    title_h = 0.1 + 0.27 * len(title_lines)

    legend_h, ncol = 0.0, 1
    if len(legend) >= 2:
        entry = max(_width_in(fig, n, 9.5) for n, _ in legend) + 0.45
        ncol = max(1, min(len(legend), int(text_w // entry)))
        legend_h = 0.28 * math.ceil(len(legend) / ncol) + 0.08

    plot_h = len(labels) * _ROW_PITCH_IN
    axis_h = 0.34 + (0.26 if x_label else 0)
    source_h = 0.14 * len(source_lines) + 0.22
    top = 0.22
    height = top + title_h + legend_h + plot_h + axis_h + source_h
    fig.set_size_inches(WIDTH_IN, height)

    def fy(inches_from_top: float) -> float:
        return 1 - inches_from_top / height

    fig.text(
        margin / WIDTH_IN,
        fy(top),
        "\n".join(title_lines),
        fontsize=14,
        fontweight="bold",
        color=INK,
        va="top",
        ha="left",
        linespacing=1.25,
    )
    if len(legend) >= 2:
        handles = [Patch(facecolor=c, edgecolor="none", label=n) for n, c in legend]
        fig.legend(
            handles=handles,
            loc="upper left",
            bbox_to_anchor=(margin / WIDTH_IN, fy(top + title_h)),
            ncol=ncol,
            borderaxespad=0,
            borderpad=0,
            handlelength=1.1,
            handleheight=1.0,
            columnspacing=1.6,
            labelcolor=INK_2,
        )
    ax = fig.add_axes(
        [
            left_in / WIDTH_IN,
            (source_h + axis_h) / height,
            (WIDTH_IN - left_in - right_pad_in) / WIDTH_IN,
            plot_h / height,
        ]
    )
    fig.text(
        margin / WIDTH_IN,
        source_h / height - 0.08 / height,
        "\n".join(source_lines),
        fontsize=8.5,
        color=INK_2,
        va="top",
        ha="left",
    )
    if x_label:
        ax.set_xlabel(x_label, color=INK_2, labelpad=6)
    n = len(labels)
    ax.set_ylim(n - 0.5 - 0.0, -0.5)  # first row at the top
    ax.set_yticks(range(n))
    ax.set_yticklabels(wrapped, color=INK_2)
    ax.yaxis.grid(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(AXIS)
    return fig, ax, wrapped


def _pairs(data, columns: Sequence[str]) -> pd.DataFrame:
    """Turn a DataFrame, a dict ``{name: value}`` or a list of tuples into a table."""
    if isinstance(data, pd.DataFrame):
        if data.shape[1] < len(columns):
            raise ValueError(f"need {len(columns)} columns: {list(columns)}")
        if all(c in data.columns for c in columns):
            out = data.loc[:, list(columns)].copy()
        else:
            out = data.iloc[:, : len(columns)].copy()
            out.columns = list(columns)
        return out.reset_index(drop=True)
    if isinstance(data, Mapping):
        return pd.DataFrame({columns[0]: list(data.keys()), columns[1]: list(data.values())})
    return pd.DataFrame(list(data), columns=list(columns))


def _fmt_count(v: float) -> str:
    return f"{v:,.0f}"


def _fmt_share(v: float) -> str:
    return f"{v:.1%}" if 0 < v < 0.01 else f"{v:.0%}"


# ---------------------------------------------------------------- charts


def bar_chart(
    data,
    title: str,
    source: str,
    *,
    share: bool = False,
    sort: bool = True,
    highlight: str | None = None,
    x_label: str | None = None,
) -> Figure:
    """Horizontal bars: how much of something for each category.

    ``data`` is a table whose first two columns are the category and its value
    (or columns named ``category`` and ``value``), a dict ``{category: value}``,
    or a list of ``(category, value)`` pairs. Bars are sorted largest first
    (``sort=False`` keeps your order, for example age bands) and each bar has
    its value written at its tip.

    ``share=True`` means the values are fractions between 0 and 1 and are shown
    as percentages. ``highlight`` names one category to draw in blue with the
    rest in grey, for when the story is about that one. Otherwise every bar is
    the same blue: bar length already says "how much", so colour is not used for
    it a second time.
    """
    df = _pairs(data, ["category", "value"])
    if df.empty:
        raise ValueError("no data to chart")
    if (df["value"] < 0).any():
        raise ValueError("bar values must not be negative")
    if highlight is not None and highlight not in set(df["category"]):
        raise ValueError(f"highlight {highlight!r} is not one of the categories")
    if sort:
        df = df.sort_values("value", ascending=False, kind="stable").reset_index(drop=True)
    fmt = _fmt_share if share else _fmt_count
    values = df["value"].astype(float).to_numpy()
    probe = _new_figure()
    right = max(_width_in(probe, fmt(v), 9.5, "bold") for v in values) + 0.25
    fig, ax, _ = _frame(title, source, df["category"].astype(str).tolist(), [], right, x_label)
    colours = [
        SERIES[0] if highlight is None or c == highlight else DEEMPHASIS for c in df["category"]
    ]
    ax.barh(range(len(df)), values, height=_BAR_THICKNESS, color=colours, linewidth=0)
    top = values.max() if values.max() > 0 else 1.0
    ax.set_xlim(0, top * 1.04)
    for i, v in enumerate(values):
        ax.annotate(
            fmt(v),
            (v, i),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            ha="left",
            fontsize=9.5,
            fontweight="bold",
            color=INK,
            annotation_clip=False,
        )
    _value_axis(ax, share)
    fig.chart_data = df  # type: ignore[attr-defined]
    return fig


def stacked_bar(
    data,
    title: str,
    source: str,
    *,
    order: Sequence[str] | None = None,
    share: bool = True,
    x_label: str | None = None,
) -> Figure:
    """Horizontal stacked bars: what each country (row) is made of.

    ``data`` has one row per country and one column per part. Give it as a
    table (country names in the index, or in a column called ``row``), or as a
    dict ``{country: {part: value}}``. Rows appear top to bottom as given, so
    sort them first if you want an order.

    ``share=True`` (the default) scales every row to 100% so rows of different
    size can be compared; ``share=False`` keeps the raw counts. ``order`` is the
    full ordered list of every part the study ever shows, so a part keeps its
    colour when this chart shows fewer of them (see ``colours_for``).
    """
    if isinstance(data, Mapping):
        df = pd.DataFrame.from_dict(data, orient="index")
    elif isinstance(data, pd.DataFrame):
        df = data.set_index("row") if "row" in data.columns else data.copy()
    else:
        raise TypeError("data must be a DataFrame or a dict of dicts")
    df = df.fillna(0).astype(float)
    if df.empty:
        raise ValueError("no data to chart")
    if (df < 0).any().any():
        raise ValueError("stacked values must not be negative")
    parts = [str(c) for c in df.columns]
    df.columns = parts
    colour_of = colours_for(parts, order)
    shown = df.copy()
    if share:
        totals = df.sum(axis=1)
        if (totals == 0).any():
            raise ValueError(f"rows with nothing in them: {list(df.index[totals == 0])}")
        shown = df.div(totals, axis=0)
    rows = [str(r) for r in df.index]
    fig, ax, _ = _frame(
        title,
        source,
        rows,
        [(p, colour_of[p]) for p in parts],
        0.35,
        x_label,
    )
    left = np.zeros(len(rows))
    for p in parts:
        w = shown[p].to_numpy()
        ax.barh(
            range(len(rows)),
            w,
            left=left,
            height=_BAR_THICKNESS,
            color=colour_of[p],
            edgecolor=SURFACE,  # the 2-pixel gap between segments
            linewidth=GAP_PT,
        )
        left = left + w
    ax.set_xlim(0, 1 if share else left.max() * 1.02)
    _value_axis(ax, share)
    out = shown.copy()
    out.index = rows
    out.index.name = "row"
    fig.chart_data = out.reset_index()  # type: ignore[attr-defined]
    return fig


def interval_chart(
    data,
    title: str,
    source: str,
    *,
    percent: bool = True,
    sort: bool = True,
    xlim: tuple[float, float] | None = None,
    x_label: str = "Estimate, with confidence interval",
) -> Figure:
    """One dot per category for an estimate, with a line for its confidence interval.

    Use it for accuracy figures: the dot is the best estimate, the line is the
    range we cannot rule out. ``data`` is a table with columns ``label``,
    ``estimate``, ``low``, ``high`` (and optionally ``n``, how many were
    checked, which is added to the label), or a list of
    ``(label, estimate, low, high)``. With ``percent=True`` the numbers are
    fractions between 0 and 1 and the axis runs 0 to 100% unless ``xlim`` says
    otherwise. A wide line means we know the figure only roughly.
    """
    cols = ["label", "estimate", "low", "high"]
    if isinstance(data, pd.DataFrame) and "n" in data.columns:
        cols = cols + ["n"]
    df = _pairs(data, cols)
    if df.empty:
        raise ValueError("no data to chart")
    if ((df["low"] > df["estimate"]) | (df["estimate"] > df["high"])).any():
        raise ValueError("each row needs low <= estimate <= high")
    if sort:
        df = df.sort_values("estimate", ascending=False, kind="stable").reset_index(drop=True)
    fmt = _fmt_share if percent else (lambda v: f"{v:,.2f}")
    names = [
        f"{r.label} (n = {int(r.n):,})" if "n" in df.columns else str(r.label)
        for r in df.itertuples()
    ]
    notes = [f"{fmt(r.estimate)}  ({fmt(r.low)} to {fmt(r.high)})" for r in df.itertuples()]
    probe = _new_figure()
    right = max(_width_in(probe, s, 9.5, "bold") for s in notes) + 0.3
    fig, ax, _ = _frame(title, source, names, [], right, x_label)
    est = df["estimate"].astype(float).to_numpy()
    low = df["low"].astype(float).to_numpy()
    high = df["high"].astype(float).to_numpy()
    ys = np.arange(len(df))
    ax.hlines(ys, low, high, color=SERIES[0], linewidth=2 * 72 / DPI, zorder=3)
    ax.plot(
        est,
        ys,
        linestyle="none",
        marker="o",
        markersize=7.5,
        markerfacecolor=SERIES[0],
        markeredgecolor=SURFACE,  # the 2-pixel ring
        markeredgewidth=GAP_PT,
        zorder=4,
    )
    if xlim is None:
        xlim = (0.0, 1.0) if percent else (min(low.min(), 0.0), high.max() * 1.05)
    ax.set_xlim(*xlim)
    for y, h, note in zip(ys, high, notes):
        ax.annotate(
            note,
            (h, y),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            ha="left",
            fontsize=9.5,
            fontweight="bold",
            color=INK,
            annotation_clip=False,
        )
    _value_axis(ax, percent)
    fig.chart_data = df  # type: ignore[attr-defined]
    return fig


def _value_axis(ax, as_share: bool) -> None:
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 5, 10], integer=not as_share))
    if as_share:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0%}"))
    else:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.xaxis.grid(True)


# ---------------------------------------------------------------- saving


def save(fig: Figure, path_stem: str | Path) -> dict[str, Path]:
    """Write ``<stem>.png`` (twice the screen size), ``<stem>.svg`` and ``<stem>.csv``.

    The CSV holds the numbers that were drawn, so every chart has a table
    behind it. Only figures made by this module can be saved this way. Returns
    the three paths.
    """
    data = getattr(fig, "chart_data", None)
    if data is None:
        raise ValueError("this figure was not made by charts, so its data table is unknown")
    stem = Path(path_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    paths = {ext: stem.with_name(stem.name + "." + ext) for ext in ("png", "svg", "csv")}
    fig.savefig(paths["png"], dpi=DPI * 2, facecolor=SURFACE)
    fig.savefig(paths["svg"], facecolor=SURFACE)
    data.to_csv(paths["csv"], index=False)
    return paths
