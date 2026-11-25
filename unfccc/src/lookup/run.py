"""The three steps of a look-up run, and the files they write.

    evidence   for each organisation: open registers, a web search for pages, code opens
               the pages, the model picks the evidence, code checks every quote
               -> <study>/data/derived/evidence/<org_id>.json
    classify   for each evidence record: code settles failed and abstained records; the
               model applies the codebook to the rest; code sets confidence and status
               and checks the result -> <study>/data/derived/classified.jsonl
    check      Haiku reads each labelled result and flags any it doubts; it changes
               nothing -> <study>/data/derived/classified_checks.jsonl

Each step skips what is already done under the same codebook version and model, so a
stopped run is started again with the same command. Every run is logged in
<study>/data/derived/lookup_runs.jsonl with what it cost.
"""

from __future__ import annotations

import datetime as dt
import json
import random
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from . import checks, llm, pages, registries
from .codebook import Codebook, load

PROMPTS = Path(__file__).parent / "prompts"
CLASSIFY_FAILED = "classification failed the code checks"
MAX_ATTEMPTS = 2  # an evidence look-up that failed is tried once more on the next run

# Rough cost per organisation, for --dry-run, in dollars at list prices. From the sizes of
# the prompts and pages; replace with measured numbers after the pilot (lookup_runs.jsonl).
ESTIMATE = {"evidence": 0.11, "classify": 0.01, "check": 0.0005}

EVIDENCE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["matched_entity", "status", "status_reason", "evidence",
                 "instructions_found_in_pages"],
    "properties": {
        "matched_entity": {"type": ["string", "null"]},
        "status": {"type": "string", "enum": ["confident", "uncertain", "abstained",
                                              "confirmed negative"]},
        "status_reason": {"type": ["string", "null"]},
        "evidence": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["source_url", "page", "quote", "level", "source_type"],
            "properties": {"source_url": {"type": "string"}, "page": {"type": "string"},
                           "quote": {"type": "string"}, "level": {"type": "integer"},
                           "source_type": {"type": "string", "enum": list(checks.SOURCE_TYPES)}}}},
        "instructions_found_in_pages": {"type": ["string", "null"]}}}

CHECK_SCHEMA = {"type": "object", "additionalProperties": False,
                "required": ["supports_match", "supports_label", "note"],
                "properties": {"supports_match": {"type": "boolean"},
                               "supports_label": {"type": "boolean"},
                               "note": {"type": "string"}}}


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


@dataclass
class Study:
    root: Path
    draft: bool = False

    @property
    def derived(self) -> Path:
        d = self.root / "data" / "derived"
        return d / "draft-codebook" if self.draft else d

    @property
    def evidence_dir(self) -> Path:
        return self.derived / "evidence"

    @property
    def classified(self) -> Path:
        return self.derived / "classified.jsonl"

    @property
    def checked(self) -> Path:
        return self.derived / "classified_checks.jsonl"

    @property
    def runs(self) -> Path:
        return self.root / "data" / "derived" / "lookup_runs.jsonl"

    @property
    def cache(self) -> Path:
        return self.root / "data" / "derived" / "lookup_cache"

    @property
    def codebook_path(self) -> Path:
        return self.root / "docs" / "codebook.md"

    def organisations(self) -> list[dict]:
        import pandas as pd

        tables = sorted((self.root / "data" / "derived").glob("organisations*.parquet"))
        if not tables:
            raise SystemExit("No organisation table yet: run /clean-data first.")
        df = pd.read_parquet(tables[0])
        out = []
        for r in df.to_dict("records"):
            spell = r.get("clean_spellings")
            if spell is None:
                spell = r.get("raw_spellings")
            spell = [str(s) for s in (list(spell) if spell is not None else [])]
            out.append({"org_id": str(r["org_id"]), "name": str(r["canonical_name"]),
                        "country": r.get("country_context"), "spellings": spell[:8]})
        return out


