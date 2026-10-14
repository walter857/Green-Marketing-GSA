#!/usr/bin/env python3
"""2026-09-26 READ-ONLY full snapshot for MasterGrass - Live (9487471092).

GAQL SELECT only. Every query result is written to its own JSON file under
clients/mastergrass-lawn-care/snapshots/audit-2026-09-26/. Search-term and
click-level corpora are written to disk and never printed.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

from google.protobuf.json_format import MessageToDict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import SNAP, client, q, write  # noqa: E402

OUT = SNAP / "audit-2026-09-26"
c = client()

D90 = "segments.date BETWEEN '2026-06-28' AND '2026-09-26'"
D30 = "segments.date BETWEEN '2026-08-28' AND '2026-09-26'"
DALL = "segments.date BETWEEN '2020-01-01' AND '2026-09-26'"

errors: dict[str, str] = {}


def rows_to_dicts(rows):
    return [MessageToDict(r._pb, preserving_proto_field_name=True) for r in rows]


def run(name: str, query: str, quiet: bool = False):
    try:
        rows = q(c, query)
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        errors[name] = msg[:800]
        print(f"  [ERR] {name}: {type(exc).__name__}: {msg[:300]}")
        return None
    data = rows_to_dicts(rows)
    path = OUT / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(data, indent=0, default=str), encoding="utf-8")
    print(f"  [OK ] {name}: {len(data)} rows")
    return data


print("=== STRUCTURE ===")
run("customer", """
SELECT customer.id, customer.descriptive_name, customer.auto_tagging_enabled,
       customer.tracking_url_template, customer.final_url_suffix,
       customer.optimization_score, customer.status
FROM customer""")

run("campaigns", """
SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
       campaign.primary_status, campaign.primary_status_reasons,
       campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
       campaign.bidding_strategy_type, campaign.bidding_strategy,
       campaign.target_spend.cpc_bid_ceiling_micros,
       campaign.maximize_conversions.target_cpa_micros,
       campaign.target_cpa.target_cpa_micros,
       campaign.manual_cpc.enhanced_cpc_enabled,
       campaign.campaign_budget, campaign_budget.amount_micros,
       campaign_budget.delivery_method, campaign_budget.explicitly_shared,
       campaign.network_settings.target_google_search,
       campaign.network_settings.target_search_network,
       campaign.network_settings.target_content_network,
       campaign.network_settings.target_partner_search_network,
       campaign.geo_target_type_setting.positive_geo_target_type,
       campaign.geo_target_type_setting.negative_geo_target_type,
       campaign.start_date_time, campaign.end_date_time,
       campaign.tracking_url_template, campaign.final_url_suffix,
       campaign.ai_max_setting.enable_ai_max,
       campaign.asset_automation_settings,
       campaign.optimization_score
FROM campaign""")

run("campaign_budgets", """
SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
       campaign_budget.status, campaign_budget.explicitly_shared,
       campaign_budget.reference_count, campaign_budget.has_recommended_budget,
       campaign_budget.recommended_budget_amount_micros
FROM campaign_budget""")

run("account_budget", """
SELECT account_budget.id, account_budget.status, account_budget.name,
       account_budget.approved_spending_limit_micros,
       account_budget.approved_spending_limit_type,
       account_budget.amount_served_micros, account_budget.total_adjustments_micros,
       account_budget.approved_start_date_time, account_budget.approved_end_date_time,
       account_budget.approved_end_time_type
FROM account_budget""")

run("billing_setup", """
SELECT billing_setup.id, billing_setup.status, billing_setup.start_date_time,
       billing_setup.end_date_time, billing_setup.payments_account
FROM billing_setup""")

run("ad_groups", """
SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
       ad_group.primary_status, ad_group.primary_status_reasons,
       ad_group.cpc_bid_micros, campaign.id, campaign.name, campaign.status
FROM ad_group""")

run("keywords", """
SELECT ad_group_criterion.criterion_id, ad_group.id, ad_group.name, campaign.id,
       campaign.name, ad_group_criterion.keyword.text,
       ad_group_criterion.keyword.match_type, ad_group_criterion.status,
       ad_group_criterion.negative, ad_group_criterion.approval_status,
       ad_group_criterion.system_serving_status,
       ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
       ad_group_criterion.quality_info.quality_score,
       ad_group_criterion.quality_info.creative_quality_score,
       ad_group_criterion.quality_info.post_click_quality_score,
       ad_group_criterion.quality_info.search_predicted_ctr,
       ad_group_criterion.final_urls, ad_group_criterion.cpc_bid_micros,
       ad_group_criterion.effective_cpc_bid_micros,
       ad_group_criterion.position_estimates.first_page_cpc_micros,
       ad_group_criterion.position_estimates.top_of_page_cpc_micros,
       ad_group_criterion.position_estimates.first_position_cpc_micros
