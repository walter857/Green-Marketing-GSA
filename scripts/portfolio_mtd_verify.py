#!/usr/bin/env python3
"""Spot-verify surprising rows in the MTD pull. Read-only."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client

load_dotenv_if_available(ROOT / ".env")
client = load_google_ads_client()
svc = client.get_service("GoogleAdsService")


def q(cid, query, label):
    print("\n---", label, "---")
    try:
        n = 0
        for r in svc.search(customer_id=cid, query=query):
            yield r
            n += 1
        if n == 0:
            print("  (0 rows)")
    except Exception as exc:  # noqa: BLE001
        print("  ERROR:", type(exc).__name__, str(exc)[:300])


# 1. Ambient 'hvac installers' - confirm QS really is unset and check impressions
for r in q("2401959466",
           "SELECT ad_group.name, ad_group_criterion.keyword.text, "
           "ad_group_criterion.quality_info.quality_score, ad_group_criterion.status, "
           "ad_group_criterion.effective_cpc_bid_micros, metrics.impressions, metrics.clicks, "
           "metrics.cost_micros, metrics.conversions "
           "FROM keyword_view WHERE segments.date DURING THIS_MONTH "
           "AND metrics.cost_micros > 0 ORDER BY metrics.cost_micros DESC LIMIT 8",
           "AMBIENT: keywords with spend MTD"):
    qi = r.ad_group_criterion.quality_info
    print(f"  {r.ad_group_criterion.keyword.text:35s} impr={r.metrics.impressions:6d} "
          f"clicks={r.metrics.clicks:4d} cost=${r.metrics.cost_micros/1e6:8,.2f} "
          f"conv={r.metrics.conversions:4.1f} "
          f"QS={qi.quality_score if qi._pb.HasField('quality_score') else 'UNSET'} "
          f"bid=${r.ad_group_criterion.effective_cpc_bid_micros/1e6:.2f}")

# 2. Greenway - campaigns exist, zero spend. Why?
for r in q("1491333698",
           "SELECT campaign.name, campaign.status, campaign.serving_status, "
           "campaign.advertising_channel_type, campaign_budget.amount_micros, "
           "campaign.bidding_strategy_type "
           "FROM campaign WHERE campaign.status != 'REMOVED'",
           "GREENWAY LAWN CARE: campaign serving status"):
    print(f"  {r.campaign.name:40s} status={r.campaign.status.name:8s} "
          f"serving={r.campaign.serving_status.name:12s} "
          f"budget=${r.campaign_budget.amount_micros/1e6:.2f} "
          f"bid={r.campaign.bidding_strategy_type.name}")

# 3. Emerald Oasis - zero campaigns at all?
for r in q("7064753033",
           "SELECT campaign.name, campaign.status, campaign.serving_status "
           "FROM campaign",
           "EMERALD OASIS: all campaigns incl REMOVED"):
    print(f"  {r.campaign.name:40s} {r.campaign.status.name} {r.campaign.serving_status.name}")

# 4. Ray Lawns - what channel is the only campaign?
for r in q("5587528194",
           "SELECT campaign.name, campaign.status, campaign.advertising_channel_type, "
           "campaign.advertising_channel_sub_type, metrics.cost_micros, metrics.conversions "
           "FROM campaign WHERE segments.date DURING THIS_MONTH",
           "RAY LAWNS: campaign channel"):
    print(f"  {r.campaign.name:40s} {r.campaign.advertising_channel_type.name}/"
          f"{r.campaign.advertising_channel_sub_type.name} "
          f"${r.metrics.cost_micros/1e6:,.2f} conv={r.metrics.conversions}")

# 5. Confirm date span actually covered (first + last delivery day portfolio-wide)
for cid, nm in [("2401959466", "Ambient"), ("3451131960", "Beaver bins")]:
    days = []
    for r in q(cid, "SELECT segments.date, metrics.cost_micros FROM customer "
                    "WHERE segments.date DURING THIS_MONTH ORDER BY segments.date",
               f"{nm}: MTD date span"):
        days.append(r.segments.date)
    if days:
        print(f"  {nm}: {days[0]} .. {days[-1]}  ({len(days)} days with delivery)")

# 6. Conversion actions in play - is the 0-conv picture a tracking problem?
for cid, nm in [("1521725229", "Softwind Power Washing"), ("7380491929", "Pro Green Austin")]:
    for r in q(cid, "SELECT conversion_action.name, conversion_action.status, "
                    "conversion_action.primary_for_goal, conversion_action.type, "
                    "metrics.all_conversions "
                    "FROM conversion_action WHERE segments.date DURING THIS_MONTH",
               f"{nm}: conversion actions with activity MTD"):
        print(f"  {r.conversion_action.name[:44]:44s} {r.conversion_action.status.name:8s} "
              f"primary={r.conversion_action.primary_for_goal} "
              f"all_conv={r.metrics.all_conversions:.1f}")
