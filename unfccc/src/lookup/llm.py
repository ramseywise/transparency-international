"""Calls to the language model: one at a time, or as a batch at half the price.

Everything about the model that a result has to record (which model, how many tokens,
what it cost) is collected here, so the run log and each record can say it (rule 11).
"""

from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AGENTS = ROOT / ".claude" / "agents"
MODEL_IDS = {"sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5", "opus": "claude-opus-5-5"}
# Dollars per million tokens: input, output, cache read, cache write (5-minute).
PRICES = {"claude-sonnet-5-5": (2.0, 10.0, 0.10, 2.5),
          "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
          "claude-opus-5-5": (4.0, 20.0, 0.40, 5.0)}
SEARCH_PRICE = 10.0 / 1000  # per web search
CHECKER = "claude-haiku-5-5"
MAX_CONTINUES = 5


def agent_model(agent: str) -> str:
    """The model an agent file pins, as a full model id: the script uses the same model."""
    text = (AGENTS / f"{agent}.md").read_text()
    m = re.search(r"^model:\s*(\S+)", text, flags=re.M)
    alias = m.group(1) if m else "sonnet"
    return MODEL_IDS.get(alias, alias)


@dataclass
class Usage:
    input: int = 0
    output: int = 0
    cache_read: int = 0
    cache_write: int = 0
    searches: int = 0
    calls: int = 0
    by_model: dict = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def add(self, model: str, u, batch: bool = False) -> None:
        if u is None:
            return
        vals = (getattr(u, "input_tokens", 0) or 0, getattr(u, "output_tokens", 0) or 0,
                getattr(u, "cache_read_input_tokens", 0) or 0,
                getattr(u, "cache_creation_input_tokens", 0) or 0)
        stu = getattr(u, "server_tool_use", None)
        n_search = (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
        with self._lock:
            self._add(model, vals, n_search, batch)

    def _add(self, model, vals, n_search, batch) -> None:
        self.input += vals[0]
        self.output += vals[1]
        self.cache_read += vals[2]
        self.cache_write += vals[3]
        self.searches += n_search
        self.calls += 1
        p = PRICES.get(model, PRICES["claude-sonnet-5-5"])
        dollars = sum(v * r for v, r in zip(vals, p, strict=True)) / 1e6 * (0.5 if batch else 1.0)
        dollars += n_search * SEARCH_PRICE
        self.by_model[model] = self.by_model.get(model, 0.0) + dollars

    @property
    def dollars(self) -> float:
        return round(sum(self.by_model.values()), 4)

    def as_dict(self) -> dict:
        return {"input_tokens": self.input, "output_tokens": self.output,
                "cache_read_tokens": self.cache_read, "cache_write_tokens": self.cache_write,
                "web_searches": self.searches, "calls": self.calls,
                "estimated_dollars": self.dollars}


def make_client():
    import anthropic

    return anthropic.Anthropic(max_retries=4)


def call(client, usage: Usage, **params):
    """One request, continued if the server pauses a long search turn. Returns the final
    message and every content block across the continuations, in order."""
    messages = list(params.pop("messages"))
    blocks: list = []
    for _ in range(MAX_CONTINUES):
        msg = client.messages.create(messages=messages, **params)
        usage.add(params["model"], msg.usage)
        blocks += list(msg.content)
        if msg.stop_reason != "pause_turn":
            return msg, blocks
        messages = messages + [{"role": "assistant", "content": msg.content}]
    return msg, blocks


def text_of(blocks) -> str:
    return "".join(getattr(b, "text", "") for b in blocks if getattr(b, "type", "") == "text")


def json_of(blocks) -> dict:
    """The JSON object in a reply. Structured output returns it as the whole text; otherwise
    the last fenced or bare object is taken."""
    text = text_of(blocks).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.findall(r"```(?:json)?\s*\n(.*?)\n```", text, flags=re.S)
    for cand in reversed(fenced):
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            continue
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start:end + 1])
    raise ValueError("The reply held no JSON object.")


def structured(schema: dict) -> dict:
    return {"format": {"type": "json_schema", "schema": schema}}


def cached_system(text: str) -> list[dict]:
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def run_batch(client, usage: Usage, requests: dict[str, dict], poll: float = 30.0,
              log=print) -> dict[str, object]:
    """Send `requests` ({custom_id: params}) as one batch at half price and wait for it.

    Returns {custom_id: message or None}. A batch can take up to a day; most finish
    within an hour. Searches cannot pause in a batch, so only steps without web search
    are sent this way (classification and the check)."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    reqs = [Request(custom_id=cid, params=MessageCreateParamsNonStreaming(**p))
            for cid, p in requests.items()]
    batch = client.messages.batches.create(requests=reqs)
    log(f"Batch {batch.id} sent with {len(reqs)} requests; waiting for it to finish.")
    while batch.processing_status != "ended":
        time.sleep(poll)
        batch = client.messages.batches.retrieve(batch.id)
    out: dict[str, object] = {cid: None for cid in requests}
    for r in client.messages.batches.results(batch.id):
        if r.result.type == "succeeded":
            msg = r.result.message
            usage.add(requests[r.custom_id]["model"], msg.usage, batch=True)
            out[r.custom_id] = msg
    return out
