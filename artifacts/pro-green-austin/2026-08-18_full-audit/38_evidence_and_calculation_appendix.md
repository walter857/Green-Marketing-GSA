# 38 — Evidence and Calculation Appendix

**Pro Green - Austin - Live | `7380491929` | outdoor design & build**
**Reporting period: Monday 2026-08-17 through Sunday 2026-08-23**
**Prepared: 2026-08-24**
**Task class: READ-ONLY REPORTING AND ANALYSIS**

> **NO EXTERNAL CHANGES WERE MADE.** Every Google Ads call in this run was a
> `GoogleAdsService.search` or `search_stream` read. No `mutate`, no `validate_only` mutate,
> no fingerprint, no approval bundle. Nothing was created, edited, paused, enabled or removed.

---

## 1. Identity confirmation

Fresh read-only lookup, `FROM customer`, before any other work.

| Field | Required | Observed | Result |
|---|---|---|---|
| `customer.descriptive_name` | `Pro Green - Austin - Live` | `Pro Green - Austin - Live` | exact match |
| `customer.id` | `7380491929` | `7380491929` | exact match |
| `- live` marker | required | present | pass |
| `customer.manager` | must be false | `false` | pass — not a manager account |
| `customer.test_account` | must be false | `false` | pass — not a test account |
| `customer.currency_code` | USD | `USD` | pass |
| `customer.time_zone` | — | `America/New_York` | recorded |
| `customer.status` | — | `ENABLED` | recorded |
| Service | `outdoor design & build` | work order + client profile agree | pass |
| Vertical | `hardscaping` (core vertical) | `hardscaping` | pass, no scope approval required |
| Monthly budget limit | `$2,000.00` | work order `monthly_budget_cap: 2000.00` | pass |

`clients/pro-green-austin/work-order.yaml` and `clients/pro-green-austin/client.yaml` both validate
and agree on account name, child customer ID, vertical and exact service. The manager ID
`3373711342` is recorded in both files and was **never** used as the operating customer ID.

### Query timestamps

| Read | UTC timestamp |
|---|---|
| Identity confirmation | `2026-08-24T22:54:43.520572+00:00` |
| Structural inventory (campaigns, ad groups, keywords, negatives, ads, assets, conversions, shared sets) | `2026-08-24T22:57:18.984859+00:00` |
| Performance, search terms, change history | same session, immediately following |

**Account timezone:** `America/New_York`. Every `segments.date` boundary in this report is an
account-timezone calendar day.

**Austin local interpretation:** the served market is `America/Chicago`, one hour behind the
account timezone. An account-timezone day therefore runs from **23:00 the previous night to
23:00 Austin local**. The one-hour offset is a real reporting artifact of this account and is why
the ad schedule reads `09:00–18:00` in Google Ads but delivers `08:00–17:00` in Austin.

### Concurrent-process check

`change_event`, 2026-08-01 → 2026-08-24, 168 rows (the API caps this resource at roughly 30 days).

| Actor | Rows | Client type | What |
|---|---|---|---|
| `access@greenmarketingfl.com` | 164 | `GOOGLE_ADS_API` | the approved Green Marketing executions listed in §2 |
| `adwords%clickcease.com@gtempaccount.com` | 4 | `UNKNOWN` | 4 `IP_BLOCK` campaign criteria created 2026-08-11 and 2026-08-14 |

**Latest change of any kind: `2026-08-22 10:09:43` account time.** Nothing has touched the account
in the 60 hours before this report. No second script, no auto-apply subscription, no Google
recommendation applied. **No concurrent process is modifying this account.**

---

## 2. Effective timestamps of the approved optimizations

Established from execution receipts and corroborated against live `change_event` rows. Server-side
`validate_only` requests, local file creation, read-only queries, ClickCease tracking-template
activity, unapproved plans and unexecuted fingerprints are **not** counted as optimization events.

| # | Change | Receipt | Effective (account time) | `change_event` corroboration |
|---|---|---|---|---|
| 1 | Budget reallocation (2 budgets) | `13_execution_qa_receipt.md` | 2026-08-19 | 2 × `CAMPAIGN_BUDGET UPDATE` on 2026-08-19 |
| 2 | CPC ceiling $22.00 + parent-asset exclusions (2 campaigns) | `13` | 2026-08-19 | 2 × `CAMPAIGN UPDATE` on 2026-08-19 |
| 3 | Ad schedule rebuilt (14 removed, 14 created) | `13` | 2026-08-19 | 14 `REMOVE` + 14 of the 30 `CREATE` `CAMPAIGN_CRITERION` on 2026-08-19 |
| 4 | 16 campaign negatives added (8 phrases × 2 campaigns) | `13` | 2026-08-19 | remaining 16 `CREATE` `CAMPAIGN_CRITERION` on 2026-08-19 |
| 5 | 7 blocking shared negatives removed | `13` | 2026-08-19 | not tracked by `change_event`; verified structurally — see §7 |
| 6 | 6 conversion actions demoted, column 9 → 3 | `13` | 2026-08-19 | not tracked by `change_event`; verified structurally — see §5 |
| 7 | 24 new RSAs created PAUSED | `18_phase2_create_paused_qa_receipt.md` | 2026-08-20 06:32 UTC = 02:32 acct | 24 × `AD_GROUP_AD CREATE` on 2026-08-20 |
| 8 | 24 new RSAs enabled | `20_phase2_enable_qa_receipt.md` | 2026-08-20 14:28:33 UTC = **10:28 acct** | 24 × `AD_GROUP_AD UPDATE` on 2026-08-20 |
| 9 | 34 campaign-negative phrases × 2 campaigns = 68 objects | `clients/pro-green-austin/receipts/exec-campaign-negatives-2026-08-22.json` | 2026-08-22 14:09:42 UTC = **10:09:43 acct** | 68 × `CAMPAIGN_CRITERION CREATE` on 2026-08-22 |

