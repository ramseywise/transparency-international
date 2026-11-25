"""Raw files sorted into topic folders, and the catalogue, both following the ledger."""

import json

from rag import paths
from rag import cli as lit
from rag import views
from rag.ledger import Ledger


def _library(tmp_path):
    root = tmp_path / "literature" / "demo"
    for sub in (paths.PDFS, paths.PAGES, paths.RECORDS):
        (root / sub).mkdir(parents=True)
    (root / paths.PDFS / "a.pdf").write_text("raw a")
    (root / paths.PDFS / "b.pdf").write_text("raw b")
    (root / paths.PAGES / "c.html").write_text("raw c")
    (root / paths.PAGES / "d.html").write_text("raw d")
    led = Ledger(root)
    led.add("https://example.org/a", id="a", status="in", file="literature/demo/data/raw/pdfs/a.pdf", question="Q1")
    led.add("https://example.org/b", id="b", status="in", file="literature/demo/data/raw/pdfs/b.pdf", question="Q1, Q2")
    led.add("https://example.org/c", id="c", status="in", file="literature/demo/data/raw/pages/c.html")
    led.add("https://example.org/d", id="d", status="out", file="literature/demo/data/raw/pages/d.html", question="Q2")
    led.add("https://example.org/e", id="e", status="in", file="literature/demo/data/raw/pdfs/gone.pdf", question="Q2")
    led.add("https://example.org/f", id="f", status="in", question="Q2")
    led.save()
    (root / "records" / "a.json").write_text("{}")
    return root


def _raw(root):
    return sorted(str(p.relative_to(root / paths.RAW)) for p in (root / paths.RAW).rglob("*") if p.is_file())


def test_files_are_moved_into_topic_folders_and_stored_paths_follow(tmp_path):
    root = _library(tmp_path)
    (root / paths.FETCH_LOG).write_text(
        json.dumps({"id": "a", "path": "literature/demo/data/raw/pdfs/a.pdf"}) + "\n"
        + json.dumps({"id": "x", "path": "literature/demo/data/raw/pdfs/x.pdf", "removed": "gone"}) + "\n")
    (root / paths.TEXT).mkdir(parents=True)
    (root / paths.TEXT / "a.json").write_text(json.dumps({"id": "a", "file": "literature/demo/data/raw/pdfs/a.pdf"}))
    res = views.build(root)
    assert _raw(root) == ["pages/not-screened-in/d.html", "pages/unsorted/c.html",
                          "pdfs/Q1/a.pdf", "pdfs/Q1/b.pdf"]  # two topics: under the first
    assert res["moved"] == {"Q1": 2, "not-screened-in": 1, "unsorted": 1}
    assert res["file_missing"] == ["e"]  # reported, never guessed
    led = Ledger(root)
    assert led.get("a")["file"] == "literature/demo/data/raw/pdfs/Q1/a.pdf"
    assert led.get("e")["file"] == "literature/demo/data/raw/pdfs/gone.pdf"  # not on disk: left as recorded
    log = [json.loads(l) for l in (root / paths.FETCH_LOG).read_text().splitlines()]
    assert [e["path"] for e in log] == ["literature/demo/data/raw/pdfs/Q1/a.pdf", "literature/demo/data/raw/pdfs/x.pdf"]
    assert json.loads((root / paths.TEXT / "a.json").read_text())["file"] == "literature/demo/data/raw/pdfs/Q1/a.pdf"
    assert (root / paths.PDFS / "Q1" / "a.pdf").read_text() == "raw a"  # content untouched, a real file
    assert not (root / paths.PDFS / "Q1" / "a.pdf").is_symlink()


def test_a_second_run_moves_nothing_and_a_new_topic_moves_the_file(tmp_path):
    root = _library(tmp_path)
    views.build(root)
    assert views.build(root)["moved"] == {}
    led = Ledger(root)
    led.get("a")["question"] = "method"
    led.get("b")["status"] = "out"
    led.save()
    assert views.build(root)["moved"] == {"method": 1, "not-screened-in": 1}
    assert _raw(root) == ["pages/not-screened-in/d.html", "pages/unsorted/c.html",
                          "pdfs/method/a.pdf", "pdfs/not-screened-in/b.pdf"]
    assert not (root / paths.PDFS / "Q1").exists()  # emptied folders go


