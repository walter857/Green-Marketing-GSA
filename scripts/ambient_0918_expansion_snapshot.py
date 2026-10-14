#!/usr/bin/env python3
"""Ambient | 2026-09-18 | Steps 1-3: identity gate, fresh snapshot, receipt reconciliation.

READ-ONLY. Zero mutations.
"""
from __future__ import annotations
import sys, json, datetime, calendar
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-20"
LIVE = ROOT / "receipts" / "live"
CAP_MONTH = 10000.00
CAP_DAY = 328.94
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
       "read_only": True, "external_writes": 0}

c = client()
# ---------------------------------------------------------------- 1. identity
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
              customer.test_account, customer.status, customer.time_zone,
              customer.currency_code, customer.auto_tagging_enabled
              FROM customer""")[0].customer
gate = {"observed_name": row.descriptive_name, "observed_id": str(row.id),
        "name_exact_match": row.descriptive_name == EXACT_NAME,
        "id_exact_match": str(row.id) == CID,
        "live_marker": "- live" in row.descriptive_name.lower(),
        "is_manager": row.manager, "is_test": row.test_account,
        "status": E(row.status), "time_zone": row.time_zone,
        "tz_expected": row.time_zone == "America/New_York",
        "currency": row.currency_code, "auto_tagging": row.auto_tagging_enabled}
# manager_customer_id is not a selectable field; it is encoded in the resource name
# customers/{cid}/customerManagerLinks/{manager_cid}~{link_id}
mgr = [r.customer_manager_link.resource_name.rsplit("/", 1)[1].split("~")[0]
       for r in q(c, """SELECT customer_manager_link.resource_name,
                        customer_manager_link.status FROM customer_manager_link
                        WHERE customer_manager_link.status = 'ACTIVE'""")]
gate["active_manager_links"] = mgr
gate["expected_manager_present"] = GM_MANAGER in mgr
gate["manager_never_used_as_client"] = str(row.id) != GM_MANAGER
gate["PASS"] = all([gate["name_exact_match"], gate["id_exact_match"], gate["live_marker"],
                    not gate["is_manager"], not gate["is_test"], gate["tz_expected"],
                    gate["expected_manager_present"], gate["manager_never_used_as_client"]])
out["identity_gate"] = gate
print(f"=== 1. IDENTITY GATE: {'PASS' if gate['PASS'] else 'FAIL'} ===")
for k in ("observed_name", "observed_id", "live_marker", "is_manager", "is_test",
          "time_zone", "currency", "expected_manager_present"):
    print(f"   {k:28s} {gate[k]}")
assert gate["PASS"], "IDENTITY GATE FAILED"

# ------------------------------------------------------------- 2. work orders
wos = sorted((ROOT / "clients" / "ambient-cooling-heating").rglob("work-order*.y*ml"))
out["work_orders_present"] = [str(p.relative_to(ROOT)) for p in wos]
print(f"\n=== 2. WORK ORDERS ({len(wos)}) ===")
for p in wos:
    print(f"   {p.relative_to(ROOT)}")

# ---------------------------------------------------------------- 3. snapshot
print("\n=== 3. FRESH ACCOUNT SNAPSHOT ===")
camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                 campaign.advertising_channel_type, campaign.bidding_strategy_type,
                 campaign.target_spend.cpc_bid_ceiling_micros,
                 campaign_budget.id, campaign_budget.amount_micros,
                 campaign_budget.explicitly_shared,
                 campaign.network_settings.target_search_network,
                 campaign.network_settings.target_content_network,
                 campaign.geo_target_type_setting.positive_geo_target_type,
                 campaign.primary_status
                 FROM campaign WHERE campaign.status != 'REMOVED'"""):
    x = r.campaign
    camps[str(x.id)] = {
        "name": x.name, "status": E(x.status), "channel": E(x.advertising_channel_type),
        "bidding": E(x.bidding_strategy_type),
        "ceiling": x.target_spend.cpc_bid_ceiling_micros / 1e6,
        "budget_id": str(r.campaign_budget.id),
        "daily": r.campaign_budget.amount_micros / 1e6,
        "shared": r.campaign_budget.explicitly_shared,
        "search_partners": x.network_settings.target_search_network,
        "display": x.network_settings.target_content_network,
        "geo": E(x.geo_target_type_setting.positive_geo_target_type),
        "primary_status": E(x.primary_status)}
out["campaigns"] = camps
en = {k: v for k, v in camps.items() if v["status"] == "ENABLED"}
pa = {k: v for k, v in camps.items() if v["status"] == "PAUSED"}
en_daily = round(sum(v["daily"] for v in en.values()), 2)
print(f"   campaigns: {len(camps)} non-removed  ({len(en)} ENABLED, {len(pa)} PAUSED)")
print(f"   ENABLED daily total: ${en_daily:.2f}")
for k, v in sorted(en.items(), key=lambda x: -x[1]["daily"]):
    print(f"      {k}  ${v['daily']:7.2f}  ceil ${v['ceiling']:6.2f}  {v['name'][:52]}")
out["enabled_daily_total"] = en_daily

ags = {}
for r in q(c, """SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
                 ad_group.status, ad_group.cpc_bid_micros, ad_group.type
                 FROM ad_group WHERE ad_group.status != 'REMOVED'"""):
    ags[str(r.ad_group.id)] = {"name": r.ad_group.name, "status": E(r.ad_group.status),
                               "campaign_id": str(r.campaign.id),
                               "campaign": r.campaign.name,
                               "cpc_bid": r.ad_group.cpc_bid_micros / 1e6}
