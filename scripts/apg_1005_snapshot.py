#!/usr/bin/env python3
"""2026-10-05 READ-ONLY snapshot for Apogee Lawns LLC - Live (8164626278).

Feeds the ChatGPT handoff briefing and the low-CTR / low-volume research. Field lists are
the ones proven by apg_0928b_snapshot.py, extended with full ad text, every asset type,
asset sets, position, day-of-week and per-keyword impression share. Every query runs on its
own so one unsupported field is recorded as an error instead of hiding the rest.
Nothing mutates. Search terms go to their own files (the work order permits raw terms in
this deliverable); contact data is never requested.
"""
from __future__ import annotations

import csv
import datetime
import json
import re
import sys
from pathlib import Path

from google.protobuf.json_format import MessageToDict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, CLIENT_DIR, EXACT_NAME, GM_MANAGER, SNAP, E, client, q, write  # noqa: E402

LABEL = sys.argv[1] if len(sys.argv) > 1 else "briefing"
OUT = CLIENT_DIR / "audits" / ("2026-10-05-briefing-research" if LABEL == "briefing" else f"2026-10-05-{LABEL}")
START, END, TODAY = "2026-09-21", "2026-10-04", "2026-10-05"
c = client()
S = {"run_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
     "customer_id": CID, "window": [START, END], "partial_day": TODAY, "errors": {}}


def M(v):
    return round(v / 1e6, 2)


def pb(msg):
    return MessageToDict(msg._pb, preserving_proto_field_name=True)


def run(label, query, cid=CID):
    try:
        return q(c, query, cid=cid)
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        i = msg.find("message:")
        S["errors"][label] = msg[i:i + 400] if i >= 0 else msg[:400]
        print(f"  !! {label}: {S['errors'][label][:200]}")
        return []


def seg_rows(label, segment, extra_fields=""):
    rows = run(label, f"""SELECT {segment}, metrics.impressions, metrics.clicks, metrics.cost_micros,
        metrics.conversions, metrics.all_conversions {extra_fields} FROM campaign
        WHERE segments.date BETWEEN '{START}' AND '{END}'""")
    field = segment.split(".")[-1]
    return [dict(seg=getattr(x.segments, field) if field == "hour" else E(getattr(x.segments, field)),
                 **pb(x.metrics)) for x in rows]


# ---------------------------------------------------------------- identity
r = run("identity_manager", f"""SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager,
    customer_client.test_account, customer_client.status, customer_client.level
    FROM customer_client WHERE customer_client.id = {CID}""", cid=GM_MANAGER)
S["identity_manager_view"] = [pb(x.customer_client) for x in r]
r = run("customer", """SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account,
    customer.status, customer.time_zone, customer.currency_code, customer.auto_tagging_enabled,
    customer.tracking_url_template, customer.final_url_suffix,
    customer.call_reporting_setting.call_reporting_enabled,
    customer.call_reporting_setting.call_conversion_reporting_enabled,
    customer.call_reporting_setting.call_conversion_action,
    customer.conversion_tracking_setting.conversion_tracking_status,
    customer.conversion_tracking_setting.accepted_customer_data_terms,
    customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled
    FROM customer""")
S["customer"] = pb(r[0].customer) if r else {}
cust = r[0].customer if r else None
S["identity_pass"] = bool(cust and str(cust.id) == CID and cust.descriptive_name == EXACT_NAME
                          and not cust.manager and not cust.test_account
                          and len(S["identity_manager_view"]) == 1)
print(f"identity_pass={S['identity_pass']} name={cust.descriptive_name if cust else None!r}")
if not S["identity_pass"]:
    write(SNAP / f"2026-10-05-{LABEL}-snapshot.json", S)
    sys.exit("IDENTITY GATE FAILED - stopping")

S["billing_setups"] = [pb(x.billing_setup) for x in run("billing", """SELECT billing_setup.id, billing_setup.status,
    billing_setup.start_date_time, billing_setup.end_date_time FROM billing_setup""")]

# ---------------------------------------------------------------- campaigns, budgets, ad groups
r = run("campaign", """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
    campaign.primary_status, campaign.primary_status_reasons, campaign.advertising_channel_type,
    campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
    campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
    campaign.network_settings.target_content_network, campaign.network_settings.target_partner_search_network,
    campaign.geo_target_type_setting.positive_geo_target_type, campaign.geo_target_type_setting.negative_geo_target_type,
    campaign.start_date_time, campaign.end_date_time, campaign.tracking_url_template, campaign.final_url_suffix,
    campaign.keyword_match_type, campaign.ai_max_setting.enable_ai_max, campaign.asset_automation_settings,
    campaign.campaign_budget FROM campaign""")