**Not optimization events, and excluded:**

- `29_validate_only_receipt.md` — a server-side dry run on 2026-08-22 13:48 UTC that wrote nothing.
- `clients/pro-green-austin/plans/adgroup-negatives-mtd-2026-08-21.json` — never executed; the 246
  ad-group negatives now live were already present at the 2026-08-18 audit.
- ClickCease's 4 IP-block criteria (2026-08-11, 2026-08-14) and its tracking-template activity.

### Conflict between local documentation and the live account — resolved in favour of the live account

`MEMORY.md` records the 68-object campaign-negative plan as *"awaits approval"* and its round-1
fingerprints as void. **That note is stale.** The live account proves the plan was executed:

- `receipts/exec-campaign-negatives-2026-08-22.json` records `"mode": "LIVE WRITE"`,
  `executed_at_utc: 2026-08-22T14:09:42`, 68 operations, `partial_failure: false`, 68 returned
  resource names.
- Live campaign negatives now total **156** (78 per campaign). The arithmetic reconciles exactly:
  72 before Phase 1 → +16 Phase 1 → 88 → +68 → **156**.
- All **34** phrases are present on **both** campaigns as PHRASE. **0 missing.**
- 68 matching `CAMPAIGN_CRITERION CREATE` change events exist on 2026-08-22.

**The report uses the live state.** The fingerprints named in the task
(`063EE720BAF3` / `628D3E61A9C2`) were the ones that authorised that execution on 2026-08-22; they
authorise nothing in this reporting task, and nothing was executed here. The earlier round-1
fingerprints `2D87A5249784` / `4EEF81C7F2F5` remain void and unused.

---

## 3. Reporting windows

| Window | Dates (account timezone) | Days | Purpose |
|---|---|---|---|
| A | 2026-08-17 → 2026-08-23 | 7 complete | current weekly report |
| B | 2026-08-10 → 2026-08-16 | 7 complete | previous week comparison |
| C | 2026-08-01 → 2026-08-18 | 18 complete | clean pre-optimization baseline |
| D | 2026-08-19 → 2026-08-20 | 2 complete | transition — changes implemented, kept separate |
| E | 2026-08-21 → 2026-08-23 | 3 complete | first clean post-change period |
| F1 / F2 | 2026-08-14 → 16 vs 2026-08-21 → 23 | 3 + 3 | matched Friday–Sunday |
| G | 2026-08-24 | partial | **PARTIAL CURRENT DAY — DATA MAY BE DELAYED** |

Window G is never combined with any completed-day comparison.

---

## 4. Account performance by window

Impression-share metrics are **not additive across days**, so each window's share figures come from
a single window-scoped query, not from summing daily rows.

| Window | Impr | Clicks | CTR | Cost | Avg CPC | Primary conv | CVR | CPL | All conv | Search IS | Lost IS (budget) | Lost IS (rank) | Invalid clicks | Invalid rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A 17–23 | 832 | 20 | 2.40% | $369.43 | $18.47 | 0.00 | 0.00% | N/A — no conversions | 2.00 | 53.88% | 8.02% | 38.10% | 14 | 41.18% |
| B 10–16 | 652 | 19 | 2.91% | $426.60 | $22.45 | 0.00 | 0.00% | N/A — no conversions | 13.00 | 46.43% | 30.28% | 23.28% | 60 | 75.95% |
| C 01–18 | 1,502 | 49 | 3.26% | $1,171.22 | $23.90 | 1.00 | 2.04% | $1,171.22 | 34.00 | 44.11% | 30.76% | 25.13% | 74 | 60.16% |
| D 19–20 | 296 | 3 | 1.01% | $57.40 | $19.13 | 0.00 | 0.00% | N/A — no conversions | 0.00 | 60.23% | 0.00% | 39.77% | 10 | 76.92% |
| E 21–23 | 314 | 10 | 3.18% | $186.36 | $18.64 | 0.00 | 0.00% | N/A — no conversions | 1.00 | 68.35% | **0.00%** | 31.65% | 3 | 23.08% |
| F1 14–16 | 167 | 9 | 5.39% | $192.53 | $21.39 | 0.00 | 0.00% | N/A — no conversions | 0.00 | 36.55% | 49.24% | 14.21% | 4 | 30.77% |
| G 24 *(partial)* | 140 | 5 | 3.57% | $100.74 | $20.15 | 0.00 | 0.00% | N/A — no conversions | 0.00 | 52.38% | 0.00% | 47.62% | 1 | 16.67% |
| MTD 01–23 | 2,112 | 62 | 2.94% | $1,414.98 | $22.82 | 1.00 | 1.61% | $1,414.98 | 35.00 | 48.31% | 24.25% | 27.44% | 87 | 58.39% |

`search_top_impression_share` and `search_absolute_top_impression_share` are **not selectable on
the `customer` resource** in Google Ads API v25 (`PROHIBITED_METRIC_IN_SELECT_OR_WHERE_CLAUSE`).
They are reported per campaign in `33_campaign_comparison.csv` instead. This is an API limitation,
not missing data.

### Formulas

```
CTR                  = clicks / impressions
Average CPC          = cost / clicks
Conversion rate      = current-primary conversions / clicks
Cost per conversion  = cost / current-primary conversions      (N/A when conversions = 0)
Budget utilization   = cost / combined approved daily budget
Invalid click rate   = invalid clicks / (valid clicks + invalid clicks)   [Google-reported]
```

A `$0.00` CPA is never printed. Zero conversions is written `N/A — no conversions`.

### Cross-check — account totals vs the sum of campaigns

