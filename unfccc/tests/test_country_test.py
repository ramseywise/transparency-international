"""Country tests (codebook 0.13 draft): the Saudi draw, the case table, person lookups, counts."""
import pandas as pd
import pytest

from analysis import country_charts as ch
from analysis import country_insights as ci
from analysis import country_pick as cp
from analysis import country_test as c


def _raw(department, sheet="Parties", nominated="Saudi Arabia"):
    return {"Nominated by": nominated, "sheet": sheet, "Department": department}


def _entry(label, inferred=None, reason=None):
    return {"label": label, "inferred": inferred, "unknown_reason": reason, "confidence": "high"}


def _case(case, delegates, party, overflow, key, why="own spelling"):
    return {"case": case, "delegates": delegates, "party": party, "overflow": overflow,
            "country_context": "X", "org_key": key, "join_reason": why}


def test_saudi_draw_joins_spellings_and_splits_badges():
    rows = c.saudi_draw([_raw("MOEN"), _raw("Moens", "Party overflow"), _raw("ACWA", "Party overflow"),
                         _raw("ACWA", "Observers"), _raw("MOEN", nominated="Germany")])
    by = {r["case"]: r for r in rows}
    assert (by["S01"]["delegates"], by["S01"]["party"], by["S01"]["overflow"]) == (2, 1, 1)
    assert by["S01"]["raw"] == "MOEN | Moens"
    assert by["S03"]["delegates"] == 1


def test_saudi_draw_refuses_an_unmapped_spelling():
    with pytest.raises(ValueError):
        c.saudi_draw([_raw("A new body")])


def test_case_table_unresolved_and_no_organisation_row():
    country = c.Country("x", "X", "X", unresolved={"X02": "generic text"}, no_organisation=(2, 1))
    draw = [{"case": "X01", "raw": "Some Body", "delegates": 3, "party": 1, "overflow": 2,
             "country_context": "X"},
            {"case": "X02", "raw": "Media", "delegates": 1, "party": 0, "overflow": 1,
             "country_context": "X"}]
    by = {r["case"]: r for r in c.case_table(draw, country)}
    assert by["X01"]["org_key"] == "X01"
    assert (by["X02"]["org_key"], by["X02"]["join_reason"]) == (None, "generic text")
    assert (by["X00"]["delegates"], by["X00"]["join_reason"]) == (3, c.NO_ORGANISATION)


def test_apply_lookups_moves_found_delegates_only_and_keeps_the_total():
    cases = [_case("X01", 2, 1, 1, None, "generic text"), _case("X00", 1, 1, 0, None, c.NO_ORGANISATION)]
    lookups = [{"case": "P1", "org_case": "X01", "badge_type": "Party overflow", "status": "found"},
               {"case": "P2", "org_case": "X01", "badge_type": "Party", "status": "abstained"},
               {"case": "P3", "org_case": None, "badge_type": "Party", "status": "found"},
               {"case": "P4", "org_case": "X01", "badge_type": "Party", "status": "found"}]
    after = c.apply_lookups(cases, lookups, {"P1": "E1", "P3": "E3"}, "X")  # P4 has no employer key
    by = {r["case"]: r for r in after}
    assert "X00" not in by                                   # emptied rows are dropped
    assert (by["X01"]["delegates"], by["X01"]["overflow"]) == (1, 0)
    assert by["P1"]["org_key"] == "E1" and by["P1"]["join_reason"] == "person lookup (from X01)"
    assert sum(r["delegates"] for r in after) == 3
    assert cases[0]["delegates"] == 2                        # the first table is untouched


def test_apply_lookups_refuses_to_move_a_delegate_who_is_not_there():
    with pytest.raises(ValueError):
        c.apply_lookups([_case("X01", 1, 1, 0, None)],
                        [{"case": "P1", "org_case": "X01", "badge_type": "Party overflow",
                          "status": "found"}], {"P1": "E1"}, "X")


