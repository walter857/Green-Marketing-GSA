#!/usr/bin/env python3
"""MasterGrass controlled attribution cycle | 2026-09-17 | Phase 1, cycle 1.

READ-ONLY. Parameterised GET navigations only. No form submitted, no telephone link
activated, no website/GTM/WhatConverts/Google Ads change, no cache purge by me.

CRITICAL ORDERING: the very first HTTP request this process makes to the target is
Visitor A's parameterised request. The page is NOT loaded beforehand.

Sequence: A (expect MISS) -> A reload (expect HIT) -> B (fresh context) -> C (no params).
"""
from __future__ import annotations
import datetime, hashlib, json, re, sys, time
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "cross-client-attribution"
EVID = OUT / "evidence-mastergrass-2026-09-17"
TZ = ZoneInfo("America/New_York")
URL = "https://offer.mastergrasslawncare.com/landscaping-contractor/"
UA_D = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
TS = datetime.datetime.now(TZ).strftime("%H%M%S")


def qs(v):
    return (f"?gclid=QA-MASTERGRASS-{v}-GCLID-{TS}"
            f"&gbraid=QA-MASTERGRASS-{v}-GBRAID-{TS}"
            f"&wbraid=QA-MASTERGRASS-{v}-WBRAID-{TS}"
            f"&utm_source=QA-MASTERGRASS-{v}-SOURCE-{TS}"
            f"&utm_medium=QA-MASTERGRASS-{v}-MEDIUM-{TS}"
            f"&utm_campaign=QA-MASTERGRASS-{v}-CAMPAIGN-{TS}"
            f"&utm_term=QA-MASTERGRASS-{v}-TERM-{TS}"
            f"&utm_content=QA-MASTERGRASS-{v}-CONTENT-{TS}")


def expected(v):
    return {"gclid": f"QA-MASTERGRASS-{v}-GCLID-{TS}",
            "gbraid": f"QA-MASTERGRASS-{v}-GBRAID-{TS}",
            "wbraid": f"QA-MASTERGRASS-{v}-WBRAID-{TS}",
            "utm_source": f"QA-MASTERGRASS-{v}-SOURCE-{TS}",
            "utm_medium": f"QA-MASTERGRASS-{v}-MEDIUM-{TS}",
            "utm_campaign": f"QA-MASTERGRASS-{v}-CAMPAIGN-{TS}",
            "utm_term": f"QA-MASTERGRASS-{v}-TERM-{TS}",
            "utm_content": f"QA-MASTERGRASS-{v}-CONTENT-{TS}"}


JS = """
() => {
  const forms=[];
  document.querySelectorAll('form').forEach((f,i)=>{
    const fields=[];
    f.querySelectorAll('input,textarea,select').forEach(el=>{
      fields.push({name:el.name||'', id:el.id||'',
                   type:(el.type||el.tagName||'').toLowerCase(),
                   domValue:(el.value||'').slice(0,240),
                   attrValue:(el.getAttribute('value')||'').slice(0,240)});
    });
    forms.push({index:i, id:f.id||'', visible:f.offsetParent!==null,
                rectH:Math.round(f.getBoundingClientRect().height), fields});
  });
  const ids=Array.from(document.querySelectorAll('[id]')).map(e=>e.id);
  const seen={},dup=[]; ids.forEach(x=>{if(seen[x]){if(!dup.includes(x))dup.push(x);}seen[x]=1;});
  let ls=[],ss=[];
  try{ls=Object.entries(localStorage).map(([k,v])=>({k,v:String(v).slice(0,200)}));}catch(e){}
  try{ss=Object.entries(sessionStorage).map(([k,v])=>({k,v:String(v).slice(0,200)}));}catch(e){}
  return {forms, formCount:forms.length, duplicateIds:dup, duplicateIdCount:dup.length,
          totalIds:ids.length,
          cookies:document.cookie.split('; ').filter(Boolean).map(c=>{
            const i=c.indexOf('='); return {k:c.slice(0,i), v:c.slice(i+1,i+201)};}),
          localStorage:ls, sessionStorage:ss,
          gtm:document.documentElement.innerHTML.includes('GTM-5M6RJZVK'),
          wcCookie:(document.cookie.match(/wc_visitor=[^;]*/)||[''])[0].slice(0,60),
          dataLayerLen:(window.dataLayer||[]).length,
          title:document.title,
          tels:Array.from(document.querySelectorAll("a[href^='tel:']")).map(a=>a.getAttribute('href'))};
}
"""


