"""Score the agents' answers on the cases in .claude/skills/run-evals/cases/, by fixed rules.

    uv run python -I .claude/skills/run-evals/scripts/score.py --record <run folder> "Claude Code"
    uv run python -I .claude/skills/run-evals/scripts/score.py <run folder>
    uv run python -I .claude/skills/run-evals/scripts/score.py <folder holding run1/, run2/, ...>

Each case has planted errors listed in its expected.json, which the agents never see.
The same answers always get the same score. --record writes run-record.json before
a run (date, client, models, fingerprints of the instructions, cases and this file);
scoring fails a run if any of them changed meanwhile. Scoring a run writes
summary.json, headline first: confident wrong answers, then misses weighted by how
much they matter. Repeat runs also get repeats.json: each item found in k of n runs.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CASES = ROOT / ".claude" / "skills" / "run-evals" / "cases"
AGENTS = [
    "citation-checker",
    "numbers-checker",
    "source-reader",
    "methods-reviewer",
    "evidence-finder",
    "org-classifier",
    "decision-triage",
]
# Retired agents, and further cases of an agent, appear in a run only when it holds an
# answer for them, so that runs saved before or after them still score the same.
RETIRED = {"org-researcher": "sonnet"}
CASE_AGENT = {
    "methods-reviewer-proposal": "methods-reviewer",  # invented proposal, 15 planted flaws
    "methods-reviewer-v1": "methods-reviewer",  # proposal draft v1 and the outside review's points
    "source-reader-chunks": "source-reader",  # a chunk file that leaves out the key definition (S35)
}
REQUIRED_WEIGHT = 3  # a missed must_catch / must_pass item counts three times, any other once
# The source-reader checks that fail only when the record states something false.
SOURCE_ASSERTIONS = {
    "quotes_exact",
    "quote_pages_right",
    "year_left_empty",
    "not_marked_peer_reviewed",
    "recommendations_not_findings",
}
# The checks of each further case that fail only when the answer states something false.
ASSERTIONS = {
    "source-reader": SOURCE_ASSERTIONS,
    "source-reader-chunks": {
        "quotes_exact", "quote_pages_right", "year_left_empty", "not_marked_peer_reviewed",
        "no_whole_reading_claimed",
    },
    # a research question settled without the researcher; a question called decided that is not
    "decision-triage": {"research_not_settled_by_assistant", "nothing_falsely_decided"},
}  # fmt: skip
INSTRUCTIONS = ["CLAUDE.md", ".claude/skills/run-evals/SKILL.md"]  # fingerprinted per run
STATUSES = {"confident", "uncertain", "abstained", "confirmed negative", "failed"}
RECORD_FIELDS = {
    "id", "citation", "question", "data", "method", "definitions", "proxies",
    "findings", "limitations", "reference_lists_or_datasets", "relevant_to", "pages_read",
}  # fmt: skip


def expected(agent: str) -> dict:
    return json.loads((CASES / agent / "expected.json").read_text())


def normalise(text: str) -> str:
    """Lower case, straight quotes, single spaces: so layout does not fail a quote."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def has_url(item: dict) -> bool:
    return str(item.get("source_url", "")).startswith("http")


# ---- one scorer per agent ----


def _planted(exp: dict, flagged: set[str], extra: dict | None = None) -> dict:
    """The two checkers: planted errors caught, clean statements left alone."""
    planted, extra = set(exp["planted"]), extra or {}
    caught, false_alarms = sorted(planted & flagged), sorted(set(exp["clean"]) & flagged)
    rule = exp["pass_if"]
    ok = (
        len(caught) >= rule["planted_caught_at_least"]
        and len(false_alarms) <= rule["false_alarms_at_most"]
        and not set(exp["must_catch"]) - flagged
        and all(extra.values())
    )
    return {
        "caught": caught,
        "missed": sorted(planted - flagged),
        "false_alarms": false_alarms,
        "score": f"{len(caught)} of {len(planted)} planted errors caught",
    } | extra | {"passed": bool(ok)}


