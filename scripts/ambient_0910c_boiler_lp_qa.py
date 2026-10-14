#!/usr/bin/env python3
"""Gas Boiler landing-page completion gate.

Real browser, desktop + mobile. GET only. NO form is submitted and NO tel: link is
activated: no approved non-production/test path exists for this property, so a submission
would create a real customer lead and fire a real Google Ads conversion.

DNI is exercised with controlled paid-click parameters, which is a GET and creates nothing.
"""
from __future__ import annotations
import json, re, sys, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence"
SHOTS = ROOT / "reports" / "ambient-cooling-heating" / "evidence" / "boiler-lp-2026-09-10"
TZ = ZoneInfo("America/New_York")
UA_D = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_M = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
URL = "https://offer.ambientcoolingandheating.com/gas-boiler-repair/"
PAID = URL + ("?gclid=TESTgclidAmbientQA20260910&utm_source=google&utm_medium=cpc"
              "&utm_campaign=gas-boiler-repair&campaignid=24132507744"
              "&adgroupid=202339087594&keyword=gas%20boiler%20repair&matchtype=e"
              "&device=c&network=g")
PAID_NUM = "410) 705-6354"
PAID_DIGITS = "4107056354"
ORG_NUM = "410) 761-0932"
ORG_DIGITS = "4107610932"
GTM = "GTM-PQTPQ436"
SHOTS.mkdir(parents=True, exist_ok=True)
res = {"generated_local": datetime.datetime.now(TZ).isoformat(), "url": URL,
       "method": "Playwright Chromium, JS enabled, GET only. NO form submitted, NO tel: "
                 "activated, nothing published.",
       "form_submission": "BLOCKED - no approved non-production/test path exists for "
                          "offer.ambientcoolingandheating.com. Submitting on production "
                          "would create a real customer lead and fire a real Google Ads "
                          "conversion, contaminating the same conversion data these CPC "
                          "decisions depend on."}
V = {}


def verdict(k, ok, detail=""):
    V[k] = {"pass": bool(ok), "detail": detail}
    print(f"  [{'PASS' if ok else 'FAIL'}] {k}" + (f" - {detail}" if detail else ""))


