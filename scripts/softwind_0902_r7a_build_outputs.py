#!/usr/bin/env python3
"""Build the R7A split-package audit CSVs and manifest. Local build, no API calls."""
from __future__ import annotations

import csv
import glob
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "clients/softwind-power-washing/audits"
PLN = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"

NA = "ACCESS UNAVAILABLE - NOT INSPECTED"
PUB = "PUBLIC CODE LOCATION CONFIRMED - INTERNAL WORDPRESS SOURCE RECORD UNKNOWN"


def w(path, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        c = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        c.writeheader()
        c.writerows(rows)
    print(f"wrote {path.name}: {len(rows)} rows")


# ---------------------------------------------------------------- page CSV
src = json.loads(Path(sorted(glob.glob(str(
    SNAP / "r7a-public-code-inspection-*.json")))[-1]).read_text(encoding="utf-8"))
page_rows = []
for p in src["pages"]:
    if "ERROR" in p:
        continue
    page_rows.append({
        "url": p["url"],
        "http_status": p["http_status"],
        "redirect_chain_len": len(p["redirect_chain"]) - 1,
        "browser_title": p["browser_title"],
        "raw_source_saved": p["raw_source_saved"],
        "rendered_dom_saved": p["rendered_dom_saved"],
        "csp_header": p["csp"],
        "AW_17878095007_present": p["masonry_present"],
        "AW_18369652705_present": p["powerwashing_present"],
        "gtm_network_loads": p["gtm_load_count"],
        "gtm_datalayer_gtmjs_pushes": p["datalayer"].get("events", []).count("gtm.js"),
        "gtag_js_loader_count": len(p["gtag_js_loaders"]),
        "whatconverts_active": bool(p["wc_cookies"]),
        "whatconverts_host_requests": len(p["whatconverts_host_requests"]),
        "wc_swap_cookie": p["wc_swap_cookie"],
        "iconnode_requests": len(p["iconnode_requests"]),
        "iconnode_method": (p["iconnode_requests"][0]["method"]
                            if p["iconnode_requests"] else ""),
        "clickcease_requests": p["clickcease_requests"],
        "gform_1_count": p["gform_count"],
        "duplicate_html_id_count": p["duplicate_id_count"],
        "honeypot_present_count": p["honeypot_present"],
        "honeypot_hidden": p["honeypot_hidden"],
        "honeypot_values_empty": all(v == "" for v in p["honeypot_values"]) if
        p["honeypot_values"] else True,
        "visible_phone": ";".join(p["phones_in_text"]),
        "tel_hrefs": ";".join(p["tel_links"]),
        "malformed_tel": ";".join(p["malformed_tel_links"]),
        "form_action": ";".join(x.split("?")[0] for x in p["form_actions"]),
        "confirmation_url": ("https://offer.softwindli.com/thank-you/"
                             if p["gform_count"] else "n/a"),
        "direct_thankyou_conversion_fires": p["direct_conversion_fires"],
        "true_conversion_accounts": ";".join(
            c["account"] for c in p["true_conversion_requests"]),
        "datalayer_events": ";".join(p["datalayer"].get("events", [])),
        "form_start_events": p["form_start_events"],
        "form_submit_events": p["form_submit_events"],
        "masonry_website_call_wcm": p["masonry_wcm"],
        "powerwashing_website_call_wcm": p["powerwashing_wcm"],
        "masonry_form_data_posts": p["masonry_form_data_posts"],
        "powerwashing_form_data_posts": p["powerwashing_form_data_posts"],
        "sgcaptcha_observed": p["sgcaptcha_observed"],
        "total_requests": p["total_requests"],
    })
w(AUD / "2026-09-02-r7a-page-code-inspection.csv", page_rows)

# ---------------------------------------------------------- source-of-truth
S = [
    dict(component="AW-17878095007 (sibling Masonry tag)",
         system_of_origin="Google tag / GTM-P3LD97NN (probable) - NOT hardcoded in page HTML",
         exact_location=("googletagmanager.com/gtag/js?id=AW-17878095007&cx=c&gtm=4e68v1 - "
                         "async-injected; the literal id appears exactly ONCE in rendered "
                         "source and only inside that injected URL. " + PUB),
         current_trigger="all pages (7/7)", current_value="active on every paid page + /thank-you/",
         pages_affected="7", destination="Google Ads customer 2429758629",
         data_transmitted=("page_view, user-list/remarketing, website-call replacement (wcm), "
                           "form_start, form_submit, form-data POSTs, GCLID"),
         google_ads_account_receiving="2429758629 Softwind Landscape & Masonry - Live",
         conflict="preempts Power Washing website-call action 7708765130", severity="P0",
         safe_correction="scope the tag off Power Washing URLs (GTM page-path exception)",
         rollback="re-enable the trigger / remove the exception",
         claude_can_execute="NO - no GTM credential", developer_ticket_required="ONLY IF hardcoded",
         cross_account_authorization_required="YES", separate_post_change_test_required="YES"),
    dict(component="AW-18369652705 (Power Washing tag)",
         system_of_origin="Google tag / GTM-P3LD97NN (probable)",
         exact_location="googletagmanager.com/gtag/js?id=AW-18369652705&cx=c&gtm=4e68v1. " + PUB,
         current_trigger="all pages (7/7)", current_value="active, correct account",
         pages_affected="7", destination="Google Ads customer 1521725229",
         data_transmitted="page_view, remarketing, conversion on /thank-you/",
         google_ads_account_receiving="1521725229", conflict="none - this is correct",
         severity="OK", safe_correction="PRESERVE", rollback="n/a",
         claude_can_execute="NO", developer_ticket_required="NO",
         cross_account_authorization_required="NO", separate_post_change_test_required="NO"),
    dict(component="GTM-P3LD97NN", system_of_origin="WordPress theme AND a second injector",
         exact_location=("TWO inline bootstraps, TWO gtm.js script tags, TWO noscript ns.html "
                         "iframes in delivered HTML; whitespace differs between the two "
                         "bootstraps, indicating two separate injectors. " + PUB),
         current_trigger="every page", current_value="container initialised TWICE",
         pages_affected="7", destination="GTM container",
         data_transmitted="dataLayer receives two gtm.js pushes",
         google_ads_account_receiving="n/a",
         conflict="every tag in the container can fire twice", severity="P1",
         safe_correction="remove one bootstrap", rollback="restore the removed snippet",
         claude_can_execute="NO", developer_ticket_required="YES - DEV-R7A3-03",
         cross_account_authorization_required="NO", separate_post_change_test_required="YES"),
    dict(component="FddkCOul59scEOHPqrdE (form conversion label)",
         system_of_origin="Google Ads conversion action 7708725995",
         exact_location="verified via Google Ads API tag_snippets, 4 snippets",
         current_trigger="fires on ANY /thank-you/ page view - PROVEN on a bare visit",
         current_value="AW-18369652705/FddkCOul59scEOHPqrdE, ONE_PER_CLICK, 90-day window",
         pages_affected="1 (/thank-you/)", destination="Google Ads 1521725229",
         data_transmitted="conversion event", google_ads_account_receiving="1521725229",
         conflict="fires without a real submission - inflation risk", severity="P0",
         safe_correction="bind to a verified form-success signal, not the page path",
         rollback="restore the page-path trigger",
         claude_can_execute="NO - GTM change", developer_ticket_required="YES - DEV-R7A3-04",
         cross_account_authorization_required="NO", separate_post_change_test_required="YES"),
    dict(component="ReAcCMrX6dscEOHPqrdE (website-call label)",
         system_of_origin="Google Ads conversion action 7708765130",
         exact_location=("API tag_snippets: gtag('config','AW-18369652705/ReAcCMrX6dscEOHPqrdE',"
                         "{'phone_conversion_number':'(631)502-7946'})"),
         current_trigger="NONE - never deployed", current_value="0 wcm requests on all 7 pages",
         pages_affected="0", destination="Google Ads 1521725229",
         data_transmitted="none - not deployed", google_ads_account_receiving="none",
         conflict="the sibling account occupies this path instead", severity="P0",
         safe_correction="deploy only if native Google call replacement is the chosen architecture",
         rollback="remove the config line",
         claude_can_execute="NO", developer_ticket_required="DEPENDS ON ARCHITECTURE",
         cross_account_authorization_required="NO", separate_post_change_test_required="YES"),
    dict(component="WhatConverts tracking script",
         system_of_origin="WordPress plugin",
         exact_location=('<script id="whatconverts-tracking-script-js" '
                         'src="//s.ksrndkehqnwntyxlhgto.com/158931.js?ver=7.1"> plus inline '
                         '"whatconverts-tracking-script-js-before" config. The -js / ver= '
                         'handle is the WordPress wp_enqueue_script signature.'),
         current_trigger="every page", current_value="ACTIVE - account/profile number 158931",
         pages_affected="7", destination="WhatConverts account 158931",
         data_transmitted="source, medium, campaign, content, term, GCLID via wc_client cookie",
         google_ads_account_receiving="n/a",
         conflict="none for attribution", severity="OK - attribution works",
         safe_correction="PRESERVE", rollback="n/a",
         claude_can_execute="NO - empty API token", developer_ticket_required="NO",
         cross_account_authorization_required="NO", separate_post_change_test_required="NO"),
    dict(component="WhatConverts DNI (number replacement)",
         system_of_origin="WhatConverts account configuration",
         exact_location="WhatConverts account 158931 - " + NA,
         current_trigger="wc_swap cookie set on every page",
         current_value="wc_swap = 6315025402+..+6315535927+..+197159 - NEITHER reaches the DOM",
         pages_affected="7", destination="WhatConverts",
         data_transmitted="n/a - replacement does not execute",
         google_ads_account_receiving="n/a",
         conflict="the sibling account's wcm replacement runs on the same displayed number",
         severity="P1",
         safe_correction="ROOT CAUSE NOT DETERMINED - requires authenticated WhatConverts read",
         rollback="n/a", claude_can_execute="NO - WHATCONVERTS_API_TOKEN is empty",
         developer_ticket_required="NO - account config, not site code",
         cross_account_authorization_required="NO", separate_post_change_test_required="YES"),
    dict(component="process.iconnode.com/google-ads/",
         system_of_origin="NOT in page HTML - injected at runtime, GTM Custom HTML most likely",
         exact_location="zero occurrences in rendered source; 1 POST per page in network. " + PUB,
         current_trigger="every page load + form submission",
         current_value="1 POST per page", pages_affected="7",
         destination="process.iconnode.com (third-party)",
         data_transmitted="UNKNOWN - payload not reproduced",
         google_ads_account_receiving="unknown",
         conflict="undocumented processor in the lead path", severity="P1",
         safe_correction="NONE YET - identify owner and authorization first",
         rollback="n/a", claude_can_execute="NO",
         developer_ticket_required="YES - DEV-R7A3-06 (investigation only)",
         cross_account_authorization_required="NO", separate_post_change_test_required="NO"),
    dict(component="ClickCease",
         system_of_origin="WordPress plugin / inline injector",
         exact_location="https://www.clickcease.com/monitor/stat.js plus a noscript monitor pixel",
         current_trigger="every page", current_value="ACTIVE", pages_affected="7",
         destination="ClickCease", data_transmitted="click-fraud telemetry",
         google_ads_account_receiving="n/a", conflict="none", severity="OK",
         safe_correction="PRESERVE - do not remove or replace", rollback="n/a",
         claude_can_execute="NO", developer_ticket_required="NO",
         cross_account_authorization_required="NO", separate_post_change_test_required="NO"),
    dict(component="Duplicate Gravity Form",
         system_of_origin="WordPress page template / builder",
         exact_location=("TWO form#gform_1 per offer page with 22 duplicate HTML ids "
                         "(gform_1, gform_wrapper_1, gform_submit_button_1, input_1_1/3/4/7/9, "
                         "et-boc). " + PUB),
         current_trigger="page render", current_value="2 forms, 22 duplicate ids",
         pages_affected="6 offer pages (thank-you has 0 forms, 2 duplicate ids)",
         destination="n/a", data_transmitted="n/a", google_ads_account_receiving="n/a",
         conflict="id-based tracker binding resolves to the wrong copy; accessibility defect",
         severity="P1", safe_correction="render one form or make every id unique",
         rollback="restore the template revision", claude_can_execute="NO",
         developer_ticket_required="YES - DEV-R7A3-01",
         cross_account_authorization_required="NO", separate_post_change_test_required="YES"),
    dict(component="Malformed telephone link",
         system_of_origin="WordPress shared header/footer or hero component",
         exact_location='a[href="tel:(631)"] present alongside a[href="tel:(631) 502-7946"]. ' + PUB,
         current_trigger="page render", current_value="tel:(631) - dials nothing",
         pages_affected="7 (ALL, including /thank-you/)", destination="n/a",
         data_transmitted="n/a", google_ads_account_receiving="n/a",
         conflict="dead click-to-call on a mobile-dominated account", severity="P1",
         safe_correction="repair or remove; use tel:+16315027946",
         rollback="restore markup", claude_can_execute="NO",
         developer_ticket_required="YES - DEV-R7A3-02",
         cross_account_authorization_required="NO", separate_post_change_test_required="YES"),
    dict(component="SG-Captcha",
         system_of_origin="SiteGround hosting", exact_location="/.well-known/sgcaptcha/",
         current_trigger="intermittent",
         current_value="absent on all 7 pages 2026-09-02; observed 2026-09-01 with HTTP 202",
         pages_affected="7 potentially", destination="n/a", data_transmitted="n/a",
         google_ads_account_receiving="n/a", conflict="may challenge paid visitors",
         severity="P2", safe_correction="MONITOR - do not disable without evidence",
         rollback="n/a", claude_can_execute="NO",
         developer_ticket_required="YES - DEV-R7A3-07 (investigation)",
         cross_account_authorization_required="NO", separate_post_change_test_required="NO"),
]
w(AUD / "2026-09-02-r7a-source-of-truth-matrix.csv", S)

# ------------------------------------------------------------ GTM inventory
gtm = [dict(field=f, value=NA, evidence_source="no Tag Manager OAuth scope and no GTM credential",
            public_evidence_substitute=sub)
       for f, sub in [
           ("GTM account name", ""), ("Container name", ""),
           ("Container public ID", "GTM-P3LD97NN - confirmed from delivered HTML"),
           ("Container numeric ID", ""), ("Published version", ""),
           ("Published timestamp", ""), ("Current workspace", ""),
           ("Unpublished changes", ""), ("Environments", ""),
           ("Consent configuration", "no CSP header; consent-mode ccm/collect requests observed"),
           ("Conversion Linker", ""), ("Google tags", "gtag/js loaders observed for "
                                       "AW-18369652705, AW-17878095007, G-D4BZM40RYD"),
           ("Google Ads conversion tags", "conversion fires on /thank-you/ to 18369652705"),
           ("Google Ads website-call tags", "wcm fires for 17878095007 on all 7 pages; "
            "zero for 18369652705"),
           ("Google Ads remarketing tags", "viewthroughconversion + rmkt/collect + 1p-user-list "
            "for BOTH accounts"),
           ("GA4 tags", "G-D4BZM40RYD observed"),
           ("WhatConverts tags", "loaded by a WordPress plugin, not GTM"),
           ("ClickCease tags", "clickcease.com/monitor/stat.js observed"),
           ("Custom HTML tags", "process.iconnode.com POST has no HTML source - "
            "consistent with a GTM Custom HTML tag"),
           ("iconnode tags", "1 POST per page, zero source occurrences"),
           ("Form listeners", "en=form_start / en=form_submit observed for 17878095007 only"),
           ("Pageview triggers", ""), ("Thank-you-page triggers",
                                       "PROVEN: bare /thank-you/ visit fires the conversion"),
           ("History-change triggers", ""), ("Gravity Forms triggers", ""),
           ("Custom-event triggers", "dataLayer carries only gtm.js x2, gtm.dom, gtm.load - "
            "NO custom form-success event exists"),
           ("Variables for form success", "none observable"),
           ("Variables for phone replacement", ""),
           ("Variables for click ids and UTMs", "GCLID/GBRAID/WBRAID/UTMs all reach the form POST"),
           ("Tag firing priority", ""), ("Tag sequencing", ""), ("Trigger exceptions", "")]]
w(AUD / "2026-09-02-r7a-gtm-inventory.csv", gtm)

# --------------------------------------------------- WhatConverts inventory
wc = [dict(field=f, value=v, evidence=e) for f, v, e in [
    ("Authenticated API access", "UNAVAILABLE - WHATCONVERTS_API_TOKEN present but EMPTY",
     "read from .env; length 0"),
    ("Master account", NA, ""), ("Profile name", NA, ""),
    ("Profile ID", "158931 (PROBABLE)",
     "tracking script s.ksrndkehqnwntyxlhgto.com/158931.js and wc_visitor cookie prefix 158931-"),
    ("Profile domain", NA, ""), ("Profile time zone", NA, ""),
    ("Google Ads integrations", NA, ""), ("Connected Google Ads customer IDs", NA, ""),
    ("Conversion-action mappings", NA, ""),
    ("Tracking numbers", "PARTIAL - wc_swap nominates 6315025402 and 6315535927",
     "wc_swap cookie, identical on all 7 pages"),
    ("Dynamic Number Pools / pool id / size / numbers", NA, ""),
    ("Destination numbers", NA, ""),
    ("Number-replacement source number", "UNKNOWN - the displayed (631) 502-7946 is never replaced",
     "DOM shows the static number in body text and tel: href on all 7 pages"),
    ("Source / medium / paid-search rules", NA, ""),
    ("Swap selectors / text-matching / tel: rules", NA, ""),
    ("Included / excluded domains", NA, ""),
    ("Cookie configuration", "wc_visitor, wc_client, wc_client_current, wc_swap all set",
     "browser cookie jar, all 7 pages"),
    ("GCLID capture", "WORKING", "wc_client carries GM-TEST-SYNTHETIC-GCLID-20260901"),
    ("GBRAID / WBRAID capture", "reached the form POST; WhatConverts storage not verifiable", ""),
    ("UTM capture", "WORKING - source, medium, campaign, content, term",
     "wc_client cookie chain"),
    ("Campaign / ad group / keyword / landing page capture", NA, ""),
    ("Form tracking", "PROBABLE - POSTs to p.ksrndkehqnwntyxlhgto.com/lead/form and /keyword/ "
     "at submission", "PLAN-R1B network capture 2026-09-02"),
    ("Gravity Forms integration", NA, ""), ("Call recording", NA, ""),
    ("Lead intelligence / Quotable", NA, ""), ("Spam filtering", NA, ""),
    ("Duplicate handling", NA, ""), ("Minimum call duration", NA, ""),
    ("Qualified-call criteria", NA, ""), ("Google Ads conversion upload", NA, ""),
    ("Qualified-lead upload", NA, ""), ("Sold-job upload", NA, ""),
    ("Unique lead / transaction ID", NA, ""),
    ("Last successful lead capture", NA + " - test lead lookup NOT possible", ""),
    ("Last successful conversion upload", NA, ""),
    ("DNI ROOT CAUSE", "NOT DETERMINED - requires authenticated WhatConverts read. "
     "Cookie evidence alone is insufficient and the brief forbids inferring from cookies.", ""),
]]
w(AUD / "2026-09-02-r7a-whatconverts-inventory.csv", wc)

# ------------------------------------------------------------- phone matrix
phones = [
    dict(number="+1 631-502-7946", role="approved Power Washing landing-page number",
         where_seen="body text + tel: href on all 7 pages; dn= of the sibling wcm request; "
                    "phone_conversion_number of conversion action 7708765130; Google Ads call "
                    "asset 403335872180",
         whatconverts_label=NA, active="YES", replaces="n/a", destination=NA,
         connected_google_ads="1521725229 (call asset + website-call action)"),
    dict(number="+1 631-502-5402", role="previously recorded untracked main-site number",
         where_seen="wc_swap cookie position 1; client.yaml untracked_phone_on_main_site",
         whatconverts_label=NA, active="nominated by wc_swap but NEVER rendered", replaces=NA,
         destination=NA, connected_google_ads="none"),
    dict(number="+1 631-553-5927", role="WhatConverts swap candidate",
         where_seen="wc_swap cookie position 2; recorded 2026-08-26 on main-site pages",
         whatconverts_label=NA, active="nominated by wc_swap but NEVER rendered", replaces=NA,
         destination=NA, connected_google_ads="none"),
    dict(number="+1 631-519-8373", role="GLE (Local Services) Power Washing tracking number",
         where_seen="NOT present anywhere in the Google Ads account or on any inspected page",
         whatconverts_label=NA, active="UNKNOWN", replaces="n/a", destination=NA,
         connected_google_ads="none - Local Services, outside this account"),
    dict(number="+1 631-315-8655", role="GBP (Business Profile) Power Washing tracking number",
         where_seen="NOT present anywhere in the Google Ads account or on any inspected page",
         whatconverts_label=NA, active="UNKNOWN", replaces="n/a", destination=NA,
         connected_google_ads="none - Business Profile, outside this account"),
]
w(AUD / "2026-09-02-r7a-phone-number-roles.csv", phones)

# ------------------------------------------------------------------ manifest
now = datetime.now(ZoneInfo("America/New_York"))
man = {
    "generated_account_local": now.isoformat(),
    "series": "R7A split package - 2026-09-02",
    "target": {"exact_child_account_name": "Softwind Power Washing - Live",
               "child_customer_id": "1521725229", "exact_service": "Power Washing",
               "manager_customer_id": "3373711342"},
    "access_reality": {
        "google_ads": "AVAILABLE - used",
        "google_tag_manager": ("NOT AVAILABLE - the Google OAuth refresh token carries only "
                               "https://www.googleapis.com/auth/adwords. No tagmanager scope, "
                               "no separate GTM credential, no stored browser session. "
                               "CLAUDE.md forbids broadening the Ads OAuth token."),
        "whatconverts": ("NOT AVAILABLE - WHATCONVERTS_API_TOKEN exists as a key in .env but "
                         "its value is EMPTY (length 0)."),
        "wordpress": "NO ACCESS BY DESIGN - developer tickets required",
    },
    "void_registry": [{
        "plan_id": "PLAN-R7A", "fingerprint": "65A748A51E48",
        "state": "SUPERSEDED - DO NOT HONOR", "do_not_honour": True,
        "superseded_on": "2026-09-02",
        "reason": ("Combined GTM, WhatConverts, WordPress and sibling-account changes in one "
                   "fingerprint; selected a call architecture before any authenticated "
                   "WhatConverts read; treated unavailable WordPress access as an execution "
                   "dependency rather than a developer ticket. Replaced by the split package."),
        "original_file_preserved": ("clients/softwind-power-washing/plans/"
                                    "2026-09-02-plan-r7a-website-tracking-form-call-repair.yaml"),
    }],
    "tracks": [
        {"track": "A", "plan_id": "PLAN-R7A1-GTM",
         "file": "clients/softwind-power-washing/plans/2026-09-02-plan-r7a1-gtm-form-measurement.yaml",
         "status": "BLOCKED - NO GTM CREDENTIAL", "executable_actions": 0,
         "object_count": 0, "mutation_count": 0, "fingerprint": None,
         "fingerprint_withheld_because": ("rule 18 - exact tag, trigger and variable IDs and "
                                          "current values are unknown without an authenticated "
                                          "GTM read; a plan with zero executable actions and "
                                          "placeholder IDs must not be fingerprinted")},
        {"track": "B", "plan_id": "PLAN-R7A2-WHATCONVERTS",
         "file": ("clients/softwind-power-washing/plans/"
                  "2026-09-02-plan-r7a2-whatconverts-call-attribution.yaml"),
         "status": "BLOCKED - NO WHATCONVERTS CREDENTIAL", "executable_actions": 0,
         "object_count": 0, "mutation_count": 0, "fingerprint": None,
         "fingerprint_withheld_because": ("rule 18 - profile, pool, number and rule IDs and "
                                          "current values are unknown; the DNI root cause was "
                                          "not determined and must not be inferred from cookies")},
        {"track": "C", "plan_id": "DEV-R7A3",
         "file": "clients/softwind-power-washing/dev-tickets/2026-09-02-r7a-developer-ticket-index.md",
         "status": "READY TO SEND", "tickets": 8, "fingerprint": None,
         "fingerprint_withheld_because": "developer tickets are never fingerprinted"},
        {"track": "D", "plan_id": "PLAN-R7A4-CROSS-ACCOUNT",
         "file": "clients/softwind-power-washing/plans/2026-09-02-plan-r7a4-sibling-tag-scoping.yaml",
         "status": "BLOCKED - SEPARATE SIBLING-ACCOUNT WORK ORDER AND APPROVAL REQUIRED",
         "executable_actions": 0, "mutation_count": 0, "fingerprint": None,
         "fingerprint_withheld_because": ("cross-account action cannot be fingerprinted under the "
                                          "Power Washing work order")},
    ],
    "google_ads_mutation_count_all_tracks": 0,
    "approval_commands_emitted": 0,
    "next_action": {
        "type": "DEVELOPER TICKET",
        "ticket": ("clients/softwind-power-washing/dev-tickets/"
                   "2026-09-02-dev-r7a-04-form-success-event.md"),
        "reason": ("Highest measurement impact with the smallest blast radius, and the only "
                   "action on the critical path that needs neither GTM nor WhatConverts "
                   "credentials. A verified dataLayer form-success event is the prerequisite "
                   "for fixing the proven direct-/thank-you/ conversion defect, and every "
                   "later GTM correction depends on having a trustworthy success signal."),
        "fingerprint": None, "approval_command": None,
    },
}
(PLN / "2026-09-02-r7a-split-plan-manifest.json").write_text(
    json.dumps(man, indent=2), encoding="utf-8")
print("wrote 2026-09-02-r7a-split-plan-manifest.json")
