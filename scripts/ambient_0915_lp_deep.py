#!/usr/bin/env python3
"""Ambient | 2026-09-15 | deep probe of the commercial landing page.

Corrects the earlier hidden-field read: getAttribute('value') returns the HTML
attribute, NOT the live DOM property, so a JS-populated attribution field looks
empty. This reads element.value. Still GET-only; nothing is submitted.
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
STAMP = "2026-09-15"
URL = "https://offer.ambientcoolingandheating.com/commercial-hvac-installation/"
PARAMS = ("?gclid=QA0915DEEP&utm_source=google&utm_medium=cpc"
          "&utm_campaign=Search%20%7C%20NonBrand%20%7C%20HVAC%20Installation"
          "&utm_term=commercial+hvac+installation&utm_content=qa-deep-content")
UA_D = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_M = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")

JS_FIELDS = """
() => {
  const out = [];
  document.querySelectorAll('form').forEach((f, fi) => {
    const fields = [];
    f.querySelectorAll('input, textarea, select').forEach(el => {
      fields.push({
        name: el.name || '', id: el.id || '',
        type: (el.type || el.tagName || '').toLowerCase(),
        domValue: (el.value || '').slice(0, 200),
        attrValue: (el.getAttribute('value') || '').slice(0, 200),
        required: el.required === true,
        visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length),
        ariaHidden: el.getAttribute('aria-hidden'),
        placeholder: el.getAttribute('placeholder') || ''
      });
    });
    const st = getComputedStyle(f);
    out.push({
      index: fi, id: f.id || '', action: f.action || '',
      display: st.display, visibility: st.visibility,
      offsetParent: f.offsetParent !== null,
      rectH: Math.round(f.getBoundingClientRect().height),
      fields: fields
    });
  });
  return out;
}
"""

JS_DATALAYER = """
() => {
  try {
    const dl = (window.dataLayer || []).map(x => {
      try { return JSON.stringify(x).slice(0, 320); } catch (e) { return String(x); }
    });
    return { present: !!window.dataLayer, length: (window.dataLayer||[]).length,
             entries: dl.slice(0, 40) };
  } catch (e) { return { error: String(e) }; }
}
"""

JS_GALLERY = """
() => {
  const heads = Array.from(document.querySelectorAll('h1,h2,h3'));
  const g = heads.find(h => /gallery/i.test(h.innerText));
  const out = { galleryHeading: g ? g.innerText : null, images: [] };
  const scope = g ? (g.closest('section,div.et_pb_section,div') || document) : document;
  scope.querySelectorAll('img').forEach(i => {
    out.images.push({
      src: (i.currentSrc || i.src || '').slice(-120),
      alt: i.alt || '', title: i.title || '',
      w: i.naturalWidth, h: i.naturalHeight,
      figcaption: (i.closest('figure') &&
        i.closest('figure').querySelector('figcaption'))
        ? i.closest('figure').querySelector('figcaption').innerText.slice(0,160) : null
    });
  });
  return out;
}
"""

JS_STICKY = """
() => Array.from(document.querySelectorAll('*')).filter(e => {
  const s = getComputedStyle(e);
  return (s.position === 'fixed' || s.position === 'sticky') &&
         e.getBoundingClientRect().height > 0;
}).slice(0, 15).map(e => ({
  tag: e.tagName,
  cls: (e.className || '').toString().slice(0, 90),
  txt: (e.innerText || '').replace(/\\s+/g, ' ').slice(0, 90),
  tel: Array.from(e.querySelectorAll("a[href^='tel:']")).map(a => a.getAttribute('href')),
  bottom: Math.round(e.getBoundingClientRect().bottom),
  pos: getComputedStyle(e).position
}))
"""

JS_CTA = """
() => Array.from(document.querySelectorAll('a,button,input[type=submit]')).map(e => ({
  tag: e.tagName,
  text: (e.innerText || e.value || '').replace(/\\s+/g,' ').trim().slice(0, 90),
  href: e.getAttribute('href') || '',
  visible: !!(e.offsetWidth || e.offsetHeight)
})).filter(x => x.text && x.visible).slice(0, 45)
"""


def run(pw, profile):
    vp = {"width": 1440, "height": 900} if profile == "desktop" else {"width": 390, "height": 844}
    ua = UA_D if profile == "desktop" else UA_M
    br = pw.chromium.launch()
    ctx = br.new_context(viewport=vp, user_agent=ua, locale="en-US",
                         is_mobile=(profile == "mobile"), has_touch=(profile == "mobile"))
    page = ctx.new_page()
    console, failed = [], []
    page.on("console", lambda m: console.append({"t": m.type, "x": m.text[:200]}))
    page.on("requestfailed", lambda r: failed.append(
        {"url": r.url[:160], "fail": (r.failure or "")[:120]}))
    rec = {"profile": profile}
    resp = page.goto(URL + PARAMS, wait_until="networkidle", timeout=90000)
    rec["http_status"] = resp.status
    page.wait_for_timeout(7000)          # give DNI + any JS field-fill time to run
    rec["forms"] = page.evaluate(JS_FIELDS)
    rec["dataLayer"] = page.evaluate(JS_DATALAYER)
    rec["gallery"] = page.evaluate(JS_GALLERY)
    rec["sticky"] = page.evaluate(JS_STICKY)
    rec["ctas"] = page.evaluate(JS_CTA)
    rec["tel_links"] = [{"href": a.get_attribute("href"),
                         "text": (a.inner_text() or "").strip()[:60],
                         "visible": a.is_visible()}
                        for a in page.query_selector_all("a[href^='tel:']")]
    # scroll to bottom, re-read stickies and tel links (mobile sticky bar often lazy)
    page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2500)
    rec["sticky_after_scroll"] = page.evaluate(JS_STICKY)
    rec["tel_links_after_scroll"] = [{"href": a.get_attribute("href"),
                                      "text": (a.inner_text() or "").strip()[:60],
                                      "visible": a.is_visible()}
                                     for a in page.query_selector_all("a[href^='tel:']")]
    rec["console_errors"] = [c for c in console if c["t"] == "error"][:25]
    rec["console_error_count"] = sum(1 for c in console if c["t"] == "error")
    rec["failed_requests"] = failed[:25]
    body = page.inner_text("body")
    rec["faq_text"] = body[body.find("FAQ"):body.find("FAQ") + 1800] if "FAQ" in body else None
    rec["body_text"] = body
    ctx.close()
    br.close()
    return rec


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "url": URL + PARAMS,
           "runs": []}
    with sync_playwright() as pw:
        for prof in ("desktop", "mobile"):
            out["runs"].append(run(pw, prof))

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"lp-commercial-deep-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {p}\n")

    for r in out["runs"]:
        print(f"########## {r['profile'].upper()}  http={r['http_status']} ##########")
        print(f"console_errors={r['console_error_count']} failed_requests={len(r['failed_requests'])}")
        for f in r["forms"]:
            print(f"\n  FORM[{f['index']}] id={f['id']!r} display={f['display']} "
                  f"vis={f['visibility']} offsetParent={f['offsetParent']} h={f['rectH']}")
            for fl in f["fields"]:
                if fl["type"] == "hidden" or fl["domValue"]:
                    print(f"    {fl['type']:9s} {fl['name']:28s} domValue={fl['domValue']!r:60s} "
                          f"attrValue={fl['attrValue']!r}")
        print(f"\n  dataLayer: present={r['dataLayer'].get('present')} "
              f"len={r['dataLayer'].get('length')}")
        for e in (r["dataLayer"].get("entries") or [])[:25]:
            print("    ", e)
        print(f"\n  gallery heading: {r['gallery']['galleryHeading']!r}")
        for i in r["gallery"]["images"][:14]:
            print(f"    {i['w']}x{i['h']} alt={i['alt']!r} cap={i['figcaption']!r} src=...{i['src']}")
        print("\n  sticky (initial):")
        for s in r["sticky"]:
            print("    ", s)
        print("  sticky (after scroll):")
        for s in r["sticky_after_scroll"]:
            print("    ", s)
        print("\n  tel links after scroll:")
        for t in r["tel_links_after_scroll"]:
            print("    ", t)
        print("\n  CTAs:")
        for ccc in r["ctas"]:
            print(f"    [{ccc['tag']:6s}] {ccc['text'][:60]!r:62s} href={ccc['href'][:60]!r}")
        print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    sys.exit(main())
