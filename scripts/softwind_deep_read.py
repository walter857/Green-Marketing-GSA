#!/usr/bin/env python3
"""Read-only deep structural snapshot for Softwind Power Washing.

SELECT-only. This script cannot mutate anything: it never constructs an
operation, never calls a mutate service, and only uses GoogleAdsService.search.
"""
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
OUT = ROOT / "clients/softwind-power-washing/snapshots/deep-read-2026-08-25.json"


def micros(v):
    return None if v in (None, 0) else v / 1_000_000


class Reader:
    def __init__(self):
        load_dotenv_if_available(ROOT / ".env")
        self.client = load_google_ads_client()
        self.svc = self.client.get_service("GoogleAdsService")
        self.errors = []

    def rows(self, name, query):
        try:
            return list(self.svc.search(customer_id=CID, query=query))
        except Exception as exc:
            msg = str(exc)
            for marker in ("message: ", "FaultMessage: "):
                if marker in msg:
                    msg = msg.split(marker, 1)[1][:400]
                    break
            self.errors.append({"query": name, "error": msg[:400]})
            print("  !! %s: %s" % (name, msg[:220]), file=sys.stderr)
            return []


def main() -> int:
    r = Reader()
    out = {"customer_id": CID}
    tz = ZoneInfo("America/New_York")
    out["snapshot_taken_account_local"] = datetime.now(tz).isoformat()

    # ---------------- CAMPAIGN SETTINGS ----------------
    q = """
      SELECT
        campaign.id, campaign.name, campaign.status, campaign.serving_status,
        campaign.primary_status, campaign.primary_status_reasons,
        campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
        campaign.start_date_time, campaign.end_date_time,
        campaign.bidding_strategy_type, campaign.bidding_strategy,
        campaign.maximize_conversions.target_cpa_micros,
        campaign.maximize_conversion_value.target_roas,
        campaign.target_spend.cpc_bid_ceiling_micros,
        campaign.target_cpa.target_cpa_micros,
        campaign.target_roas.target_roas,
        campaign.manual_cpc.enhanced_cpc_enabled,
        campaign.network_settings.target_google_search,
        campaign.network_settings.target_search_network,
        campaign.network_settings.target_content_network,
        campaign.network_settings.target_partner_search_network,
        campaign.geo_target_type_setting.positive_geo_target_type,
        campaign.geo_target_type_setting.negative_geo_target_type,
        campaign.targeting_setting.target_restrictions,
        campaign.tracking_url_template, campaign.final_url_suffix,

        campaign.optimization_score,
        campaign.payment_mode,
        campaign.experiment_type,
        campaign.dynamic_search_ads_setting.domain_name,
        campaign.dynamic_search_ads_setting.use_supplied_urls_only,
        campaign.keyword_match_type,
        campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
        campaign_budget.delivery_method, campaign_budget.explicitly_shared,
        campaign_budget.total_amount_micros, campaign_budget.period,
        campaign_budget.status, campaign_budget.recommended_budget_amount_micros,
        campaign_budget.has_recommended_budget, campaign_budget.reference_count
      FROM campaign
      ORDER BY campaign.id
    """
    camps = []
    for row in r.rows("campaign_settings", q):
        c, b = row.campaign, row.campaign_budget
        camps.append({
            "id": str(c.id), "name": c.name,
            "status": enum_name(c.status),
            "serving_status": enum_name(c.serving_status),
            "primary_status": enum_name(c.primary_status),
            "primary_status_reasons": [enum_name(x) for x in c.primary_status_reasons],
            "channel": enum_name(c.advertising_channel_type),
            "sub_type": enum_name(c.advertising_channel_sub_type),
            "start_date_time": c.start_date_time,
            "end_date_time": c.end_date_time or "",
            "bidding_strategy_type": enum_name(c.bidding_strategy_type),
            "portfolio_bidding_strategy": c.bidding_strategy or "",
            "target_spend_cpc_bid_ceiling": micros(c.target_spend.cpc_bid_ceiling_micros),
            "maximize_conversions_target_cpa": micros(c.maximize_conversions.target_cpa_micros),
            "target_cpa": micros(c.target_cpa.target_cpa_micros),
            "target_roas": c.target_roas.target_roas or None,
            "enhanced_cpc": bool(c.manual_cpc.enhanced_cpc_enabled),
            "keyword_match_type_ai_max": enum_name(c.keyword_match_type),
            "network": {
                "google_search": bool(c.network_settings.target_google_search),
                "search_partners": bool(c.network_settings.target_search_network),
                "display": bool(c.network_settings.target_content_network),
                "partner_search": bool(c.network_settings.target_partner_search_network),
            },
            "geo_target_type": {
                "positive": enum_name(c.geo_target_type_setting.positive_geo_target_type),
                "negative": enum_name(c.geo_target_type_setting.negative_geo_target_type),
            },
            "targeting_setting_restrictions": [
                {"dimension": enum_name(t.targeting_dimension), "bid_only": bool(t.bid_only)}
                for t in c.targeting_setting.target_restrictions
            ],
            "tracking_url_template": c.tracking_url_template or "",
            "final_url_suffix": c.final_url_suffix or "",
            
            "optimization_score": float(c.optimization_score or 0),
            "payment_mode": enum_name(c.payment_mode),
            "dsa_domain": c.dynamic_search_ads_setting.domain_name or "",
            "budget": {
                "id": str(b.id), "name": b.name,
                "amount": micros(b.amount_micros),
                "delivery_method": enum_name(b.delivery_method),
                "explicitly_shared": bool(b.explicitly_shared),
                "period": enum_name(b.period),
                "status": enum_name(b.status),
                "recommended_amount": micros(b.recommended_budget_amount_micros),
                "has_recommended_budget": bool(b.has_recommended_budget),
                "reference_count": int(b.reference_count),
            },
        })
    out["campaigns"] = camps

    # ---------------- CONVERSION GOALS ----------------
    q = """
      SELECT campaign.id, campaign.name,
             campaign_conversion_goal.category,
             campaign_conversion_goal.origin,
             campaign_conversion_goal.biddable
      FROM campaign_conversion_goal
    """
    goals = []
    for row in r.rows("campaign_conversion_goal", q):
        g = row.campaign_conversion_goal
        goals.append({
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "category": enum_name(g.category), "origin": enum_name(g.origin),
            "biddable": bool(g.biddable),
        })
    out["campaign_conversion_goals_biddable"] = [g for g in goals if g["biddable"]]
    out["campaign_conversion_goals_total_rows"] = len(goals)

    q = """
      SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
             customer_conversion_goal.biddable
      FROM customer_conversion_goal
    """
    out["customer_conversion_goals_biddable"] = [
        {"category": enum_name(x.customer_conversion_goal.category),
         "origin": enum_name(x.customer_conversion_goal.origin)}
        for x in r.rows("customer_conversion_goal", q)
        if x.customer_conversion_goal.biddable
    ]

    # ---------------- CAMPAIGN CRITERIA ----------------
    q = """
      SELECT campaign.id, campaign.name,
             campaign_criterion.criterion_id, campaign_criterion.type,
             campaign_criterion.negative, campaign_criterion.status,
             campaign_criterion.bid_modifier, campaign_criterion.display_name,
             campaign_criterion.location.geo_target_constant,
             campaign_criterion.proximity.radius,
             campaign_criterion.proximity.radius_units,
             campaign_criterion.proximity.geo_point.latitude_in_micro_degrees,
             campaign_criterion.proximity.geo_point.longitude_in_micro_degrees,
             campaign_criterion.proximity.address.city_name,
             campaign_criterion.proximity.address.postal_code,
             campaign_criterion.proximity.address.province_name,
             campaign_criterion.ad_schedule.day_of_week,
             campaign_criterion.ad_schedule.start_hour,
             campaign_criterion.ad_schedule.start_minute,
             campaign_criterion.ad_schedule.end_hour,
             campaign_criterion.ad_schedule.end_minute,
             campaign_criterion.device.type,
             campaign_criterion.language.language_constant,
             campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,



             campaign_criterion.user_list.user_list,
             campaign_criterion.age_range.type,
             campaign_criterion.gender.type
      FROM campaign_criterion
      ORDER BY campaign.id, campaign_criterion.type
    """
    crits = []
    for row in r.rows("campaign_criterion", q):
        cc = row.campaign_criterion
        t = enum_name(cc.type_)
        item = {
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "criterion_id": str(cc.criterion_id), "type": t,
            "negative": bool(cc.negative), "status": enum_name(cc.status),
            "bid_modifier": cc.bid_modifier if cc.bid_modifier else None,
            "display_name": cc.display_name or "",
        }
        if t == "LOCATION":
            item["geo_target_constant"] = cc.location.geo_target_constant
        elif t == "PROXIMITY":
            item["proximity"] = {
                "radius": cc.proximity.radius,
                "units": enum_name(cc.proximity.radius_units),
                "lat": (cc.proximity.geo_point.latitude_in_micro_degrees / 1e6
                        if cc.proximity.geo_point.latitude_in_micro_degrees else None),
                "lon": (cc.proximity.geo_point.longitude_in_micro_degrees / 1e6
                        if cc.proximity.geo_point.longitude_in_micro_degrees else None),
                "city": cc.proximity.address.city_name or "",
                "postal_code": cc.proximity.address.postal_code or "",
                "province": cc.proximity.address.province_name or "",
            }
        elif t == "AD_SCHEDULE":
            item["ad_schedule"] = {
                "day": enum_name(cc.ad_schedule.day_of_week),
                "start_hour": int(cc.ad_schedule.start_hour),
                "start_minute": enum_name(cc.ad_schedule.start_minute),
                "end_hour": int(cc.ad_schedule.end_hour),
                "end_minute": enum_name(cc.ad_schedule.end_minute),
            }
        elif t == "DEVICE":
            item["device"] = enum_name(cc.device.type_)
        elif t == "LANGUAGE":
            item["language"] = cc.language.language_constant
        elif t == "KEYWORD":
            item["keyword"] = {"text": cc.keyword.text,
                               "match_type": enum_name(cc.keyword.match_type)}
        elif t == "LOCATION_GROUP":
            item["location_group"] = {"note": "fields not selectable in v25"}
        elif t == "USER_LIST":
            item["user_list"] = cc.user_list.user_list
        crits.append(item)
    out["campaign_criteria"] = crits

    # ---------------- SHARED SETS ----------------
    q = """
      SELECT campaign.id, campaign.name, shared_set.id, shared_set.name,
             shared_set.type, shared_set.status, shared_set.member_count,
             campaign_shared_set.status
      FROM campaign_shared_set
    """
    out["campaign_shared_sets"] = [
        {"campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
         "shared_set_id": str(x.shared_set.id), "shared_set_name": x.shared_set.name,
         "type": enum_name(x.shared_set.type_), "status": enum_name(x.shared_set.status),
         "member_count": int(x.shared_set.member_count),
         "link_status": enum_name(x.campaign_shared_set.status)}
        for x in r.rows("campaign_shared_set", q)
    ]

    q = ("SELECT shared_set.id, shared_set.name, shared_set.type, "
         "shared_set.status, shared_set.member_count FROM shared_set")
    out["shared_sets_all"] = [
        {"id": str(x.shared_set.id), "name": x.shared_set.name,
         "type": enum_name(x.shared_set.type_), "status": enum_name(x.shared_set.status),
         "member_count": int(x.shared_set.member_count)}
        for x in r.rows("shared_set", q)
    ]

    q = """
      SELECT shared_set.id, shared_set.name, shared_criterion.criterion_id,
             shared_criterion.type, shared_criterion.keyword.text,
             shared_criterion.keyword.match_type
      FROM shared_criterion
    """
    out["shared_criteria"] = [
        {"shared_set_id": str(x.shared_set.id), "shared_set_name": x.shared_set.name,
         "criterion_id": str(x.shared_criterion.criterion_id),
         "type": enum_name(x.shared_criterion.type_),
         "text": x.shared_criterion.keyword.text,
         "match_type": enum_name(x.shared_criterion.keyword.match_type)}
        for x in r.rows("shared_criterion", q)
    ]

    # ---------------- AD GROUPS ----------------
    q = """
      SELECT campaign.id, campaign.name,
             ad_group.id, ad_group.name, ad_group.status, ad_group.type,
             ad_group.primary_status, ad_group.primary_status_reasons,
             ad_group.cpc_bid_micros, ad_group.target_cpa_micros,
             ad_group.effective_target_cpa_micros,
             ad_group.targeting_setting.target_restrictions,
             ad_group.tracking_url_template, ad_group.final_url_suffix,
             ad_group.ad_rotation_mode
      FROM ad_group
      ORDER BY campaign.id, ad_group.id
    """
    ags = []
    for row in r.rows("ad_group", q):
        a = row.ad_group
        ags.append({
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "id": str(a.id), "name": a.name, "status": enum_name(a.status),
            "type": enum_name(a.type_), "primary_status": enum_name(a.primary_status),
            "primary_status_reasons": [enum_name(x) for x in a.primary_status_reasons],
            "cpc_bid": micros(a.cpc_bid_micros),
            "target_cpa": micros(a.target_cpa_micros),
            "effective_target_cpa": micros(a.effective_target_cpa_micros),
            "ad_rotation_mode": enum_name(a.ad_rotation_mode),
            "tracking_url_template": a.tracking_url_template or "",
            "final_url_suffix": a.final_url_suffix or "",
            "targeting_setting_restrictions": [
                {"dimension": enum_name(t.targeting_dimension), "bid_only": bool(t.bid_only)}
                for t in a.targeting_setting.target_restrictions],
        })
    out["ad_groups"] = ags

    # ---------------- KEYWORDS ----------------
    q = """
      SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
             ad_group_criterion.criterion_id, ad_group_criterion.status,
             ad_group_criterion.negative,
             ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
             ad_group_criterion.quality_info.quality_score,
             ad_group_criterion.quality_info.creative_quality_score,
             ad_group_criterion.quality_info.post_click_quality_score,
             ad_group_criterion.quality_info.search_predicted_ctr,
             ad_group_criterion.approval_status,
             ad_group_criterion.system_serving_status,
             ad_group_criterion.primary_status,
             ad_group_criterion.primary_status_reasons,
             ad_group_criterion.cpc_bid_micros,
             ad_group_criterion.effective_cpc_bid_micros,
             ad_group_criterion.final_urls,
             ad_group_criterion.position_estimates.first_page_cpc_micros,
             ad_group_criterion.position_estimates.top_of_page_cpc_micros,
             ad_group_criterion.position_estimates.first_position_cpc_micros,
             ad_group_criterion.disapproval_reasons,
             ad_group_criterion.type
      FROM ad_group_criterion
      WHERE ad_group_criterion.type = KEYWORD
      ORDER BY campaign.id, ad_group.id, ad_group_criterion.criterion_id
    """
    kws = []
    for row in r.rows("keywords", q):
        k = row.ad_group_criterion
        qi = k.quality_info
        pe = k.position_estimates
        kws.append({
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "ad_group_id": str(row.ad_group.id), "ad_group_name": row.ad_group.name,
            "criterion_id": str(k.criterion_id),
            "text": k.keyword.text, "match_type": enum_name(k.keyword.match_type),
            "status": enum_name(k.status), "negative": bool(k.negative),
            "quality_score": int(qi.quality_score) if qi.quality_score else None,
            "ad_relevance": enum_name(qi.creative_quality_score),
            "landing_page_experience": enum_name(qi.post_click_quality_score),
            "expected_ctr": enum_name(qi.search_predicted_ctr),
            "approval_status": enum_name(k.approval_status),
            "system_serving_status": enum_name(k.system_serving_status),
            "primary_status": enum_name(k.primary_status),
            "primary_status_reasons": [enum_name(x) for x in k.primary_status_reasons],
            "cpc_bid": micros(k.cpc_bid_micros),
            "effective_cpc_bid": micros(k.effective_cpc_bid_micros),
            "final_urls": list(k.final_urls),
            "first_page_cpc": micros(pe.first_page_cpc_micros),
            "top_of_page_cpc": micros(pe.top_of_page_cpc_micros),
            "first_position_cpc": micros(pe.first_position_cpc_micros),
            "disapproval_reasons": [str(x) for x in k.disapproval_reasons],
        })
    out["keywords"] = kws

    # ---------------- AD-GROUP NEGATIVES ----------------
    q = """
      SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
             ad_group_criterion.criterion_id,
             ad_group_criterion.keyword.text,
             ad_group_criterion.keyword.match_type,
             ad_group_criterion.status, ad_group_criterion.negative
      FROM ad_group_criterion
      WHERE ad_group_criterion.negative = true
    """
    out["ad_group_negatives"] = [
        {"campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
         "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
         "criterion_id": str(x.ad_group_criterion.criterion_id),
         "text": x.ad_group_criterion.keyword.text,
         "match_type": enum_name(x.ad_group_criterion.keyword.match_type),
         "status": enum_name(x.ad_group_criterion.status)}
        for x in r.rows("ad_group_negatives", q)
    ]

    # ---------------- ADS ----------------
    q = """
      SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
             ad_group_ad.ad.id, ad_group_ad.ad.type,
             ad_group_ad.status, ad_group_ad.ad_strength,
             ad_group_ad.policy_summary.approval_status,
             ad_group_ad.policy_summary.review_status,
             ad_group_ad.policy_summary.policy_topic_entries,
             ad_group_ad.primary_status, ad_group_ad.primary_status_reasons,
             ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
             ad_group_ad.ad.tracking_url_template, ad_group_ad.ad.final_url_suffix,
             ad_group_ad.ad.responsive_search_ad.headlines,
             ad_group_ad.ad.responsive_search_ad.descriptions,
             ad_group_ad.ad.responsive_search_ad.path1,
             ad_group_ad.ad.responsive_search_ad.path2,
             ad_group_ad.ad.display_url
      FROM ad_group_ad
      ORDER BY campaign.id, ad_group.id, ad_group_ad.ad.id
    """
    ads = []
    for row in r.rows("ads", q):
        aga = row.ad_group_ad
        ad = aga.ad
        rsa = ad.responsive_search_ad
        ads.append({
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "ad_group_id": str(row.ad_group.id), "ad_group_name": row.ad_group.name,
            "ad_id": str(ad.id), "ad_type": enum_name(ad.type_),
            "status": enum_name(aga.status),
            "ad_strength": enum_name(aga.ad_strength),
            "approval_status": enum_name(aga.policy_summary.approval_status),
            "review_status": enum_name(aga.policy_summary.review_status),
            "policy_topics": [
                {"topic": e.topic, "type": enum_name(e.type_)}
                for e in aga.policy_summary.policy_topic_entries],
            "primary_status": enum_name(aga.primary_status),
            "primary_status_reasons": [enum_name(x) for x in aga.primary_status_reasons],
            "final_urls": list(ad.final_urls),
            "final_mobile_urls": list(ad.final_mobile_urls),
            "tracking_url_template": ad.tracking_url_template or "",
            "final_url_suffix": ad.final_url_suffix or "",
            "path1": rsa.path1 or "", "path2": rsa.path2 or "",
            "headlines": [{"text": a.text, "pinned": enum_name(a.pinned_field)}
                          for a in rsa.headlines],
            "descriptions": [{"text": a.text, "pinned": enum_name(a.pinned_field)}
                             for a in rsa.descriptions],
        })
    out["ads"] = ads

    # ---------------- ASSETS ----------------
    asset_fields = """
             asset.id, asset.name, asset.type, asset.final_urls,
             asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
             asset.sitelink_asset.description2,
             asset.callout_asset.callout_text,
             asset.structured_snippet_asset.header,
             asset.structured_snippet_asset.values,
             asset.call_asset.phone_number, asset.call_asset.country_code,
             asset.call_asset.call_conversion_action,
             asset.call_asset.call_conversion_reporting_state,
             asset.text_asset.text,
             asset.image_asset.full_size.url
    """

    def asset_dict(x, link_obj):
        return {
            "asset_id": str(x.asset.id), "asset_name": x.asset.name or "",
            "asset_type": enum_name(x.asset.type_),
            "field_type": enum_name(link_obj.field_type),
            "link_status": enum_name(link_obj.status),
            "final_urls": list(x.asset.final_urls),
            "sitelink_text": x.asset.sitelink_asset.link_text or "",
            "sitelink_desc1": x.asset.sitelink_asset.description1 or "",
            "sitelink_desc2": x.asset.sitelink_asset.description2 or "",
            "callout_text": x.asset.callout_asset.callout_text or "",
            "snippet_header": x.asset.structured_snippet_asset.header or "",
            "snippet_values": list(x.asset.structured_snippet_asset.values),
            "call_phone": x.asset.call_asset.phone_number or "",
            "call_country": x.asset.call_asset.country_code or "",
            "call_conversion_action": x.asset.call_asset.call_conversion_action or "",
            "call_conv_reporting": enum_name(
                x.asset.call_asset.call_conversion_reporting_state),
            "text": x.asset.text_asset.text or "",
            "image_url": x.asset.image_asset.full_size.url or "",
        }

    q = ("SELECT campaign.id, campaign.name, campaign_asset.asset, "
         "campaign_asset.field_type, campaign_asset.status, "
         "campaign_asset.primary_status, " + asset_fields + " FROM campaign_asset")
    rowsx = r.rows("campaign_asset", q)
    ca_list = []
    for x in rowsx:
        d = asset_dict(x, x.campaign_asset)
        d["campaign_id"] = str(x.campaign.id)
        d["campaign_name"] = x.campaign.name
        d["primary_status"] = enum_name(x.campaign_asset.primary_status)
        ca_list.append(d)
    out["campaign_assets"] = ca_list

    q = ("SELECT customer_asset.asset, customer_asset.field_type, "
         "customer_asset.status, customer_asset.primary_status, "
         + asset_fields + " FROM customer_asset")
    cu_list = []
    for x in r.rows("customer_asset", q):
        d = asset_dict(x, x.customer_asset)
        d["primary_status"] = enum_name(x.customer_asset.primary_status)
        cu_list.append(d)
    out["customer_assets"] = cu_list

    q = ("SELECT campaign.id, ad_group.id, ad_group.name, ad_group_asset.asset, "
         "ad_group_asset.field_type, ad_group_asset.status, "
         + asset_fields + " FROM ad_group_asset")
    ag_list = []
    for x in r.rows("ad_group_asset", q):
        d = asset_dict(x, x.ad_group_asset)
        d["campaign_id"] = str(x.campaign.id)
        d["ad_group_id"] = str(x.ad_group.id)
        d["ad_group_name"] = x.ad_group.name
        ag_list.append(d)
    out["ad_group_assets"] = ag_list

    q = "SELECT asset_set.id, asset_set.name, asset_set.type, asset_set.status FROM asset_set"
    out["asset_sets"] = [
        {"id": str(x.asset_set.id), "name": x.asset_set.name,
         "type": enum_name(x.asset_set.type_), "status": enum_name(x.asset_set.status)}
        for x in r.rows("asset_set", q)
    ]

    q = ("SELECT campaign.id, campaign.name, campaign_asset_set.asset_set, "
         "campaign_asset_set.status, asset_set.name, asset_set.type "
         "FROM campaign_asset_set")
    out["campaign_asset_sets"] = [
        {"campaign_id": str(x.campaign.id), "asset_set_name": x.asset_set.name,
         "asset_set_type": enum_name(x.asset_set.type_),
         "status": enum_name(x.campaign_asset_set.status)}
        for x in r.rows("campaign_asset_set", q)
    ]

    # ---------------- CONVERSION ACTIONS ----------------
    q = """
      SELECT conversion_action.id, conversion_action.name,
             conversion_action.status, conversion_action.type,
             conversion_action.category, conversion_action.origin,
             conversion_action.primary_for_goal,
             conversion_action.counting_type,
             conversion_action.attribution_model_settings.attribution_model,
             conversion_action.attribution_model_settings.data_driven_model_status,
             conversion_action.click_through_lookback_window_days,
             conversion_action.view_through_lookback_window_days,
             conversion_action.phone_call_duration_seconds,
             conversion_action.value_settings.default_value,
             conversion_action.value_settings.always_use_default_value,
             conversion_action.include_in_conversions_metric,
             conversion_action.owner_customer,
             conversion_action.tag_snippets
      FROM conversion_action
      ORDER BY conversion_action.id
    """
    cas = []
    for row in r.rows("conversion_action", q):
        ca = row.conversion_action
        cas.append({
            "id": str(ca.id), "name": ca.name, "status": enum_name(ca.status),
            "type": enum_name(ca.type_), "category": enum_name(ca.category),
            "origin": enum_name(ca.origin),
            "primary_for_goal": bool(ca.primary_for_goal),
            "counting_type": enum_name(ca.counting_type),
            "attribution_model": enum_name(ca.attribution_model_settings.attribution_model),
            "data_driven_status": enum_name(
                ca.attribution_model_settings.data_driven_model_status),
            "click_lookback_days": int(ca.click_through_lookback_window_days),
            "view_lookback_days": int(ca.view_through_lookback_window_days),
            "phone_call_duration_seconds": int(ca.phone_call_duration_seconds),
            "default_value": ca.value_settings.default_value,
            "always_use_default_value": bool(ca.value_settings.always_use_default_value),
            "include_in_conversions_metric": bool(ca.include_in_conversions_metric),
            "owner_customer": ca.owner_customer or "",
            "tag_snippet_count": len(ca.tag_snippets),
        })
    out["conversion_actions"] = cas

    out["read_errors"] = r.errors
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote %s" % OUT)
    for k, v in out.items():
        if isinstance(v, list):
            print("  %s: %d" % (k, len(v)))
    if r.errors:
        print("READ ERRORS:")
        for e in r.errors:
            print(" -", e["query"], "::", e["error"][:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
