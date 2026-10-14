#!/usr/bin/env python3
"""Ambient | 2026-09-15 | asset, conversion, geo, schedule inventory for the five + commercial."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
CAMP, COMM_AG, RES_AG = "24132507747", "199748801029", "202339087634"
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
c = client(); identity_gate(c, verbose=False)

print("=== 1. CUSTOMER-LEVEL ASSETS ===")
ca = q(c, """
    SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status,
           asset.id, asset.name, asset.type, asset.final_urls,
           asset.policy_summary.approval_status,
           asset.call_asset.phone_number, asset.call_asset.country_code,
           asset.call_asset.call_conversion_reporting_state,
           asset.callout_asset.callout_text,
           asset.structured_snippet_asset.header,
           asset.structured_snippet_asset.values,
           asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
           asset.text_asset.text,
           asset.image_asset.full_size.url
    FROM customer_asset
""")
cal = []
for r in ca:
    a, x = r.asset, r.customer_asset
    cal.append({"asset_id": str(a.id), "field_type": E(x.field_type), "status": E(x.status),
                "type": E(a.type), "name": a.name or None,
                "approval": E(a.policy_summary.approval_status),
                "final_urls": list(a.final_urls) or None,
                "call_number": a.call_asset.phone_number or None,
                "callout": a.callout_asset.callout_text or None,
                "snippet_header": a.structured_snippet_asset.header or None,
                "snippet_values": list(a.structured_snippet_asset.values) or None,
                "sitelink_text": a.sitelink_asset.link_text or None,
                "text": a.text_asset.text or None,
                "image_url": a.image_asset.full_size.url or None})
    print(f"  {E(x.field_type):22s} {E(x.status):9s} asset={a.id:>14} {E(a.type):20s} "
          f"{(a.callout_asset.callout_text or a.sitelink_asset.link_text or a.call_asset.phone_number or a.text_asset.text or a.name or '')[:44]}")
out["customer_assets"] = cal

print("\n=== 2. CAMPAIGN ASSETS ON THE FIVE ===")
cma = q(c, f"""
    SELECT campaign.id, campaign.name, campaign_asset.asset, campaign_asset.field_type,
           campaign_asset.status, asset.id, asset.type, asset.name,
           asset.policy_summary.approval_status, asset.final_urls,
           asset.call_asset.phone_number, asset.call_asset.call_conversion_reporting_state,
           asset.callout_asset.callout_text,
           asset.structured_snippet_asset.header, asset.structured_snippet_asset.values,
           asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
           asset.sitelink_asset.description2,
           asset.text_asset.text,
           asset.image_asset.full_size.url,
           asset.image_asset.full_size.width_pixels,
           asset.image_asset.full_size.height_pixels
    FROM campaign_asset WHERE campaign.id IN ({IN5})
    ORDER BY campaign.name, campaign_asset.field_type
""")
cml = []
bycamp = defaultdict(list)
for r in cma:
    a, x = r.asset, r.campaign_asset
    label = (a.callout_asset.callout_text or a.sitelink_asset.link_text
             or a.call_asset.phone_number or a.text_asset.text
             or (a.structured_snippet_asset.header + ": " + ", ".join(a.structured_snippet_asset.values)
                 if a.structured_snippet_asset.header else "")
             or a.image_asset.full_size.url or a.name or "")
    rec = {"campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
           "asset_id": str(a.id), "field_type": E(x.field_type), "status": E(x.status),
           "type": E(a.type), "approval": E(a.policy_summary.approval_status),
           "final_urls": list(a.final_urls) or None, "label": label[:200],
           "sitelink_desc1": a.sitelink_asset.description1 or None,
           "sitelink_desc2": a.sitelink_asset.description2 or None,
           "call_reporting": E(a.call_asset.call_conversion_reporting_state)
           if a.call_asset.phone_number else None,
           "image_wh": f"{a.image_asset.full_size.width_pixels}x{a.image_asset.full_size.height_pixels}"
           if a.image_asset.full_size.url else None}
    cml.append(rec); bycamp[r.campaign.name].append(rec)
out["campaign_assets"] = cml
for cn, rows in bycamp.items():
    print(f"\n  --- {cn} ({len(rows)} assets) ---")
    for x in rows:
        print(f"    {x['field_type']:22s} {x['status']:9s} {x['approval']:12s} "
              f"asset={x['asset_id']:>14} {x['label'][:56]}")
        if x["final_urls"]:
            print(f"        -> {x['final_urls']}")

print("\n=== 3. AD-GROUP ASSETS (all ad groups in the five) ===")
aga = q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group.name, ad_group_asset.asset,
           ad_group_asset.field_type, ad_group_asset.status,
           asset.id, asset.type, asset.name,
           asset.policy_summary.approval_status, asset.final_urls,
           asset.callout_asset.callout_text, asset.sitelink_asset.link_text,
           asset.structured_snippet_asset.header, asset.structured_snippet_asset.values
    FROM ad_group_asset WHERE campaign.id IN ({IN5})
""")
agl = [{"ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
        "asset_id": str(r.asset.id), "field_type": E(r.ad_group_asset.field_type),
        "status": E(r.ad_group_asset.status), "type": E(r.asset.type),
        "approval": E(r.asset.policy_summary.approval_status),
        "label": (r.asset.callout_asset.callout_text or r.asset.sitelink_asset.link_text
                  or r.asset.structured_snippet_asset.header or r.asset.name or "")[:80]}
       for r in aga]
