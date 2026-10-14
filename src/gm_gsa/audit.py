"""Read-only Google Ads account audit.

Every read goes through ``service_discovery.run_read_only_query``, which refuses
anything that is not a GAQL SELECT. Nothing in this module mutates an account.

Each query is isolated: one query that fails is recorded in ``read_errors`` and
skipped, so a single unsupported field never turns into a silent gap or a dead
audit run.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Any, Iterable

from .google_ads import enum_name
from .service_discovery import DiscoveryError, run_read_only_query

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
LONG_DIGITS_RE = re.compile(r"\d[\d\s().-]{6,}\d")


def scrub_text(value: Any) -> str:
    """Strip anything that could carry lead PII out of free text."""

    text = str(value or "")
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    return LONG_DIGITS_RE.sub("[REDACTED_NUMBER]", text)


@dataclass(frozen=True)
class DateWindow:
    label: str
    start: str
    end: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def audit_windows(as_of: date) -> list[DateWindow]:
    """Last 30, the preceding 30, and last 90 days, all ending yesterday."""

    end = as_of - timedelta(days=1)

    def window(label: str, days_back_start: int, days_back_end: int) -> DateWindow:
        return DateWindow(
            label,
            (end - timedelta(days=days_back_start)).isoformat(),
            (end - timedelta(days=days_back_end)).isoformat(),
        )

    return [
        window("last_30", 29, 0),
        window("previous_30", 59, 30),
        window("last_90", 89, 0),
    ]


def _opt(message: Any, field: str) -> Any:
    """Return an optional proto field, or None when the API did not set it."""

    try:
        if field in message:
            return getattr(message, field)
        return None
    except (TypeError, ValueError):
        return getattr(message, field, None)


def _micros(value: Any) -> float | None:
    return None if value is None else float(value) / 1_000_000


def metrics_dict(metrics: Any) -> dict[str, Any]:
    return {
        "cost": _micros(getattr(metrics, "cost_micros", 0)),
        "impressions": int(getattr(metrics, "impressions", 0)),
        "clicks": int(getattr(metrics, "clicks", 0)),
        "ctr": float(getattr(metrics, "ctr", 0.0)),
        "average_cpc": _micros(getattr(metrics, "average_cpc", 0)),
        "conversions": float(getattr(metrics, "conversions", 0.0)),
        "all_conversions": float(getattr(metrics, "all_conversions", 0.0)),
        "conversion_rate": float(getattr(metrics, "conversions_from_interactions_rate", 0.0)),
        "cost_per_conversion": _micros(getattr(metrics, "cost_per_conversion", 0)),
        "cost_per_all_conversions": _micros(getattr(metrics, "cost_per_all_conversions", 0)),
        "conversions_value": float(getattr(metrics, "conversions_value", 0.0)),
        "all_conversions_value": float(getattr(metrics, "all_conversions_value", 0.0)),
        "search_impression_share": _opt(metrics, "search_impression_share"),
        "search_budget_lost_impression_share": _opt(
            metrics, "search_budget_lost_impression_share"
        ),
        "search_rank_lost_impression_share": _opt(metrics, "search_rank_lost_impression_share"),
        "search_absolute_top_impression_share": _opt(
            metrics, "search_absolute_top_impression_share"
        ),
        "top_impression_rate": _opt(metrics, "top_impression_percentage"),
        "absolute_top_impression_rate": _opt(metrics, "absolute_top_impression_percentage"),
    }


def derived_kpis(row: dict[str, Any]) -> dict[str, Any]:
    """CPL and ROAS computed only where the inputs actually exist."""

    cost = row.get("cost") or 0.0
    conversions = row.get("conversions") or 0.0
    value = row.get("conversions_value") or 0.0
    return {
        "cost_per_conversion_calc": (cost / conversions) if conversions else None,
        "roas": (value / cost) if cost and value else None,
        "roas_note": None if value else "no conversion value recorded; ROAS unavailable",
    }


class ReadOnlyAudit:
    """Runs the audit's SELECT queries and remembers what failed."""

    def __init__(self, client: Any, customer_id: str) -> None:
        self.client = client
        self.customer_id = customer_id
        self.read_errors: list[dict[str, str]] = []
        self.queries_executed: list[str] = []

    def rows(self, name: str, query: str) -> list[Any]:
        try:
            results = list(run_read_only_query(self.client, self.customer_id, query))
        except DiscoveryError:
            raise
        except Exception as exc:
            self.read_errors.append({"query": name, "error": f"{type(exc).__name__}: {exc}"})
            return []
        self.queries_executed.append(name)
        return results


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

