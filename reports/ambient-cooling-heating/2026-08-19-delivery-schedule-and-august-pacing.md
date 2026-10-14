# Ambient Cooling — Delivery Schedule + August Pacing (READ · DRAFT · VALIDATE-ONLY)

**Child account:** `Ambient Cooling - Live` · **ID** `240-195-9466` (`2401959466`)
**Manager:** `Green Marketing` `3373711342` · **Second manager:** ClickCease Client Center `2815082755` (ACTIVE, protected)
**Timezone:** America/New_York · **Currency:** USD
**Account local time at capture:** 2026-08-19 21:35:55 −04:00
**Services:** AC Repair · HVAC Repair · HVAC Installation · HVAC Replacement · Gas Boiler Repair

> **No external change was made.** Every read was a GAQL `SELECT`. Every mutation shape was
> exercised with `validate_only=true`, which Google executes without writing. A post-probe
> re-read confirms 139 ad-schedule criteria, 30 on the five, call-asset schedule rows 0, and
> all five budgets unchanged.

---

## 1. Identity gate — PASS

| Check | Expected | Fresh API | |
|---|---|---|---|
| Name | `Ambient Cooling - Live` | `Ambient Cooling - Live` | ✅ |
| Customer ID | `2401959466` | `2401959466` | ✅ |
| Timezone | `America/New_York` | `America/New_York` | ✅ |
| Currency | `USD` | `USD` | ✅ |
| `- live` marker | required | present | ✅ |
| Manager / test account | false / false | false / false | ✅ |

Local `work-order.yaml` and `client.yaml` already carried the exact name — **no rename was
needed**. Work-order validation: `PASS | Ambient Cooling - Live | 2401959466 | heating-cooling
| AC Repair`.

Both manager links verified ACTIVE and untouched.

## 2. Preserved work — verified intact

| Ad IDs | State | |
|---|---|---|
| `821319509197` `821319509200` `821319509203` `821319509206` `821319509209` `821319509212` | ENABLED · APPROVED · REVIEWED · no policy topics | ✅ |
| `820900825428` `820900825431` `820900825434` `820900825437` `820944944368` `820944944371` | PAUSED · DISAPPROVED (CONSUMER_FINANCE) | ✅ |

Nothing was recreated, duplicated, edited or re-enabled. Stale fingerprints
`50701AE742FCDEEB` and `6A2DE7A6589CA2B7` were **not** executed and are formally superseded
inside Package A.

## 3. Campaign identity — verified fresh

| Service | Campaign ID | Name | Status |
|---|---|---|---|
| AC Repair | `24132507741` | Search \| NonBrand \| AC Repair \| Central MD \| BOFU \| 2026-08 | ENABLED / SERVING |
| HVAC Repair | `24132507750` | Search \| NonBrand \| HVAC Repair \| Central MD \| BOFU \| 2026-08 | ENABLED / SERVING |
| HVAC Installation | `24132507747` | Search \| NonBrand \| HVAC Installation \| Central MD \| BOFU \| 2026-08 | ENABLED / SERVING |
| HVAC Replacement | `24132507753` | Search \| NonBrand \| HVAC Replacement \| Central MD \| BOFU \| 2026-08 | ENABLED / SERVING |
| Gas Boiler Repair | `24132507744` | Search \| NonBrand \| Gas Boiler Repair \| Central MD \| BOFU \| 2026-08 | ENABLED / SERVING |

These five are the **only ENABLED campaigns in the account**. Every other non-removed campaign
is PAUSED and spent **$0.00** in August.

## 4. The finding that changes the schedule plan

The 30 campaign `AD_SCHEDULE` criteria were **not part of the launch build**. `change_event`
shows they were created through the Google Ads web UI on **2026-08-17 between 10:39:27 and
10:47:51** account time — three days after the 2026-08-14 13:04:40 launch.

The campaigns ran 24/7 from launch until 2026-08-17 ~10:40, and the data proves a campaign with
zero schedule criteria serves all day: 88 impressions landed in hours 00:00–07:59 / 19:00–23:59,
and 65 impressions landed on Sunday 2026-08-16 for $20.34. That removes any need to create 35
all-day rows.

## 5. Call-asset inventory — the decisive fact

`CallAsset.ad_schedule_targets` lives on the **Asset** resource, so it is shared by every link
the asset has. That normally forces a dedicated duplicate. It does not here.

| Asset | Phone | Schedule rows | Links on the five | Links elsewhere | Verdict |
|---|---|---|---|---|---|
| `407995613637` | **(410)705-6354** | 0 | **5** | **0** | Only asset that can serve with the five, and exclusive to them |
| `343054924787` | (410) 705-6354 | 0 | 0 | 6 legacy | Not touched |
| `80497290055` | (410) 415-9517 | 0 | 0 | 10 legacy | Not touched |
| `98498198415` | (410) 415-9517 | 7 | 0 | 7 legacy | Not touched |
| `369249814267` | 4107056354 | 7 | 0 | 0 (customer link REMOVED) | Inert, not touched |

