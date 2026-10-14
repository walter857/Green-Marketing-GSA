# Softwind Power Washing — Full Google Ads Audit

**Read-only forensic audit · 2026-08-25**

---

## 1. Identity and scope verification

| Item | Required | Observed (fresh read-only API lookup) | Result |
|---|---|---|---|
| Child account name | Softwind Power Washing - Live | `Softwind Power Washing - Live` | **EXACT MATCH** |
| Child customer ID | 1521725229 | `1521725229` | **EXACT MATCH** |
| Manager account | not the MCC | `manager: false` | **PASS** |
| Test account | not a test | `test_account: false` | **PASS** |
| `- live` marker | required | present | **PASS** |
| Manager link | — | level 1 under `3373711342` "Green Marketing" | **VERIFIED** |
| Currency | — | USD | — |
| Time zone | — | **America/New_York** | — |
| Account status | — | ENABLED | — |
| Vertical | similar-local-service | scope_approval `approved: true`, Walter Correa | **PASS** |
| Exact service | Power Washing | recorded in work order | **PASS** |

Validators run: `validate_work_order.py` → **PASS** · `verify_setup.py --online` → **PASS**.
Evidence: `snapshots/identity-2026-08-25.json`.

**Audit timestamp: 2026-08-25 16:57:08 America/New_York.** The audit ran on its intended
date. August is split throughout as completed days (08-01 → 08-24) versus the current
partial day (08-25 00:00 → 16:57); the two are never blended.

---

## 2. Account configuration

| Setting | Value | Policy check |
|---|---|---|
| Campaigns | **2**, both SEARCH, both ENABLED / SERVING | Expected 1 — see §5 |
| Networks | Google Search only | **PASS** — Search Partners OFF, Display OFF |
| AI Max | `enable_ai_max: false` (both) | **PASS** |
| Automatically created text assets | `TEXT_ASSET_AUTOMATION: OPTED_OUT` | **PASS** |
| Final URL expansion | `FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION: OPTED_OUT` | **PASS** |
| Dynamic Search Ads | no DSA setting | **PASS** |
| Match types | Phrase + Exact only, no Broad | **PASS** |
| Location option | **PRESENCE** / PRESENCE (changed from PRESENCE_OR_INTEREST 2026-08-04) | **PASS** |
| Country sweep-exclusions | none | **PASS** |
| Language | English (`languageConstants/1000`) | OK |
| Bidding | Maximize Clicks (`TARGET_SPEND`), **no CPC ceiling** | **CONCERN** — §11 |
| Budgets | $41.11/day × 2 = **$82.22**, STANDARD, unshared | Brief said $33 |
| Auto-tagging | enabled | **PASS** |
| Conversion tracking | self-managed, ID `18369652705` | **PASS** |
| Enhanced conversions for leads | **disabled** | Gap |
| Shared negative lists attached | **none** | See below |
| Account-level negative criteria | 1 CONTENT_LABEL | Irrelevant to Search |

**Seven orphaned shared negative lists exist and are attached to nothing.** `Christmas
Lights Install` (424), `Leaf Removal initial` (386), `General List` (1,111), `Paver` (387),
`Outdoor Kitchen` (386), `General List - Irrigation Repair` (1,107), and a REMOVED `Names`
list (436) — **4,237 criteria in total**. `campaign_shared_set` returns **zero rows**, and
none carries type `ACCOUNT_LEVEL_NEGATIVE_KEYWORDS`. **They are suppressing nothing.** This
was checked explicitly because account-level negative lists apply account-wide and never
appear as campaign links.

---

## 3–6. Chronology, launch, architecture and legacy

Full detail in **`2026-08-25-launch-chronology.md`**. Headlines:

- **Campaign created 2026-08-04 09:22:12** · **first impression 2026-08-05** ·
  **first click and first spend 2026-08-17** · **first conversion: never**.
- 22 days old. 17 days with impressions. **4 days with any click or spend.**
- 5 zero-delivery days: 08-04, 08-14, and **08-09 / 08-16 / 08-23 — all Sundays**, dark
  because the Sunday daypart was deleted on 2026-08-07 16:17:45.
- A **$5.00 Max CPC ceiling** was added 2026-08-07 16:08 and **removed 2026-08-16 23:42**.
  Twelve consecutive zero-click days under the cap; first-ever click the day after removal;
  CPC then escalated to $40+.
- Second campaign created 2026-08-18 09:24:13 and enabled **4 minutes 8 seconds later**.
- 12 SKAGs are split 6/6 across two campaigns, one duplicated, one (`House Washing Company
  Near Me`) paused in both.
- Three legacy ad groups paused 2026-08-06 still hold **72 in-scope BOFU keyword texts**,
  including the entire *pressure washing* family. Live keyword texts: **11**.

---

## 7. Performance overview — every window

| Window | Impr | Clicks | CTR | Cost | Avg CPC | Conv |
|---|---:|---:|---:|---:|---:|---:|
| **All time** (2026-08-05 → 08-25 16:57) | **107** | **6** | **5.61%** | **$171.17** | **$28.53** | **0** |
| Since revamp (campaign 2 live, 08-18 →) | 80 | 5 | 6.25% | $165.46 | $33.09 | 0 |
| August completed days (08-01 → 08-24) | 82 | 3 | 3.66% | $49.95 | $16.65 | 0 |
| **Current partial day (08-25 to 16:57)** | **25** | **3** | **12.00%** | **$121.22** | **$40.41** | **0** |
| Last 7 completed days (08-18 → 08-24) | 55 | 2 | 3.64% | $44.24 | $22.12 | 0 |
| Campaign 1 all time | 93 | 4 | 4.30% | $108.99 | $27.25 | 0 |
| Campaign 2 all time | 14 | 2 | 14.29% | $62.18 | $31.09 | 0 |

Pre-revamp versus post-revamp cannot be compared meaningfully: the legacy ad groups were
paused on 2026-08-06, two days after launch, having produced **4 impressions in total**.
Stated as insufficient data rather than estimated.

### Impression share and rank

| Metric | Campaign 1 | Campaign 2 |
|---|---:|---:|
| Search impression share | 35.3% | 66.7% |
| **Search lost IS (budget)** | **2.5%** | **0%** |
| **Search lost IS (rank)** | **62.2%** | **33.3%** |
| Search top IS | 22.7% | 55.6% |
| Search absolute top IS | 12.6% | 55.6% |
| Top impression % | **87.1%** | **100%** |
| Absolute top impression % | 48.4% | 100% |

Lost IS (rank) fell from 90% on 08-04 to **0% by 08-24**, when campaign 1 held **100%
impression share on 21 impressions**. Rank is no longer the binding constraint; the pool is.

### Invalid clicks — a genuine anomaly

| Campaign | Valid clicks | Invalid clicks | Invalid rate |
|---|---:|---:|---:|
| Power Washing | 4 | **29** | **87.88%** |
| Power Washing #2 | 2 | 1 | 33.33% |
| **Total** | **6** | **30** | **83.3%** |

Google filtered and did not charge for 30 of 36 click attempts. On only 107 impressions
that implies a raw click attempt rate above 33%, which is far outside normal. The most
likely benign explanation is repeated self-clicking by the client or agency checking their
own ads; ClickCease is also installed on the site. **Recommendation:** stop clicking the
live ads, and cross-check against ClickCease's own reporting. Flagged as P2, not a crisis.

---

## 8. Daily delivery

