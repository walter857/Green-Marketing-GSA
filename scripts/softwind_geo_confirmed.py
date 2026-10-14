#!/usr/bin/env python3
"""Confirmed geo configuration - READ-ONLY state capture.

Walter confirmed on 2026-08-26:
  positive  = all VALID New York locations in the geo-union report
  exclusion = Connecticut, United States
  setting   = Presence (people in or regularly in), unchanged
  scope     = both Power Washing campaigns
  no other state or country exclusions without evidence

This script only READS. It builds no operations and calls no mutate service.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.google_ads import enum_name                     # noqa: E402

CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "geo-confirmed-2026-08-26.json"
UNION = SNAP / "geo-union-2026-08-26.json"

Q_IDENTITY = """
SELECT customer.id, customer.descriptive_name, customer.manager,
       customer.test_account, customer.currency_code, customer.time_zone
FROM customer LIMIT 1
"""

Q_SETTING = """
SELECT campaign.id, campaign.name, campaign.status,
       campaign.geo_target_type_setting.positive_geo_target_type,
       campaign.geo_target_type_setting.negative_geo_target_type
FROM campaign WHERE campaign.status != 'REMOVED'
"""

Q_CRITERIA = """
SELECT campaign.id, campaign_criterion.criterion_id,
       campaign_criterion.type, campaign_criterion.negative,
       campaign_criterion.status,
       campaign_criterion.location.geo_target_constant
FROM campaign_criterion
WHERE campaign_criterion.type = 'LOCATION'
  AND campaign.status != 'REMOVED'
"""

Q_GEO = """
SELECT geo_target_constant.id, geo_target_constant.name,
       geo_target_constant.canonical_name, geo_target_constant.status,
       geo_target_constant.target_type, geo_target_constant.country_code
