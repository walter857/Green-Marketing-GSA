#!/usr/bin/env python3
"""Full settled performance + CPC distribution + segmentation for the five campaigns."""
from __future__ import annotations
import sys, json, statistics
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}


def camp_metrics(start, end, extra_sel="", extra_seg=None, src="campaign"):
    sel = f"campaign.id, campaign.name, {METRICS}"
    if extra_sel:
        sel += ", " + extra_sel
    rows = []
    for r in q(c, f"SELECT {sel} FROM {src} WHERE campaign.id IN ({IN5}) "
                  f"AND segments.date BETWEEN '{start}' AND '{end}'"):
        d = m(r)
        d["camp"] = str(r.campaign.id)
        if extra_seg:
            for k, fn in extra_seg.items():
                d[k] = fn(r)
        rows.append(d)
    return rows


# ---------- 1. WINDOWS ----------
print("=== CAMPAIGN PERFORMANCE BY WINDOW (settled unless flagged) ===")
wins = {}
for label, (s, e) in WINDOWS.items():
    if label in ("csv_source_window", "all_history"):
        continue
    rows = camp_metrics(s, e)
    agg = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                               "conversions": 0.0, "all_conversions": 0.0})
    for r in rows:
        for k in ("impressions", "clicks", "cost", "conversions", "all_conversions"):
            agg[NAME[r["camp"]]][k] += r[k]
    tot = {k: round(sum(v[k] for v in agg.values()), 2)
           for k in ("impressions", "clicks", "cost", "conversions", "all_conversions")}
    tot["cpc"] = round(tot["cost"] / tot["clicks"], 2) if tot["clicks"] else 0
    tot["ctr"] = round(100 * tot["clicks"] / tot["impressions"], 2) if tot["impressions"] else 0
    tot["cpa_primary"] = round(tot["cost"] / tot["conversions"], 2) if tot["conversions"] else None
    wins[label] = {"range": [s, e], "total": tot,
                   "by_campaign": {k: {**v, "cost": round(v["cost"], 2),
                                       "cpc": round(v["cost"] / v["clicks"], 2) if v["clicks"] else 0}
                                   for k, v in agg.items()}}
    print(f"\n{label} [{s} .. {e}]  {tot}")
    for k, v in sorted(agg.items()):
        cpc = round(v["cost"] / v["clicks"], 2) if v["clicks"] else 0
        ctr = round(100 * v["clicks"] / v["impressions"], 2) if v["impressions"] else 0
        print(f"   {k:<20} impr={v['impressions']:<6} clicks={v['clicks']:<4} ctr={ctr:<6} "
              f"cpc=${cpc:<8} ${round(v['cost'], 2):<9} conv={v['conversions']:<5} "
              f"allconv={v['all_conversions']}")
out["windows"] = wins

# ---------- 2. IMPRESSION SHARE ----------
print("\n=== IMPRESSION SHARE (last 30 settled) ===")
iss = []
for r in q(c, f"SELECT campaign.id, {METRICS}, {IS_METRICS} FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN "
              f"'{WINDOWS['last_30'][0]}' AND '{WINDOWS['last_30'][1]}'"):
    x = r.metrics
    iss.append({"camp": str(r.campaign.id), "cost": round(x.cost_micros / 1e6, 2),
                "search_is": round(x.search_impression_share * 100, 2),
                "lost_budget": round(x.search_budget_lost_impression_share * 100, 2),
                "lost_rank": round(x.search_rank_lost_impression_share * 100, 2),
                "top_is": round(x.search_top_impression_share * 100, 2),
                "abs_top_is": round(x.search_absolute_top_impression_share * 100, 2)})
out["impression_share_30d"] = iss
for x in sorted(iss, key=lambda x: -x["cost"]):
    print(f"  {NAME[x['camp']]:<20} IS={x['search_is']:>6}%  lostRANK={x['lost_rank']:>6}%  "
          f"lostBUDGET={x['lost_budget']:>6}%  topIS={x['top_is']:>6}%  absTopIS={x['abs_top_is']:>6}%")

# ---------- 3. CPC DISTRIBUTION from raw click-level proxy (date x keyword x term) ----------
print("\n=== CPC DISTRIBUTION (per search-term row, cost/clicks, settled 08-14..09-08) ===")
strows = []
for r in q(c, f"""
    SELECT campaign.id, search_term_view.search_term, segments.date,
           metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions
    FROM search_term_view
    WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
      AND metrics.clicks > 0
"""):
    strows.append({"camp": str(r.campaign.id), "term": r.search_term_view.search_term,
                   "date": r.segments.date, "clicks": r.metrics.clicks,
                   "cost": round(r.metrics.cost_micros / 1e6, 2),
                   "conversions": round(r.metrics.conversions, 2),
                   "all_conversions": round(r.metrics.all_conversions, 2)})
out["clicked_search_term_rows"] = strows
print("clicked rows:", len(strows), "clicks:", sum(r["clicks"] for r in strows),
      "cost:", round(sum(r["cost"] for r in strows), 2))


def pct(vals, p):
    if not vals:
        return None
    vals = sorted(vals)
    k = (len(vals) - 1) * p / 100
    f, cl = int(k), min(int(k) + 1, len(vals) - 1)
    return round(vals[f] + (vals[cl] - vals[f]) * (k - f), 2)