out["ad_groups"] = ags
print(f"   ad groups: {len(ags)} non-removed")

# ------------------------------------------------- September MTD + pace maths
now = datetime.datetime.now(TZ)
first = now.replace(day=1).strftime("%Y-%m-%d")
today = now.strftime("%Y-%m-%d")
mtd = 0.0
by_c = {}
for r in q(c, f"""SELECT campaign.id, campaign.name, metrics.cost_micros
                  FROM campaign WHERE segments.date BETWEEN '{first}' AND '{today}'"""):
    v = r.metrics.cost_micros / 1e6
    mtd += v
    by_c[r.campaign.name] = by_c.get(r.campaign.name, 0) + v
days_in_month = calendar.monthrange(now.year, now.month)[1]
days_left_incl_today = days_in_month - now.day + 1
remaining = round(CAP_MONTH - mtd, 2)
RESERVE_PCT = 0.10
reserve = round(remaining * RESERVE_PCT, 2)
safe_pace = round((remaining - reserve) / days_left_incl_today, 2)
out["september"] = {
    "window": f"{first}..{today}", "mtd_spend": round(mtd, 2),
    "monthly_cap": CAP_MONTH, "remaining_raw": remaining,
    "reserve_pct": RESERVE_PCT, "reserve_amount": reserve,
    "remaining_after_reserve": round(remaining - reserve, 2),
    "days_in_month": days_in_month, "days_left_incl_today": days_left_incl_today,
    "max_safe_september_daily_pace": safe_pace,
    "steady_state_monthly_ceiling_daily": CAP_DAY,
    "by_campaign": {k: round(v, 2) for k, v in sorted(by_c.items(), key=lambda x: -x[1])}}
print(f"\n   September MTD spend      ${mtd:,.2f}  ({first}..{today})")
print(f"   remaining allowance      ${remaining:,.2f}")
print(f"   reserve @ {RESERVE_PCT:.0%}            ${reserve:,.2f}   (conversion lag + overdelivery)")
print(f"   days left incl. today    {days_left_incl_today}")
print(f"   MAX SAFE Sept daily pace ${safe_pace:,.2f}")
print(f"   steady-state ceiling     ${CAP_DAY}/day  (= ${CAP_MONTH:,.0f}/30.4)")

# ---------------------------------------------- 4. reconcile prior receipts
print("\n=== 4. RECONCILE PRIOR EXECUTIONS ===")
rec = {}
for name, fp, ops in [("AMB-0917-HEAT-CREATE-1", "7DE31D6B6A88", 23),
                      ("AMB-0918-BUDGET-1", "39097845F5F4", 5),
                      ("AMB-0918-CONV-1", "A3370F96FA6E", 2)]:
    f = PLANS / f"{name}.json"
    plan = json.loads(f.read_text(encoding="utf-8"))
    d = plan.pop("fingerprint"); re_fp = approval_code(plan); plan["fingerprint"] = d
    receipts = [p.name for p in LIVE.glob(f"{name}-*.json") if "ABORT" not in p.name]
    rec[name] = {"fingerprint_on_disk": d, "recomputed": re_fp,
                 "matches_approved": d == re_fp == fp,
                 "operation_count": plan["operation_count"], "expected_ops": ops,
                 "receipts": receipts, "executed": bool(receipts)}
    print(f"   {name}: fp={d} match={d == re_fp == fp} ops={plan['operation_count']} "
          f"receipts={len(receipts)} -> {'ALREADY EXECUTED' if receipts else 'NOT EXECUTED'}")

live_checks = {
    "campaign_24257819463": camps.get("24257819463", {}).get("status"),
    "campaign_24257819466": camps.get("24257819466", {}).get("status"),
    "ad_group_199797580706": ags.get("199797580706", {}).get("status"),
    "ad_group_199797580746": ags.get("199797580746", {}).get("status"),
}
kw_n = len(q(c, """SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                   WHERE ad_group.id IN ('199797580706','199797580746')
                   AND ad_group_criterion.type = 'KEYWORD'
                   AND ad_group_criterion.status != 'REMOVED'"""))
rsa_n = len(q(c, """SELECT ad_group_ad.ad.id FROM ad_group_ad
                    WHERE ad_group.id IN ('199797580706','199797580746')
                    AND ad_group_ad.status != 'REMOVED'"""))
live_checks["keywords_on_the_two_ad_groups"] = kw_n
live_checks["rsas_on_the_two_ad_groups"] = rsa_n
live_checks["enabled_daily_total"] = en_daily
bidp = len(q(c, """SELECT conversion_action.id FROM conversion_action
                   WHERE conversion_action.status != 'REMOVED'
                   AND conversion_action.primary_for_goal = TRUE
                   AND conversion_action.origin != 'GOOGLE_HOSTED'"""))
live_checks["non_gbp_primary_conversion_actions"] = bidp
out["prior_executions"] = rec
out["live_state_checks"] = live_checks
print("   live state:")
for k, v in live_checks.items():
    print(f"      {k:34s} {v}")

SNAP.mkdir(parents=True, exist_ok=True)
p = SNAP / f"expansion-snapshot-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("EXTERNAL WRITES: 0")