S["campaigns"] = [pb(x.campaign) for x in r]
S["budgets"] = [pb(x.campaign_budget) for x in run("budget", """SELECT campaign_budget.id, campaign_budget.name,
    campaign_budget.amount_micros, campaign_budget.delivery_method, campaign_budget.explicitly_shared,
    campaign_budget.status, campaign_budget.type FROM campaign_budget""")]
S["ad_groups"] = [pb(x.ad_group) for x in run("ad_groups", """SELECT ad_group.id, ad_group.name, ad_group.status,
    ad_group.type, ad_group.cpc_bid_micros, ad_group.primary_status, ad_group.primary_status_reasons,
    campaign.id FROM ad_group""")]
r = run("ad_group_criteria", """SELECT ad_group.id, ad_group.name, ad_group_criterion.criterion_id, ad_group_criterion.type,
    ad_group_criterion.status, ad_group_criterion.negative, ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type, ad_group_criterion.system_serving_status,
    ad_group_criterion.approval_status, ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
    ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score,
    ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr,
    ad_group_criterion.effective_cpc_bid_micros, ad_group_criterion.final_urls, ad_group_criterion.bid_modifier,
    ad_group_criterion.position_estimates.first_page_cpc_micros,
    ad_group_criterion.position_estimates.top_of_page_cpc_micros,
    ad_group_criterion.position_estimates.first_position_cpc_micros
    FROM ad_group_criterion""")
S["ad_group_criteria"] = [dict(ad_group_id=str(x.ad_group.id), ad_group=x.ad_group.name,
                               **pb(x.ad_group_criterion)) for x in r]
S["ad_group_bid_modifiers"] = [pb(x.ad_group_bid_modifier) for x in run("agbm", """SELECT ad_group.id,
    ad_group_bid_modifier.criterion_id, ad_group_bid_modifier.bid_modifier, ad_group_bid_modifier.device.type
    FROM ad_group_bid_modifier""")]

# ---------------------------------------------------------------- campaign criteria + geo names
r = run("campaign_criteria", """SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type,
    campaign_criterion.status, campaign_criterion.negative, campaign_criterion.bid_modifier,
    campaign_criterion.location.geo_target_constant, campaign_criterion.proximity.radius,
    campaign_criterion.language.language_constant, campaign_criterion.keyword.text,
    campaign_criterion.keyword.match_type, campaign_criterion.ad_schedule.day_of_week,
    campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour,
    campaign_criterion.device.type FROM campaign_criterion""")
S["campaign_criteria"] = [dict(campaign_id=str(x.campaign.id), **pb(x.campaign_criterion)) for x in r]
S["geo_names"] = {}
geos = [x["location"]["geo_target_constant"] for x in S["campaign_criteria"] if x.get("location")]
if geos:
    for x in run("geo_names", "SELECT geo_target_constant.resource_name, geo_target_constant.id, "
                 "geo_target_constant.canonical_name, geo_target_constant.target_type, geo_target_constant.status "
                 "FROM geo_target_constant WHERE geo_target_constant.resource_name IN ("
                 + ",".join(f"'{g}'" for g in geos) + ")"):
        g = x.geo_target_constant
        S["geo_names"][g.resource_name] = {"id": str(g.id), "canonical": g.canonical_name, "type": g.target_type,
                                           "status": E(g.status)}
S["shared_sets"] = [pb(x.shared_set) for x in run("shared_sets", """SELECT shared_set.id, shared_set.name,
    shared_set.type, shared_set.status, shared_set.member_count, shared_set.reference_count FROM shared_set""")]
S["campaign_shared_sets"] = [dict(campaign_id=str(x.campaign.id), **pb(x.campaign_shared_set)) for x in run(
    "campaign_shared_sets", """SELECT campaign.id, campaign_shared_set.shared_set, campaign_shared_set.status
    FROM campaign_shared_set""")]
S["customer_negative_criteria"] = [pb(x.customer_negative_criterion) for x in run("cnc", """SELECT
    customer_negative_criterion.id, customer_negative_criterion.type,
    customer_negative_criterion.negative_keyword_list.shared_set, customer_negative_criterion.content_label.type
    FROM customer_negative_criterion""")]

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
ASSET_FIELDS = """asset.id, asset.type, asset.name, asset.final_urls, asset.policy_summary.approval_status,
    asset.policy_summary.review_status, asset.callout_asset.callout_text, asset.structured_snippet_asset.header,
    asset.structured_snippet_asset.values, asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
    asset.sitelink_asset.description2, asset.call_asset.phone_number, asset.call_asset.country_code,
    asset.call_asset.call_conversion_reporting_state, asset.call_asset.call_conversion_action,
    asset.call_asset.ad_schedule_targets, asset.text_asset.text, asset.image_asset.full_size.width_pixels,
    asset.image_asset.full_size.height_pixels"""
