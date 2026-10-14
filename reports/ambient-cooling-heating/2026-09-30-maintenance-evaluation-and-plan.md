# Ambient: Boiler Maintenance and Heat Pump Maintenance evaluation

> **REVISED 2026-09-30b. This report's recommendation is SUPERSEDED.**
> - The client now requires a CPL target of $280 and a hard ceiling of $350.
> - `AMB-0930-HPM-BUDGET-1` (`7472853C4EA9`) and `AMB-0930-HPM-ENABLE-1` (`90C7E29E61BA`) are **WITHDRAWN** and must never execute or be reused.
> - Heat Pump Maintenance is on **HOLD**: the evidence cannot support $280 CPL. Boiler Maintenance stays on **HOLD** (D2).
> - The earlier "stop-loss" was a policy statement only. **No automatic pause existed.**
> - Current package: `reports/ambient-cooling-heating/2026-09-30b-cpl-policy-revision.md`.


**Account:** Ambient Cooling - Live · child 240-195-9466 (API 2401959466) · MCC 337-371-1342 (never used as the child ID)
**Date:** 2026-09-30. Last complete day is Sept 29. Sept 30 is partial and not used for any conclusion.
**Work orders:**
- `work-orders/work-order-heat-pump-maintenance-2026-09-30.yaml` (Heat Pump Maintenance)
- `work-orders/work-order-boiler-maintenance-2026-09-30.yaml` (Boiler Maintenance)
- Both are mode `draft` and validate against `client.yaml`.

**External writes so far: none.** Google's server-side validate-only checks ran; they write nothing.

---

## Recommendation

1. **Boiler Maintenance: do not bring it live.** The D2 page defect is **not fixed**. `/boiler-maintenance/` has a maintenance H1, but every section heading, the CTA and the FAQ are still Boiler Installation content.
   - No Google Ads change is proposed.
   - Two RSAs are drafted and **held** locally, ready for when the page passes.
2. **Heat Pump Maintenance: bring it live, but only with budget room.** Everything needed already exists: 2 approved RSAs pointing at the right URL, 3 enabled keywords and clean routing negatives.
   - The Heat Pump campaign ($15/day) buys about **one click per serving day** and is at about 95% of its monthly allowance. Enabled into that budget, maintenance clicks would displace Heat Pump Repair, Installation and Replacement clicks almost one-for-one.
   - Two approvals, in order:
     1. **AMB-0930-HPM-BUDGET-1 · `7472853C4EA9` · 2 operations** (separate budget approval). Heat Pump campaign $15 → $30/day, funded by cutting the idle Maintenance & Inspection campaign $45 → $30/day. That campaign has 0 enabled ads. Enabled total stays $305/day.
     2. **AMB-0930-HPM-ENABLE-1 · `90C7E29E61BA` · 5 operations** (separate ENABLE approval, only after the Phase 6 readback). Enable the 2 existing ads and swap the label DEFERRED_BUDGET → MAINTENANCE_TEST.
   - **If the budget move is not approved, keep Heat Pump Maintenance held.**
3. No new ads, keywords, sitelinks or other assets are needed for Heat Pump Maintenance, and none are proposed.

---

## A. Current performance: live heating campaigns and ad groups

### Campaigns

"Primary conv." is the Google Conversions column: WC Lead, WC Calls and Calls from ads.

