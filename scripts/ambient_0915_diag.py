#!/usr/bin/env python3
"""Ambient | 2026-09-15 | converting-click price band, invalid clicks, device, geo, auction."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
c = client(); identity_gate(c, verbose=False)
NAMES = {"24132507741": "AC Repair", "24132507744": "Gas Boiler Repair",
         "24132507747": "HVAC Installation", "24132507750": "HVAC Repair",
         "24132507753": "HVAC Replacement"}

print("=== 1. CONVERTING vs NON-CONVERTING CLICK PRICE, settled Sept + August ===")
for lbl, lo, hi in (("SEP_SETTLED", "2026-09-01", "2026-09-14"),
                    ("AUG", "2026-08-01", "2026-08-31")):
    rows = q(c, f"""
        SELECT campaign.id, search_term_view.search_term,
               metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM search_term_view WHERE campaign.id IN ({IN5})
          AND segments.date BETWEEN '{lo}' AND '{hi}'
    """)
    agg = defaultdict(lambda: {"clk": 0, "cost": 0.0, "conv": 0.0})
    for r in rows:
        k = (str(r.campaign.id), r.search_term_view.search_term)
        agg[k]["clk"] += r.metrics.clicks
        agg[k]["cost"] += r.metrics.cost_micros / 1e6
        agg[k]["conv"] += r.metrics.conversions
    convd = {k: v for k, v in agg.items() if v["conv"] > 0 and v["clk"] > 0}
    nonc = {k: v for k, v in agg.items() if v["conv"] == 0 and v["clk"] > 0}
    cc = sum(v["clk"] for v in convd.values()); ccost = sum(v["cost"] for v in convd.values())
    nc = sum(v["clk"] for v in nonc.values()); ncost = sum(v["cost"] for v in nonc.values())
    print(f"\n  --- {lbl} {lo}..{hi} ---")
    print(f"    CONVERTING terms: {len(convd)} | clicks {cc} | cost ${ccost:.2f} | "
          f"avg CPC ${ccost/cc if cc else 0:.2f} | conversions {sum(v['conv'] for v in convd.values()):.1f}")
    print(f"    NON-CONVERTING  : {len(nonc)} | clicks {nc} | cost ${ncost:.2f} | "
          f"avg CPC ${ncost/nc if nc else 0:.2f}")
    print("    converting terms in detail:")
    for (cid, t), v in sorted(convd.items(), key=lambda x: -x[1]["cost"]):
        print(f"      {NAMES[cid]:20s} ${v['cost']:>8.2f} clk={v['clk']:>3} "
              f"cpc=${v['cost']/v['clk']:>7.2f} conv={v['conv']:.1f}  {t[:44]}")
    out[f"price_band_{lbl}"] = {
        "converting": {"terms": len(convd), "clicks": cc, "cost": round(ccost, 2),
                       "avg_cpc": round(ccost / cc, 2) if cc else 0,
                       "conversions": round(sum(v["conv"] for v in convd.values()), 2),
                       "detail": [{"campaign": NAMES[k[0]], "term": k[1], "clicks": v["clk"],
                                   "cost": round(v["cost"], 2),
                                   "cpc": round(v["cost"] / v["clk"], 2),
                                   "conversions": round(v["conv"], 2)}
                                  for k, v in sorted(convd.items(), key=lambda x: -x[1]["cost"])]},
        "non_converting": {"terms": len(nonc), "clicks": nc, "cost": round(ncost, 2),
                           "avg_cpc": round(ncost / nc, 2) if nc else 0}}

print("\n\n=== 2. VALID vs INVALID CLICKS (click_view is valid-only; use metrics) ===")
rows = q(c, f"""
    SELECT campaign.id, metrics.clicks, metrics.invalid_clicks, metrics.invalid_click_rate,
           metrics.cost_micros, metrics.impressions
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-01' AND '2026-09-14'
""")
agg = defaultdict(lambda: {"clk": 0, "inv": 0, "cost": 0.0, "impr": 0})
for r in rows:
    k = str(r.campaign.id)
    agg[k]["clk"] += r.metrics.clicks; agg[k]["inv"] += r.metrics.invalid_clicks
    agg[k]["cost"] += r.metrics.cost_micros / 1e6; agg[k]["impr"] += r.metrics.impressions
for k, v in sorted(agg.items(), key=lambda x: -x[1]["cost"]):
    raw = v["clk"] + v["inv"]
    print(f"  {NAMES[k]:20s} billable={v['clk']:>4} invalid={v['inv']:>4} raw={raw:>4} "
          f"invalid_rate={100*v['inv']/raw if raw else 0:>5.1f}%  ${v['cost']:>9.2f}")
out["invalid_clicks_aug_to_sep14"] = {NAMES[k]: {"billable_clicks": v["clk"],
                                                 "invalid_clicks": v["inv"],
                                                 "raw_clicks": v["clk"] + v["inv"],
                                                 "invalid_rate_pct": round(100 * v["inv"] / (v["clk"] + v["inv"]), 2)
                                                 if (v["clk"] + v["inv"]) else 0,
                                                 "cost": round(v["cost"], 2)}
                                      for k, v in agg.items()}

print("\n=== 3. DEVICE SPLIT, Aug 1 - Sep 14 ===")
rows = q(c, f"""
    SELECT campaign.id, segments.device, metrics.impressions, metrics.clicks,
           metrics.cost_micros, metrics.conversions
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-01' AND '2026-09-14'
""")
dv = defaultdict(lambda: {"impr": 0, "clk": 0, "cost": 0.0, "conv": 0.0})
for r in rows:
    k = E(r.segments.device)
    dv[k]["impr"] += r.metrics.impressions; dv[k]["clk"] += r.metrics.clicks
    dv[k]["cost"] += r.metrics.cost_micros / 1e6; dv[k]["conv"] += r.metrics.conversions
for k, v in sorted(dv.items(), key=lambda x: -x[1]["cost"]):
    print(f"  {k:12s} impr={v['impr']:>5} clk={v['clk']:>4} ${v['cost']:>9.2f} "
          f"cpc=${v['cost']/v['clk'] if v['clk'] else 0:>7.2f} conv={v['conv']:.1f}")
out["device"] = {k: {"impressions": v["impr"], "clicks": v["clk"],
                     "cost": round(v["cost"], 2), "conversions": round(v["conv"], 2)}
                 for k, v in dv.items()}

print("\n=== 4. CLICK TYPE, Aug 1 - Sep 14 ===")
rows = q(c, f"""
    SELECT campaign.id, segments.click_type, metrics.clicks, metrics.cost_micros,
           metrics.conversions
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-01' AND '2026-09-14'
""")
ct = defaultdict(lambda: {"clk": 0, "cost": 0.0, "conv": 0.0})
for r in rows:
    k = E(r.segments.click_type)
    ct[k]["clk"] += r.metrics.clicks; ct[k]["cost"] += r.metrics.cost_micros / 1e6
    ct[k]["conv"] += r.metrics.conversions
for k, v in sorted(ct.items(), key=lambda x: -x[1]["cost"]):
    print(f"  {k:26s} clicks={v['clk']:>4} ${v['cost']:>9.2f} "
          f"cpc=${v['cost']/v['clk'] if v['clk'] else 0:>7.2f} conv={v['conv']:.1f}")
out["click_type"] = {k: {"clicks": v["clk"], "cost": round(v["cost"], 2),
                         "conversions": round(v["conv"], 2)} for k, v in ct.items()}

print("\n=== 5. HOUR OF DAY x DAY OF WEEK spend, Aug 1 - Sep 14 ===")
rows = q(c, f"""
    SELECT campaign.id, segments.day_of_week, segments.hour,
           metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-01' AND '2026-09-14'
