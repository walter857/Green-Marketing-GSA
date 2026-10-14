# Ambient Cooling — Package C Applied + Full Optimization Audit

**Child account:** `Ambient Cooling - Live` · `2401959466` · **Identity gate: PASS**
**Manager:** Green Marketing `3373711342` · ClickCease Client Center `2815082755` (ACTIVE, unchanged)
**Timezone:** America/New_York · **Currency:** USD · **As at** 2026-08-20 11:35 ET
**Audit phase:** `READ + DRAFT + VALIDATE-ONLY` — nothing below is executed

---

## Part 1 — Package C `C6C3DFFC9BD5AF9B` EXECUTED

Preflight 15/15 (fingerprint reproduced, identity, drift, zero pre-existing rows so no
duplicate risk). Executed as one atomic `GoogleAdsService.Mutate`, 30 operations,
`partial_failure=false`, 30 responses.

### Readback 28/28 PASS

| Verified | Result |
|---|---|
| 30 rows, 6 per campaign | ✅ |
| Mon–Fri 08:00–20:00 + Sat 08:00–13:00 on **all five** | ✅ |
| **Sunday absent** everywhere | ✅ |
| All minutes `ZERO`, all ENABLED, `negative=false` | ✅ |
| No overlapping rows | ✅ |
| Account-wide 109 → 139 (legacy untouched) | ✅ |
| Criterion mix now LANG 1 · DEV 3 · LOC 75 · **SCHED 6** | ✅ |
| **Call asset schedule identical** and unchanged, no Sunday | ✅ |
| Call asset APPROVED/REVIEWED, 5 links ENABLED+ELIGIBLE | ✅ |
| Budgets, bidding, networks, locations unchanged | ✅ |
| Ads, keywords (6,968), assets (271), conversions (16) unchanged | ✅ |
| IP blocks unchanged (2,796) · negatives still 0 | ✅ |
| Both manager links ACTIVE | ✅ |

Receipts: `receipts/packageC-mutation-2026-08-20.json`, `receipts/packageC-readback-2026-08-20.json`

---

## Part 2 — Corrected performance baseline

Reframed on **billable clicks only**, as instructed. Google-filtered invalid clicks were never
charged and are excluded from every cost figure below.

**2026-08-14 → 2026-08-20 · 1,501 impressions · 37 charged clicks · $1,796.45 · 2 conversions**

| Campaign | Impr | Charged clicks | CTR | Charged spend | CPC | Conv | CPL | IS | Rank-lost | Budget-lost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HVAC Installation | 550 | 22 | 4.00% | $725.22 | **$32.96** | 0 | — | 45.19% | 11.23% | **43.58%** |
| AC Repair | 144 | 9 | 6.25% | $612.45 | $68.05 | 1.0 | $612.45 | 25.39% | **74.61%** | 0.00% |
| HVAC Repair | 413 | 6 | **1.45%** | $458.78 | $76.46 | 1.0 | $458.78 | 28.54% | **71.46%** | 0.00% |
| HVAC Replacement | 393 | 0 | **0.00%** | $0.00 | — | 0 | — | 14.29% | **85.71%** | 0.00% |
| Gas Boiler Repair | 1 | 0 | — | $0.00 | — | 0 | — | 0.00% | 0.00% | 0.00% |

**August MTD $1,796.45 · remaining against the $13,000 maximum $11,203.55.**

> **Correction to what I told you yesterday.** I described HVAC Replacement as demand-limited on
> 5 impressions. With the reporting settled it has **393 impressions and zero clicks** — that is
> an ad problem, not a demand problem, and it changes the recommendation for that campaign from
> "nothing to do" to "replace the creative". Gas Boiler Repair remains genuinely volume-limited
> at 1 impression.

**Segmentation (billable only):** mobile 29 clicks / $1,550.80, desktop 6 / $218.58. Network is
Google Search only across the board. Locations are all `LOCATION_OF_PRESENCE` inside the intended
Maryland targets. Out-of-scope search terms took **1 click and $19.53 — 1.1% of spend**, so
targeting is not leaking.

### The $359.86 on LOCATION_EXPANSION and GET_DIRECTIONS — not waste, but not leads either

| Click type | Clicks | Charged | Primary conv | All conv |
|---|---:|---:|---:|---:|
| LOCATION_EXPANSION | 6 | $220.13 | 0 | 0 |
| GET_DIRECTIONS | 3 | $139.73 | 0 | 2 (Local actions – Directions) |

