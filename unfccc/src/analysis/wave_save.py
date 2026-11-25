"""Save an agent's returned record to the wave folder, straight from the agent's transcript, so
that the record is stored exactly as returned and never retyped. Also reports the tokens the
agent used, for the usage check against batch_plan.TOKENS_PER_ORG.

Run from the workspace root:
    PYTHONPATH=unfccc/src uv run python -I -m analysis.wave_save <wave> <evidence|classified|run2>
        <case> <transcript.output> <model>
Prints one line: the path written, the record's status, and the tokens used. Nothing else.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

from analysis.wave_inputs import BASE

FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.S)


def final_text(lines: list[str]) -> str:
    """The agent's final report: the message of its last SubagentHandback call if it made one,
    otherwise the text of the last assistant message that has any text."""
    for line in reversed(lines):
        o = json.loads(line)
        m = o.get("message")
        if not isinstance(m, dict) or m.get("role") != "assistant":
            continue
        content = m.get("content", [])
        if not isinstance(content, list):
            continue
        for c in reversed(content):
            if (isinstance(c, dict) and c.get("type") == "tool_use"
                    and c.get("name") == "SubagentHandback"
                    and isinstance(c.get("input"), dict)):
                return str(c["input"].get("message", ""))
        texts = [c["text"] for c in content if isinstance(c, dict)
                 and c.get("type") == "text" and c.get("text", "").strip()]
        if texts:
            return texts[-1]
    raise ValueError("no text reply in the transcript")


def parse(text: str) -> dict:
    t = FENCE.sub("", text.strip())
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in the reply")
    return json.loads(t[start : end + 1])


REASONS = {
    "abstained": ("could be several entities", "nothing found"),
    "uncertain": ("match in doubt", "sources disagree"),
    "failed": ("search failed", "pages could not be reached"),
}
EVIDENCE_FIELDS = ("parent", "fossil_checks", "status_reason", "status_note", "pages_opened",
                   "activity", "fossil_search")   # the last two from wave 2 (decisions.md, 2026-11-25)
SEARCH_RESULTS = ("mention found", "no mention found")
CODE_SYSTEMS = ("NACE", "NAF", "ATECO", "WZ")


def check_evidence(rec: dict) -> list[str]:
    """Hold an evidence record to the format code relies on, whichever version of the agent's
    instructions produced it. Where `status_reason` starts with one of the fixed reasons and then
    explains, the reason is kept and the explanation moves to `status_note`, word for word.
    Nothing is invented: a reason that matches no fixed phrase is left as it is and flagged, and
    a missing field is flagged, not filled. Returns the flags, also stored in `save_checks`."""
    flags = [f"missing field: {f}" for f in EVIDENCE_FIELDS if f not in rec]
    fs = rec.get("fossil_search")
    if isinstance(fs, dict) and rec.get("status") in ("confident", "uncertain"):
        if not fs.get("queries"):
            flags.append("fossil_search: no queries recorded")
        if fs.get("result") not in SEARCH_RESULTS:
            flags.append("fossil_search: result not in the fixed list")
    code = (rec.get("activity") or {}).get("code") if isinstance(rec.get("activity"), dict) else None
    if isinstance(code, dict) and code.get("value"):    # from wave 2 (decisions.md, 2026-11-26)
        if code.get("system") not in CODE_SYSTEMS:
            flags.append("activity.code: system not in the fixed list")
        if not code.get("source_url"):
            flags.append("activity.code: no source page")
    status, reason = rec.get("status"), rec.get("status_reason")
    allowed = REASONS.get(status)
    if allowed is None:
        if reason:
            flags.append(f"status_reason given for status {status!r}")
    elif not isinstance(reason, str) or not reason.strip():
        flags.append("status_reason missing")
    else:
        low = reason.strip().lower()
        match = next((a for a in allowed if low.startswith(a)), None)
        if match is None:
            flags.append("status_reason not in the fixed list")
        elif low != match:
            rest = reason.strip()[len(match):].lstrip(" .;:,-\u2013\u2014").strip()
            rec["status_reason"] = match
            if rest:
                note = rec.get("status_note")
                rec["status_note"] = f"{rest} {note}".strip() if note else rest
            flags.append("status_reason split: explanation moved to status_note")
    rec["save_checks"] = flags
    return flags


KEYS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def tokens(lines: list[str]) -> dict[str, int]:
    """Two measures of usage. `context_at_end`: the last API reply's input (with cache) plus
    output, the figure the harness reports as the agent's tokens and the basis of the estimate
    of about 42,000 per organisation. `processed_incl_cache_reads`: every reply summed, each
    counted once (a reply split into several lines shares one message id); cached text is
    counted again on every turn, so this is much larger."""
    seen: dict[str, int] = {}
    last = 0
    for line in lines:
        m = json.loads(line).get("message")
        if not isinstance(m, dict) or m.get("role") != "assistant" or not m.get("usage"):
            continue
        u = m["usage"]
        last = sum(int(u.get(k) or 0) for k in KEYS)
        seen[m.get("id") or str(len(seen))] = last
    return {"context_at_end": last, "processed_incl_cache_reads": sum(seen.values())}


def save(wave: int, kind: str, case: str, transcript: Path, model: str) -> tuple[Path, dict, dict]:
    lines = transcript.read_text().splitlines()
    rec = parse(final_text(lines))
    if kind == "evidence":
        check_evidence(rec)
    inputs = {r["case"]: r for r in json.loads((BASE / f"wave{wave}" / "inputs.json").read_text())}
    rec.setdefault("org_id", case)
    rec["case"] = case
    rec["table_org_id"] = inputs[case]["org_id"] if case in inputs else None
    rec["model"] = model
    rec["run_date"] = dt.date.today().isoformat()
    rec["client"] = "Claude Code"
    used = tokens(lines)
    rec["tokens_used"] = used
    out = BASE / f"wave{wave}" / kind / f"{case}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    return out, rec, used


def main() -> None:
    wave, kind, case, transcript, model = sys.argv[1:6]
    out, rec, used = save(int(wave), kind, case, Path(transcript), model)
    flags = rec.get("save_checks") or []
    print(f"{out.relative_to(BASE)} status={rec.get('status') or rec.get('label')} "
          f"tokens={used['context_at_end']} (processed {used['processed_incl_cache_reads']})"
          + (f" checks: {'; '.join(flags)}" if flags else ""))


if __name__ == "__main__":
    main()
