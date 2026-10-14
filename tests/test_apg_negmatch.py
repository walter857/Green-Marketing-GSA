"""Unit tests for the local negative-match approximation used in the Apogee 2026-09-28 audit.

Every case restates a documented rule from Google Ads Help answer 2453972. Queries here are
illustrative test strings, not observed search terms.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from apg_negmatch import negative_blocks, positive_reaches  # noqa: E402


def test_broad_negative_any_order():
    assert negative_blocks("shoes running blue", "running shoes", "BROAD")
    assert not negative_blocks("blue running shoe", "running shoes", "BROAD")  # no plural variant


def test_broad_negative_needs_every_word():
    assert not negative_blocks("running socks", "running shoes", "BROAD")


def test_phrase_negative_order_and_extra_words():
    assert negative_blocks("red running shoes sale", "running shoes", "PHRASE")
    assert not negative_blocks("shoes for running", "running shoes", "PHRASE")


def test_exact_negative_only_exact():
    assert negative_blocks("running shoes", "running shoes", "EXACT")
    assert not negative_blocks("running shoes sale", "running shoes", "EXACT")


def test_negative_no_close_variants():
    assert not negative_blocks("christmas light kits", "kit", "BROAD")
    assert negative_blocks("christmas light kit", "kit", "BROAD")


def test_whole_word_not_substring():
    assert not negative_blocks("parent reviews", "rent", "BROAD")
    assert not negative_blocks("jobsite lights", "job", "BROAD")


def test_case_and_punctuation():
    assert negative_blocks("How-To install", "how to", "PHRASE")
    assert negative_blocks("GOVEE lights", "govee", "PHRASE")


def test_positive_phrase_proxy_variants():
    assert positive_reaches("permanent christmas lights installation cost",
                            "permanent christmas light installation", "PHRASE")
    assert positive_reaches("permanent xmas light install", "permanent christmas light installation", "PHRASE")
    assert not positive_reaches("christmas light installation", "permanent christmas light installation", "PHRASE")


def test_positive_exact_proxy():
    assert positive_reaches("permanent christmas light", "permanent christmas lights", "EXACT")
    assert not positive_reaches("permanent christmas lights cost", "permanent christmas lights", "EXACT")
