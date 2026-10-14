#!/usr/bin/env python3
"""Ambient | 2026-09-25 | Fresh READ-ONLY inventory before the service-priority + PMax pass.

Covers: identity gate, account budget, every campaign's budget resource (shared/explicit),
status, primary status and reasons, schedule, network/geo/URL-expansion settings, goals;
every non-removed ad group, ad (final + mobile URLs, policy topics), keyword, label; today's
and trailing delivery; historical PMax campaigns 22822619680 and 23883756382.
"""
from __future__ import annotations
import sys, json, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP

SEVEN = {"24257819463": 6, "24268690038": 5, "24257819466": 5, "24132507744": 5,
         "24279798229": 5, "24268690041": 3, "24274160783": 1}
COMMERCIAL = "24132507747"
c = client()
gate = identity_gate(c, verbose=True)
now = datetime.datetime.now(TZ)
today = now.date().isoformat()
out = {"when": now.isoformat(), "gate": gate}

out["account_budget"] = [dict(id=str(r.account_budget.id), status=E(r.account_budget.status),
    approved_spending_limit=r.account_budget.approved_spending_limit_micros / 1e6,
    approved_spending_limit_type=E(r.account_budget.approved_spending_limit_type),
    amount_served=r.account_budget.amount_served_micros / 1e6,
    start=r.account_budget.approved_start_date_time, end=r.account_budget.approved_end_date_time or E(r.account_budget.approved_end_time_type))
    for r in q(c, """SELECT account_budget.id, account_budget.status, account_budget.approved_spending_limit_micros,
        account_budget.approved_spending_limit_type, account_budget.amount_served_micros,
        account_budget.approved_start_date_time, account_budget.approved_end_date_time,
        account_budget.approved_end_time_type FROM account_budget""")]

camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
        campaign.primary_status, campaign.primary_status_reasons, campaign.advertising_channel_type,
        campaign.bidding_strategy_type, campaign.maximize_conversions.target_cpa_micros,
        campaign.target_spend.cpc_bid_ceiling_micros,
        campaign.network_settings.target_search_network, campaign.network_settings.target_content_network,
        campaign.network_settings.target_partner_search_network,
        campaign.geo_target_type_setting.positive_geo_target_type,
        campaign.geo_target_type_setting.negative_geo_target_type,
        campaign.campaign_budget,
        campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros, campaign_budget.explicitly_shared,
        campaign_budget.reference_count, campaign_budget.status, campaign_budget.delivery_method,
        campaign_budget.period, campaign.labels
        FROM campaign WHERE campaign.status != 'REMOVED'"""):
    x = r.campaign
    camps[str(x.id)] = dict(name=x.name, status=E(x.status), serving=E(x.serving_status),
        primary=E(x.primary_status), reasons=[E(v) for v in x.primary_status_reasons],
        channel=E(x.advertising_channel_type), bidding=E(x.bidding_strategy_type),
        max_cpc_ceiling=(x.target_spend.cpc_bid_ceiling_micros or 0) / 1e6,
        tcpa=(x.maximize_conversions.target_cpa_micros or 0) / 1e6,
        search=x.network_settings.target_search_network, display=x.network_settings.target_content_network,
        partners=x.network_settings.target_partner_search_network,
        geo_pos=E(x.geo_target_type_setting.positive_geo_target_type),
        geo_neg=E(x.geo_target_type_setting.negative_geo_target_type),

        budget_id=str(r.campaign_budget.id), budget_name=r.campaign_budget.name,
        budget=r.campaign_budget.amount_micros / 1e6, budget_shared=r.campaign_budget.explicitly_shared,
        budget_refs=r.campaign_budget.reference_count, budget_status=E(r.campaign_budget.status),
        budget_period=E(r.campaign_budget.period), labels=list(x.labels))
out["campaigns"] = camps

def metrics(where_from, key, start, end, extra=""):
    res = collections.defaultdict(lambda: dict(impr=0, clicks=0, cost=0.0, conv=0.0, allconv=0.0))
    for r in q(c, f"""SELECT {key}, metrics.impressions, metrics.clicks, metrics.cost_micros,
            metrics.conversions, metrics.all_conversions FROM {where_from}
            WHERE segments.date BETWEEN '{start}' AND '{end}' {extra}"""):
        k = str(eval("r." + key))
        d = res[k]; d["impr"] += r.metrics.impressions; d["clicks"] += r.metrics.clicks
        d["cost"] += r.metrics.cost_micros / 1e6; d["conv"] += r.metrics.conversions; d["allconv"] += r.metrics.all_conversions
    return {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in res.items()}

out["camp_today"] = metrics("campaign", "campaign.id", today, today)
out["camp_mtd"] = metrics("campaign", "campaign.id", "2026-09-01", today)
out["ag_today"] = metrics("ad_group", "ad_group.id", today, today)
out["ag_since_0921"] = metrics("ad_group", "ad_group.id", "2026-09-21", today)

labels = {r.label.resource_name: dict(id=str(r.label.id), name=r.label.name, status=E(r.label.status))
          for r in q(c, "SELECT label.id, label.name, label.status, label.resource_name FROM label")}
out["labels"] = labels
ag_labels = collections.defaultdict(list)
for r in q(c, "SELECT ad_group_label.ad_group, ad_group_label.label FROM ad_group_label"):
    ag_labels[r.ad_group_label.ad_group.split("/")[-1]].append(labels.get(r.ad_group_label.label, {}).get("name"))

ags = {}
for r in q(c, """SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status,
        ad_group.primary_status_reasons, ad_group.type, campaign.id FROM ad_group
        WHERE campaign.status != 'REMOVED' AND ad_group.status != 'REMOVED'"""):
    g = r.ad_group
    ags[str(g.id)] = dict(name=g.name, status=E(g.status), primary=E(g.primary_status),
        reasons=[E(v) for v in g.primary_status_reasons], type=E(g.type), campaign=str(r.campaign.id),
        labels=ag_labels.get(str(g.id), []))
out["ad_groups"] = ags

ads = []
for r in q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status, ad_group_ad.ad.final_urls,
        ad_group_ad.ad.final_mobile_urls, ad_group_ad.ad.tracking_url_template, ad_group_ad.ad.final_url_suffix,
        ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status,
        ad_group_ad.policy_summary.policy_topic_entries, ad_group_ad.primary_status,
        ad_group_ad.primary_status_reasons, ad_group_ad.labels, ad_group.id, campaign.id
        FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED' AND campaign.status != 'REMOVED'"""):
    a = r.ad_group_ad
    ads.append(dict(id=str(a.ad.id), type=E(a.ad.type), status=E(a.status), ad_group=str(r.ad_group.id),
        campaign=str(r.campaign.id), final=list(a.ad.final_urls), mobile=list(a.ad.final_mobile_urls),
        tracking=a.ad.tracking_url_template, suffix=a.ad.final_url_suffix,
        approval=E(a.policy_summary.approval_status), review=E(a.policy_summary.review_status),
        topics=[(t.topic, E(t.type_)) for t in a.policy_summary.policy_topic_entries],
        primary=E(a.primary_status), reasons=[E(v) for v in a.primary_status_reasons]))
