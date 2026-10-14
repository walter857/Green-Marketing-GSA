# SOFTWIND POWER WASHING — CPC CEILING ANALYSIS

**Generated:** 2026-08-31 17:22 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
**Question:** is a **$10** maximum CPC ceiling a better controlled starting point than the
**$22** in PLAN-R3?

**PLAN-R3 is on hold. Fingerprint `97D8B268A80A` is NOT to be approved or used.**
No new fingerprint is created by this analysis.

Identity gate re-run fresh: `Softwind Power Washing - Live` / `1521725229` / manager `false` /
test `false` / ENABLED / USD / America/New_York — **PASS**.

---

## 1. Current ceiling on each campaign — verified, not assumed

Read from `campaign.target_spend.cpc_bid_ceiling_micros`:

| | Power Washing | Power Washing #2 |
|---|---|---|
| Campaign ID | `24103511039` | `24145053510` |
| **CPC ceiling** | **$30.00** (`30000000` micros) | **$30.00** (`30000000` micros) |
| Bidding strategy | TARGET_SPEND (Maximize Clicks) | TARGET_SPEND (Maximize Clicks) |
| Bidding system status | ENABLED | **LEARNING_SETTING_CHANGE** |
| Campaign status | ENABLED / SERVING / **ELIGIBLE** | ENABLED / SERVING / **LEARNING** |
| Daily budget | $41.50 | $41.11 |
| Locations | 80 targeted, 1 excluded, **PRESENCE** | 80 targeted, 1 excluded, **PRESENCE** |
| Search Partners / Display | **off / off** | **off / off** |
| Impressions | 218 | 46 |
| Valid clicks | 12 | 6 |
| Spend | $403.09 | $192.78 |
| Average CPC | $33.59 | $32.13 |
| CTR | 5.50% | 13.04% |
| Search IS | 48.00% | 64.10% |
| **Lost IS — rank** | **48.89%** | 28.21% |
| Lost IS — budget | 3.11% | 7.69% |
| Top IS | 32.44% | 56.41% |
| Absolute-top IS | 25.33% | 41.03% |

---

## 2. Valid billable CPC distribution

Valid clicks only. The four clicks Google invalidated and credited back at midday
(`power washing services`, $117.28) are **excluded** — they are no longer billable.

| Statistic | Value |
|---|---:|
| Lowest | **$5.71** |
| 25th percentile | $28.73 |
| **Median** | **$29.57** |
| Average | $33.10 |
| 75th percentile | $35.31 |
| 90th percentile | $54.49 |
| Highest | **$82.22** |
| n | 18 |

Every valid click, in order:
`5.71 · 22.11 · 22.13 · 26.66 · 28.73 · 28.73 · 29.04 · 29.32 · 29.57 · 29.57 · 29.72 · 29.91 ·
29.91 · 35.31 · 40.07 · 42.67 · 54.49 · 82.22`

> **The single most important fact in this analysis: there is no observed click between $5.71
> and $22.11.** One outlier at the bottom, then a **$16.40 gap**, then everything else.
> **Every candidate ceiling from $8 to $22 sits inside that gap.** The account's own click
> history therefore cannot distinguish $8 from $10 from $22 — all six win exactly the same
> single historical auction.

### By slice

**By campaign:** A $33.59 (12 clicks) · B $32.13 (6 clicks)

**By ad group:** Power Washing Near Me **$41.15** (7) · House Pressure Washing Estimate (B)
$34.95 (3) · Residential Pressure Washing Near Me (B) $29.45 (2) · Power Washing Services Near
Me (B) $29.04 (1) · Power Washing Services Near Me (A) $27.33 (4) · Power Washing West Islip
**$5.71** (1)

**By keyword:** `power washing near me` PHRASE **$48.06** (3) · `power washing near me` EXACT
$35.97 (4) · `house pressure washing estimate` $34.95 (3) · `residential pressure washing near
me` $29.45 (2) · `power washing services near me` PHRASE $29.04 (1) · `power washing services
near me` EXACT $27.33 (4) · `power washing west islip` **$5.71** (1)

