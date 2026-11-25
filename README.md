# Transparency International Research Assistant

A workspace for doing research with Claude: from a brief, through literature and data, to a report whose numbers and citations can all be traced.

It has three parts:

- **The assistant** (`.claude/`, `CLAUDE.md`): the instructions that tell Claude how to do each research step and which rules it may never break.
- **The studies** (`unfccc/`, and later others): one folder per study, holding everything needed to see how its results were made: the brief, the code, the data, the decisions and the outputs.
- **The shared library** (`literature/`, `.claude/docs/`): the sources and the writing guidance, which every study draws on.

## Two ways to use it

**1. Ask questions, from Claude.** This is how most researchers will use it. Someone sets up a connection for you once (the technical name is an MCP server), and after that you work in the Claude app as usual. You do not need this folder, GitHub or any command. You can ask, for example:

- "What has been decided about the definition of fossil-linked, and who decided it?"
- "What is still open in the UNFCCC study?"
- "Which of our sources say how to measure lobbying presence? Give me the quotes and page numbers."
- "Show me the current draft of the research proposal."

Through this connection Claude can read and search: a study's documents, its decision log, and the source library. It cannot change anything, and it cannot see a study's data folder (the participant lists name real people). When a search finds nothing, Claude should tell you where it looked; that is not the same as the information not existing. A document it shows you may be a draft: only what is in the study's decision log is approved.

**2. Run the research steps, in Claude Code.** Doing a stage of a study (the table below), or starting a new study, changes files and runs code, so it happens in Claude Code opened in this folder (`transparency-international/` itself, not a folder above it, or the commands and helpers are not found). Type a command, or just describe what you want. Claude does the technical work and stops to ask you at the points where your judgement is needed.

Whoever sets up the connection for you will find the steps in `.claude/docs/client-setup.md`.

| Step | Type | You get | You decide |
|---|---|---|---|
| 1 | `/plan-study` | A research plan and a list of what will be built | Whether the plan is right |
| 2 | `/find-sources` | A library of sources on the topic: pages and reports downloaded, the references inside them listed, each source read and searchable | What is in and out of scope, and which references are worth downloading |
| 3 | `/literature-review` | How the literature defines and measures your key terms | |
| 4 | `/house-style` | A short guide to how TI writes, taken from its own publications, so drafts read like yours | The open style questions |
| 5 | `/research-proposal` | **A research proposal**: the literature review and the proposed method, in one document | **Approve it, comment on it, or rewrite it.** Nothing is classified before this |
| 6 | `/codebook` | The rules for classifying, from the approved proposal | Whether the rules are right |
| 7 | `/profile-dataset`, `/clean-data` | A description of the data's quality, and clean tables (can run alongside steps 2 to 4) | |
| 8 | `/classify` | Each organisation labelled, with reasoning, a source link and a confidence level | Whether to go ahead after a small trial |
| 9 | `/validate` | A spreadsheet of sampled cases for you to check, then an accuracy report | The checking itself |
| 10 | `/draft-report`, `/revise-report` | **The report**: a draft, then a reviewed revision | Which organisations are named. **Approve it, comment on it, or rewrite it** |

At any point, `/check-work` asks reviewers that have not seen Claude's reasoning to check an output. This is an extra check. It does not replace review by an independent expert or peer review.

`/run-evals` tests the assistant itself, not the study: it gives each helper a made-up case with known errors hidden in it and counts how many it catches. See "How the assistant is tested" below.

If you rewrite the proposal or the report, send your version back as it is. Claude keeps it unchanged, works from your text, lists what you changed, and checks any new numbers and citations against the sources. If it finds a mismatch it tells you; it does not quietly change your wording.

## What to expect from the AI

- It will say "unknown" when it cannot find evidence. That is intended.
- Every label comes with a link you can open. If the link does not support the label, the label is wrong; tell Claude.
- A confidence level describes the evidence found, not how sure the model feels. The codebook says which kinds of evidence earn "high", "medium" or "low". Whether "high" really means "usually right" is a separate question, answered in step 9: accuracy is measured against your checks for each confidence level, with its margin of error. Until then the levels are unproven.
- Three kinds of uncertainty are reported separately and never merged into one figure: labels that are wrong, organisations that could not be labelled at all, and the margin of error that comes from checking a sample and not every case.
- You do not need to choose which AI model to use. Each job is given a model by what it needs: the strongest available for research design and critique, a standard one for reading sources and checking citations, and ordinary code with no AI for numbers. The model actually used, and the app it ran in, are recorded with every result so they can be reported in the methods section.
- "Not found" is not "no". Each case is recorded as positive, negative or unknown, with what was searched. An unsuccessful search gives unknown, never negative.
- Where tasks do not depend on each other, Claude runs several helpers at once (for example, reading many sources, or looking up many organisations) and tells you what is running. The steps above still happen in order, and it still waits for you at each decision.
- It can be wrong in ways that look convincing. The method is built around catching that, and your sample check is the part that cannot be automated.

