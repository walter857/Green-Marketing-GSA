from __future__ import annotations

from typing import Any

from .config import ConfigurationError, normalize_customer_id

ALLOWED_VERTICALS = {
    "landscaping",
    "hardscaping",
    "heating-cooling",
    "similar-local-service",
}
ALLOWED_MODES = {"read", "draft", "create-paused", "enable"}
ALLOWED_TASKS = {
    "onboard",
    "audit",
    "lsa",
    "keyword-research",
    "campaign-build",
    "campaign-revamp",
    "ads-assets",
    "landing-page",
    "conversions",
    "search-terms",
    "speed-to-lead",
    "sales",
    "offline-conversions",
    "reporting",
    "deployment",
    "full-system",
}


def _required_text(mapping: dict[str, Any], field: str, path: str, errors: list[str]) -> str:
    value = str(mapping.get(field, "")).strip()
    if not value:
        errors.append(f"{path}.{field} is required")
    return value


def validate_work_order(
    document: dict[str, Any],
    client_profile: dict[str, Any] | None = None,
    *,
    live_marker: str = "- live",
) -> list[str]:
    errors: list[str] = []
    work_order = document.get("work_order")
    if not isinstance(work_order, dict):
        return ["work_order must be a mapping"]

    client_slug = _required_text(work_order, "client_slug", "work_order", errors)
    business_name = _required_text(work_order, "business_name", "work_order", errors)

    account = work_order.get("account")
    if not isinstance(account, dict):
        errors.append("work_order.account must be a mapping")
        account = {}
    account_name = _required_text(
        account, "exact_child_account_name", "work_order.account", errors
    )
    if account_name and live_marker.casefold() not in account_name.casefold():
        errors.append(
            f"work_order.account.exact_child_account_name must contain {live_marker!r}"
        )
    try:
        child_id = normalize_customer_id(account.get("child_customer_id"))
    except ConfigurationError as exc:
        errors.append(f"work_order.account.child_customer_id: {exc}")
        child_id = ""

    service = work_order.get("service")
    if not isinstance(service, dict):
        errors.append("work_order.service must be a mapping")
        service = {}
    vertical = str(service.get("vertical", "")).strip()
    if vertical not in ALLOWED_VERTICALS:
        errors.append(
            "work_order.service.vertical must be landscaping, hardscaping, "
            "heating-cooling, or similar-local-service"
        )
    exact_service = _required_text(
        service, "exact_primary_service", "work_order.service", errors
    )

    task = work_order.get("task")
    if not isinstance(task, dict):
        errors.append("work_order.task must be a mapping")
        task = {}
    task_type = str(task.get("type", "")).strip()
    if task_type not in ALLOWED_TASKS:
        errors.append("work_order.task.type is not an allowed Green Marketing workflow")
    mode = str(task.get("mode", "")).strip()
    if mode not in ALLOWED_MODES:
        errors.append("work_order.task.mode must be read, draft, create-paused, or enable")
    _required_text(task, "request", "work_order.task", errors)

    scope = work_order.get("scope_approval")
    if not isinstance(scope, dict):
        errors.append("work_order.scope_approval must be a mapping")
        scope = {}
    if vertical == "similar-local-service":
        if scope.get("approved") is not True:
            errors.append("similar-local-service requires scope_approval.approved: true")
        _required_text(scope, "approved_by", "work_order.scope_approval", errors)
        _required_text(scope, "reason", "work_order.scope_approval", errors)

    if client_profile is not None:
        client = client_profile.get("client")
        if not isinstance(client, dict):
            errors.append("client profile must contain a client mapping")
            return errors
        ads = client.get("google_ads") or {}
        profile_required = {
            "client.slug": client.get("slug"),
            "client.business_name": client.get("business_name"),
            "client.vertical": client.get("vertical"),
            "client.primary_service": client.get("primary_service"),
            "client.google_ads.exact_child_account_name": ads.get(
                "exact_child_account_name"
            ),
        }
        for path, value in profile_required.items():
            if not str(value or "").strip():
                errors.append(f"{path} is required")
        comparisons = [
            (client_slug, str(client.get("slug", "")).strip(), "client slug"),
            (business_name, str(client.get("business_name", "")).strip(), "business name"),
            (account_name, str(ads.get("exact_child_account_name", "")).strip(), "child account name"),
            (vertical, str(client.get("vertical", "")).strip(), "vertical"),
        ]
        for order_value, profile_value, label in comparisons:
            if order_value and profile_value and order_value.casefold() != profile_value.casefold():
                errors.append(f"work order {label} does not match the client profile")
        # One account may carry more than one approved service, so a work order's
        # exact service matches either the profile's primary service or any service
        # the profile already records as in scope. Both are client truth; nothing
        # outside the profile is ever accepted.
        approved_services = {
            str(client.get("primary_service", "")).strip().casefold()
        }
        for entry in (client.get("offer") or {}).get("services_in_scope") or []:
            approved_services.add(str(entry).strip().casefold())
        approved_services.discard("")
        if exact_service and approved_services:
            if exact_service.casefold() not in approved_services:
                errors.append(
                    "work order primary service is not the client profile's primary "
                    "service and is not listed in client.offer.services_in_scope"
                )
        try:
            profile_id = normalize_customer_id(ads.get("child_customer_id"))
        except ConfigurationError:
            errors.append("client profile google_ads.child_customer_id is invalid")
        else:
            if child_id and child_id != profile_id:
                errors.append("work order child customer ID does not match the client profile")

    return errors


def assert_valid_work_order(
    document: dict[str, Any],
    client_profile: dict[str, Any] | None = None,
) -> None:
    errors = validate_work_order(document, client_profile)
    if errors:
        raise ValueError("Work order is invalid:\n- " + "\n- ".join(errors))
