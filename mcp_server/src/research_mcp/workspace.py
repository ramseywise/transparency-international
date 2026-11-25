"""What the MCP server may read from the workspace, as plain functions.

Everything here is read-only. Nothing in this module writes, deletes or
downloads. Three limits are built in, not left to the client:

- a study's `data/` folder is never served (raw files, and tables that name people);
- only text documents in `docs/` (which holds the proposal), `report/` and `outputs/` are served;
- every answer says what was searched, so an empty result is not read as "does not exist".
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import sys
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

SERVED_FOLDERS = ("docs", "report", "outputs")
SERVED_TYPES = (".md", ".csv", ".json", ".txt")
NOT_STUDIES = {"literature", "evals", "templates", "mcp_server"}
GUIDE_FILES = (
    "CLAUDE.md",
    ".claude/docs/research-workflows.md",
    ".claude/docs/research-governance.md",
    ".claude/docs/evidence-standards.md",
    ".claude/docs/new-study-guide.md",
    ".claude/docs/client-setup.md",
    ".claude/docs/architecture.md",
)
MAX_CHARS = 20_000

EMPTY_IS_NOT_ABSENT = (
    "An empty or short result means nothing was found in the places listed under "
    "'searched'. It does not show that the information does not exist."
)


class NotAvailable(ToolError):
    """The request names something this server does not hold or does not serve.

    A ToolError, so the client is shown the message and can correct the request.
    """


def workspace_root() -> Path:
    """The workspace folder: TI_RESEARCH_ROOT if set, otherwise the folder holding this code."""
    env = os.environ.get("TI_RESEARCH_ROOT")
    return Path(env).expanduser().resolve() if env else Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------- the guide


def operating_guide(root: Path, part: str | None = None) -> dict:
    """The rules for working in this workspace: CLAUDE.md, or one of the documents it points to."""
    available = [p for p in GUIDE_FILES if (root / p).is_file()]
    wanted = part or "CLAUDE.md"
    if wanted not in available:
        raise NotAvailable(f"No guide document '{wanted}'. Available: {', '.join(available)}.")
    return {
        "document": wanted,
        "text": (root / wanted).read_text(),
        "other_documents": [p for p in available if p != wanted],
        "note": (
            "This server is read-only. Skills (the /commands), agents and the raw-file "
            "safeguard named in the guide work only in Claude Code. In any other client, "
            "follow the rules by hand and say which steps could not be run. "
            ".claude/docs/research-workflows.md says, for each kind of request, which "
            "workflow it needs, which checks must run before the result is trusted, and "
            "how to sort open questions so the researcher is asked only the research ones."
        ),
    }


# ---------------------------------------------------------------- studies


def list_studies(root: Path) -> list[dict]:
    """Every study folder: a top-level folder with a decision log."""
    out = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        if folder.name.startswith(".") or folder.name in NOT_STUDIES:
            continue
        if (folder / "docs" / "decisions.md").is_file():
            out.append({"study": folder.name, "documents": len(_documents(folder))})
    return out


def _study_folder(root: Path, study: str) -> Path:
    names = [s["study"] for s in list_studies(root)]
    if study not in names:
        raise NotAvailable(f"No study '{study}'. Studies here: {', '.join(names) or 'none'}.")
    return root / study


def _served(folder: Path, path: Path) -> bool:
    rel = path.relative_to(folder)
    return (
        len(rel.parts) >= 2
        and rel.parts[0] in SERVED_FOLDERS
        and path.suffix.lower() in SERVED_TYPES
        and not path.name.lower().startswith("delegates")
        and not any(part.startswith(".") for part in rel.parts)
    )


def _documents(folder: Path) -> list[Path]:
    found = []
    for name in SERVED_FOLDERS:
        if (folder / name).is_dir():
            found += [p for p in (folder / name).rglob("*") if p.is_file() and _served(folder, p)]
    return sorted(found)


DOCUMENT_STATUSES = ("draft", "sent", "approved", "superseded")
STATUS_HEADING = "## Document status"
NOT_RECORDED = {
    "status": "not recorded",
    "meaning": "No status for this document in docs/decisions.md. Treat it as a draft.",
}


def document_status(folder: Path) -> dict[str, dict]:
    """The status of each document, from the table under '## Document status' in the log.

    The status is read from the decision log and nowhere else, so a client cannot take a
    draft for an approved text. A document not in the table is 'not recorded'.
    """
    log = folder / "docs" / "decisions.md"
    text = log.read_text() if log.is_file() else ""
    _, found, rest = text.partition("\n" + STATUS_HEADING)
    if not found:
        return {}
    section = re.split(r"\n## ", rest, maxsplit=1)[0]
    out = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not line.lstrip().startswith("|"):
            continue
        name, status = cells[0].strip("`"), cells[1].lower()
        if status in DOCUMENT_STATUSES:
            out[name] = {"status": status, "version": cells[2], "recorded": cells[3]}
    return out


THE_LOG = {
    "status": "record",
    "meaning": "The decision log itself: the record of what was decided, and by whom.",
}


def _status_of(statuses: dict[str, dict], document: str) -> dict:
    if document == "docs/decisions.md":
        return THE_LOG
    return statuses.get(document, NOT_RECORDED)


def get_study(
    root: Path, study: str, document: str | None = None, offset: int = 0,
    max_chars: int = MAX_CHARS,
) -> dict:
    """Without `document`: what the study holds. With it: the text of that document."""
    folder = _study_folder(root, study)
    statuses = document_status(folder)
    if document is None:
        return {
            "study": study,
            "documents": [
                {
                    "document": str(p.relative_to(folder)),
                    "characters": p.stat().st_size,
                    "status": _status_of(statuses, str(p.relative_to(folder)))["status"],
                }
                for p in _documents(folder)
            ],
            "not_served": (
                "The study's data/ folder (raw files and tables that name people), its "
                "code and its notebooks are not available through this server."
            ),
            "next": "Call get_study again with one 'document' to read it. Start with "
                    "docs/decisions.md and docs/technical-requirements.md.",
        }
    path = (folder / document).resolve()
    if not path.is_relative_to(folder.resolve()) or not path.is_file() or not _served(
        folder.resolve(), path
    ):
        listed = ", ".join(str(p.relative_to(folder)) for p in _documents(folder))
        raise NotAvailable(f"'{document}' is not a served document of '{study}'. Served: {listed}.")
    text = path.read_text(errors="replace")
    offset = max(0, offset)
    piece = text[offset : offset + max(1, min(max_chars, MAX_CHARS))]
    end = offset + len(piece)
    return {
        "study": study,
        "document": document,
        "text": piece,
        "total_characters": len(text),
        "next_offset": end if end < len(text) else None,
        "status": _status_of(statuses, document),
        "status_note": (
            "The status comes from the table 'Document status' in docs/decisions.md. "
            "Approval applies only to the version named there; a document that is not "
            "'approved' must not be quoted as the study's position."
        ),
    }


# ---------------------------------------------------------------- decisions


def get_decisions(root: Path, study: str, contains: str | None = None) -> dict:
    """The study's decision log: the dated decisions, and what is still open."""
    folder = _study_folder(root, study)
    text = (folder / "docs" / "decisions.md").read_text()
    head, _, open_part = text.partition("\n## Open")
    decisions = []
    for line in head.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[0]):
            decisions.append(
                {"date": cells[0], "decision": " | ".join(cells[1:-1]), "decided_by": cells[-1]}
            )
    open_part = re.split(r"\n## ", open_part, maxsplit=1)[0]
    still_open = [
        m.group(1).strip() for m in re.finditer(r"^- (.+)$", open_part, flags=re.M)
    ]
    if contains:
        needle = contains.lower()
        decisions = [d for d in decisions if needle in json.dumps(d).lower()]
        still_open = [o for o in still_open if needle in o.lower()]
    return {
        "study": study,
        "decisions": decisions,
        "open": still_open,
        "document_status": document_status(folder),
        "searched": [f"{study}/docs/decisions.md"],
        "note": (
            "Only what is recorded here counts as decided. An item under 'open', or a "
            "proposal with no decision row, is not approved. " + EMPTY_IS_NOT_ABSENT
        ),
    }


