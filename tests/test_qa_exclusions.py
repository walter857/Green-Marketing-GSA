from pathlib import Path

from gm_gsa.qa_exclusions import QARules, split_qa


def _rules(tmp_path: Path) -> QARules:
    p = tmp_path / "client.yaml"
    p.write_text(
        "qa_exclusions:\n"
        "  identities:\n"
        "    - email: qa@example.com\n"
        "      phone_e164: \"+584242773462\"\n"
        "  label_marker: \"TEST - DO NOT DISPATCH\"\n"
        "  known_qa_leads:\n"
        "    - {whatconverts_lead_id: \"111\"}\n",
        encoding="utf-8")
    return QARules.from_client_yaml(p)


def test_each_rule_excludes(tmp_path):
    r = _rules(tmp_path)
    assert r.reason({"lead_id": 111}) == "known_qa_lead_id"
    assert r.reason({"lead_id": 2, "email_address": "QA@Example.com"}) == "qa_email"
    # a US input mask turns +58 424-277-3462 into (584) 242-7734
    assert r.reason({"lead_id": 3, "additional_fields": {"Phone": "(584) 242-7734"}}) == "qa_phone"
    assert r.reason({"lead_id": 4, "additional_fields": {"Name": "test — do not dispatch"}}) == "qa_marker"


def test_real_leads_kept(tmp_path):
    r = _rules(tmp_path)
    real = {"lead_id": 5, "email_address": "someone@home.net",
            "phone_number": "+14105550100", "additional_fields": {"Name": "Jane"}}
    kept, excluded = split_qa([real, {"lead_id": 111}], r)
    assert kept == [real]
    assert excluded == [("111", "known_qa_lead_id")]