| Window | Account cost | Σ campaigns | Delta | Account clicks | Σ clicks | Account impr | Σ impr |
|---|---:|---:|---:|---:|---:|---:|---:|
| MTD 01–23 | $1,414.98 | $1,414.98 | $0.0000 | 62 | 62 | 2,112 | 2,112 |
| A 17–23 | $369.43 | $369.43 | $0.0000 | 20 | 20 | 832 | 832 |
| E 21–23 | $186.36 | $186.36 | $0.0000 | 10 | 10 | 314 | 314 |
| G 24 | $100.74 | $100.74 | $0.0000 | 5 | 5 | 140 | 140 |

**Zero discrepancy at every level.** Daily rows also sum to the window totals exactly. No
reconciliation note is required.

---

## 5. Fair conversion comparison

### The three actions currently counted

Read fresh from `conversion_action`. Sixteen actions exist; **exactly three carry
`include_in_conversions_metric = true`** and therefore form the Conversions column:

| ID | Name | Type | Event | Minimum |
|---|---|---|---|---|
| `7644242327` | WC leads | `UPLOAD_CLICKS` | one website form submission (WhatConverts upload) | — |
| `6885610317` | Progreen - Lp - Phone Call Leads | `WEBSITE_CALL` | one connected call from the website | 30 s |
| `6566620547` | Calls from ads | `AD_CALL` | one connected call from the ad | 60 s |

**Important nuance.** Eight actions still read `primary_for_goal = true`. The extra five are
Google-hosted `Local actions – Website visits / Other engagements / Directions / Menu views` and
`Clicks to call`. Google keeps that flag set on its own hosted actions by default and it cannot be
cleared the same way; all five carry `include_in_conversions_metric = false` and contribute
**nothing** to the Conversions column. The biddable, reported lead definition is exactly the three
actions above — which is what receipt `13` asserted and what the live account still shows.

### Segmented conversion performance, August 1–24

| Action ID | Name | All conversions | Counted in Conversions column |
|---|---|---:|---:|
| `7644242327` | **WC leads** *(current primary)* | **1.00** | **1.00** |
| `6611700177` | Local actions – Other engagements | 26.00 | 0.00 |
| `6607912702` | Local actions – Website visits | 7.00 | 0.00 |
| `6626900593` | Local actions – Directions | 1.00 | 0.00 |

The other twelve actions — including all six demoted on 2026-08-19 — recorded **zero** conversions
in August.

**Like-for-like current-primary lead conversions, by window:**

| Window | Form submissions (`WC leads`) | Connected website calls (`Lp - Phone Call Leads`) | Calls from ads (`Calls from ads`) | Total |
|---|---:|---:|---:|---:|
| C 01–18 | 1.00 (Aug 4) | 0.00 | 0.00 | **1.00** |
| B 10–16 | 0.00 | 0.00 | 0.00 | **0.00** |
| A 17–23 | 0.00 | 0.00 | 0.00 | **0.00** |
| D 19–20 | 0.00 | 0.00 | 0.00 | **0.00** |
| E 21–23 | 0.00 | 0.00 | 0.00 | **0.00** |
| F1 14–16 | 0.00 | 0.00 | 0.00 | **0.00** |
| G 24 *(partial)* | 0.00 | 0.00 | 0.00 | **0.00** |

The three streams are reported separately and never added to an overlapping action. Local actions,
website visits, directions and menu views are **not** treated as leads.

### Has Google retrospectively restated historical Conversions? — Yes.

Tested on a window that lies entirely **before** the 2026-08-19 cleanup: 2026-05-01 → 2026-07-31,
when nine actions fed the column.

| Measure | Value |
|---|---:|
| Reported `metrics.conversions` for May–July | **2.00** |
| Σ `all_conversions` for the current three primary actions | **2.00** |
| Σ `all_conversions` for every action | 6.00 |
| `Clicks to call` (`6607906201`) — primary *before* the cleanup, demoted now | 1.00, reported as **0.00** |

`Clicks to call` recorded one conversion in that pre-change window and would have been counted
under the old nine-action definition, yet the Conversions column reports 2.00, not 3.00.
**Google applies the current `include_in_conversions_metric` setting retroactively to historical
reporting.** Consequently the reported Conversions column is already like-for-like across the
pre-change and post-change periods, and the normalized figures in the table above match it exactly
on every August date.

Separately, the six actions demoted on 2026-08-19 recorded **zero** conversions anywhere in August,
so the cleanup removed no August volume at all. Both facts point the same way: the pre/post
conversion comparison in this report is sound.

**What cannot be claimed.** With **one** current-primary conversion in the whole of August and
**zero** in both comparison weeks, no conversion-rate or cost-per-lead improvement can be
demonstrated, and none is claimed. CPL is reported as `N/A — no conversions`.

### One measurement limitation, stated once

Form leads on 23 of the 24 destinations still carry no click identifier (`SPEC-001` open) and the
offer-page form-submit tag is still unverified (`SPEC-002` open). Website form fills can therefore
happen without being attributed to Google Ads. Reported lead counts are a floor, not a ceiling —
so the honest reading of "zero conversions this week" is "zero *measured* conversions", and the
priority in §11 of the client report reflects that.

---

## 6. Original ads vs new ads

Cohorts split by the exact 24 ad resource IDs frozen in `20_phase2_enable_qa_receipt.md` §6.

| Cohort | Ads | Status | Approval | Review | Policy topics |
|---|---:|---|---|---|---:|
| Original (feature/process-led) | 24 | 24 ENABLED | 24 APPROVED | 24 REVIEWED | 0 |
| New (outcome-led) | 24 | 24 ENABLED | 24 APPROVED | 24 REVIEWED | 0 |