with sync_playwright() as pw:
    b = pw.chromium.launch()
    for label, ua, vp, url in [("desktop", UA_D, {"width": 1440, "height": 2400}, URL),
                               ("mobile", UA_M, {"width": 390, "height": 1800}, URL),
                               ("desktop-paid", UA_D, {"width": 1440, "height": 2400}, PAID),
                               ("mobile-paid", UA_M, {"width": 390, "height": 1800}, PAID)]:
        ctx = b.new_context(user_agent=ua, viewport=vp,
                            is_mobile=label.startswith("mobile"),
                            has_touch=label.startswith("mobile"))
        pg = ctx.new_page()
        net = []
        pg.on("request", lambda r: net.append(r.url))
        r = pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(3500)
        html = pg.content()
        txt = re.sub(r"\s+", " ", pg.inner_text("body"))
        shot = SHOTS / f"{label}.png"
        pg.screenshot(path=str(shot), full_page=True)
        d = {"status": r.status if r else None, "title": pg.title(),
             "text_len": len(txt), "html_len": len(html),
             "screenshot": str(shot.relative_to(ROOT))}

        # phone numbers
        tel = pg.eval_on_selector_all(
            "a[href^='tel:']", "e=>e.map(x=>({href:x.getAttribute('href'),txt:x.innerText}))")
        d["tel_links"] = tel
        d["paid_number_in_text"] = PAID_NUM in txt
        d["org_number_in_text"] = ORG_NUM in txt
        d["org_number_in_html"] = ORG_DIGITS in re.sub(r"[^0-9a-zA-Z]", "", html)
        d["paid_number_in_html"] = PAID_DIGITS in re.sub(r"[^0-9a-zA-Z]", "", html)
        # headings
        d["h1"] = pg.eval_on_selector_all("h1", "e=>e.map(x=>x.innerText.trim())")
        d["h2"] = pg.eval_on_selector_all("h2", "e=>e.map(x=>x.innerText.trim())")[:12]
        can = pg.eval_on_selector_all("link[rel=canonical]", "e=>e.map(x=>x.href)")
        d["canonical"] = can
        # tracking
        d["gtm_in_html"] = GTM in html
        d["gtm_network"] = any(GTM in u for u in net)
        d["whatconverts_network"] = [u.split("?")[0] for u in net
                                     if "whatconverts" in u.lower()][:6]
        d["gtag_network"] = [u.split("?")[0] for u in net
                             if "googletagmanager.com/gtag" in u
                             or "google-analytics" in u][:6]
        d["adwords_conversion_network"] = [u.split("?")[0] for u in net
                                           if "googleads.g.doubleclick.net" in u
                                           or "/pagead/" in u][:6]
        # forms
        forms = pg.eval_on_selector_all(
            "form", "e=>e.map(x=>({id:x.id,action:x.getAttribute('action'),"
                    "method:x.method,nfields:x.querySelectorAll('input,select,textarea').length}))")
        d["forms"] = forms
        ids = pg.eval_on_selector_all("[id]", "e=>e.map(x=>x.id)")
        from collections import Counter as _C
        dupe = {k: v for k, v in _C(ids).items() if v > 1 and k}
        d["duplicate_dom_ids"] = dupe
        # hidden click-id fields
        hidden = pg.eval_on_selector_all(
            "input[type=hidden]", "e=>e.map(x=>({name:x.name,id:x.id,hasvalue:!!x.value}))")
        d["hidden_fields"] = [h for h in hidden if h.get("name")][:40]
        d["clickid_field_names"] = sorted({h["name"] for h in hidden if h.get("name") and
                                           re.search(r"gclid|gbraid|wbraid|utm|campaign|"
                                                     r"adgroup|keyword|source|medium",
                                                     h["name"], re.I)})
        d["clickid_fields_populated"] = sorted(
            {h["name"] for h in hidden if h.get("name") and h.get("hasvalue") and
             re.search(r"gclid|gbraid|wbraid|utm", h["name"], re.I)})
        # legal + stale copy
        links = pg.eval_on_selector_all(
            "a[href]", "e=>e.map(x=>({t:x.innerText.trim().toLowerCase(),h:x.href}))")
        d["privacy_link"] = [l["h"] for l in links if "privacy" in l["t"]
                             or "privacy" in l["h"].lower()][:3]
        d["terms_link"] = [l["h"] for l in links if "term" in l["t"]
                           or "terms" in l["h"].lower()][:3]
        d["boiler_3_steps"] = "Gas Boiler Repair in 3 Simple Steps" in txt
        d["stale_replacement_in_text"] = bool(re.search(r"hvac replacement", txt, re.I))
        d["stale_replacement_in_html"] = bool(re.search(r"hvac[\s_-]?replacement", html, re.I))
        d["stale_3steps_variants"] = re.findall(
            r"Your [A-Za-z ]{3,40} in 3 Simple Steps", txt)[:5]
        d["boiler_mentions"] = len(re.findall(r"boiler", txt, re.I))
        res.setdefault("renders", {})[label] = d
        ctx.close()
    b.close()

D = res["renders"]["desktop"]
M = res["renders"]["mobile"]
DP = res["renders"]["desktop-paid"]
MP = res["renders"]["mobile-paid"]

print("=== GAS BOILER LANDING PAGE GATE ===")
print(f"  {URL}")
for k in ("desktop", "mobile"):
    r = res["renders"][k]
    print(f"\n  --- {k} --- HTTP {r['status']}  title {r['title'][:70]!r}")
    print(f"    H1: {r['h1']}")
    print(f"    H2: {r['h2'][:6]}")
    print(f"    canonical: {r['canonical']}")
    print(f"    tel links: {r['tel_links']}")
    print(f"    forms: {r['forms']}")
    print(f"    boiler mentions: {r['boiler_mentions']}")
    print(f"    screenshot: {r['screenshot']}")

print("\n=== VERDICTS ===")
verdict("page loads 200 on desktop and mobile",
        D["status"] == 200 and M["status"] == 200, f"{D['status']} / {M['status']}")
