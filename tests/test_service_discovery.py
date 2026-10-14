from __future__ import annotations

import unittest
from pathlib import Path

from gm_gsa.config import load_yaml
from gm_gsa.google_ads import CustomerIdentity
from gm_gsa.landing_pages import parse_page, read_landing_page
from gm_gsa.service_discovery import (
    DiscoveryError,
    ManagerLink,
    ServiceTerm,
    assert_discovery_identity,
    assert_exact_service_required,
    assert_manager_link,
    assert_read_only_query,
    assert_valid_service_discovery,
    classify_services,
    collect_account_evidence,
    discovery_target,
    load_service_lexicon,
    validate_service_discovery,
)
from gm_gsa.work_orders import validate_work_order

ROOT = Path(__file__).resolve().parents[1]


def sample_document():
    return {
        "service_discovery": {
            "client_slug": "example-landscape",
            "business_name": "Example Landscape",
            "account": {
                "exact_child_account_name": "Example Landscape - Live",
                "child_customer_id": "1234567890",
                "manager_customer_id": "9876543210",
            },
            "task": {
                "type": "service-discovery",
                "mode": "read",
                "request": "Discover the advertised services.",
            },
            "authorization": {
                "read_only_service_discovery": True,
                "approved_by": "Green Marketing",
                "granted_on": "2026-08-07",
            },
        }
    }


def sample_identity(**overrides):
    values = {
        "customer_id": "1234567890",
        "descriptive_name": "Example Landscape - Live",
        "currency_code": "USD",
        "time_zone": "America/Chicago",
        "manager": False,
        "test_account": False,
    }
    values.update(overrides)
    return CustomerIdentity(**values)


def sample_link(**overrides):
    values = {
        "manager_customer_id": "9876543210",
        "child_customer_id": "1234567890",
        "descriptive_name": "Example Landscape - Live",
        "level": 1,
        "manager": False,
        "test_account": False,
        "status": "ENABLED",
    }
    values.update(overrides)
    return ManagerLink(**values)


class DiscoveryDocumentTests(unittest.TestCase):
    def test_discovery_runs_without_a_confirmed_service(self):
        document = sample_document()
        self.assertEqual(validate_service_discovery(document), [])
        target = discovery_target(document)
        self.assertEqual(target.child_customer_id, "1234567890")
        self.assertEqual(target.manager_customer_id, "9876543210")

    def test_exact_account_name_is_mandatory(self):
        document = sample_document()
        document["service_discovery"]["account"]["exact_child_account_name"] = ""
        errors = validate_service_discovery(document)
        self.assertTrue(any("exact_child_account_name is required" in error for error in errors))

    def test_account_name_must_carry_the_live_marker(self):
        document = sample_document()
        document["service_discovery"]["account"]["exact_child_account_name"] = "Example Landscape"
        errors = validate_service_discovery(document)
        self.assertTrue(any("must contain '- live'" in error for error in errors))

    def test_ten_digit_child_id_is_mandatory(self):
        document = sample_document()
        document["service_discovery"]["account"]["child_customer_id"] = "12345"
        errors = validate_service_discovery(document)
        self.assertTrue(any("exactly 10 digits" in error for error in errors))

    def test_manager_id_is_mandatory_and_distinct(self):
        document = sample_document()
        document["service_discovery"]["account"]["manager_customer_id"] = ""
        self.assertTrue(
            any("manager_customer_id" in error for error in validate_service_discovery(document))
        )
        same = sample_document()
        same["service_discovery"]["account"]["manager_customer_id"] = "1234567890"
        self.assertTrue(
            any(
                "must not be the manager customer ID" in error
                for error in validate_service_discovery(same)
            )
        )

    def test_cannot_authorize_an_audit(self):
        document = sample_document()
        document["service_discovery"]["task"]["type"] = "audit"
        errors = validate_service_discovery(document)
        self.assertTrue(any("task.type must be 'service-discovery'" in error for error in errors))

    def test_cannot_authorize_draft_create_or_enable(self):
        for mode in ("draft", "create-paused", "enable"):
            document = sample_document()
            document["service_discovery"]["task"]["mode"] = mode
            errors = validate_service_discovery(document)
            self.assertTrue(
                any("task.mode must be 'read'" in error for error in errors),
                f"mode {mode} was not rejected",
            )

    def test_authorization_flag_must_be_true(self):
        document = sample_document()
        document["service_discovery"]["authorization"]["read_only_service_discovery"] = False
        errors = validate_service_discovery(document)
        self.assertTrue(
            any("read_only_service_discovery must be true" in error for error in errors)
        )

    def test_document_may_not_assert_a_service(self):
        document = sample_document()
        document["service_discovery"]["service"] = {"exact_primary_service": "paver patios"}
        errors = validate_service_discovery(document)
        self.assertTrue(any("never asserts one" in error for error in errors))

    def test_document_may_not_carry_a_plan(self):
        document = sample_document()
        document["service_discovery"]["campaigns"] = [{"name": "Search | Anything"}]
        errors = validate_service_discovery(document)
        self.assertTrue(any("campaigns is not allowed" in error for error in errors))

    def test_client_profile_mismatch_is_reported(self):
        profile = {
            "client": {
                "slug": "example-landscape",
                "business_name": "Example Landscape",
                "google_ads": {
                    "exact_child_account_name": "Someone Else - Live",
                    "child_customer_id": "1111111111",
                    "manager_customer_id": "9876543210",
                },
            }
        }
        errors = validate_service_discovery(sample_document(), profile)
        self.assertTrue(any("child account name does not match" in error for error in errors))
        self.assertTrue(any("child customer ID does not match" in error for error in errors))

    def test_invalid_document_raises(self):
        document = sample_document()
        document["service_discovery"]["task"]["mode"] = "enable"
        with self.assertRaises(DiscoveryError):
            assert_valid_service_discovery(document)


