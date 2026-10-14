#!/usr/bin/env python3
"""Immediate readback of every changed field + proof of zero collateral change."""
from __future__ import annotations
import sys, json, re, unicodedata, datetime
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
before = json.load(open(SNAP / "before-state-2026-09-10.json", encoding="utf-8"))
out = {"read_local": datetime.datetime.now(TZ).isoformat()}
fails = []


def chk(cond, msg):
    print(f"  [{'PASS' if cond else 'FAIL'}] {msg}")
    if not cond:
        fails.append(msg)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


print("=== IDENTITY RE-GATE BEFORE READBACK ===")
ident = identity_gate(c, verbose=False)
chk(all(ident["checks"].values()), "all six identity fields + both manager links still PASS")

# ---------------------------------------------------- COMP-1
print("\n=== READBACK: AMB-0909C-COMP-1 (3 EXACT negatives created) ===")
rec = json.load(open(ROOT / "receipts/live/AMB-0909C-COMP-1-2026-09-10-EXECUTED.json",
                     encoding="utf-8"))
want = {r.split("/")[-1] for r in rec["resource_names"]}
got = {}
for r in q(c, "SELECT campaign.id, campaign_criterion.criterion_id, "
              "campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, "
              "campaign_criterion.status, campaign_criterion.negative, "
              "campaign_criterion.type, campaign_criterion.resource_name "
              "FROM campaign_criterion WHERE campaign.id = 24132507747 "
              "AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE "
              "AND campaign_criterion.status = 'ENABLED'"):
    x = r.campaign_criterion
    got[f"{r.campaign.id}~{x.criterion_id}"] = {
        "text": x.keyword.text, "match": E(x.keyword.match_type), "status": E(x.status),
        "negative": x.negative, "type": E(x.type_), "resource_name": x.resource_name,
        "campaign": str(r.campaign.id)}
for k in sorted(want):
    v = got.get(k)
    chk(v is not None, f"criterion {k} exists and is ENABLED")
    if v:
        chk(v["match"] == "EXACT", f"  {v['text']!r} is EXACT")
        chk(v["negative"] is True, f"  {v['text']!r} negative=true")
        chk(v["campaign"] == "24132507747", f"  {v['text']!r} attached only to HVAC Installation")
        print(f"       -> {v['resource_name']}  [{v['match']}] {v['text']!r}")
out["comp1_readback"] = {k: got.get(k) for k in want}

allneg = []
for r in q(c, "SELECT campaign.id, campaign_criterion.criterion_id, "
              "campaign_criterion.keyword.text, campaign_criterion.keyword.match_type "
              "FROM campaign_criterion WHERE campaign_criterion.type = 'KEYWORD' "
              "AND campaign_criterion.negative = TRUE AND campaign_criterion.status = 'ENABLED'"):
    allneg.append({"camp": str(r.campaign.id), "crit": str(r.campaign_criterion.criterion_id),
                   "text": r.campaign_criterion.keyword.text,
                   "match": E(r.campaign_criterion.keyword.match_type)})
on5 = [n for n in allneg if n["camp"] in FIVE]
bycamp = Counter(NAME[n["camp"]] for n in on5)
BEFORE5 = {"AC Repair": 1136, "Gas Boiler Repair": 1132, "HVAC Installation": 1435,
           "HVAC Repair": 1138, "HVAC Replacement": 1319}
EXPECT5 = {"AC Repair": 1135, "Gas Boiler Repair": 1131, "HVAC Installation": 1437,
           "HVAC Repair": 1137, "HVAC Replacement": 1318}
print(f"\n  campaign negatives ENABLED on the five, before -> now -> expected:")
for k in BEFORE5:
    print(f"    {k:<20} {BEFORE5[k]:>5} -> {bycamp[k]:>5}   expected {EXPECT5[k]}")
    chk(bycamp[k] == EXPECT5[k], f"{k} negative count is {EXPECT5[k]}")
out["negative_counts"] = {"before": BEFORE5, "after": dict(bycamp), "expected": EXPECT5}

# ---------------------------------------------------- ADS-1
print("\n=== READBACK: AMB-0909-ADS-1 (2 status-only pauses) ===")
TARGETS = {("202339087634", "820900825434"), ("200159223798", "820944944368")}
ads = []
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, "
              f"ad_group_ad.policy_summary.approval_status, ad_group_ad.ad_strength, "
              f"ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.headlines "
              f"FROM ad_group_ad WHERE campaign.id IN ({IN5})"):
    x = r.ad_group_ad
    ads.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id), "ad": str(x.ad.id),
                "status": E(x.status), "approval": E(x.policy_summary.approval_status),
                "strength": E(x.ad_strength), "urls": list(x.ad.final_urls),
                "n_headlines": len(x.ad.responsive_search_ad.headlines)})
