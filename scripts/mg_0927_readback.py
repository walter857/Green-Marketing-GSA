#!/usr/bin/env python3
"""2026-09-27 READ-ONLY readback QA for MG-0926-BUD / -NEG / -RSA / -PMAX against their plan manifests."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import CID, PLANS, ROOT, E, client, q  # noqa: E402

REC = ROOT / "clients" / "mastergrass-lawn-care" / "receipts"
c = client()
res = []


def check(name, ok, detail=""):
    res.append((name, bool(ok), detail))


P = {k: json.loads((PLANS / f"{k}.json").read_text(encoding="utf-8")) for k in ("MG-0926-BUD", "MG-0926-NEG", "MG-0926-RSA", "MG-0926-PMAX")}
R = {k: json.loads((REC / f"{k}-EXECUTED.json").read_text(encoding="utf-8")) for k in P}
LAND, HARD = "23905193676", "23914692658"

# ---- BUD + untouched campaigns
b = {str(r.campaign.id): (r.campaign_budget.amount_micros / 1e6, E(r.campaign.bidding_strategy_type), E(r.campaign.status))
     for r in q(c, "SELECT campaign.id, campaign.status, campaign.bidding_strategy_type, campaign_budget.amount_micros FROM campaign WHERE campaign.status != 'REMOVED'")}
check("BUD Hardscaping budget 13.00", b[HARD][0] == 13.0, b[HARD])
check("Landscaping untouched (132.00, MAXIMIZE_CONVERSIONS, ENABLED)", b[LAND] == (132.0, "MAXIMIZE_CONVERSIONS", "ENABLED"), b[LAND])
check("Hardscaping still ENABLED / MAXIMIZE_CONVERSIONS", b[HARD][1:] == ("MAXIMIZE_CONVERSIONS", "ENABLED"), b[HARD])

# ---- NEG
ss = [n for n in R["MG-0926-NEG"]["created_or_updated"] if "/sharedSets/" in n and "~" not in n][0]
ssid = ss.split("/")[-1]
row = q(c, f"SELECT shared_set.name, shared_set.status, shared_set.type, shared_set.member_count, shared_set.reference_count FROM shared_set WHERE shared_set.id = {ssid}")[0].shared_set
members = Counter()
texts = set()
for r in q(c, f"SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type FROM shared_criterion WHERE shared_set.id = {ssid}"):
    members[E(r.shared_criterion.keyword.match_type)] += 1
    texts.add((r.shared_criterion.keyword.text, E(r.shared_criterion.keyword.match_type)))
plan_members = {tuple(x) for x in P["MG-0926-NEG"]["members"]}
check("NEG shared set ENABLED NEGATIVE_KEYWORDS", E(row.status) == "ENABLED" and E(row.type_) == "NEGATIVE_KEYWORDS", row.name)
check("NEG members == plan (407: 379 phrase / 28 exact)", texts == plan_members and members == Counter({"PHRASE": 379, "EXACT": 28}), dict(members))
links = {str(r.campaign.id): E(r.campaign_shared_set.status) for r in q(c, f"SELECT campaign.id, campaign_shared_set.status FROM campaign_shared_set WHERE shared_set.id = {ssid}")}
check("NEG list attached to Landscaping + Hardscaping ENABLED", links.get(LAND) == "ENABLED" and links.get(HARD) == "ENABLED", links)
hard_neg = {r.campaign_criterion.keyword.text for r in q(c, f"SELECT campaign_criterion.keyword.text FROM campaign_criterion WHERE campaign.id = {HARD} AND campaign_criterion.negative = TRUE AND campaign_criterion.type = 'KEYWORD'")}
check("NEG 7 Hardscaping cross-negatives present", set(P["MG-0926-NEG"]["hardscaping_cross_negatives_phrase"]) <= hard_neg, len(hard_neg))

# ---- RSA
new_ads = [n for n in R["MG-0926-RSA"]["created_or_updated"] if "/adGroupAds/" in n]
check("RSA 20 ad resources created", len(new_ads) == 20, len(new_ads))
ids = ",".join(n.split("~")[-1] for n in new_ads)
got = {}
for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls,
                   ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions,
                   ad_group_ad.ad.responsive_search_ad.path1, ad_group_ad.ad.responsive_search_ad.path2,
                   ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status
                FROM ad_group_ad WHERE ad_group_ad.ad.id IN ({ids})"""):
    a = r.ad_group_ad
    heads = [(h.text, E(h.pinned_field) if h.pinned_field else None) for h in a.ad.responsive_search_ad.headlines]
    got.setdefault(str(r.ad_group.id), []).append({"id": a.ad.id, "status": E(a.status), "url": list(a.ad.final_urls),
        "heads": heads, "descs": [d.text for d in a.ad.responsive_search_ad.descriptions],
        "path": [a.ad.responsive_search_ad.path1, a.ad.responsive_search_ad.path2],
        "approval": E(a.policy_summary.approval_status), "review": E(a.policy_summary.review_status)})
