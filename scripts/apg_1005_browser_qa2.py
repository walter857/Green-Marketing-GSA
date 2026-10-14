#!/usr/bin/env python3
"""2026-10-05 READ-ONLY browser QA pass 2 for Apogee (no submissions, no clicks).

1. Full DOM text (textContent, including collapsed FAQ accordions) of the paid page and the
   main-site permanent-lights page, to re-verify ad claims at their source.
2. Cache-leak evidence on the paid page, loaded with NO query string: compares each
   pre-filled hidden attribution field with known campaign constants and reports booleans
   only. Values are never stored or printed. Also reports whether the cached form action
   carries a click-ID parameter (boolean only) and the hidden fields' admin labels.
Conversion/ads requests are aborted exactly as in pass 1.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients" / "apogee-lawns" / "audits" / "2026-10-05-conversion-plan" / "browser-qa"
LP = "https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/"
MAIN = "https://apogeelawns.com/permanent-holiday-lights-lincoln-ne/"
BLOCK = re.compile(r"googleadservices\.com|google\.com/pagead|google\.com/ccm|doubleclick\.net|google\.com/rmkt"
                   r"|googlesyndication\.com")
CONSTANTS = {"google": "google", "cpc": "cpc", "campaign": "apogee_permanent_lights_2026",
             "term_installation": "permanent christmas light installation",
             "term_head": "permanent christmas lights", "ad_007": "825023783007", "ad_010": "825023783010",
             "ad_013": "825023783013", "ad_016": "825023783016"}
LEAK = r"""
(constants) => {
  const out = [];
  document.querySelectorAll('form[id^="gform_"]').forEach((f, idx) => {
    const a = f.getAttribute('action') || '';
    const q = a.includes('?') ? a.split('?')[1] : '';
    const row = { form_index: idx, action_has_query: q.length > 0, action_query_len: q.length,
                  action_has_gclid: /(^|&)gclid=/.test(q), action_has_gbraid: /(^|&)gbraid=/.test(q),
                  action_has_wbraid: /(^|&)wbraid=/.test(q), action_has_utm: /(^|&)utm_/.test(q), fields: [] };
    f.querySelectorAll('input[type=hidden][name^="input_"]').forEach(i => {
      const v = i.value || '';
      const m = Object.entries(constants).filter(([k, c]) => v === c).map(([k]) => k);
      const wrap = document.getElementById('field_' + i.id.replace('input_', ''));
      const lab = wrap ? (wrap.querySelector('label,.gfield_label') || {}).textContent || '' : '';
      row.fields.push({ name: i.name, filled: v.length > 0, len: v.length, equals: m,
                        looks_like_url: /^https?:\/\//.test(v), url_has_click_id: /[?&](gclid|gbraid|wbraid)=/.test(v),
                        admin_label: lab.replace(/\s+/g, ' ').trim().slice(0, 40),
                        css: (wrap ? wrap.className : '').slice(0, 80) });
    });
    out.push(row);
  });
  return { page_url_has_query: location.search.length > 0, forms: out };
}
"""

res = {"run_at": time.strftime("%Y-%m-%d %H:%M:%S %z")}
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    for label, url in (("lp", LP), ("main", MAIN)):
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/Chicago")
        ctx.route("**/*", lambda r: r.abort() if BLOCK.search(r.request.url) else r.continue_())
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(9000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:  # noqa: BLE001
            pass
        full = page.evaluate("() => document.body.textContent.replace(/\\s+/g, ' ').trim()")
        (OUT / f"{label}-fulltext.txt").write_text(full, encoding="utf-8")
        res[label] = {"final_url": page.url, "fulltext_chars": len(full)}
        if label == "lp":
            res["lp"]["cache_leak"] = page.evaluate(LEAK, CONSTANTS)
        ctx.close()
        time.sleep(20)
    browser.close()
(OUT / "browser-qa2.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1)[:6000])
