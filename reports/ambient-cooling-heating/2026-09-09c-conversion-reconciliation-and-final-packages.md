# Ambient Cooling — Conversion Reconciliation and Final Replacement Packages

**Account:** Ambient Cooling - Live · **Customer ID:** 2401959466
**Run:** 2026-09-09, third pass · **Mode:** READ + ANALYZE + DRAFT + VALIDATE-ONLY
**Mutations executed: 0.** No IP exclusion, network, device, schedule, location, budget, bid,
keyword, negative, ad or conversion action was changed.

> Supersedes the package set in `2026-09-09b-audit-correction-and-replacement-packages.md`.
> Both earlier reports are preserved unmodified.

**Identity gate:** six fields PASS. Manager links 3373711342 and 2815082755 both ACTIVE.
Account clock from the API: **2026-09-09 is partial** (82 impressions, $58.63); **latest settled
date is 2026-09-08**, used throughout. Concurrent-writer check PASS — the two running Python
processes belong to `carbon-b2b`, target different customer IDs and contain zero `mutate` calls.

---

## 1. Exact Primary versus All-conversion reconciliation

Daily rows 2026-08-18 → 2026-09-08, segmented **simultaneously** by date × campaign ID/name ×
conversion action ID/name. 47 rows returned. The two columns are reported separately and are
never summed together.

```
TOTAL metrics.conversions      = 14.00
TOTAL metrics.all_conversions  = 75.00
```

### 1.1 Per-action totals, both columns

| Action ID | Name | **Primary** | All | Counted in Primary? |
|---|---|---|---|---|
| 1068114183 | Calls from ads | **5.00** | 5.00 | yes |
| 6885463625 | Ambient Cooling - LP -Submit Lead Forms | **5.00** | 5.00 | yes |
| 7643656486 | WC Lead | **4.00** | 8.00 | **partly — 4 of 8** |
| 6642551975 | Local actions - Other engagements | 0.00 | 33.00 | no |
| 6641739327 | Local actions - Website visits | 0.00 | 9.00 | no |
| 7389995485 | (web) form_submission (GA4) | 0.00 | 6.00 | no |
| 6642544931 | Local actions - Directions | 0.00 | 5.00 | no |
| 7389995488 | (web) phone_call (GA4) | 0.00 | 3.00 | no |
| 6640721230 | Clicks to call | 0.00 | 1.00 | no |
| | **TOTAL** | **14.00** | **75.00** | |

### 1.2 The four named conversion actions, full field set

| Field | Calls from ads | LP Submit Lead Forms | WC Lead |
|---|---|---|---|
| `conversion_action.id` | 1068114183 | 6885463625 | **7643656486** |
| `resource_name` | `customers/2401959466/conversionActions/1068114183` | `.../6885463625` | `.../7643656486` |
| `name` | Calls from ads | Ambient Cooling - LP -Submit Lead Forms | WC Lead |
| `status` | ENABLED | ENABLED | ENABLED |
| `category` | PHONE_CALL_LEAD | SUBMIT_LEAD_FORM | CONTACT |
| `type` | AD_CALL | WEBPAGE | UPLOAD_CLICKS |
| `primary_for_goal` | **true** | **true** | **true** |
| `include_in_conversions_metric` | **true** | **true** | **true** |
| `counting_type` | ONE_PER_CLICK | ONE_PER_CLICK | ONE_PER_CLICK |
| `owner_customer` | 2401959466 | 2401959466 | 2401959466 |
| `origin` | CALL_FROM_ADS | WEBSITE | **WEBSITE** |
| click lookback | 30 days | 30 days | **60 days** |

**All four goal layers read, in order:**

1. `customer.conversion_tracking_setting` — tracking ID 11155434808, conversion customer is
   itself, `CONVERSION_TRACKING_MANAGED_BY_SELF`, customer data terms accepted, **enhanced
   conversions for leads ENABLED**.
2. `conversion_goal_campaign_config.goal_config_level` = **CUSTOMER on all five campaigns**, no
   custom goal. Customer-level goals therefore govern.
3. `customer_conversion_goal` biddable: **CONTACT/WEBSITE, CONTACT/CALL_FROM_ADS,
   PHONE_CALL_LEAD/WEBSITE, PHONE_CALL_LEAD/CALL_FROM_ADS, SUBMIT_LEAD_FORM/WEBSITE**. Not
   biddable: the four GOOGLE_HOSTED categories. `campaign_conversion_goal` mirrors this — 25 of
   45 rows biddable, the same five categories on each of the five campaigns.
4. `conversion_action` — as tabulated above.

