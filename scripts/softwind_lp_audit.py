#!/usr/bin/env python3
"""Read-only landing-page audit with a real browser (Softwind Power Washing).

Uses Playwright because this client's pages are behind SG-Captcha, which serves
non-JS clients an empty stub. curl or a plain fetch produces false "no tracking"
findings on these hosts.

Read-only: GET navigations only. No form is submitted, no call is placed, nothing
on the site is modified.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

UA_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

TRACKER_PATTERNS = {
    "google_ads_gtag": re.compile(r"AW-\d{9,12}"),
    "google_tag_gt": re.compile(r"\bGT-[A-Z0-9]{6,12}\b"),
    "ga4_measurement": re.compile(r"\bG-[A-Z0-9]{8,12}\b"),
    "gtm_container": re.compile(r"\bGTM-[A-Z0-9]{5,9}\b"),
    "google_conversion_label": re.compile(r"AW-\d{9,12}/[A-Za-z0-9_-]{8,}"),
    "whatconverts": re.compile(r"whatconverts", re.I),
    "clickcease": re.compile(r"clickcease", re.I),
    "callrail": re.compile(r"callrail", re.I),
    "facebook_pixel": re.compile(r"connect\.facebook\.net|fbq\(", re.I),
    "hotjar": re.compile(r"hotjar", re.I),
}
PHONE_RE = re.compile(r"\(?\b(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})\b")
MARKET_RE = {
    "islip": re.compile(r"\bislip\b", re.I),
    "west_islip": re.compile(r"west\s*islip", re.I),
    "dix_hills": re.compile(r"dix\s*hills", re.I),
    "long_island": re.compile(r"long\s*island", re.I),
    "power_washing": re.compile(r"power\s*wash", re.I),
    "pressure_washing": re.compile(r"pressure\s*wash", re.I),
    "soft_washing": re.compile(r"soft\s*wash", re.I),
    "house_washing": re.compile(r"house\s*wash", re.I),
    "driveway": re.compile(r"\bdriveway\b", re.I),
    "patio": re.compile(r"\bpatio\b", re.I),
    "roof_cleaning": re.compile(r"roof\s*clean", re.I),
    "gutter": re.compile(r"\bgutter\b", re.I),
    "paver_sealing": re.compile(r"paver\s*seal", re.I),
}
COUNTDOWN_RE = re.compile(
    r"countdown|expires?\s+in|offer\s+ends|limited\s+time|hurry"
    r"|\bdeadline\b|ends\s+(?:today|tonight|soon)", re.I)


def audit(page, url: str, viewport: str) -> dict:
    rec: dict = {"requested_url": url, "viewport": viewport}
    requests: list[str] = []
    page.on("request", lambda r: requests.append(r.url))
    redirects: list[str] = []
    # These hosts sit behind SG-Captcha. A real browser is served an interstitial that
    # clears itself; wait for that to finish instead of recording the stub as the page.
    resp = None
    for attempt in range(4):
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as exc:  # noqa: BLE001
            rec["error"] = f"{type(exc).__name__}: {exc}"
            time.sleep(5)
            continue
        if resp is None:
            rec["error"] = "no response"
            time.sleep(5)
            continue
        rec.pop("error", None)
        if "sgcaptcha" in page.url or resp.status in (202, 403, 429):
            rec["captcha_interstitial_seen"] = True
            try:
                page.wait_for_url(lambda u: "sgcaptcha" not in u, timeout=45000)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(4 + attempt * 4)
            if "sgcaptcha" in page.url or resp.status in (403, 429):
                continue
        break
    if resp is None:
        return rec
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:  # noqa: BLE001
        pass
    if "sgcaptcha" in page.url:
        rec["error"] = "still on SG-Captcha interstitial after retries"
        rec["final_url"] = page.url
        rec["http_status"] = resp.status
        return rec
    r = resp
    while r.request.redirected_from:
        r = r.request.redirected_from.response()
        if r:
            redirects.append(f"{r.status} {r.url}")
    rec["redirect_chain"] = list(reversed(redirects))
    rec["final_url"] = page.url
    rec["http_status"] = resp.status
    html = page.content()
    rec["html_bytes"] = len(html)
    rec["title"] = page.title()

    def attr(sel, name):
        el = page.query_selector(sel)
        return el.get_attribute(name) if el else None

    rec["canonical"] = attr("link[rel=canonical]", "href")
    rec["meta_description"] = attr("meta[name=description]", "content")
    rec["robots"] = attr("meta[name=robots]", "content")
    rec["h1"] = [e.inner_text().strip() for e in page.query_selector_all("h1")]
    rec["h2"] = [e.inner_text().strip() for e in page.query_selector_all("h2")][:12]

    body_text = page.inner_text("body") if page.query_selector("body") else ""
    rec["body_chars"] = len(body_text)

    # Trackers: scan rendered DOM plus every network request the page made.
    haystack = html + "\n" + "\n".join(requests)
    rec["trackers"] = {}
    for name, rx in TRACKER_PATTERNS.items():
        found = sorted(set(rx.findall(haystack)))
        if found:
            rec["trackers"][name] = [f if isinstance(f, str) else str(f) for f in found][:6]
        elif rx.search(haystack):
            rec["trackers"][name] = ["present"]
    rec["request_hosts"] = sorted({urlparse(u).netloc for u in requests})

    # Click-to-call and displayed phone numbers.
    tel = sorted({(e.get_attribute("href") or "").replace("tel:", "").strip()
                  for e in page.query_selector_all("a[href^='tel:']")})
    rec["tel_links"] = [t for t in tel if t]
    rec["phones_in_text"] = sorted({"".join(m) for m in PHONE_RE.findall(body_text)})

    # Forms, without submitting anything.
    forms = []
    for f in page.query_selector_all("form"):
        fields = []
        for inp in f.query_selector_all("input, select, textarea"):
            t = inp.get_attribute("type") or inp.evaluate("e => e.tagName.toLowerCase()")
            if t in ("hidden",):
                fields.append(f"hidden:{inp.get_attribute('name')}")
            else:
                fields.append(f"{t}:{inp.get_attribute('name') or inp.get_attribute('id')}"
                              f"{'*' if inp.get_attribute('required') is not None else ''}")
        forms.append({
            "action": f.get_attribute("action"), "method": f.get_attribute("method"),
            "id": f.get_attribute("id"), "class": (f.get_attribute("class") or "")[:80],
            "fields": fields,
        })
    rec["forms"] = forms
    rec["iframe_srcs"] = sorted({(e.get_attribute("src") or "")[:160]
                                 for e in page.query_selector_all("iframe")})

    # Market integrity: does an Austin destination mention other Pro Green markets?
    rec["market_mentions"] = {k: len(rx.findall(body_text)) for k, rx in MARKET_RE.items()}
    rec["countdown_hits"] = sorted(set(COUNTDOWN_RE.findall(body_text)))[:10]
    rec["countdown_present"] = bool(COUNTDOWN_RE.search(body_text))
    rec["out_of_scope_links"] = sorted({
        (e.get_attribute("href") or "") for e in page.query_selector_all("a[href]")
        if re.search(r"roof|gutter|paver-seal|landscap|masonry|shrink|party",
                     e.get_attribute("href") or "", re.I)
    })[:12]
    rec["body_text_sample"] = body_text[:2500]

    # Click-id preservation through the redirect chain.
    rec["query_on_final_url"] = urlparse(page.url).query

    # CTA inventory.
    ctas = []
    for e in page.query_selector_all("a, button"):
        txt = (e.inner_text() or "").strip()
        if txt and len(txt) < 60 and re.search(
                r"quote|estimate|call|contact|schedule|book|consult|get started|request",
                txt, re.I):
            ctas.append(txt)
    rec["ctas"] = sorted(set(ctas))[:20]
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", required=True, help="file with one URL per line")
    ap.add_argument("--out", required=True)
    ap.add_argument("--delay", type=float, default=6.0,
                    help="seconds between navigations")
    ap.add_argument("--gclid-test", action="store_true",
                    help="append a synthetic gclid to test click-id preservation")
    args = ap.parse_args()

    urls = [u.strip() for u in Path(args.urls).read_text(encoding="utf-8").splitlines()
            if u.strip() and not u.startswith("#")]
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"])
        for viewport, size, ua in [
            ("desktop", {"width": 1440, "height": 900}, UA_DESKTOP),
            ("mobile", {"width": 390, "height": 844}, None),
        ]:
            # One context per viewport, reused across URLs, so the bot-management
            # cookie persists exactly as it would for a real visitor.
            ctx = (browser.new_context(viewport=size, user_agent=ua,
                                       locale="en-US", timezone_id="America/New_York")
                   if ua else browser.new_context(**pw.devices["iPhone 13"],
                                                  locale="en-US",
                                                  timezone_id="America/New_York"))
            page = ctx.new_page()
            if urls:
                root = "/".join(urls[0].split("/")[:3]) + "/"
                try:
                    page.goto(root, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(9000)
                except Exception:  # noqa: BLE001
                    pass
            for u in urls:
                time.sleep(args.delay)
                target = u
                if args.gclid_test:
                    sep = "&" if "?" in u else "?"
                    target = (f"{u}{sep}gclid=TESTGCLID_readonly_audit"
                              f"&utm_source=google&utm_medium=cpc&utm_campaign=audit")
                rec = audit(page, target, viewport)
                results.append(rec)
                st = rec.get("http_status", "ERR")
                print(f"[{viewport:7}] {st} {rec.get('final_url', u)[:96]}")
                if rec.get("error"):
                    print(f"          ERROR {rec['error'][:150]}")
            ctx.close()
        browser.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwritten: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
