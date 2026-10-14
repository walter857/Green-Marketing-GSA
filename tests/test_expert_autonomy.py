"""Enforcement for the Expert Autonomy and Decision Rights policy.

These tests guard the persistent instructions themselves. Each one fails if a future edit
would let the system drift back into either failure mode: escalating routine technical
choices to the user, or letting autonomy erode an external-write gate.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml  # noqa: E402

CLAUDE_MD = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
AGENCY = load_yaml(ROOT / "config" / "agency.yaml")
AUTONOMY = AGENCY.get("expert_autonomy") or {}
SECTION_TITLE = "## Expert Autonomy and Decision Rights"


def _flatten(text: str) -> str:
    """Collapse whitespace so assertions test meaning, not line-wrap position."""
    return re.sub(r"\s+", " ", text)


def autonomy_section() -> str:
    start = CLAUDE_MD.index(SECTION_TITLE)
    rest = CLAUDE_MD[start + len(SECTION_TITLE):]
    end = rest.find("\n## ")
    return _flatten(rest if end == -1 else rest[:end])


def normalized_claude_md() -> str:
    return _flatten(CLAUDE_MD)


class PolicyPresenceTests(unittest.TestCase):
    def test_the_binding_section_exists(self):
        self.assertIn(SECTION_TITLE, CLAUDE_MD)

    def test_autonomy_is_enabled(self):
        self.assertIs(AUTONOMY.get("enabled"), True)

    def test_every_required_flag_is_present_and_true(self):
        for flag in (
            "enabled",
            "choose_single_recommendation",
            "complete_unblocked_work_before_questions",
            "batch_questions",
            "self_review_before_fingerprint",
            "do_not_escalate_routine_technical_choices",
            "agency_defaults_are_fallbacks",
            "external_write_gates_unchanged",
            "reopen_settled_decisions_only_on_new_material_evidence",
        ):
            self.assertIs(AUTONOMY.get(flag), True, f"{flag} must be true")

    def test_low_confidence_actions_are_conservative(self):
        self.assertEqual(AUTONOMY.get("low_confidence_strategy_action"), "conservative_default")
        self.assertEqual(AUTONOMY.get("low_confidence_fact_action"), "omit_or_placeholder")

    def test_public_claims_require_verified_first_party_evidence(self):
        self.assertEqual(
            AUTONOMY.get("minimum_evidence_for_public_claims"),
            "verified_client_or_first_party",
        )

    def test_there_is_only_one_instruction_system(self):
        """A second competing autonomy section would create conflicting instructions."""
        self.assertEqual(CLAUDE_MD.count(SECTION_TITLE), 1)


class ExternalWriteGatesSurviveTests(unittest.TestCase):
    """Autonomy must never be readable as permission to write externally."""

    def test_config_declares_write_gates_unchanged(self):
        self.assertIs(AUTONOMY.get("external_write_gates_unchanged"), True)

    def test_approval_gates_are_still_required_in_config(self):
        approvals = AGENCY["approvals"]
        self.assertIs(approvals["create_paused_requires_plan_fingerprint"], True)
        self.assertIs(approvals["enable_requires_separate_approval"], True)
        self.assertIs(approvals["budget_change_requires_separate_approval"], True)
        self.assertIs(approvals["deletion_requires_destructive_action_approval"], True)

    def test_the_section_states_autonomy_excludes_external_writes(self):
        body = autonomy_section().lower()
        self.assertIn("never permission to change an external account", body)
        self.assertIn("requires its own exact approval", body)

    def test_enable_is_never_permitted_during_creation(self):
        lowered = normalized_claude_md().lower()
        self.assertIn("never enable delivery in the same operation that creates resources", lowered)

    def test_separate_enablement_approval_survives(self):
        self.assertIn("separate approval after create-paused readback qa", autonomy_section().lower())

    def test_external_write_approval_is_an_escalation_trigger(self):
        self.assertIn("external_write_approval_required", AUTONOMY.get("escalation_triggers", []))


class NoRoutineEscalationTests(unittest.TestCase):
    """Fail if the policy stops forbidding routine technical questions."""

    REQUIRED_OWNED = [
        "campaign_architecture",
        "ad_group_structure",
        "canonical_keyword_themes",
        "match_types_within_policy",
        "negative_keywords",
        "bidding_recommendation",
        "rsa_structure_copy_pins",
        "api_fields_masks_sequencing_readback",
        "asset_reuse_decisions",
        "mutation_necessity",
        "conversion_goal_architecture",
    ]

    def test_owned_decisions_are_declared(self):
        owned = AUTONOMY.get("owned_technical_decisions", [])
        for item in self.REQUIRED_OWNED:
            self.assertIn(item, owned, f"{item} must remain a Claude-owned decision")

    def test_owned_decisions_are_not_escalation_triggers(self):
        owned = set(AUTONOMY.get("owned_technical_decisions", []))
        triggers = set(AUTONOMY.get("escalation_triggers", []))
        self.assertEqual(owned & triggers, set(),
                         "a Claude-owned decision must never also be an escalation trigger")

    def test_the_section_forbids_a_menu_of_equivalent_options(self):
        body = autonomy_section().lower()
        self.assertIn("not a menu", body)
        self.assertIn("do not ask about routine keyword or match-type selection", body)

    def test_the_section_names_the_do_not_ask_list(self):
        body = autonomy_section().lower()
        for phrase in ("technical field masks", "api sequencing", "redundant mutations",
                       "validator implementation", "conservative technical defaults"):
            self.assertIn(phrase, body)

    def test_repeat_questioning_requires_new_evidence(self):
        body = autonomy_section().lower()
        self.assertIn("do not repeat a question unless new conflicting evidence appears", body)
        self.assertIs(AUTONOMY.get("reopen_settled_decisions_only_on_new_material_evidence"), True)


class NoInventedFactsTests(unittest.TestCase):
    def test_the_section_forbids_inventing_business_facts(self):
        body = autonomy_section().lower()
        self.assertIn("never invent", body)
        for token in ("volume", "services", "offers", "reviews", "locations"):
            self.assertIn(token, body)

    def test_unverified_facts_are_omitted_not_guessed(self):
        self.assertEqual(AUTONOMY.get("low_confidence_fact_action"), "omit_or_placeholder")
        self.assertIn("omit the claim or keep a labelled placeholder", autonomy_section())

    def test_client_truth_rules_survive_elsewhere_in_claude_md(self):
        lowered = normalized_claude_md().lower()
        self.assertIn("never infer it from another client", lowered)
        self.assertIn("source examples are guidance, never authority to overwrite client facts",
                      lowered)


class SelfReviewBeforeFingerprintTests(unittest.TestCase):
    REQUIRED_CHECKS = [
        "client_truth", "campaign_strategy", "search_intent", "conversion_isolation",
        "mutation_necessity", "google_ads_api_field_validity", "status_handling",
        "asset_support", "character_limits", "url_mapping", "location_targeting",
        "budget_math", "landing_page_template_compliance", "unsupported_claims",
        "mutation_counts", "artifact_hashes", "approval_bundle_completeness",
    ]

    def test_self_review_is_required(self):
        self.assertIs(AUTONOMY.get("self_review_before_fingerprint"), True)

    def test_the_checklist_is_complete(self):
        checklist = AUTONOMY.get("self_review_checklist", [])
        for item in self.REQUIRED_CHECKS:
            self.assertIn(item, checklist, f"self-review must cover {item}")

    def test_the_section_orders_review_before_the_fingerprint(self):
        body = autonomy_section()
        self.assertIn("Before presenting any fingerprint", body)
        self.assertIn("only then generate the fingerprint", body)

    def test_drafts_may_be_revised_without_asking(self):
        self.assertIn("revised as many times as needed without asking", autonomy_section())


class EvidenceHierarchyTests(unittest.TestCase):
    def test_hierarchy_is_declared_and_ordered(self):
        hierarchy = AUTONOMY.get("evidence_hierarchy", [])
        self.assertGreaterEqual(len(hierarchy), 9)
        self.assertEqual(hierarchy[0], "explicit_user_instructions_and_verified_client_facts")
        self.assertEqual(hierarchy[-1], "conservative_industry_practice")

    def test_account_data_outranks_agency_policy(self):
        hierarchy = AUTONOMY.get("evidence_hierarchy", [])
        self.assertLess(hierarchy.index("fresh_google_ads_account_data"),
                        hierarchy.index("green_marketing_agency_policy"))

    def test_defaults_are_fallbacks_not_ceilings(self):
        self.assertIs(AUTONOMY.get("agency_defaults_are_fallbacks"), True)
        self.assertIn("fallbacks, not ceilings", autonomy_section())


class ConsolidatedResponseTests(unittest.TestCase):
    def test_questions_are_batched_after_unblocked_work(self):
        self.assertIs(AUTONOMY.get("complete_unblocked_work_before_questions"), True)
        self.assertIs(AUTONOMY.get("batch_questions"), True)
        body = autonomy_section().lower()
        self.assertIn("finish everything unaffected first", body)
        self.assertIn("consolidate them", body)

    def test_open_ended_endings_are_forbidden(self):
        self.assertIn("let me know how you want to proceed", autonomy_section().lower())
        self.assertIn("state the exact next approval or input required", autonomy_section().lower())


if __name__ == "__main__":
    unittest.main()
