#!/usr/bin/env python3
"""2026-09-28 (run B) READ-ONLY fresh snapshot for Apogee Lawns LLC - Live (8164626278).

Independent re-verification of the 2026-09-28 low-volume audit. Every query runs on its own
so one unsupported field is recorded as an error instead of hiding the rest. Nothing mutates.
Raw search terms are written to a separate file and never printed.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

from google.protobuf.json_format import MessageToDict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, EXACT_NAME, GM_MANAGER, E, client, q, write  # noqa: E402

CAMP = "24257151015"
c = client()
RUN_AT = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
S = {"run_at_utc": RUN_AT, "customer_id": CID, "errors": {}}


def M(v):
    return round(v / 1e6, 2)


def pb(msg):
    return MessageToDict(msg._pb, preserving_proto_field_name=True)


def run(label, query, cid=CID):
    try:
        rows = q(c, query, cid=cid)
        return rows
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        i = msg.find("message:")
        S["errors"][label] = msg[i:i + 400] if i >= 0 else msg[:400]
        print(f"  !! {label}: {S['errors'][label][:200]}")
        return []


# ---------------------------------------------------------------- identity + clock
r = run("identity_manager", f"""SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager,
    customer_client.test_account, customer_client.status, customer_client.level, customer_client.time_zone
    FROM customer_client WHERE customer_client.id = {CID}""", cid=GM_MANAGER)
S["identity_manager_view"] = [pb(x.customer_client) for x in r]
r = run("customer", """SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account,
    customer.status, customer.time_zone, customer.currency_code, customer.auto_tagging_enabled,
    customer.tracking_url_template, customer.final_url_suffix,
    customer.call_reporting_setting.call_reporting_enabled,
    customer.call_reporting_setting.call_conversion_reporting_enabled,
    customer.call_reporting_setting.call_conversion_action,
    customer.conversion_tracking_setting.conversion_tracking_id,
    customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
    customer.conversion_tracking_setting.google_ads_conversion_customer,
    customer.conversion_tracking_setting.conversion_tracking_status,
    customer.conversion_tracking_setting.accepted_customer_data_terms,
    customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
    customer.remarketing_setting.google_global_site_tag
    FROM customer""")
S["customer"] = pb(r[0].customer) if r else {}
S["customer"].pop("remarketing_setting", None)  # snippet text is long; the AW id is recorded below
cust = r[0].customer if r else None
S["identity_pass"] = bool(
    cust and str(cust.id) == CID and cust.descriptive_name == EXACT_NAME and not cust.manager
    and not cust.test_account and len(S["identity_manager_view"]) == 1
    and S["identity_manager_view"][0].get("descriptive_name") == EXACT_NAME)
print(f"IDENTITY {'PASS' if S['identity_pass'] else 'FAIL'}: {cust.id if cust else '?'} "
      f"'{cust.descriptive_name if cust else '?'}' manager={cust.manager if cust else '?'} "
      f"test={cust.test_account if cust else '?'} tz={cust.time_zone if cust else '?'}")
if not S["identity_pass"]:
    write(EVID / "2026-09-28b-snapshot.json", S)
    sys.exit("HARD STOP: identity mismatch")
if cust:
    import re
    m = re.search(r"AW-\d+", cust.remarketing_setting.google_global_site_tag or "")
    S["global_site_tag_aw_id"] = m.group(0) if m else None
for lbl, dur in (("yesterday", "YESTERDAY"), ("today", "TODAY")):
    rr = run(f"clock_{lbl}", f"SELECT segments.date, metrics.impressions FROM customer WHERE segments.date DURING {dur}")
    S[f"clock_{lbl}"] = [(x.segments.date, x.metrics.impressions) for x in rr]
print(f"  account clock: yesterday rows={S['clock_yesterday']} today rows={S['clock_today']}")

# ---------------------------------------------------------------- billing
S["billing_setups"] = [pb(x.billing_setup) for x in run("billing", """SELECT billing_setup.id, billing_setup.status,
    billing_setup.start_date_time, billing_setup.end_date_time FROM billing_setup""")]
S["account_budgets"] = [pb(x.account_budget) for x in run("account_budget", """SELECT account_budget.id,
    account_budget.status, account_budget.approved_start_date_time, account_budget.approved_end_date_time,
    account_budget.approved_spending_limit_type, account_budget.approved_spending_limit_micros,
    account_budget.amount_served_micros, account_budget.total_adjustments_micros FROM account_budget""")]

# ---------------------------------------------------------------- campaign + budget
r = run("campaign", """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
    campaign.primary_status, campaign.primary_status_reasons, campaign.advertising_channel_type,
    campaign.advertising_channel_sub_type, campaign.bidding_strategy_type, campaign.bidding_strategy,
    campaign.target_spend.cpc_bid_ceiling_micros, campaign.target_spend.target_spend_micros,
    campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
    campaign.network_settings.target_content_network, campaign.network_settings.target_partner_search_network,
    campaign.geo_target_type_setting.positive_geo_target_type, campaign.geo_target_type_setting.negative_geo_target_type,
    campaign.start_date_time, campaign.end_date_time, campaign.tracking_url_template, campaign.final_url_suffix,
    campaign.url_custom_parameters, campaign.keyword_match_type, campaign.ai_max_setting.enable_ai_max,
    campaign.asset_automation_settings, campaign.dynamic_search_ads_setting.domain_name,
    campaign.contains_eu_political_advertising, campaign.payment_mode, campaign.experiment_type,
    campaign.campaign_budget, campaign.labels, campaign.audience_setting.use_audience_grouped
    FROM campaign""")
S["campaigns"] = [pb(x.campaign) for x in r]
r = run("budget", """SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
    campaign_budget.delivery_method, campaign_budget.explicitly_shared, campaign_budget.period,
    campaign_budget.reference_count, campaign_budget.status, campaign_budget.total_amount_micros,
    campaign_budget.has_recommended_budget, campaign_budget.type FROM campaign_budget""")
S["budgets"] = [pb(x.campaign_budget) for x in r]

# ---------------------------------------------------------------- ad groups, keywords, negatives
S["ad_groups"] = [pb(x.ad_group) for x in run("ad_groups", """SELECT ad_group.id, ad_group.name, ad_group.status,
    ad_group.type, ad_group.cpc_bid_micros, ad_group.primary_status, ad_group.primary_status_reasons,
    ad_group.tracking_url_template, ad_group.final_url_suffix, ad_group.targeting_setting.target_restrictions,
    ad_group.ad_rotation_mode, campaign.id FROM ad_group""")]
r = run("ad_group_criteria", """SELECT ad_group.id, ad_group.name, ad_group_criterion.criterion_id, ad_group_criterion.type,
    ad_group_criterion.status, ad_group_criterion.negative, ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type, ad_group_criterion.system_serving_status,
    ad_group_criterion.approval_status, ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
    ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score,
    ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr,
    ad_group_criterion.cpc_bid_micros, ad_group_criterion.effective_cpc_bid_micros,
    ad_group_criterion.final_urls, ad_group_criterion.bid_modifier
    FROM ad_group_criterion""")
S["ad_group_criteria"] = [dict(ad_group_id=str(x.ad_group.id), ad_group=x.ad_group.name,
                               **pb(x.ad_group_criterion)) for x in r]
S["ad_group_bid_modifiers"] = [pb(x.ad_group_bid_modifier) for x in run("agbm", """SELECT ad_group_bid_modifier.criterion_id,
    ad_group_bid_modifier.bid_modifier, ad_group_bid_modifier.device.type FROM ad_group_bid_modifier""")]
r = run("campaign_criteria", """SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type,
    campaign_criterion.status, campaign_criterion.negative, campaign_criterion.bid_modifier,
    campaign_criterion.location.geo_target_constant, campaign_criterion.proximity.radius,
    campaign_criterion.language.language_constant, campaign_criterion.keyword.text,
    campaign_criterion.keyword.match_type, campaign_criterion.ad_schedule.day_of_week,
    campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour,
    campaign_criterion.device.type, campaign_criterion.user_list.user_list,
    campaign_criterion.age_range.type, campaign_criterion.gender.type, campaign_criterion.income_range.type,
    campaign_criterion.ip_block.ip_address, campaign_criterion.content_label.type FROM campaign_criterion""")
S["campaign_criteria"] = [dict(campaign_id=str(x.campaign.id), **pb(x.campaign_criterion)) for x in r]
S["campaign_bid_modifiers"] = [pb(x.campaign_bid_modifier) for x in run("cbm", """SELECT campaign_bid_modifier.criterion_id,
    campaign_bid_modifier.bid_modifier, campaign_bid_modifier.interaction_type.type FROM campaign_bid_modifier""")]
S["geo_names"] = {}
geos = [x["location"]["geo_target_constant"] for x in S["campaign_criteria"] if x.get("location")]
if geos:
    for x in run("geo_names", "SELECT geo_target_constant.resource_name, geo_target_constant.id, "
                 "geo_target_constant.canonical_name, geo_target_constant.target_type, geo_target_constant.status, "
                 "geo_target_constant.parent_geo_target FROM geo_target_constant WHERE geo_target_constant.resource_name IN ("
                 + ",".join(f"'{g}'" for g in geos) + ")"):
        g = x.geo_target_constant
        S["geo_names"][g.resource_name] = {"id": str(g.id), "canonical": g.canonical_name, "type": g.target_type,
                                           "status": E(g.status), "parent": g.parent_geo_target}

# shared sets / account-level negatives
S["shared_sets"] = [pb(x.shared_set) for x in run("shared_sets", """SELECT shared_set.id, shared_set.name, shared_set.type,
    shared_set.status, shared_set.member_count, shared_set.reference_count FROM shared_set""")]
S["campaign_shared_sets"] = [dict(campaign_id=str(x.campaign.id), **pb(x.campaign_shared_set)) for x in run(
    "campaign_shared_sets", """SELECT campaign.id, campaign_shared_set.shared_set, campaign_shared_set.status
    FROM campaign_shared_set""")]
S["customer_negative_criteria"] = [pb(x.customer_negative_criterion) for x in run("cnc", """SELECT
    customer_negative_criterion.id, customer_negative_criterion.type,
    customer_negative_criterion.negative_keyword_list.shared_set, customer_negative_criterion.content_label.type
    FROM customer_negative_criterion""")]
# members of any list that is attached anywhere or is account-level; else counts only
attached = {x["shared_set"] for x in S["campaign_shared_sets"] if x.get("status") == "ENABLED"}
attached |= {x.get("negative_keyword_list", {}).get("shared_set") for x in S["customer_negative_criteria"]
             if x.get("negative_keyword_list")}
attached.discard(None)
S["effective_shared_list_members"] = []
for ss in attached:
    for x in run(f"shared_members_{ss}", f"""SELECT shared_criterion.criterion_id, shared_criterion.keyword.text,
        shared_criterion.keyword.match_type, shared_set.id FROM shared_criterion WHERE shared_set.resource_name = '{ss}'"""):
        S["effective_shared_list_members"].append({"shared_set": ss, "id": str(x.shared_criterion.criterion_id),
                                                    "text": x.shared_criterion.keyword.text,
                                                    "mt": E(x.shared_criterion.keyword.match_type)})

# ---------------------------------------------------------------- ads + assets
r = run("ads", """SELECT ad_group.id, ad_group.name, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.primary_status,
    ad_group_ad.primary_status_reasons, ad_group_ad.policy_summary.approval_status,
    ad_group_ad.policy_summary.review_status, ad_group_ad.policy_summary.policy_topic_entries,
    ad_group_ad.ad_strength, ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
    ad_group_ad.ad.tracking_url_template, ad_group_ad.ad.final_url_suffix,
    ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions,
    ad_group_ad.ad.responsive_search_ad.path1, ad_group_ad.ad.responsive_search_ad.path2
    FROM ad_group_ad""")
S["ads"] = [dict(ad_group_id=str(x.ad_group.id), ad_group=x.ad_group.name, **pb(x.ad_group_ad)) for x in r]
for lvl, res, extra in (("campaign_asset", "campaign_asset", "campaign.id,"),
                        ("ad_group_asset", "ad_group_asset", "ad_group.id,"),
                        ("customer_asset", "customer_asset", "")):
    rr = run(lvl, f"""SELECT {extra} {res}.field_type, {res}.status, {res}.primary_status, {res}.primary_status_reasons,
        {res}.source, asset.id, asset.type, asset.name, asset.policy_summary.approval_status,
        asset.policy_summary.review_status, asset.callout_asset.callout_text, asset.structured_snippet_asset.header,
        asset.structured_snippet_asset.values, asset.sitelink_asset.link_text, asset.call_asset.phone_number,
        asset.call_asset.country_code, asset.call_asset.call_conversion_reporting_state,
        asset.call_asset.call_conversion_action, asset.call_asset.ad_schedule_targets FROM {res}""")
    S[lvl] = [dict(**pb(getattr(x, res)), asset=pb(x.asset)) for x in rr]

# ---------------------------------------------------------------- conversions + goals
r = run("conversion_actions", """SELECT conversion_action.id, conversion_action.name, conversion_action.status,
    conversion_action.type, conversion_action.category, conversion_action.origin, conversion_action.primary_for_goal,
    conversion_action.include_in_conversions_metric, conversion_action.counting_type,
    conversion_action.click_through_lookback_window_days, conversion_action.phone_call_duration_seconds,
    conversion_action.value_settings.default_value, conversion_action.value_settings.always_use_default_value,
    conversion_action.owner_customer, conversion_action.attribution_model_settings.attribution_model,
    conversion_action.attribution_model_settings.data_driven_model_status, conversion_action.tag_snippets
    FROM conversion_action""")
S["conversion_actions"] = []
for x in r:
    d = pb(x.conversion_action)
    snippets = d.pop("tag_snippets", [])
    labels = sorted({s for t in snippets for s in __import__("re").findall(r"AW-\d+/[A-Za-z0-9_-]+", t.get("event_snippet", ""))})
    d["send_to"] = labels
    S["conversion_actions"].append(d)
S["conversion_action_179"] = [pb(x.conversion_action) for x in run("ca179", """SELECT conversion_action.id,
    conversion_action.name, conversion_action.status FROM conversion_action WHERE conversion_action.id = 179""")]
S["customer_conversion_goals"] = [pb(x.customer_conversion_goal) for x in run("ccg", """SELECT
    customer_conversion_goal.category, customer_conversion_goal.origin, customer_conversion_goal.biddable
    FROM customer_conversion_goal""")]
S["campaign_conversion_goals"] = [pb(x.campaign_conversion_goal) for x in run("campcg", """SELECT campaign.id,
    campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable
    FROM campaign_conversion_goal""")]
S["goal_campaign_config"] = [pb(x.conversion_goal_campaign_config) for x in run("gcc", """SELECT campaign.id,
    conversion_goal_campaign_config.goal_config_level, conversion_goal_campaign_config.custom_conversion_goal
    FROM conversion_goal_campaign_config""")]
S["custom_conversion_goals"] = [pb(x.custom_conversion_goal) for x in run("custom_goals", """SELECT
    custom_conversion_goal.id, custom_conversion_goal.name, custom_conversion_goal.status,
    custom_conversion_goal.conversion_actions FROM custom_conversion_goal""")]

# ---------------------------------------------------------------- performance
MET = """metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.interactions, metrics.conversions,
    metrics.all_conversions, metrics.search_impression_share, metrics.search_budget_lost_impression_share,
    metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,
    metrics.search_absolute_top_impression_share, metrics.search_budget_lost_top_impression_share,
    metrics.search_rank_lost_top_impression_share, metrics.search_exact_match_impression_share,
    metrics.search_click_share, metrics.phone_calls, metrics.phone_impressions, metrics.invalid_clicks"""
WIN = {"since_first_serving": ("2026-09-17", "2026-09-28"), "completed_days": ("2026-09-17", "2026-09-27"),
       "latest_7_complete": ("2026-09-21", "2026-09-27"), "partial_today": ("2026-09-28", "2026-09-28")}
S["windows"] = {}
for w, (a, b) in WIN.items():
    rr = run(f"agg_{w}", f"SELECT campaign.id, {MET} FROM campaign WHERE segments.date BETWEEN '{a}' AND '{b}'")
    S["windows"][w] = {"range": [a, b], "rows": [pb(x.metrics) for x in rr]}
S["daily"] = {x.segments.date: pb(x.metrics) for x in run("daily", f"""SELECT segments.date, {MET} FROM campaign
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")}
S["lifetime_before_launch"] = [pb(x.metrics) for x in run("pre", """SELECT metrics.impressions, metrics.cost_micros
    FROM customer WHERE segments.date BETWEEN '2015-01-01' AND '2026-09-16'""")]
