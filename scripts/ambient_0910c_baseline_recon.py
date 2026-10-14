#!/usr/bin/env python3
"""The 4 failed count assertions: did the account change, or was my baseline scoped
differently? Reproduce the snapshot's own filters instead of counting everything."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
snap = json.load(open(CLIENT_DIR / "snapshots" / "before-state-2026-09-10.json",
                      encoding="utf-8"))

print("=== CAMPAIGNS ===")
allc = q(c, "SELECT campaign.id, campaign.status FROM campaign")
st = Counter(E(r.campaign.status) for r in allc)
print(f"  every campaign row regardless of status : {len(allc)}   {dict(st)}")
nonrem = [r for r in allc if E(r.campaign.status) != "REMOVED"]
print(f"  excluding REMOVED                       : {len(nonrem)}")
print(f"  snapshot 'campaigns' dict               : {len(snap['campaigns'])}")

print("\n=== AD GROUPS ===")
allg = q(c, "SELECT ad_group.id, ad_group.status FROM ad_group")
st = Counter(E(r.ad_group.status) for r in allg)
print(f"  every ad_group row regardless of status : {len(allg)}   {dict(st)}")
print(f"  excluding REMOVED                       : "
      f"{len([r for r in allg if E(r.ad_group.status) != 'REMOVED'])}")
print(f"  snapshot 'ad_groups' list               : {len(snap['ad_groups'])}")

print("\n=== GEO CRITERIA ===")
allgeo = q(c, "SELECT campaign.id, campaign.status, campaign_criterion.criterion_id, "
              "campaign_criterion.status FROM campaign_criterion "
              "WHERE campaign_criterion.type = 'LOCATION'")
print(f"  every LOCATION criterion, all campaigns : {len(allgeo)}")
onfive = [r for r in allgeo if str(r.campaign.id) in FIVE]
print(f"  on the five campaigns only              : {len(onfive)}")
print(f"  on the five, ENABLED only               : "
      f"{len([r for r in onfive if E(r.campaign_criterion.status) == 'ENABLED'])}")
print(f"  snapshot 'geo_criteria' list            : {len(snap['geo_criteria'])}")
print(f"  distinct campaigns carrying geo         : {len({str(r.campaign.id) for r in allgeo})}")

print("\n=== CONVERSION ACTIONS ===")
allca = q(c, "SELECT conversion_action.id, conversion_action.name, "
             "conversion_action.status, conversion_action.type FROM conversion_action")
st = Counter(E(r.conversion_action.status) for r in allca)
print(f"  every conversion_action row             : {len(allca)}   {dict(st)}")
print(f"  excluding REMOVED                       : "
      f"{len([r for r in allca if E(r.conversion_action.status) != 'REMOVED'])}")
print(f"  snapshot 'conversion_actions' list      : {len(snap['conversion_actions'])}")
snapids = {str(x.get('id')) for x in snap['conversion_actions']} if \
    isinstance(snap['conversion_actions'][0], dict) else set()
liveids = {str(r.conversion_action.id) for r in allca}
if snapids:
    print(f"  in snapshot but not live now            : {sorted(snapids - liveids)}")
    extra = sorted(liveids - snapids)
    print(f"  live now but not in snapshot            : {extra}")
    for r in allca:
        if str(r.conversion_action.id) in extra:
            print(f"      {r.conversion_action.id}  {E(r.conversion_action.status):<10}"
                  f"{E(r.conversion_action.type_):<28}{r.conversion_action.name}")

print("\n=== IS ANY OF THIS INSIDE THE FIVE? ===")
for r in q(c, f"SELECT campaign.id, campaign.name, campaign.status FROM campaign "
              f"WHERE campaign.id IN ({IN5})"):
    print(f"  {NAME[str(r.campaign.id)]:<20}{E(r.campaign.status)}")
n5 = len(q(c, f"SELECT ad_group.id FROM ad_group WHERE campaign.id IN ({IN5})"))
print(f"  ad groups under the five: {n5}")
