---
name: plan-study
description: Turn a research brief into a research plan and technical requirements, and get them approved before anything is built. Use at the start of a new study, when a brief or research question arrives, or when the researcher asks to plan, scope or revise the plan for a study.
---

# Plan a study

The brief says what the researcher wants to know. This skill turns it into what will be done and what will be built, and stops for approval.

## Steps

1. **Read the brief** in `<study>/docs/` (or as pasted). If there is none, ask for the research question in one or two sentences. If the study folder does not exist yet, create it from `templates/project-template/` as `.claude/docs/new-study-guide.md` describes, never by copying another study's folder.
2. **Restate each question so it can be measured.** For each: the unit counted, the population, the outcome, the comparison, and the output the researcher expects (a table, a ranking, a share).
3. **List the terms that need a definition** before anything can be counted (for example "business", "fossil-linked"). Note what the brief already says and what it leaves open. Open items become questions for the literature review, not questions for the researcher, unless only they can answer.
4. **Look at the data that exists.** For each dataset: where it came from, its size, and a first view of quality. If none is profiled yet, run `/profile-dataset` first or note it as a step.
5. **Write `<study>/docs/research-plan.md`**, two pages at most, in plain language:
   - the questions, as restated
   - definitions to settle, and where the answer will come from
   - data and its known limits
   - method in outline, and how accuracy will be measured: the sample groups and their sizes adding up to the total, the estimator named (for example weighted precision and recall, and how intervals are calculated), and a fixed test set of known cases for trying out the classifier, kept separate from the validation sample
   - how uncertainty will be reported, in three kinds kept apart: classification error, coverage (unknowns) and sampling
   - where a language model is used, what could go wrong, and the control for each
   - which model does each job and why (start from the table in `CLAUDE.md`), and which stages run in parallel. The researcher is never asked to choose a model.
   - what would change or weaken the conclusion
   - what is needed from people: who approves what, and how many hours of expert checking, worked out as records times minutes per record, to be measured in the pilot
6. **Write `<study>/docs/technical-requirements.md`**: numbered requirements grouped by stage, the research standard, the risk table, and the build steps each with a "done when". Start from the outline in `templates/project-template/docs/technical-requirements.md`. `unfccc/docs/technical-requirements.md` shows the level of detail to aim for; none of its definitions, thresholds, sample sizes or decisions carry over to another study.
7. **Ask for approval.** Summarise the plan in under 200 words and list the decisions you need. Do not build anything beyond data profiling until the plan is approved.
8. **Record the approval** and any changes in `<study>/docs/decisions.md` with the date.

## Standards the plan must meet

- Definitions, sample design and accuracy thresholds are fixed before results are seen.
- Every later claim will be traceable to a source or a generated table.
- Uncertainty and limitations are planned for, not added at the end.

## Revising

When the brief or a decision changes, update both documents, bump the status line, and log what changed and why in `decisions.md`. Do not keep a section describing the old plan.