out["ad_group_assets"] = agl
print(f"  total ad-group asset links in the five campaigns: {len(agl)}")
for x in agl:
    print(f"    ag={x['ad_group_id']} {x['field_type']:20s} {x['status']:9s} {x['label'][:50]}")
print(f"  ON COMMERCIAL AD GROUP {COMM_AG}: "
      f"{sum(1 for x in agl if x['ad_group_id']==COMM_AG)}")

print("\n=== 4. CONVERSION ACTIONS (all) ===")
conv = q(c, """
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.type, conversion_action.category,
           conversion_action.primary_for_goal,
           conversion_action.counting_type,
           conversion_action.click_through_lookback_window_days,
           conversion_action.view_through_lookback_window_days,
           conversion_action.attribution_model_settings.attribution_model,
           conversion_action.value_settings.default_value,
           conversion_action.value_settings.always_use_default_value,
           conversion_action.origin, conversion_action.owner_customer
    FROM conversion_action ORDER BY conversion_action.name
""")
cvl = []
for r in conv:
    a = r.conversion_action
    cvl.append({"id": str(a.id), "name": a.name, "status": E(a.status), "type": E(a.type),
                "category": E(a.category), "primary_for_goal": a.primary_for_goal,
                "counting": E(a.counting_type),
                "ctw_days": a.click_through_lookback_window_days,
                "vtw_days": a.view_through_lookback_window_days,
                "attribution": E(a.attribution_model_settings.attribution_model),
                "default_value": a.value_settings.default_value,
                "always_default": a.value_settings.always_use_default_value,
                "origin": E(a.origin),
                "owner": a.owner_customer.split("/")[-1] if a.owner_customer else None})
    print(f"  {a.id:>14} {E(a.status):8s} primary={str(a.primary_for_goal):5s} "
          f"{E(a.counting_type):12s} {E(a.category):22s} {E(a.type):26s} {a.name[:44]}")
out["conversion_actions"] = cvl

print("\n=== 5. CUSTOMER CONVERSION GOALS + CAMPAIGN GOAL OVERRIDES ===")
try:
    ccg = q(c, """
        SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
               customer_conversion_goal.biddable FROM customer_conversion_goal
    """)
    g = [{"category": E(r.customer_conversion_goal.category),
          "origin": E(r.customer_conversion_goal.origin),
          "biddable": r.customer_conversion_goal.biddable} for r in ccg]
    out["customer_conversion_goals"] = g
    for x in g:
        if x["biddable"]:
            print(f"  BIDDABLE  {x['category']:24s} {x['origin']}")
    print(f"  total goal rows: {len(g)}  biddable: {sum(1 for x in g if x['biddable'])}")
except Exception as ex:
    print("  ERR", str(ex)[:200])
try:
    ccg2 = q(c, f"""
        SELECT campaign.id, campaign.name,
               campaign_conversion_goal.category, campaign_conversion_goal.origin,
               campaign_conversion_goal.biddable
        FROM campaign_conversion_goal WHERE campaign.id IN ({IN5})
    """)
    g2 = [{"campaign_id": str(r.campaign.id),
           "category": E(r.campaign_conversion_goal.category),
           "origin": E(r.campaign_conversion_goal.origin),
           "biddable": r.campaign_conversion_goal.biddable} for r in ccg2]
    out["campaign_conversion_goals"] = g2
    bid = [x for x in g2 if x["biddable"]]
    print(f"  campaign-level goal rows: {len(g2)}  biddable: {len(bid)}")
    for x in bid:
        print(f"    camp {x['campaign_id']} BIDDABLE {x['category']} {x['origin']}")
