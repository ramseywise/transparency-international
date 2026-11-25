"""Raw files in topic folders, and the catalogue; both follow the ledger on every export.

A library's raw files are real files grouped by the study's topics, so they can be browsed
and opened:

    data/raw/pdfs/<topic>/<id>.pdf
    data/raw/pages/<topic>/<id>.html

- A source screened in sits under its topic (Q1, Q2, method, context for the UNFCCC study).
  One screened for two topics sits under the first; the catalogue lists it under both.
- A file whose source is not screened in sits under ``not-screened-in/``.
- A source screened in with no topic sits under ``unsorted/``.

A new download lands at the top of ``pdfs/`` or ``pages/``. ``sort`` moves each file to its
folder and rewrites the path stored for it in the ledger, the download log and the extracted
text. A file is moved, never copied or changed, and never over another file. Whether a source
has been read is not in the path, since reading it would mean moving it: that is in
``data/private/reports/catalogue.md``, which also lists the sources with no file yet. It is a
working file, not in git.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from rag import paths
from rag.ledger import Ledger

UNSORTED = "unsorted"
NOT_IN = "not-screened-in"
KINDS = (paths.PDFS, paths.PAGES)


def _topics(question) -> list[str]:
    names = [t.strip() for t in str(question or "").split(",") if t.strip()]
    return names or [UNSORTED]


def folder_for(row: dict) -> str:
    """The folder a source's raw files belong in."""
    if row.get("status") not in ("in", "read"):
        return NOT_IN
    return _topics(row.get("question"))[0]


def _held(root: Path) -> dict[tuple[Path, str], Path]:
    """Every raw file on disk, by kind (pdfs or pages) and file name."""
    found: dict[tuple[Path, str], Path] = {}
    for kind in KINDS:
        if (root / kind).is_dir():
            for p in sorted((root / kind).rglob("*")):
                if p.is_file() and not p.name.startswith("."):
                    found.setdefault((kind, p.name), p)
    return found


def _kind(stored: str) -> Path | None:
    for kind in KINDS:
        if f"{kind.as_posix()}/" in Path(stored).as_posix():
            return kind
    return None


def _stored(old: str, kind: Path, folder: str) -> str:
    """The stored path after the move, written from the same starting point as before."""
    old = Path(old).as_posix()
    return f"{old[: old.rfind(kind.as_posix())]}{kind.as_posix()}/{folder}/{Path(old).name}"


def file_folders(rows: list[dict]) -> dict[tuple[Path, str], str]:
    """The folder of every raw file the ledger names, by kind (pdfs or pages) and file name.

    One file can be the file of two rows (the same page reached under two ids). It gets one
    folder: that of the first row screened in, and only otherwise ``not-screened-in``.
    """
    shared: dict[tuple[Path, str], str] = {}
    for row in rows:
        for key in ("file", "original"):
            stored = row.get(key)
            kind = _kind(stored) if stored else None
            if kind is not None:
                name, folder = (kind, Path(stored).name), folder_for(row)
                if name not in shared or (shared[name] == NOT_IN and folder != NOT_IN):
                    shared[name] = folder
    return shared


def sort(root: Path | str = "literature") -> dict:
    """Move every raw file to its topic folder and update the paths stored for it."""
    root = Path(root)
    ledger = Ledger(root)
    held = _held(root)
    moved: dict[str, str] = {}  # stored path before -> after
    missing, blocked = [], []
    counts: Counter = Counter()
    shared = file_folders(ledger.rows)
    for row in ledger.rows:
        for key in ("file", "original"):
            stored = row.get(key)
            kind = _kind(stored) if stored else None
            if kind is None:
                continue
            folder = shared[(kind, Path(stored).name)]
            now = held.get((kind, Path(stored).name))
            if now is None:
                if key == "file" and row.get("status") in ("in", "read"):
                    missing.append(row["id"])
                continue
            target = root / kind / folder / now.name
            if now != target:
                if target.exists():
                    blocked.append(row["id"])
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                now.rename(target)
                held[(kind, now.name)] = target
                counts[folder] += 1
            new = _stored(stored, kind, folder)
            if new != stored:
                moved[stored] = new
                row[key] = new
    if moved:
        ledger.save()
        _rewrite_log(root, moved)
        _rewrite_text(root, moved)
    for kind in KINDS:  # folders left empty by a change of topic
        if (root / kind).is_dir():
            for d in (root / kind).iterdir():
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()
    return {"moved": dict(sorted(counts.items())), "file_missing": missing, "not_moved_target_exists": blocked}


def _rewrite_log(root: Path, moved: dict[str, str]) -> None:
    log = root / paths.FETCH_LOG
    if not log.exists():
        return
    lines = []
    for line in log.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            if rec.get("path") in moved:
                rec["path"] = moved[rec["path"]]
                line = json.dumps(rec, ensure_ascii=False)
        lines.append(line)
    log.write_text("\n".join(lines) + "\n")


def _rewrite_text(root: Path, moved: dict[str, str]) -> None:
    if not (root / paths.TEXT).is_dir():
        return
    for path in (root / paths.TEXT).glob("*.json"):
        doc = json.loads(path.read_text())
        if isinstance(doc, dict) and doc.get("file") in moved:
            doc["file"] = moved[doc["file"]]
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1))


