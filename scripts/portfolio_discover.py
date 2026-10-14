#!/usr/bin/env python3
"""Read-only discovery of '- live' child accounts + account-timezone clock probe."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.live_accounts import eligible_live_accounts, list_client_accounts


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    manager_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    if not manager_id:
        print("GOOGLE_ADS_LOGIN_CUSTOMER_ID missing")
        return 1
    client = load_google_ads_client()
    service = client.get_service("GoogleAdsService")

    every = list_client_accounts(client, manager_id)
    live = eligible_live_accounts(every)

    print(f"TOTAL ENABLED CLIENT ROWS UNDER MCC: {len(every)}")
    print(f"ELIGIBLE '- live' NON-MANAGER NON-TEST: {len(live)}\n")
    print("NAME\tID\tLEVEL")
    for a in live:
        print(f"{a.descriptive_name}\t{a.customer_id}\t{a.level}")

    print("\nNON-LIVE / EXCLUDED ROWS:")
    live_ids = {a.customer_id for a in live}
    for a in every:
        if a.customer_id not in live_ids:
            print(f"  {a.descriptive_name!r}\t{a.customer_id}\tmanager={a.manager}\ttest={a.test_account}\tlevel={a.level}")

    out = []
    print("\nPER-ACCOUNT IDENTITY + CLOCK PROBE (read-only):")
    for a in live:
        row_tz = None
        currency = None
        try:
            for r in service.search(
                customer_id=a.customer_id,
                query="SELECT customer.id, customer.descriptive_name, customer.time_zone, "
                      "customer.currency_code, customer.status, customer.manager, customer.test_account "
                      "FROM customer LIMIT 1",
            ):
                row_tz = r.customer.time_zone
                currency = r.customer.currency_code
                observed_name = r.customer.descriptive_name
                observed_id = str(r.customer.id)
        except Exception as exc:  # noqa: BLE001
            print(f"  {a.descriptive_name} ({a.customer_id}) -> ERROR {type(exc).__name__}: {exc}")
            continue

        # cheapest authoritative clock: last date with delivery this month
        dates = []
        try:
            for r in service.search(
                customer_id=a.customer_id,
                query="SELECT segments.date, metrics.impressions FROM customer "
                      "WHERE segments.date DURING THIS_MONTH ORDER BY segments.date DESC LIMIT 3",
            ):
                dates.append((r.segments.date, r.metrics.impressions))
        except Exception as exc:  # noqa: BLE001
            dates = [("ERR", str(exc)[:80])]

        match = (observed_name == a.descriptive_name) and (observed_id == a.customer_id)
        print(f"  {observed_name!r} id={observed_id} tz={row_tz} cur={currency} "
              f"identity_match={match} latest_dates={dates}")
        out.append({
            "name": observed_name, "customer_id": observed_id,
            "time_zone": row_tz, "currency": currency, "latest_dates": [d[0] for d in dates],
        })

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "portfolio-live-accounts.json").write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