**By search term:** `power washing near me` **$54.49** · `powerwash cost` $40.07 ·
`gas station pressure washing near me` $35.31 · `pressure washing` $29.91 ·
`power wash near me` $29.72 · `pressure washing near me` $29.57 · `power washing` $29.57 ·
`power washing companies near me` $28.73

**By device:** MOBILE $29.97 (14 clicks) · DESKTOP **$43.44** (4) · TABLET no clicks

**By hour:** 16:00 **$54.46** · 12:00 $40.07 · 11:00 $36.20 · 10:00 $35.31 · 09:00 $29.30 ·
08:00 $29.32 · 15:00 $28.73 · 14:00 $23.77 · 17:00 **$22.12** · 13:00 no clicks

---

## 3. The three prior bidding regimes — verified from the account, not quoted

| Regime | Serving days | Impressions | Impr/day | Valid clicks | Cost | Lost IS rank | Top IS | Abs-top IS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pre-$5 (08-05→08-07) | 3 | 5 | 1.7 | **0** | $0.00 | 62.58% | 28.85% | 9.99% |
| **$5.00 ceiling (08-08→08-16)** | 6 of 9 | 18 | **3.0** | **0** | **$0.00** | **76.67%** | 21.11% | **9.99%** |
| Uncapped (08-17→08-27) | 10 of 11 | 172 | 17.2 | 13 | $448.65 | 32.18% | 46.50% | 40.86% |
| **$30.00 ceiling (08-28→08-31)** | 3 of 4 | 69 | **23.0** | 5 | $147.22 | **13.37%** | 46.31% | 32.87% |

**All three prior findings verify:**

1. ✅ **"$5 produced ~12 days with no clicks."** Confirmed and slightly worse than stated —
   **12 calendar days (08-05 → 08-16) produced zero valid clicks**, of which 9 were under the
   $5.00 ceiling.
2. ✅ **"Uncapped produced a click above $80."** Confirmed — **$82.22** on 2026-08-26, which was
   exactly 2× the then-$41.11 daily budget.
3. ✅ **"Under $30, several valid clicks clustered close to $30."** Confirmed — the five
   post-ceiling clicks are **$29.04, $29.32, $29.57, $29.57, $29.72**; a $0.68 range under a
   $30.00 cap.

**And one correction to how the $5 result has been described.** A $5 ceiling did **not** stop
delivery. Impressions continued at 3.0/day. What collapsed was *position*: lost IS to rank rose
to **76.67%** and absolute-top sat at **9.99%**, which is Google's floor reporting value.

> **The failure mode of a too-low ceiling on this account is not "delivery stops." It is
> "delivery continues in positions that never get clicked."** That is a more expensive failure
> than it looks, because impressions with no clicks still depress expected CTR — which is
> already BELOW_AVERAGE on all six scored keywords and feeds directly back into Quality Score.

---

## 4. Local Keyword Planner CPC table — PRIMARY decision source

Current approved service area. English, Google Search only. Sampled on the four Towns in the
live 80-target footprint (North Hempstead, Babylon, Islip, Smithtown) plus the six largest
constituent places — `GenerateKeywordIdeas` caps geo targets at 10.

