#!/usr/bin/env python3
"""Corroborate the clicks/cost contradiction against raw click_view records,
and find when the max-CPC ceiling was actually set."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
DATES = ([f"2026-08-{x:02d}" for x in range(14, 32)] +
         [f"2026-09-{x:02d}" for x in range(1, 10)])

print("=== A. click_view ROW COUNT vs metrics.clicks vs metrics.invalid_clicks (AC Repair) ===")
cv = Counter()
for d in DATES:
    for r in q(c, f"SELECT campaign.id, segments.date FROM click_view "
                  f"WHERE segments.date = '{d}' AND campaign.id = 24132507741"):
        cv[r.segments.date] += 1
met = {}
for r in q(c, "SELECT segments.date, metrics.clicks, metrics.invalid_clicks, metrics.cost_micros "
              "FROM campaign WHERE campaign.id = 24132507741 "
              "AND segments.date BETWEEN '2026-08-14' AND '2026-09-09' ORDER BY segments.date"):
    met[r.segments.date] = (r.metrics.clicks, r.metrics.invalid_clicks,
                            r.metrics.cost_micros/1e6)
print(f"  {'date':<12}{'click_view':>11}{'valid':>7}{'invalid':>9}{'valid+inv':>11}"
      f"{'cost':>9}   click_view matches")
tot_cv = tot_v = tot_i = 0
recon = []
for d in sorted(set(cv) | set(met)):
    n = cv.get(d, 0); v, i, cost = met.get(d, (0, 0, 0.0))
    tot_cv += n; tot_v += v; tot_i += i
    match = "valid+invalid" if n == v + i else ("valid only" if n == v else "neither")
    recon.append({"date": d, "click_view_rows": n, "valid": v, "invalid": i,
                  "cost": round(cost, 2), "matches": match})
    print(f"  {d:<12}{n:>11}{v:>7}{i:>9}{v+i:>11}{cost:>9.2f}   {match}")
print(f"  {'TOTAL':<12}{tot_cv:>11}{tot_v:>7}{tot_i:>9}{tot_v+tot_i:>11}")
out["ac_repair_click_reconciliation"] = recon
out["ac_repair_totals"] = {"click_view_rows": tot_cv, "valid": tot_v, "invalid": tot_i}

print("\n=== B. DAILY COST vs DAILY BUDGET (was cost pinned to the budget cap?) ===")
b = {}
for r in q(c, f"SELECT campaign.id, campaign_budget.amount_micros FROM campaign "
              f"WHERE campaign.id IN ({IN5})"):
    b[str(r.campaign.id)] = r.campaign_budget.amount_micros/1e6
print(f"  current daily budgets: { {NAME[k]: v for k, v in b.items()} }")
print(f"  {'campaign':<18}{'date':<12}{'cost':>9}{'cost/budget':>13}")
for cid in ["24132507741", "24132507747"]:
    for r in q(c, f"SELECT segments.date, metrics.cost_micros, campaign_budget.amount_micros "
                  f"FROM campaign WHERE campaign.id = {cid} "
                  f"AND segments.date BETWEEN '2026-08-18' AND '2026-08-31' "
                  f"ORDER BY segments.date"):
        cost = r.metrics.cost_micros/1e6
        bud = r.campaign_budget.amount_micros/1e6
        if not cost:
            continue
        print(f"  {NAME[cid]:<18}{r.segments.date:<12}{cost:>9.2f}"
              f"{(cost/bud if bud else 0):>12.2f}x   (budget ${bud:.2f} as of today)")

print("\n=== C. WHEN WAS THE MAX-CPC CEILING SET? ===")
rows = []
try:
    for r in q(c, f"SELECT change_event.change_date_time, change_event.change_resource_type, "
                  f"change_event.client_type, change_event.user_email, "
                  f"change_event.changed_fields, change_event.resource_change_operation, "
                  f"campaign.id FROM change_event "
                  f"WHERE change_event.change_date_time >= '2026-08-11 00:00:00' "
                  f"AND change_event.change_date_time <= '2026-09-10 23:59:59' "
                  f"AND campaign.id IN ({IN5}) "
                  f"ORDER BY change_event.change_date_time LIMIT 10000"):
        ce = r.change_event
        rows.append({"when": ce.change_date_time[:19], "type": E(ce.change_resource_type),
                     "op": E(ce.resource_change_operation),
                     "camp": NAME.get(str(r.campaign.id), str(r.campaign.id)),
                     "client_type": E(ce.client_type), "user": ce.user_email,
                     "fields": list(ce.changed_fields.paths) if ce.changed_fields else []})
except Exception as e:
    print(f"  change_event: {type(e).__name__}: {str(e)[:200]}")
print(f"  change_event rows on the five, 2026-08-11..2026-09-10: {len(rows)}")
for x in rows:
    print(f"    {x['when']}  {x['camp']:<20}{x['type']:<20}{x['op']:<8}"
          f"{x['client_type']:<20}{x['user']:<32}{x['fields']}")
out["change_events"] = rows

print("\n=== D. INVALID-CLICK RATE ACROSS THE WHOLE ACCOUNT, BY MONTH ===")
for r in q(c, "SELECT segments.month, metrics.clicks, metrics.invalid_clicks, "
              "metrics.invalid_click_rate, metrics.cost_micros FROM customer "
              "WHERE segments.date BETWEEN '2026-06-01' AND '2026-09-09' "
              "ORDER BY segments.month"):
    m = r.metrics
    print(f"  {r.segments.month}  valid {m.clicks:>6}  invalid {m.invalid_clicks:>6}  "
          f"rate {m.invalid_click_rate*100:>5.1f}%  cost ${m.cost_micros/1e6:>9.2f}  "
          f"$/valid {(m.cost_micros/1e6/m.clicks if m.clicks else 0):>7.2f}")

write(EVID / "2026-09-10-click-reconciliation.json", out)
