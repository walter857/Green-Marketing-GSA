"""Compile an approved campaign plan into an explicit, inspectable operation inventory.

Compilation is pure data. It issues no API call, so the exact set of mutations a plan will
produce can be counted and asserted long before anything is written to an account.

Two rules drive the design:

- Nothing is implicit. A resource is compiled only because a plan field asks for it. There
  are no defaulted language criteria and no schedule criteria invented from a schema-only
  schedule entry.
- Declared counts are checked against compiled counts. A plan that says it will make 80
  creates and compiles to 81 is a broken plan, not a plan with a bonus operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Mutation types this repository knows how to compile.
CREATE_TYPES = (
    "campaign_budget",
    "campaign",
    "campaign_criterion_proximity",
    "campaign_criterion_location",
    "campaign_criterion_negative_keyword",
    "campaign_criterion_ad_schedule",
    "campaign_criterion_language",
    "ad_group",
    "ad_group_criterion_keyword",
    "ad_group_criterion_negative_keyword",
    "ad_group_ad_rsa",
    "asset_sitelink_new",
    "asset_callout_new",
    "asset_structured_snippet_new",
    "campaign_asset_association",
    "custom_conversion_goal",
)
UPDATE_TYPES = (
    "campaign_conversion_goal_biddable_false",
    "conversion_goal_campaign_config",
)


class PlanCompileError(RuntimeError):
    """Raised when a plan cannot be compiled into exactly its declared inventory."""


@dataclass(frozen=True)
class Operation:
    """One planned mutation. ``planned_id`` is the stable identity used for retry lookup."""

    mutation_type: str
    kind: str  # "create" or "update"
    planned_id: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompiledPlan:
    creates: list[Operation] = field(default_factory=list)
    updates: list[Operation] = field(default_factory=list)

    @property
    def operations(self) -> list[Operation]:
        return self.creates + self.updates

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for op in self.operations:
            out[op.mutation_type] = out.get(op.mutation_type, 0) + 1
        return out

    def summary(self) -> dict[str, int]:
        return {
            "creates": len(self.creates),
            "updates": len(self.updates),
            "total": len(self.creates) + len(self.updates),
        }


def _asset_text(asset: Any) -> str:
    return asset["text"] if isinstance(asset, dict) else asset


def _asset_pin(asset: Any) -> str | None:
    return asset.get("pin") if isinstance(asset, dict) else None


def compile_plan(plan: dict[str, Any], asset_manifest: dict[str, Any] | None = None) -> CompiledPlan:
    """Turn an approved plan into its exact operation inventory. No API call is made."""
    compiled = CompiledPlan()
    campaign_plan = plan["campaigns"][0]
    name = campaign_plan["name"]

    compiled.creates.append(Operation(
        "campaign_budget", "create", f"budget::{name}",
        {"name": f"{name} | Budget", "amount": campaign_plan["daily_budget"],
         "delivery": "STANDARD"},
    ))
    compiled.creates.append(Operation(
        "campaign", "create", f"campaign::{name}",
        {"name": name, "status": campaign_plan["status"],
         "channel": "SEARCH",
         "google_search": campaign_plan["networks"]["google_search"],
         "search_partners": campaign_plan["networks"]["search_partners"],
         "display": campaign_plan["networks"]["display"],
         "positive_geo_target_type": campaign_plan["location"]["positive_geo_target_type"],
         "negative_geo_target_type": campaign_plan["location"]["negative_geo_target_type"],
         "bidding": campaign_plan["bidding"]["proposed_strategy"]},
    ))

    location = campaign_plan["location"]

    # Every proximity target is compiled. Radii are never converted; the unit travels with
    # the target so a mile can never silently become a kilometre.
    for target in location.get("proximity") or []:
        compiled.creates.append(Operation(
            "campaign_criterion_proximity", "create", f"proximity::{target['id']}",
            {"latitude": target["latitude"], "longitude": target["longitude"],
             "radius": target["radius"], "radius_units": target["units"]},
        ))

    for geo_id in location.get("geo_target_constant_ids") or []:
        compiled.creates.append(Operation(
            "campaign_criterion_location", "create", f"location::{geo_id}",
            {"geo_target_constant": f"geoTargetConstants/{geo_id}"},
        ))

    for negative in campaign_plan.get("negatives") or []:
        compiled.creates.append(Operation(
            "campaign_criterion_negative_keyword", "create", f"campaign_negative::{negative}",
            {"text": negative, "match_type": "PHRASE"},
        ))

    # Ad schedules only when the plan explicitly asks for them. A schedule entry that exists
    # to satisfy schema validation is not an instruction to create a criterion.
    schedule_count = int(campaign_plan.get("ad_schedule_criteria_to_create", 0) or 0)
    for index, window in enumerate((campaign_plan.get("schedule") or [])[:schedule_count]):
        compiled.creates.append(Operation(
            "campaign_criterion_ad_schedule", "create", f"ad_schedule::{index}",
            {"start": window.get("start"), "end": window.get("end"), "day": window.get("day")},
        ))

    # Language criteria only when explicitly listed. There is no default.
    for language_id in campaign_plan.get("language_constant_ids") or []:
        compiled.creates.append(Operation(
            "campaign_criterion_language", "create", f"language::{language_id}",
            {"language_constant": f"languageConstants/{language_id}"},
        ))

    for ad_group in campaign_plan["ad_groups"]:
        ag_name = ad_group["name"]
        compiled.creates.append(Operation(
            "ad_group", "create", f"ad_group::{ag_name}",
            {"name": ag_name, "status": "PAUSED"},
        ))
        for keyword in ad_group["keywords"]:
            compiled.creates.append(Operation(
                "ad_group_criterion_keyword", "create",
                f"keyword::{ag_name}::{keyword['text']}::{keyword['match_type']}",
                {"ad_group": ag_name, "text": keyword["text"],
                 "match_type": keyword["match_type"], "status": "PAUSED"},
            ))
        for negative in ad_group.get("cross_negatives") or []:
            compiled.creates.append(Operation(
                "ad_group_criterion_negative_keyword", "create",
                f"ad_group_negative::{ag_name}::{negative['text']}",
                {"ad_group": ag_name, "text": negative["text"],
                 "match_type": negative["match_type"]},
            ))
        for ad in ad_group["ads"]:
            compiled.creates.append(Operation(
                "ad_group_ad_rsa", "create", f"rsa::{ag_name}::{ad['id']}",
                {"ad_group": ag_name, "status": "PAUSED",
                 "final_url": ad_group["final_url"],
                 "headlines": [{"text": _asset_text(h), "pin": _asset_pin(h)}
                               for h in ad["headlines"]],
                 "descriptions": [_asset_text(d) for d in ad["descriptions"]]},
            ))

    if asset_manifest:
        am = asset_manifest["asset_manifest"]
        for sitelink in am["sitelinks"].get("create") or []:
            compiled.creates.append(Operation(
                "asset_sitelink_new", "create", f"asset_sitelink::{sitelink['ref']}",
                {"link_text": sitelink["link_text"], "description1": sitelink["description1"],
                 "description2": sitelink["description2"], "final_url": sitelink["final_url"]},
            ))
        for callout in am["callouts"].get("create") or []:
            compiled.creates.append(Operation(
                "asset_callout_new", "create", f"asset_callout::{callout['ref']}",
                {"text": callout["text"]},
            ))
        for snippet in am["structured_snippets"].get("create") or []:
            compiled.creates.append(Operation(
                "asset_structured_snippet_new", "create", f"asset_snippet::{snippet['ref']}",
                {"header": snippet["header"],
                 "values": [v["text"] for v in snippet["values"]]},
            ))

        # One association per new asset plus one per reused asset. Every association is
        # created PAUSED; the asset resource itself carries no serving status.
        for sitelink in am["sitelinks"].get("create") or []:
            compiled.creates.append(Operation(
                "campaign_asset_association", "create", f"campaign_asset::SITELINK::{sitelink['ref']}",
                {"field_type": "SITELINK", "status": "PAUSED", "asset_ref": sitelink["ref"]},
            ))
        for callout in am["callouts"].get("create") or []:
            compiled.creates.append(Operation(
                "campaign_asset_association", "create", f"campaign_asset::CALLOUT::{callout['ref']}",
                {"field_type": "CALLOUT", "status": "PAUSED", "asset_ref": callout["ref"]},
            ))
        for reused in am["callouts"].get("reuse") or []:
            compiled.creates.append(Operation(
                "campaign_asset_association", "create",
                f"campaign_asset::CALLOUT::existing::{reused['id']}",
                {"field_type": "CALLOUT", "status": "PAUSED",
                 "existing_asset_id": str(reused["id"])},
            ))
        for snippet in am["structured_snippets"].get("create") or []:
            compiled.creates.append(Operation(
                "campaign_asset_association", "create",
                f"campaign_asset::STRUCTURED_SNIPPET::{snippet['ref']}",
                {"field_type": "STRUCTURED_SNIPPET", "status": "PAUSED",
                 "asset_ref": snippet["ref"]},
            ))

    goal = plan.get("conversion_goal_implementation") or {}
    ccg = goal.get("custom_conversion_goal") or {}
    if ccg.get("required"):
        compiled.creates.append(Operation(
            "custom_conversion_goal", "create", "custom_conversion_goal",
            {"name": ccg["proposed_name"], "status": ccg["status"],
             "conversion_actions": list(ccg["conversion_actions"])},
        ))

    isolation = plan.get("campaign_conversion_goal_isolation") or {}
    for update in isolation.get("planned_updates") or []:
        compiled.updates.append(Operation(
            "campaign_conversion_goal_biddable_false", "update",
            f"campaign_conversion_goal::{update['category']}::{update['origin']}",
            {"category": update["category"], "origin": update["origin"],
             "biddable": False, "update_mask": list(update["update_mask"])},
        ))

    config = goal.get("conversion_goal_campaign_config") or {}
    if config:
        compiled.updates.append(Operation(
            "conversion_goal_campaign_config", "update", "conversion_goal_campaign_config",
            {"update_mask": list(config["update_mask"]),
             "fields_to_set": dict(config["fields_to_set"])},
        ))

    return compiled


def assert_counts_match(plan: dict[str, Any], compiled: CompiledPlan) -> None:
    """Fail unless the compiled inventory equals the plan's declared inventory exactly."""
    declared = plan["create_paused_objects"]
    errors: list[str] = []

    compiled_counts = compiled.counts()
    for mutation_type, expected in declared["creates"].items():
        if mutation_type == "total_creates":
            continue
        actual = compiled_counts.get(mutation_type, 0)
        if actual != expected:
            errors.append(f"{mutation_type}: declared {expected}, compiled {actual}")
    for mutation_type, expected in declared["updates"].items():
        if mutation_type == "total_updates":
            continue
        actual = compiled_counts.get(mutation_type, 0)
        if actual != expected:
            errors.append(f"{mutation_type}: declared {expected}, compiled {actual}")

    declared_types = (
        {k for k in declared["creates"] if k != "total_creates"}
        | {k for k in declared["updates"] if k != "total_updates"}
    )
    for mutation_type in compiled_counts:
        if mutation_type not in declared_types:
            errors.append(f"{mutation_type}: compiled but not declared in the plan")

    if len(compiled.creates) != declared["creates"]["total_creates"]:
        errors.append(
            f"total creates: declared {declared['creates']['total_creates']}, "
            f"compiled {len(compiled.creates)}"
        )
    if len(compiled.updates) != declared["updates"]["total_updates"]:
        errors.append(
            f"total updates: declared {declared['updates']['total_updates']}, "
            f"compiled {len(compiled.updates)}"
        )
    if len(compiled.operations) != declared["total_mutations"]:
        errors.append(
            f"total mutations: declared {declared['total_mutations']}, "
            f"compiled {len(compiled.operations)}"
        )

    if errors:
        raise PlanCompileError(
            "Compiled inventory does not match the declared plan:\n- " + "\n- ".join(errors)
        )
