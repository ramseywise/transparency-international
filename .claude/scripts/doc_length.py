"""Count the words in a Markdown document, section by section, against a length budget.

    uv run python -I .claude/scripts/doc_length.py <file.md> [--max WORDS]

The main text is everything before the first heading named Endnotes, References, Notes,
Bibliography or Annex. Annexes and notes are counted separately and not held to --max.
One page is taken as 450 words. Exits with 1 when the main text is over --max, so a skill
can stop before handing over a document that is too long.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WORDS_PER_PAGE = 450
BACK_MATTER = re.compile(r"^#{1,3}\s+(annex|appendix|endnotes|references|notes|bibliography)\b",
                         re.IGNORECASE)
HEADING = re.compile(r"^(#{1,2})\s+(.*)")


def words(text: str) -> int:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"\[\^?[^\]]*\]\([^)]*\)", " link ", text)  # a link counts as one word
    return len(re.findall(r"[A-Za-z0-9À-ɏ][\w'’.-]*", text))


def sections(text: str) -> list[dict]:
    """[{title, words, back}] for each level-1 or level-2 heading (and any text before it)."""
    out, title, buf, back = [], "(before the first heading)", [], False
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            out.append({"title": title, "words": words("\n".join(buf)), "back": back})
            title, buf = m.group(2).strip(), []
            back = back or bool(BACK_MATTER.match(line))
        else:
            buf.append(line)
    out.append({"title": title, "words": words("\n".join(buf)), "back": back})
    return [s for s in out if s["words"] or s["title"] != "(before the first heading)"]


def report(path: Path, max_words: int | None) -> tuple[str, bool]:
    secs = sections(path.read_text(encoding="utf-8"))
    main = sum(s["words"] for s in secs if not s["back"])
    back = sum(s["words"] for s in secs if s["back"])
    lines = [f"{path.name}", f"{'words':>7}  section"]
    lines += [f"{s['words']:>7}  {'(back) ' if s['back'] else ''}{s['title']}" for s in secs]
    lines.append(f"main text: {main} words, about {main / WORDS_PER_PAGE:.0f} pages; "
                 f"annexes and notes: {back} words")
    over = max_words is not None and main > max_words
    if max_words is not None:
        lines.append(f"budget: {max_words} words. " + (
            f"OVER by {main - max_words}: cut before handing over." if over else "Within budget."))
    return "\n".join(lines), over


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="doc_length")
    ap.add_argument("file", type=Path)
    ap.add_argument("--max", type=int, help="word limit for the main text")
    a = ap.parse_args(argv)
    text, over = report(a.file, a.max)
    print(text)
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
