# SOFTWIND POWER WASHING — CONVERSION MEASUREMENT DECISION

**Generated:** 2026-09-01 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
**Zero external changes. No Google Ads mutation created. Plan is NOT APPROVED.**

Continues `2026-09-01-final-strategy-continuation.md`. **It overturns that file's selected next
action.** Evidence: `snapshots/goal-hierarchy-2026-09-01T183647.json`,
`snapshots/plan-r1b-validation-2026-09-01T184249.json`.

---

## Headline

# The September 1 recommendation was wrong. There is no goal-configuration defect.

The September 1 continuation selected "set the three lead `customer_conversion_goal` categories to
`biddable: true`" as the single next action, on the reasoning that the Conversions column was
"structurally zeroed". A fresh read of the **complete four-layer goal hierarchy** — which no prior
run had performed — proves that reasoning wrong in three independent ways:

1. **Both campaigns are `goal_config_level: CAMPAIGN`.** They do not use the account-default
   customer goals at all. Mutating those goals would not affect either campaign.
2. **Their campaign-level goals are already correct** — the three lead categories `biddable: true`,
   GET_DIRECTIONS `false`.
3. **`include_in_conversions_metric` is a deprecated, immutable field.** The whole "structurally
   zeroed" finding rested on misreading it. `primary_for_goal` is the controlling field, and it
   reads `true` on all four actions.

**The proposed mutation was not merely unnecessary — it was aimed at the wrong layer, justified by
a deprecated field, and one of the three fields it targeted cannot be written at all.**

---

## 1. Fresh identity gate — PASS

| Field | Observed | Required | Result |
|---|---|---|---|
| `customer.descriptive_name` | **Softwind Power Washing - Live** | exact | **PASS** |
| `customer.id` | **1521725229** | exact | **PASS** |
| `customer.manager` | **false** | false | **PASS** |
| `customer.test_account` | **false** | false | **PASS** |
| `customer.status` | **ENABLED** | ENABLED | **PASS** |
| Currency | **USD** | USD | **PASS** |
| Time zone | **America/New_York** | America/New_York | **PASS** |
| Read time (account local) | 2026-09-01 18:36:47 → 18:42:49 | — | — |

**Conversion tracking ownership**

| Field | Value |
|---|---|
| `google_ads_conversion_customer` | `customers/1521725229` — **self** |
| `conversion_tracking_status` | **CONVERSION_TRACKING_MANAGED_BY_SELF** |
| `conversion_tracking_id` | **18369652705** (account tag `AW-18369652705`) |
| `cross_account_conversion_tracking_id` | **empty** |
| **Cross-account conversion tracking active?** | **NO** |
| `enhanced_conversions_for_leads_enabled` | false |
| `accepted_customer_data_terms` | false |

**Campaign names observed — both match, neither touched**

| ID | Expected | Observed | Match |
|---|---|---|---|
| `24103511039` | Power Washing | **Power Washing** | ✓ |
| `24145053510` | Pressure Washing | **Pressure Washing** | ✓ |

---

## 2. Goal configuration level per campaign

| Campaign | Name | `goal_config_level` | `custom_conversion_goal` | Uses |
|---|---|---|---|---|
| `24103511039` | Power Washing | **CAMPAIGN** | none | **CAMPAIGN goals** |
| `24145053510` | Pressure Washing | **CAMPAIGN** | none | **CAMPAIGN goals** |

**Neither campaign uses CUSTOMER goals. Neither uses CUSTOM goals.**

Official semantics: when `goal_config_level` is CAMPAIGN, Google Ads *"stops applying
`CustomerConversionGoal` updates to the campaign's `CampaignConversionGoal` objects."*

---

## 3. CustomerConversionGoal — account defaults

| Resource name | Category | Origin | Biddable |
|---|---|---|---|
| `customers/1521725229/customerConversionGoals/GET_DIRECTIONS~GOOGLE_HOSTED` | GET_DIRECTIONS | GOOGLE_HOSTED | **false** |
| `customers/1521725229/customerConversionGoals/PHONE_CALL_LEAD~CALL_FROM_ADS` | PHONE_CALL_LEAD | CALL_FROM_ADS | **false** |
| `customers/1521725229/customerConversionGoals/PHONE_CALL_LEAD~WEBSITE` | PHONE_CALL_LEAD | WEBSITE | **false** |
| `customers/1521725229/customerConversionGoals/SUBMIT_LEAD_FORM~WEBSITE` | SUBMIT_LEAD_FORM | WEBSITE | **false** |

**These are account defaults only. No live campaign consumes them.**

---

## 4. CampaignConversionGoal — what the campaigns actually use

