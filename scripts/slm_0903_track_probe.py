#!/usr/bin/env python3
"""Deep read-only probe of the WhatConverts phone swap and the attribution chain.

The QA gate forbids asserting that the number mismatch explains zero WhatConverts
calls unless it is proven. This script gathers what a browser can see:

  - the number rendered on each page, desktop AND mobile
  - every tel: href
  - the wc_swap rule and both of its numbers
  - whether the WhatConverts script actually loads, and from where
  - whether the rendered number ever changes after the script runs
  - whether a GCLID and UTMs reach the page, the cookie, and the form

It submits nothing and clicks no tel: link.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers/19-track-probe.json"

PAGES = {"patio": "https://offer.softwindli.com/patio/",
         "pavers": "https://offer.softwindli.com/pavers/"}
PROBE = ("?gclid=GMQA_TEST_GCLID_20260903B&utm_source=google&utm_medium=cpc"
         "&utm_campaign=QAGATE_CAMPAIGN&utm_term=QAGATE_TERM"
         "&utm_content=QAGATE_ADGROUP")
PHONE_RE = re.compile(r"\(?\b(\d{3})\)?[\s\-\.]?(\d{3})[\s\-\.]?(\d{4})\b")

DESKTOP = {"viewport": {"width": 1440, "height": 900}, "is_mobile": False,
           "user_agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36")}
MOBILE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True,
          "has_touch": True,
          "user_agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                         "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                         "Version/17.0 Mobile/15E148 Safari/604.1")}


def digits(s):
    return re.sub(r"\D", "", s or "")


def probe(pw, url, ctx_args, label):
    browser = pw.chromium.launch()
    ctx = browser.new_context(**ctx_args)
    page = ctx.new_page()
    reqs, resps = [], []
    page.on("request", lambda r: reqs.append(r.url))
    page.on("response", lambda r: resps.append((r.url, r.status)))
    rec = {"label": label, "url": url}
    try:
        r = page.goto(url + PROBE, wait_until="domcontentloaded", timeout=60000)
        rec["status"] = r.status if r else None
        # snapshot the phone BEFORE the swap script can have run
        early = page.inner_text("body")
        rec["phones_at_domcontentloaded"] = sorted(
            {"".join(m) for m in PHONE_RE.findall(early)})
        page.wait_for_load_state("networkidle", timeout=60000)
        page.wait_for_timeout(6000)
        late = page.inner_text("body")
        rec["phones_after_networkidle_plus_6s"] = sorted(
            {"".join(m) for m in PHONE_RE.findall(late)})
        rec["number_changed_after_scripts_ran"] = (
            rec["phones_at_domcontentloaded"] != rec["phones_after_networkidle_plus_6s"])
        rec["tel_hrefs"] = sorted({a.get_attribute("href")
                                   for a in page.query_selector_all("a[href^='tel:']")})
        rec["tel_href_digits"] = sorted({digits(h) for h in rec["tel_hrefs"] if h})
        cookies = {c["name"]: c["value"] for c in ctx.cookies()}
        rec["wc_cookies"] = {k: v for k, v in cookies.items() if k.startswith("wc")}
        swap = cookies.get("wc_swap", "")
        parts = swap.split("+..+") if swap else []
        rec["wc_swap_raw"] = swap
        rec["wc_swap_parsed"] = {
            "number_to_find": parts[0] if len(parts) > 0 else None,
            "number_to_show": parts[1] if len(parts) > 1 else None,
            "swap_rule_id": parts[2] if len(parts) > 2 else None,
        }
        rec["swap_source_number_present_on_page"] = (
            rec["wc_swap_parsed"]["number_to_find"] in
            [d for d in rec["phones_after_networkidle_plus_6s"]]
            if rec["wc_swap_parsed"]["number_to_find"] else None)
        rec["swap_target_number_present_on_page"] = (
            rec["wc_swap_parsed"]["number_to_show"] in
            [d for d in rec["phones_after_networkidle_plus_6s"]]
            if rec["wc_swap_parsed"]["number_to_show"] else None)
        # WhatConverts script: where does it actually come from?
        rec["wc_script_requests"] = sorted({u for u in reqs
                                            if "whatconverts" in u.lower()
                                            or "/wct" in u.lower()})
        rec["wc_script_responses"] = [
            {"url": u, "status": s} for u, s in resps
            if "whatconverts" in u.lower() or "/wct" in u.lower()]
        html = page.content()
        rec["wc_in_html"] = "whatconverts" in html.lower()
        rec["wc_script_tags_in_dom"] = page.eval_on_selector_all(
            "script[src]", "els => els.map(e => e.src)")
        rec["wc_script_tags_matching"] = [s for s in rec["wc_script_tags_in_dom"]
                                          if "whatconverts" in s.lower()]
        rec["inline_script_mentions_wc"] = bool(
            re.search(r"whatconverts|wc_swap|wcSwap", html, re.I))
        # attribution chain
        rec["gclid_in_url"] = "GMQA_TEST_GCLID_20260903B" in page.url
        rec["gclid_in_dom"] = "GMQA_TEST_GCLID_20260903B" in html
        wcc = cookies.get("wc_client", "")
        rec["wc_client_fields"] = wcc.split("+..+") if wcc else []
        rec["wc_client_has_gclid"] = "GMQA_TEST_GCLID_20260903B" in wcc
        rec["wc_client_has_campaign"] = "QAGATE_CAMPAIGN" in wcc
        rec["wc_client_has_term"] = "QAGATE_TERM" in wcc
        rec["wc_client_has_adgroup"] = "QAGATE_ADGROUP" in wcc
        rec["gcl_cookies"] = sorted(k for k in cookies if k.startswith("_gcl")
                                    or k.startswith("GCL"))
        rec["form_hidden_values"] = {
            n: [e.get_attribute("value") for e in
                page.query_selector_all("input[name='%s']" % n)]
            for n in ("input_8", "gform_field_values")}
        rec["consent_banner_present"] = bool(
            page.query_selector("[id*=cookie i],[class*=cookie i],[id*=consent i],"
                                "[class*=consent i]"))
        rec["third_party_hosts"] = sorted({
            re.sub(r"^https?://([^/]+).*", r"\1", u) for u in reqs
            if u.startswith("http")
            and not re.match(r"^https?://(offer\.)?softwindli\.com", u)})
    except Exception as exc:  # noqa: BLE001
        rec["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        ctx.close(); browser.close()
    return rec


def main() -> int:
    from playwright.sync_api import sync_playwright
    report = {"checked_at": datetime.now().astimezone().isoformat(),
              "method": "headless chromium, JS enabled, read-only, nothing submitted",
              "probes": []}
    with sync_playwright() as pw:
        for name, url in PAGES.items():
            for label, args in (("desktop", DESKTOP), ("mobile", MOBILE)):
                r = probe(pw, url, args, "%s/%s" % (name, label))
                report["probes"].append(r)
                print("\n=== %s ===" % r["label"])
                if "error" in r:
                    print("  ERROR %s" % r["error"]); continue
                print("  phones @domcontentloaded : %s" % r["phones_at_domcontentloaded"])
                print("  phones @networkidle+6s   : %s" % r["phones_after_networkidle_plus_6s"])
                print("  number changed by scripts: %s" % r["number_changed_after_scripts_ran"])
                print("  tel: hrefs               : %s" % r["tel_hrefs"])
                print("  wc_swap                  : %s" % r["wc_swap_raw"])
                print("     find=%s  show=%s  rule=%s"
                      % (r["wc_swap_parsed"]["number_to_find"],
                         r["wc_swap_parsed"]["number_to_show"],
                         r["wc_swap_parsed"]["swap_rule_id"]))
                print("     find-number on page? %s   show-number on page? %s"
                      % (r["swap_source_number_present_on_page"],
                         r["swap_target_number_present_on_page"]))
                print("  wc script requests       : %s" % r["wc_script_requests"])
                print("  wc script tags in DOM    : %s" % r["wc_script_tags_matching"])
                print("  wc mentioned in html     : %s" % r["wc_in_html"])
                print("  gclid in cookie/campaign/term/adgroup: %s / %s / %s / %s"
                      % (r["wc_client_has_gclid"], r["wc_client_has_campaign"],
                         r["wc_client_has_term"], r["wc_client_has_adgroup"]))
                print("  wc_client fields         : %s" % r["wc_client_fields"])
                print("  form hidden values       : %s" % r["form_hidden_values"])
                print("  consent banner present   : %s" % r["consent_banner_present"])
    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print("\nwrote %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
