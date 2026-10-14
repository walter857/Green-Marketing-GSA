#!/usr/bin/env python3
"""Ambient | 2026-09-20 | Pull the full visible copy of the expansion destinations.

READ-ONLY. No parameters, no form submission, no tel activation.

Needed for two decisions the plan cannot make without it:
  - does each page actually support the intent its keywords carry (install vs
    repair vs replace vs service), and
  - is every RSA line backed by copy on its own landing page.

Writes full body text to the scratch snapshot so claim checks are reproducible.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-20"
DEST = {
    "Furnace Repair": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "Mini Split Installation": "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/",
    "Gas Boiler Repair": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "Boiler Repair": "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/",
    "Oil Furnace Installation": "https://ambientcoolingandheating.com/services/heating-services/oil-furnace-installations/",
    "Oil Heating System Replacement": "https://ambientcoolingandheating.com/services/heating-services/oil-replacement/",
    "Heat Pump Installation": "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/",
    "Tankless Water Heater Installation": "https://ambientcoolingandheating.com/services/heating-services/tankless-water-heaters/",
    "Geothermal HVAC Installation": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
}
INTENT = {
    "install": re.compile(r"\binstall(s|ed|ing|ation|ations)?\b", re.I),
    "replace": re.compile(r"\breplac(e|es|ed|ing|ement|ements)\b", re.I),
    "repair": re.compile(r"\brepair(s|ed|ing)?\b", re.I),
    "service_maintenance": re.compile(r"\b(maintenance|tune[- ]up|servicing|service visit)\b", re.I),
    "oil": re.compile(r"\boil\b", re.I),          # \b stops 'boiler' matching
    "gas": re.compile(r"\bgas\b", re.I),
    "commercial": re.compile(r"\bcommercial\b", re.I),
    "residential": re.compile(r"\bresidential\b", re.I),
    "financing": re.compile(r"\b(financ\w+|payment plan|0% apr|monthly payments)\b", re.I),
}
CLAIMS = {
    "same_day": re.compile(r"\bsame[- ]day\b", re.I),
    "emergency_24_7": re.compile(r"\b(24/7|24-7|round[- ]the[- ]clock|emergency service)\b", re.I),
    "guarantee": re.compile(r"\bguarantee[ds]?\b", re.I),
    "most_trusted": re.compile(r"\bmost trusted\b", re.I),
    "best_or_top": re.compile(r"\b(best|top[- ]rated|top|#1|number one)\b", re.I),
    "most_knowledgeable": re.compile(r"\bmost knowledgeable\b", re.I),
    "free_estimate": re.compile(r"\bfree (estimate|consultation|quote)\b", re.I),
    "licensed_insured": re.compile(r"\blicen[cs]ed\b|\binsured\b", re.I),
    "experienced_expert": re.compile(r"\b(expert|experienced|specialist)s?\b", re.I),
}


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "parameterised_requests": 0, "forms_submitted": 0,
           "pages": {}}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for label, url in DEST.items():
            ctx = b.new_context(locale="en-US", timezone_id="America/New_York",
                                viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            rec = {"url": url}
            try:
                pg.goto(url, wait_until="domcontentloaded", timeout=70000)
                pg.wait_for_timeout(3000)
                # NitroPack defers JS until interaction
                pg.mouse.move(400, 300); pg.mouse.wheel(0, 1600)
                pg.keyboard.press("PageDown"); pg.wait_for_timeout(6000)
                pg.mouse.wheel(0, 3000); pg.wait_for_timeout(4000)
                txt = pg.evaluate("()=>document.body?document.body.innerText:''")
                rec["h1"] = pg.evaluate(
                    "()=>[...document.querySelectorAll('h1')].map(e=>e.innerText.trim())")
                rec["h2"] = pg.evaluate(
                    "()=>[...document.querySelectorAll('h2')].map(e=>e.innerText.trim()).slice(0,25)")
                rec["h3"] = pg.evaluate(
                    "()=>[...document.querySelectorAll('h3')].map(e=>e.innerText.trim()).slice(0,25)")
                rec["chars"] = len(txt)
                rec["text"] = txt
                rec["intent"] = {k: len(rx.findall(txt)) for k, rx in INTENT.items()}
                rec["claims"] = {k: rx.findall(txt)[:4] for k, rx in CLAIMS.items()
                                 if rx.search(txt)}
            except Exception as ex:
                rec["error"] = str(ex)[:200]
            finally:
                ctx.close()
            out["pages"][label] = rec
            print(f"\n=== {label} ===")
            print(f"  H1: {rec.get('h1')}")
            print(f"  chars={rec.get('chars')}  intent={rec.get('intent')}")
            print(f"  H2: {rec.get('h2')}")
            print(f"  claims present: {sorted((rec.get('claims') or {}).keys())}")
        b.close()
    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"page-copy-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
