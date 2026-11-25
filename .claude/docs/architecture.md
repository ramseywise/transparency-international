# Architecture

What is in the workspace and what each part is for.

```
CLAUDE.md               the entry point: the rules for every task
<study>/                one folder per study (today: unfccc/)
literature/             the source library and its tools, shared by all studies
templates/              the clean starting point for a new study
mcp_server/             read-only access for clients other than Claude Code
.claude/                skills, agents, the raw-file safeguard, scripts/ (shared helpers such as
                        doc_length.py), skills/run-evals/ (tests of the assistant itself), and docs/: the assistant's own guidance (governance, evidence
                        standards, new-study guide, client setup, this file) and the house
                        style guide
README.md               the guide for researchers
pyproject.toml          the one Python project for the whole workspace
```

## Shared and study-specific

The line between the two is the most important thing in the layout.

| Shared: one copy, used by every study | Study-specific: lives in `<study>/` |
|---|---|
| `literature/` (library, ledger, reading records, tools) | the brief, plan, technical requirements, codebook |
| `.claude/skills/`, `.claude/agents/` | the decision log |
| `.claude/skills/run-evals/` | raw and derived data |
| `templates/` | code for this study's data |
| `mcp_server/` | outputs, proposal, report |
| `.claude/docs/` and `CLAUDE.md` | |

A change on the left affects every study: it needs tests and a logged reason (`CLAUDE.md` rule 14). Definitions, thresholds, classifications and conclusions live only on the right, and do not move between studies without review and approval (rule 13).

## A study folder

```
<study>/
  docs/         for the researcher and stakeholders: brief.md, technical-requirements.md,
                the current proposal, decisions.md, later codebook.md
  docs/archived/ working records: numbers.md (where each number comes from), cleaning-log.md,
                reviews/ (the record of each /check-work), old/ (superseded drafts)
  data/raw/     files as received; never edited
  data/processed/ tables built from the raw files by code
  src/  tests/  Python code specific to this study's data, and its checks
  notebooks/    worked analyses, run from top to bottom
  outputs/      generated tables and figures: the only source of reported numbers
  report/       the report, as sent and as returned
```

`docs/decisions.md` is the record of what is approved. Everything else in the folder may be a draft.

## The literature library

`literature/` holds the shared tools (`src/rag/`, `tests/`) and one library per study, for example `literature/unfccc/`. A library is that study's knowledge base: its screening decisions and topics are not inherited by another study (rule 13). Each library holds a ledger of every source considered (`ledger.jsonl`), the record of every download (`fetch-log.jsonl`), a reading record per source that was read (`records/`), and working reports in `data/private/reports/` (not in git). Downloaded files are in `data/raw/pdfs/<topic>/` and `data/raw/pages/<topic>/` (read-only; real files in one folder per topic of the study); what is made from them is in `data/processed/`, in the order it is made: `text/`, then `chunks/` (the text cut into passages), then `index/` (one vector per passage). Every source screened in is cut into passages and indexed, so all of it can be searched by keyword and by meaning; a reading record, with checked quotes and pages, is made only for a source that is cited. `data/private/reports/catalogue.md` lists every source screened in by topic and by read, to read or no file yet; `rag export` rebuilds it and moves each new download into its topic folder. Every path is defined once, in `literature/src/rag/paths.py`; `literature/README.md` has the layout and what is kept in git. The tools are run as `uv run python -I -m rag <command>`. Sources found in references become candidates; they are ranked and screened before anything is downloaded.

## The assistant's own parts

- **Skills** (`.claude/skills/`): the written steps for each stage, run as `/commands` in Claude Code.
- **Agents** (`.claude/agents/`): narrow workers with a fixed model: reading one source, researching one organisation, checking citations, recomputing numbers, reviewing methods.
- **Safeguard** (`.claude/hooks/protect_raw.py`): blocks any edit to an existing raw file or downloaded source.
- **Safeguard on the tests** (`.claude/hooks/protect_evals.py`): blocks an agent from editing the eval cases, the planted answers, the scorer or their fingerprints. It covers the editing tools, not shell commands, and does not stop reading.
- **Evals** (`.claude/skills/run-evals/`): cases with planted errors for each agent, a scorer, and checks that `CLAUDE.md`, the skills and the agents agree with each other.

These work in Claude Code only.

## The MCP server

`mcp_server/src/research_mcp/` has two files that matter:

- `workspace.py`: plain functions that read the workspace. The limits are here: only text documents in a study's `docs/`, `report/` and `outputs/` folders; never `data/`; nothing that writes.
- `server.py`: the seven tools a client sees, each marked read-only, and the short instructions sent to a client when it connects.

`.claude/docs/client-setup.md` says how to connect a client and what is deliberately left out.

## What is not here yet

- **Version control.** The workspace is a public git repository. What is published is Ramsey's decision. The literature library, with its downloaded files and search index, is in git (`literature/README.md`, "What is in git"); a study's `data/`, notebooks and outputs are not.
- **Tools that write through MCP.** Proposed, not built.
- **A `studies/` folder.** Studies sit at the top level. Moving them would change every path in the skills, tests and documents for no gain in function; it can be done later if the number of studies makes the top level crowded.
