# Ambient Cooling - Live | 2401959466
# Heating Services — historical research, Keyword Planner strategy, service selection

| | |
|---|---|
| **Data retrieved** | 2026-09-16, America/New_York |
| **Account timezone** | America/New_York |
| **Latest fully settled data date** | **2026-09-15** (2026-09-16 is PARTIAL and never mixed into a settled comparison) |
| **Mode** | READ + DRAFT |
| **External writes** | **ZERO** — no mutate, no `validate_only`, no Google Ads / WhatConverts / GTM / website / Drive change |
| **Campaign created or enabled** | **NONE** |

**Sources read:** repository `CLAUDE.md`; populated `client.yaml` and `work-order.yaml`;
`LANDING_PAGE_CONTENT_WORKFLOW.md`; prior Ambient reports, plans, receipts and snapshots;
live Google Ads API (all 33 campaigns, every status, 2019-01-01 → 2026-09-15); Keyword Planner
via `KeywordPlanIdeaService.GenerateKeywordHistoricalMetrics`; WhatConverts API (read-only,
profile 105803); the official Ambient website in a real browser.

**Sources unavailable:** Auction Insights (not exposed by the API for this account — needs a
manual UI export); Ambient's average job revenue, close rate and gross margin (still null);
`quote_value` / `sales_value` (0 of every lead); CRM webhook (unconfigured).

---

## 1. Identity gate — PASS

`Ambient Cooling - Live | 2401959466 | heating-service portfolio research`

10/10 checks: name exact · id exact (child, **not** the Green Marketing MCC `3373711342`) ·
manager=false · test=false · ENABLED · USD · America/New_York · `- live` present ·
GM manager ACTIVE · ClickCease manager ACTIVE.

---

## 2. Existing state reverified — every figure confirmed

| Claim | Reverified | Result |
|---|---|---|
| Monthly Search cap $13,000 | policy | held |
| Max combined daily $427.63 | $13,000 ÷ 30.4 | **$427.63** ✓ |
| Combined daily $421.55 | live budgets | **$421.55** ✓ |
| Monthly equivalent $12,815.12 | ×30.4 | **$12,815.12** ✓ |
| Headroom ~$184.88 | | **$184.88/month = $6.08/day** ✓ |
| August five-campaign spend $6,842.80 | API | **$6,842.80** ✓ |
| August other paid spend $0.00 | API | **$0.00** ✓ — August remains the clean window |
| AC Repair $2,550.59 · HVAC Install $2,474.53 · HVAC Replace $152.52 · HVAC Repair $1,665.16 · Gas Boiler $0.00 | API | all ✓ |

**September decline, exact before/after:**

| Window | Days | Spend | Per day | Impressions | Clicks |
|---|---:|---:|---:|---:|---:|
| Sep 1–4 (pre-cap) | 4 | $1,215.78 | **$303.94** | 858 | 18 |
| Sep 5–15 (post-cap) | 11 | $303.10 | **$27.55** | 685 | 12 |

Spend per day fell **90.9%** across the 2026-09-04 16:56 CPC-ceiling boundary. Against $421.55
available, Sep 5–15 ran at 6.5% of budget. Lost impression share moved to rank, not budget.

> **Causation language.** The timing alignment is exact and the mechanism is understood, but
> this is an observational before/after on a live account, not a controlled experiment. I state
> it as **strongly supported**, not proven-by-experiment.

**Plans not replayed.** `AMB-0915-COMM-RSA-1 / 6C32B210CF5B` and
`AMB-0915-COMM-ASSET-1 / 02F6EECCCDF8` remain executed-and-paused; the 17 commercial negatives
remain executed. Nothing was re-run.

**`AMB-0915-CPC-HR-1 / 14BD03817042` → `SUPERSEDED — DO NOT EXECUTE`.** It proposed raising HVAC
Repair $25 → $65. The August economics withdraw its basis: HVAC Repair spent $1,665.16 with zero
traceable qualified leads, and it sells the lowest-ticket work in the account.

---

## 3. Historical heating research — the account has done this before

**15 heating-relevant campaigns exist**, all but one paused or removed. Combined history:
**$108,464.01 spent · 422,594 impressions · 7,251 clicks · 211.8 conversions · $14.96 avg CPC.**

