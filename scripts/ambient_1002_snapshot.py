#!/usr/bin/env python3
"""Ambient | 2026-10-02 | READ-ONLY account-wide snapshot for the Emergency launch / full search-term / tablet / budget / PMax request.

Every non-removed campaign and ad group, serving-status reasons, keywords, ads + policy, assets, PMax asset groups and
signals, devices, schedules, locations, goals, every negative layer, budgets (shared relationships), performance
2026-09-01..today (today PARTIAL), change history since 2026-09-30, and every visible search term (all campaigns,
Sep 1..today) written to exports/search-terms-2026-10-02.jsonl. No mutations.
Writes snapshots/snapshot-2026-10-02.json.
"""
from __future__ import annotations
import sys, json, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, EXPORTS, CLIENT_DIR  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
import yaml  # noqa: E402

A = "2026-09-01"
NOW = datetime.datetime.now(TZ)
TODAY = NOW.date().isoformat()
money = lambda m: round(m / 1e6, 2)
WOS = sys.argv[1:] or []
cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
for w in WOS:
    err = validate_work_order(yaml.safe_load((CLIENT_DIR / "work-orders" / w).read_text(encoding="utf-8")), cl)
    print(f"work order {w}: {'VALID' if not err else err}")
    if err:
        sys.exit("HARD STOP: work order invalid")
c = client()
ident = identity_gate(c, verbose=True)
out = {"read_local": NOW.isoformat(), "identity": {k: v for k, v in ident.items() if k != "checks"}, "filters": "status != REMOVED; metrics "
       f"{A}..{TODAY} ({TODAY} PARTIAL); search terms: no threshold"}
yd = q(c, "SELECT segments.date, metrics.impressions FROM customer WHERE segments.date DURING YESTERDAY")
out["account_yesterday"] = yd[0].segments.date if yd else "no row"

camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status, campaign.primary_status, campaign.primary_status_reasons,
        campaign.advertising_channel_type, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros, campaign_budget.id,
        campaign_budget.name, campaign_budget.amount_micros, campaign_budget.explicitly_shared, campaign_budget.reference_count, campaign_budget.status,
        campaign.network_settings.target_google_search, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network,
        campaign.geo_target_type_setting.positive_geo_target_type, campaign.ai_max_setting.enable_ai_max, campaign.start_date_time,
        campaign.maximize_conversions.target_cpa_micros, campaign.contains_eu_political_advertising, campaign.brand_guidelines_enabled
        FROM campaign WHERE campaign.status != 'REMOVED'"""):
    x = r.campaign
    camps[str(x.id)] = dict(name=x.name, status=E(x.status), serving=E(x.serving_status), primary=E(x.primary_status),
                            reasons=[E(v) for v in x.primary_status_reasons], channel=E(x.advertising_channel_type), bidding=E(x.bidding_strategy_type),
                            ceiling=money(x.target_spend.cpc_bid_ceiling_micros) or None, budget_id=str(r.campaign_budget.id),
                            budget_name=r.campaign_budget.name, budget=money(r.campaign_budget.amount_micros), shared=r.campaign_budget.explicitly_shared,
                            budget_refs=r.campaign_budget.reference_count, search=x.network_settings.target_google_search,
                            partners=x.network_settings.target_search_network, display=x.network_settings.target_content_network,
                            geo=E(x.geo_target_type_setting.positive_geo_target_type), ai_max=x.ai_max_setting.enable_ai_max, start=x.start_date_time,
                            tcpa=money(x.maximize_conversions.target_cpa_micros) or None, brand_guidelines=x.brand_guidelines_enabled)
out["campaigns"] = camps
ENABLED = [k for k, v in camps.items() if v["status"] == "ENABLED"]
PMAX = [k for k, v in camps.items() if v["channel"] == "PERFORMANCE_MAX"]
LIVE = ",".join(ENABLED + PMAX)
ags = {}
for r in q(c, """SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status, ad_group.primary_status_reasons, ad_group.labels
        FROM ad_group WHERE ad_group.status != 'REMOVED' AND campaign.status != 'REMOVED'"""):
    g = r.ad_group
    ags[str(g.id)] = dict(campaign=str(r.campaign.id), name=g.name, status=E(g.status), primary=E(g.primary_status),
                          reasons=[E(v) for v in g.primary_status_reasons], labels=list(g.labels))
labels = {r.label.resource_name: r.label.name for r in q(c, "SELECT label.resource_name, label.name FROM label")}
for g in ags.values():
    g["labels"] = [labels.get(l, l) for l in g["labels"]]
out["ad_groups"] = ags
kws = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
        ad_group_criterion.negative, ad_group_criterion.status, ad_group_criterion.approval_status, ad_group_criterion.system_serving_status,
        ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons, ad_group_criterion.final_urls
        FROM ad_group_criterion WHERE campaign.id IN ({LIVE}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'"""):
    k = r.ad_group_criterion
    kws.append(dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), id=str(k.criterion_id), text=k.keyword.text, match=E(k.keyword.match_type),
                    negative=k.negative, status=E(k.status), approval=E(k.approval_status), serving=E(k.system_serving_status),
                    primary=E(k.primary_status), reasons=[E(v) for v in k.primary_status_reasons], url_override=list(k.final_urls)))