class ServiceRequirementBoundaryTests(unittest.TestCase):
    def test_only_discovery_may_run_without_a_service(self):
        assert_exact_service_required("service-discovery", None)

    def test_audit_draft_build_and_revamp_still_require_a_service(self):
        for task in ("audit", "campaign-build", "campaign-revamp", "landing-page", "deployment"):
            with self.assertRaises(DiscoveryError, msg=f"{task} ran without a service"):
                assert_exact_service_required(task, None)
            with self.assertRaises(DiscoveryError, msg=f"{task} ran with a blank service"):
                assert_exact_service_required(task, "   ")

    def test_confirmed_service_unblocks_later_workflows(self):
        assert_exact_service_required("audit", "paver patio installation")

    def test_work_order_validation_is_unchanged(self):
        """A discovery document's facts are not enough to pass a work order."""

        order = {
            "work_order": {
                "client_slug": "example-landscape",
                "business_name": "Example Landscape",
                "account": {
                    "exact_child_account_name": "Example Landscape - Live",
                    "child_customer_id": "1234567890",
                },
                "service": {"vertical": "landscaping", "exact_primary_service": ""},
                "task": {"type": "audit", "mode": "read", "request": "Audit the account."},
                "scope_approval": {"approved": False},
            }
        }
        errors = validate_work_order(order)
        self.assertTrue(any("exact_primary_service is required" in error for error in errors))

    def test_service_discovery_is_not_an_allowed_work_order_task(self):
        order = {
            "work_order": {
                "client_slug": "example-landscape",
                "business_name": "Example Landscape",
                "account": {
                    "exact_child_account_name": "Example Landscape - Live",
                    "child_customer_id": "1234567890",
                },
                "service": {"vertical": "landscaping", "exact_primary_service": "lawn care"},
                "task": {
                    "type": "service-discovery",
                    "mode": "read",
                    "request": "Discover services.",
                },
                "scope_approval": {"approved": False},
            }
        }
        errors = validate_work_order(order)
        self.assertTrue(any("not an allowed Green Marketing workflow" in e for e in errors))


