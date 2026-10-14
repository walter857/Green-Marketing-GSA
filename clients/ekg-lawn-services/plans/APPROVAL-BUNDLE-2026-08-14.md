# EKG Lawn Services — Final Checkpoint C Approval Bundle

**NOTHING HAS BEEN CREATED, PAUSED, EDITED, PUBLISHED, ASSOCIATED, UPLOADED, OR ENABLED EXTERNALLY.** This document lists every field that a later approved create-paused operation would write.

Date: 2026-08-14 · Mode: READ-ONLY research and local drafts

## 1. Account identity

| Field | Value |
|---|---|
| Exact child account name | `EKG Lawn Services - Live` |
| Child customer ID | `7478932848` |
| Manager (MCC) | `3373711342` (ACTIVE link) |
| Currency | USD |
| Time zone | America/New_York |
| Account status | ENABLED |
| Vertical | landscaping |
| Exact primary service | Aeration & Overseeding |

## 2. Campaign settings

| Field | Value |
|---|---|
| Campaign name | `Aeration & Overseeding` |
| Type | SEARCH (standard) |
| Status on create | **PAUSED** |
| Daily budget | **$16.45 USD**, campaign level, shared dynamically |
| Bidding | `MAXIMIZE_CONVERSIONS`, target CPA `None` |
| Launch ready | **False** |
| Google Search | ON |
| Search Partners | OFF |
| Display Network | OFF |
| AI Max / broad-match expansion / DSA / auto assets / text customization / final-URL expansion | ALL OFF |
| Ad schedule criteria | **0** (no criterion = eligible all day, every day) |
| Default final URL | https://offer.ekglawn.com/lawn-aeration/ |

### August pacing treatment

| Field | Value |
|---|---:|
| Monthly budget | $500.00 |
| Month-to-date spend (to 2026-08-14) | $259.51 |
| Remaining monthly budget | $240.49 |
| Remaining serving days | 17 |
| Temporary first-month daily (at 17 days) | $14.15 |
| Ongoing full-month daily | $16.45 |
| Projected August if existing campaign keeps running | $574.63 |

Recalculate on the actual launch date: `max(0, 500 - current account month-to-date spend) / remaining serving days`

## 3. Location targets — 6, PRESENCE only

| # | Type | Radius | Latitude | Longitude | Constant |
|---|---|---|---|---|---|
| prox-1 | Proximity | 2.0 MILES | 37.441924 | -77.704566 | — |
| prox-2 | Proximity | 2.0 MILES | 37.387932 | -77.701819 | — |
| prox-3 | Proximity | 2.0 MILES | 37.417932 | -77.750571 | — |
| prox-4 | Proximity | 2.0 MILES | 37.435133 | -77.663776 | — |
| prox-5 | Proximity | 2.0 MILES | 37.450549 | -77.751945 | — |
| postal-1 | Postal Code | — | — | — | `geoTargetConstants/9008421` (23114,Virginia,United States), targetable=True |

- `positive_geo_target_type`: **PRESENCE**
- `negative_geo_target_type`: PRESENCE
- exclude_all_other_countries: False
- Negative locations: none

## 4. Ad groups, keywords, final URLs

### Ad group `Lawn Aeration` — status PAUSED

- Canonical keyword: `lawn aeration`
- Final URL: https://offer.ekglawn.com/lawn-aeration/
- Path1 / Path2: *(none set)*

| Keyword | Match type | Status |
|---|---|---|
| `lawn aeration` | PHRASE | PAUSED |
| `lawn aeration` | EXACT | PAUSED |

### Ad group `Aeration & Overseeding` — status PAUSED

- Canonical keyword: `aeration and overseeding`
- Final URL: https://offer.ekglawn.com/aeration-overseeding/
- Path1 / Path2: *(none set)*

| Keyword | Match type | Status |
|---|---|---|
| `aeration and overseeding` | PHRASE | PAUSED |
| `aeration and overseeding` | EXACT | PAUSED |

## 5. Campaign negative keywords — all 33

