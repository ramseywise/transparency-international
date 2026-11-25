"""Put two reference tables beside the participant list: one row per badge, nothing classified.

Inputs (none of them changed):
- unfccc/data/raw/unfcc-2026.csv                the participant list, every sheet
- unfccc/data/processed/admitted_ngos.csv       UNFCCC admitted NGOs (cleaning.admitted_ngos)
- literature/unfccc/data/processed/tables/bankingonclimatechaos-sector-tables-2026.csv
                                                65 banks in the expansion league tables (cleaning.bank_tables)

Outputs, in unfccc/data/processed/:
- delegates_with_references.csv   every badge, with the admitted NGO that nominated it (name,
                                  constituency, city, country, website) and any bank whose name
                                  appears in its home organisation or nominator
- bank_matches.csv                the bank matches at organisation level, for review
- badges_match_stats.json         the counts printed at the end

All added columns are provisional matches by name. A match is not a classification, and no match
is not evidence that there is no link: admission and constituency are registration facts (codebook
rule G2) and the place of banks is not yet defined (codebook section 9, tier 3).

The file holds delegates' names (workspace rule 8): never print them in a report or a chat reply.

Run from the workspace root:
    uv run python -I -m cleaning.badges
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

from cleaning.clean import _HONORIFICS, ascii_fold

PARTICIPANTS = Path("unfccc/data/raw/unfcc-2026.csv")
ADMITTED = Path("unfccc/data/processed/admitted_ngos.csv")
BANKS = Path("literature/unfccc/data/processed/tables/bankingonclimatechaos-sector-tables-2026.csv")
OUT = Path("unfccc/data/processed/delegates_with_references.csv")
OUT_BANKS = Path("unfccc/data/processed/bank_matches.csv")
OUT_STATS = Path("unfccc/data/processed/badges_match_stats.json")

NGO_SHEET = "Non-governmental organizations"
KEEP = [
    "sheet", "Nominated by", "Name", "Functional title", "Department", "Home organization",
    "Relation", "Type of home organization", "Funding source", "Type of funding source",
]

# Search terms for each bank in the league tables, written by the assistant on 2026-11-25 for
# matching only (they are spellings of the bank's own name, not subsidiaries or asset managers).
# A term matches whole words anywhere in the organisation's name; "^" means the name must start
# with it; "=" means the name must be exactly it. Ambiguous short names are anchored on purpose.
BANK_TERMS = {
    "ANZ": ["^anz", "australia and new zealand banking"],
    "Agricultural Bank of China": ["agricultural bank of china"],
    "BMO Financial Group": ["^bmo", "bank of montreal"],
    "BNP Paribas": ["bnp paribas", "bnpp"],
    "Banco Bilbao Vizcaya Argentaria (BBVA)": ["bbva", "banco bilbao vizcaya argentaria"],
    "Bank of America": ["bank of america"],
    "Bank of Beijing": ["bank of beijing"],
    "Bank of China": ["^bank of china"],
    "Bank of Communications": ["^bank of communications"],
    "Bank of Jiangsu": ["bank of jiangsu"],
    "Barclays": ["barclays"],
    "CIBC": ["cibc", "canadian imperial bank of commerce"],
    "CITIC": ["citic"],
    "Capital One Financial": ["capital one"],
    "China Construction Bank": ["china construction bank"],
    "China Everbright": ["china everbright"],
    "China Merchants Bank": ["china merchants bank"],
    "China Minsheng Banking": ["china minsheng"],
    "Citigroup": ["citigroup", "citibank", "^citi"],
    "Commerzbank": ["commerzbank"],
    "Commonwealth Bank of Australia": ["commonwealth bank"],
    "Crédit Agricole": ["credit agricole"],
    "Crédit Mutuel": ["credit mutuel"],
    "DBS": ["^dbs"],
    "DZ Bank": ["dz bank"],
    "Danske Bank": ["danske bank"],
    "Deutsche Bank": ["deutsche bank"],
    "Goldman Sachs": ["goldman sachs"],
    "Groupe BPCE": ["bpce"],
    "HSBC": ["hsbc"],
    "Hua Xia Bank": ["hua xia bank", "huaxia bank"],
    "ING Group": ["=ing", "ing group", "ing groep", "ing bank"],
    "Industrial Bank Company": ["^industrial bank co", "china industrial bank"],
    "Industrial and Commercial Bank of China": ["industrial and commercial bank of china", "icbc"],
    "Intesa Sanpaolo": ["intesa sanpaolo"],
    "JPMorgan Chase": ["jpmorgan chase", "jp morgan chase", "j p morgan chase", "jpmorgan", "jp morgan", "j p morgan"],
    "KB Financial Group": ["kb financial", "kookmin bank"],
    "La Banque Postale": ["la banque postale", "^banque postale"],
    "La Caixa Group": ["la caixa", "caixabank"],
    "Lloyds Banking Group": ["lloyds banking", "lloyds bank"],
    "Mitsubishi UFJ Financial": ["mitsubishi ufj", "mufg"],
    "Mizuho Financial": ["mizuho"],
    "Morgan Stanley": ["morgan stanley"],
    "NatWest": ["natwest", "national westminster"],
    "National Australia Bank": ["national australia bank"],
    "Nordea": ["nordea"],
    "PNC Financial Services": ["^pnc"],
    "Ping An Insurance Group": ["ping an"],
    "Postal Savings Bank of China": ["postal savings bank of china"],
    "Rabobank": ["rabobank"],
    "Royal Bank of Canada": ["royal bank of canada", "^rbc"],
    "SMBC Group": ["smbc", "sumitomo mitsui banking", "sumitomo mitsui financial"],
    "Santander": ["banco santander", "santander bank", "^santander"],
    "Scotiabank": ["scotiabank", "bank of nova scotia"],
    "Shanghai Pudong Development Bank": ["shanghai pudong development bank", "spd bank"],
    "Société Générale": ["societe generale"],
    "Standard Chartered": ["standard chartered"],
    "State Bank of India": ["state bank of india"],
    "Toronto-Dominion Bank": ["toronto dominion", "td bank"],
    "Truist Financial": ["truist"],
    "UBS": ["ubs"],
    "US Bancorp": ["us bancorp", "u s bancorp"],
    "UniCredit": ["unicredit"],
    "Wells Fargo": ["wells fargo"],
    "Westpac": ["westpac"],
}


# Names that are not a spelling of a listed bank but may belong to one (a subsidiary, a former
# name). The link is the assistant's suggestion and has NO recorded source yet: these are listed
# for a researcher to confirm or reject, and are never counted as the bank until then.
UNCONFIRMED_TERMS = {
    "BNP Paribas": [],
    "Crédit Agricole": ["amundi"],
    "Groupe BPCE": ["natixis"],
    "Banco Bilbao Vizcaya Argentaria (BBVA)": ["garanti bankasi"],
    "NatWest": ["^rbs", "royal bank of scotland"],
    "Mitsubishi UFJ Financial": ["=mitsubishi bank"],
}

OWN_NAME = "the bank's own name"
CONTAINS = "name contains the bank's name (branch, unit, subsidiary, foundation or partner: check)"
UNCONFIRMED = "possible related entity, no source yet (confirm or reject)"

# Words that may stand beside a bank's name without making it a different organisation.
_GENERIC = {
    "the", "bank", "banking", "group", "groep", "groupe", "holding", "holdings", "financial",
    "plc", "ag", "sa", "nv", "ltd", "limited", "inc", "co", "corp", "corporation", "as", "dac",
}


def match_kind(name: object, term: str) -> str:
    """Whether the name is just the bank (with legal form) or something larger that holds its name."""
    bank = next(b for b, ts in BANK_TERMS.items() if term in ts)
    rest = f" {words(name)} "
    for other in sorted((t.lstrip("^=") for t in BANK_TERMS[bank]), key=len, reverse=True):
        rest = rest.replace(f" {other} ", " ")  # every spelling of this bank, longest first
    rest = rest.split()
    return OWN_NAME if all(len(t) == 1 or t in _GENERIC for t in rest) else CONTAINS


def find_bank_kind(name: object) -> tuple[str, str, str]:
    """(bank, term, kind of match), trying the bank's own spellings first; else three empty strings."""
    bank, term = find_bank(name)
    if bank:
        return bank, term, match_kind(name, term)
    bank, term = find_bank(name, UNCONFIRMED_TERMS)
    return (bank, term, UNCONFIRMED) if bank else ("", "", "")


