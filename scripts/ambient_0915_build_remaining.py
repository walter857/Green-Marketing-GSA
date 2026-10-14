#!/usr/bin/env python3
"""Ambient | 2026-09-15 | build the remaining fingerprinted plans.

  AMB-0915-LP-1          website remediation, specification only (no WP access exists)
  AMB-0915-CONV-1        conversion-goal correction
  AMB-0915-COMM-NEGRM-1  DESTRUCTIVE: narrow 6 campaign negatives blocking commercial
  AMB-0915-CPC-HR-1      HVAC Repair $25 -> $65 controlled test, GATED on attribution
  AMB-0915-RSA-ACR-3     supersedes AMB-0910-RSA-ACR-2 (fingerprint no longer recomputes)
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-15"
CAMP_INST, CAMP_HR, COMM_AG, RES_AG, ACR_AG = ("24132507747", "24132507750",
                                               "199748801029", "202339087634",
                                               "202339087834")
c = client(); identity_gate(c, verbose=False)
built = {}

PAGES = ["/ac-repair/", "/hvac-repair/", "/hvac-installation/", "/hvac-replacement/",
         "/gas-boiler-repair/", "/commercial-hvac-installation/"]

# ---------------------------------------------------------------- AMB-0915-LP-1
lp = {
    "plan_name": "AMB-0915-LP-1",
    "document": "AMBIENT COOLING - LANDING PAGE REMEDIATION (specification only)",
    "approval_class": "website-change-specification",
    "status": "NOT AUTHORIZED FOR PRODUCTION DEPLOYMENT BY THIS SESSION",
    "why_not_deployable": (
        "This session has no website source, no WordPress or SiteGround credential, no "
        "SFTP/SSH access and no staging environment. No environment variable, MCP server "
        "or client code in this repository can reach the site. Publishing is therefore "
        "impossible here and must not be improvised. This document is the exact "
        "specification the web developer implements, on staging, with a backup and a "
        "tested diff, before a separate production deployment approval."),
    "account": {"customer_id": CID, "exact_account_name": EXACT_NAME,
                "service": "Commercial HVAC Installation + five existing services"},
    "pages": PAGES,
    "defects": [
        {"id": "LP-1", "severity": "P0", "pages": "all 6",
         "issue": "Proxy cache serves one visitor's attribution values to every later visitor",
         "evidence": ("response headers x-cache-enabled: True, x-proxy-cache: HIT. Raw server "
                      "HTML for /hvac-installation/ requested with gclid=ZZZFRESH999 and "
                      "utm_campaign=zzz-camp returned input_14='QA0915COMMTEST' and "
                      "input_11='qa-readonly' - values from a different, earlier visit. "
                      "0 of 24 fresh-context loads captured the visitor's own GCLID."),
         "root_cause": ("Gravity Forms hidden fields input_9..input_15 are populated "
                        "SERVER-SIDE from the query string, and the rendered page is then "
                        "stored by the full-page proxy cache. Server-side population and "
                        "full-page caching are mutually incompatible."),
         "required_correction": [
             "1. Purge SiteGround Dynamic Cache for all six URLs immediately.",
             "2. Stop emitting visitor-specific values into cacheable server HTML. The "
             "hidden inputs must ship with value=\"\" in the cached document.",
             "3. Populate them client-side on DOMContentLoaded from location.search; when a "
             "parameter is absent from the current URL, fall back to a first-party cookie "
             "scoped to the registrable domain (ambientcoolingandheating.com) written on "
             "first paid landing; never from a cached value.",
             "4. First-party persistence must not overwrite a newer valid value with an "
             "older stored one: last-touch wins when the current URL carries a click id.",
             "5. A direct visit with no parameters and no cookie must leave the fields EMPTY, "
             "never inherit another visitor's data.",
             "6. Inspect and document the real Gravity Forms field map before editing. Do "
             "not assume IDs. Field 16 is the honeypot and its label rotates "
             "(LinkedIn / X-Twitter / Comments) - never populate it.",
             "7. TEMPORARY FALLBACK if (3) cannot ship immediately: exclude the six paid "
             "URLs from full-page dynamic caching. This is a stopgap, not the fix - a cache "
             "purge alone lets the very next visitor poison it again."],
         "fields_to_capture": ["gclid", "gbraid", "wbraid", "utm_source", "utm_medium",
                               "utm_campaign", "utm_term", "utm_content", "landing_url",
                               "first_landing_url", "campaign", "adgroup", "keyword",
                               "device", "lead_id_or_transaction_id", "consent_state"],
         "owner": "web developer", "launch_blocker": True,
         "retest": "ambient_0915_gclid_probe.py - require 24/24 own-GCLID capture"},
        {"id": "LP-2", "severity": "P0", "pages": "/commercial-hvac-installation/",
         "issue": "Internal developer instruction published as customer-facing body copy",
         "evidence": ("Live under the gallery heading: 'These images illustrate commercial "
                      "HVAC equipment and installation settings. Use them for the page "
                      "layout without presenting them as completed Ambient projects.'"),
         "required_correction": ["Delete the second sentence in full. It is an instruction "
                                 "to the builder, not copy."],
         "owner": "web developer", "launch_blocker": True,
         "retest": "render the page and assert the string is absent"},
        {"id": "LP-3", "severity": "P0", "pages": "/commercial-hvac-installation/",
         "issue": "Gallery section contains zero images",
         "evidence": "0 <img> elements within the gallery section scope",
         "required_correction": [
             "EITHER populate it with the four supplied commercial HVAC images IF their "
             "advertising-use rights are verified, captioned only as illustrative commercial "
             "HVAC equipment or installation settings,",
             "OR remove the entire gallery section.",
             "Never identify these images as completed Ambient projects.",
             "If rights cannot be verified, remove the section - do not ship an empty one."],
         "owner": "web developer + client", "launch_blocker": True,
         "retest": "render; gallery either has >=1 image with a compliant caption or is absent"},
        {"id": "LP-4", "severity": "P0", "pages": "/commercial-hvac-installation/",
         "issue": "Countdown timer advertising an offer that does not exist",
         "evidence": "Live text: 'Offer Ends in 15 DAY 10 HRS 15 MIN 06 SEC'",
         "why_it_matters": ("No discount, price or promotion appears anywhere on the page. "
                            "client.yaml bars discount_or_dollar_offer and records the only "
                            "verified offer as a free quote with no dollar value. An "
                            "evergreen countdown on a non-existent offer is an unverified "
                            "promotional claim and a Google Ads misrepresentation risk on a "
                            "page our ads point to."),
         "required_correction": ["Remove the countdown entirely.",
                                 "Do NOT substitute another urgency or scarcity device.",
                                 "A real dated offer may replace it only with written client "
                                 "approval of the exact terms."],
         "owner": "web developer + client", "launch_blocker": True,
         "retest": "render; assert no countdown and no 'Offer Ends' string"},
        {"id": "LP-5", "severity": "P1", "pages": "all 6",
         "issue": "form#gform_1 rendered 3x per page; 34 duplicate DOM ids",
         "evidence": "document.querySelectorAll('form#gform_1').length === 3 on every page",
         "required_correction": [
             "Preferred: ONE canonical Gravity Form instance per page; every other CTA "
             "scrolls to it via the existing #quote-form anchor.",
             "If more than one instance must remain, every form, wrapper, field, label, "
             "validation and confirmation id must be unique per instance.",
             "One submission must produce exactly one lead record, one GTM form-success "
             "event and one Google Ads conversion.",
             "GTM listeners must bind once, not once per duplicate form.",
             "Never populate the honeypot (field 16)."],
         "owner": "web developer + GTM", "launch_blocker": True,
         "retest": "single controlled QA submission; assert 1 CRM record, 1 GTM event, "
                   "1 conversion; reload and back-button must not add another"},
        {"id": "LP-6", "severity": "P1", "pages": "/commercial-hvac-installation/",
         "issue": "Testimonials rendered 3x; doubled opening quotation mark",
         "evidence": "9 testimonial blocks for 3 unique quotes; '““Quality work at "
                     "reasonable rates.”' repeated 3x",
         "required_correction": ["Render each testimonial once.",
                                 "Correct the doubled opening quote.",
                                 "Keep attribution accurate and verifiable."],
         "owner": "web developer", "launch_blocker": False, "retest": "render and count"},
        {"id": "LP-7", "severity": "P2", "pages": "all 6",
         "issue": "tel:+14109141456 present in the DOM (wrong number)",
         "evidence": "hidden anchor with text 'Call Now' -> tel:+14109141456 on every page",
         "required_correction": ["Remove it, including hidden elements.",
                                 "410-914-1456 is the MIXED-SOURCE number and must never be "
                                 "static on a paid page."],
         "owner": "web developer", "launch_blocker": False,
         "retest": "assert the string 4109141456 appears nowhere in the HTML"},
        {"id": "LP-8", "severity": "P2", "pages": "all 6",
         "issue": "tel: hrefs are not E.164 and one is malformed",
         "evidence": "tel:4107056354 (no +1) and tel:(410) 705-6354 (unencoded parens/space)",
         "required_correction": ["Every clickable telephone link must be tel:+14107056354.",
                                 "Displayed text stays (410) 705-6354.",
                                 "410-761-0932 must never appear publicly.",
                                 "DNI must not replace the paid number with an unapproved one."],
         "owner": "web developer", "launch_blocker": False,
         "retest": "assert every a[href^=tel:] equals tel:+14107056354"},
        {"id": "LP-9", "severity": "P2", "pages": "/commercial-hvac-installation/",
         "issue": "Meta description duplicates the title",
         "evidence": "observed 'Commercial HVAC Installation in Central Maryland | Ambient "
                     "Cooling & Heating'",
         "required_correction": ["Set: 'Request commercial HVAC installation or replacement "
                                 "for your Central Maryland property from Ambient Cooling & "
                                 "Heating.'"],
         "owner": "web developer", "launch_blocker": False, "retest": "render and compare"},
        {"id": "LP-10", "severity": "P3", "pages": "all 6",
         "issue": "No canonical tag",
         "evidence": "link[rel=canonical] absent on all six",
         "required_correction": ["Add a self-referencing canonical to each page.",
                                 "PRESERVE the intended noindex,nofollow on these paid pages.",
                                 "PRESERVE the Privacy and Terms links.",
                                 "PRESERVE GTM-PQTPQ436, AW-11155434808, G-9X9ZHNCRWF and "
                                 "the WhatConverts script exactly as they are."],
         "owner": "web developer", "launch_blocker": False, "retest": "render and assert"},
    ],
    "must_not_change": [
        "GTM container GTM-PQTPQ436", "Google Ads tag AW-11155434808",
        "GA4 G-9X9ZHNCRWF", "the WhatConverts script and all number routing",
        "displayed paid number (410) 705-6354",
        "the noindex,nofollow behaviour of the paid pages",
        "the Privacy Policy and Terms links",
        "commercial-only content and the verified claims on the commercial page"],
    "deployment_rule": (
        "Do not publish without: website source, a staging implementation, a tested diff, "
        "a confirmed backup, a written rollback, and a NEW deployment approval fingerprint "
        "issued after staging evidence is returned."),
    "developer_must_return": [
        "staging URL with all ten defects corrected",
        "the exact diff",
        "backup confirmation and rollback procedure",
        "screenshot evidence desktop + mobile for all six pages",
        "24/24 GCLID probe result from staging",
        "proof one submission = 1 CRM record + 1 GTM event + 1 conversion",
        "confirmation the honeypot is untouched",
        "confirmation GTM/AW/GA4/WhatConverts are unchanged",
        "cache configuration evidence for the six URLs",
        "confirmation no synthetic QA marker remains in cached HTML"],
}
built["AMB-0915-LP-1"] = lp

# ---------------------------------------------------------------- AMB-0915-CONV-1
conv_now = {r.conversion_action.id: r.conversion_action for r in q(c, """
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.type, conversion_action.category,
           conversion_action.primary_for_goal, conversion_action.counting_type
    FROM conversion_action WHERE conversion_action.status = 'ENABLED'""")}
KEEP_PRIMARY = {
    "6885463625": "Ambient Cooling - LP -Submit Lead Forms - the one canonical website "
                  "form-lead action, WEBPAGE, ONE_PER_CLICK. This is the real form outcome.",
    "6885576934": "Ambient Cooling - Lp - Phone call leads - WEBSITE_CALL, ONE_PER_CLICK. "
                  "Measures a completed website-sourced call, a distinct lead source.",
    "1068114183": "Calls from ads - AD_CALL, ONE_PER_CLICK. Measures a completed call placed "
                  "from the call asset. A genuinely different lead source from a website call.",
}
TO_SECONDARY = {
    "6640721230": ("Clicks to call - MANY_PER_CLICK CONTACT. A click is not a completed "
                   "call, and it double-counts both call actions."),
    "6642544931": "Local actions - Directions - not a lead.",
    "6641739327": "Local actions - Website visits - not a lead.",
    "6642551975": "Local actions - Other engagements - not a lead.",
    "6954620053": "Local actions - Menu views - not a lead.",
    "7643656486": ("WC Lead - UPLOAD_CLICKS. Duplicates the website form action: on "
                   "2026-09-01 in campaign 24132507747 WC Lead recorded 2.00 while the "
                   "WEBPAGE form action recorded 1.00 for the same day and campaign."),
    "7643656075": ("WC Calls - UPLOAD_CALLS. Duplicates the two call actions above for the "
                   "same physical call."),
}
conv = {
    "plan_name": "AMB-0915-CONV-1",
    "approval_class": "conversion-change",
    "customer_id": CID, "exact_account_name": EXACT_NAME,
    "summary": ("Reduce 10 ENABLED Primary conversion actions to 3 real lead outcomes and "
                "demote 7 to Secondary. 7 operations. Bidding is unaffected in practice "
                "because all five campaigns run Maximize Clicks, but the Conversions column "
                "stops double-counting."),
    "principle": ("Calls from ads and website calls are DIFFERENT lead sources and both stay "
                  "Primary. What is removed is click-proxies, local actions and the "
                  "WhatConverts uploads that re-report an event already counted."),
    "before_state": {
        "enabled_primary_actions": sorted(str(i) for i, a in conv_now.items()
                                          if a.primary_for_goal),
        "count": sum(1 for a in conv_now.values() if a.primary_for_goal),
        "observed_duplication": ("2026-09-01, campaign 24132507747: WC Lead conversions=2.00 "
                                 "vs Ambient Cooling - LP -Submit Lead Forms conversions=1.00 "
                                 "on the same date and campaign"),
        "all_conversions_vs_primary_launch_to_date": {"primary": 14.0, "all": 81.0},
    },
    "operations": [
        {"operation": "SET_PRIMARY_FOR_GOAL_FALSE", "resource": "conversion_action",
         "conversion_action_id": cid, "name": conv_now[int(cid)].name
         if int(cid) in conv_now else cid,
         "before": "primary_for_goal = true", "after": "primary_for_goal = false",
         "reason": why}
        for cid, why in TO_SECONDARY.items()],
    "operation_count": len(TO_SECONDARY),
    "remains_primary": [{"conversion_action_id": k, "reason": v}
                        for k, v in KEEP_PRIMARY.items()],
    "deduplication_requirements": [
        "Verify every imported action carries a transaction or lead id before it is ever "
        "restored to Primary.",
        "Verify the website-call action's minimum call duration is a real qualification "
        "threshold, not 0 seconds.",
        "Confirm counting_type ONE_PER_CLICK on all three retained Primary actions.",
        "Confirm click-through and view-through windows are identical across the three."],
    "sequencing": ("DO NOT EXECUTE until AMB-0915-LP-1 is deployed and the 24/24 attribution "
                   "test passes. Changing conversion configuration while click ids are "
                   "unreliable would re-baseline onto broken data."),
    "historical_note": ("A conversion counted before a fix stays in the historical column "
                        "forever. This plan does not and cannot restate history. A clean "
                        "baseline starts on the execution date."),
    "risk": "MEDIUM - reporting changes immediately; bidding does not, because all five "
            "campaigns are Maximize Clicks and do not optimise to conversions.",
    "rollback": "Set primary_for_goal back to true on the same 7 action ids.",
    "unrelated_resource_assertion": (
        "No conversion action is created, renamed, paused or removed. No counting_type, "
        "attribution model, lookback window or value setting is edited. No campaign goal "
        "override is touched. No WhatConverts configuration is changed."),
}
built["AMB-0915-CONV-1"] = conv

# ---------------------------------------------------------------- AMB-0915-COMM-NEGRM-1
cf = json.loads((SNAP / f"commercial-negative-conflict-{STAMP}.json").read_text(encoding="utf-8"))
blockers = {}
for x in cf["reachable_and_blocked"]:
    for b in x["blockers"]:
        blockers.setdefault(b["criterion_id"], {"text": b["text"], "match": b["match"],
                                                "level": b["level"], "phrases": []})
        blockers[b["criterion_id"]]["phrases"].append(x["phrase"])
negrm = {
    "plan_name": "AMB-0915-COMM-NEGRM-1",
    "approval_class": "DESTRUCTIVE - removes negatives and therefore EXPANDS traffic",
    "customer_id": CID, "exact_account_name": EXACT_NAME,
    "exact_service": "Commercial HVAC Installation",
    "summary": (f"Remove {len(blockers)} campaign-level PHRASE negatives on {CAMP_INST} that "
                f"block real, reachable commercial buyer demand. "
                f"{len(blockers)} operations."),
    "method": ("Reachability-tested, not synthetic. 37 real commercial buyer phrases were "
               "tested against every ENABLED campaign, ad-group and account negative in "
               "scope. A phrase counts as a conflict only if it could actually match one of "
               "the two live commercial keywords. 26 phrases are clear; 11 are blocked."),
    "operations": [
        {"operation": "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD", "resource": "campaign_criterion",
         "campaign_id": CAMP_INST, "criterion_id": cid, "text": v["text"],
         "match": v["match"],
         "blocks_buyer_phrases": sorted(set(v["phrases"])),
         "evidence": ("the live commercial landing page sells this explicitly"
                      if v["text"] in ("rooftop",) else
                      "agency policy forbids this as a blanket negative"
                      if v["text"] in ("licensed", "certified") else
                      "a legitimate commercial property type"
                      if v["text"] in ("warehouse", "store") else
                      "capability not confirmed - see verdict"),
         "verdict": ("REMOVE" if v["text"] in ("rooftop", "licensed", "certified",
                                               "warehouse", "store") else "HOLD")}
        for cid, v in sorted(blockers.items(), key=lambda x: x[1]["text"])],
    "operation_count": len(blockers),
    "reason": (
        "`rooftop` is the critical one: the live commercial page's own H3 is 'Rooftop and "
        "Packaged Units' and the structured snippet created today lists 'Rooftop Units'. The "
        "campaign currently blocks the exact demand the page and the ad were built to serve. "
        "`licensed` and `certified` are on the agency never-auto-negative list. `warehouse` "
        "and `store` are ordinary commercial property types."),
    "hold_note": ("`industrial` is marked HOLD, not REMOVE. The landing page says commercial, "
                  "never industrial, and Ambient's industrial capability is not verified. "
                  "Removing it would buy traffic for a service that may not be offered. "
                  "Confirm capability with the client first."),
    "risk": ("MEDIUM-HIGH. This EXPANDS traffic in a campaign that is already the only one "
             "spending. Each removed negative can admit queries beyond the commercial ad "
             "group, because these are CAMPAIGN-level and the residential ad group shares "
             "the campaign."),
    "mitigation": ("The residential ad group 202339087634 will still be protected by the "
                   "planned BROAD `commercial` routing negative once the commercial route "
                   "can serve. Until then, monitor the search-term report daily."),
    "rollback": "Re-create the removed campaign negatives with the same text and match type.",
    "sequencing": "Execute only after the commercial RSAs are APPROVED and enabled, so the "
                  "regained demand has somewhere correct to land.",
    "unrelated_resource_assertion": (
        "No positive keyword, ad, asset, budget, bid, schedule or location changes. No "
        "ad-group negative changes. No account-level or shared-set negative changes. The 17 "
        "commercial ad-group negatives are untouched."),
}
built["AMB-0915-COMM-NEGRM-1"] = negrm

# ---------------------------------------------------------------- AMB-0915-CPC-HR-1
hr = q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                     campaign.target_spend.cpc_bid_ceiling_micros,
                     campaign_budget.amount_micros
              FROM campaign WHERE campaign.id = {CAMP_HR}""")[0]
