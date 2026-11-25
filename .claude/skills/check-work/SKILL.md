---
name: check-work
description: Independent review of a piece of research work - a plan, literature review, research proposal, codebook, classification, analysis or draft report - by reviewers who see only the output and its sources. Use before anything is called finished, or when the researcher asks to check, verify, review or double-check work.
---

# Check work

The reviewers must be independent. Give them the output and where its sources are. Do not give them your reasoning, your opinion of the work, or what you expect them to find.

## Which reviewers

| Output | Reviewers |
|---|---|
| Research plan, technical requirements, validation plan | `methods-reviewer` |
| Literature review | `citation-checker`, `methods-reviewer` |
| Research proposal | all three, in parallel. `methods-reviewer` also gets the technical requirements, to check that the two agree. `numbers-checker` also gets the proposal's list of numbers and their files, since there is no `outputs/` folder yet |
| Codebook | `methods-reviewer` |
| Classification records | `citation-checker` on a random sample of 30, or all if fewer |
| Tables, charts, notebooks | `numbers-checker` |
| Draft report | all three, in parallel |

## Steps

1. Work out which output is being checked and which reviewers apply. Check the saved file in the study folder (`<study>/docs/...`), never a working file from a scratchpad. If the output will be shared as an export (.docx, .pdf), confirm it was made from that same file. A finding about missing sections or leftover `{{` markers usually means the wrong file was read.
2. Start the reviewers in parallel, each by its own type (`subagent_type` = the agent's name, so its model and tools come from its file). Each gets: the file to review, the folders its sources are in, and nothing else. If the types are not available, stop and say so; a reviewer run as `general-purpose` is not the reviewer.
3. Collect the findings. Check each one yourself against the file before passing it on; drop any that are mistaken, and say that you did.
4. Report to the researcher, most serious first:
   - **Must fix:** a number that does not match, a citation that does not support the claim, a conclusion the method cannot carry
   - **Should fix**
   - **Minor**
   For each: where it is, what is wrong, and the proposed fix.
5. State what was not checked.
6. **Save the record.** Write the verified list to the study's working records as `<study>/docs/working/reviews/<output name>-review-<date>.md` (for example `<study>/docs/working/reviews/proposal-v1-review-2026-11-24.md`; for a report, the same folder): the date, the file checked, which reviewers ran with which model and on which files, the findings as reported to the researcher, the findings dropped and why, and what was not checked. This file is the record that the check ran; without it, the check did not happen.
7. Fix nothing until the researcher has seen the list, unless they asked for fixes in the same request.
8. If the findings raise questions that need a choice (which fix to make, whether a point matters), give them to the `decision-triage` agent before the researcher sees them, with the study folder. Fix the technical ones yourself and say so in one line; ask the researcher only the research ones, as `.claude/docs/research-workflows.md` section 3 sets out.

## Rules

- A review that finds nothing says what it checked, so "no problems" can be told apart from "did not look".
- You may not review your own output in place of the agents. Write it, then hand it over.
