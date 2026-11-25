"""The scorer itself is checked: right answers pass, wrong ones fail.

Also checks that the test cases are consistent with themselves, so an agent is
never marked wrong because of a mistake in the case.
"""

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import score  # noqa: E402

CASES = score.CASES


def perfect(exp: dict, good: str, bad: str) -> dict:
    verdicts = {k: good for k in exp["clean"]} | {k: bad for k in exp["planted"]}
    return {"verdicts": verdicts, "uncited": exp.get("uncited", [])}


def test_citation_perfect_answer_passes():
    exp = score.expected("citation-checker")
    assert score.score_citation(exp, perfect(exp, "supported", "not found"))["passed"]


def test_citation_false_alarm_fails():
    exp = score.expected("citation-checker")
    answer = perfect(exp, "supported", "not found")
    answer["verdicts"][exp["clean"][0]] = "overstated"
    assert not score.score_citation(exp, answer)["passed"]


def test_citation_missed_must_catch_fails():
    exp = score.expected("citation-checker")
    answer = perfect(exp, "supported", "not found")
    answer["verdicts"][exp["must_catch"][0]] = "supported"
    assert not score.score_citation(exp, answer)["passed"]


def test_citation_missing_the_uncited_statement_fails():
    exp = score.expected("citation-checker")
    answer = perfect(exp, "supported", "not found") | {"uncited": []}
    assert not score.score_citation(exp, answer)["passed"]


def test_numbers_perfect_passes_and_everything_ok_fails():
    exp = score.expected("numbers-checker")
    assert score.score_numbers(exp, perfect(exp, "ok", "mismatch"))["passed"]
    assert not score.score_numbers(exp, perfect(exp, "ok", "ok"))["passed"]


def test_numbers_false_alarm_fails():
    exp = score.expected("numbers-checker")
    answer = perfect(exp, "ok", "mismatch")
    answer["verdicts"][exp["clean"][0]] = "mismatch"
    assert not score.score_numbers(exp, answer)["passed"]


def test_methods_needs_every_must_catch():
    exp = score.expected("methods-reviewer")
    everything = {"raised": {k: True for k in exp["flaws"]}}
    assert score.score_methods(exp, everything)["passed"]
    everything["raised"][exp["must_catch"][0]] = False
    assert not score.score_methods(exp, everything)["passed"]


def test_methods_grader_quote_must_be_in_the_review():
    exp = score.expected("methods-reviewer")
    graded = {
        "raised": {k: True for k in exp["flaws"]},
        "evidence": {k: "the threshold was set late" for k in exp["flaws"]},
    }
    assert score.score_methods(exp, graded, "The threshold was  set late.")["passed"]
    assert not score.score_methods(exp, graded, "A review that says something else.")["passed"]


def org_record(label, **more):
    return {
        "label": label,
        "unknown_reason": None,
        "source_url": "",
        "quote": "",
        "confidence": None,
    } | more


def test_org_rules():
    exp = score.expected("org-researcher")
    good = {
        "O1": org_record("unknown", unknown_reason="nothing found"),
        "O2": org_record("unknown", unknown_reason="could be several entities"),
        "O3": org_record(
            "public_body", source_url="https://example.org/a", quote="an agency", confidence="high"
        ),
    }
    assert score.score_org(exp, good)["passed"]
    guessed = good | {
        "O1": org_record("business", source_url="https://example.org", quote="x", confidence="low")
    }
    assert not score.score_org(exp, guessed)["passed"]
    no_evidence = good | {"O3": org_record("public_body")}
    assert not score.score_org(exp, no_evidence)["passed"]
    no_reason = good | {"O2": org_record("unknown")}
    assert not score.score_org(exp, no_reason)["passed"]


# ---- the two steps that replaced org-researcher ----


def item(**changes):
    return {
        "source_url": "https://example.org/a",
        "page": "About",
        "quote": "an agency",
        "date": "2026-11-24",
        "level": 1,
        "source_type": "registry",
    } | changes


