import pandas as pd

from analysis import review_summary as rs


def _sheet(tmp_path, rows):
    p = tmp_path / "sheet.csv"
    pd.DataFrame(rows).to_csv(p, index=False, encoding="utf-8-sig")
    return {"feasibility test": p}


def _row(case, business, link, reason="", url=""):
    r = {"case": case, "canonical_name": "x", "countries": "A", "n_delegates": "1",
         "matched_entity": "x" if url else "", "evidence_status": "confident", "status": "uncertain"}
    for col, v in [("business", business), ("fossil_link", link), ("state_ownership", "unknown"), ("kind", "company")]:
        r[col] = v
        for s in rs.SUFFIXES:
            r[col + s] = ""
        r[col + "_unknown_reason"] = reason if v == "unknown" else ""
        r[col + "_source_url"] = url if v != "unknown" else ""
    return r


def test_summary_counts_unknowns_and_their_reasons(tmp_path):
    sheets = _sheet(tmp_path, [_row("F01", "yes", "unknown", "nothing found", "http://a"),
                               _row("F02", "unknown", "unknown", "nothing found"),
                               _row("F03", "no", "unknown", "sources conflict", "http://b"),
                               _row("F04", "yes", "none established", url="http://c")])
    s = rs.summary(sheets).set_index("measure")
    assert s.loc["fossil fuel link: unknown", "n"] == 3
    assert s.loc["fossil fuel link: unknown", "share"] == 0.75
    assert s.loc["fossil fuel link: unknown because nothing found", "n"] == 2
    assert s.loc["business: answered", "n"] == 3
    assert s.loc["business: answered with its own source", "n"] == 3
    assert s.loc["organisation identified", "n"] == 3


def test_against_standard_flags_a_share_over_the_limit(tmp_path):
    sheets = _sheet(tmp_path, [_row("F01", "yes", "unknown", "nothing found", "http://a")] * 4
                    + [_row("F05", "unknown", "none established", "nothing found")])
    t = rs.against_standard(sheets).set_index("measure")
    assert bool(t.loc["business: unknown", "within limit"]) is True
    assert bool(t.loc["fossil fuel link: unknown", "within limit"]) is False
