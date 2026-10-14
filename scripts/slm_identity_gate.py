#!/usr/bin/env python3
"""Per-account identity confirmation read for Softwind Landscape & Masonry.

One SELECT against customer 2429758629, executed from INSIDE that account.
Read-only. Authorizes nothing. Prints the gate result and writes it to
clients/softwind-landscape-masonry/snapshots/identity-gate-<stamp>.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client

CID = "2429758629"
EXPECTED = "Softwind Landscape & Masonry - Live"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    try:
        row = list(svc.search(
            customer_id=CID,
            query="SELECT customer.id, customer.descriptive_name, customer.manager, "
                  "customer.test_account, customer.time_zone, customer.currency_code, "
                  "customer.status, customer.auto_tagging_enabled "
                  "FROM customer LIMIT 1"))[0]
    except Exception as exc:  # noqa: BLE001
        print("IDENTITY GATE: BLOCKED -> {}: {}".format(type(exc).__name__, str(exc)[:200]))
        return 2

    c = row.customer
    obs_name, obs_id = c.descriptive_name, str(c.id)
    checks = {
        "name_match": obs_name == EXPECTED,
        "id_match": obs_id == CID,
        "not_manager": not c.manager,
        "not_test": not c.test_account,
        "live_marker": "- live" in obs_name.lower(),
    }
    ok = all(checks.values())
    out = {
        "checked_at": datetime.now().astimezone().isoformat(),
        "expected_name": EXPECTED, "expected_id": CID,
        "observed_name": obs_name, "observed_id": obs_id,
        "manager": c.manager, "test_account": c.test_account,
        "time_zone": c.time_zone, "currency": c.currency_code,
        "status": c.status.name if hasattr(c.status, "name") else str(c.status),
        "auto_tagging_enabled": c.auto_tagging_enabled,
        "checks": checks, "gate": "PASS" if ok else "FAIL",
        "read_scope": "read-only; authorizes no mutation",
    }
    d = ROOT / "clients" / "softwind-landscape-masonry" / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "identity-gate-{}.json".format(datetime.now().strftime("%Y-%m-%d-%H%M"))
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    for k, v in checks.items():
        print("  {:<14} {}".format(k, v))
    print("\nobserved name : {!r}".format(obs_name))
    print("observed id   : {}".format(obs_id))
    print("tz / currency : {} / {}".format(c.time_zone, c.currency_code))
    print("status        : {}".format(out["status"]))
    print("auto-tagging  : {}".format(c.auto_tagging_enabled))
    print("\nIDENTITY GATE: {}".format(out["gate"]))
    print("receipt -> {}".format(p.relative_to(ROOT)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
