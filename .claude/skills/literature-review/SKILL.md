---
name: literature-review
description: Write a literature review that compares how the indexed sources define, identify and measure a study's key terms, so that classification rules can be based on it. Use after sources have been found and read, or when the researcher asks what the literature says about a definition, a method or a question.
---

# Literature review

The review exists to answer the study's open questions about definitions and method. It is not a general summary of the field.

## Inputs

- the list of questions in `<study>/docs/technical-requirements.md` (or the research plan)
- reading records in `literature/<study>/records/`
- passage search (`uv run python -m rag search "<question>"`) for detail the records do not hold

If fewer than five sources are read, say so and offer `/find-sources` first.

## Steps

1. **One section per question.** For each:
   - a table with one row per source that addresses it: source, peer reviewed or not, what it says, quote, page
   - where the sources agree
   - where they differ, and why (different purpose, data, or politics)
   - what none of them covers
   - a recommendation for this study, with the reasoning, marked clearly as a recommendation
2. **Proxies.** For each category the study will classify, list the observable indicators the sources used to identify it (for example: listed on a named exit list; share of revenue from a named activity; industry code; membership of a named association). Note for each how easy it is to check from public information.
3. **Published lists and datasets** the sources rely on: who compiles them, how, how often, and whether they can be reused.
4. **Criticisms** of earlier studies of the same kind, and how this study will answer each.
5. **Write it** to `<study>/docs/literature-review.md`. Start with a half-page summary of the recommendations.
6. **Check it.** Give the draft to the `citation-checker` agent (`subagent_type: "citation-checker"`; if that type is not available, stop and say so). Fix every failure before showing the researcher.

## Rules

- Every statement about a source carries its id and page, and must be supported by the record or by a passage you retrieved. Nothing is cited from memory, and nothing is cited that is not in the ledger as `read`.
- Report disagreement between sources as disagreement. Do not average it away.
- Keep apart: what peer-reviewed work found, what advocacy reports claim, and what you recommend.
- Where the literature gives no answer, say so. The codebook will then record the rule as the study's own decision.
