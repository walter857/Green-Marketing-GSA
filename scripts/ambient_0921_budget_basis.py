#!/usr/bin/env python3
"""Ambient | 2026-09-21 | Budget + ceiling basis, refreshed for the new account date.

READ-ONLY. EXTERNAL WRITES: 0.

The prior budget draft was built on 2026-09-20. The account date has rolled to
2026-09-21, which changes days-remaining and therefore every pace number, so the
whole basis is recomputed rather than adjusted.

Also reads the CPC bid ceiling on every campaign that will carry heating traffic,
because a budget increase buys nothing on a campaign whose ceiling sits below the
clearing price for its theme.
"""
from __future__ import annotations
import sys, json, datetime, calendar
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21"
CAP_MONTH = 10000.00
CAP_DAY = 328.94
WORKING_TARGET = 325.00

# Proposed end-state allocation. Every number is justified in the plan file.
PROPOSED = {
    "24132507747": ("HVAC Installation", 95.0, 55.0),
    "24132507750": ("HVAC Repair", 70.0, 55.0),
    "24132507741": ("AC Repair", 45.0, 25.0),
    "24132507753": ("HVAC Replacement", 15.0, 12.0),
    "24132507744": ("Gas Boiler + Boiler Repair", 12.0, 38.0),
    "24257819463": ("Heating Repair", 55.0, 55.0),
    "24257819466": ("Heating Installation", 35.0, 55.0),
    "NEW:HEATPUMP": ("Heat Pump & Geothermal (new)", 0.0, 18.0),
    "NEW:TANKLESS": ("Tankless Water Heaters (new)", 0.0, 12.0),
}


