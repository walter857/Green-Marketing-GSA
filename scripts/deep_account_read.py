#!/usr/bin/env python3
"""Exhaustive read-only inventory of one Green Marketing child account.

GAQL SELECT only, routed through the repository read-only guard. Every query is
isolated: one failure is recorded in read_errors and skipped, so a single
unsupported field never becomes a silent gap.

Output policy: row-level data goes to a JSON file on disk. Only counts and
aggregates are printed. Raw search-term strings are never printed.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.audit import ReadOnlyAudit, metrics_dict, scrub_text  # noqa: E402
from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402


def E(v):
    try:
        return enum_name(v)
    except Exception:  # noqa: BLE001
        return str(v)


def micros(v):
    try:
        return int(v) / 1_000_000
    except Exception:  # noqa: BLE001
        return None


def windows(today: date) -> dict[str, tuple[str, str]]:
    y = today - timedelta(days=1)

    def back(n):
        return ((y - timedelta(days=n - 1)).isoformat(), y.isoformat())

    prev30_end = y - timedelta(days=30)
    return {
        "last_7": back(7),
        "last_14": back(14),
        "last_30": back(30),
        "prev_30": ((prev30_end - timedelta(days=29)).isoformat(), prev30_end.isoformat()),
        "last_60": back(60),
        "last_90": back(90),
        "last_180": back(180),
        "last_365": back(365),
        "all_time": ("2023-01-01", y.isoformat()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    profile = load_yaml(args.client)["client"]
    cid = str(profile["google_ads"]["child_customer_id"])
    expected = profile["google_ads"]["exact_child_account_name"]

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    r = ReadOnlyAudit(client, cid)

    today = date.today()
    W = windows(today)
    snap: dict = {
        "customer_id": cid,
        "expected_account_name": expected,
        "generated_on": today.isoformat(),
        "windows": {k: {"start": v[0], "end": v[1]} for k, v in W.items()},
    }

    # ---------- identity re-confirmation inside this process ----------
    rows = r.rows("identity", """
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               customer.time_zone, customer.status, customer.manager,
               customer.test_account, customer.auto_tagging_enabled,
               customer.tracking_url_template, customer.final_url_suffix,
               customer.optimization_score,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
               customer.conversion_tracking_setting.conversion_tracking_status,
               customer.conversion_tracking_setting.accepted_customer_data_terms,
               customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
               customer.conversion_tracking_setting.google_ads_conversion_customer,
               customer.remarketing_setting.google_global_site_tag
        FROM customer LIMIT 1
    """)
    if not rows:
        print("FAIL: customer record unreadable.")
        return 1
    c = rows[0].customer
    if c.descriptive_name != expected:
        print(f"FAIL: observed {c.descriptive_name!r}, expected {expected!r}.")
        return 1
    cts = c.conversion_tracking_setting
    snap["identity"] = {
        "id": str(c.id), "descriptive_name": c.descriptive_name,
        "currency_code": c.currency_code, "time_zone": c.time_zone,
        "status": E(c.status), "manager": bool(c.manager), "test_account": bool(c.test_account),
        "auto_tagging_enabled": bool(c.auto_tagging_enabled),
        "tracking_url_template": c.tracking_url_template or "",
        "final_url_suffix": c.final_url_suffix or "",
        "optimization_score": float(c.optimization_score or 0),
        "conversion_tracking_id": str(cts.conversion_tracking_id or ""),
        "cross_account_conversion_tracking_id": str(cts.cross_account_conversion_tracking_id or ""),
        "conversion_tracking_status": E(cts.conversion_tracking_status),
        "accepted_customer_data_terms": bool(cts.accepted_customer_data_terms),
        "enhanced_conversions_for_leads_enabled": bool(cts.enhanced_conversions_for_leads_enabled),
        "google_ads_conversion_customer": cts.google_ads_conversion_customer or "",
        "global_site_tag_present": bool(c.remarketing_setting.google_global_site_tag),
    }
    print(f"Identity: {c.descriptive_name!r} | {c.id} | {c.currency_code} | {c.time_zone}")

    # ---------- campaigns, full settings ----------
    rows = r.rows("campaign_settings", """
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.primary_status, campaign.primary_status_reasons,
               campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
               campaign.bidding_strategy_type, campaign.bidding_strategy_system_status,
               campaign.bidding_strategy, campaign.campaign_budget,
               campaign.start_date_time, campaign.end_date_time,
               campaign.tracking_url_template, campaign.final_url_suffix,
               campaign.ad_serving_optimization_status, campaign.payment_mode,
               campaign.optimization_score, campaign.experiment_type, campaign.base_campaign,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network,
               campaign.network_settings.target_youtube,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign.geo_target_type_setting.negative_geo_target_type,
               campaign.dynamic_search_ads_setting.domain_name,
               campaign.dynamic_search_ads_setting.use_supplied_urls_only,
               campaign.selective_optimization.conversion_actions,
               campaign.optimization_goal_setting.optimization_goal_types,
               campaign.ai_max_setting.enable_ai_max,
               campaign.keyword_match_type,
               campaign.asset_automation_settings,
               campaign.excluded_parent_asset_field_types,
               campaign.targeting_setting.target_restrictions,
               campaign.maximize_conversions.target_cpa_micros,
               campaign.maximize_conversion_value.target_roas,
               campaign.target_cpa.target_cpa_micros,
               campaign.target_roas.target_roas,
               campaign.target_spend.target_spend_micros,
               campaign.manual_cpc.enhanced_cpc_enabled,
               campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
               campaign_budget.explicitly_shared, campaign_budget.delivery_method,
               campaign_budget.status, campaign_budget.total_amount_micros,
               campaign_budget.has_recommended_budget
        FROM campaign ORDER BY campaign.id
    """)
    camps = []
    for row in rows:
        cp, b = row.campaign, row.campaign_budget
        camps.append({
            "id": str(cp.id), "name": cp.name, "status": E(cp.status),
            "serving_status": E(cp.serving_status), "primary_status": E(cp.primary_status),
            "primary_status_reasons": [E(x) for x in cp.primary_status_reasons],
            "channel": E(cp.advertising_channel_type), "sub_type": E(cp.advertising_channel_sub_type),
            "bidding_strategy_type": E(cp.bidding_strategy_type),
            "bidding_system_status": E(cp.bidding_strategy_system_status),
            "portfolio_strategy": cp.bidding_strategy or "",
            "start": cp.start_date_time, "end": cp.end_date_time,
            "tracking_url_template": cp.tracking_url_template or "",
            "final_url_suffix": cp.final_url_suffix or "",
            "ad_serving_optimization": E(cp.ad_serving_optimization_status),
            "payment_mode": E(cp.payment_mode),
            "optimization_score": float(cp.optimization_score or 0),
            "experiment_type": E(cp.experiment_type), "base_campaign": cp.base_campaign or "",
            "net_google_search": bool(cp.network_settings.target_google_search),
            "net_search_partners": bool(cp.network_settings.target_search_network),
            "net_display": bool(cp.network_settings.target_content_network),
            "net_partner_search": bool(cp.network_settings.target_partner_search_network),
            "net_youtube": bool(cp.network_settings.target_youtube),
            "positive_geo": E(cp.geo_target_type_setting.positive_geo_target_type),
            "negative_geo": E(cp.geo_target_type_setting.negative_geo_target_type),
            "dsa_domain": cp.dynamic_search_ads_setting.domain_name or "",
            "dsa_supplied_urls_only": bool(cp.dynamic_search_ads_setting.use_supplied_urls_only),
            "selective_optimization": list(cp.selective_optimization.conversion_actions),
            "optimization_goal_types": [E(x) for x in cp.optimization_goal_setting.optimization_goal_types],
            "ai_max_enabled": bool(cp.ai_max_setting.enable_ai_max),
            "keyword_match_type_setting": E(cp.keyword_match_type),
            "asset_automation_settings": [
                {"type": E(a.asset_automation_type), "status": E(a.asset_automation_status)}
                for a in cp.asset_automation_settings],
            "excluded_parent_asset_field_types": [E(x) for x in cp.excluded_parent_asset_field_types],
            "target_restrictions": [
                {"dimension": E(t.targeting_dimension), "bid_only": bool(t.bid_only)}
                for t in cp.targeting_setting.target_restrictions],
            "maxconv_target_cpa": micros(cp.maximize_conversions.target_cpa_micros),
            "maxconvvalue_target_roas": float(cp.maximize_conversion_value.target_roas or 0),
            "target_cpa": micros(cp.target_cpa.target_cpa_micros),
            "target_roas": float(cp.target_roas.target_roas or 0),
            "target_spend": micros(cp.target_spend.target_spend_micros),
            "manual_cpc_enhanced": bool(cp.manual_cpc.enhanced_cpc_enabled),
            "budget_id": str(b.id), "budget_name": b.name,
            "budget_amount": micros(b.amount_micros),
            "budget_shared": bool(b.explicitly_shared),
            "budget_delivery": E(b.delivery_method), "budget_status": E(b.status),
            "budget_total_amount": micros(b.total_amount_micros),
            "budget_has_recommended": bool(b.has_recommended_budget),
        })
    snap["campaigns"] = camps
    print(f"campaigns: {len(camps)}")

    # ---------- portfolio bidding strategies ----------
    rows = r.rows("bidding_strategies", """
        SELECT bidding_strategy.id, bidding_strategy.name, bidding_strategy.type,
               bidding_strategy.status, bidding_strategy.campaign_count,
               bidding_strategy.target_cpa.target_cpa_micros,
               bidding_strategy.target_roas.target_roas,
               bidding_strategy.maximize_conversions.target_cpa_micros
        FROM bidding_strategy
    """)
    snap["bidding_strategies"] = [{
        "id": str(x.bidding_strategy.id), "name": x.bidding_strategy.name,
        "type": E(x.bidding_strategy.type_), "status": E(x.bidding_strategy.status),
        "campaign_count": int(x.bidding_strategy.campaign_count or 0),
        "target_cpa": micros(x.bidding_strategy.target_cpa.target_cpa_micros),
        "target_roas": float(x.bidding_strategy.target_roas.target_roas or 0),
    } for x in rows]
    print(f"portfolio bidding strategies: {len(snap['bidding_strategies'])}")

    # ---------- campaign performance per window ----------
    perf_select = """
        campaign.id, campaign.name, campaign.status,
        metrics.impressions, metrics.clicks, metrics.ctr, metrics.average_cpc,
        metrics.cost_micros, metrics.conversions, metrics.all_conversions,
        metrics.conversions_value, metrics.all_conversions_value,
        metrics.conversions_from_interactions_rate, metrics.cost_per_conversion,
        metrics.cost_per_all_conversions, metrics.search_impression_share,
        metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share,
        metrics.search_top_impression_share, metrics.search_absolute_top_impression_share,
        metrics.invalid_clicks, metrics.invalid_click_rate,
        metrics.phone_calls, metrics.phone_impressions, metrics.phone_through_rate
    """
    snap["campaign_performance"] = {}
    for label, (s, e) in W.items():
        rows = r.rows(f"camp_perf_{label}", f"""
            SELECT {perf_select} FROM campaign
            WHERE segments.date BETWEEN '{s}' AND '{e}'
        """)
        snap["campaign_performance"][label] = [{
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "status": E(x.campaign.status), **metrics_dict(x.metrics),
            "search_top_impression_share": getattr(x.metrics, "search_top_impression_share", None),
            "invalid_clicks": int(getattr(x.metrics, "invalid_clicks", 0)),
            "invalid_click_rate": float(getattr(x.metrics, "invalid_click_rate", 0.0)),
            "phone_calls": int(getattr(x.metrics, "phone_calls", 0)),
            "phone_impressions": int(getattr(x.metrics, "phone_impressions", 0)),
        } for x in rows]

    # ---------- conversion action performance per window ----------
    snap["conversion_action_performance"] = {}
    for label in ["all_time", "last_365", "last_90", "last_30", "prev_30"]:
        s, e = W[label]
        rows = r.rows(f"conv_perf_{label}", f"""
            SELECT campaign.id, campaign.name,
                   segments.conversion_action, segments.conversion_action_name,
                   segments.conversion_action_category,
                   metrics.conversions, metrics.all_conversions,
                   metrics.conversions_value, metrics.all_conversions_value
            FROM campaign
            WHERE segments.date BETWEEN '{s}' AND '{e}'
        """)
        agg: dict = {}
        for x in rows:
            key = (str(x.campaign.id), x.segments.conversion_action_name)
            b = agg.setdefault(key, {
                "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
                "conversion_action": x.segments.conversion_action,
                "conversion_action_name": x.segments.conversion_action_name,
                "category": E(x.segments.conversion_action_category),
                "conversions": 0.0, "all_conversions": 0.0, "value": 0.0,
            })
            b["conversions"] += float(x.metrics.conversions)
            b["all_conversions"] += float(x.metrics.all_conversions)
            b["value"] += float(x.metrics.conversions_value)
        snap["conversion_action_performance"][label] = list(agg.values())

    # ---------- conversion actions, full ----------
    rows = r.rows("conversion_actions_full", """
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.type, conversion_action.category, conversion_action.origin,
               conversion_action.primary_for_goal, conversion_action.counting_type,
               conversion_action.include_in_conversions_metric,
               conversion_action.click_through_lookback_window_days,
               conversion_action.view_through_lookback_window_days,
               conversion_action.phone_call_duration_seconds,
               conversion_action.attribution_model_settings.attribution_model,
               conversion_action.attribution_model_settings.data_driven_model_status,
               conversion_action.value_settings.default_value,
               conversion_action.value_settings.always_use_default_value,
               conversion_action.tag_snippets,
               conversion_action.app_id, conversion_action.owner_customer
        FROM conversion_action
    """)
    snap["conversion_actions"] = [{
        "id": str(x.conversion_action.id), "name": x.conversion_action.name,
        "status": E(x.conversion_action.status), "type": E(x.conversion_action.type_),
        "category": E(x.conversion_action.category), "origin": E(x.conversion_action.origin),
        "primary_for_goal": bool(x.conversion_action.primary_for_goal),
        "counting_type": E(x.conversion_action.counting_type),
        "include_in_conversions_metric": bool(x.conversion_action.include_in_conversions_metric),
        "click_lookback_days": int(x.conversion_action.click_through_lookback_window_days or 0),
        "view_lookback_days": int(x.conversion_action.view_through_lookback_window_days or 0),
        "phone_call_duration_seconds": int(x.conversion_action.phone_call_duration_seconds or 0),
        "attribution_model": E(x.conversion_action.attribution_model_settings.attribution_model),
        "data_driven_status": E(x.conversion_action.attribution_model_settings.data_driven_model_status),
        "default_value": float(x.conversion_action.value_settings.default_value or 0),
        "always_use_default_value": bool(x.conversion_action.value_settings.always_use_default_value),
        "owner_customer": x.conversion_action.owner_customer or "",
        "tag_snippet_count": len(x.conversion_action.tag_snippets),
    } for x in rows]

    # ---------- customer + campaign conversion goals ----------
    rows = r.rows("customer_conversion_goals", """
        SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
               customer_conversion_goal.biddable
        FROM customer_conversion_goal
    """)
    snap["customer_conversion_goals"] = [{
        "category": E(x.customer_conversion_goal.category),
        "origin": E(x.customer_conversion_goal.origin),
        "biddable": bool(x.customer_conversion_goal.biddable),
    } for x in rows]

    rows = r.rows("campaign_conversion_goals", """
        SELECT campaign.id, campaign.name, campaign_conversion_goal.category,
               campaign_conversion_goal.origin, campaign_conversion_goal.biddable
        FROM campaign_conversion_goal
    """)
    snap["campaign_conversion_goals"] = [{
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "category": E(x.campaign_conversion_goal.category),
        "origin": E(x.campaign_conversion_goal.origin),
        "biddable": bool(x.campaign_conversion_goal.biddable),
    } for x in rows]
    print(f"conversion actions: {len(snap['conversion_actions'])} | "
          f"customer goals: {len(snap['customer_conversion_goals'])} | "
          f"campaign goals: {len(snap['campaign_conversion_goals'])}")

    # ---------- ad groups ----------
    rows = r.rows("ad_groups_full", """
        SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
               ad_group.cpc_bid_micros, ad_group.cpm_bid_micros,
               ad_group.target_cpa_micros, ad_group.target_roas,
               ad_group.ad_rotation_mode, ad_group.tracking_url_template,
               ad_group.final_url_suffix, ad_group.percent_cpc_bid_micros,
               ad_group.effective_target_cpa_micros, ad_group.effective_target_roas,
               ad_group.targeting_setting.target_restrictions,
               ad_group.primary_status, ad_group.primary_status_reasons,
               campaign.id, campaign.name, campaign.status
        FROM ad_group ORDER BY ad_group.id
    """)
    snap["ad_groups"] = [{
        "id": str(x.ad_group.id), "name": x.ad_group.name, "status": E(x.ad_group.status),
        "type": E(x.ad_group.type_), "cpc_bid": micros(x.ad_group.cpc_bid_micros),
        "target_cpa": micros(x.ad_group.target_cpa_micros),
        "target_roas": float(x.ad_group.target_roas or 0),
        "effective_target_cpa": micros(x.ad_group.effective_target_cpa_micros),
        "ad_rotation": E(x.ad_group.ad_rotation_mode),
        "tracking_url_template": x.ad_group.tracking_url_template or "",
        "final_url_suffix": x.ad_group.final_url_suffix or "",
        "primary_status": E(x.ad_group.primary_status),
        "primary_status_reasons": [E(v) for v in x.ad_group.primary_status_reasons],
        "target_restrictions": [{"dimension": E(t.targeting_dimension), "bid_only": bool(t.bid_only)}
                                for t in x.ad_group.targeting_setting.target_restrictions],
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "campaign_status": E(x.campaign.status),
    } for x in rows]
    print(f"ad groups: {len(snap['ad_groups'])}")

    # ---------- ad group performance ----------
    snap["ad_group_performance"] = {}
    for label in ["all_time", "last_365", "last_90", "last_30"]:
        s, e = W[label]
        rows = r.rows(f"ag_perf_{label}", f"""
            SELECT ad_group.id, ad_group.name, campaign.id, campaign.name,
                   metrics.impressions, metrics.clicks, metrics.cost_micros,
                   metrics.conversions, metrics.all_conversions, metrics.conversions_value,
                   metrics.ctr, metrics.average_cpc, metrics.cost_per_conversion,
                   metrics.conversions_from_interactions_rate,
                   metrics.search_impression_share,
                   metrics.search_rank_lost_impression_share
            FROM ad_group WHERE segments.date BETWEEN '{s}' AND '{e}'
        """)
        snap["ad_group_performance"][label] = [{
            "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            **metrics_dict(x.metrics),
        } for x in rows]

    # ---------- keywords, full ----------
    rows = r.rows("keywords_full", """
        SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.negative, ad_group_criterion.system_serving_status,
               ad_group_criterion.approval_status, ad_group_criterion.cpc_bid_micros,
               ad_group_criterion.effective_cpc_bid_micros,
               ad_group_criterion.final_urls, ad_group_criterion.final_mobile_urls,
               ad_group_criterion.tracking_url_template,
               ad_group_criterion.quality_info.quality_score,
               ad_group_criterion.quality_info.creative_quality_score,
               ad_group_criterion.quality_info.post_click_quality_score,
               ad_group_criterion.quality_info.search_predicted_ctr,
               ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
               ad_group.id, ad_group.name, ad_group.status,
               campaign.id, campaign.name, campaign.status
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD
    """)
    kws = []
    for x in rows:
        k = x.ad_group_criterion
        kws.append({
            "criterion_id": str(k.criterion_id), "text": k.keyword.text,
            "match_type": E(k.keyword.match_type), "status": E(k.status),
            "negative": bool(k.negative), "system_serving_status": E(k.system_serving_status),
            "approval_status": E(k.approval_status),
            "cpc_bid": micros(k.cpc_bid_micros), "effective_cpc_bid": micros(k.effective_cpc_bid_micros),
            "final_urls": list(k.final_urls), "tracking_url_template": k.tracking_url_template or "",
            "quality_score": int(k.quality_info.quality_score or 0),
            "ad_relevance": E(k.quality_info.creative_quality_score),
            "landing_page_exp": E(k.quality_info.post_click_quality_score),
            "expected_ctr": E(k.quality_info.search_predicted_ctr),
            "primary_status": E(k.primary_status),
            "primary_status_reasons": [E(v) for v in k.primary_status_reasons],
            "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
            "ad_group_status": E(x.ad_group.status),
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "campaign_status": E(x.campaign.status),
        })
    snap["keywords"] = kws
    pos = [k for k in kws if not k["negative"]]
    neg = [k for k in kws if k["negative"]]
    print(f"keywords: {len(kws)} (positive {len(pos)} / ad-group negatives {len(neg)})")

    # ---------- keyword performance ----------
    snap["keyword_performance"] = {}
    for label in ["all_time", "last_365", "last_90", "last_30"]:
        s, e = W[label]
        rows = r.rows(f"kw_perf_{label}", f"""
            SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                   ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                   ad_group.id, ad_group.name, campaign.id, campaign.name,
                   metrics.impressions, metrics.clicks, metrics.cost_micros,
                   metrics.conversions, metrics.all_conversions, metrics.conversions_value,
                   metrics.ctr, metrics.average_cpc, metrics.cost_per_conversion,
                   metrics.search_impression_share
            FROM keyword_view WHERE segments.date BETWEEN '{s}' AND '{e}'
        """)
        snap["keyword_performance"][label] = [{
            "criterion_id": str(x.ad_group_criterion.criterion_id),
            "text": x.ad_group_criterion.keyword.text,
            "match_type": E(x.ad_group_criterion.keyword.match_type),
            "status": E(x.ad_group_criterion.status),
            "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            **metrics_dict(x.metrics),
        } for x in rows]

    # ---------- campaign criteria ----------
    rows = r.rows("campaign_criteria", """
        SELECT campaign.id, campaign.name, campaign.status,
               campaign_criterion.criterion_id, campaign_criterion.type,
               campaign_criterion.negative, campaign_criterion.status,
               campaign_criterion.bid_modifier,
               campaign_criterion.location.geo_target_constant,
               campaign_criterion.language.language_constant,
               campaign_criterion.device.type,
               campaign_criterion.ad_schedule.day_of_week,
               campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour,
               campaign_criterion.ad_schedule.start_minute, campaign_criterion.ad_schedule.end_minute,
               campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
               campaign_criterion.proximity.radius, campaign_criterion.proximity.radius_units,
               campaign_criterion.proximity.geo_point.latitude_in_micro_degrees,
               campaign_criterion.proximity.geo_point.longitude_in_micro_degrees,
               campaign_criterion.age_range.type, campaign_criterion.gender.type,
               campaign_criterion.income_range.type,
               campaign_criterion.user_list.user_list,
               campaign_criterion.brand_list.shared_set,
               campaign_criterion.webpage.criterion_name
        FROM campaign_criterion
    """)
    crits = []
    for x in rows:
        k = x.campaign_criterion
        t = E(k.type_)
        crits.append({
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "campaign_status": E(x.campaign.status),
            "criterion_id": str(k.criterion_id), "type": t,
            "negative": bool(k.negative), "status": E(k.status),
            "bid_modifier": float(k.bid_modifier or 0),
            "geo_target_constant": k.location.geo_target_constant or "",
            "language_constant": k.language.language_constant or "",
            "device": E(k.device.type_) if t == "DEVICE" else "",
            "ad_schedule_day": E(k.ad_schedule.day_of_week) if t == "AD_SCHEDULE" else "",
            "ad_schedule_start_hour": int(k.ad_schedule.start_hour or 0),
            "ad_schedule_end_hour": int(k.ad_schedule.end_hour or 0),
            "ad_schedule_start_minute": E(k.ad_schedule.start_minute) if t == "AD_SCHEDULE" else "",
            "ad_schedule_end_minute": E(k.ad_schedule.end_minute) if t == "AD_SCHEDULE" else "",
            "keyword_text": scrub_text(k.keyword.text) if t == "KEYWORD" else "",
            "keyword_match_type": E(k.keyword.match_type) if t == "KEYWORD" else "",
            "proximity_radius": float(k.proximity.radius or 0),
            "proximity_units": E(k.proximity.radius_units) if t == "PROXIMITY" else "",
            "proximity_lat_micro": int(k.proximity.geo_point.latitude_in_micro_degrees or 0),
            "proximity_lon_micro": int(k.proximity.geo_point.longitude_in_micro_degrees or 0),
            "age_range": E(k.age_range.type_) if t == "AGE_RANGE" else "",
            "gender": E(k.gender.type_) if t == "GENDER" else "",
            "income_range": E(k.income_range.type_) if t == "INCOME_RANGE" else "",
            "user_list": k.user_list.user_list or "",
            "brand_list_shared_set": k.brand_list.shared_set or "",
        })
    snap["campaign_criteria"] = crits
    by_type: dict[str, int] = {}
    for c2 in crits:
        by_type[c2["type"]] = by_type.get(c2["type"], 0) + 1
    print(f"campaign criteria: {len(crits)} {by_type}")

    # ---------- ad group criteria, non-keyword ----------
    rows = r.rows("ad_group_criteria_other", """
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.type,
               ad_group_criterion.negative, ad_group_criterion.status,
               ad_group_criterion.bid_modifier,
               ad_group_criterion.age_range.type, ad_group_criterion.gender.type,
               ad_group_criterion.user_list.user_list, ad_group_criterion.audience.audience,
               ad_group_criterion.webpage.criterion_name
        FROM ad_group_criterion
        WHERE ad_group_criterion.type != KEYWORD
    """)
    snap["ad_group_criteria_other"] = [{
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
        "criterion_id": str(x.ad_group_criterion.criterion_id),
        "type": E(x.ad_group_criterion.type_),
        "negative": bool(x.ad_group_criterion.negative),
        "status": E(x.ad_group_criterion.status),
        "bid_modifier": float(x.ad_group_criterion.bid_modifier or 0),
        "age_range": E(x.ad_group_criterion.age_range.type_),
        "gender": E(x.ad_group_criterion.gender.type_),
        "user_list": x.ad_group_criterion.user_list.user_list or "",
        "audience": x.ad_group_criterion.audience.audience or "",
    } for x in rows]
    print(f"non-keyword ad group criteria: {len(snap['ad_group_criteria_other'])}")

    # ---------- shared sets / negative keyword lists ----------
    rows = r.rows("shared_sets", """
        SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
               shared_set.member_count, shared_set.reference_count
        FROM shared_set
    """)
    snap["shared_sets"] = [{
        "id": str(x.shared_set.id), "name": x.shared_set.name,
        "type": E(x.shared_set.type_), "status": E(x.shared_set.status),
        "member_count": int(x.shared_set.member_count or 0),
        "reference_count": int(x.shared_set.reference_count or 0),
    } for x in rows]

    rows = r.rows("campaign_shared_sets", """
        SELECT campaign.id, campaign.name, campaign.status,
               shared_set.id, shared_set.name, shared_set.type,
               campaign_shared_set.status
        FROM campaign_shared_set
    """)
    snap["campaign_shared_sets"] = [{
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "campaign_status": E(x.campaign.status),
        "shared_set_id": str(x.shared_set.id), "shared_set_name": x.shared_set.name,
        "shared_set_type": E(x.shared_set.type_),
        "link_status": E(x.campaign_shared_set.status),
    } for x in rows]

    rows = r.rows("shared_criteria", """
        SELECT shared_set.id, shared_set.name, shared_set.type,
               shared_criterion.criterion_id, shared_criterion.type,
               shared_criterion.keyword.text, shared_criterion.keyword.match_type
        FROM shared_criterion
    """)
    snap["shared_criteria"] = [{
        "shared_set_id": str(x.shared_set.id), "shared_set_name": x.shared_set.name,
        "shared_set_type": E(x.shared_set.type_),
        "criterion_id": str(x.shared_criterion.criterion_id),
        "type": E(x.shared_criterion.type_),
        "keyword_text": scrub_text(x.shared_criterion.keyword.text),
        "match_type": E(x.shared_criterion.keyword.match_type),
    } for x in rows]
    print(f"shared sets: {len(snap['shared_sets'])} | links: {len(snap['campaign_shared_sets'])} "
          f"| members: {len(snap['shared_criteria'])}")

    # ---------- account-level negative criteria ----------
    rows = r.rows("customer_negative_criteria", """
        SELECT customer_negative_criterion.id, customer_negative_criterion.type,
               customer_negative_criterion.placement.url
        FROM customer_negative_criterion
    """)
    snap["customer_negative_criteria"] = [{
        "id": str(x.customer_negative_criterion.id),
        "type": E(x.customer_negative_criterion.type_),
        "placement_url": x.customer_negative_criterion.placement.url or "",
    } for x in rows]

    # ---------- ads, full ----------
    rows = r.rows("ads_full", """
        SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
               ad_group_ad.ad_strength, ad_group_ad.policy_summary.approval_status,
               ad_group_ad.policy_summary.review_status,
               ad_group_ad.policy_summary.policy_topic_entries,
               ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
               ad_group_ad.ad.tracking_url_template, ad_group_ad.ad.final_url_suffix,
               ad_group_ad.ad.display_url, ad_group_ad.ad.name,
               ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions,
               ad_group_ad.ad.responsive_search_ad.path1,
               ad_group_ad.ad.responsive_search_ad.path2,
               ad_group_ad.ad.expanded_text_ad.headline_part1,
               ad_group_ad.ad.expanded_text_ad.description,
               ad_group.id, ad_group.name, ad_group.status,
               campaign.id, campaign.name, campaign.status
        FROM ad_group_ad
    """)
    ads = []
    for x in rows:
        a = x.ad_group_ad.ad
        rsa = a.responsive_search_ad
        ads.append({
            "ad_id": str(a.id), "type": E(a.type_), "status": E(x.ad_group_ad.status),
            "ad_strength": E(x.ad_group_ad.ad_strength),
            "approval_status": E(x.ad_group_ad.policy_summary.approval_status),
            "review_status": E(x.ad_group_ad.policy_summary.review_status),
            "policy_topics": [t.topic for t in x.ad_group_ad.policy_summary.policy_topic_entries],
            "final_urls": list(a.final_urls), "final_mobile_urls": list(a.final_mobile_urls),
            "tracking_url_template": a.tracking_url_template or "",
            "final_url_suffix": a.final_url_suffix or "",
            "headlines": [{"text": h.text, "pinned": E(h.pinned_field) if h.pinned_field else ""}
                          for h in rsa.headlines],
            "descriptions": [{"text": d.text, "pinned": E(d.pinned_field) if d.pinned_field else ""}
                             for d in rsa.descriptions],
            "path1": rsa.path1, "path2": rsa.path2,
            "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
            "ad_group_status": E(x.ad_group.status),
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "campaign_status": E(x.campaign.status),
        })
    snap["ads"] = ads
    print(f"ads: {len(ads)}")

    # ---------- ad performance ----------
    snap["ad_performance"] = {}
    for label in ["all_time", "last_365", "last_90"]:
        s, e = W[label]
        rows = r.rows(f"ad_perf_{label}", f"""
            SELECT ad_group_ad.ad.id, ad_group.id, ad_group.name, campaign.id, campaign.name,
                   metrics.impressions, metrics.clicks, metrics.cost_micros,
                   metrics.conversions, metrics.all_conversions, metrics.ctr,
                   metrics.conversions_from_interactions_rate
            FROM ad_group_ad WHERE segments.date BETWEEN '{s}' AND '{e}'
        """)
        snap["ad_performance"][label] = [{
            "ad_id": str(x.ad_group_ad.ad.id), "ad_group_id": str(x.ad_group.id),
            "ad_group_name": x.ad_group.name, "campaign_id": str(x.campaign.id),
            "campaign_name": x.campaign.name, **metrics_dict(x.metrics),
        } for x in rows]

    # ---------- assets and associations ----------
    rows = r.rows("assets_full", """
        SELECT asset.id, asset.name, asset.type, asset.final_urls, asset.final_mobile_urls,
               asset.tracking_url_template, asset.source,
               asset.policy_summary.approval_status,
               asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
               asset.sitelink_asset.description2,
               asset.callout_asset.callout_text,
               asset.structured_snippet_asset.header, asset.structured_snippet_asset.values,
               asset.call_asset.phone_number, asset.call_asset.country_code,
               asset.call_asset.call_conversion_action,
               asset.call_asset.call_conversion_reporting_state,
               asset.text_asset.text,
               asset.image_asset.full_size.url,
               asset.lead_form_asset.business_name
        FROM asset
    """)
    snap["assets"] = [{
        "id": str(x.asset.id), "name": x.asset.name, "type": E(x.asset.type_),
        "source": E(x.asset.source), "final_urls": list(x.asset.final_urls),
        "tracking_url_template": x.asset.tracking_url_template or "",
        "approval_status": E(x.asset.policy_summary.approval_status),
        "sitelink_text": x.asset.sitelink_asset.link_text or "",
        "sitelink_desc1": x.asset.sitelink_asset.description1 or "",
        "sitelink_desc2": x.asset.sitelink_asset.description2 or "",
        "callout_text": x.asset.callout_asset.callout_text or "",
        "snippet_header": x.asset.structured_snippet_asset.header or "",
        "snippet_values": list(x.asset.structured_snippet_asset.values),
        "call_phone_number": x.asset.call_asset.phone_number or "",
        "call_country": x.asset.call_asset.country_code or "",
        "call_conversion_action": x.asset.call_asset.call_conversion_action or "",
        "call_conversion_reporting_state": E(x.asset.call_asset.call_conversion_reporting_state),
        "text": x.asset.text_asset.text or "",
        "image_url_present": bool(x.asset.image_asset.full_size.url),
        "lead_form_business": x.asset.lead_form_asset.business_name or "",
    } for x in rows]

    for label, res, extra in [
        ("campaign_assets", "campaign_asset",
         "campaign.id, campaign.name, campaign.status, campaign_asset.status, "
         "campaign_asset.field_type, campaign_asset.source, campaign_asset.primary_status"),
        ("ad_group_assets", "ad_group_asset",
         "campaign.id, campaign.name, ad_group.id, ad_group.name, ad_group_asset.status, "
         "ad_group_asset.field_type, ad_group_asset.source"),
        ("customer_assets", "customer_asset",
         "customer_asset.status, customer_asset.field_type, customer_asset.source"),
    ]:
        rows = r.rows(label, f"""
            SELECT asset.id, asset.type, asset.name, {extra} FROM {res}
        """)
        out = []
        for x in rows:
            link = getattr(x, res)
            out.append({
                "asset_id": str(x.asset.id), "asset_type": E(x.asset.type_),
                "field_type": E(link.field_type), "status": E(link.status),
                "source": E(getattr(link, "source", "")),
                "campaign_id": str(getattr(x.campaign, "id", "") or ""),
                "campaign_name": getattr(x.campaign, "name", "") or "",
                "ad_group_id": str(getattr(x.ad_group, "id", "") or ""),
                "ad_group_name": getattr(x.ad_group, "name", "") or "",
            })
        snap[label] = out
    print(f"assets: {len(snap['assets'])} | campaign links: {len(snap.get('campaign_assets', []))} "
          f"| ad group links: {len(snap.get('ad_group_assets', []))} "
          f"| account links: {len(snap.get('customer_assets', []))}")

    # ---------- geographic performance ----------
    snap["geo_performance"] = {}
    for label in ["all_time", "last_365", "last_90"]:
        s, e = W[label]
        for view, key in [("geographic_view", "matched"), ("user_location_view", "user")]:
            loc_field = ("geographic_view.country_criterion_id, geographic_view.location_type"
                         if view == "geographic_view"
                         else "user_location_view.country_criterion_id, "
                              "user_location_view.targeting_location")
            rows = r.rows(f"geo_{key}_{label}", f"""
                SELECT campaign.id, campaign.name, {loc_field},
                       segments.geo_target_city, segments.geo_target_postal_code,
                       segments.geo_target_metro, segments.geo_target_region,
                       metrics.impressions, metrics.clicks, metrics.cost_micros,
                       metrics.conversions, metrics.all_conversions
                FROM {view} WHERE segments.date BETWEEN '{s}' AND '{e}'
            """)
            snap["geo_performance"][f"{key}_{label}"] = [{
                "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
                "geo_target_city": x.segments.geo_target_city or "",
                "geo_target_postal_code": x.segments.geo_target_postal_code or "",
                "geo_target_metro": x.segments.geo_target_metro or "",
                "geo_target_region": x.segments.geo_target_region or "",
                "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
                "cost": micros(x.metrics.cost_micros),
                "conversions": float(x.metrics.conversions),
                "all_conversions": float(x.metrics.all_conversions),
            } for x in rows]

    # ---------- segments ----------
    snap["segment_performance"] = {}
    seg_defs = [
        ("device", "segments.device"),
        ("day_of_week", "segments.day_of_week"),
        ("hour", "segments.hour"),
        ("network", "segments.ad_network_type"),
        ("click_type", "segments.click_type"),
    ]
    for label in ["all_time", "last_365", "last_90"]:
        s, e = W[label]
        for seg_label, seg_field in seg_defs:
            rows = r.rows(f"seg_{seg_label}_{label}", f"""
                SELECT campaign.id, campaign.name, {seg_field},
                       metrics.impressions, metrics.clicks, metrics.cost_micros,
                       metrics.conversions, metrics.all_conversions
                FROM campaign WHERE segments.date BETWEEN '{s}' AND '{e}'
            """)
            attr = seg_field.split(".")[-1]
            out = []
            for x in rows:
                out.append({
                    "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
                    "segment": E(getattr(x.segments, attr)),
                    "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
                    "cost": micros(x.metrics.cost_micros),
                    "conversions": float(x.metrics.conversions),
                    "all_conversions": float(x.metrics.all_conversions),
                })
            snap["segment_performance"][f"{seg_label}_{label}"] = out

    # ---------- landing pages ----------
    snap["landing_pages"] = {}
    for label in ["all_time", "last_365", "last_90"]:
        s, e = W[label]
        rows = r.rows(f"landing_pages_{label}", f"""
            SELECT landing_page_view.unexpanded_final_url, campaign.id, campaign.name,
                   metrics.impressions, metrics.clicks, metrics.cost_micros,
                   metrics.conversions, metrics.all_conversions,
                   metrics.conversions_from_interactions_rate
            FROM landing_page_view WHERE segments.date BETWEEN '{s}' AND '{e}'
        """)
        snap["landing_pages"][label] = [{
            "url": x.landing_page_view.unexpanded_final_url,
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
            "cost": micros(x.metrics.cost_micros),
            "conversions": float(x.metrics.conversions),
            "all_conversions": float(x.metrics.all_conversions),
        } for x in rows]

    # ---------- search terms, full detail per window ----------
    snap["search_terms"] = {}
    for label in ["all_time", "last_365", "last_90", "last_30"]:
        s, e = W[label]
        rows = r.rows(f"search_terms_{label}", f"""
            SELECT search_term_view.search_term, search_term_view.status,
                   campaign.id, campaign.name, campaign.status,
                   ad_group.id, ad_group.name,
                   segments.keyword.info.text, segments.keyword.info.match_type,
                   segments.search_term_match_type,
                   metrics.impressions, metrics.clicks, metrics.cost_micros,
                   metrics.conversions, metrics.all_conversions, metrics.conversions_value
            FROM search_term_view WHERE segments.date BETWEEN '{s}' AND '{e}'
        """)
        snap["search_terms"][label] = [{
            "term": scrub_text(x.search_term_view.search_term),
            "added_excluded": E(x.search_term_view.status),
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "campaign_status": E(x.campaign.status),
            "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
            "matched_keyword": x.segments.keyword.info.text,
            "matched_keyword_match_type": E(x.segments.keyword.info.match_type),
            "search_term_match_type": E(x.segments.search_term_match_type),
            "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
            "cost": micros(x.metrics.cost_micros),
            "conversions": float(x.metrics.conversions),
            "all_conversions": float(x.metrics.all_conversions),
            "conversions_value": float(x.metrics.conversions_value),
        } for x in rows]
        print(f"search terms [{label}]: {len(snap['search_terms'][label])} rows")

    # ---------- change history ----------
    # change_event is capped by the API at 30 days back (START_DATE_TOO_OLD beyond that).
    # change_status carries a longer resource-level view and is read separately.
    change_rows = []
    ce_start = today - timedelta(days=29)
    rows = r.rows("change_event_30d", f"""
        SELECT change_event.change_date_time, change_event.change_resource_type,
               change_event.resource_change_operation, change_event.changed_fields,
               change_event.client_type, change_event.user_email,
               change_event.campaign, change_event.ad_group,
               change_event.change_resource_name
        FROM change_event
        WHERE change_event.change_date_time >= '{ce_start.isoformat()} 00:00:00'
          AND change_event.change_date_time <= '{today.isoformat()} 23:59:59'
        ORDER BY change_event.change_date_time DESC
        LIMIT 10000
    """)
    for x in rows:
        ce = x.change_event
        change_rows.append({
            "when": ce.change_date_time,
            "resource_type": E(ce.change_resource_type),
            "operation": E(ce.resource_change_operation),
            "changed_fields": list(ce.changed_fields.paths) if ce.changed_fields else [],
            "client_type": E(ce.client_type),
            "user_email": "[REDACTED]" if ce.user_email else "",
            "campaign": ce.campaign or "", "ad_group": ce.ad_group or "",
            "resource": ce.change_resource_name or "",
        })
    snap["change_events"] = change_rows
    snap["change_event_limitation"] = (
        "Google Ads caps change_event at 30 days back (START_DATE_TOO_OLD). "
        f"Window read: {ce_start.isoformat()}..{today.isoformat()}."
    )

    rows = r.rows("change_status_90d", """
        SELECT change_status.last_change_date_time, change_status.resource_type,
               change_status.resource_status, change_status.campaign,
               change_status.ad_group, change_status.ad_group_criterion,
               change_status.ad_group_ad, change_status.campaign_criterion
        FROM change_status
        WHERE change_status.last_change_date_time DURING LAST_30_DAYS
        ORDER BY change_status.last_change_date_time DESC
        LIMIT 10000
    """)
    snap["change_status"] = [{
        "when": x.change_status.last_change_date_time,
        "resource_type": E(x.change_status.resource_type),
        "resource_status": E(x.change_status.resource_status),
        "campaign": x.change_status.campaign or "",
        "ad_group": x.change_status.ad_group or "",
        "ad_group_criterion": x.change_status.ad_group_criterion or "",
        "ad_group_ad": x.change_status.ad_group_ad or "",
        "campaign_criterion": x.change_status.campaign_criterion or "",
    } for x in rows]
    print(f"change events (30d API cap): {len(change_rows)} | change_status rows: {len(snap['change_status'])}")

    # ---------- recommendations (read only, never applied) ----------
    rows = r.rows("recommendations", """
        SELECT recommendation.type, recommendation.campaign, recommendation.ad_group,
               recommendation.dismissed, recommendation.resource_name
        FROM recommendation
    """)
    snap["recommendations"] = [{
        "type": E(x.recommendation.type_), "campaign": x.recommendation.campaign or "",
        "ad_group": x.recommendation.ad_group or "",
        "dismissed": bool(x.recommendation.dismissed),
    } for x in rows]

    rows = r.rows("recommendation_subscriptions", """
        SELECT recommendation_subscription.type, recommendation_subscription.status
        FROM recommendation_subscription
    """)
    snap["recommendation_subscriptions"] = [{
        "type": E(x.recommendation_subscription.type_),
        "status": E(x.recommendation_subscription.status),
    } for x in rows]
    print(f"recommendations: {len(snap['recommendations'])} | "
          f"auto-apply subscriptions: {len(snap['recommendation_subscriptions'])}")

    # ---------- calls ----------
    # call_view carries no segments.date; it returns the full retained call log.
    rows = r.rows("call_view", """
        SELECT call_view.caller_area_code, call_view.caller_country_code,
               call_view.call_duration_seconds, call_view.call_status,
               call_view.type, call_view.start_call_date_time,
               call_view.end_call_date_time, call_view.call_tracking_display_location,
               campaign.id, campaign.name, campaign.status
        FROM call_view
    """)
    snap["calls"] = [{
        "area_code": x.call_view.caller_area_code or "",
        "country_code": x.call_view.caller_country_code or "",
        "duration_seconds": int(x.call_view.call_duration_seconds or 0),
        "call_status": E(x.call_view.call_status),
        "type": E(x.call_view.type_),
        "start": x.call_view.start_call_date_time or "",
        "display_location": E(x.call_view.call_tracking_display_location),
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "campaign_status": E(x.campaign.status),
    } for x in rows]
    print(f"call_view rows (all retained): {len(snap['calls'])}")

    # ---------- asset groups (PMax) ----------
    rows = r.rows("asset_groups", """
        SELECT asset_group.id, asset_group.name, asset_group.status,
               asset_group.final_urls, asset_group.final_mobile_urls,
               asset_group.path1, asset_group.path2,
               campaign.id, campaign.name, campaign.status
        FROM asset_group
    """)
    snap["asset_groups"] = [{
        "id": str(x.asset_group.id), "name": x.asset_group.name,
        "status": E(x.asset_group.status), "final_urls": list(x.asset_group.final_urls),
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "campaign_status": E(x.campaign.status),
    } for x in rows]

    snap["read_errors"] = r.read_errors
    snap["queries_executed"] = r.queries_executed

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, indent=2, default=str), encoding="utf-8")
    print(f"\nread errors: {len(r.read_errors)}")
    for err in r.read_errors:
        print(f"  {err['query']}: {err['error'][:220]}")
    print(f"queries executed: {len(r.queries_executed)}")
    print(f"snapshot: {out}  ({out.stat().st_size/1_000_000:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
