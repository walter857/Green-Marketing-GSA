# Softwind Power Washing — Conversion Tracking and Measurement Audit

**Account:** Softwind Power Washing - Live · `1521725229`
**Audit snapshot:** 2026-08-25 16:57:08 America/New_York
**Mode:** READ ONLY. No conversion action, goal, tag or page was changed.
**No form was submitted. No test call was placed.**

---

## 1. Account-level measurement settings

| Setting | Observed | Assessment |
|---|---|---|
| Conversion tracking ID | `18369652705` | Matches the `AW-18369652705` tag found on every landing page. |
| Conversion tracking status | `CONVERSION_TRACKING_MANAGED_BY_SELF` | Own tracking, not cross-account managed. Correct. |
| Conversion customer | `customers/1521725229` | Correct — this account owns its actions. |
| Auto-tagging | **enabled** | Correct. GCLID/GBRAID confirmed reaching the landing pages. |
| **Enhanced conversions for leads** | **DISABLED** | **Gap.** A lead-gen account with a phone+email form is the exact use case. |
| Account-level negative criteria | 1 `CONTENT_LABEL` | Irrelevant to Search. No hidden keyword suppression. |

---

## 2. The four conversion actions

| ID | Name | Type | Category | Origin | Primary for goal | Counting | Attribution | Click window | Call min |
|---|---|---|---|---|---|---|---|---|---|
| `7708725995` | Softwind Power Washing \| Submission Lead Form | WEBPAGE | SUBMIT_LEAD_FORM | WEBSITE | **true** | ONE_PER_CLICK | Data-driven | **90 d** | 60 s |
| `7708765130` | Softwind Power Washing \| Website Phone Call Lead | WEBSITE_CALL | PHONE_CALL_LEAD | WEBSITE | **true** | ONE_PER_CLICK | Data-driven | 30 d | 60 s |
| `7711699090` | Softwind Power Washing \| Call Asset Lead | AD_CALL | PHONE_CALL_LEAD | CALL_FROM_ADS | **true** | ONE_PER_CLICK | Data-driven | 30 d | 60 s |
| `7713188607` | **Local actions - Directions** | GOOGLE_HOSTED | GET_DIRECTIONS | GOOGLE_HOSTED | **true** | **MANY_PER_CLICK** | Last click | 30 d | — |

### What is right

The **three lead actions are correctly designed**: one action per real business outcome
(form / website call / call-asset call), `ONE_PER_CLICK` counting so a single lead cannot
inflate, a **60-second minimum call duration** on both call actions — a sensible qualified-
call threshold — and data-driven attribution with `data_driven_model_status: AVAILABLE`.

Website calls and call-asset calls are correctly held as **separate actions**, so a caller
who dials from the ad and a caller who dials from the site are not double-counted.

### What is wrong

**Finding C-1 — `Local actions - Directions` is marked `primary_for_goal: true` (P2).**
A Get Directions tap is a diagnostic, not a lead. It also counts `MANY_PER_CLICK`, so one
visitor can register it repeatedly.

*Contained, for now.* Both campaigns override with campaign-specific goals, and the
biddable set for each is exactly the three lead categories:

```
Power Washing      → PHONE_CALL_LEAD (WEBSITE), PHONE_CALL_LEAD (CALL_FROM_ADS), SUBMIT_LEAD_FORM (WEBSITE)
Power Washing #2   → PHONE_CALL_LEAD (WEBSITE), PHONE_CALL_LEAD (CALL_FROM_ADS), SUBMIT_LEAD_FORM (WEBSITE)
```

GET_DIRECTIONS is present in the goal table but **not biddable** on either campaign. So
bidding is correctly isolated today. The risk is that any new campaign created without
campaign-specific goals would inherit Directions as a primary conversion and start bidding
toward map taps.

**Finding C-2 — every lead is valued at $0.00 (P2).**
All three lead actions carry `default_value: 0.0` with `always_use_default_value: true`.

Consequences: conversion value is structurally always zero → **ROAS cannot be computed**,
value-based bidding (tROAS, Maximize Conversion Value) is impossible, and the profit
reporting required by Green Marketing policy — revenue, gross profit, profit after ad
spend — has no input. This blocks the measurement standard in `CLAUDE.md`, not just a
nice-to-have.

