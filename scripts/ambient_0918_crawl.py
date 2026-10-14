#!/usr/bin/env python3
"""Ambient | 2026-09-18 | Deep crawl of the main website to map service URLs.

READ-ONLY. No parameters are sent, so there is no cache-poisoning risk. No form is
submitted, no telephone link activated, nothing is changed.

Sitemaps are behind SG-Captcha (HTTP 202 stub), so this walks the rendered link graph.
"""
from __future__ import annotations
import sys, re, json, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

BASE = "https://ambientcoolingandheating.com"
HOST = "ambientcoolingandheating.com"
MAX_PAGES = 200
SKIP = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|pdf|zip|mp4|css|js|ico|woff2?)$", re.I)
SKIP_PATH = re.compile(r"/(wp-json|wp-admin|wp-content|feed|comment|author|tag)/", re.I)


def norm(u):
    u = urljoin(BASE, u.split("#")[0].split("?")[0])
    p = urlparse(u)
    if p.netloc != HOST:
        return None
    path = p.path
    if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
        path += "/"
    if SKIP.search(path) or SKIP_PATH.search(path):
        return None
    return f"https://{HOST}{path}"


def load(page, url):
    """Load one page, tolerating the SG-Captcha 202 -> redirect dance."""
    last = None
    for _ in range(3):
        try:
            r = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            last = r.status if r else None
            page.wait_for_timeout(2500)
            n = page.evaluate("() => document.documentElement.outerHTML.length")
            if n > 20000:
                return last, True
            page.wait_for_timeout(2500)
        except Exception:
            page.wait_for_timeout(1500)
    return last, False


def main():
    seen, queue, out = set(), [BASE + "/"], {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="en-US",
                            timezone_id="America/New_York")
        page = ctx.new_page()
        while queue and len(out) < MAX_PAGES:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            status, ok = load(page, url)
            if not ok:
                out[url] = {"status": status, "loaded": False}
                print(f"  [{len(out):3d}] SKIP  {status}  {url.replace(BASE, '') or '/'}")
                continue
            d = page.evaluate("""() => ({
                title: document.title || '',
                h1: [...document.querySelectorAll('h1')].map(e=>e.innerText.trim()).slice(0,3),
                h2: [...document.querySelectorAll('h2')].map(e=>e.innerText.trim()).slice(0,12),
                links: [...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')),
                text: (document.body?document.body.innerText:'').slice(0, 6000)
            })""")
            out[url] = {"status": status, "loaded": True, "title": d["title"],
                        "h1": d["h1"], "h2": d["h2"], "text_len": len(d["text"]),
                        "text": d["text"][:2500]}
            print(f"  [{len(out):3d}] OK    {status}  {url.replace(BASE, '') or '/'}"
                  f"   | {d['title'][:52]}")
            for h in d["links"]:
                n = norm(h)
                if n and n not in seen and n not in queue:
                    queue.append(n)
        ctx.close(); b.close()

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / "site-crawl-2026-09-18.json"
    p.write_text(json.dumps(
        {"generated_local": datetime.datetime.now(TZ).isoformat(), "base": BASE,
         "read_only": True, "parameters_sent": 0, "forms_submitted": 0,
         "pages_crawled": len(out), "pages": out}, indent=1, default=str),
        encoding="utf-8")
    loaded = {u: v for u, v in out.items() if v.get("loaded")}
    print(f"\ncrawled {len(out)} URLs, {len(loaded)} loaded OK")
    print(f"under /services/: {sum(1 for u in loaded if '/services/' in u)}")
    print(f"WROTE {p}")


if __name__ == "__main__":
    main()
