from __future__ import annotations

import unittest
from datetime import date

from gm_gsa.audit import (
    ReadOnlyAudit,
    audit_windows,
    derived_kpis,
    metrics_dict,
    scrub_text,
)
from gm_gsa.service_discovery import DiscoveryError, assert_read_only_query


class WindowTests(unittest.TestCase):
    def test_windows_end_yesterday_and_do_not_overlap(self):
        windows = {w.label: w for w in audit_windows(date(2026, 8, 7))}
        self.assertEqual((windows["last_30"].start, windows["last_30"].end), ("2026-07-08", "2026-08-06"))
        self.assertEqual(
            (windows["previous_30"].start, windows["previous_30"].end), ("2026-06-08", "2026-07-07")
        )
        self.assertEqual((windows["last_90"].start, windows["last_90"].end), ("2026-05-09", "2026-08-06"))
        self.assertLess(windows["previous_30"].end, windows["last_30"].start)


class ScrubTests(unittest.TestCase):
    def test_emails_and_phone_like_numbers_are_removed(self):
        self.assertEqual(scrub_text("call 214-555-0199 now"), "call [REDACTED_NUMBER] now")
        self.assertEqual(scrub_text("a@b.com"), "[REDACTED_EMAIL]")

    def test_ordinary_search_terms_are_untouched(self):
        self.assertEqual(scrub_text("sprinkler repair near me"), "sprinkler repair near me")


class _Metrics:
    cost_micros = 12_500_000
    impressions = 400
    clicks = 40
    ctr = 0.1
    average_cpc = 312_500
    conversions = 2.0
    all_conversions = 5.0
    conversions_from_interactions_rate = 0.05
    cost_per_conversion = 6_250_000
    cost_per_all_conversions = 2_500_000
    conversions_value = 0.0
    all_conversions_value = 0.0


class MetricTests(unittest.TestCase):
    def test_micros_are_converted(self):
        row = metrics_dict(_Metrics())
        self.assertEqual(row["cost"], 12.5)
        self.assertEqual(row["average_cpc"], 0.3125)
        self.assertEqual(row["cost_per_conversion"], 6.25)

    def test_unset_impression_share_is_none_not_zero(self):
        self.assertIsNone(metrics_dict(_Metrics())["search_impression_share"])

    def test_roas_is_unavailable_without_conversion_value(self):
        kpis = derived_kpis(metrics_dict(_Metrics()))
        self.assertIsNone(kpis["roas"])
        self.assertIn("ROAS unavailable", kpis["roas_note"])
        self.assertEqual(kpis["cost_per_conversion_calc"], 6.25)

    def test_no_conversions_yields_no_invented_cpl(self):
        self.assertIsNone(derived_kpis({"cost": 900.0, "conversions": 0.0})["cost_per_conversion_calc"])


class _FailingService:
    def __init__(self):
        self.calls = []

    def search(self, customer_id, query):
        self.calls.append(query)
        if "boom" in query:
            raise RuntimeError("INVALID_ARGUMENT")
        return [object()]

    def __getattr__(self, name):
        raise AssertionError(f"the audit must never call {name!r}")


class _Client:
    def __init__(self):
        self.service = _FailingService()
        self.requested = []

    def get_service(self, name):
        self.requested.append(name)
        if name != "GoogleAdsService":
            raise AssertionError(f"the audit must never use {name!r}")
        return self.service


class RunnerTests(unittest.TestCase):
    def test_one_failing_query_does_not_stop_the_others(self):
        runner = ReadOnlyAudit(_Client(), "1234567890")
        self.assertEqual(runner.rows("bad", "SELECT boom FROM campaign"), [])
        self.assertEqual(len(runner.rows("good", "SELECT campaign.id FROM campaign")), 1)
        self.assertEqual(runner.read_errors[0]["query"], "bad")
        self.assertEqual(runner.queries_executed, ["good"])

    def test_a_mutating_query_is_refused_and_never_swallowed(self):
        runner = ReadOnlyAudit(_Client(), "1234567890")
        with self.assertRaises(DiscoveryError):
            runner.rows("evil", "UPDATE campaign SET status = 'ENABLED'")
        self.assertEqual(runner.read_errors, [])

    def test_only_the_read_service_is_requested(self):
        client = _Client()
        runner = ReadOnlyAudit(client, "1234567890")
        runner.rows("ok", "SELECT campaign.id FROM campaign")
        self.assertEqual(set(client.requested), {"GoogleAdsService"})


class ShippedQueryTests(unittest.TestCase):
    def test_every_audit_query_passes_the_read_only_guard(self):
        from gm_gsa import audit as A

        window = A.DateWindow("last_30", "2026-07-08", "2026-08-06")
        queries = [
            A.CONVERSION_ACTION_QUERY,
            A.CAMPAIGN_SETTINGS_QUERY,
            A.CAMPAIGN_CRITERION_QUERY,
            A.AD_GROUP_CRITERION_NEGATIVE_QUERY,
            A.SHARED_SET_QUERY,
            A.SHARED_CRITERION_QUERY,
            A.CAMPAIGN_SHARED_SET_QUERY,
            A.ASSET_POLICY_QUERY,
            A.customer_query(window),
            A.campaign_performance_query(window),
            A.ad_group_performance_query(window),
            A.keyword_performance_query(window),
            A.search_term_query(window),
            A.ad_performance_query(window),
            A.ad_asset_performance_query(window),
            A.conversion_breakdown_query(window),
            A.geo_query(window),
            A.daily_series_query(window),
            A.phone_metrics_query(window),
            A._segment_query(window, "segments.device"),
            A.geo_target_constant_query(["geoTargetConstants/1026339"]),
        ]
        for query in queries:
            assert_read_only_query(query)

    def test_geo_constant_query_uses_full_resource_names(self):
        from gm_gsa import audit as A

        query = A.geo_target_constant_query(["geoTargetConstants/1026339", "1026385"])
        self.assertIn("'geoTargetConstants/1026339'", query)
        self.assertIn("'geoTargetConstants/1026385'", query)

    def test_sub_campaign_queries_omit_budget_lost_impression_share(self):
        """The API rejects that metric below campaign level."""

        from gm_gsa import audit as A

        window = A.DateWindow("last_30", "2026-07-08", "2026-08-06")
        for query in (
            A.ad_group_performance_query(window),
            A.keyword_performance_query(window),
        ):
            self.assertNotIn("search_budget_lost_impression_share", query)
        self.assertIn(
            "search_budget_lost_impression_share", A.campaign_performance_query(window)
        )

    def test_customer_query_omits_campaign_only_phone_metrics(self):
        from gm_gsa import audit as A

        window = A.DateWindow("last_30", "2026-07-08", "2026-08-06")
        self.assertNotIn("phone_calls", A.customer_query(window))
        self.assertIn("phone_calls", A.phone_metrics_query(window))


if __name__ == "__main__":
    unittest.main()