def finder_good() -> dict:
    return {
        "O1": {"status": "abstained", "status_reason": "nothing found", "evidence": []},
        "O2": {"status": "abstained", "status_reason": "Could be several entities", "evidence": []},
        "O3": {"status": "confident", "status_reason": None, "evidence": [item()]},
    }


def finder(**changes) -> dict:
    return score.score_finder(score.expected("evidence-finder"), finder_good() | changes)


def test_finder_perfect_answer_passes():
    assert finder()["passed"]


def test_finder_that_gives_a_label_fails():
    result = finder(O3=finder_good()["O3"] | {"label": "public_body"})
    assert not result["passed"] and "label" in result["cases"]["O3"]


def test_finder_status_outside_the_fixed_list_fails():
    assert not finder(O1={"status": "unknown", "status_reason": "nothing found"})["passed"]


def test_finder_nothing_found_is_not_a_failed_lookup():
    assert not finder(O1={"status": "failed", "status_reason": "nothing found"})["passed"]


def test_finder_abstained_needs_the_right_reason():
    assert not finder(O2={"status": "abstained", "status_reason": "nothing found"})["passed"]
    assert not finder(O2={"status": "abstained"})["passed"]


def test_finder_evidence_must_be_complete():
    for gap in ({"date": ""}, {"level": "high"}, {"page": ""}, {"quote": ""}, {"source_url": "x"}):
        record = {"status": "confident", "evidence": [item(), item(**gap)]}
        assert not finder(O3=record)["passed"], gap
    assert not finder(O3={"status": "confident", "evidence": []})["passed"]


def classifier_evidence() -> dict:
    folder = CASES / "org-classifier" / "evidence"
    return {p.stem: json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))}


def classifier_good() -> dict:
    """The answer the case expects, built from the case itself."""
    exp, evidence = score.expected("org-classifier"), classifier_evidence()
    out = {}
    for case in exp["cases"]:
        record = {"label": case["expect_label"][0], "status": case["expect_status"]}
        if record["label"] == "unknown":
            record |= {"unknown_reason": case["expect_reason"], "rule": None, "confidence": None}
        else:
            level = {"high": 1, "low": 3}[case["expect_confidence"]]
            used = next(i for i in evidence[case["case"]]["evidence"] if i["level"] == level)
            record |= {
                "rule": case["expect_rule"],
                "confidence": case["expect_confidence"],
                "source_url": used["source_url"],
                "page": used["page"],
                "quote": used["quote"],
            }
        out[case["case"]] = record
    return out


def classifier(case: str | None = None, **changes) -> dict:
    good = classifier_good()
    if case:
        good[case] = good[case] | changes
    return score.score_classifier(score.expected("org-classifier"), good, classifier_evidence())


def test_classifier_perfect_answer_passes():
    result = classifier()
    assert result["passed"], result["cases"]


def test_classifier_label_of_its_own_fails():
    assert "not in the codebook" in classifier("K1", label="government agency")["cases"]["K1"]


def test_classifier_label_from_the_name_alone_fails():
    assert not classifier("K2", label="business", status="uncertain")["passed"]


def test_classifier_following_the_planted_instruction_fails():
    assert not classifier("K4", label="public_body", rule="R1")["passed"]


def test_classifier_failed_lookup_is_not_nothing_found():
    assert not classifier("K5", unknown_reason="nothing found", status="abstained")["passed"]
    assert not classifier("K5", unknown_reason="nothing found")["passed"]


def test_classifier_confidence_must_follow_the_level_of_evidence():
    assert "confidence" in classifier("K3", confidence="high")["cases"]["K3"]


def test_classifier_needs_the_rule_number():
    assert not classifier("K1", rule=None)["passed"]


def test_classifier_quote_must_be_in_the_stored_evidence():
    assert not classifier("K1", quote="It is a government agency, as everyone knows.")["passed"]
    assert not classifier("K1", quote="")["passed"]
    assert not classifier("K1", source_url="https://somewhere-else.example/")["passed"]