| Campaign | Window | Spend | Impr. | Clicks | CTR | Avg CPC | Primary conv. | IS | Lost rank | Lost budget | Top | Abs. top |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Heating & Furnace Repair | Sep 24–29 | $469.90 | 1,067 | 17 | 1.6% | $27.64 | 0 | 41.8% | 39.3% | 18.9% | 29.2% | 17.4% |
|  | Sep 23–29 | $469.90 | 1,097 | 17 | 1.5% | $27.64 | 0 | 39.1% | 43.6% | 17.3% | 27.2% | 16.3% |
|  | Sep 16–29 | $469.90 | 1,103 | 17 | 1.5% | $27.64 | 0 | 37.5% | 45.9% | 16.6% | 26.2% | 15.6% |
|  | Sep 1–29 | $469.90 | 1,103 | 17 | 1.5% | $27.64 | 0 | 37.5% | 45.9% | 16.6% | 26.2% | 15.6% |
| Heat/Furnace Install & Replace | Sep 24–29 | $206.65 | 569 | 6 | 1.1% | $34.44 | 1 | 51.3% | 48.7% | 0.0% | 41.9% | 29.7% |
|  | Sep 23–29 | $233.59 | 614 | 9 | 1.5% | $25.95 | 1 | 48.9% | 51.1% | 0.0% | 39.4% | 27.4% |
|  | Sep 16–29 | $233.59 | 623 | 9 | 1.4% | $25.95 | 1 | 46.3% | 53.7% | 0.0% | 37.4% | 25.2% |
|  | Sep 1–29 | $233.59 | 623 | 9 | 1.4% | $25.95 | 1 | 46.3% | 53.7% | 0.0% | 37.4% | 25.2% |
| Boiler Services | Sep 24–29 | $333.65 | 47 | 9 | 19.1% | $37.07 | 1 | 69.0% | 31.0% | 0.0% | 65.5% | 58.6% |
|  | Sep 23–29 | $333.65 | 52 | 9 | 17.3% | $37.07 | 1 | 72.2% | 27.8% | 0.0% | 61.1% | 55.6% |
|  | Sep 16–29 | $346.49 | 61 | 10 | 16.4% | $34.65 | 1 | 68.9% | 22.2% | 8.9% | 57.8% | 46.7% |
|  | Sep 1–29 | $346.49 | 91 | 10 | 11.0% | $34.65 | 1 | 70.9% | 20.0% | 9.1% | 61.8% | 50.9% |
| Heat Pump & Ductless | all windows | $78.42 | 44 | 3 | 6.8% | $26.14 | 0 | 65.7% | 34.3% | 0.0% | 48.6% | 31.4% |
| Thermostat | all windows | $23.65 | 28 | 2 | 7.1% | $11.82 | 0 | 20.0% | 80.0% | 0.0% | 20.0% | 10.0% |
| Maintenance & Inspection (ads paused Sep 25) | Sep 1–29 | $82.22 | 324 | 5 | 1.5% | $16.44 | 0 | 28.0% | 72.0% | 0.0% | 19.4% | 12.5% |
| Geothermal (ads paused Sep 25) | Sep 1–29 | $50.58 | 44 | 3 | 6.8% | $16.86 | 0 | 43.8% | 56.2% | 0.0% | 37.5% | 29.2% |

All seven campaigns started delivering on Sept 17 or later, except Boiler Services, which is the old Gas Boiler Repair campaign. That is why the 14-day and month-to-date windows mostly match.

### Ad groups, Sept 24–29

