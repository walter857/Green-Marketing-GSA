#!/usr/bin/env python3
"""Ambient | 2026-09-30c | READ-ONLY checks for the Heating Repair containment package. No mutations. No PII printed.

1. Fresh identity gate.
2. Resource state: campaign 24257819463 (status, budget, bidding, ceiling, schedule, geo, networks), all its ad groups
   (status, enabled ads, keyword statuses), today's provisional spend by ad group.
3. The two Google call records on ad group 204129717007 with no WhatConverts match: call_view detail
   (display location, type, status, duration), the ad group's click types on those dates (a location-asset call
   shows as LOCATION_FORMAT_CALL; a call-asset call as CALLS), which CALL assets were linked and at what status,
   and every WhatConverts call within +-3 hours (number suffix, source label, duration, set only).
"""
from __future__ import annotations
import sys, json, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, CLIENT_DIR, ROOT  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.whatconverts import fetch_leads  # noqa: E402

CAMP, AG = "24257819463", "204129717007"
c = client()
ident = identity_gate(c, verbose=True)
now = datetime.datetime.now(TZ)
print("run", now.isoformat(timespec="seconds"))
out = {"run_local": now.isoformat()}

r = q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
        campaign_budget.id, campaign_budget.amount_micros, campaign_budget.explicitly_shared, campaign.network_settings.target_search_network,
        campaign.network_settings.target_content_network FROM campaign WHERE campaign.id = {CAMP}""")[0]
camp = dict(name=r.campaign.name, status=E(r.campaign.status), bidding=E(r.campaign.bidding_strategy_type),
            ceiling=r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, budget_id=str(r.campaign_budget.id),
            budget=r.campaign_budget.amount_micros / 1e6, shared=r.campaign_budget.explicitly_shared,
            partners=r.campaign.network_settings.target_search_network, display=r.campaign.network_settings.target_content_network)
print("\nCAMPAIGN", CAMP, camp)
groups = {}
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status FROM ad_group WHERE campaign.id = {CAMP} AND ad_group.status != 'REMOVED'"):
    groups[str(r.ad_group.id)] = dict(name=r.ad_group.name, status=E(r.ad_group.status), ads=collections.Counter(), kws=collections.Counter())
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group_ad.status FROM ad_group_ad WHERE campaign.id = {CAMP} AND ad_group_ad.status != 'REMOVED'"):
    groups[str(r.ad_group.id)]["ads"][E(r.ad_group_ad.status)] += 1
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.status FROM ad_group_criterion WHERE campaign.id = {CAMP}
        AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status != 'REMOVED'"""):
    groups[str(r.ad_group.id)]["kws"][E(r.ad_group_criterion.status)] += 1
today = now.date().isoformat()
spend_today = {str(r.ad_group.id): (round(r.metrics.cost_micros / 1e6, 2), r.metrics.clicks) for r in q(c, f"""
        SELECT campaign.id, ad_group.id, metrics.cost_micros, metrics.clicks FROM ad_group WHERE campaign.id = {CAMP} AND segments.date = '{today}'""")}
for g, v in groups.items():
    print(f"  AG {g} {v['status']:7s} ads {dict(v['ads'])} kws {dict(v['kws'])} today {spend_today.get(g, (0, 0))} | {v['name']}")
sched = sorted(f"{E(r.campaign_criterion.ad_schedule.day_of_week)[:3]} {r.campaign_criterion.ad_schedule.start_hour}-{r.campaign_criterion.ad_schedule.end_hour}"
               for r in q(c, f"SELECT campaign.id, campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour FROM campaign_criterion WHERE campaign.id = {CAMP} AND campaign_criterion.type = 'AD_SCHEDULE'"))
geo = len(q(c, f"SELECT campaign.id, campaign_criterion.criterion_id FROM campaign_criterion WHERE campaign.id = {CAMP} AND campaign_criterion.type = 'LOCATION' AND campaign_criterion.negative = FALSE"))
print("  schedule", sched, "| positive geo", geo)
camp_today = q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.clicks FROM campaign WHERE campaign.id = {CAMP} AND segments.date = '{today}'")
print("  campaign today (PROVISIONAL):", [(round(x.metrics.cost_micros / 1e6, 2), x.metrics.clicks) for x in camp_today])
# budget history for today (charging-limit context)
try:
    ch = q(c, f"""SELECT change_event.change_date_time, change_event.change_resource_type, change_event.changed_fields, change_event.client_type
            FROM change_event WHERE change_event.change_date_time >= '{today} 00:00:00' AND change_event.change_date_time <= '{today} 23:59:59'
            AND change_event.change_resource_type = 'CAMPAIGN_BUDGET' LIMIT 50""")
    print("  budget change_events today:", len(ch))
