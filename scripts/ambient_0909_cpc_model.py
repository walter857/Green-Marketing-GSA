#!/usr/bin/env python3
"""CPC-ceiling model: for every candidate cap, what fraction of OBSERVED clicks,
spend and conversions would have survived? Plus economic-CPC scenario bands."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

perf = json.load(open(EVID / "2026-09-09-performance.json", encoding="utf-8"))
strows = perf["clicked_search_term_rows"]
print(f"clicked search-term rows (settled 2026-08-14..2026-09-08): {len(strows)}")

# Expand to per-click records carrying their row's CPC and conversion share.
clicks = []
for r in strows:
    cpc = r["cost"] / r["clicks"]
    for i in range(r["clicks"]):
        clicks.append({"camp": r["camp"], "cpc": round(cpc, 2), "date": r["date"],
                       "conv": r["conversions"] / r["clicks"],
                       "allconv": r["all_conversions"] / r["clicks"]})
print(f"per-click records: {len(clicks)}  total cost ${round(sum(c['cpc'] for c in clicks),2)}")

MAX_CPQL = {"24132507741": 150.0, "24132507750": 250.0, "24132507747": 280.0,
            "24132507753": 280.0, "24132507744": 250.0}
CURRENT_CEILING = {"24132507741": 25.0, "24132507750": 25.0, "24132507747": 30.0,
                   "24132507753": None, "24132507744": None}
CANDIDATES = [25, 30, 40, 50, 60, 75, 90, 110, 130, 160, None]

print("\n=== MODELLED SURVIVAL AT EACH CANDIDATE CAP ===")
print("  (a click survives if its observed CPC <= cap; Maximize Clicks would have")
print("   re-auctioned some of these, so treat survival as an UPPER bound on loss)\n")
model = {}
for cid in FIVE:
    cc = [c for c in clicks if c["camp"] == cid]
    if not cc:
        print(f"  {NAME[cid]:<20} no clicked traffic in the settled window")
        model[NAME[cid]] = {"n_clicks": 0}
        continue
    base_cost = sum(c["cpc"] for c in cc)
    base_conv = sum(c["conv"] for c in cc)
    base_all = sum(c["allconv"] for c in cc)
    print(f"  {NAME[cid]}   baseline: {len(cc)} clicks  ${base_cost:.2f}  "
          f"conv={base_conv:.1f}  allconv={base_all:.1f}  CPC=${base_cost/len(cc):.2f}"
          f"   [live ceiling: {CURRENT_CEILING[cid]}]")
    rows = []
    print(f"     {'cap':>7}{'clicks':>8}{'clk%':>7}{'spend':>11}{'spend%':>8}"
          f"{'conv':>7}{'conv%':>7}{'CPA':>10}{'CPC':>8}")
    for cap in CANDIDATES:
        keep = cc if cap is None else [c for c in cc if c["cpc"] <= cap]
        k, cost = len(keep), sum(c["cpc"] for c in keep)
        conv = sum(c["conv"] for c in keep)
        allc = sum(c["allconv"] for c in keep)
        row = {"cap": cap, "clicks": k, "clicks_pct": round(100 * k / len(cc), 1),
               "spend": round(cost, 2),
               "spend_pct": round(100 * cost / base_cost, 1) if base_cost else 0,
               "conversions": round(conv, 2),
               "conv_pct": round(100 * conv / base_conv, 1) if base_conv else None,
               "cpa": round(cost / conv, 2) if conv else None,
               "cpc": round(cost / k, 2) if k else None}
        rows.append(row)
        lbl = "none" if cap is None else f"${cap}"
        print(f"     {lbl:>7}{k:>8}{row['clicks_pct']:>7}{row['spend']:>11}"
              f"{row['spend_pct']:>8}{row['conversions']:>7}"
              f"{str(row['conv_pct']):>7}{str(row['cpa']):>10}{str(row['cpc']):>8}")
    model[NAME[cid]] = {"n_clicks": len(cc), "baseline_cost": round(base_cost, 2),
                        "baseline_conv": round(base_conv, 2), "rows": rows,
                        "live_ceiling": CURRENT_CEILING[cid]}

print("\n=== ECONOMIC CPC SCENARIO BANDS ===")
print("  economic CPC = max acceptable CPQL x qualified conversion rate")
print("  qualified CVR is UNKNOWN (WHATCONVERTS_API_TOKEN is empty). Bands below assume")
print("  a qualification rate applied to the OBSERVED raw primary CVR.\n")
econ = {}
for cid in FIVE:
    cc = [c for c in clicks if c["camp"] == cid]
    if not cc:
        continue
    raw_cvr = sum(c["conv"] for c in cc) / len(cc)
    band = {}
    for lbl, q in (("conservative", 0.40), ("base", 0.60), ("optimistic", 0.80)):
        qcvr = raw_cvr * q
        band[lbl] = {"qualification_rate": q, "assumed_qualified_cvr": round(100 * qcvr, 2),
                     "economic_cpc": round(MAX_CPQL[cid] * qcvr, 2)}
    econ[NAME[cid]] = {"raw_primary_cvr_pct": round(100 * raw_cvr, 2),
                       "max_cpql": MAX_CPQL[cid], "bands": band,
                       "observed_cpc": round(sum(c["cpc"] for c in cc) / len(cc), 2)}
    print(f"  {NAME[cid]:<20} rawCVR={100*raw_cvr:>6.2f}%  maxCPQL=${MAX_CPQL[cid]:<6} "
          f"observedCPC=${econ[NAME[cid]]['observed_cpc']:<8} "
          f"econCPC: cons=${band['conservative']['economic_cpc']:<7} "
          f"base=${band['base']['economic_cpc']:<7} opt=${band['optimistic']['economic_cpc']}")

print("\n=== HVAC INSTALLATION: BEFORE vs AFTER THE 'hvac installers' KEYWORD SWAP ===")
for lbl, lo, hi in (("with 'hvac installers'   08-14..08-28", "2026-08-14", "2026-08-28"),
                    ("after swap to 'near me'  08-29..09-03", "2026-08-29", "2026-09-03"),
                    ("after 09-04 ceiling      09-05..09-08", "2026-09-05", "2026-09-08")):
    cc = [c for c in clicks if c["camp"] == "24132507747" and lo <= c["date"] <= hi]
    cost = sum(c["cpc"] for c in cc)
    conv = sum(c["conv"] for c in cc)
    allc = sum(c["allconv"] for c in cc)
    print(f"  {lbl:<40} clicks={len(cc):<4} ${cost:<9.2f} "
          f"CPC=${(cost/len(cc) if cc else 0):<7.2f} conv={conv:<5.1f} allconv={allc:<5.1f} "
          f"CPA=${(cost/conv if conv else 0):.2f}"
          f"  maxCPC=${max((c['cpc'] for c in cc), default=0):.2f}")

write(EVID / "2026-09-09-cpc-model.json", {"survival_model": model, "economic_bands": econ,
                                           "max_cpql": {NAME[k]: v for k, v in MAX_CPQL.items()},
                                           "live_ceilings": {NAME[k]: v for k, v in
                                                             CURRENT_CEILING.items()}})
