#!/usr/bin/env python3
"""2026-09-28 READ-ONLY low-volume audit for Apogee Lawns LLC - Live (8164626278).

Question: why is the permanent-Christmas-lights campaign getting so few impressions and clicks?
Nothing here mutates. Search terms are classified on disk; stdout carries aggregates only.
"""
from __future__ import annotations

import datetime
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, CLIENT_DIR, EVID, EXACT_NAME, GM_MANAGER, ROOT, E, client, q, write  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402

TODAY = datetime.date(2026, 9, 28)
OUT = {}
c = client()


def M(v):
    return round(v / 1e6, 2)


print("=== 1. WORK ORDER vs CLIENT PROFILE ===")
wo = yaml.safe_load((CLIENT_DIR / "work-order.yaml").read_text(encoding="utf-8"))
cp = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
errs = validate_work_order(wo, cp)
print(f"  validate_work_order errors: {len(errs)}")
for e in errs:
    print(f"    - {e}")
OUT["work_order_errors"] = errs

print("\n=== 2. IDENTITY GATE (fresh read) ===")
kids = q(c, f"""SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager,
    customer_client.test_account, customer_client.status FROM customer_client
    WHERE customer_client.id = {CID}""", cid=GM_MANAGER)
cust = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account,
    customer.status, customer.time_zone, customer.currency_code, customer.auto_tagging_enabled
    FROM customer""")[0].customer
ident = {
    "manager_view": [{"id": str(r.customer_client.id), "name": r.customer_client.descriptive_name,
                      "manager": r.customer_client.manager, "test": r.customer_client.test_account,
                      "status": E(r.customer_client.status)} for r in kids],
    "child_view": {"id": str(cust.id), "name": cust.descriptive_name, "manager": cust.manager,
                   "test": cust.test_account, "status": E(cust.status), "tz": cust.time_zone},
}
ok = (str(cust.id) == CID and cust.descriptive_name == EXACT_NAME and not cust.manager
      and not cust.test_account and len(kids) == 1 and kids[0].customer_client.descriptive_name == EXACT_NAME)
print(f"  child: {cust.id} '{cust.descriptive_name}' mgr={cust.manager} test={cust.test_account} "
      f"{E(cust.status)} tz={cust.time_zone}")
print(f"  GATE: {'PASS' if ok else 'FAIL'}")
OUT["identity"] = ident
if not ok:
    write(EVID / "2026-09-28-audit.json", OUT)
    sys.exit("HARD STOP: identity mismatch")

print("\n=== 3. BILLING / ACCOUNT BUDGET ===")
bs = q(c, """SELECT billing_setup.id, billing_setup.status, billing_setup.start_date_time,
    billing_setup.payments_account_info.payments_account_name FROM billing_setup""")
for r in bs:
    b = r.billing_setup
    print(f"  billing_setup {b.id} {E(b.status)} start={b.start_date_time} acct='{b.payments_account_info.payments_account_name}'")
ab = q(c, """SELECT account_budget.id, account_budget.status, account_budget.approved_start_date_time,
    account_budget.approved_end_date_time, account_budget.approved_spending_limit_micros,
    account_budget.approved_spending_limit_type, account_budget.amount_served_micros FROM account_budget""")
for r in ab:
    a = r.account_budget
    print(f"  account_budget {a.id} {E(a.status)} {a.approved_start_date_time}..{a.approved_end_date_time} "
          f"limit={M(a.approved_spending_limit_micros)} type={E(a.approved_spending_limit_type)} served={M(a.amount_served_micros)}")
OUT["billing"] = [{"id": r.billing_setup.id, "status": E(r.billing_setup.status)} for r in bs]

print("\n=== 4. CAMPAIGNS (all statuses) ===")
camps = q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
    campaign.primary_status, campaign.primary_status_reasons, campaign.advertising_channel_type,
    campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
    campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
    campaign.network_settings.target_content_network, campaign.geo_target_type_setting.positive_geo_target_type,
    campaign.start_date_time, campaign.end_date_time, campaign_budget.amount_micros,
    campaign_budget.id, campaign.keyword_match_type FROM campaign""")
for r in camps:
    x = r.campaign
    print(f"  {x.id} [{E(x.status)}/{E(x.serving_status)}/{E(x.primary_status)}] {x.name}")
    print(f"     reasons={[E(y) for y in x.primary_status_reasons]} bid={E(x.bidding_strategy_type)} "
          f"ceiling={M(x.target_spend.cpc_bid_ceiling_micros)} budget/day={M(r.campaign_budget.amount_micros)}")
    print(f"     google={x.network_settings.target_google_search} partners={x.network_settings.target_search_network} "
          f"display={x.network_settings.target_content_network} geo={E(x.geo_target_type_setting.positive_geo_target_type)} "
          f"start={x.start_date_time} end={x.end_date_time} kmt={E(x.keyword_match_type)}")