class IdentityGateTests(unittest.TestCase):
    def setUp(self):
        self.target = discovery_target(sample_document())

    def test_exact_identity_passes(self):
        assert_discovery_identity(sample_identity(), self.target)
        assert_manager_link(sample_link(), self.target)

    def test_name_mismatch_stops_the_workflow(self):
        with self.assertRaises(DiscoveryError):
            assert_discovery_identity(
                sample_identity(descriptive_name="Example Landscape - live"), self.target
            )

    def test_customer_id_mismatch_stops_the_workflow(self):
        with self.assertRaises(DiscoveryError):
            assert_discovery_identity(sample_identity(customer_id="1111111111"), self.target)

    def test_manager_or_test_account_stops_the_workflow(self):
        with self.assertRaises(DiscoveryError):
            assert_discovery_identity(sample_identity(manager=True), self.target)
        with self.assertRaises(DiscoveryError):
            assert_discovery_identity(sample_identity(test_account=True), self.target)

    def test_missing_manager_link_stops_the_workflow(self):
        with self.assertRaises(DiscoveryError):
            assert_manager_link(None, self.target)

    def test_wrong_manager_link_details_stop_the_workflow(self):
        for override in (
            {"descriptive_name": "Other Account - Live"},
            {"child_customer_id": "1111111111"},
            {"manager": True},
            {"test_account": True},
            {"level": 0},
            {"status": "SUSPENDED"},
        ):
            with self.assertRaises(DiscoveryError, msg=f"{override} was accepted"):
                assert_manager_link(sample_link(**override), self.target)


class ReadOnlyQueryTests(unittest.TestCase):
    def test_select_is_allowed(self):
        assert_read_only_query("SELECT campaign.id FROM campaign")

    def test_non_select_is_refused(self):
        for query in ("UPDATE campaign SET x = 1", "DELETE FROM campaign", "  mutate campaign  "):
            with self.assertRaises(DiscoveryError, msg=f"{query!r} was accepted"):
                assert_read_only_query(query)

    def test_mutating_keyword_inside_a_select_is_refused(self):
        with self.assertRaises(DiscoveryError):
            assert_read_only_query("SELECT campaign.id FROM campaign; MUTATE campaign")

    def test_shipped_queries_pass_the_guard(self):
        from gm_gsa import service_discovery as sd

        for query in (
            sd.CAMPAIGN_QUERY,
            sd.NON_REMOVED_CAMPAIGN_QUERY,
            sd.AD_GROUP_QUERY,
            sd.KEYWORD_QUERY,
            sd.AD_QUERY,
            sd.CAMPAIGN_ASSET_QUERY,
            sd.AD_GROUP_ASSET_QUERY,
            sd.CUSTOMER_ASSET_QUERY,
            sd.MANAGER_LINK_QUERY.format(child_id="1234567890"),
        ):
            assert_read_only_query(query)


class EnumNameTests(unittest.TestCase):
    def test_int_enum_renders_its_symbolic_name(self):
        """Python 3.11 IntEnum.__str__ returns digits, not Name.MEMBER."""

        import enum

        from gm_gsa.google_ads import enum_name

        class CustomerStatus(enum.IntEnum):
            UNSPECIFIED = 0
            ENABLED = 2

        self.assertEqual(enum_name(CustomerStatus.ENABLED), "ENABLED")
        self.assertEqual(enum_name("CampaignStatus.PAUSED"), "PAUSED")


class _FakeRow:
    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)


class _FakeService:
    def __init__(self, rows_by_resource):
        self.rows_by_resource = rows_by_resource
        self.queries = []

    def search(self, customer_id, query):
        self.queries.append((customer_id, query))
        resource = query.split("FROM")[1].split()[0].strip()
        return list(self.rows_by_resource.get(resource, []))

    def __getattr__(self, name):  # any mutate entry point is a hard failure
        raise AssertionError(f"service_discovery must never call {name!r}")


class _FakeClient:
    def __init__(self, rows_by_resource):
        self.service = _FakeService(rows_by_resource)
        self.requested_services = []

    def get_service(self, name):
        self.requested_services.append(name)
        if name != "GoogleAdsService":
            raise AssertionError(f"service_discovery must never use {name!r}")
        return self.service


