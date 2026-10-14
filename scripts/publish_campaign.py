#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.campaign_builder import publish_plan_paused
from gm_gsa.config import load_dotenv_if_available, load_yaml
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import get_customer_identity
from gm_gsa.safety import assert_create_paused_approved
from gm_gsa.validators import assert_valid_campaign_plan
from gm_gsa.work_orders import assert_valid_work_order


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    parser.add_argument("--client", required=True)
    parser.add_argument("--work-order", required=True)
    parser.add_argument("--approval-code", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--receipt", default="work/publish-receipt.json")
    args = parser.parse_args()

    plan = load_yaml(args.plan)
    profile = load_yaml(args.client)
    work_order = load_yaml(args.work_order)
    assert_valid_work_order(work_order, profile)
    assert_valid_campaign_plan(plan)
    permissions = profile["client"].get("permissions") or {}
    if not permissions.get("allow_create_paused"):
        print("Client profile does not authorize create-paused operations.")
        return 1
    if not args.execute:
        print("Dry run only. Production publishing is disabled pending independent approval.")
        return 0
    print("REFUSED: independent approval and protected execution infrastructure are not configured.")
    return 1

    load_dotenv_if_available(ROOT / ".env")
    google_client = load_google_ads_client()
    identity = get_customer_identity(google_client, plan["target"]["child_customer_id"])
    if identity.manager or identity.test_account:
        print("Refusing to publish to a manager or test account.")
        return 1
    assert_create_paused_approved(
        plan,
        profile,
        args.approval_code,
        observed_account_name=identity.descriptive_name,
    )

    print(
        f"Creating PAUSED resources in {identity.descriptive_name} "
        f"({identity.customer_id})."
    )
    try:
        receipt = publish_plan_paused(google_client, plan)
    except Exception as exc:
        print(f"Publish stopped after an API error: {exc}")
        print(
            "Do not rerun blindly. Export a fresh account snapshot and inventory "
            "resources created with the plan's campaign names."
        )
        return 1

    output = Path(args.receipt)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"Create-paused complete. Receipt: {output}")
    print("Delivery was not enabled. Complete API/UI readback QA before enablement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
