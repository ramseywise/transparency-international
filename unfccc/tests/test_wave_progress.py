from analysis import wave_progress as W


def _attrs(kind="public_sector", tiers=None, link="unknown", inferred=None):
    a = {t: {"label": "unknown", "unknown_reason": "x"} for t in W.TIERS}
    for t, lab in (tiers or {}).items():
        a[t]["label"] = lab
    a["fossil_link_kind"] = {"label": link, "unknown_reason": None}
    for t, (lab, basis) in (inferred or {}).items():
        a[t]["inferred"] = {"label": lab, "basis": basis}
    a["kind"] = {"label": kind}
    return a


def _row(delegation, kind, fossil, party, overflow):
    return {"delegation": delegation, "kind": kind, "fossil": fossil, "party": party,
            "overflow": overflow, "delegates": party + overflow}


def test_fossil_key_strict_beats_inferred():
    a = _attrs(tiers={"tier_2A": "met"}, inferred={"tier_1": ("not_met", "proxy")})
    assert W.fossil_key(a) == "tier:established"


def test_fossil_key_inferred_met_before_not_met():
    a = _attrs(inferred={"tier_1": ("not_met", "proxy"), "tier_3": ("met", "limited_evidence")})
    assert W.fossil_key(a) == "tier:limited_evidence"


def test_fossil_key_nothing_is_unknown_not_no_link():
    assert W.fossil_key(_attrs()) == "unknown"


def test_kind_key_media_and_unknown():
    assert W.kind_key(_attrs(kind="media")) == "other"
    assert W.kind_key(_attrs(kind="unknown")) == "not_identified"


def test_tiers_said_lists_only_answered_tiers():
    a = _attrs(tiers={"tier_3": "not_met"}, inferred={"tier_1": ("not_met", "proxy")})
    assert W.tiers_said(a) == "tier_3=not_met"
    assert W.tiers_said(a, inferred=True) == "tier_1=not_met (proxy)"


def test_badges_kept_apart_per_delegation():
    data = [_row("A", "business_and_commercial", "unknown", 1, 2),
            _row("A", "business_and_commercial", "unknown", 0, 3)]
    per = W.by_delegation(data, "kind")
    assert per["A"] == {("business_and_commercial", "party"): 1,
                        ("business_and_commercial", "overflow"): 5}


def test_kind_order_by_public_share_descending():
    data = [_row("Low", "public_sector", "unknown", 1, 0), _row("Low", "not_identified", "unknown", 3, 0),
            _row("High", "public_sector", "unknown", 9, 0), _row("High", "business_and_commercial", "unknown", 0, 1)]
    assert W.kind_order(W.by_delegation(data, "kind")) == ["High", "Low"]


def test_fossil_order_definitive_then_some_evidence():
    data = [_row("Some", "public_sector", "none:limited_evidence", 10, 0),
            _row("Def", "public_sector", "none:established", 1, 0),
            _row("Def", "public_sector", "unknown", 9, 0)]
    assert W.fossil_order(W.by_delegation(data, "fossil")) == ["Def", "Some"]


def test_wave_share_weights_by_delegates():
    data = [_row("A", "public_sector", "unknown", 3, 0), _row("B", "not_identified", "unknown", 1, 0)]
    assert W.wave_share(data, "kind", {"public_sector"}) == 75.0


# --- tier 3 overlay, runs, business text, all runs (2026-11-25) ---

from analysis import all_progress as A


def test_with_tier3_to_confirm_stays_unknown():
    a = W.with_tier3(_attrs(), {"label": "met", "to_confirm": True})
    assert a["tier_3"]["label"] == "unknown"
    assert a["tier_3"]["unknown_reason"] == "met by code, to confirm"


def test_with_tier3_replaces_placeholder_and_leaves_input():
    base = _attrs()
    a = W.with_tier3(base, {"label": "not_applicable"})
    assert a["tier_3"]["label"] == "not_applicable"
    assert base["tier_3"]["label"] == "unknown"
    assert W.with_tier3(base, None) is base


