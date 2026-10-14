#!/usr/bin/env python3
"""Softwind Power Washing - 2026-08-31 forensic PERFORMANCE read (READ-ONLY).

Daily, device, geo, hour, day-of-week, demographic, audience, click-type,
conversion-action and search-term segmentation. SELECT statements only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
OUT = ROOT / "clients" / "softwind-power-washing" / "snapshots"
START = "2026-08-01"
ALLTIME_START = "2026-07-01"

ERRORS: list[dict] = []


def micros(v) -> float:
    try:
        return round(int(v) / 1_000_000, 4)
    except Exception:
        return 0.0


def run(svc, cid, query, tag):
    try:
        return list(svc.search(customer_id=cid, query=query))
    except Exception as exc:
        ERRORS.append({"section": tag, "error": str(exc)[:1000]})
        return []


def m(row):
    x = row.metrics
    return {
        "impressions": int(x.impressions),
        "clicks": int(x.clicks),
        "cost": micros(x.cost_micros),
        "conversions": round(float(x.conversions), 4),
        "all_conversions": round(float(x.all_conversions), 4),
    }


MS = """
          metrics.impressions, metrics.clicks, metrics.cost_micros,
          metrics.conversions, metrics.all_conversions
"""


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    now = datetime.now(ZoneInfo("America/New_York"))
    today = now.date().isoformat()

    out: dict = {
        "meta": {
            "generated_account_local": now.isoformat(),
            "account_local_date": today,
            "mode": "READ-ONLY",
        }
    }

    # ---- daily campaign performance, whole life ----
    q = f"""
        SELECT campaign.id, campaign.name, segments.date,
               metrics.search_impression_share,
               metrics.search_budget_lost_impression_share,
               metrics.search_rank_lost_impression_share,
               metrics.search_top_impression_share,
               metrics.search_absolute_top_impression_share,
               metrics.top_impression_percentage,
               metrics.absolute_top_impression_percentage,
               metrics.invalid_clicks, metrics.invalid_click_rate,
               metrics.average_cpc, metrics.ctr,
{MS}
        FROM campaign
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
        ORDER BY segments.date
    """
    daily = []
    for r in run(svc, cid, q, "daily_campaign"):
        d = m(r)
        d.update(
            {
                "date": r.segments.date,
                "campaign_id": str(r.campaign.id),
                "campaign_name": r.campaign.name,
                "avg_cpc": micros(r.metrics.average_cpc),
                "ctr": round(float(r.metrics.ctr) * 100, 4),
                "search_is": round(float(r.metrics.search_impression_share) * 100, 2),
                "lost_is_budget": round(
                    float(r.metrics.search_budget_lost_impression_share) * 100, 2
                ),
                "lost_is_rank": round(
                    float(r.metrics.search_rank_lost_impression_share) * 100, 2
                ),
                "top_share": round(float(r.metrics.search_top_impression_share) * 100, 2),
                "abs_top_share": round(
                    float(r.metrics.search_absolute_top_impression_share) * 100, 2
                ),
                "invalid_clicks": int(r.metrics.invalid_clicks),
                "invalid_click_rate": round(float(r.metrics.invalid_click_rate) * 100, 4),
            }
        )
        daily.append(d)
    out["daily_campaign"] = daily

    # ---- account daily totals ----
    q = f"""
        SELECT segments.date, metrics.invalid_clicks, metrics.invalid_click_rate,
               metrics.average_cpc, metrics.ctr,
{MS}
        FROM customer
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
        ORDER BY segments.date
    """
    out["daily_account"] = [
        dict(
            m(r),
            date=r.segments.date,
            avg_cpc=micros(r.metrics.average_cpc),
            ctr=round(float(r.metrics.ctr) * 100, 4),
            invalid_clicks=int(r.metrics.invalid_clicks),
            invalid_click_rate=round(float(r.metrics.invalid_click_rate) * 100, 4),
        )
        for r in run(svc, cid, q, "daily_account")
    ]

    # ---- ad group daily/window ----
    for label, lo, hi in [("all_time", ALLTIME_START, today)]:
        q = f"""
            SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
                   ad_group.status, segments.date,
                   metrics.average_cpc, metrics.ctr,
{MS}
            FROM ad_group
            WHERE segments.date BETWEEN '{lo}' AND '{hi}'
        """
        out[f"daily_ad_group_{label}"] = [
            dict(
                m(r),
                date=r.segments.date,
                campaign_id=str(r.campaign.id),
                campaign_name=r.campaign.name,
                ad_group_id=str(r.ad_group.id),
                ad_group_name=r.ad_group.name,
                status=enum_name(r.ad_group.status),
            )
            for r in run(svc, cid, q, f"daily_ad_group_{label}")
        ]

    # ---- keyword daily ----
    q = f"""
        SELECT campaign.id, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, segments.date,
               metrics.average_cpc,
{MS}
        FROM keyword_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["daily_keyword"] = [
        dict(
            m(r),
            date=r.segments.date,
            campaign_id=str(r.campaign.id),
            ad_group_id=str(r.ad_group.id),
            ad_group_name=r.ad_group.name,
            criterion_id=str(r.ad_group_criterion.criterion_id),
            text=r.ad_group_criterion.keyword.text,
            match_type=enum_name(r.ad_group_criterion.keyword.match_type),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "daily_keyword")
    ]

    # ---- ad daily ----
    q = f"""
        SELECT campaign.id, ad_group.id, ad_group.name, ad_group_ad.ad.id,
               ad_group_ad.status, segments.date, metrics.average_cpc, metrics.ctr,
{MS}
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["daily_ad"] = [
        dict(
            m(r),
            date=r.segments.date,
            campaign_id=str(r.campaign.id),
            ad_group_id=str(r.ad_group.id),
            ad_group_name=r.ad_group.name,
            ad_id=str(r.ad_group_ad.ad.id),
            status=enum_name(r.ad_group_ad.status),
            avg_cpc=micros(r.metrics.average_cpc),
            ctr=round(float(r.metrics.ctr) * 100, 4),
        )
        for r in run(svc, cid, q, "daily_ad")
    ]

    # ---- search terms (all time, no impression threshold) ----
    q = f"""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               search_term_view.search_term, search_term_view.status,
               segments.keyword.info.text, segments.keyword.info.match_type,
               segments.search_term_match_type, segments.date,
               metrics.average_cpc, metrics.ctr,
{MS}
        FROM search_term_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["search_terms"] = [
        dict(
            m(r),
            date=r.segments.date,
            campaign_id=str(r.campaign.id),
            campaign_name=r.campaign.name,
            ad_group_id=str(r.ad_group.id),
            ad_group_name=r.ad_group.name,
            term=r.search_term_view.search_term,
            term_status=enum_name(r.search_term_view.status),
            matched_keyword=r.segments.keyword.info.text,
            keyword_match_type=enum_name(r.segments.keyword.info.match_type),
            term_match_type=enum_name(r.segments.search_term_match_type),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "search_terms")
    ]

    # ---- device ----
    q = f"""
        SELECT campaign.id, campaign.name, segments.device, segments.date,
               metrics.average_cpc, metrics.ctr,
{MS}
        FROM campaign
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["device"] = [
        dict(
            m(r),
            date=r.segments.date,
            campaign_id=str(r.campaign.id),
            campaign_name=r.campaign.name,
            device=enum_name(r.segments.device),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "device")
    ]

    # ---- hour of day + day of week (campaign level) ----
    q = f"""
        SELECT campaign.id, campaign.name, segments.hour, segments.day_of_week,
               metrics.average_cpc,
{MS}
        FROM campaign
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["hour_dow"] = [
        dict(
            m(r),
            campaign_id=str(r.campaign.id),
            campaign_name=r.campaign.name,
            hour=int(r.segments.hour),
            day_of_week=enum_name(r.segments.day_of_week),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "hour_dow")
    ]

    # ---- geographic (location_view = targeted locations) ----
    q = f"""
        SELECT campaign.id, campaign.name, campaign_criterion.criterion_id,
               segments.date, metrics.average_cpc, metrics.ctr,
{MS}
        FROM location_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["location_view"] = [
        dict(
            m(r),
            date=r.segments.date,
            campaign_id=str(r.campaign.id),
            campaign_name=r.campaign.name,
            criterion_id=str(r.campaign_criterion.criterion_id),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "location_view")
    ]

    # ---- geographic_view: actual user location vs location of interest ----
    q = f"""
        SELECT campaign.id, campaign.name,
               geographic_view.country_criterion_id,
               geographic_view.location_type,
               segments.geo_target_city, segments.geo_target_county,
               segments.geo_target_metro, segments.geo_target_state,
               metrics.average_cpc,
{MS}
        FROM geographic_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["geographic_view"] = [
        dict(
            m(r),
            campaign_id=str(r.campaign.id),
            campaign_name=r.campaign.name,
            location_type=enum_name(r.geographic_view.location_type),
            geo_city=r.segments.geo_target_city,
            geo_county=r.segments.geo_target_county,
            geo_metro=r.segments.geo_target_metro,
            geo_state=r.segments.geo_target_state,
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "geographic_view")
    ]

    # ---- user location view ----
    q = f"""
        SELECT campaign.id, user_location_view.country_criterion_id,
               user_location_view.targeting_location,
               segments.geo_target_city, segments.geo_target_state,
               metrics.average_cpc,
{MS}
        FROM user_location_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["user_location_view"] = [
        dict(
            m(r),
            campaign_id=str(r.campaign.id),
            targeting_location=bool(r.user_location_view.targeting_location),
            geo_city=r.segments.geo_target_city,
            geo_state=r.segments.geo_target_state,
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "user_location_view")
    ]

    # ---- demographics ----
    q = f"""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_criterion.gender.type, ad_group_criterion.criterion_id,
               ad_group_criterion.status, metrics.average_cpc,
{MS}
        FROM gender_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["gender_view"] = [
        dict(
            m(r),
            campaign_id=str(r.campaign.id),
            ad_group_id=str(r.ad_group.id),
            ad_group_name=r.ad_group.name,
            gender=enum_name(r.ad_group_criterion.gender.type_),
            status=enum_name(r.ad_group_criterion.status),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "gender_view")
    ]

    q = f"""
        SELECT campaign.id, ad_group.id, ad_group.name,
               ad_group_criterion.age_range.type, ad_group_criterion.status,
               metrics.average_cpc,
{MS}
        FROM age_range_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["age_range_view"] = [
        dict(
            m(r),
            campaign_id=str(r.campaign.id),
            ad_group_id=str(r.ad_group.id),
            ad_group_name=r.ad_group.name,
            age_range=enum_name(r.ad_group_criterion.age_range.type_),
            status=enum_name(r.ad_group_criterion.status),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "age_range_view")
    ]

    # ---- audiences ----
    q = f"""
        SELECT campaign.id, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.type,
               ad_group_criterion.status,
{MS}
        FROM ad_group_audience_view
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["ad_group_audience_view"] = [
        dict(
            m(r),
            campaign_id=str(r.campaign.id),
            ad_group_id=str(r.ad_group.id),
            ad_group_name=r.ad_group.name,
            criterion_id=str(r.ad_group_criterion.criterion_id),
            type=enum_name(r.ad_group_criterion.type_),
            status=enum_name(r.ad_group_criterion.status),
        )
        for r in run(svc, cid, q, "ad_group_audience_view")
    ]

    # ---- click type (sitelinks etc.) ----
    q = f"""
        SELECT campaign.id, campaign.name, segments.click_type, segments.date,
               metrics.average_cpc,
{MS}
        FROM campaign
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["click_type"] = [
        dict(
            m(r),
            date=r.segments.date,
            campaign_id=str(r.campaign.id),
            campaign_name=r.campaign.name,
            click_type=enum_name(r.segments.click_type),
            avg_cpc=micros(r.metrics.average_cpc),
        )
        for r in run(svc, cid, q, "click_type")
    ]

    # ---- conversions by action (all_conversions, per gaql-field-gotchas) ----
    q = f"""
        SELECT campaign.id, campaign.name, segments.date,
               segments.conversion_action_name, segments.conversion_action_category,
               metrics.all_conversions, metrics.conversions,
               metrics.all_conversions_value, metrics.view_through_conversions
        FROM campaign
        WHERE segments.date BETWEEN '{ALLTIME_START}' AND '{today}'
    """
    out["conversions_by_action"] = [
        {
            "date": r.segments.date,
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "action_name": r.segments.conversion_action_name,
            "action_category": enum_name(r.segments.conversion_action_category),
            "all_conversions": round(float(r.metrics.all_conversions), 4),
            "conversions": round(float(r.metrics.conversions), 4),
            "all_conversions_value": round(float(r.metrics.all_conversions_value), 4),
        }
        for r in run(svc, cid, q, "conversions_by_action")
    ]

    # ---- call log ----
    q = """
        SELECT call_view.caller_area_code, call_view.caller_country_code,
               call_view.call_duration_seconds, call_view.start_call_date_time,
               call_view.call_status, call_view.type, campaign.id, campaign.name
        FROM call_view
    """
    out["call_view"] = [
        {
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "area_code": r.call_view.caller_area_code,
            "country": r.call_view.caller_country_code,
            "duration_seconds": int(r.call_view.call_duration_seconds),
            "start": r.call_view.start_call_date_time,
            "status": enum_name(r.call_view.call_status),
            "type": enum_name(r.call_view.type_),
        }
        for r in run(svc, cid, q, "call_view")
    ]

    # ---- change events (30 day cap, bounded both ends) ----
    q = f"""
        SELECT change_event.change_date_time, change_event.change_resource_type,
               change_event.change_resource_name, change_event.client_type,
               change_event.user_email, change_event.resource_change_operation,
               change_event.changed_fields, campaign.id, campaign.name
        FROM change_event
        WHERE change_event.change_date_time >= '2026-08-01 00:00:00'
          AND change_event.change_date_time <= '{today} 23:59:59'
        ORDER BY change_event.change_date_time DESC
        LIMIT 10000
    """
    out["change_events"] = [
        {
            "when": r.change_event.change_date_time,
            "resource_type": enum_name(r.change_event.change_resource_type),
            "resource": r.change_event.change_resource_name,
            "client_type": enum_name(r.change_event.client_type),
            "user": r.change_event.user_email,
            "operation": enum_name(r.change_event.resource_change_operation),
            "changed_fields": list(r.change_event.changed_fields.paths),
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
        }
        for r in run(svc, cid, q, "change_event")
    ]

    # ---- change_status (longer resource-level view) ----
    q = """
        SELECT change_status.last_change_date_time, change_status.resource_type,
               change_status.resource_status, change_status.campaign,
               change_status.ad_group, change_status.ad_group_criterion,
               change_status.ad_group_ad, change_status.campaign_criterion
        FROM change_status
        WHERE change_status.last_change_date_time >= '2026-07-01 00:00:00'
        ORDER BY change_status.last_change_date_time DESC
        LIMIT 5000
    """
    out["change_status"] = [
        {
            "when": r.change_status.last_change_date_time,
            "resource_type": enum_name(r.change_status.resource_type),
            "resource_status": enum_name(r.change_status.resource_status),
            "campaign": r.change_status.campaign,
            "ad_group": r.change_status.ad_group,
        }
        for r in run(svc, cid, q, "change_status")
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    path = OUT / f"forensic-performance-{stamp}.json"
    out["errors"] = ERRORS
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"WROTE {path}")
    for k, v in out.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)}")
    if ERRORS:
        print("ERRORS:")
        for e in ERRORS:
            print("  -", e["section"], e["error"][:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
