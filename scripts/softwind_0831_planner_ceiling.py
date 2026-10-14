#!/usr/bin/env python3
"""Keyword Planner CPC ranges for the CPC-ceiling decision.

A. Current approved service area  - the PRIMARY decision source.
B. New York State                 - secondary benchmark only.

Uses KeywordPlanIdeaService, which returns ideas without creating any keyword
plan resource. English, Google Search only. No mutation.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
LANG = "1000"          # English
NY_STATE = "21167"     # New York, United States

# Exactly the themes the brief names. No equipment, rental, DIY, employment or
# unrelated-service terms.
KEYWORDS = [
    "power washing near me",
    "power washing services near me",
    "power washing company near me",
    "power washing service",
    "pressure washing near me",
    "pressure washing services near me",
    "residential pressure washing near me",
    "house washing near me",
    "house washing company near me",
    "soft washing near me",
    "soft house washing near me",
    "driveway pressure washing near me",
    "patio pressure washing near me",
    "concrete pressure washing near me",
]

# The four Towns plus the six largest constituent places, all drawn from the live
# 80-target footprint. GenerateKeywordIdeas caps geo_target_constants at 10.
LOCAL_SAMPLE = ["9198508", "9214462", "9198487", "9220615",
                "1022719", "1022748", "1023090", "1023246",
                "1023323", "9051836"]


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("KeywordPlanIdeaService")
    now = datetime.now(ZoneInfo("America/New_York"))

    struct = sorted(SNAP.glob("forensic-structure-*.json"))[0]
    live_geos = sorted({
        c["geo_id"] for c in json.loads(struct.read_text(encoding="utf-8"))["campaign_criteria"]
        if c["type"] == "LOCATION" and not c["negative"]})
    sample = [g for g in LOCAL_SAMPLE if g in set(live_geos)][:10]

    def run(geos, label):
        req = client.get_type("GenerateKeywordIdeasRequest")
        req.customer_id = CID
        req.language = f"languageConstants/{LANG}"
        req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in geos])
        req.include_adult_keywords = False
        req.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        req.keyword_seed.keywords.extend(KEYWORDS[:20])
        wanted = {k.lower() for k in KEYWORDS}
        rows = {}
        for idea in svc.generate_keyword_ideas(request=req):
            if idea.text.lower() not in wanted:
                continue
            m = idea.keyword_idea_metrics
            months = [(v.year, enum_name(v.month), int(v.monthly_searches))
                      for v in m.monthly_search_volumes]
            trend = ""
            if len(months) >= 4:
                recent = sum(x[2] for x in months[-3:]) / 3
                prior = sum(x[2] for x in months[-6:-3]) / 3 if len(months) >= 6 else recent
                if prior:
                    pct = round(100 * (recent - prior) / prior, 1)
                    trend = f"{pct:+.1f}% last 3 mo vs prior 3"
                else:
                    trend = "no prior baseline"
            rows[idea.text.lower()] = {
                "keyword": idea.text,
                "avg_monthly_searches": int(m.avg_monthly_searches or 0),
                "competition": enum_name(m.competition),
                "competition_index": int(m.competition_index or 0),
                "top_of_page_low_usd": round(int(m.low_top_of_page_bid_micros or 0) / 1e6, 2),
                "top_of_page_high_usd": round(int(m.high_top_of_page_bid_micros or 0) / 1e6, 2),
                "trend": trend,
                "last_3_months": months[-3:],
            }
        print(f"  {label}: resolved {len(rows)} of {len(KEYWORDS)} requested keywords")
        return rows

    print("Running Keyword Planner")
    local = run(sample, "A. current approved service area")
    state = run([NY_STATE], "B. New York State benchmark")

    # Bucket collapse: Planner shares one volume bucket across synonyms.
    def buckets(rows):
        b = defaultdict(list)
        for r in rows.values():
            key = (r["avg_monthly_searches"], r["top_of_page_low_usd"], r["top_of_page_high_usd"])
            b[key].append(r["keyword"])
        return b

    out = {
        "generated_account_local": now.isoformat(),
        "mode": "READ-ONLY",
        "language": "English (1000)",
        "network": "GOOGLE_SEARCH",
        "primary_source": "A. current approved service area",
        "local_geo_sample_used": sample,
        "local_geo_live_total": len(live_geos),
        "local_geo_note": (
            "GenerateKeywordIdeas caps geo_target_constants at 10. The sample is the four "
            "Towns in the live footprint (North Hempstead, Babylon, Islip, Smithtown) plus "
            "the six largest constituent places, which between them contain most of the "
            "population of the 80 live targets."),
        "state_geo": NY_STATE,
        "bucket_note": (
            "Planner collapses synonyms into shared volume buckets. Keywords sharing an "
            "identical (volume, low, high) triple are ONE bucket of demand, not several."),
        "local": local,
        "new_york_state": state,
        "local_buckets": {str(k): v for k, v in buckets(local).items()},
        "state_buckets": {str(k): v for k, v in buckets(state).items()},
    }
    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    p = SNAP / f"planner-ceiling-{stamp}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    for label, rows in (("A. CURRENT APPROVED SERVICE AREA (PRIMARY)", local),
                        ("B. NEW YORK STATE (SECONDARY BENCHMARK ONLY)", state)):
        print(f"\n=== {label} ===")
        print(f"{'keyword':38s} {'vol':>6s} {'comp':>8s} {'idx':>4s} {'TOPlow':>7s} "
              f"{'TOPhigh':>8s}  {'>=$10?':>7s}  trend")
        for k in KEYWORDS:
            r = rows.get(k.lower())
            if not r:
                print(f"{k[:38]:38s} {'--':>6s} {'--':>8s} {'--':>4s} {'--':>7s} {'--':>8s}"
                      f"  {'--':>7s}  no reportable data")
                continue
            ok = "YES" if r["top_of_page_low_usd"] and r["top_of_page_low_usd"] <= 10 else "NO"
            if not r["top_of_page_low_usd"]:
                ok = "n/a"
            print(f"{r['keyword'][:38]:38s} {r['avg_monthly_searches']:6d} "
                  f"{r['competition'][:8]:>8s} {r['competition_index']:4d} "
                  f"{r['top_of_page_low_usd']:7.2f} {r['top_of_page_high_usd']:8.2f}"
                  f"  {ok:>7s}  {r['trend']}")

    print("\n=== SHARED VOLUME BUCKETS (local) - do not sum these as separate demand ===")
    for k, v in buckets(local).items():
        if len(v) > 1:
            print(f"  vol={k[0]:5d} low=${k[1]:6.2f} high=${k[2]:6.2f}  <- {v}")

    print(f"\nWROTE {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