# ---------------------------------------------------------------- search of study documents


def _units(text: str) -> list[tuple[int, str]]:
    """The pieces a search matches against, each with its first line number.

    A paragraph is one piece. A table row is a piece of its own: a decision log is one
    long table, and matching it whole would return it for almost any query.
    """
    units: list[tuple[int, str]] = []
    start, held = 0, []
    for number, line in enumerate([*text.splitlines(), ""], start=1):
        is_row = line.lstrip().startswith("|")
        if held and (not line.strip() or is_row):
            units.append((start, "\n".join(held)))
            held = []
        if is_row:
            if not re.fullmatch(r"[\s|:-]+", line):
                units.append((number, line))
        elif line.strip():
            if not held:
                start = number
            held.append(line)
    return units


def search_research(root: Path, query: str, study: str | None = None, limit: int = 10) -> dict:
    """Find paragraphs and table rows in study documents that contain every word of the query."""
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 1]
    if not words:
        raise NotAvailable("The query has no words to search for.")
    studies = [study] if study else [s["study"] for s in list_studies(root)]
    hits, searched = [], []
    for name in studies:
        folder = _study_folder(root, name)
        statuses = document_status(folder)
        for path in _documents(folder):
            if path.suffix.lower() != ".md":
                continue
            searched.append(str(path.relative_to(root)))
            for line, unit in _units(path.read_text(errors="replace")):
                low = unit.lower()
                if all(w in low for w in words):
                    hits.append({
                        "study": name,
                        "document": str(path.relative_to(folder)),
                        "status": _status_of(statuses, str(path.relative_to(folder)))["status"],
                        "line": line,
                        "text": unit.strip()[:1200],
                        "score": sum(low.count(w) for w in words),
                    })
    hits.sort(key=lambda h: -h["score"])
    limit = max(1, min(limit, 50))
    return {
        "query": query,
        "results": hits[:limit],
        "found": len(hits),
        "searched": searched,
        "note": (
            "Word match only: a paragraph or table row is found if it contains every word "
            "of the query. "
            "Results may come from drafts; check docs/decisions.md for what is approved. "
            + EMPTY_IS_NOT_ABSENT
        ),
    }


