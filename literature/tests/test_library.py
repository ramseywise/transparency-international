"""Each real library holds together: every file has a home, every stored path exists, and the
search index holds exactly the sources screened in.

These read the libraries themselves (``literature/<study>/``), not a fixture. ``data/`` is kept
out of git, so on a fresh copy of the repository the checks that need it are skipped.
"""

import json
from pathlib import Path

import pytest

from rag import paths
from rag.ledger import Ledger

LITERATURE = Path(__file__).resolve().parents[1]     # literature/
WORKSPACE = LITERATURE.parent
LIBRARIES = paths.libraries(LITERATURE)


@pytest.fixture(params=LIBRARIES)
def ROOT(request) -> Path:
    """One library's folder; every test below runs once per library."""
    return LITERATURE / request.param


@pytest.fixture
def needs_data(ROOT):
    if not (ROOT / paths.RAW).is_dir():
        pytest.skip("data/ is not in this copy")


def _rows(root):
    return Ledger(root).rows


def _exists(stored: str) -> bool:
    """A stored path is written from the workspace root (``literature/<study>/data/...``)."""
    return (WORKSPACE / stored).exists()


def test_there_is_a_library_and_nothing_loose_beside_the_tools():
    assert LIBRARIES, "no library under literature/"
    loose = [n for n in ("ledger.jsonl", "fetch-log.jsonl", "records", "reports", "data")
             if (LITERATURE / n).exists()]
    assert loose == [], "library files at literature/ itself: they belong in literature/<study>/"


def test_the_tools_refuse_to_use_literature_itself_as_a_library():
    with pytest.raises(ValueError):
        Ledger(paths.BASE)


def test_every_stored_path_is_inside_its_own_library(ROOT):
    prefix = f"literature/{ROOT.name}/"
    stray = [(r["id"], r[k]) for r in _rows(ROOT) for k in ("file", "original", "text")
             if r.get(k) and not r[k].startswith(prefix)]
    assert stray == []


def _rows(ROOT):
    return Ledger(ROOT).rows


def _exists(stored: str) -> bool:
    """A stored path is written from the workspace root (``literature/data/...``)."""
    return (WORKSPACE / stored).exists()


def _raw_files(root):
    return [p for d in (paths.PDFS, paths.PAGES) if (root / d).is_dir()
            for p in (root / d).rglob("*") if p.is_file() and not p.name.startswith(".")]


@pytest.mark.usefixtures("needs_data")
def test_every_raw_file_has_a_ledger_row(ROOT):
    homes = {Path(r[k]).name for r in _rows(ROOT) for k in ("file", "original") if r.get(k)}
    raw = {p.name for p in _raw_files(ROOT)}
    assert sorted(raw - homes) == []


@pytest.mark.usefixtures("needs_data")
def test_every_raw_file_sits_in_the_folder_of_its_topic(ROOT):
    """`rag export` sorts them; a file elsewhere means the export has not been run since."""
    from rag import views

    want = {name: folder for (_, name), folder in views.file_folders(_rows(ROOT)).items()}
    wrong = [str(p) for p in _raw_files(ROOT) if p.name in want and p.parent.name != want[p.name]]
    assert wrong == []


@pytest.mark.usefixtures("needs_data")
def test_no_raw_file_is_held_twice(ROOT):
    names = [(p.relative_to(ROOT / paths.RAW).parts[0], p.name) for p in _raw_files(ROOT)]
    assert sorted({n for n in names if names.count(n) > 1}) == []


@pytest.mark.usefixtures("needs_data")
def test_every_path_in_the_ledger_exists(ROOT):
    missing = [(r["id"], k, r[k]) for r in _rows(ROOT) for k in ("file", "original", "text")
               if r.get(k) and not _exists(r[k])]
    assert missing == []


@pytest.mark.usefixtures("needs_data")
def test_every_download_still_on_disk_unless_marked_removed(ROOT):
    log = [json.loads(l) for l in (ROOT / paths.FETCH_LOG).read_text().splitlines() if l.strip()]
    missing = [e["id"] for e in log if e.get("path") and not e.get("removed") and not _exists(e["path"])]
    assert missing == []


def test_every_reading_record_belongs_to_a_source_screened_in(ROOT):
    status = {r["id"]: r.get("status") for r in _rows(ROOT)}
    stray = [p.stem for p in (ROOT / paths.RECORDS).glob("*.json") if status.get(p.stem) not in ("in", "read")]
    assert stray == []


def test_index_holds_exactly_the_sources_screened_in_with_text(ROOT):
    import pandas as pd

    if not (ROOT / paths.PASSAGES).exists():
        pytest.skip("no index in this copy")
    indexed = set(pd.read_parquet(ROOT / paths.PASSAGES, columns=["source_id"])["source_id"])
    wanted = {r["id"] for r in _rows(ROOT) if r.get("status") in ("in", "read") and r.get("text")}
    meta = json.loads((ROOT / paths.INDEX_META).read_text())
    assert sorted(indexed - wanted) == [], "screened out or unknown sources in the index"
    # a gap is allowed only when the index names it: text with no passage in it
    assert sorted(wanted - indexed) == meta.get("screened_in_without_passages")
