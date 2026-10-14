#!/usr/bin/env python3
"""Ambient | 2026-09-16 | independent verification of the attribution / cache fix.

READ + QA ONLY. GET navigations only. No form is submitted, no telephone link is
activated, no cache is purged, nothing on the website, GTM, WhatConverts, Gravity Forms
or Google Ads is modified. No real customer information is used anywhere.

Hidden-field mapping is DISCOVERED at runtime, never assumed - the developer may have
renamed or remapped the fields.
"""
from __future__ import annotations
import datetime, json, re, sys, time, urllib.request, urllib.error
from pathlib import Path
from collections import Counter, defaultdict
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-16"
BASE = "https://offer.ambientcoolingandheating.com"
PAGES = {
    "ac-repair": f"{BASE}/ac-repair/",
    "hvac-repair": f"{BASE}/hvac-repair/",
    "hvac-installation": f"{BASE}/hvac-installation/",
    "hvac-replacement": f"{BASE}/hvac-replacement/",
    "gas-boiler-repair": f"{BASE}/gas-boiler-repair/",
    "commercial-hvac-installation": f"{BASE}/commercial-hvac-installation/",
}
UA_D = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_M = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
VP_D = {"width": 1440, "height": 900}
VP_M = {"width": 390, "height": 844}
STALE = "QA0915COMMTEST"          # the marker the previous session left in the cache
PAID, MIXED, DEST = "4107056354", "4109141456", "4107610932"
GTM_ID, AW_ID, GA4_ID = "GTM-PQTPQ436", "AW-11155434808", "G-9X9ZHNCRWF"
RUN_TS = datetime.datetime.now(TZ).strftime("%H%M%S")

out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "account": {"name": "Ambient Cooling - Live", "customer_id": "2401959466"},
       "mode": "READ + QA", "website_changes": 0, "google_ads_changes": 0,
       "forms_submitted": 0, "telephone_links_activated": 0, "cache_purges": 0,
       "stale_marker_watched_for": STALE}

JS_FIELDS = """
() => {
  const forms = [];
  document.querySelectorAll('form').forEach((f, i) => {
    const fields = [];
    f.querySelectorAll('input,textarea,select').forEach(el => {
      fields.push({name: el.name||'', id: el.id||'',
                   type: (el.type||el.tagName||'').toLowerCase(),
                   domValue: (el.value||'').slice(0,240),
                   attrValue: (el.getAttribute('value')||'').slice(0,240)});
    });
    const st = getComputedStyle(f);
    forms.push({index:i, id:f.id||'', action:f.action||'',
                display:st.display, visibility:st.visibility,
                offsetParent: f.offsetParent!==null,
                rectH: Math.round(f.getBoundingClientRect().height),
                labels: Array.from(f.querySelectorAll('label')).map(l=>({
                  for: l.getAttribute('for')||'', text:(l.innerText||'').trim().slice(0,50)})),
                fields});
  });
  const ids = Array.from(document.querySelectorAll('[id]')).map(e=>e.id);
  const seen={}, dup=[];
  ids.forEach(x=>{ if(seen[x]){ if(!dup.includes(x)) dup.push(x);} seen[x]=1; });
  return {forms, allIdCount: ids.length, duplicateIds: dup,
          duplicateIdCount: dup.length};
}
"""
JS_TRACK = """
() => {
  const out = {dataLayerPresent: !!window.dataLayer,
               dataLayerLength: (window.dataLayer||[]).length,
               dataLayerEvents: (window.dataLayer||[]).map(x=>{
                 try{return (x && x.event) ? x.event : Object.keys(x||{})[0];}catch(e){return '?';}
               }).slice(0,30),
               cookies: document.cookie.split('; ').map(c=>c.split('=')[0]).filter(Boolean),
               wcVisitorCookie: (document.cookie.match(/wc_visitor=[^;]*/)||[''])[0].slice(0,80),
               localStorageKeys: [], sessionStorageKeys: []};
  try{ out.localStorageKeys = Object.keys(localStorage||{}).slice(0,60); }catch(e){}
  try{ out.sessionStorageKeys = Object.keys(sessionStorage||{}).slice(0,60); }catch(e){}
  return out;
}
"""
JS_TELS = """
() => Array.from(document.querySelectorAll("a[href^='tel:']")).map(a=>({
  href:a.getAttribute('href'), text:(a.innerText||'').trim().slice(0,50),
  visible: !!(a.offsetWidth||a.offsetHeight||a.getClientRects().length)}))
"""
JS_OVERLAY = """
() => {
  const f = document.querySelector('form');
  if(!f) return {formFound:false};
  const r = f.getBoundingClientRect();
  const cx = Math.round(r.left + r.width/2), cy = Math.round(r.top + Math.min(40, r.height/2));
  const top = document.elementFromPoint(cx, cy);
  return {formFound:true,
          formHeight: Math.round(r.height),
          topElementAtFormPoint: top ? (top.tagName + '.' + String(top.className||'').slice(0,40)) : null,
          formContainsTopElement: top ? f.contains(top) : false,
          horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 2};
}
"""


