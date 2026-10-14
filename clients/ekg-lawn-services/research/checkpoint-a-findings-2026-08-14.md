# EKG Lawn Services — Checkpoint A findings

Date: 2026-08-14 · Read-only. No Google Ads or Drive resource was created, changed, paused,
or enabled.

## 1. Verified account identity

| Field | Required | Observed | Result |
|---|---|---|---|
| Account name | `EKG Lawn Services - Live` | `EKG Lawn Services - Live` | exact match |
| Child customer ID | `7478932848` | `7478932848` | exact match |
| Client, not manager | true | `manager = False` | pass |
| Not a test account | true | `test_account = False` | pass |
| Account status | — | `ENABLED` | recorded |
| Currency | — | `USD` | recorded |
| Time zone | — | `America/New_York` | recorded |
| Manager link | configured MCC `3373711342` | ACTIVE | pass |

Auto-tagging is ON. A conversion-tracking ID is set (`10906176325`) and tracking is
`CONVERSION_TRACKING_MANAGED_BY_SELF` with the conversion customer pointing at this same
account.

**Observation:** a **second** manager link is also ACTIVE on this account alongside the
Green Marketing MCC. Another party retains management access. Recorded, not acted on.

## 2. Historical data coverage

Yearly windows walking backwards from 2026-08-14. Every query isolated.

| Window | Rows | Cost | Impressions | Clicks | Conversions |
|---|---:|---:|---:|---:|---:|
| 2025-08-15 → 2026-08-14 | 521 | $7,129.37 | 237,097 | 2,126 | 69.0 |
| 2024-08-15 → 2025-08-14 | 400 | $9,720.94 | 34,826 | 1,476 | 79.5 |
| 2023-08-16 → 2024-08-14 | 312 | $13,159.58 | 11,426 | 611 | 97.0 |
| 2022-08-16 → 2023-08-15 | 362 | $4,484.32 | 75,370 | 1,306 | 95.0 |
| 2021-08-16 → 2022-08-15 | 59 | $921.38 | 7,096 | 340 | 5.0 |
| 2020-08-16 → 2021-08-15 | 0 | $0.00 | 0 | 0 | 0.0 |

- **Earliest date with data: 2022-05-24.** Latest: 2026-08-14.
- The empty 2020–2021 window bounds the history: the account has no delivery before
  2022-05-24, so this **is** the complete available record, not a truncation.
- Total lifetime cost across windows: **$35,415.59**, 2,126+1,476+611+1,306+340 = 5,859
  clicks, 345.5 conversions.
- 23 queries executed, **0 read errors** in the final snapshot.

### Limitations
- `campaign.start_date` / `campaign.end_date` are **not recognized fields** in Google Ads
  API v25, so campaign start and end dates are unavailable through this path.
- Search-term rows reflect only queries Google exposes. Terms below Google's privacy
  threshold are never returned, so low-volume demand is systematically under-counted. The
  2,465 `INSUFFICIENT_DATA` terms are the visible edge of that, not the whole of it.
- Impression-share metrics were not selected in this pass.
- No WhatConverts, CRM, or call-tracking API access is configured in this repository, so
  offline lead quality could not be reconciled. Two upload-based actions (`WC calls`,
  `WC Leads`) show WhatConverts is feeding the account, but its own data is not readable
  from here.

## 3. Current campaign inventory — 10 campaigns

| Status | ID | Name | Type | Bidding |
|---|---|---|---|---|
| **ENABLED** | 19855617751 | Lawn care & Landscaping | SEARCH | MANUAL_CPC |
| PAUSED | 17325948632 | Search Ads | SEARCH | TARGET_SPEND |
| PAUSED | 20192811337 | Smart Search | SMART | TARGET_SPEND |
| PAUSED | 20218530871 | Smart Search 1 | SMART | TARGET_SPEND |
| PAUSED | 20289812562 | Mowing, Mulching & Aeration | SEARCH | MAXIMIZE_CONVERSIONS |
| PAUSED | 20428528227 | Lawn Care Phrase | SEARCH | TARGET_SPEND |
| PAUSED | 20746848156 | Lawn Care Exact | SEARCH | MANUAL_CPC |
| PAUSED | 22786228319 | Leads-Landscaping-P-Max | PERFORMANCE_MAX | MAXIMIZE_CONVERSIONS |
| PAUSED | 22915679412 | Leads-Search-Aeration | SEARCH | TARGET_SPEND |
| PAUSED | 23719224130 | Leads-Search-Hiring | SEARCH | TARGET_SPEND |

