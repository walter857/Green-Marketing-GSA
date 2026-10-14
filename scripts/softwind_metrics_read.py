#!/usr/bin/env python3
"""Read-only performance segmentation for Softwind Power Washing. SELECT-only."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
TZ = ZoneInfo("America/New_York")
OUT = ROOT / "clients/softwind-power-washing/snapshots/metrics-2026-08-25.json"
START = "2026-01-01"


class Reader:
    def __init__(self):
        load_dotenv_if_available(ROOT / ".env")
        self.svc = load_google_ads_client().get_service("GoogleAdsService")
        self.errors = []

    def rows(self, name, query):
        try:
            return list(self.svc.search(customer_id=CID, query=query))
        except Exception as exc:
            msg = str(exc)
            for m in ("message: ", "FaultMessage: "):
                if m in msg:
                    msg = msg.split(m, 1)[1][:400]
                    break
            self.errors.append({"query": name, "error": msg[:400]})
            print("  !! %s: %s" % (name, msg[:200]), file=sys.stderr)
            return []


def base(m):
    return {
        "impressions": int(m.impressions), "clicks": int(m.clicks),
        "cost": m.cost_micros / 1_000_000,
        "conversions": float(m.conversions),
        "all_conversions": float(m.all_conversions),
        "ctr": float(m.ctr),
        "avg_cpc": m.average_cpc / 1_000_000 if m.average_cpc else 0.0,
    }


def main() -> int:
    r = Reader()
    end = datetime.now(TZ).date().isoformat()
    out = {"customer_id": CID, "snapshot_taken_account_local": datetime.now(TZ).isoformat(),
           "window": {"start": START, "end": end}}
    W = "WHERE segments.date BETWEEN '%s' AND '%s'" % (START, end)

    # ---- SEARCH TERMS: every available term, no impression threshold ----
    q = """
      SELECT campaign.name, ad_group.name, ad_group.id,
             search_term_view.search_term, search_term_view.status,
             segments.keyword.info.text, segments.keyword.info.match_type,
             segments.search_term_match_type,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc, metrics.conversions_value
      FROM search_term_view %s
      ORDER BY metrics.impressions DESC
    """ % W
    out["search_terms"] = [
        dict(base(x.metrics),
             campaign=x.campaign.name, ad_group=x.ad_group.name,
             ad_group_id=str(x.ad_group.id),
             search_term=x.search_term_view.search_term,
             st_status=enum_name(x.search_term_view.status),
             matched_keyword=x.segments.keyword.info.text,
             keyword_match_type=enum_name(x.segments.keyword.info.match_type),
             search_term_match_type=enum_name(x.segments.search_term_match_type))
        for x in r.rows("search_term_view", q)
    ]

    # ---- KEYWORD performance ----
    q = """
      SELECT campaign.name, ad_group.name, ad_group.id,
             ad_group_criterion.criterion_id,
             ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
             ad_group_criterion.status,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc,
             metrics.search_impression_share,
             metrics.search_rank_lost_impression_share,
             metrics.search_top_impression_share,
             metrics.search_absolute_top_impression_share,
             metrics.top_impression_percentage,
             metrics.absolute_top_impression_percentage,
             metrics.average_cpm
      FROM keyword_view %s
      ORDER BY metrics.impressions DESC
    """ % W
    out["keyword_performance"] = [
        dict(base(x.metrics),
             campaign=x.campaign.name, ad_group=x.ad_group.name,
             ad_group_id=str(x.ad_group.id),
             criterion_id=str(x.ad_group_criterion.criterion_id),
             text=x.ad_group_criterion.keyword.text,
             match_type=enum_name(x.ad_group_criterion.keyword.match_type),
             status=enum_name(x.ad_group_criterion.status),
             search_is=float(x.metrics.search_impression_share) or None,
             lost_is_rank=float(x.metrics.search_rank_lost_impression_share) or None,
             lost_is_budget=None,
             top_pct=float(x.metrics.top_impression_percentage) or None,
             abs_top_pct=float(x.metrics.absolute_top_impression_percentage) or None)
        for x in r.rows("keyword_view", q)
    ]

    # ---- AD GROUP performance ----
    q = """
      SELECT campaign.name, ad_group.id, ad_group.name, ad_group.status,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc,
             metrics.search_impression_share,
             metrics.search_rank_lost_impression_share,
             metrics.top_impression_percentage,
             metrics.absolute_top_impression_percentage
      FROM ad_group %s
      ORDER BY metrics.impressions DESC
    """ % W
    out["ad_group_performance"] = [
        dict(base(x.metrics),
             campaign=x.campaign.name, ad_group_id=str(x.ad_group.id),
             ad_group=x.ad_group.name, status=enum_name(x.ad_group.status),
             search_is=float(x.metrics.search_impression_share) or None,
             lost_is_rank=float(x.metrics.search_rank_lost_impression_share) or None,
             lost_is_budget=None,
             top_pct=float(x.metrics.top_impression_percentage) or None,
             abs_top_pct=float(x.metrics.absolute_top_impression_percentage) or None)
        for x in r.rows("ad_group_perf", q)
    ]

    # ---- AD performance ----
    q = """
      SELECT campaign.name, ad_group.name, ad_group_ad.ad.id,
             ad_group_ad.status,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM ad_group_ad %s
      ORDER BY metrics.impressions DESC
    """ % W
    out["ad_performance"] = [
        dict(base(x.metrics), campaign=x.campaign.name, ad_group=x.ad_group.name,
             ad_id=str(x.ad_group_ad.ad.id), status=enum_name(x.ad_group_ad.status))
        for x in r.rows("ad_perf", q)
    ]

    # ---- DEVICE ----
    q = """
      SELECT campaign.name, segments.device,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM campaign %s
    """ % W
    out["device"] = [
        dict(base(x.metrics), campaign=x.campaign.name,
             device=enum_name(x.segments.device))
        for x in r.rows("device", q)
    ]

    # ---- DAY OF WEEK ----
    q = """
      SELECT campaign.name, segments.day_of_week,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM campaign %s
    """ % W
    out["day_of_week"] = [
        dict(base(x.metrics), campaign=x.campaign.name,
             day=enum_name(x.segments.day_of_week))
        for x in r.rows("day_of_week", q)
    ]

    # ---- HOUR OF DAY ----
    q = """
      SELECT campaign.name, segments.hour,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM campaign %s
    """ % W
    out["hour_of_day"] = [
        dict(base(x.metrics), campaign=x.campaign.name, hour=int(x.segments.hour))
        for x in r.rows("hour", q)
    ]

    # ---- GEO: user location and location of interest ----
    q = """
      SELECT campaign.name,
             geographic_view.country_criterion_id,
             geographic_view.location_type,
             segments.geo_target_city, segments.geo_target_county,
             segments.geo_target_postal_code, segments.geo_target_metro,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM geographic_view %s
      ORDER BY metrics.impressions DESC
    """ % W
    out["geographic_view"] = [
        dict(base(x.metrics), campaign=x.campaign.name,
             location_type=enum_name(x.geographic_view.location_type),
             city=x.segments.geo_target_city or "",
             county=x.segments.geo_target_county or "",
             postal=x.segments.geo_target_postal_code or "",
             metro=x.segments.geo_target_metro or "")
        for x in r.rows("geographic_view", q)
    ]

    q = """
      SELECT campaign.name, user_location_view.country_criterion_id,
             user_location_view.targeting_location,
             segments.geo_target_city, segments.geo_target_postal_code,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM user_location_view %s
      ORDER BY metrics.impressions DESC
    """ % W
    out["user_location_view"] = [
        dict(base(x.metrics), campaign=x.campaign.name,
             targeting_location=bool(x.user_location_view.targeting_location),
             city=x.segments.geo_target_city or "",
             postal=x.segments.geo_target_postal_code or "")
        for x in r.rows("user_location_view", q)
    ]

    # ---- LANDING PAGES ----
    q = """
      SELECT campaign.name, landing_page_view.unexpanded_final_url,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM landing_page_view %s
      ORDER BY metrics.clicks DESC
    """ % W
    out["landing_page_view"] = [
        dict(base(x.metrics), campaign=x.campaign.name,
             url=x.landing_page_view.unexpanded_final_url)
        for x in r.rows("landing_page_view", q)
    ]

    q = """
      SELECT campaign.name, expanded_landing_page_view.expanded_final_url,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM expanded_landing_page_view %s
      ORDER BY metrics.clicks DESC
    """ % W
    out["expanded_landing_page_view"] = [
        dict(base(x.metrics), campaign=x.campaign.name,
             url=x.expanded_landing_page_view.expanded_final_url)
        for x in r.rows("expanded_landing_page_view", q)
    ]

    # ---- CONVERSION ACTION performance ----
    q = """
      SELECT conversion_action.name, conversion_action.category,
             conversion_action.status,
             metrics.all_conversions,
             metrics.all_conversions_value
      FROM conversion_action %s
    """ % W
    out["conversion_action_performance"] = [
        {"name": x.conversion_action.name,
         "category": enum_name(x.conversion_action.category),
         "status": enum_name(x.conversion_action.status),
         "all_conversions": float(x.metrics.all_conversions),
         "all_conversions_value": float(x.metrics.all_conversions_value)}
        for x in r.rows("conversion_action_perf", q)
    ]

    # ---- CLICK TYPE (call clicks vs headline) ----
    q = """
      SELECT campaign.name, segments.click_type,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc
      FROM campaign %s
    """ % W
    out["click_type"] = [
        dict(base(x.metrics), campaign=x.campaign.name,
             click_type=enum_name(x.segments.click_type))
        for x in r.rows("click_type", q)
    ]

    # ---- CAMPAIGN AGGREGATE (all-time) ----
    q = """
      SELECT campaign.id, campaign.name,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions, metrics.ctr,
             metrics.average_cpc, metrics.interactions, metrics.interaction_rate,
             metrics.search_impression_share,
             metrics.search_budget_lost_impression_share,
             metrics.search_rank_lost_impression_share,
             metrics.search_top_impression_share,
             metrics.search_absolute_top_impression_share,
             metrics.top_impression_percentage,
             metrics.absolute_top_impression_percentage,
             metrics.invalid_clicks, metrics.invalid_click_rate,
             metrics.average_cpm, metrics.phone_calls, metrics.phone_impressions,
             metrics.phone_through_rate
      FROM campaign %s
    """ % W
    out["campaign_aggregate"] = [
        dict(base(x.metrics), campaign_id=str(x.campaign.id), campaign=x.campaign.name,
             search_is=float(x.metrics.search_impression_share) or None,
             lost_is_budget=float(x.metrics.search_budget_lost_impression_share) or None,
             lost_is_rank=float(x.metrics.search_rank_lost_impression_share) or None,
             search_top_is=float(x.metrics.search_top_impression_share) or None,
             search_abs_top_is=float(x.metrics.search_absolute_top_impression_share) or None,
             top_pct=float(x.metrics.top_impression_percentage) or None,
             abs_top_pct=float(x.metrics.absolute_top_impression_percentage) or None,
             invalid_clicks=int(x.metrics.invalid_clicks),
             invalid_click_rate=float(x.metrics.invalid_click_rate),
             phone_calls=int(x.metrics.phone_calls),
             phone_impressions=int(x.metrics.phone_impressions))
        for x in r.rows("campaign_aggregate", q)
    ]

    out["read_errors"] = r.errors
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote %s" % OUT)
    for k, v in out.items():
        if isinstance(v, list):
            print("  %s: %d" % (k, len(v)))
    for e in r.errors:
        print(" ERR", e["query"], "::", e["error"][:250])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
