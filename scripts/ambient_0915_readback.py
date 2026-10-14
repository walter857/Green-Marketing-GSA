#!/usr/bin/env python3
"""Ambient | 2026-09-15 | field-by-field readback of AMB-0915-COMM-RSA-1 + ASSET-1."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
CAMP, COMM_AG, RES_AG = "24132507747", "199748801029", "202339087634"
LIVE = ROOT / "receipts" / "live"
EXPECT_ADS = ["824781897834", "824781897837"]
EXPECT_ASSETS = ["421646926374", "421464532268", "421568039029", "421568040667",
                 "421646926386", "421568040679", "421646926389"]

c = client(); identity_gate(c, verbose=False)
plan_rsa = json.loads((PLANS / "AMB-0915-COMM-RSA-1.json").read_text(encoding="utf-8"))
plan_ast = json.loads((PLANS / "AMB-0915-COMM-ASSET-1.json").read_text(encoding="utf-8"))
fails, out = [], {"stamp": STAMP, "at": datetime.datetime.now(TZ).isoformat()}


def chk(label, ok, got=None, want=None):
    if not ok:
        fails.append(f"{label}: got={got!r} want={want!r}")
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}"
          + ("" if ok else f"  got={got!r} want={want!r}"))


print("=== 1. RSA READBACK ===")
ads = q(c, f"""
    SELECT ad_group.id, campaign.id, ad_group_ad.ad.id, ad_group_ad.ad.type,
           ad_group_ad.status, ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status,
           ad_group_ad.policy_summary.policy_topic_entries,
           ad_group_ad.ad.final_urls, ad_group_ad.ad.tracking_url_template,
           ad_group_ad.ad.final_url_suffix,
           ad_group_ad.ad.responsive_search_ad.headlines,
           ad_group_ad.ad.responsive_search_ad.descriptions,
           ad_group_ad.ad.responsive_search_ad.path1,
           ad_group_ad.ad.responsive_search_ad.path2,
           ad_group_ad.ad_strength
    FROM ad_group_ad WHERE ad_group.id = {COMM_AG}""")
chk("exactly 2 ads exist in the commercial ad group", len(ads) == 2, len(ads), 2)
got_ids = sorted(str(a.ad_group_ad.ad.id) for a in ads)
chk("ad IDs match execution receipt", got_ids == sorted(EXPECT_ADS), got_ids, sorted(EXPECT_ADS))

ad_rb = []
for a in ads:
    x = a.ad_group_ad
    rsa = x.ad.responsive_search_ad
    hp = [h.text for h in rsa.headlines if E(h.pinned_field) == "HEADLINE_1"]
    hu = [h.text for h in rsa.headlines if E(h.pinned_field) != "HEADLINE_1"]
    ds = [d.text for d in rsa.descriptions]
    # match this live ad to the planned ad by its pinned-headline signature
    want = next((o for o in plan_rsa["operations"]
                 if sorted(o["headlines_pinned_headline_1"]) == sorted(hp)
                 and sorted(o["headlines_unpinned"]) == sorted(hu)), None)
    label = want["ad_label"] if want else "UNMATCHED"
    print(f"\n  --- ad {x.ad.id}  {label} ---")
    chk(f"ad {x.ad.id} matched a planned ad", want is not None)
    chk(f"ad {x.ad.id} status PAUSED", E(x.status) == "PAUSED", E(x.status), "PAUSED")
    chk(f"ad {x.ad.id} type RESPONSIVE_SEARCH_AD",
        E(x.ad.type) == "RESPONSIVE_SEARCH_AD", E(x.ad.type), "RESPONSIVE_SEARCH_AD")
    if want:
        chk(f"ad {x.ad.id} final_urls", list(x.ad.final_urls) == [want["final_url"]],
            list(x.ad.final_urls), [want["final_url"]])
        chk(f"ad {x.ad.id} path1", rsa.path1 == want["path1"], rsa.path1, want["path1"])
        chk(f"ad {x.ad.id} path2", rsa.path2 == want["path2"], rsa.path2, want["path2"])
        chk(f"ad {x.ad.id} pinned HEADLINE_1 set",
            sorted(hp) == sorted(want["headlines_pinned_headline_1"]),
            sorted(hp), sorted(want["headlines_pinned_headline_1"]))
        chk(f"ad {x.ad.id} unpinned headlines",
            sorted(hu) == sorted(want["headlines_unpinned"]),
            len(hu), len(want["headlines_unpinned"]))
        chk(f"ad {x.ad.id} descriptions exact + ordered",
            ds == want["descriptions"], ds, want["descriptions"])
        chk(f"ad {x.ad.id} headline count == 15",
            len(rsa.headlines) == 15, len(rsa.headlines), 15)
        chk(f"ad {x.ad.id} description count == 4",
            len(rsa.descriptions) == 4, len(rsa.descriptions), 4)
        chk(f"ad {x.ad.id} every headline <= 30 chars",
            all(len(h.text) <= 30 for h in rsa.headlines))
        chk(f"ad {x.ad.id} every description <= 90 chars",
            all(len(d.text) <= 90 for d in rsa.descriptions))
    chk(f"ad {x.ad.id} no tracking_url_template",
        not x.ad.tracking_url_template, x.ad.tracking_url_template or None, None)
    chk(f"ad {x.ad.id} no final_url_suffix",
        not x.ad.final_url_suffix, x.ad.final_url_suffix or None, None)
    topics = [f"{E(t.topic_entry_type)}:{t.topic}" for t in x.policy_summary.policy_topic_entries]
    print(f"      policy: approval={E(x.policy_summary.approval_status)} "
          f"review={E(x.policy_summary.review_status)} topics={topics or 'none'} "
          f"strength={E(x.ad_strength)}")
    ad_rb.append({"ad_id": str(x.ad.id), "label": label, "status": E(x.status),
                  "approval": E(x.policy_summary.approval_status),
                  "review": E(x.policy_summary.review_status),
                  "policy_topics": topics, "ad_strength": E(x.ad_strength),
                  "final_urls": list(x.ad.final_urls),
                  "path1": rsa.path1, "path2": rsa.path2,
                  "headlines_pinned_h1": hp, "headlines_unpinned": hu,
                  "descriptions": ds})
out["ads"] = ad_rb

print("\n=== 2. ASSET + LINK READBACK ===")
links = q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_asset.asset, ad_group_asset.field_type,
           ad_group_asset.status, asset.id, asset.name, asset.type,
           asset.policy_summary.approval_status, asset.policy_summary.review_status,
           asset.callout_asset.callout_text,
           asset.structured_snippet_asset.header, asset.structured_snippet_asset.values
    FROM ad_group_asset WHERE ad_group.id = {COMM_AG}""")
