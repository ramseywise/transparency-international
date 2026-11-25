"""Choose the second test country by the rule logged in docs/decisions.md (2026-11-25).

The rule was written before any count by country was looked at (workspace rule 9):

* candidates: the EU member delegations other than Germany;
* workable size: at most ``MAX_SPELLINGS`` organisation spellings;
* among those, the most Party overflow delegates whose organisation name carries a
  company legal form; ties go to the higher share of overflow badges.

A legal form in a name is a signal read before any lookup. It is not a classification.

    uv run python -I -m analysis.country_pick     writes outputs/draft-codebook/country_pick.csv
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

STUDY = Path(__file__).resolve().parents[2]
DELEGATES = STUDY / "data" / "processed" / "delegates_eu.parquet"
OUT = STUDY / "outputs" / "draft-codebook" / "country_pick.csv"
MAX_SPELLINGS = 60
EXCLUDED = ("Germany", "European Union")
# Company legal forms of EU member states and common international ones. Matched as whole
# words, with or without full stops, case as usually written.
LEGAL_FORMS = (
    r"GmbH", r"AG", r"KG", r"SE", r"S\.?A\.?", r"S\.?A\.?S\.?", r"S\.?A\.?R\.?L\.?", r"S\.?p\.?A\.?",
    r"S\.?r\.?l\.?", r"S\.?L\.?", r"Lda\.?", r"Ltd\.?", r"Limited", r"plc", r"PLC", r"Inc\.?", r"LLC",
    r"Corp\.?", r"B\.?V\.?", r"N\.?V\.?", r"AB", r"Oy", r"Oyj", r"A/S", r"ApS", r"AS", r"a\.s\.",
    r"s\.r\.o\.", r"Sp\. ?z ?o\.? ?o\.?", r"Kft\.?", r"Zrt\.?", r"Nyrt\.?", r"d\.o\.o\.", r"d\.d\.",
    r"SRL", r"OÜ", r"UAB", r"SIA", r"EOOD", r"OOD", r"EAD", r"A\.?E\.?", r"DAC", r"AD",
)
_FORM = re.compile(r"(?<![\w.])(?:" + "|".join(LEGAL_FORMS) + r")(?![\w])")


def has_legal_form(name: object) -> bool:
    """True if the name carries a company legal form. Blank fields (None, NaN) are False."""
    return isinstance(name, str) and bool(_FORM.search(name))


def table(delegates: pd.DataFrame) -> pd.DataFrame:
    """One row per delegation: size, overflow, and delegates under a company-form name."""
    d = delegates.assign(company_form=delegates["Home organization"].map(has_legal_form),
                         overflow=delegates["badge_type"].eq("Party overflow"))
    g = d.groupby("nominated_by_clean")
    t = pd.DataFrame({
        "delegates": g.size(),
        "overflow": g["overflow"].sum(),
        "spellings": g["org_id"].nunique(),
        "no_org_id": g["org_id"].apply(lambda s: int(s.isna().sum())),
        "company_form": g["company_form"].sum(),
        "company_form_overflow": d[d.overflow].groupby("nominated_by_clean")["company_form"].sum(),
    }).fillna(0).astype(int)
    t["overflow_share"] = (t["overflow"] / t["delegates"]).round(3)
    t["candidate"] = ~t.index.isin(EXCLUDED)
    t["workable"] = t["candidate"] & (t["spellings"] <= MAX_SPELLINGS)
    return t.sort_values(["workable", "company_form_overflow", "overflow_share"], ascending=False)


def pick(t: pd.DataFrame) -> str:
    return t[t["workable"]].index[0]


def main() -> None:
    t = table(pd.read_parquet(DELEGATES))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT)
    print(t.to_string())
    print("picked:", pick(t))


if __name__ == "__main__":
    main()