out["ads"] = ads

kws = []
for r in q(c, """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type, ad_group_criterion.status, ad_group_criterion.negative,
        ad_group_criterion.final_urls, ad_group_criterion.final_mobile_urls, ad_group_criterion.approval_status,
        ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons, ad_group.id, campaign.id
        FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'
        AND campaign.status != 'REMOVED' AND ad_group.status != 'REMOVED'"""):
    k = r.ad_group_criterion
    kws.append(dict(id=str(k.criterion_id), text=k.keyword.text, mt=E(k.keyword.match_type), status=E(k.status),
        neg=k.negative, final=list(k.final_urls), mobile=list(k.final_mobile_urls), approval=E(k.approval_status),
        primary=E(k.primary_status), reasons=[E(v) for v in k.primary_status_reasons],
        ad_group=str(r.ad_group.id), campaign=str(r.campaign.id)))
out["keywords"] = kws

sched = collections.defaultdict(list)
for r in q(c, """SELECT campaign.id, campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour,
        campaign_criterion.ad_schedule.end_hour, campaign_criterion.ad_schedule.start_minute,
        campaign_criterion.ad_schedule.end_minute FROM campaign_criterion
        WHERE campaign_criterion.type = 'AD_SCHEDULE' AND campaign.status != 'REMOVED'"""):
    s = r.campaign_criterion.ad_schedule
    sched[str(r.campaign.id)].append(f"{E(s.day_of_week)[:3]} {s.start_hour:02d}-{s.end_hour:02d}")
out["schedules"] = sched

geo = collections.defaultdict(lambda: collections.Counter())
for r in q(c, """SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative FROM campaign_criterion
        WHERE campaign_criterion.type IN ('LOCATION','PROXIMITY') AND campaign.status != 'REMOVED'"""):
    geo[str(r.campaign.id)][("neg " if r.campaign_criterion.negative else "") + E(r.campaign_criterion.type)] += 1
out["geo_counts"] = {k: dict(v) for k, v in geo.items()}

out["conversion_actions"] = [dict(id=str(r.conversion_action.id), name=r.conversion_action.name,
    status=E(r.conversion_action.status), type=E(r.conversion_action.type), category=E(r.conversion_action.category),
    origin=E(r.conversion_action.origin), primary=r.conversion_action.primary_for_goal,
    counting=E(r.conversion_action.counting_type))
    for r in q(c, """SELECT conversion_action.id, conversion_action.name, conversion_action.status, conversion_action.type,
        conversion_action.category, conversion_action.origin, conversion_action.primary_for_goal,
        conversion_action.counting_type FROM conversion_action WHERE conversion_action.status != 'REMOVED'""")]