def test_employer_records_lay_0_14_over_0_13(tmp_path):
    import json
    for version, files in (("classified-0.13", {"XP1": "old", "XP2": "old"}),
                           ("classified-0.14", {"XP2": "new", "XP3": "new"})):
        (tmp_path / version).mkdir()
        for key, run in files.items():
            (tmp_path / version / f"{key}.json").write_text(json.dumps({"run": run}))
    got = c.employer_records(tmp_path)
    assert {k: v["run"] for k, v in got.items()} == {"XP1": "old", "XP2": "new", "XP3": "new"}
    assert c.employer_records(tmp_path / "missing") == {}


def test_kind_group():
    assert c.kind_group("public_sector", "established") == "public_sector"
    assert c.kind_group("business_and_commercial", "proxy") == "business_and_commercial"
    assert c.kind_group("intergovernmental", "established") == "other"
    assert c.kind_group("anything", "unknown") == "not_identified"


def test_summary_counts_each_delegate_once_per_measure():
    records = {"A": {"attributes": {"kind": _entry("business_and_commercial"),
                                    "business_type": _entry("company"),
                                    "tier_2A": _entry("met")}},
               "B": {"attributes": {"kind": _entry("public_sector"),
                                    "fossil_link_kind": _entry("none_established")}}}
    cases = [_case("A", 4, 1, 3, "A"), _case("B", 5, 5, 0, "B"), _case("C", 2, 0, 2, None, "generic text")]
    rows = c.summary("X", "v", c.organisations(cases, records))
    get = lambda m: {(r["value"], r["line"]): r for r in rows if r["measure"] == m}  # noqa: E731
    for m in ("kind", "headline_all"):
        assert sum(r["delegates"] for r in get(m).values()) == 11
    kind = get("kind")
    assert kind[("business_and_commercial", "")]["overflow"] == 3
    assert kind[("not_identified", "")]["delegates"] == 2
    assert get("headline_all")[("Tier 2A", "established")]["share"] == 36.4
    assert get("headline_business")[("Tier 2A", "established")]["share"] == 100.0
    assert get("business_type")[("company", "established")]["delegates"] == 4


def test_chart_bars_split_kind_and_fossil_by_badge_and_by_strength_of_evidence():
    assert ch.fossil_key("Tier 2A", "established") == "tier:established"
    assert ch.fossil_key("Tier 1", "proxy") == "tier:proxy"
    assert ch.fossil_key("no identified link", "limited_evidence") == "none:limited_evidence"
    assert ch.fossil_key("insufficient evidence", "unknown") == "unknown"
    with pytest.raises(ValueError):
        ch.fossil_key("Tier 1", "unknown")
    with pytest.raises(ValueError):
        ch.fossil_key("something else", "proxy")
    assert {k for k, *_ in ch.FOSSIL} == (
        {f"{a}:{s}" for a in ("tier", "none") for s in ch.STRENGTH} | {"unknown"})
    base = {"country": "X", "view": "organisation search", "line": "", "party": 1, "overflow": 2,
            "delegates": 3}
    rows = [{**base, "measure": "kind", "value": "public_sector"},
            {**base, "measure": "headline_all", "value": "Tier 1", "line": "established"},
            {**base, "measure": "headline_all", "value": "Tier 2A", "line": "established"},
            {**base, "measure": "headline_all", "value": "no identified link", "line": "proxy"},
            {**base, "measure": "headline_business", "value": "Tier 2A", "line": "limited_evidence"},
            {**base, "measure": "kind", "value": "public_sector", "view": "with person lookups"}]
    kind, fossil = ch.bars(rows)
    assert kind == [("X", "All delegates", {"public_sector": 3}),
                    ("X", "Party badges", {"public_sector": 1}),
                    ("X", "Overflow badges", {"public_sector": 2})]
    assert fossil == [("X", "All delegates", {"tier:established": 6, "none:proxy": 3}),
                      ("X", "Party badges", {"tier:established": 2, "none:proxy": 1}),
                      ("X", "Overflow badges", {"tier:established": 4, "none:proxy": 2}),
                      ("X", "Business: all", {"tier:limited_evidence": 3}),
                      ("X", "Business: Party", {"tier:limited_evidence": 1}),
                      ("X", "Business: overflow", {"tier:limited_evidence": 2})]
    assert ch.tiers_met(rows) == ("Tiers met: X Tier 1 (3 delegates, definitive evidence); "
                                  "X Tier 2A (3 delegates, definitive evidence).")
    assert ch.tiers_met(rows[:1]) == "No tier is met in these tests."


