#!/usr/bin/env python3
"""Ambient | Call-asset schedule + link exclusivity, before any schedule change.

READ-ONLY. EXTERNAL WRITES: 0.

CallAsset.ad_schedule_targets lives on the ASSET, not on the link. Editing the schedule
rewrites the hours on EVERY campaign the asset is linked to. So exclusivity has to be
proven before the schedule is touched, or a change meant for heating silently rewrites
hours on something else.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-22"
CALL_ASSET = "407995613637"


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    print("=== CALL ASSETS IN THE ACCOUNT ===")
    assets = {}
    for r in q(c, """SELECT asset.id, asset.type, asset.call_asset.phone_number,
                     asset.call_asset.country_code,
                     asset.call_asset.ad_schedule_targets,
                     asset.call_asset.call_conversion_reporting_state,
                     asset.policy_summary.approval_status
                     FROM asset WHERE asset.type = 'CALL'"""):
        a = r.asset
        sched = [{"day": E(t.day_of_week),
                  "start": f"{t.start_hour:02d}:{E(t.start_minute)}",
                  "end": f"{t.end_hour:02d}:{E(t.end_minute)}"}
                 for t in a.call_asset.ad_schedule_targets]
        assets[str(a.id)] = {"phone": a.call_asset.phone_number,
                             "country": a.call_asset.country_code,
                             "schedule": sched,
                             "schedule_rows": len(sched),
                             "conv_reporting": E(a.call_asset.call_conversion_reporting_state),
                             "approval": E(a.policy_summary.approval_status)}
    for k, v in assets.items():
        mark = "  <<< THE ONE IN USE" if k == CALL_ASSET else ""
        print(f"   {k:16s} {v['phone']:18s} rows={v['schedule_rows']:2d} "
              f"{v['approval']:12s}{mark}")
    out["call_assets"] = assets

    tgt = assets.get(CALL_ASSET, {})
    print(f"\n=== ASSET {CALL_ASSET} SCHEDULE (this is what would be rewritten) ===")
    if not tgt.get("schedule"):
        print("   NO ad_schedule_targets -> the call asset serves whenever its campaign does")
    for s in sorted(tgt.get("schedule", []), key=lambda x: x["day"]):
        print(f"   {s['day']:10s} {s['start']}-{s['end']}")

    print(f"\n=== EVERY LINK TO ASSET {CALL_ASSET} ===")
    links = []
    for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                      campaign_asset.field_type, campaign_asset.status, asset.id
                      FROM campaign_asset
                      WHERE asset.id = {CALL_ASSET}"""):
        links.append({"campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
                      "campaign_status": E(r.campaign.status),
                      "link_status": E(r.campaign_asset.status),
                      "field_type": E(r.campaign_asset.field_type)})
    for l in links:
        print(f"   {l['campaign_id']}  {l['campaign_status']:8s} {l['link_status']:8s} "
              f"{l['campaign'][:54]}")
    out["campaign_links"] = links
    live = [l for l in links if l["link_status"] != "REMOVED"]

    cust = []
    for r in q(c, f"""SELECT customer_asset.field_type, customer_asset.status, asset.id
                      FROM customer_asset WHERE asset.id = {CALL_ASSET}"""):
        cust.append({"field_type": E(r.customer_asset.field_type),
                     "status": E(r.customer_asset.status)})
    out["customer_level_links"] = cust
    ag = []
    for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group_asset.status, asset.id
                      FROM ad_group_asset WHERE asset.id = {CALL_ASSET}"""):
        ag.append({"ad_group_id": str(r.ad_group.id), "status": E(r.ad_group_asset.status)})
    out["ad_group_links"] = ag

    print(f"\n   non-removed campaign links : {len(live)}")
    print(f"   customer-level links       : {len(cust)}")
    print(f"   ad-group-level links       : {len(ag)}")
    outside = [l for l in live if l["campaign_id"] not in
               ("24132507741", "24132507744", "24132507747", "24132507750",
                "24132507753", "24257819463", "24257819466")]
    out["links_outside_the_in_scope_campaigns"] = outside
    print(f"   links OUTSIDE the in-scope campaigns: {len(outside)}")
    for l in outside:
        print(f"      {l['campaign_id']} {l['campaign'][:56]}")
    out["exclusive_to_in_scope_campaigns"] = not outside and not cust and not ag
    print(f"\n   EXCLUSIVE to in-scope campaigns: "
          f"{out['exclusive_to_in_scope_campaigns']}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"call-asset-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