# ---------------------------------------------------------------- literature

LEDGER_FIELDS = (
    "id", "title", "authors", "year", "type", "peer_reviewed", "doi_or_url", "status",
    "reason", "source_type", "tier", "tier_reason", "cited_by_count",
)


def _library(root: Path, library: str | None = None) -> Path:
    """The folder of one study's library, `literature/<study>/`. With no name, the only one."""
    from rag import paths

    base = root / "literature"
    found = paths.libraries(base)
    if library and library not in found:
        raise NotAvailable(
            f"No library named '{library}'. Libraries held: {', '.join(found) or 'none'}."
        )
    try:
        return paths.library(library, base)
    except ValueError:
        raise NotAvailable(
            "There is more than one library; pass `library`. Libraries held: "
            f"{', '.join(found)}." if found else "No literature library is held in this workspace."
        ) from None


def _ledger(lib: Path):
    from rag.ledger import Ledger

    return Ledger(lib)


def search_literature(
    root: Path, query: str, k: int = 8, source_id: str | None = None,
    library: str | None = None,
) -> dict:
    """Search the text of the sources held in the library, by keyword and by meaning."""
    from rag import index

    k = max(1, min(k, 25))
    lib = _library(root, library)
    state = index_state(root, library)
    if state["problem"]:
        raise NotAvailable(_index_message(state["problem"]))
    ledger = _ledger(lib)
    if source_id and source_id not in state["indexed"]:
        if (lib / "records" / f"{source_id}.json").is_file():
            raise NotAvailable(
                f"Source '{source_id}' has a reading record but its text is not in the search "
                f"index (built {state['built']}). Use get_evidence for its quotes; its full "
                "text cannot be searched until the index is rebuilt."
            )
        if ledger.get(source_id) is None:
            raise NotAvailable(
                f"No source with id '{source_id}' in the ledger. Search without source_id "
                "to find ids."
            )
        raise NotAvailable(
            f"Source '{source_id}' is in the ledger but its text is not held or not indexed, "
            "so it cannot be searched. Use get_evidence to see what is recorded about it."
        )
    try:
        # The index may print progress; on a stdio server, stdout belongs to the protocol.
        with contextlib.redirect_stdout(sys.stderr):
            rows = index.search(query, root=lib, k=k, source=source_id)
    except (SystemExit, ValueError, OSError, KeyError) as e:
        raise NotAvailable(_index_message(str(e) or type(e).__name__)) from None
    results = []
    for r in rows:
        row = ledger.get(r["source_id"]) or {}
        results.append({
            "source_id": r["source_id"],
            "title": row.get("title"),
            "year": row.get("year"),
            "location": r["loc"],
            "section": r.get("section"),
            "text": r["text"],
            "has_reading_record": (
                lib / "records" / f"{r['source_id']}.json"
            ).is_file(),
        })
    return {
        "query": query,
        "results": results,
        "library": lib.name,
        "searched": [f"the text of sources downloaded into literature/{lib.name}/ and indexed"],
        "index": {
            "built": state["built"],
            "sources": state["sources"],
            "passages": state["passages"],
        },
        "records_not_indexed": state["records_not_indexed"],
        "note": (
            "These are passages from sources, not checked findings. Quote a passage only "
            "with its source_id and location. Sources that were listed but never "
            "downloaded are not searched. "
            + (
                f"{len(state['records_not_indexed'])} source(s) have a reading record but "
                "are not in the index, so their text was not searched (listed under "
                "'records_not_indexed'). "
                if state["records_not_indexed"]
                else ""
            )
            + EMPTY_IS_NOT_ABSENT
        ),
    }