FROM ad_group_criterion
WHERE ad_group_criterion.type = 'KEYWORD'""")

run("ads", """
SELECT ad_group_ad.ad.id, ad_group.id, ad_group.name, campaign.id, campaign.name,
       ad_group_ad.status, ad_group_ad.primary_status, ad_group_ad.primary_status_reasons,
       ad_group_ad.ad.type, ad_group_ad.ad.final_urls,
       ad_group_ad.ad.responsive_search_ad.headlines,
       ad_group_ad.ad.responsive_search_ad.descriptions,
       ad_group_ad.ad.responsive_search_ad.path1,
       ad_group_ad.ad.responsive_search_ad.path2,
       ad_group_ad.ad_strength, ad_group_ad.action_items,
       ad_group_ad.policy_summary.approval_status,
       ad_group_ad.policy_summary.review_status,
       ad_group_ad.policy_summary.policy_topic_entries
FROM ad_group_ad""")

run("rsa_asset_view", f"""
SELECT ad_group_ad_asset_view.ad_group_ad, ad_group_ad_asset_view.field_type,
       ad_group_ad_asset_view.performance_label, ad_group_ad_asset_view.pinned_field,
       ad_group_ad_asset_view.enabled, asset.text_asset.text, asset.id,
       campaign.id, ad_group.id, metrics.impressions, metrics.clicks, metrics.cost_micros,
       metrics.conversions
FROM ad_group_ad_asset_view
WHERE {D90}""")

run("campaign_assets", """
SELECT campaign.id, campaign.name, campaign_asset.field_type, campaign_asset.status,
       campaign_asset.primary_status, campaign_asset.source, asset.id, asset.type, asset.name,
       asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
       asset.sitelink_asset.description2, asset.final_urls,
       asset.callout_asset.callout_text, asset.call_asset.phone_number,
       asset.call_asset.call_conversion_reporting_state,
       asset.call_asset.call_conversion_action,
       asset.structured_snippet_asset.header, asset.structured_snippet_asset.values,
       asset.image_asset.full_size.url, asset.business_profile_location.labels
FROM campaign_asset""")

run("ad_group_assets", """
SELECT campaign.id, ad_group.id, ad_group.name, ad_group_asset.field_type,
       ad_group_asset.status, ad_group_asset.primary_status, ad_group_asset.source,
       asset.id, asset.type, asset.sitelink_asset.link_text, asset.final_urls,
       asset.callout_asset.callout_text, asset.call_asset.phone_number,
       asset.call_asset.call_conversion_reporting_state,
       asset.call_asset.call_conversion_action
FROM ad_group_asset""")

run("customer_assets", """
SELECT customer_asset.field_type, customer_asset.status, customer_asset.primary_status,
       customer_asset.source, asset.id, asset.type, asset.name,
       asset.sitelink_asset.link_text, asset.final_urls, asset.callout_asset.callout_text,
       asset.call_asset.phone_number, asset.call_asset.call_conversion_reporting_state,
       asset.call_asset.call_conversion_action
FROM customer_asset""")

run("campaign_criteria", """
SELECT campaign.id, campaign.name, campaign_criterion.criterion_id,
       campaign_criterion.type, campaign_criterion.negative, campaign_criterion.status,
       campaign_criterion.bid_modifier, campaign_criterion.location.geo_target_constant,
       campaign_criterion.proximity.radius, campaign_criterion.proximity.radius_units,
       campaign_criterion.proximity.address.city_name,
       campaign_criterion.proximity.address.postal_code,
       campaign_criterion.proximity.geo_point.latitude_in_micro_degrees,
       campaign_criterion.proximity.geo_point.longitude_in_micro_degrees,
       campaign_criterion.ad_schedule.day_of_week,
       campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour,
       campaign_criterion.ad_schedule.start_minute, campaign_criterion.ad_schedule.end_minute,
       campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
       campaign_criterion.device.type, campaign_criterion.language.language_constant
FROM campaign_criterion""")

run("shared_sets", """
SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
       shared_set.member_count, shared_set.reference_count
FROM shared_set""")

run("campaign_shared_sets", """
SELECT campaign.id, campaign.name, campaign_shared_set.shared_set,
       campaign_shared_set.status, shared_set.name, shared_set.type
