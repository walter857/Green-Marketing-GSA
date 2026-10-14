#!/usr/bin/env python3
"""Readback for AMB-0910-COMM-1 A9173FADBA82 + full unrelated-resource verification."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
identity_gate(c, verbose=True)
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
FAIL = []


def chk(label, got, want):
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" != {want!r}"))
    if not ok:
        FAIL.append(f"{label}: {got!r} != {want!r}")


print("\n=== READBACK: AMB-0910-COMM-1 A9173FADBA82 ===")
ags = {}
for r in q(c, "SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type, "
              "ad_group.cpc_bid_micros, campaign.id FROM ad_group "
              "WHERE campaign.id = 24132507747"):
    a = r.ad_group
    ags[a.name] = {"id": str(a.id), "status": E(a.status), "type": E(a.type_),
                   "cpc": a.cpc_bid_micros}
print(f"  ad groups in campaign 24132507747: {len(ags)}")
for n, v in ags.items():
    print(f"    {v['id']:<16}{v['status']:<10}{v['type']:<18}cpc {v['cpc']}  {n}")
chk("ad group count in the campaign", len(ags), 2)
NEW = "SKAG | Commercial HVAC Installation"
chk("new ad group exists", NEW in ags, True)
if NEW in ags:
    NEWID = ags[NEW]["id"]
    out["new_ad_group_id"] = NEWID
    chk("new ad group status", ags[NEW]["status"], "PAUSED")
    chk("new ad group type", ags[NEW]["type"], "SEARCH_STANDARD")
    chk("new ad group cpc_bid_micros", ags[NEW]["cpc"], 10000)

    kws = []
    for r in q(c, f"SELECT ad_group_criterion.keyword.text, "
                  f"ad_group_criterion.keyword.match_type, ad_group_criterion.status, "
                  f"ad_group_criterion.negative, ad_group_criterion.approval_status "
                  f"FROM ad_group_criterion WHERE ad_group.id = {NEWID} "
                  f"AND ad_group_criterion.type='KEYWORD'"):
        k = r.ad_group_criterion
        kws.append({"text": k.keyword.text, "match": E(k.keyword.match_type),
                    "status": E(k.status), "negative": k.negative,
                    "approval": E(k.approval_status)})
    print(f"\n  keywords in the new ad group: {len(kws)}")
    for k in kws:
        print(f"    {'NEG ' if k['negative'] else 'POS '}{k['match']:<8}{k['status']:<9}"
              f"{k['approval']:<12}{k['text']}")
    out["new_keywords"] = kws
    chk("keyword count", len(kws), 2)
    chk("all positive", all(not k["negative"] for k in kws), True)
    chk("all ENABLED", all(k["status"] == "ENABLED" for k in kws), True)
    chk("match types", sorted(k["match"] for k in kws), ["EXACT", "PHRASE"])
    chk("keyword text", sorted({k["text"] for k in kws}), ["commercial hvac installation"])
    chk("no BROAD keyword", any(k["match"] == "BROAD" for k in kws), False)

    ads = q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group.id = {NEWID}")
    chk("new ad group holds ZERO ads", len(ads), 0)
    negs = [k for k in kws if k["negative"]]
    chk("new ad group holds ZERO ad-group negatives (pack set not yet approved)",
        len(negs), 0)

print("\n=== UNRELATED RESOURCES ===")
res = ags.get("SKAG | HVAC Installation")
chk("residential ad group still ENABLED", res["status"] if res else None, "ENABLED")
chk("residential ad group id", res["id"] if res else None, "202339087634")
liveads = [r for r in q(c, "SELECT ad_group_ad.ad.id, ad_group_ad.status, "
                           "ad_group_ad.policy_summary.approval_status FROM ad_group_ad "
                           "WHERE ad_group.id = 202339087634")
           if E(r.ad_group_ad.status) == "ENABLED"
           and E(r.ad_group_ad.policy_summary.approval_status) == "APPROVED"]
chk("residential ENABLED+APPROVED ads",
    sorted(str(r.ad_group_ad.ad.id) for r in liveads), ["821319509197", "821319509200"])

state = {}
for r in q(c, f"SELECT campaign.id, campaign.status, campaign_budget.amount_micros, "
              f"campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign.bidding_strategy_type, "
              f"campaign.geo_target_type_setting.positive_geo_target_type, "
              f"campaign.network_settings.target_search_network, "
              f"campaign.network_settings.target_content_network "
              f"FROM campaign WHERE campaign.id IN ({IN5})"):
    state[str(r.campaign.id)] = r
for cid, r in state.items():
    n = NAME[cid]
    chk(f"{n} status", E(r.campaign.status), "ENABLED")
    chk(f"{n} geo type", E(r.campaign.geo_target_type_setting.positive_geo_target_type),
        "PRESENCE")
    chk(f"{n} search partners off", r.campaign.network_settings.target_search_network, False)
    chk(f"{n} display off", r.campaign.network_settings.target_content_network, False)
CEIL = {"24132507741": 25000000, "24132507744": 25000000, "24132507747": 30000000,
        "24132507750": 25000000, "24132507753": 30000000}
BUD = {"24132507741": 141450000, "24132507744": 5000000, "24132507747": 176150000,
       "24132507750": 78950000, "24132507753": 20000000}
for cid, want in CEIL.items():
    chk(f"{NAME[cid]} ceiling", state[cid].campaign.target_spend.cpc_bid_ceiling_micros, want)
for cid, want in BUD.items():
    chk(f"{NAME[cid]} budget", state[cid].campaign_budget.amount_micros, want)
tot = sum(BUD.values()) / 1e6
print(f"\n  combined daily ${tot:.2f} x 30.4 = ${tot*30.4:,.2f}  "
      f"headroom ${13000 - tot*30.4:,.2f}")
chk("within the $13,000 Search maximum", tot * 30.4 <= 13000, True)

n_camp = len(q(c, "SELECT campaign.id FROM campaign WHERE campaign.status != 'REMOVED'"))
n_ag = len(q(c, "SELECT ad_group.id FROM ad_group WHERE ad_group.status != 'REMOVED'"))
n_geo = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                 f"WHERE campaign_criterion.type='LOCATION' AND campaign.id IN ({IN5})"))
n_ip = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                "WHERE campaign_criterion.type = 'IP_BLOCK'"))
n_ss = len(q(c, "SELECT shared_set.id FROM shared_set"))
n_ca = len(q(c, "SELECT conversion_action.id FROM conversion_action "
                "WHERE conversion_action.status != 'REMOVED'"))
n_neg = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                 f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='KEYWORD' "
                 f"AND campaign_criterion.negative=TRUE"))
n_acc = len(q(c, "SELECT shared_criterion.criterion_id FROM shared_criterion "
                 "WHERE shared_set.id = 11252984411"))
for lbl, got, want in [("campaigns (excl REMOVED)", n_camp, 23),
                       ("ad groups (excl REMOVED)", n_ag, 69),
                       ("geo criteria on the five", n_geo, 375),
                       ("IP blocks", n_ip, 2796), ("shared sets", n_ss, 17),
                       ("conversion actions", n_ca, 16),
                       ("campaign negatives on the five", n_neg, 6158),
                       ("account-level negative members", n_acc, 271)]:
    chk(lbl, got, want)
print("  (ad groups 68 -> 69 is the one ad group this package created, and is expected)")

for r in q(c, "SELECT customer.id, customer.tracking_url_template FROM customer"):
    t = r.customer.tracking_url_template
    chk("account tracking template still ClickCease", "clickcease" in t.lower(), True)

print(f"\n=== READBACK RESULT: {len(FAIL)} FAIL ===")
for f in FAIL:
    print(f"  {f}")
out["readback_failures"] = FAIL
write(EVID / "2026-09-10d-comm1-readback.json", out)
