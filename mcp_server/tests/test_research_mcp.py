"""The MCP server serves documents and sources, read-only, and never the data folder."""

import asyncio
import json
import re
from pathlib import Path

import pytest

from research_mcp import server
from research_mcp import workspace as ws

REPO = Path(__file__).resolve().parents[2]

DECISIONS = """# Decisions

| Date | Decision | Decided by |
|---|---|---|
| 2026-01-05 | The plan is approved. | Lead researcher |
| 2026-01-09 | Threshold for "high" set at 0.9 | with a note. | Lead researcher |

## Document status

| Document | Status | Version or date | Recorded in |
|---|---|---|---|
| `docs/plan.md` | approved | v1 | 2026-01-05 row |

## Open

- The codebook: not yet approved.

## Notes

- Not an open item.
"""


@pytest.fixture
def root(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Guide\nThe rules.\n")
    (tmp_path / ".claude" / "docs").mkdir(parents=True)
    (tmp_path / ".claude" / "docs" / "evidence-standards.md").write_text("# Evidence\n")
    study = tmp_path / "demo"
    (study / "docs").mkdir(parents=True)
    (study / "docs" / "decisions.md").write_text(DECISIONS)
    (study / "docs" / "plan.md").write_text(
        "# Plan\n\nThe sample is drawn by stratum.\n\nThe threshold is decided first.\n"
    )
    (study / "outputs").mkdir()
    (study / "outputs" / "table.csv").write_text("a,b\n1,2\n")
    (study / "outputs" / "delegates_all.csv").write_text("name\nA Person\n")
    (study / "data" / "raw").mkdir(parents=True)
    (study / "data" / "raw" / "list.csv").write_text("name\nA Person\n")
    (study / "src").mkdir()
    (study / "src" / "code.py").write_text("x = 1\n")
    lit = tmp_path / "literature" / "demo"
    (lit / "records").mkdir(parents=True)
    rows = [
        {"id": "read-2020", "title": "A read source", "year": 2020, "status": "in",
         "file": "pdfs/read-2020.pdf", "doi_or_url": "https://example.org/a"},
        {"id": "cand-2021", "title": "A candidate", "year": 2021, "status": "candidate",
         "doi_or_url": "https://example.org/b"},
    ]
    (lit / "ledger.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (lit / "records" / "read-2020.json").write_text(
        json.dumps({"id": "read-2020", "findings": [{"claim": "c", "quote": "q", "page": 3}]})
    )
    (tmp_path / "evals").mkdir()
    return tmp_path


def test_guide_is_served_and_names_the_other_documents(root):
    out = ws.operating_guide(root)
    assert out["text"].startswith("# Guide")
    assert out["other_documents"] == [".claude/docs/evidence-standards.md"]
    assert ws.operating_guide(root, ".claude/docs/evidence-standards.md")["text"] == "# Evidence\n"
    with pytest.raises(ws.NotAvailable):
        ws.operating_guide(root, "pyproject.toml")


def test_only_folders_with_a_decision_log_are_studies(root):
    assert [s["study"] for s in ws.list_studies(root)] == ["demo"]


def test_study_listing_leaves_out_data_code_and_files_named_for_delegates(root):
    listed = [d["document"] for d in ws.get_study(root, "demo")["documents"]]
    assert listed == ["docs/decisions.md", "docs/plan.md", "outputs/table.csv"]


@pytest.mark.parametrize("document", [
    "data/raw/list.csv", "src/code.py", "outputs/delegates_all.csv",
    "../CLAUDE.md", "docs/../data/raw/list.csv", "docs/missing.md",
])
def test_documents_outside_the_served_set_are_refused(root, document):
    with pytest.raises(ws.NotAvailable):
        ws.get_study(root, "demo", document)


def test_unknown_study_is_refused_with_the_known_names(root):
    with pytest.raises(ws.NotAvailable, match="demo"):
        ws.get_study(root, "literature")


def test_long_documents_come_in_pieces(root):
    first = ws.get_study(root, "demo", "docs/plan.md", max_chars=10)
    assert first["text"] == "# Plan\n\nTh" and first["next_offset"] == 10
    rest = ws.get_study(root, "demo", "docs/plan.md", offset=10)
    assert rest["next_offset"] is None
    assert first["text"] + rest["text"] == (root / "demo/docs/plan.md").read_text()


def test_decisions_are_parsed_with_open_items_kept_apart(root):
    out = ws.get_decisions(root, "demo")
    assert [d["date"] for d in out["decisions"]] == ["2026-01-05", "2026-01-09"]
    assert out["decisions"][1]["decision"].endswith("0.9 | with a note.")
    assert out["decisions"][1]["decided_by"] == "Lead researcher"
    assert out["open"] == ["The codebook: not yet approved."]
    only = ws.get_decisions(root, "demo", contains="codebook")
    assert only["decisions"] == [] and len(only["open"]) == 1


def test_search_finds_paragraphs_with_every_word_and_says_what_it_searched(root):
    out = ws.search_research(root, "threshold decided")
    assert [(r["document"], r["line"]) for r in out["results"]] == [("docs/plan.md", 5)]
    # A table row is matched on its own, not the whole decision log as one paragraph.
    row = ws.search_research(root, "threshold researcher")["results"]
    assert [(r["document"], r["line"]) for r in row] == [("docs/decisions.md", 6)]
    assert row[0]["text"].startswith("| 2026-01-09")
    empty = ws.search_research(root, "zebra")
    assert empty["results"] == [] and "demo/docs/plan.md" in empty["searched"]
    assert "does not show" in empty["note"]


def test_a_source_without_a_record_is_reported_as_not_read(root):
    read = ws.get_evidence(root, "read-2020")
    assert read["reading_record"]["findings"][0]["page"] == 3 and read["held"]
    candidate = ws.get_evidence(root, "cand-2021")
    assert candidate["reading_record"] is None and "not been read" in candidate["note"]
    with pytest.raises(ws.NotAvailable):
        ws.get_evidence(root, "nobody-1999")


def _write_index(root, ids, vectors=None, passages=None, built="2026-01-10"):
    import numpy as np
    import pandas as pd

    folder = root / "literature" / "demo" / "data" / "processed" / "index"
    chunks = folder.parent / "chunks"
    folder.mkdir(parents=True, exist_ok=True)
    chunks.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"source_id": ids, "text": ["t"] * len(ids)}).to_parquet(
        chunks / "passages.parquet"
    )
    np.save(folder / "vectors.npy", np.zeros((len(ids) if vectors is None else vectors, 4)))
    (folder / "meta.json").write_text(json.dumps({
        "built": built, "sources": len(set(ids)),
        "passages": len(ids) if passages is None else passages,
    }))