out["keywords"] = kws
ads = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.primary_status, ad_group_ad.primary_status_reasons,
        ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, ad_group_ad.policy_summary.policy_topic_entries,
        ad_group_ad.ad.final_urls, ad_group_ad.ad.type FROM ad_group_ad WHERE campaign.id IN ({LIVE}) AND ad_group_ad.status != 'REMOVED'"""):
    a = r.ad_group_ad
    ads.append(dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), id=str(a.ad.id), status=E(a.status), primary=E(a.primary_status),
                    reasons=[E(v) for v in a.primary_status_reasons], approval=E(a.policy_summary.approval_status), review=E(a.policy_summary.review_status),
                    topics=[(t.topic, E(t.type_)) for t in a.policy_summary.policy_topic_entries], urls=list(a.ad.final_urls), type=E(a.ad.type)))
out["ads"] = ads
# PMax asset groups, their assets and signals
agrp = {}
for r in q(c, """SELECT campaign.id, asset_group.id, asset_group.name, asset_group.status, asset_group.primary_status, asset_group.primary_status_reasons,
        asset_group.final_urls, asset_group.ad_strength FROM asset_group WHERE asset_group.status != 'REMOVED'"""):
    g = r.asset_group
    agrp[str(g.id)] = dict(campaign=str(r.campaign.id), name=g.name, status=E(g.status), primary=E(g.primary_status),
                           reasons=[E(v) for v in g.primary_status_reasons], urls=list(g.final_urls), strength=E(g.ad_strength), assets=collections.Counter())
for r in q(c, """SELECT asset_group.id, asset_group_asset.field_type, asset_group_asset.status, asset.id FROM asset_group_asset
        WHERE asset_group_asset.status != 'REMOVED'"""):
    g = agrp.get(str(r.asset_group.id))
    if g is not None:
        g["assets"][E(r.asset_group_asset.field_type)] += 1
for g in agrp.values():
    g["assets"] = dict(g["assets"])
sig = collections.defaultdict(list)
for r in q(c, "SELECT asset_group.id, asset_group_signal.search_theme.text, asset_group_signal.audience.audience FROM asset_group_signal"):
    s = r.asset_group_signal
    sig[str(r.asset_group.id)].append(s.search_theme.text or s.audience.audience)
for k, v in sig.items():
    if k in agrp:
        agrp[k]["signals"] = v
out["asset_groups"] = agrp
# campaign criteria (devices, schedule, geo, language, negatives) for live + PMax campaigns
crit = collections.defaultdict(lambda: collections.defaultdict(list))
for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type, campaign_criterion.negative, campaign_criterion.status,
        campaign_criterion.bid_modifier, campaign_criterion.device.type, campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour,
        campaign_criterion.ad_schedule.end_hour, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, campaign_criterion.location.geo_target_constant,
        campaign_criterion.language.language_constant, campaign_criterion.brand_list.shared_set FROM campaign_criterion WHERE campaign.id IN ({LIVE})"""):
    k = r.campaign_criterion
    t = E(k.type)
    row = dict(id=str(k.criterion_id), neg=k.negative, status=E(k.status))
    if t == "DEVICE":
        row.update(device=E(k.device.type), bid_modifier_set="bid_modifier" in k, bid_modifier=k.bid_modifier)
    elif t == "AD_SCHEDULE":
        row.update(day=E(k.ad_schedule.day_of_week), start=k.ad_schedule.start_hour, end=k.ad_schedule.end_hour)
    elif t == "KEYWORD":
        row.update(text=k.keyword.text, match=E(k.keyword.match_type))
    elif t == "LOCATION":
        row.update(geo=k.location.geo_target_constant)
    elif t == "LANGUAGE":
        row.update(lang=k.language.language_constant)
    elif t == "BRAND_LIST":
        row.update(set=k.brand_list.shared_set)
    crit[str(r.campaign.id)][t].append(row)
