#!/usr/bin/env python3
"""2026-09-16 READ-ONLY delta check against the recorded preflight state.

Every recorded finding is re-read and compared. No mutate call of any kind.
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, TZ, EVID, client, q, write, E  # noqa: E402

c = client()
out = {}
deltas: list[str] = []
same: list[str] = []


def cmp(label, expected, observed):
    ok = expected == observed
    (same if ok else deltas).append(f"{label}: expected={expected!r} observed={observed!r}")
    print(f"  [{'SAME ' if ok else 'DELTA'}] {label:<46} {observed!r}")
    return ok


print("=== A. IDENTITY + ACCOUNT SETTINGS ===")
row = q(c, """
    SELECT customer.id, customer.descriptive_name, customer.currency_code,
           customer.time_zone, customer.manager, customer.test_account,
           customer.status, customer.auto_tagging_enabled,
           customer.tracking_url_template, customer.final_url_suffix,
           customer.optimization_score,
           customer.call_reporting_setting.call_reporting_enabled,
           customer.call_reporting_setting.call_conversion_reporting_enabled,
           customer.call_reporting_setting.call_conversion_action,
           customer.conversion_tracking_setting.conversion_tracking_id,
           customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
           customer.conversion_tracking_setting.google_ads_conversion_customer,
           customer.conversion_tracking_setting.conversion_tracking_status,
           customer.conversion_tracking_setting.accepted_customer_data_terms,
           customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
           customer.customer_agreement_setting.accepted_lead_form_terms,
           customer.remarketing_setting.google_global_site_tag
    FROM customer
""")[0].customer
cts = row.conversion_tracking_setting
crs = row.call_reporting_setting

cmp("descriptive_name", EXACT_NAME, row.descriptive_name)
cmp("customer.id", CID, str(row.id))
cmp("currency_code", "USD", row.currency_code)
cmp("time_zone", "America/Chicago", row.time_zone)
cmp("manager", False, row.manager)
cmp("test_account", False, row.test_account)
cmp("status", "ENABLED", E(row.status))
cmp("auto_tagging_enabled", True, row.auto_tagging_enabled)
cmp("conversion_tracking_id", "18453077620", str(cts.conversion_tracking_id))
cmp("cross_account_conversion_tracking_id", "0", str(cts.cross_account_conversion_tracking_id))
cmp("google_ads_conversion_customer", CID,
    (cts.google_ads_conversion_customer or "").split("/")[-1])
cmp("conversion_tracking_status", "NOT_CONVERSION_TRACKED", E(cts.conversion_tracking_status))
cmp("accepted_customer_data_terms", False, cts.accepted_customer_data_terms)
cmp("enhanced_conversions_for_leads_enabled", False, cts.enhanced_conversions_for_leads_enabled)
cmp("accepted_lead_form_terms", False, row.customer_agreement_setting.accepted_lead_form_terms)
cmp("tracking_url_template", "", row.tracking_url_template)
cmp("final_url_suffix", "", row.final_url_suffix)

print("\n  -- call reporting state (account level) --")
print(f"    call_reporting_enabled            : {crs.call_reporting_enabled}")
print(f"    call_conversion_reporting_enabled : {crs.call_conversion_reporting_enabled}")
print(f"    call_conversion_action            : "
      f"{(crs.call_conversion_action or '(none)').split('/')[-1]}")
print("    call_recording_enabled            : NOT EXPOSED BY THE GOOGLE ADS API "
      "(no selectable customer.* field) -- UI-only check")
print("    advertiser_verification           : NOT EXPOSED BY THE GOOGLE ADS API "
      "-- UI-only check")

print("\n  -- AW destination proof (read-only) --")
gst = row.remarketing_setting.google_global_site_tag or ""
ids = sorted(set(re.findall(r"AW-\d+", gst)))
print(f"    google_global_site_tag length     : {len(gst)} chars")
print(f"    AW ids found in the tag           : {ids or '(none)'}")
cmp("AW destination", ["AW-18453077620"], ids)
out["aw_destination_observed"] = ids

links = {}
for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status "
              "FROM customer_manager_link"):
    links[x.customer_manager_link.manager_customer.split("/")[-1]] = E(
        x.customer_manager_link.status)
cmp(f"manager {GM_MANAGER} link", "ACTIVE", links.get(GM_MANAGER))

print("\n=== B. RESOURCE COUNTS ===")
COUNTS = {
    "campaigns": ("SELECT campaign.id FROM campaign", 0),
    "campaign_budgets": ("SELECT campaign_budget.id FROM campaign_budget", 0),
    "ad_groups": ("SELECT ad_group.id FROM ad_group", 0),
    "ad_group_criteria": ("SELECT ad_group_criterion.criterion_id FROM ad_group_criterion", 0),
    "ads": ("SELECT ad_group_ad.ad.id FROM ad_group_ad", 0),
    "conversion_actions": ("SELECT conversion_action.id FROM conversion_action", 0),
    "customer_conversion_goals": (
        "SELECT customer_conversion_goal.category FROM customer_conversion_goal", 0),
    "campaign_conversion_goals": (
        "SELECT campaign_conversion_goal.category FROM campaign_conversion_goal", 0),
    "custom_conversion_goals": (
        "SELECT custom_conversion_goal.id FROM custom_conversion_goal", 0),
    "conversion_value_rules": (
        "SELECT conversion_value_rule.id FROM conversion_value_rule", 0),
    "customer_assets": ("SELECT customer_asset.asset FROM customer_asset", 0),
    "campaign_assets": ("SELECT campaign_asset.asset FROM campaign_asset", 0),
    "ad_group_assets": ("SELECT ad_group_asset.asset FROM ad_group_asset", 0),
    "assets": ("SELECT asset.id FROM asset", 0),
    "asset_sets": ("SELECT asset_set.id FROM asset_set", 0),
    "labels": ("SELECT label.id FROM label", 0),
    "product_links_ga4_etc": (
        "SELECT product_link.product_link_id FROM product_link", 0),
    "recommendation_subscriptions": (
        "SELECT recommendation_subscription.type FROM recommendation_subscription", 0),
    "bidding_strategies": ("SELECT bidding_strategy.id FROM bidding_strategy", 0),
    "shared_sets": ("SELECT shared_set.id FROM shared_set", 7),
    "campaign_shared_sets": (
        "SELECT campaign_shared_set.shared_set FROM campaign_shared_set", 0),
    "shared_criteria": (
        "SELECT shared_criterion.criterion_id FROM shared_criterion", 4237),
    "account_negative_criteria": (
        "SELECT customer_negative_criterion.id FROM customer_negative_criterion", 1),
}
counts = {}
for label, (query, expect) in COUNTS.items():
    try:
        n = len(q(c, query))
    except Exception as exc:  # noqa: BLE001
        n = f"QUERY_FAILED:{type(exc).__name__}"
    counts[label] = n
    cmp(f"count {label}", expect, n)
out["counts"] = counts

print("\n=== C. CALL ASSETS specifically ===")
call_assets = q(c, "SELECT asset.id, asset.type, asset.call_asset.phone_number FROM asset "
                   "WHERE asset.type = CALL")
cmp("count CALL assets", 0, len(call_assets))

print("\n=== D. BILLING ===")
bs = []
for r in q(c, """
    SELECT billing_setup.id, billing_setup.status, billing_setup.start_date_time,
           billing_setup.end_date_time
    FROM billing_setup
