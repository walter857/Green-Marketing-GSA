#!/usr/bin/env python3
"""Ambient | 2026-09-24 | Landing-page-only destination audit. READ-ONLY.

Every place a paid click can land: ad final URLs + mobile URLs, keyword URL overrides,
sitelinks at customer / campaign / ad-group level, and URL templates/suffixes at every
level. Plus the 'no heat' search across enabled, paused and removed ad groups and keywords.
"""
from __future__ import annotations
import sys, json, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, SNAP, E  # noqa

STAMP = "2026-09-24"


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True}

    camps = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     campaign.serving_status, campaign.primary_status,
                     campaign.advertising_channel_type, campaign_budget.amount_micros,
                     campaign.tracking_url_template, campaign.final_url_suffix,
                     campaign.bidding_strategy_type
                     FROM campaign WHERE campaign.status != 'REMOVED'"""):
        camps[str(r.campaign.id)] = {
            "name": r.campaign.name, "status": E(r.campaign.status),
            "primary_status": E(r.campaign.primary_status),
            "type": E(r.campaign.advertising_channel_type),
            "budget": r.campaign_budget.amount_micros / 1e6,
            "bidding": E(r.campaign.bidding_strategy_type),
            "tpl": r.campaign.tracking_url_template, "sfx": r.campaign.final_url_suffix}
    out["campaigns"] = camps

    cust = list(q(c, "SELECT customer.tracking_url_template, customer.final_url_suffix FROM customer"))[0]
    out["customer_tpl"] = cust.customer.tracking_url_template
    out["customer_sfx"] = cust.customer.final_url_suffix

    ags = {}
    for r in q(c, """SELECT ad_group.id, ad_group.name, ad_group.status,
                     ad_group.primary_status, ad_group.tracking_url_template,
                     ad_group.final_url_suffix, campaign.id
                     FROM ad_group WHERE campaign.status != 'REMOVED'"""):
        ags[str(r.ad_group.id)] = {
            "name": r.ad_group.name, "status": E(r.ad_group.status),
            "primary_status": E(r.ad_group.primary_status),
            "campaign_id": str(r.campaign.id),
            "tpl": r.ad_group.tracking_url_template, "sfx": r.ad_group.final_url_suffix}
    out["ad_groups"] = ags

    ads = []
    for r in q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type,
                     ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
                     ad_group_ad.ad.tracking_url_template, ad_group_ad.ad.final_url_suffix,
                     ad_group_ad.policy_summary.approval_status,
                     ad_group_ad.policy_summary.review_status,
                     ad_group_ad.primary_status, ad_group.id, campaign.id
                     FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'
                     AND campaign.status != 'REMOVED'"""):
        a = r.ad_group_ad
        ads.append({"ad_id": str(a.ad.id), "status": E(a.status), "type": E(a.ad.type_),
                    "final_urls": list(a.ad.final_urls),
                    "mobile_urls": list(a.ad.final_mobile_urls),
                    "tpl": a.ad.tracking_url_template, "sfx": a.ad.final_url_suffix,
                    "approval": E(a.policy_summary.approval_status),
                    "review": E(a.policy_summary.review_status),
                    "primary_status": E(a.primary_status),
                    "ad_group_id": str(r.ad_group.id), "campaign_id": str(r.campaign.id)})
    out["ads"] = ads

    kws = []
    for r in q(c, """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                     ad_group_criterion.negative, ad_group_criterion.final_urls,
                     ad_group_criterion.final_mobile_urls,
                     ad_group_criterion.tracking_url_template,
                     ad_group_criterion.approval_status, ad_group_criterion.primary_status,
                     ad_group.id, campaign.id
                     FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD'
                     AND ad_group_criterion.status != 'REMOVED'
                     AND campaign.status != 'REMOVED'"""):
        k = r.ad_group_criterion
        kws.append({"crit": str(k.criterion_id), "text": k.keyword.text,
                    "match": E(k.keyword.match_type), "status": E(k.status),
                    "negative": k.negative, "final_urls": list(k.final_urls),
                    "mobile_urls": list(k.final_mobile_urls),
                    "tpl": k.tracking_url_template,
                    "approval": E(k.approval_status), "primary_status": E(k.primary_status),
                    "ad_group_id": str(r.ad_group.id), "campaign_id": str(r.campaign.id)})
    out["keywords"] = kws

    # removed ad groups / keywords too, for the 'no heat' search only
    noheat = {"ad_groups": [], "keywords": []}
    for r in q(c, """SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id,
                     campaign.name, campaign.status FROM ad_group
                     WHERE ad_group.name LIKE '%eat%'"""):
        if "no heat" in r.ad_group.name.lower() or "noheat" in r.ad_group.name.lower():
            noheat["ad_groups"].append({"id": str(r.ad_group.id), "name": r.ad_group.name,
                                        "status": E(r.ad_group.status),
                                        "campaign": r.campaign.name,
                                        "campaign_status": E(r.campaign.status)})
    for r in q(c, """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                     ad_group_criterion.negative, ad_group.id, ad_group.name,
                     ad_group.status, campaign.name, campaign.status
                     FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD'
                     AND ad_group_criterion.keyword.text LIKE '%no heat%'"""):
        k = r.ad_group_criterion
        noheat["keywords"].append({"text": k.keyword.text, "match": E(k.keyword.match_type),
                                   "status": E(k.status), "negative": k.negative,
                                   "ad_group": r.ad_group.name,
                                   "ad_group_status": E(r.ad_group.status),
                                   "campaign": r.campaign.name,
                                   "campaign_status": E(r.campaign.status)})
    out["no_heat_search"] = noheat

    # sitelinks at every level
    sl_assets = {}
    for r in q(c, """SELECT asset.id, asset.type, asset.sitelink_asset.link_text,
                     asset.final_urls, asset.final_mobile_urls, asset.tracking_url_template,
                     asset.final_url_suffix FROM asset WHERE asset.type = 'SITELINK'"""):
        sl_assets[str(r.asset.id)] = {"text": r.asset.sitelink_asset.link_text,
                                      "final_urls": list(r.asset.final_urls),
                                      "mobile_urls": list(r.asset.final_mobile_urls),
                                      "tpl": r.asset.tracking_url_template,
                                      "sfx": r.asset.final_url_suffix}
    links = []
    for r in q(c, """SELECT customer_asset.asset, customer_asset.status,
                     customer_asset.field_type FROM customer_asset
                     WHERE customer_asset.field_type = 'SITELINK'"""):
        links.append({"level": "customer", "asset": r.customer_asset.asset.split("/")[-1],
                      "status": E(r.customer_asset.status)})
    for r in q(c, """SELECT campaign_asset.asset, campaign_asset.status, campaign.id,
                     campaign.status FROM campaign_asset WHERE campaign_asset.field_type = 'SITELINK'
                     AND campaign.status != 'REMOVED'"""):
        links.append({"level": "campaign", "owner": str(r.campaign.id),
                      "asset": r.campaign_asset.asset.split("/")[-1],
                      "status": E(r.campaign_asset.status)})
    for r in q(c, """SELECT ad_group_asset.asset, ad_group_asset.status, ad_group.id,
                     campaign.id, campaign.status FROM ad_group_asset
                     WHERE ad_group_asset.field_type = 'SITELINK'
                     AND campaign.status != 'REMOVED'"""):
        links.append({"level": "ad_group", "owner": str(r.ad_group.id),
                      "campaign": str(r.campaign.id),
                      "asset": r.ad_group_asset.asset.split("/")[-1],
                      "status": E(r.ad_group_asset.status)})
    out["sitelink_assets"] = sl_assets
    out["sitelink_links"] = links

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"dest-audit-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")

    # ---------------------------------------------------------------- print
    print("=== CAMPAIGNS (non-removed) ===")
    for cid, v in sorted(camps.items(), key=lambda x: (x[1]["status"], x[1]["name"])):
        print(f"  {cid} {v['status']:8s} {v['primary_status'][:18]:18s} ${v['budget']:>7.2f} "
              f"{v['type'][:8]:8s} {v['name'][:60]}")
    print(f"customer tpl={out['customer_tpl']!r} sfx={out['customer_sfx']!r}")
    for cid, v in camps.items():
        if v["tpl"] or v["sfx"]:
            print(f"  campaign URL options {cid}: tpl={v['tpl']!r} sfx={v['sfx']!r}")
    print("\n=== ENABLED CAMPAIGNS: ad groups, ads, keyword overrides ===")
    for cid, v in sorted(camps.items(), key=lambda x: x[1]["name"]):
        if v["status"] != "ENABLED":
            continue
        print(f"\n## {cid} {v['name']}")
        for gid, g in sorted(ags.items(), key=lambda x: x[1]["name"]):
            if g["campaign_id"] != cid:
                continue
            gads = [a for a in ads if a["ad_group_id"] == gid]
            gk = [k for k in kws if k["ad_group_id"] == gid and not k["negative"]]
            urls = collections.Counter(u for a in gads for u in a["final_urls"])
            print(f"  {gid} {g['status']:7s} {g['primary_status'][:16]:16s} {g['name'][:52]}")
            for a in gads:
                print(f"      ad {a['ad_id']} {a['status']:7s} {a['approval'][:16]:16s} "
                      f"{a['review'][:18]:18s} {a['final_urls']}"
                      + (f" MOBILE={a['mobile_urls']}" if a['mobile_urls'] else "")
                      + (f" TPL={a['tpl']}" if a['tpl'] else ""))
            for k in gk:
                ov = ""
                if k["final_urls"] or k["mobile_urls"] or k["tpl"]:
                    ov = f" OVERRIDE final={k['final_urls']} mobile={k['mobile_urls']} tpl={k['tpl']!r}"
                print(f"      kw {k['match'][:6]:6s} {k['status']:7s} [{k['text']}]{ov}")
            if g["tpl"] or g["sfx"]:
                print(f"      ad-group URL options tpl={g['tpl']!r} sfx={g['sfx']!r}")
    print("\n=== 'no heat' search (all statuses incl. removed) ===")
    print(json.dumps(noheat, indent=1))
    print("\n=== SITELINKS ===")
    for l in links:
        a = sl_assets.get(l["asset"], {})
        own = l.get("owner", "")
        oname = camps.get(own, {}).get("name") or ags.get(own, {}).get("name") or ""
        print(f"  {l['level']:8s} {l['status']:7s} {own:12s} {oname[:34]:34s} "
              f"{l['asset']} '{a.get('text')}' -> {a.get('final_urls')}"
              + (f" MOBILE={a.get('mobile_urls')}" if a.get("mobile_urls") else ""))
    print(f"\nWROTE {p}\nEXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
