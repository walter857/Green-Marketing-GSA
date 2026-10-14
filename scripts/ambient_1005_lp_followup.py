#!/usr/bin/env python3
"""Ambient | 2026-10-05 | Follow-up on /hvac-repair/ only (3 server requests, spaced). GET only, nothing submitted.

a. 390px mobile load (plain URL): rendered form copies and duplicate ids at phone width (D5).
b. raw server HTML (in-page fetch, unique cache-busting key + marker): how many form#gform_1 the server sends, where the
   marker lands (context around it, marker only), and which script removes the extra copies.
c. MISS load in the browser with a unique key + marker (analytics/Ads beacons aborted): do the hidden fields fill when the
   page is NOT served from cache? Compared with the HIT simulation in ambient_1005_lp_blockers.py this isolates D7.
Appends results to snapshots/lp-blockers-2026-10-05.json under "followup".
"""
from __future__ import annotations
import json, re, time, uuid
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
URL = "https://offer.ambientcoolingandheating.com/hvac-repair/"
UA_D = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
UA_M = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
BEACONS = re.compile(r"google-analytics\.com|analytics\.google\.com|googleadservices\.com|doubleclick\.net|googlesyndication|bat\.bing|clarity\.ms")
DOM = r"""() => { const ids = {}; document.querySelectorAll('[id]').forEach(e => ids[e.id] = (ids[e.id]||0)+1);
  const vis = [...document.querySelectorAll('form#gform_1')].filter(f => f.offsetParent !== null).length;
  return {forms: document.querySelectorAll('form#gform_1').length, visible_forms: vis,
          dup_form_ids: Object.entries(ids).filter(([k,v]) => v > 1 && /gform|field_1_|input_1_/.test(k)).length}; }"""
FIELDS = r"""() => { const o = {}; document.querySelectorAll('form#gform_1 input[type=hidden]').forEach(el => {
  if (/^input_\d+$/.test(el.name)) o[el.name] = (el.value||''); }); return o; }"""
FETCH = r"""async (u) => { const r = await fetch(u, {cache:'no-store', credentials:'include'}); const h = {};
  r.headers.forEach((v,k) => { if (/x-proxy|cache/i.test(k)) h[k] = v; }); return {h, body: await r.text()}; }"""

out = {}
with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(user_agent=UA_M, viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="en-US")
    p = ctx.new_page()
    p.goto(URL, wait_until="networkidle", timeout=90000); p.wait_for_timeout(9000)
    out["a_mobile_390"] = p.evaluate(DOM)
    print("a. mobile 390px:", out["a_mobile_390"])
    time.sleep(8)
    mark = "GMQA" + uuid.uuid4().hex[:8].upper()
    f = p.evaluate(FETCH, f"{URL}?gmqa={uuid.uuid4().hex}&utm_content={mark}")
    body = f["body"]
    ctxs = [re.sub(r"\s+", " ", body[max(0, m.start() - 140): m.end() + 40]) for m in re.finditer(mark, body)]
    out["b_raw"] = {"headers": f["h"], "gform_1_in_server_html": len(re.findall(r"id=['\"]gform_1['\"]", body)),
                    "marker_hits": len(ctxs), "marker_contexts": ctxs[:4],
                    "dedupe_scripts": sorted({m.group(0)[:90] for m in re.finditer(r"[^;{}\n]{0,60}(remove\(\)|removeChild)[^;{}\n]{0,30}", body)})[:6]}
    print("b. raw:", json.dumps(out["b_raw"], indent=1)[:2500])
    ctx.close()
    time.sleep(8)
    m2 = "GMQA" + uuid.uuid4().hex[:8].upper()
    ctx = br.new_context(user_agent=UA_D, viewport={"width": 1366, "height": 900}, locale="en-US")
    p = ctx.new_page()
    p.route(BEACONS, lambda r: r.abort())
    p.goto(f"{URL}?gmqa={uuid.uuid4().hex}&gclid={m2}&utm_content={m2}", wait_until="networkidle", timeout=90000)
    p.wait_for_timeout(9000); p.mouse.move(300, 300); p.wait_for_timeout(3000)
    vals = p.evaluate(FIELDS)
    out["c_miss_load"] = {"fields_with_marker": sorted(k for k, v in vals.items() if m2 in v),
                          "fields_non_empty_other": sorted(k for k, v in vals.items() if v and m2 not in v)}
    print("c. MISS load:", out["c_miss_load"])
    ctx.close(); br.close()
P = SNAP / "lp-blockers-2026-10-05.json"
d = json.loads(P.read_text(encoding="utf-8")); d["followup"] = out
P.write_text(json.dumps(d, indent=1, default=str), encoding="utf-8")
