from __future__ import annotations

import argparse

from .config import load_yaml
from .safety import approval_code
from .validators import validate_campaign_plan
from .work_orders import validate_work_order


def main() -> int:
    parser = argparse.ArgumentParser(prog="gm-gsa")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate-plan")
    validate_parser.add_argument("plan")
    approval_parser = subparsers.add_parser("approval-code")
    approval_parser.add_argument("plan")
    work_order_parser = subparsers.add_parser("validate-work-order")
    work_order_parser.add_argument("work_order")
    work_order_parser.add_argument("--client")
    args = parser.parse_args()

    if args.command == "validate-work-order":
        document = load_yaml(args.work_order)
        profile = load_yaml(args.client) if args.client else None
        errors = validate_work_order(document, profile)
        if errors:
            for error in errors:
                print(f"- {error}")
            return 1
        print("PASS")
        return 0

    plan = load_yaml(args.plan)
    if args.command == "validate-plan":
        errors = validate_campaign_plan(plan)
        if errors:
            for error in errors:
                print(f"- {error}")
            return 1
        print("PASS")
        return 0
    if args.command == "approval-code":
        print(approval_code(plan))
        return 0
    return 1