Live total: **48 ENABLED RSAs, exactly 2 per ad group across all 24 ad groups. Zero disapproved,
zero limited, zero paused.**

### Primary comparison — August 21–23 (first clean post-change window)

| Metric | Original | New |
|---|---:|---:|
| Ads | 24 | 24 |
| Impressions | 131 | 183 |
| Share of ad impressions | 41.7% | **58.3%** |
| Clicks | 7 | 3 |
| Share of clicks | 70.0% | 30.0% |
| CTR | 5.34% | 1.64% |
| Cost | $144.99 | $41.37 |
| Average CPC | $20.71 | $13.79 |
| Current-primary conversions | 0.00 | 0.00 |
| Conversion rate | 0.00% | 0.00% |
| Cost per conversion | N/A — no conversions | N/A — no conversions |

### Partial update — August 24 *(PARTIAL CURRENT DAY — DATA MAY BE DELAYED)*

| Metric | Original | New |
|---|---:|---:|
| Impressions | 64 (45.7%) | 76 (54.3%) |
| Clicks | 2 (40.0%) | 3 (60.0%) |
| CTR | 3.12% | **3.95%** |
| Cost | $43.36 | $57.38 |
| Average CPC | $21.68 | $19.13 |

### Verdict — no winner may be called

**Sample size: 314 impressions and 10 clicks in total across both cohorts over three days.** The
CTR gap on August 21–23 rests on a 7-click versus 3-click split. One click either way moves each
cohort's CTR by roughly 0.8 to 0.5 percentage points. On the very next day the ranking **reverses**
— new ads out-click original ads 3 to 2 and post the higher CTR. That is the signature of noise,
not of a message difference.

**Verdict: `Too early`.** No statistically reliable CTR winner. No conversion winner — the
previously documented threshold of approximately **15 conversions in 30 days** has not been met;
the account has **1** in 24 days.

**Is Google starving the new ads?** No. The new cohort took **58.3%** of ad impressions on
August 21–23 and **54.3%** on August 24. Impression delivery is healthy and roughly even, so the
test is running fairly and will accumulate evidence at a normal rate.

### Ad-group verdicts, August 21–23

Eleven of the 24 live ad groups drew no impressions at all in the window. Of the 13 that did:

| Ad group | Orig impr / CTR | New impr / CTR | Orig conv | New conv | Verdict |
|---|---|---|---:|---:|---|
| Hardscape › Driveways \| Near Me | 2 / 0.00% | 2 / 0.00% | 0.0 | 0.0 | Too early |
| Hardscape › Hardscaping \| BOFU | 5 / 20.00% | 12 / 0.00% | 0.0 | 0.0 | Too early |
| Hardscape › Hardscaping \| Near Me | 5 / 0.00% | 4 / 0.00% | 0.0 | 0.0 | Too early |
| Hardscape › Patios \| Near Me | 4 / 25.00% | 1 / 0.00% | 0.0 | 0.0 | Too early |
| Hardscape › Pavers \| BOFU | 9 / 0.00% | 19 / 5.26% | 0.0 | 0.0 | Too early |
| Hardscape › Retaining Walls \| BOFU | 2 / 0.00% | 8 / 0.00% | 0.0 | 0.0 | Too early |
| Outdoor Living › Artificial Turf \| BOFU | 9 / 0.00% | 12 / 8.33% | 0.0 | 0.0 | Too early |
| Outdoor Living › Artificial Turf \| Near Me | 2 / 0.00% | 1 / 0.00% | 0.0 | 0.0 | Too early |
| Outdoor Living › Landscape Design \| BOFU | 52 / 7.69% | 86 / 1.16% | 0.0 | 0.0 | Directional only |
| Outdoor Living › Landscape Design \| Near Me | 17 / 5.88% | 14 / 0.00% | 0.0 | 0.0 | Directional only |
| Outdoor Living › Landscape Lighting \| BOFU | 16 / 0.00% | 16 / 0.00% | 0.0 | 0.0 | Directional only |
| Outdoor Living › Outdoor Living \| Near Me | 8 / 0.00% | 2 / 0.00% | 0.0 | 0.0 | Too early |
| Outdoor Living › Pergolas \| BOFU | 0 / n/a | 6 / 0.00% | 0.0 | 0.0 | Too early |

Sufficiency rule applied: `Too early` below 30 impressions or 5 clicks; `Directional only` below
300 impressions or 30 clicks; `Enough data to review` above both. **No ad group reaches
`Enough data to review`.**

`ad_strength` currently reads 19 EXCELLENT, 22 AVERAGE, 5 GOOD, 2 POOR across the 48 live ads. It
is a Google diagnostic, not a business result, and no decision in this report rests on it.

---

## 7. Live inventory verification

Every line below was read fresh from the API in this run.

