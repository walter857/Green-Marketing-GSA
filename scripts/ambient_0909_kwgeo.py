#!/usr/bin/env python3
"""Keyword-level deep dive + the out-of-state geography question."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

print("=== A. EVERY ad_group_criterion ROW IN THE FIVE, INCLUDING REMOVED ===")
rows = []
for r in q(c, f"""
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group_criterion.negative, ad_group.id, ad_group.status,
           campaign.id
    FROM ad_group_criterion
    WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type = 'KEYWORD'
"""):
    x = r.ad_group_criterion
    rows.append({"crit": str(x.criterion_id), "text": x.keyword.text, "match": E(x.keyword.match_type),
                 "status": E(x.status), "negative": x.negative, "ag": str(r.ad_group.id),
                 "ag_status": E(r.ad_group.status), "camp": str(r.campaign.id)})
out["five_agc_all"] = rows
print("rows:", len(rows))
print(" by (negative, status):", dict(Counter((r["negative"], r["status"]) for r in rows)))
pos = [r for r in rows if not r["negative"]]
print(" POSITIVES by (camp, ag, status):",
      dict(Counter((NAME[r["camp"]], r["ag"], r["status"]) for r in pos)))
print("\n --- every positive row, full list ---")
for r in sorted(pos, key=lambda r: (NAME[r["camp"]], r["status"], r["text"])):
    print(f"   {NAME[r['camp']]:<18} AG={r['ag']}({r['ag_status']:<7}) {r['status']:<8} "
          f"{r['match']:<7} crit={r['crit']:<14} [{r['text']}]")
print("\n --- ad-group NEGATIVES on the five (all 11) ---")
for r in sorted([r for r in rows if r["negative"]], key=lambda r: (NAME[r["camp"]], r["text"])):
    print(f"   {NAME[r['camp']]:<18} AG={r['ag']} {r['status']:<8} {r['match']:<7} [{r['text']}]")

print("\n=== B. KEYWORD_VIEW ALL-TIME PERFORMANCE (five campaigns, incl. removed) ===")
kv = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id,
           ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
           ad_group_criterion.status, {METRICS}
    FROM keyword_view
    WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'
"""):
    d = m(r)
    d.update({"camp": str(r.campaign.id), "ag": str(r.ad_group.id),
              "crit": str(r.ad_group_criterion.criterion_id),
              "text": r.ad_group_criterion.keyword.text,
              "match": E(r.ad_group_criterion.keyword.match_type),
              "status": E(r.ad_group_criterion.status)})
    kv.append(d)
out["keyword_view_all_time"] = kv
print("rows with delivery:", len(kv))
tot = {k: round(sum(x[k] for x in kv), 2) for k in ("impressions", "clicks", "cost", "conversions", "all_conversions")}
print("total:", tot)
for x in sorted(kv, key=lambda x: -x["cost"]):
    print(f"  {NAME[x['camp']]:<18} {x['match']:<7} {x['status']:<8} impr={x['impressions']:<6} "
          f"clicks={x['clicks']:<4} ${x['cost']:<9} cpc=${x['avg_cpc']:<7} conv={x['conversions']:<5} "
          f"allconv={x['all_conversions']:<5} [{x['text']}]")

print("\n=== C. GEOGRAPHIC_VIEW (targeted location = where the ad was targeted) ===")
gv = []
for r in q(c, f"""
    SELECT campaign.id, geographic_view.country_criterion_id,
           geographic_view.location_type, segments.geo_target_region,
           segments.geo_target_state, segments.geo_target_city,
           {METRICS}
    FROM geographic_view
    WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
"""):
    d = m(r)
    d.update({"camp": str(r.campaign.id), "location_type": E(r.geographic_view.location_type),
              "region": r.segments.geo_target_region, "state": r.segments.geo_target_state,
              "city": r.segments.geo_target_city})
    gv.append(d)
out["geographic_view"] = gv
print("rows:", len(gv))
print("by location_type:", dict(Counter(x["location_type"] for x in gv)))
agg = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0})
for x in gv:
    k = (x["location_type"], x["state"] or x["region"] or "?")
    agg[k]["impressions"] += x["impressions"]; agg[k]["clicks"] += x["clicks"]; agg[k]["cost"] += x["cost"]
for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["cost"])[:40]:
    print(f"  {k[0]:<24} {k[1]:<34} impr={v['impressions']:<7} clicks={v['clicks']:<5} ${v['cost']:.2f}")

print("\n=== D. USER_LOCATION_VIEW (where the user actually was) ===")
ul = []
for r in q(c, f"""
    SELECT campaign.id, user_location_view.country_criterion_id,
           user_location_view.targeting_location, segments.geo_target_region,
           segments.geo_target_state, segments.geo_target_city, segments.geo_target_metro,
           {METRICS}
    FROM user_location_view
    WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
"""):
    d = m(r)
    d.update({"camp": str(r.campaign.id),
              "targeting_location": r.user_location_view.targeting_location,
              "country_crit": str(r.user_location_view.country_criterion_id),
              "region": r.segments.geo_target_region, "state": r.segments.geo_target_state,
              "city": r.segments.geo_target_city, "metro": r.segments.geo_target_metro})
    ul.append(d)
out["user_location_view"] = ul
print("rows:", len(ul))
print("by targeting_location flag:", dict(Counter(x["targeting_location"] for x in ul)))
agg2 = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0})
for x in ul:
    agg2[(x["targeting_location"], x["state"] or x["region"] or "?")]["impressions"] += x["impressions"]
    agg2[(x["targeting_location"], x["state"] or x["region"] or "?")]["clicks"] += x["clicks"]
    agg2[(x["targeting_location"], x["state"] or x["region"] or "?")]["cost"] += x["cost"]
for k, v in sorted(agg2.items(), key=lambda kv: -kv[1]["cost"])[:60]:
    print(f"  in_target={str(k[0]):<6} {k[1]:<40} impr={v['impressions']:<7} clicks={v['clicks']:<5} ${v['cost']:.2f}")

write(EVID / "2026-09-09-keywords-and-geo.json", out)