def visit(pw, label, params, ctx_reuse=None, screenshot=None):
    if ctx_reuse:
        br, ctx = ctx_reuse
    else:
        br = pw.chromium.launch()
        ctx = br.new_context(user_agent=UA_D, viewport={"width": 1440, "height": 900},
                             locale="en-US")
    pg = ctx.new_page()
    final = {}
    pg.on("response", lambda r: final.__setitem__("r", r)
          if r.url.split("?")[0].rstrip("/") == URL.rstrip("/") else None)
    rec = {"visitor": label, "requested_url": URL + params,
           "at": datetime.datetime.now(TZ).isoformat()}
    resp = pg.goto(URL + params, wait_until="domcontentloaded", timeout=90000)
    hd = {k.lower(): v for k, v in (resp.headers if resp else {}).items()}
    rec["http_status"] = resp.status if resp else None
    rec["cache_headers"] = {k: v for k, v in hd.items()
                            if "cache" in k or k in ("age", "vary", "server",
                                                     "host-header", "sg-f-cache",
                                                     "x-nitro-cache", "sg-captcha")}
    rec["x_proxy_cache"] = hd.get("x-proxy-cache")
    for _ in range(10):
        pg.wait_for_timeout(2000)
        try:
            st = pg.evaluate("() => ({f:document.querySelectorAll('form').length,"
                             " l:document.body?document.body.innerText.length:0})")
        except Exception:
            continue
        if st["f"] > 0 and st["l"] > 500:
            break
    # NitroPack-class optimisers run NO JavaScript until the first user interaction, so a
    # load-and-wait probe reports GTM, WhatConverts and every JS-populated field as absent
    # (confirmed on Ambient 2026-09-17). This does not re-request the page and cannot change
    # what the cache stores; it only lets deferred scripts run before the DOM probe.
    try:
        pg.mouse.move(420, 300)
        pg.mouse.move(760, 520)
        pg.mouse.wheel(0, 1400)
        pg.keyboard.press("PageDown")
    except Exception:
        pass
    pg.wait_for_timeout(9500)
    try:
        srv = final["r"].text() if final.get("r") else ""
    except Exception:
        srv = ""
    rec["server_html_bytes"] = len(srv)
    rec["server_html_qa_markers"] = sorted(set(re.findall(r"QA-MASTERGRASS-[A-Z0-9-]+", srv)))
    rec["server_html_hidden_values"] = [
        {"field": m.group(1), "value": m.group(2)[:120]}
        for m in re.finditer(
            r'<input[^>]*name=[\'"](input_\d+)[\'"][^>]*value=[\'"]([^\'"]+)[\'"]', srv, re.I)
        if m.group(2).strip() not in ("", "0", "1")]
    d = None
    for _ in range(4):
        try:
            d = pg.evaluate(JS); break
        except Exception:
            pg.wait_for_timeout(2500)
    d = d or {}
    rec["form_count"] = d.get("formCount")
    rec["duplicate_id_count"] = d.get("duplicateIdCount")
    rec["title"] = d.get("title")
    rec["gtm_present"] = d.get("gtm")
    rec["wc_visitor_cookie"] = d.get("wcCookie") or None
    rec["dataLayer_length"] = d.get("dataLayerLen")
    rec["tel_links"] = d.get("tels")
    pop = {}
    for f in d.get("forms", []):
        for fl in f["fields"]:
            v = (fl["domValue"] or "").strip()
            if v and v not in ("0", "1", "postback", "gravity-theme", "[]"):
                pop.setdefault(fl["name"] or fl["id"], set()).add(v)
    rec["live_dom_populated"] = {k: sorted(v) for k, v in pop.items()}
    rec["live_dom_qa_markers"] = sorted(set(re.findall(
        r"QA-MASTERGRASS-[A-Z0-9-]+", json.dumps(rec["live_dom_populated"]))))
    rec["cookies"] = [c["k"] for c in d.get("cookies", [])]
    rec["cookie_qa_markers"] = sorted(set(re.findall(
        r"QA-MASTERGRASS-[A-Z0-9-]+", json.dumps(d.get("cookies", [])))))
    rec["storage_qa_markers"] = sorted(set(re.findall(
        r"QA-MASTERGRASS-[A-Z0-9-]+",
        json.dumps(d.get("localStorage", []) + d.get("sessionStorage", [])))))
    rec["hidden_field_names"] = sorted({fl["name"] for f in d.get("forms", [])
                                        for fl in f["fields"] if fl["type"] == "hidden"})
    if screenshot:
        EVID.mkdir(parents=True, exist_ok=True)
        pg.screenshot(path=str(EVID / screenshot))
        rec["screenshot"] = screenshot
    if ctx_reuse:
        pg.close()
        return rec, (br, ctx)
    ctx.close(); br.close()
    return rec, None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "target": URL, "cycle": 1,
           "preconditions": {
               "cache_purged_by": "Ahmad, confirmed by operator",
               "cache_remains_enabled": True,
               "page_not_loaded_before_visitor_a": True,
               "first_request_after_purge_is_visitor_a": True},
           "forms_submitted": 0, "tel_links_activated": 0, "website_changes": 0,
           "cache_purges_by_me": 0,
           "expected": {"A": expected("A"), "B": expected("B")},
           "visits": []}

    print("=== MASTERGRASS CYCLE 1 ===")
    print(f"target: {URL}")
    print("Visitor A is the FIRST request this process makes to the target.\n")
    with sync_playwright() as pw:
        # ---- Visitor A: FIRST request after the purge ----
        a, keep = visit(pw, "A", qs("A"), ctx_reuse=None, screenshot="01-visitorA-first.png")
        out["visits"].append(a)
        print(f"VISITOR A   HTTP {a['http_status']}  x-proxy-cache={a['x_proxy_cache']}")
        print(f"  server HTML QA markers : {a['server_html_qa_markers']}")
        print(f"  server HTML hidden vals: {a['server_html_hidden_values']}")
        print(f"  live DOM populated     : {json.dumps(a['live_dom_populated'])[:400]}")
        print(f"  hidden fields          : {a['hidden_field_names']}")
        print(f"  forms={a['form_count']} dupIDs={a['duplicate_id_count']} "
              f"GTM={a['gtm_present']} WC={bool(a['wc_visitor_cookie'])}")

        time.sleep(3)
        # ---- Visitor A reload, SAME context, to force a HIT ----
        br2 = pw.chromium.launch()
        ctx2 = br2.new_context(user_agent=UA_D, viewport={"width": 1440, "height": 900},
                               locale="en-US")
        a2, _ = visit(pw, "A-reload", qs("A"), ctx_reuse=(br2, ctx2),
                      screenshot="02-visitorA-reload.png")
        out["visits"].append(a2)
        print(f"\nVISITOR A reload  HTTP {a2['http_status']}  "
              f"x-proxy-cache={a2['x_proxy_cache']}")
        print(f"  server HTML QA markers : {a2['server_html_qa_markers']}")
        ctx2.close(); br2.close()

        time.sleep(3)
        # ---- Visitor B: completely separate context, different values ----
        b, _ = visit(pw, "B", qs("B"), ctx_reuse=None, screenshot="03-visitorB.png")
        out["visits"].append(b)
        a_markers = set(a["server_html_qa_markers"]) | set(a["live_dom_qa_markers"])
        a_only = {m for m in a_markers if "-A-" in m}
        b_srv = set(b["server_html_qa_markers"]); b_dom = set(b["live_dom_qa_markers"])
        b_got_a = sorted((b_srv | b_dom) & a_only)
        b["visitor_a_values_found"] = b_got_a
        b["received_own_values"] = sorted(m for m in (b_srv | b_dom) if "-B-" in m)
        print(f"\nVISITOR B   HTTP {b['http_status']}  x-proxy-cache={b['x_proxy_cache']}")
        print(f"  server HTML QA markers : {b['server_html_qa_markers']}")
        print(f"  live DOM populated     : {json.dumps(b['live_dom_populated'])[:400]}")
        print(f"  >>> VISITOR A VALUES IN B: {b_got_a or 'NONE'}")
        print(f"  >>> B received own vals : {b['received_own_values'] or 'NONE'}")

        time.sleep(3)
        # ---- Visitor C: clean, no parameters ----
        c, _ = visit(pw, "C", "", ctx_reuse=None, screenshot="04-visitorC-noparams.png")
        out["visits"].append(c)
        c_all = set(c["server_html_qa_markers"]) | set(c["live_dom_qa_markers"])
        c["any_qa_markers_found"] = sorted(c_all)
        print(f"\nVISITOR C   HTTP {c['http_status']}  x-proxy-cache={c['x_proxy_cache']}")
        print(f"  server HTML QA markers : {c['server_html_qa_markers']}")
        print(f"  live DOM populated     : {json.dumps(c['live_dom_populated'])[:400]}")
        print(f"  >>> ANY QA MARKER IN C : {sorted(c_all) or 'NONE'}")

    # ---- verdict ----
    a_first_miss = (a["x_proxy_cache"] or "").upper() in ("MISS", "EXPIRED", "", "NONE")
    a_got_own = bool([m for m in (set(a["server_html_qa_markers"]) |
                                  set(a["live_dom_qa_markers"])) if "-A-" in m])
    hit_seen = "HIT" in {(a2["x_proxy_cache"] or "").upper(),
                         (b["x_proxy_cache"] or "").upper(),
                         (c["x_proxy_cache"] or "").upper()}
    leak = bool(b.get("visitor_a_values_found")) or bool(c.get("any_qa_markers_found"))
    if leak:
        verdict = "CONFIRMED SAME LEAK"
    elif not a_got_own:
        verdict = ("INCONCLUSIVE - Visitor A did not capture its own values on the "
                   "initial request")
    elif not hit_seen:
        verdict = ("INCONCLUSIVE - the cache path was never exercised; no HIT was "
                   "observed on any follow-up request")
    else:
        verdict = "CLEAN CYCLE (cycle 1 of 3 required)"
    out["cycle_1_verdict"] = verdict
    out["verdict_inputs"] = {
        "visitor_a_first_cache_state": a["x_proxy_cache"],
        "visitor_a_captured_own_values": a_got_own,
        "hit_observed_on_a_followup": hit_seen,
        "visitor_b_received_visitor_a_values": b.get("visitor_a_values_found"),
        "visitor_c_received_any_qa_marker": c.get("any_qa_markers_found")}
    p = OUT / "mastergrass-cycle1-2026-09-17.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("\n" + "=" * 70)
    print(f"CYCLE 1 VERDICT: {verdict}")
    print(f"WROTE {p}")
    print("FORMS SUBMITTED: 0 | TEL ACTIVATED: 0 | WEBSITE/GTM/WC/ADS CHANGES: 0")


if __name__ == "__main__":
    sys.exit(main())