| Item | Live state | Verified |
|---|---|---|
| Enabled campaigns | 2 — `24053505501` Hardscape Construction, `24053505504` Outdoor Living & Design | yes |
| Other campaigns | 8 PAUSED, including `Leads-Performance Max-Austin` — none serving | yes |
| Daily budgets | $26.31 (Hardscape) + $39.47 (Outdoor Living) = **$65.78**; neither budget is shared; STANDARD delivery | yes |
| Bidding | `TARGET_SPEND` on both, unchanged — no learning reset | yes |
| Maximum CPC | **$22.00** on both (`target_spend.cpc_bid_ceiling_micros = 22000000`) | yes |
| Campaign serving status | `SERVING` on both | yes |
| Ad groups | 24, all ENABLED, 12 per campaign | yes |
| Positive keywords | **48**, all ENABLED — 24 PHRASE + 24 EXACT | yes |
| Ad-group negatives | 246, all PHRASE | yes |
| Campaign negatives | **156** — 78 per campaign, all PHRASE | yes |
| Linked shared negative lists | 3 per campaign — `States` `10670794921`, `General` `10670796064`, `Names` `10673711933` | yes |
| Account-level negative list | `11260450591`, 290 criteria. Reports `member_count 0` and never appears in `campaign_shared_set` — that is normal for `ACCOUNT_LEVEL_NEGATIVE_KEYWORDS`, which applies account-wide regardless | yes |
| Total shared criteria | **8,716** — the 7 Phase-1 removals have persisted (8,723 → 8,716) | yes |
| Ads | **48 ENABLED**, 2 per ad group, 48 APPROVED, 48 REVIEWED, **0 disapproved, 0 limited, 0 paused** | yes |
| Final URLs | 13 unique destinations; 12 offer-page hosts plus the one approved main-site exception (`Hardscaping \| Near Me`) | yes |
| Locations | 24 positive per campaign, **0 exclusions**, `PRESENCE` targeting on both | yes |
| Ad schedule | 14 criteria, 7 per campaign, all days `09:00–18:00` account time = `08:00–17:00` Austin, no bid modifiers | yes |
| Networks | Google Search **on**; Search Partners **off**; Display **off** | yes |
| Languages | English (`en`) on both | yes |
| Devices | Desktop, Mobile, Tablet — all targeted, no exclusions | yes |
| IP exclusions | 4 criteria (2 per campaign), created by ClickCease 2026-08-11 and 2026-08-14 | yes |
| Primary conversion actions | 3 counted (§5) | yes |
| Sitelinks | 12 campaign-level (6 per campaign) | yes |
| Callouts | 16 campaign-level (8 per campaign) | yes |
| Structured snippets | 2 campaign-level (1 per campaign) | yes |
| Call assets | 2 (1 per campaign) | yes |
| Business logos | 2 (1 per campaign) | yes |
| Parent-asset exclusions | `[SITELINK, STRUCTURED_SNIPPET]` on both campaigns | yes |
| Auto-created account assets blocked by that exclusion | `Services In Dallas`, `Services In Austin`, `Services In Houston` sitelinks and the `Highlights` snippet containing the unverified `Over 20 Years Of Experience` | yes |
| Auto-tagging | enabled | yes |
| Google recommendations | none applied; no auto-apply subscription | yes |

### Keyword serving diagnostics

Four keywords read `RARELY_SERVED` — `outdoor living design and build contractor` and
`outdoor fire pit installation company`, each in PHRASE and EXACT. This is a Google low-search-volume
flag, not a quality problem, and no action is proposed in this read-only task.

---

## 8. Quality Score review

| Measure | 2026-08-18 audit | 2026-08-24 live | Change |
|---|---:|---:|---|
| Positive keywords | 48 | 48 | none |
| Quality Score populated | 6 | 6 | none |
| Not enough data | 42 | 42 | none |
| Expected CTR `BELOW_AVERAGE` | 6 | 6 | none |
| Ad relevance `ABOVE_AVERAGE` | 2 | **4** | **+2 improved** |
| Ad relevance `AVERAGE` | 4 | 2 | −2 (moved up) |
| Landing-page experience `AVERAGE` | 4 | 4 | none |
| Landing-page experience `BELOW_AVERAGE` | 2 | 2 | none |

**Improved — 2 of 48:**

| Keyword | Match | Ad group | Change |
|---|---|---|---|
| `landscape designers near me` | PHRASE | Landscape Design \| Near Me | QS **4 → 5**; ad relevance AVERAGE → **ABOVE_AVERAGE** |
| `landscape designers near me` | EXACT | Landscape Design \| Near Me | QS **4 → 5**; ad relevance AVERAGE → **ABOVE_AVERAGE** |

**Declined: none. Unchanged: 46 of 48.**

An unpopulated Quality Score is reported as `not enough data`, never as a score of zero. Forty-two
of the 48 keywords have never accumulated enough matched-auction history to be scored — 26 of them
drew zero impressions across August 1–23.

### Keywords with a populated score

| Keyword | Match | Ad group | QS | Expected CTR | Ad relevance | Landing page |
|---|---|---|---:|---|---|---|
| `patio contractors near me` | PHRASE | Patios \| Near Me | 5 | BELOW_AVERAGE | ABOVE_AVERAGE | AVERAGE |
| `patio contractors near me` | EXACT | Patios \| Near Me | 5 | BELOW_AVERAGE | ABOVE_AVERAGE | AVERAGE |
| `landscape designers near me` | PHRASE | Landscape Design \| Near Me | 5 | BELOW_AVERAGE | ABOVE_AVERAGE | AVERAGE |
| `landscape designers near me` | EXACT | Landscape Design \| Near Me | 5 | BELOW_AVERAGE | ABOVE_AVERAGE | AVERAGE |
| `paver installation near me` | PHRASE | Pavers \| Near Me | 2 | BELOW_AVERAGE | AVERAGE | BELOW_AVERAGE |
| `paver installation near me` | EXACT | Pavers \| Near Me | 2 | BELOW_AVERAGE | AVERAGE | BELOW_AVERAGE |

Expected CTR is `BELOW_AVERAGE` on all six — the same finding that motivated the new-ad test. That
test is only four days old and cannot yet have moved these ratings.

### Highest spend without a current-primary conversion, August 1–23

