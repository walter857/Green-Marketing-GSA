#!/usr/bin/env python3
"""Ambient | 2026-09-30 | READ-ONLY Phase 1 snapshot for the Boiler Maintenance / Heat Pump Maintenance evaluation.

No mutations. Identity gate first (hard stop on mismatch).
Writes snapshots/maint-eval-2026-09-30.json (inventory + performance, no PII) and keeps raw search terms on disk
only (exports/heating-search-terms-2026-09-30.jsonl). stdout carries aggregates, IDs, settings and ad copy only.

Windows (2026-09-30 is PARTIAL and excluded): since_mig 09-24..09-29 · last7 09-23..09-29 · last14 09-16..09-29 ·
mtd 09-01..09-29.
"""
from __future__ import annotations
import sys, json, re, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, EXPORTS, CLIENT_DIR  # noqa: E402

SEVEN = ["24257819463", "24257819466", "24132507744", "24268690038", "24268690041", "24279798229", "24274160783"]
SHORT = {"24257819463": "Repair", "24257819466": "Install/Replace", "24132507744": "Boiler", "24268690038": "Heat Pump",
         "24268690041": "Thermostat", "24279798229": "Maintenance", "24274160783": "Geothermal", "24132507747": "Commercial"}
ALL8 = SEVEN + ["24132507747"]
IN7, IN8 = ",".join(SEVEN), ",".join(ALL8)
WIN = {"since_mig": ("2026-09-24", "2026-09-29"), "last7": ("2026-09-23", "2026-09-29"),
       "last14": ("2026-09-16", "2026-09-29"), "mtd": ("2026-09-01", "2026-09-29")}
MAINT_AG = {"204129718287": "Boiler Maintenance", "204129717567": "Heat Pump Maintenance"}
COMPARE_AG = {"204129718047": "Boiler Repair", "202339087594": "Gas Boiler Repair", "204129718207": "Boiler Replacement",
              "204129717327": "Heat Pump Repair", "204129717527": "Heat Pump Installation", "204129717487": "Heat Pump Replacement",
              "204129718247": "Boiler Installation", "204129717727": "Ductless Heating Repair"}
OUT = SNAP / "maint-eval-2026-09-30.json"
RAW = EXPORTS / "heating-search-terms-2026-09-30.jsonl"
out: dict = {"run_local": datetime.datetime.now(TZ).isoformat(), "windows": WIN, "errors": {}}

c = client()
print("=== IDENTITY GATE (fresh, read-only) ===")
out["identity"] = identity_gate(c, verbose=True)
print(f"  observed name: {out['identity']['descriptive_name']!r}  id: {out['identity']['customer_id']}")


def safe(name, fn):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        msg = f"{type(e).__name__}: {str(e)[:300]}"
        out["errors"][name] = msg
        print(f"  !! {name} failed: {msg[:200]}")
        return None


def mr(m):
    return dict(impr=m.impressions, clicks=m.clicks, cost=round(m.cost_micros / 1e6, 2), conv=round(m.conversions, 2),
                allconv=round(m.all_conversions, 2))


