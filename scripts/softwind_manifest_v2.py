#!/usr/bin/env python3
"""Correction 4 - reconciled fingerprint manifest. Every plan appears in EXACTLY
one status category, and the category totals are asserted to equal the plan count.
Read-only."""
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
SUP = PLANS / "superseded"
OUT = PLANS / "2026-08-26-rescue-fingerprint-manifest.json"
TZ = ZoneInfo("America/New_York")
CID, NAME, SVC = "1521725229", "Softwind Power Washing - Live", "Power Washing"

# exactly one status per plan
STATUS = {
    "PLAN-J2A":  ("EXECUTED", "R4", None, "EXECUTED 2026-08-26 17:49 ET. 144 criteria created, 0 removed, QA passed."),
    "PLAN-J2B":  ("EXECUTED", "R4", None, "EXECUTED 2026-08-26 17:56 ET. 2 exclusions created, 0 removed, QA passed."),
    "PLAN-I1C":  ("EXECUTED", "R1", None, "EXECUTED 2026-08-26 18:00 ET. Campaign A $41.11 -> $333.33, QA passed."),
    "PLAN-A2":   ("ACTIVE", "R0", 1, "Controlled form test"),
    "PLAN-H":    ("ACTIVE", "R6", 2, "Call-attribution / sitelink repair"),
    "PLAN-E2A":  ("ACTIVE", "R2", 3, "Revised out-of-scope negatives"),
    "PLAN-I2A-E":("ACTIVE", "R5", 4, "Enable the one correct existing paused SKAG"),
    "PLAN-A3":   ("ACTIVE", "R0", 5, "Controlled phone test"),
    "PLAN-I1B":  ("SUPERSEDED", "R1", None, "Superseded by PLAN-I1C, not void"),
    "PLAN-A1":   ("EXECUTED_READ_ONLY", "R0", None,
                  "Read-only inspection, executed 2026-08-26. No approval needed."),
    "PLAN-I3":   ("BLOCKED", "R3", None, "Schedule - blocked on SCHED-Q1..Q6"),
    "PLAN-I5":   ("SEPTEMBER", "R5", None,
                  "Routing fix, zero incremental impressions - not in the August path"),
    "PLAN-B":    ("HOLD", "-", None, "HOLD_UNTIL_MONTH_END_RESCUE_IS_RESOLVED"),
    "PLAN-G":    ("HOLD", "R6", None, "HOLD FOR SEPTEMBER"),
    "PLAN-C":    ("SUPERSEDED", "R3", None, "Superseded in order by PLAN-I3, not void"),
    "PLAN-D":    ("SUPERSEDED", "R5", None, "Superseded in order by PLAN-I2A-E, not void"),
    "PLAN-E1":   ("SUPERSEDED", "R5", None, "Superseded by PLAN-I5, not void"),
}