_METRIC_SELECT = """
      metrics.cost_micros,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.conversions,
      metrics.all_conversions,
      metrics.conversions_from_interactions_rate,
      metrics.cost_per_conversion,
      metrics.cost_per_all_conversions,
      metrics.conversions_value,
      metrics.all_conversions_value
"""

_SEARCH_SHARE_SELECT = """
      metrics.search_impression_share,
      metrics.search_budget_lost_impression_share,
      metrics.search_rank_lost_impression_share,
      metrics.search_absolute_top_impression_share,
      metrics.top_impression_percentage,
      metrics.absolute_top_impression_percentage
"""

# The API rejects budget-lost impression share below campaign level: it is a
# campaign-budget metric, so AD_GROUP and KEYWORD_VIEW cannot select it.
_SEARCH_SHARE_SUB_CAMPAIGN_SELECT = """
      metrics.search_impression_share,
      metrics.search_rank_lost_impression_share,
      metrics.search_absolute_top_impression_share,
      metrics.top_impression_percentage,
      metrics.absolute_top_impression_percentage
"""

CONVERSION_ACTION_QUERY = """
    SELECT
      conversion_action.id,
      conversion_action.name,
      conversion_action.status,
      conversion_action.type,
      conversion_action.category,
      conversion_action.origin,
      conversion_action.primary_for_goal,
      conversion_action.include_in_conversions_metric,
      conversion_action.counting_type,
      conversion_action.attribution_model_settings.attribution_model,
      conversion_action.attribution_model_settings.data_driven_model_status,
      conversion_action.click_through_lookback_window_days,
      conversion_action.view_through_lookback_window_days,
      conversion_action.phone_call_duration_seconds,
      conversion_action.value_settings.default_value,
      conversion_action.value_settings.always_use_default_value,
      conversion_action.owner_customer
    FROM conversion_action
"""

CAMPAIGN_SETTINGS_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.serving_status,
      campaign.primary_status,
      campaign.primary_status_reasons,
      campaign.advertising_channel_type,
      campaign.advertising_channel_sub_type,
      campaign.bidding_strategy_type,
      campaign.bidding_strategy_system_status,
      campaign.maximize_conversions.target_cpa_micros,
      campaign.target_cpa.target_cpa_micros,
      campaign.target_roas.target_roas,
      campaign.target_spend.cpc_bid_ceiling_micros,
      campaign.network_settings.target_google_search,
      campaign.network_settings.target_search_network,
      campaign.network_settings.target_content_network,
      campaign.network_settings.target_partner_search_network,
      campaign.geo_target_type_setting.positive_geo_target_type,
      campaign.geo_target_type_setting.negative_geo_target_type,
      campaign.dynamic_search_ads_setting.domain_name,
      campaign.dynamic_search_ads_setting.use_supplied_urls_only,
      campaign.ai_max_setting.enable_ai_max,
      campaign.keyword_match_type,
      campaign.optimization_score,
      campaign.start_date_time,
      campaign.end_date_time,
      campaign.final_url_suffix,
      campaign.tracking_url_template,
      campaign.ad_serving_optimization_status,
      campaign.targeting_setting.target_restrictions,
      campaign_budget.id,
      campaign_budget.name,
      campaign_budget.amount_micros,
      campaign_budget.delivery_method,
      campaign_budget.explicitly_shared,
      campaign_budget.has_recommended_budget
    FROM campaign
    WHERE campaign.status != REMOVED
"""

ASSET_AUTOMATION_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.asset_automation_settings
    FROM campaign
    WHERE campaign.status != REMOVED
"""