| Campaign | Status | Spend | Clicks | Avg CPC | Conv | **CPA** |
|---|---|---:|---:|---:|---:|---:|
| **Heating Repair** | PAUSED | $17,445.53 | 930 | $18.76 | 69.0 | **$252.83** |
| Heating Maintenance | PAUSED | $7,435.88 | 289 | $25.73 | 23.3 | $318.68 |
| Heating & Boiler Repair – Calls | REMOVED | $4,687.59 | 54 | $86.81 | 14.0 | $334.83 |
| Heating Installation (#2) | REMOVED | $6,146.15 | 397 | $15.48 | 14.0 | $439.01 |
| **Heating Installation** | PAUSED | $16,996.43 | 1,032 | $16.47 | 33.0 | **$515.04** |
| Leads-PMax-Furnace-Repair | PAUSED | $4,930.57 | 3,232 | $1.53 | 8.0 | $616.32 |
| Gas Boilers Repair | PAUSED | $6,383.12 | 71 | $89.90 | 9.0 | $709.24 |
| Mini Split | PAUSED | $22,183.67 | 882 | $25.15 | 28.5 | $778.38 |
| Gas Boilers Installs | PAUSED | $9,436.70 | 89 | $106.03 | 11.0 | $857.88 |
| Geothermal HVAC | PAUSED | $151.80 | 4 | $37.95 | 0.0 | — |
| Water Source Heat Pump | REMOVED | $134.80 | 3 | $44.93 | 0.0 | — |
| **Tankless Water Heaters** | PAUSED | $12,531.77 | 268 | $46.76 | 2.0 | **$6,265.89** |

> **Attribution confidence: PROBABLE.** These conversion counts come from the account's historical
> Google Ads configuration, which we know carries up to 10 Primary actions and duplicates a single
> lead. Treat the **CPA ranking** as reliable and the **absolute CPA values** as upper bounds.
> They are not reconciled unique WhatConverts leads.

**Two findings reframe the heating opportunity:**

1. **Generic furnace/heating intent is cheap here.** Heating Repair ran at **$18.76** and Heating
   Installation at **$16.47** across 1,962 combined clicks. Compare the live cooling campaigns:
   AC Repair $106.37 and HVAC Repair $67.31 all-time.
2. **Specialty heating is punishing.** Boiler ($89.90–$106.03), tankless ($46.76 → $6,265.89 CPA)
   and geothermal (zero conversions) each burned money.

**Seasonality in the account's own spend** (Search + PMax, 2023-09 → 2026-09): CPC climbs sharply
in the cold months — Nov 2025 $78.20, Dec 2025 $89.73, Jan 2026 $61.13 — versus $15–$25 in summer.
Budget and ceiling planning must anticipate that premium.

**Last heating season (2025-10-01 → 2026-03-31):** $38,719.25 across 2,586 clicks and 43
conversions. Search-only was $34,846.26 for 593 clicks (**$58.76 CPC**), dominated by the expensive
boiler and tankless campaigns.

**Top historical heating keywords by spend** (all statuses): `tankless water heater for home`
$9,764.09/1 conv · `boiler repair service` $5,937.82/3 · `gas boiler service` $4,688.13/5 ·
**`heat pump installers near me` $4,099.25 at $12.65 CPC / 11 conv** · `oil furnace service near me`
$3,585.60/5 · `heating and cooling repair near me` $2,266.41/7.5 · `residential heating repair`
$2,119.86/4 · `furnace repair` $1,014.58 at $32.73 / 5 conv.

Full exports: `exports/heating-history-2026-09-16.json`, `…-search-terms-…csv`,
`…-keywords-…csv`.

---

## 4. WhatConverts heating analysis — read-only, no PII retained

Trailing 12 months (2025-09-16 → 2026-09-15): **1,662 leads total; 311 carry heating intent;
53 of those are paid search; 98 are qualified (`quotable = Yes`).**

| Cluster | All leads | Paid | **Qualified** |
|---|---:|---:|---:|
| **Heat pump** | 52 | 5 | **21** |
| **Mini split / ductless** | 36 | 4 | **15** |
| **Heating repair (generic)** | 43 | 4 | **13** |
| **Furnace repair** | 44 | 4 | **11** |
| Heating maintenance / tune-up | 23 | 3 | 10 |
| **Boiler** | 35 | **20** | **8** |
| Thermostat | 34 | 2 | 6 |
| Heating install / replace | 11 | 2 | 5 |
| Water heater / tankless | 8 | 3 | 4 |
| Furnace install / replace | 13 | 2 | 3 |
| Geothermal | 12 | 4 | 2 |

**Heat pump + mini-split = 36 of 98 heating qualified leads (37%)** — the largest cluster by a
wide margin.

**Boiler is the warning.** It took **20 paid leads — more than any other heating cluster — and
converted only 8 to qualified (40%)**, the worst qualification rate among the significant clusters,
at a $89.90–$106.03 historical CPC. Expensive clicks, poor qualification.

**Heating lead seasonality, all channels:**
Sep 10 → **Oct 28 → Nov 25 → Dec 57 → Jan 34 → Feb 31** → Mar 18 → Apr 32 → May 27 → Jun 16 →
Jul 21 → Aug 7. The ramp starts in **October** and peaks in **December**.

> **`quotable = Yes` remains UNRESOLVED.** WhatConverts documents it as a lead-quality flag, and
> `quote_value` and `sales_value` are empty on every one of the 294/1,662 leads inspected. Nothing
> in the data proves whether `Yes` means *quoted*, *qualified* or *sold*. Every CPQL here is
> labelled accordingly. **No repair lead is credited with later replacement revenue** — no recorded
> lead or CRM outcome links them.

Attribution confidence for the paid subset: **AMBIGUOUS to PROBABLE.** WhatConverts labels a lead
`google/cpc` without naming the campaign, and the form-cache defect (section 8) means click IDs are
unreliable.

---

## 5. Current local Keyword Planner research

**Settings:** Google Search only · English (`languageConstants/1000`) · USD · Presence · live geo
constants from customer 2401959466 · `GenerateKeywordHistoricalMetrics` · retrieved 2026-09-16.

### Geo crosswalk — overlap controlled

All five live campaigns share an **identical 75-target** set:

| Target type | Count |
|---|---:|
| City | 28 |
| Neighborhood | 5 |
| Postal Code | 42 |

**Containment check: ZERO of the 75 sit inside another targeted area.** Every target is a peer, so
nothing is double-counted by inclusion.

The Planner caps `geo_target_constants` at **10 per request**. The batch used is 10 peer CITY-level
targets with zero containment between them: Annapolis · Glen Burnie · Ellicott City · Severn ·
Severna Park · Bowie · Laurel · Catonsville · Odenton · Arnold.

> **These figures are a SAMPLE of the service area, not the whole-area total.** They are not scaled
> by 75/10 and they are not summed across areas. Synonyms also share a single volume bucket, so
> summing rows overstates demand. Full crosswalk: `exports/geo-crosswalk-2026-09-16.csv`.

### Demand and bids (10-city sample, avg monthly searches)

| Keyword | Avg/mo | Competition | TOP low | TOP high |
|---|---:|---|---:|---:|
| **furnace repair** | **320** | LOW | — | — |
| furnace repair near me | 140 | LOW | — | — |
| **heat pump repair** | **140** | LOW | — | — |
| heating repair near me | 70 | LOW | — | — |
| furnace installation near me | 70 | LOW | — | — |
| furnace maintenance | 70 | LOW | — | — |
| heat pump installation | 50 | LOW | — | — |
| ductless mini split installation | 40 | LOW | — | — |
| thermostat repair | 40 | LOW | — | — |
| furnace installation / furnace replacement cost / furnace tune up / boiler repair / thermostat replacement | 30 | LOW–MED | — | — |
| new furnace cost | 20 | HIGH | **$4.55** | **$9.41** |
| mini split installation | 20 | HIGH | **$4.01** | **$31.91** |
| thermostat installation | 10 | HIGH | **$31.15** | **$112.34** |

**Data limitation, stated plainly:** Google returned top-of-page bid estimates for only **4 of 64**
heating keywords in this geography — volumes are too low for the rest. Every bid recommendation
below therefore leans on **actual account auction history**, with Planner used as a competition
signal only. Recommendations resting on Planner bids alone are marked provisional.

### Seasonality — the reason to act in October

| Keyword | Sep | Oct | Nov | Dec | **Jan** | Feb | Mar |
|---|---:|---:|---:|---:|---:|---:|---:|
| **furnace repair** | 110 | 320 | 390 | 590 | **720** | 480 | 260 |
| **heat pump repair** | 40 | 90 | 140 | 390 | **480** | 260 | 90 |
| furnace repair near me | 170 | 170 | 50 | 210 | **320** | 260 | 170 |
| furnace maintenance | 20 | 90 | 90 | 140 | **170** | 140 | 70 |
| furnace installation near me | 90 | 70 | 20 | 110 | **110** | 90 | 70 |

`furnace repair` swings **6.5× from September to January**. Today is 2026-09-16 — the ramp begins
in roughly two weeks.

Exports: `exports/keyword-planner-heating-2026-09-16.json` (raw micros preserved) and `.csv`.

---

## 6. Candidate normalization — 33 candidates → 3 Tier A clusters

Full table: `exports/heating-candidate-normalization-2026-09-16.csv`. The merges that matter:

| Merged | Into | Why |
|---|---|---|
| Furnace maintenance + furnace tune-up + heating maintenance + heating tune-up + heating system inspection | **Heating Maintenance** (Tier B) | One bucket, one technician visit, one page. Planner treats them as synonyms. |
| Ductless mini-split installation + mini-split installs + ductless heating installation | **Heat Pump & Ductless** | Ambient's own heat-pump page names ductless mini-splits as a heat-pump type. |
| Heat pump installation + replacement + repair | **Heat Pump & Ductless** | One dedicated page covers all three; buyer arrives with "my heat pump" not "my heat pump repair". |
| Heating replacement + heating-system replacement + heating installation + heating-system installation + furnace installation + furnace replacement | **Heating Installation & Replacement** | Install and replace are the same purchase decision — both end in a quote for a new system. |
| Heating repair + no-heat repair + furnace repair + gas-furnace repair | **Furnace & Heating Repair** | Same urgency, same visit, same page. Fuel type is a qualifier, not a separate decision. |
| Boiler installation + replacement | **Boiler** (Tier B) | Kept with boiler repair under the EXISTING campaign. |

**Kept separate:** Repair vs Installation/Replacement — materially different intent, ticket size,
page and CTA. **Heat Pump & Ductless** separated from generic heating because it is the largest
qualified-lead cluster and has its own dedicated page and year-round relevance.

---

## 7. Service selection

Full scorecard with every metric: `exports/heating-profitability-scorecard-2026-09-16.csv`.
Scoring weights were fixed **before** the ranking was produced: verified capability (gate),
expected gross profit per qualified lead (35%), qualified-lead evidence (25%), local BOFU demand
(15%), CPC/CPQL feasibility (15%), landing-page and routing readiness (10%).

### TIER A — 3 ad groups, launch in this order

| # | Cluster | Capability | Demand (10-city) | Hist. CPC | Hist. CPA | WC qualified 12mo | Confidence |
|---|---|---|---:|---:|---:|---:|---|
| 1 | **Furnace & Heating Repair** | dedicated page | 460/mo, Jan 720 | **$18.76** | **$252.83** | 24 | HIGH |
| 2 | **Heat Pump & Ductless** | dedicated page ×2 | 260/mo, Jan 480 | $25.15 | $778.38 | **36** | HIGH |
| 3 | **Heating Installation & Replacement** | dedicated page ×2 + 8 pages | 200/mo | **$16.19** | $492.40 | 8 | MED-HIGH |

Why these three: every one has a **dedicated Ambient page**, real local BOFU demand, LOW
competition, a workable historical CPC, and enough budget at the proposed split to produce useful
learning. Installation/replacement is included on priority despite lower search volume because the
August cooling analysis proved install/replace intent carried **93.9%** of pipeline value.

### TIER B — reserve, controlled later test

| Cluster | Why not now |
|---|---|
| **Heating Maintenance** | $318.68 historical CPA is respectable, but a ~$165 tune-up ticket cannot carry it. Viable only as a loss-leader into replacement — and we have **no proof** that repair/maintenance leads convert into replacement revenue. Excluded on that basis, not on demand. |
| **Boiler** | $98.87 blended historical CPC and the **worst qualification rate of any heating cluster (8 of 20 paid)**. An **ENABLED** Gas Boiler Repair campaign `24132507744` already exists — Tier B action is to raise *its* budget in peak season, never to build a second boiler structure. |
| **Oil Furnace** | Genuinely differentiated (two dedicated pages) and oil is common in older Anne Arundel housing, but only ~30/mo demand and $74–$87 CPC on oil terms. Revisit once the Tier A groups have settled data. |

### HOLD / EXCLUDE

| Service | Verdict | Reason |
|---|---|---|
| Thermostat repair / replacement / smart thermostat install | **HOLD — CAPABILITY NOT VERIFIED** | 80/mo demand exists, but **no thermostat service appears anywhere on the Ambient website**. We do not advertise what we cannot verify. |
| Electric furnace repair | **HOLD — CAPABILITY NOT VERIFIED** | No site evidence, no Planner volume. |
| Emergency heating repair | **HOLD — BARRED CLAIM** | `client.yaml` bars `same_day_or_emergency_availability`. The approved schedule ends 20:00 and excludes Sunday, so a 24/7 promise would be untrue. |
| Heating system inspection | merged | Same job as a tune-up. |
| **Water heater / tankless** | **EXCLUDE** | $12,531.77 for **2** conversions — a **$6,265.89 CPA**, eight times worse than anything else in the account. Also not an HVAC heating service. |
| **Geothermal** | **EXCLUDE** | $286.60 across two campaigns, **zero** conversions, no meaningful local volume. |

---

## 8. Heating Services campaign strategy — designed, **not created**

**Requested label:** `HEATING SERVICES`
**Proposed exact name:** `Search | NonBrand | Heating Services | Central MD | BOFU | 2026-10`
**Reason:** matches the existing five-campaign convention so reporting filters and plan lineage stay
consistent.

**Settings:** Search only · Google Search on · **Search Partners off** · Display expansion off ·
AI Max off · DSA off · automatically created assets off · text customization off · Final URL
expansion off · **Phrase + Exact only, no Broad** · **Presence** targeting · inherit the verified
75 Central MD targets · schedule **Mon–Fri 08:00–20:00 + Sat 08:00–13:00, no Sunday** (identical to
the five live campaigns; **no overnight advertising** — Ambient cannot answer and qualify those
leads).

**Bidding: Maximize Clicks with a $45.00 CPC ceiling.** Not Maximize Conversions or tCPA — the
account has no reliable qualified-conversion volume, and the measurement defect in section 10 makes
conversion-based bidding actively unsafe.

**The $45 is derived, not arbitrary.** The cooling campaigns' $25/$30 ceilings were set by hand and
this plan does not reuse them. Heating Repair ran at **$18.76** average CPC and Heating Installation
at **$16.47** across 1,962 real clicks; Planner shows LOW competition on nearly every heating term.
$45 is ≈2.4× the historical average, leaving headroom for the December–January premium (historical
Nov–Jan CPC reached $78–$90) without reopening uncapped bidding.

### Ad groups, keywords and budget share

**1. `SKAG | Furnace & Heating Repair`** — 45% share — launch first
Final URL `https://offer.ambientcoolingandheating.com/furnace-heating-repair/`
H1 `Furnace & Heating Repair in Central Maryland`
*Phrase:* `furnace repair` · `furnace repair near me` · `heating repair near me` ·
`heating system repair` · `gas furnace repair` · `furnace not working` · `heating repair` ·
`no heat repair`
*Exact:* `[furnace repair]` · `[furnace repair near me]` · `[heating repair near me]` ·
`[heating repair]`
Expected CPC $16 / **$25** / $40 (low/base/high) · Confidence HIGH

**2. `SKAG | Heat Pump & Ductless`** — 35% share — launch second
Final URL `https://offer.ambientcoolingandheating.com/heat-pump-mini-split/`
H1 `Heat Pump & Ductless Mini-Split Service in Central Maryland`
*Phrase:* `heat pump repair` · `heat pump repair near me` · `heat pump installation` ·
`heat pump replacement` · `ductless mini split installation` · `mini split installation` ·
`ductless heating installation`
*Exact:* `[heat pump repair]` · `[heat pump installation]` · `[mini split installation]` ·
`[ductless mini split installation]`
Expected CPC $13 / **$25** / $45 · Confidence HIGH

**3. `SKAG | Heating Installation & Replacement`** — 20% share — launch third
Final URL `https://offer.ambientcoolingandheating.com/furnace-installation-replacement/`
H1 `Furnace Installation & Replacement in Central Maryland`
*Phrase:* `furnace installation` · `furnace installation near me` · `furnace replacement` ·
`new furnace installation` · `heating system installation` · `heating system replacement` ·
`oil furnace installation`
*Exact:* `[furnace installation]` · `[furnace replacement]` · `[furnace installation near me]` ·
`[heating system replacement]`
Expected CPC $15 / **$22** / $40 · Confidence MEDIUM-HIGH

### Expected performance per ad group (October test allocation)

| Ad group | Monthly budget | Base CPC | Clicks | Leads @6% | Qualified @50% | CPL | **CPQL** | Days to 1st qualified lead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Furnace & Heating Repair | $1,510 | $25 | ~60 | ~3.6 | ~1.8 | ~$419 | **~$839** | ~17 |
| Heat Pump & Ductless | $1,175 | $25 | ~47 | ~2.8 | ~1.4 | ~$419 | **~$839** | ~21 |
| Heating Install & Replace | $671 | $22 | ~31 | ~1.8 | ~0.9 | ~$372 | **~$745** | ~33 |

> Ranges, not guarantees. The 6% click-to-lead and 50% qualification rates are taken from the
> account's own measured paid-search performance (14 paid leads from ~230 August clicks;
> 52.6% qualification). Both are **upper-bound-contaminated** by the tracking defect. The
> historical heating CPAs ($252.83 repair, $492.40 install) suggest the real outcome could be
> materially better than this conservative model — Heating Repair historically delivered a
> conversion every $252.83.

