#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: extract verifiable trust/offer claims from Master Grass paid landing pages.

Real browser (SG-Captcha host), GET only, no query parameters (never write QA markers into the
page cache), no form interaction. Writes page text to evidence; prints only claim-like sentences.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "mastergrass-lawn-care" / "evidence"
URLS = [
    "https://offer.mastergrasslawncare.com/landscaping-contractor/",
    "https://offer.mastergrasslawncare.com/french-drain/",
    "https://offer.mastergrasslawncare.com/retaining-walls/",
    "https://offer.mastergrasslawncare.com/hardscaping/",
    "https://mastergrasslawncare.com/",
]
CLAIM = re.compile(r"(\d+\+?\s*(years?|yrs)|review|star|rated|licensed|insured|bonded|guarantee|warrant|"
                   r"financ|family|owned|locally|since \d{4}|free (quote|estimate)|same[- ]day|"
                   r"respond|within \d+|award|certified|bbb|\bgoogle\b|satisf|\d{2,4}\+?\s*(projects|customers|clients|homes))", re.I)
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    for u in URLS:
        for _ in range(4):
            page.goto(u, wait_until="domcontentloaded", timeout=60000)
            time.sleep(6)
            if "Robot Challenge" not in page.title():
                break
        txt = page.inner_text("body")
        out[u] = txt
        sents = {s.strip() for s in re.split(r"[\n\.!?]", txt) if CLAIM.search(s) and 3 < len(s.strip()) < 180}
        print(f"\n## {u}  ({len(txt)} chars)")
        for s in sorted(sents)[:40]:
            print("  -", s)
    b.close()
(EVID / "lp-text-2026-09-26.json").write_text(json.dumps(out, indent=0), encoding="utf-8")
