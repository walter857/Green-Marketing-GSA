#!/usr/bin/env python3
"""Read-only geo target constant resolution for Softwind. SELECT-only."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "geo-resolution-2026-08-25.json"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    ids = set()
    deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
    for c in deep["campaign_criteria"]:
        if c["type"] == "LOCATION":
            ids.add(c["geo_target_constant"].split("/")[-1])
    met = json.loads((SNAP / "metrics-2026-08-25.json").read_text(encoding="utf-8"))
    for g in met["geographic_view"]:
        for k in ("city", "county", "postal", "metro"):
            v = g.get(k) or ""
            m = re.search(r"geoTargetConstants/(\d+)", v)
            if m:
                ids.add(m.group(1))
    for g in met["user_location_view"]:
        for k in ("city", "postal"):
            m = re.search(r"geoTargetConstants/(\d+)", g.get(k) or "")
            if m:
                ids.add(m.group(1))

    resolved = {}
    id_list = sorted(ids)
    for i in range(0, len(id_list), 50):
        chunk = id_list[i:i + 50]
        cond = ",".join("'geoTargetConstants/%s'" % x for x in chunk)
        q = """
          SELECT geo_target_constant.id, geo_target_constant.name,
                 geo_target_constant.canonical_name,
                 geo_target_constant.country_code,
                 geo_target_constant.target_type,
                 geo_target_constant.status,
                 geo_target_constant.resource_name
          FROM geo_target_constant
          WHERE geo_target_constant.resource_name IN (%s)
        """ % cond
        for row in svc.search(customer_id=CID, query=q):
            g = row.geo_target_constant
            resolved[str(g.id)] = {
                "id": str(g.id), "name": g.name,
                "canonical_name": g.canonical_name,
                "country_code": g.country_code,
                "target_type": g.target_type,
                "status": enum_name(g.status),
            }

    targeted = []
    for c in deep["campaign_criteria"]:
        if c["type"] == "LOCATION":
            gid = c["geo_target_constant"].split("/")[-1]
            targeted.append({
                "campaign": c["campaign_name"], "geo_id": gid,
                "negative": c["negative"],
                **resolved.get(gid, {"canonical_name": "UNRESOLVED"}),
            })

    out = {"resolved": resolved, "targeted_locations": targeted}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=== TARGETED LOCATIONS ===")
    seen = set()
    for t in targeted:
        if t["geo_id"] in seen:
            continue
        seen.add(t["geo_id"])
        print("  %-10s %-8s %s" % (t["geo_id"], t.get("target_type", "?"),
                                   t.get("canonical_name", "?")))
    print()
    print("=== ALL RESOLVED (%d) ===" % len(resolved))
    for k, v in sorted(resolved.items(), key=lambda x: x[1]["canonical_name"]):
        print("  %-10s %-10s %s" % (k, v["target_type"], v["canonical_name"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
