"""Build the review sheet for the proposed organisation name merges.

Reads   unfccc/data/processed/proposed_merges_eu.csv   (left unchanged)
Writes  unfccc/data/processed/merge_review_eu.csv      (one row per proposed pair, for the expert)
        unfccc/outputs/merge_review_summary.csv      (counts for any text)

Nothing is merged here. The sheet adds a proposed verdict to each pair and leaves
two empty columns for the expert's decision. Verdicts were set on 2026-11-24:
by reading the two names (basis "names only") or, for the pairs the names could
not settle, from official public pages opened that day (basis "public page").
Quotes from public pages are as returned by the page-fetching tool, which
extracts text with a small model; they have not been compared with the raw page.

Run from the workspace root:  uv run python -m cleaning.merge_review
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "unfccc/data/processed/proposed_merges_eu.csv"
SHEET = ROOT / "unfccc/data/processed/merge_review_eu.csv"
SUMMARY = ROOT / "unfccc/outputs/merge_review_summary.csv"
CHECKED_ON = "2026-11-24"

DEFAULT = (
    "same",
    "names only",
    "high",
    "The two names differ only in spelling, word order, punctuation, an added abbreviation or an added country name.",
    "",
    "",
)

NL = (
    "same",
    "public page",
    "medium",
    "One ministry. Its official English name is 'Ministry of Economic Affairs and Climate Policy'; "
    "'and Climate' is a shortened form. Caution: a separate climate ministry existed for a time "
    "(confirmed on Wikipedia only), and it was folded back in February 2026.",
    "https://www.government.nl/latest/news/2026/02/23/jetten-government-sworn-in",
    "Ministry of Economic Affairs and Climate Policy (was: Economic Affairs)",
)

DIFFERENT = (
    "different",
    "names only",
    "high",
    "Two different bodies with similar names. Do not merge.",
    "",
    "",
)

EMBASSY = (
    "unclear",
    "names only",
    "low",
    "One name gives no country for the embassy. It may be the Embassy in Türkiye or another Italian embassy. "
    "Public pages cannot settle this; the expert decides, or the delegation is asked.",
    "",
    "",
)

# key: the two organisation ids, sorted
SPECIAL: dict[tuple[str, str], tuple[str, str, str, str, str, str]] = {}


def put(a: str, b: str, value: tuple[str, str, str, str, str, str]) -> None:
    SPECIAL[tuple(sorted((a, b)))] = value


put("org_1ea11f6e23a3", "org_8a023db39b93", DIFFERENT)  # Milan / Turin
put("org_42f71f127582", "org_7368876015cf", DIFFERENT)  # Parma / Pavia
put("org_42f71f127582", "org_b2c9996192e0", DIFFERENT)  # Parma / Padua
put("org_7368876015cf", "org_b2c9996192e0", DIFFERENT)  # Pavia / Padua
put("org_c6c83bf368dc", "org_ff6ee8874728", DIFFERENT)  # UNEP / UNDP
put("org_3a269347dc25", "org_6b2ed6217658", DIFFERENT)  # Lithuania energy / environment

put(
    "org_88320d57244a",
    "org_c64a264e41fc",
    (
        "related",
        "public page",
        "medium",
        "Same network, separate legal bodies: the World Secretariat (a registered association in Bonn) and the "
        "European Secretariat (a limited company in Freiburg). Whether a regional office is merged with its "
        "parent is a rule for the expert. ICLEI Europe's own legal page refused access.",
        "https://iclei.org/e-library/icleis-governance-structure/ ; https://civitas.eu/legal",
        "ICLEI World Secretariat ... European Secretariat | ICLEI European Secretariat GmbH",
    ),
)
put(
    "org_0352ae71ff73",
    "org_6f905f0a1da5",
    (
        "related",
        "public page",
        "medium",
        "EbS is the television information service of the European Commission, not an independent organisation. "
        "Whether a service is merged with its parent body is a rule for the expert.",
        "https://audiovisual.ec.europa.eu/en/aboutebs",
        "This website is managed by the Directorate-General for Communication.",
    ),
)
put(
    "org_538b58e2c2b7",
    "org_cdcd8081711f",
    (
        "same",
        "public page",
        "medium",
        "'Environment and Land Security' is not the exact name of any Italian ministry, past or present. It mixes "
        "the old name (Environment, Land and Sea) with the current one (Environment and Energy Security). "
        "No other Italian ministry fits. Probably a mistyped name of the same ministry.",
        "https://www.mase.gov.it/portale/european-activities",
        "The Ministry of Environment and Energy Security (MASE) takes an active part in the European Union's decision-making",
    ),
)
put(
    "org_758a7695ebc0",
    "org_f2942ecacf6d",
    (
        "same",
        "public page",
        "high",
        "Both are variants of the one official name, 'Federal Public Service Foreign Affairs, Foreign Trade and "
        "Development Cooperation'. No second body was found.",
        "https://diplomatie.belgium.be/en",
        "Federal Public Service Foreign Affairs, Foreign Trade and Development Cooperation",
    ),
)
put(
    "org_27cd1bdeebcf",
    "org_52e78f171fcd",
    (
        "same",
        "public page",
        "medium",
        "'SOS Quinta dos Ingleses' is an environmental association in Carcavelos. No group called 'Inglesinhos' "
        "was found; not finding one is not proof that none exists.",
        "https://ppl.pt/en/node/1190104",
        "the NGO SOS Quinta dos Ingleses",
    ),
)
put(
    "org_42dc15290763",
    "org_de3586c0a9ac",
    (
        "same",
        "public page",
        "medium",
        "AdP SGPS is the holding company of the Águas de Portugal group. 'Águas de Portugal' alone could mean the "
        "holding company or the group as a whole. The company's own site could not be opened.",
        "https://unglobalcompact.org/what-is-gc/participants/150008",
        "AdP - Aguas de Portugal, SGPS (Holding Group AdP)",
    ),
)
put(
    "org_3ec9caf32a68",
    "org_d789ff6e533d",
    (
        "same",
        "public page",
        "high",
        "Denmark has one consular post in Istanbul, the Consulate General.",
        "https://um.dk/tyrkiet/en/the-trade-council/",
        "Consulate General of Denmark in Istanbul",
    ),
)
put(
    "org_8b16547eb769",
    "org_bfd4f9c5002e",
    (
        "same",
        "public page",
        "high",
        "WBGU is the German Advisory Council on Global Change. 'WGBU' is a transposed spelling; no body with that "
        "abbreviation was found. Both entries say 'on behalf of' the environment ministry (i.A. BMUKN).",
        "https://www.wbgu.de/en/",
        "German Advisory Council on Global Change",
    ),
)
put(
    "org_2bb13c",  # placeholder, replaced below by prefix match
    "org_2c3faa",
    (
        "same",
        "public page",
        "high",
        "The official English name is 'Italian Agency for Development Cooperation' (AICS). One entry leaves out 'Italian'.",
        "https://www.aics.gov.it/aics/profile-and-goals/?lang=en",
        "the Italian Agency for Development Cooperation",
    ),
)
put(
    "org_6aa26e",
    "org_cba9af",
    (
        "same",
        "public page",
        "high",
        "Expertise France is one company, a subsidiary of the AFD group. '(AFD)' in one entry names the parent only.",
        "https://expertisefrance.fr/en/our-governance",
        "the AFD group is the sole shareholder in our company.",
    ),
)

NL_IDS = ("org_7bdaac853838", "org_a2fe2f6dc60b")
EMBASSY_ID = "org_5a1bcd770ac1"

NOTES = {
    ("org_134a89", "org_e8fb4d"): "One entry has 'Cooperation', the other 'Development Cooperation'. Luxembourg has one foreign ministry; not checked on a public page.",
    ("org_0f4c83", "org_eae88d"): "One entry leaves out 'Public' before 'Health'. Not checked on a public page.",
    ("org_b4d45f", "org_c1fbe3"): "Word order and legal form differ. Not checked on a public page.",
    ("org_244348", "org_5de2e9"): "Same spelling apart from a full stop. Note for classification, not for merging: 'UBA i.A. BMUKN' means the German Environment Agency acting on behalf of the environment ministry.",
}


def lookup(a: str, b: str):
    key = tuple(sorted((a, b)))
    if key in SPECIAL:
        return SPECIAL[key]
    for (pa, pb), value in SPECIAL.items():  # entries stored with shortened ids
        if len(pa) < 16 and {a[: len(pa)], b[: len(pb)]} == {pa, pb}:
            return value
    if EMBASSY_ID in key:
        return EMBASSY
    if a in NL_IDS or b in NL_IDS:
        return NL
    for (pa, pb), note in NOTES.items():
        if {a[: len(pa)], b[: len(pb)]} == {pa, pb}:
            return (DEFAULT[0], DEFAULT[1], "medium" if "not checked" in note.lower() else "high", note, "", "")
    return DEFAULT


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["decision"] == "propose"]

    out = []
    for r in rows:
        verdict, basis, confidence, reason, url, quote = lookup(r["org_id_a"], r["org_id_b"])
        out.append(
            {
                "country": r["country"],
                "org_id_a": r["org_id_a"],
                "name_a": r["name_a"],
                "delegates_a": r["n_a"],
                "org_id_b": r["org_id_b"],
                "name_b": r["name_b"],
                "delegates_b": r["n_b"],
                "proposed_verdict": verdict,
                "basis": basis,
                "confidence": confidence,
                "reason": reason,
                "source_url": url,
                "source_quote_as_returned_by_fetch_tool": quote,
                "checked_on": CHECKED_ON,
                "expert_decision": "",
                "expert_note": "",
            }
        )
    order = {"unclear": 0, "related": 1, "different": 2, "same": 3}
    conf = {"low": 0, "medium": 1, "high": 2}
    out.sort(key=lambda r: (order[r["proposed_verdict"]], conf[r["confidence"]], r["country"], r["name_a"]))

    with SHEET.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    counts = Counter((r["proposed_verdict"], r["basis"], r["confidence"]) for r in out)
    with SUMMARY.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["proposed_verdict", "basis", "confidence", "pairs"])
        for (v, b, c), n in sorted(counts.items()):
            w.writerow([v, b, c, n])
        for v, n in sorted(Counter(r["proposed_verdict"] for r in out).items()):
            w.writerow([v, "all", "all", n])
        w.writerow(["all", "public page", "all", sum(1 for r in out if r["basis"] == "public page")])
        w.writerow(["all", "all", "all", len(out)])
    print(SUMMARY.read_text())


if __name__ == "__main__":
    main()