### Negatives and routing — every term reviewed individually

**No one-word BROAD negatives.** Never negatived: `near me` · `quote` · `price` · `pricing` ·
`cost` · `best` · `hire` · `local` · `emergency` · `company` · `companies` · `contractor` ·
`contractors`.

*Campaign-level PHRASE negatives on Heating Services:* `air conditioning repair` · `ac repair` ·
`ac installation` · `water heater` · `tankless water heater` · `hot water heater` · `geothermal` ·
`pool heater` · `hvac school` · `hvac training` · `hvac jobs` · `hvac salary` · `furnace filter` ·
`furnace parts` · `diy furnace` · `used furnace` · `furnace manual` · **`boiler`** (the existing
Gas Boiler campaign owns that intent).

*Cross-negatives into existing campaigns* (PHRASE, so legitimate buyer intent is not blocked):

| Campaign | Add PHRASE negative | Reason |
|---|---|---|
| HVAC Repair `24132507750` | `furnace repair`, `heating repair` | route to the new heating group |
| HVAC Installation `24132507747` | `furnace installation`, `heat pump installation` | route to heating |
| HVAC Replacement `24132507753` | `furnace replacement` | route to heating |

---

## 9. Budget — three views, all at or under $13,000

**The cap is absolute: $13,000/month, $427.63 max combined daily. Heating is funded by
reallocation, never addition.**

