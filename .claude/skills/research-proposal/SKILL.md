---
name: research-proposal
description: Turn a research brief, the literature review and the technical requirements into a research proposal (exposé) - background, questions, literature review, proposed definitions, methodology, limitations, timeline - for the lead researcher to approve or rewrite before any classification is done. Use when the researcher asks for a proposal, exposé, concept note, research design or methodology document, or when the literature review is finished and the codebook has not been started.
---

# Research proposal

The proposal is the first of two points where the work goes to the lead researcher as a document. She approves it, comments on it, or rewrites it. Nothing is classified until her version is taken back in. It is written so that she could defend the method to a colleague without having seen any of the code.

## Before starting

Needed:
- the brief (`<study>/docs/research-brief.md`)
- the finished literature review (`<study>/docs/literature-review.md`), checked by `citation-checker`
- the technical requirements (`<study>/docs/technical-requirements.md`)
- the data profile and cleaning log, for the description of the data
- `.claude/docs/house-style.md`. If it does not exist, run `/house-style` first.

If the literature review is not finished, do not draft sections 3 and 4. An outline with those sections marked "awaiting the literature review" may be shared instead, and must say so on its first line.

## What goes in

Translate; do not copy. The technical requirements are written for the people building the pipeline. The proposal is for a researcher and her colleagues. Requirement numbers, file names, tool names and model names stay out of the main text.

| Section | Source | Notes |
|---|---|---|
| 1. Summary | written last | half a page: the questions, the approach in three sentences, what she is asked to decide |
| 2. Background and research questions | the brief | her questions in her words; any change to scope or wording is listed in section 9, never made silently |
| 3. What the literature says | the literature review | condensed: how earlier studies defined and counted the study's key terms, where they disagree, the criticisms. Every statement with source and page. Name the fields covered (for example earlier counts, the academic work on the phenomenon, the method literature on classifying organisations and on machine-assisted coding) and say which are thin or missing. Sort each gap into one of three kinds and say who closes it: a gap in knowledge (the literature may answer it), a decision on method (the study proposes and justifies, she approves), or an empirical gap (the study measures it). Not every gap is the literature review's to close, and the proposal is not held back until all are closed. No claim to be the first study while the search is unfinished; state what the study adds instead. A source that has not been read is listed as unread; no definition or recommendation rests on it until it is |
| 4. Proposed definitions | the review's recommendations | each category with: its definition; the observable indicators; its **breadth and threshold** (what is in, what is out, and how much is enough: any activity, a current one, a material share, or only what is documented; for a threshold on exposure, which kind counts, how much, over which period, and from which sources); where a boundary is contested, a narrower and a broader version to be run side by side; the alternatives she could choose; and whether it comes from a cited source or is our own proposal |
| 4, hard cases | the data and the review | the cases the indicators do not settle, named up front with a proposed rule or a decision in section 9. Usually: state-owned bodies; organisations that span several categories (an association with members in many sectors); joint ventures, subsidiaries and holding companies; entries that describe a person's role (support staff, adviser) rather than a kind of organisation |
| 4, last subsection: dimensions and how they relate | all of section 4 | list each dimension the study records as a separate attribute (for example organisational type, economic sector, ownership, the property the study measures), with its values. One label never carries two dimensions. Legal status (what a register says the body is) is kept apart from activity (what it does). Say once whether a later dimension depends on an earlier one (for example, may a non-business hold a sector tier?) and keep to it in every later section |
| 5. Data | profile and cleaning log | what the list is, its size, what it does not tell us. Numbers from generated tables only. Name-matching problems are stated in the unit the study counts: how many people (or rows) sit behind the unresolved similar names and the ambiguous acronyms, not only how many names |
| 6. Method: preparing the data | cleaning log, technical requirements | the cleaning steps, and **entity resolution** (deciding which entries are the same organisation) as its own step, with how unresolved names and acronyms will be settled |
| 6. Method: evidence | technical requirements | an **evidence hierarchy**: which kinds of source are trusted, in what order, for each separate claim: that the organisation exists and is the one meant; that it does the activity; that the activity meets the threshold. A copy of each page used is archived with its date, not only the web address |
| 6. Method: classifying | technical requirements | in order: fixed rules, approved lists, look-ups. How missing entries are handled |
| 6. Method: checks | technical requirements | the automatic checks, and what they do and do not show |
| 6. Method: expert sample | technical requirements | the sample design written out as arithmetic: the groups (strata) and how many records each holds, the minimum per group, the total, and that they add up. Groups follow what the model predicted on each finding, so that likely missed cases (predicted negatives) are sampled, not only the confidence levels. The expert's workload in hours, estimated now and measured in the pilot |
| 6. Method: reporting and uncertainty | technical requirements | three kinds of uncertainty, reported separately: **classification error** (the label is wrong), **coverage** (the record could not be classified: unknowns) and **sampling** (error rates come from a sample). Name the estimator: weighted precision and recall, weighted table of what was confused with what, the method for intervals, and whether the finite size of the population is allowed for. Ranges built by putting all unknowns in or out of a category are bounds, never called confidence intervals. How each share is defined (counted, out of) |
| 6. Method: what the study produces | technical requirements | the organisation-level master table, one row per organisation: identity (name as written, matched entity, parent, country), classification on each dimension, evidence (source, quote, dates, evidence level, rule applied, confidence) and validation (model label, expert label, final label, error type, sampling weight). The person-level list joins to it, so the counts can be re-run under other definitions without new look-ups |
| 7. Use of a language model | technical requirements, section 5 | what the model does and does not do, the main risks and the control for each, in plain language. Also: finding evidence is kept apart from classifying it, so that the two kinds of error can be told apart and the same evidence re-classified under another definition; evidence is stored in fixed fields, each label citing a numbered rule; anything a fixed rule can decide is decided by code; what is recorded for every run (model and version, instructions, searches, pages retrieved, settings, date, retries and manual fixes); a fixed test set of known cases run before the full run and kept separate from the expert sample; and repeatability (two runs agree), validity (agrees with the expert) and coverage (share classifiable) reported as three different things. This section is what makes the method defensible: one line per point, not a sentence for the whole section and not an essay |
| 8. Limitations | technical requirements R8 and section 5 | including what cannot be removed, and coverage that may differ by language or country |
| 9. Decisions requested | all of the above | a numbered list, grouped by when the answer is needed: **before the pilot**, **before the full run**, **before publication**. For each: the question, the options, our recommendation and why, and what it changes downstream. Every design choice the method rests on appears here, including the evidence hierarchy, the dimensions and how they relate, and the sample design, not only the definitions |
| 10. Timeline and what is needed from her | implementation plan | including her time, and the expert's in hours, for the sample and for sign-off on named organisations |
| Annex A | technical requirements | a pointer to the technical requirements, with their version, not a copy of them |
| Annex B | ledger and search log | how the literature was searched: counts found, screened in, screened out, read, and a small flow diagram of those counts that adds up from first to last box |

