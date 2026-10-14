#!/usr/bin/env python3
"""Ambient | 2026-09-16 | heating research: identity gate + baseline reverification.

READ ONLY. No mutate, no validate_only, no external write of any kind.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-16"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
       "mode": "READ + DRAFT", "external_writes": 0}
c = client()

print("=== 1. FRESH IDENTITY GATE ===")
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.currency_code,
                     customer.time_zone, customer.manager, customer.test_account,
                     customer.status, customer.auto_tagging_enabled,
                     customer.conversion_tracking_setting.conversion_tracking_id
              FROM customer""")[0].customer
links = {x.customer_manager_link.manager_customer.split("/")[-1]:
         E(x.customer_manager_link.status)
         for x in q(c, """SELECT customer_manager_link.manager_customer,
                                 customer_manager_link.status FROM customer_manager_link""")}
checks = {
    "descriptive_name == 'Ambient Cooling - Live'": row.descriptive_name == EXACT_NAME,
    "customer.id == 2401959466 (child, NOT the MCC)": str(row.id) == CID,
    "is NOT a manager account": not row.manager,
    "is NOT a test account": not row.test_account,
    "time_zone == America/New_York": row.time_zone == "America/New_York",
    "currency == USD": row.currency_code == "USD",
    "status ENABLED": E(row.status) == "ENABLED",
    "'- live' marker present": "- live" in row.descriptive_name.casefold(),
    "GM manager 3373711342 ACTIVE": links.get(GM_MANAGER) == "ACTIVE",
    "ClickCease 2815082755 ACTIVE": links.get(CC_MANAGER) == "ACTIVE",
}
for k, v in checks.items():
    print(f"  [{'PASS' if v else 'FAIL'}] {k}")
assert all(checks.values()), "IDENTITY GATE FAILED"
out["identity"] = {"observed_name": row.descriptive_name, "observed_id": str(row.id),
                   "time_zone": row.time_zone, "currency": row.currency_code,
                   "manager_links": links, "checks": checks, "all_pass": True}
now = datetime.datetime.now(TZ)
out["account_local_now"] = now.isoformat()
out["today_partial"] = str(now.date())
out["last_settled"] = str(now.date() - datetime.timedelta(days=1))
print(f"\n  Ambient Cooling - Live | 2401959466 | heating-service portfolio research")
print(f"  account local now = {now.isoformat()}")
print(f"  today (PARTIAL) = {now.date()}   latest fully settled = "
      f"{now.date() - datetime.timedelta(days=1)}")

