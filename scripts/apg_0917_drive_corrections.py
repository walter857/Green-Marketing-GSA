#!/usr/bin/env python3
"""2026-09-17 in-place corrections to the two Apogee Drive documents.

Edits the EXISTING documents so Drive IDs and version history are preserved.
Never creates a replacement doc. Never deletes a Drive file.
Plain hyphens only in every inserted string.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOK = r"D:\MG\secrets\green-marketing-drive-token.json"
creds = Credentials.from_authorized_user_file(TOK)
if not creds.valid:
    creds.refresh(Request())
    Path(TOK).write_text(creds.to_json(), encoding="utf-8")
docs = build("docs", "v1", credentials=creds, cache_discovery=False)

STRATEGY = "1BDMXgZO_5byH3nCXw7XGp7YahRT1hklsqwHYlWHQWVM"
LANDING = "19MQ3J11WiUuFQZn9kCRih3sBh0BR5kp_wE_ctcxY8Ok"

BANNED = {"\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
          "\u201c": '"', "\u201d": '"'}


def clean(s: str) -> str:
    for a, b in BANNED.items():
        s = s.replace(a, b)
    return s


def doc_end(fid):
    d = docs.documents().get(documentId=fid).execute()
    return d["body"]["content"][-1]["endIndex"]


# =====================================================================
# 1. LANDING PAGE DOC - remove the unverifiable reviews section
# =====================================================================
REVIEWS_NOTE = clean("""
SECTION REMOVED 2026-09-17. Do not build a reviews or testimonial section on the paid
landing page.

Reason: Google reviews could not be verified. On 2026-09-17 the Google knowledge panel for
Apogee Lawns displayed no star rating and no review count, and the Google Business Profile
owner view prompted "Get more reviews". The only third-party rating found was Facebook,
showing 5.0 from a single review. The two excerpts previously drafted here were taken from
the Apogee website, not from Google, and no reviewer, star rating or date could be
confirmed against a live Google review.

Standing rule: if reviews cannot be verified, omit the testimonial quotes from production.

This also means the "5 Star Google Rating" wording that currently appears on the organic
Apogee website must not be reused in Google Ads copy or on this paid landing page.

Reinstate this section only when real Google reviews exist and each quote can be matched to
a live review with its reviewer name, star rating and date. Do not build review schema or
aggregate-rating schema from selected reviews.
""")

SETTLED_LANDING = clean("""

14. CURRENT IMPLEMENTATION STATUS, 2026-09-17

This section records settled facts. It replaces earlier provisional wording.

Canonical paid landing page: https://apogeelawns.com/permanent-christmas-lights-lincoln-ne/
Dedicated thank-you page: https://apogeelawns.com/thank-you/permanent-christmas-lights/
Both URLs currently return HTTP 404. Publishing them is developer work and is the main
enablement blocker.

One canonical landing page serves both ad groups. Do not build one page per ad group and do
not create near-duplicate pages to influence Quality Score. Google reports Quality Score at
the keyword level and duplicate page count is not a scoring factor.

Displayed phone on the paid funnel: 402-526-5754, linked as tel:+14025265754.
That number is a WhatConverts tracking number. It forwards to 402-202-7261, which is the
number published across the organic website, and calls are answered by a receptionist.
Do not change the sitewide organic number. Keep 402-526-5754 inside the paid funnel only.

Live-answer coverage in Central Time: Monday to Friday 08:00 to 17:00, Saturday 08:00 to
12:00, Sunday closed. The Search campaign and both forms stay eligible 24 hours a day.
Only the Google Ads call asset is restricted to the hours above.

Google Ads conversion actions now exist on child account 816-462-6278. All three are
Secondary and stay Secondary until production QA passes:
- Lead | Permanent Lights | Form Submit | Thank You, action 7772803337,
  AW-18453077620/KOL7CImirvocEPS8jt9E. This is the only form conversion sent to Google Ads.
- Call | Permanent Lights | Ads | 60s, action 7773013199, AD_CALL, 60 second minimum.
- Call | Permanent Lights | Website | 60s, action 7773043879,
  AW-18453077620/lp3jCKf5vPocEPS8jt9E. Retained but unused. WhatConverts owns website-call
  measurement, so no Google Ads Calls from Website tag will be created or fired.

Google Tag Manager container GTM-M545Z8T2 is not installed on any page. The container holds
zero tags, zero triggers and zero enabled built-in variables, and has never received data.
The GTM workspace stays unpublished.

Required hidden form capture: GCLID, GBRAID, WBRAID, the approved UTM parameters, campaign,
ad group, keyword, creative, device, landing page, consent state, submission timestamp, and
a real unique non-PII lead ID when the platform can produce one. Populate click identifiers
in the browser from the live URL, never from server-rendered cached HTML, and exclude the
landing page and thank-you page from full-page caching. Keep names, email addresses, phone
numbers, ZIP codes and project notes out of URLs and analytics parameters.