out["campaign_criteria"] = {k: dict(v) for k, v in crit.items()}
# shared sets + attachments + members (negative layers)
sets = {str(r.shared_set.id): dict(name=r.shared_set.name, type=E(r.shared_set.type), status=E(r.shared_set.status), members=r.shared_set.member_count)
        for r in q(c, "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status, shared_set.member_count FROM shared_set WHERE shared_set.status != 'REMOVED'")}
att = [dict(campaign=str(r.campaign.id), set=str(r.shared_set.id), status=E(r.campaign_shared_set.status))
       for r in q(c, "SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set WHERE campaign.status != 'REMOVED'")]
acct = [r.customer_negative_criterion.negative_keyword_list.shared_set.split("/")[-1] for r in q(c,
        "SELECT customer_negative_criterion.type, customer_negative_criterion.negative_keyword_list.shared_set FROM customer_negative_criterion")
        if E(r.customer_negative_criterion.type) == "NEGATIVE_KEYWORD_LIST"]
members = collections.defaultdict(list)
for sid in sorted(set(acct) | {a["set"] for a in att if a["status"] == "ENABLED"}):
    for r in q(c, f"SELECT shared_criterion.criterion_id, shared_criterion.keyword.text, shared_criterion.keyword.match_type, shared_criterion.type FROM shared_criterion WHERE shared_set.id = {sid}"):
        if E(r.shared_criterion.type) == "KEYWORD":
            members[sid].append(dict(id=str(r.shared_criterion.criterion_id), text=r.shared_criterion.keyword.text, match=E(r.shared_criterion.keyword.match_type)))
out.update(shared_sets=sets, attachments=att, account_level_sets=acct, shared_set_members=dict(members))
# assets linked to live campaigns
out["campaign_assets"] = [dict(campaign=str(r.campaign.id), field=E(r.campaign_asset.field_type), status=E(r.campaign_asset.status), asset=str(r.asset.id),
                               urls=list(r.asset.final_urls), text=r.asset.sitelink_asset.link_text or r.asset.callout_asset.callout_text or r.asset.call_asset.phone_number)
                          for r in q(c, f"""SELECT campaign.id, campaign_asset.field_type, campaign_asset.status, asset.id, asset.final_urls, asset.sitelink_asset.link_text,
                              asset.callout_asset.callout_text, asset.call_asset.phone_number FROM campaign_asset WHERE campaign.id IN ({LIVE}) AND campaign_asset.status != 'REMOVED'""")]
