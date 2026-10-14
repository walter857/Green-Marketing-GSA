"""Format-independent lead_id guard proposed for the Apogee GTM trigger (draft, not deployed).

GTM web-container "matches RegEx (ignore case)" evaluates a JavaScript RegExp with the i flag. The pattern
below uses only syntax that behaves identically in Python `re` with IGNORECASE (negative lookahead,
character classes, bounded repetition), so this test models it faithfully for ASCII input.

It rejects values that can never be a real accepted-lead ID whatever format the developer ships; it does
NOT enforce a numeric or UUID format (that tightening waits for the developer's actual format), and it
cannot detect a *stale but well-formed* ID reused for a different lead - that is enforced server-side
(one-time token, cache exclusion) and proven by the acceptance test "second legitimate submission".
"""
import re

GUARD = (r"^(?!(?:undefined|null|nan|none|false|true|0|lead_?id|entry_?id|test|example|placeholder|sample)$)"
         r"[^\s\"'<>{}\[\]%]{1,128}$")


def ok(v):
    v = "" if v is None else str(v)
    return re.search(GUARD, v, re.IGNORECASE) is not None


REJECT = [None, "", " ", "   ", "\t", "undefined", "Undefined", "null", "NULL", "NaN", "none", "false", "0",
          "lead_id", "leadid", "entry_id", "{entry_id}", "{{lead_id}}", "[lead_id]", "%lead_id%", "<id>",
          "test", "EXAMPLE", "placeholder", "sample", "12 34", "a" * 129, "someone@example.com trailing"]
ACCEPT = ["1842", "000123", "123456789012", "gf1-1842", "a1B2c3", "3f2b8c1e-7d4a-4c1b-9a0e-2f6d5c4b3a21",
          "lead_20260928_0001", "a" * 128]


def test_guard_rejects_invalid_values():
    bad = [v for v in REJECT if ok(v)]
    assert not bad, bad


def test_guard_accepts_plausible_ids_of_any_format():
    bad = [v for v in ACCEPT if not ok(v)]
    assert not bad, bad


def test_live_pattern_is_weaker():
    live = ".+"
    assert re.search(live, "undefined") and re.search(live, " ") and re.search(live, "{entry_id}")
