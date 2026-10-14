# PLAN-R3A — CONTROL INTEGRITY REVIEW

**Generated:** 2026-08-31 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
**Question:** is campaign `24145053510` a valid independent control for a $12 ceiling test on
campaign `24103511039`?

**Answer: NO.** PLAN-R3A `B57E427D07C5` must be revised before it can be approved.

Identity gate re-run fresh — `Softwind Power Washing - Live` / `1521725229` / manager `false` /
test `false` / ENABLED — **PASS**.

---

## 1. The mechanism Walter identified is real, and the account has already demonstrated it

Only one ad from an account enters a given auction. When two campaigns both hold an eligible
keyword for the same query, Google selects one — and **Ad Rank (bid × Quality Score) is a major
input to that selection.**

PLAN-R3A would set campaign A to $12.00 while campaign B stays at $30.00. For every query where
both campaigns are eligible, **B's maximum bid becomes 2.5× A's.** All else equal, B wins the
internal selection more often than it does today.

**This is not theoretical here. It is already happening at equal bids.**

### Five search terms have served in BOTH campaigns

| Search term | Impr | Clicks | Spend | Matched keywords |
|---|---:|---:|---:|---|
| `power wash near me` | 11 | 2 | **$56.38** | `residential pressure washing near me` (B) |
| `pressure washing near me` | 14 | 1 | **$29.57** | `residential pressure washing near me` (B) |
| `power washing services` | 5 | 1 | **$29.32** | `power washing services near me` · `residential pressure washing near me` |
| `house washing near me` | 4 | 0 | $0.00 | `power washing services near me` · `residential pressure washing near me` |
| `power washing services near me` | 3 | 0 | $0.00 | `power washing services near me` (both) |

