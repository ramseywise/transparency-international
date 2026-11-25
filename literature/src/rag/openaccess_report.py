"""data/private/reports/open-access.md in a library: for the researcher, which wanted sources have a legal
open copy, which need finding by hand (with ready-made search links), and which
sources in the library publish their code or data."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote_plus
from rag import paths

# Search pages only. These sites do not allow automated access, so the links are
# for the researcher to open; nothing here fetches them.
def search_links(title: str) -> str:
    q = quote_plus(f'"{title}"')
    return (f"[Google Scholar](https://scholar.google.com/scholar?q={q}) · "
            f"[ResearchGate](https://www.researchgate.net/search/publication?q={quote_plus(title)}) · "
            f"[CORE](https://core.ac.uk/search?q={q}) · "
            f"[BASE](https://www.base-search.net/Search/Results?lookfor={q})")


def _title(r: dict) -> str:
    return (r.get("title") or r["id"]).replace("|", "/").replace("\n", " ").strip()[:140]


VERSION = {"publishedVersion": "published version", "acceptedVersion": "author's accepted manuscript",
           "submittedVersion": "preprint (before peer review)", None: "version not stated"}


def write(root: Path | str, wanted: list[dict], all_rows: list[dict], today: str) -> Path:
    def oa(r):
        return r.get("open_access") or {}

    with_pdf = [r for r in wanted if any(c.get("pdf") for c in oa(r).get("copies") or [])]
    page_only = [r for r in wanted if r not in with_pdf and oa(r).get("copies")]
    closed = [r for r in wanted if oa(r) and not oa(r).get("copies") and not oa(r).get("unknown")]
    unknown = [r for r in wanted if oa(r).get("unknown")]
    not_looked = [r for r in wanted if not oa(r)]
    L = [f"# Open copies and code links", "",
         f"Made {today} by `rag openaccess` from OpenAlex (an open catalogue of research) "
         "and the text of sources already in the library. Only the DOI or the title was sent; "
         "nothing about the study.", "",
         f"Of {len(wanted)} sources screened in without a file: {len(with_pdf)} have a legal open PDF, "
         f"{len(page_only)} an open web page but no direct PDF, {len(closed)} are known to OpenAlex with no open copy, "
         f"{len(unknown)} could not be matched, and {len(not_looked)} were not looked up "
         "(reports and web pages OpenAlex does not list, or the title search limit).", "",
         "An open copy may be the author's manuscript rather than the journal version: its page numbers "
         "differ, so a quote must cite the version actually read.", ""]

    L += ["## Legal open PDF found", "", "The next `rag fetch` downloads these from the open copy.", "",
          "| Source | Copy | Licence |", "|---|---|---|"]
    for r in with_pdf:
        c = next(c for c in oa(r)["copies"] if c.get("pdf"))
        L.append(f"| {_title(r)} | [{VERSION.get(c['version'], c['version'])}]({c['pdf']}), "
                 f"{c['host'] or 'host not stated'} | {c['license'] or 'not stated'} |")
    L += ["", "## Open web page, no direct PDF", "", "| Source | Page |", "|---|---|"]
    for r in page_only:
        c = oa(r)["copies"][0]
        L.append(f"| {_title(r)} | [{c['host'] or 'open page'}]({c['landing']}) |")
    L += ["", "## To find by hand", "",
          "No open copy known. The links run a title search; ResearchGate and Google Scholar "
          f"often have an author's copy. A file you download goes into `{Path(root) / paths.PDFS}/`; the export step then moves it to its topic folder.", ""]
    for r in closed + unknown:
        why = oa(r).get("unknown") or "no open copy known to OpenAlex"
        L.append(f"- {_title(r)} ({why}): {search_links(r.get('title') or r['id'])}")

    coded = [r for r in all_rows if r.get("code_links")]
    L += ["", "## Code and data published with sources in the library", "",
          "Links printed in each source. \"Own\" means the text says the code or data are the authors' "
          "(for example \"code available at\"); the others are tools or datasets the source used or cited. "
          "A source not listed may still have code: only text already in the library was read.", "",
          "| Source | Link | Own | Page |", "|---|---|---|---|"]
    for r in coded:
        for l in sorted(r["code_links"], key=lambda l: not l["own"]):
            L.append(f"| {_title(r)} | [{l['url'].split('://', 1)[1]}]({l['url']}) ({l['kind']}) | "
                     f"{'yes' if l['own'] else ''} | {l['page'] or ''} |")
    path = Path(root) / paths.OPEN_ACCESS
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n")
    return path
