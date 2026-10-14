#!/usr/bin/env python3
"""Ambient | 2026-10-05 | READ-ONLY pull for the Heating & Furnace Repair optimization-prep request.

Campaign 24257819463 only (plus account-wide call_view for the phone audit). No mutations.
- identity gate + work-order validation
- live config (ceiling, budget, bidding, networks, schedule, locations, devices) for a drift check
- change_event 2026-09-30 .. today (bounded both ends), filtered to this campaign and its ad groups
- daily campaign metrics 09-17..today with impression share; window aggregates (IS is never averaged by day)
- ad group / keyword / device / click type / hour, daily
- every visible search term 09-17..today (no threshold)
- every negative layer reaching the campaign (account lists, attached shared lists, campaign, ad group)
- call assets, location asset sets, call_view since 09-17 (all campaigns)
Writes snapshots/repair-read-2026-10-05.json and exports/repair-search-terms-2026-10-05.jsonl.
"""
from __future__ import annotations
import sys, json, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, EXPORTS, CLIENT_DIR  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
import yaml  # noqa: E402

CAMP = "24257819463"
A = "2026-09-17"
NOW = datetime.datetime.now(TZ)
TODAY = NOW.date().isoformat()
WO = "work-order-heating-repair-optimization-prep-2026-10-05.yaml"
money = lambda m: round(m / 1e6, 2)

cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
err = validate_work_order(yaml.safe_load((CLIENT_DIR / "work-orders" / WO).read_text(encoding="utf-8")), cl)
print(f"work order {WO}: {'VALID' if not err else err}")
if err:
    sys.exit("HARD STOP: work order invalid")
c = client()
ident = identity_gate(c, verbose=True)
out = {"read_local": NOW.isoformat(), "identity": {k: v for k, v in ident.items() if k != "checks"}, "today_partial": TODAY}
yd = q(c, "SELECT segments.date, metrics.impressions FROM customer WHERE segments.date DURING YESTERDAY")
out["account_yesterday"] = yd[0].segments.date if yd else "no row"

# ---------------- config ----------------
r = q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign.primary_status, campaign.primary_status_reasons, campaign.bidding_strategy_type,
        campaign.target_spend.cpc_bid_ceiling_micros, campaign_budget.id, campaign_budget.amount_micros, campaign_budget.explicitly_shared,
        campaign.network_settings.target_google_search, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network,
        campaign.geo_target_type_setting.positive_geo_target_type, campaign.ai_max_setting.enable_ai_max FROM campaign WHERE campaign.id = {CAMP}""")[0]
x = r.campaign
cfg = dict(name=x.name, status=E(x.status), primary=E(x.primary_status), reasons=[E(v) for v in x.primary_status_reasons], bidding=E(x.bidding_strategy_type),
           ceiling=money(x.target_spend.cpc_bid_ceiling_micros), budget_id=str(r.campaign_budget.id), budget=money(r.campaign_budget.amount_micros),
           shared_budget=r.campaign_budget.explicitly_shared, search=x.network_settings.target_google_search, partners=x.network_settings.target_search_network,
           display=x.network_settings.target_content_network, geo=E(x.geo_target_type_setting.positive_geo_target_type), ai_max=x.ai_max_setting.enable_ai_max)
crit = collections.defaultdict(list)
for r in q(c, f"""SELECT campaign_criterion.criterion_id, campaign_criterion.type, campaign_criterion.negative, campaign_criterion.status, campaign_criterion.bid_modifier,
        campaign_criterion.device.type, campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour,
        campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, campaign_criterion.location.geo_target_constant
        FROM campaign_criterion WHERE campaign.id = {CAMP}"""):
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
    crit[t].append(row)
cfg["schedule"] = sorted((s["day"], s["start"], s["end"]) for s in crit["AD_SCHEDULE"])
cfg["locations_positive"] = sum(1 for l in crit["LOCATION"] if not l["neg"])
cfg["devices"] = {d["device"]: (round(d["bid_modifier"], 2) if d["bid_modifier_set"] else "unset") for d in crit["DEVICE"]}
out["config"], out["campaign_criteria"] = cfg, dict(crit)

ags = {}
for r in q(c, f"SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status, ad_group.primary_status_reasons FROM ad_group WHERE campaign.id = {CAMP} AND ad_group.status != 'REMOVED'"):
    g = r.ad_group
    ags[str(g.id)] = dict(name=g.name, status=E(g.status), primary=E(g.primary_status), reasons=[E(v) for v in g.primary_status_reasons])
out["ad_groups"] = ags
kws = []
for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.negative,
        ad_group_criterion.status, ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons, ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.creative_quality_score, ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr
        FROM ad_group_criterion WHERE campaign.id = {CAMP} AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'"""):
    k = r.ad_group_criterion
    kws.append(dict(ad_group=str(r.ad_group.id), id=str(k.criterion_id), text=k.keyword.text, match=E(k.keyword.match_type), negative=k.negative,
                    status=E(k.status), primary=E(k.primary_status), reasons=[E(v) for v in k.primary_status_reasons], qs=k.quality_info.quality_score,
                    ad_rel=E(k.quality_info.creative_quality_score), lp=E(k.quality_info.post_click_quality_score), ectr=E(k.quality_info.search_predicted_ctr)))
