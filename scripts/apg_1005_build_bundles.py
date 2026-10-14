#!/usr/bin/env python3
"""2026-10-05 DRAFT ONLY: build, validate and fingerprint the Apogee change bundles.

Writes plan YAMLs under clients/apogee-lawns/plans/ and a fingerprint index. Validates copy
limits, pinned-H1 installation signal, claims against TODAY's captured page text, URLs,
keyword/negative reachability both ways, resource IDs against the fresh snapshot, and
mutation counts. Fingerprint = gm_gsa.safety.approval_code(plan as written). Nothing is sent
to any external system by this script.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

CL = ROOT / "clients" / "apogee-lawns"
PLANS = CL / "plans"
AUD = CL / "audits" / "2026-10-05-conversion-plan"
SNAP = json.loads((CL / "snapshots" / "2026-10-05-conversion-plan-snapshot.json").read_text(encoding="utf-8"))
LP_TEXT = (AUD / "browser-qa" / "lp-fulltext.txt").read_text(encoding="utf-8").lower()
MAIN_TEXT = (AUD / "browser-qa" / "main-fulltext.txt").read_text(encoding="utf-8").lower()
LP = "https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/"
CID, NAME, MCC = "8164626278", "Apogee Lawns LLC - Live", "3373711342"
CAMP = "24257151015"
AG1, AG2 = "200347713516", "200347713556"
problems: list[str] = []


def check(ok: bool, msg: str) -> None:
    if not ok:
        problems.append(msg)


# ------------------------------------------------------------------ claim registry (verified today)
CLAIMS = {
    "CL1_professional_installation": [("lp", "leave the installation to a pro"), ("lp", "professional permanent-light installation"), ("main", "professional install")],
    "CL2_roofline_or_eaves": [("lp", "along the property’s roofline or eaves")],
    "CL3_app_colors_patterns_schedules": [("lp", "app-controlled colors, patterns, and schedules")],
    "CL4_year_round_holidays_game_days": [("lp", "christmas, celebrations, game days, and everyday accent lighting")],
    "CL5_homes_and_businesses": [("lp", "options for homes and businesses"), ("main", "homes & businesses")],
    "CL6_free_estimate": [("lp", "request a free estimate"), ("lp", "get my free quote")],
    "CL7_not_annual_hanging": [("lp", "not annual light hanging, removal, or storage")],
    "CL8_lincoln_area": [("lp", "installation in lincoln, ne")],
    "CL9_free_consultation_custom_design": [("main", "free consultation and custom design"), ("lp", "designed around your property")],
    "CL10_pricing_roofline_footage": [("main", "linear footage of your roofline"), ("main", "complexity of your home")],
    "POS_skip_diy": [],   # positioning statement, not a factual claim about Apogee
    "KW_keyword_relevance": [],
}
for cid, sources in CLAIMS.items():
    for where, phrase in sources:
        text = LP_TEXT if where == "lp" else MAIN_TEXT
        check(phrase.lower() in text, f"claim {cid}: phrase not found today on {where}: {phrase!r}")

BANNED = re.compile(r"warrant|guarantee|%|\$|rating|review|star|veteran|everlight|omaha|24/7|same[- ]day|fast|"
                    r"near me|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b|million|alexa|google home|one day", re.I)
INSTALL = re.compile(r"install", re.I)


def rsa(ad_group: str, path1: str, path2: str, h: list[tuple], d: list[tuple]) -> dict:
    return {"ad_group_id": ad_group, "final_urls": [LP], "path1": path1, "path2": path2, "status": "PAUSED",
            "headlines": [{"text": t, "pinned_field": p, "claims": c} for t, p, c in h],
            "descriptions": [{"text": t, "claims": c} for t, c in d]}


RSA_AG1 = rsa(AG1, "permanent", "installation", [
    ("Permanent Light Installation", "HEADLINE_1", ["CL1_professional_installation"]),
    ("Permanent Lights Installed", "HEADLINE_1", ["CL1_professional_installation"]),
    ("Pro Permanent Light Installers", "HEADLINE_1", ["CL1_professional_installation"]),
    ("Installed Along Your Roofline", None, ["CL2_roofline_or_eaves"]),
    ("Lincoln-Area Installation", None, ["CL8_lincoln_area", "CL1_professional_installation"]),
    ("Free Custom Lighting Design", None, ["CL9_free_consultation_custom_design"]),
    ("Request a Free Estimate", None, ["CL6_free_estimate"]),
    ("Homes and Businesses", None, ["CL5_homes_and_businesses"]),
    ("App-Controlled Colors", None, ["CL3_app_colors_patterns_schedules"]),
    ("Lights for Every Holiday", None, ["CL4_year_round_holidays_game_days"]),
    ("No Yearly Hanging or Removal", None, ["CL7_not_annual_hanging"]),
    ("Installed Once, Used All Year", None, ["CL4_year_round_holidays_game_days", "CL7_not_annual_hanging"]),
], [
    ("Apogee Lawns professionally installs permanent lights along your roofline. Free estimate.",
     ["CL1_professional_installation", "CL2_roofline_or_eaves", "CL6_free_estimate"]),
    ("Get a free consultation and custom lighting design for your Lincoln-area home or business.",
     ["CL9_free_consultation_custom_design", "CL8_lincoln_area", "CL5_homes_and_businesses"]),
    ("Choose colors, patterns and schedules in the app for holidays, game days and every day.",
     ["CL3_app_colors_patterns_schedules", "CL4_year_round_holidays_game_days"]),
    ("A permanent lighting system, not yearly hanging, removal or storage. Request an estimate.",
     ["CL7_not_annual_hanging", "CL6_free_estimate"]),
])
RSA_AG2 = rsa(AG2, "permanent", "installation", [
    ("Pro-Installed Permanent Lights", "HEADLINE_1", ["CL1_professional_installation"]),
    ("Permanent Light Installation", "HEADLINE_1", ["CL1_professional_installation"]),
    ("Permanent Lights Installed", "HEADLINE_1", ["CL1_professional_installation"]),
    ("Permanent Christmas Lights", None, ["KW_keyword_relevance"]),
    ("Skip the DIY Light Kit", None, ["POS_skip_diy"]),
    ("Installed Along Your Roofline", None, ["CL2_roofline_or_eaves"]),
    ("Free Custom Lighting Design", None, ["CL9_free_consultation_custom_design"]),
    ("Request a Free Estimate", None, ["CL6_free_estimate"]),
    ("Lincoln Permanent Lighting", None, ["CL8_lincoln_area"]),
    ("App-Controlled Colors", None, ["CL3_app_colors_patterns_schedules"]),
    ("Christmas and Every Holiday", None, ["CL4_year_round_holidays_game_days"]),
    ("Homes and Businesses", None, ["CL5_homes_and_businesses"]),
], [
    ("Get permanent Christmas lights professionally installed on your Lincoln-area home.",
     ["CL1_professional_installation", "CL8_lincoln_area"]),
    ("Compare options with a free estimate and a lighting design built around your property.",
     ["CL6_free_estimate", "CL9_free_consultation_custom_design"]),
    ("Choose colors, patterns and schedules from the app after professional installation.",
     ["CL3_app_colors_patterns_schedules", "CL1_professional_installation"]),
    ("Pricing is based on your roofline footage and home's architecture. Get a free estimate.",
     ["CL10_pricing_roofline_footage", "CL6_free_estimate"]),
])
CALLOUT = {"text": "Free Estimates", "claims": ["CL6_free_estimate"]}
SITELINKS_DRAFT = [  # LP-consistent descriptions; destinations need developer anchors (not yet present)
    ("Request a Free Estimate", "Free estimate for permanent lights", "Tell us about your property", "#estimate"),
    ("How Installation Works", "Request, plan, then install", "Installed along your roofline", "#how-it-works"),
    ("Custom Lighting Design", "Designed around your property", "Free consultation and design", "#design"),
    ("App-Controlled Colors", "Colors, patterns and schedules", "For every holiday and occasion", "#app-control"),
    ("Permanent Lighting FAQ", "Year-round use and controls", "How estimates are priced", "#faq"),
    ("Homes and Businesses", "Residential lighting options", "Commercial lighting options", "#homes-businesses"),
]

# ------------------------------------------------------------------ copy validation
for label, ad in (("RSA_AG1", RSA_AG1), ("RSA_AG2", RSA_AG2)):
    hs, ds = ad["headlines"], ad["descriptions"]
    check(3 <= len(hs) <= 15 and 2 <= len(ds) <= 4, f"{label}: headline/description counts")
    check(len({h["text"].lower() for h in hs}) == len(hs), f"{label}: duplicate headline")
    check(len({x["text"].lower() for x in ds}) == len(ds), f"{label}: duplicate description")
    check(len(ad["path1"]) <= 15 and len(ad["path2"]) <= 15, f"{label}: path length")
    pinned = [h for h in hs if h["pinned_field"] == "HEADLINE_1"]
    check(len(pinned) >= 2, f"{label}: fewer than 2 pinned H1 options")
    for h in pinned:
        check(bool(INSTALL.search(h["text"])), f"{label}: pinned H1 lacks installation signal: {h['text']}")
    for h in hs:
        check(len(h["text"]) <= 30, f"{label}: headline >30: {h['text']}")
        check(not BANNED.search(h["text"]), f"{label}: banned/unsupported wording: {h['text']}")
        check(all(c in CLAIMS for c in h["claims"]), f"{label}: unknown claim id on {h['text']}")
    for x in ds:
        check(len(x["text"]) <= 90, f"{label}: description >90 ({len(x['text'])}): {x['text']}")
        check(not BANNED.search(x["text"]), f"{label}: banned/unsupported wording: {x['text']}")
        check(all(c in CLAIMS for c in x["claims"]), f"{label}: unknown claim id on {x['text']}")
    check(ad["final_urls"] == [LP], f"{label}: final URL is not the verified paid page")
check(len(CALLOUT["text"]) <= 25 and not BANNED.search(CALLOUT["text"]), "callout")
for t, d1, d2, _ in SITELINKS_DRAFT:
    check(len(t) <= 25 and len(d1) <= 35 and len(d2) <= 35, f"sitelink length: {t}")
    check(not any(BANNED.search(s) for s in (t, d1, d2)), f"sitelink wording: {t}")
existing_callouts = {x["asset"].get("callout_asset", {}).get("callout_text", "").lower() for x in SNAP["campaign_asset"]}
check(CALLOUT["text"].lower() not in existing_callouts, "callout duplicates an existing callout")

# ------------------------------------------------------------------ resource IDs + keyword/negative logic
ads_by_id = {a["ad"]["id"]: a for a in SNAP["ads"]}
for ad_id in ("825023783007", "825023783010", "825023783013", "825023783016"):
    check(ads_by_id.get(ad_id, {}).get("status") == "ENABLED", f"RSA {ad_id} not ENABLED in snapshot")
ag_ids = {g["id"] for g in SNAP["ad_groups"]}
check({AG1, AG2} <= ag_ids, "ad group IDs not in snapshot")
for ag in (AG1, AG2):
    check(sum(1 for a in SNAP["ads"] if a["ad_group_id"] == ag and a["status"] != "REMOVED") == 2,
          f"ad group {ag}: expected exactly 2 non-removed RSAs before the bundle (3-RSA cap)")
negs = {x["keyword"]["text"]: x for x in SNAP["campaign_criteria"] if x["type_"] == "KEYWORD" and x.get("negative")}
REMOVE = {"labor only": "296448593009", "customer supplied": "573042878059", "my own lights": "2225874598953"}
for text, crit in REMOVE.items():
    n = negs.get(text)
    check(bool(n) and n["criterion_id"] == crit and n["keyword"]["match_type"] == "PHRASE" and n.get("status") == "ENABLED",
          f"negative to remove drifted: {text}")
ADD_NEG = [("brilliant by night", "PHRASE"), ("types of permanent outdoor christmas lights", "EXACT")]
ADD_KW = ["permanent christmas lights lincoln ne", "permanent christmas lights installation near me",
          "permanent holiday light installation near me", "permanent lighting installation"]
positives = [(k["keyword"]["text"], k["keyword"]["match_type"]) for k in SNAP["ad_group_criteria"]
             if k.get("type_") == "KEYWORD" and not k.get("negative")]


def blocks(neg_text: str, mt: str, query: str) -> bool:
    q, t = query.lower().split(), neg_text.lower().split()
    if mt == "EXACT":
        return q == t
    if mt == "PHRASE":
        return any(q[i:i + len(t)] == t for i in range(len(q) - len(t) + 1))
    return all(w in q for w in t)


after_negs = [(t, x["keyword"]["match_type"]) for t, x in negs.items() if t not in REMOVE] + ADD_NEG
for kw in ADD_KW:
    check((kw, "EXACT") not in positives, f"duplicate keyword {kw}")
    check(not any(blocks(t, mt, kw) for t, mt in after_negs), f"new keyword blocked by a negative: {kw}")
for t, mt in ADD_NEG:
    for kw, _ in positives + [(k, "EXACT") for k in ADD_KW]:
        check(not blocks(t, mt, kw), f"new negative {t} blocks positive {kw}")
terms = list(csv.DictReader((AUD / "search_terms_2026-09-21_to_2026-10-05.csv").open(encoding="utf-8")))
keep_terms = [r["search_term"] for r in terms if not r["search_term"].startswith(("brilliant by night", "types of"))]
for t, mt in ADD_NEG:
    hit = [q for q in keep_terms if blocks(t, mt, q)]
    check(not hit, f"new negative {t} would block kept search terms {hit}")

# ------------------------------------------------------------------ plans
TARGET = {"exact_child_account_name": NAME, "child_customer_id": CID, "manager_customer_id": MCC,
          "manager_never_mutated": True, "exact_primary_service": "Permanent Christmas light installation",
          "vertical": "similar-local-service", "scope_approval": "Walter, 2026-09-16 (recorded, not re-requested)",
          "work_order": "clients/apogee-lawns/work-order.yaml (validator PASS 2026-10-05)",
          "campaign": {"id": CAMP, "name": "S | Website Leads | Permanent Christmas Lights | Apogee Lawns | $500 | 09_2026",
                       "status": "ENABLED (unchanged by this bundle)", "budget_id": "15884926233",
                       "daily_budget_micros": 16440000, "monthly_cap_at_30_4_days_usd": 499.78,
                       "bidding": "MAXIMIZE_CLICKS (TARGET_SPEND) ceiling 8000000 micros (unchanged)",
                       "locations_presence": sorted(SNAP["geo_names"][x["location"]["geo_target_constant"]]["id"]
                                                    for x in SNAP["campaign_criteria"] if x["type_"] == "LOCATION"),
                       "schedule": "24/7, 0 ad-schedule criteria (unchanged)", "tablet": "-100% (unchanged)",
                       "final_url": LP,
                       "conversions": "7772803337 Primary, 7773013199 Primary, 7773043879 Secondary (unchanged)"}}
SNAPREF = {"snapshot": "clients/apogee-lawns/snapshots/2026-10-05-conversion-plan-snapshot.json",
           "snapshot_run_at_utc": SNAP["run_at_utc"],
           "browser_qa": "clients/apogee-lawns/audits/2026-10-05-conversion-plan/browser-qa/"}
COMMON_PRE = ["fresh identity gate PASS (exact name + child ID, not manager, not test)",
              "work-order validator PASS", "every resource name below re-read and unchanged since the snapshot; any drift = STOP",
              "campaign budget 16440000 micros, ceiling 8000000 micros, 14 locations, tablet 0.0 unchanged"]
RECOVERY = ("If any operation fails, the batch is atomic (partial_failure=false) and nothing is written; if a "
            "non-atomic partial success is ever observed: STOP, inventory every created/removed resource name from "
            "the response and a fresh read, write a PARTIAL-FAILURE receipt, and propose a recovery plan before any retry.")

kwneg = {
    "plan_id": "APG-1005-KWNEG", "plan_kind": "keywords_and_negatives", "generated": "2026-10-05",
    "external_writes_performed": "NONE", "target": TARGET, "evidence": SNAPREF,
    "objects": (
        [{"ordinal": i + 1, "resource": "ad_group_criterion", "operation": "create", "ad_group_id": AG1,
          "ad_group": "AG | Permanent Light Installation",
          "keyword": {"text": kw, "match_type": "EXACT"}, "status": "PAUSED", "final_urls": "inherit ad URL (none set)"}
         for i, kw in enumerate(ADD_KW)]
        + [{"ordinal": 5 + i, "resource": "campaign_criterion", "operation": "create", "campaign_id": CAMP,
            "negative": True, "keyword": {"text": t, "match_type": mt}} for i, (t, mt) in enumerate(ADD_NEG)]
        + [{"ordinal": 7 + i, "resource": "campaign_criterion", "operation": "remove",
            "resource_name": f"customers/{CID}/campaignCriteria/{CAMP}~{crit}",
            "current": {"text": t, "match_type": "PHRASE", "negative": True, "status": "ENABLED"}}
           for i, (t, crit) in enumerate(REMOVE.items())]),
    "mutation_counts": {"creates": 6, "keyword_creates_paused": 4, "negative_creates": 2, "removes": 3,
                        "updates": 0, "enables": 0, "status_changes": 0, "budget_changes": 0, "bid_changes": 0,
                        "geo_changes": 0, "conversion_changes": 0, "total_operations": 9},
    "preconditions_at_execution": COMMON_PRE,
    "readback_assertions": ["4 new EXACT keywords exist in ad group 200347713516 with status PAUSED",
                            "campaign negatives 75 -> 74 (+2 created, -3 removed); the 3 removed resource names absent",
                            "'brilliant by night' PHRASE and 'types of permanent outdoor christmas lights' EXACT present",
                            "all other 72 negatives byte-identical", "existing 5 positive keywords unchanged",
                            "campaign status, budget, ceiling, locations, device rows, RSAs, assets unchanged"],
    "qa_requirements": ["validate_only accepted the exact operations on 2026-10-05 (see validation report)",
                        "no new keyword duplicates an existing keyword; no new negative blocks a positive keyword or any kept search term",
                        "protected buying words untouched: cost, price, pricing, quote, best, hire, local, near me, emergency"],
    "recovery_plan": RECOVERY,
    "rollback": "re-add PHRASE negatives 'labor only', 'customer supplied', 'my own lights'; remove the 2 new negatives; remove the 4 new keywords",
    "enablement": "the 4 keywords stay PAUSED until a separate approval after readback (APG-1005-KWNEG-ENABLE)",
    "approval_grant": {"required_line": "APPROVE APG KWNEG <fingerprint>",
                       "fingerprint_scope": "gm_gsa.safety.approval_code over this file as loaded"},
}

ads = {
    "plan_id": "APG-1005-ADS", "plan_kind": "rsa_and_callout_create_paused", "generated": "2026-10-05",
    "external_writes_performed": "NONE", "target": TARGET, "evidence": SNAPREF,
    "claim_sources_verified_today": {k: v for k, v in CLAIMS.items() if v},
    "objects": [
        {"ordinal": 1, "resource": "ad_group_ad", "operation": "create", "ad_group": "AG | Permanent Light Installation",
         "responsive_search_ad": RSA_AG1, "role": "treatment: every pinned H1 option signals installation; comparator kept = 825023783007"},
        {"ordinal": 2, "resource": "ad_group_ad", "operation": "create", "ad_group": "AG | Permanent Christmas Lights Exact",
         "responsive_search_ad": RSA_AG2, "role": "treatment: installation-focused copy for the head-term trial; comparator kept = 825023783016"},
        {"ordinal": 3, "resource": "asset", "operation": "create", "type": "CALLOUT", "callout_text": CALLOUT["text"],
         "claims": CALLOUT["claims"]},
        {"ordinal": 4, "resource": "campaign_asset", "operation": "create", "campaign_id": CAMP, "field_type": "CALLOUT",
         "asset": "temporary resource from ordinal 3", "status": "PAUSED"},
    ],
    "mutation_counts": {"creates": 4, "rsa_creates_paused": 2, "asset_creates": 1, "campaign_asset_links_paused": 1,
                        "updates": 0, "removes": 0, "enables": 0, "status_changes": 0, "budget_changes": 0,
                        "bid_changes": 0, "conversion_changes": 0, "total_operations": 4},
    "after_creation_counts": {"ad_group_200347713516_rsas": "2 ENABLED + 1 PAUSED (cap 3)",
                              "ad_group_200347713556_rsas": "2 ENABLED + 1 PAUSED (cap 3)"},
    "preconditions_at_execution": COMMON_PRE + ["each ad group still has exactly 2 non-removed RSAs"],
    "readback_assertions": ["2 new RSAs PAUSED with exactly the headlines, pins, descriptions, paths and final URL above",
                            "callout asset text exact; campaign_asset link PAUSED", "existing 4 RSAs still ENABLED and unchanged",
                            "existing 8 campaign asset links unchanged"],
    "qa_requirements": ["validate_only accepted the exact operations on 2026-10-05",
                        "every pinned H1 option contains 'install'; headlines <=30, descriptions <=90, paths <=15",
                        "every claim found in today's captured text of the paid page or apogeelawns.com permanent-lights page",
                        "no price, warranty, rating, review, EverLights brand, Veteran, Omaha, response-time or product-spec claim"],
    "recovery_plan": RECOVERY,
    "rollback": "remove the 2 paused RSAs, the callout link and the callout asset (none serve while PAUSED)",
    "enablement": ("separate approval after readback (APG-1005-ADS-TRANSITION): enable both new RSAs and the callout "
                   "link, and pause 825023783010 and 825023783013 so each ad group keeps exactly two distinct enabled RSAs"),
    "approval_grant": {"required_line": "APPROVE APG ADS CREATE-PAUSED <fingerprint>",
                       "fingerprint_scope": "gm_gsa.safety.approval_code over this file as loaded"},
}

web = {
    "plan_id": "APG-1005-WEB-REPAIR", "plan_kind": "website_measurement_and_friction_repair_handoff",
    "generated": "2026-10-05", "external_writes_performed": "NONE", "target": TARGET, "evidence": SNAPREF,
    "executor": "Apogee's website developer (siliconprairiemarketing.com) on the owner's authorization; Green Marketing does not edit WordPress",
    "spec": "clients/apogee-lawns/audits/2026-10-05-conversion-plan/03_measurement_and_friction_repair_spec.md",
    "spec_sha256": hashlib.sha256((AUD / "03_measurement_and_friction_repair_spec.md").read_bytes()).hexdigest(),
    "gtm_changes": "NONE required: published version 3 already expects this exact path, event and lead_id key",
    "google_ads_changes": "NONE",
    "items": ["R1 thank-you page", "R2 cache exclusion + client-side attribution", "R3 accepted-entry-only redirect with token",
              "R4 server-verified success push with lead_id", "R5 remove drafting notes C1-C5 and align FAQ/form",
              "R6 one form instance", "R7 click-ID/UTM/landing/referrer/consent capture", "R8 lead delivery confirmation"],
    "approval_grant": {"required_line": "APPROVE APG WEB REPAIR HANDOFF <fingerprint>",
                       "meaning": "authorizes sending this exact spec to the developer; it does not authorize any Google Ads, GTM or WhatConverts change"},
}


blocked_drafts = {
    "APG-1005-SITELINKS": {
        "plan_id": "APG-1005-SITELINKS", "plan_kind": "sitelink_assets_DRAFT", "approval_ready": False,
        "blockers": ["the paid page has no section anchors today (only theme container IDs); R6 adds #estimate, #how-it-works, "
                     "#design, #app-control, #faq, #homes-businesses",
                     "anchors must be verified live in a browser before final URLs are fixed"],
        "why_not_main_site": "apogeelawns.com pages carry no GTM, no WhatConverts and show 402-202-7261, so sitelink clicks there lose paid call and form attribution",
        "sitelinks": [{"link_text": t, "description1": d1, "description2": d2, "final_url": LP.rstrip("/") + "/" + a}
                      for t, d1, d2, a in SITELINKS_DRAFT],
        "creation_status_when_ready": "assets + campaign links created PAUSED; separate enablement approval",
        "target": TARGET},
    "APG-1005-TEST": {
        "plan_id": "APG-1005-TEST", "plan_kind": "controlled_form_and_call_tests_DRAFT", "approval_ready": False,
        "blockers": ["APG-1005-WEB-REPAIR R1-R8 deployed and confirmed read-only",
                     "Green Marketing test identity supplied via the approved secure method and registered in client.yaml qa_exclusions"],
        "tests": ["T1 desktop submission", "T2 mobile submission", "T3 negative cases (validation error, direct thank-you visit, refresh, clicks)",
                  "T4 routing call to 402-526-5754 in staffed hours (+ optional after-hours)"],
        "rules": ["never click live ads", "never create or type click IDs", "test leads marked as tests and excluded from reporting",
                  "a direct test proves tag delivery and de-duplication, not an attributed Google Ads conversion"],
        "spec": "03_measurement_and_friction_repair_spec.md sections C and D",
        "target": TARGET},
}
for pid, p in blocked_drafts.items():
    (PLANS / f"{pid}.yaml").write_text(yaml.safe_dump(p, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")

for p in (kwneg, ads, web):
    assert_no_embedded_secrets(p)

out = {"problems": problems, "fingerprints": {}}
if not problems:
    for p in (kwneg, ads, web):
        path = PLANS / f"{p['plan_id']}.yaml"
        path.write_text(yaml.safe_dump(p, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
        loaded = load_yaml(str(path))
        fp = approval_code(loaded)
        out["fingerprints"][p["plan_id"]] = {"fingerprint": fp, "file": str(path.relative_to(ROOT)),
                                              "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
(AUD / "bundle-fingerprints.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
(AUD / "draft-copy.json").write_text(json.dumps({"RSA_AG1": RSA_AG1, "RSA_AG2": RSA_AG2, "CALLOUT": CALLOUT,
                                                  "SITELINKS_DRAFT": SITELINKS_DRAFT, "ADD_KW": ADD_KW,
                                                  "ADD_NEG": ADD_NEG, "REMOVE": REMOVE}, indent=1), encoding="utf-8")
print("problems:", len(problems))
for x in problems:
    print("  -", x)
print(json.dumps(out["fingerprints"], indent=1))
for label, ad in (("AG1", RSA_AG1), ("AG2", RSA_AG2)):
    print(label, [(len(h["text"]), h["text"]) for h in ad["headlines"]])
    print(label, [len(x["text"]) for x in ad["descriptions"]])
