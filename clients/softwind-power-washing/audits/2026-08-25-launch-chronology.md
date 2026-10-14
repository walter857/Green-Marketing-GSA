# Softwind Power Washing — Launch Chronology

**Account:** Softwind Power Washing - Live · `152-172-5229` (`1521725229`)
**Service:** Power Washing · vertical `similar-local-service` (scope approved: Walter Correa)
**Audit snapshot:** 2026-08-25 16:57:08 America/New_York
**Mode:** READ ONLY. No external change was made.

---

## 1. Correction to the brief before anything else

The work order described **one** campaign named `Power Washing` on a **$33/day** budget.
The account actually contains **two enabled Search campaigns**, each on its own
**$41.11/day** budget:

| Campaign | ID | Created | Status | Budget ID | Daily budget |
|---|---|---|---|---|---|
| Power Washing | `24103511039` | 2026-08-04 09:22:12 | ENABLED / SERVING / LEARNING | `15764226923` | $41.11 |
| Power Washing #2 | `24145053510` | 2026-08-18 09:24:13 | ENABLED / SERVING / ELIGIBLE | `15802443075` | $41.11 |

Combined committed daily budget is **$82.22**, not $33. Both budgets are unshared
(`explicitly_shared: false`, `reference_count: 1`) and both use STANDARD delivery.

The 12 expected SKAG ad groups are not in one campaign. They are **split 6 and 6 across
the two campaigns**, with one ad group duplicated and one missing entirely. Section 5
covers this.

---

## 2. Campaign chronology — Power Washing (`24103511039`)

Recovered from `change_event` (API cap: 30 days, window 2026-07-27 → 2026-08-25),
cross-checked against daily metrics. Every timestamp is account-local (America/New_York).

| When | Event | Evidence |
|---|---|---|
| **2026-08-04 09:22:12** | **Campaign created** | `campaign.start_date_time` |
| 2026-08-04 13:10:35 | Ad schedule created — **7 dayparts, Monday through Sunday** | `change_event` CREATE ×7 on `campaignCriteria/24103511039~3x3268` |
| 2026-08-04 15:16:52 | Location targeting changed **PRESENCE_OR_INTEREST → PRESENCE** | `change_event` old→new on `geo_target_type_setting.positive_geo_target_type` |
| 2026-08-04 19:23:04 | `manual_cpc.enhanced_cpc_enabled` updated | `change_event` |
| **2026-08-05** | **First impression ever (3 impressions)** | daily metrics |
| 2026-08-06 12:51:35 | Device criterion updated | `change_event` |
| 2026-08-06 13:04:40–13:04:46 | **Three legacy ad groups paused** — Driveway Patio Concrete Washing, Pressure & Power Washing, Soft & House Washing | `change_event` UPDATE `status` ×3 |
| 2026-08-07 08:39:28 | Ad schedule torn down and rebuilt (7 removed, 7 created) | `change_event` REMOVE ×7 + CREATE ×7 |
| **2026-08-07 16:17:45** | **Sunday daypart removed** (`campaignCriteria/24103511039~363272`) | `change_event` REMOVE |
| **2026-08-07 16:08:18** | **Max CPC bid limit added: none → $5.00** | `change_event` `target_spend.cpc_bid_ceiling_micros` |
| **2026-08-16 23:42:44** | **Max CPC bid limit removed: $5.00 → none** | `change_event` `target_spend.cpc_bid_ceiling_micros` |
| **2026-08-17** | **First click ever, first spend ever — 1 click, $5.71** | daily metrics |
| **2026-08-25 16:57** | Audit snapshot | — |

### The bid-ceiling story is the spine of this account's history

Delivery lines up with the two ceiling changes exactly:

- **2026-08-05 → 2026-08-16** — a $5.00 CPC ceiling was in force from 08-07. The local
  top-of-page bid range for this service is **$8.66–$23.91** (volume-weighted, Keyword
  Planner, this exact geo). A $5.00 cap sits below the bottom of that range. Result:
  1–4 impressions a day, **zero clicks, zero spend for 12 straight days.**
