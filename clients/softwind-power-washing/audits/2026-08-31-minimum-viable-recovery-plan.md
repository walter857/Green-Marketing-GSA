# SOFTWIND POWER WASHING — SAME-DAY MINIMUM VIABLE RECOVERY PLAN

**Generated:** 2026-08-31 America/New_York · Account `1521725229` · **NOT APPROVED**

This is deliberately small. **Ten mutations across two plans.** It is not the rebuild — the
rebuild is PLAN-R4 through R11 and it should not be the first action in an account that has
taken 22 clicks in its life.

---

> **CONTINUATION RESTATEMENT — 2026-08-31 16:40.** A drift check at 16:40 found Google had
> retroactively invalidated **four of the five clicks** recorded that morning on
> `power washing services`, crediting back **$117.28**. The account ledger moved from
> **22 billable clicks / $713.15** to **18 billable clicks / $595.87**; invalid clicks rose
> 60 → 73, i.e. **80.2% of all raw clicks**. Every other day is byte-identical, conversions
> remain **0**, and no conclusion below changes — the traffic-quality finding is now confirmed
> by Google's own filtering.

---

## The five questions this plan answers

### 1. What must be fixed before another dollar is spent?

**The price per click.** Since the $30.00 ceiling went in on 2026-08-27, **every one of the
five billable clicks priced between $29.04 and $29.72** — a range **$0.68 wide** sitting
directly beneath the cap. Under a $5.00 ceiling the
account took zero clicks in twelve days; uncapped it paid $54.49 and $82.22. **The price tracks
the cap in all three regimes. It does not track the market** — local top-of-page LOW for the
serving keyword set is $8.75–$13.49.

Nothing else in the account moves money as fast, as reversibly, or with as little risk.

### 2. What can reduce bad CPC immediately?

**PLAN-R3 — cut the ceiling from $30.00 to $22.00 on both campaigns.** Two mutations, one
field (`target_spend.cpc_bid_ceiling_micros`), one-write rollback.

Applied to the 22 clicks the account has actually bought:

| | Observed (corrected 16:40) | At a $22.00 ceiling |
|---|---:|---:|
| Spend | $595.87 | **$379.71** |
| Average CPC | $33.10 | **$21.10** |
| Clicks for the same money | 18 | **28.2** |
| Saving | — | **$216.16** |

For comparison, at other ceilings: $24 → $22.77 CPC and 26.2 clicks · $20 → $19.21 and 31.0 ·
$18 → $17.32 and 34.4. **$22.00 is chosen because it sits above every top-of-page LOW in the
serving keyword set ($8.75–$13.49), so eligibility survives on every core keyword, while
sitting below the HIGH ($23.34–$32.86), so what is given up is absolute-top position** — and
with 31–46% absolute-top share, Quality Score 1–5 and zero recorded conversions, absolute-top
is not worth a premium.

### 3. What can improve CTR immediately?

**Honestly: nothing can, immediately.** CTR is downstream of ad relevance and Quality Score,
and both take weeks to move. What can be *started* today is **PLAN-R5** — two rewritten RSAs
for `Power Washing Near Me`, the only ad group where Google reports ad relevance
BELOW_AVERAGE, carrying 40.4% of all spend. They are created **paused** and enable only after
readback QA, so they change nothing today.

The one genuine same-day CTR lever is **PLAN-R8's missing sitelink** (below), because Google
generally needs four sitelinks to render the full extension.

### 4. Which ad groups should own traffic?

Today, exactly three — and they already exist in campaign A:

| Ad group | ID | Lifetime |
|---|---|---|
| Power Washing Near Me | `202870585390` | 81 impr / 7 clicks / $288.07 |
| Power Washing Services Near Me | `202870585430` | 94 impr / 4 clicks / $109.31 |
| Power Washing Company Near Me | `202870585590` | 11 impr / 0 clicks / $0.00 |

**No ad group is paused in this minimum plan.** Pausing before a replacement is proven means
losing coverage the account currently has. That is PLAN-R11, and it is blocked behind PLAN-R10.

### 5. Which keywords should remain active?

**All 214.** Every one is ENABLED, APPROVED, ELIGIBLE and in scope, with zero Broad match.
**The waste is in routing and price, not in the keyword list.** Nothing is stopped today.

### Which landing pages must be corrected?

