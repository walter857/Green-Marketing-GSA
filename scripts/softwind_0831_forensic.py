#!/usr/bin/env python3
"""Softwind Power Washing - 2026-08-31 full forensic READ-ONLY snapshot.

SELECT statements only. This module constructs no operation and calls no mutate
service. Every section is independently guarded so one bad field cannot lose the
rest of the snapshot.
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
EXPECTED_NAME = "Softwind Power Washing - Live"
OUT = ROOT / "clients" / "softwind-power-washing" / "snapshots"

ERRORS: list[dict] = []


def micros(v) -> float:
    try:
        return round(int(v) / 1_000_000, 4)
    except Exception:
        return 0.0


def run(svc, cid, query, tag):
    """Execute a SELECT and return raw rows, recording any failure."""
    try:
        return list(svc.search(customer_id=cid, query=query))
    except Exception as exc:
        ERRORS.append({"section": tag, "error": str(exc)[:1200]})
        return []


def m(row):
    """Standard metric block."""
    x = row.metrics
    return {
        "impressions": int(x.impressions),
        "clicks": int(x.clicks),
        "cost": micros(x.cost_micros),
        "ctr": round(float(x.ctr) * 100, 4),
        "avg_cpc": micros(x.average_cpc),
        "conversions": round(float(x.conversions), 4),
        "all_conversions": round(float(x.all_conversions), 4),
        "conversions_value": round(float(x.conversions_value), 4),
        "all_conversions_value": round(float(x.all_conversions_value), 4),
    }


METRIC_SELECT = """
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.ctr,
          metrics.average_cpc,
          metrics.conversions,
          metrics.all_conversions,
          metrics.conversions_value,
          metrics.all_conversions_value
