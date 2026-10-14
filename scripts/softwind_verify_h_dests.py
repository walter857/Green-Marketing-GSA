#!/usr/bin/env python3
"""Re-verify the four PLAN-H destination pages with SG-Captcha handling.

The first pass flagged all four because the verdict required HTTP 200, but this
host answers 202 through its edge. Three pages were substantively fine. The
fourth, /patio-power-washing/, returned an empty stub with no tel: link and no
form - the documented SG-Captcha behaviour, which needs a retry on a warmed
context before any conclusion is drawn.

READ ONLY. GET navigation only. No form submitted, no call placed.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("America/New_York")
APPROVED_DIGITS = "6315027946"
UNTRACKED_DIGITS = "6315025402"
THIRD_DIGITS = "6315535927"
OUT = ROOT / "clients/softwind-power-washing/snapshots/h-destinations-2026-08-27.json"

URLS = [
    "https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/",
    "https://offer.softwindli.com/house-washing-company/",
    "https://offer.softwindli.com/driveway-pressure-washing/",
    "https://offer.softwindli.com/patio-power-washing/",
]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def probe(ctx, url, attempt):
    page = ctx.new_page()
    rec = {"attempt": attempt}
    paid = url + ("&" if "?" in url else "?") + (
        "gclid=TESTGCLID_readonly_planh&utm_source=google&utm_medium=cpc"
        "&utm_campaign=planh_preflight")
    resp = page.goto(paid, wait_until="domcontentloaded", timeout=60000)
    rec["http_status"] = resp.status if resp else None
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
    except Exception:                                          # noqa: BLE001
        pass
    page.wait_for_timeout(12000)
    html = page.content()
    rec["html_len"] = len(html)
    rec["captcha_stub"] = ("sgcaptcha" in html.lower()
                           or "_sg_" in html.lower()
                           or len(html) < 4000)
    tels = re.findall(r'href=["\']tel:([^"\']+)["\']', html)
    digits = {re.sub(r"\D", "", t)[-10:] for t in tels if re.sub(r"\D", "", t)}
    rec["tel_digits"] = sorted(d for d in digits if len(d) == 10)
    rec["approved_in_tel"] = APPROVED_DIGITS in digits
    rec["untracked_in_tel"] = UNTRACKED_DIGITS in digits
    rec["third_number_in_tel"] = THIRD_DIGITS in digits
    rec["form_count"] = html.count("<form")
    rec["title"] = (page.title() or "")[:140]
    h1 = page.query_selector("h1")
    rec["h1"] = ((h1.inner_text() or "").strip()[:160]) if h1 else ""
    rec["gclid_preserved"] = "TESTGCLID_readonly_planh" in page.url
    rec["final_url"] = page.url.split("?")[0]
    body_digits = re.sub(r"\D", "", re.sub(r"<[^>]+>", " ", html))
    rec["approved_in_body"] = APPROVED_DIGITS in body_digits
    rec["untracked_in_body"] = UNTRACKED_DIGITS in body_digits
    page.close()
    return rec


def main() -> int:
    from playwright.sync_api import sync_playwright
    now = datetime.now(TZ)
    out = {"read_only": True, "forms_submitted": 0, "calls_placed": 0,
           "timestamp_account_local": now.isoformat(),
           "status_note": ("This host answers 202 through its SiteGround edge. "
                           "202 is ACCEPTED as healthy; the substantive test is "
                           "the rendered tel: link, the form, and the H1."),
           "pages": []}
    print("PLAN-H DESTINATION RE-VERIFICATION  %s"
          % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 78)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        # One shared, warmed context so an SG-Captcha cookie earned on the first
        # page carries to the rest, which is how a real visitor experiences it.
        ctx = browser.new_context(viewport={"width": 1366, "height": 900},
                                  user_agent=UA, locale="en-US")
        for url in URLS:
            rec = {"url": url, "attempts": []}
            try:
                a1 = probe(ctx, url, 1)
                rec["attempts"].append(a1)
                final = a1
                if not a1["approved_in_tel"]:
                    print("   retrying %s (attempt 1 gave no tel: link)"
                          % url.rsplit("/", 2)[-2])
                    ctx.clear_cookies()
                    a2 = probe(ctx, url, 2)
                    rec["attempts"].append(a2)
                    if not a2["approved_in_tel"]:
                        a3 = probe(ctx, url, 3)
                        rec["attempts"].append(a3)
                        final = a3
                    else:
                        final = a2
                rec["final"] = final
                rec["healthy"] = bool(
                    final["http_status"] in (200, 202)
                    and final["approved_in_tel"]
                    and not final["untracked_in_tel"]
                    and final["form_count"] > 0)
            except Exception as exc:                           # noqa: BLE001
                rec["error"] = str(exc)[:300]
                rec["healthy"] = False
            out["pages"].append(rec)
            f = rec.get("final", {})
            print("\n%s" % url)
            print("   attempts=%d status=%s html_len=%s stub=%s"
                  % (len(rec["attempts"]), f.get("http_status"),
                     f.get("html_len"), f.get("captcha_stub")))
            print("   tel=%s approved=%s untracked=%s third=%s forms=%s gclid=%s"
                  % (f.get("tel_digits"), f.get("approved_in_tel"),
                     f.get("untracked_in_tel"), f.get("third_number_in_tel"),
                     f.get("form_count"), f.get("gclid_preserved")))
            print("   h1: %s" % (f.get("h1") or "(none)"))
            print("   HEALTHY: %s" % rec["healthy"])
        ctx.close()
        browser.close()

    out["all_healthy"] = all(p.get("healthy") for p in out["pages"])
    out["unhealthy"] = [p["url"] for p in out["pages"] if not p.get("healthy")]
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n" + "=" * 78)
    print("ALL FOUR HEALTHY: %s" % out["all_healthy"])
    for u in out["unhealthy"]:
        print("   NOT VERIFIED: %s" % u)
    print("wrote %s" % OUT)
    return 0 if out["all_healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