out["keywords"] = kws
ads = []
for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.policy_summary.approval_status, ad_group_ad.ad.final_urls
        FROM ad_group_ad WHERE campaign.id = {CAMP} AND ad_group_ad.status != 'REMOVED'"""):
    a = r.ad_group_ad
    ads.append(dict(ad_group=str(r.ad_group.id), id=str(a.ad.id), status=E(a.status), approval=E(a.policy_summary.approval_status), urls=list(a.ad.final_urls)))
out["ads"] = ads

# ---------------- negative layers ----------------
att = [dict(set=str(r.shared_set.id), name=r.shared_set.name, status=E(r.campaign_shared_set.status))
       for r in q(c, f"SELECT shared_set.id, shared_set.name, campaign_shared_set.status FROM campaign_shared_set WHERE campaign.id = {CAMP}")]
acct = [r.customer_negative_criterion.negative_keyword_list.shared_set.split("/")[-1] for r in q(c,
        "SELECT customer_negative_criterion.type, customer_negative_criterion.negative_keyword_list.shared_set FROM customer_negative_criterion")
        if E(r.customer_negative_criterion.type) == "NEGATIVE_KEYWORD_LIST"]
members = {}
for sid in sorted(set(acct) | {a["set"] for a in att if a["status"] == "ENABLED"}):
    members[sid] = [dict(text=r.shared_criterion.keyword.text, match=E(r.shared_criterion.keyword.match_type))
                    for r in q(c, f"SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type, shared_criterion.type FROM shared_criterion WHERE shared_set.id = {sid}")
                    if E(r.shared_criterion.type) == "KEYWORD"]
out.update(attachments=att, account_level_sets=acct, shared_set_members=members)

# ---------------- change history ----------------
agids = set(ags)
ce = []
for r in q(c, f"""SELECT change_event.change_date_time, change_event.change_resource_type, change_event.change_resource_name, change_event.client_type,
        change_event.resource_change_operation, change_event.changed_fields, change_event.campaign FROM change_event
        WHERE change_event.change_date_time >= '2026-09-30 00:00:00' AND change_event.change_date_time <= '{TODAY} 23:59:59'
        ORDER BY change_event.change_date_time DESC LIMIT 5000"""):
    e = r.change_event
    rn = e.change_resource_name
    mine = CAMP in (e.campaign or "") or any(f"/{g}" in rn or f"/{g}~" in rn or f"{g}~" in rn for g in agids) or "/campaignBudgets/" in rn or "customers/2401959466/sharedCriteria" in rn
    ce.append(dict(at=e.change_date_time, type=E(e.change_resource_type), resource=rn, client=E(e.client_type), op=E(e.resource_change_operation),
                   fields=list(e.changed_fields.paths), campaign=e.campaign, in_scope=bool(mine)))
out["change_events"] = ce

# ---------------- performance ----------------
M = "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions"
mm = lambda x: dict(impr=x.impressions, clicks=x.clicks, cost=money(x.cost_micros), conv=round(x.conversions, 2), all_conv=round(x.all_conversions, 2))
ISM = ("metrics.search_impression_share, metrics.search_rank_lost_impression_share, metrics.search_budget_lost_impression_share, "
       "metrics.search_top_impression_share, metrics.search_absolute_top_impression_share")
ISM_AG = ("metrics.search_impression_share, metrics.search_rank_lost_impression_share, "
          "metrics.search_top_impression_share, metrics.search_absolute_top_impression_share")
isa = lambda x: dict(IS=x.search_impression_share, lost_rank=x.search_rank_lost_impression_share, top=x.search_top_impression_share,
                     abs_top=x.search_absolute_top_impression_share)
isd = lambda x: dict(IS=x.search_impression_share, lost_rank=x.search_rank_lost_impression_share, lost_budget=x.search_budget_lost_impression_share,
                     top=x.search_top_impression_share, abs_top=x.search_absolute_top_impression_share)
perf = collections.defaultdict(dict)
for r in q(c, f"SELECT segments.date, {M}, {ISM} FROM campaign WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{TODAY}'"):
    perf["campaign_daily"][r.segments.date] = {**mm(r.metrics), **isd(r.metrics)}
WINS = {"baseline_0924_0930": ("2026-09-24", "2026-09-30"), "baseline_0924_0929": ("2026-09-24", "2026-09-29"), "d0930": ("2026-09-30", "2026-09-30"),
        "test_complete_1001_1002": ("2026-10-01", "2026-10-02"), "d1001": ("2026-10-01", "2026-10-01"), "d1002": ("2026-10-02", "2026-10-02"),
        "today_partial": (TODAY, TODAY), "since_0917": (A, "2026-10-04")}
for w, (a, b) in WINS.items():
    rr = q(c, f"SELECT campaign.id, {M}, {ISM} FROM campaign WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{a}' AND '{b}'")
    perf["campaign_window"][w] = {**mm(rr[0].metrics), **isd(rr[0].metrics)} if rr else None
    perf["ad_group_window_is"][w] = {str(r.ad_group.id): {**mm(r.metrics), **isa(r.metrics)} for r in
                                      q(c, f"SELECT ad_group.id, {M}, {ISM_AG} FROM ad_group WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{a}' AND '{b}'")}
    perf["keyword_window_is"][w] = {f"{r.ad_group.id}~{r.ad_group_criterion.criterion_id}": {**mm(r.metrics), **isa(r.metrics)} for r in
                                     q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, {M}, {ISM_AG} FROM keyword_view WHERE campaign.id = {CAMP}
                                     AND segments.date BETWEEN '{a}' AND '{b}'""")}