| Date | Day | Campaign | Impr | Clicks | Cost | CTR | Avg CPC | Search IS | Lost IS rank |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 08-04 | Tue | PW | 0 | 0 | $0 | — | — | 10.0% | 90.0% |
| 08-05 | Wed | PW | **3** | 0 | $0 | 0% | — | 10.0% | 90.0% |
| 08-06 | Thu | PW | 1 | 0 | $0 | 0% | — | 100% | — |
| 08-07 | Fri | PW | 1 | 0 | $0 | 0% | — | 14.3% | 42.9% |
| 08-08 | Sat | PW | 4 | 0 | $0 | 0% | — | 50.0% | 50.0% |
| **08-09** | **Sun** | — | **0** | **0** | **$0** | — | — | — | **schedule dark** |
| 08-10 | Mon | PW | 1 | 0 | $0 | 0% | — | 50.0% | 50.0% |
| 08-11 | Tue | PW | 4 | 0 | $0 | 0% | — | 20.0% | 80.0% |
| 08-12 | Wed | PW | 4 | 0 | $0 | 0% | — | 10.0% | 90.0% |
| 08-13 | Thu | PW | 2 | 0 | $0 | 0% | — | 10.0% | 90.0% |
| 08-14 | Fri | PW | 0 | 0 | $0 | — | — | 10.0% | 90.0% |
| 08-15 | Sat | PW | 3 | 0 | $0 | 0% | — | 10.0% | 90.0% |
| **08-16** | **Sun** | — | **0** | **0** | **$0** | — | — | — | **schedule dark** |
| **08-17** | Mon | PW | 4 | **1** | **$5.71** | 25.0% | $5.71 | 25.0% | 75.0% |
| 08-18 | Tue | PW / PW#2 | 3 / 0 | 0 | $0 | 0% | — | 33.3% / 10.0% | 66.7% / 90.0% |
| 08-19 | Wed | PW / PW#2 | 10 / 2 | 1 / 0 | $22.13 | 10.0% | $22.13 | 45.5% / 100% | 54.5% / — |
| 08-20 | Thu | PW | 8 | 0 | $0 | 0% | — | 60.0% | 40.0% |
| 08-21 | Fri | PW / PW#2 | 2 / 2 | 0 | $0 | 0% | — | 66.7% / 100% | 33.3% / — |
| 08-22 | Sat | PW / PW#2 | 0 / 2 | 0 | $0 | 0% | — | 60.0% / 100% | 40.0% / — |
| **08-23** | **Sun** | — | **0** | **0** | **$0** | — | — | — | **schedule dark** |
| 08-24 | Mon | PW / PW#2 | **21** / 5 | 0 / **1** | $22.11 | 3.8% | $22.11 | **100%** / 75.0% | — / 25.0% |
| **08-25** | Tue | PW / PW#2 | 22 / 3 | **2 / 1** | **$81.15 / $40.07** | 9.1% / 33.3% | **$40.58 / $40.07** | — | — |

*08-25 is a partial day through 16:57.*

What the table shows: three visible regimes. **08-05 → 08-16** — impressions trickle, zero
clicks, zero spend under the $5.00 cap. **08-17 → 08-24** — cap removed, clicks begin at
$5.71 then settle around $22. **08-25** — CPC doubles to ~$40 and campaign 1 spends 197% of
its daily budget in under nine hours. Volatility this small is not a trend; the **regime
changes** are, and each maps to a dated configuration change.

---

## 9–10. Pacing and budget diagnosis

Full detail in **`2026-08-25-pacing-analysis.md`**.

| | |
|---|---:|
| MTD spend through the audit | **$171.17** |
| Remaining to $2,500 | **$2,328.83** |
| Remaining full days / serving days | **6 / 5** (Aug 30 Sunday is dark) |
| Required per remaining full day | **$388.14** |
| **Required impressions/day at 10% CTR and $16.29 CPC** | **238** |
| **Maximum defensible impressions/day** | **47.8** |
| **Highest defensible month-end spend** | **$638.49** |

**BUDGET-LIMITED? NO.** Lost IS (budget) 2.5% / 0%. Spending $7.78/day against $82.22.
**DEMAND-LIMITED? YES** — primary constraint. 100% impression share at 21–26 impressions/day.
**RANK-LIMITED? YES, historically** — resolved since 08-24, at a ruinous CPC.
**KEYWORD-COVERAGE-LIMITED? YES** — 11 live keyword texts against 72 paused ones.
**IS $2,500 REALISTIC? NO.** Shortfall **$1,861.51 (74.5%)**.

---

## 11. Bidding diagnosis

| | |
|---|---|
| Strategy (fresh read, both campaigns) | `TARGET_SPEND` — Maximize Clicks |
| **CPC ceiling** | **none** since 2026-08-16 23:42 |
| Portfolio strategy | none |
| Ad-group CPC bids | **$0.01 on every ad group** — ignored by Maximize Clicks, but a latent trap if bidding is ever switched to Manual CPC |
| Local top-of-page range (volume-weighted) | **$8.66 – $23.91** |
| **Actual average CPC** | **$28.53** |
| Highest single click | **$54.49** |

The account is paying above the volume-weighted high end of the local top-of-page range.

**Recommendation: stay on Maximize Clicks; add a $22.00 Max CPC ceiling.** Do **not** move
to Maximize Conversions or tCPA.

Reasoning, not preference: conversion volume is **zero**; conversion tracking is
**unverified**; the campaign is 22 days old; addressable volume is ~26 impressions/day.
Smart Bidding on a signal that has never fired, in a pool this thin, produces erratic
delivery rather than efficiency. A $22.00 ceiling sits below the $23.91 volume-weighted
high and above the $16.29 midpoint — it stops $40 clicks without repeating the $5.00
mistake that cost twelve days of zero delivery.

Revisit at ≥15 verified conversions in 30 days.

---

## 12. Impression and delivery diagnosis — root cause per constraint

Every candidate cause was tested, not assumed.

| Candidate cause | Tested | Verdict |
|---|---|---|
| Campaign / ad group status | both campaigns ENABLED, SERVING | **NOT a cause** |
| Keyword eligibility | **214/214 `system_serving_status: ELIGIBLE`** | **NOT a cause** |
| Low Search Volume status | **zero keywords flagged** | **NOT a cause** |
| Keyword approval | **214/214 APPROVED**, no disapproval reasons | **NOT a cause** |
| Ad approval / policy | **54/54 APPROVED + REVIEWED, zero policy topics** | **NOT a cause** |
| Negative conflicts with own keywords | 47 campaign negatives checked against all 11 live keywords | **NOT a cause** — no self-block |
| Shared list suppression | `campaign_shared_set` = 0 rows; no ACCOUNT_LEVEL list | **NOT a cause** |
| Ad-group negatives | **zero exist** | **NOT a cause** |
| Audience restrictions | AUDIENCE `bid_only: true` (observation) | **NOT a cause** |
| Device exclusions | all three devices targeted, no modifiers | **NOT a cause** |
| Geo mis-targeting | `user_location_view.targeting_location: true` on **every** row | **NOT a cause** — no leakage |
| Landing page availability | all six offer pages HTTP 200, no redirects | **NOT a cause** |
| Budget | lost IS (budget) 2.5% / 0% | **NOT a cause** |
| **Ad schedule** | **60 of 168 hours; Sunday dark; cut off at the peak hour** | **PRIMARY CAUSE** |
| **Search demand** | 800 BOFU searches/month locally; 100% IS at 25/day | **PRIMARY CAUSE** |
| **Keyword coverage** | 11 live texts vs 72 paused | **MAJOR CAUSE** |
| **Exact-match narrowness / city size** | `[power washing islip]` targets a hamlet of ~18k; **zero impressions all-time** | **MAJOR CAUSE** |
| **Quality Score** | `power washing near me` **QS 1**, both rows flagged `AD_GROUP_CRITERION_LOW_QUALITY` | **CONTRIBUTING** |
| Bid constraint | $5.00 ceiling 08-07 → 08-16 | **HISTORIC CAUSE — resolved** |
| Close-variant routing | 11 of 15 pressure-phrasing impressions misrouted | **CONTRIBUTING** |
| Account learning | campaign 1 `LEARNING (BIDDING_STRATEGY_LEARNING)` | **CONTRIBUTING** |
| AI Max / DSA / URL expansion | all off | **NOT a cause** |

**Six of the twelve live ad groups have never received a single impression:**
Power Washing Islip · Power Washing Dix Hills · Driveway Pressure Washing Near Me ·
Patio Pressure Washing Near Me · Residential Pressure Washing Near Me ·
Soft House Washing Near Me. Nineteen of thirty ad groups account-wide have zero impressions.

This is **not** "low search volume" as a status — no keyword carries that flag. It is
genuine market thinness in an eight-city footprint, compounded by exact-match keywords
aimed at very small places, compounded by a schedule that is dark 64% of the week.

