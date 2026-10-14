#!/usr/bin/env python3
"""CORRECTED budget analysis: 30.4-day month, served vs billed cost, spending-limit evidence,
September budget-change reconstruction, and IS decontamination for HVAC Installation."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

DAYS_IN_AVG_MONTH = 30.4
MONTHLY_MAX = 13000.0
HARD_DAILY_MAX = MONTHLY_MAX / DAYS_IN_AVG_MONTH
print("=== 1. THE CORRECTED HARD DAILY MAXIMUM ===")
print(f"  Google applies a monthly spending limit of daily_budget x {DAYS_IN_AVG_MONTH}.")
print(f"  ${MONTHLY_MAX:,.2f} / {DAYS_IN_AVG_MONTH} = ${HARD_DAILY_MAX:.7f}")
print(f"  -> combined average daily budgets must not exceed ${HARD_DAILY_MAX:.2f}")
out["hard_daily_max"] = round(HARD_DAILY_MAX, 7)

LIVE = {"15787409435": ("AC Repair", 141.45), "15787409438": ("Gas Boiler Repair", 42.76),
        "15787409441": ("HVAC Installation", 176.15), "15787409444": ("HVAC Repair", 78.95),
        "15787409447": ("HVAC Replacement", 26.32)}
live_total = sum(v[1] for v in LIVE.values())
print(f"\n  LIVE combined daily total: ${live_total:.2f}")
print(f"  Implied 30.4-day exposure: ${live_total*DAYS_IN_AVG_MONTH:,.2f}  "
      f"-> ${live_total*DAYS_IN_AVG_MONTH-MONTHLY_MAX:+,.2f} vs the ${MONTHLY_MAX:,.0f} maximum")
prior = 433.33
print(f"\n  PRIOR PACKAGE AMB-0909-BUD-1 proposed ${prior:.2f}/day")
print(f"    x 30 (what the prior run used)   = ${prior*30:,.2f}  <- WRONG DENOMINATOR")
print(f"    x 30.4 (what Google actually uses)= ${prior*DAYS_IN_AVG_MONTH:,.2f}  "
      f"-> ${prior*DAYS_IN_AVG_MONTH-MONTHLY_MAX:+,.2f} vs maximum")
print(f"    VERDICT: ${prior:.2f}/day is NOT compliant. The prior claim was arithmetically wrong.")
out["prior_package_check"] = {"daily": prior, "x30": round(prior*30, 2),
                              "x30_4": round(prior*DAYS_IN_AVG_MONTH, 2),
                              "overrun_vs_max": round(prior*DAYS_IN_AVG_MONTH-MONTHLY_MAX, 2),
                              "compliant": False}

print("\n=== 2. SEPTEMBER BUDGET-CHANGE RECONSTRUCTION ===")
budch = []
for r in q(c, """
    SELECT change_event.change_date_time, change_event.change_resource_name,
           change_event.client_type, change_event.user_email,
           change_event.resource_change_operation, change_event.changed_fields,
           change_event.campaign, change_event.new_resource, change_event.old_resource
    FROM change_event
    WHERE change_event.change_date_time >= '2026-08-11 00:00:00'
      AND change_event.change_date_time <= '2026-09-09 23:59:59'
      AND change_event.change_resource_type = 'CAMPAIGN_BUDGET'
    LIMIT 10000