Where the data are in several languages, searching in each organisation's own language is a requirement in section 6, not a mitigation in section 7.

## Length

The proposal is for a researcher to read in one sitting: **about 5,000 words of main text (10 to 12 pages), and never more than 6,500 (15 pages)**, unless she asked for a different length. Endnotes and annexes are not counted, but the annexes together stay under 2,000 words. Budgets per section, in words:

| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 350 | 900 | 1,000 | 350 | 1,100 | 450 | 250 | 600 | 200 |

The table in "What goes in" lists what must be *covered*, not what must be written at length. To fit:

- Say each thing once. A point made in one section is referred to from another ("see 4.3"), not repeated. No closing recap in a section.
- The literature review and the technical requirements already hold the detail. The proposal gives the finding and points there; it does not restate either.
- Options go in a table (option, what it includes, our recommendation), not in paragraphs.
- Each hard case is one or two lines: the case and the rule or decision number.
- A sentence that only says what the next paragraph will say is cut.

If the material does not fit, the answer is a shorter proposal and a pointer, not a longer proposal. Say in the cover note what was left in the supporting documents.

## Steps

1. **Outline.** One line per section and the decisions that will be requested. Agree it with whoever is running the session.
2. **Draft** to the budgets under "Length", in the order 3, 4, 5, 6, 7, 8, 9, 10, 2, 1, following the house style in its **report** register: it should read like a TI research report. No "we" or contractions, "per cent" in words, sources in numbered endnotes, an introduction that states the gap, the aim and a roadmap, and any recommendation as a named actor plus "should".
3. **Keep the trace.** Every statement about a source has its id and page. Every number is listed in `<study>/docs/archived/numbers.md` with the file it came from.
4. **Count, reconcile, then save** to `<study>/docs/proposal-vN.md` (see "Before saving, check" below). Count with `uv run python -I .claude/scripts/doc_length.py <file> --max 6500`; if it is over, cut the longest sections against their budgets before anything else. Run `/check-work` on it (methods, citations, numbers). It saves its findings beside the proposal as `<study>/docs/proposal-vN-review-<date>.md`; add to that file what was done about each. Fix what it finds.
5. **Hand over.** Export a Word version with the `docx` skill if she works in Word. Export from the saved `proposal-vN.md`, never from a working file in a scratchpad, and check the exported file itself: no build markers, every section present, the status note on the first page. Only the exported file is shared; name its path in the cover note. With it, send a half-page cover note: what this is, the decisions requested (section 9, by when each is needed), what happens after she replies, and that she may rewrite any part.
6. **Stop.** This is an approval point. Do not start the codebook.