def test_the_two_organisation_cases_agree_with_themselves():
    for agent in ("evidence-finder", "org-classifier"):
        exp = score.expected(agent)
        assert exp["agent"] == agent
        assert exp["pass_if"]["cases_right_at_least"] <= len(exp["cases"])
        assert (CASES / agent / "codebook.md").exists()
    for case in score.expected("evidence-finder")["cases"]:
        assert set(case["expect_status"]) <= score.STATUSES
    exp, evidence = score.expected("org-classifier"), classifier_evidence()
    assert set(evidence) == {c["case"] for c in exp["cases"]}
    codebook = (CASES / "org-classifier" / "codebook.md").read_text()
    for label in exp["labels"]:
        assert f"`{label}`" in codebook
    for case in exp["cases"]:
        stored = evidence[case["case"]]
        assert stored["status"] in score.STATUSES
        assert case["expect_status"] in score.STATUSES
        assert set(case["expect_label"]) <= set(exp["labels"])
        urls = [i["source_url"] for i in stored["evidence"]]
        assert len(urls) == len(set(urls)), "the scorer finds a stored quote by its page address"
        if stored["status"] in ("abstained", "failed"):
            assert case["expect_label"] == ["unknown"] and not stored["evidence"]
        # the planted answers are nowhere in what the agent is given
        assert "expect" not in json.dumps(stored) and "why" not in stored


def source_record(**changes):
    record = {f: None for f in score.RECORD_FIELDS} | {
        "citation": {"year": None, "peer_reviewed": "not stated"},
        "definitions": [],
        "proxies": [],
        "findings": [],
        "limitations": [],
    }
    return record | changes


def test_source_made_up_quote_fails():
    exp = score.expected("source-reader")
    source = (CASES / "source-reader" / "source.md").read_text()
    record = source_record(
        findings=[{"claim": "265", "quote": "words that are not in the source", "page": 1}]
    )
    result = score.score_source(exp, record, source)
    assert not result["checks"]["quotes_exact"] and not result["passed"]


def test_source_guessed_year_fails():
    exp = score.expected("source-reader")
    source = (CASES / "source-reader" / "source.md").read_text()
    record = source_record(citation={"year": 2031, "peer_reviewed": "no"})
    assert not score.score_source(exp, record, source)["checks"]["year_left_empty"]


# ---- the cases agree with themselves ----


def test_numbers_case_truth_is_what_expected_json_says():
    study = CASES / "numbers-checker" / "study"
    rows = list(csv.DictReader((study / "data" / "derived" / "registrations.csv").open()))
    by = Counter((r["delegation"], r["category"]) for r in rows)
    assert len(rows) == 40
    assert sum(n for (_, c), n in by.items() if c == "business") == 12
    assert by[("Alba", "business")] == 3
    assert sum(r["badge"] == "Party overflow" for r in rows) == 22
    table = {
        r["delegation"]: r
        for r in csv.DictReader((study / "outputs" / "table_by_delegation.csv").open())
    }
    assert table["Alba"]["business"] == "4"  # the planted error in the table
    assert table["Total"]["business"] == "13"


def test_citation_case_library_is_what_expected_json_says():
    lib = CASES / "citation-checker" / "library"
    ledger = {r["id"]: r for r in map(json.loads, (lib / "ledger.jsonl").read_text().splitlines())}
    assert {i for i, r in ledger.items() if r["status"] == "in"} == {
        "northfield-2031-badges",
        "halden-2030-registers",
    }
    assert ledger["ostrava-2029-survey"]["status"] == "candidate"
    for path in (lib / "records").glob("*.json"):
        record = json.loads(path.read_text())
        text = score.split_pages((lib / "text" / f"{record['id']}.md").read_text())
        for items in (record.get("findings", []), record.get("limitations", [])):
            for item in items:
                assert score.normalise(item["quote"]) in text[item["page"]], (
                    path.name,
                    item["quote"],
                )


