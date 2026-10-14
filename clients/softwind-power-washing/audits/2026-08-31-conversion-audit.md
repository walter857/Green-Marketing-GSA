# SOFTWIND POWER WASHING — CONVERSION AND MEASUREMENT AUDIT

**Generated:** 2026-08-31 10:21:20 America/New_York · Account `1521725229` · **READ-ONLY**

---

> **CONTINUATION RESTATEMENT — 2026-08-31 16:40.** A drift check at 16:40 found Google had
> retroactively invalidated **four of the five clicks** recorded that morning on
> `power washing services`, crediting back **$117.28**. The account ledger moved from
> **22 billable clicks / $713.15** to **18 billable clicks / $595.87**; invalid clicks rose
> 60 → 73, i.e. **80.2% of all raw clicks**. Every other day is byte-identical, conversions
> remain **0**, and no conclusion below changes — the traffic-quality finding is now confirmed
> by Google's own filtering.

---

## The one-paragraph answer

Zero conversions have been recorded on 18 billable clicks and $595.87. That single number
hides three separate facts, and conflating them produces the wrong fix. **(1)** The conversion
tag demonstrably fires — 16 users sit in the `All Converters` remarketing list. **(2)** No paid
click has produced a recorded conversion of any kind — `metrics.all_conversions` is 0.00 on
every campaign on every date. **(3)** The account's "Conversions" column is *structurally
incapable* of counting a lead even if one arrives, because every conversion action carries
`include_in_conversions_metric: FALSE`. Fact 3 is a real P0 defect that must be fixed, but
fixing it will not create leads. Fact 2 is the business problem.

---

## 1. Conversion action inventory — fresh read

| ID | Name | Status | Type | Category | Counting | Primary for goal | **In Conversions metric** | Click lookback | Call duration | Default value | Always default | Attribution | Origin | Tag snippets |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---:|
| `7708725995` | Softwind Power Washing \| Submission Lead Form | ENABLED | WEBPAGE | SUBMIT_LEAD_FORM | ONE_PER_CLICK | **TRUE** | **FALSE** | 90 d | 60 s | 0.0 | TRUE | GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN | WEBSITE | 4 |
| `7708765130` | Softwind Power Washing \| Website Phone Call Lead | ENABLED | WEBSITE_CALL | PHONE_CALL_LEAD | ONE_PER_CLICK | **TRUE** | **FALSE** | 30 d | 60 s | 0.0 | TRUE | GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN | WEBSITE | 1 |
| `7711699090` | Softwind Power Washing \| Call Asset Lead | ENABLED | AD_CALL | PHONE_CALL_LEAD | ONE_PER_CLICK | **TRUE** | **FALSE** | 30 d | 60 s | 0.0 | TRUE | GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN | CALL_FROM_ADS | 0 |
| `7713188607` | Local actions - Directions | ENABLED | GOOGLE_HOSTED | GET_DIRECTIONS | MANY_PER_CLICK | **TRUE** | **FALSE** | 30 d | 60 s | 1.0 | TRUE | GOOGLE_ADS_LAST_CLICK | GOOGLE_HOSTED | 0 |

**What is right about this architecture.** Three distinct lead actions, one per real outcome —
form, website call, call-from-ad. A 60-second qualified-call threshold on both call actions.
`ONE_PER_CLICK` counting on all three lead actions, so a single visitor cannot inflate the
count. A 90-day form window and 30-day call windows, both sensible for an estimate-driven home
service. **This was designed correctly.**

---

## 2. P0-1 — the Conversions column is structurally zeroed

### The finding

```
customer_conversion_goal
  PHONE_CALL_LEAD   / WEBSITE         biddable = FALSE
  PHONE_CALL_LEAD   / CALL_FROM_ADS   biddable = FALSE
  SUBMIT_LEAD_FORM  / WEBSITE         biddable = FALSE
  GET_DIRECTIONS    / GOOGLE_HOSTED   biddable = FALSE
```

**No conversion goal is biddable at ACCOUNT level.** That is why all four conversion actions
report `include_in_conversions_metric: FALSE`. The `metrics.conversions` column — the one the
Google Ads UI shows by default, the one every dashboard reads, the one every report quotes —
**excludes all four actions**. It will read 0.00 on a fully successful conversion.

### What is NOT affected

```
campaign_conversion_goal
  24103511039  PHONE_CALL_LEAD  / WEBSITE        biddable = TRUE
  24103511039  PHONE_CALL_LEAD  / CALL_FROM_ADS  biddable = TRUE
  24103511039  SUBMIT_LEAD_FORM / WEBSITE        biddable = TRUE
  24103511039  GET_DIRECTIONS   / GOOGLE_HOSTED  biddable = FALSE   <- correctly excluded
  24145053510  ... identical ...
```

