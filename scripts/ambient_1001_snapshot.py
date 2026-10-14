#!/usr/bin/env python3
"""Ambient | 2026-10-01 | READ-ONLY identity gate + snapshot for the search-term / landing-page activation request.

Work orders (all three validated first):
  work-orders/work-order-heating-repair-search-terms-2026-10-01.yaml   (Heating Repair, read)
  work-orders/work-order-emergency-heating-repair-lp-2026-10-01.yaml   (Emergency Heating Repair, draft)
  work-orders/work-order-geothermal-heat-pump-lp-2026-10-01.yaml       (Geothermal Heat Pump, draft)

In scope: campaign 24257819463 (Heating & Furnace Repair, all ad groups) and 24274160783 (Geothermal Heat Pump).
Every other campaign/ad group is inventoried (names, ids, statuses) and labelled OUT OF THIS WORK ORDER.
No mutations. Writes snapshots/snapshot-2026-10-01.json and exports/search-terms-2026-10-01.jsonl.
"""
from __future__ import annotations
import sys, json, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, EXPORTS, CLIENT_DIR  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
import yaml  # noqa: E402

REPAIR, GEO = "24257819463", "24274160783"
INS = f"{REPAIR},{GEO}"
NOW = datetime.datetime.now(TZ)
TODAY = NOW.date().isoformat()
HIST_A = "2026-09-17"

cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
for wo_name in ("work-order-heating-repair-search-terms-2026-10-01", "work-order-emergency-heating-repair-lp-2026-10-01",
                "work-order-geothermal-heat-pump-lp-2026-10-01"):
    wo = yaml.safe_load((CLIENT_DIR / "work-orders" / f"{wo_name}.yaml").read_text(encoding="utf-8"))
    err = validate_work_order(wo, cl)
    print(f"work order {wo_name}: {'VALID' if not err else err}")
    if err:
        sys.exit("HARD STOP: work order invalid")

c = client()
ident = identity_gate(c, verbose=True)
out = {"read_local": NOW.isoformat(), "identity": {k: v for k, v in ident.items() if k != "checks"},
       "identity_checks": ident["checks"]}
yday = q(c, "SELECT segments.date, metrics.impressions FROM customer WHERE segments.date DURING YESTERDAY")
out["account_clock_yesterday"] = yday[0].segments.date if yday else "no delivery row (zero-delivery day)"
print("account clock: yesterday =", out["account_clock_yesterday"], "| host now", NOW.isoformat(timespec="seconds"))


def money(micros):
    return round(micros / 1e6, 2)


