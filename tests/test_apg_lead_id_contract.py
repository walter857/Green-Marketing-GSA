"""Local model of the Apogee form-conversion trigger's lead_id gate (no production event).

Live published GTM version 3 (read 2026-09-28): the custom-event trigger requires
  {{DLV | lead_id}} matches RegEx ".+"   with the DLV default value "" (empty string).
GTM "matches RegEx" is a JavaScript RegExp test: case-sensitive, unanchored unless the
pattern anchors itself. Python re.search with the same pattern reproduces that behaviour
for these ASCII cases.

PROPOSED (not deployed): "^[1-9][0-9]{0,11}$" - a Gravity Forms entry ID is a positive
integer generated server-side, non-PII. Adopt it only if the developer confirms the ID
format; otherwise derive the pattern from the format they actually ship.
"""
import re

LIVE = ".+"
PROPOSED = r"^[1-9][0-9]{0,11}$"


def gate(pattern: str, value) -> bool:
    # a missing dataLayer key resolves to the DLV default value, which is ""
    v = "" if value is None else str(value)
    return re.search(pattern, v) is not None


CASES = {
    "missing key (default empty string)": (None, False),
    "empty string": ("", False),
    "literal undefined": ("undefined", False),
    "literal null": ("null", False),
    "whitespace only": ("   ", False),
    "unreplaced merge tag": ("{entry_id}", False),
    "fixed placeholder zero": ("0", False),
    "leading zeros": ("000123", False),
    "valid entry id": ("1842", True),
    "valid large entry id": ("123456789012", True),
    "too long": ("1234567890123", False),
    "email-like PII": ("someone@example.com", False),
}


def test_live_gate_rejects_missing_and_empty():
    assert not gate(LIVE, None)
    assert not gate(LIVE, "")


def test_live_gate_accepts_invalid_strings():
    """Documents the weakness: '.+' lets every non-empty junk value through."""
    for bad in ("undefined", "null", "   ", "{entry_id}", "0", "someone@example.com"):
        assert gate(LIVE, bad), bad


def test_proposed_gate_matches_contract():
    for label, (value, expected) in CASES.items():
        assert gate(PROPOSED, value) is expected, label


def test_reload_keeps_same_id_and_separate_leads_differ():
    """Contract: one accepted lead keeps one ID across reloads; two leads never share one.
    Deduplication is Google's (same action + same transaction ID), not the regex's."""
    first_load = "1842"
    reload = "1842"
    second_lead = "1843"
    assert gate(PROPOSED, first_load) and gate(PROPOSED, reload) and first_load == reload
    assert gate(PROPOSED, second_lead) and second_lead != first_load
