#!/usr/bin/env python3
"""Build PLAN-I2A - true SKAG demand expansion, replacing PLAN-I2.

Generates and validates RSA copy from the verified-claim vocabulary only.
Local file generation. No API calls, no mutations.
"""
from __future__ import annotations

import json
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLANS = ROOT / "clients/softwind-power-washing/plans"

BANNED = re.compile(
    r"\b(licensed|insured|bonded|certified|guarantee[ds]?|warrant|"
    r"\d+\s*(years?|yrs?)|since\s*\d{4}|award|rated|rating|stars?|reviews?|"
    r"\d+\s*%|\$\d|cheap|discount|sale|deal|coupon|promo|"
    r"same[- ]day|24/7|emergency|instant|immediately|fastest|"
    r"best|#1|number one|top rated|voted|trusted by|review|"
    r"roof|gutter|seal(ing|er|ant)|masonry|landscap|paint)\b", re.I)

TARGET = {"exact_child_account_name": "Softwind Power Washing - Live",
          "child_customer_id": "1521725229",
          "manager_customer_id": "3373711342",
          "exact_service": "Power Washing",
          "vertical": "similar-local-service"}

# ---------------------------------------------------------------- SKAG defs
SKAGS = [
    {
        "name": "Power Washing Service",
        "campaign_id": "24103511039", "campaign": "Power Washing",
        "phrase": "power washing service", "exact": "power washing service",
        "volume": 70, "trend": 293.3, "bid_low": 11.40, "bid_high": 26.35,
        "competition": "LOW",
        "url": "https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/",
        "lp_h1": "Power Washing Service In Islip, West Islip & Dix Hills, NY",
        "path1": "power-washing", "path2": "service",
        "why": ("Highest-volume single bucket recovered from the legacy container, and the "
                "fastest-growing term in the account at +293.3% over the last three months "
                "versus the prior three. The live keyword is 'power washing services NEAR "
                "ME' - a query for 'power washing service' does not match its Exact form "
                "and does not contain its Phrase form, so this demand is genuinely "
                "uncovered."),
        "rsa1": {
            "H": ["Power Washing Service", "Local Power Washing Service",
                  "Power Washing In Islip NY", "Long Island Power Washing",
                  "Free Power Washing Quote", "Residential Power Washing",
                  "House, Patio And Driveway", "Siding, Concrete And Pavers",
                  "Method Matched To Surface", "Soft Washing For Siding",
                  "Serving Islip & West Islip", "Power Washing Dix Hills",
                  "Call (631) 502-7946", "Request Your Free Quote",
                  "Softwind Power Washing"],
            "D": ["A local power washing service for siding, driveways, patios and pavers.",
                  "The cleaning method is chosen for the surface, from concrete to siding.",
                  "Serving Islip, West Islip and Dix Hills homeowners. Free quote.",
                  "Power washing service on Long Island. Call (631) 502-7946 for a quote."]},
        "rsa2": {
            "H": ["Power Washing Service", "Exterior Washing Service",
                  "Right Pressure, Right Surface", "Low-Pressure Siding Washing",
                  "Driveway And Patio Washing", "Paver And Concrete Washing",
                  "Walkway And Fence Washing", "Cleaner Home Exteriors",
                  "Free Quote On Your Project", "Tell Us What Needs Cleaning",
                  "Islip Power Washing", "West Islip Power Washing",
                  "Dix Hills Power Washing", "Local Long Island Team",
                  "Softwind Exterior Washing"],
            "D": ["We match the washing method to the material, so siding is treated gently.",
                  "Driveways, patios, walkways, pavers and concrete washed and refreshed.",
                  "Tell us what needs cleaning and where. We will send you a free quote.",
                  "A local power washing service for Long Island homes. Free quote."]},
    },
    {
        "name": "Pressure Washing Service",
        "campaign_id": "24145053510", "campaign": "Power Washing #2",
        "phrase": "pressure washing service", "exact": "pressure washing service",
        "volume": 70, "trend": 293.3, "bid_low": 11.40, "bid_high": 26.35,
        "competition": "LOW",
        "url": "https://offer.softwindli.com/residential-pressure-washing/",
        "lp_h1": "Residential Pressure Washing In Islip, West Islip & Dix Hills, NY",
        "path1": "pressure-wash", "path2": "service",
        "why": ("Shares a Keyword Planner volume bucket with 'power washing service', which "
                "means Google treats them as near-synonyms - but the SEARCHER types one or "
                "the other, and the account has hard evidence that copy match decides the "
                "click: 'pressure wash' phrasing has produced 15 impressions and ZERO "
                "clicks (0% CTR) while 'power wash' phrasing runs 7.25%. Eleven of those "
                "fifteen were served power-washing copy. A separate SKAG exists precisely "
                "to serve matching copy, which is the whole purpose of the architecture."),
        "rsa1": {
            "H": ["Pressure Washing Service", "Local Pressure Washing",
                  "Pressure Washing In Islip", "Long Island Pressure Wash",
                  "Free Pressure Washing Quote", "Residential Pressure Wash",
                  "Driveways, Patios & Siding", "Pavers, Concrete & Walkways",
                  "Method Matched To Surface", "Soft Washing For Siding",
                  "Serving Islip & West Islip", "Pressure Washing Dix Hills",
                  "Call (631) 502-7946", "Request Your Free Quote",
                  "Softwind Pressure Washing"],
            "D": ["A local pressure washing service for driveways, patios and siding.",
                  "The washing method is chosen for the surface, from concrete to siding.",
                  "Serving Islip, West Islip and Dix Hills homeowners. Free quote.",
                  "Pressure washing service on Long Island. Call (631) 502-7946."]},
        "rsa2": {
            "H": ["Pressure Washing Service", "Exterior Washing Service",
                  "Right Pressure, Right Surface", "Low-Pressure Siding Washing",
                  "Driveway And Patio Washing", "Paver And Concrete Washing",
                  "Walkway And Fence Washing", "Cleaner Home Exteriors",
                  "Free Quote On Your Project", "Tell Us What Needs Cleaning",
                  "Islip Pressure Washing", "West Islip Pressure Wash",
                  "Dix Hills Pressure Wash", "Local Long Island Team",
                  "Softwind Exterior Washing"],
            "D": ["We match the washing method to the material, so siding is treated gently.",
                  "Driveways, patios, walkways, pavers and concrete washed and refreshed.",
                  "Tell us what needs cleaning and where. We will send you a free quote.",
                  "Residential pressure washing for Long Island homes. Free quote."]},
    },
    {
        "name": "House Washing Near Me",
        "campaign_id": "24145053510", "campaign": "Power Washing #2",
        "phrase": "house washing near me", "exact": "house washing near me",
        "volume": 40, "trend": -73.3, "bid_low": 10.46, "bid_high": 32.09,
        "competition": "MEDIUM",
        "url": "https://offer.softwindli.com/house-washing-company/",
        "lp_h1": "House Washing Company In Islip, West Islip & Dix Hills, NY",
        "path1": "house-washing", "path2": "free-quote",
        "why": ("The single highest-value text inside the legacy Soft & House Washing "
                "container, and the term the 2026-08-25 audit mistakenly attributed to the "
                "'house washing company near me' ad group. Highest top-of-page ceiling in "
                "the whole set at $32.09. CAUTION: recent trend is -73.3%, so this is a "
                "declining term - included on volume and bid strength, not momentum."),
        "rsa1": {
            "H": ["House Washing Near You", "Local House Washing",
                  "House Washing In Islip", "Long Island House Washing",
                  "Free House Washing Quote", "Siding, Trim And Fences",
                  "Gentle Low-Pressure Wash", "Soft Washing For Siding",
                  "Remove Algae And Mildew", "Serving Islip & West Islip",
                  "House Washing Dix Hills", "Call (631) 502-7946",
                  "Request Your Free Quote", "Cleaner Home Exterior",
                  "Softwind House Washing"],
            "D": ["House washing for siding, trim and fences. Request a free quote today.",
                  "A gentler low-pressure approach for materials that need care.",
                  "Serving Islip, West Islip and Dix Hills homeowners. Free quote.",
                  "House washing near you on Long Island. Call (631) 502-7946."]},
        "rsa2": {
            "H": ["House Washing Near You", "House Washing Company",
                  "Soft Wash For Your Siding", "Algae, Mildew And Pollen",
                  "Trim, Fences And Siding", "Method Chosen For Material",
                  "Cleaner Curb Appeal", "Free Exterior Cleaning Quote",
                  "Tell Us What Needs Washing", "Islip House Washing",
                  "West Islip House Washing", "Dix Hills House Washing",
                  "Local Long Island Team", "Request A Free Estimate",
                  "Softwind Exterior Care"],
            "D": ["We choose the washing method around your siding, trim and surfaces.",
                  "Lower-pressure cleaning for surfaces that should not take force.",
                  "Tell us what needs washing and where. We will send you a free quote.",
                  "House washing for Long Island homes. Free quote at (631) 502-7946."]},
    },
    {
        "name": "Power Washing Long Island",
        "campaign_id": "24103511039", "campaign": "Power Washing",
        "phrase": "power washing long island", "exact": "power washing long island",
        "volume": 40, "trend": 30.8, "bid_low": 8.12, "bid_high": 18.02,
        "competition": "MEDIUM",
        "url": "https://offer.softwindli.com/power-washing-soft-washing/",
        "lp_h1": "Power Washing & Soft Washing in Long Island",
        "path1": "power-washing", "path2": "long-island",
        "why": ("A region-level intent that no live keyword covers. Uniquely, the legacy "
                "landing page /power-washing-soft-washing/ has H1 'Power Washing & Soft "
                "Washing in Long Island' and mentions Long Island 17 times - it is the "
                "BEST-matched published page in the account for this exact intent, which "
                "is the one place the legacy asset genuinely earns its keep. Lowest bid "
                "range of any candidate at $8.12-$18.02."),
        "rsa1": {
            "H": ["Power Washing Long Island", "Long Island Power Washing",
                  "Local Power Washing", "Free Power Washing Quote",
                  "House, Patio And Driveway", "Siding, Concrete And Pavers",
                  "Method Matched To Surface", "Soft Washing For Siding",
                  "Power Washing In Islip NY", "Serving Long Island Homes",
                  "Cleaner Home Exteriors", "Call (631) 502-7946",
                  "Request Your Free Quote", "Exterior Washing Long Island",
                  "Softwind Power Washing"],
            "D": ["Power washing for Long Island homes. Siding, driveways, patios, pavers.",
                  "The cleaning method is chosen for the surface, from concrete to siding.",
                  "Serving Long Island homeowners. Request a free quote, no obligation.",
                  "Long Island power washing. Call (631) 502-7946 or request a quote."]},
        "rsa2": {
            "H": ["Power Washing Long Island", "Long Island Exterior Wash",
                  "Right Pressure, Right Surface", "Low-Pressure Siding Washing",
                  "Driveway And Patio Washing", "Paver And Concrete Washing",
                  "Walkway And Fence Washing", "Restore Your Curb Appeal",
                  "Free Quote On Your Project", "Tell Us What Needs Cleaning",
                  "Local Long Island Team", "Islip Area Power Washing",
                  "Homes Across Long Island", "Request A Free Estimate",
                  "Softwind Exterior Washing"],
            "D": ["We match the washing method to the material, so siding is treated gently.",
                  "Driveways, patios, walkways, pavers and concrete washed and refreshed.",
                  "Tell us what needs cleaning and where. We will send you a free quote.",
                  "Power washing across Long Island. Free quote available."]},
    },
]


