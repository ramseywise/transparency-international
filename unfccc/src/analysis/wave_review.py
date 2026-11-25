"""The review samples of one wave and the agreement of its second run. PROVISIONAL.

  sample N     writes data/processed/draft-codebook/wave<N>/review_sample.json:
               citation: a random 10% of the answered records (kind not unknown) plus every
                         record lookup.verify did not pass;
               run2:     a random 10% of all records, classified a second time blind.
  agreement N  compares run2/<case>.json with classified/<case>.json, attribute by attribute,
               and writes outputs/draft-codebook/wave<N>/wave<N>_agreement_PROVISIONAL.csv
               and, per attribute, wave<N>_agreement_summary_PROVISIONAL.csv.
  basis N [attr] writes wave<N>_<attr>_basis_PROVISIONAL.csv: for each record, the source type
               and level its label rests on (codebook 0.17, 5.5).
  citations N  counts citation_check.json by item and by record into
               wave<N>_citation_totals_PROVISIONAL.csv.

Seeds are fixed (SEED + wave) so the samples can be drawn again.
Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.wave_review sample 1
"""
import csv
import json
import math
import random
import sys
from pathlib import Path

from analysis.stats import agreement as agree

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261125
SHARE = 0.10


def folder(wave: int) -> Path:
    return ROOT / "data" / "processed" / "draft-codebook" / f"wave{wave}"


def _records(wave: int, sub: str = "classified") -> dict:
    return {p.stem: json.loads(p.read_text()) for p in sorted((folder(wave) / sub).glob("*.json"))}


def sample(wave: int) -> dict:
    recs = _records(wave)
    verify = json.loads((folder(wave) / "verify.json").read_text())["records"]
    cases = sorted(recs)
    answered = [c for c in cases if recs[c]["attributes"]["kind"]["label"] != "unknown"]
    flagged = sorted(c for c, v in verify.items() if v["outcome"] != "passed")
    rng = random.Random(SEED + wave)
    pool = [c for c in answered if c not in flagged]
    cite_random = sorted(rng.sample(pool, math.ceil(SHARE * len(answered))))
    run2 = sorted(random.Random(SEED + wave + 1000).sample(cases, math.ceil(SHARE * len(cases))))
    out = {"wave": wave, "seed": SEED + wave, "share": SHARE, "answered": len(answered),
           "records": len(cases), "citation_random": cite_random, "citation_flagged": flagged,
           "run2": run2}
    (folder(wave) / "review_sample.json").write_text(json.dumps(out, indent=1))
    return out


def _labels(rec: dict) -> dict:
    return {k: v.get("label") for k, v in rec["attributes"].items()}


def agreement(wave: int) -> list[dict]:
    first, second = _records(wave), _records(wave, "run2")
    rows = []
    for case in sorted(second):
        a, b = _labels(first[case]), _labels(second[case])
        for attr in sorted(set(a) | set(b)):
            rows.append({"case": case, "attribute": attr, "run1": a.get(attr),
                         "run2": b.get(attr), "same": a.get(attr) == b.get(attr)})
    out = ROOT / "outputs" / "draft-codebook" / f"wave{wave}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"wave{wave}_agreement_PROVISIONAL.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


def summary(rows: list[dict]) -> dict:
    by_attr: dict = {}
    for r in rows:
        by_attr.setdefault(r["attribute"], ([], []))
        by_attr[r["attribute"]][0].append(r["run1"])
        by_attr[r["attribute"]][1].append(r["run2"])
    return {k: agree(a, b) for k, (a, b) in by_attr.items()}


def _write(wave: int, name: str, rows: list[dict]) -> Path:
    out = ROOT / "outputs" / "draft-codebook" / f"wave{wave}"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"wave{wave}_{name}_PROVISIONAL.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return path


def citation_totals(wave: int) -> list[dict]:
    """Counts from citation_check.json, by item and by record, so quoted totals have a file."""
    checked = json.loads((folder(wave) / "citation_check.json").read_text())["checked"]
    rows = []
    for basis, values in (("item", [i["verdict"] for c in checked for i in c["items"]]),
                          ("record", [c["record_verdict"] for c in checked])):
        for verdict in sorted(set(values)):
            rows.append({"basis": basis, "verdict": verdict, "count": values.count(verdict),
                         "of": len(values)})
    _write(wave, "citation_totals", rows)
    return rows


def agreement_summary(wave: int, rows: list[dict]) -> list[dict]:
    out = []
    for attr, stats in sorted(summary(rows).items()):
        out.append({"attribute": attr} | {k: (round(v, 3) if isinstance(v, float) else v)
                                          for k, v in stats.items()})
    _write(wave, "agreement_summary", out)
    return out


def label_basis(wave: int, attribute: str = "kind") -> list[dict]:
    """Where each record's label for one attribute comes from (codebook 0.17, 5.5): the
    source_type and level of the stored evidence item its source_url cites. A label with no
    cited item (unknown, or set by code) has basis "none cited"."""
    rows = []
    for case, rec in _records(wave).items():
        ev_path = folder(wave) / "evidence" / f"{case}.json"
        items = json.loads(ev_path.read_text()).get("evidence") or [] if ev_path.exists() else []
        a = rec["attributes"].get(attribute) or {}
        hit = next((i for i in items if a.get("source_url") and i.get("source_url") == a["source_url"]), None)
        rows.append({"case": case, "attribute": attribute, "label": a.get("label"),
                     "confidence": a.get("confidence"),
                     "source_type": hit.get("source_type") if hit else "none cited",
                     "level": hit.get("level") if hit else ""})
    _write(wave, f"{attribute}_basis", rows)
    return rows


def main() -> None:
    step, wave = sys.argv[1], int(sys.argv[2])
    if step == "citations":
        for r in citation_totals(wave):
            print(r)
    elif step == "basis":
        rows = label_basis(wave, sys.argv[3] if len(sys.argv) > 3 else "kind")
        counts: dict = {}
        for r in rows:
            counts[r["source_type"]] = counts.get(r["source_type"], 0) + 1
        print(counts)
    elif step == "sample":
        s = sample(wave)
        print(f"citation: {len(s['citation_random'])} random + {len(s['citation_flagged'])} "
              f"flagged; run2: {len(s['run2'])}")
    else:
        rows = agreement(wave)
        cases = {r["case"] for r in rows}
        whole = sum(all(r["same"] for r in rows if r["case"] == c) for c in cases)
        print(f"records: {len(cases)}, identical on every attribute: {whole}")
        for r in agreement_summary(wave, rows):
            print(r)


if __name__ == "__main__":
    main()
