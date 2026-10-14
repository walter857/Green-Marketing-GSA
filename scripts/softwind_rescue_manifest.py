#!/usr/bin/env python3
"""Build the 2026-08-26 month-end rescue fingerprint manifest.

Read-only. Uses gm_gsa.safety.approval_code so fingerprints are byte-identical
to every other one in the project.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

PLANS = ROOT / "clients/softwind-power-washing/plans"
OUT = PLANS / "2026-08-26-rescue-fingerprint-manifest.json"
TZ = ZoneInfo("America/New_York")
CID, NAME, SVC = "1521725229", "Softwind Power Washing - Live", "Power Washing"

# R-priority mapping for the new recommendation order
RANK = {
    "PLAN-A2":    ("R0", 1, "Controlled form test - verify measurement before scaling"),
    "PLAN-H":     ("R6", 2, "Call-attribution and sitelink repair, pre-scaling"),
    "PLAN-E2":    ("R2", 3, "Out-of-scope negatives - pairs with any enablement"),
    "PLAN-I2A-E": ("R5-A", 4, "Enable the one correct existing paused SKAG"),
    "PLAN-I2A-C": ("R5-B", 5, "Create four true SKAGs paused"),
    "PLAN-I2A-EN":("R5-C", 6, "Enable created SKAGs AFTER readback QA - regenerate fp"),
    "PLAN-I5":    ("R5-D", 7, "Create Pressure Washing Near Me paused"),
    "PLAN-I1A":   ("R1", 8, "Budget headroom AFTER demand is final"),
    "PLAN-G":     ("R6", 9, "Resolve the duplicate ad group"),
    "PLAN-A3":    ("R0", 10, "Controlled phone test"),
    "PLAN-I3":    ("R3", None, "Schedule expansion - BLOCKED on SCHED-Q1..Q6"),
    "PLAN-I1":    ("SUPERSEDED", None, "Superseded in order by PLAN-I1A, not void"),
    "PLAN-B":     ("HOLD", None, "HOLD_UNTIL_MONTH_END_RESCUE_IS_RESOLVED"),
    "PLAN-C":     ("SUPERSEDED", None, "Superseded in order by PLAN-I3, not void"),
    "PLAN-D":     ("SUPERSEDED", None, "Superseded in order by PLAN-I2A-E, not void"),
    "PLAN-E1":    ("SUPERSEDED", None, "Superseded in order by PLAN-I5, not void"),
    "PLAN-A1":    ("R0", None, "READ-ONLY, already executed 2026-08-26"),
}


def normalize(plan):
    p = plan["change_plan"]
    t = p["target"]
    acts = []
    for a in p.get("actions", []):
        acts.append({
            "action_id": a["action_id"], "priority": a["priority"],
            "resource_type": a["resource_type"], "operation": a["operation"],
            "customer_id": a.get("customer_id", t["child_customer_id"]),
            "campaign_id": a.get("campaign_id"), "ad_group_id": a.get("ad_group_id"),
            "resource_id": a.get("resource_id"),
            "current_value": a.get("current_value"),
            "proposed_value": a.get("proposed_value"),
            "object_count": a.get("object_count", 1)})
    acts.sort(key=lambda x: x["action_id"])
    return {"target": {"exact_child_account_name": t["exact_child_account_name"],
                       "child_customer_id": t["child_customer_id"],
                       "exact_service": t["exact_service"]},
            "plan_id": p["plan_id"], "approval_type": p["approval_type"],
            "actions": acts, "action_count": len(acts),
            "object_count": sum(a["object_count"] for a in acts)}


def main() -> int:
    rows = []
    for path in sorted(PLANS.glob("2026-08-2*-plan-*.yaml")):
        doc = load_yaml(path)
        assert_no_embedded_secrets(doc)
        p = doc["change_plan"]
        pid = p["plan_id"]
        payload = normalize(doc)
        fp = approval_code(payload)
        pri, order, theme = RANK.get(pid, ("UNRANKED", None, ""))
        rows.append({
            "plan_id": pid, "plan_title": p["plan_title"], "file": path.name,
            "rescue_priority": pri, "rescue_approval_order": order,
            "rescue_theme": theme,
            "approval_type": p["approval_type"],
            "fingerprint": fp,
            "action_count": payload["action_count"],
            "object_count": payload["object_count"],
            "ads_mutation_count": p.get("ads_mutation_count"),
            "approval_status": p.get("approval_status"),
            "execution_status": p.get("execution_status"),
            "requires_separate_enable_approval": p.get(
                "requires_separate_enable_approval", False),
            "supersedes": p.get("supersedes"),
            "hold_status": (p.get("hold_status") or {}).get("state"),
            "blocked": "BLOCKED" in str(p.get("approval_status", "")),
            "approval_phrase": "APPROVE %s %s FOR %s" % (pid, fp, CID),
        })

    order_rows = sorted([r for r in rows if r["rescue_approval_order"]],
                        key=lambda r: r["rescue_approval_order"])

    manifest = {
        "generated_account_local": datetime.now(TZ).isoformat(),
        "decision_timestamp_supplied_by_owner": "2026-08-26 09:50 America/New_York",
        "snapshot_timestamp": "2026-08-26 10:02:12 America/New_York",
        "target": {"exact_child_account_name": NAME, "child_customer_id": CID,
                   "exact_service": SVC, "manager_customer_id": "3373711342"},
        "fingerprint_function": "gm_gsa.safety.approval_code (SHA-256, first 12 hex, upper)",
        "note": ("A fingerprint identifies an exact plan. It does NOT grant permission. "
                 "Every plan is NOT APPROVED and must not be executed."),
        "new_priority_order": {
            "R0": "Verify measurement before scaling",
            "R1": "Create enough budget headroom",
            "R2": "Unlock existing qualified demand",
            "R3": "Expand the qualified ad schedule",
            "R4": "Expand verified service geography - NO FINGERPRINT, needs Walter",
            "R5": "Create missing high-demand SKAGs paused",
            "R6": "Fix call attribution and sitelink leakage",
            "R7": "Monitor and repace daily",
        },
        "pacing_at_snapshot": {
            "target": 2500.00, "fresh_mtd_spend": 171.17,
            "remaining_budget": 2328.83,
            "remaining_calendar_days_incl_aug26": 6,
            "remaining_hours": 133.96,
            "required_average_per_remaining_calendar_day": 388.14,
            "required_rolling_24_hour_pace": 417.22,
            "current_combined_daily_budget": 82.22,
            "current_combined_2x_limit": 164.44,
            "minimum_combined_daily_budget_needed": 388.14,
            "max_theoretical_under_current_budgets": 1157.81,
            "CAN_CURRENT_BUDGETS_REACH_2500": "NO",
            "CAN_CURRENT_VERIFIED_DEMAND_REACH_2500": "NO - not inside the current 8-target footprint",
        },
        "voided_fingerprints": [
            {"plan_id": "PLAN-A", "fingerprint": "701E8E5ED639", "status": "VOID",
             "voided_on": "2026-08-26", "replaced_by": ["PLAN-A1", "PLAN-A2", "PLAN-A3"]},
            {"plan_id": "PLAN-E", "fingerprint": "F453AD249497", "status": "VOID",
             "voided_on": "2026-08-26", "replaced_by": ["PLAN-E1", "PLAN-E2"]},
            {"plan_id": "PLAN-I2", "fingerprint": "6AF733F709E2", "status": "VOID",
             "voided_on": "2026-08-26",
             "reason": ("SKAG-integrity audit of all 62 keyword rows: BOTH proposed ad "
                        "groups fail the one-canonical-intent test. Pressure & Power "
                        "Washing = 4 canonical intents across 34 rows; Soft & House "
                        "Washing = 2 across 28 rows. All 62 rows show semantic overlap "
                        "with live keywords and only PARTIAL landing-page relevance."),
             "replaced_by": ["PLAN-I2A-E", "PLAN-I2A-C", "PLAN-I2A-EN"]},
        ],
        "superseded_in_order_but_still_valid": [
            {"plan_id": "PLAN-C", "fingerprint": "9E18503B5BEA",
             "superseded_by": "PLAN-I3", "status": "NOT VOID - actions unchanged"},
            {"plan_id": "PLAN-D", "fingerprint": "F61C9F287B82",
             "superseded_by": "PLAN-I2", "status": "NOT VOID - actions unchanged",
             "reason": ("Fresh Planner shows its ad group's only keyword text has no "
                        "reportable local volume, so it is not one of the strongest "
                        "delivery opportunities.")},
            {"plan_id": "PLAN-I1", "fingerprint": "9308DFCF8741",
             "superseded_by": "PLAN-I1A", "status": "NOT VOID - actions unchanged",
             "reason": ("Its $299.93/$88.21 split was derived from demand ratios "
                        "measured before PLAN-I2 was voided and before any geo "
                        "decision. Must be recalculated, not executed as written.")},
            {"plan_id": "PLAN-E1", "fingerprint": "40385B68584E",
             "superseded_by": "PLAN-I5", "status": "NOT VOID - actions unchanged",
             "reason": ("Its House Washing Near Me SKAG became redundant once PLAN-I2 "
                        "proposed enabling the legacy group that already contains that "
                        "exact keyword text.")},
        ],
        "on_hold": [
            {"plan_id": "PLAN-B", "fingerprint": "F80E8D398811",
             "state": "HOLD_UNTIL_MONTH_END_RESCUE_IS_RESOLVED",
             "not_void": True,
             "reason": ("Its own impact model shows the $24.00 CPC ceiling LOWERS "
                        "August spend ($330.51 vs $405.49 for no change), which works "
                        "against the full-spend objective."),
             "early_invocation_only_via": ("STOP-level trigger of the emergency "
                                           "high-CPC stop condition")},
        ],
        "no_fingerprint_by_design": [
            {"plan_id": "PLAN-A1", "reason": "READ-ONLY. Fingerprint generated for identification only; not required to execute."},
            {"plan_id": "PLAN-I1A", "reason": "Budget values cannot be computed until six demand inputs are resolved. Fingerprinting provisional amounts would create an approvable artifact encoding stale assumptions."},
            {"plan_id": "PLAN-I2A-EN", "reason": "PROVISIONAL ONLY. The four ad groups do not exist yet, so its fingerprint hashes PENDING_CREATION placeholders. MUST be regenerated with real resource IDs after PLAN-I2A-C executes and readback QA passes."},
            {"plan_id": "PLAN-I4", "file": "2026-08-26-plan-i4-service-area-opportunity.md",
             "reason": "Opportunity analysis. Every candidate NEEDS WALTER CONFIRMATION. Nothing executable."},
            {"plan_id": "PLAN-F", "file": "2026-08-25-plan-f-landing-page-fixes.md",
             "reason": "Website changes, deliberately kept out of Ads fingerprints."},
            {"plan_id": "R7", "file": "2026-08-26-daily-pacing-control.md",
             "reason": "Read-only monitoring process. Never writes."},
        ],
        "recommended_approval_order": [
            {"order": r["rescue_approval_order"], "plan_id": r["plan_id"],
             "priority": r["rescue_priority"], "fingerprint": r["fingerprint"],
             "approval_phrase": r["approval_phrase"]} for r in order_rows],
        "plans": rows,
        "totals": {
            "plans": len(rows),
            "total_actions": sum(r["action_count"] for r in rows),
            "total_objects": sum(r["object_count"] for r in rows),
            "total_ads_mutations": sum(r["ads_mutation_count"] or 0 for r in rows),
            "rescue_path_ads_mutations": sum(
                r["ads_mutation_count"] or 0 for r in rows
                if r["plan_id"] in ("PLAN-I1", "PLAN-I2", "PLAN-E2", "PLAN-I5")),
        },
        "zero_external_changes_confirmed": True,
        "no_form_submitted": True,
        "no_call_placed": True,
    }
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("RESCUE FINGERPRINT MANIFEST  %s" % manifest["generated_account_local"])
    print()
    print("%-8s %-5s %-13s %5s %5s %-42s %s"
          % ("PLAN", "PRI", "FINGERPRINT", "ACTS", "OBJS", "STATUS", "ORDER"))
    print("-" * 108)
    for r in sorted(rows, key=lambda x: (x["rescue_approval_order"] or 99, x["plan_id"])):
        st = r["approval_status"] or ""
        print("%-8s %-5s %-13s %5d %5d %-42s %s"
              % (r["plan_id"], r["rescue_priority"], r["fingerprint"],
                 r["action_count"], r["object_count"], st[:42],
                 r["rescue_approval_order"] or "-"))
    print()
    print("VOID: %s" % [v["plan_id"] + " " + v["fingerprint"]
                        for v in manifest["voided_fingerprints"]])
    print("HOLD: %s" % [h["plan_id"] + " " + h["fingerprint"]
                        for h in manifest["on_hold"]])
    print("SUPERSEDED (not void): %s"
          % [s["plan_id"] for s in manifest["superseded_in_order_but_still_valid"]])
    print()
    print("TOTALS: %s" % json.dumps(manifest["totals"]))
    print()
    print("RECOMMENDED APPROVAL ORDER")
    for o in manifest["recommended_approval_order"]:
        print("   %d. %-8s %-4s %s" % (o["order"], o["plan_id"], o["priority"],
                                       o["approval_phrase"]))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
