#!/usr/bin/env python3
"""Full live readback of the CAMP-I paused campaign build."""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, TZ, RECEIPTS, client, q, write, E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402

plan = load_yaml(str(ROOT / "clients/apogee-lawns/plans/APG-0917-CAMP-I.yaml"))
C0 = plan["campaigns"][0]
c = client()
out, fails = {}, []


def ck(ok, m, detail=""):
    print(f"  [{'OK  ' if ok else 'FAIL'}] {m}{(' -> ' + str(detail)) if detail != '' else ''}")
    if not ok:
        fails.append(m)


print("=" * 78 + "\nCAMPAIGN\n" + "=" * 78)
cp = q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
                    campaign.advertising_channel_type, campaign.bidding_strategy_type,
                    campaign.campaign_budget, campaign.start_date_time, campaign.end_date_time,
                    campaign.target_spend.cpc_bid_ceiling_micros,
                    campaign.network_settings.target_google_search,
                    campaign.network_settings.target_search_network,
                    campaign.network_settings.target_content_network,
                    campaign.network_settings.target_partner_search_network,
                    campaign.geo_target_type_setting.positive_geo_target_type,
                    campaign.final_url_suffix, campaign.keyword_match_type,
                    campaign.primary_status, campaign.primary_status_reasons,
                    campaign.asset_automation_settings
             FROM campaign""")[0].campaign
out["campaign"] = {"id": str(cp.id), "name": cp.name, "status": E(cp.status)}
print(f"  ID            : {cp.id}")
print(f"  Name          : {cp.name}")
print(f"  Status        : {E(cp.status)}   serving_status={E(cp.serving_status)}")
print(f"  primary_status: {E(cp.primary_status)}")
print(f"  reasons       : {[E(r) for r in cp.primary_status_reasons]}")
print(f"  Type          : {E(cp.advertising_channel_type)}")
print(f"  Bidding       : {E(cp.bidding_strategy_type)}  cpc_ceiling=${cp.target_spend.cpc_bid_ceiling_micros/1e6:.2f}")
print(f"  Budget        : {cp.campaign_budget.split('/')[-1]}")
print(f"  Start / End   : {cp.start_date_time} / {cp.end_date_time or '(none)'}")
print(f"  URL suffix    : {cp.final_url_suffix[:80]}...")
print(f"  keyword_match_type (campaign broad match): {E(cp.keyword_match_type)}")
print(f"  asset_automation_settings: {[(E(s.asset_automation_type), E(s.asset_automation_status)) for s in cp.asset_automation_settings]}")
ck(E(cp.status) == "PAUSED", "campaign PAUSED")
ck(E(cp.advertising_channel_type) == "SEARCH", "type SEARCH")
ck(E(cp.bidding_strategy_type) == "TARGET_SPEND", "Maximize Clicks (TARGET_SPEND)")
ck(cp.target_spend.cpc_bid_ceiling_micros == 8_000_000, "CPC ceiling $8.00")
ck(cp.network_settings.target_google_search is True, "Google Search ON")
ck(cp.network_settings.target_search_network is False, "Search Partners OFF")
ck(cp.network_settings.target_content_network is False, "Display OFF")
ck(cp.network_settings.target_partner_search_network is False, "partner search OFF")
ck(E(cp.geo_target_type_setting.positive_geo_target_type) == "PRESENCE", "PRESENCE targeting")
ck(E(cp.keyword_match_type) in ("UNSPECIFIED", "UNKNOWN"), "campaign broad match OFF", E(cp.keyword_match_type))
ck(cp.final_url_suffix == C0["final_url_suffix"], "URL suffix matches plan")

bud = q(c, "SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros, "
           "campaign_budget.status, campaign_budget.delivery_method, "
           "campaign_budget.explicitly_shared FROM campaign_budget")[0].campaign_budget
print(f"\n  Budget ID     : {bud.id}   ${bud.amount_micros/1e6:.2f}/day  {E(bud.status)}  "
      f"{E(bud.delivery_method)} shared={bud.explicitly_shared}")
ck(bud.amount_micros == 16_440_000, "daily budget $16.44")
ck(round(bud.amount_micros/1e6*30.4, 2) == 499.78, "monthly at x30.4 = $499.78")
ck(len(q(c, "SELECT campaign_budget.id FROM campaign_budget")) == 1, "exactly 1 budget (no duplicate)")

print("\n" + "=" * 78 + "\nAD GROUPS / KEYWORDS / ADS\n" + "=" * 78)
ags = q(c, "SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type FROM ad_group ORDER BY ad_group.id")
for r in ags:
    a = r.ad_group
    print(f"  {a.id}  {E(a.status):<8} {E(a.type_):<16} {a.name}")
ck(len(ags) == 2, "2 ad groups")

kws = q(c, """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                     ad_group_criterion.ad_group
              FROM ad_group_criterion WHERE ad_group_criterion.type = KEYWORD""")
print()
for r in kws:
    k = r.ad_group_criterion
    print(f"  {k.criterion_id}  {E(k.keyword.match_type):<7} {E(k.status):<8} "
          f"ag={k.ad_group.split('/')[-1]}  {k.keyword.text}")
ck(len(kws) == 5, "5 keywords")
ck({E(r.ad_group_criterion.keyword.match_type) for r in kws} <= {"EXACT", "PHRASE"}, "only Exact/Phrase")

ads = q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls,
                     ad_group_ad.policy_summary.approval_status,
                     ad_group_ad.policy_summary.review_status,
                     ad_group_ad.policy_summary.policy_topic_entries,
                     ad_group_ad.ad.responsive_search_ad.path1,
                     ad_group_ad.ad.responsive_search_ad.path2,
                     ad_group_ad.ad_group
              FROM ad_group_ad""")
