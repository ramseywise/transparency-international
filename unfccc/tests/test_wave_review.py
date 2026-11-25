import json

from analysis import wave_review as wr


def _rec(kind, state):
    return {"attributes": {"kind": {"label": kind}, "state_ownership": {"label": state}}}


def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(wr, "ROOT", tmp_path)
    base = tmp_path / "data" / "processed" / "draft-codebook" / "wave9"
    for sub in ("classified", "run2"):
        (base / sub).mkdir(parents=True)
    kinds = ["public_sector"] * 15 + ["unknown"] * 5
    for i, k in enumerate(kinds):
        (base / "classified" / f"W9-{i:03}.json").write_text(json.dumps(_rec(k, "unknown")))
    verify = {f"W9-{i:03}": {"outcome": "failed" if i == 0 else "passed"} for i in range(20)}
    (base / "verify.json").write_text(json.dumps({"records": verify}))
    return base


def test_sample_is_repeatable_and_keeps_flagged_out_of_the_random_draw(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    a, b = wr.sample(9), wr.sample(9)
    assert a == b
    assert a["citation_flagged"] == ["W9-000"]
    assert "W9-000" not in a["citation_random"]
    assert len(a["citation_random"]) == 2  # ceil(10% of 15 answered)
    assert len(a["run2"]) == 2  # ceil(10% of 20 records)


def test_agreement_compares_label_by_label(tmp_path, monkeypatch):
    base = _setup(tmp_path, monkeypatch)
    (base / "run2" / "W9-001.json").write_text(json.dumps(_rec("public_sector", "unknown")))
    (base / "run2" / "W9-002.json").write_text(json.dumps(_rec("civil_society", "unknown")))
    rows = wr.agreement(9)
    same = {(r["case"], r["attribute"]): r["same"] for r in rows}
    assert same[("W9-001", "kind")] and not same[("W9-002", "kind")]
    assert same[("W9-002", "state_ownership")]
    assert (tmp_path / "outputs" / "draft-codebook" / "wave9" / "wave9_agreement_PROVISIONAL.csv").exists()
    assert wr.summary(rows)["kind"]["observed"] == 0.5
    wr.agreement_summary(9, rows)
    assert (tmp_path / "outputs" / "draft-codebook" / "wave9" / "wave9_agreement_summary_PROVISIONAL.csv").exists()


def test_citation_totals_count_items_and_records_separately(tmp_path, monkeypatch):
    base = _setup(tmp_path, monkeypatch)
    checked = [{"case": "W9-001", "record_verdict": "weak",
                "items": [{"verdict": "supported"}, {"verdict": "weak"}]},
               {"case": "W9-002", "record_verdict": "supported", "items": [{"verdict": "supported"}]}]
    (base / "citation_check.json").write_text(json.dumps({"checked": checked}))
    rows = {(r["basis"], r["verdict"]): (r["count"], r["of"]) for r in wr.citation_totals(9)}
    assert rows[("item", "supported")] == (2, 3)
    assert rows[("record", "weak")] == (1, 2)


def test_label_basis_names_the_source_type_of_the_cited_item(tmp_path, monkeypatch):
    base = _setup(tmp_path, monkeypatch)
    rec = {"attributes": {"kind": {"label": "public_sector", "confidence": "low",
                                   "source_url": "https://a.example/"}}}
    (base / "classified" / "W9-001.json").write_text(json.dumps(rec))
    (base / "evidence").mkdir()
    (base / "evidence" / "W9-001.json").write_text(json.dumps({"evidence": [
        {"source_url": "https://a.example/", "level": 5, "source_type": "register code"}]}))
    rows = {r["case"]: r for r in wr.label_basis(9)}
    assert (rows["W9-001"]["source_type"], rows["W9-001"]["level"]) == ("register code", 5)
    assert rows["W9-002"]["source_type"] == "none cited"
    assert (tmp_path / "outputs" / "draft-codebook" / "wave9" / "wave9_kind_basis_PROVISIONAL.csv").exists()