| Keyword | Vol/mo | Comp | Idx | TOP low | TOP high | **$10 clears?** | Trend (3mo vs prior 3) | Account coverage | Impr | Clk | Cost | CPC | QS | ExpCTR | AdRel | LP |
|---|---:|---|---:|---:|---:|:---:|---|---|---:|---:|---:|---:|---:|---|---|---|
| power washing near me | 260 | HIGH | 84 | **$10.90** | $28.32 | **NO** | +22.2% | SERVING | 90 | 7 | $288.07 | $41.15 | **1** | BELOW | BELOW | BELOW |
| power washing company near me | 260 | HIGH | 84 | **$10.90** | $28.32 | **NO** | +22.2% | SERVING | 14 | 0 | $0.00 | — | — | — | — | — |
| pressure washing services near me | 260 | HIGH | 84 | **$10.90** | $28.32 | **NO** | +22.2% | **NOT IN ACCOUNT** | — | — | — | — | — | — | — | — |
| power washing service | 140 | LOW | 13 | **$11.55** | $23.34 | **NO** | **+131.2%** | dormant (paused) | 3 | 0 | $0.00 | — | — | — | — | — |
| pressure washing near me | 90 | MEDIUM | 61 | **$8.75** | $24.66 | **YES** | −43.8% | **NOT IN ACCOUNT** | — | — | — | — | — | — | — | — |
| house washing near me | 40 | MEDIUM | 48 | **$10.46** | $24.75 | **NO** | −53.3% | dormant (paused) | 0 | 0 | $0.00 | — | — | — | — | — |
| power washing services near me | 30 | HIGH | 92 | **$10.62** | $28.70 | **NO** | −20.0% | SERVING | 111 | 5 | $138.35 | $27.67 | **3** | BELOW | ABOVE | BELOW |
| residential pressure washing near me | 20 | LOW | 0 | no data | no data | n/a | −52.9% | SERVING | 13 | 2 | $58.89 | $29.45 | — | — | — | — |
| soft washing near me | 10 | HIGH | 70 | $15.09 | $41.58 | **NO** | −40.0% | dormant (paused) | 0 | 0 | $0.00 | — | — | — | — | — |
| house washing company near me | 10 | HIGH | 100 | no data | no data | n/a | — | dormant (paused) | 2 | 0 | $0.00 | — | — | — | — | — |
| soft house washing near me | 10 | HIGH | 100 | no data | no data | n/a | +200.0% | SERVING | 0 | 0 | $0.00 | — | — | — | — | — |
| driveway pressure washing near me | 10 | — | 0 | no data | no data | n/a | +100.0% | SERVING | 0 | 0 | $0.00 | — | — | — | — | — |
| patio pressure washing near me | 0 | — | 0 | no data | no data | n/a | — | SERVING | 0 | 0 | $0.00 | — | — | — | — | — |
| concrete pressure washing near me | 0 | — | 0 | no data | no data | n/a | — | **NOT IN ACCOUNT** | — | — | — | — | — | — | — | — |

**Shared volume buckets — not separate demand.** `power washing near me`,
`power washing company near me` and `pressure washing services near me` all report
**260/mo @ $10.90–$28.32**. That is **one** bucket of 260, not three of 260.

### The head terms the account does **not** own

| Keyword | Vol/mo | Comp | TOP low | TOP high | **$10 clears?** |
|---|---:|---|---:|---:|:---:|
| **power washing** | **880** | HIGH | **$0.58** | $14.31 | **YES** |
| **pressure washing** | **480** | HIGH | **$0.30** | $10.77 | **YES** |
| house power washing | 40 | HIGH | $7.97 | $23.98 | **YES** |
| power washing long island | 70 | MEDIUM | $10.66 | $22.87 | NO |

---

## 5. New York State benchmark — SECONDARY ONLY

| Keyword | Vol/mo | Comp | TOP low | TOP high | $10 clears? |
|---|---:|---|---:|---:|:---:|
| power washing near me | 2,400 | MEDIUM | **$5.04** | $22.09 | YES |
| power washing company near me | 2,400 | MEDIUM | **$5.04** | $22.09 | YES |
| pressure washing services near me | 2,400 | MEDIUM | **$5.04** | $22.09 | YES |
| power washing service | 2,400 | LOW | **$4.42** | $18.14 | YES |
| pressure washing near me | 1,600 | MEDIUM | **$3.62** | $16.15 | YES |
| house washing near me | 590 | MEDIUM | **$3.59** | $15.00 | YES |
| power washing services near me | 390 | HIGH | **$5.07** | $15.90 | YES |
| soft washing near me | 110 | MEDIUM | **$5.57** | $20.01 | YES |
| residential pressure washing near me | 50 | LOW | no data | no data | n/a |
| house washing company near me | 10 | HIGH | $3.89 | $15.50 | YES |