"""):
    x = r.billing_setup
    bs.append({"id": str(x.id), "status": E(x.status), "start": x.start_date_time,
               "end": x.end_date_time})
    print(f"    {x.id} {E(x.status):<10} start={x.start_date_time} end={x.end_date_time or '-'}")
active = [b for b in bs if b["status"] in ("APPROVED", "APPROVED_HELD", "PENDING")]
cmp("billing setups total", 2, len(bs))
cmp("billing setups APPROVED/PENDING", 0, len(active))
cmp("account_budgets", 0, len(q(c, "SELECT account_budget.id FROM account_budget")))
out["billing_setup"] = bs

print("\n=== E. SHARED NEGATIVE LISTS (still unattached?) ===")
sets_ = {}
for r in q(c, "SELECT shared_set.id, shared_set.name, shared_set.status, "
              "shared_set.member_count, shared_set.reference_count FROM shared_set"):
    x = r.shared_set
    sets_[str(x.id)] = {"name": x.name, "status": E(x.status),
                        "members": x.member_count, "refs": x.reference_count}
    print(f"    {x.id:>12} {E(x.status):>8} refs={x.reference_count} "
          f"members={x.member_count:>5}  {x.name}")
cmp("shared lists with refs > 0", 0, sum(1 for v in sets_.values() if v["refs"] > 0))
out["shared_sets"] = sets_

print("\n=== F. LIFETIME DELIVERY ===")
life = None
for r in q(c, """
    SELECT metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
    FROM customer WHERE segments.date BETWEEN '2015-01-01' AND '2026-09-16'
"""):
    life = {"impr": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": round(r.metrics.cost_micros / 1e6, 2),
            "conv": round(r.metrics.conversions, 2)}
    break
life = life or {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0}
cmp("lifetime cost", 0.0, life["cost"])
cmp("lifetime clicks", 0, life["clicks"])
out["lifetime"] = life

print("\n=== G. RECENT CHANGES (change_status, bounded window) ===")
try:
    ch = q(c, """
        SELECT change_status.resource_type, change_status.resource_status,
               change_status.last_change_date_time
        FROM change_status
        WHERE change_status.last_change_date_time > '2026-09-01 00:00:00'
          AND change_status.last_change_date_time < '2026-09-17 00:00:00'
        ORDER BY change_status.last_change_date_time DESC
        LIMIT 200
    """)
    print(f"    change_status rows since 2026-09-01: {len(ch)}")
    for r in ch[:20]:
        x = r.change_status
        print(f"      {x.last_change_date_time}  {E(x.resource_type):<26} {E(x.resource_status)}")
    out["change_status_rows"] = len(ch)
except Exception as exc:  # noqa: BLE001
    print(f"    change_status query failed: {type(exc).__name__}: {str(exc)[:160]}")
    out["change_status_rows"] = "QUERY_FAILED"

print("\n" + "=" * 78)
print(f"DELTA CHECK: {len(same)} unchanged, {len(deltas)} CHANGED")
for d in deltas:
    print(f"  CHANGED -> {d}")
print("=" * 78)
out["deltas"] = deltas
out["unchanged_count"] = len(same)
out["checked_local"] = datetime.datetime.now(TZ).isoformat()
write(EVID / "2026-09-16-delta.json", out)
