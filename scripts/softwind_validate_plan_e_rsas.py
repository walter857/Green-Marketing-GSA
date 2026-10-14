#!/usr/bin/env python3
"""Validate the PLAN-E drafted RSAs before they enter the plan file. Local only."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients/softwind-power-washing/plans/2026-08-25-plan-e-rsa-validation.json"

# Claims verified on the live pages / client site 2026-08-25. Anything outside
# this vocabulary must not appear.
BANNED = re.compile(
    r"\b(licensed|insured|bonded|certified|guarantee[ds]?|warrant|"
    r"\d+\s*(years?|yrs?)|since\s*\d{4}|award|rated|rating|stars?|reviews?|"
    r"\d+\s*%|\$\d|cheap|discount|sale|deal|coupon|promo|"
    r"same[- ]day|24/7|emergency|instant|immediately|fastest|"
    r"best|#1|number one|top rated|voted|trusted by|"
    r"roof|gutter|seal(ing|er|ant)|masonry|landscap|paint)\b", re.I)

ADS = {
    "Pressure Washing Near Me / RSA 1": {
        "final_url": "https://offer.softwindli.com/residential-pressure-washing/",
        "path1": "pressure-wash", "path2": "free-quote",
        "H": ["Pressure Washing Near You", "Local Pressure Washing",
              "Pressure Washing In Islip", "Long Island Pressure Wash",
              "Free Pressure Washing Quote", "Residential Pressure Wash",
              "Driveways, Patios & Siding", "Pavers, Concrete & Walkways",
              "Method Matched To Surface", "Soft Washing For Siding",
              "Serving Islip & West Islip", "Pressure Washing Dix Hills",
              "Call (631) 502-7946", "Request Your Free Quote",
              "Softwind Pressure Washing"],
        "pins": {0: "HEADLINE_1", 1: "HEADLINE_1"},
        "D": ["Local pressure washing for driveways, patios, pavers and siding. Request a free quote.",
              "The washing method is chosen for the surface, from hard concrete to delicate siding.",
              "Serving Islip, West Islip and Dix Hills homeowners. Free quote, no obligation.",
              "Pressure washing near you on Long Island. Call (631) 502-7946 or request a quote."],
    },
    "Pressure Washing Near Me / RSA 2": {
        "final_url": "https://offer.softwindli.com/residential-pressure-washing/",
        "path1": "pressure-wash", "path2": "islip",
        "H": ["Pressure Washing Near You", "Exterior Washing Near You",
              "Right Pressure, Right Surface", "Low-Pressure Siding Washing",
              "Driveway And Patio Washing", "Paver And Concrete Washing",
              "Walkway And Fence Washing", "Cleaner Home Exteriors",
              "Free Quote On Your Project", "Tell Us What Needs Cleaning",
              "Islip Pressure Washing", "West Islip Pressure Wash",
              "Dix Hills Pressure Wash", "Local Long Island Team",
              "Softwind Exterior Washing"],
        "pins": {0: "HEADLINE_1", 1: "HEADLINE_1"},
        "D": ["We match the washing method to the material, so siding is treated gently.",
              "Driveways, patios, walkways, pavers and concrete washed and refreshed.",
              "Tell us what needs cleaning and where. We will send you a free quote.",
              "Residential pressure washing for Long Island homes. Free quote available."],
    },
    "House Washing Near Me / RSA 1": {
        "final_url": "https://offer.softwindli.com/house-washing-company/",
        "path1": "house-washing", "path2": "free-quote",
        "H": ["House Washing Near You", "Local House Washing",
              "House Washing In Islip", "Long Island House Washing",
              "Free House Washing Quote", "Siding, Trim And Fences",
              "Gentle Low-Pressure Wash", "Soft Washing For Siding",
              "Remove Algae And Mildew", "Serving Islip & West Islip",
              "House Washing Dix Hills", "Call (631) 502-7946",
              "Request Your Free Quote", "Cleaner Home Exterior",
              "Softwind House Washing"],
        "pins": {0: "HEADLINE_1", 1: "HEADLINE_1"},
        "D": ["House washing for siding, trim and fences. Request a free quote today.",
              "A gentler low-pressure approach for materials that need careful handling.",
              "Serving Islip, West Islip and Dix Hills homeowners. Free quote, no obligation.",
              "House washing near you on Long Island. Call (631) 502-7946 or request a quote."],
    },
    "House Washing Near Me / RSA 2": {
        "final_url": "https://offer.softwindli.com/house-washing-company/",
        "path1": "house-washing", "path2": "islip",
        "H": ["House Washing Near You", "House Washing Company",
              "Soft Wash For Your Siding", "Algae, Mildew And Pollen",
              "Trim, Fences And Siding", "Method Chosen For Material",
              "Cleaner Curb Appeal", "Free Exterior Cleaning Quote",
              "Tell Us What Needs Washing", "Islip House Washing",
              "West Islip House Washing", "Dix Hills House Washing",
              "Local Long Island Team", "Request A Free Estimate",
              "Softwind Exterior Care"],
        "pins": {0: "HEADLINE_1", 1: "HEADLINE_1"},
        "D": ["We choose the washing method around your siding, trim and exterior surfaces.",
              "Lower-pressure cleaning for surfaces that should not take aggressive force.",
              "Tell us what needs washing and where. We will send you a free quote.",
              "House washing for Long Island homes. Free quote at (631) 502-7946."],
    },
}


def main() -> int:
    report = {}
    ok = True
    for name, a in ADS.items():
        issues = []
        H, D = a["H"], a["D"]
        if len(H) != 15:
            issues.append("expected 15 headlines, got %d" % len(H))
        if len(D) != 4:
            issues.append("expected 4 descriptions, got %d" % len(D))
        for h in H:
            if len(h) > 30:
                issues.append("headline over 30 (%d): %s" % (len(h), h))
        for d in D:
            if len(d) > 90:
                issues.append("description over 90 (%d): %s" % (len(d), d))
        if len(set(H)) != len(H):
            issues.append("duplicate headline within the ad")
        if len(set(D)) != len(D):
            issues.append("duplicate description within the ad")
        for t in H + D:
            m = BANNED.search(t)
            if m:
                issues.append("unverified/out-of-scope claim %r in: %s" % (m.group(0), t))
        if len(a["path1"]) > 15 or len(a["path2"]) > 15:
            issues.append("display path over 15 characters")
        report[name] = {
            "final_url": a["final_url"],
            "path1": a["path1"], "path2": a["path2"],
            "headline_count": len(H), "description_count": len(D),
            "max_headline_len": max(len(h) for h in H),
            "max_description_len": max(len(d) for d in D),
            "pinned_headline_1_count": len(a["pins"]),
            "headlines": [{"text": h, "len": len(h),
                           "pinned": a["pins"].get(i)} for i, h in enumerate(H)],
            "descriptions": [{"text": d, "len": len(d)} for d in D],
            "issues": issues,
        }
        if issues:
            ok = False

    # sibling overlap per ad group
    for ag in ("Pressure Washing Near Me", "House Washing Near Me"):
        a = set(ADS["%s / RSA 1" % ag]["H"])
        b = set(ADS["%s / RSA 2" % ag]["H"])
        ov = sorted(a & b)
        report["%s :: sibling overlap" % ag] = {
            "shared_headlines": len(ov), "shared": ov,
            "pct": round(100 * len(ov) / 15, 1),
            "note": "Only the pinned HEADLINE_1 variant is intentionally shared."}
        if len(ov) > 2:
            report["%s :: sibling overlap" % ag]["issues"] = ["overlap above 2"]
            ok = False

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for k, v in report.items():
        if "sibling overlap" in k:
            print("%-42s overlap %d/15 (%.0f%%) %s"
                  % (k, v["shared_headlines"], v["pct"], v["shared"]))
            continue
        print("%-34s H=%d D=%d maxH=%d maxD=%d pins=%d  %s"
              % (k, v["headline_count"], v["description_count"],
                 v["max_headline_len"], v["max_description_len"],
                 v["pinned_headline_1_count"],
                 "OK" if not v["issues"] else "ISSUES"))
        for i in v["issues"]:
            print("      !! %s" % i)
    print()
    print("ALL PLAN-E RSA VALIDATION PASSED" if ok else "VALIDATION FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
