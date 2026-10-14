#!/usr/bin/env python3
"""Ambient | 2026-09-22 | SAFE form inspection. Nothing is submitted.

Maps every field on the two distinct form integrations before any test submission, and
identifies honeypots by their own signature rather than by inheriting a field map from a
previous client. Filling a honeypot makes a working form look broken.

No URL parameters are sent: the SiteGround full-page proxy cache is shared, and a synthetic
click id could be cached and replayed to real visitors. There is no established purge
method available here, so parameters stay out.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-22"
TARGETS = {
    # one per DISTINCT form integration
    "main-site gform_2": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "offer gform_1": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
}

PROBE = """() => {
  const out = [];
  document.querySelectorAll('form').forEach((f, fi) => {
    const fields = [...f.querySelectorAll('input,textarea,select')].map(e => {
      const st = getComputedStyle(e);
      const r = e.getBoundingClientRect();
      // A honeypot is present in the DOM but hidden from a human: zero box, or
      // display:none / visibility:hidden / opacity:0, or parked off-screen.
      const hidden = e.type === 'hidden' || st.display === 'none'
        || st.visibility === 'hidden' || parseFloat(st.opacity) === 0
        || (r.width === 0 && r.height === 0) || r.left < -500 || r.top < -500;
      let label = '';
      if (e.id) {
        const l = document.querySelector(`label[for="${CSS.escape(e.id)}"]`);
        if (l) label = (l.innerText || '').trim();
      }
      if (!label && e.closest('li,div')) {
        const l = e.closest('li,div').querySelector('label');
        if (l) label = (l.innerText || '').trim();
      }
      return { id: e.id || '', name: e.name || '', type: e.type || e.tagName,
               required: e.required || /gfield_required/.test(
                 (e.closest('li,div') || {}).innerHTML || ''),
               placeholder: e.placeholder || '', label: label.slice(0, 60),
               visuallyHidden: hidden, value: (e.value || '').slice(0, 40),
               autocomplete: e.getAttribute('autocomplete') || '',
               tabindex: e.getAttribute('tabindex') || '' };
    });
    out.push({ index: fi, id: f.id || '', action: f.getAttribute('action') || '',
               method: f.method, fieldCount: fields.length, fields });
  });
  return out;
}"""


def main():
    out = {"when": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "parameterised_requests": 0, "forms_submitted": 0, "tel_activated": 0,
           "targets": {}}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for label, url in TARGETS.items():
            ctx = b.new_context(locale="en-US", timezone_id="America/New_York",
                                viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            rec = {"url": url}
            try:
                r = pg.goto(url, wait_until="domcontentloaded", timeout=70000)
                rec["status"] = r.status if r else None
                pg.wait_for_timeout(2500)
                pg.mouse.wheel(0, 1600)
                pg.keyboard.press("PageDown")
                pg.wait_for_timeout(6000)
                rec["forms"] = pg.evaluate(PROBE)
                rec["cookies"] = {x["name"]: x["value"][:44] for x in ctx.cookies()}
            except Exception as ex:
                rec["error"] = str(ex)[:200]
            finally:
                ctx.close()
            out["targets"][label] = rec
            print(f"\n{'=' * 78}\n{label}  {url}\n  status={rec.get('status')}")
            for f in rec.get("forms", []):
                print(f"  --- form[{f['index']}] id={f['id']!r} action={f['action'][:50]!r} "
                      f"fields={f['fieldCount']}")
                for fl in f["fields"]:
                    if fl["type"] == "hidden" and not fl["id"]:
                        continue
                    flag = ""
                    if fl["visuallyHidden"] and fl["type"] != "hidden":
                        flag = "   <<< HIDDEN FROM HUMANS - LIKELY HONEYPOT, DO NOT FILL"
                    print(f"       {fl['type']:9s} id={fl['id'][:34]:34s} "
                          f"req={str(fl['required'])[:5]:5s} label={fl['label'][:26]:26s}"
                          f"{flag}")
            wc = {k: v for k, v in (rec.get("cookies") or {}).items()
                  if k.startswith("wc_")}
            print(f"  WhatConverts cookies: {wc}")
        b.close()

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"form-inspect-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("PARAMETERISED REQUESTS: 0 | FORMS SUBMITTED: 0 | TEL ACTIVATED: 0")


if __name__ == "__main__":
    main()
