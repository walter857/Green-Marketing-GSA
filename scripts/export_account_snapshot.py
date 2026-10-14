#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, load_yaml
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import account_snapshot, get_customer_identity
from gm_gsa.work_orders import assert_valid_work_order


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-order", required=True)
    parser.add_argument("--client", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    order_document = load_yaml(args.work_order)
    profile_document = load_yaml(args.client)
    assert_valid_work_order(order_document, profile_document)
    target = order_document["work_order"]["account"]

    load_dotenv_if_available(ROOT / ".env")
    google_client = load_google_ads_client()
    identity = get_customer_identity(google_client, target["child_customer_id"])
    if identity.descriptive_name != target["exact_child_account_name"]:
        print("FAIL: observed child account name does not match the work order.")
        return 1
    snapshot = account_snapshot(google_client, target["child_customer_id"])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote read-only snapshot: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