| Campaign | Ad group | Status | Spend | Impr. | Clicks | CTR | Avg CPC | Primary conv. | IS | Lost rank | Abs. top |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Repair | Heating Repair | serving | $406.12 | 859 | 15 | 1.7% | $27.07 | 0 | 41.8% | 39.3% | 16.6% |
| Repair | Furnace Repair | serving | $63.78 | 168 | 2 | 1.2% | $31.89 | 0 | 49.0% | 32.3% | 23.5% |
| Repair | Gas Furnace Repair | serving | $0.00 | 38 | 0 | 0.0% | – | 0 | 10.0% | 75.0% | 10.0% |
| Repair | No Heat Repair | serving | $0.00 | 2 | 0 | – | – | 0 | – | – | – |
| Repair | Electric Furnace Repair | serving | $0.00 | 0 | 0 | – | – | 0 | – | – | – |
| Repair | Emergency Heating Repair | held, no ads | – | – | – | – | – | – | – | – | – |
| Install/Replace | Furnace Replacement | serving | $161.92 | 159 | 5 | 3.1% | $32.38 | **1** | 66.2% | 33.8% | 41.5% |
| Install/Replace | Heating Installation | serving | $44.73 | 269 | 1 | **0.4%** | $44.73 | 0 | 44.8% | 55.2% | 24.1% |
| Install/Replace | Furnace Installation | serving | $0.00 | 62 | 0 | 0.0% | – | 0 | 42.9% | 57.1% | 35.7% |
| Install/Replace | Heating Replacement | serving | $0.00 | 51 | 0 | 0.0% | – | 0 | 35.5% | 64.5% | 19.4% |
| Install/Replace | Ductless Heating Installation | held, ads paused | $0.00 | 28 | 0 | – | – | 0 | – | – | – |
| Boiler | Boiler Repair | serving | $242.87 | 26 | 6 | 23.1% | $40.48 | 0 | 61.1% | 38.9% | 50.0% |
| Boiler | Gas Boiler Repair | serving | $69.57 | 9 | 2 | 22.2% | $34.78 | 0 | 75.0% | 25.0% | 75.0% |
| Boiler | Boiler Replacement | serving | $21.21 | 12 | 1 | 8.3% | $21.21 | **1** | 85.7% | 14.3% | 71.4% |
| Boiler | Boiler Maintenance | held, no ads, keywords paused | – | – | – | – | – | – | – | – | – |
| Boiler | Boiler Installation | held, no ads | – | – | – | – | – | – | – | – | – |
| Heat Pump | Heat Pump Installation | serving | $78.42 | 20 | 3 | 15.0% | $26.14 | 0 | 64.7% | 35.3% | 35.3% |
| Heat Pump | Heat Pump Replacement | serving | $0.00 | 22 | 0 | – | – | 0 | 64.7% | 35.3% | 23.5% |
| Heat Pump | Heat Pump Repair | serving | $0.00 | 2 | 0 | – | – | 0 | – | – | – |
| Heat Pump | Heat Pump Maintenance | held, 2 ads paused | – | – | – | – | – | – | – | – | – |
| Heat Pump | Ductless Heating Repair | held, ads paused | – | – | – | – | – | – | – | – | – |
| Thermostat | Thermostat Replacement | serving | $23.65 | 21 | 2 | 9.5% | $11.82 | 0 | 20.0% | 80.0% | 10.0% |
| Thermostat | Thermostat Repair / Smart Thermostat | serving | $0.00 | 7 | 0 | – | – | 0 | – | – | – |

### Leads and attribution

These follow the handoff rules: each lead has a click ID or a Google call record, not just a label.

- **Identifiable paid leads with a Google click ID, Sept 17–30:** exactly 2, both on Sept 28. They also appear as the 2 Primary conversions (WC Lead):
  1. A web form from `/boiler-replacement/`, ad group Boiler Replacement, from a single $21.21 click.
  2. A 266-second call on the DNI number 914-1456 after landing on `/hvac-replacement/`, ad group Furnace Replacement.
- **Quotable disposition of both Sept 28 leads: still "Not Set"** (WhatConverts API, read 2026-09-30).
- **Google call records:**
  - 52 seconds on Sept 25 in Heating Repair, which is under the 60-second threshold.
  - 60 seconds today at 11:38 in Heating Repair. Today is partial, so it isn't counted here.
- **Other WhatConverts leads labeled google/cpc, not counted as paid:**
  - A 56-second wrong-number call (Sept 23, marked not quotable).
  - A repeat main-site contact form with an old campaign label and no click ID (Sept 27).
- **CPL, Sept 24–29:**
  - $1,214.07 across the seven campaigns ÷ 2 = **$607**.
  - Core only (excluding Maintenance and Geothermal spend before their ads were paused): $1,112.27 ÷ 2 = **$556**.
  - Both are upper bounds, because calls on fixed-source numbers can't be tied to clicks.
- **Qualified leads and CPQL: not computable.** No September lead has a quotable disposition, and no revenue or sale values exist.

