"""Does search find the right passage? Checked against questions with a known answer.

Each question in literature/tests/fixtures/search-questions.json names the source that answers it
and a phrase from the answering passage. A question counts as found when a passage
from that source containing that phrase is among the first results.

The thresholds sit just under the measured result (2026-11-24: 17 of 22 first,
20 of 22 in the first five), so the test fails if search gets worse. Do not edit a
question to make it pass: a miss is information. Known misses on that date: the
question asked in German, and the question asking for a definition.

Skipped when the library has not been indexed (for example on a fresh copy).
"""

import json
from pathlib import Path

import pytest
from rag import paths

# The questions are about the UNFCCC study's library.
ROOT = Path(__file__).parents[2] / "literature" / "unfccc"
QUESTIONS = Path(__file__).parent / "fixtures" / "search-questions.json"

pytestmark = pytest.mark.skipif(
    not (ROOT / paths.VECTORS).exists() or not QUESTIONS.exists(),
    reason="the literature index has not been built",
)


def ranks() -> list[tuple[dict, int | None]]:
    from rag import index

    out = []
    for t in json.loads(QUESTIONS.read_text()):
        hits = index.search(t["q"], ROOT, 8)
        rank = next((i + 1 for i, h in enumerate(hits)
                     if h["source_id"] == t["source"] and t["phrase"] in h["text"]), None)
        out.append((t, rank))
    return out


def test_search_finds_the_answering_passage():
    result = ranks()
    first = sum(r == 1 for _, r in result)
    top5 = sum(bool(r and r <= 5) for _, r in result)
    missed = [t["q"] for t, r in result if not r or r > 5]
    n = len(result)
    print(f"\nsearch quality: {first} of {n} first, {top5} of {n} in the first five; missed: {missed}")
    assert n, "no questions"
    assert top5 / n >= 0.85, f"only {top5} of {n} in the first five; missed: {missed}"
    assert first / n >= 0.70, f"only {first} of {n} ranked first"
