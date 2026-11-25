# Starting a new study

A new study reuses the process, not the conclusions (`CLAUDE.md` rules 13 to 15). It starts from the template in `templates/project-template/`, never from another study's folder.

Starting a study changes files, so it is done in Claude Code on the user's explicit request. It cannot be done through the MCP server, which is read-only.

## What a new study may reuse

- the literature tools (`literature/src/rag/`). The new study gets its own, empty source library in `literature/<study>/`; another study's library, with its screening decisions and topics, is not inherited. A source wanted from another library is added and screened again for the new question;
- data-processing utilities that are already shared;
- the validation methods and the evaluation framework (`.claude/skills/run-evals/`);
- the skills, the agents and the document templates.

## What it must not inherit

Another study's definitions, thresholds, classifications, sampling decisions or conclusions. Any of these can be adopted, but only after the lead researcher has reviewed whether it applies to the new question and approved it, and the approval is in the new study's own decision log, naming where it came from.

Raw data and classifications are never copied from another study by default.

## Steps

1. **Agree the scope with the user.** The study's short name (lower case, one word, used as the folder name), its question, and who the lead researcher is.
2. **Create the folder from the template.** Copy `templates/project-template/` to `<study>/`. Copy nothing from another study's folder.
3. **Fill in the brief** (`<study>/docs/brief.md`) from what the researcher provides. Where the brief is silent, write "not yet decided". Do not fill the gap from another study.
4. **Start the decision log** (`<study>/docs/decisions.md`). The first row records that the study was created, from which template, on which date, at whose request.
5. **Register the data sources.** Each raw file goes in `<study>/data/raw/` with a note of where it came from and when. Once there it is never edited.
6. **Run `/plan-study`** to turn the brief into a research plan and technical requirements. Stop for approval.
7. **Continue through the stages** in `CLAUDE.md`, in order, stopping at each approval gate.

If the study needs its own Python code, it goes in `<study>/src/` with module names that start with the study's name, tests go in `<study>/tests/`, and the folder is added to the path lists in `pyproject.toml`. It does not copy the literature tools. Its library is started by `/find-sources`, which runs the tools with `--library <study>`.

## If a shared tool does not fit

Do not bend a shared tool, skill or template to solve one study's problem. First ask whether the change is useful to every study.

- If it is: make the change in the shared place, with tests and a logged reason.
- If it is not: put the code in the study's own folder.

## Checks before the first stage is called done

- The new folder holds no file copied from another study's `data/`, `outputs/`, `report/`, or its proposal and decisions in `docs/`.
- No definition or threshold in the new study's documents is there without a row in its own decision log.
- The brief, the plan and the technical requirements name this study's question and data, not another's.
