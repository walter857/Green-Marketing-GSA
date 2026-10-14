#!/usr/bin/env python3
"""Final read-only state check. Confirms what is live right now matches the report."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
identity_gate(c, verbose=True)
print("\n=== LIVE STATE OF THE FIVE, 2026-09-10 ===")
tot = 0.0
for r in q(c, f"SELECT campaign.id, campaign.status, campaign_budget.amount_micros, "
              f"campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign.bidding_strategy_type FROM campaign WHERE campaign.id IN ({IN5}) "
              f"ORDER BY campaign.id"):
    b = r.campaign_budget.amount_micros/1e6
    ceil = r.campaign.target_spend.cpc_bid_ceiling_micros
    tot += b
    print(f"  {NAME[str(r.campaign.id)]:<20}{E(r.campaign.status):<9}"
          f"budget ${b:>7.2f}/day   ceiling "
          f"{('$%.2f' % (ceil/1e6)) if ceil else 'UNCAPPED':<10}"
          f"{E(r.campaign.bidding_strategy_type)}")
print(f"\n  combined daily ${tot:.2f}  x 30.4 = ${tot*30.4:,.2f}  "
      f"headroom ${13000 - tot*30.4:,.2f} under $13,000")
assert tot*30.4 <= 13000, "CHARGING LIMIT BREACH"
print("  [PASS] within the $13,000 monthly charging limit")

n = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
             f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='KEYWORD' "
             f"AND campaign_criterion.negative=TRUE"))
print(f"\n  campaign negatives on the five: {n}")
kw = q(c, f"SELECT ad_group_criterion.keyword.text, ad_group_criterion.status, "
          f"ad_group_criterion.approval_status FROM ad_group_criterion "
          f"WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type='KEYWORD' "
          f"AND ad_group_criterion.negative=FALSE AND ad_group_criterion.status='ENABLED'")
print(f"  live positive keywords: {len(kw)}  "
      f"all ELIGIBLE: {all(E(x.ad_group_criterion.approval_status)=='ELIGIBLE' for x in kw)}")
ads = q(c, f"SELECT ad_group_ad.ad.id, ad_group_ad.status, "
           f"ad_group_ad.policy_summary.approval_status FROM ad_group_ad "
           f"WHERE campaign.id IN ({IN5}) AND ad_group_ad.status='ENABLED'")
print(f"  ENABLED ads on the five: {len(ads)}  "
      f"all APPROVED: {all(E(x.ad_group_ad.policy_summary.approval_status)=='APPROVED' for x in ads)}")
for r in q(c, "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status "
              "FROM shared_set WHERE shared_set.id = 11252984411"):
    print(f"  account negative set {r.shared_set.id} {E(r.shared_set.status)} "
          f"{E(r.shared_set.type)}")
m = len(q(c, "SELECT shared_criterion.criterion_id FROM shared_criterion "
             "WHERE shared_set.id = 11252984411"))
print(f"  members: {m}")
comm = q(c, "SELECT shared_criterion.keyword.text FROM shared_criterion "
            "WHERE shared_set.id = 11252984411 AND shared_criterion.type='KEYWORD'")
print(f"  'commercial' present: "
      f"{any(x.shared_criterion.keyword.text.strip().lower()=='commercial' for x in comm)}")