# ---------------- account-wide inventory (every campaign + ad group, nothing silently omitted) ----------------
camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status, campaign.advertising_channel_type,
        campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros, campaign_budget.id, campaign_budget.amount_micros,
        campaign_budget.explicitly_shared, campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
        campaign.network_settings.target_content_network, campaign.geo_target_type_setting.positive_geo_target_type,
        campaign.geo_target_type_setting.negative_geo_target_type, campaign.tracking_url_template, campaign.final_url_suffix,
        campaign.primary_status, campaign.ai_max_setting.enable_ai_max
        FROM campaign WHERE campaign.status != 'REMOVED'"""):
    x = r.campaign
    camps[str(x.id)] = dict(name=x.name, status=E(x.status), serving=E(x.serving_status), channel=E(x.advertising_channel_type),
                            bidding=E(x.bidding_strategy_type), ceiling=money(x.target_spend.cpc_bid_ceiling_micros) or None,
                            budget_id=str(r.campaign_budget.id), budget=money(r.campaign_budget.amount_micros),
                            budget_shared=r.campaign_budget.explicitly_shared, search=x.network_settings.target_google_search,
                            partners=x.network_settings.target_search_network, display=x.network_settings.target_content_network,
                            geo_pos=E(x.geo_target_type_setting.positive_geo_target_type),
                            geo_neg=E(x.geo_target_type_setting.negative_geo_target_type),
                            tracking_template=x.tracking_url_template, final_url_suffix=x.final_url_suffix,
                            primary_status=E(x.primary_status), ai_max=x.ai_max_setting.enable_ai_max,
                            in_scope=str(x.id) in (REPAIR, GEO))
ags = {}
for r in q(c, """SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.type, ad_group.tracking_url_template,
        ad_group.final_url_suffix, ad_group.cpc_bid_micros, ad_group.primary_status, ad_group.labels FROM ad_group WHERE ad_group.status != 'REMOVED'"""):
    g = r.ad_group
    ags[str(g.id)] = dict(campaign_id=str(r.campaign.id), name=g.name, status=E(g.status), type=E(g.type),
                          tracking_template=g.tracking_url_template, final_url_suffix=g.final_url_suffix,
                          cpc_bid=money(g.cpc_bid_micros), primary_status=E(g.primary_status), labels=list(g.labels),
                          in_scope=str(r.campaign.id) in (REPAIR, GEO))
labels = {r.label.resource_name: r.label.name for r in q(c, "SELECT label.resource_name, label.name FROM label")}
for g in ags.values():
    g["labels"] = [labels.get(x, x) for x in g["labels"]]
out["campaigns"], out["ad_groups"] = camps, ags
print(f"\nINVENTORY (status != REMOVED): {len(camps)} campaigns, {len(ags)} ad groups")
for cid, x in sorted(camps.items(), key=lambda kv: (kv[1]['status'], kv[1]['name'])):
    n_ag = sum(1 for g in ags.values() if g["campaign_id"] == cid)
    print(f"  {'IN ' if x['in_scope'] else 'out'} {cid} {x['status']:8s} {x['channel']:15s} ${x['budget']:>6} ceil={x['ceiling']} ag={n_ag} {x['name']}")

# ---------------- in-scope detail ----------------
print("\nIN-SCOPE CAMPAIGNS")
for cid in (REPAIR, GEO):
    print(" ", cid, json.dumps({k: v for k, v in camps[cid].items() if k not in ("name",)}))
    for gid, g in sorted(ags.items(), key=lambda kv: kv[1]["name"]):
        if g["campaign_id"] == cid:
            print(f"     ag {gid} {g['status']:8s} {g['primary_status']:12s} {g['name']} labels={g['labels']} tt={bool(g['tracking_template'])} sfx={bool(g['final_url_suffix'])}")

# campaign criteria: schedule, locations, negatives, devices, language
crit = collections.defaultdict(lambda: collections.defaultdict(list))
for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type, campaign_criterion.negative,
        campaign_criterion.status, campaign_criterion.bid_modifier, campaign_criterion.ad_schedule.day_of_week,
        campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour, campaign_criterion.ad_schedule.start_minute,
        campaign_criterion.ad_schedule.end_minute, campaign_criterion.location.geo_target_constant, campaign_criterion.keyword.text,
        campaign_criterion.keyword.match_type, campaign_criterion.language.language_constant, campaign_criterion.device.type
        FROM campaign_criterion WHERE campaign.id IN ({INS})"""):
    k = r.campaign_criterion
    t = E(k.type)
    row = dict(id=str(k.criterion_id), negative=k.negative, status=E(k.status), bid_modifier=k.bid_modifier)
    if t == "AD_SCHEDULE":
        s = k.ad_schedule
        row.update(day=E(s.day_of_week), start_hour=s.start_hour, end_hour=s.end_hour,
                   start_minute=E(s.start_minute), end_minute=E(s.end_minute))
    elif t == "LOCATION":
        row.update(geo=k.location.geo_target_constant)
    elif t == "KEYWORD":
        row.update(text=k.keyword.text, match=E(k.keyword.match_type))
    elif t == "LANGUAGE":
        row.update(lang=k.language.language_constant)
    elif t == "DEVICE":
        row.update(device=E(k.device.type))
    crit[str(r.campaign.id)][t].append(row)