def validate(s):
    issues = []
    for tag, ad in (("RSA1", s["rsa1"]), ("RSA2", s["rsa2"])):
        H, D = ad["H"], ad["D"]
        if len(H) != 15:
            issues.append("%s: %d headlines" % (tag, len(H)))
        if len(D) != 4:
            issues.append("%s: %d descriptions" % (tag, len(D)))
        for h in H:
            if len(h) > 30:
                issues.append("%s headline %d chars: %s" % (tag, len(h), h))
        for d in D:
            if len(d) > 90:
                issues.append("%s description %d chars: %s" % (tag, len(d), d))
        if len(set(H)) != len(H):
            issues.append("%s duplicate headline" % tag)
        if len(set(D)) != len(D):
            issues.append("%s duplicate description" % tag)
        for t in H + D:
            m = BANNED.search(t)
            if m:
                issues.append("%s banned claim %r in: %s" % (tag, m.group(0), t))
    if len(s["path1"]) > 15 or len(s["path2"]) > 15:
        issues.append("display path over 15 chars")
    ov = set(s["rsa1"]["H"]) & set(s["rsa2"]["H"])
    if len(ov) > 2:
        issues.append("sibling overlap %d: %s" % (len(ov), sorted(ov)))
    return issues, sorted(ov)


def main() -> int:
    snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
    AG = snap["ad_groups"]
    live_texts = {k["text"] for k in snap["enabled_keywords_live"]}
    # Containers this plan commits to keeping PERMANENTLY PAUSED. A keyword text that
    # exists ONLY inside one of these is a dormant resource, not a serving duplicate.
    LEGACY_PERMANENTLY_PAUSED = {"Pressure & Power Washing", "Soft & House Washing",
                                 "Driveway Patio Concrete Washing"}
    texts_in_legacy = set()
    texts_in_real_skags = set()
    for k in snap["keywords"]:
        g = AG[k["ad_group_id"]]
        if g["name"] in LEGACY_PERMANENTLY_PAUSED:
            texts_in_legacy.add(k["text"])
        else:
            texts_in_real_skags.add(k["text"])

    ok = True
    for s in SKAGS:
        iss, ov = validate(s)
        s["_issues"], s["_overlap"] = iss, ov
        in_live = s["exact"] in live_texts
        in_skag = s["exact"] in texts_in_real_skags
        in_legacy = s["exact"] in texts_in_legacy
        if in_live or in_skag:
            verdict = "DUPLICATE - DO NOT CREATE"
        elif in_legacy:
            verdict = ("SAFE TO CREATE - text exists only inside a legacy container "
                       "this plan keeps PERMANENTLY PAUSED, so it is a dormant "
                       "resource and never a serving duplicate")
        else:
            verdict = "NO DUPLICATE - safe to create"
        s["duplicate_check"] = {
            "exact_text_already_live": in_live,
            "exact_text_in_another_real_skag": in_skag,
            "exact_text_in_permanently_paused_legacy_container": in_legacy,
            "verdict": verdict,
        }
        if iss:
            ok = False
        print("%-28s H/D ok=%s  overlap=%d  dup=%s"
              % (s["name"], not iss, len(ov), s["duplicate_check"]["verdict"]))
        for i in iss:
            print("    !! %s" % i)

    if not ok:
        print("\nVALIDATION FAILED - plan not written")
        return 1

    # split: any SKAG whose text already exists must not be created
    creatable = [s for s in SKAGS
                 if not s["duplicate_check"]["verdict"].startswith("DUPLICATE")]
    blocked = [s for s in SKAGS
               if s["duplicate_check"]["verdict"].startswith("DUPLICATE")]

    print("\ncreatable: %d   blocked as duplicates: %d"
          % (len(creatable), len(blocked)))
    for s in blocked:
        print("   BLOCKED %s - text '%s' is live or in another real SKAG"
              % (s["name"], s["exact"]))

    Path(SNAP / "i2a-skag-validation-2026-08-26.json").write_text(
        json.dumps({"skags": [{k: v for k, v in s.items()} for s in SKAGS],
                    "creatable": [s["name"] for s in creatable],
                    "blocked_as_duplicate": [s["name"] for s in blocked]},
                   indent=2), encoding="utf-8")
    print("\nvalidation written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