for lvl, extra in (("campaign_asset", "campaign.id,"), ("ad_group_asset", "ad_group.id,"), ("customer_asset", "")):
    rr = run(lvl, f"""SELECT {extra} {lvl}.field_type, {lvl}.status, {lvl}.primary_status, {lvl}.primary_status_reasons,
        {lvl}.source, {ASSET_FIELDS} FROM {lvl}""")
    S[lvl] = [dict(**pb(getattr(x, lvl)), asset=pb(x.asset)) for x in rr]
S["asset_sets"] = [pb(x.asset_set) for x in run("asset_sets", """SELECT asset_set.id, asset_set.name, asset_set.type,
    asset_set.status FROM asset_set""")]
S["campaign_asset_sets"] = [pb(x.campaign_asset_set) for x in run("campaign_asset_sets", """SELECT
    campaign_asset_set.campaign, campaign_asset_set.asset_set, campaign_asset_set.status FROM campaign_asset_set""")]
S["customer_asset_sets"] = [pb(x.customer_asset_set) for x in run("customer_asset_sets", """SELECT
    customer_asset_set.asset_set, customer_asset_set.status FROM customer_asset_set""")]
S["asset_perf"] = [dict(asset_id=str(x.asset.id), field_type=E(x.campaign_asset.field_type), **pb(x.metrics))
                   for x in run("asset_perf", f"""SELECT asset.id, campaign_asset.field_type, metrics.impressions,
    metrics.clicks FROM campaign_asset WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["customer_asset_perf"] = [dict(asset_id=str(x.asset.id), field_type=E(x.customer_asset.field_type), **pb(x.metrics))
                            for x in run("customer_asset_perf", f"""SELECT asset.id, customer_asset.field_type,
    metrics.impressions, metrics.clicks FROM customer_asset WHERE segments.date BETWEEN '{START}' AND '{END}'""")]

# ---------------------------------------------------------------- conversions + goals
r = run("conversion_actions", """SELECT conversion_action.id, conversion_action.name, conversion_action.status,
    conversion_action.type, conversion_action.category, conversion_action.origin, conversion_action.primary_for_goal,
    conversion_action.counting_type, conversion_action.click_through_lookback_window_days,
    conversion_action.phone_call_duration_seconds, conversion_action.tag_snippets FROM conversion_action""")
S["conversion_actions"] = []
for x in r:
    d = pb(x.conversion_action)
    snippets = d.pop("tag_snippets", [])
    d["send_to"] = sorted({s for t in snippets for s in re.findall(r"AW-\d+/[A-Za-z0-9_-]+", t.get("event_snippet", ""))})
    S["conversion_actions"].append(d)
S["campaign_conversion_goals"] = [pb(x.campaign_conversion_goal) for x in run("campcg", """SELECT campaign.id,
    campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable
    FROM campaign_conversion_goal""")]

# ---------------------------------------------------------------- performance
MET = """metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, metrics.average_cpc,
    metrics.interactions, metrics.conversions, metrics.all_conversions, metrics.search_impression_share,
    metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share,
    metrics.search_top_impression_share, metrics.search_absolute_top_impression_share,
    metrics.search_rank_lost_top_impression_share, metrics.search_budget_lost_top_impression_share,
    metrics.search_exact_match_impression_share, metrics.search_click_share,
    metrics.top_impression_percentage, metrics.absolute_top_impression_percentage,
    metrics.phone_calls, metrics.phone_impressions, metrics.invalid_clicks"""
WIN = {"launch_to_yesterday": (START, END), "first_7": ("2026-09-21", "2026-09-27"),
       "last_7": ("2026-09-28", END), "partial_today": (TODAY, TODAY)}
S["windows"] = {}
for w, (a, b) in WIN.items():
    rr = run(f"agg_{w}", f"SELECT campaign.id, {MET} FROM campaign WHERE segments.date BETWEEN '{a}' AND '{b}'")
    S["windows"][w] = {"range": [a, b], "rows": [pb(x.metrics) for x in rr]}
S["daily"] = {x.segments.date: pb(x.metrics) for x in run("daily", f"""SELECT segments.date, {MET} FROM campaign
    WHERE segments.date BETWEEN '{START}' AND '{TODAY}'""")}
KWMET = """metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, metrics.average_cpc,
    metrics.conversions, metrics.all_conversions, metrics.search_impression_share,
    metrics.search_rank_lost_impression_share, metrics.search_exact_match_impression_share,
    metrics.search_top_impression_share, metrics.search_absolute_top_impression_share"""
S["keyword_perf"] = [dict(ad_group_id=str(x.ad_group.id), criterion_id=str(x.ad_group_criterion.criterion_id),
                          text=x.ad_group_criterion.keyword.text, mt=E(x.ad_group_criterion.keyword.match_type),
                          **pb(x.metrics)) for x in run("kw_perf", f"""SELECT ad_group.id, ad_group_criterion.criterion_id,
    ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, {KWMET} FROM keyword_view
    WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["ad_group_perf"] = [dict(ad_group_id=str(x.ad_group.id), **pb(x.metrics)) for x in run("ag_perf", f"""SELECT
    ad_group.id, {KWMET} FROM ad_group WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["ad_perf"] = [dict(ad_id=str(x.ad_group_ad.ad.id), **pb(x.metrics)) for x in run("ad_perf", f"""SELECT
    ad_group_ad.ad.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr FROM ad_group_ad
    WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["device"] = seg_rows("device", "segments.device")
S["slot"] = seg_rows("slot", "segments.slot")
S["day_of_week"] = seg_rows("day_of_week", "segments.day_of_week")
S["hour"] = seg_rows("hour", "segments.hour")
S["network"] = seg_rows("network", "segments.ad_network_type")
S["click_type"] = seg_rows("click_type", "segments.click_type")
S["kw_device"] = [dict(criterion_id=str(x.ad_group_criterion.criterion_id), ad_group_id=str(x.ad_group.id),
                       device=E(x.segments.device), **pb(x.metrics)) for x in run("kw_device", f"""SELECT ad_group.id,
    ad_group_criterion.criterion_id, segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM keyword_view WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["kw_slot"] = [dict(criterion_id=str(x.ad_group_criterion.criterion_id), ad_group_id=str(x.ad_group.id),
                     slot=E(x.segments.slot), **pb(x.metrics)) for x in run("kw_slot", f"""SELECT ad_group.id,
    ad_group_criterion.criterion_id, segments.slot, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM keyword_view WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["conv_by_action"] = [dict(action=x.segments.conversion_action_name, **pb(x.metrics)) for x in run("conv_by_action", f"""SELECT
    segments.conversion_action_name, metrics.all_conversions, metrics.conversions FROM campaign
    WHERE segments.date BETWEEN '{START}' AND '{TODAY}'""")]
S["call_view"] = [pb(x.call_view) for x in run("call_view", """SELECT call_view.start_call_date_time, call_view.call_status,
    call_view.call_duration_seconds, call_view.type, call_view.call_tracking_display_location FROM call_view""")]

# ---------------------------------------------------------------- geo
S["user_location_view"] = [dict(targeting_location=x.user_location_view.targeting_location,
                                most_specific=x.segments.geo_target_most_specific_location, **pb(x.metrics))
                           for x in run("ulv", f"""SELECT user_location_view.targeting_location,
    segments.geo_target_most_specific_location, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM user_location_view WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["location_view"] = [dict(criterion_id=str(x.campaign_criterion.criterion_id), **pb(x.metrics)) for x in run(
    "location_view", f"""SELECT campaign_criterion.criterion_id, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM location_view WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
most = sorted({x["most_specific"] for x in S["user_location_view"] if x["most_specific"]})
S["most_specific_names"] = {}
if most:
    for x in run("most_specific_names", "SELECT geo_target_constant.resource_name, geo_target_constant.canonical_name "
                 "FROM geo_target_constant WHERE geo_target_constant.resource_name IN ("
                 + ",".join(f"'{g}'" for g in most) + ")"):
        S["most_specific_names"][x.geo_target_constant.resource_name] = x.geo_target_constant.canonical_name

# ---------------------------------------------------------------- search terms (own files)
r = run("search_terms", f"""SELECT ad_group.id, search_term_view.search_term, search_term_view.status,
    segments.keyword.info.text, segments.keyword.info.match_type, segments.search_term_match_type,
    metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.all_conversions FROM search_term_view
    WHERE segments.date BETWEEN '{START}' AND '{TODAY}'""")
terms = [{"ad_group_id": str(x.ad_group.id), "search_term": x.search_term_view.search_term,
          "status": E(x.search_term_view.status), "keyword": x.segments.keyword.info.text,
          "keyword_match": E(x.segments.keyword.info.match_type), "query_match": E(x.segments.search_term_match_type),
          "impressions": x.metrics.impressions, "clicks": x.metrics.clicks, "cost": M(x.metrics.cost_micros),
          "all_conversions": x.metrics.all_conversions} for x in r]
OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "search_terms_2026-09-21_to_2026-10-05.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(terms[0]) if terms else ["search_term"])
    w.writeheader()
    w.writerows(sorted(terms, key=lambda t: (-t["impressions"], t["search_term"])))
S["search_terms_rowcount"] = len(terms)
S["search_terms_totals"] = {"impressions": sum(t["impressions"] for t in terms),
                            "clicks": sum(t["clicks"] for t in terms), "cost": round(sum(t["cost"] for t in terms), 2)}

# ---------------------------------------------------------------- change history since the 09-28 audit
r = run("change_event", f"""SELECT change_event.change_date_time, change_event.change_resource_type,
    change_event.resource_change_operation, change_event.client_type, change_event.changed_fields,
    change_event.change_resource_name, change_event.old_resource, change_event.new_resource
    FROM change_event WHERE change_event.change_date_time >= '2026-09-17 00:00:00'
    AND change_event.change_date_time <= '{TODAY} 23:59:59' ORDER BY change_event.change_date_time ASC LIMIT 2000""")
S["change_events"] = [{"t": x.change_event.change_date_time, "type": E(x.change_event.change_resource_type),
                       "op": E(x.change_event.resource_change_operation), "client": E(x.change_event.client_type),
                       "fields": list(x.change_event.changed_fields.paths), "res": x.change_event.change_resource_name,
                       "old": pb(x.change_event.old_resource), "new": pb(x.change_event.new_resource)} for x in r]


# ---------------------------------------------------------------- extra settings checks (run b)
S["recommendation_subscriptions"] = [pb(x.recommendation_subscription) for x in run("rec_subs", """SELECT
    recommendation_subscription.type, recommendation_subscription.status FROM recommendation_subscription""")]
S["campaign_extra"] = [pb(x.campaign) for x in run("campaign_extra", """SELECT campaign.id,
    campaign.dynamic_search_ads_setting.domain_name, campaign.url_expansion_opt_out,
    campaign.local_services_campaign_settings.category_bids FROM campaign""")]
S["landing_page_view"] = [dict(url=x.landing_page_view.unexpanded_final_url, **pb(x.metrics)) for x in run("lpv", f"""SELECT
    landing_page_view.unexpanded_final_url, metrics.impressions, metrics.clicks, metrics.speed_score,
    metrics.mobile_friendly_clicks_percentage FROM landing_page_view WHERE segments.date BETWEEN '{START}' AND '{END}'""")]
S["expanded_landing_page_view"] = [dict(url=x.expanded_landing_page_view.expanded_final_url, **pb(x.metrics)) for x in run("elpv", f"""SELECT
    expanded_landing_page_view.expanded_final_url, metrics.clicks FROM expanded_landing_page_view
    WHERE segments.date BETWEEN '{START}' AND '{END}'""")]

write(SNAP / f"2026-10-05-{LABEL}-snapshot.json", S)

# ---------------------------------------------------------------- aggregate summary (stdout)
print(f"errors: {len(S['errors'])} -> {list(S['errors'])}")
for cmp in S["campaigns"]:
    print("campaign", cmp.get("id"), cmp.get("status"), cmp.get("primary_status"), cmp.get("primary_status_reasons"),
          cmp.get("bidding_strategy_type"), "ceiling", M(int(cmp.get("target_spend", {}).get("cpc_bid_ceiling_micros", 0))))
print("budgets", [(b.get("id"), M(int(b.get("amount_micros", 0))), b.get("status")) for b in S["budgets"]])
print("billing", [(b.get("id"), b.get("status")) for b in S["billing_setups"]])
for w, d in S["windows"].items():
    for m in d["rows"]:
        print(f"{w:20s} impr={m.get('impressions', 0)} clicks={m.get('clicks', 0)} cost=${M(int(m.get('cost_micros', 0)))} "
              f"ctr={m.get('ctr')} is={m.get('search_impression_share')} rank_lost={m.get('search_rank_lost_impression_share')} "
              f"budget_lost={m.get('search_budget_lost_impression_share')} top={m.get('search_top_impression_share')} "
              f"abs_top={m.get('search_absolute_top_impression_share')} click_share={m.get('search_click_share')} "
              f"conv={m.get('conversions', 0)} all_conv={m.get('all_conversions', 0)}")
print("search terms rows", S["search_terms_rowcount"], S["search_terms_totals"])
print("change events", len(S["change_events"]), "since 2026-09-17")