for r in q(c, f"SELECT ad_group.id, segments.date, {M} FROM ad_group WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["ad_group_daily"][f"{r.ad_group.id}|{r.segments.date}"] = mm(r.metrics)
for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, segments.date, {M}
        FROM keyword_view WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0"""):
    perf["keyword_daily"][f"{r.ad_group.id}~{r.ad_group_criterion.criterion_id}|{r.segments.date}"] = dict(
        text=r.ad_group_criterion.keyword.text, match=E(r.ad_group_criterion.keyword.match_type), **mm(r.metrics))
for r in q(c, f"SELECT segments.date, segments.device, {M} FROM campaign WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["device_daily"][f"{r.segments.date}|{E(r.segments.device)}"] = mm(r.metrics)
for r in q(c, f"SELECT ad_group.id, segments.date, segments.click_type, {M} FROM ad_group WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["click_type_daily"][f"{r.ad_group.id}|{r.segments.date}|{E(r.segments.click_type)}"] = mm(r.metrics)
for r in q(c, f"SELECT segments.date, segments.hour, {M} FROM campaign WHERE campaign.id = {CAMP} AND segments.date BETWEEN '2026-09-24' AND '{TODAY}' AND metrics.impressions > 0"):
    perf["hourly"][f"{r.segments.date}|{r.segments.hour:02d}"] = mm(r.metrics)
for r in q(c, f"""SELECT segments.date, segments.conversion_action_name, metrics.conversions, metrics.all_conversions FROM campaign WHERE campaign.id = {CAMP}
        AND segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.all_conversions > 0"""):
    perf["conv_by_action_daily"][f"{r.segments.date}|{r.segments.conversion_action_name}"] = dict(conv=round(r.metrics.conversions, 2), all_conv=round(r.metrics.all_conversions, 2))
out["performance"] = dict(perf)

# ---------------- search terms (no threshold) ----------------
rows = []
for r in q(c, f"""SELECT ad_group.id, search_term_view.search_term, search_term_view.status, segments.date, segments.search_term_match_type,
        segments.keyword.ad_group_criterion, segments.keyword.info.text, segments.keyword.info.match_type, metrics.impressions, metrics.clicks,
        metrics.cost_micros, metrics.conversions, metrics.all_conversions FROM search_term_view WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{TODAY}'"""):
    rows.append(dict(ad_group=str(r.ad_group.id), term=r.search_term_view.search_term, status=E(r.search_term_view.status), date=r.segments.date,
                     st_match=E(r.segments.search_term_match_type),
                     kw_id=r.segments.keyword.ad_group_criterion.split("~")[-1] if r.segments.keyword.ad_group_criterion else "",
                     kw_text=r.segments.keyword.info.text, kw_match=E(r.segments.keyword.info.match_type), impr=r.metrics.impressions,
                     clicks=r.metrics.clicks, cost=money(r.metrics.cost_micros), conv=round(r.metrics.conversions, 2), all_conv=round(r.metrics.all_conversions, 2)))
ST = EXPORTS / "repair-search-terms-2026-10-05.jsonl"
ST.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
out["search_terms_file"] = str(ST.relative_to(CLIENT_DIR))

# ---------------- phone: call assets, location asset sets, call_view (all campaigns) ----------------
digits = lambda s: "".join(ch for ch in str(s or "") if ch.isdigit())[-10:]
out["call_asset_links"] = [dict(campaign=str(r.campaign.id), status=E(r.campaign_asset.status), asset=str(r.asset.id), number=digits(r.asset.call_asset.phone_number))
                           for r in q(c, """SELECT campaign.id, campaign.status, campaign_asset.status, asset.id, asset.call_asset.phone_number FROM campaign_asset
                               WHERE campaign_asset.field_type = 'CALL' AND campaign_asset.status != 'REMOVED' AND campaign.status = 'ENABLED'""")]
out["customer_call_assets"] = [dict(status=E(r.customer_asset.status), asset=str(r.asset.id), number=digits(r.asset.call_asset.phone_number))
                               for r in q(c, "SELECT customer_asset.status, asset.id, asset.call_asset.phone_number FROM customer_asset WHERE customer_asset.field_type = 'CALL'")]
out["customer_asset_sets"] = [dict(set=str(r.asset_set.id), name=r.asset_set.name, type=E(r.asset_set.type), status=E(r.customer_asset_set.status))
                              for r in q(c, "SELECT asset_set.id, asset_set.name, asset_set.type, customer_asset_set.status FROM customer_asset_set")]
out["campaign_asset_sets"] = [dict(set=str(r.asset_set.id), type=E(r.asset_set.type), status=E(r.campaign_asset_set.status))
                              for r in q(c, f"SELECT asset_set.id, asset_set.type, campaign_asset_set.status FROM campaign_asset_set WHERE campaign.id = {CAMP}")]
cv = []
for r in q(c, """SELECT call_view.start_call_date_time, call_view.end_call_date_time, call_view.call_duration_seconds, call_view.call_status, call_view.type,
        call_view.call_tracking_display_location, call_view.caller_area_code, campaign.id, ad_group.id FROM call_view
        WHERE call_view.start_call_date_time >= '2026-09-17 00:00:00'"""):
    v = r.call_view
    cv.append(dict(start=v.start_call_date_time, end=v.end_call_date_time, dur=v.call_duration_seconds, status=E(v.call_status), type=E(v.type),
                   display=E(v.call_tracking_display_location), campaign=str(r.campaign.id), ad_group=str(r.ad_group.id)))
out["call_view_since_0917"] = cv
(SNAP / "repair-read-2026-10-05.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")

# ---------------- compact print (aggregates only) ----------------
print(f"\naccount yesterday={out['account_yesterday']} now={NOW.isoformat(timespec='seconds')}")
print("config:", json.dumps({k: v for k, v in cfg.items()}, default=str))
print("ad groups:", {k: (v["name"], v["status"], v["primary"]) for k, v in ags.items()})
print("in-scope change_events:", [(e["at"], e["client"], e["type"], e["op"], e["resource"].split("/")[-1][:40], e["fields"][:6]) for e in ce if e["in_scope"]])
print("all change_events by (date, client, type):", dict(collections.Counter((e["at"][:10], e["client"], e["type"]) for e in ce)))
for w, v in perf["campaign_window"].items():
    print(f"  {w:26s} {v}")
print("search-term rows:", len(rows), "distinct:", len({x['term'] for x in rows}), "by date:", dict(sorted(collections.Counter(x["date"] for x in rows).items())))
print("call_view since 09-17:", [(v["start"], v["dur"], v["status"], v["type"], v["display"], v["campaign"], v["ad_group"]) for v in cv])
print("call asset links:", sorted((l["campaign"], l["number"], l["status"]) for l in out["call_asset_links"]))
print("customer call assets:", out["customer_call_assets"], "| customer asset sets:", out["customer_asset_sets"], "| campaign asset sets:", out["campaign_asset_sets"])
print("wrote snapshots/repair-read-2026-10-05.json and", ST.name)
