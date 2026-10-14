#!/usr/bin/env python3
"""Ambient | 2026-09-17 | main-website URL + tracking QA for the heating build.

READ + QA ONLY. GET navigations only. No form submitted, no telephone link activated,
no website/GTM/WhatConverts/Google Ads change. Synthetic markers only.
"""
from __future__ import annotations
import datetime, json, re, sys, time, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
EVID = ROOT / "reports" / "ambient-cooling-heating" / "evidence" / "heating-url-qa-2026-09-17"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-17"
TS = datetime.datetime.now(TZ).strftime("%H%M%S")
B = "https://ambientcoolingandheating.com"
URLS = {
    "furnace-repair": f"{B}/services/heating-services/furnace-repair/",
    "heat-pumps": f"{B}/services/heating-services/heat-pumps/",
    "mini-splits": f"{B}/services/cooling-services/mini-splits/",
    "boiler-repair": f"{B}/services/heating-services/boiler-repair/",
    "heating-services-hub": f"{B}/services/heating-services/",
    "oil-furnace-installations": f"{B}/services/heating-services/oil-furnace-installations/",
    "oil-replacement": f"{B}/services/heating-services/oil-replacement/",
}
UA_D = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_M = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
PAID, MIXED, MAIN = "4107056354", "4109141456", "4107610932"
GTM, AW, GA4 = "GTM-PQTPQ436", "AW-11155434808", "G-9X9ZHNCRWF"
BARRED = {
    "emergency": r"\bemergency\b", "24/7": r"\b24\s*/\s*7\b",
    "same-day": r"\bsame.?day\b", "financing": r"\bfinanc(e|ing)\b|\brebate\b",
    "warranty": r"\bwarrant(y|ies)\b", "licensed/insured": r"licen[cs]ed|\binsured\b",
    "rating/reviews": r"\b\d+(\.\d)?\s*stars?\b|\b\d+\+?\s*reviews?\b|\brated\b",
    "free estimate": r"free (estimate|quote|consultation)",
    "response time": r"within \d+\s*(min|hour)|response time",
    "guarantee": r"\bguarantee",
}
JS = """
() => {
  const forms=[];
  document.querySelectorAll('form').forEach((f,i)=>{
    const fields=[];
    f.querySelectorAll('input,textarea,select').forEach(el=>{
      fields.push({name:el.name||'', id:el.id||'', type:(el.type||el.tagName||'').toLowerCase(),
                   domValue:(el.value||'').slice(0,200)});
    });
    forms.push({id:f.id||'', visible:f.offsetParent!==null,
                h:Math.round(f.getBoundingClientRect().height), fields});
  });
  const ids=Array.from(document.querySelectorAll('[id]')).map(e=>e.id);
  const seen={},dup=[]; ids.forEach(x=>{if(seen[x]){if(!dup.includes(x))dup.push(x);}seen[x]=1;});
  const links=Array.from(document.querySelectorAll('a[href]')).map(a=>({
    h:a.getAttribute('href')||'', t:(a.innerText||'').trim().slice(0,40)}));
  let ls=[],ss=[];
  try{ls=Object.entries(localStorage).map(([k,v])=>({k,v:String(v).slice(0,200)}));}catch(e){}
  try{ss=Object.entries(sessionStorage).map(([k,v])=>({k,v:String(v).slice(0,200)}));}catch(e){}
  return {forms, formCount:forms.length, duplicateIds:dup, duplicateIdCount:dup.length,
          totalIds:ids.length,
          canonical:(document.querySelector('link[rel=canonical]')||{}).href||null,
          robots:(document.querySelector('meta[name=robots]')||{}).content||null,
          title:document.title,
          h1:Array.from(document.querySelectorAll('h1')).map(x=>x.innerText.trim()).slice(0,3),
          h2:Array.from(document.querySelectorAll('h2')).map(x=>x.innerText.trim()).slice(0,12),
          tels:Array.from(document.querySelectorAll("a[href^='tel:']")).map(a=>({
            href:a.getAttribute('href'), txt:(a.innerText||'').trim().slice(0,40),
            visible:!!(a.offsetWidth||a.offsetHeight)})),
          privacy:links.filter(l=>/privacy/i.test(l.h+l.t)).map(l=>l.h).slice(0,3),
          terms:links.filter(l=>/terms|conditions/i.test(l.h+l.t)).map(l=>l.h).slice(0,3),
          cookies:document.cookie.split('; ').filter(Boolean).map(c=>{
            const i=c.indexOf('='); return {k:c.slice(0,i), v:c.slice(i+1,i+201)};}),
          localStorage:ls, sessionStorage:ss,
          dataLayerLen:(window.dataLayer||[]).length,
          overflow:document.documentElement.scrollWidth>window.innerWidth+2,
          bodyText:(document.body?document.body.innerText:'').slice(0,20000)};
}
"""


