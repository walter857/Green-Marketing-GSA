"""Read-only landing-page reading for service discovery.

HTTP GET only. This module never posts a form, never submits a lead, never
triggers a chat widget, and never changes a website. It reads the public page a
Google Ads final URL points at and extracts the headings and service text a
human would see.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse

DEFAULT_TIMEOUT_SECONDS = 20
MAX_RESPONSE_BYTES = 2_000_000
MAX_SERVICE_TEXT_CHARS = 6_000
USER_AGENT = (
    "GreenMarketingGSA-ServiceDiscovery/1.0 (read-only; GET only; no forms submitted)"
)
SKIPPED_TAGS = {"script", "style", "noscript", "template", "svg", "iframe"}
HEADING_TAGS = {"h1", "h2", "h3"}


class LandingPageError(RuntimeError):
    pass


@dataclass
class PageReadout:
    url: str
    ok: bool = False
    status_code: int | None = None
    final_url: str = ""
    canonical_url: str = ""
    title: str = ""
    meta_description: str = ""
    h1: list[str] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    service_text: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.canonical_url = ""
        self.meta_description = ""
        self.h1: list[str] = []
        self.headings: list[str] = []
        self._skip_depth = 0
        self._capture: str | None = None
        self._buffer: list[str] = []
        self._body: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered in SKIPPED_TAGS:
            self._skip_depth += 1
            return
        attributes = {key.lower(): (value or "") for key, value in attrs}
        if lowered == "link" and "canonical" in attributes.get("rel", "").lower():
            self.canonical_url = attributes.get("href", "").strip()
        if lowered == "meta" and attributes.get("name", "").lower() == "description":
            self.meta_description = attributes.get("content", "").strip()
        if lowered == "title" or lowered in HEADING_TAGS:
            self._capture = lowered
            self._buffer = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered in SKIPPED_TAGS:
            return
        self.handle_starttag(tag, attrs)
        if self._capture == lowered:
            self._capture = None
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in SKIPPED_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._capture and lowered == self._capture:
            text = " ".join("".join(self._buffer).split())
            if text:
                if lowered == "title":
                    self.title = self.title or text
                elif lowered == "h1":
                    self.h1.append(text)
                else:
                    self.headings.append(text)
            self._capture = None
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._capture:
            self._buffer.append(data)
        stripped = data.strip()
        if stripped:
            self._body.append(stripped)

    def body_text(self) -> str:
        return " ".join(" ".join(self._body).split())


def parse_page(html: str, *, url: str = "", final_url: str = "") -> PageReadout:
    """Parse already-fetched HTML. No network access happens here."""

    parser = _PageParser()
    parser.feed(html)
    parser.close()
    canonical = parser.canonical_url
    if canonical and final_url:
        canonical = urljoin(final_url, canonical)
    return PageReadout(
        url=url,
        ok=True,
        final_url=final_url or url,
        canonical_url=canonical,
        title=parser.title,
        meta_description=parser.meta_description,
        h1=parser.h1,
        headings=parser.headings[:60],
        service_text=parser.body_text()[:MAX_SERVICE_TEXT_CHARS],
    )


def _assert_readable_url(url: str, allowed_hosts: Iterable[str] | None) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise LandingPageError(f"Refusing a non-http(s) URL: {url}")
    if not parsed.netloc:
        raise LandingPageError(f"Refusing a URL without a host: {url}")
    hosts = {str(host).casefold() for host in (allowed_hosts or []) if str(host).strip()}
    if hosts and parsed.netloc.casefold() not in hosts:
        raise LandingPageError(
            f"Refusing {parsed.netloc}: it is not one of the account's own final-URL hosts."
        )
    return url


def read_landing_page(
    url: str,
    *,
    allowed_hosts: Iterable[str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    session: Any | None = None,
) -> PageReadout:
    """GET one public page and return its visible headings and service text."""

    try:
        target = _assert_readable_url(str(url).strip(), allowed_hosts)
    except LandingPageError as exc:
        return PageReadout(url=str(url), ok=False, error=str(exc))

    try:
        import requests
    except ImportError as exc:  # pragma: no cover - requests is a declared dependency
        return PageReadout(url=target, ok=False, error=f"requests is not installed: {exc}")

    getter = session.get if session is not None else requests.get
    try:
        response = getter(
            target,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        )
    except Exception as exc:  # network errors must not stop a discovery run
        return PageReadout(url=target, ok=False, error=f"{type(exc).__name__}: {exc}")

    status = getattr(response, "status_code", None)
    final_url = str(getattr(response, "url", target) or target)
    content_type = ""
    headers = getattr(response, "headers", {}) or {}
    try:
        content_type = str(headers.get("Content-Type", ""))
    except AttributeError:
        content_type = ""
    if status is None or int(status) >= 400:
        return PageReadout(
            url=target,
            ok=False,
            status_code=status,
            final_url=final_url,
            error=f"HTTP {status}",
        )
    if content_type and "html" not in content_type.casefold():
        return PageReadout(
            url=target,
            ok=False,
            status_code=status,
            final_url=final_url,
            error=f"Skipped non-HTML content type: {content_type}",
        )

    text = getattr(response, "text", "") or ""
    readout = parse_page(text[:MAX_RESPONSE_BYTES], url=target, final_url=final_url)
    readout.status_code = int(status)
    return readout


def read_landing_pages(
    urls: Iterable[str],
    *,
    allowed_hosts: Iterable[str] | None = None,
    max_pages: int = 8,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    session: Any | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for url in urls:
        if len(results) >= max_pages:
            break
        key = str(url).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        results.append(
            read_landing_page(
                key, allowed_hosts=allowed_hosts, timeout=timeout, session=session
            ).to_dict()
        )
    return results


def hosts_from_urls(urls: Iterable[str]) -> list[str]:
    hosts: list[str] = []
    for url in urls:
        netloc = urlparse(str(url)).netloc.casefold()
        if netloc and netloc not in hosts:
            hosts.append(netloc)
    return hosts
