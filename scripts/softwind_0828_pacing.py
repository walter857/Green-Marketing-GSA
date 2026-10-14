#!/usr/bin/env python3
"""AUGUST 28 fresh read-only pacing + blocker sweep for Softwind Power Washing.

Stages 4-6 of the August 28 delivery-and-budget-recovery instruction:
  Stage 4  account-level spending limit / billing / verification probe
  Stage 5  fresh August pacing snapshot (Aug 1-27, Aug 28 partial, MTD, daily, hourly)
  Stage 6  serving-blocker sweep

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
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
OUT = ROOT / "clients/softwind-power-washing/snapshots/pacing-2026-08-28.json"

MTD_START = "2026-08-01"
COMPLETE_END = "2026-08-27"
TODAY = "2026-08-28"

METRIC_FIELDS = [
    "metrics.cost_micros", "metrics.impressions", "metrics.clicks",
    "metrics.ctr", "metrics.average_cpc", "metrics.conversions",
    "metrics.conversions_from_interactions_rate",
    "metrics.cost_per_conversion",
    "metrics.search_impression_share",
    "metrics.search_budget_lost_impression_share",
    "metrics.search_rank_lost_impression_share",
    "metrics.search_top_impression_share",
    "metrics.search_absolute_top_impression_share",
]


def rows(svc, query):
    out = []
    for batch in svc.search_stream(customer_id=CID, query=query):
        for r in batch.results:
            out.append(r)
    return out


def usd(micros):
    return round((micros or 0) / 1_000_000, 2)


def pct(v):
    return None if v is None else round(v * 100, 2)


def metric_block(m, has_is=True):
    d = {
        "cost": usd(m.cost_micros),
        "impressions": m.impressions,
        "clicks": m.clicks,
        "ctr_pct": pct(m.ctr) if m.impressions else 0.0,
        "avg_cpc": usd(m.average_cpc),
        "conversions": round(m.conversions, 2),
        "conv_rate_pct": pct(m.conversions_from_interactions_rate) if m.clicks else 0.0,
        "cost_per_conversion": usd(m.cost_per_conversion) if m.conversions else None,
    }
    if has_is:
        d.update({
            "search_impression_share_pct": pct(m.search_impression_share),
            "search_lost_is_budget_pct": pct(m.search_budget_lost_impression_share),
            "search_lost_is_rank_pct": pct(m.search_rank_lost_impression_share),
            "search_top_is_pct": pct(m.search_top_impression_share),
            "search_abs_top_is_pct": pct(m.search_absolute_top_impression_share),
        })
    return d


def window(svc, start, end, sel=None, extra_group=""):
    sel = sel or METRIC_FIELDS
    q = ("SELECT campaign.id, campaign.name, " + ", ".join(sel) +
         f"{extra_group} FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '{start}' AND '{end}'")
    return rows(svc, q)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")

    now = datetime.now(TZ)
    snap = {"read_only": True, "mutations_issued": 0,
            "snapshot_account_local": now.isoformat(),
            "snapshot_account_local_human": now.strftime("%Y-%m-%d %H:%M:%S %Z")}

    # ============ Stage 4: billing / account-level spending limit ============
    billing = {"api_note": (
        "The Google Ads API exposes NO customer-level 'daily spending limit' field. "
        "A GoogleAdsFieldService scan of customer.%limit% returns zero rows. The "
        "new-account daily spending limit, if present, is visible only in the UI "
        "notification bar. account_budget/billing_setup below cover the invoiced "
        "and payments-profile side, which is what the API does expose.")}
    for res, sel in (
        ("billing_setup",
         ["billing_setup.id", "billing_setup.status",
          "billing_setup.start_date_time", "billing_setup.end_date_time",
          "billing_setup.end_time_type",
          "billing_setup.payments_account_info.payments_account_id",
          "billing_setup.payments_account_info.payments_account_name",
          "billing_setup.payments_account_info.payments_profile_id"]),
        ("account_budget",
         ["account_budget.id", "account_budget.name", "account_budget.status",
          "account_budget.approved_spending_limit_micros",
          "account_budget.approved_spending_limit_type",
          "account_budget.adjusted_spending_limit_micros",
          "account_budget.adjusted_spending_limit_type",
          "account_budget.proposed_spending_limit_micros",
          "account_budget.proposed_spending_limit_type",
          "account_budget.amount_served_micros",
          "account_budget.total_adjustments_micros",
          "account_budget.approved_start_date_time",
          "account_budget.approved_end_date_time",
          "account_budget.approved_end_time_type"]),
    ):
        try:
            got = rows(svc, "SELECT " + ", ".join(sel) + " FROM " + res)
            recs = []
            for r in got:
                obj = getattr(r, res)
                rec = {}
                for f in sel:
                    leaf = f.split(".", 1)[1]
                    cur = obj
                    for part in leaf.split("."):
                        cur = getattr(cur, part)
                    rec[leaf] = cur.name if hasattr(cur, "name") else (
                        str(cur) if not isinstance(cur, (int, float, bool)) else cur)
                    if leaf.endswith("_micros") and isinstance(rec[leaf], int):
                        rec[leaf.replace("_micros", "_usd")] = usd(rec[leaf])
                recs.append(rec)
            billing[res] = {"row_count": len(recs), "rows": recs}
        except Exception as exc:
            billing[res] = {"error": str(exc)[:400]}

    # campaign-level primary status reasons already read in the state snapshot;
    # re-read here so the pacing receipt is self-contained.
    q = ("SELECT campaign.id, campaign.name, campaign.primary_status, "
         "campaign.primary_status_reasons, campaign.serving_status, "
         "campaign.bidding_strategy_system_status "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    billing["campaign_primary_status"] = {
        str(r.campaign.id): {
            "primary_status": r.campaign.primary_status.name,
            "primary_status_reasons": [x.name for x in r.campaign.primary_status_reasons],
            "serving_status": r.campaign.serving_status.name,
            "bidding_strategy_system_status":
                r.campaign.bidding_strategy_system_status.name,
        } for r in rows(svc, q)}
    snap["billing_and_account_limits"] = billing

    # ============ Stage 5: pacing ============
    pacing = {}
    for label, (s, e) in {
        "aug_01_to_27_complete": (MTD_START, COMPLETE_END),
        "aug_28_partial": (TODAY, TODAY),
        "aug_mtd_combined": (MTD_START, TODAY),
    }.items():
        per = {}
        for r in window(svc, s, e):
            per[str(r.campaign.id)] = metric_block(r.metrics)
        combined = {"cost": round(sum(v["cost"] for v in per.values()), 2),
                    "impressions": sum(v["impressions"] for v in per.values()),
                    "clicks": sum(v["clicks"] for v in per.values()),
                    "conversions": round(sum(v["conversions"] for v in per.values()), 2)}
        combined["ctr_pct"] = (round(combined["clicks"] / combined["impressions"] * 100, 2)
                               if combined["impressions"] else 0.0)
        combined["avg_cpc"] = (round(combined["cost"] / combined["clicks"], 2)
                               if combined["clicks"] else 0.0)
        combined["conv_rate_pct"] = (round(combined["conversions"] / combined["clicks"] * 100, 2)
                                     if combined["clicks"] else 0.0)
        combined["cost_per_conversion"] = (round(combined["cost"] / combined["conversions"], 2)
                                           if combined["conversions"] else None)
        combined["impression_share_note"] = (
            "Impression share is a weighted metric and is NOT summable across "
            "campaigns. Per-campaign values above are authoritative.")
        pacing[label] = {"start": s, "end": e, "per_campaign": per, "combined": combined}
    snap["pacing"] = pacing

    # daily Aug 20 -> Aug 28, per campaign
    daily = {}
    q = ("SELECT campaign.id, segments.date, metrics.cost_micros, "
         "metrics.impressions, metrics.clicks, metrics.average_cpc, "
         "metrics.conversions, metrics.search_impression_share, "
         "metrics.search_budget_lost_impression_share, "
         "metrics.search_rank_lost_impression_share "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-20' AND '{TODAY}'")
    for r in rows(svc, q):
        d = r.segments.date
        daily.setdefault(d, {})[str(r.campaign.id)] = {
            "cost": usd(r.metrics.cost_micros),
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "avg_cpc": usd(r.metrics.average_cpc),
            "conversions": round(r.metrics.conversions, 2),
            "is_pct": pct(r.metrics.search_impression_share),
            "lost_is_budget_pct": pct(r.metrics.search_budget_lost_impression_share),
            "lost_is_rank_pct": pct(r.metrics.search_rank_lost_impression_share),
        }
    snap["daily_aug20_to_aug28"] = dict(sorted(daily.items()))

    # hourly Aug 27 and Aug 28
    hourly = {}
    q = ("SELECT campaign.id, segments.date, segments.hour, "
         "metrics.cost_micros, metrics.impressions, metrics.clicks "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-27' AND '{TODAY}'")
    for r in rows(svc, q):
        key = r.segments.date
        hourly.setdefault(key, {}).setdefault(int(r.segments.hour), {})[
            str(r.campaign.id)] = {
            "cost": usd(r.metrics.cost_micros),
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
        }
    snap["hourly"] = {k: dict(sorted(v.items())) for k, v in sorted(hourly.items())}

    # individual click costs today (click_view is 90-day retained, date-required)
    try:
        q = ("SELECT click_view.gclid, campaign.id, segments.date, "
             "metrics.clicks "
             f"FROM click_view WHERE segments.date = '{TODAY}'")
        cv = rows(svc, q)
        snap["click_view_today"] = {"row_count": len(cv)}
    except Exception as exc:
        snap["click_view_today"] = {"error": str(exc)[:300]}

    # ============ Stage 6: serving blockers ============
    blockers = {}

    q = ("SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, "
         "ad_group.type, ad_group.cpc_bid_micros "
         f"FROM ad_group WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND ad_group.status != 'REMOVED'")
    ags = {}
    for r in rows(svc, q):
        ags.setdefault(str(r.campaign.id), []).append({
            "id": str(r.ad_group.id), "name": r.ad_group.name,
            "status": r.ad_group.status.name,
            "cpc_bid_usd": usd(r.ad_group.cpc_bid_micros)})
    blockers["ad_groups"] = {
        k: {"total": len(v),
            "enabled": sum(1 for x in v if x["status"] == "ENABLED"),
            "paused": sum(1 for x in v if x["status"] == "PAUSED"),
            "enabled_names": sorted(x["name"] for x in v if x["status"] == "ENABLED")}
        for k, v in ags.items()}

    q = ("SELECT campaign.id, ad_group.id, ad_group.name, "
         "ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
         "ad_group_criterion.keyword.match_type, ad_group_criterion.status, "
         "ad_group_criterion.system_serving_status, "
         "ad_group_criterion.approval_status, "
         "ad_group_criterion.effective_cpc_bid_micros, "
         "ad_group_criterion.quality_info.quality_score "
         f"FROM ad_group_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND ad_group_criterion.type = 'KEYWORD' "
         "AND ad_group_criterion.negative = FALSE "
         "AND ad_group_criterion.status != 'REMOVED'")
    kws = []
    for r in rows(svc, q):
        c = r.ad_group_criterion
        kws.append({
            "campaign_id": str(r.campaign.id), "ad_group_id": str(r.ad_group.id),
            "ad_group": r.ad_group.name,
            "text": c.keyword.text, "match": c.keyword.match_type.name,
            "status": c.status.name,
            "system_serving_status": c.system_serving_status.name,
            "approval_status": c.approval_status.name,
            "effective_cpc_bid_usd": usd(c.effective_cpc_bid_micros),
            "quality_score": c.quality_info.quality_score or None,
        })
    enabled_kws = [k for k in kws if k["status"] == "ENABLED"]
    blockers["keywords"] = {
        "total_non_removed": len(kws),
        "enabled": len(enabled_kws),
        "paused": sum(1 for k in kws if k["status"] == "PAUSED"),
        "enabled_by_campaign": {
            c: sum(1 for k in enabled_kws if k["campaign_id"] == c)
            for c in (CAMP_A, CAMP_B)},
        "enabled_system_serving_status": _tally(enabled_kws, "system_serving_status"),
        "enabled_approval_status": _tally(enabled_kws, "approval_status"),
        "enabled_low_search_volume": sorted(
            "%s [%s] %s" % (k["text"], k["match"], k["ad_group"])
            for k in enabled_kws if k["system_serving_status"] == "RARELY_SERVED"),
        "enabled_not_eligible": sorted(
            "%s [%s] %s -> %s" % (k["text"], k["match"], k["ad_group"],
                                  k["approval_status"])
            for k in enabled_kws
            if k["approval_status"] not in ("APPROVED", "UNSPECIFIED", "UNKNOWN")),
    }

    q = ("SELECT campaign.id, ad_group.id, ad_group.name, ad_group_ad.ad.id, "
         "ad_group_ad.status, ad_group_ad.policy_summary.approval_status, "
         "ad_group_ad.policy_summary.review_status, "
         "ad_group_ad.ad.type, ad_group_ad.ad.final_urls "
         f"FROM ad_group_ad WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND ad_group_ad.status != 'REMOVED'")
    ads = []
    for r in rows(svc, q):
        a = r.ad_group_ad
        ads.append({
            "campaign_id": str(r.campaign.id), "ad_group": r.ad_group.name,
            "ad_id": str(a.ad.id), "status": a.status.name,
            "approval": a.policy_summary.approval_status.name,
            "review": a.policy_summary.review_status.name,
            "type": a.ad.type_.name,
            "final_urls": list(a.ad.final_urls)})
    en_ads = [a for a in ads if a["status"] == "ENABLED"]
    blockers["ads"] = {
        "total_non_removed": len(ads), "enabled": len(en_ads),
        "enabled_approval": _tally(en_ads, "approval"),
        "enabled_review": _tally(en_ads, "review"),
        "enabled_by_campaign": {c: sum(1 for a in en_ads if a["campaign_id"] == c)
                                for c in (CAMP_A, CAMP_B)},
        "not_approved": [a for a in en_ads if a["approval"] not in
                         ("APPROVED", "APPROVED_LIMITED")],
        "distinct_final_urls": sorted({u for a in en_ads for u in a["final_urls"]}),
    }

    q = ("SELECT campaign.id, campaign_criterion.criterion_id, "
         "campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, "
         "campaign_criterion.status "
         f"FROM campaign_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND campaign_criterion.type = 'KEYWORD' "
         "AND campaign_criterion.negative = TRUE "
         "AND campaign_criterion.status != 'REMOVED'")
    negs = []
    for r in rows(svc, q):
        negs.append({"campaign_id": str(r.campaign.id),
                     "text": r.campaign_criterion.keyword.text,
                     "match": r.campaign_criterion.keyword.match_type.name})
    blockers["campaign_negative_keywords"] = {
        "total": len(negs),
        "by_campaign": {c: sum(1 for n in negs if n["campaign_id"] == c)
                        for c in (CAMP_A, CAMP_B)}}

    # negative-keyword conflict check against enabled keyword texts
    conflicts = []
    for c in (CAMP_A, CAMP_B):
        neg_texts = {n["text"].lower(): n["match"] for n in negs
                     if n["campaign_id"] == c}
        for k in enabled_kws:
            if k["campaign_id"] != c:
                continue
            kt = k["text"].lower()
            for nt, nm in neg_texts.items():
                if nm == "EXACT" and nt == kt:
                    conflicts.append({"campaign": c, "keyword": k["text"],
                                      "negative": nt, "neg_match": nm,
                                      "kind": "EXACT block"})
                elif nm == "PHRASE" and nt in kt:
                    conflicts.append({"campaign": c, "keyword": k["text"],
                                      "negative": nt, "neg_match": nm,
                                      "kind": "PHRASE block"})
                elif nm == "BROAD" and all(
                        w in kt.split() for w in nt.split()):
                    conflicts.append({"campaign": c, "keyword": k["text"],
                                      "negative": nt, "neg_match": nm,
                                      "kind": "BROAD block"})
    blockers["negative_conflicts"] = {"count": len(conflicts),
                                      "detail": conflicts[:50]}

    q = ("SELECT campaign.id, shared_set.id, shared_set.name, shared_set.type, "
         "shared_set.member_count, shared_set.status "
         f"FROM campaign_shared_set WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    ss = [{"campaign_id": str(r.campaign.id), "id": str(r.shared_set.id),
           "name": r.shared_set.name, "type": r.shared_set.type_.name,
           "members": r.shared_set.member_count,
           "status": r.shared_set.status.name} for r in rows(svc, q)]
    blockers["shared_negative_lists"] = {"count": len(ss), "detail": ss}

    q = ("SELECT campaign.id, campaign_conversion_goal.category, "
         "campaign_conversion_goal.origin, campaign_conversion_goal.biddable "
         f"FROM campaign_conversion_goal WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    goals = []
    for r in rows(svc, q):
        g = r.campaign_conversion_goal
        if g.biddable:
            goals.append({"campaign_id": str(r.campaign.id),
                          "category": g.category.name, "origin": g.origin.name})
    blockers["biddable_conversion_goals"] = {
        "count": len(goals),
        "by_campaign": {c: sorted(g["category"] + "/" + g["origin"]
                                  for g in goals if g["campaign_id"] == c)
                        for c in (CAMP_A, CAMP_B)}}

    q = ("SELECT conversion_action.id, conversion_action.name, "
         "conversion_action.status, conversion_action.type, "
         "conversion_action.category, conversion_action.primary_for_goal, "
         "conversion_action.counting_type "
         "FROM conversion_action WHERE conversion_action.status != 'REMOVED'")
    blockers["conversion_actions"] = [
        {"id": str(r.conversion_action.id), "name": r.conversion_action.name,
         "status": r.conversion_action.status.name,
         "type": r.conversion_action.type_.name,
         "category": r.conversion_action.category.name,
         "primary_for_goal": r.conversion_action.primary_for_goal,
         "counting": r.conversion_action.counting_type.name}
        for r in rows(svc, q)]

    snap["blockers"] = blockers
    OUT.write_text(json.dumps(snap, indent=2), encoding="utf-8")

    # ------------------------- console report -------------------------
    print("SNAPSHOT (account-local): %s" % snap["snapshot_account_local_human"])
    print("\n===== STAGE 4  ACCOUNT-LEVEL SPENDING LIMIT / BILLING =====")
    print(billing["api_note"])
    for res in ("billing_setup", "account_budget"):
        print("\n%s: %s" % (res.upper(), json.dumps(billing[res], indent=2)[:1600]))
    print("\nCAMPAIGN PRIMARY STATUS: %s"
          % json.dumps(billing["campaign_primary_status"], indent=2))

    print("\n===== STAGE 5  AUGUST PACING =====")
    for label in ("aug_01_to_27_complete", "aug_28_partial", "aug_mtd_combined"):
        b = pacing[label]
        print("\n--- %s  (%s .. %s) ---" % (label, b["start"], b["end"]))
        for cid_, m in b["per_campaign"].items():
            print("  %-16s %s" % (NAMES[cid_], json.dumps(m)))
        print("  %-16s %s" % ("COMBINED", json.dumps(
            {k: v for k, v in b["combined"].items()
             if k != "impression_share_note"})))

    print("\n--- DAILY 2026-08-20 .. 2026-08-28 ---")
    for d, per in snap["daily_aug20_to_aug28"].items():
        tot = round(sum(x["cost"] for x in per.values()), 2)
        imp = sum(x["impressions"] for x in per.values())
        clk = sum(x["clicks"] for x in per.values())
        det = " | ".join("%s $%s/%si/%sc IS=%s LostBud=%s LostRank=%s"
                         % (NAMES[c][-2:], v["cost"], v["impressions"], v["clicks"],
                            v["is_pct"], v["lost_is_budget_pct"], v["lost_is_rank_pct"])
                         for c, v in sorted(per.items()))
        print("  %s  TOTAL $%-7s %3di %2dc   %s" % (d, tot, imp, clk, det))

    print("\n--- HOURLY ---")
    for d, hrs in snap["hourly"].items():
        print("  %s" % d)
        for h, per in hrs.items():
            tot = round(sum(x["cost"] for x in per.values()), 2)
            imp = sum(x["impressions"] for x in per.values())
            clk = sum(x["clicks"] for x in per.values())
            if imp or tot:
                print("    %02d:00  $%-7s %3di %2dc" % (h, tot, imp, clk))
    print("  click_view today: %s" % json.dumps(snap["click_view_today"]))

    print("\n===== STAGE 6  SERVING BLOCKERS =====")
    for k in ("ad_groups", "keywords", "ads", "campaign_negative_keywords",
              "negative_conflicts", "shared_negative_lists",
              "biddable_conversion_goals"):
        print("\n%s:\n%s" % (k.upper(), json.dumps(blockers[k], indent=2)[:2500]))
    print("\nCONVERSION ACTIONS:\n%s"
          % json.dumps(blockers["conversion_actions"], indent=2))
    print("\nwrote %s" % OUT)
    return 0


def _tally(items, key):
    out = {}
    for i in items:
        out[i[key]] = out.get(i[key], 0) + 1
    return dict(sorted(out.items()))


if __name__ == "__main__":
    raise SystemExit(main())
