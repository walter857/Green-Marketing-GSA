#!/usr/bin/env python3
"""Ambient | 2026-09-17 | heating build: identity gate + fresh full snapshot. READ ONLY."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-17"
MONTHLY_CAP = 10000.0
MAX_DAILY = round(MONTHLY_CAP / 30.4, 2)
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
       "monthly_cap": MONTHLY_CAP, "max_combined_daily": MAX_DAILY,
       "external_writes": 0}
c = client()

print("=== 1. IDENTITY GATE ===")
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.currency_code,
       customer.time_zone, customer.manager, customer.test_account, customer.status,
       customer.auto_tagging_enabled, customer.tracking_url_template,
       customer.final_url_suffix,
       customer.conversion_tracking_setting.conversion_tracking_id,
       customer.conversion_tracking_setting.google_ads_conversion_customer,
       customer.conversion_tracking_setting.conversion_tracking_status
       FROM customer""")[0].customer
links = {x.customer_manager_link.manager_customer.split("/")[-1]:
         E(x.customer_manager_link.status)
         for x in q(c, """SELECT customer_manager_link.manager_customer,
                          customer_manager_link.status FROM customer_manager_link""")}
checks = {
    "name == 'Ambient Cooling - Live'": row.descriptive_name == EXACT_NAME,
    "id == 2401959466 (child, not MCC 3373711342)": str(row.id) == CID,
    "NOT manager": not row.manager, "NOT test": not row.test_account,
    "TZ America/New_York": row.time_zone == "America/New_York",
    "USD": row.currency_code == "USD", "ENABLED": E(row.status) == "ENABLED",
    "'- live' marker": "- live" in row.descriptive_name.casefold(),
    "GM 3373711342 ACTIVE": links.get(GM_MANAGER) == "ACTIVE",
    "ClickCease 2815082755 ACTIVE": links.get(CC_MANAGER) == "ACTIVE"}
for k, v in checks.items():
    print(f"  [{'PASS' if v else 'FAIL'}] {k}")
assert all(checks.values())
now = datetime.datetime.now(TZ)
out["identity"] = {"name": row.descriptive_name, "id": str(row.id), "checks": checks,
                   "auto_tagging": row.auto_tagging_enabled,
                   "customer_tracking_url_template": row.tracking_url_template or None,
                   "customer_final_url_suffix": row.final_url_suffix or None,
                   "conversion_tracking_id": row.conversion_tracking_setting.conversion_tracking_id,
                   "conv_owner": row.conversion_tracking_setting.google_ads_conversion_customer,
                   "conv_status": E(row.conversion_tracking_setting.conversion_tracking_status),
                   "manager_links": links}
print(f"\n  Ambient Cooling - Live | 2401959466 | Residential heating repair, "
      f"installation, replacement")
print(f"  auto_tagging={row.auto_tagging_enabled} "
      f"customer tracking_url_template={row.tracking_url_template or '(none)'} "
      f"final_url_suffix={row.final_url_suffix or '(none)'}")
print(f"  account local now = {now.isoformat()}  today PARTIAL={now.date()}")

print("\n=== 2. CHANGE HISTORY THROUGH NOW (explicit time bound, includes today) ===")
hi = now.strftime("%Y-%m-%d %H:%M:%S")
lo = (now - datetime.timedelta(days=29)).strftime("%Y-%m-%d 00:00:00")
ce = q(c, f"""SELECT change_event.change_date_time, change_event.change_resource_type,
              change_event.resource_change_operation, change_event.changed_fields,
              change_event.user_email, change_event.client_type,
              change_event.change_resource_name, change_event.campaign,
              change_event.old_resource, change_event.new_resource
              FROM change_event
              WHERE change_event.change_date_time >= '{lo}'
                AND change_event.change_date_time <= '{hi}'
              ORDER BY change_event.change_date_time DESC LIMIT 400""")
print(f"  window {lo} .. {hi}   rows={len(ce)}")
evs = []
for r in ce[:40]:
    e = r.change_event
    evs.append({"when": e.change_date_time, "type": E(e.change_resource_type),
                "op": E(e.resource_change_operation),
                "fields": list(e.changed_fields.paths) if e.changed_fields else [],
                "user": e.user_email, "client_type": E(e.client_type),
                "resource": e.change_resource_name})