**Source identified:** an ENABLED `LOCATION_SYNC` asset set — `8620443109 "Business Profile"` —
linked at **customer level**, so it serves on all five campaigns. There is no campaign-level
location asset set.

They did produce 2 direction requests, which for a local HVAC business is a genuine local action.
But both sit in the non-biddable `GET_DIRECTIONS` goal and neither produced a call or form lead.
At $39.98 per interaction with zero leads, this is **worth watching, not cutting** — 9 clicks is
far too small a sample to justify removing a Business Profile link.

---

# P0 — Tracking, eligibility and severe spend

## P0-1 · Unverified claims running on every ad · `A21587057F5C113E`

**Current state:** three ENABLED account-level callouts, inherited by all five campaigns:
`Get Free Online Quote`, **`Licensed & Insured`**, **`Claim Your Discount`**.

**Evidence:** `client.yaml` `offer.barred_claims` lists `license_number_claim`,
`insurance_claim` and `discount_or_dollar_offer`. `verified_offers` records the only published
offer as *"Free [service] quote. No price, discount, or dollar value is published."*

**Proposed state:** remove the customer-level **links** for `89063098373` and `89063098376`.
`Get Free Online Quote` stays; the five campaign-level callouts stay.

| | |
|---|---|
| Resources | `customerAssets/89063098373~CALLOUT`, `customerAssets/89063098376~CALLOUT` |
| Counts | **0 creates · 0 updates · 2 removals** |
| Benefit | Removes two unverifiable public claims from every ad the account serves |
| Risk | **LOW** — callouts are additive; six remain. Assets are not deleted, only unlinked |
| Rollback | Re-create the two links · 2 mutations |
| Validate-only | **VALIDATE_OK**, 0 errors |

## P0-2 · Conversion double-counting · `011EA574B826F45B`

**Current state:** seven actions are Primary *and* counted, and four overlap in pairs.

| Action | Type / Category | All-time | Verdict |
|---|---|---:|---|
| `6885463625` LP Submit Lead Forms | WEBPAGE / SUBMIT_LEAD_FORM | 71 | **Keep primary** |
| `6885576934` Lp – Phone call leads | WEBSITE_CALL / PHONE_CALL_LEAD | 23 | **Keep primary** |
| `1068114183` Calls from ads | AD_CALL / PHONE_CALL_LEAD | 237 | **Keep primary** |
| `6498555481` Visit Thank you page | WEBPAGE / SUBMIT_LEAD_FORM | 3 | **Demote** — duplicates 6885463625 |
| `6498555484` Call BTN Click | WEBPAGE / CONTACT | 34 | **Demote** — duplicates 6885576934 |
| `7643656075` WC Calls | UPLOAD_CALLS | **0** | **Demote** — latent triple-count |
| `7643656486` WC Lead | UPLOAD_CLICKS | **0** | **Demote** — latent double-count |

Secondary/diagnostic actions (GA4 form_submit 37, GA4 phone_call 352, and the Google-hosted
local actions) are already correctly excluded from the conversions metric — no change needed.

**Is Google Ads receiving what bidding needs?** Not relevant today: all five campaigns run
`TARGET_SPEND` (Maximize Clicks), which ignores conversion data entirely. For any future move
to conversion bidding, no — 2 primary conversions since launch is far too little, and it must
be counting each lead once first.

**GTM and WhatConverts are kept.** Both confirmed live on all five pages. The two WhatConverts
actions stay ENABLED; only `primary_for_goal` changes, so they can be promoted the moment a
deduplication key is confirmed.

| | |
|---|---|
| Counts | **0 creates · 4 updates · 0 removals** |
| Benefit | Each lead counted once; the precondition for conversion bidding and a real target CPL |
| Risk | **LOW**, reversible. Reported conversion totals will step *down* — that is the fix working |
| Rollback | Set `primary_for_goal = true` on the same four · 4 mutations |
| Validate-only | **VALIDATE_OK**, 0 errors |

## P0-3 · Are the two conversions genuine? — unresolved, needs WhatConverts

| Date | Campaign | Action | Device | Attributed hour |
|---|---|---|---|---|
| 08-20 | HVAC Repair | LP Submit Lead Forms | Mobile | **06:00** |
| 08-20 | AC Repair | Calls from ads | Mobile | **07:00** |