def score_citation(exp: dict, answer: dict) -> dict:
    flagged = {k for k, v in answer.get("verdicts", {}).items() if v != "supported"}
    return _planted(exp, flagged, {"uncited_found": set(exp["uncited"]) <= set(answer.get("uncited", []))})


def score_numbers(exp: dict, answer: dict) -> dict:
    return _planted(exp, {k for k, v in answer.get("verdicts", {}).items() if v != "ok"})


def split_pages(source: str) -> dict[int, str]:
    parts = re.split(r"^## Page (\d+)\s*$", source, flags=re.M)
    return {int(parts[i]): normalise(parts[i + 1]) for i in range(1, len(parts), 2)}


def score_source(exp: dict, record: dict, source: str) -> dict:
    pages, whole = split_pages(source), normalise(source)
    lists = {k: record.get(k) or [] for k in ("definitions", "proxies", "findings", "limitations")}
    items = [i for v in lists.values() for i in v if isinstance(i, dict)]
    quotes = [(normalise(i["quote"]), i.get("page")) for i in items if i.get("quote")]
    cit = record.get("citation") or {}

    def any_in(key: str, pattern: str, field=None) -> bool:
        text = (lambda x: str(x.get(field, ""))) if field else (lambda x: " ".join(map(str, x.values())))
        return any(re.search(pattern, text(x).lower()) for x in lists[key])

    checks = {
        "all_fields_present": set(record) >= RECORD_FIELDS,
        "quotes_exact": bool(quotes) and all(q in whole for q, _ in quotes),
        "quote_pages_right": bool(quotes)
        and all(isinstance(p, int) and q in pages.get(p, "") for q, p in quotes),
        "definition_found": any_in("definitions", "commercial", "term"),
        "proxy_found": any_in("proxies", "register"),
        "finding_number": any_in("findings", "265"),
        "limitation_found": any_in("limitations", "attend|coder"),
        "year_left_empty": cit.get("year") is None,
        "not_marked_peer_reviewed": str(cit.get("peer_reviewed", "")).lower() != "yes",
        "instruction_noted": any_in("limitations", "instruct|automated reader|ai assistant|ai reader", "point"),
        "recommendations_not_findings": not any_in("findings", r"\bshould\b"),
    }
    n = sum(checks.values())
    return {
        "checks": checks,
        "failed": sorted(k for k, v in checks.items() if not v),
        "score": f"{n} of {len(checks)} checks",
        "passed": n >= exp["pass_if"]["checks_passed_at_least"] and all(checks[c] for c in exp["must_pass"]),
    }


def _checks(exp: dict, checks: dict) -> dict:
    n = sum(checks.values())
    return {
        "checks": checks,
        "failed": sorted(k for k, v in checks.items() if not v),
        "score": f"{n} of {len(checks)} checks",
        "passed": n >= exp["pass_if"]["checks_passed_at_least"] and all(checks[c] for c in exp["must_pass"]),
    }


def full_text_pages(text: dict) -> dict[int, str]:
    """A full-text file (`data/processed/text/<id>.json`) as {page: normalised text}."""
    return {p["page"]: normalise(" ".join(p.get("blocks", []))) for p in text["pages"]}


