import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doc_length  # noqa: E402

DOC = """# Title

## 1. Summary

One two three four five.

## 2. Method

Six seven eight, see [the requirements](docs/technical-requirements.md).

## Endnotes

1. A long note that is not main text.

## Annex A

More words that do not count.
"""


def test_counts_main_text_and_back_matter_apart(tmp_path):
    p = tmp_path / "d.md"
    p.write_text(DOC)
    secs = {s["title"]: s for s in doc_length.sections(DOC)}
    assert secs["1. Summary"]["words"] == 5 and not secs["1. Summary"]["back"]
    assert secs["2. Method"]["words"] == 5  # the link counts as one word
    assert secs["Endnotes"]["back"] and secs["Annex A"]["back"]
    text, over = doc_length.report(p, max_words=10)
    assert not over and "main text: 10 words" in text
    assert doc_length.main([str(p), "--max", "9"]) == 1
