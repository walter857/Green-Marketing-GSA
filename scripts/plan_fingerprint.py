#!/usr/bin/env python3
"""Deterministic approval fingerprints for a Green Marketing remediation plan.

Uses the repository's existing fingerprint function, gm_gsa.safety.approval_code, so a
fingerprint printed here is byte-identical to one produced anywhere else in the project.
scripts/approval_code.py wraps the same function but additionally enforces the
campaign-plan schema, which does not apply to a remediation plan, so this CLI exists for
plans of that shape.

Read-only. Changes nothing locally and nothing in Google Ads.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

SUBPLANS = ["STATUS", "BUDGET", "EXISTING_RESOURCES", "CONVERSIONS",
            "CREATE_PAUSED", "SITE_OR_TRACKING", "ENABLE"]


def count_objects(block) -> int:
    if isinstance(block, dict):
        actions = block.get("actions")
        if isinstance(actions, list):
            return sum(int(a.get("object_count", 1)) for a in actions)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--emit", choices=["table", "markdown"], default="table")
    args = ap.parse_args()

    doc = load_yaml(args.plan)
    assert_no_embedded_secrets(doc)
    plan = doc["change_plan"]
    target = plan["target"]

    master_payload = {
        "target": target,
        "subplans": {name: plan["subplans"].get(name) for name in SUBPLANS},
    }
    master = approval_code(master_payload)

    rows = []
    for name in SUBPLANS:
        block = plan["subplans"].get(name)
        actions = (block or {}).get("actions") or []
        if not actions:
            rows.append((name, 0, 0, "", (block or {}).get("empty_reason", "")))
            continue
        payload = {"target": target, "subplan": name, "actions": actions}
        rows.append((name, len(actions), count_objects(block), approval_code(payload), ""))

    if args.emit == "markdown":
        print(f"**Account:** {target['exact_child_account_name']} | "
              f"`{target['child_customer_id']}` | {target['exact_service']}")
        print(f"\n**MASTER PLAN FINGERPRINT: `{master}`**\n")
        print("| Subplan | Actions | Objects | Fingerprint | Paste-back approval |")
        print("|---|---|---|---|---|")
        for name, n, objs, fp, reason in rows:
            if not fp:
                print(f"| {name} | 0 | 0 | _(empty)_ | _{reason}_ |")
            else:
                print(f"| {name} | {n} | {objs} | `{fp}` | "
                      f"`APPROVE {name} {fp} FOR 7380491929` |")
    else:
        print(f"target: {target['exact_child_account_name']} | "
              f"{target['child_customer_id']} | {target['exact_service']}")
        print(f"MASTER: {master}")
        for name, n, objs, fp, reason in rows:
            if fp:
                print(f"  {name:<20} actions={n:<4} objects={objs:<4} {fp}")
                print(f"      APPROVE {name} {fp} FOR {target['child_customer_id']}")
            else:
                print(f"  {name:<20} EMPTY  ({reason})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