out["campaign_criteria"] = {cid: dict(v) for cid, v in crit.items()}
for cid in (REPAIR, GEO):
    v = crit[cid]
    sched = sorted((x["day"], x["start_hour"], x["end_hour"], x["start_minute"], x["end_minute"]) for x in v["AD_SCHEDULE"])
    locs = [x for x in v["LOCATION"] if not x["negative"]]
    print(f"\n  {cid} schedule rows={len(sched)} {sched}")
    print(f"  {cid} locations positive={len(locs)} negative={sum(1 for x in v['LOCATION'] if x['negative'])} "
          f"campaign negative keywords={sum(1 for x in v['KEYWORD'] if x['negative'])} "
          f"(match {collections.Counter(x['match'] for x in v['KEYWORD'] if x['negative'])}) languages={[x['lang'] for x in v['LANGUAGE']]} "
          f"device modifiers={[(x['device'], x['bid_modifier']) for x in v['DEVICE']]}")

# keywords (positive + negative) in scope
kw = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type, ad_group_criterion.negative, ad_group_criterion.status,
        ad_group_criterion.system_serving_status, ad_group_criterion.approval_status, ad_group_criterion.final_urls,
        ad_group_criterion.final_mobile_urls, ad_group_criterion.tracking_url_template, ad_group_criterion.final_url_suffix,
        ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score,
        ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr,
        ad_group_criterion.cpc_bid_micros
        FROM ad_group_criterion WHERE campaign.id IN ({INS}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'"""):
    k = r.ad_group_criterion
    kw.append(dict(campaign_id=str(r.campaign.id), ad_group_id=str(r.ad_group.id), criterion_id=str(k.criterion_id), text=k.keyword.text,
                   match=E(k.keyword.match_type), negative=k.negative, status=E(k.status), serving=E(k.system_serving_status),
                   approval=E(k.approval_status), final_urls=list(k.final_urls), final_mobile_urls=list(k.final_mobile_urls),
                   tracking_template=k.tracking_url_template, final_url_suffix=k.final_url_suffix, qs=k.quality_info.quality_score,
                   ad_rel=E(k.quality_info.creative_quality_score), lp_exp=E(k.quality_info.post_click_quality_score),
                   exp_ctr=E(k.quality_info.search_predicted_ctr), cpc_bid=money(k.cpc_bid_micros)))
out["keywords"] = kw
print("\n  KEYWORDS (in scope)")
for x in sorted(kw, key=lambda z: (z["campaign_id"], ags[z["ad_group_id"]]["name"], z["negative"], z["text"])):
    if not x["negative"]:
        print(f"    {ags[x['ad_group_id']]['name'][7:]:28s} {x['criterion_id']:>13s} {x['match']:6s} {x['status']:8s} {x['serving']:10s} QS={x['qs']} "
              f"[{x['ad_rel']}/{x['lp_exp']}/{x['exp_ctr']}] urlov={x['final_urls']} mob={x['final_mobile_urls']} {x['text']}")
neg_ag = collections.Counter((ags[x["ad_group_id"]]["name"], x["match"]) for x in kw if x["negative"])
print("  ad-group negatives by (ad group, match):", dict(neg_ag))

# ads
ads = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.primary_status,
        ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, ad_group_ad.ad.type,
        ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls, ad_group_ad.ad.tracking_url_template, ad_group_ad.ad.final_url_suffix,
        ad_group_ad.ad.responsive_search_ad.path1, ad_group_ad.ad.responsive_search_ad.path2,
        ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions, ad_group_ad.labels
        FROM ad_group_ad WHERE campaign.id IN ({INS}) AND ad_group_ad.status != 'REMOVED'"""):
    a = r.ad_group_ad
    rsa = a.ad.responsive_search_ad
    ads.append(dict(campaign_id=str(r.campaign.id), ad_group_id=str(r.ad_group.id), ad_id=str(a.ad.id), status=E(a.status),
                    primary_status=E(a.primary_status), approval=E(a.policy_summary.approval_status), review=E(a.policy_summary.review_status),
                    type=E(a.ad.type), final_urls=list(a.ad.final_urls), final_mobile_urls=list(a.ad.final_mobile_urls),
                    tracking_template=a.ad.tracking_url_template, final_url_suffix=a.ad.final_url_suffix, path1=rsa.path1, path2=rsa.path2,
                    headlines=[(h.text, E(h.pinned_field)) for h in rsa.headlines], descriptions=[(d.text, E(d.pinned_field)) for d in rsa.descriptions],
                    labels=[labels.get(x, x) for x in a.labels]))
out["ads"] = ads
print("\n  ADS (in scope)")
for x in sorted(ads, key=lambda z: (z["campaign_id"], ags[z["ad_group_id"]]["name"])):
    print(f"    {ags[x['ad_group_id']]['name'][7:]:28s} ad {x['ad_id']} {x['status']:8s} {x['approval']:20s} {x['review']:12s} url={x['final_urls']} "
          f"mob={x['final_mobile_urls']} tt={bool(x['tracking_template'])} sfx={bool(x['final_url_suffix'])} path={x['path1']}/{x['path2']} labels={x['labels']}")

# assets linked at campaign / ad group / customer level
assets = []
for lvl, frm, idf in (("campaign", "campaign_asset", "campaign.id"), ("ad_group", "ad_group_asset", "ad_group.id")):
    extra = "campaign.id, " if lvl == "campaign" else "campaign.id, ad_group.id, "
    for r in q(c, f"""SELECT {extra}{frm}.status, {frm}.field_type, asset.id, asset.type, asset.name, asset.final_urls, asset.final_mobile_urls,
            asset.tracking_url_template, asset.final_url_suffix, asset.sitelink_asset.link_text, asset.callout_asset.callout_text,
            asset.call_asset.phone_number, asset.structured_snippet_asset.header, asset.policy_summary.approval_status
            FROM {frm} WHERE campaign.id IN ({INS}) AND {frm}.status != 'REMOVED'"""):
        s = getattr(r, frm)
        a = r.asset
        assets.append(dict(level=lvl, campaign_id=str(r.campaign.id), ad_group_id=str(r.ad_group.id) if lvl == "ad_group" else None,
                           link_status=E(s.status), field=E(s.field_type), asset_id=str(a.id), type=E(a.type),
                           text=a.sitelink_asset.link_text or a.callout_asset.callout_text or a.call_asset.phone_number or a.structured_snippet_asset.header or a.name,
                           final_urls=list(a.final_urls), final_mobile_urls=list(a.final_mobile_urls), tracking_template=a.tracking_url_template,
                           final_url_suffix=a.final_url_suffix, approval=E(a.policy_summary.approval_status)))
for r in q(c, """SELECT customer_asset.status, customer_asset.field_type, asset.id, asset.type, asset.final_urls, asset.sitelink_asset.link_text,
        asset.callout_asset.callout_text, asset.call_asset.phone_number FROM customer_asset WHERE customer_asset.status != 'REMOVED'"""):
    a = r.asset
    assets.append(dict(level="customer", link_status=E(r.customer_asset.status), field=E(r.customer_asset.field_type), asset_id=str(a.id),
                       type=E(a.type), text=a.sitelink_asset.link_text or a.callout_asset.callout_text or a.call_asset.phone_number,
                       final_urls=list(a.final_urls)))
out["assets"] = assets
print("\n  ASSETS (in-scope links + customer level)")
for x in assets:
    print(f"    {x['level']:8s} {x.get('campaign_id') or '':11s} {x.get('ad_group_id') or '':12s} {x['field']:18s} {x['link_status']:7s} {x['asset_id']} {x.get('text')!r} {x.get('final_urls')}")
for r in q(c, f"""SELECT campaign.id, campaign_asset_set.status, asset_set.id, asset_set.type, asset_set.name FROM campaign_asset_set
        WHERE campaign.id IN ({INS}) AND campaign_asset_set.status != 'REMOVED'"""):
    print(f"    campaign asset set {r.campaign.id} {E(r.asset_set.type)} {r.asset_set.id} {r.asset_set.name} {E(r.campaign_asset_set.status)}")
for r in q(c, "SELECT customer_asset_set.status, asset_set.id, asset_set.type, asset_set.name FROM customer_asset_set WHERE customer_asset_set.status != 'REMOVED'"):
    print(f"    customer asset set {E(r.asset_set.type)} {r.asset_set.id} {r.asset_set.name} {E(r.customer_asset_set.status)}")

# shared negative lists: campaign attachments + account level
sets = {}
for r in q(c, "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status, shared_set.member_count FROM shared_set WHERE shared_set.status != 'REMOVED'"):
    sets[str(r.shared_set.id)] = dict(name=r.shared_set.name, type=E(r.shared_set.type), status=E(r.shared_set.status), members=r.shared_set.member_count)
attach = collections.defaultdict(list)
for r in q(c, f"SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set WHERE campaign.id IN ({INS})"):
    attach[str(r.campaign.id)].append(dict(set_id=str(r.shared_set.id), status=E(r.campaign_shared_set.status)))
acct_sets = []
for r in q(c, "SELECT customer_negative_criterion.id, customer_negative_criterion.type, customer_negative_criterion.negative_keyword_list.shared_set FROM customer_negative_criterion"):
    if E(r.customer_negative_criterion.type) == "NEGATIVE_KEYWORD_LIST":
        acct_sets.append(r.customer_negative_criterion.negative_keyword_list.shared_set.split("/")[-1])
need = set(acct_sets) | {a["set_id"] for v in attach.values() for a in v if a["status"] == "ENABLED"}
members = collections.defaultdict(list)
for sid in sorted(need):
    for r in q(c, f"SELECT shared_set.id, shared_criterion.criterion_id, shared_criterion.keyword.text, shared_criterion.keyword.match_type, shared_criterion.type FROM shared_criterion WHERE shared_set.id = {sid}"):
        if E(r.shared_criterion.type) == "KEYWORD":
            members[sid].append(dict(id=str(r.shared_criterion.criterion_id), text=r.shared_criterion.keyword.text, match=E(r.shared_criterion.keyword.match_type)))
out["shared_sets"] = sets
out["campaign_shared_set_attachments"] = dict(attach)
out["account_level_negative_sets"] = acct_sets
out["shared_set_members"] = dict(members)
print("\n  NEGATIVE LISTS")
for sid in acct_sets:
    print(f"    ACCOUNT-LEVEL set {sid} {sets.get(sid, {}).get('name')} members={len(members[sid])} {collections.Counter(m['match'] for m in members[sid])}")
for cid in (REPAIR, GEO):
    for a in attach[cid]:
        s = sets.get(a["set_id"], {})
        print(f"    {cid} attached {a['set_id']} {a['status']} {s.get('type')} {s.get('name')} members={len(members[a['set_id']])} {collections.Counter(m['match'] for m in members[a['set_id']])}")

# conversion actions + goals
conv = []
for r in q(c, """SELECT conversion_action.id, conversion_action.name, conversion_action.type, conversion_action.category, conversion_action.status,
        conversion_action.primary_for_goal, conversion_action.include_in_conversions_metric, conversion_action.counting_type,
        conversion_action.click_through_lookback_window_days, conversion_action.phone_call_duration_seconds, conversion_action.origin
        FROM conversion_action WHERE conversion_action.status = 'ENABLED'"""):
    x = r.conversion_action
    conv.append(dict(id=str(x.id), name=x.name, type=E(x.type), category=E(x.category), primary=x.primary_for_goal,
                     in_conv=x.include_in_conversions_metric, counting=E(x.counting_type), lookback=x.click_through_lookback_window_days,
                     call_secs=x.phone_call_duration_seconds, origin=E(x.origin)))
out["conversion_actions_enabled"] = conv
print("\n  CONVERSION ACTIONS (ENABLED)")
for x in sorted(conv, key=lambda z: (not z["primary"], z["name"])):
    print(f"    {x['id']:>11s} {'PRIMARY  ' if x['primary'] else 'secondary'} inConv={x['in_conv']} {x['type']:24s} {x['category']:22s} {x['counting']:14s} lb={x['lookback']} {x['name']}")
goals = []
for r in q(c, "SELECT customer_conversion_goal.category, customer_conversion_goal.origin, customer_conversion_goal.biddable FROM customer_conversion_goal"):
    goals.append(dict(level="customer", category=E(r.customer_conversion_goal.category), origin=E(r.customer_conversion_goal.origin), biddable=r.customer_conversion_goal.biddable))
for r in q(c, f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id IN ({INS})"):
    goals.append(dict(level="campaign", campaign_id=str(r.campaign.id), category=E(r.campaign_conversion_goal.category),
                      origin=E(r.campaign_conversion_goal.origin), biddable=r.campaign_conversion_goal.biddable))
out["conversion_goals"] = goals
print("  biddable goals:", sorted({(g['level'], g.get('campaign_id', ''), g['category'], g['origin']) for g in goals if g['biddable']}))

# change history since the baseline start (account-local time; bounded both ends)
chg = []
for r in q(c, f"""SELECT change_event.change_date_time, change_event.change_resource_type, change_event.change_resource_name,
        change_event.client_type, change_event.resource_change_operation, change_event.changed_fields, change_event.campaign,
        change_event.old_resource, change_event.new_resource
        FROM change_event WHERE change_event.change_date_time >= '2026-09-24 00:00:00' AND change_event.change_date_time <= '{TODAY} 23:59:59'
        ORDER BY change_event.change_date_time DESC LIMIT 1000"""):
    e = r.change_event
    chg.append(dict(at=e.change_date_time, type=E(e.change_resource_type), resource=e.change_resource_name, client=E(e.client_type),
                    op=E(e.resource_change_operation), fields=list(e.changed_fields.paths), campaign=e.campaign,
                    old_ceiling=money(e.old_resource.campaign.target_spend.cpc_bid_ceiling_micros),
                    new_ceiling=money(e.new_resource.campaign.target_spend.cpc_bid_ceiling_micros)))
out["change_events_since_0924"] = chg
print(f"\n  CHANGE_EVENT 2026-09-24..{TODAY}: {len(chg)} rows; by (date, client, type): "
      f"{dict(collections.Counter((x['at'][:10], x['client'], x['type']) for x in chg))}")
for x in chg:
    if x["type"] == "CAMPAIGN" and (REPAIR in x["resource"] or GEO in x["resource"]):
        print(f"    {x['at']} {x['client']} {x['op']} {x['resource']} fields={x['fields']} ceiling {x['old_ceiling']} -> {x['new_ceiling']}")
cs = []
for r in q(c, f"""SELECT change_status.resource_type, change_status.resource_status, change_status.last_change_date_time, change_status.campaign,
        change_status.ad_group FROM change_status WHERE change_status.last_change_date_time >= '2026-09-30 00:00:00'
        AND change_status.last_change_date_time <= '{TODAY} 23:59:59' LIMIT 1000"""):
    s = r.change_status
    cs.append(dict(type=E(s.resource_type), status=E(s.resource_status), at=s.last_change_date_time, campaign=s.campaign, ad_group=s.ad_group))
out["change_status_since_0930"] = cs
print(f"  CHANGE_STATUS since 09-30: {len(cs)} rows {dict(collections.Counter((x['at'][:10], x['type']) for x in cs))}")

# ---------------- performance (in scope) ----------------
perf = collections.defaultdict(dict)
METRIC = "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions"


def mm(x):
    return dict(impr=x.impressions, clicks=x.clicks, cost=money(x.cost_micros), conv=round(x.conversions, 2), all_conv=round(x.all_conversions, 2))


for r in q(c, f"SELECT campaign.id, segments.date, {METRIC} FROM campaign WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"):
    perf["campaign_daily"][f"{r.campaign.id}|{r.segments.date}"] = mm(r.metrics)
for r in q(c, f"""SELECT campaign.id, segments.date, metrics.search_impression_share, metrics.search_rank_lost_impression_share,
        metrics.search_budget_lost_impression_share FROM campaign WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"""):
    x = r.metrics
    perf["campaign_daily_is"][f"{r.campaign.id}|{r.segments.date}"] = dict(IS=x.search_impression_share, lost_rank=x.search_rank_lost_impression_share,
                                                                            lost_budget=x.search_budget_lost_impression_share)
for r in q(c, f"SELECT campaign.id, ad_group.id, segments.date, {METRIC} FROM ad_group WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"):
    perf["ad_group_daily"][f"{r.ad_group.id}|{r.segments.date}"] = mm(r.metrics)
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, segments.date, {METRIC} FROM keyword_view
        WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"""):
    perf["keyword_daily"][f"{r.ad_group.id}|{r.ad_group_criterion.criterion_id}|{r.segments.date}"] = mm(r.metrics)
