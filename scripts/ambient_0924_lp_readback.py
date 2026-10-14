#!/usr/bin/env python3
"""Ambient | 2026-09-24 | READBACK of NEG-THERMO-1, PAUSE-2 and CREATE-2. READ-ONLY."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, PLANS, RECEIPTS, SNAP

c = client(); identity_gate(c, verbose=False)
res = {"PASS": 0, "FAIL": []}


def chk(ok, label):
    if ok: res["PASS"] += 1
    else: res["FAIL"].append(label); print("  FAIL", label)


def plan(n): return json.loads((PLANS / f"{n}.json").read_text(encoding="utf-8"))
def rcpt(n): return json.loads((RECEIPTS / f"{n}-EXECUTED.json").read_text(encoding="utf-8"))


# NEG
neg = plan("AMB-0924-NEG-THERMO-1")
have = {(str(r.campaign.id), r.campaign_criterion.keyword.text.lower(), E(r.campaign_criterion.keyword.match_type))
        for r in q(c, """SELECT campaign.id, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
                         FROM campaign_criterion WHERE campaign_criterion.type = 'KEYWORD'
                         AND campaign_criterion.negative = TRUE""")}
for o in neg["operations"]:
    if o["op"] == "ADD_CAMPAIGN_NEGATIVE":
        chk((o["campaign_id"], o["text"], "PHRASE") in have, f"neg {o['campaign_id']} {o['text']}")
acct = [r.shared_criterion.keyword.text for r in q(c, """SELECT shared_criterion.keyword.text FROM shared_criterion
        WHERE shared_set.id = 11252984411 AND shared_criterion.type = 'KEYWORD'""")]
chk(not any(t.lower() in ("thermostat", "thermostats") for t in acct), "account list still has thermostat")
print(f"NEG: account-level list now {len(acct)} keywords, thermostat removed")

# PAUSE
pz = plan("AMB-0924-LP-PAUSE-2")
ags = {str(r.ad_group.id): E(r.ad_group.status) for r in q(c, "SELECT ad_group.id, ad_group.status FROM ad_group WHERE campaign.status != 'REMOVED'")}
links = {(str(r.campaign.id), r.campaign_asset.asset.split("/")[-1]): E(r.campaign_asset.status)
         for r in q(c, """SELECT campaign.id, campaign.status, campaign_asset.asset, campaign_asset.status FROM campaign_asset
                         WHERE campaign_asset.field_type = 'SITELINK' AND campaign.status != 'REMOVED'""")}
for o in pz["operations"]:
    if o["op"] == "PAUSE_AD_GROUP": chk(ags.get(o["ad_group_id"]) == "PAUSED", f"ad group {o['ad_group_id']} not PAUSED")
    else: chk(links.get((o["campaign_id"], o["asset_id"])) == "PAUSED", f"link {o['campaign_id']}~{o['asset_id']} not PAUSED")

# CREATE
cr, cp = rcpt("AMB-0924-LP-CREATE-2"), plan("AMB-0924-LP-CREATE-2")
sl_ids = cr["committed"]["sitelink_assets"]
assets = {str(r.asset.id): r for r in q(c, "SELECT asset.id, asset.sitelink_asset.link_text, asset.sitelink_asset.description1, asset.sitelink_asset.description2, asset.final_urls FROM asset WHERE asset.type = 'SITELINK'")}
for o in cp["operations"]:
    if o["op"] == "CREATE_SITELINK_ASSET":
        a = assets.get(sl_ids[o["key"]])
        chk(a is not None and a.asset.sitelink_asset.link_text == o["link_text"]
            and list(a.asset.final_urls) == [o["final_url"]]
            and a.asset.sitelink_asset.description1 == o["description1"], f"sitelink {o['key']}")
existing = {"SL_HVACINST": "410638276380", "SL_HVACREPL": "410638278156", "SL_HVACREP": "410638280067", "SL_GASBOIL": "410465469923"}
allsl = {**existing, **sl_ids}
for o in cp["operations"]:
    if o["op"] == "LINK_SITELINK_TO_CAMPAIGN_PAUSED":
        chk(links.get((o["campaign_id"], allsl[o["sitelink"]])) == "PAUSED", f"new link {o['campaign_id']} {o['sitelink']}")
ads = {}
for r in q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
                 ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions,
                 ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, ad_group.id
                 FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
    ads[str(r.ad_group_ad.ad.id)] = r
review = {}
for m in cr["committed"]["rsas"]:
    a = ads.get(m["ad_id"])
    ok = (a is not None and E(a.ad_group_ad.status) == "PAUSED" and str(a.ad_group.id) == m["ad_group_id"]
          and list(a.ad_group_ad.ad.final_urls) == [m["final_url"]] and not a.ad_group_ad.ad.final_mobile_urls)
    chk(ok, f"RSA {m['ad_id']} {m['ad_group']}")
    if a is not None:
        k = (E(a.ad_group_ad.policy_summary.approval_status), E(a.ad_group_ad.policy_summary.review_status))
        review[k] = review.get(k, 0) + 1
print(f"CREATE: {len(sl_ids)} sitelinks, {len(cr['committed']['rsas'])} RSAs | review status: {review}")
print(f"\nREADBACK PASS {res['PASS']} / FAIL {len(res['FAIL'])}")
(SNAP / "lp-readback-2026-09-24.json").write_text(json.dumps({"when": datetime.datetime.now(TZ).isoformat(),
    "pass": res["PASS"], "fail": res["FAIL"], "review": {f"{k[0]}/{k[1]}": v for k, v in review.items()}}, indent=1), encoding="utf-8")
