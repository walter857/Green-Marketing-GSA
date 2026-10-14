"""Read-only service discovery.

This module supports exactly one narrowly scoped workflow: look at a live child
account and report which services it appears to advertise, so a human can
confirm an exact service before anything else happens.

The Green Marketing gate is unchanged everywhere else. A service-discovery
document authorizes reads only. It cannot authorize an audit, a draft, a
campaign build, a campaign revamp, or any Google Ads write, and it must not
assert a service of its own. See ``assert_exact_service_required``.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator
from urllib.parse import urldefrag, urlparse

from .config import PROJECT_ROOT, ConfigurationError, load_yaml, normalize_customer_id
from .google_ads import enum_name as _enum_name

DISCOVERY_TASK_TYPE = "service-discovery"
DISCOVERY_MODE = "read"
DISCOVERY_EXEMPT_TASKS = frozenset({DISCOVERY_TASK_TYPE})
DEFAULT_LIVE_MARKER = "- live"
DEFAULT_LEXICON_PATH = PROJECT_ROOT / "config" / "service-discovery-lexicon.yaml"
DEFAULT_MAX_LANDING_PAGES = 8

CLIENT_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# A discovery document discovers a service. It must never assert one, and it
# must never carry plan-shaped keys that belong to a build workflow.
FORBIDDEN_DOCUMENT_KEYS = frozenset(
    {
        "service",
        "services",
        "exact_primary_service",
        "primary_service",
        "related_services",
        "vertical",
        "campaigns",
        "ad_groups",
        "keywords",
        "plan",
        "scope_approval",
    }
)

_SELECT_RE = re.compile(r"^\s*SELECT\s", re.IGNORECASE)
_MUTATING_TOKEN_RE = re.compile(
    r"\b(MUTATE|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|UPLOAD)\b",
    re.IGNORECASE,
)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

STRUCTURAL_KINDS = frozenset({"campaign_name", "ad_group_name", "keyword"})
ACCOUNT_KINDS = frozenset(
    {
        "campaign_name",
        "ad_group_name",
        "keyword",
        "ad_headline",
        "ad_description",
        "final_url",
        "asset",
    }
)


class DiscoveryError(RuntimeError):
    """Raised when a discovery document, identity, or query fails its gate."""


# ---------------------------------------------------------------------------
# Document validation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiscoveryTarget:
    client_slug: str
    business_name: str
    exact_child_account_name: str
    child_customer_id: str
    manager_customer_id: str
    fetch_landing_pages: bool = True
    max_landing_pages: int = DEFAULT_MAX_LANDING_PAGES
    allowed_hosts: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_text(mapping: dict[str, Any], field: str, path: str, errors: list[str]) -> str:
    value = str(mapping.get(field, "")).strip()
    if not value:
        errors.append(f"{path}.{field} is required")
    return value


def _iter_keys(value: Any, path: str = "service_discovery") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield path, str(key)
            yield from _iter_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_keys(item, f"{path}[{index}]")


def validate_service_discovery(
    document: dict[str, Any],
    client_profile: dict[str, Any] | None = None,
    *,
    live_marker: str = DEFAULT_LIVE_MARKER,
) -> list[str]:
    """Return every reason this document may not authorize a discovery read."""

    errors: list[str] = []
    order = document.get("service_discovery")
    if not isinstance(order, dict):
        return ["service_discovery must be a mapping"]

    client_slug = _required_text(order, "client_slug", "service_discovery", errors)
    if client_slug and not CLIENT_SLUG_RE.fullmatch(client_slug):
        errors.append("service_discovery.client_slug must be lowercase kebab-case")
    business_name = _required_text(order, "business_name", "service_discovery", errors)

    account = order.get("account")
    if not isinstance(account, dict):
        errors.append("service_discovery.account must be a mapping")
        account = {}
    account_name = _required_text(
        account, "exact_child_account_name", "service_discovery.account", errors
    )
    if account_name and live_marker.casefold() not in account_name.casefold():
        errors.append(
            f"service_discovery.account.exact_child_account_name must contain {live_marker!r}"
        )
    try:
        child_id = normalize_customer_id(account.get("child_customer_id"))
    except ConfigurationError as exc:
        errors.append(f"service_discovery.account.child_customer_id: {exc}")
        child_id = ""
    try:
        manager_id = normalize_customer_id(account.get("manager_customer_id"))
    except ConfigurationError as exc:
        errors.append(f"service_discovery.account.manager_customer_id: {exc}")
        manager_id = ""
    if child_id and manager_id and child_id == manager_id:
        errors.append(
            "service_discovery.account.child_customer_id must not be the manager customer ID"
        )

    task = order.get("task")
    if not isinstance(task, dict):
        errors.append("service_discovery.task must be a mapping")
        task = {}
    task_type = str(task.get("type", "")).strip()
    if task_type != DISCOVERY_TASK_TYPE:
        errors.append(
            f"service_discovery.task.type must be {DISCOVERY_TASK_TYPE!r}; "
            "audits, drafts, builds, revamps, and writes need a work order with an exact service"
        )
    mode = str(task.get("mode", "")).strip()
    if mode != DISCOVERY_MODE:
        errors.append(
            f"service_discovery.task.mode must be {DISCOVERY_MODE!r}; "
            "this document can never authorize draft, create-paused, or enable"
        )
    _required_text(task, "request", "service_discovery.task", errors)

    authorization = order.get("authorization")
    if not isinstance(authorization, dict):
        errors.append("service_discovery.authorization must be a mapping")
        authorization = {}
    if authorization.get("read_only_service_discovery") is not True:
        errors.append(
            "service_discovery.authorization.read_only_service_discovery must be true"
        )
    _required_text(authorization, "approved_by", "service_discovery.authorization", errors)
    _required_text(authorization, "granted_on", "service_discovery.authorization", errors)

    landing_pages = order.get("landing_pages", {})
    if landing_pages is None:
        landing_pages = {}
    if not isinstance(landing_pages, dict):
        errors.append("service_discovery.landing_pages must be a mapping")
        landing_pages = {}
    if "fetch" in landing_pages and not isinstance(landing_pages.get("fetch"), bool):
        errors.append("service_discovery.landing_pages.fetch must be true or false")
    if "max_pages" in landing_pages:
        max_pages = landing_pages.get("max_pages")
        if not isinstance(max_pages, int) or isinstance(max_pages, bool) or max_pages < 1:
            errors.append("service_discovery.landing_pages.max_pages must be a positive integer")
    hosts = landing_pages.get("allowed_hosts", [])
    if hosts is not None and not isinstance(hosts, list):
        errors.append("service_discovery.landing_pages.allowed_hosts must be a list")

    for parent_path, key in _iter_keys(order):
        if key in FORBIDDEN_DOCUMENT_KEYS:
            errors.append(
                f"{parent_path}.{key} is not allowed: a service-discovery document "
                "discovers services, it never asserts one or carries a plan"
            )

    if client_profile is not None:
        client = client_profile.get("client")
        if not isinstance(client, dict):
            errors.append("client profile must contain a client mapping")
            return errors
        ads = client.get("google_ads") or {}
        comparisons = [
            (client_slug, str(client.get("slug", "")).strip(), "client slug"),
            (business_name, str(client.get("business_name", "")).strip(), "business name"),
            (
                account_name,
                str(ads.get("exact_child_account_name", "")).strip(),
                "child account name",
            ),
        ]
        for order_value, profile_value, label in comparisons:
            if order_value and profile_value and order_value.casefold() != profile_value.casefold():
                errors.append(f"service discovery {label} does not match the client profile")
        for field, observed, label in (
            ("child_customer_id", child_id, "child customer ID"),
            ("manager_customer_id", manager_id, "manager customer ID"),
        ):
            try:
                profile_id = normalize_customer_id(ads.get(field))
            except ConfigurationError:
                errors.append(f"client profile google_ads.{field} is invalid")
                continue
            if observed and observed != profile_id:
                errors.append(f"service discovery {label} does not match the client profile")

    return errors


def assert_valid_service_discovery(
    document: dict[str, Any],
    client_profile: dict[str, Any] | None = None,
) -> None:
    errors = validate_service_discovery(document, client_profile)
    if errors:
        raise DiscoveryError(
            "Service-discovery document is invalid:\n- " + "\n- ".join(errors)
        )


def discovery_target(
    document: dict[str, Any],
    client_profile: dict[str, Any] | None = None,
) -> DiscoveryTarget:
    assert_valid_service_discovery(document, client_profile)
    order = document["service_discovery"]
    account = order["account"]
    landing_pages = order.get("landing_pages") or {}
    hosts = landing_pages.get("allowed_hosts") or []
    return DiscoveryTarget(
        client_slug=str(order["client_slug"]).strip(),
        business_name=str(order["business_name"]).strip(),
        exact_child_account_name=str(account["exact_child_account_name"]).strip(),
        child_customer_id=normalize_customer_id(account["child_customer_id"]),
        manager_customer_id=normalize_customer_id(account["manager_customer_id"]),
        fetch_landing_pages=bool(landing_pages.get("fetch", True)),
        max_landing_pages=int(landing_pages.get("max_pages", DEFAULT_MAX_LANDING_PAGES)),
        allowed_hosts=tuple(str(host).strip().casefold() for host in hosts if str(host).strip()),
    )


def assert_exact_service_required(task_type: str, exact_service: str | None) -> None:
    """The exact-service gate, unchanged for every workflow except discovery.

    Read-only service discovery is the only task that may run before a service
    is confirmed. Audits, drafts, builds, revamps, and writes still stop here.
    """

    normalized_task = str(task_type or "").strip()
    if normalized_task in DISCOVERY_EXEMPT_TASKS:
        return
    if not normalized_task:
        raise DiscoveryError("A task type is required before any client work.")
    if not str(exact_service or "").strip():
        raise DiscoveryError(
            f"Task {normalized_task!r} requires a confirmed exact service. "
            "Run read-only service discovery first, then have the user confirm "
            "the exact service in a work order."
        )


# ---------------------------------------------------------------------------
# Read-only Google Ads access
# ---------------------------------------------------------------------------


def assert_read_only_query(query: str) -> str:
    """Allow a GAQL SELECT and nothing else."""

    text = str(query or "").strip()
    if not _SELECT_RE.match(text):
        raise DiscoveryError("Service discovery may only run GAQL SELECT queries.")
    token = _MUTATING_TOKEN_RE.search(text)
    if token:
        raise DiscoveryError(
            f"Service discovery refused a query containing the mutating keyword {token.group(0)!r}."
        )
    return text


def run_read_only_query(client: Any, customer_id: str, query: str) -> Iterable[Any]:
    cid = normalize_customer_id(customer_id)
    safe_query = assert_read_only_query(query)
    service = client.get_service("GoogleAdsService")
    return service.search(customer_id=cid, query=safe_query)


def assert_discovery_identity(identity: Any, target: DiscoveryTarget) -> None:
    """Stop unless the observed customer is exactly the authorized child account."""

    observed_id = normalize_customer_id(getattr(identity, "customer_id", None))
    if observed_id != target.child_customer_id:
        raise DiscoveryError(
            f"Observed customer ID {observed_id} does not match the authorized "
            f"child customer ID {target.child_customer_id}."
        )
    observed_name = str(getattr(identity, "descriptive_name", "") or "")
    if observed_name != target.exact_child_account_name:
        raise DiscoveryError(
            "Observed Google Ads account name does not exactly match the authorized "
            f"child account name {target.exact_child_account_name!r}."
        )
    if getattr(identity, "manager", False):
        raise DiscoveryError("The authorized target resolved to a manager account. Stopping.")
    if getattr(identity, "test_account", False):
        raise DiscoveryError("The authorized target resolved to a test account. Stopping.")


@dataclass(frozen=True)
class ManagerLink:
    manager_customer_id: str
    child_customer_id: str
    descriptive_name: str
    level: int
    manager: bool
    test_account: bool
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


MANAGER_LINK_QUERY = """
    SELECT
      customer_client.id,
      customer_client.client_customer,
      customer_client.descriptive_name,
      customer_client.level,
      customer_client.manager,
      customer_client.test_account,
      customer_client.status
    FROM customer_client
    WHERE customer_client.id = {child_id}
