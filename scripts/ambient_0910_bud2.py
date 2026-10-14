#!/usr/bin/env python3
"""Corrected budget replacement package. Same two mutations, corrected hashed calculations."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

DAYS, MAXM = 30.4, 13000.0
EDIT_DAY = "2026-09-10"
REMAIN = 21          # 2026-09-10 .. 2026-09-30 inclusive
NOW = datetime.datetime.now(TZ).isoformat()
TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "AC Repair",
          "related_services": ["HVAC Repair", "HVAC Installation", "HVAC Replacement",
                               "Gas Boiler Repair"]}
UNCHANGED = {"AC Repair": ("15787409435", 141.45), "HVAC Installation": ("15787409441", 176.15),
             "HVAC Repair": ("15787409444", 78.95)}
CHANGE = {"15787409438": ("Gas Boiler Repair", 42760000, 5000000, 0.00,
                          {"impressions": 34, "clicks": 0, "cost": 0.00, "conversions": 0,
                           "lost_is_budget_pct": 0.00, "lost_is_rank_pct": 48.39}),
          "15787409447": ("HVAC Replacement", 26320000, 20000000, 0.00,
                          {"impressions": 199, "clicks": 5, "cost": 152.52, "conversions": 0,
                           "lost_is_budget_pct": 0.00, "lost_is_rank_pct": 45.54})}
unchanged_sub = sum(v[1] * DAYS for v in UNCHANGED.values())
sept_change = {b: v[3] + (v[2] / 1e6) * REMAIN for b, v in CHANGE.items()}
sept_total = unchanged_sub + sum(sept_change.values())
daily_after = sum(v[1] for v in UNCHANGED.values()) + sum(v[2] / 1e6 for v in CHANGE.values())
steady = daily_after * DAYS

ops = []
for bid, (label, cur, new, spend, ev) in CHANGE.items():
    ops.append({
        "operation": "UPDATE_CAMPAIGN_BUDGET", "resource": "campaign_budget",
        "resource_id": bid, "resource_name": f"customers/{CID}/campaignBudgets/{bid}",
        "campaign": label,
        "current_state": f"amount_micros = {cur} (${cur/1e6:.2f}/day)",
        "proposed_state": f"amount_micros = {new} (${new/1e6:.2f}/day)",
        "field_mask": ["amount_micros"],
        "budget_is_individual": True,
        "reason": (f"Fresh settled data 2026-08-14..2026-09-09: {ev['impressions']} impressions, "
                   f"{ev['clicks']} clicks, ${ev['cost']:.2f}, {ev['conversions']} Primary "
                   f"conversion records. Search lost impression share to BUDGET is "
                   f"{ev['lost_is_budget_pct']:.2f}% and to RANK is {ev['lost_is_rank_pct']:.2f}%. "
                   f"September spend through the 2026-09-10 preflight is ${spend:.2f}. Budget has "
                   f"never been this campaign's constraint, so the reduction cannot cost "
                   f"delivery."),
        "current_month_limit_CORRECTED": {
            "method": "September spend before the edit + (new average daily budget x remaining "
                      "CALENDAR days INCLUDING the edit day). The highest budget in force on the "
                      "edit day affects that single day's daily delivery limit; it does NOT "
                      "replace the latest budget in the remaining-month formula.",
            "september_spend_before_edit": spend,
            "edit_day": EDIT_DAY,
            "remaining_calendar_days_incl_edit_day": REMAIN,
            "campaign_september_maximum": round(sept_change[bid], 2)},
        "steady_state_monthly_max_30_4": round((new / 1e6) * DAYS, 2),
        "rollback": ("NOT a blind restore. Gas Boiler Repair + HVAC Replacement combined must "
                     "stay at or below $31.08/day while AC Repair $141.45, HVAC Installation "
                     "$176.15 and HVAC Repair $78.95 are unchanged. Any restoration above that "
                     "needs an offsetting reduction, a fresh cap calculation and a NEW approval "
                     "fingerprint."),
        "risk": "LOW", "risk_reason": "0.00% Search lost IS (budget) in every measured window",
        "unrelated_resource_assertion":
            "budgets 15787409435 ($141.45), 15787409441 ($176.15) and 15787409444 ($78.95) must "
            f"be unchanged; combined daily total must read ${daily_after:.2f}; no budget may "
            "become explicitly_shared"})

plan = {
    "plan_name": "AMB-0910-BUD-2", "approval_class": "reversible-budget-change",
    "generated_local": NOW,
    "supersedes": "AMB-0909C-BUD-1 (A7118436590B) - SUPERSEDED, DO_NOT_EXECUTE",
    "target": TARGET,
    "summary": (f"Gas Boiler Repair $42.76 -> $5.00 and HVAC Replacement $26.32 -> $20.00. "
                f"Identical mutation payload to A7118436590B; the hashed calculation metadata is "
                f"corrected. Combined daily $465.63 -> ${daily_after:.2f}."),
    "object_count": len(ops), "partial_failure": False, "atomic": True, "operations": ops,
    "notes": {
        "why_A7118436590B_was_superseded":
            "Its hashed operations embedded per_campaign_limits.september_campaign_maximum of "
            "142.76 (Gas Boiler) and 426.32 (HVAC Replacement), computed by the retracted method "
            "'September spend + highest budget in force on the edit day + new daily x remaining "
            "days after the edit day'. The corrected figures are 105.00 and 420.00. Because the "
            "retracted assertion sat inside a hashed plan field and was a mandatory precondition, "
            "the fingerprint was superseded rather than executed.",
        "retracted_combined_figure": {
            "prior": 10216.12, "corrected": round(sept_total, 2),
            "understatement": round(sept_total - 10216.12, 2),
            "why": "The prior method also applied spend-to-date plus one budget per remaining day "
                   "to the three UNCHANGED campaigns. A campaign with no September budget edit "
                   "carries its own applicable monthly charging limit instead."},
        "current_month_september": {
            "unchanged_campaign_monthly_limits": {
                k: {"budget_id": v[0], "daily": v[1], "monthly_limit": round(v[1] * DAYS, 2)}
                for k, v in UNCHANGED.items()},
            "unchanged_subtotal": round(unchanged_sub, 2),
            "gas_boiler_september_maximum": round(sept_change["15787409438"], 2),
            "hvac_replacement_september_maximum": round(sept_change["15787409447"], 2),
            "conservative_account_september_upper_bound": round(sept_total, 2),
            "headroom_under_13000": round(MAXM - sept_total, 2),
            "cost_basis": "SERVED cost. Google Ads exposes no per-month BILLED figure through "
                          "this API surface without monthly invoicing. Served cost can still be "
                          "restated by invalid-activity credits."},
        "steady_state_future_month": {
            "combined_daily": round(daily_after, 2),
            "x30_4": round(steady, 2),
            "headroom_under_13000": round(MAXM - steady, 2)},
        "compliant_rollback_envelope": {
            "blind_restore_forbidden": True,
            "blind_restore_daily": 465.63,
            "blind_restore_x30_4": round(465.63 * DAYS, 2),
            "blind_restore_breach": round(465.63 * DAYS - MAXM, 2),
            "two_campaign_envelope_daily": round(MAXM / DAYS - 396.55, 2),
            "example_compliant_partial_restore": "Gas Boiler $10.00 + HVAC Replacement $21.00 = "
                                                 "$31.00 combined, $427.55/day, $12,997.52 over "
                                                 "30.4 days"},
        "requires_new_approval": True}}
plan["fingerprint"] = approval_code({"target": TARGET, "plan": plan["plan_name"],
                                     "operations": ops})

print("=== CORRECTED BUDGET CALCULATION (fresh, 2026-09-10) ===")
for k, v in UNCHANGED.items():
    print(f"  {k:<20} ${v[1]:>7.2f} x 30.4 = ${v[1]*DAYS:>9,.2f}   (no September edit)")
print(f"  {'unchanged subtotal':<20} {'':>17} ${unchanged_sub:>9,.2f}")
for b, v in CHANGE.items():
    print(f"  {v[0]:<20} $0.00 + (${v[2]/1e6:.2f} x {REMAIN}) = ${sept_change[b]:>9,.2f}")
print(f"  {'SEPTEMBER UPPER BOUND':<20} {'':>17} ${sept_total:>9,.2f}   "
      f"headroom ${MAXM-sept_total:,.2f}")
print(f"  {'STEADY STATE':<20} ${daily_after:>7.2f} x 30.4 = ${steady:>9,.2f}   "
      f"headroom ${MAXM-steady:,.2f}")
print(f"\n=== {plan['plan_name']} ops={len(ops)} fingerprint={plan['fingerprint']} ===")
(CLIENT_DIR / "plans" / f"{plan['plan_name']}.json").write_text(
    json.dumps(plan, indent=1, default=str), encoding="utf-8")
(TOPPLANS / "AMBIENT-2026-09-10-packages.json").write_text(
    json.dumps({plan["plan_name"]: plan}, indent=1, default=str), encoding="utf-8")
print(f"WROTE clients/ambient-cooling-heating/plans/{plan['plan_name']}.json")
print(f"WROTE plans/AMBIENT-2026-09-10-packages.json")
ops_str = json.dumps(ops)
print(f"\n  hashed operations contain 142.76 : {'142.76' in ops_str}  (must be False)")
print(f"  hashed operations contain 426.32 : {'426.32' in ops_str}  (must be False)")
print(f"  hashed operations contain 105.0  : {'105.0' in ops_str}   (corrected)")
print(f"  hashed operations contain 420.0  : {'420.0' in ops_str}   (corrected)")
