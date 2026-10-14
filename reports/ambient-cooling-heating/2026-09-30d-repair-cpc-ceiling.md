# Ambient: Heating & Furnace Repair CPC ceiling (2026-09-30d)

> **SUPERSEDED 2026-09-30e. See `2026-09-30e-repair-cpc-18-vs-21.md`.**
> - The recommendation is now **$18** (`AMB-0930-REPAIR-CPC-2` / `CC87C9A6F406`). `CB667F2D4610` ($21) is superseded.
> - The claim that the forecast API cannot return impressions was wrong. It applies to v24/v25 only; v23 returns them.
> - The top-of-page low estimate is evidence, not a floor.


- **Account:** Ambient Cooling - Live · child 2401959466.
- **Campaign:** 24257819463 `Search | NonBrand | Heating & Furnace Repair | Central MD | BOFU | 2026-09`.
- **Work order:** `work-orders/work-order-heating-repair-cpc-ceiling-2026-09-30.yaml` (valid).
- **Checks:** identity 8/8.
- **Changes: none.** Only Google's validate-only check ran, and it writes nothing.
- **Owner direction:** the repair services stay live. `AMB-0930-CPL-CONTAIN-1R` / `4C544E4CE290` is **withdrawn**: its file is renamed `.WITHDRAWN` and its executor refuses to run.

## Recommendation: lower the ceiling from $42 to $21

Plan `AMB-0930-REPAIR-CPC-1` · fingerprint **`CB667F2D4610`** · 1 operation · VALIDATE_OK.

- **Changes only** `campaign.target_spend.cpc_bid_ceiling_micros`, from 42,000,000 to 21,000,000.
- **Stays as is:** all five repair ad groups (none paused), keywords and match types, ads, landing pages, locations, schedule, negative lists, conversions, Search-only networks, and the $85/day budget. These are locked into the fingerprint and compared again after execution.
- **Before execution** the plan is rebuilt from fresh data. Any drift changes the fingerprint, and the run refuses.

## Evidence

**Actual, complete days Sept 17–29** (Sept 30 provisional: 6 clicks, $169.21, 0 leads):
- The campaign spent $469.90 on 17 clicks, **$27.64 average**, with **0 verified leads**. All 15 Heating Repair clicks came from the phrase keyword "heating repair" ($406.12).
- Impression share was 37.5%: 45.9% lost to rank and 16.6% to budget.
- Search terms cover 54% of the campaign's cost. The visible click prices:
  - $15–18: 1 click
  - $21–25: 1 click
  - $25–30: 5 clicks
  - $30–42: 2 clicks
  
  So 7 of 9 visible clicks cost more than $21.

**Keyword Planner, Maryland** (`geoTargetConstants/21153`, resolved from Google; English; Google Search). Top-of-page ranges run from Google's 20th to 80th percentile of bids:

| Keyword | Maryland searches/mo | Top of page, low – high | Planner average CPC | Ambient actual CPC |
|---|---|---|---|---|
| furnace repair | 2,900 (Jan 6,600) | $12.55 – $61.73 | $38.09 | no clicks yet |
| furnace repair near me | 1,300 (Jan 2,400) | **$20.41** – $53.64 | $41.68 | no clicks yet |
| heater repair (Google merges "heating repair" into this) | 170 (Jan 320) | no data | – | heating repair: $27.07 |
| gas furnace repair | 260 | no data | – | – |
| furnace repair service | 170 | no data | – | – |
| furnace not working | 30 | no data | – | $31.89 |
| others (electric furnace, residential, no heat) | ≤ 10 | no data | – | – |

**Forecasts** (Maximize Clicks, Oct 1–31, Maryland, all enabled repair keywords):
- The API returns clicks, cost and average CPC only. **No impressions**, no negatives, no schedule.
- Results are the same at the real $85 budget and uncapped, so the budget doesn't bind.
- Read the results as relative changes.

| Ceiling | Clicks | Cost | Avg CPC | Clicks vs $42 |
|---|---|---|---|---|
| $8 | 51 | $241 | $4.69 | −62% |
| $10 | 63 | $345 | $5.44 | −54% |
| $12 | 73 | $455 | $6.24 | −47% |
| $15 | 87 | $645 | $7.40 | −36% |
| $18 | 95 | $780 | $8.20 | −30% |
| **$21** | **103** | **$933** | **$9.06** | **−25%** |
| $25 | 112 | $1,156 | $10.33 | −18% |
| $30 | 121 | $1,431 | $11.82 | −12% |
| $42 (current) | 137 | $2,045 | $14.93 | – |