**Exactly one campaign is ENABLED.** All ten use PRESENCE geo targeting already.

**No Local Services Ads campaign exists** in this account — channel types present are
SEARCH, SMART, and PERFORMANCE_MAX only.

## 4. Search-term analysis — 13,508 rows, 7,755 distinct terms

Every historical campaign was included, not only aeration-associated ones.

| Verdict | Terms | Clicks | Click share | Cost | Cost share | Conv |
|---|---:|---:|---:|---:|---:|---:|
| CANDIDATE_KEYWORD | 78 | 101 | 5.2% | $1,309.68 | 7.1% | 12.5 |
| WATCH | 95 | 49 | 2.5% | $367.49 | 2.0% | 1.0 |
| AMBIGUOUS | 592 | 699 | 35.7% | $7,387.53 | 40.1% | 80.2 |
| INSUFFICIENT_DATA | 2,465 | 0 | 0.0% | $0.00 | 0.0% | 0.0 |
| IRRELEVANT | 4,310 | 1,100 | 56.1% | $9,216.67 | 50.0% | 110.4 |
| NEGATIVE_RECOMMENDATION | 215 | 11 | 0.6% | $143.21 | 0.8% | 0.0 |

Candidate terms trace back to five historical campaigns, confirming the instruction to look
beyond aeration-named campaigns was correct: `Lawn Care Phrase` (83 candidate clicks),
`Leads-Search-Aeration` (80), `Lawn care & Landscaping` (67), `Search Ads` (34),
`Mowing, Mulching & Aeration` (11).

### Evidence depth by approved ad group

| Theme | All terms | Candidates | Impr | Clicks | Cost | Conv |
|---|---:|---:|---:|---:|---:|---:|
| Lawn Aeration | 175 | **54** | 627 | 66 | $891.89 | 6.5 |
| Lawn Overseeding | 155 | **3** | 12 | 2 | $15.69 | **0.0** |
| Combined aeration+seeding | 91 | **21** | 341 | 33 | $402.10 | 6.0 |

### Step-19 evidence gap — reported, not papered over

`Lawn Aeration` has strong, conversion-backed BOFU demand. Its best canonical candidates are
`lawn aeration service near me` (9 clicks), `lawn aeration near me` (8), `aeration services
near me` (5), `lawn aeration` (4).

**`Lawn Overseeding` does not have viable standalone BOFU demand in this account's history.**
Across four years the entire overseeding/seeding theme drew 12 impressions and 2 clicks in
its three candidate terms, with zero conversions. Its strongest standalone terms sit at 3–7
impressions each (`overseeding lawn`, `lawn overseeding near me`, `lawn overseeding service`).

Overseeding demand here is almost entirely **bundled with aeration**: the combined theme has
341 impressions, 33 clicks, and 6.0 conversions on terms such as `aeration and seeding near
me`, `aeration and overseeding`, and `aeration and overseeding near me`.

I have not invented volume and have not replaced the service. The two-ad-group structure
stands as approved; this is a flag that ad group 2 will start thin and that combined-intent
routing between the two ad groups needs a deliberate decision at Checkpoint C.

### Related-intent review (step 16) — all held at WATCH

Not verified as EKG services, so none was promoted: sod installation (8 clicks),
dethatching (6 clicks across variants), top dressing (6 clicks), lawn renovation,
lawn restoration, yard renovation, bare-spot and thin-grass phrasing. 95 WATCH terms,
49 clicks, $367.49 total.

### Negatives — 215 proposed, **0 applied**

