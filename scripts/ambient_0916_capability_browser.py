#!/usr/bin/env python3
"""Ambient | 2026-09-16 | heating capability verification via a REAL browser.

The official site sits behind NitroCDN/bot protection; a plain urllib fetch returns
nothing and produces a false "service not offered" verdict. Playwright is mandatory.
GET navigations only. No form submitted, no tel: activated, nothing modified.
"""
from __future__ import annotations
import json, re, sys, datetime
from pathlib import Path
from collections import defaultdict
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-16"
BASE = "https://ambientcoolingandheating.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "method": "playwright chromium, JS enabled, GET only", "external_writes": 0}

CANDIDATES = {
    "Furnace repair": r"furnace repair|repair\w*\s+(your |a |the )?furnace",
    "Furnace replacement": r"furnace replacement|replac\w*\s+(your |a |the )?furnace",
    "Furnace installation": r"furnace install\w*|install\w*\s+(your |a |the )?furnace",
    "Furnace maintenance / tune-up": r"furnace (maintenance|tune.?up|clean)",
    "Ductless mini-split installation": r"(mini.?split|ductless)[^.]{0,60}install|install[^.]{0,60}(mini.?split|ductless)",
    "Ductless mini-split repair": r"(mini.?split|ductless)[^.]{0,60}(repair|service)",
    "Heat pump repair": r"heat pump[^.]{0,50}(repair|service|fix)",
    "Heat pump replacement": r"heat pump[^.]{0,50}replac|replac[^.]{0,50}heat pump",
    "Heat pump installation": r"heat pump[^.]{0,50}install|install[^.]{0,50}heat pump",
    "Heat pump maintenance": r"heat pump[^.]{0,50}(maintenance|tune)",
    "Boiler repair": r"boiler[^.]{0,50}(repair|fix|service)",
    "Boiler replacement": r"boiler[^.]{0,50}replac|replac[^.]{0,50}boiler",
    "Boiler installation": r"boiler[^.]{0,50}install|install[^.]{0,50}boiler",
    "Boiler maintenance": r"boiler[^.]{0,50}(maintenance|tune|clean)",
    "Heating repair": r"heating repair|heating[^.]{0,40}(repair|service)",
    "Heating replacement": r"heating[^.]{0,40}replac",
    "Heating installation": r"heating[^.]{0,40}install",
    "Heating maintenance / tune-up": r"heating[^.]{0,40}(maintenance|tune.?up)",
    "Emergency heating repair": r"emergency[^.]{0,40}heat|24.?7[^.]{0,30}heat",
    "No-heat repair": r"\bno heat\b|not (heating|blowing hot|producing heat)",
    "Thermostat repair": r"thermostat[^.]{0,40}(repair|fix)",
    "Thermostat replacement / install": r"thermostat[^.]{0,40}(replac|install)|smart thermostat",
    "Gas furnace": r"gas furnace",
    "Electric furnace": r"electric furnace",
    "Heating system inspection": r"heating[^.]{0,40}(inspect|safety check)",
    "Geothermal heat pump": r"geothermal",
    "Water heater / tankless": r"water heater|tankless",
    "Oil furnace": r"oil furnace|oil.?fired",
    "Ductwork / air handler": r"\bductwork\b|air handler",
    "Commercial HVAC": r"commercial[^.]{0,50}(hvac|heating|cooling|propert)",
    "Indoor air quality": r"air quality|air purif|humidifier",
}


def clean(t):
    return re.sub(r"\s+", " ", t or "")


