#!/usr/bin/env python3
"""STAGE 1 - fresh read-only identity and full state check. SELECT-only."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.google_ads import enum_name                     # noqa: E402

CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
TZ = ZoneInfo("America/New_York")
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "stage1-state-2026-08-26.json"

Q_ID = """
SELECT customer.id, customer.descriptive_name, customer.manager,
       customer.test_account, customer.currency_code, customer.time_zone
FROM customer LIMIT 1
"""

Q_CAMP = """
SELECT campaign.id, campaign.name, campaign.status,
       campaign.advertising_channel_type,
       campaign.bidding_strategy_type,
       campaign.maximize_conversions.target_cpa_micros,
       campaign.target_spend.cpc_bid_ceiling_micros,
       campaign.network_settings.target_search_network,
       campaign.network_settings.target_content_network,
       campaign.network_settings.target_partner_search_network,
       campaign.geo_target_type_setting.positive_geo_target_type,
       campaign.geo_target_type_setting.negative_geo_target_type,
       campaign_budget.id, campaign_budget.amount_micros,
       campaign_budget.explicitly_shared, campaign_budget.delivery_method
FROM campaign WHERE campaign.status != 'REMOVED'
"""

Q_MTD = """
SELECT campaign.id, metrics.cost_micros, metrics.impressions, metrics.clicks,
       metrics.average_cpc, metrics.conversions, metrics.all_conversions,
       metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share,
       metrics.search_impression_share
FROM campaign
WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'
  AND campaign.status != 'REMOVED'
"""

Q_TODAY = """
SELECT campaign.id, metrics.cost_micros, metrics.impressions, metrics.clicks,
       metrics.conversions
FROM campaign
WHERE segments.date = '2026-08-26' AND campaign.status != 'REMOVED'
"""

Q_LOC = """
SELECT campaign.id, campaign_criterion.criterion_id,
       campaign_criterion.negative, campaign_criterion.status,
       campaign_criterion.location.geo_target_constant
FROM campaign_criterion
WHERE campaign_criterion.type = 'LOCATION' AND campaign.status != 'REMOVED'
"""

Q_SCHED = """
SELECT campaign.id, campaign_criterion.criterion_id,
       campaign_criterion.ad_schedule.day_of_week,
       campaign_criterion.ad_schedule.start_hour,
       campaign_criterion.ad_schedule.end_hour,
       campaign_criterion.ad_schedule.start_minute,
       campaign_criterion.ad_schedule.end_minute
