#!/usr/bin/env python3
"""$106 average CPC against a $25 max-CPC ceiling cannot be a search click.
Decompose the spend by click type, network and invalid-click credit."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
W = "segments.date BETWEEN '2026-08-14' AND '2026-09-09'"

print("=== A. SPEND BY CLICK TYPE (campaign x segments.click_type) ===")
print(f"  {'campaign':<20}{'click_type':<28}{'cost':>10}{'clicks':>8}{'impr':>8}{'avgCPC':>9}")
tot = {}
for r in q(c, f"SELECT campaign.id, segments.click_type, metrics.cost_micros, metrics.clicks, "
              f"metrics.impressions FROM campaign WHERE campaign.id IN ({IN5}) AND {W}"):
    m = r.metrics
    if not m.impressions and not m.clicks and not m.cost_micros:
        continue
    cid = str(r.campaign.id)
    cpc = m.cost_micros/1e6/m.clicks if m.clicks else 0
    print(f"  {NAME[cid]:<20}{E(r.segments.click_type):<28}{m.cost_micros/1e6:>10.2f}"
          f"{m.clicks:>8}{m.impressions:>8}{cpc:>9.2f}")
    tot[E(r.segments.click_type)] = tot.get(E(r.segments.click_type), 0) + m.cost_micros/1e6
print(f"\n  spend by click type across all five: "
      f"{ {k: round(v,2) for k,v in sorted(tot.items(), key=lambda z:-z[1])} }")

print("\n=== B. NETWORK: is any of this Search Partners or Display? ===")
print(f"  {'campaign':<20}{'network':<32}{'cost':>10}{'clicks':>8}{'impr':>8}")
for r in q(c, f"SELECT campaign.id, segments.ad_network_type, metrics.cost_micros, "
              f"metrics.clicks, metrics.impressions FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND {W}"):
    m = r.metrics
    if not (m.impressions or m.clicks or m.cost_micros):
        continue
    print(f"  {NAME[str(r.campaign.id)]:<20}{E(r.segments.ad_network_type):<32}"
          f"{m.cost_micros/1e6:>10.2f}{m.clicks:>8}{m.impressions:>8}")

print("\n=== C. INVALID CLICKS: how many were reversed, and was the cost credited? ===")
print(f"  {'campaign':<20}{'clicks':>8}{'invalid':>9}{'invalid%':>10}{'cost':>10}")
for r in q(c, f"SELECT campaign.id, metrics.clicks, metrics.invalid_clicks, "
              f"metrics.invalid_click_rate, metrics.cost_micros FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND {W}"):
    m = r.metrics
    if not (m.clicks or m.invalid_clicks):
        continue
    print(f"  {NAME[str(r.campaign.id)]:<20}{m.clicks:>8}{m.invalid_clicks:>9}"
          f"{m.invalid_click_rate*100:>9.1f}%{m.cost_micros/1e6:>10.2f}")

print("\n=== D. AC REPAIR: what did each individual click actually cost? (click_view) ===")
n = 0
for d in [f"2026-08-{x:02d}" for x in range(14, 32)] + [f"2026-09-{x:02d}" for x in range(1, 10)]:
    try:
        for r in q(c, f"SELECT campaign.id, segments.date, segments.click_type, "
                      f"segments.device, segments.slot, metrics.clicks FROM click_view "
                      f"WHERE segments.date = '{d}' AND campaign.id = 24132507741"):
            n += 1
            print(f"  {r.segments.date}  {E(r.segments.click_type):<24}"
                  f"{E(r.segments.device):<10}{E(r.segments.slot)}")
    except Exception as e:
        print(f"  click_view {d}: {type(e).__name__}: {str(e)[:90]}")
        break
print(f"  AC Repair click_view rows in window: {n}")

print("\n=== E. IS THE CEILING ACTUALLY ENFORCED? top-of-page / abs-top bid estimates ===")
print(f"  {'campaign':<20}{'avgCPC':>9}{'topPageBid':>12}{'absTopBid':>11}")
for r in q(c, f"SELECT campaign.id, metrics.average_cpc, metrics.average_cpm, "
              f"metrics.top_impression_percentage, metrics.absolute_top_impression_percentage "
              f"FROM campaign WHERE campaign.id IN ({IN5}) AND {W}"):
    m = r.metrics
    print(f"  {NAME[str(r.campaign.id)]:<20}{m.average_cpc/1e6:>9.2f}"
          f"{m.top_impression_percentage*100:>11.1f}%{m.absolute_top_impression_percentage*100:>10.1f}%")
