from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import normalize_customer_id


@dataclass(frozen=True)
class ClientAccount:
    customer_id: str
    descriptive_name: str
    level: int
    manager: bool
    test_account: bool
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def list_client_accounts(
    google_ads_client: Any,
    manager_customer_id: str,
) -> list[ClientAccount]:
    manager_id = normalize_customer_id(manager_customer_id)
    service = google_ads_client.get_service("GoogleAdsService")
    query = """
        SELECT
          customer_client.id,
          customer_client.descriptive_name,
          customer_client.level,
          customer_client.manager,
          customer_client.test_account,
          customer_client.status
        FROM customer_client
        WHERE customer_client.status = ENABLED
    """
    accounts: list[ClientAccount] = []
    for row in service.search(customer_id=manager_id, query=query):
        customer = row.customer_client
        accounts.append(
            ClientAccount(
                customer_id=normalize_customer_id(customer.id),
                descriptive_name=customer.descriptive_name or "",
                level=int(customer.level),
                manager=bool(customer.manager),
                test_account=bool(customer.test_account),
                status="ENABLED",
            )
        )
    return accounts


def eligible_live_accounts(
    accounts: list[ClientAccount],
    marker: str = "- live",
) -> list[ClientAccount]:
    needle = marker.casefold()
    return sorted(
        [
            account
            for account in accounts
            if needle in account.descriptive_name.casefold()
            and not account.manager
            and not account.test_account
            and account.status.upper().endswith("ENABLED")
        ],
        key=lambda account: account.descriptive_name.casefold(),
    )
