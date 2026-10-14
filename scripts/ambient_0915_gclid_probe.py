#!/usr/bin/env python3
"""Ambient | 2026-09-15 | characterise GCLID/UTM capture into the Gravity Form.

Loads each paid page N times in a fresh context, waits long, and reads the LIVE DOM
value of every hidden field. GET only; nothing is submitted.
"""
from __future__ import annotations
import datetime, json, sys
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-15"
BASE = "https://offer.ambientcoolingandheating.com"
PAGES = {
    "Commercial HVAC Installation": f"{BASE}/commercial-hvac-installation/",
    "AC Repair": f"{BASE}/ac-repair/",
    "HVAC Repair": f"{BASE}/hvac-repair/",
    "HVAC Installation": f"{BASE}/hvac-installation/",
    "HVAC Replacement": f"{BASE}/hvac-replacement/",
    "Gas Boiler Repair": f"{BASE}/gas-boiler-repair/",
}
MARK = "QA0915PROBE"
PARAMS = (f"?gclid={MARK}&utm_source=google&utm_medium=cpc&utm_campaign=qa-probe"
          f"&utm_term=qa-term&utm_content=qa-content")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
JS = """
() => {
  const f = document.querySelector('form#gform_1');
  if (!f) return {found:false};
  const out = {found:true, fields:{}};
  f.querySelectorAll("input[type=hidden]").forEach(el => {
    if (/^input_\\d+$/.test(el.name)) out.fields[el.name] = (el.value||'').slice(0,160);
  });
  out.allForms = document.querySelectorAll('form#gform_1').length;
  out.wcReady = typeof window.wc !== 'undefined' || !!document.cookie.match(/wc_visitor/);
  return out;
}
"""
N = 4


def main():
    res = {"generated_local": datetime.datetime.now(TZ).isoformat(), "marker": MARK,
           "loads_per_page": N, "pages": {}}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for svc, url in PAGES.items():
            runs = []
            for i in range(N):
                ctx = br.new_context(user_agent=UA, viewport={"width": 1440, "height": 900},
                                     locale="en-US")
                page = ctx.new_page()
                try:
                    page.goto(url + PARAMS, wait_until="networkidle", timeout=90000)
                    page.wait_for_timeout(9000)
                    d = page.evaluate(JS)
                    filled = {k: v for k, v in (d.get("fields") or {}).items() if v}
                    runs.append({"run": i + 1, "found_form": d.get("found"),
                                 "form_copies": d.get("allForms"),
                                 "wc_ready": d.get("wcReady"),
                                 "filled_fields": filled,
                                 "gclid_captured": MARK in json.dumps(filled),
                                 "utm_captured": "qa-content" in json.dumps(filled)})
                except Exception as ex:
                    runs.append({"run": i + 1, "error": str(ex)[:200]})
                ctx.close()
            hits = sum(1 for r in runs if r.get("gclid_captured"))
            res["pages"][svc] = {"url": url, "runs": runs,
                                 "gclid_capture_rate": f"{hits}/{N}"}
            print(f"{svc:30s} gclid captured {hits}/{N}")
            for r in runs:
                print(f"    run{r['run']} gclid={r.get('gclid_captured')} "
                      f"utm={r.get('utm_captured')} copies={r.get('form_copies')} "
                      f"filled={r.get('filled_fields')}")
        br.close()
    p = SNAP / f"gclid-capture-probe-{STAMP}.json"
    p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    tot = sum(int(v["gclid_capture_rate"].split("/")[0]) for v in res["pages"].values())
    print(f"OVERALL: {tot}/{len(PAGES)*N} loads captured the GCLID "
          f"({100*tot/(len(PAGES)*N):.0f}%)")


if __name__ == "__main__":
    sys.exit(main())