# ---------------------------------------------------------------- files

def read_jsonl(path: Path) -> dict[str, dict]:
    """The last record for each org_id: the file is only appended to."""
    out: dict[str, dict] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                out[rec["org_id"]] = rec
    return out


def append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_evidence(study: Study, org_id: str) -> dict | None:
    p = study.evidence_dir / f"{org_id}.json"
    return json.loads(p.read_text()) if p.exists() else None


def write_evidence(study: Study, rec: dict) -> None:
    study.evidence_dir.mkdir(parents=True, exist_ok=True)
    p = study.evidence_dir / f"{rec['org_id']}.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    tmp.replace(p)


def choose(orgs: list[dict], sample: int | None = None, seed: int = 7,
           ids: list[str] | None = None) -> list[dict]:
    if ids:
        want = set(ids)
        return [o for o in orgs if o["org_id"] in want]
    if sample and sample < len(orgs):
        return sorted(random.Random(seed).sample(orgs, sample), key=lambda o: o["org_id"])
    return orgs


# ---------------------------------------------------------------- evidence

def _get(obj, key, default=None):
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def searches_and_urls(blocks) -> tuple[list[str], set[str]]:
    """The searches the model actually ran, and every address its results contained."""
    queries, urls = [], set()
    for b in blocks:
        kind = _get(b, "type")
        if kind == "server_tool_use" and _get(b, "name") == "web_search":
            q = (_get(b, "input") or {}).get("query")
            if q:
                queries.append(q)
        elif kind == "web_search_tool_result":
            content = _get(b, "content")
            if isinstance(content, list):
                for item in content:
                    u = _get(item, "url")
                    if u:
                        urls.add(u)
    return queries, urls


def describe_org(org: dict) -> str:
    """Only the organisation's name, country and spellings go to the model and the web."""
    lines = [f"Name as written: {org['name']}", f"Country: {org.get('country') or 'not given'}"]
    others = [s for s in org.get("spellings", []) if s != org["name"]]
    if others:
        lines.append("Other spellings seen: " + "; ".join(others))
    return "\n".join(lines)


def page_block(p: dict, names: list[str]) -> str:
    body = pages.excerpt(p["text"], names)
    return (f'<page url="{p["final_url"] if p["url"] != p["final_url"] else p["url"]}" '
            f'kind="{p["kind"]}" opened="{p["fetched"]}">\n{body}\n</page>')


