#!/usr/bin/env python3
"""Ambient | 2026-09-16 | geo crosswalk + Keyword Planner for heating clusters.

READ ONLY. KeywordPlanIdeaService caps geo_target_constants at 10 per request and has
its own quota that 429s quickly, so batches are small, reproducible and paced.

Overlap control: every live geo target is resolved to its canonical name and target_type.
Containment is detected (a City inside a targeted County, a Postal Code inside a targeted
City) so overlapping areas are never summed and presented as unique demand.
"""
from __future__ import annotations
import sys, json, time, csv, datetime
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-16"
c = client(); identity_gate(c, verbose=False)
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "account_timezone": "America/New_York", "latest_settled": "2026-09-15",
       "api_method": "KeywordPlanIdeaService.GenerateKeywordHistoricalMetrics",
       "network": "GOOGLE_SEARCH", "language": "languageConstants/1000 (English)",
       "currency": "USD", "external_writes": 0}

print("=== 1. LIVE GEO TARGETS ON THE FIVE CAMPAIGNS ===")
geo_by_camp = defaultdict(set)
for r in q(c, f"""SELECT campaign.id, campaign_criterion.location.geo_target_constant,
                         campaign_criterion.negative
                  FROM campaign_criterion WHERE campaign.id IN ({IN5})
                    AND campaign_criterion.type = LOCATION"""):
    gid = r.campaign_criterion.location.geo_target_constant.split("/")[-1]
    if not r.campaign_criterion.negative:
        geo_by_camp[str(r.campaign.id)].add(gid)
for cid, s in sorted(geo_by_camp.items()):
    print(f"  {NAME[cid]:20s} {len(s)} positive location targets")
union = sorted(set().union(*geo_by_camp.values()))
identical = len({frozenset(v) for v in geo_by_camp.values()}) == 1
print(f"  union across the five: {len(union)}   all five identical: {identical}")
out["geo_targets_per_campaign"] = {NAME[k]: len(v) for k, v in geo_by_camp.items()}
out["geo_union_count"] = len(union)
out["all_five_share_the_same_geo_set"] = identical

print("\n=== 2. RESOLVE EVERY TARGET (name + type + parent) ===")
meta = {}
for i in range(0, len(union), 40):
    batch = ",".join(f"'geoTargetConstants/{g}'" for g in union[i:i + 40])
    for r in q(c, f"""SELECT geo_target_constant.id, geo_target_constant.name,
                             geo_target_constant.canonical_name,
                             geo_target_constant.target_type,
                             geo_target_constant.country_code,
                             geo_target_constant.parent_geo_target,
                             geo_target_constant.status
                      FROM geo_target_constant
                      WHERE geo_target_constant.resource_name IN ({batch})"""):
        g = r.geo_target_constant
        meta[str(g.id)] = {"name": g.name, "canonical": g.canonical_name,
                           "type": E(g.target_type), "country": g.country_code,
                           "parent": g.parent_geo_target.split("/")[-1]
                           if g.parent_geo_target else None,
                           "status": E(g.status)}
types = Counter(v["type"] for v in meta.values())
print(f"  resolved {len(meta)}/{len(union)}")
print(f"  target types: {dict(types)}")
for t in sorted(types):
    ex = [v["canonical"] for v in meta.values() if v["type"] == t][:6]
    print(f"    {t:16s} {types[t]:>3}  e.g. {ex}")
out["geo_target_types"] = dict(types)
out["geo_resolved"] = meta

print("\n=== 3. OVERLAP / CONTAINMENT DETECTION ===")
targeted = set(meta)
contained = []
for gid, v in meta.items():
    p = v["parent"]
    chain = []
    while p:
        chain.append(p)
        pv = meta.get(p)
        p = pv["parent"] if pv else None
        if len(chain) > 6:
            break
    inside = [x for x in chain if x in targeted]
    if inside:
        contained.append({"child": gid, "child_name": v["canonical"],
                          "child_type": v["type"],
                          "inside_targeted_parents": [
                              {"id": x, "name": meta[x]["canonical"],
                               "type": meta[x]["type"]} for x in inside]})
print(f"  targets that sit INSIDE another targeted area: {len(contained)}")
for x in contained[:15]:
    print(f"    {x['child_name']} ({x['child_type']}) inside "
          f"{[p['name'] for p in x['inside_targeted_parents']]}")
