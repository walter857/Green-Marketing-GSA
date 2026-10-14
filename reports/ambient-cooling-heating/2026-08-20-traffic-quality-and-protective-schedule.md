# Ambient Cooling — Traffic-Quality Investigation + Protective Schedule Package

**Child account:** `Ambient Cooling - Live` · **ID** `240-195-9466` (`2401959466`)
**Manager:** `Green Marketing` `3373711342` · ClickCease Client Center `2815082755` (ACTIVE, untouched)
**Timezone:** America/New_York · **Currency:** USD · **Identity gate: PASS**
**Phase:** `READ + DRAFT + VALIDATE-ONLY` — no mutation performed

---

## 0. Voided

| Fingerprint | Status |
|---|---|
| `EF9FBA55926545F2` | Package B v1 — **REJECTED, VOID** |
| `93A1EA55973F7A94` | Package B-v2 staged increase — **WITHDRAWN, VOID** |

Both plan files on disk are now stamped `VOID: true` with the reason. **No budget increase is
proposed anywhere in this document.**

---

## 1. The two root causes

### ClickCease is not protecting the five campaigns — in two independent ways

**(a) Zero IP exclusions have ever reached them.**

ClickCease has pushed **2,796 IP exclusions** into this account. Every one sits on a **legacy
campaign that is PAUSED or REMOVED**. The five live campaigns carry **zero**.

| Campaign group | Campaigns | IP exclusions |
|---|---:|---:|
| Legacy (all PAUSED / REMOVED) | 18 | **2,796** (137–199 each) |
| **The five live campaigns** | 5 | **0** |

