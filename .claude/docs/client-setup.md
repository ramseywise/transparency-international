# Using the workspace from different clients

The workspace was built for Claude Code. It can also be read from Claude Desktop and other clients through a small MCP server. (MCP, the Model Context Protocol, is the standard way an assistant is given tools.) The clients are not equal, and an assistant should say which one it is in.

## What each client can do

| | Claude Code, opened in this folder | Claude Desktop or another client, through the MCP server |
|---|---|---|
| Loads `CLAUDE.md` by itself | yes | **no** |
| Skills (the `/commands`) and agents | yes | no |
| Safeguard that blocks edits to raw files | yes | not needed: nothing can be written |
| Runs Python, builds the index, downloads sources | yes | no |
| Reads study documents and decisions | yes | yes |
| Searches the source library | yes | yes, if the index has been built |
| Reads a study's `data/` folder | yes | **never** |
| Changes files | yes, on request | **no** |

So: Claude Code is for doing research (running a stage, starting a study). The MCP server is for asking questions of what is already there.

## The instructions do not travel by themselves

MCP gives a client tools. It does not make `CLAUDE.md` load as instructions. Three things cover the gap:

1. The server announces short instructions when a client connects, telling the assistant to read the guide first.
2. The tool `get_operating_guide` returns `CLAUDE.md`, and each of the documents in `.claude/docs/` on request. The same text is offered as the resource `research://guide`.
3. In Claude Desktop, create a project for this work and paste this as its instructions:

   > This project uses the ti-research tools. Before answering any research question, call get_operating_guide and follow it. Say for each statement whether it was retrieved from the workspace, checked against an outside source, or is your own assumption. A search that finds nothing does not show that something does not exist. You cannot change the workspace from here.

## Connecting Claude Desktop

The server runs on the same computer as the workspace. In Claude Desktop, open Settings, then Developer, then Edit Config, and add:

```json
{
  "mcpServers": {
    "ti-research": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/transparency-international", "python", "-m", "research_mcp"]
    }
  }
}
```

Replace the path with the real location of this folder. If Claude Desktop reports that it cannot find `uv`, replace `"uv"` with its full path (the output of `which uv` in a terminal). Restart Claude Desktop; the tools appear under the name ti-research.

To use it from Claude Code in another folder: `claude mcp add ti-research -- uv run --directory /absolute/path/to/transparency-international python -m research_mcp`.

## The tools

All seven only read. None can write, delete, download or run code.

| Tool | What it returns |
|---|---|
| `get_operating_guide` | `CLAUDE.md`, or one of the documents in `.claude/docs/`. Call it first. |
| `list_studies` | the studies in the workspace |
| `get_study` | the list of a study's documents, or the text of one (the brief, technical requirements, decision log, proposal, report, generated tables) |
| `get_decisions` | a study's decision log: dated decisions with who decided, and the open items |
| `search_research` | paragraphs in study documents that contain every word searched for |
| `search_literature` | passages from the sources in a study's library, with source id and page (takes the study's name once there is more than one library) |
| `get_evidence` | one source: its ledger entry and, if it was read, its reading record with quotes and pages |

Every search answer lists what was searched, so that an empty result is not read as "does not exist".

## What is deliberately left out

- **The `data/` folders.** They hold raw files and tables that name people. They are not served, and a file whose name starts with "delegates" is not served from any folder.
- **Code and notebooks.**
- **Tools that write.** Creating a study (`create_study`) and running a check (`run_research_check`) have been proposed and are not built. They would let a client change the workspace without the safeguards Claude Code has, so they need Ramsey's approval, a decision log entry, and explicit authorisation from the user on every call.
- **Access over the internet.** The server runs locally only. Reading the workspace from a hosted repository is a separate decision: it depends on version control being set up and on what may be published.

## Checking that it works

Two tests show the workspace is portable:

1. A fresh Claude Desktop session, with only the MCP server, answers questions about the COP31 study and says where each answer came from and what it could not check.
2. A separate Claude Code session creates a new study from the template without carrying over any definition, threshold or classification from the COP31 study.

For the first test, use the questions in `mcp_server/demo-questions.json`. Each has a known answer, what a good reply does, the documents it should cite and what it must not do; compare the Desktop replies with those (layer 2). That the server returns the text each answer rests on, and refuses the delegate data, is checked automatically (layer 1).

The server's own checks run with the rest: `uv run pytest -q`.
