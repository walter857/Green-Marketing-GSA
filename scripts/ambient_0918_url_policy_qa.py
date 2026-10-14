#!/usr/bin/env python3
"""Ambient | 2026-09-18 | Step 4: QA all nine expansion destinations.

READ-ONLY. No parameters are sent (so no cache-poisoning risk), no form is submitted,
no telephone link activated, no CAPTCHA bypassed, nothing changed.

Per destination: desktop + mobile render, AdsBot fetch, tracking stack, phone behaviour,
form/DOM integrity, policy/legal links, claim scan.
"""
from __future__ import annotations
import sys, re, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-20"
DEST = {
    "Furnace Repair": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "Mini Split Installation": "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/",
    "Gas Boiler Repair": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "Boiler Repair": "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/",
    "Oil Furnace Installation": "https://ambientcoolingandheating.com/services/heating-services/oil-furnace-installations/",
    "Oil Heating System Replacement": "https://ambientcoolingandheating.com/services/heating-services/oil-replacement/",
    "Heat Pump Installation": "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/",
    "Tankless Water Heater Installation": "https://ambientcoolingandheating.com/services/heating-services/tankless-water-heaters/",
    "Geothermal HVAC Installation": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
}
GTM_ID, GA4_ID, AW_ID = "GTM-PQTPQ436", "G-9X9ZHNCRWF", "11155434808"
WANT_PHONE = "4107610932"      # main business number - must be the one on the page
BAD_PHONE = "4109141456"       # must never render or be clickable
ADS_PHONE = "4107056354"       # Google Ads call asset only - must NOT be on the page
ADSBOT_UA = ("AdsBot-Google (+http://www.google.com/adsbot.html)")

# Claims that may not appear unless separately verified and recorded in client.yaml.
CLAIMS = {
    "same_day": re.compile(r"\bsame[- ]day\b", re.I),
    "emergency_availability": re.compile(r"\b(24/7|24-7|round[- ]the[- ]clock|emergency service available)\b", re.I),
    "guarantee": re.compile(r"\b(guarantee[ds]?|guaranteed results)\b", re.I),
    "most_trusted": re.compile(r"\bmost trusted\b", re.I),
    "best_or_top": re.compile(r"\b(best|top[- ]rated|#1|number one) (hvac|heating|provider|company|contractor)\b", re.I),
    "most_knowledgeable": re.compile(r"\bmost knowledgeable\b", re.I),
    "free_estimate": re.compile(r"\bfree (estimate|consultation)\b", re.I),
    "licensed_insured": re.compile(r"\blicen[cs]ed (and|&) insured\b", re.I),
    "rating_or_reviews": re.compile(r"\b\d+(\.\d+)?\s*(star|stars)\b|\b\d{2,}\+?\s*(reviews|ratings)\b", re.I),
}
PLACEHOLDER = re.compile(r"lorem ipsum|\[insert|\{\{|TODO:|FIXME|coming soon|placeholder", re.I)

DEVICES = {
    "desktop": dict(viewport={"width": 1440, "height": 900}),
    "mobile": dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True,
                   user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 "
                              "Mobile/15E148 Safari/604.1"),
}