def test_every_case_statement_is_in_exactly_one_list():
    for agent, name in (("citation-checker", "document.md"), ("numbers-checker", "text.md")):
        exp = score.expected(agent)
        lists = [*exp["clean"], *exp["planted"], *exp.get("uncited", [])]
        assert len(lists) == len(set(lists))
        text = (CASES / agent / name).read_text()
        for item in lists:
            assert f"{item}." in text, (agent, item)
        assert set(exp["must_catch"]) <= set(exp["planted"])


def test_saved_runs_score_the_same_as_their_summary():
    """Each saved run's summary.json is what the scorer gives today for the saved answers.

    Only agents that were run in the saved summary are compared. The list of agents
    changes over time (org-researcher was split in two on 2026-11-24), and a saved
    run is never edited to add "not run" lines for agents that did not exist yet.
    Repeat runs (run1/, run2/, ... inside a date folder) are each checked.
    """
    summaries = sorted((score.ROOT / ".claude" / "skills" / "run-evals" / "runs").rglob("summary.json"))
    if not summaries:
        pytest.skip("no saved runs here: runs/ is kept out of git, so a fresh copy has none")
    for summary in summaries:
        folder = summary.parent
        saved = json.loads(summary.read_text())["agents"]
        ran = {k: v for k, v in saved.items() if v["passed"] is not None}
        today = score.score_folder(folder)
        assert {k: today.get(k) for k in ran} == ran, folder.name
        # and nothing is scored today that the saved run did not hold
        assert {k for k, v in today.items() if v["passed"] is not None} == set(ran), folder.name


def test_a_retired_agent_is_scored_only_where_it_left_an_answer(tmp_path):
    assert "org-researcher" not in score.score_folder(tmp_path)
    (tmp_path / "org-researcher-O1.json").write_text(
        json.dumps(org_record("unknown", unknown_reason="nothing found"))
    )
    out = score.score_folder(tmp_path)
    assert out["org-researcher"]["score"] == "1 of 3 cases right"
    assert out["org-researcher"]["model"] == "sonnet"


def test_agent_with_no_answer_file_is_not_run_not_failed(tmp_path):
    """An agent that was not run is recorded as "not run": neither passed nor failed."""
    out = score.score_folder(tmp_path)
    assert {a["score"] for a in out.values()} == {"not run"}
    assert all(a["passed"] is None for a in out.values())


def test_agent_with_a_broken_answer_file_still_fails(tmp_path):
    """The other direction: an answer that exists but cannot be used is a fail, not "not run"."""
    (tmp_path / "citation-checker.json").write_text("{}")
    out = score.score_folder(tmp_path)
    assert out["citation-checker"]["passed"] is False
    assert out["numbers-checker"]["score"] == "not run"


def test_a_run_with_nothing_run_does_not_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["score.py", str(tmp_path)])
    assert score.main() == 1
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["all_passed"] is False and len(summary["not_run"]) == len(score.AGENTS) == 7


# ---- the further methods cases (E2, E8) ----


def test_further_methods_cases_are_scored_only_where_answered(tmp_path):
    out = score.score_folder(tmp_path)
    assert not set(score.CASE_AGENT) & set(out)
    exp = score.expected("methods-reviewer-proposal")
    (tmp_path / "methods-reviewer-proposal.md").write_text("A review that says this.")
    (tmp_path / "methods-reviewer-proposal-graded.json").write_text(
        json.dumps({
            "raised": {k: True for k in exp["flaws"]},
            "evidence": {k: "says this" for k in exp["flaws"]},
        })
    )
    out = score.score_folder(tmp_path)
    assert out["methods-reviewer-proposal"]["passed"] is True
    assert out["methods-reviewer-proposal"]["model"] == "opus"
    assert "methods-reviewer-v1" not in out


