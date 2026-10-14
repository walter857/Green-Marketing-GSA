#!/usr/bin/env python3
"""2026-09-16 LOCAL-ONLY unit economics for the Apogee Lawns CPC decision.

Reads the saved forecast JSON. No API call. Forecasts are Google's model, not a
promise of traffic or clicks.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "reports/apogee-lawns/evidence"
d = json.loads((EV / "2026-09-16-keyword-options.json").read_text(encoding="utf-8"))
fc = d["forecasts"]

SEASON = "season_2026-09-21_to_12-20"
PEAK = "peak_nov_2026-11-01_to_11-30"
CAPS = [4.00, 6.00, 8.00, 10.00, 13.00]
CR = [0.03, 0.05, 0.08, 0.10]

DAILY = 16.44
SEASON_DAYS = 91           # 2026-09-21 .. 2026-12-20 inclusive
SEASON_BUDGET = round(DAILY * SEASON_DAYS, 2)
PEAK_BUDGET = round(DAILY * 30, 2)

print("=" * 96)
print("1. AFFORDABLE CPC = target CPL x conservative click-to-lead rate")
print("=" * 96)
print(f"  {'target CPL':>11} | " + " | ".join(f"CR {int(r*100):>2}% -> max CPC" for r in CR))
for cpl in [50, 75, 100, 150, 200, 250, 300, 400, 500]:
    cells = " | ".join(f"{'':>8}${cpl*r:>7.2f}" for r in CR)
    print(f"  ${cpl:>10,} | {cells}")

print()
print("  Inverse read: what target CPL does a given CPC cap REQUIRE?")
print(f"  {'CPC cap':>8} | " + " | ".join(f"CR {int(r*100):>2}% needs CPL" for r in CR))
for cap in CAPS:
    cells = " | ".join(f"{'':>7}${cap/r:>8,.0f}" for r in CR)
    print(f"  ${cap:>7.2f} | {cells}")

print()
print("=" * 96)
print(f"2. SEASON FORECAST vs BUDGET  ({SEASON_DAYS} days, ${DAILY}/day = ${SEASON_BUDGET:,.2f} available)")
print("=" * 96)
for opt in ["A_quality_first", "B_head_exact_only", "B2_head_exact_plus_phrase", "A_plus_B_exact"]:
    print(f"\n  --- {opt} ---")
    print(f"  {'cap':>6} {'clicks':>8} {'cost':>9} {'avgCPC':>8} {'spend%':>7} | "
          + " ".join(f"{'lds@'+str(int(r*100))+'%':>9}" for r in CR))
    for cap in CAPS:
        r_ = fc[SEASON][opt][f"cap_{cap:.2f}"]
        if "error" in r_:
            print(f"  {cap:>6.2f}  ERROR")
            continue
        clicks, cost = r_["clicks"], r_["cost"]
        spend_pct = cost / SEASON_BUDGET * 100
        leads = [clicks * r for r in CR]
        cells = " ".join(f"{l:>9.2f}" for l in leads)
        print(f"  {cap:>6.2f} {clicks:>8.1f} {cost:>9.2f} {str(r_['avg_cpc']):>8} "
              f"{spend_pct:>6.1f}% | {cells}")

print()
print("=" * 96)
print("3. COST PER LEAD IMPLIED BY THE FORECAST (season, Option B head-exact-only)")
print("=" * 96)
print(f"  {'cap':>6} {'clicks':>8} {'cost':>9} | " + " | ".join(f"CPL @ {int(r*100)}%" for r in CR))
for cap in CAPS:
    r_ = fc[SEASON]["B_head_exact_only"][f"cap_{cap:.2f}"]
    if "error" in r_:
        continue
    clicks, cost = r_["clicks"], r_["cost"]
    cells = []
    for r in CR:
        leads = clicks * r
        cells.append(f"{'n/a':>10}" if leads < 0.01 else f"${cost/leads:>9,.0f}")
    print(f"  {cap:>6.2f} {clicks:>8.1f} {cost:>9.2f} | " + " | ".join(cells))

print()
print("  NOTE: at these click volumes a 'lead' is a fraction of a lead. Option B at an $8")
print("  cap models 11.0 clicks across the WHOLE 91-day season. At a 5% conversion rate")
print("  that is 0.55 leads. The honest read is that this campaign is a low-volume,")
print("  high-intent capture play, not a lead engine, and it cannot be judged on CPL")
print("  until it has accumulated far more than one season of clicks.")

print()
print("=" * 96)
print(f"4. PEAK-MONTH FORECAST (Nov 2026, 30 days, ${PEAK_BUDGET:,.2f} available)")
print("=" * 96)
print(f"  {'option':<28} {'cap':>6} {'clicks':>8} {'cost':>9} {'spend%':>7}")
for opt in ["A_quality_first", "B_head_exact_only", "B2_head_exact_plus_phrase", "A_plus_B_exact"]:
    for cap in CAPS:
        r_ = fc[PEAK][opt][f"cap_{cap:.2f}"]
        if "error" in r_:
            continue
        print(f"  {opt:<28} {cap:>6.2f} {r_['clicks']:>8.1f} {r_['cost']:>9.2f} "
              f"{r_['cost']/PEAK_BUDGET*100:>6.1f}%")

print()
print("=" * 96)
print("5. INTENT COMPOSITION REACHABLE BY A PHRASE HEAD KEYWORD")
print("=" * 96)
print(f"  ideas returned around the head term        : {d['ideas_count']}")
print(f"  terms a PHRASE head keyword would reach    : {d['phrase_reached_total']}")
print(f"    with a service-hiring marker             : {d['phrase_reached_service']}")
print(f"    with NO service-hiring marker            : {d['phrase_reached_nonservice']}")
sv = sum(x["avg"] or 0 for x in d["phrase_reached_nonservice_terms"])
print(f"  summed volume of the NO-service terms      : {sv}")
print("  Marker buckets across all 159 ideas:")
for k, v in sorted(d["intent_buckets"].items(), key=lambda kv: -kv[1]["vol"]):
    print(f"    {k:<14} terms={v['n']:>4}  summed_volume={v['vol']:>7}")