for r in q(c, f"SELECT campaign.id, segments.date, segments.device, {METRIC} FROM campaign WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"):
    perf["device_daily"][f"{r.campaign.id}|{r.segments.date}|{E(r.segments.device)}"] = mm(r.metrics)
for r in q(c, f"SELECT campaign.id, segments.date, segments.hour, metrics.impressions, metrics.clicks, metrics.cost_micros FROM campaign WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '2026-09-24' AND '{TODAY}'"):
    perf["hourly"][f"{r.campaign.id}|{r.segments.date}|{r.segments.hour:02d}"] = dict(impr=r.metrics.impressions, clicks=r.metrics.clicks, cost=money(r.metrics.cost_micros))
for r in q(c, f"SELECT campaign.id, segments.date, segments.click_type, metrics.clicks, metrics.cost_micros FROM campaign WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"):
    perf["click_type_daily"][f"{r.campaign.id}|{r.segments.date}|{E(r.segments.click_type)}"] = dict(clicks=r.metrics.clicks, cost=money(r.metrics.cost_micros))
for r in q(c, f"""SELECT campaign.id, segments.date, segments.conversion_action, segments.conversion_action_name, metrics.conversions, metrics.all_conversions
        FROM campaign WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"""):
    perf["conv_by_action_daily"][f"{r.campaign.id}|{r.segments.date}|{r.segments.conversion_action_name}"] = dict(conv=round(r.metrics.conversions, 2), all_conv=round(r.metrics.all_conversions, 2))
