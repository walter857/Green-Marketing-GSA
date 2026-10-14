#!/usr/bin/env python3
"""Ambient | 2026-09-30 | READ-ONLY landing-page QA for the Boiler / Heat Pump maintenance evaluation.

GET only. No form is submitted, no phone link is clicked, no gclid/gbraid/wbraid is ever sent.
Per page: desktop + mobile clean loads (no query string, so the shared cache entry is never primed),
rendered headings/CTAs/phones/forms/duplicate ids/D6 markup, raw server HTML phone counts (D1), and a
D7 probe that uses a unique NON-utm cache-busting parameter plus a utm_content marker with every
third-party host blocked, followed by a clean request that must not carry the marker.
Writes snapshots/maint-lp-qa-2026-09-30.json.
"""
from __future__ import annotations
import sys, json, re, time, uuid, collections
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
O = "https://offer.ambientcoolingandheating.com"
PAGES = {"Boiler Repair": "/gas-boiler-repair/", "Boiler Replacement": "/boiler-replacement/",
         "Boiler Maintenance": "/boiler-maintenance/", "Heat Pump Maintenance": "/heat-pump-maintenance/"}
SERVICE_WORDS = {"repair": r"\brepair", "replacement": r"\breplac", "installation": r"\binstall",
                 "maintenance": r"\bmaint|tune[- ]?up|check[- ]?up|inspection"}
EQUIP = {"boiler": r"\bboiler", "heat pump": r"heat pump", "furnace": r"\bfurnace", "thermostat": r"thermostat",
         "ac": r"\bair condition|\bac\b", "ductless": r"ductless|mini[- ]split", "geothermal": r"geotherm"}
BARRED = re.compile(r"24/7|24-7|24 hours|same[- ]day|emergenc|licens|insured|guarantee|warrant|financ|\$\s?\d|% off|"
                    r"discount|rebate|tax credit|years? (of )?experience|\d+\+? years|\d(\.\d)? ?stars?|rated|review|"
                    r"certified|fast response|within \d+ (min|hour)|free estimate|no[- ]obligation|award", re.I)
THIRD_PARTY = re.compile(r"googletagmanager|google-analytics|googleadservices|doubleclick|gstatic|google\.com|facebook|"
                         r"bing|nextdoor|ksrndkehqnwntyxlhgto|iconnode|clickcease|whatconverts", re.I)
PHONES = {"705-6354": r"705[\s.\-)]*6354", "914-1456": r"914[\s.\-)]*1456", "761-0932": r"761[\s.\-)]*0932",
          "415-9517": r"415[\s.\-)]*9517"}

RENDER_JS = r"""
() => {
  const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const txt = el => (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
  const q = s => Array.from(document.querySelectorAll(s));
  const ids = {}; q('[id]').forEach(e => { ids[e.id] = (ids[e.id] || 0) + 1; });
  const dups = Object.entries(ids).filter(([k, v]) => v > 1);
  const f7 = q('#field_1_7'); const i7 = q('#input_1_7');
  return {
    title: document.title, url: location.href,
    h1: q('h1').map(txt), h2: q('h2').map(txt), h3: q('h3').map(txt),
    ctas: q('a.et_pb_button, .et_pb_button, button, input[type=submit], .gform_button').map(e => (txt(e) || e.value || '').trim()).filter(Boolean),
    tel: q('a[href^="tel:"]').map(e => ({href: e.getAttribute('href'), text: txt(e), visible: vis(e)})),
    forms: q('form').map(f => ({id: f.id, visible: vis(f)})),
    dup_id_count: dups.length, dup_examples: dups.slice(0, 6),
    f7: f7.map(e => ({cls: e.className, label: txt(e.querySelector('label') || e)})),
    i7: i7.map(e => ({required: e.required, aria: e.getAttribute('aria-required'), tag: e.tagName})),
    hidden_values: q('input[id^="input_1_"]').filter(e => { const n = +e.id.split('_')[2]; return n >= 9 && n <= 26; })
                     .map(e => ({id: e.id, has_value: !!e.value})),
    text: document.body ? document.body.innerText : '',
    wc_cookies: document.cookie.split(';').map(s => s.trim().split('=')[0]).filter(n => n.startsWith('wc_')),
    gtm: !!(window.google_tag_manager && window.google_tag_manager['GTM-PQTPQ436']),
    wc_script: performance.getEntriesByType('resource').map(r => r.name).filter(n => /ksrndkehqnwntyxlhgto|whatconverts/.test(n)).slice(0, 3),
  };
}
"""


def count(pat, s):
    return len(re.findall(pat, s or "", re.I))


def analyse(service, r):
    heads = r["h1"] + r["h2"] + r["h3"]
    svc_key = {"Boiler Repair": "repair", "Boiler Replacement": "replacement", "Boiler Maintenance": "maintenance",
               "Heat Pump Maintenance": "maintenance"}[service]
    eq_key = "heat pump" if service.startswith("Heat Pump") else "boiler"
    wrong = []
    for h in heads + r["ctas"]:
        for k, p in SERVICE_WORDS.items():
            if k != svc_key and re.search(p, h, re.I) and not re.search(SERVICE_WORDS[svc_key], h, re.I):
                wrong.append(f"{k}: {h[:90]}")
        for k, p in EQUIP.items():
            if k != eq_key and re.search(p, h, re.I) and not re.search(EQUIP[eq_key], h, re.I):
                wrong.append(f"{k}: {h[:90]}")
    body = r["text"]
    return dict(service_word_counts={k: count(p, body) for k, p in SERVICE_WORDS.items()},
                equipment_counts={k: count(p, body) for k, p in EQUIP.items()},
                off_service_headings_or_ctas=sorted(set(wrong)),
                barred_hits=sorted({m.group(0).lower() for m in BARRED.finditer(body)}),
                rendered_phone_counts={k: count(p, body) for k, p in PHONES.items()})


out = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    for service, path in PAGES.items():
        url = O + path
        res = {"url": url}
        for label, vp in (("desktop", {"width": 1366, "height": 900}), ("mobile", {"width": 390, "height": 844})):
            ctx = b.new_context(locale="en-US", viewport=vp, is_mobile=(label == "mobile"), has_touch=(label == "mobile"))
            pg = ctx.new_page()
            resp = pg.goto(url, wait_until="domcontentloaded", timeout=90000)
            raw = resp.text() if resp else ""
            hdr = dict(resp.headers) if resp else {}
            try:
                pg.mouse.move(200, 300); pg.mouse.wheel(0, 900); time.sleep(1.5); pg.mouse.wheel(0, -900)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(8)
            r = pg.evaluate(RENDER_JS)
            r["status"] = resp.status if resp else None
            r["final_url"] = pg.url
            r["x_proxy_cache"] = hdr.get("x-proxy-cache")
            r["raw_len"] = len(raw)
            r["raw_phone_counts"] = {k: count(p, raw) for k, p in PHONES.items()}
            r["raw_tel_hrefs"] = sorted(set(re.findall(r'href=["\']tel:([^"\']+)', raw)))
            r["raw_gform1_count"] = count(r"<form[^>]+id=['\"]gform_1['\"]", raw)
            r["raw_form_ids"] = sorted(set(re.findall(r"<form[^>]+id=['\"](gform_\d+)['\"]", raw)))
            r["analysis"] = analyse(service, r)
            res[label] = r
            ctx.close()
        # D7 probe: unique non-utm cache-buster + utm marker, all third-party hosts blocked
        marker = "GMQA" + uuid.uuid4().hex[:10].upper()
        ctx = b.new_context(locale="en-US")
        ctx.route("**/*", lambda route: route.abort() if THIRD_PARTY.search(route.request.url) else route.continue_())
        pg = ctx.new_page()
        pr = pg.goto(f"{url}?gmqa{uuid.uuid4().hex[:8]}=1&utm_content={marker}", wait_until="domcontentloaded", timeout=90000)
        praw = pr.text() if pr else ""
        clean = pg.goto(url, wait_until="domcontentloaded", timeout=90000)
        craw = clean.text() if clean else ""
        res["d7_probe"] = dict(probe_status=pr.status if pr else None, probe_cache=pr.headers.get("x-proxy-cache") if pr else None,
                               marker_in_probe_server_html=marker in praw,
                               clean_status=clean.status if clean else None,
                               clean_cache=clean.headers.get("x-proxy-cache") if clean else None,
                               marker_in_clean_server_html=marker in craw,
                               clean_hidden_fields_with_value=len(re.findall(
                                   r'<input[^>]+id=[\'"]input_1_(?:9|1\d|2[0-6])[\'"][^>]*value=[\'"][^\'"]+[\'"]', craw)))
        ctx.close()
        out[service] = res
    b.close()

(SNAP / "maint-lp-qa-2026-09-30.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for service, res in out.items():
    print(f"\n==================== {service}  {res['url']}")
    for label in ("desktop", "mobile"):
        r = res[label]; a = r["analysis"]
        print(f" [{label}] HTTP {r['status']} final={r['final_url'].replace(O, '')} cache={r['x_proxy_cache']} gtm={r['gtm']} "
              f"wc_cookies={r['wc_cookies']} wc_script={[s.split('/')[-1][:40] for s in r['wc_script']]}")
        if label == "desktop":
            print(f"   title: {r['title']}")
            print(f"   H1: {r['h1']}")
            print(f"   H2: {r['h2']}")
            print(f"   H3: {r['h3'][:14]}")
            print(f"   CTAs: {sorted(set(r['ctas']))}")
            print(f"   service words: {a['service_word_counts']}  equipment: {a['equipment_counts']}")
            print(f"   off-service headings/CTAs: {a['off_service_headings_or_ctas']}")
            print(f"   barred-claim hits (visible text): {a['barred_hits']}")
            print(f"   RAW server HTML: phones {r['raw_phone_counts']} tel hrefs {r['raw_tel_hrefs']} "
                  f"gform_1 x{r['raw_gform1_count']} form ids {r['raw_form_ids']}")
        print(f"   rendered phones {a['rendered_phone_counts']}")
        print(f"   tel links: {[(t['href'], t['text'][:24], t['visible']) for t in r['tel']]}")
        print(f"   forms: {r['forms']} dup ids: {r['dup_id_count']}")
        if label == "desktop":
            print(f"   D6 field_1_7: {r['f7'][:1]} input: {r['i7'][:1]}")
            print(f"   hidden attribution fields with a value (clean load): {sum(1 for h in r['hidden_values'] if h['has_value'])}/{len(r['hidden_values'])}")
    print(f" D7 probe: {res['d7_probe']}")
