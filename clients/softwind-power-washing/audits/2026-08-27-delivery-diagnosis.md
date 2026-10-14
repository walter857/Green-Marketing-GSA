# August Delivery Diagnosis — Softwind Power Washing

**Account:** Softwind Power Washing - Live · `1521725229` · Power Washing
**Snapshot (account-local):** 2026-08-27 10:11:14 EDT
**Mode:** READ. Zero Google Ads mutations issued. Verified by 28/28 red-team checks.

---

## 0. Date correction — the checkpoint header is one day ahead

The instruction is dated **August 28, 2026 09:52 America/New_York**. The actual
account-local date is **August 27, 2026**. Four independent sources agree:

| Source | Value |
|---|---|
| Host clock, America/New_York | `2026-08-27T10:09:32-04:00` |
| Host clock, UTC | `2026-08-27T14:09:35+00:00` (consistent, EDT = UTC−4) |
| Google Ads API `segments.date DURING YESTERDAY` | returns **2026-08-26** |
| Newest `change_event` in the account | `2026-08-26 18:00:31` (the PLAN-I1C budget write) |

Everything else in the header is correct: MTD was ≈$253 (exactly **$253.39**) and
remaining ≈$2,247 (exactly **$2,246.61**). Only the date line is wrong.

This matters because it changes the denominators. All math below uses 2026-08-27.

| | Header assumed (Aug 28) | Actual (Aug 27) |
|---|---|---|
| Remaining calendar days D | 4 | **5** |
| Remaining hours H | ~86 | **109.81** |
| Remaining **serving** days | 3 | **4** |
| Remaining **scheduled serving hours** | ~28 | **37.81** |

---

## 1. Identity gate — PASSED

| Field | Observed | Expected | |
|---|---|---|---|
| Account name | Softwind Power Washing - Live | exact match | ✓ |
| Customer ID | 1521725229 | exact match | ✓ |
| Manager | false | false | ✓ |
| Test account | false | false | ✓ |
| Currency | USD | USD | ✓ |
| Time zone | America/New_York | America/New_York | ✓ |
| Status | ENABLED | — | ✓ |

---

## 2. Deployed rescue state — NO DRIFT

Every expected prior readback value is confirmed live.

| Item | Expected | Observed | |
|---|---|---|---|
| Campaign A budget | $333.33/day | $333.33/day | ✓ |
| Campaign B budget | $41.11/day | $41.11/day | ✓ |
| Combined | $374.44/day | $374.44/day | ✓ |
| Bidding | Maximize Clicks / TARGET_SPEND | TARGET_SPEND both | ✓ |
| CPC ceiling | none | **unset both** | ✓ |
| Positive locations | 80 per campaign | 80 / 80, all ENABLED | ✓ |
| Negative locations | 1 CT exclusion each | `21139` ENABLED both | ✓ |
| Location option | Presence | PRESENCE both | ✓ |
| Search Partners | off | false both | ✓ |
| Display | off | false both | ✓ |
| Ad schedule | Mon–Sat 08:00–18:00 | 6 dayparts each, Sunday absent | ✓ |
| Budget sharing | — | `reference_count`=1, `explicitly_shared`=false both | ✓ |

Zero `change_event` rows after `2026-08-26 18:00:32`. Nothing has drifted.

---

## 3. Account-level spending limit — NONE DETECTABLE

| Signal | Reading |
|---|---|
| `account_budget.approved_spending_limit_type` | **INFINITE** |
| `account_budget.adjusted_spending_limit_type` | **INFINITE** |
| `account_budget.proposed_spending_limit_type` | **INFINITE** |
| `account_budget.amount_served` | $253.39 against no cap |
| `billing_setup` (2 rows) | both **APPROVED**; live one runs FOREVER, no end date |
| `customer.status` | ENABLED |
| Payment failure / verification signal | none in any readable field |
| Campaign `primary_status` | **ELIGIBLE**, `primary_status_reasons` **empty**, both |

**API limitation, stated honestly:** the Google Ads API exposes **no customer-level
daily spending limit field at all** — a `GoogleAdsFieldService` scan of
`customer.%limit%` returns zero rows. The new-account daily spending limit that
appears in the UI notification bar is not readable through the API, so I cannot
positively exclude one by API alone.

The evidence argues strongly against one binding: **Search Lost IS (budget) is
0.00% on both campaigns** for 2026-08-20..26, and the account billed $121.22 in a
single day on 2026-08-25. A binding account cap would show as lost impressions.
It does not.

**Verdict: account-level spending limit is NOT the constraint.**
No billing or payment change was made or is proposed.

---

## 4. Did the campaigns spend after August 26? — NOT YET, AND THAT IS EXPECTED

