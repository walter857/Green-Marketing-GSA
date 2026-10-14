#!/usr/bin/env python3
"""Average CPC of $106 on AC Repair against a $25 ceiling would be impossible.
Find out what the per-campaign, per-day cost/click actually is."""
from __future__ import annotations
import sys, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
print("=== PER-CAMPAIGN COST / CLICK, 2026-08-14 .. 2026-09-09 ===")
print(f"  {'campaign':<20}{'cost':>10}{'clicks':>8}{'avgCPC':>10}{'maxCPC ceiling':>16}")
ceil = {}
for r in q(c, f"SELECT campaign.id, campaign.name, campaign.bidding_strategy_type, "
              f"campaign.target_spend.cpc_bid_ceiling_micros, campaign.percent_cpc.cpc_bid_ceiling_micros "
              f"FROM campaign WHERE campaign.id IN ({IN5})"):
    ceil[str(r.campaign.id)] = {
        "strategy": E(r.campaign.bidding_strategy_type),
        "target_spend_ceiling": r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6}
for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.clicks, metrics.average_cpc "
              f"FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    cid = str(r.campaign.id); m = r.metrics
    cpc = m.cost_micros / 1e6 / m.clicks if m.clicks else 0
    print(f"  {NAME[cid]:<20}{m.cost_micros/1e6:>10.2f}{m.clicks:>8}{cpc:>10.2f}"
          f"{ceil[cid]['target_spend_ceiling']:>16.2f}   {ceil[cid]['strategy']}")

print("\n=== AC REPAIR DAY BY DAY (is the high CPC recent or throughout?) ===")
print(f"  {'date':<12}{'cost':>9}{'clicks':>8}{'avgCPC':>9}{'impr':>7}")
for r in q(c, "SELECT segments.date, metrics.cost_micros, metrics.clicks, metrics.impressions "
              "FROM campaign WHERE campaign.id = 24132507741 "
              "AND segments.date BETWEEN '2026-08-14' AND '2026-09-09' ORDER BY segments.date"):
    m = r.metrics
    if not m.impressions: continue
    cpc = m.cost_micros/1e6/m.clicks if m.clicks else 0
    print(f"  {r.segments.date:<12}{m.cost_micros/1e6:>9.2f}{m.clicks:>8}{cpc:>9.2f}{m.impressions:>7}")

print("\n=== AD-GROUP-LEVEL cpc_bid ON THE FIVE LIVE AD GROUPS ===")
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.name, ad_group.cpc_bid_micros, "
              f"ad_group.status FROM ad_group WHERE campaign.id IN ({IN5}) "
              f"AND ad_group.status = 'ENABLED'"):
    a = r.ad_group
    print(f"  {NAME[str(r.campaign.id)]:<20}{a.id:<16}{a.cpc_bid_micros/1e6:>8.2f}  {a.name[:40]}")