## Before saving, check

- The main text is within the length budget (`.claude/scripts/doc_length.py` exits without complaint), and no section is more than half as long again as its budget.
- Every number in the text matches `numbers.md`, and numbers that should add up do (sample groups to the sample total; search counts from box to box; data counts before and after cleaning).
- The main text agrees with Annex A and with the technical requirements. Where they differ, fix one of them.
- Sections agree with each other: a rule stated in section 4 is not contradicted in section 6 or 9; a problem the data section says does not exist is not handled in a later section as if it did.
- Each dimension carries one meaning throughout, and the stated dependence between dimensions holds in every section.
- Every category has a breadth and a threshold; every hard case has a rule or a decision.
- Every design choice the method rests on is a numbered decision in section 9, placed in its time group.
- No recommendation rests on a source marked unread.
- **Every variant is carried through.** A narrower or broader version defined in section 4 has a stated role (headline, second version, robustness only) and appears in the method, the reporting order and section 9. A variant with no role is withdrawn or made a decision, not left defined.
- **Validation sets are disjoint and listed.** The pilot, the fixed test set, the hard cases and the expert sample are each given with size, how chosen, who labels it and what it is used for, and no case is in two of them unless the text says so and why.
- **Every threshold names its metric and its test.** For each accuracy threshold: which measure (defined in the text), on which set, and whether the point estimate or the lower bound of the interval must meet it; what happens when a measure has too few cases.
- **"N items" means N listed.** Wherever the text says "seven reasons", "four sets" or "nine attributes", all N are named in the text or a table, and the count matches the list.
- **Order of events holds.** Nothing is tested, piloted or judged against a rule that is defined or decided later. Each decision in section 9 is in the time group before the first step that depends on it (a threshold the pilot is judged against is a "before the pilot" decision).
- **Literature counts reconcile.** The counts in section 3 and Annex B (records, read, cited, by kind) add up from box to box and match `numbers.md`; works cited are counted the same way each time (say whether by record or by web address).
- **Each point is made once.** Search the draft for repeated sentences and repeated source citations across sections; keep the fullest one and point to it from the others.
- **The working file is not the deliverable.** No `{{`, `TODO`, `[[` or other build markers remain; every section in the outline is present in the saved file.
- **A status note opens the document**: version, date, what it is (draft for comments, for approval), and whether `/check-work` has run on it.

## When her reply comes back

She may approve, comment, or return a rewritten document. In each case:

1. Save what she sent, unchanged, as `<study>/docs/returned-vN.<ext>` and never edit it.
2. **Compare** it with the version she was sent, and list every difference in `<study>/docs/changes-vN.md`, in three groups:
   - **Substance:** a definition, category, scope, threshold, method step or claim changed. Each one is a decision.
   - **Style:** wording, order, tone. These go to `/house-style` as evidence of how she writes.
   - **Questions and comments** that need an answer.
3. **Check her changes like any other text.** If a rewritten sentence now states something the cited source does not support, or a number no longer matches its table, say so plainly and propose a fix. Do not silently correct her text and do not silently accept it.
4. **Record** each substance change and each answered decision in `<study>/docs/decisions.md` with the date and her name as approver.
5. **Carry the changes through:** update the technical requirements, and write the codebook (`/codebook`) from the approved definitions. If she changed a definition in a way the literature review does not cover, the codebook marks it as the study's own decision.
6. If open points remain, produce `proposal-vN+1.md` by copying the last version and editing the parts that change; do not write it out again in full. Then send it back. The approved version is copied to `<study>/docs/research-proposal.md`.

An outside review of the proposal is handled the same way: saved unchanged, each point answered in `changes-vN.md` as accepted (and where it is carried through), declined (and why), or put to her as a decision.

## Rules

- The proposal promises only what the technical requirements can deliver. If the two differ, fix one of them before sending.
- No results. The proposal is written before classification; it contains no counts of the categories being measured, and no organisation is named as belonging to a sensitive category.
- Recommendations are marked as recommendations. Where the literature gives no answer (for example, no source in the library defines "business"), say so and present the definition as the study's own proposal.
- Her wording of the research questions is kept unless she changes it.
- Definitions are frozen before the pilot, and only after the sources they rest on have been read.
