"""Synthetic-string tests for cleaning.orgs. No real data."""

import pandas as pd

from cleaning.orgs import (
    NO_ORG_REASONS,
    is_country_scoped,
    make_org_id,
    no_org_reason,
    normalise_org_name,
    pass1_assign,
    propose_merges,
    resolve_auto_merges,
)


def test_normalise_ignores_case_punctuation_diacritics_legal_form():
    a = normalise_org_name("Acme Energie GmbH")
    assert a == normalise_org_name("ACME energie, G.m.b.H.") or a == normalise_org_name("acme energie")
    assert normalise_org_name("Café Corp Ltd") == normalise_org_name("cafe corp")
    assert normalise_org_name("Nordic Power A/S") == normalise_org_name("Nordic Power")


def test_different_names_stay_different():
    assert normalise_org_name("Alpha Institute") != normalise_org_name("Beta Institute")


def test_no_org_reasons():
    c = {"utopia"}
    assert no_org_reason(None, None, c) == "blank"
    assert no_org_reason(None, "-", c) == "placeholder"
    assert no_org_reason("Independent", "Independent", c) == "generic"
    assert no_org_reason("Utopia", "Utopia", c) == "country_name"
    assert no_org_reason("Director of Things", "Director of Things", c) == "person_or_title"
    assert no_org_reason("Acme Works", "Acme Works", c) is None
    assert no_org_reason("Professor X High School", "Professor X High School", c) is None
    assert float("nan") != float("nan") and no_org_reason(float("nan"), float("nan"), c) == "blank"
    assert all(r in NO_ORG_REASONS for r in ["blank", "placeholder", "generic", "country_name", "person_or_title"])


def test_scoping_government_names_and_acronyms():
    assert is_country_scoped(normalise_org_name("Ministry of Finance"))
    assert is_country_scoped("bmf")
    assert not is_country_scoped(normalise_org_name("European Parliament"))


def test_pass1_scopes_ministries_by_country():
    keys = pd.Series([normalise_org_name("Ministry of Finance")] * 2 + [normalise_org_name("Acme Works")] * 2)
    nom = pd.Series(["Utopia", "Elsewhere", "Utopia", "Elsewhere"])
    out = pass1_assign(keys, nom)
    assert out["org_id"].iloc[0] != out["org_id"].iloc[1]
    assert out["org_id"].iloc[2] == out["org_id"].iloc[3]


def test_make_org_id_stable():
    assert make_org_id("acme", "*") == make_org_id("acme", "*")
    assert make_org_id("acme", "*") != make_org_id("acme", "Utopia")


def _orgs(names):
    rows = []
    for n in names:
        k = normalise_org_name(n)
        rows.append({"org_id": make_org_id(k, "Utopia"), "org_key": k, "canonical_name": n,
                     "countries": ["Utopia"], "n_delegates": 1})
    return pd.DataFrame(rows)


def test_pass2_auto_merges_typo_only():
    o = _orgs(["Ministry of Agriculture and Fisheries", "Ministry of Agricultre and Fisheries"])
    pairs = propose_merges(o, 88.0, 96.0)
    assert len(pairs) == 1 and pairs["decision"].iloc[0] == "auto"
    assert len(resolve_auto_merges(pairs, dict(zip(o["org_id"], o["n_delegates"])))) == 1


def test_pass2_never_auto_merges_different_places():
    o = _orgs(["Polytechnic University of Alpha", "Polytechnic University of Omega"])
    pairs = propose_merges(o, 80.0, 96.0)
    assert (pairs["decision"] != "auto").all()
