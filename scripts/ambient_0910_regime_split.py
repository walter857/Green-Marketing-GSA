#!/usr/bin/env python3
"""The max-CPC ceilings were set 2026-09-04 16:56 (GOOGLE_ADS_WEB_CLIENT).
Never average across a ceiling change. Split every number at that boundary."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "ceiling_set_at": "2026-09-04 16:56 America/New_York, GOOGLE_ADS_WEB_CLIENT, "
                         "user access@greenmarketingfl.com",
       "ceilings_now": {"AC Repair": 25.0, "HVAC Repair": 25.0, "HVAC Installation": 30.0,
                        "HVAC Replacement": "NONE - still uncapped",
                        "Gas Boiler Repair": "NONE - still uncapped"}}
REG = [("UNCAPPED", "2026-08-14", "2026-09-03"),
       ("MIXED DAY", "2026-09-04", "2026-09-04"),
       ("CAPPED", "2026-09-05", "2026-09-09")]

print("=== PER-REGIME: what did a valid click actually cost? ===")
res = {}
for label, a, b in REG:
    print(f"\n--- {label}  {a} .. {b} ---")
    print(f"  {'campaign':<20}{'cost':>10}{'valid':>7}{'invalid':>9}{'inv%':>7}"
          f"{'$/valid':>10}{'impr':>7}{'CTR':>7}")
    tv = ti = 0; tc = 0.0
    per = {}
    for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.clicks, "
                  f"metrics.invalid_clicks, metrics.impressions FROM campaign "
                  f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '{a}' AND '{b}'"):
        m = r.metrics
        k = NAME[str(r.campaign.id)]
        cost = m.cost_micros/1e6; raw = m.clicks + m.invalid_clicks
        if not (cost or raw or m.impressions):
            continue
        tv += m.clicks; ti += m.invalid_clicks; tc += cost
        per[k] = {"cost": round(cost, 2), "valid": m.clicks, "invalid": m.invalid_clicks,
                  "impr": m.impressions,
                  "per_valid": round(cost/m.clicks, 2) if m.clicks else None}
        print(f"  {k:<20}{cost:>10.2f}{m.clicks:>7}{m.invalid_clicks:>9}"
              f"{(100*m.invalid_clicks/raw if raw else 0):>6.1f}%"
              f"{(f'{cost/m.clicks:.2f}' if m.clicks else '-'):>10}{m.impressions:>7}"
              f"{(100*m.clicks/m.impressions if m.impressions else 0):>6.2f}%")
    print(f"  {'TOTAL':<20}{tc:>10.2f}{tv:>7}{ti:>9}"
          f"{(100*ti/(tv+ti) if tv+ti else 0):>6.1f}%"
          f"{(f'{tc/tv:.2f}' if tv else '-'):>10}")
    days = (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days + 1
    print(f"  days {days}   spend/day ${tc/days:,.2f}   implied monthly ${tc/days*30.4:,.2f}")
    res[label] = {"window": [a, b], "days": days, "cost": round(tc, 2), "valid": tv,
                  "invalid": ti, "per_campaign": per,
                  "spend_per_day": round(tc/days, 2),
                  "implied_monthly": round(tc/days*30.4, 2),
                  "cost_per_valid_click": round(tc/tv, 2) if tv else None}
out["regimes"] = res

print("\n\n=== DID THE CEILING WORK? cost per valid click, before vs after ===")
u, cp = res["UNCAPPED"], res["CAPPED"]
print(f"  UNCAPPED  {u['window'][0]}..{u['window'][1]}  ${u['cost']:>9,.2f}  "
      f"{u['valid']:>4} valid clicks  ${u['cost_per_valid_click']}/valid click")
print(f"  CAPPED    {cp['window'][0]}..{cp['window'][1]}  ${cp['cost']:>9,.2f}  "
      f"{cp['valid']:>4} valid clicks  ${cp['cost_per_valid_click']}/valid click")
if u["cost_per_valid_click"] and cp["cost_per_valid_click"]:
    print(f"  change in cost per valid click: "
          f"{100*(cp['cost_per_valid_click']/u['cost_per_valid_click']-1):+.1f}%")
print(f"  daily spend fell from ${u['spend_per_day']:,.2f}/day to ${cp['spend_per_day']:,.2f}/day "
      f"({100*(cp['spend_per_day']/u['spend_per_day']-1):+.1f}%)")
print("  NOTE: the capped window is 5 settled days. It is directionally consistent with the")
print("  ceiling binding, but it is far too short to call the effect established.")

print("\n\n=== WHICH REGIME DID EACH PAID LEAD COME FROM? ===")
wc = json.load(open(EVID / "2026-09-10-whatconverts-lead-analysis.json", encoding="utf-8"))
for r in wc["paid_attributable_rows"]:
    reg = "UNCAPPED" if r["click_date"] <= "2026-09-03" else (
        "MIXED DAY" if r["click_date"] == "2026-09-04" else "CAPPED")
    print(f"  {r['campaign']:<20}click {r['click_date']}  {reg:<10}"
          f"{str(r['lead_type']):<13}{str(r['lead_status']):<9}"
          f"uniqQL={r['unique_qualified']}")
byreg = Counter("UNCAPPED" if r["click_date"] <= "2026-09-03" else
                ("MIXED DAY" if r["click_date"] == "2026-09-04" else "CAPPED")
                for r in wc["paid_attributable_rows"] if r["unique_qualified"])
print(f"\n  unique qualified leads by regime: {dict(byreg)}")
print(f"  -> every measured unique qualified lead came from a click bought BEFORE the")
print(f"     ceiling existed. The capped regime has produced {byreg.get('CAPPED',0)} so far.")
out["leads_by_regime"] = dict(byreg)

print("\n\n=== THE TWO CAMPAIGNS THAT ARE STILL UNCAPPED ===")
for r in q(c, f"SELECT campaign.id, campaign.name, campaign.status, "
              f"campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign_budget.amount_micros FROM campaign WHERE campaign.id IN ({IN5})"):
    ceil = r.campaign.target_spend.cpc_bid_ceiling_micros
    print(f"  {NAME[str(r.campaign.id)]:<20}{E(r.campaign.status):<10}"
          f"budget ${r.campaign_budget.amount_micros/1e6:>7.2f}/day   "
          f"ceiling {('$%.2f' % (ceil/1e6)) if ceil else 'NONE - UNCAPPED'}")
write(EVID / "2026-09-10-regime-split.json", out)
