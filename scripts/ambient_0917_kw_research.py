#!/usr/bin/env python3
"""Ambient | 2026-09-17 | Keyword Planner + historical evidence for the heating build.

READ ONLY. Planner geo = 10 peer CITY targets from the live BOFU geo set.
Results are a SAMPLE of the service area and are never scaled by 75/10.
"""
from __future__ import annotations
import sys, json, time, csv, re, datetime
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-17"
c = client(); identity_gate(c, verbose=False)
now = datetime.datetime.now(TZ)
out = {"generated_local": now.isoformat(), "external_writes": 0,
       "planner_note": ("10 peer CITY targets from the live BOFU geo set; zero containment; "
                        "a SAMPLE of the service area, never scaled by 75/10; synonyms share "
                        "one volume bucket so rows are not summed")}

geo_ids = sorted({r.campaign_criterion.location.geo_target_constant.split("/")[-1]
                  for r in q(c, """SELECT campaign.id,
                            campaign_criterion.location.geo_target_constant,
                            campaign_criterion.negative FROM campaign_criterion
                            WHERE campaign.id = 24132507747
                            AND campaign_criterion.type = LOCATION
                            AND campaign_criterion.negative = FALSE""")})
names = {}
for i in range(0, len(geo_ids), 40):
    batch = ",".join(f"'geoTargetConstants/{g}'" for g in geo_ids[i:i + 40])
    for r in q(c, f"""SELECT geo_target_constant.id, geo_target_constant.canonical_name,
                      geo_target_constant.target_type FROM geo_target_constant
                      WHERE geo_target_constant.resource_name IN ({batch})"""):
        names[str(r.geo_target_constant.id)] = (r.geo_target_constant.canonical_name,
                                                E(r.geo_target_constant.target_type))
PREF = ["Annapolis,Maryland", "Glen Burnie,Maryland", "Ellicott City,Maryland",
        "Severn,Maryland", "Severna Park,Maryland", "Bowie,Maryland",
        "Laurel,Maryland", "Catonsville,Maryland", "Odenton,Maryland", "Arnold,Maryland"]
sample = []
for w in PREF:
    for g in geo_ids:
        if names.get(g, ("", ""))[0].startswith(w) and g not in sample:
            sample.append(g); break
print("=== PLANNER GEO SAMPLE (10 peer CITY of 75 live targets) ===")
for g in sample:
    print(f"  {g}  {names[g][0]}")
out["planner_geo"] = [{"id": g, "canonical": names[g][0]} for g in sample]

