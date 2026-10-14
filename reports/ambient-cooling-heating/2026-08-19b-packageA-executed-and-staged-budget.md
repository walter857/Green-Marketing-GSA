# Ambient Cooling — Package A EXECUTED · Staged August Budget Rebuilt

**Child account:** `Ambient Cooling - Live` · **ID** `240-195-9466` (`2401959466`)
**Manager:** `Green Marketing` `3373711342` · ClickCease Client Center `2815082755` (ACTIVE, protected)
**Timezone:** America/New_York · **Currency:** USD
**Account local time:** 2026-08-19 22:28 −04:00

---

## 0. Shell process — confirmed finished

The one background task from the previous run (a read-only GAQL query started 21:44) had
completed: output file static at 9,007 bytes, **0 CPU over a 4-second sample**, and `taskkill`
reported *"no running instance of the task"* — a defunct entry, not a live process. Its parent
shell was stopped.

Two unrelated python processes are alive on this machine. Both belong to a **different project**
(`carbon-ppc`) and target customers `2646876213`, `9720978817` and `7239732058`. **No live
process anywhere references `2401959466`.** No concurrency hazard.

---

## 1. Preflight — 32/32 gates passed

Plan fingerprint reproduced from file (`44D14DA4714BB6E8`); identity, both manager links, all
five campaign names, ENABLED/SERVING, TARGET_SPEND, budgets, 139 account-wide schedule criteria,
all 30 planned removals present with **zero drift in any before-state**, call asset exclusive to
the five with 0 schedule rows, all 12 tracked RSAs correct, and `validate_only=true` on the exact
31 operations: `VALIDATE_OK`.

## 2. Package A — EXECUTED

`GoogleAdsService.Mutate` · **31 operations** · `partial_failure=false` · `validate_only=false`
· 31 responses returned · receipt `receipts/packageA-mutation-2026-08-19.json`

Op 1 set the call-asset schedule; ops 2–31 removed the campaign schedules — asset first, so there
was no instant where the campaign ran 24/7 with an unrestricted phone number.

### Readback QA — 31/31 pass

| Verified | Result |
|---|---|
| `AD_SCHEDULE` criteria on the five | **0** → campaigns deliver 24/7 ✅ |
| Legacy criteria untouched | exactly **109** across **19** campaigns ✅ |
| Criterion mix per campaign | LANGUAGE 1 · DEVICE 3 · LOCATION 75 · AD_SCHEDULE 0 ✅ |
| Call asset schedule | **6 rows**, Mon–Fri 08:00–20:00, Sat 08:00–13:00 ✅ |
| Sunday | **absent** ✅ |
| All minutes | `ZERO` ✅ |
| Phone / country / conversion action | `(410)705-6354` / US / `conversionActions/179` — unchanged ✅ |
| Asset links | exactly the five, all ENABLED, no sixth campaign ✅ |
| Legacy call assets | 343054924787:0, 80497290055:0, 98498198415:7, 369249814267:7 — unchanged ✅ |
| Budgets | unchanged — Package B was **not** applied ✅ |
| RSAs | 6 replacements ENABLED+APPROVED, 6 originals PAUSED+DISAPPROVED ✅ |
| Counts | campaigns 23, ad groups 68, ads 113, campaign_assets 271, conversion actions 16, keywords 6,968 — all unchanged ✅ |
| `campaign_criterion` total | 13,810 → **13,780** (−30 exactly) ✅ |
| Manager links | both ACTIVE ✅ |

**One thing to watch.** Editing the asset resubmitted it for review: `review_status =
REVIEW_IN_PROGRESS`, `campaign_asset.primary_status = PENDING` with reason `ASSET_UNDER_REVIEW`,
**zero policy topics**. That is Google's standard post-edit re-review, not a disapproval — the
same pattern the replacement RSAs went through on 08-18 before returning APPROVED within hours.
**The call extension will not show in ads until review clears.** Campaign delivery is unaffected.
Worth a recheck tomorrow.

> Two of my readback assertions initially failed. Both were my error, not the account's: the
> first pair was written against the pre-edit steady state and did not allow for re-review; then
> I asserted on `review_status` and `policy_topic_entries` without selecting them, so they
> defaulted to empty and passed vacuously. Both are corrected above and the receipt reflects the
> real queried values.