No customer-level and no ad-group-level CALL asset can serve with the five. The barred numbers
(410) 914-1456, (410) 761-0932 and (410) 415-9517 appear on **no** call asset linked to the five.

**Because `407995613637` is exclusive to the five campaigns, the schedule is set in place — one
mutation, no duplicate asset, no association added or removed, zero reach into legacy campaigns.**

---

# Package A — Delivery and call schedule

### `PLAN FINGERPRINT: 44D14DA4714BB6E8`

`clients/ambient-cooling-heating/plans/delivery-and-call-schedule-package-2026-08-19.json`

**31 mutations: 0 creates · 1 update · 30 removals.** One atomic
`GoogleAdsService.Mutate`, `partial_failure=false`.

**Operation 1 — call asset schedule (applied first, so the number is never live unattended)**

`update customers/2401959466/assets/407995613637`, `update_mask ["call_asset.ad_schedule_targets"]`

| Day | Before | After |
|---|---|---|
| Monday–Friday | *(no asset schedule)* | 08:00–20:00 ET |
| Saturday | *(no asset schedule)* | 08:00–13:00 ET |
| Sunday | *(no asset schedule)* | **no row — ineligible** |

Phone number, country code, conversion reporting state and conversion action are **not** in the
update mask. Hours are account-timezone; no UTC conversion anywhere.

**Operations 2–31 — remove all 30 campaign `AD_SCHEDULE` criteria**

6 per campaign × 5 campaigns. All currently ENABLED, `negative=false`, `bid_modifier=0.0`, so no
bid modifier is lost. Criterion IDs `303280` `313280` `323280` `333280` `343280` `353252` on each
of the five campaign IDs.

| | Before | After |
|---|---|---|
| Campaign eligible hours/week | 65 (38.7%) | **168 (100%)** |
| Sunday | 0 hours | 24 hours |
| Call-asset eligible hours/week | 65 (inherited) | **65 (its own schedule)** |
| Criterion counts per campaign | LANG 1 · DEVICE 3 · **SCHED 6** · LOC 75 | LANG 1 · DEVICE 3 · **SCHED 0** · LOC 75 |

**Campaign associations to create: 0. To remove: 0.**

**Effect on legacy campaigns: none.** 109 `AD_SCHEDULE` criteria on 19 PAUSED/REMOVED campaigns
are not referenced. The four legacy call assets are not referenced. Both manager links, GTM and
WhatConverts are not referenced.

**Forms:** unaffected and still 24/7 — removing the campaign schedule only widens the hours a
paid visitor can reach the form. The landing-page phone button stays 24/7 by design.

**Validate-only:** `VALIDATE_OK`, 31 operations, 0 errors. Component probes all `VALIDATE_OK`,
including a fallback duplicate-asset create that is **not** used.

**Rollback:** clear `ad_schedule_targets` back to empty on `407995613637`, then re-create the 30
criteria from the verbatim before-state in the plan. 31 mutations, no data loss.

---

# Package B — August budget pacing

### `PLAN FINGERPRINT: EF9FBA55926545F2`

`clients/ambient-cooling-heating/plans/august-budget-pacing-package-2026-08-19.json`

**5 mutations: 0 creates · 5 updates · 0 removals.** One atomic
`GoogleAdsService.Mutate`, `partial_failure=false`.

## Fresh pacing

| | |
|---|---|
| August MTD spend, five campaigns (Aug 1–19) | **$1,033.23** |
| Spend since 2026-08-14 launch | $1,033.23 |
| Spend since replacement RSAs eligible (Aug 18 15:17 ET) | $884.64 |
| Remaining budget | **$13,000.00 − $1,033.23 = $11,966.77** |
| Remaining calendar days incl. today / days a new budget applies | 13 / **12** (Aug 20–31) |
| Required daily pace | **$997.23/day** |
| Current total daily budget | $427.64/day |
| Multiplier required | **2.33×** |
| Projected August at current budgets | **$6,164.91** |
| Budget utilisation since launch / today | 40.3% / 142.4% |

*The old $22.68 figure is superseded.* Today is 21:35 ET and Google's last recorded hour is
17:00, so Aug 19 may still rise; every figure is re-derived from a fresh read before execution.

### Daily spend by campaign