Fixing it needs a client fact that is currently **UNKNOWN**: average job revenue and gross
margin for power washing. Those are in `client.yaml` as `null` and must not be invented.

**Finding C-3 — inconsistent click-through windows (P3).**
Form = 90 days, calls = 30 days. Exterior washing is an estimate-driven sale where the
homeowner may take weeks to decide, so 90 is arguably right for the form — but the
mismatch means form and call leads are attributed over different horizons and are not
directly comparable in any report.

**Finding C-4 — `include_in_conversions_metric` returns `false` on all four actions (P2, verify).**
This is worth flagging honestly rather than over-claiming. Under the goal-based conversion
model the campaign-level goal set governs what is bid toward and what lands in the
Conversions column, and that set is correct. But with **zero recorded conversions of any
kind**, the API alone cannot distinguish "correctly configured, nothing has happened yet"
from "configured such that nothing will ever be counted."

This must be resolved by a live Tag Assistant or end-to-end test before any Smart Bidding
change is considered. See section 5.

---

## 3. Recorded conversion volume — all time

| Action | Conversions | All conversions | Value |
|---|---:|---:|---:|
| Submission Lead Form | 0 | **0** | $0 |
| Website Phone Call Lead | 0 | **0** | $0 |
| Call Asset Lead | 0 | **0** | $0 |
| Local actions - Directions | 0 | **0** | $0 |

Supporting signals: `metrics.phone_calls` = **0** across **107 phone impressions**;
`segments.conversion_action_name` returns **zero rows** for the whole period; the
call-asset click type recorded **35 impressions and 0 clicks**.

**Read this carefully.** Zero conversions on **6 total clicks** is not evidence that
tracking is broken. At any plausible local-service conversion rate (5–15%), six clicks
should be expected to produce **0.3 to 0.9 leads**. Zero is entirely consistent with
correctly-working tracking and a sample far too small to say anything.

It is equally consistent with tracking that has never fired. **The API cannot tell these
apart, and this audit does not claim to.**

---

## 4. Landing-page tag inventory — verified in a real browser

Checked with Playwright at desktop (1440×900) and mobile (iPhone 13) viewports. These
hosts sit behind SG-Captcha, which serves non-JS clients an empty stub — a plain fetch
would have produced a false "no tracking" finding.

All six offer landing pages returned HTTP 200, no redirects, and carry an identical stack:

| Tracker | Value | Assessment |
|---|---|---|
| Google Ads gtag | **`AW-18369652705`** | Correct — matches this account. |
| Google Ads gtag | **`AW-17878095007`** | **A SECOND, DIFFERENT Google Ads account.** See C-5. |
| GA4 | `G-D4BZM40RYD` | Present. |
| Google Tag Manager | `GTM-P3LD97NN` | Present. |
| WhatConverts | present | Call/form tracking platform. |
| ClickCease | present | Click-fraud filtering. |
| Facebook Pixel | present | Present. |

**Click-ID preservation: PASS.** A synthetic `gclid` plus UTMs survived intact to the final
URL on all six pages (`gclid=…&utm_source=google&utm_medium=cpc&utm_campaign=audit`), with
no redirect stripping them. Combined with auto-tagging enabled, the attribution chain into
the CRM is structurally sound.

**Finding C-5 — a second Google Ads conversion ID fires on every landing page (P1).**
`AW-17878095007` is not this account. Every paid visit is being reported to a second
Google Ads account. Depending on that account's configuration this can duplicate
conversion credit, leak this client's audience and conversion data, and make any future
cross-account attribution unreliable. This needs identification and a decision before any
Smart Bidding migration.

**Finding C-6 — no conversion label was observable at page load (informational).**
The `AW-…/label` pattern does not appear in the initial DOM, which is expected if the form
conversion fires as a GTM event on submit rather than on page view. It means page-load
inspection alone **cannot confirm the form conversion fires.** Only a submission test can.

---

## 5. What still needs a live test