---

## 3. Diagnosis before any budget decision

### Search volume — the finding that drives everything

`KeywordPlanIdeaService.GenerateKeywordHistoricalMetrics`, read-only, Google Search, English,
scoped to the 10 core service-area cities (the planner rejects postal-code and neighbourhood
targets, so 42 + 5 of the 75 are excluded).

| Keyword | Avg monthly searches | Competition | Top-of-page bid range |
|---|---:|---|---|
| **`ac repair near me`** | **260** | HIGH (74) | $19.94 – $94.04 |
| **`hvac repair near me`** | **70** | HIGH (79) | $23.32 – $107.10 |
| **`hvac installers`** | **10** | LOW (7) | — |
| **`hvac replacement near me`** | **10** | HIGH (100) | — |
| **`gas boiler repair`** | **10** | LOW (0) | — |
| *`ac repair` (comparator)* | 390 | LOW (18) | $16.29 – $92.40 |
| *`furnace repair` (comparator)* | 170 | LOW (6) | — |
| *`hvac repair` (comparator)* | 140 | LOW (24) | $31.36 – $95.07 |
| *`boiler repair` (comparator)* | 30 | LOW (15) | — |

### Quality Score components

| Campaign | QS | Expected CTR | Ad relevance | Landing page | Actual CTR |
|---|---:|---|---|---|---:|
| AC Repair | **4** | BELOW_AVERAGE | AVERAGE | AVERAGE | 5.79% |
| HVAC Repair | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** | 0.99% |
| HVAC Installation | n/a | — | — | — | 3.70% |
| HVAC Replacement | n/a | — | — | — | 0% |
| Gas Boiler Repair | n/a | — | — | — | — |

### Impression share — where the constraint actually is

| Campaign | IS (MTD / 08-19) | **Lost to budget** | Lost to rank | Budget used 08-19 |
|---|---|---:|---:|---:|
| **HVAC Installation** | 52.03% / 46.99% | **32.47% / 53.01%** | 15.50% / 0.00% | **197.4%** |
| AC Repair | 21.84% / 36.96% | 0.00% / 0.00% | 78.16% / 63.04% | 199.4% |
| HVAC Repair | 23.04% / 24.39% | 0.00% / 0.00% | 76.96% / 75.61% | 68.7% |
| HVAC Replacement | 13.04% / 13.64% | 0.00% / 0.00% | 86.96% / 86.36% | 0% |
| Gas Boiler Repair | **0.00%** | 0.00% | 0.00% | 0% |

### Other diagnostics

- **Keyword eligibility:** all 12 non-removed keywords are ENABLED, `system_serving_status`
  ELIGIBLE, `approval_status` APPROVED. Nothing is blocked.
- **Negative conflicts: NONE.** Zero campaign negatives, zero ad-group negatives, no list
  attached to the five. The account-level set `11252984411` — 59 BROAD members, applies
  account-wide, reports `member_count 0` and is invisible in `campaign_shared_set` — was tested
  separately against all five keywords: **zero blocks**.
- **Search terms:** 191 rows classified on disk against a positive HVAC whitelist; only counts
  and cost shares were read back. Out-of-scope terms took **0 clicks and $0.00** across all five.
  There is no waste to negate.
- **Post-RSA delivery** (from 08-18 15:17): HVAC Installation $275.58 then $272.75; Gas Boiler
  and HVAC Replacement still $0.00.

### Why Gas Boiler Repair has 0.00% impression share

Eliminated in turn: keyword eligibility (ELIGIBLE/APPROVED), negatives (zero blocks), policy
(both RSAs APPROVED, ad strength EXCELLENT), the ad-disapproval window (still zero in the clean
window), budget (0% budget-lost, never spent a cent), and ad schedule (Package A removed it).

