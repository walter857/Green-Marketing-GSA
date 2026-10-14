#!/usr/bin/env python3
"""PLAN-R1B actions T-3 through T-8. Approved fingerprint B7AD76CB16F8.

ONE browser. ONE page load. ONE fill. ONE submit click. Never a retry.

Hard guards:
  * SUBMIT_CLICKS is asserted to be exactly 1 at the end.
  * The submit control is clicked once and the handle is then discarded.
  * If Gravity Forms rejects the reserved test phone, the run STOPS and no
    substitute number is ever tried.
No Google Ads call. No mutation. No phone call.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
SHOT = ROOT / "clients/softwind-power-washing/receipts"

PAGE = "https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/"
PARAMS = {
    "gclid": "GM-TEST-SYNTHETIC-GCLID-20260901",
    "gbraid": "GM-TEST-SYNTHETIC-GBRAID-20260901",
    "wbraid": "GM-TEST-SYNTHETIC-WBRAID-20260901",
    "utm_source": "google", "utm_medium": "cpc", "utm_campaign": "gm-conversion-test",
    "utm_term": "power+washing+near+me", "utm_content": "plan-r1b",
}
ARRIVAL = PAGE + "?" + "&".join(f"{k}={v}" for k, v in PARAMS.items())

TEST_NAME = "GM TEST DO NOT CONTACT"
TEST_PHONE = "631-555-0147"
TEST_EMAIL = "access@greenmarketing.com"
TEST_NOTE = ("Green Marketing conversion tracking test - not a customer - submitted "
             "2026-09-02 - please delete after verification.")

OWN = "18369652705"
OWN_LABEL = "FddkCOul59scEOHPqrdE"
FOREIGN = "17878095007"

SUBMIT_CLICKS = 0


def classify(url: str) -> str:
    if "/pagead/conversion/" in url and "/wcm" in url:
        return "WEBSITE_CALL_REPLACEMENT"
    if "/pagead/attribution/wcm" in url:
        return "WEBSITE_CALL_ATTRIBUTION"
    if "/pagead/conversion/" in url or "/pagead/1p-conversion/" in url:
        return "CONVERSION"
    if "viewthroughconversion" in url:
        return "PAGE_VIEW_REMARKETING"
    if "1p-user-list" in url or "rmkt/collect" in url:
        return "USER_LIST_REMARKETING"
    if "/ccm/collect" in url:
        return "CONSENT_MODE_COLLECT"
    return "OTHER"


def acct(url: str) -> str:
    m = re.search(r"/(?:conversion|viewthroughconversion|1p-conversion|1p-user-list|"
                  r"rmkt/collect)/(\d{9,12})", url)
    return m.group(1) if m else ""


def main() -> int:
    global SUBMIT_CLICKS
    now = datetime.now(ZoneInfo("America/New_York"))
    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    reqs: list[dict] = []
    responses: list[dict] = []
    console: list[str] = []
    out: dict = {
        "plan_id": "PLAN-R1B", "fingerprint": "B7AD76CB16F8",
        "actions": ["T-3", "T-4", "T-5", "T-6", "T-7", "T-8"],
        "started_account_local": now.isoformat(),
        "test_identity": {"name": TEST_NAME, "phone": TEST_PHONE, "email": TEST_EMAIL},
        "google_ads_mutations": 0, "calls_placed": 0,
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()

        def on_req(r):
            body = ""
            if r.method == "POST":
                try:
                    body = (r.post_data or "")[:4000]
                except Exception:
                    body = "<unavailable>"
            reqs.append({"t": datetime.now(ZoneInfo("America/New_York")).isoformat(),
                         "method": r.method, "url": r.url, "type": r.resource_type,
                         "post_data": body})

        def on_resp(r):
            responses.append({"url": r.url, "status": r.status})

        page.on("request", on_req)
        page.on("response", on_resp)
        page.on("console", lambda m: console.append(f"{m.type}: {m.text[:200]}"))

        # ---------------- arrive ----------------
        resp = page.goto(ARRIVAL, wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(6000)
        out["arrival"] = {"http_status": resp.status if resp else None,
                          "final_url": page.url,
                          "sgcaptcha_in_chain": any("sgcaptcha" in r["url"] for r in reqs)}
        pre_n = len(reqs)
        out["beacons_before_submit"] = [
            {"account": acct(r["url"]), "kind": classify(r["url"]), "url": r["url"][:260]}
            for r in reqs if classify(r["url"]) not in ("OTHER",)]
        page.screenshot(path=str(SHOT / f"r1b-t3-before-{stamp}.png"), full_page=False)

        # ---------------- T-3 fill ----------------
        # DEFECT: form#gform_1 is DUPLICATED on the page - every DOM id appears
        # TWICE (hero form ~400px, second form ~5305px). Bare id selectors are
        # ambiguous, so scope every action to the FIRST (hero) form and address
        # fields by NAME within that scope.
        forms = page.locator("form#gform_1")
        out["duplicate_form_count"] = forms.count()
        form = forms.nth(0)
        form.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)
        # CORRECTION 2026-09-02: input_9 is a Gravity Forms HONEYPOT
        # (gfield--type-honeypot / gform_validation_container, display:none,
        # autocomplete="new-password"). PLAN-R1B and PLAN-A2 both mislabel it as
        # "Full Name". Filling it would flag the submission as SPAM and Gravity
        # Forms would silently discard the lead. It is LEFT EMPTY. The real name
        # field is input_1. Not a fingerprinted field, so B7AD76CB16F8 is unchanged.
        out["honeypot_field_left_empty"] = "input_9"
        out["corrected_field_map"] = {
            "input_1": "Full Name (real)", "input_4": "Phone",
            "input_3": "Email", "input_7": "Project",
            "input_9": "HONEYPOT - NOT FILLED"}
        out["field_labels"] = page.evaluate("""() => {
            const f = document.querySelector('form#gform_1');
            const o = {};
            f.querySelectorAll('.gfield').forEach(g => {
                const inp = g.querySelector('input:not([type=hidden]),textarea');
                const lab = g.querySelector('label,legend');
                if (inp) o[inp.name] = (lab ? lab.innerText.trim() : '').slice(0, 60);
            });
            return o; }""")
        for nm, val in (("input_1", TEST_NAME),
                        ("input_4", TEST_PHONE), ("input_3", TEST_EMAIL),
                        ("input_7", TEST_NOTE)):
            sel = f"textarea[name={nm}]" if nm == "input_7" else f"input[name={nm}]"
            form.locator(sel).first.fill(val, timeout=45000)
        out["filled_values_readback"] = form.evaluate("""f => ({
            input_9_honeypot_must_be_empty: f.querySelector('[name=input_9]')?.value,
            input_1: f.querySelector('[name=input_1]')?.value,
            input_4: f.querySelector('[name=input_4]')?.value,
            input_3: f.querySelector('[name=input_3]')?.value,
            input_7: (f.querySelector('[name=input_7]')?.value || '').slice(0, 60)
        })""")

        submit_ts = datetime.now(ZoneInfo("America/New_York"))
        out["submission_timestamp_account_local"] = submit_ts.isoformat()

        # ---------------- T-3 submit, EXACTLY ONCE ----------------
        assert SUBMIT_CLICKS == 0, "guard: submit already performed"
        btn = page.query_selector("#gform_submit_button_1") or \
            page.query_selector("input[type=submit], button[type=submit]")
        out["submit_control"] = btn.get_attribute("id") if btn else None
        if btn is None:
            out["ERROR"] = "submit control not found - NOTHING SUBMITTED"
            browser.close()
            (SNAP / f"r1b-t3-t8-{stamp}.json").write_text(
                json.dumps(out, indent=2, default=str), encoding="utf-8")
            print(json.dumps(out, indent=2, default=str))
            return 2
        btn.click(timeout=45000)
        SUBMIT_CLICKS += 1
        btn = None
        try:
            page.wait_for_load_state("networkidle", timeout=90000)
        except Exception as exc:
            out["post_submit_wait_note"] = str(exc)[:200]
        page.wait_for_timeout(9000)

        # ---------------- T-4 confirmation behaviour ----------------
        post = reqs[pre_n:]
        form_posts = [r for r in post if r["method"] == "POST"
                      and "offer.softwindli.com" in r["url"]]
        conf = page.evaluate("""() => {
            const err = document.querySelector('.gform_validation_errors, .validation_error');
            const errs = [...document.querySelectorAll('.gfield_error .validation_message,'
                          + ' .validation_message')].map(e => e.innerText.trim()).slice(0, 12);
            const c = document.querySelector('.gform_confirmation_message,'
                      + ' .gform_confirmation_wrapper, #gform_confirmation_message_1');
            const still = !!document.querySelector('form#gform_1');
            return { validation_banner: err ? err.innerText.trim().slice(0, 300) : null,
                     field_errors: errs,
                     confirmation_text: c ? c.innerText.trim().slice(0, 500) : null,
                     form_still_present: still,
                     title: document.title };
        }""")
        page.screenshot(path=str(SHOT / f"r1b-t3-after-{stamp}.png"), full_page=False)
        out["T4_form_and_confirmation"] = {
            "submit_clicks": SUBMIT_CLICKS,
            "final_url_after_submit": page.url,
            "redirected": page.url.split("?")[0] != PAGE,
            "http_statuses_for_page": [r["status"] for r in responses
                                       if r["url"].split("?")[0] == PAGE],
            "form_post_count": len(form_posts),
            "form_post_urls": [r["url"][:160] for r in form_posts],
            "post_body_field_echo": [
                {k: v for k, v in
                 (dict(p.split("=", 1) for p in r["post_data"].split("&")
                       if "=" in p and p.split("=", 1)[0] in
                       ("input_9", "input_1", "input_4", "input_3", "is_submit_1",
                        "gform_submit"))).items()}
                for r in form_posts if r["post_data"]],
            "validation_banner": conf["validation_banner"],
            "field_errors": conf["field_errors"],
            "confirmation_text": conf["confirmation_text"],
            "form_still_present": conf["form_still_present"],
            "page_title": conf["title"],
            "sgcaptcha_after_submit": [r["url"][:150] for r in post if "sgcaptcha" in r["url"]],
            "console_errors": [c for c in console if c.startswith("error")][:10],
            "automatic_retry_detected": len(form_posts) > 1,
        }

        # phone rejection guard
        blob = " ".join(conf["field_errors"] + [conf["validation_banner"] or ""]).lower()
        out["phone_rejected"] = any(k in blob for k in ("phone", "telephone", "number"))
        out["STOPPED_ON_PHONE_REJECTION"] = bool(out["phone_rejected"])

        # ---------------- T-5 / T-6 beacons after submit ----------------
        beacons = [{"t": r["t"], "account": acct(r["url"]), "kind": classify(r["url"]),
                    "url": r["url"][:300]} for r in post
                   if classify(r["url"]) != "OTHER"]
        out["beacons_after_submit"] = beacons
        own_conv = [b for b in beacons if b["account"] == OWN and b["kind"] == "CONVERSION"]
        own_label_hits = [b for b in beacons if OWN_LABEL in b["url"]]
        for_conv = [b for b in beacons if b["account"] == FOREIGN and b["kind"] == "CONVERSION"]
        out["T5_softwind_conversion"] = {
            "expected_account": f"AW-{OWN}", "expected_label": OWN_LABEL,
            "conversion_requests_to_own_account": len(own_conv),
            "requests_carrying_expected_label": len(own_label_hits),
            "endpoints": [b["url"] for b in own_conv],
            "label_endpoints": [b["url"] for b in own_label_hits],
            "fired": bool(own_conv or own_label_hits),
            "synthetic_gclid_present": any("GM-TEST-SYNTHETIC-GCLID" in b["url"]
                                           for b in own_conv + own_label_hits),
        }
        out["T6_foreign_tag"] = {
            "account": f"AW-{FOREIGN}",
            "by_kind": {k: len([b for b in beacons if b["account"] == FOREIGN
                                and b["kind"] == k])
                        for k in ("CONVERSION", "PAGE_VIEW_REMARKETING",
                                  "USER_LIST_REMARKETING", "WEBSITE_CALL_REPLACEMENT",
                                  "WEBSITE_CALL_ATTRIBUTION")},
            "form_conversion_requests": len(for_conv),
            "wcm_requests_total_session": len([r for r in reqs
                                               if classify(r["url"]).startswith("WEBSITE_CALL")]),
            "carries_synthetic_gclid": any("GM-TEST-SYNTHETIC-GCLID" in b["url"]
                                           for b in beacons if b["account"] == FOREIGN),
            "endpoints": [b["url"] for b in beacons if b["account"] == FOREIGN][:12],
        }

        # ---------------- T-7 destination signals visible from the browser ----------------
        out["T7_destination_signals"] = {
            "note": ("Direct record inspection of WordPress, WhatConverts and any CRM "
                     "requires credentials this session does not hold. What follows is "
                     "what the browser could observe."),
            "third_party_posts_at_submit": [
                {"url": r["url"][:160], "method": r["method"]} for r in post
                if r["method"] == "POST" and "offer.softwindli.com" not in r["url"]],
            "whatconverts_host_requests": [r["url"][:160] for r in reqs
                                           if "whatconverts" in r["url"].lower()],
            "wc_cookies": {c["name"]: c["value"][:120] for c in ctx.cookies()
                           if c["name"].startswith("wc_")},
            "utm_term_in_post_body": any("utm_term" in (r["post_data"] or "")
                                         for r in form_posts),
            "gclid_in_post_body": any("GM-TEST-SYNTHETIC-GCLID" in (r["post_data"] or "")
                                      for r in form_posts),
            "gbraid_in_post_body": any("GM-TEST-SYNTHETIC-GBRAID" in (r["post_data"] or "")
                                       for r in form_posts),
            "wbraid_in_post_body": any("GM-TEST-SYNTHETIC-WBRAID" in (r["post_data"] or "")
                                       for r in form_posts),
        }
        out["total_requests"] = len(reqs)
        browser.close()

    assert SUBMIT_CLICKS == 1, f"GUARD FAILED: {SUBMIT_CLICKS} submit clicks"
    out["submit_clicks_final"] = SUBMIT_CLICKS
    out["screenshots"] = [f"receipts/r1b-t3-before-{stamp}.png",
                          f"receipts/r1b-t3-after-{stamp}.png"]
    path = SNAP / f"r1b-t3-t8-{stamp}.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("beacons_after_submit", "beacons_before_submit")},
                     indent=2, default=str))
    print("\n--- BEACONS AFTER SUBMIT ---")
    for b in out["beacons_after_submit"]:
        print(f"  {b['account'] or '-':12} {b['kind']:26} {b['url'][:150]}")
    print("\nWROTE", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