def words(value: object) -> str:
    """Lower-case words without accents or punctuation. For matching only."""
    if not isinstance(value, str):
        return ""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_fold(value).casefold()).split())


def org_key(value: object) -> str:
    """As `words`, with anything in brackets left out ("Example Fund (EF)" -> "example fund")."""
    return words(re.sub(r"\([^)]*\)", " ", value)) if isinstance(value, str) else ""


def person_tokens(value: object) -> frozenset[str]:
    """The words of a person's name without titles, in no order. For matching only."""
    if not isinstance(value, str):
        return frozenset()
    s = _HONORIFICS.sub("", ascii_fold(value).casefold().strip())
    return frozenset(t for t in re.split(r"[^a-z0-9]+", s) if t)


def same_person(a: frozenset[str], b: frozenset[str]) -> bool:
    """Same words, or one name holds all of the other's and they share at least two."""
    if not a or not b:
        return False
    return a == b or (len(a & b) >= 2 and (a <= b or b <= a))


def find_bank(name: object, terms: dict[str, list[str]] = BANK_TERMS) -> tuple[str, str]:
    """(bank, term) for the first bank whose term is in the name, longest term first; else ("", "")."""
    key = words(name)
    if not key:
        return "", ""
    best = ("", "")
    for bank, bank_terms in terms.items():
        for term in bank_terms:
            text = term.lstrip("^=")
            if term.startswith("="):
                hit = key == text
            elif term.startswith("^"):
                hit = key == text or key.startswith(text + " ")
            else:
                hit = f" {text} " in f" {key} "
            if hit and len(text) > len(best[1].lstrip("^=")):
                best = (bank, term)
    return best


