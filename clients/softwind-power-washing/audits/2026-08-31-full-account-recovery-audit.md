# SOFTWIND POWER WASHING — FULL ACCOUNT RECOVERY AUDIT

**Generated:** 2026-08-31 10:21:20 America/New_York (account-local)
**Account:** Softwind Power Washing - Live · `1521725229` · MCC `3373711342`
**Service:** Power Washing · Vertical `similar-local-service` (scope approved, Walter Correa)
**Mode:** READ + DRAFT — **zero Google Ads mutations**

Evidence files, all written fresh this run and none overwriting a previous snapshot:

| File | Contents |
|---|---|
| `snapshots/forensic-structure-2026-08-31T102120.json` | 2 campaigns, 30 ad groups, 214 keywords, 54 ads, 426 assets, 446 campaign criteria, 4 conversion actions |
| `snapshots/forensic-performance-2026-08-31T102242.json` | daily / device / hour / DOW / geo / demographic / audience / click-type / search-term / call-log segmentation |
| `snapshots/forensic-changes-2026-08-31T102326.json` | 706 change events, 1,244 change-status rows |
| `snapshots/forensic-landing-pages-2026-08-31.json` | 11 URLs × desktop and mobile, real Chromium, GCLID test |
| `snapshots/forensic-demand-2026-08-31T103247.json` | 2,968 Keyword Planner ideas, live 80-target footprint |
| `snapshots/forensic-audiences-2026-08-31.json` | resolved user lists and user-interest segment IDs |
| `snapshots/geo-names-2026-08-31.json` | canonical names for all 81 geo criteria |
| `snapshots/forensic-auction-insights-2026-08-31.json` | the PERMISSION_DENIED record |

---

> ### CONTINUATION RESTATEMENT — 2026-08-31 16:40 America/New_York
>
> This report was written against the **10:21 audit snapshot**. A continuation drift check at
> **16:40** found that **Google retroactively invalidated four of the five clicks** recorded
> that morning on the query `power washing services` and **credited back $117.28**. Those four
> clicks moved into the invalid-clicks column.
>
> | | Audit snapshot 10:21 | Current live 16:40 |
> |---|---:|---:|
> | Impressions | 246 | **282** |
> | Billable clicks | 22 | **18** |
> | Spend | $713.15 | **$595.87** |
> | Average CPC | $32.42 | **$33.10** |
> | Invalid clicks | 60 | **73** |
> | Invalid share of raw clicks | 73.2% | **80.2%** |
> | Conversions | 0 | **0** |
>
> **Every other day in the ledger is byte-identical.** The reversal is isolated to the
> 2026-08-31 event. **No conclusion in this report is weakened by it — the traffic-quality
> finding is now confirmed by Google's own filtering**, and the CPC finding sharpens: the five
> post-ceiling billable clicks span **$29.04–$29.72**, a $0.68 range under a $30.00 cap.
>
> Figures below are the 10:21 audit snapshot unless marked otherwise. Where a decision depends
> on the corrected numbers, PLAN-R3 has been restated against the 16:40 ledger.

---

## 1. Identity gate — PASS

| Check | Observed | Required | Result |
|---|---|---|---|
| `customer.descriptive_name` | `Softwind Power Washing - Live` | exact | PASS |
| `customer.id` | `1521725229` | exact | PASS |
| `- live` marker | present | required | PASS (identifies a candidate; never authorises) |
| `customer.manager` | `false` | false | PASS |
| `customer.test_account` | `false` | false | PASS |
| `customer.status` | `ENABLED` | — | PASS |
| Currency | `USD` | — | PASS |
| Time zone | `America/New_York` | expected | PASS |
| Manager link (level 1) | `3373711342` Green Marketing | expected MCC | PASS |
| Work order vs client profile | `validate_work_order.py` → PASS | — | PASS |
| Work order mode | `read` | matches this run | PASS |
| Vertical | `similar-local-service`, `scope_approval.approved: true`, approver Walter Correa, rationale present | required | PASS |

**Account-level settings:** auto-tagging `true` · conversion tracking ID `18369652705` ·
`CONVERSION_TRACKING_MANAGED_BY_SELF` · enhanced conversions for leads `false` ·
tracking URL template empty · final URL suffix empty · optimization score 88.2%.

**Billing:** two `account_budget` rows, both `APPROVED` with `INFINITE` spending limit;
`amount_served` $648.77 on the active one. There is no readable customer-level daily spending
limit field in the API, so a UI-only cap cannot be ruled out — but Lost IS (budget) would
expose one and it is effectively zero.

---

## 2. Spend reconciliation — the brief's ~$2,000 does not match this account

| Source | Audit snapshot 10:21 | Current live 16:40 |
|---|---:|---:|
| `FROM customer` segmented by date, 2026-07-01 → 2026-08-31 | **$713.15** | **$595.87** |
| Campaign A `24103511039` all-time | $403.09 | $403.09 |
| Campaign B `24145053510` all-time | $310.06 | **$192.78** |
| A + B | **$713.15** ✓ | **$595.87** ✓ |
| `account_budget.amount_served` (billing, lags reporting) | $648.77 | — |

The $117.28 difference is entirely campaign B, and entirely the 2026-08-31 click reversal.
Campaign A is unchanged to the cent.

The account has never delivered outside August 2026 — the first impression is 2026-08-05, and
a July-inclusive query returns no July rows.

**Most likely reconciliation of "approximately $2,000":** this account ($595.87 corrected,
$713.15 at the audit snapshot) plus the sibling **Softwind Landscape & Masonry** `2429758629`,
whose local record shows $1,163.22 of all-time zero-converting spend → **$1,759.09** corrected,
$1,876.37 uncorrected. Softwind is one company across two child
accounts with deliberately mutually exclusive scope. **This is an inference.** The sibling sits
under its own work order and was not read in this run; confirming it requires a separate
client gate.

---

## 3. Launch chronology — exact timestamps

All timestamps are `change_event.change_date_time` in **account-local** time. Verified against
a known anchor: the negative-keyword rollout receipt records `started: 2026-08-30T084204` (host
ET) and `change_event` returns `2026-08-30 08:42` — an exact match, so `change_event` is
account-local, not UTC.

| When | Event | Via |
|---|---|---|
| 2026-08-04 09:22:12 | Campaign **Power Washing** `24103511039` created **and enabled** | web client |
| 2026-08-04 13:16:57 | Call asset `403335872180` created — (631) 502-7946 | web client |
| 2026-08-04 13:17:11 | First RSA updated; first campaign call-asset link | web client |
| 2026-08-04 15:16:52 | `geo_target_type_setting.positive_geo_target_type` changed → PRESENCE | web client |
| 2026-08-04 19:23:04 | `manual_cpc.enhanced_cpc_enabled` changed | web client |
| 2026-08-04 19:26–19:27 | 4 account-level sitelinks, 4 callouts, 1 structured snippet created | web client |
| **2026-08-05** | **FIRST IMPRESSION** (3 impressions, $0.00) | — |
| 2026-08-06 13:04 | Three ad groups status-changed | web client |
| 2026-08-06 21:18:57 | Call asset `ad_schedule_targets` set | web client |
| 2026-08-07 16:08:18 | **CPC ceiling set to $5.00** | web client |
| 2026-08-07 (per prior audit) | Sunday daypart deleted | web client |
| 2026-08-07 → 08-16 | **Twelve consecutive days, zero clicks** under the $5.00 cap | — |
| 2026-08-16 23:42:44 | **CPC ceiling removed** — uncapped | web client |
| **2026-08-17** | **FIRST CLICK and FIRST SPEND — $5.71**, day 13 | — |
| 2026-08-18 09:24:13 | Campaign **Power Washing #2** `24145053510` + budget created | web client |
| 2026-08-18 09:28:21 | Campaign B **enabled** — four minutes after creation | web client |
| 2026-08-18 09:34:01 / 09:34:13 | Both budgets set to $41.11 | web client |
| 2026-08-26 17:49:03 | **PLAN-J2A: geo expansion**, +72 locations per campaign, 144 mutations | API |
| 2026-08-26 18:00:31 | Campaign A budget **$41.11 → $333.33** (PLAN-I1C, month-end spend push) | API |
| 2026-08-26 | PLAN-J2B: Connecticut `21139` excluded on both campaigns | API |
| 2026-08-27 12:25:35 | **PLAN-K1: CPC ceiling $30.00 on BOTH campaigns** | API |
| 2026-08-27 | PLAN-H: 4 sitelinks created, repointed to `offer.softwindli.com` | API |
| 2026-08-30 08:42 | Portfolio negative rollout: **170 campaign negatives created** | API |
| **2026-08-31 09:39:41** | **Campaign A budget $333.33 → $41.50, BY HAND in the UI** | **web client** |
| 2026-08-31 10:21:20 | This audit snapshot | API (read-only) |
| — | **FIRST CONVERSION: never** | — |

**The 09:39 budget change is the reason the local record and the live account disagreed until
this snapshot.** Nothing in this repository authorised it. It is recorded as observed state,
not as drift to be reverted — and with $146.60 already spent by 09:00, it was the right instinct.

---

## 4. Required date windows

| # | Window | Impr | Clicks | Cost | CPC | CTR |
|---|---|---:|---:|---:|---:|---:|
| A | All time since first impression (08-05 → 08-31) | 246 | 22 | $713.15 | $32.42 | 8.94% |
| B | Post-revamp / campaign B live (08-18 → 08-31) | 219 | 21 | $707.44 | $33.69 | 9.59% |
| C | August 1–31 2026 (identical to A) | 246 | 22 | $713.15 | $32.42 | 8.94% |
| D | Post geo + budget change (08-26 → 08-31) | 143 | 16 | $541.98 | $33.87 | 11.19% |
| D′ | **Same, completed days only (08-26 → 08-30)** | 141 | 11 | $395.38 | $35.94 | 7.80% |
| E | Last 7 completed days (08-24 → 08-30) | 188 | 15 | $538.71 | $35.91 | 7.98% |
| F | Last 3 completed days (08-28 → 08-30) | 49 | 4 | $117.90 | $29.48 | 8.16% |
| G | **Current partial day (08-31 to 10:21)** | **2** | **5** | **$146.60** | $29.32 | *n/a* |
| H1 | Pre-CPC-ceiling (08-05 → 08-27) | 195 | 13 | $448.65 | $34.51 | 6.67% |
| H2 | Post-CPC-ceiling (08-28 → 08-31) | 51 | 9 | $264.50 | $29.39 | 17.65% |

