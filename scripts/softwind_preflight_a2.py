#!/usr/bin/env python3
"""Preflight for PLAN-A2 - controlled single form-submission conversion test.

APPROVAL RECEIVED: APPROVE PLAN-A2 3B30BD017E0C FOR 1521725229

This plan is NOT a Google Ads mutation. It submits a REAL lead into up to four
live systems and adds ONE PERMANENT, NON-DELETABLE Google Ads conversion. It
carries four explicit blocked_on preconditions. This script verifies the
fingerprint and reports precisely which preconditions are satisfied and which
are not. It SUBMITS NOTHING.

READ ONLY.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.safety import approval_code                     # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
APPROVED_FP = "3B30BD017E0C"
CLIENT = ROOT / "clients/softwind-power-washing"
PLAN_FILE = CLIENT / "plans/2026-08-26-plan-a2-controlled-form-test.yaml"
A1_RECEIPT = CLIENT / "snapshots/plan-a1-inspection-2026-08-26.json"
OUT = CLIENT / "snapshots/a2-preflight-2026-08-27.json"


def normalize(plan: dict) -> dict:
    p = plan["change_plan"]
    t = p["target"]
    actions = []
    for a in p.get("actions", []):
        actions.append({
            "action_id": a["action_id"], "priority": a["priority"],
            "resource_type": a["resource_type"], "operation": a["operation"],
            "customer_id": a.get("customer_id", t["child_customer_id"]),
            "campaign_id": a.get("campaign_id"),
            "ad_group_id": a.get("ad_group_id"),
            "resource_id": a.get("resource_id"),
            "current_value": a.get("current_value"),
            "proposed_value": a.get("proposed_value"),
            "object_count": a.get("object_count", 1)})
    actions.sort(key=lambda x: x["action_id"])
    return {"target": {"exact_child_account_name": t["exact_child_account_name"],
                       "child_customer_id": t["child_customer_id"],
                       "exact_service": t["exact_service"]},
            "plan_id": p["plan_id"], "approval_type": p["approval_type"],
            "actions": actions, "action_count": len(actions),
            "object_count": sum(a["object_count"] for a in actions)}


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    r = {"read_only": True, "submissions_made": 0, "mutations_issued": 0,
         "timestamp_account_local": now.isoformat()}

    print("=" * 74)
    print("PLAN-A2 PREFLIGHT  %s" % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 74)

    # ---- fingerprint ----
    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    p = plan["change_plan"]
    fp = approval_code(normalize(plan))
    r["fingerprint"] = {"recomputed": fp, "approved": APPROVED_FP,
                        "match": fp == APPROVED_FP}
    print("\n1. FINGERPRINT")
    print("   recomputed : %s" % fp)
    print("   approved   : %s" % APPROVED_FP)
    print("   MATCH      : %s" % (fp == APPROVED_FP))
    print("   identity   : %s | %s | %s"
          % (p["target"]["exact_child_account_name"],
             p["target"]["child_customer_id"], p["target"]["exact_service"]))
    r["identity_ok"] = (p["target"]["child_customer_id"] == CID
                        and p["target"]["exact_child_account_name"] == NAME)

    # ---- what this plan actually does ----
    print("\n2. WHAT THIS PLAN DOES")
    cc = p["change_counts"]
    print("   google_ads_mutations_total          : %s" % cc["google_ads_mutations_total"])
    print("   forms_submitted                     : %s" % cc["forms_submitted"])
    print("   crm_records_created                 : %s" % cc["crm_records_created"])
    print("   permanent_google_ads_conversions    : %s"
          % cc["permanent_google_ads_conversions_added"])
    print("   IRREVERSIBLE: %s" % p["crm_impact"]["irreversibility_warning"][:200])
    r["change_counts"] = cc

    # ---- blocked_on precondition audit ----
    print("\n3. BLOCKED_ON PRECONDITIONS")
    a1_done = A1_RECEIPT.exists()
    a1_detail = ""
    if a1_done:
        a1 = json.loads(A1_RECEIPT.read_text(encoding="utf-8"))
        a1_detail = "receipt present (%d keys)" % len(a1)
    pre = [
        {"id": "A2-PRE-1", "requirement": "PLAN-A1 complete and findings reviewed",
         "satisfied": a1_done,
         "evidence": a1_detail or "no PLAN-A1 receipt found"},
        {"id": "A2-PRE-2",
         "requirement": "Client-supplied test identity (name, phone, email)",
         "satisfied": False,
         "evidence": ("NOT SUPPLIED. The approval message contained only the "
                      "approval phrase. No test name, no client-controlled test "
                      "phone number, no client-controlled test email address.")},
        {"id": "A2-PRE-3",
         "requirement": "Client notified in advance so nobody chases the fake lead",
         "satisfied": False,
         "evidence": "NOT CONFIRMED. No statement that Softwind has been told."},
        {"id": "A2-PRE-4", "requirement": "Named cleanup owner agreed",
         "satisfied": False,
         "evidence": ("NOT NAMED. cleanup_procedure.owner is still "
                      "'To be named by the approval owner before execution.'")},
    ]
    for x in pre:
        print("   [%s] %-10s %s" % ("OK  " if x["satisfied"] else "MISSING",
                                    x["id"], x["requirement"]))
        print("        %s" % x["evidence"])
    r["preconditions"] = pre
    r["all_preconditions_met"] = all(x["satisfied"] for x in pre)

    # ---- arrival path: is the click now capped? ----
    q = ("SELECT campaign.id, campaign.name, "
         "campaign.target_spend.cpc_bid_ceiling_micros, "
         "campaign.bidding_strategy_type, campaign_budget.amount_micros "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    ceil = {}
    for x in rows(svc, q):
        ceil[str(x.campaign.id)] = {
            "name": x.campaign.name,
            "ceiling_usd": usd(x.campaign.target_spend.cpc_bid_ceiling_micros) or None,
            "budget_usd": usd(x.campaign_budget.amount_micros)}
    r["cpc_ceiling_state"] = ceil
    capped = all(v["ceiling_usd"] == 30.0 for v in ceil.values())
    print("\n4. ARRIVAL-PATH COST CONTROL")
    print("   The plan recommends capping the test click before using the real-ad")
    print("   path. It names PLAN-B ($24). PLAN-K1 ($30) executed today instead.")
    for cid_, v in ceil.items():
        print("     %-17s ceiling $%s  budget $%s"
              % (v["name"], v["ceiling_usd"], v["budget_usd"]))
    print("   TEST CLICK NOW CAPPED: %s (max cost of the test click = $30.00)" % capped)
    r["test_click_capped"] = capped

    # ---- conversion baseline ----
    q = ("SELECT conversion_action.id, conversion_action.name, "
         "conversion_action.status, conversion_action.type, "
         "conversion_action.category, conversion_action.counting_type, "
         "conversion_action.primary_for_goal "
         "FROM conversion_action WHERE conversion_action.id = 7708725995")
    ca = [{"id": str(x.conversion_action.id), "name": x.conversion_action.name,
           "status": x.conversion_action.status.name,
           "type": x.conversion_action.type_.name,
           "category": x.conversion_action.category.name,
           "counting": x.conversion_action.counting_type.name,
           "primary_for_goal": x.conversion_action.primary_for_goal}
          for x in rows(svc, q)]
    r["target_conversion_action"] = ca
    q = ("SELECT campaign.id, metrics.conversions, metrics.all_conversions "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND segments.date BETWEEN '2026-08-01' AND '%s'"
         % now.strftime("%Y-%m-%d"))
    conv = {NAMES[str(x.campaign.id)]: {
        "conversions": round(x.metrics.conversions, 2),
        "all_conversions": round(x.metrics.all_conversions, 2)}
        for x in rows(svc, q)}
    r["conversion_baseline_mtd"] = conv
    total_conv = sum(v["conversions"] for v in conv.values())
    print("\n5. CONVERSION BASELINE")
    for k, v in ca[0].items() if ca else []:
        pass
    if ca:
        print("   action 7708725995 : %s | %s | %s | %s"
              % (ca[0]["name"], ca[0]["status"], ca[0]["category"], ca[0]["counting"]))
    print("   MTD conversions   : %s" % json.dumps(conv))
    print("   TOTAL             : %s" % total_conv)
    print("   -> one test conversion would be %s of August conversion history."
          % ("100%" if total_conv == 0 else "a material share"))
    r["baseline_total_conversions"] = total_conv

    # ---- K1-W1: has the ceiling started biting? ----
    today = now.strftime("%Y-%m-%d")
    q = ("SELECT campaign.id, ad_group.name, segments.hour, metrics.clicks, "
         "metrics.cost_micros, metrics.average_cpc, metrics.impressions "
         f"FROM ad_group WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date = '{today}' AND metrics.impressions > 0")
    hrs = []
    for x in rows(svc, q):
        hrs.append({"hour": int(x.segments.hour),
                    "campaign": NAMES[str(x.campaign.id)],
                    "ad_group": x.ad_group.name,
                    "impressions": x.metrics.impressions,
                    "clicks": x.metrics.clicks,
                    "cost": usd(x.metrics.cost_micros),
                    "avg_cpc": usd(x.metrics.average_cpc)})
    hrs.sort(key=lambda x: x["hour"])
    r["today_hourly"] = hrs
    post = [h for h in hrs if h["hour"] >= 12 and h["clicks"]]
    r["k1_w1"] = {
        "post_1230_clicks": post,
        "resolved": bool(post),
        "verdict": ("CEILING HOLDING - all post-12:00 clicks at or under $30.00"
                    if post and all(h["avg_cpc"] <= 30.0 for h in post)
                    else "CEILING BREACHED after 12:00" if post
                    else "STILL UNRESOLVED - no billable click after 12:00 yet")}
    print("\n6. K1-W1 CEILING TEST (carried over)")
    for h in hrs:
        flag = ""
        if h["clicks"] and h["avg_cpc"] > 30.0:
            flag = "  <-- ABOVE $30 CEILING"
        print("   %02d:00 %-17s %-32s %2di %dc $%-7s avgcpc $%s%s"
              % (h["hour"], h["campaign"][:17], h["ad_group"][:32],
                 h["impressions"], h["clicks"], h["cost"], h["avg_cpc"], flag))
    print("   VERDICT: %s" % r["k1_w1"]["verdict"])

    # ---- MTD ----
    q = ("SELECT campaign.id, metrics.cost_micros, metrics.clicks, "
         "metrics.impressions FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-01' AND '{today}'")
    mtd, per = 0.0, {}
    for x in rows(svc, q):
        c = usd(x.metrics.cost_micros)
        mtd += c
        per[NAMES[str(x.campaign.id)]] = {"cost": c, "clicks": x.metrics.clicks,
                                          "impressions": x.metrics.impressions}
    r["mtd"] = {"total": round(mtd, 2), "per_campaign": per,
                "remaining": round(2500 - mtd, 2)}
    print("\n7. PACING")
    print("   MTD $%.2f  remaining $%.2f  %s" % (mtd, 2500 - mtd, json.dumps(per)))

    OUT.write_text(json.dumps(r, indent=2), encoding="utf-8")
    print("\n" + "=" * 74)
    if r["fingerprint"]["match"] and r["all_preconditions_met"]:
        print("RESULT: CLEAR TO EXECUTE")
    else:
        print("RESULT: BLOCKED - fingerprint %s, preconditions %d of %d met"
              % ("OK" if r["fingerprint"]["match"] else "MISMATCH",
                 sum(1 for x in pre if x["satisfied"]), len(pre)))
        print("        NOTHING WAS SUBMITTED.")
    print("=" * 74)
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