### View 1 — current, pre-heating

| Campaign | Daily | Monthly |
|---|---:|---:|
| HVAC Installation | $176.15 | $5,354.96 |
| AC Repair | $141.45 | $4,300.08 |
| HVAC Repair | $78.95 | $2,400.08 |
| HVAC Replacement | $20.00 | $608.00 |
| Gas Boiler Repair | $5.00 | $152.00 |
| **Total** | **$421.55** | **$12,815.12** |

### View 2 — initial heating test (October)

| Campaign | From | To | Δ | Reason | Stop-loss |
|---|---:|---:|---:|---|---|
| **AC Repair** | $141.45 | **$70.00** | −$71.45 | August proved **0.51:1** on revenue alone — $2,550.59 for ~$1,298 pipeline. Largest budget, weakest economics. Cooling demand falls from October. | restore if qualified leads hit zero for 14 settled days while IS holds |
| **HVAC Repair** | $78.95 | **$40.00** | −$38.95 | $1,665.16 in August, **zero** traceable qualified leads. QS 2, below-average LP experience. | n/a — not currently producing |
| HVAC Installation | $176.15 | $176.15 | $0 | **Unchanged.** Best performer, carries the commercial ad group. | n/a |
| HVAC Replacement | $20.00 | $20.00 | $0 | Unchanged. High ticket, minimal spend. | n/a |
| Gas Boiler Repair | $5.00 | $5.00 | $0 | Unchanged. Designated boiler route; do not duplicate. | n/a |
| **Heating Services (NEW)** | $0.00 | **$110.40** | +$110.40 | Exactly the sum of the two cuts. Splits 45/35/20. | $450 incremental per ad group with zero qualified lead |
| **Total** | **$421.55** | **$421.55** | **$0** | | |