**Window G is a partial day and must never be merged into a completed-day average.** Its
"CTR" of 250% is a same-day reporting artefact — five clicks are recorded against two
impressions because click processing runs ahead of impression processing. Window D′ is the
honest post-change read.

**2026-08-30 (Sunday) returned zero rows.** The API omits all-zero date rows, so an absent day
is real zero delivery. Sunday has had no daypart since 2026-08-07 and has never delivered.

### Complete daily ledger

| Date | Impr | Clicks | Cost | CPC | CTR | Conv | Invalid clicks |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08-05 | 3 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-06 | 1 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-07 | 1 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-08 | 4 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-10 | 1 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-11 | 4 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-12 | 4 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-13 | 2 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-15 | 3 | 0 | $0.00 | — | 0.00% | 0 | 0 |
| 08-17 | 4 | 1 | $5.71 | $5.71 | 25.00% | 0 | 0 |
| 08-18 | 3 | 0 | $0.00 | — | 0.00% | 0 | 1 |
| 08-19 | 12 | 1 | $22.13 | $22.13 | 8.33% | 0 | 2 |
| 08-20 | 8 | 0 | $0.00 | — | 0.00% | 0 | 1 |
| 08-21 | 4 | 0 | $0.00 | — | 0.00% | 0 | 3 |
| 08-22 | 2 | 0 | $0.00 | — | 0.00% | 0 | 7 |
| 08-24 | 26 | 1 | $22.11 | $22.11 | 3.85% | 0 | 12 |
| 08-25 | 21 | 3 | $121.22 | $40.41 | 14.29% | 0 | 4 |
| 08-26 | 30 | 1 | $82.22 | $82.22 | 3.33% | 0 | 9 |
| 08-27 | 62 | 6 | $195.26 | $32.54 | 9.68% | 0 | 2 |
| 08-28 | 19 | 2 | $59.14 | $29.57 | 10.53% | 0 | 10 |
| 08-29 | 30 | 2 | $58.76 | $29.38 | 6.67% | 0 | 9 |
| 08-30 | *(Sunday — no delivery, dark by schedule)* | | | | | | |
| 08-31 | 2 | 5 | $146.60 | $29.32 | *partial* | 0 | 0 |
| **Total (10:21 audit snapshot)** | **246** | **22** | **$713.15** | **$32.42** | **8.94%** | **0** | **60** |
| **Total (16:40 corrected)** | **282** | **18** | **$595.87** | **$33.10** | **6.38%** | **0** | **73** |

**Nine of 21 delivering days spent nothing.** Days 08-09, 08-14, 08-16, 08-23 and 08-30 had no
delivery at all.

---

## 5. Account-level report

| Metric | 10:21 audit snapshot | **16:40 corrected** |
|---|---:|---:|
| Spend | $713.15 | **$595.87** |
| Impressions | 246 | **282** |
| Clicks | 22 | **18** |
| CTR | 8.94% | **6.38%** |
| Average CPC | $32.42 | **$33.10** |
| Conversions (`metrics.conversions`) | 0.00 | **0.00** |
| All conversions (`metrics.all_conversions`) | 0.00 | **0.00** |
| Conversion rate | 0.00% | **0.00%** |
| Cost per conversion | undefined | **undefined** |
| Conversion value | $0.00 (all three lead actions use `default_value 0.0` with `always_use_default_value true` — value is structurally always zero) |
| Qualified WhatConverts leads | **UNKNOWN — no export supplied** |
| Qualified calls | 0 recorded · `call_view` returns zero rows for the entire retained log |
| Qualified forms | 0 recorded |
| Search Impression Share (impression-weighted) | A 61.24% · B 75.34% | **A 53.55% · B 66.30%** |
| Search Lost IS — budget | A 2.30% · B 2.27% | **A 2.01% · B 2.00%** (0.00% on 24 of 30 delivering campaign-days) |
| Search Lost IS — rank | A 35.97% · B 20.12% | **A 31.45% · B 17.70%** |
| Search top impression share | A 42.55% · B 70.98% | — |
| Search absolute-top impression share | A 35.86% · B 51.89% | **A 31.35% · B 45.67%** |
| **Invalid clicks** | **60** | **73** |
| **Invalid click share of raw clicks** | **73.2%** (60 of 82) | **80.2%** (73 of 91) |

**Reconciliation of Google Ads conversions with WhatConverts: NOT POSSIBLE.** A
repository-wide search found no WhatConverts export for this client. **Zero Google Ads
conversions does not mean zero real leads** — see §11.

---

## 6. Campaign-level report

| | Power Washing | Power Washing #2 |
|---|---|---|
| Campaign ID | `24103511039` | `24145053510` |
| Status / serving | ENABLED / SERVING | ENABLED / SERVING |
| Primary status | **ELIGIBLE** (no reasons) | **LEARNING** (`BIDDING_STRATEGY_LEARNING`) |
| Created | 2026-08-04 09:22:12 | 2026-08-18 09:24:13 |
| Daily budget | **$41.50** (budget `15764226923`) | $41.11 (budget `15802443075`) |
| Bidding strategy | TARGET_SPEND (Maximize Clicks) | TARGET_SPEND (Maximize Clicks) |
| **CPC ceiling** | **$30.00** | **$30.00** |
| Bidding system status | ENABLED | `LEARNING_SETTING_CHANGE` |
| Biddable conversion goals | PHONE_CALL_LEAD/WEBSITE · PHONE_CALL_LEAD/CALL_FROM_ADS · SUBMIT_LEAD_FORM/WEBSITE | same three |
| Non-biddable goal | GET_DIRECTIONS/GOOGLE_HOSTED | same |
| Locations targeted | 80 | 80 |
| Location exclusions | 1 (Connecticut `21139`) | 1 (Connecticut `21139`) |
| Location option | PRESENCE (positive **and** negative) | PRESENCE |
| Ad schedule | Mon–Sat 08:00–18:00, 6 dayparts | Mon–Sat 08:00–18:00, 6 dayparts |
| Search Partners | **OFF** | **OFF** |
| Display Network | **OFF** | **OFF** |
| AI Max | **OFF** | **OFF** |
| Final URL expansion | `FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION` = **OPTED_OUT** | OPTED_OUT |
| Auto-created assets | `TEXT_ASSET_AUTOMATION` = **OPTED_OUT** | OPTED_OUT |
| Audience targeting mode | `AUDIENCE` `bid_only: true` — **observation**, with zero audiences attached | same |
| Demographic exclusions | **NONE** (zero GENDER / AGE_RANGE / INCOME_RANGE criteria) | **NONE** |
| Language | `languageConstants/1000` (English) | same |
| IP blocks | **0** — ClickCease is not syncing to this campaign | **0** |
| Tracking template / suffix / custom params | empty | empty |
| Impressions | 202 | 44 |
| Clicks | 12 | 10 |
| CTR | 5.94% | **22.73%** |
| Cost | $403.09 | $310.06 |
| Average CPC | $33.59 | $31.01 |
| Conversions | 0 | 0 |

**Every Green Marketing channel-policy default is correctly set on both campaigns.** Search
Partners off, Display off, AI Max off, asset automation opted out, Phrase + Exact only,
PRESENCE targeting, no country sweep, no demographic exclusion. There is nothing to undo before
scaling — which is why the diagnosis lands on price, routing and measurement rather than on
configuration.

### Are the two campaigns complementary, duplicative or cannibalizing?

**Verdict: DUPLICATIVE AND CANNIBALIZING.**

1. **Exact mirrors.** 15 ad groups each with *identical names*; 107 keywords each with
   identical texts and match types. All 15 ad-group names exist in both.
2. **One directly duplicated serving container.** `Power Washing Services Near Me` is ENABLED
   in **both** (A: 94 impr / 4 clicks / $109.31; B: 13 impr / 1 click / $29.04).
3. **Semantic overlap is far wider than identical text.** Judged by close-variant routing, not
   keyword text:
   - `power washing services` served in **both** campaigns from *different* keywords, and on
     2026-08-31 the campaign-B routing took **$146.60**.
   - `pressure washing near me` served in **four** ad groups across both campaigns.
   - `house washing near me` served in **three** ad groups across both.
   - `power washing services near me` served in both.
4. **Shared assets.** Ten asset IDs are shared, including the single call asset `403335872180`.
   Editing one edits both.
