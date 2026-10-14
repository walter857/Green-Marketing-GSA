**Ambient Cooling — BOFU search-term and CPC audit, 2026-09-09**

Completed a full read-only audit of the five live Search campaigns (customer 2401959466).
Identity gate passed; no live changes were made.

**Measured:** CPC bid ceilings were set in the Google Ads UI on 2026-09-04 (AC Repair $25,
HVAC Repair $25, HVAC Installation $30). Delivery in the four settled days after
(2026-09-05 → 09-08) was 2 clicks and $45.08, against 172 clicks and $8,025.18 in the 21 days
before. Primary conversions went from 14 to 0.

**Measured:** of 952 visible search-term rows, 419 (44%) are already blocked by the existing
6,160 campaign negatives and 452 (47.5%) are legitimate HVAC intent. Two rows worth $20.44
qualified as new negative candidates.

**Measured:** 88 live negatives collide with protected demand. 33 distinct terms block
supported manufacturers or confirmed Ambient services — 22 at campaign level and 18 at the
account level, with 7 present at both. The account-level ones cannot be overridden by a
campaign-level rule. One PHRASE negative blocks Savage, Maryland, a live location target,
across all five campaigns.

**Measured:** search terms naming other states are query text, not user location. 100% of
impressions and clicks came from users physically inside the targeted Maryland locations
(185 of 185 `user_location_view` rows in-target). No budget went out of state.

**Measured:** the removed keyword `hvac installers` cost $2,430.35 over 102 clicks with zero
primary conversions — 30% of all account spend — and produced 53.6% of the search-term rows.

**Verified:** the 79 competitor keywords added on 2026-08-31 were removed on 2026-09-01 and
cost $44.18 in total. No remediation is needed.

**Delivered:** six validated, fingerprinted change packages (119 operations) awaiting approval,
plus a landing-page and conversion-tracking defect list.

**Not measured:** lead quality, CPQL, sold jobs, revenue and gross profit. The WhatConverts API
token is empty. No savings or lead-quality improvement is claimed.
