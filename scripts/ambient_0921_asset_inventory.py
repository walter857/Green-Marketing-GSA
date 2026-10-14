#!/usr/bin/env python3
"""Ambient | 2026-09-21 | Reusable CALLOUT / SITELINK / STRUCTURED_SNIPPET inventory.

READ-ONLY. EXTERNAL WRITES: 0.

The two new campaigns in AMB-0921-HEAT-EXPAND-1 would launch with only CALL and
BUSINESS_NAME, while every comparable campaign in the account carries five callouts, a
structured snippet and three to eight sitelinks. This lists what already exists so the gap
is closed by REUSING assets rather than minting duplicates, and flags which sitelink targets
are safe (a sitelink pointing at the destination-blocked heat-pumps URL must not be used).
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21"
BLOCKED_URL = "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/"
HEATING_REF = ("24257819463", "24257819466")


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    # Which assets the two 2026-09-17 heating campaigns already use -> the reuse set.
    on_heating = {}
    for r in q(c, """SELECT campaign.id, campaign.status, campaign_asset.asset,
                     campaign_asset.field_type, campaign_asset.status, asset.id
                     FROM campaign_asset
                     WHERE campaign_asset.status != 'REMOVED'
                       AND campaign.status != 'REMOVED'"""):
        if str(r.campaign.id) in HEATING_REF:
            on_heating.setdefault(E(r.campaign_asset.field_type), set()).add(str(r.asset.id))
    out["assets_on_existing_heating_campaigns"] = {k: sorted(v)
                                                   for k, v in on_heating.items()}

    print("=== CALLOUT ASSETS ===")
    co = {}
    for r in q(c, """SELECT asset.id, asset.callout_asset.callout_text, asset.type
                     FROM asset WHERE asset.type = 'CALLOUT'"""):
        co[str(r.asset.id)] = r.asset.callout_asset.callout_text
    used = on_heating.get("CALLOUT", set())
    for aid, t in sorted(co.items(), key=lambda x: x[1]):
        mark = " <- on heating campaigns" if aid in used else ""
        print(f"   {aid:16s} {t[:44]:44s}{mark}")
    out["callout_assets"] = co
    print(f"   total {len(co)}; {len(used)} already on the heating campaigns")

    print("\n=== STRUCTURED SNIPPET ASSETS ===")
    ss = {}
    for r in q(c, """SELECT asset.id, asset.structured_snippet_asset.header,
                     asset.structured_snippet_asset.values, asset.type
                     FROM asset WHERE asset.type = 'STRUCTURED_SNIPPET'"""):
        ss[str(r.asset.id)] = {"header": r.asset.structured_snippet_asset.header,
                               "values": list(r.asset.structured_snippet_asset.values)}
    used = on_heating.get("STRUCTURED_SNIPPET", set())
    for aid, v in ss.items():
        mark = " <- on heating campaigns" if aid in used else ""
        print(f"   {aid:16s} {v['header']:18s} {', '.join(v['values'])[:60]}{mark}")
    out["structured_snippet_assets"] = ss

    print("\n=== SITELINK ASSETS ===")
    sl = {}
    for r in q(c, """SELECT asset.id, asset.sitelink_asset.link_text,
                     asset.sitelink_asset.description1,
                     asset.sitelink_asset.description2,
                     asset.final_urls, asset.type
                     FROM asset WHERE asset.type = 'SITELINK'"""):
        sl[str(r.asset.id)] = {
            "text": r.asset.sitelink_asset.link_text,
            "d1": r.asset.sitelink_asset.description1,
            "d2": r.asset.sitelink_asset.description2,
            "urls": list(r.asset.final_urls)}
    used = on_heating.get("SITELINK", set())
    for aid, v in sorted(sl.items(), key=lambda x: x[1]["text"]):
        u = v["urls"][0] if v["urls"] else ""
        flag = ""
        if u.rstrip("/") == BLOCKED_URL.rstrip("/"):
            flag = "  *** POINTS AT THE DESTINATION-BLOCKED URL - DO NOT USE ***"
        elif aid in used:
            flag = "  <- on heating campaigns"
        print(f"   {aid:16s} {v['text'][:26]:26s} {u[:62]:62s}{flag}")
    out["sitelink_assets"] = sl
    out["sitelinks_pointing_at_blocked_url"] = [
        aid for aid, v in sl.items()
        if v["urls"] and v["urls"][0].rstrip("/") == BLOCKED_URL.rstrip("/")]
    print(f"   total {len(sl)}; {len(used)} already on the heating campaigns; "
          f"{len(out['sitelinks_pointing_at_blocked_url'])} point at the blocked URL")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"asset-inventory-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
