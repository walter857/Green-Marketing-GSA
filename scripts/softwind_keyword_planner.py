#!/usr/bin/env python3
"""Read-only Keyword Planner demand research for Softwind Power Washing.

Uses KeywordPlanIdeaService.GenerateKeywordIdeas, which returns ideas without
creating any keyword plan resource. No mutation of any kind.

Geo targeting mirrors the eight locations the live campaigns actually target,
so the volumes are local, never national.
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
OUT = ROOT / "clients/softwind-power-washing/snapshots/keyword-planner-2026-08-25.json"

# The eight geo target constants the live campaigns target, verified read-only.
GEOS = ["1022729", "1023035", "1023415", "1023482",
        "9051836", "9052792", "9198508", "9214462"]
LANG = "1000"  # English

SEEDS = [
    # in-scope service families only
    "power washing", "power wash", "powerwashing", "powerwash",
    "pressure washing", "pressure wash", "pressure washing service",
    "house washing", "house power washing", "house pressure washing",
    "soft washing", "soft wash house",
    "residential pressure washing", "exterior house washing",
    "driveway pressure washing", "driveway power washing",
    "patio pressure washing", "patio power washing",
    "concrete pressure washing", "concrete cleaning",
    "paver cleaning", "paver pressure washing",
    "siding washing", "deck pressure washing",
    "power washing company", "power washing services",
    "pressure washing company", "pressure washing companies",
    "power washing near me", "pressure washing near me",
    "power washing cost", "pressure washing estimate",
    "power washing quote", "exterior cleaning service",
]


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("KeywordPlanIdeaService")
    gtc = client.get_service("GeoTargetConstantService")

    out = {
        "customer_id": CID,
        "taken_account_local": datetime.now(TZ).isoformat(),
        "geo_targets": GEOS,
        "geo_note": "Exactly the 8 geo target constants the live campaigns target.",
        "language": LANG,
        "network": "GOOGLE_SEARCH",  # excludes Search Partners, matching campaign settings
        "seeds": SEEDS,
    }

    req = client.get_type("GenerateKeywordIdeasRequest")
    req.customer_id = CID
    req.language = "languageConstants/%s" % LANG
    req.geo_target_constants.extend("geoTargetConstants/%s" % g for g in GEOS)
    req.include_adult_keywords = False
    req.keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH)
    req.keyword_seed.keywords.extend(SEEDS)
    # 12 complete months ending with the last complete month before today.
    req.historical_metrics_options.year_month_range.start.year = 2025
    req.historical_metrics_options.year_month_range.start.month = (
        client.enums.MonthOfYearEnum.AUGUST)
    req.historical_metrics_options.year_month_range.end.year = 2026
    req.historical_metrics_options.year_month_range.end.month = (
        client.enums.MonthOfYearEnum.JULY)

    ideas = []
    seen = set()
    batches = [SEEDS[i:i + 20] for i in range(0, len(SEEDS), 20)]
    out["seed_batches"] = len(batches)
    rows = []
    for batch in batches:
        del req.keyword_seed.keywords[:]
        req.keyword_seed.keywords.extend(batch)
        try:
            rows.extend(list(svc.generate_keyword_ideas(request=req)))
        except Exception as exc:
            msg = str(exc)
            for mk in ("message: ", "FaultMessage: "):
                if mk in msg:
                    msg = msg.split(mk, 1)[1][:400]
                    break
            out.setdefault("errors", []).append(msg[:400])
            print("ERR batch:", msg[:200], file=sys.stderr)
    try:
        for r in rows:
            if r.text in seen:
                continue
            seen.add(r.text)
            m = r.keyword_idea_metrics
            monthly = [
                {"year": int(v.year), "month": enum_name(v.month),
                 "searches": int(v.monthly_searches)}
                for v in m.monthly_search_volumes
            ]
            ideas.append({
                "keyword": r.text,
                "avg_monthly_searches": int(m.avg_monthly_searches),
                "competition": enum_name(m.competition),
                "competition_index": int(m.competition_index),
                "low_top_of_page_bid": (m.low_top_of_page_bid_micros / 1_000_000
                                        if m.low_top_of_page_bid_micros else None),
                "high_top_of_page_bid": (m.high_top_of_page_bid_micros / 1_000_000
                                         if m.high_top_of_page_bid_micros else None),
                "monthly": monthly,
            })
    except Exception as exc:
        out["error"] = str(exc)[:400]
        print("ERROR:", str(exc)[:300], file=sys.stderr)

    ideas.sort(key=lambda x: -x["avg_monthly_searches"])
    out["ideas"] = ideas
    out["idea_count"] = len(ideas)
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote %s  (%d ideas)" % (OUT, len(ideas)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