kwmet = """metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions,
    metrics.search_impression_share, metrics.search_rank_lost_impression_share,
    metrics.search_exact_match_impression_share, metrics.search_top_impression_share"""
S["keyword_perf"] = [dict(ad_group_id=str(x.ad_group.id), criterion_id=str(x.ad_group_criterion.criterion_id),
                          text=x.ad_group_criterion.keyword.text, mt=E(x.ad_group_criterion.keyword.match_type),
                          **pb(x.metrics)) for x in run("kw_perf", f"""SELECT ad_group.id, ad_group_criterion.criterion_id,
    ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, {kwmet} FROM keyword_view
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["ad_group_perf"] = [dict(ad_group_id=str(x.ad_group.id), **pb(x.metrics)) for x in run("ag_perf", f"""SELECT ad_group.id,
    {kwmet} FROM ad_group WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["ad_perf"] = [dict(ad_id=str(x.ad_group_ad.ad.id), **pb(x.metrics)) for x in run("ad_perf", """SELECT ad_group_ad.ad.id,
    metrics.impressions, metrics.clicks, metrics.cost_micros FROM ad_group_ad
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["device"] = [dict(device=E(x.segments.device), **pb(x.metrics)) for x in run("device", """SELECT segments.device,
    metrics.impressions, metrics.clicks, metrics.cost_micros FROM campaign WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["network"] = [dict(net=E(x.segments.ad_network_type), **pb(x.metrics)) for x in run("network", """SELECT segments.ad_network_type,
    metrics.impressions, metrics.clicks, metrics.cost_micros FROM campaign WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["click_type"] = [dict(ct=E(x.segments.click_type), **pb(x.metrics)) for x in run("click_type", """SELECT segments.click_type,
    metrics.impressions, metrics.clicks, metrics.cost_micros FROM campaign WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["hourly"] = [dict(date=x.segments.date, hour=x.segments.hour, **pb(x.metrics)) for x in run("hourly", """SELECT segments.date,
    segments.hour, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.search_impression_share,
    metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share FROM campaign
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["conv_by_action"] = [dict(action=x.segments.conversion_action_name, **pb(x.metrics)) for x in run("conv_by_action", """SELECT
    segments.conversion_action_name, metrics.all_conversions, metrics.conversions FROM campaign
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["conv_action_all_conversions_lifetime"] = [dict(id=str(x.conversion_action.id), **pb(x.metrics)) for x in run("ca_allconv", """SELECT
    conversion_action.id, metrics.all_conversions FROM conversion_action
    WHERE segments.date BETWEEN '2026-09-16' AND '2026-09-28'""")]
S["call_view"] = [pb(x.call_view) for x in run("call_view", """SELECT call_view.start_call_date_time, call_view.call_status,
    call_view.call_duration_seconds, call_view.type, call_view.call_tracking_display_location FROM call_view""")]
S["asset_perf_call"] = [dict(**pb(x.metrics)) for x in run("call_asset_perf", """SELECT asset.id, campaign_asset.field_type,
    metrics.impressions, metrics.clicks, metrics.phone_calls FROM campaign_asset
    WHERE campaign_asset.field_type = 'CALL' AND segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]

# ---------------------------------------------------------------- geo
S["location_view"] = [dict(criterion_id=str(x.campaign_criterion.criterion_id), **pb(x.metrics)) for x in run("location_view", """SELECT
    campaign_criterion.criterion_id, metrics.impressions, metrics.clicks, metrics.cost_micros FROM location_view
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["user_location_view"] = [dict(targeting_location=x.user_location_view.targeting_location,
                                country=str(x.user_location_view.country_criterion_id),
                                most_specific=x.segments.geo_target_most_specific_location, **pb(x.metrics))
                           for x in run("ulv", """SELECT user_location_view.country_criterion_id,
    user_location_view.targeting_location, segments.geo_target_most_specific_location, metrics.impressions,
    metrics.clicks FROM user_location_view WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]
S["geographic_view"] = [dict(location_type=E(x.geographic_view.location_type), **pb(x.metrics)) for x in run("geographic_view", """SELECT
    geographic_view.location_type, geographic_view.country_criterion_id, metrics.impressions, metrics.clicks
    FROM geographic_view WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")]

# ---------------------------------------------------------------- search terms (raw to disk only)
r = run("search_terms", """SELECT ad_group.id, search_term_view.search_term, search_term_view.status,
    segments.keyword.info.text, segments.keyword.info.match_type, segments.search_term_match_type, segments.date,
    metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.all_conversions FROM search_term_view
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
raw = [{"ad_group_id": str(x.ad_group.id), "term": x.search_term_view.search_term,
        "status": E(x.search_term_view.status), "kw": x.segments.keyword.info.text,
        "kw_mt": E(x.segments.keyword.info.match_type), "st_mt": E(x.segments.search_term_match_type),
        "date": x.segments.date, "impr": x.metrics.impressions, "clicks": x.metrics.clicks,
        "cost": M(x.metrics.cost_micros), "all_conv": x.metrics.all_conversions} for x in r]
write(EVID / "2026-09-28b-search-terms-RAW.json", raw)
S["search_terms_rowcount"] = len(raw)

# ---------------------------------------------------------------- change history
r = run("change_event", """SELECT change_event.change_date_time, change_event.change_resource_type,
    change_event.resource_change_operation, change_event.client_type, change_event.user_email,
    change_event.changed_fields, change_event.change_resource_name, change_event.old_resource, change_event.new_resource
    FROM change_event WHERE change_event.change_date_time >= '2026-08-30 00:00:00'
    AND change_event.change_date_time <= '2026-09-28 23:59:59' ORDER BY change_event.change_date_time ASC LIMIT 2000""")
S["change_events"] = []
for x in r:
    e = x.change_event
    S["change_events"].append({"t": e.change_date_time, "type": E(e.change_resource_type),
                               "op": E(e.resource_change_operation), "client": E(e.client_type),
                               "user_is_agency_login": (e.user_email or "").lower() == "access@greenmarketingfl.com",
                               "fields": list(e.changed_fields.paths), "res": e.change_resource_name,
                               "old": pb(e.old_resource), "new": pb(e.new_resource)})
S["change_status"] = [pb(x.change_status) for x in run("change_status", """SELECT change_status.resource_type,
    change_status.resource_status, change_status.last_change_date_time, change_status.resource_name
    FROM change_status WHERE change_status.last_change_date_time >= '2026-09-15 00:00:00'
    AND change_status.last_change_date_time <= '2026-09-28 23:59:59' LIMIT 10000""")]

write(EVID / "2026-09-28b-snapshot.json", S)
print(f"errors: {len(S['errors'])} -> {list(S['errors'])}")
