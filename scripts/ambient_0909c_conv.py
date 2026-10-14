#!/usr/bin/env python3
"""CONVERSION RECONCILIATION - the gate for every CPC decision in this run.

Reads all four goal layers, then daily rows segmented simultaneously by
date x campaign x conversion action, returning conversions AND all_conversions
separately. Proves or retracts every headline conversion figure.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}

print("=== 0. IDENTITY GATE ===")
ident = identity_gate(c)
out["identity"] = ident["checks"]

print("\n=== 0b. ACCOUNT CLOCK ===")
t = q(c, "SELECT segments.date, metrics.impressions, metrics.cost_micros FROM customer "
         "WHERE segments.date DURING TODAY")
y = q(c, "SELECT segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros "
         "FROM customer WHERE segments.date DURING YESTERDAY")
today = t[0].segments.date if t else None
yest = y[0].segments.date if y else None
print(f"  TODAY (partial)  : {today}  impr={t[0].metrics.impressions if t else 0} "
      f"cost=${(t[0].metrics.cost_micros/1e6) if t else 0:.2f}")
print(f"  YESTERDAY        : {yest}  impr={y[0].metrics.impressions if y else 0} "
      f"clicks={y[0].metrics.clicks if y else 0} "
      f"cost=${(y[0].metrics.cost_micros/1e6) if y else 0:.2f}")
LAST_SETTLED = yest or "2026-09-08"
out["today_partial"] = today
out["last_settled"] = LAST_SETTLED
print(f"  -> LATEST SETTLED DATE USED THROUGHOUT: {LAST_SETTLED}")

# ---------------------------------------------------------------- LAYER 1
print("\n=== 1. LAYER 1: customer.conversion_tracking_setting ===")
r = q(c, "SELECT customer.conversion_tracking_setting.conversion_tracking_id, "
         "customer.conversion_tracking_setting.google_ads_conversion_customer, "
         "customer.conversion_tracking_setting.cross_account_conversion_tracking_id, "
         "customer.conversion_tracking_setting.accepted_customer_data_terms, "
         "customer.conversion_tracking_setting.conversion_tracking_status, "
         "customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled "
         "FROM customer")[0].customer.conversion_tracking_setting
l1 = {"conversion_tracking_id": str(r.conversion_tracking_id),
      "google_ads_conversion_customer": r.google_ads_conversion_customer,
      "cross_account_conversion_tracking_id": str(r.cross_account_conversion_tracking_id),
      "accepted_customer_data_terms": r.accepted_customer_data_terms,
      "conversion_tracking_status": E(r.conversion_tracking_status),
      "enhanced_conversions_for_leads_enabled": r.enhanced_conversions_for_leads_enabled}
out["layer1_customer"] = l1
for k, v in l1.items():
    print(f"  {k}: {v}")

# ---------------------------------------------------------------- LAYER 2
print("\n=== 2. LAYER 2: conversion_goal_campaign_config (goal_config_level) ===")
l2 = []
for x in q(c, f"SELECT campaign.id, conversion_goal_campaign_config.goal_config_level, "
              f"conversion_goal_campaign_config.custom_conversion_goal "
              f"FROM conversion_goal_campaign_config WHERE campaign.id IN ({IN5})"):
    g = x.conversion_goal_campaign_config
    l2.append({"campaign": NAME[str(x.campaign.id)], "campaign_id": str(x.campaign.id),
               "goal_config_level": E(g.goal_config_level),
               "custom_conversion_goal": g.custom_conversion_goal or None})
out["layer2_goal_config_level"] = l2
for x in l2:
    print(f"  {x['campaign']:<20} goal_config_level={x['goal_config_level']:<10} "
          f"custom_goal={x['custom_conversion_goal']}")
levels = {x["goal_config_level"] for x in l2}
print(f"  -> distinct levels: {levels}")
print("     CUSTOMER level means customer_conversion_goal governs. CAMPAIGN level means")
print("     campaign_conversion_goal governs and customer-level edits are NOT applied.")

# ---------------------------------------------------------------- LAYER 3
print("\n=== 3. LAYER 3: customer_conversion_goal (biddable state) ===")
l3 = []
for x in q(c, "SELECT customer_conversion_goal.category, customer_conversion_goal.origin, "
              "customer_conversion_goal.biddable FROM customer_conversion_goal"):
    g = x.customer_conversion_goal
    l3.append({"category": E(g.category), "origin": E(g.origin), "biddable": g.biddable})
out["layer3_customer_conversion_goal"] = l3
for x in sorted(l3, key=lambda z: (not z["biddable"], z["category"])):
    flag = "BIDDABLE" if x["biddable"] else "not biddable"
    print(f"  {x['category']:<24} {x['origin']:<24} {flag}")

print("\n=== 3b. campaign_conversion_goal on the five ===")
l3b = []
try:
    for x in q(c, f"SELECT campaign.id, campaign_conversion_goal.category, "
                  f"campaign_conversion_goal.origin, campaign_conversion_goal.biddable "
                  f"FROM campaign_conversion_goal WHERE campaign.id IN ({IN5})"):
        g = x.campaign_conversion_goal
        l3b.append({"campaign": NAME[str(x.campaign.id)], "category": E(g.category),
                    "origin": E(g.origin), "biddable": g.biddable})
except Exception as e:
    print("  campaign_conversion_goal read failed:", type(e).__name__, str(e)[:160])
out["layer3b_campaign_conversion_goal"] = l3b
bidd = [x for x in l3b if x["biddable"]]
print(f"  rows: {len(l3b)}  biddable rows: {len(bidd)}")
for x in sorted(bidd, key=lambda z: (z["campaign"], z["category"])):
    print(f"    {x['campaign']:<20} {x['category']:<24} {x['origin']:<24} BIDDABLE")

# ---------------------------------------------------------------- LAYER 4
print("\n=== 4. LAYER 4: conversion_action full field set ===")
ca = []
for x in q(c, "SELECT conversion_action.id, conversion_action.resource_name, "
              "conversion_action.name, conversion_action.status, conversion_action.category, "
              "conversion_action.type, conversion_action.primary_for_goal, "
              "conversion_action.include_in_conversions_metric, "
              "conversion_action.counting_type, conversion_action.owner_customer, "
              "conversion_action.origin, conversion_action.click_through_lookback_window_days, "
              "conversion_action.phone_call_duration_seconds "
              "FROM conversion_action WHERE conversion_action.status != 'REMOVED'"):
    a = x.conversion_action
    ca.append({"id": str(a.id), "resource_name": a.resource_name, "name": a.name,
               "status": E(a.status), "category": E(a.category), "type": E(a.type_),
               "primary_for_goal": a.primary_for_goal,
               "include_in_conversions_metric": a.include_in_conversions_metric,
               "counting_type": E(a.counting_type),
               "owner_customer": a.owner_customer.split("/")[-1] if a.owner_customer else None,
               "origin": E(a.origin),
               "click_window_days": a.click_through_lookback_window_days,
               "phone_call_duration_seconds": a.phone_call_duration_seconds})
out["layer4_conversion_actions"] = ca
FOCUS = {"1068114183", "6885463625", "7643656486"}
print(f"  non-removed conversion actions: {len(ca)}")
print(f"\n  {'id':<12}{'pfg':<6}{'incl':<6}{'counting':<15}{'category':<20}{'type':<26}name")
for a in sorted(ca, key=lambda z: (not z["primary_for_goal"], z["name"])):
    mark = "  <<<" if a["id"] in FOCUS else ""
    print(f"  {a['id']:<12}{str(a['primary_for_goal']):<6}"
          f"{str(a['include_in_conversions_metric']):<6}{a['counting_type']:<15}"
          f"{a['category']:<20}{a['type']:<26}{a['name'][:40]}{mark}")

print("\n  --- REQUIRED DETAIL FOR THE THREE NAMED ACTIONS ---")
for a in ca:
    if a["id"] in FOCUS:
        print(f"\n  {a['name']}")
        for k in ("id", "resource_name", "name", "status", "category", "type",
                  "primary_for_goal", "include_in_conversions_metric", "counting_type",
                  "owner_customer", "origin", "click_window_days",
                  "phone_call_duration_seconds"):
            print(f"      {k:<32} {a[k]}")

# ---------------------------------------------------------------- DAILY
print(f"\n=== 5. DAILY ROWS 2026-08-18 .. {LAST_SETTLED}, "
      f"segmented date x campaign x conversion action ===")
rows = []
for x in q(c, f"""
    SELECT segments.date, campaign.id, campaign.name,
           segments.conversion_action, segments.conversion_action_name,
           segments.conversion_action_category,
           metrics.conversions, metrics.all_conversions,
           metrics.conversions_value, metrics.all_conversions_value
    FROM campaign
    WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-18' AND '{LAST_SETTLED}'