Nothing was added. By reason: aftercare/DIY maintenance (51 terms, $125.62), equipment
purchase or rental (77, $12.91), employment (27, $4.68), informational with no click (60,
$0.00). 47 terms containing protected commercial words (`near me`, `cost`, `price`, `best`,
`local`, `hire`, `quote`) were **held at WATCH** rather than proposed as negatives, per
Green Marketing policy.

## 5. Conversion audit — 31 actions, and this is the biggest risk

| Status | Count |
|---|---:|
| ENABLED | 21 |
| REMOVED | 9 |
| HIDDEN | 1 |

**17 of the 21 enabled actions are marked `primary_for_goal`**, meaning 17 different things
currently feed bidding. They include Smart-campaign actions, Google-hosted "Local actions"
(website visits, menu views, map directions), a `Click To Email`, GA4 imports, and
WhatConverts uploads.

Problems visible without any further reads:

1. **Map directions, menu views, and website visits are counted as primary conversions.**
   These are engagement signals, not leads. Bidding toward them buys traffic, not jobs.
2. **Call actions are duplicated across at least three surfaces** — `Calls from ads`,
   `Manually Dialled Calls`, `Clicks to call`, `Clicks To Call`, `Click To Call (Button 2)`,
   `EKG - Lp - Phone Call Leads`, `WC calls`. Two share the name `clicks to call` with
   different casing. The same phone lead can be counted several times.
3. **Call duration thresholds are inconsistent**: 60 seconds on most, 30 seconds on
   `Calls from Smart Campaign Ads` and `EKG - Lp - Phone Call Leads`.
4. **Four Smart-campaign actions remain primary** although every Smart campaign is paused.
5. Several use `MANY_PER_CLICK` counting where a lead action should be `ONE_PER_CLICK`.

Per the operating rules I am not optimizing toward any of these until their meaning and
validity are confirmed. **Bidding strategy for the new campaign cannot be responsibly chosen
until this is settled** — a Maximize Conversions strategy pointed at 17 mixed primary actions
would optimize for map clicks.

## 6. Budget and pacing

| Item | Value |
|---|---:|
| Monthly budget | $500.00 |
| Month-to-date spend (Aug 1–14) | $259.51 |
| Remaining monthly budget | $240.49 |
| Remaining serving days | 17 |
| Current run rate | $18.54/day |
| **Projected month-end if unchanged** | **$574.63 — $74.63 over** |
| Proposed first-month daily, if the enabled campaign is paused | $14.15/day |
| Ongoing full-month daily | $16.45/day |

All month-to-date spend comes from the single enabled campaign, whose own daily budget is
$18.44 — above what a $500 month sustains. This overrun predates the new build.

## 7. Location targets — all six confirmed

Five 2.0-mile proximity targets, unchanged and PRESENCE-only, plus postal code 23114
resolved by fresh lookup:

- `geoTargetConstants/9008421`
- canonical name `23114,Virginia,United States` (matches the supplied string exactly)
- country `US`, target type `Postal Code`, status `ENABLED`, **targetable: true**
- estimated reach 90,000; exactly one suggestion returned, so no ambiguity

Coordinates unchanged, radii still miles, `exact_duplicates_found: 0`.

## 8. Business facts — verified vs still open

**Verified from the live account (an authoritative source):**
- Main website `https://ekglawn.com/` — appears in serving ad final URLs.
- Landing-page subdomain `https://offer.ekglawn.com/` is real and in use.
- **An aeration landing page already exists at `https://offer.ekglawn.com/aeration/`.**
  This conflicts with the proposed `/lawn-aeration/` slug.
- Other live offer pages: `/landscaping-brandermill/`, `/landscaping-hallsboro/`,
  `/lawn-care-brandermill/`, `/lawn-maintenance-brandermill/`.

**Still unverified — none invented:** public business name, phone number, service-area
wording, business and call-answering hours, aeration and overseeding availability and
whether they sell separately or bundled, seasonal windows, lawn types, offers, licences,
guarantees, years in business, differentiators, approved images, Privacy Policy and Terms
URLs, and every review.