print()
policy = []
for r in ads:
    a = r.ad_group_ad
    topics = [t.topic for t in a.policy_summary.policy_topic_entries]
    policy.extend(topics)
    print(f"  RSA {a.ad.id}  {E(a.status):<8} approval={E(a.policy_summary.approval_status):<12} "
          f"review={E(a.policy_summary.review_status):<16} paths=/{a.ad.responsive_search_ad.path1}/{a.ad.responsive_search_ad.path2}")
    print(f"      final_url: {list(a.ad.final_urls)[0] if a.ad.final_urls else '(none)'}")
    if topics:
        print(f"      POLICY TOPICS: {topics}")
ck(len(ads) == 4, "4 RSAs")
ck(all(list(r.ad_group_ad.ad.final_urls)[0] == C0["final_url"] for r in ads),
   "every RSA final_url matches the approved slug", C0["final_url"])
out["policy_topics"] = sorted(set(policy))

print("\n" + "=" * 78 + "\nCAMPAIGN CRITERIA\n" + "=" * 78)
crit = q(c, """SELECT campaign_criterion.criterion_id, campaign_criterion.type,
                      campaign_criterion.negative, campaign_criterion.keyword.text,
                      campaign_criterion.keyword.match_type,
                      campaign_criterion.location.geo_target_constant,
                      campaign_criterion.language.language_constant
               FROM campaign_criterion""")
locs = [r for r in crit if E(r.campaign_criterion.type_) == "LOCATION"]
langs = [r for r in crit if E(r.campaign_criterion.type_) == "LANGUAGE"]
negs = [r for r in crit if E(r.campaign_criterion.type_) == "KEYWORD" and r.campaign_criterion.negative]
print(f"  locations : {len(locs)}")
print(f"  languages : {len(langs)} -> {[r.campaign_criterion.language.language_constant for r in langs]}")
print(f"  negatives : {len(negs)}  (broad={sum(1 for r in negs if E(r.campaign_criterion.keyword.match_type)=='BROAD')}, "
      f"phrase={sum(1 for r in negs if E(r.campaign_criterion.keyword.match_type)=='PHRASE')})")
ck(len(locs) == 14, "14 location criteria")
ck(len(langs) == 1, "1 language criterion")
ck(len(negs) == 75, "75 negative keywords")
gids = sorted(int(r.campaign_criterion.location.geo_target_constant.split("/")[-1]) for r in locs)
ck(gids == sorted(C0["location"]["geo_target_constant_ids"]), "geo IDs match the plan exactly")
ck(9233865 in gids, "Nemaha Precinct 9233865 present")
ck(21162 not in gids, "state of Nebraska NOT targeted")
sched = [r for r in crit if E(r.campaign_criterion.type_) == "AD_SCHEDULE"]
ck(len(sched) == 0, "0 ad schedule criteria (24/7 by design)")

print("\n" + "=" * 78 + "\nASSETS\n" + "=" * 78)
cas = q(c, """SELECT campaign_asset.asset, campaign_asset.field_type, campaign_asset.status,
                     asset.id, asset.type, asset.callout_asset.callout_text,
                     asset.structured_snippet_asset.header,
                     asset.structured_snippet_asset.values
              FROM campaign_asset""")
for r in cas:
    label = r.asset.callout_asset.callout_text or r.asset.structured_snippet_asset.header
    extra = list(r.asset.structured_snippet_asset.values)
    print(f"  {r.asset.id}  {E(r.campaign_asset.field_type):<20} {E(r.campaign_asset.status):<8} {label}"
          + (f"  {extra}" if extra else ""))
