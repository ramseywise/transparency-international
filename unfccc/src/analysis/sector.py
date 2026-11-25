"""Sector of each business organisation, set by code from what is stored, never by a model.
PROVISIONAL.

The codebook (3.3) leaves the sector label "unknown" until the lead researcher chooses the list of
sectors. What this module gives is a record beside it: a NACE group with the basis it rests on, for
the charts and for her to choose from. The grouping in GROUPS (NACE Rev. 2 sections, with the
fossil-relevant divisions split out) is a proposal, open in decisions.md.

Order of evidence, the first that answers decides:
1. `register code`: an official activity code (NACE, or a national version of it that is the same
   to four digits: NAF rév. 2, WZ 2008, ATECO 2007) for the very entity the evidence step
   identified, from a register record saved under <run>/register/ or recorded by evidence-finder in
   `activity.code`. Head office and holding codes (64.20, 70.10) say nothing about what the group
   does and give "holding or head office".
2. `business type (C4)`: the classifier's business type where it has an exact NACE equivalent
   (financial institution: K 64-66; consultancy: M 70.2; law firm: M 69.1; trade or industry
   association: S 94.1). The association's members' industry is not recorded.
3. `word match`: a fossil-relevant activity word in the stored activity text or quotes. Low
   confidence, and to be checked by a person: a quote may name coal or gas without the body doing
   either. Words place only the fossil-relevant groups, never another sector.
4. otherwise "sector unknown", with the reason.

The division-to-section table is NACE Rev. 2 (Eurostat, 2008), which is not yet in the study
library (codebook section 9): check it against the publication before the grouping is approved.

Register lookup (France only, wave 2 on): `recherche-entreprises.api.gouv.fr`, free, no key. By
SIREN where the evidence records one; otherwise by the organisation's name, accepted only when
exactly one active entry has that exact name. Only the name or SIREN is sent. Officers' names in
the reply are dropped and never stored (workspace rule 8).
Run from unfccc/: PYTHONPATH=src uv run python -I -m analysis.sector lookup-fr <wave>
"""
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "data" / "processed" / "draft-codebook"

# (key, label): fossil-relevant first, then the other NACE sections, then what code cannot place.
GROUPS = (
    ("B05-06", "B 05-06 Coal, oil and gas extraction"),
    ("B09", "B 09 Mining support services"),
    ("C19", "C 19 Coke and refined petroleum"),
    ("D35.1", "D 35.1 Electricity"),
    ("D35.2", "D 35.2 Gas supply"),
    ("D35.3", "D 35.3 Heat and cooling"),
    ("H49.5", "H 49.5 Pipelines"),
    ("K", "K Finance and insurance"),
    ("A", "A Agriculture, forestry, fishing"),
    ("B07-08", "B 07-08 Other mining"),
    ("C", "C Other manufacturing"),
    ("E", "E Water, waste"),
    ("F", "F Construction"),
    ("G", "G Trade"),
    ("H", "H Other transport"),
    ("I", "I Accommodation, food"),
    ("J", "J Information, communication"),
    ("L", "L Real estate"),
    ("M69.1", "M 69.1 Law firms"),
    ("M70.2", "M 70.2 Consultancy"),
    ("M", "M Other professional, scientific"),
    ("N", "N Administrative services"),
    ("O", "O Public administration"),
    ("P", "P Education"),
    ("Q", "Q Health, social work"),
    ("R", "R Arts, recreation"),
    ("S94.1", "S 94.1 Business associations"),
    ("S", "S Other services"),
    ("holding", "Holding or head office (code says nothing of activity)"),
    ("unknown", "Sector unknown"),
)
LABEL = dict(GROUPS)
FOSSIL_RELEVANT = ("B05-06", "B09", "C19", "D35.1", "D35.2", "D35.3", "H49.5", "K")

# NACE Rev. 2 divisions to sections (to be checked against the publication, see above).
SECTION_OF = [((1, 3), "A"), ((5, 9), "B"), ((10, 33), "C"), ((35, 35), "D"), ((36, 39), "E"),
              ((41, 43), "F"), ((45, 47), "G"), ((49, 53), "H"), ((55, 56), "I"), ((58, 63), "J"),
              ((64, 66), "K"), ((68, 68), "L"), ((69, 75), "M"), ((77, 82), "N"), ((84, 84), "O"),
              ((85, 85), "P"), ((86, 88), "Q"), ((90, 93), "R"), ((94, 96), "S"), ((97, 98), "T"),
              ((99, 99), "U")]