| # | Text | Match | Intent | Protected scan |
|---:|---|---|---|---|
| 1 | `job` | PHRASE | employment | CLEAN |
| 2 | `jobs` | PHRASE | employment | CLEAN |
| 3 | `hiring` | PHRASE | employment | CLEAN |
| 4 | `career` | PHRASE | employment | CLEAN |
| 5 | `salary` | PHRASE | employment | CLEAN |
| 6 | `employment` | PHRASE | employment | CLEAN |
| 7 | `rental` | PHRASE | equipment | CLEAN |
| 8 | `rent` | PHRASE | equipment | CLEAN |
| 9 | `aerator rental` | PHRASE | equipment | CLEAN |
| 10 | `buy` | PHRASE | equipment | CLEAN |
| 11 | `for sale` | PHRASE | equipment | CLEAN |
| 12 | `machine` | PHRASE | equipment | CLEAN |
| 13 | `equipment` | PHRASE | equipment | CLEAN |
| 14 | `how to` | PHRASE | informational | CLEAN |
| 15 | `diy` | PHRASE | informational | CLEAN |
| 16 | `when to overseed` | PHRASE | aftercare_diy | CLEAN |
| 17 | `after overseeding` | PHRASE | aftercare_diy | CLEAN |
| 18 | `watering schedule` | PHRASE | aftercare_diy | CLEAN |
| 19 | `mow after` | PHRASE | aftercare_diy | CLEAN |
| 20 | `sod` | PHRASE | other_service_line | CLEAN |
| 21 | `sod installation` | PHRASE | other_service_line | CLEAN |
| 22 | `dethatching` | PHRASE | related_unverified | CLEAN |
| 23 | `top dressing` | PHRASE | related_unverified | CLEAN |
| 24 | `lawn renovation` | PHRASE | related_unverified | CLEAN |
| 25 | `lawn restoration` | PHRASE | related_unverified | CLEAN |
| 26 | `mowing` | PHRASE | other_service_line | CLEAN |
| 27 | `mulch` | PHRASE | other_service_line | CLEAN |
| 28 | `landscaping` | PHRASE | other_service_line | CLEAN |
| 29 | `irrigation` | PHRASE | other_service_line | CLEAN |
| 30 | `sprinkler` | PHRASE | other_service_line | CLEAN |
| 31 | `leaf removal` | PHRASE | other_service_line | CLEAN |
| 32 | `fertilizer` | PHRASE | other_service_line | CLEAN |
| 33 | `weed control` | PHRASE | other_service_line | CLEAN |

Protected terms never negatived: `near me, quote, price, pricing, cost, best, hire, local, emergency`. **Scan result: ZERO hits.**

Flagged for term-level review (4): `rent`, `buy`, `sod`, `sod installation`

## 6. Ad-group negative keywords — all 4

| Ad group | Text | Match | Reason |
|---|---|---|---|
| Lawn Aeration | `overseeding` | PHRASE | Routes combined intent to the second ad group. |
| Lawn Aeration | `overseed` | PHRASE | Stem form; catches aerate-and-overseed phrasing. |
| Lawn Aeration | `seeding` | PHRASE | aeration and seeding is the highest-volume combined phrasing, 20 clicks. |
| Aeration & Overseeding | `lawn aeration` | EXACT | Protects the aeration-only exact term for ad group 1. |

## 7. Responsive search ads — every headline and description

### Lawn Aeration — RSA-A (direct high-intent service response) — status PAUSED

Final URL: https://offer.ekglawn.com/lawn-aeration/

| # | Headline | Chars | Pin |
|---:|---|---:|---|
| 1 | Lawn Aeration Service | 21 | HEADLINE_1 |
| 2 | Professional Lawn Aeration | 26 | — |
| 3 | Aeration For Your Lawn | 22 | — |
| 4 | Book Lawn Aeration Today | 24 | — |
| 5 | Local Lawn Aeration Experts | 27 | — |
| 6 | Aeration Done Right | 19 | — |
| 7 | Relieve Compacted Soil | 22 | — |
| 8 | Request a Free Quote | 20 | — |
| 9 | Aeration For Healthier Roots | 28 | — |
| 10 | Get My Free Quote | 17 | — |

| # | Description | Chars |
|---:|---|---:|
| 1 | Professional lawn aeration that opens compacted soil so air and water reach the roots. | 86 |
| 2 | Request a free quote for lawn aeration. Clear answers and a tidy finish. | 72 |

