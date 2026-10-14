#!/usr/bin/env python3
"""2026-09-16 READ-ONLY geo-target resolution for the Apogee Lawns Lincoln service area."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import EVID, client, write, E  # noqa: E402

c = client()
svc = c.get_service("GeoTargetConstantService")

REQUESTED = [
    ("68372", "POSTAL_CODE"), ("68430", "POSTAL_CODE"), ("68527", "POSTAL_CODE"),
    ("68347", "POSTAL_CODE"), ("68526", "POSTAL_CODE"), ("68461", "POSTAL_CODE"),
    ("68516", "POSTAL_CODE"), ("68520", "POSTAL_CODE"),
    ("Waverly, Nebraska", "CITY"), ("Eagle, Nebraska", "CITY"),
    ("Lincoln, Nebraska", "CITY"), ("Ashland Township, Nebraska", "?"),
    ("Crete, Nebraska", "CITY"), ("Nemaha Precinct, Nebraska", "?"),
]

out = {}
print(f"{'REQUESTED':<30} {'ID':>10} {'TYPE':<14} {'STATUS':<8} REACH   CANONICAL")
print("-" * 120)
for term, expect in REQUESTED:
    req = c.get_type("SuggestGeoTargetConstantsRequest")
    req.locale = "en"
    req.country_code = "US"
    req.location_names.names.append(term)
    try:
        resp = svc.suggest_geo_target_constants(request=req)
    except Exception as exc:  # noqa: BLE001
        print(f"{term:<30} SUGGEST FAILED: {type(exc).__name__}")
        out[term] = {"error": str(exc)[:200]}
        continue

    cands = []
    for s in resp.geo_target_constant_suggestions:
        g = s.geo_target_constant
        cands.append({
            "id": str(g.id), "name": g.name, "canonical": g.canonical_name,
            "type": g.target_type, "status": E(g.status),
            "country": g.country_code, "reach": s.reach,
            "locale": s.locale, "search_term": s.search_term,
        })
    cands.sort(key=lambda x: -x["reach"])
    out[term] = {"expected_type": expect, "candidates": cands}
    if not cands:
        print(f"{term:<30} {'NONE':>10} -- NO MATCH --")
        continue
    for i, x in enumerate(cands[:4]):
        mark = "*" if i == 0 else " "
        print(f"{(term if i == 0 else ''):<30}{mark}{x['id']:>9} {x['type']:<14} "
              f"{x['status']:<8} {x['reach']:>7} {x['canonical']}")
    if len(cands) > 4:
        print(f"{'':<30} ... {len(cands) - 4} more candidates")
    print()

# ---- ambiguity / out-of-area flags -------------------------------------
print("\n=== RESOLUTION VERDICT ===")
verdict = {}
for term, expect in REQUESTED:
    rec = out.get(term) or {}
    cands = rec.get("candidates") or []
    if not cands:
        verdict[term] = "NO_MATCH -- cannot target"
    else:
        top = cands[0]
        ne = "Nebraska" in top["canonical"]
        typ_ok = (expect == "?") or (top["type"] == expect)
        exact_name_hits = [x for x in cands
                           if x["canonical"].lower().startswith(term.split(",")[0].strip().lower())]
        amb = len([x for x in cands if x["type"] == top["type"] and "Nebraska" in x["canonical"]]) > 1
        flags = []
        if not ne:
            flags.append("NOT_IN_NEBRASKA")
        if not typ_ok:
            flags.append(f"TYPE={top['type']}_EXPECTED_{expect}")
        if amb:
            flags.append("MULTIPLE_NE_CANDIDATES")
        verdict[term] = {
            "id": top["id"], "canonical": top["canonical"], "type": top["type"],
            "reach": top["reach"], "flags": flags or ["OK"],
            "alt_count": len(cands),
        }
    print(f"  {term:<30} {verdict[term]}")

out["_verdict"] = verdict
write(EVID / "2026-09-16-geo-resolution.json", out)