def group_of_code(code: str) -> str:
    """NACE group of an activity code ("06.10Z", "0610", "35.11", "49.50"). "unknown" if the code
    cannot be read."""
    digits = re.sub(r"\D", "", code or "")
    if len(digits) < 2:
        return "unknown"
    div, four = int(digits[:2]), digits[:4]
    if four in ("6420", "7010"):
        return "holding"
    if div in (5, 6):
        return "B05-06"
    if div in (7, 8):
        return "B07-08"
    if div == 9:
        return "B09"
    if div == 19:
        return "C19"
    if div == 35:
        return {"1": "D35.1", "2": "D35.2", "3": "D35.3"}.get(digits[2:3], "unknown")
    if digits[:3] == "495":
        return "H49.5"
    if digits[:3] == "691":
        return "M69.1"
    if digits[:3] == "702":
        return "M70.2"
    if digits[:3] == "941":
        return "S94.1"
    for (lo, hi), sec in SECTION_OF:
        if lo <= div <= hi:
            return sec if sec in LABEL else "unknown"
    return "unknown"


BY_TYPE = {"financial_institution": "K", "consultancy": "M70.2", "law_firm": "M69.1",
           "trade_or_industry_association": "S94.1"}

# Fossil-relevant activity words, in the languages of the lists. Kept narrow on purpose:
# "pipeline" alone, "energy" or "utility" would match too much.
WORDS = (
    ("B05-06", r"oil and gas (exploration|production|extraction)|upstream oil|crude oil production"
               r"|natural gas production|coal min(e|es|ing)\b|lignite min|braunkohle"
               r"|erdöl- und erdgasförderung|extraction de (pétrole|gaz|charbon)"
               r"|estrazione di (petrolio|gas|carbone)|extracción de (petróleo|gas|carbón)"),
    ("B09", r"oilfield services|drilling services|support activities for petroleum"),
    ("C19", r"\brefiner(y|ies)\b|oil refining|raffinerie|raffineria|refinería"),
    ("D35.1", r"electricity (generation|production|supply|distribution|transmission)"
              r"|power (generation|plants?|stations?)|transmission system operator"
              r"|stromerzeugung|stromversorgung|production d'électricité"
              r"|produzione di energia elettrica|generación eléctrica"),
    ("D35.2", r"gas (supply|distribution|transmission|grid|network|storage)\b|lng terminal"
              r"|gasversorgung|gasnetz|distribution de gaz|distribuzione (del )?gas"),
    ("D35.3", r"district heating|fernwärme|chauffage urbain|teleriscaldamento"),
    ("H49.5", r"(oil|gas) pipelines?\b|pipeline operator|oléoduc|gazoduc|gasdotto|oleodotto"
              r"|gasoducto|oleoducto"),
)


def from_text(texts: list[tuple[str, str]]) -> dict | None:
    """The fossil-relevant group named by the stored text, as (text, source_url) pairs. None where
    no word matches; "unknown" where words point to more than one group."""
    hits: dict = {}
    for text, url in texts:
        low = (text or "").lower()
        for key, pattern in WORDS:
            m = re.search(pattern, low)
            if m and key not in hits:
                hits[key] = {"word": m.group(0), "quote": text, "source_url": url}
    if not hits:
        return None
    if len(hits) > 1:
        return {"group": "unknown", "basis": "word match",
                "reason": "words for several groups: " + ", ".join(sorted(hits)),
                "confidence": "low", "word": "; ".join(h["word"] for h in hits.values()),
                "source_url": "", "quote": ""}
    key, h = next(iter(hits.items()))
    return {"group": key, "basis": "word match", "reason": "", "confidence": "low"} | h


def _texts(ev: dict) -> list[tuple[str, str]]:
    out = []
    act = ev.get("activity") or {}
    if act.get("text"):
        out.append((act["text"], act.get("source_url") or ""))
    out += [(e.get("quote") or "", e.get("source_url") or "") for e in ev.get("evidence") or []]
    return out


def sector(business_type: str, ev: dict, register: dict | None) -> dict:
    """The sector record of one business organisation from its stored evidence and register
    record, by the order in the module text."""
    code = (register or {}).get("activite_principale") or ((ev.get("activity") or {}).get("code")
                                                            or {}).get("value")
    if code:
        src = register or (ev.get("activity") or {}).get("code") or {}
        g = group_of_code(code)
        if g != "unknown":
            return {"group": g, "basis": "register code", "code": code,
                    "confidence": src.get("confidence", "high"), "reason": "",
                    "source_url": src.get("source_url", ""), "quote": "", "word": ""}
    if business_type in BY_TYPE:
        return {"group": BY_TYPE[business_type], "basis": "business type (C4)", "code": "",
                "confidence": "as the business type", "reason": "", "source_url": "",
                "quote": "", "word": ""}
    found = from_text(_texts(ev))
    if found:
        return {"code": ""} | found
    reason = ("no activity code, business type or fossil-relevant word in the stored evidence"
              if ev else "no evidence record")
    return {"group": "unknown", "basis": "", "code": "", "confidence": "", "reason": reason,
            "source_url": "", "quote": "", "word": ""}


