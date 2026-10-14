#!/usr/bin/env python3
"""Ambient 2026-09-15 | full commercial ad-group inventory + change history + serving chain."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
CAMP, RES_AG, COMM_AG = "24132507747", "202339087634", "199748801029"
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
c = client()
identity_gate(c, verbose=False)

print("=== A. CHANGE HISTORY (change_event, last 29 days, capped by API at 30) ===")
today = datetime.date(2026, 9, 15)
start = today - datetime.timedelta(days=29)
ce = []
try:
    rows = q(c, f"""
        SELECT change_event.change_date_time, change_event.change_resource_type,
               change_event.resource_change_operation, change_event.changed_fields,
               change_event.user_email, change_event.client_type,
               change_event.campaign, change_event.ad_group,
               change_event.change_resource_name,
               change_event.old_resource, change_event.new_resource
        FROM change_event
        WHERE change_event.change_date_time >= '{start}'
          AND change_event.change_date_time <= '{today}'
        ORDER BY change_event.change_date_time DESC
        LIMIT 500
    """)
    for r in rows:
        e = r.change_event
        ce.append({
            "when": e.change_date_time, "type": E(e.change_resource_type),
            "op": E(e.resource_change_operation),
            "fields": list(e.changed_fields.paths) if e.changed_fields else [],
            "user": e.user_email, "client_type": E(e.client_type),
            "campaign": e.campaign.split("/")[-1] if e.campaign else None,
            "ad_group": e.ad_group.split("/")[-1] if e.ad_group else None,
            "resource": e.change_resource_name,
        })
except Exception as ex:
    ce = [{"error": str(ex)[:400]}]
out["change_events"] = ce
print(f"  rows: {len(ce)}")
for e in ce[:60]:
    if "error" in e:
        print("  ERROR", e["error"]); continue
    print(f"  {e['when'][:19]} {e['type']:26s} {e['op']:8s} ag={str(e['ad_group']):14s} "
          f"{','.join(e['fields'])[:70]}  <{e['user']}> {e['client_type']}")

print("\n=== B. COMMERCIAL AD GROUP LIVE STATE ===")
ag = q(c, f"""
    SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
           ad_group.cpc_bid_micros, ad_group.tracking_url_template,
           ad_group.final_url_suffix, ad_group.url_custom_parameters,
           campaign.id, campaign.name, campaign.status
    FROM ad_group WHERE ad_group.id = {COMM_AG}
""")[0]
out["commercial_ad_group"] = {
    "id": str(ag.ad_group.id), "name": ag.ad_group.name, "status": E(ag.ad_group.status),
    "type": E(ag.ad_group.type), "cpc_bid_micros": ag.ad_group.cpc_bid_micros,
    "tracking_url_template": ag.ad_group.tracking_url_template or None,
    "final_url_suffix": ag.ad_group.final_url_suffix or None,
    "campaign_id": str(ag.campaign.id), "campaign_status": E(ag.campaign.status),
}
print(f"  {ag.ad_group.id}  {ag.ad_group.name}")
print(f"  status={E(ag.ad_group.status)}  cpc_bid={ag.ad_group.cpc_bid_micros}  "
      f"campaign={ag.campaign.id} ({E(ag.campaign.status)})")
print(f"  ad_group tracking_url_template={ag.ad_group.tracking_url_template or '(none)'}")
print(f"  ad_group final_url_suffix={ag.ad_group.final_url_suffix or '(none)'}")

print("\n=== C. COMMERCIAL KEYWORDS ===")
kws = q(c, f"""
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group_criterion.approval_status, ad_group_criterion.final_urls,
           ad_group_criterion.tracking_url_template,
           ad_group_criterion.system_serving_status,
           ad_group_criterion.quality_info.quality_score,
           ad_group_criterion.quality_info.creative_quality_score,
           ad_group_criterion.quality_info.post_click_quality_score,
           ad_group_criterion.quality_info.search_predicted_ctr,
           ad_group_criterion.cpc_bid_micros, ad_group_criterion.effective_cpc_bid_micros,
           ad_group_criterion.negative
    FROM ad_group_criterion
    WHERE ad_group.id = {COMM_AG} AND ad_group_criterion.negative = FALSE
