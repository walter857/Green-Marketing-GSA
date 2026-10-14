#!/usr/bin/env python3
"""Read-only preconditions audit for the call-asset / website-call delta plans."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, client, q, E  # noqa: E402

c = client()
def hdr(t): print("\n" + "=" * 74 + "\n" + t + "\n" + "=" * 74)

hdr("IDENTITY")
r = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
                   customer.test_account, customer.time_zone,
                   customer.call_reporting_setting.call_reporting_enabled,
                   customer.call_reporting_setting.call_conversion_reporting_enabled,
                   customer.call_reporting_setting.call_conversion_action
            FROM customer""")[0].customer
print(f"  {r.id} | {r.descriptive_name} | mgr={r.manager} test={r.test_account} tz={r.time_zone}")
crs = r.call_reporting_setting
print(f"  call_reporting_enabled={crs.call_reporting_enabled} "
      f"call_conversion_reporting_enabled={crs.call_conversion_reporting_enabled}")
print(f"  account-level call_conversion_action='{crs.call_conversion_action}'")

hdr("CONVERSION ACTIONS")
for x in q(c, """SELECT conversion_action.id, conversion_action.name, conversion_action.type,
                        conversion_action.category, conversion_action.origin,
                        conversion_action.status, conversion_action.primary_for_goal,
                        conversion_action.phone_call_duration_seconds,
                        conversion_action.include_in_conversions_metric
                 FROM conversion_action ORDER BY conversion_action.id"""):
    a = x.conversion_action
    print(f"  {a.id} {E(a.type_):<13} {E(a.category):<17} {E(a.origin):<14} "
          f"primary={str(a.primary_for_goal):<5} dur={a.phone_call_duration_seconds}s "
          f"in_conv={a.include_in_conversions_metric} | {a.name}")

hdr("ASSETS (all) + CALL assets")
ass = q(c, "SELECT asset.id, asset.type, asset.name FROM asset ORDER BY asset.id")
from collections import Counter
print("  by type:", dict(Counter(E(x.asset.type_) for x in ass)), " total:", len(ass))
calls = q(c, """SELECT asset.id, asset.call_asset.phone_number,
                       asset.call_asset.country_code,
                       asset.call_asset.call_conversion_reporting_state,
                       asset.call_asset.call_conversion_action
                FROM asset WHERE asset.type = 'CALL'""")
print(f"  CALL assets: {len(calls)}")
for x in calls:
    ca = x.asset.call_asset
    print(f"    {x.asset.id} {ca.country_code} {ca.phone_number} "
          f"{E(ca.call_conversion_reporting_state)} -> {ca.call_conversion_action}")

hdr("CAMPAIGN + CAMPAIGN ASSETS")
for x in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                        campaign.advertising_channel_type
                 FROM campaign"""):
    cm = x.campaign
    print(f"  {cm.id} {E(cm.status):<8} {E(cm.advertising_channel_type):<8} {cm.name}")
cas = q(c, """SELECT campaign_asset.campaign, campaign_asset.asset,
                     campaign_asset.field_type, campaign_asset.status
              FROM campaign_asset ORDER BY campaign_asset.field_type""")
print(f"  campaign_asset links: {len(cas)}")
print("  by field_type:", dict(Counter(E(x.campaign_asset.field_type) for x in cas)))
print(f"  CALL field_type links: "
      f"{sum(1 for x in cas if E(x.campaign_asset.field_type) == 'CALL')}")

hdr("CAMPAIGN CRITERIA — ad schedule")
sched = q(c, """SELECT campaign_criterion.criterion_id, campaign_criterion.ad_schedule.day_of_week,
                       campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour
                FROM campaign_criterion WHERE campaign_criterion.type = 'AD_SCHEDULE'""")
print(f"  ad_schedule criteria: {len(sched)}  (0 == campaign runs 24/7, by design)")

hdr("CAMPAIGN CONVERSION GOALS")
for x in q(c, """SELECT campaign_conversion_goal.category, campaign_conversion_goal.origin,
                        campaign_conversion_goal.biddable FROM campaign_conversion_goal"""):
    g = x.campaign_conversion_goal
    print(f"  {E(g.category):<17} {E(g.origin):<14} biddable={g.biddable}")
print(f"  custom_conversion_goals: {len(q(c, 'SELECT custom_conversion_goal.id FROM custom_conversion_goal'))}")

hdr("MANAGER LINK")
for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status FROM customer_manager_link"):
    l = x.customer_manager_link
    print(f"  {l.manager_customer.split('/')[-1]} {E(l.status)}")
print("\nAUDIT COMPLETE — zero mutations issued.")
