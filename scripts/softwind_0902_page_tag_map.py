#!/usr/bin/env python3
"""Page-by-page tag / form / phone map for the Softwind paid landing pages.

READ ONLY. Loads each page in instrumented Chromium with network capture.
NEVER fills a field, NEVER clicks submit, NEVER places a call.
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
BASE = "https://offer.softwindli.com"

PAGES = [
    f"{BASE}/power-washing-services-islip-west-islip-dix-hills/",
    f"{BASE}/residential-pressure-washing/",
    f"{BASE}/house-washing-company/",
    f"{BASE}/soft-house-washing/",
    f"{BASE}/driveway-pressure-washing/",
    f"{BASE}/patio-power-washing/",
    f"{BASE}/thank-you/",
]
Q = ("?gclid=GM-TRACE-GCLID&gbraid=GM-TRACE-GBRAID&wbraid=GM-TRACE-WBRAID"
     "&utm_source=google&utm_medium=cpc&utm_campaign=gm-trace&utm_term=trace&utm_content=r7a")

MASONRY = "17878095007"   # conversion tracking id of Softwind Landscape & Masonry (2429758629)
POWERW = "18369652705"    # conversion tracking id of Softwind Power Washing (1521725229)


def scan(pw, url: str) -> dict:
    browser = pw.chromium.launch()
    ctx = browser.new_context()
    page = ctx.new_page()
    reqs: list[str] = []
    page.on("request", lambda r: reqs.append(r.url))
    resp = page.goto(url + Q, wait_until="networkidle", timeout=90000)
    page.wait_for_timeout(7000)
    html = page.content()

    def any_req(pat):
        return [u for u in reqs if pat in u]

    dom = page.evaluate("""() => {
        const forms = [...document.querySelectorAll('form#gform_1')];
        const seen = {}, dups = {};
        document.querySelectorAll('[id]').forEach(e => { seen[e.id] = (seen[e.id] || 0) + 1; });
        for (const k in seen) if (seen[k] > 1) dups[k] = seen[k];
        const tels = [...document.querySelectorAll("a[href^='tel:']")]
                       .map(e => e.getAttribute('href'));
        const body = document.body.innerText;
        const phones = [...new Set((body.match(/\\(?\\d{3}\\)?[\\s.\\-]?\\d{3}[\\s.\\-]?\\d{4}/g)
                        || []))];
        // how is gtag injected? look for inline config lines
        const inline = [...document.querySelectorAll('script:not([src])')]
            .map(s => s.textContent || '')
            .filter(t => t.includes('AW-') || t.includes('phone_conversion_number'))
            .map(t => t.slice(0, 400));
        const srcs = [...document.querySelectorAll('script[src]')]
            .map(s => s.src).filter(s => /gtm|gtag|googletagmanager|whatconverts|wc|iconnode/i
                                          .test(s));
        return { form_count: forms.length, duplicate_ids: dups,
                 duplicate_id_count: Object.keys(dups).length,
                 tel_links: [...new Set(tels)], phones_in_text: phones,
                 title: document.title, inline_tag_scripts: inline, tracking_srcs: srcs };
    }""")
    cookies = {c["name"]: c["value"][:120] for c in ctx.cookies()}
    aw_html = sorted(set(re.findall(r"AW-\d{9,12}", html)))
    out = {
        "url": url,
        "http_status": resp.status if resp else None,
        "final_url": page.url.split("?")[0],
        "browser_title": dom["title"],
        "aw_ids_in_html": aw_html,
        "masonry_tag_present": MASONRY in " ".join(aw_html + reqs),
        "powerwashing_tag_present": POWERW in " ".join(aw_html + reqs),
        "masonry_pageview_remarketing": len(any_req(f"viewthroughconversion/{MASONRY}")),
        "masonry_user_list": len(any_req(f"1p-user-list/{MASONRY}")) +
                             len(any_req(f"rmkt/collect/{MASONRY}")),
        "masonry_website_call_wcm": len(any_req(f"conversion/{MASONRY}/wcm")),
        "masonry_form_data_posts": len(any_req(f"form-data/{MASONRY}")),
        "powerwashing_website_call_wcm": len(any_req(f"conversion/{POWERW}/wcm")),
        "powerwashing_conversion_reqs": len([u for u in reqs
                                             if f"conversion/{POWERW}/" in u
                                             and "/wcm" not in u]),
        "attribution_wcm_any": len(any_req("pagead/attribution/wcm")),
        "wc_cookies": sorted(k for k in cookies if k.startswith("wc_")),
        "wc_swap_cookie": cookies.get("wc_swap", "ABSENT"),
        "whatconverts_host_requests": len([u for u in reqs
                                           if "whatconverts" in u.lower()]),
        "iconnode_requests": len([u for u in reqs if "iconnode" in u.lower()]),
        "clickcease_requests": len([u for u in reqs if "ksrndkehqnwntyxlhgto" in u
                                    or "clickcease" in u.lower()]),
        "sgcaptcha_observed": len(any_req("sgcaptcha")) > 0,
        "gtm_ids": sorted(set(re.findall(r"GTM-[A-Z0-9]{6,10}", html))),
        "ga4_ids": sorted(set(re.findall(r"G-[A-Z0-9]{8,12}", html))),
        "gform_count": dom["form_count"],
        "duplicate_id_count": dom["duplicate_id_count"],
        "duplicate_ids_sample": sorted(dom["duplicate_ids"])[:14],
        "tel_links": dom["tel_links"],
        "malformed_tel_links": [t for t in dom["tel_links"]
                                if len(re.sub(r"\D", "", t)) < 10],
        "phones_in_text": dom["phones_in_text"],
        "tracking_script_srcs": dom["tracking_srcs"][:10],
        "inline_tag_script_excerpts": dom["inline_tag_scripts"][:4],
    }
    browser.close()
    return out


def main() -> int:
    now = datetime.now(ZoneInfo("America/New_York"))
    res = {"generated_account_local": now.isoformat(),
           "mode": "READ ONLY - no form filled, no submit clicked, no call placed",
           "masonry_tracking_id": MASONRY,
           "masonry_owner": "Softwind Landscape & Masonry - Live / customer 2429758629",
           "powerwashing_tracking_id": POWERW,
           "powerwashing_owner": "Softwind Power Washing - Live / customer 1521725229",
           "pages": []}
    with sync_playwright() as pw:
        for u in PAGES:
            try:
                res["pages"].append(scan(pw, u))
                print("scanned", u)
            except Exception as exc:
                res["pages"].append({"url": u, "ERROR": str(exc)[:200]})
                print("FAILED", u, str(exc)[:120])
    path = SNAP / f"page-tag-map-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    path.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("\nWROTE", path)
    for p in res["pages"]:
        if "ERROR" in p:
            print(f"\n{p['url']}  ERROR {p['ERROR']}")
            continue
        print(f"\n{p['url'].replace(BASE, '')}  [{p['http_status']}]  {p['browser_title'][:52]}")
        print(f"   AW ids: {p['aw_ids_in_html']}  | masonry={p['masonry_tag_present']} "
              f"powerwashing={p['powerwashing_tag_present']}")
        print(f"   masonry: pv={p['masonry_pageview_remarketing']} userlist={p['masonry_user_list']} "
              f"wcm={p['masonry_website_call_wcm']} form-data={p['masonry_form_data_posts']}")
        print(f"   powerwashing: wcm={p['powerwashing_website_call_wcm']} "
              f"conv={p['powerwashing_conversion_reqs']}")
        print(f"   forms={p['gform_count']} dupIDs={p['duplicate_id_count']} "
              f"tel={p['tel_links']} malformed={p['malformed_tel_links']}")
        print(f"   phones={p['phones_in_text']} wc_swap={p['wc_swap_cookie'][:46]}")
        print(f"   iconnode={p['iconnode_requests']} clickcease={p['clickcease_requests']} "
              f"sgcaptcha={p['sgcaptcha_observed']} gtm={p['gtm_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
