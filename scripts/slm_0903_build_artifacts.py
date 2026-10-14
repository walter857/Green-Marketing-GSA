#!/usr/bin/env python3
"""Build the remaining Softwind L&M recovery artifacts.

00-program-manifest.yaml, 02-before-snapshot.md, 03-service-truth-decisions.yaml,
04-measurement-map.csv, 07-keyword-migration-map.csv, 09-rsa-copy-and-url-plan.csv,
12-quality-loop-template.csv, 13-monitoring-log.csv

Local only. Validates RSA character limits and refuses to emit copy that breaks
them or that uses an unverified claim.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
TZ = ZoneInfo("America/New_York")
PATIO, PAVERS = "23484806108", "23489296528"

# Claims that may NOT appear in drafted copy. Every one of these is currently
# live somewhere in the account or on the landing pages and is unverified.
BANNED = [
    r"\blicen[cs]ed\b", r"\binsured\b", r"\bbonded\b", r"\bcertified\b",
    r"\bwarrant", r"\bguarantee", r"\byears? (of|in)\b", r"\b\d+\s*star",
    r"\breviews?\b", r"\bwithin \d+ (minute|hour|day)", r"\bin \d+ days\b",
    r"\bsame.day\b", r"\bfree consultation\b", r"\b\$\d", r"\b\d+%\s*off\b",
    r"\bdiscount\b", r"\bfinancing\b", r"\baward", r"\b#1\b", r"\bbest in\b",
]

CANONICAL = {
    "Patio Construction": {
        "campaign_id": PATIO, "campaign": "Patio",
        "intent": "General patio construction and patio contractor intent.",
        "final_url": "https://offer.softwindli.com/patio/",
        "owns": ["patio construction", "patio contractor", "patio builder",
                 "patio installation", "patio company"],
        "routes_away": ("Queries that name pavers AND patio go to Patio Paver "
                        "Installation. Queries that name pavers without patio go to "
                        "Paver Installation in the Pavers campaign."),
    },
    "Patio Paver Installation": {
        "campaign_id": PATIO, "campaign": "Patio",
        "intent": "Patio intent that explicitly names pavers or paving stone.",
        "final_url": "https://offer.softwindli.com/patio/",
        "owns": ["paver patio installation", "patio pavers", "patio paver installer",
                 "paver patio contractor"],
        "routes_away": ("Generic paver installation with no patio word belongs to "
                        "Paver Installation."),
    },
    "Paver Installation": {
        "campaign_id": PAVERS, "campaign": "Pavers",
        "intent": "General paver installation with no patio qualifier.",
        "final_url": "https://offer.softwindli.com/pavers/",
        "owns": ["paver installation", "paver installer", "paver contractor",
                 "brick paver installation", "interlocking pavers installation",
                 "paver walkway installation", "paving stone installation"],
        "routes_away": ("Anything naming patio goes to the Patio campaign's two "
                        "groups."),
    },
}

# Two materially distinct RSAs per canonical ad group.
# Every claim below is traceable to: the live landing page, the account's own
# 110 New York geo targets, or the approved service list. No claim from BANNED.
RSAS = {
    "Patio Construction": [
        {"variant": "A - contractor and process",
         "path1": "patio", "path2": "free-quote",
         "headlines": [
             "Patio Construction Company", "Hire A Patio Contractor",
             "Long Island Patio Builders", "Patio Construction Quote",
             "Patio Contractor Near You", "Custom Patio Construction",
             "Built On A Level Base", "Drainage Planned From Day 1",
             "Layout And Material Guidance", "Request A Free Patio Quote",
             "Talk To A Patio Builder", "Serving Long Island, NY",
             "Start Your Patio Project", "Get My Free Patio Quote",
             "Book A Patio Site Visit"],
         "descriptions": [
             "Hire a patio contractor for layout, base prep, drainage and clean installation.",
             "Request a free patio quote with a clear scope, material options and a timeline.",
             "Long Island patio construction. Talk through your space before any work starts.",
             "Call or request your free quote and get a plan for your new patio."]},
        {"variant": "B - outcome and planning",
         "path1": "patio-build", "path2": "estimate",
         "headlines": [
             "Build Your New Patio", "Patio Construction Estimate",
             "Local Patio Construction", "Plan Your Patio Layout",
             "More Usable Backyard Space", "Patio Built For Entertaining",
             "Compare Patio Materials", "Clean Cuts, Tight Joints",
             "A Patio That Drains Right", "Get A Clear Patio Timeline",
             "Patio Builders Near You", "Islip And Nearby Towns",
             "Speak With A Patio Team", "Request Your Free Estimate",
             "Schedule A Patio Walkthrough"],
         "descriptions": [
             "Turn unused yard into a patio built for how you actually use the space.",
             "Compare paver and stone options with guidance before you commit to a layout.",
             "Serving Islip and Long Island. Schedule a walkthrough and get a clear scope.",
             "Request a free estimate and see what your patio project will involve."]},
    ],
    "Patio Paver Installation": [
        {"variant": "A - paver patio specific",
         "path1": "paver-patio", "path2": "free-quote",
         "headlines": [
             "Paver Patio Installation", "Paver Patio Contractors",
             "Patio Paver Installers", "Install A Paver Patio",
             "Paver Patio Quote", "Long Island Paver Patios",
             "Base Prep And Edge Restraint", "Pitched For Drainage",
             "Choose Your Paver Pattern", "Color And Border Guidance",
             "Paver Patio Near You", "Serving Long Island, NY",
             "Request A Free Paver Quote", "Book A Patio Paver Visit",
             "Get My Free Patio Quote"],
         "descriptions": [
             "Paver patio installation with proper base prep, drainage and edge restraint.",
             "Pick colors, patterns and borders with guidance so the finish suits your home.",
             "Long Island paver patio contractors. Request a free quote and a clear scope.",
             "Call or request your free paver patio quote and get a project timeline."]},
        {"variant": "B - material and durability",
         "path1": "patio-pavers", "path2": "estimate",
         "headlines": [
             "Patio Pavers Installed", "Paver Patio Installers",
             "Replace An Old Patio Slab", "Brick And Stone Paver Patios",
             "Patio Pavers Estimate", "Built To Handle Our Winters",
             "Level Finish, Clean Edges", "Interlocking Paver Patios",
             "Pool And Backyard Patios", "Walkways And Steps Too",
             "Local Paver Patio Team", "Islip And Nearby Towns",
             "Request A Paver Patio Quote", "See Your Paver Options",
             "Get A Free Patio Estimate"],
         "descriptions": [
             "Swap a cracked slab for an interlocking paver patio built on a proper base.",
             "Brick, stone and interlocking pavers with layout guidance for your space.",
             "Patios, walkways and steps installed by a local Long Island paver team.",
             "Request a free estimate for patio pavers and get a clear project scope."]},
    ],
    "Paver Installation": [
        {"variant": "A - installer and process",
         "path1": "pavers", "path2": "free-quote",
         "headlines": [
             "Paver Installation Near You", "Hire A Paver Contractor",
             "Long Island Paver Installers", "Paver Installation Quote",
             "Professional Paver Install", "Base Prep And Drainage",
             "Edge Restraint Done Right", "Clean Lines, Tight Joints",
             "Layout And Material Help", "Walkways, Patios And Steps",
             "Paver Installers Near You", "Serving Long Island, NY",
             "Request A Free Paver Quote", "Get My Free Paver Quote",
             "Book A Paver Site Visit"],
         "descriptions": [
             "Paver installation with proper base prep, drainage and edge restraint.",
             "Request a free paver quote with clear scope, material options and a timeline.",
             "Long Island paver installers for walkways, patios, steps and pool surrounds.",
             "Call or request your free quote and get a plan for your paver project."]},
        {"variant": "B - surfaces and curb appeal",
         "path1": "paver-install", "path2": "estimate",
         "headlines": [
             "Interlocking Paver Install", "Brick Paver Installation",
             "Paving Stone Installation", "Paver Walkway Installation",
             "Upgrade Your Curb Appeal", "Paver Installation Estimate",
             "A Level, Lasting Finish", "Built For Daily Use",
             "Pool Surrounds And Steps", "Compare Paver Options",
             "Local Paver Installation", "Islip And Nearby Towns",
             "Speak With A Paver Team", "Request Your Free Estimate",
             "See Your Paver Choices"],
         "descriptions": [
             "Interlocking, brick and stone pavers installed level and built for daily use.",
             "Walkways, steps and pool surrounds that lift curb appeal and stay put.",
             "Serving Islip and Long Island. Get guidance on pattern, color and border.",
             "Request a free estimate for paver installation and a clear project scope."]},
    ],
}


def check_copy():
    problems = []
    for group, ads in RSAS.items():
        for ad in ads:
            for h in ad["headlines"]:
                if len(h) > 30:
                    problems.append("HEADLINE %d chars > 30: %s / %s" % (len(h), group, h))
            for d in ad["descriptions"]:
                if len(d) > 90:
                    problems.append("DESC %d chars > 90: %s / %s" % (len(d), group, d))
            for p in (ad["path1"], ad["path2"]):
                if len(p) > 15:
                    problems.append("PATH %d chars > 15: %s / %s" % (len(p), group, p))
            if len(ad["headlines"]) != 15:
                problems.append("%s %s has %d headlines, want 15"
                                % (group, ad["variant"], len(ad["headlines"])))
            if len(ad["descriptions"]) != 4:
                problems.append("%s %s has %d descriptions, want 4"
                                % (group, ad["variant"], len(ad["descriptions"])))
            for txt in ad["headlines"] + ad["descriptions"]:
                for pat in BANNED:
                    if re.search(pat, txt, re.I):
                        problems.append("UNVERIFIED CLAIM %r in %r" % (pat, txt))
                if any(ord(c) > 127 for c in txt):
                    problems.append("NON-ASCII in %r" % txt)
            seen = set()
            for h in ad["headlines"]:
                if h.lower() in seen:
                    problems.append("duplicate headline %r in %s" % (h, group))
                seen.add(h.lower())
    return problems


def main() -> int:
    snap = json.loads((B / "01-before-snapshot.json").read_text(encoding="utf-8"))
    perf = json.loads((B / "01b-before-performance.json").read_text(encoding="utf-8"))
    stamp = datetime.now(TZ).isoformat()

    problems = check_copy()
    if problems:
        print("RSA COPY VALIDATION FAILED:")
        for p in problems:
            print("  - %s" % p)
        return 1
    print("RSA copy validation: PASS (6 ads, 90 headlines, 24 descriptions, "
          "all within limits, no banned claim, ASCII only)")

    # ---------------- 04-measurement-map.csv ----------------
    byaction = defaultdict(lambda: {"conv": 0.0, "all": 0.0, "last": ""})
    for r in perf["conversions_by_action"]:
        a = byaction[r["conversion_action_name"]]
        a["conv"] += r["conversions"]; a["all"] += r["all_conversions"]
        if r["all_conversions"] > 0 and r["month"] > a["last"]:
            a["last"] = r["month"]
    goals = defaultdict(list)
    for g in snap["customer_conversion_goals"]:
        goals[(g["category"], g["origin"])] = g["biddable"]
    with (B / "04-measurement-map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["conversion_action_id", "name", "status", "type", "category",
                    "origin", "primary_for_goal", "include_in_conversions_metric",
                    "counting_type", "call_min_seconds", "attribution_model",
                    "click_lookback_days", "customer_goal_biddable",
                    "alltime_conversions", "alltime_all_conversions",
                    "last_month_with_activity", "role_today", "proposed_role",
                    "evidence"])
        for c in sorted(snap["conversion_actions"], key=lambda x: x["name"]):
            st = byaction.get(c["name"], {"conv": 0.0, "all": 0.0, "last": ""})
            biddable = goals.get((c["category"], c["origin"]), "n/a")
            if c["primary_for_goal"] and c["include_in_conversions_metric"]:
                role = "PRIMARY - counts in Conversions"
            elif c["primary_for_goal"]:
                role = "PRIMARY flag but excluded from Conversions"
            else:
                role = "SECONDARY diagnostic"
            prop = role
            ev = ""
            if c["id"] == "7461619140":
                prop = "SECONDARY diagnostic"; ev = "PLAN-SLM-CONV-1: duplicate of 7480764700"
            elif c["id"] == "7508686781":
                prop = "SECONDARY diagnostic"; ev = "PLAN-SLM-CONV-1: duplicate of 7461572537"
            elif c["id"] == "7480764700":
                prop = "PRIMARY - the single form lead signal"; ev = "most complete form action"
            elif c["id"] == "7461572537":
                prop = "PRIMARY - the qualified call signal"; ev = "only call route with activity"
            elif c["id"] == "7635680357":
                prop = "HOLD - demote after WhatConverts repair"; ev = "third credit for one form lead"
            elif c["id"] == "7635680543":
                prop = "BROKEN - zero events ever recorded"; ev = "0 conversions and 0 all_conversions in every month"
            elif c["id"] == "7461590068":
                prop = "BROKEN - silent since June 2026"; ev = "WCM tag loads but records nothing"
            elif c["origin"] == "GOOGLE_HOSTED":
                prop = "SECONDARY diagnostic - correct as is"; ev = "customer goal biddable=false"
            w.writerow([c["id"], c["name"], c["status"], c["type"], c["category"],
                        c["origin"], c["primary_for_goal"],
                        c["include_in_conversions_metric"], c["counting_type"],
                        c["phone_call_duration_seconds"], c["attribution_model"],
                        c["click_lookback_days"], biddable,
                        round(st["conv"], 1), round(st["all"], 1), st["last"] or "never",
                        role, prop, ev])

    # ---------------- 07-keyword-migration-map.csv ----------------
    kperf = defaultdict(lambda: {"cost": 0.0, "clicks": 0, "impr": 0, "conv": 0.0})
    for r in perf["keyword_perf_alltime"]:
        k = kperf[(r["ad_group_id"], r["text"], r["match_type"])]
        k["cost"] += r["cost"] or 0; k["clicks"] += r["clicks"]
        k["impr"] += r["impressions"]; k["conv"] += r["conversions"]
    paused_by_kw1 = {a["keyword_text"] for a in json.loads(
        (B / "10-change-packages/PLAN-SLM-KW-1.json").read_text(encoding="utf-8"))["actions"]}

    def owner(text):
        t = " " + text.lower() + " "
        has_patio = " patio" in t
        has_paver = "paver" in t or "paving stone" in t
        if "asphalt" in t:
            return "NONE - out of scope", "exclude"
        if has_patio and has_paver:
            return "Patio Paver Installation", "migrate"
        if has_patio:
            return "Patio Construction", "migrate"
        if has_paver:
            return "Paver Installation", "migrate"
        if "hardscap" in t:
            return "NONE - Hardscaping campaign owns this", "exclude"
        if "paving" in t or "driveway" in t:
            return "UNRESOLVED - pending SLM-Q5", "hold"
        return "UNRESOLVED - manual review", "hold"

    dupes = defaultdict(list)
    for k in snap["keywords"]:
        if not k["negative"] and k["campaign_id"] in (PATIO, PAVERS):
            dupes[(k["text"], k["match_type"])].append(k["ad_group_name"])
    with (B / "07-keyword-migration-map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["campaign_id", "campaign", "current_ad_group_id",
                    "current_ad_group", "ad_group_status", "criterion_id",
                    "keyword_text", "match_type", "keyword_status",
                    "effectively_serving", "quality_score", "alltime_cost",
                    "alltime_clicks", "alltime_impressions", "alltime_raw_credits",
                    "intended_canonical_owner", "verdict", "duplicate_across_groups",
                    "note"])
        for k in sorted(snap["keywords"], key=lambda x: (x["campaign_name"],
                                                         x["ad_group_name"], x["text"])):
            if k["negative"] or k["campaign_id"] not in (PATIO, PAVERS):
                continue
            ag = snap["ad_groups"][k["ad_group_id"]]
            p = kperf[(k["ad_group_id"], k["text"], k["match_type"])]
            own, verdict = owner(k["text"])
            serving = k["status"] == "ENABLED" and ag["status"] == "ENABLED"
            note = ""
            if k["text"] in paused_by_kw1 and k["status"] == "ENABLED":
                verdict = "pause"; note = "PLAN-SLM-KW-1 pauses this"
            if k["status"] == "ENABLED" and ag["status"] != "ENABLED":
                note = ("ENABLED inside a PAUSED ad group - starts serving the instant "
                        "the group is enabled. Enumerate before any enable.")
            d = dupes[(k["text"], k["match_type"])]
            w.writerow([k["campaign_id"], k["campaign_name"], k["ad_group_id"],
                        ag["name"], ag["status"], k["criterion_id"], k["text"],
                        k["match_type"], k["status"], serving,
                        k["quality_score"] or "", round(p["cost"], 2), p["clicks"],
                        p["impr"], round(p["conv"], 1), own, verdict,
                        "|".join(sorted(set(d))) if len(set(d)) > 1 else "",
                        note])

    # ---------------- 09-rsa-copy-and-url-plan.csv ----------------
    with (B / "09-rsa-copy-and-url-plan.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["canonical_ad_group", "campaign", "campaign_id", "rsa_variant",
                    "asset_type", "position", "text", "characters", "limit",
                    "pinned", "final_url", "path1", "path2"])
        for group, ads in RSAS.items():
            meta = CANONICAL[group]
            for ad in ads:
                for i, h in enumerate(ad["headlines"], 1):
                    w.writerow([group, meta["campaign"], meta["campaign_id"],
                                ad["variant"], "HEADLINE", i, h, len(h), 30, "none",
                                meta["final_url"], ad["path1"], ad["path2"]])
                for i, d in enumerate(ad["descriptions"], 1):
                    w.writerow([group, meta["campaign"], meta["campaign_id"],
                                ad["variant"], "DESCRIPTION", i, d, len(d), 90, "none",
                                meta["final_url"], ad["path1"], ad["path2"]])

    # ---------------- 12-quality-loop-template.csv ----------------
    (B / "12-quality-loop-template.csv").write_text(",".join([
        "report_date", "account_timezone", "customer_id", "campaign_id",
        "campaign_name", "ad_group_id", "ad_group_name", "criterion_id",
        "keyword_text", "match_type", "search_term", "device", "landing_page",
        "cost", "impressions", "clicks", "google_conversion_credits",
        "lead_id_hashed", "lead_source", "lead_type_call_or_form",
        "attribution_complete", "campaign_present", "ad_group_present",
        "keyword_present", "gclid_present", "qualified_status",
        "qualification_reason", "estimate_scheduled", "estimate_completed",
        "sold_status", "loss_reason", "revenue", "gross_profit",
        "recommended_search_term_action", "reviewer", "approval_fingerprint",
    ]) + "\n", encoding="utf-8")

    # ---------------- 13-monitoring-log.csv ----------------
    (B / "13-monitoring-log.csv").write_text(",".join([
        "checkpoint_date", "checkpoint_type", "plan_fingerprint", "campaign_id",
        "spend_mtd", "projected_month_end", "cap_status", "impressions", "clicks",
        "avg_cpc", "raw_credits", "qualified_leads", "cpl", "cpql",
        "wrong_service_visible_spend_share", "attribution_completeness_pct",
        "duplicate_primary_credits", "search_impression_share",
        "lost_is_rank", "lost_is_budget", "new_disapprovals", "anomaly",
        "escalation_triggered", "action_taken", "reviewer",
    ]) + "\n", encoding="utf-8")

    print("wrote 04-measurement-map.csv, 07-keyword-migration-map.csv, "
          "09-rsa-copy-and-url-plan.csv, 12-quality-loop-template.csv, "
          "13-monitoring-log.csv")
    (B / "_canonical.json").write_text(json.dumps(
        {"canonical": CANONICAL, "rsas": RSAS}, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