FROM campaign_shared_set""")

run("shared_criteria", """
SELECT shared_set.id, shared_set.name, shared_criterion.keyword.text,
       shared_criterion.keyword.match_type, shared_criterion.type
FROM shared_criterion""", quiet=True)

run("customer_negative_criteria", """
SELECT customer_negative_criterion.id, customer_negative_criterion.type,
       customer_negative_criterion.negative_keyword_list.shared_set
FROM customer_negative_criterion""")

print("=== CONVERSIONS ===")
run("conversion_actions", """
SELECT conversion_action.id, conversion_action.name, conversion_action.status,
       conversion_action.type, conversion_action.category, conversion_action.origin,
       conversion_action.primary_for_goal, conversion_action.counting_type,
       conversion_action.include_in_conversions_metric,
       conversion_action.click_through_lookback_window_days,
       conversion_action.view_through_lookback_window_days,
       conversion_action.attribution_model_settings.attribution_model,
       conversion_action.value_settings.default_value,
       conversion_action.value_settings.always_use_default_value,
       conversion_action.phone_call_duration_seconds,
       conversion_action.tag_snippets, conversion_action.owner_customer,
       metrics.all_conversions
FROM conversion_action""")

run("customer_conversion_goals", """
SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
       customer_conversion_goal.biddable
FROM customer_conversion_goal""")

run("conversion_goal_campaign_config", """
SELECT conversion_goal_campaign_config.campaign,
       conversion_goal_campaign_config.goal_config_level,
       conversion_goal_campaign_config.custom_conversion_goal
FROM conversion_goal_campaign_config""")

run("campaign_conversion_goals", """
SELECT campaign_conversion_goal.campaign, campaign_conversion_goal.category,
       campaign_conversion_goal.origin, campaign_conversion_goal.biddable
FROM campaign_conversion_goal""")

run("conv_by_action_date_all", f"""
SELECT segments.date, campaign.id, segments.conversion_action,
       segments.conversion_action_name, segments.conversion_action_category,
       metrics.conversions, metrics.all_conversions
FROM campaign
WHERE {DALL} AND metrics.all_conversions > 0""")

run("conv_by_conversion_date_all", f"""
SELECT segments.date, campaign.id, segments.conversion_action_name,
       metrics.conversions_by_conversion_date,
       metrics.all_conversions_by_conversion_date
FROM campaign
WHERE {DALL} AND metrics.all_conversions_by_conversion_date > 0""")

run("call_view", """
SELECT call_view.caller_area_code, call_view.call_duration_seconds,
       call_view.start_call_date_time, call_view.end_call_date_time,
       call_view.call_status, call_view.call_tracking_display_location,
       call_view.type, campaign.id, ad_group.id
FROM call_view""")

print("=== PERFORMANCE ===")
run("campaign_daily_all", f"""
SELECT segments.date, campaign.id, campaign.name, metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions, metrics.all_conversions,
       metrics.conversions_value, metrics.interactions, metrics.phone_calls,
       metrics.phone_impressions, metrics.invalid_clicks,
       metrics.search_impression_share, metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,
       metrics.search_absolute_top_impression_share, metrics.average_cpc
FROM campaign
WHERE {DALL} AND metrics.impressions > 0""")

run("campaign_device_90", f"""
SELECT campaign.id, segments.device, metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions, metrics.all_conversions
FROM campaign WHERE {D90}""")

run("campaign_click_type_90", f"""
SELECT campaign.id, segments.click_type, metrics.clicks, metrics.cost_micros,
       metrics.conversions, metrics.all_conversions
FROM campaign WHERE {D90}""")

run("campaign_hour_90", f"""
SELECT campaign.id, segments.day_of_week, segments.hour, metrics.clicks,
       metrics.cost_micros, metrics.conversions
FROM campaign WHERE {D90}""")

run("adgroup_daily_90", f"""
SELECT segments.date, campaign.id, ad_group.id, ad_group.name, metrics.impressions,
       metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions,
       metrics.search_rank_lost_impression_share, metrics.search_impression_share
FROM ad_group WHERE {D90} AND metrics.impressions > 0""")

run("keyword_perf_all", f"""
SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id,
       ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
       metrics.all_conversions, metrics.search_impression_share,
       metrics.search_rank_lost_impression_share, metrics.search_top_impression_share
FROM keyword_view WHERE {DALL} AND metrics.impressions > 0""")

run("keyword_perf_7", """
SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id,
       ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
       metrics.all_conversions, metrics.average_cpc
