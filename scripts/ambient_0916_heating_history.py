#!/usr/bin/env python3
"""Ambient | 2026-09-16 | historical heating research across ALL campaigns, all statuses.

READ ONLY. No mutate, no validate_only.
"""
from __future__ import annotations
import sys, json, re, datetime, csv
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-16"
SETTLED = "2026-09-15"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "latest_settled": SETTLED, "account_timezone": "America/New_York",
       "external_writes": 0}
c = client(); identity_gate(c, verbose=False)

# canonical heating clusters -> regex over keyword / search-term / campaign text
CLUSTERS = {
    "Furnace Repair":        r"\bfurnace\b.*\b(repair|fix|broke|not work|service)\b|\b(repair|fix)\b.*\bfurnace\b|gas furnace|electric furnace",
    "Furnace Install/Replace": r"\bfurnace\b.*\b(install|replace|new)\b|\b(install|replace|new)\b.*\bfurnace\b",
    "Heating Repair":        r"\bheat(ing)?\b.*\b(repair|fix|not work|broke)\b|\bno heat\b|\bheater (repair|fix|broke)\b|heat (and|&) air repair",
    "Heating Install/Replace": r"\bheat(ing)?( system)?\b.*\b(install|replace|new)\b|\b(install|replace)\b.*\bheating\b",
    "Heating Maintenance":   r"\bheat(ing)?\b.*\b(maintenance|tune.?up|inspect|check)\b|furnace (maintenance|tune.?up|clean)",
    "Boiler Repair":         r"\bboiler\b.*\b(repair|fix|service|not work)\b|\b(repair|fix)\b.*\bboiler\b",
    "Boiler Install/Replace": r"\bboiler\b.*\b(install|replace|new)\b|\b(install|replace|new)\b.*\bboiler\b|tankless boiler",
    "Heat Pump":             r"\bheat pump\b|water source heat pump|geothermal",
    "Mini Split / Ductless": r"mini.?split|\bductless\b",
    "Thermostat":            r"\bthermostat\b|\bnest\b.*install",
    "Emergency / No Heat":   r"\bemergency\b.*\b(heat|furnace|boiler)\b|\bno heat\b|24 hour heat",
    "Water Heater":          r"water heater|\btankless water\b|\bhot water\b",
    "Geothermal":            r"\bgeothermal\b",
}
HEAT_ANY = re.compile("|".join(f"(?:{v})" for v in CLUSTERS.values()), re.I)


def cluster_of(text):
    hits = [k for k, v in CLUSTERS.items() if re.search(v, str(text), re.I)]
    if not hits:
        return None
    # prefer the most specific (install/replace over generic repair)
    for pref in ("Geothermal", "Mini Split / Ductless", "Heat Pump", "Water Heater",
                 "Thermostat", "Boiler Install/Replace", "Boiler Repair",
                 "Furnace Install/Replace", "Furnace Repair", "Heating Install/Replace",
                 "Heating Maintenance", "Emergency / No Heat", "Heating Repair"):
        if pref in hits:
            return pref
    return hits[0]