def raw_headers(url):
    """Raw HTTP, no JS. Used ONLY for response and cache headers plus server HTML."""
    try:
        r = urllib.request.Request(url, headers={"User-Agent": UA_D})
        with urllib.request.urlopen(r, timeout=45) as z:
            h = {k.lower(): v for k, v in z.headers.items()}
            body = z.read().decode("utf-8", "replace")
            return {"status": z.status, "final_url": z.geturl(),
                    "x_cache_enabled": h.get("x-cache-enabled"),
                    "x_proxy_cache": h.get("x-proxy-cache"),
                    "cache_control": h.get("cache-control"),
                    "age": h.get("age"),
                    "nitro": h.get("x-nitro-cache") or h.get("x-nitropack-cache"),
                    "sg": h.get("x-sg-cache") or h.get("host-header"),
                    "server": h.get("server"),
                    "all_cache_headers": {k: v for k, v in h.items()
                                          if "cache" in k or k in ("age", "vary", "expires")},
                    "server_html": body}
    except Exception as e:
        return {"status": None, "error": f"{type(e).__name__}: {str(e)[:160]}"}


def probe(pw, page_key, url, run_label, params, profile, marker_map,
          extra_stale_markers=()):
    """One isolated test in a brand-new incognito context."""
    br = pw.chromium.launch()
    ctx = br.new_context(user_agent=UA_D if profile == "desktop" else UA_M,
                         viewport=VP_D if profile == "desktop" else VP_M,
                         is_mobile=(profile == "mobile"),
                         has_touch=(profile == "mobile"), locale="en-US")
    pg = ctx.new_page()
    console, failed = [], []
    pg.on("console", lambda m: console.append({"t": m.type, "x": m.text[:180]}))
    pg.on("requestfailed", lambda r: failed.append(
        {"url": r.url[:150], "fail": (r.failure or "")[:100]}))
    rec = {"page": page_key, "run": run_label, "profile": profile,
           "requested_url": url + params, "expected": dict(marker_map)}
    # capture the FINAL page response (not the SG-Captcha 202 stub) so raw server
    # HTML is the real document
    final_resp = {}

    def _cap(r):
        try:
            if r.url.split("?")[0].rstrip("/") == url.rstrip("/") and r.status == 200:
                final_resp["r"] = r
        except Exception:
            pass
    pg.on("response", _cap)

    try:
        t0 = time.time()
        resp = pg.goto(url + params, wait_until="domcontentloaded", timeout=90000)
        rec["initial_http_status"] = resp.status if resp else None
        sg = {k.lower(): v for k, v in (resp.headers if resp else {}).items()}.get("sg-captcha")
        rec["sg_captcha_challenge_served"] = bool(sg) or (resp and resp.status == 202)
        # SiteGround SG-Captcha answers automation with a 179-byte 202 stub that
        # meta-refreshes to /.well-known/sgcaptcha/. A real browser solves it and is
        # redirected back. Wait for the REAL document before measuring anything.
        for _ in range(12):
            pg.wait_for_timeout(2500)
            st = pg.evaluate("() => ({f: document.querySelectorAll('form').length,"
                             " l: document.body ? document.body.innerText.length : 0})")
            if st["f"] > 0 and st["l"] > 500:
                break
        rec["challenge_passed"] = bool(final_resp.get("r"))
        fr = final_resp.get("r")
        rec["http_status"] = fr.status if fr else (resp.status if resp else None)
        rec["final_url"] = pg.url
        hdrs = {k.lower(): v for k, v in (fr.headers if fr else (resp.headers if resp else {})).items()}
        rec["x_proxy_cache"] = hdrs.get("x-proxy-cache")
        rec["x_cache_enabled"] = hdrs.get("x-cache-enabled")
        rec["x_proxy_cache_info"] = hdrs.get("x-proxy-cache-info")
        rec["cache_control"] = hdrs.get("cache-control")
        rec["age"] = hdrs.get("age")
        try:
            srv = fr.text() if fr else ""
        except Exception:
            srv = ""
        rec["server_html_has_stale"] = STALE in srv
        rec["server_html_len"] = len(srv)
        # server-side hidden input values BEFORE any JS
        rec["server_hidden_values"] = sorted({
            m.group(2) for m in re.finditer(
                r'<input[^>]*name=["\'](input_\d+|[a-z_]*(?:gclid|gbraid|wbraid|utm)[a-z_]*)'
                r'["\'][^>]*value=["\']([^"\']+)["\']', srv, re.I)
            if m.group(2).strip()} - {"", "0", "1"})
        pg.wait_for_timeout(9500)               # >= 9 s AFTER the real page renders
        rec["settle_ms"] = int((time.time() - t0) * 1000)

        dom = pg.evaluate(JS_FIELDS)
        rec["form_count"] = len(dom["forms"])
        rec["form_ids"] = [f["id"] for f in dom["forms"]]
        rec["visible_forms"] = sum(1 for f in dom["forms"]
                                   if f["offsetParent"] and f["rectH"] > 0)
        rec["hidden_or_zero_height_forms"] = sum(
            1 for f in dom["forms"] if not f["offsetParent"] or f["rectH"] == 0)
        rec["duplicate_dom_ids"] = dom["duplicateIds"][:60]
        rec["duplicate_dom_id_count"] = dom["duplicateIdCount"]
        rec["total_ids_on_page"] = dom["allIdCount"]

        # ---- DISCOVER the field mapping: which field holds which marker ----
        populated, mapping = {}, {}
        for f in dom["forms"]:
            for fl in f["fields"]:
                v = (fl["domValue"] or "").strip()
                if not v or v in ("0", "1", "postback", "gravity-theme", "[]"):
                    continue
                populated.setdefault(fl["name"] or fl["id"], set()).add(v)
        rec["populated_fields"] = {k: sorted(v) for k, v in populated.items()}
        blob = json.dumps(rec["populated_fields"])
        for role, want in marker_map.items():
            hit = [k for k, vals in populated.items() if want in vals]
            mapping[role] = {"expected": want, "found_in_fields": hit,
                             "captured": bool(hit)}
        rec["field_mapping_discovered"] = mapping
        rec["all_expected_captured"] = all(v["captured"] for v in mapping.values())
        rec["observed_click_id"] = next(
            (v["expected"] for k, v in mapping.items()
             if k in ("gclid", "gbraid", "wbraid") and v["captured"]), None)
        rec["utms_correct"] = all(mapping[k]["captured"] for k in mapping
                                  if k.startswith("utm"))
        # ---- contamination: any OTHER test's marker present? ----
        contaminants = [STALE] + list(extra_stale_markers)
        rec["stale_values_found"] = [s for s in contaminants if s and s in blob]
        rec["contaminated"] = bool(rec["stale_values_found"])
        # any marker-shaped string that is not one of ours
        ours = set(marker_map.values())
        foreign = sorted({v for vals in populated.values() for v in vals
                          if re.match(r"^QA\d{4}", v) and v not in ours})
        rec["foreign_qa_markers"] = foreign
        if foreign:
            rec["contaminated"] = True

        tr = pg.evaluate(JS_TRACK)
        page_html = pg.content()
        net_blob = page_html
        rec["gtm_present"] = GTM_ID in net_blob
        rec["aw_present"] = AW_ID in net_blob
        rec["ga4_present"] = GA4_ID in net_blob
        rec["whatconverts_present"] = bool(re.search(r"whatconverts|wc_visitor|iyzt",
                                                     net_blob + json.dumps(tr), re.I))
        rec["wc_visitor_cookie"] = tr.get("wcVisitorCookie") or None
        rec["datalayer_present"] = tr.get("dataLayerPresent")
        rec["datalayer_length"] = tr.get("dataLayerLength")
        rec["datalayer_events"] = tr.get("dataLayerEvents")
        rec["cookies"] = tr.get("cookies")
        rec["localStorage_keys"] = tr.get("localStorageKeys")
        rec["sessionStorage_keys"] = tr.get("sessionStorageKeys")

        tels = pg.evaluate(JS_TELS)
        rec["tel_links"] = tels
        rec["tel_digits"] = sorted({re.sub(r"\D", "", t["href"] or "") for t in tels})
        rec["approved_number_present"] = PAID in re.sub(r"\D", "", pg.inner_text("body"))
        rec["mixed_number_clickable"] = any(
            MIXED in re.sub(r"\D", "", t["href"] or "") and t["visible"] for t in tels)
        rec["mixed_number_in_dom"] = any(MIXED in re.sub(r"\D", "", t["href"] or "")
                                         for t in tels) or MIXED in re.sub(r"\D", "", page_html)
        rec["forwarding_number_public"] = DEST in re.sub(r"\D", "", pg.inner_text("body"))

        ov = pg.evaluate(JS_OVERLAY)
        rec["usability"] = ov
        rec["console_errors"] = [x for x in console if x["t"] == "error"][:12]
        rec["console_error_count"] = sum(1 for x in console if x["t"] == "error")
        rec["failed_requests"] = failed[:12]
    except Exception as ex:
        rec["error"] = f"{type(ex).__name__}: {str(ex)[:300]}"
    finally:
        ctx.close(); br.close()
    return rec