FROM campaign_criterion
WHERE campaign_criterion.type = 'AD_SCHEDULE' AND campaign.status != 'REMOVED'
"""


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    out = {"snapshot_account_local": now.isoformat(), "stage": 1}

    for row in svc.search(customer_id=CID, query=Q_ID):
        c = row.customer
        out["identity"] = {
            "id": str(c.id), "descriptive_name": c.descriptive_name,
            "manager": c.manager, "test_account": c.test_account,
            "currency": c.currency_code, "time_zone": c.time_zone}
    i = out["identity"]
    gate = {
        "name_matches": i["descriptive_name"] == NAME,
        "id_matches": i["id"] == CID,
        "manager_is_false": i["manager"] is False,
        "test_account_is_false": i["test_account"] is False,
        "currency_is_usd": i["currency"] == "USD",
        "timezone_is_america_new_york": i["time_zone"] == "America/New_York"}
    out["identity_gate"] = gate
    out["identity_gate_passed"] = all(gate.values())

    print("STAGE 1 - FRESH IDENTITY AND STATE")
    print("  account-local timestamp : %s" % now.isoformat())
    print("  account   : %s" % i["descriptive_name"])
    print("  id        : %s" % i["id"])
    print("  manager   : %s   test: %s" % (i["manager"], i["test_account"]))
    print("  currency  : %s   tz: %s" % (i["currency"], i["time_zone"]))
    for k, v in gate.items():
        print("     %-32s %s" % (k, "PASS" if v else "FAIL"))
    if not out["identity_gate_passed"]:
        print()
        print("IDENTITY MISMATCH - STOPPING")
        OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
        return 1

    camps = {}
    for row in svc.search(customer_id=CID, query=Q_CAMP):
        cp, b = row.campaign, row.campaign_budget
        camps[str(cp.id)] = {
            "name": cp.name, "status": enum_name(cp.status),
            "channel": enum_name(cp.advertising_channel_type),
            "bidding_strategy": enum_name(cp.bidding_strategy_type),
            "target_spend_cpc_ceiling_micros": (
                cp.target_spend.cpc_bid_ceiling_micros or None),
            "search_network": cp.network_settings.target_search_network,
            "content_network": cp.network_settings.target_content_network,
            "search_partners": cp.network_settings.target_partner_search_network,
            "positive_geo_target_type": enum_name(
                cp.geo_target_type_setting.positive_geo_target_type),
            "negative_geo_target_type": enum_name(
                cp.geo_target_type_setting.negative_geo_target_type),
            "budget_id": str(b.id), "budget_micros": b.amount_micros,
            "budget_usd": round(b.amount_micros / 1e6, 2),
            "budget_explicitly_shared": b.explicitly_shared,
            "budget_delivery": enum_name(b.delivery_method)}
    out["campaigns"] = camps

    for key, q in (("mtd", Q_MTD), ("today", Q_TODAY)):
        agg = {}
        for row in svc.search(customer_id=CID, query=q):
            m = row.metrics
            d = {"cost": round(m.cost_micros / 1e6, 2),
                 "impressions": m.impressions, "clicks": m.clicks,
                 "conversions": round(m.conversions, 2)}
            if key == "mtd":
                d.update({
                    "average_cpc": round(m.average_cpc / 1e6, 2),
                    "all_conversions": round(m.all_conversions, 2),
                    "search_impression_share": m.search_impression_share or None,
                    "search_lost_is_budget":
                        m.search_budget_lost_impression_share or None,
                    "search_lost_is_rank":
                        m.search_rank_lost_impression_share or None})
            agg[str(row.campaign.id)] = d
        out[key] = agg

    out["mtd_total_cost"] = round(sum(v["cost"] for v in out["mtd"].values()), 2)
    out["today_total_cost"] = round(sum(v["cost"] for v in out["today"].values()), 2)

    loc = {c: {"positive": [], "negative": []} for c in CAMPAIGNS}
    for row in svc.search(customer_id=CID, query=Q_LOC):
        cid = str(row.campaign.id)
        cc = row.campaign_criterion
        if cid not in loc:
            continue
        loc[cid]["negative" if cc.negative else "positive"].append({
            "criterion_id": str(cc.criterion_id),
            "geo_target_constant_id":
                cc.location.geo_target_constant.split("/")[-1],
            "status": enum_name(cc.status)})
    out["location_criteria"] = loc

    sched = {c: [] for c in CAMPAIGNS}
    for row in svc.search(customer_id=CID, query=Q_SCHED):
        cid = str(row.campaign.id)
        a = row.campaign_criterion.ad_schedule
        if cid in sched:
            sched[cid].append({"day": enum_name(a.day_of_week),
                               "start": "%02d:%02d" % (a.start_hour,
                                                       0 if a.start_minute == 0 else 30),
                               "end": "%02d:%02d" % (a.end_hour,
                                                     0 if a.end_minute == 0 else 30)})
    out["ad_schedules"] = sched

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print()
    print("CAMPAIGN STATE")
    for cid, cname in CAMPAIGNS.items():
        c = camps[cid]
        m = out["mtd"].get(cid, {})
        t = out["today"].get(cid, {})
        print("  %s  %s  [%s]" % (cid, c["name"], c["status"]))
        print("     budget        : $%.2f/day  (budget_id %s, shared=%s)"
              % (c["budget_usd"], c["budget_id"], c["budget_explicitly_shared"]))
        print("     bidding       : %s   cpc_ceiling=%s"
              % (c["bidding_strategy"], c["target_spend_cpc_ceiling_micros"]))
        print("     networks      : search=%s partners=%s display=%s"
              % (c["search_network"], c["search_partners"], c["content_network"]))
        print("     geo option    : positive=%s negative=%s"
              % (c["positive_geo_target_type"], c["negative_geo_target_type"]))
        print("     locations     : %d positive, %d negative"
              % (len(loc[cid]["positive"]), len(loc[cid]["negative"])))
        print("     ad schedules  : %d rows" % len(sched[cid]))
        print("     MTD           : cost $%.2f impr %s clicks %s cpc $%.2f conv %s"
              % (m.get("cost", 0), m.get("impressions"), m.get("clicks"),
                 m.get("average_cpc", 0), m.get("conversions")))
        print("     lost IS       : budget=%s rank=%s   IS=%s"
              % (m.get("search_lost_is_budget"), m.get("search_lost_is_rank"),
                 m.get("search_impression_share")))
        print("     Aug 26        : cost $%.2f impr %s clicks %s conv %s"
              % (t.get("cost", 0), t.get("impressions"), t.get("clicks"),
                 t.get("conversions")))
        print()
    print("  AUGUST MTD TOTAL : $%.2f" % out["mtd_total_cost"])
    print("  AUGUST 26 TOTAL  : $%.2f" % out["today_total_cost"])
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