print("=== 1. HEATING-RELEVANT CAMPAIGNS (any status) ===")
camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                        campaign.advertising_channel_type, campaign_budget.amount_micros
                 FROM campaign"""):
    camps[str(r.campaign.id)] = {"name": r.campaign.name, "status": E(r.campaign.status),
                                 "channel": E(r.campaign.advertising_channel_type),
                                 "budget": round(r.campaign_budget.amount_micros/1e6, 2)}
heat_camps = {k: v for k, v in camps.items()
              if HEAT_ANY.search(v["name"]) or re.search(
                  r"heat|furnace|boiler|geotherm|mini.?split|thermostat|tankless",
                  v["name"], re.I)}
for k, v in sorted(heat_camps.items(), key=lambda x: x[1]["name"]):
    print(f"  {k} {v['status']:8s} {v['channel']:16s} ${v['budget']:>7.2f}/d  {v['name']}")
print(f"  total heating-relevant campaigns: {len(heat_camps)}")
out["heating_campaigns"] = heat_camps

print("\n=== 2. ALL-TIME PERFORMANCE OF EVERY HEATING CAMPAIGN ===")
IDS = ",".join(heat_camps)
perf = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                            "allconv": 0.0, "months": set()})
for r in q(c, f"""SELECT campaign.id, segments.month, metrics.impressions, metrics.clicks,
                         metrics.cost_micros, metrics.conversions, metrics.all_conversions
                  FROM campaign WHERE campaign.id IN ({IDS})
                    AND segments.date BETWEEN '2019-01-01' AND '{SETTLED}'"""):
    k = str(r.campaign.id); p = perf[k]
    p["impr"] += r.metrics.impressions; p["clicks"] += r.metrics.clicks
    p["cost"] += r.metrics.cost_micros / 1e6
    p["conv"] += r.metrics.conversions; p["allconv"] += r.metrics.all_conversions
    if r.metrics.impressions:
        p["months"].add(r.segments.month)
rows = []
print(f"  {'campaign':44s} {'status':8s} {'impr':>7} {'clk':>5} {'cost':>10} "
      f"{'CPC':>8} {'CTR':>6} {'conv':>6} {'CPA':>9}")
for k, p in sorted(perf.items(), key=lambda x: -x[1]["cost"]):
    if not p["impr"]:
        continue
    cpc = p["cost"] / p["clicks"] if p["clicks"] else 0
    ctr = 100 * p["clicks"] / p["impr"] if p["impr"] else 0
    cpa = p["cost"] / p["conv"] if p["conv"] else 0
    print(f"  {camps[k]['name'][:44]:44s} {camps[k]['status']:8s} {p['impr']:>7} "
          f"{p['clicks']:>5} ${p['cost']:>9,.2f} ${cpc:>7.2f} {ctr:>5.2f}% "
          f"{p['conv']:>6.1f} " + (f"${cpa:>8,.2f}" if p["conv"] else "       -"))
    rows.append({"campaign_id": k, "campaign": camps[k]["name"],
                 "status": camps[k]["status"], "channel": camps[k]["channel"],
                 "impressions": p["impr"], "clicks": p["clicks"],
                 "cost": round(p["cost"], 2), "avg_cpc": round(cpc, 2),
                 "ctr_pct": round(ctr, 2), "conversions": round(p["conv"], 2),
                 "all_conversions": round(p["allconv"], 2),
                 "cpa": round(cpa, 2) if p["conv"] else None,
                 "active_months": sorted(p["months"])})
out["heating_campaign_alltime"] = rows
tot = {k: sum(r[k] for r in rows) for k in ("impressions", "clicks", "cost", "conversions")}
print(f"\n  TOTAL heating history: impr={tot['impressions']:,} clicks={tot['clicks']:,} "
      f"cost=${tot['cost']:,.2f} conv={tot['conversions']:.1f}  "
      f"avgCPC=${tot['cost']/tot['clicks'] if tot['clicks'] else 0:.2f}")
out["heating_alltime_total"] = {k: round(v, 2) for k, v in tot.items()}

print("\n=== 3. MONTH-BY-MONTH HEATING SPEND (seasonality) ===")
bymonth = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0})
for r in q(c, f"""SELECT campaign.id, segments.month, metrics.impressions, metrics.clicks,
                         metrics.cost_micros, metrics.conversions
                  FROM campaign WHERE campaign.id IN ({IDS})
                    AND segments.date BETWEEN '2023-09-01' AND '{SETTLED}'"""):
    m = r.segments.month
    bymonth[m]["impr"] += r.metrics.impressions; bymonth[m]["clicks"] += r.metrics.clicks
    bymonth[m]["cost"] += r.metrics.cost_micros / 1e6
    bymonth[m]["conv"] += r.metrics.conversions
print(f"  {'month':10s} {'impr':>7} {'clk':>5} {'cost':>10} {'CPC':>8} {'conv':>6}")
for m in sorted(bymonth):
    v = bymonth[m]
    if not v["impr"]:
        continue
    print(f"  {m:10s} {v['impr']:>7} {v['clicks']:>5} ${v['cost']:>9,.2f} "
          f"${v['cost']/v['clicks'] if v['clicks'] else 0:>7.2f} {v['conv']:>6.1f}")
out["heating_by_month"] = {m: {"impressions": v["impr"], "clicks": v["clicks"],
                               "cost": round(v["cost"], 2),
                               "avg_cpc": round(v["cost"]/v["clicks"], 2) if v["clicks"] else None,
                               "conversions": round(v["conv"], 2)}
                           for m, v in sorted(bymonth.items()) if v["impr"]}

print("\n=== 4. LAST HEATING SEASON: Oct 2025 - Mar 2026 ===")
season = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0})
for r in q(c, f"""SELECT campaign.id, metrics.impressions, metrics.clicks,
                         metrics.cost_micros, metrics.conversions
                  FROM campaign WHERE campaign.id IN ({IDS})
                    AND segments.date BETWEEN '2025-10-01' AND '2026-03-31'"""):
    k = str(r.campaign.id)
    season[k]["impr"] += r.metrics.impressions; season[k]["clicks"] += r.metrics.clicks
    season[k]["cost"] += r.metrics.cost_micros / 1e6
    season[k]["conv"] += r.metrics.conversions
sr = []
for k, v in sorted(season.items(), key=lambda x: -x[1]["cost"]):
    if not v["impr"]:
        continue
    cpc = v["cost"] / v["clicks"] if v["clicks"] else 0
    print(f"  {camps[k]['name'][:44]:44s} impr={v['impr']:>6} clk={v['clicks']:>4} "
          f"${v['cost']:>9,.2f} CPC=${cpc:>7.2f} conv={v['conv']:>5.1f}")
    sr.append({"campaign": camps[k]["name"], "campaign_id": k,
               "impressions": v["impr"], "clicks": v["clicks"],
               "cost": round(v["cost"], 2), "avg_cpc": round(cpc, 2),
               "conversions": round(v["conv"], 2)})
out["last_heating_season_2025_10_to_2026_03"] = sr
st = {kk: sum(x[kk] for x in sr) for kk in ("impressions", "clicks", "cost", "conversions")}
print(f"  SEASON TOTAL: impr={st['impressions']:,} clicks={st['clicks']:,} "
      f"cost=${st['cost']:,.2f} conv={st['conversions']:.1f} "
      f"CPC=${st['cost']/st['clicks'] if st['clicks'] else 0:.2f}")
out["last_season_total"] = {k: round(v, 2) for k, v in st.items()}

print("\n=== 5. HISTORICAL HEATING KEYWORDS (all statuses, all campaigns) ===")
kw = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                          "campaigns": set(), "match": set(), "status": set()})
for r in q(c, f"""SELECT campaign.id, campaign.name, ad_group.name,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status,
                         metrics.impressions, metrics.clicks, metrics.cost_micros,
                         metrics.conversions
                  FROM keyword_view
                  WHERE segments.date BETWEEN '2019-01-01' AND '{SETTLED}'"""):
    t = r.ad_group_criterion.keyword.text
    if not HEAT_ANY.search(t):
        continue
    d = kw[t]
    d["impr"] += r.metrics.impressions; d["clicks"] += r.metrics.clicks
    d["cost"] += r.metrics.cost_micros / 1e6; d["conv"] += r.metrics.conversions
    d["campaigns"].add(r.campaign.name[:34])
    d["match"].add(E(r.ad_group_criterion.keyword.match_type))
    d["status"].add(E(r.ad_group_criterion.status))
print(f"  distinct historical heating keywords with data: "
      f"{sum(1 for v in kw.values() if v['impr'])}")
print(f"  {'cost':>9} {'clk':>5} {'impr':>7} {'CPC':>8} {'conv':>5}  keyword")
kwrows = []
for t, v in sorted(kw.items(), key=lambda x: -x[1]["cost"])[:45]:
    if not v["impr"]:
        continue
    cpc = v["cost"] / v["clicks"] if v["clicks"] else 0
    print(f"  ${v['cost']:>8,.2f} {v['clicks']:>5} {v['impr']:>7} ${cpc:>7.2f} "
          f"{v['conv']:>5.1f}  {t[:44]:44s} {sorted(v['match'])}")
for t, v in kw.items():
    if v["impr"]:
        kwrows.append({"keyword": t, "cluster": cluster_of(t),
                       "match_types": sorted(v["match"]),
                       "statuses": sorted(v["status"]),
                       "campaigns": sorted(v["campaigns"]),
                       "impressions": v["impr"], "clicks": v["clicks"],
                       "cost": round(v["cost"], 2),
                       "avg_cpc": round(v["cost"]/v["clicks"], 2) if v["clicks"] else None,
                       "conversions": round(v["conv"], 2)})
out["historical_heating_keywords"] = sorted(kwrows, key=lambda x: -x["cost"])

print("\n=== 6. HISTORICAL HEATING SEARCH TERMS (all campaigns, all time) ===")
st_ = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                           "campaigns": set()})
for r in q(c, f"""SELECT campaign.id, campaign.name, search_term_view.search_term,
                         metrics.impressions, metrics.clicks, metrics.cost_micros,
                         metrics.conversions FROM search_term_view
                  WHERE segments.date BETWEEN '2019-01-01' AND '{SETTLED}'"""):
    t = r.search_term_view.search_term
    if not HEAT_ANY.search(t):
        continue
    d = st_[t]
    d["impr"] += r.metrics.impressions; d["clicks"] += r.metrics.clicks
    d["cost"] += r.metrics.cost_micros / 1e6; d["conv"] += r.metrics.conversions
    d["campaigns"].add(r.campaign.name[:30])
print(f"  distinct heating search terms: {len(st_)}")
strows = [{"search_term": t, "cluster": cluster_of(t), "impressions": v["impr"],
           "clicks": v["clicks"], "cost": round(v["cost"], 2),
           "avg_cpc": round(v["cost"]/v["clicks"], 2) if v["clicks"] else None,
           "conversions": round(v["conv"], 2), "campaigns": sorted(v["campaigns"])}
          for t, v in st_.items()]
out["historical_heating_search_terms"] = sorted(strows, key=lambda x: -x["cost"])
print(f"  {'cost':>9} {'clk':>4} {'impr':>6} {'CPC':>8} {'conv':>5}  term")
for x in out["historical_heating_search_terms"][:40]:
    print(f"  ${x['cost']:>8,.2f} {x['clicks']:>4} {x['impressions']:>6} "
          f"${x['avg_cpc'] or 0:>7.2f} {x['conversions']:>5.1f}  {x['search_term'][:50]}")

print("\n=== 7. CLUSTER ROLL-UP (historical account evidence) ===")
cl = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0, "terms": 0})
for x in strows:
    k = x["cluster"] or "Unclassified"
    cl[k]["impr"] += x["impressions"]; cl[k]["clicks"] += x["clicks"]
    cl[k]["cost"] += x["cost"]; cl[k]["conv"] += x["conversions"]; cl[k]["terms"] += 1
print(f"  {'cluster':26s} {'terms':>6} {'impr':>7} {'clk':>5} {'cost':>10} {'CPC':>8} {'conv':>5}")
for k, v in sorted(cl.items(), key=lambda x: -x[1]["cost"]):
    print(f"  {k:26s} {v['terms']:>6} {v['impr']:>7} {v['clicks']:>5} ${v['cost']:>9,.2f} "
          f"${v['cost']/v['clicks'] if v['clicks'] else 0:>7.2f} {v['conv']:>5.1f}")
out["cluster_rollup"] = {k: {"distinct_terms": v["terms"], "impressions": v["impr"],
                             "clicks": v["clicks"], "cost": round(v["cost"], 2),
                             "avg_cpc": round(v["cost"]/v["clicks"], 2) if v["clicks"] else None,
                             "conversions": round(v["conv"], 2)}
                         for k, v in sorted(cl.items(), key=lambda x: -x[1]["cost"])}

EXPORTS.mkdir(parents=True, exist_ok=True)
p = EXPORTS / f"heating-history-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
cp = EXPORTS / f"heating-history-search-terms-{STAMP}.csv"
with cp.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["search_term", "cluster", "impressions", "clicks",
                                      "cost", "avg_cpc", "conversions", "campaigns"])
    w.writeheader()
    for x in out["historical_heating_search_terms"]:
        w.writerow({**x, "campaigns": "; ".join(x["campaigns"])})
kp = EXPORTS / f"heating-history-keywords-{STAMP}.csv"
with kp.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["keyword", "cluster", "match_types", "statuses",
                                      "impressions", "clicks", "cost", "avg_cpc",
                                      "conversions", "campaigns"])
    w.writeheader()
    for x in out["historical_heating_keywords"]:
        w.writerow({**x, "match_types": "; ".join(x["match_types"]),
                    "statuses": "; ".join(x["statuses"]),
                    "campaigns": "; ".join(x["campaigns"])})
print(f"\nWROTE {p}\nWROTE {cp}\nWROTE {kp}")
print("EXTERNAL WRITES: 0")
