#!/usr/bin/env python3
"""Softwind post-launch monitor. READ-ONLY. Constructs no operation, calls no mutate service.

Usage:  python scripts/softwind_monitor.py [health|terms|spend|invalid|campaign|adgroup|
        keyword|rsa|location|device|schedule|audience|demo|quality|all]
"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
D = "segments.date BETWEEN '2026-09-02' AND '2026-12-31'"
Q = {
 "health": f"""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
        metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "terms": f"""SELECT search_term_view.search_term, ad_group.name,
        segments.search_term_match_type, metrics.impressions, metrics.clicks,
        metrics.cost_micros, metrics.conversions FROM search_term_view WHERE {D}""",
 "spend": f"""SELECT segments.date, campaign.name, metrics.cost_micros, metrics.clicks,
        metrics.average_cpc FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "invalid": f"""SELECT campaign.name, metrics.clicks, metrics.invalid_clicks,
        metrics.invalid_click_rate, metrics.cost_micros FROM campaign
        WHERE {D} AND campaign.status!='REMOVED'""",
 "campaign": f"""SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.ctr,
        metrics.average_cpc, metrics.conversions, metrics.search_impression_share,
        metrics.search_rank_lost_impression_share, metrics.search_budget_lost_impression_share
        FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "adgroup": f"""SELECT ad_group.name, metrics.impressions, metrics.clicks, metrics.ctr,
        metrics.average_cpc, metrics.conversions FROM ad_group
        WHERE {D} AND ad_group.status='ENABLED'""",
 "keyword": f"""SELECT ad_group.name, ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type, metrics.impressions, metrics.clicks,
        metrics.average_cpc, metrics.conversions FROM keyword_view WHERE {D}""",
 "rsa": f"""SELECT ad_group.name, ad_group_ad.ad.id, metrics.impressions, metrics.clicks,
        metrics.ctr, metrics.conversions FROM ad_group_ad
        WHERE {D} AND ad_group_ad.status='ENABLED'""",
 "location": f"""SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros
        FROM location_view WHERE {D}""",
 "device": f"""SELECT segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros,
        metrics.conversions FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "schedule": f"""SELECT segments.day_of_week, segments.hour, metrics.clicks, metrics.cost_micros
        FROM campaign WHERE {D} AND campaign.status!='REMOVED'""",
 "audience": f"""SELECT campaign.name, metrics.impressions, metrics.clicks
        FROM campaign_audience_view WHERE {D}""",
 "demo": f"""SELECT ad_group.name, metrics.impressions, metrics.clicks, metrics.cost_micros
        FROM gender_view WHERE {D}""",
 "quality": """SELECT ad_group.name, ad_group_criterion.keyword.text,
        ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.search_predicted_ctr,
        ad_group_criterion.quality_info.creative_quality_score,
        ad_group_criterion.quality_info.post_click_quality_score
        FROM keyword_view WHERE ad_group_criterion.quality_info.quality_score > 0""",
 "conversions": """SELECT conversion_action.name, metrics.all_conversions
        FROM conversion_action WHERE segments.date BETWEEN '2026-09-02' AND '2026-12-31'""",
}

def main() -> int:
    what = sys.argv[1] if len(sys.argv) > 1 else "health"
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    keys = list(Q) if what == "all" else [what]
    for k in keys:
        if k not in Q:
            print(f"unknown view: {k}. options: {', '.join(Q)}"); return 2
        print(f"\n===== {k.upper()} =====")
        try:
            for r in svc.search(customer_id=cid, query=Q[k]):
                print(" ", r)
        except Exception as e:
            print("  ERROR:", str(e)[:200])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