Both are attributed to clicks in the 06:00–07:00 window, on mobile. The HVAC Repair conversion is
split 0.5/0.5 across a URL click and a **sitelink** click — and every sitelink currently points at
the main website (see P1-1).

**I cannot classify them from Google Ads**, which exposes no lead content. The determinative
non-PII signals — call duration and form-field coherence — are in WhatConverts profile 105803.
**One check settles both:** a sub-10-second call is not a lead.

---

# P1 — Conversion rate and Quality Score

## Quality Score, every active keyword

| Campaign | Keyword | Match | QS | Expected CTR | Ad relevance | Landing page | IS | Rank-lost | Budget-lost | CPC | CTR | Conv | CPL |
|---|---|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| AC Repair | `ac repair near me` | Phrase | **4** | Below avg | Average | Average | 25.4% | 74.6% | 0% | $61.92 | 8.2% | 1.0 | $612.45 |
| AC Repair | `ac repair near me` | Exact | **4** | Below avg | Average | Average | — | — | 0% | $117.08 | 2.2% | 0 | — |
| HVAC Repair | `hvac repair near me` | Phrase | **2** | Below avg | Average | **Below avg** | 28.5% | 71.5% | 0% | $76.46 | 1.8% | 1.0 | $458.78 |
| HVAC Repair | `hvac repair near me` | Exact | **2** | Below avg | Average | **Below avg** | — | — | 0% | — | 0% | 0 | — |
| HVAC Installation | `hvac installers` | Phrase | n/a | — | — | — | 45.2% | 11.2% | **43.6%** | $34.91 | 4.1% | 0 | — |
| HVAC Replacement | `hvac replacement near me` | Phrase+Exact | n/a | — | — | — | 14.3% | 85.7% | 0% | — | **0%** | 0 | — |
| Gas Boiler Repair | `gas boiler repair` | Phrase+Exact | n/a | — | — | — | 0% | 0% | 0% | — | — | 0 | — |

**Where the fix belongs, per campaign:**

- **AC Repair — the ad, not the bid or the page.** QS 4 with Average ad relevance and Average
  landing page, but **Below Average expected CTR**. Its two ads split 9.09% CTR versus 1.79%, so
  one is carrying the campaign. Fix: rewrite the weak ad. Budget-lost is 0% — money is not the lever.
- **HVAC Repair — the ad AND the page.** QS 2, Below Average expected CTR *and* Below Average
  landing-page experience. Both components need work: new copy (P1-2) and page changes (P1-4).
- **HVAC Replacement — the ad.** 393 impressions, 0 clicks. No QS exists because there is no
  click history. Expected CTR is the only available lever.
- **HVAC Installation — nothing structural.** Best CPC in the account at $32.96, best CTR
  trajectory, and the only campaign with real budget-lost impression share (43.58%). It is the
  one campaign where more budget would convert — but no increase is proposed this phase.
- **Gas Boiler Repair — keywords.** 1 impression. See P2-2.

## P1-1 · Sitelinks all point at the main website · `FFD4FC4647539998`

**Current state:** all 9 sitelinks on the five campaigns resolve to
`ambientcoolingandheating.com`. Sitelink clicks took **$215.98** of charged spend, and half of
one primary conversion is attributed to a sitelink click.

**Why it matters:** the main site carries the main-site number **(410) 761-0932**, which
`client.yaml` marks `MUST_NOT_APPEAR_ON_ANY_PAID_CONVERSION_PATH`. The offer subdomain carries
GTM-PQTPQ436 and WhatConverts 105803 — confirmed live by browser render today. The main site is
not the measured paid path.

