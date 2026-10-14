"""Offline regression tests for fail-closed Google Ads execution gates."""
from __future__ import annotations

import copy
import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import ConfigurationError, load_yaml
from gm_gsa.safety import SafetyError, approval_code, require_independent_execution_authorization
from gm_gsa.work_orders import validate_work_order


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class HardenedExecutionTests(unittest.TestCase):
    def setUp(self):
        self.executor = module("hardened_exec", "execute_approved_plan.py")
        self.publisher = module("hardened_publish", "publish_campaign.py")

    def run_executor(self, extra):
        with mock.patch.object(sys, "argv", [
            "execute_approved_plan.py", "--plan", "/unreadable/plan.yaml",
            "--subplan", "STATUS", "--fingerprint", "0123456789AB",
            "--out", "/unwritable/receipt.json", *extra,
        ]), mock.patch.object(self.executor, "load_google_ads_client",
                             side_effect=AssertionError("API client must not load")), redirect_stdout(io.StringIO()):
            return self.executor.main()

    def test_no_execute_does_not_access_api(self):
        self.assertEqual(self.run_executor([]), 0)

    def test_execute_fails_closed_before_credentials(self):
        self.assertEqual(self.run_executor(["--execute"]), 1)

    def test_enable_blocked_even_during_validation(self):
        with mock.patch.object(sys, "argv", [
            "execute_approved_plan.py", "--plan", "/unreadable/plan.yaml",
            "--subplan", "ENABLE", "--fingerprint", "0123456789AB",
            "--out", "/unwritable/receipt.json", "--validate-only",
        ]), redirect_stdout(io.StringIO()):
            self.assertEqual(self.executor.main(), 1)

    def test_conflicting_arguments_rejected(self):
        with mock.patch.object(sys, "argv", [
            "execute_approved_plan.py", "--plan", "x", "--subplan", "STATUS",
            "--fingerprint", "a", "--out", "r", "--validate-only", "--execute",
        ]), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exc:
            self.executor.main()
        self.assertEqual(exc.exception.code, 2)

    def test_publish_execute_fails_before_any_api_access(self):
        with mock.patch.object(sys, "argv", [
            "publish_campaign.py", "plan.yaml", "--client", "client.yaml",
            "--work-order", "work-order.yaml", "--approval-code", "FAKE",
            "--execute",
        ]), mock.patch.object(self.publisher, "load_yaml", side_effect=[
            {"target": {}}, {"client": {"permissions": {"allow_create_paused": True}}},
            {"work_order": {}},
        ]), mock.patch.object(self.publisher, "assert_valid_work_order"), mock.patch.object(
            self.publisher, "assert_valid_campaign_plan"
        ), mock.patch.object(self.publisher, "load_google_ads_client",
                             side_effect=AssertionError("No API client")), redirect_stdout(io.StringIO()):
            self.assertEqual(self.publisher.main(), 1)

    def test_fingerprint_never_grants_independent_permission(self):
        plan = {"target": {"child_customer_id": "1234567890"}}
        self.assertTrue(approval_code(plan))
        with self.assertRaises(SafetyError):
            require_independent_execution_authorization(plan=plan, operation="CREATE_PAUSED")

    def test_mutated_plan_remains_unapproved(self):
        plan = {"target": {"child_customer_id": "1234567890"}}
        changed = copy.deepcopy(plan)
        changed["target"]["child_customer_id"] = "0987654321"
        self.assertNotEqual(approval_code(plan), approval_code(changed))
        with self.assertRaises(SafetyError):
            require_independent_execution_authorization(plan=changed, operation="STATUS")

    def test_duplicate_yaml_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "plan.yaml"
            path.write_text("target:\\n  child_customer_id: '1234567890'\\n  child_customer_id: '0987654321'\\n".replace("\\n", "\n"))
            with self.assertRaisesRegex(ConfigurationError, "Duplicate YAML key"):
                load_yaml(path)

    def test_valid_yaml_loads(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "client.yaml"
            path.write_text("client:\n  slug: example\n  services: [landscaping, hardscaping]\n")
            self.assertEqual(load_yaml(path)["client"]["slug"], "example")

    def test_second_scoped_service_is_allowed(self):
        profile = {
            "client": {"slug": "sample", "business_name": "Sample", "vertical": "landscaping",
                       "primary_service": "lawn mowing",
                       "offer": {"services_in_scope": ["patio installation"]},
                       "google_ads": {"child_customer_id": "1234567890",
                                      "exact_child_account_name": "Sample - live"}},
        }
        order = {"work_order": {
            "client_slug": "sample", "business_name": "Sample",
            "account": {"exact_child_account_name": "Sample - live",
                        "child_customer_id": "1234567890"},
            "service": {"vertical": "landscaping", "exact_primary_service": "patio installation"},
            "task": {"type": "campaign-build", "mode": "draft", "request": "Patio campaign"},
            "scope_approval": {"approved": False},
        }}
        self.assertEqual(validate_work_order(order, profile), [])
        order["work_order"]["service"]["exact_primary_service"] = "unapproved service"
        self.assertTrue(validate_work_order(order, profile))


if __name__ == "__main__":
    unittest.main()
