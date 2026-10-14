"""Permanent guards for the campaign-negative package validator.

Fixtures are synthetic. No client search-term string appears here.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = _load("validate_negative_plan")


class NegativeMatchSemantics(unittest.TestCase):
    """Negative keywords do not match close variants. The helpers must agree."""

    def test_phrase_requires_contiguous_tokens(self):
        self.assertTrue(V.blocks("alpha beta", "PHRASE", "buy alpha beta today"))
        self.assertFalse(V.blocks("alpha beta", "PHRASE", "alpha gamma beta"))

    def test_phrase_does_not_cover_plural_or_singular(self):
        self.assertFalse(V.blocks("widget", "PHRASE", "widgets near me"))
        self.assertFalse(V.blocks("widgets", "PHRASE", "widget near me"))

    def test_phrase_does_not_cover_reordering(self):
        self.assertFalse(V.blocks("alpha beta", "PHRASE", "beta alpha"))

    def test_phrase_does_not_cover_a_misspelling(self):
        self.assertFalse(V.blocks("blingle", "PHRASE", "bingle lighting"))

    def test_exact_matches_only_the_whole_query(self):
        self.assertTrue(V.blocks("alpha beta", "EXACT", "alpha beta"))
        self.assertFalse(V.blocks("alpha beta", "EXACT", "alpha beta gamma"))

    def test_broad_ignores_order_but_needs_every_token(self):
        self.assertTrue(V.blocks("alpha beta", "BROAD", "beta gamma alpha"))
        self.assertFalse(V.blocks("alpha beta", "BROAD", "alpha gamma"))


class RedundancyRules(unittest.TestCase):
    def test_shorter_phrase_makes_longer_phrase_redundant(self):
        self.assertTrue(V.makes_redundant("for sale", "PHRASE", "widgets for sale"))

    def test_longer_phrase_does_not_make_shorter_redundant(self):
        self.assertFalse(V.makes_redundant("widgets for sale", "PHRASE", "for sale"))

    def test_broad_subset_makes_phrase_redundant(self):
        self.assertTrue(V.makes_redundant("sale widgets", "BROAD", "widgets for sale"))

    def test_exact_never_makes_a_broader_phrase_redundant(self):
        self.assertFalse(V.makes_redundant("for sale", "EXACT", "widgets for sale"))

    def test_identical_exact_is_redundant(self):
        self.assertTrue(V.makes_redundant("for sale", "EXACT", "for sale"))


class ProtectedTermGuard(unittest.TestCase):
    def test_every_agency_protected_term_is_listed(self):
        for term in ("near me", "quote", "price", "pricing", "cost", "best",
                     "hire", "local", "emergency"):
            self.assertIn(term, V.PROTECTED_TERMS)

    def test_a_protected_term_is_caught_as_a_proposal(self):
        self.assertTrue(V.contiguous(V.toks("near me"), V.toks("near me")))

    def test_a_phrase_that_merely_contains_a_protected_term_is_allowed(self):
        # A longer phrase blocks strictly less, so it is not a protected-term violation.
        self.assertFalse(V.contiguous(V.toks("acme widgets near me"), V.toks("near me")))


class VoidFingerprintGuard(unittest.TestCase):
    def test_both_voided_codes_are_registered(self):
        self.assertEqual(V.VOID_FINGERPRINTS, {"2D87A5249784", "4EEF81C7F2F5"})


class ScopeGuard(unittest.TestCase):
    def test_only_the_two_approved_campaigns_are_allowed(self):
        self.assertEqual(V.ALLOWED_CAMPAIGNS, {"24053505504", "24053505501"})

    def test_only_campaign_negative_creation_is_allowed(self):
        self.assertEqual(V.ALLOWED_OPERATIONS, {"ADD_CAMPAIGN_NEGATIVE_KEYWORD"})

    def test_phase_1_negatives_are_registered_for_the_duplication_check(self):
        self.assertEqual(len(V.PHASE1_NEGATIVES), 8)


class DecisionTableIntegrity(unittest.TestCase):
    """The adjudicated table must stay internally consistent."""

    def setUp(self):
        self.DEC = _load("pga_decisions_2026_08_22")

    def test_every_verified_competitor_phrase_carries_evidence(self):
        for phrase in set(self.DEC.COMPETITOR_VERIFIED.values()):
            self.assertIn(phrase, self.DEC.COMPETITOR_EVIDENCE, phrase)
            self.assertTrue(self.DEC.COMPETITOR_EVIDENCE[phrase].strip())

    def test_every_wrong_market_phrase_carries_evidence(self):
        for phrase in set(self.DEC.WRONG_MARKET.values()):
            self.assertIn(phrase, self.DEC.WRONG_MARKET_EVIDENCE, phrase)

    def test_every_wrong_service_phrase_carries_evidence(self):
        for phrase in set(self.DEC.WRONG_SERVICE.values()):
            self.assertIn(phrase, self.DEC.WRONG_SERVICE_EVIDENCE, phrase)

    def test_no_term_is_both_blocked_and_watched(self):
        blocked = (set(self.DEC.COMPETITOR_VERIFIED) | set(self.DEC.WRONG_MARKET)
                   | set(self.DEC.WRONG_SERVICE))
        watched = set(self.DEC.WATCH_OVERRIDES) | set(self.DEC.COMPETITOR_UNVERIFIED_RESIDUE)
        self.assertEqual(blocked & watched, set())

    def test_no_generic_landscaping_term_is_proposed_as_a_negative(self):
        blocked = (set(self.DEC.COMPETITOR_VERIFIED) | set(self.DEC.WRONG_MARKET)
                   | set(self.DEC.WRONG_SERVICE))
        self.assertEqual(blocked & set(self.DEC.GENERIC_LANDSCAPING), set())

    def test_no_proposed_phrase_blocks_a_generic_landscaping_term(self):
        phrases = (set(self.DEC.COMPETITOR_VERIFIED.values())
                   | set(self.DEC.WRONG_MARKET.values())
                   | set(self.DEC.WRONG_SERVICE.values()))
        for phrase in phrases:
            for generic in self.DEC.GENERIC_LANDSCAPING:
                self.assertFalse(V.blocks(phrase, "PHRASE", generic),
                                 f"{phrase!r} would block {generic!r}")

    def test_no_proposed_phrase_is_a_protected_buyer_intent_term(self):
        phrases = (set(self.DEC.COMPETITOR_VERIFIED.values())
                   | set(self.DEC.WRONG_MARKET.values())
                   | set(self.DEC.WRONG_SERVICE.values()))
        for phrase in phrases:
            for protected in V.PROTECTED_TERMS:
                self.assertFalse(V.contiguous(V.toks(phrase), V.toks(protected)),
                                 f"{phrase!r} would suppress {protected!r}")

    def test_no_proposed_phrase_duplicates_a_phase_1_negative(self):
        phrases = (set(self.DEC.COMPETITOR_VERIFIED.values())
                   | set(self.DEC.WRONG_MARKET.values())
                   | set(self.DEC.WRONG_SERVICE.values()))
        self.assertEqual(phrases & {V.norm(p) for p in V.PHASE1_NEGATIVES}, set())


if __name__ == "__main__":
    unittest.main()
