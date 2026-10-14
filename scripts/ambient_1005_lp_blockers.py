#!/usr/bin/env python3
"""Ambient | 2026-10-05 | READ-ONLY status check of developer blockers D1, D5, D6, D7 on the repair landing pages.

GET only, nothing submitted, 2 pages, requests spaced out (SiteGround firewalled this machine on 10-02 after bursts).
Per page:
  1. page.goto(plain URL)            -> rendered DOM: D5 form copies + duplicate ids, D6 message-field config, rendered numbers.
  2. in-page fetch(plain URL)        -> proxy-cache headers + RAW server HTML: D1 (761-0932 in source), are the shared copy's
                                        attribution fields pre-filled (length only, never the value).
  3. in-page fetch(URL?gmqa=<uuid>&utm_content=<marker>) -> unique cache key (MISS, never primes the shared entry): does the
                                        SERVER still write query values into the hidden fields?
  4. D7 simulation: a fresh context requests URL?gclid=<m>&utm_content=<m>; page.route() fulfils that document locally with the
     shared copy from step 2, so the marker never reaches the server and cannot seed the cache. Analytics/Ads/WhatConverts
     beacons are aborted in this load. Reads the live el.value of every hidden field: did the visitor's own values land?
Writes snapshots/lp-blockers-2026-10-05.json. Prints aggregates only.
"""
from __future__ import annotations
import datetime, json, re, time, uuid
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
TZ = ZoneInfo("America/New_York")
BASE = "https://offer.ambientcoolingandheating.com"
PAGES = {"Heating Repair (204129717007)": f"{BASE}/hvac-repair/", "Furnace / Gas / Electric Furnace Repair": f"{BASE}/furnace-repair/"}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
BEACONS = re.compile(r"google-analytics\.com|analytics\.google\.com|googleadservices\.com|doubleclick\.net|googlesyndication|whatconverts|ksrndkehqnwntyxlhgto|bat\.bing|clarity\.ms")
NUMS = {"761-0932": r"761[\s.\-]?0932", "914-1456": r"914[\s.\-]?1456", "705-6354": r"705[\s.\-]?6354", "415-9517": r"415[\s.\-]?9517"}

DOM_JS = r"""
() => {
  const forms = document.querySelectorAll('form#gform_1').length;
  const ids = {}; document.querySelectorAll('[id]').forEach(e => ids[e.id] = (ids[e.id]||0)+1);
  const dup = Object.entries(ids).filter(([k,v]) => v > 1);
  const msg = [...document.querySelectorAll('[id^="field_1_7"]')].map(f => ({
      label: (f.querySelector('label')||{}).innerText || '', cls_required: f.classList.contains('gfield_contains_required'),
      aria_required: (f.querySelector('textarea,input')||{getAttribute:()=>null}).getAttribute('aria-required'),
      required_attr: !!(f.querySelector('textarea[required],input[required]'))}));
  const text = document.body.innerText;
  const tels = [...document.querySelectorAll('a[href^="tel:"]')].map(a => a.getAttribute('href').replace(/\D/g,'').slice(-10));
  return {forms, dup_ids: dup.length, dup_examples: dup.slice(0,4).map(x=>x[0]), msg, text, tels,
          phone_fix: window.__gmPhoneFix || null, wc_cookie: /wc_swap|wc_visitor/.test(document.cookie)};
}
"""
FIELDS_JS = r"""
() => { const out = {}; document.querySelectorAll('form#gform_1 input[type=hidden]').forEach((el,i) => {
          if (/^input_\d+$/.test(el.name)) { (out[el.name] = out[el.name] || []).push(el.value || ''); } }); return out; }
"""
FETCH_JS = r"""
async (u) => { const r = await fetch(u, {cache: 'no-store', credentials: 'include'});
  const h = {}; r.headers.forEach((v,k) => { if (/cache|x-proxy|age|x-sg/i.test(k)) h[k] = v; });
  return {status: r.status, headers: h, body: await r.text()}; }
"""


def count_nums(s):
    return {k: len(re.findall(p, s)) for k, p in NUMS.items()}


def server_fields(html):
    """name -> list of value lengths for input_N hidden fields in raw HTML (values never returned)."""
    out = {}
    for m in re.finditer(r"<input[^>]+>", html):
        tag = m.group(0)
        if "type='hidden'" not in tag and 'type="hidden"' not in tag:
            continue
        n = re.search(r"name=['\"](input_\d+)['\"]", tag)
        v = re.search(r"value=['\"]([^'\"]*)['\"]", tag)
        if n:
            out.setdefault(n.group(1), []).append(len(v.group(1)) if v else 0)
    return out