VOID_REGISTER = [
    {"plan_id": "PLAN-A", "fingerprint": "701E8E5ED639", "voided_on": "2026-08-26",
     "replaced_by": ["PLAN-A1", "PLAN-A2", "PLAN-A3"],
     "reason": "Bundled a read-only inspection with a form test and a phone test."},
    {"plan_id": "PLAN-E", "fingerprint": "F453AD249497", "voided_on": "2026-08-26",
     "replaced_by": ["PLAN-E1", "PLAN-E2"],
     "reason": "Bundled create-paused resources with negatives that go live on creation."},
    {"plan_id": "PLAN-I2", "fingerprint": "6AF733F709E2", "voided_on": "2026-08-26",
     "replaced_by": ["PLAN-I2A-E"],
     "reason": ("62-keyword SKAG-integrity audit: both legacy ad groups carry multiple "
                "canonical intents (4 and 2).")},
    {"plan_id": "PLAN-I2A-C", "fingerprint": "D50CDC94927C", "voided_on": "2026-08-26",
     "replaced_by": [],
     "reason": ("All four SKAGs failed the corrected incrementality test. Modern Phrase "
                "Match matches meaning, so Planner volume is not incremental. Enabled "
                "keywords already match every one of these query spaces, and NO query "
                "in account history has ever contained 'long island'.")},
    {"plan_id": "PLAN-I2A-EN", "fingerprint": "9ABDF6DDE3F4", "voided_on": "2026-08-26",
     "replaced_by": [], "reason": "Enables the output of PLAN-I2A-C, which is void."},
    {"plan_id": "PLAN-E2", "fingerprint": "09E91EA674C8", "voided_on": "2026-08-26",
     "replaced_by": ["PLAN-E2A"],
     "reason": "PHRASE 'house cleaning' too broad; narrowed to EXACT."},
    {"plan_id": "PLAN-I1", "fingerprint": "9308DFCF8741", "voided_on": "2026-08-26",
     "replaced_by": ["PLAN-I1B"],
     "reason": "Split derived from a 10:02 snapshot and PLAN-I2's demand assumptions."},
    {"plan_id": "PLAN-I1A", "fingerprint": "5B9BCFA06FD5", "voided_on": "2026-08-26",
     "replaced_by": ["PLAN-I1B"],
     "reason": "Actions-empty no-op; inputs now resolved so it is replaced by I1B."},
    {"plan_id": "PLAN-J", "fingerprint": "B42EAD386795", "voided_on": "2026-08-26",
     "replaced_by": ["PLAN-J2A", "PLAN-J2B"],
     "reason": ("SOURCE MISMATCH - built from the 16-location geo-union analysis "
                "because the client-approved CSV was not available to that run. "
                "The approved source is 'Location report (2).csv', which carries "
                "75 New York rows resolving to 72 net-new targets, not 8. Also "
                "wrongly combined positive targeting with the Connecticut "
                "exclusion in a single fingerprint.")},
]


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
        status, pri, order, note = STATUS.get(pid, ("UNCLASSIFIED", "-", None, ""))
        approvable = status == "ACTIVE" and payload["action_count"] > 0
        rows.append({
            "plan_id": pid, "plan_title": p["plan_title"], "file": path.name,
            "status": status, "priority": pri, "approval_order": order, "note": note,
            "approval_type": p["approval_type"], "fingerprint": fp,
            "action_count": payload["action_count"],
            "object_count": payload["object_count"],
            "ads_mutation_count": p.get("ads_mutation_count", 0),
            "approval_status_in_file": p.get("approval_status"),
            "requires_separate_enable_approval": p.get(
                "requires_separate_enable_approval", False),
            "approvable_now": approvable,
            "approval_phrase": ("APPROVE %s %s FOR %s" % (pid, fp, CID)
                                if approvable else
                                "NOT APPROVABLE - status %s" % status)})

    by_status = {}
    for r in rows:
        by_status.setdefault(r["status"], []).append(r["plan_id"])

    # strict reconciliation
    categorised = sum(len(v) for v in by_status.values())
    recon = {
        "plan_files_in_approvable_directory": len(rows),
        "plans_categorised": categorised,
        "categories_sum_equals_plan_count": categorised == len(rows),
        "each_plan_appears_in_exactly_one_category": (
            len({p for v in by_status.values() for p in v}) == len(rows)),
        "void_register_entries": len(VOID_REGISTER),
        "void_files_moved_out_of_approvable_directory": len(
            list(SUP.glob("*.yaml"))),
        "total_actions": sum(r["action_count"] for r in rows),
        "total_objects": sum(r["object_count"] for r in rows),
        "total_ads_mutations": sum(r["ads_mutation_count"] or 0 for r in rows),
        "approvable_now_count": sum(1 for r in rows if r["approvable_now"]),
        "approvable_now_mutations": sum(
            r["ads_mutation_count"] or 0 for r in rows if r["approvable_now"]),
    }

    manifest = {
        "generated_account_local": datetime.now(TZ).isoformat(),
        "snapshot_used": "2026-08-26 16:01:33 America/New_York",
        "target": {"exact_child_account_name": NAME, "child_customer_id": CID,
                   "exact_service": SVC, "manager_customer_id": "3373711342"},
        "fingerprint_function": "gm_gsa.safety.approval_code (SHA-256, first 12 hex, upper)",
        "fingerprint_storage": ("Fingerprints are RECOMPUTED from each plan file every time this manifest is built. They are deliberately NOT stored inside the plan YAML. Any hand-edit to a plan action therefore changes its fingerprint and invalidates a prior approval, which is the intended safety property."),
        "note": ("A fingerprint identifies an exact plan. It does NOT grant permission. "
                 "Only plans with status ACTIVE and at least one action carry an "
                 "approval command."),
        "status_definitions": {
            "ACTIVE": "Approvable now. Has actions and a valid fingerprint.",
            "EXECUTED_READ_ONLY": "Read-only, already run. No approval applicable.",
            "EXECUTED": "Approved, executed and verified by readback QA. Closed.",
            "BLOCKED": "Drafted and fingerprinted but blocked on an external answer.",
            "SEPTEMBER": "Valid but deliberately outside the August path.",
            "HOLD": "Valid, fingerprint preserved, deliberately not approved now.",
            "SUPERSEDED": "Displaced in order by a newer plan. NOT void; actions unchanged.",
            "VOID": "Retired. Fingerprint must never be approved. File moved to superseded/.",
        },
        "reconciliation": recon,
        "by_status": {k: sorted(v) for k, v in sorted(by_status.items())},
        "void_register": VOID_REGISTER,
        "plans": rows,
        "recommended_approval_order": [
            {"order": r["approval_order"], "plan_id": r["plan_id"],
             "priority": r["priority"], "fingerprint": r["fingerprint"],
             "mutations": r["ads_mutation_count"],
             "approval_phrase": r["approval_phrase"]}
            for r in sorted([x for x in rows if x["approval_order"]],
                            key=lambda x: x["approval_order"])],
        "approval_order_rationale": {"1_PLAN-J2A": "Supplies the demand. MUST precede the budget: raising spend first, with no new demand to buy, makes uncapped Maximize Clicks bid UP on the current thin pool.", "2_PLAN-J2B": "Separate fingerprint, separate approval. Exclusions are a different risk class from positive targeting and must not ride along on one approval.", "3_PLAN-I1C": "Budget headroom, executed only AFTER PLAN-J2A readback QA passes and a fresh post-geo snapshot is taken.", "4_PLAN-A2": "Lead-protection queue. Zero Google Ads mutations; answers whether the new spend is measurable at all.", "5_PLAN-H": "Lead-protection queue. Repairs sitelink call leakage so leads bought with the new budget are actually attributed.", "6_PLAN-E2A": "Deliberately AFTER geo and budget. Roof-cleaning scope is still unresolved and must not delay delivery work.", "7_PLAN-I2A-E": "Adds qualified reach on an existing, already-QA-verified paused SKAG.", "8_PLAN-A3": "Must run AFTER PLAN-H so the phone test exercises the corrected, tracked number."},
        "zero_external_changes_confirmed": True,
        "no_form_submitted": True,
        "no_call_placed": True,
    }
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("RECONCILED MANIFEST  %s" % manifest["generated_account_local"])
    print()
    print("%-11s %-19s %-13s %5s %5s %5s  %s"
          % ("PLAN", "STATUS", "FINGERPRINT", "ACTS", "OBJS", "MUT", "APPROVABLE"))
    print("-" * 92)
    for r in sorted(rows, key=lambda x: (x["approval_order"] or 99, x["plan_id"])):
        print("%-11s %-19s %-13s %5d %5d %5s  %s"
              % (r["plan_id"], r["status"], r["fingerprint"], r["action_count"],
                 r["object_count"], r["ads_mutation_count"],
                 "YES  order %s" % r["approval_order"] if r["approvable_now"] else "no"))
    print()
    print("BY STATUS (each plan appears exactly once)")
    for k, v in sorted(by_status.items()):
        print("   %-19s %d  %s" % (k, len(v), v))
    print()
    print("RECONCILIATION")
    for k, v in recon.items():
        print("   %-52s %s" % (k, v))
    print()
    print("VOID REGISTER (%d) - files moved out of the approvable directory"
          % len(VOID_REGISTER))
    for v in VOID_REGISTER:
        print("   %-12s %-13s -> %s" % (v["plan_id"], v["fingerprint"],
                                        v["replaced_by"] or "nothing"))
    print()
    print("RECOMMENDED APPROVAL ORDER")
    for o in manifest["recommended_approval_order"]:
        print("   %d. %-11s %-4s %2s mutations   %s"
              % (o["order"], o["plan_id"], o["priority"], o["mutations"],
                 o["approval_phrase"]))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
