"""A small search index over the extracted literature.

Each source is split into passages (a paragraph of a web page; a few
neighbouring blocks of a PDF page). A search combines two rankings: keyword
match (BM25) and meaning (a small multilingual embedding model that runs on
this computer; nothing is sent anywhere). Results always carry the source id
and the page or section, so a passage can be quoted and checked.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from rag import paths

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MIN_WORDS, MAX_WORDS = 60, 220


def _passages_html(doc: dict) -> list[dict]:
    out = []
    for section in doc["sections"]:
        buf, first = [], None
        last = None

        def flush():
            loc = f"para {first}" if first == last else f"paras {first}-{last}"
            out.append({"loc": loc, "section": section["heading"], "text": " ".join(buf)})

        for p in section["paragraphs"]:
            buf.append(p["text"])
            first, last = first or p["n"], p["n"]
            if sum(len(t.split()) for t in buf) >= MIN_WORDS:
                flush()
                buf, first = [], None
        if buf:
            flush()
    return out


def _passages_pdf(doc: dict) -> list[dict]:
    out = []
    for page in doc["pages"]:
        buf: list[str] = []
        for block in page["blocks"]:
            words = block.split()
            while len(words) > MAX_WORDS:  # a very long block is cut
                out.append({"loc": f"p.{page['page']}", "section": None, "text": " ".join(words[:MAX_WORDS])})
                words = words[MAX_WORDS:]
            buf.append(" ".join(words))
            if sum(len(t.split()) for t in buf) >= MIN_WORDS:
                out.append({"loc": f"p.{page['page']}", "section": None, "text": " ".join(buf)})
                buf = []
        if buf:
            out.append({"loc": f"p.{page['page']}", "section": None, "text": " ".join(buf)})
    return out


def passages(doc: dict) -> list[dict]:
    rows = _passages_pdf(doc) if doc["kind"] == "pdf" else _passages_html(doc)
    for i, r in enumerate(rows):
        r.update(source_id=doc["id"], title=doc.get("title"), chunk=i)
    return [r for r in rows if len(r["text"].split()) >= 5]


def _embed(texts: list[str]) -> np.ndarray:
    from fastembed import TextEmbedding

    model = TextEmbedding(EMBED_MODEL)
    vecs = np.array(list(model.embed(texts, batch_size=64)), dtype=np.float32)
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


def build(root: Path | str = "literature", embed: bool = True) -> dict:
    """Index the text of every source screened in (ledger status "in" or "read").

    Text files of sources screened out stay on disk but are left out, so a search never
    returns a source the study decided not to use.
    """
    from rag.ledger import Ledger

    root = Path(root)
    ids = {Path(r["text"]).stem: r["id"] for r in Ledger(root).rows
           if r.get("status") in ("in", "read") and r.get("text")}
    wanted = {f"{stem}.json" for stem in ids}
    ids = list(ids.values())
    files = sorted((root / paths.TEXT).glob("*.json"))
    rows = []
    for f in files:
        if f.name in wanted:
            rows += passages(json.loads(f.read_text()))
    if not rows:
        raise SystemExit("Nothing to index: no source screened in has text in data/processed/text/. "
                         "Run the crawl or extract step first.")
    df = pd.DataFrame(rows)
    for made in (paths.PASSAGES, paths.VECTORS):
        (root / made).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(root / paths.PASSAGES, index=False)
    if embed:
        np.save(root / paths.VECTORS, _embed(df["text"].tolist()))
    elif (root / paths.VECTORS).exists():
        (root / paths.VECTORS).unlink()
    meta = {"built": date.today().isoformat(), "sources": int(df["source_id"].nunique()),
            "passages": len(df), "embedding_model": EMBED_MODEL if embed else None,
            "text_files_not_screened_in": sum(f.name not in wanted for f in files),
            # screened in, but the saved text gives no passage (an empty or script-only page)
            "screened_in_without_passages": sorted(set(ids) - set(df["source_id"]))}
    (root / paths.INDEX_META).write_text(json.dumps(meta, indent=1))
    return meta


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9à-ÿ]+", text.lower())


def _bm25(query: str, docs: list[list[str]], k1: float = 1.5, b: float = 0.75) -> np.ndarray:
    n = len(docs)
    avg = sum(map(len, docs)) / n
    df = Counter(t for d in docs for t in set(d))
    scores = np.zeros(n)
    for term in set(_tokens(query)):
        if term not in df:
            continue
        idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
        for i, d in enumerate(docs):
            tf = d.count(term)
            if tf:
                scores[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(d) / avg))
    return scores


def search(query: str, root: Path | str = "literature", k: int = 8, source: str | None = None) -> list[dict]:
    root = Path(root)
    if not (root / paths.PASSAGES).exists():
        raise SystemExit("No index yet. Run: uv run python -m rag index")
    df = pd.read_parquet(root / paths.PASSAGES)
    kw = _bm25(query, [_tokens(t) for t in df["text"]])
    ranks = [pd.Series(-kw).rank(method="first")]
    vec_path = root / paths.VECTORS
    sem = None
    if vec_path.exists():
        vectors = np.load(vec_path)
        sem = vectors @ _embed([query])[0]
        ranks.append(pd.Series(-sem).rank(method="first"))
    # Reciprocal rank fusion: a passage ranked well by either method rises.
    df["score"] = sum(1.0 / (60 + r) for r in ranks).to_numpy()
    df["keyword"] = kw
    df["meaning"] = sem if sem is not None else np.nan
    if source:
        df = df[df["source_id"] == source]
    top = df.sort_values("score", ascending=False).head(k)
    hits = top[["source_id", "loc", "section", "text", "keyword", "meaning"]].to_dict("records")
    for h in hits:
        if not isinstance(h["section"], str):
            h["section"] = None  # PDFs have pages, not sections
    return hits
