#!/usr/bin/env python3
"""Crawl the live Ambient site for COMMERCIAL HVAC evidence and licence/insurance substantiation.
Real browser, GET only. No form submitted, no tel: link activated, nothing published."""
from __future__ import annotations
import json, re, sys, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence"
TZ = ZoneInfo("America/New_York")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
BASE = "https://ambientcoolingandheating.com"

COMM = re.compile(r"[^.!?]{0,150}\bcommercial\b[^.!?]{0,150}", re.I)
LIC = re.compile(r"[^.!?]{0,150}(licen[sc]ed|licen[sc]e\s*#?\s*\d|insured|bonded|"
                 r"MHIC|HVACR|liability insurance)[^.!?]{0,150}", re.I)
LICNUM = re.compile(r"(?:licen[sc]e|lic\.?|MHIC|HVACR)\s*#?\s*[:\-]?\s*(\d{3,8})", re.I)

results, comm_hits, lic_hits, licnums = {}, [], [], set()
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(user_agent=UA, viewport={"width": 1440, "height": 2600})
    pg = ctx.new_page()
    seen, queue = set(), [BASE + "/"]
    while queue and len(seen) < 45:
        url = queue.pop(0).split("#")[0]
        if url in seen or not url.startswith(BASE):
            continue
        seen.add(url)
        try:
            r = pg.goto(url, wait_until="networkidle", timeout=45000)
            pg.wait_for_timeout(900)
            txt = re.sub(r"\s+", " ", pg.inner_text("body"))
            title = pg.title()
        except Exception as e:
            results[url] = {"error": f"{type(e).__name__}"}
            continue
        cm = [m.group(0).strip() for m in COMM.finditer(txt)][:8]
        lc = [m.group(0).strip() for m in LIC.finditer(txt)][:8]
        for m in LICNUM.finditer(txt):
            licnums.add(m.group(1))
        results[url] = {"status": r.status if r else None, "title": title,
                        "commercial_hits": len(cm), "licence_hits": len(lc),
                        "commercial_snippets": cm, "licence_snippets": lc}
        if cm:
            comm_hits.append((url, title, cm))
        if lc:
            lic_hits.append((url, title, lc))
        if len(seen) < 45:
            for h in pg.eval_on_selector_all("a[href]", "e=>e.map(x=>x.href)"):
                h = (h or "").split("#")[0]
                if h.startswith(BASE) and h not in seen and not re.search(
                        r"\.(png|jpe?g|webp|gif|pdf|svg|css|js)$", h, re.I):
                    queue.append(h)
    b.close()

print(f"=== CRAWLED {len(results)} PAGES ON {BASE} ===")
print(f"\n=== COMMERCIAL HVAC EVIDENCE: {len(comm_hits)} pages mention 'commercial' ===")
for url, title, cm in comm_hits:
    print(f"\n  {url}")
    print(f"    {title[:80]!r}")
    for s in cm[:4]:
        print(f"      ...{s[:230]}")

DEDICATED = [u for u in results if re.search(r"commercial", u, re.I)]
print(f"\n  dedicated commercial URLs: {DEDICATED}")

print(f"\n\n=== LICENCE / INSURANCE EVIDENCE: {len(lic_hits)} pages ===")
for url, title, lc in lic_hits:
    print(f"\n  {url}")
    for s in lc[:4]:
        print(f"      ...{s[:230]}")
print(f"\n  licence numbers found in page text: {sorted(licnums) or 'NONE'}")

out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "method": "Playwright Chromium, JS enabled, GET only, nothing submitted or published",
       "pages_crawled": len(results),
       "commercial_pages": [{"url": u, "title": t, "snippets": s} for u, t, s in comm_hits],
       "dedicated_commercial_urls": DEDICATED,
       "licence_pages": [{"url": u, "title": t, "snippets": s} for u, t, s in lic_hits],
       "licence_numbers_on_site": sorted(licnums),
       "pages": results}
EVID.mkdir(parents=True, exist_ok=True)
(EVID / "2026-09-10-commercial-and-licence-crawl.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {(EVID / '2026-09-10-commercial-and-licence-crawl.json').relative_to(ROOT)}")