## What is in this folder

```
CLAUDE.md        the assistant's standing rules
.claude/         the assistant's skills, helpers and safeguards, and its own guidance in docs/
                 (governance, evidence standards, starting a new study, setting up the
                 connection, and how TI writes)
unfccc/          a study (one folder per study): its code, data, documents and outputs
literature/      the source library and the tools that build it, shared across studies
templates/       the empty starting point for a new study
mcp_server/      the read-only connection that lets the Claude app read and search this workspace
.claude/skills/run-evals/           tests of the assistant itself: made-up cases with known errors, the scorer, saved results
pyproject.toml, uv.lock   the Python packages the code needs, and their exact versions
```

A study folder is self-contained on purpose. The code that collected, cleaned and classified its data sits beside that data, so anyone can see how each result was made, and a later study cannot change it by accident. Only the sources, the tools that collect them, and the style guide are shared, so a source is downloaded and read once.

### The assistant

`literature/README.md` lists what is in each folder, what is kept in git and how to rebuild the parts that can be rebuilt.

The library is built in separate stages, so that a problem can be traced to the stage that caused it: **finding** candidates (references inside sources, a catalogue search, a web search); **screening** each one in or out, with a reason; **downloading** only what was screened in and approved; **reading** each source into a record whose quotes are checked against the source text; and **comparing** the sources in the literature review. A candidate is never treated as a source until it has been screened and read. The tiers used to order the reading show how much attention a source has received, not how well it fits the question.

**`literature/src/rag/`: the literature tools.** Ordinary Python, with no AI in it. They belong to the library, not to any one study, so every study uses the same ones. Claude runs them for you.

| File | What it does |
|---|---|
| `fetch.py` | Downloads web pages and PDFs politely, once, and logs every download |
| `crawl.py` | Downloads the pages it is given and lists the links inside them as candidates. It does not wander |
| `extract.py` | Turns a page or PDF into text by section or page, and lists its references |
| `ledger.py` | Keeps the list of every source considered and its status: candidate, in, out, or read |
| `rank.py` | Sorts candidate sources into five tiers by how often our sources cite them and who published them |
| `screening.py` | Writes the screening decisions to one file a person can review |
| `index.py` | Builds the search index and answers searches by keyword and by meaning. It runs on this computer; nothing is sent anywhere |
| `openalex.py` | Searches OpenAlex, a public catalogue of academic work, for related papers and citation counts |
| `quotes.py` | Checks that every quote in a reading record really is in the source |
| `cli.py` | The commands that run the above |

### House style: `.claude/docs/`

`house-style.md` describes how TI writes, derived from its own publications in the library. Proposals and reports are drafted against it.

### A study folder

Everything that belongs to one study. `unfccc/` is the first.

```
<study>/
  docs/        the brief, research plan, technical requirements, codebook,
               the cleaning log, and decisions.md (every approval, dated)
  src/         the Python code (described below)
  tests/       checks that the code in src/ does what it says
  data/        raw files as downloaded in data/raw/ (never edited); cleaned tables in data/derived/
  notebooks/   data profiles and analysis
  outputs/     generated tables and charts; every number in a text comes from here
  report/      report drafts, what the lead researcher sent back, the changes
```

Folders appear as the study reaches each stage.

### The code: `unfccc/src/`

Ordinary Python, with no AI in it. It does the jobs that must give the same answer every time. Claude runs it for you.

**`cleaning/`: cleaning the participant list**

| File | What it does |
|---|---|
| `clean.py` | The cleaning step for this study, and its helpers. Tidies text, recognises placeholder values such as "n/a", loads spreadsheet sheets, and gives every row a stable identifier. Cleaned values go beside the original, never over it |
| `orgs.py` | Works out which spellings are the same organisation. It prefers leaving one organisation as two over wrongly merging two into one |

**`analysis/`: validation statistics**

| File | What it does |
|---|---|
| `sampling.py` | Draws the sample of cases for the expert to check, and says how precise the result will be |
| `stats.py` | Measures the classifier's accuracy from the checked sample, with margins of error |

