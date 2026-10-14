#!/usr/bin/env python3
"""Inspect campaign 24132507747 so the new commercial ad group inherits exactly."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
CAMP = "24132507747"
print("=== CAMPAIGN 24132507747 ===")
for r in q(c, f"SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, "
              f"campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign_budget.amount_micros, campaign.tracking_url_template, "
              f"campaign.network_settings.target_google_search, "
              f"campaign.network_settings.target_search_network, "
              f"campaign.network_settings.target_content_network, "
              f"campaign.geo_target_type_setting.positive_geo_target_type "
              f"FROM campaign WHERE campaign.id = {CAMP}"):
    x = r.campaign
    print(f"  name            {x.name}")
    print(f"  status          {E(x.status)}   channel {E(x.advertising_channel_type)}")
    print(f"  bidding         {E(x.bidding_strategy_type)}  ceiling "
          f"${x.target_spend.cpc_bid_ceiling_micros/1e6:.2f}")
    print(f"  budget          ${r.campaign_budget.amount_micros/1e6:.2f}/day")
    print(f"  geo type        {E(x.geo_target_type_setting.positive_geo_target_type)}")
    print(f"  google search   {x.network_settings.target_google_search}")
    print(f"  search partners {x.network_settings.target_search_network}")
    print(f"  display         {x.network_settings.target_content_network}")
    print(f"  tracking tmpl   {x.tracking_url_template[:90]!r}")

print("\n=== EXISTING AD GROUPS IN THIS CAMPAIGN ===")
for r in q(c, f"SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type, "
              f"ad_group.cpc_bid_micros FROM ad_group WHERE campaign.id = {CAMP}"):
    a = r.ad_group
    print(f"  {a.id:<16}{E(a.status):<10}{E(a.type_):<20}cpc ${a.cpc_bid_micros/1e6:.2f}  {a.name}")

print("\n=== RESIDENTIAL AD GROUP 202339087634 CONTENT ===")
for r in q(c, "SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
              "ad_group_criterion.status, ad_group_criterion.negative "
              "FROM ad_group_criterion WHERE ad_group.id = 202339087634 "
              "AND ad_group_criterion.type='KEYWORD'"):
    k = r.ad_group_criterion
    print(f"  {'NEG ' if k.negative else 'POS '}{E(k.keyword.match_type):<8}"
          f"{E(k.status):<10}{k.keyword.text}")

print("\n=== ADS IN 202339087634 (final urls + paths) ===")
for r in q(c, "SELECT ad_group_ad.ad.id, ad_group_ad.status, "
              "ad_group_ad.policy_summary.approval_status, "
              "ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.path1, "
              "ad_group_ad.ad.responsive_search_ad.path2 FROM ad_group_ad "
              "WHERE ad_group.id = 202339087634"):
    x = r.ad_group_ad
    print(f"  {x.ad.id:<14}{E(x.status):<9}{E(x.policy_summary.approval_status):<14}"
          f"{list(x.ad.final_urls)}  /{x.ad.responsive_search_ad.path1}"
          f"/{x.ad.responsive_search_ad.path2}")

print("\n=== 'commercial' ANYWHERE AS A NEGATIVE ON THIS CAMPAIGN? ===")
n = 0
for r in q(c, f"SELECT campaign_criterion.keyword.text, campaign_criterion.keyword.match_type "
              f"FROM campaign_criterion WHERE campaign.id = {CAMP} "
              f"AND campaign_criterion.type='KEYWORD' AND campaign_criterion.negative=TRUE"):
    t = r.campaign_criterion.keyword.text.lower()
    if "commercial" in t:
        n += 1
        print(f"  CAMPAIGN NEG {E(r.campaign_criterion.keyword.match_type):<8}{t}")
print(f"  campaign-level negatives containing 'commercial': {n}")
n2 = 0
for r in q(c, "SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type, "
              "shared_set.id FROM shared_criterion WHERE shared_criterion.type='KEYWORD'"):
    if "commercial" in r.shared_criterion.keyword.text.lower():
        n2 += 1
        print(f"  SHARED SET {r.shared_set.id} {E(r.shared_criterion.keyword.match_type):<8}"
              f"{r.shared_criterion.keyword.text}")
print(f"  shared-set negatives containing 'commercial': {n2}")