**END-TO-END TEST REQUIRES SEPARATE APPROVAL.**

Confirming the form and call conversions actually fire requires actions this READ-only
work order does not authorise and that would create real artifacts in the client's CRM and
phone system:

| Test | Why it needs approval |
|---|---|
| Submit a real lead form on an offer page | Creates a live lead in Gravity Forms / WhatConverts / the CRM and may trigger a sales follow-up to a fake person |
| Place a call to (631) 502-7946 lasting >60 s | Rings the client's real phone and creates a billable tracked call |
| Tag Assistant / GTM preview session | Needs Google Tag Manager access, which this work order does not hold |

Recommended sequence once approved: GTM preview first (no artifacts created), then a single
clearly-marked test form submission, then a single test call, verifying each against the
Google Ads conversion action within 24 hours.

**Until that test passes, no Smart Bidding change should be made.** Migrating to Maximize
Conversions or tCPA on a conversion signal that has never once fired would hand bidding to
a model with no data.

---

## 6. Phone number integrity

| Location | Number | Status |
|---|---|---|
| Google Ads call asset `403335872180` | **(631) 502-7946** | Matches the approved tracking number. |
| All six offer landing pages (`tel:` links and body copy) | **(631) 502-7946** | Correct and consistent. |
| `softwindli.com/contact-us/` | **(631) 502-5402** | **Different, untracked number.** |
| `softwindli.com/our-work/` | (631) 502-5402 | Untracked. |
| `softwindli.com/service-areas/` | (631) 502-5402 | Untracked. |
| `softwindli.com/reviews/` | (631) 502-5402 | Untracked. |
| `softwindli.com/services/landscaping/pressure-washing/` | (631) 502-5402 | Untracked. |

**Finding C-7 — sitelinks route paid traffic to pages showing an untracked phone number (P1).**

The four campaign sitelinks (Customer Reviews, Contact Us, Our Work, Service Areas) and the
account-level "Pressure Washing" sitelink all point to `softwindli.com`, where the displayed
number is **(631) 502-5402** — not the tracked (631) 502-7946.

This is not hypothetical. It has already happened:

- `SITELINKS` click type: **40 impressions, 1 click, $40.07**
- That click landed on `softwindli.com/services/landscaping/pressure-washing/`
- **$40.07 = 23% of all money this account has ever spent** went to a page where a
  resulting phone call would be **invisible to Google Ads, to WhatConverts, and to this
  campaign's reporting**

Call-asset configuration itself is correct: `call_conversion_reporting_state:
USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION`, country US. The asset is linked to **both**
campaigns — so any future call-asset schedule change would rewrite hours on both at once.

---

## 7. Measurement scorecard

| Requirement (`CLAUDE.md` conversion policy) | Status |
|---|---|
| Primary bidding conversions separated from secondary diagnostics | **PASS** at campaign level; **FAIL** at account level (Directions is primary_for_goal) |
| Form lead tracked | Configured; **unverified** — never fired |
| Qualified call tracked with a duration threshold | Configured, 60 s; **unverified** — never fired |
| Qualified / closed-won offline outcome | **ABSENT** — no offline import, no CRM stage mapping |
| Deduplicated by lead or transaction ID | **UNKNOWN** — not observable from the API or page load |
| GCLID / GBRAID / WBRAID / UTMs preserved | **PASS** — verified end-to-end in a real browser |
| Campaign, ad group, keyword, device, landing page kept in the CRM | **UNKNOWN** — no CRM access under this work order |
| Consent status captured | **UNKNOWN** — no consent-mode signal observed |
| Conversion values set | **FAIL** — all leads valued $0.00 |
| Dashboard: spend, leads, qualified leads, sales, revenue, gross profit, CPL, CPQL, CAC, ROAS, profit after ad spend | **BLOCKED** — no lead volume, no conversion value, no client economics |

### Client facts still UNKNOWN and needed before measurement can be completed

- Average job revenue for power washing
- Gross margin percentage
- Lead-to-sale close rate
- Target CPL / CPQL / CAC
- CRM in use and its stage names
- Whether WhatConverts is the system of record for leads
- Who owns Google Ads account `17878095007`