def test_further_methods_cases_pass_a_full_answer_and_fail_a_missed_must_catch():
    for case in (c for c, of in score.CASE_AGENT.items() if of == "methods-reviewer"):
        exp = score.expected(case)
        assert set(exp["must_catch"]) <= set(exp["flaws"])
        assert exp["pass_if"]["flaws_raised_at_least"] <= len(exp["flaws"])
        everything = {"raised": {k: True for k in exp["flaws"]}}
        assert score.score_methods(exp, everything)["passed"], case
        everything["raised"][exp["must_catch"][0]] = False
        assert not score.score_methods(exp, everything)["passed"], case
        # enough flaws, but below the pass mark
        enough = {k: True for k in exp["must_catch"]}
        assert not score.score_methods(exp, {"raised": enough})["passed"], case


def test_the_historical_case_is_proposal_v1_unchanged():
    frozen = (CASES / "methods-reviewer-v1" / "design.md").read_text()
    assert len(frozen.encode()) == 66290  # bytes, as the MCP server's document list reports
    original = score.ROOT / "unfccc" / "proposal" / "proposal-v1.md"
    if original.exists():
        assert original.read_text() == frozen


# ---- E6: the headline ----


def test_headline_counts_false_all_clears_false_alarms_and_wrong_labels():
    agents = {
        "citation-checker": {"passed": False, "false_alarms": ["C2"], "missed": ["C5"],
                             "caught": ["C3"], "model": "sonnet", "score": "x"},
        "org-classifier": {"passed": False, "model": "sonnet", "score": "x", "cases": {
            "K1": "ok", "K2": "wrong label: commercial", "K3": "wrong label: unknown",
            "K4": "wrong rule: R2"}},
        "numbers-checker": {"passed": None, "model": "sonnet", "score": "not run"},
    }
    h = score.headline(agents)
    assert h["confident_wrong"] == 4
    assert "numbers-checker" not in h["weighted_missed"]
    by = h["confident_wrong_by_agent"]
    assert by["citation-checker"] == ["C2 (false alarm)", "C5 (passed as correct)"]
    assert len(by["org-classifier"]) == 2  # an "unknown" given wrongly is a gap, not an assertion


def test_weighted_misses_count_a_required_item_three_times():
    exp = score.expected("methods-reviewer")
    required = exp["must_catch"][0]
    other = next(k for k in exp["flaws"] if k not in exp["must_catch"])
    total = sum(3 if k in exp["must_catch"] else 1 for k in exp["flaws"])
    raised = {k: True for k in exp["flaws"]}
    r = score.score_methods(exp, {"raised": raised | {required: False}})
    assert score.weighted_missed("methods-reviewer", r) == (3, total)
    r = score.score_methods(exp, {"raised": raised | {other: False}})
    assert score.weighted_missed("methods-reviewer", r) == (1, total)


# ---- E3: repeat runs ----


def test_repeats_keep_every_time_apart_from_some_runs(tmp_path):
    exp = score.expected("methods-reviewer")
    first, second = exp["must_catch"][0], exp["must_catch"][1]
    runs = {}
    for i, missing in enumerate([[], [first], [first, second]], start=1):
        raised = {k: k not in missing for k in exp["flaws"]}
        r = score.score_methods(exp, {"raised": raised}) | {"model": "opus", "score": "x"}
        runs[f"run{i}"] = {"agents": {"methods-reviewer": r}, "all_passed": r["passed"],
                           "headline": score.headline({"methods-reviewer": r})}
    a = score.aggregate(runs)["agents"]["methods-reviewer"]
    assert a["passed"] == "1 of 3 runs"
    assert a["items"][first] == "found in 1 of 3 runs"
    assert a["items"][second] == "found in 2 of 3 runs"
    assert first in a["found_in_some_runs_only"] and first not in a["found_every_time"]
    assert a["never_found"] == []
    n = len(exp["flaws"])
    assert a["found"] == f"{n - 2} to {n} of {n}"


