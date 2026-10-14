#!/usr/bin/env python3
"""Fresh same-minute snapshot for the August month-end delivery rescue.

READ-ONLY. SELECT queries only. No mutation of any kind.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
TZ = ZoneInfo("America/New_York")
OUT = ROOT / "clients/softwind-power-washing/snapshots/rescue-snapshot-2026-08-26.json"
A, B = "24103511039", "24145053510"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    today = now.date().isoformat()
    out = {"snapshot_account_local": now.isoformat(), "account_local_date": today}

    # ---------- identity ----------
    r = next(iter(svc.search(customer_id=CID, query="""
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account, customer.currency_code, customer.time_zone,
               customer.status
        FROM customer LIMIT 1""")))
    c = r.customer
    out["identity"] = {
        "descriptive_name": c.descriptive_name,
        "customer_id": normalize_customer_id(c.id),
        "manager": bool(c.manager), "test_account": bool(c.test_account),
        "currency": c.currency_code, "time_zone": c.time_zone,
        "status": enum_name(c.status),
    }
    out["identity_gate"] = {
        "name_ok": c.descriptive_name == "Softwind Power Washing - Live",
        "id_ok": normalize_customer_id(c.id) == CID,
        "manager_false": not bool(c.manager),
        "test_false": not bool(c.test_account),
        "currency_ok": c.currency_code == "USD",
        "tz_ok": c.time_zone == "America/New_York",
    }

    # ---------- campaign config ----------
    camps = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.primary_status, campaign.primary_status_reasons,
               campaign.bidding_strategy_type,
               campaign.target_spend.cpc_bid_ceiling_micros,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign_budget.id, campaign_budget.name,
               campaign_budget.amount_micros, campaign_budget.delivery_method,
               campaign_budget.explicitly_shared, campaign_budget.status
        FROM campaign ORDER BY campaign.id"""):
        cp = row.campaign
        camps[str(cp.id)] = {
            "name": cp.name, "status": enum_name(cp.status),
            "serving_status": enum_name(cp.serving_status),
            "primary_status": enum_name(cp.primary_status),
            "primary_status_reasons": [enum_name(x) for x in cp.primary_status_reasons],
            "bidding_strategy_type": enum_name(cp.bidding_strategy_type),
            "cpc_bid_ceiling": (cp.target_spend.cpc_bid_ceiling_micros / 1_000_000
                                if cp.target_spend.cpc_bid_ceiling_micros else None),
            "search_partners": bool(cp.network_settings.target_search_network),
            "display": bool(cp.network_settings.target_content_network),
            "geo_option": enum_name(cp.geo_target_type_setting.positive_geo_target_type),
            "budget_id": str(row.campaign_budget.id),
            "budget_name": row.campaign_budget.name,
            "daily_budget": row.campaign_budget.amount_micros / 1_000_000,
            "budget_delivery": enum_name(row.campaign_budget.delivery_method),
            "budget_shared": bool(row.campaign_budget.explicitly_shared),
            "budget_status": enum_name(row.campaign_budget.status),
        }
    out["campaigns"] = camps

    # ---------- spend windows ----------
    def window(lo, hi, label):
        rows = {}
        for row in svc.search(customer_id=CID, query="""
            SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks,
                   metrics.cost_micros, metrics.ctr, metrics.average_cpc,
                   metrics.conversions, metrics.all_conversions,
                   metrics.search_impression_share,
                   metrics.search_budget_lost_impression_share,
                   metrics.search_rank_lost_impression_share,
                   metrics.search_top_impression_share,
                   metrics.search_absolute_top_impression_share
            FROM campaign WHERE segments.date BETWEEN '%s' AND '%s'""" % (lo, hi)):
            m = row.metrics
            rows[str(row.campaign.id)] = {
                "campaign": row.campaign.name,
                "impressions": int(m.impressions), "clicks": int(m.clicks),
                "cost": round(m.cost_micros / 1_000_000, 2),
                "ctr": round(float(m.ctr), 4),
                "avg_cpc": round(m.average_cpc / 1_000_000, 2) if m.average_cpc else 0.0,
                "conversions": float(m.conversions),
                "all_conversions": float(m.all_conversions),
                "search_is": float(m.search_impression_share) or None,
                "lost_is_budget": float(m.search_budget_lost_impression_share) or None,
                "lost_is_rank": float(m.search_rank_lost_impression_share) or None,
                "search_top_is": float(m.search_top_impression_share) or None,
                "search_abs_top_is": float(m.search_absolute_top_impression_share) or None,
            }
        comb = {
            "impressions": sum(v["impressions"] for v in rows.values()),
            "clicks": sum(v["clicks"] for v in rows.values()),
            "cost": round(sum(v["cost"] for v in rows.values()), 2),
            "conversions": sum(v["conversions"] for v in rows.values()),
        }
        comb["ctr"] = round(comb["clicks"] / comb["impressions"], 4) if comb["impressions"] else 0
        comb["avg_cpc"] = round(comb["cost"] / comb["clicks"], 2) if comb["clicks"] else 0
        return {"label": label, "start": lo, "end": hi,
                "per_campaign": rows, "combined": comb}

    out["spend_aug01_to_aug25_complete"] = window("2026-08-01", "2026-08-25",
                                                  "Aug 1-25 complete days")
    out["spend_aug26_partial"] = window(today, today, "Aug 26 partial to snapshot")
    out["spend_mtd"] = window("2026-08-01", today, "MTD through snapshot")

    # ---------- daily, for pacing ----------
    daily = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, segments.date, metrics.impressions,
               metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM campaign WHERE segments.date BETWEEN '2026-08-01' AND '%s'
        ORDER BY segments.date""" % today):
        daily.append({"campaign_id": str(row.campaign.id),
                      "campaign": row.campaign.name, "date": row.segments.date,
                      "impressions": int(row.metrics.impressions),
                      "clicks": int(row.metrics.clicks),
                      "cost": round(row.metrics.cost_micros / 1_000_000, 2),
                      "conversions": float(row.metrics.conversions)})
    out["daily"] = daily

    # ---------- schedules ----------
    sched = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign_criterion.criterion_id,
               campaign_criterion.ad_schedule.day_of_week,
               campaign_criterion.ad_schedule.start_hour,
               campaign_criterion.ad_schedule.end_hour,
               campaign_criterion.status
        FROM campaign_criterion WHERE campaign_criterion.type = AD_SCHEDULE"""):
        cc = row.campaign_criterion
        sched.setdefault(str(row.campaign.id), []).append({
            "criterion_id": str(cc.criterion_id),
            "day": enum_name(cc.ad_schedule.day_of_week),
            "start_hour": int(cc.ad_schedule.start_hour),
            "end_hour": int(cc.ad_schedule.end_hour),
            "status": enum_name(cc.status)})
    out["ad_schedules"] = sched

    # ---------- enabled ad groups + keywords ----------
    ags = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status,
               ad_group.primary_status
        FROM ad_group ORDER BY campaign.id, ad_group.id"""):
        ags[str(row.ad_group.id)] = {
            "campaign_id": str(row.campaign.id), "name": row.ad_group.name,
            "status": enum_name(row.ad_group.status),
            "primary_status": enum_name(row.ad_group.primary_status)}
    out["ad_groups"] = ags
    out["enabled_ad_groups"] = {k: v for k, v in ags.items() if v["status"] == "ENABLED"}

    kws = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.approval_status,
               ad_group_criterion.system_serving_status,
               ad_group_criterion.primary_status,
               ad_group_criterion.primary_status_reasons,
               ad_group_criterion.quality_info.quality_score
        FROM ad_group_criterion WHERE ad_group_criterion.type = KEYWORD"""):
        k = row.ad_group_criterion
        kws.append({
            "campaign_id": str(row.campaign.id), "ad_group_id": str(row.ad_group.id),
            "ad_group": row.ad_group.name, "criterion_id": str(k.criterion_id),
            "text": k.keyword.text, "match_type": enum_name(k.keyword.match_type),
            "status": enum_name(k.status),
            "approval": enum_name(k.approval_status),
            "serving": enum_name(k.system_serving_status),
            "primary_status": enum_name(k.primary_status),
            "primary_status_reasons": [enum_name(x) for x in k.primary_status_reasons],
            "quality_score": int(k.quality_info.quality_score)
                             if k.quality_info.quality_score else None})
    out["keywords"] = kws
    out["enabled_keywords_live"] = [
        k for k in kws if k["status"] == "ENABLED"
        and ags[k["ad_group_id"]]["status"] == "ENABLED"]

    # ---------- ads policy / serving ----------
    ads = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
               ad_group_ad.policy_summary.approval_status,
               ad_group_ad.policy_summary.review_status,
               ad_group_ad.primary_status, ad_group_ad.ad_strength
        FROM ad_group_ad"""):
        a = row.ad_group_ad
        ads.append({"campaign_id": str(row.campaign.id),
                    "ad_group_id": str(row.ad_group.id), "ad_id": str(a.ad.id),
                    "status": enum_name(a.status),
                    "approval": enum_name(a.policy_summary.approval_status),
                    "review": enum_name(a.policy_summary.review_status),
                    "primary_status": enum_name(a.primary_status),
                    "ad_strength": enum_name(a.ad_strength)})
    out["ads"] = ads
    out["ads_summary"] = {
        "total": len(ads),
        "enabled": sum(1 for a in ads if a["status"] == "ENABLED"),
        "not_approved": [a["ad_id"] for a in ads if a["approval"] != "APPROVED"],
        "under_review": [a["ad_id"] for a in ads if a["review"] != "REVIEWED"],
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("SNAPSHOT %s" % out["snapshot_account_local"])
    print()
    print("IDENTITY GATE")
    for k, v in out["identity_gate"].items():
        print("  %-16s %s" % (k, "PASS" if v else "*** FAIL ***"))
    print("  %s | %s | %s | %s" % (out["identity"]["descriptive_name"],
                                   out["identity"]["customer_id"],
                                   out["identity"]["currency"],
                                   out["identity"]["time_zone"]))
    print()
    print("CAMPAIGN CONFIG")
    for cid_, v in camps.items():
        print("  %s %-18s %s/%s/%s bid=%s ceiling=%s budget=$%.2f (%s) partners=%s display=%s geo=%s"
              % (cid_, v["name"], v["status"], v["serving_status"], v["primary_status"],
                 v["bidding_strategy_type"], v["cpc_bid_ceiling"], v["daily_budget"],
                 v["budget_id"], v["search_partners"], v["display"], v["geo_option"]))
    print()
    for key in ("spend_aug01_to_aug25_complete", "spend_aug26_partial", "spend_mtd"):
        w = out[key]
        print("%s  (%s .. %s)" % (w["label"], w["start"], w["end"]))
        for cid_, v in w["per_campaign"].items():
            f = lambda x: ("%.1f%%" % (x * 100)) if x is not None else "  -  "
            print("   %-18s impr=%4d clk=%2d $%8.2f CTR=%5.2f%% CPC=$%6.2f conv=%.0f IS=%s lostBud=%s lostRank=%s"
                  % (v["campaign"][:18], v["impressions"], v["clicks"], v["cost"],
                     v["ctr"] * 100, v["avg_cpc"], v["conversions"],
                     f(v["search_is"]), f(v["lost_is_budget"]), f(v["lost_is_rank"])))
        cb = w["combined"]
        print("   %-18s impr=%4d clk=%2d $%8.2f CTR=%5.2f%% CPC=$%6.2f conv=%.0f"
              % ("COMBINED", cb["impressions"], cb["clicks"], cb["cost"],
                 cb["ctr"] * 100, cb["avg_cpc"], cb["conversions"]))
        print()
    print("SCHEDULES")
    for cid_, rows in sched.items():
        days = sorted("%s %02d-%02d" % (r["day"][:3], r["start_hour"], r["end_hour"])
                      for r in rows)
        print("  %s  %d dayparts: %s" % (cid_, len(rows), days))
    print()
    print("ENABLED AD GROUPS: %d of %d" % (len(out["enabled_ad_groups"]), len(ags)))
    for gid, v in sorted(out["enabled_ad_groups"].items(),
                         key=lambda x: (x[1]["campaign_id"], x[1]["name"])):
        print("   %s %s  %s" % (v["campaign_id"], gid, v["name"]))
    print()
    print("LIVE KEYWORD ROWS: %d" % len(out["enabled_keywords_live"]))
    print("ADS: %s" % out["ads_summary"])
    print()
    print("Wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