**`charts.py`**: one look for every chart: fixed colours that survive colour-blindness and black-and-white printing, a title that states the finding, and a table of the plotted numbers saved beside each chart.

**Running the cleaning step**: `uv run python -m cleaning.clean` cleans the participant list, builds the organisation table and writes the cleaning log. `uv run python -m cleaning.clean csv` copies the raw workbook into one viewable table.

**`unfccc/tests/`**: one file of checks per module above. They are run after any change to the code, together with the checks in `literature/tests/`.

## How a result can be traced

Every result is meant to be followed back, step by step, to what it rests on:

- a **statement about the literature** to a source, a page and an exact quote, which a check finds in the source text;
- a **label** to the codebook rule applied, the page used, the quote and the date it was retrieved;
- a **number** in a text to a generated table in `outputs/`, and from there to the code and data that produced it;
- a **definition or design choice** to a dated approval in the study's `decisions.md`.

## How the assistant is tested: `.claude/skills/run-evals/`

The study's accuracy is measured by your sample check in step 9. Separately, `.claude/skills/run-evals/` tests whether the assistant's own parts do their jobs. `.claude/skills/run-evals/reference/spec.md` has the detail.

- **The six helpers** each get a made-up case with errors hidden in it: for example, a text of ten statements of which six are wrong in a known way, or a study design with seven planted weaknesses. The cases are invented, so no answer can come from what a model already knows, and the helper never sees the list of errors. A fixed scorer, with no AI in it, counts what was caught and what was wrongly flagged.
- **The setup** is checked for consistency: every helper has a model and it matches the rules, no instruction names a file or helper that does not exist, and the safeguard on raw files really blocks a change.
- **The tests themselves are protected.** Every test case and the scorer has a fingerprint (a short code computed from the file's contents). A check fails if any of them has changed, and a helper is blocked from editing them. A changed case counts as a new case.
- **Some rules are checked by machine, not left to instructions:** the literature counts written in a study's numbers file must equal what the library gives, and a draft may cite only sources that were actually read.
- **The library and the documents** are checked: every quote in every reading record is found in its source on the stated page, and a draft cites only sources that were actually read.
- **The code** has its own checks.

In the first run (24 November 2026, one run per helper) every helper passed its case. `/run-evals` is run again after any change to a helper, a skill or a model; `uv run python -I .claude/skills/run-evals/scripts/what_to_run.py` says which cases a change needs, at no cost. `.claude/scripts/doc_length.py` counts a document's words against its budget. A result has three possible states: passed, failed, or not run. A helper that was not run in a given test run is recorded as "not run", never as passed.

## Running the helpers, and what it costs

Each helper runs on a fixed model, set in its file in `.claude/agents/`. Most run on Sonnet. The methods reviewer and the question sorter (`decision-triage`) run on Opus, because their work depends on judgement. Cleaning, matching names and the statistics are ordinary code with no AI in them, so they cost nothing to run, however often.

The figures below are what each task cost when it was done in this project, priced at the public per-token rates for the helper's own model: Sonnet 5.5 at $2 per million tokens read and $10 per million written, Opus 5.5 at $4 and $20. They were measured on 24 November 2026 from the records of each helper's run. On a Claude subscription nothing is charged per task; the run counts towards the plan's usage limit instead.

| Task | Helper (model) | Cost each time | Example |
|---|---|---|---|
| **New data into the pipeline** | | | |
| Profiling and cleaning a dataset | code, no AI | nothing | |
| Looking up organisations in public sources | `evidence-finder` (Sonnet) | about $0.09 per organisation when given four at a time; about $0.20–$0.25 when given one at a time | |
| Classifying organisations against the codebook | `org-classifier` (Sonnet) | about $0.03–$0.04 per organisation, in batches of 10 | |
| Checking matched organisation names in public sources | Sonnet | about $0.55 per set of pairs | |
| Full classification of about 1,250 organisations | both of the above | | about $150 in batches; the second, independent classification for the agreement check reuses the evidence and adds about $40 |
| A pilot of 20–50 organisations | both of the above | | about $3–$6 |
| The same look-ups run by the script (`python -m lookup`) | Sonnet, checked by Haiku | estimated $0.11 to look up, $0.01 to classify ($0.005 as a batch), under $0.001 to check, per organisation | estimated, not yet measured; about $150 for all 1,250. Each step prints its own estimate first |
| **Literature** | | | |
| Reading one source into a reading record | `source-reader` (Sonnet) | usually $0.15–$0.90, typically $0.35; a long book up to $2.60 | 100 new sources: about $35–$50 |
| Screening a batch of search results | Sonnet | $0.20–$1.00 per batch | |
| Checking a set of reading records against their sources | Sonnet | $1.50–$2.00 | |
| **Checks (`/check-work`)** | | | |
| Citation check of a proposal | `citation-checker` (Sonnet) | about $1.00–$1.20 | |
| Numbers check of a proposal | `numbers-checker` (Sonnet) | about $0.60–$0.80 | |
| Methods review of a proposal | `methods-reviewer` (Opus) | about $1.60 | all three on a proposal: about $3–$4 |
| **Analysis and writing** | | | |
| Writing the code for a cleaning, statistics or chart step | Sonnet | about $0.70–$1.10, once | running it afterwards costs nothing |
| A house-style draft of a text | Sonnet | about $1.40 | |
| **Testing the assistant (`/run-evals`)** | | | |
| One helper on one test case, with its scorer | Sonnet or Opus | $0.30–$1.10 | one full test run: about $5–$8; three runs: $15–$25 |

What these figures leave out:

- **The session that directs the helpers costs extra.** You talk to a main session, which plans the work, starts the helpers and checks what they return. Its cost depends on the model chosen for it and on how long the conversation runs, and it can be larger than the helpers' cost. Choosing a smaller model for that session lowers it.
- **Every helper pays a fixed amount to start.** Each one begins by loading about 35,000 tokens of instructions and tool descriptions, about $0.14 on Sonnet, before it does any work. That is why small tasks given one at a time cost more per item than the same tasks given in batches.
- **They come from one study.** Longer sources, more organisations or harder cases cost more. Treat them as an order of magnitude, not a quote.
- **Prices change.** Check the current rates before using these figures in a budget.

What keeps the cost down: looking organisations up with the script rather than the helpers (it pays no start-up cost per batch, and code does the checks a helper would be paid to do), letting a source-reader start from the chosen passages (`rag chunks`), keeping documents to their length budget (written text costs five times what is read), running one session at a time rather than several in parallel, giving helpers work in batches (ten organisations at once, not one), running a pilot before a full classification, and leaving cleaning, matching and statistics to code, which costs nothing to rerun.

## What is not yet shown

- **The classification has not been run.** No figure for its accuracy exists yet. That comes from the expert sample in step 9.
- **One test run per helper.** A model can answer differently a second time, so one pass is one observation, not a rate.
- **The test cases are small and invented.** Real texts are longer and their errors less tidy.
- **The methods review is graded by a second AI model**, because it is free text.
- **The steps are not replayed from start to finish as a test.** Their parts are tested, and their outputs go through `/check-work`.
- **The workspace has been used on one study.** Whether it serves a different kind of study as well is untested.
- **The connection from the Claude app has not been tried by a researcher.** It is built and its checks pass on this computer. Two trials are proposed: a fresh session in the Claude app answering questions about the study, and a separate Claude Code session starting a new study from the template.
- **The connection works only on a computer that holds this folder.** Access for colleagues elsewhere depends on decisions not yet taken: version control, and what may leave this computer.
- **The literature search for the first study is unfinished**; its search log lists what is still to do.

Planned changes that address these points are listed in section 10 of `unfccc/docs/technical-requirements.md`, each with a requirement number. Section 10 was approved on 24 November 2026, except E10 (version control); most of it is not built yet. Section 11 covers the connection and the rules for working across studies: what is built, and what is proposed and not approved. Among the section 10 changes: three runs per test case (E3), a test study taken through every step with one error planted per step (E7), a past real proposal with known problems as a test case (E8), tests that a helper cannot alter (E4), and rules that a machine can check moved from written instructions into automatic checks (E9).

## Studies

Each top-level folder holds its own code beside what that code produces: the literature tools in `literature/src/`, a study's cleaning and analysis in `<study>/src/`. A new study gets its own folder with the same layout, started from the empty template in `templates/project-template/` and never by copying another study's folder. It uses the literature tools as they are. It may reuse the process; it does not inherit another study's definitions, thresholds, classifications or conclusions unless they are reviewed and approved for it.

- `unfccc/`: business and fossil fuel presence in country delegations at COP31. Start with `unfccc/docs/technical-requirements.md`. Status on 24 November 2026: the data are cleaned, the literature search is part done, and a second draft of the research proposal is being prepared for the lead researcher. No codebook has been written and nothing has been classified.
