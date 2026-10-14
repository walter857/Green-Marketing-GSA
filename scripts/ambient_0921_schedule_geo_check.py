#!/usr/bin/env python3
"""Ambient | 2026-09-21 | What ad schedule and geo targeting the live campaigns actually carry.

READ-ONLY. EXTERNAL WRITES: 0.

client.yaml records required_campaign_delivery = "24 hours a day, 7 days a week on
all five campaigns" and puts the Mon-Fri 08:00-20:00 / Sat 08:00-13:00 hours on the
CALL ASSET instead. The 2026-09 heating instruction asks for an "approved
business-hour schedule" on the heating campaigns. Those two are not the same thing,
so the live state decides what "approved" currently means in this account.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21"
WATCH = {
    "24132507741": "AC Repair (enabled)",
    "24132507744": "Gas Boiler Repair (enabled, will host Boiler Repair)",
    "24132507747": "HVAC Installation (enabled)",
    "24132507750": "HVAC Repair (enabled)",
    "24132507753": "HVAC Replacement (enabled)",
    "24257819463": "Heating Repair (paused, built 2026-09-17)",
    "24257819466": "Heating Installation (paused, built 2026-09-17)",
}


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    print("=== AD SCHEDULE CRITERIA PER CAMPAIGN ===")
    sched = {}
    for r in q(c, """SELECT campaign.id, campaign.name,
                     campaign_criterion.criterion_id,
                     campaign_criterion.ad_schedule.day_of_week,
                     campaign_criterion.ad_schedule.start_hour,
                     campaign_criterion.ad_schedule.start_minute,
                     campaign_criterion.ad_schedule.end_hour,
                     campaign_criterion.ad_schedule.end_minute,
                     campaign_criterion.bid_modifier, campaign_criterion.status
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = 'AD_SCHEDULE'
                       AND campaign.status != 'REMOVED'"""):
        a = r.campaign_criterion.ad_schedule
        sched.setdefault(str(r.campaign.id), []).append({
            "day": E(a.day_of_week), "start": f"{a.start_hour:02d}:{E(a.start_minute)}",
            "end": f"{a.end_hour:02d}:{E(a.end_minute)}",
            "bid_modifier": r.campaign_criterion.bid_modifier,
            "status": E(r.campaign_criterion.status)})
    for cid, label in WATCH.items():
        rows = sched.get(cid, [])
        print(f"\n   {cid}  {label}")
        if not rows:
            print("      NO ad schedule rows -> delivers 24/7")
        for x in sorted(rows, key=lambda y: y["day"]):
            print(f"      {x['day']:10s} {x['start']}-{x['end']}  "
                  f"mod={x['bid_modifier']}  {x['status']}")
    out["ad_schedule_by_campaign"] = {k: sched.get(k, []) for k in WATCH}
    out["campaigns_with_no_schedule_24_7"] = [k for k in WATCH if not sched.get(k)]
    out["campaigns_with_schedule"] = {k: len(sched.get(k, [])) for k in WATCH
                                      if sched.get(k)}

    print("\n=== GEO TARGETING PER CAMPAIGN ===")
    geo = {}
    for r in q(c, """SELECT campaign.id, campaign_criterion.criterion_id,
                     campaign_criterion.location.geo_target_constant,
                     campaign_criterion.negative, campaign_criterion.type
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = 'LOCATION'
                       AND campaign.status != 'REMOVED'"""):
        k = str(r.campaign.id)
        g = geo.setdefault(k, {"positive": [], "negative": []})
        gid = r.campaign_criterion.location.geo_target_constant.rsplit("/", 1)[-1]
        g["negative" if r.campaign_criterion.negative else "positive"].append(gid)
    for cid, label in WATCH.items():
        g = geo.get(cid, {"positive": [], "negative": []})
        print(f"   {cid}  pos={len(g['positive']):3d}  neg={len(g['negative']):3d}  {label}")
    out["geo_by_campaign"] = {k: {"positive": len(geo.get(k, {}).get("positive", [])),
                                  "negative": len(geo.get(k, {}).get("negative", []))}
                              for k in WATCH}

    # The plan copies the geo set and the schedule from the two heating campaigns
    # built on 2026-09-17, so those are the ones that define "approved".
    ref_geo = sorted(geo.get("24257819463", {}).get("positive", []))
    print(f"\n   reference geo set (Heating Repair 24257819463): {len(ref_geo)} targets")
    same = {cid: sorted(geo.get(cid, {}).get("positive", [])) == ref_geo for cid in WATCH}
    print(f"   campaigns whose positive geo set matches it exactly: "
          f"{[k for k, v in same.items() if v]}")
    out["reference_geo_count"] = len(ref_geo)
    out["geo_matches_reference"] = same

    print("\n=== NETWORK / EXPANSION SETTINGS ===")
    net = {}
    for r in q(c, """SELECT campaign.id, campaign.name,
                     campaign.network_settings.target_google_search,
                     campaign.network_settings.target_search_network,
                     campaign.network_settings.target_content_network,
                     campaign.network_settings.target_partner_search_network,
                     campaign.geo_target_type_setting.positive_geo_target_type,
                     campaign.geo_target_type_setting.negative_geo_target_type
                     FROM campaign WHERE campaign.status != 'REMOVED'"""):
        if str(r.campaign.id) not in WATCH:
            continue
        n = r.campaign.network_settings
        net[str(r.campaign.id)] = {
            "google_search": n.target_google_search,
            "search_partners": n.target_search_network,
            "display": n.target_content_network,
            "partner_search": n.target_partner_search_network,
            "pos_geo": E(r.campaign.geo_target_type_setting.positive_geo_target_type),
            "neg_geo": E(r.campaign.geo_target_type_setting.negative_geo_target_type)}
    for cid, v in net.items():
        print(f"   {cid}  search={v['google_search']} partners={v['search_partners']} "
              f"display={v['display']} geo={v['pos_geo']}/{v['neg_geo']}")
    out["network_settings"] = net
    out["any_search_partners_on"] = any(v["search_partners"] for v in net.values())
    out["any_display_on"] = any(v["display"] for v in net.values())

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"schedule-geo-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