**Proposed state:** five new offer-subdomain sitelink assets, one per service. Each campaign
receives the **other four** (a sitelink may not duplicate the ad's own final URL). The eight
main-site *service* sitelink links are unlinked. **Contact Ambient, Customer Reviews, Service
Areas and View Our Work stay on the main site deliberately** — no offer-subdomain equivalent exists.

| | |
|---|---|
| Counts | **25 creates (5 assets + 20 links) · 0 updates · 8 removals** = 33 mutations |
| Benefit | Sitelink clicks stay on the tracked subdomain with the approved phone architecture |
| Risk | **MEDIUM-LOW** — new assets enter review; the four main-site sitelinks remain throughout so no campaign is left without sitelinks |
| Rollback | Remove 20 new links, re-create 8 removed links · 28 mutations |
| Validate-only | **VALIDATE_OK**, 0 errors |

## P1-2 · Replacement RSAs for HVAC Repair and HVAC Replacement · `18AA929B46A83104`

Every active ad group already holds **exactly two enabled RSAs** — compliant, and the six
preserved replacements are untouched. This package **creates four new RSAs PAUSED** in the two
weakest ad groups. One direct-response and one benefit/decision ad each, 15 headlines and 4
descriptions, no pins, main keyword used naturally across multiple headlines, "Near You" instead
of awkward "near me".

**Policy discipline:** no finance language of any kind (the original disapproval was
`CONSUMER_FINANCE`); no price, discount, response-time, same-day/emergency, years-in-business,
licence, insurance, rating, guarantee or certification claim. Only the verified free-quote offer
and the verified service area.

**RSA limit:** paused RSAs do not count. HVAC Repair goes 2 enabled + 2 paused; HVAC Replacement
2 enabled + 4 paused. Enabling them later would exceed 3 enabled per ad group unless the current
pair is paused in the **same atomic request** — a separate package with its own fingerprint,
exactly as the 2026-08-18 swap required.

| | |
|---|---|
| Counts | **4 creates · 0 updates · 0 removals** |
| Benefit | Expected CTR is the QS component copy can move, and both campaigns are rank-limited |
| Risk | **LOW** while paused — nothing serves until a separate enablement approval |
| Rollback | Remove the 4 created ad IDs · 4 mutations |
| Validate-only | **VALIDATE_OK**, 0 errors (all 60 headlines ≤30, all 16 descriptions ≤90, paths ≤15) |

## P1-3 · Landing pages — website work, no Google Ads mutation

Real-browser audit, mobile viewport, all five pages. **Speed is not a problem:** TTFB 104–108 ms,
FCP 328–420 ms, load 1.8–2.1 s. H1 matches the service on **all five**. GTM and WhatConverts live
on all five. `gclid`, `_gcl_aw` and the four `wc_` cookies all captured.

Defects, in priority order — **HVAC Repair first**, since Google rates its landing-page
experience Below Average:

1. **No privacy policy or terms link on any page.** Google's lead-form policy expects a privacy
   policy on pages collecting personal data. Most likely single contributor to the Below Average
   rating. **Fix first.**
2. **Three Gravity Forms per page all carrying DOM id `gform_1`.** Duplicate ids break GTM form
   triggers and accessibility, and make submissions ambiguous to tracking.
3. **The form posts no click identifier.** The only hidden fields are
   `gform_source_page_number_1`. No `gclid`, `gbraid`, `wbraid` or UTM hidden field, so the CRM
   receives the lead without the click ID. WhatConverts captures them in cookies, but the form
   post does not. **This is the biggest measurement gap in the account.**
4. **`tel:` href formatting.** `tel:4107056354` (no country code) and `tel:(410) 705-6354`
   (unencoded parentheses and space). Should be `tel:+14107056354`. The third number
   `+14109141456` is the WhatConverts DNI pool number and is **correct, not a defect**.

Above-the-fold CTAs are present and correctly sized on mobile (Call 142×29 at top 41, Free Quote
visible). Form is 5 fields, 4 required — reasonable for HVAC lead capture.

---

# P2 — Expansion and cleanup

## P2-1 · Orphaned ad group inside the AC Repair campaign

Ad group `202339087874` "SKAG | HVAC Replacement Near Me" sits inside the **AC Repair** campaign,
is REMOVED, yet still holds 2 non-removed keywords and **2 ENABLED ads carrying
`AREA_OF_INTEREST_ONLY` and a CONSUMER_FINANCE policy topic**. Nothing serves. Recommend removing
the two ads to clear the residual policy flag. **Not packaged** — removals are destructive and
need their own approval; no delivery benefit, cosmetic only.

## P2-2 · Keyword expansion, researched not applied

Historical volume, 10 core service-area cities, Google Search, English:

| Theme | Avg monthly | Competition | Note |
|---|---:|---|---|
| `ac repair near me` (live) | 260 | HIGH (74) | best keyword in the account |
| `hvac repair near me` (live) | 70 | HIGH (79) | |
| **`boiler repair`** | **30** | LOW (15) | **3× the live `gas boiler repair`** |
| **`ac replacement`** | **30** | MEDIUM (34) | |
| **`hvac replacement`** | **20** | MEDIUM (51) | **2× the live term, and far less competitive** |
| `furnace replacement` | 20 | LOW (14) | |
| `gas boiler repair` (live) | 10 | LOW (0) | |
| `hvac replacement near me` (live) | 10 | **HIGH (100)** | most competitive term in the set |
| residential/emergency/near-me boiler variants | 10 each | LOW | |

Two evidence-backed opportunities, **both requiring their own approval package**:

- **HVAC Replacement:** the live keyword `hvac replacement near me` has 10 searches at competition
  index **100**. Dropping "near me" gives `hvac replacement` at 20 searches and index **51** —
  double the volume at roughly half the competition. Still Phrase + Exact, still BOFU.
- **Gas Boiler Repair:** a tightly themed second ad group on `boiler repair` (30/mo, LOW) with
  Phrase + Exact, two RSAs and the existing `/gas-boiler-repair/` page would triple its
  addressable volume. Honest framing: 30 searches a month is still very small, and this will not
  move the account's total materially.

## P2-3 · Negatives — nothing to add

Zero campaign negatives, zero ad-group negatives, no negative list attached to the five. The
account-level list `11252984411` (59 BROAD members, applies account-wide, invisible in
`campaign_shared_set`) was tested against **all five active keywords: zero conflicts**.
Out-of-scope charged terms took 1 click and $19.53. **No negative package is warranted** —
adding negatives here would be activity without benefit.

## P2-4 · Assets

Call asset, callouts and structured snippets are in good order: one call asset on the approved
number with the correct schedule; five campaign-level callouts that are specific,
non-duplicative and consistent with verified facts; five service-specific structured snippets,
one per campaign, correctly themed. Only the two account-level callouts in P0-1 are a problem.

---

# P8 · Budget and bidding — no change proposed

Packages B v1 (`EF9FBA55926545F2`) and B-v2 (`93A1EA55973F7A94`) remain **VOID**.

- All five budgets unchanged: $141.45 / $78.95 / $138.16 / $26.32 / $42.76 = **$427.64/day**.
- $13,000 is treated as a **maximum, not a target**. MTD $1,796.45.
- Underspending is the correct outcome while four of five campaigns are rank-, quality- or
  volume-limited.
- No Broad Match, no location widening, no Search Partners, no bid inflation proposed.
- **No move to Maximize Conversions** — 2 primary conversions is nowhere near enough, and P0-2
  must land first so the data counts each lead once.
- **No CPC cap proposed.** A cap needs a confirmed target CPL, and `target_cpl`, `target_cpqL`,
  `target_cac`, `average_job_revenue`, `gross_margin_pct` and `close_rate_pct` are all null in
  `client.yaml`. I will not invent one. The historical Search conversion rate (5.47% trailing
  year) is available the moment you supply a target CPL.
- **Pacing recalculation is due after 24 hours under the restored schedule**, i.e. from
  2026-08-21 11:35 ET. Only one full day of post-schedule data will exist before then.

---

## Approval summary

| Priority | Package | Fingerprint | Creates | Updates | Removals | Validate |
|---|---|---|---:|---:|---:|---|
| **P0** | Remove unverified account callouts | `A21587057F5C113E` | 0 | 0 | 2 | ✅ OK |
| **P0** | Conversion de-duplication | `011EA574B826F45B` | 0 | 4 | 0 | ✅ OK |
| **P1** | Sitelinks to offer subdomain | `FFD4FC4647539998` | 25 | 0 | 8 | ✅ OK |
| **P1** | Replacement RSAs (created PAUSED) | `18AA929B46A83104` | 4 | 0 | 0 | ✅ OK |

Recommended order: **P0-1 and P0-2 first** (compliance and measurement integrity, 6 mutations
total, both trivially reversible), then **P1-1**, then **P1-2**. Landing-page work (P1-3) runs in
parallel on the website and needs no Google Ads change.

Nothing is executed. Each package needs its own explicit approval:

```
APPROVE A21587057F5C113E FOR 2401959466
APPROVE 011EA574B826F45B FOR 2401959466
APPROVE FFD4FC4647539998 FOR 2401959466
APPROVE 18AA929B46A83104 FOR 2401959466
```
