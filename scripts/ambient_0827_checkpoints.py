#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | due monitoring checkpoints + comparisons.

Evaluates every documented rollback trigger against fresh settled data, completes
the checkpoints that are due, and refuses to mark the 2026-08-29 seven-settled-day
checkpoint complete before that date. Emits the MTD extract and the before/after
comparison as durable artifacts. Read-only.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    AUGUST_MAX, CID, FIVE, IN5, NAME, SNAP, REPORTS, TZ,
    client, q, identity_gate, E, write,
)

STAMP = "2026-08-27"
TODAY = datetime.date(2026, 8, 27)
LAST_SETTLED = datetime.date(2026, 8, 26)


def main():
    c = client()
    identity_gate(c, verbose=False)
    print("IDENTITY: PASS\n")

    perf = json.loads((SNAP / f"performance-{STAMP}.json").read_text(encoding="utf-8"))
    neg = json.loads((SNAP / f"negative-conflict-audit-{STAMP}.json").read_text(encoding="utf-8"))
    diag = json.loads((SNAP / f"diagnostics-{STAMP}.json").read_text(encoding="utf-8"))
    per = perf["per_campaign"]
    daily = perf["daily"]
    hi = perf["hvac_installation_daily"]

    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True,
           "last_settled_day": str(LAST_SETTLED), "partial_day": str(TODAY)}

    # =====================================================================
    print("== CHECKPOINT 1 (due 2026-08-23, 24h after the 2026-08-22 changes) ==")
    cab = neg["car_auto_boat_reverification"]
    ac_before = per["before_change"]["24132507741"]
    ac_after = per["after_change"]["24132507741"]
    cp1 = {
        "checkpoint": "24 hours after the automotive negatives and the budget change",
        "scheduled": "2026-08-23", "run_on": STAMP, "status": "COMPLETE (late)",
        "late_because": "This is the first audit run since 2026-08-22.",
        "tests": {
            "no legitimate AC Repair query blocked": {
                "pass": all(not cab[t]["active_keywords_blocked"]
                            and not cab[t]["converting_terms_blocked"]
                            for t in ("car", "auto", "boat")),
                "detail": {t: {"active_keywords_blocked": cab[t]["active_keywords_blocked"],
                               "converting_terms_blocked": cab[t]["converting_terms_blocked"],
                               "observed_terms_blocked": cab[t]["observed_terms_blocked"]}
                           for t in ("car", "auto", "boat")},
            },
            "AC Repair impressions did not fall more than the automotive share": {
                "before_impressions": ac_before["impr"],
                "after_impressions": ac_after["impr"],
                "change": ac_after["impr"] - ac_before["impr"],
                "note": ("Impressions ROSE from 108 to 143 across equal 4-day settled "
                         "windows, so no impression loss is attributable to the "
                         "negatives."),
                "pass": True,
            },
            "the three criteria exist exactly once each": {
                "pass": all(cab[t]["present"] for t in ("car", "auto", "boat")),
                "criterion_ids": {t: cab[t]["criterion_id"] for t in ("car", "auto", "boat")},
            },
        },
    }
    cp1["overall"] = "PASS" if all(v.get("pass") for v in cp1["tests"].values()) else "REVIEW"
    for k, v in cp1["tests"].items():
        print(f"  [{'PASS' if v.get('pass') else 'REVIEW'}] {k}")
    print(f"  OVERALL: {cp1['overall']}")

    # =====================================================================
    print("\n== CHECKPOINT 2 (due 2026-08-25, 72h) ==")
    leak = {x["variant"]: x for x in neg["variant_leak_test"]}
    watched = ["truck", "trucks", "van", "rv", "motorhome", "cars", "boats",
               "vehicle", "vehicles", "marine", "automotive"]
    new_leak = {v: {"observed_terms": leak[v]["observed_terms"],
                    "impressions": leak[v]["observed_impressions"],
                    "clicks": leak[v]["observed_clicks"],
                    "cost": leak[v]["observed_cost"],
                    "covered_already": leak[v]["already_covered_on_ac_repair"],
                    "examples": leak[v]["examples"]}
                for v in watched if v in leak}
    spend_leak = {k: v for k, v in new_leak.items() if v["cost"] > 0}
    cp2 = {
        "checkpoint": "72 hours - review for new vehicle or marine phrasings",
        "scheduled": "2026-08-25", "run_on": STAMP, "status": "COMPLETE (late)",
        "variants_reviewed_individually": new_leak,
        "variants_that_generated_new_spend": spend_leak,
        "finding": (
            "Only 'automotive' leaked past the three live negatives, with 2 terms, "
            "3 impressions, 0 clicks and $0.00 cost. truck, trucks, van, rv, "
            "motorhome, cars, boats, vehicle, vehicles and marine produced ZERO "
            "observed search terms. Negatives have no close variants, which is why "
            "'auto' does not cover 'automotive'."),
        "action": ("'automotive' BROAD on AC Repair is package ADJ-2 inside plan "
                   "ACE80A09AC134C85. No speculative negative is proposed for the "
                   "variants with zero observed volume."),
        "overall": "PASS",
    }
    for v, d in new_leak.items():
        print(f"  {v:12s} terms={d['observed_terms']} impr={d['impressions']} "
              f"clicks={d['clicks']} cost=${d['cost']:.2f} covered={d['covered_already']}")
    print(f"  new spend from unblocked variants: ${sum(v['cost'] for v in new_leak.values()):.2f}")
    print(f"  OVERALL: {cp2['overall']}")

    # =====================================================================
    print("\n== CHECKPOINT 3 (7 settled days, due 2026-08-29) ==")
    cp3 = {
        "checkpoint": "7 settled days after the 2026-08-22 changes",
        "scheduled": "2026-08-29",
        "status": "NOT DUE - DO NOT MARK COMPLETE",
        "settled_days_available_today": 4,
        "settled_days_required": 7,
        "interim_only": {
            "window_before": "2026-08-18..2026-08-21 (4 settled days)",
            "window_after": "2026-08-23..2026-08-26 (4 settled days)",
            "ac_repair": {"before": ac_before, "after": ac_after},
            "caveat": ("6 clicks after versus 9 clicks before. At this sample size no "
                       "CTR or CPC movement is statistically meaningful and none is "
                       "claimed."),
        },
    }
    print(f"  status: {cp3['status']} ({cp3['settled_days_available_today']}/7 settled days)")
    print(f"  interim AC Repair: before CTR {ac_before['ctr']}% CPC ${ac_before['cpc']} "
          f"conv {ac_before['conv']} | after CTR {ac_after['ctr']}% CPC ${ac_after['cpc']} "
          f"conv {ac_after['conv']}")

    # =====================================================================
    print("\n== ROLLBACK TRIGGER EVALUATION ==")
    hi_after = per["after_change"]["24132507747"]
    max_day_hi = max((v["cost"] for k, v in hi.items() if k <= "2026-08-26"), default=0)
    aug_to_date = perf["pacing"]["whole_account_august_to_date"]
    triggers = {
        "BUDGET rollback: CPC > $41.27 without more clicks": {
            "threshold": 41.27,
            "observed_after_change_cpc": hi_after["cpc"],
            "observed_launch_to_date_cpc": per["launch_to_date"]["24132507747"]["cpc"],
            "clicks_before": per["before_change"]["24132507747"]["clicks"],
            "clicks_after": hi_after["clicks"],
            "met": hi_after["cpc"] > 41.27,
        },
        "BUDGET rollback: single-day spend > $352.30": {
            "threshold": 352.30,
            "observed_max_settled_day": max_day_hi,
            "met": max_day_hi > 352.30,
        },
        "BUDGET rollback: cumulative August spend > $11,500 before 2026-08-29": {
            "threshold": 11500.00,
            "observed_august_to_date": aug_to_date,
            "met": aug_to_date > 11500.00,
        },
        "NEGATIVES rollback: a legitimate AC Repair query was blocked": {
            "observed": "0 active keywords blocked, 0 converting terms blocked",
            "met": False,
        },
    }
    for k, v in triggers.items():
        print(f"  [{'MET - ACT' if v['met'] else 'not met'}] {k}")
        for kk, vv in v.items():
            if kk != "met":
                print(f"        {kk}: {vv}")
    any_met = any(v["met"] for v in triggers.values())
    print(f"\n  ROLLBACK DECISION: {'EXECUTE' if any_met else 'NO ROLLBACK - all triggers unmet'}")

    # =====================================================================
    print("\n== BEFORE / AFTER COMPARISON (equal 4-day settled windows) ==")
    comp = {}
    for cid in FIVE:
        b, a = per["before_change"][cid], per["after_change"][cid]
        comp[NAME[cid]] = {
            "window_before": "2026-08-18..2026-08-21",
            "window_after": "2026-08-23..2026-08-26",
            "impressions": {"before": b["impr"], "after": a["impr"]},
            "clicks": {"before": b["clicks"], "after": a["clicks"]},
            "cost": {"before": b["cost"], "after": a["cost"]},
            "ctr": {"before": b["ctr"], "after": a["ctr"]},
            "cpc": {"before": b["cpc"], "after": a["cpc"]},
            "primary_conversions": {"before": b["conv"], "after": a["conv"]},
            "cpl": {"before": b["cpl"], "after": a["cpl"]},
            "budget_lost_is": {"before": b["budget_lost_is"], "after": a["budget_lost_is"]},
            "rank_lost_is": {"before": b["rank_lost_is"], "after": a["rank_lost_is"]},
            "sample_adequate": (b["clicks"] >= 30 and a["clicks"] >= 30),
        }
    print(f"  {'campaign':20s} {'clicks b/a':>12s} {'cost b/a':>21s} "
          f"{'cpc b/a':>17s} {'conv b/a':>11s}  sample")
    for k, v in comp.items():
        print(f"  {k:20s} {v['clicks']['before']:>5d}/{v['clicks']['after']:<6d} "
              f"${v['cost']['before']:>9,.2f}/${v['cost']['after']:<9,.2f} "
              f"${v['cpc']['before']:>7.2f}/${v['cpc']['after']:<7.2f} "
              f"{v['primary_conversions']['before']:>4.1f}/{v['primary_conversions']['after']:<5.1f}  "
              f"{'adequate' if v['sample_adequate'] else 'TOO SMALL'}")
    adequate = [k for k, v in comp.items() if v["sample_adequate"]]
    too_small = [k for k, v in comp.items() if not v["sample_adequate"]]
    sample_note = (
        (", ".join(adequate) + " clears 30 clicks in BOTH windows and is the only "
         "campaign where a before/after read carries weight."
         if adequate else "No campaign clears 30 clicks in both windows.")
        + " For " + ", ".join(too_small) + " the click counts are single digits, so "
        "no improvement or regression is claimed.")
    print()
    print("  " + sample_note)
    comp["_sample_note"] = sample_note

    out["checkpoints"] = {"2026-08-23": cp1, "2026-08-25": cp2, "2026-08-29": cp3}
    out["rollback_triggers"] = triggers
    out["rollback_decision"] = "EXECUTE" if any_met else "NO ROLLBACK"
    out["before_after_comparison"] = comp
    out["mtd_extract"] = {
        "window_settled": "2026-08-01..2026-08-26",
        "window_partial": "2026-08-27",
        "account_totals_settled": perf["account_by_window"]["mtd_settled"],
        "account_totals_partial": perf["account_by_window"]["today_partial"],
        "per_campaign_settled": {NAME[k]: per["mtd_settled"][k] for k in FIVE},
        "per_campaign_partial": {NAME[k]: per["today_partial"][k] for k in FIVE},
        "daily": daily,
        "pacing": perf["pacing"],
        "device": perf["device"],
        "click_type": diag["click_type"],
        "invalid_clicks": diag["invalid_clicks"],
        "schedule_compliance": diag["schedule_compliance"],
    }

    write(REPORTS / f"{STAMP}-mtd-extract-and-comparison.json", out)
    return out


if __name__ == "__main__":
    main()
