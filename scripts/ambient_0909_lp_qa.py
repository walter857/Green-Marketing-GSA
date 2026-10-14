#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | landing-page and tracking QA.

Renders every active final URL in a real JavaScript-enabled Chromium on both a
desktop and a mobile profile. GET navigations only: no form is submitted, no
tel: link is activated, nothing on the site is modified.

These pages sit behind SG-Captcha, which serves non-JS clients an empty stub,
so a plain fetch produces a false "no tracking" finding. A real browser is
mandatory here.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-09"

BASE = "https://offer.ambientcoolingandheating.com"
PAGES = {
    "AC Repair": f"{BASE}/ac-repair/",
    "HVAC Repair": f"{BASE}/hvac-repair/",
    "HVAC Installation": f"{BASE}/hvac-installation/",
    "HVAC Replacement": f"{BASE}/hvac-replacement/",
    "Gas Boiler Repair": f"{BASE}/gas-boiler-repair/",
}
# Expected service-specific H2 for the three-step block, per the work order.
EXPECTED_STEP_H2 = {
    "AC Repair": "Your AC Repair in 3 Simple Steps",
    "HVAC Repair": "Your HVAC Repair in 3 Simple Steps",
    "HVAC Installation": "Your HVAC Installation in 3 Simple Steps",
    "HVAC Replacement": "Your HVAC Replacement in 3 Simple Steps",
    "Gas Boiler Repair": "Your Gas Boiler Repair in 3 Simple Steps",
}
APPROVED_PAID = "4107056354"
WC_POOL = "4109141456"
MAIN_SITE = "4107610932"
UNEXPLAINED = "4104159517"
GTM_ID = "GTM-PQTPQ436"

BARRED = [
    r"open 24/7", r"24/7 live", r"24/7 answer", r"emergency service",
    r"guaranteed response", r"same[- ]day service",
]

UA_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")

PHONE_RE = re.compile(r"\(?\b(\d{3})\)?[\s.‑-]?(\d{3})[\s.‑-]?(\d{4})\b")
TRACKERS = {
    "gtm_container": re.compile(r"\bGTM-[A-Z0-9]{5,9}\b"),
    "google_ads_gtag": re.compile(r"\bAW-\d{9,12}\b"),
    "ga4_measurement": re.compile(r"\bG-[A-Z0-9]{8,12}\b"),
    "whatconverts": re.compile(r"whatconverts", re.I),
    "clickcease": re.compile(r"clickcease", re.I),
}
GCLID_TEST = ("?gclid=QA0827TEST&utm_source=google&utm_medium=cpc"
              "&utm_campaign=qa-readonly&utm_term=qa&utm_content=qa")


def digits(s):
    return re.sub(r"\D", "", s)