except Exception as ex:  # noqa: BLE001
    print("  budget change_event read failed:", str(ex)[:120])

# ---- the unmatched Heating Repair call records ----
print("\n=== Google call records on ad group 204129717007 ===")
calls = []
for r in q(c, f"""SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.call_status, call_view.type,
        call_view.call_tracking_display_location, campaign.id, ad_group.id FROM call_view
        WHERE call_view.start_call_date_time >= '2026-09-17 00:00:00'"""):
    if str(r.ad_group.id) == AG:
        calls.append(dict(start=r.call_view.start_call_date_time, dur=r.call_view.call_duration_seconds, status=E(r.call_view.call_status),
                          type=E(r.call_view.type), display=E(r.call_view.call_tracking_display_location)))
for cv in calls:
    print("  ", cv)
dates = sorted({cv["start"][:10] for cv in calls})
print("\n=== click types on ad group 204129717007 for those dates ===")
for r in q(c, f"""SELECT ad_group.id, segments.date, segments.click_type, metrics.clicks, metrics.impressions, metrics.cost_micros FROM ad_group
        WHERE ad_group.id = {AG} AND segments.date BETWEEN '{dates[0]}' AND '{dates[-1]}'"""):
    if (r.metrics.clicks or r.metrics.impressions) and r.segments.date in dates:
        print(f"   {r.segments.date} {E(r.segments.click_type):26s} clicks {r.metrics.clicks} impr {r.metrics.impressions} cost ${r.metrics.cost_micros/1e6:.2f}")
print("\n=== CALL assets linked to campaign 24257819463 (and account level) ===")
for r in q(c, f"""SELECT campaign.id, asset.id, asset.call_asset.phone_number, campaign_asset.status FROM campaign_asset
        WHERE campaign.id = {CAMP} AND campaign_asset.field_type = 'CALL'"""):
    print(f"   campaign link {r.asset.id} {r.asset.call_asset.phone_number} {E(r.campaign_asset.status)}")
for r in q(c, "SELECT customer_asset.field_type, customer_asset.status, asset.id, asset.call_asset.phone_number FROM customer_asset WHERE customer_asset.field_type = 'CALL'"):
    print(f"   account link {r.asset.id} {r.asset.call_asset.phone_number} {E(r.customer_asset.status)}")
for r in q(c, "SELECT customer.id, customer.call_reporting_setting.call_reporting_enabled, customer.call_reporting_setting.call_conversion_reporting_enabled FROM customer"):
    print("   call reporting:", r.customer.call_reporting_setting.call_reporting_enabled, "| call conversion reporting:", r.customer.call_reporting_setting.call_conversion_reporting_enabled)
print("   location asset sets:", [(str(r.asset_set.id), E(r.asset_set.type), E(r.asset_set.status)) for r in q(c,
      "SELECT asset_set.id, asset_set.type, asset_set.status FROM asset_set WHERE asset_set.type = 'LOCATION_SYNC'")])
print("   customer asset set links:", [(r.asset_set.id, E(r.customer_asset_set.status)) for r in q(c,
      "SELECT customer_asset_set.status, asset_set.id FROM customer_asset_set")])

print("\n=== WhatConverts calls within +-3 h of each record (default + duplicate + spam; no PII) ===")
load_dotenv_if_available(ROOT / ".env")
wc = []
for flt in ({}, {"duplicate": "true"}, {"spam": "true"}):
    for l in fetch_leads("115814", "105803", dates[0], today, client_yaml=CLIENT_DIR / "client.yaml", **flt)["leads"]:
        if l.get("lead_type") in ("Phone Call", "Text Message"):
            t = datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00")).astimezone(TZ)
            wc.append((t, str(l.get("tracking_number") or "")[-4:], f"{l.get('lead_source')}/{l.get('lead_medium')}",
                       l.get("call_duration_seconds"), "spam" if flt.get("spam") else "dup" if flt.get("duplicate") else "default", l.get("lead_id")))
for cv in calls:
    ct = datetime.datetime.fromisoformat(cv["start"]).replace(tzinfo=TZ)
    near = sorted((round((w[0] - ct).total_seconds() / 60, 1),) + w[1:] for w in wc if abs((w[0] - ct).total_seconds()) <= 3 * 3600)
    print(f"  call {cv['start']} {cv['dur']}s -> {near if near else 'no WhatConverts call or text within 3 hours'}")
out.update(identity={k: ident[k] for k in ("customer_id", "descriptive_name")}, campaign=camp,
           groups={g: {**v, "ads": dict(v["ads"]), "kws": dict(v["kws"])} for g, v in groups.items()},
           spend_today=spend_today, calls=calls)
(SNAP / "hr-containment-checks-2026-09-30.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