def fake_account_rows():
    campaign = _FakeRow(id=101, name="Search | Paver Patios | Dallas")
    campaign.status = "CampaignStatus.ENABLED"
    campaign.advertising_channel_type = "AdvertisingChannelType.SEARCH"
    campaign.advertising_channel_sub_type = "AdvertisingChannelSubType.UNSPECIFIED"
    ad_group = _FakeRow(id=201, name="paver patio installation")
    ad_group.status = "AdGroupStatus.ENABLED"
    criterion = _FakeRow(
        criterion_id=301,
        keyword=_FakeRow(text="paver patio installation", match_type="KeywordMatchType.PHRASE"),
        status="AdGroupCriterionStatus.ENABLED",
        final_urls=[],
    )
    ad = _FakeRow(
        id=401,
        type_="AdType.RESPONSIVE_SEARCH_AD",
        final_urls=["https://example.com/paver-patios"],
        responsive_search_ad=_FakeRow(
            path1="patios",
            path2="dallas",
            headlines=[_FakeRow(text="Paver Patio Installation", pinned_field="HEADLINE_1")],
            descriptions=[_FakeRow(text="Custom paver patios built in Dallas.", pinned_field=None)],
        ),
    )
    ad_group_ad = _FakeRow(
        ad=ad,
        status="AdGroupAdStatus.ENABLED",
        policy_summary=_FakeRow(
            approval_status="PolicyApprovalStatus.APPROVED",
            review_status="PolicyReviewStatus.REVIEWED",
        ),
    )
    asset = _FakeRow(
        id=501,
        name="",
        type_="AssetType.SITELINK",
        final_urls=["https://example.com/retaining-walls"],
        sitelink_asset=_FakeRow(
            link_text="Retaining Walls", description1="Block and stone", description2="Free quote"
        ),
        callout_asset=_FakeRow(callout_text=""),
        structured_snippet_asset=_FakeRow(header="", values=[]),
    )
    return {
        "campaign": [_FakeRow(campaign=campaign)],
        "ad_group": [_FakeRow(ad_group=ad_group, campaign=campaign)],
        "ad_group_criterion": [
            _FakeRow(ad_group_criterion=criterion, ad_group=ad_group, campaign=campaign)
        ],
        "ad_group_ad": [
            _FakeRow(ad_group_ad=ad_group_ad, ad_group=ad_group, campaign=campaign)
        ],
        "campaign_asset": [
            _FakeRow(
                asset=asset,
                campaign_asset=_FakeRow(
                    field_type="AssetFieldType.SITELINK", status="AssetLinkStatus.ENABLED"
                ),
                campaign=campaign,
            )
        ],
        "ad_group_asset": [],
        "customer_asset": [],
    }


class EvidenceCollectionTests(unittest.TestCase):
    def test_collection_only_reads(self):
        client = _FakeClient(fake_account_rows())
        target = discovery_target(sample_document())
        evidence = collect_account_evidence(client, target)

        self.assertEqual(set(client.requested_services), {"GoogleAdsService"})
        for customer_id, query in client.service.queries:
            self.assertEqual(customer_id, target.child_customer_id)
            assert_read_only_query(query)

        self.assertEqual(len(evidence["campaigns"]), 1)
        self.assertEqual(evidence["campaigns"][0]["status"], "ENABLED")
        self.assertEqual(evidence["keywords"][0]["match_type"], "PHRASE")
        self.assertEqual(evidence["ads"][0]["approval_status"], "APPROVED")
        self.assertEqual(evidence["assets"][0]["sitelink_text"], "Retaining Walls")
        self.assertEqual(evidence["non_removed_campaign_index"], [])

    def test_empty_account_falls_back_to_a_names_only_index(self):
        rows = {resource: [] for resource in fake_account_rows()}
        paused = _FakeRow(id=999, name="Search | Paused")
        paused.status = "CampaignStatus.PAUSED"
        paused.advertising_channel_type = "AdvertisingChannelType.SEARCH"
        paused.advertising_channel_sub_type = "AdvertisingChannelSubType.UNSPECIFIED"
        rows["campaign"] = []
        client = _FakeClient(rows)

        original_search = client.service.search
        calls = {"count": 0}

        def search(customer_id, query):
            calls["count"] += 1
            if "!= REMOVED" in query:
                return [_FakeRow(campaign=paused)]
            return original_search(customer_id, query)

        client.service.search = search
        evidence = collect_account_evidence(client, discovery_target(sample_document()))
        self.assertEqual(evidence["campaigns"], [])
        self.assertEqual(evidence["non_removed_campaign_index"][0]["status"], "PAUSED")


