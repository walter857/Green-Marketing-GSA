**Ambient Cooling — conversion reconciliation and final package set, 2026-09-09 (third pass)**

Read-only run on customer 2401959466. Identity gate passed on six fields; both manager links
ACTIVE. Nothing was changed in Google Ads, the website, GTM, WhatConverts, ClickCease or any CRM.
No IP exclusion, network, device, schedule or location was touched.

**Reconciled:** total Primary conversions are 14 and total All conversions are 75. They are
separate columns and are not added together. Calls from ads 5, LP Submit Lead Forms 5, WC Lead 4.
All three figures proven from daily rows segmented by date, campaign and conversion action.

**Retracted:** the finding that WC Lead recorded zero Primary conversions after 2026-08-21. Two
later rows carry Primary values — 2026-08-28 (1.00) and 2026-09-01 (2.00). The real split is 4 of
8 WC Lead records reaching the Primary column, per record, not by date.

**Corrected:** the HVAC Installation post-swap CPA of $141.87 divided visible search-term cost
($425.60) by campaign-level conversions (3) — two different measurement grains. The correct
campaign-level raw CPA is $161.33.

**Flagged:** all three Installation Primary records landed on 2026-09-01, a day with three clicks.
The landing-page form action and the WhatConverts upload both counted, which is the signature of
one interaction recorded twice. The unique lead count is between 1 and 3. If it is 1, cost per
unique lead is $483.98 against a $280 target. This cannot be resolved from the Google Ads API.

**Rebuilt:** the budget analysis campaign by campaign. Each campaign carries its own monthly
limit, so the September maximum is the sum of per-campaign maxima ($10,216.12), not account
spend-to-date plus a combined formula. Steady state moves from $14,155.15 to $12,815.12 against
the $13,000 cap. A blind rollback is now blocked: Gas Boiler plus HVAC Replacement must stay at or
below $31.08 a day combined.

**Proven:** Savage, Maryland is an ENABLED positive location target on all five campaigns, so the
PHRASE negative blocking it can be removed. Proven separately: no duplicate "commercial" negative
exists on any of the five live campaigns, so removing the single account-level entry is enough.

**Could not prove:** that "licensed" is supported advertising language. It appears in zero live
ads, zero callouts and zero of the five landing pages. The only adjacent phrase anywhere is
"CERTIFIED SERVICE TECHNICIAN" in the main-site footer. Those five removals are held pending a
claim-substantiation answer.

**Held on evidence:** the five "free" removals. Exactly one search-term row containing "free" has
ever been observed — "hvac repair free estimate near me", 6 impressions, 0 clicks, $0.00 — and no
"free" query has ever converted account-wide.

**Investigated:** invalid clicks, read-only, one segmentation dimension at a time. 1,773 invalid
clicks against 175 billable in the settled window. 1,706 of them, 96.2%, sit on the
LOCATION_EXPANSION click type at a 98.05% invalid rate, concentrated on mobile. These are clicks
Google filtered before billing, so they are not unbilled spend. They are not evidence about
ClickCease: all 2,796 ClickCease IP exclusions sit on legacy campaigns and none is attached to the
five live campaigns. No ClickCease attribution is claimed.

**Delivered:** five new validated packages totalling 12 operations, plus the carried-forward
two-operation ad cleanup, for 14 operations in the approval block. Four earlier fingerprints
marked superseded with a preserved audit trail.

**Not measured:** qualified leads, CPQL, sold jobs, revenue and gross profit. The WhatConverts API
token is empty. No conversion record in this account is described as a qualified lead, and no
savings or performance improvement is claimed.