def main():
    EVID.mkdir(parents=True, exist_ok=True)
    SNAP.mkdir(parents=True, exist_ok=True)

    print("=== TEST 1: RAW HTTP CACHE HEADERS (no JS) ===")
    out["test1_cache"] = {}
    for k, u in PAGES.items():
        h = raw_headers(u)
        srv = h.pop("server_html", "")
        h["server_html_contains_stale_marker"] = STALE in srv
        h["server_html_hidden_values"] = sorted({
            m.group(2) for m in re.finditer(
                r'<input[^>]*name=["\'](input_\d+)["\'][^>]*value=["\']([^"\']+)["\']',
                srv, re.I) if m.group(2).strip() not in ("", "0", "1")})[:12]
        verdict = (h.get("x_proxy_cache") or "NONE").upper()
        out["test1_cache"][k] = h
        print(f"  {k:32s} HTTP {h.get('status')}  x-proxy-cache={verdict:8s} "
              f"x-cache-enabled={h.get('x_cache_enabled')}  age={h.get('age')}  "
              f"stale_in_server_html={h['server_html_contains_stale_marker']}")
        if h["server_html_hidden_values"]:
            print(f"      server HTML hidden values: {h['server_html_hidden_values']}")

    results = []
    all_markers = []
    with sync_playwright() as pw:
        print("\n=== TEST 2+3: 24 PARAMETERISED TESTS (fresh context each, >=9s settle) ===")
        for pk, url in PAGES.items():
            for run, (idkind, profile) in enumerate(
                    [("gclid", "desktop"), ("gbraid", "mobile"),
                     ("wbraid", "desktop"), ("gclid", "desktop")], start=1):
                tag = f"QA0916{pk.replace('-','')[:8].upper()}R{run}T{RUN_TS}"
                mm = {idkind: tag,
                      "utm_source": "google",
                      "utm_medium": "cpc",
                      "utm_campaign": f"{tag}CAMP",
                      "utm_term": f"{tag}TERM",
                      "utm_content": f"{tag}CONT"}
                qs = (f"?{idkind}={tag}&utm_source=google&utm_medium=cpc"
                      f"&utm_campaign={tag}CAMP&utm_term={tag}TERM&utm_content={tag}CONT")
                label = f"run{run}-{idkind}-{profile}"
                if run == 4:
                    # warm-cache isolation: load marker A, close, fresh context marker B
                    a = f"{tag}A"
                    mmA = {"gclid": a, "utm_source": "google", "utm_medium": "cpc",
                           "utm_campaign": f"{a}CAMP", "utm_term": f"{a}TERM",
                           "utm_content": f"{a}CONT"}
                    qsA = (f"?gclid={a}&utm_source=google&utm_medium=cpc"
                           f"&utm_campaign={a}CAMP&utm_term={a}TERM&utm_content={a}CONT")
                    recA = probe(pw, pk, url, "run4-warmA-desktop", qsA, "desktop", mmA)
                    recA["role"] = "warm-cache seed (not counted in the 24)"
                    results.append(recA)
                    all_markers.append(a)
                    b = f"{tag}B"
                    mm = {"gclid": b, "utm_source": "google", "utm_medium": "cpc",
                          "utm_campaign": f"{b}CAMP", "utm_term": f"{b}TERM",
                          "utm_content": f"{b}CONT"}
                    qs = (f"?gclid={b}&utm_source=google&utm_medium=cpc"
                          f"&utm_campaign={b}CAMP&utm_term={b}TERM&utm_content={b}CONT")
                    label = "run4-warmB-desktop"
                    rec = probe(pw, pk, url, label, qs, "desktop", mm,
                                extra_stale_markers=[a])
                    rec["warm_cache_marker_A"] = a
                    rec["marker_A_absent"] = a not in json.dumps(
                        rec.get("populated_fields", {}))
                else:
                    rec = probe(pw, pk, url, label, qs, profile, mm)
                rec["counted_in_24"] = True
                results.append(rec)
                all_markers.append(tag)
                time.sleep(3)
                ok = rec.get("all_expected_captured") and not rec.get("contaminated")
                print(f"  {pk:30s} {label:22s} HTTP {rec.get('http_status')} "
                      f"cache={str(rec.get('x_proxy_cache')):6s} "
                      f"captured={rec.get('all_expected_captured')} "
                      f"stale={rec.get('stale_values_found')} "
                      f"dupIDs={rec.get('duplicate_dom_id_count')} "
                      f"forms={rec.get('form_count')} -> "
                      f"{'PASS' if ok else 'FAIL'}")

        print("\n=== TEST 4: SIX NO-PARAMETER ISOLATION CONTROLS ===")
        controls = []
        for pk, url in PAGES.items():
            rec = probe(pw, pk, url, "control-noparams-desktop", "", "desktop", {},
                        extra_stale_markers=all_markers)
            rec["counted_in_24"] = False
            rec["role"] = "no-parameter control"
            pop = json.dumps(rec.get("populated_fields", {}))
            leaked = [m for m in all_markers + [STALE] if m and m in pop]
            rec["leaked_markers"] = leaked
            rec["control_clean"] = not leaked
            controls.append(rec)
            print(f"  {pk:32s} populated_attr_fields="
                  f"{len(rec.get('populated_fields', {}))} leaked={leaked or 'NONE'} -> "
                  f"{'PASS' if rec['control_clean'] else 'FAIL'}")
        out["test4_controls"] = controls

        print("\n=== TEST 5: SAME-VISITOR PERSISTENCE (one context, 4 navigations) ===")
        br = pw.chromium.launch()
        ctx = br.new_context(user_agent=UA_D, viewport=VP_D, locale="en-US")
        pg = ctx.new_page()
        p1 = f"QA0916PERSIST1T{RUN_TS}"
        p2 = f"QA0916PERSIST2T{RUN_TS}"
        steps = []

        def snap(label):
            d = pg.evaluate(JS_FIELDS)
            pop = {}
            for f in d["forms"]:
                for fl in f["fields"]:
                    v = (fl["domValue"] or "").strip()
                    if v and v not in ("0", "1", "postback", "gravity-theme", "[]"):
                        pop.setdefault(fl["name"] or fl["id"], set()).add(v)
            pop = {k: sorted(v) for k, v in pop.items()}
            j = json.dumps(pop)
            s = {"step": label, "url": pg.url, "populated_fields": pop,
                 "contains_marker1": p1 in j, "contains_marker2": p2 in j}
            steps.append(s)
            print(f"  {label:44s} m1={s['contains_marker1']} m2={s['contains_marker2']}")
            return s

        pg.goto(PAGES["ac-repair"] + f"?gclid={p1}&utm_source=google&utm_medium=cpc"
                f"&utm_campaign={p1}CAMP&utm_term={p1}TERM&utm_content={p1}CONT",
                wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(9500); snap("1. enter /ac-repair/ with marker1")
        pg.goto(PAGES["hvac-repair"], wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(9500); snap("2. navigate to /hvac-repair/ WITHOUT params")
        pg.goto(PAGES["hvac-repair"] + f"?gclid={p2}&utm_source=google&utm_medium=cpc"
                f"&utm_campaign={p2}CAMP&utm_term={p2}TERM&utm_content={p2}CONT",
                wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(9500); s3 = snap("3. re-enter /hvac-repair/ with marker2")
        ctx.close(); br.close()
        br2 = pw.chromium.launch()
        ctx2 = br2.new_context(user_agent=UA_D, viewport=VP_D, locale="en-US")
        pg2 = ctx2.new_page()
        pg2.goto(PAGES["hvac-repair"], wait_until="networkidle", timeout=90000)
        pg2.wait_for_timeout(9500)
        d = pg2.evaluate(JS_FIELDS)
        pop = {}
        for f in d["forms"]:
            for fl in f["fields"]:
                v = (fl["domValue"] or "").strip()
                if v and v not in ("0", "1", "postback", "gravity-theme", "[]"):
                    pop.setdefault(fl["name"] or fl["id"], set()).add(v)
        pop = {k: sorted(v) for k, v in pop.items()}
        j = json.dumps(pop)
        s4 = {"step": "4. SEPARATE fresh context, no params", "url": pg2.url,
              "populated_fields": pop, "contains_marker1": p1 in j,
              "contains_marker2": p2 in j}
        steps.append(s4)
        print(f"  {s4['step']:44s} m1={s4['contains_marker1']} m2={s4['contains_marker2']}")
        ctx2.close(); br2.close()
        persists = steps[1]["contains_marker1"]
        rule = ("NO PERSISTENCE - attribution is read from the URL only"
                if not persists else
                ("LAST-CLICK - a newer click id overwrites the stored one"
                 if s3["contains_marker2"] and not s3["contains_marker1"]
                 else "FIRST-CLICK - the original click id is retained"))
        out["test5_persistence"] = {"steps": steps, "persists_across_pages": persists,
                                    "attribution_rule_observed": rule,
                                    "fresh_context_isolated": not (s4["contains_marker1"]
                                                                   or s4["contains_marker2"])}
        print(f"  => attribution rule observed: {rule}")
        print(f"  => fresh context isolated: {out['test5_persistence']['fresh_context_isolated']}")

    out["test2_3_results"] = results
    counted = [r for r in results if r.get("counted_in_24")]
    out["counts"] = {
        "parameterised_tests": len(counted),
        "captured_own_values": sum(1 for r in counted if r.get("all_expected_captured")),
        "contaminated": sum(1 for r in counted if r.get("contaminated")),
        "http_200": sum(1 for r in counted if r.get("http_status") == 200),
        "controls": len(controls),
        "controls_clean": sum(1 for r in controls if r.get("control_clean")),
        "max_duplicate_dom_ids": max((r.get("duplicate_dom_id_count") or 0)
                                     for r in counted + controls),
        "max_form_count": max((r.get("form_count") or 0) for r in counted + controls),
        "gtm_all": all(r.get("gtm_present") for r in counted),
        "wc_all": all(r.get("whatconverts_present") for r in counted),
        "mixed_number_clickable_anywhere": any(r.get("mixed_number_clickable")
                                               for r in counted + controls),
        "forwarding_number_public_anywhere": any(r.get("forwarding_number_public")
                                                 for r in counted + controls),
    }
    p = SNAP / f"attribution-fix-verification-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("\n" + "=" * 78)
    print("SUMMARY")
    for k, v in out["counts"].items():
        print(f"  {k:38s} {v}")
    print(f"\nWROTE {p}")
    print("FORMS SUBMITTED: 0 | TELEPHONE LINKS ACTIVATED: 0 | CACHE PURGES: 0")
    print("WEBSITE CHANGES: 0 | GOOGLE ADS CHANGES: 0")


if __name__ == "__main__":
    sys.exit(main())
