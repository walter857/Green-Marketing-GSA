#!/usr/bin/env python3
"""When was the max-CPC ceiling actually set, and what do the numbers look like
BEFORE and AFTER that date? Split stats by ceiling regime - never average across one."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}

print("=== A. CHANGE HISTORY: when did a bidding / budget change land on the five? ===")
rows = []
try:
    for r in q(c, f"SELECT change_event.change_date_time, change_event.change_resource_type, "
                  f"change_event.client_type, change_event.user_email, "
                  f"change_event.changed_fields, change_event.resource_change_operation, "
                  f"campaign.id FROM change_event "
                  f"WHERE change_event.change_date_time >= '2026-08-11' "
                  f"AND campaign.id IN ({IN5}) LIMIT 10000"):
        ce = r.change_event
        f = list(ce.changed_fields.paths) if ce.changed_fields else []
        rows.append({"when": ce.change_date_time[:19],
                     "type": E(ce.change_resource_type),
                     "op": E(ce.resource_change_operation),
                     "camp": NAME.get(str(r.campaign.id), str(r.campaign.id)),
                     "client_type": E(ce.client_type), "user": ce.user_email, "fields": f})
except Exception as e:
    print(f"  change_event: {type(e).__name__}: {str(e)[:160]}")
bid = [x for x in rows if any("bid" in f.lower() or "target_spend" in f.lower()
                              or "bidding" in f.lower() for f in x["fields"])]
print(f"  total change_event rows on the five since 2026-08-11: {len(rows)}")
print(f"  of those, rows touching a bid / bidding / target_spend field: {len(bid)}")
for x in sorted(bid, key=lambda z: z["when"]):
    print(f"    {x['when']}  {x['camp']:<20}{x['op']:<10}{x['client_type']:<22}"
          f"{x['user']:<34}{x['fields']}")
out["bid_changes"] = bid
print("\n  all change types seen: "
      f"{sorted({(x['type'], x['op']) for x in rows})}")

print("\n=== B. AC REPAIR + HVAC REPAIR: cost, VALID clicks, INVALID clicks, per day ===")
print(f"  {'campaign':<18}{'date':<12}{'cost':>9}{'valid':>7}{'invalid':>9}{'raw':>6}"
      f"{'$/valid':>10}{'$/raw':>8}")
daily = {}
for cid in ["24132507741", "24132507750", "24132507747"]:
    for r in q(c, f"SELECT segments.date, metrics.cost_micros, metrics.clicks, "
                  f"metrics.invalid_clicks, metrics.impressions FROM campaign "
                  f"WHERE campaign.id = {cid} AND segments.date BETWEEN '2026-08-14' "
                  f"AND '2026-09-09' ORDER BY segments.date"):
        m = r.metrics
        if not (m.clicks or m.invalid_clicks or m.cost_micros):
            continue
        cost = m.cost_micros/1e6
        raw = m.clicks + m.invalid_clicks
        daily.setdefault(NAME[cid], []).append(
            {"date": r.segments.date, "cost": round(cost, 2), "valid": m.clicks,
             "invalid": m.invalid_clicks, "raw": raw,
             "per_valid": round(cost/m.clicks, 2) if m.clicks else None,
             "per_raw": round(cost/raw, 2) if raw else None})
        print(f"  {NAME[cid]:<18}{r.segments.date:<12}{cost:>9.2f}{m.clicks:>7}"
              f"{m.invalid_clicks:>9}{raw:>6}"
              f"{(f'{cost/m.clicks:.2f}' if m.clicks else '-'):>10}"
              f"{(f'{cost/raw:.2f}' if raw else '-'):>8}")
out["daily"] = daily

print("\n=== C. RECONCILIATION: which denominator respects the max-CPC ceiling? ===")
CEIL = {"AC Repair": 25.0, "HVAC Repair": 25.0, "HVAC Installation": 30.0,
        "HVAC Replacement": 0.0, "Gas Boiler Repair": 0.0}
print(f"  {'campaign':<20}{'cost':>10}{'valid':>7}{'invalid':>9}{'$/valid':>10}{'$/raw':>8}"
      f"{'ceiling':>9}   verdict")
rec = {}
for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.clicks, metrics.invalid_clicks "
              f"FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    m = r.metrics
    k = NAME[str(r.campaign.id)]
    cost, raw = m.cost_micros/1e6, m.clicks + m.invalid_clicks
    pv = cost/m.clicks if m.clicks else None
    pr = cost/raw if raw else None
    ce = CEIL[k]
    v = ("no spend" if not cost else
         "$/valid BREACHES ceiling; $/raw does not" if ce and pv and pv > ce and pr and pr <= ce
         else "$/valid within ceiling" if ce and pv and pv <= ce else "no ceiling set")
    rec[k] = {"cost": round(cost, 2), "valid": m.clicks, "invalid": m.invalid_clicks,
              "per_valid": round(pv, 2) if pv else None,
              "per_raw": round(pr, 2) if pr else None, "ceiling": ce, "verdict": v}
    print(f"  {k:<20}{cost:>10.2f}{m.clicks:>7}{m.invalid_clicks:>9}"
          f"{(f'{pv:.2f}' if pv else '-'):>10}{(f'{pr:.2f}' if pr else '-'):>8}"
          f"{ce:>9.2f}   {v}")
out["reconciliation"] = rec

print("\n=== D. GOOGLE'S OWN average_cpc FIELD vs cost/clicks ===")
for r in q(c, f"SELECT campaign.id, metrics.average_cpc, metrics.cost_micros, metrics.clicks "
              f"FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    m = r.metrics
    if not m.clicks: continue
    print(f"  {NAME[str(r.campaign.id)]:<20}Google average_cpc {m.average_cpc/1e6:>8.2f}   "
          f"my cost/clicks {m.cost_micros/1e6/m.clicks:>8.2f}")

write(EVID / "2026-09-10-ceiling-regime-and-invalid-clicks.json", out)
