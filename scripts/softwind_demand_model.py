#!/usr/bin/env python3
"""Local BOFU demand model for Softwind Power Washing.

Keyword Planner groups semantically identical phrasings into one shared volume
bucket (e.g. 'power washing near me', 'pressure washing services near me' and
'power washing companies near me' all return 110). Summing raw rows therefore
overstates demand badly. This script collapses each bucket to a single
representative before any total is taken, then classifies intent.

Local only, read-only, no API calls: it reads the saved Keyword Planner snapshot.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "demand-model-2026-08-25.json"

# --- intent classifiers -------------------------------------------------
EQUIPMENT = re.compile(
    r"\b(karcher|ryobi|simpson|dewalt|greenworks|green works|sun ?joe|snow joe|"
    r"honda|craftsman|westinghouse|generac|ridgid|makita|milwaukee|ego|"
    r"home ?depot|lowe'?s|lowes|harbor freight|costco|walmart|menards|amazon|"
    r"psi|gpm|nozzle|hose|pump|wand|surface cleaner|sidewalk cleaner|"
    r"cordless|battery|portable|electric|gas(oline)? ?power|hot water|"
    r"wall mounted|attachment|tips?|soap|detergent|chemical|bleach|"
    r"for sale|buy|used|rental|rent|parts|repair|manual|review|best |good |"
    r"cheap(est)? |top rated|vs\b|which |brand)", re.I)
JOBS_RESEARCH = re.compile(
    r"\b(job|jobs|career|salary|hiring|hire me|employment|resume|"
    r"training|course|certification|school|class|"
    r"business|start(ing)? a|llc|insurance|license|licensing|software|"
    r"flyer|logo|invoice|contract template|marketing|leads|seo|website|"
    r"how to|diy|tutorial|youtube|reddit|meaning|definition|what is|wikipedia)", re.I)
OUT_OF_SCOPE_SERVICE = re.compile(
    r"\b(roof|gutter|chimney|dryer vent|window|carpet|solar|"
    r"boat|car|truck|auto|vehicle|fleet|rv\b|trailer|"
    r"graffiti|dumpster|kitchen hood|restaurant|parking lot|"
    r"tank|mold|paint(ing|er)?|seal(ing|er|ant)|stain(ing)?|"
    r"tree|lawn|landscap|masonry|snow|christmas|"
    r"apartment|office|commercial|industrial|warehouse|"
    r"grave ?stone|headstone|monument|pool deck resurfac)", re.I)
SERVICE_INTENT = re.compile(
    r"\b(near me|near by|nearby|company|companies|service|services|contractor|"
    r"pro|professional|quote|estimate|cost|price|pricing|hire|local|"
    r"residential|house|home|siding|driveway|patio|deck|fence|paver|concrete|"
    r"walkway|sidewalk|porch|exterior|my house|my home|your house|your home)",
    re.I)
CORE = re.compile(
    r"(power\s*wash|pressure\s*wash|powerwash|soft\s*wash|house\s*wash|"
    r"exterior\s*clean|paver\s*clean|concrete\s*clean|driveway\s*clean|"
    r"patio\s*clean|siding\s*clean|deck\s*clean)", re.I)
CITY = re.compile(
    r"\b(islip|west islip|dix hills|babylon|bellmore|syosset|salisbury|"
    r"north hempstead|huntington|massapequa|deer park|lindenhurst|copiague|"
    r"bay shore|brentwood|commack|smithtown|hauppauge|farmingdale|amityville|"
    r"long island|suffolk|nassau|westbury|manhasset|roslyn|great neck)", re.I)


def classify(kw: str) -> str:
    if JOBS_RESEARCH.search(kw):
        return "JOBS_OR_RESEARCH"
    if EQUIPMENT.search(kw):
        return "EQUIPMENT_OR_PRODUCT"
    if not CORE.search(kw):
        return "NOT_CORE_SERVICE"
    if OUT_OF_SCOPE_SERVICE.search(kw):
        return "OUT_OF_SCOPE_SERVICE"
    if SERVICE_INTENT.search(kw):
        return "BOFU_SERVICE"
    return "GENERIC_CORE"


def main() -> int:
    data = json.loads((SNAP / "keyword-planner-2026-08-25.json").read_text(encoding="utf-8"))
    ideas = [i for i in data["ideas"] if i["avg_monthly_searches"] > 0]

    # Collapse Planner volume buckets. Rows sharing identical volume + both bid
    # estimates + competition index are the same underlying bucket.
    buckets = defaultdict(list)
    for i in ideas:
        key = (i["avg_monthly_searches"], i["competition_index"],
               round(i["low_top_of_page_bid"] or -1, 4),
               round(i["high_top_of_page_bid"] or -1, 4))
        buckets[key].append(i)

    collapsed = []
    for key, members in buckets.items():
        members.sort(key=lambda m: (classify(m["keyword"]) != "BOFU_SERVICE",
                                    len(m["keyword"])))
        rep = members[0]
        # A bucket counts as BOFU if any phrasing in it is BOFU service intent.
        cats = {classify(m["keyword"]) for m in members}
        cat = ("BOFU_SERVICE" if "BOFU_SERVICE" in cats
               else "GENERIC_CORE" if "GENERIC_CORE" in cats
               else sorted(cats)[0])
        collapsed.append({
            "representative": rep["keyword"],
            "variants": len(members),
            "sample_variants": [m["keyword"] for m in members[:6]],
            "avg_monthly_searches": rep["avg_monthly_searches"],
            "competition": rep["competition"],
            "competition_index": rep["competition_index"],
            "low_top_of_page_bid": rep["low_top_of_page_bid"],
            "high_top_of_page_bid": rep["high_top_of_page_bid"],
            "category": cat,
            "has_city": bool(CITY.search(" ".join(m["keyword"] for m in members))),
            "monthly": rep["monthly"],
        })

    collapsed.sort(key=lambda x: -x["avg_monthly_searches"])

    totals = defaultdict(lambda: {"buckets": 0, "monthly_searches": 0})
    for c in collapsed:
        t = totals[c["category"]]
        t["buckets"] += 1
        t["monthly_searches"] += c["avg_monthly_searches"]

    bofu = [c for c in collapsed if c["category"] == "BOFU_SERVICE"]
    generic = [c for c in collapsed if c["category"] == "GENERIC_CORE"]

    bofu_total = sum(c["avg_monthly_searches"] for c in bofu)
    generic_total = sum(c["avg_monthly_searches"] for c in generic)

    # Bid evidence from the BOFU buckets that carry bid estimates.
    bids_low = [c["low_top_of_page_bid"] for c in bofu if c["low_top_of_page_bid"]]
    bids_high = [c["high_top_of_page_bid"] for c in bofu if c["high_top_of_page_bid"]]

    # Weight bids by volume so the head terms dominate, as they do in the auction.
    wl = sum((c["low_top_of_page_bid"] or 0) * c["avg_monthly_searches"] for c in bofu)
    wh = sum((c["high_top_of_page_bid"] or 0) * c["avg_monthly_searches"] for c in bofu)
    wv = sum(c["avg_monthly_searches"] for c in bofu
             if c["low_top_of_page_bid"] or c["high_top_of_page_bid"])

    # Seasonality of the single largest BOFU bucket family, month by month.
    season = {}
    for c in bofu[:6]:
        season[c["representative"]] = c["monthly"]

    out = {
        "note": ("Volumes are Keyword Planner averages for exactly the 8 geo targets "
                 "the live campaigns use. Buckets are collapsed before summing."),
        "category_totals": dict(totals),
        "bofu_bucket_count": len(bofu),
        "bofu_monthly_searches": bofu_total,
        "generic_core_monthly_searches": generic_total,
        "bofu_plus_generic_monthly_searches": bofu_total + generic_total,
        "bid_evidence": {
            "bofu_low_top_of_page_min": min(bids_low) if bids_low else None,
            "bofu_low_top_of_page_max": max(bids_low) if bids_low else None,
            "bofu_high_top_of_page_min": min(bids_high) if bids_high else None,
            "bofu_high_top_of_page_max": max(bids_high) if bids_high else None,
            "volume_weighted_low_top_of_page": round(wl / wv, 2) if wv else None,
            "volume_weighted_high_top_of_page": round(wh / wv, 2) if wv else None,
        },
        "top_bofu_buckets": bofu[:60],
        "top_generic_buckets": generic[:20],
        "seasonality_top_bofu": season,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("CATEGORY TOTALS (collapsed buckets)")
    for k, v in sorted(totals.items(), key=lambda x: -x[1]["monthly_searches"]):
        print("  %-22s buckets=%-5d monthly_searches=%d"
              % (k, v["buckets"], v["monthly_searches"]))
    print()
    print("BOFU service monthly searches (local, 8 cities): %d" % bofu_total)
    print("Generic core monthly searches:                   %d" % generic_total)
    print("Combined:                                        %d" % (bofu_total + generic_total))
    print()
    print("BID EVIDENCE (BOFU buckets)")
    for k, v in out["bid_evidence"].items():
        print("  %-38s %s" % (k, v))
    print()
    print("TOP 40 BOFU BUCKETS")
    print("%9s %6s %5s %8s %8s  %s" % ("searches", "comp", "vars", "bidLow", "bidHigh",
                                       "representative"))
    for c in bofu[:40]:
        print("%9d %6s %5d %8s %8s  %s"
              % (c["avg_monthly_searches"], c["competition"][:6], c["variants"],
                 ("%.2f" % c["low_top_of_page_bid"]) if c["low_top_of_page_bid"] else "-",
                 ("%.2f" % c["high_top_of_page_bid"]) if c["high_top_of_page_bid"] else "-",
                 c["representative"]))
    print()
    print("TOP GENERIC CORE BUCKETS")
    for c in generic[:12]:
        print("%9d %6s %5d  %s | variants: %s"
              % (c["avg_monthly_searches"], c["competition"][:6], c["variants"],
                 c["representative"], ", ".join(c["sample_variants"][:4])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
