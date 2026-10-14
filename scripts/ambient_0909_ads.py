#!/usr/bin/env python3
"""RSA / asset / QS audit + the 'hvac installers' timeline."""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

print("=== RSAs IN THE FIVE ===")
ads = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group.name, ad_group_ad.ad.id,
           ad_group_ad.status, ad_group_ad.ad_strength,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status,
           ad_group_ad.ad.type, ad_group_ad.ad.final_urls,
           ad_group_ad.ad.responsive_search_ad.headlines,
           ad_group_ad.ad.responsive_search_ad.descriptions,
           ad_group_ad.ad.responsive_search_ad.path1,
           ad_group_ad.ad.responsive_search_ad.path2
    FROM ad_group_ad WHERE campaign.id IN ({IN5})
"""):
    x = r.ad_group_ad
    heads = [{"text": h.text, "pin": E(h.pinned_field), "len": len(h.text)}
             for h in x.ad.responsive_search_ad.headlines]
    descs = [{"text": d.text, "pin": E(d.pinned_field), "len": len(d.text)}
             for d in x.ad.responsive_search_ad.descriptions]
    ads.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id), "ag_name": r.ad_group.name,
                "ad_id": str(x.ad.id), "status": E(x.status), "strength": E(x.ad_strength),
                "approval": E(x.policy_summary.approval_status),
                "review": E(x.policy_summary.review_status), "type": E(x.ad.type_),
                "final_urls": list(x.ad.final_urls), "n_head": len(heads), "n_desc": len(descs),
                "headlines": heads, "descriptions": descs,
                "path1": x.ad.responsive_search_ad.path1, "path2": x.ad.responsive_search_ad.path2})
out["ads"] = ads
print("total ad rows:", len(ads), dict(Counter(a["status"] for a in ads)))
for a in sorted(ads, key=lambda a: (NAME[a["camp"]], a["status"])):
    if a["status"] != "REMOVED":
        print(f"  {NAME[a['camp']]:<20} ad={a['ad_id']:<14} {a['status']:<8} {a['approval']:<18} "
              f"strength={a['strength']:<14} H={a['n_head']} D={a['n_desc']} "
              f"pinned_H={sum(1 for h in a['headlines'] if h['pin'] != 'UNSPECIFIED')} "
              f"url={a['final_urls']}")

print("\n=== RSA COPY (enabled ads only) ===")
for a in sorted([a for a in ads if a["status"] == "ENABLED"], key=lambda a: NAME[a["camp"]]):
    print(f"\n  --- {NAME[a['camp']]} / ad {a['ad_id']} / {a['final_urls']} paths={a['path1']}/{a['path2']}")
    for h in a["headlines"]:
        print(f"      H({h['len']:>2}) pin={h['pin']:<12} {h['text']}")
    for d in a["descriptions"]:
        print(f"      D({d['len']:>2}) pin={d['pin']:<12} {d['text']}")

print("\n=== CAMPAIGN ASSETS ON THE FIVE ===")
casts = []
for r in q(c, f"""
    SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type,
           campaign_asset.status, asset.id, asset.type, asset.name,
           asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
           asset.sitelink_asset.description2, asset.callout_asset.callout_text,
           asset.structured_snippet_asset.header, asset.structured_snippet_asset.values,
           asset.call_asset.phone_number, asset.call_asset.country_code,
           asset.final_urls
    FROM campaign_asset WHERE campaign.id IN ({IN5})
"""):
    x = r.campaign_asset
    casts.append({"camp": str(r.campaign.id), "field": E(x.field_type), "status": E(x.status),
                  "asset_id": str(r.asset.id), "asset_type": E(r.asset.type_),
                  "sitelink": r.asset.sitelink_asset.link_text,
                  "sitelink_d1": r.asset.sitelink_asset.description1,
                  "sitelink_d2": r.asset.sitelink_asset.description2,
                  "callout": r.asset.callout_asset.callout_text,
                  "snippet_header": r.asset.structured_snippet_asset.header,
                  "snippet_values": list(r.asset.structured_snippet_asset.values),
                  "phone": r.asset.call_asset.phone_number,
                  "final_urls": list(r.asset.final_urls)})
out["campaign_assets"] = casts
print("rows:", len(casts))
print("by (field, status):", dict(Counter((a["field"], a["status"]) for a in casts)))
for camp in FIVE:
    rows = [a for a in casts if a["camp"] == camp and a["status"] == "ENABLED"]
    print(f"\n  {NAME[camp]} ({len(rows)} enabled)")
    for a in sorted(rows, key=lambda a: a["field"]):
        label = (a["sitelink"] or a["callout"] or a["phone"]
                 or (a["snippet_header"] + ": " + ", ".join(a["snippet_values"])
                     if a["snippet_header"] else "") or a["asset_type"])
        print(f"     {a['field']:<22} {str(label)[:70]}  {a['final_urls'] if a['final_urls'] else ''}")

print("\n=== CUSTOMER ASSETS (account-level) ===")
cust = []
for r in q(c, """
    SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status,
           asset.id, asset.type, asset.call_asset.phone_number,
           asset.callout_asset.callout_text, asset.sitelink_asset.link_text
    FROM customer_asset WHERE customer_asset.status != 'REMOVED'
"""):
    x = r.customer_asset
    cust.append({"field": E(x.field_type), "status": E(x.status), "asset_id": str(r.asset.id),
                 "type": E(r.asset.type_), "phone": r.asset.call_asset.phone_number,
                 "callout": r.asset.callout_asset.callout_text,
                 "sitelink": r.asset.sitelink_asset.link_text})
out["customer_assets"] = cust
for a in cust:
    print(f"  {a['field']:<22} {a['status']:<8} {a['type']:<22} "
          f"{a['phone'] or a['callout'] or a['sitelink']}")

print("\n=== 'hvac installers' TIMELINE (daily keyword_view) ===")
tl = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
for r in q(c, f"""
    SELECT segments.date, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           campaign.id, metrics.impressions, metrics.clicks, metrics.cost_micros,
           metrics.conversions
    FROM keyword_view WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'
"""):
    k = (r.segments.date, r.ad_group_criterion.keyword.text,
         E(r.ad_group_criterion.keyword.match_type))
    tl[k]["impressions"] += r.metrics.impressions
    tl[k]["clicks"] += r.metrics.clicks
    tl[k]["cost"] += r.metrics.cost_micros / 1e6
    tl[k]["conversions"] += r.metrics.conversions
out["keyword_daily"] = {f"{k[0]}|{k[1]}|{k[2]}": {kk: round(vv, 2) for kk, vv in v.items()}
                        for k, v in tl.items()}
print("  installers-family rows by date:")
for k in sorted(tl):
    if "installers" in k[1]:
        v = tl[k]
        print(f"    {k[0]}  {k[2]:<7} impr={v['impressions']:<5} clk={v['clicks']:<3} "
              f"${round(v['cost'],2):<8} conv={round(v['conversions'],1)}   [{k[1]}]")

write(EVID / "2026-09-09-ads-assets.json", out)