**Bidding is fine.** Both campaigns override the account default with campaign-specific goals
where the three lead categories are biddable and Get Directions is correctly excluded. If the
account ever switches to Smart Bidding, it will optimise toward the right three outcomes.

### Why this matters anyway

1. **Every report lies by omission.** Any statement of the form "the account has 0 conversions"
   is unfalsifiable while this is true. A lead could arrive today and the column would still
   read 0.00.
2. **It hides the fix.** If a controlled test is run and verified against `metrics.conversions`,
   it will appear to fail even on success.
3. **It blocks Smart Bidding later.** A future migration to Maximize Conversions needs a clean
   conversion history in the metric the strategy reads.

### The verification rule

> **Query `metrics.all_conversions` segmented by `segments.conversion_action_name`.**
> `metrics.conversions` will read 0.00 even on a fully successful test.

---

## 3. Does the tag actually fire? — YES

| List ID | Name | Google's description | Type | Membership | **Size for Search** |
|---|---|---|---|---:|---:|
| `9446096870` | All visitors (AdWords) | People who visited pages that contain your remarketing tags | RULE_BASED | 30 d | 160 |
| `9447544308` | All visitors (AdWords) (system-defined) | same | RULE_BASED | 30 d | 160 |
| `9446154938` | AdWords optimized list | Combined audience based on available data sources | LOGICAL | 30 d | 160 |
| **`9446168598`** | **All Converters** | **"People who converted on your site."** | RULE_BASED | **180 d** | **16** |

**Sixteen distinct users have triggered a conversion on the Softwind site inside 180 days.**
The conversion tag is not dead, not misconfigured to the point of silence, and not absent.
`prepopulation_status` is `FINISHED`, so this is a settled figure, not a list still filling.

### The caveat, stated plainly

This list counts **all traffic sources over 180 days** — organic, direct, social, referral,
paid — and its size is a **rounded audience estimate**, not a lead count. It proves the tag
fires. It proves **nothing** about any specific paid click, and it must never be quoted as
"Softwind got 16 leads."

### What it does change

It moves the diagnosis. The question is no longer *"is tracking broken?"* — it is
**"why has none of 18 paid clicks converted, when site visitors do convert?"** That points at
traffic quality, landing-page conversion and sample size, not at the tag.

---

## 4. Have any paid conversions been recorded? — NO

| Query | Result |
|---|---|
| `metrics.conversions`, all campaigns, all dates | **0.00** |
| `metrics.all_conversions`, all campaigns, all dates | **0.00** |
| `FROM campaign` segmented by `segments.conversion_action_name`, 07-01 → 08-31 | **zero rows** |
| `FROM call_view`, no date filter (whole retained log) | **zero rows** |
| `segments.click_type = CALLS` | **86 impressions, 0 clicks, $0.00** |
| `segments.click_type = GET_DIRECTIONS` | 17 impressions, 0 clicks |
| `metrics.conversions_value` / `all_conversions_value` | $0.00 |

**The API omits all-zero segment rows**, so zero rows from a conversion-action segment means
nothing was recorded on any action — not a reporting gap.

**The call button has served 86 times and has never been clicked.** That is the single
strongest measurement fact in the account: there is no call to attribute, so the call path is
**untested**, not broken.

---

## 5. Conversion value is structurally zero

All three lead actions use `default_value: 0.0` with `always_use_default_value: TRUE`.

**Consequence:** conversion value, ROAS, revenue and profit-after-ad-spend are **impossible to
report** until client economics exist. `client.yaml` records `average_job_revenue`,
`gross_margin_pct`, `close_rate_pct`, `target_cpl`, `target_cpql` and `target_cac` all as
`null`.

**Formulae, once the inputs exist:**

| Metric | Formula | Blocked on |
|---|---|---|
| CPL | spend ÷ recorded leads | a non-zero lead count |
| CPQL | spend ÷ qualified leads | WhatConverts export + a qualification rule |
| CAC | spend ÷ sold jobs | CRM outcome data |
| ROAS | revenue ÷ spend | `average_job_revenue` |
| Gross profit | revenue × `gross_margin_pct` | `gross_margin_pct` |
| **Profit after ad spend** | (revenue × gross margin) − spend | both, plus sold-job counts |

