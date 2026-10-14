# 01 — Work order, source ledger and fresh snapshot

**Apogee Lawns LLC - Live · 8164626278 · Permanent Christmas light installation** · similar-local-service
Run: 2026-09-28, account time zone **America/Chicago (verified)**. Snapshot read at **2026-09-28 19:45 UTC = 14:45 CDT**.
Modes: READ for every connected system, DRAFT for local files. **External mutations executed: 0.**

## Work order and gates (actual validator output)

| Check | Command / source | Result |
|---|---|---|
| Task work order (new, non-overwriting) | `scripts/validate_work_order.py clients/apogee-lawns/work-orders/work-order-low-volume-audit-2026-09-28.yaml --client clients/apogee-lawns/client.yaml` | `Work order: PASS \| Apogee Lawns LLC - Live \| 8164626278 \| similar-local-service \| Permanent Christmas light installation` · exit 0 |
| Canonical work order (unchanged) | same script on `clients/apogee-lawns/work-order.yaml` | same PASS line · exit 0 |
| JSON schema | `schemas/work-order.schema.json` (jsonschema Draft 2020-12) | 0 errors on both files |
| Scope approval | reused from `work-order.yaml`: approved true, approver Walter, reason recorded 2026-09-16 | present; not re-requested, not manufactured |
| Fresh identity | `customer` + `customer_client` under manager 3373711342 | name and ID exact, manager=false, test=false, ENABLED, America/Chicago — **PASS** |
| Account clock | `segments.date DURING YESTERDAY / TODAY` | yesterday = 2026-09-27, today = 2026-09-28 (partial) |

## Source ledger

Types: **FRESH** = read in this run · **RECEIPT** = historical repo receipt · **PRIOR** = earlier assertion (report/memory) · **DOC** = official documentation · **INFERENCE** = my reasoning.

