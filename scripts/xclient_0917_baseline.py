#!/usr/bin/env python3
"""Cross-client attribution baseline inspection | 2026-09-17.

STEP 1 ONLY. Sends NO tracking parameters and therefore cannot seed any cache.
GET navigations only. No form submitted, no tel: activated, nothing modified.

Any real click ID or UTM value found is SHA-256 hashed and truncated - never stored raw.

This step alone can be decisive: on Ambient, a no-parameter request already returned a
previous visitor's GCLID in the server HTML.
"""
from __future__ import annotations
import datetime, hashlib, json, re, sys, time, urllib.request, urllib.error
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "cross-client-attribution"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-17"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
SITES = {
    "BEAVER": "https://offer.beaverbinsin.com/",
    "NOLTE": "https://offer.nolteandsons.com/landscaping-2/",
    "MASTERGRASS": "https://offer.mastergrasslawncare.com/landscaping-contractor/",
}
# value shapes that indicate a REAL click id / campaign value leaked into the page
CLICKID_SHAPE = re.compile(
    r"^(?:Cj0|CjwK|EAIa|Cj[A-Za-z0-9])[A-Za-z0-9_\-]{15,}$")   # typical gclid prefixes
LONGTOKEN = re.compile(r"^[A-Za-z0-9_\-]{20,}$")


def h(v):
    """Hash any potentially real value. Never return the raw string."""
    if not v:
        return None
    return "sha256:" + hashlib.sha256(str(v).encode()).hexdigest()[:16]


def classify(name, val):
    """Is this hidden-field value a leaked real attribution value?"""
    v = (val or "").strip()
    if not v or v in ("0", "1", "postback", "gravity-theme", "[]"):
        return None
    low = v.lower()
    if CLICKID_SHAPE.match(v):
        return "REAL_CLICK_ID_SHAPE"
    if low in ("google", "cpc", "ppc", "paid", "organic", "(direct)", "facebook",
               "bing", "email", "referral"):
        return "generic_source_medium"
    if low.startswith("qa-") or low.startswith("qa0"):
        return "QA_MARKER"
    if LONGTOKEN.match(v) and len(v) >= 24:
        return "OPAQUE_TOKEN_possibly_real"
    return "other_value_present"


JS = """
() => {
  const forms=[];
  document.querySelectorAll('form').forEach((f,i)=>{
    const fields=[];
    f.querySelectorAll('input,textarea,select').forEach(el=>{
      fields.push({name:el.name||'', id:el.id||'',
                   type:(el.type||el.tagName||'').toLowerCase(),
                   domValue:(el.value||'').slice(0,200),
                   attrValue:(el.getAttribute('value')||'').slice(0,200)});
    });
    const st=getComputedStyle(f);
    forms.push({index:i, id:f.id||'', cls:String(f.className||'').slice(0,80),
                action:(f.action||'').slice(0,140), method:f.method||'',
                display:st.display, offsetParent:f.offsetParent!==null,
                rectH:Math.round(f.getBoundingClientRect().height),
                fieldCount:fields.length, fields});
  });
  const ids=Array.from(document.querySelectorAll('[id]')).map(e=>e.id);
  const seen={},dup=[];
  ids.forEach(x=>{if(seen[x]){if(!dup.includes(x))dup.push(x);}seen[x]=1;});
  let ls=[],ss=[];
  try{ls=Object.entries(localStorage).map(([k,v])=>({k,v:String(v).slice(0,160)}));}catch(e){}
  try{ss=Object.entries(sessionStorage).map(([k,v])=>({k,v:String(v).slice(0,160)}));}catch(e){}
  return {forms, formCount:forms.length,
          duplicateIds:dup, duplicateIdCount:dup.length, totalIds:ids.length,
          cookies:document.cookie.split('; ').filter(Boolean).map(c=>{
            const i=c.indexOf('='); return {k:c.slice(0,i), v:c.slice(i+1,i+161)};}),
          localStorage:ls, sessionStorage:ss,
          dataLayerPresent: !!window.dataLayer,
          dataLayerLength:(window.dataLayer||[]).length,
          h1:Array.from(document.querySelectorAll('h1')).map(x=>x.innerText.trim()).slice(0,2),
          title:document.title,
          tels:Array.from(document.querySelectorAll("a[href^='tel:']")).map(a=>({
            href:a.getAttribute('href'), visible:!!(a.offsetWidth||a.offsetHeight)}))};
}
"""


