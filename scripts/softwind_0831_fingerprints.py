#!/usr/bin/env python3
"""Per-plan approval fingerprints for the 2026-08-31 R-series recovery plans.

Uses gm_gsa.safety.approval_code, the repository standard fingerprint function,
so a code produced here is byte-identical to one produced anywhere else in the
project. Each plan is fingerprinted independently, so approving one plan can
never implicitly approve another.

Parsing is duplicate-key aware: plain PyYAML silently keeps the LAST value when a
mapping key repeats, which would let a stale duplicate change a plan's meaning
without changing its fingerprint. This loader raises instead.

Read-only. Changes nothing locally and nothing in Google Ads.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

PLANS = ROOT / "clients/softwind-power-washing/plans"
MANIFEST = PLANS / "2026-08-31-r-series-fingerprint-manifest.json"
TZ = ZoneInfo("America/New_York")

EXPECT_CID = "1521725229"
EXPECT_NAME = "Softwind Power Washing - Live"
EXPECT_SERVICE = "Power Washing"

# Fingerprints that must never be honoured again, with the reason.
VOID_REGISTRY = [
    {
        "plan_id": "PLAN-R3A",
        "fingerprint": "B57E427D07C5",
        "version": "$12.00 on campaign 24103511039 only, 1 mutation, generated 2026-08-31 17:30",
        "state": "VOID - SUPERSEDED BY PLAN-R3B",
        "reason": (
            "The $12.00 figure was sound; the single-campaign control design was not. "
            "Campaign 24145053510 is not a valid independent control - five search terms "
            "have served in BOTH campaigns at an equal bid, carrying 26.7% of valid clicks "
            "and 24.8% of spend, and four of those five were absorbed by one campaign-B "
            "keyword. Holding B at $30 while moving A to $12 would give B a 2.5x bid "
            "advantage on shared query space. PLAN-R3B applies $12.00 symmetrically to "
            "both campaigns instead."),
        "do_not_honour": True,
    },
    {
        "plan_id": "PLAN-R3",
        "fingerprint": "97D8B268A80A",
        "version": "$22.00 ceiling on BOTH campaigns, 2 mutations, generated 2026-08-31 10:45",
        "state": "VOID - SUPERSEDED BY PLAN-R3A",
        "reason": (
            "Walter did not approve a $22 ceiling. The completed CPC ceiling analysis "
            "found $12.00 to be the lowest defensible test ceiling: $10 clears ~15.8% of "
            "measured local demand, $12 clears ~98.2%, and $18/$22 add almost no "
            "additional measured keyword coverage over $12. PLAN-R3 also changed both "
            "campaigns at once, destroying the control group and restarting campaign B's "
            "learning window. Replaced by PLAN-R3A: one field, one campaign, campaign "
            "24145053510 held at $30.00 as the control."),
        "do_not_honour": True,
    },
    {
        "plan_id": "PLAN-R8",
        "fingerprint": "DFF115FF4D26",
        "version": "two-mutation asset-parity version, generated 2026-08-31 10:55",
        "state": "VOID - ACTIONS ALREADY COMPLETED MANUALLY",
        "reason": (
            "R8-01 (link SITELINK 413928453094 to campaign 24103511039) and R8-02 "
            "(link STRUCTURED_SNIPPET 404844116658 to campaign 24103511039) were both "
            "performed by hand in the Google Ads UI between 10:21 and 10:52 on "
            "2026-08-31, while the audit was running. Executing them now would attempt "
            "to create campaign_asset links that already exist. Verified present and "
            "ENABLED by fresh read at 16:40."),
        "do_not_honour": True,
    },
]


class DuplicateKeyError(ValueError):
    pass


class DupCheckLoader(yaml.SafeLoader):
    """SafeLoader that refuses a mapping containing a repeated key."""


def _no_duplicates(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            m = key_node.start_mark
            raise DuplicateKeyError(
                f"duplicate key {key!r} at line {m.line + 1}, column {m.column + 1}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


DupCheckLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def normalize(plan: dict) -> dict:
    """Canonical payload: target identity plus the exact action list, nothing else.

    Narrative and evidence are deliberately excluded so restating a figure does not
    invalidate an approval, while any change to a resource ID, current value,
    proposed value, field mask or count does. RSA copy IS included, because changing
    an advertisement changes the thing being approved.
    """
    p = plan["change_plan"]
    t = p["target"]
    actions = []
    for a in p.get("actions", []):
        row = {
            "action_id": a["action_id"],
            "priority": a.get("priority"),
            "resource_type": a["resource_type"],
            "operation": a["operation"],
            "customer_id": str(a.get("customer_id", t["child_customer_id"])),
            "campaign_id": str(a.get("campaign_id") or ""),
            "ad_group_id": str(a.get("ad_group_id") or ""),
            "resource_id": str(a.get("resource_id") or ""),
            "field_mask": a.get("field_mask"),
            "current_value": a.get("current_value"),
            "proposed_value": a.get("proposed_value"),
            "object_count": a.get("object_count", 1),
        }
        ad = a.get("ad")
        if ad:
            row["ad"] = {
                "status": ad.get("status"),
                "final_url": ad.get("final_url"),
                "path1": ad.get("path1"),
                "path2": ad.get("path2"),
                "headlines": list(ad.get("headlines", [])),
                "descriptions": list(ad.get("descriptions", [])),
            }
        actions.append(row)
    actions.sort(key=lambda x: x["action_id"])
    return {
        "target": {
            "exact_child_account_name": t["exact_child_account_name"],
            "child_customer_id": str(t["child_customer_id"]),
            "exact_service": t["exact_service"],
        },
        "plan_id": p["plan_id"],
        "approval_type": p["approval_type"],
        "actions": actions,
        "action_count": len(actions),
        "object_count": sum(a["object_count"] for a in actions),
    }


def classify(p: dict, payload: dict) -> tuple[str, bool, str]:
    """Return (status_category, approval_command_allowed, reason)."""
    pid = p["plan_id"]
    acts = payload["action_count"]
    fp_state = str(p.get("fingerprint_state", "FINAL"))
    blocking = (p.get("blocking_status") or {}).get("state")
    declared = p.get("ads_mutation_count") or 0

    if p.get("superseded_by"):
        sb = p["superseded_by"]
        return ("SUPERSEDED", False,
                f"void - superseded by {sb.get('plan_id')}; its fingerprint must not be "
                f"honoured")
    if fp_state.startswith("PROVISIONAL"):
        return ("PROVISIONAL", False,
                "every action names a PENDING_CREATION placeholder; the fingerprint must be "
                "regenerated against real resource IDs after PLAN-R5 and PLAN-R6 are created "
                "paused and read back")
    if blocking == "BLOCKED":
        return ("BLOCKED", False,
                "blocked on a dependency; replacements must be created, enabled and verified "
                "serving first")
    if acts == 0 and declared == 0:
        if pid == "PLAN-R8":
            return ("NO-ACTION - CLOSED BY OWNER", False,
                    "the two proposed mutations were completed manually by the owner during "
                    "the audit; a zero-action status record is not an executable change plan")
        if pid == "PLAN-R12":
            return ("NO-ACTION - HOLD", False,
                    "proposes no budget change; recording the decision not to act is not an "
                    "executable change plan")
        if pid == "PLAN-R4":
            return ("DECISION RECORD", False,
                    "structural decision record with zero mutations; it is not an execution "
                    "approval and must not carry an approval command")
        if pid == "PLAN-R7":
            return ("WEBSITE - SEPARATE TRACK", False,
                    "website changes only, zero Google Ads mutations; approval belongs to "
                    "whoever owns the site, on its own track")
        if pid == "PLAN-R1":
            return ("READ-ONLY / INVESTIGATION", False,
                    "zero Google Ads mutations; the work is investigation and client-supplied "
                    "inputs, which need action but not an Ads approval phrase")
        return ("NO-ACTION", False, "zero actions and zero declared mutations")
    if acts == 0 and declared:
        return ("INCONSISTENT", False,
                f"declares {declared} mutations but carries no executable action list")
    if p.get("approval_status") != "NOT APPROVED":
        return ("INCONSISTENT", False, "approval_status is not exactly 'NOT APPROVED'")
    return ("APPROVAL-READY", True, "")


def main() -> int:
    rows = []
    parse_failures = []
    for path in sorted(PLANS.glob("2026-08-31-plan-r*.yaml")):
        text = path.read_text(encoding="utf-8")
        try:
            doc = yaml.load(text, Loader=DupCheckLoader)
        except DuplicateKeyError as exc:
            parse_failures.append({"file": path.name, "error": f"DUPLICATE KEY: {exc}"})
            continue
        assert_no_embedded_secrets(doc)
        p = doc["change_plan"]
        t = p["target"]

        problems = []
        if t["exact_child_account_name"] != EXPECT_NAME:
            problems.append("account name mismatch")
        if str(t["child_customer_id"]) != EXPECT_CID:
            problems.append("customer id mismatch")
        if t["exact_service"] != EXPECT_SERVICE:
            problems.append("service mismatch")
        if str(p.get("approval_status", "")) != "NOT APPROVED":
            problems.append("approval_status must be exactly 'NOT APPROVED'")
        if str(p.get("execution_status", "")) != "DO NOT EXECUTE":
            problems.append("execution_status must be exactly 'DO NOT EXECUTE'")

        payload = normalize(doc)
        fp = approval_code(payload)
        canon = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

        declared = p.get("ads_mutation_count")
        counted = payload["object_count"]
        if declared is not None and payload["action_count"] and declared != counted:
            problems.append(
                f"declared ads_mutation_count {declared} != summed object_count {counted}")

        status, may_approve, why = classify(p, payload)
        if status == "INCONSISTENT":
            problems.append(why)

        rows.append({
            "plan_id": p["plan_id"],
            "plan_title": p["plan_title"],
            "file": path.name,
            "approval_type": p["approval_type"],
            "priority": p.get("priority"),
            "status_category": status,
            "fingerprint": fp,
            "fingerprint_state": p.get("fingerprint_state", "FINAL"),
            "action_count": payload["action_count"],
            "object_count": counted,
            "ads_mutation_count": declared,
            "website_action_count": len(p.get("findings", []))
            if p["plan_id"] == "PLAN-R7" else 0,
            "requires_separate_enable_approval": p.get(
                "requires_separate_enable_approval", False),
            "recommended_approval_order": p.get("recommended_approval_order"),
            "depends_on": p.get("depends_on"),
            "blocking_state": (p.get("blocking_status") or {}).get("state"),
            "approval_status": p.get("approval_status"),
            "execution_status": p.get("execution_status"),
            "canonical_sha256_full": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
            "identity_gate_problems": problems,
            "approval_command_allowed": may_approve and not problems,
            "approval_command_suppressed_because": (
                "" if (may_approve and not problems) else (why or "; ".join(problems))),
            "approval_phrase": (
                f"APPROVE {p['plan_id']} {fp} FOR {EXPECT_CID}"
                if (may_approve and not problems) else None),
        })

    # ---------------- reconciliation ----------------
    by_status = {}
    for r in rows:
        by_status.setdefault(r["status_category"], []).append(r["plan_id"])

    approval_ready = [r for r in rows if r["approval_command_allowed"]]
    asserts = []

    def a(name, ok, detail=""):
        asserts.append({"assertion": name, "pass": bool(ok), "detail": detail})

    a("every plan appears in exactly one status category",
      sum(len(v) for v in by_status.values()) == len(rows),
      f"{sum(len(v) for v in by_status.values())} categorised vs {len(rows)} plans")
    a("status counts equal total plan count",
      sum(len(v) for v in by_status.values()) == len(rows))
    a("every approval-ready plan has at least one action",
      all(r["action_count"] >= 1 for r in approval_ready))
    a("every approval-ready plan targets at least one real resource",
      all(r["action_count"] >= 1 and "PENDING" not in json.dumps(r) for r in approval_ready))
    a("no provisional placeholder is approvable",
      not any(r["approval_command_allowed"] for r in rows
              if str(r["fingerprint_state"]).startswith("PROVISIONAL")))
    a("no zero-action plan emits an approval command",
      not any(r["approval_command_allowed"] for r in rows if r["action_count"] == 0))
    a("no blocked plan emits an approval command",
      not any(r["approval_command_allowed"] for r in rows if r["blocking_state"] == "BLOCKED"))
    a("no obsolete R8 fingerprint remains approvable",
      not any(r["fingerprint"] == "DFF115FF4D26" for r in rows),
      "current PLAN-R8 fingerprint is "
      f"{next((r['fingerprint'] for r in rows if r['plan_id'] == 'PLAN-R8'), 'n/a')}")
    a("PLAN-R8 emits no approval command",
      not any(r["approval_command_allowed"] for r in rows if r["plan_id"] == "PLAN-R8"))
    a("PLAN-R12 emits no approval command",
      not any(r["approval_command_allowed"] for r in rows if r["plan_id"] == "PLAN-R12"))
    a("no superseded plan emits an approval command",
      not any(r["approval_command_allowed"] for r in rows
              if r["status_category"] == "SUPERSEDED"))
    a("every void-registry fingerprint is absent from the approvable set",
      not any(r["approval_command_allowed"] and r["fingerprint"] == v["fingerprint"]
              for r in rows for v in VOID_REGISTRY))
    a("PLAN-R3 is superseded and not approvable",
      not any(r["approval_command_allowed"] for r in rows if r["plan_id"] == "PLAN-R3"))
    a("PLAN-R3B exists, is approval-ready and carries exactly 2 mutations",
      any(r["plan_id"] == "PLAN-R3B" and r["approval_command_allowed"]
          and r["object_count"] == 2 and r["action_count"] == 2 for r in rows))
    a("PLAN-R3A is superseded and emits no approval command",
      not any(r["approval_command_allowed"] for r in rows if r["plan_id"] == "PLAN-R3A"))
    a("PLAN-R3A exists and carries exactly 1 mutation",
      any(r["plan_id"] == "PLAN-R3A" and r["object_count"] == 1 for r in rows))
    a("PLAN-R3A is SUPERSEDED (was BLOCKED) and emits no approval command",
      any(r["plan_id"] == "PLAN-R3A"
          and r["status_category"] in ("BLOCKED", "SUPERSEDED")
          and not r["approval_command_allowed"] for r in rows),
      "superseded by PLAN-R3B; control design was invalid")
    a("no duplicate-key parse failures", not parse_failures,
      json.dumps(parse_failures) if parse_failures else "all plans parsed dup-key clean")
    a("no identity gate problems on any plan",
      not any(r["identity_gate_problems"] for r in rows))
    a("declared mutations reconcile with summed object counts",
      all((r["ads_mutation_count"] or 0) == r["object_count"]
          for r in rows if r["action_count"]))

    manifest = {
        "generated_account_local": datetime.now(TZ).isoformat(),
        "series": "R - 2026-08-31 recovery",
        "revision": "2 - continuation reconciliation",
        "target": {
            "exact_child_account_name": EXPECT_NAME,
            "child_customer_id": EXPECT_CID,
            "exact_service": EXPECT_SERVICE,
            "manager_customer_id": "3373711342",
        },
        "fingerprint_function": (
            "gm_gsa.safety.approval_code (SHA-256 over the canonical action payload, "
            "first 12 hex, uppercase). The canonical payload covers target identity and "
            "the exact action list only - never narrative or evidence - so restating a "
            "figure does not invalidate an approval, while any change to a resource ID, "
            "value, field mask or count does."),
        "parser": "duplicate-key-aware SafeLoader; a repeated mapping key raises",
        "note": (
            "A fingerprint identifies an exact plan. It does NOT grant permission. Every "
            "plan below is NOT APPROVED and must not be executed. Only plans with "
            "approval_command_allowed = true carry an approval phrase."),
        "void_registry": VOID_REGISTRY,
        "totals": {
            "plans": len(rows),
            "approval_ready": len(approval_ready),
            "read_only_or_investigation": len(by_status.get("READ-ONLY / INVESTIGATION", [])),
            "decision_record": len(by_status.get("DECISION RECORD", [])),
            "website_separate_track": len(by_status.get("WEBSITE - SEPARATE TRACK", [])),
            "no_action_closed_by_owner": len(by_status.get("NO-ACTION - CLOSED BY OWNER", [])),
            "no_action_hold": len(by_status.get("NO-ACTION - HOLD", [])),
            "provisional": len(by_status.get("PROVISIONAL", [])),
            "blocked": len(by_status.get("BLOCKED", [])),
            "superseded": len(by_status.get("SUPERSEDED", [])),
            "void_fingerprints": len(VOID_REGISTRY),
            "total_actions": sum(r["action_count"] for r in rows),
            "total_objects": sum(r["object_count"] for r in rows),
            "total_google_ads_mutations_all_plans": sum(r["ads_mutation_count"] or 0
                                                        for r in rows),
            "google_ads_mutations_approval_ready_only": sum(r["object_count"]
                                                            for r in approval_ready),
            "total_website_actions": sum(r["website_action_count"] for r in rows),
        },
        "status_index": by_status,
        "reconciliation_assertions": asserts,
        "reconciliation_pass": all(x["pass"] for x in asserts),
        "plans": rows,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"{'plan':9s} {'fingerprint':13s} {'act':>3s} {'obj':>3s} {'mut':>3s}  "
          f"{'status':30s} approval")
    for r in sorted(rows, key=lambda x: (x["recommended_approval_order"] or 99)):
        cmdtxt = r["approval_phrase"] or "-- none --"
        print(f"{r['plan_id']:9s} {r['fingerprint']:13s} {r['action_count']:3d} "
              f"{r['object_count']:3d} {str(r['ads_mutation_count']):>3s}  "
              f"{r['status_category'][:30]:30s} {cmdtxt}")
    t = manifest["totals"]
    print(f"\nplans={t['plans']}  approval-ready={t['approval_ready']}  "
          f"provisional={t['provisional']}  blocked={t['blocked']}  "
          f"no-action={t['no_action_closed_by_owner'] + t['no_action_hold']}  "
          f"decision-record={t['decision_record']}  website={t['website_separate_track']}  "
          f"read-only={t['read_only_or_investigation']}")
    print(f"total actions={t['total_actions']}  total objects={t['total_objects']}  "
          f"Ads mutations across all plans={t['total_google_ads_mutations_all_plans']}  "
          f"approval-ready mutations={t['google_ads_mutations_approval_ready_only']}")
    print("\nRECONCILIATION:")
    for x in asserts:
        print(f"  [{'PASS' if x['pass'] else 'FAIL'}] {x['assertion']}"
              + (f"  ({x['detail']})" if x["detail"] else ""))
    print(f"\nVOID REGISTRY: {len(VOID_REGISTRY)}")
    for v in VOID_REGISTRY:
        print(f"  {v['plan_id']} {v['fingerprint']} -> {v['state']}")
    print(f"\nWROTE {MANIFEST}")
    return 0 if manifest["reconciliation_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
