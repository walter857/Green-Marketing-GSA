#!/usr/bin/env python3
"""Per-plan approval fingerprints for the Softwind P0/P1 change plans.

Uses gm_gsa.safety.approval_code, the repository's standard fingerprint function,
so a code produced here is byte-identical to one produced anywhere else in the
project. Each plan file is fingerprinted independently, so approving one plan can
never implicitly approve another.

Read-only. Changes nothing locally and nothing in Google Ads.
"""
from __future__ import annotations

import argparse
import hashlib
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
MANIFEST = PLANS / "2026-08-25-fingerprint-manifest.json"
TZ = ZoneInfo("America/New_York")

EXPECT_CID = "1521725229"
EXPECT_NAME = "Softwind Power Washing - Live"
EXPECT_SERVICE = "Power Washing"


def normalize(plan: dict) -> dict:
    """Canonical payload: target identity + the exact action list, nothing else.

    Narrative fields are deliberately excluded so a wording change does not
    invalidate an approval, while any change to a resource ID, current value,
    proposed value or count does.
    """
    p = plan["change_plan"]
    t = p["target"]
    actions = []
    for a in p.get("actions", []):
        actions.append({
            "action_id": a["action_id"],
            "priority": a["priority"],
            "resource_type": a["resource_type"],
            "operation": a["operation"],
            "customer_id": a.get("customer_id", t["child_customer_id"]),
            "campaign_id": a.get("campaign_id"),
            "ad_group_id": a.get("ad_group_id"),
            "resource_id": a.get("resource_id"),
            "current_value": a.get("current_value"),
            "proposed_value": a.get("proposed_value"),
            "object_count": a.get("object_count", 1),
        })
    actions.sort(key=lambda x: x["action_id"])
    return {
        "target": {
            "exact_child_account_name": t["exact_child_account_name"],
            "child_customer_id": t["child_customer_id"],
            "exact_service": t["exact_service"],
        },
        "plan_id": p["plan_id"],
        "approval_type": p["approval_type"],
        "actions": actions,
        "action_count": len(actions),
        "object_count": sum(a["object_count"] for a in actions),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-manifest", action="store_true")
    args = ap.parse_args()

    rows = []
    for path in sorted(PLANS.glob("2026-08-2*-plan-*.yaml")):
        doc = load_yaml(path)
        assert_no_embedded_secrets(doc)
        p = doc["change_plan"]
        t = p["target"]

        # identity gate on every plan
        problems = []
        if t["exact_child_account_name"] != EXPECT_NAME:
            problems.append("account name mismatch")
        if str(t["child_customer_id"]) != EXPECT_CID:
            problems.append("customer id mismatch")
        if t["exact_service"] != EXPECT_SERVICE:
            problems.append("service mismatch")
        if not str(p.get("approval_status", "")).startswith("NOT APPROVED"):
            problems.append("approval_status must start with 'NOT APPROVED'")
        ex = str(p.get("execution_status", ""))
        if not (ex.startswith("DO NOT EXECUTE") or ex.startswith("READ-ONLY")):
            problems.append("execution_status must be DO NOT EXECUTE or READ-ONLY")

        payload = normalize(doc)
        fp = approval_code(payload)
        canon = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False)
        rows.append({
            "plan_id": p["plan_id"],
            "plan_title": p["plan_title"],
            "file": path.name,
            "approval_type": p["approval_type"],
            "priority": p.get("priority"),
            "fingerprint": fp,
            "action_count": payload["action_count"],
            "object_count": payload["object_count"],
            "ads_mutation_count": p.get("ads_mutation_count"),
            "requires_separate_enable_approval": p.get(
                "requires_separate_enable_approval", False),
            "recommended_approval_order": p.get("recommended_approval_order"),
            "blocked_on": p.get("blocked_on", []),
            "approval_status": p.get("approval_status", "NOT APPROVED"),
            "execution_status": p.get("execution_status", "DO NOT EXECUTE"),
            "fingerprint_required": p.get("fingerprint_required", True),
            "supersedes": p.get("supersedes"),
            "blocking_state": (p.get("blocking_status") or {}).get("state"),
            "canonical_sha256_full": hashlib.sha256(
                canon.encode("utf-8")).hexdigest(),
            "identity_gate_problems": problems,
            "approval_phrase": "APPROVE %s %s FOR %s" % (p["plan_id"], fp, EXPECT_CID),
        })

    manifest = {
        "generated_account_local": datetime.now(TZ).isoformat(),
        "target": {"exact_child_account_name": EXPECT_NAME,
                   "child_customer_id": EXPECT_CID,
                   "exact_service": EXPECT_SERVICE,
                   "manager_customer_id": "3373711342"},
        "fingerprint_function": "gm_gsa.safety.approval_code (SHA-256, first 12 hex, upper)",
        "note": ("A fingerprint identifies an exact plan. It does NOT grant permission. "
                 "Every plan below is NOT APPROVED and must not be executed."),
        "voided_fingerprints": [
            {"plan_id": "PLAN-A", "fingerprint": "701E8E5ED639",
             "status": "VOID",
             "voided_on": "2026-08-26",
             "reason": ("Bundled a read-only inspection that creates nothing with a "
                        "form test that creates a real CRM lead and a phone test that "
                        "rings the client's line. Three different risk classes under "
                        "one approval."),
             "replaced_by": ["PLAN-A1", "PLAN-A2", "PLAN-A3"]},
            {"plan_id": "PLAN-E", "fingerprint": "F453AD249497",
             "status": "VOID",
             "voided_on": "2026-08-26",
             "reason": ("Bundled create-paused resources, which cannot serve until a "
                        "second enable approval, with negative keywords that go live "
                        "the instant they are created."),
             "replaced_by": ["PLAN-E1", "PLAN-E2"]},
        ],
        "superseded_plan_files_retained_for_audit_trail": [
            "2026-08-25-plan-a-measurement.yaml",
            "2026-08-25-plan-e-create-paused-expansion.yaml",
        ],
        "plans": rows,
        "totals": {
            "plans": len(rows),
            "total_actions": sum(r["action_count"] for r in rows),
            "total_objects": sum(r["object_count"] for r in rows),
            "total_ads_mutations": sum(r["ads_mutation_count"] or 0 for r in rows),
        },
    }

    if args.write_manifest:
        MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print("wrote %s" % MANIFEST)

    print()
    print("%-8s %-46s %-12s %6s %6s  %s"
          % ("PLAN", "TITLE", "FINGERPRINT", "ACTS", "OBJS", "STATUS"))
    for r in rows:
        flag = "IDENTITY FAIL" if r["identity_gate_problems"] else "NOT APPROVED"
        print("%-8s %-46s %-12s %6d %6d  %s"
              % (r["plan_id"], r["plan_title"][:46], r["fingerprint"],
                 r["action_count"], r["object_count"], flag))
        if r["identity_gate_problems"]:
            print("         !! %s" % "; ".join(r["identity_gate_problems"]))
    print()
    print("TOTALS: %s" % json.dumps(manifest["totals"]))
    print()
    print("Every plan above is NOT APPROVED / DO NOT EXECUTE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
