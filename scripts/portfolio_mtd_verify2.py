#!/usr/bin/env python3
"""Second verification pass: conversion inclusion flags + zero-delivery causes. Read-only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client

load_dotenv_if_available(ROOT / ".env")
client = load_google_ads_client()
svc = client.get_service("GoogleAdsService")

ACCTS = [
    ("2401959466", "Ambient Cooling"),
    ("3451131960", "Beaver bins"),
    ("7478932848", "EKG Lawn Services"),
    ("9487471092", "MasterGrass"),
    ("1837139601", "Nolte & Son's"),
    ("7380491929", "Pro Green - Austin"),
    ("5587528194", "Ray Lawns"),
    ("2429758629", "Softwind Landscape & Masonry"),
    ("1521725229", "Softwind Power Washing"),
]

print("=" * 100)
print("CONVERSION ACTION SETUP: which actions actually feed the Conversions column / bidding")
print("=" * 100)
for cid, nm in ACCTS:
    print(f"\n## {nm} ({cid})")
    try:
        rows = list(svc.search(
            customer_id=cid,
            query="SELECT conversion_action.name, conversion_action.status, "
                  "conversion_action.type, conversion_action.category, "
                  "conversion_action.primary_for_goal, "
                  "conversion_action.include_in_conversions_metric "
                  "FROM conversion_action WHERE conversion_action.status = 'ENABLED'"))
    except Exception as exc:  # noqa: BLE001
        print("  ERROR:", str(exc)[:200])
        continue
    counted = [r for r in rows if r.conversion_action.include_in_conversions_metric]
    print(f"  enabled actions={len(rows)}  counted in 'Conversions'={len(counted)}")
    for r in counted:
        ca = r.conversion_action
        print(f"    [COUNTED ] {ca.name[:46]:46s} {ca.type_.name[:22]:22s} "
              f"cat={ca.category.name[:16]:16s} primary={ca.primary_for_goal}")
    for r in rows:
        ca = r.conversion_action
        if not ca.include_in_conversions_metric:
            print(f"    [excluded] {ca.name[:46]:46s} {ca.type_.name[:22]:22s} "
                  f"cat={ca.category.name[:16]:16s} primary={ca.primary_for_goal}")

print("\n" + "=" * 100)
print("GREENWAY LAWN CARE (1491333698): why is an ENABLED+SERVING campaign spending $0?")
print("=" * 100)
for q, label in [
    ("SELECT campaign.name, ad_group.name, ad_group.status, ad_group_ad.status, "
     "ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, "
     "ad_group_ad.ad.type FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'", "ADS + POLICY"),
    ("SELECT campaign.name, metrics.impressions, metrics.cost_micros "
     "FROM campaign WHERE segments.date DURING LAST_30_DAYS", "LAST 30 DAYS DELIVERY"),
    ("SELECT billing_setup.status, billing_setup.payments_account_info.payments_account_name "
     "FROM billing_setup", "BILLING SETUP"),
]:
    print(f"\n--- {label} ---")
    try:
        n = 0
        for r in svc.search(customer_id="1491333698", query=q):
            n += 1
            if label == "ADS + POLICY":
                print(f"  {r.campaign.name[:26]:26s} | {r.ad_group.name[:20]:20s} | "
                      f"ag={r.ad_group.status.name:8s} ad={r.ad_group_ad.status.name:8s} "
                      f"approval={r.ad_group_ad.policy_summary.approval_status.name} "
                      f"review={r.ad_group_ad.policy_summary.review_status.name}")
            elif label == "LAST 30 DAYS DELIVERY":
                print(f"  {r.campaign.name[:34]:34s} impr={r.metrics.impressions} "
                      f"cost=${r.metrics.cost_micros/1e6:,.2f}")
            else:
                print(f"  {r.billing_setup.status.name} "
                      f"{r.billing_setup.payments_account_info.payments_account_name}")
        if n == 0:
            print("  (0 rows)")
    except Exception as exc:  # noqa: BLE001
        print("  ERROR:", str(exc)[:200])
