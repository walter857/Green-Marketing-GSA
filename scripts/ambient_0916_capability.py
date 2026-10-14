#!/usr/bin/env python3
"""Ambient | 2026-09-16 | verify which heating services Ambient actually offers.

Reads the official website only. GET only, no forms, no tel: activation, nothing modified.
"""
from __future__ import annotations
import json, re, sys, datetime, urllib.request, urllib.error
from pathlib import Path
from collections import defaultdict
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-16"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
BASE = "https://ambientcoolingandheating.com"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "source": "official website, read-only", "external_writes": 0}


def get(url):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(r, timeout=45) as z:
            return z.status, z.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


print("=== 1. DISCOVER SERVICE PAGES FROM THE SITEMAP / NAV ===")
urls = set()
for sm in ("/sitemap_index.xml", "/sitemap.xml", "/page-sitemap.xml",
           "/wp-sitemap.xml"):
    st, body = get(BASE + sm)
    if st == 200 and body:
        for m in re.finditer(r"<loc>([^<]+)</loc>", body):
            u = m.group(1)
            if u.endswith(".xml"):
                st2, b2 = get(u)
                if st2 == 200:
                    for m2 in re.finditer(r"<loc>([^<]+)</loc>", b2):
                        urls.add(m2.group(1))
            else:
                urls.add(u)
        if urls:
            print(f"  {sm}: found {len(urls)} URLs")
            break
st, home = get(BASE + "/")
for m in re.finditer(r'href="(https://ambientcoolingandheating\.com/[^"#?]*)"', home or ""):
    urls.add(m.group(1))
svc = sorted(u for u in urls
             if re.search(r"/services?/|/heating|/cooling|/hvac|/furnace|/boiler|"
                          r"/heat-pump|/mini-split|/ductless|/thermostat|/geothermal|"
                          r"/water-heater|/maintenance|/install|/repair|/replace", u, re.I))
print(f"  service-ish URLs: {len(svc)}")
for u in svc[:60]:
    print("   ", u.replace(BASE, ""))
out["discovered_service_urls"] = svc

print("\n=== 2. FETCH SERVICE PAGES AND TEST CAPABILITY EVIDENCE ===")
CANDIDATES = {
    "Furnace repair": r"furnace repair|repair (your |a )?furnace|furnace.{0,30}(repair|fix)",
    "Furnace replacement": r"furnace replacement|replace (your |a |an )?furnace",
    "Furnace installation": r"furnace install",
    "Furnace maintenance / tune-up": r"furnace (maintenance|tune.?up|clean)",
    "Ductless mini-split installation": r"(mini.?split|ductless).{0,40}install|install.{0,40}(mini.?split|ductless)",
    "Ductless mini-split repair": r"(mini.?split|ductless).{0,40}(repair|service)",
    "Heat pump repair": r"heat pump.{0,30}(repair|service|fix)",
    "Heat pump replacement": r"heat pump.{0,30}replac|replac.{0,30}heat pump",
    "Heat pump installation": r"heat pump.{0,30}install|install.{0,30}heat pump",
    "Heat pump maintenance": r"heat pump.{0,30}(maintenance|tune)",
    "Boiler repair": r"boiler.{0,30}(repair|fix|service)",
    "Boiler replacement": r"boiler.{0,30}replac|replac.{0,30}boiler",
    "Boiler installation": r"boiler.{0,30}install|install.{0,30}boiler",
    "Boiler maintenance": r"boiler.{0,30}(maintenance|tune|clean)",
    "Heating repair": r"heating repair|heating.{0,30}(repair|service)",
    "Heating replacement": r"heating.{0,30}replac",
    "Heating installation": r"heating.{0,30}install",
    "Heating maintenance / tune-up": r"heating.{0,30}(maintenance|tune.?up)",
    "Emergency heating repair": r"emergency.{0,30}heat|24.?7.{0,20}heat",
    "No-heat repair": r"no heat\b|not (heating|blowing hot)",
    "Thermostat repair": r"thermostat.{0,30}(repair|fix)",
    "Thermostat replacement / install": r"thermostat.{0,30}(replac|install)|smart thermostat",
    "Gas furnace repair": r"gas furnace",
    "Electric furnace repair": r"electric furnace",
    "Heating system inspection": r"heating.{0,30}(inspect|safety check)",
    "Geothermal heat pump": r"geothermal",
    "Water heater / tankless": r"water heater|tankless",
    "Oil furnace": r"oil furnace|oil.?fired",
    "Ductwork / air handler": r"\bductwork\b|air handler",
    "Commercial HVAC": r"commercial.{0,40}(hvac|heating|cooling)",
}
pages = {}
for u in svc[:70]:
    st, body = get(u)
    if st == 200 and body:
        txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body,
                     flags=re.S | re.I)
        txt = re.sub(r"<[^>]+>", " ", txt)
        txt = re.sub(r"\s+", " ", txt)
        pages[u] = txt
print(f"  fetched {len(pages)} pages")

evidence = defaultdict(list)
for label, pat in CANDIDATES.items():
    for u, txt in pages.items():
        m = re.search(pat, txt, re.I)
        if m:
            s = max(0, m.start() - 70)
            snippet = txt[s:m.end() + 70].strip()
            evidence[label].append({"url": u.replace(BASE, ""),
                                    "snippet": snippet[:190]})
print("\n=== 3. CAPABILITY VERDICTS ===")
verdicts = {}
for label in CANDIDATES:
    ev = evidence.get(label, [])
    # a dedicated page whose slug names the service is the strongest signal
    ded = [e for e in ev if re.search(
        label.split("/")[0].strip().lower().replace(" ", "[-_ ]"),
        e["url"].lower())]
    if ded:
        v = "VERIFIED - dedicated page"
    elif len(ev) >= 3:
        v = "VERIFIED - named on 3+ pages"
    elif len(ev) >= 1:
        v = "PARTIAL - mentioned, no dedicated page"
    else:
        v = "HOLD - CLIENT CAPABILITY NOT VERIFIED"
    verdicts[label] = {"verdict": v, "page_hits": len(ev),
                       "dedicated_pages": [e["url"] for e in ded][:4],
                       "example_urls": [e["url"] for e in ev][:5],
                       "example_snippet": ev[0]["snippet"] if ev else None}
    print(f"  [{v:42s}] {label}  ({len(ev)} pages)")
out["capability"] = verdicts

print("\n=== 4. BARRED-CLAIM SCAN ON THE OFFICIAL SITE (for copy safety) ===")
BARRED = {"24/7": r"\b24\s*/\s*7\b", "emergency": r"\bemergency\b",
          "same-day": r"\bsame.?day\b", "financing": r"\bfinanc(e|ing)\b",
          "licensed/insured": r"licen[cs]ed|\binsured\b",
          "warranty": r"\bwarrant(y|ies)\b", "rating/reviews": r"\b\d+\s*star|\breviews?\b",
          "years in business": r"\b(since|over)\s+\d{2,4}\b|\b\d+\+?\s*years\b"}
found = {}
for k, pat in BARRED.items():
    hits = [u.replace(BASE, "") for u, t in pages.items() if re.search(pat, t, re.I)]
    found[k] = len(hits)
    print(f"  {k:20s} appears on {len(hits):>2} pages")
out["site_claim_scan"] = found
print("  NOTE: presence on the main site is NOT authorization to use a claim in paid ads.")
print("  'Licensed & Insured' remains WITHDRAWN by the approval owner (2026-09-10).")

SNAP.mkdir(parents=True, exist_ok=True)
p = SNAP / f"heating-capability-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("EXTERNAL WRITES: 0")
