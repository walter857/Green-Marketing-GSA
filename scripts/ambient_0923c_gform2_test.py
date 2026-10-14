#!/usr/bin/env python3
"""Ambient | 2026-09-23 | ONE authorised main-site test after registering #gform_2.

WhatConverts form 208722 (#gform_2) was added to profile 105803 on 2026-09-23 beside the
existing 205016 (#gform_1). This submits the main-site form ONCE and records whether the
WhatConverts capture request fires.

Identity and label are the owner-approved QA values from 2026-09-22.

Fixes over ambient_0922_form_test.py:
  * the WhatConverts tracker is served from ksrndkehqnwntyxlhgto.com, not a host named
    "whatconverts", so the old detector could never see a capture. This one matches the
    real host and the /lead/form endpoint.
  * "confirmed" now means the Gravity Forms confirmation element for form 2 exists, not a
    word such as "we will" appearing anywhere in the page chrome.
  * the profile script body actually served to the page is checked for #gform_2, so a
    stale or cached copy cannot pass silently.
  * every field, select and checkbox is visibility-checked; hidden (honeypot) inputs are
    never touched.

Safety: NO URL parameters (shared proxy cache), no ad clicked, no click id, no upload.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-23c"
LABEL = "TEST - DO NOT DISPATCH"
EMAIL = "walter@greenmarketingfl.com"
PHONE = "+584242773462"
MSG = (f"{LABEL}. Green Marketing WhatConverts form 208722 verification "
       f"{datetime.date.today().isoformat()}. Please do not dispatch a technician, do not "
       f"call back and do not treat this as a customer enquiry.")
URL = "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/"
WC_HOST = re.compile(r"ksrndkehqnwntyxlhgto\.com|whatconverts", re.I)
WC_FORM = re.compile(r"ksrndkehqnwntyxlhgto\.com/lead/form", re.I)
PROFILE_JS = re.compile(r"ksrndkehqnwntyxlhgto\.com/105803\.js", re.I)
CONV = re.compile(r"/pagead/1p-conversion|/pagead/conversion|/ccm/collect", re.I)

VISIBLE = """(e)=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);
  return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'
  &&!e.closest('.gform_validation_container,.gfield--type-honeypot,[aria-hidden=true]')}"""


def main():
    out = {"when": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP, "url": URL,
           "identity": {"email": EMAIL, "phone": PHONE, "label": LABEL},
           "parameterised_requests": 0, "ads_clicked": 0, "conversions_uploaded": 0,
           "submissions": 0}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        ctx = b.new_context(locale="en-US", timezone_id="America/New_York",
                            viewport={"width": 1440, "height": 950})
        pg = ctx.new_page()
        reqs, profile_bodies = [], []
        pg.on("request", lambda r: reqs.append({"url": r.url, "method": r.method}))

        def on_resp(r):
            if PROFILE_JS.search(r.url):
                try:
                    profile_bodies.append(r.text())
                except Exception:
                    profile_bodies.append("")
        pg.on("response", on_resp)

        r = pg.goto(URL, wait_until="domcontentloaded", timeout=70000)
        out["status"] = r.status if r else None
        pg.wait_for_timeout(2500)
        pg.mouse.move(420, 300)          # NitroPack defers JS until interaction
        pg.mouse.wheel(0, 1600)
        pg.keyboard.press("PageDown")
        pg.wait_for_timeout(9000)

        out["profile_js_loaded"] = len(profile_bodies)
        out["profile_js_has_gform_2"] = any('"#gform_2"' in x for x in profile_bodies)
        out["wc_cookies"] = sorted(c["name"] for c in ctx.cookies()
                                   if c["name"].startswith("wc_"))
        if not out["profile_js_has_gform_2"]:
            out["abort"] = "served profile script does not contain #gform_2; not submitting"
            print(json.dumps(out, indent=1))
            b.close()
            return

        forms = pg.query_selector_all("form#gform_2")
        out["gform_2_instances"] = len(forms)
        target = None
        for i, f in enumerate(forms):
            if f.evaluate(VISIBLE):
                target, out["instance_used"] = f, i
                break
        if target is None:
            out["abort"] = "no visible #gform_2"
            print(json.dumps(out, indent=1))
            b.close()
            return

        # field map by label, measured on the live form, never inherited
        fields = target.evaluate("""(f)=>[...f.querySelectorAll('input,textarea,select')]
          .map(e=>{const l=e.id?f.querySelector('label[for="'+e.id+'"]'):null;
            const g=e.closest('.gfield');
            const gl=g?g.querySelector('.gfield_label,legend'):null;
            return {id:e.id,type:e.type||e.tagName.toLowerCase(),tag:e.tagName,
              label:((l&&l.innerText)||(gl&&gl.innerText)||'').trim().slice(0,40)}})""")
        vis = {}
        for fd in fields:
            if fd["id"]:
                el = target.query_selector(f"#{fd['id']}")
                vis[fd["id"]] = bool(el and el.evaluate(VISIBLE))
        out["field_map"] = [dict(fd, visible=vis.get(fd["id"], False)) for fd in fields]

        filled = []

        def put(el, val):
            el.fill(val)
            filled.append({"id": el.get_attribute("id"), "value": val[:40]})

        for fd in out["field_map"]:
            if not fd["visible"] or not fd["id"]:
                continue
            el = target.query_selector(f"#{fd['id']}")
            lab, t = fd["label"].lower(), fd["type"]
            if t in ("hidden", "submit", "button", "checkbox", "radio"):
                continue
            if t == "email":
                put(el, EMAIL)
            elif t == "tel" or "phone" in lab or "contact number" in lab:
                put(el, PHONE)
            elif fd["tag"] == "TEXTAREA":
                put(el, MSG)
            elif fd["tag"] == "SELECT":
                opts = el.evaluate("s=>[...s.options].map(o=>o.value).filter(Boolean)")
                if "state" in lab:
                    pick = next((o for o in opts if o.lower() == "maryland"), None)
                else:
                    pick = next((o for o in opts
                                 if "heat" in o.lower() or "furnace" in o.lower()),
                                opts[0] if opts else None)
                if pick:
                    el.select_option(pick)
                    filled.append({"id": fd["id"], "value": pick[:40]})
            elif "last" in lab:
                put(el, LABEL)
            elif "first" in lab or "name" in lab:
                put(el, "TEST")
            elif "zip" in lab or "postal" in lab:
                put(el, "21104")
            elif "street" in lab:
                put(el, LABEL)           # clearly not a real address
            elif lab == "city":
                put(el, "TEST")
        # non-marketing consent only; marketing consent stays unticked
        for cb in target.query_selector_all("input[type=checkbox]"):
            if not cb.evaluate(VISIBLE):
                continue
            lab = (cb.evaluate("e=>{const l=document.querySelector('label[for=\"'+e.id+'\"]');"
                               "return l?l.innerText:''}") or "").lower()
            if "non-marketing" not in lab:       # marketing consent is never ticked
                continue
            cb.check()
            filled.append({"id": cb.get_attribute("id"), "value": "checked"})
        out["fields_filled"] = filled
        out["hidden_inputs_touched"] = 0
        req_empty = target.evaluate(
            f"""(f)=>{{const V={VISIBLE};return [...f.querySelectorAll('.gfield_contains_required')]
              .flatMap(g=>[...g.querySelectorAll('input:not([type=hidden]),textarea,select')])
              .filter(e=>V(e)&&!e.value).map(e=>e.id)}}""")
        out["required_left_empty"] = req_empty
        if req_empty:
            out["abort"] = f"required fields still empty: {req_empty}; not submitting"
            print(json.dumps({k: out[k] for k in ("fields_filled", "abort")}, indent=1))
            b.close()
            return

        before = len(reqs)
        btn = target.query_selector("input[type=submit],button[type=submit]")
        out["submit_button"] = btn.get_attribute("id") if btn else None
        btn.click()
        out["submissions"] = 1
        pg.wait_for_timeout(15000)
        after = reqs[before:]
        out["after_url"] = pg.url
        out["gf_confirmation"] = pg.evaluate(
            "()=>{const c=document.querySelector('#gform_confirmation_message_2,"
            ".gform_confirmation_message_2');return c?c.innerText.trim().slice(0,200):null}")
        out["gf_validation_errors"] = pg.evaluate(
            "()=>[...document.querySelectorAll('.gform_validation_errors,.gfield_error')]"
            ".map(e=>e.innerText.trim().slice(0,80))")
        out["wc_requests_after_submit"] = [{"m": x["method"], "u": x["url"][:90]}
                                           for x in after if WC_HOST.search(x["url"])]
        out["wc_lead_form_posts"] = sum(1 for x in after if WC_FORM.search(x["url"]))
        out["google_conversion_pings"] = [x["url"][:110] for x in after
                                          if CONV.search(x["url"])]
        b.close()

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"form-test-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for k in ("status", "profile_js_loaded", "profile_js_has_gform_2", "wc_cookies",
              "gform_2_instances", "instance_used", "submit_button", "after_url",
              "gf_confirmation", "gf_validation_errors", "wc_lead_form_posts"):
        print(f"{k:24s}: {out.get(k)}")
    print(f"{'fields_filled':24s}: {[f['id'] for f in out.get('fields_filled', [])]}")
    print(f"{'wc requests after submit':24s}: {out.get('wc_requests_after_submit')}")
    print(f"{'google conversion pings':24s}: {len(out.get('google_conversion_pings', []))}")
    print(f"\nWROTE {p}\nSUBMISSIONS: {out['submissions']} | PARAMETERS: 0 | ADS CLICKED: 0")


if __name__ == "__main__":
    main()
