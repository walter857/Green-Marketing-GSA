#!/usr/bin/env python3
"""Ambient | 2026-09-22 | AUTHORISED production form test. ONE per form integration.

Owner authorised on 2026-09-22: identity walter@greenmarketingfl.com / +584242773462,
label "TEST - DO NOT DISPATCH", one submission per distinct form integration.

Safety rules applied:
  * NO URL parameters. The SiteGround full-page proxy cache is shared and no purge method
    is available here, so a synthetic click id could be cached and replayed to real
    visitors. This test therefore proves the FORM -> WhatConverts -> conversion path; it
    does NOT prove Google Ads click-id attribution.
  * The honeypot is never filled. On the offer form it is input_1_27, labelled "Name" and
    hidden from humans - a DIFFERENT id from other clients, so the map was measured here
    rather than inherited. Filling it would make a working form look broken.
  * The main site renders TWO forms with the same id gform_2, so fields are targeted by
    element inside the chosen form, never by getElementById, which returns only the first.
  * Marketing consent is NOT ticked. Only the non-marketing/transactional consent is used.
  * ONE submission per integration. No ad is clicked and no conversion is uploaded.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-22"
LABEL = "TEST - DO NOT DISPATCH"
EMAIL = "walter@greenmarketingfl.com"
PHONE = "+584242773462"
MSG = (f"{LABEL}. Green Marketing tracking verification submitted "
       f"{datetime.date.today().isoformat()}. Please do not dispatch a technician, do not "
       f"call back and do not treat this as a customer enquiry. Contact Green Marketing "
       f"with any question about this record.")

TARGETS = [
    {"key": "main-site gform_2",
     "url": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
     "form_index": 0,
     "fields": [("input[id^='input_2_1']:not([id*='_17']):not([id*='_18']):not([id*='_19'])",
                 "TEST"),
                ("input[id$='_2_17']", LABEL),
                ("input[type=email]", EMAIL),
                ("input[type=tel]", PHONE),
                ("textarea", MSG)],
     "honeypot_ids": []},
    {"key": "offer gform_1",
     "url": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
     "form_index": 1,
     "fields": [("input[id$='_1_1']", f"TEST {LABEL}"),
                ("input[type=tel]", PHONE),
                ("input[type=email]", EMAIL),
                ("textarea", MSG)],
     "honeypot_ids": ["input_1_27"]},
]
WC = re.compile(r"whatconverts", re.I)
GADS = re.compile(r"googleadservices|google\.com/(pagead|ccm)|doubleclick", re.I)


def run(b, t):
    ctx = b.new_context(locale="en-US", timezone_id="America/New_York",
                        viewport={"width": 1440, "height": 950})
    pg = ctx.new_page()
    net = []
    pg.on("request", lambda r: net.append(r.url))
    rec = {"target": t["key"], "url": t["url"], "label": LABEL,
           "parameterised": False, "honeypot_filled": False}
    try:
        r = pg.goto(t["url"], wait_until="domcontentloaded", timeout=70000)
        rec["status"] = r.status if r else None
        pg.wait_for_timeout(2500)
        pg.mouse.wheel(0, 1600)
        pg.keyboard.press("PageDown")
        pg.wait_for_timeout(7000)

        forms = pg.query_selector_all("form")
        rec["forms_on_page"] = len(forms)
        # choose the first form that is actually visible to a human
        target = None
        for i, f in enumerate(forms):
            box = f.bounding_box()
            if box and box["width"] > 50 and box["height"] > 50:
                target = f
                rec["form_chosen_index"] = i
                rec["form_chosen_id"] = f.get_attribute("id")
                break
        if target is None:
            rec["error"] = "no visible form found"
            return rec

        filled = []
        for sel, val in t["fields"]:
            els = target.query_selector_all(sel)
            for e in els:
                eid = e.get_attribute("id") or ""
                if eid in t["honeypot_ids"]:
                    continue
                box = e.bounding_box()
                if not box or box["width"] == 0:
                    continue
                e.fill(val)
                filled.append({"id": eid, "selector": sel, "value": val[:50]})
                break
        # service dropdown, where present
        for s in target.query_selector_all("select"):
            opts = [o.get_attribute("value") or "" for o in s.query_selector_all("option")]
            pick = next((o for o in opts if o and "heat" in o.lower()), None) \
                or next((o for o in opts if o), None)
            if pick:
                try:
                    s.select_option(pick)
                    filled.append({"id": s.get_attribute("id") or "", "value": pick})
                except Exception:
                    pass
        # non-marketing consent only
        for cb in target.query_selector_all("input[type=checkbox]"):
            lid = cb.get_attribute("id") or ""
            if "_19_" in lid:
                try:
                    cb.check()
                    filled.append({"id": lid, "value": "consent(non-marketing) checked"})
                except Exception:
                    pass
        rec["fields_filled"] = filled

        # confirm the honeypot is still empty
        for hid in t["honeypot_ids"]:
            h = pg.query_selector(f"#{hid}")
            rec["honeypot_value_before_submit"] = h.input_value() if h else None
            rec["honeypot_filled"] = bool(h and h.input_value())

        rec["cookies_before"] = {x["name"]: x["value"][:48] for x in ctx.cookies()
                                 if x["name"].startswith("wc_")}
        rec["hidden_values_before"] = pg.evaluate("""(idx)=>{
            const f=[...document.querySelectorAll('form')][idx];
            return [...f.querySelectorAll('input[type=hidden]')]
              .filter(e=>e.id).map(e=>({id:e.id, value:(e.value||'').slice(0,60)}))
              .filter(x=>x.value)}""", rec["form_chosen_index"])

        before = len(net)
        btn = target.query_selector("input[type=submit], button[type=submit]") \
            or target.query_selector("button:not([type])")
        rec["submit_button"] = btn.get_attribute("id") if btn else None
        btn.click()
        pg.wait_for_timeout(12000)
        rec["after_url"] = pg.url
        body = pg.evaluate("()=>document.body?document.body.innerText:''")
        rec["confirmation_text"] = re.sub(r"\s+", " ", body)[:400]
        rec["looks_confirmed"] = bool(re.search(
            r"thank you|received|we will|success|submitted", body, re.I))
        after = net[before:]
        rec["whatconverts_calls_after_submit"] = [u[:170] for u in after if WC.search(u)]
        rec["google_ads_calls_after_submit"] = [u[:170] for u in after if GADS.search(u)]
        rec["conversion_pings"] = [u[:170] for u in after
                                   if re.search(r"/pagead/1p-conversion|/ccm/collect|"
                                                r"conversion/", u, re.I)]
        rec["cookies_after"] = {x["name"]: x["value"][:48] for x in ctx.cookies()
                                if x["name"].startswith("wc_")}
    except Exception as ex:
        rec["error"] = str(ex)[:300]
    finally:
        ctx.close()
    return rec


def main():
    out = {"when": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "authorised_by_owner": "2026-09-22",
           "identity": {"email": EMAIL, "phone": PHONE, "label": LABEL},
           "parameterised_requests": 0, "ads_clicked": 0, "conversions_uploaded": 0,
           "submissions": []}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for t in TARGETS:
            r = run(b, t)
            out["submissions"].append(r)
            print(f"\n{'=' * 78}\n{t['key']}")
            print(f"  status={r.get('status')} form={r.get('form_chosen_id')} "
                  f"(index {r.get('form_chosen_index')} of {r.get('forms_on_page')})")
            print(f"  honeypot filled: {r.get('honeypot_filled')}")
            print(f"  fields: {[f.get('id') for f in r.get('fields_filled', [])]}")
            print(f"  submitted -> {r.get('after_url')}")
            print(f"  confirmed: {r.get('looks_confirmed')}")
            print(f"  confirmation: {str(r.get('confirmation_text'))[:190]}")
            print(f"  WhatConverts calls after submit: "
                  f"{len(r.get('whatconverts_calls_after_submit', []))}")
            print(f"  Google Ads calls after submit  : "
                  f"{len(r.get('google_ads_calls_after_submit', []))}")
            print(f"  conversion pings               : "
                  f"{len(r.get('conversion_pings', []))}")
            for u in r.get("conversion_pings", [])[:4]:
                print(f"      {u}")
            if r.get("error"):
                print(f"  ERROR {r['error']}")
        b.close()
    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"form-test-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print(f"SUBMISSIONS: {len(out['submissions'])} | PARAMETERS SENT: 0 | "
          f"ADS CLICKED: 0 | CONVERSIONS UPLOADED: 0")


if __name__ == "__main__":
    main()