OUT["campaigns"] = [{"id": r.campaign.id, "name": r.campaign.name, "status": E(r.campaign.status),
                     "primary_status": E(r.campaign.primary_status),
                     "reasons": [E(y) for y in r.campaign.primary_status_reasons]} for r in camps]

print("\n=== 5. AD GROUPS ===")
ags = q(c, """SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status,
    ad_group.primary_status_reasons, ad_group.cpc_bid_micros, campaign.id FROM ad_group
    WHERE ad_group.status != 'REMOVED'""")
for r in ags:
    a = r.ad_group
    print(f"  {a.id} [{E(a.status)}/{E(a.primary_status)}] {a.name} reasons={[E(y) for y in a.primary_status_reasons]}")

print("\n=== 6. KEYWORDS (status, serving, QS) ===")
kws = q(c, """SELECT ad_group.id, ad_group.name, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type, ad_group_criterion.status, ad_group_criterion.negative,
    ad_group_criterion.system_serving_status, ad_group_criterion.approval_status,
    ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
    ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score,
    ad_group_criterion.quality_info.post_click_quality_score,
    ad_group_criterion.quality_info.search_predicted_ctr,
    ad_group_criterion.position_estimates.first_page_cpc_micros,
    ad_group_criterion.position_estimates.top_of_page_cpc_micros,
    ad_group_criterion.position_estimates.first_position_cpc_micros,
    ad_group_criterion.effective_cpc_bid_micros
    FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'
    AND ad_group_criterion.negative = FALSE""")
kwrows = []
for r in kws:
    k = r.ad_group_criterion
    qi, pe = k.quality_info, k.position_estimates
    row = {"ag": r.ad_group.name, "id": k.criterion_id, "text": k.keyword.text, "mt": E(k.keyword.match_type),
           "status": E(k.status), "serving": E(k.system_serving_status), "approval": E(k.approval_status),
           "primary": E(k.primary_status), "reasons": [E(y) for y in k.primary_status_reasons],
           "qs": qi.quality_score, "ad_rel": E(qi.creative_quality_score), "lp": E(qi.post_click_quality_score),
           "ectr": E(qi.search_predicted_ctr), "first_page": M(pe.first_page_cpc_micros),
           "top": M(pe.top_of_page_cpc_micros), "first_pos": M(pe.first_position_cpc_micros),
           "eff_bid": M(k.effective_cpc_bid_micros)}
    kwrows.append(row)
    print(f"  {row['ag'][:34]:<34} {row['mt']:<6} {row['text']:<42} {row['status']}/{row['serving']}/{row['primary']} "
          f"{row['reasons']} QS={row['qs']} ({row['ectr']}/{row['ad_rel']}/{row['lp']}) "
          f"1stpg=${row['first_page']} top=${row['top']} 1st=${row['first_pos']}")
OUT["keywords"] = kwrows

print("\n=== 7. ADS (approval / policy) ===")
ads = q(c, """SELECT ad_group.name, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.primary_status,
    ad_group_ad.primary_status_reasons, ad_group_ad.policy_summary.approval_status,
    ad_group_ad.policy_summary.review_status, ad_group_ad.policy_summary.policy_topic_entries,
    ad_group_ad.ad.final_urls, ad_group_ad.ad_strength FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'""")
adrows = []
for r in ads:
    a = r.ad_group_ad
    topics = [(t.topic, E(t.type_)) for t in a.policy_summary.policy_topic_entries]
    adrows.append({"ag": r.ad_group.name, "id": a.ad.id, "status": E(a.status), "primary": E(a.primary_status),
                   "reasons": [E(y) for y in a.primary_status_reasons],
                   "approval": E(a.policy_summary.approval_status), "review": E(a.policy_summary.review_status),
                   "topics": topics, "urls": list(a.ad.final_urls), "strength": E(a.ad_strength)})
    print(f"  {a.ad.id} {r.ad_group.name[:30]:<30} {E(a.status)}/{E(a.primary_status)} "
          f"{[E(y) for y in a.primary_status_reasons]} approval={E(a.policy_summary.approval_status)} "
          f"review={E(a.policy_summary.review_status)} topics={topics} strength={E(a.ad_strength)}")
    print(f"     url={list(a.ad.final_urls)}")