### Strongest and weakest

This rests on 2 raw leads, so it is directional. There is no qualified-lead or revenue evidence yet.

**Strongest:**
- **Furnace Replacement:** 1 click-ID lead for $161.92, 3.1% CTR, 66% impression share.
- **Boiler Replacement:** 1 click-ID lead from a single click, 86% impression share, 71% absolute-top.
- **The Boiler campaign overall** has by far the best ad relevance: 19% CTR, 59% absolute-top.

These fit the August finding that replacement and installation carry most of the pipeline value.

**Weakest:**
- **Heating Repair:** $406, or 33% of spend since Sept 24, for 15 clicks and 0 leads. CTR is 1.7%, and the campaign loses 39% of impressions to rank and 19% to budget.
- **Boiler Repair:** $242.87 on 6 clicks at $40.48 each, 0 leads.
- **Heating Installation:** 269 impressions and 1 click (0.4% CTR). Furnace Installation (62 impressions) and Heating Replacement (51) had none, which points to weak ad or query relevance.

### Device, click type, location, final URL (Sept 24–29, seven campaigns)

- **Device:**
  - Mobile: 35 of 42 clicks, $1,006.21, both conversions.
  - Desktop: 7 clicks, $207.86, 0 conversions.
  - Tablet: 0 clicks.
- **Click type:**
  - Headline clicks: 26 clicks, $798.97, 1 conversion.
  - Sitelinks: 7 clicks, $206.10, 1 conversion.
  - Location expansion: 8 clicks, $187.51, 0 conversions.
  - Calls: 1 click, $21.49, 0 conversions.
- **User location:**
  - Top spend: Bowie $183.09 (5 clicks), Mitchellville $119.53 (3 clicks, 1 conversion: the call), Linthicum Heights $117.70, Catonsville $91.70, Lansdowne $84.96 and Columbia $83.89.
  - The form lead came from Baltimore.
  - Annapolis had 169 impressions and 0 clicks.
- **Final URL:**
  - `/hvac-repair/`: $383.16, 13 clicks, 0 conversions.
  - `/gas-boiler-repair/`: $201.50, 5 clicks, 0 conversions.
  - `/hvac-replacement/`: $146.08, 4 clicks, 1 conversion.
  - `/heat-pump-installation/`: $78.42, 3 clicks, 0 conversions.
  - `/boiler-replacement/`: $76.10, 2 clicks, 1 conversion.
  - `/hvac-installation/`: 460 impressions, 1 click.
  - `/furnace-repair/`: 320 impressions, 1 click.
  - Main-site URLs took $175.16, **all on Sept 24 before the ad swap. None since.**

### Search terms

Raw terms stay on disk under the standing rule. These are aggregates only.

- 353 distinct terms since Sept 24.
- Visible terms cover only about 32% of spend. The rest is below Google's privacy threshold or comes from non-keyword clicks.
- Only 10 terms spent $20 or more, for $323.08 in total (11 clicks, 1 conversion).
- **By intent bucket:**
  - Replace/install: $89.30 (1 conversion)
  - Repair: $63.78
  - Other heating-service wording: $153.98
  - "service" wording: $28.85
  - Maintenance: $22.45 (1 click, in Heating System Inspection before its pause)
  - Out-of-scope: $28.58
- **No maintenance-intent search term has matched a Boiler or Heat Pump ad group,** so there is no existing maintenance leak into the core groups.

---

## B. Landing-page and destination QA

Method:
- Real Chromium, desktop and mobile, GET only.
- No form submitted and no call placed.
- No query string on the QA loads. The D7 probe used a unique non-UTM cache-buster with every third-party host blocked.