Heating share: **$3,356.16/month.**

### View 3 — colder season (November–February)

| Campaign | From | To | Δ | Reason |
|---|---:|---:|---:|---|
| AC Repair | $70.00 | $40.00 | −$30.00 | Cooling troughs Nov–Feb |
| HVAC Repair | $40.00 | $30.00 | −$10.00 | Keep a year-round floor only |
| HVAC Installation | $176.15 | $130.00 | −$46.15 | Reduced winter level; retains commercial |
| HVAC Replacement | $20.00 | $20.00 | $0 | Unchanged |
| **Gas Boiler Repair** | $5.00 | **$15.00** | +$10.00 | **Tier B expansion of the EXISTING campaign** in peak boiler season |
| **Heating Services** | $110.40 | **$186.55** | +$76.15 | Planner: furnace repair 720/mo in January vs 110 in September |
| **Total** | **$421.55** | **$421.55** | **$0** | |

Heating share: **$5,671.12/month.** **Cooling is never switched off** — it retains $220.00/day
(52%) through the winter.

---

## 10. Seasonal transition — triggers, not the calendar

**Signals:** Planner monthly seasonality (furnace repair 6.5× Sep→Jan) · WhatConverts heating leads
(Sep 10 → Oct 28 → Dec 57) · current 7/14-day search-term mix · qualified leads and CPQL ·
impression share and lost-IS(rank) · local temperature as a **secondary** signal only ·
Ambient's staffing.

