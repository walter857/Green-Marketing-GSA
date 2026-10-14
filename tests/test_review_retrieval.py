"""Regression coverage for automatic review retrieval.

Written after a real failure: Google's review interface was unreachable, and the workflow
stopped at a placeholder even though the client's own website carried usable reviews. It
also copied one placeholder string into all three review-card fields.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.review_retrieval import (  # noqa: E402
    PLACEHOLDER,
    SOURCE_GBP,
    SOURCE_WEBSITE,
    Review,
    ReviewRetrievalError,
    retrieve_reviews,
    select_three,
)

WEBSITE_URL = "https://ekglawn.com/reviews/"


def website_reviews() -> list[Review]:
    return [
        Review("CHELLY", "If I could leave 10 stars, I would!", SOURCE_WEBSITE,
               WEBSITE_URL, "2026-08-14", "5"),
        Review("DONNA, W.", "This company is honest and fair.", SOURCE_WEBSITE,
               WEBSITE_URL, "2026-08-14", "5"),
        Review("RANDALL, L.", "They always do a great job at a fair price.", SOURCE_WEBSITE,
               WEBSITE_URL, "2026-08-14", "5"),
    ]


def gbp_reviews() -> list[Review]:
    return [
        Review("Pat M.", "Great aeration service.", SOURCE_GBP, "https://g.page/x",
               "2026-08-14", "5", service_relevant=True),
        Review("Sam T.", "Lawn looks fantastic.", SOURCE_GBP, "https://g.page/x", "2026-08-14", "5"),
        Review("Lee R.", "Reliable and tidy.", SOURCE_GBP, "https://g.page/x", "2026-08-14", "5"),
    ]


def unreachable():
    raise ConnectionError("ECONNREFUSED")


class SourceOrderTests(unittest.TestCase):
    def test_google_is_attempted_first(self):
        result = retrieve_reviews(gbp_fetcher=gbp_reviews, website_fetcher=website_reviews)
        self.assertEqual(result.source_used, SOURCE_GBP)
        self.assertEqual(result.attempts[0]["source"], SOURCE_GBP)

    def test_official_website_is_the_fallback(self):
        result = retrieve_reviews(gbp_fetcher=unreachable, website_fetcher=website_reviews)
        self.assertEqual(result.source_used, SOURCE_WEBSITE)
        self.assertEqual(result.attempts[0]["outcome"], "unreachable")

    def test_accessible_website_reviews_prevent_placeholder_output(self):
        """The exact failure this module exists to stop."""
        result = retrieve_reviews(gbp_fetcher=unreachable, website_fetcher=website_reviews)
        self.assertTrue(result.resolved)
        for card in result.card_values():
            self.assertNotIn(PLACEHOLDER, card.values())
            self.assertNotIn("REVIEW PENDING", card["text"])

    def test_placeholder_only_when_neither_source_yields_three(self):
        result = retrieve_reviews(gbp_fetcher=unreachable, website_fetcher=unreachable)
        self.assertFalse(result.resolved)
        for card in result.card_values():
            self.assertEqual(card["text"], PLACEHOLDER)

    def test_unconfirmed_listing_identity_skips_google(self):
        result = retrieve_reviews(gbp_fetcher=gbp_reviews, website_fetcher=website_reviews,
                                  identity_confirmed=False)
        self.assertEqual(result.source_used, SOURCE_WEBSITE)
        self.assertEqual(result.attempts[0]["outcome"], "identity_not_confirmed")


class CardPopulationTests(unittest.TestCase):
    def test_text_and_names_populate_their_own_fields(self):
        cards = retrieve_reviews(gbp_fetcher=unreachable,
                                 website_fetcher=website_reviews).card_values()
        self.assertEqual(cards[0]["reviewer"], "CHELLY")
        self.assertEqual(cards[0]["text"], "If I could leave 10 stars, I would!")
        self.assertEqual(cards[1]["reviewer"], "DONNA, W.")
        self.assertEqual(cards[2]["reviewer"], "RANDALL, L.")
        for card in cards:
            self.assertNotEqual(card["text"], card["reviewer"])

    def test_one_value_is_not_copied_into_every_field(self):
        cards = retrieve_reviews(gbp_fetcher=unreachable,
                                 website_fetcher=website_reviews).card_values()
        self.assertEqual(len({c["text"] for c in cards}), 3)
        self.assertEqual(len({c["reviewer"] for c in cards}), 3)
        for card in cards:
            self.assertEqual(len({card["text"], card["reviewer"], card["attribution"]}), 3)

    def test_attribution_field_carries_no_source_url(self):
        cards = retrieve_reviews(gbp_fetcher=unreachable,
                                 website_fetcher=website_reviews).card_values(
                                     customer_label="EKG Lawn Customer")
        for card in cards:
            self.assertNotIn("http", card["attribution"])
            self.assertEqual(card["attribution"], "EKG Lawn Customer")

    def test_customer_label_is_not_hard_coded_to_one_client(self):
        """The module is reusable: no client's wording may be baked into it."""
        default = retrieve_reviews(gbp_fetcher=unreachable,
                                   website_fetcher=website_reviews).card_values()
        for card in default:
            self.assertEqual(card["attribution"], "Verified Customer")
        other = retrieve_reviews(gbp_fetcher=unreachable,
                                 website_fetcher=website_reviews).card_values(
                                     customer_label="Pro-Green Customer")
        for card in other:
            self.assertEqual(card["attribution"], "Pro-Green Customer")


