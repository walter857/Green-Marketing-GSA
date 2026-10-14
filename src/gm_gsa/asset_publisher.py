from __future__ import annotations

from typing import Any


def _deduplicate(items: list[Any], key_fn) -> list[Any]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        key = key_fn(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def publish_campaign_assets(
    client: Any,
    customer_id: str,
    campaign_resource_name: str,
    ad_groups: list[dict[str, Any]],
) -> list[str]:
    sitelinks: list[dict[str, Any]] = []
    callouts: list[str] = []
    snippets: list[dict[str, Any]] = []
    for group in ad_groups:
        assets = group.get("assets") or {}
        sitelinks.extend(assets.get("sitelinks") or [])
        callouts.extend(assets.get("callouts") or [])
        snippets.extend(assets.get("structured_snippets") or [])

    sitelinks = _deduplicate(
        sitelinks,
        lambda item: (item.get("title"), item.get("final_url")),
    )
    callouts = _deduplicate(callouts, lambda item: str(item).casefold())
    snippets = _deduplicate(
        snippets,
        lambda item: (item.get("header"), tuple(item.get("values") or [])),
    )
    if not sitelinks and not callouts and not snippets:
        return []

    asset_service = client.get_service("AssetService")
    campaign_asset_service = client.get_service("CampaignAssetService")
    created: list[tuple[str, str]] = []

    asset_operations = []
    field_types = []
    for item in sitelinks:
        op = client.get_type("AssetOperation")
        asset = op.create
        asset.name = f"Sitelink | {item['title']} | {item['final_url']}"
        asset.final_urls.append(item["final_url"])
        asset.sitelink_asset.link_text = item["title"]
        if item.get("description_1"):
            asset.sitelink_asset.description1 = item["description_1"]
        if item.get("description_2"):
            asset.sitelink_asset.description2 = item["description_2"]
        asset_operations.append(op)
        field_types.append("SITELINK")

    for text in callouts:
        op = client.get_type("AssetOperation")
        op.create.name = f"Callout | {text}"
        op.create.callout_asset.callout_text = text
        asset_operations.append(op)
        field_types.append("CALLOUT")

    for item in snippets:
        op = client.get_type("AssetOperation")
        header = item["header"]
        op.create.name = f"Structured snippet | {header} | {' | '.join(item['values'])}"
        op.create.structured_snippet_asset.header = header
        op.create.structured_snippet_asset.values.extend(item["values"])
        asset_operations.append(op)
        field_types.append("STRUCTURED_SNIPPET")

    response = asset_service.mutate_assets(
        customer_id=customer_id,
        operations=asset_operations,
    )
    association_operations = []
    for result, field_type in zip(response.results, field_types, strict=True):
        op = client.get_type("CampaignAssetOperation")
        op.create.campaign = campaign_resource_name
        op.create.asset = result.resource_name
        op.create.field_type = getattr(
            client.enums.AssetFieldTypeEnum,
            field_type,
        )
        association_operations.append(op)
        created.append((result.resource_name, field_type))

    campaign_asset_service.mutate_campaign_assets(
        customer_id=customer_id,
        operations=association_operations,
    )
    return [resource_name for resource_name, _ in created]

