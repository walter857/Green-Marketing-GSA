#!/usr/bin/env python3
"""R2 - re-rank every paused in-scope ad group with FRESH Keyword Planner demand.

READ-ONLY. GenerateKeywordIdeas creates no plan resource. No mutation.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "rescue-inventory-ranking-2026-08-26.json"
GEOS = ["1022729", "1023035", "1023415", "1023482",
        "9051836", "9052792", "9198508", "9214462"]
A, B = "24103511039", "24145053510"

# Fresh CTR / CPC basis from the 2026-08-26 snapshot
OBS_CTR = 0.0571
OBS_CPC = 28.53
DAYS_LEFT = 6


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")

    deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
    snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
    met = json.loads((SNAP / "metrics-2026-08-25.json").read_text(encoding="utf-8"))
    lp_all = []
    for f in ("landing-pages-2026-08-25.json", "landing-pages-paused-skags-2026-08-25.json",
              "landing-pages-retry-2026-08-25.json"):
        lp_all += json.loads((SNAP / f).read_text(encoding="utf-8"))
    LP_OK = {r["requested_url"].split("?")[0] for r in lp_all
             if not r.get("error") and r.get("http_status") == 200}

    AG = snap["ad_groups"]
    live_texts = {k["text"] for k in snap["enabled_keywords_live"]}

    # group paused ad groups by name
    paused = defaultdict(lambda: {"texts": set(), "instances": []})
    for gid, g in AG.items():
        if g["status"] == "ENABLED":
            continue
        e = paused[g["name"]]
        e["instances"].append({"ad_group_id": gid, "campaign_id": g["campaign_id"]})
    for k in snap["keywords"]:
        g = AG[k["ad_group_id"]]
        if g["status"] != "ENABLED":
            paused[g["name"]]["texts"].add(k["text"])

    # fresh Planner for every paused text
    all_texts = sorted({t for e in paused.values() for t in e["texts"]})
    kp = client.get_service("KeywordPlanIdeaService")
    planner = {}
    for i in range(0, len(all_texts), 20):
        batch = all_texts[i:i + 20]
        req = client.get_type("GenerateKeywordIdeasRequest")
        req.customer_id = CID
        req.language = "languageConstants/1000"
        req.geo_target_constants.extend("geoTargetConstants/%s" % g for g in GEOS)
        req.include_adult_keywords = False
        req.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        req.keyword_seed.keywords.extend(batch)
        req.historical_metrics_options.year_month_range.start.year = 2025
        req.historical_metrics_options.year_month_range.start.month = (
            client.enums.MonthOfYearEnum.SEPTEMBER)
        req.historical_metrics_options.year_month_range.end.year = 2026
        req.historical_metrics_options.year_month_range.end.month = (
            client.enums.MonthOfYearEnum.AUGUST)
        want = {t.lower() for t in batch}
        try:
            for r in kp.generate_keyword_ideas(request=req):
                if r.text.lower() in want and r.text.lower() not in planner:
                    m = r.keyword_idea_metrics
                    months = [(v.year, enum_name(v.month), int(v.monthly_searches))
                              for v in m.monthly_search_volumes]
                    last3 = [x[2] for x in months[-3:]]
                    prev3 = [x[2] for x in months[-6:-3]]
                    trend = None
                    if prev3 and sum(prev3):
                        trend = round(100 * (sum(last3) - sum(prev3)) / sum(prev3), 1)
                    planner[r.text.lower()] = {
                        "avg_monthly_searches": int(m.avg_monthly_searches),
                        "competition": enum_name(m.competition),
                        "low_bid": (m.low_top_of_page_bid_micros / 1_000_000
                                    if m.low_top_of_page_bid_micros else None),
                        "high_bid": (m.high_top_of_page_bid_micros / 1_000_000
                                     if m.high_top_of_page_bid_micros else None),
                        "recent_trend_pct_last3_vs_prev3": trend,
                        "last_3_months": last3,
                    }
        except Exception as exc:
            print("  planner batch error:", str(exc)[:150], file=sys.stderr)

    st_hist = defaultdict(list)
    for s in met["search_terms"]:
        st_hist[s["ad_group"]].append(s)

    rows = []
    for name, e in paused.items():
        texts = sorted(e["texts"])
        best_text, best_vol = None, 0
        for t in texts:
            v = planner.get(t.lower(), {}).get("avg_monthly_searches", 0)
            if v > best_vol:
                best_vol, best_text = v, t
        bids = [planner[t.lower()]["high_bid"] for t in texts
                if planner.get(t.lower(), {}).get("high_bid")]
        lows = [planner[t.lower()]["low_bid"] for t in texts
                if planner.get(t.lower(), {}).get("low_bid")]
        overlap = sorted(t for t in texts if t in live_texts)

        # per-instance detail
        insts = []
        for inst in e["instances"]:
            gid = inst["ad_group_id"]
            ads = [a for a in deep["ads"] if a["ad_group_id"] == gid]
            kws = [k for k in snap["keywords"] if k["ad_group_id"] == gid]
            urls = sorted({u for a in ads for u in a["final_urls"]})
            insts.append({
                "campaign_id": inst["campaign_id"],
                "campaign": ("Power Washing" if inst["campaign_id"] == A
                             else "Power Washing #2"),
                "ad_group_id": gid,
                "phrase_keywords": sorted({k["text"] for k in kws
                                           if k["match_type"] == "PHRASE"}),
                "exact_keywords": sorted({k["text"] for k in kws
                                          if k["match_type"] == "EXACT"}),
                "keyword_rows": len(kws),
                "rsa_count": len(ads),
                "rsa_ad_status": sorted({a["status"] for a in ads}),
                "rsa_approval": sorted({a["approval_status"] for a in ads}),
                "rsa_strength": sorted({a["ad_strength"] for a in ads}),
                "final_urls": urls,
                "landing_page_200": all(u in LP_OK for u in urls) if urls else False,
            })

        hist = st_hist.get(name, [])
        # expected incremental delivery over the remaining 6 days
        daily_share = best_vol / 30.44 if best_vol else 0
        # current schedule reaches ~53% of the day; use that unless schedule changes
        inc_impr = round(daily_share * 0.531 * DAYS_LEFT, 1)
        inc_clicks = round(inc_impr * OBS_CTR, 2)
        inc_spend = round(inc_clicks * OBS_CPC, 2)

        # classification
        if overlap:
            cls = "DUPLICATE"
            why = ("Keyword text already live: %s. Enabling would put two ad groups "
                   "in the same auction for one query." % ", ".join(overlap))
        elif not all(i["landing_page_200"] for i in insts):
            cls = "LANDING PAGE MISMATCH"
            why = "A Final URL did not return HTTP 200 in the browser audit."
        elif best_vol >= 40:
            cls = "ENABLE AFTER QA"
            why = ("Best keyword '%s' carries %d local searches/month. Ad group, "
                   "keywords and RSAs already exist." % (best_text, best_vol))
        elif best_vol >= 10:
            cls = "KEEP PAUSED"
            why = ("Best keyword '%s' carries only %d local searches/month - real "
                   "intent, too thin to justify splitting the pool."
                   % (best_text, best_vol))
        else:
            cls = "LOW VOLUME"
            why = "No keyword reaches a reportable local volume bucket."

        # RSA quality gate can downgrade
        min_rsa = min(i["rsa_count"] for i in insts)
        if cls == "ENABLE AFTER QA" and min_rsa < 2:
            why += (" CAUTION: only %d RSA present, against the two-RSA SOP."
                    % min_rsa)

        rows.append({
            "ad_group_name": name, "classification": cls, "reason": why,
            "best_keyword": best_text, "best_keyword_local_monthly_volume": best_vol,
            "recent_trend_pct": (planner.get((best_text or "").lower(), {})
                                 .get("recent_trend_pct_last3_vs_prev3")),
            "top_of_page_low_min": min(lows) if lows else None,
            "top_of_page_high_max": max(bids) if bids else None,
            "distinct_texts": len(texts), "texts": texts,
            "overlaps_live_keyword": overlap,
            "instances": insts,
            "historical_impressions": sum(h["impressions"] for h in hist),
            "historical_clicks": sum(h["clicks"] for h in hist),
            "expected_incremental_impressions_6d": inc_impr,
            "expected_incremental_clicks_6d": inc_clicks,
            "expected_incremental_spend_6d": inc_spend,
            "planner_detail": {t: planner.get(t.lower()) for t in texts},
        })

    rows.sort(key=lambda r: (-r["best_keyword_local_monthly_volume"], r["ad_group_name"]))
    result = {
        "generated": "2026-08-26",
        "basis": {"observed_ctr": OBS_CTR, "observed_cpc": OBS_CPC,
                  "days_left": DAYS_LEFT,
                  "schedule_reach_fraction": 0.531,
                  "note": ("Incremental estimates assume the CURRENT Mon-Sat 08:00-18:00 "
                           "schedule. If PLAN-I3 opens the schedule they rise by roughly "
                           "the schedule uplift.")},
        "paused_ad_groups": len(rows),
        "distinct_paused_texts": len(all_texts),
        "rankings": rows,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("PAUSED AD GROUPS: %d   DISTINCT TEXTS: %d" % (len(rows), len(all_texts)))
    print()
    hdr = "%-36s %-22s %6s %8s %9s %7s %7s %8s" % (
        "AD GROUP", "CLASS", "VOL", "TREND", "BID HIGH", "+IMPR", "+CLK", "+SPEND")
    print(hdr); print("-" * len(hdr))
    for r in rows:
        print("%-36s %-22s %6d %7s%% %9s %7.1f %7.2f %8.2f"
              % (r["ad_group_name"][:36], r["classification"],
                 r["best_keyword_local_monthly_volume"],
                 r["recent_trend_pct"] if r["recent_trend_pct"] is not None else "  - ",
                 ("$%.2f" % r["top_of_page_high_max"]) if r["top_of_page_high_max"] else "-",
                 r["expected_incremental_impressions_6d"],
                 r["expected_incremental_clicks_6d"],
                 r["expected_incremental_spend_6d"]))
    print()
    print("ENABLE AFTER QA candidates:")
    for r in rows:
        if r["classification"] == "ENABLE AFTER QA":
            print("  %s  best='%s' vol=%d" % (r["ad_group_name"], r["best_keyword"],
                                              r["best_keyword_local_monthly_volume"]))
            for i in r["instances"]:
                print("     %s ag=%s rsas=%d %s %s url=%s"
                      % (i["campaign"], i["ad_group_id"], i["rsa_count"],
                         i["rsa_ad_status"], i["rsa_strength"], i["final_urls"]))
            print("     %s" % r["reason"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
