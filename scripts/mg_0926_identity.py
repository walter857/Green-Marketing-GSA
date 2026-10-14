#!/usr/bin/env python3
"""2026-09-26 READ-ONLY identity gate + account discovery for MasterGrass - Live."""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import CID, EXACT_NAME, GM_MANAGER, TZ, EVID, client, q, write, E  # noqa: E402

c = client()
out = {}

print("=== STEP 1: MANAGER-LEVEL DISCOVERY (read-only) ===")
rows = q(
    c,
    """
    SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager,
           customer_client.test_account, customer_client.status, customer_client.level,
           customer_client.currency_code, customer_client.time_zone,
           customer_client.client_customer
    FROM customer_client
    """,
    cid=GM_MANAGER,
)
cands = []
for r in rows:
    x = r.customer_client
    cands.append({
        "id": str(x.id),
        "name": x.descriptive_name,
        "manager": x.manager,
        "test": x.test_account,
        "status": E(x.status),
        "level": x.level,
        "currency": x.currency_code,
        "tz": x.time_zone,
    })
out["manager_children"] = cands
print(f"  children visible under manager {GM_MANAGER}: {len(cands)}")
live = [x for x in cands if "- live" in (x["name"] or "").lower()]
print(f"  '- live' candidates: {len(live)}")
for x in sorted(live, key=lambda y: y["name"]):
    mark = "  <<< TARGET" if x["id"] == CID else ""
    print(f"    {x['id']:>12} lvl={x['level']} mgr={int(x['manager'])} test={int(x['test'])} "
          f"{x['status']:>8} {x['currency']} {x['tz']:<20} {x['name']}{mark}")

hit = [x for x in cands if x["id"] == CID]
print(f"\n  exact-ID match rows for {CID}: {len(hit)}")
for x in hit:
    print(f"    {x}")

print("\n=== STEP 2: DIRECT CHILD IDENTITY READ ===")
try:
    row = q(
        c,
        """
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               customer.time_zone, customer.manager, customer.test_account,
               customer.auto_tagging_enabled, customer.status,
               customer.tracking_url_template, customer.final_url_suffix,
               customer.has_partners_badge, customer.pay_per_conversion_eligibility_failure_reasons,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.google_ads_conversion_customer,
               customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
               customer.conversion_tracking_setting.accepted_customer_data_terms,
               customer.conversion_tracking_setting.conversion_tracking_status,
               customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
               customer.optimization_score
        FROM customer
        """,
    )[0].customer
except Exception as exc:  # noqa: BLE001
    print(f"  READ FAILED: {type(exc).__name__}: {exc}")
    write(EVID / "2026-09-26-identity.json", {"error": str(exc), "manager_children": cands})
    sys.exit("HARD STOP: could not read the child account.")

cts = row.conversion_tracking_setting
checks = {
    f"descriptive_name == '{EXACT_NAME}'": row.descriptive_name == EXACT_NAME,
    f"customer.id == {CID}": str(row.id) == CID,
    "name contains '- live' (case-insensitive)": "- live" in (row.descriptive_name or "").lower(),
    "not a manager account": not row.manager,
    "not a test account": not row.test_account,
    "time_zone == America/New_York": row.time_zone == "America/New_York",
    "currency_code == USD": row.currency_code == "USD",
    "auto_tagging_enabled": bool(row.auto_tagging_enabled),
}

links = {}
for x in q(c, """
    SELECT customer_manager_link.manager_customer, customer_manager_link.status
    FROM customer_manager_link
"""):
    links[x.customer_manager_link.manager_customer.split("/")[-1]] = E(
        x.customer_manager_link.status
    )
checks[f"Green Marketing manager {GM_MANAGER} ACTIVE"] = links.get(GM_MANAGER) == "ACTIVE"

for k, v in checks.items():
    print(f"  [{'PASS' if v else 'FAIL'}] {k}")
print(f"  manager links: {links}")

ident = {
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
    "optimization_score": row.optimization_score,
    "conversion_tracking_id": str(cts.conversion_tracking_id),
    "cross_account_conversion_tracking_id": str(cts.cross_account_conversion_tracking_id),
    "google_ads_conversion_customer": cts.google_ads_conversion_customer,
    "conversion_tracking_status": E(cts.conversion_tracking_status),
    "accepted_customer_data_terms": cts.accepted_customer_data_terms,
    "enhanced_conversions_for_leads_enabled": cts.enhanced_conversions_for_leads_enabled,
    "manager_links": links,
    "checks": checks,
    "checked_local": datetime.datetime.now(TZ).isoformat(),
}

print("\n=== STEP 3: CONVERSION OWNERSHIP ===")
owner = (cts.google_ads_conversion_customer or "").split("/")[-1]
print(f"  conversion_tracking_id            : {cts.conversion_tracking_id}")
print(f"  cross_account_conversion_tracking_id: {cts.cross_account_conversion_tracking_id}")
print(f"  google_ads_conversion_customer    : {owner}")
print(f"  conversion_tracking_status        : {E(cts.conversion_tracking_status)}")
print(f"  accepted_customer_data_terms      : {cts.accepted_customer_data_terms}")
print(f"  enhanced_conversions_for_leads    : {cts.enhanced_conversions_for_leads_enabled}")
if owner and owner != CID:
    print(f"  >>> CROSS-ACCOUNT: conversion actions are OWNED BY {owner}, not this child.")
else:
    print("  >>> Conversion actions are owned by THIS child account.")

out["identity"] = ident
out["conversion_owner"] = owner
write(EVID / "2026-09-26-identity.json", out)

if not all(checks.values()):
    failed = [k for k, v in checks.items() if not v]
    print("\nFAILED CHECKS: " + "; ".join(failed))
    sys.exit("HARD STOP: identity gate failed. No further account work.")
print("\nIDENTITY GATE: PASS")