def _found(query, root, k, source):
    return [{"source_id": "read-2020", "loc": "p.3", "section": None, "text": "q",
             "keyword": 1.0, "meaning": 0.5}]


def test_literature_search_adds_titles_and_says_how_fresh_the_index_is(root, monkeypatch):
    from rag import index

    _write_index(root, ["read-2020", "read-2020"])
    monkeypatch.setattr(index, "search", _found)
    out = ws.search_literature(root, "anything")
    hit = out["results"][0]
    assert hit["title"] == "A read source" and hit["has_reading_record"]
    assert out["index"] == {"built": "2026-01-10", "sources": 1, "passages": 2}
    assert out["records_not_indexed"] == [] and "not in the index" not in out["note"]
    assert ws.get_evidence(root, "read-2020")["in_search_index"] is True


def test_a_read_source_missing_from_the_index_is_named(root, monkeypatch):
    from rag import index

    _write_index(root, ["other-2019"])
    monkeypatch.setattr(index, "search", _found)
    out = ws.search_literature(root, "anything")
    assert out["records_not_indexed"] == ["read-2020"]
    assert "not in the index" in out["note"]
    with pytest.raises(ws.NotAvailable, match="reading record but its text is not in"):
        ws.search_literature(root, "anything", source_id="read-2020")
    with pytest.raises(ws.NotAvailable, match="not held or not indexed"):
        ws.search_literature(root, "anything", source_id="cand-2021")
    with pytest.raises(ws.NotAvailable, match="No source with id"):
        ws.search_literature(root, "anything", source_id="nobody-1999")
    assert ws.get_evidence(root, "read-2020")["in_search_index"] is False


@pytest.mark.parametrize("setup", ["missing", "vectors", "meta", "unreadable", "raises"])
def test_a_missing_or_half_built_index_gives_a_plain_message(root, monkeypatch, setup):
    from rag import index

    if setup == "vectors":
        _write_index(root, ["read-2020", "read-2020"], vectors=1)
    elif setup == "meta":
        _write_index(root, ["read-2020"], passages=5)
    elif setup == "unreadable":
        _write_index(root, ["read-2020"])
        (root / "literature" / "demo" / "data" / "processed" / "chunks" / "passages.parquet").write_text("half written")
    elif setup == "raises":
        _write_index(root, ["read-2020"])

        def broken(query, root, k, source):
            raise ValueError("shapes (3,4) and (5,) not aligned")

        monkeypatch.setattr(index, "search", broken)
    with pytest.raises(ws.NotAvailable, match="missing, incomplete or being rebuilt") as e:
        ws.search_literature(root, "anything")
    assert "other tools still work" in str(e.value)
    # The other tools are not affected.
    assert ws.get_evidence(root, "read-2020")["reading_record"] is not None


