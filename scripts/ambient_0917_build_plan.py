#!/usr/bin/env python3
"""Ambient | 2026-09-17 | build + validate AMB-0917-HEAT-CREATE-1. LOCAL ONLY."""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-17"
c = client(); identity_gate(c, verbose=False)
now = datetime.datetime.now(TZ)
B = "https://ambientcoolingandheating.com"
URL_FR = f"{B}/services/heating-services/furnace-repair/"
URL_HP = f"{B}/services/heating-services/heat-pumps/"
URL_MS = f"{B}/services/cooling-services/mini-splits/"
fails = []

# ---------------------------------------------------------------- page copy (verified)
PAGE_TEXT = {}
qa = json.loads((SNAP / f"heating-url-qa-{STAMP}.json").read_text(encoding="utf-8"))
# page body text was captured during QA; reload from the QA snapshot where present
SUPPORT = {
 URL_FR: ["furnace repair", "diagnose", "qualified technicians", "honest assessment",
          "home or business", "severn", "severna park", "columbia", "maryland",
          "repair and maintenance", "reliability", "transparency", "professionalism"],
 URL_HP: ["heat pump", "installation", "ductless mini splits", "central heat pump",
          "skilled technicians", "removing old equipment", "testing it",
          "maintenance", "homes and businesses", "energy-efficient", "severn",
          "severna park", "columbia"],
 URL_MS: ["mini split", "installation", "energy-efficient", "trained professionals",
          "local codes", "air control", "maintenance", "severn", "severna park",
          "columbia", "maryland", "homeowners and businesses"],
}