OUT["ads"] = adrows

print("\n=== 8. CAMPAIGN CRITERIA ===")
cc = q(c, """SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type, campaign_criterion.negative,
    campaign_criterion.status, campaign_criterion.bid_modifier, campaign_criterion.location.geo_target_constant,
    campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
    campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour,
    campaign_criterion.ad_schedule.end_hour, campaign_criterion.device.type
    FROM campaign_criterion""")
types = Counter((E(r.campaign_criterion.type), r.campaign_criterion.negative) for r in cc)
print(f"  criteria by (type, negative): {dict(types)}")
geos = [r.campaign_criterion.location.geo_target_constant for r in cc
        if E(r.campaign_criterion.type) == "LOCATION" and not r.campaign_criterion.negative]
negkw = [(r.campaign_criterion.keyword.text, E(r.campaign_criterion.keyword.match_type)) for r in cc
         if E(r.campaign_criterion.type) == "KEYWORD" and r.campaign_criterion.negative]
sched = [(E(r.campaign_criterion.ad_schedule.day_of_week), r.campaign_criterion.ad_schedule.start_hour,
          r.campaign_criterion.ad_schedule.end_hour) for r in cc if E(r.campaign_criterion.type) == "AD_SCHEDULE"]
dev = [(E(r.campaign_criterion.device.type), r.campaign_criterion.bid_modifier) for r in cc
       if E(r.campaign_criterion.type) == "DEVICE"]
print(f"  ad schedule rows: {sched}")
print(f"  device modifiers: {dev}")
OUT["geo_targets"] = geos
OUT["campaign_negatives"] = negkw
if geos:
    names = q(c, "SELECT geo_target_constant.resource_name, geo_target_constant.canonical_name, "
                 "geo_target_constant.target_type, geo_target_constant.status FROM geo_target_constant "
                 "WHERE geo_target_constant.resource_name IN (" + ",".join(f"'{g}'" for g in geos) + ")")
    OUT["geo_names"] = {r.geo_target_constant.resource_name: [r.geo_target_constant.canonical_name,
                        r.geo_target_constant.target_type, E(r.geo_target_constant.status)] for r in names}
    for g, v in OUT["geo_names"].items():
        print(f"    geo {g.split('/')[-1]:>9} {v[1]:<14} {v[2]:<8} {v[0]}")

print("\n=== 9. NEGATIVE REVERSE CHECK (does any campaign negative block a positive?) ===")
positives = [k["text"].lower() for k in kwrows]
hits = []
for text, mt in negkw:
    nt = text.lower().strip('"[]')
    for p in positives:
        pw = p.split()
        if mt == "BROAD" and all(w in pw for w in nt.split()):
            hits.append((text, mt, p))
        elif mt == "PHRASE" and f" {nt} " in f" {p} ":
            hits.append((text, mt, p))
        elif mt == "EXACT" and nt == p:
            hits.append((text, mt, p))
print(f"  campaign negatives: {len(negkw)}; conflicts with positives: {len(hits)}")
for h in hits:
    print(f"    CONFLICT {h}")
shared = q(c, """SELECT campaign_shared_set.shared_set, campaign_shared_set.status, campaign.id FROM campaign_shared_set""")
print(f"  campaign_shared_set rows: {len(shared)} {[ (r.campaign_shared_set.shared_set, E(r.campaign_shared_set.status)) for r in shared]}")
acct = q(c, """SELECT customer_negative_criterion.id, customer_negative_criterion.type,
    customer_negative_criterion.negative_keyword_list.shared_set FROM customer_negative_criterion""")
print(f"  customer_negative_criterion rows: {[(r.customer_negative_criterion.id, E(r.customer_negative_criterion.type), r.customer_negative_criterion.negative_keyword_list.shared_set) for r in acct]}")

print("\n=== 10. CHANGE HISTORY since 2026-08-30 ===")
ch = q(c, """SELECT change_event.change_date_time, change_event.change_resource_type, change_event.resource_change_operation,
    change_event.client_type, change_event.changed_fields, change_event.change_resource_name,
    change_event.new_resource, change_event.old_resource
    FROM change_event WHERE change_event.change_date_time >= '2026-08-30 00:00:00'
    AND change_event.change_date_time <= '2026-09-28 23:59:59' ORDER BY change_event.change_date_time ASC LIMIT 1000""")