5. **Campaign B's 22.73% CTR is an artefact.** Strip out the single `Residential Pressure
   Washing Near Me` group (7 impressions, 6 clicks) and campaign B is 37 impressions, 4 clicks,
   10.8% CTR.

**Consequence:** conversion data is fragmented across two containers that have produced zero
conversions between them, and close-variant routing is choosing the wrong one.

---

## 7. Ad-group-level report

Full data in `2026-08-31-ad-group-performance.csv` (30 rows). Everything with delivery:

### Campaign A — Power Washing (6 enabled, 9 paused)

| Ad group | ID | Status | Impr | Clicks | Cost | CPC | IS% | LostRank% | Classification |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Power Washing Near Me | `202870585390` | ENABLED | 81 | 7 | $288.07 | $41.15 | 52.86 | 41.43 | **KEEP BUT REWRITE ADS** |
| Power Washing Services Near Me | `202870585430` | ENABLED | 94 | 4 | $109.31 | $27.33 | 66.29 | 31.46 | KEEP |
| Power Washing West Islip | `202870585670` | ENABLED | 1 | 1 | $5.71 | $5.71 | 100.0 | 0.0 | PAUSE AFTER REPLACEMENT |
| Power Washing Company Near Me | `202870585590` | ENABLED | 11 | 0 | $0.00 | — | 45.45 | 54.55 | KEEP |
| Power Washing Islip | `202870585630` | ENABLED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | PAUSE AFTER REPLACEMENT |
| Power Washing Dix Hills | `202870585830` | ENABLED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | PAUSE AFTER REPLACEMENT |
| House Pressure Washing Estimate | `202870586070` | PAUSED | 3 | 0 | $0.00 | — | 33.33 | 66.67 | WEAK INTENT |
| Residential Pressure Washing Near Me | `202870585870` | PAUSED | 6 | 0 | $0.00 | — | 16.67 | 83.33 | CONSOLIDATE |
| Pressure & Power Washing | `205713509704` | PAUSED | 3 | 0 | $0.00 | — | 9.99 | 90.01 | **DUPLICATE** — 34 keywords across 4 canonical intents |
| Soft & House Washing | `205713509744` | PAUSED | 1 | 0 | $0.00 | — | 11.11 | 88.89 | **DUPLICATE** — 28 keywords across 2 canonical intents |
| House Washing Company Near Me | `202870585910` | PAUSED | 2 | 0 | $0.00 | — | 9.99 | 85.71 | LOW VOLUME |
| Driveway Patio Concrete Washing | `205713509664` | PAUSED | 0 | 0 | $0.00 | — | 9.99 | 90.01 | LOW VOLUME |
| Driveway Pressure Washing Near Me | `202870586110` | PAUSED | 0 | 0 | $0.00 | — | 9.99 | 90.01 | NEEDS MORE DATA |
| Patio Pressure Washing Near Me | `202870586150` | PAUSED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | NEEDS MORE DATA |
| Soft House Washing Near Me | `202870586310` | PAUSED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | NEEDS MORE DATA |

### Campaign B — Power Washing #2 (6 enabled, 9 paused)

| Ad group | ID | Status | Impr | Clicks | Cost | CPC | IS% | LostRank% | Classification |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Residential Pressure Washing Near Me | `198082079423` | ENABLED | 7 | 6 | $176.17 | $29.36 | 50.0 | 50.0 | **PAUSE AFTER REPLACEMENT** |
| House Pressure Washing Estimate | `198082078983` | ENABLED | 24 | 3 | $104.85 | $34.95 | 61.90 | 28.57 | **WEAK INTENT** |
| Power Washing Services Near Me | `198082078783` | ENABLED | 13 | 1 | $29.04 | $29.04 | 75.0 | 16.67 | **DUPLICATE** — enabled in both campaigns |
| Driveway Pressure Washing Near Me | `198082079023` | ENABLED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | NEEDS MORE DATA |
| Patio Pressure Washing Near Me | `198082079183` | ENABLED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | NEEDS MORE DATA |
| Soft House Washing Near Me | `198082078703` | ENABLED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | NEEDS MORE DATA |
| *(9 paused groups)* | | PAUSED | 0 | 0 | $0.00 | — | 0.0 | 0.0 | REMAIN PAUSED |

**`Residential Pressure Washing Near Me` (B) at 7 impressions and 6 clicks is an 85.7% CTR.**
That is not a shape human search produces. It is the ad group that absorbed today's
five-clicks-on-one-impression event.

**Ad-group count judgement.** 30 ad groups and 214 keywords for 22 lifetime clicks is roughly
one click per 10 keywords. But the defect is **not** simply "too many SKAGs" — it is that the
SKAGs that exist do not own the demand (§9). The recommendation is a *smaller core structure
that owns more demand*: five to six ad groups in one campaign.

---

## 8. Ad-level report

Full data in `2026-08-31-ad-performance.csv` (54 rows, every current ad with complete headline
and description text).

**Structural audit result: the ad copy is not the primary problem.**

| Check | Result |
|---|---|
| Approval status | **54 of 54 APPROVED** |
| Policy issues | **zero** across all 54 |
| Ad Strength | GOOD or EXCELLENT throughout |
| Character limits | zero breaches — no headline over 30, no description over 90, no path over 15 |
| Pinning | **none** anywhere — full asset rotation available |
| Duplicate headlines within an ad | none |
| Phone numbers in copy | none |
| Unsupported claims (years, ratings, licence, guarantee, response time, price, "best", "#1") | **none found** |
| Awkward "near me" in copy | none — copy correctly uses "Near You" |
| Service clarity | strong — every ad names power/pressure/soft/house washing explicitly |
| Free-estimate offer | present in every ad |
| Landing-page match | correct on every ad group |

**The two defects that do exist:**

1. **Ad relevance BELOW_AVERAGE on `power washing near me`** despite Ad Strength EXCELLENT.
   *Ad Strength is Google's asset-diversity score; ad relevance is the auction signal.*
   Optimising for the first has not fixed the second.
2. **Geographic copy is stale.** Nine of fifteen headlines on `819975939342` and six on
   `819975939345` name Islip, West Islip or Dix Hills. Since 2026-08-26 the campaigns target
   **80 places across Nassau and Suffolk**. Copy written for three hamlets is now served to
   searchers in 77 other towns. This is a defect *created by the geo expansion*, not by the
   copy author.

### The ads that carry the spend

| Ad ID | Ad group | Impr | Clicks | CTR | Cost | Verdict |
|---|---|---:|---:|---:|---:|---|
| `819975939345` | Power Washing Near Me | 36 | 6 | **16.67%** | $205.85 | **KEEP** — the account's best ad |
| `819975939342` | Power Washing Near Me | 45 | 1 | 2.22% | $82.22 | **PAUSE AFTER REPLACEMENT** |
| `819975939348` | Power Washing Services Near Me | 54 | 3 | 5.56% | $87.18 | KEEP |
| `819975939351` | Power Washing Services Near Me | 40 | 1 | 2.50% | $22.13 | INSUFFICIENT DATA |
| `821376899993` | House Pressure Washing Estimate (B) | 12 | 2 | 16.67% | $82.74 | INSUFFICIENT DATA — ad group is WEAK INTENT |
| `821261156070` | House Pressure Washing Estimate (B) | 12 | 1 | 8.33% | $22.11 | INSUFFICIENT DATA |
| *all others* | | ≤11 | 0–1 | — | ≤$5.71 | **INSUFFICIENT DATA** |

The gap between `819975939345` (16.67%) and `819975939342` (2.22%) is real but rests on 7
clicks. **No RSA is declared a winner on this sample.** The one structural difference worth
noting: the winner leads with benefit ("Restore Your Curb Appeal"), the loser leads with
geography.

---

## 9. Keyword-level report

Full data in `2026-08-31-keyword-performance.csv` (all 214 keywords, with Quality Score
components, position estimates and Planner demand joined).

| Check | Result |
|---|---|
| Total keywords | 214 (107 per campaign, exact mirrors) |
| Status | **214 ENABLED** |
| Policy approval | **214 APPROVED** |
| System serving status | **214 ELIGIBLE** |
| Match types | 110 EXACT · 104 PHRASE · **zero BROAD** ✓ |
| **Distinct texts actually SERVING** | **11** |
| Distinct texts DORMANT behind paused ad groups | 44 |

### The keywords Google has scored

| Campaign | Ad group | Keyword | MT | Impr | Clk | Cost | CPC | **QS** | Exp. CTR | Ad rel. | LP exp. |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| A | Power Washing Near Me | power washing near me | PHRASE | 39 | 3 | $144.19 | $48.06 | **1** | BELOW | **BELOW** | **BELOW** |
| A | Power Washing Near Me | power washing near me | EXACT | 42 | 4 | $143.88 | $35.97 | **1** | BELOW | **BELOW** | **BELOW** |
| A | Power Washing Services Near Me | power washing services near me | EXACT | 76 | 4 | $109.31 | $27.33 | 3 | BELOW | ABOVE | **BELOW** |
| A | Power Washing Services Near Me | power washing services near me | PHRASE | 18 | 0 | $0.00 | — | 3 | BELOW | ABOVE | **BELOW** |
| B | Power Washing Services Near Me | power washing services near me | PHRASE | 12 | 1 | $29.04 | $29.04 | 5 | BELOW | ABOVE | AVERAGE |
| B | Power Washing Services Near Me | power washing services near me | EXACT | 1 | 0 | $0.00 | — | 5 | BELOW | ABOVE | AVERAGE |

The other 208 keywords have `UNSPECIFIED` on every component — insufficient impressions for
Google to score them.

**`power washing near me` PHRASE at $48.06 average CPC is the account's most expensive
keyword**, and it carries Quality Score 1. Those two facts are the same fact: low Ad Rank has
to be bought.

Position estimates (`first_page_cpc`, `top_of_page_cpc`, `first_position_cpc`) return **$0.00
on all 214 keywords** — they are not populated under a portfolio-free Maximize Clicks strategy.
`effective_cpc_bid` reads $0.01 throughout, which is vestigial under TARGET_SPEND. **Market
price therefore comes from Keyword Planner, not from the keyword resource.**

### Keyword scoring and verdicts

Scored on BOFU intent /5, local intent /5, service specificity /5, likelihood of hiring /5, and
DIY-or-equipment ambiguity /5 *(higher is worse)*:

| Keyword | BOFU | Local | Spec | Hire | Ambig↓ | Local demand | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| power washing near me | 5 | 5 | 5 | 5 | 1 | 260/mo | **CORE** |
| power washing services near me | 5 | 5 | 5 | 5 | 0 | 30/mo | **CORE** |
| power washing company near me | 5 | 5 | 5 | 5 | 0 | 260/mo (shared bucket) | **KEEP** |
| residential pressure washing near me | 5 | 5 | 5 | 5 | 0 | 20/mo | KEEP |
| driveway pressure washing near me | 5 | 5 | 5 | 4 | 1 | 20/mo | KEEP |
| patio pressure washing near me | 5 | 5 | 5 | 4 | 1 | low | LOW VOLUME |
| soft house washing near me | 5 | 5 | 5 | 4 | 0 | low | LOW VOLUME |
| house pressure washing estimate | 3 | 2 | 4 | 2 | 2 | low | **WATCH** — pulls price researchers |
| power washing islip | 4 | 5 | 4 | 4 | 1 | no reportable volume | **LOW VOLUME** |
| power washing west islip | 4 | 5 | 4 | 4 | 1 | no reportable volume | **LOW VOLUME** |
| power washing dix hills | 4 | 5 | 4 | 4 | 1 | no reportable volume | **LOW VOLUME** |
| **pressure washing near me** | 5 | 5 | 5 | 5 | 1 | **90/mo** | **ADD AS EXACT + PHRASE** |
| **power washing services** | 5 | 2 | 5 | 5 | 1 | **140/mo** | **ADD AS EXACT + PHRASE** |
| **power washing** | 4 | 1 | 4 | 3 | 3 | **880/mo** | **ADD AS PHRASE** (higher variance) |
| pressure washing | 4 | 1 | 4 | 3 | 3 | 480/mo | ADD AS PHRASE — phase 2 |
| house washing near me | 5 | 5 | 5 | 5 | 0 | 40/mo | ADD AS EXACT + PHRASE — phase 2 |
| power washing long island | 5 | 5 | 5 | 5 | 0 | 70/mo | phase 2 |
| jet wash near me | 5 | 5 | 4 | 5 | 2 | low | ADD AS EXACT — synonym, not a negative |
| *34 dormant texts in permanently-paused containers* | | | | | | | REMAIN DORMANT |

**Keywords to stop: none.** All 214 are approved, eligible and in scope. The waste is in
routing and price, not in the keyword list. Long keywords are not treated as automatically
high-intent — `house pressure washing estimate` is the longest serving text and the weakest.

---

## 10. Search-term report

Full data in `2026-08-31-search-term-verdicts.csv` — **88 rows, no impression threshold**,
covering **53 distinct terms**.

**Corpus coverage, stated up front:** `search_term_view` covers **209 of 246 impressions
(85.0%)**, **18 of 22 clicks (81.8%)** and **$555.89 of $713.15 (77.9%)** — all against the
10:21 snapshot denominators. The rest is Google
withholding queries below its privacy threshold plus same-day lag. **Corpus percentages are
never account percentages**, and on a base of 22 clicks every percentage is weak evidence.

### The terms that cost money

| Search term | Campaign | Ad group | Matched keyword | Impr | Clk | Cost | Verdict |
|---|---|---|---|---:|---:|---:|---|
| **power washing services** | **B** | **Residential Pressure Washing Near Me** | residential pressure washing near me EXACT | 5 | **5** | **$146.60** | **ROUTING ISSUE** |
| pressure washing | A | Power Washing Near Me | power washing near me EXACT | 3 | 2 | $59.82 | ADD AS KEYWORD |
| power washing companies near me | A | Power Washing Services Near Me | power washing services near me EXACT | 8 | 2 | $57.46 | ADD AS KEYWORD |
| power washing near me | A | Power Washing Near Me | power washing near me EXACT | 9 | 1 | $54.49 | **KEEP — CORE** |
| powerwash cost | B | House Pressure Washing Estimate | house pressure washing estimate EXACT | 2 | 1 | $40.07 | WATCH — price research |
| **gas station pressure washing near me** | A | Power Washing Near Me | power washing near me PHRASE | 4 | 1 | $35.31 | **NEGATIVE CANDIDATE** (blocked on K1-W2) |
| power wash near me | A | Power Washing Services Near Me | power washing services near me EXACT | 11 | 1 | $29.72 | ADD AS KEYWORD |
| power washing | A | Power Washing Near Me | power washing near me EXACT | 32 | 1 | $29.57 | **ADD AS KEYWORD — 880/mo** |
| pressure washing near me | B | Residential Pressure Washing Near Me | residential pressure washing near me EXACT | 13 | 1 | $29.57 | **ADD AS KEYWORD — 90/mo** |
| **deck cleaning services near me** | B | Power Washing Services Near Me | power washing services near me PHRASE | 8 | 1 | $29.04 | **OVER-BLOCKED** since 08-30 |
| powerwashing companies near me | A | Power Washing Services Near Me | power washing services near me EXACT | 3 | 1 | $22.13 | KEEP |
| average cost to power wash a house | B | House Pressure Washing Estimate | house pressure washing estimate EXACT | 2 | 1 | $22.11 | WATCH — price research |

### The headline search-term finding: over-blocking, not under-blocking

**Of 53 distinct terms, 49 are in scope.** The account does not have a junk-traffic problem.
It has the opposite: on **2026-08-30 the portfolio negative rollout added a bare PHRASE negative
on the single word `cleaning`**, and that negative now blocks:

- `deck cleaning services near me` — **which took a $29.04 click the day before**. Deck washing
  *is* power washing.
- `outdoor house cleaning services near me` — "outdoor" resolves it unambiguously to exterior work.
- **Four of the account's own live keywords**: `concrete cleaning service`,
  `driveway cleaning service`, `outdoor surface cleaning service`, `patio cleaning service`
  (all in the `Driveway Patio Concrete Washing` groups, EXACT and PHRASE, both campaigns).

Those ad groups are currently paused, so no live delivery is lost *today* — but the fence
permanently poisons any future enablement of an in-scope intent. **This is exactly the "never
fence with a bare noun" trap.**

Conversely, one genuine out-of-scope intent has **no** fence: `power washing repair near me`.
The existing BROAD negative `power washer repair` requires *every* word, and the term says
"washing", not "washer".

### Correctly blocked today

`roof washing near me` and `slate roof cleaning near me` (roof cleaning is on the work order's
`excluded_services`), and `house cleaning services near me` (interior cleaning).

### Never blindly negatived

`near me`, `quote`, `estimate`, `cost`, `price`, `pricing`, `best`, `hire`, `local` were all
reviewed as tokens, never auto-negatived. `jet wash near me` is kept as a **synonym opportunity**.
`outdoor house cleaning services near me` is kept while `house cleaning services near me` is
blocked — that contrast is the whole judgement.

### The cost cluster

Nine terms are price research reaching the account through the keyword
`house pressure washing estimate`: `powerwash cost`, `average cost to power wash a house`,
`cost to power wash`, `house wash price`, `house soft wash cost`,
`how much does power washing a house cost`, `how much is powerwashing a house`,
`power washing costs`, `price to powerwash house`. **Combined $62.18, zero conversions.**
Negativing them one at a time is the wrong instrument — the decision is structural (§14).

**No negative was added during this run.** PLAN-R2 is the term-level approval plan.

---

## 11. Zero-CVR diagnosis

The brief asks which of sixteen causes is responsible. Each was tested against evidence:

| Candidate cause | Verdict | Evidence |
|---|---|---|
| **Broken tracking** | **NO — the tag demonstrably fires** | Remarketing list `All Converters` ("People who converted on your site", 180-day) holds **16 members** against `All visitors` at 160. *Caveat: all traffic sources, 180 days, rounded audience estimate. It proves the tag fires; it is not a lead count and proves nothing about any specific paid click.* |
| **Conversion counting misconfigured** | **YES — CONFIRMED, P0** | All four conversion actions have `include_in_conversions_metric: FALSE` because `customer_conversion_goal` returns `biddable: FALSE` for all four categories. The Conversions column is structurally incapable of counting a lead. **Bidding is unaffected** — campaign-level goals override with the three lead categories biddable. |
| **No real leads from paid** | **YES — CONFIRMED** | `metrics.all_conversions` is 0.00 on every campaign on every date; `segments.conversion_action_name` returns zero rows, and the API omits all-zero rows, so that is real zero. |
| **Low click sample** | **YES — MATERIAL** | 18 billable clicks lifetime. At a plausible 5–10% lead rate the *expected* number of leads is 1.1–2.2. **Zero on 22 is disappointing, not statistically impossible.** |
| **Unqualified clicks / bot traffic** | **YES — CONFIRMED** | Google filtered **73 invalid clicks against 18 billable — 80.2% of all raw clicks** (60 vs 22 at the 10:21 snapshot), and by 16:40 had retroactively invalidated four of the five clicks on today's event, crediting back $117.28. Today's event was 5 billable clicks on 1 recorded impression from one postal code. ClickCease is on the site but syncs **zero** IP blocks to these campaigns. |
| **Poor search terms** | **NO** | 49 of 53 distinct terms are in scope; the core terms are textbook BOFU. |
| **Wrong locations** | **NO** | `user_location_view.targeting_location` is `true` on **every** row. Zero out-of-area delivery. |
| **Poor landing-page conversion** | **PROBABLE — untestable in READ mode** | Pages load, forms render, phone is correct, GCLID survives. But the brand title is wrong, the H1 is city-locked to 3 of 80 towns, and a fake countdown runs on every page. |
| **Weak offer** | **PROBABLE** | Free quote only. No price range, while competitors publish theirs openly. |
| **Weak trust** | **PROBABLE** | No review count, rating, years, licence or insurance on any page — all on the *unverified claims* list, so none may be added without written client confirmation. |
| **High friction** | **NO** | 5 visible form fields. Low for a home-services quote. |
| **Mobile usability** | **NO** | Mobile and desktop render identically: same H1, same phone, same form, HTTP 200 both. |
| **Unanswered calls / wrong phone routing** | **UNTESTED — no call has ever occurred** | `call_view` returns zero rows for the whole retained log; `segments.click_type = CALLS` shows **86 impressions and 0 clicks**. |
| **Form failures** | **UNKNOWN** | Requires the controlled test in PLAN-R1. No form was submitted in READ mode. |
| **Slow response / speed to lead** | **UNKNOWN** | `speed_to_lead` is empty in `client.yaml`. |
| **Duplicate conversion configuration** | **NO** | Four distinct actions, one per real outcome, no duplication. |
| **Foreign Google Ads tag** | **YES — P0, UNRESOLVED** | `AW-17878095007` loads on all six offer pages plus two main-site pages, alongside the account's own `AW-18369652705`. Flagged 2026-08-25; still live; owner unknown. |
| **WhatConverts attribution failure** | **UNKNOWN — no export** | Blocker WC-1. |

### Phone reconciliation

| Number | Where it appears | Status |
|---|---|---|
| **(631) 502-7946** | `tel:` link and body copy on **all six** offer pages, desktop and mobile · Google Ads call asset `403335872180` | **Approved and tracked** ✓ |
| (631) 502-5402 | `softwindli.com/our-work/` and `/service-areas/` | **UNTRACKED.** Destinations of two surviving account-level sitelinks. Latent leak — campaign-level sitelinks override them today. |
| (631) 553-5927 | not observed in this run | Recorded 2026-08-26 via the `wc_swap` cookie on main-site pages. Not re-confirmed. Offer pages render the static approved number. |
| **+1 631-519-8373** (GLE, from the brief) | **NOWHERE** | Not in any Ads asset, `tel:` link, or landing-page body text. |
| **+1 631-315-8655** (GBP, from the brief) | **NOWHERE** | Not in any Ads asset, `tel:` link, or landing-page body text. |

### The honest statement

**No August report may say this account has "no leads."** It may say **no conversion was
RECORDED** — a different claim. The distinction matters because (a) the Conversions column is
structurally zeroed, (b) no WhatConverts export exists, and (c) the tag demonstrably fires
site-wide. What *is* certain: **no paid click has produced a recorded conversion of any kind,
on 18 attempts and $595.87.**

---

## 12. CPC root-cause analysis

### CPC distribution — all 18 billable clicks (16:40 corrected)

| Statistic | Value |
|---|---:|
| Minimum | $5.71 |
| 25th percentile | $28.73 |
| **Median** | **$29.57** |
| Mean | $33.10 |
| 75th percentile | $35.31 |
| 90th percentile | $54.49 |
| Maximum | **$82.22** |

Full ordered list:
`5.71 · 22.11 · 22.13 · 26.66 · 28.73 · 28.73 · 29.04 · 29.32 · 29.57 · 29.57 · 29.72 · 29.91 ·
29.91 · 35.31 · 40.07 · 42.67 · 54.49 · 82.22`

**Restrict it to the post-ceiling window and it collapses onto the cap:** the five billable
clicks since 2026-08-27 12:25 priced **$29.57, $29.57, $29.72, $29.04, $29.32** — a range
**$0.68 wide** under a $30.00 ceiling. **That is a capped distribution, not a market
distribution.** The whole-life spread is wide only because it spans three bidding regimes
($5.00 cap, uncapped, $30.00 cap).

*(At the 10:21 snapshot this table read median $29.32, mean $32.42, p75 $29.91, p90 $42.67
across 22 clicks. Four duplicate $29.32 clicks were reversed by Google at midday.)*

### Cause-by-cause

| Cause | Evidence | Confidence | Financial impact | Action | Risk |
|---|---|---|---|---|---|
| **Maximize Clicks with the ceiling acting as the price** | All 5 post-ceiling clicks priced $29.04–$29.72, a $0.68 range under a $30 cap. Under $5.00: zero clicks in 12 days. Uncapped: $54.49 and $82.22, the latter exactly 2× the then-budget. | **HIGH** | **~$216 of $596 recoverable** | **PLAN-R3 — ceiling to $22.00** | Impression share falls |
| **Low Quality Score → Ad Rank must be bought** | QS **1** on `power washing near me` with BELOW_AVERAGE ×3. All six scored keywords BELOW_AVERAGE on expected CTR. | **HIGH** | drives the whole premium | PLAN-R5 (ad relevance), PLAN-R7 (LP experience) | slow to take effect |
| **Below-average landing-page experience** | BELOW_AVERAGE on 4 of 6 scored keywords. H1 city-locked to 3 of 80 towns; browser title carries the sibling brand. | **HIGH** | contributes to QS | PLAN-R7 | website change |
| **Below-average ad relevance** | BELOW_AVERAGE on `power washing near me` despite Ad Strength EXCELLENT. | **HIGH** | contributes to QS | PLAN-R5 | low |
| **Duplicate campaigns competing for the same query space** | `power washing services` served in **both**; the campaign-B routing cost $146.60. 4 ad groups matched `pressure washing near me`. | **HIGH** | $146.60 measured, today alone | PLAN-R4 → R6 → R10 → R11 | learning reset |
| **Aggressive absolute-top position** | Absolute-top IS 31.35% (A) / 45.67% (B) with QS 1–5. | **HIGH** | premium paid for position | PLAN-R3 | position loss |
| **Overly narrow keyword coverage forcing close variants** | Only 11 serving texts. The 880/mo, 480/mo and 140/mo buckets have no keyword. | **HIGH** | routing waste | PLAN-R6 | broader intent |
| **Poor query quality / invalid traffic** | **73 invalid vs 18 billable (80.2%)**; 4 of today's 5 clicks retroactively reversed by Google. Zero IP blocks synced from ClickCease. | **HIGH** | $117.28 already credited back | PLAN-R1 investigation | none |
| **Expanded geography without matching local copy** | +72 locations on 08-26; copy and H1 still name 3 hamlets. | **MEDIUM** | contributes to CTR and QS | PLAN-R5, PLAN-R7 | none |
| **Schedule concentration** | 60 of 168 hours = 35.7%. All spend compressed into a 10-hour window. | **MEDIUM** | forces competition into peak hours | blocked on SCHED-Q | call coverage |
| **Device differences** | Desktop $43.44 CPC at 4.94% CTR vs mobile $29.97 at 10.98%. | **MEDIUM** | desktop is 24% of spend at 44% higher CPC | watch; no modifier yet | thin sample |
| **High auction competition** | 10+ competitors identified in local SERP research; Suffolk/Nassau power washing is dense. | **MEDIUM** | structural | competitive copy | none |
| **Thin search demand** | ~1,100–1,200 BOFU searches/month across the footprint, ~36–40/day. | **MEDIUM** | limits total volume | geo already expanded | none |
| **Low CTR causing weak Ad Rank** | 8.94% account CTR; campaign A 5.94%. | **MEDIUM** | feeds the QS loop | PLAN-R5 | none |

### CPC by dimension

**By campaign (16:40):** A $33.59 · B $32.13
**By ad group (spending):** Power Washing Near Me $41.15 · House Pressure Washing Estimate (B)
$34.95 · Residential Pressure Washing Near Me (B) $29.36 · Power Washing Services Near Me (B)
$29.04 · Power Washing Services Near Me (A) $27.33 · Power Washing West Islip $5.71
**By keyword:** `power washing near me` PHRASE **$48.06** · `power washing near me` EXACT $35.97
· `house pressure washing estimate` $34.95 · `residential pressure washing near me` $29.36 ·
`power washing services near me` PHRASE $29.04 · `power washing services near me` EXACT $27.33
· `power washing west islip` $5.71
**By device:** DESKTOP **$43.44** (4.94% CTR) · MOBILE $29.97 (10.98% CTR) · TABLET no clicks
**By hour:** 16:00 **$54.46** (3 clicks, $163.37) · 12:00 $40.07 · 11:00 $36.20 · 10:00 $35.31
· 08:00 $29.32 · 09:00 $29.30 · 15:00 $28.73 · 14:00 $23.77 · 17:00 $22.12 · 13:00 no clicks
**By day:** WED **$52.17** · TUE $40.41 · THU $32.54 · FRI $29.57 · SAT $29.38 · MON $24.92
**By location:** Dix Hills `9051836` **$54.46** · West Babylon `1023474` $42.67 · 11740
`9004506` $35.31 · North Hempstead `9198508` $29.85–$31.09 · **11742 Holbrook `9004508` $29.32
(5 clicks, $146.60)** · Babylon Town `9214462` $13.92 · 11702 `9004477` $28.73

### The decisive distinction

> **MORE QUALIFIED AUCTIONS — or GOOGLE BIDDING MORE FOR THE SAME AUCTIONS?**

**GOOGLE IS BIDDING MORE FOR THE SAME AUCTIONS. Decisively.**

1. The price tracks the *cap* in all three regimes ($5 → no clicks; uncapped → $82; $30 → $29).
   It does not track the market.
2. Keyword Planner top-of-page **LOW** for the serving set is $8.75–$13.49. The account pays
   **2.2×–3.4×** that.
3. The 2026-08-26 geo expansion added 72 locations per campaign and produced **no impression
   lift** on the day it delivered. The extra spend came from **price**, not volume.
4. Quality Score is 1–5 with BELOW_AVERAGE expected CTR throughout. A weak Ad Rank has to be
   bought.

---

## 13. Asset-level report

Full data in `2026-08-31-asset-performance.csv` (25 linked assets).

**Inventory:** 426 assets total — TEXT 401, SITELINK 12, CALLOUT 8, STRUCTURED_SNIPPET 2,
CALL 1, LOCATION 1, IMAGE 1. All `source: ADVERTISER` — **no automatically created assets**.
408 are unlinked (the 401 TEXT assets are RSA components).

| Scope | Sitelinks | Callouts | Snippets | Call | Images | Business name | Logo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Campaign A `24103511039` at 10:21 | **3** | 3 | **0** | 1 | 0 | 0 | 0 |
| Campaign B `24145053510` at 10:21 | 4 | 3 | 1 | 1 | 0 | 0 | 0 |
| **Campaign A at 10:52** | **4** | **4** | **1** | 1 | 0 | 0 | 0 |
| **Campaign B at 10:52** | **4** | **4** | **1** | 1 | 0 | 0 | 0 |
| Account level | 3 | 4 | 1 | 0 | 0 | 0 | 1 |
| **Ad-group level** | **0** | **0** | **0** | **0** | **0** | **0** | **0** |

**The parity gap closed during this audit.** Four campaign_asset links were created by hand in
the UI between the opening and closing reads — see §19. Both campaigns now carry identical asset
sets. Findings 1 and 2 below describe the state at 10:21 and are **RESOLVED**; PLAN-R8 was
rewritten to zero mutations as a result.

### Findings

1. **RESOLVED at 10:52 — campaign A was one sitelink short.** PLAN-H created 4 sitelink assets
   and 8 campaign links on 2026-08-27; at 10:21 there were **7**, with `413928453094` "Free
   Quote" linked only to campaign B. Campaign A carries 202 of 246 impressions, and **sitelinks
   account for 5 clicks and $158.59 — 22.2% of all account spend**, so this was not a cosmetic
   asset. The link was created by hand during this audit. *(PLAN-R8, now 0 mutations)*
2. **RESOLVED at 10:52 — campaign A had no campaign-level structured snippet** and was falling
   back to the account-level one. `404844116658` was linked by hand during this audit.
   *(PLAN-R8, now 0 mutations)*
3. **The call asset switches off an hour before the campaigns do.** Asset `403335872180` is
   scheduled Mon–Sat **08:00–17:00**; the campaigns run **08:00–18:00**. For the last hour of
   every serving day the ads run with no call button. The 17:00 hour has delivered 27
   impressions, 2 clicks, $44.24. Published hours are Mon–Fri 08:00–18:00, so extending Mon–Fri
   is supported by a verified fact; Saturday is NOT PUBLISHED and must stay at 17:00.
   *(BLOCKED on SCHED-Q — is the phone answered 17:00–18:00?)*
   **Blast radius verified, not assumed:** the schedule lives on the **asset**, and this asset is
   linked to `campaign_asset` rows on both in-scope campaigns and to **zero** `ad_group_asset`
   rows. The account has exactly two non-removed campaigns, both under this work order.
4. **The call asset has served 86 times and been clicked zero times.** Not an asset defect — the
   strongest single piece of evidence that paid traffic is not converting.
5. **No image assets, no business-name asset.** 164 of 246 impressions are mobile, where image
   extensions matter most. *(BLOCKED on client-supplied, rights-cleared photographs.)*
6. **Three account-level sitelinks point at pages showing the untracked (631) 502-5402** —
   `403497568748` Service Areas, `403497573329` Request A Quote, `403497584582` Our Work.
   Campaign-level sitelinks override them today. *(PLAN-R11)*
7. `LOCATION_EXPANSION` click type: **108 impressions, 0 clicks**. One LOCATION asset exists,
   unlinked; the extension serves from a linked Business Profile asset set. Not automatically
   waste — but with zero conversions there is nothing to defend it either. Re-check in 30 days.
8. **Asset wording is clean.** All callouts and snippets are in scope (Surface-Specific
   Cleaning, Long Island Service, Free Quotes; snippet values Pressure Washing / House Washing
   / Soft Washing / Patio Cleaning / Driveway Cleaning). **No irrelevant landscaping asset. No
   unapproved claim. No wrong phone number.** All assets APPROVED.

---

## 14. Landing-page audit

Full data in `2026-08-31-landing-page-audit.csv` (11 URLs, desktop + mobile, real Chromium
with GCLID and UTMs).

### Spend concentration

| Page | Ad groups | Clicks | Cost | Share |
|---|---:|---:|---:|---:|
| `/power-washing-services-islip-west-islip-dix-hills/` | 12 | 13 | **$432.13** | **60.6%** |
| `/residential-pressure-washing/` | 2 | 6 | $176.17 | 24.7% |
| `/house-pressure-washing-estimate/` | 2 | 3 | $104.85 | 14.7% |
| all other offer pages | 8 | 0 | $0.00 | 0% |

### Per-page results

| URL | HTTP | Redirects | Title | H1 city-locked | Phone | Form fields | GCLID | Foreign tag | Countdown |
|---|---|---|---|---|---|---:|---|---|---|
| `/driveway-pressure-washing/` | 200 | none | *…\| Softwind Landscape & Masonry* | **YES** | PASS | 5 | PASS | **PRESENT** | **YES** |
| `/house-pressure-washing-estimate/` | 200 | none | *…\| Softwind Landscape & Masonry* | no | PASS | 5 | PASS | **PRESENT** | **YES** |
| `/house-washing-company/` | 200 | none | *…\| Softwind Landscape & Masonry* | **YES** | PASS | 5 | PASS | **PRESENT** | **YES** |
| `/patio-power-washing/` | 200 | none | *…\| Softwind Landscape & Masonry* | **YES** | PASS | 5 | PASS | **PRESENT** | **YES** |
| `/power-washing-services-islip-west-islip-dix-hills/` | 200 | none | *…\| Softwind Landscape & Masonry* | **YES** | PASS | 5 | PASS | **PRESENT** | **YES** |
| `/power-washing-soft-washing/` | 200 | none | *…\| Softwind Landscape & Masonry* | **no** | PASS | 5 | PASS | **PRESENT** | **YES** |
| `/residential-pressure-washing/` | 200 | none | *…\| Softwind Landscape & Masonry* | **YES** | PASS | 5 | PASS | **PRESENT** | **YES** |
| `/soft-house-washing/` | 200 | none | *…\| Softwind Landscape & Masonry* | **YES** | PASS | 5 | PASS | **PRESENT** | **YES** |
| `softwindli.com/our-work/` | 200 | none | Check Out Our Work Portfolio | no | **FAIL — (631) 502-5402** | 12 | PASS | PRESENT | no |
| `softwindli.com/service-areas/` | 200 | none | Find Out Where We Serve | no | **FAIL — (631) 502-5402** | 12 | PASS | PRESENT | no |
| `softwindli.com/contact-us/` | 202 | — | **UNKNOWN — SG-Captcha interstitial** | — | UNKNOWN | — | — | — | — |

### Scores — the two pages that carry 85% of spend

| Dimension | `/power-washing-services-islip-…/` | `/residential-pressure-washing/` |
|---|---:|---:|
| Keyword-to-page match | **9/10** | **9/10** |
| Ad-to-page match | **9/10** | 8/10 |
| Service clarity | **10/10** (35 "power washing" mentions) | **10/10** (21 "pressure washing" mentions) |
| Local relevance | **4/10** — names 3 of 80 targeted towns | **4/10** — same |
| Trust | **3/10** — no reviews, rating, years, licence; sibling brand in the title | **3/10** |
| Mobile conversion readiness | **9/10** — full parity, 5-field form, tel: button | **9/10** |
| Form friction | **9/10** — 5 visible fields | **9/10** |
| Call tracking | **PASS** — approved (631) 502-7946 in tel: and body | **PASS** |
| Form tracking | **UNKNOWN** — no form submitted in READ mode | **UNKNOWN** |

### Specific checks the brief asked for

| Check | Result |
|---|---|
| Generic landing-page copy | **NO** — each page is service-specific and well written |
| Keyword stuffing | **NO** — mention density is natural |
| Weak H1 | **NO** — but city-locked (see below) |
| **City mismatch** | **YES — 6 of 8 offer pages name 3 of 80 targeted towns** |
| Patio "power washing" vs "pressure washing" mismatch | **YES — minor.** `/patio-power-washing/` has H1 "Patio **Pressure** Washing", title "Patio **Power** Washing". Both terms are used in the market; the page is internally coherent. Low priority. |
| Reviews unrelated to the service | **NO** — no reviews on any offer page at all |
| **Fake or resetting countdown** | **YES — "Offer Ends" on all six offer pages, backed by no dated offer** |
| Published implementation notes | **NO — resolved.** The authoring instruction flagged on 2026-08-25 is gone. |
| **Wrong phone number** | **NO on offer pages** (approved number throughout) · **YES on the two main-site sitelink destinations** |
| Untracked sitelink destinations | **YES — 3 account-level sitelinks**, overridden today by campaign-level ones |
| Slow mobile load | **NO** — 159–163 KB mobile, no render blockers observed |
| Form submission errors | **UNKNOWN** — requires the controlled test |
| Weak CTA hierarchy | **NO** — 7–9 distinct CTAs per page, quote-led |
| No above-the-fold proof | **YES** — no proof element above the fold on any page |
| No project-specific images | **NO** — each page has a "Recent … Results" section |
| **No clear free-estimate offer** | **NO — the free-quote offer is clear and repeated** |

**No form was submitted and no call was placed.** A controlled test requires separate approval
(PLAN-R1).

---

## 15. Audience, demographic, device, location and schedule reports

### Audiences — none attached

`ad_group_audience_view` returns **zero rows**. Both campaigns carry
`targeting_setting.target_restrictions` with `dimension: AUDIENCE`, `bid_only: true` — already
configured for observation, with **zero audience criteria attached**. *(PLAN-R9)*

### Demographics — no exclusions anywhere

`campaign_criterion` returns **zero** GENDER, **zero** AGE_RANGE and **zero** INCOME_RANGE
criteria on both campaigns. **Verified clean — nothing to undo.**

| Gender | Impr | Clicks | CTR | Cost | CPC |
|---|---:|---:|---:|---:|---:|
| **FEMALE** | 39 | 7 | **17.95%** | $179.41 | **$25.63** |
| MALE | 141 | 13 | 9.22% | $421.95 | $32.46 |
| UNDETERMINED | 66 | 2 | 3.03% | $111.79 | $55.90 |

| Age | Impr | Clicks | CTR | Cost | CPC |
|---|---:|---:|---:|---:|---:|
| **65+** | 33 | **11** | **33.33%** | **$301.54** | $27.41 |
| 18–24 | 28 | 3 | 10.71% | $123.82 | $41.27 |
| UNDETERMINED | 66 | 2 | 3.03% | $111.79 | $55.90 |
| 45–54 | 34 | 2 | 5.88% | $64.35 | $32.17 |
| 55–64 | 41 | 2 | 4.88% | $59.82 | $29.91 |
| 35–44 | 17 | 1 | 5.88% | $29.72 | $29.72 |
| 25–34 | 27 | 1 | 3.70% | $22.11 | $22.11 |

**Household income:** no rows — not reported for this account.

**DO NOT EXCLUDE WOMEN.** The data actively argues against it: women click at nearly twice the
rate of men and cost **21% less** per click. On 7 clicks that is not proof women are better
customers — it is proof there is **no evidence whatsoever** for an exclusion, in an account
that cannot afford to lose reach.

**65+ is a WATCH item, not an action.** 42.3% of all spend at a 33.33% CTR on 33 impressions.
That CTR is far outside the normal range for a search result and, on this sample, is as
consistent with accidental mobile taps as with high intent. No age modifier is proposed.

### Device

| Device | Impr | Clicks | CTR | Cost | CPC |
|---|---:|---:|---:|---:|---:|
| MOBILE | 164 | 18 | 10.98% | $539.39 | $29.97 |
| DESKTOP | 81 | 4 | 4.94% | $173.76 | **$43.44** |
| TABLET | 1 | 0 | 0.00% | $0.00 | — |

Desktop is 24.4% of spend at a **45% higher CPC and less than half the CTR**. A negative
desktop modifier is a reasonable next test, but 4 clicks is too thin to act on now.

### Locations — 23 of 80 targets have ever delivered

Full data in `2026-08-31-location-performance.csv` (162 rows = 81 criteria × 2 campaigns).

**Zero out-of-area delivery.** `user_location_view.targeting_location` is `true` on every row.

| Location | Type | Campaign | Impr | Clicks | Cost | CPC |
|---|---|---|---:|---:|---:|---:|
| Dix Hills `9051836` | City | A | 27 | 3 | $163.37 | **$54.46** |
| **11742 Holbrook `9004508`** | Postal Code | **B** | **1** | **5** | **$146.60** | $29.32 |
| North Hempstead `9198508` | Municipality | A | 62 | 3 | $89.54 | $29.85 |
| North Hempstead `9198508` | Municipality | B | 11 | 2 | $62.18 | $31.09 |
| 11702 `9004477` | Postal Code | A | 3 | 2 | $57.46 | $28.73 |
| West Babylon `1023474` | City | B | 3 | 1 | $42.67 | $42.67 |
| 11740 `9004506` | Postal Code | A | 4 | 1 | $35.31 | $35.31 |
| Bay Shore `1022719` | City | A | 7 | 1 | $29.57 | $29.57 |
| Sayville `1023347` | City | B | 2 | 1 | $29.57 | $29.57 |
| North Babylon `1023202` | City | B | 8 | 1 | $29.04 | $29.04 |
| Babylon `9214462` | Municipality | A | 26 | 2 | $27.84 | **$13.92** |
| Salisbury `9052792` | City | A | 23 | 0 | $0.00 | — |
| West Islip `1023482` | City | A | 5 | 0 | $0.00 | — |
| Islip (hamlet) `1023035` | City | A | 5 | 0 | $0.00 | — |
| *12 more with impressions, zero clicks* | | | | | | |
| **57 targets** | | | **0** | **0** | **$0.00** | — |

- **High-CPC locations:** Dix Hills $54.46, West Babylon $42.67, 11740 $35.31
- **Cheapest converting-scale location:** Babylon Town $13.92
- **No-click locations with real impressions:** Salisbury (23), West Islip (18 across both), 11795 (12)
- **57 of 80 targets have never served** — the geo expansion added reach the demand has not filled
- **No landing-page city match** for 77 of the 80 targeted places (§14)

**Governance note.** `client.yaml` records a `verified_service_area_locations` block of **16**
locations, while the live account targets **80**. The 80 are legitimate: PLAN-J2A was approved
and executed on 2026-08-26 from a client-supplied `Location report (2).csv` with 75 New York
rows (SHA-256 recorded in the plan). Four locations Walter confirmed in the earlier 16-item list
— Huntington `1023022`, Oyster Bay `9198014`, Brookhaven `9198728`, Hempstead `9198814`, all
large Towns — are **NOT** targeted, while their constituent villages and ZIPs are. **`client.yaml`
is stale, not wrong.** It should be updated to the executed 80; that is documentation drift, not
a compliance failure.

### Schedule

Both campaigns: **Monday–Saturday 08:00–18:00, six dayparts, bid modifier 0. Sixty of 168 hours
= 35.7%. No Sunday.** Sunday 2026-08-30 returned zero rows, as every Sunday has since the
daypart was deleted on 2026-08-07.

| Hour | Impr | Clicks | CTR | Cost | CPC |
|---|---:|---:|---:|---:|---:|
| 16:00 | 31 | 3 | 9.68% | **$163.37** | **$54.46** |
| 08:00 | 13 | 5 | 38.46% | $146.60 | $29.32 *(today's anomaly)* |
| 14:00 | 32 | 4 | 12.50% | $95.10 | $23.77 |
| 11:00 | 21 | 2 | 9.52% | $72.39 | $36.20 |
| 09:00 | 21 | 2 | 9.52% | $58.61 | $29.30 |
| 15:00 | 26 | 2 | 7.69% | $57.46 | $28.73 |
| 17:00 | 27 | 2 | 7.41% | $44.24 | $22.12 |
| 12:00 | 38 | 1 | 2.63% | $40.07 | $40.07 |
| 10:00 | 18 | 1 | 5.56% | $35.31 | $35.31 |
| 13:00 | 19 | 0 | 0.00% | $0.00 | — |

| Day | Impr | Clicks | CTR | Cost | CPC |
|---|---:|---:|---:|---:|---:|
| THURSDAY | 73 | 6 | 8.22% | $195.26 | $32.54 |
| MONDAY | 33 | 7 | 21.21% | $174.42 | $24.92 |
| TUESDAY | 28 | 3 | 10.71% | $121.22 | $40.41 |
| WEDNESDAY | 49 | 2 | 4.08% | $104.35 | **$52.17** |
| FRIDAY | 24 | 2 | 8.33% | $59.14 | $29.57 |
| SATURDAY | 39 | 2 | 5.13% | $58.76 | $29.38 |
| **SUNDAY** | **0** | **0** | — | **$0.00** | — |

**16:00 is the most expensive hour** at $54.46 and 22.9% of all spend. **17:00 is the
cheapest** at $22.12 — and it is the hour with no call button.

**No schedule change is proposed.** Expansion stays blocked until call-answering and
lead-response hours are confirmed (SCHED-Q1..Q6), and the landing pages carry a clickable phone
button that Google Ads cannot switch off — so a 24/7 campaign would expose a call surface
regardless of the call asset's hours.

---

## 16. Auction Insights — INSUFFICIENT AUCTION DATA

`metrics.auction_insight_search_impression_share`, `…_overlap_rate`, `…_position_above_rate`,
`…_top_impression_percentage`, `…_absolute_top_impression_percentage` and
`…_outranking_share` all exist and are `selectable: true` in `GoogleAdsFieldService`.

Every query returns:

```
PERMISSION_DENIED
The developer doesn't have access to metrics: ''auction_insight_search_impression_share''.
```

Tested at customer, campaign, ad-group and keyword level, with and without a date filter, and
with a minimal single-metric SELECT. All four fail identically. **The Green Marketing developer
token is Basic access and does not carry Auction Insights.**

**Auction Insights must be exported from the Google Ads UI by a signed-in user.** I have no
authenticated UI session and did not attempt an interactive login.

`2026-08-31-auction-insights-campaign.csv` and `…-ad-group.csv` therefore carry a single row
reading **`INSUFFICIENT AUCTION DATA - API ACCESS DENIED`**. **No competitor figure has been
invented.**

### What can be said without it

| Proxy (impression-weighted, 16:40) | Campaign A | Campaign B |
|---|---:|---:|
| Search impression share | 53.55% | 66.30% |
| Lost IS — rank | 31.45% | 17.70% |
| Lost IS — budget | 2.01% | 2.00% |
| Absolute-top impression share | 31.35% | 45.67% |

*(At the 10:21 audit snapshot: 61.24% / 75.34% IS, 35.97% / 20.12% lost-to-rank,
35.86% / 51.89% absolute-top. The fall is the day's later impressions landing.)*

**Softwind is NOT losing on budget and is NOT absent from the auction.** It holds 54–66%
impression share and 31–46% absolute-top. What it loses, it loses on **rank** — and it holds
that top position only by bidding at its ceiling with Quality Score 1–5. That is the signature
of an advertiser **already overpaying for top positions**, not one being outbid.

### Manual UI export instructions

1. Sign in to Google Ads on account **152-172-5229**.
2. Campaigns → select **Power Washing** → **Insights and reports → Auction insights** →
   date range 2026-08-01 to 2026-08-31 → **Download → CSV**.
3. Repeat for **Power Washing #2**.
4. Repeat at ad-group level for `Power Washing Near Me`, `Power Washing Services Near Me`,
   `Residential Pressure Washing Near Me` and `House Pressure Washing Estimate` — the only four
   with enough impressions to meet Google's reporting threshold. Groups with 0–11 impressions
   will return nothing; that is **INSUFFICIENT AUCTION DATA**, not an error.
5. Save into `clients/softwind-power-washing/audits/`.
6. **Do not click a competitor's paid ad.**

---

## 17. Priority classification

### P0 — CRITICAL

| # | Finding | Plan |
|---|---|---|
| P0-1 | **Conversion counting is structurally zeroed.** All four actions `include_in_conversions_metric: FALSE`; `customer_conversion_goal` biddable FALSE ×4. No report can show a lead. | R1 |
| P0-2 | **Foreign Google Ads tag `AW-17878095007`** on all six offer pages + two main-site pages. Owner unknown since 2026-08-25. | R1, R7 |
| P0-3 | **Duplicate campaigns materially competing.** `power washing services` cost **$146.60** today by routing to the wrong campaign. | R4, R6, R11 |
| P0-4 | **The CPC ceiling is the price.** 9 of 11 post-ceiling clicks at $28.73–$29.91; QS 1 on the biggest keyword. | R3 |
| P0-5 | **Traffic quality — CONFIRMED by Google's own filtering.** 73 invalid vs 18 billable (**80.2%** of raw clicks); Google retroactively reversed 4 of the 5 clicks on the 08-31 event and credited back $117.28; **zero** ClickCease IP blocks synced. | R1 |
| P0-6 | **Landing pages branded for the sibling company** in every browser title. | R7 |
| P0-7 | **No WhatConverts export exists.** Reconciliation impossible. | R1 (WC-1) |

*Not present:* broken form conversion (untested, not broken) · wrong phone on offer pages
(correct) · broken Final URL (all 200).

### P1 — HIGH

| # | Finding | Plan |
|---|---|---|
| P1-1 | **Over-broad negative `cleaning`** blocks in-scope demand and 4 own keywords. | R2 |
| P1-2 | `power washing repair` has **no** fence. | R2 |
| P1-3 | **The account does not own its three largest demand buckets** (880/480/140 per month). | R6 |
| P1-4 | **Ad relevance BELOW_AVERAGE**; copy names 3 of 80 targeted towns. | R5 |
| P1-5 | **H1 city lock** on 6 of 8 offer pages, incl. the page carrying 60.6% of spend. | R7 |
| P1-6 | ~~Campaign A is one sitelink short~~ — **RESOLVED by owner action at 10:52**, mid-audit. | R8 (now 0 mutations) |
| P1-7 | **The call asset switches off at 17:00** while campaigns run to 18:00. | R8 (blocked) |
| P1-8 | **Fake "Offer Ends" countdown** on every offer page. | R7 |
| P1-9 | **The `estimate` keyword pulls price researchers** — $62.18, zero conversions. | R4, R7, R11 |
| P1-10 | **Untracked (631) 502-5402** on two account-level sitelink destinations. | R7, R11 |

### P2 — MEDIUM

Audience observations (R9) · ~~campaign-A structured snippet~~ (**resolved mid-audit**) · missing image and
business-name assets (R8, blocked) · landing-page price transparency (R7, blocked) · the three
zero-impression geo SKAGs (R11) · desktop CPC 45% above mobile (watch) · `client.yaml`
service-area block stale at 16 vs 80 live targets · reviews-page sentiment gating (R7).

### P3 — LOW

Ad Strength is already GOOD/EXCELLENT — no cosmetic work justified · `/patio-power-washing/`
title-vs-H1 power/pressure wording · low-volume keyword experiments (`jet wash near me`) ·
`LOCATION_EXPANSION` 108 impressions / 0 clicks (re-check in 30 days).

---

## 18. Campaign-structure decision

Recorded in full in `2026-08-31-core-structure-recommendation.md` and fingerprinted as
**PLAN-R4 `0E08B1CF1F16`** (zero mutations).

**Summary:** one campaign — **`24103511039`** — owns everything. Campaign B is retired (paused,
never deleted) only after its four unique intents are rebuilt, verified and enabled in campaign
A. The core structure is **six ad groups**: three that exist and are kept, three created paused.
The account moves from *30 ad groups owning 11 serving texts* to *6 ad groups owning 14*.

---

## 19. Closing verification — 40 checks, 39 unchanged, 1 changed by the owner

This audit ran `SELECT` statements only. No script in this run constructs an operation or calls
a mutate service. The closing check re-read every mutable surface against the opening snapshot.

| Surface | Value at 10:21 | Value at 10:52 | Changed |
|---|---|---|---|
| Campaigns (non-removed) | 2 | 2 | no |
| Ad groups | 30 | 30 | no |
| Keywords | 214 | 214 | no |
| Ads (non-removed) | 54 | 54 | no |
| Campaign criteria (non-removed) | 446 | 446 | no |
| Campaign negative keywords | 132 + 132 | 132 + 132 | no |
| Budget `15764226923` | $41.50 | $41.50 | no |
| Budget `15802443075` | $41.11 | $41.11 | no |
| CPC ceiling A / B | $30.00 / $30.00 | $30.00 / $30.00 | no |
| Conversion actions | 4 | 4 | no |
| Ad group statuses (all 30) | — | identical | no |
| Ad statuses (all 54) | — | identical | no |
| Account assets / ad-group assets | 9 / 0 | 9 / 0 | no |
| **Campaign asset links** | **16** | **20** | **YES — see below** |

### The one change, and who made it

**Four `campaign_asset` links were created between 10:21 and 10:52, while this audit was
running. This agent made no mutation of any kind.**

| Campaign | Asset | Type | Text |
|---|---|---|---|
| `24103511039` | `413928453094` | SITELINK | Free Quote |
| `24103511039` | `404844116658` | STRUCTURED_SNIPPET | Service catalog |
| `24103511039` | `404773124911` | CALLOUT | Careful Washing Methods |
| `24145053510` | `404773124911` | CALLOUT | Careful Washing Methods |

These were made by hand in the Google Ads UI — consistent with the 09:39:41 budget change from
the same web client earlier the same morning. `change_event` returns only that budget change,
which is expected: it lags by hours and is unusable for same-session corroboration.

**The first two are exactly what PLAN-R8 proposed.** Rather than leave an approvable artifact
that would try to create links which now exist, **PLAN-R8 has been rewritten to zero mutations**
and re-fingerprinted from `DFF115FF4D26` to **`C941DDCA44C6`**. Any approval phrase issued
against the earlier two-mutation version is void.

**All four new assets were scope-checked:** every one is policy APPROVED, `source: ADVERTISER`
(not auto-created), and carries no unverified claim. The callout "Careful Washing Methods" is
supported by the client's verified surface-specific-method USP; the snippet values are all
inside `services_in_scope`. **No objection.**

*(Full check log in `snapshots/forensic-unchanged-proof-2026-08-31.json`.)*

---

## 19b. The 2026-08-31 click reversal — traffic quality, confirmed

The continuation drift check at **16:40** found the day's ledger materially restated by Google.

| 2026-08-31 | At 10:21 | At 16:40 |
|---|---:|---:|
| Impressions | 2 | **38** |
| Billable clicks | **5** | **1** |
| Cost | **$146.60** | **$29.32** |
| Invalid clicks | 0 | **13** |

**Google retroactively invalidated four of the five clicks on `power washing services` and
credited back $117.28** — exactly 4 × $29.32. Those four clicks moved into the invalid column.
**Every other day in the ledger is byte-identical.**

This converts the morning's hypothesis into a confirmed finding. The audit flagged five
billable clicks on one recorded impression from a single postal code as "not a shape human
search produces" and noted that some of the spend might yet be credited back. Google's own
invalid-click filtering has now agreed.

**Account-level effect:**

| | 10:21 | 16:40 |
|---|---:|---:|
| Impressions | 246 | 282 |
| Billable clicks | 22 | **18** |
| Spend | $713.15 | **$595.87** |
| CTR | 8.94% | **6.38%** |
| Average CPC | $32.42 | **$33.10** |
| Invalid clicks | 60 | **73** |
| **Invalid share of raw clicks** | 73.2% | **80.2%** |
| Conversions | 0 | **0** |

**Four in five raw clicks on this account are invalid.** That is an extraordinary rate and it
is now the strongest single argument in the audit for the ClickCease integration check
(§13 finding C-6: the script loads on every page while syncing **zero** `IP_BLOCK` criteria to
either campaign).

**The CPC finding sharpens rather than weakens.** With the four duplicate $29.32 clicks removed,
the post-ceiling window is five billable clicks priced **$29.57, $29.57, $29.72, $29.04,
$29.32** — a **$0.68 range under a $30.00 cap**. PLAN-R3 has been restated against this ledger;
its recommended ceiling ($22.00) and its action list are unchanged, so its fingerprint is
unchanged.

**New search terms observed today, after the audit corpus was built** — all reinforcing
existing findings, none changing a verdict: `pressure washing services near me` (7 impressions),
`driveway pressure washing near me` (4, EXACT/EXACT), `house washing services near me` (3),
`house washing near me` (2), `commercial pressure washing near me` (2, the K1-W2 commercial
gate again), `pressure washing prices` (2, the cost cluster again), `power washing` (2),
`pressure washing near me` (2 across two ad groups), `power washing services` (1),
`power washing companies near me` (1), and **`window and house washing near me` (1)** — window
cleaning is out of scope and is **not** fenced by any of the 123 live negative texts. It cost
$0.00 and is a WATCH item, not yet a negative candidate.

---

## 20. Consolidated open questions

Only the items that materially change the deliverable. Each names what stays blocked without it.

| # | Question | Blocks | Recommended answer |
|---|---|---|---|
| **Q1** | **Does Softwind sell commercial / industrial washing?** | PLAN-R2 negatives for `gas station` and `commercial power washing company` ($35.31 measured). *(K1-W2, open since 08-27.)* | If NO → add both as PHRASE negatives. If YES → they become keyword opportunities, but serving them needs a commercial landing page first; every offer page is residential. |
| **Q2** | **Who owns Google Ads account `17878095007`?** | PLAN-R7 F2, P0. | If not Softwind-controlled, remove the tag from `offer.softwindli.com` this week. |
| **Q3** | **Can you supply the WhatConverts export for 2026-08-01 → 08-31?** | The entire lead reconciliation (WC-1). | Export the Power Washing profile; without it no one can say whether leads arrived. |
| **Q4** | **Is (631) 502-7946 answered 17:00–18:00 Mon–Fri?** | PLAN-R8 call-asset schedule; all schedule expansion (SCHED-Q). | Published hours say Mon–Fri 08:00–18:00. If yes, extend Mon–Fri only; Saturday hours are not published. |
| **Q5** | **Is there a real, dated offer behind the "Offer Ends" countdown?** | PLAN-R7 F3. | If no → remove it. Fake urgency is prohibited and it costs trust. |
| **Q6** | **Average job revenue, gross margin, close rate, target CPL?** | Every profit, ROAS and CPL figure. All `null` today. | Supply them, even as ranges. Without a denominator no budget number can be justified. |
| **Q7** | **Can you export Auction Insights from the UI?** | §16 competitor analysis. | Follow the six steps in §16. The API cannot do it on a Basic-access token. |
| **Q8** | **Was the 09:39 budget cut to $41.50 deliberate and should it stand?** | PLAN-R12 (which currently recommends holding it). | Recommend it stands. Budget is not the constraint; price is. |

---

**READ-ONLY FORENSIC AUDIT COMPLETE — NO EXTERNAL CHANGES MADE**
