#!/usr/bin/env python3
"""PLAN-R1B actions T-1 and T-2 ONLY. Approved fingerprint B7AD76CB16F8.

T-1  Load the arrival URL in instrumented Chromium with network capture armed.
T-2  Snapshot every persisted identifier BEFORE touching the form.

THIS SCRIPT NEVER SUBMITS THE FORM. It never clicks a submit control, never calls
form.submit(), and never issues a POST. T-3 is gated on preconditions R1B-PRE-2,
R1B-PRE-3 and R1B-PRE-4, which are NOT MET.
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

PAGE = "https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/"
PARAMS = {
    "gclid": "GM-TEST-SYNTHETIC-GCLID-20260901",
    "gbraid": "GM-TEST-SYNTHETIC-GBRAID-20260901",
    "wbraid": "GM-TEST-SYNTHETIC-WBRAID-20260901",
    "utm_source": "google", "utm_medium": "cpc", "utm_campaign": "gm-conversion-test",
    "utm_term": "power washing near me", "utm_content": "plan-r1b",
}
ARRIVAL = PAGE + "?" + "&".join(f"{k}={v.replace(' ', '%20')}" for k, v in PARAMS.items())

OWN_TAG = "AW-18369652705"
FOREIGN_TAG = "AW-17878095007"
APPROVED_PHONE = "6315027946"

BEACON_HOSTS = ("googleadservices.com", "google.com/pagead", "googletagmanager.com",
                "google-analytics.com", "analytics.google.com", "doubleclick.net",
                "whatconverts", "clickcease", "facebook.com", "facebook.net")


def profile(pw, name: str, device: dict | None):
    browser = pw.chromium.launch()
    ctx = browser.new_context(**device) if device else browser.new_context()
    page = ctx.new_page()
    requests: list[dict] = []
    console: list[str] = []

    def on_request(req):
        requests.append({"method": req.method, "url": req.url,
                         "type": req.resource_type})
    page.on("request", on_request)
    page.on("console", lambda m: console.append(f"{m.type}: {m.text[:200]}"))

    resp = page.goto(ARRIVAL, wait_until="networkidle", timeout=90000)
    page.wait_for_timeout(6000)          # let deferred tags fire
    final_url = page.url
    status = resp.status if resp else None

    # ---------- tags present ----------
    aw_ids = sorted(set(re.findall(r"AW-\d{9,12}", " ".join(r["url"] for r in requests))))
    html = page.content()
    aw_in_html = sorted(set(re.findall(r"AW-\d{9,12}", html)))
    ga4 = sorted(set(re.findall(r"G-[A-Z0-9]{8,12}", html)))
    gtm = sorted(set(re.findall(r"GTM-[A-Z0-9]{6,10}", html)))

    # ---------- persisted identifiers ----------
    storage = page.evaluate("""() => {
        const grab = (s) => { const o = {}; try { for (let i = 0; i < s.length; i++) {
            const k = s.key(i); o[k] = (s.getItem(k) || '').slice(0, 300); } } catch (e) {}
            return o; };
        return { local: grab(localStorage), session: grab(sessionStorage) };
    }""")
    cookies = {c["name"]: c["value"][:300] for c in ctx.cookies()}

    # ---------- form inspection, READ ONLY ----------
    form = page.evaluate("""() => {
        const f = document.querySelector('form#gform_1, form[id^="gform_"]');
        if (!f) return null;
        const fields = [...f.querySelectorAll('input,textarea,select')].map(e => ({
            name: e.name || '', id: e.id || '', type: e.type || e.tagName.toLowerCase(),
            required: !!e.required,
            hidden: e.type === 'hidden' || getComputedStyle(e).display === 'none',
            value: (e.type === 'hidden' ? (e.value || '').slice(0, 300) : '')
        }));
        return { id: f.id, action: f.action, method: f.method,
                 visible: fields.filter(x => !x.hidden).length,
                 hidden: fields.filter(x => x.hidden).length, fields };
    }""")

    # ---------- phone rendering ----------
    tels = page.eval_on_selector_all(
        "a[href^='tel:']", "els => els.map(e => e.getAttribute('href'))")
    body_txt = page.evaluate("() => document.body.innerText")
    phones_in_text = sorted(set(re.findall(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", body_txt)))

    # ---------- identifier persistence ----------
    blob = json.dumps({"storage": storage, "cookies": cookies, "form": form})
    persistence = {}
    for k, v in PARAMS.items():
        persistence[k] = {
            "in_final_url": v.replace(" ", "%20") in final_url or v in final_url,
            "in_storage_or_cookie_or_hidden_field": v in blob,
        }

    ctx.close()
    browser.close()
    return {
        "profile": name,
        "http_status": status,
        "arrival_url": ARRIVAL,
        "final_url": final_url,
        "redirected": final_url.split("?")[0] != PAGE,
        "total_requests": len(requests),
        "google_ads_tag_ids_in_network": aw_ids,
        "google_ads_tag_ids_in_html": aw_in_html,
        "own_tag_present": OWN_TAG in aw_ids or OWN_TAG in aw_in_html,
        "foreign_tag_present": FOREIGN_TAG in aw_ids or FOREIGN_TAG in aw_in_html,
        "ga4_ids": ga4, "gtm_ids": gtm,
        "whatconverts_loaded": any("whatconverts" in r["url"] for r in requests),
        "clickcease_loaded": any("clickcease" in r["url"] for r in requests),
        "conversion_beacons_before_submit": [
            r["url"][:300] for r in requests
            if any(h in r["url"] for h in ("googleadservices.com/pagead/conversion",
                                           "google.com/pagead/1p-conversion",
                                           "/pagead/conversion/"))],
        "tracking_hosts_contacted": sorted({h for h in BEACON_HOSTS
                                            for r in requests if h in r["url"]}),
        "identifier_persistence": persistence,
        "wc_swap_cookie": cookies.get("wc_swap", "ABSENT"),
        "cookie_names": sorted(cookies),
        "storage_keys": {"local": sorted(storage["local"]),
                         "session": sorted(storage["session"])},
        "tel_links": sorted(set(tels)),
        "phones_in_body_text": phones_in_text,
        "approved_phone_rendered": any(APPROVED_PHONE in (t or "").replace("-", "")
                                       .replace(" ", "").replace("(", "").replace(")", "")
                                       for t in tels),
        "form": form,
        "console_errors": [c for c in console if c.startswith("error")][:10],
        "FORM_SUBMITTED": False,
    }


def main() -> int:
    now = datetime.now(ZoneInfo("America/New_York"))
    out = {
        "plan_id": "PLAN-R1B",
        "fingerprint": "B7AD76CB16F8",
        "approved_by": "Walter Correa",
        "actions_executed": ["T-1", "T-2"],
        "actions_not_executed": ["T-3", "T-4", "T-5", "T-6", "T-7", "T-8"],
        "halt_reason": ("T-3 is an EXTERNAL WRITE gated on preconditions R1B-PRE-2 "
                        "(test email), R1B-PRE-3 (client notified) and R1B-PRE-4 "
                        "(named cleanup owner). All three are NOT MET."),
        "form_submitted": False,
        "call_placed": False,
        "google_ads_mutations": 0,
        "executed_account_local": now.isoformat(),
        "profiles": [],
    }
    with sync_playwright() as pw:
        out["profiles"].append(profile(pw, "desktop", None))
        out["profiles"].append(profile(pw, "mobile", {
            "viewport": {"width": 390, "height": 844},
            "user_agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                           "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                           "Mobile/15E148 Safari/604.1"),
            "is_mobile": True, "has_touch": True, "device_scale_factor": 3,
        }))
    path = SNAP / f"r1b-t1-t2-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    for p in out["profiles"]:
        print(f"\n===== {p['profile'].upper()} =====")
        for k in ("http_status", "redirected", "total_requests",
                  "google_ads_tag_ids_in_network", "google_ads_tag_ids_in_html",
                  "own_tag_present", "foreign_tag_present", "ga4_ids", "gtm_ids",
                  "whatconverts_loaded", "clickcease_loaded",
                  "conversion_beacons_before_submit", "tracking_hosts_contacted",
                  "wc_swap_cookie", "tel_links", "phones_in_body_text",
                  "approved_phone_rendered", "console_errors"):
            print(f"  {k}: {p[k]}")
        print("  identifier_persistence:")
        for k, v in p["identifier_persistence"].items():
            print(f"    {k:14} url={v['in_final_url']!s:5} "
                  f"storage/cookie/hidden={v['in_storage_or_cookie_or_hidden_field']}")
        f = p["form"]
        if f:
            print(f"  form: id={f['id']} method={f['method']} visible={f['visible']} "
                  f"hidden={f['hidden']}")
            print(f"    action={f['action'][:110]}")
            for fl in f["fields"]:
                if not fl["hidden"]:
                    print(f"    VISIBLE {fl['type']:9} name={fl['name']:12} "
                          f"id={fl['id']:14} required={fl['required']}")
            for fl in f["fields"]:
                if fl["hidden"] and fl["value"]:
                    print(f"    HIDDEN  {fl['name']:22} = {fl['value'][:90]}")
        else:
            print("  form: NOT FOUND")
        print(f"  FORM_SUBMITTED: {p['FORM_SUBMITTED']}")
    print("\nWROTE", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