"""


def get_manager_link(
    client: Any,
    manager_customer_id: str,
    child_customer_id: str,
) -> ManagerLink | None:
    manager_id = normalize_customer_id(manager_customer_id)
    child_id = normalize_customer_id(child_customer_id)
    query = MANAGER_LINK_QUERY.format(child_id=child_id)
    for row in run_read_only_query(client, manager_id, query):
        record = row.customer_client
        return ManagerLink(
            manager_customer_id=manager_id,
            child_customer_id=normalize_customer_id(record.id),
            descriptive_name=record.descriptive_name or "",
            level=int(record.level),
            manager=bool(record.manager),
            test_account=bool(record.test_account),
            status=_enum_name(record.status),
        )
    return None


def assert_manager_link(link: ManagerLink | None, target: DiscoveryTarget) -> None:
    if link is None:
        raise DiscoveryError(
            f"Child customer ID {target.child_customer_id} is not linked under manager "
            f"{target.manager_customer_id}. Stopping."
        )
    if link.child_customer_id != target.child_customer_id:
        raise DiscoveryError("The manager link returned a different child customer ID. Stopping.")
    if link.descriptive_name != target.exact_child_account_name:
        raise DiscoveryError(
            "The manager link account name does not exactly match the authorized "
            f"child account name {target.exact_child_account_name!r}."
        )
    if link.manager:
        raise DiscoveryError("The linked account is a manager account. Stopping.")
    if link.test_account:
        raise DiscoveryError("The linked account is a test account. Stopping.")
    if link.level < 1:
        raise DiscoveryError(
            "The linked account is the manager itself, not a child account. Stopping."
        )
    if link.status.upper() != "ENABLED":
        raise DiscoveryError(f"The linked child account status is {link.status}, not ENABLED.")


CAMPAIGN_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      campaign.advertising_channel_sub_type
    FROM campaign
    WHERE campaign.status = ENABLED
"""

