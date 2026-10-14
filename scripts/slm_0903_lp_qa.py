#!/usr/bin/env python3
"""Read-only landing-page QA for the Softwind L&M Patio and Pavers offers.

Uses a real headless browser. A plain HTTP GET is not a valid test here: the
site fronts pages with SG-Captcha, which serves non-JS clients an empty stub
(memory landing-page-qa-needs-real-browser).

READ ONLY. It never submits a form, never clicks a tel: link, and never
writes to the site. Query parameters are appended only to observe whether
click IDs survive the redirect chain and reach the form.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers/10-lp-qa.json"

PAGES = {
    "patio": "https://offer.softwindli.com/patio/",
    "pavers": "https://offer.softwindli.com/pavers/",
}
# Synthetic, obviously-fake click identifiers. Nothing is submitted.
PROBE = ("?gclid=GMQA_TEST_GCLID_20260903&utm_source=google&utm_medium=cpc"
         "&utm_campaign=qa_probe&utm_term=qa_probe_term")

TAG_PATTERNS = {
    "google_ads_gtag": r"googletagmanager\.com/gtag/js\?id=AW-(\d+)",
    "gtm_container": r"googletagmanager\.com/gtm\.js\?id=(GTM-[A-Z0-9]+)",
    "ga4": r"gtag\('config',\s*'(G-[A-Z0-9]+)'",
    "conversion_send_to": r"send_to['\"]?\s*:\s*['\"](AW-[\d]+/[\w\-]+)",
    "conversion_label": r"conversion/(\d+)/(\w+)",
    "whatconverts": r"(whatconverts|wct\.js|scripts\.whatconverts)",
    "clickcease": r"(clickcease|monitor\.clickcease)",
    "iconnode": r"process\.iconnode\.com",
}


def main() -> int:
    from playwright.sync_api import sync_playwright

    report = {"checked_at": datetime.now().astimezone().isoformat(),
              "method": "headless chromium, JS enabled, read-only",
              "pages": {}}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for name, base in PAGES.items():
            page_report = {"requested_url": base}
            ctx = browser.new_context(
                viewport={"width": 390, "height": 844}, is_mobile=True,
                user_agent=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                            "Version/17.0 Mobile/15E148 Safari/604.1"))
            page = ctx.new_page()
            requests = []
            page.on("request", lambda r: requests.append(r.url))
            try:
                resp = page.goto(base + PROBE, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)
                page_report["status"] = resp.status if resp else None
                page_report["final_url"] = page.url
                page_report["redirected"] = page.url.split("?")[0] != base
                chain = []
                r = resp
                while r is not None:
                    req = r.request
                    chain.append({"url": req.url, "status": r.status})
                    r = req.redirected_from.response() if req.redirected_from else None
                page_report["redirect_chain"] = list(reversed(chain))

                html = page.content()
                page_report["html_bytes"] = len(html)
                page_report["title"] = page.title()

                # canonical
                can = page.query_selector("link[rel=canonical]")
                page_report["canonical"] = can.get_attribute("href") if can else None

                # headings
                page_report["h1"] = [h.inner_text().strip()
                                     for h in page.query_selector_all("h1")]
                page_report["h2"] = [h.inner_text().strip()
                                     for h in page.query_selector_all("h2")][:12]

                # phone numbers rendered and tel: links
                tels = sorted({a.get_attribute("href")
                               for a in page.query_selector_all("a[href^='tel:']")})
                page_report["tel_links"] = tels
                page_report["malformed_tel"] = [t for t in tels
                                                if t and not re.fullmatch(r"tel:\+?[\d\-\.\(\)\s]+", t)]
                body = page.inner_text("body")
                page_report["visible_phone_numbers"] = sorted(set(
                    re.findall(r"\(?\b\d{3}\)?[\s\-\.]\d{3}[\s\-\.]\d{4}\b", body)))

                # forms
                forms = page.query_selector_all("form")
                page_report["form_count"] = len(forms)
                page_report["form_ids"] = [f.get_attribute("id") for f in forms]
                fields = []
                for f in forms:
                    for el in f.query_selector_all("input, select, textarea"):
                        fields.append({
                            "form": f.get_attribute("id"),
                            "name": el.get_attribute("name"),
                            "id": el.get_attribute("id"),
                            "type": el.get_attribute("type"),
                            "required": el.get_attribute("aria-required")
                                        or el.get_attribute("required"),
                            "hidden": (el.get_attribute("type") == "hidden"),
                        })
                page_report["form_fields"] = fields
                page_report["hidden_field_names"] = sorted(
                    {f["name"] for f in fields if f["hidden"] and f["name"]})
                # duplicate DOM ids
                ids = page.eval_on_selector_all(
                    "[id]", "els => els.map(e => e.id)")
                seen, dupes = set(), set()
                for i in ids:
                    if i in seen:
                        dupes.add(i)
                    seen.add(i)
                page_report["duplicate_dom_ids"] = sorted(dupes)

                # tags observed in HTML + network
                joined = html + "\n" + "\n".join(requests)
                tags = {}
                for k, pat in TAG_PATTERNS.items():
                    tags[k] = sorted(set(
                        m if isinstance(m, str) else "/".join(m)
                        for m in re.findall(pat, joined, re.I)))
                page_report["tags"] = tags
                page_report["third_party_hosts"] = sorted({
                    re.sub(r"^https?://([^/]+).*", r"\1", u) for u in requests
                    if not re.match(r"^https?://(offer\.)?softwindli\.com", u)
                    and u.startswith("http")})

                # did the probe click ID survive into the page / form?
                page_report["gclid_in_final_url"] = "GMQA_TEST_GCLID_20260903" in page.url
                page_report["gclid_in_dom"] = "GMQA_TEST_GCLID_20260903" in html
                page_report["utm_in_dom"] = "qa_probe" in html
                page_report["cookies"] = sorted({
                    c["name"] for c in ctx.cookies()})

                page.screenshot(path=str(OUT.parent / ("10-lp-%s-mobile.png" % name)),
                                full_page=False)
            except Exception as exc:  # noqa: BLE001
                page_report["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
            finally:
                ctx.close()
            report["pages"][name] = page_report
        browser.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    for name, p in report["pages"].items():
        print("\n=== %s ===" % name)
        if "error" in p:
            print("   ERROR: %s" % p["error"]); continue
        print("   status=%s bytes=%d redirected=%s" % (p["status"], p["html_bytes"], p["redirected"]))
        print("   final_url=%s" % p["final_url"][:110])
        print("   title=%r" % p["title"])
        print("   h1=%s" % p["h1"])
        print("   forms=%d ids=%s" % (p["form_count"], p["form_ids"]))
        print("   duplicate_dom_ids=%d" % len(p["duplicate_dom_ids"]))
        print("   tel_links=%s malformed=%s" % (p["tel_links"], p["malformed_tel"]))
        print("   visible_phones=%s" % p["visible_phone_numbers"])
        print("   gclid_in_final_url=%s gclid_in_dom=%s utm_in_dom=%s" % (
            p["gclid_in_final_url"], p["gclid_in_dom"], p["utm_in_dom"]))
        for k, v in p["tags"].items():
            if v:
                print("   tag %-22s %s" % (k, v))
        print("   hidden_fields=%s" % p["hidden_field_names"])
        print("   third_party_hosts=%s" % p["third_party_hosts"])
    print("\nwrote %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
