#!/usr/bin/env python3
"""AUGUST 28 fresh read-only snapshot for Softwind Power Washing (1521725229).

Stages 2-3 of the August 28 delivery-and-budget-recovery instruction:
  Stage 2  fresh identity check
  Stage 3  verify the deployed rescue state (campaigns, budgets, bidding, geo, schedule)

READ ONLY. Issues SELECT queries only. Performs no mutation of any kind.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
EXPECT_NAME = "Softwind Power Washing - Live"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
OUT = ROOT / "clients/softwind-power-washing/snapshots/snapshot-2026-08-28.json"

MIN_MAP = {"ZERO": "00", "FIFTEEN": "15", "THIRTY": "30", "FORTY_FIVE": "45"}
DAY_ORDER = {d: i for i, d in enumerate(
    ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"])}


def rows(svc, query):
    out = []
    for batch in svc.search_stream(customer_id=CID, query=query):
        for r in batch.results:
            out.append(r)
    return out


def money(micros):
    return None if not micros else round(micros / 1_000_000, 2)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")

    snap = {"read_only": True, "mutations_issued": 0}
    now = datetime.now(TZ)
    snap["snapshot_account_local"] = now.isoformat()
    snap["snapshot_date"] = now.strftime("%Y-%m-%d")

    # ---------------- Stage 2: identity ----------------
    q = ("SELECT customer.id, customer.descriptive_name, customer.manager, "
         "customer.test_account, customer.currency_code, customer.time_zone, "
         "customer.status, customer.auto_tagging_enabled, "
         "customer.conversion_tracking_setting.conversion_tracking_id, "
         "customer.conversion_tracking_setting.conversion_tracking_status, "
         "customer.pay_per_conversion_eligibility_failure_reasons "
         "FROM customer LIMIT 1")
    c = rows(svc, q)[0].customer
    ident = {
        "id": str(c.id),
        "descriptive_name": c.descriptive_name,
        "manager": c.manager,
        "test_account": c.test_account,
        "currency_code": c.currency_code,
        "time_zone": c.time_zone,
        "status": c.status.name,
        "auto_tagging_enabled": c.auto_tagging_enabled,
        "conversion_tracking_id": str(
            c.conversion_tracking_setting.conversion_tracking_id),
        "conversion_tracking_status":
            c.conversion_tracking_setting.conversion_tracking_status.name,
        "pay_per_conversion_eligibility_failure_reasons":
            [r.name for r in c.pay_per_conversion_eligibility_failure_reasons],
    }
    ident["matches_expected"] = {
        "name": c.descriptive_name == EXPECT_NAME,
        "id": str(c.id) == CID,
        "manager_false": c.manager is False,
        "test_false": c.test_account is False,
        "currency_usd": c.currency_code == "USD",
        "tz_ny": c.time_zone == "America/New_York",
    }
    ident["identity_gate_passed"] = all(ident["matches_expected"].values())
    snap["identity"] = ident
    if not ident["identity_gate_passed"]:
        snap["ABORT"] = "IDENTITY MISMATCH"
        OUT.write_text(json.dumps(snap, indent=2), encoding="utf-8")
        print(json.dumps(snap["identity"], indent=2))
        return 2

    # ---------------- Stage 3: deployed campaign state ----------------
    q = ("SELECT campaign.id, campaign.name, campaign.status, "
         "campaign.serving_status, campaign.primary_status, "
         "campaign.primary_status_reasons, campaign.advertising_channel_type, "
         "campaign.advertising_channel_sub_type, "
         "campaign.bidding_strategy_type, campaign.bidding_strategy_system_status, "
         "campaign.target_spend.cpc_bid_ceiling_micros, "
         "campaign.network_settings.target_google_search, "
         "campaign.network_settings.target_search_network, "
         "campaign.network_settings.target_content_network, "
         "campaign.network_settings.target_partner_search_network, "
         "campaign.geo_target_type_setting.positive_geo_target_type, "
         "campaign.geo_target_type_setting.negative_geo_target_type, "
         "campaign.start_date_time, campaign.end_date_time, "
         "campaign.campaign_budget, campaign.optimization_score, "

         "campaign.payment_mode, campaign.experiment_type "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    camps = {}
    budget_res = {}
    for r in rows(svc, q):
        cp = r.campaign
        camps[str(cp.id)] = {
            "id": str(cp.id), "name": cp.name, "status": cp.status.name,
            "serving_status": cp.serving_status.name,
            "primary_status": cp.primary_status.name,
            "primary_status_reasons": [x.name for x in cp.primary_status_reasons],
            "channel": cp.advertising_channel_type.name,
            "sub_type": cp.advertising_channel_sub_type.name,
            "bidding_strategy_type": cp.bidding_strategy_type.name,
            "bidding_strategy_system_status": cp.bidding_strategy_system_status.name,
            "target_spend_cpc_ceiling_micros":
                cp.target_spend.cpc_bid_ceiling_micros or None,
            "target_spend_cpc_ceiling_usd":
                money(cp.target_spend.cpc_bid_ceiling_micros),
            "network_google_search": cp.network_settings.target_google_search,
            "network_search_partners": cp.network_settings.target_search_network,
            "network_display": cp.network_settings.target_content_network,
            "network_partner_search": cp.network_settings.target_partner_search_network,
            "positive_geo": cp.geo_target_type_setting.positive_geo_target_type.name,
            "negative_geo": cp.geo_target_type_setting.negative_geo_target_type.name,
            "start_date_time": cp.start_date_time,
            "end_date_time": cp.end_date_time or None,
            "campaign_budget_resource": cp.campaign_budget,

            "payment_mode": cp.payment_mode.name,
            "experiment_type": cp.experiment_type.name,
        }
        budget_res[str(cp.id)] = cp.campaign_budget
    snap["campaigns"] = camps

    # budgets (all non-removed, so a shared budget elsewhere is visible)
    q = ("SELECT campaign_budget.id, campaign_budget.name, "
         "campaign_budget.amount_micros, campaign_budget.total_amount_micros, "
         "campaign_budget.delivery_method, campaign_budget.explicitly_shared, "
         "campaign_budget.reference_count, campaign_budget.status, "
         "campaign_budget.period, campaign_budget.type, "
         "campaign_budget.has_recommended_budget, "
         "campaign_budget.recommended_budget_amount_micros "
         "FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'")
    buds = {}
    for r in rows(svc, q):
        b = r.campaign_budget
        buds[str(b.id)] = {
            "id": str(b.id), "name": b.name,
            "amount_micros": b.amount_micros,
            "amount_usd": money(b.amount_micros),
            "total_amount_micros": b.total_amount_micros or None,
            "delivery_method": b.delivery_method.name,
            "explicitly_shared": b.explicitly_shared,
            "reference_count": b.reference_count,
            "status": b.status.name,
            "period": b.period.name,
            "type": b.type_.name,
            "has_recommended_budget": b.has_recommended_budget,
            "recommended_budget_usd": money(b.recommended_budget_amount_micros),
        }
    snap["campaign_budgets"] = buds
    for cid_, res in budget_res.items():
        bid = res.rsplit("/", 1)[-1]
        camps[cid_]["budget_id"] = bid
        camps[cid_]["budget"] = buds.get(bid)

    # locations
    q = ("SELECT campaign.id, campaign_criterion.criterion_id, "
         "campaign_criterion.negative, campaign_criterion.status, "
         "campaign_criterion.location.geo_target_constant "
         f"FROM campaign_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND campaign_criterion.type = 'LOCATION' "
         "AND campaign_criterion.status != 'REMOVED'")
    locs = {CAMP_A: {"positive": [], "negative": []},
            CAMP_B: {"positive": [], "negative": []}}
    for r in rows(svc, q):
        cc = r.campaign_criterion
        gid = cc.location.geo_target_constant.rsplit("/", 1)[-1]
        locs[str(r.campaign.id)]["negative" if cc.negative else "positive"].append(gid)
    snap["locations"] = {k: {"positive_count": len(v["positive"]),
                             "negative_count": len(v["negative"]),
                             "negative_ids": sorted(v["negative"]),
                             "positive_ids": sorted(v["positive"])}
                         for k, v in locs.items()}

    # ad schedules
    q = ("SELECT campaign.id, campaign_criterion.criterion_id, "
         "campaign_criterion.status, campaign_criterion.ad_schedule.day_of_week, "
         "campaign_criterion.ad_schedule.start_hour, "
         "campaign_criterion.ad_schedule.start_minute, "
         "campaign_criterion.ad_schedule.end_hour, "
         "campaign_criterion.ad_schedule.end_minute, "
         "campaign_criterion.bid_modifier "
         f"FROM campaign_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND campaign_criterion.type = 'AD_SCHEDULE' "
         "AND campaign_criterion.status != 'REMOVED'")
    sched = {CAMP_A: [], CAMP_B: []}
    for r in rows(svc, q):
        a = r.campaign_criterion.ad_schedule
        sm = MIN_MAP.get(a.start_minute.name, a.start_minute.name)
        em = MIN_MAP.get(a.end_minute.name, a.end_minute.name)
        sched[str(r.campaign.id)].append({
            "day": a.day_of_week.name,
            "start": "%02d:%s" % (a.start_hour, sm),
            "end": "%02d:%s" % (a.end_hour, em),
            "start_hour": a.start_hour,
            "end_hour": a.end_hour,
            "bid_modifier": r.campaign_criterion.bid_modifier or None,
            "status": r.campaign_criterion.status.name,
        })
    for k in sched:
        sched[k].sort(key=lambda x: (DAY_ORDER.get(x["day"], 9), x["start"]))
    snap["ad_schedules"] = sched

    OUT.write_text(json.dumps(snap, indent=2), encoding="utf-8")

    print(json.dumps({
        "snapshot_account_local": snap["snapshot_account_local"],
        "identity_gate_passed": ident["identity_gate_passed"],
        "identity_checks": ident["matches_expected"],
        "identity": {k: ident[k] for k in
                     ("descriptive_name", "id", "manager", "test_account",
                      "currency_code", "time_zone", "status",
                      "pay_per_conversion_eligibility_failure_reasons")},
    }, indent=2))
    for cid_, cp in camps.items():
        print("\n--- %s (%s) ---" % (cp["name"], cid_))
        for k in ("status", "serving_status", "primary_status",
                  "primary_status_reasons", "bidding_strategy_type",
                  "bidding_strategy_system_status", "target_spend_cpc_ceiling_usd",
                  "network_google_search", "network_search_partners",
                  "network_display", "network_partner_search", "positive_geo",
                  "start_date_time", "end_date_time", "budget_id",
                  "payment_mode", "experiment_type"):
            print("  %s: %s" % (k, cp[k]))
        b = cp["budget"]
        print("  BUDGET: $%s/day delivery=%s shared=%s refs=%s period=%s type=%s status=%s"
              % (b["amount_usd"], b["delivery_method"], b["explicitly_shared"],
                 b["reference_count"], b["period"], b["type"], b["status"]))
        print("  RECOMMENDED_BUDGET: has=%s value=%s"
              % (b["has_recommended_budget"], b["recommended_budget_usd"]))
        print("  LOCATIONS: +%s -%s neg=%s"
              % (snap["locations"][cid_]["positive_count"],
                 snap["locations"][cid_]["negative_count"],
                 snap["locations"][cid_]["negative_ids"]))
        print("  SCHEDULE (%d dayparts): %s"
              % (len(sched[cid_]),
                 ", ".join("%s %s-%s" % (s["day"][:3], s["start"], s["end"])
                           for s in sched[cid_])))
    print("\nALL campaign_budget rows in account (non-removed):")
    for bid, b in sorted(buds.items()):
        print("  %s %-40s $%-9s refs=%s shared=%s"
              % (bid, b["name"][:40], b["amount_usd"], b["reference_count"],
                 b["explicitly_shared"]))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