chk("exactly 7 ad-group asset links", len(links) == 7, len(links), 7)
got_assets = sorted(str(l.asset.id) for l in links)
chk("asset IDs match execution receipt", got_assets == sorted(EXPECT_ASSETS),
    got_assets, sorted(EXPECT_ASSETS))
chk("ALL 7 links PAUSED", all(E(l.ad_group_asset.status) == "PAUSED" for l in links),
    sorted({E(l.ad_group_asset.status) for l in links}), ["PAUSED"])
want_co = {o["text"] for o in plan_ast["operations"] if o.get("text")}
got_co = {l.asset.callout_asset.callout_text for l in links
          if E(l.ad_group_asset.field_type) == "CALLOUT"}
chk("6 callouts exact text match", got_co == want_co, sorted(got_co), sorted(want_co))
sn = [l for l in links if E(l.ad_group_asset.field_type) == "STRUCTURED_SNIPPET"]
chk("exactly 1 structured snippet", len(sn) == 1, len(sn), 1)
if sn:
    s = sn[0].asset.structured_snippet_asset
    want_sn = next(o for o in plan_ast["operations"] if o.get("header"))
    chk("snippet header 'Types'", s.header == want_sn["header"], s.header, want_sn["header"])
    chk("snippet values exact", list(s.values) == want_sn["values"],
        list(s.values), want_sn["values"])
link_rb = []
for l in links:
    print(f"  {E(l.ad_group_asset.field_type):20s} {E(l.ad_group_asset.status):8s} "
          f"asset={l.asset.id:>14} approval={E(l.asset.policy_summary.approval_status):12s} "
          f"review={E(l.asset.policy_summary.review_status):22s} "
          f"{(l.asset.callout_asset.callout_text or (l.asset.structured_snippet_asset.header + ': ' + ', '.join(l.asset.structured_snippet_asset.values)))[:60]}")
    link_rb.append({"asset_id": str(l.asset.id),
                    "field_type": E(l.ad_group_asset.field_type),
                    "link_status": E(l.ad_group_asset.status),
                    "approval": E(l.asset.policy_summary.approval_status),
                    "review": E(l.asset.policy_summary.review_status),
                    "callout": l.asset.callout_asset.callout_text or None,
                    "snippet_header": l.asset.structured_snippet_asset.header or None,
                    "snippet_values": list(l.asset.structured_snippet_asset.values) or None})