BATCH = {
 "furnace_repair": ["furnace repair", "furnace repair near me", "gas furnace repair",
                    "furnace not working", "furnace repair service",
                    "furnace repair cost", "residential furnace repair",
                    "furnace technician near me", "furnace fix", "furnace service"],
 "heating_repair_generic": ["heating repair", "heating repair near me",
                            "heating system repair", "heating service near me",
                            "heating contractor near me", "heater repair near me",
                            "heating repair service", "residential heating repair",
                            "heating and cooling repair near me", "heat repair"],
 "heat_pump_install": ["heat pump installation", "heat pump installers near me",
                       "heat pump replacement", "install heat pump",
                       "heat pump installation cost", "new heat pump",
                       "heat pump contractor near me", "central heat pump installation",
                       "heat pump install near me", "heat pump companies near me"],
 "mini_split_install": ["mini split installation", "ductless mini split installation",
                        "mini split installers near me", "ductless installation",
                        "mini split install cost", "ductless mini split installers",
                        "install mini split", "ductless heating installation",
                        "mini split ac installation", "ductless system installation"],
 "oil": ["oil furnace installation", "oil furnace replacement", "oil furnace installers",
         "oil heating system replacement", "replace oil furnace",
         "oil to gas conversion", "oil furnace repair", "oil boiler replacement",
         "oil heating installation", "oil furnace cost"],
 "furnace_replacement": ["furnace replacement", "furnace replacement cost",
                         "replace furnace", "new furnace cost", "furnace installation",
                         "furnace installation near me", "new furnace installation",
                         "furnace replacement near me", "install new furnace",
                         "furnace upgrade"],
}
svc = c.get_service("KeywordPlanIdeaService")
res = {}
for label, seeds in BATCH.items():
    try:
        req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
        req.customer_id = CID
        req.keywords.extend(seeds)
        req.language = "languageConstants/1000"
        req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in sample])
        req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        resp = svc.generate_keyword_historical_metrics(request=req)
        rows = []
        for r in resp.results:
            m = r.keyword_metrics
            rows.append({"keyword": r.text,
                         "avg_monthly_searches": m.avg_monthly_searches,
                         "competition": E(m.competition),
                         "competition_index": m.competition_index,
                         "low_top_usd": round(m.low_top_of_page_bid_micros/1e6, 2)
                         if m.low_top_of_page_bid_micros else None,
                         "high_top_usd": round(m.high_top_of_page_bid_micros/1e6, 2)
                         if m.high_top_of_page_bid_micros else None,
                         "low_top_micros": m.low_top_of_page_bid_micros or None,
                         "high_top_micros": m.high_top_of_page_bid_micros or None,
                         "monthly": [{"y": v.year, "m": E(v.month),
                                      "searches": v.monthly_searches}
                                     for v in m.monthly_search_volumes],
                         "retrieved": now.isoformat()})
        res[label] = rows
        print(f"\n=== {label} ===")
        print(f"  {'avg/mo':>7} {'comp':>11} {'TOPlow':>8} {'TOPhigh':>8}  keyword")
        for x in sorted(rows, key=lambda y: -(y["avg_monthly_searches"] or 0)):
            print(f"  {x['avg_monthly_searches'] or 0:>7} {x['competition']:>11} "
                  f"{str(x['low_top_usd']):>8} {str(x['high_top_usd']):>8}  {x['keyword']}")
    except Exception as ex:
        res[label] = {"error": str(ex)[:400]}
        print(f"\n=== {label} FAILED: {str(ex)[:250]}")
    time.sleep(5)
out["planner"] = res

print("\n\n=== SEASONALITY Sep->Mar for the top terms ===")
seas = {}
for lab, rows in res.items():
    if isinstance(rows, dict):
        continue
    for x in rows:
        mv = {f"{m['y']}-{m['m'][:3]}": m["searches"] for m in x["monthly"]}
        if mv and (x["avg_monthly_searches"] or 0) >= 20:
            seas[x["keyword"]] = mv
mon = sorted({m for k in seas for m in seas[k]})[-13:]
print(f"  {'keyword':32s} " + " ".join(f"{m[-7:]:>8}" for m in mon))
for k in sorted(seas, key=lambda z: -max(seas[z].values()))[:14]:
    print(f"  {k[:32]:32s} " + " ".join(f"{seas[k].get(m,0):>8}" for m in mon))
out["seasonality"] = seas

print("\n=== HISTORICAL ACCOUNT EVIDENCE: keywords matching the candidates ===")
PATS = {
 "Furnace Repair": r"furnace.*(repair|fix|service)|(repair|fix).*furnace",
 "Heating Repair (generic)": r"heating.*(repair|service)|heat.*repair|heating and (cooling|air).*repair",
 "Heat Pump Install": r"heat pump.*(install|replac)|install.*heat pump",
 "Mini Split Install": r"(mini.?split|ductless).*(install)|install.*(mini.?split|ductless)",
 "Oil": r"\boil\b",
 "Furnace Install/Replace": r"furnace.*(install|replac)|(install|replac).*furnace",
}
kw = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0, "kws": set()})
for r in q(c, f"""SELECT campaign.name, ad_group_criterion.keyword.text,
                  metrics.impressions, metrics.clicks, metrics.cost_micros,
                  metrics.conversions FROM keyword_view
                  WHERE segments.date BETWEEN '2019-01-01' AND '{now.date()}'"""):
    t = r.ad_group_criterion.keyword.text
    for lab, p in PATS.items():
        if re.search(p, t, re.I):
            d = kw[lab]
            d["impr"] += r.metrics.impressions; d["clicks"] += r.metrics.clicks
            d["cost"] += r.metrics.cost_micros/1e6; d["conv"] += r.metrics.conversions
            d["kws"].add(t)
            break