FROM geo_target_constant
WHERE geo_target_constant.resource_name IN (%s)
"""


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    gts = client.get_service("GeoTargetConstantService")
    out = {"generated": "2026-08-26", "read_only": True}

    # ---- identity gate -------------------------------------------------
    for row in svc.search(customer_id=CID, query=Q_IDENTITY):
        c = row.customer
        out["identity"] = {
            "id": str(c.id), "name": c.descriptive_name,
            "name_ok": c.descriptive_name == NAME, "id_ok": str(c.id) == CID,
            "manager": c.manager, "test_account": c.test_account,
            "currency": c.currency_code, "time_zone": c.time_zone}
    g = out["identity"]
    if not (g["name_ok"] and g["id_ok"] and not g["manager"]
            and not g["test_account"]):
        print("IDENTITY GATE FAILED")
        return 1

    # ---- current geo target type setting -------------------------------
    settings = {}
    for row in svc.search(customer_id=CID, query=Q_SETTING):
        cp = row.campaign
        settings[str(cp.id)] = {
            "name": cp.name, "status": enum_name(cp.status),
            "positive_geo_target_type": enum_name(
                cp.geo_target_type_setting.positive_geo_target_type),
            "negative_geo_target_type": enum_name(
                cp.geo_target_type_setting.negative_geo_target_type)}
    out["current_geo_target_type_setting"] = settings

    # ---- current LOCATION criteria, positive and negative --------------
    current = {cid: {"positive": [], "negative": []} for cid in CAMPAIGNS}
    for row in svc.search(customer_id=CID, query=Q_CRITERIA):
        cid = str(row.campaign.id)
        cc = row.campaign_criterion
        if cid not in current:
            continue
        gid = cc.location.geo_target_constant.split("/")[-1]
        bucket = "negative" if cc.negative else "positive"
        current[cid][bucket].append({
            "criterion_id": str(cc.criterion_id),
            "geo_target_constant_id": gid,
            "status": enum_name(cc.status)})
    out["current_location_criteria"] = current

    # ---- validate every NY constant in the union report ----------------
    union = json.loads(UNION.read_text(encoding="utf-8"))
    uu = union["unique_union"]
    ny_ids = sorted(set(uu["current_footprint_ids"])
                    | set(uu["proposed_union_unique_ids"]))
    cond = ",".join("'geoTargetConstants/%s'" % i for i in ny_ids)
    resolved = {}
    for row in svc.search(customer_id=CID, query=Q_GEO % cond):
        gc = row.geo_target_constant
        resolved[str(gc.id)] = {
            "id": str(gc.id), "name": gc.name,
            "canonical_name": gc.canonical_name,
            "status": enum_name(gc.status), "target_type": gc.target_type,
            "country_code": gc.country_code}

    valid, invalid = [], []
    for i in ny_ids:
        r = resolved.get(i)
        if r is None:
            invalid.append({"id": i, "reason": "did not resolve"})
            continue
        if r["status"] != "ENABLED":
            invalid.append({"id": i, "reason": "status %s" % r["status"],
                            "name": r["canonical_name"]})
            continue
        if r["country_code"] != "US" or ",New York," not in r["canonical_name"] + ",":
            invalid.append({"id": i, "reason": "not a New York, US location",
                            "name": r["canonical_name"]})
            continue
        valid.append(r)
    out["ny_validation"] = {"checked": len(ny_ids), "valid": valid,
                            "invalid": invalid, "all_valid": not invalid}

    # ---- resolve the Connecticut exclusion constant ---------------------
    req = client.get_type("SuggestGeoTargetConstantsRequest")
    req.locale = "en"
    req.country_code = "US"
    req.location_names.names.extend(["Connecticut"])
    ct = []
    try:
        resp = gts.suggest_geo_target_constants(request=req)
        for s in resp.geo_target_constant_suggestions:
            gc = s.geo_target_constant
            ct.append({"id": str(gc.id), "name": gc.name,
                       "canonical_name": gc.canonical_name,
                       "target_type": gc.target_type,
                       "status": enum_name(gc.status),
                       "country_code": gc.country_code,
                       "reach": int(s.reach) if s.reach else None})
    except Exception as exc:                                   # noqa: BLE001
        out["connecticut_suggest_error"] = str(exc)[:300]
    exact = [c for c in ct
             if c["canonical_name"] == "Connecticut,United States"
             and c["target_type"] == "State" and c["status"] == "ENABLED"]
    out["connecticut"] = {"all_suggestions": ct, "exact_match": exact,
                          "resolved_unambiguously": len(exact) == 1}

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("IDENTITY  %s  %s  manager=%s test=%s  %s"
          % (g["name"], g["id"], g["manager"], g["test_account"], g["time_zone"]))
    print()
    print("GEO TARGET TYPE SETTING (must stay Presence)")
    for cid, s in settings.items():
        print("   %-13s %-18s positive=%-28s negative=%s"
              % (cid, s["name"], s["positive_geo_target_type"],
                 s["negative_geo_target_type"]))
    print()
    print("CURRENT LOCATION CRITERIA")
    for cid, b in current.items():
        print("   %-13s %-18s positive=%d  negative=%d"
              % (cid, CAMPAIGNS[cid], len(b["positive"]), len(b["negative"])))
    print()
    print("NEW YORK VALIDATION  checked=%d valid=%d invalid=%d"
          % (len(ny_ids), len(valid), len(invalid)))
    for v in valid:
        already = {cid: any(p["geo_target_constant_id"] == v["id"]
                            for p in current[cid]["positive"])
                   for cid in CAMPAIGNS}
        print("   %-10s %-11s %-42s A=%-5s B=%s"
              % (v["id"], v["target_type"], v["canonical_name"][:42],
                 already["24103511039"], already["24145053510"]))
    for iv in invalid:
        print("   INVALID %s" % iv)
    print()
    print("CONNECTICUT  suggestions=%d  exact=%d  unambiguous=%s"
          % (len(ct), len(exact), out["connecticut"]["resolved_unambiguously"]))
    for c in ct[:6]:
        print("   %-10s %-11s %-34s status=%s reach=%s"
              % (c["id"], c["target_type"], c["canonical_name"][:34],
                 c["status"], c["reach"]))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
