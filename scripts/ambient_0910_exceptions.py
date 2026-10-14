#!/usr/bin/env python3
"""Which keywords are not ELIGIBLE and which ENABLED ads are not APPROVED, and do they
sit under an ENABLED ad group in an ENABLED campaign (i.e. can they actually serve)?"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
print("=== POSITIVE KEYWORDS ON THE FIVE ===")
print(f"  {'campaign':<20}{'ad group':<16}{'agStatus':<10}{'kwStatus':<9}"
      f"{'approval':<22}{'match':<8}text")
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.status, "
              f"ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
              f"ad_group_criterion.status, ad_group_criterion.approval_status "
              f"FROM ad_group_criterion WHERE campaign.id IN ({IN5}) "
              f"AND ad_group_criterion.type='KEYWORD' AND ad_group_criterion.negative=FALSE "
              f"AND ad_group_criterion.status='ENABLED'"):
    x = r.ad_group_criterion
    print(f"  {NAME[str(r.campaign.id)]:<20}{r.ad_group.id:<16}{E(r.ad_group.status):<10}"
          f"{E(x.status):<9}{E(x.approval_status):<22}{E(x.keyword.match_type):<8}"
          f"{x.keyword.text}")

print("\n=== ENABLED ADS ON THE FIVE ===")
print(f"  {'campaign':<20}{'ad group':<16}{'agStatus':<10}{'ad':<14}{'approval':<14}"
      f"{'strength'}")
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.status, ad_group_ad.ad.id, "
              f"ad_group_ad.status, ad_group_ad.policy_summary.approval_status, "
              f"ad_group_ad.ad_strength FROM ad_group_ad WHERE campaign.id IN ({IN5}) "
              f"AND ad_group_ad.status='ENABLED'"):
    x = r.ad_group_ad
    flag = "" if E(x.policy_summary.approval_status) == "APPROVED" else "   <-- NOT APPROVED"
    print(f"  {NAME[str(r.campaign.id)]:<20}{r.ad_group.id:<16}{E(r.ad_group.status):<10}"
          f"{x.ad.id:<14}{E(x.policy_summary.approval_status):<14}{E(x.ad_strength)}{flag}")

print("\n=== AD GROUPS ON THE FIVE ===")
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status "
              f"FROM ad_group WHERE campaign.id IN ({IN5})"):
    print(f"  {NAME[str(r.campaign.id)]:<20}{r.ad_group.id:<16}"
          f"{E(r.ad_group.status):<10}{r.ad_group.name}")