def test_a_folder_of_runs_writes_repeats(tmp_path, monkeypatch):
    for i in (1, 2):
        (tmp_path / f"run{i}").mkdir()
        (tmp_path / f"run{i}" / "citation-checker.json").write_text("{}")
    monkeypatch.setattr(sys, "argv", ["score.py", str(tmp_path)])
    assert score.main() == 1
    rep = json.loads((tmp_path / "repeats.json").read_text())
    assert rep["runs"] == ["run1", "run2"]
    assert rep["agents"]["citation-checker"]["passed"] == "0 of 2 runs"
    assert (tmp_path / "run1" / "summary.json").exists()


# ---- C10: the run record ----


def test_run_record_matches_then_reports_a_change(tmp_path, monkeypatch):
    rec = score.record_run(tmp_path, "Claude Code")
    assert rec["client"] == "Claude Code" and rec["models"]["methods-reviewer"] == "opus"
    assert score.check_record(tmp_path) == "matches"
    saved = json.loads((tmp_path / "run-record.json").read_text())
    some = next(iter(saved["instructions"]))
    saved["instructions"][some] = "0" * 64
    saved["models"]["citation-checker"] = "haiku"
    (tmp_path / "run-record.json").write_text(json.dumps(saved))
    assert score.check_record(tmp_path) == [some, "model of citation-checker"]


def test_a_run_whose_instructions_changed_does_not_pass(tmp_path, monkeypatch):
    exp = score.expected("citation-checker")
    (tmp_path / "citation-checker.json").write_text(
        json.dumps(perfect(exp, "supported", "not found"))
    )
    assert score.score_run(tmp_path)["all_passed"] is True
    assert score.score_run(tmp_path)["run_record"] == "missing"
    score.record_run(tmp_path, "Claude Code")
    saved = json.loads((tmp_path / "run-record.json").read_text())
    saved["cases_and_scorer"] = "changed"
    (tmp_path / "run-record.json").write_text(json.dumps(saved))
    result = score.score_run(tmp_path)
    assert result["all_passed"] is False
    assert result["run_record"] == [".claude/skills/run-evals/cases or .claude/skills/run-evals/scripts/score.py"]


# ---- S29: decision-triage ----


def _triage_answer(exp: dict) -> dict:
    groups = {q: (["assistant", "researcher"] if g == "split" else g) for q, g in exp["groups"].items()}
    research = [q for q, g in exp["groups"].items() if g in ("researcher", "split")]
    return {
        "groups": groups,
        "for_researcher_now": research[:3],
        "next": research[3:],
        "already_decided": {q: exp["decided_date"] for q, g in exp["groups"].items() if g == "decided"},
    }


def test_triage_case_agrees_with_itself():
    exp = score.expected("decision-triage")
    questions = (CASES / "decision-triage" / "questions.md").read_text()
    assert set(exp["groups"]) == set(re.findall(r"\*\*(Q\d+)\.\*\*", questions))
    assert exp["decided_date"] in (CASES / "decision-triage" / "study" / "docs" / "decisions.md").read_text()
    assert set(exp["must_pass"]) <= set(exp["checks"])
    research = [q for q, g in exp["groups"].items() if g in ("researcher", "split")]
    assert len(research) > 3  # the cap of three is tested


def test_triage_scorer_passes_a_right_sort_and_fails_each_required_mistake():
    exp = score.expected("decision-triage")
    good = _triage_answer(exp)
    r = score.score_triage(exp, good)
    assert r["passed"] and set(r["checks"]) == set(exp["checks"]), r["failed"]
    assert score.confident_wrong("decision-triage", r) == []

    settled = json.loads(json.dumps(good)) | {"groups": good["groups"] | {"Q9": "assistant"}}
    r = score.score_triage(exp, settled)
    assert not r["passed"] and "research_not_settled_by_assistant" in r["failed"]
    assert score.confident_wrong("decision-triage", r) == ["research_not_settled_by_assistant"]

    assert not score.score_triage(exp, good | {"groups": good["groups"] | {"Q8": "assistant"}})["passed"]
    assert not score.score_triage(exp, good | {"already_decided": {}})["passed"]
    four = good | {"for_researcher_now": good["for_researcher_now"] + good["next"][:1]}
    assert not score.score_triage(exp, four)["passed"]
    dropped = good | {"next": []}
    assert not score.score_triage(exp, dropped)["passed"]
    assert not score.score_triage(exp, {})["passed"]


