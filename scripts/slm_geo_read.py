#!/usr/bin/env python3
"""Read-only: pull LOCATION campaign criteria for Softwind Landscape & Masonry.

The search-term corpus pull only fetches negative KEYWORD criteria, so the
service area was never captured. classify() mints GEO_OUT_OF_AREA negatives from
geo_out, so guessing the area would mint destructive negatives. This reads it.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "2429758629"
EXPECT_NAME = "Softwind Landscape & Masonry - Live"

def main() -> int:
    load_dotenv_if_available()
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")

    # identity re-gate from inside the account
    idr = list(svc.search(customer_id=CID, query=(
        "SELECT customer.id, customer.descriptive_name, customer.manager, "
        "customer.test_account FROM customer LIMIT 1")))[0]
    obs = idr.customer.descriptive_name
    ok = (obs == EXPECT_NAME and str(idr.customer.id) == CID
          and not idr.customer.manager and not idr.customer.test_account)
    print("identity: observed '{}' / {} -> {}".format(obs, idr.customer.id,
                                                      "PASS" if ok else "FAIL"))
    if not ok:
        return 1

    rows = list(svc.search(customer_id=CID, query=(
        "SELECT campaign.id, campaign.name, campaign.status, "
        "campaign_criterion.criterion_id, campaign_criterion.type, "
        "campaign_criterion.negative, "
        "campaign_criterion.location.geo_target_constant, "
        "campaign_criterion.proximity.radius, "
        "campaign_criterion.proximity.radius_units, "
        "campaign_criterion.proximity.address.city_name, "
        "campaign_criterion.proximity.address.province_code, "
        "campaign_criterion.proximity.address.postal_code "
        "FROM campaign_criterion "
        "WHERE campaign_criterion.type IN ('LOCATION','PROXIMITY')")))

    out = []
    gtc_ids = set()
    for r in rows:
        cc = r.campaign_criterion
        t = enum_name(cc.type_)
        rec = {"campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
               "campaign_status": enum_name(r.campaign.status),
               "criterion_id": str(cc.criterion_id), "type": t,
               "negative": bool(cc.negative)}
        if t == "LOCATION":
            gtc = cc.location.geo_target_constant or ""
            rec["geo_target_constant"] = gtc
            rec["gtc_id"] = gtc.rsplit("/", 1)[-1] if gtc else ""
            if rec["gtc_id"]:
                gtc_ids.add(rec["gtc_id"])
        else:
            rec["proximity"] = {
                "radius": cc.proximity.radius,
                "units": enum_name(cc.proximity.radius_units),
                "city": cc.proximity.address.city_name,
                "province": cc.proximity.address.province_code,
                "postal_code": cc.proximity.address.postal_code}
        out.append(rec)

    # resolve geo target constant names
    names = {}
    if gtc_ids:
        res = ",".join("'geoTargetConstants/{}'".format(i) for i in sorted(gtc_ids))
        for r in svc.search(customer_id=CID, query=(
                "SELECT geo_target_constant.id, geo_target_constant.name, "
                "geo_target_constant.canonical_name, "
                "geo_target_constant.target_type, "
                "geo_target_constant.country_code FROM geo_target_constant "
                "WHERE geo_target_constant.resource_name IN ({})".format(res))):
            g = r.geo_target_constant
            names[str(g.id)] = {"name": g.name, "canonical": g.canonical_name,
                                "target_type": g.target_type,
                                "country": g.country_code}
    for rec in out:
        if rec.get("gtc_id"):
            rec["resolved"] = names.get(rec["gtc_id"], {})

    # also read location settings (presence vs interest)
    settings = []
    for r in svc.search(customer_id=CID, query=(
            "SELECT campaign.id, campaign.name, campaign.status, "
            "campaign.geo_target_type_setting.positive_geo_target_type, "
            "campaign.geo_target_type_setting.negative_geo_target_type "
            "FROM campaign")):
        settings.append({
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "status": enum_name(r.campaign.status),
            "positive": enum_name(r.campaign.geo_target_type_setting.positive_geo_target_type),
            "negative": enum_name(r.campaign.geo_target_type_setting.negative_geo_target_type)})

    dest = ROOT / "clients" / "softwind-landscape-masonry" / "snapshots" / "geo-read-2026-08-30.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"customer_id": CID, "account_name": obs,
                                "criteria": out, "geo_settings": settings},
                               indent=2), encoding="utf-8")

    print("\nLOCATION / PROXIMITY criteria: {}".format(len(out)))
    for rec in sorted(out, key=lambda x: (x["campaign_name"], x["type"])):
        if rec["type"] == "LOCATION":
            rs = rec.get("resolved", {})
            print("  {:<18} {:<9} {:<8} {:<40} {}".format(
                rec["campaign_name"][:18], rec["campaign_status"][:9],
                "EXCLUDE" if rec["negative"] else "target",
                rs.get("canonical", "?")[:40], rs.get("target_type", "")))
        else:
            p = rec["proximity"]
            print("  {:<18} {:<9} {:<8} PROXIMITY {} {} around {} {} {}".format(
                rec["campaign_name"][:18], rec["campaign_status"][:9],
                "EXCLUDE" if rec["negative"] else "target",
                p["radius"], p["units"], p["city"], p["province"], p["postal_code"]))

    print("\nGEO TARGET TYPE SETTINGS")
    for s in settings:
        print("  {:<18} {:<9} positive={} negative={}".format(
            s["campaign_name"][:18], s["status"][:9], s["positive"], s["negative"]))
    print("\nwritten -> {}".format(dest.relative_to(ROOT)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