CAMPAIGN_CRITERION_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign_criterion.criterion_id,
      campaign_criterion.type,
      campaign_criterion.negative,
      campaign_criterion.status,
      campaign_criterion.bid_modifier,
      campaign_criterion.display_name,
      campaign_criterion.location.geo_target_constant,
      campaign_criterion.proximity.radius,
      campaign_criterion.proximity.radius_units,
      campaign_criterion.language.language_constant,
      campaign_criterion.device.type,
      campaign_criterion.ad_schedule.day_of_week,
      campaign_criterion.ad_schedule.start_hour,
      campaign_criterion.ad_schedule.end_hour,
      campaign_criterion.keyword.text,
      campaign_criterion.keyword.match_type
    FROM campaign_criterion
    WHERE campaign.status != REMOVED
"""

SHARED_SET_QUERY = """
    SELECT
      shared_set.id,
      shared_set.name,
      shared_set.type,
      shared_set.status,
      shared_set.member_count
    FROM shared_set
"""

SHARED_CRITERION_QUERY = """
    SELECT
      shared_set.id,
      shared_set.name,
      shared_criterion.criterion_id,
      shared_criterion.type,
      shared_criterion.keyword.text,
      shared_criterion.keyword.match_type
    FROM shared_criterion
"""

CAMPAIGN_SHARED_SET_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      shared_set.id,
      shared_set.name,
      shared_set.type,
      campaign_shared_set.status
    FROM campaign_shared_set
"""

AD_GROUP_CRITERION_NEGATIVE_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      ad_group_criterion.status
    FROM ad_group_criterion
    WHERE ad_group_criterion.negative = TRUE
      AND ad_group_criterion.type = KEYWORD
      AND campaign.status != REMOVED
"""

ASSET_POLICY_QUERY = """
    SELECT
      asset.id,
      asset.name,
      asset.type,
      asset.final_urls,
      asset.policy_summary.approval_status,
      asset.policy_summary.review_status,
      asset.sitelink_asset.link_text,
      asset.sitelink_asset.start_date,
      asset.sitelink_asset.end_date,
      asset.callout_asset.callout_text,
      asset.call_asset.phone_number,
      asset.call_asset.country_code,
      asset.structured_snippet_asset.header,
      asset.structured_snippet_asset.values
    FROM asset
"""


def customer_query(window: DateWindow) -> str:
    return f"""
    SELECT
      customer.id,
      customer.descriptive_name,
{_METRIC_SELECT},
      metrics.invalid_clicks,
      metrics.invalid_click_rate
    FROM customer
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
"""


def phone_metrics_query(window: DateWindow) -> str:
    """Phone metrics are campaign-level; CUSTOMER cannot select them."""

    return f"""
    SELECT
      campaign.id,
      campaign.name,
      metrics.phone_calls,
      metrics.phone_impressions,
      metrics.phone_through_rate
    FROM campaign
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
      AND campaign.status != REMOVED
"""


def campaign_performance_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      campaign_budget.amount_micros,
{_METRIC_SELECT},
{_SEARCH_SHARE_SELECT},
      metrics.invalid_clicks,
      metrics.invalid_click_rate
    FROM campaign
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
      AND campaign.status != REMOVED
"""


def ad_group_performance_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group.status,
{_METRIC_SELECT},
{_SEARCH_SHARE_SUB_CAMPAIGN_SELECT}
    FROM ad_group
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
      AND campaign.status != REMOVED
"""


def keyword_performance_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      ad_group_criterion.status,
      ad_group_criterion.system_serving_status,
      ad_group_criterion.approval_status,
      ad_group_criterion.final_urls,
      ad_group_criterion.quality_info.quality_score,
      ad_group_criterion.quality_info.creative_quality_score,
      ad_group_criterion.quality_info.post_click_quality_score,
      ad_group_criterion.quality_info.search_predicted_ctr,
{_METRIC_SELECT},
{_SEARCH_SHARE_SUB_CAMPAIGN_SELECT}
    FROM keyword_view
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
      AND campaign.status != REMOVED
"""