**Configuration verdict: no defect.** WC Lead's `category`/`origin` pair is CONTACT/WEBSITE,
which is biddable at both the customer and campaign layer, and both `primary_for_goal` and
`include_in_conversions_metric` read true. There is nothing to fix at the goal level.
(`include_in_conversions_metric` is deprecated and immutable; it is read here because the brief
requires it, not because it is actionable.)

### 1.3 The WC Lead claim — **RETRACTED**

The prior finding was that *"WC Lead events after 2026-08-21 had conversions=0.0 and
all_conversions=1.0."* Day by day:

| Date | Campaign | **Primary** | All |
|---|---|---|---|
| 2026-08-20 | HVAC Repair | **1.00** | 1.00 |
| 2026-08-21 | AC Repair | 0.00 | 1.00 |
| 2026-08-21 | HVAC Installation | 0.00 | 1.00 |
| 2026-08-22 | AC Repair | 0.00 | 1.00 |
| 2026-08-25 | AC Repair | 0.00 | 1.00 |
| **2026-08-28** | **HVAC Repair** | **1.00** | 1.00 |
| **2026-09-01** | **HVAC Installation** | **2.00** | 2.00 |

| Split | Primary | All | Rows |
|---|---|---|---|
| on/before 2026-08-21 | 1.00 | 3.00 | 3 |
| **after 2026-08-21** | **3.00** | 5.00 | 4 |

**The date rule is false and is retracted.** Two WC Lead rows *after* 2026-08-21 carry non-zero
Primary values (2026-08-28 = 1.00 and 2026-09-01 = 2.00). What is true is that **4 of 8 WC Lead
records reached the Primary column** — a per-record split, not a date cut-off. The four that did
not are consistent with `ONE_PER_CLICK` de-duplication against a click that had already recorded
this action, but the API does not expose per-conversion GCLIDs, so the mechanism cannot be proved
from here.

### 1.4 Prove or retract — every requested figure

| Claim | Verdict | Evidence |
|---|---|---|
| **Calls 5** | **PROVEN** | action 1068114183: Primary 5.00, All 5.00. AC Repair 3, HVAC Repair 2. |
| **LP Forms 5** | **PROVEN** | action 6885463625: Primary 5.00, All 5.00. AC Repair 2, HVAC Repair 2, HVAC Installation 1. |
| **WC Lead 4** | **PROVEN** | action 7643656486: Primary 4.00 (All 8.00). |
| **Total Primary 14** | **PROVEN** | 5 + 5 + 4 = 14.00, and `metrics.conversions` sums to 14.00. Difference from the segmented sum: **0.00**. |
| **Installation post-swap conversions 3** | **PROVEN as RECORDS, not as unique leads** | 3.00 Primary, all on 2026-09-01. See §1.5. |
| **Installation post-swap CPA $141.87** | **RETRACTED** | Grain mismatch. Correct figure **$161.33**. See §2. |

### 1.5 Three records ≠ three leads

Every HVAC Installation record in the post-swap window 2026-08-29 → 09-03:

| Date | Action | Primary | All |
|---|---|---|---|
| 2026-09-01 | Ambient Cooling - LP -Submit Lead Forms | 1.00 | 1.00 |
| 2026-09-01 | **WC Lead** | **2.00** | 2.00 |
| 2026-09-01 | (web) form_submission (GA4) | 0.00 | 2.00 |
| 2026-09-01 | Clicks to call | 0.00 | 1.00 |
| 2026-09-01 | Local actions - Website visits | 0.00 | 2.00 |
| 2026-09-02 | Local actions - Other engagements | 0.00 | 7.00 |
| 2026-09-03 | Local actions - Website visits | 0.00 | 1.00 |

Installation clicks by day in that window: 08-31 → 1, **09-01 → 3**, 09-02 → 5, 09-03 → 1.

**All three Primary records landed on a day with exactly three clicks — a 100% click-to-record
rate.** `LP Submit Lead Forms` (WEBPAGE, fires on the thank-you view) and `WC Lead`
(UPLOAD_CLICKS, WhatConverts uploading the *same* submission back against the same GCLID) both
counted, alongside GA4 `form_submission` and `Clicks to call` in All conversions. **One
interaction can generate records under several conversion actions**, and this day has the exact
signature of that.

**Unique lead count is bounded, not known: between 1 and 3.**

| If unique leads = | Cost per unique lead | vs $280 target |
|---|---|---|
| 1 | **$483.98** | **OVER** |
| 2 | $241.99 | within |
| 3 | $161.33 | within |