**Confirmed cause: search volume.** `gas boiler repair` averages **10 searches/month** — Google's
minimum reported bucket, so true volume is ≤10. The broader head term `boiler repair` is only 30.
With Presence-only targeting across 75 tight local targets, English only, and Phrase/Exact on a
boiler-specific phrase, well under one query per day is expected — zero impressions in 19 days is
the **statistically ordinary outcome**. `search_term_view` returned **zero rows**: not weak terms,
no terms at all. Impression share is zero because the *denominator* is zero. **No budget change
can move a metric whose denominator is zero.**

---

# Package B-v2 — Staged August budget

### `PLAN FINGERPRINT: 93A1EA55973F7A94`

`clients/ambient-cooling-heating/plans/august-budget-staged-package-2026-08-19-v2.json`
Supersedes and does **not** reuse the rejected `EF9FBA55926545F2`.

**Principle: increase a budget only where lost impression share from budget proves budget is the
binding constraint. Never increase a budget to reach a spend target.**

## Stage 1 — immediate (1 mutation)

| Campaign | Current | Proposed | Change |
|---|---:|---:|---|
| **HVAC Installation** `24132507747` | $138.16 | **$276.32** | **+$138.16 (+100%)** |
| AC Repair | $141.45 | $141.45 | unchanged — Ad Rank limited |
| HVAC Repair | $78.95 | $78.95 | unchanged — quality limited (QS 2) |
| HVAC Replacement | $26.32 | $26.32 | unchanged — demand limited |
| Gas Boiler Repair | $42.76 | $42.76 | unchanged — zero eligible auctions |
| **Total daily** | **$427.64** | **$565.80** | +$138.16 |

**Sizing is observed, not projected.** 2.0× is exactly what the campaign already consumes: it
spent **199.5%** and **197.4%** of its budget on the two clean post-RSA days by using Google's 2×
overdelivery allowance. This converts proven overdelivery into a planned budget.

**Why not straight to the full amount:** closing the 53.01% budget-lost IS implies ~$580/day of
available demand ($272.75 ÷ 0.4699). That is a 4.2× step on a campaign still in
`BIDDING_STRATEGY_LEARNING`; large single-step changes extend learning and spike CPC. The stages
reach it by 08-22 **only if** the evidence supports it.

## Checkpoints

**24-hour (08-21 09:00 ET, measuring 08-20).** Advance to Stage 2 only if **all**: budget-lost IS
≥ 20%; avg CPC ≤ **$52.73** (baseline $42.18 +25%); clicks ≥ 13; cumulative spend within guardrail.
Hold if budget-lost IS is 5–20% or CPC is $52.73–$63.27. **Roll back to $138.16** if CPC > $63.27
without more clicks, single-day spend > $552.64, or guardrail breached by >20%.

**48-hour (08-22 09:00 ET, measuring 08-21).** Advance to Stage 3 only if budget-lost IS still
≥ 20%, CPC still ≤ $52.73, and CPC has not risen >25% for two consecutive days.

**Stage 2** → $414.48 (3.0×) · **Stage 3** → $552.64 (4.0×).
Both are pre-computed and gated, and **each requires its own separate approval and fingerprint.**
This package authorizes **Stage 1 only**.

## Projection

| | |
|---|---|
| August MTD (five) | $1,033.23 |
| Remaining vs cap | $11,966.77 |
| Days a new budget applies | 12 (08-20 → 08-31) |
| **Stage 1 budget-bounded** | **$7,822.83** |
| **Demand-bounded central** | **≈ $7,033** (range $5,593 – $7,823) |
| Expected shortfall vs $13,000 | $5,177 – $7,407 |

Central daily build: HVAC Installation $300 + AC Repair $140 + HVAC Repair $45 + HVAC Replacement
$3 + Gas Boiler $0 = $488, plus ~15% from the Package A 24/7 uplift → **≈$561/day**, just under
the $565.80 total budget — the expected shape when budget matches demand instead of chasing a
target.

> **This plan will not spend $13,000, and it should not.** Four of five campaigns are limited by
> demand, Ad Rank, quality or eligibility. Closing the gap would need more eligible auction
> volume — more keyword themes, more services, wider geography, or a real Quality Score
> improvement — all explicitly out of scope.

## Daily guardrail

`allowed(D) = 1033.23 + (stage_total_daily × days_since_08-19) × 1.20`