def test_each_document_carries_its_status_from_the_decision_log(root):
    listed = {d["document"]: d["status"] for d in ws.get_study(root, "demo")["documents"]}
    assert listed == {
        "docs/decisions.md": "record", "docs/plan.md": "approved",
        "outputs/table.csv": "not recorded",
    }
    plan = ws.get_study(root, "demo", "docs/plan.md")["status"]
    assert plan == {"status": "approved", "version": "v1", "recorded": "2026-01-05 row"}
    table = ws.get_study(root, "demo", "outputs/table.csv")["status"]
    assert table["status"] == "not recorded" and "draft" in table["meaning"]
    hit = ws.search_research(root, "threshold decided")["results"][0]
    assert hit["document"] == "docs/plan.md" and hit["status"] == "approved"


def test_a_status_table_is_not_read_as_decisions_or_open_items(root):
    out = ws.get_decisions(root, "demo")
    assert len(out["decisions"]) == 2
    assert out["open"] == ["The codebook: not yet approved."]
    assert set(out["document_status"]) == {"docs/plan.md"}


def test_an_unknown_status_word_is_not_taken_as_a_status(root):
    log = root / "demo" / "docs" / "decisions.md"
    log.write_text(log.read_text().replace("| approved |", "| nearly approved |"))
    assert ws.get_study(root, "demo", "docs/plan.md")["status"]["status"] == "not recorded"


def test_nothing_in_the_module_writes(root):
    before = sorted((p, p.stat().st_mtime_ns) for p in root.rglob("*"))
    ws.operating_guide(root)
    ws.get_study(root, "demo")
    ws.get_study(root, "demo", "docs/plan.md")
    ws.get_decisions(root, "demo")
    ws.search_research(root, "sample")
    ws.get_evidence(root, "read-2020")
    assert sorted((p, p.stat().st_mtime_ns) for p in root.rglob("*")) == before


# ---- the server as a client sees it


def test_every_tool_is_marked_read_only_and_described():
    tools = asyncio.run(server.mcp.list_tools())
    assert {t.name for t in tools} == {
        "get_operating_guide", "list_studies", "get_study", "get_decisions",
        "search_research", "search_literature", "get_evidence",
    }
    for t in tools:
        assert t.annotations.read_only_hint is True, t.name
        assert t.annotations.destructive_hint is False, t.name
        assert t.description and len(t.description) > 40, t.name


def test_a_refusal_reaches_the_client_as_a_readable_message(root, monkeypatch):
    monkeypatch.setenv("TI_RESEARCH_ROOT", str(root))
    with pytest.raises(ws.ToolError, match="not a served document"):
        asyncio.run(server.mcp.call_tool(
            "get_study", {"study": "demo", "document": "data/raw/list.csv"}
        ))
    ok = asyncio.run(server.mcp.call_tool("list_studies", {}))
    assert ok.is_error is False and "demo" in str(ok.content)


# ---- against this workspace


def test_this_workspace_serves_its_guide_and_no_data_file():
    assert ws.operating_guide(REPO)["text"].startswith("# ")
    for study in ws.list_studies(REPO):
        for doc in ws.get_study(REPO, study["study"])["documents"]:
            first = doc["document"].split("/")[0]
            assert first in ws.SERVED_FOLDERS, doc
            assert not doc["document"].endswith(".parquet"), doc


def test_every_proposal_and_report_in_this_workspace_has_a_recorded_status():
    for study in ws.list_studies(REPO):
        for doc in ws.get_study(REPO, study["study"])["documents"]:
            name = doc["document"]
            if re.fullmatch(r"docs/proposal-v\d+\.md|report/report-v\d+\.md", name):
                assert doc["status"] != "not recorded", (study["study"], doc["document"])


def test_every_guide_document_named_by_the_server_exists():
    for name in ws.GUIDE_FILES:
        assert (REPO / name).is_file(), name


WORKFLOWS = REPO / ".claude" / "docs" / "research-workflows.md"


def test_the_server_points_the_client_to_the_workflow_guide():
    assert ".claude/docs/research-workflows.md" in ws.GUIDE_FILES
    assert "research-workflows.md" in server.INSTRUCTIONS
    assert "research-workflows.md" in ws.operating_guide(REPO)["note"]


def test_the_workflow_guide_covers_every_skill_and_names_only_real_ones():
    import re

    text = WORKFLOWS.read_text()
    skills = {p.name for p in (REPO / ".claude" / "skills").iterdir() if (p / "SKILL.md").is_file()}
    agents = {p.stem for p in (REPO / ".claude" / "agents").glob("*.md")}
    named_skills = set(re.findall(r"`/([a-z][a-z-]+)`", text))
    assert skills <= named_skills, sorted(skills - named_skills)
    assert named_skills <= skills, sorted(named_skills - skills)
    for name in set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", text)):
        if name.endswith(("-reviewer", "-checker", "-reader", "-finder", "-classifier", "-triage")):
            assert name in agents, name