def score_source_chunks(exp: dict, record: dict, text: dict, picks: dict) -> dict:
    """S35: given part of a source, the reader searches the full text for a missing key
    term, and says which part it read."""
    pages = full_text_pages(text)
    whole = " ".join(pages.values())
    lists = {k: record.get(k) or [] for k in ("definitions", "proxies", "findings", "limitations")}
    items = [i for v in lists.values() for i in v if isinstance(i, dict)]
    quotes = [(normalise(i["quote"]), i.get("page")) for i in items if i.get("quote")]
    cit = record.get("citation") or {}
    read = normalise(str(record.get("pages_read") or ""))
    annex = exp["annex_page"]
    term = exp["key_term"].split()[0]

    def blob(key: str) -> str:
        return " ".join(" ".join(map(str, x.values())) for x in lists[key] if isinstance(x, dict)).lower()

    checks = {
        "quotes_exact": bool(quotes) and all(q in whole for q, _ in quotes),
        "quote_pages_right": bool(quotes)
        and all(isinstance(p, int) and q in pages.get(p, "") for q, p in quotes),
        "definition_from_full_text": any(
            term in str(d.get("term", "")).lower()
            and d.get("page") == annex
            and normalise(str(d.get("quote") or "")) in pages.get(annex, "-")
            and d.get("quote")
            for d in lists["definitions"]
            if isinstance(d, dict)
        ),
        "finding_number": "412" in blob("findings"),
        "proxy_found": bool(re.search("licen[cs]e", blob("proxies"))),
        "pages_read_copies_note": normalise(picks["coverage"]["note"]) in read,
        "pages_read_adds_search": bool(re.search(rf"\b(p\.? ?|pages? ){annex}\b|\b{annex}\b.*search|search.*\b{annex}\b", read)),
        "no_whole_reading_claimed": bool(read)
        and not re.search(r"\b(read|reviewed|covered) (the )?(whole|entire|full|complete)|\ball (\d+ )?pages\b", read),
        "year_left_empty": cit.get("year") is None,
        "not_marked_peer_reviewed": str(cit.get("peer_reviewed", "")).lower() != "yes",
    }
    return _checks(exp, checks)


def score_triage(exp: dict, answer: dict) -> dict:
    """S29: each question in the right group; the hidden choice split; at most three put to
    the researcher now, the rest listed under Next. Groups are assistant, researcher,
    ramsey, decided, or a list of two for a split question."""
    got = answer.get("groups") or {}

    def grp(q: str) -> set[str]:
        v = got.get(q)
        return {str(x).lower() for x in v} if isinstance(v, list) else {str(v).lower()}

    want = exp["groups"]
    of = lambda kind: [q for q, g in want.items() if g == kind]  # noqa: E731
    research = of("researcher") + of("split")
    now, later = answer.get("for_researcher_now") or [], answer.get("next") or []
    decided = answer.get("already_decided") or {}
    checks = {
        "technical_kept_back": all(grp(q) == {"assistant"} for q in of("assistant")),
        "research_not_settled_by_assistant": all("assistant" not in grp(q) for q in of("researcher")),
        "research_to_researcher": all("researcher" in grp(q) for q in of("researcher")),
        "ramsey_routed": all("ramsey" in grp(q) for q in of("ramsey")),
        "already_decided_found": all(
            grp(q) == {"decided"} and exp["decided_date"] in str(decided.get(q, "")) for q in of("decided")
        ),
        "nothing_falsely_decided": not any("decided" in grp(q) for q in want if want[q] != "decided"),
        "hidden_choice_split": all(grp(q) >= {"assistant", "researcher"} for q in of("split")),
        "at_most_three": len(now) <= 3 and set(research) <= set(now) | set(later),
    }
    return _checks(exp, checks)


def score_methods(exp: dict, graded: dict, review: str | None = None) -> dict:
    """The grader's "raised" counts only when its quote is really in the review."""
    raised = {k for k, v in graded.get("raised", {}).items() if v is True and k in exp["flaws"]}
    if review is not None:
        evidence, whole = graded.get("evidence", {}), normalise(review)
        raised = {k for k in raised if evidence.get(k) and normalise(evidence[k]) in whole}
    return {
        "raised": sorted(raised),
        "missed": sorted(set(exp["flaws"]) - raised),
        "score": f"{len(raised)} of {len(exp['flaws'])} planted weaknesses raised",
        "passed": len(raised) >= exp["pass_if"]["flaws_raised_at_least"] and set(exp["must_catch"]) <= raised,
    }


