"""Germany test of the draft codebook (0.13): PROVISIONAL, not a finding.

35 spellings from Germany's delegation are joined into organisations by a curated
variant table (each join has a reason), the "i.A." marker is split off by
``cleaning.orgs.split_acting_for``, and one classification record per
organisation is joined back to the delegates. Counts are kept on four lines for
each attribute (codebook 5.5): established (the strict label), limited evidence,
proxy, and unknown. The reporting group (codebook rule R1) is made here, by code.

    uv run python -I -m analysis.germany_test     writes outputs/draft-codebook/germany-test/

The counts written to ``outputs/`` carry no organisation names. The table by
organisation stays in the test folder under ``data/processed/``, because naming an
organisation as fossil-linked needs sign-off (workspace rule 7).
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from cleaning.orgs import split_acting_for

STUDY = Path(__file__).resolve().parents[2]
TEST = STUDY / "data" / "processed" / "draft-codebook" / "germany-test"
RECORDS = TEST / "classified-0.13"
OUT = STUDY / "outputs" / "draft-codebook" / "germany-test"

# Spellings joined by hand, with the reason. Not found by the automatic merge:
# its guards rightly refuse translations and short-word typos (see cleaning.orgs).
VARIANTS: dict[str, tuple[str, str]] = {
    "G21": ("G16", "same ministry: acronym with its English remit added"),
    "G24": ("G16", "same ministry: acronym with its German remit added"),
    "G26": ("G04", "same body: English name of the Auswärtiges Amt"),
    "G27": ("G07", "same body: English name of the Deutscher Bundestag"),
    "G32": ("G09", "same body: 'i.A' without the final full stop"),
    "G30": ("G29", "same body: with the 'i.A.' marker"),
    "G34": ("G33", "same body: letters swapped (WGBU for WBGU)"),
    "G28": ("G06", "same name: 'Median' for 'Medien'"),
}
# Spellings that name no organisation under the draft rules. G02 and G31 are a
# research question (whether a post decides its host body), open in decisions.md.
UNRESOLVED: dict[str, str] = {
    "G02": "generic text",          # "Botschaft": an embassy, not which body
    "G31": "not an organisation",   # "MdB": a member of parliament, a post
}

ATTRIBUTES = ("kind", "business_status", "state_ownership", "commercial_activity", "utility",
              "fossil_link_kind", "tier_1", "tier_2A", "tier_2B_O", "tier_2B_S", "tier_3")
FOSSIL_POSITIVE = {"own_operations", "fossil_electricity", "other_commercial_dependence",
                   "representing_fossil_interests"}
LINES = ("established", "limited_evidence", "proxy", "unknown")
# Headline order (codebook 5.2, and the comparison methodology of 2026-11-25): each
# delegate is counted once, at the first tier met; then "no identified link"; then
# "insufficient evidence". All flags stay in the table by organisation.
TIER_ORDER = (("tier_1", "Tier 1"), ("tier_2A", "Tier 2A"), ("tier_2B_O", "Tier 2B-O"),
              ("tier_3", "Tier 3"))
HEADLINE_ORDER = ("Tier 1", "Tier 2A", "Tier 2B-O", "Tier 3", "no identified link",
                  "insufficient evidence")
# An organisation with at least this many delegates and no established fossil line
# could move the headline on its own, so it goes to human review.
REVIEW_DELEGATES = 10
# Where an inferred value is the only trigger, the check is of the rule (P1, P2), done
# once for all such bodies, not of each body.
INFERRED_ONLY = "inferred value used"


def case_table(draw_rows: list[dict]) -> list[dict]:
    """One row per spelling: employer, body acted for, organisation key, and why."""
    out = []
    for r in draw_rows:
        employer, acting_for = split_acting_for(r["raw"])
        case = r["case"]
        if case in UNRESOLVED:
            key, why = None, UNRESOLVED[case]
        elif employer is None:
            key, why = None, "not an organisation"  # a bare "i.A. X" (codebook I2)
        elif case in VARIANTS:
            key, why = VARIANTS[case]
        else:
            key, why = case, "own spelling"
        out.append({**r, "employer": employer, "acting_for": acting_for, "org_key": key,
                    "join_reason": why})
    return out


def line_of(entry: dict | None) -> tuple[str, str]:
    """(line, value) for one attribute entry of a classification record."""
    if not isinstance(entry, dict):
        return "unknown", "no record"
    label = entry.get("label")
    if label and label != "unknown":
        return "established", label
    inferred = entry.get("inferred")
    if isinstance(inferred, dict) and inferred.get("basis") in ("limited_evidence", "proxy"):
        return inferred["basis"], inferred.get("label") or "unknown"
    return "unknown", entry.get("unknown_reason") or "no reason given"


def reporting_group(kind: str, ownership: str) -> str:
    """Codebook rule R1: state-owned bodies form a group of their own."""
    if kind in (None, "", "unknown"):
        return "unknown"
    if kind == "public_sector":
        return "public_sector"
    if ownership == "majority_state":
        return "state_owned_enterprise_or_non_profit"
    if ownership in (None, "", "unknown") and kind in ("business_and_commercial",
                                                       "civil_society_and_other_non_state"):
        return "unknown"
    return {"business_and_commercial": "business",
            "civil_society_and_other_non_state": "civil_society",
            "media": "media"}.get(kind, "other")


def _value(entry: dict | None, with_inferred: bool) -> str:
    line, value = line_of(entry)
    if line == "established" or (with_inferred and line != "unknown"):
        return value
    return "unknown"


def group_of(record: dict | None, with_inferred: bool = False) -> str:
    attrs = (record or {}).get("attributes") or {}
    return reporting_group(_value(attrs.get("kind"), with_inferred),
                           _value(attrs.get("state_ownership"), with_inferred))


def headline(row: dict) -> tuple[str, str]:
    """(headline, line) for one organisation row: the first tier met, else no link, else
    insufficient evidence. The line says whether it rests on evidence or on inference."""
    for attr, name in TIER_ORDER:
        if row.get(attr) == "met":
            return name, row[f"{attr}_line"]
    if row.get("fossil_link_kind") == "none_established":
        return "no identified link", row["fossil_link_kind_line"]
    return "insufficient evidence", "unknown"


I4_IDENTITY = "resolved by list context (proxy)"


def has_record(identity: str) -> bool:
    """True where a classification record may be read for this organisation."""
    return identity in ("resolved", I4_IDENTITY)


def by_list_context(record: dict) -> bool:
    """True if any attribute carries a value inferred under codebook rule I4."""
    return any(((e or {}).get("inferred") or {}).get("rule") == "I4"
               for e in (record.get("attributes") or {}).values())


def review_reasons(row: dict, record: dict | None) -> list[str]:
    """Why a researcher should look at this organisation; empty if no trigger applies."""
    if not has_record(row["identity"]) or record is None:
        return ["identity unresolved"]
    attrs = record.get("attributes") or {}
    out = []
    if row["identity"] == I4_IDENTITY:
        out.append("identity by list context only (I4)")
    ident = (attrs.get("identity_confidence") or {}).get("label")
    if ident not in ("high",):
        out.append(f"identity confidence {ident or 'not recorded'}")
    reasons = " ".join(str((v or {}).get("unknown_reason") or "") for v in attrs.values()
                       if isinstance(v, dict))
    if "several" in reasons:
        out.append("several possible legal entities")
    # Tier 3 is "not yet defined" for every body; only a link kind waiting on F4 is a trigger.
    if "not yet defined" in str((attrs.get("fossil_link_kind") or {}).get("unknown_reason") or ""):
        out.append("fossil rule not yet defined (F4)")
    if row["kind"] != "public_sector" and row["state_ownership_line"] == "unknown":
        out.append("ownership unclear")
    if (attrs.get("kind") or {}).get("confidence") == "low":
        out.append("kind at low confidence")
    if any(row[f"{a}_line"] in ("limited_evidence", "proxy") for a in ATTRIBUTES):
        out.append(INFERRED_ONLY)
    if row["headline"] == "insufficient evidence" and not any("F4" in x for x in out):
        out.append("fossil link unresolved")
    if row["delegates"] >= REVIEW_DELEGATES and row["headline_line"] != "established":
        out.append(f"{row['delegates']} delegates: could move the headline")
    return out


def _topup_by_case(folder: Path) -> dict[str, list[dict]]:
    """Top-up results by case. A file holds one case, or several under ``by_case``."""
    out: dict[str, list[dict]] = defaultdict(list)
    for f in sorted(folder.glob("*.json")):
        j = json.loads(f.read_text())
        parts = j["by_case"].items() if "by_case" in j else [(j.get("case") or f.stem, j)]
        for case, part in parts:
            out[case].append({**part, "_file": f.name})
    return out


def merge_evidence(cases: list[dict], original: Path, topup: Path) -> dict[str, dict]:
    """One evidence record per organisation: the items of every spelling joined to it, then
    the top-up items. Duplicates (same page and quote) are kept once."""
    tops = _topup_by_case(topup)
    merged: dict[str, dict] = {}
    for c in cases:
        key = c["org_key"]
        if key is None:
            continue
        rec = merged.setdefault(key, {"org_key": key, "spellings": [], "matched_entity": None,
                                      "status_by_source": {}, "notes": [], "searches": [],
                                      "evidence": []})
        rec["spellings"].append(c["case"])
        orig = json.loads((original / f"{c['case']}.json").read_text())
        rec["matched_entity"] = rec["matched_entity"] or orig.get("matched_entity")
        rec["status_by_source"][f"{c['case']} first lookup"] = orig.get("status")
        rec["searches"] += orig.get("searches") or []
        items = [{**i, "from": f"{c['case']} first lookup"} for i in orig.get("evidence") or []]
        for t in tops.get(c["case"], []):
            items += [{**i, "from": f"top-up {t['_file']}"} for i in t.get("evidence") or []]
            if t.get("matched_entity"):
                rec["matched_entity"] = t["matched_entity"]
            if t.get("status"):
                rec["status_by_source"][f"top-up {t['_file']}"] = t["status"]
            for k in ("status_reason", "note", "notes", "reason"):
                if isinstance(t.get(k), str):
                    rec["notes"].append(f"top-up {t['_file']}: {t[k]}")
        seen = {(i["source_url"], i.get("quote")) for i in rec["evidence"]}
        for i in items:
            if (i.get("source_url"), i.get("quote")) not in seen:
                seen.add((i.get("source_url"), i.get("quote")))
                rec["evidence"].append(i)
    return merged


def load_records(folder: Path = RECORDS) -> dict[str, dict]:
    return {f.stem: json.loads(f.read_text()) for f in sorted(folder.glob("*.json"))}


def by_organisation(cases: list[dict], records: dict[str, dict]) -> list[dict]:
    """One row per organisation (and per unresolved spelling), delegates summed."""
    rows: dict[str, dict] = {}
    for c in cases:
        key = c["org_key"] or c["case"]
        row = rows.setdefault(key, {"org_key": key, "cases": [], "delegates": 0, "party": 0,
                                    "overflow": 0, "identity": "resolved" if c["org_key"] else
                                    f"unresolved ({c['join_reason']})"})
        row["cases"].append(c["case"])
        for k in ("delegates", "party", "overflow"):
            row[k] += int(c[k])
    for key, row in rows.items():
        rec = records.get(key) if row["identity"] == "resolved" else None
        if rec and ((rec.get("attributes") or {}).get("kind") or {}).get(
                "unknown_reason") == "could be several entities":
            if by_list_context(rec):
                # Codebook I4: the list's own context points to one body. The strict labels
                # stay unknown; the record is kept for its values beside the strict line.
                row["identity"] = I4_IDENTITY
            else:
                # Codebook I1: a name borne by several legal entities is identity unresolved.
                row["identity"] = "unresolved (could be several entities)"
                rec = None
        attrs = (rec or {}).get("attributes") or {}
        row["name"] = (rec or {}).get("matched_entity") or ""
        for a in ATTRIBUTES:
            line, value = line_of(attrs.get(a)) if rec else ("unknown", "identity unresolved")
            row[a] = value
            row[f"{a}_line"] = line
        row["reporting_group"] = group_of(rec) if rec else "unknown"
        row["reporting_group_with_inferred"] = group_of(rec, True) if rec else "unknown"
        row["headline"], row["headline_line"] = headline(row)
        why = review_reasons(row, rec)
        row["human_review"] = ("no" if not why else
                               "batch (rule P1/P2)" if why == [INFERRED_ONLY] else "individual")
        row["review_reasons"] = "; ".join(why)
        row["cases"] = " ".join(row["cases"])
    return list(rows.values())


def counts(orgs: list[dict]) -> list[dict]:
    """Organisations and delegates by attribute, line and value. No names."""
    tally: dict[tuple, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for o in orgs:
        for a in ATTRIBUTES:
            t = tally[(a, o[f"{a}_line"], o[a])]
            t[0] += 1; t[1] += o["delegates"]; t[2] += o["party"]; t[3] += o["overflow"]
        for g in ("reporting_group", "reporting_group_with_inferred"):
            t = tally[(g, "derived", o[g])]
            t[0] += 1; t[1] += o["delegates"]; t[2] += o["party"]; t[3] += o["overflow"]
    return [{"attribute": a, "line": ln, "value": v, "organisations": n, "delegates": d,
             "party": p, "overflow": ov}
            for (a, ln, v), (n, d, p, ov) in sorted(tally.items())]


def fossil_lines(orgs: list[dict]) -> list[dict]:
    """The headline: delegates by what is known of their organisation's fossil fuel link."""
    def bucket(o: dict) -> str:
        line, value = o["fossil_link_kind_line"], o["fossil_link_kind"]
        if line == "unknown":
            return "unknown"
        side = "link" if value in FOSSIL_POSITIVE else "no link"
        if line == "proxy" and side == "link":
            return "possible link (proxy)"
        return f"{side} ({line.replace('_', ' ')})"
    tally: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for o in orgs:
        t = tally[bucket(o)]
        t[0] += 1; t[1] += o["delegates"]
    total = sum(o["delegates"] for o in orgs)
    return [{"line": k, "organisations": n, "delegates": d,
             "share_of_delegates": round(100 * d / total, 1)}
            for k, (n, d) in sorted(tally.items(), key=lambda x: -x[1][1])]