| Date | AC Repair | HVAC Repair | HVAC Install | HVAC Replace | Gas Boiler | Total |
|---|---:|---:|---:|---:|---:|---:|
| 08-14 | 2.34 | 0.00 | 0.00 | 0.00 | 0.00 | 2.34 |
| 08-15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 08-16 | 0.00 | 20.34 | 0.00 | 0.00 | 0.00 | 20.34 |
| 08-17 | 47.78 | 21.72 | 0.00 | 0.00 | 0.00 | 69.50 |
| 08-18 | 0.00 | 56.41 | 275.58 | 0.00 | 0.00 | 331.99 |
| 08-19 | 282.06 | 54.25 | 272.75 | 0.00 | 0.00 | 609.06 |
| **MTD** | **332.18** | **152.72** | **548.33** | **0.00** | **0.00** | **1,033.23** |

### Performance and impression share, August MTD

| Campaign | Cost | Impr | Clicks | CTR | CPC | Conv | Search IS | Lost IS budget | Lost IS rank |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HVAC Installation | 548.33 | 351 | 13 | 3.70% | $42.18 | 0 | 52.03% | **32.47%** | 15.50% |
| AC Repair | 332.18 | 121 | 7 | 5.79% | $47.45 | 0 | 21.84% | 0.00% | **78.16%** |
| HVAC Repair | 152.72 | 404 | 4 | 0.99% | $38.18 | 0 | 23.04% | 0.00% | **76.96%** |
| HVAC Replacement | 0.00 | 5 | 0 | — | — | 0 | 13.04% | 0.00% | **86.96%** |
| Gas Boiler Repair | 0.00 | 0 | 0 | — | — | 0 | **0.00%** | 0.00% | 0.00% |
| **Total** | **1,033.23** | **881** | **24** | **2.72%** | **$43.05** | **0** | | | |

**Segmented by conversion action:** zero primary conversions. The only recorded event is
2 × *Local actions – Directions* (`6642544931`, GET_DIRECTIONS) on HVAC Repair, which is excluded
from the conversions metric and is not a bidding signal. Seven primary lead actions — LP form,
phone-call lead, thank-you page, call button, calls from ads, WC Calls, WC Lead — all recorded
zero. **CPL, CPQL, CAC and ROAS are undefined.**

**Serving status:** all five ENABLED / SERVING. Three show `LIMITED (HAS_ADS_DISAPPROVED)` —
cosmetic: Google counts the six paused CONSUMER_FINANCE originals. Every ENABLED RSA is APPROVED
and REVIEWED. Bidding is TARGET_SPEND on all five, standard not portfolio, with
`cpc_bid_ceiling_micros = 0` (**no max-CPC limit set**).

**Pre-fix vs post-fix:** Aug 14–18 $424.17 — Gas Boiler, HVAC Installation and HVAC Replacement
were blocked by disapprovals for most of it and are not judged on it. Post-fix (Aug 18 15:17
onward) $884.64 with all five carrying approved enabled RSAs.

## Proposed budgets — approved percentages preserved exactly

There is **zero** conversion evidence, so no reallocation is defensible. Each campaign keeps its
approved share of the $11,966.77 remaining, spread over 12 days.

| Campaign | Share | Current/day | **Proposed/day** | Δ | Remaining month share | Max 2× overdelivery |
|---|---:|---:|---:|---:|---:|---:|
| AC Repair | 33.08% | $141.45 | **$329.85** | +$188.40 | $3,958.24 | $659.70 |
| HVAC Repair | 18.46% | $78.95 | **$184.10** | +$105.15 | $2,209.25 | $368.20 |
| HVAC Installation | 32.31% | $138.16 | **$322.18** | +$184.02 | $3,866.19 | $644.36 |
| HVAC Replacement | 6.15% | $26.32 | **$61.37** | +$35.05 | $736.42 | $122.74 |
| Gas Boiler Repair | 10.00% | $42.76 | **$99.72** | +$56.96 | $1,196.68 | $199.44 |
| **Total** | 100% | **$427.64** | **$997.22** | **+$569.58** | **$11,966.77** | **$1,994.44** |

`1,033.23 + (997.22 × 12) = $12,999.87` — $0.13 under the cap.

### Evidence per campaign

- **HVAC Installation — increase well supported.** The only campaign where budget is provably
  binding: 32.47% budget-lost IS MTD, 53.01% today, against 15.50% / 0.00% rank-lost. Expect this
  increase to convert almost fully.
- **AC Repair — increase partly supported.** 0.00% budget-lost but 78.16% rank-lost. It still hit
  199.4% of its daily budget today, so real demand is pressing on the budget, but auction rank
  caps it.
- **HVAC Repair — increase not supported by delivery evidence.** 0.00% budget-lost, 76.96%
  rank-lost, only 68.7% of today's budget used, CTR 0.99%. Applied to hold the approved 18.46%
  share.