def test_list_alone_bar_goes_first_and_refuses_a_stated_type():
    kind = [("X", "All delegates", {"public_sector": 3}), ("X", "Party badges", {"public_sector": 1})]
    alone = [{"country": "X", "value": "stated", "delegates": 0},
             {"country": "X", "value": "not stated", "delegates": 3}]
    out = ch.with_list_alone(kind, alone)
    assert out[0] == ("X", ch.LIST_ALONE, {"not_identified": 3})
    assert [n for _, n, _ in out[1:]] == ["After web search: all", "Party badges"]
    alone[0]["delegates"] = 1
    with pytest.raises(ValueError):
        ch.with_list_alone(kind, alone)


def _org(key, headline, delegates, party, identity="resolved", kind="public_sector", reasons=""):
    return {"org_key": key, "headline": headline, "headline_line": "unknown", "identity": identity,
            "kind_group": kind, "review_reasons": reasons, "delegates": delegates, "party": party,
            "overflow": delegates - party}


def test_list_alone_counts_only_this_country_and_its_party_sheets():
    raw = [{"Nominated by": "X", "sheet": "Parties", ci.TYPE_COLUMN: ""},
           {"Nominated by": "X", "sheet": "Party overflow", ci.TYPE_COLUMN: "NGO"},
           {"Nominated by": "X", "sheet": "Observers", ci.TYPE_COLUMN: ""},
           {"Nominated by": "Y", "sheet": "Parties", ci.TYPE_COLUMN: ""}]
    by = {r["value"]: r for r in ci.list_alone(raw, "X")}
    assert (by["not stated"]["delegates"], by["not stated"]["party"]) == (1, 1)
    assert (by["stated"]["delegates"], by["stated"]["overflow"]) == (1, 1)


def test_cannot_say_sorts_each_reason_to_a_route_and_skips_the_placed():
    orgs = [_org("A", "insufficient evidence", 4, 1),
            _org("B", "insufficient evidence", 2, 0, reasons=ci.F4),
            _org("C", "insufficient evidence", 5, 5, identity="unresolved: acronym not confirmed"),
            _org("D", "insufficient evidence", 3, 0, identity="unresolved: generic text"),
            _org("E", "Tier 2A", 9, 0)]
    rows = ci.cannot_say(orgs, "X")
    assert sum(r["delegates"] for r in rows) == 14
    by = {r["reason"]: r for r in rows}
    assert by["Organisation found, fossil evidence incomplete"]["route"] == ci.SEARCH
    assert by["Finance rule (Tier 3) not defined"]["route"] == ci.DECISION
    assert by["Abbreviation not confirmed by a source"]["party"] == 5
    assert by["Entry is generic text"]["route"] == ci.PERSON
    assert [r["route"] for r in rows] == sorted((r["route"] for r in rows), key=ci.ROUTES.index)
    with pytest.raises(ValueError):
        ci.reason_of(_org("F", "insufficient evidence", 1, 0, identity="a new reason"))


def test_list_context_identity_has_its_own_reason_and_uses_the_record():
    from analysis import germany_test as g
    org = _org("S", "insufficient evidence", 7, 4, identity=g.I4_IDENTITY)
    assert ci.reason_of(org) == ("Body known from the list's context only", ci.PERSON)
    case = _case("S", 7, 4, 3, "S")
    inferred = {"label": "public_sector", "basis": "proxy", "rule": "I4", "confidence": "low"}
    rec = {"attributes": {"kind": _entry("unknown", inferred, "could be several entities")}}
    row = c.organisations([case], {"S": rec})[0]
    assert (row["kind_group"], row["business_type_line"]) == ("public_sector", "unknown")
    assert "S01" not in c.COUNTRIES["saudi-arabia"].unresolved


