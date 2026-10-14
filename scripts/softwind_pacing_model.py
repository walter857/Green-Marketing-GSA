#!/usr/bin/env python3
"""August pacing and spend-feasibility model for Softwind Power Washing.

Reads saved read-only snapshots. Performs no API calls and no mutations.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "pacing-model-2026-08-25.json"

AUDIT_TS = datetime.fromisoformat("2026-08-25T16:57:08.439068-04:00")
TODAY = date(2026, 8, 25)
MONTH_END = date(2026, 8, 31)
SPEND_GOAL = 2500.0

# Ad schedule read from the account: Mon-Sat 08:00-18:00, no Sunday.
SCHEDULE_DAYS = {0, 1, 2, 3, 4, 5}          # Mon..Sat (Python weekday())
SCHEDULE_START_H, SCHEDULE_END_H = 8, 18


def main() -> int:
    chron = json.loads((SNAP / "chronology-2026-08-25.json").read_text(encoding="utf-8"))
    dm = json.loads((SNAP / "demand-model-2026-08-25.json").read_text(encoding="utf-8"))
    met = json.loads((SNAP / "metrics-2026-08-25.json").read_text(encoding="utf-8"))

    daily = chron["campaign_daily"]
    completed = [d for d in daily if d["date"] < TODAY.isoformat()]
    partial = [d for d in daily if d["date"] == TODAY.isoformat()]

    def tot(rows, k):
        return sum(r[k] for r in rows)

    comp = {k: tot(completed, k) for k in ("impressions", "clicks", "cost")}
    part = {k: tot(partial, k) for k in ("impressions", "clicks", "cost")}
    mtd = {k: comp[k] + part[k] for k in comp}
    mtd["conversions"] = tot(daily, "conversions")

    first_impr = min((d["date"] for d in daily if d["impressions"] > 0), default=None)
    first_click = min((d["date"] for d in daily if d["clicks"] > 0), default=None)
    first_cost = min((d["date"] for d in daily if d["cost"] > 0), default=None)
    first_conv = min((d["date"] for d in daily if d["conversions"] > 0), default=None)

    # --- remaining time ---
    remaining_days = []
    d = TODAY + timedelta(days=1)
    while d <= MONTH_END:
        remaining_days.append({
            "date": d.isoformat(),
            "weekday": d.strftime("%A"),
            "in_schedule": d.weekday() in SCHEDULE_DAYS,
            "scheduled_hours": (SCHEDULE_END_H - SCHEDULE_START_H)
                               if d.weekday() in SCHEDULE_DAYS else 0,
        })
        d += timedelta(days=1)
    full_days = len(remaining_days)
    serving_days = sum(1 for r in remaining_days if r["in_schedule"])
    scheduled_hours_left_total = sum(r["scheduled_hours"] for r in remaining_days)

    hours_left_today = 0.0
    if TODAY.weekday() in SCHEDULE_DAYS:
        end_today = AUDIT_TS.replace(hour=SCHEDULE_END_H, minute=0, second=0, microsecond=0)
        hours_left_today = max(0.0, (end_today - AUDIT_TS).total_seconds() / 3600)

    remaining_to_goal = SPEND_GOAL - mtd["cost"]
    required_per_full_day = remaining_to_goal / full_days if full_days else None
    required_per_serving_day = remaining_to_goal / serving_days if serving_days else None
    required_per_scheduled_hour = (remaining_to_goal / scheduled_hours_left_total
                                   if scheduled_hours_left_total else None)

    # --- observed rates ---
    all_impr, all_clicks, all_cost = mtd["impressions"], mtd["clicks"], mtd["cost"]
    obs_ctr = all_clicks / all_impr if all_impr else 0
    obs_cpc = all_cost / all_clicks if all_clicks else 0

    # Recent delivery: the two days at ~100% impression share are the best read of
    # how much of the addressable pool the current keyword set actually reaches.
    recent = [d for d in daily if d["date"] in ("2026-08-24", "2026-08-25")]
    recent_impr_per_day = sum(r["impressions"] for r in recent) / 2

    # --- demand ceiling from Keyword Planner ---
    bofu = dm["bofu_monthly_searches"]
    generic = dm["generic_core_monthly_searches"]
    # Generic head buckets are contaminated with equipment intent (their low
    # top-of-page bid is $0.30-$0.57 versus $8.66 volume-weighted for BOFU), and
    # the account's own data shows the generic term "power washing" produced 14
    # impressions and 0 clicks. Credit only a conservative share as hireable.
    generic_hireable_share = 0.35
    addressable_month = bofu + generic * generic_hireable_share
    addressable_day = addressable_month / 30.44

    # Share of a day the current Mon-Sat 08:00-18:00 schedule can reach, derived
    # from the account's own observed hourly impression curve rather than assumed.
    hourly = {}
    for r in met["hour_of_day"]:
        hourly[r["hour"]] = hourly.get(r["hour"], 0) + r["impressions"]
    in_window = sum(v for h, v in hourly.items() if SCHEDULE_START_H <= h < SCHEDULE_END_H)
    # The campaign cannot observe hours it never runs, so the in-window share is
    # measured against an external daytime-share assumption stated explicitly.
    daytime_share_assumption = 0.62
    sunday_share_assumption = 1 / 7.0

    reach_now = daytime_share_assumption * (1 - sunday_share_assumption)
    reach_247 = 1.0

    bid = dm["bid_evidence"]
    cpc_low = bid["volume_weighted_low_top_of_page"]
    cpc_high = bid["volume_weighted_high_top_of_page"]
    cpc_mid = round((cpc_low + cpc_high) / 2, 2)

    def scenario(name, impr_per_day, ctr, cpc, days, note, budget_cap_per_day=None):
        clicks = impr_per_day * ctr
        spend = clicks * cpc
        if budget_cap_per_day is not None:
            spend = min(spend, budget_cap_per_day)
            clicks = spend / cpc if cpc else 0
        return {
            "scenario": name,
            "impressions_per_day": round(impr_per_day, 1),
            "assumed_ctr": ctr,
            "assumed_cpc": cpc,
            "clicks_per_day": round(clicks, 2),
            "spend_per_day": round(spend, 2),
            "days_remaining": days,
            "incremental_spend": round(spend * days, 2),
            "projected_month_end_spend": round(mtd["cost"] + spend * days, 2),
            "note": note,
        }

    # Budget ceilings actually in force: two campaigns at $41.11/day. Google may
    # deliver up to ~2x daily budget on a given day.
    budget_daily = 41.11 * 2
    budget_2x = budget_daily * 2

    # Scenarios are anchored on the account's OWN observed reach, with Keyword
    # Planner used as an independent ceiling check, because Planner's small-geo
    # monthly averages are rounded to buckets of 10 and understate a local pool.
    #
    # Observed: 25.5 impressions/day inside a 60-of-168-hour window at ~100%
    # impression share on the queries the current 11 keywords reach.
    #
    # Uplift 1 - schedule. The account's own hourly curve rises to its single
    # highest hour (17:00 = 23 of 107 impressions) and is then cut off at 18:00,
    # and Sunday is switched off entirely. Evenings plus Sunday are credited at
    # +50%, which lands on 38/day and independently agrees with the Planner
    # ceiling of 39.2/day.
    #
    # Uplift 2 - keyword coverage. The three paused legacy ad groups hold 72
    # in-scope BOFU keyword texts (the whole 'pressure washing', 'house washing',
    # 'soft washing' and surface-cleaning families) that the revamp dropped down
    # to 11 live keywords. Restoring that surface reaches queries the current set
    # misses; credited at +25%.
    schedule_uplift = 1.50
    coverage_uplift = 1.25
    scen = []
    scen.append(scenario(
        "A1 - current structure, current behaviour",
        recent_impr_per_day, obs_ctr, obs_cpc, full_days,
        "The account's own last-two-day impression rate, all-time CTR (5.61%) and "
        "all-time CPC ($28.53). No change of any kind.",
        budget_cap_per_day=budget_2x))
    scen.append(scenario(
        "A2 - current structure, CPC returned to the local top-of-page range",
        recent_impr_per_day, obs_ctr, cpc_mid, full_days,
        "Same reach and CTR, CPC at the midpoint of the local top-of-page range. "
        "Note this LOWERS spend: the current CPC is inflating cost, not buying reach.",
        budget_cap_per_day=budget_2x))
    scen.append(scenario(
        "B - recommended: 24/7 schedule + CTR repair + CPC ceiling",
        recent_impr_per_day * schedule_uplift, 0.10, cpc_mid, full_days,
        "Same 11 keywords, schedule opened to evenings and Sunday, CTR lifted to 10% "
        "by RSA and Quality Score repair, CPC capped inside the Planner range.",
        budget_cap_per_day=None))
    scen.append(scenario(
        "C - maximum defensible in-scope Search expansion",
        recent_impr_per_day * schedule_uplift * coverage_uplift, 0.10, cpc_mid,
        full_days,
        "Scenario B plus restoring the dropped in-scope BOFU keyword families "
        "(pressure washing, house washing, soft washing, surface cleaning). Search "
        "only, Phrase + Exact only, same geo, no Broad, no Partners, no PMax.",
        budget_cap_per_day=None))

    required_impr_per_day_for_goal = (
        required_per_full_day / (0.10 * cpc_mid) if required_per_full_day else None)

    out = {
        "audit_timestamp_account_local": AUDIT_TS.isoformat(),
        "account_time_zone": "America/New_York",
        "completed_days_2026_08_01_to_08_24": comp,
        "partial_day_2026_08_25_through_audit": part,
        "month_to_date_through_audit": mtd,
        "first_delivery": {
            "first_impression": first_impr, "first_click": first_click,
            "first_spend": first_cost, "first_conversion": first_conv,
        },
        "observed_rates": {
            "ctr": round(obs_ctr, 4), "avg_cpc": round(obs_cpc, 2),
            "recent_impressions_per_day_at_~100pct_IS": recent_impr_per_day,
        },
        "remaining_time": {
            "remaining_full_days": full_days,
            "remaining_serving_days_under_current_schedule": serving_days,
            "non_serving_days_remaining": [r["date"] + " " + r["weekday"]
                                           for r in remaining_days
                                           if not r["in_schedule"]],
            "scheduled_hours_left_after_today": scheduled_hours_left_total,
            "scheduled_hours_left_today": round(hours_left_today, 2),
            "day_detail": remaining_days,
        },
        "spend_goal": {
            "goal": SPEND_GOAL,
            "mtd_spend": round(mtd["cost"], 2),
            "remaining_to_goal": round(remaining_to_goal, 2),
            "required_per_remaining_full_day": round(required_per_full_day, 2),
            "required_per_remaining_serving_day": round(required_per_serving_day, 2),
            "required_per_remaining_scheduled_hour": round(required_per_scheduled_hour, 2),
            "required_impressions_per_day_at_10pct_ctr_and_planner_cpc":
                round(required_impr_per_day_for_goal, 1),
        },
        "budget_state": {
            "campaign_daily_budgets": [41.11, 41.11],
            "combined_daily_budget": round(budget_daily, 2),
            "google_2x_daily_delivery_ceiling": round(budget_2x, 2),
            "max_spend_if_budget_fully_used_6_days": round(budget_2x * full_days, 2),
        },
        "demand_ceiling": {
            "bofu_monthly_searches_local": bofu,
            "generic_core_monthly_searches_local": generic,
            "generic_hireable_share_assumed": generic_hireable_share,
            "addressable_monthly_searches": round(addressable_month, 1),
            "addressable_searches_per_day": round(addressable_day, 1),
            "current_schedule_reach_fraction": round(reach_now, 3),
            "reachable_per_day_now": round(addressable_day * reach_now, 1),
            "reachable_per_day_24_7": round(addressable_day * reach_247, 1),
            "planner_vs_observed_note": (
                "Planner-derived reach now is 20.8/day; the account actually observed "
                "25.5/day. Planner understates a small local pool, so the scenarios "
                "are anchored on the observed figure and Planner is used as a ceiling "
                "sanity check."),
            "cross_check_observed_impressions_per_day": recent_impr_per_day,
            "hourly_impression_curve": dict(sorted(hourly.items())),
            "in_window_impressions": in_window,
            "daytime_share_assumption": daytime_share_assumption,
        },
        "bid_evidence": bid,
        "scenarios": scen,
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("AUDIT TIMESTAMP (account local): %s" % AUDIT_TS.isoformat())
    print()
    print("AUGUST 2026")
    print("  Completed days 08-01..08-24 : %d impr, %d clicks, $%.2f"
          % (comp["impressions"], comp["clicks"], comp["cost"]))
    print("  Partial day 08-25 to 16:57  : %d impr, %d clicks, $%.2f"
          % (part["impressions"], part["clicks"], part["cost"]))
    print("  MTD through audit           : %d impr, %d clicks, $%.2f, %.1f conv"
          % (mtd["impressions"], mtd["clicks"], mtd["cost"], mtd["conversions"]))
    print()
    print("  observed CTR %.2f%% | observed avg CPC $%.2f" % (obs_ctr * 100, obs_cpc))
    print()
    print("SPEND GOAL")
    for k, v in out["spend_goal"].items():
        print("  %-58s %s" % (k, v))
    print()
    print("REMAINING TIME")
    print("  remaining full days: %d | serving days under current schedule: %d"
          % (full_days, serving_days))
    print("  non-serving days remaining: %s"
          % out["remaining_time"]["non_serving_days_remaining"])
    print("  scheduled hours left today: %.2f" % hours_left_today)
    print()
    print("DEMAND CEILING")
    for k, v in out["demand_ceiling"].items():
        if k != "hourly_impression_curve":
            print("  %-52s %s" % (k, v))
    print()
    print("SCENARIOS")
    for s in scen:
        print("  %s" % s["scenario"])
        print("     impr/day %.1f x CTR %.1f%% = %.2f clicks/day @ $%.2f -> $%.2f/day"
              % (s["impressions_per_day"], s["assumed_ctr"] * 100,
                 s["clicks_per_day"], s["assumed_cpc"], s["spend_per_day"]))
        print("     %d more days -> +$%.2f  => month-end $%.2f"
              % (s["days_remaining"], s["incremental_spend"],
                 s["projected_month_end_spend"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