| Campaign | Name | Resource name | Category | Origin | Biddable |
|---|---|---|---|---|---|
| 24103511039 | Power Washing | `…/campaignConversionGoals/24103511039~PHONE_CALL_LEAD~CALL_FROM_ADS` | PHONE_CALL_LEAD | CALL_FROM_ADS | **true** |
| 24103511039 | Power Washing | `…/campaignConversionGoals/24103511039~PHONE_CALL_LEAD~WEBSITE` | PHONE_CALL_LEAD | WEBSITE | **true** |
| 24103511039 | Power Washing | `…/campaignConversionGoals/24103511039~SUBMIT_LEAD_FORM~WEBSITE` | SUBMIT_LEAD_FORM | WEBSITE | **true** |
| 24103511039 | Power Washing | `…/campaignConversionGoals/24103511039~GET_DIRECTIONS~GOOGLE_HOSTED` | GET_DIRECTIONS | GOOGLE_HOSTED | **false** |
| 24145053510 | Pressure Washing | `…/campaignConversionGoals/24145053510~PHONE_CALL_LEAD~CALL_FROM_ADS` | PHONE_CALL_LEAD | CALL_FROM_ADS | **true** |
| 24145053510 | Pressure Washing | `…/campaignConversionGoals/24145053510~PHONE_CALL_LEAD~WEBSITE` | PHONE_CALL_LEAD | WEBSITE | **true** |
| 24145053510 | Pressure Washing | `…/campaignConversionGoals/24145053510~SUBMIT_LEAD_FORM~WEBSITE` | SUBMIT_LEAD_FORM | WEBSITE | **true** |
| 24145053510 | Pressure Washing | `…/campaignConversionGoals/24145053510~GET_DIRECTIONS~GOOGLE_HOSTED` | GET_DIRECTIONS | GOOGLE_HOSTED | **false** |

**8 rows. Three lead goals biddable on each campaign; GET_DIRECTIONS correctly non-biddable on
both. This is exactly the configuration the September 1 plan proposed to create — it already
exists, one layer down, where it actually applies.**

---

## 5. Conversion actions

| Field | Submission Lead Form | Website Phone Call Lead | Call Asset Lead | Local actions - Directions |
|---|---|---|---|---|
| **ID** | **7708725995** | **7708765130** | **7711699090** | **7713188607** |
| Resource name | `…/conversionActions/7708725995` | `…/conversionActions/7708765130` | `…/conversionActions/7711699090` | `…/conversionActions/7713188607` |
| Status | **ENABLED** | ENABLED | ENABLED | ENABLED |
| Type | WEBPAGE | WEBSITE_CALL | AD_CALL | GOOGLE_HOSTED |
| Category | SUBMIT_LEAD_FORM | PHONE_CALL_LEAD | PHONE_CALL_LEAD | GET_DIRECTIONS |
| Origin | WEBSITE | WEBSITE | CALL_FROM_ADS | GOOGLE_HOSTED |
| **Owning conversion customer** | **1521725229** | **1521725229** | **1521725229** | **1521725229** |
| **`primary_for_goal`** | **true** | **true** | **true** | **true** |
| `include_in_conversions_metric` | false *(deprecated)* | false *(deprecated)* | false *(deprecated)* | false *(deprecated)* |
| Counting | ONE_PER_CLICK | ONE_PER_CLICK | ONE_PER_CLICK | MANY_PER_CLICK |
| Attribution model | GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN | GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN | GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN | GOOGLE_ADS_LAST_CLICK |
| Click window | **90 days** | 30 | 30 | 30 |
| View window | 1 day | 30 | 30 | 7 |
| Min. call duration | n/a (60 default) | **60 s** | **60 s** | n/a |
| Default value / currency | 0.0 / USD | 0.0 / USD | 0.0 / USD | 1.0 / USD |
| Tag snippets | **4** | 1 | 0 | 0 |
| **Google tag ID** | **AW-18369652705** | — | — | — |
| **Conversion label** | **FddkCOul59scEOHPqrdE** | — | — | — |
| **All-time `all_conversions`** | **0.0** | **0.0** | **0.0** | **0.0** |

**Every action belongs to customer `1521725229`.** None belongs to another conversion customer.

**Last conversion date / recording status:** the Google Ads API exposes no `last_conversion_date`
or `recording_status` field on `conversion_action`. The equivalent evidence is
`metrics.all_conversions` by date, which is **0.0 for every action across the account's entire
life**, and **zero** `campaign` × `segments.conversion_action` rows exist.

**Account tag `AW-18369652705` ≠ foreign tag `AW-17878095007`.** Confirmed distinct against
`conversion_tracking_id: 18369652705`.

---

## 6. Root-cause verdict table