def test_version_groups_keep_order_and_tags_only_when_mixed():
    data = [{"codebook": "0.16", "delegation": "FR"}, {"codebook": "0.13", "delegation": "DE"},
            {"codebook": "0.16", "delegation": "FR"}]
    groups = W.version_groups(data)
    assert [g for g, _ in groups] == ["0.16", "0.13"]
    assert [len(rs) for _, rs in groups] == [2, 1]
    tags = W.delegation_versions(data)
    assert tags == {"DE": " · 0.13"}                    # only the earlier version is marked
    assert W.delegation_versions(data[:1] + data[2:]) == {}


def test_business_text_prefers_sector_as_found():
    r = {"business_type": "company", "utility": "no", "state_ownership": "private",
         "activity_as_found": "manufacture of steel"}
    assert W.business_text(r) == "manufacture of steel; utility: no"
    r["activity_as_found"] = ""
    assert W.business_text(r).startswith("company;")


def test_short_name_cuts_description():
    assert W.short_name("ACME GmbH (an energy agency, Berlin)") == "ACME GmbH"
    assert len(W.short_name("x" * 40)) == 28


def test_fossil_note_counts_per_version():
    data = [{"codebook": "0.16", "fossil": f, "tier3_set_by_code": t, "delegates": 1,
             "party": 1, "overflow": 0}
            for f, t in (("tier:established", ""), ("none:established", "not_applicable x"),
                         ("none:proxy", "unknown y"), ("not_run", ""))]
    note = W.fossil_note(data)
    assert note.startswith('Codebook 0.16: 1 of 3 fit a tier; "no link found" 1 strict, '
                           "1 inferred; tier 3 by code: 1 not applicable, 1 unknown.")


def _test_csv_row(**over):
    row = {"org_key": "k", "name": "N", "delegates": "2", "party": "1", "overflow": "1",
           "kind_group": "business", "headline": "insufficient evidence", "headline_line": "",
           "fossil_link_kind": "unknown", "tier_3": "not assessed", "business_type": "company",
           "state_ownership": "private", "utility": "no utility found"}
    for t in W.TIERS:
        row[t], row[f"{t}_line"] = "unknown", ""
    return row | over


def test_country_test_mapping():
    assert A.fossil_from_test(_test_csv_row(headline="Tier 2A", headline_line="established")) \
        == "tier:established"
    assert A.fossil_from_test(_test_csv_row(headline="no identified link",
                                            headline_line="proxy")) == "none:proxy"
    assert A.fossil_from_test(_test_csv_row()) == "unknown"
    r = A.test_row("Germany", _test_csv_row(tier_1="not_met", tier_1_line="proxy"), "run")
    assert r["utility"] == "unknown"          # an unknown reason is never shown as a label
    assert r["tiers_strict"] == "" and r["tiers_inferred"] == "tier_1=not_met (proxy)"
    assert r["codebook"] == A.TEST_VERSION and r["run"] == "run"


def _srow(delegation, kind, party, overflow, fossil="unknown", own=""):
    return {"codebook": "0.16", "delegation": delegation, "kind": kind, "party": party,
            "overflow": overflow, "delegates": party + overflow, "fossil": fossil,
            "state_ownership": own}


def test_summary_weighted_and_unweighted_differ():
    data = [_srow("Big", "public_sector", 9, 0), _srow("Big", "not_identified", 1, 0),
            _srow("Small", "business_and_commercial", 0, 1, "tier:established", "majority_state")]
    out = {(r["delegation"], r["badge"]): r for r in A.summary(data)}
    pooled = out[("all delegates (weighted)", "delegates")]
    mean = out[("mean of delegations (unweighted)", "delegates")]
    assert pooled["public_sector_pct"] == 81.8          # 9 of 11 delegates
    assert mean["public_sector_pct"] == 45.0            # (90 + 0) / 2
    assert pooled["business_state_majority"] == 1 and pooled["fossil_tier_orgs"] == 1
    assert out[("Small", "party")]["public_sector_pct"] == ""   # no party delegates: blank, not 0


def test_summary_pools_kind_only_across_versions():
    data = [_srow("Big", "public_sector", 9, 0),
            _srow("Old", "business_and_commercial", 1, 0, "tier:established") | {"codebook": "0.13"}]
    out = [r for r in A.summary(data) if r["codebook"] == "all versions (kind only)"
           and r["delegation"] == "all delegates (weighted)" and r["badge"] == "delegates"]
    assert out[0]["public_sector_pct"] == 90.0
    assert out[0]["fossil_tier_orgs"] == "" and out[0]["fossil_unknown_pct"] == ""
