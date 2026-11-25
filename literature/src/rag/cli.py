"""Command line for a literature library (one per study, in literature/<study>/).

Give --library NAME before the command when there is more than one library.

  uv run python -m rag crawl URL [URL ...] [--id ID] [--depth 1]
  uv run python -m rag fetch ID_OR_URL [...]     download screened-in candidates
  uv run python -m rag add FILE --id ID [--url URL] [--title T]
  uv run python -m rag extract [ID ...]          re-read raw files into literature/<study>/data/processed/text/
  uv run python -m rag links [--kind K] [--host H] [--via ID]
  uv run python -m rag rank [--status candidate] sort cited sources into tiers
  uv run python -m rag screen in|out ID [...] --reason "..." [--question Q1]
  uv run python -m rag index [--no-embed]
  uv run python -m rag search "question" [-k 8] [--source ID]
  uv run python -m rag related "query" [...] [--since 2015] [-n 25]   search OpenAlex; hits become candidates
  uv run python -m rag citations                 fill worldwide citation counts for sources with a DOI
  uv run python -m rag openaccess [ID ...]       find legal open copies and code/data links; write data/private/reports/open-access.md
  uv run python -m rag export                    write data/processed/screening.json, data/private/reports/catalogue.md
  uv run python -m rag check-quotes [ID ...]     every quote in a reading record is in its source
  uv run python -m rag chunks ID [...] [--terms "a" "b"] [--budget N]
                                                 passages for the reader; writes data/processed/reader-picks/
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from collections import Counter
from pathlib import Path

from rag import crawl as crawl_mod
from rag import paths
from rag.fetch import Fetcher
from rag.ledger import Ledger


def cmd_crawl(a) -> None:
    if a.id and len(a.urls) != 1:
        raise SystemExit("--id can only be used with one URL")
    results = crawl_mod.crawl([(u, a.id) for u in a.urls], a.root, a.depth, tuple(a.follow), a.max_pages)
    ok = sum(r["ok"] for r in results)
    print(f"{ok} of {len(results)} pages downloaded and extracted.")


def cmd_fetch(a) -> None:
    root = Path(a.root)
    ledger, fetcher = Ledger(root), Fetcher(root)
    try:
        targets = list(a.targets)
        if a.screened_in:
            targets += [r["id"] for r in ledger.rows if r["status"] == "in" and not r.get("file")]
        if not targets:
            raise SystemExit("nothing to download: name a source, or use --screened-in")
        tally = Counter()
        for target in targets:
            row = ledger.get(target)
            if row is None and "://" in target:
                row = ledger.by_url(target) or ledger.add(target)
            if row is None:
                print(f"  SKIPPED {target}: not in the ledger")
                tally["skipped"] += 1
                continue
            if row["status"] not in ("in", "read") and not a.force:
                print(f"  SKIPPED {row['id']}: status is '{row['status']}', not screened in "
                      f"(screen it in first, or use --force)")
                tally["skipped"] += 1
                continue
            if not row.get("doi_or_url") or "://" not in row["doi_or_url"]:
                print(f"  SKIPPED {row['id']}: no web address on record; it has to be found by hand")
                ledger.add(None, id=row["id"], reason=(row.get("reason") or "") if "no web address" in (row.get("reason") or "")
                           else ((row.get("reason") or "") + " | no web address on record").strip(" |"))
                tally["no address"] += 1
                continue
            got, used = None, None
            for copy in open_copies(row):  # a legal open copy first: publisher pages usually refuse
                got = fetcher.fetch(copy["pdf"], row["id"])
                if got.ok or got.duplicate_of:
                    used = copy
                    break
            if used is None:
                got = fetcher.fetch(row["doi_or_url"], row["id"])
            if got.duplicate_of:
                ledger.add(None, id=row["id"], status="out",
                           reason=f"duplicate: {got.note}")
                print(f"  DUPLICATE {row['id']}: {got.note}")
                tally["duplicate"] += 1
                continue
            if not got.ok:
                tally["failed"] += 1
                ledger.add(None, id=row["id"], reason=f"download failed: {got.note}")
                print(f"  FAILED {row['id']}: {got.note}")
                continue
            doc = crawl_mod.process(row["id"], got.path, row["doi_or_url"], root, ledger)
            if used:
                # page numbers in a manuscript or preprint differ from the published version
                note = (f"open copy: {used['version'] or 'version not stated'}, from "
                        f"{used['host'] or used['pdf']}, licence {used['license'] or 'not stated'}")
                ledger.add(None, id=row["id"], reason=((row.get("reason") or "") + " | " + note).strip(" |"))
            print(f"  {row['id']}: {doc['counts']}" + (f" (open copy, {used['version']})" if used else ""))
            tally["downloaded"] += 1
            ledger.save()
        print(f"Done: {dict(tally)}")
    finally:
        ledger.save()
        fetcher.close()


def open_copies(row: dict) -> list[dict]:
    """The open copies with a direct PDF link that `rag openaccess` recorded for a source."""
    return [c for c in ((row.get("open_access") or {}).get("copies") or []) if c.get("pdf")]


def cmd_add(a) -> None:
    root = Path(a.root)
    ledger = Ledger(root)
    doc = crawl_mod.process(a.id, a.file, a.url, root, ledger, status="in",
                            reason="supplied by the researcher", title=a.title, type=a.type)
    ledger.save()
    print(f"{a.id}: {doc['counts']}")


def cmd_extract(a) -> None:
    root = Path(a.root)
    ledger = Ledger(root)
    rows = [r for r in ledger.rows if r.get("file") and (not a.ids or r["id"] in a.ids)]
    for r in rows:
        doc = crawl_mod.process(r["id"], r["file"], r["doi_or_url"], root, ledger)
        print(f"  {r['id']}: {doc['counts']}")
    ledger.save()


def cmd_links(a) -> None:
    rows = [r for r in Ledger(a.root).rows if r.get("link_kind")]
    if a.kind:
        rows = [r for r in rows if r["link_kind"] == a.kind]
    if a.host:
        rows = [r for r in rows if a.host in (r["doi_or_url"] or "")]
    if a.via:
        rows = [r for r in rows if any(v.startswith(a.via + " ") for v in r["found_via"])]
    if a.status:
        rows = [r for r in rows if r["status"] == a.status]
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return
    print(f"{len(rows)} links. By kind: {dict(Counter(r['link_kind'] for r in rows))}")
    for r in rows:
        print(f"- [{r['status']}] {r['id']}  ({r['link_kind']}, cited {len(r['found_via'])}x)\n"
              f"    {r['doi_or_url']}\n    anchor: {r['anchor']}")


def cmd_rank(a) -> None:
    from rag import rank

    ledger = Ledger(a.root)
    ranked = rank.rank(ledger.rows)
    ledger.save()
    if a.status:
        ranked = [r for r in ranked if r["status"] == a.status]
    print(f"{len(ranked)} cited sources. By tier: "
          f"{dict(sorted(Counter(r['tier'] for r in ranked).items()))}")
    for r in ranked:
        print(f"- T{r['tier']} {rank.TIER_NAMES[r['tier']]} [{r['status']}] {r['id']}\n"
              f"    {r['tier_reason']}\n    {r['doi_or_url'] or r['title']}")


def cmd_screen(a) -> None:
    ledger = Ledger(a.root)
    for id in a.ids:
        if ledger.get(id) is None:
            raise SystemExit(f"no such source: {id}")
        ledger.add(None, id=id, status=a.decision, reason=a.reason, question=a.question)
    ledger.save()
    print(f"{len(a.ids)} marked {a.decision}.")


def cmd_index(a) -> None:
    from rag import index

    print(json.dumps(index.build(a.root, embed=not a.no_embed)))


def cmd_search(a) -> None:
    from rag import index

    hits = index.search(a.query, a.root, a.k, a.source)
    if a.json:
        print(json.dumps(hits, ensure_ascii=False, indent=1, default=float))
        return
    for h in hits:
        where = h["loc"] + (f", section: {h['section']}" if h["section"] else "")
        print(f"\n[{h['source_id']}, {where}]")
        print(textwrap.fill(h["text"], 110, initial_indent="  ", subsequent_indent="  "))


def cmd_related(a) -> None:
    from rag import openalex

    ledger = Ledger(a.root)
    log = []
    with openalex.client() as c:
        for query in a.queries:
            total, works = openalex.search(query, a.since, a.n, c)
            new = 0
            for w in works:
                known = ledger.by_url(w["url"]) is not None
                ledger.add(w["url"], found_by_search=query, **{k: w[k] for k in
                           ("title", "authors", "year", "type", "context", "cited_by_count")})
                new += not known
            log.append({"query": query, "since": a.since, "matches": total, "looked_at": len(works), "new": new})
            print(f"  {query!r}: {total} matches, top {len(works)} looked at, {new} new candidates",
                  file=sys.stderr if a.json else sys.stdout)
    ledger.save()
    if a.json:
        print(json.dumps(log, ensure_ascii=False, indent=1))


def cmd_citations(a) -> None:
    from rag import openalex

    ledger = Ledger(a.root)
    rows = {openalex.doi_of(r["doi_or_url"]): r for r in ledger.rows if openalex.doi_of(r.get("doi_or_url"))}
    with openalex.client() as c:
        counts = openalex.citation_counts(list(rows), c)
    for doi, n in counts.items():
        rows[doi]["cited_by_count"] = n
    ledger.save()
    print(f"{len(rows)} sources with a DOI; citation count found for {len(counts)}.")


def cmd_openaccess(a) -> None:
    from datetime import date

    from rag import codelinks, openalex, openaccess_report

    root = Path(a.root)
    ledger = Ledger(root)
    today = date.today().isoformat()
    if a.ids:
        rows = [ledger.get(i) for i in a.ids]
        if None in rows:
            raise SystemExit(f"no such source: {a.ids[rows.index(None)]}")
    else:  # wanted: screened in, no file yet
        rows = [r for r in ledger.rows if r["status"] == "in" and not r.get("file")]
    by_doi = {openalex.doi_of(r.get("doi_or_url")): r for r in rows if openalex.doi_of(r.get("doi_or_url"))}
    # by title only where there is no address of our own to go on
    by_title = [r for r in rows if not openalex.doi_of(r.get("doi_or_url")) and r.get("title")
                and ("scholar.google." in (r.get("doi_or_url") or "") or "://" not in (r.get("doi_or_url") or ""))]
    looked = Counter()
    with openalex.client() as c:
        found = openalex.open_access(list(by_doi), c)
        for doi, r in by_doi.items():
            looked["by DOI"] += 1
            r["open_access"] = ({"checked": today, "via": "OpenAlex, by DOI", "doi": doi} | found[doi]
                                if doi in found else {"checked": today, "via": "OpenAlex, by DOI",
                                                      "doi": doi, "unknown": "DOI not in OpenAlex"})
        for r in by_title[:a.max_titles]:
            looked["by title"] += 1
            hit = openalex.open_access_by_title(r["title"], c)
            r["open_access"] = ({"checked": today, "via": "OpenAlex, exact title match"} | hit if hit else
                                {"checked": today, "via": "OpenAlex, exact title match",
                                 "unknown": "no single work with exactly this title"})
    for id, links in codelinks.scan(root).items():
        r = ledger.get(id)
        if r is not None:
            r["code_links"] = links
    ledger.save()
    path = openaccess_report.write(root, rows, ledger.rows, today)
    open_n = sum(bool(open_copies(r)) for r in rows)
    print(f"{len(rows)} sources wanted; looked up {dict(looked)}"
          + (f" (another {len(by_title) - a.max_titles} by title next time)" if len(by_title) > a.max_titles else "")
          + f"; open PDF found for {open_n}. Code or data links in "
          f"{sum(bool(r.get('code_links')) for r in ledger.rows)} sources. Report: {path}")


def cmd_export(a) -> None:
    from rag import screening, views

    print(json.dumps(screening.write(a.root) | {"raw_files": views.build(a.root)}))


def cmd_check_quotes(a) -> None:
    from rag import quotes

    res = quotes.check_all(a.root, a.ids or None)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print(f"{res['quotes']} quotes in {res['records']} records: {res['ok']} found, "
          f"{res['wrong_page']} on a different page, {res['not_found']} not found.")
    for p in res["problems"]:
        print(f"  PROBLEM {p['id']}: {p['problem']}")
    for f in res["failures"]:
        print(f"  {f['result'].upper()} {f['id']} {f['field']}[{f['item']}] (page {f['page']}): {f['quote'][:110]}")
    if res["failures"] or res["problems"]:
        raise SystemExit(1)


def cmd_chunks(a) -> None:
    from rag import chunks

    rows = chunks.write(a.ids, a.root, terms=a.terms, budget=a.budget)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return
    for r in rows:
        print(f"{r['id']}: {r['note']}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="rag", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--library", help="the study whose library to use, for example unfccc; "
                                      "not needed while there is only one")
    p.add_argument("--root", help="the library folder itself, in place of --library")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("crawl")
    s.add_argument("urls", nargs="+")
    s.add_argument("--id")
    s.add_argument("--depth", type=int, default=0, choices=[0, 1])
    s.add_argument("--follow", nargs="+", default=["internal"], choices=["internal", "download", "external"])
    s.add_argument("--max-pages", type=int, default=25)
    s.set_defaults(fn=cmd_crawl)

    s = sub.add_parser("fetch")
    s.add_argument("targets", nargs="*")
    s.add_argument("--screened-in", action="store_true",
                   help="every source screened in that has no file yet")
    s.add_argument("--force", action="store_true", help="download even if not screened in")
    s.set_defaults(fn=cmd_fetch)

    s = sub.add_parser("add")
    s.add_argument("file")
    s.add_argument("--id", required=True)
    s.add_argument("--url")
    s.add_argument("--title")
    s.add_argument("--type")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("extract")
    s.add_argument("ids", nargs="*")
    s.set_defaults(fn=cmd_extract)

    s = sub.add_parser("links")
    s.add_argument("--kind", choices=["internal", "download", "external"])
    s.add_argument("--host")
    s.add_argument("--via")
    s.add_argument("--status")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_links)

    s = sub.add_parser("rank")
    s.add_argument("--status")
    s.set_defaults(fn=cmd_rank)

    s = sub.add_parser("screen")
    s.add_argument("decision", choices=["in", "out", "candidate"])
    s.add_argument("ids", nargs="+")
    s.add_argument("--reason", required=True)
    s.add_argument("--question")
    s.set_defaults(fn=cmd_screen)

    s = sub.add_parser("index")
    s.add_argument("--no-embed", action="store_true")
    s.set_defaults(fn=cmd_index)

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=8)
    s.add_argument("--source")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_search)

    s = sub.add_parser("related")
    s.add_argument("queries", nargs="+")
    s.add_argument("--since", type=int, default=2015)
    s.add_argument("-n", type=int, default=25)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_related)

    s = sub.add_parser("citations")
    s.set_defaults(fn=cmd_citations)

    s = sub.add_parser("openaccess")
    s.add_argument("ids", nargs="*", help="default: every source screened in that has no file yet")
    s.add_argument("--max-titles", type=int, default=50,
                   help="title searches per run; the free OpenAlex allowance is small")
    s.set_defaults(fn=cmd_openaccess)

    s = sub.add_parser("export")
    s.set_defaults(fn=cmd_export)

    s = sub.add_parser("check-quotes")
    s.add_argument("ids", nargs="*")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_check_quotes)

    s = sub.add_parser("chunks")
    s.add_argument("ids", nargs="+")
    s.add_argument("--terms", nargs="*", default=None, help="the study's key terms")
    s.add_argument("--budget", type=int, default=4000, help="words per source")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_chunks)

    a = p.parse_args(argv)
    if not a.root:
        try:
            a.root = str(paths.library(a.library))
        except ValueError as e:
            raise SystemExit(f"{e} (use --library NAME)") from None
    a.fn(a)


if __name__ == "__main__":
    main()
