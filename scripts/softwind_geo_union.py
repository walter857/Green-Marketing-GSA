#!/usr/bin/env python3
"""Correction 2 - rebuild the geo model as a UNIQUE UNION with parent hierarchy.

Standalone Keyword Planner volumes must NOT be added when locations overlap.
READ-ONLY.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "geo-union-2026-08-26.json"

CURRENT = ["1022729", "1023035", "1023415", "1023482",
           "9051836", "9052792", "9198508", "9214462"]
PROPOSED = ["9198487", "9198014", "9198728", "9220615",
            "9198814", "1023022", "1022748", "1022719"]


def resolve(svc, ids):
    res = {}
    todo = list(dict.fromkeys(ids))
    seen = set()
    # walk up the parent chain so containment can be proven, not assumed
    while todo:
        batch = [i for i in todo[:50] if i not in seen]
        todo = todo[50:]
        if not batch:
            continue
        cond = ",".join("'geoTargetConstants/%s'" % i for i in batch)
        for row in svc.search(customer_id=CID, query="""
            SELECT geo_target_constant.id, geo_target_constant.name,
                   geo_target_constant.canonical_name,
                   geo_target_constant.target_type,
                   geo_target_constant.parent_geo_target,
                   geo_target_constant.country_code,
                   geo_target_constant.status
            FROM geo_target_constant
            WHERE geo_target_constant.resource_name IN (%s)""" % cond):
            g = row.geo_target_constant
            gid = str(g.id)
            seen.add(gid)
            parent = (g.parent_geo_target.split("/")[-1]
                      if g.parent_geo_target else None)
            res[gid] = {"id": gid, "name": g.name,
                        "canonical_name": g.canonical_name,
                        "target_type": g.target_type,
                        "parent_geo_target_id": parent,
                        "country_code": g.country_code,
                        "status": enum_name(g.status)}
            if parent and parent not in seen and parent not in todo:
                todo.append(parent)
    return res


def ancestors(gid, res):
    out, cur, guard = [], res.get(gid, {}).get("parent_geo_target_id"), 0
    while cur and guard < 12:
        out.append(cur)
        cur = res.get(cur, {}).get("parent_geo_target_id")
        guard += 1
    return out


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    res = resolve(svc, CURRENT + PROPOSED)

    out = {"generated": "2026-08-26",
           "rule": ("Standalone Planner volumes are NOT summed across overlapping "
                    "locations. Demand is measured on the UNIQUE UNION only."),
           "resolved": res}

    # hierarchy
    hier = {}
    for gid in CURRENT + PROPOSED:
        g = res.get(gid, {})
        anc = ancestors(gid, res)
        hier[gid] = {
            "canonical_name": g.get("canonical_name"),
            "target_type": g.get("target_type"),
            "status": g.get("status"),
            "parent_id": g.get("parent_geo_target_id"),
            "parent_name": res.get(g.get("parent_geo_target_id") or "", {}).get("canonical_name"),
            "ancestor_ids": anc,
            "ancestor_names": [res.get(a, {}).get("canonical_name") for a in anc],
            "in_current": gid in CURRENT, "in_proposed": gid in PROPOSED,
        }
    out["hierarchy"] = hier

    # containment analysis
    cur_in_prop, prop_in_prop, cur_in_cur = [], [], []
    for c in CURRENT:
        for p in PROPOSED:
            if p in ancestors(c, res):
                cur_in_prop.append({
                    "current_target": res[c]["canonical_name"], "current_id": c,
                    "contained_in_proposed": res[p]["canonical_name"], "proposed_id": p})
    for a in PROPOSED:
        for b in PROPOSED:
            if a != b and b in ancestors(a, res):
                prop_in_prop.append({
                    "proposed_target": res[a]["canonical_name"], "id": a,
                    "contained_in_proposed": res[b]["canonical_name"], "parent_id": b})
    for a in CURRENT:
        for b in CURRENT:
            if a != b and b in ancestors(a, res):
                cur_in_cur.append({
                    "current_target": res[a]["canonical_name"], "id": a,
                    "contained_in_current": res[b]["canonical_name"], "parent_id": b})

    out["containment"] = {
        "current_targets_contained_inside_a_proposed_target": cur_in_prop,
        "proposed_targets_contained_inside_another_proposed_target": prop_in_prop,
        "current_targets_contained_inside_another_current_target": cur_in_cur,
    }

    # target-type / status anomalies
    anomalies = []
    for gid, g in hier.items():
        if g["status"] != "ENABLED":
            anomalies.append({"id": gid, "issue": "status is %s" % g["status"],
                              "name": g["canonical_name"]})
        # a "City" whose canonical name repeats the name is a hamlet-inside-town pattern
        cn = g["canonical_name"] or ""
        parts = [x.strip() for x in cn.split(",")]
        if len(parts) >= 3 and parts[0] == parts[1]:
            anomalies.append({
                "id": gid, "issue": "MISLEADING LABEL - hamlet/place sharing its town name",
                "name": cn, "target_type": g["target_type"],
                "detail": ("Google labels this '%s' but the canonical name repeats the "
                           "town, which is the classic hamlet-inside-town pattern. This "
                           "is exactly the trap behind the Islip finding."
                           % g["target_type"])})
    out["anomalies"] = anomalies

    # unique union
    def unique(ids):
        keep = []
        for i in ids:
            anc = set(ancestors(i, res))
            if any(other in anc for other in ids if other != i):
                continue          # contained in another member of the same set
            keep.append(i)
        return keep

    cur_u = unique(CURRENT)
    prop_all = list(dict.fromkeys(CURRENT + PROPOSED))
    prop_u = unique(prop_all)
    net_new = [i for i in prop_u if i not in cur_u]
    absorbed = [i for i in CURRENT if i not in prop_u]

    out["unique_union"] = {
        "current_footprint_ids": CURRENT,
        "current_unique_ids": cur_u,
        "current_unique_names": [res[i]["canonical_name"] for i in cur_u],
        "current_redundant_within_itself": [
            {"id": i, "name": res[i]["canonical_name"]}
            for i in CURRENT if i not in cur_u],
        "proposed_union_unique_ids": prop_u,
        "proposed_union_unique_names": [res[i]["canonical_name"] for i in prop_u],
        "net_new_unique_ids": net_new,
        "net_new_unique_names": [res[i]["canonical_name"] for i in net_new],
        "current_targets_absorbed_by_a_proposed_parent": [
            {"id": i, "name": res[i]["canonical_name"]} for i in absorbed],
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("HIERARCHY")
    for gid in CURRENT + PROPOSED:
        g = hier[gid]
        tag = "CURRENT " if g["in_current"] else "PROPOSED"
        print("  [%s] %-10s %-13s %-46s parent=%s"
              % (tag, gid, g["target_type"], (g["canonical_name"] or "")[:46],
                 g["parent_name"]))
    print()
    print("CONTAINMENT")
    print("  CURRENT targets inside a PROPOSED target: %d" % len(cur_in_prop))
    for c in cur_in_prop:
        print("     %-34s -> absorbed by %s" % (c["current_target"][:34],
                                                c["contained_in_proposed"]))
    print("  PROPOSED inside another PROPOSED: %d" % len(prop_in_prop))
    for c in prop_in_prop:
        print("     %-34s -> inside %s" % (c["proposed_target"][:34],
                                           c["contained_in_proposed"]))
    print("  CURRENT inside another CURRENT: %d" % len(cur_in_cur))
    for c in cur_in_cur:
        print("     %-34s -> inside %s" % (c["current_target"][:34],
                                           c["contained_in_current"]))
    print()
    print("ANOMALIES: %d" % len(anomalies))
    for a in anomalies:
        print("   %s %s -> %s" % (a["id"], a["name"], a["issue"]))
    print()
    u = out["unique_union"]
    print("UNIQUE UNION")
    print("  current unique footprint : %d of %d ids" % (len(cur_u), len(CURRENT)))
    for n in u["current_unique_names"]:
        print("     %s" % n)
    print("  redundant within current : %s" % u["current_redundant_within_itself"])
    print("  proposed union unique    : %d ids" % len(prop_u))
    for n in u["proposed_union_unique_names"]:
        print("     %s" % n)
    print("  NET-NEW unique ids       : %d" % len(net_new))
    for n in u["net_new_unique_names"]:
        print("     %s" % n)
    print("  current targets absorbed : %s"
          % [x["name"] for x in u["current_targets_absorbed_by_a_proposed_parent"]])
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
