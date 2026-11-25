"""Progress charts for one wave of the batch run, drawn after each batch. PROVISIONAL.

Reads data/processed/draft-codebook/wave<N>/inputs.json and the classified records beside it,
and writes to outputs/draft-codebook/wave<N>/:
  wave<N>_kind_PROVISIONAL.png      who the delegates represent: one row per delegation, sorted
                                    by public-sector share; each kind split into Party badges
                                    (solid) and overflow badges (hatched); a line at the wave's
                                    public-sector share
  wave<N>_business_PROVISIONAL.png  each business organisation: delegates by badge, the
                                    codebook's business type, state ownership where on record
  wave<N>_fossil_PROVISIONAL.png    the fossil question per delegation: "fits a tier" to the
                                    left of zero, "no link found" to the right, each from the
                                    strongest evidence outward; "neither yes nor no" in its own
                                    panel; lines at the wave's shares
  wave<N>_progress_PROVISIONAL.csv  the counts behind the charts, one row per organisation, with
                                    which tier each record meets (strict and inferred)
Organisations not yet classified are drawn as "not yet searched", never as unknown.
Colours are those of analysis.country_charts (validated there); hatching is the second cue
for overflow badges, so the badge split never rests on colour alone.

Fossil segment of one record (codebook 5.5): a tier met on the strict label is definitive; a
strict "no link" is definitive; else an inferred value beside it, by its basis
(limited_evidence = some evidence, proxy = by proxy); else neither yes nor no.
Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.wave_progress 1
"""
import csv
import json
import re
import textwrap
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from analysis import sector as S  # noqa: E402
from analysis.country_charts import (FOSSIL, GREEN, GREY, INK, KIND, MUTED,  # noqa: E402
                                     NO_EVIDENCE, SURFACE)

ROOT = Path(__file__).resolve().parents[2]
TIERS = ("tier_1", "tier_2A", "tier_2B_O", "tier_2B_S", "tier_3")
NOT_RUN = ("not_run", "Not yet searched", "#f4f3ef", INK)
KIND_SEG = tuple((k, lab.replace("Other (for", "Other: media and others (for"), c, i)
                 for k, lab, c, i in KIND) + (NOT_RUN,)
BADGES = ("party", "overflow")
HATCH = "////"
BUSINESS_TYPE = {"company": "company", "consultancy": "consultancy",
                 "trade_or_industry_association": "trade or industry association",
                 "financial_institution": "financial institution",
                 "unknown": "type not established"}


def kind_key(attrs: dict) -> str:
    label = attrs["kind"]["label"]
    if label == "media":
        return "other"
    return "not_identified" if label == "unknown" else label


def fossil_key(attrs: dict) -> str:
    strict = [attrs[t]["label"] for t in TIERS] + [attrs["fossil_link_kind"]["label"]]
    if "met" in strict:
        return "tier:established"
    if attrs["fossil_link_kind"]["label"] in ("none_established", "no_link"):
        return "none:established"
    inferred = [attrs[t].get("inferred") for t in TIERS + ("fossil_link_kind",)]
    inferred = [i for i in inferred if i]
    for i in inferred:
        if i["label"] == "met":
            return f"tier:{i['basis']}"
    for i in inferred:
        if i["label"] in ("not_met", "none_established"):
            return f"none:{i['basis']}"
    return "unknown"


def tiers_said(attrs: dict, inferred: bool = False) -> str:
    """Each tier whose label is not unknown, as tier=label; strict labels or inferred ones."""
    out = []
    for t in TIERS:
        v = attrs[t].get("inferred") if inferred else attrs[t]
        if v and v.get("label") not in (None, "unknown"):
            out.append(f"{t}={v['label']}" + (f" ({v['basis']})" if inferred else ""))
    return "; ".join(out)