| Date | Allowed cumulative |
|---|---:|
| 08-20 | $1,712.19 |
| 08-21 | $2,391.15 |
| 08-24 | $4,428.03 |
| 08-27 | $6,464.91 |
| 08-31 | $9,180.75 |

Breach → propose a reduction and advance no stage. **Absolute stop at $12,400.**

**Maximum daily overdelivery at Stage 1: $1,131.60/day** (2× total), arithmetic ceiling
$14,612.43 for August — *above* the cap. Google's monthly charging limit is per campaign and is
recalculated on mid-month changes, so **Google does not enforce a $13,000 account cap**. The daily
guardrail is what enforces it, and it must actually be run.

## CPC ceiling — NOT PROPOSED

| Available | Missing |
|---|---|
| Search conv rate, trailing 365d pre-launch: **5.47%** | Target CPL — **not supplied** |
| Search CPA, trailing 365d: **$915.96** | Target CPQL / CAC — **not supplied** |
| Search avg CPC, trailing 365d: **$50.14** | Job value, margin, close rate — **not supplied** |
| Search all-time: 3.25% CR, $544.74 CPA, $17.73 CPC | Qualified-lead data — **not available** (both WhatConverts upload actions: 0 conversions all-time) |
| New campaigns: 0 conversions on 24 clicks | |

Max CPC = target CPL × conversion rate. A conversion rate exists; **no target CPL exists
anywhere in the client record**, so deriving a ceiling would mean inventing it. Not done.

**Correction to my earlier analysis.** In the rejected package I called the $43.05 CPC evidence of
bid inflation. That was wrong: this account's own Search channel averaged **$50.14/click over the
trailing year**, and the planner puts top-of-page bids at $19.94–$94.04 and $23.32–$107.10 for our
two main terms. **$43.05 is below the account's own recent Search norm.** High CPC here is the
market, not a bidding error — and a ceiling set below the market range would simply stop delivery
on the one campaign that works.

One input unlocks it — a target CPL or acceptable CPA:

| Target CPL | Implied max CPC @ 5.47% |
|---:|---:|
| $300 | $16.41 |
| $500 | $27.35 |
| $750 | $41.03 |
| $916 (matches trailing CPA) | $50.10 |

A ceiling matching today's CPA sits *above* the current CPC and would barely bind; one that
restrains spend needs a target CPL below ~$790.

---

## Findings flagged, not actioned

1. Ad group `202339087874` "SKAG | HVAC Replacement Near Me" sits **inside the AC Repair
   campaign**, is REMOVED, yet still holds 2 non-removed keywords and 2 ENABLED
   `AREA_OF_INTEREST_ONLY` ads with a CONSUMER_FINANCE topic. Nothing serves. Cosmetic, but it is
   why AC Repair appears to carry HVAC Replacement keywords.
2. `HAS_ADS_DISAPPROVED` on three campaigns counts only the six PAUSED originals. Clearing it
   needs a destructive removal with its own approval.
3. **Zero primary conversions account-wide in August**, and both WhatConverts upload actions have
   0 all-time. This is the single most valuable fix available and the input that unlocks the CPC
   ceiling.

## Receipts

| File | Contents |
|---|---|
| `snapshots/preflight-packageA-2026-08-19.json` | 32 preflight gates |
| `receipts/packageA-mutation-2026-08-19.json` | 31-op mutation, returned resource names, pre-write counts |
| `receipts/packageA-readback-2026-08-19.json` | 31 readback checks |
| `snapshots/diagnosis-2026-08-19.json` | Quality, eligibility, negatives, search-term aggregates, CPC |
| `snapshots/keyword-volume-2026-08-19.json` | Historical search volume |
| `snapshots/validate-only-stage1-2026-08-19.json` | Stage 1 validate-only |
| `plans/august-budget-staged-package-2026-08-19-v2.json` | Package B-v2 · `93A1EA55973F7A94` |

## Required next input

```
APPROVE PACKAGE B-v2 STAGE 1 93A1EA55973F7A94 FOR 2401959466
```

Stage 1 is one budget update: HVAC Installation $138.16 → $276.32/day. Stages 2 and 3 are defined
and gated but each need their own approval. `EF9FBA55926545F2` is retired and must not be reused.
