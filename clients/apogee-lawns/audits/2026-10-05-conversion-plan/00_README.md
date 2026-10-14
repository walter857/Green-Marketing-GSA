# Apogee Lawns — conversion-path plan, 2026-10-05

**Account:** Apogee Lawns LLC - Live · **816-462-6278** (manager 337-371-1342, not the account)
**Service:** Permanent Christmas light installation · similar-local-service. Scope was approved by Walter on
2026-09-16; it is recorded, not re-requested.
**Campaign:** S | Website Leads | Permanent Christmas Lights | Apogee Lawns | $500 | 09_2026 (24257151015)
**Mode:** READ and local DRAFT. **External writes: none.** The only Google Ads calls that touch the mutate
endpoint were `validate_only` dry runs, which write nothing.

## Best conversion recommendation

**Fix the inquiry path before November.** The page's form cannot produce a countable lead today:
- there is no thank-you page and no success event;
- the page cache hands one ad visitor's attribution (including another visitor's gclid and gbraid) to everyone;
- three copies of the form sit on one page;
- internal drafting notes are published on it.

November holds about half of the year's searches (Planner, three full years).

Approve the developer handoff **APG-1005-WEB-REPAIR** first. Run the controlled tests (APG-1005-TEST) when it is
deployed. In parallel, the low-risk Google Ads bundles can go in **paused**:
- APG-1005-KWNEG: installation Exact keywords, a competitor negative, and removal of three negatives that block
  the owner-confirmed customer-supplied service;
- APG-1005-ADS: installation-signaling RSAs and a "Free Estimates" callout.

Keep bidding and budget unchanged until tracking is verified.

## Gates

| Gate | Result |
|---|---|
| Work order reconciled (task, final URL, settled decisions, bidding deviation) and client profile reconciled (landing page, phones, hours, conversions, integrations) | done |
| `python scripts/validate_work_order.py clients/apogee-lawns/work-order.yaml --client clients/apogee-lawns/client.yaml` | **PASS** · Apogee Lawns LLC - Live · 8164626278 · similar-local-service · Permanent Christmas light installation |
| Work-order and policy unit tests | 36 passed |
| Fresh identity lookup (three separate times today) | **PASS**. The exact name and ID match, not a manager, not a test account |

## Verified 2026-10-05 · supplied context · assumptions

**Verified today**
- **Account and settings** (snapshot `snapshots/2026-10-05-conversion-plan-snapshot.json`):
  - The account is unchanged since the 09-25 tablet edit.
  - Search only; Search Partners and Display off; Broad off; AI Max unset; text automation opted out; DSA off.
  - Presence targeting on the 14 expected geo IDs; tablet −100%; 24/7.
  - All 7 legacy lists unattached; no auto-apply subscriptions.
- **Performance:**
  - 09-21 to 10-04: **194 impressions, 7 clicks, $46.32, CPC $6.6171, 0 conversions.**
  - Last 7 days (09-28 to 10-04): 142 impressions, 4 clicks, $27.63, CPC $6.91, budget-lost impression share 0%.
  - Today (partial): 1 click, $6.83.
- **Placement:** 97 top-of-page impressions earned all 7 clicks; the 97 other impressions earned 0. The
  installation Phrase keyword at the top: 52 impressions, 6 clicks, 11.5% CTR. The general Exact term at the top:
  44 impressions, 0 clicks.
- **Search terms:** 36 visible terms, 129 impressions, **0 clicks**. All 8 clicked queries are hidden by Google's
  privacy threshold, so they are not reported here.
- **WhatConverts:** 0 paid-search leads; 11 LSA leads (requested service unknown and not credited to permanent
  lighting).
- **Inquiry path:** see the A01–A08 table in `03`. 5 of 7 ad clicks arrived with gbraid, 0 with gclid.
- **Claims:** re-verified against the full text of Apogee's site and the paid page (see `05`).
- **Competitors:** Brilliant By Night is a permanent-lighting company serving Lincoln (brilliantbynight.com/lincoln).

**Supplied context, confirmed:** the baseline numbers, the A01–A08 checklist, notes C1–C3, the keyword results, the
placement split, and the seasonality. Fresh Planner data, same day: Lincoln Sep 4% · Oct 13% · Nov 50% · Dec 18%;
service area 5/13/49/19%.

**Assumptions, not results:** the 5%, 8% and 10% click-to-lead rates; the 20% close rate (the owner has not
measured it); any November projection.

Eligible impression share (80.7%) covers only the searches the current keywords and targeting qualified for. It is
not total local demand.

## Audit summary (7 dimensions)