if not contained:
    print("  -> no containment. Every target is a peer, so no area is double-counted")
    print("     by inclusion. Planner values still must not be summed across areas,")
    print("     because Keyword Planner models each area independently.")
out["containment_overlaps"] = contained

print("\n=== 4. NON-OVERLAPPING PLANNER GEOGRAPHY ===")
# Peer city-level targets: pick the 10 largest / most representative to represent the
# service area. Report as a SAMPLE of the area, never as the whole-area total.
cities = [g for g, v in meta.items() if v["type"] == "CITY"]
PREF = ["Columbia,Maryland", "Annapolis,Maryland", "Glen Burnie,Maryland",
        "Ellicott City,Maryland", "Severn,Maryland", "Severna Park,Maryland",
        "Bowie,Maryland", "Laurel,Maryland", "Catonsville,Maryland", "Odenton,Maryland"]
sample, sample_names = [], []
for want in PREF:
    for g in union:
        if meta.get(g, {}).get("canonical", "").startswith(want) and g not in sample:
            sample.append(g); sample_names.append(meta[g]["canonical"]); break
for g in union:
    if len(sample) >= 10:
        break
    if g not in sample:
        sample.append(g); sample_names.append(meta[g]["canonical"])
print(f"  Planner geo batch (10 of {len(union)} live targets, peer CITY level, "
      f"no containment):")
for g, n in zip(sample, sample_names):
    print(f"    {g}  {n}")
out["planner_geo_batch"] = [{"id": g, "canonical": n} for g, n in zip(sample, sample_names)]
out["planner_geo_note"] = (
    f"10 of {len(union)} live targets. KeywordPlanIdeaService caps geo_target_constants "
    f"at 10. These 10 are peer CITY-level targets with zero containment between them, so "
    f"the batch is internally non-overlapping. The result is a SAMPLE of the service area, "
    f"NOT the whole-area total, and must not be scaled up by 75/10.")

print("\n=== 5. KEYWORD PLANNER: HEATING CLUSTERS ===")
svc = c.get_service("KeywordPlanIdeaService")
BATCHES = {
    "furnace_repair": ["furnace repair", "furnace repair near me", "gas furnace repair",
                       "furnace not working", "furnace repair service",
                       "oil furnace repair", "furnace repair cost", "emergency furnace repair",
                       "furnace technician near me", "residential furnace repair"],
    "heating_repair": ["heating repair", "heating repair near me", "no heat repair",
                       "heater repair near me", "heating system repair",
                       "emergency heating repair", "heating service near me",
                       "heat not working", "furnace and heating repair",
                       "heating contractor near me"],
    "furnace_install_replace": ["furnace installation", "furnace replacement",
                                "new furnace cost", "furnace replacement cost",
                                "furnace installation near me", "replace furnace",
                                "new furnace installation", "oil furnace installation",
                                "gas furnace installation", "furnace installers near me"],
    "heating_install_replace": ["heating installation", "heating system installation",
                                "heating replacement", "heating system replacement",
                                "new heating system", "heating installation near me",
                                "heating system cost", "install heating system",
                                "replace heating system", "heating installers near me"],
    "boiler": ["boiler repair", "boiler repair near me", "gas boiler repair",
               "boiler installation", "boiler replacement", "new boiler cost",
               "boiler service near me", "boiler replacement cost",
               "residential boiler repair", "boiler installers near me"],
    "heat_pump": ["heat pump repair", "heat pump installation", "heat pump replacement",
                  "heat pump repair near me", "heat pump installers near me",
                  "heat pump cost", "ductless mini split installation",
                  "mini split installation", "mini split installers near me",
                  "ductless heating installation"],
    "maintenance_thermostat": ["furnace maintenance", "furnace tune up",
                               "heating maintenance", "heating tune up",
                               "heating system inspection", "hvac tune up near me",
                               "thermostat installation", "thermostat replacement",
                               "smart thermostat installation", "thermostat repair"],
}
res, raw = {}, {}
for label, seeds in BATCHES.items():
    try:
        req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
        req.customer_id = CID
        req.keywords.extend(seeds)
        req.language = "languageConstants/1000"
        req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in sample])
        req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        t0 = datetime.datetime.now(TZ)
        resp = svc.generate_keyword_historical_metrics(request=req)
        rows = []
        for r in resp.results:
            m = r.keyword_metrics
            monthly = [{"year": v.year, "month": E(v.month),
                        "searches": v.monthly_searches} for v in m.monthly_search_volumes]
            rows.append({
                "keyword": r.text,
                "avg_monthly_searches": m.avg_monthly_searches,
                "competition": E(m.competition),
                "competition_index": m.competition_index,
                "low_top_of_page_bid_micros": m.low_top_of_page_bid_micros or None,
                "high_top_of_page_bid_micros": m.high_top_of_page_bid_micros or None,
                "low_top_of_page_bid_usd": round(m.low_top_of_page_bid_micros/1e6, 2)
                if m.low_top_of_page_bid_micros else None,
                "high_top_of_page_bid_usd": round(m.high_top_of_page_bid_micros/1e6, 2)
                if m.high_top_of_page_bid_micros else None,
                "close_variants": list(r.close_variants)[:8],
                "monthly_search_volumes": monthly,
                "retrieved_local": t0.isoformat()})
        res[label] = rows
        raw[label] = rows
        print(f"\n  --- {label} ({len(rows)} rows) ---")
        print(f"  {'avg/mo':>7} {'comp':>11} {'TOPlow':>8} {'TOPhigh':>8}  keyword")
        for x in sorted(rows, key=lambda y: -(y["avg_monthly_searches"] or 0)):
            print(f"  {x['avg_monthly_searches'] or 0:>7} {x['competition']:>11} "
                  f"{str(x['low_top_of_page_bid_usd']):>8} "
                  f"{str(x['high_top_of_page_bid_usd']):>8}  {x['keyword']}")
    except Exception as ex:
        res[label] = {"error": str(ex)[:600], "endpoint":
                      "KeywordPlanIdeaService.GenerateKeywordHistoricalMetrics"}
        print(f"\n  --- {label} FAILED ---")
        print(f"      {str(ex)[:400]}")
    time.sleep(5)
