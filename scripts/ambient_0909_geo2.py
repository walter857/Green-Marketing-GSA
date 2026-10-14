#!/usr/bin/env python3
"""Resolve geo target constants + list every location target on the five campaigns."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

# --- every geo criterion on the five campaigns ---
print("=== LOCATION TARGETS ON THE FIVE CAMPAIGNS ===")
geo = []
ids = set()
for r in q(c, f"""
    SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type,
           campaign_criterion.negative, campaign_criterion.status,
           campaign_criterion.location.geo_target_constant,
           campaign_criterion.proximity.radius,
           campaign_criterion.proximity.geo_point.longitude_in_micro_degrees,
           campaign_criterion.proximity.geo_point.latitude_in_micro_degrees
    FROM campaign_criterion
    WHERE campaign.id IN ({IN5})
      AND campaign_criterion.type IN ('LOCATION','PROXIMITY','LOCATION_GROUP')
"""):
    x = r.campaign_criterion
    gid = x.location.geo_target_constant.split("/")[-1] if x.location.geo_target_constant else None
    if gid:
        ids.add(gid)
    geo.append({"camp": str(r.campaign.id), "crit": str(x.criterion_id), "type": E(x.type_),
                "negative": x.negative, "status": E(x.status), "geo_id": gid,
                "radius": x.proximity.radius})
out["campaign_geo_criteria"] = geo
print("rows:", len(geo))
print("by (campaign, type, negative):",
      dict(Counter((NAME[g["camp"]], g["type"], g["negative"]) for g in geo)))

# --- resolve names ---
names = {}
idlist = sorted(ids | {"21153", "21133", "21151", "21158", "21184", "21140", "21167", "21176",
                       "21142", "21171", "2840"})
for i in range(0, len(idlist), 200):
    chunk = idlist[i:i + 200]
    inlist = ",".join(f"'geoTargetConstants/{g}'" for g in chunk)
    for r in q(c, f"""
        SELECT geo_target_constant.id, geo_target_constant.name,
               geo_target_constant.canonical_name, geo_target_constant.country_code,
               geo_target_constant.target_type, geo_target_constant.status
        FROM geo_target_constant
        WHERE geo_target_constant.resource_name IN ({inlist})
    """):
        g = r.geo_target_constant
        names[str(g.id)] = {"name": g.name, "canonical": g.canonical_name,
                            "country": g.country_code, "type": g.target_type,
                            "status": E(g.status)}
out["geo_names"] = names

print("\n--- delivery locations observed, resolved ---")
for gid in ["21153", "21133", "21151", "21158", "21184", "21140", "21167", "21176", "21142", "21171"]:
    n = names.get(gid, {})
    print(f"  {gid:<8} {n.get('canonical', '??'):<50} type={n.get('type')} country={n.get('country')}")

print("\n--- all distinct targeted locations on the five (should be 75 per campaign) ---")
percamp = defaultdict(list)
for g in geo:
    if g["type"] == "LOCATION" and not g["negative"]:
        percamp[g["camp"]].append(g["geo_id"])
for cid, lst in percamp.items():
    print(f"  {NAME[cid]:<20} positive LOCATION targets = {len(lst)}")
uniq = sorted({g for lst in percamp.values() for g in lst})
print(f"  distinct geo ids across the five: {len(uniq)}")
nonmd = []
for gid in uniq:
    n = names.get(gid, {})
    can = n.get("canonical", "")
    if ",Maryland,United States" not in can and can != "Maryland,United States":
        nonmd.append((gid, can, n.get("type")))
print(f"  targets NOT inside Maryland: {len(nonmd)}")
for gid, can, t in nonmd:
    print(f"    {gid:<10} {can}  ({t})")
print("\n  first 20 Maryland targets:")
for gid in uniq[:20]:
    print(f"    {gid:<10} {names.get(gid, {}).get('canonical')}  ({names.get(gid, {}).get('type')})")

print("\n--- negative / excluded locations ---")
neg = [g for g in geo if g["negative"]]
print("  count:", len(neg))
for g in neg:
    print(f"    {NAME[g['camp']]:<20} {g['type']:<12} {g['geo_id']} "
          f"{names.get(g['geo_id'], {}).get('canonical')}")

write(EVID / "2026-09-09-geo-targets.json", out)
