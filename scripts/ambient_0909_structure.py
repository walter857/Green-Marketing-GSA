#!/usr/bin/env python3
"""2026-09-09 full structural snapshot: ad groups, keywords, ads, negatives, assets, conversions."""
from __future__ import annotations
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

# ---- AD GROUPS (all campaigns, all statuses) ----
ags = []
for r in q(c, """
    SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
           ad_group.cpc_bid_micros, ad_group.campaign, campaign.id, campaign.name,
           campaign.status
    FROM ad_group ORDER BY campaign.id, ad_group.id
"""):
    ags.append({"id": str(r.ad_group.id), "name": r.ad_group.name,
                "status": E(r.ad_group.status), "type": E(r.ad_group.type_),
                "cpc_bid": round(r.ad_group.cpc_bid_micros / 1e6, 2),
                "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
                "campaign_status": E(r.campaign.status)})
out["ad_groups"] = ags
live_ag = [a for a in ags if a["status"] == "ENABLED" and a["campaign_status"] == "ENABLED"]
print(f"ad_groups total={len(ags)} enabled-in-enabled-campaign={len(live_ag)}")
for a in live_ag:
    print(f"   AG {a['id']:>12} {a['name'][:50]:<50} camp={a['campaign_id']} bid=${a['cpc_bid']}")

# ---- POSITIVE KEYWORDS (all) ----
kws = []
for r in q(c, """
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group_criterion.negative, ad_group_criterion.system_serving_status,
           ad_group_criterion.approval_status, ad_group_criterion.final_urls,
           ad_group_criterion.effective_cpc_bid_micros,
           ad_group_criterion.quality_info.quality_score,
           ad_group_criterion.quality_info.creative_quality_score,
           ad_group_criterion.quality_info.post_click_quality_score,
           ad_group_criterion.quality_info.search_predicted_ctr,
           ad_group.id, ad_group.name, ad_group.status,
           campaign.id, campaign.name, campaign.status
    FROM ad_group_criterion
    WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
"""):
    x = r.ad_group_criterion
    kws.append({"criterion_id": str(x.criterion_id), "text": x.keyword.text,
                "match": E(x.keyword.match_type), "status": E(x.status),
                "system_serving": E(x.system_serving_status),
                "approval": E(x.approval_status),
                "final_urls": list(x.final_urls),
                "eff_cpc": round(x.effective_cpc_bid_micros / 1e6, 2),
                "qs": x.quality_info.quality_score or None,
                "qs_creative": E(x.quality_info.creative_quality_score),
                "qs_lp": E(x.quality_info.post_click_quality_score),
                "qs_ctr": E(x.quality_info.search_predicted_ctr),
                "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
                "ad_group_status": E(r.ad_group.status),
                "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
                "campaign_status": E(r.campaign.status)})
out["positive_keywords"] = kws
livekw = [k for k in kws if k["status"] == "ENABLED" and k["ad_group_status"] == "ENABLED"
          and k["campaign_status"] == "ENABLED"]
print(f"\npositive keywords total={len(kws)} live(enabled x3)={len(livekw)}")
print("  live by campaign:", dict(Counter(NAME.get(k['campaign_id'], k['campaign_id']) for k in livekw)))
print("  live by match:", dict(Counter(k['match'] for k in livekw)))
print("  live by system_serving:", dict(Counter(k['system_serving'] for k in livekw)))

# ---- NEGATIVE KEYWORDS: ad group level ----
agneg = []
for r in q(c, """
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group.id, ad_group.status, campaign.id, campaign.status
    FROM ad_group_criterion
    WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = TRUE
"""):
    x = r.ad_group_criterion
    agneg.append({"criterion_id": str(x.criterion_id), "text": x.keyword.text,
                  "match": E(x.keyword.match_type), "status": E(x.status),
                  "ad_group_id": str(r.ad_group.id), "ad_group_status": E(r.ad_group.status),
                  "campaign_id": str(r.campaign.id), "campaign_status": E(r.campaign.status)})
out["ad_group_negatives"] = agneg
print(f"\nad-group negatives total={len(agneg)}")
print("  on the five:", len([n for n in agneg if n["campaign_id"] in FIVE]))

# ---- NEGATIVE KEYWORDS: campaign level ----
cneg = []
for r in q(c, """
    SELECT campaign_criterion.criterion_id, campaign_criterion.keyword.text,
           campaign_criterion.keyword.match_type, campaign_criterion.status,
           campaign_criterion.negative, campaign_criterion.type,
           campaign.id, campaign.name, campaign.status
    FROM campaign_criterion
    WHERE campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE
"""):
    x = r.campaign_criterion
    cneg.append({"criterion_id": str(x.criterion_id), "text": x.keyword.text,
                 "match": E(x.keyword.match_type), "status": E(x.status),
                 "campaign_id": str(r.campaign.id), "campaign_status": E(r.campaign.status)})
out["campaign_negatives"] = cneg
print(f"campaign negatives total={len(cneg)}")
en5 = [n for n in cneg if n["campaign_id"] in FIVE and n["status"] == "ENABLED"]
print(f"  ENABLED on the five = {len(en5)}")
print("  by campaign:", dict(Counter(NAME[n['campaign_id']] for n in en5)))
print("  by match:", dict(Counter(n['match'] for n in en5)))

# ---- SHARED SETS + members ----
sets = []
for r in q(c, "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status, "
              "shared_set.member_count FROM shared_set"):
    x = r.shared_set
    sets.append({"id": str(x.id), "name": x.name, "type": E(x.type_),
                 "status": E(x.status), "member_count": x.member_count})
out["shared_sets"] = sets
print("\nshared sets:")
for s in sets:
    print(f"  {s['id']:>12} {s['type']:<34} {s['status']:<8} members={s['member_count']:<5} {s['name']}")

members = []
for r in q(c, "SELECT shared_criterion.shared_set, shared_criterion.criterion_id, "
              "shared_criterion.keyword.text, shared_criterion.keyword.match_type, "
              "shared_criterion.type FROM shared_criterion"):
    x = r.shared_criterion
    members.append({"shared_set": x.shared_set.split("/")[-1], "criterion_id": str(x.criterion_id),
                    "text": x.keyword.text, "match": E(x.keyword.match_type)})
out["shared_criteria"] = members
print("shared_criterion rows:", len(members), dict(Counter(m['shared_set'] for m in members)))

links = []
for r in q(c, "SELECT campaign_shared_set.campaign, campaign_shared_set.shared_set, "
              "campaign_shared_set.status FROM campaign_shared_set"):
    x = r.campaign_shared_set
    links.append({"campaign": x.campaign.split("/")[-1], "shared_set": x.shared_set.split("/")[-1],
                  "status": E(x.status)})
out["campaign_shared_sets"] = links
print("campaign_shared_set links:", len(links))
for l in links:
    print("   ", l)

cnc = []
for r in q(c, "SELECT customer_negative_criterion.id, customer_negative_criterion.type, "
              "customer_negative_criterion.negative_keyword_list.shared_set "
              "FROM customer_negative_criterion"):
    x = r.customer_negative_criterion
    cnc.append({"id": str(x.id), "type": E(x.type_),
                "shared_set": x.negative_keyword_list.shared_set.split("/")[-1]
                if x.negative_keyword_list.shared_set else None})
out["customer_negative_criteria"] = cnc
print("customer_negative_criterion:", dict(Counter(x['type'] for x in cnc)))
print("  account-level negative keyword lists:", [x for x in cnc if x['type'] == 'NEGATIVE_KEYWORD_LIST'])

write(EVID / "2026-09-09-structure.json", out)