| Date | Spend | Impr | Clicks |
|---|---|---|---|
| 2026-08-24 | $22.11 | 26 | 1 |
| 2026-08-25 | $121.22 | 21 | 3 |
| 2026-08-26 | $82.22 | 30 | 1 |
| **2026-08-27 (today, to 10:11)** | **$0.00** | **0** | **0** |

The geo expansion landed at **17:49** on 2026-08-26 and the budget rise at
**18:00** — both *after* that day's 18:00 serving cutoff. **Today is the first
serving day either change has ever been live for.** It is 2 hours into a 10-hour
window.

Zero-by-10:11 is **not** evidence of a blocker:

- Only **15.5%** of this account's historical impressions land before 10:00.
- Volume is extremely lumpy: 2026-08-22 produced 2 impressions all day, 08-18
  produced 3, 08-17 produced 4.
- Clicks cluster in the afternoon — the billable clicks landed at 16:00, 17:00,
  12:00, 14:00.
- Same-day reporting lags by up to ~3 hours.

**Classification: INCONCLUSIVE, leaning normal variance.** Re-check at 13:00 ET.

Also worth noting: of 162 location rows, only **11 have ever delivered**, and all
11 are among the *original 8* targets. **None of the 72 net-new geo targets has
had a single serving hour yet.**

---

## 5. Serving blockers — ALL CLEAR

| Check | Result |
|---|---|
| Campaign status / serving status | ENABLED / SERVING, both |
| Campaign primary status | **ELIGIBLE**, reasons **empty**, both |
| Bid strategy status | A: ENABLED · B: **LIMITED_BY_INVENTORY** |
| Campaign start / end dates | started 08-04 / 08-18, **no end date** |
| Ad groups | 6 enabled per campaign (12 of 30) |
| Keywords | **214 / 214** `ELIGIBLE` + `APPROVED` |
| Low Search Volume | **0** `RARELY_SERVED` |
| RSAs | **44 / 44** `APPROVED` + `REVIEWED` |
| Final URLs | 8 distinct, all on `offer.softwindli.com` |
| Location criteria | 160 positive + 2 negative, **all ENABLED** |
| Ad schedule | 12 dayparts, Mon–Sat 08:00–18:00 |
| Negative-keyword conflicts | **0** across 94 negatives × 214 keywords |
| Shared negative lists | **0** attached |
| Conversion goals | 3 biddable per campaign |
| Billing / account restriction | none detectable |

There is **no eligibility, policy, keyword, ad, negative, schedule-config or
conversion-goal blocker.** The account is technically healthy.

### Primary constraint classification

**DEMAND LIMITED · RANK LIMITED · SCHEDULE LIMITED**