### Lawn Aeration — RSA-B (trust and reassurance, no invented urgency) — status PAUSED

Final URL: https://offer.ekglawn.com/lawn-aeration/

| # | Headline | Chars | Pin |
|---:|---|---:|---|
| 1 | Lawn Aeration You Can Trust | 27 | HEADLINE_1 |
| 2 | Careful, Thorough Aeration | 26 | — |
| 3 | Aeration By A Local Team | 24 | — |
| 4 | We Treat Your Lawn Like Ours | 28 | — |
| 5 | Clear Quotes, No Surprises | 26 | — |
| 6 | Aeration Without The Guesswork | 30 | — |
| 7 | Talk To A Real Person | 21 | — |
| 8 | Your Lawn, Handled Properly | 27 | — |

| # | Description | Chars |
|---:|---|---:|
| 1 | A local crew that shows up, does the work properly and leaves your lawn tidy. | 77 |
| 2 | Ask us what aeration will do for your lawn. Honest advice and a clear quote. | 76 |

### Aeration & Overseeding — RSA-A (direct high-intent combined-service response) — status PAUSED

Final URL: https://offer.ekglawn.com/aeration-overseeding/

| # | Headline | Chars | Pin |
|---:|---|---:|---|
| 1 | Aeration And Overseeding | 24 | HEADLINE_1 |
| 2 | Aeration & Overseeding Service | 30 | — |
| 3 | Aerate And Overseed Your Lawn | 29 | — |
| 4 | Thicken Your Lawn This Season | 29 | — |
| 5 | Book Aeration And Overseeding | 29 | — |
| 6 | Aeration With Overseeding | 25 | — |
| 7 | Request a Free Quote | 20 | — |
| 8 | Get My Free Quote | 17 | — |
| 9 | Overseeding After Aeration | 26 | — |

| # | Description | Chars |
|---:|---|---:|
| 1 | We aerate to open compacted soil, then overseed so seed reaches soil rather than thatch. | 88 |
| 2 | Request a free quote for aeration and overseeding. Clear answers and a tidy finish. | 83 |

### Aeration & Overseeding — RSA-B (trust and reassurance, no invented urgency) — status PAUSED

Final URL: https://offer.ekglawn.com/aeration-overseeding/

| # | Headline | Chars | Pin |
|---:|---|---:|---|
| 1 | Aeration And Overseeding | 24 | HEADLINE_1 |
| 2 | A Thicker Lawn, Step By Step | 28 | — |
| 3 | Local Aeration And Seeding | 26 | — |
| 4 | We Explain What Lawns Need | 26 | — |
| 5 | Careful Work, Clear Quotes | 26 | — |
| 6 | Talk To A Real Person | 21 | — |
| 7 | Your Lawn In Good Hands | 23 | — |
| 8 | No Pressure, Just Advice | 24 | — |

| # | Description | Chars |
|---:|---|---:|
| 1 | We aerate first so seed makes proper contact with soil, then overseed thin areas. | 81 |
| 2 | Ask what aeration and overseeding would do for your lawn. Honest advice, clear quote. | 85 |

## 8. Assets

### Sitelinks — 4 new, 0 reused. All associations PAUSED.

| Ref | Link text | Chars | Description 1 | Chars | Description 2 | Chars | Final URL |
|---|---|---:|---|---:|---|---:|---|
| SL-1 | Lawn Aeration | 13 | Aeration to relieve | 19 | compacted soil. | 15 | https://offer.ekglawn.com/lawn-aeration/ |
| SL-2 | Aeration & Overseeding | 22 | Aerate and overseed | 19 | for a thicker lawn. | 19 | https://offer.ekglawn.com/aeration-overseeding/ |
| SL-3 | Request a Free Quote | 20 | Tell us about your lawn | 23 | and we'll send a quote. | 23 | https://offer.ekglawn.com/lawn-aeration/ |
| SL-4 | Contact EKG Lawn | 16 | Call or send a message. | 23 | Open 8am to 4:30pm daily. | 25 | https://ekglawn.com/contact-us/ |

### Callouts — 2 reused, 6 new. All associations PAUSED.