def with_tier3(attrs: dict, t3: dict | None) -> dict:
    """The record's attributes with tier 3 as code set it (codebook section 9,
    analysis.tier3_draft), in place of the classifier's placeholder. A "met" that still waits for
    a person to confirm the legal entity (`to_confirm`) is not counted: tier 3 stays unknown,
    with that reason, until it is confirmed."""
    if not t3:
        return attrs
    a = dict(attrs)
    t = dict(t3)
    if t.get("label") == "met" and t.get("to_confirm"):
        t["label"], t["unknown_reason"] = "unknown", "met by code, to confirm"
    a["tier_3"] = t
    return a


def utility_key(attrs: dict) -> str:
    label = attrs.get("utility", {}).get("label", "unknown")
    return label if label in ("yes", "no") else "unknown"


def rows(wave: int) -> list[dict]:
    folder = ROOT / "data" / "processed" / "draft-codebook" / f"wave{wave}"
    t3_path = folder / "tier3_run.json"
    t3_all = json.loads(t3_path.read_text())["results"] if t3_path.exists() else {}
    out = []
    for r in json.loads((folder / "inputs.json").read_text()):
        path = folder / "classified" / f"{r['case']}.json"
        rec = json.loads(path.read_text()) if path.exists() else None
        a = with_tier3(rec["attributes"], t3_all.get(r["case"])) if rec else None
        ev_path = folder / "evidence" / f"{r['case']}.json"
        ev = json.loads(ev_path.read_text()) if ev_path.exists() else {}
        activity = (ev.get("activity") or {}).get("text") or ""
        biz = bool(a) and kind_key(a) == "business_and_commercial"
        sec = S.columns(biz, a["business_type"]["label"] if a else "", ev,
                        S.register_record(folder, r["case"]))
        out.append({"case": r["case"], "name": rec["name"] if rec else "",
                    "codebook": rec.get("codebook_version", "") if rec else "",
                    "delegation": "; ".join(r["wave_delegations"]),
                    "delegates": r["delegates"], "party": r["party"], "overflow": r["overflow"],
                    "kind": kind_key(a) if a else "not_run",
                    "fossil": fossil_key(a) if a else "not_run",
                    "tiers_strict": tiers_said(a) if a else "",
                    "tiers_inferred": tiers_said(a, inferred=True) if a else "",
                    "fossil_unknown_reason": a["fossil_link_kind"]["unknown_reason"] or "" if a else "",
                    "tier3_unknown_reason": a["tier_3"]["unknown_reason"] or "" if a else "",
                    "tier3_set_by_code": (f"{a['tier_3']['label']}"
                                          f" (step {a['tier_3'].get('step')})"
                                          if a and r["case"] in t3_all else ""),
                    "business_type": a["business_type"]["label"] if a else "",
                    "state_ownership": a["state_ownership"]["label"] if a else "",
                    "utility": utility_key(a) if a else "",
                    "activity_as_found": activity} | sec)
    return out


# ---- what the charts show -------------------------------------------------------------------

def by_delegation(data: list[dict], field: str) -> dict:
    """{delegation: {(segment, badge): delegates}}."""
    out: dict = {}
    for r in data:
        bar = out.setdefault(r["delegation"], {})
        for b in BADGES:
            if r[b]:
                bar[(r[field], b)] = bar.get((r[field], b), 0) + r[b]
    return out


def share(bar: dict, keys) -> float:
    total = sum(bar.values())
    return 100 * sum(v for (k, _), v in bar.items() if k in keys) / total if total else 0.0


def kind_order(per: dict) -> list[str]:
    """Largest public-sector share first; ties by size of delegation."""
    return sorted(per, key=lambda d: (-share(per[d], {"public_sector"}), -sum(per[d].values()), d))


def fossil_order(per: dict) -> list[str]:
    """Most "no link found" on definitive evidence first, then on some evidence, then by proxy."""
    return sorted(per, key=lambda d: (-share(per[d], {"none:established"}),
                                      -share(per[d], {"none:limited_evidence"}),
                                      -share(per[d], {"none:proxy"}), d))


