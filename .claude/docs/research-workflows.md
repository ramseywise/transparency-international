# Research workflows: which steps and which checks

The researcher brings domain knowledge: corruption, lobbying, climate policy, what TI needs. They are not expected to know which skill, agent, model or check a request needs. That choice is the assistant's. This document is how it makes the choice, in Claude Code and in Claude Desktop through the MCP server.

Three steps for every request:

1. **Recognise the request** (table 1) and say in one line what you will do and which checks will run.
2. **Run the checks** that the request needs (table 2) before calling anything finished or trusted.
3. **Sort the open questions** before asking the researcher anything (section "Sorting questions before they reach the researcher").

## 1. From what the researcher asks to what runs

The researcher will not name a skill. Match on what they want, not on the words.

| The researcher wants to | Workflow in Claude Code | Checks before it counts as done | What only the researcher decides | In Claude Desktop (read-only) |
|---|---|---|---|---|
| know something about a study: its purpose, a definition, where it stands, what was decided | none: answer from the files | source check | nothing, unless the answer shows an open question | yes: `get_decisions` first, then `get_study` or `search_research` |
| know what the literature says | none: answer from the library | source check | nothing | yes: `search_literature`, then `get_evidence` for each source quoted |
| start a new study from a brief | `/plan-study` (template steps in `new-study-guide.md`) | design critic, then independent check | scope, research questions, the plan's approval | no: say it needs Claude Code; can read the template guide and draft questions |
| find, screen or read sources | `/find-sources`, with `source-reader` agents | source check on the reading records | screening criteria; the screened-in list; search scope (years, languages) | no; can report what the library already holds |
| compare how sources define the key terms | `/literature-review` | independent check (citations, methods) | which gaps matter for the study | can draft from `search_literature`, marked unchecked |
| derive or apply TI's writing style | `/house-style` | none beyond reading the sources | open style questions | can read `.claude/docs/house-style.md` |
| get the research proposal written, revised or taken back in | `/research-proposal` | design critic, then independent check (all three reviewers) | approval; every change of substance in a returned version | can read the draft and its status; cannot run the checks |
| fix the categories and rules for classifying | `/codebook` | design critic, then independent check | every definition, threshold and hard-case rule | can read and comment; cannot run the checks |
| describe or clean a dataset | `/profile-dataset`, `/clean-data` | numbers check | which records are in scope; any merge of names that a rule cannot settle | no: the data folder is never served |
| classify organisations | `/classify`, with `evidence-finder` then `org-classifier` | source check on a sample; repeat-run agreement | go or no-go after the pilot | no |
| know how accurate the classification is | `/validate` | numbers check | thresholds and the sample design, fixed before results are seen | no; can read the accuracy report once it exists |
| get the report drafted, revised or taken back in | `/draft-report`, `/revise-report` | independent check (all three reviewers); numbers check on every figure | approval; each organisation named as fossil-linked | can read drafts and their status |
| have any piece of work checked | `/check-work` | it is the check | which findings to act on | no: say the output stays unchecked |
| change how the assistant works (an agent, a skill, a model, the rules) | edit the file, then `/run-evals` | the eval run, three repeats | nothing; Ramsey approves changes to the shared setup | no |

If a request fits two rows, say so and take the earlier stage first (stages run in the order in `CLAUDE.md`). If it fits none, it is a question: answer it from the files, with the source check.

## 2. The checks

Each check is named in plain words so it can be named to the researcher the same way.