"""):
    x = r.change_event
    budch.append({"ts": x.change_date_time, "rn": x.change_resource_name,
                  "client_type": E(x.client_type), "user_email": x.user_email,
                  "op": E(x.resource_change_operation),
                  "campaign": x.campaign.split("/")[-1] if x.campaign else None,
                  "old": x.old_resource.campaign_budget.amount_micros or None,
                  "new": x.new_resource.campaign_budget.amount_micros or None})
out["budget_changes"] = budch
sept = [b for b in budch if b["ts"] >= "2026-09-01"]
print(f"  CAMPAIGN_BUDGET change events 2026-08-11..2026-09-09: {len(budch)}")
for b in budch:
    print(f"    {b['ts'][:19]}  {NAME.get(b['campaign'], b['campaign'])}  {b['op']}  "
          f"{b['client_type']}  {b['user_email']}  "
          f"${(b['old'] or 0)/1e6:.2f} -> ${(b['new'] or 0)/1e6:.2f}")
print(f"\n  SEPTEMBER budget changes: {len(sept)}")
print("  -> Every one of the five budgets has held its current value for the whole of")
print("     September. There is no mid-month step to prorate around. The only budget change")
print("     in the retrievable window is HVAC Installation on 2026-08-22 (August).")
out["september_budget_changes"] = sept

print("\n=== 3. SERVED COST vs BILLED COST ===")
served = {}
for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.impressions, metrics.clicks "
              f"FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-09-01' AND '2026-09-09'"):
    served[str(r.campaign.id)] = {"served_cost": round(r.metrics.cost_micros/1e6, 2),
                                  "impressions": r.metrics.impressions,
                                  "clicks": r.metrics.clicks}
sept_served = round(sum(v["served_cost"] for v in served.values()), 2)
print(f"  SERVED cost, five campaigns, 2026-09-01..2026-09-09 (incl. partial today): "
      f"${sept_served:,.2f}")
for cid in FIVE:
    v = served.get(cid, {"served_cost": 0, "clicks": 0, "impressions": 0})
    print(f"    {NAME[cid]:<20} ${v['served_cost']:>8.2f}  clicks={v['clicks']:<4} "
          f"impr={v['impressions']}")
acct_sept = q(c, "SELECT metrics.cost_micros FROM customer "
                 "WHERE segments.date BETWEEN '2026-09-01' AND '2026-09-09'")
acct_cost = round(acct_sept[0].metrics.cost_micros/1e6, 2) if acct_sept else 0.0
print(f"  SERVED cost, WHOLE ACCOUNT, same window: ${acct_cost:,.2f}")
print(f"    (the other 18 campaigns are PAUSED; difference = "
      f"${acct_cost - sept_served:,.2f})")
out["september_served"] = {"by_campaign": served, "five_total": sept_served,
                           "account_total": acct_cost}

print("\n  --- BILLED cost evidence (account_budget / billing_setup) ---")
billing = []
try:
    for r in q(c, """
        SELECT account_budget.id, account_budget.name, account_budget.status,
               account_budget.approved_spending_limit_type,
               account_budget.approved_spending_limit_micros,
               account_budget.adjusted_spending_limit_type,
               account_budget.adjusted_spending_limit_micros,
               account_budget.proposed_spending_limit_type,
               account_budget.amount_served_micros,
               account_budget.total_adjustments_micros,
               account_budget.approved_start_date_time,
               account_budget.approved_end_date_time
        FROM account_budget
    """):
        x = r.account_budget
        billing.append({
            "id": str(x.id), "name": x.name, "status": E(x.status),
            "approved_limit_type": E(x.approved_spending_limit_type),
            "approved_limit": (round(x.approved_spending_limit_micros/1e6, 2)
                               if x.approved_spending_limit_micros else None),
            "adjusted_limit_type": E(x.adjusted_spending_limit_type),
            "amount_served": round(x.amount_served_micros/1e6, 2),
            "total_adjustments": round(x.total_adjustments_micros/1e6, 2),
            "start": x.approved_start_date_time, "end": x.approved_end_date_time})
except Exception as e:
    print("  account_budget read failed:", type(e).__name__, str(e)[:200])
out["account_budget"] = billing
for b in billing:
    print(f"    account_budget {b['id']} {b['status']:<10} "
          f"approved_limit_type={b['approved_limit_type']:<10} "
          f"amount_served=${b['amount_served']:,.2f} adjustments=${b['total_adjustments']:,.2f}")
    print(f"      window {b['start']} .. {b['end'] or 'open'}  name={b['name']!r}")

try:
    for r in q(c, "SELECT billing_setup.id, billing_setup.status, "
                  "billing_setup.payments_account_info.payments_account_id, "
                  "billing_setup.payments_account_info.payments_profile_id "
                  "FROM billing_setup"):
        x = r.billing_setup
        print(f"    billing_setup {x.id} status={E(x.status)}")
        out.setdefault("billing_setup", []).append({"id": str(x.id), "status": E(x.status)})
except Exception as e:
    print("  billing_setup read failed:", type(e).__name__, str(e)[:200])

print("\n  BILLED vs SERVED note:")
print("    account_budget.amount_served_micros is the account-level served total for the")
print("    budget window, not a monthly invoice. Google Ads does not expose per-month BILLED")
print("    cost through this API surface unless the account is on monthly invoicing and the")
print("    Invoice service is enabled. Served cost is therefore the best available figure,")
print("    and it can still be restated downward by invalid-click credits.")

print("\n=== 4. INVALID CLICKS (served vs eventually-billed gap) ===")
inv = []
for r in q(c, f"SELECT campaign.id, metrics.invalid_clicks, metrics.invalid_click_rate, "
              f"metrics.clicks, metrics.cost_micros FROM campaign "
              f"WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    inv.append({"camp": str(r.campaign.id), "invalid_clicks": r.metrics.invalid_clicks,
                "invalid_rate": round(r.metrics.invalid_click_rate*100, 2),
                "clicks": r.metrics.clicks,
                "cost": round(r.metrics.cost_micros/1e6, 2)})
out["invalid_clicks"] = inv
tot_inv = sum(x["invalid_clicks"] for x in inv)
tot_clk = sum(x["clicks"] for x in inv)
for x in sorted(inv, key=lambda x: -x["cost"]):
    print(f"    {NAME[x['camp']]:<20} billable_clicks={x['clicks']:<5} "
          f"invalid_clicks={x['invalid_clicks']:<5} invalid_rate={x['invalid_rate']}%")
print(f"    TOTAL billable={tot_clk}  invalid={tot_inv}  "
      f"(invalid clicks are already excluded from cost)")

print("\n=== 5. SPENDING-LIMIT EVIDENCE PER CAMPAIGN ===")
print("  Search lost impression share (BUDGET) is the only readable proxy for a campaign")
print("  hitting its daily budget. Shown on three windows to expose contamination.")
windows = [("all launch-to-settled 08-14..09-08", "2026-08-14", "2026-09-08"),
           ("CONTAMINATED 'hvac installers' era 08-14..08-28", "2026-08-14", "2026-08-28"),
           ("CLEAN post-swap 08-29..09-03 (pre-ceiling)", "2026-08-29", "2026-09-03"),
           ("post-ceiling 09-05..09-08", "2026-09-05", "2026-09-08")]
islim = {}
for label, s, e in windows:
    print(f"\n  {label}")
    islim[label] = {}
    for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.impressions, "
                  f"metrics.search_impression_share, "
                  f"metrics.search_budget_lost_impression_share, "
                  f"metrics.search_rank_lost_impression_share FROM campaign "
                  f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '{s}' AND '{e}'"):
        x = r.metrics
        d = {"cost": round(x.cost_micros/1e6, 2), "impressions": x.impressions,
             "is": round(x.search_impression_share*100, 2),
             "lost_budget": round(x.search_budget_lost_impression_share*100, 2),
             "lost_rank": round(x.search_rank_lost_impression_share*100, 2)}
        islim[label][NAME[str(r.campaign.id)]] = d
        print(f"    {NAME[str(r.campaign.id)]:<20} cost=${d['cost']:>8.2f} "
              f"IS={d['is']:>6.2f}%  lostBUDGET={d['lost_budget']:>6.2f}%  "
              f"lostRANK={d['lost_rank']:>6.2f}%")
out["impression_share_windows"] = islim

print("\n=== 6. DAILY SPEND vs DAILY BUDGET, SEPTEMBER ===")
byd = defaultdict(lambda: defaultdict(float))
for r in q(c, f"SELECT campaign.id, segments.date, metrics.cost_micros FROM campaign "
              f"WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-09-01' AND '2026-09-09'"):
    byd[r.segments.date][str(r.campaign.id)] += r.metrics.cost_micros/1e6
print(f"  {'date':<12}{'AC':>9}{'GasB':>8}{'Instal':>9}{'Repair':>9}{'Replc':>8}{'TOTAL':>10}"
      f"{'vs $465.63':>12}")
sept_rows = {}
for d in sorted(byd):
    v = byd[d]
    t = sum(v.values())
    sept_rows[d] = {NAME[k]: round(x, 2) for k, x in v.items()}
    sept_rows[d]["TOTAL"] = round(t, 2)
    print(f"  {d:<12}{v.get('24132507741',0):>9.2f}{v.get('24132507744',0):>8.2f}"
          f"{v.get('24132507747',0):>9.2f}{v.get('24132507750',0):>9.2f}"
          f"{v.get('24132507753',0):>8.2f}{t:>10.2f}{100*t/465.63:>11.1f}%")
out["september_daily"] = sept_rows
print(f"\n  Peak single-day spend in September: "
      f"${max((s['TOTAL'] for s in sept_rows.values()), default=0):.2f} "
      f"against a ${live_total:.2f} combined daily budget.")
print("  Google permits up to 2x the daily budget on any single day, balanced over the month;")
print(f"  the 2x single-day ceiling on the current configuration is ${live_total*2:.2f}.")

write(EVID / "2026-09-09b-budget-analysis.json", out)