PROBE = """() => {
  const norm = s => (s||'').replace(/[\\s().\\-+]/g,'');
  const ids = [...document.querySelectorAll('[id]')].map(e=>e.id);
  const dup = {}; ids.forEach(i => dup[i]=(dup[i]||0)+1);
  const tel = [...document.querySelectorAll('a[href^="tel:"]')].map(a=>({
    digits: norm(a.getAttribute('href')), text:(a.innerText||'').trim().slice(0,30),
    visible: !!(a.offsetWidth||a.offsetHeight||a.getClientRects().length)}));
  const forms = [...document.querySelectorAll('form')].map(f=>({
    id: f.id||'', fields: f.querySelectorAll('input,textarea,select').length,
    submit: !!f.querySelector('input[type=submit],button[type=submit],button:not([type])'),
    visible: !!(f.offsetWidth||f.offsetHeight)}));
  const links = [...document.querySelectorAll('a[href]')].map(a=>
    ({href:a.getAttribute('href')||'', text:(a.innerText||'').trim().toLowerCase()}));
  return {
    title: document.title||'',
    h1: [...document.querySelectorAll('h1')].map(e=>e.innerText.trim()).slice(0,3),
    canonical: (document.querySelector('link[rel=canonical]')||{}).href||'',
    robots: (document.querySelector('meta[name=robots]')||{}).content||'',
    url: location.href,
    ids_total: ids.length, ids_unique: new Set(ids).size,
    duplicate_ids: Object.entries(dup).filter(([,n])=>n>1).map(([i,n])=>[i,n]),
    tel, forms, links,
    body_text: (document.body?document.body.innerText:'').slice(0,120000),
    html_has_bad: norm(document.documentElement.outerHTML).includes('4109141456'),
    html_has_want: norm(document.documentElement.outerHTML).includes('4107610932'),
    html_has_ads: norm(document.documentElement.outerHTML).includes('4107056354'),
    gtm: Object.keys(window.google_tag_manager||{}),
    gtag: typeof window.gtag === 'function',
    wc: Object.keys(window).filter(k=>/whatconv|^wc_|^__wc/i.test(k)).slice(0,10),
    scrollW: document.documentElement.scrollWidth,
    clientW: document.documentElement.clientWidth
  };
}"""


def visit(ctx, url):
    net, status, hdrs = [], None, {}
    pg = ctx.new_page()
    pg.on("request", lambda r: net.append(r.url))
    last = None
    for _ in range(4):
        try:
            resp = pg.goto(url, wait_until="domcontentloaded", timeout=70000)
            if resp is not None:
                status = resp.status
                hdrs = {k.lower(): v for k, v in resp.headers.items()}
            pg.wait_for_timeout(3000)
            if pg.evaluate("()=>document.documentElement.outerHTML.length") > 20000:
                break
            pg.wait_for_timeout(3000)
        except Exception as ex:
            last = str(ex)[:160]; pg.wait_for_timeout(1500)
    # NitroPack defers all JS until first interaction
    try:
        pg.mouse.move(420, 300); pg.mouse.wheel(0, 1400)
        pg.keyboard.press("PageDown"); pg.wait_for_timeout(7000)
        pg.mouse.wheel(0, 2500); pg.wait_for_timeout(4000)
    except Exception:
        pass
    d = None
    for _ in range(3):
        try:
            d = pg.evaluate(PROBE); break
        except Exception as ex:
            last = str(ex)[:160]; pg.wait_for_timeout(1500)
    ck = {x["name"]: x["value"] for x in ctx.cookies()} if d else {}
    pg.close()
    return {"status": status, "error": last if d is None else None,
            "headers": {k: v for k, v in hdrs.items()
                        if k in ("x-proxy-cache", "x-nitro-cache", "cache-control",
                                 "host-header", "sg-captcha", "content-type", "location")},
            "net": net, "cookies": ck, "probe": d}


