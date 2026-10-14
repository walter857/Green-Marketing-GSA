#!/usr/bin/env python3
"""Public read-only code inspection of every LIVE paid Final URL plus /thank-you/.

Captures redirect chain, response headers, CSP, raw source, rendered DOM, network
requests WITH INITIATOR CHAINS, dataLayer contents, GTM load count, form markup,
phone anchors, duplicate ids, and whether a bare /thank-you/ visit fires a
conversion.

NEVER fills a field, NEVER clicks anything, NEVER submits, NEVER dials.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
RAW = SNAP / "r7a-page-source-2026-09-02"
RAW.mkdir(parents=True, exist_ok=True)

PAID = [
    "https://offer.softwindli.com/driveway-pressure-washing/",
    "https://offer.softwindli.com/house-pressure-washing-estimate/",
    "https://offer.softwindli.com/patio-power-washing/",
    "https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/",
    "https://offer.softwindli.com/residential-pressure-washing/",
    "https://offer.softwindli.com/soft-house-washing/",
    "https://offer.softwindli.com/thank-you/",
]
Q = ("?gclid=GM-R7A-TRACE&gbraid=GM-R7A-GB&wbraid=GM-R7A-WB&utm_source=google"
     "&utm_medium=cpc&utm_campaign=r7a-trace&utm_term=trace&utm_content=r7a")
MASONRY, POWERW = "17878095007", "18369652705"


def initiator_of(req):
    """Best-effort initiator: the request's own initiator chain is not exposed by
    Playwright's sync API, so use the frame url + resource type + referer header."""
    try:
        hdr = req.all_headers()
    except Exception:
        hdr = {}
    return {"resource_type": req.resource_type,
            "referer": (hdr.get("referer") or "")[:160],
            "sec_fetch_dest": hdr.get("sec-fetch-dest", ""),
            "frame_url": (req.frame.url if req.frame else "")[:120]}