**Costs currently missing from any profit figure:** agency management fee, WhatConverts
subscription, ClickCease subscription, landing-page hosting, and the cost of the sales time
spent quoting unsold jobs. None is in this repository.

---

## 6. Tag inventory on the live landing pages

Verified in a real Chromium browser, desktop and mobile, on 2026-08-31, with GCLID and UTMs
appended. These hosts sit behind SG-Captcha and serve non-JS clients an empty stub, so a
`curl` or plain fetch produces false findings.

| Tag | On all 6 offer pages | Status |
|---|---|---|
| `AW-18369652705` (this account) | YES | correct |
| **`AW-17878095007`** | **YES** | **P0 — a DIFFERENT Google Ads account. Owner unknown since 2026-08-25.** |
| `G-D4BZM40RYD` (GA4) | YES | expected |
| `GTM-P3LD97NN` (Tag Manager) | YES | expected |
| WhatConverts | YES | expected |
| ClickCease | YES | expected on the page — **but see below** |
| Facebook Pixel | YES | expected |

**Conversion label confirmed on 2026-08-27 (PLAN-A1):** action `7708725995` is technically
configured with 4 tag snippets — global site tag plus event snippet, label
`AW-18369652705/FddkCOul59scEOHPqrdE`.

### ClickCease is on the page but not in the account

`campaign_criterion` with `type = 'IP_BLOCK'` returns **zero rows on both campaigns**.
ClickCease's script loads on every landing page, but **it is syncing no IP exclusions into
Google Ads**. Against a backdrop of **73 invalid clicks vs 18 billable (80.2% of raw clicks)**
and today's five-clicks-on-one-impression event, that is worth the client checking: either the
Google Ads integration was never connected, or it is connected and has chosen to block nothing.

---

## 7. Click-ID and UTM preservation — PASS

| Page | HTTP | Redirects | GCLID survives | UTMs survive |
|---|---|---|---|---|
| `/power-washing-services-islip-west-islip-dix-hills/` | 200 | none | **PASS** | **PASS** |
| `/residential-pressure-washing/` | 200 | none | **PASS** | **PASS** |
| `/house-pressure-washing-estimate/` | 200 | none | **PASS** | **PASS** |
| `/driveway-pressure-washing/` | 200 | none | **PASS** | **PASS** |
| `/patio-power-washing/` | 200 | none | **PASS** | **PASS** |
| `/house-washing-company/` | 200 | none | **PASS** | **PASS** |
| `/soft-house-washing/` | 200 | none | **PASS** | **PASS** |
| `/power-washing-soft-washing/` | 200 | none | **PASS** | **PASS** |

Auto-tagging is `true` at account level; there is no tracking template, no final-URL suffix and
no custom parameter anywhere in the account to interfere.

**Click-ID preservation is not the failure point.**

---

## 8. Phone reconciliation

| Number | Where it appears | Verdict |
|---|---|---|
| **(631) 502-7946** | `tel:` link and body copy on all 6 offer pages, desktop and mobile · Google Ads call asset `403335872180` | **Approved and tracked** ✓ |
| (631) 502-5402 | `softwindli.com/our-work/`, `/service-areas/` | **UNTRACKED.** Destinations of 2 surviving account-level sitelinks. Latent leak — campaign-level sitelinks override them today. |
| (631) 553-5927 | not observed in this run | Recorded 2026-08-26 via the `wc_swap` cookie on main-site pages. Not re-confirmed; the offer pages render the static approved number in both the tel: link and body copy. |
| **+1 631-519-8373** (GLE — supplied in the brief) | **NOWHERE** in any Google Ads asset, `tel:` link or landing-page body text | **UNEXPLAINED — Q** |
| **+1 631-315-8655** (GBP — supplied in the brief) | **NOWHERE** | **UNEXPLAINED — Q** |

Two numbers named in the brief as *"Power Washing tracking numbers"* do not appear anywhere in
the audited surface. Either they are used somewhere outside Google Ads and this website
(a GBP listing, an LSA profile), or they are stale. **This must be resolved before any lead
count is trusted**, because a lead arriving on an unaudited number would be invisible to this
reconciliation.

---

## 9. WhatConverts reconciliation — CANNOT BE COMPLETED

A repository-wide search found **no WhatConverts export for this client**. The only such files
belong to other accounts. Machine-readable detail in
`2026-08-31-whatconverts-reconciliation.csv`.

**Blocker WC-1.** Without it:

- No lead can be counted as unique-new vs repeat vs support vs spam vs unrelated-service.
- No lead can be matched to a GCLID, campaign, ad group, keyword, device or landing page.
- Cost per qualified lead cannot be computed.
- The claim "zero leads" cannot be confirmed *or* refuted.

