#!/usr/bin/env python3
"""Ambient | 2026-09-16 | browser evidence capture for the attribution verification.

READ + QA ONLY. Screenshots + DOM extracts. No form submitted, no tel: activated,
nothing modified. Handles the SiteGround SG-Captcha 202 challenge.
"""
from __future__ import annotations
import datetime, json, re, sys, time
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence" / "attribution-2026-09-16"
TZ = ZoneInfo("America/New_York")
BASE = "https://offer.ambientcoolingandheating.com"
UA_D = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_M = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
TS = datetime.datetime.now(TZ).strftime("%H%M%S")

JS = """
() => {
  const pop = {};
  document.querySelectorAll('form input,form textarea,form select').forEach(el => {
    const v = (el.value||'').trim();
    if (v && !['0','1','postback','gravity-theme','[]'].includes(v))
      pop[el.name||el.id] = v.slice(0,90);
  });
  const ids = Array.from(document.querySelectorAll('[id]')).map(e=>e.id);
  const seen={}, dup=[];
  ids.forEach(x=>{ if(seen[x]){ if(!dup.includes(x)) dup.push(x);} seen[x]=1; });
  const forms = Array.from(document.querySelectorAll('form')).map(f=>({
    id: f.id||'', h: Math.round(f.getBoundingClientRect().height),
    visible: f.offsetParent !== null}));
  return {populated: pop, duplicateIds: dup, duplicateIdCount: dup.length,
          totalIds: ids.length, forms, formCount: forms.length,
          h1: Array.from(document.querySelectorAll('h1')).map(h=>h.innerText.trim()).slice(0,2),
          gtm: document.documentElement.innerHTML.includes('GTM-PQTPQ436'),
          aw: document.documentElement.innerHTML.includes('AW-11155434808'),
          ga4: document.documentElement.innerHTML.includes('G-9X9ZHNCRWF'),
          wcCookie: (document.cookie.match(/wc_visitor=[^;]*/)||[''])[0].slice(0,70),
          dataLayerLen: (window.dataLayer||[]).length,
          tels: Array.from(document.querySelectorAll("a[href^='tel:']")).map(a=>({
            href: a.getAttribute('href'),
            visible: !!(a.offsetWidth||a.offsetHeight)}))};
}
"""


def grab(pw, name, page, qs, profile, label):
    br = pw.chromium.launch()
    ctx = br.new_context(user_agent=UA_D if profile == "desktop" else UA_M,
                         viewport={"width": 1440, "height": 900} if profile == "desktop"
                         else {"width": 390, "height": 844},
                         is_mobile=(profile == "mobile"), locale="en-US")
    pg = ctx.new_page()
    final = {}
    pg.on("response", lambda r: final.__setitem__("r", r)
          if r.url.split("?")[0].rstrip("/") == page.rstrip("/") and r.status == 200 else None)
    resp = pg.goto(page + qs, wait_until="domcontentloaded", timeout=90000)
    init = resp.status if resp else None
    for _ in range(14):
        pg.wait_for_timeout(2500)
        try:
            st = pg.evaluate("() => ({f: document.querySelectorAll('form').length,"
                             " l: document.body ? document.body.innerText.length : 0})")
        except Exception:
            continue          # navigation in flight (SG-Captcha redirect) - retry
        if st["f"] > 0 and st["l"] > 500:
            break
    pg.wait_for_timeout(9500)
    d = None
    for _ in range(4):
        try:
            d = pg.evaluate(JS); break
        except Exception:
            pg.wait_for_timeout(3000)
    if d is None:
        d = {"populated": {}, "duplicateIds": [], "duplicateIdCount": None,
             "totalIds": None, "forms": [], "formCount": None, "h1": [],
             "gtm": None, "aw": None, "ga4": None, "wcCookie": "",
             "dataLayerLen": None, "tels": [], "_blocked": True}
    srv = ""
    try:
        srv = final["r"].text() if final.get("r") else ""
    except Exception:
        pass
    d["_meta"] = {"evidence": label, "url": page + qs, "profile": profile,
                  "initial_http_status": init,
                  "final_http_status": final["r"].status if final.get("r") else None,
                  "sg_captcha_challenge": init == 202,
                  "server_html_len": len(srv),
                  "server_html_hidden_values": sorted({
                      m.group(2) for m in re.finditer(
                          r'<input[^>]*name=["\'](input_\d+)["\'][^>]*value=["\']([^"\']+)["\']',
                          srv, re.I) if m.group(2).strip() not in ("", "0", "1")})[:12],
                  "captured_local": datetime.datetime.now(TZ).isoformat()}
    EVID.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(EVID / f"{name}.png"), full_page=False)
    (EVID / f"{name}.json").write_text(json.dumps(d, indent=1, default=str),
                                       encoding="utf-8")
    print(f"  [{label}] {name}.png  initial={init} final="
          f"{d['_meta']['final_http_status']} forms={d['formCount']} "
          f"dupIDs={d['duplicateIdCount']} gtm={d['gtm']} wc={bool(d['wcCookie'])}")
    print(f"      populated: {d['populated']}")
    print(f"      serverHTML hidden: {d['_meta']['server_html_hidden_values']}")
    ctx.close(); br.close()
    return d


def main():
    P = f"{BASE}/ac-repair/"
    C = f"{BASE}/commercial-hvac-installation/"
    with sync_playwright() as pw:
        g = f"EVGCLID{TS}"
        grab(pw, "01-gclid-desktop", P,
             f"?gclid={g}&utm_source=google&utm_medium=cpc&utm_campaign={g}CAMP"
             f"&utm_term={g}TERM&utm_content={g}CONT", "desktop",
             "correct GCLID test")
        time.sleep(4)
        b = f"EVGBRAID{TS}"
        grab(pw, "02-gbraid-mobile", C,
             f"?gbraid={b}&utm_source=google&utm_medium=cpc&utm_campaign={b}CAMP"
             f"&utm_term={b}TERM&utm_content={b}CONT", "mobile",
             "correct GBRAID test")
        time.sleep(4)
        w = f"EVWBRAID{TS}"
        grab(pw, "03-wbraid-desktop", f"{BASE}/hvac-installation/",
             f"?wbraid={w}&utm_source=google&utm_medium=cpc&utm_campaign={w}CAMP"
             f"&utm_term={w}TERM&utm_content={w}CONT", "desktop",
             "correct WBRAID test")
        time.sleep(4)
        grab(pw, "04-no-parameters", P, "", "desktop", "no-parameter control")
        time.sleep(4)
        grab(pw, "05-forms-and-duplicate-ids", f"{BASE}/hvac-repair/", "", "desktop",
             "form count + duplicate-ID result")
        time.sleep(4)
        grab(pw, "06-gtm-whatconverts", f"{BASE}/gas-boiler-repair/", "", "desktop",
             "GTM + WhatConverts")
    print(f"\nWROTE evidence to {EVID}")
    print("FORMS SUBMITTED: 0 | TEL LINKS ACTIVATED: 0 | WEBSITE CHANGES: 0")


if __name__ == "__main__":
    sys.exit(main())