# ---------------- campaigns ----------------
def campaigns():
    res = {}
    for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign.primary_status, campaign.primary_status_reasons,
            campaign.serving_status, campaign.advertising_channel_type, campaign.bidding_strategy_type,
            campaign.target_spend.cpc_bid_ceiling_micros, campaign_budget.id, campaign_budget.amount_micros,
            campaign_budget.explicitly_shared, campaign_budget.delivery_method,
            campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
            campaign.network_settings.target_content_network, campaign.network_settings.target_partner_search_network,
            campaign.geo_target_type_setting.positive_geo_target_type, campaign.geo_target_type_setting.negative_geo_target_type,
            campaign.contains_eu_political_advertising
            FROM campaign WHERE campaign.id IN ({IN8})"""):
        x = r.campaign
        res[str(x.id)] = dict(name=x.name, status=E(x.status), primary=E(x.primary_status),
                              reasons=[E(v) for v in x.primary_status_reasons], serving=E(x.serving_status),
                              bidding=E(x.bidding_strategy_type), ceiling=round(x.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
                              budget_id=str(r.campaign_budget.id), budget=round(r.campaign_budget.amount_micros / 1e6, 2),
                              shared_budget=r.campaign_budget.explicitly_shared, delivery=E(r.campaign_budget.delivery_method),
                              search=x.network_settings.target_google_search, partners=x.network_settings.target_search_network,
                              display=x.network_settings.target_content_network,
                              geo_pos=E(x.geo_target_type_setting.positive_geo_target_type),
                              geo_neg=E(x.geo_target_type_setting.negative_geo_target_type))
    # automation settings, separately (field support varies by version)
    for fld in ("campaign.ai_max_setting.enable_ai_max", "campaign.asset_automation_settings"):
        try:
            for r in q(c, f"SELECT campaign.id, {fld} FROM campaign WHERE campaign.id IN ({IN8})"):
                cid = str(r.campaign.id)
                if fld.endswith("enable_ai_max"):
                    res[cid]["ai_max"] = r.campaign.ai_max_setting.enable_ai_max
                else:
                    res[cid]["asset_automation"] = {E(s.asset_automation_type): E(s.asset_automation_status)
                                                    for s in r.campaign.asset_automation_settings}
        except Exception as e:  # noqa: BLE001
            out["errors"][fld] = str(e)[:200]
    return res


out["campaigns"] = safe("campaigns", campaigns) or {}
print("\n=== CAMPAIGNS ===")
for cid in ALL8:
    v = out["campaigns"].get(cid)
    if v:
        print(f"  {cid} {SHORT[cid]:15s} {v['status']:7s} {v['primary']:12s} {v['reasons']} budget ${v['budget']} ceil ${v['ceiling']} "
              f"{v['bidding']} search={v['search']} partners={v['partners']} display={v['display']} geo={v['geo_pos']} "
              f"aimax={v.get('ai_max')} auto={v.get('asset_automation')}")


# ---------------- schedule + locations ----------------
def schedule_geo():
    sched = collections.defaultdict(list)
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour,
            campaign_criterion.ad_schedule.start_minute, campaign_criterion.ad_schedule.end_hour,
            campaign_criterion.ad_schedule.end_minute, campaign_criterion.bid_modifier, campaign_criterion.status
            FROM campaign_criterion WHERE campaign_criterion.type = 'AD_SCHEDULE' AND campaign.id IN ({IN8})"""):
        s = r.campaign_criterion.ad_schedule
        sched[str(r.campaign.id)].append(f"{E(s.day_of_week)[:3]} {s.start_hour:02d}-{s.end_hour:02d}")
    geo = collections.defaultdict(lambda: {"pos": set(), "neg": set(), "other": 0})
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative,
            campaign_criterion.location.geo_target_constant FROM campaign_criterion
            WHERE campaign_criterion.type IN ('LOCATION','PROXIMITY') AND campaign.id IN ({IN8})"""):
        g = geo[str(r.campaign.id)]
        if E(r.campaign_criterion.type) == "LOCATION":
            (g["neg"] if r.campaign_criterion.negative else g["pos"]).add(r.campaign_criterion.location.geo_target_constant)
        else:
            g["other"] += 1
    ref = geo[SEVEN[0]]["pos"]
    return {"schedule": {k: sorted(v) for k, v in sched.items()},
            "geo": {k: dict(pos=len(v["pos"]), neg=len(v["neg"]), proximity=v["other"], same_set_as_repair=(v["pos"] == ref))
                    for k, v in geo.items()}}


out["schedule_geo"] = safe("schedule_geo", schedule_geo) or {}
print("\n=== SCHEDULE / LOCATIONS ===")
for cid in ALL8:
    print(f"  {SHORT[cid]:15s} sched={out['schedule_geo'].get('schedule', {}).get(cid)} geo={out['schedule_geo'].get('geo', {}).get(cid)}")


# ---------------- conversion goals ----------------
def goals():
    res = collections.defaultdict(list)
    for r in q(c, f"""SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin,
            campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id IN ({IN8})"""):
        g = r.campaign_conversion_goal
        if g.biddable:
            res[str(r.campaign.id)].append(f"{E(g.category)}/{E(g.origin)}")
    cfg = {}
    for r in q(c, f"SELECT campaign.id, conversion_goal_campaign_config.goal_config_level FROM conversion_goal_campaign_config WHERE campaign.id IN ({IN8})"):
        cfg[str(r.campaign.id)] = E(r.conversion_goal_campaign_config.goal_config_level)
    acts = {}
    for r in q(c, """SELECT conversion_action.id, conversion_action.name, conversion_action.type, conversion_action.category,
            conversion_action.origin, conversion_action.primary_for_goal, conversion_action.include_in_conversions_metric,
            conversion_action.status FROM conversion_action WHERE conversion_action.status = 'ENABLED'"""):
        a = r.conversion_action
        acts[str(a.id)] = dict(name=a.name, type=E(a.type), category=E(a.category), origin=E(a.origin),
                               primary=a.primary_for_goal, in_conv=a.include_in_conversions_metric)
    return {"biddable_goals": dict(res), "goal_config_level": cfg, "actions": acts}


out["goals"] = safe("goals", goals) or {}
print("\n=== CONVERSION GOALS ===")
print("  config level:", out["goals"].get("goal_config_level"))
bg = out["goals"].get("biddable_goals", {})
print("  biddable goals (same on all?):", len({tuple(sorted(v)) for v in bg.values()}) == 1, sorted(next(iter(bg.values()), [])))
for k, a in out["goals"].get("actions", {}).items():
    if a["primary"] and a["in_conv"]:
        print(f"  PRIMARY+counted {k} {a['name']} {a['type']} {a['category']}")


# ---------------- negatives (lists + campaign + account level) ----------------
def negatives():
    res = {"campaign_shared_sets": collections.defaultdict(list), "campaign_negatives": {}, "account_level": {}}
    for r in q(c, f"""SELECT campaign.id, shared_set.id, shared_set.name, shared_set.type, campaign_shared_set.status
            FROM campaign_shared_set WHERE campaign.id IN ({IN8}) AND campaign_shared_set.status = 'ENABLED'"""):
        res["campaign_shared_sets"][str(r.campaign.id)].append(str(r.shared_set.id))
    sets = {}
    for sid in {s for v in res["campaign_shared_sets"].values() for s in v} | {"11252984411"}:
        rows = q(c, f"""SELECT shared_set.name, shared_set.type, shared_criterion.keyword.text, shared_criterion.keyword.match_type
                FROM shared_criterion WHERE shared_set.id = {sid}""")
        sets[sid] = dict(name=rows[0].shared_set.name if rows else "", type=E(rows[0].shared_set.type) if rows else "",
                         kws=[(r.shared_criterion.keyword.text.lower(), E(r.shared_criterion.keyword.match_type)) for r in rows])
    # account-level list actually attached at customer level?
    acct = [str(r.shared_set.id) for r in q(c, "SELECT shared_set.id, shared_set.type, shared_set.status FROM shared_set "
                                              "WHERE shared_set.type = 'ACCOUNT_LEVEL_NEGATIVE_KEYWORDS' AND shared_set.status = 'ENABLED'")]
    res["account_level_sets"] = acct
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
            FROM campaign_criterion WHERE campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE
            AND campaign.id IN ({IN8})"""):
        res["campaign_negatives"].setdefault(str(r.campaign.id), []).append(
            (r.campaign_criterion.keyword.text.lower(), E(r.campaign_criterion.keyword.match_type)))
    res["sets"] = sets
    res["campaign_shared_sets"] = dict(res["campaign_shared_sets"])
    return res