| Trigger | Condition | Action |
|---|---|---|
| **Begin the heating test** | All section 11 measurement gates pass **AND** heating search terms appear in the existing campaigns **or** the date reaches 2026-10-01 | Enable Heating Services at $110.40/day |
| **Increase heating budget** | ≥2 verified qualified heating leads within 21 days **AND** CPQL ≤ $500 **AND** lost-IS(budget) > 15% | Move to View 3 |
| **Reduce cooling** | Cooling qualified leads fall ≥50% versus the trailing 14 settled days **AND** heating is budget-constrained | Apply the View 3 cooling cuts |
| **Keep cooling active** | Always — cooling never drops below $220.00/day | Hard floor |
| **Pause a heating ad group** | $450 incremental spend, zero verified qualified lead, ≥30 clicks | Pause that ad group only |
| **Expand a Tier B service** | A Tier A group hits CPQL ≤ $400 with ≥3 qualified leads and is budget-limited | Fund Boiler via the existing campaign, or Heating Maintenance |
| **Stop-loss** | Any ad group exceeds $450 incremental with no qualified lead | Pause and review |

All stop-losses are **qualified-lead and economic**, never click counts.

---

## 11. Measurement prerequisites — the real blocker

**No heating campaign may be recommended for launch until every item passes:**