Google Ads does not expose per-conversion GCLIDs. **This cannot be resolved from the API.**
WhatConverts or an anonymised lead export joined on GCLID is required.

---

## 2. Corrected campaign CPA figures

All-time settled, 2026-08-14 → 2026-09-08.

| Campaign | Clicks | Cost | Primary records | **Raw CPA** | Max CPQL | Verdict |
|---|---|---|---|---|---|---|
| AC Repair | 29 | $3,084.87 | 5 | **$616.97** | $150 | OVER |
| HVAC Repair | 29 | $1,951.94 | 6 | **$325.32** | $250 | OVER |
| HVAC Installation | 112 | $2,914.33 | 3 | **$971.44** | $280 | OVER |
| HVAC Replacement | 5 | $152.52 | 0 | — | $280 | no data |
| Gas Boiler Repair | 0 | $0.00 | 0 | — | $250 | no data |

### The $141.87 defect

| Measure | Value |
|---|---|
| Campaign-level cost, 2026-08-29 → 09-03 | **$483.98** (10 clicks) |
| Visible search-term cost, same window | $425.60 (9 clicks) |
| Primary conversion records | 3 |
| Prior figure: visible cost ÷ campaign conversions | $425.60 ÷ 3 = **$141.87** ❌ |
| **Correct: campaign cost ÷ campaign conversions** | $483.98 ÷ 3 = **$161.33** ✅ |

The prior figure divided a **visible search-term** numerator by a **campaign-level** denominator.
Every use of $141.87 in earlier reports is retracted and replaced with **$161.33 raw CPA on raw
conversion records**.

---

## 3. Installation CPC decision

**The rejection trigger did not fire.** The brief said: *if Installation has only one Primary
conversion, mark DE376F91F449 rejected.* Installation has **3** Primary conversion records, not
one. `DE376F91F449` is nonetheless **SUPERSEDED / DO_NOT_EXECUTE** because its stated rationale
carried the wrong CPA and a 30-click rollback trigger.

**Replacement: `AMB-0909C-CPC-INST-2` — fingerprint `5D57E0EF3B70` — 1 operation.**
HVAC Installation `target_spend.cpc_bid_ceiling_micros` 30000000 → **65000000**.

**What supports it:** all three conversion records came from clicks priced **$50.00 – $62.13**.
The live $30 ceiling admits 76% of historical click volume while excluding every one of those
clicks. Live keyword re-verified as `hvac installers near me` (PHRASE crit 295495761070, EXACT
crit 315030681341, both ELIGIBLE); the removed `hvac installers` is confirmed not live. Bid-
modifier audit: 5 modifiers exist, **all DEVICE/TABLET ×0.0**; highest modifier anywhere is
×0.0, so nothing can raise the effective bid above $65.

**What does not support it:** the corrected raw CPA is $161.33, not $141.87; the unique lead
count is 1–3; and if it is 1 the cost per unique lead is $483.98, well over the $280 target.

### Outcome-based stop-loss gates

| Gate | Incremental spend since execution | Requirement | If not met |
|---|---|---|---|
| **1** | **$280.00** | at least **one** verified unique qualified lead | roll back to $30 immediately |
| **2** | **$560.00** | at least **two** verified unique qualified leads | roll back to $30 immediately |

- Verification source: **WhatConverts, or an anonymised lead export joined on GCLID.** A raw
  conversion record is not a qualified lead.
- **The 30-click threshold is removed.** At a $65 ceiling, 30 clicks could cost up to $1,950
  before intervention. Click counts are not used as a gate.
- **Rollback target is exactly `30000000` micros ($30.00)** — the verified pre-test value. Any
  other rollback amount requires separate approval.
- **Outcome data are currently unavailable** (`WHATCONVERTS_API_TOKEN` is empty). The test is
  therefore labelled **UNVERIFIED** and **no CPQL compliance is claimed**. Gate 1 still applies
  as a hard $280 spend stop.

### Sequencing constraint

**Do not execute this CPC increase and any material HVAC Installation search-term expansion in
the same change window.** Separate them by **at least 7 settled days, or the $280 gate-1 spend
threshold, whichever comes first.**

`AMB-0909C-COMP-1` adds three negatives to Installation — negatives *narrow* matching and do not
conflict. **`AMB-0909C-NEG-COMMERCIAL` widens matching on all five campaigns including
Installation and must be separated from the CPC package by the stated interval.**

---

## 4. Per-campaign budget-limit calculations

Rebuilt campaign by campaign. **Only Gas Boiler Repair and HVAC Replacement change.** The other
three retain their own campaign-level monthly limits, so the September maximum is the **sum of
per-campaign maxima**, not account spend-to-date plus a combined formula.

