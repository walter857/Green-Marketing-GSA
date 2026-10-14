#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path

CUSTOMER_ID = re.compile(r"^[0-9]{10}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIERS = ("gclid", "gbraid", "wbraid", "email_sha256", "phone_sha256")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a CSV before Data Manager API ingestion."
    )
    parser.add_argument("csv_file")
    args = parser.parse_args()

    errors: list[str] = []
    seen_transactions: set[str] = set()
    with Path(args.csv_file).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for index, row in enumerate(rows, start=2):
        prefix = f"row {index}"
        if not CUSTOMER_ID.fullmatch(row.get("customer_id", "")):
            errors.append(f"{prefix}: invalid customer_id")
        if not row.get("conversion_action_id", "").isdigit():
            errors.append(f"{prefix}: invalid conversion_action_id")
        try:
            datetime.fromisoformat(row.get("conversion_time", "").replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{prefix}: conversion_time must be ISO 8601 with timezone")
        try:
            if float(row.get("conversion_value", "")) < 0:
                raise ValueError
        except ValueError:
            errors.append(f"{prefix}: conversion_value must be non-negative")
        if not re.fullmatch(r"[A-Z]{3}", row.get("currency", "")):
            errors.append(f"{prefix}: currency must be a 3-letter code")
        if not any(row.get(name) for name in IDENTIFIERS):
            errors.append(f"{prefix}: at least one click or hashed user identifier is required")
        for name in ("email_sha256", "phone_sha256"):
            if row.get(name) and not SHA256.fullmatch(row[name]):
                errors.append(f"{prefix}: {name} must be lowercase SHA-256 hex")
        transaction_id = row.get("transaction_id", "")
        if not transaction_id:
            errors.append(f"{prefix}: transaction_id is required for deduplication")
        elif transaction_id in seen_transactions:
            errors.append(f"{prefix}: duplicate transaction_id {transaction_id}")
        seen_transactions.add(transaction_id)
        if row.get("ad_user_data") not in {"GRANTED", "DENIED"}:
            errors.append(f"{prefix}: ad_user_data must be GRANTED or DENIED")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {len(rows)} rows ready for a Data Manager API validate-only request")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