class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self.lexicon = [
            ServiceTerm(
                canonical="paver patio installation",
                vertical="hardscaping",
                synonyms=("paver patio", "pavers", "patio installation"),
            ),
            ServiceTerm(
                canonical="retaining walls",
                vertical="hardscaping",
                synonyms=("retaining wall",),
            ),
            ServiceTerm(
                canonical="AC repair",
                vertical="heating-cooling",
                synonyms=("ac repair", "air conditioning repair"),
            ),
        ]

    def test_strong_multi_source_evidence_is_high_confidence(self):
        client = _FakeClient(fake_account_rows())
        evidence = collect_account_evidence(client, discovery_target(sample_document()))
        result = classify_services(evidence, [], self.lexicon, [])
        patios = next(c for c in result["candidates"] if c["service"] == "paver patio installation")
        self.assertEqual(patios["confidence"], "high")
        self.assertIn("campaign_name", patios["evidence_kinds"])
        self.assertIn("keyword", patios["evidence_kinds"])
        self.assertEqual(patios["campaigns"], [{"id": "101", "name": "Search | Paver Patios | Dallas"}])

    def test_synonyms_group_into_one_service(self):
        evidence = {
            "campaigns": [{"id": "1", "name": "Pavers"}],
            "ad_groups": [
                {"id": "2", "name": "paver patio", "campaign_id": "1", "campaign_name": "Pavers"}
            ],
            "keywords": [
                {
                    "text": "patio installation",
                    "match_type": "EXACT",
                    "ad_group_id": "2",
                    "ad_group_name": "paver patio",
                    "campaign_id": "1",
                    "campaign_name": "Pavers",
                    "final_urls": [],
                }
            ],
            "ads": [],
            "assets": [],
        }
        result = classify_services(evidence, [], self.lexicon, [])
        self.assertEqual([c["service"] for c in result["candidates"]], ["paver patio installation"])
        self.assertEqual(
            result["candidates"][0]["matched_terms"],
            ["patio installation", "paver patio", "pavers"],
        )

    def test_distinct_services_stay_separate(self):
        evidence = {
            "campaigns": [
                {"id": "1", "name": "Paver Patios"},
                {"id": "2", "name": "Retaining Walls"},
            ],
            "ad_groups": [],
            "keywords": [],
            "ads": [],
            "assets": [],
        }
        services = {c["service"] for c in classify_services(evidence, [], self.lexicon, [])["candidates"]}
        self.assertEqual(services, {"paver patio installation", "retaining walls"})

    def test_a_single_weak_clue_is_low_confidence(self):
        evidence = {
            "campaigns": [],
            "ad_groups": [],
            "keywords": [],
            "ads": [],
            "assets": [
                {
                    "asset_name": "",
                    "sitelink_text": "AC Repair",
                    "sitelink_description_1": "",
                    "sitelink_description_2": "",
                    "callout_text": "",
                    "structured_snippet_header": "",
                    "structured_snippet_values": [],
                    "final_urls": [],
                    "field_type": "SITELINK",
                    "scope": "customer",
                    "campaign_id": "",
                    "campaign_name": "",
                    "ad_group_id": "",
                    "ad_group_name": "",
                }
            ],
        }
        candidate = classify_services(evidence, [], self.lexicon, [])["candidates"][0]
        self.assertEqual(candidate["confidence"], "low")
        self.assertTrue(any("Single weak clue" in note for note in candidate["notes"]))

    def test_landing_page_only_evidence_never_reaches_medium(self):
        evidence = {"campaigns": [], "ad_groups": [], "keywords": [], "ads": [], "assets": []}
        pages = [
            {
                "ok": True,
                "url": "https://example.com/",
                "title": "AC Repair and Air Conditioning Repair",
                "h1": ["AC Repair"],
                "headings": ["Air Conditioning Repair"],
                "service_text": "We handle ac repair across the metro.",
            }
        ]
        candidate = classify_services(evidence, pages, self.lexicon, [])["candidates"][0]
        self.assertEqual(candidate["confidence"], "low")
        self.assertTrue(any("Landing-page evidence only" in note for note in candidate["notes"]))

    def test_unmatched_campaign_names_are_reported(self):
        evidence = {
            "campaigns": [{"id": "1", "name": "Search | Brand | Dallas"}],
            "ad_groups": [],
            "keywords": [],
            "ads": [],
            "assets": [],
        }
        result = classify_services(evidence, [], self.lexicon, ["brand", "search"])
        unmatched = result["unmatched_signals"]["names_without_a_service_match"]
        self.assertEqual(unmatched[0]["text"], "Search | Brand | Dallas")
        self.assertEqual(
            [item["term"] for item in result["unmatched_signals"]["residual_terms"]], ["dallas"]
        )

    def test_word_boundaries_prevent_false_positives(self):
        evidence = {
            "campaigns": [{"id": "1", "name": "HVAC Repair"}],
            "ad_groups": [],
            "keywords": [],
            "ads": [],
            "assets": [],
        }
        result = classify_services(evidence, [], self.lexicon, [])
        self.assertEqual(result["candidates"], [])

    def test_shipped_lexicon_loads(self):
        terms, ignore_terms = load_service_lexicon()
        canonicals = {term.canonical for term in terms}
        self.assertIn("paver patio installation", canonicals)
        self.assertIn("AC repair", canonicals)
        self.assertIn("lawn care and mowing", canonicals)
        self.assertTrue(ignore_terms)