verdict("heading reads 'Your Gas Boiler Repair in 3 Simple Steps'",
        D["boiler_3_steps"] and M["boiler_3_steps"],
        f"desktop={D['boiler_3_steps']} mobile={M['boiler_3_steps']} "
        f"variants={D['stale_3steps_variants']}")
verdict("old 'HVAC Replacement' wording absent from rendered TEXT",
        not D["stale_replacement_in_text"] and not M["stale_replacement_in_text"])
verdict("old 'HVAC Replacement' wording absent from HTML source",
        not D["stale_replacement_in_html"] and not M["stale_replacement_in_html"],
        "HTML still contains the string" if D["stale_replacement_in_html"] else "")
verdict("H1 present and boiler-specific", bool(D["h1"]) and
        any("boiler" in h.lower() for h in D["h1"]), str(D["h1"]))
verdict("canonical present", bool(D["canonical"]), str(D["canonical"]))
verdict("paid number (410) 705-6354 displayed", D["paid_number_in_text"])
verdict("paid number is a tel: link",
        any(PAID_DIGITS in (t.get("href") or "").replace("-", "").replace(" ", "")
            for t in D["tel_links"]), str(D["tel_links"]))
verdict("organic number (410) 761-0932 NEVER rendered on default load",
        not D["org_number_in_text"] and not M["org_number_in_text"])
verdict("organic number absent from HTML source too",
        not D["org_number_in_html"] and not M["org_number_in_html"],
        "present in HTML - can flash before swap" if D["org_number_in_html"] else "")
verdict(f"GTM {GTM} present", D["gtm_in_html"] or D["gtm_network"],
        f"html={D['gtm_in_html']} network={D['gtm_network']}")
verdict("WhatConverts script loaded", bool(D["whatconverts_network"]),
        str(D["whatconverts_network"][:2]))
verdict("Privacy link present", bool(D["privacy_link"]), str(D["privacy_link"][:1]))
verdict("Terms link present", bool(D["terms_link"]), str(D["terms_link"][:1]))
verdict("no duplicate DOM ids", not D["duplicate_dom_ids"],
        f"duplicates: {D['duplicate_dom_ids']}")

print("\n=== DNI UNDER PAID-CLICK PARAMETERS ===")
print(f"  desktop-paid: paid number shown={DP['paid_number_in_text']}  "
      f"organic shown={DP['org_number_in_text']}")
print(f"  mobile-paid : paid number shown={MP['paid_number_in_text']}  "
      f"organic shown={MP['org_number_in_text']}")
print(f"  desktop-paid tel links: {DP['tel_links']}")
verdict("paid number still correct under gclid parameters",
        DP["paid_number_in_text"] and MP["paid_number_in_text"])
verdict("organic number never appears under gclid parameters",
        not DP["org_number_in_text"] and not MP["org_number_in_text"])

print("\n=== CLICK-ID PERSISTENCE INTO THE FORM ===")
print(f"  hidden fields whose name looks attribution-related: {DP['clickid_field_names']}")
print(f"  of those, POPULATED on the paid load            : {DP['clickid_fields_populated']}")
verdict("form carries a gclid/utm field", bool(DP["clickid_field_names"]),
        str(DP["clickid_field_names"]))
verdict("that field is populated when a gclid is present",
        bool(DP["clickid_fields_populated"]), str(DP["clickid_fields_populated"]))

print("\n=== FORM SUBMISSION ===")
print("  NOT PERFORMED. " + res["form_submission"])
verdict("form submission + thank-you + one-conversion-per-submit verified", False,
        "BLOCKED - needs an approved non-production/test path or a staging clone")

npass = sum(1 for v in V.values() if v["pass"])
print(f"\n=== GATE RESULT: {npass}/{len(V)} PASS ===")
fails = [k for k, v in V.items() if not v["pass"]]
for f in fails:
    print(f"  OPEN: {f} - {V[f]['detail']}")
res["verdicts"] = V
res["gate_open_items"] = fails
res["gate_pass"] = not fails
(EVID / "2026-09-10c-boiler-lp-gate.json").write_text(
    json.dumps(res, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {(EVID / '2026-09-10c-boiler-lp-gate.json').relative_to(ROOT)}")
print(f"screenshots in {SHOTS.relative_to(ROOT)}")