- **2026-08-16 23:42** — the ceiling was removed entirely.
- **2026-08-17** — first click in the account's life, $5.71.
- Then CPC escalated with nothing holding it back: **$22.13 (08-19) → $22.11 (08-24) →
  $40.58 and $40.07 (08-25)**, peaking at a **single $54.49 click**.

The account has never been bid correctly. It went straight from *capped far too low to
compete* to *entirely uncapped*. Neither state was ever inside the defensible range.

---

## 3. Campaign chronology — Power Washing #2 (`24145053510`)

| When | Event | Evidence |
|---|---|---|
| **2026-08-18 09:24:13** | Campaign + budget `15802443075` created, **status PAUSED** | `change_event` CREATE |
| 2026-08-18 09:24:22 | 15 ad groups created | `change_event` CREATE ×15 |
| 2026-08-18 09:26:08 | 12 ad groups paused | `change_event` UPDATE `status` ×12 |
| 2026-08-18 09:26:11 | 47 campaign negative keywords created | `change_event` CREATE |
| **2026-08-18 09:28:21** | **Campaign enabled — 4 minutes 8 seconds after creation** | `change_event` `status` PAUSED → ENABLED |
| **2026-08-19** | First impression (2) | daily metrics |
| **2026-08-24** | First click, $22.11 | daily metrics |

For the record: this campaign went from created to serving in **4 minutes**, without a
create-paused → readback → separate-enable cycle. That is noted as history, not as a
finding against this work order.

---

## 4. First-delivery milestones — the answer to questions 1–6

| Milestone | Date | Detail |
|---|---|---|
| Campaign created | **2026-08-04 09:22:12** | `Power Washing`. Second campaign 2026-08-18 09:24:13. |
| First enabled | **2026-08-04 09:22:12** | Campaign 1 was created enabled — the earliest daily row (2026-08-04) already carries impression-share data, so it was eligible that day. Campaign 2 was created paused and enabled 2026-08-18 09:28:21. |
| **First impression** | **2026-08-05** | 3 impressions, campaign 1. Account had zero impressions on 08-04. |
| **First click** | **2026-08-17** | 1 click. Campaign 2's first click: 2026-08-24. |
| **First spend** | **2026-08-17** | $5.71. Same event as the first click. |
| **First conversion** | **NONE** | Zero conversions and zero all-conversions across every action, every day, all time. |
| First phone conversion | **NONE** | `metrics.phone_calls` = 0 across 107 phone impressions. |
| First form conversion | **NONE** | `Softwind Power Washing \| Submission Lead Form` all_conversions = 0. |

### Elapsed counters

| Counter | Value |
|---|---|
| Days since campaign 1 created (08-04 → 08-25) | **22** |
| Days since campaign 2 created (08-18 → 08-25) | **8** |
| Days with ≥1 impression | **17** |
| Days with ≥1 click | **4** (08-17, 08-19, 08-24, 08-25) |
| Days with >$0 spend | **4** (same days) |
| Days with a conversion | **0** |
| Calendar days in range with **zero delivery** | **5** — 08-04, 08-09, 08-14, 08-16, 08-23 |

**08-09, 08-16 and 08-23 are all Sundays.** They are zero because the Sunday daypart was
deleted on 2026-08-07 16:17:45, not because demand was absent. Sunday has recorded
**0 impressions all-time** and does not even appear in the day-of-week segment.

---

## 5. Expected versus observed architecture

