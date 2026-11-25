"""Polite downloading of web pages and PDFs into the literature folder.

Raw downloads are written once and never overwritten:
  data/raw/pages/<id>.html     web pages, exactly as served
  data/raw/pdfs/<id>.pdf       PDF files
  fetch-log.jsonl              one line per download: URL, date, checksum
The export step (views.sort) later moves each file into its topic folder.

(all inside one library's folder, literature/<study>/)
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from rag import paths

USER_AGENT = "research-crawler/0.1"
MIN_DELAY_SECONDS = 2.0
MAX_BYTES = 60 * 1024 * 1024
# Query parameters that act as access tokens. Kept out of every file we write.
SECRET_PARAMS = {"x-craft-preview", "token", "access_token", "key"}
TRACKING_PREFIXES = ("utm_",)
TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def tidy_url(url: str) -> str:
    """Drop the sentence punctuation that a printed reference leaves on a link.

    A reference list prints "https://example.org/report/." and the PDF stores
    the full stop as part of the link. No real address ends in one. Brackets
    are kept: some DOIs end in ")".
    """
    return url.strip().rstrip(".,;")


def normalise_url(url: str) -> str:
    """Canonical form used to recognise the same link twice."""
    parts = urlsplit(tidy_url(url))
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k not in TRACKING_PARAMS and not k.startswith(TRACKING_PREFIXES)
    ]
    path = parts.path or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def match_key(url: str) -> str:
    """A looser form, used only to ask "do we already hold this document?".

    http and https, a leading www., a trailing slash and upper or lower case in
    the host all point to the same document in practice. The key is never
    stored or cited; the address as given is.
    """
    parts = urlsplit(normalise_url(redact_url(url)))
    host = parts.netloc.removeprefix("www.")
    path = parts.path.rstrip("/") or "/"
    if host in ("doi.org", "dx.doi.org"):
        return "doi:" + path.strip("/").lower()
    return host + path + ("?" + parts.query if parts.query else "")


def redact_url(url: str) -> str:
    """The URL with any access token removed, safe to store and cite."""
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k.lower() not in SECRET_PARAMS]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def has_secret(url: str) -> bool:
    return any(k.lower() in SECRET_PARAMS for k, _ in parse_qsl(urlsplit(url).query, keep_blank_values=True))


class Robots:
    """robots.txt rules for one site, including * and $ patterns."""

    def __init__(self, text: str | None, allow_all: bool = True):
        self.rules: list[tuple[bool, re.Pattern]] = []
        self.allow_all = allow_all
        if text:
            self._parse(text)

    def _parse(self, text: str) -> None:
        groups: dict[str, list[tuple[bool, str]]] = {}
        agents: list[str] = []
        in_rules = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            field, value = (s.strip() for s in line.split(":", 1))
            field = field.lower()
            if field == "user-agent":
                if in_rules:
                    agents, in_rules = [], False
                agents.append(value.lower())
                groups.setdefault(value.lower(), [])
            elif field in ("allow", "disallow"):
                in_rules = True
                if value:
                    for a in agents:
                        groups[a].append((field == "allow", value))
        ours = USER_AGENT.split("/")[0].lower()
        chosen = groups.get(ours, groups.get("*", []))
        for allow, pattern in chosen:
            rx = re.escape(pattern).replace(r"\*", ".*")
            if rx.endswith(r"\$"):
                rx = rx[:-2] + "$"
            self.rules.append((allow, re.compile(rx)))
        self.rules.sort(key=lambda r: len(r[1].pattern), reverse=True)

    def allowed(self, url: str) -> bool:
        if not self.rules:
            return self.allow_all
        parts = urlsplit(url)
        target = parts.path or "/"
        if parts.query:
            target += "?" + parts.query
        for allow, rx in self.rules:
            if rx.match(target):
                return allow
        return True


@dataclass
class Fetched:
    id: str
    url: str  # redacted
    final_url: str  # redacted
    status: int | None
    kind: str | None  # html | pdf | other
    content_type: str | None
    path: str | None
    sha256: str | None
    bytes: int | None
    retrieved: str
    note: str = ""
    duplicate_of: str | None = None  # id of the source that already holds this document

    @property
    def ok(self) -> bool:
        return self.path is not None and self.duplicate_of is None


class Fetcher:
    def __init__(self, root: Path | str = "literature", delay: float = MIN_DELAY_SECONDS,
                 transport: httpx.BaseTransport | None = None):
        self.root = Path(root)
        self.delay = delay
        # transport is only for tests (httpx.MockTransport); None means the real network
        self.client = httpx.Client(
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.5"},
            follow_redirects=True,
            timeout=40,
            transport=transport,
        )
        self._robots: dict[str, Robots] = {}
        self._last: dict[str, float] = {}

    @property
    def log_path(self) -> Path:
        return self.root / paths.FETCH_LOG

    def _wait(self, host: str) -> None:
        gap = time.monotonic() - self._last.get(host, 0.0)
        if gap < self.delay:
            time.sleep(self.delay - gap)
        self._last[host] = time.monotonic()

    def robots(self, url: str) -> Robots:
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            self._wait(parts.netloc)
            try:
                r = self.client.get(origin + "/robots.txt")
                if r.status_code == 200:
                    self._robots[origin] = Robots(r.text)
                elif r.status_code in (401, 403) or r.status_code >= 500:
                    self._robots[origin] = Robots(None, allow_all=False)
                else:
                    self._robots[origin] = Robots(None)
            except httpx.HTTPError:
                self._robots[origin] = Robots(None, allow_all=False)
        return self._robots[origin]

    def existing(self, id: str) -> Fetched | None:
        """The earlier download of this id, if there is one."""
        if not self.log_path.exists():
            return None
        found = None
        for line in self.log_path.read_text().splitlines():
            rec = json.loads(line)
            if rec["id"] == id and rec.get("path") and Path(rec["path"]).exists():
                found = rec
        return Fetched(**found) if found else None

    def held(self, url: str | None = None, sha256: str | None = None, not_id: str | None = None) -> dict | None:
        """A download already in the library under another id: the same address
        (as given or after redirects, compared loosely) or the same bytes."""
        if not self.log_path.exists():
            return None
        key = match_key(url) if url else None
        for line in self.log_path.read_text().splitlines():
            rec = json.loads(line)
            if rec["id"] == not_id or not rec.get("path") or rec.get("duplicate_of"):
                continue
            if not Path(rec["path"]).exists():
                continue
            if sha256 and rec.get("sha256") == sha256:
                return rec
            # a file supplied by hand has no address: it can match only by its bytes
            if key and key in {match_key(u) for u in (rec.get("url"), rec.get("final_url")) if u}:
                return rec
        return None

    def fetch(self, url: str, id: str) -> Fetched:
        today = date.today().isoformat()
        safe = redact_url(url)
        prior = self.existing(id)
        if prior:
            prior.note = "already downloaded; not fetched again"
            return prior

        def fail(note: str, status=None, final=safe, ctype=None) -> Fetched:
            rec = Fetched(id, safe, final, status, None, ctype, None, None, None, today, note)
            self._log(rec)
            return rec

        def duplicate(of: dict, why: str, status=None, final=safe, ctype=None) -> Fetched:
            rec = Fetched(id, safe, final, status, of.get("kind"), ctype, of["path"], of.get("sha256"),
                          of.get("bytes"), today, f"{why} as {of['id']}; not stored twice", of["id"])
            self._log(rec)
            return rec

        same = self.held(url=safe, not_id=id)
        if same:
            return duplicate(same, "this address is already in the library")

        try:  # a reference copied badly ("https://doi:10.1088/...") must fail alone, not stop a batch
            scheme = urlsplit(url).scheme
            httpx.URL(url)
        except (ValueError, httpx.InvalidURL):
            return fail("not a valid web address")
        if scheme not in ("http", "https"):
            return fail("not a web address")
        if not self.robots(url).allowed(url):
            return fail("the site's robots.txt does not allow automated access to this page")
        self._wait(urlsplit(url).netloc)
        try:
            r = self.client.get(url)
        except httpx.HTTPError as e:
            return fail(f"request failed: {type(e).__name__}")
        final = redact_url(str(r.url))
        ctype = r.headers.get("content-type", "").split(";")[0].strip().lower()
        if r.status_code != 200:
            return fail(f"HTTP {r.status_code}", r.status_code, final, ctype)
        body = r.content
        if len(body) > MAX_BYTES:
            return fail("file larger than 60 MB", 200, final, ctype)
        same = self.held(url=final, sha256=hashlib.sha256(body).hexdigest(), not_id=id)
        if same:
            return duplicate(same, "the same document is already in the library", 200, final, ctype)
        if body[:5] == b"%PDF-" or ctype == "application/pdf":
            kind, path = "pdf", self.root / paths.PDFS / f"{id}.pdf"
        elif "html" in ctype or body[:200].lstrip().lower().startswith((b"<!doctype html", b"<html")):
            kind, path = "html", self.root / paths.PAGES / f"{id}.html"
        else:
            return fail(f"unsupported content type {ctype or 'unknown'}", 200, final, ctype)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "xb") as f:  # x: never overwrite a raw file
                f.write(body)
        except FileExistsError:
            return fail(f"{path} already exists and is not in the fetch log; not overwritten", 200, final, ctype)
        rec = Fetched(
            id, safe, final, 200, kind, ctype,
            str(path),
            hashlib.sha256(body).hexdigest(), len(body), today,
            "fetched with an access token that is not stored" if has_secret(url) else "",
        )
        self._log(rec)
        return rec

    def _log(self, rec: Fetched) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")

    def close(self) -> None:
        self.client.close()
