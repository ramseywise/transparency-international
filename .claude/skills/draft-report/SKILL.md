---
name: draft-report
description: Draft a research report or paper from a study's outputs, codebook, validation report and literature review, with every number and citation traceable. Use when the researcher asks to write, draft or outline the report, paper, methods note or a section of it.
---

# Draft the report

## Before starting

Needed: generated tables in `<study>/outputs/`, the approved research proposal (`<study>/docs/research-proposal.md`), the approved codebook, the validation report, the literature review, and `.claude/docs/house-style.md` (run `/house-style` if it does not exist). If the validation is not done, a draft may be written but every finding is marked provisional.

The report continues the proposal. Its background, literature and method sections start from the approved proposal text, updated for what was actually done; any departure from the proposal is stated in the method section with the reason.

## Steps

1. **Outline first.** One line per section and the one finding each results section will state. Unless the researcher says otherwise, the final document is an **online article** in the feature register of the house style, like the two TI articles in the library: a short summary of findings, a story-led body with the data source named before each number, linked sources, a list of recommendations, and a closing Methodology section that ends on the limits. Confirm the length with the researcher (an online article is usually 1,500 to 3,000 words), write the word budget for each section into the outline, then agree it.
2. **Write in this order** (the order of writing, not of the article; in the article the method goes last and the full detail stays in the approved proposal, which the article links to or annexes):
   1. Data and method: from the codebook, cleaning log, validation plan and report. Include where a language model was used, the model and dates, and how its output was checked.
   2. Results: one section per research question. State the finding, then the table or chart, then the range and the share that is unknown.
   3. Limitations: registered is not attended; self-declared affiliations; measured error rates; uneven unknowns across countries; one expert.
   4. Background and literature: from the review.
   5. Discussion and recommendations: what follows from the results, kept apart from the results.
   6. Summary: last.
3. **Numbers.** Take each one from a file in `outputs/` and keep a list in `<study>/report/numbers.md`: the number, the sentence it is in, the file and cell it came from.
4. **Citations.** Cite only sources with a reading record, with the page. Keep the reference list generated from the ledger.
5. **Named organisations.** Listing an organisation as fossil-linked is a public claim. Put every name the draft uses in `<study>/report/named-organisations.md` with its evidence record, and ask the researcher to sign off each one before the draft is shared.
6. **Count, then save** to `<study>/report/draft-vN.md`. Count with `uv run python -I .claude/scripts/doc_length.py <file> --max <agreed length>`; if it is over, cut against the outline's budgets before anything else. Then run `/check-work` on it.
7. **Hand over** to the lead researcher, with a half-page cover note: the headline findings with their ranges, what is provisional, the named organisations awaiting her sign-off, and that she may rewrite any part. Export a Word version with the `docx` skill if she works in Word. This is an approval point. What she sends back is handled by `/revise-report`.

## Writing standard

- Follow `.claude/docs/house-style.md` for structure, voice, terms and number format. Where it conflicts with the points below, the points below win.
- Academic in care, plain in language. Short sentences, defined terms, no jargon the reader has not been given.
- Say each thing once. Detail the approved proposal already holds is linked, not restated.
- Say what the data shows, not more. "Registered", not "attended". "Linked to", as the codebook defines it, not "lobbyist", unless the codebook defines that too.
- Give every count with its share and its base. Give ranges where the validation supplies them.
- Charts follow the `dataviz` skill.
- No sentence may rest on something you remember about an organisation or a paper.