""")
kl = []
for r in kws:
    k = r.ad_group_criterion
    kl.append({"criterion_id": str(k.criterion_id), "text": k.keyword.text,
               "match": E(k.keyword.match_type), "status": E(k.status),
               "approval": E(k.approval_status),
               "system_serving": E(k.system_serving_status),
               "final_urls": list(k.final_urls) or None,
               "tracking_url_template": k.tracking_url_template or None,
               "qs": k.quality_info.quality_score or None,
               "exp_ctr": E(k.quality_info.search_predicted_ctr),
               "ad_relevance": E(k.quality_info.creative_quality_score),
               "lp_experience": E(k.quality_info.post_click_quality_score),
               "cpc_bid_micros": k.cpc_bid_micros,
               "eff_cpc_bid_micros": k.effective_cpc_bid_micros})
    print(f"  {k.criterion_id} {E(k.keyword.match_type):6s} '{k.keyword.text}' "
          f"{E(k.status)} {E(k.approval_status)} serving={E(k.system_serving_status)} "
          f"QS={k.quality_info.quality_score or '-'} "
          f"final_urls={list(k.final_urls) or '(inherit)'}")
out["commercial_keywords"] = kl

print("\n=== D. COMMERCIAL AD-GROUP NEGATIVES ===")
negs = q(c, f"""
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status
    FROM ad_group_criterion
    WHERE ad_group.id = {COMM_AG} AND ad_group_criterion.negative = TRUE
""")
nl = [{"criterion_id": str(r.ad_group_criterion.criterion_id),
       "text": r.ad_group_criterion.keyword.text,
       "match": E(r.ad_group_criterion.keyword.match_type),
       "status": E(r.ad_group_criterion.status)} for r in negs]
out["commercial_ad_group_negatives"] = nl
INTENDED17 = ["residential", "homeowner", "house", "diy", "job", "jobs", "career", "careers",
              "salary", "salaries", "course", "courses", "parts", "used", "wholesale",
              "supplier", "supply"]
HELD5 = ["school", "schools", "rent", "rental", "training"]
live_terms = sorted(x["text"] for x in nl)
print(f"  live count: {len(nl)}")
print(f"  terms: {live_terms}")
print(f"  all BROAD: {all(x['match']=='BROAD' for x in nl)}  "
      f"all ENABLED: {all(x['status']=='ENABLED' for x in nl)}")
print(f"  == intended 17 set: {sorted(INTENDED17) == live_terms}")
print(f"  held-5 absent: {[h for h in HELD5 if h in live_terms] == []}")
out["neg_verdict"] = {
    "live_count": len(nl), "expected": 17,
    "set_matches": sorted(INTENDED17) == live_terms,
    "all_broad": all(x["match"] == "BROAD" for x in nl),
    "all_enabled": all(x["status"] == "ENABLED" for x in nl),
    "held_absent": [h for h in HELD5 if h in live_terms] == [],
    "missing": sorted(set(INTENDED17) - set(live_terms)),
    "extra": sorted(set(live_terms) - set(INTENDED17)),
}

print("\n=== E. ADS IN THE COMMERCIAL AD GROUP ===")
ads = q(c, f"""
    SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status,
           ad_group_ad.policy_summary.policy_topic_entries,
           ad_group_ad.ad.final_urls, ad_group_ad.ad.tracking_url_template,
           ad_group_ad.ad.final_url_suffix, ad_group_ad.ad.url_custom_parameters,
           ad_group_ad.ad.responsive_search_ad.headlines,
           ad_group_ad.ad.responsive_search_ad.descriptions,
           ad_group_ad.ad.responsive_search_ad.path1,
           ad_group_ad.ad.responsive_search_ad.path2,
           ad_group_ad.ad_strength
    FROM ad_group_ad WHERE ad_group.id = {COMM_AG}