| URL | Result | Evidence |
|---|---|---|
| Boiler Repair `/gas-boiler-repair/` | **PASS** (site-wide defects) | HTTP 200, no redirect. H1 "Gas Boiler Repair in Severn, Severna Park & Columbia, MD". Every H2 and CTA is about gas boiler repair. Rendered phone is 705-6354 only. |
| Boiler Replacement `/boiler-replacement/` | **PASS with defect** | HTTP 200. H1 "Boiler Replacement in Central MD". **D4 still open:** FAQ H2 "Heat Pump Repair Questions". |
| Boiler Maintenance `/boiler-maintenance/` | **FAIL (D2 not fixed)** | Only the H1 and intro are maintenance. The H2s are "Request a Boiler Installation Assessment", "A Boiler Installation Planned Around Your Property", "Boiler Installation for Your Home", "Three Steps to Boiler Installation", "Boiler Installation Questions" and "Let's Discuss Your Boiler Installation". FAQ: "What affects the installation price?" CTA: "Request a Boiler Installation Assessment". Counts: "installation" 21 times, "maintenance" 4 times. |
| Heat Pump Maintenance `/heat-pump-maintenance/` | **CONDITIONAL PASS** | Details below. |

**Heat Pump Maintenance, what passes:**
- HTTP 200, no redirect. H1 "Heat Pump Maintenance in Central MD". The intro and top form ("Request Heat Pump Maintenance") are correct.
- The offer is a free quote, and Mon–Fri 8 a.m.–4 p.m. is stated.
- Every rendered `tel:` link dials 705-6354, and 761-0932 is never rendered.
- The form is `#gform_1`, which is registered in WhatConverts (`form_list`: 205016 `#gform_1`, 208722 `#gform_2`). GTM and the WhatConverts cookies are present.
- **No barred claims.** The FAQ says maintenance "does not guarantee that equipment will never fail". The testimonials are the site template.

**Heat Pump Maintenance, defects:**
- **D4, three times:**
  - H2 "Three Steps to Heat Pump **Repair**"
  - H2 "Heat Pump **Replacement** Questions"
  - The bottom form is titled "Request an **Installation** Assessment".

**Site-wide defects, same on all four pages. None are fixed:**

| Defect | Finding 2026-09-30 |
|---|---|
| D1 | Raw server HTML still contains 761-0932 two or three times per page. `/gas-boiler-repair/` still has a `tel:+14107610932` href. GTM corrects it in the browser. `tel:` hrefs are not E.164 (`tel:(410)%20705-6354`). |
| D5 | `form#gform_1` rendered 3 times per page, 55 duplicate element IDs. |
| D6 | "Tell us about your project (optional)*" is still marked required (`gfield_contains_required`, `aria-required=true`). |
| D7 | The server still fills the attribution fields: a unique-parameter request (cache MISS) echoed the `utm_content` marker into the HTML. The clean request that followed was a cache HIT with 0 of 51 hidden fields carrying a value, so no replay was observed. The fix is still open. |

---

## C. Exact proposed changes

### Plan 1: AMB-0930-HPM-BUDGET-1 · fingerprint `7472853C4EA9` · separate budget approval

| Campaign | Budget ID | Current | Proposed |
|---|---|---|---|
| 24268690038 Search \| NonBrand \| Heat Pump & Ductless Heating \| Central MD \| BOFU \| 2026-09 | 15887323562 | $15.00/day | **$30.00/day** |
| 24279798229 Search \| NonBrand \| Heating Maintenance & Inspection \| Central MD \| BOFU \| 2026-09 | 15887323565 | $45.00/day | **$30.00/day** |

- **Objects:** 2 budget updates. 0 created. No status, keyword, ad, URL or asset change.
- **Budget impact:**
  - Enabled daily total stays **$305.00**, a monthly maximum of $9,272 ($9,880 if the paused PMax pilot were ever enabled). Both are under $10,000.
  - The Heat Pump monthly ceiling goes from $456 to $912.
  - The Maintenance campaign serves nothing, so cutting it changes no delivery. **Real spend can rise by at most $456/month.**
  - The PMax launch path still fits: pause Maintenance (−$30), raise PMax $20 → $45, total $320, within $325.