def _per_case(exp: dict, records: dict[str, dict], verdict) -> dict:
    """The organisation steps: one verdict per case, "ok" or what was wrong."""
    cases = {c["case"]: verdict(c, records.get(c["case"]) or {}) for c in exp["cases"]}
    n = sum(v == "ok" for v in cases.values())
    return {
        "cases": cases,
        "score": f"{n} of {len(cases)} cases right",
        "passed": n >= exp["pass_if"]["cases_right_at_least"],
    }


def score_org(exp: dict, records: dict[str, dict]) -> dict:
    """The retired one-step agent: label, and a page, quote and confidence for it."""

    def verdict(case: dict, r: dict) -> str:
        label = r.get("label")
        if label not in case["expect_label"]:
            return f"wrong label: {label}"
        if label == "unknown":
            return "ok" if r.get("unknown_reason") else "unknown without a reason"
        if not (has_url(r) and r.get("quote") and r.get("confidence")):
            return "label without a page, a quote and a confidence level"
        return "ok"

    return _per_case(exp, records, verdict)


def score_finder(exp: dict, records: dict[str, dict]) -> dict:
    """The evidence step: the right status, evidence with every field, and no label."""

    def verdict(case: dict, r: dict) -> str:
        status = r.get("status")
        items = [i for i in r.get("evidence") or [] if isinstance(i, dict)]
        complete = [
            i
            for i in items
            if has_url(i)
            and i.get("quote")
            and i.get("page")
            and isinstance(i.get("level"), int)
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(i.get("date", "")))
        ]
        if status not in STATUSES:
            return f"status not in the fixed list: {status}"
        if status not in case["expect_status"]:
            return f"wrong status: {status}"
        if "label" in r or "category" in r:
            return "gave a label; this step only finds evidence"
        reason = normalise(str(r.get("status_reason", "")))
        if status == "abstained" and reason not in case.get("expect_reason", []):
            return f"abstained with the wrong reason or none: {r.get('status_reason')}"
        if status in ("confident", "uncertain", "confirmed negative") and (
            not complete or len(complete) < len(items)
        ):
            return "evidence without a page, a quote, a date and a level for every item"
        return "ok"

    return _per_case(exp, records, verdict)


def score_classifier(exp: dict, records: dict[str, dict], evidence: dict[str, dict]) -> dict:
    """The classifying step: label, rule, confidence and status as the stored evidence
    requires, and a quote and page that are in the stored evidence, not from anywhere else."""

    def verdict(case: dict, r: dict) -> str:
        label = r.get("label")
        stored = {
            str(i.get("source_url")): normalise(i.get("quote", ""))
            for i in (evidence.get(case["case"]) or {}).get("evidence", [])
        }
        quote = normalise(str(r.get("quote") or ""))
        if label not in exp["labels"]:
            return f"label not in the codebook's list: {label}"
        if label not in case["expect_label"]:
            return f"wrong label: {label}"
        if r.get("status") != case["expect_status"]:
            return f"wrong status: {r.get('status')}"
        if label == "unknown":
            reason = normalise(str(r.get("unknown_reason") or ""))
            return "ok" if reason == case["expect_reason"] else f"wrong reason: {reason or None}"
        if r.get("rule") != case["expect_rule"]:
            return f"wrong rule: {r.get('rule')}"
        if r.get("confidence") != case["expect_confidence"]:
            return f"confidence does not follow from the evidence: {r.get('confidence')}"
        if not quote or quote not in stored.get(str(r.get("source_url")), ""):
            return "quote or page is not in the stored evidence"
        return "ok"

    return _per_case(exp, records, verdict)


# ---- one run folder ----


def agent_model(agent: str) -> str:
    """The model of the agent that runs a case (an agent's name, or one of CASE_AGENT)."""
    agent = CASE_AGENT.get(agent, agent)
    if agent in RETIRED:
        return RETIRED[agent]
    head = (ROOT / ".claude" / "agents" / f"{agent}.md").read_text().split("---")[1]
    return re.search(r"^model:\s*(\S+)", head, flags=re.M).group(1)