| Ref/ID | Text | Chars | Reused or new |
|---|---|---:|---|
| **279041242351** | Local Midlothian Pros | 21 | REUSED (existing resource ID) |
| **279041242357** | Overseeding Available | 21 | REUSED (existing resource ID) |
| CO-1 | Lawn Aeration Service | 21 | NEW |
| CO-2 | Aeration & Overseeding | 22 | NEW |
| CO-3 | Woodlake & Brandermill | 22 | NEW |
| CO-4 | Open 7 Days A Week | 18 | NEW |
| CO-5 | Get My Free Quote | 17 | NEW |
| CO-6 | Accepting New Customers | 23 | NEW |

### Structured snippet — 1 new

- Header: `Services`
- Values: `Lawn Aeration` (13), `Aeration with Overseeding` (25), `Overseeding` (11), `Aeration & Overseeding` (22)

### Withheld asset types

- **CALL** — Call-answering hours are unconfirmed. Published opening hours do not prove a human answers throughout them. Withheld until confirmed.
- **IMAGE** — No image is verified as a genuine EKG project photo for this service. Existing assets include stock-named files (e.g. "shutterstock ..."). Withheld.
- **PROMOTION** — No verified offer, discount, or price. Withheld.
- **PRICE** — No verified pricing. Withheld.
- **LOCATION** — Physical address is an UNRESOLVED_CONFLICT between the contact/footer address and the privacy-page address. Withheld.
- **RATING / REVIEW** — No directly verified GBP review evidence. Direct GBP access was attempted and failed. Withheld.

## 9. CampaignAsset associations — 13, every one PAUSED

| Field type | Count | Status on create |
|---|---:|---|
| SITELINK | 4 | **PAUSED** |
| CALLOUT | 8 | **PAUSED** |
| STRUCTURED_SNIPPET | 1 | **PAUSED** |
| **Total** | **13** | **PAUSED** |

AdGroupAsset associations: 0. Existing associations altered anywhere in the account: **0**.

## 10. Conversion goal configuration

### Effective conversion customer

| Field | Value |
|---|---|
| `google_ads_conversion_customer` | `customers/7478932848` |
| Equals campaign child account `7478932848` | **YES** |
| Readable with current credentials | **YES** |
| Both proposed actions owned by it | **YES** |
| Cross-account conversion tracking | none |

The CustomConversionGoal is therefore created in this same account. No write to any other account is planned.

### Members of the proposed custom conversion goal

| Name | Resource name | Category | Origin | Counting | Threshold |
|---|---|---|---|---|---|
| EKG Lawn - Lp - Submit Lead Form | `customers/7478932848/conversionActions/6885542325` | SUBMIT_LEAD_FORM | WEBSITE | ONE_PER_CLICK | — |
| EKG - Lp - Phone Call Leads | `customers/7478932848/conversionActions/6885543534` | PHONE_CALL_LEAD | WEBSITE | ONE_PER_CLICK | 30 |

### Why a standard goal is insufficient

- Pair `SUBMIT_LEAD_FORM / WEBSITE` would also include: `SAU - Submit Form Thank You Page` (id 6483211131), `EKG Lawn (web) form_submission` (id 7388219489)
- Pair `PHONE_CALL_LEAD / WEBSITE` would also include: `EKG Lawn (web) phone_call_click` (id 7388142394)

### Mutations

1. **CREATE** `CustomConversionGoal` — name **`EKG Aeration & Overseeding - Lead Actions`**, resource `customers/7478932848/customConversionGoals/{goal_id}`, status `ENABLED` (no PAUSED state exists for this type), members = exactly the two actions above.
2. **UPDATE** `ConversionGoalCampaignConfig` — resource `customers/7478932848/conversionGoalCampaignConfigs/{campaign_id}`, update_mask **`['custom_conversion_goal']`**, setting only `custom_conversion_goal`. `goal_config_level` is NOT in the mask and is NOT set: Google flips it to CAMPAIGN automatically. It is a readback assertion.

3. **UPDATE x7** `CampaignConversionGoal` — only the rows currently inherited as biddable=true are mutated. CREATE operations planned: **0** (Google auto-creates these).

