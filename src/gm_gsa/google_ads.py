from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import normalize_customer_id


def enum_name(value: Any) -> str:
    """Return an API enum's symbolic name.

    On Python 3.11+, ``str()`` on an ``IntEnum`` returns the numeric value, so
    the older ``str(value).split(".")[-1]`` form silently produced digits.
    """

    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name
    return str(value).split(".")[-1]


@dataclass(frozen=True)
class CustomerIdentity:
    customer_id: str
    descriptive_name: str
    currency_code: str
    time_zone: str
    manager: bool
    test_account: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_customer_identity(client: Any, customer_id: str) -> CustomerIdentity:
    cid = normalize_customer_id(customer_id)
    service = client.get_service("GoogleAdsService")
    query = """
        SELECT
          customer.id,
          customer.descriptive_name,
          customer.currency_code,
          customer.time_zone,
          customer.manager,
          customer.test_account
        FROM customer
        LIMIT 1
    """
    row = next(iter(service.search(customer_id=cid, query=query)))
    customer = row.customer
    return CustomerIdentity(
        customer_id=normalize_customer_id(customer.id),
        descriptive_name=customer.descriptive_name or "",
        currency_code=customer.currency_code or "",
        time_zone=customer.time_zone or "",
        manager=bool(customer.manager),
        test_account=bool(customer.test_account),
    )


def account_snapshot(client: Any, customer_id: str) -> dict[str, Any]:
    cid = normalize_customer_id(customer_id)
    service = client.get_service("GoogleAdsService")
    identity = get_customer_identity(client, cid)
    campaigns: list[dict[str, Any]] = []
    query = """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.advertising_channel_type,
          campaign_budget.amount_micros,
          metrics.cost_micros,
          metrics.clicks,
          metrics.conversions,
          metrics.conversions_value
        FROM campaign
        WHERE campaign.status != REMOVED
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
    """
    for row in service.search(customer_id=cid, query=query):
        campaigns.append(
            {
                "id": str(row.campaign.id),
                "name": row.campaign.name,
                "status": enum_name(row.campaign.status),
                "channel": enum_name(row.campaign.advertising_channel_type),
                "daily_budget": row.campaign_budget.amount_micros / 1_000_000,
                "cost_30d": row.metrics.cost_micros / 1_000_000,
                "clicks_30d": int(row.metrics.clicks),
                "conversions_30d": float(row.metrics.conversions),
                "conversion_value_30d": float(row.metrics.conversions_value),
            }
        )
    return {"customer": identity.to_dict(), "campaigns": campaigns}