def find_evidence(org: dict, cb: Codebook, client, http, usage: llm.Usage, model: str,
                  cache: Path | None = None, max_searches: int = 5) -> dict:
    rec = {"org_id": org["org_id"], "name_as_written": org["name"], "country": org.get("country"),
           "matched_entity": None, "status": None, "status_reason": None, "searches": [],
           "evidence": [], "instructions_found_in_pages": None, "pages_opened": [],
           "problems": [], "model": model, "codebook_version": cb.version, "run_date": now()}
    names = [org["name"], *org.get("spellings", [])]

    reg_pages, reg_problems = registries.lookup(org["name"], http, cache and cache / "registries")
    rec["problems"] += reg_problems
    reg_text = "\n\n".join(p["text"] for p in reg_pages) or "Nothing found in the registers."

    msg, blocks = llm.call(
        client, usage, model=model, max_tokens=4000,
        system=llm.cached_system((PROMPTS / "find_pages.md").read_text()),
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": max_searches}],
        messages=[{"role": "user", "content": describe_org(org)
                   + "\n\nWhat the open registers returned:\n" + reg_text}])
    queries, seen = searches_and_urls(blocks)
    try:
        chosen = llm.json_of(blocks)
    except ValueError:
        chosen = {"urls": [], "note": "the page search gave no list of pages"}
    langs = chosen.get("languages") or {}
    rec["searches"] = [{"query": q, "language": langs.get(q)} for q in queries]
    rec["searches"] += [{"query": f"register:{s}", "language": None}
                        for s in ("wikidata", "gleif")]
    allowed = seen | {w for p in reg_pages for w in p.get("websites", [])}
    urls = [u for u in chosen.get("urls", []) if u in allowed][:6]
    rejected = [u for u in chosen.get("urls", []) if u not in allowed]
    if rejected:
        rec["problems"].append(
            f"{len(rejected)} address(es) not in the search results were not opened")

    fetched = [pages.fetch(u, http, cache and cache / "pages") for u in urls]
    rec["pages_opened"] = [{"url": p["url"], "final_url": p["final_url"], "ok": p["ok"],
                            "error": p["error"], "fetched": p["fetched"]} for p in fetched]
    usable = [p for p in reg_pages + fetched if p["ok"]]
    by_url = {}
    for p in usable:
        by_url[p["url"]] = p
        by_url[p["final_url"]] = p

    if not usable:
        rec["status"] = "abstained"
        rec["status_reason"] = "nothing found"
        if urls and not any(p["ok"] for p in fetched):
            rec["status"] = "failed"
            rec["status_reason"] = "the chosen pages could not be opened: " + "; ".join(
                sorted({p["error"] for p in fetched if p["error"]}))
        return rec

    injected = sorted({x for p in usable for x in checks.injection_phrases(p["text"])})
    user = (describe_org(org) + f"\n\nNote from the page search: {chosen.get('note', '')}\n\n"
            + "\n\n".join(page_block(p, names) for p in usable))
    system = llm.cached_system((PROMPTS / "extract_evidence.md").read_text()
                               + "\n\n## The codebook\n\n" + cb.text)
    messages = [{"role": "user", "content": user}]
    out, problems = None, []
    for _attempt in range(2):
        msg, blocks = llm.call(client, usage, model=model, max_tokens=4000, system=system,
                               output_config=llm.structured(EVIDENCE_SCHEMA), messages=messages)
        out = llm.json_of(blocks)
        for item in out.get("evidence", []):
            p = by_url.get(item.get("source_url"))
            item["date"] = p["fetched"] if p else None
        trial = dict(rec, **{k: out.get(k) for k in ("matched_entity", "status", "status_reason",
                                                     "evidence")})
        problems = checks.check_evidence(trial, by_url)
        if not problems:
            break
        messages = messages + [
            {"role": "assistant", "content": llm.text_of(blocks)},
            {"role": "user", "content": "Code found these problems. Return the record again with "
             "them fixed; copy quotes exactly from the page text:\n- " + "\n- ".join(problems)}]
    rec.update({k: out.get(k) for k in ("matched_entity", "status", "status_reason", "evidence")})
    found = [x for x in [out.get("instructions_found_in_pages"), *injected] if x]
    rec["instructions_found_in_pages"] = "; ".join(found) or None
    rec, notes = checks.repair_evidence(rec, by_url)
    rec["problems"] += notes
    return rec


def failed_record(org: dict, cb: Codebook, model: str, reason: str) -> dict:
    return {"org_id": org["org_id"], "name_as_written": org["name"], "country": org.get("country"),
            "matched_entity": None, "status": "failed", "status_reason": reason, "searches": [],
            "evidence": [], "instructions_found_in_pages": None, "pages_opened": [],
            "problems": [], "model": model, "codebook_version": cb.version, "run_date": now()}


def evidence_todo(study: Study, orgs: list[dict], cb: Codebook, model: str) -> list[dict]:
    todo = []
    for o in orgs:
        old = read_evidence(study, o["org_id"])
        if (old is None or old.get("codebook_version") != cb.version
                or old.get("model") != model
                or (old["status"] == "failed" and old.get("attempts", 1) < MAX_ATTEMPTS)):
            todo.append(o)
    return todo


