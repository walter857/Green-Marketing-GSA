#!/usr/bin/env python3
"""Fresh P0/P1 impact model for Softwind. Reads saved snapshots only.

Deliberately conservative about DAYS LIVE. A plan approved today does not deliver
for six days: create-paused resources need readback QA and a second enable
approval, so PLAN-E cannot realistically serve for the whole remaining window.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "impact-model-2026-08-25.json"

MTD_SPEND = 171.17
REMAINING_FULL_DAYS = 6          # Aug 26-31
SPEND_GOAL = 2500.0


def scen(name, impr_day, ctr, cpc, days_live, note, cvr_low=0.03, cvr_base=0.07,
         cvr_high=0.12):
    clicks_day = impr_day * ctr
    spend_day = clicks_day * cpc
    clicks_total = clicks_day * days_live
    p = lambda c: 1 - (1 - c) ** clicks_total
    return {
        "scenario": name,
        "daily_eligible_impressions": round(impr_day, 1),
        "ctr": round(ctr, 4),
        "daily_clicks": round(clicks_day, 2),
        "average_cpc": round(cpc, 2),
        "daily_spend": round(spend_day, 2),
        "days_live_in_august": days_live,
        "incremental_spend": round(spend_day * days_live, 2),
        "projected_august_spend": round(MTD_SPEND + spend_day * days_live, 2),
        "clicks_remaining_august": round(clicks_total, 1),
        "lead_probability": {
            "low_cvr_3pct": round(p(cvr_low), 3),
            "base_cvr_7pct": round(p(cvr_base), 3),
            "high_cvr_12pct": round(p(cvr_high), 3),
        },
        "note": note,
    }


def main() -> int:
    drift = json.loads((SNAP / "drift-check-2026-08-25b.json").read_text(encoding="utf-8"))
    daily = drift["campaign_daily_now"]
    recent = [d for d in daily if d["date"] in ("2026-08-24", "2026-08-25")]
    impr_now = sum(r["impressions"] for r in recent) / 2
    mtd = drift["mtd_now"]
    ctr_now = mtd["clicks"] / mtd["impressions"]
    cpc_now = mtd["cost"] / mtd["clicks"]

    out = {
        "baseline_fresh_2026_08_25_1744": {
            "mtd_impressions": mtd["impressions"],
            "mtd_clicks": mtd["clicks"],
            "mtd_spend": mtd["cost"],
            "mtd_conversions": mtd["conversions"],
            "ctr": round(ctr_now, 4),
            "avg_cpc": round(cpc_now, 2),
            "recent_impressions_per_day": impr_now,
        },
        "assumptions": {
            "cpc_after_24usd_ceiling": (
                "Modelled at $20.00. Three of six observed clicks were bought above "
                "$24.00 ($26.66, $40.07, $54.49). Capping the bid does not guarantee "
                "the same clicks at a lower price - some are lost, some are won lower. "
                "$20 sits between the $16.29 Planner midpoint and the current $28.53."),
            "schedule_uplift": (
                "Conservative +35%, base and high +50%. The account's own hourly curve "
                "peaks at its final serving hour (17:00 = 23 of 107 impressions) and is "
                "cut off at 18:00; Sunday has never run. +50% lands on ~35/day, which "
                "agrees with the Keyword Planner all-hours ceiling of 39.2/day."),
            "ctr_improvement": (
                "No RSA rewrite is in the P0/P1 set, so CTR gains come only from better "
                "keyword-to-copy matching as new SKAGs take their own queries. Held at "
                "6% conservative, 8% base, 10% high. The best live ad group already "
                "runs 10.53%."),
            "plan_e_days_live": (
                "PLAN-E resources are CREATED PAUSED and need readback QA plus a "
                "SECOND enable approval. Even on the fastest realistic path they "
                "cannot serve before ~2026-08-28, so the high case credits 4 days, "
                "not 6."),
            "conversion_rate": (
                "The account has never produced a lead, so there is no observed CVR. "
                "3% / 7% / 12% are industry ranges for a local home-service landing "
                "page with a 4-field form and click-to-call. LOW CONFIDENCE."),
        },
        "scenarios": [],
    }

    out["scenarios"].append(scen(
        "CURRENT - nothing approved",
        impr_now, ctr_now, cpc_now, REMAINING_FULL_DAYS,
        "Observed reach, observed CTR, observed CPC. Sunday 2026-08-30 stays dark."))

    out["scenarios"].append(scen(
        "P0 ONLY - PLAN-A + PLAN-B",
        impr_now * 0.97, ctr_now, 20.00, REMAINING_FULL_DAYS,
        "Tracking verified (no traffic effect) and a $24.00 CPC ceiling. Reach is "
        "shaded down 3% for the small rank loss the ceiling causes. Note this "
        "REDUCES August spend - the ceiling buys the same clicks for less."))

    out["scenarios"].append(scen(
        "P0 + P1 CONSERVATIVE",
        impr_now * 1.35, 0.06, 20.00, REMAINING_FULL_DAYS,
        "Adds PLAN-C 24/7 schedule at a conservative +35%, PLAN-D enable, PLAN-G "
        "duplicate pause and PLAN-H sitelink repoint. PLAN-E not yet enabled."))

    out["scenarios"].append(scen(
        "P0 + P1 BASE",
        impr_now * 1.50, 0.08, 19.00, REMAINING_FULL_DAYS,
        "Schedule uplift at the full +50% corroborated by the Planner ceiling. CTR "
        "8% as traffic reaches better-matched ad groups. PLAN-E still not enabled."))

    out["scenarios"].append(scen(
        "P0 + P1 HIGH - includes PLAN-E enabled ~2026-08-28",
        impr_now * 1.50 * 1.25, 0.10, 18.00, 4,
        "Everything above plus the two new SKAGs live for the last 4 days only. "
        "The +25% coverage uplift captures a larger share of the same ~39/day pool; "
        "it does not create new demand."))

    for s in out["scenarios"]:
        s["remaining_to_2500_goal"] = round(SPEND_GOAL - s["projected_august_spend"], 2)
        s["pct_of_2500_goal"] = round(
            100 * s["projected_august_spend"] / SPEND_GOAL, 1)

    best = max(s["projected_august_spend"] for s in out["scenarios"])
    out["spend_goal_verdict"] = {
        "goal": SPEND_GOAL,
        "highest_projected": best,
        "shortfall": round(SPEND_GOAL - best, 2),
        "pct_achieved": round(100 * best / SPEND_GOAL, 1),
        "verdict": ("$2,500 IS NOT A DEFENSIBLE QUALIFIED-SEARCH SPEND TARGET FOR "
                    "THE REMAINING PERIOD. Executing every P0 and P1 plan raises "
                    "projected August spend from roughly $406 to roughly $%d - "
                    "still about %d%% of the goal." % (best, 100 * best / SPEND_GOAL)),
        "note": ("The P0 bidding fix REDUCES spend. Capping CPC is the single most "
                 "valuable technical action and it moves the spend number the wrong "
                 "way. Where those two conflict, this plan set recommends the "
                 "client's interest."),
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    b = out["baseline_fresh_2026_08_25_1744"]
    print("BASELINE (fresh 2026-08-25 17:44)")
    print("  MTD %d impr, %d clicks, $%.2f, %d conv | CTR %.2f%% | CPC $%.2f | recent %.1f impr/day"
          % (b["mtd_impressions"], b["mtd_clicks"], b["mtd_spend"], b["mtd_conversions"],
             b["ctr"] * 100, b["avg_cpc"], b["recent_impressions_per_day"]))
    print()
    hdr = ("%-46s %7s %7s %7s %8s %9s %9s %8s" %
           ("SCENARIO", "IMPR/D", "CTR", "CLK/D", "CPC", "SPEND/D", "AUG TOTAL", "P(lead)"))
    print(hdr)
    print("-" * len(hdr))
    for s in out["scenarios"]:
        print("%-46s %7.1f %6.2f%% %7.2f %8.2f %9.2f %9.2f %7.0f%%"
              % (s["scenario"][:46], s["daily_eligible_impressions"], s["ctr"] * 100,
                 s["daily_clicks"], s["average_cpc"], s["daily_spend"],
                 s["projected_august_spend"],
                 s["lead_probability"]["base_cvr_7pct"] * 100))
    print()
    print("LEAD PROBABILITY DETAIL (low 3% / base 7% / high 12% CVR)")
    for s in out["scenarios"]:
        lp = s["lead_probability"]
        print("  %-46s clicks_left=%4.1f  %3.0f%% / %3.0f%% / %3.0f%%"
              % (s["scenario"][:46], s["clicks_remaining_august"],
                 lp["low_cvr_3pct"] * 100, lp["base_cvr_7pct"] * 100,
                 lp["high_cvr_12pct"] * 100))
    print()
    v = out["spend_goal_verdict"]
    print("SPEND GOAL: highest projected $%.2f of $%.0f = %.1f%%  (shortfall $%.2f)"
          % (v["highest_projected"], v["goal"], v["pct_achieved"], v["shortfall"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