### Expected CampaignConversionGoal inventory — all 14 rows

Effective conversion customer: `customers/7478932848`. This full set is asserted at preflight AND at final readback. A row added, removed, or with different inherited biddability stops the run and invalidates the fingerprint.

| # | Category | Origin | Inherited biddable | Mutation planned | Required final readback |
|---:|---|---|---|---|---|
| 1 | CONTACT | CALL_FROM_ADS | **TRUE** | **YES** | biddable = **false** |
| 2 | CONTACT | WEBSITE | **TRUE** | **YES** | biddable = **false** |
| 3 | ENGAGEMENT | WEBSITE | **TRUE** | **YES** | biddable = **false** |
| 4 | PAGE_VIEW | WEBSITE | **TRUE** | **YES** | biddable = **false** |
| 5 | PHONE_CALL_LEAD | CALL_FROM_ADS | **TRUE** | **YES** | biddable = **false** |
| 6 | PHONE_CALL_LEAD | WEBSITE | **TRUE** | **YES** | biddable = **false** |
| 7 | SUBMIT_LEAD_FORM | WEBSITE | **TRUE** | **YES** | biddable = **false** |
| 8 | CONTACT | GOOGLE_HOSTED | **FALSE** | no | biddable = **false** |
| 9 | CONTACT | UNKNOWN | **FALSE** | no | biddable = **false** |
| 10 | ENGAGEMENT | GOOGLE_HOSTED | **FALSE** | no | biddable = **false** |
| 11 | ENGAGEMENT | UNKNOWN | **FALSE** | no | biddable = **false** |
| 12 | GET_DIRECTIONS | GOOGLE_HOSTED | **FALSE** | no | biddable = **false** |
| 13 | PAGE_VIEW | GOOGLE_HOSTED | **FALSE** | no | biddable = **false** |
| 14 | PHONE_CALL_LEAD | UNKNOWN | **FALSE** | no | biddable = **false** |

### The only mutations — 7 operations

| Op | Campaign | Category | Origin | Current | Planned | Update mask |
|---:|---|---|---|---|---|---|
| 1 | `{new_campaign_resource_name}` | CONTACT | CALL_FROM_ADS | true | **false** | `['biddable']` |
| 2 | `{new_campaign_resource_name}` | CONTACT | WEBSITE | true | **false** | `['biddable']` |
| 3 | `{new_campaign_resource_name}` | ENGAGEMENT | WEBSITE | true | **false** | `['biddable']` |
| 4 | `{new_campaign_resource_name}` | PAGE_VIEW | WEBSITE | true | **false** | `['biddable']` |
| 5 | `{new_campaign_resource_name}` | PHONE_CALL_LEAD | CALL_FROM_ADS | true | **false** | `['biddable']` |
| 6 | `{new_campaign_resource_name}` | PHONE_CALL_LEAD | WEBSITE | true | **false** | `['biddable']` |
| 7 | `{new_campaign_resource_name}` | SUBMIT_LEAD_FORM | WEBSITE | true | **false** | `['biddable']` |

### No mutation planned — 7 rows, assertion only

| Category | Origin | Inherited | Mutation |
|---|---|---|---|
| CONTACT | GOOGLE_HOSTED | false | **none** |
| CONTACT | UNKNOWN | false | **none** |
| ENGAGEMENT | GOOGLE_HOSTED | false | **none** |
| ENGAGEMENT | UNKNOWN | false | **none** |
| GET_DIRECTIONS | GOOGLE_HOSTED | false | **none** |
| PAGE_VIEW | GOOGLE_HOSTED | false | **none** |
| PHONE_CALL_LEAD | UNKNOWN | false | **none** |

These are already false. Updating them would be a no-op external write. They still carry preflight and readback assertions.

### Future create-paused sequence

1. Create the approved campaign and all new resources PAUSED.
2. Read the ACTUAL CampaignConversionGoal inventory for the new campaign.
3. Compare category, origin and inherited biddability against the 14-row expected inventory.
4. If anything differs, STOP with the campaign still paused and invalidate the fingerprint.
5. If it matches, apply the seven biddable=false updates.
6. Apply the CustomConversionGoal through ConversionGoalCampaignConfig.
7. Read everything back.

