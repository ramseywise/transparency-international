"""Charts comparing the country tests of the draft codebook. PROVISIONAL.

The records are those of draft 0.13, with the three entries searched again under draft 0.14
laid over them (see analysis.country_test).

Reads the tables in outputs/draft-codebook/comparison/ (made by analysis.country_test and
analysis.country_insights) and writes four charts beside them:
  kind_by_country_PROVISIONAL.png        who the delegates represent: from the list alone,
                                         then after the web search, all / Party / overflow
  business_activity_PROVISIONAL.png      business delegates by provisional activity group
  fossil_by_country_PROVISIONAL.png      the fossil question by strength of evidence (codebook
                                         5.5): all / Party / overflow, then the same three
                                         for business delegates only
  cannot_say_PROVISIONAL.png             the "cannot say" delegates by what could settle them
Stacked bars are shares of each row's own total, because the delegations differ in size;
segments carry their count. Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.country_charts

Colours (dataviz validator, light surface). Kind: one blue ramp for the three non-business
groups, green for business, light grey for not identified. Fossil: the colour is the answer and
its depth is the strength of the evidence: a warm ramp for "fits a tier", a blue ramp for "no
link found" (darkest = definitive evidence, lightest = by proxy), pale grey for "no evidence
either way". Which tier is met is said in the note, from the data. The ramps and the grey fail
the validator's categorical lightness band by design; every adjacent pair passes its
separation checks, and every segment of 5% or more carries its count.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from analysis.country_insights import ROUTES  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "draft-codebook" / "comparison"
SRC = OUT / "country_comparison_PROVISIONAL.csv"
SURFACE, INK, MUTED, GREY = "#fcfcfb", "#0b0b0b", "#52514e", "#c9c8c2"
GREEN = "#008300"
KIND = (  # (value in the table, legend label, colour, label ink)
    ("public_sector", "Public sector", "#104281", "white"),
    ("civil_society_and_other_non_state", "Civil society and other non-profit", "#3987e5", "white"),
    ("other", "Other (for example intergovernmental bodies)", "#86b6ef", INK),
    ("business_and_commercial", "Business", GREEN, "white"),
    ("not_identified", "Not identified / not stated", GREY, INK),
)
NO_EVIDENCE = "#e3e2dc"
STRENGTH = ("established", "limited_evidence", "proxy")
FOSSIL = (
    ("tier:established", "Definitive evidence", "#6e2206", "white"),
    ("tier:limited_evidence", "Some evidence", "#ad3f14", "white"),
    ("tier:proxy", "By proxy (assumed from the kind of body)", "#f2a17e", INK),
    ("none:established", "Definitive evidence", "#104281", "white"),
    ("none:limited_evidence", "Some evidence", "#3987e5", "white"),
    ("none:proxy", "By proxy (assumed from the kind of body)", "#86b6ef", INK),
    ("unknown", "Neither yes nor no can be said", NO_EVIDENCE, INK),
)
FOSSIL_GROUPS = (("Fits a fossil tier", 3), ("No fossil link found", 3),
                 ("No evidence either way", 1))
ROUTE = tuple(zip(ROUTES, ROUTES, ("#2a78d6", "#1baf7a", "#6250d6"), ("white", INK, "white")))
LIST_ALONE = "From the list alone"


def fossil_key(headline: str, line: str) -> str:
    """The chart segment of one headline row: the answer ("tier" or "none") with the strength
    of its evidence, or "unknown". An unexpected line is an error, never a guess."""
    if headline == "insufficient evidence":
        return "unknown"
    if line not in STRENGTH:
        raise ValueError(f"{headline}: line {line!r} is not one of {STRENGTH}")
    if headline.startswith("Tier"):
        return f"tier:{line}"
    if headline == "no identified link":
        return f"none:{line}"
    raise ValueError(f"unknown headline {headline!r}")


SPLITS = (("delegates", "All delegates"), ("party", "Party badges"), ("overflow", "Overflow badges"))
BUSINESS = (("delegates", "Business: all"), ("party", "Business: Party"),
            ("overflow", "Business: overflow"))


def bars(rows: list[dict], view: str = "organisation search") -> tuple[list, list]:
    """(kind bars, fossil bars): each bar is (country, bar label, {segment: delegates}).
    Per country: all delegates, Party badges, overflow badges; the fossil bars then give the
    same three for business delegates only."""
    kind: dict = {}
    fossil: dict = {}
    for r in rows:
        if r["view"] != view or r["measure"] not in ("kind", "headline_all", "headline_business"):
            continue
        target = kind if r["measure"] == "kind" else fossil
        key = r["value"] if r["measure"] == "kind" else fossil_key(r["value"], r["line"])
        for col, name in BUSINESS if r["measure"] == "headline_business" else SPLITS:
            bar = target.setdefault((r["country"], name), {})
            bar[key] = bar.get(key, 0) + int(r[col])
    order = [n for _, n in SPLITS + BUSINESS]
    by_country = lambda d: sorted(d.items(), key=lambda x: order.index(x[0][1]))  # noqa: E731
    countries = list(dict.fromkeys(c for c, _ in list(kind) + list(fossil)))
    pick = lambda d: [(c, n, v) for want in countries  # noqa: E731
                      for (c, n), v in by_country(d) if c == want]
    return pick(kind), pick(fossil)


def tiers_met(rows: list[dict], view: str = "organisation search") -> str:
    """One sentence naming each tier met, per country, with its delegates and evidence line."""
    said = {"established": "definitive evidence", "limited_evidence": "some evidence",
            "proxy": "by proxy"}
    met = [f"{r['country']} {r['value']} ({r['delegates']} delegates, {said[r['line']]})"
           for r in rows if r["view"] == view and r["measure"] == "headline_all"
           and r["value"].startswith("Tier")]
    return "Tiers met: " + "; ".join(met) + "." if met else "No tier is met in these tests."


def with_list_alone(kind_bars: list, alone_rows: list[dict]) -> list:
    """Put a "From the list alone" bar before each country's bars. The list states no type of
    organisation, so the whole bar is "not stated"; a stated type would need a rule first."""
    out, seen = [], set()
    for country, name, values in kind_bars:
        if country not in seen:
            seen.add(country)
            mine = {r["value"]: int(r["delegates"]) for r in alone_rows if r["country"] == country}
            if mine.get("stated"):
                raise ValueError(f"{country}: the list states a type; no rule maps it to a kind")
            out.append((country, LIST_ALONE, {"not_identified": mine.get("not stated", 0)}))
        out.append((country, name.replace("All delegates", "After web search: all"), values))
    return out


def _figure(n_rows: float, bottom: float):
    fig, ax = plt.subplots(figsize=(8.2, 0.42 * n_rows + 2.4), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    return fig, ax


def _finish(fig, title: str, note: str, path: Path) -> None:
    fig.text(0.02, 0.985, title, fontsize=10, color=INK, weight="bold", va="top")
    fig.text(0.02, 0.01, note, fontsize=6.5, color=MUTED, va="bottom", linespacing=1.4)
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    print(path)


def draw(bar_rows: list, segments: tuple, title: str, note: str, path: Path,
         groups: tuple = ()) -> None:
    """100% stacked horizontal bars. `groups` = ((heading, number of segments), ...) splits
    the legend into headed columns, in segment order."""
    fig, ax = _figure(len(bar_rows), 0.3)
    y, last = 0.0, None
    for country, name, values in bar_rows:
        if last is not None and country != last:
            y += 0.9
        if country != last:
            ax.text(-46, y - 0.62, country, ha="left", va="center", fontsize=9, color=INK,
                    weight="bold")
        total = sum(values.values())
        left = 0.0
        for key, _, colour, ink in segments:
            v = values.get(key, 0)
            share = 100 * v / total if total else 0
            ax.barh(y, share, left=left, height=0.62, color=colour, edgecolor=SURFACE, linewidth=2)
            if share >= 5:
                ax.text(left + share / 2, y, f"{v} ({share:.0f}%)" if share >= 13 else str(v),
                        ha="center", va="center", fontsize=8, color=ink)
            left += share
        ax.text(-2, y, f"{name} ({total})", ha="right", va="center", fontsize=8.5, color=INK)
        last = country
        y += 1
    ax.set_xlim(-46, 100)
    ax.set_ylim(y - 0.4, -1.1)
    start, x = 0, 0.0
    for heading, n in groups or (("", len(segments)),):
        handles = [Patch(facecolor=c, edgecolor=SURFACE, label=lab)
                   for _, lab, c, _ in segments[start:start + n]]
        leg = ax.legend(handles=handles, title=heading or None, loc="upper left",
                        bbox_to_anchor=(x, 0.0), ncol=1 if groups else 2, frameon=False,
                        fontsize=7.5, title_fontsize=8, labelcolor=MUTED, handlelength=1.2,
                        alignment="left")
        if heading:
            leg.get_title().set_color(INK)
            leg.get_title().set_weight("bold")
        ax.add_artist(leg)
        start += n
        x += 0.36 if n > 2 else 0.33
    rows_in_legend = max(n for _, n in groups) + 1 if groups else (len(segments) + 1) // 2
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93,
                        bottom=(0.75 + 0.2 * rows_in_legend) / fig.get_figheight())
    _finish(fig, title, note, path)


def activity_rows(rows: list[dict]) -> list:
    """(country, activity group, delegates, what the fossil question says) per bar."""
    said = {"insufficient evidence": "cannot say yet", "no identified link": "no fossil link identified"}
    out = []
    for r in rows:
        out.append((r["country"], r["provisional_group"], int(r["delegates"]),
                    said.get(r["headline"], f"{r['headline']} met")))
    return out


def draw_activity(rows: list, title: str, note: str, path: Path) -> None:
    """Counts, one bar per activity group, one colour: the title names the single series."""
    fig, ax = _figure(len(rows) + 2, 0.12)
    y, last, top = 0.0, None, max(r[2] for r in rows)
    for country, group, n, fossil in rows:
        if last is not None and country != last:
            y += 0.9
        if country != last:
            total = sum(r[2] for r in rows if r[0] == country)
            ax.text(-0.9 * top, y - 0.62, f"{country} ({total} business delegates)", ha="left",
                    va="center", fontsize=9, color=INK, weight="bold")
        ax.barh(y, n, height=0.62, color=GREEN, edgecolor=SURFACE, linewidth=2)
        ax.text(-0.03 * top, y, group, ha="right", va="center", fontsize=8.5, color=INK)
        ax.text(n + 0.03 * top, y, f"{n}", ha="left", va="center", fontsize=8.5, color=INK)
        ax.text(n + 0.12 * top, y, f"fossil link: {fossil}", ha="left", va="center",
                fontsize=7.5, color=MUTED)
        last = country
        y += 1
    ax.set_xlim(-0.9 * top, 1.9 * top)
    ax.set_ylim(y - 0.4, -1.1)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.75 / fig.get_figheight())
    _finish(fig, title, note, path)


def route_bars(rows: list[dict], totals: dict) -> list:
    """One bar per country: its "cannot say" delegates by what could settle them."""
    out: dict = {}
    for r in rows:
        bar = out.setdefault(r["country"], {})
        bar[r["route"]] = bar.get(r["route"], 0) + int(r["delegates"])
    return [(c, f"cannot say, of {totals[c]}", v) for c, v in out.items()]


def _read(name: str) -> list[dict]:
    return list(csv.DictReader(open(OUT / name)))


def main() -> None:
    rows = _read("country_comparison_PROVISIONAL.csv")
    kind, fossil = bars(rows)
    totals = {c: sum(v.values()) for c, n, v in kind if n == "All delegates"}
    source = ("Source: UNFCCC COP31 provisional list of participants; country tests, codebook "
              "drafts 0.13 and 0.14 (not approved). Accuracy not measured.")
    share = "\nCounts of registered delegates; each segment is a share of its own bar."
    draw(with_list_alone(kind, _read("kind_from_list_alone_PROVISIONAL.csv")), KIND,
         "Who the registered delegates represent: the list alone, then after the web search (PROVISIONAL)",
         source + share + "\nThe list's own \"type of organisation\" field is empty for every "
         "delegate of these three delegations.\nSaudi Arabia: the largest entry is an "
         "abbreviation; its kind is taken from the list's own context (a proxy, low confidence).",
         OUT / "kind_by_country_PROVISIONAL.png")
    draw_activity(activity_rows(_read("business_activity_PROVISIONAL.csv")),
                  "Business delegates by what the organisation does (PROVISIONAL, not the sector rule)",
                  source + "\nGroups assigned by hand from one stored evidence item per "
                  "organisation. The sector rule is not yet defined.",
                  OUT / "business_activity_PROVISIONAL.png")
    draw(fossil, FOSSIL,
         "Fossil fuel link: how strong is the evidence, for all and for business delegates (PROVISIONAL)",
         source + share + "\nEach delegate is counted once, at the highest tier their "
         "organisation meets. " + tiers_met(rows) + "\n\"No fossil link found\" rests on rules "
         "that are not approved; it does not mean no link exists. Tier 3 (finance) has no rule yet.",
         OUT / "fossil_by_country_PROVISIONAL.png", FOSSIL_GROUPS)
    draw(route_bars(_read("cannot_say_reasons_PROVISIONAL.csv"), totals), ROUTE,
         "The delegates we cannot place on the fossil question: what could settle them (PROVISIONAL)",
         source + share + "\nA decision: define the finance tier. A person lookup covers every "
         "delegate under the entry (rule 8: employer and source only) and has not been run for these.",
         OUT / "cannot_say_PROVISIONAL.png", tuple((r, 1) for r in ()))


if __name__ == "__main__":
    main()
