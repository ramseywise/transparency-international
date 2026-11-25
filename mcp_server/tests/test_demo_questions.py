"""The demonstration questions (S17) have answers the server really gives.

Layer 1 of the demo set: each question names the tool calls that hold its answer. Each call
goes through the server as a client would make it, against this workspace, and the reply
must contain the stated text, or be a refusal when the request is restricted. Layer 2 (the
answer a researcher gets) is judged by a person; here only its fields are checked to exist.
"""

import asyncio
import contextlib
import json
from pathlib import Path

import pytest

from research_mcp import server
from research_mcp import workspace as ws

REPO = Path(__file__).resolve().parents[2]
QUESTIONS = json.loads((REPO / "mcp_server" / "demo-questions.json").read_text())["questions"]
KINDS = {"answerable", "partial", "not recorded", "restricted", "research required"}
CHECKS = [(q["id"], i, c) for q in QUESTIONS for i, c in enumerate(q["checks"], 1)]


def test_the_set_covers_every_kind_of_question():
    kinds = [q["kind"] for q in QUESTIONS]
    assert 12 <= len(QUESTIONS) <= 15
    assert set(kinds) == KINDS
    assert any("delegate" in q["question"].lower() for q in QUESTIONS if q["kind"] == "restricted")
    assert len({q["id"] for q in QUESTIONS}) == len(QUESTIONS)


@pytest.mark.parametrize("q", QUESTIONS, ids=[q["id"] for q in QUESTIONS])
def test_each_question_states_what_a_good_answer_does(q):
    assert q["answer"] and q["must"] and q["cite"] and q["must_not"] and q["checks"]
    if q["kind"] == "restricted":
        assert all("refused" in c for c in q["checks"])


@pytest.mark.parametrize("check", [c for _, _, c in CHECKS], ids=[f"{q}-{i}" for q, i, _ in CHECKS])
def test_each_check_gets_its_known_answer_from_the_server(check, monkeypatch):
    monkeypatch.setenv("TI_RESEARCH_ROOT", str(REPO))
    if "refused" in check:
        with pytest.raises(ws.ToolError, match=check["refused"]):
            asyncio.run(server.mcp.call_tool(check["tool"], check["args"]))
        return
    out = asyncio.run(server.mcp.call_tool(check["tool"], check["args"]))
    assert out.is_error is False
    raw = "".join(getattr(c, "text", "") for c in out.content)
    # replies are indented JSON; compare against the compact form as well as the raw text
    with contextlib.suppress(ValueError):
        raw += json.dumps(json.loads(raw), separators=(",", ":"), ensure_ascii=False)
    assert check["contains"] in raw
