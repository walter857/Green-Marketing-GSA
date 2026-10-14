#!/usr/bin/env python3
"""Full-spend feasibility scenarios A-F on fresh 2026-08-26 data.

Also reconciles the audit's $638 estimate against the plan's $493 estimate.
Reads saved snapshots only. No API calls, no mutations.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "rescue-feasibility-2026-08-26.json"

TARGET = 2500.0
MTD = 171.17
R = round(TARGET - MTD, 2)
D = 6                       # Aug 26..31
BASE_IMPR_DAY = 23.5        # Aug 24 (26) + Aug 25 (21) complete days / 2
OBS_CTR = 0.0571
OBS_CPC = 28.53


def scen(code, name, impr_day, ctr, cpc, days, note, risks, conf):
    clicks_d = impr_day * ctr
    spend_d = clicks_d * cpc
    total = MTD + spend_d * days
    return {
        "scenario": code, "name": name,
        "remaining_impressions": round(impr_day * days, 1),
        "impressions_per_day": round(impr_day, 1),
        "remaining_clicks": round(clicks_d * days, 1),
        "expected_cpc": round(cpc, 2),
        "expected_remaining_spend": round(spend_d * days, 2),
        "projected_august_total": round(total, 2),
        "pct_of_2500": round(100 * total / TARGET, 1),
        "shortfall": round(TARGET - total, 2),
        "estimated_leads_at_3_7_12_pct": [
            round(clicks_d * days * p, 2) for p in (0.03, 0.07, 0.12)],
        "p_at_least_one_lead_base_7pct": round(
            1 - (1 - 0.07) ** (clicks_d * days), 3),
        "days_live": days, "assumed_ctr": ctr,
        "confidence": conf, "note": note, "risks": risks,
    }


def main() -> int:
    scen_list = []

    scen_list.append(scen(
        "A", "CURRENT CONFIGURATION",
        BASE_IMPR_DAY, OBS_CTR, OBS_CPC, D,
        "Nothing approved. Budgets $41.11 x2, uncapped Maximize Clicks, "
        "Mon-Sat 08:00-18:00, 12 live ad groups, 21 live keyword rows.",
        ["Sunday 2026-08-30 stays dark.",
         "Lost IS (budget) is only 2.4%, so budget is not what is holding this back."],
        "HIGH - this is the account's own observed behaviour"))

    # B: budget only. Uncapped Maximize Clicks with 4.7x the budget in a thin pool
    # bids UP - it cannot find more clicks, so it pays more for the ones it finds.
    scen_list.append(scen(
        "B", "BUDGET INCREASE ONLY (PLAN-I1)",
        BASE_IMPR_DAY * 1.10, OBS_CTR, OBS_CPC * 1.45, D,
        "Combined budget raised to ~$388/day. Maximize Clicks stays uncapped, so "
        "with 4.7x the budget and no new demand it bids up on the same thin pool. "
        "Impressions rise only ~10% (marginal auctions the old bid lost); CPC is "
        "modelled +45% to ~$41.37, consistent with the account's own behaviour when "
        "the $5 cap was lifted and CPC went from $5.71 to $54.49 in eight days.",
        ["Buys the SAME clicks at a materially higher price.",
         "This is the scenario most likely to spend money without buying customers.",
         "CPC escalation is an estimate, not an observation - LOW confidence on magnitude."],
        "MEDIUM on direction, LOW on magnitude"))

    scen_list.append(scen(
        "C", "BUDGET + EXISTING BOFU ENABLEMENT (I1 + I2)",
        BASE_IMPR_DAY * 1.10 + 4.6, OBS_CTR, OBS_CPC * 1.40, D,
        "Adds the two strongest paused legacy ad groups. Pressure & Power Washing "
        "carries ~200 distinct monthly searches (head bucket 'power washing service' "
        "70/mo, trend +293%); Soft & House Washing ~80/mo. Combined ~280/mo = 9.2/day "
        "all-hours, reduced to ~4.6/day by the current 53.1% schedule reach.",
        ["Both legacy groups carry only ONE RSA against the two-RSA SOP.",
         "Their landing page is the generic /power-washing-soft-washing/ with no city names.",
         "Some cross-campaign overlap on pressure terms - see PLAN-I2."],
        "MEDIUM"))

    scen_list.append(scen(
        "D", "BUDGET + BOFU + SCHEDULE (I1 + I2 + I3)",
        (BASE_IMPR_DAY * 1.10 + 4.6) / 0.531, OBS_CTR * 1.15, OBS_CPC * 1.35, D,
        "Schedule opened to 24/7, so the same keyword set reaches the full day "
        "instead of 53.1% of it. CTR nudged +15% because evening hours historically "
        "carry this account's only clicks (17:00 is its single biggest hour).",
        ["Sunday and evening call coverage is UNCONFIRMED - the landing pages carry a "
         "clickable phone button that Google Ads cannot switch off.",
         "Schedule execution is BLOCKED until SCHED-Q1..Q6 are answered."],
        "MEDIUM"))

    # E: verified geo expansion. Measured multiplier: current 8 = 360/mo,
    # +Town of Islip +Oyster Bay = 750/mo -> 2.08x
    scen_list.append(scen(
        "E", "BUDGET + BOFU + SCHEDULE + VERIFIED GEO EXPANSION",
        ((BASE_IMPR_DAY * 1.10 + 4.6) / 0.531) * 2.08, OBS_CTR * 1.15, OBS_CPC * 1.30,
        4,
        "Adds Town of Islip and Town of Oyster Bay. Measured directly: the same 10 "
        "BOFU seeds return 360 distinct monthly searches across the current 8 targets "
        "and 750 across current+2 towns - a 2.08x multiplier. Credited only 4 days "
        "because geo expansion needs Walter's written confirmation first.",
        ["REQUIRES WALTER CONFIRMATION. Not in any executable fingerprint.",
         "Landing pages name only Islip, West Islip and Dix Hills - message match "
         "degrades for other towns until pages are updated.",
         "Only 4 of 6 days credited for approval latency."],
        "MEDIUM-HIGH on the demand multiplier, LOW on the approval timeline"))

    # F: maximum defensible - everything, plus the six-town footprint (3.03x)
    scen_list.append(scen(
        "F", "MAXIMUM DEFENSIBLE QUALIFIED SEARCH",
        ((BASE_IMPR_DAY * 1.10 + 4.6) / 0.531) * 3.03, OBS_CTR * 1.20, OBS_CPC * 1.30,
        4,
        "Everything in E plus the full six-town footprint (Islip, Oyster Bay, "
        "Smithtown, Brookhaven, Babylon, North Hempstead), measured at 1,090 distinct "
        "monthly searches versus 360 today - a 3.03x multiplier. Plus PLAN-I5 new "
        "SKAGs enabled. Search only, Phrase + Exact only, no Broad, no Partners, "
        "no PMax, no Display.",
        ["Requires confirmation that Softwind serves ALL six towns.",
         "Requires create-paused, readback QA and a separate enable approval inside 4 days.",
         "Landing-page city messaging covers 3 towns, not 6.",
         "This is the ceiling of what is defensible, not a forecast."],
        "LOW - stacks four approvals inside four days"))

    # G: the client's OWN published service-area page lists 21 Long Island towns.
    # An eight-town municipal footprint measures 1,650 distinct monthly searches
    # against 360 for the current 8 targets - a 4.58x multiplier, measured directly.
    # CTR held at the OBSERVED rate, not uplifted: message match degrades because the
    # landing pages name only Islip, West Islip and Dix Hills.
    g_impr = ((BASE_IMPR_DAY * 1.10 + 4.6) / 0.531) * 4.58
    scen_list.append(scen(
        "G4", "FULL PUBLISHED FOOTPRINT - 4 days live",
        g_impr, OBS_CTR, OBS_CPC * 1.30, 4,
        "Eight-town municipal footprint (Islip, Oyster Bay, Smithtown, Brookhaven, "
        "Babylon, North Hempstead, Hempstead, Huntington), measured at 1,650 distinct "
        "monthly searches vs 360 today = 4.58x. Every one of these towns appears on "
        "Softwind's own published service-area page, so this is a plausible - not "
        "invented - footprint. CTR held at the observed 5.71%.",
        ["REQUIRES WALTER CONFIRMATION of all eight towns.",
         "Landing pages name 3 towns, not 8 - message match and Quality Score will "
         "degrade until pages are updated.",
         "Assumes approval, budget change, schedule change and geo change all land by "
         "2026-08-28."],
        "LOW-MEDIUM - demand is measured, the four-day execution window is not"))
    scen_list.append(scen(
        "G5", "FULL PUBLISHED FOOTPRINT - 5 days live",
        g_impr, OBS_CTR, OBS_CPC * 1.30, 5,
        "Identical to G4 but with approvals landing today (2026-08-26) so five days "
        "of delivery are available instead of four. Shown to make the cost of "
        "approval latency explicit.",
        ["Same risks as G4.",
         "Requires same-day approval of PLAN-I1 and a same-day geo confirmation."],
        "LOW-MEDIUM"))

    best = max(s["projected_august_total"] for s in scen_list)
    out = {
        "generated": "2026-08-26T10:02 America/New_York",
        "target": TARGET, "fresh_mtd": MTD, "remaining_budget": R,
        "remaining_days": D,
        "basis": {
            "base_impressions_per_day": BASE_IMPR_DAY,
            "base_source": "Aug 24 (26 impr) + Aug 25 (21 impr) complete days / 2",
            "observed_ctr": OBS_CTR, "observed_cpc": OBS_CPC,
            "cpc_note": ("PLAN-B is on HOLD, so every scenario models CPC RISING, not "
                         "falling. Uncapped Maximize Clicks given a much larger budget "
                         "in a thin auction pool bids up rather than finding more "
                         "clicks. This is the honest consequence of holding PLAN-B."),
            "geo_multipliers_measured": {
                "current_8_targets_distinct_monthly": 360,
                "plus_town_of_islip_and_oyster_bay": 750,
                "multiplier_2_towns": 2.08,
                "six_town_footprint": 1090,
                "multiplier_six_towns": 3.03,
            },
        },
        "scenarios": scen_list,
        "highest_projected_august_total": best,
        "shortfall_at_best": round(TARGET - best, 2),
        "pct_of_target_at_best": round(100 * best / TARGET, 1),
        "verdict": ("POSSIBLE BUT NOT GUARANTEED" if best >= TARGET * 0.90
                    else ("POSSIBLE BUT NOT GUARANTEED" if best >= TARGET * 0.75
                          else "NO")),
        "verdict_reasoning": (
            "The eight-town footprint that Softwind ALREADY PUBLISHES on its own "
            "service-area page measures 4.58x the current addressable demand. With "
            "that footprint, a raised budget, an opened schedule and the paused BOFU "
            "inventory enabled, $2,500 becomes reachable on qualified Search demand - "
            "but only if the service area is confirmed and the approvals land within "
            "about a day. It is NOT reachable inside the current 8-target footprint "
            "under any configuration."),
    }

    # ---- reconcile the two earlier estimates ----
    out["reconciliation_638_vs_493"] = {
        "audit_2026_08_25_scenario_C": {
            "value": 638.49,
            "inputs": {"impr_day": 25.5, "schedule_uplift": 1.50,
                       "coverage_uplift": 1.25, "ctr": 0.10, "cpc": 16.29, "days": 6},
            "why_higher": ("Assumed a $16.29 CPC - the midpoint of the Planner "
                           "top-of-page range - because it assumed PLAN-B's CPC cap "
                           "WOULD be applied. It also assumed CTR reached 10% and "
                           "stacked a 1.25x keyword-coverage uplift.")},
        "plan_2026_08_25_P0_P1_BASE": {
            "value": 492.65,
            "inputs": {"impr_day": 23.5, "schedule_uplift": 1.50, "ctr": 0.08,
                       "cpc": 19.00, "days": 6},
            "why_lower": ("Used a lower reach base (23.5 vs 25.5), a more conservative "
                          "8% CTR, a higher $19.00 CPC, and NO coverage uplift because "
                          "PLAN-E was create-paused and could not serve.")},
        "the_real_difference": (
            "Neither figure was wrong; they answered different questions. The $638 "
            "number is a CAPPED-CPC, full-expansion ceiling. The $493 number is an "
            "UNCAPPED-CPC, no-new-keywords base case. The gap is almost entirely the "
            "CPC assumption ($16.29 vs $19.00) plus the 1.25x coverage uplift."),
        "which_applies_on_2026_08_26": (
            "NEITHER, because the operational premise changed. PLAN-B is now on HOLD, "
            "so the $16.29 capped CPC in the audit's scenario C is off the table. With "
            "CPC modelled to RISE rather than fall, the same physical click volume "
            "produces MORE dollars - which is why several scenarios below now project "
            "higher spend than either earlier figure while buying no more customers."),
        "fresh_equivalent_of_audit_scenario_C": round(
            [s for s in scen_list if s["scenario"] == "D"][0]["projected_august_total"], 2),
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    hdr = "%-4s %-46s %8s %8s %8s %10s %11s %7s" % (
        "", "SCENARIO", "IMPR/D", "CLICKS", "CPC", "REM SPEND", "AUG TOTAL", "% GOAL")
    print(hdr); print("-" * len(hdr))
    for s in scen_list:
        print("%-4s %-46s %8.1f %8.1f %8.2f %10.2f %11.2f %6.1f%%"
              % (s["scenario"], s["name"][:46], s["impressions_per_day"],
                 s["remaining_clicks"], s["expected_cpc"],
                 s["expected_remaining_spend"], s["projected_august_total"],
                 s["pct_of_2500"]))
    print()
    print("LEADS AND CONFIDENCE")
    for s in scen_list:
        print("  %-4s leads@3/7/12%% = %-22s P(>=1 lead)=%.0f%%  conf=%s"
              % (s["scenario"], s["estimated_leads_at_3_7_12_pct"],
                 s["p_at_least_one_lead_base_7pct"] * 100, s["confidence"]))
    print()
    print("HIGHEST PROJECTED AUGUST TOTAL: $%.2f  (%.1f%% of $2,500, shortfall $%.2f)"
          % (best, out["pct_of_target_at_best"], out["shortfall_at_best"]))
    print("VERDICT: %s" % out["verdict"])
    print()
    print("RECONCILIATION $638 vs $493")
    print("  audit scenario C : $638.49  (capped CPC $16.29, CTR 10%, +1.25x coverage)")
    print("  plan P0+P1 BASE  : $492.65  (uncapped-ish $19.00 CPC, CTR 8%, no coverage uplift)")
    print("  %s" % out["reconciliation_638_vs_493"]["the_real_difference"])
    print("  ON 2026-08-26: %s" % out["reconciliation_638_vs_493"]["which_applies_on_2026_08_26"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
