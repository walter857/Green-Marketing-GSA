#!/usr/bin/env python3
"""Policy topic detail for the two live DISAPPROVED RSAs, plus keyword QS detail."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

print("=== POLICY SUMMARY FOR NON-APPROVED ADS IN THE FIVE ===")
rows = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status,
           ad_group_ad.policy_summary.policy_topic_entries
    FROM ad_group_ad
    WHERE campaign.id IN ({IN5})
      AND ad_group_ad.policy_summary.approval_status != 'APPROVED'
"""):
    x = r.ad_group_ad
    ents = []
    for e in x.policy_summary.policy_topic_entries:
        ents.append({"topic": e.topic, "type": E(e.type_),
                     "evidences": len(e.evidences),
                     "constraints": [E(cst.__class__) for cst in e.constraints]})
    rows.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id), "ad": str(x.ad.id),
                 "status": E(x.status), "approval": E(x.policy_summary.approval_status),
                 "review": E(x.policy_summary.review_status), "entries": ents})
out["policy"] = rows
for r in rows:
    print(f"\n  {NAME[r['camp']]:<20} ad={r['ad']} AG={r['ag']} status={r['status']} "
          f"approval={r['approval']} review={r['review']}")
    for e in r["entries"]:
        print(f"      topic={e['topic']!r} type={e['type']} evidences={e['evidences']}")

print("\n=== QUALITY SCORE, LIVE KEYWORDS ===")
qs = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type,
           ad_group_criterion.quality_info.quality_score,
           ad_group_criterion.quality_info.creative_quality_score,
           ad_group_criterion.quality_info.post_click_quality_score,
           ad_group_criterion.quality_info.search_predicted_ctr,
           ad_group_criterion.position_estimates.first_page_cpc_micros,
           ad_group_criterion.position_estimates.top_of_page_cpc_micros,
           ad_group_criterion.position_estimates.first_position_cpc_micros,
           ad_group_criterion.effective_cpc_bid_micros
    FROM keyword_view
    WHERE campaign.id IN ({IN5}) AND ad_group_criterion.status = 'ENABLED'
      AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
"""):
    x = r.ad_group_criterion
    qs.append({"camp": str(r.campaign.id), "text": x.keyword.text, "match": E(x.keyword.match_type),
               "qs": x.quality_info.quality_score or None,
               "ctr_component": E(x.quality_info.search_predicted_ctr),
               "ad_relevance": E(x.quality_info.creative_quality_score),
               "lp_experience": E(x.quality_info.post_click_quality_score),
               "first_page_cpc": round(x.position_estimates.first_page_cpc_micros / 1e6, 2),
               "top_of_page_cpc": round(x.position_estimates.top_of_page_cpc_micros / 1e6, 2),
               "first_position_cpc": round(x.position_estimates.first_position_cpc_micros / 1e6, 2),
               "eff_cpc_bid": round(x.effective_cpc_bid_micros / 1e6, 2)})
out["quality_score"] = qs
seen = set()
for x in qs:
    k = (x["camp"], x["text"], x["match"])
    if k in seen:
        continue
    seen.add(k)
    print(f"  {NAME[x['camp']]:<20} {x['match']:<7} QS={str(x['qs']):<5} "
          f"ctr={x['ctr_component']:<14} rel={x['ad_relevance']:<14} lp={x['lp_experience']:<14} "
          f"firstPageCPC=${x['first_page_cpc']:<7} topOfPageCPC=${x['top_of_page_cpc']:<7} "
          f"firstPosCPC=${x['first_position_cpc']:<8} [{x['text']}]")

write(EVID / "2026-09-09-policy-and-qs.json", out)