def search_term_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      search_term_view.search_term,
      search_term_view.status,
      segments.search_term_match_type,
      segments.keyword.info.text,
      segments.keyword.info.match_type,
{_METRIC_SELECT}
    FROM search_term_view
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
"""


def ad_performance_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group_ad.ad.id,
      ad_group_ad.ad.type,
      ad_group_ad.status,
      ad_group_ad.ad_strength,
      ad_group_ad.policy_summary.approval_status,
      ad_group_ad.policy_summary.review_status,
      ad_group_ad.ad.final_urls,
      ad_group_ad.ad.responsive_search_ad.path1,
      ad_group_ad.ad.responsive_search_ad.path2,
{_METRIC_SELECT}
    FROM ad_group_ad
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
      AND campaign.status != REMOVED
"""


def ad_asset_performance_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.name,
      ad_group.name,
      ad_group_ad.ad.id,
      ad_group_ad_asset_view.field_type,
      ad_group_ad_asset_view.performance_label,
      ad_group_ad_asset_view.pinned_field,
      ad_group_ad_asset_view.enabled,
      asset.id,
      asset.text_asset.text,
      metrics.impressions,
      metrics.clicks,
      metrics.conversions
    FROM ad_group_ad_asset_view
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
"""


def conversion_breakdown_query(window: DateWindow) -> str:
    return f"""
    SELECT
      segments.conversion_action,
      segments.conversion_action_name,
      segments.conversion_action_category,
      metrics.conversions,
      metrics.all_conversions,
      metrics.conversions_value,
      metrics.all_conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
"""


def _segment_query(window: DateWindow, segment: str, extra: str = "") -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      {segment}{extra},
{_METRIC_SELECT}
    FROM campaign
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
      AND campaign.status != REMOVED
"""


def geo_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      geographic_view.location_type,
      geographic_view.country_criterion_id,
      segments.geo_target_city,
      segments.geo_target_metro,
{_METRIC_SELECT}
    FROM geographic_view
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
"""


def daily_series_query(window: DateWindow) -> str:
    return f"""
    SELECT
      campaign.id,
      campaign.name,
      segments.date,
{_METRIC_SELECT}
    FROM campaign
    WHERE segments.date BETWEEN '{window.start}' AND '{window.end}'
      AND campaign.status != REMOVED
"""


def geo_target_constant_query(resource_names: Iterable[str]) -> str:
    ids = sorted({str(name).split("/")[-1] for name in resource_names if name})
    quoted = ", ".join(f"'geoTargetConstants/{value}'" for value in ids if value.isdigit())
    return f"""
    SELECT
      geo_target_constant.id,
      geo_target_constant.name,
      geo_target_constant.canonical_name,
      geo_target_constant.target_type,
      geo_target_constant.country_code
    FROM geo_target_constant
    WHERE geo_target_constant.resource_name IN ({quoted})