class LandingPageTests(unittest.TestCase):
    HTML = """
    <html><head><title>Paver Patios in Dallas | Pro Green</title>
    <link rel="canonical" href="/paver-patios">
    <meta name="description" content="Paver patio installation.">
    <script>var services = ['not a heading'];</script></head>
    <body><h1>Paver Patio Installation</h1><h2>Retaining Walls</h2>
    <p>We build paver patios and retaining walls.</p>
    <form action="/lead"><input name="email"><button>Submit</button></form>
    </body></html>
    """

    def test_parse_extracts_headings_and_canonical(self):
        page = parse_page(self.HTML, url="https://example.com/p", final_url="https://example.com/p")
        self.assertEqual(page.title, "Paver Patios in Dallas | Pro Green")
        self.assertEqual(page.h1, ["Paver Patio Installation"])
        self.assertIn("Retaining Walls", page.headings)
        self.assertEqual(page.canonical_url, "https://example.com/paver-patios")
        self.assertNotIn("not a heading", page.service_text)
        self.assertIn("paver patios and retaining walls", page.service_text)

    def test_non_http_scheme_is_refused(self):
        page = read_landing_page("file:///etc/hosts")
        self.assertFalse(page.ok)
        self.assertIn("non-http", page.error)

    def test_hosts_outside_the_account_are_refused(self):
        page = read_landing_page(
            "https://someone-else.example/", allowed_hosts=["example.com"]
        )
        self.assertFalse(page.ok)
        self.assertIn("not one of the account", page.error)

    def test_only_get_is_used(self):
        calls = []

        class _Session:
            def get(self, url, **kwargs):
                calls.append((url, kwargs))
                return type(
                    "Response",
                    (),
                    {
                        "status_code": 200,
                        "url": url,
                        "headers": {"Content-Type": "text/html"},
                        "text": LandingPageTests.HTML,
                    },
                )()

            def __getattr__(self, name):
                raise AssertionError(f"landing-page reading must never call {name!r}")

        page = read_landing_page("https://example.com/p", session=_Session())
        self.assertTrue(page.ok)
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0][1]["allow_redirects"])


class ShippedDocumentTests(unittest.TestCase):
    def test_template_and_client_documents(self):
        template = load_yaml(ROOT / "clients" / "_template" / "service-discovery.yaml")
        errors = validate_service_discovery(template)
        # The template intentionally ships with placeholders.
        self.assertTrue(all("task." not in error for error in errors))

        document = load_yaml(ROOT / "clients" / "pro-green-dallas" / "service-discovery.yaml")
        self.assertEqual(validate_service_discovery(document), [])
        target = discovery_target(document)
        self.assertEqual(target.exact_child_account_name, "Pro Green - Dallas - Live")
        self.assertEqual(target.child_customer_id, "8735782888")
        self.assertEqual(target.manager_customer_id, "3373711342")


if __name__ == "__main__":
    unittest.main()
