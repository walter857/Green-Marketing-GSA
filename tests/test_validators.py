from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from gm_gsa.validators import validate_campaign_plan


ROOT = Path(__file__).resolve().parents[1]


def load_example():
    return yaml.safe_load(
        (ROOT / "templates/campaigns/search-skag.example.yaml").read_text(
            encoding="utf-8"
        )
    )


class ValidatorTests(unittest.TestCase):
    def test_example_campaign_plan_passes(self):
        self.assertEqual(validate_campaign_plan(load_example()), [])

    def test_plan_rejects_non_paused_campaign(self):
        plan = load_example()
        plan["campaigns"][0]["status"] = "ENABLED"
        errors = validate_campaign_plan(plan)
        self.assertTrue(any("status must be PAUSED" in error for error in errors))

    def test_plan_rejects_protected_negative(self):
        plan = load_example()
        plan["campaigns"][0]["negatives"].append("cost")
        errors = validate_campaign_plan(plan)
        self.assertTrue(any("protected buyer-intent term" in error for error in errors))

    def test_plan_requires_two_rsas(self):
        plan = load_example()
        plan["campaigns"][0]["ad_groups"][0]["ads"] = plan["campaigns"][0]["ad_groups"][0]["ads"][:1]
        errors = validate_campaign_plan(plan)
        self.assertTrue(any("exactly 2 RSAs" in error for error in errors))

    def test_plan_rejects_long_headline(self):
        plan = load_example()
        plan["campaigns"][0]["ad_groups"][0]["ads"][0]["headlines"][0]["text"] = "X" * 31
        errors = validate_campaign_plan(plan)
        self.assertTrue(any("exceeds 30 characters" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