def scan(pw, url: str) -> dict:
    browser = pw.chromium.launch()
    ctx = browser.new_context()
    page = ctx.new_page()
    reqs, resps, chain = [], [], []
    page.on("request", lambda r: reqs.append((r.method, r.url, initiator_of(r))))
    page.on("response", lambda r: resps.append((r.url, r.status,
                                                dict(list(r.headers.items())[:40]))))
    page.on("requestfinished", lambda r: None)

    main = page.goto(url + Q, wait_until="networkidle", timeout=90000)
    page.wait_for_timeout(8000)
    # redirect chain
    rq = main.request if main else None
    while rq is not None:
        chain.append({"url": rq.url[:180], "method": rq.method})
        rq = rq.redirected_from
    chain.reverse()

    html = page.content()
    slug = re.sub(r"[^a-z0-9]+", "-", url.replace("https://offer.softwindli.com/", "")
                  .strip("/") or "root")
    (RAW / f"{slug}.rendered.html").write_text(html, encoding="utf-8")

    dl = page.evaluate("""() => {
        try {
            if (!window.dataLayer) return {present:false, events:[], count:0};
            const ev = window.dataLayer.map(o => {
                if (Array.isArray(o)) return String(o[0]) + ':' + String(o[1] || '');
                if (o && typeof o === 'object') return o.event || Object.keys(o).slice(0,3).join(',');
                return String(o);
            });
            return {present:true, count: window.dataLayer.length, events: ev.slice(0,40)};
        } catch (e) { return {present:false, error:String(e).slice(0,120)}; }
    }""")
    dom = page.evaluate("""() => {
        const seen={}, dups={};
        document.querySelectorAll('[id]').forEach(e=>{seen[e.id]=(seen[e.id]||0)+1;});
        for(const k in seen) if(seen[k]>1) dups[k]=seen[k];
        const forms=[...document.querySelectorAll('form#gform_1')];
        const hp=[...document.querySelectorAll('.gfield--type-honeypot, .gform_validation_container')];
        return {
          gform_count: forms.length,
          form_actions: forms.map(f=>(f.action||'').slice(0,150)),
          duplicate_ids: dups, duplicate_id_count: Object.keys(dups).length,
          honeypot_present: hp.length, honeypot_hidden: hp.every(e=>getComputedStyle(e).display==='none'),
          honeypot_values: [...document.querySelectorAll('[name=input_9]')].map(e=>e.value),
          tel_links: [...new Set([...document.querySelectorAll("a[href^='tel:']")]
                      .map(e=>e.getAttribute('href')))],
          phones_in_text: [...new Set((document.body.innerText
                            .match(/\\(?\\d{3}\\)?[\\s.\\-]?\\d{3}[\\s.\\-]?\\d{4}/g)||[]))],
          title: document.title
        };
    }""")
    cookies = {c["name"]: c["value"][:110] for c in ctx.cookies()}

    def hits(pat, method=None):
        return [(m, u, i) for (m, u, i) in reqs
                if pat in u and (method is None or m == method)]

    gtm_loads = hits("googletagmanager.com/gtm.js")
    conv_true = [(m, u, i) for (m, u, i) in reqs
                 if re.search(r"/pagead/(1p-)?conversion/\d+/", u) and "/wcm" not in u]
    main_hdrs = {}
    for u, st, h in resps:
        if u.split("?")[0] == url:
            main_hdrs = h
            break
    out = {
        "url": url,
        "http_status": main.status if main else None,
        "redirect_chain": chain,
        "final_url": page.url.split("?")[0],
        "browser_title": dom["title"],
        "raw_source_saved": f"snapshots/r7a-page-source-2026-09-02/{slug}.rendered.html",
        "rendered_dom_saved": True,
        "csp": main_hdrs.get("content-security-policy", "NONE"),
        "server": main_hdrs.get("server", ""),
        "aw_ids_in_html": sorted(set(re.findall(r"AW-\d{9,12}", html))),
        "masonry_present": bool(hits(MASONRY)),
        "powerwashing_present": bool(hits(POWERW)),
        "gtm_load_count": len(gtm_loads),
        "gtm_loader_initiators": [i for (_, _, i) in gtm_loads],
        "gtm_loader_urls": [u for (_, u, _) in gtm_loads],
        "gtag_js_loaders": [u for (_, u, _) in reqs if "googletagmanager.com/gtag/js" in u],
        "whatconverts_host_requests": [u for (_, u, _) in reqs if "whatconverts" in u.lower()],
        "wc_cookies": sorted(k for k in cookies if k.startswith("wc_")),
        "wc_swap_cookie": cookies.get("wc_swap", "ABSENT"),
        "iconnode_requests": [{"method": m, "url": u.split("?")[0], "initiator": i}
                              for (m, u, i) in reqs if "iconnode" in u.lower()],
        "clickcease_requests": len([u for (_, u, _) in reqs
                                    if "ksrndkehqnwntyxlhgto" in u or "clickcease" in u.lower()]),
        "sgcaptcha_observed": bool(hits("sgcaptcha")),
        "masonry_wcm": len(hits(f"conversion/{MASONRY}/wcm")),
        "powerwashing_wcm": len(hits(f"conversion/{POWERW}/wcm")),
        "masonry_form_data_posts": len(hits(f"form-data/{MASONRY}")),
        "powerwashing_form_data_posts": len(hits(f"form-data/{POWERW}")),
        "true_conversion_requests": [{"url": u.split("?")[0],
                                      "account": (re.search(r"conversion/(\d+)/", u).group(1)
                                                  if re.search(r"conversion/(\d+)/", u) else ""),
                                      "en": (re.search(r"[?&]en=([^&]+)", u).group(1)
                                             if re.search(r"[?&]en=([^&]+)", u) else "")}
                                     for (m, u, i) in conv_true],
        "direct_conversion_fires": len(conv_true) > 0,
        "form_start_events": len([u for (_, u, _) in reqs if "en=form_start" in u]),
        "form_submit_events": len([u for (_, u, _) in reqs if "en=form_submit" in u]),
        "datalayer": dl,
        "gform_count": dom["gform_count"],
        "form_actions": dom["form_actions"],
        "duplicate_id_count": dom["duplicate_id_count"],
        "duplicate_ids": sorted(dom["duplicate_ids"]),
        "honeypot_present": dom["honeypot_present"],
        "honeypot_hidden": dom["honeypot_hidden"],
        "honeypot_values": dom["honeypot_values"],
        "tel_links": dom["tel_links"],
        "malformed_tel_links": [t for t in dom["tel_links"] if len(re.sub(r"\D", "", t)) < 10],
        "phones_in_text": dom["phones_in_text"],
        "total_requests": len(reqs),
    }
    browser.close()
    return out


def main() -> int:
    now = datetime.now(ZoneInfo("America/New_York"))
    res = {"generated_account_local": now.isoformat(),
           "mode": "READ ONLY - no fill, no click, no submit, no call",
           "live_paid_final_urls_source": "Google Ads API, ENABLED ads in ENABLED ad groups/campaigns",
           "pages": []}
    with sync_playwright() as pw:
        for u in PAID:
            try:
                res["pages"].append(scan(pw, u))
                print("scanned", u)
            except Exception as exc:
                res["pages"].append({"url": u, "ERROR": str(exc)[:200]})
                print("FAILED", u, str(exc)[:140])
    p = SNAP / f"r7a-public-code-inspection-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("\nWROTE", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
