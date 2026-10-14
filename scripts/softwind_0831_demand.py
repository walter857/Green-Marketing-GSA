#!/usr/bin/env python3
"""Softwind Power Washing - 2026-08-31 local demand read (READ-ONLY).

KeywordPlanIdeaService.GenerateKeywordIdeas returns ideas without creating any
keyword plan resource. Geo mirrors the 80 locations the live campaigns actually
target today, so the volumes are local, never national.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
TZ = ZoneInfo("America/New_York")
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
LANG = "1000"

SEEDS = [
    "power washing near me", "pressure washing near me",
    "power washing services near me", "power washing company near me",
    "power washing services", "pressure washing services",
    "residential pressure washing near me", "house pressure washing estimate",
    "house washing near me", "soft washing near me",
    "driveway pressure washing near me", "patio pressure washing near me",
    "power washing long island", "pressure washing long island",
    "power wash near me", "house power washing", "exterior house washing",
    "concrete pressure washing", "deck pressure washing", "siding washing",
    "power washing quote", "pressure washing estimate", "power washing cost",
    "jet wash near me", "exterior cleaning service near me",
]


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("KeywordPlanIdeaService")
    now = datetime.now(TZ)

    struct = sorted(SNAP.glob("forensic-structure-*.json"))[-1]
    st = json.loads(struct.read_text(encoding="utf-8"))
    geos = sorted({
        c["geo_id"] for c in st["campaign_criteria"]
        if c["type"] == "LOCATION" and not c["negative"]
    })

    req = client.get_type("GenerateKeywordIdeasRequest")
    req.customer_id = CID
    req.language = f"languageConstants/{LANG}"
    # KeywordPlanIdeaService accepts at most 10 geo targets. Use the four
    # Towns plus the six largest constituent places so the sample represents
    # the whole 80-target footprint rather than one corner of it.
    REPRESENTATIVE = ["9198508", "9214462", "9198487", "9220615",
                      "1022719", "1022748", "1023090", "1023246",
                      "1023323", "9051836"]
    sample = [g for g in REPRESENTATIVE if g in set(geos)][:10]
    req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in sample])
    req.include_adult_keywords = False
    req.keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    )
    # GenerateKeywordIdeas caps the keyword seed at 20 terms.
    req.keyword_seed.keywords.extend(SEEDS[:20])

    rows = []
    for idea in svc.generate_keyword_ideas(request=req):
        m = idea.keyword_idea_metrics
        rows.append({
            "text": idea.text,
            "avg_monthly_searches": int(m.avg_monthly_searches or 0),
            "competition": enum_name(m.competition),
            "competition_index": int(m.competition_index or 0),
            "low_top_of_page_bid": round(int(m.low_top_of_page_bid_micros or 0) / 1e6, 2),
            "high_top_of_page_bid": round(int(m.high_top_of_page_bid_micros or 0) / 1e6, 2),
            "monthly": [
                {"y": v.year, "m": enum_name(v.month), "n": int(v.monthly_searches)}
                for v in m.monthly_search_volumes
            ][-14:],
        })

    out = {
        "meta": {
            "generated_account_local": now.isoformat(),
            "geo_target_count_live": len(geos),
            "geo_sample_used": sample,
            "geo_targets": geos,
            "language": LANG,
            "network": "GOOGLE_SEARCH",
            "seeds": SEEDS,
            "mode": "READ-ONLY",
            "note": (
                "Planner collapses synonyms into shared volume buckets. "
                "Summing raw rows overstates demand; dedupe by bucket before "
                "modelling a market ceiling."
            ),
        },
        "ideas": rows,
    }
    p = SNAP / f"forensic-demand-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"WROTE {p}  ideas={len(rows)}  geos={len(geos)}")

    seen = set()
    print(f"\n{'keyword':46s} {'vol':>6s} {'comp':>10s} {'idx':>4s} {'lowTOP':>7s} {'highTOP':>8s}")
    for r in sorted(rows, key=lambda x: -x["avg_monthly_searches"])[:60]:
        key = (r["avg_monthly_searches"], r["low_top_of_page_bid"], r["high_top_of_page_bid"])
        dup = "  <-same bucket" if key in seen else ""
        seen.add(key)
        print(f"{r['text'][:46]:46s} {r['avg_monthly_searches']:6d} "
              f"{r['competition'][:10]:>10s} {r['competition_index']:4d} "
              f"{r['low_top_of_page_bid']:7.2f} {r['high_top_of_page_bid']:8.2f}{dup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