""")
hh = defaultdict(lambda: {"impr": 0, "clk": 0, "cost": 0.0})
outside = {"impr": 0, "clk": 0, "cost": 0.0}
for r in rows:
    d, h = E(r.segments.day_of_week), r.segments.hour
    hh[(d, h)]["impr"] += r.metrics.impressions
    hh[(d, h)]["clk"] += r.metrics.clicks
    hh[(d, h)]["cost"] += r.metrics.cost_micros / 1e6
    ok = ((d in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY") and 8 <= h < 20)
          or (d == "SATURDAY" and 8 <= h < 13))
    if not ok:
        outside["impr"] += r.metrics.impressions
        outside["clk"] += r.metrics.clicks
        outside["cost"] += r.metrics.cost_micros / 1e6
print(f"  delivery OUTSIDE the approved schedule: impr={outside['impr']} "
      f"clicks={outside['clk']} cost=${outside['cost']:.2f}")
out["outside_schedule_delivery"] = {k: (round(v, 2) if isinstance(v, float) else v)
                                    for k, v in outside.items()}

print("\n=== 6. GEO: matched user location vs targeted, Aug 1 - Sep 14 ===")
try:
    rows = q(c, f"""
        SELECT campaign.id, user_location_view.country_criterion_id,
               user_location_view.targeting_location,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions
        FROM user_location_view WHERE campaign.id IN ({IN5})
          AND segments.date BETWEEN '2026-08-01' AND '2026-09-14'
    """)
    g = defaultdict(lambda: {"impr": 0, "clk": 0, "cost": 0.0, "conv": 0.0})
    for r in rows:
        k = (r.user_location_view.country_criterion_id,
             r.user_location_view.targeting_location)
        g[k]["impr"] += r.metrics.impressions; g[k]["clk"] += r.metrics.clicks
        g[k]["cost"] += r.metrics.cost_micros / 1e6; g[k]["conv"] += r.metrics.conversions
    print(f"  rows: {len(g)}  (country_criterion_id, targeting_location)")
    for k, v in sorted(g.items(), key=lambda x: -x[1]["cost"])[:15]:
        print(f"    {k} impr={v['impr']:>5} clk={v['clk']:>4} ${v['cost']:>9.2f} conv={v['conv']:.1f}")
    out["user_location"] = [{"country_criterion_id": k[0], "targeting_location": k[1],
                             "impressions": v["impr"], "clicks": v["clk"],
                             "cost": round(v["cost"], 2), "conversions": round(v["conv"], 2)}
                            for k, v in sorted(g.items(), key=lambda x: -x[1]["cost"])]
except Exception as ex:
    print("  ERR", str(ex)[:300])

print("\n=== 7. AUCTION INSIGHTS (campaign level, settled Sept) ===")
try:
    rows = q(c, f"""
        SELECT campaign.id, auction_insight_domain,
               metrics.auction_insight_search_impression_share,
               metrics.auction_insight_search_overlap_rate,
               metrics.auction_insight_search_position_above_rate,
               metrics.auction_insight_search_top_impression_percentage,
               metrics.auction_insight_search_absolute_top_impression_percentage,
               metrics.auction_insight_search_outranking_share
        FROM campaign_search_term_insight
        WHERE segments.date BETWEEN '2026-09-01' AND '2026-09-14'
        LIMIT 100
    """)
    print(f"  rows: {len(rows)}")
except Exception as ex:
    print("  auction insights not available via this resource:", str(ex)[:200])
    out["auction_insights"] = "NOT AVAILABLE via API for this account/resource"

p = SNAP / f"diagnostics-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