Claims that must not appear on this page or in ads until verified in writing: warranty
duration, certification or dealer status, IP rating, financing, response-time promises,
installation-time promises, star ratings, review counts, and any five-star claim.
""")

print("=== LANDING PAGE DOC ===")
reqs = [
    # descending index order
    {"deleteContentRange": {"range": {"startIndex": 9314, "endIndex": 9873}}},
    {"insertText": {"location": {"index": 9314}, "text": REVIEWS_NOTE}},
    {"deleteContentRange": {"range": {"startIndex": 9294, "endIndex": 9313}}},
    {"insertText": {"location": {"index": 9294}, "text": "9. CUSTOMER REVIEWS - SECTION REMOVED"}},
]
docs.documents().batchUpdate(documentId=LANDING, body={"requests": reqs}).execute()
print("  reviews section replaced with the removal note")

end = doc_end(LANDING)
docs.documents().batchUpdate(documentId=LANDING, body={"requests": [
    {"insertText": {"location": {"index": end - 1}, "text": SETTLED_LANDING}}
]}).execute()
print("  settled implementation status appended")

# =====================================================================
# 2. STRATEGY DOC - replace AG2/AG3 with the settled structure
# =====================================================================
AG_REPLACEMENT = clean("""AG2: Permanent Christmas Lights Exact

Launch status: Built paused alongside AG1. Exact match only.

[permanent christmas lights]

Match-type decision: EXACT only. Phrase match is deliberately withheld. A seeded intent scan
of 159 keyword ideas around this term found that of the 43 terms a phrase keyword would
reach, only 14 carry a service-hiring marker, about 120 summed monthly volume, while 29
carry none, about 250 summed volume. The non-hiring terms include competing brands such as
govee, trimlight, gemstone and minleon, and research terms such as reddit, tiktok and best.
Phrase match buys roughly 5 extra clicks per season for about two thirds irrelevant reach.
Revisit only when real search-term data justifies it.

Demand evidence: 90 average monthly searches in the approved area, 480 in November 2025,
about 840 across September to December, and the only bucket in the entire research set that
returned top-of-page bid data at 4.66 to 13.76 US dollars, HIGH competition.

Ad groups that are NOT built

Permanent Holiday Light Installation is not built. The installation variant recorded 10
searches in November 2025 and zero in the other eleven months. The broader permanent holiday
lights bucket averages 10 per month and shares its volume bucket with permanent holiday
lighting. Two ad groups and four ads cannot accumulate a usable sample against roughly 40
searches across the whole September to December window. Reconsider only if November
search-term data shows real permanent holiday light queries.

EverLights Installation is not built. Both everlights installer and everlights installation
return zero average monthly searches in the approved geography, and everlights alone
averages 10 per month. There is no demand to buy. Separately, the Apogee website states that
Apogee is a certified EverLights dealer and installer, but that is first-party website
wording, not the written paid-trademark permission required for brand ad copy, and it does
not create search volume.
""")

print("\n=== STRATEGY DOC ===")
reqs = [
    {"deleteContentRange": {"range": {"startIndex": 5923, "endIndex": 6428}}},
    {"insertText": {"location": {"index": 5923}, "text": AG_REPLACEMENT}},
]
docs.documents().batchUpdate(documentId=STRATEGY, body={"requests": reqs}).execute()
print("  AG2/AG3 replaced with the settled two-ad-group structure")

SETTLED_STRATEGY = clean("""

CURRENT IMPLEMENTATION STATUS, 2026-09-17

This section records settled facts and supersedes earlier provisional wording.

Account and identifiers
Google Ads child account: Apogee Lawns LLC - Live, child customer ID 816-462-6278.
Manager account: 337-371-1342. Never mutate the manager account.
Google Ads destination: AW-18453077620. Confirmed three ways: the account conversion
tracking ID, the account global site tag snippet, and the tag snippet of conversion action
7772803337. It is never derived from the customer ID.
Google Tag Manager container: GTM-M545Z8T2, account 6377231045, container 264326944.
Scope approval: recorded 2026-09-17, approver Walter, similar-local-service.

Conversion actions, created 2026-09-17, all Secondary
Lead | Permanent Lights | Form Submit | Thank You, action 7772803337, WEBPAGE,
Submit lead form, count one, 30 day click window, no conversion value,
AW-18453077620/KOL7CImirvocEPS8jt9E. This is the only form conversion sent to Google Ads.
WhatConverts may record forms internally but must not send form conversions to Google Ads.

Call | Permanent Lights | Ads | 60s, action 7773013199, AD_CALL, Phone call lead, count one,
60 second minimum, no conversion value. No GTM tag. Calls from ads are configured in Google
Ads only.