out["ads_readback"] = ads
beforeads = {(a["ag"], a["ad"]): a for a in before["ads"]}
for ag, ad in sorted(TARGETS):
    a = next((z for z in ads if z["ag"] == ag and z["ad"] == ad), None)
    chk(a is not None and a["status"] == "PAUSED", f"ad {ad} is now PAUSED")
    b = beforeads[(ag, ad)]
    if a:
        chk(a["approval"] == b["approval"], f"  ad {ad} approval unchanged ({a['approval']})")
        chk(a["urls"] == b["urls"], f"  ad {ad} final URLs unchanged")
        chk(a["n_headlines"] == 15, f"  ad {ad} still has 15 headlines (text untouched)")
    keep = [z for z in ads if z["ag"] == ag and z["status"] == "ENABLED"
            and z["approval"] == "APPROVED"]
    chk(len(keep) == 2, f"  ad group {ag} still has exactly 2 ENABLED+APPROVED RSAs")
    print(f"       remaining enabled+approved in {ag}: {[z['ad'] for z in keep]}")
changed = [(a["ag"], a["ad"]) for a in ads
           if beforeads.get((a["ag"], a["ad"]))
           and beforeads[(a["ag"], a["ad"])]["status"] != a["status"]]
chk(set(changed) == TARGETS, f"exactly the 2 target ads changed status ({len(changed)} changed)")

# ---------------------------------------------------- NEG-SAVAGE
print("\n=== READBACK: AMB-0909C-NEG-SAVAGE (5 removals) ===")
sav_left = [n for n in allneg if "savage" in norm(n["text"]).split() and n["camp"] in FIVE]
chk(len(sav_left) == 0, f"zero 'savage' campaign negatives remain on the five ({len(sav_left)})")
acct_now = []
for r in q(c, "SELECT shared_criterion.resource_name, shared_criterion.keyword.text, "
              "shared_criterion.keyword.match_type FROM shared_criterion "
              "WHERE shared_set.id = 11252984411"):
    acct_now.append({"rn": r.shared_criterion.resource_name,
                     "text": r.shared_criterion.keyword.text,
                     "match": E(r.shared_criterion.keyword.match_type)})
chk(len(acct_now) == 272, f"account-level set 11252984411 still holds 272 members "
                          f"({len(acct_now)})")
chk(not any("savage" in norm(a["text"]).split() for a in acct_now),
    "no 'savage' blocker at account level")
geo = []
for r in q(c, f"SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.status, "
              f"campaign_criterion.negative, campaign_criterion.location.geo_target_constant "
              f"FROM campaign_criterion WHERE campaign.id IN ({IN5}) "
              f"AND campaign_criterion.type = 'LOCATION'"):
    geo.append({"camp": str(r.campaign.id),
                "geo": r.campaign_criterion.location.geo_target_constant.split("/")[-1],
                "negative": r.campaign_criterion.negative,
                "status": E(r.campaign_criterion.status)})
sav_geo = [g for g in geo if g["geo"] == "1018704" and not g["negative"]
           and g["status"] == "ENABLED"]
chk(len(sav_geo) == 5, f"Savage MD 1018704 still an ENABLED positive target on all five "
                       f"({len(sav_geo)})")
chk(len(geo) == 375, f"geo criteria on the five unchanged at 375 ({len(geo)})")
out["savage_readback"] = {"remaining_savage_negatives_on_five": len(sav_left),
                          "savage_geo_targets": len(sav_geo), "geo_total": len(geo),
                          "account_set_members": len(acct_now)}

# ---------------------------------------------------- COLLATERAL
print("\n=== UNRELATED-RESOURCE VERIFICATION (before vs now) ===")
now = {}
now["campaigns_non_removed"] = len(q(c, "SELECT campaign.id FROM campaign "
                                        "WHERE campaign.status != 'REMOVED'"))
now["campaigns_enabled"] = len(q(c, "SELECT campaign.id FROM campaign "
                                    "WHERE campaign.status = 'ENABLED'"))
now["ad_groups_non_removed"] = len(q(c, "SELECT ad_group.id FROM ad_group "
                                        "WHERE ad_group.status != 'REMOVED'"))
now["ad_schedules_on_five"] = len(q(c, f"SELECT campaign_criterion.criterion_id FROM "
                                       f"campaign_criterion WHERE campaign.id IN ({IN5}) "
                                       f"AND campaign_criterion.type = 'AD_SCHEDULE'"))
now["ip_blocks"] = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                            "WHERE campaign_criterion.type = 'IP_BLOCK'"))
now["ip_blocks_on_five"] = len(q(c, f"SELECT campaign_criterion.criterion_id FROM "
                                    f"campaign_criterion WHERE campaign.id IN ({IN5}) "
                                    f"AND campaign_criterion.type = 'IP_BLOCK'"))
now["shared_sets"] = len(q(c, "SELECT shared_set.id FROM shared_set"))
now["conversion_actions"] = len(q(c, "SELECT conversion_action.id FROM conversion_action "
                                     "WHERE conversion_action.status != 'REMOVED'"))