out["ad_group_assets"] = [dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), field=E(r.ad_group_asset.field_type), status=E(r.ad_group_asset.status),
                               asset=str(r.asset.id), urls=list(r.asset.final_urls))
                          for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_asset.field_type, ad_group_asset.status, asset.id, asset.final_urls
                              FROM ad_group_asset WHERE campaign.id IN ({LIVE}) AND ad_group_asset.status != 'REMOVED'""")]
# conversion actions + goals
out["conversion_actions"] = [dict(id=str(r.conversion_action.id), name=r.conversion_action.name, type=E(r.conversion_action.type),
                                  category=E(r.conversion_action.category), primary=r.conversion_action.primary_for_goal,
                                  in_conv=r.conversion_action.include_in_conversions_metric)
                             for r in q(c, "SELECT conversion_action.id, conversion_action.name, conversion_action.type, conversion_action.category, conversion_action.primary_for_goal, conversion_action.include_in_conversions_metric FROM conversion_action WHERE conversion_action.status = 'ENABLED'")]
out["campaign_goals"] = [dict(campaign=str(r.campaign.id), category=E(r.campaign_conversion_goal.category), origin=E(r.campaign_conversion_goal.origin),
                              biddable=r.campaign_conversion_goal.biddable)
                         for r in q(c, f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id IN ({LIVE})")]
# change history (bounded both ends)
out["change_events"] = [dict(at=r.change_event.change_date_time, type=E(r.change_event.change_resource_type), resource=r.change_event.change_resource_name,
                             client=E(r.change_event.client_type), op=E(r.change_event.resource_change_operation), fields=list(r.change_event.changed_fields.paths))
                        for r in q(c, f"""SELECT change_event.change_date_time, change_event.change_resource_type, change_event.change_resource_name, change_event.client_type,
                            change_event.resource_change_operation, change_event.changed_fields FROM change_event WHERE change_event.change_date_time >= '2026-09-30 00:00:00'
                            AND change_event.change_date_time <= '{TODAY} 23:59:59' ORDER BY change_event.change_date_time DESC LIMIT 2000""")]
# performance (all campaigns with delivery) Sep 1..today
perf = collections.defaultdict(dict)
M = "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions"
mm = lambda x: dict(impr=x.impressions, clicks=x.clicks, cost=money(x.cost_micros), conv=round(x.conversions, 2), all_conv=round(x.all_conversions, 2))
for r in q(c, f"SELECT campaign.id, segments.date, {M} FROM campaign WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["campaign_daily"][f"{r.campaign.id}|{r.segments.date}"] = mm(r.metrics)
for r in q(c, f"SELECT campaign.id, ad_group.id, segments.date, {M} FROM ad_group WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["ad_group_daily"][f"{r.ad_group.id}|{r.segments.date}"] = mm(r.metrics)
for r in q(c, f"SELECT campaign.id, segments.date, segments.device, {M} FROM campaign WHERE segments.date BETWEEN '2026-09-24' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["device_daily"][f"{r.campaign.id}|{r.segments.date}|{E(r.segments.device)}"] = mm(r.metrics)
for r in q(c, f"SELECT campaign.id, segments.date, segments.hour, segments.device, metrics.impressions, metrics.clicks FROM campaign WHERE segments.date BETWEEN '2026-10-01' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["device_hourly"][f"{r.campaign.id}|{r.segments.date}|{r.segments.hour:02d}|{E(r.segments.device)}"] = dict(impr=r.metrics.impressions, clicks=r.metrics.clicks)
for r in q(c, f"""SELECT campaign.id, metrics.search_impression_share, metrics.search_rank_lost_impression_share, metrics.search_budget_lost_impression_share
        FROM campaign WHERE segments.date BETWEEN '2026-09-01' AND '2026-09-30' AND campaign.status = 'ENABLED'"""):
    x = r.metrics
    perf["sept_is"][str(r.campaign.id)] = dict(IS=x.search_impression_share, rank=x.search_rank_lost_impression_share, budget=x.search_budget_lost_impression_share)
out["performance"] = dict(perf)
# search terms: every campaign, Sep 1..today, no threshold
rows = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, search_term_view.search_term, search_term_view.status, segments.date, segments.search_term_match_type,
        segments.keyword.ad_group_criterion, segments.keyword.info.text, segments.keyword.info.match_type, metrics.impressions, metrics.clicks,
        metrics.cost_micros, metrics.conversions, metrics.all_conversions FROM search_term_view WHERE segments.date BETWEEN '{A}' AND '{TODAY}'"""):
    rows.append(dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), term=r.search_term_view.search_term, status=E(r.search_term_view.status),
                     date=r.segments.date, st_match=E(r.segments.search_term_match_type),
                     kw_id=r.segments.keyword.ad_group_criterion.split("~")[-1] if r.segments.keyword.ad_group_criterion else "",
                     kw_text=r.segments.keyword.info.text, kw_match=E(r.segments.keyword.info.match_type), impr=r.metrics.impressions,
                     clicks=r.metrics.clicks, cost=money(r.metrics.cost_micros), conv=round(r.metrics.conversions, 2), all_conv=round(r.metrics.all_conversions, 2)))