def test_two_similar_bodies_is_not_reported_as_no_evidence():
    """S02: the search found two similarly named bodies and chose neither (decision 2026-11-25)."""
    why = c.COUNTRIES["saudi-arabia"].unresolved["S02"]
    org = _org("S", "insufficient evidence", 20, 0, identity=f"unresolved: {why}")
    assert ci.reason_of(org) == ("Could be several bodies", ci.PERSON)


def test_activity_groups_business_only_and_never_guesses_a_group():
    orgs = [_org("A", "Tier 2A", 4, 0, kind="business_and_commercial"),
            _org("B", "insufficient evidence", 2, 1, kind="business_and_commercial"),
            _org("C", "insufficient evidence", 7, 7)]
    table = [{"org_key": "A", "country": "X", "provisional_group": "Power generation"},
             {"org_key": "B", "country": "Y", "provisional_group": "Other country"}]
    rows = ci.activity(orgs, table, "X")
    assert [(r["provisional_group"], r["delegates"], r["cases"]) for r in rows] == [
        ("Power generation", 4, "A"), (ci.NOT_GROUPED, 2, "B")]
    assert ch.activity_rows(rows)[0] == ("X", "Power generation", 4, "Tier 2A met")


def test_country_pick_legal_form_and_rule():
    assert cp.has_legal_form("Example Energy GmbH") and cp.has_legal_form("Example S.A.")
    assert not cp.has_legal_form("Ministry of Sagas") and not cp.has_legal_form(None)
    d = pd.DataFrame({
        "nominated_by_clean": ["Germany", "A", "A", "B", "B"],
        "Home organization": ["X GmbH", "Y Ltd", "Ministry", "Z AG", "W AG"],
        "badge_type": ["Party overflow", "Party overflow", "Party", "Party overflow", "Party overflow"],
        "org_id": ["g", "a1", "a2", "b1", "b2"]})
    t = cp.table(d)
    assert not t.loc["Germany", "candidate"]
    assert t.loc["B", "company_form_overflow"] == 2
    assert cp.pick(t) == "B"


def test_country_draw_folds_joined_spellings_and_skips_blank_organisations(monkeypatch):
    from analysis import country_draw as cd
    monkeypatch.setitem(cd.JOINS, "X", {"o1": ("o2", "same name with a typing error")})
    d = pd.DataFrame({
        "nominated_by_clean": ["X", "X", "X", "X", "Y"], "org_id": ["o1", "o2", "o3", None, "o9"],
        "org_canonical_name": ["Body", "Bodi", "Other", None, "Else"],
        "row_id": [1, 2, 3, 4, 5], "Home organization": ["Body", "Bodi", "Other", None, "Else"],
        "badge_type": ["Party", "Party overflow", "Party", "Party", "Party"]})
    g = cd.draw(d, "X", "X")
    assert list(g["case"]) == ["X01", "X02"] and int(g["delegates"].sum()) == 3
    top = g.iloc[0]
    assert (top["org_id"], top["org_canonical_name"], top["party"], top["overflow"]) == ("o1", "Body", 1, 1)


def test_tier3_run_reasons_have_their_own_groups_before_the_old_f4_reason():
    review = _org("G", "insufficient evidence", 2, 1, reasons=f"{ci.F4}")
    review["tier3_reason"] = "for review: on the bank table"
    assert ci.reason_of(review) == ("Bank on the table, for the researcher's review", ci.DECISION)
    off = _org("H", "insufficient evidence", 1, 0, reasons="not covered by the bank table")
    assert ci.reason_of(off) == ("Financial institution not covered by the bank table", ci.SEARCH)
