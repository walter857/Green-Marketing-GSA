#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, load_yaml, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.live_accounts import eligible_live_accounts, list_client_accounts
from gm_gsa.work_orders import assert_valid_work_order


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--marker", default="- live")
    parser.add_argument("--manager-customer-id")
    parser.add_argument("--work-order", required=True)
    parser.add_argument("--client", required=True)
    args = parser.parse_args()

    order_document = load_yaml(args.work_order)
    profile_document = load_yaml(args.client)
    assert_valid_work_order(order_document, profile_document)
    target = order_document["work_order"]["account"]

    load_dotenv_if_available(ROOT / ".env")
    manager_id = args.manager_customer_id or os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    if not manager_id:
        print("GOOGLE_ADS_LOGIN_CUSTOMER_ID is required.")
        return 1

    client = load_google_ads_client()
    accounts = eligible_live_accounts(
        list_client_accounts(client, manager_id),
        marker=args.marker,
    )
    if not accounts:
        print(f"No eligible client accounts contain {args.marker!r}.")
        return 0

    print("ACCOUNT NAME\tCUSTOMER ID\tLEVEL")
    for account in accounts:
        print(f"{account.descriptive_name}\t{account.customer_id}\t{account.level}")
    target_id = normalize_customer_id(target["child_customer_id"])
    matches = [
        account
        for account in accounts
        if account.customer_id == target_id
        and account.descriptive_name == target["exact_child_account_name"]
    ]
    if len(matches) != 1:
        print("\nFAIL: the exact work-order account name and child ID were not found together.")
        return 1
    print("\nIdentity: PASS. The name marker is still not write permission.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