def match_admitted(delegates: pd.DataFrame, admitted: pd.DataFrame) -> pd.DataFrame:
    """Columns that say which admitted NGO nominated each badge on the NGO sheet."""
    admitted = admitted.fillna("")
    by_full, by_short = defaultdict(list), defaultdict(list)
    for i, name in enumerate(admitted["official_name"]):
        by_full[words(name)].append(i)
        by_short[org_key(name)].append(i)
    contact = [person_tokens(p) for p in admitted["contact_person"]]
    by_contact = defaultdict(list)
    for i, tokens in enumerate(contact):
        if len(tokens) >= 2:
            by_contact[tokens].append(i)

    ngo = delegates[delegates["sheet"] == NGO_SHEET]
    names = {idx: person_tokens(n) for idx, n in ngo["Name"].items()}

    # 1. by the nominating organisation's name
    org_rows: dict[str, tuple[list[int], str]] = {}
    for nominator in ngo["Nominated by"].dropna().unique():
        if by_full.get(words(nominator)):
            org_rows[nominator] = (by_full[words(nominator)], "name")
        elif by_short.get(org_key(nominator)):
            org_rows[nominator] = (by_short[org_key(nominator)], "name ignoring brackets")
    # 2. where the name finds nothing: a delegate who is the contact person of exactly one admitted NGO
    for nominator, group in ngo[~ngo["Nominated by"].isin(org_rows)].groupby("Nominated by"):
        found = {i for idx in group.index for i in by_contact.get(names[idx], []) if len(by_contact[names[idx]]) == 1}
        if len(found) == 1:
            org_rows[nominator] = (list(found), "contact person")

    out = pd.DataFrame("", index=delegates.index, columns=[
        "admitted_match", "admitted_official_name", "admitted_constituency", "admitted_city",
        "admitted_country", "admitted_website", "admitted_rows_with_this_name", "is_contact_person",
    ])
    for idx, nominator in ngo["Nominated by"].items():
        if nominator not in org_rows:
            out.at[idx, "admitted_match"] = "none"
            continue
        rows, how = org_rows[nominator]
        is_contact = [i for i in rows if same_person(names[idx], contact[i])]
        row = admitted.iloc[(is_contact or rows)[0]]
        out.loc[idx] = [
            how, row["official_name"], row["constituency"], row["city"], row["country"],
            row["website"], str(len(rows)), "yes" if is_contact else "no",
        ]
    return out