| Dimension | Severity | Finding |
|---|---|---|
| Conversion tracking | **Critical** | The form conversion cannot fire (no thank-you page or event), and cached attribution is cross-contaminated. Calls: configuration correct, routing untested |
| Landing page | **High** | Drafting notes C1–C5 published; 3 form copies; form and FAQ disagree; email required |
| Ad creative | Medium | 8 of 12 pinned H1 options do not say "install"; the consultation/design offer is unused; no sitelinks, location, images or business name |
| Keywords and search terms | Medium | The structure is right. Close variants pull product research into the Exact head term, and 3 live negatives contradict the owner-confirmed service |
| Bidding and budget | Low today | "Limited by bid strategy" ($8 ceiling); 20% of budget used. No change until tracking works |
| Targeting | OK | Matches every settled decision |
| Wasted spend | Not assessable | $46.32 total. With 0 conversions on a tracking path that cannot record a form lead, zero-conversion spend is **not** labeled waste |

## Search terms and keywords

All 36 terms are judged individually in `02_search_term_verdicts.csv`.

- **Add Exact to the installation group:**
  - [permanent christmas lights lincoln ne]
  - [permanent christmas lights installation near me]
  - [permanent holiday light installation near me]
  - [permanent lighting installation]

  These are hiring-intent queries that today match only through Google's meaning-based matching. **They add no
  new demand.** They give the queries their own keyword rows and bids.
- **Keep eligible:** every cost/price and near-me query, all mixed roofline queries, and the general head term
  (Exact only, under the installation-focused trial).
- **Negatives:**
  - add phrase "brilliant by night" (competitor, navigational);
  - add Exact [types of permanent outdoor christmas lights] (informational; this query only, not a broad
    "types of");
  - **remove** phrase "customer supplied", "labor only" and "my own lights" (the owner confirms Apogee installs
    customer-supplied lights);
  - **hold** Inception, pending owner confirmation of supported customer-supplied systems.

## Economics (pure calculation; observed CPL, CPQL, CAC, revenue and profit are unavailable, not $0)

| Click-to-lead (assumed) | CPL at $6.6171 | CPL at $6.9075 (last 7) | CAC at 20% close (assumed) | P(0 leads in 7 clicks) |
|---|---|---|---|---|
| 5% | $132.34 | $138.15 | $661.71 | 69.8% |
| 8% | $82.71 | $86.34 | $413.57 | 55.8% |
| 10% | $66.17 | $69.07 | $330.85 | 47.8% |

- A $100 CPL needs a 6.62% click-to-lead rate (6.91% at the last-7-day CPC).
- The $499.78 monthly cap (16.44 × 30.4) buys at most about 72–76 clicks.
- **Ad-cost-only break-even:** gross profit per sold job must exceed the CAC above, and that is before any other
  cost. **The owner's gross profit per installation is the missing input.**

## Bidding decision (recorded deviation)

- **Now:** keep Maximize Clicks with the $8 ceiling, no budget change. This is a temporary deviation from the
  agency default (Maximize Conversions), recorded in the work order. Maximize Conversions "requires conversion
  tracking" and "will try to fully spend your average daily budget" (support.google.com/google-ads/answer/7381968),
  and the tracking does not work yet.
- **After repair:** once R1–R8 pass and T1/T2 pass, re-decide no earlier than 14 days of verified tracking, using
  verified leads, the qualified share, and the owner's gross profit per job.
- **Expected next step:** Maximize Conversions with **no target CPA**, accepting that spend may rise toward
  $16.44 a day. Tablet −100% still applies under it. **It is not approval-ready until those inputs exist.**

**Conversion goals:** no change. Website calls (7773043879) stay Secondary until routing and attribution are
verified with a real ad visitor's call.

## Bundles

| Bundle | Scope | Objects | Readiness | Fingerprint | Approval line |
|---|---|---|---|---|---|
| **APG-1005-WEB-REPAIR** | Developer handoff R1–R8 (spec `03`, its SHA-256 is inside the plan). No Ads, GTM or WhatConverts change | 8 items | **Ready** | **5C808616F617** | `APPROVE APG WEB REPAIR HANDOFF 5C808616F617` |
| **APG-1005-KWNEG** | 4 Exact keywords (PAUSED) in 200347713516; +2 negatives; −3 negatives (criterion IDs 296448593009, 573042878059, 2225874598953) | 9 operations | **Ready.** `validate_only` accepted | **EECDDF0AF0DE** | `APPROVE APG KWNEG EECDDF0AF0DE` |
| **APG-1005-ADS** | 2 RSAs (PAUSED), 1 callout asset, 1 PAUSED campaign link | 4 operations | **Ready.** `validate_only` accepted | **0A321B6092AE** | `APPROVE APG ADS CREATE-PAUSED 0A321B6092AE` |
| APG-1005-TEST | Controlled desktop and mobile form tests, plus a routing call | 4 tests | **Blocked**: needs WEB-REPAIR deployed and a test identity | — | — |
| APG-1005-SITELINKS | 6 sitelinks to real page sections | 6 + 6 | **Blocked**: anchors added by R6 must exist live | — | — |
| Follow-ups after readback | KWNEG-ENABLE (enable the 4 keywords); ADS-TRANSITION (enable 2 new RSAs and the callout link; pause 825023783010 and 825023783013) | — | Prepared after readback; separate approval | — | — |

