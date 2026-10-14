from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any

from .config import ConfigurationError, normalize_customer_id

SECRET_KEY_PATTERN = re.compile(
    r"(token|secret|password|api[_-]?key|refresh[_-]?token|authorization)",
    re.IGNORECASE,
)


class SafetyError(RuntimeError):
    pass


def canonical_plan_bytes(plan: dict[str, Any]) -> bytes:
    return json.dumps(
        plan,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def approval_code(plan: dict[str, Any], length: int = 12) -> str:
    return hashlib.sha256(canonical_plan_bytes(plan)).hexdigest()[:length].upper()


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            clean[key] = "[REDACTED]" if SECRET_KEY_PATTERN.search(str(key)) else redact_secrets(item)
        return clean
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value


def assert_no_embedded_secrets(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_path = f"{path}.{key}"
            if SECRET_KEY_PATTERN.search(str(key)) and item not in (None, "", "[REDACTED]"):
                raise SafetyError(f"Secret-like value is embedded at {key_path}. Use .env instead.")
            assert_no_embedded_secrets(item, key_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_no_embedded_secrets(item, f"{path}[{index}]")


def assert_target_matches(
    plan: dict[str, Any],
    client_profile: dict[str, Any],
    *,
    observed_account_name: str | None = None,
    live_marker: str = "- live",
) -> None:
    target = plan.get("target", {})
    client = client_profile.get("client", {})
    ads = client.get("google_ads", {})
    plan_id = normalize_customer_id(target.get("child_customer_id"))
    client_id = normalize_customer_id(ads.get("child_customer_id"))
    if plan_id != client_id:
        raise SafetyError(
            f"Plan customer ID {plan_id} does not match client profile {client_id}."
        )

    expected_plan_name = str(target.get("exact_child_account_name", "")).strip()
    expected_client_name = str(ads.get("exact_child_account_name", "")).strip()
    if expected_plan_name != expected_client_name:
        raise SafetyError("Plan account name does not match the client profile.")

    if ads.get("must_contain_live_marker", True):
        name_to_check = observed_account_name or expected_plan_name
        if live_marker.casefold() not in name_to_check.casefold():
            raise SafetyError(
                f"Account name does not contain required marker {live_marker!r}."
            )

    if observed_account_name and observed_account_name != expected_client_name:
        raise SafetyError(
            "Observed Google Ads account name does not match the client profile."
        )


def assert_create_paused_approved(
    plan: dict[str, Any],
    client_profile: dict[str, Any],
    supplied_code: str,
    *,
    observed_account_name: str | None = None,
) -> None:
    assert_no_embedded_secrets(plan)
    assert_target_matches(
        plan,
        client_profile,
        observed_account_name=observed_account_name,
    )
    if supplied_code.strip().upper() != approval_code(plan):
        raise SafetyError("Approval code does not match the current campaign plan.")
    for campaign in plan.get("campaigns", []):
        if campaign.get("status") != "PAUSED":
            raise SafetyError("All campaigns must be PAUSED for create-paused mode.")