for r in q(c, f"""SELECT campaign.id, ad_group.id, metrics.search_impression_share, metrics.search_rank_lost_impression_share FROM ad_group
        WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '2026-09-24' AND '2026-09-30'"""):
    perf["ad_group_is_baseline"][str(r.ad_group.id)] = dict(IS=r.metrics.search_impression_share, lost_rank=r.metrics.search_rank_lost_impression_share)
out["performance"] = dict(perf)

print("\n  CAMPAIGN DAILY (impr/clicks/cost/conv/all_conv) + IS")
for k in sorted(perf["campaign_daily"]):
    v, s = perf["campaign_daily"][k], perf["campaign_daily_is"].get(k, {})
    print(f"    {k} {v} IS={s.get('IS')} lostRank={s.get('lost_rank')} lostBud={s.get('lost_budget')}")
hrs = collections.defaultdict(list)
for k, v in perf["hourly"].items():
    cid, d, h = k.split("|")
    if v["impr"]:
        hrs[(cid, d)].append(int(h))
print("  serving hours (first..last hour with impressions):", {f"{a}|{b}": (min(v), max(v)) for (a, b), v in sorted(hrs.items())})

# ---------------- search terms (raw rows to disk only) ----------------
st_rows = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, search_term_view.search_term, search_term_view.status, segments.date,
        segments.search_term_match_type, segments.keyword.ad_group_criterion, segments.keyword.info.text, segments.keyword.info.match_type,
        metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions
        FROM search_term_view WHERE campaign.id IN ({INS}) AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}'"""):
    st_rows.append(dict(campaign_id=str(r.campaign.id), ad_group_id=str(r.ad_group.id), term=r.search_term_view.search_term,
                        status=E(r.search_term_view.status), date=r.segments.date, st_match=E(r.segments.search_term_match_type),
                        kw_criterion=r.segments.keyword.ad_group_criterion.split("~")[-1] if r.segments.keyword.ad_group_criterion else "",
                        kw_text=r.segments.keyword.info.text, kw_match=E(r.segments.keyword.info.match_type),
                        impr=r.metrics.impressions, clicks=r.metrics.clicks, cost=money(r.metrics.cost_micros),
                        conv=round(r.metrics.conversions, 2), all_conv=round(r.metrics.all_conversions, 2)))