NON_REMOVED_CAMPAIGN_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type
    FROM campaign
    WHERE campaign.status != REMOVED
"""

AD_GROUP_QUERY = """
    SELECT
      ad_group.id,
      ad_group.name,
      ad_group.status,
      campaign.id,
      campaign.name
    FROM ad_group
    WHERE ad_group.status = ENABLED
      AND campaign.status = ENABLED
"""

KEYWORD_QUERY = """
    SELECT
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      ad_group_criterion.status,
      ad_group_criterion.final_urls,
      ad_group.id,
      ad_group.name,
      campaign.id,
      campaign.name
    FROM ad_group_criterion
    WHERE ad_group_criterion.type = KEYWORD
      AND ad_group_criterion.negative = FALSE
      AND ad_group_criterion.status = ENABLED
      AND ad_group.status = ENABLED
      AND campaign.status = ENABLED
"""

AD_QUERY = """
    SELECT
      ad_group_ad.ad.id,
      ad_group_ad.ad.type,
      ad_group_ad.ad.final_urls,
      ad_group_ad.ad.responsive_search_ad.headlines,
      ad_group_ad.ad.responsive_search_ad.descriptions,
      ad_group_ad.ad.responsive_search_ad.path1,
      ad_group_ad.ad.responsive_search_ad.path2,
      ad_group_ad.status,
      ad_group_ad.policy_summary.approval_status,
      ad_group_ad.policy_summary.review_status,
      ad_group.id,
      ad_group.name,
      campaign.id,
      campaign.name
    FROM ad_group_ad
    WHERE ad_group_ad.status = ENABLED
      AND ad_group.status = ENABLED
      AND campaign.status = ENABLED
