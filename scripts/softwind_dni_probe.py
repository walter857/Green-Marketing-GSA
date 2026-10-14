#!/usr/bin/env python3
"""PLAN-H precondition: does WhatConverts dynamic number insertion swap the
static main-site phone to the tracked campaign number for paid visitors?

READ-ONLY. GET navigation only. No form is submitted. No call is placed.
Nothing on the site is modified.

Each URL is loaded twice in a FRESH browser context:
  pass 1  clean          - no tracking parameters, no prior cookies
  pass 2  paid           - gclid + gbraid + utm_source/medium/campaign

DNI is asynchronous, so each pass waits for network idle and then polls the DOM
for a number change before recording. WhatConverts sets a wc_swap cookie that
reveals whether a swap was attempted at all.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients/softwind-power-washing/snapshots/dni-probe-2026-08-26.json"

APPROVED_TRACKED = "6315027946"     # campaign / offer-page number
STATIC_MAIN_SITE = "6315025402"     # number published on softwindli.com

URLS = [
    "https://softwindli.com/reviews/",
    "https://softwindli.com/contact-us/",
    "https://softwindli.com/our-work/",
    "https://softwindli.com/service-areas/",
    "https://softwindli.com/services/landscaping/pressure-washing/",
]

PAID_QS = ("gclid=TESTGCLID_readonly_dni_probe"
           "&gbraid=0AAAABEbqp-TESTREADONLY"
           "&utm_source=google&utm_medium=cpc&utm_campaign=dni-probe")

PHONE_RE = re.compile(r"\(?\b(\d{3})\)?[\s.\-]?(\d{3})[\s.\-]?(\d{4})\b")
WC_HOSTS = re.compile(r"whatconverts|wct\.|leadassist", re.I)


def digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def probe(ctx, url: str, label: str) -> dict:
    page = ctx.new_page()
    reqs: list[str] = []
    page.on("request", lambda r: reqs.append(r.url))
    rec = {"pass": label, "requested_url": url}

    resp = None
    for attempt in range(4):
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as exc:
            rec["nav_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
            time.sleep(5)
            continue
        if resp is None:
            time.sleep(5)
            continue
        if "sgcaptcha" in page.url or resp.status in (202, 403, 429):
            rec["captcha_interstitial"] = True
            try:
                page.wait_for_url(lambda u: "sgcaptcha" not in u, timeout=45000)
            except Exception:
                pass
            time.sleep(4 + attempt * 4)
            if "sgcaptcha" in page.url:
                continue
        rec.pop("nav_error", None)
        break

    if resp is None or "sgcaptcha" in page.url:
        rec["error"] = "could not clear SG-Captcha"
        rec["final_url"] = page.url
        page.close()
        return rec

    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass

    # DNI is async. Poll for up to ~12s for the tracked number to appear.
    # page.content() throws while the page is mid-navigation (SG-Captcha bounces),
    # so every read is guarded and a failed read simply retries.
    def safe_html():
        for _ in range(3):
            try:
                return page.content()
            except Exception:
                time.sleep(1)
        return ""

    swapped_at = None
    for i in range(12):
        h = safe_html()
        if h and APPROVED_TRACKED in digits(h):
            swapped_at = i
            break
        time.sleep(1)

    rec["final_url"] = page.url
    rec["http_status"] = resp.status
    rec["dni_wait_seconds_until_tracked_number_seen"] = swapped_at

    try:
        body = page.inner_text("body") if page.query_selector("body") else ""
    except Exception:
        body = ""
    tel = sorted({(e.get_attribute("href") or "").replace("tel:", "").strip()
                  for e in page.query_selector_all("a[href^='tel:']")})
    rec["tel_links_raw"] = [t for t in tel if t]
    rec["tel_links_digits"] = sorted({digits(t) for t in tel if digits(t)})
    rec["phones_in_visible_text"] = sorted({"".join(m) for m in PHONE_RE.findall(body)})

    html = safe_html()
    rec["tracked_number_anywhere_in_dom"] = APPROVED_TRACKED in digits(html)
    rec["static_number_anywhere_in_dom"] = STATIC_MAIN_SITE in digits(html)

    # WhatConverts activity
    wc_reqs = sorted({r for r in reqs if WC_HOSTS.search(r)})
    rec["whatconverts_requests"] = [r[:160] for r in wc_reqs][:12]
    rec["whatconverts_request_count"] = len(wc_reqs)
    rec["whatconverts_script_in_dom"] = bool(re.search(r"whatconverts", html, re.I))

    cookies = ctx.cookies()
    rec["cookies"] = sorted(
        "%s=%s" % (c["name"], (c["value"] or "")[:60])
        for c in cookies if re.search(r"wc|convert|swap|gclid|profile",
                                      c["name"], re.I))
    rec["wc_swap_cookie_present"] = any(
        c["name"].lower().startswith("wc_swap") for c in cookies)

    # number pool: WhatConverts exposes swapped numbers via data attributes
    pool = set()
    for sel in ("[data-wc-number]", "[data-number]", ".wc_number", "[class*=wc-]"):
        for e in page.query_selector_all(sel):
            for a in ("data-wc-number", "data-number"):
                v = e.get_attribute(a)
                if v and digits(v):
                    pool.add(digits(v))
    rec["number_pool_attributes_observed"] = sorted(pool)

    page.close()
    return rec


def main() -> int:
    results = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"])
        for url in URLS:
            for label, target in (("clean", url),
                                  ("paid", url + ("&" if "?" in url else "?") + PAID_QS)):
                # fresh context per pass so no cookie carries a prior swap over
                ctx = b.new_context(
                    viewport={"width": 1440, "height": 900},
                    user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/141.0.0.0 Safari/537.36"),
                    locale="en-US", timezone_id="America/New_York")
                if label == "paid":
                    ctx.set_extra_http_headers({"Referer": "https://www.google.com/"})
                rec = probe(ctx, target, label)
                rec["base_url"] = url
                results.append(rec)
                st = rec.get("http_status", "ERR")
                print("[%-5s] %s %s" % (label, st, url))
                print("         tel=%s  text=%s  tracked_in_dom=%s  wc_reqs=%d"
                      % (rec.get("tel_links_digits"), rec.get("phones_in_visible_text"),
                         rec.get("tracked_number_anywhere_in_dom"),
                         rec.get("whatconverts_request_count", 0)))
                if rec.get("error"):
                    print("         ERROR %s" % rec["error"])
                ctx.close()
                time.sleep(3)
        b.close()

    # verdict per URL
    verdicts = []
    by = {}
    for r in results:
        by.setdefault(r["base_url"], {})[r["pass"]] = r
    for url, passes in by.items():
        c, p = passes.get("clean", {}), passes.get("paid", {})
        if c.get("error") or p.get("error"):
            v = "INCONCLUSIVE - page could not be rendered"
        elif p.get("tracked_number_anywhere_in_dom"):
            v = "DNI WORKS - tracked number present on the paid load"
        elif (c.get("tel_links_digits") != p.get("tel_links_digits")):
            v = "NUMBER CHANGED but not to the approved tracked number"
        else:
            v = "DNI DOES NOT SWAP - paid load shows the same static number"
        verdicts.append({
            "url": url, "verdict": v,
            "clean_tel": c.get("tel_links_digits"),
            "paid_tel": p.get("tel_links_digits"),
            "clean_text_phones": c.get("phones_in_visible_text"),
            "paid_text_phones": p.get("phones_in_visible_text"),
            "paid_tracked_in_dom": p.get("tracked_number_anywhere_in_dom"),
            "paid_wc_requests": p.get("whatconverts_request_count"),
            "paid_wc_script_in_dom": p.get("whatconverts_script_in_dom"),
            "paid_wc_swap_cookie": p.get("wc_swap_cookie_present"),
            "paid_cookies": p.get("cookies"),
            "number_pool": p.get("number_pool_attributes_observed"),
        })

    out = {
        "probe_date": "2026-08-26",
        "method": ("GET navigation only, fresh browser context per pass, "
                   "networkidle + up to 12s DOM poll for an async swap. "
                   "No form submitted, no call placed."),
        "approved_tracked_number": APPROVED_TRACKED,
        "static_main_site_number": STATIC_MAIN_SITE,
        "paid_query_string": PAID_QS,
        "verdicts": verdicts,
        "raw": results,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("\n" + "=" * 78)
    print("PER-URL VERDICT")
    for v in verdicts:
        print("\n  %s" % v["url"])
        print("    verdict          : %s" % v["verdict"])
        print("    clean tel / text : %s / %s" % (v["clean_tel"], v["clean_text_phones"]))
        print("    paid  tel / text : %s / %s" % (v["paid_tel"], v["paid_text_phones"]))
        print("    tracked in DOM   : %s" % v["paid_tracked_in_dom"])
        print("    WC requests/script/swap-cookie : %s / %s / %s"
              % (v["paid_wc_requests"], v["paid_wc_script_in_dom"],
                 v["paid_wc_swap_cookie"]))
        if v["paid_cookies"]:
            print("    cookies          : %s" % v["paid_cookies"])
        if v["number_pool"]:
            print("    number pool      : %s" % v["number_pool"])
    works = sum(1 for v in verdicts if v["verdict"].startswith("DNI WORKS"))
    print("\n%d of %d sitelink destinations swap to the tracked number."
          % (works, len(verdicts)))
    print("\nWrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