def probe(pw, key, url, profile, params, marker):
    br = pw.chromium.launch()
    ctx = br.new_context(user_agent=UA_D if profile == "desktop" else UA_M,
                         viewport={"width": 1440, "height": 900} if profile == "desktop"
                         else {"width": 390, "height": 844},
                         is_mobile=(profile == "mobile"), locale="en-US")
    pg = ctx.new_page()
    net, console = [], []
    pg.on("request", lambda r: net.append(r.url))
    pg.on("console", lambda m: console.append(m.type))
    final = {}
    pg.on("response", lambda r: final.__setitem__("r", r)
          if r.url.split("?")[0].rstrip("/") == url.rstrip("/") and r.status == 200 else None)
    rec = {"page": key, "url": url + params, "profile": profile, "marker": marker}
    try:
        resp = pg.goto(url + params, wait_until="domcontentloaded", timeout=90000)
        rec["initial_status"] = resp.status if resp else None
        chain = []
        rr = resp.request.redirected_from if resp else None
        while rr is not None:
            chain.append(rr.url); rr = rr.redirected_from
        rec["redirect_chain"] = list(reversed(chain))
        for _ in range(12):
            pg.wait_for_timeout(2000)
            try:
                s = pg.evaluate("() => ({l: document.body?document.body.innerText.length:0})")
            except Exception:
                continue
            if s["l"] > 800:
                break
        pg.wait_for_timeout(9000)
        d = None
        for _ in range(3):
            try:
                d = pg.evaluate(JS); break
            except Exception:
                pg.wait_for_timeout(2500)
        d = d or {}
        fr = final.get("r")
        hd = {k.lower(): v for k, v in (fr.headers if fr else (resp.headers if resp else {})).items()}
        rec["http_status"] = fr.status if fr else (resp.status if resp else None)
        rec["final_url"] = pg.url
        rec["cache_headers"] = {k: v for k, v in hd.items()
                                if "cache" in k or k in ("age", "vary", "server",
                                                         "host-header", "x-nitro-cache",
                                                         "sg-captcha")}
        rec["x_proxy_cache"] = hd.get("x-proxy-cache")
        try:
            srv = fr.text() if fr else ""
        except Exception:
            srv = ""
        rec["server_html_bytes"] = len(srv)
        rec["server_html_marker_found"] = marker in srv if marker else None
        rec["canonical"] = d.get("canonical")
        rec["canonical_matches_url"] = (str(d.get("canonical") or "").rstrip("/")
                                        == url.rstrip("/"))
        rec["robots"] = d.get("robots")
        rec["title"] = d.get("title"); rec["h1"] = d.get("h1"); rec["h2"] = d.get("h2")
        rec["form_count"] = d.get("formCount")
        rec["form_ids"] = [f["id"] for f in d.get("forms", [])]
        rec["duplicate_id_count"] = d.get("duplicateIdCount")
        rec["duplicate_ids"] = d.get("duplicateIds", [])[:30]
        rec["privacy_links"] = d.get("privacy"); rec["terms_links"] = d.get("terms")
        rec["tels"] = d.get("tels")
        digits = {re.sub(r"\D", "", t["href"] or "") for t in d.get("tels", [])}
        rec["tel_digits"] = sorted(digits)
        rec["paid_number_present"] = any(PAID in x for x in digits)
        rec["mixed_number_present"] = any(MIXED in x for x in digits)
        rec["main_number_present"] = any(MAIN in x for x in digits)
        blob = "\n".join(net) + "\n" + (srv or "")
        rec["gtm"] = GTM in blob
        rec["aw"] = AW in blob or "11155434808" in blob
        rec["ga4"] = GA4 in blob
        rec["whatconverts"] = bool(re.search(r"whatconverts|wc_visitor|iyzt", blob, re.I))
        rec["wc_cookie"] = next((c["v"][:40] for c in d.get("cookies", [])
                                 if c["k"] == "wc_visitor"), None)
        rec["all_gtm_ids"] = sorted(set(re.findall(r"GTM-[A-Z0-9]{5,9}", blob)))
        rec["all_aw_ids"] = sorted(set(re.findall(r"AW-\d{9,12}", blob)))
        rec["all_ga4_ids"] = sorted(set(re.findall(r"G-[A-Z0-9]{8,12}", blob)))
        rec["dataLayer_len"] = d.get("dataLayerLen")
        rec["overflow"] = d.get("overflow")
        # attribution capture
        hid = {}
        for f in d.get("forms", []):
            for fl in f["fields"]:
                if fl["type"] == "hidden" and fl["domValue"].strip():
                    hid.setdefault(fl["name"] or fl["id"], set()).add(fl["domValue"])
        rec["populated_hidden"] = {k: sorted(v) for k, v in hid.items()}
        j = json.dumps(rec["populated_hidden"]) + json.dumps(d.get("cookies", [])) \
            + json.dumps(d.get("localStorage", [])) + json.dumps(d.get("sessionStorage", []))
        rec["marker_in_form"] = bool(marker) and marker in json.dumps(rec["populated_hidden"])
        rec["marker_in_storage"] = bool(marker) and marker in j
        body = d.get("bodyText", "")
        rec["barred_claims"] = {k: re.findall(p, body, re.I)[:2]
                                for k, p in BARRED.items() if re.search(p, body, re.I)}
        rec["console_errors"] = console.count("error")
        EVID.mkdir(parents=True, exist_ok=True)
        if profile == "desktop" and params:
            pg.screenshot(path=str(EVID / f"{key}-paid-session.png"))
    except Exception as ex:
        rec["error"] = f"{type(ex).__name__}: {str(ex)[:200]}"
    finally:
        ctx.close(); br.close()
    return rec


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "mode": "READ + QA", "forms_submitted": 0, "tel_activated": 0,
           "website_changes": 0, "results": []}
    print("=== MAIN-WEBSITE URL + TRACKING QA ===\n")
    with sync_playwright() as pw:
        for key, url in URLS.items():
            mk = f"QA-HEAT-{key.upper().replace('-','')}-{TS}"
            qp = (f"?gclid={mk}-GCLID&gbraid={mk}-GBRAID&wbraid={mk}-WBRAID"
                  f"&utm_source=google&utm_medium=cpc&utm_campaign={mk}-CAMP"
                  f"&utm_term={mk}-TERM&utm_content={mk}-CONT")
            r = probe(pw, key, url, "desktop", qp, mk)
            out["results"].append(r)
            print(f"{key:28s} HTTP {str(r.get('http_status')):4s} "
                  f"cache={str(r.get('x_proxy_cache')):5s} "
                  f"canon_ok={r.get('canonical_matches_url')} "
                  f"forms={r.get('form_count')} dupIDs={r.get('duplicate_id_count')} "
                  f"GTM={r.get('gtm')} AW={r.get('aw')} WC={r.get('whatconverts')}")
            print(f"    H1: {r.get('h1')}")
            print(f"    tel: {r.get('tel_digits')}  paid={r.get('paid_number_present')} "
                  f"mixed={r.get('mixed_number_present')} main={r.get('main_number_present')}")
            print(f"    privacy={bool(r.get('privacy_links'))} terms={bool(r.get('terms_links'))}"
                  f"  marker_in_form={r.get('marker_in_form')} "
                  f"marker_in_storage={r.get('marker_in_storage')}")
            print(f"    populated hidden: {json.dumps(r.get('populated_hidden'))[:160]}")
            print(f"    barred claims: {list((r.get('barred_claims') or {}).keys())}")
            time.sleep(3)
            rm = probe(pw, key, url, "mobile", qp, mk)
            out["results"].append(rm)
            print(f"    [mobile] HTTP {rm.get('http_status')} overflow={rm.get('overflow')} "
                  f"forms={rm.get('form_count')} tel={rm.get('tel_digits')}")
            print()
            time.sleep(3)
    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"heating-url-qa-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {p}")
    print("FORMS SUBMITTED: 0 | TEL ACTIVATED: 0 | WEBSITE CHANGES: 0")


if __name__ == "__main__":
    sys.exit(main())