- **Conversion impact:** none.
- **Reason:** gives Heat Pump Maintenance room without taking clicks from Heat Pump Repair, Installation or Replacement (see D and Phase 4).
- **This reopens the Sept 25 decision that kept Maintenance at a nominal $45 as the PMax donor.** It needs the owner's sign-off.

### Plan 2: AMB-0930-HPM-ENABLE-1 · fingerprint `90C7E29E61BA` · separate ENABLE approval after the Phase 6 readback

| # | Operation | Resource | Current | Proposed |
|---|---|---|---|---|
| 1 | Create label | MAINTENANCE_TEST | does not exist | created |
| 2 | Link label | ad group 204129717567 SKAG \| Heat Pump Maintenance | – | MAINTENANCE_TEST |
| 3 | Unlink label | 204129717567 ~ DEFERRED_BUDGET (22294514687) | linked | removed |
| 4 | Ad status | RSA 825863405664 | PAUSED | **ENABLED** |
| 5 | Ad status | RSA 825863405667 | PAUSED | **ENABLED** |

- **Campaign:** 24268690038 (ENABLED, unchanged).
- **Ad group:** 204129717567 (ENABLED, unchanged).
- **Keywords affected:** none. These 3 are already ENABLED and ELIGIBLE:
  - `heat pump maintenance` PHRASE (314713475)
  - `heat pump maintenance` EXACT (1460863200)
  - `heat pump tune up` EXACT (14273503331)
- **Existing ads:** the 2 above.
  - Both are APPROVED with no policy topics and AVERAGE ad strength.
  - Both point to `https://offer.ambientcoolingandheating.com/heat-pump-maintenance/`.
  - 15 headlines and 4 descriptions each. No barred claims.
- **New ads:** none.
- **Final URLs:** unchanged.
- **Sitelinks and assets:** none changed. The ad group inherits the campaign's assets:
  - Sitelinks: Heat Pump Repair, Installation and Replacement
  - 4 callouts, and the Services snippet
  - Call asset 415-9517
  - Business name
- **Objects:** created 1 label and 1 label link, removed 1 label link, updated 2 ads.
- **Budget impact:** none in this plan. It requires Plan 1 to be executed with a clean readback, and the script refuses otherwise.
- **Conversion impact:** no setting changes. New leads count through the existing Primary actions. The known call double count (Calls from ads plus WC Lead via enhanced conversions) is unchanged.
- **Stop-loss:** pause both ads if any of these happens:
  - $300 of maintenance spend with no click-ID lead
  - Heat Pump lost-IS (budget) above 10% over 7 complete days
  - Core Heat Pump impressions fall more than 30% while maintenance takes more than 30% of campaign spend
  - Any policy limit, or a page QA failure
- **Checkpoints:** day 2, 7 and 14.

### Boiler Maintenance: 0 operations

Held payload **AMB-0930-BM-HELD-PAYLOAD**, content hash `2C7D2C005624`. It is **not for approval.**

- **It contains 2 drafted RSAs.** They use only verified claims: free quote, Mon–Fri 8–4, service area, trained technicians.
  - Each has 15 headlines of 30 characters or fewer and 4 descriptions of 90 or fewer.
  - Paths: Boiler / Maintenance.
  - Each shares at most 2 generic headlines with the existing Boiler ads.
- **When D2 passes:**
  - Create the RSAs PAUSED.
  - Enable `boiler maintenance` PHRASE + EXACT.
  - Keep `boiler service` PHRASE/EXACT paused, because its intent is mixed with repair.
  - Add an `oil` PHRASE ad-group negative (Boiler Repair already has one).
  - Settle a budget first.
  - Re-run QA and issue a new fingerprint.

### Boiler Repair and Boiler Replacement: 0 operations

Read-only comparison only. Both destinations match fresh account data, so no separate work order is needed.

---

## D. Redundancy check