# conversions by action per term (so a Primary record can be named)
st_conv = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, search_term_view.search_term, segments.date, segments.conversion_action_name,
        metrics.conversions, metrics.all_conversions FROM search_term_view WHERE campaign.id IN ({INS})
        AND segments.date BETWEEN '{HIST_A}' AND '{TODAY}' AND metrics.all_conversions > 0"""):
    st_conv.append(dict(campaign_id=str(r.campaign.id), ad_group_id=str(r.ad_group.id), term=r.search_term_view.search_term, date=r.segments.date,
                        action=r.segments.conversion_action_name, conv=round(r.metrics.conversions, 2), all_conv=round(r.metrics.all_conversions, 2)))
ST = EXPORTS / "search-terms-2026-10-01.jsonl"
with ST.open("w", encoding="utf-8") as f:
    for x in st_rows:
        f.write(json.dumps(x) + "\n")
(EXPORTS / "search-term-conversions-2026-10-01.json").write_text(json.dumps(st_conv, indent=1), encoding="utf-8")
out["search_terms_file"] = str(ST.relative_to(CLIENT_DIR))
print(f"\n  SEARCH TERMS: {len(st_rows)} date-rows, {len({(x['ad_group_id'], x['term']) for x in st_rows})} distinct (ad group, term) -> {ST.name}; "
      f"conversion rows {len(st_conv)}")
for cid in (REPAIR, GEO):
    for win, (a, b) in (("hist 09-17..09-23", (HIST_A, "2026-09-23")), ("baseline 09-24..09-30", ("2026-09-24", "2026-09-30")), (f"post {TODAY} PARTIAL", (TODAY, TODAY))):
        rows = [x for x in st_rows if x["campaign_id"] == cid and a <= x["date"] <= b]
        cr = {k: v for k, v in perf["campaign_daily"].items() if k.startswith(cid) and a <= k.split("|")[1] <= b}
        ci = sum(v["impr"] for v in cr.values()); cc = sum(v["cost"] for v in cr.values()); ck = sum(v["clicks"] for v in cr.values())
        si = sum(x["impr"] for x in rows); sc = round(sum(x["cost"] for x in rows), 2); sk = sum(x["clicks"] for x in rows)
        print(f"    {cid} {win:22s} campaign impr={ci} clicks={ck} cost=${cc:.2f} | visible terms impr={si} clicks={sk} cost=${sc} "
              f"({(100 * sc / cc if cc else 0):.0f}% of cost visible) distinct={len({x['term'] for x in rows})}")

(SNAP / "snapshot-2026-10-01.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print("\nwrote snapshots/snapshot-2026-10-01.json")