Proposed edit day **2026-09-10**. Remaining calendar days including the edit day: **21**
(09-10 → 09-30). The edit day itself is evaluated at the **highest budget in force that day**.

| Campaign | Before | Proposed | Sept spend to preflight | Edit-day limit | × 20 rest days | **Sept campaign max** | **Steady 30.4** |
|---|---|---|---|---|---|---|---|
| AC Repair | $141.45 | $141.45 | $534.28 | $141.45 | $2,829.00 | $3,504.73 | $4,300.08 |
| Gas Boiler Repair | $42.76 | **$5.00** | $0.00 | $42.76 | $100.00 | $142.76 | $152.00 |
| HVAC Installation | $176.15 | $176.15 | $498.43 | $176.15 | $3,523.00 | $4,197.58 | $5,354.96 |
| HVAC Repair | $78.95 | $78.95 | $286.78 | $78.95 | $1,579.00 | $1,944.73 | $2,400.08 |
| HVAC Replacement | $26.32 | **$20.00** | $0.00 | $26.32 | $400.00 | $426.32 | $608.00 |
| **COMBINED** | **$465.63** | **$421.55** | **$1,319.49** | | | **$10,216.12** | **$12,815.12** |

- Hard daily maximum: **$13,000 ÷ 30.4 = $427.6315789**
- Steady-state **before**: $465.63 × 30.4 = **$14,155.15** → **$1,155.15 breach**
- Steady-state **after**: $421.55 × 30.4 = **$12,815.12** → **$184.88 headroom** ✅
- September combined maximum: **$10,216.12** → $2,783.88 headroom

**Realistic projection (not the maximum):**

| Scenario | Modelled September |
|---|---|
| No change, ceilings hold ($11.27/day) | ~$1,556 — 12% of cap |
| Installation restored to its pre-ceiling rate | ~$4,471 — 34% of cap |

### The $5 and $20 amounts remain justified on fresh data

| Campaign | All-time settled | September to preflight | Lost IS (budget) | Lost IS (rank) |
|---|---|---|---|---|
| Gas Boiler Repair | 34 impr, **0 clicks**, $0.00, 0 conv | 29 impr, 0 clicks, $0.00 | **0.00%** | 48.39% |
| HVAC Replacement | 199 impr, 5 clicks, $152.52, **0 conv** | 106 impr, 0 clicks, $0.00 | **0.00%** | 45.54% |

Budget has never been either campaign's constraint. Both lose share to **rank**. The reductions
cannot cost delivery.

---

## 5. Future-safe budget rollback

**A blind restore of $42.76 + $26.32 is forbidden.** It returns the combined daily total to
$465.63 = **$14,155.15** over 30.4 days, a **$1,155.15 breach**.

**Compliant envelope:**

```
hard daily max                                     $427.63
minus the three unchanged budgets
  AC Repair $141.45 + Installation $176.15 + Repair $78.95 = $396.55
= envelope for Gas Boiler + HVAC Replacement TOGETHER        $31.08/day
```

- Proposed $5.00 + $20.00 = **$25.00** → $6.08 unused headroom ✅
- Any restoration must keep the two **at or below $31.08/day combined**.
- Example compliant partial restore: Gas Boiler $10.00 + HVAC Replacement $21.00 = $31.00
  → $427.55/day → $12,997.52 over 30.4 days.
- **Anything above $31.08 combined requires an offsetting reduction elsewhere, a fresh cap
  calculation and a new approval fingerprint.**

---

## 6. Three separated negative-removal decisions

`AMB-0909B-NEG-A` (`18143479027D`, 16 ops) is **SUPERSEDED / DO_NOT_EXECUTE** and split.

### 6.1 `AMB-0909C-NEG-SAVAGE` — **5 operations** — `10F76004E1B6` — APPROVE-READY

Remove PHRASE `savage` from all five campaigns.

**Proof — Savage, Maryland is actively targeted:**

| Evidence | Result |
|---|---|
| `geoTargetConstants/1018704` | `'Savage,Savage,Maryland,United States'`, type **Neighborhood**, status ENABLED, country US |
| Positive LOCATION criteria on the five | **5 of 5**, every one `status = ENABLED`, `negative = false` |
| Geo × service probe grid | PHRASE `savage` blocked **300 of 300** Savage probes and was the only negative responsible |

**Conflict validation:** active keywords — clear (no live positive contains `savage`); converting
queries — clear (0 of 304 account-wide all-time contain it); targeted locations — **restores
one**; BOFU probes — removal unblocks, never blocks. Observed search terms containing `savage`
since launch: **0**, which is the expected consequence of the negative suppressing them before
they could be reported, not evidence of absent demand.

