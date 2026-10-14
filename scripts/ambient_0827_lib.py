#!/usr/bin/env python3
"""Shared read-only helpers for the Ambient Cooling 2026-08-27 audit run.

No mutation code lives in this module. Every helper wraps
``run_read_only_query``, which rejects anything that is not a SELECT.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.service_discovery import run_read_only_query  # noqa: E402
from gm_gsa.google_ads import enum_name as E  # noqa: E402

CID = "2401959466"
EXACT_NAME = "Ambient Cooling - Live"
GM_MANAGER = "3373711342"
CC_MANAGER = "2815082755"
TZ = ZoneInfo("America/New_York")

CLIENT_DIR = ROOT / "clients" / "ambient-cooling-heating"
SNAP = CLIENT_DIR / "snapshots"
EXPORTS = CLIENT_DIR / "exports"
RECEIPTS = CLIENT_DIR / "receipts"
PLANS = CLIENT_DIR / "plans"
REPORTS = ROOT / "reports" / "ambient-cooling-heating"

FIVE = ["24132507741", "24132507744", "24132507747", "24132507750", "24132507753"]
IN5 = ",".join(FIVE)
NAME = {
    "24132507741": "AC Repair",
    "24132507744": "Gas Boiler Repair",
    "24132507747": "HVAC Installation",
    "24132507750": "HVAC Repair",
    "24132507753": "HVAC Replacement",
}

AUGUST_MAX = 13000.00
MONTH_START = datetime.date(2026, 8, 1)
MONTH_END = datetime.date(2026, 8, 31)
LAUNCH = datetime.date(2026, 8, 14)

# Settled/partial split for this run.
TODAY = datetime.date(2026, 8, 27)
LAST_SETTLED = datetime.date(2026, 8, 26)

WINDOWS = {
    "mtd_settled": ("2026-08-01", "2026-08-26"),
    "today_partial": ("2026-08-27", "2026-08-27"),
    "since_last_audit": ("2026-08-22", "2026-08-26"),
    "before_change": ("2026-08-18", "2026-08-21"),
    "change_day_partial": ("2026-08-22", "2026-08-22"),
    "after_change": ("2026-08-23", "2026-08-26"),
    "launch_to_date": ("2026-08-14", "2026-08-26"),
    "last_30": ("2026-07-29", "2026-08-27"),
    "last_90": ("2026-05-30", "2026-08-27"),
    "last_365": ("2025-08-28", "2026-08-27"),
    "all_history": ("2019-01-01", "2026-08-27"),
}

METRICS = (
    "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, "
    "metrics.average_cpc, metrics.conversions, metrics.all_conversions, "
    "metrics.conversions_value, metrics.all_conversions_value"
)
IS_METRICS = (
    "metrics.search_impression_share, metrics.search_budget_lost_impression_share, "
    "metrics.search_rank_lost_impression_share, metrics.search_absolute_top_impression_share"
)


def client():
    load_dotenv_if_available(ROOT / ".env")
    return load_google_ads_client()


def q(c, query):
    return list(run_read_only_query(c, CID, query))


def identity_gate(c, verbose=True):
    """Hard identity gate. Exits the process on any mismatch."""
    row = q(c, """
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               customer.time_zone, customer.manager, customer.test_account,
               customer.auto_tagging_enabled, customer.status,
               customer.tracking_url_template, customer.final_url_suffix,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.conversion_tracking_status,
               customer.optimization_score
        FROM customer
    """)[0].customer
    checks = {
        "descriptive_name == 'Ambient Cooling - Live'": row.descriptive_name == EXACT_NAME,
        "customer.id == 2401959466": str(row.id) == CID,
        "not a manager account": not row.manager,
        "not a test account": not row.test_account,
        "time_zone == America/New_York": row.time_zone == "America/New_York",
        "currency_code == USD": row.currency_code == "USD",
    }
    links = {}
    for x in q(c, """
        SELECT customer_manager_link.manager_customer,
               customer_manager_link.status
        FROM customer_manager_link
    """):
        links[x.customer_manager_link.manager_customer.split("/")[-1]] = E(
            x.customer_manager_link.status
        )
    checks["Green Marketing manager 3373711342 ACTIVE"] = links.get(GM_MANAGER) == "ACTIVE"
    checks["ClickCease manager 2815082755 ACTIVE"] = links.get(CC_MANAGER) == "ACTIVE"

    if verbose:
        for k, v in checks.items():
            print(f"  [{'PASS' if v else 'FAIL'}] {k}")
        print(f"  manager links: {links}")
    if not all(checks.values()):
        sys.exit("HARD STOP: identity gate failed. No further account work.")
    return {
        "customer_id": str(row.id),
        "descriptive_name": row.descriptive_name,
        "currency": row.currency_code,
        "time_zone": row.time_zone,
        "manager": row.manager,
        "test_account": row.test_account,
        "status": E(row.status),
        "auto_tagging_enabled": row.auto_tagging_enabled,
        "tracking_url_template": row.tracking_url_template,
        "final_url_suffix": row.final_url_suffix,
        "conversion_tracking_id": str(
            row.conversion_tracking_setting.conversion_tracking_id
        ),
        "conversion_tracking_status": E(
            row.conversion_tracking_setting.conversion_tracking_status
        ),
        "optimization_score": row.optimization_score,
        "manager_links": links,
        "checks": checks,
        "checked_local": datetime.datetime.now(TZ).isoformat(),
    }


def m(r):
    x = r.metrics
    return {
        "impressions": x.impressions,
        "clicks": x.clicks,
        "cost": round(x.cost_micros / 1e6, 2),
        "ctr": round(x.ctr * 100, 2),
        "avg_cpc": round(x.average_cpc / 1e6, 2),
        "conversions": round(x.conversions, 2),
        "all_conversions": round(x.all_conversions, 2),
        "conv_value": round(x.conversions_value, 2),
    }


def write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")
