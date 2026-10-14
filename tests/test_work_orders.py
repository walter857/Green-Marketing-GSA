from __future__ import annotations

import copy
import unittest

from gm_gsa.work_orders import validate_work_order


def sample_profile():
    return {
        "client": {
            "slug": "example-landscape",
            "business_name": "Example Landscape",
            "vertical": "landscaping",
            "primary_service": "landscape design",
            "google_ads": {
                "child_customer_id": "1234567890",
                "exact_child_account_name": "Example Landscape - live",
            },
        }
    }


def sample_order():
    return {
        "work_order": {
            "client_slug": "example-landscape",
            "business_name": "Example Landscape",
            "account": {
                "exact_child_account_name": "Example Landscape - live",
                "child_customer_id": "1234567890",
            },
            "service": {
                "vertical": "landscaping",
                "exact_primary_service": "landscape design",
                "related_services": [],
            },
            "task": {
                "type": "audit",
                "mode": "read",
                "request": "Audit the landscape design campaign.",
            },
            "scope_approval": {"approved": False},
        }
    }


class WorkOrderTests(unittest.TestCase):
    def test_valid_order_matches_profile(self):
        self.assertEqual(validate_work_order(sample_order(), sample_profile()), [])

    def test_requires_exact_service(self):
        order = sample_order()
        order["work_order"]["service"]["exact_primary_service"] = ""
        self.assertTrue(any("exact_primary_service is required" in error for error in validate_work_order(order)))

    def test_rejects_manager_id_length(self):
        order = sample_order()
        order["work_order"]["account"]["child_customer_id"] = "123"
        self.assertTrue(any("exactly 10 digits" in error for error in validate_work_order(order)))

    def test_similar_service_requires_explicit_approval(self):
        order = sample_order()
        order["work_order"]["service"]["vertical"] = "similar-local-service"
        errors = validate_work_order(order)
        self.assertTrue(any("requires scope_approval.approved" in error for error in errors))

    def test_accepts_second_approved_service_from_profile_scope(self):
        profile = sample_profile()
        profile["client"]["offer"] = {
            "services_in_scope": ["landscape design", "paver patio installation"]
        }
        order = copy.deepcopy(sample_order())
        order["work_order"]["service"]["exact_primary_service"] = "paver patio installation"
        self.assertEqual(validate_work_order(order, profile), [])

    def test_rejects_service_absent_from_profile_scope(self):
        profile = sample_profile()
        profile["client"]["offer"] = {"services_in_scope": ["landscape design"]}
        order = copy.deepcopy(sample_order())
        order["work_order"]["service"]["exact_primary_service"] = "asphalt paving"
        self.assertTrue(
            any("services_in_scope" in error for error in validate_work_order(order, profile))
        )

    def test_rejects_profile_account_mismatch(self):
        order = copy.deepcopy(sample_order())
        order["work_order"]["account"]["exact_child_account_name"] = "Wrong - live"
        self.assertTrue(any("child account name" in error for error in validate_work_order(order, sample_profile())))


if __name__ == "__main__":
    unittest.main()
