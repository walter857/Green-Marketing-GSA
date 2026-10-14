from __future__ import annotations

from collections import Counter
from datetime import time
from typing import Any
from urllib.parse import urlparse

PROTECTED_NEGATIVES = {
    "near me",
    "quote",
    "price",
    "pricing",
    "cost",
    "best",
    "hire",
    "local",
    "emergency",
}
MATCH_TYPES = {"PHRASE", "EXACT"}
ALLOWED_VERTICALS = {"landscaping", "hardscaping", "heating-cooling", "similar-local-service"}
QUARTER_MINUTES = {0, 15, 30, 45}


def _text_asset_text(asset: Any) -> str:
    if isinstance(asset, str):
        return asset.strip()
    if isinstance(asset, dict):
        return str(asset.get("text", "")).strip()
    return ""


def _normalize_negative(value: str) -> str:
    return value.strip().strip('"').strip("[]").strip().casefold()


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _parse_time(value: str) -> time | None:
    try:
        hour_s, minute_s = value.split(":", 1)
        return time(int(hour_s), int(minute_s))
    except (AttributeError, TypeError, ValueError):
        return None


def validate_campaign_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    target = plan.get("target")
    if not isinstance(target, dict):
        return ["target must be a mapping"]
    customer_id = str(target.get("child_customer_id", ""))
    if len(customer_id) != 10 or not customer_id.isdigit():
        errors.append("target.child_customer_id must contain exactly 10 digits")
    if not str(target.get("exact_child_account_name", "")).strip():
        errors.append("target.exact_child_account_name is required")
    if str(target.get("vertical", "")).strip() not in ALLOWED_VERTICALS:
        errors.append("target.vertical is not in the Green Marketing vertical scope")
    if not str(target.get("exact_primary_service", "")).strip():
        errors.append("target.exact_primary_service is required")

    campaigns = plan.get("campaigns")
    if not isinstance(campaigns, list) or not campaigns:
        return errors + ["campaigns must be a non-empty list"]

    names = [str(c.get("name", "")).strip() for c in campaigns if isinstance(c, dict)]
    duplicates = [name for name, count in Counter(names).items() if name and count > 1]
    for name in duplicates:
        errors.append(f"duplicate campaign name: {name}")

    for campaign_index, campaign in enumerate(campaigns):
        prefix = f"campaigns[{campaign_index}]"
        if not isinstance(campaign, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        if not str(campaign.get("name", "")).strip():
            errors.append(f"{prefix}.name is required")
        if campaign.get("status") != "PAUSED":
            errors.append(f"{prefix}.status must be PAUSED")
        try:
            if float(campaign.get("daily_budget", 0)) <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"{prefix}.daily_budget must be positive")
        final_url = str(campaign.get("final_url", ""))
        if not _valid_url(final_url):
            errors.append(f"{prefix}.final_url must be an http(s) URL")

        _validate_location(campaign.get("location"), prefix, errors)
        _validate_schedule(campaign.get("schedule"), prefix, errors)

        for negative in campaign.get("negatives", []) or []:
            normalized = _normalize_negative(str(negative))
            if normalized in PROTECTED_NEGATIVES:
                errors.append(
                    f"{prefix}.negatives contains protected buyer-intent term: {negative}"
                )

        ad_groups = campaign.get("ad_groups")
        if not isinstance(ad_groups, list) or not ad_groups:
            errors.append(f"{prefix}.ad_groups must be a non-empty list")
            continue
        for group_index, group in enumerate(ad_groups):
            _validate_ad_group(group, f"{prefix}.ad_groups[{group_index}]", errors)

    return errors


def _validate_location(location: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(location, dict):
        errors.append(f"{prefix}.location must be a mapping")
        return
    if location.get("option") != "PRESENCE":
        errors.append(f"{prefix}.location.option must be PRESENCE")
    ids = location.get("geo_target_constant_ids") or []
    radius = location.get("radius") or {}
    has_radius = all(
        radius.get(key) not in (None, "")
        for key in ("latitude", "longitude", "distance", "unit")
    )
    if not ids and not has_radius:
        errors.append(
            f"{prefix}.location needs geo_target_constant_ids or a complete radius"
        )
    if has_radius:
        try:
            latitude = float(radius["latitude"])
            longitude = float(radius["longitude"])
            distance = float(radius["distance"])
            if not -90 <= latitude <= 90 or not -180 <= longitude <= 180 or distance <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"{prefix}.location.radius contains invalid coordinates or distance")
        if str(radius.get("unit", "")).upper() not in {"MILES", "KILOMETERS"}:
            errors.append(f"{prefix}.location.radius.unit must be MILES or KILOMETERS")


