#!/usr/bin/env python3
"""LOCATION_EXPANSION is 90% of raw clicks and 97.9% invalid, yet no LOCATION asset is
attached to the five campaigns. Find where it comes from, and check whether the clicks
Google KEPT actually convert before proposing anything."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}

print("=== A. ASSET SETS ON THE ACCOUNT ===")
for r in q(c, "SELECT asset_set.id, asset_set.name, asset_set.type, asset_set.status, "
              "asset_set.resource_name FROM asset_set"):
    a = r.asset_set
    print(f"  {a.id:<16}{E(a.type):<28}{E(a.status):<10}{a.name}")
    out.setdefault("asset_sets", []).append(
        {"id": str(a.id), "type": E(a.type), "status": E(a.status), "name": a.name})

print("\n=== B. ASSET SETS LINKED AT ACCOUNT LEVEL ===")
for r in q(c, "SELECT customer_asset_set.asset_set, customer_asset_set.status "
              "FROM customer_asset_set"):
    print(f"  {r.customer_asset_set.asset_set}  {E(r.customer_asset_set.status)}")
    out.setdefault("customer_asset_sets", []).append(
        {"asset_set": r.customer_asset_set.asset_set,
         "status": E(r.customer_asset_set.status)})

print("\n=== C. ASSET SETS LINKED TO THE FIVE CAMPAIGNS ===")
n = 0
for r in q(c, f"SELECT campaign.id, campaign_asset_set.asset_set, campaign_asset_set.status "
              f"FROM campaign_asset_set WHERE campaign.id IN ({IN5})"):
    n += 1
    print(f"  {NAME[str(r.campaign.id)]:<20}{r.campaign_asset_set.asset_set}  "
          f"{E(r.campaign_asset_set.status)}")
print(f"  campaign_asset_set links on the five: {n}")

print("\n=== D. IS A BUSINESS PROFILE LINKED TO THE ACCOUNT? ===")
try:
    for r in q(c, "SELECT customer.id, customer.descriptive_name, "
                  "customer.location_asset_auto_migration_done, "
                  "customer.image_asset_auto_migration_done FROM customer"):
        print(f"  {r.customer.descriptive_name}  "
              f"location_asset_auto_migration_done="
              f"{r.customer.location_asset_auto_migration_done}")
except Exception as e:
    print(f"  {type(e).__name__}: {str(e)[:140]}")

print("\n=== E. DO THE KEPT LOCATION_EXPANSION CLICKS CONVERT? ===")
print("  (memory: LOCATION_EXPANSION is not automatically waste - check before excluding)")
print(f"  {'campaign':<20}{'click_type':<22}{'clicks':>7}{'cost':>10}{'conv':>7}"
      f"{'allconv':>9}{'cost/conv':>11}")
tot = {}
for r in q(c, f"SELECT campaign.id, segments.click_type, metrics.clicks, metrics.cost_micros, "
              f"metrics.conversions, metrics.all_conversions FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' "
              f"AND '2026-09-09'"):
    m = r.metrics
    if not (m.clicks or m.cost_micros):
        continue
    t = E(r.segments.click_type)
    cost = m.cost_micros/1e6
    tot.setdefault(t, {"clicks": 0, "cost": 0.0, "conv": 0.0, "all": 0.0})
    tot[t]["clicks"] += m.clicks; tot[t]["cost"] += cost
    tot[t]["conv"] += m.conversions; tot[t]["all"] += m.all_conversions
    print(f"  {NAME[str(r.campaign.id)]:<20}{t:<22}{m.clicks:>7}{cost:>10.2f}"
          f"{m.conversions:>7.1f}{m.all_conversions:>9.1f}"
          f"{(f'{cost/m.conversions:.2f}' if m.conversions else '-'):>11}")
print(f"\n  {'ALL FIVE by click type':<42}{'clicks':>7}{'cost':>10}{'conv':>7}{'allconv':>9}"
      f"{'cost/conv':>11}")
for t, v in sorted(tot.items(), key=lambda z: -z[1]["cost"]):
    cpc_str = f"{v['cost']/v['conv']:.2f}" if v['conv'] else '-'
    print(f"  {t:<42}{v['clicks']:>7}{v['cost']:>10.2f}{v['conv']:>7.1f}{v['all']:>9.1f}"
          f"{cpc_str:>11}")
out["by_click_type"] = {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in tot.items()}

print("\n=== F. SHARE OF SPEND AND OF PRIMARY CONVERSIONS ===")
tc = sum(v["cost"] for v in tot.values()); tk = sum(v["conv"] for v in tot.values())
for t, v in sorted(tot.items(), key=lambda z: -z[1]["cost"]):
    print(f"  {t:<24}{100*v['cost']/tc:>6.1f}% of spend"
          f"{(100*v['conv']/tk if tk else 0):>8.1f}% of primary conversion records")

write(EVID / "2026-09-10-location-expansion-source.json", out)