def audit_one(ctx, service, url, profile, with_params):
    page = ctx.new_page()
    net = []
    page.on("request", lambda r: net.append(r.url))
    target = url + (GCLID_TEST if with_params else "")
    rec = {"service": service, "url": target, "profile": profile,
           "click_params_sent": with_params}
    try:
        resp = page.goto(target, wait_until="networkidle", timeout=60000)
        rec["http_status"] = resp.status if resp else None
        page.wait_for_timeout(3500)
        html = page.content()
        text = page.inner_text("body")
        rec["final_url"] = page.url
        rec["title"] = page.title()
        rec["render_ok"] = len(text.strip()) > 400
        rec["body_text_len"] = len(text)

        rec["canonical"] = page.eval_on_selector(
            "link[rel=canonical]", "e => e.href") if page.query_selector(
            "link[rel=canonical]") else ""
        rec["h1"] = [h.inner_text().strip() for h in page.query_selector_all("h1")]
        rec["h2"] = [h.inner_text().strip() for h in page.query_selector_all("h2")]
        rec["h3"] = [h.inner_text().strip() for h in page.query_selector_all("h3")][:12]

        # phone numbers, displayed and in tel: links
        rec["phones_displayed"] = sorted({
            "".join(m.groups()) for m in PHONE_RE.finditer(text)})
        tels = []
        for a in page.query_selector_all("a[href^='tel:']"):
            tels.append({"href": a.get_attribute("href"),
                         "text": (a.inner_text() or "").strip()})
        rec["tel_links"] = tels
        rec["tel_digits"] = sorted({digits(t["href"]) for t in tels})

        # trackers, from rendered DOM and from actual network requests
        blob = html + "\n" + "\n".join(net)
        rec["trackers"] = {k: sorted(set(v.findall(blob)))[:6] if k in (
            "gtm_container", "google_ads_gtag", "ga4_measurement")
            else bool(v.search(blob)) for k, v in TRACKERS.items()}
        rec["gtm_expected_present"] = GTM_ID in blob
        rec["network_hosts"] = sorted({re.sub(r"^https?://([^/]+).*", r"\1", u)
                                       for u in net})[:40]

        # click-ID / UTM capture into the form
        hidden = []
        for i in page.query_selector_all("input[type=hidden]"):
            hidden.append({"name": i.get_attribute("name") or i.get_attribute("id") or "",
                           "value": (i.get_attribute("value") or "")[:120]})
        rec["hidden_fields"] = hidden
        rec["gclid_captured_in_form"] = any(
            "QA0827TEST" in (h["value"] or "") for h in hidden)
        rec["utm_captured_in_form"] = any(
            "qa-readonly" in (h["value"] or "") for h in hidden)
        try:
            store = page.evaluate(
                "() => ({ls: Object.keys(localStorage||{}).slice(0,40),"
                " cookies: document.cookie.split('; ').map(c=>c.split('=')[0]).slice(0,60)})")
        except Exception:  # noqa: BLE001
            store = {"ls": [], "cookies": []}
        rec["storage_keys"] = store
        rec["wc_swap_cookie_present"] = any(
            "wc_swap" in c for c in store.get("cookies", []))
        rec["gclid_in_storage"] = bool(page.evaluate(
            "() => JSON.stringify({l:localStorage, c:document.cookie}).includes('QA0827TEST')"))

        # forms, without submitting
        forms = []
        for f in page.query_selector_all("form"):
            fields = []
            for el in f.query_selector_all("input, textarea, select"):
                fields.append({"name": el.get_attribute("name") or "",
                               "type": el.get_attribute("type") or el.evaluate("e=>e.tagName"),
                               "required": el.get_attribute("required") is not None})
            forms.append({"action": f.get_attribute("action") or "",
                          "method": f.get_attribute("method") or "",
                          "id": f.get_attribute("id") or "",
                          "field_count": len(fields), "fields": fields[:14]})
        rec["forms"] = forms

        # duplicate DOM ids
        ids = page.evaluate(
            "() => Array.from(document.querySelectorAll('[id]')).map(e=>e.id)")
        seen, dup = set(), set()
        for i in ids:
            if i in seen:
                dup.add(i)
            seen.add(i)
        rec["duplicate_dom_ids"] = sorted(dup)[:25]
        rec["duplicate_dom_id_count"] = len(dup)

        # policy / privacy links
        links = [(a.get_attribute("href") or "", (a.inner_text() or "").strip())
                 for a in page.query_selector_all("a[href]")]
        rec["privacy_link"] = [h for h, t in links if re.search(r"privacy", h + t, re.I)][:3]
        rec["terms_link"] = [h for h, t in links
                             if re.search(r"terms|conditions", h + t, re.I)][:3]

        # barred claims
        rec["barred_claims_found"] = [p for p in BARRED
                                      if re.search(p, text, re.I)]

        # step H2 check
        want = EXPECTED_STEP_H2[service]
        step = [h for h in rec["h2"] + rec["h3"] if "3 Simple Steps" in h]
        rec["step_headings_found"] = step
        rec["step_heading_correct"] = any(want.lower() in h.lower() for h in step)
        cross = [h for h in step if not any(
            want.lower() in h.lower() for _ in [0])]
        rec["step_heading_cross_service"] = [
            h for h in step if want.lower() not in h.lower()]

        # cross-service copy: another service name in the H1
        others = {k for k in PAGES if k != service}
        rec["cross_service_in_h1"] = [
            o for o in others
            if any(o.lower() in h.lower() for h in rec["h1"])]

        # mobile layout: horizontal overflow
        rec["horizontal_overflow"] = page.evaluate(
            "() => document.documentElement.scrollWidth > window.innerWidth + 2")
        rec["viewport"] = page.viewport_size
    except Exception as exc:  # noqa: BLE001
        rec["error"] = str(exc)[:400]
    finally:
        page.close()
    return rec


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "read_only": True,
           "method": "Playwright Chromium, JS enabled, GET only, no form submitted, "
                     "no tel: link activated"}
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for profile, ua, vp, mobile in (
                ("desktop", UA_DESKTOP, {"width": 1440, "height": 900}, False),
                ("mobile", UA_MOBILE, {"width": 390, "height": 844}, True)):
            ctx = browser.new_context(
                user_agent=ua, viewport=vp, is_mobile=mobile,
                has_touch=mobile, device_scale_factor=3 if mobile else 1,
                locale="en-US", timezone_id="America/New_York")
            for service, url in PAGES.items():
                for with_params in (False, True):
                    r = audit_one(ctx, service, url, profile, with_params)
                    results.append(r)
                    err = r.get("error", "")
                    print(f"  {profile:7s} params={str(with_params):5s} {service:18s} "
                          f"HTTP={r.get('http_status')} render={r.get('render_ok')} "
                          f"{'ERR: ' + err if err else ''}")
            ctx.close()
        browser.close()
    out["results"] = results

    # ---------- consolidated verdicts ----------
    print("\n== CONSOLIDATED LANDING-PAGE VERDICTS ==")
    verdicts = {}
    for service in PAGES:
        rs = [r for r in results if r["service"] == service and "error" not in r]
        if not rs:
            verdicts[service] = {"status": "ERROR", "detail": "no successful render"}
            print(f"  {service:18s} ERROR")
            continue
        phones = sorted({p for r in rs for p in r["phones_displayed"]})
        tels = sorted({t for r in rs for t in r["tel_digits"]})
        v = {
            "http_status": sorted({r["http_status"] for r in rs}),
            "render_ok": all(r["render_ok"] for r in rs),
            "canonical": sorted({r["canonical"] for r in rs}),
            "h1": sorted({h for r in rs for h in r["h1"]}),
            "step_headings": sorted({h for r in rs for h in r["step_headings_found"]}),
            "step_heading_correct": all(r["step_heading_correct"] for r in rs),
            "expected_step_heading": EXPECTED_STEP_H2[service],
            "cross_service_in_h1": sorted({c for r in rs for c in r["cross_service_in_h1"]}),
            "phones_displayed": phones,
            "tel_link_digits": tels,
            "approved_paid_number_displayed": APPROVED_PAID in phones or APPROVED_PAID in tels,
            "wc_pool_number_seen": WC_POOL in phones or WC_POOL in tels,
            "main_site_number_seen": MAIN_SITE in phones or MAIN_SITE in tels,
            "unexplained_number_seen": UNEXPLAINED in phones or UNEXPLAINED in tels,
            "gtm_present": all(r["gtm_expected_present"] for r in rs),
            "whatconverts_present": all(r["trackers"]["whatconverts"] for r in rs),
            "clickcease_present": all(r["trackers"]["clickcease"] for r in rs),
            "google_ads_ids": sorted({x for r in rs for x in r["trackers"]["google_ads_gtag"]}),
            "ga4_ids": sorted({x for r in rs for x in r["trackers"]["ga4_measurement"]}),
            "gtm_ids": sorted({x for r in rs for x in r["trackers"]["gtm_container"]}),
            "gclid_captured": any(r["gclid_captured_in_form"] for r in rs if r["click_params_sent"]),
            "utm_captured": any(r["utm_captured_in_form"] for r in rs if r["click_params_sent"]),
            "gclid_in_storage": any(r["gclid_in_storage"] for r in rs if r["click_params_sent"]),
            "wc_swap_cookie": any(r["wc_swap_cookie_present"] for r in rs),
            "form_count": sorted({len(r["forms"]) for r in rs}),
            "duplicate_dom_ids": sorted({d for r in rs for d in r["duplicate_dom_ids"]}),
            "privacy_link": sorted({x for r in rs for x in r["privacy_link"]}),
            "terms_link": sorted({x for r in rs for x in r["terms_link"]}),
            "barred_claims": sorted({b for r in rs for b in r["barred_claims_found"]}),
            "mobile_horizontal_overflow": any(
                r["horizontal_overflow"] for r in rs if r["profile"] == "mobile"),
        }
        verdicts[service] = v
        print(f"\n  --- {service} ---")
        for k in ("http_status", "render_ok", "h1", "step_headings",
                  "step_heading_correct", "cross_service_in_h1",
                  "phones_displayed", "tel_link_digits",
                  "approved_paid_number_displayed", "wc_pool_number_seen",
                  "main_site_number_seen", "unexplained_number_seen",
                  "gtm_present", "gtm_ids", "google_ads_ids", "ga4_ids",
                  "whatconverts_present", "clickcease_present",
                  "gclid_captured", "utm_captured", "gclid_in_storage",
                  "wc_swap_cookie", "form_count", "duplicate_dom_ids",
                  "privacy_link", "terms_link", "barred_claims",
                  "mobile_horizontal_overflow"):
            print(f"     {k:34s} {v[k]}")
    out["verdicts"] = verdicts

    # ---------- the Gas Boiler gate ----------
    gb = verdicts.get("Gas Boiler Repair", {})
    gate = {
        "expected_h2": EXPECTED_STEP_H2["Gas Boiler Repair"],
        "observed_step_headings": gb.get("step_headings", []),
        "pass": bool(gb.get("step_heading_correct")),
        "keyword_package_3D823A10CB3C0B25": (
            "UNBLOCKED - rebuild the package from current state"
            if gb.get("step_heading_correct")
            else "STILL BLOCKED - do not execute"),
    }
    out["gas_boiler_gate"] = gate
    print("\n== GAS BOILER LANDING-PAGE GATE ==")
    for k, v in gate.items():
        print(f"  {k:38s} {v}")

    SNAP.mkdir(parents=True, exist_ok=True)
    path = SNAP / f"lp-browser-qa-{STAMP}.json"
    path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {path}")
    return out


if __name__ == "__main__":
    main()