def main():
    res = {"generated_local": datetime.datetime.now(TZ).isoformat(), "pages": {}}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for name, url in PAGES.items():
            r = {"url": url}
            ctx = br.new_context(user_agent=UA, viewport={"width": 1366, "height": 900}, locale="en-US")
            page = ctx.new_page()
            resp = page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(8000)
            page.mouse.move(400, 400); page.mouse.wheel(0, 600); page.wait_for_timeout(4000)
            d = page.evaluate(DOM_JS)
            r["goto_status"] = resp.status if resp else None
            r["D5"] = {"gform_1_copies": d["forms"], "duplicate_ids": d["dup_ids"], "examples": d["dup_examples"]}
            r["D6"] = d["msg"]
            r["rendered_numbers"] = count_nums(d["text"])
            r["tel_links"] = sorted(set(d["tels"]))
            r["phone_fix_state"], r["wc_cookie"] = d["phone_fix"], d["wc_cookie"]
            time.sleep(6)
            f1 = page.evaluate(FETCH_JS, url)
            r["plain_fetch"] = {"status": f1["status"], "headers": f1["headers"], "bytes": len(f1["body"]),
                                "D1_numbers_in_server_html": count_nums(f1["body"]), "hidden_field_value_lengths": server_fields(f1["body"])}
            shared_html = f1["body"]
            time.sleep(6)
            mark = "GMQA" + uuid.uuid4().hex[:8].upper()
            f2 = page.evaluate(FETCH_JS, f"{url}?gmqa={uuid.uuid4().hex}&utm_content={mark}")
            r["busting_fetch"] = {"status": f2["status"], "headers": f2["headers"], "bytes": len(f2["body"]),
                                  "server_writes_query_into_fields": mark in f2["body"], "hidden_field_value_lengths": server_fields(f2["body"])}
            ctx.close()
            # D7 simulation: cached shared copy served to a visitor carrying their own values (never sent to the server)
            m2 = "GMQA" + uuid.uuid4().hex[:8].upper()
            sim_url = f"{url}?gclid={m2}&utm_content={m2}"
            ctx = br.new_context(user_agent=UA, viewport={"width": 1366, "height": 900}, locale="en-US")
            page = ctx.new_page()
            page.route(re.compile(re.escape(url) + r"\?gclid=.*"), lambda route: route.fulfill(status=200, body=shared_html, content_type="text/html; charset=UTF-8"))
            page.route(BEACONS, lambda route: route.abort())
            page.goto(sim_url, wait_until="load", timeout=90000)
            page.wait_for_timeout(8000)
            page.mouse.move(300, 300); page.wait_for_timeout(3000)
            vals = page.evaluate(FIELDS_JS)
            r["D7_simulation"] = {"shared_copy_bytes": len(shared_html),
                                  "visitor_marker_in_any_field": any(m2 in v for vs in vals.values() for v in vs),
                                  "fields_with_marker": sorted(k for k, vs in vals.items() if any(m2 in v for v in vs)),
                                  "fields_non_empty_other": sorted(k for k, vs in vals.items() if any(v and m2 not in v for v in vs))}
            ctx.close()
            res["pages"][name] = r
            print(f"\n== {name} {url}  goto={r['goto_status']}")
            print("  D5:", r["D5"])
            print("  D6:", [(x["label"][:40], x["cls_required"], x["aria_required"], x["required_attr"]) for x in r["D6"]])
            print("  rendered numbers:", r["rendered_numbers"], "tel:", r["tel_links"], "phoneFix:", r["phone_fix_state"], "wc cookie:", r["wc_cookie"])
            print("  plain fetch:", r["plain_fetch"]["status"], r["plain_fetch"]["headers"], r["plain_fetch"]["bytes"], "D1:", r["plain_fetch"]["D1_numbers_in_server_html"],
                  "field lengths:", r["plain_fetch"]["hidden_field_value_lengths"])
            print("  busting fetch:", r["busting_fetch"]["status"], r["busting_fetch"]["headers"], "server writes query:", r["busting_fetch"]["server_writes_query_into_fields"],
                  "field lengths:", r["busting_fetch"]["hidden_field_value_lengths"])
            print("  D7 sim:", r["D7_simulation"])
            time.sleep(10)
        br.close()
    (SNAP / "lp-blockers-2026-10-05.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print("\nwrote snapshots/lp-blockers-2026-10-05.json")


if __name__ == "__main__":
    main()