- **HVAC Replacement — increase not supported.** 5 impressions, $0.00 in 19 days, 0% of budget
  used. Its RSAs only became eligible Aug 18 15:17, so the blocked period is excluded; it still
  has no delivery. Applied to hold the approved 6.15% share.
- **Gas Boiler Repair — increase not supported.** 0 impressions and **0.00% search impression
  share** in 19 days: Google recorded no eligible auction at all. Applied to hold the approved
  10.00% share.

## Expected August projection — and the honest verdict

| | |
|---|---|
| Budget-bounded ceiling (design target, not a forecast) | **$12,999.87** |
| **Demand-bounded central estimate** | **≈ $9,133** |
| Demand-bounded range | $7,957 – $10,477 |
| Expected shortfall vs cap | $2,523 – $5,043 |

> ### Increasing budgets alone will not produce $13,000 of August spend.
>
> Four of five campaigns report **0.00% search lost impression share from budget** — for those,
> budget is not the constraint and raising it cannot buy a single extra impression. The same four
> report 63–87% lost impression share from **rank**, or in Gas Boiler Repair's case no eligible
> auction at all. Total eligible impressions since launch are ~3,021, about 500/day; at the
> observed 2.72% CTR and $43.05 CPC, even 100% impression share is worth only about **$590/day**.
>
> Of the $569.58/day increase, ~$184 (HVAC Installation) is well supported, ~$188 (AC Repair) is
> partly supported, and ~$197 across the other three is expected to sit unspent.
>
> Only a broader keyword footprint, a higher bid ceiling, more services or more geography would
> raise eligible auction volume. All four are out of scope and none is proposed.

### Risks

- **Maximum possible daily overdelivery:** Google may spend 2× a daily budget on any day →
  **$1,994.44/day**, an arithmetic ceiling of **$23,933.28** across Aug 20–31 ($24,966.51 for
  August). Google's monthly charging limit is per campaign and is recalculated when a budget
  changes mid-month, so it cannot be relied on to hold this account to $13,000. Observed demand
  makes the ceiling unreachable in practice — the dependable safeguard is the daily pacing check.
- **CPC inflation.** CPC is already $43.05 across the five and **$70.52 on AC Repair today**, with
  zero leads. Under Maximize Clicks with no CPC ceiling, raising the budget on a rank-limited
  campaign is functionally an instruction to bid harder. **Recommended but NOT included and NOT in
  this fingerprint:** a `target_spend.cpc_bid_ceiling_micros` on AC Repair and HVAC Installation.
  It caps inflation without changing the strategy type, and needs its own approval.
- **Measurement.** Zero primary conversions reach Google Ads. Spending to a $13,000 cap while no
  lead event lands means the money buys clicks with no measurable outcome. Out of scope here;
  flagged, not actioned.

### Monitoring

Daily read-only pacing check at/after 09:00 ET. Reduce-trigger: cumulative spend exceeds
`1,033.23 + 997.23 × days-elapsed` by more than 10%. Stop-trigger: cumulative reaches $12,400.
Full re-pace on **2026-08-24**, the first point at which the increase can be judged.

**Validate-only:** `VALIDATE_OK`, 5 operations, 0 errors. Budgets re-read unchanged after the
probe.

**Rollback:** one 5-operation mutate restoring 141450000 / 42760000 / 138160000 / 78950000 /
26320000 micros. Immediate, no data loss.

**Alternative not proposed:** moving the ~$161/day that Gas Boiler Repair and HVAC Replacement
cannot spend into AC Repair and HVAC Installation. It changes the approved per-service
percentages — a business decision, not a technical one — and would still not reach $13,000. It
would need a new package and a new fingerprint.

---

## Receipts

| File | Contents |
|---|---|
| `snapshots/identity-gate-2026-08-19.json` | Fresh identity + manager links + account local time |
| `snapshots/preflight-structure-2026-08-19.json` | Campaigns, budgets, 139 schedule criteria, full call-asset inventory, RSA state |
| `snapshots/pacing-audit-2026-08-19.json` | Daily/windowed spend, impression share, conversion segmentation, keyword and hour/day segments |
| `snapshots/validate-only-2026-08-19.json` | Component validate-only probes |
| `snapshots/validate-only-atomic-2026-08-19.json` | Exact atomic execution shapes for A and B |
| `plans/delivery-and-call-schedule-package-2026-08-19.json` | Package A · `44D14DA4714BB6E8` |
| `plans/august-budget-pacing-package-2026-08-19.json` | Package B · `EF9FBA55926545F2` |

## Required next input

Approve each fingerprint separately and exactly. Nothing is executed until then.

```
APPROVE PACKAGE A 44D14DA4714BB6E8 FOR 2401959466
APPROVE PACKAGE B EF9FBA55926545F2 FOR 2401959466
```
