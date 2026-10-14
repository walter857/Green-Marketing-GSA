#!/usr/bin/env python3
"""Ambient | 2026-09-21b | Discover every candidate landing page for the 31-service scope.

READ-ONLY. No parameters sent, no forms submitted, no tel links activated.

Pulls both sitemaps (main site and the offer subdomain), then renders every plausible
service page to capture its real H1, title and the intents its copy actually supports.
A page is only a valid destination for an intent if its own copy supports that intent —
judge by H1 and body, never by slug, because several short-path service URLs on this site
are generic shells.

Also re-checks the commercial-hvac-installation offer page, whose status decides whether
the cooling pause can be taken at campaign level.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
import urllib.request
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-21b"
SITES = ["https://ambientcoolingandheating.com",
         "https://offer.ambientcoolingandheating.com"]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/125.0.0.0 Safari/537.36")

# Only pages that could plausibly host one of the 31 heating services, plus the
# commercial page the cooling-pause decision depends on.
# Only real service pages, plus the two offer pages the transition depends on.
# The first cut matched blog posts and category archives too, which is 200+ pages of
# editorial content that can never be an ad destination.
KEEP = re.compile(r"/services/|^https://offer\.", re.I)
SKIP = re.compile(r"/category/|/blog|/faqs/|/tag/|/author/", re.I)

INTENT = {
    "repair": re.compile(r"\brepair(s|ed|ing)?\b|\bfix(es|ed|ing)?\b|\bbroken\b", re.I),
    "replace": re.compile(r"\breplac(e|es|ed|ing|ement|ements)\b", re.I),
    "install": re.compile(r"\binstall(s|ed|ing|ation|ations|er|ers)?\b", re.I),
    "maintenance": re.compile(r"\bmaintenance\b|\bmaintain\b", re.I),
    "tune_up": re.compile(r"\btune[- ]?up[s]?\b", re.I),
    "inspection": re.compile(r"\binspect(ion|ions|ing|s)?\b", re.I),
    "emergency": re.compile(r"\bemergency\b|\bno heat\b|\burgent\b", re.I),
    "thermostat": re.compile(r"\bthermostat[s]?\b", re.I),
    "ductless": re.compile(r"\bductless\b|\bmini[- ]?split[s]?\b", re.I),
    "heat_pump": re.compile(r"\bheat[- ]?pump[s]?\b", re.I),
    "geothermal": re.compile(r"\bgeothermal\b", re.I),
    "boiler": re.compile(r"\bboiler[s]?\b", re.I),
    "furnace": re.compile(r"\bfurnace[s]?\b", re.I),
    "gas": re.compile(r"\bgas\b", re.I),
    "electric": re.compile(r"\belectric\b", re.I),
    "commercial": re.compile(r"\bcommercial\b", re.I),
}


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def sitemap_urls(base):
    """Walk sitemap index -> child sitemaps -> page urls."""
    seen, todo, out = set(), [f"{base}/sitemap_index.xml", f"{base}/sitemap.xml"], set()
    while todo:
        sm = todo.pop()
        if sm in seen:
            continue
        seen.add(sm)
        st, body = fetch(sm)
        if st != 200 or not body:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
        for u in locs:
            if u.endswith(".xml"):
                todo.append(u)
            elif u.startswith(base):
                out.add(u.split("?")[0])
    return sorted(out)


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "parameterised_requests": 0, "forms_submitted": 0,
           "sites": {}, "pages": {}}

    candidates = []
    for base in SITES:
        urls = sitemap_urls(base)
        keep = [u for u in urls if KEEP.search(u) and not SKIP.search(u)]
        out["sites"][base] = {"sitemap_urls": len(urls), "service_candidates": len(keep),
                              "all_urls": urls}
        candidates += keep
        print(f"{base}: {len(urls)} urls in sitemap, {len(keep)} look service-related")
    candidates = sorted(set(candidates))
    print(f"\nrendering {len(candidates)} candidate pages\n")

    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for u in candidates:
            ctx = b.new_context(locale="en-US", timezone_id="America/New_York",
                                viewport={"width": 1366, "height": 900})
            pg = ctx.new_page()
            rec = {"url": u}
            try:
                r = pg.goto(u, wait_until="domcontentloaded", timeout=60000)
                rec["status"] = r.status if r else None
                pg.wait_for_timeout(2500)
                pg.mouse.wheel(0, 1600)
                pg.keyboard.press("PageDown")
                pg.wait_for_timeout(4000)
                txt = pg.evaluate("()=>document.body?document.body.innerText:''")
                rec["h1"] = pg.evaluate(
                    "()=>[...document.querySelectorAll('h1')].map(e=>e.innerText.trim())")
                rec["title"] = pg.evaluate("()=>document.title||''")
                rec["canonical"] = pg.evaluate(
                    "()=>{const e=document.querySelector('link[rel=canonical]');"
                    "return e?e.href:''}")
                rec["h2"] = pg.evaluate(
                    "()=>[...document.querySelectorAll('h2')]"
                    ".map(e=>e.innerText.trim()).slice(0,18)")
                rec["chars"] = len(txt)
                rec["forms"] = pg.evaluate("()=>document.querySelectorAll('form').length")
                head = " ".join(rec["h1"]) + " " + rec["title"] + " " + " ".join(rec["h2"])
                rec["intent_head"] = sorted(k for k, rx in INTENT.items() if rx.search(head))
                rec["intent_body"] = sorted(k for k, rx in INTENT.items() if rx.search(txt))
                rec["intent_body_counts"] = {k: len(rx.findall(txt))
                                             for k, rx in INTENT.items() if rx.search(txt)}
            except Exception as ex:
                rec["error"] = str(ex)[:180]
            finally:
                ctx.close()
            out["pages"][u] = rec
            print(f"  {str(rec.get('status')):4s} {u[:74]}")
            print(f"        H1={rec.get('h1')}  chars={rec.get('chars')}")
            print(f"        head-intents={rec.get('intent_head')}")
        b.close()

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"lp-discovery-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("PARAMETERISED REQUESTS: 0 | FORMS SUBMITTED: 0 | CHANGES: 0")


if __name__ == "__main__":
    main()
