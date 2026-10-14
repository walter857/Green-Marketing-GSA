#!/usr/bin/env python3
"""Month-end feasibility RE-MODELLED with the confirmed geo footprint.

Supersedes the scenario table in rescue-feasibility-2026-08-26.json, which
stacked PLAN-I2 (now VOID) and PLAN-I3 (still BLOCKED) into its headline
numbers. This model turns those off unless explicitly enabled.

Local computation only. No API calls, no writes.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "geo-feasibility-2026-08-26.json"

# ---- measured inputs -------------------------------------------------------
MTD = 171.17
TARGET = 2500.0
HOURS_REMAINING = 127.97          # from the 16:01:33 snapshot
BASE_IMPR_DAY = 23.5              # observed recent rate, current 8-town footprint
BASE_CTR = 0.0571                 # observed
CPC_NOW = 28.53                   # observed, uncapped Maximize Clicks
CPC_EXPANDED = 37.09              # modelled CPC once budget rises, uncapped
CUR_BUDGET_DAY = 82.22
CUR_2X = 164.44
I1B_BUDGET_DAY = 388.14
I1B_2X = I1B_BUDGET_DAY * 2

# Measured combined multi-location Keyword Planner readings (union measurements,
# never summed standalone figures).
GEO_360_CURRENT = 360
GEO_1650_EIGHT_TOWN = 1650
GEO_MULT = GEO_1650_EIGHT_TOWN / GEO_360_CURRENT      # 4.58x

SCHEDULE_UPLIFT_IF_UNBLOCKED = 1.5    # PLAN-I3, still BLOCKED
I2AE_UPLIFT = 1.03                    # one existing SKAG, no reportable local volume


def model(name, days, geo=False, budget=False, i2ae=False, sched=False,
          note="", confidence=""):
    impr = BASE_IMPR_DAY
    if geo:
        impr *= GEO_MULT
    if i2ae:
        impr *= I2AE_UPLIFT
    if sched:
        impr *= SCHEDULE_UPLIFT_IF_UNBLOCKED
    cpc = CPC_EXPANDED if budget else CPC_NOW
    ctr = BASE_CTR
    clicks = impr * ctr
    demand_spend_day = clicks * cpc

    cap = I1B_2X if budget else CUR_2X
    actual_day = min(demand_spend_day, cap)
    budget_limited = demand_spend_day > cap

    spend = actual_day * days
    total = MTD + spend
    return {
        "scenario": name, "days_live": days,
        "geo_confirmed": geo, "budget_i1b": budget,
        "skag_i2ae": i2ae, "schedule_i3_unblocked": sched,
        "impressions_per_day": round(impr, 1),
        "clicks_per_day": round(clicks, 2),
        "expected_cpc": cpc,
        "unconstrained_spend_per_day": round(demand_spend_day, 2),
        "daily_delivery_ceiling_2x": round(cap, 2),
        "actual_spend_per_day": round(actual_day, 2),
        "BUDGET_LIMITED": budget_limited,
        "remaining_spend": round(spend, 2),
        "projected_august_total": round(total, 2),
        "pct_of_2500": round(100 * total / TARGET, 1),
        "shortfall": round(TARGET - total, 2),
        "estimated_leads_at_3_7_12_pct": [round(clicks * days * r, 2)
                                          for r in (0.03, 0.07, 0.12)],
        "note": note, "confidence": confidence}


def main() -> int:
    days5 = 5.33
    days4 = 4.0
    rows = [
        model("A  NOTHING APPROVED", days5, note=(
            "Live account as it stands today: 8 targets, $82.22/day combined."),
            confidence="HIGH - the account's own observed behaviour"),
        model("B  PLAN-J ONLY (geo, no budget change)", days5, geo=True, note=(
            "Geo expands the eligible pool 4.58x, but the $164.44/day delivery "
            "ceiling binds almost immediately. Spend is capped by budget, not by "
            "demand. This combination wastes most of the demand it unlocks."),
            confidence="MEDIUM-HIGH"),
        model("C  PLAN-J + PLAN-I1B", days5, geo=True, budget=True, note=(
            "The realistic best case for August. Geo supplies the demand, the "
            "budget supplies the headroom. Schedule stays Mon-Sat 08:00-18:00 "
            "because PLAN-I3 is still BLOCKED."),
            confidence="MEDIUM - demand multiplier is measured, CPC response is not"),
        model("D  PLAN-J + I1B + I2A-E", days5, geo=True, budget=True, i2ae=True,
              note=("Adds the one existing paused SKAG that survived the integrity "
                    "audit. Keyword Planner shows no reportable local volume for it, "
                    "so the uplift modelled here is deliberately small."),
              confidence="MEDIUM"),
        model("E  D + SCHEDULE, IF I3 EVER UNBLOCKS", days4, geo=True, budget=True,
              i2ae=True, sched=True,
              note=("SHOWN FOR REFERENCE ONLY. PLAN-I3 is BLOCKED on SCHED-Q1..Q6 "
                    "(after-hours call coverage). Days reduced to 4 because the "
                    "schedule answers cannot realistically land today."),
              confidence="LOW - depends on an unanswered operational question"),
        model("C4 PLAN-J + I1B, approvals land tomorrow", days4, geo=True,
              budget=True, note=("Same as C but one day of delivery is lost."),
              confidence="MEDIUM"),
    ]

    best = max(r["projected_august_total"] for r in rows[:4])
    out = {
        "generated": "2026-08-26",
        "supersedes": ("rescue-feasibility-2026-08-26.json scenario table, which "
                       "stacked PLAN-I2 (VOID) and PLAN-I3 (BLOCKED)."),
        "inputs": {
            "mtd_spend": MTD, "target": TARGET,
            "hours_remaining_at_1601": HOURS_REMAINING,
            "base_impressions_per_day": BASE_IMPR_DAY, "base_ctr": BASE_CTR,
            "cpc_current": CPC_NOW, "cpc_if_budget_raised": CPC_EXPANDED,
            "geo_demand_current_8": GEO_360_CURRENT,
            "geo_demand_confirmed_16": GEO_1650_EIGHT_TOWN,
            "geo_multiplier": round(GEO_MULT, 2),
            "geo_multiplier_basis": (
                "Combined multi-location Keyword Planner queries. These are union "
                "measurements. Standalone town volumes were never summed."),
            "current_daily_ceiling_2x": CUR_2X,
            "i1b_daily_ceiling_2x": I1B_2X},
        "scenarios": rows,
        "verdict": {
            "can_2500_be_spent_by_aug_31": "NO",
            "best_achievable_without_the_blocked_schedule": best,
            "best_pct_of_target": round(100 * best / TARGET, 1),
            "why": (
                "The confirmed geo footprint is the single biggest lever available "
                "and it roughly triples the realistic outcome - from about $400 to "
                "about $1,300. It still does not reach $2,500. Reaching the target "
                "would need the demand to arrive roughly twice as fast as 4.58x the "
                "account's own measured rate, inside five days, with no schedule "
                "change approved. Buying the gap would mean paying materially above "
                "the local top-of-page range for traffic the account has not "
                "qualified, which the standing instruction forbids."),
            "what_would_close_more_of_the_gap": [
                "PLAN-I3 (schedule) - blocked only on SCHED-Q1..Q6, the after-hours "
                "call-coverage questions. This is the largest remaining lever.",
                "PLAN-B (CPC ceiling) is on HOLD and would REDUCE spend, not raise "
                "it. It should stay on hold while the spend objective is live.",
            ],
            "recommendation": (
                "Approve PLAN-J and PLAN-I1B together. Separately they are worth "
                "much less: PLAN-J alone is budget-capped within a day, and PLAN-I1B "
                "alone buys the same small click pool at a higher price. Together "
                "they are the defensible maximum for August.")},
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("MONTH-END FEASIBILITY, RE-MODELLED WITH CONFIRMED GEO")
    print("geo multiplier %.2fx  (%d -> %d distinct monthly searches)"
          % (GEO_MULT, GEO_360_CURRENT, GEO_1650_EIGHT_TOWN))
    print()
    hdr = ("%-38s %5s %7s %7s %9s %6s %9s %8s"
           % ("SCENARIO", "DAYS", "IMPR/D", "CLK/D", "SPEND/D", "CAP?",
              "AUG TOTAL", "% TGT"))
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print("%-38s %5s %7s %7s %9s %6s %9s %7s%%"
              % (r["scenario"][:38], r["days_live"], r["impressions_per_day"],
                 r["clicks_per_day"], r["actual_spend_per_day"],
                 "YES" if r["BUDGET_LIMITED"] else "no",
                 r["projected_august_total"], r["pct_of_2500"]))
    print()
    for r in rows:
        print("%-38s leads @3/7/12%%  %s"
              % (r["scenario"][:38], r["estimated_leads_at_3_7_12_pct"]))
    print()
    v = out["verdict"]
    print("CAN $2,500 BE SPENT BY AUG 31: %s" % v["can_2500_be_spent_by_aug_31"])
    print("Best achievable without the blocked schedule: $%.2f (%.1f%% of target)"
          % (v["best_achievable_without_the_blocked_schedule"],
             v["best_pct_of_target"]))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