now["shared_sets_attached_to_five"] = len([
    r for r in q(c, "SELECT campaign.id, campaign_shared_set.shared_set "
                    "FROM campaign_shared_set") if str(r.campaign.id) in FIVE])
livekw = []
for r in q(c, f"SELECT campaign.id, ad_group.status, ad_group_criterion.criterion_id, "
              f"ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
              f"ad_group_criterion.status, ad_group_criterion.system_serving_status "
              f"FROM ad_group_criterion WHERE campaign.id IN ({IN5}) "
              f"AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE "
              f"AND ad_group_criterion.status = 'ENABLED'"):
    if E(r.ad_group.status) == "ENABLED":
        livekw.append({"camp": NAME[str(r.campaign.id)],
                       "text": r.ad_group_criterion.keyword.text,
                       "match": E(r.ad_group_criterion.keyword.match_type),
                       "serving": E(r.ad_group_criterion.system_serving_status)})
now["live_positive_keywords"] = len(livekw)
now["live_keywords_eligible"] = sum(1 for k in livekw if k["serving"] == "ELIGIBLE")
buds = {}
ceil = {}
for r in q(c, f"SELECT campaign.id, campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign.bidding_strategy_type, campaign.status FROM campaign "
              f"WHERE campaign.id IN ({IN5})"):
    ceil[NAME[str(r.campaign.id)]] = {
        "ceiling": r.campaign.target_spend.cpc_bid_ceiling_micros,
        "bidding": E(r.campaign.bidding_strategy_type), "status": E(r.campaign.status)}
for r in q(c, "SELECT campaign_budget.id, campaign_budget.amount_micros, "
              "campaign_budget.explicitly_shared FROM campaign_budget "
              "WHERE campaign_budget.status = 'ENABLED'"):
    buds[str(r.campaign_budget.id)] = {
        "micros": r.campaign_budget.amount_micros,
        "shared": r.campaign_budget.explicitly_shared}
now["ceilings"] = ceil
now["five_budgets"] = {b: buds.get(b) for b in ["15787409435", "15787409438", "15787409441",
                                                "15787409444", "15787409447"]}
out["after_state"] = now

chk(now["campaigns_non_removed"] == 23, f"campaigns non-removed 23 ({now['campaigns_non_removed']})")
chk(now["campaigns_enabled"] == 5, f"campaigns ENABLED 5 ({now['campaigns_enabled']})")
chk(now["ad_groups_non_removed"] == len(before["ad_groups"]),
    f"ad groups unchanged at {len(before['ad_groups'])} ({now['ad_groups_non_removed']})")
chk(now["ad_schedules_on_five"] == 30, f"ad schedules 30 ({now['ad_schedules_on_five']})")
chk(now["ip_blocks"] == 2796, f"IP blocks 2796 ({now['ip_blocks']})")
chk(now["ip_blocks_on_five"] == 0, f"IP blocks on the five still 0 ({now['ip_blocks_on_five']})")
chk(now["shared_sets"] == 17, f"shared sets 17 ({now['shared_sets']})")
chk(now["shared_sets_attached_to_five"] == 0, "no shared list attached to the five")
chk(now["conversion_actions"] == 16, f"conversion actions 16 ({now['conversion_actions']})")
chk(now["live_positive_keywords"] == 10,
    f"10 live positive keywords ({now['live_positive_keywords']})")
chk(now["live_keywords_eligible"] == 10,
    f"all 10 live keywords still ELIGIBLE ({now['live_keywords_eligible']})")
for k, v in ceil.items():
    b = before["campaigns"][[c2 for c2 in FIVE if NAME[c2] == k][0]]
    chk(v["ceiling"] == b["ceiling_micros"],
        f"{k} CPC ceiling unchanged at {v['ceiling']}")
    chk(v["bidding"] == "TARGET_SPEND", f"{k} still TARGET_SPEND")
    chk(v["status"] == "ENABLED", f"{k} still ENABLED")
EXPB = {"15787409435": 141450000, "15787409438": 42760000, "15787409441": 176150000,
        "15787409444": 78950000, "15787409447": 26320000}
for b, m in EXPB.items():
    chk(now["five_budgets"][b]["micros"] == m,
        f"budget {b} UNCHANGED at ${m/1e6:.2f} (BUD-1 was not executed)")
    chk(now["five_budgets"][b]["shared"] is False, f"budget {b} still individual, not shared")
chk(ident["manager_links"] == {"2815082755": "ACTIVE", "3373711342": "ACTIVE"},
    "both manager links still ACTIVE")
chk("clickcease" in (ident.get("tracking_url_template") or "").lower(),
    "ClickCease tracking template intact")

print("\n" + "=" * 76)
print(f"READBACK: {len(fails)} FAIL")
for f in fails:
    print("  FAIL:", f)
print("=" * 76)
out["fails"] = fails
write(EVID / "2026-09-10-readback.json", out)
sys.exit(1 if fails else 0)
