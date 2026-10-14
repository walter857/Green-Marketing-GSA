#!/usr/bin/env python3
"""Phase A performance / measurement read for Softwind Landscape & Masonry.

SELECT-only. Writes 01b-before-performance.json next to the structural
snapshot. Ratios are computed from summed numerators and denominators, never
by averaging row-level ratios.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "2429758629"
TZ = ZoneInfo("America/New_York")
OUTDIR = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PATIO, PAVERS = "23484806108", "23489296528"


def m(v):
    return None if v is None else round(v / 1_000_000, 6)


class Reader:
    def __init__(self):
        load_dotenv_if_available(ROOT / ".env")
        self.client = load_google_ads_client()
        self.svc = self.client.get_service("GoogleAdsService")
        self.errors, self.ok = [], []

    def rows(self, name, query):
        try:
            out = list(self.svc.search(customer_id=CID, query=query))
            self.ok.append({"query": name, "rows": len(out)})
            print("  ok  %-40s %5d rows" % (name, len(out)))
            return out
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            for k in ("message: ", "FaultMessage: "):
                if k in msg:
                    msg = msg.split(k, 1)[1][:400]
                    break
            self.errors.append({"query": name, "error": msg[:400]})
            print("  !!  %-40s %s" % (name, msg[:150]), file=sys.stderr)
            return []


def main() -> int:
    r = Reader()
    today_local = datetime.now(TZ).date()
    out = {
        "customer_id": CID,
        "read_taken_account_local": datetime.now(TZ).isoformat(),
        "today_account_local": today_local.isoformat(),
        "ratio_policy": "ratios computed from summed numerator/denominator only",
    }

    # ------- 1. ACCOUNT MONTHLY, all campaigns, Jan..today -------
    out["account_monthly"] = [{
        "month": x.segments.month, "cost": m(x.metrics.cost_micros),
        "impressions": x.metrics.impressions, "clicks": x.metrics.clicks,
        "conversions": round(x.metrics.conversions, 4),
        "all_conversions": round(x.metrics.all_conversions, 4),
        "conversions_value": round(x.metrics.conversions_value, 2),
    } for x in r.rows("account_monthly", """
        SELECT segments.month, metrics.cost_micros, metrics.impressions,
               metrics.clicks, metrics.conversions, metrics.all_conversions,
               metrics.conversions_value
        FROM customer WHERE segments.date BETWEEN '2026-01-01' AND '%s'
        ORDER BY segments.month""" % today_local)]

    # ------- 2. CAMPAIGN MONTHLY -------
    out["campaign_monthly"] = [{
        "month": x.segments.month, "campaign_id": str(x.campaign.id),
        "campaign_name": x.campaign.name, "status": enum_name(x.campaign.status),
        "cost": m(x.metrics.cost_micros), "impressions": x.metrics.impressions,
        "clicks": x.metrics.clicks, "conversions": round(x.metrics.conversions, 4),
        "all_conversions": round(x.metrics.all_conversions, 4),
        "search_impression_share": x.metrics.search_impression_share or None,
        "search_budget_lost_is": x.metrics.search_budget_lost_impression_share or None,
        "search_rank_lost_is": x.metrics.search_rank_lost_impression_share or None,
    } for x in r.rows("campaign_monthly", """
        SELECT segments.month, campaign.id, campaign.name, campaign.status,
               metrics.cost_micros, metrics.impressions, metrics.clicks,
               metrics.conversions, metrics.all_conversions,
               metrics.search_impression_share,
               metrics.search_budget_lost_impression_share,
               metrics.search_rank_lost_impression_share
        FROM campaign WHERE segments.date BETWEEN '2026-01-01' AND '%s'
        ORDER BY segments.month, campaign.name""" % today_local)]

    # ------- 3. ACCOUNT DAILY, last 45 days (pacing) -------
    start45 = (today_local - timedelta(days=45)).isoformat()
    out["account_daily"] = [{
        "date": x.segments.date, "cost": m(x.metrics.cost_micros),
        "impressions": x.metrics.impressions, "clicks": x.metrics.clicks,
        "conversions": round(x.metrics.conversions, 4),
        "all_conversions": round(x.metrics.all_conversions, 4),
        "invalid_clicks": x.metrics.invalid_clicks,
    } for x in r.rows("account_daily_45", """
        SELECT segments.date, metrics.cost_micros, metrics.impressions,
               metrics.clicks, metrics.conversions, metrics.all_conversions,
               metrics.invalid_clicks
        FROM customer WHERE segments.date BETWEEN '%s' AND '%s'
        ORDER BY segments.date""" % (start45, today_local))]

    # ------- 4. CAMPAIGN DAILY, last 45 days -------
    out["campaign_daily"] = [{
        "date": x.segments.date, "campaign_id": str(x.campaign.id),
        "campaign_name": x.campaign.name, "cost": m(x.metrics.cost_micros),
        "impressions": x.metrics.impressions, "clicks": x.metrics.clicks,
        "conversions": round(x.metrics.conversions, 4),
        "all_conversions": round(x.metrics.all_conversions, 4),
        "invalid_clicks": x.metrics.invalid_clicks,
    } for x in r.rows("campaign_daily_45", """
        SELECT segments.date, campaign.id, campaign.name, metrics.cost_micros,
               metrics.impressions, metrics.clicks, metrics.conversions,
               metrics.all_conversions, metrics.invalid_clicks
        FROM campaign WHERE segments.date BETWEEN '%s' AND '%s'
        ORDER BY segments.date""" % (start45, today_local))]

    # ------- 5. CONVERSIONS BY ACTION x CAMPAIGN x MONTH -------
    out["conversions_by_action"] = [{
        "month": x.segments.month, "campaign_id": str(x.campaign.id),
        "campaign_name": x.campaign.name,
        "conversion_action": x.segments.conversion_action,
        "conversion_action_name": x.segments.conversion_action_name,
        "category": enum_name(x.segments.conversion_action_category),
        "conversions": round(x.metrics.conversions, 4),
        "all_conversions": round(x.metrics.all_conversions, 4),
    } for x in r.rows("conversions_by_action", """
        SELECT segments.month, campaign.id, campaign.name,
               segments.conversion_action, segments.conversion_action_name,
               segments.conversion_action_category,
               metrics.conversions, metrics.all_conversions
        FROM campaign WHERE segments.date BETWEEN '2026-01-01' AND '%s'
        ORDER BY segments.month""" % today_local)]

    # ------- 6. SEARCH TERMS, Patio+Pavers, all retained history -------
    for label, start in (("st_alltime", "2026-01-01"),
                         ("st_90d", (today_local - timedelta(days=90)).isoformat()),
                         ("st_30d", (today_local - timedelta(days=30)).isoformat())):
        out[label] = [{
            "term": x.search_term_view.search_term,
            "status": enum_name(x.search_term_view.status),
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
            "keyword": x.segments.keyword.info.text,
            "keyword_match_type": enum_name(x.segments.keyword.info.match_type),
            "cost": m(x.metrics.cost_micros), "impressions": x.metrics.impressions,
            "clicks": x.metrics.clicks, "conversions": round(x.metrics.conversions, 4),
            "all_conversions": round(x.metrics.all_conversions, 4),
        } for x in r.rows(label, """
            SELECT search_term_view.search_term, search_term_view.status,
                   campaign.id, campaign.name, ad_group.id, ad_group.name,
                   segments.keyword.info.text, segments.keyword.info.match_type,
                   metrics.cost_micros, metrics.impressions, metrics.clicks,
                   metrics.conversions, metrics.all_conversions
            FROM search_term_view
            WHERE segments.date BETWEEN '%s' AND '%s'
            ORDER BY metrics.cost_micros DESC""" % (start, today_local))]

    # ------- 7. KEYWORD PERFORMANCE, all time -------
    out["keyword_perf_alltime"] = [{
        "criterion_id": str(x.ad_group_criterion.criterion_id),
        "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "text": x.ad_group_criterion.keyword.text,
        "match_type": enum_name(x.ad_group_criterion.keyword.match_type),
        "status": enum_name(x.ad_group_criterion.status),
        "cost": m(x.metrics.cost_micros), "impressions": x.metrics.impressions,
        "clicks": x.metrics.clicks, "conversions": round(x.metrics.conversions, 4),
        "all_conversions": round(x.metrics.all_conversions, 4),
        "avg_cpc": m(x.metrics.average_cpc),
        "search_rank_lost_is": x.metrics.search_rank_lost_impression_share or None,
    } for x in r.rows("keyword_perf_alltime", """
        SELECT ad_group_criterion.criterion_id, ad_group.id, ad_group.name,
               campaign.id, campaign.name, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               metrics.cost_micros, metrics.impressions, metrics.clicks,
               metrics.conversions, metrics.all_conversions, metrics.average_cpc,
               metrics.search_rank_lost_impression_share
        FROM keyword_view WHERE segments.date BETWEEN '2026-01-01' AND '%s'
        ORDER BY metrics.cost_micros DESC""" % today_local)]

    # ------- 8. AD PERFORMANCE -------
    out["ad_perf_alltime"] = [{
        "ad_id": str(x.ad_group_ad.ad.id), "ad_group_id": str(x.ad_group.id),
        "ad_group_name": x.ad_group.name, "campaign_name": x.campaign.name,
        "status": enum_name(x.ad_group_ad.status),
        "cost": m(x.metrics.cost_micros), "impressions": x.metrics.impressions,
        "clicks": x.metrics.clicks, "conversions": round(x.metrics.conversions, 4),
    } for x in r.rows("ad_perf_alltime", """
        SELECT ad_group_ad.ad.id, ad_group.id, ad_group.name, campaign.name,
               ad_group_ad.status, metrics.cost_micros, metrics.impressions,
               metrics.clicks, metrics.conversions
        FROM ad_group_ad WHERE segments.date BETWEEN '2026-01-01' AND '%s'"""
        % today_local)]

    # ------- 9. TRUE USER LOCATION -------
    out["user_location_city"] = [{
        "location_type": enum_name(x.geographic_view.location_type),
        "geo_target_city": x.segments.geo_target_city,
        "geo_target_county": x.segments.geo_target_county,
        "geo_target_metro": x.segments.geo_target_metro,
        "geo_target_state": x.segments.geo_target_state,
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "cost": m(x.metrics.cost_micros), "clicks": x.metrics.clicks,
        "impressions": x.metrics.impressions,
        "conversions": round(x.metrics.conversions, 4),
    } for x in r.rows("geographic_view_city", """
        SELECT geographic_view.location_type, segments.geo_target_city,
               segments.geo_target_county, segments.geo_target_metro,
               segments.geo_target_state, campaign.id, campaign.name,
               metrics.cost_micros, metrics.clicks, metrics.impressions,
               metrics.conversions
        FROM geographic_view WHERE segments.date BETWEEN '2026-01-01' AND '%s'
        ORDER BY metrics.cost_micros DESC""" % today_local)]

    out["geographic_view"] = [{
        "location_type": enum_name(x.geographic_view.location_type),
        "country_criterion_id": str(x.geographic_view.country_criterion_id),
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "cost": m(x.metrics.cost_micros), "clicks": x.metrics.clicks,
        "impressions": x.metrics.impressions,
        "conversions": round(x.metrics.conversions, 4),
    } for x in r.rows("geographic_view", """
        SELECT geographic_view.location_type, geographic_view.country_criterion_id,
               campaign.id, campaign.name, metrics.cost_micros, metrics.clicks,
               metrics.impressions, metrics.conversions
        FROM geographic_view WHERE segments.date BETWEEN '2026-01-01' AND '%s'"""
        % today_local)]

    out["location_view"] = [{
        "campaign_criterion": x.location_view.resource_name,
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "geo_target_constant": x.campaign_criterion.location.geo_target_constant,
        "cost": m(x.metrics.cost_micros), "clicks": x.metrics.clicks,
        "impressions": x.metrics.impressions,
        "conversions": round(x.metrics.conversions, 4),
    } for x in r.rows("location_view", """
        SELECT location_view.resource_name, campaign.id, campaign.name,
               campaign_criterion.location.geo_target_constant,
               metrics.cost_micros, metrics.clicks, metrics.impressions,
               metrics.conversions
        FROM location_view WHERE segments.date BETWEEN '2026-01-01' AND '%s'
        ORDER BY metrics.cost_micros DESC""" % today_local)]

    # ------- 10. DEVICE / DAY-HOUR -------
    out["device"] = [{
        "device": enum_name(x.segments.device), "campaign_id": str(x.campaign.id),
        "campaign_name": x.campaign.name, "cost": m(x.metrics.cost_micros),
        "clicks": x.metrics.clicks, "impressions": x.metrics.impressions,
        "conversions": round(x.metrics.conversions, 4),
    } for x in r.rows("device", """
        SELECT segments.device, campaign.id, campaign.name, metrics.cost_micros,
               metrics.clicks, metrics.impressions, metrics.conversions
        FROM campaign WHERE segments.date BETWEEN '2026-01-01' AND '%s'"""
        % today_local)]

    out["day_hour"] = [{
        "day": enum_name(x.segments.day_of_week), "hour": x.segments.hour,
        "campaign_id": str(x.campaign.id), "cost": m(x.metrics.cost_micros),
        "clicks": x.metrics.clicks, "conversions": round(x.metrics.conversions, 4),
    } for x in r.rows("day_hour", """
        SELECT segments.day_of_week, segments.hour, campaign.id,
               metrics.cost_micros, metrics.clicks, metrics.conversions
        FROM campaign WHERE segments.date BETWEEN '2026-01-01' AND '%s'
          AND campaign.id IN (%s, %s)""" % (today_local, PATIO, PAVERS))]

    # ------- 11. LANDING PAGES -------
    out["landing_page_view"] = [{
        "unexpanded_final_url": x.landing_page_view.unexpanded_final_url,
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "cost": m(x.metrics.cost_micros), "clicks": x.metrics.clicks,
        "impressions": x.metrics.impressions,
        "conversions": round(x.metrics.conversions, 4),
    } for x in r.rows("landing_page_view", """
        SELECT landing_page_view.unexpanded_final_url, campaign.id, campaign.name,
               metrics.cost_micros, metrics.clicks, metrics.impressions,
               metrics.conversions
        FROM landing_page_view WHERE segments.date BETWEEN '2026-01-01' AND '%s'"""
        % today_local)]

    # ------- 12. CALL VIEW (no date filter allowed) -------
    out["call_view"] = [{
        "campaign_id": str(x.campaign.id) if x.campaign.id else None,
        "call_status": enum_name(x.call_view.call_status),
        "duration_seconds": x.call_view.call_duration_seconds,
        "type": enum_name(x.call_view.call_tracking_display_location),
        "start_time": x.call_view.start_call_date_time,
    } for x in r.rows("call_view", """
        SELECT call_view.call_status, call_view.call_duration_seconds,
               call_view.call_tracking_display_location,
               call_view.start_call_date_time, campaign.id
        FROM call_view""")]

    # ------- 13. CHANGE EVENTS (30-day cap, both bounds required) -------
    lo = (today_local - timedelta(days=28)).isoformat()
    out["change_events"] = [{
        "when": x.change_event.change_date_time,
        "resource_type": enum_name(x.change_event.change_resource_type),
        "resource": x.change_event.change_resource_name,
        "operation": enum_name(x.change_event.resource_change_operation),
        "client_type": enum_name(x.change_event.client_type),
        "campaign": x.change_event.campaign,
        "changed_fields": list(x.change_event.changed_fields.paths)
                          if x.change_event.changed_fields else [],
    } for x in r.rows("change_event_28d", """
        SELECT change_event.change_date_time, change_event.change_resource_type,
               change_event.change_resource_name,
               change_event.resource_change_operation, change_event.client_type,
               change_event.campaign, change_event.changed_fields
        FROM change_event
        WHERE change_event.change_date_time >= '%s 00:00:00'
          AND change_event.change_date_time <= '%s 23:59:59'
        ORDER BY change_event.change_date_time DESC LIMIT 2000"""
        % (lo, today_local))]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out["read_log"] = {"ok": r.ok, "errors": r.errors}
    p = OUTDIR / "01b-before-performance.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("\nwrote %s\nerrors: %d" % (p.relative_to(ROOT), len(r.errors)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
