"""Where a library keeps each kind of file.

``literature/`` holds the shared tools (``src/rag/``, ``tests/``) and one library per study,
for example ``literature/unfccc/``. A library is a study's own knowledge base: its screening
decisions and topics belong to that study and are not inherited by another (rule 13). The
names below are relative to a library's folder, so the layout is defined once:

    ledger.jsonl, fetch-log.jsonl   the catalogue and the record of every download
    records/                        reading records (quotes, pages, claims)
    reports/                        written reports: search log, open copies, checks,
                                    and catalogue.md (sources by topic; rebuilt on export)
    data/raw/pdfs/<topic>/, data/raw/pages/<topic>/
                                    downloaded files, exactly as served; never changed in
                                    content. A new download lands at the top of pdfs/ or
                                    pages/ and the export step moves it to its topic folder
    data/processed/text/            1. the text extracted from each raw file
    data/processed/chunks/          2. that text cut into passages (passages.parquet)
    data/processed/index/           3. one vector per passage (vectors.npy) and meta.json
    data/processed/reader-picks/    passages picked for a reader (a reading aid, not the index)
    data/processed/screening.json   export of the ledger with screening counts
"""

from __future__ import annotations

from pathlib import Path

BASE = Path("literature")
NOT_LIBRARIES = {"src", "tests"}

LEDGER = Path("ledger.jsonl")
FETCH_LOG = Path("fetch-log.jsonl")
RECORDS = Path("records")
REPORTS = Path("reports")
OPEN_ACCESS = REPORTS / "open-access.md"
CATALOGUE = REPORTS / "catalogue.md"

RAW = Path("data") / "raw"
PDFS = RAW / "pdfs"
PAGES = RAW / "pages"

PROCESSED = Path("data") / "processed"
TEXT = PROCESSED / "text"
CHUNKS = PROCESSED / "chunks"
PASSAGES = CHUNKS / "passages.parquet"
INDEX = PROCESSED / "index"
VECTORS = INDEX / "vectors.npy"
INDEX_META = INDEX / "meta.json"
READER_PICKS = PROCESSED / "reader-picks"
SCREENING = PROCESSED / "screening.json"


def libraries(base: Path | str = BASE) -> list[str]:
    """The libraries that exist: the folders under ``literature/`` that hold a ledger."""
    base = Path(base)
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir()
                  if p.is_dir() and p.name not in NOT_LIBRARIES and (p / LEDGER).is_file())


def library(name: str | None = None, base: Path | str = BASE) -> Path:
    """The folder of one library. With no name, the only library there is.

    A name need not exist yet: a new study starts its library by naming it. With no name and
    none or several libraries, this stops and says which exist, and never picks one.
    """
    base = Path(base)
    if name:
        if name in NOT_LIBRARIES or Path(name).name != name:
            raise ValueError(f"'{name}' is not a library name")
        return base / name
    found = libraries(base)
    if len(found) == 1:
        return base / found[0]
    raise ValueError(
        f"name the library: {', '.join(found)}" if found else f"no library found under {base}/"
    )