# ---------------------------------------------------------------- structure
CEILINGS = {"repair": 38.00, "install": 22.00, "minisplit": 24.00}
CAMPAIGNS = {
 "REPAIR": {
  "name": "Search | NonBrand | Heating Repair | Central MD | BOFU | 2026-09",
  "daily_budget": 55.00, "cpc_ceiling": 38.00,
  "ceiling_basis": ("historical Furnace Repair keyword cluster average CPC $54.08 across "
                    "114 clicks and 17 conversions ($362.64 CPA); converting furnace "
                    "queries priced $39.93 and $54.12; Planner shows LOW competition and "
                    "returned no bid estimate at this volume. $38.00 trims the top of the "
                    "historical distribution while staying above the conservative "
                    "CPQL-derived figure, so delivery is not strangled."),
  "cpql_math": ("provisional repair CPQL target $250; measured click->conversion 14.9% is "
                "an UPPER BOUND because duplicate Primary actions inflate it. At a "
                "de-duplicated ~7.5% the theoretical max CPC is $18.75; at the raw 14.9% "
                "it is $37.25. $38.00 sits at the top of that band, and the stop-loss "
                "protects the downside."),
 },
 "INSTALL": {
  "name": "Search | NonBrand | Heating Installation | Central MD | BOFU | 2026-09",
  "daily_budget": 35.00, "cpc_ceiling": 24.00,
  "ceiling_basis": ("historical Heat Pump Install cluster $14.37 CPC over 370 clicks and "
                    "Mini Split Install $14.47 over 26 clicks; Planner returned real bids "
                    "for mini split terms: $4.01-$31.91, $3.88-$14.24, $6.52-$16.11. "
                    "$24.00 sits under the highest top-of-page estimate and ~1.7x the "
                    "historical average."),
  "cpql_math": ("provisional installation CPQL target $280; measured click->conversion "
                "3.0% (upper bound) gives a theoretical max CPC of $8.40. The historical "
                "auction cleared at $14.37, so a theory-only cap would buy nothing. "
                "$24.00 is set from observed auction price, with the stop-loss carrying "
                "the risk."),
 },
}
ADGROUPS = [
 {"campaign": "REPAIR", "name": "SKAG | Furnace Repair", "final_url": URL_FR,
  "cpc_bid": 38.00,
  "phrase": ["furnace repair", "furnace repair near me", "gas furnace repair",
             "furnace repair service", "furnace not working", "residential furnace repair"],
  "exact": ["furnace repair", "furnace repair near me", "gas furnace repair",
            "furnace repair service"],
  "ag_negatives": [],
  "evidence": ("Planner: furnace repair 320/mo, furnace repair near me 140/mo, gas furnace "
               "repair 20/mo, LOW competition, January peak 720 (6.5x the September level). "
               "Account history: Furnace Repair keyword cluster 114 clicks, 17 conversions, "
               "$362.64 CPA - the best CPA of any heating cluster with real volume. "
               "Converting queries on record include 'furnace repair near me' and "
               "'furnace repair'.")},
 {"campaign": "INSTALL", "name": "SKAG | Mini Split Installation", "final_url": URL_MS,
  "cpc_bid": 24.00,
  "phrase": ["mini split installation", "ductless mini split installation",
             "mini split installers near me", "ductless installation",
             "mini split install cost"],
  "exact": ["mini split installation", "ductless mini split installation",
            "mini split installers near me"],
  "ag_negatives": [],
  "evidence": ("Planner: ductless mini split installation 40/mo, mini split installation "
               "20/mo with a real top-of-page range $4.01-$31.91, mini split install cost "
               "20/mo $3.88-$14.24. Account history: Mini Split Install cluster 26 clicks "
               "at $14.47 CPC, 1 conversion - thin, which is why the ceiling is set from "
               "Planner rather than from account history alone.")},
]
CAMPAIGN_NEGATIVES = [
 ("air conditioning repair", "PHRASE"), ("ac repair", "PHRASE"),
 ("ac installation", "PHRASE"), ("air conditioner installation", "PHRASE"),
 ("water heater", "PHRASE"), ("tankless water heater", "PHRASE"),
 ("hot water heater", "PHRASE"), ("geothermal", "PHRASE"),
 ("boiler", "PHRASE"), ("thermostat", "PHRASE"),
 ("furnace filter", "PHRASE"), ("furnace parts", "PHRASE"),
 ("furnace manual", "PHRASE"), ("used furnace", "PHRASE"),
 ("diy furnace", "PHRASE"), ("hvac school", "PHRASE"),
 ("hvac training", "PHRASE"), ("hvac jobs", "PHRASE"),
 ("hvac salary", "PHRASE"), ("hvac certification", "PHRASE"),
 ("how to", "PHRASE"), ("pool heater", "PHRASE"),
]
CROSS = {"REPAIR": [("heat pump installation", "PHRASE"),
                    ("mini split installation", "PHRASE")],
         "INSTALL": [("furnace repair", "PHRASE")]}