def main() -> int:
    delegates = pd.read_csv(PARTICIPANTS, usecols=KEEP, dtype=str, low_memory=False)[KEEP]
    delegates.insert(0, "source_row", delegates.index + 2)  # line in the raw CSV, header is line 1
    admitted = pd.read_csv(ADMITTED, dtype=str)
    bank_names = sorted(set(pd.read_csv(BANKS, usecols=["bank"])["bank"]))
    if bank_names != sorted(BANK_TERMS) or not set(UNCONFIRMED_TERMS) <= set(BANK_TERMS):
        print("PROBLEM: the bank search terms do not cover exactly the banks in the league tables.")
        return 1

    merged = pd.concat([delegates, match_admitted(delegates, admitted)], axis=1)
    for column, prefix in (("Home organization", "bank_in_home_org"), ("Nominated by", "bank_in_nominator")):
        found = {v: find_bank_kind(v) for v in merged[column].dropna().unique()}
        for n, suffix in enumerate(("", "_term", "_kind")):
            merged[prefix + suffix] = merged[column].map(lambda v, n=n: found.get(v, ("", "", ""))[n])
    merged.to_csv(OUT, index=False, encoding="utf-8")

    parts = []
    for column, prefix in (("Home organization", "bank_in_home_org"), ("Nominated by", "bank_in_nominator")):
        hit = merged[merged[prefix] != ""]
        keys = [prefix, prefix + "_kind", prefix + "_term", column, "sheet"]
        part = hit.groupby(keys).size().reset_index(name="n_badges")
        part.columns = ["bank", "match_kind", "matched_term", "organisation_as_written", "sheet", "n_badges"]
        part.insert(3, "found_in", column)
        parts.append(part)
    banks = pd.concat(parts).sort_values(["bank", "match_kind", "found_in", "organisation_as_written", "sheet"])
    # the figures that make the link visible: financing of oil and gas expansion, 2021 to 2025
    league = pd.read_csv(BANKS).pivot(index="bank", columns="sector", values="usd_bn_total_2021_2025")
    league.columns = [f"usd_bn_2021_2025_{c}" for c in league.columns]
    banks = banks.merge(league.reset_index(), on="bank", how="left")
    banks["figures_source_id"] = "bankingonclimatechaos-sector-tables-2026"
    banks.to_csv(OUT_BANKS, index=False, encoding="utf-8")

    ngo = merged[merged["sheet"] == NGO_SHEET]
    orgs = ngo.drop_duplicates("Nominated by")
    any_bank = (merged["bank_in_home_org"] != "") | (merged["bank_in_nominator"] != "")
    stats = {
        "made": "2026-11-25, Claude Code, claude-fable-5-2 (code only; no model reads the data)",
        "badges_all_sheets": len(merged),
        "ngo_sheet_badges": len(ngo),
        "ngo_sheet_nominating_organisations": len(orgs),
        "nominating_organisations_by_match": orgs["admitted_match"].value_counts().to_dict(),
        "ngo_sheet_badges_by_match": ngo["admitted_match"].value_counts().to_dict(),
        "ngo_sheet_badges_by_constituency": ngo["admitted_constituency"].replace("", "no match").value_counts().to_dict(),
        "ngo_sheet_badges_held_by_the_contact_person": int((ngo["is_contact_person"] == "yes").sum()),
        "nominators_matching_a_name_used_by_two_admitted_rows": int((orgs["admitted_rows_with_this_name"] == "2").sum()),
        "badges_with_a_bank_name": int(any_bank.sum()),
        "badges_by_kind_of_bank_match_in_home_organisation": merged.loc[
            merged["bank_in_home_org"] != "", "bank_in_home_org_kind"].value_counts().to_dict(),
        "banks_found_by_kind_of_match": banks.groupby("match_kind")["bank"].nunique().to_dict(),
        "banks_found": int(banks["bank"].nunique()),
        "badges_with_a_bank_name_by_sheet": merged[any_bank]["sheet"].value_counts().to_dict(),
    }
    OUT_STATS.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