Planner's average CPC at $42 ($14.93) is about half Ambient's actual $27.64. Planner blends in cheap statewide, lower-position clicks, so it understates what Ambient's footprint really pays.

By keyword, "furnace repair" loses 46% of forecast clicks at $12 and 24% at $18. "furnace repair near me" loses 47% at $12 and 31% at $18.

**History** (Google's conversion counts, which double-counted calls):
- **All-time repair-intent search terms:** converting terms averaged **$62.91** a click, non-converting terms $8.96.
  - 34.3 of 36.3 conversions came from terms averaging $18 or more.
  - 29 came from terms averaging $30 or more.
- **Legacy "Heating Repair" campaign** (manual CPC):
  - 2023–24: $28.27 a click, 16.2% conversion rate, $174 per conversion.
  - 2024–25: $14.60 a click, **2.1%**, **$686 per conversion**.
  - Of its 69 conversions, 45.3 were call-button calls.

## Why $21

- **$21 is the lowest round ceiling above the top-of-page low end for both core terms.** Those are "furnace repair" at $12.55 and "furnace repair near me" at $20.41, the highest-intent query.
- **At $18,** Ambient drops below the low end for "near me", for a gain of only 5 points of forecast traffic.
- **At $12,** Ambient is below the low end on both. It loses about 47% of forecast clicks. It also buys the price band where repair clicks historically didn't convert: $14.60 a click came with a 2.1% conversion rate.
- **At $25–30,** the savings are small, and hitting $280 would need a 7.9%+ conversion rate.

## CPL math

Required conversion rate = CPC ÷ CPL. Planner does not predict CPL or lead quality.

| Ceiling | Likely average CPC* | Needed for $280 | Needed for $350 |
|---|---|---|---|
| $12 | $10–11.50 | 3.6–4.1% | 2.9–3.3% |
| $18 | $15.50–17 | 5.5–6.1% | 4.4–4.9% |
| **$21** | **$18–20** | **6.4–7.1%** | **5.1–5.7%** |
| $42 now (actual) | $27.64 | 9.9% | 7.9% |

\* Maximize Clicks tends to price near a ceiling that binds.

What conversion rates look like today:
- Repair campaign: 0 of 17 on complete days.
- Heating program since Sept 24: 4.8% (2 of 42).
- Legacy repair: 2.1% at about $15 CPC, and 16.2% at about $28 when the call button was on.

**At 4.8% and about $19 a click, CPL would be about $396.** That is a 30% improvement on cost per click, but still above the $350 ceiling. Reaching $280 needs about 6.8%.

A lower ceiling alone won't deliver $280. The rest has to come from the conversion rate:
- the D6 form fix;
- a verified call path, since the repair call button is paused and repair demand has historically come by phone;
- message match.

## Expected impact and risk

- **Traffic:** −25% of clicks by forecast. It could be as much as about −60% if every current $21+ click is lost and not replaced. The 16.6% of impressions lost to budget should mostly disappear.
- **Spend:** the budget stays $85/day, so the monthly charging limit stays about $2,584. Expected spend is about $55–75 per serving day, roughly $1,200–1,650 a month, rising with the Oct–Jan season.
- **Risk to good searches: moderate to high.** Historically the converting repair clicks were the expensive ones. But those came with call extensions, which are paused on this campaign now, so today's $27 clicks aren't the same traffic.
- **Evaluation** (manual; the monitor is **NOT ACTIVE**):
  - Compare complete days after the change with the days before, keeping the full history.
  - Track clicks, average CPC, rank- and budget-lost impression share, verified leads and CPL bands.
  - Nothing reverses automatically. Going back to $42, or any other change, needs its own approval.

## Flagged, not in the plan

The "heating repair" **phrase** keyword got 815 impressions in 8 days, against about 170 Maryland searches a month for its Planner bucket. Most visible clicks came from heating searches that don't say "repair" (Google's same-meaning phrase matching).

Keywords, match types and negatives stay unchanged per the owner. I recommend a separate relevance review.