> **This is exactly why the brief said not to decide on the statewide number.** Statewide
> top-of-page LOW is **$3.59–$5.57**; in the actual Nassau/Suffolk footprint the same keywords
> are **$8.75–$15.09** — **two to three times higher**. A statewide read would say "$10 is
> comfortable." In the market Softwind actually buys, it is not. Upstate New York is cheap;
> Long Island is not.

---

## 6. Ceiling comparison

Two independent models, deliberately shown side by side because they bracket the truth.

**Demand coverage** — share of local monthly demand (buckets with reportable bid data,
570/mo total) whose **top-of-page LOW** the ceiling clears.
**Observed-auction coverage** — under Maximize Clicks the CPC paid approximates the minimum
needed to outrank the next competitor, so a ceiling **cannot** have won an auction that cleared
above it *at that position*. This is an upper bound on historical auctions retained.

| Ceiling | Local demand clearing TOP-low | Buckets | Observed clicks ≤ ceiling | Naive capped avg CPC | Delivery verdict |
|---|---:|---:|---:|---:|---|
| **$8** | **0/mo — 0.0%** | 0/6 | 1/18 — 5.6% | $7.87 | **Severely restricts** — below every local top-of-page range |
| **$10** | **90/mo — 15.8%** | 1/6 | 1/18 — 5.6% | $9.76 | **Severely restricts** — clears only `pressure washing near me`, which is not a keyword in the account |
| **$12** | **560/mo — 98.2%** | 5/6 | 1/18 — 5.6% | $11.65 | **Moderate reduction** — clears every material bucket |
| **$15** | 560/mo — 98.2% | 5/6 | 1/18 — 5.6% | $14.48 | Moderate reduction, more headroom |
| **$18** | 570/mo — 100.0% | 6/6 | 1/18 — 5.6% | $17.32 | Mild reduction |
| **$22** | 570/mo — 100.0% | 6/6 | 1/18 — 5.6% | $21.10 | Mild reduction |
| **$30 (current)** | 570/mo — 100.0% | 6/6 | **13/18 — 72.2%** | $27.28 | Current behaviour |
| **No ceiling** | 100.0% | 6/6 | 18/18 — 100% | $33.10 | Proven to produce $82.22 clicks |

### The cliff

> **Between $10 and $12, the share of local demand whose top-of-page range the ceiling clears
> jumps from 15.8% to 98.2% — from 90 searches a month to 560.**

That single step is the whole decision. It is not a gentle curve; it is a threshold, created by
the fact that five of the six local buckets have a top-of-page LOW between **$10.46 and $11.55**.
**$10 lands just underneath all five of them.**

### Is $10 likely to…

| | Verdict |
|---|---|
| Continue generating qualified clicks | **Unlikely at current Quality Score.** $10 is below top-of-page LOW on every keyword that has ever produced a click in this account. |
| Reduce expensive clicks | **Yes, mechanically** — no click could exceed $10. |
| Reduce impressions moderately | **Probably not merely moderately.** The $5 precedent cut impressions to 3.0/day with 76.67% lost to rank. |
| Severely restrict delivery | **Yes — this is the most likely outcome.** |
| Stop delivery almost completely | **No.** Impressions would continue; clicks are what would stop. That is the $5 pattern. |