"""

_ASSET_FIELDS = """
      asset.id,
      asset.name,
      asset.type,
      asset.final_urls,
      asset.sitelink_asset.link_text,
      asset.sitelink_asset.description1,
      asset.sitelink_asset.description2,
      asset.callout_asset.callout_text,
      asset.structured_snippet_asset.header,
      asset.structured_snippet_asset.values
"""

CAMPAIGN_ASSET_QUERY = f"""
    SELECT
{_ASSET_FIELDS},
      campaign_asset.field_type,
      campaign_asset.status,
      campaign.id,
      campaign.name,
      campaign.status
    FROM campaign_asset
    WHERE campaign_asset.status = ENABLED
      AND campaign.status = ENABLED
"""

AD_GROUP_ASSET_QUERY = f"""
    SELECT
{_ASSET_FIELDS},
      ad_group_asset.field_type,
      ad_group_asset.status,
      ad_group.id,
      ad_group.name,
      ad_group.status,
      campaign.id,
      campaign.name,
      campaign.status
    FROM ad_group_asset
    WHERE ad_group_asset.status = ENABLED
      AND ad_group.status = ENABLED
      AND campaign.status = ENABLED
"""

CUSTOMER_ASSET_QUERY = f"""
    SELECT
{_ASSET_FIELDS},
      customer_asset.field_type,
      customer_asset.status
    FROM customer_asset
    WHERE customer_asset.status = ENABLED