---

## 13. Ad-group analysis

Full table: **`2026-08-25-ad-group-performance.csv`**. Live ad groups:

| Campaign | Ad group | Impr | Clicks | CTR | Cost | Avg CPC | Search IS | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| PW | Power Washing Services Near Me | 51 | 1 | **1.96%** | $22.13 | $22.13 | 66.7% | **CONSTRAINED** — absorbs the head term and every pressure-phrasing variant; worst CTR in the account |
| PW | Power Washing Near Me | 19 | 2 | **10.53%** | $81.15 | **$40.58** | 21.4% | **STRUCTURAL ISSUE** — best CTR, worst CPC, **QS 1** |
| PW#2 | House Pressure Washing Estimate | 13 | 2 | 15.38% | $62.18 | $31.09 | 66.7% | **WEAK INTENT** — pulls cost-research queries; 36% of all spend, no lead |
| PW | Power Washing Company Near Me | 7 | 0 | 0% | $0 | — | 50.0% | **NEEDS DATA** |
| PW | Power Washing West Islip | 1 | 1 | 100% | $5.71 | $5.71 | 100% | **NEEDS DATA** — single event |
| PW#2 | Power Washing Services Near Me | 1 | 0 | 0% | $0 | — | — | **STRUCTURAL ISSUE — duplicate of campaign 1** |
| PW | Power Washing Islip | 0 | 0 | — | $0 | — | — | **CONSTRAINED** — hamlet ~18k, exact match, never served |
| PW | Power Washing Dix Hills | 0 | 0 | — | $0 | — | — | **CONSTRAINED** — same |
| PW#2 | Driveway Pressure Washing Near Me | 0 | 0 | — | $0 | — | — | **NEEDS DATA** — live only since 08-18 |
| PW#2 | Patio Pressure Washing Near Me | 0 | 0 | — | $0 | — | — | **NEEDS DATA** |
| PW#2 | Residential Pressure Washing Near Me | 0 | 0 | — | $0 | — | — | **NEEDS DATA** |
| PW#2 | Soft House Washing Near Me | 0 | 0 | — | $0 | — | — | **NEEDS DATA** |

**None of the zero-impression ad groups is "bad".** Four have been live for seven days in a
market with ~26 daily impressions to share among eleven SKAGs. The two city SKAGs are a
different matter: `[power washing islip]` and `[power washing dix hills]` are exact-match
terms for places of roughly 18,000 and 26,000 people, and after 22 and 7 days respectively
they have produced nothing. They are **structurally unlikely to ever deliver** at exact
match, and that is a design finding, not a performance one.

---

## 14. Keyword analysis

Full scoring: **`2026-08-25-keyword-audit.csv`** (214 rows).

**11 distinct live keyword texts, 21 rows, all Phrase + Exact, all APPROVED, all ELIGIBLE.**

| Keyword | Match | QS | Exp CTR | Ad rel | LP exp | Local demand | Verdict |
|---|---|---|---|---|---|---|---|
| power washing near me | P + E | **1** | Below Avg | Below Avg | Below Avg | **110/mo, $10.89–$28.23** | **KEEP** — fix the ad, not the keyword |
| power washing services near me | P + E | **3** | Below Avg | **Above Avg** | Below Avg | 110/mo bucket | **KEEP** |
| power washing company near me | P + E | n/a | n/a | n/a | n/a | 20/mo, $10.95–$21.73 | KEEP |
| power washing islip | E | n/a | n/a | n/a | n/a | below Planner threshold | **WATCH** |
| power washing west islip | E | n/a | n/a | n/a | n/a | below threshold | WATCH |
| power washing dix hills | E | n/a | n/a | n/a | n/a | below threshold | **WATCH** |
| residential pressure washing near me | P + E | n/a | n/a | n/a | n/a | in-scope | KEEP |
| house pressure washing estimate | P + E | n/a | n/a | n/a | n/a | mixed | **WATCH** |
| driveway pressure washing near me | P + E | n/a | n/a | n/a | n/a | in-scope | KEEP |
| patio pressure washing near me | P + E | n/a | n/a | n/a | n/a | in-scope | KEEP |
| soft house washing near me | P + E | n/a | n/a | n/a | n/a | in-scope | KEEP |
| **house washing company near me** | P + E | — | — | — | — | **40/mo, $10.46–$32.09** | **EXPAND — paused in both campaigns** |

Quality Score is available for only 2 of the 11 texts. Everything else reads
**NOT ENOUGH DATA** and is reported as such — no score was invented.

**Intent scoring** (BOFU / local / specificity / hire-likelihood, each 0–5; equipment
ambiguity 0–5 where higher is worse) is in the CSV. The live set scores well: every keyword
is a service-buying phrase. The problems are demand and copy match, not intent.

Two nuances worth stating:
- A keyword with perfect intent and no volume cannot help. `[power washing islip]` is
  flawless intent and has produced **zero impressions in 22 days**.
- `house pressure washing estimate` scores lower on BOFU (4/5) than it looks. "Estimate"
  attracts *"how much does it cost"* as readily as *"send me a quote"*, and the search-term
  data confirms it.

---

## 15. Search-term analysis

Full table: **`2026-08-25-search-term-verdicts.csv`** — **all 45 terms, no impression
threshold**, as required for a new account.

**Verdicts: 30 KEEP · 6 ROUTING ISSUE · 6 WATCH · 3 NEGATIVE CANDIDATE.**

### Phrasing split

| Phrasing | Impressions | Clicks | CTR | Cost |
|---|---:|---:|---:|---:|
| "power wash" family | 69 | 5 | **7.25%** | $165.46 |
| **"pressure wash" family** | **15** | **0** | **0.00%** | **$0.00** |
| other | 5 | 0 | 0% | $0 |

Fifteen impressions of pressure-washing demand, zero clicks. **Eleven of the fifteen were
served by a *power washing* ad group.** This is the clearest single piece of evidence in
the audit for a dedicated Pressure Washing SKAG.

### Top terms

| Term | Impr | Clicks | Cost | Matched keyword | Verdict |
|---|---:|---:|---:|---|---|
| power washing | **14** | **0** | $0 | power washing services near me (EXACT / NEAR_EXACT) | KEEP — but 0% CTR on the biggest term |
| power washing near me | 5 | 1 | **$54.49** | power washing near me (EXACT) | KEEP |
| best power washing company | 3 | 0 | $0 | power washing services near me | KEEP |
| power wash companies near me | 3 | 0 | $0 | power washing services near me | KEEP |
| powerwash company | 3 | 0 | $0 | power washing services near me | KEEP |
| **pressure washing service near me** | 3 | 0 | $0 | power washing services near me | **ROUTING ISSUE** |
| **average cost to power wash a house** | 2 | **1** | **$22.11** | house pressure washing estimate | **WATCH** |
| **powerwash cost** | 2 | **1** | **$40.07** | house pressure washing estimate | **WATCH** |
| roof washing near me | 2 | 0 | $0 | power washing company near me | **NEGATIVE CANDIDATE** |
| house cleaning services near me | 1 | 0 | $0 | house washing company near me | **NEGATIVE CANDIDATE** |
| slate roof cleaning near me | 1 | 0 | $0 | house washing company near me | **NEGATIVE CANDIDATE** |

**Only three negative candidates, and all three are out-of-scope *services*:** `roof
cleaning`, `roof washing`, `house cleaning`. Roof cleaning is outside this work order's
approved scope; "house cleaning services" reads as interior maid work.

**No protected term was proposed as a negative.** `near me`, `quote`, `estimate`, `cost`,
`price`, `best`, `hire`, `local` all appear in the term list and all were kept.

The cost-research cluster — `average cost to power wash a house`, `powerwash cost`, `cost to
power wash`, `price to powerwash house`, `how much is powerwashing a house` — took **2
clicks and $62.18, 36% of all account spend, with no lead.** It is still marked **WATCH,
not NEGATIVE**: two clicks prove nothing, agency policy protects cost terms, and these
convert in this vertical. The fix is intent re-mapping, not suppression.

