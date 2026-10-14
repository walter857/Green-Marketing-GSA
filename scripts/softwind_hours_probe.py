#!/usr/bin/env python3
"""Read-only: extract the published hours of operation from the Softwind contact page.

GET navigation only. Nothing is submitted and nothing on the site is changed.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients/softwind-power-washing/snapshots/business-hours-2026-08-25.json"
URL = "https://softwindli.com/contact-us/"


def main() -> int:
    rec = {"url": URL}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True,
                               args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(viewport={"width": 1440, "height": 900},
                            locale="en-US", timezone_id="America/New_York")
        page = ctx.new_page()
        for _ in range(4):
            try:
                page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            except Exception:
                time.sleep(6)
                continue
            if "sgcaptcha" in page.url:
                try:
                    page.wait_for_url(lambda u: "sgcaptcha" not in u, timeout=45000)
                except Exception:
                    pass
                time.sleep(6)
            if "sgcaptcha" not in page.url:
                break
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        rec["final_url"] = page.url
        text = page.inner_text("body")
        text = re.sub(r"[-]", " ", text)
        rec["full_text_len"] = len(text)
        i = text.lower().find("hours of operation")
        rec["hours_block"] = text[i:i + 700] if i >= 0 else ""
        # every emails / phones anywhere on the page
        rec["phones"] = sorted(set(re.findall(
            r"\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b", text)))
        rec["emails"] = sorted(set(re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))
        # service-area list, if the page carries one
        j = text.lower().find("service area")
        rec["service_area_block"] = text[j:j + 900] if j >= 0 else ""
        ctx.close()
        b.close()
    OUT.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(json.dumps(rec, indent=2)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