"""


def _text_assets(assets: Iterable[Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for asset in assets or []:
        text = str(getattr(asset, "text", "") or "").strip()
        if not text:
            continue
        pinned = getattr(asset, "pinned_field", None)
        items.append({"text": text, "pinned": _enum_name(pinned) if pinned else ""})
    return items


def _asset_record(row: Any) -> dict[str, Any]:
    asset = row.asset
    sitelink = asset.sitelink_asset
    snippet = asset.structured_snippet_asset
    return {
        "asset_id": str(asset.id),
        "asset_name": asset.name or "",
        "asset_type": _enum_name(asset.type_),
        "final_urls": [str(url) for url in asset.final_urls],
        "sitelink_text": sitelink.link_text or "",
        "sitelink_description_1": sitelink.description1 or "",
        "sitelink_description_2": sitelink.description2 or "",
        "callout_text": asset.callout_asset.callout_text or "",
        "structured_snippet_header": snippet.header or "",
        "structured_snippet_values": [str(value) for value in snippet.values],
    }


def read_enabled_campaigns(client: Any, customer_id: str) -> list[dict[str, Any]]:
    campaigns = [
        {
            "id": str(row.campaign.id),
            "name": row.campaign.name or "",
            "status": _enum_name(row.campaign.status),
            "channel_type": _enum_name(row.campaign.advertising_channel_type),
            "channel_sub_type": _enum_name(row.campaign.advertising_channel_sub_type),
        }
        for row in run_read_only_query(client, customer_id, CAMPAIGN_QUERY)
    ]
    return sorted(campaigns, key=lambda item: item["name"].casefold())


def read_non_removed_campaign_index(client: Any, customer_id: str) -> list[dict[str, Any]]:
    """Names and statuses only. Used to explain an account with nothing enabled."""

    campaigns = [
        {
            "id": str(row.campaign.id),
            "name": row.campaign.name or "",
            "status": _enum_name(row.campaign.status),
            "channel_type": _enum_name(row.campaign.advertising_channel_type),
        }
        for row in run_read_only_query(client, customer_id, NON_REMOVED_CAMPAIGN_QUERY)
    ]
    return sorted(campaigns, key=lambda item: item["name"].casefold())


def read_enabled_ad_groups(client: Any, customer_id: str) -> list[dict[str, Any]]:
    ad_groups = [
        {
            "id": str(row.ad_group.id),
            "name": row.ad_group.name or "",
            "status": _enum_name(row.ad_group.status),
            "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name or "",
        }
        for row in run_read_only_query(client, customer_id, AD_GROUP_QUERY)
    ]
    return sorted(
        ad_groups,
        key=lambda item: (item["campaign_name"].casefold(), item["name"].casefold()),
    )


def read_enabled_keywords(client: Any, customer_id: str) -> list[dict[str, Any]]:
    keywords = [
        {
            "criterion_id": str(row.ad_group_criterion.criterion_id),
            "text": row.ad_group_criterion.keyword.text or "",
            "match_type": _enum_name(row.ad_group_criterion.keyword.match_type),
            "status": _enum_name(row.ad_group_criterion.status),
            "final_urls": [str(url) for url in row.ad_group_criterion.final_urls],
            "ad_group_id": str(row.ad_group.id),
            "ad_group_name": row.ad_group.name or "",
            "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name or "",
        }
        for row in run_read_only_query(client, customer_id, KEYWORD_QUERY)
    ]
    return sorted(
        keywords,
        key=lambda item: (item["campaign_name"].casefold(), item["text"].casefold()),
    )


def read_enabled_ads(client: Any, customer_id: str) -> list[dict[str, Any]]:
    ads: list[dict[str, Any]] = []
    for row in run_read_only_query(client, customer_id, AD_QUERY):
        ad = row.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        ads.append(
            {
                "ad_id": str(ad.id),
                "ad_type": _enum_name(ad.type_),
                "status": _enum_name(row.ad_group_ad.status),
                "approval_status": _enum_name(row.ad_group_ad.policy_summary.approval_status),
                "review_status": _enum_name(row.ad_group_ad.policy_summary.review_status),
                "final_urls": [str(url) for url in ad.final_urls],
                "path1": rsa.path1 or "",
                "path2": rsa.path2 or "",
                "headlines": _text_assets(rsa.headlines),
                "descriptions": _text_assets(rsa.descriptions),
                "ad_group_id": str(row.ad_group.id),
                "ad_group_name": row.ad_group.name or "",
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name or "",
            }
        )
    return sorted(
        ads, key=lambda item: (item["campaign_name"].casefold(), item["ad_group_name"].casefold())
    )


def read_campaign_assets(client: Any, customer_id: str) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for row in run_read_only_query(client, customer_id, CAMPAIGN_ASSET_QUERY):
        record = _asset_record(row)
        record.update(
            {
                "scope": "campaign",
                "field_type": _enum_name(row.campaign_asset.field_type),
                "link_status": _enum_name(row.campaign_asset.status),
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name or "",
                "ad_group_id": "",
                "ad_group_name": "",
            }
        )
        assets.append(record)
    return assets


def read_ad_group_assets(client: Any, customer_id: str) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for row in run_read_only_query(client, customer_id, AD_GROUP_ASSET_QUERY):
        record = _asset_record(row)
        record.update(
            {
                "scope": "ad_group",
                "field_type": _enum_name(row.ad_group_asset.field_type),
                "link_status": _enum_name(row.ad_group_asset.status),
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name or "",
                "ad_group_id": str(row.ad_group.id),
                "ad_group_name": row.ad_group.name or "",
            }
        )
        assets.append(record)
    return assets


def read_customer_assets(client: Any, customer_id: str) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for row in run_read_only_query(client, customer_id, CUSTOMER_ASSET_QUERY):
        record = _asset_record(row)
        record.update(
            {
                "scope": "customer",
                "field_type": _enum_name(row.customer_asset.field_type),
                "link_status": _enum_name(row.customer_asset.status),
                "campaign_id": "",
                "campaign_name": "",
                "ad_group_id": "",
                "ad_group_name": "",
            }
        )
        assets.append(record)
    return assets


def read_url_assets(client: Any, customer_id: str) -> list[dict[str, Any]]:
    return [
        *read_campaign_assets(client, customer_id),
        *read_ad_group_assets(client, customer_id),
        *read_customer_assets(client, customer_id),
    ]


def collect_account_evidence(client: Any, target: DiscoveryTarget) -> dict[str, Any]:
    """Read every enabled resource needed to name the advertised services.

    One resource that fails to read is recorded and skipped. It never turns into
    a silent gap, and it never stops the other reads.
    """

    customer_id = target.child_customer_id
    read_errors: list[dict[str, str]] = []
    queries_executed: list[str] = []

    def read(resource: str, reader: Any, default: Any) -> Any:
        try:
            value = reader(client, customer_id)
        except DiscoveryError:
            raise
        except Exception as exc:
            read_errors.append({"resource": resource, "error": f"{type(exc).__name__}: {exc}"})
            return default
        queries_executed.append(resource)
        return value

    campaigns = read("campaign", read_enabled_campaigns, [])
    evidence: dict[str, Any] = {
        "campaigns": campaigns,
        "ad_groups": read("ad_group", read_enabled_ad_groups, []) if campaigns else [],
        "keywords": read("ad_group_criterion", read_enabled_keywords, []) if campaigns else [],
        "ads": read("ad_group_ad", read_enabled_ads, []) if campaigns else [],
        "assets": [
            *read("campaign_asset", read_campaign_assets, []),
            *read("ad_group_asset", read_ad_group_assets, []),
            *read("customer_asset", read_customer_assets, []),
        ],
        "non_removed_campaign_index": [],
        "read_errors": read_errors,
        "queries_executed": queries_executed,
    }
    if not campaigns:
        # Nothing is serving. Read names and statuses only so the report can say
        # why there is no evidence instead of reporting an empty account.
        evidence["non_removed_campaign_index"] = read(
            "campaign (non-removed index)", read_non_removed_campaign_index, []
        )
    return evidence


# ---------------------------------------------------------------------------
# Final URL collection
# ---------------------------------------------------------------------------


def _clean_url(value: str) -> str:
    text = str(value or "").strip()
    if not text or "{" in text or "}" in text:
        return ""
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return urldefrag(text).url


def collect_final_urls(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    sources: dict[str, set[str]] = {}

    def record(raw: str, source: str) -> None:
        url = _clean_url(raw)
        if not url:
            return
        counter[url] += 1
        sources.setdefault(url, set()).add(source)

    for ad in evidence.get("ads", []):
        for url in ad.get("final_urls", []):
            record(url, "ad")
    for keyword in evidence.get("keywords", []):
        for url in keyword.get("final_urls", []):
            record(url, "keyword")
    for asset in evidence.get("assets", []):
        for url in asset.get("final_urls", []):
            record(url, f"{asset.get('field_type', 'asset').lower()} asset")

    return [
        {"url": url, "references": count, "sources": sorted(sources.get(url, set()))}
        for url, count in counter.most_common()
    ]


# ---------------------------------------------------------------------------
# Service classification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ServiceTerm:
    canonical: str
    vertical: str
    synonyms: tuple[str, ...]
    generic: bool = False


def normalize_text(value: Any) -> str:
    return _NON_ALNUM_RE.sub(" ", str(value or "").casefold()).strip()


def _phrase_pattern(phrase: str) -> re.Pattern[str] | None:
    tokens = normalize_text(phrase).split()
    if not tokens:
        return None
    parts = [re.escape(token) for token in tokens]
    parts[-1] = parts[-1] + r"(?:s|es)?"
    return re.compile(r"(?<![a-z0-9])" + r"\s+".join(parts) + r"(?![a-z0-9])")


def load_service_lexicon(path: str | Path | None = None) -> tuple[list[ServiceTerm], list[str]]:
    document = load_yaml(path or DEFAULT_LEXICON_PATH)
    terms: list[ServiceTerm] = []
    for entry in document.get("services", []) or []:
        canonical = str(entry.get("canonical", "")).strip()
        if not canonical:
            continue
        synonyms = tuple(
            str(item).strip() for item in entry.get("synonyms", []) or [] if str(item).strip()
        )
        terms.append(
            ServiceTerm(
                canonical=canonical,
                vertical=str(entry.get("vertical", "")).strip(),
                synonyms=synonyms or (canonical,),
                generic=bool(entry.get("generic", False)),
            )
        )
    ignore_terms = [
        str(item).strip() for item in document.get("ignore_terms", []) or [] if str(item).strip()
    ]
    return terms, ignore_terms


def _evidence_items(
    evidence: dict[str, Any],
    landing_pages: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for campaign in evidence.get("campaigns", []):
        items.append(
            {
                "kind": "campaign_name",
                "text": campaign.get("name", ""),
                "campaign_id": campaign.get("id", ""),
                "campaign_name": campaign.get("name", ""),
                "ad_group_id": "",
                "ad_group_name": "",
                "detail": campaign.get("channel_type", ""),
            }
        )
    for group in evidence.get("ad_groups", []):
        items.append(
            {
                "kind": "ad_group_name",
                "text": group.get("name", ""),
                "campaign_id": group.get("campaign_id", ""),
                "campaign_name": group.get("campaign_name", ""),
                "ad_group_id": group.get("id", ""),
                "ad_group_name": group.get("name", ""),
                "detail": "",
            }
        )
    for keyword in evidence.get("keywords", []):
        items.append(
            {
                "kind": "keyword",
                "text": keyword.get("text", ""),
                "campaign_id": keyword.get("campaign_id", ""),
                "campaign_name": keyword.get("campaign_name", ""),
                "ad_group_id": keyword.get("ad_group_id", ""),
                "ad_group_name": keyword.get("ad_group_name", ""),
                "detail": keyword.get("match_type", ""),
            }
        )
    for ad in evidence.get("ads", []):
        context = {
            "campaign_id": ad.get("campaign_id", ""),
            "campaign_name": ad.get("campaign_name", ""),
            "ad_group_id": ad.get("ad_group_id", ""),
            "ad_group_name": ad.get("ad_group_name", ""),
        }
        for headline in ad.get("headlines", []):
            items.append(
                {"kind": "ad_headline", "text": headline.get("text", ""), "detail": ad.get("ad_id", ""), **context}
            )
        for description in ad.get("descriptions", []):
            items.append(
                {
                    "kind": "ad_description",
                    "text": description.get("text", ""),
                    "detail": ad.get("ad_id", ""),
                    **context,
                }
            )
        for url in ad.get("final_urls", []):
            cleaned = _clean_url(url)
            if cleaned:
                items.append({"kind": "final_url", "text": cleaned, "detail": "ad final URL", **context})
    for keyword in evidence.get("keywords", []):
        for url in keyword.get("final_urls", []):
            cleaned = _clean_url(url)
            if cleaned:
                items.append(
                    {
                        "kind": "final_url",
                        "text": cleaned,
                        "campaign_id": keyword.get("campaign_id", ""),
                        "campaign_name": keyword.get("campaign_name", ""),
                        "ad_group_id": keyword.get("ad_group_id", ""),
                        "ad_group_name": keyword.get("ad_group_name", ""),
                        "detail": "keyword final URL",
                    }
                )
    for asset in evidence.get("assets", []):
        context = {
            "campaign_id": asset.get("campaign_id", ""),
            "campaign_name": asset.get("campaign_name", ""),
            "ad_group_id": asset.get("ad_group_id", ""),
            "ad_group_name": asset.get("ad_group_name", ""),
        }
        texts = [
            asset.get("asset_name", ""),
            asset.get("sitelink_text", ""),
            asset.get("sitelink_description_1", ""),
            asset.get("sitelink_description_2", ""),
            asset.get("callout_text", ""),
            asset.get("structured_snippet_header", ""),
            *asset.get("structured_snippet_values", []),
        ]
        for text in texts:
            if str(text).strip():
                items.append(
                    {
                        "kind": "asset",
                        "text": str(text).strip(),
                        "detail": f"{asset.get('field_type', '')} ({asset.get('scope', '')})",
                        **context,
                    }
                )
        for url in asset.get("final_urls", []):
            cleaned = _clean_url(url)
            if cleaned:
                items.append(
                    {
                        "kind": "final_url",
                        "text": cleaned,
                        "detail": f"{asset.get('field_type', '')} asset final URL",
                        **context,
                    }
                )

    for page in landing_pages or []:
        if not page.get("ok"):
            continue
        context = {
            "campaign_id": "",
            "campaign_name": "",
            "ad_group_id": "",
            "ad_group_name": "",
        }
        for text in [page.get("title", ""), *page.get("h1", []), *page.get("headings", [])]:
            if str(text).strip():
                items.append(
                    {
                        "kind": "landing_page",
                        "text": str(text).strip(),
                        "detail": page.get("url", ""),
                        **context,
                    }
                )
        body = str(page.get("service_text", "")).strip()
        if body:
            items.append(
                {"kind": "landing_page", "text": body, "detail": page.get("url", ""), **context}
            )

    return [item for item in items if str(item.get("text", "")).strip()]


def _confidence(kinds: set[str]) -> str:
    account_kinds = kinds & ACCOUNT_KINDS
    if len(kinds) >= 3 and kinds & STRUCTURAL_KINDS and account_kinds:
        return "high"
    if len(kinds) >= 2 and account_kinds:
        return "medium"
    return "low"


def _sample(values: Iterable[str], limit: int) -> list[str]:
    seen: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.append(text)
        if len(seen) >= limit:
            break
    return seen


def classify_services(
    evidence: dict[str, Any],
    landing_pages: list[dict[str, Any]] | None = None,
    lexicon: list[ServiceTerm] | None = None,
    ignore_terms: list[str] | None = None,
) -> dict[str, Any]:
    """Group account evidence into candidate services with confidence levels."""

    if lexicon is None:
        lexicon, default_ignore = load_service_lexicon()
        if ignore_terms is None:
            ignore_terms = default_ignore
    ignore_terms = ignore_terms or []

    patterns = {
        term.canonical: [
            (synonym, pattern)
            for synonym in term.synonyms
            if (pattern := _phrase_pattern(synonym)) is not None
        ]
        for term in lexicon
    }
    by_canonical = {term.canonical: term for term in lexicon}

    items = _evidence_items(evidence, landing_pages)
    hits: dict[str, list[dict[str, Any]]] = {}
    matched_item_ids: set[int] = set()

    for index, item in enumerate(items):
        normalized = normalize_text(item["text"])
        if not normalized:
            continue
        for canonical, synonym_patterns in patterns.items():
            matched_terms = sorted(
                {synonym for synonym, pattern in synonym_patterns if pattern.search(normalized)}
            )
            if not matched_terms:
                continue
            matched_item_ids.add(index)
            hits.setdefault(canonical, []).append({**item, "matched_terms": matched_terms})

    landing_pages_attempted = bool(landing_pages)
    candidates: list[dict[str, Any]] = []
    for canonical, item_hits in hits.items():
        term = by_canonical[canonical]
        kinds = {hit["kind"] for hit in item_hits}
        confidence = _confidence(kinds)
        campaigns = {
            (hit["campaign_id"], hit["campaign_name"])
            for hit in item_hits
            if hit.get("campaign_id")
        }
        ad_groups = {
            (hit["ad_group_id"], hit["ad_group_name"], hit["campaign_name"])
            for hit in item_hits
            if hit.get("ad_group_id")
        }
        notes: list[str] = []
        if term.generic:
            notes.append(
                "Catch-all industry term. Confirm the specific service before any audit or build."
            )
        if kinds == {"landing_page"}:
            notes.append(
                "Landing-page evidence only. Site navigation often lists services the "
                "account does not advertise."
            )
        elif landing_pages_attempted and "landing_page" not in kinds:
            notes.append("No landing-page corroboration for this service.")
        if not kinds & STRUCTURAL_KINDS:
            notes.append(
                "No campaign, ad group, or keyword names support this service; ad copy or "
                "site text only."
            )
        if confidence == "low":
            notes.append("Single weak clue. Not sufficient to finalize a service.")
        if term.vertical == "similar-local-service":
            notes.append(
                "Outside the core Green Marketing verticals. Needs explicit scope approval "
                "before any work."
            )

        candidates.append(
            {
                "service": canonical,
                "vertical": term.vertical,
                "generic": term.generic,
                "confidence": confidence,
                "evidence_kinds": sorted(kinds),
                "match_count": len(item_hits),
                "matched_terms": sorted({t for hit in item_hits for t in hit["matched_terms"]}),
                "campaigns": [
                    {"id": cid, "name": name}
                    for cid, name in sorted(campaigns, key=lambda pair: pair[1].casefold())
                ],
                "ad_groups": [
                    {"id": gid, "name": name, "campaign_name": campaign}
                    for gid, name, campaign in sorted(
                        ad_groups, key=lambda triple: (triple[2].casefold(), triple[1].casefold())
                    )
                ],
                "keywords": _sample(
                    (
                        f"{hit['text']} [{hit['detail']}]"
                        for hit in item_hits
                        if hit["kind"] == "keyword"
                    ),
                    12,
                ),
                "headlines": _sample(
                    (hit["text"] for hit in item_hits if hit["kind"] == "ad_headline"), 8
                ),
                "descriptions": _sample(
                    (hit["text"] for hit in item_hits if hit["kind"] == "ad_description"), 6
                ),
                "final_urls": _sample(
                    (hit["text"] for hit in item_hits if hit["kind"] == "final_url"), 8
                ),
                "assets": _sample(
                    (
                        f"{hit['text']} ({hit['detail']})"
                        for hit in item_hits
                        if hit["kind"] == "asset"
                    ),
                    8,
                ),
                "landing_page_evidence": _sample(
                    (
                        f"{hit['text']} -> {hit['detail']}"
                        for hit in item_hits
                        if hit["kind"] == "landing_page"
                    ),
                    6,
                ),
                "notes": notes,
            }
        )

    order = {"high": 0, "medium": 1, "low": 2}
    candidates.sort(
        key=lambda item: (order[item["confidence"]], -item["match_count"], item["service"])
    )

    return {
        "candidates": candidates,
        "conflicts": _conflicts(candidates),
        "unmatched_signals": _unmatched_signals(items, matched_item_ids, ignore_terms),
    }


def _conflicts(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    ad_group_owners: dict[tuple[str, str], list[str]] = {}
    for candidate in candidates:
        for group in candidate["ad_groups"]:
            ad_group_owners.setdefault((group["id"], group["name"]), []).append(
                candidate["service"]
            )
    # Group by the service set so one shared theme is one line, not one per ad group.
    shared: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for (group_id, group_name), services in sorted(ad_group_owners.items()):
        if len(services) > 1:
            shared.setdefault(tuple(sorted(services)), []).append(
                {"id": group_id, "name": group_name}
            )
    for services, groups in shared.items():
        conflicts.append(
            {
                "type": "ad_groups_support_multiple_services",
                "ad_groups": groups,
                "services": list(services),
                "note": f"{len(groups)} ad group(s) support more than one candidate service. "
                "Confirm whether these are one service or several.",
            }
        )
    for candidate in candidates:
        if candidate["confidence"] == "low":
            conflicts.append(
                {
                    "type": "insufficient_evidence",
                    "service": candidate["service"],
                    "services": [candidate["service"]],
                    "note": "Only one kind of evidence supports this candidate.",
                }
            )
    return conflicts


def _unmatched_signals(
    items: list[dict[str, Any]],
    matched_item_ids: set[int],
    ignore_terms: list[str],
) -> dict[str, Any]:
    ignore_patterns = [
        pattern for term in ignore_terms if (pattern := _phrase_pattern(term)) is not None
    ]
    unmatched_names: list[dict[str, str]] = []
    residual: Counter[str] = Counter()
    for index, item in enumerate(items):
        if index in matched_item_ids or item["kind"] not in {"campaign_name", "ad_group_name"}:
            continue
        unmatched_names.append(
            {
                "kind": item["kind"],
                "text": item["text"],
                "campaign_name": item.get("campaign_name", ""),
            }
        )
        normalized = normalize_text(item["text"])
        for pattern in ignore_patterns:
            normalized = pattern.sub(" ", normalized)
        for token in normalized.split():
            if len(token) > 2 and not token.isdigit():
                residual[token] += 1
    return {
        "names_without_a_service_match": unmatched_names,
        "residual_terms": [
            {"term": term, "count": count} for term, count in residual.most_common(20)
        ],
    }
