#!/usr/bin/env python3
"""Ambient | 2026-09-24 | Post-enable READBACK + destination audit. READ-ONLY."""
from __future__ import annotations
import sys, json, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, PLANS, RECEIPTS, SNAP

O = "https://offer.ambientcoolingandheating.com/"
c = client(); identity_gate(c, verbose=False)
fails = []
def chk(ok, msg):
    if not ok: fails.append(msg); print("  FAIL", msg)

camps = {str(r.campaign.id): r for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.primary_status,
          campaign_budget.amount_micros FROM campaign WHERE campaign.status != 'REMOVED'""")}
en_camps = {k: v for k, v in camps.items() if E(v.campaign.status) == "ENABLED"}
ags = {str(r.ad_group.id): r for r in q(c, """SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status,
          campaign.id FROM ad_group WHERE campaign.status != 'REMOVED'""")}
ads = list(q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
          ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, ad_group_ad.primary_status,
          ad_group.id, campaign.id FROM ad_group_ad WHERE ad_group_ad.status = 'ENABLED' AND campaign.status = 'ENABLED'"""))
kws = list(q(c, """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
          ad_group_criterion.status, ad_group_criterion.final_urls, ad_group_criterion.final_mobile_urls,
          ad_group_criterion.approval_status, ad_group_criterion.primary_status, ad_group.id, campaign.id
          FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
          AND ad_group_criterion.status = 'ENABLED' AND campaign.status = 'ENABLED' AND ad_group.status = 'ENABLED'"""))
sl = {str(r.asset.id): list(r.asset.final_urls) for r in q(c, "SELECT asset.id, asset.final_urls FROM asset WHERE asset.type = 'SITELINK'")}
links = list(q(c, """SELECT campaign.id, campaign.status, campaign_asset.asset, campaign_asset.status FROM campaign_asset
          WHERE campaign_asset.field_type = 'SITELINK' AND campaign.status = 'ENABLED' AND campaign_asset.status = 'ENABLED'"""))
acct_sl = list(q(c, "SELECT customer_asset.asset, customer_asset.status FROM customer_asset WHERE customer_asset.field_type = 'SITELINK' AND customer_asset.status = 'ENABLED'"))
agsl = list(q(c, """SELECT ad_group.id, ad_group_asset.asset, ad_group_asset.status, campaign.status FROM ad_group_asset
          WHERE ad_group_asset.field_type = 'SITELINK' AND ad_group_asset.status = 'ENABLED' AND campaign.status = 'ENABLED'"""))

# receipts
swap2 = json.loads((PLANS / "AMB-0924-LP-SWAP-2.json").read_text(encoding="utf-8"))
still_old = {o["ad_id"] for o in swap2["operations"]}
en2a = json.loads((PLANS / "AMB-0924-LP-ENABLE-2A.json").read_text(encoding="utf-8"))
for o in en2a["operations"]:
    if o["op"] == "ENABLE_AD_GROUP": chk(E(ags[o["ad_group_id"]].ad_group.status) == "ENABLED", f"ad group {o['name']} not ENABLED")
chk(E(camps["24268690041"].campaign.status) == "ENABLED", "Thermostat campaign not ENABLED")

main_site_serving = []
for a in ads:
    u = list(a.ad_group_ad.ad.final_urls)
    enabled_group = E(ags[str(a.ad_group.id)].ad_group.status) == "ENABLED"
    if not enabled_group: continue
    if not u[0].startswith(O):
        main_site_serving.append((str(a.ad_group.id), str(a.ad_group_ad.ad.id), u[0]))
        chk(str(a.ad_group_ad.ad.id) in still_old, f"unexpected main-site ad {a.ad_group_ad.ad.id} {u[0]}")
    chk(not a.ad_group_ad.ad.final_mobile_urls, f"mobile URL on ad {a.ad_group_ad.ad.id}")
for k in kws:
    chk(not k.ad_group_criterion.final_urls and not k.ad_group_criterion.final_mobile_urls,
        f"keyword URL override {k.ad_group_criterion.keyword.text}")
for l in links:
    aid = l.campaign_asset.asset.split("/")[-1]
    chk(sl.get(aid, [""])[0].startswith(O), f"enabled sitelink {aid} -> {sl.get(aid)} on {l.campaign.id}")
chk(not acct_sl, f"{len(acct_sl)} account-level sitelinks enabled")
for l in agsl:
    aid = l.ad_group_asset.asset.split("/")[-1]
    chk(sl.get(aid, [""])[0].startswith(O), f"ad-group sitelink {aid} -> {sl.get(aid)}")

budget = sum(v.campaign_budget.amount_micros for v in en_camps.values()) / 1e6
serving_budget = sum(v.campaign_budget.amount_micros for k, v in en_camps.items()
                     if any(E(g.ad_group.status) == "ENABLED" and str(g.campaign.id) == k for g in ags.values())) / 1e6
rows = []
for gid, g in sorted(ags.items(), key=lambda x: x[1].ad_group.name):
    cid = str(g.campaign.id)
    if cid not in en_camps: continue
    gads = [a for a in ads if str(a.ad_group.id) == gid]
    rows.append({"ad_group_id": gid, "ad_group": g.ad_group.name, "campaign": camps[cid].campaign.name[19:60],
                 "group_status": E(g.ad_group.status), "group_primary": E(g.ad_group.primary_status),
                 "enabled_ads": len(gads),
                 "review": dict(collections.Counter(f"{E(a.ad_group_ad.policy_summary.approval_status)}/{E(a.ad_group_ad.policy_summary.review_status)}" for a in gads)),
                 "ad_primary": dict(collections.Counter(E(a.ad_group_ad.primary_status) for a in gads)),
                 "urls": sorted({list(a.ad_group_ad.ad.final_urls)[0].replace("https://", "") for a in gads}),
                 "keywords_enabled": sum(1 for k in kws if str(k.ad_group.id) == gid)})
out = {"when": datetime.datetime.now(TZ).isoformat(), "fails": fails, "enabled_budget_total": budget,
       "budget_of_campaigns_with_enabled_groups": serving_budget,
       "enabled_campaigns": {k: [v.campaign.name[19:60], E(v.campaign.primary_status), v.campaign_budget.amount_micros / 1e6] for k, v in en_camps.items()},
       "main_site_ads_still_serving_until_swap2": main_site_serving, "rows": rows,
       "enabled_sitelinks": [(str(l.campaign.id), l.campaign_asset.asset.split("/")[-1]) for l in links]}
(SNAP / "launch-readback-2026-09-24.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"enabled campaigns: {len(en_camps)} | enabled budget total ${budget:.2f} | budget of campaigns with an enabled ad group ${serving_budget:.2f}")
for k, v in out["enabled_campaigns"].items(): print("  ", k, v)
for r in rows:
    if r["group_status"] == "ENABLED":
        print(f"  {r['ad_group_id']} {r['ad_group'][:34]:34s} {r['group_primary'][:14]:14s} ads={r['enabled_ads']} kw={r['keywords_enabled']} {r['review']} {r['ad_primary']} {r['urls']}")
print("main-site ads still serving (SWAP-2 pending):", main_site_serving)
print(f"enabled sitelink links: {len(links)} | account-level: {len(acct_sl)} | ad-group-level: {len(agsl)}")
print(f"READBACK FAILS: {len(fails)}")