out["customer_goals"] = [(E(r.customer_conversion_goal.category), E(r.customer_conversion_goal.origin), r.customer_conversion_goal.biddable)
    for r in q(c, "SELECT customer_conversion_goal.category, customer_conversion_goal.origin, customer_conversion_goal.biddable FROM customer_conversion_goal")]
cg = collections.defaultdict(list)
for r in q(c, """SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin,
        campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.status != 'REMOVED'"""):
    if r.campaign_conversion_goal.biddable:
        cg[str(r.campaign.id)].append(f"{E(r.campaign_conversion_goal.category)}/{E(r.campaign_conversion_goal.origin)}")
out["campaign_biddable_goals"] = cg
out["campaign_goal_config"] = {str(r.campaign.id): [E(r.conversion_goal_campaign_config.goal_config_level),
    r.conversion_goal_campaign_config.custom_conversion_goal]
    for r in q(c, """SELECT campaign.id, conversion_goal_campaign_config.goal_config_level,
        conversion_goal_campaign_config.custom_conversion_goal FROM conversion_goal_campaign_config
        WHERE campaign.status != 'REMOVED'""")}
out["custom_goals"] = [(r.custom_conversion_goal.resource_name, r.custom_conversion_goal.name,
    list(r.custom_conversion_goal.conversion_actions), E(r.custom_conversion_goal.status))
    for r in q(c, "SELECT custom_conversion_goal.resource_name, custom_conversion_goal.name, custom_conversion_goal.conversion_actions, custom_conversion_goal.status FROM custom_conversion_goal")]

(SNAP / "inventory-2026-09-25.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")

# ---------- print compact view ----------
print(f"\n{now:%Y-%m-%d %H:%M} ET | account budgets: {out['account_budget']}")
enabled_total = 0.0; seen_budgets = set()
for cid, v in sorted(camps.items(), key=lambda x: x[1]["name"]):
    if v["status"] == "ENABLED" and v["budget_id"] not in seen_budgets:
        enabled_total += v["budget"]; seen_budgets.add(v["budget_id"])
    t = out["camp_today"].get(cid, {}); mt = out["camp_mtd"].get(cid, {})
    if v["status"] == "ENABLED" or cid in SEVEN or v["channel"] == "PERFORMANCE_MAX":
        print(f"{cid} {v['status']:7s} {v['channel'][:6]} {v['primary'][:12]:12s} ${v['budget']:>6.2f} b{v['budget_id']} shared={v['budget_shared']} refs={v['budget_refs']} "
              f"{v['bidding']} ceil={v['max_cpc_ceiling']} | today {t.get('impr',0)}i ${t.get('cost',0)} | MTD ${mt.get('cost',0)} {mt.get('conv',0)}cv | {v['name'][:55]}")
        print(f"      reasons={v['reasons']} sched={sched.get(cid)} geo={out['geo_counts'].get(cid)} partners={v['partners']} display={v['display']} goals={cg.get(cid)} cfg={out['campaign_goal_config'].get(cid)}")
print(f"ENABLED campaign budget total (unique budgets): ${enabled_total:.2f}")
print("labels:", sorted(v["name"] for v in labels.values()))
for cid in list(SEVEN) + [COMMERCIAL]:
    print(f"\n== {cid} {camps[cid]['name']} ({camps[cid]['status']}) expected groups {SEVEN.get(cid,'-')}")
    for gid, g in sorted(ags.items(), key=lambda x: x[1]["name"]):
        if g["campaign"] != cid: continue
        gads = [a for a in ads if a["ad_group"] == gid]
        en = [a for a in gads if a["status"] == "ENABLED"]
        urls = sorted({(a["final"] or [""])[0].replace("https://", "")[:60] for a in gads})
        gk = [k for k in kws if k["ad_group"] == gid and not k["neg"]]
        t = out["ag_today"].get(gid, {}); s = out["ag_since_0921"].get(gid, {})
        print(f"  {gid} {g['status']:7s} {g['primary'][:12]:12s} {g['name'][:40]:40s} ads {len(en)}en/{len(gads)} kw {sum(1 for k in gk if k['status']=='ENABLED')}en/{len(gk)} "
              f"today {t.get('impr',0)}i since0921 {s.get('impr',0)}i ${s.get('cost',0)} {s.get('conv',0)}cv labels={g['labels']} reasons={g['reasons']}")
        for a in gads:
            print(f"      ad {a['id']} {a['status']:7s} {a['approval']:16s} {a['primary'][:12]:12s} {(a['final'] or [''])[0].replace('https://','')[:70]} mob={a['mobile']} sfx={a['suffix']!r} topics={a['topics']}")
print("\nconversion actions (non-removed, enabled):")
for x in out["conversion_actions"]:
    if x["status"] == "ENABLED":
        print(f"  {x['id']} primary={x['primary']!s:5s} {x['category']:22s} {x['origin']:12s} {x['type']:22s} {x['name']}")
print("customer goals biddable:", [g for g in out["customer_goals"] if g[2]])
print("custom goals:", out["custom_goals"])
