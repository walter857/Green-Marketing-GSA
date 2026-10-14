from __future__ import annotations

from datetime import datetime
from typing import Any

from .asset_publisher import publish_campaign_assets
from .config import normalize_customer_id
from .validators import assert_valid_campaign_plan

MINUTE_ENUMS = {
    0: "ZERO",
    15: "FIFTEEN",
    30: "THIRTY",
    45: "FORTY_FIVE",
}


def _micros(value: float) -> int:
    return int(round(float(value) * 1_000_000))


def _time_parts(value: str) -> tuple[int, int]:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour, parsed.minute


def publish_plan_paused(client: Any, plan: dict[str, Any]) -> dict[str, Any]:
    assert_valid_campaign_plan(plan)
    customer_id = normalize_customer_id(plan["target"]["child_customer_id"])
    result: dict[str, Any] = {"customer_id": customer_id, "campaigns": []}
    for campaign_plan in plan["campaigns"]:
        result["campaigns"].append(
            _publish_campaign(client, customer_id, campaign_plan)
        )
    return result


def _publish_campaign(
    client: Any,
    customer_id: str,
    plan: dict[str, Any],
) -> dict[str, Any]:
    created: dict[str, Any] = {
        "name": plan["name"],
        "budget": None,
        "campaign": None,
        "criteria": [],
        "ad_groups": [],
        "assets": [],
    }

    budget_service = client.get_service("CampaignBudgetService")
    budget_op = client.get_type("CampaignBudgetOperation")
    budget_op.create.name = f"{plan['name']} | Budget"
    budget_op.create.amount_micros = _micros(plan["daily_budget"])
    budget_op.create.delivery_method = (
        client.enums.BudgetDeliveryMethodEnum.STANDARD
    )
    budget_response = budget_service.mutate_campaign_budgets(
        customer_id=customer_id,
        operations=[budget_op],
    )
    budget_resource = budget_response.results[0].resource_name
    created["budget"] = budget_resource

    campaign_service = client.get_service("CampaignService")
    campaign_op = client.get_type("CampaignOperation")
    campaign = campaign_op.create
    campaign.name = plan["name"]
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum.SEARCH
    )
    campaign.campaign_budget = budget_resource
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = False
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False
    campaign.geo_target_type_setting.positive_geo_target_type = (
        client.enums.PositiveGeoTargetTypeEnum.PRESENCE
    )
    campaign.geo_target_type_setting.negative_geo_target_type = (
        client.enums.NegativeGeoTargetTypeEnum.PRESENCE
    )
    campaign.contains_eu_political_advertising = getattr(
        client.enums.EuPoliticalAdvertisingStatusEnum,
        "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
    )

    bidding = plan.get("bidding") or {}
    target_cpa = bidding.get("target_cpa")
    if target_cpa:
        campaign.maximize_conversions.target_cpa_micros = _micros(target_cpa)
    else:
        campaign._pb.maximize_conversions.SetInParent()

    campaign_response = campaign_service.mutate_campaigns(
        customer_id=customer_id,
        operations=[campaign_op],
    )
    campaign_resource = campaign_response.results[0].resource_name
    created["campaign"] = campaign_resource

    created["criteria"] = _publish_campaign_criteria(
        client,
        customer_id,
        campaign_resource,
        plan,
    )

    for ad_group_plan in plan["ad_groups"]:
        created["ad_groups"].append(
            _publish_ad_group(
                client,
                customer_id,
                campaign_resource,
                plan["final_url"],
                ad_group_plan,
            )
        )

    created["assets"] = publish_campaign_assets(
        client,
        customer_id,
        campaign_resource,
        plan["ad_groups"],
    )
    return created


