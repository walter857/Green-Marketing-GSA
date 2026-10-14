"""Synthetic-data tests for gm_gsa.wc_sanitize. No real lead data is used anywhere in this file."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gm_gsa.wc_sanitize import assert_no_pii, field_names, sanitize_lead  # noqa: E402

BUSINESS = ["+1 (402) 526-5754", "4022027261"]
SYNTH = {
    "lead_id": 1, "lead_type": "Phone Call", "lead_source": "google", "lead_medium": "cpc",
    "lead_status": "Unique", "quotable": "Yes", "duplicate": False, "spam": False,
    "date_created": "2026-09-28T17:41:05Z",
    "tracking_number": "+14025265754", "phone_name": "Paid LP",
    "phone_number": "+15550100111", "caller_number": "+15550100111", "caller_name": "Synthetic Caller",
    "contact_email_address": "synthetic.person@example.com", "contact_name": "Synthetic Person",
    "contact_phone_number": "(555) 010-0222", "message": "please call me at 555 010 0333",
    "landing_url": "https://offer.example.com/page/?gclid=SYNTHCLICKID123&utm_source=google&email=synthetic.person@example.com",
    "lead_url": "https://offer.example.com/page/#frag",
    "additional_fields": {"Form Name": "GF1", "Full Name": "Synthetic Person", "Email": "synthetic.person@example.com"},
    "custom_fields": {"gbraid": "SYNTHGBRAID"},
}
FORBIDDEN = ["5550100111", "555) 010-0222", "555 010 0333", "Synthetic Caller", "Synthetic Person",
             "synthetic.person@example.com", "SYNTHCLICKID123", "SYNTHGBRAID"]


def test_no_pii_or_click_id_values_survive():
    out = json.dumps(sanitize_lead(SYNTH, BUSINESS))
    assert_no_pii(out, FORBIDDEN)


def test_business_number_allowlist():
    s = sanitize_lead(SYNTH, BUSINESS)
    assert s["tracking_number"] == "4025265754" and s["phone_name"] == "Paid LP"
    other = dict(SYNTH, tracking_number="+15550100999")
    s2 = sanitize_lead(other, BUSINESS)
    assert s2["tracking_number"] == "NON_ALLOWLISTED_NUMBER" and s2["phone_name"] is None


def test_url_reduced_to_host_path():
    s = sanitize_lead(SYNTH, BUSINESS)
    assert s["landing"] == "offer.example.com/page/" and s["lead_url"] == "offer.example.com/page/"


def test_click_id_and_utm_presence_only():
    s = sanitize_lead(SYNTH, BUSINESS)
    assert s["click_ids_present"]["gclid"] is True       # from the landing URL query
    assert s["click_ids_present"]["gbraid"] is True      # from a nested field
    assert s["click_ids_present"]["wbraid"] is False
    assert s["utms_present"]["utm_source"] is True and s["utms_present"]["utm_term"] is False


def test_placeholder_click_ids_are_not_presence():
    s = sanitize_lead(dict(SYNTH, landing_url="https://x.example/?gclid=", custom_fields={"gclid": "undefined"}), BUSINESS)
    assert s["click_ids_present"]["gclid"] is False


def test_form_name_only_from_allowlisted_key():
    s = sanitize_lead(SYNTH, BUSINESS)
    assert s["form_name"] == "GF1"
    weird = dict(SYNTH, additional_fields={"Form Name": "synthetic.person@example.com"})
    assert sanitize_lead(weird, BUSINESS)["form_name"] == "NON_CONFORMING_FORM_NAME"


def test_field_names_never_include_values():
    names = field_names(SYNTH)
    assert "additional_fields.Full Name" in names
    assert_no_pii(json.dumps(names), FORBIDDEN)


def test_assert_no_pii_raises():
    with pytest.raises(AssertionError):
        assert_no_pii("x 5550100111 y", ["5550100111"])


def test_top_level_form_name_and_new_pii_fields():
    lead = dict(SYNTH, form_name="GF1", email_address="synthetic.person@example.com", zip="68000",
                call_transcription="my number is 555 010 0333", recording="https://rec.example/abc")
    out = sanitize_lead(lead, BUSINESS)
    assert out["form_name"] == "GF1"
    assert_no_pii(json.dumps(out), FORBIDDEN + ["68000", "rec.example"])