def wave_share(data: list[dict], field: str, keys) -> float:
    total = sum(r["delegates"] for r in data)
    return 100 * sum(r["delegates"] for r in data if r[field] in keys) / total if total else 0.0


# ---- drawing -----------------------------------------------------------------------------------

def _fig(n_rows: int, width: float = 8.2):
    fig, ax = plt.subplots(figsize=(width, 0.3 * n_rows + 2.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    return fig, ax


PALE = {NO_EVIDENCE, NOT_RUN[2]}   # near-white fills: hatch them in grey, or it does not show


def _hatch(colour, hatched):
    if not hatched:
        return {}
    return {"hatch": HATCH, "hatchcolor": MUTED if colour in PALE else SURFACE}


def _seg(ax, y, left, width, colour, ink, n, hatched, label_min=6.0):
    ax.barh(y, width, left=left, height=0.7, color=colour, edgecolor=SURFACE, linewidth=1.5,
            **_hatch(colour, hatched))
    if abs(width) >= label_min:
        ax.text(left + width / 2, y, str(n), ha="center", va="center", fontsize=7, color=ink,
                bbox=dict(boxstyle="square,pad=0.15", fc=colour, ec="none") if hatched else None)


def _vline(ax, x, top, bottom, text):
    ax.plot([x, x], [top, bottom], color=INK, lw=0.9, ls=(0, (3, 2)), zorder=5)
    ax.text(x, top - 0.15, text, ha="center", va="bottom", fontsize=7, color=INK)


def version_groups(data: list[dict]) -> list[tuple[str, list[dict]]]:
    """Rows split by codebook version, in the order they come. The fossil results of different
    versions are never pooled into one average (decisions.md, 2026-11-26)."""
    vs = list(dict.fromkeys(r.get("codebook", "") for r in data))
    return [(v, [r for r in data if r.get("codebook", "") == v]) for v in vs]


def delegation_versions(data: list[dict]) -> dict:
    """{delegation: " · 0.13"} for delegations classified with an earlier codebook version than
    the newest in `data`, so a reader can tell them apart; {} when there is only one version."""
    vs = {r["codebook"] for r in data if r["codebook"]}
    if len(vs) < 2:
        return {}
    out: dict = {}
    for r in data:
        if r["codebook"]:
            out.setdefault(r["delegation"], set()).add(r["codebook"])
    newest = max(vs, key=lambda v: tuple(int(x) for x in v.split(".")))
    return {d: " · " + "/".join(sorted(v)) for d, v in out.items() if v != {newest}}


def _badge_legend():
    return [Patch(facecolor=MUTED, edgecolor=SURFACE, label="Party badge"),
            Patch(facecolor=MUTED, edgecolor=SURFACE, hatch=HATCH, label="Overflow badge")]


def _finish(fig, ax, title, note, path, handles, ncol, legend_rows):
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, 0), ncol=ncol,
              frameon=False, fontsize=7.5, labelcolor=MUTED, handlelength=1.6)
    h = fig.get_figheight()
    note = "\n".join(textwrap.fill(line, int(fig.get_figwidth() * 24))
                     for line in note.split("\n"))
    fig.subplots_adjust(left=0.02, right=0.98, top=1 - 0.45 / h,
                        bottom=(0.3 + 0.14 * note.count("\n") + 0.22 * legend_rows) / h)
    fig.text(0.02, 1 - 0.12 / h, title, fontsize=10, color=INK, weight="bold", va="top")
    fig.text(0.02, 0.08 / h, note, fontsize=6.5, color=MUTED, va="bottom", linespacing=1.4)
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    print(path)


