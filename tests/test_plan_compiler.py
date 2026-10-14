"""Regression proofs for plan compilation and publisher capability.

Each test pins down one way the executor could silently diverge from an approved plan. The
gap these were written for was real: the previous publisher would have created 1 of 6
location targets, invented two unplanned criteria, and skipped every asset and conversion-goal
mutation, while the plan still carried a valid-looking fingerprint.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.plan_compiler import (  # noqa: E402
    PlanCompileError,
    assert_counts_match,
    compile_plan,
)
from gm_gsa.publisher_capability import (  # noqa: E402
    HANDLERS,
    PublisherCapabilityError,
    assert_publishable,
    can_issue_fingerprint,
    unsupported_types,
)

CLIENT = ROOT / "clients" / "ekg-lawn-services"
PLAN = load_yaml(CLIENT / "plans" / "campaign-blueprint-2026-08-14.yaml")
ASSETS = load_yaml(CLIENT / "plans" / "asset-manifest-2026-08-14.yaml")


def compiled():
    return compile_plan(PLAN, ASSETS)


def counts():
    return compiled().counts()


class ProximityTests(unittest.TestCase):
    def test_five_proximity_targets_produce_five_criteria(self):
        self.assertEqual(counts()["campaign_criterion_proximity"], 5)

    def test_no_proximity_target_is_silently_dropped(self):
        planned = {t["id"] for t in PLAN["campaigns"][0]["location"]["proximity"]}
        got = {op.planned_id.split("::")[1] for op in compiled().creates
               if op.mutation_type == "campaign_criterion_proximity"}
        self.assertEqual(got, planned)
        self.assertEqual(len(got), 5)

    def test_each_coordinate_and_radius_survives_exactly(self):
        by_id = {t["id"]: t for t in PLAN["campaigns"][0]["location"]["proximity"]}
        for op in compiled().creates:
            if op.mutation_type != "campaign_criterion_proximity":
                continue
            src = by_id[op.planned_id.split("::")[1]]
            self.assertEqual(op.payload["latitude"], src["latitude"])
            self.assertEqual(op.payload["longitude"], src["longitude"])
            self.assertEqual(op.payload["radius"], src["radius"])

    def test_miles_are_never_converted_to_kilometres(self):
        for op in compiled().creates:
            if op.mutation_type == "campaign_criterion_proximity":
                self.assertEqual(op.payload["radius_units"], "MILES")
                self.assertEqual(op.payload["radius"], 2.0)

    def test_the_single_radius_slot_is_not_used_as_a_source(self):
        """The old publisher read location.radius and would have produced 0 or 1 target."""
        self.assertNotIn("radius", PLAN["campaigns"][0]["location"])

    def test_one_geo_target_constant_criterion(self):
        self.assertEqual(counts()["campaign_criterion_location"], 1)


class NoUnplannedDefaultsTests(unittest.TestCase):
    def test_zero_planned_schedules_produce_zero_ad_schedule_criteria(self):
        self.assertEqual(PLAN["campaigns"][0]["ad_schedule_criteria_to_create"], 0)
        self.assertEqual(counts().get("campaign_criterion_ad_schedule", 0), 0)

    def test_a_schema_only_schedule_entry_creates_nothing(self):
        """The plan carries one schedule entry purely to satisfy the schema validator."""
        self.assertEqual(len(PLAN["campaigns"][0]["schedule"]), 1)
        self.assertEqual(counts().get("campaign_criterion_ad_schedule", 0), 0)

    def test_schedules_are_created_when_explicitly_requested(self):
        plan = copy.deepcopy(PLAN)
        plan["campaigns"][0]["ad_schedule_criteria_to_create"] = 1
        self.assertEqual(compile_plan(plan, ASSETS).counts()
                         .get("campaign_criterion_ad_schedule", 0), 1)

    def test_zero_planned_language_criteria_produce_zero(self):
        self.assertNotIn("language_constant_ids", PLAN["campaigns"][0])
        self.assertEqual(counts().get("campaign_criterion_language", 0), 0)

    def test_no_silent_default_to_language_constant_1000(self):
        for op in compiled().creates:
            self.assertNotIn("languageConstants/1000", str(op.payload))

    def test_languages_are_created_when_explicitly_listed(self):
        plan = copy.deepcopy(PLAN)
        plan["campaigns"][0]["language_constant_ids"] = ["1000"]
        self.assertEqual(compile_plan(plan, ASSETS).counts()
                         .get("campaign_criterion_language", 0), 1)


class AssetTests(unittest.TestCase):
    def test_eleven_new_assets_produce_eleven_asset_resources(self):
        c = counts()
        total = (c["asset_sitelink_new"] + c["asset_callout_new"]
                 + c["asset_structured_snippet_new"])
        self.assertEqual(total, 11)
        self.assertEqual((c["asset_sitelink_new"], c["asset_callout_new"],
                          c["asset_structured_snippet_new"]), (4, 6, 1))

    def test_thirteen_associations_and_all_are_paused(self):
        assoc = [op for op in compiled().creates
                 if op.mutation_type == "campaign_asset_association"]
        self.assertEqual(len(assoc), 13)
        for op in assoc:
            self.assertEqual(op.payload["status"], "PAUSED")

    def test_reused_assets_are_associated_not_recreated(self):
        assoc = [op for op in compiled().creates
                 if op.mutation_type == "campaign_asset_association"]
        reused = [op for op in assoc if "existing_asset_id" in op.payload]
        self.assertEqual(len(reused), 2)
        created_ids = {op.planned_id for op in compiled().creates
                       if op.mutation_type.startswith("asset_")}
        for op in reused:
            self.assertNotIn(op.payload["existing_asset_id"], created_ids)


class ConversionGoalTests(unittest.TestCase):
    def test_already_false_goals_produce_no_update(self):
        iso = PLAN["campaign_conversion_goal_isolation"]
        self.assertEqual(len(iso["no_mutation_planned"]), 7)
        planned = {(u["category"], u["origin"]) for u in iso["planned_updates"]}
        for row in iso["no_mutation_planned"]:
            self.assertNotIn((row["category"], row["origin"]), planned)

    def test_exactly_seven_true_goals_produce_seven_biddable_updates(self):
        ops = [op for op in compiled().updates
               if op.mutation_type == "campaign_conversion_goal_biddable_false"]
        self.assertEqual(len(ops), 7)
        for op in ops:
            self.assertIs(op.payload["biddable"], False)
            self.assertEqual(op.payload["update_mask"], ["biddable"])

    def test_exactly_one_conversion_goal_campaign_config_update(self):
        ops = [op for op in compiled().updates
               if op.mutation_type == "conversion_goal_campaign_config"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].payload["update_mask"], ["custom_conversion_goal"])
        self.assertNotIn("goal_config_level", ops[0].payload["fields_to_set"])

    def test_custom_goal_carries_exactly_the_two_approved_actions(self):
        ops = [op for op in compiled().creates
               if op.mutation_type == "custom_conversion_goal"]
        self.assertEqual(len(ops), 1)
        actions = ops[0].payload["conversion_actions"]
        self.assertEqual(len(actions), 2)
        self.assertEqual(sorted(a.split("/")[-1] for a in actions),
                         ["6885542325", "6885543534"])


class InventoryTests(unittest.TestCase):
    def test_compiled_inventory_is_exactly_eighty_creates_and_eight_updates(self):
        c = compiled()
        self.assertEqual(len(c.creates), 80)
        self.assertEqual(len(c.updates), 8)
        self.assertEqual(c.summary()["total"], 88)

    def test_compiled_matches_the_declared_plan(self):
        assert_counts_match(PLAN, compiled())

    def test_no_unapproved_operation_is_present(self):
        declared = PLAN["create_paused_objects"]
        allowed = ({k for k in declared["creates"] if k != "total_creates"}
                   | {k for k in declared["updates"] if k != "total_updates"})
        for mutation_type in compiled().counts():
            self.assertIn(mutation_type, allowed)

    def test_an_extra_operation_fails_the_count_check(self):
        plan = copy.deepcopy(PLAN)
        plan["campaigns"][0]["language_constant_ids"] = ["1000"]
        with self.assertRaises(PlanCompileError):
            assert_counts_match(plan, compile_plan(plan, ASSETS))

    def test_a_dropped_operation_fails_the_count_check(self):
        plan = copy.deepcopy(PLAN)
        plan["campaigns"][0]["location"]["proximity"].pop()
        with self.assertRaises(PlanCompileError):
            assert_counts_match(plan, compile_plan(plan, ASSETS))


class PublishabilityGateTests(unittest.TestCase):
    def test_the_real_plan_is_publishable(self):
        assert_publishable(PLAN, ASSETS)
        self.assertTrue(can_issue_fingerprint(PLAN, ASSETS))

    def test_every_compiled_type_has_a_handler(self):
        self.assertEqual(unsupported_types(compiled()), [])

    def test_an_unsupported_mutation_type_prevents_fingerprint_issuance(self):
        removed = HANDLERS.pop("campaign_criterion_proximity")
        try:
            self.assertFalse(can_issue_fingerprint(PLAN, ASSETS))
            with self.assertRaises(PublisherCapabilityError) as ctx:
                assert_publishable(PLAN, ASSETS)
            self.assertIn("no publisher handler", str(ctx.exception))
        finally:
            HANDLERS["campaign_criterion_proximity"] = removed

    def test_an_unsupported_status_prevents_fingerprint_issuance(self):
        original = HANDLERS["campaign_asset_association"]["statuses"]
        HANDLERS["campaign_asset_association"]["statuses"] = ["ENABLED"]
        try:
            self.assertFalse(can_issue_fingerprint(PLAN, ASSETS))
        finally:
            HANDLERS["campaign_asset_association"]["statuses"] = original

    def test_an_unsupported_update_mask_prevents_fingerprint_issuance(self):
        original = HANDLERS["conversion_goal_campaign_config"]["update_masks"]
        HANDLERS["conversion_goal_campaign_config"]["update_masks"] = [["goal_config_level"]]
        try:
            self.assertFalse(can_issue_fingerprint(PLAN, ASSETS))
        finally:
            HANDLERS["conversion_goal_campaign_config"]["update_masks"] = original

    def test_a_count_mismatch_prevents_fingerprint_issuance(self):
        plan = copy.deepcopy(PLAN)
        plan["create_paused_objects"]["creates"]["campaign_criterion_proximity"] = 1
        self.assertFalse(can_issue_fingerprint(plan, ASSETS))


class PausedStatusTests(unittest.TestCase):
    def test_campaign_ad_groups_keywords_and_rsas_are_all_paused(self):
        for op in compiled().creates:
            if op.mutation_type in {"campaign", "ad_group", "ad_group_criterion_keyword",
                                    "ad_group_ad_rsa", "campaign_asset_association"}:
                self.assertEqual(op.payload["status"], "PAUSED", op.planned_id)

    def test_custom_conversion_goal_is_enabled_because_it_cannot_serve_alone(self):
        op = next(op for op in compiled().creates
                  if op.mutation_type == "custom_conversion_goal")
        self.assertEqual(op.payload["status"], "ENABLED")

    def test_every_planned_id_is_unique_so_retries_cannot_duplicate(self):
        ids = [op.planned_id for op in compiled().operations]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
