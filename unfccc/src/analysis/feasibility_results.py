"""Tables for the feasibility test (notebook 05). PROVISIONAL, n=20.

Everything here reads the saved evidence and the two classification runs in
``data/processed/feasibility/`` and returns tables keyed by case code (F01-F20).
No organisation name is returned by any function, so nothing here can name an
organisation as fossil-linked. Nothing here feeds the proposal, the report or
``numbers.md``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analysis.feasibility import FEAS, read_records

ATTRS = {
    "status": "status",
    "R1 kind": "attributes.R1_kind.label",
    "R2 commercial activity": "attributes.R2_commercial.label",
    "R3 represents commercial interests": "attributes.R3_represents_commercial.label",
    "R4 business": "attributes.R4_business.label",
    "R5 sector": "attributes.R5_sector.label",
    "R6 state ownership": "attributes.R6_state_ownership.label",
    "R7 fossil-fuel proxy": "attributes.R7_fossil_link.rule",
    "R8 tier": "attributes.R8_tier.label",
}

PROXIES = {
    "R7.1": "own operations",
    "R7.2": "fossil-based electricity or heat",
    "R7.3": "other commercial dependence",
    "R7.4": "financing or ownership",
    "R7.5": "representation",
    "R7.6": "none established",
    "R7.7": "unknown",
}

STRATA = ["government word", "company legal form", "acronym-like", "other"]


def _evidence_level(case: str, url, feas: Path = FEAS):
    """Level of the evidence item with this URL in the case's evidence file."""
    if not isinstance(url, str):
        return None
    rec = json.loads((feas / "evidence" / f"{case}.json").read_text())
    levels = [e["level"] for e in rec.get("evidence", []) if e["source_url"] == url]
    return min(levels) if levels else None


def case_table(feas: Path = FEAS) -> pd.DataFrame:
    """One row per case: what the list says beside what each run found."""
    recs = read_records(feas)
    sample = pd.read_csv(feas / "sample.csv")[["case", "name_cue", "list_reading", "delegates"]]
    ev = recs["evidence"][["case", "status", "best_level"]].rename(
        columns={"status": "evidence_status"})
    out = sample.rename(columns={"name_cue": "stratum"}).merge(ev, on="case")
    for run in ("run1", "run2"):
        d = recs[run].set_index("case")
        n = run[-1]
        out[f"status_{n}"] = out.case.map(d["status"])
        out[f"R1_{n}"] = out.case.map(d[ATTRS["R1 kind"]])
        out[f"R4_{n}"] = out.case.map(d[ATTRS["R4 business"]])
        out[f"R5_{n}"] = out.case.map(d[ATTRS["R5 sector"]])
        out[f"R7_{n}"] = out.case.map(d[ATTRS["R7 fossil-fuel proxy"]])
    return out


def list_vs_evidence(ct: pd.DataFrame, run: str = "1") -> pd.DataFrame:
    """Counts: what the list fields suggest (rows) against R4 from evidence (columns)."""
    t = pd.crosstab(ct.list_reading, ct[f"R4_{run}"]).reindex(
        columns=["yes", "no", "unknown"], fill_value=0)
    t.columns = [f"evidence: business {c}" for c in t.columns]
    return t


def by_stratum(ct: pd.DataFrame, col: str, run: str = "1") -> pd.DataFrame:
    """Counts of a run's outcome per sampling stratum."""
    return pd.crosstab(ct.stratum, ct[f"{col}_{run}"]).reindex(STRATA).fillna(0).astype(int)


def proxies(feas: Path = FEAS) -> pd.DataFrame:
    """Per proxy and run: number of cases, their codes, and the evidence level cited."""
    recs = read_records(feas)
    rows = []
    for run in ("run1", "run2"):
        d = recs[run]
        for rule, label in PROXIES.items():
            hit = d[d[ATTRS["R7 fossil-fuel proxy"]] == rule]
            levels = [_evidence_level(c, u, feas) for c, u in
                      zip(hit.case, hit["attributes.R7_fossil_link.source_url"])]
            rows.append({
                "run": run[-1], "rule": rule, "proxy": label, "cases": len(hit),
                "case_codes": "|".join(hit.case) if rule != "R7.7" else "",
                "levels_cited": "|".join(sorted({str(l) for l in levels if l is not None})),
                "confidence": "|".join(sorted(set(hit["attributes.R7_fossil_link.confidence"].dropna()))),
            })
    return pd.DataFrame(rows)


def cohen_kappa(a: pd.Series, b: pd.Series) -> float | None:
    """Cohen's kappa for two label series; None when chance agreement is 1."""
    a, b = a.fillna("<missing>").astype(str), b.fillna("<missing>").astype(str)
    po = (a == b).mean()
    cats = set(a) | set(b)
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return None if pe == 1 else (po - pe) / (1 - pe)


def agreement(feas: Path = FEAS) -> pd.DataFrame:
    """Per attribute: how many of the cases the two runs labelled the same."""
    recs = read_records(feas)
    r1 = recs["run1"].set_index("case").sort_index()
    r2 = recs["run2"].set_index("case").sort_index()
    rows = []
    for name, col in ATTRS.items():
        a, b = r1[col], r2[col]
        same = (a.fillna("") == b.fillna(""))
        k = cohen_kappa(a, b)
        rows.append({"attribute": name, "agree": int(same.sum()), "of": len(same),
                     "percent": round(100 * same.mean(), 1),
                     "kappa": None if k is None else round(k, 2),
                     "differ_on": "|".join(same.index[~same])})
    return pd.DataFrame(rows)


def cost(feas: Path = FEAS) -> pd.DataFrame:
    """Tokens, tool calls and time per step, in total and per organisation."""
    log = pd.read_csv(feas / "run_log.csv")
    log["n_cases"] = log.cases.str.count(r"\|") + 1
    t = log.groupby("step").agg(calls=("batch", "count"), cases=("n_cases", "sum"),
                                tokens=("tokens", "sum"), tool_uses=("tool_uses", "sum"),
                                minutes=("duration_ms", lambda s: s.sum() / 60000))
    t["tokens_per_org"] = (t.tokens / t.cases).round(0)
    t["seconds_per_org"] = (t.minutes * 60 / t.cases).round(1)
    t["minutes"] = t.minutes.round(1)
    return t