chrows = []
for r in ch:
    e = r.change_event
    row = {"t": e.change_date_time, "type": E(e.change_resource_type), "op": E(e.resource_change_operation),
           "client": E(e.client_type), "fields": list(e.changed_fields.paths), "res": e.change_resource_name}
    extra = ""
    if row["type"] == "CAMPAIGN" and "status" in row["fields"]:
        extra = f" status {E(e.old_resource.campaign.status)}->{E(e.new_resource.campaign.status)}"
    if row["type"] == "CAMPAIGN_BUDGET" and "amount_micros" in row["fields"]:
        extra = f" budget {M(e.old_resource.campaign_budget.amount_micros)}->{M(e.new_resource.campaign_budget.amount_micros)}"
    if row["type"] == "CAMPAIGN" and any("cpc_bid_ceiling" in f for f in row["fields"]):
        extra += (f" ceiling {M(e.old_resource.campaign.target_spend.cpc_bid_ceiling_micros)}->"
                  f"{M(e.new_resource.campaign.target_spend.cpc_bid_ceiling_micros)}")
    if row["type"] == "AD_GROUP" and "status" in row["fields"]:
        extra = f" ag status {E(e.old_resource.ad_group.status)}->{E(e.new_resource.ad_group.status)}"
    if row["type"] == "AD_GROUP_CRITERION":
        k = e.new_resource.ad_group_criterion
        extra = f" kw '{k.keyword.text}' {E(k.keyword.match_type)} neg={k.negative} status={E(k.status)}"
    if row["type"] == "CAMPAIGN_CRITERION":
        k = e.new_resource.campaign_criterion
        extra = f" crit type={E(k.type_)} neg={k.negative}"
    row["extra"] = extra
    chrows.append(row)
    print(f"  {row['t']} {row['client']:<22} {row['op']:<7} {row['type']:<22} {row['fields'][:6]}{extra}")
OUT["changes"] = chrows