**What is needed:** the WhatConverts Power Washing profile export for **2026-08-01 → 2026-08-31**,
with columns for date/time, lead type (call / form), tracking number dialled, call duration,
call status, form fields, GCLID, UTM source/medium/campaign, landing page, and the quoted
service. PII stays in the export; only aggregates appear in any Green Marketing report.

**Counting rule once it arrives** — a lead counts as relevant when *either*:
- it requests Power Washing or Pressure Washing-related service, regardless of source; **or**
- it arrived on one of the approved Power Washing tracking numbers.

Then separate: unique new leads · repeat contacts · support calls · spam · unrelated services ·
qualified estimate requests.

---

## 10. Controlled tests — still blocked

### Form test (supersedes PLAN-A2 `3B30BD017E0C`, approved 2026-08-27, never submitted)

| Precondition | State |
|---|---|
| A2-PRE-1 — read-only inspection complete | **MET** |
| A2-PRE-2 — client-controlled plus-addressed email | **NOT MET** |
| A2-PRE-3 — client notified before a test lead reaches their inbox or CRM | **NOT MET** |
| A2-PRE-4 — named cleanup owner for the test record | **NOT MET** |
| **PRESENCE-targeting constraint** | **NOT SOLVABLE REMOTELY** |

**The binding constraint is PRESENCE targeting.** Both campaigns target 80 New York locations
with `PRESENCE` on both positive and negative geo settings. Producing a real GCLID needs a
click on a real ad by a person **physically on Long Island** during Mon–Sat 08:00–18:00.
Neither the agent nor a Florida-based approver can produce that. Without a real ad click there
is no real GCLID, Google records no conversion, and the GCLID-to-conversion join — the entire
point of the test — cannot be proven remotely.

**Settled so it need not be re-litigated:** test name `GM TEST DO NOT CONTACT`; test phone from
the **NANP reserved fictitious range 555-0100..555-0199** (e.g. 631-555-0147), because it
cannot ring a real person, so speed-to-lead automation cannot dial a stranger. The form test
covers the FORM path only; the phone path is a separate test.

### Call test

Blocked by the same PRESENCE constraint, and additionally: calling (631) 502-7946 rings the
client's real business line and needs their prior consent and a named recipient.

**No form was submitted and no call was placed during this audit.**

---

## 11. Findings, prioritised

| # | Severity | Finding | Fix |
|---|---|---|---|
| C-1 | **P0** | `customer_conversion_goal` biddable FALSE ×4 → all four actions `include_in_conversions_metric: FALSE` → the Conversions column cannot count a lead | PLAN-R1 T1 |
| C-2 | **P0** | Foreign tag `AW-17878095007` on all 6 offer pages + 2 main-site pages | PLAN-R1 T2 / PLAN-R7 F2 |
| C-3 | **P0** | No WhatConverts export exists — reconciliation impossible | PLAN-R1 T3 (WC-1) |
| C-4 | **P1** | Two phone numbers named in the brief appear nowhere in the audited surface | PLAN-R1 T4 |
| C-5 | **P1** | Call asset served 86× and never clicked; `call_view` empty | diagnostic — feeds PLAN-R3/R5/R7 |
| C-6 | **P1** | ClickCease loads on the page but syncs **zero** IP blocks into either campaign, against a 73.2% invalid-click rate | client to check the integration |
| C-7 | **P1** | Conversion value structurally $0.00 — no ROAS, no profit reporting possible | client economics (Q6) |
| C-8 | **P2** | `Local actions - Directions` is `primary_for_goal: TRUE` at account level with `MANY_PER_CLICK` counting — contained today only because both campaigns override it | demote when C-1 is fixed |
| C-9 | **P2** | Enhanced conversions for leads is `false` | consider after C-1 and a verified lead |
| C-10 | **P2** | WhatConverts DNI on the offer subdomain not re-confirmed this run | PLAN-R1 T5 (read-only, can run now) |

---

## 12. The sentence that must appear in any August report

> **No conversion was RECORDED.** That is not the same claim as *"the account produced no
> leads."* The Conversions column is structurally incapable of counting one, no WhatConverts
> export has been supplied, and the conversion tag demonstrably fires site-wide. What is
> certain is that **no paid click has produced a recorded conversion of any kind, across 22
> clicks and $595.87.**

---

**MEASUREMENT AUDIT COMPLETE — READ-ONLY, NO FORM SUBMITTED, NO CALL PLACED, NO CHANGE MADE**