for x in evs[:12]:
    print(f"  {x['when'][:19]} {x['type']:20s} {x['op']:7s} {','.join(x['fields'])[:44]:44s} "
          f"<{x['user']}> {x['client_type']}")
out["recent_change_events"] = evs
out["newest_change_event"] = evs[0]["when"] if evs else None

print("\n=== 3. SEPTEMBER MTD SPEND + SAFE REMAINING PACE ===")
mtd_rows = q(c, f"""SELECT campaign.id, campaign.name, metrics.cost_micros
                    FROM campaign WHERE segments.date BETWEEN '2026-09-01' AND '{now.date()}'""")
mtd_by = defaultdict(float)
for r in mtd_rows:
    mtd_by[(str(r.campaign.id), r.campaign.name)] += r.metrics.cost_micros / 1e6
mtd = sum(mtd_by.values())
days_in_sep = 30
day_of_month = now.day
days_left_incl_today = days_in_sep - day_of_month + 1
RESERVE_PCT = 0.10
remaining_raw = MONTHLY_CAP - mtd
remaining_after_reserve = remaining_raw - (MONTHLY_CAP * RESERVE_PCT)
safe_daily = remaining_after_reserve / days_left_incl_today
print(f"  September MTD spend (2026-09-01..{now.date()}): ${mtd:,.2f}")
for (cid, nm), v in sorted(mtd_by.items(), key=lambda x: -x[1]):
    if v > 0:
        print(f"    ${v:>9,.2f}  {cid}  {nm[:52]}")
print(f"  monthly cap                         : ${MONTHLY_CAP:,.2f}")
print(f"  remaining raw allowance             : ${remaining_raw:,.2f}")
print(f"  documented reserve ({int(RESERVE_PCT*100)}% of cap)    : "
      f"-${MONTHLY_CAP*RESERVE_PCT:,.2f}  (covers conversion lag, invalid-click "
      f"restatement and the partial-day tail)")
print(f"  remaining after reserve             : ${remaining_after_reserve:,.2f}")
print(f"  days left incl. today ({now.date()}) : {days_left_incl_today}")
print(f"  SAFE DAILY PACE for the rest of Sept: ${safe_daily:,.2f}/day")
print(f"  (cap-derived steady-state max daily : ${MAX_DAILY:,.2f}/day)")
out["september"] = {"mtd_spend": round(mtd, 2), "by_campaign":
                    {f"{k[0]} {k[1]}": round(v, 2) for k, v in mtd_by.items() if v > 0},
                    "monthly_cap": MONTHLY_CAP, "remaining_raw": round(remaining_raw, 2),
                    "reserve_pct": RESERVE_PCT,
                    "reserve_amount": round(MONTHLY_CAP * RESERVE_PCT, 2),
                    "remaining_after_reserve": round(remaining_after_reserve, 2),
                    "days_left_incl_today": days_left_incl_today,
                    "safe_daily_pace": round(safe_daily, 2),
                    "steady_state_max_daily": MAX_DAILY}