print("\n=== 11. DAILY DELIVERY since 2026-09-17 ===")
d = q(c, """SELECT segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
    metrics.search_impression_share, metrics.search_budget_lost_impression_share,
    metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,
    metrics.search_absolute_top_impression_share, metrics.average_cpc, metrics.invalid_clicks
    FROM campaign WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
byday = {}
for r in d:
    m = r.metrics
    byday[r.segments.date] = {"impr": m.impressions, "clicks": m.clicks, "cost": M(m.cost_micros),
                              "conv": round(m.conversions, 2), "is": round(m.search_impression_share, 3),
                              "lost_budget": round(m.search_budget_lost_impression_share, 3),
                              "lost_rank": round(m.search_rank_lost_impression_share, 3),
                              "top": round(m.search_top_impression_share, 3), "invalid": m.invalid_clicks}
axis = [(datetime.date(2026, 9, 17) + datetime.timedelta(days=i)).isoformat() for i in range(12)]
for day in axis:
    print(f"  {day} {byday.get(day, 'NO ROW (zero delivery)')}")
OUT["daily"] = byday

print("\n=== 12. TOTALS since 2026-09-17 by campaign / ad group / keyword ===")
tot = q(c, """SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
    metrics.all_conversions, metrics.search_impression_share, metrics.search_budget_lost_impression_share,
    metrics.search_rank_lost_impression_share, metrics.search_exact_match_impression_share,
    metrics.average_cpc, metrics.ctr FROM campaign WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
for r in tot:
    m = r.metrics
    print(f"  campaign {r.campaign.id}: impr={m.impressions} clicks={m.clicks} cost=${M(m.cost_micros)} "
          f"conv={m.conversions:.2f} allconv={m.all_conversions:.2f} IS={m.search_impression_share:.3f} "
          f"lostB={m.search_budget_lost_impression_share:.3f} lostR={m.search_rank_lost_impression_share:.3f} "
          f"exactIS={m.search_exact_match_impression_share:.3f} cpc=${M(m.average_cpc)} ctr={m.ctr:.3f}")
kv = q(c, """SELECT ad_group.id, ad_group.name, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type, metrics.impressions, metrics.clicks, metrics.cost_micros,
    metrics.search_impression_share, metrics.search_rank_lost_impression_share,
    metrics.search_exact_match_impression_share, metrics.average_cpc
    FROM keyword_view WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
for r in kv:
    m = r.metrics
    print(f"  kw {r.ad_group.name[:30]:<30} {E(r.ad_group_criterion.keyword.match_type):<6} "
          f"{r.ad_group_criterion.keyword.text:<42} impr={m.impressions} clicks={m.clicks} cost=${M(m.cost_micros)} "
          f"IS={m.search_impression_share:.3f} lostR={m.search_rank_lost_impression_share:.3f} cpc=${M(m.average_cpc)}")
OUT["keyword_perf"] = [{"ag": r.ad_group.name, "text": r.ad_group_criterion.keyword.text,
                        "mt": E(r.ad_group_criterion.keyword.match_type), "impr": r.metrics.impressions,
                        "clicks": r.metrics.clicks, "cost": M(r.metrics.cost_micros),
                        "is": r.metrics.search_impression_share,
                        "lost_rank": r.metrics.search_rank_lost_impression_share} for r in kv]

print("\n=== 13. HOURLY / DEVICE / NETWORK split since 2026-09-17 ===")
hr = q(c, """SELECT segments.hour, metrics.impressions, metrics.clicks FROM campaign
    WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
hh = Counter()
for r in hr:
    hh[r.segments.hour] += r.metrics.impressions
print(f"  impressions by hour: {dict(sorted(hh.items()))}")
dv = q(c, """SELECT segments.device, segments.ad_network_type, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM campaign WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
for r in dv:
    print(f"  {E(r.segments.device):<14} {E(r.segments.ad_network_type):<14} impr={r.metrics.impressions} "
          f"clicks={r.metrics.clicks} cost=${M(r.metrics.cost_micros)}")

print("\n=== 14. WHERE THE IMPRESSIONS CAME FROM ===")
uv = q(c, """SELECT user_location_view.country_criterion_id, user_location_view.targeting_location,
    segments.geo_target_most_specific_location, metrics.impressions, metrics.clicks
    FROM user_location_view WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
locs = Counter()
for r in uv:
    locs[(r.segments.geo_target_most_specific_location, r.user_location_view.targeting_location)] += r.metrics.impressions
lv = q(c, """SELECT campaign_criterion.criterion_id, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM location_view WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
for r in lv:
    print(f"  target {r.campaign_criterion.criterion_id}: impr={r.metrics.impressions} clicks={r.metrics.clicks} "
          f"cost=${M(r.metrics.cost_micros)}")
OUT["user_locations"] = {f"{k[0]}|{k[1]}": v for k, v in locs.items()}
print(f"  user_location rows: {len(locs)}; in-target impressions share: "
      f"{sum(v for k, v in locs.items() if k[1]) }/{sum(locs.values())}")

print("\n=== 15. SEARCH TERMS (aggregates only; raw terms stay on disk) ===")
st = q(c, """SELECT search_term_view.search_term, search_term_view.status, segments.keyword.info.text,
    segments.keyword.info.match_type, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM search_term_view WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
raw_path = EVID / "2026-09-28-search-terms-RAW.json"
raw = [{"term": r.search_term_view.search_term, "kw": r.segments.keyword.info.text,
        "mt": E(r.segments.keyword.info.match_type), "impr": r.metrics.impressions,
        "clicks": r.metrics.clicks, "cost": M(r.metrics.cost_micros)} for r in st]
write(raw_path, raw)
agg = defaultdict(lambda: [0, 0, 0, 0.0])
for x in raw:
    a = agg[(x["kw"], x["mt"])]
    a[0] += 1
    a[1] += x["impr"]
    a[2] += x["clicks"]
    a[3] += x["cost"]
for k, v in agg.items():
    print(f"  via {k}: terms={v[0]} impr={v[1]} clicks={v[2]} cost=${v[3]:.2f}")
print(f"  total search-term rows: {len(raw)}")

print("\n=== 16. CONVERSIONS since 2026-09-17 by action ===")
cv = q(c, """SELECT segments.conversion_action_name, metrics.all_conversions, metrics.conversions
    FROM campaign WHERE segments.date BETWEEN '2026-09-17' AND '2026-09-28'""")
for r in cv:
    print(f"  {r.segments.conversion_action_name}: all={r.metrics.all_conversions:.2f} conv={r.metrics.conversions:.2f}")

print("\n=== 17. ASSETS linked to the campaign ===")
ca = q(c, """SELECT campaign.id, campaign_asset.field_type, campaign_asset.status, campaign_asset.primary_status,
    campaign_asset.primary_status_reasons, asset.id, asset.type, asset.policy_summary.approval_status
    FROM campaign_asset WHERE campaign_asset.status != 'REMOVED'""")
for r in ca:
    print(f"  {E(r.campaign_asset.field_type):<18} {r.asset.id} {E(r.campaign_asset.status)}/{E(r.campaign_asset.primary_status)} "
          f"{[E(y) for y in r.campaign_asset.primary_status_reasons]} approval={E(r.asset.policy_summary.approval_status)}")

write(EVID / "2026-09-28-audit.json", OUT)
