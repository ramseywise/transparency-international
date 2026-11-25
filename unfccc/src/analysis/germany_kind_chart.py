"""Germany test chart: delegates by kind of organisation, Party and overflow badges side by side.

Reads data/processed/draft-codebook/germany-test/germany_by_organisation_0.13_PROVISIONAL.csv and
writes outputs/draft-codebook/germany-test/germany_kind_PROVISIONAL.png.
Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.germany_kind_chart

Colours (dataviz validator, light surface): categorical slots 1 to 3 in fixed order, and a neutral
grey for "not yet identified" (unknown is not a series). Aqua is below 3:1 against the surface, so
segments are labelled and the legend carries each total.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "draft-codebook" / "germany-test" / "germany_by_organisation_0.13_PROVISIONAL.csv"
OUT = ROOT / "outputs" / "draft-codebook" / "germany-test"
SEGMENTS = (  # (kind in the data, legend label, colour, label ink)
    ("public_sector", "Public sector", "#2a78d6", "white"),
    ("civil_society_and_other_non_state", "Civil society and other non-profit", "#eb6834", "#0b0b0b"),
    ("business_and_commercial", "Business", "#1baf7a", "#0b0b0b"),
    (None, "Not yet identified", "#8a8983", "white"),
)
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"
KINDS = {s[0] for s in SEGMENTS if s[0]}


def counts() -> dict:
    """Delegates by (kind or None, badge). Any kind outside the three named ones counts as None."""
    out: dict = {}
    for r in csv.DictReader(open(SRC)):
        kind = r["kind"] if r["kind"] in KINDS else None
        for col in ("party", "overflow"):
            out[(kind, col)] = out.get((kind, col), 0) + int(r[col])
    return out


def main() -> None:
    n = counts()
    fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for y, (col, name) in enumerate((("party", "Party badges"), ("overflow", "Party overflow badges"))):
        total = sum(n.get((k, col), 0) for k, *_ in SEGMENTS)
        left = 0
        for kind, label, colour, ink in SEGMENTS:
            v = n.get((kind, col), 0)
            both = n.get((kind, "party"), 0) + n.get((kind, "overflow"), 0)
            ax.barh(y, v, left=left, height=0.55, color=colour, edgecolor=SURFACE, linewidth=2,
                    label=f"{label} ({both})" if y == 0 else None)
            if v >= 5:
                ax.text(left + v / 2, y, f"{v}  ({100 * v / total:.0f}%)" if v >= 20 else str(v),
                        ha="center", va="center", fontsize=9, color=ink)
            left += v
        ax.text(-3, y, f"{name}\n({total} delegates)", ha="right", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 135)
    ax.set_ylim(1.5, -0.6)
    ax.axis("off")
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.02), ncol=2, frameon=False, fontsize=8,
              labelcolor=MUTED, handlelength=1.2)
    total = sum(n.values())
    fig.text(0.01, 0.97, f"Germany: who the {total} registered delegates represent (PROVISIONAL)",
             fontsize=10, color=INK, weight="bold", va="top")
    fig.text(0.01, 0.03, "Source: UNFCCC COP31 provisional list of participants; Germany test, codebook 0.13 draft.\n"
             "Business on Party badges: 1 delegate. 'Not yet identified' is mostly one embassy entry (34 delegates).",
             fontsize=7, color=MUTED, va="bottom", linespacing=1.4)
    fig.subplots_adjust(left=0.24, right=0.98, top=0.84, bottom=0.38)
    fig.savefig(OUT / "germany_kind_PROVISIONAL.png", facecolor=SURFACE)
    print(OUT / "germany_kind_PROVISIONAL.png")


if __name__ == "__main__":
    main()
