from cleaning.orgs import split_acting_for


def test_employer_and_principal():
    assert split_acting_for("UBA i.A. BMUKN") == ("UBA", "BMUKN")
    assert split_acting_for("UBA i.A BMUKN") == ("UBA", "BMUKN")
    assert split_acting_for("Jacobs Medien i.A. BMUKN") == ("Jacobs Medien", "BMUKN")


def test_bare_principal_leaves_employer_unresolved():
    assert split_acting_for("i.A. BMUKN") == (None, "BMUKN")


def test_no_marker_unchanged():
    for v in ["BMUKN", "Via Campesina", "Asia Society", "IASS", None, ""]:
        assert split_acting_for(v) == (v, None)
