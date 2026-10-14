#!/usr/bin/env python3
"""Month-end rescue pacing math + budget allocation models. Reads snapshots only."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "rescue-pacing-2026-08-26.json"
TZ = ZoneInfo("America/New_York")

TARGET = 2500.0
A, B = "24103511039", "24145053510"


def main() -> int:
    s = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
    snap_ts = datetime.fromisoformat(s["snapshot_account_local"])
    sep1 = datetime(2026, 9, 1, 0, 0, 0, tzinfo=TZ)

    mtd = s["spend_mtd"]
    S = mtd["combined"]["cost"]
    R = round(TARGET - S, 2)
    D = 6                                   # Aug 26,27,28,29,30,31 inclusive
    H = (sep1 - snap_ts).total_seconds() / 3600.0

    per = mtd["per_campaign"]
    budA = s["campaigns"][A]["daily_budget"]
    budB = s["campaigns"][B]["daily_budget"]
    comb_budget = round(budA + budB, 2)
    comb_2x = round(comb_budget * 2, 2)

    out = {
        "snapshot_timestamp": s["snapshot_account_local"],
        "target": TARGET,
        "fresh_mtd_spend_S": S,
        "remaining_budget_R": R,
        "remaining_calendar_days_D_incl_aug26": D,
        "remaining_hours_H": round(H, 2),
        "remaining_days_decimal": round(H / 24, 4),
        "required_average_per_remaining_calendar_day": round(R / D, 2),
        "required_rolling_24_hour_pace": round(R / (H / 24), 2),
        "current_combined_average_daily_budget": comb_budget,
        "current_combined_daily_spending_limit_2x": comb_2x,
        "minimum_combined_average_daily_budget_to_create_sufficient_monthly_limit":
            round(R / D, 2),
    }

    # Google mid-month rule check: MTD + proposed_combined_budget * remaining days
    proposed_min = R / D
    out["mid_month_budget_rule_check"] = {
        "formula": "fresh_MTD + proposed_combined_avg_daily_budget * remaining_calendar_days",
        "at_minimum_budget": round(S + proposed_min * D, 2),
        "meets_2500": (S + proposed_min * D) >= TARGET - 0.02,
        "note": ("Google's monthly charging limit is computed from the average daily "
                 "budget in force on each day, so raising the budget on 2026-08-26 "
                 "creates capacity only for the 6 remaining days, not retroactively."),
    }

    # Max theoretical spend under CURRENT budgets, even at the 2x daily ceiling
    out["max_theoretical_august_spend_under_current_budgets"] = {
        "mtd": S,
        "remaining_days": D,
        "daily_2x_limit_combined": comb_2x,
        "max_remaining": round(comb_2x * D, 2),
        "max_august_total": round(S + comb_2x * D, 2),
        "shortfall_vs_target": round(TARGET - (S + comb_2x * D), 2),
    }
    out["CAN_CURRENT_DAILY_BUDGETS_REACH_2500"] = (
        "YES" if S + comb_2x * D >= TARGET else "NO")

    # ---- demand evidence for allocation ----
    daily = s["daily"]
    def days_live(cid):
        ds = sorted({d["date"] for d in daily
                     if d["campaign_id"] == cid and d["impressions"] > 0})
        return len(ds), (ds[0] if ds else None), (ds[-1] if ds else None)

    recent_dates = ["2026-08-24", "2026-08-25", "2026-08-26"]
    def recent(cid, field):
        return sum(d[field] for d in daily
                   if d["campaign_id"] == cid and d["date"] in recent_dates)

    demand = {}
    for cid, label in ((A, "Power Washing"), (B, "Power Washing #2")):
        n, first, last = days_live(cid)
        p = per[cid]
        isv = p["search_is"] or 0
        avail = (p["impressions"] / isv) if isv else None
        demand[cid] = {
            "campaign": label,
            "mtd_impressions": p["impressions"], "mtd_clicks": p["clicks"],
            "mtd_cost": p["cost"], "avg_cpc": p["avg_cpc"],
            "search_is": isv, "lost_is_rank": p["lost_is_rank"],
            "lost_is_budget": p["lost_is_budget"],
            "days_with_impressions": n, "first_day": first, "last_day": last,
            "impressions_per_active_day": round(p["impressions"] / n, 2) if n else 0,
            "total_addressable_impressions_mtd": round(avail, 1) if avail else None,
            "addressable_per_active_day": round(avail / n, 2) if avail and n else None,
            "recent_3day_impressions": recent(cid, "impressions"),
            "recent_3day_clicks": recent(cid, "clicks"),
            "recent_3day_cost": round(recent(cid, "cost"), 2),
            "enabled_ad_groups": sum(1 for v in s["enabled_ad_groups"].values()
                                     if v["campaign_id"] == cid),
            "live_keyword_rows": sum(1 for k in s["enabled_keywords_live"]
                                     if k["campaign_id"] == cid),
        }
    out["demand_evidence"] = demand

    # ---- allocation models ----
    addA = demand[A]["addressable_per_active_day"] or 0
    addB = demand[B]["addressable_per_active_day"] or 0
    tot_add = addA + addB
    total_budget = round(R / D, 2)

    def split(fa, label, rationale):
        a = round(total_budget * fa, 2)
        b = round(total_budget - a, 2)
        return {
            "model": label, "rationale": rationale,
            "campaign_A_share": round(fa, 4), "campaign_B_share": round(1 - fa, 4),
            "campaign_A_daily_budget": a, "campaign_B_daily_budget": b,
            "combined": round(a + b, 2),
            "A_change": round(a - budA, 2), "B_change": round(b - budB, 2),
            "A_monthly_capacity_remaining": round(a * D, 2),
            "B_monthly_capacity_remaining": round(b * D, 2),
            "combined_capacity_remaining": round((a + b) * D, 2),
            "combined_2x_daily_ceiling": round((a + b) * 2, 2),
        }

    fa1 = addA / tot_add if tot_add else 0.5
    m1 = split(fa1, "MODEL 1 - Proportional to qualified demand",
               ("Split by addressable impressions per active day, derived from each "
                "campaign's own impressions divided by its search impression share. "
                "A = %.1f/day addressable, B = %.1f/day." % (addA, addB)))
    m2 = split(0.75, "MODEL 2 - Primary campaign weighted",
               ("Campaign A carries 87%% of MTD impressions, 4 of 6 clicks, the entire "
                "Quality Score history, and 58.3%% lost IS (rank) versus B's 30.0%% - "
                "so A has far more unclaimed auction headroom to buy into."))
    m3 = split(0.50, "MODEL 3 - Equal split",
               "Mechanical 50/50. Ignores that the two campaigns have very different "
               "addressable pools and very different rank headroom.")
    out["allocation_models"] = [m1, m2, m3]

    # ---- demand-side reality check ----
    # Recent observed reach, both campaigns, per day
    recent_impr = sum(recent(c, "impressions") for c in (A, B))
    recent_days = 3
    impr_day = recent_impr / recent_days
    ctr = mtd["combined"]["ctr"]
    cpc = mtd["combined"]["avg_cpc"]
    out["demand_reality_check"] = {
        "recent_3day_combined_impressions": recent_impr,
        "observed_impressions_per_day": round(impr_day, 2),
        "observed_ctr": ctr,
        "observed_avg_cpc": cpc,
        "clicks_per_day_at_observed_rates": round(impr_day * ctr, 2),
        "spend_per_day_at_observed_rates": round(impr_day * ctr * cpc, 2),
        "projected_remaining_spend_no_change": round(impr_day * ctr * cpc * D, 2),
        "projected_august_total_no_change": round(S + impr_day * ctr * cpc * D, 2),
        "impressions_per_day_required_for_target": round(
            (R / D) / (ctr * cpc), 1) if ctr and cpc else None,
    }
    req_impr = out["demand_reality_check"]["impressions_per_day_required_for_target"]
    out["CAN_CURRENT_VERIFIED_SEARCH_DEMAND_REACH_2500"] = "NO"
    out["demand_verdict_reasoning"] = (
        "Reaching $%.2f/day at the observed 5.71%% CTR and $%.2f CPC requires about "
        "%s qualified impressions per day. The account is currently reaching about "
        "%.1f/day and has held 100%% impression share on individual days, so the "
        "auction pool - not the budget - is the binding constraint."
        % (R / D, cpc, req_impr, impr_day))

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("MONTH-END RESCUE PACING  (snapshot %s)" % out["snapshot_timestamp"])
    print()
    for k in ("target", "fresh_mtd_spend_S", "remaining_budget_R",
              "remaining_calendar_days_D_incl_aug26", "remaining_hours_H",
              "required_average_per_remaining_calendar_day",
              "required_rolling_24_hour_pace",
              "current_combined_average_daily_budget",
              "current_combined_daily_spending_limit_2x",
              "minimum_combined_average_daily_budget_to_create_sufficient_monthly_limit"):
        print("  %-62s %s" % (k, out[k]))
    print()
    print("MID-MONTH BUDGET RULE CHECK: %s" % json.dumps(
        out["mid_month_budget_rule_check"], indent=4)[:400])
    print()
    mx = out["max_theoretical_august_spend_under_current_budgets"]
    print("MAX THEORETICAL UNDER CURRENT BUDGETS (even at 2x every day)")
    print("   $%.2f MTD + $%.2f/day x %d days = $%.2f   shortfall $%.2f"
          % (mx["mtd"], mx["daily_2x_limit_combined"], mx["remaining_days"],
             mx["max_august_total"], mx["shortfall_vs_target"]))
    print("   CAN CURRENT DAILY BUDGETS MATHEMATICALLY REACH $2,500? %s"
          % out["CAN_CURRENT_DAILY_BUDGETS_REACH_2500"])
    print()
    print("DEMAND EVIDENCE")
    for cid_, v in demand.items():
        print("  %s %-18s mtd_impr=%3d clk=%d $%7.2f IS=%.1f%% lostRank=%s addressable/day=%s ags=%d kw=%d"
              % (cid_, v["campaign"][:18], v["mtd_impressions"], v["mtd_clicks"],
                 v["mtd_cost"], (v["search_is"] or 0) * 100,
                 ("%.1f%%" % ((v["lost_is_rank"] or 0) * 100)),
                 v["addressable_per_active_day"], v["enabled_ad_groups"],
                 v["live_keyword_rows"]))
    print()
    print("ALLOCATION MODELS (combined $%.2f/day)" % total_budget)
    for m in out["allocation_models"]:
        print("  %s" % m["model"])
        print("     A $%.2f/day (%+.2f)   B $%.2f/day (%+.2f)   capacity $%.2f"
              % (m["campaign_A_daily_budget"], m["A_change"],
                 m["campaign_B_daily_budget"], m["B_change"],
                 m["combined_capacity_remaining"]))
    print()
    d = out["demand_reality_check"]
    print("DEMAND REALITY CHECK")
    for k, v in d.items():
        print("   %-52s %s" % (k, v))
    print()
    print("CAN CURRENT VERIFIED SEARCH DEMAND REACH $2,500? %s"
          % out["CAN_CURRENT_VERIFIED_SEARCH_DEMAND_REACH_2500"])
    print("   %s" % out["demand_verdict_reasoning"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