**Also flagged:** the existing campaign negative **`how to` at BROAD match** blocks any
query containing both "how" and "to" — including *"how much does it cost **to** power wash
a house"*. Recommend narrowing to PHRASE.

---

## 16. SKAG routing and close-variant analysis

| Search term | Matched keyword | Actual ad group | Ideal ad group | Classification |
|---|---|---|---|---|
| power washing | power washing services near me (E) | Power Washing Services Near Me | Power Washing Near Me | **INEFFICIENT** — 14 impr, 0 clicks |
| power wash near me | power washing services near me (E) | Power Washing Services Near Me | Power Washing Near Me | ACCEPTABLE CLOSE VARIANT |
| powerwash near me | power washing near me (E) | Power Washing Near Me | same | **CORRECT** |
| power washing companies near me | power washing near me (P) | Power Washing Near Me | Power Washing Company Near Me | **INEFFICIENT** |
| powerwashing companies near me | power washing services near me (E) | Power Washing Services Near Me | Power Washing Company Near Me | **INEFFICIENT** — took a $22.13 click |
| **pressure washing near me** | power washing services near me (P/E) | Power Washing Services Near Me | **Pressure Washing Near Me (does not exist)** | **SERIOUS MISMATCH** |
| **pressure washing service near me** | power washing services near me (E) | Power Washing Services Near Me | **Pressure Washing Services Near Me (does not exist)** | **SERIOUS MISMATCH** |
| pressure washing companies near me | power washing company near me (P) | Power Washing Company Near Me | Pressure Washing Company Near Me | **SERIOUS MISMATCH** |
| local services pressure washing | power washing services near me (E) | Power Washing Services Near Me | Pressure Washing Services Near Me | INEFFICIENT |
| house exterior power washing | power washing services near me (E) | Power Washing Services Near Me | House Washing Company Near Me *(paused)* | **INEFFICIENT** |
| roof washing near me | power washing company near me (P) | Power Washing Company Near Me | **none — out of scope** | **SERIOUS MISMATCH** |
| house cleaning services near me | house washing company near me (P) | House Washing Company Near Me | **none — wrong industry** | **SERIOUS MISMATCH** |
| average cost to power wash a house | house pressure washing estimate (E) | House Pressure Washing Estimate | acceptable, weak intent | ACCEPTABLE CLOSE VARIANT |

