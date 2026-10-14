#!/usr/bin/env python3
"""Ambient | 2026-09-17 | READBACK of AMB-0917-HEAT-CREATE-1 / 7DE31D6B6A88.

Read-only. Every created resource is fetched fresh from the API and compared
field-by-field with the SAVED MANIFEST. Also re-asserts that no pre-existing
campaign, budget or conversion action moved.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-17"
LIVE = ROOT / "receipts" / "live"
out = {"plan": "AMB-0917-HEAT-CREATE-1", "when": datetime.datetime.now(TZ).isoformat(),
       "read_only": True, "external_writes": 0, "assertions": []}
P = F = 0


def chk(label, ok, detail=""):
    global P, F
    if ok:
        P += 1
    else:
        F += 1
    out["assertions"].append({"check": label, "result": "PASS" if ok else "FAIL",
                              "detail": str(detail)[:400]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  -- {detail}" if detail else ""))


c = client()
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
              customer.test_account FROM customer""")[0].customer
assert row.descriptive_name == EXACT_NAME and str(row.id) == CID
print(f"identity: {row.descriptive_name} / {row.id}\n")

plan = json.loads((PLANS / "AMB-0917-HEAT-CREATE-1.json").read_text(encoding="utf-8"))
fp = plan.pop("fingerprint"); re_fp = approval_code(plan); plan["fingerprint"] = fp
assert fp == re_fp == "7DE31D6B6A88"
rcpt = json.loads((LIVE / f"AMB-0917-HEAT-CREATE-1-{STAMP}.json").read_text(encoding="utf-8"))
com = rcpt["committed"]
snap = json.loads((SNAP / f"heating-build-snapshot-{STAMP}.json").read_text(encoding="utf-8"))

cid_of = {k: v.rsplit("/", 1)[1] for k, v in com["campaigns"].items()}
agid_of = {k: v.rsplit("/", 1)[1] for k, v in com["ad_groups"].items()}
IDS = "', '".join(cid_of.values())

# ------------------------------------------------------------------ 1. budgets
print("=== 1. CAMPAIGN BUDGETS ===")
bids = "', '".join(v.rsplit("/", 1)[1] for v in com["campaign_budgets"].values())
brows = {str(r.campaign_budget.id): r.campaign_budget for r in q(c, f"""
    SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
           campaign_budget.explicitly_shared, campaign_budget.delivery_method,
           campaign_budget.status, campaign_budget.reference_count
    FROM campaign_budget WHERE campaign_budget.id IN ('{bids}')""")}
chk("2 budgets returned", len(brows) == 2, f"{len(brows)}")
for key, rn in com["campaign_budgets"].items():
    b = brows[rn.rsplit("/", 1)[1]]
    want = plan["campaigns"][key]["daily_budget"]
    # Google renames a NON-SHARED budget to its campaign name on attach. Verified
    # account-wide: 25/25 non-shared budgets here are named exactly after their campaign.
    # The name the plan set ("Budget | <campaign>") is therefore not retrievable.
    chk(f"budget {key} name is the plan name or the platform-synced campaign name",
        b.name in (f"Budget | {plan['campaigns'][key]['name']}",
                   plan['campaigns'][key]['name']), b.name)
    chk(f"budget {key} amount ${want}/day", b.amount_micros == int(round(want * 1e6)),
        f"${b.amount_micros / 1e6:.2f}")
    chk(f"budget {key} not shared", b.explicitly_shared is False, b.explicitly_shared)
    chk(f"budget {key} STANDARD delivery", E(b.delivery_method) == "STANDARD",
        E(b.delivery_method))
    chk(f"budget {key} reference_count == 1 (one campaign, no orphan/dupe)",
        b.reference_count == 1, b.reference_count)