def _index_message(detail: str) -> str:
    return (
        f"The literature search index is missing, incomplete or being rebuilt ({detail}). "
        "It is built in Claude Code with the literature tools; this server cannot build it. "
        "The other tools still work: get_evidence gives the checked quotes of every source "
        "that was read, and search_research searches the study documents."
    )


def index_state(root: Path, library: str | None = None) -> dict:
    """When the search index was built, what it holds, and whether its files agree.

    Checked before every search, so a half-written or missing index gives a plain message
    and not a failure deep in the search code.
    """
    from rag import paths

    lib = _library(root, library)
    records = sorted(p.stem for p in (lib / paths.RECORDS).glob("*.json"))
    state = {
        "built": None, "sources": None, "passages": None, "indexed": set(),
        "records_not_indexed": records, "problem": None,
    }
    parquet, vectors, meta_path = (
        lib / paths.PASSAGES, lib / paths.VECTORS, lib / paths.INDEX_META
    )
    missing = [p.name for p in (parquet, vectors, meta_path) if not p.is_file()]
    if missing:
        state["problem"] = f"missing: {', '.join(missing)}"
        return state
    try:
        import numpy as np
        import pandas as pd

        meta = json.loads(meta_path.read_text())
        ids = pd.read_parquet(parquet, columns=["source_id"])["source_id"]
        n_vectors = np.load(vectors, mmap_mode="r").shape[0]
    except Exception as e:  # noqa: BLE001 - any unreadable file means the same to the user
        state["problem"] = f"a file cannot be read: {type(e).__name__}"
        return state
    state.update(
        built=meta.get("built"), sources=meta.get("sources"), passages=meta.get("passages"),
        indexed=set(ids),
    )
    state["records_not_indexed"] = [r for r in records if r not in state["indexed"]]
    if not (len(ids) == n_vectors == meta.get("passages")):
        state["problem"] = (
            f"its files disagree: {len(ids)} passages, {n_vectors} vectors, "
            f"{meta.get('passages')} recorded"
        )
    return state


def get_evidence(root: Path, source_id: str, library: str | None = None) -> dict:
    """One source: its entry in the ledger and, if it was read, its reading record."""
    lib = _library(root, library)
    row = _ledger(lib).get(source_id)
    if row is None:
        raise NotAvailable(
            f"No source with id '{source_id}' in the ledger. Use search_literature to find ids."
        )
    record_path = lib / "records" / f"{source_id}.json"
    record = json.loads(record_path.read_text()) if record_path.is_file() else None
    state = index_state(root, library)
    return {
        "library": lib.name,
        "source": {k: row.get(k) for k in LEDGER_FIELDS},
        "held": bool(row.get("file")),
        "in_search_index": None if state["problem"] else source_id in state["indexed"],
        "index_built": state["built"],
        "reading_record": record,
        "note": (
            "The reading record holds quotes with page numbers, checked against the "
            "source text."
            if record
            else "This source has no reading record: it has not been read. Its ledger "
                 "entry shows only that it was considered. Do not cite it as read."
        ),
    }