mism = 0
for ag, g in P["MG-0926-RSA"]["ads"].items():
    rows = got.get(ag, [])
    for k in ("A", "B"):
        want = [(h, p) for h, p in g[k]["headlines"]]
        hit = [x for x in rows if x["heads"] == [tuple(w) for w in want] and x["descs"] == g[k]["descriptions"]
               and x["url"] == [g["final_url"]] and x["path"] == g["path"] and x["status"] == "PAUSED"]
        if len(hit) != 1:
            mism += 1
check("RSA text/pins/url/path/status PAUSED match plan for all 20", mism == 0, f"mismatches {mism}")
check("RSA policy review states", True, dict(Counter((x["approval"], x["review"]) for v in got.values() for x in v)))
old_enabled = sum(1 for r in q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE campaign.id IN ({LAND},{HARD}) AND ad_group_ad.status = 'ENABLED'"))
check("old RSAs untouched (10 ENABLED)", old_enabled == 10, old_enabled)
co = Counter((str(r.campaign.id), E(r.campaign_asset.status), r.asset.callout_asset.callout_text)
             for r in q(c, f"SELECT campaign.id, campaign_asset.status, asset.callout_asset.callout_text FROM campaign_asset WHERE campaign.id IN ({LAND},{HARD}) AND campaign_asset.field_type = 'CALLOUT'"))
newco = {k: v for k, v in co.items() if k[2] in P["MG-0926-RSA"]["new_callouts"]}
check("RSA 3 new callouts linked PAUSED on both campaigns", len(newco) == 6 and all(k[1] == "PAUSED" for k in newco), newco)

# ---- PMAX
camp = [n for n in R["MG-0926-PMAX"]["created_or_updated"] if "/campaigns/" in n and "~" not in n][0]
pid = camp.split("/")[-1]
x = q(c, f"""SELECT campaign.name, campaign.status, campaign.advertising_channel_type, campaign.bidding_strategy_type,
               campaign.maximize_conversions.target_cpa_micros, campaign.brand_guidelines_enabled,
               campaign.geo_target_type_setting.positive_geo_target_type, campaign.asset_automation_settings,
               campaign.contains_eu_political_advertising, campaign_budget.amount_micros, campaign_budget.explicitly_shared
             FROM campaign WHERE campaign.id = {pid}""")[0]
cc = x.campaign
check("PMAX campaign PAUSED / PERFORMANCE_MAX / MAXIMIZE_CONVERSIONS", (E(cc.status), E(cc.advertising_channel_type), E(cc.bidding_strategy_type)) == ("PAUSED", "PERFORMANCE_MAX", "MAXIMIZE_CONVERSIONS"), pid)
check("PMAX budget 20.00 non-shared", x.campaign_budget.amount_micros == 20_000_000 and not x.campaign_budget.explicitly_shared, x.campaign_budget.amount_micros / 1e6)
check("PMAX brand guidelines on, PRESENCE", cc.brand_guidelines_enabled and E(cc.geo_target_type_setting.positive_geo_target_type) == "PRESENCE")
auto = {E(s.asset_automation_type): E(s.asset_automation_status) for s in cc.asset_automation_settings}
check("PMAX automation opt-outs", all(auto.get(t) == "OPTED_OUT" for t in P["MG-0926-PMAX"]["asset_automation_opted_out"]), auto)
crit = Counter()
negs = set()
for r in q(c, f"SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative, campaign_criterion.keyword.text FROM campaign_criterion WHERE campaign.id = {pid}"):
    crit[(E(r.campaign_criterion.type_), r.campaign_criterion.negative)] += 1
    if E(r.campaign_criterion.type_) == "KEYWORD":
        negs.add(r.campaign_criterion.keyword.text)
geo_plan = Counter(g["t"] for g in P["MG-0926-PMAX"]["geo"])
check("PMAX geo == Landscaping (LOCATION + PROXIMITY)", crit[("LOCATION", False)] == geo_plan["LOCATION"] and crit[("PROXIMITY", False)] == geo_plan["PROXIMITY"], dict(crit))
check("PMAX language + 5 schedule rows", crit[("LANGUAGE", False)] == 1 and crit[("AD_SCHEDULE", False)] == 5, dict(crit))
check("PMAX 24 cross-negatives", set(P["MG-0926-PMAX"]["negatives"]["cross_phrase"]) == negs, len(negs))
pl = {str(r.campaign.id): E(r.campaign_shared_set.status) for r in q(c, f"SELECT campaign.id, campaign_shared_set.status FROM campaign_shared_set WHERE shared_set.id = {ssid}")}
check("PMAX shared negative list attached", pl.get(pid) == "ENABLED", pl)
ca = Counter(E(r.campaign_asset.field_type) for r in q(c, f"SELECT campaign.id, campaign_asset.field_type FROM campaign_asset WHERE campaign.id = {pid} AND campaign_asset.status != 'REMOVED'"))
check("PMAX campaign assets (1 name, 1 logo, 1 snippet, 5 sitelinks, 10 callouts)",
      ca == Counter({"BUSINESS_NAME": 1, "LOGO": 1, "STRUCTURED_SNIPPET": 1, "SITELINK": 5, "CALLOUT": 10}), dict(ca))
ag = q(c, f"SELECT campaign.id, asset_group.id, asset_group.status, asset_group.final_urls, asset_group.path1, asset_group.path2, asset_group.primary_status, asset_group.ad_strength FROM asset_group WHERE campaign.id = {pid}")
check("PMAX 1 asset group PAUSED, drainage URL + paths", len(ag) == 1 and E(ag[0].asset_group.status) == "PAUSED"
      and list(ag[0].asset_group.final_urls) == [P["MG-0926-PMAX"]["asset_group"]["final_url"]]
      and [ag[0].asset_group.path1, ag[0].asset_group.path2] == P["MG-0926-PMAX"]["asset_group"]["path"],
      f"{ag[0].asset_group.id if ag else None} strength={E(ag[0].asset_group.ad_strength) if ag else None}")
agid = ag[0].asset_group.id
aga = Counter()
txt = {"HEADLINE": set(), "LONG_HEADLINE": set(), "DESCRIPTION": set()}
for r in q(c, f"SELECT asset_group_asset.field_type, asset_group_asset.status, asset.text_asset.text FROM asset_group_asset WHERE asset_group.id = {agid}"):
    ft = E(r.asset_group_asset.field_type)
    aga[ft] += 1
    if ft in txt:
        txt[ft].add(r.asset.text_asset.text)
t = P["MG-0926-PMAX"]["asset_group"]["text"]
check("PMAX 15 H / 5 LH / 5 D text == plan", txt["HEADLINE"] == set(t["headlines"]) and txt["LONG_HEADLINE"] == set(t["long_headlines"]) and txt["DESCRIPTION"] == set(t["descriptions"]), dict(aga))
check("PMAX images 8 L / 6 S / 3 P + CTA", aga["MARKETING_IMAGE"] == 8 and aga["SQUARE_MARKETING_IMAGE"] == 6 and aga["PORTRAIT_MARKETING_IMAGE"] == 3 and aga["CALL_TO_ACTION_SELECTION"] == 1, dict(aga))
sig = Counter("THEME" if r.asset_group_signal.search_theme.text else "AUDIENCE" for r in q(c, f"SELECT asset_group_signal.search_theme.text, asset_group_signal.audience.audience FROM asset_group_signal WHERE asset_group.id = {agid}"))
check("PMAX 20 search themes + 1 audience signal", sig == Counter({"THEME": 20, "AUDIENCE": 1}), dict(sig))
lvl = [E(r.conversion_goal_campaign_config.goal_config_level) for r in q(c, f"SELECT campaign.id, conversion_goal_campaign_config.goal_config_level FROM conversion_goal_campaign_config WHERE campaign.id = {pid}")]
bid = sorted(f"{E(r.campaign_conversion_goal.category)}/{E(r.campaign_conversion_goal.origin)}" for r in q(c, f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id = {pid}") if r.campaign_conversion_goal.biddable)
check("PMAX goals = account default (WC Call Lead QUALIFIED_LEAD not biddable)", "QUALIFIED_LEAD/CALL_FROM_ADS" not in bid, f"{lvl} {bid}")
pol = Counter(E(r.asset.policy_summary.approval_status) for r in q(c, f"SELECT asset.policy_summary.approval_status FROM asset_group_asset WHERE asset_group.id = {agid}"))
check("PMAX asset review states", True, dict(pol))

fails = [r for r in res if not r[1]]
for n, ok, d in res:
    print(f"[{'PASS' if ok else 'FAIL'}] {n}  {d if d != '' else ''}")
print(f"\nREADBACK: {len(res) - len(fails)} PASS / {len(fails)} FAIL")
out = {"checks": [{"name": n, "pass": ok, "detail": str(d)} for n, ok, d in res], "pmax_campaign": pid, "asset_group": str(agid),
       "shared_set": ssid, "new_rsa_ids": {ag: [x["id"] for x in v] for ag, v in got.items()}}
(REC / "MG-0926-READBACK-2026-09-27.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