percamp = defaultdict(list)
allcpc = []
for r in strows:
    cpc = r["cost"] / r["clicks"]
    for _ in range(r["clicks"]):
        percamp[r["camp"]].append(round(cpc, 2))
        allcpc.append(round(cpc, 2))
dist = {}
for cid, v in percamp.items():
    dist[NAME[cid]] = {"n_clicks": len(v), "min": min(v), "p25": pct(v, 25), "median": pct(v, 50),
                       "p75": pct(v, 75), "p90": pct(v, 90), "p95": pct(v, 95), "max": max(v),
                       "mean": round(sum(v) / len(v), 2)}
dist["ALL FIVE"] = {"n_clicks": len(allcpc), "min": min(allcpc), "p25": pct(allcpc, 25),
                    "median": pct(allcpc, 50), "p75": pct(allcpc, 75), "p90": pct(allcpc, 90),
                    "p95": pct(allcpc, 95), "max": max(allcpc),
                    "mean": round(sum(allcpc) / len(allcpc), 2)}
out["cpc_distribution"] = dist
for k, v in dist.items():
    print(f"  {k:<20} n={v['n_clicks']:<4} min=${v['min']:<7} p25=${v['p25']:<7} med=${v['median']:<7} "
          f"p75=${v['p75']:<7} p90=${v['p90']:<7} p95=${v['p95']:<7} max=${v['max']:<7} mean=${v['mean']}")

# ---------- 4. CPC OF CONVERTING CLICKS ----------
print("\n=== CPC OF CLICKS THAT PRODUCED A CONVERSION ===")
convclicks = [r for r in strows if r["conversions"] > 0]
allconvclicks = [r for r in strows if r["all_conversions"] > 0]
cc = sorted(round(r["cost"] / r["clicks"], 2) for r in convclicks)
ac = sorted(round(r["cost"] / r["clicks"], 2) for r in allconvclicks)
out["converting_click_cpcs"] = {"primary": cc, "all_conversions": ac}
print("  rows with PRIMARY conversions:", len(convclicks), "CPCs:", cc)
print("  rows with ALL conversions   :", len(allconvclicks), "n:", len(ac),
      "min/med/max:", (min(ac), pct(ac, 50), max(ac)) if ac else None)
print("  all_conv CPC percentiles: p25", pct(ac, 25), "p50", pct(ac, 50), "p75", pct(ac, 75),
      "p90", pct(ac, 90))

# ---------- 5. SEGMENTS ----------
def seg(name, sel, key, start="2026-08-14", end="2026-09-08", src="campaign"):
    print(f"\n=== {name} ===")
    agg = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                               "conversions": 0.0, "all_conversions": 0.0})
    for r in q(c, f"SELECT campaign.id, {sel}, {METRICS} FROM {src} "
                  f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '{start}' AND '{end}'"):
        k = key(r)
        for f in ("impressions", "clicks", "conversions", "all_conversions"):
            agg[k][f] += getattr(r.metrics, f)
        agg[k]["cost"] += r.metrics.cost_micros / 1e6
    res = {}
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["cost"]):
        v["cost"] = round(v["cost"], 2)
        v["cpc"] = round(v["cost"] / v["clicks"], 2) if v["clicks"] else 0
        v["ctr"] = round(100 * v["clicks"] / v["impressions"], 2) if v["impressions"] else 0
        res[str(k)] = v
        print(f"  {str(k):<44} impr={v['impressions']:<6} clicks={v['clicks']:<4} "
              f"ctr={v['ctr']:<6} cpc=${v['cpc']:<8} ${v['cost']:<9} conv={round(v['conversions'],2):<5} "
              f"allconv={round(v['all_conversions'],2)}")
    out[name] = res
    return res


seg("device", "segments.device", lambda r: E(r.segments.device))
seg("day_of_week", "segments.day_of_week", lambda r: E(r.segments.day_of_week))
seg("hour", "segments.hour", lambda r: f"{r.segments.hour:02d}:00")
seg("click_type", "segments.click_type", lambda r: E(r.segments.click_type))
# conversion_action segments cannot be combined with click/cost metrics
# (PROHIBITED_SEGMENT_WITH_METRIC). Handled separately in ambient_0909_perf2.py.
seg("campaign_x_date", "segments.date", lambda r: r.segments.date)
seg("network", "segments.ad_network_type", lambda r: E(r.segments.ad_network_type))

print("\n=== TOP vs OTHER (campaign, settled 30d) ===")
for r in q(c, f"SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.cost_micros, "
              f"metrics.search_top_impression_share, metrics.search_absolute_top_impression_share, "
              f"metrics.absolute_top_impression_percentage, metrics.top_impression_percentage "
              f"FROM campaign WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN "
              f"'2026-08-14' AND '2026-09-08'"):
    x = r.metrics
    print(f"  {NAME[str(r.campaign.id)]:<20} impr={x.impressions:<6} "
          f"topPCT={round(x.top_impression_percentage*100,2):<7} "
          f"absTopPCT={round(x.absolute_top_impression_percentage*100,2):<7}")

write(EVID / "2026-09-09-performance.json", out)
