"""Open web pages, keep their text as the snapshot, and choose the part a model reads.

Every page is fetched by code, not by the model, and its text is saved with the date
it was opened. That saved text is the snapshot rule 2 asks for, and it is what the
quote check compares against: a quote counts only if it is on the page we fetched.

The model is shown the opening of each page and the paragraphs that mention the
organisation's name, not the whole page; the check still uses the whole text.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

USER_AGENT = "research-organisation-lookup/0.1 (public-interest research; httpx)"
MAX_BYTES = 5_000_000
TIMEOUT = 20.0
HEAD_WORDS = 1500
PAGE_WORDS = 3000
LOGIN = re.compile(r"/(login|log-in|signin|sign-in|sso|auth|account/login)\b", re.I)
SKIP_TAGS = ("script", "style", "noscript", "svg", "nav", "footer", "form", "header")


def today() -> str:
    return dt.date.today().isoformat()


def _key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:24]


def safe_url(url: str) -> bool:
    """Only public http(s) addresses: no files, no local or private hosts."""
    try:
        u = urlparse(url)
    except ValueError:
        return False
    if u.scheme not in ("http", "https") or not u.hostname:
        return False
    host = u.hostname.lower()
    if host in ("localhost",) or host.endswith(".local") or host.endswith(".internal"):
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True
    return ip.is_global


def html_text(raw: bytes, encoding: str | None = None) -> tuple[str, str | None]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw, "lxml", from_encoding=encoding)
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    for tag in soup(SKIP_TAGS):
        tag.decompose()
    lines = [ln.strip() for ln in soup.get_text("\n").splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    return text, title


def pdf_text(raw: bytes) -> str:
    import pymupdf

    with pymupdf.open(stream=raw, filetype="pdf") as doc:
        return "\n\n".join(f"[page {i + 1}]\n{p.get_text()}" for i, p in enumerate(doc))


def looks_like_login(url: str, text: str) -> bool:
    if LOGIN.search(urlparse(url).path):
        return True
    head = text[:3000].lower()
    return ("password" in head and ("sign in" in head or "log in" in head)
            and len(text.split()) < 400)


def json_text(value) -> str:
    """The values of a JSON document as lines of text, keys kept beside their values."""
    lines: list[str] = []

    def walk(v, key=""):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, list):
            for x in v:
                walk(x, key)
        elif v is not None:
            lines.append(f"{key}: {v}" if key else str(v))

    walk(value)
    return "\n".join(lines)


def fetch(url: str, client: httpx.Client, cache: Path | None = None) -> dict:
    """The page at `url` as {url, final_url, kind, title, text, fetched, ok, error}.

    A saved copy is used if there is one, so a resumed run quotes the same text."""
    if cache is not None:
        path = cache / f"{_key(url)}.json"
        if path.exists():
            return json.loads(path.read_text())
    page = _fetch(url, client)
    if cache is not None and (page["ok"] or page["error"] != "network"):
        cache.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(page, ensure_ascii=False))
    return page


def _fetch(url: str, client: httpx.Client) -> dict:
    page = {"url": url, "final_url": url, "kind": None, "title": None, "text": "",
            "fetched": today(), "ok": False, "error": None}
    if not safe_url(url):
        page["error"] = "not a public web address"
        return page
    try:
        with client.stream("GET", url, follow_redirects=True, timeout=TIMEOUT) as r:
            page["final_url"] = str(r.url)
            if not safe_url(page["final_url"]):
                page["error"] = "redirected to a non-public address"
                return page
            if r.status_code >= 400:
                page["error"] = f"HTTP {r.status_code}"
                return page
            raw = b""
            for chunk in r.iter_bytes():
                raw += chunk
                if len(raw) > MAX_BYTES:
                    page["error"] = "larger than 5 MB"
                    return page
            ctype = r.headers.get("content-type", "").lower()
            encoding = r.encoding
    except httpx.HTTPError as e:
        page["error"] = "network"
        page["detail"] = type(e).__name__
        return page
    if "pdf" in ctype or raw[:5] == b"%PDF-":
        page["kind"] = "pdf"
        try:
            page["text"] = pdf_text(raw)
        except Exception as e:  # a broken PDF is a failed page, not a failed run
            page["error"] = f"unreadable PDF ({type(e).__name__})"
            return page
    elif "html" in ctype or "xml" in ctype or not ctype:
        page["kind"] = "html"
        page["text"], page["title"] = html_text(raw, encoding)
    elif "json" in ctype or ctype.startswith("text/plain"):
        # Register APIs (for example the Czech ARES) answer in JSON: keep its values as text,
        # with escaped characters decoded, so a quoted register field can be found.
        page["kind"] = "data"
        text = raw.decode(encoding or "utf-8", errors="replace")
        if "json" in ctype:
            try:
                text = json_text(json.loads(text))
            except ValueError:
                pass
        page["text"] = text
    else:
        page["error"] = f"not a page or PDF ({ctype})"
        return page
    if looks_like_login(page["final_url"], page["text"]):
        page["error"] = "needs a login"
        page["text"] = ""
        return page
    if not page["text"].strip():
        page["error"] = "no text"
        return page
    page["ok"] = True
    return page


def _name_tokens(names: list[str]) -> list[str]:
    """Distinctive words of the names: 4+ letters, or an acronym of 2+ capitals."""
    out = set()
    for n in names:
        for w in re.findall(r"[^\W\d_][\w&'-]*", n):
            if len(w) >= 4 or (len(w) >= 2 and w.isupper()):
                out.add(w.lower())
    stop = {"gmbh", "group", "company", "limited", "association", "international", "the",
            "national", "foundation", "institute", "and", "for"}
    return sorted(out - stop)


def excerpt(text: str, names: list[str], head: int = HEAD_WORDS, limit: int = PAGE_WORDS) -> str:
    """The opening `head` words, then the paragraphs that name the organisation, to `limit`."""
    words = text.split()
    if len(words) <= limit:
        return text
    paras = [p for p in re.split(r"\n+", text) if p.strip()]
    out, used = [], 0
    for p in paras:
        n = len(p.split())
        if used + n > head:
            break
        out.append(p)
        used += n
    tokens = _name_tokens(names)
    shown = set(range(len(out)))
    for i, p in enumerate(paras):
        if i in shown:
            continue
        low = p.lower()
        if tokens and any(t in low for t in tokens):
            n = len(p.split())
            if used + n > limit:
                continue
            out.append("[...]\n" + p)
            used += n
    return "\n".join(out) + "\n[... the rest of the page is not shown]"


def needs_browser(page: dict) -> str | None:
    """Why a fetched HTML page holds no content to check against, or None.

    Some sites send code a cookie-consent screen, or an empty shell that a browser fills in.
    The agent's reader may have seen the real text, so a quote missing from such a page is
    "could not check", never "wrong"."""
    if page.get("kind") != "html":
        return None
    text = page.get("text") or ""
    n = len(text.split())
    title = (page.get("title") or "").strip()
    shell = {title.lower(), "skip to main content", "skip to content"}
    if n < 3 or not [ln for ln in text.splitlines() if ln.strip().lower() not in shell]:
        return "nothing but the title: the page needs a browser"
    if n < 400 and "cookie" in text[:1500].lower():
        return "only a cookie-consent screen"
    return None


def normalise(s: str) -> str:
    """For comparing a quote with a page: one kind of space, quote mark and dash; no case."""
    s = s.replace("­", "")
    s = re.sub(r"[‘’‚‛′`´]", "'", s)
    s = re.sub(r"[“”„‟″«»]", '"', s)
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"-\s*\n\s*", "", s)  # words broken across lines in PDFs
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_on_page(quote: str, page_text: str) -> bool:
    q = normalise(quote).strip(" .\"'")
    if not q:
        return False
    page = normalise(page_text)
    if q in page:
        return True
    # HTML breaks lines inside inline markup ("\nName\n", "LEGMC\n)"): same characters, spacing ignored
    tight = lambda s: re.sub(r"\s+", "", s)
    if tight(q) in tight(page):
        return True
    # Encyclopaedia footnote markers inside a sentence ("party [5] [6] ."), which a quote leaves out
    unmark = lambda s: tight(re.sub(r"\[\s*(\d+|[a-z]|note \d+|citation needed)\s*\]", "", s))
    return unmark(q) in unmark(page)