"""


# ---------------------------------------------------------------------------
# Row mappers
# ---------------------------------------------------------------------------


def _campaign_ref(row: Any) -> dict[str, str]:
    return {"campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name or ""}


def _ad_group_ref(row: Any) -> dict[str, str]:
    return {"ad_group_id": str(row.ad_group.id), "ad_group_name": row.ad_group.name or ""}


def map_conversion_action(row: Any) -> dict[str, Any]:
    action = row.conversion_action
    settings = action.attribution_model_settings
    return {
        "id": str(action.id),
        "name": action.name or "",
        "status": enum_name(action.status),
        "type": enum_name(action.type_),
        "category": enum_name(action.category),
        "origin": enum_name(action.origin),
        "primary_for_goal": bool(action.primary_for_goal),
        "include_in_conversions_metric": bool(action.include_in_conversions_metric),
        "counting_type": enum_name(action.counting_type),
        "attribution_model": enum_name(settings.attribution_model),
        "data_driven_model_status": enum_name(settings.data_driven_model_status),
        "click_through_lookback_days": int(action.click_through_lookback_window_days),
        "view_through_lookback_days": int(action.view_through_lookback_window_days),
        "phone_call_duration_seconds": int(action.phone_call_duration_seconds),
        "default_value": float(action.value_settings.default_value),
        "always_use_default_value": bool(action.value_settings.always_use_default_value),
        "owner_customer": str(action.owner_customer or "").split("/")[-1],
    }


def map_campaign_settings(row: Any) -> dict[str, Any]:
    campaign = row.campaign
    network = campaign.network_settings
    geo = campaign.geo_target_type_setting
    budget = row.campaign_budget
    return {
        **_campaign_ref(row),
        "status": enum_name(campaign.status),
        "serving_status": enum_name(campaign.serving_status),
        "primary_status": enum_name(campaign.primary_status),
        "primary_status_reasons": [enum_name(item) for item in campaign.primary_status_reasons],
        "channel_type": enum_name(campaign.advertising_channel_type),
        "channel_sub_type": enum_name(campaign.advertising_channel_sub_type),
        "bidding_strategy_type": enum_name(campaign.bidding_strategy_type),
        "bidding_strategy_system_status": enum_name(campaign.bidding_strategy_system_status),
        "maximize_conversions_target_cpa": _micros(
            campaign.maximize_conversions.target_cpa_micros
        ),
        "target_cpa": _micros(campaign.target_cpa.target_cpa_micros),
        "target_roas": float(campaign.target_roas.target_roas),
        "network_google_search": bool(network.target_google_search),
        "network_search_partners": bool(network.target_search_network),
        "network_display": bool(network.target_content_network),
        "network_partner_search": bool(network.target_partner_search_network),
        "positive_geo_target_type": enum_name(geo.positive_geo_target_type),
        "negative_geo_target_type": enum_name(geo.negative_geo_target_type),
        "dsa_domain": campaign.dynamic_search_ads_setting.domain_name or "",
        "ai_max_enabled": bool(campaign.ai_max_setting.enable_ai_max),
        "campaign_keyword_match_type": enum_name(campaign.keyword_match_type),
        "optimization_score": float(campaign.optimization_score),
        "ad_serving_optimization_status": enum_name(campaign.ad_serving_optimization_status),
        "target_restrictions": [
            {
                "dimension": enum_name(item.targeting_dimension),
                "bid_only": bool(item.bid_only),
            }
            for item in campaign.targeting_setting.target_restrictions
        ],
        "start_date_time": campaign.start_date_time or "",
        "end_date_time": campaign.end_date_time or "",
        "final_url_suffix": campaign.final_url_suffix or "",
        "tracking_url_template": campaign.tracking_url_template or "",
        "budget_id": str(budget.id),
        "budget_name": budget.name or "",
        "daily_budget": _micros(budget.amount_micros),
        "budget_delivery": enum_name(budget.delivery_method),
        "budget_shared": bool(budget.explicitly_shared),
    }


def map_campaign_criterion(row: Any) -> dict[str, Any]:
    criterion = row.campaign_criterion
    return {
        **_campaign_ref(row),
        "criterion_id": str(criterion.criterion_id),
        "type": enum_name(criterion.type_),
        "negative": bool(criterion.negative),
        "status": enum_name(criterion.status),
        # Unset and -100% both read as 0.0 without a presence check, and the
        # difference is "no modifier" versus "this device is excluded".
        "bid_modifier": _opt(criterion, "bid_modifier"),
        "bid_modifier_set": _opt(criterion, "bid_modifier") is not None,
        "display_name": criterion.display_name or "",
        "geo_target_constant": str(criterion.location.geo_target_constant or ""),
        "proximity_radius": float(criterion.proximity.radius),
        "proximity_units": enum_name(criterion.proximity.radius_units),
        "language_constant": str(criterion.language.language_constant or ""),
        "device": enum_name(criterion.device.type_),
        "ad_schedule_day": enum_name(criterion.ad_schedule.day_of_week),
        "ad_schedule_start_hour": int(criterion.ad_schedule.start_hour),
        "ad_schedule_end_hour": int(criterion.ad_schedule.end_hour),
        "keyword_text": criterion.keyword.text or "",
        "keyword_match_type": enum_name(criterion.keyword.match_type),
    }


def map_keyword(row: Any) -> dict[str, Any]:
    criterion = row.ad_group_criterion
    quality = criterion.quality_info
    return {
        **_campaign_ref(row),
        **_ad_group_ref(row),
        "criterion_id": str(criterion.criterion_id),
        "text": criterion.keyword.text or "",
        "match_type": enum_name(criterion.keyword.match_type),
        "status": enum_name(criterion.status),
        "system_serving_status": enum_name(criterion.system_serving_status),
        "approval_status": enum_name(criterion.approval_status),
        "final_urls": [str(url) for url in criterion.final_urls],
        "quality_score": _opt(quality, "quality_score"),
        "creative_quality": enum_name(quality.creative_quality_score),
        "landing_page_quality": enum_name(quality.post_click_quality_score),
        "expected_ctr": enum_name(quality.search_predicted_ctr),
        **metrics_dict(row.metrics),
    }


def map_search_term(row: Any) -> dict[str, Any]:
    view = row.search_term_view
    return {
        **_campaign_ref(row),
        **_ad_group_ref(row),
        "search_term": scrub_text(view.search_term),
        "status": enum_name(view.status),
        "match_type": enum_name(row.segments.search_term_match_type),
        "matched_keyword": scrub_text(row.segments.keyword.info.text),
        "matched_keyword_match_type": enum_name(row.segments.keyword.info.match_type),
        **metrics_dict(row.metrics),
    }


def map_ad(row: Any) -> dict[str, Any]:
    ad_group_ad = row.ad_group_ad
    ad = ad_group_ad.ad
    return {
        **_campaign_ref(row),
        **_ad_group_ref(row),
        "ad_id": str(ad.id),
        "ad_type": enum_name(ad.type_),
        "status": enum_name(ad_group_ad.status),
        "ad_strength": enum_name(ad_group_ad.ad_strength),
        "approval_status": enum_name(ad_group_ad.policy_summary.approval_status),
        "review_status": enum_name(ad_group_ad.policy_summary.review_status),
        "final_urls": [str(url) for url in ad.final_urls],
        "path1": ad.responsive_search_ad.path1 or "",
        "path2": ad.responsive_search_ad.path2 or "",
        **metrics_dict(row.metrics),
    }


def map_ad_asset(row: Any) -> dict[str, Any]:
    view = row.ad_group_ad_asset_view
    return {
        "campaign_name": row.campaign.name or "",
        "ad_group_name": row.ad_group.name or "",
        "ad_id": str(row.ad_group_ad.ad.id),
        "asset_id": str(row.asset.id),
        "field_type": enum_name(view.field_type),
        "performance_label": enum_name(view.performance_label),
        "pinned_field": enum_name(view.pinned_field),
        "enabled": bool(view.enabled),
        "text": row.asset.text_asset.text or "",
        "impressions": int(row.metrics.impressions),
        "clicks": int(row.metrics.clicks),
        "conversions": float(row.metrics.conversions),
    }


def map_asset_policy(row: Any) -> dict[str, Any]:
    asset = row.asset
    return {
        "asset_id": str(asset.id),
        "name": asset.name or "",
        "type": enum_name(asset.type_),
        "final_urls": [str(url) for url in asset.final_urls],
        "approval_status": enum_name(asset.policy_summary.approval_status),
        "review_status": enum_name(asset.policy_summary.review_status),
        "sitelink_text": asset.sitelink_asset.link_text or "",
        "sitelink_start_date": asset.sitelink_asset.start_date or "",
        "sitelink_end_date": asset.sitelink_asset.end_date or "",
        "callout_text": asset.callout_asset.callout_text or "",
        "call_phone_present": bool(asset.call_asset.phone_number),
        "call_country_code": asset.call_asset.country_code or "",
        "snippet_header": asset.structured_snippet_asset.header or "",
        "snippet_values": [str(value) for value in asset.structured_snippet_asset.values],
    }


def map_conversion_breakdown(row: Any) -> dict[str, Any]:
    segments = row.segments
    return {
        "conversion_action_id": str(segments.conversion_action or "").split("/")[-1],
        "conversion_action_name": segments.conversion_action_name or "",
        "category": enum_name(segments.conversion_action_category),
        "conversions": float(row.metrics.conversions),
        "all_conversions": float(row.metrics.all_conversions),
        "conversions_value": float(row.metrics.conversions_value),
        "all_conversions_value": float(row.metrics.all_conversions_value),
    }
