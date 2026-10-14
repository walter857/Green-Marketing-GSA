#!/usr/bin/env python3
"""R4 - service-area opportunity research. READ-ONLY.

Reads Softwind's published service-area page as RESEARCH EVIDENCE ONLY (a page
listing a town is not proof the client serves it for power washing), resolves
candidate geo target constants, and measures incremental local BOFU demand with
Keyword Planner.

No geo change is proposed. Nothing enters an executable fingerprint.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name
from playwright.sync_api import sync_playwright

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "geo-opportunity-2026-08-26.json"

CURRENT = ["1022729", "1023035", "1023415", "1023482",
           "9051836", "9052792", "9198508", "9214462"]

# Head BOFU seeds used consistently so the two geo sets are comparable.
SEEDS = ["power washing near me", "pressure washing near me", "power washing service",
         "pressure washing service", "power washing company", "house washing near me",
         "power washing long island", "soft washing near me",
         "driveway pressure washing near me", "patio pressure washing near me"]

# Candidate expansions. Towns (municipalities) that CONTAIN the currently
# targeted hamlets, plus the adjacent towns in the same corridor.
CANDIDATE_NAMES = [
    "Islip, New York", "Huntington, New York", "Oyster Bay, New York",
    "Hempstead, New York", "Smithtown, New York", "Brookhaven, New York",
    "Bay Shore, New York", "Massapequa, New York", "Commack, New York",
    "Farmingdale, New York", "Deer Park, New York", "Lindenhurst, New York",
    "Amityville, New York", "Hauppauge, New York", "Brentwood, New York",
    "Melville, New York", "Northport, New York", "Bethpage, New York",
]


def scrape_service_areas():
    rec = {"url": "https://softwindli.com/service-areas/", "towns_mentioned": [],
           "note": "RESEARCH EVIDENCE ONLY. A town on a marketing page is not proof "
                   "the client serves it for Power Washing."}
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True,
                                   args=["--disable-blink-features=AutomationControlled"])
            ctx = b.new_context(viewport={"width": 1440, "height": 900},
                                locale="en-US", timezone_id="America/New_York")
            page = ctx.new_page()
            for _ in range(4):
                try:
                    r = page.goto(rec["url"], wait_until="domcontentloaded", timeout=60000)
                except Exception:
                    time.sleep(6); continue
                if "sgcaptcha" in page.url or (r and r.status in (202, 403, 429)):
                    try:
                        page.wait_for_url(lambda u: "sgcaptcha" not in u, timeout=45000)
                    except Exception:
                        pass
                    time.sleep(8)
                if "sgcaptcha" not in page.url:
                    break
            try:
                page.wait_for_load_state("networkidle", timeout=25000)
            except Exception:
                pass
            text = page.inner_text("body")
            rec["http_status"] = r.status if r else None
            rec["body_chars"] = len(text)
            # Long Island town/hamlet names appearing on the page
            known = ["Islip", "West Islip", "East Islip", "Central Islip", "Dix Hills",
                     "Huntington", "Babylon", "West Babylon", "North Babylon",
                     "Bay Shore", "Brentwood", "Commack", "Deer Park", "Bethpage",
                     "Massapequa", "Farmingdale", "Lindenhurst", "Amityville",
                     "Copiague", "Hauppauge", "Smithtown", "Melville", "Northport",
                     "Bellmore", "Syosset", "Salisbury", "Hempstead", "Oyster Bay",
                     "Brookhaven", "Wantagh", "Seaford", "Merrick", "Wyandanch",
                     "Islandia", "Ronkonkoma", "Holbrook", "Sayville", "Patchogue"]
            found = sorted({k for k in known
                            if re.search(r"\b%s\b" % re.escape(k), text, re.I)})
            rec["towns_mentioned"] = found
            rec["sample_text"] = text[:1200]
            ctx.close(); b.close()
    except Exception as exc:
        rec["error"] = str(exc)[:200]
    return rec


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    gts = client.get_service("GeoTargetConstantService")
    kp = client.get_service("KeywordPlanIdeaService")

    out = {"generated": "2026-08-26",
           "rule": ("NO GEO CHANGE IS PROPOSED. Every candidate below is marked "
                    "NEEDS WALTER CONFIRMATION and none enters an executable "
                    "fingerprint.")}

    out["published_service_area_page"] = scrape_service_areas()

    # resolve current targets
    def resolve_ids(ids):
        res = {}
        cond = ",".join("'geoTargetConstants/%s'" % i for i in ids)
        for row in svc.search(customer_id=CID, query="""
            SELECT geo_target_constant.id, geo_target_constant.name,
                   geo_target_constant.canonical_name,
                   geo_target_constant.target_type, geo_target_constant.status
            FROM geo_target_constant
            WHERE geo_target_constant.resource_name IN (%s)""" % cond):
            g = row.geo_target_constant
            res[str(g.id)] = {"id": str(g.id), "name": g.name,
                              "canonical_name": g.canonical_name,
                              "target_type": g.target_type,
                              "status": enum_name(g.status)}
        return res
    out["current_targets"] = resolve_ids(CURRENT)

    # suggest candidate geo constants by name
    req = client.get_type("SuggestGeoTargetConstantsRequest")
    req.locale = "en"
    req.country_code = "US"
    req.location_names.names.extend(CANDIDATE_NAMES)
    cands = []
    try:
        resp = gts.suggest_geo_target_constants(request=req)
        for s in resp.geo_target_constant_suggestions:
            g = s.geo_target_constant
            cands.append({
                "search_term": s.search_term,
                "geo_target_constant_id": str(g.id),
                "name": g.name,
                "canonical_name": g.canonical_name,
                "target_type": g.target_type,
                "status": enum_name(g.status),
                "reach": int(s.reach) if s.reach else None,
            })
    except Exception as exc:
        out["suggest_error"] = str(exc)[:300]
    # keep only NY results, dedupe, drop anything already targeted
    seen = set()
    filtered = []
    for c in cands:
        if ",New York," not in c["canonical_name"]:
            continue
        if c["geo_target_constant_id"] in CURRENT:
            c["already_targeted"] = True
        key = c["geo_target_constant_id"]
        if key in seen:
            continue
        seen.add(key)
        filtered.append(c)
    filtered.sort(key=lambda x: -(x.get("reach") or 0))
    out["candidate_geo_constants"] = filtered

    # Planner demand: current geo vs current + candidates
    def planner_total(geo_ids, label):
        req2 = client.get_type("GenerateKeywordIdeasRequest")
        req2.customer_id = CID
        req2.language = "languageConstants/1000"
        req2.geo_target_constants.extend("geoTargetConstants/%s" % g for g in geo_ids)
        req2.include_adult_keywords = False
        req2.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        req2.keyword_seed.keywords.extend(SEEDS)
        want = {t.lower() for t in SEEDS}
        rows = {}
        try:
            for r in kp.generate_keyword_ideas(request=req2):
                if r.text.lower() in want:
                    m = r.keyword_idea_metrics
                    rows[r.text.lower()] = {
                        "avg_monthly_searches": int(m.avg_monthly_searches),
                        "competition": enum_name(m.competition),
                        "low_bid": (m.low_top_of_page_bid_micros / 1_000_000
                                    if m.low_top_of_page_bid_micros else None),
                        "high_bid": (m.high_top_of_page_bid_micros / 1_000_000
                                     if m.high_top_of_page_bid_micros else None)}
        except Exception as exc:
            rows["__error__"] = str(exc)[:200]
        # collapse shared buckets before summing
        buckets = {}
        for k, v in rows.items():
            if k == "__error__":
                continue
            key = (v["avg_monthly_searches"], v["low_bid"], v["high_bid"])
            buckets.setdefault(key, []).append(k)
        total = sum(k[0] for k in buckets)
        return {"label": label, "geo_count": len(geo_ids), "per_seed": rows,
                "collapsed_buckets": len(buckets),
                "distinct_monthly_searches": total}

    base = planner_total(CURRENT, "current 8 targets")
    out["demand_current_geo"] = base

    # top expansion candidates by reach, excluding already-targeted
    top = [c for c in filtered if not c.get("already_targeted")][:8]
    out["expansion_tested"] = [c["canonical_name"] for c in top]
    exp_ids = CURRENT + [c["geo_target_constant_id"] for c in top]
    expanded = planner_total(exp_ids, "current 8 + top expansion candidates")
    out["demand_expanded_geo"] = expanded

    delta = expanded["distinct_monthly_searches"] - base["distinct_monthly_searches"]
    out["incremental_demand"] = {
        "current_distinct_monthly": base["distinct_monthly_searches"],
        "expanded_distinct_monthly": expanded["distinct_monthly_searches"],
        "incremental_monthly": delta,
        "multiplier": (round(expanded["distinct_monthly_searches"]
                             / base["distinct_monthly_searches"], 2)
                       if base["distinct_monthly_searches"] else None),
        "incremental_per_day": round(delta / 30.44, 1),
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("PUBLISHED SERVICE-AREA PAGE (research evidence only)")
    sa = out["published_service_area_page"]
    print("  status=%s  towns mentioned: %s" % (sa.get("http_status"),
                                                sa.get("towns_mentioned")))
    print()
    print("CURRENT TARGETS")
    for g in out["current_targets"].values():
        print("   %-10s %-12s %s" % (g["id"], g["target_type"], g["canonical_name"]))
    print()
    print("CANDIDATE GEO CONSTANTS (top 15 by reach)")
    for c in filtered[:15]:
        print("   %-10s %-12s reach=%-10s %s%s"
              % (c["geo_target_constant_id"], c["target_type"],
                 c.get("reach"), c["canonical_name"],
                 "   [ALREADY TARGETED]" if c.get("already_targeted") else ""))
    print()
    print("DEMAND COMPARISON (same 10 BOFU seeds, buckets collapsed)")
    print("   current 8 targets : %d distinct monthly searches (%d buckets)"
          % (base["distinct_monthly_searches"], base["collapsed_buckets"]))
    print("   expanded          : %d distinct monthly searches (%d buckets)"
          % (expanded["distinct_monthly_searches"], expanded["collapsed_buckets"]))
    print("   incremental       : %s/month  (x%s)  = %s/day"
          % (out["incremental_demand"]["incremental_monthly"],
             out["incremental_demand"]["multiplier"],
             out["incremental_demand"]["incremental_per_day"]))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
