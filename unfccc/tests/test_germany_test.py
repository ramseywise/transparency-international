"""Germany test (codebook 0.13 draft): lines, reporting group, headline order, review flag."""

from analysis import germany_test as g


def _entry(label=None, inferred=None, reason=None, confidence="high"):
    return {"label": label, "inferred": inferred, "unknown_reason": reason, "confidence": confidence}


def _row(**over):
    row = {"identity": "resolved", "delegates": 2, "party": 1, "overflow": 1}
    for a in g.ATTRIBUTES:
        row[a], row[f"{a}_line"] = "unknown", "unknown"
    row.update(over)
    row["headline"], row["headline_line"] = g.headline(row)
    return row


def test_line_of_keeps_strict_and_inferred_apart():
    assert g.line_of(_entry("public_sector")) == ("established", "public_sector")
    inf = {"basis": "proxy", "label": "none_established"}
    assert g.line_of(_entry("unknown", inf)) == ("proxy", "none_established")
    assert g.line_of(_entry("unknown", None, "description partial")) == ("unknown", "description partial")
    assert g.line_of(None) == ("unknown", "no record")


def test_reporting_group_r1():
    assert g.reporting_group("public_sector", "majority_state") == "public_sector"
    assert g.reporting_group("business_and_commercial", "majority_state") == \
        "state_owned_enterprise_or_non_profit"
    assert g.reporting_group("business_and_commercial", "no_state_majority") == "business"
    assert g.reporting_group("business_and_commercial", "unknown") == "unknown"
    assert g.reporting_group("unknown", "majority_state") == "unknown"


def test_headline_takes_first_tier_met():
    row = _row(tier_2A="met", tier_2A_line="established", tier_1="met", tier_1_line="proxy")
    assert (row["headline"], row["headline_line"]) == ("Tier 1", "proxy")
    row = _row(tier_2B_O="met", tier_2B_O_line="established")
    assert row["headline"] == "Tier 2B-O"


def test_headline_no_link_and_insufficient():
    row = _row(fossil_link_kind="none_established", fossil_link_kind_line="limited_evidence")
    assert (row["headline"], row["headline_line"]) == ("no identified link", "limited_evidence")
    assert _row()["headline"] == "insufficient evidence"


def test_review_inferred_only_is_batch_trigger():
    rec = {"attributes": {"identity_confidence": {"label": "high"}, "kind": _entry("public_sector")}}
    row = _row(kind="public_sector", kind_line="established",
               fossil_link_kind="none_established", fossil_link_kind_line="proxy")
    assert g.review_reasons(row, rec) == [g.INFERRED_ONLY]


def test_review_triggers():
    assert g.review_reasons(_row(identity="unresolved (generic text)"), None) == ["identity unresolved"]
    rec = {"attributes": {"identity_confidence": {"label": "medium"},
                          "kind": _entry("business_and_commercial", confidence="low"),
                          "fossil_link_kind": _entry("unknown", reason="not yet defined")}}
    row = _row(kind="business_and_commercial", kind_line="established", delegates=12)
    why = g.review_reasons(row, rec)
    assert "identity confidence medium" in why
    assert "ownership unclear" in why
    assert "kind at low confidence" in why
    assert "fossil rule not yet defined (F4)" in why
    assert "fossil link unresolved" not in why
    assert any("could move the headline" in x for x in why)


def test_tier3_not_yet_defined_alone_is_no_f4_trigger():
    rec = {"attributes": {"identity_confidence": {"label": "high"},
                          "tier_3": _entry("unknown", reason="not yet defined")}}
    why = g.review_reasons(_row(kind="public_sector"), rec)
    assert "fossil rule not yet defined (F4)" not in why
    assert "fossil link unresolved" in why


def test_headline_counts_each_delegate_once():
    orgs = [_row(delegates=5, party=3, overflow=2, fossil_link_kind="none_established",
                 fossil_link_kind_line="proxy"),
            _row(delegates=3, party=1, overflow=2)]
    hl = g.headline_counts(orgs)
    assert sum(r["delegates"] for r in hl) == 8
    assert [r["headline"] for r in hl] == ["no identified link", "insufficient evidence"]
    assert hl[0]["share_of_delegates"] == 62.5


def test_could_be_several_entities_is_identity_unresolved():
    case = {"case": "c1", "org_key": "K", "join_reason": "", "delegates": 2, "party": 0,
            "overflow": 2}
    rec = {"attributes": {"kind": _entry("unknown", reason="could be several entities")}}
    row = g.by_organisation([case], {"K": rec})[0]
    assert row["identity"] == "unresolved (could be several entities)"
    assert row["headline"] == "insufficient evidence"
    assert row["human_review"] == "individual"


def test_list_context_keeps_the_record_and_the_strict_labels_unknown():
    case = {"case": "c1", "org_key": "K", "join_reason": "", "delegates": 5, "party": 3,
            "overflow": 2}
    inferred = {"label": "public_sector", "basis": "proxy", "rule": "I4", "confidence": "low"}
    rec = {"attributes": {"kind": _entry("unknown", inferred, "could be several entities")}}
    row = g.by_organisation([case], {"K": rec})[0]
    assert row["identity"] == g.I4_IDENTITY
    assert (row["kind"], row["kind_line"]) == ("public_sector", "proxy")
    assert row["headline"] == "insufficient evidence"
    assert "identity by list context only (I4)" in row["review_reasons"]
    assert row["human_review"] == "individual"


def test_an_inferred_value_under_another_rule_does_not_resolve_the_identity():
    inferred = {"label": "public_sector", "basis": "proxy", "rule": "K2", "confidence": "low"}
    rec = {"attributes": {"kind": _entry("unknown", inferred, "could be several entities")}}
    assert not g.by_list_context(rec)
    assert g.has_record("resolved") and g.has_record(g.I4_IDENTITY)
    assert not g.has_record("unresolved (could be several entities)")


def test_curated_variants_point_at_kept_cases():
    targets = {t for t, _ in g.VARIANTS.values()}
    assert not targets & set(g.VARIANTS)
    assert not set(g.UNRESOLVED) & set(g.VARIANTS)
