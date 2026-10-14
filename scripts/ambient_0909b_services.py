#!/usr/bin/env python3
"""Render the LIVE Ambient website in a real browser and record which services it advertises.
GET navigations only. No form submitted, no tel: link activated."""
from __future__ import annotations
import json, re, sys, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence"
TZ = ZoneInfo("America/New_York")

MAIN = "https://ambientcoolingandheating.com/"
PAGES = [MAIN]

SERVICE_PATTERNS = {
    "air duct cleaning": r"air\s*duct\s*clean|duct\s*clean",
    "ductwork": r"duct\s*work|ductwork|air\s*duct",
    "thermostat": r"thermostat",
    "humidifier": r"\bhumidifier",
    "dehumidifier": r"dehumidifier",
    "geothermal": r"geothermal",
    "mini split / ductless": r"mini[\s-]?split|ductless",
    "boiler": r"boiler",
    "furnace": r"furnace",
    "heat pump": r"heat\s*pump",
    "tankless water heater": r"tankless|water\s*heater",
    "commercial": r"\bcommercial\b",
    "residential": r"\bresidential\b",
    "maintenance": r"maintenance|tune[\s-]?up",
    "indoor air quality": r"indoor\s*air\s*quality|air\s*quality|air\s*purif",
}
MANU_PATTERNS = {m: rf"\b{m}\b" for m in
                 ["lennox", "carrier", "trane", "goodman", "daikin", "rheem", "amana", "bosch",
                  "mitsubishi", "armstrong", "burnham", "spacepak", "aciq", "york", "bryant",
                  "ruud", "american standard", "navien", "rinnai", "mrcool"]}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

results = {}
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(user_agent=UA, viewport={"width": 1440, "height": 2400})
    page = ctx.new_page()
    seen = set()
    queue = list(PAGES)
    while queue and len(seen) < 14:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            resp = page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(1500)
            html = page.content()
            text = page.inner_text("body")
        except Exception as e:
            results[url] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}
            continue
        low = text.lower()
        svc = {k: bool(re.search(v, low)) for k, v in SERVICE_PATTERNS.items()}
        manu = {k: bool(re.search(v, low)) for k, v in MANU_PATTERNS.items()}
        h1 = [x.strip() for x in page.eval_on_selector_all("h1", "e=>e.map(x=>x.innerText)") if x.strip()]
        h2 = [x.strip() for x in page.eval_on_selector_all("h2", "e=>e.map(x=>x.innerText)") if x.strip()]
        links = page.eval_on_selector_all(
            "a[href]", "e=>e.map(x=>({t:(x.innerText||'').trim(), h:x.href}))")
        results[url] = {"status": resp.status if resp else None,
                        "title": page.title(), "h1": h1, "h2": h2[:40],
                        "services_mentioned": {k: v for k, v in svc.items() if v},
                        "services_absent": [k for k, v in svc.items() if not v],
                        "manufacturers_mentioned": {k: v for k, v in manu.items() if v},
                        "text_len": len(text)}
        if url == MAIN:
            for l in links:
                h = (l["h"] or "").split("#")[0].rstrip("/") + "/"
                if h.startswith("https://ambientcoolingandheating.com/") and h not in seen:
                    if re.search(r"service|repair|install|replace|duct|thermostat|humid|"
                                 r"geothermal|boiler|furnace|heat|air|commercial|residential",
                                 h, re.I):
                        queue.append(h)
            results[url]["internal_service_links"] = sorted(
                {(l["h"] or "").split("#")[0] for l in links
                 if (l["h"] or "").startswith("https://ambientcoolingandheating.com/")})
    b.close()

print("=== AMBIENT LIVE WEBSITE — ADVERTISED SERVICES ===")
agg_services = set()
agg_manu = set()
for url, d in results.items():
    if "error" in d:
        print(f"\n  {url}\n     ERROR {d['error']}")
        continue
    print(f"\n  {url}  [{d['status']}]  {d['title'][:70]!r}")
    if d["h1"]:
        print(f"     H1: {d['h1'][:3]}")
    print(f"     services mentioned: {sorted(d['services_mentioned'])}")
    if d["manufacturers_mentioned"]:
        print(f"     manufacturers mentioned: {sorted(d['manufacturers_mentioned'])}")
    agg_services |= set(d["services_mentioned"])
    agg_manu |= set(d["manufacturers_mentioned"])

print("\n=== UNION ACROSS ALL RENDERED PAGES ===")
print(f"  SERVICES advertised anywhere: {sorted(agg_services)}")
print(f"  MANUFACTURERS named anywhere: {sorted(agg_manu)}")
print("\n  Contested services from the correction brief:")
for s in ["air duct cleaning", "thermostat", "humidifier", "dehumidifier", "geothermal"]:
    print(f"    {s:<20} advertised on the live site: {s in agg_services}")

out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "method": "Playwright Chromium, JS enabled, GET only",
       "pages": results, "services_union": sorted(agg_services),
       "manufacturers_union": sorted(agg_manu)}
EVID.mkdir(parents=True, exist_ok=True)
(EVID / "2026-09-09b-website-services.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {(EVID / '2026-09-09b-website-services.json').relative_to(ROOT)}")