def run_evidence(study: Study, orgs: list[dict], cb: Codebook, client, http, usage: llm.Usage,
                 workers: int = 4, log=print) -> dict:
    model = llm.agent_model("evidence-finder")
    todo = evidence_todo(study, orgs, cb, model)
    log(f"Evidence: {len(todo)} to look up, {len(orgs) - len(todo)} already done.")

    def one(org):
        old = read_evidence(study, org["org_id"])
        old = old or {}
        attempts = old.get("attempts", 0) + 1 if old.get("status") == "failed" else 1
        try:
            rec = find_evidence(org, cb, client, http, usage, model, study.cache)
        except Exception as e:  # one organisation failing must not stop the run
            rec = failed_record(org, cb, model, f"the look-up did not finish ({type(e).__name__})")
            rec["problems"].append(traceback.format_exception_only(e)[-1].strip()[:300])
        rec["attempts"] = attempts
        write_evidence(study, rec)
        return rec["status"]

    counts: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, fut in enumerate(as_completed([pool.submit(one, o) for o in todo]), 1):
            s = fut.result()
            counts[s] = counts.get(s, 0) + 1
            if i % 25 == 0:
                log(f"  {i}/{len(todo)} done, about ${usage.dollars:.2f} so far")
    return counts


# ---------------------------------------------------------------- classify

def classify_schema(cb: Codebook) -> dict:
    props = {f: {"enum": allowed} for f, allowed in cb.labels["fields"].items()}
    props.update({"rule": {"enum": [*cb.labels["rules"], None]},
                  "reasoning": {"type": "string"},
                  "evidence_index": {"type": ["integer", "null"]},
                  "unknown_reason": {"enum": [*sorted(cb.unknown_reasons), None]}})
    return {"type": "object", "additionalProperties": False, "required": list(props),
            "properties": props}


def base_record(org: dict, ev: dict, cb: Codebook, model: str) -> dict:
    rec = {"org_id": org["org_id"], "name": org["name"], "country_context": org.get("country"),
           "matched_entity": ev.get("matched_entity")}
    rec.update({f: None for f in cb.labels["fields"]})
    rec.update({"rule": None, "reasoning": None, "source_url": None, "page": None, "quote": None,
                "source_type": None, "evidence_level": None, "retrieved": None,
                "confidence": None, "status": None, "unknown_reason": None, "method": "lookup",
                "codebook_version": cb.version, "model": model, "run_date": now()})
    return rec


def settled_by_code(org: dict, ev: dict, cb: Codebook, model: str) -> dict | None:
    """Failed and abstained look-ups are classified by code, as the org-classifier rules say."""
    if ev["status"] not in ("failed", "abstained"):
        return None
    rec = base_record(org, ev, cb, None)
    rec[cb.label_field] = "unknown"
    rec["method"] = "rule"
    if ev["status"] == "failed":
        rec.update(unknown_reason="lookup failed", status="failed",
                   reasoning=f"The look-up did not finish: {ev.get('status_reason')}")
    else:
        reason = ev.get("status_reason")
        reason = reason if reason in cb.unknown_reasons else "nothing found"
        rec.update(unknown_reason=reason, status="abstained",
                   reasoning=f"The evidence step abstained: {ev.get('status_reason')}")
    return rec


def classify_request(ev: dict, cb: Codebook, model: str, problems: list[str] | None = None) -> dict:
    shown = {k: ev.get(k) for k in ("name_as_written", "country", "matched_entity", "status",
                                    "status_reason", "evidence")}
    messages = [{"role": "user", "content": "The evidence record:\n\n"
                 + json.dumps(shown, ensure_ascii=False, indent=1)}]
    if problems:
        messages[0]["content"] += ("\n\nA first answer had these problems, found by code. "
                                   "Avoid them:\n- " + "\n- ".join(problems))
    return {"model": model, "max_tokens": 2000,
            "system": llm.cached_system((PROMPTS / "classify.md").read_text() + "\n\n" + cb.text),
            "output_config": llm.structured(classify_schema(cb)), "messages": messages}