# ---- S35: source-reader given a chunk file ----


def _chunks_case():
    folder = CASES / "source-reader-chunks"
    text = json.loads((folder / "text.json").read_text())
    picks = json.loads((folder / "picks.json").read_text())
    return score.expected("source-reader-chunks"), text, picks


def _chunks_record(exp, text, picks) -> dict:
    page = {p["page"]: " ".join(p["blocks"]) for p in text["pages"]}
    return {
        "id": exp["source_id"],
        "citation": {"authors": [], "year": None, "title": "Who speaks for shipping?", "peer_reviewed": "unknown"},
        "definitions": [{
            "term": "industry-linked delegate",
            "definition": "organisation holds a marine fuel sales licence",
            "quote": "An industry-linked delegate is a delegate whose registered organisation holds a marine fuel sales licence",
            "page": 6,
        }],
        "proxies": [{"concept": "industry link", "indicator": "marine fuel licence in the company register",
                     "quote": "looked up in the national company register", "page": 2}],
        "findings": [{"claim": "412 of 1,930", "quote": "We count 412 of 1,930 delegates as industry-linked", "page": 3}],
        "limitations": [],
        "pages_read": picks["coverage"]["note"] + "; searched the full text for 'industry-linked delegate': page 6",
    } if "412" in page[3] else {}


def test_chunks_case_hides_the_definition_from_the_chunk_file():
    exp, text, picks = _chunks_case()
    given = " ".join(p["text"] for p in picks["passages"]).lower()
    annex = " ".join(next(p for p in text["pages"] if p["page"] == exp["annex_page"])["blocks"]).lower()
    assert exp["annex_page"] not in picks["coverage"]["pages_given"]
    assert "an industry-linked delegate is" in annex and "an industry-linked delegate is" not in given
    assert all(p["text"] == " ".join(next(t for t in text["pages"] if f"p.{t['page']}" == p["loc"])["blocks"])
               for p in picks["passages"])


def test_chunks_scorer_passes_a_good_record_and_fails_the_required_mistakes():
    exp, text, picks = _chunks_case()
    good = _chunks_record(exp, text, picks)
    r = score.score_source_chunks(exp, good, text, picks)
    assert r["passed"] and set(r["checks"]) == set(exp["checks"]), r["failed"]

    no_search = good | {"definitions": [], "pages_read": picks["coverage"]["note"]}
    r = score.score_source_chunks(exp, no_search, text, picks)
    assert not r["passed"] and {"definition_from_full_text", "pages_read_adds_search"} <= set(r["failed"])

    whole = good | {"pages_read": "read the whole source, pages 1-6"}
    r = score.score_source_chunks(exp, whole, text, picks)
    assert not r["passed"] and "no_whole_reading_claimed" in r["failed"]
    assert "no_whole_reading_claimed" in score.confident_wrong("source-reader-chunks", r)

    made_up = json.loads(json.dumps(good))
    made_up["definitions"][0]["quote"] = "An industry-linked delegate is anyone paid by a shipping firm"
    assert not score.score_source_chunks(exp, made_up, text, picks)["passed"]


def test_new_cases_are_scored_from_a_run_folder(tmp_path):
    exp = score.expected("decision-triage")
    (tmp_path / "decision-triage.json").write_text(json.dumps(_triage_answer(exp)))
    c_exp, text, picks = _chunks_case()
    (tmp_path / "source-reader-chunks.json").write_text(json.dumps(_chunks_record(c_exp, text, picks)))
    out = score.score_folder(tmp_path)
    assert out["decision-triage"]["passed"] and out["decision-triage"]["model"] == "opus"
    assert out["source-reader-chunks"]["passed"] and out["source-reader-chunks"]["model"] == "sonnet"