def draw_kind(data: list[dict], title: str, note: str, path: Path) -> None:
    """One list of delegations and one average: the kind rules (codebook 3.1, K1-K5) are the
    same in every version so far, so kind is pooled across versions (decisions.md, 2026-11-26)."""
    per = by_delegation(data, "kind")
    tag = delegation_versions(data)
    fig, ax = _fig(len(per))
    y, present = 0, {k for bar in per.values() for k, _ in bar}
    for d in kind_order(per):
        bar, total, left = per[d], sum(per[d].values()), 0.0
        for key, _, colour, ink in KIND_SEG:
            for b in BADGES:
                n = bar.get((key, b), 0)
                if n:
                    w = 100 * n / total
                    _seg(ax, y, left, w, colour, ink, n, b == "overflow")
                    left += w
        ax.text(-2, y, f"{d} ({total}){tag.get(d, '')}", ha="right", va="center", fontsize=8,
                color=INK)
        y += 1
    avg = wave_share(data, "kind", {"public_sector"})
    _vline(ax, avg, -0.55, y - 0.45, f"public sector, average: {avg:.0f}%")
    ax.set_xlim(-38, 101)
    ax.set_ylim(y - 0.4, -0.95)
    handles = [Patch(facecolor=c, edgecolor=SURFACE, label=lab)
               for k, lab, c, _ in KIND_SEG if k in present] + _badge_legend()
    _finish(fig, ax, title, note, path, handles, 2, (len(handles) + 1) // 2)


FOSSIL_COLOUR = {k: c for k, _, c, _ in FOSSIL} | {NOT_RUN[0]: NOT_RUN[2]}
UTILITY = {"yes": "utility: yes", "no": "utility: no", "unknown": "utility: not established"}


def business_text(r: dict) -> str:
    """What the business chart says beside each bar: the organisation's activity in the source's
    own words where the evidence records it (codebook 3.3, "sector as found"), else its business
    type; whether it supplies electricity, gas or heat (S1); and majority state ownership."""
    what = r.get("activity_as_found") or BUSINESS_TYPE.get(
        r["business_type"], r["business_type"].replace("_", " "))
    if len(what) > 48:
        what = what[:47].rstrip() + "…"
    parts = [what, UTILITY.get(r.get("utility") or "unknown", "utility: not established")]
    if r["state_ownership"] == "majority_state":
        parts.append("majority state-owned")
    return "; ".join(parts)


def short_name(name: str, n: int = 28) -> str:
    """The name up to its first bracket or comma (the country tests store a description after
    it), cut to n characters."""
    name = re.split(r" \(|, ", name, maxsplit=1)[0].strip()
    return name if len(name) <= n else name[: n - 1].rstrip() + "…"


def draw_business(data: list[dict], title: str, note: str, path: Path) -> None:
    """One bar per business organisation, its length the delegates (solid: Party badge, hatched:
    overflow), its colour the answer to the fossil question."""
    biz = [r for r in data if r["kind"] == "business_and_commercial"]
    tag = delegation_versions(data)
    top = max(r["delegates"] for r in biz)
    fig, ax = _fig(len(biz) + 1, width=9.0)
    y, present = 0, set()
    for g in (biz,):
        per_country: dict = {}
        for r in g:
            per_country[r["delegation"]] = per_country.get(r["delegation"], 0) + r["delegates"]
        last = None
        for c in sorted(per_country, key=lambda c: (-per_country[c], c)):
            for r in sorted((x for x in g if x["delegation"] == c),
                            key=lambda x: (-x["delegates"], x["name"])):
                if last is not None and c != last:
                    ax.plot([-1.4 * top, 2.6 * top], [y - 0.5] * 2, color=GREY, lw=0.6)
                who = f"{c} ({per_country[c]}){tag.get(c, '')}" if c != last else ""
                ax.text(-1.4 * top, y, who, ha="left", va="center", fontsize=8, color=INK)
                ax.text(-0.04 * top, y, short_name(r["name"]), ha="right", va="center", fontsize=7.5,
                        color=INK)
                colour = FOSSIL_COLOUR.get(r["fossil"], NO_EVIDENCE)
                present.add(r["fossil"])
                left = 0
                for b in BADGES:
                    if r[b]:
                        ax.barh(y, r[b], left=left, height=0.7, color=colour, edgecolor=SURFACE,
                                linewidth=1.5, **_hatch(colour, b == "overflow"))
                        left += r[b]
                ax.text(left + 0.04 * top, y, f"{r['delegates']}   {business_text(r)}",
                        ha="left", va="center", fontsize=7, color=MUTED)
                last = c
                y += 1
    ax.set_xlim(-1.4 * top, 2.6 * top)
    ax.set_ylim(y - 0.4, -0.8)
    handles = ([Patch(facecolor=c, edgecolor=SURFACE, label=f"Fits a tier: {lab.lower()}")
                for k, lab, c, _ in FOSSIL_TIER if k in present]
               + [Patch(facecolor=c, edgecolor=SURFACE, label=f"No link found: {lab.lower()}")
                  for k, lab, c, _ in FOSSIL_NONE if k in present]
               + [Patch(facecolor=c, edgecolor=MUTED if c in PALE else SURFACE, label=lab)
                  for k, lab, c, _ in FOSSIL_UNSURE if k in present]
               + _badge_legend())
    _finish(fig, ax, title, note, path, handles, 3, (len(handles) + 2) // 3)


FOSSIL_TIER = [s for s in FOSSIL if s[0].startswith("tier:")]   # strongest first
FOSSIL_NONE = [s for s in FOSSIL if s[0].startswith("none:")]
FOSSIL_UNSURE = [s for s in FOSSIL if s[0] == "unknown"] + [NOT_RUN]


def draw_fossil(data: list[dict], title: str, note: str, path: Path) -> None:
    """One list of delegations, each tagged with its codebook version when versions differ.
    No average line is drawn when they differ: fossil results of different versions are not
    pooled, and the note gives each version's figures."""
    per = by_delegation(data, "fossil")
    tag = delegation_versions(data)
    tier_keys = {s[0] for s in FOSSIL_TIER}
    tier_max = max([share(per[d], tier_keys) for d in per] + [0])
    left_lim = max(38.0, tier_max + 5)
    gap = 14.0
    u0 = 100 + gap  # where the "neither yes nor no" panel starts
    fig, ax = _fig(len(per), width=9.0)
    y, present = 0, {k for bar in per.values() for k, _ in bar}
    for g in (data,):
        for d in fossil_order(per):
            bar, total = per[d], sum(per[d].values())
            for segs, sign, start in ((FOSSIL_TIER, -1, 0.0), (FOSSIL_NONE, 1, 0.0),
                                      (FOSSIL_UNSURE, 1, u0)):
                x = start
                for key, _, colour, ink in segs:
                    for b in BADGES:
                        n = bar.get((key, b), 0)
                        if n:
                            w = sign * 100 * n / total
                            _seg(ax, y, x, w, colour, ink, n, b == "overflow")
                            x += w
            ax.text(-left_lim - 2, y, f"{d} ({total}){tag.get(d, '')}", ha="right",
                    va="center", fontsize=8, color=INK)
            y += 1
        if not tag:
            none_avg = wave_share(g, "fossil", {s[0] for s in FOSSIL_NONE})
            unk_avg = wave_share(g, "fossil", {"unknown"})
            _vline(ax, none_avg, -0.55, y - 0.45, f"average: {none_avg:.0f}%")
            _vline(ax, u0 + unk_avg, -0.55, y - 0.45, f"average: {unk_avg:.0f}%")
    bottom = y - 0.4
    for x0 in (0, u0):
        ax.plot([x0, x0], [-0.5, bottom], color=INK, lw=0.8)
    if not tier_max:
        ax.text(-left_lim / 2, (y - 1) / 2, "no organisation\nfits a fossil tier",
                ha="center", va="center", fontsize=7.5, color=MUTED, style="italic")
    head = -1.15
    ax.text(-1.5, head, "← fits a fossil tier", ha="right", va="bottom", fontsize=7.5,
            color=INK, weight="bold")
    ax.text(1.5, head, "no fossil link found →", ha="left", va="bottom", fontsize=7.5,
            color=INK, weight="bold")
    ax.text(u0 + 1.5, head, "neither yes nor no can be said", ha="left", va="bottom",
            fontsize=7.5, color=INK, weight="bold")
    ax.set_xlim(-left_lim - 52, u0 + 101)
    ax.set_ylim(bottom, -1.6)
    handles = ([Patch(facecolor=c, edgecolor=SURFACE, label=f"Fits a tier: {lab.lower()}")
                for _, lab, c, _ in FOSSIL_TIER]
               + [Patch(facecolor=c, edgecolor=SURFACE, label=f"No link found: {lab.lower()}")
                  for _, lab, c, _ in FOSSIL_NONE]
               + [Patch(facecolor=c, edgecolor=SURFACE, label=lab)
                  for k, lab, c, _ in FOSSIL_UNSURE if k in present or k == "unknown"]
               + _badge_legend())
    _finish(fig, ax, title, note, path, handles, 3, (len(handles) + 2) // 3)


SEQ = ("#e5f5e0", "#a1d99b", "#41ab5d", "#006d2c", "#00441b")   # one hue, light to dark
BASIS_MARK = {"register code": "R", "business type (C4)": "T", "word match": "W"}
SOE = "◆"


def sector_cells(data: list[dict]) -> tuple[list[str], list[str], dict]:
    """Rows (sector groups present, fossil-relevant first, "sector unknown" always last),
    columns (delegations, most business delegates first) and
    {(group, delegation): {"delegates", "orgs", "soe", "basis"}} for business organisations."""
    biz = [r for r in data if r["kind"] == "business_and_commercial"]
    cells: dict = {}
    for r in biz:
        c = cells.setdefault((r["sector_group"] or "unknown", r["delegation"]),
                             {"delegates": 0, "orgs": 0, "soe": 0, "basis": set()})
        c["delegates"] += r["delegates"]
        c["orgs"] += 1
        c["soe"] += r["state_ownership"] == "majority_state"
        if r["sector_basis"]:
            c["basis"].add(BASIS_MARK[r["sector_basis"]])
    groups = [k for k, _ in S.GROUPS if k != "unknown" and any(g == k for g, _ in cells)]
    groups.append("unknown")
    per: dict = {}
    for r in biz:
        per[r["delegation"]] = per.get(r["delegation"], 0) + r["delegates"]
    cols = sorted(per, key=lambda d: (-per[d], d))
    return groups, cols, cells


def draw_sector(data: list[dict], title: str, note: str, path: Path) -> None:
    """Business delegates by sector (rows) and delegation (columns). Shade: delegates, one hue.
    In each cell: delegates, organisations, the basis of the sector (R register code, T business
    type, W word match) and majority state-owned organisations (◆). The "sector unknown" row is
    grey and kept last, however large, so it is never mistaken for a sector."""
    groups, cols, cells = sector_cells(data)
    top = max(c["delegates"] for c in cells.values())
    n_c, n_r = len(cols) + 1, len(groups)
    fig, ax = plt.subplots(figsize=(max(7.5, 2.4 + 0.62 * n_c), 0.42 * n_r + 2.9), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    x0 = -3.3
    tag = delegation_versions(data)
    for j, d in enumerate(cols + ["All"]):
        ax.text(j + 0.5, -0.25, d + tag.get(d, ""), ha="left", va="bottom", fontsize=7,
                color=INK, rotation=40, rotation_mode="anchor")
    for i, g in enumerate(groups):
        y = i + (i >= len([k for k in groups if k in S.FOSSIL_RELEVANT])) * 0.35 \
            + (g == "unknown") * 0.35
        row = [cells.get((g, d)) for d in cols]
        tot = {"delegates": sum(c["delegates"] for c in row if c),
               "orgs": sum(c["orgs"] for c in row if c), "soe": sum(c["soe"] for c in row if c),
               "basis": set().union(*[c["basis"] for c in row if c])}
        ax.text(x0, y + 0.5, S.LABEL[g], ha="left", va="center", fontsize=7.5, color=INK,
                weight="bold" if g == "unknown" else "normal")
        for j, c in enumerate(row + [tot]):
            if not c or not c["delegates"]:
                ax.add_patch(plt.Rectangle((j + 0.04, y + 0.04), 0.92, 0.92, fc="none",
                                           ec=GREY, lw=0.4))
                continue
            if g == "unknown":
                fc, ink = NO_EVIDENCE, INK
            else:
                step = min(len(SEQ) - 1, int(len(SEQ) * c["delegates"] / (top + 1)))
                fc, ink = SEQ[step], "white" if step >= 2 else INK
            ax.add_patch(plt.Rectangle((j + 0.04, y + 0.04), 0.92, 0.92, fc=fc,
                                       ec=INK if j == len(cols) else SURFACE, lw=0.8))
            ax.text(j + 0.5, y + 0.38, str(c["delegates"]), ha="center", va="center",
                    fontsize=8, color=ink, weight="bold")
            sub = f"{c['orgs']} org" + (" " + "".join(sorted(c["basis"])) if c["basis"] else "")
            if c["soe"]:
                sub += f" {SOE}{c['soe']}"
            ax.text(j + 0.5, y + 0.72, sub, ha="center", va="center", fontsize=5.2, color=ink)
    n_fossil = len([k for k in groups if k in S.FOSSIL_RELEVANT])
    if n_fossil:
        ax.text(x0, -0.05, "Fossil-relevant sectors", ha="left", va="bottom", fontsize=7,
                color=MUTED, style="italic")
    bottom = n_r + 0.7
    ax.set_xlim(x0 - 0.1, n_c + 0.1)
    ax.set_ylim(bottom, -2.6)
    h = fig.get_figheight()
    note = "\n".join(textwrap.fill(line, int(fig.get_figwidth() * 18)) for line in note.split("\n"))
    fig.subplots_adjust(left=0.02, right=0.98, top=1 - 0.45 / h,
                        bottom=(0.3 + 0.14 * note.count("\n")) / h)
    fig.text(0.02, 1 - 0.12 / h, title, fontsize=10, color=INK, weight="bold", va="top")
    fig.text(0.02, 0.08 / h, note, fontsize=6.5, color=MUTED, va="bottom", linespacing=1.4)
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    print(path)


# ---- notes from the data -----------------------------------------------------------------------

def fossil_note(data: list[dict]) -> str:
    """One line per codebook version: how many fit a tier, how the "no link found" splits
    between strict and inferred, what code set on tier 3, and the version's own shares of
    delegates (given here because the chart draws no pooled average across versions).
    Computed, never written by hand."""
    lines = []
    for v, g in version_groups(data):
        done = [r for r in g if r["fossil"] != "not_run"]
        tier = sum(r["fossil"].startswith("tier:") for r in done)
        none_strict = sum(r["fossil"] == "none:established" for r in done)
        none_inf = sum(r["fossil"].startswith("none:") for r in done) - none_strict
        t3 = [r["tier3_set_by_code"].split(" ")[0] for r in done if r.get("tier3_set_by_code")]
        t3_text = (", ".join(f"{t3.count(k)} {k.replace('_', ' ')}" for k in sorted(set(t3)))
                   if t3 else "not run by code")
        none_pct = wave_share(g, "fossil", {s[0] for s in FOSSIL_NONE})
        unk_pct = wave_share(g, "fossil", {"unknown"})
        lines.append(f"Codebook {v or 'not recorded'}: {tier} of {len(done)} fit a tier; "
                     f"\"no link found\" {none_strict} strict, {none_inf} inferred; tier 3 by "
                     f"code: {t3_text}. Of delegates: {none_pct:.0f}% no link found, "
                     f"{unk_pct:.0f}% neither yes nor no.")
    return "\n".join(lines)


def versions(data: list[dict]) -> str:
    v = sorted({r["codebook"] for r in data if r["codebook"]})
    return "codebook " + (", ".join(v) if v else "version not recorded")


def charts(data: list[dict], scope: str, out: Path, prefix: str) -> None:
    """Write the four charts and the table for `data`. Kind is pooled across codebook versions
    (rules K1-K5 unchanged from 0.13 to 0.17, decisions.md 2026-11-26); the fossil result is
    shown per version and never averaged across versions. A delegation whose rows come from an
    earlier version carries the version in its label."""
    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"{prefix}_progress_PROVISIONAL.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)
    done = sum(r["kind"] != "not_run" for r in data)
    n_org = len(data)
    biz = [r for r in data if r["kind"] == "business_and_commercial"]
    head = (f"PROVISIONAL, {versions(data)} drafts, not validated. {done} of {n_org} "
            f"organisations classified; shares are of each row's delegates.")
    grouped = (" \"· 0.13\": classified with codebook 0.13; kind rules are unchanged, so kind "
               "is pooled."
               if len(version_groups(data)) > 1 else "")
    draw_kind(data, f"{scope}: who the delegates represent, by badge ({done} of {n_org} "
              "organisations)",
              head + " Media are counted under Other.\nSorted by public-sector share." + grouped
              + " \"European Union\" is the EU's own delegation, not an average of member states.",
              out / f"{prefix}_kind_PROVISIONAL.png")
    with_activity = sum(bool(r["activity_as_found"]) for r in biz)
    draw_business(data, f"{scope}: business organisations, delegates and fossil result "
                  f"({len(biz)} organisations)",
                  head.replace("shares are of each row's delegates", "bars count delegates")
                  + "\nBar colour: the fossil result. Text: what the organisation does in the "
                  f"source's words where recorded ({with_activity} of {len(biz)}; recorded from "
                  "wave 2), otherwise the codebook's business type (C4).",
                  out / f"{prefix}_business_PROVISIONAL.png")
    draw_fossil(data, f"{scope}: the fossil question by strength of evidence "
                f"({done} of {n_org} organisations)",
                head + " Sorted by \"no link found\": definitive, then some evidence.\n"
                + fossil_note(data), out / f"{prefix}_fossil_PROVISIONAL.png")
    if biz:
        draw_sector(data, f"{scope}: business delegates by sector and delegation "
                    f"({len(biz)} organisations)",
                    head.replace("shares are of each row's delegates", "cells count delegates")
                    + "\n" + sector_note(biz), out / f"{prefix}_sector_PROVISIONAL.png")


def sector_note(biz: list[dict]) -> str:
    """Counts by basis, and what the sector grouping is and is not."""
    n = {b: sum(r["sector_basis"] == b for r in biz) for b in BASIS_MARK}
    unk = sum((r["sector_group"] or "unknown") == "unknown" for r in biz)
    return (f"Sector is a derived grouping on NACE Rev. 2, not a codebook label, and the grouping "
            f"is for the lead researcher to approve. Basis: R register code {n['register code']}, "
            f"T business type (C4) {n['business type (C4)']}, W word match in the stored evidence "
            f"{n['word match']} (low confidence; fossil-relevant sectors only); sector unknown "
            f"{unk} of {len(biz)}. Unknown means no activity code was stored, not that the "
            f"organisation has no sector: codes are recorded from wave 2. {SOE} majority "
            "state-owned. Electricity (D35.1) includes nuclear and renewables; a sector is not "
            "a fossil link.")


def run_label(wave: int, data: list[dict]) -> str:
    return f"Wave {wave} · {versions(data)}"


def main() -> None:
    wave = int(sys.argv[1])
    data = rows(wave)
    label = run_label(wave, data)
    for r in data:
        r["run"] = label
    charts(data, f"Wave {wave}", ROOT / "outputs" / "draft-codebook" / f"wave{wave}",
           f"wave{wave}")


if __name__ == "__main__":
    main()