FROM keyword_view WHERE segments.date BETWEEN '2026-09-19' AND '2026-09-26'
  AND metrics.impressions > 0""")

run("ad_perf_all", f"""
SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, metrics.impressions,
       metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions,
       metrics.ctr
FROM ad_group_ad WHERE {DALL} AND metrics.impressions > 0""")

run("ad_perf_30", f"""
SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, metrics.impressions,
       metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.ctr
FROM ad_group_ad WHERE {D30} AND metrics.impressions > 0""")

run("landing_pages_90", f"""
SELECT landing_page_view.unexpanded_final_url, campaign.id, metrics.clicks,
       metrics.cost_micros, metrics.conversions, metrics.all_conversions,
       metrics.mobile_friendly_clicks_percentage, metrics.speed_score
FROM landing_page_view WHERE {D90} AND metrics.clicks > 0""")

run("expanded_landing_pages_90", f"""
SELECT expanded_landing_page_view.expanded_final_url, campaign.id, metrics.clicks,
       metrics.cost_micros, metrics.conversions
FROM expanded_landing_page_view WHERE {D90} AND metrics.clicks > 0""")

run("geo_user_location_90", f"""
SELECT campaign.id, user_location_view.country_criterion_id,
       user_location_view.targeting_location, segments.geo_target_city,
       segments.geo_target_region, metrics.clicks, metrics.cost_micros,
       metrics.conversions, metrics.impressions
FROM user_location_view WHERE {D90} AND metrics.impressions > 0""")

run("location_view_90", f"""
SELECT campaign.id, campaign_criterion.criterion_id, location_view.resource_name,
       metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.impressions
FROM location_view WHERE {D90} AND metrics.impressions > 0""")

print("=== SEARCH TERMS (to disk only) ===")
run("search_terms_all", f"""
SELECT search_term_view.search_term, search_term_view.status, campaign.id, ad_group.id,
       segments.keyword.info.text, segments.keyword.info.match_type,
       segments.search_term_match_type, segments.date,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
       metrics.all_conversions
FROM search_term_view WHERE {DALL} AND metrics.impressions > 0""", quiet=True)

run("campaign_search_term_view_all", f"""
SELECT campaign_search_term_view.search_term, campaign.id, segments.date,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM campaign_search_term_view WHERE {DALL} AND metrics.impressions > 0""", quiet=True)

print("=== CLICK VIEW (per day, last 35 days, to disk only) ===")
clicks = []
start = datetime.date(2026, 8, 23)
d = start
while d <= datetime.date(2026, 9, 26):
    try:
        rows = q(c, f"""
        SELECT click_view.gclid, click_view.ad_group_ad, click_view.keyword,
               click_view.keyword_info.text, click_view.keyword_info.match_type,
               click_view.area_of_interest.city, click_view.location_of_presence.city,
               click_view.location_of_presence.most_specific,
               click_view.page_number, segments.click_type, segments.device,
               segments.date, campaign.id, ad_group.id, metrics.clicks
        FROM click_view WHERE segments.date = '{d.isoformat()}'""")
        clicks.extend(rows_to_dicts(rows))
    except Exception as exc:  # noqa: BLE001
        errors[f"click_view_{d}"] = str(exc)[:400]
    d += datetime.timedelta(days=1)
import json  # noqa: E402

(OUT / "click_view_35.json").write_text(json.dumps(clicks, indent=0), encoding="utf-8")
print(f"  [OK ] click_view_35: {len(clicks)} rows")

print("=== CHANGE HISTORY ===")
run("change_event_29", """
SELECT change_event.change_date_time, change_event.change_resource_type,
       change_event.resource_change_operation, change_event.changed_fields,
       change_event.client_type, change_event.user_email, change_event.campaign,
       change_event.ad_group, change_event.change_resource_name,
       change_event.old_resource, change_event.new_resource
FROM change_event
WHERE change_event.change_date_time >= '2026-08-29 00:00:00'
  AND change_event.change_date_time <= '2026-09-26 23:59:59'
ORDER BY change_event.change_date_time DESC
LIMIT 10000""")

run("change_status_90", """
SELECT change_status.last_change_date_time, change_status.resource_type,
       change_status.resource_status, change_status.campaign, change_status.ad_group
FROM change_status
WHERE change_status.last_change_date_time >= '2026-06-28 00:00:00'
  AND change_status.last_change_date_time <= '2026-09-26 23:59:59'
LIMIT 10000""")

write(OUT / "_read_errors.json", errors)
print(f"\nread errors: {len(errors)}")
