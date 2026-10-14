#!/usr/bin/env python3
"""PLAN-H confirmation pass: longer DNI wait, and explicitly hunt for the swap
target revealed by the wc_swap cookie.

READ-ONLY. GET navigation only. No form submitted. No call placed.

The first probe found wc_swap = 6315025402 .. 6315535927 .. 197159, meaning
WhatConverts is configured to replace the static main-site number with
(631) 553-5927 - which is NEITHER the static number NOR the approved campaign
tracking number (631) 502-7946. This pass waits 40s and re-reads to establish
whether that swap ever actually reaches the DOM.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients/softwind-power-washing/snapshots/dni-confirm-2026-08-26.json"

APPROVED_TRACKED = "6315027946"
STATIC_MAIN_SITE = "6315025402"
WC_SWAP_TARGET = "6315535927"

URLS = [
    "https://softwindli.com/reviews/",
    "https://softwindli.com/services/landscaping/pressure-washing/",
    "https://softwindli.com/contact-us/",
]
PAID_QS = ("gclid=TESTGCLID_readonly_dni_confirm"
           "&utm_source=google&utm_medium=cpc&utm_campaign=dni-confirm")
PHONE_RE = re.compile(r"\(?\b(\d{3})\)?[\s.\-]?(\d{3})[\s.\-]?(\d{4})\b")


def d(s):
    return re.sub(r"\D", "", s or "")


def main() -> int:
    results = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True,
                               args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"),
            locale="en-US", timezone_id="America/New_York")
        ctx.set_extra_http_headers({"Referer": "https://www.google.com/"})
        page = ctx.new_page()

        # warm the bot-management cookie once, as a real visitor would
        try:
            page.goto("https://softwindli.com/", wait_until="domcontentloaded",
                      timeout=60000)
            page.wait_for_timeout(12000)
        except Exception:
            pass

        for url in URLS:
            target = url + ("&" if "?" in url else "?") + PAID_QS
            rec = {"url": url, "pass": "paid_long_wait"}
            ok = False
            for attempt in range(5):
                try:
                    resp = page.goto(target, wait_until="domcontentloaded", timeout=60000)
                except Exception as e:
                    rec["nav_error"] = str(e)[:120]
                    time.sleep(8)
                    continue
                if "sgcaptcha" in page.url or resp.status in (202, 403, 429):
                    try:
                        page.wait_for_url(lambda u: "sgcaptcha" not in u, timeout=45000)
                    except Exception:
                        pass
                    time.sleep(8 + attempt * 5)
                if "sgcaptcha" not in page.url:
                    ok = True
                    rec["http_status"] = resp.status
                    break
            if not ok:
                rec["error"] = "SG-Captcha never cleared after 5 attempts"
                results.append(rec)
                print("  %-62s CAPTCHA BLOCKED" % url)
                continue

            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass

            timeline = []
            for sec in (0, 5, 10, 20, 30, 40):
                if sec:
                    time.sleep(sec - timeline[-1]["t"] if timeline else sec)
                try:
                    html = page.content()
                    body = page.inner_text("body")
                    tel = sorted({d((e.get_attribute("href") or "").replace("tel:", ""))
                                  for e in page.query_selector_all("a[href^='tel:']")})
                except Exception:
                    continue
                timeline.append({
                    "t": sec,
                    "tel_links": [t for t in tel if t],
                    "text_phones": sorted({"".join(m) for m in PHONE_RE.findall(body)}),
                    "static_in_dom": STATIC_MAIN_SITE in d(html),
                    "wc_swap_target_in_dom": WC_SWAP_TARGET in d(html),
                    "approved_tracked_in_dom": APPROVED_TRACKED in d(html),
                })
            rec["timeline"] = timeline
            cookies = ctx.cookies()
            rec["wc_cookies"] = sorted(
                "%s=%s" % (c["name"], c["value"][:80])
                for c in cookies if c["name"].lower().startswith("wc"))
            results.append(rec)
            last = timeline[-1] if timeline else {}
            print("  %-62s tel=%s static=%s swap_target=%s approved=%s"
                  % (url, last.get("tel_links"), last.get("static_in_dom"),
                     last.get("wc_swap_target_in_dom"),
                     last.get("approved_tracked_in_dom")))
        ctx.close()
        b.close()

    approved_anywhere = any(
        p.get("approved_tracked_in_dom")
        for r in results for p in r.get("timeline", []))
    swap_anywhere = any(
        p.get("wc_swap_target_in_dom")
        for r in results for p in r.get("timeline", []))

    out = {
        "probe_date": "2026-08-26",
        "method": ("Warmed bot-management cookie, single reused context, paid "
                   "parameters, DOM re-read at 0/5/10/20/30/40 seconds. GET only. "
                   "No form submitted, no call placed."),
        "numbers": {
            "approved_campaign_tracking": APPROVED_TRACKED,
            "static_main_site": STATIC_MAIN_SITE,
            "whatconverts_swap_target_from_wc_swap_cookie": WC_SWAP_TARGET,
        },
        "approved_tracked_number_ever_rendered": approved_anywhere,
        "whatconverts_swap_target_ever_rendered": swap_anywhere,
        "results": results,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print()
    print("approved tracked number (%s) ever rendered : %s"
          % (APPROVED_TRACKED, approved_anywhere))
    print("wc_swap target        (%s) ever rendered : %s"
          % (WC_SWAP_TARGET, swap_anywhere))
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
