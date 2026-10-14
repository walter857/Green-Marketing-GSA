#!/usr/bin/env python3
"""Part 2: conversion actions, campaign x date CPC (the 09-04 ceiling test), conversion config."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

CONV_ONLY = "metrics.conversions, metrics.all_conversions, metrics.conversions_value, metrics.all_conversions_value"

print("=== CONVERSION ACTION CONFIGURATION (all, non-removed) ===")
ca = []
for r in q(c, """
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.type, conversion_action.category,
           conversion_action.primary_for_goal, conversion_action.counting_type,
           conversion_action.attribution_model_settings.attribution_model,
           conversion_action.click_through_lookback_window_days,
           conversion_action.view_through_lookback_window_days,
           conversion_action.value_settings.default_value,
           conversion_action.origin, conversion_action.owner_customer,
           conversion_action.phone_call_duration_seconds,
           metrics.all_conversions, metrics.all_conversions_value
    FROM conversion_action
    WHERE conversion_action.status != 'REMOVED'
      AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
"""):
    x = r.conversion_action
    ca.append({"id": str(x.id), "name": x.name, "status": E(x.status), "type": E(x.type_),
               "category": E(x.category), "primary_for_goal": x.primary_for_goal,
               "counting": E(x.counting_type), "origin": E(x.origin),
               "attribution": E(x.attribution_model_settings.attribution_model),
               "click_window": x.click_through_lookback_window_days,
               "phone_min_secs": x.phone_call_duration_seconds,
               "owner": x.owner_customer.split("/")[-1] if x.owner_customer else None,
               "all_conversions": round(r.metrics.all_conversions, 2)})
out["conversion_actions"] = ca
for x in sorted(ca, key=lambda x: -x["all_conversions"]):
    print(f"  {x['id']:>12} pfg={str(x['primary_for_goal']):<5} {x['category']:<22} {x['type']:<26} "
          f"cnt={x['counting']:<10} allconv={x['all_conversions']:<7} owner={x['owner']} {x['name'][:44]}")

print("\n=== conversion_action with ZERO delivery in window (config-only read) ===")
ca2 = []
for r in q(c, """
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.type, conversion_action.category,
           conversion_action.primary_for_goal, conversion_action.counting_type,
           conversion_action.phone_call_duration_seconds, conversion_action.owner_customer
    FROM conversion_action WHERE conversion_action.status != 'REMOVED'
"""):
    x = r.conversion_action
    ca2.append({"id": str(x.id), "name": x.name, "status": E(x.status), "type": E(x.type_),
                "category": E(x.category), "primary_for_goal": x.primary_for_goal,
                "counting": E(x.counting_type), "phone_min_secs": x.phone_call_duration_seconds,
                "owner": x.owner_customer.split("/")[-1] if x.owner_customer else None})
out["conversion_actions_config"] = ca2
print("non-removed conversion actions:", len(ca2))
print("  primary_for_goal=True:", sum(1 for x in ca2 if x["primary_for_goal"]))
for x in sorted(ca2, key=lambda x: (not x["primary_for_goal"], x["name"])):
    print(f"  {x['id']:>12} {x['status']:<8} pfg={str(x['primary_for_goal']):<5} "
          f"{x['category']:<24} {x['type']:<26} cnt={x['counting']:<10} "
          f"min_secs={x['phone_min_secs']:<4} owner={x['owner']} {x['name'][:40]}")

print("\n=== CONVERSIONS BY ACTION x CAMPAIGN (all time, conversions-only metrics) ===")
agg = defaultdict(lambda: {"conversions": 0.0, "all_conversions": 0.0})
for r in q(c, f"""
    SELECT campaign.id, segments.conversion_action_name, segments.conversion_action_category,
           {CONV_ONLY}
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
"""):
    k = (NAME[str(r.campaign.id)], r.segments.conversion_action_name,
         E(r.segments.conversion_action_category))
    agg[k]["conversions"] += r.metrics.conversions
    agg[k]["all_conversions"] += r.metrics.all_conversions
out["conversions_by_action_campaign"] = {str(k): {kk: round(vv, 2) for kk, vv in v.items()}
                                         for k, v in agg.items()}
for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["all_conversions"]):
    print(f"  {k[0]:<20} {k[2]:<22} conv={round(v['conversions'],2):<6} "
          f"allconv={round(v['all_conversions'],2):<7} {k[1][:44]}")

print("\n=== CAMPAIGN x DATE  (the 2026-09-04 CPC-ceiling before/after test) ===")
byd = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                           "conversions": 0.0, "all_conversions": 0.0})
for r in q(c, f"""
    SELECT campaign.id, segments.date, {METRICS}
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
"""):
    k = (r.segments.date, NAME[str(r.campaign.id)])
    for f in ("impressions", "clicks", "conversions", "all_conversions"):
        byd[k][f] += getattr(r.metrics, f)
    byd[k]["cost"] += r.metrics.cost_micros / 1e6
out["campaign_by_date"] = {f"{k[0]}|{k[1]}": {kk: round(vv, 2) for kk, vv in v.items()}
                           for k, v in byd.items()}
print(f"  {'date':<12}{'campaign':<20}{'impr':>6}{'clk':>5}{'cost':>10}{'cpc':>9}{'conv':>6}{'allc':>6}")
for k in sorted(byd):
    v = byd[k]
    cpc = v["cost"] / v["clicks"] if v["clicks"] else 0
    mark = "  <== ceiling set 16:56" if k[0] == "2026-09-04" else ""
    print(f"  {k[0]:<12}{k[1]:<20}{v['impressions']:>6}{v['clicks']:>5}"
          f"{round(v['cost'],2):>10}{round(cpc,2):>9}{round(v['conversions'],1):>6}"
          f"{round(v['all_conversions'],1):>6}{mark}")

print("\n=== BEFORE / AFTER the 2026-09-04 ceiling, per campaign (settled) ===")
for label, s, e in [("before 08-14..09-03", "2026-08-14", "2026-09-03"),
                    ("after  09-05..09-08", "2026-09-05", "2026-09-08")]:
    print(f"\n  {label}")
    a = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                             "conversions": 0.0, "all_conversions": 0.0})
    days = (3 if "after" in label else 21)
    for r in q(c, f"SELECT campaign.id, {METRICS} FROM campaign WHERE campaign.id IN ({IN5}) "
                  f"AND segments.date BETWEEN '{s}' AND '{e}'"):
        k = NAME[str(r.campaign.id)]
        for f in ("impressions", "clicks", "conversions", "all_conversions"):
            a[k][f] += getattr(r.metrics, f)
        a[k]["cost"] += r.metrics.cost_micros / 1e6
    for k, v in sorted(a.items()):
        cpc = v["cost"] / v["clicks"] if v["clicks"] else 0
        print(f"    {k:<20} impr={v['impressions']:<6} clk={v['clicks']:<4} "
              f"cost=${round(v['cost'],2):<9} cpc=${round(cpc,2):<8} "
              f"conv={round(v['conversions'],1):<5} allconv={round(v['all_conversions'],1):<6} "
              f"$/day=${round(v['cost']/days,2)}")

write(EVID / "2026-09-09-performance-2.json", out)