def main():
    pages, urls = {}, set()
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(user_agent=UA, viewport={"width": 1440, "height": 900},
                             locale="en-US")
        pg = ctx.new_page()
        print("=== 1. HOMEPAGE + NAVIGATION DISCOVERY ===")
        pg.goto(BASE + "/", wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(3000)
        hrefs = pg.evaluate(
            "() => Array.from(document.querySelectorAll('a[href]')).map(a=>a.href)")
        for h in hrefs:
            if h.startswith(BASE) and "#" not in h and "?" not in h:
                urls.add(h.rstrip("/") + "/")
        print(f"  homepage links on-domain: {len(urls)}")
        # second hop: follow service hubs to find leaf service pages
        hubs = [u for u in sorted(urls)
                if re.search(r"/services?/|/heating|/cooling|/hvac", u, re.I)]
        print(f"  service hubs to expand: {len(hubs)}")
        for u in hubs[:20]:
            try:
                pg.goto(u, wait_until="domcontentloaded", timeout=60000)
                pg.wait_for_timeout(1200)
                for h in pg.evaluate(
                        "() => Array.from(document.querySelectorAll('a[href]')).map(a=>a.href)"):
                    if h.startswith(BASE) and "#" not in h and "?" not in h:
                        urls.add(h.rstrip("/") + "/")
            except Exception:
                pass
        svc = sorted(u for u in urls if re.search(
            r"/services?/|/heating|/cooling|/hvac|/furnace|/boiler|/heat-pump|"
            r"/mini-split|/ductless|/thermostat|/geothermal|/water-heater|"
            r"/maintenance|/install|/repair|/replace|/air-quality", u, re.I))
        print(f"  service-ish URLs discovered: {len(svc)}")
        for u in svc:
            print("   ", u.replace(BASE, ""))

        print("\n=== 2. FETCH EACH SERVICE PAGE (real browser) ===")
        for u in svc[:60]:
            try:
                resp = pg.goto(u, wait_until="domcontentloaded", timeout=60000)
                pg.wait_for_timeout(1400)
                if resp and resp.status == 200:
                    pages[u] = {"title": clean(pg.title()),
                                "h1": [clean(h.inner_text())
                                       for h in pg.query_selector_all("h1")][:3],
                                "text": clean(pg.inner_text("body"))}
            except Exception as ex:
                print(f"    skip {u.replace(BASE,'')}: {str(ex)[:60]}")
        print(f"  fetched {len(pages)} pages with HTTP 200")
        ctx.close(); br.close()

    out["pages_fetched"] = len(pages)
    out["page_index"] = {u.replace(BASE, ""): {"title": v["title"], "h1": v["h1"],
                                               "chars": len(v["text"])}
                         for u, v in pages.items()}

    print("\n=== 3. CAPABILITY VERDICTS ===")
    evidence = defaultdict(list)
    for label, pat in CANDIDATES.items():
        for u, v in pages.items():
            m = re.search(pat, v["text"], re.I)
            if m:
                s = max(0, m.start() - 80)
                evidence[label].append({"url": u.replace(BASE, ""),
                                        "snippet": v["text"][s:m.end() + 80].strip()[:200]})
    verdicts = {}
    for label in CANDIDATES:
        ev = evidence.get(label, [])
        key = re.split(r"[/(]", label)[0].strip().lower()
        slug = key.replace(" ", "-")
        ded = [e for e in ev if slug.split("-")[0] in e["url"].lower()
               and (len(slug.split("-")) < 2 or slug.split("-")[1] in e["url"].lower()
                    or slug.split("-")[0] in e["url"].lower())]
        exact_slug = [e for e in ev if slug in e["url"].lower()]
        if exact_slug:
            v = "VERIFIED (dedicated page)"
        elif len(ev) >= 4:
            v = "VERIFIED (named across 4+ pages)"
        elif len(ev) >= 1:
            v = "PARTIAL (mentioned, no dedicated page)"
        else:
            v = "HOLD - CAPABILITY NOT VERIFIED"
        verdicts[label] = {"verdict": v, "page_hits": len(ev),
                           "dedicated_page_urls": [e["url"] for e in exact_slug][:4],
                           "example_urls": [e["url"] for e in ev][:6],
                           "example_snippet": ev[0]["snippet"] if ev else None}
        print(f"  [{v:34s}] {label:34s} ({len(ev)} pages)"
              + (f"  -> {exact_slug[0]['url']}" if exact_slug else ""))
    out["capability"] = verdicts

    print("\n=== 4. CLAIM SCAN ACROSS THE OFFICIAL SITE ===")
    BARRED = {"24/7": r"\b24\s*/\s*7\b", "emergency": r"\bemergency\b",
              "same-day": r"\bsame.?day\b", "financing": r"\bfinanc(e|ing)\b",
              "licensed/insured": r"licen[cs]ed|\binsured\b",
              "warranty": r"\bwarrant(y|ies)\b",
              "reviews/rating": r"\b\d+\s*star|\breviews?\b",
              "years in business": r"\b(since|over)\s+\d{4}\b|\b\d+\+?\s*years\b"}
    cs = {}
    for k, pat in BARRED.items():
        hits = [u.replace(BASE, "") for u, v in pages.items()
                if re.search(pat, v["text"], re.I)]
        cs[k] = {"pages": len(hits), "examples": hits[:4]}
        print(f"  {k:20s} on {len(hits):>2} pages  {hits[:3]}")
    out["site_claim_scan"] = cs
    print("\n  Site presence is NOT paid-ad authorization. 'Licensed & Insured' stays")
    print("  WITHDRAWN per the approval owner, 2026-09-10.")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"heating-capability-browser-{STAMP}.json"
    payload = dict(out)
    payload["page_text"] = {u.replace(BASE, ""): v["text"][:6000]
                            for u, v in pages.items()}
    p.write_text(json.dumps(payload, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    sys.exit(main())
