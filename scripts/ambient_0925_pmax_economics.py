#!/usr/bin/env python3
"""Ambient | 2026-09-25 | READ-ONLY economics for the service allocation + PMax pilot decision.

Google Ads: every campaign (any status) by month since 2025-06-01, bucketed by service from the
campaign name; PMax conversions by conversion action (contamination check).
WhatConverts: leads 2025-06-01..2026-09-25, QA leads excluded via client.yaml, aggregated by
month x paid/other x service (from lead_analysis topic text) x quotable. COUNTS ONLY, no PII.
"""
from __future__ import annotations
import sys, json, re, collections, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, CLIENT_DIR
from gm_gsa.whatconverts import fetch_leads

c = client(); identity_gate(c, verbose=False)
out = {"when": datetime.datetime.now(TZ).isoformat()}

def bucket(name: str) -> str:
    n = name.lower()
    if "performance max" in n or "pmax" in n: return "PMAX:" + name.split("-")[-1].strip()[:28]
    if "commercial" in n: return "commercial"
    if re.search(r"geotherm", n): return "geothermal"
    if re.search(r"maint|tune|inspection", n): return "heating_maintenance"
    if re.search(r"thermostat", n): return "thermostat"
    if re.search(r"heat pump|ductless|mini split", n): return "heat_pump_ductless"
    if re.search(r"boiler", n): return "boiler"
    if re.search(r"water heater|tankless", n): return "water_heater"
    if re.search(r"(heating|furnace).*(install|replace)|install.*(heat|furnace)", n): return "heating_install_replace"
    if re.search(r"heating|furnace", n): return "heating_repair"
    if re.search(r"hvac (install|replace)", n): return "hvac_install_replace"
    if re.search(r"ac |a/c|cool|air cond|hvac", n): return "cooling_hvac"
    return "other:" + name[:30]

