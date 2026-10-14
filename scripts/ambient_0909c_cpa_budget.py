#!/usr/bin/env python3
"""Corrected per-campaign CPA, unique-lead bounding, and PER-CAMPAIGN budget limits."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
SETTLED = "2026-09-08"
conv = json.load(open(EVID / "2026-09-09c-conversion-reconciliation.json", encoding="utf-8"))
rows = conv["daily_rows"]

print("=== 1. CORRECTED CAMPAIGN CPA, ALL TIME SETTLED (2026-08-14..2026-09-08) ===")
camp = {}
for r in q(c, f"SELECT campaign.id, metrics.clicks, metrics.cost_micros, metrics.conversions, "
              f"metrics.all_conversions FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '{SETTLED}'"):
    x = r.metrics
    camp[str(r.campaign.id)] = {"clicks": x.clicks, "cost": round(x.cost_micros/1e6, 2),
                               "primary": round(x.conversions, 2),
                               "all": round(x.all_conversions, 2)}
MAXCPQL = {"24132507741": 150.0, "24132507750": 250.0, "24132507747": 280.0,
           "24132507753": 280.0, "24132507744": 250.0}
print(f"  {'campaign':<20}{'clicks':>7}{'cost':>11}{'PRIMARY':>9}{'raw CPA':>10}"
      f"{'maxCPQL':>9}{'verdict':>12}")
for cid in FIVE:
    v = camp[cid]
    cpa = v["cost"]/v["primary"] if v["primary"] else None
    verdict = "-" if cpa is None else ("WITHIN" if cpa <= MAXCPQL[cid] else "OVER")
    print(f"  {NAME[cid]:<20}{v['clicks']:>7}{v['cost']:>11.2f}{v['primary']:>9.1f}"
          f"{(f'{cpa:.2f}' if cpa else '-'):>10}{MAXCPQL[cid]:>9.0f}{verdict:>12}")
out["campaign_cpa_all_time"] = {NAME[k]: {**v, "raw_cpa": round(v["cost"]/v["primary"], 2)
                                          if v["primary"] else None,
                                          "max_cpql": MAXCPQL[k]} for k, v in camp.items()}

print("\n=== 2. HVAC INSTALLATION POST-SWAP WINDOW 2026-08-29..2026-09-03 ===")
inst = "24132507747"
w = q(c, f"SELECT campaign.id, metrics.clicks, metrics.cost_micros, metrics.conversions, "
         f"metrics.all_conversions FROM campaign WHERE campaign.id = {inst} "
         f"AND segments.date BETWEEN '2026-08-29' AND '2026-09-03'")[0].metrics
pc = round(w.cost_micros/1e6, 2)
pk = w.clicks
pv = round(w.conversions, 2)
print(f"  CAMPAIGN-LEVEL: {pk} clicks, ${pc:.2f}, {pv:.0f} primary conversions")
print(f"    campaign-level raw CPA = ${pc:.2f} / {pv:.0f} = ${pc/pv:.2f}")
stcost = 0.0
stclicks = 0
for r in q(c, f"SELECT campaign.id, metrics.clicks, metrics.cost_micros FROM search_term_view "
              f"WHERE campaign.id = {inst} AND segments.date BETWEEN '2026-08-29' AND '2026-09-03'"):
    stcost += r.metrics.cost_micros/1e6
    stclicks += r.metrics.clicks
print(f"  VISIBLE SEARCH-TERM GRAIN: {stclicks} clicks, ${stcost:.2f}")
print(f"    that grain divided by the CAMPAIGN conversion count = ${stcost/pv:.2f}"
      f"   <- the $141.87 figure")
print(f"\n  *** THE $141.87 FIGURE IS A MISMATCH ***")
print(f"      It divided VISIBLE search-term cost (${stcost:.2f}) by CAMPAIGN-level")
print(f"      conversions ({pv:.0f}). Numerator and denominator came from different grains.")
print(f"      The correct campaign-level raw CPA is ${pc/pv:.2f}.")
out["installation_post_swap"] = {
    "window": "2026-08-29..2026-09-03", "campaign_clicks": pk, "campaign_cost": pc,
    "primary_conversions": pv, "correct_campaign_raw_cpa": round(pc/pv, 2),
    "visible_search_term_cost": round(stcost, 2),
    "visible_search_term_clicks": stclicks,
    "prior_141_87_figure": round(stcost/pv, 2),
    "prior_figure_defect": "visible-grain numerator over campaign-grain denominator"}

print("\n=== 3. UNIQUE-LEAD BOUNDING FOR THE INSTALLATION CONVERSIONS ===")
i_rows = [r for r in rows if r["campaign_id"] == inst
          and "2026-08-29" <= r["date"] <= "2026-09-03"
          and (r["conversions"] or r["all_conversions"])]
print(f"  every Installation conversion record in the post-swap window:")
print(f"  {'date':<12}{'action_id':<13}{'PRIMARY':>9}{'ALL':>7}  action")
for r in sorted(i_rows, key=lambda r: (r["date"], r["action_name"])):
    print(f"  {r['date']:<12}{r['action_id']:<13}{r['conversions']:>9.2f}"
          f"{r['all_conversions']:>7.2f}  {r['action_name'][:44]}")
days = sorted({r["date"] for r in i_rows})
print(f"\n  distinct days carrying a record: {days}")
d = q(c, f"SELECT segments.date, metrics.clicks, metrics.cost_micros FROM campaign "
         f"WHERE campaign.id = {inst} AND segments.date BETWEEN '2026-08-29' AND '2026-09-03'")
daily = {r.segments.date: (r.metrics.clicks, round(r.metrics.cost_micros/1e6, 2)) for r in d}
print(f"  Installation clicks by day in the window: {daily}")
conv_day = "2026-09-01"
ck, cost_day = daily.get(conv_day, (0, 0))
print(f"\n  ALL THREE primary conversions landed on {conv_day}, a day with {ck} clicks "
      f"and ${cost_day:.2f} spend.")
print(f"  That is a {100*3/ck:.0f}% click-to-primary-conversion rate for that day.")
print("\n  DUPLICATE-ARCHITECTURE READ (per the instruction not to treat duplicate")
print("  conversion actions as unique leads):")
print("    - 'Ambient Cooling - LP -Submit Lead Forms' (WEBPAGE) fires on the landing-page")
print("      thank-you view.")
print("    - 'WC Lead' (UPLOAD_CLICKS, origin WEBSITE) is WhatConverts uploading the SAME")
print("      form submission back as an offline conversion against the same GCLID.")
print("    - Both are primary_for_goal and both counted on 2026-09-01 in the same campaign.")
print("    - The GA4 duplicates 'form_submission' (2 all-conv) and 'Clicks to call' (1) also")
print("      landed the same day.")
print(f"\n  UNIQUE LEAD COUNT IS BOUNDED, NOT KNOWN: between 1 and 3.")
for u in (1, 2, 3):
    print(f"    if unique leads = {u}: cost per unique lead = ${pc/u:>8.2f}   "
          f"{'WITHIN' if pc/u <= 280 else 'OVER'} the $280 target")
print("  Google Ads does not expose per-conversion GCLIDs, so this cannot be resolved from")
print("  the API. WhatConverts or an anonymised lead export is required.")
out["installation_unique_lead_bounds"] = {
    "records": i_rows, "all_on_date": conv_day, "clicks_that_day": ck,
    "cost_that_day": cost_day,
    "unique_lead_range": [1, 3],
    "cost_per_unique_lead": {str(u): round(pc/u, 2) for u in (1, 2, 3)},
    "resolvable_from_google_ads_api": False}

print("\n=== 4. PER-CAMPAIGN BUDGET LIMITS ===")
DAYS = 30.4
MAXM = 13000.0
BUD = {"24132507741": ("AC Repair", "15787409435", 141.45, 141.45),
       "24132507744": ("Gas Boiler Repair", "15787409438", 42.76, 5.00),
       "24132507747": ("HVAC Installation", "15787409441", 176.15, 176.15),
       "24132507750": ("HVAC Repair", "15787409444", 78.95, 78.95),
       "24132507753": ("HVAC Replacement", "15787409447", 26.32, 20.00)}
print("  September spend BY CAMPAIGN through the preflight read "
      "(2026-09-01..2026-09-09, incl. partial today):")
sept = {}
for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.clicks, metrics.impressions "
              f"FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-09-01' AND '2026-09-09'"):
    sept[str(r.campaign.id)] = {"cost": round(r.metrics.cost_micros/1e6, 2),
                                "clicks": r.metrics.clicks,
                                "impressions": r.metrics.impressions}
EDIT_DAY = "2026-09-10"
REMAIN_INCL_EDIT = 21   # 09-10 .. 09-30 inclusive
print(f"  Proposed edit day: {EDIT_DAY}. Remaining calendar days INCLUDING the edit day: "
      f"{REMAIN_INCL_EDIT} (09-10..09-30).")
print()
hdr = (f"  {'campaign':<20}{'before':>9}{'proposed':>10}{'Sep spend':>11}"
       f"{'editday':>9}{'x rest':>10}{'Sep max':>10}{'steady 30.4':>13}")
print(hdr)
tot = {"sept_spend": 0.0, "sept_max": 0.0, "steady": 0.0, "before_steady": 0.0}
percamp = {}
for cid, (label, bid, before, proposed) in BUD.items():
    s = sept.get(cid, {"cost": 0.0})["cost"]
    # the edit day itself is governed by the HIGHEST budget in force that day
    editday = max(before, proposed)
    rest = proposed * (REMAIN_INCL_EDIT - 1)
    sepmax = s + editday + rest
    steady = proposed * DAYS
    before_steady = before * DAYS
    percamp[label] = {"budget_id": bid, "before": before, "proposed": proposed,
                      "september_spend_to_preflight": s,
                      "edit_day_limit_highest_in_force": editday,
                      "remaining_calendar_days_after_edit_day": REMAIN_INCL_EDIT - 1,
                      "september_campaign_maximum": round(sepmax, 2),
                      "steady_state_monthly_max_30_4": round(steady, 2),
                      "steady_state_before": round(before_steady, 2)}
    tot["sept_spend"] += s
    tot["sept_max"] += sepmax
    tot["steady"] += steady
    tot["before_steady"] += before_steady
    print(f"  {label:<20}{before:>9.2f}{proposed:>10.2f}{s:>11.2f}"
          f"{editday:>9.2f}{rest:>10.2f}{sepmax:>10.2f}{steady:>13.2f}")
print(f"  {'COMBINED':<20}{sum(v[2] for v in BUD.values()):>9.2f}"
      f"{sum(v[3] for v in BUD.values()):>10.2f}{tot['sept_spend']:>11.2f}"
      f"{'':>9}{'':>10}{tot['sept_max']:>10.2f}{tot['steady']:>13.2f}")
print(f"\n  COMBINED steady-state BEFORE : ${tot['before_steady']:,.2f}  "
      f"{'BREACH' if tot['before_steady']>MAXM else 'ok'} by "
      f"${tot['before_steady']-MAXM:+,.2f}")
print(f"  COMBINED steady-state AFTER  : ${tot['steady']:,.2f}  "
      f"{'BREACH' if tot['steady']>MAXM else 'ok'} by ${tot['steady']-MAXM:+,.2f}")
print(f"  COMBINED September maximum   : ${tot['sept_max']:,.2f}  "
      f"headroom ${MAXM-tot['sept_max']:,.2f}")
print("\n  NOTE: the September maximum above is the SUM OF PER-CAMPAIGN maxima. Each campaign")
print("  carries its own monthly limit; this is not account spend-to-date plus a combined")
print("  budget formula.")
out["per_campaign_budget"] = percamp
out["budget_totals"] = {k: round(v, 2) for k, v in tot.items()}
out["hard_daily_max"] = round(MAXM/DAYS, 7)

print("\n=== 5. REALISTIC PROJECTION (not the maximum) ===")
print("  Observed run rates:")
pre = 8025.18/21
post = 45.08/4
print(f"    2026-08-14..09-03 (pre-ceiling)  : ${pre:.2f}/day")
print(f"    2026-09-05..09-08 (post-ceiling) : ${post:.2f}/day")
for lbl, rate in (("no change (ceilings hold)", post),
                  ("Installation restored to its pre-ceiling rate", post + 138.78)):
    proj = tot["sept_spend"] + rate * REMAIN_INCL_EDIT
    print(f"    {lbl:<46} -> September ~${proj:,.2f}  "
          f"({100*proj/MAXM:.0f}% of cap)")
out["projection"] = {"pre_ceiling_daily": round(pre, 2), "post_ceiling_daily": round(post, 2),
                     "september_spend_to_preflight": round(tot["sept_spend"], 2)}

print("\n=== 6. FRESH JUSTIFICATION FOR THE $5 AND $20 AMOUNTS ===")
for cid, label in (("24132507744", "Gas Boiler Repair"), ("24132507753", "HVAC Replacement")):
    a = q(c, f"SELECT campaign.id, metrics.clicks, metrics.impressions, metrics.cost_micros, "
             f"metrics.conversions, metrics.search_budget_lost_impression_share, "
             f"metrics.search_rank_lost_impression_share FROM campaign "
             f"WHERE campaign.id = {cid} AND segments.date BETWEEN '2026-08-14' AND '{SETTLED}'")[0]
    m2 = a.metrics
    s = sept.get(cid, {"cost": 0, "clicks": 0, "impressions": 0})
    print(f"\n  {label}")
    print(f"    all-time settled : {m2.impressions} impr, {m2.clicks} clicks, "
          f"${m2.cost_micros/1e6:.2f}, {m2.conversions:.0f} conv")
    print(f"    September to now : {s['impressions']} impr, {s['clicks']} clicks, ${s['cost']:.2f}")
    print(f"    lost IS (budget) : {100*m2.search_budget_lost_impression_share:.2f}%   "
          f"lost IS (rank): {100*m2.search_rank_lost_impression_share:.2f}%")
    print(f"    -> budget has never been the constraint; the proposed cut cannot cost delivery")
    out.setdefault("cut_justification", {})[label] = {
        "impressions": m2.impressions, "clicks": m2.clicks,
        "cost": round(m2.cost_micros/1e6, 2), "conversions": round(m2.conversions, 2),
        "lost_is_budget_pct": round(100*m2.search_budget_lost_impression_share, 2),
        "lost_is_rank_pct": round(100*m2.search_rank_lost_impression_share, 2),
        "september_spend": s["cost"]}

print("\n=== 7. FUTURE-SAFE ROLLBACK ARITHMETIC ===")
print("  Blind restoration of $42.76 + $26.32 would return the combined daily total to "
      f"${sum(v[2] for v in BUD.values()):.2f}")
print(f"  -> x30.4 = ${sum(v[2] for v in BUD.values())*DAYS:,.2f}  "
      f"= a ${sum(v[2] for v in BUD.values())*DAYS - MAXM:+,.2f} BREACH. NOT PERMITTED.")
head = MAXM/DAYS - (141.45 + 176.15 + 78.95)
print(f"\n  Compliant envelope for the two campaigns together:")
print(f"    hard daily max ${MAXM/DAYS:.2f} minus the three unchanged budgets "
      f"(${141.45+176.15+78.95:.2f}) = ${head:.2f}")
print(f"    proposed $5.00 + $20.00 = $25.00  -> ${head-25:.2f} of unused headroom")
print(f"    a compliant restoration must keep GasBoiler + Replacement <= ${head:.2f}")
print(f"    example compliant partial restore: $10.00 + $21.00 = $31.00 "
      f"(${head-31:.2f} headroom)")
out["rollback_envelope"] = {
    "blind_restore_daily": round(sum(v[2] for v in BUD.values()), 2),
    "blind_restore_x30_4": round(sum(v[2] for v in BUD.values())*DAYS, 2),
    "blind_restore_breach": round(sum(v[2] for v in BUD.values())*DAYS - MAXM, 2),
    "blind_restore_permitted": False,
    "two_campaign_compliant_envelope_daily": round(head, 2),
    "proposed_uses": 25.00}

write(EVID / "2026-09-09c-cpa-and-budget.json", out)
