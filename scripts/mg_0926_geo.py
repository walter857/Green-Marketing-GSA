#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: resolve geo target constants used by the live campaigns and seen in clicks."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import SNAP, client, q  # noqa: E402

OUT = SNAP / "audit-2026-09-26"
c = client()
ids = set()
for r in json.loads((OUT / "campaign_criteria.json").read_text(encoding="utf-8")):
    g = r.get("campaign_criterion", {}).get("location", {}).get("geo_target_constant")
    if g:
        ids.add(g.split("/")[-1])
for r in json.loads((OUT / "click_view_35.json").read_text(encoding="utf-8")):
    for k in ("location_of_presence", "area_of_interest"):
        v = r.get("click_view", {}).get(k, {})
        for f in ("most_specific", "city", "metro", "region", "country"):
            if v.get(f):
                ids.add(v[f].split("/")[-1])
for r in json.loads((OUT / "geo_user_location_90.json").read_text(encoding="utf-8")):
    for f in ("geo_target_city", "geo_target_region"):
        v = r.get("segments", {}).get(f)
        if v:
            ids.add(v.split("/")[-1])
    t = r.get("user_location_view", {}).get("targeting_location")
    if t is not None:
        ids.add(str(t))
ids = {x for x in ids if x.isdigit()}
res = {}
idl = sorted(ids)
for i in range(0, len(idl), 200):
    chunk = ",".join(f"'geoTargetConstants/{x}'" for x in idl[i:i + 200])
    for r in q(c, f"""SELECT geo_target_constant.id, geo_target_constant.canonical_name,
                        geo_target_constant.target_type, geo_target_constant.status
                      FROM geo_target_constant WHERE geo_target_constant.resource_name IN ({chunk})"""):
        g = r.geo_target_constant
        res[str(g.id)] = {"name": g.canonical_name, "type": g.target_type}
(OUT / "geo_names.json").write_text(json.dumps(res, indent=0), encoding="utf-8")
print(f"resolved {len(res)} of {len(ids)} geo ids")