def build(root: Path | str = "literature") -> dict:
    """Sort the raw files into their topic folders and rebuild the catalogue. Returns the counts."""
    root = Path(root)
    res = sort(root)
    held = _held(root)
    listed: dict[str, dict[str, list[dict]]] = {}
    for row in Ledger(root).rows:
        if row.get("status") not in ("in", "read"):
            continue
        kind = _kind(row["file"]) if row.get("file") else None
        on_disk = kind is not None and (kind, Path(row["file"]).name) in held
        if (root / paths.RECORDS / f"{row['id']}.json").exists():
            state = "read"
        else:
            state = "to-read" if on_disk else "no-file"
        for topic in _topics(row.get("question")):
            listed.setdefault(topic, {}).setdefault(state, []).append(row)
    kinds = source_kinds(listed)
    _catalogue(root, listed, kinds)
    return res | {"catalogue": {t: {k: len(v) for k, v in s.items()} for t, s in sorted(listed.items())},
                  "source_kind": kinds}


STATES = [("read", "Read"), ("to-read", "To read"), ("no-file", "No file yet")]

# The kind of each read source, as recorded in the ledger's ``source_type``, kept apart from
# coverage (requirement L10): how much has been read says nothing about what kind it is.
# "scholarly" is not "peer reviewed": a preprint or a working paper is scholarly too. Peer review
# is counted from the ledger's own ``peer_reviewed`` field, and where that is empty it is
# "not recorded", never inferred from the source type.
SOURCE_KINDS = [("scholarly", "Scholarly"), ("ti", "TI publication"), ("report", "Other report (NGO, think tank)"),
                ("official", "Official"), ("data", "Data"), ("news", "News"), ("other", "Other"),
                (None, "Not recorded")]
PEER = [(True, "yes"), (False, "no"), (None, "not recorded")]


def source_kinds(listed: dict) -> dict:
    """Per topic, the read sources counted by kind and, separately, by whether peer review is recorded."""
    known = {k for k, _ in SOURCE_KINDS}
    out = {}
    for topic, states in listed.items():
        rows = states.get("read", [])
        kind = Counter(r.get("source_type") if r.get("source_type") in known else None for r in rows)
        peer = Counter(r.get("peer_reviewed") if isinstance(r.get("peer_reviewed"), bool) else None for r in rows)
        out[topic] = {"read": len(rows),
                      "kind": {label: kind.get(k, 0) for k, label in SOURCE_KINDS},
                      "peer_reviewed": {label: peer.get(k, 0) for k, label in PEER}}
    return dict(sorted(out.items()))


def _cell(text) -> str:
    return str(text or "").replace("|", "/").replace("\n", " ").strip()


def _catalogue(root: Path, listed: dict, kinds: dict | None = None) -> Path:
    """Write ``data/private/reports/catalogue.md``: every screened-in source by topic and reading state."""
    topics = sorted(listed, key=lambda t: (t == UNSORTED, t))
    L = ["# Library catalogue", "",
         "Every source screened in, by topic and by how far it has got. Rebuilt from `ledger.jsonl` "
         "by `rag export`; do not edit by hand. The topics are the study's questions, set out in "
         "`search-log.md`. A source screened for two topics is listed under both; its file is in the "
         "folder of the first. Files are in `data/raw/pdfs/<topic>/` and `data/raw/pages/<topic>/`.", "",
         "- **Read**: has a reading record in `records/` (quotes, pages, claims).",
         "- **To read**: the file is downloaded, no reading record yet.",
         "- **No file yet**: not downloaded, usually because no open copy was found; "
         "`open-access.md` lists where to look.", "",
         "| Topic | Read | To read | No file yet |", "|---|---|---|---|"]
    for t in topics:
        L.append(f"| {t} | " + " | ".join(str(len(listed[t].get(k, []))) for k, _ in STATES) + " |")
    kinds = kinds if kinds is not None else source_kinds(listed)
    L += ["", "## Kind of source read", "",
          "The read sources of each topic by kind, as recorded in the ledger (`source_type`), and by whether "
          "peer review is recorded (`peer_reviewed`). This is a separate question from how much has been read: "
          "the table above. \"Scholarly\" includes preprints and working papers; it does not mean peer reviewed.", "",
          "| Topic | Read | " + " | ".join(label for _, label in SOURCE_KINDS)
          + " | Peer reviewed: " + " / ".join(label for _, label in PEER) + " |",
          "|---|---|" + "---|" * len(SOURCE_KINDS) + "---|"]
    for t in topics:
        k = kinds[t]
        L.append(f"| {t} | {k['read']} | " + " | ".join(str(k["kind"][label]) for _, label in SOURCE_KINDS)
                 + " | " + " / ".join(str(k["peer_reviewed"][label]) for _, label in PEER) + " |")
    for t in topics:
        L += ["", f"## {t}"]
        for key, label in STATES:
            rows = sorted(listed[t].get(key, []), key=lambda r: (_cell(r.get("title")) or r["id"]).lower())
            if not rows:
                continue
            L += ["", f"### {label} ({len(rows)})", "", "| Source | Year | Id |", "|---|---|---|"]
            for r in rows:
                title = _cell(r.get("title")) or r["id"]
                url = r.get("doi_or_url")
                src = f"[{title[:140]}]({url})" if url else title[:140]
                rid = f"[{r['id']}](../records/{r['id']}.json)" if key == "read" else r["id"]
                L.append(f"| {src} | {r.get('year') or ''} | {rid} |")
    path = root / paths.CATALOGUE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n")
    return path
