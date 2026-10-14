#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: where does the French Drain 'Destination not working' warning live?

Reads policy topics with evidences at every level that can carry one: ad, RSA text assets,
campaign/ad-group/customer assets (sitelinks), keywords, and every ad in the account.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from google.protobuf.json_format import MessageToDict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import EVID, client, q  # noqa: E402

c = client()
AG = "195877148126"
out = {}


def run(name, query):
    try:
        rows = [MessageToDict(r._pb, preserving_proto_field_name=True) for r in q(c, query)]
    except Exception as exc:  # noqa: BLE001
        print(f"[ERR] {name}: {str(exc)[:300]}")
        return []
    out[name] = rows
    return rows


rows = run("ad_policy", f"""
SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.primary_status,
       ad_group_ad.primary_status_reasons, ad_group_ad.policy_summary.approval_status,
       ad_group_ad.policy_summary.review_status, ad_group_ad.policy_summary.policy_topic_entries,
       ad_group.primary_status, ad_group.primary_status_reasons, ad_group_ad.ad.final_urls,
       ad_group_ad.ad.final_mobile_urls
FROM ad_group_ad WHERE ad_group.id = {AG}""")
for r in rows:
    print("AD", json.dumps(r)[:1500])

rows = run("rsa_asset_policy", f"""
SELECT ad_group_ad_asset_view.field_type, ad_group_ad_asset_view.policy_summary.approval_status,
       ad_group_ad_asset_view.policy_summary.review_status,
       ad_group_ad_asset_view.policy_summary.policy_topic_entries, asset.id
FROM ad_group_ad_asset_view WHERE ad_group.id = {AG}""")
bad = [r for r in rows if r.get("ad_group_ad_asset_view", {}).get("policy_summary", {}).get("approval_status") != "APPROVED"
       or r.get("ad_group_ad_asset_view", {}).get("policy_summary", {}).get("policy_topic_entries")]
print(f"RSA assets: {len(rows)} rows, non-clean {len(bad)}")
for r in bad[:10]:
    print("  ", json.dumps(r)[:600])

rows = run("kw_policy", f"""
SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
       ad_group_criterion.approval_status, ad_group_criterion.disapproval_reasons,
       ad_group_criterion.final_urls, ad_group_criterion.status, ad_group_criterion.primary_status,
       ad_group_criterion.primary_status_reasons
FROM ad_group_criterion WHERE ad_group.id = {AG} AND ad_group_criterion.negative = FALSE""")
for r in rows:
    a = r["ad_group_criterion"]
    if a.get("approval_status") not in (None, "APPROVED") or a.get("disapproval_reasons") or a.get("final_urls"):
        print("  KW", json.dumps(a)[:400])
print(f"keywords checked: {len(rows)}")

for lvl, frm, extra in [("campaign_asset", "campaign_asset", "campaign.id,"),
                        ("ad_group_asset", "ad_group_asset", "ad_group.id,"),
                        ("customer_asset", "customer_asset", "")]:
    rows = run(lvl, f"""
    SELECT {extra} {frm}.field_type, {frm}.status, {frm}.primary_status, {frm}.primary_status_reasons,
           asset.id, asset.final_urls, asset.policy_summary.approval_status,
           asset.policy_summary.review_status, asset.policy_summary.policy_topic_entries
    FROM {frm} WHERE {frm}.status != 'REMOVED'""")
    for r in rows:
        ps = r.get("asset", {}).get("policy_summary", {})
        if ps.get("policy_topic_entries") or ps.get("approval_status") not in ("APPROVED", None) \
                or r.get(frm, {}).get("primary_status") not in ("ELIGIBLE", None):
            print(f"  {lvl}", json.dumps(r)[:700])
    print(f"{lvl}: {len(rows)} rows checked")

rows = run("all_ad_topics", """
SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, ad_group_ad.status,
       ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.policy_topic_entries
FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'""")
for r in rows:
    t = r["ad_group_ad"].get("policy_summary", {}).get("policy_topic_entries")
    if t:
        print("  TOPIC", r["campaign"]["name"][:30], r["ad_group"]["name"][:26], r["ad_group_ad"]["status"],
              json.dumps(t)[:500])
print(f"all non-removed ads checked: {len(rows)}")
(EVID / "2026-09-26-destination-policy.json").write_text(json.dumps(out, indent=0), encoding="utf-8")