rows = q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
        segments.month, metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions,
        metrics.all_conversions FROM campaign WHERE segments.date BETWEEN '2025-06-01' AND '2026-09-25'
        AND metrics.impressions > 0""")
mon = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0, 0.0]))
names = {}
for r in rows:
    b = bucket(r.campaign.name); names[str(r.campaign.id)] = (r.campaign.name, E(r.campaign.status), E(r.campaign.advertising_channel_type), b)
    a = mon[b][r.segments.month[:7]]
    a[0] += r.metrics.cost_micros / 1e6; a[1] += r.metrics.clicks; a[2] += r.metrics.conversions
out["spend_by_bucket_month"] = {b: {m: [round(v[0], 2), v[1], round(v[2], 1)] for m, v in sorted(d.items())} for b, d in mon.items()}
print("SPEND by service bucket x month (cost, clicks, conv) 2025-06..2026-09:")
for b, d in sorted(out["spend_by_bucket_month"].items()):
    tot = [round(sum(v[0] for v in d.values()), 2), sum(v[1] for v in d.values()), round(sum(v[2] for v in d.values()), 1)]
    print(f"  {b:34s} total {tot}  " + " ".join(f"{m[2:]}:{int(v[0])}" for m, v in d.items()))

# PMax all-time by conversion action
PM = ["22822619680", "23883756382", "22855140165", "22379067302"]
pm = {}
for cid in PM:
    life = q(c, f"""SELECT campaign.id, campaign.name, metrics.cost_micros, metrics.clicks, metrics.impressions,
            metrics.conversions, metrics.all_conversions FROM campaign WHERE campaign.id = {cid} AND segments.date BETWEEN '2023-01-01' AND '2026-09-25'""")
    cost = sum(r.metrics.cost_micros for r in life) / 1e6
    by_act = collections.Counter(); by_act_all = collections.Counter()
    for r in q(c, f"""SELECT segments.conversion_action_name, metrics.conversions, metrics.all_conversions FROM campaign
            WHERE campaign.id = {cid} AND segments.date BETWEEN '2023-01-01' AND '2026-09-25'"""):
        by_act[r.segments.conversion_action_name] += r.metrics.conversions
        by_act_all[r.segments.conversion_action_name] += r.metrics.all_conversions
    months = sorted({r.segments.month[:7] for r in q(c, f"SELECT segments.month, metrics.cost_micros FROM campaign WHERE campaign.id = {cid} AND segments.date BETWEEN '2023-01-01' AND '2026-09-25' AND metrics.cost_micros > 0")})
    pm[cid] = dict(name=names.get(cid, ("?",))[0], cost=round(cost, 2), clicks=sum(r.metrics.clicks for r in life),
                   impr=sum(r.metrics.impressions for r in life), conv=round(sum(r.metrics.conversions for r in life), 1),
                   months=f"{months[0]}..{months[-1]}" if months else "-",
                   conv_by_action={k: round(v, 1) for k, v in by_act.most_common()},
                   allconv_by_action={k: round(v, 1) for k, v in by_act_all.most_common(8)})
out["pmax_history"] = pm
print("\nPMAX HISTORY (all time):")
for k, v in pm.items():
    print(f"  {k} {v['name'][:45]:45s} {v['months']} ${v['cost']} {v['clicks']}cl {v['conv']}cv -> CPA {round(v['cost']/v['conv'],2) if v['conv'] else '-'}")
    print(f"      conv by action: {v['conv_by_action']}")
# PMax channel/asset-group signals (asset group status + policy)
for r in q(c, f"""SELECT campaign.id, asset_group.id, asset_group.name, asset_group.status, asset_group.primary_status,
        asset_group.primary_status_reasons, asset_group.final_urls FROM asset_group WHERE campaign.id IN ({','.join(PM)})"""):
    print(f"  AG {r.campaign.id} {r.asset_group.id} {r.asset_group.name[:40]} {E(r.asset_group.status)} {E(r.asset_group.primary_status)} {[E(x) for x in r.asset_group.primary_status_reasons]} {list(r.asset_group.final_urls)[:1]}")

# WhatConverts
wc = {"leads": [], "qa_excluded": [], "raw_count": 0}
for a, b in (("2025-06-01", "2026-01-31"), ("2026-02-01", "2026-09-25")):
    part = fetch_leads("115814", "105803", a, b, client_yaml=CLIENT_DIR / "client.yaml")
    wc["leads"] += part["leads"]; wc["qa_excluded"] += part["qa_excluded"]; wc["raw_count"] += part["raw_count"]
leads = wc["leads"]
SVC = [
    ("maintenance", r"maint|tune[\s-]?up|inspection|clean|service plan|check[\s-]?up"),
    ("ductless", r"ductless|mini[\s-]?split"),
    ("geothermal", r"geotherm"),
    ("boiler", r"boiler|radiator|hot water heat"),
    ("heat_pump", r"heat pump"),
    ("thermostat", r"thermostat"),
    ("install_replace", r"install|replac|new (system|unit|furnace|hvac)|estimate|quote"),
    ("heating_repair", r"furnace|heat(ing)?\b|no heat|pilot|ignit|burner"),
    ("cooling", r"\bac\b|a/c|air condition|cooling|compressor|condenser"),
]
def svc(l):
    t = json.dumps(l.get("lead_analysis") or "") + " " + json.dumps(l.get("additional_fields") or "")
    for k, rx in SVC:
        if re.search(rx, t, re.I): return k
    return "unclassified"
def paid(l):
    med = str(l.get("lead_medium") or "").lower(); src = str(l.get("lead_source") or "").lower()
    has_click = bool(l.get("gclid") or l.get("gbraid") or l.get("wbraid"))
    if has_click: return "paid_click_id"
    if med == "cpc" and "google" in src: return "paid_label_only"
    if "lsa" in src or "local services" in src: return "lsa"
    return "other"
agg = collections.defaultdict(lambda: collections.Counter())
season = lambda m: "heat_2025_26" if "2025-10" <= m <= "2026-03" else ("cool_2026" if "2026-04" <= m <= "2026-09" else "pre")
for l in leads:
    m = str(l.get("date_created", ""))[:7]
    key = (season(m), paid(l), svc(l))
    agg[key]["leads"] += 1
    agg[key]["q_" + str(l.get("quotable"))] += 1
    agg[key]["type_" + str(l.get("lead_type"))] += 1
    if l.get("sales_value"): agg[key]["has_sales_value"] += 1
out["wc_raw"] = wc["raw_count"]; out["wc_qa_excluded"] = len(wc["qa_excluded"])
out["wc_agg"] = {"|".join(k): dict(v) for k, v in agg.items()}
print(f"\nWHATCONVERTS {wc['raw_count']} raw, {len(wc['qa_excluded'])} QA excluded, {len(leads)} kept")
for k in sorted(agg):
    if k[1] in ("paid_click_id", "paid_label_only"):
        v = agg[k]; print(f"  {k[0]:12s} {k[1]:15s} {k[2]:16s} leads {v['leads']:3d} quotable Yes {v['q_Yes']} No {v['q_No']} other {v['leads']-v['q_Yes']-v['q_No']} | forms {v['type_Web Form']} calls {v['type_Phone Call']}")
tot = collections.Counter()
for k, v in agg.items(): tot[(k[0], k[1])] += v["leads"]
print("  totals by season x path:", dict(tot))
(SNAP / "pmax-economics-2026-09-25.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
