# EKG Lawn Services — budget and pacing report

Date: 2026-08-14 · Account 7478932848 · Currency USD · Time zone America/New_York
Source: `snapshots/all-time-2026-08-14.json` (live read)

## Current month

| Item | Value |
|---|---:|
| Monthly Google Ads budget | $500.00 |
| Days in August 2026 | 31 |
| Days elapsed through 2026-08-14 | 14 |
| Remaining serving days | 17 |
| **Month-to-date spend** | **$259.51** |
| **Remaining monthly budget** = max(0, 500 − 259.51) | **$240.49** |
| Current daily run rate (259.51 ÷ 14) | $18.54/day |

All $259.51 of month-to-date spend comes from one campaign, `Lawn care & Landscaping`
(19855617751), the only ENABLED campaign in the account.

## The pacing problem

At the current run rate the account is **already tracking to overspend** before the new
campaign exists:

```
259.51 + (18.54 × 17 remaining days) = $574.63 projected month-end
$574.63 − $500.00 = $74.63 over the monthly budget
```

The existing campaign's own daily budget is $18.44, which is above the $16.45 that a
$500 month supports. This is a pre-existing condition, not something the new build creates.

## Proposed first-month daily budget

Only valid **if** the enabled campaign is paused at Checkpoint B, which frees the whole
remaining balance:

| Item | Value |
|---|---:|
| Remaining monthly budget | $240.49 |
| Remaining serving days | 17 |
| **Temporary first-month daily budget** | **$14.15/day** |
| Ongoing full-month daily budget (500 ÷ 30.4) | $16.45/day |
| Projected month-end if paused now and the new campaign runs the balance | ~$500.00 |

If the existing campaign is **not** paused, there is no room for the new campaign inside
$500 this month. The account would need either a higher monthly budget or a later start.

## Budget rules observed

- The $16.45 ongoing daily budget is set at **campaign level** and shared dynamically
  across both ad groups. It is not split into fixed per-ad-group budgets.
- No budget has been changed. Changing one requires separate approval.
- The new campaign will be created PAUSED, so it spends nothing until Checkpoint H.

## Decision needed

1. Confirm $500/month is still correct.
2. Choose: pause the existing campaign now (releases $240.49), or accept a projected
   $574.63 month and defer the new campaign's start.
3. Confirm whether the first month should use the temporary $14.15/day or start at the
   ongoing $16.45/day and accept a small overrun.