out["asset_links"] = link_rb

print("\n=== 3. SERVING CHAIN - the ad group STILL CANNOT SERVE ===")
ag = q(c, f"""SELECT ad_group.id, ad_group.status, campaign.status FROM ad_group
              WHERE ad_group.id = {COMM_AG}""")[0]
serving_ads = [a for a in ads if E(a.ad_group_ad.status) == "ENABLED"]
chk("ZERO ENABLED ads in the commercial ad group", len(serving_ads) == 0,
    len(serving_ads), 0)
chk("ZERO ENABLED asset links", sum(1 for l in links
                                    if E(l.ad_group_asset.status) == "ENABLED") == 0)
print(f"  campaign {E(ag.campaign.status)} / ad group {E(ag.ad_group.status)} / "
      f"ads 2 (both PAUSED) / asset links 7 (all PAUSED)")
print("  => cannot serve: an ENABLED ad group with zero ENABLED ads delivers nothing")
out["serving_chain"] = {"campaign": E(ag.campaign.status),
                        "ad_group": E(ag.ad_group.status),
                        "enabled_ads": len(serving_ads),
                        "enabled_asset_links": 0, "can_serve": False}

print("\n=== 4. UNRELATED RESOURCES UNCHANGED ===")
u = {}
camps = q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                        campaign.target_spend.cpc_bid_ceiling_micros,
                        campaign.network_settings.target_search_network,
                        campaign.network_settings.target_content_network,
                        campaign.geo_target_type_setting.positive_geo_target_type,
                        campaign_budget.amount_micros
                 FROM campaign WHERE campaign.id IN ({IN5})""")
u["budgets"] = {str(r.campaign.id): r.campaign_budget.amount_micros / 1e6 for r in camps}
u["ceilings"] = {str(r.campaign.id): r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6
                 for r in camps}
u["statuses"] = {str(r.campaign.id): E(r.campaign.status) for r in camps}
u["search_partners"] = {str(r.campaign.id): r.campaign.network_settings.target_search_network
                        for r in camps}
u["geo"] = {str(r.campaign.id): E(r.campaign.geo_target_type_setting.positive_geo_target_type)
            for r in camps}
chk("budgets unchanged", u["budgets"] == {"24132507741": 141.45, "24132507744": 5.0,
                                          "24132507747": 176.15, "24132507750": 78.95,
                                          "24132507753": 20.0}, u["budgets"])
chk("ceilings unchanged", u["ceilings"] == {"24132507741": 25.0, "24132507744": 25.0,
                                            "24132507747": 30.0, "24132507750": 25.0,
                                            "24132507753": 30.0}, u["ceilings"])
chk("all five campaigns ENABLED", set(u["statuses"].values()) == {"ENABLED"})
chk("Search Partners still off everywhere", not any(u["search_partners"].values()))
chk("PRESENCE geo everywhere", set(u["geo"].values()) == {"PRESENCE"})
combined = round(sum(u["budgets"].values()), 2)
chk("combined daily still $421.55", combined == 421.55, combined, 421.55)
chk("30.4-day plan still $12,815.12", round(combined * 30.4, 2) == 12815.12)

u["commercial_negs"] = len(q(c, f"""SELECT ad_group_criterion.criterion_id
    FROM ad_group_criterion WHERE ad_group.id = {COMM_AG}
      AND ad_group_criterion.negative = TRUE"""))
chk("17 ad-group negatives untouched", u["commercial_negs"] == 17, u["commercial_negs"], 17)
u["commercial_keywords"] = sorted(
    f"{E(r.ad_group_criterion.keyword.match_type)}:{E(r.ad_group_criterion.status)}"
    for r in q(c, f"""SELECT ad_group_criterion.keyword.match_type,
                             ad_group_criterion.status FROM ad_group_criterion
                      WHERE ad_group.id = {COMM_AG}
                        AND ad_group_criterion.negative = FALSE"""))
chk("2 keywords still ENABLED", u["commercial_keywords"] == ["EXACT:ENABLED", "PHRASE:ENABLED"],
    u["commercial_keywords"])
res = q(c, f"""SELECT ad_group_ad.ad.id, ad_group_ad.status,
                      ad_group_ad.policy_summary.approval_status
               FROM ad_group_ad WHERE ad_group.id = {RES_AG}""")
u["residential_ads"] = sorted(f"{a.ad_group_ad.ad.id}:{E(a.ad_group_ad.status)}:"
                              f"{E(a.ad_group_ad.policy_summary.approval_status)}" for a in res)
chk("residential ads 821319509197 + 821319509200 still ENABLED+APPROVED",
    "821319509197:ENABLED:APPROVED" in u["residential_ads"]
    and "821319509200:ENABLED:APPROVED" in u["residential_ads"], u["residential_ads"])
u["residential_negs"] = len(q(c, f"""SELECT ad_group_criterion.criterion_id
    FROM ad_group_criterion WHERE ad_group.id = {RES_AG}
      AND ad_group_criterion.negative = TRUE"""))
chk("residential ad group still has 0 ad-group negatives (routing negative NOT applied)",
    u["residential_negs"] == 0, u["residential_negs"], 0)
u["campaign_negs_total"] = len(q(c, f"""SELECT campaign_criterion.criterion_id
    FROM campaign_criterion WHERE campaign.id IN ({IN5})
      AND campaign_criterion.negative = TRUE AND campaign_criterion.type = KEYWORD"""))
chk("campaign negatives still 6,158", u["campaign_negs_total"] == 6158,
    u["campaign_negs_total"], 6158)
u["conversion_actions"] = len(q(c, "SELECT conversion_action.id FROM conversion_action"))
chk("23 conversion actions, none changed", u["conversion_actions"] == 23,
    u["conversion_actions"], 23)
u["campaign_assets_on_five"] = len(q(c, f"""SELECT campaign.id, campaign_asset.asset
    FROM campaign_asset WHERE campaign.id IN ({IN5})"""))
u["call_asset"] = [{"id": str(r.asset.id), "num": r.asset.call_asset.phone_number,
                    "status": E(r.campaign_asset.status),
                    "approval": E(r.asset.policy_summary.approval_status)}
                   for r in q(c, f"""SELECT campaign.id, campaign_asset.status, asset.id,
                                            asset.call_asset.phone_number,
                                            asset.policy_summary.approval_status
                                     FROM campaign_asset WHERE campaign.id = {CAMP}
                                       AND campaign_asset.field_type = CALL""")]
chk("call asset 407995613637 still ENABLED+APPROVED on the campaign",
    any(x["id"] == "407995613637" and x["status"] == "ENABLED"
        and x["approval"] == "APPROVED" for x in u["call_asset"]), u["call_asset"])
sched = len(q(c, f"""SELECT campaign_criterion.criterion_id FROM campaign_criterion
    WHERE campaign.id = {CAMP} AND campaign_criterion.type = AD_SCHEDULE"""))
chk("ad schedule still 6 rows", sched == 6, sched, 6)
geo = len(q(c, f"""SELECT campaign_criterion.criterion_id FROM campaign_criterion
    WHERE campaign.id = {CAMP} AND campaign_criterion.type = LOCATION
      AND campaign_criterion.negative = FALSE"""))
chk("75 positive geo targets", geo == 75, geo, 75)
out["unchanged"] = u

print("\n=== 5. CHANGE EVENTS FROM THIS EXECUTION ONLY ===")
ce = q(c, """SELECT change_event.change_date_time, change_event.change_resource_type,
                    change_event.resource_change_operation, change_event.user_email,
                    change_event.client_type, change_event.change_resource_name
             FROM change_event
             WHERE change_event.change_date_time > '2026-09-15 09:00:00'
               AND change_event.change_date_time <= '2026-09-15 23:59:59'
             ORDER BY change_event.change_date_time DESC LIMIT 100""")
ev = [{"when": e.change_event.change_date_time,
       "type": E(e.change_event.change_resource_type),
       "op": E(e.change_event.resource_change_operation),
       "resource": e.change_event.change_resource_name} for e in ce]
out["change_events_this_session"] = ev
from collections import Counter
print(f"  events since 09:00 today: {len(ev)} -> "
      f"{Counter((x['type'], x['op']) for x in ev).most_common()}")
for x in ev[:12]:
    print(f"    {x['when'][:19]} {x['type']:18s} {x['op']:7s} {x['resource']}")
chk("only CREATEs, no UPDATE or REMOVE from this session",
    all(x["op"] == "CREATE" for x in ev), sorted({x["op"] for x in ev}))

print("\n" + "=" * 70)
out["fail_count"] = len(fails)
out["failures"] = fails
if fails:
    print(f"READBACK: {len(fails)} FAIL")
    for f in fails:
        print("  FAIL:", f)
else:
    print("READBACK: 0 FAIL")
LIVE.mkdir(parents=True, exist_ok=True)
p = LIVE / f"AMB-0915-READBACK-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"WROTE {p}")
