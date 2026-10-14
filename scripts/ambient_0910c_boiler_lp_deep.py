#!/usr/bin/env python3
"""Follow-ups on the boiler page: the unexplained third phone number, whether WhatConverts
loads from its CDN domain rather than whatconverts.com, and where Privacy/Terms live.
GET only. Nothing submitted."""
from __future__ import annotations
import json, re, sys, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from collections import Counter
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence"
TZ = ZoneInfo("America/New_York")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
PAGES = {
    "gas-boiler-repair": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "ac-repair": "https://offer.ambientcoolingandheating.com/ac-repair/",
    "hvac-repair": "https://offer.ambientcoolingandheating.com/hvac-repair/",
    "hvac-installation": "https://offer.ambientcoolingandheating.com/hvac-installation/",
    "hvac-replacement": "https://offer.ambientcoolingandheating.com/hvac-replacement/"}
GCLID = "?gclid=TESTgclidAmbientQA20260910&utm_source=google&utm_medium=cpc"
KNOWN = {"4107056354": "PAID (410) 705-6354", "4107610932": "ORGANIC (410) 761-0932"}
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "method": "Playwright Chromium, GET only, nothing submitted"}

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for name, base in PAGES.items():
        ctx = b.new_context(user_agent=UA, viewport={"width": 1440, "height": 2400})
        pg = ctx.new_page()
        net = []
        pg.on("request", lambda r: net.append(r.url))
        pg.goto(base + GCLID, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(4000)
        html = pg.content()
        txt = re.sub(r"\s+", " ", pg.inner_text("body"))

        tel = pg.eval_on_selector_all(
            "a[href^='tel:']", "e=>e.map(x=>({href:x.getAttribute('href'),txt:x.innerText.trim()}))")
        nums = Counter()
        for t in tel:
            d = re.sub(r"\D", "", t["href"] or "")
            d = d[-10:] if len(d) >= 10 else d
            nums[d] += 1
        for d in re.findall(r"\(?\b(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})\b", txt):
            nums["".join(d)] += 0
        unknown = {d: n for d, n in nums.items() if d and d not in KNOWN}

        third = [t for t in tel
                 if re.sub(r"\D", "", t["href"] or "")[-10:] not in KNOWN]
        # tracking vendors: WhatConverts serves from scripts.iyzt.com, not whatconverts.com
        vend = {}
        for host, label in [("whatconverts", "whatconverts.com"), ("iyzt", "scripts.iyzt.com"),
                            ("googletagmanager", "GTM/gtag"), ("doubleclick", "doubleclick"),
                            ("google-analytics", "GA"), ("clickcease", "ClickCease"),
                            ("clarity", "MS Clarity"), ("hotjar", "Hotjar")]:
            hits = [u.split("?")[0] for u in net if host in u.lower()]
            if hits:
                vend[label] = sorted(set(hits))[:4]
        # WhatConverts leaves a wc_swap / wctclid cookie when its DNI runs
        cookies = ctx.cookies()
        wc_cookies = sorted({c["name"] for c in cookies
                             if re.search(r"wc|swap|iyzt", c["name"], re.I)})
        allcookies = sorted({c["name"] for c in cookies})
        # legal links anywhere, including footer
        links = pg.eval_on_selector_all(
            "a[href]", "e=>e.map(x=>({t:(x.innerText||'').trim(),h:x.href}))")
        legal = [l for l in links
                 if re.search(r"privacy|terms|tos\b|conditions", (l["t"] + " " + l["h"]), re.I)]
        # gclid capture into the form
        hidden = pg.eval_on_selector_all(
            "input[type=hidden]", "e=>e.map(x=>({name:x.name,hasvalue:!!x.value}))")
        gfields = sorted({h["name"] for h in hidden if h.get("name") and
                          re.search(r"gclid|gbraid|wbraid|utm|source|medium|campaign|"
                                    r"keyword|adgroup", h["name"], re.I)})
        gpop = sorted({h["name"] for h in hidden if h.get("name") and h.get("hasvalue") and
                       re.search(r"gclid|gbraid|wbraid|utm", h["name"], re.I)})
        formids = pg.eval_on_selector_all("form", "e=>e.map(x=>x.id)")
        d = {"url": base, "tel_links": tel, "unknown_numbers": sorted(unknown),
             "third_party_numbers": third, "tracking_vendors": vend,
             "wc_related_cookies": wc_cookies, "all_cookie_names": allcookies,
             "legal_links": legal[:6],
             "attribution_hidden_fields": gfields,
             "attribution_fields_populated": gpop,
             "form_ids": formids,
             "duplicate_form_ids": {k: v for k, v in Counter(formids).items() if v > 1}}
        out.setdefault("pages", {})[name] = d
        ctx.close()
    b.close()

print("=== THE THIRD PHONE NUMBER ===")
for n, d in out["pages"].items():
    print(f"\n  {n}")
    for t in d["tel_links"]:
        dig = re.sub(r"\D", "", t["href"] or "")[-10:]
        tag = KNOWN.get(dig, "*** UNACCOUNTED ***")
        print(f"    {t['href']:<26}{t['txt'][:34]:<36}{tag}")
    if d["third_party_numbers"]:
        print(f"    UNACCOUNTED on this page: "
              f"{[t['href'] for t in d['third_party_numbers']]}")

print("\n\n=== TRACKING VENDORS ACTUALLY LOADED (WhatConverts serves from scripts.iyzt.com) ===")
for n, d in out["pages"].items():
    print(f"  {n:<22}{ {k: len(v) for k, v in d['tracking_vendors'].items()} }")
print("\n  WhatConverts-related cookies per page:")
for n, d in out["pages"].items():
    print(f"    {n:<22}{d['wc_related_cookies']}")

print("\n=== LEGAL LINKS ===")
for n, d in out["pages"].items():
    print(f"  {n:<22}{[l['t'][:24] or l['h'][-30:] for l in d['legal_links']] or 'NONE FOUND'}")

print("\n=== CLICK-ID CAPTURE INTO THE FORM, PER PAGE (with ?gclid= present) ===")
print(f"  {'page':<22}{'forms':>6}{'dupe form ids':>16}   attribution fields / populated")
for n, d in out["pages"].items():
    print(f"  {n:<22}{len(d['form_ids']):>6}{str(d['duplicate_form_ids']):>16}   "
          f"{d['attribution_hidden_fields']} / {d['attribution_fields_populated']}")

print("\n=== SUMMARY ===")
nogclid = [n for n, d in out["pages"].items() if not d["attribution_fields_populated"]]
print(f"  pages whose form does NOT populate a gclid/utm field: {nogclid}")
dupes = [n for n, d in out["pages"].items() if d["duplicate_form_ids"]]
print(f"  pages with duplicate form ids: {dupes}")
unacc = {n: [t["href"] for t in d["third_party_numbers"]]
         for n, d in out["pages"].items() if d["third_party_numbers"]}
print(f"  pages carrying an unaccounted phone number: {unacc}")
out["summary"] = {"pages_without_populated_click_id": nogclid,
                  "pages_with_duplicate_form_ids": dupes,
                  "pages_with_unaccounted_number": unacc}
(EVID / "2026-09-10c-lp-deep-inspection.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {(EVID / '2026-09-10c-lp-deep-inspection.json').relative_to(ROOT)}")