def finish(org: dict, ev: dict, cb: Codebook, model: str, answer: dict) -> dict:
    """Turn the model's answer into a record: code copies the evidence and sets confidence."""
    rec = base_record(org, ev, cb, model)
    for f in cb.labels["fields"]:
        rec[f] = answer.get(f)
    rec.update(rule=answer.get("rule"), reasoning=answer.get("reasoning"),
               unknown_reason=answer.get("unknown_reason"))
    if rec[cb.label_field] == "unknown":
        rec["status"] = "abstained"
        rec["rule"] = None
        return rec
    rec["unknown_reason"] = None
    items = ev.get("evidence") or []
    i = answer.get("evidence_index")
    if isinstance(i, int) and 0 <= i < len(items):
        it = items[i]
        rec.update(source_url=it["source_url"], page=it["page"], quote=it["quote"],
                   source_type=it["source_type"], evidence_level=it["level"],
                   retrieved=it.get("date"))
        conf = cb.confidence(it["level"], ev["status"])
        rec["confidence"] = conf
        rec["status"] = checks.expected_status(cb, rec, conf) if conf else None
    return rec


def unchecked_failure(org, ev, cb, model, problems) -> dict:
    rec = base_record(org, ev, cb, model)
    rec[cb.label_field] = "unknown"
    rec.update(unknown_reason=CLASSIFY_FAILED, status="failed", check_problems=problems,
               reasoning="Two answers failed the code checks; a person should look at this one.")
    return rec


def classify_todo(study: Study, orgs: list[dict], cb: Codebook, model: str):
    done = read_jsonl(study.classified)
    todo, missing = [], 0
    for o in orgs:
        ev = read_evidence(study, o["org_id"])
        if ev is None:
            missing += 1
            continue
        old = done.get(o["org_id"])
        if old and old.get("codebook_version") == cb.version and old.get("model") in (model, None) \
                and old.get("evidence_run") == ev.get("run_date"):
            continue
        todo.append((o, ev))
    return todo, missing


def run_classify(study: Study, orgs: list[dict], cb: Codebook, client, usage: llm.Usage,
                 batch: bool = False, workers: int = 4, log=print) -> dict:
    model = llm.agent_model("org-classifier")
    todo, missing = classify_todo(study, orgs, cb, model)
    log(f"Classify: {len(todo)} to classify; {missing} have no evidence record yet.")
    counts: dict[str, int] = {}

    def save(rec, ev):
        rec["evidence_run"] = ev.get("run_date")
        append_jsonl(study.classified, rec)
        counts[rec["status"]] = counts.get(rec["status"], 0) + 1

    need_model = []
    for o, ev in todo:
        rec = settled_by_code(o, ev, cb, model)
        if rec:
            save(rec, ev)
        else:
            need_model.append((o, ev))

    def attempt(pairs, problems_by_id):
        reqs = {o["org_id"]: classify_request(ev, cb, model, problems_by_id.get(o["org_id"]))
                for o, ev in pairs}
        if batch and reqs:
            msgs = llm.run_batch(client, usage, reqs, log=log)
            return {k: (llm.json_of(m.content) if m else None) for k, m in msgs.items()}
        out = {}

        def one(k):
            try:
                _, blocks = llm.call(client, usage, **reqs[k])
                return k, llm.json_of(blocks)
            except Exception:
                return k, None
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for k, ans in pool.map(one, list(reqs)):
                out[k] = ans
        return out

    problems_by_id: dict[str, list[str]] = {}
    pending = need_model
    for round_no in range(2):
        answers = attempt(pending, problems_by_id)
        retry = []
        for o, ev in pending:
            ans = answers.get(o["org_id"])
            if ans is None:
                probs = ["the model gave no usable answer"]
            else:
                rec = finish(o, ev, cb, model, ans)
                probs = checks.check_classified(rec, ev, cb)
                if not probs:
                    save(rec, ev)
                    continue
            if round_no == 0:
                problems_by_id[o["org_id"]] = probs
                retry.append((o, ev))
            else:
                save(unchecked_failure(o, ev, cb, model, probs), ev)
        pending = retry
    return counts