def headline_counts(orgs: list[dict]) -> list[dict]:
    """Delegates once each, by headline and line, split by badge. No names."""
    tally: dict[tuple, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for o in orgs:
        t = tally[(o["headline"], o["headline_line"])]
        t[0] += 1; t[1] += o["delegates"]; t[2] += o["party"]; t[3] += o["overflow"]
    total = sum(o["delegates"] for o in orgs)
    rows = sorted(tally.items(), key=lambda x: (HEADLINE_ORDER.index(x[0][0]), LINES.index(x[0][1])))
    return [{"headline": h, "line": ln, "organisations": n, "delegates": d, "party": p,
             "overflow": ov, "share_of_delegates": round(100 * d / total, 1)}
            for (h, ln), (n, d, p, ov) in rows]


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def write_merged_evidence(cases: list[dict]) -> int:
    """Write evidence-0.13/<org_key>.json for the classifier; returns the number written."""
    merged = merge_evidence(cases, TEST / "evidence", TEST / "evidence-topup")
    folder = TEST / "evidence-0.13"
    folder.mkdir(exist_ok=True)
    for key, rec in merged.items():
        (folder / f"{key}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    return len(merged)


def main() -> None:
    import sys
    draw = list(csv.DictReader(open(TEST / "germany_test_draw.csv")))
    cases = case_table(draw)
    if "--merge-evidence" in sys.argv:
        print(f"evidence records written: {write_merged_evidence(cases)}")
        return
    orgs = by_organisation(cases, load_records())
    _write(TEST / "germany_cases_0.13_PROVISIONAL.csv", cases)
    _write(TEST / "germany_by_organisation_0.13_PROVISIONAL.csv", orgs)
    _write(OUT / "germany_counts_PROVISIONAL.csv", counts(orgs))
    fl = fossil_lines(orgs)
    _write(OUT / "germany_fossil_lines_PROVISIONAL.csv", fl)
    hl = headline_counts(orgs)
    _write(OUT / "germany_headline_PROVISIONAL.csv", hl)
    review = [{"human_review": level,
               "organisations": sum(o["human_review"] == level for o in orgs),
               "delegates": sum(o["delegates"] for o in orgs if o["human_review"] == level)}
              for level in ("individual", "batch (rule P1/P2)", "no")]
    _write(OUT / "germany_review_PROVISIONAL.csv", review)
    print(f"spellings {len(cases)}; organisations and unresolved spellings {len(orgs)}; "
          f"delegates {sum(o['delegates'] for o in orgs)}")
    for r in fl:
        print(f"  {r['line']:32s} orgs {r['organisations']:2d}  delegates {r['delegates']:3d}"
              f"  {r['share_of_delegates']}%")
    for r in hl:
        print(f"  headline {r['headline']:22s} {r['line']:17s} orgs {r['organisations']:2d}"
              f"  delegates {r['delegates']:3d} (P {r['party']}, O {r['overflow']})")
    for level in ("individual", "batch (rule P1/P2)", "no"):
        sel = [o for o in orgs if o["human_review"] == level]
        print(f"  human review {level:20s} orgs {len(sel):2d}  delegates "
              f"{sum(o['delegates'] for o in sel):3d}")


if __name__ == "__main__":
    main()
