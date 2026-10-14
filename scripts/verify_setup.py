#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, load_yaml, normalize_customer_id
from gm_gsa.credentials import GOOGLE_ADS_ENV_KEYS, load_google_ads_client
from gm_gsa.google_ads import get_customer_identity
from gm_gsa.work_orders import ALLOWED_VERTICALS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()

    profile = load_yaml(args.client)
    client = profile["client"]
    ads = client["google_ads"]
    normalize_customer_id(ads["child_customer_id"])
    normalize_customer_id(ads["manager_customer_id"])
    required_text = {
        "client.business_name": client.get("business_name"),
        "client.vertical": client.get("vertical"),
        "client.primary_service": client.get("primary_service"),
        "google_ads.exact_child_account_name": ads.get("exact_child_account_name"),
        "website.primary_url": client.get("website", {}).get("primary_url"),
    }
    missing_profile = [name for name, value in required_text.items() if not value]
    if client.get("vertical") not in ALLOWED_VERTICALS:
        missing_profile.append("client.vertical must be in the Green Marketing vertical scope")
    expected_name = str(ads.get("exact_child_account_name", ""))
    if ads.get("must_contain_live_marker", True) and "- live" not in expected_name.casefold():
        missing_profile.append("google_ads.exact_child_account_name must contain '- live'")
    if missing_profile:
        print("Client profile is incomplete:")
        for item in missing_profile:
            print(f"- {item}")
        return 1

    load_dotenv_if_available(ROOT / ".env")
    missing_env = [name for name in GOOGLE_ADS_ENV_KEYS if not os.getenv(name)]
    if missing_env:
        print("Local credential variables missing (values were not inspected or printed):")
        for name in missing_env:
            print(f"- {name}")
        if args.online:
            return 1
    else:
        print("Credential variable names: present")

    if args.online:
        google_client = load_google_ads_client()
        identity = get_customer_identity(google_client, ads["child_customer_id"])
        if identity.descriptive_name != ads["exact_child_account_name"]:
            print("FAIL: observed account name does not match the client profile")
            return 1
        print(
            f"Connection: OK | {identity.descriptive_name} | "
            f"{identity.customer_id} | {identity.currency_code} | {identity.time_zone}"
        )

    print("Preflight: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