Google's close-variant engine is doing very heavy lifting: `[power washing services near
me]` as an **Exact** keyword matched **14 distinct search terms** including "power washing",
"pressure washing near me", "house exterior power washing" and "powerwash company". Exact
match is behaving close to phrase here.

**No aggressive cross-negatives are recommended.** With ~26 impressions a day, forcing
perfect routing with cross-negatives would suppress real buyer demand for a marginal
relevance gain. The correct fix is **adding the missing SKAGs** so the right ad group wins
naturally — and, for roof/house-cleaning, three narrow out-of-scope negatives.

---

## 17. RSA and CTR analysis

Full table: **`2026-08-25-rsa-audit.csv`** (54 ads).

| Check | Result |
|---|---|
| Live RSAs | **24 — exactly 2 per live ad group** ✓ |
| Approval | **54/54 APPROVED + REVIEWED**, zero policy topic entries ✓ |
| Ad Strength | 38 EXCELLENT, 13 GOOD, 3 POOR |
| Headlines / descriptions per ad | **15 / 4 on all 54** ✓ |
| Character limits | **zero violations** — max headline 30, max description 90 ✓ |
| Duplicate assets within an ad | **none** ✓ |
| Unverified claims | **none found** — "free quote" is verified on the live pages and site ✓ |
| Awkward "near me" copy | **none** — copy correctly uses "Near You" ✓ |
| **Pinned assets** | **ZERO across all 24 live RSAs** |
| Final URL alignment | correct per ad group ✓ |

### The two real copy problems

**1 · No pinning anywhere.** Google can serve a combination whose first headline never
mentions the searched service. In `Power Washing Near Me` the headline pool includes
"Local Exterior Cleaning", "Restore Your Curb Appeal" and "Clean Siding & Hardscapes" — a
searcher who typed *power washing near me* may see none of those words. This is a direct
contributor to **Below Average expected CTR and Below Average ad relevance on a QS 1
keyword**.

**2 · The two RSAs in an ad group are too similar.**

| Ad group | Shared headlines / 15 | |
|---|---:|---|
| Driveway Pressure Washing Near Me | **11** | **73%** |
| Soft House Washing Near Me | 8 | 53% |
| Power Washing Near Me | 7 | **47%** |
| Patio Pressure Washing Near Me | 7 | 47% |
| Power Washing Services Near Me (both campaigns) | 5 | 33% |
| Power Washing Company Near Me | 6 | 40% |
| Islip / West Islip / Dix Hills / Residential | 3 | 20% |
| House Pressure Washing Estimate | 2 | 13% ✓ |

The SOP requires two *distinct* RSAs. At 73% overlap the second ad is not a real test.

### Ad-level performance

**INSUFFICIENT DATA to declare a winner anywhere.** The highest-impression single ad has
fewer than 30 impressions. No RSA-versus-RSA conclusion is drawn, and none should be.
Verdict for all 24: **INSUFFICIENT DATA — structural review only.**

Drafted replacements for the QS 1 ad group are in the expansion plan, character-validated.

---

## 18. Asset analysis

| Asset type | Count | Status | Finding |
|---|---:|---|---|
| Sitelinks (campaign) | 4 | ENABLED, ELIGIBLE | Within SOP 4–8, **but all point to `softwindli.com`** |
| Sitelinks (account) | 4 | ENABLED | Includes "Pressure Washing" → main site |
| **Callouts (campaign)** | **4** | ENABLED | **Below the SOP minimum of 8** |
| Callouts (account) | 4 | ENABLED | Overridden by campaign-level |
| Structured snippets | 1 set | ENABLED | Values all in scope ✓ |
| Call asset | 1 | ENABLED | **(631) 502-7946 — matches approved number** ✓ |
| **Business logo** | 1 | **`primary_status: PENDING`** | Not serving |
| Image assets | **0** | — | None exist |
| Location assets | LOCATION_SYNC "Business Profile" | ENABLED | Serving — 49 LOCATION_EXPANSION impressions |
| Lead form / promotion assets | 0 | — | None |

**Call asset:** `(631)502-7946`, US, `USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION`. Correct
and matching. Linked to **both** campaigns — any future schedule edit rewrites hours on both.

**It has served 35 impressions and taken 0 clicks.** Not alarming at this volume, but worth
watching given mobile is 73% of impressions.

**Sitelink destinations are the material problem.** All show the untracked **(631)
502-5402**, carry a 50-option service dropdown and a 50-state address form, and link out to
paver sealing, masonry, Christmas lights and landscaping — services outside this work order.
The `Customer Reviews` sitelink additionally hit an **SG-Captcha interstitial** that a full
browser could not clear on first attempt, and its reviews are about fencing, tree removal
and hedge trimming, not power washing.

**Real cost already incurred:** SITELINKS took **1 click for $40.07 — 23% of all account
spend** — to `softwindli.com/services/landscaping/pressure-washing/`.

### Click-type distribution

| Click type | Impressions | Clicks | Cost |
|---|---:|---:|---:|
| URL_CLICKS (headline) | 107 | 5 | $131.10 |
| **SITELINKS** | 40 | **1** | **$40.07** |
| **CALLS** | 35 | **0** | $0 |
| LOCATION_EXPANSION | 49 | 0 | $0 |
| GET_DIRECTIONS | 8 | 0 | $0 |

---

## 19. Location analysis

**Targeted — 8 locations, identical on both campaigns, all positive, no exclusions,
PRESENCE:**

| Geo ID | Type | Name |
|---|---|---|
| 1022729 | City | Bellmore, NY *(Nassau)* |
| 1023035 | City | **Islip, NY** *(Suffolk — the hamlet, ~18k, not the Town of Islip ~340k)* |
| 1023415 | City | Syosset, NY *(Nassau)* |
| 1023482 | City | West Islip, NY *(Suffolk)* |
| 9051836 | City | Dix Hills, NY *(Suffolk)* |
| 9052792 | City | Salisbury, NY *(Nassau)* |
| 9198508 | **Municipality** | North Hempstead, NY *(Nassau town, ~230k)* |
| 9214462 | **Municipality** | Babylon, NY *(Suffolk town, ~210k)* |

**Presence targeting confirmed** (`positive_geo_target_type: PRESENCE`, changed from
PRESENCE_OR_INTEREST on 2026-08-04 15:16:52). **No excluded locations. No country sweep.**

### Where delivery actually landed

| City | Impr | Clicks | Cost |
|---|---:|---:|---:|
| Dix Hills | 19 | 2 | $81.15 |
| North Hills | 13 | 0 | $0 |
| Babylon | 12 | 0 | $0 |
| West Babylon | 7 | 1 | $22.13 |
| North Bellmore | 9 | 0 | $0 |
| Westbury | 7 | 2 | $62.18 |
| Islip | 5 | 0 | $0 |
| West Islip | 5 | 0 | $0 |
| Great Neck Plaza, Manhasset, Roslyn, Copiague, Deer Park, Lindenhurst, North Babylon, Wheatley Heights, Salisbury | 1–3 each | 1 | $5.71 |

**`user_location_view.targeting_location` is `true` on every single row. Zero out-of-area
delivery.** The spill into West Babylon, North Babylon, Copiague, Lindenhurst, Manhasset,
Roslyn and Great Neck Plaza is correct — those sit inside the Babylon and North Hempstead
township targets.

**The finding:** this is a **fragmented, non-contiguous footprint straddling two counties**
with large gaps. Six of the eight targets are small hamlets. The Towns of Islip (~340k),
Huntington (Dix Hills sits inside it), Oyster Bay (Syosset sits inside it) and Hempstead
are almost entirely untargeted — yet Dix Hills and Syosset are targeted as isolated points
inside them.

**No location change is recommended in this audit.** The verified service area is
**UNKNOWN** and expanding it requires a client fact, not a technical judgment. It is
question 1 in the consolidated list, and it is the **only lever that materially changes the
demand ceiling.**

---

## 20. Schedule, day and hour analysis

**Ad schedule as read: Monday–Saturday 08:00–18:00. Six dayparts. No Sunday. 60 of 168
hours = 35.7% of the week.**

| Day | Impr | Clicks | CTR | Cost |
|---|---:|---:|---:|---:|
| Monday | 31 | 2 | 6.45% | $27.82 |
| Tuesday | 32 | 3 | 9.38% | $121.22 |
| Wednesday | 19 | 1 | 5.26% | $22.13 |
| Thursday | 11 | 0 | 0% | $0 |
| Friday | 5 | 0 | 0% | $0 |
| Saturday | 9 | 0 | 0% | $0 |
| **Sunday** | **0** | **0** | — | **$0** | 

Sunday does not even appear in the day-of-week segment — the campaign has never run.

| Hour | 00–07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | **17** | 18–23 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Impressions | **dark** | 5 | 8 | 8 | 7 | 12 | 11 | 11 | 9 | 13 | **23** | **dark** |
| CTR | — | 0% | 0% | 0% | 0% | 8.3% | 0% | 9.1% | 0% | **15.4%** | 8.7% | — |

**This is the most actionable finding in the audit.** The 17:00 hour is the single largest
in the account — **23 impressions, 21.5% of all delivery** — nearly double the next-highest.
The demand curve is still climbing when the schedule cuts it off at 18:00. Morning hours
08:00–11:00 produced 28 impressions and **zero clicks**; afternoon and evening hours carry
every click the account has ever received.

The campaign is switched off precisely when its buyers are searching.

**Verdict: the schedule is materially suppressing qualified demand.**

**Recommendation with a caveat.** Published hours are **Mon–Fri 8AM–6PM** (from
`softwindli.com/contact-us/`) — so the ad schedule already runs one day beyond office hours
on Saturday, which produced 9 impressions and 0 clicks. Opening to 24/7 is safe for **form**
capture at any hour; it is not safe to imply a live phone answer.

**Schedule expansion: NEEDS INTERNAL CONFIRMATION** on after-hours call answering and the
callback commitment for an evening or Sunday form lead. Recommended shape: campaign 24/7,
call asset constrained to answerable hours.

---

## 21. Device analysis

| Device | Impr | Share | Clicks | CTR | Cost | Avg CPC |
|---|---:|---:|---:|---:|---:|---:|
| **Mobile** | **78** | **72.9%** | **5** | **6.41%** | $144.51 | $28.90 |
| Desktop | 28 | 26.2% | 1 | 3.57% | $26.66 | $26.66 |
| Tablet | 1 | 0.9% | 0 | 0% | $0 | — |

Mobile carries nearly three quarters of impressions, five of six clicks, and **1.8× the
desktop CTR**. No device bid modifiers are set and all three devices are targeted.

Mobile experience was verified in a real browser at 390×844: **all six offer pages render
with the form present, the `tel:` link present and 7–9 CTAs visible**. Body content is
~10% shorter than desktop, which is normal responsive behaviour. **No mobile defect found.**

**No device-specific action is recommended.** One click of desktop data is not a basis for
a bid modifier. The actionable conclusion is that all future page and copy work must be
mobile-first, and that the call asset's zero clicks on 35 impressions deserves monitoring
on a mobile-dominant account.

---

## 22. Conversion tracking

Full detail in **`2026-08-25-conversion-audit.md`**. Summary:

- Three lead actions correctly designed: form / website call / call-asset call, all
  `ONE_PER_CLICK`, 60-second qualified-call threshold, data-driven attribution.
- **Campaign-specific goals are correctly set** — the biddable set on both campaigns is
  exactly the three lead categories. Get Directions is present but **not biddable**.
- **`Local actions - Directions` is `primary_for_goal: true` at account level** with
  `MANY_PER_CLICK` counting. Contained today; a hazard for any future campaign.
- **All leads valued $0.00** (`always_use_default_value: true`) → ROAS and profit reporting
  are structurally impossible.
- **A second Google Ads tag `AW-17878095007` fires on every landing page.**
- **Click-ID preservation PASS** — gclid and UTMs verified surviving to the final URL.
- **Enhanced conversions for leads: disabled.**
- **Zero conversions all time.** On 6 clicks this proves nothing either way. **Tracking is
  unverified, not proven broken.**
- **END-TO-END TEST REQUIRES SEPARATE APPROVAL.** No form was submitted; no call was placed.

---

## 23. Landing pages

Full table: **`2026-08-25-landing-page-audit.csv`**. Verified in a real browser at two
viewports — these hosts sit behind SG-Captcha and a plain fetch would have produced a false
"no tracking" result.

| Ad group | Final URL | Status | H1 | Match |
|---|---|---|---|---:|
| 6 power-washing SKAGs | `/power-washing-services-islip-west-islip-dix-hills/` | 200 | "Power Washing Service In Islip, West Islip & Dix Hills, NY" | **9/10** |
| Residential Pressure Washing | `/residential-pressure-washing/` | 200 | "Residential Pressure Washing In Islip, West Islip & Dix Hills, NY" | **9/10** |
| House Pressure Washing Estimate | `/house-pressure-washing-estimate/` | 200 | "Get A House Pressure Washing Estimate In Long Island" | **8/10** |
| Driveway Pressure Washing | `/driveway-pressure-washing/` | 200 | "Driveway Pressure Washing In Islip, West Islip & Dix Hills, NY" | **9/10** |
| **Patio Pressure Washing** | **`/patio-power-washing/`** | 200 | **"Patio Pressure Washing In Islip, West Islip & Dix Hills, NY"** | **9/10** |
| Soft House Washing | `/soft-house-washing/` | 200 | "Soft House Washing In Islip, West Islip & Dix Hills, NY" | **9/10** |
| Sitelinks | `softwindli.com/*` | 200 / 202 | "CONTACT US", "OUR WORK", "SERVICE AREAS", "CUSTOMER REVIEWS" | **3/10** |

### The `/patio-power-washing/` slug question — answered

The work order flagged this specifically. **The slug is not a problem.** The page's H1 is
*"Patio Pressure Washing In Islip, West Islip & Dix Hills, NY"*, its H2 is *"Professional
Patio Pressure Washing For Pavers, Concrete And Stone"*, and the body uses "pressure
washing" **17 times** against "power washing" 8 times, with "patio" 41 times. Content, not
the slug, drives Quality Score's landing-page component, and the content is strongly aligned
to `patio pressure washing near me`. **No change recommended.**

### What is right across all six offer pages

HTTP 200, no redirects, HTTPS, self-referencing canonical, correct `noindex, nofollow` for
paid pages, **gclid and UTMs preserved end-to-end**, approved phone **(631) 502-7946** in
both `tel:` links and body copy, a short 4-field Gravity Form (Name*, Phone*, Email*,
optional project note), 7–9 CTAs, strong city and service message match, mobile parity, and
**no links out to out-of-scope services**.

### Three real defects

**LP-1 · A published authoring instruction (P1).** The highest-spend page — $108.99, 64% of
all account spend — contains in live body copy:

> "Refresh siding, driveways, patios, walkways, pavers, and concrete **without making the
> page about unrelated services**."

**LP-2 · Evergreen countdown with no offer (P1).** All six pages show **"Offer Ends in — 06
DAY 02 HRS 55 MIN"**. Two different pages loaded seconds apart both read ~6d 2h 55m,
indicating a rolling per-visitor timer, not a real deadline. And the block it sits under is
headed *"Get A Free Quote"* — **there is no offer to expire.** A resetting countdown on a
free quote is manufactured urgency: a Google Ads misleading-claims risk and an FTC
deceptive-urgency risk. **Not removed during this READ audit.**

**LP-3 · Sitelink destinations are a different, weaker experience (P1).** Untracked phone
**(631) 502-5402**, a 50-option service dropdown, a 50-state address form on a Long Island
local service, links out to paver sealing / masonry / Christmas lights / landscaping, and
`/reviews/` presents a **HAPPY / NEUTRAL / POOR emoji gate** before routing reviewers —
which `config/agency.yaml` prohibits (`review_collection.prohibit_review_gating: true`) and
Google's review policy also prohibits. Already cost **$40.07, 23% of all spend**.

---

## 24. Quality Score deep dive

| Keyword | Match | QS | Expected CTR | Ad relevance | Landing page | Primary constraint |
|---|---|---:|---|---|---|---|
| power washing near me | PHRASE | **1** | **Below Average** | **Below Average** | **Below Average** | **All three** — see below |
| power washing near me | EXACT | **1** | **Below Average** | **Below Average** | **Below Average** | **All three** |
| power washing services near me | PHRASE | **3** | **Below Average** | Above Average | **Below Average** | Expected CTR + landing page |
| power washing services near me | EXACT | **3** | **Below Average** | Above Average | **Below Average** | Expected CTR + landing page |
| All other 17 live keyword rows | — | **NOT ENOUGH DATA** | NOT ENOUGH DATA | NOT ENOUGH DATA | NOT ENOUGH DATA | insufficient impressions |

**Both `power washing near me` rows carry `primary_status_reasons:
["AD_GROUP_CRITERION_LOW_QUALITY"]`** — Google is explicitly flagging them as rarely shown
due to low quality. These are the only two keywords in the account with that flag, and they
are the account's highest-intent term.

### Diagnosis and action, per component

**Expected CTR — Below Average on all four scored rows.** The ad group has 19 impressions
and 2 clicks. With zero pinning, Google may serve headline combinations that never echo
"power washing". **Action: P2-1 RSA rewrite with H1 pinned to a near-you power-washing
variant.**

**Ad relevance — Below Average on `power washing near me`, Above Average on `power washing
services near me`.** Instructive: the *services* ad group's copy leads with "Power Washing
Services", while the *near me* ad group's copy leads with generic benefit lines. Same
landing page, different result. **Action: same RSA rewrite.**

**Landing page experience — Below Average on all four rows, including the ad group whose ad
relevance is Above Average.** This is the one component the copy fix will not touch. The
page is technically sound — 200, fast-loading, mobile-parity, strong H1 match — so the
likely drivers are its youth (first crawled in August), the `noindex, nofollow` directive,
thin body content (~7,000 characters), and plausibly the published authoring instruction and
the fake countdown. **Action: LP-1 and LP-2, then re-measure after 2–4 weeks of delivery.**

**Confidence: MEDIUM.** Quality Score at 19–51 impressions is unstable. The components are
directionally reliable; the composite score will move as volume accrues.

---

## 25–26. Market demand and seasonality

Keyword Planner, `GOOGLE_SEARCH` network, **exactly the eight geo targets the campaigns
use**, English, 12 complete months to July 2026. **6,987 ideas returned.** Planner groups
semantically identical phrasings into shared volume buckets, so buckets were collapsed
before any total was taken — summing raw rows would have overstated demand several-fold.

| Category | Buckets | Local monthly searches |
|---|---:|---:|
| **EQUIPMENT_OR_PRODUCT** | 46 | **1,310** ← the largest category in the market |
| GENERIC_CORE (mixed intent) | 18 | 1,120 |
| **BOFU_SERVICE** | 49 | **800** |
| NOT_CORE_SERVICE | 15 | 210 |
| OUT_OF_SCOPE_SERVICE | 2 | 20 |

**The single most important number in this audit: ~800 bottom-of-funnel exterior-washing
searches per month across the entire eight-city footprint — about 26 per day, all 24 hours
combined.**

The largest untapped volume in this market is **equipment and product shopping** — people
buying pressure washers, not hiring one. It is worthless to this client and is correctly
blocked by the existing negatives.

### Top BOFU buckets

| Local searches/mo | Competition | Top-of-page bid | Representative | Covered? |
|---:|---|---|---|---|
| 110 | HIGH | $10.89–$28.23 | power washing near me | ✓ live |
| 70 | LOW | $11.40–$26.35 | power washing services | ✓ live |
| **70** | **HIGH** | **$8.75–$24.53** | **pressure washing near me** | **✗ NOT COVERED** |
| **40** | MEDIUM | **$10.46–$32.09** | **house washing near me** | **✗ PAUSED IN BOTH CAMPAIGNS** |
| **40** | HIGH | $5.05–$15.18 | **paver cleaning** | **✗ NOT COVERED** |
| 20 | HIGH | $8.50–$30.12 | power wash home | ✓ via close variant |
| 20 | MEDIUM | $10.95–$21.73 | power washing company | ✓ live |

**Bid evidence: volume-weighted top-of-page $8.66 low – $23.91 high.** The account pays
**$28.53**.

### Seasonality — the window is closing

Combined monthly volume, top six BOFU buckets, this exact geo:

| Aug 25 | Sep 25 | Oct 25 | Nov 25 | Dec 25 | Jan 26 | Feb 26 | Mar 26 | **Apr 26** | May 26 | Jun 26 | Jul 26 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 340 | **200** | 150 | 100 | 360 | 350 | 100 | 330 | **740** | 570 | 420 | 610 |

Peak is April–July. **September 2025 came in 41% below August 2025**, falling further
through October and November.

**Two conclusions.** First, late August is one of the last strong weeks of the year for this
service — an argument for fixing the constraints *this week*. Second, deferring the unspent
budget into September means spending it into a market roughly 41% smaller. Neither changes
the fact that the August demand simply is not there.

---

## 27. Metric advantages — ranked by business importance

1. **Conversion architecture is correctly designed and campaign-isolated.** Three distinct
   lead actions, one per real outcome, `ONE_PER_CLICK`, 60-second qualified-call threshold,
   and campaign-specific goals whose biddable set is exactly the three lead categories. Most
   new accounts get this wrong. *Leverage: the moment leads start arriving, they will be
   measured correctly.*
2. **Full policy compliance on every delivery switch.** Search Partners OFF, Display OFF,
   AI Max OFF, auto text assets OPTED_OUT, Final URL expansion OPTED_OUT, no DSA, Phrase +
   Exact only, no Broad, PRESENCE targeting, no country sweep-exclusion. *Leverage: nothing
   has to be undone before scaling; the foundation is clean.*
3. **Zero wasted geography.** `targeting_location: true` on every delivery row. Not one
   impression served outside the intended footprint. *Leverage: every dollar reached the
   right market.*
4. **Landing pages are genuinely good.** Six purpose-built pages, HTTP 200, no redirects,
   strong H1 and city match, 4-field forms, approved tracked phone, verified mobile parity,
   and **gclid/UTM preservation confirmed end-to-end**. *Leverage: the attribution chain is
   sound; only three content defects stand between this and a strong conversion path.*
5. **Top-of-page presence is excellent when the ads do run.** 87.1% and 100% top impression
   percentage; campaign 2 at 100% absolute top. *Leverage: visibility is not the problem —
   the account owns the top of the page whenever it enters an auction.*
6. **Rank loss is solved.** From 90% lost IS (rank) on 08-04 to **0% by 08-24 at 100%
   impression share.** *Leverage: the auction is winnable; the remaining work is demand and
   cost, both of which are addressable.*
7. **A clean, approved creative and keyword inventory sits ready.** 54 RSAs and 214 keyword
   rows, **100% approved, zero policy issues, zero character violations**, plus 72 in-scope
   BOFU keyword texts already built in paused ad groups. *Leverage: expansion is largely an
   unpause, not a build — the fastest possible route to more qualified demand.*
8. **Mobile engagement is healthy.** 73% of impressions, 1.8× desktop CTR, no rendering
   defect. *Leverage: the dominant channel is working.*

---

## 28. Metric problems — ranked P0 to P3

| # | Priority | Problem | Evidence | Impact | Root cause | Confidence | Action | Approval? |
|---|---|---|---|---|---|---|---|---|
| 1 | **P0** | Ad schedule dark 64% of the week, cut off at the peak hour | 60/168 hrs; Sunday 0 impressions all-time; **17:00 = 23 impr, 21.5% of all delivery**, then dark | Largest single suppressor of qualified impressions | Sunday daypart deleted 2026-08-07 16:17:45; 18:00 cutoff | **HIGH** | Open to 24/7; constrain call asset separately | YES |
| 2 | **P0** | No CPC ceiling → $28.53 avg CPC | Local top-of-page $8.66–$23.91; one click **$54.49**; ceiling removed 2026-08-16 23:42 | Burning ~40% of every click | Uncapped Maximize Clicks in a thin pool | **HIGH** | Max CPC $22.00 | YES |
| 3 | **P0** | Conversion tracking unverified | 0 conversions; no label observable at page load; 6 clicks | Blocks all bidding and optimisation decisions | Never fired; sample far too small to judge | **HIGH** (that it is unverified) | GTM preview, then approved end-to-end test | YES |
| 4 | **P1** | Second Google Ads tag `AW-17878095007` on every page | Rendered DOM + network requests, all 6 pages | Data leakage; attribution corruption | Unknown third-party tag | **HIGH** | Identify owner, then decide | YES |
| 5 | **P1** | Two campaigns splitting one small market | `24103511039` + `24145053510`, identical settings; `Power Washing Services Near Me` enabled in **both** | Fragmented budget, learning and reporting | Campaign 2 created 2026-08-18 | **HIGH** | Pause duplicate now; consolidate in September | YES |
| 6 | **P1** | `House Washing Company Near Me` paused in **both** campaigns | 40 searches/mo at $10.46–$32.09 unserved | Unserved in-scope BOFU demand | Revamp oversight | **HIGH** | Unpause — status change only | YES (enable) |
| 7 | **P1** | Pressure-washing demand misrouted | 15 impr, **0 clicks, 0% CTR**; 11 of 15 served by a power-washing ad group | Lost clicks on the second-largest term family | No `pressure washing` head keyword | **HIGH** | New SKAGs A–C | YES |
| 8 | **P1** | Sitelinks send paid traffic to untracked pages | SITELINKS 1 click **$40.07 = 23% of all spend**; destination shows (631) 502-5402 | Calls invisible to Ads and WhatConverts | Sitelinks point to main site | **HIGH** | Repoint to offer subdomain | YES |
| 9 | **P1** | Authoring instruction published in live copy | "…without making the page about unrelated services" on the $108.99 page | Credibility damage on 64% of spend | Content never cleaned | **HIGH** | Delete the clause | YES |
| 10 | **P1** | Evergreen countdown, no offer | "Offer Ends in 06 DAY 02 HRS 55 MIN" on all 6 pages, same value seconds apart | Misleading-urgency and FTC risk | Rolling per-visitor timer | **MEDIUM-HIGH** | Remove or attach a real dated offer | YES |
| 11 | **P2** | Quality Score 1 on the account's best keyword | Both rows `AD_GROUP_CRITERION_LOW_QUALITY`, Below Average ×3 | Suppresses the highest-intent term | No pinning; generic headline pool | **MEDIUM** | RSA rewrite with pinned H1 | YES |
| 12 | **P2** | 87.88% invalid click rate, campaign 1 | 29 invalid vs 4 valid; 30 of 36 attempts filtered | Distorts every rate; suggests self-clicking or bots | Probably self-clicking; ClickCease installed | **MEDIUM** | Stop clicking live ads; cross-check ClickCease | NO |
| 13 | **P2** | Every lead valued $0.00 | `always_use_default_value: true`, `default_value: 0.0` ×3 | ROAS and profit reporting impossible | Never configured | **HIGH** | Set values once client economics are known | YES + client fact |
| 14 | **P2** | `Local actions - Directions` is `primary_for_goal` | Account level, `MANY_PER_CLICK` | Contained now; hazard for future campaigns | Google default | **HIGH** | Demote to secondary | YES |
| 15 | **P2** | Only 4 callouts | SOP minimum 8 | Reduced ad real estate on a mobile-first account | Under-built | **HIGH** | Add 4–8 verified callouts | YES |
| 16 | **P2** | RSA pairs too similar | Driveway **73%** shared headlines; Soft House 53%; Power Washing Near Me 47% | Second RSA is not a real test | Built from one template | **HIGH** | Diversify on next rewrite | YES |
| 17 | **P3** | City SKAGs never served | `[power washing islip]`, `[power washing dix hills]` — **0 impressions, 22 and 7 days** | Dead weight | Exact match on hamlets of ~18k and ~26k | **HIGH** | Keep for now; revisit if still zero in September | NO |
| 18 | **P3** | `how to` as a BROAD negative | Blocks any query containing "how" + "to", incl. "how much does it cost **to** power wash a house" | Small false-negative risk | Over-broad negative | **MEDIUM** | Narrow to PHRASE | YES |
| 19 | **P3** | Business logo `PENDING` | `primary_status: PENDING` | Reduced ad real estate | Awaiting review | **HIGH** | Monitor | NO |
| 20 | **P3** | Enhanced conversions for leads disabled | account setting | Weaker lead attribution | Never enabled | **HIGH** | Enable after tracking is verified | YES |
| 21 | **P3** | Review gating on `/reviews/` | HAPPY / NEUTRAL / POOR selector; sitelink destination | Violates agency policy and Google review policy | Client site widget | **HIGH** | Raise with client | Client decision |
| 22 | **P3** | Ad-group CPC bids all $0.01 | every ad group | Latent trap if bidding ever switches to Manual CPC | Editor default | **HIGH** | Set sane defaults when bidding changes | YES |

---

## 29. Lead-goal feasibility — at least one qualified lead by 2026-08-31

**No lead is guaranteed, and none will be promised here.**

The account has produced **6 clicks and 0 leads** in its lifetime. There is no observed
conversion rate. The scenarios below use transparent industry-range assumptions, clearly
labelled, for a local exterior-service landing page with a 4-field form and click-to-call.

| Case | Assumed CVR | Basis | Clicks Aug 26–31 | Expected leads | P(≥1 lead) |
|---|---:|---|---:|---:|---:|
| **LOW** | 3% | Poor message match, unverified tracking, cost-research traffic | 8.6 | **0.26** | **~23%** |
| **BASE** | 7% | Typical local home-service LP with form + click-to-call | 23.0 | **1.61** | **~81%** |
| **HIGH** | 12% | Strong intent, top-of-page, repaired copy | 28.7 | **3.44** | **~97%** |

*LOW uses Scenario A1 (no change): 1.43 clicks/day × 6. BASE uses Scenario B: 3.83/day × 6.
HIGH uses Scenario C: 4.78/day × 6. P(≥1) = 1 − (1 − CVR)^clicks.*

**Confidence: LOW.** Every conversion-rate figure is an industry assumption, not this
account's data. The honest summary: **doing nothing gives roughly a one-in-four chance;
executing the recommended fixes gives roughly four-in-five (81%).**

There is a harder caveat. **If conversion tracking has never fired, a lead could arrive and
never be recorded** — the client would see it as a phone call or an email, not as a
conversion. That is precisely why P0-3 outranks every traffic change.

### Fastest defensible path to one qualified lead — ranked

1. **Verify the tags fire** (P0-3). A lead you cannot see is a lead you cannot count.
   *Same-day, needs test approval.*
2. **Open the schedule to evenings and Sunday** (P1-1). Largest single source of additional
   qualified impressions. **+50% reach, immediate.** Includes Sunday Aug 30, currently dark.
3. **Cap CPC at $22.00** (P0-4). Converts the same budget into **more clicks** — roughly
   1.4/day at $28.53 becomes ~2.5/day at $16–18 for the same money.
4. **Unpause `House Washing Company Near Me`** (P1-2). Zero build, 40 monthly searches at
   $10.46–$32.09, already approved.
5. **Fix the two landing-page defects** (P0-1, LP-2). Removing the published authoring
   instruction and the fake countdown from the page carrying 64% of spend is free and
   immediate.
6. **Repoint sitelinks to the offer subdomain** (P2-2). Stops the next $40 click landing on
   an untracked page.

Items 2, 3, 4 and 6 are Google Ads changes that could be executed in a single approved
package. Items 1 and 5 need client-side access.

---

## 30. Spend-goal feasibility

Answered in full in §9 and `2026-08-25-pacing-analysis.md`.

**$2,500 IS NOT A DEFENSIBLE QUALIFIED-SEARCH SPEND TARGET FOR THE REMAINING PERIOD.**

Highest defensible month-end spend: **$638.49**. Shortfall **$1,861.51 (74.5%)**. The goal
requires 238 qualified impressions per day; the maximum defensible plan produces 47.8 — the
campaign can reach **20% of the demand the goal requires**.

And the uncomfortable corollary, stated plainly: **the single most valuable technical fix —
capping CPC — will reduce August spend.** Scenario A2 spends $310.93 against Scenario A1's
$415.93. Buying the same clicks for less money is right for the client and wrong for the
spend number. Where those two conflict, this audit recommends the client's interest.

---

## 31. Expansion opportunities

Full table: **`2026-08-25-keyword-opportunities.csv`**. Drafted plan:
**`2026-08-25-draft-expansion-plan.md`**.

**ADD-NOW candidates** (still DRAFT — nothing added):
`pressure washing near me` (70/mo, $8.75–$24.53) · `pressure washing services near me`
(110/mo bucket, $10.89–$28.23) · **unpause `house washing company near me`** (40/mo,
$10.46–$32.09, already built and approved).

**TEST candidates:** `pressure washing company near me` (LOW competition) ·
`paver cleaning near me` (40 + 20/mo — cleaning only; **paver sealing is out of scope**) ·
`concrete pressure washing near me` · `soft washing near me`.

**REJECTED with reasons:** the generic `power washing` (480/mo) and `pressure washing`
(260/mo) head buckets — their low top-of-page bids collapse to $0.57 and $0.30, they group
with "power pressure washer", and in this account `power washing` produced **14 impressions
and 0 clicks**. Also rejected: `power washing cost` ($0.31 low bid = research intent), and
every equipment, rental and retail term.

---

## 32. Prioritized action ladder

Consolidated in `2026-08-25-draft-expansion-plan.md` with why / evidence / expected effect /
risk / approval for every item.

- **P0 — fix before buying more traffic:** verify tags · Max CPC $22.00 · remove the
  published authoring instruction · identify `AW-17878095007`
- **P1 — unlock qualified demand:** 24/7 schedule · unpause House Washing Company Near Me ·
  pause the duplicate ad group · 3 out-of-scope negatives · 2–4 new Pressure Washing SKAGs
- **P2 — improve CTR and Ad Rank:** RSA rewrite with pinned H1 on the QS 1 ad group ·
  repoint sitelinks · add 4–8 callouts
- **P3 — improve CVR:** remove or legitimise the countdown · re-map the estimate ad group's
  intent · keep everything mobile-first
- **P4 — future bidding and scale:** stay on Maximize Clicks; revisit Smart Bidding at ≥15
  verified conversions in 30 days; offline outcomes via Data Manager API

---

## 33. DRAFT change plan

**`2026-08-25-draft-expansion-plan.md`** — including two fully drafted, character-validated
replacement RSAs for the QS 1 ad group and a **~55–60 mutation inventory**.
**Nothing has been implemented.**

---

## 34. Missing information and confidence

### Client facts marked UNKNOWN — not invented anywhere in this audit

Verified service area · after-hours call answering and callback commitment · average job
revenue · gross margin · close rate · target CPL / CPQL / CAC · CRM in use · whether
WhatConverts is the system of record · owner of Google Ads account `17878095007` · whether
the countdown reflects a real offer.

### Data unavailable from the Google Ads API — stated, never estimated

- Keyword-level and ad-group-level **lost IS (budget)** — not selectable from `keyword_view`
  or `ad_group` in v25.
- **Keyword position estimates** — returned null on all 214 rows; Keyword Planner
  top-of-page estimates used instead.
- **Auction Insights** — not exposed via the API. No competitor named.
- **Page speed metrics** — not measured; would need PageSpeed Insights.
- **Whether conversion tags actually fire** — requires an approved end-to-end test.

### Confidence by finding class

| Class | Confidence | Why |
|---|---|---|
| **Structural findings** (two campaigns, duplicate ad group, paused SKAG, schedule, no CPC cap, sitelink destinations, second tag, landing-page defects) | **HIGH** | Read directly from the API and a real browser. Independent of sample size. |
| **Market-demand findings** (800 BOFU searches/mo, $8.66–$23.91 bid range, seasonality, coverage gaps) | **MEDIUM-HIGH** | Keyword Planner for the exact geo, buckets collapsed. Small-geo averages are coarse and round to 10. Cross-validated against observed 100% impression share. |
| **Data-proven findings** (0 conversions, 6 clicks, $171.17, 100% IS, Sunday zero, hour curve, 15 pressure-phrasing impressions at 0% CTR, 87.88% invalid rate) | **HIGH as facts, LOW as trends** | The numbers are exact. The samples are tiny. |
| **Hypotheses to test** (CTR reaches 10% after RSA repair; QS recovers from 1; evenings deliver ~+50%; CVR lands near 7%) | **LOW** | Industry-range assumptions, explicitly labelled. |

**The central caution:** this account has **6 clicks and 0 conversions**. Almost nothing
here is statistically significant, and this audit does not pretend otherwise. The
conclusions rest on **configuration, impression share, market demand and bid evidence** —
all of which are reliable at any volume — not on performance trends, which are not.

---

## 35. Short executive report

See **`2026-08-25-power-washing-executive-report.md`**.

---

## Final safety check

| Check | Result |
|---|---|
| Google Ads mutations | **ZERO** |
| Budget changes | **ZERO** |
| Keywords added | **ZERO** |
| Negatives added | **ZERO** |
| Ads added or changed | **ZERO** |
| Resources paused | **ZERO** |
| Resources enabled | **ZERO** |
| Final URLs changed | **ZERO** |
| Conversion actions changed | **ZERO** |
| Forms submitted | **ZERO** |
| Test calls placed | **ZERO** |
| Google recommendations applied | **ZERO** |

Every Google Ads call in this audit was `GoogleAdsService.Search` (GAQL `SELECT`) or
`KeywordPlanIdeaService.GenerateKeywordIdeas`, which returns ideas without creating a plan
resource. No mutate service was constructed or called. All web access was GET navigation.

**READ-ONLY AUDIT COMPLETE — NO EXTERNAL CHANGES MADE**