| # | Gate | Status |
|---|---|---|
| 1 | SiteGround cache defect corrected | **OPEN** — `AMB-0915-LP-1 / 5354E1E2F576` awaiting approval |
| 2 | 24/24 fresh loads capture their own click IDs | **OPEN** — currently **0/24** |
| 3 | GCLID/GBRAID/WBRAID/UTMs persist through submission | **OPEN** |
| 4 | Unique lead IDs working | **OPEN** |
| 5 | Duplicate conversion actions resolved | **OPEN** — `AMB-0915-CONV-1 / 981A790ACDBB` awaiting approval |
| 6 | One approved submission = exactly one conversion | **OPEN** |
| 7 | Call tracking verified | **PARTIAL** — paid calls fragment across 3 numbers |
| 8 | Primary/secondary conversions separated | **OPEN** — 10 Primary today |
| 9 | WhatConverts reconciliation complete | **DONE** 2026-09-15 |
| 10 | Landing pages return HTTP 200 | **NOT BUILT** — the 3 heating pages do not exist |
| 11 | Mobile + desktop QA passes | pending build |
| 12 | Privacy + Terms present | template requirement |
| 13 | Ads pass policy review | pending |
| 14 | Keywords eligible | pending |
| 15 | Budget reallocation approved | `AMB-0916-HEAT-BUDGET-1 / 54613304B752` |
| 16 | Create-paused plan approved | not yet drafted — depends on pages existing |
| 17 | Readback QA passes | pending |
| 18 | Enablement separately approved | pending |

**Honest sequencing consequence:** gates 1–8 belong to the *cooling* remediation already awaiting
approval. **Heating cannot launch before that work ships.** Given the October ramp, the critical
path is `AMB-0915-LP-1` — every week it waits costs heating season.

Offline outcomes should later use the **Google Data Manager API**; not implemented here.

---

## 12. Deliverables produced

| Deliverable | Path |
|---|---|
| This report | `reports/ambient-cooling-heating/2026-09-16-heating-services-research-and-strategy.md` |
| Historical heating export | `clients/ambient-cooling-heating/exports/heating-history-2026-09-16.json` + 2 CSVs |
| Keyword Planner export | `…/exports/keyword-planner-heating-2026-09-16.json` + `.csv` (raw micros preserved) |
| Geo crosswalk | `…/exports/geo-crosswalk-2026-09-16.csv` |
| Candidate normalization | `…/exports/heating-candidate-normalization-2026-09-16.csv` |
| Profitability scorecard | `…/exports/heating-profitability-scorecard-2026-09-16.csv` |
| Capability verification | `…/snapshots/heating-capability-browser-2026-09-16.json` |
| Identity + baseline | `…/snapshots/heating-identity-baseline-2026-09-16.json` |
| Composite research manifest | `…/work-orders/work-order-heating-research-manifest.yaml` |
| 3 service-specific work orders | `…/work-orders/work-order-{heating-repair,heat-pump,heating-installation}.yaml` |
| Landing-page content packages | `reports/ambient-cooling-heating/2026-09-16-heating-landing-page-drafts.md` |
| RSA + asset drafts | `reports/ambient-cooling-heating/2026-09-16-heating-rsa-and-asset-drafts.md` |
| Strategy plan | `…/plans/AMB-0916-HEAT-STRATEGY-1.json` |
| Budget plan | `…/plans/AMB-0916-HEAT-BUDGET-1.json` |

