#!/usr/bin/env python3
"""Rule out the innocent explanation: was the max-CPC ceiling raised and lowered
during the window? change_event only reaches back 30 days, so start at the limit."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
rows = []
for start in ["2026-08-12", "2026-08-13", "2026-08-14"]:
    try:
        rows = []
        for r in q(c, f"SELECT change_event.change_date_time, change_event.change_resource_type, "
                      f"change_event.client_type, change_event.user_email, "
                      f"change_event.changed_fields, change_event.resource_change_operation, "
                      f"change_event.old_resource, change_event.new_resource, campaign.id "
                      f"FROM change_event "
                      f"WHERE change_event.change_date_time >= '{start} 00:00:00' "
                      f"AND change_event.change_date_time <= '2026-09-10 23:59:59' "
                      f"AND campaign.id IN ({IN5}) "
                      f"ORDER BY change_event.change_date_time LIMIT 10000"):
            ce = r.change_event
            rows.append({"when": ce.change_date_time[:19], "type": E(ce.change_resource_type),
                         "op": E(ce.resource_change_operation),
                         "camp": NAME.get(str(r.campaign.id), str(r.campaign.id)),
                         "client_type": E(ce.client_type), "user": ce.user_email,
                         "fields": list(ce.changed_fields.paths) if ce.changed_fields else [],
                         "old": str(ce.old_resource)[:400], "new": str(ce.new_resource)[:400]})
        print(f"=== change_event from {start}: {len(rows)} rows ===")
        break
    except Exception as e:
        print(f"  start {start}: {str(e)[:80]}")

for x in rows:
    print(f"\n  {x['when']}  {x['camp']}  {x['type']} {x['op']}")
    print(f"    by client_type={x['client_type']}  user={x['user']}")
    print(f"    fields: {x['fields']}")
    if any("bid" in f.lower() or "target_spend" in f.lower() or "amount" in f.lower()
           for f in x["fields"]):
        print(f"    OLD: {x['old']}")
        print(f"    NEW: {x['new']}")
out["change_events"] = rows

bidrows = [x for x in rows if any("bid" in f.lower() or "target_spend" in f.lower()
                                  for f in x["fields"])]
print(f"\n=== ROWS TOUCHING A BID CEILING: {len(bidrows)} ===")
print("  -> if zero, the $25.00 / $30.00 ceilings were NOT changed inside the 30-day window,")
print("     so a mid-window ceiling change cannot explain a $106.37 reported average CPC.")

print("\n=== ACCOUNT-WIDE INVALID CLICKS BY DAY, LAST 30 DAYS ===")
print(f"  {'date':<12}{'valid':>7}{'invalid':>9}{'rate':>8}{'cost':>10}{'$/valid':>9}")
tot = {"v": 0, "i": 0, "c": 0.0}
for r in q(c, "SELECT segments.date, metrics.clicks, metrics.invalid_clicks, "
              "metrics.invalid_click_rate, metrics.cost_micros FROM customer "
              "WHERE segments.date BETWEEN '2026-08-11' AND '2026-09-09' ORDER BY segments.date"):
    m = r.metrics
    if not (m.clicks or m.invalid_clicks or m.cost_micros):
        continue
    tot["v"] += m.clicks; tot["i"] += m.invalid_clicks; tot["c"] += m.cost_micros/1e6
    print(f"  {r.segments.date:<12}{m.clicks:>7}{m.invalid_clicks:>9}"
          f"{m.invalid_click_rate*100:>7.1f}%{m.cost_micros/1e6:>10.2f}"
          f"{(m.cost_micros/1e6/m.clicks if m.clicks else 0):>9.2f}")
print(f"  {'TOTAL':<12}{tot['v']:>7}{tot['i']:>9}"
      f"{100*tot['i']/(tot['v']+tot['i']):>7.1f}%{tot['c']:>10.2f}"
      f"{(tot['c']/tot['v'] if tot['v'] else 0):>9.2f}")
out["account_daily"] = tot
write(EVID / "2026-09-10-change-history-and-invalid-daily.json", out)