# ------------------------------------------------------------------ 2. campaigns
print("\n=== 2. CAMPAIGNS ===")
crows = {str(r.campaign.id): r.campaign for r in q(c, f"""
    SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
           campaign.advertising_channel_sub_type, campaign.bidding_strategy_type,
           campaign.target_spend.cpc_bid_ceiling_micros, campaign.campaign_budget,
           campaign.network_settings.target_google_search,
           campaign.network_settings.target_search_network,
           campaign.network_settings.target_content_network,
           campaign.network_settings.target_partner_search_network,
           campaign.geo_target_type_setting.positive_geo_target_type,
           campaign.geo_target_type_setting.negative_geo_target_type,
           campaign.contains_eu_political_advertising, campaign.primary_status,
           campaign.primary_status_reasons, campaign.serving_status,
           campaign.start_date_time
    FROM campaign WHERE campaign.id IN ('{IDS}')""")}
chk("2 campaigns returned", len(crows) == 2, f"{len(crows)}")
for key, rn in com["campaigns"].items():
    cm = crows[cid_of[key]]; want = plan["campaigns"][key]
    chk(f"campaign {key} name", cm.name == want["name"], cm.name)
    chk(f"campaign {key} STATUS=PAUSED", E(cm.status) == "PAUSED", E(cm.status))
    chk(f"campaign {key} channel SEARCH",
        E(cm.advertising_channel_type) == "SEARCH", E(cm.advertising_channel_type))
    chk(f"campaign {key} bidding TARGET_SPEND",
        E(cm.bidding_strategy_type) == "TARGET_SPEND", E(cm.bidding_strategy_type))
    chk(f"campaign {key} CPC ceiling ${want['cpc_ceiling']}",
        cm.target_spend.cpc_bid_ceiling_micros == int(round(want["cpc_ceiling"] * 1e6)),
        f"${cm.target_spend.cpc_bid_ceiling_micros / 1e6:.2f}")
    chk(f"campaign {key} bound to its own budget",
        cm.campaign_budget == com["campaign_budgets"][key], cm.campaign_budget)
    n = cm.network_settings
    chk(f"campaign {key} Google Search ON", n.target_google_search is True,
        n.target_google_search)
    chk(f"campaign {key} Search Partners OFF", n.target_search_network is False,
        n.target_search_network)
    chk(f"campaign {key} Display OFF", n.target_content_network is False,
        n.target_content_network)
    chk(f"campaign {key} partner search OFF",
        n.target_partner_search_network is False, n.target_partner_search_network)
    g = cm.geo_target_type_setting
    chk(f"campaign {key} positive geo PRESENCE",
        E(g.positive_geo_target_type) == "PRESENCE", E(g.positive_geo_target_type))
    chk(f"campaign {key} negative geo PRESENCE",
        E(g.negative_geo_target_type) == "PRESENCE", E(g.negative_geo_target_type))
    chk(f"campaign {key} EU political declaration",
        E(cm.contains_eu_political_advertising)
        == "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
        E(cm.contains_eu_political_advertising))
    # NOTE: campaign.serving_status reads SERVING on 16 of the 17 pre-existing PAUSED
    # campaigns in this account, so it does not indicate delivery. primary_status does.
    chk(f"campaign {key} primary_status PAUSED (not delivering)",
        E(cm.primary_status) == "PAUSED",
        f"{E(cm.primary_status)} reasons={[E(r) for r in cm.primary_status_reasons]} "
        f"(serving_status={E(cm.serving_status)}, informational only)")

# ------------------------------------------------------------------ 3. criteria
print("\n=== 3. CAMPAIGN CRITERIA ===")
crit = {k: {"loc": [], "sch": [], "neg": []} for k in cid_of}
by_id = {v: k for k, v in cid_of.items()}
for r in q(c, f"""
    SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative,
           campaign_criterion.location.geo_target_constant,
           campaign_criterion.ad_schedule.day_of_week,
           campaign_criterion.ad_schedule.start_hour,
           campaign_criterion.ad_schedule.end_hour,
           campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
           campaign_criterion.status
    FROM campaign_criterion WHERE campaign.id IN ('{IDS}')
      AND campaign_criterion.status != 'REMOVED'"""):
    k = by_id[str(r.campaign.id)]; t = E(r.campaign_criterion.type_)
    if t == "LOCATION":
        crit[k]["loc"].append(r.campaign_criterion.location.geo_target_constant
                              .rsplit("/", 1)[1])
    elif t == "AD_SCHEDULE":
        s = r.campaign_criterion.ad_schedule
        crit[k]["sch"].append((E(s.day_of_week), s.start_hour, s.end_hour))
    elif t == "KEYWORD":
        crit[k]["neg"].append((r.campaign_criterion.keyword.text,
                               E(r.campaign_criterion.keyword.match_type),
                               r.campaign_criterion.negative))

