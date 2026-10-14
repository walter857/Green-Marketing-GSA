#!/usr/bin/env python3
"""Change history reconstruction for the five Ambient campaigns, 2026-08-11..2026-09-09."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

print("=== CHANGE_EVENT 2026-08-11 .. 2026-09-09 (account-local time) ===")
rows = []
try:
    for r in q(c, """
        SELECT change_event.change_date_time, change_event.change_resource_type,
               change_event.change_resource_name, change_event.client_type,
               change_event.user_email, change_event.resource_change_operation,
               change_event.changed_fields, change_event.campaign, change_event.ad_group,
               change_event.new_resource, change_event.old_resource
        FROM change_event
        WHERE change_event.change_date_time >= '2026-08-11 00:00:00'
          AND change_event.change_date_time <= '2026-09-09 23:59:59'
        ORDER BY change_event.change_date_time DESC
        LIMIT 10000
    """):
        x = r.change_event
        rows.append({
            "ts": x.change_date_time,
            "resource_type": E(x.change_resource_type),
            "resource_name": x.change_resource_name,
            "client_type": E(x.client_type),
            "user_email": x.user_email,
            "op": E(x.resource_change_operation),
            "fields": list(x.changed_fields.paths) if x.changed_fields else [],
            "campaign": x.campaign.split("/")[-1] if x.campaign else None,
            "ad_group": x.ad_group.split("/")[-1] if x.ad_group else None,
            "new_cc_kw": x.new_resource.campaign_criterion.keyword.text or None,
            "new_cc_match": E(x.new_resource.campaign_criterion.keyword.match_type),
            "new_ceiling": x.new_resource.campaign.target_spend.cpc_bid_ceiling_micros or None,
            "old_ceiling": x.old_resource.campaign.target_spend.cpc_bid_ceiling_micros or None,
            "new_budget": x.new_resource.campaign_budget.amount_micros or None,
            "old_budget": x.old_resource.campaign_budget.amount_micros or None,
            "new_agc_status": E(x.new_resource.ad_group_criterion.status),
            "old_agc_status": E(x.old_resource.ad_group_criterion.status),
            "new_agc_kw": x.new_resource.ad_group_criterion.keyword.text or None,
        })
except Exception as e:
    print("change_event FAILED:", type(e).__name__, str(e)[:400])
out["change_events"] = rows
print("rows:", len(rows))
print("by resource_type:", dict(Counter(r["resource_type"] for r in rows)))
print("by client_type:", dict(Counter(r["client_type"] for r in rows)))
print("by op:", dict(Counter(r["op"] for r in rows)))
print("by date:", dict(Counter(r["ts"][:10] for r in rows)))

print("\n--- CAMPAIGN-level changes on the five (bid ceiling / settings) ---")
for r in rows:
    if r["resource_type"] == "CAMPAIGN" and r["campaign"] in FIVE:
        print(f"  {r['ts']} {NAME[r['campaign']]:<20} {r['op']:<7} {r['client_type']:<22} "
              f"fields={r['fields']} old_ceiling={r['old_ceiling']} new_ceiling={r['new_ceiling']}")

print("\n--- CAMPAIGN_BUDGET changes ---")
for r in rows:
    if r["resource_type"] == "CAMPAIGN_BUDGET":
        print(f"  {r['ts']} camp={r['campaign']} {r['op']:<7} {r['client_type']:<22} "
              f"fields={r['fields']} old=${(r['old_budget'] or 0)/1e6:.2f} new=${(r['new_budget'] or 0)/1e6:.2f}")

print("\n--- AD_GROUP_CRITERION changes on the five (positive keyword removals) ---")
n = 0
for r in rows:
    if r["resource_type"] == "AD_GROUP_CRITERION" and r["campaign"] in FIVE:
        n += 1
        if n <= 120:
            print(f"  {r['ts']} {NAME[r['campaign']]:<18} AG={r['ad_group']} {r['op']:<7} "
                  f"{r['client_type']:<22} {r['old_agc_status']}->{r['new_agc_status']} "
                  f"kw={r['new_agc_kw']!r} fields={r['fields']}")
print("  total AD_GROUP_CRITERION change rows on the five:", n)

print("\n--- CAMPAIGN_CRITERION changes on the five, by day and campaign ---")
cc = defaultdict(int)
for r in rows:
    if r["resource_type"] == "CAMPAIGN_CRITERION" and r["campaign"] in FIVE:
        cc[(r["ts"][:10], NAME[r["campaign"]], r["op"], r["client_type"])] += 1
for k, v in sorted(cc.items()):
    print(f"  {k[0]} {k[1]:<20} {k[2]:<7} {k[3]:<22} n={v}")

print("\n--- non-five, non-criterion changes (drift watch) ---")
for r in rows:
    if r["resource_type"] not in ("CAMPAIGN_CRITERION", "AD_GROUP_CRITERION") and r["campaign"] not in FIVE:
        print(f"  {r['ts']} {r['resource_type']:<22} camp={r['campaign']} {r['op']:<7} "
              f"{r['client_type']:<22} {r['resource_name'][-40:]} fields={r['fields']}")

write(EVID / "2026-09-09-change-history.json", out)
