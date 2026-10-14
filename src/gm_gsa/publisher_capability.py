"""Pre-approval publishability check.

An approval fingerprint is a promise that the plan can be executed exactly as written. That
promise is only worth something if a publisher handler exists for every mutation the plan
declares, supports the statuses and fields the plan requires, and produces exactly the
declared counts.

This module makes that check a gate rather than a hope: ``assert_publishable`` refuses a
plan whose mutations the publisher cannot reproduce, and ``can_issue_fingerprint`` is the
call that plan finalization must pass before a fingerprint is presented.
"""

from __future__ import annotations

from typing import Any

from .plan_compiler import CompiledPlan, PlanCompileError, assert_counts_match, compile_plan


class PublisherCapabilityError(RuntimeError):
    """Raised when the publisher cannot reproduce a plan exactly."""


# Every mutation type the publisher can execute, with the capabilities each handler covers.
# A plan that needs a type absent from this registry cannot be fingerprinted.
HANDLERS: dict[str, dict[str, Any]] = {
    "campaign_budget": {"handler": "_publish_budget", "kind": "create", "statuses": []},
    "campaign": {"handler": "_publish_campaign_resource", "kind": "create",
                 "statuses": ["PAUSED"],
                 "fields": ["name", "status", "channel", "networks", "geo_target_type_setting"]},
    "campaign_criterion_proximity": {"handler": "_publish_proximity", "kind": "create",
                                     "statuses": [],
                                     "fields": ["latitude", "longitude", "radius", "radius_units"],
                                     "supports_multiple": True},
    "campaign_criterion_location": {"handler": "_publish_location", "kind": "create",
                                    "statuses": [], "fields": ["geo_target_constant"]},
    "campaign_criterion_negative_keyword": {"handler": "_publish_campaign_negatives",
                                            "kind": "create", "statuses": [],
                                            "fields": ["text", "match_type"]},
    "campaign_criterion_ad_schedule": {"handler": "_publish_ad_schedule", "kind": "create",
                                       "statuses": [], "fields": ["start", "end", "day"]},
    "campaign_criterion_language": {"handler": "_publish_language", "kind": "create",
                                    "statuses": [], "fields": ["language_constant"]},
    "ad_group": {"handler": "_publish_ad_group", "kind": "create", "statuses": ["PAUSED"]},
    "ad_group_criterion_keyword": {"handler": "_publish_keywords", "kind": "create",
                                   "statuses": ["PAUSED"],
                                   "fields": ["text", "match_type", "status"]},
    "ad_group_criterion_negative_keyword": {"handler": "_publish_ad_group_negatives",
                                            "kind": "create", "statuses": [],
                                            "fields": ["text", "match_type"]},
    "ad_group_ad_rsa": {"handler": "_publish_rsa", "kind": "create", "statuses": ["PAUSED"],
                        "fields": ["headlines", "descriptions", "final_url", "pin"]},
    "asset_sitelink_new": {"handler": "_publish_sitelink_assets", "kind": "create",
                           "statuses": [],
                           "fields": ["link_text", "description1", "description2", "final_url"]},
    "asset_callout_new": {"handler": "_publish_callout_assets", "kind": "create",
                          "statuses": [], "fields": ["text"]},
    "asset_structured_snippet_new": {"handler": "_publish_snippet_assets", "kind": "create",
                                     "statuses": [], "fields": ["header", "values"]},
    "campaign_asset_association": {"handler": "_publish_campaign_assets", "kind": "create",
                                   "statuses": ["PAUSED", "ENABLED"],
                                   "fields": ["field_type", "status", "asset"]},
    "custom_conversion_goal": {"handler": "_publish_custom_conversion_goal", "kind": "create",
                               "statuses": ["ENABLED"],
                               "fields": ["name", "status", "conversion_actions"]},
    "campaign_conversion_goal_biddable_false": {"handler": "_update_campaign_conversion_goals",
                                                "kind": "update", "statuses": [],
                                                "fields": ["biddable"],
                                                "update_masks": [["biddable"]]},
    "conversion_goal_campaign_config": {"handler": "_update_conversion_goal_campaign_config",
                                        "kind": "update", "statuses": [],
                                        "fields": ["custom_conversion_goal"],
                                        "update_masks": [["custom_conversion_goal"]]},
}


def unsupported_types(compiled: CompiledPlan) -> list[str]:
    return sorted({op.mutation_type for op in compiled.operations if op.mutation_type not in HANDLERS})


def assert_publishable(plan: dict[str, Any], asset_manifest: dict[str, Any] | None = None) -> CompiledPlan:
    """Compile the plan and refuse it unless the publisher can reproduce it exactly."""
    try:
        compiled = compile_plan(plan, asset_manifest)
    except Exception as exc:  # noqa: BLE001
        raise PublisherCapabilityError(f"Plan could not be compiled: {exc}") from exc

    errors: list[str] = []

    missing = unsupported_types(compiled)
    if missing:
        errors.append("no publisher handler for: " + ", ".join(missing))

    for op in compiled.operations:
        spec = HANDLERS.get(op.mutation_type)
        if not spec:
            continue
        if spec["kind"] != op.kind:
            errors.append(f"{op.mutation_type}: handler is {spec['kind']}, plan wants {op.kind}")
        status = op.payload.get("status")
        if status and status not in spec.get("statuses", []):
            errors.append(
                f"{op.mutation_type} ({op.planned_id}): handler does not support status {status}"
            )
        mask = op.payload.get("update_mask")
        if mask is not None:
            allowed = spec.get("update_masks") or []
            if allowed and list(mask) not in [list(m) for m in allowed]:
                errors.append(
                    f"{op.mutation_type} ({op.planned_id}): update mask {mask} is not supported"
                )

    try:
        assert_counts_match(plan, compiled)
    except PlanCompileError as exc:
        errors.append(str(exc))

    if errors:
        raise PublisherCapabilityError(
            "Publisher cannot reproduce this plan:\n- " + "\n- ".join(errors)
        )
    return compiled


def can_issue_fingerprint(plan: dict[str, Any], asset_manifest: dict[str, Any] | None = None) -> bool:
    """Plan finalization must pass this before a fingerprint is presented for approval."""
    try:
        assert_publishable(plan, asset_manifest)
    except PublisherCapabilityError:
        return False
    return True