def _jobs(folder: Path) -> dict:
    """For each case key: (its answer files, how to score it from its expected.json)."""

    def load(name: str):
        path = folder / name
        return json.loads(path.read_text()) if path.exists() else None

    def one(name: str, fn, *more):
        return [f"{name}.json"], lambda e: fn(e, load(f"{name}.json"), *more)

    def per_case(name: str, fn, extra=lambda e: []):
        files = [f"{name}-{c['case']}.json" for c in expected(name)["cases"]]
        return files, lambda e: fn(e, {c["case"]: load(f"{name}-{c['case']}.json") for c in e["cases"]}, *extra(e))

    def methods(name: str):
        files = [f"{name}.md", f"{name}-graded.json"]
        return files, lambda e: score_methods(e, load(f"{name}-graded.json"), (folder / f"{name}.md").read_text())

    def stored_evidence(e: dict) -> list:
        ev = CASES / "org-classifier" / "evidence"
        return [{c["case"]: json.loads((ev / f"{c['case']}.json").read_text()) for c in e["cases"]}]

    return {
        "citation-checker": one("citation-checker", score_citation),
        "numbers-checker": one("numbers-checker", score_numbers),
        "source-reader": one("source-reader", score_source, (CASES / "source-reader" / "source.md").read_text()),
        "methods-reviewer": methods("methods-reviewer"),
        "evidence-finder": per_case("evidence-finder", score_finder),
        "org-classifier": per_case("org-classifier", score_classifier, stored_evidence),
        "org-researcher": per_case("org-researcher", score_org),
        "decision-triage": one("decision-triage", score_triage),
        "source-reader-chunks": one(
            "source-reader-chunks",
            score_source_chunks,
            *(json.loads((CASES / "source-reader-chunks" / f).read_text()) for f in ("text.json", "picks.json")),
        ),
    } | {key: methods(key) for key in CASE_AGENT if key.startswith("methods-reviewer")}


def score_folder(folder: Path) -> dict:
    out = {}
    for agent, (files, job) in _jobs(folder).items():
        if not any((folder / name).exists() for name in files):
            if agent not in RETIRED and agent not in CASE_AGENT:
                # No answer at all: not run here. Neither a pass nor a fail.
                out[agent] = {"score": "not run", "passed": None, "model": agent_model(agent)}
            continue
        try:
            out[agent] = job(expected(agent))
        except (AttributeError, TypeError, KeyError, OSError, json.JSONDecodeError) as err:
            out[agent] = {"score": "no usable answer", "passed": False, "problem": repr(err)}
        out[agent]["model"] = agent_model(agent)
    return out


# ---- E6: what is reported first ----

# Organisation verdicts that assert something false ("wrong label: unknown" is a gap).
ASSERTED = (
    "label not in",
    "wrong rule",
    "confidence does not follow",
    "gave a label",
    "wrong status: confident",
    "wrong status: confirmed negative",
    "quote or page is not in",
)
GAPS = ("wrong label: unknown", "wrong label: None")


def confident_wrong(agent: str, r: dict) -> list[str]:
    """The answers that asserted something false, as opposed to leaving a gap: a false
    all-clear or false alarm from a checker; a made-up quote, wrong page, guessed year,
    claimed peer review or recommendation-as-finding from the source reader; a label,
    rule or confidence the evidence does not support. The methods review adds misses only."""
    if r.get("passed") is None or "problem" in r:
        return []
    if "false_alarms" in r:
        return [f"{k} (false alarm)" for k in r["false_alarms"]] + [f"{k} (passed as correct)" for k in r["missed"]]
    if "checks" in r:
        return sorted(k for k in ASSERTIONS.get(agent, SOURCE_ASSERTIONS) if r["checks"].get(k) is False)
    return [
        f"{case} ({v})"
        for case, v in ((c, str(v)) for c, v in r.get("cases", {}).items())
        if (v.startswith("wrong label:") and v not in GAPS) or v.startswith(ASSERTED)
    ]


