"""All runs so far in one set of charts. PROVISIONAL.

Takes in the country tests (Germany, Luxembourg, Saudi Arabia, codebook 0.13) and every wave
folder that has an inputs.json (wave 1 at 0.16; France, wave 2, and Italy, wave 3, appear as they
run). Kind is pooled across codebook versions, because rules K1-K5 have not changed
(decisions.md 2026-11-26); the fossil result is summarised per version and never pooled.

Writes to outputs/draft-codebook/all/: all_{kind,business,fossil,sector}_PROVISIONAL.png,
all_summary_PROVISIONAL.csv (shares by delegation and badge, weighted and unweighted averages) and
all_progress_PROVISIONAL.csv, the same charts and columns as analysis.wave_progress.
Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.all_progress
"""
import csv
import json
import re

from analysis import sector as S
from analysis import wave_progress as W

BASE = W.ROOT / "data" / "processed" / "draft-codebook"
COUNTRY_TESTS = (("Germany", "germany-test", "germany"),
                 ("Luxembourg", "luxembourg-test", "luxembourg"),
                 ("Saudi Arabia", "saudi-arabia-test", "saudi_arabia"))
TEST_VERSION = "0.13"
TIER_COLS = W.TIERS
LABELS = {"met", "not_met"}


def _known(value: str, allowed) -> str:
    """A label from the list, or "unknown": the tests store the unknown reason in its place."""
    return value if value in allowed else "unknown"


def fossil_from_test(row: dict) -> str:
    head, line = row["headline"], row["headline_line"]
    if head.startswith("Tier"):
        return f"tier:{line}"
    if head == "no identified link":
        return f"none:{line}"
    return "unknown"


def tiers_from_test(row: dict, inferred: bool) -> str:
    out = []
    for t in TIER_COLS:
        v, line = row[t], row[f"{t}_line"]
        if v in LABELS and (line != "established") == inferred:
            out.append(f"{t}={v}" + (f" ({line})" if inferred else ""))
    return "; ".join(out)


def _evidence(folder: str, row: dict) -> dict:
    case = re.split(r"[;\s]+", row.get("cases") or row["org_key"])[0]
    p = BASE / folder / f"evidence-{TEST_VERSION}" / f"{case}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def test_row(country: str, row: dict, run: str, ev: dict | None = None) -> dict:
    """One country-test organisation in the columns of wave_progress.rows. The test tables keep
    the evidence step's description of the body after its name; it is read as stored text for
    the sector (word match only)."""
    biz = row["business_type"]
    desc = row["name"].split(" (", 1)[1] if " (" in row["name"] else ""
    sec = S.columns(row["kind_group"].startswith("business"), biz, ev or {}, None, desc)
    return sec | {"case": row["org_key"], "name": row["name"], "codebook": TEST_VERSION,
            "delegation": country, "delegates": int(row["delegates"]),
            "party": int(row["party"]), "overflow": int(row["overflow"]),
            "kind": row["kind_group"] or "not_identified",
            "fossil": fossil_from_test(row),
            "tiers_strict": tiers_from_test(row, inferred=False),
            "tiers_inferred": tiers_from_test(row, inferred=True),
            "fossil_unknown_reason": "" if row["fossil_link_kind"] in ("none_established",)
            else row["fossil_link_kind"],
            "tier3_unknown_reason": "" if row["tier_3"] in LABELS else row["tier_3"],
            "tier3_set_by_code": "",
            "business_type": biz if biz in W.BUSINESS_TYPE or biz == "not_business"
            else "unknown",
            "state_ownership": row["state_ownership"],
            "utility": _known(row["utility"], ("yes", "no")),
            "activity_as_found": "", "run": run}


def country_test_rows() -> list[dict]:
    run = f"Country tests · codebook {TEST_VERSION}"
    out = []
    for country, folder, stem in COUNTRY_TESTS:
        path = BASE / folder / f"{stem}_by_organisation_with_lookups_{TEST_VERSION}_PROVISIONAL.csv"
        with open(path, newline="") as fh:
            out += [test_row(country, r, run, _evidence(folder, r)) for r in csv.DictReader(fh)]
    return out


