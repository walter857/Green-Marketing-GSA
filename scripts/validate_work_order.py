#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml
from gm_gsa.work_orders import validate_work_order


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Green Marketing client work order."
    )
    parser.add_argument("work_order")
    parser.add_argument("--client")
    args = parser.parse_args()

    document = load_yaml(args.work_order)
    profile = load_yaml(args.client) if args.client else None
    errors = validate_work_order(document, profile)
    if errors:
        print("Work order is not ready:")
        for error in errors:
            print(f"- {error}")
        return 1

    order = document["work_order"]
    account = order["account"]
    service = order["service"]
    print(
        "Work order: PASS | "
        f"{account['exact_child_account_name']} | "
        f"{account['child_customer_id']} | "
        f"{service['vertical']} | {service['exact_primary_service']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
