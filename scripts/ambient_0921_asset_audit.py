#!/usr/bin/env python3
"""Ambient | 2026-09-21 | What assets are linked to the heating campaigns, and what the two
new campaigns would be missing.

READ-ONLY. EXTERNAL WRITES: 0.

The expansion plan links only the call asset and the business-name asset to the two new
campaigns. The instruction also asks for callouts, structured snippets and service-specific
sitelinks. This establishes what the comparable live campaigns actually carry, so the gap is
stated against real precedent rather than against a generic checklist.
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
    "24132507744": "Gas Boiler Repair (enabled)",
    "24132507747": "HVAC Installation (enabled)",
    "24132507750": "HVAC Repair (enabled)",
    "24132507753": "HVAC Replacement (enabled)",
    "24257819463": "Heating Repair (paused)",
    "24257819466": "Heating Installation (paused)",
}


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    print("=== CAMPAIGN ASSET LINKS BY TYPE ===")
    links = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign_asset.asset,
                     campaign_asset.field_type, campaign_asset.status,
                     asset.id, asset.type, asset.name,
                     asset.callout_asset.callout_text,
                     asset.sitelink_asset.link_text,
                     asset.structured_snippet_asset.header,
                     asset.structured_snippet_asset.values,
                     asset.call_asset.phone_number,
                     asset.text_asset.text
                     FROM campaign_asset
                     WHERE campaign_asset.status != 'REMOVED'
                       AND campaign.status != 'REMOVED'"""):
        cid = str(r.campaign.id)
        if cid not in WATCH:
            continue
        a = r.asset
        label = (a.callout_asset.callout_text or a.sitelink_asset.link_text
                 or a.structured_snippet_asset.header
                 or a.call_asset.phone_number
                 or a.text_asset.text or a.name or "")
        links.setdefault(cid, {}).setdefault(E(r.campaign_asset.field_type), []).append(
            {"asset_id": str(a.id), "status": E(r.campaign_asset.status), "text": label})
    for cid, label in WATCH.items():
        d = links.get(cid, {})
        tot = sum(len(v) for v in d.values())
        print(f"\n   {cid}  {label}   {tot} links")
        for ft, items in sorted(d.items()):
            texts = ", ".join(sorted({i['text'][:26] for i in items}))[:110]
            print(f"      {ft:22s} x{len(items):2d}  {texts}")
    out["campaign_asset_links"] = links

    # What the two heating campaigns carry is the precedent for the two new ones.
    ref = {ft: len(v) for ft, v in links.get("24257819463", {}).items()}
    print(f"\n   PRECEDENT (Heating Repair 24257819463): {ref}")
    out["precedent_heating_repair"] = ref

    types_on_heating = set(links.get("24257819463", {})) | set(links.get("24257819466", {}))
    planned_on_new = {"CALL", "BUSINESS_NAME"}
    gap = sorted(types_on_heating - planned_on_new)
    print(f"   field types on the 2026-09-17 heating campaigns: {sorted(types_on_heating)}")
    print(f"   field types the plan links to the 2 NEW campaigns: {sorted(planned_on_new)}")
    print(f"   GAP (present on heating, absent from the plan): {gap}")
    out["asset_gap_on_new_campaigns"] = gap

    print("\n=== ACCOUNT-LEVEL (customer) ASSET LINKS ===")
    cust = {}
    for r in q(c, """SELECT customer_asset.asset, customer_asset.field_type,
                     customer_asset.status, asset.id, asset.type, asset.name
                     FROM customer_asset WHERE customer_asset.status != 'REMOVED'"""):
        cust.setdefault(E(r.customer_asset.field_type), []).append(str(r.asset.id))
    for ft, ids in sorted(cust.items()):
        print(f"   {ft:22s} x{len(ids)}")
    out["customer_level_assets"] = {k: len(v) for k, v in cust.items()}
    print("   NOTE: account-level links serve on every campaign that has no campaign-level "
          "override of the same type.")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"asset-audit-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