| Check | What it does | Who runs it | When it is required |
|---|---|---|---|
| **Source check** | Every factual statement points to a `source_id` or document with page or section and the quote; "nothing found" says what was searched | the assistant, re-opening each source it quotes (`get_evidence` over MCP) | every answer and every output |
| **Design critic** | A reviewer who has not seen the reasoning is asked only how the design fails: what it returns when it finds nothing, what happens when a step is confidently wrong (requirements W5) | a fresh reviewer given only the document; in Claude Code a separate agent; *the dedicated agent is not built yet*, so until then `methods-reviewer` is asked these two questions in addition to its own | before a plan, proposal or codebook goes for approval |
| **Independent check** | Reviewers see only the output and its sources, never the author's reasoning; the overall verdict follows from the findings | `/check-work`: `methods-reviewer`, `citation-checker`, `numbers-checker`, as its table says | before anything is called finished (`CLAUDE.md` rule 12) |
| **Numbers check** | Every figure is found in a generated file in `outputs/` and recomputed in Python | `numbers-checker`, and the automatic tests | any table, chart, proposal or report with numbers |
| **Decision sorting** | Open questions are sorted so the researcher sees only theirs, each with a recommendation | `decision-triage`, given the questions and the study's documents | before a list of questions goes to the researcher, and at the end of every stage |
| **Approval record** | The decision is written in `decisions.md` with the exact version, who, the date and any condition | the assistant, after the researcher answers | every approval; silence is not approval |
| **Eval run** | The agents are tested on cases with planted errors, three runs each | `/run-evals` | after any change to an agent, a skill, a model or `CLAUDE.md` |

A check that could not run is reported as not run, by name. An output with a check not run is called unchecked, not finished.

## 3. Sorting questions before they reach the researcher

Work produces questions. Most are about how to build things, and the researcher should not have to answer them. Before asking the researcher anything, sort every open question into one of three groups.

| Group | Examples | What happens |
|---|---|---|
| **The assistant decides** | which model or agent; file layout; how to run a search; which check to run; how to fix a failing test; the order of independent work | decided and recorded; mentioned to the researcher in one line at most, never asked |
| **The researcher decides** | a definition, category, threshold or hard case; scope (years, languages, countries); sample design; which evidence counts for which claim; what a finding means; naming an organisation; approving a document | asked, in the form below |
| **Ramsey decides** | anything that changes the shared setup, gives access to someone else, writes outside the agreed folder, or leaves this computer | sent to Ramsey, not to the researcher |

A question can be in the wrong group by its wording. "Should the search use a year limit?" is the researcher's (it changes what the study covers). "Should the search run in two batches?" is the assistant's. When a technical question hides a research choice (for example, a matching tolerance that decides which organisations count as the same), the research choice is put to the researcher in research terms, and the technical part is decided by the assistant.

**How a question is put to the researcher:**

- one question per item, in their terms, with no code, file names or agent names unless they need to open the file;
- the options (two or three), the recommendation and the reason for it in one or two sentences;
- what changes in the study depending on the answer, and what waits until it is answered;
- at most three at a time, the one blocking the most work first; the rest listed as "next" with no detail;
- where the literature or the study's own documents bear on it, the source, so the researcher can judge the recommendation rather than take it.

**Who does the sorting.** In Claude Code, the `decision-triage` agent: it is given the list of questions and the study folder, not the reasoning that produced them, and returns each question in its group with a recommendation. The main session checks the result, then asks the researcher. In Claude Desktop there are no agents: the assistant sorts the questions itself, in a separate pass after the work, and says that the sorting was not done by a separate reviewer.

## 4. In Claude Desktop

Through the MCP server the assistant can read and search, and nothing else. For every request:

- say at the start, once, what cannot be done here: no skills, no agents, no Python, no changes to files;
- for a request in table 1 that needs Claude Code, say which workflow it would be and which checks it would need, and offer what can be done here (reading, drafting from the files, preparing the questions for the researcher);
- run the source check on every answer: each statement marked as retrieved from the workspace, checked against an outside source, or an assumption;
- never present a draft made here as checked: the independent check, the design critic and the numbers check need Claude Code;
- before ending, sort any open questions (section 3) and give the researcher only theirs.

## 5. End of every stage

The report to the researcher has four parts, as `CLAUDE.md` asks: what was done, what was found, what is uncertain, what is needed from them. Add one line naming the checks that ran and the checks that did not. "What is needed from them" holds only questions from the researcher's group, sorted as in section 3.
