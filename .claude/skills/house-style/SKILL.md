---
name: house-style
description: Derive or update the writing style guide from published Transparency International documents in the library, so that proposals and reports read like TI's own. Use when the researcher asks to match, copy, extract or update the house style, when new TI publications are added to the library, or before the first draft of a proposal or report if `.claude/docs/house-style.md` does not exist.
---

# House style

Output: `.claude/docs/house-style.md`, a short guide that every writing skill loads before drafting. It describes how TI writes, with evidence. It is not a place for rules we would like TI to follow.

## Steps

1. **Choose the models.** List the TI publications in `literature/<study>/ledger.jsonl` that have extracted text. Group them by kind, because TI writes them differently: research reports and working papers (PDF), news and feature articles (web), policy positions. Ask the researcher which kind the next document should resemble, and whether any listed item is not a good model. At least three documents in total, and at least one of the target kind. If the library has fewer, say so and offer `/find-sources`.
2. **Read the full text** of each from `literature/<study>/data/processed/text/<id>.json`. Do not work from search results or from memory of how TI writes.
3. **Record patterns, each with evidence.** A pattern goes in the guide only if it has a short verbatim example (under 25 words) with source id and page or paragraph, and appears in at least two documents. A pattern seen in one document is listed as "seen once". Cover:
   - **Structure:** the order of sections; how a report opens; where recommendations sit; how methodology and limitations are presented; length of summary.
   - **Voice and stance:** who is speaking ("we", "Transparency International", passive); how strong the claims are and how they are qualified; how companies and governments are named and criticised.
   - **Numbers and evidence:** how counts and shares are written; how sources are cited (footnotes, links, in text); how uncertainty and method caveats are worded.
   - **Terms and spelling:** British or American spelling; "per cent" or "%"; capitalisation of terms like Party, COP; the fixed vocabulary for recurring ideas (for example how lobbying, undue influence, conflicts of interest are named).
   - **Sentences and paragraphs:** typical length, use of headings, lists, call-out boxes, quotations.
4. **Write the guide**, 900 to 1,400 words, with these sections: Sources (ids and kinds, date derived); Voice and stance; Structure; Numbers and evidence; Terms and spelling; Do / avoid (a two-column table, at most ten rows); By document kind (only what differs between a research report and a web article); Open questions for the researcher.
5. **Check it.** Give the guide and the source texts to the `citation-checker` agent: every quoted example must appear at the stated location.
6. **Ask the researcher** the open questions, and whether TI has an official style guide or template. If it does, that document wins wherever the two differ; note the differences in the guide.

## How the guide is used

- `/research-proposal`, `/draft-report` and `/revise-report` read `.claude/docs/house-style.md` before writing and follow it for structure, voice, terms and number format.
- The guide governs how things are said. It never changes what may be said: the workspace rules on sources, numbers, uncertainty and named organisations come first. Where TI's published tone is stronger than this study's evidence supports, the evidence decides.
- Style is copied; sentences are not. Never reuse a sentence from a TI publication without quotation marks and a citation.

## Updating

Re-run when a new TI publication of the target kind is added, or when the researcher rewrites a draft: her edits are the best evidence of the style she wants. Compare her version with ours, add the patterns that recur, and note the date and source of each change at the foot of the guide.
