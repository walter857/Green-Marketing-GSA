#!/usr/bin/env python3
"""Ambient | 2026-09-21b | Keyword Planner + account-history research for the 31 services.

READ-ONLY. EXTERNAL WRITES: 0.

Two independent sources, reconciled, never mixed:

  A. KEYWORD PLANNER for Ambient's real service area. Geo targets are capped at 10 per
     call and the seed list at 20 terms, and the endpoint has its own quota that 429s
     quickly, so the 75-target footprint is sampled with the 10 largest places and the
     result is reported as a SAMPLE, never scaled to all 75.

  B. THE ACCOUNT'S OWN HISTORY. Every search term that has ever converted, bucketed to one
     of the 31 services. This outranks Planner volume: it is realised demand for this
     advertiser in this market, not a national estimate.

Planner volumes are forecasts of demand, not historical results for this account, and
close variants collapse into one volume bucket, so identical figures across synonyms are
one bucket reported repeatedly rather than additive demand.
"""
from __future__ import annotations
import sys, json, re, time, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21b"

# 10 largest places in the verified 75-target footprint. Planner caps geo at 10.
GEO_SAMPLE_NAMES = ["Columbia", "Glen Burnie", "Annapolis", "Severn", "Severna Park",
                    "Odenton", "Pasadena", "Catonsville", "Ellicott City", "Laurel"]

# Seed groups, <= 20 terms each, one call per group.
SEEDS = {
    "furnace_repair": ["furnace repair", "furnace repair near me", "gas furnace repair",
                       "electric furnace repair", "furnace not working", "furnace fix"],
    "furnace_install_replace": ["furnace installation", "furnace replacement",
                                "new furnace cost", "replace furnace", "furnace install"],
    "furnace_maintenance": ["furnace maintenance", "furnace tune up",
                            "furnace cleaning", "furnace service"],
    "heating_repair": ["heating repair", "heating repair near me", "heater repair",
                       "no heat", "no heat repair", "emergency heating repair",
                       "emergency heat repair", "heating service"],
    "heating_install_replace": ["heating installation", "heating replacement",
                                "heating system replacement", "heating system installation",
                                "new heating system"],
    "heating_maintenance": ["heating maintenance", "heating tune up",
                            "heating system inspection", "heating inspection"],
    "heat_pump": ["heat pump repair", "heat pump replacement", "heat pump installation",
                  "heat pump maintenance", "heat pump service", "heat pump not heating"],
    "ductless": ["ductless heating repair", "ductless heating installation",
                 "mini split repair", "mini split installation", "ductless mini split"],
    "boiler": ["boiler repair", "boiler replacement", "boiler installation",
               "boiler maintenance", "boiler service", "gas boiler repair"],
    "thermostat": ["thermostat repair", "thermostat replacement",
                   "smart thermostat installation", "thermostat installation",
                   "nest thermostat installation"],
    "geothermal": ["geothermal heat pump", "geothermal heating",
                   "geothermal installation", "geothermal hvac"],
}

