#!/usr/bin/env python3
"""Ambient | 2026-09-17 | INDEPENDENT TRACKING RETEST of the two launch URLs.

SAFETY DESIGN -- READ THIS BEFORE CHANGING ANYTHING.

The 2026-09-16 verification proved attribution is still populated SERVER-SIDE and the
rendered HTML is stored by the SiteGround full-page proxy cache. Sending a request with a
synthetic GCLID can therefore write that GCLID into the cached page that REAL visitors are
served. The standing instruction is that a developer must be on standby to purge the cache
immediately after any parameterised request. No such standby is confirmed right now, so
THIS SCRIPT SENDS ZERO PARAMETERISED REQUESTS. Every visit is a clean, no-parameter visit.

That is not a weaker test -- it is the stronger one. Parameterised QA runs earlier today
(scripts/ambient_0917_url_qa.py) already pushed the marker "174247" through all seven
pages. If a clean, no-parameter visitor is handed those values back, that is conclusive
proof of cross-visitor cache replay, and it costs no new writes to the cache.

No form is submitted. No tel: link is activated. No CAPTCHA is bypassed. No real visitor
data or real click ID is retained.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-17"
BASE = "https://ambientcoolingandheating.com"
LAUNCH = {"furnace-repair", "mini-splits"}
PAGES = {
    "furnace-repair": "/services/heating-services/furnace-repair/",
    "mini-splits": "/services/cooling-services/mini-splits/",
    "heat-pumps": "/services/heating-services/heat-pumps/",
    "boiler-repair": "/services/heating-services/boiler-repair/",
    "heating-services-hub": "/services/heating-services/",
    "oil-furnace-installations": "/services/heating-services/oil-furnace-installations/",
    "oil-replacement": "/services/heating-services/oil-replacement/",
}
# Markers pushed into these pages by EARLIER authorised parameterised QA runs. Finding any
# of them in a clean no-parameter visit proves cross-visitor replay.
FOREIGN_MARKERS = ["174247", "QA-HEAT-", "QA0916", "T140501", "T140122", "QA0915"]
AW_ID = "11155434808"
MIXED_NUMBER = "410-914-1456"          # must never appear or be clickable
PAID_NUMBER = "410-705-6354"           # WhatConverts paid tracking number
DEST_NUMBER = "410-761-0932"           # real destination number
PHONE_RE = re.compile(r"\(?\b(\d{3})\)?[\s.\-]?(\d{3})[\s.\-]?(\d{4})\b")

DEVICES = {
    # Do NOT override the desktop UA: the spoofed Windows UA draws a 403 from the
    # host's bot protection, while the default Chromium UA is served normally.
    "desktop": dict(viewport={"width": 1440, "height": 900}, is_mobile=False,
                    has_touch=False, device_scale_factor=1),
    "mobile": dict(viewport={"width": 390, "height": 844}, is_mobile=True,
                   has_touch=True, device_scale_factor=3,
                   user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                              "Version/17.5 Mobile/15E148 Safari/604.1"),
}

PROBE = """() => {
  const norm = s => (s || '').replace(/[\\s().\\-]/g, '');
  const inputs = [...document.querySelectorAll('input,textarea,select')].map(el => ({
    id: el.id || '', name: el.getAttribute('name') || '',
    type: (el.getAttribute('type') || el.tagName).toLowerCase(),
    hidden: el.type === 'hidden',
    value: (el.value === undefined || el.value === null) ? '' : String(el.value)
  }));
  const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
  const dup = {}; ids.forEach(i => dup[i] = (dup[i] || 0) + 1);
  const tel = [...document.querySelectorAll('a[href^="tel:"]')].map(a => ({
    href: a.getAttribute('href'), digits: norm(a.getAttribute('href')),
    text: (a.innerText || '').trim().slice(0, 40),
    visible: !!(a.offsetWidth || a.offsetHeight || a.getClientRects().length)
  }));
  let dl = [];
  try { dl = (window.dataLayer || []).map(x => { try { return JSON.stringify(x).slice(0, 220); }
        catch (e) { return String(x).slice(0, 120); } }); } catch (e) {}
  const ls = {}; try { for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i); ls[k] = String(localStorage.getItem(k)).slice(0, 220); } } catch (e) {}
  const ss = {}; try { for (let i = 0; i < sessionStorage.length; i++) {
      const k = sessionStorage.key(i); ss[k] = String(sessionStorage.getItem(k)).slice(0, 220); } } catch (e) {}
  return {
    inputs, tel, dataLayer: dl, localStorage: ls, sessionStorage: ss,
    duplicate_ids: Object.entries(dup).filter(([, n]) => n > 1).map(([i, n]) => [i, n]),
    total_ids: ids.length,
    forms: [...document.querySelectorAll('form')].map(f => ({
      id: f.id || '', action: (f.getAttribute('action') || '').slice(0, 120),
      fields: f.querySelectorAll('input,textarea,select').length,
      submit: !!f.querySelector('input[type=submit],button[type=submit],button:not([type])'),
      visible: !!(f.offsetWidth || f.offsetHeight)
    })),
    body_text: (document.body ? document.body.innerText : '').slice(0, 200000),
    has_gtm_object: typeof window.google_tag_manager !== 'undefined',
    gtm_containers: (() => { try { return Object.keys(window.google_tag_manager || {})
        .filter(k => /^(GTM|G|AW)-/.test(k)); } catch (e) { return []; } })(),
    has_gtag: typeof window.gtag === 'function',
    has_wc: !!(window.__wc || window.whatconverts || window.wc_track || window.WhatConverts),
    wc_globals: Object.keys(window).filter(k => /whatconv|^wc_|^__wc/i.test(k)).slice(0, 12),
    title: document.title.slice(0, 120), url: location.href
  };
}"""


def visit(ctx, url):
    """One clean, no-parameter visit. Returns the probe plus network evidence."""
    net, doc_headers, status = [], {}, None
    page = ctx.new_page()
    page.on("request", lambda r: net.append(r.url))

    def on_resp(r):
        nonlocal doc_headers, status
        if r.url.split("#")[0].rstrip("/") == url.rstrip("/") and not doc_headers:
            try:
                doc_headers = dict(r.headers)
                status = r.status
            except Exception:
                pass
    page.on("response", on_resp)

    last = None
    for attempt in range(4):
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if resp is not None and status is None:
                status = resp.status
                doc_headers = dict(resp.headers)
            # SG-Captcha answers automation with HTTP 202 + a meta-refresh stub. A real
            # browser solves it; give the redirect time to land rather than calling it a
            # page failure.
            page.wait_for_timeout(3500)
            html_len = page.evaluate("() => document.documentElement.outerHTML.length")
            if html_len > 20000:
                break
            page.wait_for_timeout(3000)
        except Exception as ex:
            last = str(ex)[:200]
            page.wait_for_timeout(2000)
    # --- NitroPack defers ALL JavaScript until the first user interaction. Probing
    # before interacting reports GTM, GA4, the Google Ads tag and WhatConverts as absent.
    # Capture the pre-interaction state (the deferral is itself a finding), then interact.
    pre = {"requests": len(net),
           "gtm": any("googletagmanager.com/gtm.js" in u for u in net),
           "ga4": any("/g/collect" in u for u in net),
           "aw": any(AW_ID in u for u in net),
           "wc": any("whatconverts" in u.lower() for u in net)}
    try:
        page.mouse.move(400, 300)
        page.mouse.move(700, 500)
        page.mouse.wheel(0, 1200)
        page.keyboard.press("PageDown")
        page.wait_for_timeout(6000)
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(5000)
    except Exception as ex:
        last = str(ex)[:200]
    data = None
    for _ in range(3):                        # execution context can die mid-redirect
        try:
            data = page.evaluate(PROBE)
            break
        except Exception as ex:
            last = str(ex)[:200]
            page.wait_for_timeout(1500)
    cookies = ctx.cookies() if data else []
    out = {"url": url, "status": status, "error": last if data is None else None,
           "pre_interaction": pre,
           "headers": {k: v for k, v in doc_headers.items()
                       if k.lower() in ("x-proxy-cache", "x-nitro-cache", "host-header",
                                        "cache-control", "content-type", "age",
                                        "x-cache", "cf-cache-status", "vary")},
           "network": net, "cookies": [{"name": c["name"], "value": str(c["value"])[:160],
                                        "domain": c["domain"]} for c in cookies],
           "probe": data}
    page.close()
    return out


def analyse(v):
    """Turn one visit into per-requirement evidence."""
    net = v["network"]; p = v["probe"] or {}
    joined = " ".join(net)
    a = {}
    a["pre_interaction"] = v.get("pre_interaction")
    a["scripts_deferred_until_interaction"] = bool(
        v.get("pre_interaction") and not v["pre_interaction"]["gtm"])
    a["gtm_loaded"] = ("googletagmanager.com/gtm.js" in joined
                       or bool(p.get("has_gtm_object")))
    a["gtm_containers"] = p.get("gtm_containers", [])
    a["ga4_loaded"] = bool(re.search(r"gtag/js\?id=G-|google-analytics\.com/g/collect"
                                     r"|googletagmanager\.com/g/collect", joined))
    a["ga4_hits"] = [u[:120] for u in net if "/g/collect" in u][:3]
    # The Google Ads tag loads through GTM, so a DOM-only check reports a false absence.
    # Score it on real network traffic carrying the conversion ID.
    a["aw_loaded"] = AW_ID in joined
    a["aw_requests"] = [u[:140] for u in net if AW_ID in u][:4]
    a["wc_loaded"] = ("whatconverts" in joined.lower() or bool(p.get("has_wc"))
                      or bool(p.get("wc_globals")))
    a["wc_requests"] = [u[:120] for u in net if "whatconverts" in u.lower()][:3]
    cookies = {c["name"]: c["value"] for c in v["cookies"]}
    a["cookies_present"] = sorted(cookies)
    a["wc_visitor"] = cookies.get("wc_visitor")
    a["wc_swap"] = cookies.get("wc_swap")
    a["gcl_cookies"] = {k: val for k, val in cookies.items() if k.startswith("_gcl")}

    # --- the decisive check: does a CLEAN visitor receive foreign attribution? ---
    inputs = p.get("inputs", [])
    foreign = []
    for el in inputs:
        val = (el.get("value") or "").strip()
        if not val:
            continue
        for m in FOREIGN_MARKERS:
            if m in val:
                foreign.append({"id": el.get("id"), "name": el.get("name"),
                                "value": val[:80], "marker": m})
                break
    a["foreign_attribution_in_fields"] = foreign
    # Any non-empty attribution-shaped field on a no-parameter visit is contamination,
    # whether or not it carries one of our own markers.
    ATTR = re.compile(r"gclid|gbraid|wbraid|utm_|campaign|keyword|adgroup|click",
                      re.IGNORECASE)
    nonempty_attr = [{"id": el.get("id"), "name": el.get("name"),
                      "value": (el.get("value") or "")[:80]}
                     for el in inputs
                     if (el.get("value") or "").strip()
                     and (ATTR.search(el.get("name") or "") or ATTR.search(el.get("id") or "")
                          or ATTR.search(el.get("value") or ""))]
    a["nonempty_attribution_fields"] = nonempty_attr
    a["hidden_field_values"] = [{"id": el.get("id"), "value": (el.get("value") or "")[:60]}
                                for el in inputs if el.get("hidden")
                                and (el.get("value") or "").strip()][:20]

    # --- phone numbers ---
    text = p.get("body_text", "")
    seen = set()
    for m in PHONE_RE.finditer(text):
        seen.add(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
    a["numbers_displayed"] = sorted(seen)
    tel = p.get("tel", [])
    a["tel_links"] = tel
    a["tel_digits"] = sorted({t["digits"].replace("tel:", "") for t in tel})
    mixed_digits = MIXED_NUMBER.replace("-", "")
    a["mixed_number_in_text"] = MIXED_NUMBER in text or mixed_digits in text.replace("-", "").replace(" ", "")
    a["mixed_number_clickable"] = any(mixed_digits in t["digits"] for t in tel)
    disp = {n.replace("-", "") for n in seen}
    telset = {t["digits"].replace("tel:", "").lstrip("+1") for t in tel}
    a["tel_not_displayed"] = sorted(telset - disp)
    a["displayed_not_tel"] = sorted(disp - telset)
    a["paid_number_present"] = PAID_NUMBER.replace("-", "") in "".join(disp) or \
        PAID_NUMBER.replace("-", "") in "".join(telset)

    # --- forms / DOM ---
    a["duplicate_ids"] = p.get("duplicate_ids", [])
    a["forms"] = p.get("forms", [])
    a["cache"] = {k: v["headers"].get(k) for k in
                  ("x-proxy-cache", "x-nitro-cache", "age", "host-header")}
    return a


def main():
    res = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "mode": "INDEPENDENT TRACKING RETEST - clean no-parameter visitors only",
           "parameterised_requests_sent": 0, "forms_submitted": 0,
           "tel_links_activated": 0, "captcha_bypass_attempted": False,
           "website_changes": 0, "google_ads_changes": 0,
           "why_no_parameters": "Attribution is populated server-side and cached by the "
                                "SiteGround full-page proxy cache (proven 2026-09-16). A "
                                "synthetic GCLID could be served to real visitors. No "
                                "developer cache-purge standby is confirmed, so no "
                                "parameterised request was sent.",
           "visits": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for name, path in PAGES.items():
            for dev, cfg in DEVICES.items():
                url = BASE + path
                # Fresh isolated context => no cookies, no storage carried over.
                ctx = browser.new_context(locale="en-US",
                                          timezone_id="America/New_York", **cfg)
                try:
                    v = visit(ctx, url)
                    v.update({"page": name, "device": dev,
                              "launch_critical": name in LAUNCH})
                    v["analysis"] = analyse(v)
                    v.pop("network", None)
                    if v.get("probe"):
                        v["probe"].pop("body_text", None)
                    res["visits"].append(v)
                    an = v["analysis"]
                    print(f"{name:26s} {dev:7s} status={v['status']} "
                          f"cache={an['cache'].get('x-proxy-cache')} "
                          f"GTM={an['gtm_loaded']} GA4={an['ga4_loaded']} "
                          f"AW={an['aw_loaded']} WC={an['wc_loaded']} "
                          f"foreign={len(an['foreign_attribution_in_fields'])} "
                          f"dupIDs={len(an['duplicate_ids'])}")
                except Exception as ex:
                    res["visits"].append({"page": name, "device": dev,
                                          "fatal": str(ex)[:300]})
                    print(f"{name:26s} {dev:7s} FATAL {str(ex)[:120]}")
                finally:
                    ctx.close()
        browser.close()
    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"tracking-retest-{STAMP}.json"
    p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("PARAMETERISED REQUESTS SENT: 0 | FORMS SUBMITTED: 0 | TEL ACTIVATED: 0")


if __name__ == "__main__":
    main()