print("\n=== 4. ENABLED CAMPAIGNS + DAILY BUDGET TOTAL vs NEW $10,000 CAP ===")
camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                 campaign.advertising_channel_type, campaign.bidding_strategy_type,
                 campaign.target_spend.cpc_bid_ceiling_micros,
                 campaign.network_settings.target_search_network,
                 campaign.network_settings.target_content_network,
                 campaign.geo_target_type_setting.positive_geo_target_type,
                 campaign.tracking_url_template, campaign.final_url_suffix,
                 campaign_budget.id, campaign_budget.amount_micros,
                 campaign_budget.explicitly_shared FROM campaign"""):
    camps[str(r.campaign.id)] = {
        "name": r.campaign.name, "status": E(r.campaign.status),
        "channel": E(r.campaign.advertising_channel_type),
        "bidding": E(r.campaign.bidding_strategy_type),
        "ceiling": round(r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
        "search_partners": r.campaign.network_settings.target_search_network,
        "display": r.campaign.network_settings.target_content_network,
        "geo": E(r.campaign.geo_target_type_setting.positive_geo_target_type),
        "tracking_url_template": r.campaign.tracking_url_template or None,
        "final_url_suffix": r.campaign.final_url_suffix or None,
        "budget_id": str(r.campaign_budget.id),
        "budget": round(r.campaign_budget.amount_micros / 1e6, 2),
        "budget_shared": r.campaign_budget.explicitly_shared}
enabled = {k: v for k, v in camps.items() if v["status"] == "ENABLED"}
tot = sum(v["budget"] for v in enabled.values())
print(f"  ENABLED campaigns: {len(enabled)}")
for k, v in sorted(enabled.items(), key=lambda x: -x[1]["budget"]):
    print(f"    ${v['budget']:>7.2f}/d  ceil=${v['ceiling']:>5.2f}  {v['bidding']:13s} "
          f"shared={v['budget_shared']}  {k} {v['name'][:48]}")
print(f"  COMBINED ENABLED DAILY : ${tot:,.2f}")
print(f"  x30.4                  : ${tot*30.4:,.2f}")
print(f"  NEW CAP                : ${MONTHLY_CAP:,.2f}  (max daily ${MAX_DAILY})")
over = tot - MAX_DAILY
print(f"  >>> {'OVER' if over>0 else 'under'} the new daily cap by ${abs(over):,.2f}/day "
      f"= ${abs(over)*30.4:,.2f}/month")
out["budgets"] = {"all_campaigns": camps, "enabled_count": len(enabled),
                  "combined_enabled_daily": round(tot, 2),
                  "combined_enabled_monthly": round(tot * 30.4, 2),
                  "over_new_daily_cap_by": round(over, 2),
                  "over_new_monthly_cap_by": round(over * 30.4, 2),
                  "any_shared_budget": any(v["budget_shared"] for v in enabled.values())}

print("\n=== 5. HEATING CAMPAIGN INVENTORY (current + historical, all statuses) ===")
import re
HEAT = re.compile(r"heat|furnace|boiler|geotherm|mini.?split|thermostat|tankless|oil",
                  re.I)
heat = {k: v for k, v in camps.items() if HEAT.search(v["name"])}
perf = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0})
for r in q(c, f"""SELECT campaign.id, metrics.impressions, metrics.clicks,
                  metrics.cost_micros, metrics.conversions FROM campaign
                  WHERE campaign.id IN ({','.join(heat)})
                  AND segments.date BETWEEN '2019-01-01' AND '{now.date()}'"""):
    p = perf[str(r.campaign.id)]
    p["impr"] += r.metrics.impressions; p["clicks"] += r.metrics.clicks
    p["cost"] += r.metrics.cost_micros / 1e6; p["conv"] += r.metrics.conversions
print(f"  heating-relevant campaigns: {len(heat)}")
rows = []
for k, v in sorted(heat.items(), key=lambda x: -perf[x[0]]["cost"]):
    p = perf[k]
    cpc = p["cost"] / p["clicks"] if p["clicks"] else 0
    cpa = p["cost"] / p["conv"] if p["conv"] else None
    print(f"    {v['status']:8s} ${v['budget']:>7.2f}/d  ${p['cost']:>9,.2f} "
          f"clk={p['clicks']:>5} CPC=${cpc:>7.2f} conv={p['conv']:>5.1f} "
          f"CPA={('$%.2f' % cpa) if cpa else '-':>10s}  {v['name'][:44]}")
    rows.append({"campaign_id": k, **v, "impressions": p["impr"], "clicks": p["clicks"],
                 "cost": round(p["cost"], 2), "avg_cpc": round(cpc, 2),
                 "conversions": round(p["conv"], 2),
                 "cpa": round(cpa, 2) if cpa else None})
out["heating_campaigns"] = rows

print("\n=== 6. DOES ANYTHING FROM A PRIOR HEATING PLAN ALREADY EXIST? ===")
WANT_NAMES = ["Search | NonBrand | Heating Repair | Central MD | BOFU | 2026-09",
              "Search | NonBrand | Heating Installation | Central MD | BOFU | 2026-09",
              "Search | NonBrand | Oil Heating | Central MD | BOFU | 2026-09",
              "Search | NonBrand | Heating Services | Central MD | BOFU | 2026-10"]
exists = {n: [k for k, v in camps.items() if v["name"] == n] for n in WANT_NAMES}
for n, ids in exists.items():
    print(f"  {'EXISTS ' + str(ids) if ids else 'absent '}  {n}")
ag_want = ["SKAG | Furnace Repair", "SKAG | Heat Pump Installation",
           "SKAG | Mini Split Installation", "SKAG | Oil Furnace Installation",
           "SKAG | Oil System Replacement"]
ags = {}
for r in q(c, """SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
                 ad_group.status FROM ad_group"""):
    ags.setdefault(r.ad_group.name, []).append(
        {"ad_group_id": str(r.ad_group.id), "status": E(r.ad_group.status),
         "campaign_id": str(r.campaign.id), "campaign": r.campaign.name})
for n in ag_want:
    print(f"  {'EXISTS ' + json.dumps(ags[n]) if n in ags else 'absent '}  ad group {n}")
out["preexisting_check"] = {"campaigns": exists,
                            "ad_groups": {n: ags.get(n, []) for n in ag_want}}

print("\n=== 7. CONVERSION ACTIONS: PRIMARY / SECONDARY / DUPLICATES ===")
conv = []
for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                 conversion_action.status, conversion_action.type,
                 conversion_action.category, conversion_action.primary_for_goal,
                 conversion_action.counting_type, conversion_action.origin,
                 conversion_action.click_through_lookback_window_days,
                 conversion_action.attribution_model_settings.attribution_model
                 FROM conversion_action ORDER BY conversion_action.name"""):
    a = r.conversion_action
    conv.append({"id": str(a.id), "name": a.name, "status": E(a.status),
                 "type": E(a.type), "category": E(a.category),
                 "primary": a.primary_for_goal, "counting": E(a.counting_type),
                 "origin": E(a.origin), "ctw_days": a.click_through_lookback_window_days,
                 "attribution": E(a.attribution_model_settings.attribution_model)})