def _publish_campaign_criteria(
    client: Any,
    customer_id: str,
    campaign_resource: str,
    plan: dict[str, Any],
) -> list[str]:
    service = client.get_service("CampaignCriterionService")
    operations = []

    location = plan["location"]
    for geo_id in location.get("geo_target_constant_ids") or []:
        op = client.get_type("CampaignCriterionOperation")
        op.create.campaign = campaign_resource
        op.create.location.geo_target_constant = f"geoTargetConstants/{geo_id}"
        operations.append(op)

    radius = location.get("radius") or {}
    if all(radius.get(key) not in (None, "") for key in ("latitude", "longitude", "distance", "unit")):
        op = client.get_type("CampaignCriterionOperation")
        criterion = op.create
        criterion.campaign = campaign_resource
        criterion.proximity.geo_point.latitude_in_micro_degrees = int(
            round(float(radius["latitude"]) * 1_000_000)
        )
        criterion.proximity.geo_point.longitude_in_micro_degrees = int(
            round(float(radius["longitude"]) * 1_000_000)
        )
        criterion.proximity.radius = float(radius["distance"])
        criterion.proximity.radius_units = getattr(
            client.enums.ProximityRadiusUnitsEnum,
            str(radius["unit"]).upper(),
        )
        operations.append(op)

    for geo_id in location.get("exclusions") or []:
        op = client.get_type("CampaignCriterionOperation")
        op.create.campaign = campaign_resource
        op.create.negative = True
        op.create.location.geo_target_constant = f"geoTargetConstants/{geo_id}"
        operations.append(op)

    for language_id in plan.get("language_constant_ids") or ["1000"]:
        op = client.get_type("CampaignCriterionOperation")
        op.create.campaign = campaign_resource
        op.create.language.language_constant = f"languageConstants/{language_id}"
        operations.append(op)

    for window in plan["schedule"]:
        start_hour, start_minute = _time_parts(window["start"])
        end_hour, end_minute = _time_parts(window["end"])
        op = client.get_type("CampaignCriterionOperation")
        schedule = op.create.ad_schedule
        op.create.campaign = campaign_resource
        schedule.day_of_week = getattr(
            client.enums.DayOfWeekEnum,
            str(window["day"]).upper(),
        )
        schedule.start_hour = start_hour
        schedule.start_minute = getattr(
            client.enums.MinuteOfHourEnum,
            MINUTE_ENUMS[start_minute],
        )
        schedule.end_hour = end_hour
        schedule.end_minute = getattr(
            client.enums.MinuteOfHourEnum,
            MINUTE_ENUMS[end_minute],
        )
        operations.append(op)

    for negative in plan.get("negatives") or []:
        op = client.get_type("CampaignCriterionOperation")
        op.create.campaign = campaign_resource
        op.create.negative = True
        op.create.keyword.text = negative
        op.create.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
        operations.append(op)

    if not operations:
        return []
    response = service.mutate_campaign_criteria(
        customer_id=customer_id,
        operations=operations,
    )
    return [item.resource_name for item in response.results]


def _publish_ad_group(
    client: Any,
    customer_id: str,
    campaign_resource: str,
    final_url: str,
    plan: dict[str, Any],
) -> dict[str, Any]:
    service = client.get_service("AdGroupService")
    op = client.get_type("AdGroupOperation")
    op.create.name = plan["name"]
    op.create.campaign = campaign_resource
    op.create.status = client.enums.AdGroupStatusEnum.PAUSED
    op.create.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    response = service.mutate_ad_groups(customer_id=customer_id, operations=[op])
    resource = response.results[0].resource_name

    criteria_service = client.get_service("AdGroupCriterionService")
    keyword_ops = []
    for keyword in plan["keywords"]:
        keyword_op = client.get_type("AdGroupCriterionOperation")
        keyword_op.create.ad_group = resource
        keyword_op.create.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        keyword_op.create.keyword.text = keyword["text"]
        keyword_op.create.keyword.match_type = getattr(
            client.enums.KeywordMatchTypeEnum,
            keyword["match_type"],
        )
        keyword_ops.append(keyword_op)
    keyword_response = criteria_service.mutate_ad_group_criteria(
        customer_id=customer_id,
        operations=keyword_ops,
    )

    ad_service = client.get_service("AdGroupAdService")
    ad_ops = []
    for ad in plan["ads"]:
        ad_op = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_op.create
        ad_group_ad.ad_group = resource
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        rsa = ad_group_ad.ad.responsive_search_ad
        for headline in ad["headlines"]:
            text = headline["text"] if isinstance(headline, dict) else headline
            asset = client.get_type("AdTextAsset")
            asset.text = text
            if isinstance(headline, dict) and headline.get("pin"):
                asset.pinned_field = getattr(
                    client.enums.ServedAssetFieldTypeEnum,
                    headline["pin"],
                )
            rsa.headlines.append(asset)
        for description in ad["descriptions"]:
            asset = client.get_type("AdTextAsset")
            asset.text = (
                description["text"] if isinstance(description, dict) else description
            )
            rsa.descriptions.append(asset)
        if plan.get("path1"):
            rsa.path1 = plan["path1"]
        if plan.get("path2"):
            rsa.path2 = plan["path2"]
        ad_group_ad.ad.final_urls.append(final_url)
        ad_ops.append(ad_op)
    ad_response = ad_service.mutate_ad_group_ads(
        customer_id=customer_id,
        operations=ad_ops,
    )

    return {
        "name": plan["name"],
        "resource_name": resource,
        "keywords": [item.resource_name for item in keyword_response.results],
        "ads": [item.resource_name for item in ad_response.results],
    }