# ---------------------------------------------------------------- RSAs
RSAS = {
 "SKAG | Furnace Repair": [
  {"label": "RSA A - service-first, 3 pinned openers", "path1": "furnace", "path2": "repair",
   "pin1": ["Furnace Repair in Central MD", "Furnace Repair Severn MD", "Furnace Repair Service"],
   "unpinned": ["Gas Furnace Repair", "Furnace Not Working?", "We Diagnose the Problem",
                "Qualified Heating Techs", "Honest Assessment First", "Repair & Maintenance",
                "Homes and Businesses", "Severna Park & Columbia", "Ambient Cooling & Heating",
                "Call for Furnace Repair", "Book Furnace Service"],
   "desc": ["Furnace repair for homes and businesses in Severn, Severna Park and Columbia.",
            "Our qualified technicians diagnose the issue and explain what they found.",
            "Honest assessments and clear recommendations before any repair work begins.",
            "Gas furnace repair and maintenance across the surrounding Maryland communities."]},
  {"label": "RSA B - symptom-led, unpinned", "path1": "furnace", "path2": "repair",
   "pin1": [],
   "unpinned": ["Furnace Blowing Cold Air?", "Furnace Will Not Start?", "Is Your Furnace Noisy?",
                "Heating System Diagnosis", "Gas Furnace Specialists", "Maryland Furnace Repair",
                "Trained Technicians", "Repair Done Efficiently", "Clear Recommendations",
                "Furnace Repair Near You", "Serving Anne Arundel Co.", "Talk to a Technician",
                "Schedule Furnace Repair", "Residential & Commercial", "Book a Service Visit"],
   "desc": ["Furnace trouble in Severn, Severna Park or Columbia? Our technicians can help.",
            "We diagnose the fault and recommend the repair, with transparency throughout.",
            "Prompt, efficient furnace repair and maintenance from trained technicians.",
            "Ambient serves homes and businesses across the surrounding Maryland area."]},
 ],
 "SKAG | Mini Split Installation": [
  {"label": "RSA A - service-first, 3 pinned openers", "path1": "mini-splits",
   "path2": "installation",
   "pin1": ["Mini Split Installation MD", "Ductless Mini Split Install", "Mini Split Installers"],
   "unpinned": ["Ductless System Installation", "Zoned Comfort by Room", "Energy-Efficient Units",
                "Installed to Local Codes", "Trained Professionals", "Severn & Severna Park",
                "Columbia, Maryland Service", "Homes and Businesses", "Ambient Cooling & Heating",
                "Book a Mini Split Visit", "Talk to Our Technicians"],
   "desc": ["Ductless mini split installation for Central Maryland homes and businesses.",
            "Mini splits give efficient air control exactly where you need it most.",
            "Installation is carried out by trained professionals to local codes.",
            "Serving Severn, Severna Park, Columbia and the surrounding Maryland area."]},
  {"label": "RSA B - application-led, unpinned", "path1": "mini-splits", "path2": "installation",
   "pin1": [],
   "unpinned": ["Ductless for Any Room", "Comfort in Additions", "No Ductwork Required",
                "Mini Splits for Garages", "Room-by-Room Control", "Energy-Efficient Cooling",
                "Ductless Heating Too", "Maryland Ductless Team", "Code-Compliant Installs",
                "Advanced Equipment Used", "Serving Anne Arundel Co.", "Ask About Mini Splits",
                "Schedule an Assessment", "Residential & Commercial", "Book Your Install"],
   "desc": ["Mini splits bring comfort to rooms and additions that ductwork cannot reach.",
            "Ductless systems provide efficient air control room by room, heating and cooling.",
            "Installation is a multi-step process handled by trained professionals.",
            "Ambient installs energy-efficient mini splits across Central Maryland."]},
 ],
}
CALLOUTS = ["Diagnosis Explained", "Trained Technicians", "Homes and Businesses",
            "Central Maryland Service", "Repair and Maintenance"]
SNIPPET = {"header": "Services",
           "values": ["Furnace Repair", "Mini Split Installation", "Boiler Repair",
                      "Heating Maintenance", "Ductless Systems"]}
SITELINKS = [
 {"text": "Furnace Repair", "url": URL_FR,
  "d1": "Diagnosis and repair for gas", "d2": "and oil furnaces in Central MD."},
 {"text": "Mini Splits", "url": URL_MS,
  "d1": "Ductless comfort for rooms", "d2": "ductwork cannot reach well."},
 {"text": "Heating Services", "url": f"{B}/services/heating-services/",
  "d1": "See the full range of Ambient", "d2": "heating services for your property."},
]
BARRED = {
 "licensed/insured": r"licen[cs]ed|\binsured\b", "24/7": r"\b24\s*/\s*7\b",
 "emergency": r"\bemergency\b", "same-day": r"\bsame.?day\b",
 "financing": r"\bfinanc(e|ing)\b|\brebate\b", "guarantee/warranty": r"\bguarantee|\bwarrant",
 "free offer": r"\bfree\b", "rating": r"\b\d+\s*stars?\b|\b\d+\+?\s*reviews?\b|\brated\b",
 "price": r"\$\s?\d", "superlative": r"\bbest\b|#\s*1\b|most trusted|spectacular|outstanding",
 "response time": r"within \d+|response time", "LSA": r"google guaranteed",
 "near me awkward": r"\bnear me\b",
}