### Final QA assertions

- Custom goal contains EXACTLY the two approved conversion actions (count == 2).
- ALL 14 CampaignConversionGoal rows read back biddable == false.
- conversion_goal_campaign_config.goal_config_level == CAMPAIGN (set by Google).
- conversion_goal_campaign_config.custom_conversion_goal == the created goal.
- No account-level CustomerConversionGoal row changed.
- No other conversion action can drive bidding.

## 11. Complete mutation inventory

| Resource type | Operation | Count | Status on create |
|---|---|---:|---|
| CampaignBudget | CREATE | 1 | no status field |
| Campaign | CREATE | 1 | **PAUSED** |
| CampaignCriterion (proximity) | CREATE | 5 | no paused state |
| CampaignCriterion (location) | CREATE | 1 | no paused state |
| CampaignCriterion (negative kw) | CREATE | 33 | no paused state |
| CampaignCriterion (ad schedule) | CREATE | 0 | n/a — none created |
| AdGroup | CREATE | 2 | **PAUSED** |
| AdGroupCriterion (keyword) | CREATE | 4 | **PAUSED** |
| AdGroupCriterion (negative kw) | CREATE | 4 | no paused state |
| AdGroupAd (RSA) | CREATE | 4 | **PAUSED** |
| Asset (sitelink) | CREATE | 4 | no serving status |
| Asset (callout) | CREATE | 6 | no serving status |
| Asset (structured snippet) | CREATE | 1 | no serving status |
| CampaignAsset | CREATE | 13 | **PAUSED** |
| AdGroupAsset | CREATE | 0 | n/a — none |
| CustomConversionGoal | CREATE | 1 | ENABLED (no PAUSED state) |
| ConversionGoalCampaignConfig | UPDATE | 1 | no status field |

**Total creates: 80 · Total updates: 8 · Total mutations: 88**

Reused assets associated but NOT created: 2 (callout IDs 279041242351, 279041242357).

Withheld, zero planned: call, image, promotion, price, location, rating/review assets.

## 12. Landing-page artifacts

### Template source

| Field | Value |
|---|---|
| Drive ID | `1ohZDtALF5Px8RygicPx5_VQyVz6e4TcsY8rbDDgc7ZQ` |
| Title | `Landing Page Content Template - Master` |
| Parent folder | `1JGAe8PSK9Vs83wk12K5VztKOFhctDMEZ` |
| Modified | 2026-08-14T13:29:01.261Z |
| Drive version | 9 |
| Document SHA-256 | `bd6bba3911db44d259de9db56036d3809444b982b18ebc7912db0c9b0c64653a` |
| Ambiguity check | Exactly one candidate master exists in the Templates folder. |
| Signature match | **True** — 1 tab, 177 paragraphs, 13 bullets, 0 tables, 9 image placements, 3 review slots |

### Draft artifacts and hashes

| Page | File | SHA-256 |
|---|---|---|
| Lawn Aeration | `clients/ekg-lawn-services/landing-pages/lawn-aeration-content.md` | `40a693eb4b8db5d8f43e127ae83467d9f84f783680350322177ed84c2c67a2bd` |
| Aeration & Overseeding | `clients/ekg-lawn-services/landing-pages/aeration-overseeding-content.md` | `9fff280e55779bf657dab8f934591fe745b969f8ceded559101d0d5e530d8987` |

| Provenance manifest | File | SHA-256 |
|---|---|---|
| Image and review provenance | `clients/ekg-lawn-services/landing-pages/image-and-review-provenance-manifest.md` | `3cd2814f902c7505171ae306c99901e5e6627065d748981ded028eb9435f4194` |

### Image slots — 0 selected, 2 developer candidates, 7 developer TODOs

Visual QA was performed by downloading and rendering the actual files where the source permitted. Reading a source page is not visual verification.

