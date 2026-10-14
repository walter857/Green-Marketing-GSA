#!/usr/bin/env python3
"""Ambient | 2026-10-02 | READ-ONLY policy inventory: every ad and linked asset in the enabled Search campaigns + PMax shells,
with policy topic, type, constraints (country / reseller / certificate) and evidence. No mutations.
Writes snapshots/policy-2026-10-02.json; prints a compact table of every entry that carries a topic.
"""
from __future__ import annotations
import sys, json, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, SNAP  # noqa: E402

c = client()
identity_gate(c, verbose=False)
camps = {str(r.campaign.id): (r.campaign.name, E(r.campaign.status), E(r.campaign.advertising_channel_type)) for r in q(c,
         "SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type FROM campaign WHERE campaign.status != 'REMOVED'")}
LIVE = [k for k, v in camps.items() if v[1] == "ENABLED" or v[2] == "PERFORMANCE_MAX"]
IN = ",".join(LIVE)


def entries(ps):
    out = []
    for t in ps.policy_topic_entries:
        cons = []
        for k in t.constraints:
            if k._pb.HasField("country_constraint_list"):
                cons.append({"countries": [x.country_criterion for x in k.country_constraint_list.countries],
                             "total_targeted": k.country_constraint_list.total_targeted_countries})
            if k._pb.HasField("reseller_constraint"):
                cons.append({"reseller": True})
            if k._pb.HasField("certificate_missing_in_country_list"):
                cons.append({"certificate_missing": [x.country_criterion for x in k.certificate_missing_in_country_list.countries]})
            if k._pb.HasField("certificate_domain_mismatch_in_country_list"):
                cons.append({"certificate_domain_mismatch": True})
        ev = []
        for e in t.evidences:
            if e._pb.HasField("website_list"): ev.append({"websites": list(e.website_list.websites)})
            if e._pb.HasField("text_list"): ev.append({"text": list(e.text_list.texts)[:5]})
            if e._pb.HasField("destination_text_list"): ev.append({"destination_text": list(e.destination_text_list.destination_texts)[:5]})
            if e._pb.HasField("destination_mismatch"): ev.append({"destination_mismatch": [E(x) for x in e.destination_mismatch.url_types]})
            if e._pb.HasField("destination_not_working"): ev.append({"destination_not_working": E(e.destination_not_working.device),
                                                                     "url": e.destination_not_working.expanded_url})
        out.append({"topic": t.topic, "type": E(t.type_), "constraints": cons, "evidence": ev})
    return out


rows = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls,
        ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, ad_group_ad.policy_summary.policy_topic_entries,
        ad_group_ad.primary_status, ad_group_ad.primary_status_reasons FROM ad_group_ad WHERE campaign.id IN ({IN}) AND ad_group_ad.status != 'REMOVED'"""):
    a = r.ad_group_ad
    rows.append(dict(kind="ad", campaign=str(r.campaign.id), campaign_name=camps[str(r.campaign.id)][0], ad_group=str(r.ad_group.id),
                     ad_group_name=r.ad_group.name, ad_group_status=E(r.ad_group.status), id=str(a.ad.id), status=E(a.status), urls=list(a.ad.final_urls),
                     approval=E(a.policy_summary.approval_status), review=E(a.policy_summary.review_status), primary=E(a.primary_status),
                     reasons=[E(x) for x in a.primary_status_reasons], topics=entries(a.policy_summary)))
assets = {}
for frm, lvl in (("campaign_asset", "campaign"), ("ad_group_asset", "ad_group"), ("customer_asset", "customer")):
    where = f"WHERE campaign.id IN ({IN}) AND {frm}.status != 'REMOVED'" if lvl != "customer" else f"WHERE {frm}.status != 'REMOVED'"
    sel = "campaign.id, " if lvl == "campaign" else ("campaign.id, ad_group.id, " if lvl == "ad_group" else "")
    for r in q(c, f"""SELECT {sel}{frm}.field_type, {frm}.status, {frm}.primary_status, {frm}.primary_status_reasons, asset.id, asset.type, asset.final_urls,
            asset.policy_summary.approval_status, asset.policy_summary.review_status, asset.policy_summary.policy_topic_entries,
            asset.sitelink_asset.link_text, asset.callout_asset.callout_text FROM {frm} {where}"""):
        link = getattr(r, frm); a = r.asset
        rows.append(dict(kind=f"{lvl}_asset", campaign=str(r.campaign.id) if lvl != "customer" else "", ad_group=str(r.ad_group.id) if lvl == "ad_group" else "",
                         id=str(a.id), field=E(link.field_type), status=E(link.status), primary=E(link.primary_status),
                         reasons=[E(x) for x in link.primary_status_reasons], urls=list(a.final_urls), text=a.sitelink_asset.link_text or a.callout_asset.callout_text,
                         approval=E(a.policy_summary.approval_status), review=E(a.policy_summary.review_status), topics=entries(a.policy_summary)))
(SNAP / "policy-2026-10-02.json").write_text(json.dumps(rows, indent=1, default=str), encoding="utf-8")
print("rows", len(rows), "with topics", sum(1 for x in rows if x["topics"]))
by = collections.Counter((x["kind"], x["status"], tuple(sorted({t["topic"] for t in x["topics"]}))) for x in rows if x["topics"])
for k, v in sorted(by.items(), key=lambda kv: -kv[1]):
    print(" ", v, k)
print("\nCURRENT (status ENABLED) items with a topic:")
for x in rows:
    if x["topics"] and x["status"] == "ENABLED":
        print(" ", x["kind"], x["campaign"][-4:], x.get("ad_group_name", x.get("ad_group", ""))[:28], x["id"], x["approval"], x["primary"], x["reasons"],
              [(t["topic"], t["type"], t["constraints"]) for t in x["topics"]], x["urls"][:1])
print("\nhousing details (any status):")
for x in rows:
    for t in x["topics"]:
        if "HOUSING" in t["topic"].upper():
            print(" ", x["kind"], x["campaign"][-4:], x["id"], x["status"], x["approval"], t["type"], t["constraints"], t["evidence"][:2], x["urls"][:1])