Capacity used on the five: **0 of 2,500** (Google's limit is 500 per campaign). ClickCease's
IP-block sync is still pointed at the old campaign set and was never extended to the campaigns
launched 2026-08-14.

**(b) The ClickCease JavaScript tag is absent from all five landing pages.**

Verified by real-browser render (Playwright, mobile viewport, JS executing — these pages sit
behind SG-Captcha and a plain fetch gives false negatives):

| Page | HTTP | Bytes | ClickCease | GTM | WhatConverts |
|---|---|---|---|---|---|
| /ac-repair/ | 202 | 190,424 | ❌ **absent** | ✅ | ✅ |
| /hvac-repair/ | 202 | 161,461 | ❌ **absent** | ✅ | ✅ |
| /hvac-installation/ | 202 | 160,025 | ❌ **absent** | ✅ | ✅ |
| /hvac-replacement/ | 202 | 193,465 | ❌ **absent** | ✅ | ✅ |
| /gas-boiler-repair/ | 202 | 193,018 | ❌ **absent** | ✅ | ✅ |

Zero ClickCease script tags and zero ClickCease network requests on any page. GTM and
WhatConverts both present, which confirms the render was genuine.

**What IS working:** the account-level tracking template. `monitor.clickcease.com` with account
id `Y6qzID4E9cPYCj`, `ccpturl=offer.ambientcoolingandheating.com`, all six ValueTrack parameters
present, auto-tagging **on**, and **no campaign-level template override** on any of the five. So
ClickCease sees the clicks arrive — but without the page tag it cannot fingerprint the visitor,
and without the IP sync it blocks nothing on these campaigns.

That is a complete explanation for the next section.

### The result: 92.5% of click attempts are invalid

| Campaign | Charged clicks | Filtered invalid | Invalid % | Charged spend | Charged CPC |
|---|---:|---:|---:|---:|---:|
| HVAC Installation | 20 | 21 | 51.2% | $698.15 | $34.91 |
| AC Repair | 9 | 212 | **95.9%** | $612.45 | $68.05 |
| HVAC Repair | 6 | 181 | **96.8%** | $458.78 | $76.46 |
| HVAC Replacement | 0 | 18 | 100% | $0.00 | — |
| Gas Boiler Repair | 0 | 0 | — | $0.00 | — |
| **Total** | **35** | **432** | **92.5%** | **$1,769.38** | **$50.55** |

Against a **27.9% baseline** across this account's prior 12 months (17,118 valid / 6,616 invalid)
— on the legacy campaigns that *do* carry ClickCease IP blocks.

> Filtered invalid clicks are clicks Google detected and **did not bill**. They are reported
> separately throughout and are never counted as charged spend.

---

## 2. Segmentation of charged clicks and spend

### By hour — the overnight block

| Window | Impressions | Charged clicks | Charged spend | Charged CPC |
|---|---:|---:|---:|---:|
| **00:00–07:59** | 105 (9.9%) | 6 | **$567.61 (32.1%)** | **$94.60** |
| 08:00–23:59 | 951 (90.1%) | 29 | $1,201.77 | $41.44 |

**One tenth of the impressions, one third of the money, at 2.3× the cost per click.**

Worst hours: **06:00 — $335.45 at $111.82/click**; **07:00 — $181.79 for a single click**.
(15:00 also shows $117.08 for one click.) Hours 19:00–23:59 produced 76 impressions and **$0.00**.

### By device

| Device | Impressions | Charged clicks | Filtered invalid | Invalid % | Charged spend | CPC |
|---|---:|---:|---:|---:|---:|---:|
| **Mobile** | 627 | 29 | 418 | **93.5%** | **$1,550.80** | $53.48 |
| Desktop | 427 | 6 | 14 | 70.0% | $218.58 | $36.43 |

Mobile carries 87.6% of charged spend and effectively all of the invalid traffic.

### By click type — 20% of spend never reaches the landing page

| Click type | Charged clicks | Charged spend |
|---|---:|---:|
| URL_CLICKS | 21 | $944.69 |
| CALLS | 3 | $261.35 |
| SITELINKS | 3 | $215.98 |
| **LOCATION_EXPANSION** | 5 | **$207.63** |
| **GET_DIRECTIONS** | 3 | **$139.73** |

$347.36 (19.6%) went to location-expansion and get-directions interactions rather than a landing
page visit. Worth a separate look later; not actioned here.

### By keyword

| Keyword | Campaign | Impr | Charged clicks | Spend | CPC |
|---|---|---:|---:|---:|---:|
| `hvac installers` PHRASE | HVAC Installation | 482 | 20 | $698.15 | **$34.91** |
| `ac repair near me` PHRASE | AC Repair | 98 | 8 | $495.37 | $61.92 |
| `hvac repair near me` PHRASE | HVAC Repair | 329 | 6 | $458.78 | $76.46 |
| `ac repair near me` EXACT | AC Repair | 45 | 1 | $117.08 | **$117.08** |
| `hvac repair near me` EXACT | HVAC Repair | 84 | 0 | $0.00 | — |
| `hvac replacement near me` (orphaned in AC Repair) | AC Repair | 17 | 0 | $0.00 | — |
| `gas boiler repair` PHRASE + EXACT | Gas Boiler Repair | 1 | 0 | $0.00 | — |

### By search term — aggregates only

236 rows classified on disk against a positive HVAC whitelist; no raw query string entered the
analysis. Raw file `exports/search-terms-2026-08-20-RAW.jsonl`, sha256 `0f74841b70641014`.

Out-of-scope terms took **1 charged click and $19.53 of $1,769.38 (1.1%)** across all five
campaigns. **Keyword targeting is not the leak.** The waste is invalid clicks on in-scope terms.

### By location

Charged spend is spread across the intended Maryland targets, all `LOCATION_OF_PRESENCE`, top
three at $378.80 / $298.87 / $182.40. No out-of-area concentration.

---

## 3. Are the two conversions real?

Three conversion events exist since launch — one more than I reported earlier:

| Date | Campaign | Action | Category | Device | Attributed hour |
|---|---|---|---|---|---|
| 08-17 | HVAC Repair | Local actions – Directions | GET_DIRECTIONS | Mobile | — (not a primary conversion) |
| **08-20** | **HVAC Repair** | Ambient Cooling – LP Submit Lead Forms | SUBMIT_LEAD_FORM | Mobile | **06:00** |
| **08-20** | **AC Repair** | Calls from ads | PHONE_CALL_LEAD | Mobile | **07:00** |

**Both primary conversions are attributed to clicks in the 06:00 and 07:00 hours — precisely the
two worst fraud hours — on mobile, the device running a 93.5% invalid rate.**

That is strong circumstantial reason to doubt both. **I cannot classify them definitively.**
Google Ads exposes no lead content, and the determinative non-PII signals — form field pattern,
time-on-page, call duration, call recording/transcript — live in **WhatConverts profile 105803**
and the CRM, which I have no access to. Both actions are `ONE_PER_CLICK` with a 30-day lookback.

**Recommended check on your side:** in WhatConverts, pull the two leads from 2026-08-20 and look
at call duration (a sub-10-second call is almost certainly not a lead) and whether the form
fields contain coherent human input. That single check settles it.

---

## 4. Pacing snapshot (no action proposed)

August MTD for the five: **$1,785.88** as of 10:03 on 08-20 — already past the $1,712.19
guardrail line, with no budget increase applied. Daily trend: $69.50 → $331.99 → $609.06 →
$752.65. All five budgets remain untouched at $141.45 / $78.95 / $138.16 / $26.32 / $42.76.

---

# Package C — Protective campaign schedule

### `PLAN FINGERPRINT: C6C3DFFC9BD5AF9B`

`clients/ambient-cooling-heating/plans/protective-campaign-schedule-package-2026-08-20.json`

**30 mutations: 30 creates · 0 updates · 0 removals.** One atomic `GoogleAdsService.Mutate`,
`partial_failure=false`.

Six non-overlapping `AD_SCHEDULE` rows per campaign × 5 campaigns:

| Day | Hours (America/New_York) |
|---|---|
| Monday – Friday | 08:00 – 20:00 |
| Saturday | 08:00 – 13:00 |
| **Sunday** | **no row — no delivery** |

No UTC conversion anywhere; the account timezone handles EST/EDT. `bid_modifier` deliberately
not set — Maximize Clicks ignores ad-schedule bid modifiers, so setting one would be inert.

| | Before | After |
|---|---|---|
| Eligible hours/week | 168 (100%) | **65 (38.7%)** |
| Criteria per campaign | LANG 1 · DEV 3 · LOC 75 · **SCHED 0** | LANG 1 · DEV 3 · LOC 75 · **SCHED 6** |
| Account-wide AD_SCHEDULE | 109 | 139 |

**Call asset: 0 operations.** `407995613637` already carries exactly Mon–Fri 08:00–20:00 and
Sat 08:00–13:00 with no Sunday row, and cleared review this morning (APPROVED / REVIEWED, all
five links ELIGIBLE). Campaign and call-asset hours will match exactly.

**Stays 24/7:** website, all five landing pages, Gravity Forms, GTM-PQTPQ436, WhatConverts, and
the landing-page phone button. Only paid campaign delivery is restricted.

**Not changed:** budgets, bidding, bids, keywords, negatives, RSAs, call asset, conversions,
locations, assets, ClickCease access, and all 18 legacy campaigns with their 109 schedule
criteria and 2,796 IP exclusions.

**Validate-only:** preflight **16/16**, `VALIDATE_OK` on the exact 30 operations, 0 errors,
post-probe confirms the five still carry zero criteria.

**Rollback:** remove the 30 criteria by returned resource name — one atomic request, returns to
24/7, no data loss.

### Honest scope limit

This closes the worst window — 00:00–07:59 carried 32.1% of charged spend on 9.9% of impressions.
It does **not** restore click-fraud protection. Daytime still ran a $41.44 charged CPC and mobile
still shows 93.5% invalid. **The schedule buys time; the ClickCease fix is the actual remedy.**
It also does not guarantee a proportional spend drop — Maximize Clicks may redistribute into the
remaining open hours.

---

## 5. For you to check in the ClickCease console

I stayed read-only on ClickCease as agreed, and **added no IP exclusions in Google Ads** —
ClickCease must manage its own.

| Item | Google Ads API can see | Status |
|---|---|---|
| Correct Google Ads account connected | ✅ | Manager link `2815082755` **ACTIVE** on `2401959466` |
| Tracking template active | ✅ | **Yes** — `monitor.clickcease.com`, id `Y6qzID4E9cPYCj`, all ValueTrack params, no campaign override |
| Auto-tagging active | ✅ | **Yes** |
| Tracking code on the five landing pages | ✅ (browser) | ❌ **ABSENT on all five** |
| IP exclusions synced to the five campaigns | ✅ | ❌ **ZERO** (2,796 exist, all on legacy) |
| Automatic IP blocking enabled | ❌ console only | **please confirm** |
| Blocking threshold and duration | ❌ console only | **please confirm** |
| Recent blocked-click report | ❌ console only | **please confirm** |
| Sync status with Google Ads | ❌ console only | **please confirm** — the zero-exclusion finding suggests it is not syncing to the new campaigns |

The two questions that matter most: **is the new campaign set included in ClickCease's protected
scope**, and **why is the page tag missing from the offer subdomain** (the main site may carry it
while `offer.` does not).

---

## Receipts

| File | Contents |
|---|---|
| `snapshots/schedule-package-preflight-2026-08-20.json` | 16 gates + validate-only |
| `snapshots/traffic-quality-investigation-2026-08-20.json` | Full segmentation |
| `snapshots/traffic-quality-2026-08-20.json` | Invalid-click finding + pacing |
| `snapshots/clickcease-landing-pages-2026-08-20.json` | Real-browser page audit |
| `exports/search-terms-2026-08-20-RAW.jsonl` | Raw terms, on disk only |
| `plans/protective-campaign-schedule-package-2026-08-20.json` | Package C · `C6C3DFFC9BD5AF9B` |

## Required next input

```
APPROVE PACKAGE C C6C3DFFC9BD5AF9B FOR 2401959466
```

After it is applied I will run the 24-hour comparison — daytime spend, CPC, invalid-click rate,
conversions and qualified leads — before any budget proposal.
