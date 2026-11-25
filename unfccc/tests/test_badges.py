"""Checks on the matching of badges to the admitted NGO table and the bank list (made-up data only)."""

import pandas as pd

from cleaning.badges import NGO_SHEET, find_bank, match_admitted, org_key, person_tokens, same_person, words


def test_words_and_org_key():
    assert words("Société  Générale, S.A.") == "societe generale s a"
    assert org_key("Example Fund (EF)") == "example fund"
    assert words(None) == "" and org_key(float("nan")) == ""


def test_same_person_ignores_titles_and_order_but_needs_two_shared_words():
    assert same_person(person_tokens("Ms. Ada Example"), person_tokens("EXAMPLE Ada"))
    assert same_person(person_tokens("Ada Maria Example"), person_tokens("Ada Example"))
    assert not same_person(person_tokens("Ada Example"), person_tokens("Ada Sample"))
    assert not same_person(person_tokens("Ada"), person_tokens("Ada Example"))
    assert not same_person(person_tokens(""), person_tokens(""))


def test_find_bank_matches_whole_words_and_respects_anchors():
    assert find_bank("HSBC Bank plc")[0] == "HSBC"
    assert find_bank("Clubs United")[0] == ""                       # "ubs" inside a word
    assert find_bank("Training Institute")[0] == ""                 # "ing" inside a word
    assert find_bank("Ing")[0] == "ING Group"
    assert find_bank("Development Bank of China Region")[0] == ""   # "bank of china" must start the name
    assert find_bank("Agricultural Bank of China")[0] == "Agricultural Bank of China"
    assert find_bank("Citizens Trust")[0] == ""
    assert find_bank(None) == ("", "")


def test_kind_of_bank_match_separates_the_bank_from_names_that_only_hold_its_name():
    from cleaning.badges import CONTAINS, OWN_NAME, UNCONFIRMED, find_bank_kind

    assert find_bank_kind("HSBC Bank plc")[2] == OWN_NAME
    assert find_bank_kind("HSBC Bank A.Ş.")[2] == OWN_NAME
    assert find_bank_kind("JP Morgan Chase")[2] == OWN_NAME
    assert find_bank_kind("Mitsubishi UFJ Financial Group (MUFG)")[2] == OWN_NAME
    assert find_bank_kind("Fondation BNP Paribas")[2] == CONTAINS
    assert find_bank_kind("HSBC Vietnam")[2] == CONTAINS
    assert find_bank_kind("BNPP Asset Management")[:1] == ("BNP Paribas",)
    assert find_bank_kind("Natixis Corporate and Investment Bank")[::2] == ("Groupe BPCE", UNCONFIRMED)
    assert find_bank_kind("Mitsubishi Corporation") == ("", "", "")


def test_match_admitted_by_name_brackets_and_contact_person():
    admitted = pd.DataFrame({
        "official_name": ["Alpha Institute", "Beta Forum (BF)", "Gamma Network"],
        "website": ["a.example", "", "g.example"],
        "contact_person": ["Ms. Ada Example", "Bo Sample", "Cy Person"],
        "city": ["Oslo", "Bergen", "Lima"],
        "country": ["Norway", "Norway", "Peru"],
        "constituency": ["Youth", "Environmental", "Farmers"],
    })
    delegates = pd.DataFrame({
        "sheet": [NGO_SHEET, NGO_SHEET, NGO_SHEET, NGO_SHEET, NGO_SHEET, "Parties"],
        "Nominated by": ["Alpha Institute", "Alpha Institute", "Beta Forum", "Gamma Net", "Delta Club", "Norway"],
        "Name": ["Example Ada", "Dan Other", "Eve Other", "Mr. Cy Person", "Fay Other", "Gil Other"],
    })
    out = match_admitted(delegates, admitted)
    assert list(out["admitted_match"]) == ["name", "name", "name ignoring brackets", "contact person", "none", ""]
    assert list(out["is_contact_person"]) == ["yes", "no", "no", "yes", "", ""]
    assert out.loc[2, "admitted_constituency"] == "Environmental"
    assert out.loc[3, "admitted_official_name"] == "Gamma Network"
    assert out.loc[5, "admitted_official_name"] == ""