class ProvenanceTests(unittest.TestCase):
    def test_provenance_is_recorded_internally(self):
        result = retrieve_reviews(gbp_fetcher=unreachable, website_fetcher=website_reviews)
        prov = result.provenance()
        self.assertEqual(len(prov), 3)
        for entry in prov:
            self.assertEqual(entry["source_url"], WEBSITE_URL)
            self.assertTrue(entry["retrieved_on"])
            self.assertTrue(entry["exact_text"])

    def test_provenance_never_leaks_into_card_values(self):
        result = retrieve_reviews(gbp_fetcher=unreachable, website_fetcher=website_reviews)
        rendered = " ".join(v for c in result.card_values() for v in c.values())
        for token in ("http", "ekglawn.com/reviews", "source", "retrieved"):
            self.assertNotIn(token, rendered.lower())


class SelectionTests(unittest.TestCase):
    def test_service_relevant_reviews_are_preferred(self):
        mixed = [
            Review("A", "general", SOURCE_GBP, "u", "d"),
            Review("B", "aeration was great", SOURCE_GBP, "u", "d", service_relevant=True),
            Review("C", "general two", SOURCE_GBP, "u", "d"),
            Review("D", "overseeding was great", SOURCE_GBP, "u", "d", service_relevant=True),
        ]
        chosen = select_three(mixed)
        self.assertEqual([c.reviewer_name for c in chosen[:2]], ["B", "D"])

    def test_general_company_reviews_are_allowed_when_no_service_review_exists(self):
        chosen = select_three(website_reviews())
        self.assertEqual(len(chosen), 3)
        self.assertTrue(all(not c.service_relevant for c in chosen))

    def test_fewer_than_three_yields_nothing_rather_than_padding(self):
        self.assertEqual(select_three(website_reviews()[:2]), [])

    def test_anonymous_reviewers_are_refused(self):
        for bad in ("Anonymous", "A Google User", "Customer", "  "):
            with self.assertRaises(ReviewRetrievalError):
                select_three([Review(bad, "text", SOURCE_GBP, "u", "d")] * 3)

    def test_a_review_without_text_is_refused(self):
        with self.assertRaises(ReviewRetrievalError):
            select_three([Review("Name", "   ", SOURCE_GBP, "u", "d")] * 3)

    def test_a_review_without_a_source_url_is_refused(self):
        with self.assertRaises(ReviewRetrievalError):
            select_three([Review("Name", "text", SOURCE_GBP, "", "d")] * 3)


class NoDeveloperTodoTests(unittest.TestCase):
    def test_no_developer_todo_remains_after_successful_retrieval(self):
        cards = retrieve_reviews(gbp_fetcher=unreachable,
                                 website_fetcher=website_reviews).card_values()
        rendered = " ".join(v for c in cards for v in c.values())
        self.assertNotIn("DEVELOPER TODO", rendered)
        self.assertNotIn("Insert a review", rendered)


class LiveDocumentTests(unittest.TestCase):
    """The shipped EKG documents must stay free of TODO language."""

    def test_local_artifacts_carry_no_developer_todo(self):
        for name in ("lawn-aeration-content.md", "aeration-overseeding-content.md"):
            path = ROOT / "clients" / "ekg-lawn-services" / "landing-pages" / name
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("DEVELOPER TODO", text, name)
            self.assertEqual(text.count("IMAGE SUGGESTION:"), 9, name)
            for reviewer in ("CHELLY", "DONNA, W.", "RANDALL, L."):
                self.assertIn(reviewer, text, f"{name} missing {reviewer}")


if __name__ == "__main__":
    unittest.main()
