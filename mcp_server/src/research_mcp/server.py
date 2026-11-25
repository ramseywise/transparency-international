"""The MCP server: read-only tools over the research workspace.

Run with `uv run python -m research_mcp` from the workspace root. It speaks MCP
over stdio, so a client such as Claude Desktop starts it as a local program.
See .claude/docs/client-setup.md.
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from research_mcp import workspace as ws

INSTRUCTIONS = """\
Read-only access to a Transparency International research workspace: its studies, \
their decision logs, and each study's library of sources.

Before answering a research question, call get_operating_guide once and follow it. \
The rules that matter most here:
- Say for each statement whether it was retrieved from this workspace, checked \
against an outside source, or is your own assumption.
- A search that finds nothing does not show that something does not exist. Report \
what was searched.
- A document in a study may be a draft. Only docs/decisions.md says what is approved.
- Cite a source by its source_id and page or section, with the quote.
- This server cannot change anything. Creating a study or running a check is done \
in Claude Code, on the user's explicit request.

The researcher is an expert in the subject, not in software or AI. They will not \
name a workflow, a model or a check, and should not have to. Read \
.claude/docs/research-workflows.md (get_operating_guide with that name) and use it to:
- recognise what the request needs and say in one line which workflow and which \
checks it would take, and which of those cannot run here;
- call nothing checked that has not been through the checks it needs;
- before asking the researcher anything, sort the open questions: decide the \
technical ones yourself, send setup and access questions to Ramsey, and put to the \
researcher only the research ones, at most three, each with options and a \
recommendation.
"""

READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
)

mcp = MCPServer(name="ti-research", instructions=INSTRUCTIONS)


@mcp.resource(
    "research://guide",
    name="operating-guide",
    description="The workspace's standing rules (CLAUDE.md).",
    mime_type="text/markdown",
)
def guide_resource() -> str:
    return ws.operating_guide(ws.workspace_root())["text"]


@mcp.tool(annotations=READ_ONLY)
def get_operating_guide(document: str | None = None) -> dict:
    """Return the rules for working in this workspace. Call this first.

    Without arguments it returns CLAUDE.md and lists the detailed documents
    (research workflows, research governance, evidence standards, starting a new
    study, client setup, architecture). Pass one of those names as `document` to
    read it. Read `.claude/docs/research-workflows.md` before deciding what a
    request needs and before asking the researcher anything.
    """
    return ws.operating_guide(ws.workspace_root(), document)


@mcp.tool(annotations=READ_ONLY)
def list_studies() -> list[dict]:
    """List the studies in the workspace, with the number of readable documents in each."""
    return ws.list_studies(ws.workspace_root())


@mcp.tool(annotations=READ_ONLY)
def get_study(
    study: str, document: str | None = None, offset: int = 0, max_chars: int = ws.MAX_CHARS
) -> dict:
    """List a study's documents, or read one of them.

    `study` is a name from list_studies, for example "unfccc". Without `document`
    the answer lists what can be read (the brief, technical requirements, decision
    log, proposal drafts, report drafts, generated tables). With `document`, for
    example "docs/technical-requirements.md", it returns the text; long documents
    come in pieces, continue with `offset` set to the `next_offset` returned.
    The study's data folder is never served.
    """
    return ws.get_study(ws.workspace_root(), study, document, offset, max_chars)


@mcp.tool(annotations=READ_ONLY)
def get_decisions(study: str, contains: str | None = None) -> dict:
    """Return a study's decision log: dated decisions with who decided, and open items.

    Use this to find out whether a definition, threshold, document or method is
    approved. `contains` keeps only entries that mention that text.
    """
    return ws.get_decisions(ws.workspace_root(), study, contains)


@mcp.tool(annotations=READ_ONLY)
def search_research(query: str, study: str | None = None, limit: int = 10) -> dict:
    """Search the study documents (plans, proposals, logs, reports) for a few words.

    Finds paragraphs that contain every word of `query`, so use two or three
    distinctive words, not a sentence. Searches all studies unless `study` is given.
    For what published sources say, use search_literature instead.
    """
    return ws.search_research(ws.workspace_root(), query, study, limit)


@mcp.tool(annotations=READ_ONLY)
def search_literature(
    query: str, k: int = 8, source_id: str | None = None, library: str | None = None,
) -> dict:
    """Search the text of the sources in a study's library, by keyword and meaning.

    Each study has its own library; `library` is the study's name (for example
    "unfccc") and is needed only when there is more than one.

    Returns up to `k` passages (at most 25), each with its source_id, title, and page
    or section. `source_id` limits the search to one source. Follow up with
    get_evidence for the source's reading record.
    """
    return ws.search_literature(ws.workspace_root(), query, k, source_id, library)


@mcp.tool(annotations=READ_ONLY)
def get_evidence(source_id: str, library: str | None = None) -> dict:
    """Return one source: its ledger entry and, if it was read, its reading record.

    The reading record holds the source's definitions, indicators, findings and
    limitations, each with an exact quote and page. A source without a record was
    considered but not read and must not be cited as read.
    """
    return ws.get_evidence(ws.workspace_root(), source_id, library)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