| Cost | Impr | Clicks | CTR | Avg CPC | Keyword | Match | Ad group |
|---:|---:|---:|---:|---:|---|---|---|
| $384.36 | 831 | 22 | 2.65% | $17.47 | `residential landscape design company` | PHRASE | Landscape Design \| BOFU |
| $230.91 | 279 | 7 | 2.51% | $32.99 | `paver installation company` | PHRASE | Pavers \| BOFU |
| $142.61 | 141 | 5 | 3.55% | $28.52 | `residential hardscape contractor` | PHRASE | Hardscaping \| BOFU |
| $90.70 | 124 | 4 | 3.23% | $22.68 | `artificial turf installation company` | PHRASE | Artificial Turf \| BOFU |
| $89.61 | 138 | 4 | 2.90% | $22.40 | `landscape designers near me` | EXACT | Landscape Design \| Near Me |
| $86.93 | 69 | 5 | 7.25% | $17.39 | `outdoor living contractors near me` | PHRASE | Outdoor Living \| Near Me |
| $76.35 | 56 | 2 | 3.57% | $38.17 | `patio contractors near me` | PHRASE | Patios \| Near Me |

`residential landscape design company` is the one keyword that has ever produced a current-primary
conversion in August — the single `WC leads` form submission on 2026-08-04. It is also the single
largest spender, at 27.2% of month-to-date cost.

**No keyword pause is recommended on three days of post-change data.** These keywords are all
on-service, BOFU-intent, and carry the account's only conversion evidence.

---

## 9. Search-term and negative-keyword evidence

### Visible coverage — Google does not reveal every query

| Window | Distinct visible terms | Visible cost | True account cost | Coverage | Visible clicks | Visible impressions | Impression coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| MTD 01–23 | 326 | $602.64 | $1,414.98 | **42.6%** | 28 / 62 | 867 / 2,112 | 41.1% |
| A 17–23 | 135 | $92.45 | $369.43 | **25.0%** | 6 / 20 | 317 / 832 | 38.1% |
| E 21–23 | 51 | $78.41 | $186.36 | **42.1%** | 5 / 10 | 117 / 314 | 37.3% |
| G 24 *(partial)* | 24 | $36.67 | $100.74 | 36.4% | 2 / 5 | 51 / 140 | 36.4% |
| Aug 01–24 | 340 | $639.31 | $1,515.72 | 42.2% | 30 / 67 | 918 / 2,252 | 40.8% |

Roughly **three-fifths of spend is attached to queries Google withholds** for privacy reasons.
Visible search-term cost is never used as total account cost anywhere in this report.

### Evidence-based spend attribution of the visible corpus

Buckets keyed to the actual negative-plan families, not to a generic classifier.

| Bucket | MTD 01–23 | A 17–23 | E 21–23 | Aug 23–24 *(both negative sets fully effective)* |
|---|---:|---:|---:|---:|
| Relevant / on-service and other visible terms | $338.61 (56.2%) | $54.97 (59.5%) | $40.93 (52.2%) | $25.50 (40.6%) |
| Generic landscaping family — **protected, deliberately kept eligible** | $84.90 (14.1%) | $15.88 (17.2%) | $15.88 (20.3%) | $37.32 (59.4%) |
| Competitor (Phase-1 8 phrases) | $97.33 (16.2%) | $0.00 | $0.00 | **$0.00** |
| Competitor (34-phrase plan) | $36.39 (6.0%) | $21.60 (23.4%) | $21.60 (27.5%) | **$0.00** |
| Wrong market | $33.01 (5.5%) | $0.00 | $0.00 | **$0.00** |
| Wrong service | $12.40 (2.1%) | $0.00 | $0.00 | **$0.00** |
| Wrong material | $0.00 | $0.00 | $0.00 | **$0.00** |

The $21.60 attributed to the 34-phrase plan inside windows A and E is a single click on
`terra landscaping` on **2026-08-21** — one day *before* that negative took effect. It is
pre-effective spend, not leakage.

### Post-effective performance of the five named Phase-1 negatives

Effective 2026-08-19. Six full days of post-effective data.

| Negative | Pre (Aug 1–18) impr / clicks / cost | Post (Aug 19–24) impr / clicks / cost / conv |
|---|---|---|
| `agc turf` | 3 / 1 / $24.51 | **0 / 0 / $0.00 / 0.0** |
| `ulm austin` | 4 / 1 / $24.24 | **0 / 0 / $0.00 / 0.0** |
| `garden goat` | 2 / 1 / $19.42 | **0 / 0 / $0.00 / 0.0** |
| `agave landscaping` | 2 / 1 / $18.87 | **0 / 0 / $0.00 / 0.0** |
| `astoria lighting` | 10 / 1 / $10.29 | **0 / 0 / $0.00 / 0.0** |

**All five remain at zero. The negative controls continue to work.** Combined, these five terms
drew 5 clicks and $97.33 before the negatives; none has recurred since. That is a statement about
blocked *traffic*, not about leads — no lead was demonstrably saved, and none is claimed.

### Post-effective performance of the 34-phrase campaign-negative plan

Effective **2026-08-22 10:09:43** account time, so 2026-08-22 is a straddling partial day and
2026-08-23 is the first fully governed day.

- **0 of 34 phrases** show any visible matched traffic on 2026-08-23 or 2026-08-24.
- The last visible hits on any covered phrase were `cutters landscaping austin`,
  `ranchers landscaping`, `the mark landscapes`, `yardzen packages` and `terra landscaping` on
  **2026-08-21**, and `outdoor lighting perspectives` (3 impressions, no click, no cost) on
  **2026-08-22**, which straddles the 10:09 cutover.
- Across the whole month those 34 phrases attracted 46 visible terms, 178 impressions, 4 clicks and
  **$81.80** of visible spend — all of it pre-effective.

**Status of the plan: LIVE AND VERIFIED — not pending, not partial, not replaced.** 34 phrases ×
2 campaigns = 68 objects, all present as PHRASE on both campaigns, 0 missing.

### New irrelevant traffic since the 2026-08-18 audit

85 search terms appeared for the first time on or after 2026-08-19. Three classify as irrelevant,
and **all three drew impressions only — zero clicks, $0.00 cost.**