def score(label, url, v):
    p = v["probe"] or {}
    txt = p.get("body_text", "")
    joined = " ".join(v["net"])
    tel = p.get("tel", [])
    telset = {t["digits"].lstrip("tel:").lstrip("1") for t in tel}
    links = p.get("links", [])
    has_priv = any("privacy" in l["text"] or "privacy" in l["href"].lower() for l in links)
    has_terms = any(("terms" in l["text"] or "terms" in l["href"].lower()
                     or "conditions" in l["text"]) for l in links)
    forms = p.get("forms", [])
    claims = {k: bool(rx.search(txt)) for k, rx in CLAIMS.items()}
    return {
        "http_status": v["status"],
        "http_200": v["status"] == 200,
        "captcha_202": v["status"] == 202 or bool(v["headers"].get("sg-captcha")),
        "final_url": p.get("url"),
        "canonical": p.get("canonical"),
        "canonical_matches": (p.get("canonical", "").rstrip("/") == url.rstrip("/")),
        "redirected_offsite": (p.get("url", "").split("?")[0].rstrip("/") != url.rstrip("/")),
        "h1": p.get("h1"),
        "title": p.get("title"),
        "robots": p.get("robots"),
        "ids_total": p.get("ids_total"), "ids_unique": p.get("ids_unique"),
        "duplicate_id_count": len(p.get("duplicate_ids", [])),
        "unique_ids_ok": p.get("ids_total") == p.get("ids_unique"),
        "forms": forms,
        "form_count": len(forms),
        "working_form": any(f["submit"] and f["fields"] >= 3 for f in forms),
        "duplicate_form_ids": len(forms) != len({f["id"] for f in forms}),
        "privacy_link": has_priv, "terms_link": has_terms,
        "mobile_overflow": (p.get("scrollW", 0) - p.get("clientW", 0)) > 4,
        "tel_links": tel, "tel_digits": sorted(telset),
        "phone_bad_present": p.get("html_has_bad"),
        "phone_want_present": p.get("html_has_want"),
        "phone_ads_present": p.get("html_has_ads"),
        "phone_ok": (p.get("html_has_want") and not p.get("html_has_bad")
                     and not p.get("html_has_ads")),
        "gtm": GTM_ID in (p.get("gtm") or []) or "googletagmanager.com/gtm.js" in joined,
        "ga4": GA4_ID in joined or "/g/collect" in joined,
        "aw": AW_ID in joined,
        "whatconverts": bool(p.get("wc")) or "whatconverts" in joined.lower(),
        "wc_visitor": v["cookies"].get("wc_visitor"),
        "wc_swap": v["cookies"].get("wc_swap"),
        "cache": {k: v["headers"].get(k) for k in ("x-proxy-cache", "x-nitro-cache")},
        "unsupported_claims_found": [k for k, hit in claims.items() if hit],
        "placeholder_text": bool(PLACEHOLDER.search(txt)),
    }


def main():
    res = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "parameterised_requests": 0, "forms_submitted": 0,
           "tel_activated": 0, "captcha_bypass_attempted": False, "website_changes": 0,
           "destinations": {}}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for label, url in DEST.items():
            res["destinations"][label] = {"url": url, "devices": {}}
            for dev, cfg in DEVICES.items():
                ctx = b.new_context(locale="en-US", timezone_id="America/New_York", **cfg)
                try:
                    v = visit(ctx, url)
                    s = score(label, url, v)
                    res["destinations"][label]["devices"][dev] = s
                    print(f"{label[:30]:30s} {dev:7s} {s['http_status']} "
                          f"h1={'Y' if s['h1'] else 'N'} dupIDs={s['duplicate_id_count']:3d} "
                          f"form={s['form_count']} phoneOK={s['phone_ok']} "
                          f"GTM={s['gtm']} GA4={s['ga4']} AW={s['aw']} WC={s['whatconverts']} "
                          f"priv={s['privacy_link']} terms={s['terms_link']}")
                except Exception as ex:
                    res["destinations"][label]["devices"][dev] = {"fatal": str(ex)[:250]}
                    print(f"{label[:30]:30s} {dev:7s} FATAL {str(ex)[:90]}")
                finally:
                    ctx.close()
            # --- AdsBot fetch: does Google's crawler get a 202 CAPTCHA stub? ---
            ctx = b.new_context(user_agent=ADSBOT_UA, viewport={"width": 1280, "height": 800})
            pg = ctx.new_page()
            try:
                r = pg.goto(url, wait_until="domcontentloaded", timeout=60000)
                st = r.status if r else None
                hd = {k.lower(): v for k, v in (r.headers if r else {}).items()}
                n = pg.evaluate("()=>document.documentElement.outerHTML.length")
                res["destinations"][label]["adsbot"] = {
                    "status": st, "html_bytes": n,
                    "captcha_stub": st == 202 or n < 5000,
                    "sg_captcha_header": hd.get("sg-captcha"),
                    "x_proxy_cache": hd.get("x-proxy-cache")}
                print(f"{label[:30]:30s} AdsBot  {st}  {n} bytes  "
                      f"{'CAPTCHA STUB' if (st == 202 or n < 5000) else 'full page'}")
            except Exception as ex:
                res["destinations"][label]["adsbot"] = {"error": str(ex)[:200]}
                print(f"{label[:30]:30s} AdsBot  ERROR {str(ex)[:70]}")
            finally:
                ctx.close()
        b.close()
    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"expansion-url-qa-{STAMP}.json"
    p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("PARAMETERISED REQUESTS: 0 | FORMS SUBMITTED: 0 | TEL ACTIVATED: 0 | CHANGES: 0")


if __name__ == "__main__":
    main()
