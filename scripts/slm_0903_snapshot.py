#!/usr/bin/env python3
"""Phase A before-snapshot for Softwind Landscape & Masonry (2429758629).

SELECT-only. Never constructs an operation, never calls a mutate service.
Writes clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers/
01-before-snapshot.json

Known API constraints applied up front (see memory gaql-field-gotchas):
  - Auction Insights metrics are PERMISSION_DENIED on a Basic developer token.
  - change_event is capped at 30 days and needs BOTH bounds.
  - campaign.start_date_time / end_date_time (not start_date / end_date).
  - metrics.conversions is prohibited FROM conversion_action; segment a
    campaign query on segments.conversion_action instead.
  - ad_group_criterion.criterion_id is NOT unique; key on (ad_group_id, id).
  - REMOVED rows are returned unless filtered; the filter is recorded.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
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


def m(v):
    return None if v is None else round(v / 1_000_000, 6)


class Reader:
    def __init__(self):
        load_dotenv_if_available(ROOT / ".env")
        self.client = load_google_ads_client()
        self.svc = self.client.get_service("GoogleAdsService")
        self.errors = []
        self.ok = []

    def rows(self, name, query):
        try:
            out = list(self.svc.search(customer_id=CID, query=query))
            self.ok.append({"query": name, "rows": len(out)})
            print("  ok  %-38s %5d rows" % (name, len(out)))
            return out
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            for marker in ("message: ", "FaultMessage: "):
                if marker in msg:
                    msg = msg.split(marker, 1)[1][:400]
                    break
            self.errors.append({"query": name, "error": msg[:400]})
            print("  !!  %-38s %s" % (name, msg[:160]), file=sys.stderr)
            return []


def main() -> int:
    r = Reader()
    now_local = datetime.now(TZ)
    out = {
        "customer_id": CID,
        "snapshot_taken_account_local": now_local.isoformat(),
        "read_scope": "SELECT-only; authorizes no mutation",
        "removed_filter_policy": "status != 'REMOVED' applied and recorded per section",
    }

    # ---------------- 1. CUSTOMER ----------------
    for row in r.rows("customer", """
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               customer.time_zone, customer.status, customer.manager,
               customer.test_account, customer.auto_tagging_enabled,
               customer.tracking_url_template, customer.final_url_suffix,
               customer.has_partners_badge, customer.optimization_score,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
               customer.conversion_tracking_setting.conversion_tracking_status,
               customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
               customer.conversion_tracking_setting.google_ads_conversion_customer
        FROM customer LIMIT 1"""):
        c = row.customer
        cts = c.conversion_tracking_setting
        out["customer"] = {
            "id": str(c.id), "descriptive_name": c.descriptive_name,
            "currency": c.currency_code, "time_zone": c.time_zone,
            "status": enum_name(c.status), "manager": c.manager,
            "test_account": c.test_account,
            "auto_tagging_enabled": c.auto_tagging_enabled,
            "tracking_url_template": c.tracking_url_template or None,
            "final_url_suffix": c.final_url_suffix or None,
            "optimization_score": c.optimization_score,
            "conversion_tracking_id": str(cts.conversion_tracking_id) or None,
            "cross_account_conversion_tracking_id":
                str(cts.cross_account_conversion_tracking_id) or None,
            "conversion_tracking_status": enum_name(cts.conversion_tracking_status),
            "enhanced_conversions_for_leads_enabled":
                cts.enhanced_conversions_for_leads_enabled,
            "google_ads_conversion_customer": cts.google_ads_conversion_customer,
        }

    # ---------------- 2. CAMPAIGNS ----------------
    camps = {}
    for row in r.rows("campaign", """
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
               campaign.start_date_time, campaign.end_date_time,
               campaign.bidding_strategy_type, campaign.bidding_strategy,
               campaign.campaign_budget, campaign.optimization_score,
               campaign.tracking_url_template, campaign.final_url_suffix,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign.geo_target_type_setting.negative_geo_target_type,
               campaign.target_spend.cpc_bid_ceiling_micros,
               campaign.target_cpa.target_cpa_micros,
               campaign.target_roas.target_roas,
               campaign.maximize_conversions.target_cpa_micros,
               campaign.manual_cpc.enhanced_cpc_enabled,
               campaign.ai_max_setting.enable_ai_max,
               campaign.payment_mode, campaign.experiment_type
        FROM campaign WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name"""):
        c = row.campaign
        camps[str(c.id)] = {
            "id": str(c.id), "name": c.name, "status": enum_name(c.status),
            "serving_status": enum_name(c.serving_status),
            "channel": enum_name(c.advertising_channel_type),
            "sub_type": enum_name(c.advertising_channel_sub_type),
            "start_date_time": c.start_date_time or None,
            "end_date_time": c.end_date_time or None,
            "bidding_strategy_type": enum_name(c.bidding_strategy_type),
            "portfolio_bidding_strategy": c.bidding_strategy or None,
            "campaign_budget_resource": c.campaign_budget,
            "tracking_url_template": c.tracking_url_template or None,
            "final_url_suffix": c.final_url_suffix or None,
            "network": {
                "google_search": c.network_settings.target_google_search,
                "search_partners": c.network_settings.target_search_network,
                "display": c.network_settings.target_content_network,
                "partner_search": c.network_settings.target_partner_search_network,
            },
            "geo_target_type": {
                "positive": enum_name(c.geo_target_type_setting.positive_geo_target_type),
                "negative": enum_name(c.geo_target_type_setting.negative_geo_target_type),
            },
            "target_spend_cpc_bid_ceiling": m(c.target_spend.cpc_bid_ceiling_micros) or None,
            "target_cpa": m(c.target_cpa.target_cpa_micros) or None,
            "maximize_conversions_target_cpa": m(c.maximize_conversions.target_cpa_micros) or None,
            "target_roas": c.target_roas.target_roas or None,
            "enhanced_cpc": c.manual_cpc.enhanced_cpc_enabled,
            "ai_max": c.ai_max_setting.enable_ai_max,
            "payment_mode": enum_name(c.payment_mode),
            "experiment_type": enum_name(c.experiment_type),
        }
    out["campaigns"] = camps
    out["campaigns_filter"] = "campaign.status != 'REMOVED'"

    # ---------------- 3. BUDGETS ----------------
    buds = {}
    for row in r.rows("campaign_budget", """
        SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
               campaign_budget.total_amount_micros, campaign_budget.delivery_method,
               campaign_budget.explicitly_shared, campaign_budget.reference_count,
               campaign_budget.status, campaign_budget.period,
               campaign_budget.recommended_budget_amount_micros
        FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'"""):
        b = row.campaign_budget
        buds[str(b.id)] = {
            "id": str(b.id), "name": b.name,
            "amount": m(b.amount_micros), "total_amount": m(b.total_amount_micros) or None,
            "delivery_method": enum_name(b.delivery_method),
            "explicitly_shared": b.explicitly_shared,
            "reference_count": b.reference_count,
            "status": enum_name(b.status), "period": enum_name(b.period),
            "recommended_amount": m(b.recommended_budget_amount_micros) or None,
        }
    out["campaign_budgets"] = buds

    # ---------------- 4. AD GROUPS ----------------
    ags = {}
    for row in r.rows("ad_group", """
        SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
               ad_group.campaign, ad_group.cpc_bid_micros,
               ad_group.target_cpa_micros, ad_group.tracking_url_template,
               ad_group.final_url_suffix, ad_group.effective_target_cpa_micros,
               campaign.id, campaign.name
        FROM ad_group WHERE ad_group.status != 'REMOVED' ORDER BY campaign.name, ad_group.name"""):
        a = row.ad_group
        ags[str(a.id)] = {
            "id": str(a.id), "name": a.name, "status": enum_name(a.status),
            "type": enum_name(a.type_), "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name,
            "cpc_bid": m(a.cpc_bid_micros) or None,
            "target_cpa": m(a.target_cpa_micros) or None,
            "tracking_url_template": a.tracking_url_template or None,
            "final_url_suffix": a.final_url_suffix or None,
        }
    out["ad_groups"] = ags
    out["ad_groups_filter"] = "ad_group.status != 'REMOVED'"

    # ---------------- 5. KEYWORDS ----------------
    kws = []
    for row in r.rows("keywords", """
        SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.negative, ad_group_criterion.cpc_bid_micros,
               ad_group_criterion.effective_cpc_bid_micros,
               ad_group_criterion.quality_info.quality_score,
               ad_group_criterion.quality_info.creative_quality_score,
               ad_group_criterion.quality_info.post_click_quality_score,
               ad_group_criterion.quality_info.search_predicted_ctr,
               ad_group_criterion.final_urls, ad_group_criterion.system_serving_status,
               ad_group_criterion.approval_status,
               ad_group.id, ad_group.name, campaign.id, campaign.name
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = 'KEYWORD'
          AND ad_group_criterion.status != 'REMOVED'"""):
        k = row.ad_group_criterion
        q = k.quality_info
        kws.append({
            "criterion_id": str(k.criterion_id),
            "ad_group_id": str(row.ad_group.id), "ad_group_name": row.ad_group.name,
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "text": k.keyword.text, "match_type": enum_name(k.keyword.match_type),
            "status": enum_name(k.status), "negative": k.negative,
            "cpc_bid": m(k.cpc_bid_micros) or None,
            "effective_cpc_bid": m(k.effective_cpc_bid_micros) or None,
            "quality_score": q.quality_score or None,
            "ad_relevance": enum_name(q.creative_quality_score),
            "landing_page_exp": enum_name(q.post_click_quality_score),
            "expected_ctr": enum_name(q.search_predicted_ctr),
            "final_urls": list(k.final_urls),
            "system_serving_status": enum_name(k.system_serving_status),
            "approval_status": enum_name(k.approval_status),
        })
    out["keywords"] = kws
    out["keywords_filter"] = "type = KEYWORD and status != REMOVED (includes ad-group negatives)"

    # ---------------- 6. CAMPAIGN CRITERIA ----------------
    crits = []
    for row in r.rows("campaign_criterion", """
        SELECT campaign_criterion.criterion_id, campaign_criterion.type,
               campaign_criterion.negative, campaign_criterion.status,
               campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
               campaign_criterion.location.geo_target_constant,
               campaign_criterion.proximity.radius,
               campaign_criterion.proximity.radius_units,
               campaign_criterion.proximity.geo_point.latitude_in_micro_degrees,
               campaign_criterion.proximity.geo_point.longitude_in_micro_degrees,
               campaign_criterion.proximity.address.city_name,
               campaign_criterion.proximity.address.postal_code,
               campaign_criterion.language.language_constant,
               campaign_criterion.ad_schedule.day_of_week,
               campaign_criterion.ad_schedule.start_hour,
               campaign_criterion.ad_schedule.end_hour,
               campaign_criterion.device.type,
               campaign_criterion.bid_modifier,
               campaign_criterion.ip_block.ip_address,
               campaign.id, campaign.name
        FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'"""):
        cc = row.campaign_criterion
        t = enum_name(cc.type_)
        e = {
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "criterion_id": str(cc.criterion_id), "type": t,
            "negative": cc.negative, "status": enum_name(cc.status),
            "bid_modifier": cc.bid_modifier or None,
        }
        if t == "KEYWORD":
            e["keyword_text"] = cc.keyword.text
            e["match_type"] = enum_name(cc.keyword.match_type)
        elif t == "LOCATION":
            e["geo_target_constant"] = cc.location.geo_target_constant
        elif t == "PROXIMITY":
            e["radius"] = cc.proximity.radius
            e["radius_units"] = enum_name(cc.proximity.radius_units)
            e["lat"] = cc.proximity.geo_point.latitude_in_micro_degrees / 1e6
            e["lon"] = cc.proximity.geo_point.longitude_in_micro_degrees / 1e6
            e["city"] = cc.proximity.address.city_name
            e["postal_code"] = cc.proximity.address.postal_code
        elif t == "LANGUAGE":
            e["language_constant"] = cc.language.language_constant
        elif t == "AD_SCHEDULE":
            e["day"] = enum_name(cc.ad_schedule.day_of_week)
            e["start_hour"] = cc.ad_schedule.start_hour
            e["end_hour"] = cc.ad_schedule.end_hour
        elif t == "DEVICE":
            e["device"] = enum_name(cc.device.type_)
        elif t == "IP_BLOCK":
            e["ip"] = cc.ip_block.ip_address
        crits.append(e)
    out["campaign_criteria"] = crits

    # ---------------- 7. SHARED SETS ----------------
    out["shared_sets"] = [{
        "id": str(x.shared_set.id), "name": x.shared_set.name,
        "type": enum_name(x.shared_set.type_), "status": enum_name(x.shared_set.status),
        "member_count": x.shared_set.member_count,
    } for x in r.rows("shared_set", """
        SELECT shared_set.id, shared_set.name, shared_set.type,
               shared_set.status, shared_set.member_count
        FROM shared_set WHERE shared_set.status != 'REMOVED'""")]

    out["campaign_shared_sets"] = [{
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "shared_set": x.campaign_shared_set.shared_set,
        "status": enum_name(x.campaign_shared_set.status),
    } for x in r.rows("campaign_shared_set", """
        SELECT campaign_shared_set.shared_set, campaign_shared_set.status,
               campaign.id, campaign.name
        FROM campaign_shared_set WHERE campaign_shared_set.status != 'REMOVED'""")]

    out["shared_criteria"] = [{
        "shared_set": x.shared_criterion.shared_set,
        "criterion_id": str(x.shared_criterion.criterion_id),
        "type": enum_name(x.shared_criterion.type_),
        "keyword_text": x.shared_criterion.keyword.text,
        "match_type": enum_name(x.shared_criterion.keyword.match_type),
    } for x in r.rows("shared_criterion", """
        SELECT shared_criterion.shared_set, shared_criterion.criterion_id,
               shared_criterion.type, shared_criterion.keyword.text,
               shared_criterion.keyword.match_type
        FROM shared_criterion""")]

    out["customer_negative_criteria"] = [{
        "criterion_id": str(x.customer_negative_criterion.id),
        "type": enum_name(x.customer_negative_criterion.type_),
        "negative_keyword_list":
            x.customer_negative_criterion.negative_keyword_list.shared_set,
    } for x in r.rows("customer_negative_criterion", """
        SELECT customer_negative_criterion.id, customer_negative_criterion.type,
               customer_negative_criterion.negative_keyword_list.shared_set
        FROM customer_negative_criterion""")]

    # ---------------- 8. ADS ----------------
    ads = []
    for row in r.rows("ad_group_ad", """
        SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
               ad_group_ad.policy_summary.approval_status,
               ad_group_ad.policy_summary.review_status,
               ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
               ad_group_ad.ad.tracking_url_template,
               ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions,
               ad_group_ad.ad.responsive_search_ad.path1,
               ad_group_ad.ad.responsive_search_ad.path2,
               ad_group_ad.ad_strength,
               ad_group.id, ad_group.name, campaign.id, campaign.name
        FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        a = row.ad_group_ad
        rsa = a.ad.responsive_search_ad
        ads.append({
            "ad_id": str(a.ad.id), "type": enum_name(a.ad.type_),
            "status": enum_name(a.status),
            "approval_status": enum_name(a.policy_summary.approval_status),
            "review_status": enum_name(a.policy_summary.review_status),
            "ad_strength": enum_name(a.ad_strength),
            "ad_group_id": str(row.ad_group.id), "ad_group_name": row.ad_group.name,
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "final_urls": list(a.ad.final_urls),
            "tracking_url_template": a.ad.tracking_url_template or None,
            "path1": rsa.path1 or None, "path2": rsa.path2 or None,
            "headlines": [{"text": h.text, "pinned": enum_name(h.pinned_field)}
                          for h in rsa.headlines],
            "descriptions": [{"text": d.text, "pinned": enum_name(d.pinned_field)}
                             for d in rsa.descriptions],
        })
    out["ads"] = ads

    # ---------------- 9. CONVERSION ACTIONS ----------------
    convs = []
    for row in r.rows("conversion_action", """
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.type, conversion_action.category,
               conversion_action.origin, conversion_action.primary_for_goal,
               conversion_action.counting_type,
               conversion_action.click_through_lookback_window_days,
               conversion_action.view_through_lookback_window_days,
               conversion_action.attribution_model_settings.attribution_model,
               conversion_action.attribution_model_settings.data_driven_model_status,
               conversion_action.value_settings.default_value,
               conversion_action.value_settings.always_use_default_value,
               conversion_action.phone_call_duration_seconds,
               conversion_action.include_in_conversions_metric,
               conversion_action.app_id, conversion_action.owner_customer,
               conversion_action.tag_snippets
        FROM conversion_action WHERE conversion_action.status != 'REMOVED'"""):
        ca = row.conversion_action
        convs.append({
            "id": str(ca.id), "name": ca.name, "status": enum_name(ca.status),
            "type": enum_name(ca.type_), "category": enum_name(ca.category),
            "origin": enum_name(ca.origin),
            "primary_for_goal": ca.primary_for_goal,
            "counting_type": enum_name(ca.counting_type),
            "click_lookback_days": ca.click_through_lookback_window_days,
            "view_lookback_days": ca.view_through_lookback_window_days,
            "attribution_model":
                enum_name(ca.attribution_model_settings.attribution_model),
            "data_driven_status":
                enum_name(ca.attribution_model_settings.data_driven_model_status),
            "default_value": ca.value_settings.default_value,
            "always_use_default_value": ca.value_settings.always_use_default_value,
            "phone_call_duration_seconds": ca.phone_call_duration_seconds or None,
            "include_in_conversions_metric": ca.include_in_conversions_metric,
            "owner_customer": ca.owner_customer or None,
        })
    out["conversion_actions"] = convs

    # ---------------- 10. GOALS ----------------
    out["conversion_goal_campaign_config"] = [{
        "campaign": x.conversion_goal_campaign_config.campaign,
        "goal_setting": enum_name(x.conversion_goal_campaign_config.goal_config_level),
        "custom_goal": x.conversion_goal_campaign_config.custom_conversion_goal or None,
    } for x in r.rows("conversion_goal_campaign_config", """
        SELECT conversion_goal_campaign_config.campaign,
               conversion_goal_campaign_config.goal_config_level,
               conversion_goal_campaign_config.custom_conversion_goal
        FROM conversion_goal_campaign_config""")]

    out["customer_conversion_goals"] = [{
        "category": enum_name(x.customer_conversion_goal.category),
        "origin": enum_name(x.customer_conversion_goal.origin),
        "biddable": x.customer_conversion_goal.biddable,
    } for x in r.rows("customer_conversion_goal", """
        SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
               customer_conversion_goal.biddable FROM customer_conversion_goal""")]

    out["campaign_conversion_goals"] = [{
        "campaign": x.campaign_conversion_goal.campaign,
        "category": enum_name(x.campaign_conversion_goal.category),
        "origin": enum_name(x.campaign_conversion_goal.origin),
        "biddable": x.campaign_conversion_goal.biddable,
    } for x in r.rows("campaign_conversion_goal", """
        SELECT campaign_conversion_goal.campaign, campaign_conversion_goal.category,
               campaign_conversion_goal.origin, campaign_conversion_goal.biddable
        FROM campaign_conversion_goal""")]

    out["custom_conversion_goals"] = [{
        "id": str(x.custom_conversion_goal.id),
        "name": x.custom_conversion_goal.name,
        "status": enum_name(x.custom_conversion_goal.status),
        "actions": list(x.custom_conversion_goal.conversion_actions),
    } for x in r.rows("custom_conversion_goal", """
        SELECT custom_conversion_goal.id, custom_conversion_goal.name,
               custom_conversion_goal.status, custom_conversion_goal.conversion_actions
        FROM custom_conversion_goal""")]

    # ---------------- 11. ASSETS ----------------
    out["campaign_assets"] = [{
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "asset_id": str(x.asset.id), "asset_name": x.asset.name or None,
        "field_type": enum_name(x.campaign_asset.field_type),
        "status": enum_name(x.campaign_asset.status),
        "asset_type": enum_name(x.asset.type_),
        "call_phone": x.asset.call_asset.phone_number or None,
        "call_country": x.asset.call_asset.country_code or None,
        "sitelink_text": x.asset.sitelink_asset.link_text or None,
        "sitelink_urls": list(x.asset.final_urls),
        "callout_text": x.asset.callout_asset.callout_text or None,
        "snippet_header": x.asset.structured_snippet_asset.header or None,
        "snippet_values": list(x.asset.structured_snippet_asset.values),
        "text": x.asset.text_asset.text or None,
    } for x in r.rows("campaign_asset", """
        SELECT campaign_asset.field_type, campaign_asset.status, campaign.id, campaign.name,
               asset.id, asset.name, asset.type, asset.final_urls,
               asset.call_asset.phone_number, asset.call_asset.country_code,
               asset.sitelink_asset.link_text, asset.callout_asset.callout_text,
               asset.structured_snippet_asset.header,
               asset.structured_snippet_asset.values, asset.text_asset.text
        FROM campaign_asset WHERE campaign_asset.status != 'REMOVED'""")]

    out["customer_assets"] = [{
        "asset_id": str(x.asset.id), "asset_name": x.asset.name or None,
        "field_type": enum_name(x.customer_asset.field_type),
        "status": enum_name(x.customer_asset.status),
        "asset_type": enum_name(x.asset.type_),
        "call_phone": x.asset.call_asset.phone_number or None,
        "sitelink_text": x.asset.sitelink_asset.link_text or None,
        "callout_text": x.asset.callout_asset.callout_text or None,
        "final_urls": list(x.asset.final_urls),
        "text": x.asset.text_asset.text or None,
    } for x in r.rows("customer_asset", """
        SELECT customer_asset.field_type, customer_asset.status,
               asset.id, asset.name, asset.type, asset.final_urls,
               asset.call_asset.phone_number, asset.sitelink_asset.link_text,
               asset.callout_asset.callout_text, asset.text_asset.text
        FROM customer_asset WHERE customer_asset.status != 'REMOVED'""")]

    out["ad_group_assets"] = [{
        "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
        "asset_id": str(x.asset.id),
        "field_type": enum_name(x.ad_group_asset.field_type),
        "status": enum_name(x.ad_group_asset.status),
    } for x in r.rows("ad_group_asset", """
        SELECT ad_group_asset.field_type, ad_group_asset.status,
               ad_group.id, ad_group.name, asset.id
        FROM ad_group_asset WHERE ad_group_asset.status != 'REMOVED'""")]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out["read_log"] = {"ok": r.ok, "errors": r.errors}
    path = OUTDIR / "01-before-snapshot.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("\nwrote %s" % path.relative_to(ROOT))
    print("errors: %d" % len(r.errors))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