Call | Permanent Lights | Website | 60s, action 7773043879, WEBSITE_CALL, Phone call lead,
60 second minimum, AW-18453077620/lp3jCKf5vPocEPS8jt9E. Retained, Secondary and unused.
It is excluded from every campaign goal and custom goal.

Measurement ownership
WhatConverts owns website-call measurement. No Google Ads Calls from Website tag will be
created, published or fired. The reason is that 402-526-5754 is a WhatConverts tracking
number, and the Google tag performs forwarding-number replacement on the same displayed
number that WhatConverts would swap. Two replacement systems on one number race each other
and the loser silently records nothing.

A fixed single tracking number stamps every call with one source and never binds to the
visitor session, which means calls carry no click identifier. Click-level call attribution
therefore requires a WhatConverts dynamic number pool scoped to the paid landing page, not a
single static number.

Campaign
Name: S | Website Leads | Permanent Christmas Lights | Apogee Lawns | $500 | 09_2026
Status at build: Paused. Enablement is a separate approval.
Type: Search. Network: Google Search only.
Average daily budget: 16.44 US dollars. 16.44 multiplied by 30.4 equals 499.78, which stays
under a 500 US dollar recurring monthly limit. The multiplier is 30.4, never 30.
Bidding: Maximize Clicks with an approved maximum CPC ceiling of 8.00 US dollars. The
ceiling is a delivery cap, not an expected CPC. Forecast average CPC is 4.85 US dollars,
which models a cost per lead of about 97 US dollars at a 5 percent landing-page conversion
rate against a 100 US dollar target.
Search Partners off. Display Network off. AI Max off. Campaign broad match off. Dynamic
Search Ads off. Final URL expansion off. URL inclusions off. Text customization off.
Automatically created assets off. Audiences observation only. Language English.

Schedule
The Search campaign and both forms stay eligible 24 hours a day. No ad schedule criteria are
created, because in Google Ads the absence of an ad schedule means all days and all hours.
The call asset alone is restricted to live-answer hours: Monday to Friday 08:00 to 17:00,
Saturday 08:00 to 12:00, Sunday no row. Six schedule rows in total, America/Chicago.

Locations, Presence targeting, all 14 resolved and confirmed ENABLED
Postal codes 68372, 68430, 68527, 68347, 68526, 68461, 68516, 68520.
Cities Waverly, Eagle, Lincoln and Crete, Nebraska.
Municipalities Ashland Township and Nemaha Precinct, Nebraska.
Nemaha Precinct uses geo target 9233865, whose canonical Google label is exactly
"Nemaha Precinct,Nebraska,United States". The county is not inferred and targeting is not
broadened to county level.
Omaha is excluded. Any Omaha expansion requires a separate strategy, budget, location set
and approval.
The state of Nebraska is never targeted. It is the parent of all 14 targets, not a target.

Landing page
One canonical paid page serves both ad groups:
https://apogeelawns.com/permanent-christmas-lights-lincoln-ne/
Dedicated thank-you page: https://apogeelawns.com/thank-you/permanent-christmas-lights/
Both currently return HTTP 404 and are developer work.
Duplicate pages are not created merely to influence Quality Score. Google reports Quality
Score at the keyword level and duplicate page count is not a scoring factor.

Negative keywords
75 campaign-level negatives, 37 broad and 38 phrase. None of the seven pre-existing shared
negative lists in the account are attached. The list named Christmas Lights Install contains
the phrase negative "permanent christmas lights", which would block the campaign's own head
keyword, and two General List sets contain the single-word broad negatives cost, price,
pricing, best, hire, emergency and reviews, which are deliberately kept eligible.

Reviews
Google reviews could not be verified on 2026-09-17. No star rating and no review count
appear in the Google knowledge panel. No rating claim, review-count claim, five-star claim,
Google reviews call to action or testimonial may be used in ads or on the paid landing page.

Developer responsibilities
Install GTM-M545Z8T2 sitewide including the 404 template, publish the paid landing page and
the dedicated thank-you page, build a dedicated PPC form that redirects only after a
verified server-side success and exposes a real unique non-PII lead ID, keep the PPC phone
number inside the paid funnel, add a Terms and Conditions page because none exists, and
exclude the paid pages from full-page caching.