### 6.2 `AMB-0909C-NEG-COMMERCIAL` — **1 operation** — `9F88FEE76803` — APPROVE-READY

Remove account-level BROAD `commercial` from shared set 11252984411.

**Duplicate sweep — every exact-token `commercial` negative in the account:**

| Layer | Count | Detail |
|---|---|---|
| Account-level set 11252984411 | **1** | the removal target, `.../sharedCriteria/11252984411~10061081` |
| Other shared sets | **0** | (41 *multiword* rows exist — `commercial tree removal` etc. — none is the bare token) |
| Campaign level | **2** | 22822619680 and 23883756382, both **PAUSED** Performance Max campaigns |
| Ad group level | **2** | ad groups 159023127588 and 201974220664 in campaign 20293627152 "HVAC Install", **campaign PAUSED** |
| **On the five live campaigns** | **0** | |

**Conclusion: removing the account-level member is sufficient to unblock `commercial` on
everything that can currently serve.** All four duplicates sit in PAUSED campaigns and would need
separate handling only if any of those were re-enabled. (All five share `criterion_id` 10061081 —
criterion ids are not unique across resources; the resource name is the key.)

**Effect across all non-removed campaigns:** the list governs all **23** non-removed campaigns —
**5 ENABLED** (the five in scope) and **18 PAUSED**. Removal widens matching on all 23, but only
the 5 ENABLED can serve. The 18 paused change in configuration only, with zero delivery effect.

**Historical evidence — raw records, not qualified leads.** Eleven all-time search-term rows
containing `commercial` produced **3.83 raw primary conversion records** across five legacy
campaigns (`commercial ac repair near me`, `commercial hvac companies near me`,
`commercial furnace repair`, `commercial boiler repair`, `commercial radiator repair`,
`commercial ductwork installation near me`, `commercial hvac near me`). **These are raw conversion
records. Qualification is unknown and none is described as a qualified lead.** Supporting service
evidence: the homepage and furnace-repair page both name commercial work,
`/services/hvac/condominium-hvac/` is a dedicated page, and `/category/commercial-hvac/` carries a
Maryland BEPS compliance article.

**Rollback:** re-create `commercial` as a **BROAD** negative keyword in shared set 11252984411.

### 6.3 `NEG-FREE` — **HELD, 0 operations**

Held as instructed, and the fresh evidence supports holding.

**Every observed search-term row containing `free` since launch — there is exactly one:**

| Intent bucket | Rows | Impressions | Clicks | Cost |
|---|---|---|---|---|
| **free estimate / quote** (supported proposition) | **1** — `hvac repair free estimate near me`, HVAC Repair | 6 | **0** | $0.00 |
| free repair | 0 | 0 | 0 | $0.00 |
| free service | 0 | 0 | 0 | $0.00 |
| free parts | 0 | 0 | 0 | $0.00 |
| free diagnostic / free service call | 0 | 0 | 0 | $0.00 |
| free, other | 0 | 0 | 0 | $0.00 |

**Account-wide, all-time `free` queries that have ever converted: 0.**

The intents are separable in principle — free estimate is a supported Ambient proposition, while
free repair, free service, free parts and free diagnostic are not — but **no query in any of those
buckets has ever been observed**, and there is no campaign-specific routing for them. Removing
`free` merely because the company offers free estimates is not justified. **HELD pending real
search-term evidence and a routing decision.**

### 6.4 `NEG-LICENSED` — **HELD, 0 operations — the required proof FAILED**

The brief required proof that `licensed` is supported advertising language. **It could not be
proved.**

| Evidence source | Result |
|---|---|
| Live ENABLED ad assets on the five campaigns containing `licens`/`licenc` | **0** |
| Live ENABLED callouts containing it | **0** |
| `/ac-repair/` landing page | **0 matches** for licensed / licence / insured / bonded / certified / NATE |
| `/hvac-repair/` | **0 matches** |
| `/hvac-installation/` | **0 matches** |
| `/hvac-replacement/` | **0 matches** |
| `/gas-boiler-repair/` | **0 matches** |
| Main website homepage | 1 match — footer string **"CERTIFIED SERVICE TECHNICIAN"** |
| Main website /services/ and /reviews/ | same footer string only |

The word **"licensed" appears nowhere** on any Ambient property that was rendered. The only
adjacent language is "CERTIFIED SERVICE TECHNICIAN" in the main-site footer, which is *certified*,
not *licensed and insured*. The work order lists "licensed and insured" among approved baseline
claims, but nothing live corroborates it.