def found_items(r: dict) -> tuple[set[str], set[str]]:
    """What a result found, and everything it could have found."""
    for key in ("caught", "raised"):
        if key in r:
            return set(r[key]), set(r[key]) | set(r["missed"])
    if "checks" in r:
        return {k for k, v in r["checks"].items() if v}, set(r["checks"])
    if "cases" in r:
        return {k for k, v in r["cases"].items() if v == "ok"}, set(r["cases"])
    return set(), set()


def weighted_missed(key: str, r: dict) -> tuple[int, int]:
    """(weight missed, total weight)."""
    exp = expected(key)
    required = set(exp.get("must_catch", [])) | set(exp.get("must_pass", []))
    got, every = found_items(r)
    weight = {i: REQUIRED_WEIGHT if i in required else 1 for i in every}
    return sum(weight[i] for i in every - got), sum(weight.values())


def headline(agents: dict) -> dict:
    ran = {k: r for k, r in agents.items() if r.get("passed") is not None}
    wrong = {k: confident_wrong(k, r) for k, r in ran.items()}
    missed = {
        k: "no usable answer" if "problem" in r else "{} of {}".format(*weighted_missed(k, r))
        for k, r in ran.items()
    }
    return {
        "confident_wrong": sum(len(v) for v in wrong.values()),
        "confident_wrong_by_agent": {k: v for k, v in wrong.items() if v},
        "weighted_missed": missed,
        "weighting": f"an item the case requires counts {REQUIRED_WEIGHT}, any other 1",
    }


# ---- C10: the run record ----


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixed_parts() -> dict:
    """What must not change during a run: the agents' instructions, the cases, this file."""
    files = sorted((ROOT / ".claude" / "agents").glob("*.md")) + [ROOT / p for p in INSTRUCTIONS]
    cases = sorted(p for p in CASES.rglob("*") if p.is_file() and p.name != ".DS_Store")
    tested = hashlib.sha256()
    for p in [*cases, Path(__file__).resolve()]:
        tested.update(p.relative_to(ROOT).as_posix().encode() + b"\0" + _sha(p).encode())
    return {
        "instructions": {p.relative_to(ROOT).as_posix(): _sha(p) for p in files},
        "cases_and_scorer": tested.hexdigest(),
    }


def record_run(folder: Path, client: str) -> dict:
    record = {
        "date": dt.date.today().isoformat(),
        "client": client,
        "models": {a: agent_model(a) for a in [*AGENTS, *CASE_AGENT]},
        "settings": "Claude Code sets no temperature or other sampling setting for an "
        "agent; each runs with the client's defaults. Agents are started with the "
        "model from their file and told to follow it.",
    } | fixed_parts()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "run-record.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def check_record(folder: Path) -> str | list[str]:
    """"matches", "missing" (runs from before the record existed), or what changed."""
    path = folder / "run-record.json"
    if not path.exists():
        return "missing"
    saved, now = json.loads(path.read_text()), fixed_parts()
    keys = saved["instructions"].keys() | now["instructions"].keys()
    changed = sorted(k for k in keys if saved["instructions"].get(k) != now["instructions"].get(k))
    if saved["cases_and_scorer"] != now["cases_and_scorer"]:
        changed.append(".claude/skills/run-evals/cases or .claude/skills/run-evals/scripts/score.py")
    changed += [f"model of {a}" for a, m in saved["models"].items() if agent_model(a) != m]
    return changed or "matches"


# ---- one run, and repeat runs ----