# ---------------------------------------------------------------- check

def check_request(rec: dict, cb: Codebook) -> dict:
    shown = {"name_as_written": rec["name"], "country": rec.get("country_context"),
             "matched_entity": rec.get("matched_entity"),
             "label": {f: rec.get(f) for f in cb.labels["fields"]}, "rule": rec.get("rule"),
             "reasoning": rec.get("reasoning"), "quote": rec.get("quote")}
    return {"model": llm.CHECKER, "max_tokens": 600,
            "system": llm.cached_system((PROMPTS / "check.md").read_text()),
            "output_config": {"effort": "low", **llm.structured(CHECK_SCHEMA)},
            "messages": [{"role": "user", "content": json.dumps(shown, ensure_ascii=False)}]}


def run_check(study: Study, orgs: list[dict], cb: Codebook, client, usage: llm.Usage,
              batch: bool = False, workers: int = 8, log=print) -> dict:
    wanted = {o["org_id"] for o in orgs}
    classified = read_jsonl(study.classified)
    done = read_jsonl(study.checked)
    todo = [r for k, r in classified.items() if k in wanted and r[cb.label_field] != "unknown"
            and done.get(k, {}).get("run_date_checked_record") != r["run_date"]]
    log(f"Check: {len(todo)} labelled results to check with {llm.CHECKER}.")
    reqs = {r["org_id"]: check_request(r, cb) for r in todo}
    if batch and reqs:
        msgs = llm.run_batch(client, usage, reqs, log=log)
        answers = {k: (llm.json_of(m.content) if m else None) for k, m in msgs.items()}
    else:
        def one(k):
            try:
                _, blocks = llm.call(client, usage, **reqs[k])
                return k, llm.json_of(blocks)
            except Exception:
                return k, None
        with ThreadPoolExecutor(max_workers=workers) as pool:
            answers = dict(pool.map(one, list(reqs)))
    flagged = 0
    for r in todo:
        a = answers.get(r["org_id"])
        out = {"org_id": r["org_id"], "model": llm.CHECKER, "run_date": now(),
               "run_date_checked_record": r["run_date"]}
        if a is None:
            out.update(supports_match=None, supports_label=None,
                       note="the check did not run", needs_review=True)
        else:
            out.update(supports_match=a.get("supports_match"),
                       supports_label=a.get("supports_label"), note=a.get("note", ""),
                       needs_review=not (a.get("supports_match") and a.get("supports_label")))
        flagged += out["needs_review"]
        append_jsonl(study.checked, out)
    return {"checked": len(todo), "needs_review": flagged}


# ---------------------------------------------------------------- status and log

def status(study: Study, cb: Codebook | None = None) -> dict:
    ev_counts: dict[str, int] = {}
    if study.evidence_dir.exists():
        for p in study.evidence_dir.glob("*.json"):
            s = json.loads(p.read_text()).get("status")
            ev_counts[s] = ev_counts.get(s, 0) + 1
    cl = read_jsonl(study.classified)
    cl_counts: dict[str, int] = {}
    for r in cl.values():
        cl_counts[r["status"]] = cl_counts.get(r["status"], 0) + 1
    ch = read_jsonl(study.checked)
    return {"evidence": ev_counts, "classified": cl_counts,
            "checked": len(ch), "needs_review": sum(1 for r in ch.values() if r["needs_review"])}


def estimate(step: str, n: int, batch: bool = False) -> float:
    per = ESTIMATE[step] * (0.5 if batch and step != "evidence" else 1.0)
    return round(per * n, 2)


def log_run(study: Study, entry: dict) -> None:
    append_jsonl(study.runs, {"org_id": "_run", **entry})


def codebook_for(study: Study, draft: bool) -> Codebook:
    return load(study.codebook_path, draft=draft)
