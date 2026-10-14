#!/usr/bin/env python3
"""Read-only orientation probe: what campaigns/ad groups exist at all."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"

def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    out = {}

    q = """
      SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
             campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
             campaign.start_date_time, campaign.end_date_time, campaign.bidding_strategy_type,
             campaign_budget.id, campaign_budget.amount_micros,
             campaign.primary_status, campaign.experiment_type
      FROM campaign
      ORDER BY campaign.id
    """
    camps = []
    for r in svc.search(customer_id=CID, query=q):
        c = r.campaign
        camps.append({
            "id": str(c.id), "name": c.name, "status": enum_name(c.status),
            "serving_status": enum_name(c.serving_status),
            "primary_status": enum_name(c.primary_status),
            "channel": enum_name(c.advertising_channel_type),
            "sub_type": enum_name(c.advertising_channel_sub_type),
            "start_date_time": c.start_date_time, "end_date_time": c.end_date_time or "",
            "bidding_strategy_type": enum_name(c.bidding_strategy_type),
            "budget_id": str(r.campaign_budget.id),
            "daily_budget": r.campaign_budget.amount_micros / 1_000_000,
            "experiment_type": enum_name(c.experiment_type),
        })
    out["campaigns"] = camps

    q2 = """
      SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
             campaign.id, campaign.name, ad_group.primary_status
      FROM ad_group
      ORDER BY campaign.id, ad_group.id
    """
    ags = []
    for r in svc.search(customer_id=CID, query=q2):
        a = r.ad_group
        ags.append({
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "id": str(a.id), "name": a.name, "status": enum_name(a.status),
            "type": enum_name(a.type_), "primary_status": enum_name(a.primary_status),
        })
    out["ad_groups"] = ags

    print(json.dumps(out, indent=2))
    (ROOT / "clients/softwind-power-washing/snapshots/probe-2026-08-25.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