| Evidence | Value |
|---|---|
| Search impression share, 08-20..26 | **81.03%** (A) / **85.71%** (B) |
| Search Lost IS — **budget** | **0.00%** / **0.00%** |
| Search Lost IS — **rank** | 18.97% / 14.29% |
| Campaign B bid strategy | **LIMITED_BY_INVENTORY** (Google's own term) |
| Servable share of remaining clock hours | **37.81 / 109.81 = 34%** |

The account already wins roughly four of every five available impressions. All
residual loss is to **rank**, none to budget. Sunday 2026-08-30 has no daypart,
so only **4 serving days** remain, not 5.

Learning is **not** offered as an explanation. Both campaigns show
`bidding_strategy_system_status` of ENABLED or LIMITED_BY_INVENTORY — neither is
a learning state, and neither campaign has zero delivery to explain.

---

## 6. THE URGENT FINDING — cost per click is unbounded and escalating

Every billable click in the account's life, in order:

| Date | Campaign | Keyword | Match | Cost |
|---|---|---|---|---|
| 08-17 | Power Washing | power washing west islip | EXACT | $5.71 |
| 08-19 | Power Washing | power washing services near me | EXACT | $22.13 |
| 08-24 | Power Washing #2 | house pressure washing estimate | EXACT | $22.11 |
| 08-25 | Power Washing | power washing near me | PHRASE | $26.66 |
| 08-25 | Power Washing #2 | house pressure washing estimate | EXACT | $40.07 |
| 08-25 | Power Washing | power washing near me | EXACT | $54.49 |
| 08-26 | Power Washing | power washing near me | PHRASE | **$82.22** |

**7 clicks · $253.39 · average CPC $36.20.**

The documented local top-of-page **high** for the twelve keyword texts this
account actually runs is **$28.23**. The last three clicks were bought at 1.4×,
1.9× and **2.91×** that.

The **$82.22 click was the entire day's spend on 2026-08-26** — and it is exactly
2× the then-$41.11 budget. That is not a coincidence:

> **The 2× daily overdelivery cap on a $41.11 budget was the only thing bounding
> the per-click price.** PLAN-I1C raised Campaign A to $333.33 at 18:00:30 that
> same evening. That lifted the effective per-click brake from **$82.22 to
> $666.66** — and left `target_spend.cpc_bid_ceiling_micros` **unset**.

The account's own emergency stop condition, set on 2026-08-26, is **breached**:

- $82.22 ≥ $60.00 single-click **STOP**
- $54.49 and $40.07 ≥ $40.00 single-click **INVESTIGATE**
- trailing-3-click average $49.65 ≥ $45.00 rolling **STOP**

**The search terms themselves are fine.** `power washing near me`,
`power wash near me` and `powerwashing companies near me` are core BOFU intents
inside the approved service. Zero negative candidates were found across 36 search
terms. This is a good search bought at a bad price — not junk traffic.

---

## 7. Remaining-month math

```
TARGET                                   $2,500.00
S   fresh exact August MTD spend           $253.39   (A $191.21 · B $62.18)
R   remaining                            $2,246.61
D   remaining calendar days (incl. today)         5
H   remaining hours to Sept 1 00:00 ET       109.81
```

| Quantity | Value |
|---|---|
| Required average per remaining calendar day | **$449.32** |
| Required rolling 24-hour pace | **$491.02** |
| Remaining **scheduled serving hours** | **37.81** |
| Required spend **per scheduled serving hour** | **$59.42** |
| Observed run rate | $75.18 per serving day ≈ **$7.52/serving hour** |
| **Gap** | **7.9×** |

Remaining serving windows (Sunday 08-30 excluded — no daypart):

| Date | Day | Window | Hours |
|---|---|---|---|
| 2026-08-27 | Thursday | 10:11–18:00 | 7.81 |
| 2026-08-28 | Friday | 08:00–18:00 | 10.00 |
| 2026-08-29 | Saturday | 08:00–18:00 | 10.00 |
| 2026-08-31 | Monday | 08:00–18:00 | 10.00 |
| | | **Total** | **37.81** |

| Capacity | Value |
|---|---|
| Current combined daily budget | $374.44 |
| Current combined 2× delivery ceiling | $748.88/day |
| Remaining-month billing capacity @ 1× (4 serving days) | $1,497.76 |
| Remaining-month billing capacity @ 2× | $2,995.52 |
| **Projected August at observed run rate** | **$554.11** |

### The three required answers

**CAN THE CURRENT BUDGETS SUPPORT THE REQUIRED PACE?**
**NO at standard delivery** ($1,497.76 < $2,246.61). YES only if all four
remaining serving days bill at the full 2× ceiling — which has never happened on
consecutive days.

**CAN THE CURRENT DAILY SPENDING LIMIT SUPPORT THE REQUIRED PACE?**
**YES.** No account-level limit exists; the 2× combined ceiling of $748.88/day
comfortably exceeds the required $491.02.

**CAN CURRENT QUALIFIED DEMAND SUPPORT THE REQUIRED PACE?**
**NO.** Spending $2,246.61 at the current $36.20 CPC needs **62 more clicks in 4
serving days — 15.5/day against an observed 0.7/day**. At the observed 5.26% CTR
that needs ~295 impressions/serving day against an observed 13. The account
already holds 81–86% impression share, so the headroom simply is not there.

---

## 8. Budget decision rule — BUDGET IS NOT THE ACTIVE DELIVERY CONSTRAINT

| # | Criterion | Verdict |
|---|---|---|
| 1 | Remaining-month billing capacity below $2,500 | **TRUE only at 1× delivery** ($1,497.76). At 2× it is $2,995.52. Pure arithmetic. |
| 2 | Combined daily spending limit below required pace | **FALSE** — $748.88 > $491.02 |
| 3 | Either campaign currently Limited by budget | **FALSE** — `primary_status` ELIGIBLE, reasons empty, both |
| 4 | Lost IS (budget) shows material missed demand | **FALSE** — 0.00% on both |
| 5 | Fresh data proves demand exists but budget throttles it | **FALSE** — 81–86% IS, LIMITED_BY_INVENTORY |

**Four of five evidence-based criteria are FALSE.** The one arguable criterion is
arithmetic capacity — and a budget rise cannot convert capacity into spend when
impression share is already 81–86% and Google itself reports LIMITED_BY_INVENTORY.

**PLAN-I1D was NOT created.** Raising budgets here would buy nothing except a
higher ceiling on an already-unbounded per-click price.

---

## 9. The $2,500 goal is not reachable

| Scenario | Assumption | August total |
|---|---|---|
| Status quo run rate | no further change | **$554** |
| Geo lift ×4.58 @ $30 capped CPC | ceiling applied | **$628** |
| Geo lift ×4.58 @ current $36.20 CPC | uncapped | **$705** |
| Geo lift ×4.58 @ escalated $60 CPC | uncapped, worst case | **$1,001** |

**Honest ceiling: roughly $550–$1,000**, and the top of that range is only
attainable by continuing to pay ~$60 per click — which the work order's own
constraint ("Do not buy low-quality traffic merely to spend") forbids in spirit.

The shortfall is **$1,500–$1,950**. It should be communicated to the client now,
not on September 1.

---

## 10. Recommendation — PLAN-K1 (DRAFT, NOT APPROVED)

**PLAN-K1 — August 27 CPC control and delivery diagnosis**
File: `clients/softwind-power-washing/plans/2026-08-27-plan-k1-cpc-control.yaml`
Fingerprint: **`3B77F0F4C879`** · 2 actions · 2 objects · **2 mutations**

Set `target_spend.cpc_bid_ceiling_micros = 30000000` ($30.00) on **both**
campaigns. Update mask exactly `target_spend.cpc_bid_ceiling_micros`.

**Budget-neutral. Neither budget is raised or lowered.**

### Why $30.00

Just above the **$28.23** documented top-of-page high, so head-term rank is
preserved in an account that is already rank-limited, while the tail is hard-
capped. Lost IS (rank) has fallen to 18.97%/14.29%, so the account wins most
auctions well under the ceiling — it binds only the outliers.

- **$24.00** (PLAN-B) rejected: sits *below* the $28.23 top-of-page high and
  would cost head-term rank. PLAN-B stays on hold.
- **No ceiling** rejected: unbounded per-click price behind a $333.33 budget with
  a proven $82.22 click and a monotonically rising trend.
- **$60.00** rejected: ratifies the outlier rather than preventing it.

### The cost of the ceiling, measured

Applied retroactively to the 7 clicks already bought, a $30.00 ceiling would have
cut spend from $253.39 to ~$166.61 — it **reduces** August spend by ~$87. That is
**4% of a $1,950 gap that is unreachable either way**. Trading 4% of an
unreachable goal for a hard bound against a $200 click is the correct trade.

### Why keep the $333.33 budget

With the ceiling in place the high budget becomes harmless — at max observed ~3
clicks/day × $30 the campaign cannot physically approach it — while preserving
full headroom for the geo expansion, which gets its first serving day today.
Without the ceiling, that same budget is the risk.

**Approval command:**

```
APPROVE PLAN-K1 3B77F0F4C879 FOR 1521725229
```

---

## 11. Open questions for the owner

| ID | Question | Recommendation |
|---|---|---|
| K1-Q1 | $2,500 is not reachable in 4 serving days. Restate the August target to the achievable $550–$1,000 range? | **Restate. Do not chase.** |
| K1-Q2 | Schedule expansion would add ~66 servable hours — the largest remaining delivery lever. Still BLOCKED on SCHED-Q1..Q6: is (631) 502-7946 answered outside Mon–Fri 08:00–18:00, and what is the callback commitment for an after-hours form lead? | Answer both. If after-hours calls are unanswered, expand to form-capture hours only, not 24/7. |
| K1-Q3 | 7 clicks and $253.39 have produced **0 conversions**. WhatConverts DNI is proven broken and foreign tag `AW-17878095007` is actively firing on the landing pages. | Approve PLAN-A2 and PLAN-A3 controlled tests before September. |

---

## 12. Monitoring

`scripts/softwind_checkpoint.py --label <immediately|1300|1700|eod>`

Emits today's spend, MTD, remaining, required rolling pace, projected August
total, impressions, clicks, average CPC, **individual click costs**, search terms,
negative candidates, leads, Lost IS (budget), Lost IS (rank), A/B spend split and
location performance — plus the emergency CPC stop-condition state.

Checkpoint 1 of 4 ran at 10:17 ET. Receipt:
`receipts/checkpoint-2026-08-27-1017-immediately.json`

**No automated budget writes.** Every further budget change requires a fresh
snapshot, plan, fingerprint and explicit approval.

---

## 13. Confirmation

**No unauthorized change occurred.** 28/28 red-team and no-change checks passed:
both budgets unchanged at $333.33 / $41.11, no CPC ceiling yet set, bidding still
TARGET_SPEND, Search Partners and Display still off, Presence geo intact, and
unchanged counts of 214 keywords, 54 ads, 94 campaign negatives, 12 ad schedules,
4 conversion actions, 20 campaign assets and 30 ad groups. Zero `change_event`
rows since `2026-08-26 18:00:32`.

Evidence: `snapshots/redteam-2026-08-27.json`