want_geo = set(snap["reusable_geo_target_ids"])
want_sch = {(s["day"], s["start"], s["end"]) for s in snap["reusable_schedule"]}
for key in cid_of:
    d = crit[key]
    chk(f"{key} 75 location criteria", len(d["loc"]) == 75, len(d["loc"]))
    chk(f"{key} geo set matches the snapshot exactly", set(d["loc"]) == want_geo,
        f"missing={sorted(want_geo - set(d['loc']))[:5]} extra={sorted(set(d['loc']) - want_geo)[:5]}")
    chk(f"{key} 6 ad-schedule rows", len(d["sch"]) == 6, len(d["sch"]))
    chk(f"{key} schedule matches the snapshot exactly", set(d["sch"]) == want_sch,
        sorted(d["sch"]))
    wn = {(n["text"], n["match"]) for n in
          list(plan["campaign_negatives"]) + list(plan["cross_negatives"][key])}
    got = {(t, m) for t, m, neg in d["neg"]}
    chk(f"{key} {len(wn)} campaign negatives", len(d["neg"]) == len(wn),
        f"{len(d['neg'])} vs {len(wn)}")
    chk(f"{key} negative set matches the plan exactly", got == wn,
        f"missing={sorted(wn - got)[:5]} extra={sorted(got - wn)[:5]}")
    chk(f"{key} every keyword criterion is NEGATIVE",
        all(neg is True for _, _, neg in d["neg"]),
        sum(1 for _, _, neg in d["neg"] if neg is not True))