All 6 work orders validate:
```
PASS | Heating Repair      PASS | Heat Pump Installation
PASS | Heating Installation  PASS | Heating Repair (research manifest)
PASS | AC Repair (existing)  PASS | Commercial HVAC Installation (existing)
```

---

## 13. Missing client economics

| Input | Status | What it unblocks |
|---|---|---|
| Average job revenue — furnace repair | **MISSING** | whether repair clears its CPQL |
| Average job revenue — furnace/heat-pump replacement | **MISSING** | break-even CPQL for Tier A #2 and #3 |
| Qualified-to-sale close rate | **MISSING** | gross profit per qualified lead |
| Gross margin % | **MISSING** | profit after ad spend |
| Definition of `quotable = Yes` | **UNRESOLVED** | whether 98 qualified heating leads are quotes or sales |
| Does Ambient service thermostats? | **MISSING** | releases 80/mo of held demand |
| Does Ambient service electric furnaces? | **MISSING** | releases held demand |

Provisional control limits (**not proven profit targets**): AC Repair $150 · HVAC/Boiler Repair
$250 · Installation/Replacement/Commercial $280. **August's $977.54 new-business CPQL is a baseline,
not a target.**

Recommendations that depend on missing economics: the Tier B verdict on Heating Maintenance (a
verified tune-up ticket could change it), and the final CPQL guardrail for each Tier A group.
Recommendations that do **not** depend on them: all three Tier A selections, the exclusions, the
budget reallocation, and the $45 ceiling — each rests on measured account data.

---

## 14. Future approvals — separate stages, do not combine

```
1  STRATEGY          APPROVE AMB-0916-HEAT-STRATEGY-1 9EC0CE017DE7 strategy FOR 2401959466
2  LANDING CONTENT   (fingerprint issued when the 3 page packages are signed off)
3  LANDING DEPLOY    (separate; requires staging, diff, backup, rollback)
4  CREATE-PAUSED     (drafted only after the pages return HTTP 200)
5  BUDGET REALLOC    APPROVE AMB-0916-HEAT-BUDGET-1 54613304B752 6 operations FOR 2401959466
6  READBACK QA       (no approval line — a verification step)
7  ENABLEMENT        (separate approval after policy approval and readback)
```

**Nothing above was executed.** Any later change to the account, service, budget, locations,
schedule, URLs, keywords, negatives, ads, assets or landing-page copy produces a **new fingerprint**.

### Do not execute
`AMB-0915-CPC-HR-1 14BD03817042` — **SUPERSEDED**, basis withdrawn by the August economics ·
`AMB-0910-COMM-RSA-2 41C183D15C93` · `AMB-0910-RSA-ACR-2 1F166DE17017` ·
`AMB-0910-COMM-NEG-1 C4142D5D5DE0` · `AMB-0910-COMM-NEG-1-FULL A774B9C14896` ·
`AMB-0910-COMM-NEG-2 A9C9BCBDDD74` · `AMB-0910-RSA-ACR-1 19E2F2FFC311` ·
`AMB-0910-COMM-RSA-1 30312BC45992` · `AMB-0909C-CPC-INST-2 5D57E0EF3B70`

---

## 15. Assumptions and confidence

| Assumption | Confidence | If wrong |
|---|---|---|
| Historical heating CPAs rank clusters correctly | MEDIUM-HIGH | absolute values are upper bounds; ranking is what drives the decision |
| 6% click-to-lead, 50% qualification carry to heating | MEDIUM | taken from cooling; heating intent is more urgent, so likely conservative |
| Planner LOW competition reflects the real auction | MEDIUM | only 4 of 64 keywords returned bids; account history is the primary bid basis |
| The 10-city sample represents the 75-target area | MEDIUM-HIGH | peer CITY targets, zero containment; never scaled up |
| Heating demand ramps from October | HIGH | two independent sources agree — Planner and WhatConverts |
| `quotable = Yes` approximates a qualified lead | LOW-MEDIUM | **UNRESOLVED**; would change every CPQL |

**Forecasts are estimates, not guaranteed results. Nothing here claims Ambient is profitable —
that requires sold revenue and gross margin the account does not hold.**