en_prim = [x for x in conv if x["status"] == "ENABLED" and x["primary"]]
print(f"  total conversion actions: {len(conv)}   ENABLED+PRIMARY: {len(en_prim)}")
for x in en_prim:
    print(f"    {x['id']:>12} {x['counting']:14s} {x['category']:22s} {x['type']:24s} {x['name'][:40]}")
dupes = defaultdict(list)
for x in en_prim:
    dupes[x["category"]].append(x["name"])
print("  duplicate Primary by category:")
for k, v in dupes.items():
    if len(v) > 1:
        print(f"    {k}: {len(v)} actions -> {v}")
out["conversion_actions"] = conv
out["enabled_primary"] = en_prim
out["duplicate_primary_by_category"] = {k: v for k, v in dupes.items() if len(v) > 1}

print("\n=== 8. GEO TARGETS + SCHEDULE FROM ACTIVE BOFU CAMPAIGNS (to reuse) ===")
geo = sorted({r.campaign_criterion.location.geo_target_constant.split("/")[-1]
              for r in q(c, f"""SELECT campaign.id,
                       campaign_criterion.location.geo_target_constant,
                       campaign_criterion.negative FROM campaign_criterion
                       WHERE campaign.id = 24132507747
                       AND campaign_criterion.type = LOCATION
                       AND campaign_criterion.negative = FALSE""")})
sched = [{"day": E(r.campaign_criterion.ad_schedule.day_of_week),
          "start": r.campaign_criterion.ad_schedule.start_hour,
          "end": r.campaign_criterion.ad_schedule.end_hour}
         for r in q(c, """SELECT campaign.id,
                   campaign_criterion.ad_schedule.day_of_week,
                   campaign_criterion.ad_schedule.start_hour,
                   campaign_criterion.ad_schedule.end_hour
                   FROM campaign_criterion WHERE campaign.id = 24132507747
                   AND campaign_criterion.type = AD_SCHEDULE""")]
print(f"  geo target constants on 24132507747: {len(geo)}")
print(f"  ad schedule rows: {len(sched)} -> {sched}")
out["reusable_geo_target_ids"] = geo
out["reusable_schedule"] = sched

p = SNAP / f"heating-build-snapshot-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("EXTERNAL WRITES: 0")
