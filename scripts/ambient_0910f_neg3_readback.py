#!/usr/bin/env python3
"""Readback for AMB-0910-COMM-NEG-3 51CF5986F18A + unrelated-resource verification."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
identity_gate(c, verbose=True)
NEW_AG, RES_AG, CAMP = "199748801029", "202339087634", "24132507747"
SHIP = ["residential", "homeowner", "house", "diy", "job", "jobs", "career", "careers",
        "salary", "salaries", "course", "courses", "parts", "used",
        "wholesale", "supplier", "supply"]
HOLD = ["school", "schools", "rent", "rental", "training"]
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
FAIL = []


def chk(label, got, want):
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {got!r}" + ("" if ok else f" != {want!r}"))
    if not ok:
        FAIL.append(f"{label}: {got!r} != {want!r}")


print("\n=== READBACK: AMB-0910-COMM-NEG-3 51CF5986F18A ===")
negs = []
for r in q(c, f"SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
              f"ad_group_criterion.keyword.match_type, ad_group_criterion.status, "
              f"ad_group_criterion.negative, ad_group_criterion.type "
              f"FROM ad_group_criterion WHERE ad_group.id = {NEW_AG} "
              f"AND ad_group_criterion.negative = TRUE"):
    k = r.ad_group_criterion
    negs.append({"id": str(k.criterion_id), "text": k.keyword.text,
                 "match": E(k.keyword.match_type), "status": E(k.status),
                 "type": E(k.type_)})
print(f"  ad-group negatives now on {NEW_AG}: {len(negs)}")
for n in sorted(negs, key=lambda z: SHIP.index(z["text"]) if z["text"] in SHIP else 99):
    print(f"    {n['match']:<7}{n['status']:<9}{n['text']}")
out["negatives"] = negs

chk("negative count", len(negs), 17)
chk("all BROAD", sorted({n["match"] for n in negs}), ["BROAD"])
chk("all ENABLED", sorted({n["status"] for n in negs}), ["ENABLED"])
chk("all KEYWORD type", sorted({n["type"] for n in negs}), ["KEYWORD"])
chk("exact term set", sorted(n["text"] for n in negs), sorted(SHIP))
chk("no duplicates created", len({n["text"] for n in negs}), 17)
present = {n["text"] for n in negs}
for h in HOLD:
    chk(f"HELD term {h!r} absent", h in present, False)

print("\n=== THE AD GROUP ITSELF ===")
ag = q(c, f"SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.cpc_bid_micros, "
          f"campaign.id FROM ad_group WHERE ad_group.id = {NEW_AG}")[0]
chk("ad group still PAUSED", E(ag.ad_group.status), "PAUSED")
chk("ad group name", ag.ad_group.name, "SKAG | Commercial HVAC Installation")
chk("ad group campaign", str(ag.campaign.id), CAMP)
chk("ad group cpc_bid_micros", ag.ad_group.cpc_bid_micros, 10000)
pos = [(r.ad_group_criterion.keyword.text, E(r.ad_group_criterion.keyword.match_type))
       for r in q(c, f"SELECT ad_group_criterion.keyword.text, "
                     f"ad_group_criterion.keyword.match_type FROM ad_group_criterion "
                     f"WHERE ad_group.id = {NEW_AG} AND ad_group_criterion.negative = FALSE "
                     f"AND ad_group_criterion.type = 'KEYWORD'")]
chk("positive keywords unchanged", sorted(pos),
    [("commercial hvac installation", "EXACT"), ("commercial hvac installation", "PHRASE")])
chk("still ZERO ads on the commercial ad group",
    len(q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group.id = {NEW_AG}")), 0)

print("\n=== UNRELATED RESOURCES ===")
res = q(c, f"SELECT ad_group.status FROM ad_group WHERE ad_group.id = {RES_AG}")[0]
chk("residential ad group still ENABLED", E(res.ad_group.status), "ENABLED")
chk("residential ad-group negatives still ZERO",
    len(q(c, f"SELECT ad_group_criterion.criterion_id FROM ad_group_criterion "
             f"WHERE ad_group.id = {RES_AG} AND ad_group_criterion.negative = TRUE")), 0)
live = sorted(str(r.ad_group_ad.ad.id)
              for r in q(c, f"SELECT ad_group_ad.ad.id, ad_group_ad.status, "
                            f"ad_group_ad.policy_summary.approval_status FROM ad_group_ad "
                            f"WHERE ad_group.id = {RES_AG}")
              if E(r.ad_group_ad.status) == "ENABLED"
              and E(r.ad_group_ad.policy_summary.approval_status) == "APPROVED")
chk("residential ENABLED+APPROVED ads", live, ["821319509197", "821319509200"])

state = {}
for r in q(c, f"SELECT campaign.id, campaign.status, campaign_budget.amount_micros, "
              f"campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign.geo_target_type_setting.positive_geo_target_type "
              f"FROM campaign WHERE campaign.id IN ({IN5})"):
    state[str(r.campaign.id)] = r
CEIL = {"24132507741": 25000000, "24132507744": 25000000, "24132507747": 30000000,
        "24132507750": 25000000, "24132507753": 30000000}
BUD = {"24132507741": 141450000, "24132507744": 5000000, "24132507747": 176150000,
       "24132507750": 78950000, "24132507753": 20000000}
for cid in CEIL:
    chk(f"{NAME[cid]} ceiling", state[cid].campaign.target_spend.cpc_bid_ceiling_micros,
        CEIL[cid])
    chk(f"{NAME[cid]} budget", state[cid].campaign_budget.amount_micros, BUD[cid])
    chk(f"{NAME[cid]} status", E(state[cid].campaign.status), "ENABLED")
    chk(f"{NAME[cid]} geo", E(state[cid].campaign.geo_target_type_setting
                              .positive_geo_target_type), "PRESENCE")
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
n_cneg = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                  f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='KEYWORD' "
                  f"AND campaign_criterion.negative=TRUE"))
n_acc = len(q(c, "SELECT shared_criterion.criterion_id FROM shared_criterion "
                 "WHERE shared_set.id = 11252984411"))
for lbl, got, want in [("campaigns (excl REMOVED)", n_camp, 23),
                       ("ad groups (excl REMOVED)", n_ag, 69),
                       ("geo criteria on the five", n_geo, 375),
                       ("IP blocks", n_ip, 2796), ("shared sets", n_ss, 17),
                       ("conversion actions", n_ca, 16),
                       ("CAMPAIGN-level negatives on the five", n_cneg, 6158),
                       ("account-level list members", n_acc, 271)]:
    chk(lbl, got, want)
acct = {r.shared_criterion.keyword.text.strip().lower()
        for r in q(c, "SELECT shared_criterion.keyword.text FROM shared_criterion "
                      "WHERE shared_set.id = 11252984411")}
chk("'commercial' still absent from the account-level list", "commercial" in acct, False)
for r in q(c, "SELECT customer.tracking_url_template FROM customer"):
    chk("ClickCease tracking template intact",
        "clickcease" in r.customer.tracking_url_template.lower(), True)

print(f"\n=== READBACK RESULT: {len(FAIL)} FAIL ===")
for f in FAIL:
    print(f"  {f}")
out["readback_failures"] = FAIL
write(EVID / "2026-09-10f-neg3-readback.json", out)