def raw(url):
    try:
        r = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "identity"})
        with urllib.request.urlopen(r, timeout=45) as z:
            hd = {k.lower(): v for k, v in z.headers.items()}
            return z.status, hd, z.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, ""
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {str(e)[:140]}"}, ""


def main():
    res = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "step": "1 - BASELINE INSPECTION ONLY",
           "parameters_sent": "NONE - no gclid/gbraid/wbraid/utm was transmitted",
           "cache_seeding_risk": "none - no parameterised request was made",
           "forms_submitted": 0, "tel_links_activated": 0, "website_changes": 0,
           "pii_policy": "any real-looking click id or token is SHA-256 hashed, never stored raw",
           "sites": {}}

    print("=== STEP 1: BASELINE (NO PARAMETERS SENT) ===\n")
    with sync_playwright() as pw:
        for code, url in SITES.items():
            print(f"########## {code}  {url} ##########")
            st, hd, body = raw(url)
            cache_hdrs = {k: v for k, v in hd.items()
                          if "cache" in k or k in ("age", "vary", "expires", "server",
                                                   "cf-ray", "x-nitro-cache",
                                                   "x-nitropack-cache", "sg-captcha",
                                                   "host-header", "x-powered-by")}
            print(f"  RAW HTTP {st}")
            for k, v in sorted(cache_hdrs.items()):
                print(f"    {k}: {str(v)[:90]}")

            # hidden input values present in the SERVER HTML with no params sent
            srv_hidden = []
            for m in re.finditer(
                    r'<input[^>]*?name=["\']([^"\']+)["\'][^>]*?value=["\']([^"\']*)["\']',
                    body, re.I):
                nm, val = m.group(1), m.group(2)
                c = classify(nm, val)
                if c and c != "generic_source_medium":
                    srv_hidden.append({"field": nm, "classification": c,
                                       "value_hash": h(val), "length": len(val),
                                       "preview": (val[:6] + "…") if len(val) > 6 else val})
                elif c == "generic_source_medium":
                    srv_hidden.append({"field": nm, "classification": c,
                                       "value": val, "length": len(val)})
            print(f"  server HTML: {len(body)} bytes, "
                  f"{len(srv_hidden)} populated input value(s) with NO params sent")
            for x in srv_hidden[:14]:
                print(f"    {x['field']:26s} {x['classification']:28s} "
                      f"{x.get('value', x.get('value_hash'))}")

            br = pw.chromium.launch()
            ctx = br.new_context(user_agent=UA, viewport={"width": 1440, "height": 900},
                                 locale="en-US")
            pg = ctx.new_page()
            net = []
            pg.on("request", lambda r: net.append(r.url))
            try:
                r2 = pg.goto(url, wait_until="domcontentloaded", timeout=90000)
                init = r2.status if r2 else None
                for _ in range(12):
                    pg.wait_for_timeout(2500)
                    try:
                        s2 = pg.evaluate(
                            "() => ({f:document.querySelectorAll('form').length,"
                            " l:document.body?document.body.innerText.length:0})")
                    except Exception:
                        continue
                    if s2["l"] > 500:
                        break
                pg.wait_for_timeout(9000)
                d = pg.evaluate(JS)
            except Exception as ex:
                d = {"error": str(ex)[:200]}
                init = None
            blob = "\n".join(net)
            trackers = {
                "gtm": sorted(set(re.findall(r"GTM-[A-Z0-9]{5,9}", blob + body))),
                "google_ads": sorted(set(re.findall(r"AW-\d{9,12}", blob + body))),
                "ga4": sorted(set(re.findall(r"G-[A-Z0-9]{8,12}", blob + body))),
                "whatconverts": bool(re.search(r"whatconverts|wc_visitor|iyzt",
                                               blob + body, re.I)),
                "hubspot": bool(re.search(r"hs-scripts|hubspot", blob + body, re.I)),
                "callrail": bool(re.search(r"callrail", blob + body, re.I)),
                "gravity_forms": bool(re.search(r"gform|gravityforms", blob + body, re.I)),
                "hubspot_forms": bool(re.search(r"hsforms", blob + body, re.I)),
                "wpforms": bool(re.search(r"wpforms", blob + body, re.I)),
                "elementor_forms": bool(re.search(r"elementor.*form", blob + body, re.I)),
            }
            live_pop = []
            for f in d.get("forms", []):
                for fl in f["fields"]:
                    c = classify(fl["name"], fl["domValue"])
                    if c:
                        live_pop.append({
                            "form": f["id"], "field": fl["name"] or fl["id"],
                            "classification": c,
                            "value": fl["domValue"] if c == "generic_source_medium"
                            else h(fl["domValue"]),
                            "attr_equals_dom": fl["attrValue"] == fl["domValue"]})
            attr_cookies = [c for c in d.get("cookies", [])
                            if re.search(r"gcl|utm|wc_|click|attrib|_ga|source|campaign",
                                         c["k"], re.I)]
            attr_storage = [x for x in (d.get("localStorage", []) +
                                        d.get("sessionStorage", []))
                            if re.search(r"gcl|utm|wc_|click|attrib|source|campaign",
                                         x["k"], re.I)]
            print(f"  browser: init HTTP {init}  title={str(d.get('title'))[:60]!r}")
            print(f"  forms={d.get('formCount')} "
                  f"ids={d.get('totalIds')} duplicateIDs={d.get('duplicateIdCount')}")
            print(f"  form stack: " + ", ".join(k for k, v in trackers.items()
                                                if v and "form" in k) or "  form stack: ?")
            print(f"  trackers: GTM={trackers['gtm']} AW={trackers['google_ads']} "
                  f"GA4={trackers['ga4']} WC={trackers['whatconverts']} "
                  f"CallRail={trackers['callrail']} HubSpot={trackers['hubspot']}")
            print(f"  LIVE DOM populated attribution-ish fields: {len(live_pop)}")
            for x in live_pop[:12]:
                print(f"    {x['field']:26s} {x['classification']:28s} {x['value']}")
            print(f"  attribution cookies: {[c['k'] for c in attr_cookies][:12]}")
            print(f"  attribution storage keys: {[x['k'] for x in attr_storage][:12]}")
            hidden_names = sorted({fl["name"] for f in d.get("forms", [])
                                   for fl in f["fields"] if fl["type"] == "hidden"})
            print(f"  hidden field names: {hidden_names[:18]}")
            has = {k: any(k in n.lower() for n in hidden_names)
                   for k in ("gclid", "gbraid", "wbraid", "utm", "campaign", "keyword")}
            print(f"  field presence: {has}")
            print()

            res["sites"][code] = {
                "url": url, "raw_http_status": st, "cache_headers": cache_hdrs,
                "server_html_bytes": len(body),
                "server_html_populated_inputs": srv_hidden,
                "browser_initial_status": init,
                "title": d.get("title"), "h1": d.get("h1"),
                "form_count": d.get("formCount"),
                "forms": [{"id": f["id"], "cls": f["cls"], "action": f["action"],
                           "method": f["method"], "visible": f["offsetParent"],
                           "height": f["rectH"], "fieldCount": f["fieldCount"],
                           "hidden_fields": sorted({fl["name"] for fl in f["fields"]
                                                    if fl["type"] == "hidden"})}
                          for f in d.get("forms", [])],
                "duplicate_id_count": d.get("duplicateIdCount"),
                "duplicate_ids": d.get("duplicateIds", [])[:40],
                "total_ids": d.get("totalIds"),
                "trackers": trackers,
                "hidden_field_names": hidden_names,
                "attribution_field_presence": has,
                "live_dom_populated": live_pop,
                "attribution_cookies": [{"k": c["k"], "v_hash": h(c["v"])}
                                        for c in attr_cookies],
                "attribution_storage": [{"k": x["k"], "v_hash": h(x["v"])}
                                        for x in attr_storage],
                "dataLayer_present": d.get("dataLayerPresent"),
                "dataLayer_length": d.get("dataLayerLength"),
                "tel_links": d.get("tels"),
                "network_hosts": sorted({re.sub(r"^https?://([^/]+).*", r"\1", u)
                                         for u in net})[:30],
            }
            ctx.close(); br.close()
            time.sleep(3)

    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"baseline-inspection-{STAMP}.json"
    p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {p}")
    print("PARAMETERS SENT: NONE | FORMS SUBMITTED: 0 | WEBSITE CHANGES: 0")


if __name__ == "__main__":
    sys.exit(main())