| # | Possibility | Verdict | Evidence |
|---|---|---|---|
| **A** | Customer account-default goals incorrectly non-biddable | **REJECTED** *(as a cause)* | All four are `biddable: false`, but **neither campaign consumes them** — both are `goal_config_level: CAMPAIGN`. Real, but causally inert here. Reclassified as latent hygiene in §8. |
| **B** | Campaign-specific goals incorrectly non-biddable | **REJECTED** | All six lead goals across the two campaigns read `biddable: true`. |
| **C** | Intended actions Secondary because `primary_for_goal = false` | **REJECTED** | All four read `primary_for_goal: true`. |
| **D** | Campaigns use customer goals rather than campaign goals | **REJECTED** | `goal_config_level: CAMPAIGN` on both. |
| **E** | Campaigns use campaign-specific goals correctly | **SUPPORTED** | 8 `campaign_conversion_goal` rows, three lead categories biddable per campaign, GET_DIRECTIONS false. |
| **F** | Conversion actions belong to a different conversion customer | **REJECTED** | `owner_customer = customers/1521725229` on all four. `cross_account_conversion_tracking_id` empty; tracking `MANAGED_BY_SELF`. |
| **G** | Configuration correct, but no conversion event ever fired | **SUPPORTED — CONTROLLING** | `all_conversions = 0.0` on all four actions, all time. Official docs: when `primary_for_goal` is false the data *"remains accessible in All conversions"* — so `all_conversions` is **not gated by any goal or primary/secondary setting**. Zero there means nothing was ever recorded. |
| **H** | The form event is not firing | **INCONCLUSIVE** | Cannot be separated from G by reading the account. The 18 valid ad clicks may simply never have submitted — WhatConverts independently confirms zero relevant leads, which explains the zero with no defect. Only a controlled event test can settle it. |
| **I** | Website-call number replacement not working | **INCONCLUSIVE** | Offer pages render the approved tracked **(631) 502-7946** in `tel:` and body (verified 2026-08-31). A `wc_swap`-sourced number was seen on main-site pages 2026-08-26 and not re-confirmed. Untestable until the form path is understood. |
| **J** | Call asset has never received a qualifying call | **SUPPORTED** | 88 `CALLS` impressions, **0 call clicks**, **0 `call_view` rows** across the whole retained log. `phone_call_duration_seconds: 60` — no call has ever reached the threshold because no call has ever occurred. |
| **K** | Foreign tag `AW-17878095007` receiving events belonging to this account | **INCONCLUSIVE** | Confirmed present on 6 offer + 2 main-site pages and confirmed to be a different account from `AW-18369652705`. Whether it **receives the conversion event** requires network capture during a real submission. This is the highest-value single output of PLAN-R1B. |
| **L** | Prior audit misinterpreted `include_in_conversions_metric` | **SUPPORTED** | The field is **deprecated**; official docs state setting it raises `FieldError.IMMUTABLE_FIELD` and that `primary_for_goal` must be set instead. The September 1 "structurally zeroed Conversions column" finding rested entirely on it. |

---

## 7. Would the previously proposed customer-goal mutations affect these two campaigns?

# NO.

Both campaigns are `goal_config_level: CAMPAIGN`. Google Ads *"stops applying
`CustomerConversionGoal` updates to the campaign's `CampaignConversionGoal` objects"* for such a
campaign. The three proposed mutations would change **account defaults only**.

**Their actual effect:**

- **On campaigns `24103511039` and `24145053510`: none.** Not on bidding, not on the Conversions
  column, not on learning. Their campaign-level goals already carry the intended values.
- **On future campaigns: real.** A new campaign created at `goal_config_level: CUSTOMER` would
  today inherit **four non-biddable goals** and would have no biddable goal at all.

**Are they still independently desirable?** Yes, as **latent account hygiene** — but **DEFERRED,
not actioned here.** No new campaign is in the roadmap: the recommended architecture is one
campaign (`24103511039`, already CAMPAIGN-level), and PLAN-R6 creates ad groups inside it, not new
campaigns. **They must not be mutated to make the standard Conversions column appear different —
that is precisely the mistaken reasoning being retired.**

**Note also:** one of the three fields the September 1 action targeted at the action layer,
`include_in_conversions_metric`, **cannot be written at all**. Any plan built on it would have
failed with `IMMUTABLE_FIELD`.

---

## 8. Final technical verdict

# D — NO GOAL-CONFIGURATION DEFECT — CONTROLLED EVENT TEST REQUIRED

Not A: the customer goals are non-biddable but causally inert. Not B, C, D, or F: every one is
disproven by fresh read. Not E as a *defect* — E is the correct configuration. **Not E-plus-A as
"multiple independent defects", because a setting that governs nothing currently live is not a
defect in the measurement path; it is deferred hygiene.**