budgets = {str(r.campaign.id): r.campaign_budget.amount_micros / 1e6 for r in q(c, f"""
    SELECT campaign.id, campaign_budget.amount_micros FROM campaign
    WHERE campaign.id IN ({IN5})""")}
cpc = {
    "plan_name": "AMB-0915-CPC-HR-1",
    "approval_class": "bid-change",
    "customer_id": CID, "exact_account_name": EXACT_NAME, "exact_service": "HVAC Repair",
    "summary": ("Raise the HVAC Repair Maximize Clicks CPC ceiling from $25.00 to $65.00. "
                "1 operation. One campaign, one variable."),
    "campaign_id": CAMP_HR, "campaign_name": hr.campaign.name,
    "before_state": {
        "cpc_bid_ceiling_usd": hr.campaign.target_spend.cpc_bid_ceiling_micros / 1e6,
        "daily_budget_usd": hr.campaign_budget.amount_micros / 1e6,
        "status": E(hr.campaign.status),
        "all_five_budgets": budgets,
        "combined_daily": round(sum(budgets.values()), 2),
        "planning_30_4": round(sum(budgets.values()) * 30.4, 2),
        "monthly_maximum": 13000.0,
        "headroom": round(13000.0 - sum(budgets.values()) * 30.4, 2)},
    "operations": [{"operation": "UPDATE_CAMPAIGN_CPC_BID_CEILING",
                    "resource": "campaign", "campaign_id": CAMP_HR,
                    "field_mask": "target_spend.cpc_bid_ceiling_micros",
                    "before_micros": 25000000, "after_micros": 65000000,
                    "before_usd": 25.00, "after_usd": 65.00}],
    "operation_count": 1,
    "why_65_and_not_30": [
        "Google Keyword Planner top-of-page bid estimate for the live keyword "
        "`hvac repair near me`, measured against the campaign's own 75-target Central "
        "Maryland geo: LOW $49.47, HIGH $126.18. The current $25.00 ceiling sits BELOW "
        "Google's own LOW estimate.",
        "`ac repair near me` estimates LOW $38.98 / HIGH $118.07 - also above $25.00.",
        "HVAC Repair's August average CPC when uncapped was $106.27 and it produced 4 of the "
        "account's conversions.",
        "Of the 13 clicks that have ever converted in this account, 12 cost more than every "
        "ceiling now in place; the cheapest converting click above $25 was $59.44.",
        "$65.00 sits between Google's LOW and HIGH top-of-page estimates - deliberately "
        "mid-band, not a return to uncapped bidding.",
        "A +20% step to $30.00 is rejected: it remains below the LOW estimate and would "
        "almost certainly reproduce the current zero-delivery result while consuming a test "
        "cycle."],
    "guardrails": {
        "daily_budget": "UNCHANGED at $78.95",
        "stop_loss": "$250.00 incremental spend with zero verified qualified lead",
        "max_exposure_before_review": "$250.00",
        "monitoring": ["technical health at ~24h and ~72h",
                       "review EVERY new search term",
                       "valid vs invalid click rate",
                       "impression share, lost-IS rank, lost-IS budget",
                       "no performance verdict before 14 settled days"],
        "rollback": "set target_spend.cpc_bid_ceiling_micros back to 25000000",
        "rollback_triggers": ["$250 incremental spend with no verified qualified lead",
                              "irrelevant search terms appearing at volume",
                              "any ad policy change", "tracking failure",
                              "abnormal invalid-click rate"],
        "do_not_change_during_the_test": [
            "any RSA in HVAC Repair", "any keyword in HVAC Repair",
            "any negative in HVAC Repair", "locations", "schedule",
            "the HVAC Repair landing page", "any other campaign's ceiling"]},
    "budget_safety": {
        "ceiling_change_does_not_alter_daily_budget": True,
        "combined_daily_after": round(sum(budgets.values()), 2),
        "planning_30_4_after": round(sum(budgets.values()) * 30.4, 2),
        "within_13000_monthly_maximum": sum(budgets.values()) * 30.4 <= 13000.0},
    "HARD_GATE": (
        "DO NOT EXECUTE until: (1) AMB-0915-LP-1 is deployed, (2) the attribution probe "
        "returns 24/24, and (3) AMB-0915-CONV-1 is executed or a reliable manual "
        "qualified-lead verification path is agreed. Raising a bid while form attribution is "
        "broken buys traffic that cannot be measured."),
    "economic_warning": (
        "Measured paid-search CPQL over the last 90 settled days is $827.45 upper bound "
        "($8,274.54 spend / 10 WhatConverts quotable=Yes paid-search leads). Even the most "
        "generous correction for click-id loss leaves it near $394. Every provisional "
        "guardrail is $150-$280. This test is therefore a DELIVERY and MEASUREMENT test - "
        "does volume return and can we see it - not a profitability claim. If volume returns "
        "at a CPQL still far above guardrail, the correct next move is landing-page "
        "conversion rate, not more bid."),
    "risk": "MEDIUM. Bounded by the $78.95 daily budget and the $250 stop-loss.",
    "unrelated_resource_assertion": (
        "Only campaign 24132507750's target_spend.cpc_bid_ceiling_micros changes. Budget, "
        "status, networks, geo, schedule, keywords, negatives, ads, assets and conversion "
        "settings are untouched, on this and all other campaigns."),
}
built["AMB-0915-CPC-HR-1"] = cpc