def test_a_file_is_never_moved_over_another(tmp_path):
    root = _library(tmp_path)
    (root / paths.PDFS / "Q1").mkdir()
    (root / paths.PDFS / "Q1" / "zz.pdf").write_text("other")
    (root / paths.PDFS / "zz.pdf").write_text("loose")
    led = Ledger(root)
    led.add("https://example.org/zz", id="zz", status="in", file="literature/demo/data/raw/pdfs/zz.pdf", question="Q1")
    led.save()
    res = views.build(root)
    assert (root / paths.PDFS / "Q1" / "zz.pdf").read_text() == "other"


def test_export_sorts_the_files(tmp_path, capsys):
    root = _library(tmp_path)
    (root / paths.TEXT).mkdir(parents=True)
    lit.main(["--root", str(root), "export"])
    out = json.loads(capsys.readouterr().out)
    assert out["raw_files"]["moved"]["Q1"] == 2
    assert (root / paths.PDFS / "Q1" / "b.pdf").exists()


def test_catalogue_lists_every_screened_in_source_by_topic_and_state(tmp_path):
    root = _library(tmp_path)
    res = views.build(root)
    assert res["catalogue"] == {"Q1": {"read": 1, "to-read": 1}, "Q2": {"to-read": 1, "no-file": 2},
                                "unsorted": {"to-read": 1}}
    text = (root / paths.CATALOGUE).read_text()
    assert "[a](../records/a.json)" in text            # read sources link to their record
    q2 = text.split("\n## Q2")[1].split("\n## ")[0]
    assert "No file yet (2)" in q2 and "| e |" in q2 and "| f |" in q2  # not downloaded, still listed
    assert "| d |" not in text                          # screened out: not in the catalogue
    assert text.index("## Q2") < text.index("## unsorted")  # unset topic last


def test_catalogue_escapes_table_breaking_titles(tmp_path):
    root = _library(tmp_path)
    led = Ledger(root)
    led.add("https://example.org/g", id="g", status="in", title="A | B\nC", question="Q1")
    led.save()
    views.build(root)
    assert "[A / B C](https://example.org/g)" in (root / paths.CATALOGUE).read_text()


def test_a_file_shared_by_two_sources_gets_one_folder_and_stays_there(tmp_path):
    # the same page reached under two ids, one screened out and listed first: found in the
    # UNFCCC library on 2026-11-25, where three such files moved back and forth on every export
    root = _library(tmp_path)
    led = Ledger(root)
    led.rows.insert(0, dict(led.get("d"), id="d0", file="literature/demo/data/raw/pdfs/a.pdf"))
    led.save()
    views.build(root)
    assert (root / paths.PDFS / "Q1" / "a.pdf").exists()  # the source screened in decides
    led = Ledger(root)
    assert led.get("d0")["file"] == led.get("a")["file"] == "literature/demo/data/raw/pdfs/Q1/a.pdf"
    assert views.build(root)["moved"] == {}


def test_source_kind_is_a_table_of_its_own_and_peer_review_is_never_inferred(tmp_path):
    """L10: coverage and kind are separate; "scholarly" does not become "peer reviewed"."""
    root = _library(tmp_path)
    led = Ledger(root)
    led.get("a")["source_type"] = "scholarly"
    led.save()
    (root / "records" / "b.json").write_text("{}")
    led = Ledger(root)
    led.get("b")["source_type"] = "ti"
    led.get("b")["peer_reviewed"] = False
    led.save()
    res = views.build(root)
    q1 = res["source_kind"]["Q1"]
    assert q1["read"] == 2
    assert q1["kind"]["Scholarly"] == 1 and q1["kind"]["TI publication"] == 1
    assert q1["peer_reviewed"] == {"yes": 0, "no": 1, "not recorded": 1}  # scholarly a: not recorded
    assert res["source_kind"]["Q2"]["kind"]["TI publication"] == 1  # b is read under both topics
    text = (root / paths.CATALOGUE).read_text()
    assert "## Kind of source read" in text
    cover, kind = text.split("## Kind of source read")[0], text.split("## Kind of source read")[1]
    assert "Scholarly" not in cover and "| Topic | Read | To read |" in cover
    assert "| Q1 | 2 | 1 | 1 |" in kind