Two additional competitor-shaped named-business terms are **not** covered by any live negative and
did draw clicks:

| Term | Dates | Impr | Clicks | Cost |
|---|---|---:|---:|---:|
| `dennis jackson landscaping` | 2026-08-24 | 4 | 1 | $15.23 |
| `perfect cuts landscaping` | 2026-08-21 → 23 | 6 | 1 | $10.27 |

Combined **$25.50**. Recorded here as evidence for a future negative-keyword review. **No negative
was added, and none is proposed for execution in this task.**

### Protected families — confirmed still eligible

Checked directly against the 156 live campaign negatives and the 246 ad-group negatives:

| Family | Status |
|---|---|
| `landscaper near me`, `landscapers near me`, `landscape companies near me`, `landscaping services near me` | **eligible at campaign level** |
| Pro Green brand searches | eligible |
| Converted search families (`residential landscape design company`) | eligible |
| Paving contractor searches | eligible |
| Deck builder searches | eligible |
| Verified buyer-intent and first-party service terms | eligible |

The generic landscaping family drew 13 visible terms, $84.90 and 4 clicks across August with zero
conversions. It remains eligible by policy.

`near me` **is** a PHRASE negative — but only inside the twelve `| BOFU` ad groups, never at
campaign level. That is deliberate cross-negation that routes "near me" queries to the paired
`| Near Me` ad group. It does not block the family from the account.

### `cost`, `emergency` and `keystone` — effective-scope check

| Term | Where it lives now | Effective on the live campaigns? | Note |
|---|---|---|---|
| `cost` BROAD | `General List` `11813144900` and `General List - Irrigation Repair` `12178646912` | **No** — neither list is linked to either live campaign, and `cost` is **not** in the account-level list `11260450591` | The Phase-1 removal from the account-level list has held. **No current buyer-intent conflict.** Internal follow-up only: two unlinked lists still carry it and would block cost queries if ever linked. |
| `emergency` PHRASE | 6 memberships, one of them in `General` `10670796064` | **Yes** | Retained on explicit prior instruction. Flagged as an internal follow-up because agency policy bars auto-negativing `emergency`. |
| `keystone` PHRASE | `Names` `10673711933` | **Yes** | Internal follow-up: Keystone is a common retaining-wall block brand, so this may block genuine retaining-wall buyer intent. |

**Nothing was removed. These are read-only observations for a future review.**

---

## 10. Budget pacing

```
August calendar length              = 31 days
Monthly limit                       = $2,000.00
Completed days measured             = Aug 1-23 (23 days)
Partial current day                 = Aug 24, reported separately
Remaining full days after Aug 24    = Aug 25-31 = 7 days
```

| Step | Formula | Result |
|---|---|---:|
| 1. August spend through Aug 23 | Σ daily cost, Aug 1–23 | **$1,414.98** |
| 2. Aug 24 partial spend | daily cost, Aug 24 | **$100.74** |
| 3. Total spend as of the query | step 1 + step 2 | **$1,515.72** |
| 4. % of monthly limit used | $1,515.72 / $2,000.00 | **75.79%** |
| 5. Remaining monthly budget | $2,000.00 − $1,515.72 | **$484.28** |
| 6. Average completed-day spend | $1,414.98 / 23 | **$61.52** |
| 7. Average post-change completed-day spend | $186.36 / 3 | **$62.12** |
| 8. Required daily pace for the remaining days | $484.28 / 7 | **$69.18** |
| 9. Projection A — MTD completed-day pace | $1,515.72 + ($61.52 × 7) | **$1,946.36** |
| 10. Projection B — post-change completed-day pace | $1,515.72 + ($62.12 × 7) | **$1,950.56** |
| 11a. Expected variance, method A | $2,000.00 − $1,946.36 | **$53.64 under** |
| 11b. Expected variance, method B | $2,000.00 − $1,950.56 | **$49.44 under** |

Both projections land **under** the limit, within 2.5% to 2.7% of it. The approved combined daily
budget of $65.78 implies a 31-day maximum of $2,039.18, slightly above the cap — but observed
delivery has averaged below the budget, so the cap holds in practice.

**Caveat on the projection.** Aug 24 is still open at $100.74, already above the $65.78 combined
daily budget. Google permits daily overdelivery up to twice the daily budget provided the monthly
average holds, so a day like this is within normal delivery behaviour and is not evidence of a
budget fault. If several such days recur in the final week, actual month-end spend will land nearer
the cap than either projection shows.

### Per-campaign budget utilization, August 21–23

| Campaign | Daily budget | 3-day spend | Average per day | Utilization |
|---|---:|---:|---:|---:|
| Hardscape Construction | $26.31 | $52.25 | $17.42 | 66.2% |
| Outdoor Living & Design | $39.47 | $134.11 | $44.70 | **113.3%** |

Outdoor Living & Design is running slightly over its daily budget on a three-day average, which is
normal overdelivery, while Hardscape Construction is under-spending its allocation. Neither
campaign lost any impression share to budget in the post-change window.

**No budget change is recommended and none was made.** If the client wishes to hold well clear of
the cap, the read-only observation is that the account is on track without intervention.

---

## 11. Old versus current live setup