NEG = safe("negatives", negatives) or {}
print("\n=== NEGATIVES ===")
for sid, s in NEG.get("sets", {}).items():
    mt = collections.Counter(m for _, m in s["kws"])
    print(f"  set {sid} {s['type']:32s} members={len(s['kws'])} {dict(mt)} | {s['name'][:70]}")
print("  account-level sets enabled:", NEG.get("account_level_sets"))
for cid in ALL8:
    n = NEG.get("campaign_negatives", {}).get(cid, [])
    print(f"  {SHORT[cid]:15s} campaign negatives={len(n)} {dict(collections.Counter(m for _, m in n))} shared={NEG.get('campaign_shared_sets', {}).get(cid)}")


# ---------------- ad groups, labels, keywords, ads ----------------
def structure():
    ags = {}
    for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status,
            ad_group.primary_status_reasons, ad_group.cpc_bid_micros FROM ad_group
            WHERE campaign.id IN ({IN8}) AND ad_group.status != 'REMOVED'"""):
        ags[str(r.ad_group.id)] = dict(campaign=str(r.campaign.id), name=r.ad_group.name, status=E(r.ad_group.status),
                                       primary=E(r.ad_group.primary_status), reasons=[E(v) for v in r.ad_group.primary_status_reasons],
                                       labels=[], kw=[], neg=[], ads=[])
    for r in q(c, f"SELECT campaign.id, ad_group.id, label.name FROM ad_group_label WHERE campaign.id IN ({IN8})"):
        if str(r.ad_group.id) in ags:
            ags[str(r.ad_group.id)]["labels"].append(r.label.name)
    for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type, ad_group_criterion.negative, ad_group_criterion.status,
            ad_group_criterion.approval_status, ad_group_criterion.system_serving_status,
            ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr
            FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND campaign.id IN ({IN8})
            AND ad_group_criterion.status != 'REMOVED'"""):
        g = ags.get(str(r.ad_group.id))
        if not g:
            continue
        k = r.ad_group_criterion
        if k.negative:
            g["neg"].append((k.keyword.text.lower(), E(k.keyword.match_type)))
        else:
            qi = k.quality_info
            g["kw"].append(dict(id=str(k.criterion_id), text=k.keyword.text, match=E(k.keyword.match_type), status=E(k.status),
                                approval=E(k.approval_status), serving=E(k.system_serving_status), qs=qi.quality_score,
                                ctr=E(qi.search_predicted_ctr), rel=E(qi.creative_quality_score), lp=E(qi.post_click_quality_score)))
    for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type, ad_group_ad.ad.final_urls,
            ad_group_ad.ad_strength, ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status,
            ad_group_ad.policy_summary.policy_topic_entries, ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions, ad_group_ad.ad.responsive_search_ad.path1,
            ad_group_ad.ad.responsive_search_ad.path2, ad_group_ad.labels
            FROM ad_group_ad WHERE campaign.id IN ({IN8}) AND ad_group_ad.status != 'REMOVED'"""):
        g = ags.get(str(r.ad_group.id))
        if not g:
            continue
        a = r.ad_group_ad
        rsa = a.ad.responsive_search_ad
        g["ads"].append(dict(id=str(a.ad.id), status=E(a.status), type=E(a.ad.type), urls=list(a.ad.final_urls),
                             strength=E(a.ad_strength), approval=E(a.policy_summary.approval_status),
                             review=E(a.policy_summary.review_status),
                             topics=[(t.topic, E(t.type_)) for t in a.policy_summary.policy_topic_entries],
                             h=[(x.text, E(x.pinned_field) if x.pinned_field else "") for x in rsa.headlines],
                             d=[(x.text, E(x.pinned_field) if x.pinned_field else "") for x in rsa.descriptions],
                             path=[rsa.path1, rsa.path2]))
    return ags


AGS = safe("structure", structure) or {}
out["ad_groups"] = AGS
print("\n=== AD GROUPS (7 heating + commercial) ===")
for cid in ALL8:
    print(f"  --- {SHORT[cid]}")
    for gid, g in sorted(AGS.items(), key=lambda x: x[1]["name"]):
        if g["campaign"] != cid:
            continue
        en = sum(1 for a in g["ads"] if a["status"] == "ENABLED")
        pa = sum(1 for a in g["ads"] if a["status"] == "PAUSED")
        kmt = collections.Counter(k["match"] for k in g["kw"] if k["status"] == "ENABLED")
        urls = sorted({u.replace("https://offer.ambientcoolingandheating.com", "") for a in g["ads"] for u in a["urls"]})
        print(f"   {gid} {g['status']:7s} {g['primary']:12s} ads E{en}/P{pa} kw {dict(kmt)} adgrp-neg {len(g['neg'])} "
              f"labels {g['labels']} urls {urls} | {g['name']}")


# ---------------- assets ----------------
def assets():
    res = {"campaign": collections.defaultdict(list), "ad_group": collections.defaultdict(list), "customer": []}
    sel = ("asset.id, asset.type, asset.name, asset.final_urls, asset.sitelink_asset.link_text, asset.callout_asset.callout_text, "
           "asset.structured_snippet_asset.header, asset.structured_snippet_asset.values, asset.call_asset.phone_number, "
           "asset.policy_summary.approval_status")

    def row(r, fld):
        a = r.asset
        txt = a.sitelink_asset.link_text or a.callout_asset.callout_text or a.structured_snippet_asset.header or a.call_asset.phone_number or a.name
        vals = list(a.structured_snippet_asset.values)
        return dict(id=str(a.id), field=E(fld), text=txt, values=vals, urls=list(a.final_urls),
                    approval=E(a.policy_summary.approval_status))
    for r in q(c, f"SELECT campaign.id, campaign_asset.field_type, campaign_asset.status, {sel} FROM campaign_asset "
                  f"WHERE campaign.id IN ({IN8}) AND campaign_asset.status != 'REMOVED'"):
        d = row(r, r.campaign_asset.field_type); d["link_status"] = E(r.campaign_asset.status)
        res["campaign"][str(r.campaign.id)].append(d)
    for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group_asset.field_type, ad_group_asset.status, {sel} FROM ad_group_asset "
                  f"WHERE campaign.id IN ({IN8}) AND ad_group_asset.status != 'REMOVED'"):
        d = row(r, r.ad_group_asset.field_type); d["link_status"] = E(r.ad_group_asset.status)
        res["ad_group"][str(r.ad_group.id)].append(d)
    for r in q(c, f"SELECT customer_asset.field_type, customer_asset.status, {sel} FROM customer_asset WHERE customer_asset.status != 'REMOVED'"):
        d = row(r, r.customer_asset.field_type); d["link_status"] = E(r.customer_asset.status)
        res["customer"].append(d)
    # every sitelink asset in the account (to find existing maintenance sitelinks)
    res["all_sitelinks"] = [dict(id=str(r.asset.id), text=r.asset.sitelink_asset.link_text, urls=list(r.asset.final_urls))
                            for r in q(c, "SELECT asset.id, asset.sitelink_asset.link_text, asset.final_urls FROM asset WHERE asset.type = 'SITELINK'")]
    res["campaign"] = dict(res["campaign"]); res["ad_group"] = dict(res["ad_group"])
    return res


AS = safe("assets", assets) or {}
out["assets"] = AS
print("\n=== ASSETS (enabled campaigns) ===")
for cid in ALL8:
    rows = AS.get("campaign", {}).get(cid, [])
    by = collections.defaultdict(list)
    for a in rows:
        by[(a["field"], a["link_status"])].append(a["text"] + (" -> " + a["urls"][0].replace("https://offer.ambientcoolingandheating.com", "")
                                                              if a["urls"] else ""))
    print(f"  {SHORT[cid]}:")
    for k, v in sorted(by.items()):
        print(f"     {k[0]:18s} {k[1]:8s} {len(v)}: {v if k[0] in ('SITELINK', 'CALL', 'STRUCTURED_SNIPPET') else len(v)}")
for gid in list(MAINT_AG) + list(COMPARE_AG):
    rows = AS.get("ad_group", {}).get(gid, [])
    if rows:
        print(f"  ad-group assets {gid} {AGS.get(gid, {}).get('name')}: {[(a['field'], a['link_status'], a['text']) for a in rows]}")
print("  customer-level:", collections.Counter((a["field"], a["link_status"]) for a in AS.get("customer", [])))
print("  sitelink assets pointing at maintenance pages:",
      [(a["id"], a["text"], a["urls"]) for a in AS.get("all_sitelinks", []) if any("maint" in u for u in a["urls"])])


# ---------------- performance ----------------
def perf():
    res = {"campaign": {}, "ad_group": {}, "keyword": {}, "device": {}, "network": {}, "click_type": {}}
    for w, (a, b) in WIN.items():
        for r in q(c, f"""SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
                metrics.all_conversions, metrics.search_impression_share, metrics.search_rank_lost_impression_share,
                metrics.search_budget_lost_impression_share, metrics.search_top_impression_share,
                metrics.search_absolute_top_impression_share FROM campaign
                WHERE campaign.id IN ({IN8}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
            m = r.metrics
            d = mr(m)
            d.update(IS=round(m.search_impression_share * 100, 1), lost_rank=round(m.search_rank_lost_impression_share * 100, 1),
                     lost_budget=round(m.search_budget_lost_impression_share * 100, 1), top=round(m.search_top_impression_share * 100, 1),
                     abs_top=round(m.search_absolute_top_impression_share * 100, 1))
            res["campaign"][f"{r.campaign.id}|{w}"] = d
        for r in q(c, f"""SELECT ad_group.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
                metrics.all_conversions, metrics.search_impression_share, metrics.search_rank_lost_impression_share,
                metrics.search_top_impression_share, metrics.search_absolute_top_impression_share FROM ad_group
                WHERE campaign.id IN ({IN8}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
            m = r.metrics
            d = mr(m)
            d.update(IS=round(m.search_impression_share * 100, 1), lost_rank=round(m.search_rank_lost_impression_share * 100, 1),
                     top=round(m.search_top_impression_share * 100, 1), abs_top=round(m.search_absolute_top_impression_share * 100, 1))
            res["ad_group"][f"{r.ad_group.id}|{w}"] = d
    a, b = WIN["since_mig"]
    for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
            metrics.all_conversions FROM keyword_view WHERE campaign.id IN ({IN8}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
        if r.metrics.impressions:
            res["keyword"][f"{r.ad_group.id}|{r.ad_group_criterion.criterion_id}"] = dict(
                text=r.ad_group_criterion.keyword.text, match=E(r.ad_group_criterion.keyword.match_type), **mr(r.metrics))
    for w in ("since_mig", "mtd"):
        a, b = WIN[w]
        for r in q(c, f"""SELECT campaign.id, segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros,
                metrics.conversions, metrics.all_conversions FROM campaign
                WHERE campaign.id IN ({IN7}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
            res["device"][f"{r.campaign.id}|{E(r.segments.device)}|{w}"] = mr(r.metrics)
    a, b = WIN["since_mig"]
    for r in q(c, f"""SELECT campaign.id, segments.click_type, metrics.clicks, metrics.cost_micros, metrics.conversions,
            metrics.impressions, metrics.all_conversions FROM campaign WHERE campaign.id IN ({IN7}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
        k = f"{r.campaign.id}|{E(r.segments.click_type)}"
        res["click_type"][k] = mr(r.metrics)
    return res


P = safe("perf", perf) or {}
out["perf"] = P


def fmt(d):
    if not d:
        return "-"
    ctr = f"{100 * d['clicks'] / d['impr']:.1f}%" if d["impr"] else "-"
    cpc = f"${d['cost'] / d['clicks']:.2f}" if d["clicks"] else "-"
    return (f"impr {d['impr']:5d} clk {d['clicks']:3d} ctr {ctr:>6s} cpc {cpc:>7s} cost ${d['cost']:8.2f} conv {d['conv']:.0f}/{d['allconv']:.0f}"
            + (f" IS {d.get('IS')} rank {d.get('lost_rank')} bud {d.get('lost_budget', '-')} top {d.get('top')} abs {d.get('abs_top')}"
               if 'IS' in d else ""))


print("\n=== CAMPAIGN PERFORMANCE (conv = primary/all) ===")
for cid in ALL8:
    for w in WIN:
        print(f"  {SHORT[cid]:15s} {w:9s} {fmt(P.get('campaign', {}).get(f'{cid}|{w}'))}")
print("\n=== AD GROUP PERFORMANCE since_mig | last14 (groups with impressions) ===")
for gid, g in sorted(AGS.items(), key=lambda x: (x[1]["campaign"], x[1]["name"])):
    sm, l14 = P.get("ad_group", {}).get(f"{gid}|since_mig"), P.get("ad_group", {}).get(f"{gid}|last14")
    if (sm and sm["impr"]) or (l14 and l14["impr"]):
        print(f"  {SHORT[g['campaign']]:12s} {g['name'][7:32]:25s} SM {fmt(sm)}")
        print(f"  {'':12s} {'':25s} 14 {fmt(l14)}")
print("\n=== DEVICE (7 heating, since_mig) ===")
dev = collections.defaultdict(lambda: collections.Counter())
for k, v in P.get("device", {}).items():
    cid, d, w = k.split("|")
    if w == "since_mig":
        for kk in ("impr", "clicks", "cost", "conv", "allconv"):
            dev[d][kk] += v[kk]
for d, v in dev.items():
    print(f"  {d:12s} {dict(v)}")
print("\n=== CLICK TYPE (7 heating, since_mig) ===")
ct = collections.defaultdict(collections.Counter)
for k, v in P.get("click_type", {}).items():
    for kk in ("clicks", "cost", "conv"):
        ct[k.split("|")[1]][kk] += v[kk]
for k, v in ct.items():
    print(f"  {k:22s} {dict(v)}")


# ---------------- final URL + location performance ----------------
def url_geo():
    res = {"url": {}, "geo": {}}
    a, b = WIN["since_mig"]
    for r in q(c, f"""SELECT campaign.id, landing_page_view.unexpanded_final_url, metrics.impressions, metrics.clicks, metrics.cost_micros,
            metrics.conversions, metrics.all_conversions FROM landing_page_view
            WHERE campaign.id IN ({IN7}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
        u = r.landing_page_view.unexpanded_final_url.replace("https://offer.ambientcoolingandheating.com", "")
        prev = res["url"].get(u, dict(impr=0, clicks=0, cost=0, conv=0, allconv=0))
        for k, v in mr(r.metrics).items():
            prev[k] = round(prev[k] + v, 2)
        res["url"][u] = prev
    cities = collections.defaultdict(lambda: collections.Counter())
    for r in q(c, f"""SELECT campaign.id, segments.geo_target_city, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
            FROM user_location_view WHERE campaign.id IN ({IN7}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
        cc = cities[r.segments.geo_target_city or "(none)"]
        cc["impr"] += r.metrics.impressions; cc["clicks"] += r.metrics.clicks
        cc["cost"] += r.metrics.cost_micros / 1e6; cc["conv"] += r.metrics.conversions
    ids = [k.split("/")[-1] for k in cities if k.startswith("geoTargetConstants/")]
    names = {}
    if ids:
        for r in q(c, f"SELECT geo_target_constant.id, geo_target_constant.canonical_name FROM geo_target_constant "
                      f"WHERE geo_target_constant.id IN ({','.join(ids)})"):
            names[f"geoTargetConstants/{r.geo_target_constant.id}"] = r.geo_target_constant.canonical_name
    res["geo"] = {names.get(k, k): {kk: round(vv, 2) for kk, vv in v.items()} for k, v in cities.items()}
    return res


UG = safe("url_geo", url_geo) or {}
out["url_geo"] = UG
print("\n=== FINAL URL PERFORMANCE (7 heating, since_mig) ===")
for u, v in sorted(UG.get("url", {}).items(), key=lambda x: -x[1]["cost"]):
    print(f"  {u:45s} {fmt(v)}")
print("\n=== USER LOCATION BY CITY (7 heating, since_mig) ===")
for k, v in sorted(UG.get("geo", {}).items(), key=lambda x: -x[1]["cost"]):
    print(f"  {k.replace(',Maryland,United States', ''):40s} impr {v['impr']:.0f} clk {v['clicks']:.0f} cost ${v['cost']:.2f} conv {v['conv']:.0f}")


# ---------------- search terms: raw to disk, aggregates to stdout ----------------
SERVICE = re.compile(r"furnace|heat|boiler|radiator|baseboard|thermostat|hvac|geotherm|ductless|mini ?split|hydronic|steam", re.I)
BUCKETS = [("MAINTENANCE", re.compile(r"maint|tune ?-?up|tuneup|annual|inspect|check ?-?up|clean", re.I)),
           ("SERVICE_WORD", re.compile(r"\bservic", re.I)),
           ("REPLACE_INSTALL", re.compile(r"replac|install|new |cost|price|quote|estimat", re.I)),
           ("REPAIR", re.compile(r"repair|fix|not working|broken|no heat|leak|noise|won'?t|stopped", re.I))]


def search_terms():
    rows = []
    for w in ("mtd",):
        a, b = WIN[w]
        for r in q(c, f"""SELECT campaign.id, ad_group.id, search_term_view.search_term, search_term_view.status,
                segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions
                FROM search_term_view WHERE campaign.id IN ({IN7}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
            rows.append(dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), term=r.search_term_view.search_term,
                             status=E(r.search_term_view.status), date=r.segments.date, **mr(r.metrics)))
    with RAW.open("w", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(x) + "\n")
    agg = collections.defaultdict(lambda: collections.Counter())
    terms = collections.defaultdict(lambda: collections.Counter())
    for x in rows:
        if x["date"] < WIN["since_mig"][0]:
            continue
        t = x["term"]
        bucket = "OUT_OF_SCOPE" if not SERVICE.search(t) else next((n for n, rx in BUCKETS if rx.search(t)), "OTHER_SERVICE")
        grp = AGS.get(x["ad_group"], {}).get("name", x["ad_group"])[7:]
        agg[(bucket, grp)].update(dict(clicks=x["clicks"], cost=x["cost"], conv=x["conv"], impr=x["impr"]))
        terms[t].update(dict(cost=x["cost"], clicks=x["clicks"], conv=x["conv"]))
    meaningful = [t for t, v in terms.items() if v["cost"] >= 20]
    return {"rows": len(rows), "distinct_since_mig": len(terms),
            "meaningful_ge_20": dict(count=len(meaningful), cost=round(sum(terms[t]["cost"] for t in meaningful), 2),
                                     clicks=sum(terms[t]["clicks"] for t in meaningful),
                                     conv=sum(terms[t]["conv"] for t in meaningful)),
            "buckets": {f"{k[0]}|{k[1]}": {kk: round(vv, 2) for kk, vv in v.items()} for k, v in agg.items()}}


ST = safe("search_terms", search_terms) or {}
out["search_terms_agg"] = ST
print(f"\n=== SEARCH TERMS (raw on disk only, {ST.get('rows')} rows MTD; since_mig distinct {ST.get('distinct_since_mig')}) ===")
print("  terms with >= $20 since_mig:", ST.get("meaningful_ge_20"))
bt = collections.defaultdict(collections.Counter)
for k, v in ST.get("buckets", {}).items():
    bt[k.split("|")[0]].update(v)
for k, v in sorted(bt.items()):
    print(f"  {k:16s} {dict(v)}")
print("  MAINTENANCE / SERVICE_WORD by ad group:")
for k, v in sorted(ST.get("buckets", {}).items()):
    if k.startswith(("MAINTENANCE", "SERVICE_WORD")):
        print(f"     {k:50s} {v}")


# ---------------- conversions, calls, WhatConverts ----------------
def conv():
    res = {"by_group_action": {}, "calls": []}
    a, b = WIN["mtd"]
    for r in q(c, f"""SELECT ad_group.id, segments.conversion_action_name, segments.date, metrics.conversions, metrics.all_conversions
            FROM ad_group WHERE campaign.id IN ({IN8}) AND segments.date BETWEEN '{a}' AND '{b}'"""):
        if r.metrics.all_conversions:
            res["by_group_action"][f"{r.ad_group.id}|{r.segments.conversion_action_name}|{r.segments.date}"] = dict(
                conv=round(r.metrics.conversions, 2), allconv=round(r.metrics.all_conversions, 2))
    for r in q(c, """SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.call_status,
            call_view.type, campaign.id, ad_group.id FROM call_view WHERE call_view.start_call_date_time >= '2026-09-17 00:00:00'"""):
        res["calls"].append(dict(start=r.call_view.start_call_date_time, dur=r.call_view.call_duration_seconds,
                                 status=E(r.call_view.call_status), campaign=str(r.campaign.id), ad_group=str(r.ad_group.id)))
    return res


CV = safe("conv", conv) or {}
out["conversions"] = CV
print("\n=== CONVERSIONS (heating + commercial, MTD, click date; Local actions excluded) ===")
for k, v in sorted(CV.get("by_group_action", {}).items(), key=lambda x: x[0].split("|")[2]):
    gid, act, d = k.split("|")
    if "Local actions" in act or "Clicks to call" in act:
        continue
    print(f"  {d} {AGS.get(gid, {}).get('name', gid):35s} {act:45s} {v}")
print("  call_view since 09-17:", CV.get("calls"))


def wc():
    from gm_gsa.config import load_dotenv_if_available
    from gm_gsa.whatconverts import fetch_leads
    load_dotenv_if_available(Path(__file__).resolve().parents[1] / ".env")
    res = {"paid": [], "summary": collections.Counter()}
    leads = fetch_leads("115814", "105803", "2026-09-17", "2026-09-30", client_yaml=CLIENT_DIR / "client.yaml")["leads"]
    for dup in (False, True):
        pass
    for l in leads:
        has_id = bool(l.get("gclid") or l.get("gbraid") or l.get("wbraid"))
        res["summary"][("click_id" if has_id else "no_click_id") + "|" + str(l.get("quotable") or "Not Set")] += 1
        if has_id or l.get("lead_medium") == "cpc":
            path = lambda u: re.sub(r"\?.*$", "", u or "").replace("https://", "")
            res["paid"].append(dict(lead_id=l.get("lead_id"), created_utc=l.get("date_created"), type=l.get("lead_type"),
                                    source=f"{l.get('lead_source')}/{l.get('lead_medium')}", has_click_id=has_id,
                                    quotable=l.get("quotable") or "Not Set", status=l.get("lead_status"),
                                    duration=l.get("call_duration_seconds"), landing=path(l.get("landing_url")),
                                    number_suffix=str(l.get("tracking_number") or "")[-4:],
                                    quote_value=l.get("quote_value"), sales_value=l.get("sales_value")))
    res["total"] = len(leads)
    res["summary"] = dict(res["summary"])
    return res


W = safe("whatconverts", wc) or {}
out["whatconverts"] = W
print(f"\n=== WHATCONVERTS 09-17..09-30 (QA excluded): total {W.get('total')} ===")
print("  ", W.get("summary"))
for x in W.get("paid", []):
    print("  ", x)

OUT.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print("\nwrote", OUT, "| raw search terms on disk:", RAW.name, "| errors:", list(out["errors"]))
