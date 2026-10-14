"""Allowlist sanitizer for WhatConverts lead rows. Nothing leaves this module unless allowlisted.

Background (2026-09-28 incident): in WhatConverts API v1 lead rows, ``phone_number`` is the CALLER's
number, not the business tracking number. A script that printed it exposed caller numbers. From now on
every lead is passed through :func:`sanitize_lead` before any count, print, log or file write.

Rules:
  * contact/PII fields are never read into the output (denylist is belt-and-braces; the allowlist rules);
  * business phone numbers appear only if they are on the caller-supplied business allowlist,
    otherwise they are replaced by ``"NON_ALLOWLISTED_NUMBER"``;
  * URLs are reduced to host + path (query strings and fragments dropped);
  * click IDs and UTMs are reported as presence booleans only, never values;
  * nested field *names* may be listed (for schema discovery), never nested values.
"""
from __future__ import annotations

import re
from typing import Any, Iterable
from urllib.parse import urlparse

CONTACT_FIELDS = frozenset({
    "phone_number", "caller_number", "caller_name", "caller_city", "caller_state", "caller_country",
    "contact_name", "contact_email_address", "contact_phone_number", "contact_company_name",
    "message", "city", "state", "country", "lead_analysis", "custom_fields", "mapped_fields",
    "additional_fields", "spotted_keywords", "ip_address", "user_agent", "email_address", "zip", "caller_zip",
    "call_transcription", "recording", "play_recording", "user_id", "destination_number",
})
SAFE_SCALARS = ("lead_type", "lead_source", "lead_medium", "lead_status", "quotable", "duplicate", "spam")
CLICK_ID_KEYS = ("gclid", "gbraid", "wbraid", "msclkid", "fbclid")
UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")
FORM_NAME_KEYS = ("Form Name", "form_name")
_DIGITS = re.compile(r"\D+")


def _digits10(value: Any) -> str:
    d = _DIGITS.sub("", str(value or ""))
    return d[-10:] if len(d) >= 10 else d


def _host_path(url: Any) -> str | None:
    if not url:
        return None
    try:
        p = urlparse(str(url))
    except ValueError:
        return "UNPARSEABLE_URL"
    return (p.netloc + p.path) or None


def _walk_keys(obj: Any, prefix: str = "") -> Iterable[str]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            name = f"{prefix}.{k}" if prefix else str(k)
            yield name
            yield from _walk_keys(v, name)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v, prefix + "[]")


def _presence(lead: dict, keys: tuple[str, ...]) -> dict[str, bool]:
    """True if any key (at any depth, case-insensitive) with that name carries a non-empty value,
    or if a URL field carries it as a query parameter. Values are never returned."""
    found = {k: False for k in keys}

    def visit(obj: Any) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                lk = str(k).strip().lower()
                if lk in found and str(v or "").strip() not in ("", "none", "null", "undefined"):
                    found[lk] = True
                visit(v)
        elif isinstance(obj, list):
            for v in obj:
                visit(v)
        elif isinstance(obj, str) and "?" in obj and "=" in obj:
            q = obj.split("?", 1)[1].lower()
            for k in found:
                if re.search(rf"(^|[&#]){k}=[^&#\s]+", q):
                    found[k] = True

    visit(lead)
    return found


def sanitize_lead(lead: dict, business_numbers: Iterable[str]) -> dict[str, Any]:
    allowed = {_digits10(n) for n in business_numbers}
    out: dict[str, Any] = {k: lead.get(k) for k in SAFE_SCALARS}
    out["date_created"] = str(lead.get("date_created") or "")[:16] or None
    tn = _digits10(lead.get("tracking_number"))
    out["tracking_number"] = (tn if tn in allowed else ("NON_ALLOWLISTED_NUMBER" if tn else None))
    out["phone_name"] = lead.get("phone_name") if tn in allowed else None
    out["landing"] = _host_path(lead.get("landing_url"))
    out["lead_url"] = _host_path(lead.get("lead_url"))
    af = lead.get("additional_fields") if isinstance(lead.get("additional_fields"), dict) else {}
    top = str(lead.get("form_name") or "").strip()
    out["form_name"] = top or next((str(af[k]) for k in FORM_NAME_KEYS if k in af and af[k]), None)
    if out["form_name"] and not re.fullmatch(r"[A-Za-z0-9 _\-|]{1,40}", out["form_name"]):
        out["form_name"] = "NON_CONFORMING_FORM_NAME"
    out["click_ids_present"] = _presence(lead, CLICK_ID_KEYS)
    out["utms_present"] = _presence(lead, UTM_KEYS)
    return out


def field_names(lead: dict) -> list[str]:
    """Schema discovery: every key name at every depth. Values are never included."""
    return sorted(set(_walk_keys(lead)))


def assert_no_pii(rendered: str, forbidden: Iterable[str]) -> None:
    """Raise if any known-forbidden token (e.g. synthetic caller values in tests) survives rendering."""
    for token in forbidden:
        if token and token in rendered:
            raise AssertionError("sanitized output still contains a forbidden token")