**This is the single largest reason the operation count is 14 rather than 24.** The removal is
held pending a claim-substantiation answer from the client — see the question in §10.

> Worth separating for the decision: the negative blocks *searcher queries* such as
> `licensed hvac contractor near me`, and Maryland law requires HVAC contractors to hold an
> HVACR licence. Whether Ambient *advertises* the word and whether the *query* is valuable are
> different questions. But the brief set the gate at advertising language, and that gate failed.

---

## 7. Exact-only competitor package

`AMB-0909C-COMP-1` — **3 operations** — `D434D6F41747`. All EXACT. All reproduce a **verbatim
observed query**; no variant was invented.

| # | Match | Verbatim observed query | Impr | Clicks | Cost | Entity |
|---|---|---|---|---|---|---|
| 1 | EXACT | `arundel cooling and heating reviews` | 8 | 1 | **$20.44** | Arundel Cooling & Heating Co., Inc. |
| 2 | EXACT | `arundel heating and cooling maryland` | 1 | 0 | $0.00 | Arundel Cooling & Heating Co., Inc. |
| 3 | EXACT | `maryland mechanical heating & cooling` | 4 | 1 | **$50.17** | Maryland Mechanical Heating & Cooling LLC |

**Match-type correction:** PHRASE `maryland mechanical heating` is **withdrawn** — it can overlap
generic Maryland mechanical-heating intent. Operation 3 uses the observed spelling **including the
ampersand**.

**Conflicts re-run — all clear:**

| Test | Result |
|---|---|
| Active keywords (10 live positives) | 0 blocked |
| Historical converting terms (304 account-wide, all time) | 0 blocked |
| Targeted Maryland locations (80 tokens) | 0 blocked |
| **Anne Arundel queries** (6 probes × 3 negatives = 18 checks) | **0 blocked** |
| BOFU service probes (67) | 0 blocked |
| Brand / manufacturer queries | no operation contains any manufacturer token |
| Word limit ≤10, character limit ≤80 | 3/3 pass |
| Already present at campaign / ad group / account level | 0/3 |

**Deliberately not blocked:** `arundel cooling and heating` (6 impressions, 0 clicks, $0.00 — one
word from the county queries), `anne arundel cooling and heating` (produced a primary phone-call
record), `hvac anne arundel county` (county intent in the core service area).

### Paste-ready blocks

**REMOVE — campaign level, all five campaigns** (`AMB-0909C-NEG-SAVAGE`)
```
"savage"
```

**REMOVE — account-level list 11252984411** (`AMB-0909C-NEG-COMMERCIAL`)
```
commercial
```

**ADD — HVAC Installation, campaign 24132507747** (`AMB-0909C-COMP-1`)
```
[arundel cooling and heating reviews]
[arundel heating and cooling maryland]
[maryland mechanical heating & cooling]
```

---

## 8. Invalid-click investigation

Read-only. Settled window 2026-08-14 → 2026-09-08. **Each dimension was queried on its own before
any conclusion was combined.** Nothing was changed — no IP exclusion, network, device, schedule or
location.

### By campaign

| Campaign | Impr | Billable clicks | Invalid clicks | Raw | Invalid % |
|---|---|---|---|---|---|
| AC Repair | 879 | 29 | **939** | 968 | 97.00% |
| HVAC Repair | 1,058 | 29 | **619** | 648 | 95.52% |
| HVAC Installation | 3,419 | 112 | 91 | 203 | 44.83% |
| HVAC Replacement | 199 | 5 | 82 | 87 | 94.25% |
| Gas Boiler Repair | 34 | 0 | 42 | 42 | 100.00% |
| **Account total** | **5,589** | **175** | **1,773** | **1,948** | **91.02%** |

### By device

| Device | Impr | Billable | Invalid | Invalid % |
|---|---|---|---|---|
| **MOBILE** | 3,027 | 126 | **1,743** | **93.26%** |
| DESKTOP | 2,562 | 49 | 30 | 37.97% |

### By network

| Network | Impr | Billable | Invalid | Invalid % |
|---|---|---|---|---|
| SEARCH | 5,589 | 175 | 1,773 | 91.02% |

Search Partners and Display are off, so the whole population is Google Search.

### By click type — **this is where it concentrates**

| Click type | Impr | Billable | Invalid | Invalid % |
|---|---|---|---|---|
| **LOCATION_EXPANSION** | 2,937 | 34 | **1,706** | **98.05%** |
| URL_CLICKS | 5,589 | 99 | 63 | 38.89% |
| CALLS | 1,698 | 10 | 4 | 28.57% |
| SITELINKS | 1,595 | 26 | **0** | 0.00% |
| GET_DIRECTIONS | 335 | 6 | **0** | 0.00% |

