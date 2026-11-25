---
name: revise-report
description: Revise a draft report in response to independent review findings or the researcher's comments, keeping numbers and citations traceable. Use when the researcher asks to revise, edit, tighten, respond to comments on, or prepare a new version of a draft.
---

# Revise the report

## Steps

1. **Collect the comments:** the findings from `/check-work`, and anything the researcher or their colleagues wrote. If there has been no independent check of this version, run `/check-work` first.
2. **List them** in `<study>/report/revision-vN.md`, one row each: the comment, who raised it, how serious, and what you propose (fix, partly, decline with a reason).
3. **Ask the researcher** only about comments that change a finding, a definition or the tone toward a named organisation. Handle the rest yourself.
4. **Revise** into a new file, `draft-vN+1.md`. Never overwrite the previous version.
5. **If a number changes,** it changes in `outputs/` first, by re-running the analysis, and then in the text and in `numbers.md`. If a definition changes, that is a codebook change: stop and use `/codebook`.
6. **Re-run the checks** (numbers and citations) on the new version.
7. **Report:** what changed, what was declined and why, and what is still open.

## When the researcher returns a rewritten draft

Her version is the new base. Do not merge it back into ours.

1. Save what she sent, unchanged, as `<study>/report/returned-vN.<ext>`.
2. Compare it with the version she was sent and list the differences in `revision-vN.md` as substance (a finding, number, definition or claim about a named organisation changed), style, or question.
3. Re-run the number and citation checks on her text. Where a rewritten sentence no longer matches its table or its source, or states more than the validation supports, tell her plainly with the evidence and a proposed wording. Do not silently change her text and do not silently accept it.
4. Record her approval, and each substance change, in `<study>/docs/decisions.md`.
5. Pass the style differences to `/house-style`.
6. The report is final only when she has approved a version on which the number and citation checks pass and every named organisation is signed off.

## Editing standard

- Follow `.claude/docs/house-style.md`.
- Cut before adding. Remove repetition, hedging that adds no information, and claims the evidence does not carry.
- Keep each finding next to its uncertainty.
- Read it as the organisation being named would. Every statement about them must be supported by their evidence record and be fair in tone.
- Read it as a sceptical journalist would. Check that the headline claim survives the strictest definition in the sensitivity tables, or say that it does not.
