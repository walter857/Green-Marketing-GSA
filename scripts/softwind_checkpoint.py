#!/usr/bin/env python3
"""Read-only pacing checkpoint for Softwind Power Washing (1521725229).

Stage 13 of the August delivery-and-budget-recovery instruction. Run at each
checkpoint:  immediately, 13:00 ET, 17:00 ET, end of day.

Emits every field the instruction requires: today's spend, MTD, remaining,
required rolling pace, projected August total, impressions, clicks, average CPC,
INDIVIDUAL click costs, search terms, negative candidates, leads, Lost IS
(budget), Lost IS (rank), the A/B spend split and location performance.

READ ONLY. Never writes to Google Ads. No automated budget writes, ever.

usage: softwind_checkpoint.py [--label immediately|1300|1700|eod]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
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
TARGET = 2500.0
MONTH_END = datetime(2026, 9, 1, 0, 0, 0, tzinfo=TZ)
RECEIPTS = ROOT / "clients/softwind-power-washing/receipts"

# Emergency high-CPC stop condition, carried forward from 2026-08-26.
SINGLE_INVESTIGATE, SINGLE_STOP = 40.00, 60.00
ROLLING_INVESTIGATE, ROLLING_STOP = 38.00, 45.00

# Intent guard: never propose these as negatives without a human intent check.
PROTECTED = {"near me", "quote", "price", "pricing", "cost", "best", "hire",
             "local", "emergency"}
# Out-of-scope intents that are legitimate negative CANDIDATES for this service.
DISQUALIFY = ["rental", "rent ", "for rent", "equipment", "machine", "buy ",
              "for sale", "diy", "how to", "job", "jobs", "hiring", "salary",
              "career", "training", "course", "certification", "franchise",
              "roof", "gutter", "paver seal", "landscap", "masonry", "painting",
              "shrink wrap", "party rental", "lawn care",
              "gas station", "commercial", "industrial", "warehouse", "fleet",
              "parking lot", "restaurant", "storefront", "store front", "hoa",
              "house cleaning", "maid", "window clean", "carpet", "chimney",
              "pool", "tree"]


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def pct(v):
    return None if v is None else round(v * 100, 2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="adhoc")
    args = ap.parse_args()

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    today = now.strftime("%Y-%m-%d")
    cp = {"read_only": True, "mutations_issued": 0, "label": args.label,
          "timestamp_account_local": now.isoformat(), "today": today}

    # identity re-assert on every checkpoint
    c = rows(svc, "SELECT customer.id, customer.descriptive_name, customer.manager, "
                  "customer.test_account, customer.currency_code, customer.time_zone "
                  "FROM customer LIMIT 1")[0].customer
    cp["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                      "manager": c.manager, "test_account": c.test_account,
                      "currency": c.currency_code, "tz": c.time_zone}
    if str(c.id) != CID or c.descriptive_name != "Softwind Power Washing - Live":
        cp["ABORT"] = "IDENTITY MISMATCH"
        print(json.dumps(cp, indent=2))
        return 2

    # today + MTD, per campaign
    def win(start, end):
        q = ("SELECT campaign.id, metrics.cost_micros, metrics.impressions, "
             "metrics.clicks, metrics.average_cpc, metrics.conversions, "
             "metrics.search_impression_share, "
             "metrics.search_budget_lost_impression_share, "
             "metrics.search_rank_lost_impression_share "
             f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
             f"AND segments.date BETWEEN '{start}' AND '{end}'")
        d = {}
        for r in rows(svc, q):
            d[str(r.campaign.id)] = {
                "cost": usd(r.metrics.cost_micros),
                "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
                "avg_cpc": usd(r.metrics.average_cpc),
                "conversions": round(r.metrics.conversions, 2),
                "search_is_pct": pct(r.metrics.search_impression_share),
                "lost_is_budget_pct": pct(
                    r.metrics.search_budget_lost_impression_share),
                "lost_is_rank_pct": pct(
                    r.metrics.search_rank_lost_impression_share)}
        return d

    cp["today_per_campaign"] = win(today, today)
    cp["mtd_per_campaign"] = win("2026-08-01", today)
    cp["today_spend"] = round(sum(v["cost"] for v in
                                  cp["today_per_campaign"].values()), 2)
    cp["mtd_spend"] = round(sum(v["cost"] for v in
                                cp["mtd_per_campaign"].values()), 2)
    cp["today_impressions"] = sum(v["impressions"] for v in
                                  cp["today_per_campaign"].values())
    cp["today_clicks"] = sum(v["clicks"] for v in
                             cp["today_per_campaign"].values())
    cp["campaign_ab_spend_split"] = {
        NAMES[k]: v["cost"] for k, v in cp["mtd_per_campaign"].items()}
    cp["leads_mtd"] = round(sum(v["conversions"] for v in
                                cp["mtd_per_campaign"].values()), 2)

    # pacing math
    R = round(TARGET - cp["mtd_spend"], 2)
    H = round((MONTH_END - now).total_seconds() / 3600, 2)
    D = (datetime(2026, 8, 31, tzinfo=TZ).date() - now.date()).days + 1
    serving_days, cur = 0, now
    serving_hours = 0.0
    while cur < MONTH_END:
        if cur.weekday() != 6:
            s = max(cur, cur.replace(hour=8, minute=0, second=0, microsecond=0))
            e = min(MONTH_END, cur.replace(hour=18, minute=0, second=0,
                                           microsecond=0))
            if e > s:
                serving_days += 1
                serving_hours += (e - s).total_seconds() / 3600
        cur = (cur + timedelta(days=1)).replace(hour=0, minute=0, second=0,
                                                microsecond=0)
    serving_hours = round(serving_hours, 2)
    cp["pacing"] = {
        "target": TARGET, "mtd_spend": cp["mtd_spend"], "remaining_R": R,
        "remaining_calendar_days_D": D, "remaining_hours_H": H,
        "remaining_serving_days": serving_days,
        "remaining_scheduled_serving_hours": serving_hours,
        "required_rolling_24h_pace": round(R / (H / 24), 2) if H > 0 else None,
        "required_per_scheduled_serving_hour": (
            round(R / serving_hours, 2) if serving_hours > 0 else None),
    }

    # projection from observed serving-day run rate
    q = ("SELECT campaign.id, segments.date, metrics.cost_micros FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-24' AND '{today}'")
    per_day = {}
    for r in rows(svc, q):
        per_day[r.segments.date] = round(
            per_day.get(r.segments.date, 0.0) + usd(r.metrics.cost_micros), 2)
    rr = round(sum(per_day.values()) / max(len(per_day), 1), 2)
    cp["pacing"]["observed_run_rate_per_serving_day"] = rr
    cp["pacing"]["recent_daily"] = dict(sorted(per_day.items()))
    cp["pacing"]["projected_august_total"] = round(
        cp["mtd_spend"] + rr * max(serving_days - 1, 0)
        + max(rr - cp["today_spend"], 0), 2)

    # INDIVIDUAL click costs, today and month-to-date
    q = ("SELECT campaign.id, ad_group.name, ad_group_criterion.keyword.text, "
         "ad_group_criterion.keyword.match_type, segments.date, "
         "metrics.clicks, metrics.cost_micros, metrics.average_cpc "
         f"FROM keyword_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-01' AND '{today}' "
         "AND metrics.clicks > 0")
    clicks = [{"date": r.segments.date, "campaign": NAMES[str(r.campaign.id)],
               "ad_group": r.ad_group.name,
               "keyword": r.ad_group_criterion.keyword.text,
               "match": r.ad_group_criterion.keyword.match_type.name,
               "clicks": r.metrics.clicks, "cost": usd(r.metrics.cost_micros),
               "avg_cpc": usd(r.metrics.average_cpc)} for r in rows(svc, q)]
    clicks.sort(key=lambda x: (x["date"], -x["cost"]))
    cp["individual_click_costs"] = clicks
    cp["individual_click_costs_today"] = [c for c in clicks if c["date"] == today]

    # emergency high-CPC stop condition
    costs = [c["avg_cpc"] for c in clicks]
    rolling3 = round(sum(costs[-3:]) / len(costs[-3:]), 2) if costs else 0.0
    worst = max(costs) if costs else 0.0
    alerts = []
    for c in clicks:
        if c["avg_cpc"] >= SINGLE_STOP:
            alerts.append("STOP: %s %s '%s' at $%s (>= $%s)"
                          % (c["date"], c["campaign"], c["keyword"],
                             c["avg_cpc"], SINGLE_STOP))
        elif c["avg_cpc"] >= SINGLE_INVESTIGATE:
            alerts.append("INVESTIGATE: %s %s '%s' at $%s (>= $%s)"
                          % (c["date"], c["campaign"], c["keyword"],
                             c["avg_cpc"], SINGLE_INVESTIGATE))
    if rolling3 >= ROLLING_STOP:
        alerts.append("STOP: trailing-3-click average $%s (>= $%s)"
                      % (rolling3, ROLLING_STOP))
    elif rolling3 >= ROLLING_INVESTIGATE:
        alerts.append("INVESTIGATE: trailing-3-click average $%s (>= $%s)"
                      % (rolling3, ROLLING_INVESTIGATE))
    cp["cpc_stop_condition"] = {
        "thresholds": {"single_investigate": SINGLE_INVESTIGATE,
                       "single_stop": SINGLE_STOP,
                       "rolling_investigate": ROLLING_INVESTIGATE,
                       "rolling_stop": ROLLING_STOP},
        "worst_single_click": worst, "trailing_3_click_avg": rolling3,
        "breached": bool(alerts), "alerts": alerts}

    # search terms + negative candidates
    q = ("SELECT campaign.id, search_term_view.search_term, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM search_term_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-01' AND '{today}'")
    terms = {}
    for r in rows(svc, q):
        t = r.search_term_view.search_term
        d = terms.setdefault(t, {"term": t, "impressions": 0, "clicks": 0,
                                 "cost": 0.0, "campaigns": set()})
        d["impressions"] += r.metrics.impressions
        d["clicks"] += r.metrics.clicks
        d["cost"] = round(d["cost"] + usd(r.metrics.cost_micros), 2)
        d["campaigns"].add(NAMES[str(r.campaign.id)])
    term_list = sorted(terms.values(),
                       key=lambda x: (-x["cost"], -x["clicks"], -x["impressions"]))
    for t in term_list:
        t["campaigns"] = sorted(t["campaigns"])
    cp["search_terms"] = term_list
    cp["search_terms_today"] = [t for t in term_list]  # date-agnostic aggregate

    # A protected token must never be negatived ON ITS OWN, but its presence
    # must NOT exclude the whole term from review - almost every query in this
    # account contains "near me", so the old guard hid every real candidate.
    cands = []
    for t in term_list:
        low = t["term"].lower()
        hit = next((d for d in DISQUALIFY if d in low), None)
        if not hit:
            continue
        cands.append({"term": t["term"],
                      "reason": "out-of-scope: %s" % hit.strip(),
                      "protected_tokens_present": [p for p in PROTECTED
                                                   if p in low],
                      "negative_form": "EXACT on the complete phrase only",
                      "impressions": t["impressions"], "clicks": t["clicks"],
                      "cost": t["cost"]})
    cp["negative_candidates"] = {
        "count": len(cands), "detail": cands,
        "policy": ("Protected terms are never auto-negatived: %s. Every candidate "
                   "still needs a human intent check before any plan."
                   % ", ".join(sorted(PROTECTED)))}

    # location performance
    q = ("SELECT campaign.id, campaign_criterion.criterion_id, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM location_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-01' AND '{today}'")
    lv = [{"campaign": NAMES[str(r.campaign.id)],
           "criterion_id": str(r.campaign_criterion.criterion_id),
           "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
           "cost": usd(r.metrics.cost_micros)} for r in rows(svc, q)]
    active = [x for x in lv if x["impressions"] or x["cost"]]
    active.sort(key=lambda x: (-x["cost"], -x["impressions"]))
    cp["location_performance"] = {"rows_total": len(lv),
                                  "rows_with_delivery": len(active),
                                  "detail": active}

    RECEIPTS.mkdir(parents=True, exist_ok=True)
    out = RECEIPTS / ("checkpoint-%s-%s.json"
                      % (now.strftime("%Y-%m-%d-%H%M"), args.label))
    out.write_text(json.dumps(cp, indent=2, default=str), encoding="utf-8")

    p = cp["pacing"]
    print("=" * 72)
    print("PACING CHECKPOINT [%s]  %s" % (args.label,
                                          now.strftime("%Y-%m-%d %H:%M:%S %Z")))
    print("  %s | %s | Power Washing" % (cp["identity"]["name"], cp["identity"]["id"]))
    print("=" * 72)
    print("  today spend            $%s   (%d impr, %d clicks)"
          % (cp["today_spend"], cp["today_impressions"], cp["today_clicks"]))
    print("  MTD spend              $%s" % cp["mtd_spend"])
    print("  remaining to $2,500    $%s" % p["remaining_R"])
    print("  remaining hours        %s   (calendar days %s)"
          % (p["remaining_hours_H"], p["remaining_calendar_days_D"]))
    print("  remaining serving      %s days / %sh"
          % (p["remaining_serving_days"], p["remaining_scheduled_serving_hours"]))
    print("  required 24h pace      $%s" % p["required_rolling_24h_pace"])
    print("  required per serv. hr  $%s" % p["required_per_scheduled_serving_hour"])
    print("  observed run rate      $%s / serving day" % p["observed_run_rate_per_serving_day"])
    print("  PROJECTED AUGUST       $%s" % p["projected_august_total"])
    print("  A/B spend split        %s" % json.dumps(cp["campaign_ab_spend_split"]))
    print("  leads MTD              %s" % cp["leads_mtd"])
    for cid_, v in cp["mtd_per_campaign"].items():
        print("  %-17s IS %s%%  LostBudget %s%%  LostRank %s%%  avgCPC $%s"
              % (NAMES[cid_], v["search_is_pct"], v["lost_is_budget_pct"],
                 v["lost_is_rank_pct"], v["avg_cpc"]))
    print("\n  INDIVIDUAL CLICK COSTS (%d):" % len(clicks))
    for c in clicks:
        print("    %s %-17s %-32s %-7s $%s"
              % (c["date"], c["campaign"][:17], c["keyword"][:32], c["match"][:7],
                 c["avg_cpc"]))
    s = cp["cpc_stop_condition"]
    print("\n  CPC STOP CONDITION: %s  (worst $%s, trailing-3 $%s)"
          % ("BREACHED" if s["breached"] else "clear", s["worst_single_click"],
             s["trailing_3_click_avg"]))
    for a in s["alerts"]:
        print("    !! %s" % a)
    print("\n  SEARCH TERMS (%d): top by cost" % len(term_list))
    for t in term_list[:12]:
        print("    %-42s %3di %2dc $%s" % (t["term"][:42], t["impressions"],
                                           t["clicks"], t["cost"]))
    print("\n  NEGATIVE CANDIDATES: %d" % cp["negative_candidates"]["count"])
    for c in cp["negative_candidates"]["detail"]:
        print("    %-42s %s" % (c["term"][:42], c["reason"]))
    print("\n  LOCATIONS WITH DELIVERY: %d of %d"
          % (len(active), cp["location_performance"]["rows_total"]))
    for x in active[:12]:
        print("    %-17s crit %-10s %3di %2dc $%s"
              % (x["campaign"][:17], x["criterion_id"], x["impressions"],
                 x["clicks"], x["cost"]))
    print("\n  NO AUTOMATED BUDGET WRITES. Every budget change needs a fresh plan,")
    print("  fingerprint and explicit approval.")
    print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