**`LOCATION_EXPANSION` carries 1,706 of 1,773 invalid clicks — 96.2% of all invalid traffic in the
account — at a 98.05% invalid rate.** Cross-referenced with the device split, the invalid
population is overwhelmingly **mobile × location expansion**: the Google Business Profile location
surface, which is well known for accidental taps.

By date, invalid clicks peak on 2026-08-20 (216), 08-26 (193), 08-22 (183) and 08-27 (178), and
fall away after the 09-04 ceilings simply because delivery stopped.

**The nuance that matters:** LOCATION_EXPANSION is *also* a real conversion source — 34 billable
clicks, $2,003.44, **4 of the 14 primary conversion records** and 35 all-conversions. It is
simultaneously the highest-invalid surface and a genuine lead source. **No exclusion is proposed.**

### What these numbers do and do not prove

- `metrics.invalid_clicks` counts clicks **Google** detected as invalid and filtered **before
  billing**. They are already excluded from `metrics.clicks` and `metrics.cost_micros`. **This is
  not unbilled spend and not a refund owed.**
- **It does not measure ClickCease.** ClickCease works by adding IP exclusions, which *prevent* an
  ad from being shown to a blocked IP — a prevented impression never becomes a click and therefore
  never appears in either column. Google's invalid-click count and ClickCease's blocked count are
  different populations measured by different systems.
- **Direct evidence against attributing any of this to ClickCease:** there are 2,796 `IP_BLOCK`
  criteria in the account and **0 of them on the five live campaigns**. All 2,796 sit on the 18
  legacy campaigns. Whatever is driving the invalid-click counts on the five, ClickCease IP
  blocking is demonstrably not filtering it.
- Attributing anything to ClickCease requires **the ClickCease dashboard's own blocked-click
  report** for 2401959466 over the same settled window. That is outside the Google Ads API and was
  not available in this run. **No ClickCease attribution is claimed.**

---

## 9. Exact operation count

| Package | Fingerprint | Class | Ops |
|---|---|---|---|
| AMB-0909C-BUD-1 | `A7118436590B` | reversible-budget-change | **2** |
| AMB-0909C-CPC-INST-2 | `5D57E0EF3B70` | reversible-setting-change, UNVERIFIED TEST | **1** |
| AMB-0909C-NEG-SAVAGE | `10F76004E1B6` | DESTRUCTIVE-removal | **5** |
| AMB-0909C-NEG-COMMERCIAL | `9F88FEE76803` | DESTRUCTIVE-removal, ACCOUNT-LEVEL | **1** |
| AMB-0909C-COMP-1 | `D434D6F41747` | reversible-addition | **3** |
| | | **New packages** | **12** |
| AMB-0909-ADS-1 | `11A79347A296` | carried forward, revalidated | **2** |
| | | **APPROVAL BLOCK TOTAL** | **14** |

**The brief anticipated 22 new / 24 total. The actual figures are 12 new / 14 total.**

The **10-operation delta is exactly the two held sub-packages**:

| Held | Ops not drafted | Why |
|---|---|---|
| NEG-LICENSED | **5** | Required proof failed — `licensed` appears in zero live ads, zero callouts and zero of the five landing pages (§6.4) |
| NEG-FREE | **5** | Held as instructed, and only one `free` query has ever been observed, with 0 clicks and 0 conversions (§6.3) |
| | **10** | |

Drafting either would mean asserting something the evidence does not support.

---

## 10. Consolidated approval block

All five new packages **VALIDATED_OK**, one atomic mutate each, `partial_failure = false`.
AMB-0909-ADS-1 re-verified and re-validated. **Nothing was executed. This report is not approval.**

### Safe, reversible

```
APPROVE AMB-0909C-BUD-1          A7118436590B     2 operations
```
Gas Boiler Repair $42.76 → $5.00; HVAC Replacement $26.32 → $20.00. Combined $465.63 → $421.55 =
**$12,815.12** over 30.4 days, $184.88 inside the cap. Per-campaign limits in §4. Rollback
envelope in §5.

```
APPROVE AMB-0909C-COMP-1         D434D6F41747     3 operations
```
Three EXACT competitor negatives on HVAC Installation, each a verbatim observed query.

```
APPROVE AMB-0909-ADS-1           11A79347A296     2 operations
```
Carried forward and revalidated: both ads still ENABLED + DISAPPROVED, each ad group retains 2
ENABLED + APPROVED RSAs, update mask is status-only. **Inert cleanup, not a performance change.**

