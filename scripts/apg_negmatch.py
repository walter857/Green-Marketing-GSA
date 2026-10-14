"""Local approximation of Google Ads NEGATIVE keyword matching, plus a positive-reach proxy.

Documented negative behaviour (Google Ads Help, "About negative keywords", answer 2453972):
  * negative BROAD  - blocks a search that contains ALL the negative's words, in any order;
  * negative PHRASE - blocks a search that contains the words in the same order, with other
                      words allowed before or after;
  * negative EXACT  - blocks a search that is exactly the words, in order, with nothing added;
  * negatives do NOT match close variants: "flowers" does not block "flower", and misspellings,
    synonyms and plural/singular forms are not blocked.

Known limitations of this approximation (disclosed in the audit):
  * tokenization is lowercase, split on anything that is not a letter, digit or apostrophe;
    Google's own normalization of punctuation, accents and symbols is not published in detail;
  * the positive-reach proxy below models only literal containment plus singular/plural and
    installation/installer/install variants. Google's phrase and exact matching also matches
    queries with the same MEANING, which this proxy cannot model. A query flagged unreachable
    here may still be reachable in the live auction; a query flagged reachable may not be.
"""
from __future__ import annotations

import re

TOKEN = re.compile(r"[a-z0-9']+")


def tokens(text: str) -> list[str]:
    return TOKEN.findall((text or "").lower())


def _contains_seq(hay: list[str], needle: list[str]) -> bool:
    n = len(needle)
    return n > 0 and any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def negative_blocks(query: str, neg_text: str, match_type: str) -> bool:
    q, n = tokens(query), tokens(neg_text)
    if not n:
        return False
    mt = match_type.upper()
    if mt == "BROAD":
        return set(n) <= set(q)
    if mt == "PHRASE":
        return _contains_seq(q, n)
    if mt == "EXACT":
        return q == n
    raise ValueError(match_type)


VARIANTS = {
    "light": {"light", "lights"}, "lights": {"light", "lights"},
    "installation": {"installation", "installations", "install", "installs", "installed", "installing"},
    "installer": {"installer", "installers"},
    "christmas": {"christmas", "xmas"},
}


def _tok_eq(a: str, b: str) -> bool:
    return a == b or b in VARIANTS.get(a, set())


def positive_reaches(query: str, kw_text: str, match_type: str) -> bool:
    """Literal-containment proxy for positive PHRASE / EXACT reach (see module limitations)."""
    q, k = tokens(query), tokens(kw_text)
    n = len(k)
    if match_type.upper() == "EXACT":
        return len(q) == n and all(_tok_eq(a, b) for a, b in zip(k, q))
    if match_type.upper() == "PHRASE":
        return any(all(_tok_eq(a, b) for a, b in zip(k, q[i:i + n])) for i in range(len(q) - n + 1))
    raise ValueError(match_type)