**What every bundle carries:**
- the exact account and service;
- current and proposed values;
- campaign, budget, location, schedule, URL and conversion state, all unchanged unless listed;
- full keywords and copy;
- statuses and counts;
- preconditions, readback assertions, a recovery plan and a rollback.

**Execution rules:**
- Batches are atomic (`partial_failure=false`).
- If a partial success is ever observed: stop, inventory every resource ID, and propose recovery before any
  retry.
- `APG-0928-NEG-LO` / 58362D536336 is superseded and must never be executed.

## Validation summary

- **Pre-fingerprint red-team** covered: client truth, strategy, search intent, conversion isolation (no
  conversion change), mutation necessity, API fields, statuses (all creates PAUSED), asset support, character
  limits (headlines ≤30, descriptions ≤90, paths ≤15, callout ≤25, sitelinks 25/35), URL mapping, locations,
  budget math, claims, mutation counts and artifact hashes.
- **Automated builder checks:** 0 problems.
- **Claim matching:** every claim matched today's captured page text.
- **Keyword and negative checks:**
  - no new keyword duplicates an existing one or is blocked by a negative;
  - no new negative blocks a positive keyword or any kept search term;
  - the protected words (cost, price, pricing, quote, best, hire, local, near me, emergency) are untouched.
- **Google Ads `validate_only`:** both Ads bundles accepted, with the identity gate passed first.

## Genuine blockers (each listed once)

1. The developer must ship R1–R8 before any conversion can be counted (owner authorizes WordPress work).
2. A Green Marketing test identity, via the approved secure method, is needed for the controlled tests.
3. Sitelinks need the R6 section anchors live.
4. Images need confirmed account eligibility (≥60 days open, checked in the interface) and written commercial-use
   rights for the photos.
5. Business name and logo need advertiser verification; location assets need the Business Profile owner to
   accept a link.
6. Bidding economics need the gross profit per sold installation.

## Questions for the owner (only what changes the plan)

1. **Gross profit per sold installation** (or average job value and margin), and what counts as a sold job.
   *Recommended:* supply one figure now. *If unanswered:* bidding stays on Maximize Clicks at $8.
2. **Who receives form notifications, and what happens to an unanswered or after-hours call to 402-526-5754?**
   *If unanswered:* lead delivery stays unverified (A08) and section E cannot be finalized.
3. **Which customer-supplied systems will Apogee install?** This decides whether the existing brand negatives
   (govee, gemstone, jellyfish, oelo, trimlight, celebright) and the Inception hold block real "brand +
   installer" customers. *If unanswered:* those negatives stay as they are.
4. **Photo rights, advertiser verification, and the Business Profile link.** These unlock images, business name
   and logo, and location assets.
5. **LSA job types:** do the 11 LSA leads include holiday lighting? Answer only if you want a separate LSA
   workflow; nothing changes here.

## Monitoring after repair (read-only reviews; no automatic account changes)

- **Day 1 after deploy:** read-only browser check of acceptance criteria 5, 7, 8 and 9; then T1–T4 under their
  own approval.
- **Weekly:**
  - WhatConverts paid-funnel leads: form and call, click ID captured (gclid or gbraid), qualified Y/N, estimate
    booked, sold, revenue, gross profit;
  - Google Ads conversions reconciled against WhatConverts paid leads;
  - visible search terms;
  - top-of-page share for the installation keyword, CPC, and budget pacing ($16.44 a day, $499.78 at 30.4 days).
- **Diagnostic thresholds:** at an assumed 5% click-to-lead rate, zero leads is 21% likely after 30 tracked clicks,
  10% after 45, and 5% after 60.
  - Zero leads after **45 tracked clicks** triggers a landing-page and offer review, not a bid increase.
- **Monthly:** spend, leads, qualified leads, estimates, sales, revenue, gross profit, CPL, CPQL, CAC, ROAS and
  profit after ad spend, with formulas, and with missing outcomes shown as unavailable.

## Files

- `03_measurement_and_friction_repair_spec.md`: A01–A08 status, R1–R8, acceptance criteria, tests, lead handling.
- `05_ads_and_assets_drafts.md`: full copy, pins, counts, claim sources, sitelinks, asset status.
- `02_search_term_verdicts.csv`: the 36 terms, each with intent, action and reason.
- `economics.json`, `tag-config.json`, `validate-only-results.json`, `bundle-fingerprints.json`, `browser-qa/`.
- Plans: `clients/apogee-lawns/plans/APG-1005-{WEB-REPAIR,KWNEG,ADS,TEST,SITELINKS}.yaml`.
- Official sources used:
  - 6105160 (GTM conversion tag, linker, transaction ID)
  - 6386790 (transaction-ID rules)
  - 9342105 (close variants)
  - 2472708 (search terms report, privacy)
  - 9566341 (image eligibility)
  - 7381968 (Maximize Conversions)
  - adspolicy 1054210 (sitelink domain)