"""):
    rows.append({"date": x.segments.date, "campaign_id": str(x.campaign.id),
                 "campaign": NAME[str(x.campaign.id)],
                 "action_id": x.segments.conversion_action.split("/")[-1],
                 "action_name": x.segments.conversion_action_name,
                 "category": E(x.segments.conversion_action_category),
                 "conversions": round(x.metrics.conversions, 2),
                 "all_conversions": round(x.metrics.all_conversions, 2)})
out["daily_rows"] = rows
print(f"  rows returned: {len(rows)}")
print(f"  TOTAL metrics.conversions     = {sum(r['conversions'] for r in rows):.2f}")
print(f"  TOTAL metrics.all_conversions = {sum(r['all_conversions'] for r in rows):.2f}")
print("  (these are different columns and are never summed together)")

print(f"\n  --- EVERY ROW WITH A NON-ZERO VALUE IN EITHER COLUMN ---")
print(f"  {'date':<12}{'campaign':<20}{'action_id':<14}{'PRIMARY':>9}{'ALL':>8}  action")
for r in sorted([r for r in rows if r["conversions"] or r["all_conversions"]],
                key=lambda r: (r["date"], r["campaign"], r["action_name"])):
    star = " *" if r["conversions"] == 0 and r["all_conversions"] > 0 else "  "
    print(f"  {r['date']:<12}{r['campaign']:<20}{r['action_id']:<14}"
          f"{r['conversions']:>9.2f}{r['all_conversions']:>8.2f}{star}{r['action_name'][:38]}")
print("  * = recorded in All conversions but NOT in the Primary Conversions column")

print("\n=== 6. PER-ACTION TOTALS, BOTH COLUMNS ===")
byact = defaultdict(lambda: {"conversions": 0.0, "all_conversions": 0.0})
for r in rows:
    byact[(r["action_id"], r["action_name"])]["conversions"] += r["conversions"]
    byact[(r["action_id"], r["action_name"])]["all_conversions"] += r["all_conversions"]
print(f"  {'action_id':<14}{'PRIMARY':>9}{'ALL':>9}  name")
for k, v in sorted(byact.items(), key=lambda kv: -kv[1]["all_conversions"]):
    if v["conversions"] or v["all_conversions"]:
        print(f"  {k[0]:<14}{v['conversions']:>9.2f}{v['all_conversions']:>9.2f}  {k[1][:46]}")
out["per_action_totals"] = {f"{k[0]}|{k[1]}": {a: round(b, 2) for a, b in v.items()}
                            for k, v in byact.items()}

print("\n=== 7. WC LEAD (7643656486) DAY BY DAY ===")
wc = [r for r in rows if r["action_id"] == "7643656486"
      and (r["conversions"] or r["all_conversions"])]
print(f"  {'date':<12}{'campaign':<20}{'PRIMARY':>9}{'ALL':>8}")
for r in sorted(wc, key=lambda r: (r["date"], r["campaign"])):
    print(f"  {r['date']:<12}{r['campaign']:<20}{r['conversions']:>9.2f}"
          f"{r['all_conversions']:>8.2f}")
pre = [r for r in wc if r["date"] <= "2026-08-21"]
post = [r for r in wc if r["date"] > "2026-08-21"]
print(f"\n  on/before 2026-08-21 : PRIMARY={sum(r['conversions'] for r in pre):.2f} "
      f"ALL={sum(r['all_conversions'] for r in pre):.2f}  ({len(pre)} rows)")
print(f"  after     2026-08-21 : PRIMARY={sum(r['conversions'] for r in post):.2f} "
      f"ALL={sum(r['all_conversions'] for r in post):.2f}  ({len(post)} rows)")
out["wc_lead_split"] = {
    "on_or_before_2026_08_21": {"primary": round(sum(r["conversions"] for r in pre), 2),
                                "all": round(sum(r["all_conversions"] for r in pre), 2),
                                "rows": len(pre)},
    "after_2026_08_21": {"primary": round(sum(r["conversions"] for r in post), 2),
                         "all": round(sum(r["all_conversions"] for r in post), 2),
                         "rows": len(post)}}

write(EVID / "2026-09-09c-conversion-reconciliation.json", out)