print("\n=== 2. EVERY CAMPAIGN IN THE ACCOUNT, ALL STATUSES ===")
camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                        campaign.advertising_channel_type,
                        campaign.advertising_channel_sub_type,
                        campaign.bidding_strategy_type,
                        campaign.target_spend.cpc_bid_ceiling_micros,
                        campaign.start_date_time, campaign.end_date_time,
                        campaign_budget.amount_micros, campaign_budget.id
                 FROM campaign ORDER BY campaign.name"""):
    cm = r.campaign
    camps[str(cm.id)] = {
        "name": cm.name, "status": E(cm.status), "channel": E(cm.advertising_channel_type),
        "sub_type": E(cm.advertising_channel_sub_type),
        "bidding": E(cm.bidding_strategy_type),
        "cpc_ceiling_usd": round(cm.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
        "budget_usd": round(r.campaign_budget.amount_micros / 1e6, 2),
        "budget_id": str(r.campaign_budget.id),
        "start": cm.start_date_time or None, "end": cm.end_date_time or None}
out["all_campaigns"] = camps
by_status = defaultdict(list)
for cid, v in camps.items():
    by_status[v["status"]].append((cid, v))
print(f"  total campaigns: {len(camps)}")
for st in sorted(by_status):
    print(f"\n  --- {st} ({len(by_status[st])}) ---")
    for cid, v in sorted(by_status[st], key=lambda x: x[1]["name"]):
        mark = " <-- FIVE BOFU" if cid in FIVE else ""
        print(f"    {cid} {v['channel']:16s} ${v['budget_usd']:>7.2f}/d "
              f"ceil=${v['cpc_ceiling_usd']:>5.2f} {v['name'][:52]}{mark}")

print("\n=== 3. BUDGET HEADROOM AGAINST $13,000 ===")
enabled_search = {cid: v for cid, v in camps.items()
                  if v["status"] == "ENABLED" and v["channel"] == "SEARCH"}
five_daily = sum(camps[c_]["budget_usd"] for c_ in FIVE)
all_enabled_search_daily = sum(v["budget_usd"] for v in enabled_search.values())
print(f"  FIVE BOFU combined daily        : ${five_daily:,.2f}")
print(f"  x30.4                           : ${five_daily*30.4:,.2f}")
print(f"  $13,000 / 30.4 = max daily      : ${13000/30.4:,.2f}")
print(f"  headroom vs $13,000 (monthly)   : ${13000 - five_daily*30.4:,.2f}")
print(f"  headroom vs max daily           : ${13000/30.4 - five_daily:,.2f}/day")
print(f"\n  ALL ENABLED SEARCH campaigns    : {len(enabled_search)}")
for cid, v in sorted(enabled_search.items(), key=lambda x: -x[1]["budget_usd"]):
    mark = " <-- FIVE BOFU" if cid in FIVE else ""
    print(f"    ${v['budget_usd']:>7.2f}/d  {v['name'][:56]}{mark}")
print(f"  combined ENABLED Search daily   : ${all_enabled_search_daily:,.2f}"
      f"  (x30.4 = ${all_enabled_search_daily*30.4:,.2f})")
out["budget"] = {
    "five_bofu_daily": round(five_daily, 2),
    "five_bofu_monthly_30_4": round(five_daily * 30.4, 2),
    "monthly_cap": 13000.0,
    "max_combined_daily": round(13000 / 30.4, 2),
    "headroom_monthly": round(13000 - five_daily * 30.4, 2),
    "headroom_daily": round(13000 / 30.4 - five_daily, 2),
    "all_enabled_search_count": len(enabled_search),
    "all_enabled_search_daily": round(all_enabled_search_daily, 2),
    "all_enabled_search_monthly": round(all_enabled_search_daily * 30.4, 2)}

print("\n=== 4. GAS BOILER REPAIR CAMPAIGN AUDIT (do not duplicate) ===")
gb = "24132507744"
gbc = camps[gb]
print(f"  {gb} {gbc['name']}")
print(f"  status={gbc['status']} budget=${gbc['budget_usd']}/d ceiling=${gbc['cpc_ceiling_usd']} "
      f"bidding={gbc['bidding']}")
gb_ags = [{"id": str(r.ad_group.id), "name": r.ad_group.name,
           "status": E(r.ad_group.status)}
          for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group.status
                            FROM ad_group WHERE campaign.id = {gb}""")]
gb_kws = [{"text": r.ad_group_criterion.keyword.text,
           "match": E(r.ad_group_criterion.keyword.match_type),
           "status": E(r.ad_group_criterion.status),
           "approval": E(r.ad_group_criterion.approval_status),
           "qs": r.ad_group_criterion.quality_info.quality_score or None}
          for r in q(c, f"""SELECT ad_group_criterion.keyword.text,
                                   ad_group_criterion.keyword.match_type,
                                   ad_group_criterion.status,
                                   ad_group_criterion.approval_status,
                                   ad_group_criterion.quality_info.quality_score
                            FROM ad_group_criterion WHERE campaign.id = {gb}
                              AND ad_group_criterion.type = KEYWORD
                              AND ad_group_criterion.negative = FALSE""")]
gb_ads = [{"ad_id": str(r.ad_group_ad.ad.id), "status": E(r.ad_group_ad.status),
           "approval": E(r.ad_group_ad.policy_summary.approval_status),
           "final_urls": list(r.ad_group_ad.ad.final_urls)}
          for r in q(c, f"""SELECT ad_group_ad.ad.id, ad_group_ad.status,
                                   ad_group_ad.policy_summary.approval_status,
                                   ad_group_ad.ad.final_urls
                            FROM ad_group_ad WHERE campaign.id = {gb}""")]
gb_negs = len(q(c, f"""SELECT campaign_criterion.criterion_id FROM campaign_criterion
                       WHERE campaign.id = {gb} AND campaign_criterion.negative = TRUE
                         AND campaign_criterion.type = KEYWORD"""))
