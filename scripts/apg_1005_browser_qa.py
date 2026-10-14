#!/usr/bin/env python3
"""2026-10-05 READ-ONLY browser QA for the Apogee paid page (no submissions, no clicks).

Uses Playwright with the installed Google Chrome (a real browser engine, so the SiteGround
challenge runs as it does for people). Every request that could record a conversion is
intercepted and ABORTED (googleadservices, pagead, ccm, doubleclick, rmkt) and logged by
path only, so we learn whether a tag WOULD fire without sending anything. The thank-you
probe additionally blocks WhatConverts. Hidden-field values are never stored or printed:
only whether each is empty and its length. No form is submitted and nothing is clicked.

    python scripts/apg_1005_browser_qa.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients" / "apogee-lawns" / "audits" / "2026-10-05-conversion-plan" / "browser-qa"
OUT.mkdir(parents=True, exist_ok=True)
LP = "https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/"
TY = "https://offer.apogeelawns.com/thank-you/permanent-christmas-lights/"
MAIN = "https://apogeelawns.com/permanent-holiday-lights-lincoln-ne/"
BLOCK_ADS = re.compile(r"googleadservices\.com|google\.com/pagead|google\.com/ccm|doubleclick\.net|google\.com/rmkt"
                       r"|googlesyndication\.com|google\.[a-z.]+/pagead")
BLOCK_WC = re.compile(r"ksrndkehqnwntyxlhgto\.com|whatconverts\.com")
NOTES = {
    "C1": "Reconfirm the current EverLights relationship and commercial availability before publication.",
    "C2": "Exact consultation steps and estimate timing require client confirmation.",
    "C3": "Exact installation timing and handoff process require client confirmation.",
}
EXTRACT = r"""
() => {
  const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const txt = el => (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
  const forms = [...document.querySelectorAll('form')].map(f => ({
    id: f.id, action: (f.getAttribute('action') || ''), method: f.method, visible: vis(f),
    fields: [...f.querySelectorAll('input,select,textarea')].map(i => {
      const lab = i.id ? document.querySelector(`label[for="${i.id}"]`) : null;
      const hidden = i.type === 'hidden' || !vis(i);
      return { name: i.name, id: i.id, type: i.type, required: i.required || i.getAttribute('aria-required') === 'true',
               label: lab ? txt(lab).slice(0, 80) : '', placeholder: i.placeholder || '',
               hidden, value_present: hidden ? (i.value || '').length > 0 : null,
               value_len: hidden ? (i.value || '').length : null, autocomplete: i.autocomplete || '' };
    }),
    submit: [...f.querySelectorAll('button,input[type=submit]')].map(b => txt(b) || b.value).slice(0, 3),
  }));
  const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
  const dupIds = [...new Set(ids.filter((v, i) => ids.indexOf(v) !== i))];
  const anchors = [...document.querySelectorAll('section[id],div[id],h2[id],h3[id]')]
     .filter(e => /^[a-z][a-z0-9_-]{2,}$/i.test(e.id) && !/^(gform|input_|field_|elementor|e-|wpforms)/i.test(e.id))
     .map(e => ({ id: e.id, tag: e.tagName, heading: txt(e.querySelector('h1,h2,h3') || e).slice(0, 70) }));
  const tel = [...document.querySelectorAll('a[href^="tel:"]')].map(a => ({ href: a.getAttribute('href'), text: txt(a).slice(0, 40), visible: vis(a) }));
  const phones = [...new Set((document.body.innerText.match(/\(?\d{3}\)?[-. ]?\d{3}[-. ]\d{4}/g) || []))];
  const fixed = [...document.querySelectorAll('body *')].filter(e => { const p = getComputedStyle(e).position;
     return (p === 'fixed' || p === 'sticky') && vis(e) && txt(e).length > 0; })
     .map(e => ({ tag: e.tagName, cls: (e.className || '').toString().slice(0, 60), text: txt(e).slice(0, 80),
                  rect: (r => [Math.round(r.top), Math.round(r.height), Math.round(r.width)])(e.getBoundingClientRect()) }));
  const imgs = [...document.images].filter(vis).map(i => ({ file: (i.currentSrc || i.src).split('/').pop().split('?')[0],
     host: (() => { try { return new URL(i.currentSrc || i.src).host } catch (e) { return '' } })(), alt: i.alt,
     w: i.naturalWidth, h: i.naturalHeight }));
  const headings = [...document.querySelectorAll('h1,h2,h3')].filter(vis).map(h => h.tagName + ': ' + txt(h).slice(0, 100));
  const dl = (window.dataLayer || []).map(e => (e && e.event) ? e.event : (Array.isArray(e) ? 'array:' + e[0] : typeof e));
  const gtm = window.google_tag_manager ? Object.keys(window.google_tag_manager).filter(k => /^(GTM-|AW-|G-)/.test(k)) : [];
  return { url: location.href, title: document.title, headings, forms, form_count: document.querySelectorAll('form').length,
           gform_instances: document.querySelectorAll('[id^="gform_wrapper_"]').length, dupIds: dupIds.slice(0, 40),
           dup_id_count: dupIds.length, anchors, tel, phones, fixed, imgs, datalayer_events: dl, gtm_objects: gtm,
           overflow_x: document.documentElement.scrollWidth > window.innerWidth + 1,
           scroll_w: document.documentElement.scrollWidth, inner_w: window.innerWidth,
           body_text: document.body.innerText,
           robots: (document.querySelector('meta[name=robots]') || {}).content || '',
           cookie_names: document.cookie.split(';').map(c => c.split('=')[0].trim()).filter(Boolean) };
}
"""


def probe(browser, label, url, viewport, mobile=False, block_wc=False, wait=9000):
    ua = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
          "Version/17.5 Mobile/15E148 Safari/604.1") if mobile else None
    ctx = browser.new_context(viewport=viewport, is_mobile=mobile, has_touch=mobile, user_agent=ua,
                              device_scale_factor=2 if mobile else 1, locale="en-US", timezone_id="America/Chicago")
    blocked, wc_requests, statuses = [], [], []

    def route(r):
        u = r.request.url
        if BLOCK_ADS.search(u):
            p = urlparse(u)
            blocked.append(f"{p.netloc}{p.path}"[:120])
            return r.abort()
        if BLOCK_WC.search(u):
            wc_requests.append(urlparse(u).path[:60])
            if block_wc:
                return r.abort()
        return r.continue_()

    ctx.route("**/*", route)
    page = ctx.new_page()
    page.on("response", lambda resp: statuses.append((resp.status, resp.url[:100])) if resp.url.rstrip("/") == url.rstrip("/") or resp.request.is_navigation_request() else None)
    nav = page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(wait)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:  # noqa: BLE001
        pass
    data = page.evaluate(EXTRACT)
    page.screenshot(path=str(OUT / f"{label}.png"), full_page=True)
    page.screenshot(path=str(OUT / f"{label}-viewport.png"), full_page=False)
    body = data.pop("body_text")
    (OUT / f"{label}-text.txt").write_text(body, encoding="utf-8")
    data["drafting_notes_present"] = {k: (v.lower() in body.lower()) for k, v in NOTES.items()}
    data["drafting_note_fragments"] = {k: (k_frag in body) for k, k_frag in
                                       (("reconfirm", "Reconfirm"), ("require client confirmation", "require client confirmation"))}
    data["nav_status"] = nav.status if nav else None
    data["navigations"] = statuses[:8]
    data["blocked_ad_or_conversion_requests"] = blocked
    data["whatconverts_requests"] = sorted(set(wc_requests))[:12]
    data["captcha_stub"] = "sgcaptcha" in page.content().lower()
    ctx.close()
    return data


prev = OUT / "browser-qa.json"
results = json.loads(prev.read_text(encoding="utf-8")) if prev.exists() else {"probes": {}}
results["run_at"] = time.strftime("%Y-%m-%d %H:%M:%S %z")
SKIP = {k for k, v in results["probes"].items() if "error" not in v}
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    plan = [("lp-desktop", LP, {"width": 1440, "height": 900}, False, False),
            ("lp-mobile", LP, {"width": 390, "height": 844}, True, False),
            ("thankyou-direct-desktop", TY, {"width": 1440, "height": 900}, False, True),
            ("main-permanent-lights-desktop", MAIN, {"width": 1440, "height": 900}, False, True)]
    for label, url, vp, mobile, block_wc in plan:
        if label in SKIP:
            print('skip (already ok):', label)
            continue
        try:
            results["probes"][label] = probe(browser, label, url, vp, mobile, block_wc)
        except Exception as exc:  # noqa: BLE001
            results["probes"][label] = {"error": str(exc)[:300]}
        d = results["probes"][label]
        print(f"\n=== {label}: nav={d.get('nav_status')} url={d.get('url')} title={d.get('title')!r} captcha={d.get('captcha_stub')} err={d.get('error')}")
        time.sleep(20)
    browser.close()
(OUT / "browser-qa.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
print("\nWROTE", OUT / "browser-qa.json")