### Outcome-gated test — approve only with the stop-losses

```
APPROVE AMB-0909C-CPC-INST-2     5D57E0EF3B70     1 operation
```
HVAC Installation ceiling $30 → $65. **UNVERIFIED test.** Gate 1: $280 incremental spend requires
≥1 verified unique qualified lead. Gate 2: $560 requires ≥2. Rollback to exactly $30. **No CPQL
compliance is claimed.** Must be separated from `AMB-0909C-NEG-COMMERCIAL` by ≥7 settled days or
the $280 threshold.

### Destructive — separate approval lines

```
APPROVE DESTRUCTIVE AMB-0909C-NEG-SAVAGE      10F76004E1B6     5 operations
```
Remove PHRASE `savage` from all five campaigns. Savage MD proven an ENABLED positive target on
every one.

```
APPROVE DESTRUCTIVE AMB-0909C-NEG-COMMERCIAL  9F88FEE76803     1 operation
```
Remove account-level BROAD `commercial`. Duplicate sweep proves 0 duplicates on the five live
campaigns.

### Recommended order

1. **`AMB-0909C-BUD-1`** — bring the configuration inside the cap before restoring delivery.
2. **`AMB-0909C-COMP-1`** and **`AMB-0909-ADS-1`** — narrowing and inert, safe any time.
3. **`AMB-0909C-NEG-SAVAGE`** — restores a targeted city.
4. **`AMB-0909C-CPC-INST-2`** — start the gated test; begin counting incremental spend here.
5. **≥7 settled days or $280 incremental spend**, then `AMB-0909C-NEG-COMMERCIAL`.

### Superseded — DO NOT EXECUTE

`752BF95EBD7C` · `DE376F91F449` · `05FBCBD34B4A` · `18143479027D`
(plus the second-pass set: `46C39C6B7091`, `D448BFDE4650`, `23BE8FF0F24C`, `CE289F3508A2`,
`A435FA09AC97`)

All plan files are preserved byte-for-byte with a SHA-256 recorded in
`evidence/2026-09-09c-package-ledger.json`. Old and new fingerprint sets are provably disjoint.

### Held — no operations

NEG-LICENSED (proof failed) · NEG-FREE (no evidence) · Package B manufacturers · Package C
additional services · Package D dealer/installer.

---

## 11. The open questions

1. **Can Ambient substantiate "licensed and insured"?** The claim appears in the work order but on
   none of the live properties. A yes unblocks 5 held operations and should also be added to the ad
   copy; a no means the negative stays and the claim leaves the approved list.
2. **WhatConverts access.** `WHATCONVERTS_API_TOKEN` is empty. Until it is restored, every CPA in
   every report is a raw figure over raw records, the unique-lead count for Installation stays
   bounded at 1–3, and the CPC test cannot clear its own gates.
3. **Do the $150 / $250 / $280 CPQL limits outrank spending the $13,000?** Unchanged from the
   prior report and still unanswered. All three campaigns with data are over their limits on raw
   CPA alone.

---

## 12. Evidence index

| File | Contents |
|---|---|
| `evidence/2026-09-09c-conversion-reconciliation.json` | four goal layers, 16 conversion actions, 47 daily rows segmented date × campaign × action |
| `evidence/2026-09-09c-cpa-and-budget.json` | corrected CPAs, unique-lead bounding, per-campaign budget limits, rollback envelope |
| `evidence/2026-09-09c-negative-evidence.json` | Savage proof, licensed proof, `commercial` duplicate sweep, `free` intent split, competitor observed spellings |
| `evidence/2026-09-09c-licensed-evidence.json` | 8 rendered pages, licensed/insured/certified search |
| `evidence/2026-09-09c-invalid-click-audit.json` | invalid clicks by campaign, date, device, network, click type |
| `evidence/2026-09-09c-local-preflight.json` | preflight result, 0 FAIL |
| `evidence/2026-09-09c-package-ledger.json` | supersession ledger, SHA-256 per preserved plan, final unchanged proof |
| `clients/ambient-cooling-heating/plans/AMB-0909C-*.json` | the five new packages |
| `plans/AMBIENT-2026-09-09c-packages.json` | combined manifest |
| `receipts/validate-only/AMB-0909C-*-2026-09-09c.json` | five validate-only receipts |
| `receipts/validate-only/AMB-0909-ADS-1-2026-09-09c-revalidation.json` | ADS-1 revalidation |

---

*Third pass. Zero mutations executed. Every external change requires its own explicit approval
line above.*
