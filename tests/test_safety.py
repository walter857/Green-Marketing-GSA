from __future__ import annotations

import copy
import unittest

from gm_gsa.safety import (
    SafetyError,
    approval_code,
    assert_create_paused_approved,
    assert_no_embedded_secrets,
)


def sample_plan():
    return {
        "plan_version": 1,
        "target": {
            "child_customer_id": "1234567890",
            "exact_child_account_name": "Example Client - live",
        },
        "campaigns": [{"name": "Search | Example", "status": "PAUSED"}],
    }


def sample_profile():
    return {
        "client": {
            "google_ads": {
                "child_customer_id": "1234567890",
                "exact_child_account_name": "Example Client - live",
                "must_contain_live_marker": True,
            }
        }
    }


class SafetyTests(unittest.TestCase):
    def test_approval_code_changes_when_plan_changes(self):
        original = sample_plan()
        changed = copy.deepcopy(original)
        changed["campaigns"][0]["name"] = "Search | Changed"
        self.assertNotEqual(approval_code(original), approval_code(changed))

    def test_approval_gate_accepts_exact_plan(self):
        plan = sample_plan()
        assert_create_paused_approved(
            plan,
            sample_profile(),
            approval_code(plan),
            observed_account_name="Example Client - live",
        )

    def test_approval_gate_rejects_customer_mismatch(self):
        plan = sample_plan()
        plan["target"]["child_customer_id"] = "9999999999"
        with self.assertRaises(SafetyError):
            assert_create_paused_approved(plan, sample_profile(), approval_code(plan))

    def test_embedded_secret_is_rejected(self):
        with self.assertRaises(SafetyError):
            assert_no_embedded_secrets({"refresh_token": "do-not-store-me"})


if __name__ == "__main__":
    unittest.main()
