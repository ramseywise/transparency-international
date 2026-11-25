# The literature libraries

`literature/` holds the shared tools (`src/rag/`, `tests/`) and one library per study, for example `unfccc/`. A library is a study's own knowledge base. A new study starts an empty one and inherits nothing from another. Claude runs the tools (`uv run python -I -m rag <command>` from the workspace root, with `--library <study>` once there is more than one library).

## What is in a library

| Where, under `literature/<study>/` | What it is | In git |
|---|---|---|
| `ledger.jsonl` | Every source and link considered, its status, and the path of its file and text | yes |
| `fetch-log.jsonl` | Every download: address, date, result, checksum | yes |
| `records/` | One reading record per source that has been read: quotes, pages, claims | yes |
| `data/private/reports/` | Working reports: the search log, the open-access report, dated checks, and `catalogue.md`: every source screened in, by topic and by read, to read or no file yet | no |
| `data/raw/pdfs/<topic>/`, `data/raw/pages/<topic>/` | Downloaded PDFs and web pages, exactly as received, one folder per topic of the study. Never edited | yes |
| `data/processed/text/` | Step 1: the text taken out of each raw file | yes |
| `data/processed/chunks/` | Step 2: that text cut into passages, all in `passages.parquet` | yes |
| `data/processed/index/` | Step 3: one vector per passage (`vectors.npy`: the passage's meaning as numbers) and `meta.json` (date, counts, the model that made the vectors) | yes |
| `data/processed/reader-picks/` | Passages picked out for the source reader. A reading aid only | yes |
| `data/processed/screening.json` | The ledger exported with screening counts | yes |

**Topic folders.** A source screened in sits under its topic. One screened for two topics sits under the first (the catalogue lists it under both). Files of sources not screened in are in `not-screened-in/`. A new download lands at the top of `pdfs/` or `pages/`; `rag export` moves it to its folder and updates the path stored for it. Whether a source has been read is in `data/private/reports/catalogue.md`, not in the folder name.

Every path is set once, in `src/rag/paths.py`.

## Searching and reading

- **Search.** `rag index` makes steps 2 and 3 above for every source screened in. A search scores each passage by its words and by its meaning and returns the best, with source and page.
- **Reading records.** A source that a document cites is read in full into a record in `records/`, with checked quotes and page numbers. Search finds a passage; only a reading record lets it be cited.

## What is in git, and why

Everything in a library is in git, the downloaded files and the search index included (Ramsey's decision, 2026-11-25), so that the MCP server can search the library from any machine straight after a clone. The repository is public, so a library holds only what is worth keeping: a source that is TI's own, cited in the study's documents, or read into a record. Web pages that were downloaded but never read or cited are deleted and marked screened out in the ledger, which keeps their address.

Material that is not public, such as an unpublished draft a researcher supplied, is not kept in the library at all: the repository is public. If such a file is ever needed, put it in `data/private/`, which git ignores and the index does not read.

The ledger and download log record the address, date and checksum of each file, so a copy can be fetched again and checked.

The MCP server (read-only, for other clients) reads the ledger, the reading records and the search index.

## Rebuilding

| To rebuild | Run |
|---|---|
| text, from the raw files | `rag extract` |
| the passages and their vectors | `rag index` |
| the topic folders, `catalogue.md` and `screening.json` | `rag export` |

## The moves of 2026-11-25

The single library at `literature/` became the UNFCCC study's library at `literature/unfccc/`. Raw files went into topic folders under `data/raw/`, and everything made from them into `data/processed/`. The stored paths in `ledger.jsonl`, `fetch-log.jsonl` and seven reading records were rewritten to match; older reports still name the old paths. `tests/test_library.py` checks that every raw file has one ledger row, sits in its topic folder and is not held twice.

The raw files were lost from disk that day and downloaded again; `unfccc/data/private/reports/recovery-2026-11-25.md` (not in git) records what came back identical, what differs and what is still missing.