**Confidence: MEDIUM-HIGH on direction, LOW on magnitude.** Direction is supported by two
independent sources (Planner top-of-page ranges and the account's own $5 regime). Magnitude is
not forecastable from 18 clicks, and I will not manufacture a number for it.

---

## 7. Lowest defensible ceiling

**Campaign `24103511039` (Power Washing): $12.00.**
**Campaign `24145053510` (Power Washing #2): $12.00 — but do not change it yet (see §8).**

**$12 is the lowest ceiling that keeps the account eligible for top-of-page on essentially all
of its addressable local demand** (560 of 570 searches/month, 5 of 6 buckets — the only
exclusion is `soft washing near me` at 10/mo). Below $12 the account falls under the top-of-page
LOW of the five buckets that generate every click it has ever had.

### Should both campaigns use the same ceiling?

**Eventually yes — the demand, geography, landing pages and keywords are identical mirrors, so
there is no evidence base for differentiating them. But not simultaneously.** Campaign B is
`primary_status: LEARNING` with `bidding_strategy_system_status: LEARNING_SETTING_CHANGE`; a
second bid change would restart that window again. Campaign B is also the better control: 46
impressions against A's 218.

### Is $10 supported by current local market evidence?

**No — not as a blanket ceiling on the current keyword set.** It clears the top-of-page LOW on
**15.8%** of local demand, and that single qualifying bucket (`pressure washing near me`,
$8.75) **is not a keyword in the account.** In practical terms $10 clears the top-of-page range
for **0%** of what the account actually buys today.

### But $10 is right for something — and it is worth saying plainly

Walter's instinct is not wrong; it is aimed at the wrong keyword set. **$10 comfortably clears
the two largest, cheapest local buckets — `power washing` (880/mo, $0.58–$14.31) and
`pressure washing` (480/mo, $0.30–$10.77)** — which together are **2.4× the entire demand the
account currently competes for**, at roughly a third of the price.

**The account owns neither of them.** Those are exactly the SKAGs PLAN-R6 proposes creating
paused. **A $10 ceiling and the head-term expansion are the same strategy** — cheap, broad,
high-volume — and $10 becomes defensible the moment those keywords exist. On today's near-me
keyword set alone, it is not.

### Is a short controlled $10 test safer than immediately using $22?

**Neither is well evidenced, and that is the honest answer.** $10 and $22 win **exactly the same
1 of 18** observed auctions; the $16.40 gap between $5.71 and $22.11 contains no data at all.
The difference is direction of risk: **$22 risks continuing to overpay; $10 risks repeating the
$5 outcome.** $12 is the point where the Planner evidence turns, so **a controlled $12 test is
better evidenced than either.**

**PLAN-R3's $22 is not defended here.** It was chosen to sit above the documented top-of-page
highs. On the coverage model $18 achieves 100% just as $22 does, and $12 achieves 98.2%. There
is no evidence supporting $22 over $12 — only more caution.

---

## 8. Controlled test design — DRAFT ONLY, DO NOT EXECUTE

| Item | Specification |
|---|---|
| **Test one campaign or both** | **One.** Campaign A alone; campaign B is the within-account control. |
| **Campaign under test** | `24103511039` "Power Washing" — 218 impressions (4.7× B), `ELIGIBLE` not `LEARNING`, and **48.89% lost IS to rank**, the number a ceiling change moves most visibly |
| **Control campaign** | `24145053510` — **unchanged at $30.00**, no mutation of any kind |
| **Current ceiling** | $30.00 (`target_spend.cpc_bid_ceiling_micros = 30000000`) |
| **Proposed ceiling** | **$12.00** (`12000000`) — *or $10.00 if Walter chooses to accept the higher delivery risk knowingly* |
| **Mutation count** | **1** — one field on one campaign |
| **Start time** | A Monday 08:00 ET, at the start of a serving day. **Not** mid-day, and **not** on 08-31 with one day of data left in the month |
| **Minimum duration** | **10 serving days.** The schedule is Mon–Sat only, so that is ~12 calendar days |
| **Minimum impression threshold** | **150 impressions** before any read. At A's 23.0 impr/day that is ~7 serving days |
| **Minimum click threshold** | **8 valid clicks.** Below that, do not draw a CPC conclusion |
| **Stop — delivery collapse** | Impressions fall below **8/day** for 3 consecutive serving days (A's uncapped baseline is 17.2/day, current 23.0/day), **or** lost IS to rank exceeds **65%** on a 3-day rolling basis. Both are calibrated to the $5 regime's 3.0/day and 76.67% |
| **Stop — CPC still excessive** | Any valid click exceeds the ceiling by more than $0.50 later than 4 hours after the write. Bid propagation delay is real and expected — the $30 ceiling showed two apparently-breaching clicks that turned out to be pre-ceiling |
| **Stop — zero clicks** | **6 consecutive serving days with impressions but zero valid clicks.** This is the exact $5 signature and the single most important trip-wire |
| **Rollback value** | `target_spend.cpc_bid_ceiling_micros = 30000000`. One mutation, immediate |
| **Metrics to inspect after** | Impressions/day · valid clicks · **CTR** · average CPC · **CPC distribution, not just the mean** · Search IS · **lost IS to rank** · top and absolute-top IS · Quality Score components on `power washing near me` · search-term quality · **invalid-click rate** · and above all **cost per qualified lead once PLAN-R1 makes leads countable** |

**Do not judge this test from one hour or one click.** The account averages roughly one valid
click per serving day; a single click is noise, and a single hour is not even a sample.

**A prerequisite worth stating.** With zero recorded conversions, the test can only be judged on
clicks and CPC — not on leads. **PLAN-R1's conversion-counting fix should land before or
alongside this test**, otherwise a cheaper CPC that produces no leads will look like success.

**If $10 is chosen anyway**, the same design applies with `10000000`, plus one addition: check
impressions and lost-IS-to-rank at **day 3**, not day 7, because the $5 precedent suggests
degradation would show early.

---

## 9. Exact risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **$10 repeats the $5 outcome** — impressions continue, clicks stop | **HIGH at $10**, MEDIUM at $12 | Lost month of delivery | Zero-click stop condition at 6 serving days |
| 2 | **Depressed CTR feeds back into Quality Score.** Impressions in unclickable positions lower expected CTR, which is already BELOW_AVERAGE on all six scored keywords | MEDIUM | Raises future CPC even after rollback | Shortest viable test; rank stop condition at 65% |
| 3 | **Restarting the learning window.** Campaign B is already LEARNING | HIGH if B is changed | Delayed stabilisation | **Do not touch campaign B** |
| 4 | Lost IS to rank rises on campaign A from 48.89% | **CERTAIN** — this is the intended trade | Fewer impressions | It is the point of the test; judge on cost per qualified lead |
| 5 | 18 clicks is too small to conclude from | **CERTAIN** | Over-reading noise | Minimum thresholds; report the distribution |
| 6 | **Judging the test on cost per click instead of cost per lead** | HIGH | Optimising the wrong metric | Land PLAN-R1 first |
| 7 | **80.2% of raw clicks are invalid.** A ceiling change may alter that mix in ways that flatter or distort the CPC read | MEDIUM | Misattributed effect | Track invalid-click rate as a test metric |
| 8 | Month boundary — a 08-31 start straddles two billing months | HIGH if started today | Confounded comparison | Start Monday 2026-09-01 or later |
| 9 | **Deciding from the statewide benchmark** | — | Would give the wrong answer by 2–3× | Local footprint is the primary source; statewide is labelled secondary throughout |

---

## 10. Confirmation

**Zero external changes were made.** This analysis ran `SELECT` statements and
`KeywordPlanIdeaService.GenerateKeywordIdeas` only, which returns ideas without creating any
keyword plan resource. No mutate-capable service client was instantiated. Bidding, budgets,
campaign status, keywords, ads, locations, schedules, assets, audiences, negatives, conversions
and Final URLs are all untouched. **No new fingerprint was created.** PLAN-R3 `97D8B268A80A`
remains unapproved and unused.

**Evidence files:**
`snapshots/cpc-ceiling-study-2026-08-31T172*.json` ·
`snapshots/planner-ceiling-2026-08-31T172249.json` ·
`scripts/softwind_0831_cpc_ceiling_study.py` · `scripts/softwind_0831_planner_ceiling.py`
