---
name: run-evals
description: Test the research assistant itself - give each agent a small case with planted errors and score what it catches, and check that the skills, agents and instructions still agree with each other. Use after any change to an agent file, a skill, a model, or the workspace instructions, or when someone asks whether the assistant can be trusted, how it is tested, or to run the evals.
---

# Run the evals

An eval is a test with a known answer. Each agent gets a small invented case in which errors were planted on purpose. The score is how many it catches and how many false alarms it raises. `.claude/skills/run-evals/reference/spec.md` explains each case and its limits.

## When

- After changing an agent file, a skill, a model, `CLAUDE.md`, a prompt in `unfccc/src/lookup/prompts/`, or the literature chunk selection. A model change is also logged in `<study>/docs/decisions.md`. `uv run python -I .claude/skills/run-evals/scripts/what_to_run.py` says whether anything has changed since the last tested run and which cases that touches; it costs nothing.
- Before the full classification run.
- When asked.

## Steps

1. **Checks that need no model.** Run `uv run pytest -q`. This covers the code, the scorer, the setup (skills, agents, instructions, the guards on raw files and on the test cases), the fingerprints of the cases and the scorer, the literature library and the figures written from it, and the endnotes of every proposal and report. Fix what fails before going on.
2. **Agent cases.** First run `uv run python -I .claude/skills/run-evals/scripts/what_to_run.py`: it compares the agents, skills, instructions and prompts with those of the last tested run and lists the cases the change affects, and whether three runs are needed. Run those cases (all of them if it says so, or when asked for a full run). Start them in parallel, in one message, each by its own type (`subagent_type` = the agent's name, so its model and tools come from its file). If the types are not available, stop and say so; never run a case as `general-purpose`. The cases:
   - `citation-checker` on `.claude/skills/run-evals/cases/citation-checker/document.md`, with `.claude/skills/run-evals/cases/citation-checker/library/` as its library
   - `numbers-checker` on `.claude/skills/run-evals/cases/numbers-checker/text.md`, with `.claude/skills/run-evals/cases/numbers-checker/study/` as the study folder
   - `source-reader` on `.claude/skills/run-evals/cases/source-reader/source.md`, and, as a separate agent, on `.claude/skills/run-evals/cases/source-reader-chunks/picks.json` (the chunk file) with `.claude/skills/run-evals/cases/source-reader-chunks/text.json` as the full text, told the key term is "industry-linked delegate"
   - `decision-triage` on `.claude/skills/run-evals/cases/decision-triage/questions.md`, with `.claude/skills/run-evals/cases/decision-triage/study/` as the study folder; it is asked to end its answer with a JSON block: `{"groups": {"Q1": "assistant", ...}, "for_researcher_now": [...], "next": [...], "already_decided": {"Q..": "<date> ..."}}`, each group one of assistant, researcher, ramsey, decided, or a list for a question that splits
   - `methods-reviewer` on `.claude/skills/run-evals/cases/methods-reviewer/design.md` (regression case), on `.claude/skills/run-evals/cases/methods-reviewer-proposal/design.md` (hard case: a full proposal) and on `.claude/skills/run-evals/cases/methods-reviewer-v1/design.md` (historical case: proposal v1 as sent). Each is a separate agent and is told only that the file is a research design or proposal to review.
   - `evidence-finder`, once per case in `.claude/skills/run-evals/cases/evidence-finder/expected.json` (give it only the name as written, the country and the other spellings, typed into the instruction), with `.claude/skills/run-evals/cases/evidence-finder/codebook.md` as the codebook
   - `org-classifier`, once per file in `.claude/skills/run-evals/cases/org-classifier/evidence/`, with `.claude/skills/run-evals/cases/org-classifier/codebook.md` as the codebook

   Each agent is told only its task and where its inputs are. It must not open any `expected.json`, `.claude/skills/run-evals/tests/`, `.claude/skills/run-evals/scripts/score.py` or `.claude/skills/run-evals/runs/`. Say so in the instruction.
   Run **three times** (E3) when `what_to_run` says so: a model change, a change to `CLAUDE.md` or to the cases, before the full classification run, or when asked. Otherwise run the affected cases once. Each run goes in its own folder: `.claude/skills/run-evals/runs/<date>/run1/`, `run2/`, `run3/`. Before each run write its run record: `uv run python -I .claude/skills/run-evals/scripts/score.py --record .claude/skills/run-evals/runs/<date>/runN "Claude Code"`. It notes the date, client, models and fingerprints of the instructions, cases and scorer (C10); a run whose instructions changed while it ran does not pass.
3. **Save the answers** in the run folder, named as the scorer expects: one file per agent as in earlier runs, one per case for the two organisation steps (`evidence-finder-O1.json`, `org-classifier-K1.json` and so on), and `methods-reviewer-proposal.md`, `methods-reviewer-v1.md` for the two further methods cases, `source-reader-chunks.json` for the chunk case, and for triage the full text as `decision-triage.md` and its JSON block as `decision-triage.json`. Never overwrite an earlier run; add a letter to the date if there are two in one day.
4. **Grade the methods reviews.** They are free text, so a second agent (sonnet) reads each review and the list of planted weaknesses (for v1: the outside reviewer's problems) and says which were raised, with an exact quote from the review for each. Save as `methods-reviewer-graded.json`, `methods-reviewer-proposal-graded.json`, `methods-reviewer-v1-graded.json`. The scorer accepts a "raised" only if the quote is really in the review.
5. **Score.** `uv run python -I .claude/skills/run-evals/scripts/score.py .claude/skills/run-evals/runs/<date>` scores each run and writes `repeats.json`. The scoring is by fixed rules in code.
6. **Mark what was tested.** When the runs are scored, run `uv run python -I .claude/skills/run-evals/scripts/what_to_run.py --save .claude/skills/run-evals/runs/<date>/run1`. The next check compares against this point. Do not save after a run that did not pass: the change stays untested. Then add one row for the run to `.claude/skills/run-evals/results.md`, in the form of the rows above it: that file is what is kept in git, since `runs/` is scratch and stays out of it.
7. **Report** in plain language, the headline first (E6): how many confident wrong answers (a false all-clear, a false alarm, a wrong label given with confidence), and the weighted misses (a required item counts three times). Then per agent: the model, what was found in every run, what only in some runs ("found in k of 3 runs"), what never, and any false alarm, compared with the previous run. Three runs show how stable an agent is on these cases; they are still not a measured error rate.

## Rules

- A failed case is a finding. Do not change the case or the scoring rule to make it pass. If the case itself is wrong, fix it, say so, and re-run every agent on it.
- The cases and the scorer are fingerprinted in `.claude/skills/run-evals/scripts/fingerprints.json`, and a test fails when one differs. A changed case is a new case: earlier results do not carry over to it. Re-fingerprint only on purpose, with the command in `.claude/skills/run-evals/reference/spec.md`, and log the reason. An agent cannot edit the cases, the planted answers, the scorer or the fingerprints; the guard `.claude/hooks/protect_evals.py` blocks it.
- Do not edit an agent file and test it on the same cases over and over until it passes: that fits the agent to the test. Change it for a stated reason, run once, report.
- These cases are invented. They show that an agent follows its rules; they do not show how accurate the study's classification is. That is measured by `/validate`.
