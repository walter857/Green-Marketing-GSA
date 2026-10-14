#!/usr/bin/env python3
"""Ambient | 2026-09-23 | Census of EVERY form instance on every live ad destination.

READ-ONLY. No parameters, no submissions, no tel activation.

Purpose: produce the exact selector list WhatConverts needs. The profile currently
registers only #gform_1. Anything else found here is invisible to WhatConverts today.
Checks desktop AND mobile, and re-scans after interaction so popup / lazy-loaded /
dynamically injected instances are counted.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-23"
# The destinations actually used by enabled ad groups, plus the offer pages.
DEST = {
    "MAIN heating hub": "https://ambientcoolingandheating.com/services/heating-services/",
    "MAIN furnace-repair": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "MAIN boiler-repair": "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/",
    "MAIN mini-splits": "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/",
    "MAIN geothermal": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
    "OFFER gas-boiler": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "OFFER hvac-installation": "https://offer.ambientcoolingandheating.com/hvac-installation/",
    "OFFER hvac-replacement": "https://offer.ambientcoolingandheating.com/hvac-replacement/",
}
PROBE = """() => [...document.querySelectorAll('form')].map((f,i) => {
  const r = f.getBoundingClientRect();
  const st = getComputedStyle(f);
  const vis = !!(r.width>20 && r.height>20 && st.display!=='none' && st.visibility!=='hidden');
  const fields = [...f.querySelectorAll('input,textarea,select')];
  return {
    index:i, id:f.id||'', cls:(f.className||'').slice(0,60),
    action:(f.getAttribute('action')||'').slice(0,60),
    selector: f.id ? '#'+f.id : (f.className? '.'+String(f.className).trim().split(/\\s+/)[0] : 'form:nth-of-type('+(i+1)+')'),
    visible: vis, fields: fields.length,
    named: fields.filter(e=>e.name).length,
    inModal: !!f.closest('[role=dialog],.modal,.popup,.mfp-content,.elementor-popup-modal'),
    submit: !!f.querySelector('input[type=submit],button[type=submit],button:not([type])')
  };
})"""


def scan(pg):
    return pg.evaluate(PROBE)


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "parameterised_requests": 0, "forms_submitted": 0,
           "whatconverts_registered_selectors": ["#gform_1"], "pages": {}}
    allsel = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for label, url in DEST.items():
            rec = {"url": url, "devices": {}}
            for dev, cfg in (("desktop", {"viewport": {"width": 1440, "height": 900}}),
                             ("mobile", {"viewport": {"width": 390, "height": 844},
                                         "is_mobile": True, "has_touch": True,
                                         "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone "
                                         "OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
                                         "(KHTML, like Gecko) Version/17.5 Mobile/15E148 "
                                         "Safari/604.1"})):
                ctx = b.new_context(locale="en-US", timezone_id="America/New_York", **cfg)
                pg = ctx.new_page()
                d = {}
                try:
                    r = pg.goto(url, wait_until="domcontentloaded", timeout=70000)
                    d["status"] = r.status if r else None
                    pg.wait_for_timeout(2500)
                    d["before_interaction"] = scan(pg)
                    # NitroPack defers JS until interaction; popups need a scroll/click
                    pg.mouse.move(400, 300)
                    pg.mouse.wheel(0, 2000)
                    pg.keyboard.press("PageDown")
                    pg.wait_for_timeout(6000)
                    pg.mouse.wheel(0, 4000)
                    pg.keyboard.press("End")
                    pg.wait_for_timeout(5000)
                    d["after_interaction"] = scan(pg)
                except Exception as ex:
                    d["error"] = str(ex)[:200]
                finally:
                    ctx.close()
                rec["devices"][dev] = d
                for f in d.get("after_interaction", []):
                    key = f["selector"]
                    a = allsel.setdefault(key, {"pages": set(), "visible_anywhere": False,
                                                "in_modal": False, "max_fields": 0})
                    a["pages"].add(label)
                    a["visible_anywhere"] |= f["visible"]
                    a["in_modal"] |= f["inModal"]
                    a["max_fields"] = max(a["max_fields"], f["fields"])
            out["pages"][label] = rec
            dd = rec["devices"]["desktop"].get("after_interaction", [])
            mm = rec["devices"]["mobile"].get("after_interaction", [])
            print(f"\n=== {label} ===")
            print(f"  desktop: {len(dd)} forms  {[f['selector'] for f in dd]}")
            print(f"  mobile : {len(mm)} forms  {[f['selector'] for f in mm]}")
            pre = len(rec["devices"]["desktop"].get("before_interaction", []))
            if pre != len(dd):
                print(f"  NOTE: desktop form count changed {pre} -> {len(dd)} after "
                      f"interaction (lazy/dynamic instance)")
        b.close()

    out["selectors_found"] = {k: {"pages": sorted(v["pages"]),
                                  "visible_anywhere": v["visible_anywhere"],
                                  "in_modal": v["in_modal"],
                                  "max_fields": v["max_fields"],
                                  "registered_in_whatconverts": k == "#gform_1"}
                              for k, v in allsel.items()}
    print("\n=== SELECTOR CENSUS ===")
    print(f"{'selector':22s} {'reg?':5s} {'vis':4s} {'modal':6s} {'flds':5s} pages")
    for k, v in sorted(out["selectors_found"].items()):
        reg = "YES" if v["registered_in_whatconverts"] else "NO"
        print(f"  {k:22s} {reg:5s} {str(v['visible_anywhere'])[:4]:4s} "
              f"{str(v['in_modal'])[:5]:6s} {v['max_fields']:5d} "
              f"{len(v['pages'])} page(s)")
    missing = [k for k, v in out["selectors_found"].items()
               if not v["registered_in_whatconverts"]]
    out["selectors_missing_from_whatconverts"] = missing
    print(f"\n  MISSING from WhatConverts form_list: {missing}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"form-census-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("PARAMETERISED REQUESTS: 0 | FORMS SUBMITTED: 0")


if __name__ == "__main__":
    main()