COLUMNS = ("sector_group", "sector_basis", "sector_code", "sector_confidence", "sector_word",
           "sector_source", "sector_reason")


def columns(is_business: bool, business_type: str, ev: dict, register: dict | None,
            extra_text: str = "") -> dict:
    """The sector columns of one row of the progress table: blank for an organisation that is
    not business. `extra_text` is stored text that is not in the evidence record (the country
    tests keep the evidence step's description of the body after its name)."""
    if not is_business:
        return dict.fromkeys(COLUMNS, "")
    ev = dict(ev)
    if extra_text:
        ev["evidence"] = list(ev.get("evidence") or []) + [{"quote": extra_text, "source_url": ""}]
    s = sector(business_type, ev, register)
    return {"sector_group": s["group"], "sector_basis": s["basis"], "sector_code": s["code"],
            "sector_confidence": s["confidence"], "sector_word": s.get("word", ""),
            "sector_source": s.get("source_url", ""), "sector_reason": s["reason"]}


# ---- the French register --------------------------------------------------------------------

API = "https://recherche-entreprises.api.gouv.fr/search"
KEEP = ("siren", "nom_complet", "nom_raison_sociale", "activite_principale", "nature_juridique",
        "etat_administratif", "date_creation", "date_fermeture")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


def _get(query: str) -> list[dict]:
    url = f"{API}?{urllib.parse.urlencode({'q': query, 'per_page': 10})}"
    req = urllib.request.Request(url, headers={"User-Agent": "research-client"})
    with urllib.request.urlopen(req, timeout=20) as fh:
        return [{k: r.get(k) for k in KEEP} for r in json.load(fh).get("results", [])]


def pick(name: str, siren: str, results: list[dict]) -> tuple[dict | None, str]:
    """The register entry for this organisation, and why. By SIREN where known; by name only
    where exactly one active entry has exactly that name."""
    if siren:
        hit = [r for r in results if r.get("siren") == siren]
        return (hit[0], "matched by SIREN") if hit else (None, "SIREN not found in register")
    exact = [r for r in results if r.get("etat_administratif") == "A"
             and _norm(name) in (_norm(r.get("nom_raison_sociale")), _norm(r.get("nom_complet")))]
    if len(exact) == 1:
        return exact[0], "matched by exact name, one active entry"
    return None, ("no active entry with this exact name" if not exact
                  else f"could be several entities: {len(exact)} active entries with this name")


SIREN = re.compile(r"\b(\d{3}\s?\d{3}\s?\d{3})\b")


def siren_in(ev: dict) -> str:
    code = ((ev.get("activity") or {}).get("register_id") or "")
    m = SIREN.search(code)
    return m.group(1).replace(" ", "") if m else ""


def lookup_fr(wave: int) -> None:
    """Look up every business organisation of the wave in the French register, and save what
    was found (or why not) in wave<n>/register/<case>.json."""
    folder = BASE / f"wave{wave}"
    out = folder / "register"
    out.mkdir(exist_ok=True)
    for path in sorted((folder / "classified").glob("*.json")):
        rec = json.loads(path.read_text())
        if rec["attributes"]["kind"]["label"] != "business_and_commercial":
            continue
        case = path.stem
        ev_path = folder / "evidence" / f"{case}.json"
        ev = json.loads(ev_path.read_text()) if ev_path.exists() else {}
        name = ev.get("matched_entity") or rec["name"]
        if isinstance(name, dict):
            name = name.get("name") or ""
        siren = siren_in(ev)
        results = _get(siren or name)
        hit, why = pick(name, siren, results)
        rec_out = {"case": case, "register": "recherche-entreprises (INSEE SIRENE / RNE)",
                   "query": siren or name, "accessed": date.today().isoformat(), "match": why,
                   "candidates": len(results)}
        if hit:
            rec_out |= hit | {"source_url": f"https://annuaire-entreprises.data.gouv.fr/entreprise/"
                                            f"{hit['siren']}",
                              "confidence": "high" if siren else "medium"}
        (out / f"{case}.json").write_text(json.dumps(rec_out, ensure_ascii=False, indent=1))
        print(case, why)


def register_record(folder: Path, case: str) -> dict | None:
    p = folder / "register" / f"{case}.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    return r if r.get("activite_principale") else None


if __name__ == "__main__":
    if sys.argv[1:2] == ["lookup-fr"]:
        lookup_fr(int(sys.argv[2]))
    else:
        sys.exit(__doc__)
