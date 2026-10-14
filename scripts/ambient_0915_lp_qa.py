#!/usr/bin/env python3
"""Ambient | 2026-09-15 | real-browser QA of the commercial page + all six paid pages.

GET navigations only. No form is submitted. No tel: link is activated. Nothing on the
site is modified. These pages sit behind SiteGround SG-Captcha, which feeds non-JS
clients an empty stub, so a real JavaScript browser is mandatory.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
TZ = ZoneInfo("America/New_York")
STAMP = "2026-09-15"

BASE = "https://offer.ambientcoolingandheating.com"
COMMERCIAL = f"{BASE}/commercial-hvac-installation/"
PAGES = {
    "Commercial HVAC Installation": COMMERCIAL,
    "AC Repair": f"{BASE}/ac-repair/",
    "HVAC Repair": f"{BASE}/hvac-repair/",
    "HVAC Installation": f"{BASE}/hvac-installation/",
    "HVAC Replacement": f"{BASE}/hvac-replacement/",
    "Gas Boiler Repair": f"{BASE}/gas-boiler-repair/",
}

APPROVED_PAID = "4107056354"     # (410) 705-6354  approved paid display number
WC_POOL = "4109141456"           # (410) 914-1456  mixed-source, must not be static on paid
MAIN_SITE = "4107610932"         # (410) 761-0932  forwarding destination, never public
UNEXPLAINED = "4104159517"
GTM_ID = "GTM-PQTPQ436"
AW_ID = "AW-11155434808"

# Section 8 of the master instruction: intended commercial page elements.
INTENDED = {
    "title": "Commercial HVAC Installation | Ambient Cooling & Heating",
    "meta_description": ("Request commercial HVAC installation or replacement for your "
                         "Central Maryland property from Ambient Cooling & Heating."),
    "h1": "Commercial HVAC Installation in Central Maryland",
    "primary_cta": "Request a Free Commercial HVAC Quote",
    "secondary_cta": "Call (410) 705-6354",
}

BARRED = {
    "24/7 availability": r"\b24\s*/\s*7\b|\btwenty[- ]four seven\b",
    "emergency service": r"\bemergency\b",
    "guaranteed response time": r"guaranteed\s+(response|arrival)|response\s+time\s+guarantee",
    "same-day service": r"\bsame[-\s]day\b",
    "licensed & insured": r"licen[cs]ed\s*(&|and)\s*insured|fully\s+licen[cs]ed|\binsured\b",
    "financing / rebates": r"\bfinanc(e|ing)\b|\brebate|\b0%\s*apr|\bmonthly payments?\b",
    "guaranteed savings": r"guaranteed\s+savings|save\s+guaranteed",
    "#1 claim": r"#\s*1\b|\bnumber one\b|\bbest in\b",
    "ratings / review counts": r"\b\d(\.\d)?\s*star(s)?\b|\b\d{2,}\+?\s*reviews?\b",
    "warranty claim": r"\bwarrant(y|ies)\b",
    "certification claim": r"\bnate[- ]certified\b|\bcertified technician",
    "price claim": r"\$\s?\d",
    "LSA / Google Guaranteed": r"google\s+guaranteed|local\s+services\s+ads",
}

# Services the commercial page may legitimately name (master instruction section 8).
COMMERCIAL_TERMS = {
    "commercial": r"\bcommercial\b",
    "installation": r"\binstall(ation|ed|ing|s)?\b",
    "replacement": r"\breplace(ment|d|s)?\b",
    "rooftop unit": r"\brooftop\b|\bRTU\b",
    "packaged system": r"\bpackaged?\s+(system|unit)",
    "heat pump": r"\bheat pumps?\b",
    "central air": r"\bcentral air\b",
    "ductwork": r"\bduct(work|s)?\b",
    "ventilation": r"\bventilation\b",
    "controls": r"\bcontrols?\b",
    "Central Maryland": r"central maryland",
    "business / property": r"\bbusiness(es)?\b|\bpropert(y|ies)\b|\bbuilding\b",
}
RESIDENTIAL_LEAK = {
    "home/homeowner": r"\bhome ?owner|\byour home\b|\bhouses?\b|\bresidential\b",
}

UA_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 "
             "Safari/604.1")

PHONE_RE = re.compile(r"\(?\b(\d{3})\)?[\s.‑-]?(\d{3})[\s.‑-]?(\d{4})\b")
TRACKERS = {
    "gtm_container": re.compile(r"\bGTM-[A-Z0-9]{5,9}\b"),
    "google_ads_gtag": re.compile(r"\bAW-\d{9,12}\b"),
    "ga4_measurement": re.compile(r"\bG-[A-Z0-9]{8,12}\b"),
    "whatconverts": re.compile(r"whatconverts", re.I),
    "clickcease": re.compile(r"clickcease", re.I),
}
CLICK_PARAMS = ("?gclid=QA0915COMMTEST&utm_source=google&utm_medium=cpc"
                "&utm_campaign=qa-readonly&utm_term=commercial+hvac+installation"
                "&utm_content=qa-readonly-content")


def digits(s):
    return re.sub(r"\D", "", s or "")


def audit(ctx, service, url, profile, with_params):
    page = ctx.new_page()
    net, console, failed = [], [], []
    page.on("request", lambda r: net.append(r.url))
    page.on("console", lambda m: console.append(
        {"type": m.type, "text": m.text[:220]}) if m.type in ("error", "warning") else None)
    page.on("requestfailed", lambda r: failed.append(
        {"url": r.url[:200], "failure": (r.failure or "")[:120]}))

    target = url + (CLICK_PARAMS if with_params else "")
    rec = {"service": service, "requested_url": target, "profile": profile,
           "click_params_sent": with_params}
    try:
        t0 = datetime.datetime.now()
        resp = page.goto(target, wait_until="networkidle", timeout=90000)
        rec["nav_ms"] = int((datetime.datetime.now() - t0).total_seconds() * 1000)
        rec["http_status"] = resp.status if resp else None
        # redirect chain
        chain = []
        r = resp.request.redirected_from if resp else None
        while r is not None:
            chain.append(r.url)
            r = r.redirected_from
        rec["redirect_chain"] = list(reversed(chain))
        rec["final_url"] = page.url
        rec["https"] = page.url.startswith("https://")
        rec["destination_matches_requested"] = (
            page.url.split("?")[0].rstrip("/") == url.rstrip("/"))

        page.wait_for_timeout(4000)
        html = page.content()
        text = page.inner_text("body")
        rec["body_text_len"] = len(text)
        rec["render_ok"] = len(text.strip()) > 400
        rec["soft_404"] = bool(re.search(r"\b(page not found|404|nothing found)\b", text, re.I))

        rec["title"] = page.title()
        md = page.query_selector("meta[name='description']")
        rec["meta_description"] = md.get_attribute("content") if md else None
        rb = page.query_selector("meta[name='robots']")
        rec["meta_robots"] = rb.get_attribute("content") if rb else None
        cn = page.query_selector("link[rel=canonical]")
        rec["canonical"] = cn.get_attribute("href") if cn else None
        vp = page.query_selector("meta[name='viewport']")
        rec["viewport_meta"] = vp.get_attribute("content") if vp else None

        rec["h1"] = [h.inner_text().strip() for h in page.query_selector_all("h1")]
        rec["h2"] = [h.inner_text().strip() for h in page.query_selector_all("h2")]
        rec["h3"] = [h.inner_text().strip() for h in page.query_selector_all("h3")][:20]

        # ---- phones ----
        rec["phones_in_text"] = sorted({"".join(m.groups())
                                        for m in PHONE_RE.finditer(text)})
        rec["phones_in_html"] = sorted({"".join(m.groups())
                                        for m in PHONE_RE.finditer(html)})
        tels = [{"href": a.get_attribute("href"), "text": (a.inner_text() or "").strip()}
                for a in page.query_selector_all("a[href^='tel:']")]
        rec["tel_links"] = tels
        rec["tel_digits"] = sorted({digits(t["href"]) for t in tels})
        rec["approved_number_present"] = APPROVED_PAID in rec["phones_in_text"]
        rec["forwarding_number_leaked_text"] = MAIN_SITE in rec["phones_in_text"]
        rec["forwarding_number_leaked_html"] = MAIN_SITE in rec["phones_in_html"]
        rec["wc_pool_number_present_text"] = WC_POOL in rec["phones_in_text"]
        rec["wc_pool_number_present_html"] = WC_POOL in rec["phones_in_html"]
        rec["unexplained_number_present"] = UNEXPLAINED in rec["phones_in_html"]
        rec["unapproved_numbers_in_text"] = [p for p in rec["phones_in_text"]
                                             if p != APPROVED_PAID and len(p) == 10]

        # ---- trackers ----
        blob = html + "\n" + "\n".join(net)
        rec["trackers"] = {}
        for k, v in TRACKERS.items():
            rec["trackers"][k] = (sorted(set(v.findall(blob)))[:6]
                                  if k in ("gtm_container", "google_ads_gtag",
                                           "ga4_measurement") else bool(v.search(blob)))
        rec["gtm_expected_present"] = GTM_ID in blob
        rec["aw_expected_present"] = AW_ID in blob
        rec["network_hosts"] = sorted({re.sub(r"^https?://([^/]+).*", r"\1", u)
                                       for u in net})

        # ---- storage / DNI evidence ----
        try:
            store = page.evaluate(
                "() => ({ls: Object.keys(localStorage||{}).slice(0,50),"
                " ss: Object.keys(sessionStorage||{}).slice(0,50),"
                " cookies: document.cookie.split('; ').map(c=>c.split('=')[0]).slice(0,80)})")
        except Exception as ex:  # noqa: BLE001
            store = {"ls": [], "ss": [], "cookies": [], "error": str(ex)[:120]}
        rec["storage_keys"] = store
        rec["wc_swap_cookie"] = [c for c in store.get("cookies", []) if "wc_" in c]
        try:
            rec["wc_swap_value"] = page.evaluate(
                "() => (document.cookie.split('; ').find(c=>c.startsWith('wc_swap'))||'')"
                ".slice(0,300)")
        except Exception:  # noqa: BLE001
            rec["wc_swap_value"] = None
        rec["click_id_in_storage"] = bool(page.evaluate(
            "() => JSON.stringify({l:localStorage,s:sessionStorage,c:document.cookie})"
            ".includes('QA0915COMMTEST')")) if with_params else None

        # ---- forms ----
        forms = []
        for f in page.query_selector_all("form"):
            fields = []
            for el in f.query_selector_all("input, textarea, select"):
                fields.append({
                    "name": el.get_attribute("name") or "",
                    "id": el.get_attribute("id") or "",
                    "type": el.get_attribute("type") or el.evaluate("e=>e.tagName"),
                    "required": el.get_attribute("required") is not None
                    or "gfield_contains_required" in (el.get_attribute("class") or ""),
                    "hidden_value": (el.get_attribute("value") or "")[:140]
                    if (el.get_attribute("type") or "") == "hidden" else None,
                    "aria_label": el.get_attribute("aria-label"),
                    "visible": el.is_visible(),
                })
            labels = [(l.get_attribute("for"), (l.inner_text() or "").strip()[:60])
                      for l in f.query_selector_all("label")]
            forms.append({"id": f.get_attribute("id") or "",
                          "action": f.get_attribute("action") or "",
                          "method": f.get_attribute("method") or "",
                          "field_count": len(fields),
                          "visible": f.is_visible(),
                          "labels": labels[:20], "fields": fields[:40]})
        rec["forms"] = forms
        rec["form_count"] = len(forms)
        rec["visible_form_count"] = sum(1 for f in forms if f["visible"])
        rec["hidden_form_count"] = sum(1 for f in forms if not f["visible"])

        hidden_all = []
        for f in forms:
            for fl in f["fields"]:
                if fl["type"] == "hidden":
                    hidden_all.append({"form": f["id"], "name": fl["name"],
                                       "value": fl["hidden_value"]})
        rec["hidden_fields"] = hidden_all
        if with_params:
            j = json.dumps(hidden_all)
            rec["gclid_captured_in_form"] = "QA0915COMMTEST" in j
            rec["utm_campaign_captured"] = "qa-readonly" in j
            rec["utm_content_captured"] = "qa-readonly-content" in j
            rec["utm_term_captured"] = "commercial" in j

        # ---- duplicate DOM ids / duplicate form ids ----
        ids = page.evaluate(
            "() => Array.from(document.querySelectorAll('[id]')).map(e=>e.id)")
        seen, dup = set(), []
        for i in ids:
            if i in seen and i not in dup:
                dup.append(i)
            seen.add(i)
        rec["duplicate_dom_ids"] = dup[:40]
        rec["duplicate_dom_id_count"] = len(dup)
        fids = [f["id"] for f in forms if f["id"]]
        rec["duplicate_form_ids"] = sorted({x for x in fids if fids.count(x) > 1})

        # ---- links ----
        links = [(a.get_attribute("href") or "", (a.inner_text() or "").strip())
                 for a in page.query_selector_all("a[href]")]
        rec["privacy_link"] = [h for h, t in links
                               if re.search(r"privacy", h + " " + t, re.I)][:4]
        rec["terms_link"] = [h for h, t in links
                             if re.search(r"terms|conditions", h + " " + t, re.I)][:4]
        rec["anchor_targets"] = sorted({h for h, _ in links if h.startswith("#")})[:25]
        rec["outbound_links"] = sorted({h for h, _ in links
                                        if h.startswith("http")
                                        and "ambientcoolingandheating" not in h})[:15]

        # ---- images ----
        imgs = page.evaluate(
            "() => Array.from(document.images).map(i => ({src:i.currentSrc||i.src,"
            " w:i.naturalWidth, h:i.naturalHeight, alt:i.alt||''}))")
        rec["image_count"] = len(imgs)
        rec["broken_images"] = [i["src"][:160] for i in imgs if i["w"] == 0][:15]
        rec["images_missing_alt"] = sum(1 for i in imgs if not i["alt"].strip())

        # ---- claims / relevance ----
        rec["barred_claims_found"] = {k: re.findall(p, text, re.I)[:3]
                                      for k, p in BARRED.items()
                                      if re.search(p, text, re.I)}
        rec["commercial_terms_present"] = {k: bool(re.search(p, text, re.I))
                                           for k, p in COMMERCIAL_TERMS.items()}
        rec["residential_leak"] = {k: re.findall(p, text, re.I)[:5]
                                   for k, p in RESIDENTIAL_LEAK.items()
                                   if re.search(p, text, re.I)}

        # ---- layout ----
        rec["horizontal_overflow"] = page.evaluate(
            "() => document.documentElement.scrollWidth > window.innerWidth + 2")
        rec["viewport"] = page.viewport_size
        if profile == "mobile":
            rec["sticky_elements"] = page.evaluate(
                "() => Array.from(document.querySelectorAll('*')).filter(e=>{"
                "const s=getComputedStyle(e);"
                "return (s.position==='fixed'||s.position==='sticky') && e.offsetHeight>0;"
                "}).slice(0,12).map(e=>({tag:e.tagName, cls:(e.className||'').toString()"
                ".slice(0,70), txt:(e.innerText||'').slice(0,70)}))")
            rec["sticky_has_call"] = any(
                "tel:" in (page.evaluate(
                    "e => e.innerHTML", el) or "")
                for el in page.query_selector_all(
                    "[style*='fixed'], .et_pb_sticky, [class*='sticky'], [class*='fixed']")[:20]
            ) if page.query_selector_all("[class*='sticky'], [class*='fixed']") else False

        # ---- structured data ----
        sd = []
        for s in page.query_selector_all("script[type='application/ld+json']"):
            sd.append((s.inner_text() or "")[:1200])
        rec["structured_data_blocks"] = len(sd)
        rec["structured_data_phones"] = sorted({"".join(m.groups())
                                                for b in sd
                                                for m in PHONE_RE.finditer(b)})

        rec["console_errors"] = [c for c in console if c["type"] == "error"][:20]
        rec["console_error_count"] = sum(1 for c in console if c["type"] == "error")
        rec["failed_requests"] = failed[:20]
    except Exception as exc:  # noqa: BLE001
        rec["error"] = str(exc)[:500]
    finally:
        page.close()
    return rec


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "method": "playwright chromium, JS on, GET only, no form submitted, "
                     "no tel: activated", "results": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for profile, vp, ua in (("desktop", {"width": 1440, "height": 900}, UA_DESKTOP),
                                ("mobile", {"width": 390, "height": 844}, UA_MOBILE)):
            ctx = browser.new_context(viewport=vp, user_agent=ua,
                                      is_mobile=(profile == "mobile"),
                                      has_touch=(profile == "mobile"),
                                      locale="en-US")
            # commercial page gets both a clean and a paid-parameter render
            out["results"].append(audit(ctx, "Commercial HVAC Installation",
                                        COMMERCIAL, profile, False))
            out["results"].append(audit(ctx, "Commercial HVAC Installation",
                                        COMMERCIAL, profile, True))
            for svc, url in PAGES.items():
                if svc == "Commercial HVAC Installation":
                    continue
                out["results"].append(audit(ctx, svc, url, profile, True))
            ctx.close()
        # DNI repeat-render probe: 3 consecutive loads in one fresh context
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  user_agent=UA_DESKTOP, locale="en-US")
        probes = []
        for i in range(3):
            p = ctx.new_page()
            p.goto(COMMERCIAL + CLICK_PARAMS, wait_until="networkidle", timeout=90000)
            p.wait_for_timeout(4500)
            t = p.inner_text("body")
            probes.append({
                "render": i + 1,
                "phones_in_text": sorted({"".join(m.groups())
                                          for m in PHONE_RE.finditer(t)}),
                "tel_digits": sorted({digits(a.get_attribute("href"))
                                      for a in p.query_selector_all("a[href^='tel:']")}),
                "wc_cookie": p.evaluate(
                    "() => (document.cookie.split('; ').find(c=>c.startsWith('wc_'))||'')"
                    ".slice(0,200)"),
            })
            p.close()
        out["dni_repeat_probe"] = probes
        ctx.close()
        browser.close()

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"lp-browser-qa-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {p}")
    print(f"results: {len(out['results'])}")
    for r in out["results"]:
        if r["service"] != "Commercial HVAC Installation":
            continue
        print(f"\n--- {r['profile']} params={r['click_params_sent']} ---")
        print(f"  http={r.get('http_status')} final={r.get('final_url')}")
        print(f"  title={r.get('title')!r}")
        print(f"  h1={r.get('h1')}")
        print(f"  approved_number={r.get('approved_number_present')} "
              f"fwd_leak_text={r.get('forwarding_number_leaked_text')} "
              f"fwd_leak_html={r.get('forwarding_number_leaked_html')} "
              f"wc_pool_text={r.get('wc_pool_number_present_text')}")
        print(f"  tel_digits={r.get('tel_digits')}  phones={r.get('phones_in_text')}")
        print(f"  privacy={r.get('privacy_link')} terms={r.get('terms_link')}")
        print(f"  forms={r.get('form_count')} visible={r.get('visible_form_count')} "
              f"hidden={r.get('hidden_form_count')} dupids={r.get('duplicate_dom_id_count')}")
        print(f"  barred={list((r.get('barred_claims_found') or {}).keys())}")
        print(f"  gclid_in_form={r.get('gclid_captured_in_form')}")
        print(f"  error={r.get('error')}")
    print("\nDNI repeat probe:")
    for p_ in out["dni_repeat_probe"]:
        print(" ", p_)


if __name__ == "__main__":
    sys.exit(main())