def waves() -> list[int]:
    found = [int(m.group(1)) for p in BASE.glob("wave*/inputs.json")
             if (m := re.fullmatch(r"wave(\d+)", p.parent.name))]
    return sorted(found)


def all_rows() -> list[dict]:
    data = country_test_rows()
    for n in waves():
        wave = W.rows(n)
        label = W.run_label(n, wave)
        data += [r | {"run": label} for r in wave]
    return data


KINDS = {"public_sector": "public_sector", "civil_society": "civil_society_and_other_non_state",
         "other": "other", "business": "business_and_commercial", "not_identified": "not_identified"}
SUMMARY_COLS = ("codebook", "delegation", "badge", "delegates", "organisations") + tuple(
    f"{k}_pct" for k in KINDS) + ("business_state_majority", "fossil_tier_orgs",
                                  "fossil_unknown_pct")


def _shares(rows: list[dict], badge: str) -> dict:
    """Shares of delegates by kind for one group of rows, counting only the given badge
    ("party", "overflow" or "delegates" for both)."""
    n = sum(r[badge] for r in rows)
    out = {"badge": badge, "delegates": n, "organisations": sum(r[badge] > 0 for r in rows)}
    for k, key in KINDS.items():
        out[f"{k}_pct"] = round(100 * sum(r[badge] for r in rows if r["kind"] == key) / n, 1) if n else ""
    biz = [r for r in rows if r["kind"] == KINDS["business"] and r[badge] > 0]
    out["business_state_majority"] = sum(r["state_ownership"] == "majority_state" for r in biz)
    out["fossil_tier_orgs"] = sum(r["fossil"].startswith("tier:") for r in rows if r[badge] > 0)
    out["fossil_unknown_pct"] = (round(100 * sum(r[badge] for r in rows
                                                 if r["fossil"] == "unknown") / n, 1) if n else "")
    return out


def summary(data: list[dict]) -> list[dict]:
    """Per codebook version: each delegation, by badge, plus two averages that answer different
    questions: `all delegates (weighted)` pools every delegate, so large delegations weigh more
    (the figure the charts draw); `mean of delegations (unweighted)` averages the delegations'
    percentages, so each delegation counts once. When there is more than one version, a block
    "all versions (kind only)" adds the pooled kind shares; its fossil columns are left blank,
    because fossil results are never pooled across versions."""
    out = []
    groups = W.version_groups(data)
    blocks = [(v, g, False) for v, g in groups]
    if len(groups) > 1:
        blocks.append(("all versions (kind only)", data, True))
    for run, g, kind_only in blocks:
        per = {}
        for r in g:
            per.setdefault(r["delegation"], []).append(r)
        for badge in ("delegates", "party", "overflow"):
            rows_ = [{"codebook": run, "delegation": d} | _shares(rs, badge)
                     for d, rs in per.items()]
            pooled = {"codebook": run, "delegation": "all delegates (weighted)"} | _shares(g, badge)
            if kind_only:
                for x in rows_ + [pooled]:
                    x["fossil_tier_orgs"] = x["fossil_unknown_pct"] = ""
            out += rows_
            out.append(pooled)
            mean = {"codebook": run, "delegation": "mean of delegations (unweighted)",
                    "badge": badge}
            for k in KINDS:
                vals = [x[f"{k}_pct"] for x in rows_ if x[f"{k}_pct"] != ""]
                mean[f"{k}_pct"] = round(sum(vals) / len(vals), 1) if vals else ""
            out.append(mean)
    return out


def main() -> None:
    data = all_rows()
    out = W.ROOT / "outputs" / "draft-codebook" / "all"
    W.charts(data, "All delegations so far", out, "all")
    with open(out / "all_summary_PROVISIONAL.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, SUMMARY_COLS)
        w.writeheader()
        w.writerows(summary(data))


if __name__ == "__main__":
    main()