print(f"  ad groups: {gb_ags}")
print(f"  keywords : {gb_kws}")
print(f"  ads      : {gb_ads}")
print(f"  campaign negatives: {gb_negs}")
m = q(c, f"""SELECT campaign.id, metrics.impressions, metrics.clicks,
                    metrics.cost_micros, metrics.conversions
             FROM campaign WHERE campaign.id = {gb}
               AND segments.date BETWEEN '2019-01-01' AND '{out['last_settled']}'""")
print(f"  ALL-TIME: impr={sum(x.metrics.impressions for x in m)} "
      f"clicks={sum(x.metrics.clicks for x in m)} "
      f"cost=${sum(x.metrics.cost_micros for x in m)/1e6:,.2f} "
      f"conv={sum(x.metrics.conversions for x in m):.1f}")
out["gas_boiler_audit"] = {"campaign": gbc, "ad_groups": gb_ags, "keywords": gb_kws,
                           "ads": gb_ads, "campaign_negatives": gb_negs,
                           "all_time": {"impressions": sum(x.metrics.impressions for x in m),
                                        "clicks": sum(x.metrics.clicks for x in m),
                                        "cost": round(sum(x.metrics.cost_micros for x in m)/1e6, 2),
                                        "conversions": sum(x.metrics.conversions for x in m)}}

print("\n=== 5. REVERIFY AUGUST BASELINE ===")
aug = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0})
for r in q(c, """SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks,
                        metrics.cost_micros, metrics.conversions FROM campaign
                 WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-31'"""):
    k = str(r.campaign.id)
    aug[k]["impr"] += r.metrics.impressions; aug[k]["clicks"] += r.metrics.clicks
    aug[k]["cost"] += r.metrics.cost_micros / 1e6; aug[k]["conv"] += r.metrics.conversions
aug_five = sum(aug[c_]["cost"] for c_ in FIVE)
aug_all = sum(v["cost"] for v in aug.values())
print(f"  August FIVE BOFU spend  : ${aug_five:,.2f}  (claim $6,842.80 -> "
      f"{'MATCH' if abs(aug_five-6842.80) < 0.01 else 'MISMATCH'})")
print(f"  August WHOLE ACCOUNT    : ${aug_all:,.2f}")
print(f"  other paid campaigns    : ${aug_all-aug_five:,.2f}  (claim $0.00 -> "
      f"{'MATCH' if abs(aug_all-aug_five) < 0.01 else 'MISMATCH'})")
for c_ in FIVE:
    print(f"    {NAME[c_]:20s} ${aug[c_]['cost']:>9,.2f}")
out["august_reverified"] = {
    "five_spend": round(aug_five, 2), "whole_account": round(aug_all, 2),
    "other_paid": round(aug_all - aug_five, 2),
    "per_campaign": {NAME[c_]: round(aug[c_]["cost"], 2) for c_ in FIVE},
    "claim_6842_80_matches": abs(aug_five - 6842.80) < 0.01,
    "claim_other_paid_zero_matches": abs(aug_all - aug_five) < 0.01}

print("\n=== 6. REVERIFY SEPTEMBER DECLINE ===")
for lo, hi, lbl in (("2026-09-01", "2026-09-04", "Sep 1-4 pre-cap"),
                    ("2026-09-05", "2026-09-15", "Sep 5-15 post-cap"),
                    ("2026-09-01", "2026-09-15", "Sep 1-15 settled")):
    s = i = cl = 0.0
    for r in q(c, f"""SELECT campaign.id, metrics.cost_micros, metrics.impressions,
                             metrics.clicks FROM campaign WHERE campaign.id IN ({IN5})
                      AND segments.date BETWEEN '{lo}' AND '{hi}'"""):
        s += r.metrics.cost_micros / 1e6; i += r.metrics.impressions; cl += r.metrics.clicks
    days = (datetime.date.fromisoformat(hi) - datetime.date.fromisoformat(lo)).days + 1
    print(f"  {lbl:20s} ${s:>9,.2f} over {days:>2}d = ${s/days:>7,.2f}/day  "
          f"impr={int(i):>5} clicks={int(cl):>3}")
    out.setdefault("september", {})[lbl] = {"spend": round(s, 2), "days": days,
                                            "per_day": round(s / days, 2),
                                            "impressions": int(i), "clicks": int(cl)}

Path(SNAP).mkdir(parents=True, exist_ok=True)
p = SNAP / f"heating-identity-baseline-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("EXTERNAL WRITES: 0")