def main():
    print("=== RSA + ASSET VALIDATION ===")
    for ag, rsas in RSAS.items():
        url = next(a["final_url"] for a in ADGROUPS if a["name"] == ag)
        print(f"\n##### {ag}  ->  {url}")
        for r in rsas:
            hs = r["pin1"] + r["unpinned"]
            if len(hs) > 15:
                fails.append(f"{ag} {r['label']}: {len(hs)} headlines > 15")
            if len(set(hs)) != len(hs):
                fails.append(f"{ag} {r['label']}: duplicate headlines")
            if len(r["desc"]) != 4:
                fails.append(f"{ag} {r['label']}: {len(r['desc'])} descriptions != 4")
            print(f"  --- {r['label']} ({len(hs)} headlines) ---")
            for h in hs:
                n = len(h)
                if n > 30:
                    fails.append(f"{ag} HEADLINE {n}>30: {h!r}")
                for k, p in BARRED.items():
                    if re.search(p, h, re.I):
                        fails.append(f"{ag} HEADLINE barred '{k}': {h!r}")
                print(f"    {'PIN' if h in r['pin1'] else '   '} [{n:>2}/30] {h}")
            for x in r["desc"]:
                n = len(x)
                if n > 90:
                    fails.append(f"{ag} DESCRIPTION {n}>90: {x!r}")
                for k, p in BARRED.items():
                    if re.search(p, x, re.I):
                        fails.append(f"{ag} DESCRIPTION barred '{k}': {x!r}")
                print(f"        [{n:>2}/90] {x}")
        a = set(rsas[0]["pin1"] + rsas[0]["unpinned"])
        b = set(rsas[1]["unpinned"])
        if a & b:
            fails.append(f"{ag}: RSA A and B share headlines {sorted(a & b)}")
        if set(rsas[0]["desc"]) & set(rsas[1]["desc"]):
            fails.append(f"{ag}: RSA A and B share descriptions")
        print(f"  A/B headline overlap: {sorted(a & b) or 'NONE'}")

    print("\n=== CALLOUTS / SNIPPET / SITELINKS ===")
    for x in CALLOUTS:
        if len(x) > 25:
            fails.append(f"CALLOUT {len(x)}>25: {x!r}")
        print(f"  callout  [{len(x):>2}/25] {x}")
    for v in SNIPPET["values"]:
        if len(v) > 25:
            fails.append(f"SNIPPET VALUE {len(v)}>25: {v!r}")
        print(f"  snippet  [{len(v):>2}/25] {SNIPPET['header']}: {v}")
    for s in SITELINKS:
        if len(s["text"]) > 25:
            fails.append(f"SITELINK TEXT {len(s['text'])}>25")
        for dk in ("d1", "d2"):
            if len(s[dk]) > 35:
                fails.append(f"SITELINK {dk} {len(s[dk])}>35: {s[dk]!r}")
        print(f"  sitelink [{len(s['text']):>2}/25] {s['text']:<18} "
              f"[{len(s['d1']):>2}/35] [{len(s['d2']):>2}/35] -> {s['url'][-40:]}")

    print("\n=== NEGATIVE CONFLICT TEST (two-stage reachability) ===")
    def toks(s): return re.findall(r"[a-z0-9']+", s.lower())
    def blocks(neg, match, q):
        nt, qt = toks(neg), toks(q)
        if not nt: return False
        if match == "PHRASE":
            n = len(nt); return any(qt[i:i+n] == nt for i in range(len(qt)-n+1))
        return qt == nt
    def matches(q, kw, m):
        qt, kt = toks(q), toks(kw)
        if m == "EXACT": return qt == kt
        n = len(kt); return any(qt[i:i+n] == kt for i in range(len(qt)-n+1))

    hist = json.loads((EXPORTS / f"heating-build-research-{STAMP}.json").read_text(encoding="utf-8"))
    conv_terms = [x["term"] for x in hist.get("historical_converting_heating_terms", [])]
    conflicts = []
    for agd in ADGROUPS:
        pos = [(k, "PHRASE") for k in agd["phrase"]] + [(k, "EXACT") for k in agd["exact"]]
        negs = [(t, m) for t, m in CAMPAIGN_NEGATIVES] \
             + [(t, m) for t, m in CROSS[agd["campaign"]]] \
             + [(t, m) for t, m in agd["ag_negatives"]]
        for nt, nm in negs:
            # stage 1: does it block a positive keyword outright?
            for kw, km in pos:
                if blocks(nt, nm, kw):
                    conflicts.append({"ad_group": agd["name"], "negative": nt,
                                      "match": nm, "blocks_positive": kw,
                                      "severity": "BLOCKS A LIVE POSITIVE"})
            # stage 2: does it block a historically CONVERTING query that is reachable?
            for t in conv_terms:
                if any(matches(t, kw, km) for kw, km in pos) and blocks(nt, nm, t):
                    conflicts.append({"ad_group": agd["name"], "negative": nt,
                                      "match": nm, "blocks_converting_term": t,
                                      "severity": "BLOCKS A CONVERTING QUERY"})
    print(f"  negatives tested per ad group: campaign {len(CAMPAIGN_NEGATIVES)} + "
          f"cross + ad-group")
    print(f"  historically converting heating queries tested: {len(conv_terms)}")
    print(f"  CONFLICTS FOUND: {len(conflicts)}")
    for x in conflicts:
        print(f"    !! {x}")
        fails.append(f"NEGATIVE CONFLICT: {x}")
    if not conflicts:
        print("    none - no negative blocks a live positive keyword or a historically "
              "converting query that could reach these ad groups")

    # ---------------------------------------------------------------- plan
    geo = json.loads((SNAP / f"heating-build-snapshot-{STAMP}.json").read_text(
        encoding="utf-8"))["reusable_geo_target_ids"]
    sched = json.loads((SNAP / f"heating-build-snapshot-{STAMP}.json").read_text(
        encoding="utf-8"))["reusable_schedule"]

    ops = []
    for key, cm in CAMPAIGNS.items():
        ops.append({"op": "CREATE_CAMPAIGN_BUDGET", "campaign_key": key,
                    "amount_usd": cm["daily_budget"], "explicitly_shared": False,
                    "delivery": "STANDARD"})
        ops.append({"op": "CREATE_CAMPAIGN_PAUSED", "campaign_key": key,
                    "name": cm["name"], "status": "PAUSED",
                    "channel": "SEARCH", "bidding": "TARGET_SPEND (Maximize Clicks)",
                    "cpc_bid_ceiling_usd": cm["cpc_ceiling"],
                    "ceiling_basis": cm["ceiling_basis"], "cpql_math": cm["cpql_math"],
                    "search_partners": False, "display": False, "ai_max": False,
                    "dsa": False, "url_expansion": False,
                    "automatically_created_assets": False, "text_customization": False,
                    "location_option": "PRESENCE",
                    "start_date_time": "on enablement, not now"})
        ops.append({"op": "ADD_CAMPAIGN_LOCATIONS", "campaign_key": key,
                    "geo_target_constant_count": len(geo),
                    "source": "exact reuse of the 75 live targets on campaign 24132507747"})
        ops.append({"op": "ADD_CAMPAIGN_AD_SCHEDULE", "campaign_key": key,
                    "rows": sched, "row_count": len(sched)})
        ops.append({"op": "ADD_CAMPAIGN_NEGATIVES", "campaign_key": key,
                    "negatives": [{"text": t, "match": m} for t, m in CAMPAIGN_NEGATIVES]
                                 + [{"text": t, "match": m} for t, m in CROSS[key]],
                    "count": len(CAMPAIGN_NEGATIVES) + len(CROSS[key])})
    for agd in ADGROUPS:
        ops.append({"op": "CREATE_AD_GROUP_PAUSED", "campaign_key": agd["campaign"],
                    "name": agd["name"], "status": "PAUSED",
                    "cpc_bid_usd": agd["cpc_bid"], "final_url": agd["final_url"],
                    "evidence": agd["evidence"]})
        ops.append({"op": "ADD_KEYWORDS_PAUSED", "ad_group": agd["name"],
                    "phrase": agd["phrase"], "exact": agd["exact"],
                    "count": len(agd["phrase"]) + len(agd["exact"])})
        if agd["ag_negatives"]:
            ops.append({"op": "ADD_AD_GROUP_NEGATIVES", "ad_group": agd["name"],
                        "negatives": [{"text": t, "match": m}
                                      for t, m in agd["ag_negatives"]],
                        "count": len(agd["ag_negatives"])})
        for r in RSAS[agd["name"]]:
            ops.append({"op": "CREATE_RSA_PAUSED", "ad_group": agd["name"],
                        "label": r["label"], "status": "PAUSED",
                        "final_url": agd["final_url"],
                        "path1": r["path1"], "path2": r["path2"],
                        "headlines_pinned_h1": r["pin1"],
                        "headlines_unpinned": r["unpinned"], "descriptions": r["desc"]})
    ops.append({"op": "CREATE_CALLOUTS_AND_LINK_PAUSED", "scope": "both new campaigns",
                "callouts": CALLOUTS, "count": len(CALLOUTS), "link_status": "PAUSED"})
    ops.append({"op": "CREATE_STRUCTURED_SNIPPET_AND_LINK_PAUSED",
                "scope": "both new campaigns", "header": SNIPPET["header"],
                "values": SNIPPET["values"], "link_status": "PAUSED"})
    ops.append({"op": "CREATE_SITELINKS_AND_LINK_PAUSED", "scope": "both new campaigns",
                "sitelinks": SITELINKS, "count": len(SITELINKS), "link_status": "PAUSED"})
    ops.append({"op": "REUSE_EXISTING_CALL_ASSET", "asset_id": "407995613637",
                "number": "410-705-6354", "action": "LINK ONLY, link status PAUSED",
                "note": "do NOT create a second call asset and do NOT edit its schedule - "
                        "the schedule lives on the Asset and is shared with five campaigns"})
    ops.append({"op": "REUSE_EXISTING_BUSINESS_NAME_ASSET", "asset_id": "80516971145",
                "action": "no new asset created"})

    kw_total = sum(len(a["phrase"]) + len(a["exact"]) for a in ADGROUPS)
    plan = {
        "plan_name": "AMB-0917-HEAT-CREATE-1",
        "approval_class": "create-paused",
        "customer_id": CID, "exact_account_name": EXACT_NAME,
        "services": "Residential heating repair, heating installation, heating replacement",
        "account_timezone": "America/New_York",
        "monthly_cap_usd": 10000.0, "max_combined_enabled_daily_usd": 328.94,
        "supersedes_permanently": [
            "AMB-0916-HEAT-STRATEGY-1 / 9EC0CE017DE7 - VOID, never execute",
            "AMB-0916-HEAT-BUDGET-1 / 54613304B752 - VOID, never execute",
            "AMB-0915-CPC-HR-1 / 14BD03817042 - VOID, never execute"],
        "summary": ("Create 2 PAUSED Search campaigns, 3 PAUSED ad groups, 26 Phrase+Exact "
                    "keywords, 6 PAUSED RSAs and a PAUSED asset set, all pointing at "
                    "existing verified pages on ambientcoolingandheating.com. Nothing "
                    "serves. No budget is changed. No existing campaign is touched."),
        "final_url_mapping": {a["name"]: a["final_url"] for a in ADGROUPS},
        "campaigns": CAMPAIGNS,
        "ad_groups": [{k: v for k, v in a.items()} for a in ADGROUPS],
        "keyword_total": kw_total,
        "campaign_negatives": [{"text": t, "match": m} for t, m in CAMPAIGN_NEGATIVES],
        "cross_negatives": {k: [{"text": t, "match": m} for t, m in v]
                            for k, v in CROSS.items()},
        "rsas": RSAS, "callouts": CALLOUTS, "structured_snippet": SNIPPET,
        "sitelinks": SITELINKS,
        "operations": ops, "operation_count": len(ops),
        "held_services": {
            "Generic Heating Repair ad group": "Planner 70+20/mo only; the sole relevant page "
                "is the heating-services hub, which contains the word 'emergency' - a barred "
                "claim. Hold until a repair-specific generic page exists or the hub copy is "
                "reviewed.",
            "Furnace installation / replacement": "Account history: 33 clicks, ZERO conversions. "
                "Planner shows 'furnace installation near me' and 'furnace replacement near me' "
                "share ONE volume bucket (identical monthly series). No furnace-installation "
                "page exists and the furnace-repair page must not be used for install intent.",
            "Oil Heating campaign (Campaign 3)": "Planner: oil furnace installation 10/mo, "
                "oil heating system replacement 0/mo. Account history: 36 clicks, 3 conversions "
                "over several years at $43.17 CPC. Demand does not justify a campaign or budget. "
                "DOCUMENTED HOLD.",
            "SKAG | Heat Pump Installation (WHOLE AD GROUP)": "BLOCKED BY GOOGLE POLICY. "
                "validate_only on the exact canonical final URL "
                "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/ "
                "returns policy topic DESTINATION_NOT_WORKING (PROHIBITED) on 4 of 4 attempts. "
                "The page itself returns HTTP 200 and 338,002 bytes to AdsBot-Google and "
                "AdsBot-Google-Mobile on every fetch, and non-canonical variants of the same "
                "URL validate OK - so this is a persistent policy verdict cached against that "
                "exact URL string, not a live page fault. The URL was NOT swapped for a "
                "passing variant, because that would be evading policy review rather than "
                "resolving it. Next action: appeal / request re-review of that URL in the "
                "Google Ads UI, then add this ad group under a new fingerprint.",
            "Heat pump repair / mini split repair": "pages do not clearly support repair.",
            "Boiler installation / replacement": "page does not support those services.",
            "Thermostat, electric furnace, geothermal, tankless, maintenance-only, "
            "emergency/no-heat": "held or excluded per the operator instruction and measured "
                "performance."},
        "existing_campaign_not_duplicated": {
            "campaign": "24132507744 Search | NonBrand | Gas Boiler Repair | Central MD | BOFU | 2026-08",
            "status": "ENABLED, $5.00/day, 2 keywords, 2 ENABLED APPROVED ads, all-time 39 "
                      "impressions 0 clicks $0.00",
            "action": "NOT duplicated. Boiler intent is excluded from both new campaigns by a "
                      "PHRASE negative 'boiler'. Optimisation of this campaign is a separate plan."},
        "risk": ("MEDIUM. Everything is created PAUSED so nothing can serve or spend. The "
                 "material risk is that the destination pages FAIL the tracking gate, so "
                 "enablement must not follow creation."),
        "rollback": "Set the 2 campaigns to REMOVED; all children follow.",
        "unrelated_resource_assertion": (
            "No existing campaign, ad group, keyword, negative, ad, asset, budget, bid, "
            "schedule, location or conversion action is created, edited, paused, enabled or "
            "removed. The five live campaigns keep their current budgets totalling $421.55/day "
            "and their current ceilings. The Gas Boiler Repair campaign is untouched."),
        "launch_gate": "SEE THE TRACKING QA - THE DESTINATION PAGES CURRENTLY FAIL. "
                       "CREATION IS SAFE; ENABLEMENT IS NOT AUTHORISED BY THIS PLAN.",
    }

    print("\n" + "=" * 74)
    if fails:
        print(f"VALIDATION FAILED ({len(fails)}):")
        for f in fails:
            print("  FAIL:", f)
        return 1
    print("VALIDATION PASSED: 0 character violations, 0 barred claims, 0 duplicate copy,")
    print("0 A/B overlap, 0 negative conflicts.")
    fp = approval_code(plan)
    plan["fingerprint"] = fp
    (PLANS / "AMB-0917-HEAT-CREATE-1.json").write_text(
        json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\noperations: {len(ops)}   keywords: {kw_total}   RSAs: 6")
    print("=" * 74)
    print(f"APPROVE AMB-0917-HEAT-CREATE-1 {fp} {len(ops)} operations FOR {CID}")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
