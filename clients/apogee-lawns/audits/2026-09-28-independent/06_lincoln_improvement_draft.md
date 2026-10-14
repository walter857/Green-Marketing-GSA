# 06 — Lincoln improvement draft (local only)

## Conclusion on keywords and structure

**No keyword or ad-group addition is justified today** (evidence in `04_keyword_and_forecast_scenarios.md`):

- Explicit buyer and local variants forecast 1.2 clicks on their own for 83 days.
- Holiday-installation synonyms carry no measurable demand.
- EverLights forecasts 0.
- The only material increments come from Phrase reach into mixed product and research queries.

Because no new ad group is proposed, no new RSAs are drafted. The existing four RSAs use only verified claims, carry
justified Headline-1 pins and point at the correct page, and nothing in the data (31 and 34 impressions per ad group)
justifies rewriting them.

What *is* drafted:

## A. IMPLEMENTATION-READY — `APG-0928-DEV-T` (restore tablet eligibility)

File: `clients/apogee-lawns/plans/APG-0928-DEV-T.yaml` · **fingerprint `46060B03F5C9`** (re-verified by the package
validator).

| Object | Resource | Before → after | Condition |
|---|---|---|---|
| 1 | `customers/8164626278/campaignCriteria/24257151015~30002` (DEVICE TABLET), mask `bid_modifier` | 0.0 (−100%) → 1.0 (no adjustment) | always |
| 2 | `adGroupBidModifiers/200347713516~30002`, mask `bid_modifier` | 0.0 → 1.0 | only if the post-object-1 readback still shows an explicit 0.0 |
| 3 | `adGroupBidModifiers/200347713556~30002`, mask `bid_modifier` | 0.0 → 1.0 | same |

Creates 0 · updates 1–3 · removes 0 · status, budget, bid strategy, CPC limit, geo and keyword changes 0.

- **Why:** tablets have been excluded since the 09-25 web-interface edit, with no recorded reason. Before that they were
  1 of 20 impressions.
- **Expected effect:** small; this is hygiene, not a volume fix.
- **Reject it if the exclusion was deliberate** for a reason not on file.
- **Rollback:** the same fields back to 0.0.

## B. GATED DRAFT (not fingerprinted) — `APG-0928-KW-P`: head-term Phrase test

- **Change:** add PHRASE `permanent christmas lights` to ad group **200347713556** `AG | Permanent Christmas Lights Exact`.
  Its two RSAs (825023783013, 825023783016) already lead with "Permanent Christmas Lights"; reuse them, and add no new
  ads. Add campaign negatives on 24257151015:
  - PHRASE `reddit`
  - PHRASE `tiktok`
  - PHRASE `semi permanent`
  - PHRASE `dude dad`
  - BROAD `minleon` (a competing system)

  None of these contains a protected buyer term, and none blocks a live positive (checked by the package validator).
  "best", "cost", "price" and "near me" stay eligible.
- **Gate — all three must hold before this becomes a fingerprinted plan:**
  1. The form conversion is verified end to end (the developer handoff plus the approved Preview test). Without it, the
     test's lead quality cannot be judged.
  2. The date is 2026-10-15 or later, when the head family ramps (Oct 140 → Nov 480).
  3. A fresh search-term read shows the Exact keyword's queries still reach at least one buyer- or local-marked term per
     week.
- **Forecast:** +8.0 clicks, +$55.21 across Sep 29–Dec 20 (≈$6.90 per extra click). This comes from the forecast tool,
  which cannot model the new negatives, so treat it as a ceiling.
- **Stop rule:** after $40 of Phrase-attributed spend, pause the Phrase keyword if more than half of its cost comes from
  queries with no buyer or local marker and there is no qualified lead.
- **Owner approval needed:** none beyond the normal plan approval. This is a match-type decision inside policy.

## C. CONDITIONAL — `APG-0928-NEG-H` (negative hygiene; low priority)

- **Candidates for removal** (only if search terms ever show 'permanent' + seasonal-wording buyers):
  - PHRASE `christmas light hanging service` (criterion 13815997505)
  - PHRASE `seasonal light installation` (2356007674300)
  - PHRASE `take down christmas lights` (1733687419372)
- **Decided by owner answer:** `labor only`, `customer supplied`, `my own lights`. Keep them if Apogee does not install
  customer-supplied lights; remove them if it does.

## Budget within the fixed $500 per month (unchanged)

| Item | Value |
|---|---|
| Daily budget (live) | $16.44 → monthly charging limit $16.44 × 30.4 = **$499.78** (≤ $500) |
| September spent to date | $18.69 (Sep 25 $5.52, Sep 27 $13.17) |
| Maximum on any single day | about 2 × daily = $32.88; the month stays capped by the 30.4-day rule |
| Forecast spend Sep 29–Dec 20 | $266.57 in total, ≈ $3.21 a day, roughly $97 per 30.4 days on average; November will run higher |
| Recommendation | **No budget change.** The forecast shows no budget sensitivity at $10 or $25. The live budget-lost IS (18.5%, mechanism unverified) is re-checked in the October review before anything is proposed. Any increase above $16.44 would exceed the approved total and needs a separately labelled exception |

A second campaign is not recommended, so the shared-versus-allocated budget comparison applies only to the conditional
Omaha brief.

## Economics (owner planning assumptions of 2026-09-16 — not Apogee history)

| Metric | Value | Status |
|---|---|---|
| Spend to date | $18.69 | measured |
| Leads from ads | 0 | Google Ads 0 conversions; WhatConverts 0 leads with GCLID or google/cpc; form tag cannot fire, so the Ads figure is not reliable on its own |
| Qualified leads, sold jobs, revenue, gross profit | 0 / 0 / unknown / unknown | no CRM stage mapping; **gross profit per sold job not supplied** |
| CPL, CPQL, CAC, ROAS, gross-profit ROAS | not computable | zero denominators; no revenue |
| Profit after ad spend (measured) | −$18.69 against unmeasured gross profit | incomplete |
| Planning bar | target CPL $100 (acceptable $90–125); 5% click-to-lead; 20% lead-to-sale; ⇒ affordable CPC ≈ $5.00 and about $500 of ads per sale | assumptions, not forecasts |

Using those assumptions only as a sanity check, the $12 cap's extra clicks at about $19.55 each imply roughly $390 per
extra lead, well outside the bar. That is why the cap stays at $8. No lead, sale or revenue projection is made from
forecast clicks.
