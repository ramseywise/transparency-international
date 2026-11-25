"""Germany test chart: delegates by headline outcome, Party and overflow badges side by side.

Reads outputs/draft-codebook/germany-test/germany_headline_PROVISIONAL.csv and writes
germany_headline_PROVISIONAL.png beside it. Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.germany_chart

Colours (dataviz validator, light surface): blue 550 and blue 300 for the two "no identified
link" lines, a neutral grey for insufficient evidence. The grey fails the chroma floor on
purpose (unknown is not a series); the pale blue is below 3:1, so every segment is labelled.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "outputs" / "draft-codebook" / "germany-test"
SEGMENTS = (  # (headline, line, legend label, colour, label ink)
    ("no identified link", "limited_evidence", "No identified link – limited evidence", "#1c5cab", "white"),
    ("no identified link", "proxy", "No identified link – proxy (type of body)", "#6da7ec", "#0b0b0b"),
    ("insufficient evidence", "unknown", "Insufficient evidence", "#8a8983", "white"),
)
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"


def main() -> None:
    rows = {(r["headline"], r["line"]): r for r in csv.DictReader(open(OUT / "germany_headline_PROVISIONAL.csv"))}
    bars = (("party", "Party badges"), ("overflow", "Party overflow badges"))
    fig, ax = plt.subplots(figsize=(7.2, 2.8), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for y, (col, name) in enumerate(bars):
        total = sum(int(r[col]) for r in rows.values())
        left = 0
        for h, line, label, colour, ink in SEGMENTS:
            n = int(rows[(h, line)][col])
            ax.barh(y, n, left=left, height=0.55, color=colour, edgecolor=SURFACE, linewidth=2,
                    label=label if y == 0 else None)
            ax.text(left + n / 2, y, str(n), ha="center", va="center", fontsize=9, color=ink)
            left += n
        ax.text(-3, y, f"{name}\n({total} delegates)", ha="right", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 135)
    ax.set_ylim(1.5, -0.6)
    ax.axis("off")
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.02), ncol=2, frameon=False, fontsize=8,
              labelcolor=MUTED, handlelength=1.2)
    fig.text(0.01, 0.97, "Germany: what the evidence shows for 253 registered delegates (PROVISIONAL)",
             fontsize=10, color=INK, weight="bold", va="top")
    fig.text(0.01, 0.03, "Source: UNFCCC COP31 provisional list of participants; Germany test, codebook 0.13 draft.\n"
             "Tiers 1 and 2 assessed as not met for 165 delegates, unknown for 88; Tier 3 not yet defined.\n"
             "On established evidence alone, no delegate has 'no identified link'.",
             fontsize=7, color=MUTED, va="bottom", linespacing=1.4)
    fig.subplots_adjust(left=0.24, right=0.98, top=0.84, bottom=0.40)
    fig.savefig(OUT / "germany_headline_PROVISIONAL.png", facecolor=SURFACE)
    print(OUT / "germany_headline_PROVISIONAL.png")


if __name__ == "__main__":
    main()
