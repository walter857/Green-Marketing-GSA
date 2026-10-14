# Ambient Cooling - Live | 2401959466
## AUGUST 2026 — cost per qualified lead, services requested, revenue model

**Window: 2026-08-01 → 2026-08-31.** Read-only. Transcripts and form messages were read in
memory to classify the service and discarded — no names, telephone numbers, email addresses,
IP addresses, recordings or message bodies are retained.

### Why August is the clean window

In August the five BOFU Search campaigns were **100% of the account's paid spend**. Every other
paid campaign — including both Performance Max campaigns — spent **$0.00**. Whole account =
$6,842.80 = the five campaigns.

That removes the attribution ambiguity that affects the 90-day view, where $2,235.33 of Performance
Max and legacy Search spend runs alongside and WhatConverts cannot tell the campaigns apart.
**Any August `google/cpc` lead is attributable to the five campaigns.**

---

## 1. August cost per qualified lead

| Metric | August 2026 |
|---|---:|
| Google Ads spend — five campaigns (= whole account) | **$6,842.80** |
| Paid-search leads (WhatConverts) | 14 |
| …of which before the 2026-08-14 launch | 1 |
| Qualified — `quotable = Yes` | **8** |
| Qualified, new business only (excl. 1 existing-customer admin call) | **7** |
| **CPL** | **$488.77** |
| **CPQL — all 8 qualified** | **$855.35** |
| **CPQL — 7 new-business only** | **$977.54** |

Provisional guardrails are $150–$280. August CPQL is **3.5×–6.5× guardrail**.

For contrast, September 1–14: $1,431.74 spend, 2 paid leads, 2 qualified. August ran ~$380/day
across 18 served days; September 1–14 ran $102.27/day.

---

## 2. What the 8 qualified leads actually wanted

| Date | Type | Service requested | Landing page | Click ID |
|---|---|---|---|---|
| 08-20 | Web form | AC Repair | `/reviews/` *(main site — a sitelink click)* | yes |
| 08-21 | Web form | AC Repair | `offer…/ac-repair/` | yes |
| 08-22 | Web form | AC Repair | `offer…/ac-repair/` | yes |
| 08-25 | Web form | **Duct / Airflow** | `offer…/ac-repair/` | yes |
| 08-27 | Phone call | **HVAC Installation** | — | no (`…6354`) |
| 08-27 | Phone call | **HVAC Replacement** | main site home | yes (`…1456`) |
| 08-28 | Phone call | **HVAC Replacement** | — | no (`…6354`) |
| 08-31 | Phone call | *Existing customer / admin* | — | no (`…6354`) |

**New-business mix (7):** AC Repair 3 · HVAC Replacement 2 · HVAC Installation 1 · Duct/Airflow 1

Classified from WhatConverts AI call analysis (Topic / Intent / Keyword Detection, Lead Summary,
Call Type, Customer Type) plus form project text and landing page.

Two incidental findings: the `/reviews/` sitelink I flagged as leakage **produced a qualified lead**
— re-point it, don't remove it. And the mixed-source number `410-914-1456` took a qualified HVAC
Replacement call, which is exactly why it must come off the paid pages.

---

## 3. Service value — EXTERNAL MARKET BENCHMARKS, not Ambient's prices

> ⚠️ **These are published Maryland market ranges, not Ambient's rates.** `client.yaml` still has
> `average_job_revenue: null`, and WhatConverts holds **no** monetary value on any of 294 leads
> (`quote_value` 0/294, `sales_value` 0/294). **Never use these figures in ad copy, on a landing
> page, or in a client-facing profitability claim.** They exist only to size the opportunity until
> Ambient supplies real numbers.

| Service | Maryland 2026 range | Midpoint used |
|---|---|---:|
| AC Repair | $150–$450 per repair; service call $75–$150; MD tune-up avg $165 | **$319** |
| HVAC Replacement | MD $5,000–$13,500; MD avg ~$8,300; Baltimore avg $8,118 | **$8,300** |
| HVAC Installation | $5,000–$12,500 | **$8,300** |
| Ductwork repair | $200–$2,100, avg ~$660; full replacement $1,400–$5,600 | **$660** |

Ambient's service area (Severn, Severna Park, Columbia, Annapolis — Anne Arundel and Howard) sits
between Baltimore City and the DC suburbs, where published guides note a **+10–15%** uplift. The
midpoints above do **not** include that uplift, so this model is conservative.

---

## 4. August revenue model

| Service | Qualified | Low | **Mid** | High |
|---|---:|---:|---:|---:|
| AC Repair | 3 | $450 | **$957** | $1,350 |
| HVAC Replacement | 2 | $10,000 | **$16,600** | $27,000 |
| HVAC Installation | 1 | $5,000 | **$8,300** | $12,500 |
| Duct / Airflow | 1 | $200 | **$660** | $2,100 |
| **Total pipeline** | **7** | **$15,650** | **$26,517** | **$42,950** |