ST = EXPORTS / "search-terms-2026-10-02.jsonl"
ST.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
out["search_terms_file"] = str(ST.relative_to(CLIENT_DIR))
(SNAP / "snapshot-2026-10-02.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")

# ---------------- compact print ----------------
print(f"\naccount yesterday={out['account_yesterday']} now={NOW.isoformat(timespec='seconds')}  campaigns={len(camps)} ad_groups={len(ags)}")
for cid in sorted(ENABLED + PMAX, key=lambda k: (camps[k]["channel"], camps[k]["name"])):
    v = camps[cid]
    dev = {d["device"]: (round(d["bid_modifier"], 2) if d["bid_modifier_set"] else "unset") for d in crit[cid].get("DEVICE", [])}
    print(f"  {cid} {v['status']:7s} {v['channel'][:6]} {v['primary']:12s} {v['reasons'][:3]} ${v['budget']} budget={v['budget_id']} shared={v['shared']} refs={v['budget_refs']} "
          f"{v['bidding']} ceil={v['ceiling']} sched={len(crit[cid].get('AD_SCHEDULE', []))} geo={sum(1 for x in crit[cid].get('LOCATION', []) if not x['neg'])} dev={dev} | {v['name'][:70]}")
print("asset groups:", {k: (v["campaign"], v["name"], v["status"], v["primary"], v["reasons"], v["urls"], v["assets"]) for k, v in agrp.items()})
ce = [x for x in out["change_events"]]
print(f"change_events since 09-30: {len(ce)} by (date, client, type): {dict(collections.Counter((x['at'][:10], x['client'], x['type']) for x in ce))}")
for scope, (a, b) in (("Sep", ("2026-09-01", "2026-09-30")), ("Oct1", ("2026-10-01", "2026-10-01")), (f"{TODAY} PARTIAL", (TODAY, TODAY))):
    sr = [x for x in rows if a <= x["date"] <= b]
    tot = {m: round(sum(v[m] for k, v in perf["campaign_daily"].items() if a <= k.split("|")[1] <= b), 2) for m in ("impr", "clicks", "cost")}
    print(f"  {scope:16s} account total impr={tot['impr']} clicks={tot['clicks']} cost=${tot['cost']} | visible terms rows={len(sr)} distinct="
          f"{len({(x['ad_group'], x['term']) for x in sr})} impr={sum(x['impr'] for x in sr)} clicks={sum(x['clicks'] for x in sr)} cost=${round(sum(x['cost'] for x in sr), 2)} "
          f"campaigns={len({x['campaign'] for x in sr})}")
print("wrote snapshots/snapshot-2026-10-02.json and", ST.name)