ck(len(cas) == 7, "7 campaign assets linked")
ck(sum(1 for r in cas if E(r.campaign_asset.field_type) == "CALLOUT") == 6, "6 callouts")
ck(sum(1 for r in cas if E(r.campaign_asset.field_type) == "STRUCTURED_SNIPPET") == 1, "1 structured snippet")
callassets = q(c, "SELECT asset.id FROM asset WHERE asset.type = CALL")
ck(len(callassets) == 0, "0 call assets (deferred on routing verification, per plan)")

print("\n" + "=" * 78 + "\nCONVERSION GOALS\n" + "=" * 78)
cfg = q(c, """SELECT conversion_goal_campaign_config.goal_config_level,
                     conversion_goal_campaign_config.custom_conversion_goal
              FROM conversion_goal_campaign_config""")
for r in cfg:
    x = r.conversion_goal_campaign_config
    print(f"  goal_config_level = {E(x.goal_config_level)}   custom_goal={x.custom_conversion_goal or '(none)'}")
    ck(E(x.goal_config_level) == "CAMPAIGN", "goal_config_level CAMPAIGN")
    ck(not x.custom_conversion_goal, "no custom goal attached")

ccg = q(c, """SELECT campaign_conversion_goal.category, campaign_conversion_goal.origin,
                     campaign_conversion_goal.biddable FROM campaign_conversion_goal""")
got = {}
for r in ccg:
    x = r.campaign_conversion_goal
    got[(E(x.category), E(x.origin))] = x.biddable
for k in sorted(got):
    flag = "" if got[k] is False or "LEAD" in k[0] else ""
    print(f"  {k[0]:<20} / {k[1]:<16} biddable={got[k]}{flag}")
ck(got.get(("SUBMIT_LEAD_FORM", "WEBSITE")) is True, "SUBMIT_LEAD_FORM/WEBSITE biddable TRUE")
ck(got.get(("PHONE_CALL_LEAD", "CALL_FROM_ADS")) is True, "PHONE_CALL_LEAD/CALL_FROM_ADS biddable TRUE")
ck(got.get(("PHONE_CALL_LEAD", "WEBSITE")) is False, "PHONE_CALL_LEAD/WEBSITE biddable FALSE")
ck(len(q(c, "SELECT custom_conversion_goal.id FROM custom_conversion_goal")) == 0, "0 custom conversion goals")

print("\n  conversion action states:")
for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                        conversion_action.primary_for_goal FROM conversion_action
                 ORDER BY conversion_action.id"""):
    a = r.conversion_action
    print(f"    {a.id}  {'PRIMARY' if a.primary_for_goal else 'SECONDARY':<9}  {a.name}")

print("\n" + "=" * 78)
print(f"READBACK QA: {len(fails)} failures")
for f in fails:
    print(f"  FAIL: {f}")
print("=" * 78)

out.update({
    "campaign_id": str(cp.id), "campaign_status": E(cp.status),
    "serving_status": E(cp.serving_status), "primary_status": E(cp.primary_status),
    "primary_status_reasons": [E(r) for r in cp.primary_status_reasons],
    "budget_id": str(bud.id), "daily_budget": bud.amount_micros/1e6,
    "cpc_ceiling": cp.target_spend.cpc_bid_ceiling_micros/1e6,
    "final_url": C0["final_url"],
    "ad_groups": [{"id": str(r.ad_group.id), "name": r.ad_group.name, "status": E(r.ad_group.status)} for r in ags],
    "keywords": [{"id": str(r.ad_group_criterion.criterion_id), "text": r.ad_group_criterion.keyword.text,
                  "match": E(r.ad_group_criterion.keyword.match_type),
                  "status": E(r.ad_group_criterion.status)} for r in kws],
    "ads": [{"id": str(r.ad_group_ad.ad.id), "status": E(r.ad_group_ad.status),
             "approval": E(r.ad_group_ad.policy_summary.approval_status),
             "review": E(r.ad_group_ad.policy_summary.review_status),
             "topics": [t.topic for t in r.ad_group_ad.policy_summary.policy_topic_entries]} for r in ads],
    "locations": len(locs), "languages": len(langs), "negatives": len(negs),
    "assets": [{"id": str(r.asset.id), "field_type": E(r.campaign_asset.field_type)} for r in cas],
    "campaign_conversion_goals": {f"{k[0]}/{k[1]}": v for k, v in got.items()},
    "qa_failures": len(fails),
    "eu_political_declaration": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
    "forced_correction": "ad_serving_optimization_status omitted - deprecated at campaign level",
    "read_local": datetime.datetime.now(TZ).isoformat(),
})
write(RECEIPTS / "2026-09-17-campi-readback.json", out)