out["planner"] = res

print("\n=== 6. SEASONALITY: Sep-Mar monthly volume for the top heating terms ===")
seas = {}
for label, rows in res.items():
    if isinstance(rows, dict):
        continue
    for x in rows:
        mv = {f"{m['year']}-{m['month']}": m["searches"]
              for m in x["monthly_search_volumes"]}
        if mv:
            seas[x["keyword"]] = mv
if seas:
    top = sorted(seas, key=lambda k: -max(seas[k].values()))[:12]
    months = sorted({m for k in top for m in seas[k]})[-14:]
    print(f"  {'keyword':34s} " + " ".join(f"{m[-9:][:7]:>7}" for m in months))
    for k in top:
        print(f"  {k[:34]:34s} " + " ".join(f"{seas[k].get(m, 0):>7}" for m in months))
out["monthly_seasonality"] = seas

EXPORTS.mkdir(parents=True, exist_ok=True)
p = EXPORTS / f"keyword-planner-heating-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
cp = EXPORTS / f"keyword-planner-heating-{STAMP}.csv"
with cp.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["cluster", "keyword", "avg_monthly_searches", "competition",
                "competition_index", "low_top_bid_usd", "high_top_bid_usd",
                "low_top_bid_micros", "high_top_bid_micros", "retrieved_local"])
    for label, rows in res.items():
        if isinstance(rows, dict):
            continue
        for x in rows:
            w.writerow([label, x["keyword"], x["avg_monthly_searches"], x["competition"],
                        x["competition_index"], x["low_top_of_page_bid_usd"],
                        x["high_top_of_page_bid_usd"], x["low_top_of_page_bid_micros"],
                        x["high_top_of_page_bid_micros"], x["retrieved_local"]])
gp = EXPORTS / f"geo-crosswalk-{STAMP}.csv"
with gp.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geo_id", "canonical_name", "target_type", "parent_id", "status",
                "in_planner_batch", "inside_another_targeted_area"])
    cset = {x["child"] for x in contained}
    for g in union:
        v = meta.get(g, {})
        w.writerow([g, v.get("canonical"), v.get("type"), v.get("parent"),
                    v.get("status"), g in sample, g in cset])
print(f"\nWROTE {p}\nWROTE {cp}\nWROTE {gp}")
print("EXTERNAL WRITES: 0")