| Item | Old state (pre-2026-08-19) | Current live state | What changed | Why | Verified result |
|---|---|---|---|---|---|
| Campaign budgets | $32.89 + $32.89 | **$26.31 + $39.47** | reallocated toward the higher-volume campaign | Outdoor Living & Design carried the demand and the only conversion | Lost IS to budget fell 30.28% → **0.00%** |
| Combined daily budget | $65.78 | **$65.78** | unchanged | hold the $2,000 monthly cap | 30.4-day projection $1,999.71; live pacing $1,946–$1,951 |
| Maximum CPC | none (uncapped) | **$22.00 both campaigns** | ceiling added under TARGET_SPEND | uncapped bidding was buying $30–$40 clicks | Avg CPC $22.45 → **$18.47** week over week |
| Ad schedule (account time) | 08:00–17:00, 7 days | **09:00–18:00, 7 days** | shifted one hour later | correct the account/market timezone offset | 14 criteria confirmed live, no bid modifiers |
| Ad schedule (Austin time) | 07:00–16:00 | **08:00–17:00** | adds the 4–5pm Austin hour, drops 7am | align delivery to answering hours | confirmed live |
| Primary conversion actions | 9 counted | **3 counted** | 6 demoted to secondary | one action per real lead event, no double counting | column verified at exactly 3; historical figures restated by Google to match |
| Campaign negative count | 72 | **156** | +16 on 2026-08-19, +68 on 2026-08-22 | block confirmed competitor, wrong-market, wrong-service and wrong-material traffic | all 34 + all 8 phrases live on both campaigns; zero post-effective traffic |
| Shared-negative removals | 8,723 criteria | **8,716 criteria** | 7 blocking negatives removed | `cost`, `hire`, `shade`, `oasis`, `keystone`, `black`, `replacement` were blocking buyer intent | removal has held; `cost` is no longer effective on the live campaigns |
| Enabled RSAs | 24 | **48** | 24 outcome-led ads created paused, then enabled | test a new message against BELOW_AVERAGE expected CTR | 48 ENABLED, 48 APPROVED, 0 disapproved |
| Ads per ad group | 1 | **2** | one original + one new in every ad group | fair head-to-head test | exactly 2 in all 24 ad groups |
| Positive keywords | 48 | **48** | unchanged | BOFU set was already correct | 24 PHRASE + 24 EXACT, all ENABLED |
| Location count | 24 per campaign | **24 per campaign** | unchanged | approved service area | 48 criteria, 0 exclusions |
| Location targeting mode | PRESENCE | **PRESENCE** | unchanged | correct for a local service business | confirmed on both campaigns |
| Sitelinks | 12 | **12** | unchanged | — | 6 per campaign |
| Callouts | 16 | **16** | unchanged | — | 8 per campaign |
| Structured snippets | 2 | **2** | unchanged | — | 1 per campaign |
| Call assets | 2 | **2** | unchanged | — | 1 per campaign |
| Business logos | 2 | **2** | unchanged | — | 1 per campaign |
| Landing-page mapping | 13 destinations | **13 destinations** | unchanged | one offer page per theme pair | 12 offer-page hosts + 1 approved main-site exception |
| Parent-asset exclusions | `[]` | **`[SITELINK, STRUCTURED_SNIPPET]`** | added on both campaigns | stop Dallas/Houston sitelinks and the unverified "Over 20 Years Of Experience" snippet from serving in Austin | confirmed live on both campaigns |

**Prepared but never executed, and therefore not described as live work:** the ad-group negative
plan of 2026-08-21, `BLK-001` (ClickCease `ccpturl`), `BLK-002` (sitelink repointing), and
`SPEC-001`, `SPEC-002`, `SPEC-005`.

**One out-of-scope observation.** `customer.tracking_url_template` now carries
`ccpturl=offeraustin.progreenlandscapesolutions.com`, which is the correct landing-page host — the
2026-08-18 audit found `offer.sehydroseed.com`, a different business. Green Marketing did **not**
write this field; `BLK-001` remains unexecuted and unapproved. Per this task's rules, ClickCease
tracking-template activity is not counted as an optimization event. The value has oscillated before,
so it is recorded, not relied upon.

---

## 12. Analytical rules applied

- All figures come from fresh API reads in this session. No screenshots, no stale reports.
- Account totals reconcile to campaign totals and to daily totals with **zero** discrepancy.
- Impression-share metrics are queried per window, never summed across days.
- Facts, directional indications and recommendations are separated.
- No causal claim is made from correlation. The CPC and impression-share movements are consistent
  with the budget and CPC-ceiling changes, and are described as consistent, not proven.
- No claim is made that leads were saved or prevented.
- CTR, conversion rate and CPL are computed before and after, and reported even where the answer is
  unfavourable or undefined.
- Ad Strength and Optimization Score are not treated as business results.
- All conversions are never used as qualified leads.
- Partial-day data (Aug 24) is never combined with completed-day comparisons.
- Sample sizes are shown wherever a comparison is made.
- Reduced reported conversions after the cleanup are not described as lost real leads.
- Visible search-term cost is never used as total account cost.
- No credentials, tokens, GCLIDs, lead information or PII appear in any artifact.

## 13. Artifacts produced by this run

| File | Contents |
|---|---|
| `32_daily_performance_aug01_24.csv` | 24 rows — one per August day, with period labels and the partial-day flag |
| `33_campaign_comparison.csv` | 88 rows — account and per-campaign metrics for all eight windows |
| `34_rsa_original_vs_new.csv` | 58 rows — cohort totals plus ad-group-level detail with sufficiency verdicts |
| `35_keyword_and_quality_score.csv` | 48 rows — all positive keywords with current and prior Quality Score components |
| `36_post_change_search_term_verdicts.csv` | 340 rows — every visible term, negative coverage, and post-effective traffic |
| `37_current_state_inventory.json` | complete live structural inventory as read in this session |
| `38_evidence_and_calculation_appendix.md` | this file |
| `39_weekly_report_2026-08-17_to_08-23.md` | the client-ready weekly report |

No existing artifact, frozen plan, execution receipt, snapshot or previous report was modified.

**READ-ONLY REPORT COMPLETE — NO EXTERNAL CHANGES MADE**