`/power-washing-services-islip-west-islip-dix-hills/` carries **13 clicks and $432.13 — 60.6%
of all account spend.** It needs three fixes, all in **PLAN-R7** (website only, zero Ads
mutations, and it needs the site owner's separate approval):

1. Browser title reads **"Power Washing | Softwind Landscape & Masonry"** — the *sibling*
   company's brand, on the page a power-washing searcher lands on.
2. H1 is locked to **"Islip, West Islip & Dix Hills, NY"** while the campaigns have targeted
   **80 places across Nassau and Suffolk since 2026-08-26**.
3. An **"Offer Ends" countdown** runs with no dated offer behind it.

### Which negatives are clearly safe?

**Three additions, all collision-tested against every one of the 55 distinct live keyword texts
with zero collisions:**

- `roof cleaning` PHRASE — roof cleaning is on the work order's `excluded_services`
- `house cleaning services` PHRASE — interior cleaning (deliberately *not* bare "house
  cleaning", which would also block `outdoor house cleaning services near me`)
- `power washing repair` PHRASE — pressure-washer servicing, and the existing BROAD
  `power washer repair` does not catch it because BROAD requires every word and the term says
  "washing", not "washer"

**And one removal, which is the more important half.** On 2026-08-30 the portfolio negative
rollout added a bare PHRASE negative on the single word **`cleaning`**. It now blocks
`deck cleaning services near me` (which took a $29.04 click the day before),
`outdoor house cleaning services near me`, and **four of the account's own live keywords**:
`concrete cleaning service`, `driveway cleaning service`, `outdoor surface cleaning service`,
`patio cleaning service`.

**The adds must execute and read back before the removes**, so there is never a window in which
roof or interior-cleaning queries are unblocked.

### Which assets are missing?

**Campaign A has only three sitelinks; campaign B has four.** PLAN-H created four assets and
eight campaign links on 2026-08-27; today there are seven. The missing one is `413928453094`
"Free Quote" — already APPROVED, already live on campaign B. Campaign A carries 202 of 246
impressions, and **sitelinks account for 5 clicks and $158.59 — 22.2% of all spend.**
*(PLAN-R8, 1 mutation.)*

### Which conversions must be tested?

**All three lead actions — and the test is blocked, for a reason that is not going away.**

Both campaigns use `PRESENCE` targeting on 80 New York locations. A real GCLID requires a click
on a real ad by a person **physically on Long Island** during Mon–Sat 08:00–18:00. Neither the
agent nor a Florida-based approver can produce one, so the GCLID-to-conversion join cannot be
proven remotely.

What **can** be done today, with zero mutations:

- **Fix the conversion-counting configuration.** All four conversion actions carry
  `include_in_conversions_metric: FALSE` because `customer_conversion_goal` returns
  `biddable: FALSE` for all four categories. **The Conversions column is structurally
  incapable of counting a lead.** *(Bidding is unaffected — campaign-level goals override.)*
- **Get the WhatConverts export.** None exists in this repository. Without it "zero leads"
  cannot be confirmed or refuted.
- **Resolve the foreign tag `AW-17878095007`**, live on all six offer pages since at least
  2026-08-25, owner unknown.

**And one fact that reframes the whole question:** the remarketing list `All Converters`
("People who converted on your site", 180 days) holds **16 members** against `All visitors` at
160. **The conversion tag demonstrably fires.** *(Caveat: all traffic sources, 180 days, a
rounded audience estimate — it proves the tag fires; it is not a lead count.)* The question is
therefore not "is tracking broken?" but **"why has none of 22 paid clicks converted, when site
visitors do?"**

---

## The minimum viable plan — 10 mutations

| # | Plan | Action | Mutations | Approval phrase |
|---|---|---|---:|---|
| 1 | **R3** | CPC ceiling $30.00 → $22.00 on both campaigns | **2** | `APPROVE PLAN-R3 97D8B268A80A FOR 1521725229` |
| 2 | **R2** | Add 3 precise negatives ×2 campaigns, then remove the bare `cleaning` ×2 | **8** | `APPROVE PLAN-R2 2A06983866C1 FOR 1521725229` |
| | | **Total** | **10** | |

**Running alongside, with zero Google Ads mutations:**

| Plan | What | Mutations |
|---|---|---:|
| **R1** | Fix conversion counting · get the WhatConverts export · resolve the foreign tag | 0 |
| **R7** | Landing-page brand, city lock, countdown — *needs the site owner's separate approval* | 0 |

**Explicitly held back from the minimum plan:** R8 (asset parity — 2 mutations, safe, but not
same-day critical), R5 and R6 (create-paused — no same-day effect by design), R9 (produces no
leads), R10 and R11 (blocked), R12 (recommends no change).

---

## Expected effects

| Change | CPC | CTR | CVR | Qualified leads | Risk | Confidence | Time |
|---|---|---|---|---|---|---|---|
| **R3 — ceiling $22.00** | **−36%** ($33.10 → ~$21.10) | neutral | neutral | **+~57% click volume at flat spend** | **MEDIUM-LOW** — impression share falls; lost IS to rank rises from 20–36% | **HIGH** on price, **MEDIUM** on volume | **~15 min**, effect within 2–4 h (bid propagation) |
| **R2 — negative fix** | slight ↑ (unblocks in-scope demand) | slight ↑ (better intent match) | slight ↑ | **+~1–3 qualified impressions/day** | **MEDIUM** — two removals increase exposure, re-fenced first by the adds | **MEDIUM** — based on 8 impressions and 1 click of measured blocked demand | **~10 min**, effect within 1 h |
| **R1 — conversion counting** | none | none | **none** | **0 new leads** — but every future lead becomes visible | **NONE** — zero mutations | **HIGH** | 1 h once UI access exists |
| **R7 — landing-page fixes** | ↓ indirectly, via landing-page Quality Score | neutral | **↑ — the largest untapped lever** | unquantifiable without a baseline | **LOW–MEDIUM** — a WordPress edit could break the form or tag; QA list covers it | **MEDIUM** | 2–4 h developer time |

### Combined, honestly stated

Applied to the 18 clicks already bought, **PLAN-R3 alone turns $595.87 into $379.71** — the
same traffic for **$216.16 less**. Forward-looking, at a flat $82.61/day combined budget it
should buy roughly **50% more clicks**.

**But: more clicks at a lower price is not the same as more leads.** The account has produced
zero recorded conversions in 18 attempts. If the true lead rate is 5%, 28 clicks yields ~1.4
expected leads where 18 yields ~0.9. **That is the honest size of the prize from the bidding
fix alone** — meaningful, not transformative. The transformation, if it comes, comes from
PLAN-R7's landing-page and trust work and from PLAN-R6 buying the two large, cheap demand
buckets the account currently ignores.

### What this plan will make *worse*, stated plainly

**Impression share will fall.** Campaign A is at 53.55% and campaign B at 66.30%; absolute-top
share is 31.35% and 45.67%. A $22 ceiling deliberately gives some of that back. **If the
account is judged on impression share or Optimization Score, PLAN-R3 will look like a
regression.** It should be judged on cost per qualified lead. That is the whole argument.

---

## Review gate

**14 days after PLAN-R3 executes.** Revert to $30.00 if *both*: total impressions fall below
60% of the trailing 14-day baseline, **and** no qualified lead has been produced. In that case
the lower ceiling bought neither volume nor leads, and $30.00 should be restored while the
Quality Score work in R5 and R7 takes effect.

**Immediate watch item, first three billable clicks after execution:** if any exceeds $22.00
more than two hours after the write, the ceiling is not binding and R3 must be revisited. Bid
propagation delay is expected — the equivalent watch on the $30 ceiling resolved correctly on
2026-08-27, where two clicks above the cap turned out to be pre-ceiling.

**Do not use `change_event` to corroborate execution.** It lags by hours and returned zero rows
for a confirmed PLAN-K1 write two hours after the fact. Corroborate with a resource readback
plus a field-level before/after diff.

---

## Recommended first approval

```
APPROVE PLAN-R3 97D8B268A80A FOR 1521725229
```

Two mutations. One field. Immediate effect on the account's single largest controllable cost.
Rollback is one write.

**PLAN-R1 can start in parallel** — it has zero Google Ads mutations and its three P0 items
(conversion counting, the WhatConverts export, the foreign tag) all need someone other than
this agent to act.

---

**MINIMUM VIABLE RECOVERY PLAN — NOT APPROVED, DO NOT EXECUTE**