**Four of those five were absorbed by a single campaign-B keyword:
`residential pressure washing near me`.** That keyword is a close-variant magnet already
competing for campaign A's core query space — `power wash near me` and `pressure washing near
me` are campaign A intents by any reading, and B took them at an equal bid.

### Google's close variants in this account are very loose

Proven from the account's own data, not assumed:

| Search term | Matched keyword | Match |
|---|---|---|
| `power washing services` | `residential pressure washing near me` | NEAR_EXACT |
| `powerwash cost` | `house pressure washing estimate` | NEAR_EXACT |
| `deck cleaning services near me` | `power washing services near me` | NEAR_PHRASE |

`power washing services` → `residential pressure washing near me` shares **one token in five**.
Google matched it anyway. Any conservative simulation of eligibility will therefore
**understate** overlap, and mine does.

---

## 2. Overlap analysis

Full term-by-term table in `snapshots/control-integrity-2026-08-31T*.json` — 55 distinct search
terms, every one with impressions or clicks, each carrying matched campaign, ad group, keyword,
match type, both campaigns' eligibility with evidence, both ceilings, landing pages, and a
shift verdict.

### Classification

| Class | Terms |
|---|---:|
| **BOTH CAMPAIGNS ELIGIBLE** (served in both — proven) | **5** |
| CAMPAIGN A ONLY | 28 |
| CAMPAIGN B ONLY | 10 |
| INCONCLUSIVE | 12 |

### Overlap percentages — stated as a range, because a point estimate would be false precision

| | Impressions | Valid clicks | Spend |
|---|---:|---:|---:|
| **Proven floor** — served in both campaigns | **16.7%** (37/221) | **26.7%** (4/15) | **24.8%** ($115.27/$465.27) |
| **Plausible ceiling** — washing-themed terms B's serving set could close-variant match | **96.8%** | **100%** | **100%** |

The floor is what the account has **already demonstrated**. The ceiling is what Google's
demonstrated close-variant looseness makes reachable. **The truth lies between — and both bounds
are high enough to break the control design.** A quarter of spend in *proven* shared space is
already disqualifying; the ceiling says it could be nearly all of it.

### Why the "CAMPAIGN A ONLY" bucket is not reassuring

Those 28 terms are classified A-only because no *serving* campaign-B keyword plausibly matched
them under a conservative test. But that same conservative test would have said
`power washing services` could not match `residential pressure washing near me` — and it did.
**"CAMPAIGN A ONLY" here means "not yet observed in B", not "cannot occur in B".**

### Structural overlap, for completeness

| | Campaign A | Campaign B |
|---|---|---|
| Serving keyword rows | 9 | 12 |
| Distinct serving texts | 6 | 6 |
| **Texts serving in both** | **1** — `power washing services near me` | |
| **Landing pages** | 8 | 8 — **all 8 shared, 100%** |
| Ad-group names | 15 | the same 15 |
| Keyword rows total | 107 | the same 107 |
| Geography | 80 targets + CT exclusion, PRESENCE | identical |

The serving keyword *texts* are mostly distinct (5 A-only, 5 B-only, 1 shared) — which is why
the proven floor is 16.7% rather than 90%. But **every landing page is shared**, ad-group
relevance is near-identical by construction, and the close-variant behaviour above shows the
distinct texts do not keep the query spaces apart.

---

## 3. Is campaign B a valid independent control?

# NO.

**Campaign B can absorb campaign A's search traffic, so campaign A's post-change decline could
not be attributed solely to the $12 ceiling.**

Four specific reasons:

1. **The confound is bidirectional and unmeasurable.** After the change, A's impression and
   click decline is a mixture of (a) external auctions genuinely lost at $12 and (b) internal
   auctions ceded to B's 2.5× bid. **Nothing in Google Ads reporting separates those two.**
   There is no "lost to my own other campaign" metric.

2. **A control that changes is not a control.** B is unchanged in *configuration* but would not
   be unchanged in *outcome* — it would gain the traffic A gives up. Its impressions, clicks,
   CPC, impression share and lost-IS-to-rank would all move as a direct consequence of the
   intervention. **"Campaign B was unchanged" is a statement about settings, not about validity.**

3. **The stop conditions would fire for the wrong reason — and this is the most expensive
   failure.** STOP-1 (fewer than 8 impressions/day for 3 days), STOP-2 (lost IS to rank above
   65%) and STOP-3 (six serving days with impressions but zero clicks) all read campaign A in
   isolation. If B cannibalises A, every one of them can trip on cannibalisation rather than on
   the ceiling. The test would roll back, and **$12 would be recorded as "proven too low" when
   it had never actually been tested.** A false negative here poisons a correct hypothesis and
   pushes the account back toward $30 with false confidence.

4. **The account-level result could be null even if $12 works.** If B keeps taking the
   contested queries at $30, blended account CPC barely moves and $12 looks ineffective — again
   without having been tested.

**Verdict: NO — not PARTIALLY VALID.** With 26.7% of valid clicks and 24.8% of spend in
*proven* shared space, and a plausible ceiling near 100%, there is no threshold at which this
design yields an attributable result.

---

## 4. The three test designs compared

| | **OPTION A** — $12 on both campaigns, pre/post | **OPTION B** — Google Ads experiment | **OPTION C** — $12 on A after query ownership is separated |
|---|---|---|---|
| **Required changes** | Lower ceiling on both campaigns | Create campaign draft + experiment with traffic split on A | Execute R6 (create paused) → R10 (enable) → R11 (pause B), then the $12 change |
| **Mutation count** | **2** (one field each) | Several: 1 draft + 1 experiment + arms; then teardown | 14 + 11 + 11 + 1 = **37 across four approvals** |
| **Expected test validity** | **MEDIUM-GOOD.** No internal Ad Rank asymmetry — both campaigns move together, so the A-vs-B internal selection stays as it is today. Confounded only by time (seasonality, day-of-week, the 08-30 negatives still bedding in) | **HIGHEST in principle** — randomised split is the correct instrument. **But see the two disqualifiers below** | **HIGHEST in practice** — one campaign, no overlap, clean pre/post |
| **Risk of delivery loss** | **MEDIUM-HIGH** — both campaigns exposed at once, no fallback arm | LOW — only the trial arm's share is exposed | LOW at the ceiling step; MEDIUM across the consolidation programme |
| **Risk of continued $30 clicks** | **Eliminated** | Persists on the control arm **and entirely on campaign B**, which is not in the experiment | **Persists for weeks** while consolidation runs |
| **Time to a useful sample** | ~150 impressions in **~6 serving days**; 8 valid clicks in **~8–10 serving days** at the current ~1 click/day | **Months.** A 50/50 split halves an already ~1 click/day rate to ~0.5/arm/day; 8 clicks per arm is ~16 serving days *per arm* before any significance test | **3–5 weeks** before the ceiling test even starts |
| **Is current traffic volume sufficient?** | **Marginal — but the best of the three** | **NO. This is the disqualifier.** 18 valid clicks in the account's entire life | Yes, once consolidated — A would hold all the volume |
| **Rollback** | 2 mutations, one field each, back to `30000000` | Remove experiment and draft; more surface to unwind | 1 mutation for the ceiling; the consolidation steps have their own rollbacks |

### Option B — the two conditions it fails

Walter's own preconditions decide it:

- **"The account has enough traffic for a meaningful experiment." — FAILS.** 18 valid billable
  clicks lifetime, ~1 per serving day. Splitting that in two produces arms that cannot separate
  from noise in any reasonable window.
- **"The duplicate second campaign will not contaminate the experiment." — FAILS.** An
  experiment splits traffic *within campaign A*. **Campaign B is outside the experiment
  entirely** and would keep absorbing shared queries from both the control and trial arms at
  $30. The experiment would isolate A-control from A-trial while leaving the actual confound
  untouched.
- *No existing experiment conflicts* — **PASSES.** Verified: `experiment`, `experiment_arm` and
  `campaign_draft` all return **zero rows**.
- *Can test only the CPC ceiling* — **PASSES** technically.

Two of four fail, and both failures are fundamental rather than fixable.

### Recommended: **OPTION A**

**Apply $12.00 to both campaigns and evaluate the account pre-versus-post.**

The reasoning is the inverse of the flaw Walter found: **the problem with PLAN-R3A is the
*asymmetry*, not the change.** Moving both campaigns to the same ceiling removes the asymmetry
entirely — the internal A-vs-B selection stays in the same relative position it occupies today,
so shared-query traffic does not systematically shift. What is lost is a concurrent control;
what is gained is an attributable account-level read.

**Its honest weakness, stated plainly:** a pre/post test has no concurrent control, so
seasonality and day-of-week confound it. Two mitigations, neither perfect: compare
**serving-day to serving-day** rather than calendar days, and note that **local demand history
shows September running roughly 41% below August** — so a post-period decline of that order is
expected from seasonality alone and must not be read as a ceiling effect.

**Option C is the better science and should still happen** — it is PLAN-R4 → R6 → R10 → R11,
already drafted. But it is 37 mutations across four approvals and 3–5 weeks, during which the
account keeps paying ~$29 per click for traffic that has produced zero recorded leads.
**Option A now, Option C's clean measurement later, is the right sequence.**

---

## 5. Measurement correction

**Superseding the earlier statement that no WhatConverts export exists.**

> **USER-SUPPLIED WHATCONVERTS RECORDS REVIEWED — ZERO CONFIRMED RELEVANT LEADS IN THE SUPPLIED
> ROWS**

Walter supplied WhatConverts lead records for review. Under the agreed filtering rules — a lead
counts as relevant when it requests Power Washing or Pressure Washing-related service regardless
of source, **or** it arrived on one of the approved Power Washing tracking numbers — the supplied
records contained **zero confirmed Power Washing or Pressure Washing leads**.

No customer PII from those records appears in this or any other report.

**The separate Google Ads measurement finding is preserved and unchanged:**

- All four conversion actions carry `include_in_conversions_metric: FALSE`, because
  `customer_conversion_goal` returns `biddable: FALSE` for all four categories.
- `metrics.conversions` is structurally incapable of counting a lead;
  `metrics.all_conversions` is also 0.00 on every campaign and every date.
- **Google Ads conversion measurement is therefore still not configured to support a reliable
  CPL or conversion-rate judgement**, independently of what the WhatConverts records show.

**The two findings now converge rather than conflict.** Previously the zero could not be
interpreted, because no independent source existed. Now there is one, and it also reads zero.
That materially strengthens the read: **the account is most likely genuinely not producing
qualified leads, rather than producing them invisibly.** It does not remove the need to fix the
conversion configuration — without it, a lead that *does* arrive still cannot be counted, and
the $12 test still cannot be judged on CPL.

---

## 6. Effect on PLAN-R3A

**PLAN-R3A `B57E427D07C5` is NOT approval-ready. It must be revised.**

What is **still sound** and should carry into the revision:

- **$12.00 is the right number.** Nothing in this review touches the pricing evidence: $10
  clears ~15.8% of measured local demand, $12 clears ~98.2%, $18 and $22 add almost nothing over
  $12.
- The six stop conditions, the 10-serving-day window, the 150-impression / 8-click thresholds,
  the invalid-click exclusion rule, and the rollback to `30000000` are all sound and transfer
  unchanged.
- The measurement dependency is unchanged and now better evidenced.

What is **broken**:

- The single-campaign design and the claim that campaign B is a valid control.
- Consequently the action count: **1 mutation → 2**, and the field mask applies to both
  campaigns.
- STOP-1, STOP-2 and STOP-3 must be re-scoped from campaign A alone to the **account**, since
  there is no longer a control campaign to compare against and cannibalisation is no longer the
  confound.

**No new fingerprint has been created.** As instructed, the revision waits for Walter's
decision. `B57E427D07C5` has been marked **BLOCKED — CONTROL DESIGN INVALID** in the plan file
and now emits **no approval command** from the manifest. That change does not alter its
fingerprint, because the canonical payload covers target identity and the action list only —
the plan's actions have not been edited.

---

**CONTROL INTEGRITY REVIEW COMPLETE — ZERO EXTERNAL CHANGES MADE**
