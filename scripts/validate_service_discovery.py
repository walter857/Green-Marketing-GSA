#!/usr/bin/env python3
"""Validate a read-only service-discovery document.

A passing document authorizes reads only. It never authorizes an audit, draft,
campaign build, campaign revamp, or any Google Ads write.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml
from gm_gsa.service_discovery import validate_service_discovery

DEFAULT_SCHEMA = ROOT / "schemas" / "service-discovery.schema.json"


def _schema_errors(document: dict, schema_path: Path) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return []
    if not schema_path.exists():
        return [f"schema file is missing: {schema_path}"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [
        "schema: " + "/".join(str(part) for part in error.path) + f": {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("discovery")
    parser.add_argument("--client", help="Optional client profile to cross-check.")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    args = parser.parse_args()

    document = load_yaml(args.discovery)
    profile = load_yaml(args.client) if args.client else None
    errors = validate_service_discovery(document, profile)
    errors.extend(_schema_errors(document, Path(args.schema)))
    if errors:
        print("Service-discovery document is not ready:")
        for error in errors:
            print(f"- {error}")
        return 1

    order = document["service_discovery"]
    account = order["account"]
    print(
        "Service discovery: PASS | "
        f"{account['exact_child_account_name']} | "
        f"child {account['child_customer_id']} | "
        f"manager {account['manager_customer_id']} | "
        f"{order['task']['type']} / {order['task']['mode']}"
    )
    print(
        "Scope: read-only service discovery. No exact service is required or asserted here. "
        "Every later workflow still requires a confirmed exact service in a work order."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