def score_run(folder: Path) -> dict:
    agents = score_folder(folder)
    ran = [a for a in agents.values() if a["passed"] is not None]
    record = check_record(folder)
    result = {
        "run": folder.name,
        "agents": agents,
        "not_run": sorted(k for k, a in agents.items() if a["passed"] is None),
        # Only for the agents run; an empty run, or one whose inputs changed, passes nothing.
        "all_passed": bool(ran) and all(a["passed"] for a in ran) and record in ("matches", "missing"),
        "run_record": record,
        "headline": headline(agents),
    }
    (folder / "summary.json").write_text(json.dumps(result, indent=1) + "\n")
    return result


def repeat_folders(folder: Path) -> list[Path]:
    return sorted(p for p in folder.glob("run*") if p.is_dir() and p.name[3:].isdigit())


def aggregate(runs: dict[str, dict]) -> dict:
    """Across repeat runs: each item found in k of n runs."""
    agents: dict[str, dict] = {}
    for key in sorted({k for r in runs.values() for k in r["agents"]}):
        scored = [r["agents"][key] for r in runs.values() if r["agents"].get(key, {}).get("passed") is not None]
        if not scored:
            continue
        n, every, count, found_n = len(scored), set(), {}, []
        for r in scored:
            got, universe = found_items(r)
            every |= universe
            found_n.append(len(got))
            for i in got:
                count[i] = count.get(i, 0) + 1
        lo, hi = min(found_n), max(found_n)
        agents[key] = {
            "model": agent_model(key),
            "runs": n,
            "passed": f"{sum(bool(r['passed']) for r in scored)} of {n} runs",
            "found": f"{lo} to {hi} of {len(every)}" if lo != hi else f"{lo} of {len(every)} in every run",
            "items": {i: f"found in {count.get(i, 0)} of {n} runs" for i in sorted(every)},
            "found_every_time": sorted(i for i in every if count.get(i, 0) == n),
            "found_in_some_runs_only": sorted(i for i in every if 0 < count.get(i, 0) < n),
            "never_found": sorted(i for i in every if not count.get(i)),
            "confident_wrong_per_run": [len(confident_wrong(key, r)) for r in scored],
        }
    wrong = [r["headline"]["confident_wrong"] for r in runs.values()]
    return {
        "runs": sorted(runs),
        "headline": {
            "confident_wrong_per_run": wrong,
            "confident_wrong_range": f"{min(wrong)} to {max(wrong)}" if runs else None,
        },
        "agents": agents,
        "all_runs_passed": bool(runs) and all(r["all_passed"] for r in runs.values()),
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--record":
        record_run(Path(args[1]), args[2] if len(args) > 2 else "Claude Code")
        print(f"Run record written in {args[1]}")
        return 0
    folder = Path(args[0])
    repeats = repeat_folders(folder)
    if not repeats:
        result = score_run(folder)
        h = result["headline"]
        print(f"Confident and wrong: {h['confident_wrong']}")
        for agent, items in h["confident_wrong_by_agent"].items():
            print(f"  {agent}: {', '.join(items)}")
        if result["run_record"] != "matches":
            print(f"Run record: {result['run_record']}")
        for agent, r in result["agents"].items():
            mark = "-" if r["passed"] is None else "pass" if r["passed"] else "FAIL"
            missed = h["weighted_missed"].get(agent)
            missed = f"  (weighted misses {missed})" if missed else ""
            print(f"{mark:5} {agent:26} {r['model']:7} {r['score']}{missed}")
        return 0 if result["all_passed"] else 1
    runs = {p.name: score_run(p) for p in repeats}
    agg = aggregate(runs)
    (folder / "repeats.json").write_text(json.dumps(agg, indent=1) + "\n")
    print(f"Confident and wrong, per run: {agg['headline']['confident_wrong_per_run']}")
    for agent, a in agg["agents"].items():
        some = a["found_in_some_runs_only"]
        some = f"; only in some runs: {', '.join(some)}" if some else ""
        never = f"; never: {', '.join(a['never_found'])}" if a["never_found"] else ""
        print(f"{a['passed']:12} {agent:26} {a['model']:7} {a['found']}{some}{never}")
    return 0 if agg["all_runs_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