except Exception as ex:
    print("  ERR", str(ex)[:200])

print("\n=== 6. AD SCHEDULE + GEO on campaign 24132507747 ===")
sched = q(c, f"""
    SELECT campaign_criterion.criterion_id, campaign_criterion.ad_schedule.day_of_week,
           campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.start_minute,
           campaign_criterion.ad_schedule.end_hour, campaign_criterion.ad_schedule.end_minute,
           campaign_criterion.status, campaign_criterion.negative
    FROM campaign_criterion WHERE campaign.id = {CAMP}
      AND campaign_criterion.type = AD_SCHEDULE
""")
sl = [{"criterion_id": str(r.campaign_criterion.criterion_id),
       "day": E(r.campaign_criterion.ad_schedule.day_of_week),
       "start": f"{r.campaign_criterion.ad_schedule.start_hour}:{E(r.campaign_criterion.ad_schedule.start_minute)}",
       "end": f"{r.campaign_criterion.ad_schedule.end_hour}:{E(r.campaign_criterion.ad_schedule.end_minute)}",
       "status": E(r.campaign_criterion.status),
       "negative": r.campaign_criterion.negative} for r in sched]
out["ad_schedule_24132507747"] = sl
for x in sl:
    print(f"  {x['day']:10s} {x['start']:8s} -> {x['end']:8s} {x['status']} neg={x['negative']}")
print(f"  rows: {len(sl)}")

geo = q(c, f"""
    SELECT campaign_criterion.criterion_id, campaign_criterion.location.geo_target_constant,
           campaign_criterion.negative, campaign_criterion.status, campaign_criterion.type
    FROM campaign_criterion WHERE campaign.id = {CAMP}
      AND campaign_criterion.type IN (LOCATION, PROXIMITY)
""")
gpos = [r for r in geo if not r.campaign_criterion.negative]
gneg = [r for r in geo if r.campaign_criterion.negative]
out["geo_positive_count"] = len(gpos)
out["geo_negative_count"] = len(gneg)
print(f"  geo targets on {CAMP}: positive={len(gpos)} negative={len(gneg)}")

print("\n=== 7. ALL ADS IN THE FIVE (policy + status) ===")
ads = q(c, f"""
    SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id, campaign.name,
           ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status,
           ad_group_ad.policy_summary.policy_topic_entries,
           ad_group_ad.ad.final_urls, ad_group_ad.ad_strength,
           ad_group_ad.ad.responsive_search_ad.path1,
           ad_group_ad.ad.responsive_search_ad.path2
    FROM ad_group_ad WHERE campaign.id IN ({IN5})
    ORDER BY campaign.name, ad_group.name
""")
al = []
for r in ads:
    a = r.ad_group_ad
    al.append({"campaign_id": str(r.campaign.id), "ad_group_id": str(r.ad_group.id),
               "ad_group_name": r.ad_group.name, "ad_group_status": E(r.ad_group.status),
               "ad_id": str(a.ad.id), "status": E(a.status), "type": E(a.ad.type),
               "approval": E(a.policy_summary.approval_status),
               "review": E(a.policy_summary.review_status),
               "topics": [t.topic for t in a.policy_summary.policy_topic_entries],
               "final_urls": list(a.ad.final_urls),
               "strength": E(a.ad_strength),
               "path1": a.ad.responsive_search_ad.path1 or None,
               "path2": a.ad.responsive_search_ad.path2 or None})
out["all_ads"] = al
from collections import Counter
print("  by (ad_group_status, ad status, approval):",
      Counter((x["ad_group_status"], x["status"], x["approval"]) for x in al).most_common())
print(f"  total ad rows: {len(al)}")
for x in al:
    if x["ad_group_status"] != "REMOVED" and x["status"] != "REMOVED":
        print(f"    ag={x['ad_group_id']} {x['ad_group_name'][:34]:34s} ad={x['ad_id']} "
              f"{x['status']:8s} {x['approval']:12s} {x['review']:22s} "
              f"str={x['strength']:12s} {x['topics']} {x['final_urls']}")

p = SNAP / f"assets-and-conversions-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