# ------------------------------------------------------------------ 4. ad groups
print("\n=== 4. AD GROUPS ===")
AGIDS = "', '".join(agid_of.values())
arows = {r.ad_group.name: r for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.type,
           ad_group.cpc_bid_micros FROM ad_group WHERE ad_group.id IN ('{AGIDS}')""")}
chk("2 ad groups returned", len(arows) == 2, len(arows))
for a in plan["ad_groups"]:
    r = arows.get(a["name"])
    chk(f"ad group present: {a['name']}", r is not None)
    if not r:
        continue
    chk(f"{a['name']} STATUS=PAUSED", E(r.ad_group.status) == "PAUSED",
        E(r.ad_group.status))
    chk(f"{a['name']} type SEARCH_STANDARD", E(r.ad_group.type_) == "SEARCH_STANDARD",
        E(r.ad_group.type_))
    chk(f"{a['name']} cpc bid ${a['cpc_bid']}",
        r.ad_group.cpc_bid_micros == int(round(a["cpc_bid"] * 1e6)),
        f"${r.ad_group.cpc_bid_micros / 1e6:.2f}")
    chk(f"{a['name']} in campaign {a['campaign']}",
        str(r.campaign.id) == cid_of[a["campaign"]], r.campaign.id)

# ------------------------------------------------------------------ 5. keywords
print("\n=== 5. KEYWORDS ===")
kw = {a["name"]: [] for a in plan["ad_groups"]}
agname = {agid_of[a["name"]] if False else None: None}
agn_by_id = {v.rsplit("/", 1)[1]: k for k, v in com["ad_groups"].items()}
for r in q(c, f"""
    SELECT ad_group.id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group_criterion.negative
    FROM ad_group_criterion WHERE ad_group.id IN ('{AGIDS}')
      AND ad_group_criterion.type = 'KEYWORD'
      AND ad_group_criterion.status != 'REMOVED'"""):
    kw[agn_by_id[str(r.ad_group.id)]].append(
        (r.ad_group_criterion.keyword.text, E(r.ad_group_criterion.keyword.match_type),
         E(r.ad_group_criterion.status), r.ad_group_criterion.negative))
tot = 0
for a in plan["ad_groups"]:
    got = kw[a["name"]]; tot += len(got)
    want = {(t, "PHRASE") for t in a["phrase"]} | {(t, "EXACT") for t in a["exact"]}
    chk(f"{a['name']} {len(want)} keywords", len(got) == len(want),
        f"{len(got)} vs {len(want)}")
    chk(f"{a['name']} keyword+match set matches the plan exactly",
        {(t, m) for t, m, _, _ in got} == want,
        f"missing={sorted(want - {(t, m) for t, m, _, _ in got})[:6]}")
    chk(f"{a['name']} every keyword PAUSED",
        all(s == "PAUSED" for _, _, s, _ in got),
        sorted({s for _, _, s, _ in got}))
    chk(f"{a['name']} no keyword created as negative",
        all(n is False for _, _, _, n in got))
chk("18 keywords total", tot == 18, tot)

# ------------------------------------------------------------------ 6. RSAs
print("\n=== 6. RSAs ===")
ads = {}
for r in q(c, f"""
    SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
           ad_group_ad.ad.final_urls, ad_group_ad.ad.type,
           ad_group_ad.ad.responsive_search_ad.path1,
           ad_group_ad.ad.responsive_search_ad.path2,
           ad_group_ad.ad.responsive_search_ad.headlines,
           ad_group_ad.ad.responsive_search_ad.descriptions,
           ad_group_ad.policy_summary.approval_status
    FROM ad_group_ad WHERE ad_group.id IN ('{AGIDS}')
      AND ad_group_ad.status != 'REMOVED'"""):
    a = r.ad_group_ad.ad
    ads.setdefault(agn_by_id[str(r.ad_group.id)], []).append({
        "id": a.id, "status": E(r.ad_group_ad.status), "type": E(a.type_),
        "urls": list(a.final_urls),
        "p1": a.responsive_search_ad.path1, "p2": a.responsive_search_ad.path2,
        "h": [(t.text, E(t.pinned_field) if t.pinned_field else "")
              for t in a.responsive_search_ad.headlines],
        "d": [t.text for t in a.responsive_search_ad.descriptions],
        "approval": E(r.ad_group_ad.policy_summary.approval_status)})
nr = 0
for o in plan["operations"]:
    if o["op"] != "CREATE_RSA_PAUSED":
        continue
    nr += 1
    pool = ads.get(o["ad_group"], [])
    want_h = [(h, "HEADLINE_1") for h in o["headlines_pinned_h1"]] + \
             [(h, "") for h in o["headlines_unpinned"]]
    m = [x for x in pool if sorted(x["h"]) == sorted(want_h)]
    chk(f"RSA matched in live account: {o['ad_group']} / {o['label'][:34]}",
        len(m) == 1, f"{len(m)} candidates")
    if len(m) != 1:
        continue
    x = m[0]
    chk(f"  RSA {x['id']} STATUS=PAUSED", x["status"] == "PAUSED", x["status"])
    chk(f"  RSA {x['id']} type RESPONSIVE_SEARCH_AD",
        x["type"] == "RESPONSIVE_SEARCH_AD", x["type"])
    chk(f"  RSA {x['id']} final URL", x["urls"] == [o["final_url"]], x["urls"])
    chk(f"  RSA {x['id']} paths /{o['path1']}/{o['path2']}",
        (x["p1"], x["p2"]) == (o["path1"], o["path2"]), f"/{x['p1']}/{x['p2']}")
    chk(f"  RSA {x['id']} {len(want_h)} headlines", len(x["h"]) == len(want_h),
        len(x["h"]))
    chk(f"  RSA {x['id']} 3 headlines pinned to H1",
        sum(1 for _, p in x["h"] if p == "HEADLINE_1")
        == len(o["headlines_pinned_h1"]),
        sum(1 for _, p in x["h"] if p == "HEADLINE_1"))
    chk(f"  RSA {x['id']} descriptions match", x["d"] == o["descriptions"], x["d"][:1])
    chk(f"  RSA {x['id']} policy not DISAPPROVED", x["approval"] != "DISAPPROVED",
        x["approval"])
chk("4 RSAs in the plan, 4 read back", nr == 4 and sum(len(v) for v in ads.values()) == 4,
    f"plan={nr} live={sum(len(v) for v in ads.values())}")

# ------------------------------------------------------------------ 7. assets
print("\n=== 7. ASSETS ===")
aids = "', '".join(a["resource"].rsplit("/", 1)[1] for a in com["assets"])
arow = {str(r.asset.id): r.asset for r in q(c, f"""
    SELECT asset.id, asset.name, asset.type, asset.final_urls,
           asset.callout_asset.callout_text,
           asset.structured_snippet_asset.header,
           asset.structured_snippet_asset.values,
           asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
           asset.sitelink_asset.description2
    FROM asset WHERE asset.id IN ('{aids}')""")}
chk("9 assets returned", len(arow) == 9, len(arow))
got_call = {a.callout_asset.callout_text for a in arow.values() if E(a.type_) == "CALLOUT"}
chk("5 callouts match the plan exactly", got_call == set(plan["callouts"]),
    sorted(got_call ^ set(plan["callouts"])))
sn = [a for a in arow.values() if E(a.type_) == "STRUCTURED_SNIPPET"]
chk("1 structured snippet", len(sn) == 1, len(sn))
if sn:
    chk(f"snippet header '{plan['structured_snippet']['header']}'",
        sn[0].structured_snippet_asset.header == plan["structured_snippet"]["header"],
        sn[0].structured_snippet_asset.header)
    chk("snippet values match the plan",
        list(sn[0].structured_snippet_asset.values) == plan["structured_snippet"]["values"],
        list(sn[0].structured_snippet_asset.values))
sl = {a.sitelink_asset.link_text: a for a in arow.values() if E(a.type_) == "SITELINK"}
chk("3 sitelinks", len(sl) == 3, sorted(sl))
for s in plan["sitelinks"]:
    a = sl.get(s["text"])
    chk(f"sitelink '{s['text']}' present", a is not None)
    if a:
        chk(f"  sitelink '{s['text']}' descriptions",
            (a.sitelink_asset.description1, a.sitelink_asset.description2)
            == (s["d1"], s["d2"]), a.sitelink_asset.description1)
        chk(f"  sitelink '{s['text']}' URL", list(a.final_urls) == [s["url"]],
            list(a.final_urls))

# ------------------------------------------------------------------ 8. asset links
print("\n=== 8. CAMPAIGN ASSET LINKS ===")
links = {k: [] for k in cid_of}
for r in q(c, f"""
    SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type,
           campaign_asset.status
    FROM campaign_asset WHERE campaign.id IN ('{IDS}')
      AND campaign_asset.status != 'REMOVED'"""):
    links[by_id[str(r.campaign.id)]].append(
        (r.campaign_asset.asset.rsplit("/", 1)[1], E(r.campaign_asset.field_type),
         E(r.campaign_asset.status)))
tot = 0
for key in cid_of:
    L = links[key]; tot += len(L)
    chk(f"{key} 11 asset links", len(L) == 11, len(L))
    chk(f"{key} every asset link PAUSED", all(s == "PAUSED" for _, _, s in L),
        sorted({s for _, _, s in L}))
    ft = sorted(f for _, f, _ in L)
    chk(f"{key} field types 5 CALLOUT / 3 SITELINK / 1 SNIPPET / CALL / BUSINESS_NAME",
        ft == sorted(["CALLOUT"] * 5 + ["SITELINK"] * 3 + ["STRUCTURED_SNIPPET",
                                                           "CALL", "BUSINESS_NAME"]), ft)
    ids = {a for a, _, _ in L}
    chk(f"{key} reuses existing call asset 407995613637 (no new call asset)",
        "407995613637" in ids)
    chk(f"{key} reuses existing business name asset 80516971145",
        "80516971145" in ids)
chk("22 campaign asset links total", tot == 22, tot)

# ------------------------------------------------------- 9. unrelated resources
print("\n=== 9. UNRELATED RESOURCES UNCHANGED ===")
base_all = snap["budgets"]["all_campaigns"]
base = {k: v for k, v in base_all.items() if v["status"] != "REMOVED"}
base_removed = {k for k, v in base_all.items() if v["status"] == "REMOVED"}
now = {str(r.campaign.id): r for r in q(c, """
    SELECT campaign.id, campaign.name, campaign.status,
           campaign_budget.amount_micros, campaign.target_spend.cpc_bid_ceiling_micros
    FROM campaign WHERE campaign.status != 'REMOVED'""")}
drift = []
for cidx, b in base.items():
    r = now.get(cidx)
    if r is None:
        drift.append(f"{b['name']} DISAPPEARED"); continue
    if E(r.campaign.status) != b["status"]:
        drift.append(f"{b['name']} status {b['status']} -> {E(r.campaign.status)}")
    if abs(r.campaign_budget.amount_micros / 1e6 - b["budget"]) > 0.005:
        drift.append(f"{b['name']} budget {b['budget']} -> "
                     f"{r.campaign_budget.amount_micros / 1e6}")
    if abs(r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6 - b["ceiling"]) > 0.005:
        drift.append(f"{b['name']} ceiling {b['ceiling']} -> "
                     f"{r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6}")
chk(f"all {len(base)} live pre-existing campaigns unchanged "
    f"(status + daily budget + CPC ceiling)", not drift, drift[:8])
chk(f"the {len(base_removed)} already-REMOVED campaigns were not resurrected",
    not (base_removed & set(now)), sorted(base_removed & set(now))[:5])
chk("live non-removed campaign count = 23 pre-existing + 2 new",
    len(now) == len(base) + 2, f"{len(now)} vs {len(base)}+2")
new_ids = set(cid_of.values())
en = [r for k, r in now.items() if E(r.campaign.status) == "ENABLED"]
chk("enabled campaign count unchanged at 5", len(en) == 5, len(en))
chk("neither new campaign is ENABLED",
    all(str(r.campaign.id) not in new_ids for r in en))
en_daily = sum(r.campaign_budget.amount_micros / 1e6 for r in en)
chk(f"combined ENABLED daily spend unchanged at "
    f"${snap['budgets']['combined_enabled_daily']:.2f}",
    abs(en_daily - snap["budgets"]["combined_enabled_daily"]) < 0.01, f"${en_daily:.2f}")
ca = q(c, """SELECT conversion_action.id, conversion_action.status,
             conversion_action.primary_for_goal FROM conversion_action
             WHERE conversion_action.status != 'REMOVED'""")
base_ca = [x for x in snap["conversion_actions"] if x["status"] != "REMOVED"]
chk(f"non-removed conversion action count unchanged at {len(base_ca)} "
    f"(14 ENABLED + 2 HIDDEN)", len(ca) == len(base_ca), len(ca))
base_prim = {x["id"] for x in base_ca if x["primary"]}
now_prim = {str(r.conversion_action.id) for r in ca
            if r.conversion_action.primary_for_goal}
chk(f"primary-for-goal set unchanged ({len(base_prim)} actions), none added or removed", base_prim == now_prim,
    sorted(base_prim ^ now_prim))

out["summary"] = {"pass": P, "fail": F, "total": P + F}
(LIVE / f"AMB-0917-HEAT-CREATE-1-{STAMP}-READBACK.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\n{'=' * 60}\nREADBACK: {P} PASS / {F} FAIL / {P + F} assertions")
print("EXTERNAL WRITES DURING READBACK: 0")
sys.exit(1 if F else 0)