| Item | Expected (per work order) | Observed | Difference |
|---|---|---|---|
| Campaigns | 1 | **2** | +1 unplanned campaign |
| Daily budget | $33 | **$41.11 × 2 = $82.22** | +$49.22/day |
| Active revamp ad groups | 12 | **12 enabled**, but split 6 / 6 across two campaigns | structurally different |
| Distinct SKAG intents live | 12 | **11** | `House Washing Company Near Me` is PAUSED in **both** campaigns |
| Duplicated ad groups | 0 | **1** — `Power Washing Services Near Me` is enabled in both campaigns | direct self-overlap |
| Keyword rows live | 21 | **21** | matches, but 9 in campaign 1 and 12 in campaign 2 |
| Distinct keyword texts live | 12 | **11** | `house washing company near me` not serving anywhere |
| RSAs live | 24 | **24** | matches — exactly 2 per live ad group |
| Total ad groups in account | 12 | **30** | 12 enabled, 18 paused (12 revamp duplicates + 6 legacy) |
| Total RSAs in account | 24 | **54** | 44 enabled, 10 paused |
| Total keyword rows | 21 | **214** | 21 live, 193 sitting in paused ad groups |

### Live ad-group map

**Power Washing (`24103511039`)** — the *power washing* phrasing family, 6 enabled:
Power Washing Near Me · Power Washing Services Near Me · Power Washing Company Near Me ·
Power Washing Islip · Power Washing West Islip · Power Washing Dix Hills

**Power Washing #2 (`24145053510`)** — the *pressure / house / soft washing* family, 6 enabled:
Residential Pressure Washing Near Me · House Pressure Washing Estimate ·
Driveway Pressure Washing Near Me · Patio Pressure Washing Near Me ·
Soft House Washing Near Me · **Power Washing Services Near Me** ← duplicate of campaign 1

---

## 6. Legacy architecture — what the revamp turned off

The three pre-revamp ad groups still exist, paused, in **both** campaigns. They are not
empty shells: they hold **72 distinct in-scope BOFU keyword texts** in Phrase and Exact.

| Legacy ad group | Keyword families it covered |
|---|---|
| **Pressure & Power Washing** | power washing company / contractor / estimate / quote / service / long island · **pressure washing company / contractor / estimate / quote / service / long island** · professional pressure washing · residential power & pressure washing service · exterior pressure washing service |
| **Soft & House Washing** | house washing company / contractor / **near me** / quote / service / long island · house soft washing · soft washing company / contractor / estimate / **near me** / quote / service / long island |
| **Driveway Patio Concrete Washing** | driveway, patio, concrete, **paver**, walkway and outdoor-surface cleaning / power washing / pressure washing service |

Legacy delivery before they were paused was minimal — `Pressure & Power Washing` 3
impressions (08-05), `Soft & House Washing` 1 impression (08-06) — because the campaign
was only two days old when they were switched off on 2026-08-06.

**This matters for the expansion plan.** The revamp narrowed the account from ~72 BOFU
keyword texts to **11 live ones**, and in doing so it dropped the entire *"pressure
washing"* phrasing family as a targeted keyword. The account still receives that demand,
but only as close variants routed into *power washing* ad groups showing *power washing*
ad copy — and that traffic converts to clicks at **0%** (15 impressions, 0 clicks).

---

## 7. What could not be recovered

- `change_event` is capped at 30 days by the API. The window used (2026-07-27 → 2026-08-25)
  fully covers both campaigns, so nothing was lost to the cap — but the **campaign CREATE
  event for `24103511039` itself does not appear** in the returned event set. Its creation
  time is taken from `campaign.start_date_time` = **2026-08-04 09:22:12**, which is
  authoritative for when the campaign began, and is corroborated by the first ad-schedule
  criteria being created the same day at 13:10:35.
- **Keyword-level `search_budget_lost_impression_share` is not selectable** from
  `keyword_view` or `ad_group` in Google Ads API v25. Budget-loss diagnosis is therefore
  campaign-level only. Stated as unavailable, not estimated.
- **Keyword position estimates** (`first_page_cpc`, `top_of_page_cpc`,
  `first_position_cpc`) returned **null for every one of the 214 keyword rows**. Bid
  benchmarks in this audit come from Keyword Planner top-of-page estimates for the exact
  8-city geo instead.
- **Auction Insights is not exposed through the Google Ads API.** No competitor data is
  reported and none was invented.
