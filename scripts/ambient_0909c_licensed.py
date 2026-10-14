#!/usr/bin/env python3
"""Is 'licensed' supported advertising language for Ambient? Real-browser evidence."""
from __future__ import annotations
import json, re, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence"
TZ = ZoneInfo("America/New_York")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

PAGES = [
    "https://offer.ambientcoolingandheating.com/ac-repair/",
    "https://offer.ambientcoolingandheating.com/hvac-repair/",
    "https://offer.ambientcoolingandheating.com/hvac-installation/",
    "https://offer.ambientcoolingandheating.com/hvac-replacement/",
    "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "https://ambientcoolingandheating.com/",
    "https://ambientcoolingandheating.com/services/",
    "https://ambientcoolingandheating.com/reviews/",
]
PAT = re.compile(r"[^.]{0,130}(licen[sc]ed|licen[sc]e|insured|bonded|certified|NATE)[^.]{0,130}",
                 re.I)

res = {}
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(user_agent=UA, viewport={"width": 1440, "height": 2400})
    pg = ctx.new_page()
    for u in PAGES:
        try:
            r = pg.goto(u, wait_until="networkidle", timeout=45000)
            pg.wait_for_timeout(1400)
            txt = re.sub(r"\s+", " ", pg.inner_text("body"))
        except Exception as e:
            res[u] = {"error": f"{type(e).__name__}: {str(e)[:140]}"}
            continue
        hits = [m.group(0).strip() for m in PAT.finditer(txt)][:6]
        res[u] = {"status": r.status if r else None, "title": pg.title(),
                  "hits": hits, "n_hits": len(hits)}
    b.close()

print("=== IS 'licensed' SUPPORTED LANGUAGE? LIVE-PAGE EVIDENCE ===")
any_hit = False
for u, d in res.items():
    print(f"\n  {u}")
    if "error" in d:
        print(f"     ERROR {d['error']}")
        continue
    print(f"     [{d['status']}] {d['title'][:64]!r}   matches={d['n_hits']}")
    for h in d["hits"]:
        any_hit = True
        print(f"       ...{h[:190]}")

print("\n=== VERDICT ===")
print(f"  any licensed/insured/certified language found on a live Ambient page: {any_hit}")
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "method": "Playwright Chromium, JS enabled, GET only",
       "pages": res, "any_supporting_language_found": any_hit}
(EVID / "2026-09-09c-licensed-evidence.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"WROTE {(EVID / '2026-09-09c-licensed-evidence.json').relative_to(ROOT)}")