# Bucket account search terms to the 31 services. First match wins, most specific first.
BUCKETS = [
    ("Geothermal Heat Pump", re.compile(r"geothermal", re.I)),
    ("Smart Thermostat Installation",
     re.compile(r"(smart|nest|ecobee).*(thermostat)|thermostat.*(install)", re.I)),
    ("Thermostat Replacement", re.compile(r"thermostat.*(replac|new)", re.I)),
    ("Thermostat Repair", re.compile(r"thermostat", re.I)),
    ("Ductless Heating Installation",
     re.compile(r"(ductless|mini ?split).*(install|replac|new|cost)", re.I)),
    ("Ductless Heating Repair", re.compile(r"ductless|mini ?split", re.I)),
    ("Heat Pump Maintenance",
     re.compile(r"heat ?pump.*(maintenance|tune|clean|inspect)", re.I)),
    ("Heat Pump Replacement", re.compile(r"heat ?pump.*(replac|new)", re.I)),
    ("Heat Pump Installation", re.compile(r"heat ?pump.*(install)", re.I)),
    ("Heat Pump Repair", re.compile(r"heat ?pump", re.I)),
    ("Boiler Maintenance", re.compile(r"boiler.*(maintenance|tune|clean|inspect|service)", re.I)),
    ("Boiler Replacement", re.compile(r"boiler.*(replac|new)", re.I)),
    ("Boiler Installation", re.compile(r"boiler.*(install)", re.I)),
    ("Boiler Repair", re.compile(r"boiler", re.I)),
    ("Gas Furnace Repair", re.compile(r"gas furnace", re.I)),
    ("Electric Furnace Repair", re.compile(r"electric furnace", re.I)),
    ("Furnace Tune-Up", re.compile(r"furnace.*(tune)", re.I)),
    ("Furnace Maintenance", re.compile(r"furnace.*(maintenance|clean|service|inspect)", re.I)),
    ("Furnace Replacement", re.compile(r"furnace.*(replac|new)", re.I)),
    ("Furnace Installation", re.compile(r"furnace.*(install)", re.I)),
    ("Furnace Repair", re.compile(r"furnace", re.I)),
    ("No Heat Repair", re.compile(r"\bno heat\b|not heating|won'?t heat", re.I)),
    ("Emergency Heating Repair", re.compile(r"emergency|24 ?hour|same day|urgent", re.I)),
    ("Heating System Inspection", re.compile(r"heat(ing)?.*(inspect)", re.I)),
    ("Heating Tune-Up", re.compile(r"heat(ing)?.*(tune)", re.I)),
    ("Heating Maintenance", re.compile(r"heat(ing)?.*(maintenance|clean|service)", re.I)),
    ("Heating System Replacement", re.compile(r"heating system.*(replac)", re.I)),
    ("Heating System Installation", re.compile(r"heating system.*(install)", re.I)),
    ("Heating Replacement", re.compile(r"heat(ing|er)?.*(replac|new)", re.I)),
    ("Heating Installation", re.compile(r"heat(ing|er)?.*(install)", re.I)),
    ("Heating Repair", re.compile(r"heat(ing|er)?", re.I)),
]


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0,
           "planner_is_forecast_not_history": True,
           "planner_geo_is_a_sample_not_all_75": True}

    # ---------------------------------------------------- resolve geo targets
    gtc = c.get_service("GeoTargetConstantService")
    geo_ids, geo_named = [], {}
    for nm in GEO_SAMPLE_NAMES:
        req = c.get_type("SuggestGeoTargetConstantsRequest")
        req.locale = "en"
        req.country_code = "US"
        req.location_names.names.append(nm)
        try:
            resp = gtc.suggest_geo_target_constants(request=req)
        except Exception as ex:
            print(f"   geo suggest failed for {nm}: {str(ex)[:120]}")
            continue
        # Match canonical_name exactly - the top suggestion by reach is often the wrong
        # place entirely, so never take rank order.
        want = f"{nm},Maryland,United States"
        hit = next((r for r in resp.geo_target_constant_suggestions
                    if r.geo_target_constant.canonical_name.replace(", ", ",") == want), None)
        if hit is None:
            print(f"   no exact canonical match for {nm}; skipped")
            continue
        gid = hit.geo_target_constant.resource_name
        geo_ids.append(gid)
        geo_named[nm] = {"resource": gid,
                         "canonical": hit.geo_target_constant.canonical_name}
    print(f"=== GEO SAMPLE RESOLVED: {len(geo_ids)}/10 ===")
    for nm, v in geo_named.items():
        print(f"   {nm:16s} {v['canonical']}")
    out["geo_sample"] = geo_named
    assert len(geo_ids) <= 10, "Planner caps geo_target_constants at 10"

    # ------------------------------------------------------- Keyword Planner
    print("\n=== KEYWORD PLANNER (sample geo, en, Google Search) ===")
    svc = c.get_service("KeywordPlanIdeaService")
    planner = {}
    for group, seeds in SEEDS.items():
        req = c.get_type("GenerateKeywordIdeasRequest")
        req.customer_id = CID
        req.language = c.get_service("GoogleAdsService").language_constant_path("1000")
        req.geo_target_constants.extend(geo_ids)
        req.include_adult_keywords = False
        req.keyword_plan_network = (
            c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH)
        req.keyword_seed.keywords.extend(seeds[:20])
        rows = []
        try:
            for idea in svc.generate_keyword_ideas(request=req):
                m = idea.keyword_idea_metrics
                rows.append({"text": idea.text,
                             "avg_monthly_searches": m.avg_monthly_searches,
                             "competition": E(m.competition),
                             "low_bid": round(m.low_top_of_page_bid_micros / 1e6, 2),
                             "high_bid": round(m.high_top_of_page_bid_micros / 1e6, 2)})
        except Exception as ex:
            rows = [{"error": str(ex)[:220]}]
            print(f"   {group:26s} FAILED {str(ex)[:110]}")
            time.sleep(2)
        planner[group] = rows
        ok = [r for r in rows if "error" not in r]
        if ok:
            ok.sort(key=lambda x: -x["avg_monthly_searches"])
            print(f"   {group:26s} {len(ok):4d} ideas; top: " +
                  ", ".join(f"{r['text']}({r['avg_monthly_searches']})" for r in ok[:4]))
        time.sleep(1)
    out["planner"] = planner

    # ------------------------------------------- account history by service
    print("\n=== ACCOUNT SEARCH-TERM HISTORY, BUCKETED TO THE 31 SERVICES ===")
    buckets = {}
    total_terms = 0
    for r in q(c, """SELECT search_term_view.search_term, metrics.clicks,
                     metrics.cost_micros, metrics.conversions, metrics.impressions
                     FROM search_term_view
                     WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-21'"""):
        t = r.search_term_view.search_term.lower()
        total_terms += 1
        svc_name = next((n for n, rx in BUCKETS if rx.search(t)), None)
        if not svc_name:
            continue
        a = buckets.setdefault(svc_name, {"terms": 0, "clicks": 0, "cost": 0.0,
                                          "conv": 0.0, "impr": 0, "converting_terms": 0})
        a["terms"] += 1
        a["clicks"] += r.metrics.clicks
        a["cost"] += r.metrics.cost_micros / 1e6
        a["conv"] += r.metrics.conversions
        a["impr"] += r.metrics.impressions
        if r.metrics.conversions > 0:
            a["converting_terms"] += 1
    for k, a in buckets.items():
        a["cost"] = round(a["cost"], 2)
        a["conv"] = round(a["conv"], 2)
        a["cpc"] = round(a["cost"] / a["clicks"], 2) if a["clicks"] else None
        a["cpa"] = round(a["cost"] / a["conv"], 2) if a["conv"] else None
    print(f"   {total_terms} search-term rows scanned; raw terms NOT retained")
    print(f"   {'service':34s} {'terms':>6s} {'clicks':>7s} {'cost':>10s} "
          f"{'conv':>7s} {'CPC':>8s} {'CPA':>9s}")
    for k, a in sorted(buckets.items(), key=lambda x: -x[1]["conv"]):
        print(f"   {k:34s} {a['terms']:6d} {a['clicks']:7d} {a['cost']:10.2f} "
              f"{a['conv']:7.2f} {str(a['cpc']):>8s} {str(a['cpa']):>9s}")
    out["account_history_by_service"] = buckets
    out["raw_search_terms_retained"] = False

    SERVICES = [n for n, _ in BUCKETS]
    missing = [s for s in SERVICES if s not in buckets]
    out["services_with_no_account_history"] = missing
    print(f"\n   services with NO account search-term history ({len(missing)}): {missing}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"keyword-research-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