| | |
|---|---:|
| Ad spend | $6,842.80 |
| Revenue per qualified lead (mid) | **$3,788** |
| Cost per qualified lead | **$978** |
| Revenue : ad cost, if every lead closed | **3.9 : 1** |

### Break-even close rates

| Basis | Close rate needed |
|---|---:|
| Revenue only | **25.8%** |
| Gross profit @ 55% margin | 46.9% |
| Gross profit @ 45% margin | **57.3%** |
| Gross profit @ 35% margin | 73.7% |

**August was plausibly around break-even, and only because of the replacement work.** At a normal
HVAC close rate of 30–40% on replacement quotes and 45% margin, August lost money modestly. At
50%+ close it made money.

---

## 5. The finding that matters — the money is not where the budget is

| | Qualified leads | Pipeline value | Share of revenue |
|---|---:|---:|---:|
| **HVAC Replacement + Installation** | 3 | **$24,900** | **93.9%** |
| AC Repair + Duct / Airflow | 4 | $1,617 | 6.1% |

Now set that against where August's budget actually went:

| Campaign | August spend | Traceable qualified output | Pipeline | Ratio |
|---|---:|---|---:|---:|
| **AC Repair** | **$2,550.59** | 2 AC Repair + 1 Duct *(provable — all landed on `/ac-repair/`)* | $1,298 | **0.51 : 1** |
| HVAC Installation | $2,474.53 | *(with Replacement)* 2 Replacement + 1 Installation | $24,900 | **9.5 : 1** |
| HVAC Replacement | $152.52 | ″ | ″ | ″ |
| HVAC Repair | $1,665.16 | **0 qualified leads traced** | $0 | — |
| Gas Boiler Repair | $0.00 | no spend, no leads | — | — |

**The AC Repair campaign is the largest line item in the account and is underwater on revenue alone
— before any close rate or margin.** It spent $2,550.59 to generate roughly $1,298 of top-line
pipeline. Even at a 100% close rate it returns 51 cents on the dollar. A repair ticket averages
~$319; the campaign's CPQL is ~$978. **The lead costs three times the job.**

Meanwhile Installation + Replacement spent $2,627.05 combined and produced the three leads carrying
94% of the pipeline — a 9.5 : 1 ratio at full close, roughly 3 : 1 at a realistic 30% close rate.

HVAC Repair spent $1,665.16 in August with no qualified lead traceable to it.

---

## 6. What this changes

1. **The budget split is inverted relative to the economics.** AC Repair holds $141.45/day — the
   largest of the five — for the lowest-value job type. Installation and Replacement hold $176.15
   and $20.00 for the job types carrying 94% of the value. **HVAC Replacement is at $20.00/day.**
2. **Repair-intent keywords cannot clear a ~$978 CPQL.** No bid change fixes that; the arithmetic
   of a $319 job forbids it. Repair campaigns need a much lower CPQL to work, which means cheaper
   clicks or a far better conversion rate — not more bid.
3. **This sharpens the CPC-ceiling plan.** `AMB-0915-CPC-HR-1` proposes $25 → $65 on **HVAC
   Repair**, which produced zero traceable qualified leads in August and sells low-ticket work.
   On this evidence **HVAC Installation or HVAC Replacement is the better first bid test.** I am
   not silently swapping the target — the existing plan stands as approved-pending — but I would
   recommend re-pointing it, and I can issue a superseding plan on your word.
4. **Nothing here is a profitability verdict** until Ambient supplies real job values, close rate
   and gross margin. Swap the four midpoints for Ambient's own and every number above recomputes.

---

## 7. Still missing

| Input | Effect |
|---|---|
| Ambient's average AC repair ticket | replaces the $319 benchmark |
| Ambient's average replacement / installation job | replaces the $8,300 benchmark |
| Close rate on quoted replacement work | turns pipeline into booked revenue |
| Gross margin % | turns revenue into profit after ad spend |
| Whether `quotable = Yes` means *quoted* or *sold* | the whole model hinges on this definition |

`quote_value` and `sales_value` are empty on all 294 leads and no CRM webhook is configured
(`CRM_WEBHOOK_URL` is blank), so none of this can be read from a system — it has to come from
Ambient.

**Sources for the market benchmarks:**
[Angi — HVAC repair cost](https://www.angi.com/articles/how-much-hvac-repair-cost.htm) ·
[HomeGuide — HVAC repair cost](https://homeguide.com/costs/hvac-repair-cost) ·
[RealCostIQ — Baltimore HVAC replacement](https://realcostiq.com/cost-guides/hvac-replacement/baltimore-md/) ·
[HomeScore — Maryland HVAC replacement](https://myhomescore.app/costs/hvac/maryland) ·
[hvacprojectcost — Maryland HVAC replacement](https://hvacprojectcost.com/hvac-replacement-cost-maryland/) ·
[Angi — ductwork repair cost](https://www.angi.com/articles/ductwork-repair-cost.htm) ·
[HomeGuide — ductwork replacement](https://homeguide.com/costs/cost-to-replace-ductwork)
