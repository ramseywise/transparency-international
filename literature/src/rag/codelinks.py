"""Find the code and data that go with a source: links to GitHub, GitLab, Zenodo,
OSF, Dataverse, Figshare, Hugging Face and similar, as printed in the source itself.

Only text already in the library is read (data/processed/text/<id>.json); nothing is
sent anywhere. A link found this way is evidence that the authors published code
or data, with the page it is on. Not finding one is not evidence that there is
none: the source may be abstract-only here, or link from a separate appendix.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from rag import paths

# host -> what it usually holds
HOSTS = {
    "github.com": "code", "gitlab.com": "code", "bitbucket.org": "code", "codeocean.com": "code",
    "huggingface.co": "code or data", "zenodo.org": "data", "osf.io": "data",
    "figshare.com": "data", "dataverse.harvard.edu": "data", "dataverse.nl": "data",
    "datadryad.org": "data", "kaggle.com": "data", "data.mendeley.com": "data",
    "icpsr.umich.edu": "data", "openicpsr.org": "data", "dataverse.org": "data",
}
# DOI prefixes registered by data repositories
DOI_PREFIXES = {"10.5281": "data", "10.7910": "data", "10.17605": "data",
                "10.6084": "data", "10.5061": "data", "10.3886": "data", "10.17632": "data"}
_URL = re.compile(r"https?://[^\s<>\"'()\[\]{}]+", re.I)
# a bare github.com/owner/repo without the scheme, as often printed in footnotes
_BARE = re.compile(r"(?<![\w/.])((?:github|gitlab)\.com/[\w.-]+/[\w.-]+)", re.I)
# pages about the host itself (help, docs, a user's profile), not a project on it
_NOT_A_PROJECT = re.compile(
    r"^/(?:|about|features|pricing|login|join|search|topics|explore|contact|help|docs|site|blog)(?:/.*)?$", re.I)
# the source says the code or data are its own, not a tool it used
_OWN = re.compile(
    r"(?:code|data|datasets|materials|scripts|replication)\W+(?:\w+\W+){0,6}?(?:is|are)?\W*(?:publicly\W+)?"
    r"(?:available|can be found|deposited|released|shared)"
    r"|our (?:public |github |code )?(?:code|data|repository|replication)"
    r"|(?:code|data) availability|analysis code for|replication (?:package|files|data|materials)"
    r"|we (?:release|publish|share|make available)", re.I)


def kind_of(url: str) -> str | None:
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    if host in ("doi.org", "dx.doi.org"):
        prefix = parts.path.strip("/").split("/")[0]
        return DOI_PREFIXES.get(prefix)
    for h, kind in HOSTS.items():
        if host == h or host.endswith("." + h):
            path = parts.path.rstrip("/") or "/"
            if _NOT_A_PROJECT.match(path):
                return None
            if h in ("github.com", "gitlab.com", "bitbucket.org", "huggingface.co") and \
                    len([s for s in path.split("/") if s]) < 2:
                return None  # a person or organisation page, not a repository
            if h == "zenodo.org" and not re.match(r"^/(?:records?|doi|communities)/", path):
                return None
            return kind
    return None


def _clean(url: str) -> str:
    url = url.rstrip(".,;:")
    parts = urlsplit(url)
    if parts.netloc.lower().removeprefix("www.") in ("github.com", "gitlab.com"):
        # the repository is owner/name; deeper paths (a file, a branch) point into it
        segs = [s for s in parts.path.split("/") if s][:2]
        url = f"https://{parts.netloc.lower()}/" + "/".join(segs)
        url = re.sub(r"\.git$", "", url)
    m = re.match(r"https?://files\.osf\.io/v1/resources/(\w+)", url)
    if m:  # a file inside an OSF project: the project is the citable unit
        url = f"https://osf.io/{m.group(1)}"
    return url


def find(doc: dict) -> list[dict]:
    """[{url, kind, own, page, context}] for each distinct code or data link in one source.
    own is True when the words around the link say the material is the source's own
    (\"code available at\", \"replication data\"); False means only that the
    words do not say so: it may be a tool or dataset the source used."""
    found: dict[str, dict] = {}

    def keep(url, page, context):
        url = _clean(url)
        kind = kind_of(url)
        if kind and url.lower().replace("://dx.doi.org", "://doi.org") not in found:
            url = url.replace("://dx.doi.org", "://doi.org")
            found[url.lower()] = {"url": url, "kind": kind, "own": bool(_OWN.search(context or "")),
                                  "page": page, "context": (context or "")[:200]}

    for link in doc.get("links") or []:
        keep(link.get("url") or "", link.get("page"), link.get("context") or link.get("anchor"))
    for p in doc.get("pages") or []:
        prev = ""
        for b in p.get("blocks") or []:
            text = b if isinstance(b, str) else str(b)
            # the block is the context, so a neighbouring sentence cannot lend its wording;
            # a short heading just above ("Code availability") counts
            context = (prev + " " + text) if len(prev) < 40 and _OWN.search(prev) else text
            for m in _URL.finditer(text):
                keep(m.group(0), p.get("page"), context)
            for m in _BARE.finditer(text):
                keep("https://" + m.group(1), p.get("page"), context)
            prev = text
    return list(found.values())


def scan(root: Path | str = "literature") -> dict[str, list[dict]]:
    """{source id: its code and data links} for every extracted source that has any."""
    out = {}
    for path in sorted((Path(root) / paths.TEXT).glob("*.json")):
        links = find(json.loads(path.read_text()))
        if links:
            out[path.stem] = links
    return out