def main():
    c = client()
    identity_gate(c, verbose=False)
    now = datetime.datetime.now(TZ)
    first = now.replace(day=1).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    dim = calendar.monthrange(now.year, now.month)[1]
    out = {"generated_local": now.isoformat(), "stamp": STAMP, "read_only": True,
           "external_writes": 0, "account_today": today}
    print(f"account local date: {today}  (days in month {dim})")

    # ------------------------------------------------------- current state
    cur = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     campaign.bidding_strategy_type,
                     campaign.target_spend.cpc_bid_ceiling_micros,
                     campaign.maximize_conversions.target_cpa_micros,
                     campaign_budget.id, campaign_budget.amount_micros,
                     campaign_budget.explicitly_shared,
                     campaign_budget.reference_count
                     FROM campaign WHERE campaign.status != 'REMOVED'"""):
        x = r.campaign
        cur[str(x.id)] = {
            "name": x.name, "status": E(x.status),
            "bidding": E(x.bidding_strategy_type),
            "ceiling": round(x.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
            "budget_id": str(r.campaign_budget.id),
            "daily": round(r.campaign_budget.amount_micros / 1e6, 2),
            "shared": r.campaign_budget.explicitly_shared,
            "refs": r.campaign_budget.reference_count}
    out["campaigns_now"] = cur

    print("\n=== CAMPAIGNS THAT WILL CARRY THE STRATEGY ===")
    print(f"{'id':14s} {'status':8s} {'daily':>8s} {'ceil':>7s}  {'bidding':22s} name")
    for cid in PROPOSED:
        if cid.startswith("NEW:"):
            continue
        v = cur[cid]
        print(f"{cid:14s} {v['status']:8s} {v['daily']:8.2f} {v['ceiling']:7.2f}  "
              f"{v['bidding']:22s} {v['name'][:44]}")

    en_now = round(sum(v["daily"] for v in cur.values() if v["status"] == "ENABLED"), 2)
    print(f"\nENABLED daily total now: ${en_now:.2f}")
    out["enabled_daily_total_now"] = en_now

    # ------------------------------------------------------------ September
    byday, tot = {}, 0.0
    for r in q(c, f"""SELECT campaign.id, segments.date, metrics.cost_micros
                      FROM campaign
                      WHERE segments.date BETWEEN '{first}' AND '{today}'"""):
        v = r.metrics.cost_micros / 1e6
        tot += v
        byday[r.segments.date] = byday.get(r.segments.date, 0.0) + v
    # Denominator must be CALENDAR days elapsed, not "days Google returned a row
    # for". A day on which nothing delivered often comes back with no row at all,
    # and dividing by the row count silently drops those zeros and overstates the
    # daily rate. Build the full date axis and fill the gaps with 0.00.
    d0 = now.replace(day=1).date()
    dlast = (now - datetime.timedelta(days=1)).date()
    axis = [(d0 + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((dlast - d0).days + 1)]
    settled = {d: round(byday.get(d, 0.0), 2) for d in axis}
    n_set = len(settled)                      # calendar days, zeros included
    n_delivered = sum(1 for v in settled.values() if v > 0)
    set_cost = round(sum(settled.values()), 2)
    avg_set = round(set_cost / n_set, 2) if n_set else 0.0
    last7 = axis[-7:]
    avg7 = round(sum(settled[d] for d in last7) / len(last7), 2) if last7 else 0.0
    print("\n   September daily spend (calendar axis, zeros included):")
    for d in axis:
        print(f"      {d}  ${settled[d]:8.2f}")
    print(f"      {today}  ${byday.get(today, 0.0):8.2f}  <- PARTIAL (today)")

    days_left = dim - now.day + 1
    remaining = round(CAP_MONTH - tot, 2)
    reserve = round(remaining * 0.10, 2)
    safe_pace = round((remaining - reserve) / days_left, 2) if days_left else 0.0

    print(f"\n=== SEPTEMBER {first}..{today} ===")
    print(f"   MTD spend (incl. partial today)   ${tot:,.2f}")
    print(f"   settled CALENDAR days             {n_set} -> ${set_cost:,.2f}")
    print(f"   of those, days with any delivery  {n_delivered}")
    print(f"   settled daily average (calendar)  ${avg_set:,.2f}")
    print(f"   last-7 calendar daily average     ${avg7:,.2f}")
    print(f"   days remaining incl. today        {days_left}")
    print(f"   remaining allowance to $10,000    ${remaining:,.2f}")
    print(f"   conversion-lag/overdelivery 10%   ${reserve:,.2f}")
    print(f"   MAX SAFE September daily pace     ${safe_pace:,.2f}")
    print(f"   steady-state ceiling  $10,000/30.4 = ${CAP_MONTH/30.4:,.2f}/day")

    # --------------------------------------- projections under the proposal
    prop_total = round(sum(v[2] for v in PROPOSED.values()), 2)
    # Worst case: every enabled budget spends in full, every remaining day.
    worst = round(tot + prop_total * days_left, 2)
    # Evidence case: delivery continues at the observed settled rate. Heating adds
    # demand, so the observed rate is scaled by the share of budget that is new.
    evidence = round(tot + avg7 * days_left, 2)
    print(f"\n=== PROPOSED ALLOCATION ===")
    tot_new = 0.0
    for cid, (nm, frm, to) in PROPOSED.items():
        tot_new += to
        d = to - frm
        print(f"   {nm[:34]:34s} ${frm:6.2f} -> ${to:6.2f}   "
              f"{'+' if d > 0 else ''}{d:.2f}")
    print(f"   {'TOTAL':34s} {'':9s}    ${tot_new:.2f}")
    print(f"\n   daily cap        ${CAP_DAY:.2f}   headroom ${CAP_DAY - tot_new:.2f}")
    print(f"   working target   ${WORKING_TARGET:.2f}   within target: "
          f"{tot_new <= WORKING_TARGET}")
    print(f"   monthly equivalent (x30.4) ${tot_new * 30.4:,.2f}  under $10,000: "
          f"{tot_new * 30.4 <= CAP_MONTH}")
    print(f"\n   September worst case (every budget fully spent every day): "
          f"${worst:,.2f}  under cap: {worst <= CAP_MONTH}")
    print(f"   September worst case + reserve: ${worst + reserve:,.2f}")
    print(f"   September evidence case (last-7 delivery rate): ${evidence:,.2f}")

    out["september"] = {
        "mtd_incl_partial_today": round(tot, 2),
        "settled_calendar_days": n_set, "days_with_delivery": n_delivered,
        "daily_spend_calendar_axis": settled,
        "settled_cost": set_cost, "settled_daily_avg": avg_set,
        "last7_daily_avg": avg7, "days_left_incl_today": days_left,
        "remaining_allowance": remaining, "reserve_10pct": reserve,
        "max_safe_daily_pace": safe_pace,
        "steady_state_daily_ceiling": round(CAP_MONTH / 30.4, 2)}
    out["proposed_allocation"] = {k: {"name": v[0], "from": v[1], "to": v[2]}
                                  for k, v in PROPOSED.items()}
    out["proposed_total_daily"] = round(tot_new, 2)
    out["proposed_monthly_equivalent"] = round(tot_new * 30.4, 2)
    out["september_projection_worst_case"] = worst
    out["september_projection_worst_plus_reserve"] = round(worst + reserve, 2)
    out["september_projection_evidence_case"] = evidence
    out["within_daily_cap"] = tot_new <= CAP_DAY
    out["within_working_target"] = tot_new <= WORKING_TARGET
    out["september_under_10k_worst_case"] = worst + reserve <= CAP_MONTH

    # ------------------------------------------ unattached budgets for reuse
    print("\n=== UNATTACHED BUDGETS (reference_count = 0) ===")
    free = []
    for r in q(c, """SELECT campaign_budget.id, campaign_budget.name,
                     campaign_budget.amount_micros, campaign_budget.reference_count,
                     campaign_budget.explicitly_shared, campaign_budget.status
                     FROM campaign_budget
                     WHERE campaign_budget.status != 'REMOVED'"""):
        b = r.campaign_budget
        if b.reference_count == 0:
            free.append({"id": str(b.id), "name": b.name,
                         "amount": round(b.amount_micros / 1e6, 2),
                         "shared": b.explicitly_shared})
    for b in free[:12]:
        print(f"   {b['id']}  ${b['amount']:8.2f}  shared={b['shared']}  {b['name'][:44]}")
    print(f"   total unattached: {len(free)}")
    out["unattached_budgets"] = free

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"budget-basis-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