**Configuration eligibility is proven correct. Event firing is unknown. Those are different
things, and only the second one is still open.**

---

## 9. The one next action

# Run the controlled instrumented form-conversion test — PLAN-R1B.

**Not a configuration change.** No goal-layer or conversion-action mutation can create an event
that never fired, and none of the four layers is misconfigured. Per the decision order, step 1
(repair a proven controlling configuration defect) is **unavailable — there is no such defect**,
so step 2 applies.

**Design decision — instrumented synthetic-GCLID arrival, not a real ad click.** PLAN-A2's
preferred real-click path stays blocked: PRESENCE targeting on 80 New York locations means a real
GCLID needs a click from someone physically on Long Island during Mon–Sat 08:00–18:00, which
neither the agent nor a Florida-based approver can produce. The instrumented path is executable
today and satisfies every verification item required of this test — including the one a real click
alone would *not* answer, namely whether `AW-17878095007` also receives the event, which requires
network capture. It also writes **nothing** to Google Ads conversion history, preserving a clean
record in an account that has never recorded a conversion.

**Stated honestly:** a synthetic GCLID will not join to a real click, so `all_conversions` will
remain 0.00 after the test. **That is the expected result, not a failure.** The server-side join
remains PLAN-A2's job and remains blocked.

---

## 10. Plan created

**PLAN-R1B — Controlled instrumented form-conversion test**
`plans/2026-09-01-plan-r1b-controlled-form-test.yaml`

| | |
|---|---|
| Action count | **8** |
| Object count | **8** |
| **Google Ads mutation count** | **0** |
| External test-action count | **8** (6 read, **2 write**) |
| Forms submitted when executed | **1** |
| Calls placed | **0** |
| `validate_only` | **NOT APPLICABLE** — zero mutations, so no payload to validate; running it would burn the same daily mutate quota for no information |
| Validation | **46 / 46 checks pass**, duplicate-key-aware YAML, every asserted value re-confirmed by fresh read |
| **Fingerprint** | **`B7AD76CB16F8`** (recomputed twice, identical) |
| Full SHA-256 | `b7ad76cb16f812f164040e194f1efa0963e1d21ebfff3a0ca6660b21aa976545` |
| Status | **NOT APPROVED · DO NOT EXECUTE** |

**Test identity — already settled in this repository, not invented:** name `GM TEST DO NOT
CONTACT`; phone `631-555-0147` from the NANP reserved fictitious range 555-0100..555-0199, which
cannot ring a real person. The **test email** remains a pre-execution precondition carried forward
from PLAN-A2 (`A2-PRE-2`), with an RFC 2606 reserved address as the safe fallback. **No blocking
input is emitted for the phone number — it is settled.**

**PLAN-A2 is NOT superseded.** It stays approved-in-principle and blocked, as the instrument for
the server-side join whenever a Long Island click can be arranged.

---

## 11. Evidence discipline

| Distinction | State |
|---|---|
| **Configuration eligibility** | **PROVEN CORRECT** — goals and actions would count and would feed bidding |
| **Event firing** | **UNKNOWN** — what PLAN-R1B establishes |
| **Attribution** | **UNTESTABLE REMOTELY** — needs a real Long Island GCLID |
| **Reporting** | **CORRECT BY CONFIGURATION** — nothing to repair |
| **Bidding eligibility** | **PROVEN CORRECT** |
| **Actual lead generation** | **ZERO** |

> **USER-SUPPLIED WHATCONVERTS RECORDS REVIEWED — ZERO CONFIRMED RELEVANT POWER WASHING OR
> PRESSURE WASHING LEADS IN THE SUPPLIED ROWS.**

WhatConverts evidence **exists** and was reviewed. Tracking is **not** claimed to work merely
because tags are present, and it is **not** claimed to be broken merely because the account has
zero conversions — the zero is fully explained by zero real leads across 18 valid clicks, which
two independent sources agree on.

---

## 12. Safety

**Zero external changes.** Every Google Ads call was a `SELECT` through `GoogleAdsService.search`.
No operation object constructed, no mutate service called, no `validate_only` request issued.

Untouched and re-verified unchanged: campaign bidding · CPC ceilings · budgets · campaign names ·
campaign statuses · ad groups · keywords · negative keywords · RSAs · assets · locations ·
schedules · audiences · demographics · final URLs · landing pages · tracking templates · final URL
suffixes · custom parameters.

**GET_DIRECTIONS remains `biddable: false`** at customer level and on both campaigns — unchanged,
and PLAN-R1B changes nothing.

**No form was submitted. No call was placed. No website was modified.**

---

**CONVERSION MEASUREMENT DECISION COMPLETE — ONE APPROVAL-READY NEXT ACTION PRODUCED — ZERO
EXTERNAL CHANGES MADE**