**Reused as they are:**
- Ad group 204129717567 and its RSAs 825863405664 and 825863405667.
- The 3 keywords.
- 10 ad-group routing negatives: installation, repair, boiler, furnace, geothermal, thermostat, installers, replacement, ductless, mini split.
- Campaign assets on 24268690038: 3 offer-page sitelinks, 4 callouts, snippet 424717815118, call asset 424764337810, business name 80516971145.
- Shared negative lists 12249470554 and 12252013691.
- Schedule (Mon–Fri 08–16, 5 rows), 75 Presence targets, and the customer-level conversion goals.

**Created:** only the MAINTENANCE_TEST label and its link. A no-duplicate check confirmed no label of that name exists. No ad, keyword, sitelink, callout, snippet, call asset, ad group, campaign or budget is created.

**Deliberately left paused:**
- **Sitelink 424481133551 "Heat Pump Maintenance".** It is linked at campaign level, so it would show under Heat Pump Repair, Installation and Replacement ads and divert higher-value clicks to the maintenance page. It also duplicates the maintenance ads' own final URL.
- **Callout 422577777442 "Repair and Maintenance"** on the Heat Pump campaign. It is not needed.

**Boiler:** nothing created. The Boiler Repair, Gas Boiler Repair and Boiler Replacement ads are untouched.

---

## E. Validation and fingerprints

| Check | Result |
|---|---|
| Fresh identity gate: exact name and child ID, not a manager, not a test account, USD, America/New_York, both manager links ACTIVE | PASS, 8/8 (run three times) |
| Work orders validated with `gm_gsa.work_orders.validate_work_order` and `schemas/work-order.schema.json`: main, heating transition, Heat Pump Maintenance, Boiler Maintenance | 0 errors |
| `assert_target_matches`, `assert_no_embedded_secrets` | PASS |
| Heat Pump Maintenance ads: APPROVED, no policy topics, canonical URL, character limits, barred-claim scan | PASS |
| Enabled RSAs in the ad group after the change | 2 (cap is 3) |
| Keywords: 3 Phrase/Exact, all eligible, 0 Broad | PASS |
| Negative reachability: 169 Heat Pump and 254 Boiler probes against the account list (269), campaign negatives (2 and 1,133), both shared lists (78 and 491) and ad-group negatives | 0 unintended blocks. The only block is the intended "…maintenance and repair" routing. |
| Landing-page gate | Heat Pump Maintenance PASS_WITH_DEFECTS. Boiler Maintenance FAIL_D2. |
| Budget math (daily × 30.4) | $305 → $9,272; $9,880 including PMax. Under $10,000. |
| Google validate-only | BUDGET-1 VALIDATE_OK. ENABLE-1 VALIDATE_OK. |
| Determinism: rebuilt twice from fresh data | identical fingerprints |
| Phase 6 read-only readback of the current paused state | PASS |

| Plan | Fingerprint | Operations | Approval |
|---|---|---|---|
| AMB-0930-HPM-BUDGET-1 | `7472853C4EA9` | 2 | Budget approval, now |
| AMB-0930-HPM-ENABLE-1 | `90C7E29E61BA` | 5 | ENABLE approval, only after the Phase 6 QA report |

---

## Phase 4: budget and cannibalization

**Budgets now:**

| Budget | Amount |
|---|---|
| Enabled daily total | $305: Repair 85, Install/Replace 60, Boiler 45, Heat Pump 15, Thermostat 15, Maintenance 45, Geothermal 20, Commercial 20 |
| Actually spendable (campaigns with enabled ads) | **$220/day** |
| Idle (no enabled ads) | $85/day |

**Spend:**
- September to date (Sept 1–29, all campaigns): **$3,018.41**.
- September should close around $3.3k–$3.5k. The month ends today, so the $10,000 cap is not at risk.

