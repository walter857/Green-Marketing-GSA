#!/usr/bin/env python3
"""Ambient | Verify PUBLISHED business hours from the client's own website.

READ-ONLY. No parameters, no forms, no tel activation.

client.yaml records three different things that are easy to confuse:
  expected_ad_schedule  "Mon-Fri 8:00 AM to 4:00 PM"  <- what was originally supplied
  verified_ad_schedule  "Mon-Fri 08:00-20:00 + Sat 08:00-13:00"  <- what is LIVE in the
                        account, created by a human in the Google Ads web client on
                        2026-08-17. That is an ADVERTISING schedule, not evidence of who
                        answers the phone.
  call_answering_hours_confirmed: false

The instruction is explicit: do not reuse the broader historical advertising schedule as if
it were verified answered hours. This reads the hours Ambient actually publishes.
"""
from __future__ import annotations
import sys, re, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-22"
PAGES = [
    "https://ambientcoolingandheating.com/contact-us/",
    "https://ambientcoolingandheating.com/",
    "https://ambientcoolingandheating.com/about-us/",
    "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
]
DAY = r"(mon|tues?|wed|thur?s?|fri|sat|sun)[a-z]*"
TIME = r"\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|AM|PM)"
HOUR_LINE = re.compile(rf"{DAY}[^\n]{{0,60}}?{TIME}\s*(?:-|–|—|to)\s*{TIME}", re.I)
CLOSED = re.compile(rf"{DAY}[^\n]{{0,30}}closed", re.I)
ALWAYS = re.compile(r"24/7|24-7|24 hours|around the clock|always open", re.I)
EMERGENCY = re.compile(r"emergency", re.I)


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "parameterised_requests": 0, "forms_submitted": 0,
           "pages": {}}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for u in PAGES:
            ctx = b.new_context(locale="en-US", timezone_id="America/New_York",
                                viewport={"width": 1366, "height": 900})
            pg = ctx.new_page()
            rec = {"url": u}
            try:
                r = pg.goto(u, wait_until="domcontentloaded", timeout=60000)
                rec["status"] = r.status if r else None
                pg.wait_for_timeout(2500)
                pg.mouse.wheel(0, 2000)
                pg.keyboard.press("End")
                pg.wait_for_timeout(5000)
                txt = pg.evaluate("()=>document.body?document.body.innerText:''")
                rec["hour_lines"] = sorted({m.group(0).strip()
                                            for m in HOUR_LINE.finditer(txt)})
                rec["closed_lines"] = sorted({m.group(0).strip()
                                              for m in CLOSED.finditer(txt)})
                rec["always_open_claims"] = sorted({m.group(0)
                                                    for m in ALWAYS.finditer(txt)})
                rec["emergency_mentions"] = len(EMERGENCY.findall(txt))
                # schema.org openingHours, if the theme emits it
                rec["schema_hours"] = pg.evaluate("""() => {
                  const out = [];
                  document.querySelectorAll('script[type="application/ld+json"]')
                    .forEach(s => { try {
                      const j = JSON.parse(s.textContent);
                      const walk = o => {
                        if (!o || typeof o !== 'object') return;
                        if (o.openingHours) out.push(JSON.stringify(o.openingHours));
                        if (o.openingHoursSpecification)
                          out.push(JSON.stringify(o.openingHoursSpecification));
                        Object.values(o).forEach(walk);
                      };
                      walk(j);
                    } catch(e){} });
                  return out;
                }""")
            except Exception as ex:
                rec["error"] = str(ex)[:200]
            finally:
                ctx.close()
            out["pages"][u] = rec
            print(f"\n=== {u} ===  status={rec.get('status')}")
            print(f"  hour lines      : {rec.get('hour_lines')}")
            print(f"  closed lines    : {rec.get('closed_lines')}")
            print(f"  schema hours    : {rec.get('schema_hours')}")
            print(f"  24/7 claims     : {rec.get('always_open_claims')}")
            print(f"  'emergency' hits: {rec.get('emergency_mentions')}")
        b.close()

    allhours = sorted({h for p in out["pages"].values() for h in p.get("hour_lines", [])})
    allschema = sorted({h for p in out["pages"].values() for h in p.get("schema_hours", [])})
    out["all_published_hour_lines"] = allhours
    out["all_schema_hours"] = allschema
    out["any_24_7_claim_on_site"] = any(p.get("always_open_claims")
                                        for p in out["pages"].values())
    print("\n=== CONSOLIDATED ===")
    print(f"  published hour lines: {allhours}")
    print(f"  schema openingHours : {allschema}")
    print(f"  any 24/7 claim      : {out['any_24_7_claim_on_site']}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"business-hours-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