# ---------------------------------------------------------------- AMB-0915-RSA-ACR-3
old = json.loads((PLANS / "AMB-0910-RSA-ACR-2.json").read_text(encoding="utf-8"))
old_fp = old.pop("fingerprint", None)
copy_ops = []
def _walk(o):
    if isinstance(o, dict):
        if any(k in o for k in ("headlines_pinned_headline_1", "headlines_unpinned",
                                "descriptions")):
            copy_ops.append(o)
        for v in o.values():
            _walk(v)
    elif isinstance(o, list):
        for x in o:
            _walk(x)
_walk(old)
acr_ads_now = [str(r.ad_group_ad.ad.id) for r in q(c, f"""
    SELECT ad_group.id, ad_group_ad.ad.id FROM ad_group_ad
    WHERE ad_group.id = {ACR_AG}""")]
acr = {
    "plan_name": "AMB-0915-RSA-ACR-3",
    "approval_class": "create-paused",
    "customer_id": CID, "exact_account_name": EXACT_NAME, "exact_service": "AC Repair",
    "supersedes": (f"AMB-0910-RSA-ACR-2 / {old_fp} - the on-disk plan no longer recomputes "
                   f"to its published fingerprint (recomputes to 4C7E73A3194D) and carries no "
                   f"operation_count field, so it is not approvable as {old_fp}. The AD COPY "
                   f"itself was re-checked and is CLEAN: zero barred or withdrawn claims in "
                   f"any headline or description. This plan re-issues the same copy under a "
                   f"fingerprint that verifies."),
    "summary": "Create 1 AC Repair RSA challenger PAUSED in ad group 202339087834. "
               "1 operation.",
    "before_state": {"ad_group_id": ACR_AG, "ads_now": acr_ads_now,
                     "ads_count": len(acr_ads_now),
                     "after_count": len(acr_ads_now) + 1,
                     "google_rsa_cap_per_ad_group": 3,
                     "within_cap": len(acr_ads_now) + 1 <= 3},
    "operations": copy_ops[:1] if copy_ops else [],
    "operation_count": 1,
    "reason": ("AC Repair runs 2 ENABLED APPROVED RSAs and has had zero clicks since "
               "2026-09-04. A third, materially different challenger is ready and costs "
               "nothing while paused."),
    "sequencing": ("LOW priority. AC Repair currently cannot win auctions at a $25 ceiling, "
                   "so a new ad changes nothing until the bid question is settled. Approve "
                   "this only if you want it staged and policy-reviewed in advance."),
    "risk": "LOW - created PAUSED.",
    "rollback": "set the created ad_group_ad to REMOVED",
    "unrelated_resource_assertion": ("The two existing AC Repair ads 820900825416 and "
                                     "820900825419 remain ENABLED and unedited. No other "
                                     "resource changes."),
}
built["AMB-0915-RSA-ACR-3"] = acr

# ---------------------------------------------------------------- emit
print("=" * 78)
lines = []
for name, plan in built.items():
    fp = approval_code(plan)
    plan["fingerprint"] = fp
    (PLANS / f"{name}.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    n = plan.get("operation_count", len(plan.get("defects", [])) or 0)
    kind = plan.get("approval_class", "")
    print(f"{name:26s} {fp}  ops={n:<3} {kind}")
    if name == "AMB-0915-COMM-NEGRM-1":
        lines.append(f"APPROVE DESTRUCTIVE {name} {fp} {n} operations FOR {CID}")
    elif name == "AMB-0915-LP-1":
        lines.append(f"APPROVE {name} {fp} specification FOR ambientcoolingandheating.com")
    else:
        lines.append(f"APPROVE {name} {fp} {n} operations FOR {CID}")
print("\n--- APPROVAL LINES ---")
for l in lines:
    print(l)
(SNAP / f"plans-built-{STAMP}.json").write_text(
    json.dumps({n: p["fingerprint"] for n, p in built.items()}, indent=1), encoding="utf-8")
print(f"\nWROTE {len(built)} plans to {PLANS}")