| # | Finding | Type | Source / query / observation | Timestamp | Limitation |
|---|---|---|---|---|---|
| L1 | Campaign 24257151015 ENABLED / SERVING / primary LEARNING (`BIDDING_STRATEGY_LEARNING` only) | FRESH | `campaign` query, snapshot JSON | 19:45 UTC | none |
| L2 | Enabled 2026-09-21 09:04:56 CT, PAUSED→ENABLED, `GOOGLE_ADS_WEB_CLIENT` | FRESH | `change_event` old/new `campaign.status` | 19:45 UTC | agency login is shared: the person is not identified |
| L3 | Created PAUSED 2026-09-17 12:31:52 by API (CAMP-I) | FRESH + RECEIPT | `change_event`; `receipts/2026-09-17-campi-*.json` | — | — |
| L4 | Maximize Clicks (`TARGET_SPEND`), CPC ceiling 8,000,000 micros; budget 15884926233 = 16,440,000 micros, STANDARD, not shared, reference_count 1 | FRESH | `campaign`, `campaign_budget` | 19:45 UTC | — |
| L5 | Google Search only; partners, display, partner-search off; PRESENCE positive and negative; AI Max absent; TEXT_ASSET_AUTOMATION OPTED_OUT; no broad-match setting; no DSA | FRESH | `campaign` | 19:45 UTC | `url_expansion_opt_out` is not selectable in v25 |
| L6 | **TABLET device criterion 24257151015~30002 carries an explicit `bid_modifier` 0.0 (−100%)**; ad-group rows 200347713516~30002 and 200347713556~30002 also report explicit 0.0; desktop/mobile unset | FRESH | `campaign_criterion`, `ad_group_bid_modifier`, `_pb.HasField('bid_modifier')` | 19:45 UTC | change_event for the 09-25 edit has an empty payload, so the prior value is inferred from delivery (tablet impression on 09-23, none after 09-25) |
| L7 | 14 LOCATION (all ENABLED, IDs equal the approved list), 1 LANGUAGE (English), 75 negative KEYWORD, 0 AD_SCHEDULE, 0 audience/demographic exclusions | FRESH | `campaign_criterion`; ad groups' demographic restrictions are all `bid_only: true` (observation) | 19:45 UTC | — |
| L8 | 0 ad-group negatives; 7 shared negative lists, **0 attached** (`campaign_shared_set` 0 rows, all `reference_count` 0); account level = PARKED_DOMAIN content label only | FRESH | `ad_group_criterion`, `shared_set`, `campaign_shared_set`, `customer_negative_criterion` | 19:45 UTC | — |
| L9 | 4 RSAs APPROVED / ELIGIBLE, Ad Strength AVERAGE, final URL `https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/`; 6 callouts + 1 snippet + 1 call asset APPROVED; 0 ad-group or customer assets | FRESH | `ad_group_ad`, `campaign_asset`, `ad_group_asset`, `customer_asset` | 19:45 UTC | — |
| L10 | Call asset 422649064971 = 402-526-5754, `USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION` → 7773013199; schedule Mon–Fri 08:00–17:00, Sat 08:00–12:00, Sunday absent | FRESH | `campaign_asset` + `asset.call_asset` | 19:45 UTC | routing (who answers) not testable without a call |
| L11 | Conversions: 7772803337 form (Primary), 7773013199 ads calls (Primary), 7773043879 website calls (Secondary, `include_in_conversions_metric` false); goal config CAMPAIGN; campaign goals form + ads-call biddable, website-call not; 0 custom goals | FRESH | `conversion_action`, goal resources | 19:45 UTC | — |
| L12 | Account call reporting points at `conversionActions/179`; no conversion_action 179 exists in the child under any status | FRESH | `customer.call_reporting_setting`, `conversion_action WHERE id = 179` → 0 rows | 19:45 UTC | absence of a row is not proof of a "dead" pointer; its effective scope is nil here (see 05) |
| L13 | Billing setup 8587299012 APPROVED since 2026-09-16 19:01:11; account budget INFINITE; served $18.69 | FRESH | `billing_setup`, `account_budget` | 19:45 UTC | advertiser verification status is not exposed by the API |
| L14 | Delivery, completed days 09-17..09-27 (serving began 09-21): 52 impr, 3 clicks, $18.69, CPC $6.23, CTR 5.8%, 0 conv, 0 all conv | FRESH | campaign query, no date segment (Google's own aggregate) | 19:45 UTC | 3 clicks: no rate is statistically meaningful |
| L15 | Aggregate IS (same window): Search IS 72.2%, lost-budget 18.5%, lost-rank 9.3%, top IS 55.6%, abs-top 16.7%, lost-top-budget 25.9%, lost-top-rank 18.5%, **click share 19.6%**, exact-match IS 69.2% | FRESH | aggregate query (not an average of daily %) | 19:45 UTC | values < 10% are reported as 0.0999; tiny denominators |
| L16 | Partial day 09-28: 13 impr, 0 clicks | FRESH | `DURING TODAY` | 19:45 UTC | provisional; same-day figures are restated |
| L17 | Search-term report covers 42 of 65 impressions and **0 of 3 clicks** | FRESH | `search_term_view` vs campaign totals | 19:45 UTC | raw terms stored locally only |
| L18 | Live GTM = **version 3** "Add Conversion Linker tag", created+published 09/28/2026; version 2 "Apogee \| PPC Tracking \| 2026-09" created+published **09/17/2026**; both by the agency login | FRESH | GTM UI Versions tab (read-only) + public `gtm.js` `Last-Modified: 2026-09-28 19:38:53 GMT` | 19:57 UTC | GTM shows dates, not times, in the list |
| L19 | Repo receipts for GTM-K/GTM-P say "versions 0, publishes 0" | RECEIPT | `receipts/2026-09-17-gtm*-receipt.json` | 09-17 | superseded by L18; the publication receipt is **missing evidence**, not proof of unauthorized action |
| L20 | `/thank-you/permanent-christmas-lights/` does not exist; `/thank-you/` (page 1702) is published | FRESH | public WordPress REST API `wp/v2/pages` from the browser | 20:00 UTC | an unpublished draft would not appear |
| L21 | Direct navigation to the approved thank-you URL lands on the LP via WordPress's closest-slug redirect (a nonexistent slug 404s; `/permanent-christmas/` also redirects to the LP) | FRESH | browser fetch probes | 20:00 UTC | redirect status code not visible to fetch |
| L22 | `apg_permanent_lights_lead`, `lead_id` and any `dataLayer.push` appear 0 times on the LP, `/thank-you/`, inline scripts and 28 same-origin scripts | FRESH | browser fetch + scan | 20:00 UTC | a server-side confirmation hook after a real submission cannot be seen without submitting |
| L23 | WhatConverts `wc_swap` = replacement 402-783-8482 for source 402-202-7261 (entry 233469); no number mutation during 25 s; rendered number only 402-526-5754 | FRESH | runtime cookie + MutationObserver | 19:58 UTC | Google forwarding-number swap for ad visitors NOT TESTED (needs a real ad click) |
| L24 | WhatConverts 09-10..09-28: 28 leads (17 calls, 9 texts, 2 forms); numbers 402-256-7520 "LSA Traffic", 402-383-2673 "GBP Traffic"; 0 leads on 402-526-5754 in default, duplicate and spam views; 0 leads with a GCLID; 2 GF1 forms from the paid LP on 09-28 at 12:41 and 14:01 CDT, source `(direct)` | FRESH | WhatConverts API v1, aggregates only | 20:05 UTC | WhatConverts tracking-number inventory and integrations are not exposed by API v1 |
| L25 | Planner (approved area, 10 of 14 geos): `permanent christmas lights` avg 90; Sep/Oct/Nov/Dec 2025 = 50/140/480/170; top-of-page $4.66–$13.76 | FRESH | `GenerateKeywordHistoricalMetrics` | 19:50:31 UTC | one season of history; rounded buckets; 10-geo cap |
| L26 | Forecasts 2026-09-29..12-20 (S0 55.5 clicks / $266.57 etc.) | FRESH | `GenerateKeywordForecastMetrics`, settings in `2026-09-28b-forecasts.json` | 19:54:00–19:57:05 UTC (21 calls) | tool cannot model negatives, tablet exclusion, network or ad-group splits |
| L27 | Omaha is EXCLUDED, "settled — not to be reopened on search volume or website wording" | RECEIPT | `work-order.yaml` `location_decision_2026_09_16` | 09-16 | — |
| L28 | Apogee is an EverLights certified dealer (first-party site) | PRIOR | `READ-ONLY-PREFLIGHT-2026-09-16.md` §7 | 09-16 | the ad brief bars brand wording pending client confirmation |
| L29 | Budget-lost IS on zero-spend days is not a hard budget cap | INFERENCE | L14/L15 daily rows; forecast budget sensitivity | — | mechanism unverified |
| L30 | `change_status` shows CAMPAIGN + both AD_GROUPs CHANGED 2026-09-28 11:47:23 CT and CAMPAIGN_BUDGET CHANGED 02:33:58 CT; `change_event` has no rows for either | FRESH | `change_status`, `change_event` | 19:45–19:55 UTC | **what changed is unverified**; every field read matches the 09-17 intended values; change_event lags by hours |

## Snapshot files (sanitized, no PII)

- `reports/apogee-lawns/evidence/2026-09-28b-snapshot.json` — full structured read (0 query errors after two unsupported fields were dropped: `ad_group_criterion.policy_summary.approval_status`, `campaign_criterion.location_group.feed`).
- `…/2026-09-28b-search-terms-RAW.json` — raw search terms, **never printed**; 22 daily rows, 14 distinct terms.
- `…/2026-09-28b-planner.json`, `…-planner-ideas.json`, `…-forecasts.json`, `…-negative-corpus-test.json`, `…-phrase-intent-test.json`, `…-search-term-coverage.json`, `…-gtm-published-v2-v3.json`, `…-whatconverts-aggregates.json`.
- Earlier run A evidence (`2026-09-28-*.json`) is preserved unchanged.

## Stale client-profile fields (recorded, not edited)

`client.yaml` still says: landing page 404, no WhatConverts, GTM not installed, Forminator form, no Terms page. All are now false for `offer.apogeelawns.com` (Gravity Forms, GTM v3 live, WhatConverts live, Terms page 17395 published). The profile is left untouched; the correction is proposed in `07_proposed_change_manifest.yaml`.
