#!/usr/bin/env python3
"""Post-execution verification for PLAN-K1.

Two things to settle:
  1. the change_event corroboration gate returned 0 rows at execution time -
     confirm whether that was indexing lag or a real problem
  2. MTD moved from $253.39 to $331.37 during execution - resolve exactly what
     delivered today and what each new click cost

READ ONLY.
"""
from __future__ import annotations

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
OUT = ROOT / "clients/softwind-power-washing/snapshots/k1-verify-2026-08-27.json"


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    today = now.strftime("%Y-%m-%d")
    v = {"read_only": True, "mutations_issued": 0,
         "timestamp_account_local": now.isoformat()}

    # ---- 1. authoritative resource state (this is what governs delivery) ----
    q = ("SELECT campaign.id, campaign.name, campaign.bidding_strategy_type, "
         "campaign.target_spend.cpc_bid_ceiling_micros, "
         "campaign.bidding_strategy_system_status, campaign.primary_status, "
         "campaign.primary_status_reasons, campaign_budget.amount_micros "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    state = {}
    for r in rows(svc, q):
        state[str(r.campaign.id)] = {
            "name": r.campaign.name,
            "bidding": r.campaign.bidding_strategy_type.name,
            "ceiling_micros": r.campaign.target_spend.cpc_bid_ceiling_micros or None,
            "ceiling_usd": usd(r.campaign.target_spend.cpc_bid_ceiling_micros) or None,
            "bid_system_status": r.campaign.bidding_strategy_system_status.name,
            "primary_status": r.campaign.primary_status.name,
            "primary_status_reasons": [x.name for x in
                                       r.campaign.primary_status_reasons],
            "budget_usd": usd(r.campaign_budget.amount_micros)}
    v["live_state"] = state
    v["ceiling_confirmed_both"] = all(
        s["ceiling_micros"] == 30_000_000 for s in state.values())

    # ---- 2. change_event re-query (lag test) ----
    lo = (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    hi = (now + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    ce = rows(svc, "SELECT change_event.change_date_time, "
                   "change_event.change_resource_type, "
                   "change_event.resource_change_operation, "
                   "change_event.changed_fields, "
                   "change_event.change_resource_name FROM change_event "
                   f"WHERE change_event.change_date_time >= '{lo}' "
                   f"AND change_event.change_date_time <= '{hi}' "
                   "ORDER BY change_event.change_date_time DESC LIMIT 20")
    v["change_events_last_2h"] = [
        {"when": e.change_event.change_date_time,
         "type": e.change_event.change_resource_type.name,
         "op": e.change_event.resource_change_operation.name,
         "fields": list(e.change_event.changed_fields.paths),
         "resource": e.change_event.change_resource_name.rsplit("/", 2)[-2:]}
        for e in ce]
    v["change_event_indexed"] = len(v["change_events_last_2h"]) > 0

    # ---- 3. what delivered today, per click ----
    q = ("SELECT campaign.id, ad_group.name, ad_group_criterion.keyword.text, "
         "ad_group_criterion.keyword.match_type, segments.date, "
         "metrics.clicks, metrics.cost_micros, metrics.average_cpc "
         f"FROM keyword_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date = '{today}' AND metrics.clicks > 0")
    today_clicks = [{"campaign": NAMES[str(r.campaign.id)],
                     "ad_group": r.ad_group.name,
                     "keyword": r.ad_group_criterion.keyword.text,
                     "match": r.ad_group_criterion.keyword.match_type.name,
                     "clicks": r.metrics.clicks,
                     "cost": usd(r.metrics.cost_micros),
                     "avg_cpc": usd(r.metrics.average_cpc)}
                    for r in rows(svc, q)]
    today_clicks.sort(key=lambda x: -x["cost"])
    v["today_clicks"] = today_clicks

    q = ("SELECT campaign.id, segments.hour, metrics.impressions, "
         "metrics.clicks, metrics.cost_micros FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) AND segments.date = '{today}'")
    hourly = {}
    for r in rows(svc, q):
        h = hourly.setdefault(int(r.segments.hour),
                              {"impressions": 0, "clicks": 0, "cost": 0.0})
        h["impressions"] += r.metrics.impressions
        h["clicks"] += r.metrics.clicks
        h["cost"] = round(h["cost"] + usd(r.metrics.cost_micros), 2)
    v["today_hourly"] = dict(sorted(hourly.items()))

    q = ("SELECT campaign.id, metrics.cost_micros, metrics.impressions, "
         "metrics.clicks, metrics.search_impression_share, "
         "metrics.search_budget_lost_impression_share, "
         "metrics.search_rank_lost_impression_share FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) AND segments.date = '{today}'")
    v["today_per_campaign"] = {
        NAMES[str(r.campaign.id)]: {
            "cost": usd(r.metrics.cost_micros),
            "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
            "is_pct": round((r.metrics.search_impression_share or 0) * 100, 2),
            "lost_is_budget_pct": round(
                (r.metrics.search_budget_lost_impression_share or 0) * 100, 2),
            "lost_is_rank_pct": round(
                (r.metrics.search_rank_lost_impression_share or 0) * 100, 2)}
        for r in rows(svc, q)}

    # ---- 4. search terms today ----
    q = ("SELECT campaign.id, search_term_view.search_term, metrics.impressions, "
         "metrics.clicks, metrics.cost_micros FROM search_term_view "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) AND segments.date = '{today}'")
    st = [{"campaign": NAMES[str(r.campaign.id)],
           "term": r.search_term_view.search_term,
           "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
           "cost": usd(r.metrics.cost_micros)} for r in rows(svc, q)]
    st.sort(key=lambda x: (-x["cost"], -x["impressions"]))
    v["today_search_terms"] = st

    OUT.write_text(json.dumps(v, indent=2), encoding="utf-8")

    print("POST-EXECUTION VERIFICATION  %s" % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 72)
    print("\n1. AUTHORITATIVE RESOURCE STATE")
    for cid_, s in state.items():
        print("   %-17s ceiling=$%s bidding=%s budget=$%s bid_status=%s"
              % (s["name"], s["ceiling_usd"], s["bidding"], s["budget_usd"],
                 s["bid_system_status"]))
        print("   %-17s primary=%s reasons=%s"
              % ("", s["primary_status"], s["primary_status_reasons"]))
    print("   CEILING CONFIRMED ON BOTH: %s" % v["ceiling_confirmed_both"])

    print("\n2. CHANGE_EVENT INDEXING (lag test)")
    print("   rows in last 2h: %d" % len(v["change_events_last_2h"]))
    for e in v["change_events_last_2h"]:
        print("     %s %-10s %-7s %s %s" % (e["when"], e["type"], e["op"],
                                            "/".join(e["resource"]), e["fields"]))

    print("\n3. TODAY'S DELIVERY (%s)" % today)
    for n, d in v["today_per_campaign"].items():
        print("   %-17s $%-8s %3di %2dc  IS=%s%% LostBud=%s%% LostRank=%s%%"
              % (n, d["cost"], d["impressions"], d["clicks"], d["is_pct"],
                 d["lost_is_budget_pct"], d["lost_is_rank_pct"]))
    print("   hourly:")
    for h, d in v["today_hourly"].items():
        print("     %02d:00  $%-8s %3di %2dc" % (h, d["cost"], d["impressions"],
                                                 d["clicks"]))
    print("   individual clicks today:")
    for c in today_clicks:
        flag = "  <-- >= $40" if c["avg_cpc"] >= 40 else ""
        print("     %-17s %-32s %-7s $%s%s"
              % (c["campaign"][:17], c["keyword"][:32], c["match"][:7],
                 c["avg_cpc"], flag))

    print("\n4. SEARCH TERMS TODAY")
    for s in st[:15]:
        print("     %-17s %-40s %2di %2dc $%s"
              % (s["campaign"][:17], s["term"][:40], s["impressions"],
                 s["clicks"], s["cost"]))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