""")
al = []
for r in ads:
    a = r.ad_group_ad
    rsa = a.ad.responsive_search_ad
    rec = {"ad_id": str(a.ad.id), "type": E(a.ad.type), "status": E(a.status),
           "approval": E(a.policy_summary.approval_status),
           "review": E(a.policy_summary.review_status),
           "policy_topics": [E(t.topic_entry_type) + ":" + t.topic
                             for t in a.policy_summary.policy_topic_entries],
           "final_urls": list(a.ad.final_urls),
           "tracking_url_template": a.ad.tracking_url_template or None,
           "final_url_suffix": a.ad.final_url_suffix or None,
           "path1": rsa.path1 or None, "path2": rsa.path2 or None,
           "ad_strength": E(a.ad_strength),
           "headlines": [{"text": h.text, "pin": E(h.pinned_field)} for h in rsa.headlines],
           "descriptions": [{"text": d.text, "pin": E(d.pinned_field)} for d in rsa.descriptions]}
    al.append(rec)
    print(f"  ad {a.ad.id} {E(a.ad.type)} {E(a.status)} approval={E(a.policy_summary.approval_status)} "
          f"review={E(a.policy_summary.review_status)} strength={E(a.ad_strength)}")
out["commercial_ads"] = al
print(f"  TOTAL ADS IN COMMERCIAL AD GROUP: {len(al)}")

print("\n=== F. CAMPAIGN-LEVEL NEGATIVES ON 24132507747 THAT COULD BLOCK COMMERCIAL ===")
cneg = q(c, f"""
    SELECT campaign_criterion.criterion_id, campaign_criterion.keyword.text,
           campaign_criterion.keyword.match_type, campaign_criterion.status
    FROM campaign_criterion
    WHERE campaign.id = {CAMP} AND campaign_criterion.negative = TRUE
      AND campaign_criterion.type = KEYWORD
""")
cl = [{"criterion_id": str(r.campaign_criterion.criterion_id),
       "text": r.campaign_criterion.keyword.text,
       "match": E(r.campaign_criterion.keyword.match_type),
       "status": E(r.campaign_criterion.status)} for r in cneg]
out["campaign_negatives_count"] = len(cl)
out["campaign_negatives"] = cl
print(f"  total campaign-level KEYWORD negatives on {CAMP}: {len(cl)}")

print("\n=== G. ACCOUNT-LEVEL NEGATIVE LISTS + SHARED SETS ===")
sets = q(c, """
    SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
           shared_set.member_count
    FROM shared_set
""")
ss = [{"id": str(r.shared_set.id), "name": r.shared_set.name,
       "type": E(r.shared_set.type), "status": E(r.shared_set.status),
       "member_count": r.shared_set.member_count} for r in sets]
out["shared_sets"] = ss
for s in ss:
    print(f"  {s['id']:14s} {s['type']:32s} {s['status']:8s} members={s['member_count']:>6} {s['name'][:50]}")
camp_sets = q(c, """
    SELECT campaign_shared_set.campaign, campaign_shared_set.shared_set,
           campaign_shared_set.status FROM campaign_shared_set
""")
cs = [{"campaign": r.campaign_shared_set.campaign.split("/")[-1],
       "shared_set": r.campaign_shared_set.shared_set.split("/")[-1],
       "status": E(r.campaign_shared_set.status)} for r in camp_sets]
out["campaign_shared_sets"] = cs
print(f"  campaign_shared_set attachments: {len(cs)}")
for x in cs:
    print(f"    campaign {x['campaign']} <- shared_set {x['shared_set']} {x['status']}")

Path(SNAP).mkdir(parents=True, exist_ok=True)
p = SNAP / f"commercial-inventory-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