print(f"  {'cluster':26s} {'impr':>7} {'clk':>6} {'cost':>11} {'CPC':>8} {'conv':>6} {'CPA':>10}  #kw")
hist = {}
for lab, d in sorted(kw.items(), key=lambda x: -x[1]["cost"]):
    cpc = d["cost"]/d["clicks"] if d["clicks"] else 0
    cpa = d["cost"]/d["conv"] if d["conv"] else None
    print(f"  {lab:26s} {d['impr']:>7} {d['clicks']:>6} ${d['cost']:>10,.2f} "
          f"${cpc:>7.2f} {d['conv']:>6.1f} {('$%.2f'%cpa) if cpa else '-':>10}  {len(d['kws'])}")
    hist[lab] = {"impressions": d["impr"], "clicks": d["clicks"],
                 "cost": round(d["cost"], 2), "avg_cpc": round(cpc, 2),
                 "conversions": round(d["conv"], 2),
                 "cpa": round(cpa, 2) if cpa else None,
                 "distinct_keywords": len(d["kws"])}
out["historical_by_cluster"] = hist

print("\n=== HISTORICAL CONVERTING SEARCH TERMS (heating) ===")
st = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0})
HEAT = re.compile(r"heat|furnace|boiler|mini.?split|ductless|oil\b", re.I)
for r in q(c, f"""SELECT search_term_view.search_term, metrics.impressions,
                  metrics.clicks, metrics.cost_micros, metrics.conversions
                  FROM search_term_view
                  WHERE segments.date BETWEEN '2019-01-01' AND '{now.date()}'"""):
    t = r.search_term_view.search_term
    if not HEAT.search(t):
        continue
    d = st[t]
    d["impr"] += r.metrics.impressions; d["clicks"] += r.metrics.clicks
    d["cost"] += r.metrics.cost_micros/1e6; d["conv"] += r.metrics.conversions
conv_terms = {k: v for k, v in st.items() if v["conv"] > 0}
print(f"  heating search terms with data: {len(st)}   CONVERTING: {len(conv_terms)}")
print(f"  {'cost':>10} {'clk':>5} {'conv':>5} {'CPC':>8}  term")
for t, v in sorted(conv_terms.items(), key=lambda x: -x[1]["conv"])[:30]:
    print(f"  ${v['cost']:>9,.2f} {v['clicks']:>5} {v['conv']:>5.1f} "
          f"${v['cost']/v['clicks'] if v['clicks'] else 0:>7.2f}  {t[:52]}")
out["historical_converting_heating_terms"] = [
    {"term": t, "impressions": v["impr"], "clicks": v["clicks"],
     "cost": round(v["cost"], 2), "conversions": round(v["conv"], 2),
     "avg_cpc": round(v["cost"]/v["clicks"], 2) if v["clicks"] else None}
    for t, v in sorted(conv_terms.items(), key=lambda x: -x[1]["conv"])]

EXPORTS.mkdir(parents=True, exist_ok=True)
p = EXPORTS / f"heating-build-research-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
cp = EXPORTS / f"heating-build-planner-{STAMP}.csv"
with cp.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["cluster", "keyword", "avg_monthly_searches", "competition",
                "competition_index", "low_top_usd", "high_top_usd",
                "low_top_micros", "high_top_micros", "retrieved"])
    for lab, rows in res.items():
        if isinstance(rows, dict):
            continue
        for x in rows:
            w.writerow([lab, x["keyword"], x["avg_monthly_searches"], x["competition"],
                        x["competition_index"], x["low_top_usd"], x["high_top_usd"],
                        x["low_top_micros"], x["high_top_micros"], x["retrieved"]])
print(f"\nWROTE {p}\nWROTE {cp}")
print("EXTERNAL WRITES: 0")
