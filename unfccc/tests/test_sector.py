from analysis import sector as S
from analysis import wave_progress as W


def test_group_of_code_reads_nace_naf_and_bare_digits():
    assert S.group_of_code("06.10Z") == "B05-06"
    assert S.group_of_code("7010") == "holding"
    assert S.group_of_code("64.20Z") == "holding"
    assert S.group_of_code("35.22") == "D35.2"
    assert S.group_of_code("49.50") == "H49.5"
    assert S.group_of_code("46") == "G"
    assert S.group_of_code("") == "unknown"


def _hit(siren, name, state="A"):
    return {"siren": siren, "nom_complet": name, "nom_raison_sociale": name,
            "etat_administratif": state}


def test_pick_by_siren_then_only_one_exact_active_name():
    res = [_hit("111111111", "ACME"), _hit("222222222", "ACME")]
    assert S.pick("ACME", "222222222", res)[0]["siren"] == "222222222"
    assert S.pick("ACME", "999999999", res)[0] is None
    hit, why = S.pick("Acme", "", res)
    assert hit is None and "several" in why            # two entities: never guess
    hit, _ = S.pick("Acme", "", [_hit("1", "ACME"), _hit("2", "ACME", state="C")])
    assert hit["siren"] == "1"                          # the closed one does not count
    assert S.pick("Acme", "", [{"siren": "3", "nom_complet": "ACME", "nom_raison_sociale": None,
                                "etat_administratif": "A"}])[0]["siren"] == "3"


def test_from_text_several_groups_is_unknown_not_a_pick():
    out = S.from_text([("refinery and oil pipeline operator", "u")])
    assert out["group"] == "unknown" and "several" in out["reason"]
    assert S.from_text([("a bakery", "u")]) is None


def test_sector_order_register_then_type_then_words():
    ev = {"activity": {"text": "operates a gas pipeline", "source_url": "u"}}
    reg = {"activite_principale": "19.20Z", "source_url": "r", "confidence": "high"}
    assert S.sector("financial_institution", ev, reg)["group"] == "C19"
    assert S.sector("financial_institution", ev, None)["basis"] == "business type (C4)"
    s = S.sector("company", ev, None)
    assert s["group"] == "H49.5" and s["confidence"] == "low"
    assert S.sector("company", {}, None)["reason"] == "no evidence record"
    coded = {"activity": {"text": "x", "code": {"system": "ATECO", "value": "35.21",
                                                 "source_url": "c"}}}
    s = S.sector("company", coded, None)            # a code the evidence step copied (wave 2 on)
    assert (s["group"], s["basis"], s["source_url"]) == ("D35.2", "register code", "c")


def test_columns_blank_when_not_business():
    assert set(S.columns(False, "company", {}, None).values()) == {""}
    assert S.columns(True, "law_firm", {}, None)["sector_group"] == "M69.1"


def _b(delegation, group, delegates, basis="", own="private"):
    return {"kind": "business_and_commercial", "delegation": delegation, "delegates": delegates,
            "sector_group": group, "sector_basis": basis, "state_ownership": own,
            "codebook": "0.16"}


def test_sector_cells_unknown_last_and_counts_kept_apart():
    data = [_b("FR", "unknown", 5), _b("FR", "K", 2, "business type (C4)"),
            _b("IT", "D35.1", 3, "word match", "majority_state"),
            {"kind": "public_sector", "delegation": "IT", "delegates": 50, "sector_group": "",
             "sector_basis": "", "state_ownership": "", "codebook": "0.16"}]
    groups, cols, cells = W.sector_cells(data)
    assert groups == ["D35.1", "K", "unknown"]          # fossil-relevant order, unknown last
    assert cols == ["FR", "IT"]                         # public sector does not count
    assert cells[("D35.1", "IT")] == {"delegates": 3, "orgs": 1, "soe": 1, "basis": {"W"}}
