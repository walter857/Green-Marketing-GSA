# Ambient Cooling — 2026-09-16 heating research activity update

**Account:** Ambient Cooling - Live | 2401959466
**Mode:** research and drafting only. **Zero external writes. No campaign created or enabled.**

## The headline

**Ambient has run heating ads before, and the numbers are much better than cooling.**
15 heating campaigns in the account history: **$108,464 spent, 7,251 clicks, $14.96 average CPC**.
The best of them, *Heating Repair*, delivered a conversion every **$252.83** at an **$18.76** click.
For comparison, the live cooling campaigns run at $67–$106 per click and August's cost per
qualified lead was **$977.54**.

Heating clicks in this market are roughly **a quarter the price of cooling clicks**, and Google's
Keyword Planner shows **LOW competition** on nearly every heating term while the cooling equivalents
are HIGH.

## Timing matters — the window is about two weeks out

`furnace repair` searches in Ambient's own service area go **110 in September → 320 in October →
590 in December → 720 in January**. A 6.5× swing. WhatConverts heating leads follow the same curve:
10 in September, 28 in October, **57 in December**.

## What we recommend

**Three ad groups in one new Heating Services campaign:**

| # | Ad group | Why |
|---|---|---|
| 1 | **Furnace & Heating Repair** | Biggest demand (460/mo), best CPA in account history ($252.83), dedicated Ambient page |
| 2 | **Heat Pump & Ductless** | Largest qualified-lead cluster — 36 of 98 heating qualified leads in 12 months. Works year-round |
| 3 | **Heating Installation & Replacement** | Highest ticket, cheapest historical clicks ($16.19) |

**Held back on evidence:** Heating Maintenance and Boiler (Tier B), Oil Furnace (Tier B).
**Excluded:** Tankless water heaters — $12,531 spent historically for **2** conversions, a $6,265
cost per conversion. Geothermal — zero conversions across two campaigns.
**On hold — we cannot verify Ambient offers them:** thermostat repair/replacement and electric
furnace repair. There is real demand (80/mo) but nothing on the website confirms the service.

**Boiler note:** an ENABLED Gas Boiler Repair campaign already exists. We would raise *its* budget
in peak season rather than build a duplicate. It also had the worst qualification rate of any
heating cluster — 8 qualified from 20 paid leads — at ~$99 per click.

## Budget — no new money

The $13,000/month cap is unchanged and heating is funded **entirely by reallocation**:

| Campaign | Now | October | Nov–Feb |
|---|---:|---:|---:|
| AC Repair | $141.45 | **$70.00** | $40.00 |
| HVAC Repair | $78.95 | **$40.00** | $30.00 |
| HVAC Installation | $176.15 | $176.15 | $130.00 |
| HVAC Replacement | $20.00 | $20.00 | $20.00 |
| Gas Boiler Repair | $5.00 | $5.00 | $15.00 |
| **Heating Services (new)** | — | **$110.40** | **$186.55** |
| **Total daily** | **$421.55** | **$421.55** | **$421.55** |

Cooling is never switched off — it keeps $220/day (52%) even at peak winter. The money comes from
AC Repair (August: 0.51:1 on revenue) and HVAC Repair (August: $1,665 spent, zero qualified leads).

## The blocker is not heating — it is tracking

Heating cannot launch until the landing-page cache defect is fixed. Right now **0 of 24** test
loads capture the visitor's own click ID, and there are still 10 Primary conversion actions
double-counting. Those fixes are already drafted and waiting for approval as
`AMB-0915-LP-1` and `AMB-0915-CONV-1`.

**Every week that waits costs heating season.** That is the single most useful thing the client can
unblock this week.

Also note: `AMB-0915-CPC-HR-1` (raise HVAC Repair $25 → $65) is now **SUPERSEDED — do not execute**.
The August economics withdrew its basis.

## What was produced

Full research report · historical heating export (JSON + 2 CSV) · Keyword Planner export (JSON +
CSV, raw micros preserved) · geo crosswalk of all 75 targets · candidate normalization for all 33
services · profitability scorecard · 4 validated work orders · **3 complete landing-page content
packages** · **6 RSAs (90 headlines, 24 descriptions, zero violations)** · callout and snippet
drafts · 19 QA acceptance tests · 2 fingerprinted future plans.

## Needed from the client

Average job value for furnace repair and for furnace/heat-pump replacement · close rate · gross
margin · **what `quotable = Yes` actually means in WhatConverts** (quoted, qualified, or sold — it
changes every CPQL) · does Ambient service thermostats and electric furnaces · an approved logo
file at 128×128 or larger.

## Next approval

```
APPROVE AMB-0916-HEAT-STRATEGY-1 9EC0CE017DE7 strategy FOR 2401959466
```

Strategy first. Landing-page content, deployment, create-paused, budget and enablement each follow
as separate approvals with their own fingerprints.
