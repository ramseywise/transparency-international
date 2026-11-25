"""Command line for the look-up script. See lookup/__init__.py and run.py."""

from __future__ import annotations

import argparse
import json
import sys

from . import llm, registries, run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lookup")
    ap.add_argument("step", choices=["evidence", "classify", "check", "status"])
    ap.add_argument("--study", default="unfccc")
    ap.add_argument("--sample", type=int, help="a random sample of this many organisations")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--ids", nargs="*", help="only these org_ids")
    ap.add_argument("--batch", action="store_true", help="classify/check as a batch, half price")
    ap.add_argument("--dry-run", action="store_true", help="count and estimate, call nothing")
    ap.add_argument("--draft", action="store_true",
                    help="allow a codebook below 1.0; results go to data/derived/draft-codebook/")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)

    study = run.Study(run.llm.ROOT / a.study, draft=a.draft)
    if a.step == "status":
        print(json.dumps(run.status(study), indent=1))
        return 0

    cb = run.codebook_for(study, a.draft)
    orgs = run.choose(study.organisations(), a.sample, a.seed, a.ids)

    if a.step == "evidence":
        n = len(run.evidence_todo(study, orgs, cb, llm.agent_model("evidence-finder")))
    elif a.step == "classify":
        todo, _ = run.classify_todo(study, orgs, cb, llm.agent_model("org-classifier"))
        n = sum(1 for _, ev in todo if ev["status"] not in ("failed", "abstained"))
    else:
        n = len(orgs)
    cost = run.estimate(a.step, n, a.batch)
    print(f"{a.step}: {n} organisation(s) need a model call; about ${cost:.2f} at list prices.")
    if a.dry_run:
        return 0

    usage = llm.Usage()
    client = llm.make_client()
    started = run.now()
    if a.step == "evidence":
        with registries.client() as http:
            counts = run.run_evidence(study, orgs, cb, client, http, usage, workers=a.workers)
    elif a.step == "classify":
        counts = run.run_classify(study, orgs, cb, client, usage, batch=a.batch,
                                  workers=a.workers)
    else:
        counts = run.run_check(study, orgs, cb, client, usage, batch=a.batch)
    run.log_run(study, {"step": a.step, "started": started, "finished": run.now(),
                        "client": "script (python -m lookup)", "codebook_version": cb.version,
                        "models": sorted(usage.by_model), "organisations": len(orgs),
                        "batch": a.batch, "draft": a.draft, "counts": counts,
                        "usage": usage.as_dict()})
    print(json.dumps({"counts": counts, "usage": usage.as_dict()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