Owner-only launch blockers
Restore billing. The account has no active billing setup and the signup screen pre-selects a
payments profile belonging to a different company, which must not be used for Apogee.
Complete advertiser verification. Google states a review time of 1 to 10 days.
Verify that 402-526-5754 routes to 402-202-7261 and is answered as described.
Supply average gross profit per sold project so acquisition cost can be judged.
""")

end = doc_end(STRATEGY)
docs.documents().batchUpdate(documentId=STRATEGY, body={"requests": [
    {"insertText": {"location": {"index": end - 1}, "text": SETTLED_STRATEGY}}
]}).execute()
print("  settled implementation status appended")

# =====================================================================
# 3. TEXT REPLACEMENTS across both docs
# =====================================================================
REPL_STRATEGY = [
    ("Maximum CPC: TBD after local Keyword Planner review and target-CPL math; $8 may be evaluated but is not approved",
     "Maximum CPC: 8.00 US dollars, approved 2026-09-17 as a controlled initial ceiling. It is a delivery cap, not an expected CPC. Forecast average CPC is 4.85 US dollars."),
    ("Ad schedule: TBD: confirmed staffed phone and form-response hours only, with Central Time documented",
     "Ad schedule: the campaign runs 24 hours a day and no ad schedule criteria are created. Only the call asset is limited to live-answer hours, Monday to Friday 08:00 to 17:00 and Saturday 08:00 to 12:00, America/Chicago."),
    ("Final URL: Dedicated PPC landing-page URL: TBD after publication and QA",
     "Final URL: https://apogeelawns.com/permanent-christmas-lights-lincoln-ne/ Currently HTTP 404 and pending developer publication."),
    ("Final URL: Dedicated PPC URL: TBD",
     "Final URL: https://apogeelawns.com/permanent-christmas-lights-lincoln-ne/"),
    ("The proposed $8 maximum CPC is an unvalidated candidate, not an approved bid. Finalize the cap from live Keyword Planner evidence and unit economics after the identity and access checks pass.",
     "The 8.00 US dollar maximum CPC was validated against live Keyword Planner evidence and unit economics and approved on 2026-09-17 as a controlled initial ceiling."),
    ("Current status: Google Ads conversion actions have not been created, and GTM-M545Z8T2 has not been proven installed on the live landing page.",
     "Current status as at 2026-09-17: all three Google Ads conversion actions have been created on child account 816-462-6278 and read back clean, and all three are Secondary. GTM-M545Z8T2 is confirmed NOT installed on the live site; the container has never received data."),
]
REPL_LANDING = [
    ("Apogee Lawns offers professional EverLights installation for homes and businesses in Lincoln and the approved surrounding service area. Reconfirm the current EverLights relationship and commercial availability before publication.",
     "Apogee Lawns installs permanent exterior lighting for homes and businesses in Lincoln and the approved surrounding service area. Do not name a manufacturer, dealer status or certification in ads or on this page until written paid-trademark permission is on file."),
]

print("\n=== TEXT REPLACEMENTS ===")
for fid, repls, label in ((STRATEGY, REPL_STRATEGY, "strategy"), (LANDING, REPL_LANDING, "landing")):
    requests = [{"replaceAllText": {"containsText": {"text": clean(a), "matchCase": True},
                                    "replaceText": clean(b)}} for a, b in repls]
    resp = docs.documents().batchUpdate(documentId=fid, body={"requests": requests}).execute()
    total = sum(r.get("replaceAllText", {}).get("occurrencesChanged", 0) for r in resp.get("replies", []))
    print(f"  {label}: {total} occurrences replaced across {len(repls)} rules")
    for (a, _b), r in zip(repls, resp.get("replies", [])):
        print(f"      {r.get('replaceAllText', {}).get('occurrencesChanged', 0)}x  {a[:70]}...")

# =====================================================================
# 4. VERIFICATION
# =====================================================================
print("\n" + "=" * 70)
print("TEXT CLEANUP VERIFICATION")
print("=" * 70)
for label, fid in (("strategy", STRATEGY), ("landing", LANDING)):
    d = docs.documents().get(documentId=fid).execute()
    full = "".join("".join(r.get("textRun", {}).get("content", "")
                           for r in el["paragraph"].get("elements", []))
                   for el in d["body"]["content"] if el.get("paragraph"))
    counts = {
        "U+2013 en dash": full.count("\u2013"),
        "U+2014 em dash": full.count("\u2014"),
        "DO NOT PUBLISH": len(re.findall(r"DO NOT PUBLISH", full)),
        "APPENDIX": len(re.findall(r"APPENDIX", full)),
        "Appendix": len(re.findall(r"Appendix", full)),
        "appendix": len(re.findall(r"appendix", full)),
        "5 Star / five star / star rating": len(re.findall(r"5 Star|five star|5-star|star rating|Google Rating", full, re.I)),
        "Read Google Reviews CTA": len(re.findall(r"Read Google Reviews", full)),
        "Reviewer:": len(re.findall(r"Reviewer:", full)),
        "Dedicated PPC URL: TBD": len(re.findall(r"Dedicated PPC URL: TBD", full)),
    }
    print(f"\n  {label} ({fid}) - {len(full)} chars")
    for k, v in counts.items():
        print(f"    {'OK ' if v == 0 else 'HIT'}  {k:<36} {v}")
print("\nDONE. Both documents edited in place; Drive IDs and version history preserved.")