**October pacing at the current rate** (Sept 24–29 spend per serving day × 22 weekdays, against each campaign's daily × 30.4 ceiling):

| Campaign | Pace | Ceiling | Utilization |
|---|---|---|---|
| Repair | $2,585 | $2,584 | **100%** |
| Install/Replace | $1,137 | $1,824 | 62% |
| Boiler | $1,835 | $1,368 | **134%, will be capped** |
| Heat Pump | $431 | $456 | **95%** |
| Thermostat | $130 | $456 | 28% |

Expected October heating spend is about $5.7k–$6.7k. The enabled maximum is $9,272.

**Cannibalization:**
- **Query routing is clean.** Every Boiler and Heat Pump repair, installation and replacement group already excludes `maintenance`, `tune up` and `inspection`, and both maintenance groups exclude repair, replacement and installation. No maintenance search term has matched a core group.
- **The risk is budget.** Maximize Clicks spends each campaign's budget on whatever clicks it can get, and the Heat Pump campaign buys one $19–$30 click per serving day.
  - Heat pump maintenance demand is about **70 searches/month**, against Repair 140, Installation 50 and Replacement 10 (Planner, 10-city sample). That is roughly a quarter of the campaign's demand.
  - Expect about 2–4 maintenance clicks a month (about $50–$100). At $15/day those clicks would come out of core Heat Pump clicks.
  - At $30/day, expected Heat Pump spend (about $430 core plus $50–$100 maintenance) uses about 53–58% of the new ceiling, so there is no displacement.
- **Boiler Maintenance** demand is small: about 10 searches/month. History: 28 clicks, $2,102 and 4 conversions at a $75 CPC in the uncapped period. Boiler Services is already above its allowance, so when D2 passes Boiler Maintenance needs its own budget decision.

**Value evidence:**
- Last heating season: 8 paid-labeled maintenance, tune-up or inspection leads. Quotable: 0 Yes, 1 No, 7 unset.
- Heat pump maintenance all-time: 4 clicks, $183.63, 0 conversions.
- Maintenance is lower-ticket work. Treat it as a monitored test, not a growth lever.

---

## Open items (not part of these plans)

1. **Developer fixes.** D2 blocks Boiler Maintenance. D4 is needed on the Heat Pump Maintenance and Boiler Replacement pages. D1, D5, D6 and D7 remain open site-wide.
2. **Lead marking.** Ask Ambient to mark the two Sept 28 leads Quotable Yes or No. This is still the only qualification evidence for heating.
3. **Idle budget.** Even after Plan 1, $70/day stays idle (Maintenance $30, Geothermal $20, Commercial $20), while Repair is at its ceiling and Boiler is above it. A separate budget plan moving idle budget to Repair and Boiler is the higher-value follow-up.
4. **Callout wording.** The Boiler campaign callout "Prompt, Reliable Service" is vague responsiveness language. Review it under a separate work order.

## Next approvals

1. `APPROVE AMB-0930-HPM-BUDGET-1 7472853C4EA9 2 operations FOR 2401959466`
   - Execute, then read back.
   - Then run Phase 6: a read-only readback of the Heat Pump Maintenance resources and a fresh page QA.
2. After the Phase 6 QA report: `ENABLE AMB-0930-HPM-ENABLE-1 90C7E29E61BA 5 operations FOR 2401959466`

Evidence files:
- `clients/ambient-cooling-heating/snapshots/maint-eval-2026-09-30.json`
- `clients/ambient-cooling-heating/snapshots/maint-lp-qa-2026-09-30.json`
- `clients/ambient-cooling-heating/snapshots/maint-neg-reach-2026-09-30.json`
- `clients/ambient-cooling-heating/plans/AMB-0930-HPM-BUDGET-1.json`
- `clients/ambient-cooling-heating/plans/AMB-0930-HPM-ENABLE-1.json`
- `clients/ambient-cooling-heating/plans/AMB-0930-BM-HELD-PAYLOAD.json`
- Scripts: `scripts/ambient_0930_maint_eval_snapshot.py`, `ambient_0930_maint_lp_qa.py`, `ambient_0930_maint_neg_reach.py`, `ambient_0930_hpm_plans.py`
