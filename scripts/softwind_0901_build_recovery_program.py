#!/usr/bin/env python3
"""Build the Softwind complete recovery program artifacts.

Generates the authoritative keyword inventory, RSA copy + QA, keyword/ad/page map,
routing-negative matrix, and the recovery manifest. Validates every constraint
programmatically: keyword ownership uniqueness, RSA character limits, duplicate
and near-duplicate headlines, routing-negative self-block collisions, and object
counts.

Pure local build. No Google Ads call of any kind.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.safety import approval_code  # noqa: E402

AUD = ROOT / "clients/softwind-power-washing/audits"
PLN = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
CID = "1521725229"
CAMP = "24103511039"
BASE = "https://offer.softwindli.com"

# ---------------------------------------------------------------- architecture
# Every group already EXISTS inside the surviving campaign 24103511039.
GROUPS = {
    "Power Washing": {
        "ad_group_id": "202870585390",
        "current_name": "Power Washing Near Me",
        "current_status": "ENABLED",
        "page": f"{BASE}/power-washing-services-islip-west-islip-dix-hills/",
        "texts": ["power washing", "power washing near me", "power washing service",
                  "power washing services near me", "power washing company near me"],
        "existing": [("power washing near me", "PHRASE"), ("power washing near me", "EXACT")],
        "p1": "power-washing", "p2": "free-quote",
    },
    "Pressure Washing": {
        "ad_group_id": "202870585870",
        "current_name": "Residential Pressure Washing Near Me",
        "current_status": "PAUSED",
        "page": f"{BASE}/residential-pressure-washing/",
        "texts": ["pressure washing", "pressure washing near me",
                  "residential pressure washing near me"],
        "existing": [("residential pressure washing near me", "PHRASE"),
                     ("residential pressure washing near me", "EXACT")],
        "p1": "pressure-wash", "p2": "residential",
    },
    "House Washing": {
        "ad_group_id": "202870585910",
        "current_name": "House Washing Company Near Me",
        "current_status": "PAUSED",
        "page": f"{BASE}/house-washing-company/",
        "texts": ["house washing near me", "house pressure washing near me",
                  "house power washing near me", "exterior house washing near me"],
        "existing": [],
        "p1": "house-washing", "p2": "free-quote",
    },
    "Soft Washing": {
        "ad_group_id": "202870586310",
        "current_name": "Soft House Washing Near Me",
        "current_status": "PAUSED",
        "page": f"{BASE}/soft-house-washing/",
        "texts": ["soft house washing near me", "soft washing near me"],
        "existing": [("soft house washing near me", "PHRASE"),
                     ("soft house washing near me", "EXACT")],
        "p1": "soft-washing", "p2": "house-washing",
    },
    "Driveway Pressure Washing": {
        "ad_group_id": "202870586110",
        "current_name": "Driveway Pressure Washing Near Me",
        "current_status": "PAUSED",
        "page": f"{BASE}/driveway-pressure-washing/",
        "texts": ["driveway pressure washing near me", "driveway power washing near me"],
        "existing": [("driveway pressure washing near me", "PHRASE"),
                     ("driveway pressure washing near me", "EXACT")],
        "p1": "driveway", "p2": "pressure-wash",
    },
    "Patio Pressure Washing": {
        "ad_group_id": "202870586150",
        "current_name": "Patio Pressure Washing Near Me",
        "current_status": "PAUSED",
        "page": f"{BASE}/patio-power-washing/",
        "texts": ["patio pressure washing near me", "patio power washing near me",
                  "concrete pressure washing near me"],
        "existing": [("patio pressure washing near me", "PHRASE"),
                     ("patio pressure washing near me", "EXACT")],
        "p1": "patio", "p2": "pressure-wash",
    },
}

# Local Keyword Planner evidence, 80-target footprint (planner-architecture-2026-08-31.json)
DEMAND = {
    "power washing": (880, "HIGH", 0.58, 14.31, "+58%"),
    "power washing near me": (260, "HIGH", 10.90, 28.32, "+22%"),
    "power washing service": (140, "LOW", 11.55, 23.34, "+131%"),
    "power washing services near me": (30, "HIGH", 10.62, 28.70, "-20%"),
    "power washing company near me": (260, "HIGH", 10.90, 28.32, "+22%"),
    "pressure washing": (480, "HIGH", 0.30, 10.77, "+26%"),
    "pressure washing near me": (90, "MEDIUM", 8.75, 24.66, "-44%"),
    "residential pressure washing near me": (20, "LOW", 0.0, 0.0, "-53%"),
    "house washing near me": (40, "MEDIUM", 10.46, 24.75, "-53%"),
    "house pressure washing near me": (20, "HIGH", 13.49, 32.86, "+0%"),
    "house power washing near me": (20, "HIGH", 13.49, 32.86, "+0%"),
    "exterior house washing near me": (10, "HIGH", 0.0, 0.0, "n/a"),
    "soft washing near me": (10, "HIGH", 15.09, 41.58, "-40%"),
    "soft house washing near me": (10, "HIGH", 0.0, 0.0, "+200%"),
    "driveway pressure washing near me": (10, "UNSPECIFIED", 0.0, 0.0, "+100%"),
    "driveway power washing near me": (10, "UNSPECIFIED", 0.0, 0.0, "+100%"),
    "patio pressure washing near me": (0, "UNSPECIFIED", 0.0, 0.0, "n/a"),
    "patio power washing near me": (10, "MEDIUM", 0.0, 0.0, "n/a"),
    "concrete pressure washing near me": (0, "UNSPECIFIED", 0.0, 0.0, "n/a"),
}
# Texts sharing one Planner volume bucket with an owned text -> volume counted once.
SHARED_BUCKET = {
    "power washing company near me": "power washing near me",
    "house power washing near me": "house pressure washing near me",
    "soft house washing near me": "soft washing near me",
    "driveway power washing near me": "driveway pressure washing near me",
}
# Live keyword-level Quality Score evidence, read 2026-09-01.
QS = {
    ("power washing near me", "EXACT"): (2, "BELOW_AVERAGE", "AVERAGE", "BELOW_AVERAGE"),
    ("power washing near me", "PHRASE"): (2, "BELOW_AVERAGE", "AVERAGE", "BELOW_AVERAGE"),
    ("power washing services near me", "EXACT"): (3, "BELOW_AVERAGE", "ABOVE_AVERAGE",
                                                  "BELOW_AVERAGE"),
    ("power washing services near me", "PHRASE"): (3, "BELOW_AVERAGE", "ABOVE_AVERAGE",
                                                   "BELOW_AVERAGE"),
}
HIST = {  # all-time impressions / clicks / cost against the text, campaign 24103511039
    "power washing near me": (95, 8, 317.57),
    "power washing services near me": (104, 4, 109.31),
    "power washing company near me": (16, 0, 0.0),
    "residential pressure washing near me": (6, 0, 0.0),
    "house pressure washing estimate": (3, 0, 0.0),
    "power washing service": (3, 0, 0.0),
    "house washing company near me": (2, 0, 0.0),
}

# Texts reviewed and DEFERRED or REMOVED from the launch inventory.
REJECTED = [
    ("power washing services", "Power Washing", "REMOVE - bucket collapse",
     "Plural of `power washing service`; same 140/mo Planner bucket. Phrase `power washing "
     "service` already matches it."),
    ("pressure washing services", "Pressure Washing", "REMOVE - bucket collapse",
     "Same 140/mo bucket as `power washing service`, already owned in Power Washing."),
    ("pressure washing service", "Pressure Washing", "REMOVE - bucket collapse",
     "Shares the 140/mo bucket with `power washing service`. Adding both double-counts demand "
     "and creates sibling self-competition."),
    ("pressure washing services near me", "Pressure Washing", "REMOVE - bucket collapse",
     "Shares the 260/mo bucket with `power washing near me`. Google collapses power/pressure."),
    ("pressure washing company near me", "Pressure Washing", "REMOVE - bucket collapse",
     "20/mo, same bucket as `residential pressure washing near me`."),
    ("local power washing", "Power Washing", "REMOVE - covered",
     "No reportable local volume. Phrase `power washing` matches it."),
    ("power washing quote", "Power Washing", "REMOVE - covered, do NOT negative",
     "10/mo. Phrase `power washing` matches it. BOFU intent - never added as a negative."),
    ("power washing estimate", "Power Washing", "REMOVE - covered, do NOT negative",
     "No reportable volume. Phrase `power washing` matches it. BOFU - never negatived."),
    ("pressure washing quote", "Pressure Washing", "REMOVE - covered, do NOT negative",
     "Phrase `pressure washing` matches it. BOFU - never negatived."),
    ("pressure washing estimate", "Pressure Washing", "REMOVE - covered, do NOT negative",
     "Phrase `pressure washing` matches it. The `estimate` token skews to cost research, but it "
     "is BOFU-adjacent and is NEVER auto-negatived under agency policy."),
    ("house washing company near me", "House Washing", "REMOVE - bucket collapse",
     "Shares the 40/mo bucket with `house washing near me`. NOTE: its ad group 202870585910 IS "
     "reused as the House Washing container; only the keyword text is displaced."),
    ("house washing company", "House Washing", "REMOVE - covered",
     "Phrase `house washing near me` does not match it, but it has no reportable local volume."),
    ("soft washing company near me", "Soft Washing", "REMOVE - no demand",
     "No reportable local volume; 10/mo family total is already owned."),
    ("driveway cleaning service", "Driveway Pressure Washing", "DEFER - expansion candidate",
     "No reportable local volume and not matched by the owned driveway texts. Revisit after the "
     "six core groups produce routing evidence. NOT a launch keyword."),
    ("patio cleaning service", "Patio Pressure Washing", "DEFER - expansion candidate",
     "No reportable local volume. Revisit after launch. NOT a launch keyword."),
    ("house pressure washing estimate", "House Washing", "REMOVE - displaced legacy",
     "Live text in BOTH campaigns with 33 impressions and 3 clicks at $104.85 and zero leads. "
     "Covered by Phrase `house pressure washing near me`. Its ad groups are retired."),
    ("power washing islip", "-", "REMOVE - zero-volume city SKAG",
     "0 reportable volume, 0 impressions all-time. Retire; do not preserve merely because it "
     "exists. No city keyword has reportable demand."),
    ("power washing west islip", "-", "REMOVE - zero-volume city SKAG",
     "1 impression, 1 click, $5.71, zero leads all-time. Retire."),
    ("power washing dix hills", "-", "REMOVE - zero-volume city SKAG",
     "0 reportable volume, 0 impressions all-time. Retire."),
    ("pressure washer / power washer / equipment / rental / machine / repair / parts",
     "-", "NEVER USE AS POSITIVE",
     "Local SERP evidence: bare `pressure washer` and `power washer` return 100% equipment "
     "retail (Ace, Tractor Supply, Lowe's, Harbor Freight). The distinguishing token is "
     "grammatical: *washing* is the service, *washer* is the machine. Blocked by the existing "
     "132-per-campaign universal fence."),
]

# ------------------------------------------------------------------- RSA copy
RSA = {
    "Power Washing": [
        {"n": 1, "angle": "Exact service intent, local availability, free quote, direct response",
         "h": ["Power Washing Near You", "Local Power Washing Service", "Power Washing Long Island",
               "Free Power Washing Quote", "Softwind Power Washing", "Serving Nassau & Suffolk",
               "Request A Free Quote Today", "Get Your Free Estimate", "Exterior Home Washing",
               "Wash Your Home Exterior", "Book Your Free Quote", "Homes Across Long Island",
               "Clean Siding And Concrete", "Dirt, Grime And Algae Gone", "Free Quotes For Homeowners"],
         "d": ["Local power washing across Long Island. Request a free quote for your home today.",
               "Power Washing for homes in Nassau and Suffolk County. Free quotes, no obligation.",
               "Lifts dirt, grime and algae from siding, concrete and walkways around your home.",
               "Tell us about your project and we will send back a free quote."]},
        {"n": 2, "angle": "Exterior transformation, surface-specific method, curb appeal, process",
         "h": ["Restore Your Home Exterior", "Curb Appeal Starts Outside", "Siding, Patio And Driveway",
               "Surface-Specific Washing", "Careful Washing Methods", "Right Pressure Per Surface",
               "Power Washing With Care", "Long Island Power Washing", "Nassau And Suffolk Homes",
               "Get A Free Estimate", "Request Your Free Estimate", "Visibly Cleaner Results",
               "Wash Away Years Of Grime", "See The Difference Outside", "Power Washing Specialists"],
         "d": ["We match the right power washing pressure and method to every surface we clean.",
               "Siding, concrete and walkways washed with care and the right method. Free estimate.",
               "See the difference a professional exterior wash makes. Request an estimate.",
               "Serving homeowners across Nassau and Suffolk County. Get a free estimate."]},
    ],
    "Pressure Washing": [
        {"n": 1, "angle": "Exact service intent, local availability, free quote, direct response",
         "h": ["Pressure Washing Near You", "Local Pressure Washing Service", "Pressure Washing Long Island",
               "Free Pressure Washing Quote", "Softwind Pressure Washing", "Serving Nassau & Suffolk",
               "Request A Free Quote Today", "Get Your Free Estimate", "Residential Washing",
               "Wash Your Home Exterior", "Book Your Free Quote", "Homes Across Long Island",
               "Clean Siding And Concrete", "Dirt, Grime And Algae Gone", "Free Quotes For Homeowners"],
         "d": ["Local pressure washing across Long Island. Request a free quote for your home today.",
               "Pressure Washing for homes in Nassau and Suffolk County. Free quotes, no obligation.",
               "Lifts dirt, grime and algae from siding, concrete and walkways around your home.",
               "Tell us about your project and we will send back a free quote."]},
        {"n": 2, "angle": "Exterior transformation, surface-specific method, curb appeal, process",
         "h": ["Restore Your Home Exterior", "Curb Appeal Starts Outside", "Siding, Patio And Driveway",
               "Surface-Specific Washing", "Careful Washing Methods", "Right Pressure Per Surface",
               "Pressure Washing With Care", "Long Island Pressure Washing", "Nassau And Suffolk Homes",
               "Get A Free Estimate", "Request Your Free Estimate", "Visibly Cleaner Results",
               "Wash Away Years Of Grime", "See The Difference Outside", "Pressure Washing Specialists"],
         "d": ["We match the right pressure washing pressure and method to every surface we clean.",
               "Siding, concrete and walkways washed with care and the right method. Free estimate.",
               "See the difference a professional exterior wash makes. Request an estimate.",
               "Serving homeowners across Nassau and Suffolk County. Get a free estimate."]},
    ],
    "House Washing": [
        {"n": 1, "angle": "Exact service intent, local availability, free quote, direct response",
         "h": ["House Washing Near You", "Local House Washing Service", "House Washing Long Island",
               "Free House Washing Quote", "Softwind House Washing", "Serving Nassau & Suffolk",
               "Request A Free Quote Today", "Get Your Free Estimate", "Exterior House Washing",
               "Wash Your Home Exterior", "Book Your Free Quote", "Homes Across Long Island",
               "Clean Siding And Trim", "Dirt, Grime And Algae Gone", "Free Quotes For Homeowners"],
         "d": ["Local house washing across Long Island. Request a free quote for your home today.",
               "House Washing for homes in Nassau and Suffolk County. Free quotes, no obligation.",
               "Lifts dirt, grime and algae from siding, trim and exterior walls around your home.",
               "Tell us about your project and we will send back a free quote."]},
        {"n": 2, "angle": "Exterior transformation, surface-specific method, curb appeal, process",
         "h": ["Bring Back Clean Siding", "Curb Appeal Starts Outside", "Siding, Trim And Gutters",
               "Surface-Specific Washing", "Careful Washing Methods", "Right Pressure Per Surface",
               "House Washing With Care", "Long Island House Washing", "Nassau And Suffolk Homes",
               "Get A Free Estimate", "Request Your Free Estimate", "Visibly Cleaner Results",
               "Wash Away Years Of Grime", "See The Difference Outside", "House Washing Specialists"],
         "d": ["We match the right house washing pressure and method to every surface we clean.",
               "Siding, trim and exterior walls washed with care and the right method. Free estimate.",
               "See the difference a professional exterior wash makes. Request an estimate.",
               "Serving homeowners across Nassau and Suffolk County. Get a free estimate."]},
    ],
    "Soft Washing": [
        {"n": 1, "angle": "Exact service intent, local availability, free quote, direct response",
         "h": ["Soft Washing Near You", "Local Soft Washing Service", "Soft Washing Long Island",
               "Free Soft Washing Quote", "Softwind Soft Washing", "Serving Nassau & Suffolk",
               "Request A Free Quote Today", "Get Your Free Estimate", "Soft House Washing",
               "Low Pressure Washing", "Book Your Free Quote", "Homes Across Long Island",
               "Clean Siding Without Force", "Dirt, Grime And Algae Gone", "Free Quotes For Homeowners"],
         "d": ["Local soft washing across Long Island. Request a free quote for your home today.",
               "Soft Washing for homes in Nassau and Suffolk County. Free quotes, no obligation.",
               "Lifts dirt, grime and algae from siding, trim and delicate surfaces around your home.",
               "Tell us about your project and we will send back a free quote."]},
        {"n": 2, "angle": "Exterior transformation, surface-specific method, curb appeal, process",
         "h": ["Low Pressure, Real Results", "Curb Appeal Starts Outside", "Gentle On Your Siding",
               "Surface-Specific Washing", "Careful Washing Methods", "Right Pressure Per Surface",
               "Soft Washing With Care", "Long Island Soft Washing", "Nassau And Suffolk Homes",
               "Get A Free Estimate", "Request Your Free Estimate", "Visibly Cleaner Results",
               "Wash Away Years Of Grime", "See The Difference Outside", "Soft Washing Specialists"],
         "d": ["We match the right soft washing pressure and method to every surface we clean.",
               "Siding, trim and delicate surfaces washed with care and the right method. Free estimate.",
               "See the difference a professional exterior wash makes. Request an estimate.",
               "Serving homeowners across Nassau and Suffolk County. Get a free estimate."]},
    ],
    "Driveway Pressure Washing": [
        {"n": 1, "angle": "Exact service intent, local availability, free quote, direct response",
         "h": ["Driveway Washing Near You", "Local Driveway Washing Service", "Driveway Washing Long Island",
               "Free Driveway Washing Quote", "Softwind Driveway Washing", "Serving Nassau & Suffolk",
               "Request A Free Quote Today", "Get Your Free Estimate", "Driveway Power Washing",
               "Wash Your Driveway Clean", "Book Your Free Quote", "Homes Across Long Island",
               "Clean Concrete And Pavers", "Dirt, Grime And Algae Gone", "Free Quotes For Homeowners"],
         "d": ["Local driveway washing across Long Island. Request a free quote for your home today.",
               "Driveway Washing for homes in Nassau and Suffolk County. Free quotes, no obligation.",
               "Lifts dirt, grime and algae from concrete, pavers and stone around your home.",
               "Tell us about your project and we will send back a free quote."]},
        {"n": 2, "angle": "Exterior transformation, surface-specific method, curb appeal, process",
         "h": ["Bring Back Clean Concrete", "Curb Appeal Starts Outside", "Driveways, Paths And Pavers",
               "Surface-Specific Washing", "Careful Washing Methods", "Right Pressure Per Surface",
               "Driveway Washing With Care", "Long Island Driveway Washing", "Nassau And Suffolk Homes",
               "Get A Free Estimate", "Request Your Free Estimate", "Visibly Cleaner Results",
               "Wash Away Years Of Grime", "See The Difference Outside", "Driveway Washing Specialists"],
         "d": ["We match the right driveway washing pressure and method to every surface we clean.",
               "Concrete, pavers and stone washed with care and the right method. Free estimate.",
               "See the difference a professional exterior wash makes. Request an estimate.",
               "Serving homeowners across Nassau and Suffolk County. Get a free estimate."]},
    ],
    "Patio Pressure Washing": [
        {"n": 1, "angle": "Exact service intent, local availability, free quote, direct response",
         "h": ["Patio Washing Near You", "Local Patio Washing Service", "Patio Washing Long Island",
               "Free Patio Washing Quote", "Softwind Patio Washing", "Serving Nassau & Suffolk",
               "Request A Free Quote Today", "Get Your Free Estimate", "Patio Power Washing",
               "Wash Your Patio Clean", "Book Your Free Quote", "Homes Across Long Island",
               "Clean Concrete And Pavers", "Dirt, Grime And Algae Gone", "Free Quotes For Homeowners"],
         "d": ["Local patio washing across Long Island. Request a free quote for your home today.",
               "Patio Washing for homes in Nassau and Suffolk County. Free quotes, no obligation.",
               "Lifts dirt, grime and algae from pavers, concrete and stone around your home.",
               "Tell us about your project and we will send back a free quote."]},
        {"n": 2, "angle": "Exterior transformation, surface-specific method, curb appeal, process",
         "h": ["Bring Back Clean Pavers", "Curb Appeal Starts Outside", "Patios, Pavers And Concrete",
               "Surface-Specific Washing", "Careful Washing Methods", "Right Pressure Per Surface",
               "Patio Washing With Care", "Long Island Patio Washing", "Nassau And Suffolk Homes",
               "Get A Free Estimate", "Request Your Free Estimate", "Visibly Cleaner Results",
               "Wash Away Years Of Grime", "See The Difference Outside", "Patio Washing Specialists"],
         "d": ["We match the right patio washing pressure and method to every surface we clean.",
               "Pavers, concrete and stone washed with care and the right method. Free estimate.",
               "See the difference a professional exterior wash makes. Request an estimate.",
               "Serving homeowners across Nassau and Suffolk County. Get a free estimate."]},
    ],
}

BANNED = ["best", "#1", "number one", "cheapest", "guarantee", "guaranteed", "same-day",
          "same day", "licensed", "insured", "award", "five-star", "5-star", "years of experience",
          "years in business", "24/7", "fastest", "permanent"]

errors: list[str] = []
warnings: list[str] = []


def main() -> int:
    now = datetime.now(ZoneInfo("America/New_York"))

    # ------------------------------------------------ 1. ownership uniqueness
    owner: dict[str, str] = {}
    for g, cfg in GROUPS.items():
        for t in cfg["texts"]:
            if t in owner:
                errors.append(f"DUPLICATE OWNER: '{t}' owned by {owner[t]} and {g}")
            owner[t] = g
    all_texts = sorted(owner)
    if len(all_texts) != 19:
        errors.append(f"expected 19 canonical texts, got {len(all_texts)}")

    # ------------------------------------------------ 2. keyword inventory CSV
    rows = []
    add_objects = 0
    reuse_objects = 0
    for g, cfg in GROUPS.items():
        for t in cfg["texts"]:
            vol, comp, lo, hi, trend = DEMAND[t]
            bucket = SHARED_BUCKET.get(t, "")
            for mt in ("PHRASE", "EXACT"):
                exists = (t, mt) in cfg["existing"]
                if exists:
                    reuse_objects += 1
                else:
                    add_objects += 1
                q = QS.get((t, mt), ("", "", "", ""))
                h = HIST.get(t, (0, 0, 0.0))
                bofu = 5 if "near me" in t else (4 if t.endswith("service") else 4)
                equip = 3 if t in ("power washing", "pressure washing") else (
                    1 if "power washing" in t or "pressure washing" in t else 0)
                rows.append({
                    "owner_ad_group": g,
                    "ad_group_id": cfg["ad_group_id"],
                    "ad_group_current_name": cfg["current_name"],
                    "ad_group_current_status": cfg["current_status"],
                    "keyword_text": t,
                    "match_type": mt,
                    "action": "REUSE EXISTING" if exists else "ADD - CREATE PAUSED",
                    "local_monthly_demand": vol,
                    "demand_counted_once_in_bucket_of": bucket or t,
                    "shares_bucket_with": bucket,
                    "competition": comp,
                    "top_of_page_low_usd": f"{lo:.2f}" if lo else "no data",
                    "top_of_page_high_usd": f"{hi:.2f}" if hi else "no data",
                    "planner_trend": trend,
                    "historical_impressions": h[0],
                    "historical_clicks": h[1],
                    "historical_cost_usd": f"{h[2]:.2f}",
                    "historical_query_evidence": (
                        "served, paid clicks, zero leads" if h[1] else
                        ("served, no clicks" if h[0] else "no impressions all-time")),
                    "quality_score": q[0],
                    "expected_ctr": q[1],
                    "ad_relevance": q[2],
                    "landing_page_experience": q[3],
                    "bofu_score_0_5": bofu,
                    "equipment_ambiguity_0_5": equip,
                    "landing_page": cfg["page"],
                    "landing_page_match_0_5": 4 if t in ("power washing", "pressure washing") else 5,
                    "verdict": "FINAL - ACTIVE",
                })
    for t, g, verdict, why in REJECTED:
        rows.append({
            "owner_ad_group": g, "ad_group_id": "", "ad_group_current_name": "",
            "ad_group_current_status": "", "keyword_text": t, "match_type": "-",
            "action": verdict, "local_monthly_demand": DEMAND.get(t, ("",))[0]
            if t in DEMAND else "", "demand_counted_once_in_bucket_of": "",
            "shares_bucket_with": "", "competition": "", "top_of_page_low_usd": "",
            "top_of_page_high_usd": "", "planner_trend": "",
            "historical_impressions": HIST.get(t, (0, 0, 0))[0],
            "historical_clicks": HIST.get(t, (0, 0, 0))[1],
            "historical_cost_usd": f"{HIST.get(t, (0, 0, 0.0))[2]:.2f}",
            "historical_query_evidence": why, "quality_score": "", "expected_ctr": "",
            "ad_relevance": "", "landing_page_experience": "", "bofu_score_0_5": "",
            "equipment_ambiguity_0_5": "", "landing_page": "", "landing_page_match_0_5": "",
            "verdict": verdict,
        })
    write_csv(AUD / "2026-09-01-authoritative-keyword-inventory.csv", rows)

    # deduped demand
    counted = {}
    for t in all_texts:
        key = SHARED_BUCKET.get(t, t)
        counted[key] = DEMAND[key][0] if key in DEMAND else DEMAND[t][0]
    deduped_demand = sum(counted.values())

    # ------------------------------------------------ 3. RSA CSV + validation
    rsa_rows = []
    seen_h_global = {}
    for g, cfg in GROUPS.items():
        if g not in RSA or len(RSA[g]) != 2:
            errors.append(f"{g}: expected exactly 2 RSAs")
            continue
        for ad in RSA[g]:
            hs, ds = ad["h"], ad["d"]
            if len(hs) > 15:
                errors.append(f"{g} RSA{ad['n']}: {len(hs)} headlines > 15")
            if len(ds) > 4:
                errors.append(f"{g} RSA{ad['n']}: {len(ds)} descriptions > 4")
            for x in hs:
                if len(x) > 30:
                    errors.append(f"{g} RSA{ad['n']} HEADLINE {len(x)}>30: '{x}'")
            for x in ds:
                if len(x) > 90:
                    errors.append(f"{g} RSA{ad['n']} DESC {len(x)}>90: '{x}'")
            if len(set(hs)) != len(hs):
                errors.append(f"{g} RSA{ad['n']}: duplicate headline within ad")
            if len(set(ds)) != len(ds):
                errors.append(f"{g} RSA{ad['n']}: duplicate description within ad")
            for p in (cfg["p1"], cfg["p2"]):
                if len(p) > 15:
                    errors.append(f"{g}: path '{p}' {len(p)}>15")
            blob = " ".join(hs + ds).lower()
            for b in BANNED:
                if b in blob:
                    errors.append(f"{g} RSA{ad['n']}: banned claim '{b}'")
            if any(ch.isdigit() for ch in blob):
                errors.append(f"{g} RSA{ad['n']}: digit found - possible phone number in copy")
            if "near me" in blob:
                errors.append(f"{g} RSA{ad['n']}: awkward 'near me' copy")
            canon = g.split()[0].lower()
            svc_h = sum(1 for x in hs if canon in x.lower())
            if not 3 <= svc_h <= 8:
                warnings.append(f"{g} RSA{ad['n']}: service token in {svc_h} headlines")
            local_h = sum(1 for x in hs
                          if any(k in x for k in ("Long Island", "Nassau", "Suffolk",
                                                  "Local", "Near You")))
            if local_h < 2:
                errors.append(f"{g} RSA{ad['n']}: only {local_h} local headlines, need >=2")
            offer_h = sum(1 for x in hs
                          if "Free" in x or "Quote" in x or "Estimate" in x)
            if offer_h < 2:
                errors.append(f"{g} RSA{ad['n']}: only {offer_h} quote/estimate headlines")
            if not any(canon in d.lower() for d in ds):
                errors.append(f"{g} RSA{ad['n']}: service absent from every description")
            for x in hs:
                seen_h_global.setdefault(x, []).append(f"{g}/RSA{ad['n']}")
            rsa_rows.append({
                "ad_group": g, "ad_group_id": cfg["ad_group_id"], "rsa": f"RSA {ad['n']}",
                "angle": ad["angle"], "status_on_create": "PAUSED",
                "final_url": cfg["page"], "path1": cfg["p1"], "path2": cfg["p2"],
                "headline_count": len(hs), "description_count": len(ds),
                "max_headline_len": max(len(x) for x in hs),
                "max_description_len": max(len(x) for x in ds),
                "service_token_headlines": svc_h, "local_headlines": local_h,
                "offer_headlines": offer_h, "pinning": "NONE",
                **{f"H{i+1}": hs[i] if i < len(hs) else "" for i in range(15)},
                **{f"H{i+1}_len": len(hs[i]) if i < len(hs) else "" for i in range(15)},
                **{f"D{i+1}": ds[i] if i < len(ds) else "" for i in range(4)},
                **{f"D{i+1}_len": len(ds[i]) if i < len(ds) else "" for i in range(4)},
            })
    # cross-ad duplicate headlines are allowed across DIFFERENT ad groups but the two
    # RSAs inside one ad group must not be minor rewrites of each other
    for g in GROUPS:
        if g in RSA and len(RSA[g]) == 2:
            a, b = set(RSA[g][0]["h"]), set(RSA[g][1]["h"])
            overlap = len(a & b) / max(len(a | b), 1)
            if overlap > 0.20:
                errors.append(f"{g}: RSA1/RSA2 headline overlap {overlap:.0%} > 20% "
                              f"- they are minor rewrites")
            da, db = set(RSA[g][0]["d"]), set(RSA[g][1]["d"])
            if da & db:
                errors.append(f"{g}: RSA1/RSA2 share a description")
    write_csv(AUD / "2026-09-01-final-rsa-copy-and-qa.csv", rsa_rows)

    # ------------------------------------------------ 4. keyword/ad/page map
    map_rows = []
    for g, cfg in GROUPS.items():
        for t in cfg["texts"]:
            map_rows.append({
                "final_ad_group": g, "ad_group_id": cfg["ad_group_id"],
                "ad_group_current_name": cfg["current_name"],
                "ad_group_current_status": cfg["current_status"],
                "keyword_text": t, "match_types": "PHRASE + EXACT",
                "landing_page": cfg["page"],
                "page_current_title": PAGE_FACTS[cfg["page"]]["title"],
                "page_current_h1": PAGE_FACTS[cfg["page"]]["h1"],
                "page_city_locked": PAGE_FACTS[cfg["page"]]["locked"],
                "page_countdown": "YES", "page_foreign_tag": "AW-17878095007 PRESENT",
                "rsa_1": f"{g} RSA 1", "rsa_2": f"{g} RSA 2",
                "path1": cfg["p1"], "path2": cfg["p2"],
                "keyword_to_title_alignment": PAGE_FACTS[cfg["page"]]["title_align"],
                "keyword_to_h1_alignment": PAGE_FACTS[cfg["page"]]["h1_align"],
                "page_verdict": PAGE_FACTS[cfg["page"]]["verdict"],
            })
    write_csv(AUD / "2026-09-01-final-keyword-ad-page-map.csv", map_rows)

    # ------------------------------------------------ 5. routing negative matrix
    neg_rows = []
    for t in all_texts:
        own = owner[t]
        for g, cfg in GROUPS.items():
            if g == own:
                continue
            if any(t == x for x in cfg["texts"]):
                errors.append(f"SELF-BLOCK: negative '{t}' in its own owner {g}")
            neg_rows.append({
                "layer": "1 - SIBLING EXACT MIRROR", "negative_text": t,
                "match_type": "EXACT", "level": "AD GROUP",
                "target_ad_group": g, "target_ad_group_id": cfg["ad_group_id"],
                "owner_ad_group": own, "owner_ad_group_id": GROUPS[own]["ad_group_id"],
                "self_block_check": "PASS - owner group excluded",
                "blocks_owned_text_in_target": "NO",
                "deploy_at_launch": "YES",
                "reason": f"Enforces one-owner-per-text. '{t}' belongs to {own}.",
            })
    MODIFIERS = ["house washing", "soft washing", "driveway", "patio"]
    MOD_TARGETS = ["Power Washing", "Pressure Washing"]
    for m in MODIFIERS:
        for g in MOD_TARGETS:
            cfg = GROUPS[g]
            collide = [t for t in cfg["texts"] if m in t]
            if collide:
                errors.append(f"MODIFIER COLLISION: phrase '{m}' blocks owned {collide} in {g}")
                continue
            neg_rows.append({
                "layer": "2 - MODIFIER PHRASE", "negative_text": m,
                "match_type": "PHRASE", "level": "AD GROUP",
                "target_ad_group": g, "target_ad_group_id": cfg["ad_group_id"],
                "owner_ad_group": owner_family(m, owner),
                "owner_ad_group_id": GROUPS[owner_family(m, owner)]["ad_group_id"],
                "self_block_check": "PASS - no owned text in target contains this phrase",
                "blocks_owned_text_in_target": "NO", "deploy_at_launch": "YES",
                "reason": (f"'{g}' owns the loose head term and would otherwise vacuum "
                           f"'{m}' family queries away from their owner."),
            })
    for m in MODIFIERS:
        for g in GROUPS:
            if g in MOD_TARGETS:
                continue
            cfg = GROUPS[g]
            if any(m in t for t in cfg["texts"]):
                continue
            neg_rows.append({
                "layer": "2 - MODIFIER PHRASE (DEFERRED)", "negative_text": m,
                "match_type": "PHRASE", "level": "AD GROUP",
                "target_ad_group": g, "target_ad_group_id": cfg["ad_group_id"],
                "owner_ad_group": owner_family(m, owner),
                "owner_ad_group_id": GROUPS[owner_family(m, owner)]["ad_group_id"],
                "self_block_check": "PASS", "blocks_owned_text_in_target": "NO",
                "deploy_at_launch": "NO - DEFER",
                "reason": ("Narrow-intent group; its own EXACT and PHRASE texts already scope it. "
                           "Adding this is theoretical routing with no observed leak. Defer."),
            })
    for t, why in [("pressure washer near me",
                    "Equipment intent. Served 2026-09-01 as NEAR_EXACT close variant in "
                    "Power Washing Near Me. 1 impression, 0 clicks, $0.00."),
                   ("commercial pressure washing near me",
                    "Outside verified residential scope. Served 2026-09-01 as NEAR_EXACT close "
                    "variant. 1 impression, 0 clicks, $0.00.")]:
        neg_rows.append({
            "layer": "3 - HISTORICAL ROGUE QUERY", "negative_text": t, "match_type": "EXACT",
            "level": "CAMPAIGN (universal)", "target_ad_group": "n/a - campaign level",
            "target_ad_group_id": CAMP, "owner_ad_group": "none - not an approved intent",
            "owner_ad_group_id": "", "self_block_check": "PASS - no owned text matches",
            "blocks_owned_text_in_target": "NO", "deploy_at_launch": "NO - DEFER 14 DAYS",
            "reason": why,
        })
    write_csv(AUD / "2026-09-01-final-routing-negative-matrix.csv", neg_rows)

    launch_negs = sum(1 for r in neg_rows if r["deploy_at_launch"] == "YES")
    l1 = sum(1 for r in neg_rows if r["layer"].startswith("1"))
    l2 = sum(1 for r in neg_rows if r["layer"] == "2 - MODIFIER PHRASE")
    l2d = sum(1 for r in neg_rows if "DEFERRED" in r["layer"])
    l3 = sum(1 for r in neg_rows if r["layer"].startswith("3"))

    # ------------------------------------------------ 6. manifest
    canonical = {
        "program": "Softwind complete recovery, September 2026",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "surviving_campaign_id": CAMP},
        "final_ad_groups": [{"name": g, "ad_group_id": c["ad_group_id"],
                             "texts": sorted(c["texts"]), "page": c["page"]}
                            for g, c in sorted(GROUPS.items())],
        "keyword_objects_total": len(all_texts) * 2,
        "keyword_objects_to_add": add_objects,
        "keyword_objects_reused": reuse_objects,
        "rsas_to_create_paused": len(rsa_rows),
        "launch_routing_negatives": launch_negs,
    }
    fp = approval_code(canonical)
    manifest = {
        "generated_account_local": now.isoformat(),
        "program_fingerprint_reference_only": fp,
        "program_fingerprint_note": ("This identifies the ARCHITECTURE, not an executable "
                                     "plan. It is NOT an approval code and no approval "
                                     "command uses it."),
        "canonical_sha256_full": hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")).hexdigest(),
        "architecture": canonical,
        "counts": {
            "final_campaigns": 1,
            "final_ad_groups": len(GROUPS),
            "ad_groups_to_create": 0,
            "ad_groups_reused_existing": len(GROUPS),
            "canonical_keyword_texts": len(all_texts),
            "keyword_objects_final": len(all_texts) * 2,
            "keyword_objects_to_add_paused": add_objects,
            "keyword_objects_reused": reuse_objects,
            "rsas_final": len(rsa_rows),
            "rsas_to_create_paused": len(rsa_rows),
            "create_paused_objects_total": add_objects + len(rsa_rows),
            "routing_negatives_layer1_sibling_exact": l1,
            "routing_negatives_layer2_modifier_deployed": l2,
            "routing_negatives_layer2_modifier_deferred": l2d,
            "routing_negatives_layer3_deferred": l3,
            "routing_negatives_at_launch": launch_negs,
            "deduped_local_monthly_demand": deduped_demand,
            "keyword_texts_reviewed_and_rejected": len(REJECTED),
        },
        "validation": {
            "errors": errors, "warnings": warnings,
            "error_count": len(errors), "warning_count": len(warnings),
            "all_pass": not errors,
            "checks": [
                "every canonical text has exactly one owner ad group",
                "no routing negative is placed in its own owner group",
                "no modifier phrase negative blocks an owned text in its target group",
                "every RSA headline <= 30 characters",
                "every RSA description <= 90 characters",
                "every path <= 15 characters",
                "no duplicate headline or description within an ad",
                "RSA1/RSA2 headline overlap <= 20% inside each ad group",
                "no banned or unverified claim in any asset",
                "no digit in any asset (phone-number guard)",
                "no awkward 'near me' ad copy",
                ">= 2 local headlines and >= 2 quote/estimate headlines per RSA",
                "service token present in 3-9 headlines and >= 1 description per RSA",
                "no pinning",
            ],
        },
    }
    (PLN / "2026-09-01-complete-recovery-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps({"counts": manifest["counts"],
                      "validation": {"errors": errors, "warnings": warnings,
                                     "all_pass": not errors}}, indent=2))
    return 0 if not errors else 1


def owner_family(mod: str, owner: dict[str, str]) -> str:
    for t, g in owner.items():
        if mod in t:
            return g
    return {"driveway": "Driveway Pressure Washing", "patio": "Patio Pressure Washing"}[mod]


PAGE_FACTS = {
    f"{BASE}/power-washing-services-islip-west-islip-dix-hills/": {
        "title": "Power Washing | Softwind Landscape & Masonry",
        "h1": "Power Washing Service In Islip, West Islip & Dix Hills, NY",
        "locked": "YES", "title_align": "STRONG service / WRONG brand",
        "h1_align": "STRONG service / CITY-LOCKED to 3 of 80 targets",
        "verdict": "REUSE AFTER P0+P1 FIX - live QS shows landing-page experience BELOW_AVERAGE"},
    f"{BASE}/residential-pressure-washing/": {
        "title": "Residential Pressure Washing | Softwind Landscape & Masonry",
        "h1": "Residential Pressure Washing In Islip, West Islip & Dix Hills, NY",
        "locked": "YES", "title_align": "STRONG service / WRONG brand",
        "h1_align": "STRONG service / CITY-LOCKED",
        "verdict": "REUSE AFTER P0+P1 FIX - 21 pressure-washing mentions, best pressure page"},
    f"{BASE}/house-washing-company/": {
        "title": "House Washing Company | Softwind Landscape & Masonry",
        "h1": "House Washing Company In Islip, West Islip & Dix Hills, NY",
        "locked": "YES", "title_align": "STRONG service / WRONG brand",
        "h1_align": "STRONG service / CITY-LOCKED",
        "verdict": "REUSE AFTER P0+P1 FIX - 24 house-washing mentions, best house page"},
    f"{BASE}/soft-house-washing/": {
        "title": "Soft House Washing | Softwind Landscape & Masonry",
        "h1": "Soft House Washing In Islip, West Islip & Dix Hills, NY",
        "locked": "YES", "title_align": "STRONG service / WRONG brand",
        "h1_align": "STRONG service / CITY-LOCKED",
        "verdict": ("REUSE AFTER P0+P1 FIX. ALTERNATIVE EXISTS: /power-washing-soft-washing/ is "
                    "NOT city-locked and carries 17 Long Island mentions and 9 soft-washing "
                    "mentions - evaluate as the replacement during Stage 3.")},
    f"{BASE}/driveway-pressure-washing/": {
        "title": "Driveway Pressure Washing | Softwind Landscape & Masonry",
        "h1": "Driveway Pressure Washing In Islip, West Islip & Dix Hills, NY",
        "locked": "YES", "title_align": "STRONG service / WRONG brand",
        "h1_align": "STRONG service / CITY-LOCKED",
        "verdict": "REUSE AFTER P0+P1 FIX"},
    f"{BASE}/patio-power-washing/": {
        "title": "Patio Power Washing | Softwind Landscape & Masonry",
        "h1": "Patio Pressure Washing In Islip, West Islip & Dix Hills, NY",
        "locked": "YES", "title_align": "MISMATCH - title says Power, H1 says Pressure",
        "h1_align": "STRONG service / CITY-LOCKED",
        "verdict": "REUSE AFTER P0+P1+P3 FIX - title/H1 power-vs-pressure mismatch"},
}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.name}: {len(rows)} rows")


if __name__ == "__main__":
    raise SystemExit(main())
