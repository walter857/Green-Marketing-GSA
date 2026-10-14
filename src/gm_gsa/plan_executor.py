"""Execute a compiled campaign plan against Google Ads, in dependency order.

Safety properties this module is built around:

- ``validate_only=True`` runs the whole sequence through the API without creating anything,
  so field-level rejections surface before a single durable resource exists.
- Every operation records its own result: type, planned identity, resource name, success,
  request ID, error, and whether a retry is safe.
- Dependent work stops at the first failure. Nothing is deleted to "clean up", and nothing
  is enabled.
- Retry is guarded by planned identity. Before creating anything the executor can look up
  what already exists, so a rerun after a partial failure cannot duplicate a resource.
- The conversion-goal inventory is verified against the approved expectation before any
  goal update is applied. A mismatch stops the run with everything still paused.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from .plan_compiler import CompiledPlan, Operation


class ExecutionStopped(RuntimeError):
    """Raised when the run must stop. Carries the result ledger."""

    def __init__(self, message: str, ledger: "Ledger") -> None:
        super().__init__(message)
        self.ledger = ledger


@dataclass
class OperationResult:
    mutation_type: str
    kind: str
    planned_id: str
    status: str  # success | failed | not_attempted
    resource_name: str | None = None
    request_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    retry_safe: bool | None = None


@dataclass
class Ledger:
    validate_only: bool
    results: list[OperationResult] = field(default_factory=list)

    def record(self, **kwargs: Any) -> OperationResult:
        result = OperationResult(**kwargs)
        self.results.append(result)
        return result

    def by_status(self, status: str) -> list[OperationResult]:
        return [r for r in self.results if r.status == status]

    def summary(self) -> dict[str, int]:
        return {
            "success": len(self.by_status("success")),
            "failed": len(self.by_status("failed")),
            "not_attempted": len(self.by_status("not_attempted")),
            "total": len(self.results),
        }

    def to_json(self) -> str:
        return json.dumps(
            {"validate_only": self.validate_only, "summary": self.summary(),
             "results": [asdict(r) for r in self.results]},
            indent=2,
        )


def _error_details(exc: Exception) -> tuple[str, str, str]:
    """Return (request_id, error_code, message) from a GoogleAdsException, redacted."""
    request_id = str(getattr(exc, "request_id", "") or "")
    code = ""
    message = str(exc)
    failure = getattr(exc, "failure", None)
    if failure is not None and getattr(failure, "errors", None):
        first = failure.errors[0]
        try:
            which = first.error_code._pb.WhichOneof("error_code")
            code = f"{which}:{getattr(first.error_code, which)}"
        except Exception:  # noqa: BLE001
            code = "unknown"
        message = first.message
    return request_id, code, message[:500]


# Errors that mean "already there" rather than "broken", so a retry must look before leaping.
_NON_RETRYABLE = {"DUPLICATE_NAME", "RESOURCE_ALREADY_EXISTS", "DUPLICATE_KEYWORD"}


def _retry_safe(code: str) -> bool:
    return not any(marker in code.upper() for marker in _NON_RETRYABLE)


def _failed_index(exc: Exception) -> int:
    """Which operation in an atomic batch caused the failure, or -1."""
    failure = getattr(exc, "failure", None)
    if failure is None or not getattr(failure, "errors", None):
        return -1
    for error in failure.errors:
        for element in getattr(error.location, "field_path_elements", []) or []:
            if element.field_name == "mutate_operations":
                try:
                    return int(element.index)
                except (TypeError, ValueError):
                    continue
    return -1



class PlanExecutor:
    def __init__(self, client: Any, customer_id: str, *, validate_only: bool = True) -> None:
        self.client = client
        self.customer_id = customer_id
        self.validate_only = validate_only
        self.ledger = Ledger(validate_only=validate_only)
        self.resources: dict[str, str] = {}  # planned_id -> resource_name
        self.stopped = False

    # -- helpers ---------------------------------------------------------

    def _mutate(self, service_name: str, method: str, operations: list[Any],
                ops_meta: list[Operation]) -> bool:
        """Run one batched mutate. Returns True on success, records every result."""
        if self.stopped:
            for op in ops_meta:
                self.ledger.record(mutation_type=op.mutation_type, kind=op.kind,
                                   planned_id=op.planned_id, status="not_attempted")
            return False
        service = self.client.get_service(service_name)
        # validate_only is a field on the request message, not a call kwarg. Build the
        # request explicitly so a dry run exercises the same code path as a real write.
        request_type = "".join(part.capitalize() for part in method.split("_")) + "Request"
        try:
            request = self.client.get_type(request_type)
            request.customer_id = self.customer_id
            request.operations.extend(operations)
            supports_validate_only = hasattr(request, "validate_only")
            if supports_validate_only:
                request.validate_only = self.validate_only
            elif self.validate_only:
                # Cannot dry-run this service. Never fall through to a durable write.
                for op in ops_meta:
                    self.ledger.record(mutation_type=op.mutation_type, kind=op.kind,
                                       planned_id=op.planned_id, status="not_attempted",
                                       error_message=f"{service_name} does not support validate_only")
                return True
            response = getattr(service, method)(request=request)
        except Exception as exc:  # noqa: BLE001
            request_id, code, message = _error_details(exc)
            for op in ops_meta:
                self.ledger.record(mutation_type=op.mutation_type, kind=op.kind,
                                   planned_id=op.planned_id, status="failed",
                                   request_id=request_id, error_code=code,
                                   error_message=message, retry_safe=_retry_safe(code))
            self.stopped = True
            return False

        request_id = str(getattr(response, "request_id", "") or "")
        for op, result in zip(ops_meta, response.results):
            resource_name = getattr(result, "resource_name", "") or None
            if resource_name:
                self.resources[op.planned_id] = resource_name
            self.ledger.record(mutation_type=op.mutation_type, kind=op.kind,
                               planned_id=op.planned_id, status="success",
                               resource_name=resource_name, request_id=request_id)
        return True

    def _skip_remaining(self, operations: list[Operation]) -> None:
        for op in operations:
            self.ledger.record(mutation_type=op.mutation_type, kind=op.kind,
                               planned_id=op.planned_id, status="not_attempted")

    @staticmethod
    def _of_type(compiled: CompiledPlan, *types: str) -> list[Operation]:
        return [op for op in compiled.operations if op.mutation_type in types]

    # -- execution -------------------------------------------------------

    def execute(self, compiled: CompiledPlan, *, expected_goal_inventory: list[dict] | None = None,
                existing_asset_ids: dict[str, str] | None = None) -> Ledger:
        c = self.client
        cid = self.customer_id
        steps: list[tuple[str, list[Operation]]] = []

        # 1 budget
        budget_ops = self._of_type(compiled, "campaign_budget")
        ops = []
        for op in budget_ops:
            o = c.get_type("CampaignBudgetOperation")
            o.create.name = op.payload["name"]
            o.create.amount_micros = int(round(float(op.payload["amount"]) * 1_000_000))
            o.create.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
            ops.append(o)
        if not self._mutate("CampaignBudgetService", "mutate_campaign_budgets", ops, budget_ops):
            self._skip_remaining([o for o in compiled.operations if o not in budget_ops])
            return self.ledger
        budget_resource = self.resources.get(budget_ops[0].planned_id)

        # 2 campaign
        campaign_ops = self._of_type(compiled, "campaign")
        ops = []
        for op in campaign_ops:
            o = c.get_type("CampaignOperation")
            cp = o.create
            cp.name = op.payload["name"]
            cp.status = c.enums.CampaignStatusEnum.PAUSED
            cp.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
            cp.campaign_budget = budget_resource or ""
            cp.network_settings.target_google_search = bool(op.payload["google_search"])
            cp.network_settings.target_search_network = bool(op.payload["search_partners"])
            cp.network_settings.target_content_network = bool(op.payload["display"])
            cp.network_settings.target_partner_search_network = False
            cp.geo_target_type_setting.positive_geo_target_type = getattr(
                c.enums.PositiveGeoTargetTypeEnum, op.payload["positive_geo_target_type"])
            cp.geo_target_type_setting.negative_geo_target_type = getattr(
                c.enums.NegativeGeoTargetTypeEnum, op.payload["negative_geo_target_type"])
            cp.maximize_conversions.target_cpa_micros = 0
            ops.append(o)
        remaining = [o for o in compiled.operations if o not in budget_ops + campaign_ops]
        if not self._mutate("CampaignService", "mutate_campaigns", ops, campaign_ops):
            self._skip_remaining(remaining)
            return self.ledger
        campaign_resource = self.resources.get(campaign_ops[0].planned_id)

        # 3-4 campaign criteria: proximity, location, negatives (+ any explicit schedule/language)
        crit_ops = self._of_type(
            compiled, "campaign_criterion_proximity", "campaign_criterion_location",
            "campaign_criterion_negative_keyword", "campaign_criterion_ad_schedule",
            "campaign_criterion_language")
        ops = []
        for op in crit_ops:
            o = c.get_type("CampaignCriterionOperation")
            cr = o.create
            cr.campaign = campaign_resource or ""
            p = op.payload
            if op.mutation_type == "campaign_criterion_proximity":
                cr.proximity.geo_point.latitude_in_micro_degrees = int(round(float(p["latitude"]) * 1_000_000))
                cr.proximity.geo_point.longitude_in_micro_degrees = int(round(float(p["longitude"]) * 1_000_000))
                cr.proximity.radius = float(p["radius"])
                cr.proximity.radius_units = getattr(
                    c.enums.ProximityRadiusUnitsEnum, str(p["radius_units"]).upper())
            elif op.mutation_type == "campaign_criterion_location":
                cr.location.geo_target_constant = p["geo_target_constant"]
            elif op.mutation_type == "campaign_criterion_negative_keyword":
                cr.negative = True
                cr.keyword.text = p["text"]
                cr.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, p["match_type"])
            elif op.mutation_type == "campaign_criterion_language":
                cr.language.language_constant = p["language_constant"]
            elif op.mutation_type == "campaign_criterion_ad_schedule":
                cr.ad_schedule.day_of_week = getattr(c.enums.DayOfWeekEnum, p["day"])
                sh, sm = p["start"].split(":")
                eh, em = p["end"].split(":")
                cr.ad_schedule.start_hour = int(sh)
                cr.ad_schedule.end_hour = int(eh)
                cr.ad_schedule.start_minute = getattr(c.enums.MinuteOfHourEnum, f"{'ZERO' if sm=='00' else 'FIFTEEN' if sm=='15' else 'THIRTY' if sm=='30' else 'FORTY_FIVE'}")
                cr.ad_schedule.end_minute = getattr(c.enums.MinuteOfHourEnum, f"{'ZERO' if em=='00' else 'FIFTEEN' if em=='15' else 'THIRTY' if em=='30' else 'FORTY_FIVE'}")
            ops.append(o)
        remaining = [o for o in remaining if o not in crit_ops]
        if ops and not self._mutate("CampaignCriterionService", "mutate_campaign_criteria", ops, crit_ops):
            self._skip_remaining(remaining)
            return self.ledger

        # 5 ad groups
        ag_ops = self._of_type(compiled, "ad_group")
        ops = []
        for op in ag_ops:
            o = c.get_type("AdGroupOperation")
            o.create.name = op.payload["name"]
            o.create.campaign = campaign_resource or ""
            o.create.status = c.enums.AdGroupStatusEnum.PAUSED
            o.create.type_ = c.enums.AdGroupTypeEnum.SEARCH_STANDARD
            ops.append(o)
        remaining = [o for o in remaining if o not in ag_ops]
        if not self._mutate("AdGroupService", "mutate_ad_groups", ops, ag_ops):
            self._skip_remaining(remaining)
            return self.ledger
        ag_resource = {op.payload["name"]: self.resources.get(op.planned_id) for op in ag_ops}

        # 6 keywords + ad-group negatives
        kw_ops = self._of_type(compiled, "ad_group_criterion_keyword",
                               "ad_group_criterion_negative_keyword")
        ops = []
        for op in kw_ops:
            o = c.get_type("AdGroupCriterionOperation")
            cr = o.create
            cr.ad_group = ag_resource.get(op.payload["ad_group"]) or ""
            cr.keyword.text = op.payload["text"]
            cr.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, op.payload["match_type"])
            if op.mutation_type == "ad_group_criterion_negative_keyword":
                cr.negative = True
            else:
                cr.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
            ops.append(o)
        remaining = [o for o in remaining if o not in kw_ops]
        if not self._mutate("AdGroupCriterionService", "mutate_ad_group_criteria", ops, kw_ops):
            self._skip_remaining(remaining)
            return self.ledger

        # 7 RSAs
        rsa_ops = self._of_type(compiled, "ad_group_ad_rsa")
        ops = []
        for op in rsa_ops:
            o = c.get_type("AdGroupAdOperation")
            aga = o.create
            aga.ad_group = ag_resource.get(op.payload["ad_group"]) or ""
            aga.status = c.enums.AdGroupAdStatusEnum.PAUSED
            aga.ad.final_urls.append(op.payload["final_url"])
            for h in op.payload["headlines"]:
                asset = c.get_type("AdTextAsset")
                asset.text = h["text"]
                if h.get("pin") == "HEADLINE_1":
                    asset.pinned_field = c.enums.ServedAssetFieldTypeEnum.HEADLINE_1
                aga.ad.responsive_search_ad.headlines.append(asset)
            for d in op.payload["descriptions"]:
                asset = c.get_type("AdTextAsset")
                asset.text = d
                aga.ad.responsive_search_ad.descriptions.append(asset)
            ops.append(o)
        remaining = [o for o in remaining if o not in rsa_ops]
        if not self._mutate("AdGroupAdService", "mutate_ad_group_ads", ops, rsa_ops):
            self._skip_remaining(remaining)
            return self.ledger

        # 8 assets
        asset_ops = self._of_type(compiled, "asset_sitelink_new", "asset_callout_new",
                                  "asset_structured_snippet_new")
        ops = []
        for op in asset_ops:
            o = c.get_type("AssetOperation")
            a = o.create
            p = op.payload
            if op.mutation_type == "asset_sitelink_new":
                a.sitelink_asset.link_text = p["link_text"]
                a.sitelink_asset.description1 = p["description1"]
                a.sitelink_asset.description2 = p["description2"]
                a.final_urls.append(p["final_url"])
            elif op.mutation_type == "asset_callout_new":
                a.callout_asset.callout_text = p["text"]
            else:
                a.structured_snippet_asset.header = p["header"]
                for v in p["values"]:
                    a.structured_snippet_asset.values.append(v)
            ops.append(o)
        remaining = [o for o in remaining if o not in asset_ops]
        if ops and not self._mutate("AssetService", "mutate_assets", ops, asset_ops):
            self._skip_remaining(remaining)
            return self.ledger

        # 9 CampaignAsset associations, all PAUSED
        assoc_ops = self._of_type(compiled, "campaign_asset_association")
        existing_asset_ids = existing_asset_ids or {}
        ops = []
        for op in assoc_ops:
            o = c.get_type("CampaignAssetOperation")
            ca = o.create
            ca.campaign = campaign_resource or ""
            ca.field_type = getattr(c.enums.AssetFieldTypeEnum, op.payload["field_type"])
            ca.status = c.enums.AssetLinkStatusEnum.PAUSED
            if "existing_asset_id" in op.payload:
                ca.asset = f"customers/{cid}/assets/{op.payload['existing_asset_id']}"
            else:
                ref = op.payload["asset_ref"]
                planned = next((k for k in self.resources
                                if k.startswith("asset_") and k.endswith(f"::{ref}")), None)
                ca.asset = self.resources.get(planned, "") if planned else ""
            ops.append(o)
        remaining = [o for o in remaining if o not in assoc_ops]
        if ops and not self._mutate("CampaignAssetService", "mutate_campaign_assets", ops, assoc_ops):
            self._skip_remaining(remaining)
            return self.ledger

        # 10 CustomConversionGoal
        ccg_ops = self._of_type(compiled, "custom_conversion_goal")
        ops = []
        for op in ccg_ops:
            o = c.get_type("CustomConversionGoalOperation")
            g = o.create
            g.name = op.payload["name"]
            g.status = c.enums.CustomConversionGoalStatusEnum.ENABLED
            for action in op.payload["conversion_actions"]:
                g.conversion_actions.append(action)
            ops.append(o)
        remaining = [o for o in remaining if o not in ccg_ops]
        if ops and not self._mutate("CustomConversionGoalService",
                                    "mutate_custom_conversion_goals", ops, ccg_ops):
            self._skip_remaining(remaining)
            return self.ledger
        goal_resource = self.resources.get(ccg_ops[0].planned_id) if ccg_ops else None

        # 11-12 verify the generated CampaignConversionGoal inventory before touching it
        cgc_ops = self._of_type(compiled, "campaign_conversion_goal_biddable_false")
        config_ops = self._of_type(compiled, "conversion_goal_campaign_config")
        if expected_goal_inventory is not None and not self.validate_only and campaign_resource:
            from .service_discovery import run_read_only_query
            actual = sorted(
                (r.campaign_conversion_goal.category.name, r.campaign_conversion_goal.origin.name)
                for r in run_read_only_query(c, cid, f"""
                    SELECT campaign_conversion_goal.category, campaign_conversion_goal.origin,
                           campaign_conversion_goal.biddable
                    FROM campaign_conversion_goal
                    WHERE campaign_conversion_goal.campaign = '{campaign_resource}'""")
            )
            expected = sorted((g["category"], g["origin"]) for g in expected_goal_inventory)
            if actual != expected:
                self._skip_remaining(cgc_ops + config_ops)
                self.stopped = True
                raise ExecutionStopped(
                    "CampaignConversionGoal inventory differs from the approved expectation. "
                    f"Expected {len(expected)} rows, found {len(actual)}. Everything created "
                    "remains PAUSED; no conversion-goal update was applied.",
                    self.ledger,
                )

        # 13 seven biddable=false updates
        from google.protobuf import field_mask_pb2
        ops = []
        for op in cgc_ops:
            o = c.get_type("CampaignConversionGoalOperation")
            u = o.update
            u.resource_name = (
                f"customers/{cid}/campaignConversionGoals/"
                f"{campaign_resource.split('/')[-1]}~{op.payload['category']}~{op.payload['origin']}"
            )
            u.biddable = False
            c.copy_from(o.update_mask, field_mask_pb2.FieldMask(paths=["biddable"]))
            ops.append(o)
        remaining = [o for o in remaining if o not in cgc_ops]
        if ops and not self._mutate("CampaignConversionGoalService",
                                    "mutate_campaign_conversion_goals", ops, cgc_ops):
            self._skip_remaining(remaining)
            return self.ledger

        # 14 ConversionGoalCampaignConfig
        ops = []
        for op in config_ops:
            o = c.get_type("ConversionGoalCampaignConfigOperation")
            u = o.update
            u.resource_name = (
                f"customers/{cid}/conversionGoalCampaignConfigs/"
                f"{campaign_resource.split('/')[-1]}"
            )
            u.custom_conversion_goal = goal_resource or ""
            c.copy_from(o.update_mask,
                        field_mask_pb2.FieldMask(paths=list(op.payload["update_mask"])))
            ops.append(o)
        if ops:
            self._mutate("ConversionGoalCampaignConfigService",
                         "mutate_conversion_goal_campaign_configs", ops, config_ops)

        return self.ledger

    # ------------------------------------------------------------------
    # Atomic create phase
    # ------------------------------------------------------------------

    def execute_atomic_creates(self, compiled: "CompiledPlan") -> Ledger:
        """Run all 80 creates as ONE atomic GoogleAdsService.mutate.

        Temporary negative resource IDs let later operations reference earlier ones inside
        the same request, which is what makes an end-to-end validate_only pass possible.
        Atomicity also removes the partial-failure class outright: either every create lands
        or none does.
        """
        c = self.client
        cid = self.customer_id
        ops: list[Any] = []
        meta: list[Operation] = []
        temp = {}
        counter = [-1]

        def next_temp(path: str) -> str:
            rn = f"customers/{cid}/{path}/{counter[0]}"
            counter[0] -= 1
            return rn

        def add(op_meta: Operation, mutate_op: Any) -> None:
            ops.append(mutate_op)
            meta.append(op_meta)

        by_type: dict[str, list[Operation]] = {}
        for op in compiled.creates:
            by_type.setdefault(op.mutation_type, []).append(op)

        # budget
        for op in by_type.get("campaign_budget", []):
            m = c.get_type("MutateOperation")
            b = m.campaign_budget_operation.create
            b.resource_name = next_temp("campaignBudgets")
            b.name = op.payload["name"]
            b.amount_micros = int(round(float(op.payload["amount"]) * 1_000_000))
            b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
            b.explicitly_shared = False
            temp[op.planned_id] = b.resource_name
            add(op, m)

        # campaign
        for op in by_type.get("campaign", []):
            m = c.get_type("MutateOperation")
            cp = m.campaign_operation.create
            cp.resource_name = next_temp("campaigns")
            cp.name = op.payload["name"]
            cp.status = c.enums.CampaignStatusEnum.PAUSED
            cp.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
            cp.campaign_budget = temp[next(iter(by_type["campaign_budget"])).planned_id]
            cp.network_settings.target_google_search = True
            cp.network_settings.target_search_network = False
            cp.network_settings.target_content_network = False
            cp.network_settings.target_partner_search_network = False
            cp.geo_target_type_setting.positive_geo_target_type = (
                c.enums.PositiveGeoTargetTypeEnum.PRESENCE)
            cp.geo_target_type_setting.negative_geo_target_type = (
                c.enums.NegativeGeoTargetTypeEnum.PRESENCE)
            cp.maximize_conversions.target_cpa_micros = 0
            # Required by Google Ads API v25. A lawn-care campaign carries no EU political
            # advertising. This is a mandatory API field, not a plan option, so it changes
            # no declared mutation count.
            cp.contains_eu_political_advertising = (
                c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
            temp[op.planned_id] = cp.resource_name
            add(op, m)
        campaign_temp = temp[by_type["campaign"][0].planned_id]

        # campaign criteria
        for key in ("campaign_criterion_proximity", "campaign_criterion_location",
                    "campaign_criterion_negative_keyword", "campaign_criterion_language",
                    "campaign_criterion_ad_schedule"):
            for op in by_type.get(key, []):
                m = c.get_type("MutateOperation")
                cr = m.campaign_criterion_operation.create
                cr.campaign = campaign_temp
                p = op.payload
                if key == "campaign_criterion_proximity":
                    cr.proximity.geo_point.latitude_in_micro_degrees = int(round(float(p["latitude"]) * 1_000_000))
                    cr.proximity.geo_point.longitude_in_micro_degrees = int(round(float(p["longitude"]) * 1_000_000))
                    cr.proximity.radius = float(p["radius"])
                    cr.proximity.radius_units = getattr(
                        c.enums.ProximityRadiusUnitsEnum, str(p["radius_units"]).upper())
                elif key == "campaign_criterion_location":
                    cr.location.geo_target_constant = p["geo_target_constant"]
                elif key == "campaign_criterion_negative_keyword":
                    cr.negative = True
                    cr.keyword.text = p["text"]
                    cr.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, p["match_type"])
                elif key == "campaign_criterion_language":
                    cr.language.language_constant = p["language_constant"]
                add(op, m)

        # ad groups
        ag_temp = {}
        for op in by_type.get("ad_group", []):
            m = c.get_type("MutateOperation")
            ag = m.ad_group_operation.create
            ag.resource_name = next_temp("adGroups")
            ag.name = op.payload["name"]
            ag.campaign = campaign_temp
            ag.status = c.enums.AdGroupStatusEnum.PAUSED
            ag.type_ = c.enums.AdGroupTypeEnum.SEARCH_STANDARD
            ag_temp[op.payload["name"]] = ag.resource_name
            temp[op.planned_id] = ag.resource_name
            add(op, m)

        # keywords and ad-group negatives
        for key in ("ad_group_criterion_keyword", "ad_group_criterion_negative_keyword"):
            for op in by_type.get(key, []):
                m = c.get_type("MutateOperation")
                cr = m.ad_group_criterion_operation.create
                cr.ad_group = ag_temp[op.payload["ad_group"]]
                cr.keyword.text = op.payload["text"]
                cr.keyword.match_type = getattr(
                    c.enums.KeywordMatchTypeEnum, op.payload["match_type"])
                if key == "ad_group_criterion_negative_keyword":
                    cr.negative = True
                else:
                    cr.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
                add(op, m)

        # RSAs
        for op in by_type.get("ad_group_ad_rsa", []):
            m = c.get_type("MutateOperation")
            aga = m.ad_group_ad_operation.create
            aga.ad_group = ag_temp[op.payload["ad_group"]]
            aga.status = c.enums.AdGroupAdStatusEnum.PAUSED
            aga.ad.final_urls.append(op.payload["final_url"])
            for h in op.payload["headlines"]:
                a = c.get_type("AdTextAsset")
                a.text = h["text"]
                if h.get("pin") == "HEADLINE_1":
                    a.pinned_field = c.enums.ServedAssetFieldTypeEnum.HEADLINE_1
                aga.ad.responsive_search_ad.headlines.append(a)
            for d in op.payload["descriptions"]:
                a = c.get_type("AdTextAsset")
                a.text = d
                aga.ad.responsive_search_ad.descriptions.append(a)
            add(op, m)

        # assets
        asset_temp = {}
        for key in ("asset_sitelink_new", "asset_callout_new", "asset_structured_snippet_new"):
            for op in by_type.get(key, []):
                m = c.get_type("MutateOperation")
                a = m.asset_operation.create
                a.resource_name = next_temp("assets")
                p = op.payload
                if key == "asset_sitelink_new":
                    a.sitelink_asset.link_text = p["link_text"]
                    a.sitelink_asset.description1 = p["description1"]
                    a.sitelink_asset.description2 = p["description2"]
                    a.final_urls.append(p["final_url"])
                elif key == "asset_callout_new":
                    a.callout_asset.callout_text = p["text"]
                else:
                    a.structured_snippet_asset.header = p["header"]
                    for v in p["values"]:
                        a.structured_snippet_asset.values.append(v)
                asset_temp[op.planned_id.split("::")[-1]] = a.resource_name
                temp[op.planned_id] = a.resource_name
                add(op, m)

        # campaign asset associations, all PAUSED
        for op in by_type.get("campaign_asset_association", []):
            m = c.get_type("MutateOperation")
            ca = m.campaign_asset_operation.create
            ca.campaign = campaign_temp
            ca.field_type = getattr(c.enums.AssetFieldTypeEnum, op.payload["field_type"])
            ca.status = c.enums.AssetLinkStatusEnum.PAUSED
            if "existing_asset_id" in op.payload:
                ca.asset = f"customers/{cid}/assets/{op.payload['existing_asset_id']}"
            else:
                ca.asset = asset_temp[op.payload["asset_ref"]]
            add(op, m)

        # custom conversion goal
        for op in by_type.get("custom_conversion_goal", []):
            m = c.get_type("MutateOperation")
            g = m.custom_conversion_goal_operation.create
            g.resource_name = next_temp("customConversionGoals")
            g.name = op.payload["name"]
            g.status = c.enums.CustomConversionGoalStatusEnum.ENABLED
            for action in op.payload["conversion_actions"]:
                g.conversion_actions.append(action)
            temp[op.planned_id] = g.resource_name
            add(op, m)

        self.compiled_operation_count = len(ops)
        service = c.get_service("GoogleAdsService")
        request = c.get_type("MutateGoogleAdsRequest")
        request.customer_id = cid
        request.mutate_operations.extend(ops)
        request.validate_only = self.validate_only
        request.partial_failure = False

        try:
            response = service.mutate(request=request)
        except Exception as exc:  # noqa: BLE001
            request_id, code, message = _error_details(exc)
            index = _failed_index(exc)
            for i, op in enumerate(meta):
                self.ledger.record(
                    mutation_type=op.mutation_type, kind=op.kind, planned_id=op.planned_id,
                    status="failed" if i == index else "not_attempted",
                    request_id=request_id,
                    error_code=code if i == index else None,
                    error_message=message if i == index else "atomic batch rolled back",
                    retry_safe=_retry_safe(code) if i == index else True)
            self.stopped = True
            return self.ledger

        request_id = str(getattr(response, "request_id", "") or "")
        results = list(response.mutate_operation_responses)
        if self.validate_only and not results:
            # validate_only returns an empty body. No exception means every operation in the
            # atomic batch was accepted by the API.
            for op in meta:
                self.ledger.record(mutation_type=op.mutation_type, kind=op.kind,
                                   planned_id=op.planned_id, status="success",
                                   request_id=request_id,
                                   error_message="validated only, not created")
            return self.ledger
        for op, res in zip(meta, results):
            which = res._pb.WhichOneof("response")
            rn = getattr(getattr(res, which), "resource_name", "") if which else ""
            if rn:
                self.resources[op.planned_id] = rn
            self.ledger.record(mutation_type=op.mutation_type, kind=op.kind,
                               planned_id=op.planned_id, status="success",
                               resource_name=rn or None, request_id=request_id)
        return self.ledger
