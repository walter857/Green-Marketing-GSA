#!/usr/bin/env python3
"""2026-09-16 READ-ONLY full account inventory for Apogee Lawns LLC (8164626278)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, client, q, write, E  # noqa: E402

c = client()
out = {}


def section(title, query, render, key, cid=CID):
    print(f"\n=== {title} ===")
    try:
        rows = q(c, query, cid=cid)
    except Exception as exc:  # noqa: BLE001
        msg = f"{type(exc).__name__}: {str(exc)[:400]}"
        print(f"  QUERY FAILED: {msg}")
        out[key] = {"error": msg}
        return []
    recs = [render(r) for r in rows]
    out[key] = recs
    print(f"  rows: {len(recs)}")
    return recs


# ---------------------------------------------------------------- campaigns
camps = section(
    "CAMPAIGNS (all statuses)",
    """
    SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
           campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
           campaign.bidding_strategy_type, campaign.campaign_budget,
           campaign.start_date, campaign.end_date,
           campaign.network_settings.target_google_search,
           campaign.network_settings.target_search_network,
           campaign.network_settings.target_content_network,
           campaign.network_settings.target_partner_search_network,
           campaign.geo_target_type_setting.positive_geo_target_type,
           campaign.geo_target_type_setting.negative_geo_target_type,
           campaign.optimization_score, campaign.tracking_url_template,
           campaign.final_url_suffix
    FROM campaign
    ORDER BY campaign.id
    """,
    lambda r: {
        "id": str(r.campaign.id), "name": r.campaign.name,
        "status": E(r.campaign.status), "serving": E(r.campaign.serving_status),
        "channel": E(r.campaign.advertising_channel_type),
        "sub_type": E(r.campaign.advertising_channel_sub_type),
        "bidding": E(r.campaign.bidding_strategy_type),
        "budget": r.campaign.campaign_budget.split("/")[-1] if r.campaign.campaign_budget else None,
        "start": r.campaign.start_date, "end": r.campaign.end_date,
        "search": r.campaign.network_settings.target_google_search,
        "partners": r.campaign.network_settings.target_search_network,
        "display": r.campaign.network_settings.target_content_network,
        "pos_geo": E(r.campaign.geo_target_type_setting.positive_geo_target_type),
    },
    "campaigns",
)
for x in camps:
    print(f"    {x['id']:>12} {x['status']:>8} {x['serving']:>10} {x['channel']:>14} "
          f"{x['bidding']:>24} {x['name'][:60]}")

# ---------------------------------------------------------------- budgets
buds = section(
    "CAMPAIGN BUDGETS",
    """
    SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
           campaign_budget.status, campaign_budget.delivery_method,
           campaign_budget.explicitly_shared, campaign_budget.reference_count,
           campaign_budget.period
    FROM campaign_budget
    """,
    lambda r: {
        "id": str(r.campaign_budget.id), "name": r.campaign_budget.name,
        "daily": round(r.campaign_budget.amount_micros / 1e6, 2),
        "status": E(r.campaign_budget.status), "refs": r.campaign_budget.reference_count,
        "shared": r.campaign_budget.explicitly_shared,
        "delivery": E(r.campaign_budget.delivery_method),
        "period": E(r.campaign_budget.period),
    },
    "budgets",
)
for x in buds:
    print(f"    {x['id']:>12} ${x['daily']:>8.2f} {x['status']:>8} refs={x['refs']} {x['name'][:50]}")

# ---------------------------------------------------------------- ad groups
ags = section(
    "AD GROUPS",
    """
    SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
           ad_group.campaign, ad_group.cpc_bid_micros
    FROM ad_group
    """,
    lambda r: {
        "id": str(r.ad_group.id), "name": r.ad_group.name, "status": E(r.ad_group.status),
        "type": E(r.ad_group.type_), "campaign": r.ad_group.campaign.split("/")[-1],
        "cpc": round(r.ad_group.cpc_bid_micros / 1e6, 2),
    },
    "ad_groups",
)
for x in ags:
    print(f"    {x['id']:>12} {x['status']:>8} camp={x['campaign']} {x['name'][:50]}")

# ---------------------------------------------------------------- keywords
kws = section(
    "KEYWORDS (positive + negative)",
    """
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.negative,
           ad_group_criterion.status, ad_group_criterion.ad_group
    FROM ad_group_criterion
    WHERE ad_group_criterion.type = KEYWORD
    """,
    lambda r: {
        "id": str(r.ad_group_criterion.criterion_id),
        "text": r.ad_group_criterion.keyword.text,
        "match": E(r.ad_group_criterion.keyword.match_type),
        "negative": r.ad_group_criterion.negative,
        "status": E(r.ad_group_criterion.status),
        "ad_group": r.ad_group_criterion.ad_group.split("/")[-1],
    },
    "keywords",
)
for x in kws[:40]:
    print(f"    {'NEG' if x['negative'] else 'POS'} {x['match']:>6} {x['status']:>8} {x['text'][:60]}")

# ---------------------------------------------------------------- ads
section(
    "ADS",
    """
    SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
           ad_group_ad.ad.final_urls, ad_group_ad.policy_summary.approval_status,
           ad_group_ad.ad_group
    FROM ad_group_ad
    """,
    lambda r: {
        "id": str(r.ad_group_ad.ad.id), "type": E(r.ad_group_ad.ad.type_),
        "status": E(r.ad_group_ad.status),
        "urls": list(r.ad_group_ad.ad.final_urls),
        "approval": E(r.ad_group_ad.policy_summary.approval_status),
        "ad_group": r.ad_group_ad.ad_group.split("/")[-1],
    },
    "ads",
)

# ---------------------------------------------------------------- conversion actions
ca = section(
    "CONVERSION ACTIONS (all)",
    """
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.type, conversion_action.category, conversion_action.origin,
           conversion_action.primary_for_goal, conversion_action.counting_type,
           conversion_action.click_through_lookback_window_days,
           conversion_action.view_through_lookback_window_days,
           conversion_action.attribution_model_settings.attribution_model,
           conversion_action.attribution_model_settings.data_driven_model_status,
           conversion_action.value_settings.default_value,
           conversion_action.value_settings.always_use_default_value,
           conversion_action.phone_call_duration_seconds,
           conversion_action.include_in_conversions_metric,
           conversion_action.owner_customer, conversion_action.app_id,
           conversion_action.tag_snippets
    FROM conversion_action
    """,
    lambda r: {
        "id": str(r.conversion_action.id), "name": r.conversion_action.name,
        "status": E(r.conversion_action.status), "type": E(r.conversion_action.type_),
        "category": E(r.conversion_action.category),
        "origin": E(r.conversion_action.origin),
        "primary_for_goal": r.conversion_action.primary_for_goal,
        "counting": E(r.conversion_action.counting_type),
        "click_window": r.conversion_action.click_through_lookback_window_days,
        "view_window": r.conversion_action.view_through_lookback_window_days,
        "attribution": E(r.conversion_action.attribution_model_settings.attribution_model),
        "ddm_status": E(r.conversion_action.attribution_model_settings.data_driven_model_status),
        "default_value": r.conversion_action.value_settings.default_value,
        "always_default": r.conversion_action.value_settings.always_use_default_value,
        "phone_duration_s": r.conversion_action.phone_call_duration_seconds,
        "in_conv_metric": r.conversion_action.include_in_conversions_metric,
        "owner": (r.conversion_action.owner_customer or "").split("/")[-1],
        "labels": [
            {"type": E(t.type_), "page_format": E(t.page_format),
             "global_site_tag_present": bool(t.global_site_tag),
             "event_snippet_present": bool(t.event_snippet)}
            for t in r.conversion_action.tag_snippets
        ],
    },
    "conversion_actions",
)
for x in ca:
    print(f"    {x['id']:>12} {x['status']:>8} primary={int(x['primary_for_goal'])} "
          f"{x['type']:>22} {x['category']:>18} dur={x['phone_duration_s']}s {x['name'][:45]}")

# ---------------------------------------------------------------- conversion goals
section(
    "CUSTOMER CONVERSION GOALS (account default)",
    """
    SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
           customer_conversion_goal.biddable
    FROM customer_conversion_goal
    """,
    lambda r: {
        "category": E(r.customer_conversion_goal.category),
        "origin": E(r.customer_conversion_goal.origin),
        "biddable": r.customer_conversion_goal.biddable,
    },
    "customer_conversion_goals",
)
for x in out.get("customer_conversion_goals", []) or []:
    if isinstance(x, dict) and x.get("biddable"):
        print(f"    BIDDABLE  {x['category']:>24} / {x['origin']}")

section(
    "CAMPAIGN CONVERSION GOALS",
    """
    SELECT campaign_conversion_goal.campaign, campaign_conversion_goal.category,
           campaign_conversion_goal.origin, campaign_conversion_goal.biddable
    FROM campaign_conversion_goal
    """,
    lambda r: {
        "campaign": r.campaign_conversion_goal.campaign.split("/")[-1],
        "category": E(r.campaign_conversion_goal.category),
        "origin": E(r.campaign_conversion_goal.origin),
        "biddable": r.campaign_conversion_goal.biddable,
    },
    "campaign_conversion_goals",
)

section(
    "CONVERSION GOAL CAMPAIGN CONFIG",
    """
    SELECT conversion_goal_campaign_config.campaign,
           conversion_goal_campaign_config.goal_config_level,
           conversion_goal_campaign_config.custom_conversion_goal
    FROM conversion_goal_campaign_config
    """,
    lambda r: {
        "campaign": r.conversion_goal_campaign_config.campaign.split("/")[-1],
        "level": E(r.conversion_goal_campaign_config.goal_config_level),
        "custom_goal": r.conversion_goal_campaign_config.custom_conversion_goal,
    },
    "conversion_goal_campaign_config",
)

section(
    "CUSTOM CONVERSION GOALS",
    """
    SELECT custom_conversion_goal.id, custom_conversion_goal.name,
           custom_conversion_goal.conversion_actions, custom_conversion_goal.status
    FROM custom_conversion_goal
    """,
    lambda r: {
        "id": str(r.custom_conversion_goal.id), "name": r.custom_conversion_goal.name,
        "actions": [a.split("/")[-1] for a in r.custom_conversion_goal.conversion_actions],
        "status": E(r.custom_conversion_goal.status),
    },
    "custom_conversion_goals",
)

# ---------------------------------------------------------------- assets
section(
    "CUSTOMER ASSETS (account-level)",
    """
    SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status,
           asset.id, asset.name, asset.type, asset.call_asset.phone_number,
           asset.call_asset.country_code, asset.call_asset.call_conversion_action,
           asset.call_asset.call_conversion_reporting_state,
           asset.sitelink_asset.link_text, asset.final_urls
    FROM customer_asset
    """,
    lambda r: {
        "asset_id": str(r.asset.id), "name": r.asset.name, "type": E(r.asset.type_),
        "field": E(r.customer_asset.field_type), "status": E(r.customer_asset.status),
        "phone": r.asset.call_asset.phone_number,
        "call_conv_action": (r.asset.call_asset.call_conversion_action or "").split("/")[-1],
        "call_conv_state": E(r.asset.call_asset.call_conversion_reporting_state),
        "sitelink_text": r.asset.sitelink_asset.link_text,
        "final_urls": list(r.asset.final_urls),
    },
    "customer_assets",
)
for x in out.get("customer_assets", []) or []:
    if isinstance(x, dict):
        print(f"    {x['asset_id']:>14} {x['field']:>18} {x['status']:>8} "
              f"{x['phone'] or x['sitelink_text'] or x['name'] or ''}")

section(
    "ALL ASSETS",
    "SELECT asset.id, asset.name, asset.type, asset.source FROM asset",
    lambda r: {"id": str(r.asset.id), "name": r.asset.name,
               "type": E(r.asset.type_), "source": E(r.asset.source)},
    "assets",
)

# ---------------------------------------------------------------- negatives / shared sets
section(
    "SHARED SETS",
    """
    SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
           shared_set.member_count, shared_set.reference_count
    FROM shared_set
    """,
    lambda r: {"id": str(r.shared_set.id), "name": r.shared_set.name,
               "type": E(r.shared_set.type_), "status": E(r.shared_set.status),
               "members": r.shared_set.member_count, "refs": r.shared_set.reference_count},
    "shared_sets",
)

section(
    "ACCOUNT-LEVEL NEGATIVE CRITERIA",
    """
    SELECT customer_negative_criterion.id, customer_negative_criterion.type,
           customer_negative_criterion.keyword.text,
           customer_negative_criterion.keyword.match_type,
           customer_negative_criterion.placement.url
    FROM customer_negative_criterion
    """,
    lambda r: {"id": str(r.customer_negative_criterion.id),
               "type": E(r.customer_negative_criterion.type_),
               "text": r.customer_negative_criterion.keyword.text,
               "match": E(r.customer_negative_criterion.keyword.match_type)},
    "account_negatives",
)

# ---------------------------------------------------------------- links / billing
section(
    "PRODUCT LINKS (GA4, Merchant, partners)",
    """
    SELECT product_link.product_link_id, product_link.type,
           product_link.google_ads.customer,
           product_link.data_partner.data_partner_id,
           product_link.merchant_center.merchant_center_id
    FROM product_link
    """,
    lambda r: {"id": str(r.product_link.product_link_id), "type": E(r.product_link.type_)},
    "product_links",
)

section(
    "BILLING SETUP",
    """
    SELECT billing_setup.id, billing_setup.status, billing_setup.payments_account,
           billing_setup.payments_account_info.payments_account_name,
           billing_setup.payments_account_info.payments_profile_name,
           billing_setup.start_date_time, billing_setup.end_date_time
    FROM billing_setup
    """,
    lambda r: {"id": str(r.billing_setup.id), "status": E(r.billing_setup.status),
               "start": r.billing_setup.start_date_time,
               "end": r.billing_setup.end_date_time},
    "billing_setup",
)
for x in out.get("billing_setup", []) or []:
    if isinstance(x, dict):
        print(f"    {x['id']} {x['status']} start={x['start']} end={x['end']}")

section(
    "ACCOUNT BUDGETS",
    """
    SELECT account_budget.id, account_budget.status, account_budget.name,
           account_budget.approved_spending_limit_micros,
           account_budget.amount_served_micros, account_budget.total_adjustments_micros
    FROM account_budget
    """,
    lambda r: {"id": str(r.account_budget.id), "status": E(r.account_budget.status),
               "name": r.account_budget.name,
               "served": round(r.account_budget.amount_served_micros / 1e6, 2)},
    "account_budgets",
)

section(
    "USER ACCESS",
    """
    SELECT customer_user_access.user_id, customer_user_access.access_role,
           customer_user_access.email_address, customer_user_access.access_creation_date_time
    FROM customer_user_access
    """,
    lambda r: {"role": E(r.customer_user_access.access_role),
               "created": r.customer_user_access.access_creation_date_time},
    "user_access",
)
for x in out.get("user_access", []) or []:
    if isinstance(x, dict):
        print(f"    role={x['role']} created={x['created']}")

section(
    "RECOMMENDATION SUBSCRIPTIONS (auto-apply)",
    """
    SELECT recommendation_subscription.type, recommendation_subscription.status,
           recommendation_subscription.apply_automatically
    FROM recommendation_subscription
    """,
    lambda r: {"type": E(r.recommendation_subscription.type_),
               "status": E(r.recommendation_subscription.status),
               "auto": r.recommendation_subscription.apply_automatically},
    "recommendation_subscriptions",
)
for x in out.get("recommendation_subscriptions", []) or []:
    if isinstance(x, dict):
        print(f"    {x['type']:>40} {x['status']:>10} auto={x['auto']}")

# ---------------------------------------------------------------- lifetime spend
print("\n=== LIFETIME ACCOUNT METRICS ===")
try:
    for r in q(c, """
        SELECT metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions, metrics.all_conversions
        FROM customer
        WHERE segments.date BETWEEN '2015-01-01' AND '2026-09-16'
    """):
        lifetime = {
            "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": round(r.metrics.cost_micros / 1e6, 2),
            "conversions": round(r.metrics.conversions, 2),
            "all_conversions": round(r.metrics.all_conversions, 2),
        }
        out["lifetime"] = lifetime
        print(f"    {lifetime}")
        break
    else:
        out["lifetime"] = {"note": "no rows - zero lifetime activity"}
        print("    no rows returned -> zero lifetime activity")
except Exception as exc:  # noqa: BLE001
    print(f"    FAILED: {type(exc).__name__}: {str(exc)[:200]}")

write(EVID / "2026-09-16-inventory.json", out)
print("\nINVENTORY COMPLETE")