"""


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)

    snap: dict = {"meta": {}}

    # ---------- identity + clock ----------
    q = """
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               customer.time_zone, customer.manager, customer.test_account,
               customer.status, customer.auto_tagging_enabled,
               customer.tracking_url_template, customer.final_url_suffix,
               customer.optimization_score,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.conversion_tracking_status,
               customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
               customer.conversion_tracking_setting.google_ads_conversion_customer
        FROM customer LIMIT 1
    """
    rows = run(svc, cid, q, "customer")
    if not rows:
        print("FATAL: could not read customer", json.dumps(ERRORS, indent=2))
        return 2
    c = rows[0].customer
    tz = c.time_zone or "America/New_York"
    now = datetime.now(ZoneInfo(tz))
    snap["meta"] = {
        "generated_account_local": now.isoformat(),
        "account_local_date": now.date().isoformat(),
        "account_time_zone": tz,
        "script": "softwind_0831_forensic.py",
        "mode": "READ-ONLY",
    }
    snap["identity"] = {
        "customer_id": normalize_customer_id(c.id),
        "descriptive_name": c.descriptive_name,
        "name_matches": c.descriptive_name == EXPECTED_NAME,
        "id_matches": normalize_customer_id(c.id) == CID,
        "currency": c.currency_code,
        "time_zone": tz,
        "manager": bool(c.manager),
        "test_account": bool(c.test_account),
        "status": enum_name(c.status),
        "auto_tagging_enabled": bool(c.auto_tagging_enabled),
        "tracking_url_template": c.tracking_url_template or "",
        "final_url_suffix": c.final_url_suffix or "",
        "optimization_score": round(float(c.optimization_score or 0), 6),
        "conversion_tracking_id": str(c.conversion_tracking_setting.conversion_tracking_id or ""),
        "conversion_tracking_status": enum_name(c.conversion_tracking_setting.conversion_tracking_status),
        "enhanced_conversions_for_leads": bool(
            c.conversion_tracking_setting.enhanced_conversions_for_leads_enabled
        ),
        "google_ads_conversion_customer": c.conversion_tracking_setting.google_ads_conversion_customer or "",
    }
    if not (snap["identity"]["name_matches"] and snap["identity"]["id_matches"]):
        print("FATAL: identity mismatch")
        return 2

    # ---------- account budget / billing ----------
    q = """
        SELECT account_budget.id, account_budget.status, account_budget.name,
               account_budget.approved_spending_limit_type,
               account_budget.approved_spending_limit_micros,
               account_budget.adjusted_spending_limit_type,
               account_budget.adjusted_spending_limit_micros,
               account_budget.amount_served_micros,
               account_budget.total_adjustments_micros
        FROM account_budget
    """
    snap["account_budget"] = [
        {
            "id": str(r.account_budget.id),
            "name": r.account_budget.name,
            "status": enum_name(r.account_budget.status),
            "approved_limit_type": enum_name(r.account_budget.approved_spending_limit_type),
            "approved_limit": micros(r.account_budget.approved_spending_limit_micros),
            "adjusted_limit_type": enum_name(r.account_budget.adjusted_spending_limit_type),
            "amount_served": micros(r.account_budget.amount_served_micros),
        }
        for r in run(svc, cid, q, "account_budget")
    ]

    # ---------- campaigns (ALL statuses) ----------
    q = f"""
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.primary_status, campaign.primary_status_reasons,
               campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
               campaign.bidding_strategy_type, campaign.bidding_strategy_system_status,
               campaign.target_spend.cpc_bid_ceiling_micros,
               campaign.target_spend.target_spend_micros,
               campaign.campaign_budget, campaign.start_date_time, campaign.end_date_time,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign.geo_target_type_setting.negative_geo_target_type,
               campaign.ai_max_setting.enable_ai_max,
               campaign.asset_automation_settings,
               campaign.optimization_score,
               campaign.tracking_url_template, campaign.final_url_suffix,
               campaign.url_custom_parameters,
               campaign.payment_mode, campaign.experiment_type,
               campaign.targeting_setting.target_restrictions,
{METRIC_SELECT}
        FROM campaign
    """
    camps = []
    for r in run(svc, cid, q, "campaign"):
        cp = r.campaign
        camps.append(
            {
                "id": str(cp.id),
                "name": cp.name,
                "status": enum_name(cp.status),
                "serving_status": enum_name(cp.serving_status),
                "primary_status": enum_name(cp.primary_status),
                "primary_status_reasons": [enum_name(x) for x in cp.primary_status_reasons],
                "channel": enum_name(cp.advertising_channel_type),
                "sub_channel": enum_name(cp.advertising_channel_sub_type),
                "bidding_strategy_type": enum_name(cp.bidding_strategy_type),
                "bidding_system_status": enum_name(cp.bidding_strategy_system_status),
                "cpc_bid_ceiling": micros(cp.target_spend.cpc_bid_ceiling_micros),
                "budget_resource": cp.campaign_budget,
                "budget_id": cp.campaign_budget.split("/")[-1] if cp.campaign_budget else "",
                "start": cp.start_date_time,
                "end": cp.end_date_time,
                "net_google_search": bool(cp.network_settings.target_google_search),
                "net_search_partners": bool(cp.network_settings.target_search_network),
                "net_display": bool(cp.network_settings.target_content_network),
                "net_partner_search": bool(cp.network_settings.target_partner_search_network),
                "geo_positive": enum_name(cp.geo_target_type_setting.positive_geo_target_type),
                "geo_negative": enum_name(cp.geo_target_type_setting.negative_geo_target_type),
                "ai_max": bool(cp.ai_max_setting.enable_ai_max),
                "asset_automation": [
                    {
                        "type": enum_name(a.asset_automation_type),
                        "status": enum_name(a.asset_automation_status),
                    }
                    for a in cp.asset_automation_settings
                ],
                "optimization_score": round(float(cp.optimization_score or 0), 6),
                "tracking_url_template": cp.tracking_url_template or "",
                "final_url_suffix": cp.final_url_suffix or "",
                "custom_parameters": [
                    {"key": p.key, "value": p.value} for p in cp.url_custom_parameters
                ],
                "targeting_restrictions": [
                    {
                        "dimension": enum_name(t.targeting_dimension),
                        "bid_only": bool(t.bid_only),
                    }
                    for t in cp.targeting_setting.target_restrictions
                ],
                "metrics_all_time": m(r),
            }
        )
    snap["campaigns"] = camps
    live_ids = [c_["id"] for c_ in camps if c_["status"] != "REMOVED"]

    # ---------- budgets ----------
    q = """
        SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
               campaign_budget.status, campaign_budget.delivery_method,
               campaign_budget.explicitly_shared, campaign_budget.reference_count,
               campaign_budget.total_amount_micros, campaign_budget.period,
               campaign_budget.has_recommended_budget
        FROM campaign_budget
    """
    snap["budgets"] = [
        {
            "id": str(r.campaign_budget.id),
            "name": r.campaign_budget.name,
            "amount": micros(r.campaign_budget.amount_micros),
            "status": enum_name(r.campaign_budget.status),
            "delivery": enum_name(r.campaign_budget.delivery_method),
            "explicitly_shared": bool(r.campaign_budget.explicitly_shared),
            "reference_count": int(r.campaign_budget.reference_count),
            "period": enum_name(r.campaign_budget.period),
        }
        for r in run(svc, cid, q, "campaign_budget")
    ]

    # ---------- ad groups ----------
    q = f"""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, ad_group.status,
               ad_group.type, ad_group.cpc_bid_micros, ad_group.primary_status,
               ad_group.primary_status_reasons,
               ad_group.tracking_url_template, ad_group.final_url_suffix,
               metrics.search_rank_lost_impression_share,
               metrics.search_impression_share,
               metrics.search_top_impression_share,
               metrics.search_absolute_top_impression_share,
               metrics.top_impression_percentage,
               metrics.absolute_top_impression_percentage,
{METRIC_SELECT}
        FROM ad_group
    """
    ags = []
    for r in run(svc, cid, q, "ad_group"):
        a = r.ad_group
        d = {
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "ad_group_id": str(a.id),
            "ad_group_name": a.name,
            "status": enum_name(a.status),
            "type": enum_name(a.type_),
            "cpc_bid": micros(a.cpc_bid_micros),
            "primary_status": enum_name(a.primary_status),
            "primary_status_reasons": [enum_name(x) for x in a.primary_status_reasons],
            "metrics_all_time": m(r),
        }
        try:
            d["search_is"] = round(float(r.metrics.search_impression_share) * 100, 2)
            d["lost_is_rank"] = round(float(r.metrics.search_rank_lost_impression_share) * 100, 2)
            d["top_share"] = round(float(r.metrics.search_top_impression_share) * 100, 2)
            d["abs_top_share"] = round(
                float(r.metrics.search_absolute_top_impression_share) * 100, 2
            )
            d["top_pct"] = round(float(r.metrics.top_impression_percentage) * 100, 2)
            d["abs_top_pct"] = round(
                float(r.metrics.absolute_top_impression_percentage) * 100, 2
            )
        except Exception:
            pass
        ags.append(d)
    snap["ad_groups"] = ags

    # ---------- keywords (positive) ----------
    q = f"""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.system_serving_status,
               ad_group_criterion.approval_status,
               ad_group_criterion.quality_info.quality_score,
               ad_group_criterion.quality_info.creative_quality_score,
               ad_group_criterion.quality_info.post_click_quality_score,
               ad_group_criterion.quality_info.search_predicted_ctr,
               ad_group_criterion.position_estimates.first_page_cpc_micros,
               ad_group_criterion.position_estimates.top_of_page_cpc_micros,
               ad_group_criterion.position_estimates.first_position_cpc_micros,
               ad_group_criterion.effective_cpc_bid_micros,
               ad_group_criterion.final_urls,
               metrics.search_impression_share,
               metrics.search_rank_lost_impression_share,
               metrics.top_impression_percentage,
               metrics.absolute_top_impression_percentage,
{METRIC_SELECT}
        FROM keyword_view
    """
    kws = []
    for r in run(svc, cid, q, "keyword_view"):
        k = r.ad_group_criterion
        d = {
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id),
            "ad_group_name": r.ad_group.name,
            "criterion_id": str(k.criterion_id),
            "text": k.keyword.text,
            "match_type": enum_name(k.keyword.match_type),
            "status": enum_name(k.status),
            "system_serving_status": enum_name(k.system_serving_status),
            "approval_status": enum_name(k.approval_status),
            "quality_score": int(k.quality_info.quality_score or 0),
            "qs_ad_relevance": enum_name(k.quality_info.creative_quality_score),
            "qs_lp_experience": enum_name(k.quality_info.post_click_quality_score),
            "qs_expected_ctr": enum_name(k.quality_info.search_predicted_ctr),
            "est_first_page_cpc": micros(k.position_estimates.first_page_cpc_micros),
            "est_top_of_page_cpc": micros(k.position_estimates.top_of_page_cpc_micros),
            "est_first_position_cpc": micros(k.position_estimates.first_position_cpc_micros),
            "effective_cpc_bid": micros(k.effective_cpc_bid_micros),
            "final_urls": list(k.final_urls),
            "metrics_all_time": m(r),
        }
        try:
            d["search_is"] = round(float(r.metrics.search_impression_share) * 100, 2)
            d["lost_is_rank"] = round(float(r.metrics.search_rank_lost_impression_share) * 100, 2)
            d["top_pct"] = round(float(r.metrics.top_impression_percentage) * 100, 2)
            d["abs_top_pct"] = round(float(r.metrics.absolute_top_impression_percentage) * 100, 2)
        except Exception:
            pass
        kws.append(d)
    snap["keywords"] = kws

    # ---------- ad group negatives ----------
    q = """
        SELECT campaign.id, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.type
        FROM ad_group_criterion
        WHERE ad_group_criterion.negative = TRUE
          AND ad_group_criterion.status != 'REMOVED'
    """
    snap["ad_group_negatives"] = [
        {
            "campaign_id": str(r.campaign.id),
            "ad_group_id": str(r.ad_group.id),
            "ad_group_name": r.ad_group.name,
            "criterion_id": str(r.ad_group_criterion.criterion_id),
            "text": r.ad_group_criterion.keyword.text,
            "match_type": enum_name(r.ad_group_criterion.keyword.match_type),
            "status": enum_name(r.ad_group_criterion.status),
        }
        for r in run(svc, cid, q, "ad_group_negatives")
    ]

    # ---------- campaign criteria (negatives, geo, schedule, audience, ip) ----------
    q = """
        SELECT campaign.id, campaign.name, campaign_criterion.criterion_id,
               campaign_criterion.type, campaign_criterion.negative,
               campaign_criterion.status,
               campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
               campaign_criterion.location.geo_target_constant,
               campaign_criterion.ad_schedule.day_of_week,
               campaign_criterion.ad_schedule.start_hour,
               campaign_criterion.ad_schedule.start_minute,
               campaign_criterion.ad_schedule.end_hour,
               campaign_criterion.ad_schedule.end_minute,
               campaign_criterion.language.language_constant,
               campaign_criterion.device.type,
               campaign_criterion.gender.type,
               campaign_criterion.age_range.type,
               campaign_criterion.income_range.type,
               campaign_criterion.user_list.user_list,
               campaign_criterion.ip_block.ip_address,
               campaign_criterion.bid_modifier
        FROM campaign_criterion
        WHERE campaign_criterion.status != 'REMOVED'
    """
    crit = []
    for r in run(svc, cid, q, "campaign_criterion"):
        cc = r.campaign_criterion
        t = enum_name(cc.type_)
        d = {
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "criterion_id": str(cc.criterion_id),
            "type": t,
            "negative": bool(cc.negative),
            "status": enum_name(cc.status),
            "bid_modifier": round(float(cc.bid_modifier or 0), 4),
        }
        if t == "KEYWORD":
            d["text"] = cc.keyword.text
            d["match_type"] = enum_name(cc.keyword.match_type)
        elif t == "LOCATION":
            d["geo_target_constant"] = cc.location.geo_target_constant
            d["geo_id"] = (cc.location.geo_target_constant or "").split("/")[-1]
        elif t == "AD_SCHEDULE":
            d["day"] = enum_name(cc.ad_schedule.day_of_week)
            d["start_hour"] = int(cc.ad_schedule.start_hour)
            d["end_hour"] = int(cc.ad_schedule.end_hour)
            d["start_minute"] = enum_name(cc.ad_schedule.start_minute)
            d["end_minute"] = enum_name(cc.ad_schedule.end_minute)
        elif t == "LANGUAGE":
            d["language"] = cc.language.language_constant
        elif t == "DEVICE":
            d["device"] = enum_name(cc.device.type_)
        elif t == "GENDER":
            d["gender"] = enum_name(cc.gender.type_)
        elif t == "AGE_RANGE":
            d["age_range"] = enum_name(cc.age_range.type_)
        elif t == "INCOME_RANGE":
            d["income_range"] = enum_name(cc.income_range.type_)
        elif t == "USER_LIST":
            d["user_list"] = cc.user_list.user_list
        elif t == "IP_BLOCK":
            d["ip"] = cc.ip_block.ip_address
        crit.append(d)
    snap["campaign_criteria"] = crit

    # ---------- ads ----------
    q = f"""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type,
               ad_group_ad.policy_summary.approval_status,
               ad_group_ad.policy_summary.review_status,
               ad_group_ad.policy_summary.policy_topic_entries,
               ad_group_ad.ad_strength, ad_group_ad.ad.final_urls,
               ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions,
               ad_group_ad.ad.responsive_search_ad.path1,
               ad_group_ad.ad.responsive_search_ad.path2,
               ad_group_ad.ad.tracking_url_template,
               ad_group_ad.ad.final_url_suffix,
{METRIC_SELECT}
        FROM ad_group_ad
        WHERE ad_group_ad.status != 'REMOVED'
    """
    ads = []
    for r in run(svc, cid, q, "ad_group_ad"):
        a = r.ad_group_ad
        rsa = a.ad.responsive_search_ad
        ads.append(
            {
                "campaign_id": str(r.campaign.id),
                "campaign_name": r.campaign.name,
                "ad_group_id": str(r.ad_group.id),
                "ad_group_name": r.ad_group.name,
                "ad_id": str(a.ad.id),
                "status": enum_name(a.status),
                "type": enum_name(a.ad.type_),
                "approval_status": enum_name(a.policy_summary.approval_status),
                "review_status": enum_name(a.policy_summary.review_status),
                "policy_topics": [
                    enum_name(p.type_) + ":" + p.topic for p in a.policy_summary.policy_topic_entries
                ],
                "ad_strength": enum_name(a.ad_strength),
                "final_urls": list(a.ad.final_urls),
                "path1": rsa.path1,
                "path2": rsa.path2,
                "headlines": [
                    {"text": h.text, "pinned": enum_name(h.pinned_field) if h.pinned_field else ""}
                    for h in rsa.headlines
                ],
                "descriptions": [
                    {"text": h.text, "pinned": enum_name(h.pinned_field) if h.pinned_field else ""}
                    for h in rsa.descriptions
                ],
                "tracking_url_template": a.ad.tracking_url_template or "",
                "final_url_suffix": a.ad.final_url_suffix or "",
                "metrics_all_time": m(r),
            }
        )
    snap["ads"] = ads

    # ---------- assets ----------
    q = """
        SELECT asset.id, asset.name, asset.type, asset.final_urls, asset.source,
               asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
               asset.sitelink_asset.description2,
               asset.callout_asset.callout_text,
               asset.structured_snippet_asset.header,
               asset.structured_snippet_asset.values,
               asset.call_asset.phone_number, asset.call_asset.country_code,
               asset.call_asset.call_conversion_action,
               asset.call_asset.call_conversion_reporting_state,
               asset.text_asset.text,
               asset.image_asset.full_size.url,
               asset.policy_summary.approval_status
        FROM asset
    """
    assets = {}
    for r in run(svc, cid, q, "asset"):
        a = r.asset
        t = enum_name(a.type_)
        d = {
            "asset_id": str(a.id),
            "name": a.name or "",
            "type": t,
            "source": enum_name(a.source),
            "final_urls": list(a.final_urls),
            "approval_status": enum_name(a.policy_summary.approval_status),
        }
        if t == "SITELINK":
            d["link_text"] = a.sitelink_asset.link_text
            d["desc1"] = a.sitelink_asset.description1
            d["desc2"] = a.sitelink_asset.description2
        elif t == "CALLOUT":
            d["text"] = a.callout_asset.callout_text
        elif t == "STRUCTURED_SNIPPET":
            d["header"] = a.structured_snippet_asset.header
            d["values"] = list(a.structured_snippet_asset.values)
        elif t == "CALL":
            d["phone"] = a.call_asset.phone_number
            d["country"] = a.call_asset.country_code
            d["call_conversion_action"] = a.call_asset.call_conversion_action
            d["call_conversion_reporting_state"] = enum_name(
                a.call_asset.call_conversion_reporting_state
            )
        elif t in ("TEXT", "BUSINESS_NAME"):
            d["text"] = a.text_asset.text
        elif t in ("IMAGE", "LOGO", "MARKETING_IMAGE"):
            d["url"] = a.image_asset.full_size.url
        assets[str(a.id)] = d
    snap["assets"] = assets

    # ---------- asset links ----------
    q = f"""
        SELECT campaign.id, campaign.name, campaign_asset.asset,
               campaign_asset.field_type, campaign_asset.status,
               campaign_asset.primary_status,
{METRIC_SELECT}
        FROM campaign_asset
        WHERE campaign_asset.status != 'REMOVED'
    """
    snap["campaign_assets"] = [
        {
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "asset_id": r.campaign_asset.asset.split("/")[-1],
            "field_type": enum_name(r.campaign_asset.field_type),
            "status": enum_name(r.campaign_asset.status),
            "primary_status": enum_name(r.campaign_asset.primary_status),
            "metrics_all_time": m(r),
        }
        for r in run(svc, cid, q, "campaign_asset")
    ]

    q = """
        SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status
        FROM customer_asset WHERE customer_asset.status != 'REMOVED'
    """
    snap["customer_assets"] = [
        {
            "asset_id": r.customer_asset.asset.split("/")[-1],
            "field_type": enum_name(r.customer_asset.field_type),
            "status": enum_name(r.customer_asset.status),
        }
        for r in run(svc, cid, q, "customer_asset")
    ]

    q = """
        SELECT campaign.id, ad_group.id, ad_group.name, ad_group_asset.asset,
               ad_group_asset.field_type, ad_group_asset.status
        FROM ad_group_asset WHERE ad_group_asset.status != 'REMOVED'
    """
    snap["ad_group_assets"] = [
        {
            "campaign_id": str(r.campaign.id),
            "ad_group_id": str(r.ad_group.id),
            "ad_group_name": r.ad_group.name,
            "asset_id": r.ad_group_asset.asset.split("/")[-1],
            "field_type": enum_name(r.ad_group_asset.field_type),
            "status": enum_name(r.ad_group_asset.status),
        }
        for r in run(svc, cid, q, "ad_group_asset")
    ]

    # ---------- conversion actions ----------
    q = """
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.type, conversion_action.category,
               conversion_action.counting_type, conversion_action.primary_for_goal,
               conversion_action.include_in_conversions_metric,
               conversion_action.click_through_lookback_window_days,
               conversion_action.view_through_lookback_window_days,
               conversion_action.phone_call_duration_seconds,
               conversion_action.value_settings.default_value,
               conversion_action.value_settings.always_use_default_value,
               conversion_action.attribution_model_settings.attribution_model,
               conversion_action.origin, conversion_action.owner_customer
        FROM conversion_action
    """
    snap["conversion_actions"] = [
        {
            "id": str(r.conversion_action.id),
            "name": r.conversion_action.name,
            "status": enum_name(r.conversion_action.status),
            "type": enum_name(r.conversion_action.type_),
            "category": enum_name(r.conversion_action.category),
            "counting": enum_name(r.conversion_action.counting_type),
            "primary_for_goal": bool(r.conversion_action.primary_for_goal),
            "include_in_conversions_metric": bool(
                r.conversion_action.include_in_conversions_metric
            ),
            "click_lookback_days": int(r.conversion_action.click_through_lookback_window_days),
            "phone_call_duration_seconds": int(
                r.conversion_action.phone_call_duration_seconds
            ),
            "default_value": round(float(r.conversion_action.value_settings.default_value), 4),
            "always_use_default_value": bool(
                r.conversion_action.value_settings.always_use_default_value
            ),
            "attribution_model": enum_name(
                r.conversion_action.attribution_model_settings.attribution_model
            ),
            "origin": enum_name(r.conversion_action.origin),
            "owner_customer": r.conversion_action.owner_customer or "",
        }
        for r in run(svc, cid, q, "conversion_action")
    ]

    # ---------- conversion goals ----------
    q = """
        SELECT campaign.id, campaign.name,
               campaign_conversion_goal.category, campaign_conversion_goal.origin,
               campaign_conversion_goal.biddable
        FROM campaign_conversion_goal
    """
    snap["campaign_conversion_goals"] = [
        {
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "category": enum_name(r.campaign_conversion_goal.category),
            "origin": enum_name(r.campaign_conversion_goal.origin),
            "biddable": bool(r.campaign_conversion_goal.biddable),
        }
        for r in run(svc, cid, q, "campaign_conversion_goal")
    ]

    q = """
        SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
               customer_conversion_goal.biddable
        FROM customer_conversion_goal
    """
    snap["customer_conversion_goals"] = [
        {
            "category": enum_name(r.customer_conversion_goal.category),
            "origin": enum_name(r.customer_conversion_goal.origin),
            "biddable": bool(r.customer_conversion_goal.biddable),
        }
        for r in run(svc, cid, q, "customer_conversion_goal")
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    path = OUT / f"forensic-structure-{stamp}.json"
    snap["errors"] = ERRORS
    path.write_text(json.dumps(snap, indent=2), encoding="utf-8")

    print(f"WROTE {path}")
    print(f"campaigns={len(snap['campaigns'])} live={len(live_ids)}")
    print(f"ad_groups={len(snap['ad_groups'])} keywords={len(snap['keywords'])}")
    print(f"ads={len(snap['ads'])} assets={len(snap['assets'])}")
    print(f"campaign_criteria={len(snap['campaign_criteria'])}")
    print(f"ad_group_negatives={len(snap['ad_group_negatives'])}")
    print(f"conversion_actions={len(snap['conversion_actions'])}")
    if ERRORS:
        print("ERRORS:")
        for e in ERRORS:
            print("  -", e["section"], e["error"][:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