| Slot | Para | Status | Visually inspected | Alt text |
|---|---:|---|---|---|
| 1 Hero | 22 | **DEVELOPER CANDIDATE — VISUAL QA REQUIRED** | No — HTTP 401 | A residential home with a healthy green lawn |
| 2 Main | 69 | **DEVELOPER TODO** — candidate rejected | Yes — rendered | A lawn being aerated |
| 3 Card 1 | 89 | **DEVELOPER CANDIDATE — VISUAL QA REQUIRED** | No — HTTP 401 | A lush green lawn with trees behind it |
| 4 Card 2 | 92 | DEVELOPER TODO | — | Water soaking into a lawn |
| 5 Card 3 | 95 | DEVELOPER TODO | — | per page |
| 6-9 Gallery | 105,107,109,111 | DEVELOPER TODO | — | A completed EKG lawn project |

The slot-2 candidate was rejected on inspection: a prominent third-party manufacturer logo is legible in the centre of the frame, and the framing shows consumer tow-behind equipment. Source URLs, creators and licences are recorded ONLY in the internal provenance manifest and never appear in page copy.

### Review slots — 3 developer TODOs

Template paragraphs 128, 130, 132 preserved. Every supplied Google source returned an error page or refused connection on 2026-08-14. No review, rating, or review count appears on either page, and no website testimonial or third-party mirror was substituted.

### Logo

Template positions 7 and 174 preserved as the template's own `LOGO HERE` markers. `[DEVELOPER TODO: Insert official EKG Lawn logo]` recorded in the provenance manifest. Not a create-paused blocker.

| Compliance manifest | File | SHA-256 |
|---|---|---|
| Lawn Aeration | `clients/ekg-lawn-services/landing-pages/lawn-aeration-template-compliance.md` | `0cd9c784e0978a50afbaca839f90db441e536ff8fb910852dbf60730240beb27` |
| Aeration & Overseeding | `clients/ekg-lawn-services/landing-pages/aeration-overseeding-template-compliance.md` | `585ccaf74c0c572cc0056f2d75b79df47c93dc150630de5675a5381a46fdea28` |

Both pages: **177/177 paragraphs PASS**, all 9 image placements preserved, all 3 review slots preserved as labelled placeholders. Neither page published or uploaded.

## 13. Unresolved launch blockers

**Create-paused stage** — 0

- none

**Page publication stage** — 5

- `P1` No real project photos — Section 7 is RETAINED in both drafts with four PENDING_REAL_PROJECT_PHOTO placements. Required by the master template, so the page cannot publish until real EKG job photos are supplied.
- `P2` No verified GBP reviews — Section 9 is RETAINED with three PENDING_VERIFIED_GBP_REVIEW placements. Direct GBP access was attempted and failed. Website testimonials must not be substituted.
- `P3` Logo asset not supplied
- `P4` Process section not confirmed against EKG real workflow
- `P5` Both pages do not exist yet and must return HTTP 200

**Enablement stage** — 5

- `E1` Form conversion trigger unverified — Read-only QA must prove it fires on completed submission, not button click.
- `E2` Qualified-call configuration unresolved — conversionActions/6885543534 counts at 30s against an account norm of 60s.
- `E3` Existing campaign 19855617751 not paused — August projects 574.63 USD against a 500 USD budget.
- `E4` August budget pacing — Recalculate on the actual launch date.
- `E5` Landing pages must return HTTP 200 and pass mobile/form/call QA

**Asset-only** — 1

- `A1` Call-answering hours unconfirmed — Blocks the CALL asset only, not the campaign. The call asset is withheld, so this does not gate create-paused or enablement.

**Measurement only** — 1

- `M1` WhatConverts deduplication unverified — WC Leads and WC calls stay SECONDARY_PENDING_DEDUPLICATION and are excluded from bidding. A measurement issue, not a launch gate.

**Business information only** — 1

- `I1` Physical address conflict — Unresolved business-information issue. NOT a campaign launch blocker: no address appears on either page and no location asset is attached.

## 14. Preserved and unchanged

- Existing campaign `19855617751` (`Lawn care & Landscaping`) — untouched. Pause fingerprint `22F413D569DB` unchanged and NOT authorization to pause.
- Legacy page `https://offer.ekglawn.com/aeration/` — untouched.
- Existing assets `94530956715` and `81374700734` — rejected for reuse, neither edited nor removed.
- The nine already-paused campaigns — untouched.
- Account-level conversion goals — unchanged.
- Google Ads OAuth, Drive OAuth, ADC, gcloud config, `.env` — untouched.

