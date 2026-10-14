# PLAN-GA-BID-2 — EXECUTION RECEIPT

**Executed:** 2026-09-02 23:59:24 −04:00 (America/New_York)
**Plan:** PLAN-GA-BID-2 — Final interim Maximize Clicks CPC control
**Fingerprint:** `3F1AB2CCFBDA`
**Approval:** `APPROVE PLAN-GA-BID-2 3F1AB2CCFBDA FOR 1521725229` — Walter Correa
**Result:** EXECUTED — 2 mutations, atomic, readback 20/20 PASS

---

## 1. Target

| Field | Value |
|---|---|
| Account | Softwind Power Washing - Live |
| Child customer ID | `1521725229` (152-172-5229) |
| Manager ID | `3373711342` — not used as the operating ID |
| Service | Power Washing |
| Vertical | similar-local-service |

Identity re-verified at execution time: manager=false, test_account=false, status=ENABLED.

## 2. Pre-execution gate — 25/25 PASS

Fingerprint re-derived from `2026-09-02-plan-ga-bid-2-payload.json` = `3F1AB2CCFBDA`,
matching the approval exactly. Both campaigns confirmed still at 30000000 micros and still
`TARGET_SPEND` before the write, so no drift occurred between fingerprinting and execution.
Names and resource names matched the payload. Unrelated pre-state recorded: 17 enabled ad
groups, 240 enabled keywords, 52 enabled ads, 0 ad-group negatives, budgets $41.50 / $41.11.

`validate_only` was run once more against the exact payload immediately before the write:
**PASS**, 2 operations accepted, nothing written.

## 3. What changed

Atomic `MutateCampaigns`, `partial_failure=False`, 2 operations.

| Campaign | Name | Field | Before | After |
|---|---|---|---|---|
| `24103511039` | Power Washing | `target_spend.cpc_bid_ceiling_micros` | 30000000 ($30.00) | **18000000 ($18.00)** |
| `24145053510` | Pressure Washing | `target_spend.cpc_bid_ceiling_micros` | 30000000 ($30.00) | **18000000 ($18.00)** |

`update_mask` on both operations was exactly `["target_spend.cpc_bid_ceiling_micros"]`.

Resources returned:
- `customers/1521725229/campaigns/24103511039`
- `customers/1521725229/campaigns/24145053510`

## 4. Readback QA — 20/20 PASS

Both ceilings read back at 18000000 micros. Verified unchanged on both campaigns: bidding
strategy (`TARGET_SPEND`), budget, status, serving status, name, Search Partners (off),
Display (off). Verified unchanged account-wide: 17 enabled ad groups, 240 enabled keywords,
52 enabled ads, 0 ad-group negatives.

## 5. Why $18.00 and not $14.00

$14.00 was the candidate carried into this run. It was rejected on fresh evidence, not
preference. The localized Keyword Planner sweep over the live service area found a hard
top-of-page-LOW cliff at **$15.09** gating five of the eleven priced keyword families —
`pressure washing near me`, `house washing near me`, `house power washing near me`,
`house pressure washing near me`, `soft washing near me`. Those are every keyword in the
House Washing and Soft Washing ad groups enabled the previous day by PLAN-GA-LAUNCH-3A.
$15.00 clears nothing $14.00 does not, with $0.09 of margin on an estimate.

$18.00 is the lowest ceiling in the compared set ($10 / $12 / $14 / $15 / $18 / $30) that
keeps all 11 priced families top-of-page eligible. Against $30.00 it gives up roughly one
point of priced demand (56% vs 57%) for about 40% off the clearing price.

Supporting evidence: with the $30.00 ceiling, **7 of 8** clean post-ceiling clicks cleared
between $29.04 and $29.90 — the ceiling, not competition, was setting the price. Lost
impression share to budget was only 2.9% / 6.7% while lost to rank was 43.0% / 24.4%.

## 6. Expected effect and what to watch

Clearing price should fall to roughly $17.50, raising click capacity at the unchanged
$82.61/day combined budget from about 2.75 to about 4.59 clicks per day. Lost impression
share to rank will rise.

**Checkpoint 2026-09-03, after at least five full serving hours.** If lost-IS-to-rank exceeds
roughly 65% on either campaign without a compensating rise in click volume, revisit the
ceiling through a new plan. Run `python scripts/softwind_monitor.py all`.

No qualified-lead forecast is offered. `metrics.all_conversions` is 0.0 on both campaigns, so
there is no baseline from which a CPL or lead count could be projected honestly.

## 7. Rollback

Restore `target_spend.cpc_bid_ceiling_micros` to **30000000** on both campaigns through a
new, separately approved plan. No automated rollback exists and none was created.

## 8. Scope statement

This execution changed **two campaign bid ceilings and nothing else**. It did not change any
budget, bidding strategy, campaign status, campaign name, ad group, keyword, ad, negative
keyword, asset, audience, demographic, location, ad schedule, conversion action, conversion
goal, final URL, or network setting. It made no website, Google Tag Manager, or WhatConverts
change. The 103 routing negatives in PLAN-GA-LAUNCH-2A were **not** applied and still await
their own approval.