def _validate_schedule(schedule: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(schedule, list) or not schedule:
        errors.append(f"{prefix}.schedule must be a non-empty list")
        return
    for index, window in enumerate(schedule):
        item_prefix = f"{prefix}.schedule[{index}]"
        if not isinstance(window, dict):
            errors.append(f"{item_prefix} must be a mapping")
            continue
        start = _parse_time(str(window.get("start", "")))
        end = _parse_time(str(window.get("end", "")))
        if start is None or end is None:
            errors.append(f"{item_prefix} uses an invalid time")
            continue
        if start.minute not in QUARTER_MINUTES or end.minute not in QUARTER_MINUTES:
            errors.append(f"{item_prefix} times must use 15-minute increments")
        if start >= end:
            errors.append(f"{item_prefix} must not cross midnight; split overnight windows")


def _validate_ad_group(group: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(group, dict):
        errors.append(f"{prefix} must be a mapping")
        return
    canonical = str(group.get("canonical_keyword", "")).strip().casefold()
    if not canonical:
        errors.append(f"{prefix}.canonical_keyword is required")

    keywords = group.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        errors.append(f"{prefix}.keywords must be a non-empty list")
    else:
        observed_matches: set[str] = set()
        for index, keyword in enumerate(keywords):
            item_prefix = f"{prefix}.keywords[{index}]"
            if not isinstance(keyword, dict):
                errors.append(f"{item_prefix} must be a mapping")
                continue
            text = str(keyword.get("text", "")).strip().casefold()
            match_type = str(keyword.get("match_type", "")).upper()
            if text != canonical:
                errors.append(f"{item_prefix}.text must match canonical_keyword")
            if match_type not in MATCH_TYPES:
                errors.append(f"{item_prefix}.match_type must be PHRASE or EXACT")
            observed_matches.add(match_type)
        if observed_matches != MATCH_TYPES:
            errors.append(f"{prefix}.keywords must include PHRASE and EXACT")

    for path_name in ("path1", "path2"):
        path_value = str(group.get(path_name, ""))
        if len(path_value) > 15:
            errors.append(f"{prefix}.{path_name} exceeds 15 characters")

    ads = group.get("ads")
    if not isinstance(ads, list) or len(ads) != 2:
        errors.append(f"{prefix}.ads must contain exactly 2 RSAs")
    else:
        for ad_index, ad in enumerate(ads):
            _validate_rsa(ad, f"{prefix}.ads[{ad_index}]", canonical, errors)

    _validate_assets(group.get("assets") or {}, prefix, errors)


def _validate_rsa(
    ad: Any,
    prefix: str,
    canonical_keyword: str,
    errors: list[str],
) -> None:
    if not isinstance(ad, dict):
        errors.append(f"{prefix} must be a mapping")
        return
    headlines = ad.get("headlines")
    descriptions = ad.get("descriptions")
    if not isinstance(headlines, list) or not 3 <= len(headlines) <= 15:
        errors.append(f"{prefix}.headlines must contain 3 to 15 items")
        headlines = []
    if not isinstance(descriptions, list) or not 2 <= len(descriptions) <= 4:
        errors.append(f"{prefix}.descriptions must contain 2 to 4 items")
        descriptions = []

    seen: set[str] = set()
    has_h1_pin = False
    for index, asset in enumerate(headlines):
        text = _text_asset_text(asset)
        if not text:
            errors.append(f"{prefix}.headlines[{index}] is empty")
        if len(text) > 30:
            errors.append(f"{prefix}.headlines[{index}] exceeds 30 characters: {text}")
        normalized = text.casefold()
        if normalized in seen:
            errors.append(f"{prefix}.headlines contains duplicate text: {text}")
        seen.add(normalized)
        if isinstance(asset, dict) and asset.get("pin") == "HEADLINE_1":
            has_h1_pin = True
    if not has_h1_pin:
        errors.append(f"{prefix} needs at least one keyword-relevant HEADLINE_1 pin")

    for index, asset in enumerate(descriptions):
        text = _text_asset_text(asset)
        if not text:
            errors.append(f"{prefix}.descriptions[{index}] is empty")
        if len(text) > 90:
            errors.append(f"{prefix}.descriptions[{index}] exceeds 90 characters")

    if canonical_keyword and not any(
        canonical_keyword.split()[0] in _text_asset_text(asset).casefold()
        for asset in headlines
    ):
        errors.append(f"{prefix} does not contain a canonical-keyword term in headlines")


def _validate_assets(assets: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(assets, dict):
        errors.append(f"{prefix}.assets must be a mapping")
        return
    for index, sitelink in enumerate(assets.get("sitelinks", []) or []):
        if len(str(sitelink.get("title", ""))) > 25:
            errors.append(f"{prefix}.assets.sitelinks[{index}].title exceeds 25 characters")
        for field in ("description_1", "description_2"):
            if len(str(sitelink.get(field, ""))) > 35:
                errors.append(f"{prefix}.assets.sitelinks[{index}].{field} exceeds 35 characters")
        if sitelink.get("final_url") and not _valid_url(str(sitelink["final_url"])):
            errors.append(f"{prefix}.assets.sitelinks[{index}].final_url is invalid")
    for index, callout in enumerate(assets.get("callouts", []) or []):
        if len(str(callout)) > 25:
            errors.append(f"{prefix}.assets.callouts[{index}] exceeds 25 characters")
    for snippet_index, snippet in enumerate(assets.get("structured_snippets", []) or []):
        values = snippet.get("values", []) if isinstance(snippet, dict) else []
        if len(values) < 3:
            errors.append(
                f"{prefix}.assets.structured_snippets[{snippet_index}] needs at least 3 values"
            )
        for value_index, value in enumerate(values):
            if len(str(value)) > 25:
                errors.append(
                    f"{prefix}.assets.structured_snippets[{snippet_index}].values[{value_index}] exceeds 25 characters"
                )


def assert_valid_campaign_plan(plan: dict[str, Any]) -> None:
    errors = validate_campaign_plan(plan)
    if errors:
        raise ValueError("Campaign plan is invalid:\n- " + "\n- ".join(errors))
