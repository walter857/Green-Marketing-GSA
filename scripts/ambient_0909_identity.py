#!/usr/bin/env python3
"""2026-09-09 identity gate + structural snapshot for Ambient Cooling."""
from __future__ import annotations
import datetime, json, sys
sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else ".")
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
print("=== IDENTITY GATE 2026-09-09 ===")
ident = identity_gate(c)

out = {"identity": ident}

print("\n=== CAMPAIGNS (all) ===")
camps = []
for r in q(c, """
    SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
           campaign.advertising_channel_sub_type, campaign.serving_status,
           campaign.bidding_strategy_type,
           campaign.target_spend.cpc_bid_ceiling_micros,
           campaign.campaign_budget, campaign.start_date_time, campaign.end_date_time,
           campaign.network_settings.target_google_search,
           campaign.network_settings.target_search_network,
           campaign.network_settings.target_content_network,
           campaign.network_settings.target_partner_search_network,
           campaign.geo_target_type_setting.positive_geo_target_type,
           campaign.geo_target_type_setting.negative_geo_target_type,
           campaign.optimization_score
    FROM campaign
    ORDER BY campaign.id
"""):
    x = r.campaign
    camps.append({
        "id": str(x.id), "name": x.name, "status": E(x.status),
        "channel": E(x.advertising_channel_type), "sub_type": E(x.advertising_channel_sub_type),
        "serving_status": E(x.serving_status), "bidding": E(x.bidding_strategy_type),
        "target_spend_ceiling_micros": x.target_spend.cpc_bid_ceiling_micros,
        "budget": x.campaign_budget.split("/")[-1] if x.campaign_budget else None,
        "start": x.start_date_time, "end": x.end_date_time,
        "net_google_search": x.network_settings.target_google_search,
        "net_search_partners": x.network_settings.target_search_network,
        "net_display": x.network_settings.target_content_network,
        "net_partner": x.network_settings.target_partner_search_network,
        "positive_geo": E(x.geo_target_type_setting.positive_geo_target_type),
        "negative_geo": E(x.geo_target_type_setting.negative_geo_target_type),
    })
out["campaigns"] = camps
print(f"  total campaigns: {len(camps)}")
for x in camps:
    flag = " <<< FIVE" if x["id"] in FIVE else ""
    print(f"  {x['id']:>12} {x['status']:>8} {x['serving_status']:>10} {x['channel']:>14} {x['bidding']:>22} geo+={x['positive_geo']:<24} {x['name'][:52]}{flag}")

print("\n=== BUDGETS ===")
buds = []
for r in q(c, """
    SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
           campaign_budget.explicitly_shared, campaign_budget.status,
           campaign_budget.delivery_method, campaign_budget.reference_count,
           campaign_budget.total_amount_micros
    FROM campaign_budget
    ORDER BY campaign_budget.id
"""):
    x = r.campaign_budget
    buds.append({"id": str(x.id), "name": x.name, "daily": round(x.amount_micros/1e6, 2),
                 "status": E(x.status), "delivery": E(x.delivery_method),
                 "shared": x.explicitly_shared, "refs": x.reference_count})
out["budgets"] = buds
for x in buds:
    if x["status"] == "ENABLED":
        print(f"  {x['id']:>12} ${x['daily']:>8.2f} refs={x['refs']} {x['name'][:60]}")

write(EVID / "2026-09-09-identity-and-structure.json", out)
