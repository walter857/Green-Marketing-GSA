#!/usr/bin/env python3
"""Read-only Google Ads identity check for Softwind Power Washing.

Runs SELECT statements only. No mutation is possible from this script.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

EXPECTED_NAME = "Softwind Power Washing - Live"
EXPECTED_ID = "1521725229"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(EXPECTED_ID)

    out: dict = {"expected": {"name": EXPECTED_NAME, "customer_id": EXPECTED_ID}}

    q = """
        SELECT
          customer.id,
          customer.descriptive_name,
          customer.currency_code,
          customer.time_zone,
          customer.manager,
          customer.test_account,
          customer.status,
          customer.auto_tagging_enabled,
          customer.tracking_url_template,
          customer.final_url_suffix,
          customer.conversion_tracking_setting.conversion_tracking_id,
          customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
          customer.conversion_tracking_setting.conversion_tracking_status,
          customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
          customer.conversion_tracking_setting.google_ads_conversion_customer,
          customer.optimization_score,
          customer.pay_per_conversion_eligibility_failure_reasons
        FROM customer
        LIMIT 1
    """
    row = next(iter(svc.search(customer_id=cid, query=q)))
    c = row.customer
    cts = c.conversion_tracking_setting
    observed = {
        "customer_id": normalize_customer_id(c.id),
        "descriptive_name": c.descriptive_name or "",
        "currency_code": c.currency_code or "",
        "time_zone": c.time_zone or "",
        "manager": bool(c.manager),
        "test_account": bool(c.test_account),
        "status": enum_name(c.status),
        "auto_tagging_enabled": bool(c.auto_tagging_enabled),
        "tracking_url_template": c.tracking_url_template or "",
        "final_url_suffix": c.final_url_suffix or "",
        "conversion_tracking_id": str(cts.conversion_tracking_id or ""),
        "cross_account_conversion_tracking_id": str(
            cts.cross_account_conversion_tracking_id or ""
        ),
        "conversion_tracking_status": enum_name(cts.conversion_tracking_status),
        "enhanced_conversions_for_leads_enabled": bool(
            cts.enhanced_conversions_for_leads_enabled
        ),
        "google_ads_conversion_customer": cts.google_ads_conversion_customer or "",
        "optimization_score": float(c.optimization_score or 0.0),
    }
    out["observed"] = observed

    out["identity_match"] = {
        "name_matches": observed["descriptive_name"] == EXPECTED_NAME,
        "id_matches": observed["customer_id"] == EXPECTED_ID,
        "is_manager": observed["manager"],
        "is_test": observed["test_account"],
        "live_marker_present": "- live" in observed["descriptive_name"].casefold(),
    }

    # Manager link, read from the child's own customer_client view.
    links = []
    try:
        q2 = """
            SELECT
              customer_client.client_customer,
              customer_client.id,
              customer_client.descriptive_name,
              customer_client.level,
              customer_client.manager,
              customer_client.status,
              customer_client.time_zone,
              customer_client.currency_code
            FROM customer_client
        """
        for r in svc.search(customer_id=cid, query=q2):
            cc = r.customer_client
            links.append(
                {
                    "id": str(cc.id),
                    "descriptive_name": cc.descriptive_name or "",
                    "level": int(cc.level),
                    "manager": bool(cc.manager),
                    "status": enum_name(cc.status),
                    "time_zone": cc.time_zone or "",
                    "currency_code": cc.currency_code or "",
                }
            )
    except Exception as exc:  # pragma: no cover - reported, never guessed
        out["customer_client_error"] = str(exc)[:400]
    out["customer_client"] = links

    mgr = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
    mgr_view = []
    if mgr:
        try:
            q3 = """
                SELECT
                  customer_client.id,
                  customer_client.descriptive_name,
                  customer_client.level,
                  customer_client.manager,
                  customer_client.status,
                  customer_client.currency_code,
                  customer_client.time_zone
                FROM customer_client
                WHERE customer_client.id = %s
            """ % normalize_customer_id(EXPECTED_ID)
            for r in svc.search(customer_id=normalize_customer_id(mgr), query=q3):
                cc = r.customer_client
                mgr_view.append(
                    {
                        "id": str(cc.id),
                        "descriptive_name": cc.descriptive_name or "",
                        "level": int(cc.level),
                        "manager": bool(cc.manager),
                        "status": enum_name(cc.status),
                        "currency_code": cc.currency_code or "",
                        "time_zone": cc.time_zone or "",
                    }
                )
            out["manager_customer_id"] = normalize_customer_id(mgr)
        except Exception as exc:
            out["manager_view_error"] = str(exc)[:400]
    out["manager_view_of_child"] = mgr_view

    tz = observed["time_zone"] or "America/New_York"
    now_local = datetime.now(ZoneInfo(tz))
    out["timing"] = {
        "account_time_zone": tz,
        "account_local_timestamp": now_local.isoformat(),
        "account_local_date": now_local.date().isoformat(),
        "account_local_time": now_local.strftime("%H:%M:%S"),
        "machine_utc": datetime.utcnow().isoformat() + "Z",
    }

    dest = ROOT / "clients/softwind-power-washing/snapshots/identity-2026-08-25.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
