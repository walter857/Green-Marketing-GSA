# Ambient Cooling & Heating — Full Launch Audit

**Client:** Ambient Cooling & Heating LLC
**Vertical:** heating-cooling
**Services in scope:** AC Repair, HVAC Repair, HVAC Installation, HVAC Replacement, Gas Boiler Repair
**Audit mode:** READ ONLY
**Audit date:** 2026-08-17
**Account timezone:** America/New_York
**Campaign launch date:** Friday, 2026-08-14

> **No external changes were made.** No Google Ads object was created, edited, paused, enabled,
> or deleted. No GTM container, tag, trigger, variable, version, or workspace was touched. No
> website, form, CRM, call-tracking, budget, or campaign-status change was made. No form was
> submitted and no phone link was clicked or dialed. Every Google Ads call was a GAQL `SELECT`;
> every web call was an HTTP `GET`.

---

## 1. Final verdict

# ⛔ FAIL — and the entire Google Ads account audit is BLOCKED

Two separate verdicts, because they have two separate causes:

| Scope | Verdict | Basis |
|---|---|---|
| **Google Ads account audit** | **BLOCKED** | The mandatory identity gate failed. The child account **name** does not match, so no campaign, keyword, ad, asset, budget, conversion, or performance data was read. |
| **Tracking and landing pages** | **FAIL** | Independently verified. Conversion tracking is **entirely absent** from all five paid landing pages, and the primary mobile call CTA dials the **wrong phone number** on all five pages. |

The landing-page and tracking half of this audit needed no account access, so it was completed
in full. It failed on confirmed, reproducible evidence.

---

## 2. Executive summary

**The campaigns cannot be measured, and mobile callers are being sent to the wrong number.**

1. **The Google Ads identity gate failed and I stopped.** Customer ID `2401959466` is exactly
   correct, but its name in Google Ads is **`Ambient Cooling`**, not the expected
   **`Ambient Cooling & Heating`**, and it lacks the `- live` marker that agency policy requires.
   Per `CLAUDE.md` I stopped the account-specific audit and did not select any other account.
   A second enabled account, **`OLD Ambient C&H` (2391758435)**, also exists under the same
   manager — exactly the ambiguity this gate exists to catch. **One written confirmation from
   Green Marketing unblocks the whole account audit.**

2. **There is no conversion tracking on any paid landing page.** This is not "GTM did not fire".
   There is no tag of any kind: zero requests to `googletagmanager.com`, no `dataLayer`, no
   `google_tag_manager` object, no `gtag()`, and no `GTM-`, `AW-`, `G-`, or `UA-` identifier
   anywhere in the rendered HTML of any of the five pages. The only third-party host requested
   is Google Fonts. **Every form lead and every call from these pages is currently invisible to
   Google Ads.**

3. **Root cause found.** The approved container `GTM-PQTPQ436` **is** present on the main site
   `ambientcoolingandheating.com`. It was never deployed to the `offer.` subdomain where all
   paid traffic lands. The same copy/paste gap explains the phone defect: the wrong number
   `(410) 761-0932` is the **main site's** number, leaking onto the paid pages.

4. **The primary mobile "Call Now" button dials the wrong number on all five pages.** The button
   is `display:none` on desktop (0×0 px) but **visible and tappable on mobile** (175×37 px) —
   the exact device where calls happen. It is the visually dominant yellow CTA, sitting directly
   above the correct green button. Mobile call volume is being routed off the approved paid line
   and off attribution entirely.

5. **Every previously reported landing-page defect was independently retested. 12 of 13 are
   CONFIRMED**, one is corrected in scope (the earlier report understated the GTM problem — the
   container is not merely failing to load, it is not installed). Two **new** defects were found
   that were not in the prior list: the wrong number also appears in **FAQ body copy** on three
   pages, and the countdown deadline is set in **UTC**, not Eastern.

6. **No profitability verdict is possible**, and no early-performance verdict is possible. No
   target CPL, CPQL, or qualified-lead data was supplied, and the performance read is blocked.
   Even once unblocked, three days of data would not support a profitability conclusion.

---

## 3. Account identity evidence

### 3.1 What was checked

Fresh read-only GAQL `SELECT ... FROM customer` against customer `2401959466`, plus a
`FROM customer_client` lookup from the configured manager. Executed 2026-08-17.

| Field | Expected (assignment) | Observed (fresh API read) | Match |
|---|---|---|---|
| Child customer ID | `240-195-9466` → `2401959466` | `2401959466` | ✅ **exact** |
| Child account name | `Ambient Cooling & Heating` | **`Ambient Cooling`** | ❌ **MISMATCH** |
| `- live` marker required by `config/agency.yaml` | present | **absent** | ❌ **MISSING** |
| Vertical | heating-cooling | n/a (not an API field) | — |
| Currency | — | `USD` | ✅ |
| Timezone | `America/New_York` | `America/New_York` | ✅ |
| Account status | — | `ENABLED` | ✅ |
| Is manager account | false | `False` | ✅ |
| Is test account | false | `False` | ✅ |
| Auto-tagging | — | `True` | ✅ |
| Manager link | under GM MCC | level `1`, status `ENABLED` | ✅ |

### 3.2 Why this stopped the audit

`CLAUDE.md` states: *"Stop on any name, ID, service, or vertical mismatch"* and *"The account
name must contain `- live` for a Green Marketing managed account."* The assignment restated the
same rule: *"If the observed account name or ID does not match, stop the account-specific audit
and clearly report the mismatch. Never select another account."*

Two independent gate rules failed. I stopped.

**The `- live` convention is real and in active use**, so its absence here is meaningful rather
than a project-wide non-convention:

- 33 enabled accounts are visible under manager `3373711342`.
- **11 of them carry the `- live` marker.**

### 3.3 The ambiguity that makes this worth stopping for

Only two accounts under the manager contain "ambient":

| Customer ID | Descriptive name | Level | Status | Manager | Test |
|---|---|---|---|---|---|
| `2401959466` | `Ambient Cooling` | 1 | ENABLED | false | false |
| `2391758435` | **`OLD Ambient C&H`** | 1 | **ENABLED** | false | false |

Neither is named `Ambient Cooling & Heating`. A second, still-**ENABLED** legacy account exists
for what appears to be the same business. This is precisely the scenario the identity gate
protects against, and it is also a **budget-leakage risk worth checking** once access is
confirmed — a still-enabled legacy account can serve and spend.

> `OLD Ambient C&H` was observed **only** in the account-selection listing, which is the
> permitted discovery step. It was **not** read, audited, or selected.

### 3.4 Circumstantial evidence that `2401959466` is the right business

Recorded for the decision-maker's benefit. **It does not satisfy the gate** and I did not act on it:

- The account-level tracking template contains `ccpturl=offer.ambientcoolingandheating.com`.
- The ID matches the assignment exactly.
- Currency and timezone match.

### 3.5 Work-order validator result

```
$ python scripts/validate_work_order.py \
    clients/ambient-cooling-heating/work-order.yaml \
    --client clients/ambient-cooling-heating/client.yaml

Work order is not ready:
- work_order.account.exact_child_account_name must contain '- live'
EXIT=1
```

Exactly one blocker, and it is the identity blocker. The work order and client profile are
otherwise complete and internally consistent. **I deliberately did not edit the name to force a
pass** — that would defeat the gate.

### 3.6 Additional account-level facts captured during the identity read

These came from the identity query itself, which is part of the gate and therefore permitted.
They are **not** a substitute for the blocked account audit.

| Field | Value | Note |
|---|---|---|
| Conversion tracking ID | `11155434808` | A conversion tracking setup **does** exist in the account |
| Conversion tracking status | `CONVERSION_TRACKING_MANAGED_BY_SELF` | Not manager-managed |
| Cross-account conversion tracking ID | `0` | Not using cross-account conversions |
| Optimization score | `0.9679` | Not a business outcome; recorded only |
| Pay-per-conversion eligibility failures | `HAS_UPLOAD_CLICKS_CONVERSION`, `NOT_ENOUGH_CONVERSIONS` | Indicates an **upload-clicks (offline) conversion action exists** and conversion volume is low |
| Account tracking URL template | ClickCease redirect (`monitor.clickcease.com`) | ⚠️ See P1-6 |
| Final URL suffix | *(empty)* | No suffix-based attribution |

⚠️ **The account routes every click through a ClickCease redirect**, while the landing pages
carry **no** tracking tags at all. The full template is:

```
https://monitor.clickcease.com/tracker/tracker.aspx?id=Y6qzID4E9cPYCj&adpos={adposition}
&locphisical={loc_physical_ms}&locinterest={loc_interest_ms}&adgrp={adgroupid}&kw={keyword}
&nw={network}&url={lpurl}&cpn={campaignid}&device={device}&ccpturl=offer.ambientcoolingandheating.com
&pl={placement}
```

A third-party redirect in front of every click, combined with zero tags on the destination, is a
compounding attribution risk. Verifying that this redirect preserves `gclid`/`gbraid`/`wbraid`
should be a priority once the account is unblocked.

---

## 4. Campaign performance table

**BLOCKED — no performance data was read.**

The following were requested and are **all pending** the identity resolution: impressions,
clicks, cost, CTR, average CPC, conversions, all conversions, conversion rate, cost per
conversion, phone calls, form leads, search impression share, search top IS, search absolute
top IS, lost IS (budget), and lost IS (rank) — for each campaign, ad group, keyword, ad,
device, network, and conversion action, across:

| Window | Range | Status |
|---|---|---|
| Launch to date | 2026-08-14 → 2026-08-17 | BLOCKED |
| Today | 2026-08-17 | BLOCKED |
| Last 7 days | 2026-08-10 → 2026-08-16 | BLOCKED |
| Last 30 days (account context) | 2026-07-18 → 2026-08-16 | BLOCKED |
| Last 90 days (historical search terms/conversions) | 2026-05-19 → 2026-08-16 | BLOCKED |
| Day and hour segmentation (approved-hours check) | launch → date | BLOCKED |

**Even when unblocked, three days of data cannot support a performance verdict.** The correct
early read separates configuration health from delivery health from outcome, and treats the
outcome column as insufficient data.

---

## 5. Campaign configuration matrix

**BLOCKED — no campaign was read.** Expected values are recorded so the comparison can run
immediately on unblock.

| Setting | Expected | Observed |
|---|---|---|
| Campaign name / resource ID | 5 campaigns, one per service | BLOCKED |
| Status / serving status | ENABLED, serving | BLOCKED |
| Start date | 2026-08-14 | BLOCKED |
| Campaign type | Search only | BLOCKED |
| Bidding strategy | per approved blueprint | BLOCKED |
| Daily budget | see §7 | BLOCKED |
| Search Network | on | BLOCKED |
| **Search Partners** | **off** | BLOCKED |
| **Display expansion** | **off** | BLOCKED |
| **AI Max** | **off** | BLOCKED |
| **Broad-match expansion** | **off** | BLOCKED |
| **DSA** | **off** | BLOCKED |
| **Final URL expansion** | **off** | BLOCKED |
| **Automatically created assets** | **off** | BLOCKED |
| **Text customization** | **off** | BLOCKED |
| Location targeting method | **PRESENCE** | BLOCKED |
| Location target count | **75 Maryland targets** | BLOCKED |
| Ad schedule | Mon–Fri 08:00–16:00 ET | BLOCKED |
| Device performance / adjustments | — | BLOCKED |
| Audience settings | — | BLOCKED |
| Policy problems | none | BLOCKED |
| Account-level negative lists | — | BLOCKED |
| Shared budgets | — | BLOCKED |
| Account-level assets | — | BLOCKED |
| Auto-applied recommendations | off | BLOCKED |
| Unrelated campaigns spending | none | BLOCKED — ⚠️ but see `OLD Ambient C&H` in §3.3 |

⚠️ **Landing-page evidence contradicts the expected ad schedule.** The pages advertise a
`(410) 705-6354` call CTA with no stated hours, while the expected schedule is Mon–Fri
08:00–16:00 ET. If the campaigns only serve 8–4 on weekdays, the mobile call CTA is only
reachable by paid traffic in that window — but the pages imply always-on availability. This
needs an operational answer (see §15, Q3).

---

## 6. Ad group, keyword, negative, RSA, and asset findings

**BLOCKED — no ad group, keyword, negative, RSA, or asset was read.**

Pending checks: ad-group count and naming, one tight service intent per ad group, Phrase/Exact
only, no Broad Match, no duplicate keywords, no keywords in the wrong campaign, no negative
conflicts blocking approved keywords, no cross-service leakage, keyword approval status,
Quality Score components, search impression share, search terms since launch, and 30/90-day
historical terms.

Expected canonical themes: `ac repair near me`, `hvac repair near me`, `hvac installers`,
`hvac replacement near me`, `gas boiler repair`.

**Search-term classification (KEEP / WATCH / NEGATIVE CANDIDATE) could not be performed** — no
search terms were read. No negatives were added; none would be added in READ mode regardless.
The protected-term rule stands: `near me`, `quote`, `price`, `pricing`, `cost`, `best`, `hire`,
`local`, and `emergency` must not be auto-negatived.

### What the landing pages already tell us about ad/LP alignment

This much **is** verified, and one item is a real alignment defect:

| Page | H1 | Aligns with intended theme? |
|---|---|---|
| ac-repair | AC Repair in Severn, Severna Park & Columbia, MD | ✅ |
| hvac-repair | HVAC Repair in Severn, Severna Park & Columbia, MD | ✅ |
| hvac-installation | **HVAC Installers** in Severn, Severna Park & Columbia, MD | ✅ matches `hvac installers` |
| hvac-replacement | HVAC Replacement in Severn, Severna Park & Columbia, MD | ✅ |
| gas-boiler-repair | Gas Boiler Repair in Severn, Severna Park & Columbia, MD | ✅ |

✅ **Ad copy correctly avoids awkward "near me" repetition.** No landing-page headline or CTA
repeats "near me"; the H1s use natural city phrasing. This satisfies the agency copy rule.

❌ Two **cross-service content leaks** in section headings — see P1-3 and P1-4.

---

## 7. Budget pacing and projection

**BLOCKED — live daily budgets and spend could not be read.**

I searched the repository for an authoritative approved campaign blueprint for this client.
**None exists.** `clients/ambient-cooling-heating/` did not exist before this audit; there is no
`plans/campaign-blueprint-*.yaml`, no approval bundle, and no pause/create receipt. The only
blueprints in the repo belong to `ekg-lawn-services` and `pro-green-dallas`.

**Therefore the $13,000 figure could not be reconciled against an approved artifact — only
against the assignment text.**

| Campaign | Planning allocation | Implied daily (÷31) | Implied daily (Aug 14–31, 18 days) | Live daily budget | Variance |
|---|---:|---:|---:|---|---|
| AC Repair | $4,300 | $138.71 | $238.89 | BLOCKED | BLOCKED |
| HVAC Repair | $2,400 | $77.42 | $133.33 | BLOCKED | BLOCKED |
| HVAC Installation | $4,200 | $135.48 | $233.33 | BLOCKED | BLOCKED |
| HVAC Replacement | $800 | $25.81 | $44.44 | BLOCKED | BLOCKED |
| Gas Boiler Repair | $1,300 | $41.94 | $72.22 | BLOCKED | BLOCKED |
| **Total** | **$13,000** | **$419.35** | **$722.22** | BLOCKED | BLOCKED |

⚠️ **The conversion basis is itself an open question and materially changes the answer.** The
assignment does not say whether $13,000 is a **full-month** budget or a budget for the
**Aug 14–31 launch period**. The two readings differ by **72%** in daily budget. If the
campaigns were built on the wrong basis, they are either badly underspending or badly
overspending right now. This is the single most important budget question and it needs an
answer regardless of the identity blocker (see §15, Q2).

Also unread: spend since launch, current daily pace, projected period-end spend, variance,
budget-limited status, lost IS (budget), and lost IS (rank).

**No budget was changed.**

---

## 8. Conversion-action inventory

**BLOCKED at the account level.** Name, resource ID, source, category, primary/secondary status,
inclusion in account-default goals, use by the five campaigns, status, counting method,
attribution model, click-through and view-through windows, recent activity, tag diagnostics,
Enhanced Conversions status, and duplicate/competing actions were all **not read**.

### What is verified, and it is decisive

**Whatever conversion actions exist in the account, the five paid landing pages cannot fire any
of them.** Verified by full browser render of all five pages (§10.2). There is no tag, no
`dataLayer`, and no Google identifier on any page.

Two facts from the identity read sharpen this:

- `HAS_UPLOAD_CLICKS_CONVERSION` — an **offline/upload** conversion action exists.
- `NOT_ENOUGH_CONVERSIONS` — conversion volume is low.

### Lead-event taxonomy — none of these are currently measurable

The assignment correctly requires distinguishing these. **None is currently tracked:**

| Event type | Tracked today? | Note |
|---|---|---|
| Click-to-call event (`tel:` tap) | ❌ No | No tag. And a tap is **not** a completed call — it must never be counted as one. |
| Google Ads call-asset call | ❓ BLOCKED | Requires the account read |
| Website call via Google forwarding number | ❌ No | No forwarding number and no call script on any page |
| Completed qualified call | ❌ No | No call tracking, so no duration or disposition exists |
| Offline qualified lead / sale | ❓ BLOCKED | An upload-clicks action exists; its feed is unverified |

### Duplicate-counting risk

**Cannot be assessed today because nothing fires at all.** However, the page structure creates a
serious *latent* duplicate risk that must be resolved before any tag is deployed: **three
identical copies of Gravity Form 1 exist in the DOM of every page** (§10.4). A naive
form-submission trigger would be ambiguous across three identical `#gform_1` nodes. Any future
form conversion must key on a **confirmed successful submission with a unique lead ID**, not on
page load, form visibility, CTA click, submit-button click, validation error, a duplicate form
instance, or a thank-you reload.

**Thank-you behavior (checked without submitting):** forms post back to the same URL
(`method="post"`, `action="/ac-repair/"`, `gform_submission_method=postback`). There is **no
separate thank-you URL**, so a URL-based conversion trigger is not available. Confirmation
renders inline. A `gform_confirmation_loaded` style event plus a unique entry ID is the correct
basis. **No form was submitted during this audit.**

---

## 9. GTM tag, trigger, and variable inventory

**Container audited: `GTM-PQTPQ436` — read-only.**
**No tag, trigger, variable, version, or workspace was created, edited, published, paused, or deleted.**

### 9.1 Access limitation

Direct GTM container access was **not available** — no Tag Manager API credential is configured
in this project (`credentials.py` provisions Google Ads scopes only; `config/google-drive.yaml`
covers Drive/Docs). Per the assignment I completed all possible browser and source-code checks
instead. **The container's internal tag/trigger/variable list could not be enumerated.**

That limitation turned out not to matter for the verdict, because the container never loads.

### 9.2 Verified by full browser render — all five pages, desktop and mobile

| Check | Expected | Observed | Result |
|---|---|---|---|
| GTM script once in `<head>` | present | **absent** | ❌ FAIL |
| Noscript iframe immediately after `<body>` | present | **absent — zero `<noscript>` blocks** | ❌ FAIL |
| Browser requests `gtm.js?id=GTM-PQTPQ436` | yes | **0 requests to googletagmanager.com** | ❌ FAIL |
| `dataLayer` initializes | yes | `Array.isArray(dataLayer) === false`, length 0 | ❌ FAIL |
| Correct container on all five pages | yes | **no container on any page** | ❌ FAIL |
| `window.google_tag_manager` | populated | `[]` (empty) | ❌ FAIL |
| No duplicate GTM containers | pass | ✅ vacuously — zero containers | ⚠️ N/A |
| No conflicting hardcoded Google tags | pass | ✅ none — no `AW-`, `G-`, or `UA-` id anywhere | ✅ |
| Google tag / configuration tag | present | absent | ❌ FAIL |
| Google Ads Conversion Linker | present | absent | ❌ FAIL |
| Form conversion tag | present | absent | ❌ FAIL |
| Call / click-to-call tag | present | absent | ❌ FAIL |
| Consent Mode signals | present | absent | ❌ FAIL |
| Enhanced Conversions | configured | absent | ❌ FAIL |
| Deduplication method | defined | absent | ❌ FAIL |
| Cross-domain configuration | configured | absent | ❌ FAIL |
| GCLID / GBRAID / WBRAID / UTM persistence | captured | **not captured** — see §10.5 | ❌ FAIL |

**Complete third-party host list requested by the pages:** `fonts.googleapis.com`,
`fonts.gstatic.com`. That is all. (`d1rozh26tys225.cloudfront.net` appeared on one ac-repair
load only and did not recur.)

**29 external scripts load per page** — all first-party WordPress, Divi 5.10.1, Gravity Forms
3.0.2, and the `dynamic-offer-countdown` plugin. **Not one analytics or advertising tag.**

### 9.3 Root cause

| Property | `GTM-PQTPQ436` in HTML | Container initialized | Phone used |
|---|---|---|---|
| `ambientcoolingandheating.com` (main site) | ✅ **yes** | no (see note) | `(410) 761-0932` |
| `offer.ambientcoolingandheating.com` (all 5 paid pages) | ❌ **no** | no | `(410) 705-6354` + wrong number |

**The container was deployed to the main site and never to the offer subdomain.** The main site
also carries `G-9X9ZHNCRWF`. The offer subdomain is a separate WordPress install and inherited
none of it.

> Note: on my render the main site's container also did not initialize (`google_tag_manager`
> empty, `dataLayer` false) despite the ID being present in HTML. The main site is outside this
> audit's scope, but this is worth a separate look — it may indicate a broken snippet there too.

**Correction to the prior inspection:** the earlier note said "GTM-PQTPQ436 did not appear to
load." That understates it. The container is **not installed on the offer subdomain at all**.
The distinction matters: this is a deployment task, not a debugging task.

### 9.4 WhatConverts

**Correctly absent, and not reported as an error**, per the assignment. WhatConverts is not the
selected platform for this account.

---

## 10. Landing-page QA table — all five pages

Method: real Chrome render, desktop (1440×900) and mobile (390×844, 2× DPR), with a test query
string `?gclid=TESTGCLID12345&gbraid=…&wbraid=…&utm_source=google&utm_medium=cpc&…`.

> **Host bot protection:** `offer.ambientcoolingandheating.com` sits behind SiteGround SG-Captcha,
> which returns HTTP 202 + a JS challenge to non-browser clients. Plain HTTP clients cannot read
> these pages. All findings below come from a **real browser** that cleared the challenge. Worth
> knowing: **naive uptime or SEO monitors will see 202/403, not the page.**

### 10.1 Per-page summary

| Check | ac-repair | hvac-repair | hvac-installation | hvac-replacement | gas-boiler-repair |
|---|---|---|---|---|---|
| HTTP (browser) | 200 | 200 | 200 | 200 | 200 |
| Redirect chain | none | none | none | none | none |
| HTTPS / cert valid | ✅ | ✅ | ✅ | ✅ | ✅ |
| Canonical correct & self-referencing | ✅ | ✅ | ✅ | ✅ | ✅ |
| `robots` | `noindex, nofollow` ✅ | ✅ | ✅ | ✅ | ✅ |
| Title | ✅ | ✅ | ✅ | ✅ | ✅ |
| H1 service-specific | ✅ | ✅ | ✅ | ✅ | ✅ |
| Keyword/ad/LP alignment | ✅ | ⚠️ §P1-3 | ✅ | ✅ | ⚠️ §P1-4 |
| **GTM loads** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Attribution fields populated** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Wrong `tel:` present** | ❌ 2× | ❌ 2× | ❌ 2× | ❌ 1× | ❌ 1× |
| Privacy Policy link | ❌ none | ❌ none | ❌ none | ❌ none | ❌ none |
| Terms link | ❌ none | ❌ none | ❌ none | ❌ none | ❌ none |
| Gravity Form copies | ❌ 3 | ❌ 3 | ❌ 3 | ❌ 3 | ❌ 3 |
| Duplicate DOM IDs | ❌ 34 | ❌ 34 | ❌ 34 | ❌ 34 | ❌ 34 |
| Phone placeholder `(712) 555-0123` | ❌ | ❌ | ❌ | ❌ | ❌ |
| Textarea optional/required conflict | ❌ | ❌ | ❌ | ❌ | ❌ |
| Countdown vs "before today ends" | ⚠️ | ⚠️ | ❌ | ❌ | ❌ |
| Pinch-to-zoom disabled | ❌ | ❌ | ❌ | ❌ | ❌ |
| Structured data present | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| Broken images | ✅ 0 | ✅ 0 | ✅ 0 | ✅ 0 | ✅ 0 |
| Desktop layout | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mobile layout | ⚠️ CTA overlap | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Form visible & usable | ✅ | ✅ | ✅ | ✅ | ✅ |

### 10.2 Tracking (all five pages, both viewports)

```
network requests to googletagmanager.com : []
window.google_tag_manager containers     : []
dataLayer exists / length                : False / 0
gtag() defined                           : False
GTM- ids anywhere in rendered HTML       : []
AW-/G-/UA- ids anywhere in rendered HTML : []
<noscript> blocks                        : none
```

### 10.3 Page speed and technical health

| Page | TTFB | DOMContentLoaded | Load | FCP | Requests | Transfer |
|---|---:|---:|---:|---:|---:|---:|
| ac-repair | 117 ms | 537 ms | 785 ms | 660 ms | 63 | 3,156 KB |
| hvac-repair | 76 ms | 378 ms | 430 ms | 332 ms | 63 | 682 KB |
| hvac-installation | 106 ms | 430 ms | 470 ms | 368 ms | 64 | 586 KB |
| hvac-replacement | 280 ms | 671 ms | 754 ms | 576 ms | 63 | 808 KB |
| gas-boiler-repair | 106 ms | 432 ms | 514 ms | 352 ms | 63 | 595 KB |

**Speed is good.** No broken images across any page (0 of 22 per page). Four images per page
report `0×0` natural size — these are lazy-loaded below-fold gallery images that had not entered
the viewport, which is expected behavior, not a defect.

**TLS:** valid, Let's Encrypt (`YR1`), TLS 1.3, `notBefore` 2026-08-13, `notAfter` 2026-11-11,
SAN `offer.ambientcoolingandheating.com`. ⚠️ Certificate expires in **86 days** — ensure
auto-renewal is active.

### 10.4 Forms

Identical on all five pages:

| Field | Type | Label | Required | Note |
|---|---|---|---|---|
| `input_16` | text | "Email" | no | ✅ Gravity Forms **honeypot** — correct, not a defect |
| `input_1` | text | Full Name | ✅ yes | placeholder "Enter your full name" |
| `input_4` | tel | Phone Number | ✅ yes | ❌ placeholder **`(712) 555-0123`** |
| `input_3` | email | Email Address | ✅ yes | placeholder "your.email@example.com" |
| `input_7` | textarea | **"Tell us about your project (optional)\*"** | ✅ **yes** | ❌ says optional, is required, shows `*` |
| `input_9`–`input_15` | hidden ×7 | — | no | ❌ **all empty** — intended attribution fields, never populated |

**Three identical copies of Gravity Form 1** per page (`gform_wrapper_1` ×3, `gform_1` ×3,
`gform_submit=1` ×3) producing **34 duplicated DOM IDs**, each appearing 3×.

### 10.5 Attribution field test (no submission)

Loaded every page with `?gclid=TESTGCLID12345&gbraid=TESTGBRAID123&wbraid=TESTWBRAID123&utm_source=google&utm_medium=cpc&utm_campaign=audit-test&utm_term=ac+repair+near+me&utm_content=audit`.

**Result: all seven hidden fields remained empty on all five pages.**

```
[('input_9',''), ('input_10',''), ('input_11',''), ('input_12',''),
 ('input_13',''), ('input_14',''), ('input_15','')]
```

`gform_field_values` was also empty. The hidden fields exist but have **no dynamic population
binding**. Even if a lead is submitted, it arrives with **no click ID and no campaign context** —
so offline conversion upload and closed-loop reporting are impossible.

### 10.6 Content, offer, and claims

✅ **No invented claims found.** Scanned for prices, dollar amounts, percentage discounts,
guarantees, "24/7", "same-day", "licensed", "insured", "certified", years in business, star
ratings, and review counts. **None present.** The only offer is a **free quote**, consistently
worded. This is compliant with the client-truth rule.

**Location claims:** "Severn, Severna Park & Columbia, MD" plus "and nearby service areas" —
consistent across all five pages. ⚠️ Must be reconciled against the expected **75 Maryland
location targets** once the account is readable; three named cities and 75 geo targets are
plausibly consistent but unverified.

**Recent Work images:** filenames follow `ambientcoolingandheating-AC-Repair-<city>-N.webp` and
alt text describes Ambient technicians. **Filenames and alt text are not proof of ownership.**
Marked BLOCKED — requires written client confirmation that these are genuine Ambient project
photos (see §15, Q4).

### 10.7 Accessibility

| Check | Result |
|---|---|
| Pinch-to-zoom | ❌ `maximum-scale=1.0, user-scalable=0` — **WCAG 2.1 SC 1.4.4 failure** |
| Image alt text | ✅ present and descriptive (logo correctly `alt=""`) |
| Form labels | ⚠️ present, but broken by triplication — `label[for]` resolves to the first duplicate ID only |
| Duplicate IDs | ❌ 34 — invalid HTML; breaks assistive-technology label association |
| Countdown | ✅ `aria-live="polite"` |
| Required-field signalling | ❌ textarea labeled "(optional)" but `aria-required="true"` — contradictory for screen readers |

---

## 11. Phone-number consistency table

**Approved paid number: `(410) 705-6354` / `+14107056354` / `tel:+14107056354`**

### 11.1 Every `tel:` link found

| # | Location | `href` | Desktop | Mobile | Verdict |
|---|---|---|---|---|---|
| 1 | Header CTA "CALL: (410) 705-6354" | `tel:4107056354` | visible 204×41 | visible 143×30 | ⚠️ right number, **non-E.164** (no `+1`) |
| 2 | Hero CTA "Call Now: (410) 705-6354" | `tel:(410) 705-6354` | visible 240×41 | visible 240×41 | ⚠️ right number, **malformed href** (parens + space) |
| 3 | **Mobile "Call Now" button** | **`tel:+14107610932`** | **hidden 0×0** | **VISIBLE 175×37** | ❌ **P0 — WRONG NUMBER** |

Identical on all five pages, both viewports.

### 11.2 Wrong-number scan across full rendered HTML

| Number | ac-repair | hvac-repair | hvac-installation | hvac-replacement | gas-boiler-repair |
|---|---|---|---|---|---|
| `410-761-0932` / `+14107610932` | ❌ **2×** | ❌ **2×** | ❌ **2×** | ❌ **1×** | ❌ **1×** |
| `410-914-8446` / `+14109148446` | ✅ not found | ✅ not found | ✅ not found | ✅ not found | ✅ not found |
| `(712) 555-0123` | ❌ **3×** | ❌ 3× | ❌ 3× | ❌ 3× | ❌ 3× |
| `(410) 705-6354` in visible text | ✅ 3× | ✅ 3× | ✅ 3× | ✅ 3× | ✅ 3× |
| Any other phone number | ✅ none | ✅ none | ✅ none | ✅ none | ✅ none |

**Occurrence 1 (all five pages) — the mobile CTA button:**
```html
<a class="et_pb_button_5 et_pb_button …" href="tel:+14107610932" data-icon="">Call Now</a>
```
Inside a column classed `et_flex_column_24_24_phone` — a **phone-only** column. Hidden on
desktop, live on mobile.

**Occurrence 2 (ac-repair, hvac-repair, hvac-installation) — NEW FINDING, FAQ body copy:**
```html
<p>Complete the AC repair quote form with your contact information, service location,
and a short description of the cooling problem. You can also call Ambient Cooling &amp;
Heating at (410) 761-0932.</p>
```
This sits in a **collapsed** accordion (`et_pb_toggle_close`), so it does not appear in
`innerText` — but it is fully visible to any user who expands the FAQ. **This was not in the
prior defect list.**

### 11.3 Visual proof — mobile

The wrong-number button is the **dominant yellow CTA**, rendered directly above the correct
green button, and the two visually collide:

- 🟡 **"Call Now"** → `tel:+14107610932` ❌ **wrong number**
- 🟢 **"Call Now: (410) 705-6354"** → `tel:(410) 705-6354` ✅ right number

Screenshot evidence: `rendered/mobile_callnow_crop.png`.

### 11.4 Other required surfaces

| Surface | Status |
|---|---|
| Google Ads call asset | ❓ **BLOCKED** — must be verified to route to `(410) 705-6354` |
| Call conversion action | ❓ **BLOCKED** |
| Schema / structured data phone field | ✅ N/A — **no structured data exists** (itself a defect, P2-4) |
| Form confirmation | ⚠️ inline postback, no phone shown; no separate thank-you page |
| Main website | ✅ uses `(410) 761-0932` — **accepted and correct by design** |

---

## 12. Confirmed problems, ranked

### P0 — tracking, lead loss, wrong phone, wrong account, uncontrolled spend

| ID | Problem | Evidence | Impact |
|---|---|---|---|
| **P0-1** | **No conversion tracking on any paid landing page.** No GTM, no gtag, no Google Ads tag, no `dataLayer`. | §9.2, §10.2 | Every form lead and call is invisible to Google Ads. Smart Bidding cannot learn. All spend since 2026-08-14 is unmeasured. |
| **P0-2** | **Mobile "Call Now" CTA dials the wrong number** (`+14107610932`) on all five pages. Hidden on desktop, visible on mobile. | §11.1, §11.3 | Mobile calls — the majority of HVAC lead volume — bypass the approved paid line and all attribution. |
| **P0-3** | **Wrong number in FAQ body copy** on 3 pages. | §11.2 | Same leak through a second, less obvious path. |
| **P0-4** | **Attribution fields never populate.** 7 hidden fields stay empty with `gclid`/`gbraid`/`wbraid`/UTMs present. | §10.5 | Leads arrive with no click ID. Offline conversion upload and closed-loop profit reporting are impossible. |
| **P0-5** | **Account identity gate failed.** Name is `Ambient Cooling`, not `Ambient Cooling & Heating`; no `- live` marker. A second enabled `OLD Ambient C&H` exists. | §3 | Account audit blocked. Risk of operating on the wrong account; possible legacy-account spend. |

### P1 — major targeting, conversion, policy, or landing-page problems

| ID | Problem | Evidence |
|---|---|---|
| **P1-1** | **No Privacy Policy or Terms link on any of the five pages.** Lead-gen forms collecting name, phone, and email. Google Ads policy and privacy-law exposure. | §10.1 |
| **P1-2** | **Three identical copies of Gravity Form 1** per page → 34 duplicated DOM IDs. Invalid HTML; ambiguous submission target; blocks reliable conversion tagging. | §10.4 |
| **P1-3** | **HVAC Repair page shows "Recent AC Repair Work"** — cross-service content leak. | §6 |
| **P1-4** | **Gas Boiler Repair page shows "Your HVAC Replacement in 3 Simple Steps"** — wrong service in a core conversion section. | §6 |
| **P1-5** | **Countdown contradicts copy.** Deadline `2026-08-31T23:59:59+00:00`, timer displays "14 DAY", while copy says "before today ends" on installation, replacement, and gas-boiler pages. | §10.1 |
| **P1-6** | **Countdown deadline set in UTC, not Eastern** — `+00:00` means it expires 2026-08-31 **7:59:59 PM ET**, four hours early. **NEW FINDING.** | §10.1 |
| **P1-7** | **Phone placeholder `(712) 555-0123`** — a fake number shown in the phone field on all five pages. | §10.4 |
| **P1-8** | **Textarea labeled "(optional)" but required** (`aria-required="true"`, shows `*`). Users are blocked by a field they were told to skip. | §10.4 |
| **P1-9** | **ClickCease redirect on every click** with zero tags on the destination. Click-ID preservation unverified. | §3.6 |
| **P1-10** | **`OLD Ambient C&H` (2391758435) still ENABLED** — potential unintended delivery and budget leakage. | §3.3 |

### P2 — optimization, copy, CRO, accessibility

| ID | Problem | Evidence |
|---|---|---|
| **P2-1** | **Pinch-to-zoom disabled** (`user-scalable=0`) — WCAG 2.1 SC 1.4.4 failure. | §10.7 |
| **P2-2** | **Non-canonical `tel:` hrefs** on the two correct buttons (`tel:4107056354`, `tel:(410) 705-6354`). Should both be `tel:+14107056354`. | §11.1 |
| **P2-3** | **Mobile CTA overlap** — yellow and green call buttons visually collide. | §11.3 |
| **P2-4** | **No structured data** on any page (0 JSON-LD blocks). No LocalBusiness/Service schema, so no schema phone field either. | §10.1 |
| **P2-5** | **"Recent Work" image provenance unproven.** | §10.6 |
| **P2-6** | **TLS certificate expires 2026-11-11** (86 days). Confirm auto-renewal. | §10.3 |
| **P2-7** | **SG-Captcha blocks non-browser clients** (202/403). Naive monitors will misreport uptime. | §10 intro |
| **P2-8** | **Main site GTM container also failed to initialize** on render despite the ID being present. Out of scope; flagged. | §9.3 |

---

## 13. Previously observed issues — independent retest

Every item was retested from scratch. **No prior result was assumed.**

| # | Previously observed | Verdict | Evidence |
|---|---|---|---|
| 1 | Hidden/mobile "Call Now" using `tel:+14107610932` | ✅ **CONFIRMED** | Present on all 5 pages. Desktop 0×0, **mobile 175×37 visible**. §11.1 |
| 2 | GTM-PQTPQ436 did not appear to load | ✅ **CONFIRMED — and worse** | Not merely failing to load: **not installed at all** on the offer subdomain. §9.2 |
| 3 | Form attribution fields empty with test query params | ✅ **CONFIRMED** | All 7 hidden fields empty on all 5 pages. §10.5 |
| 4 | No Privacy Policy or Terms links | ✅ **CONFIRMED** | Zero matching links on all 5 pages. §10.1 |
| 5 | Three copies of Gravity Form 1 on each page | ✅ **CONFIRMED** | `gform_wrapper_1` ×3 on all 5 pages. §10.4 |
| 6 | Duplicate DOM IDs | ✅ **CONFIRMED** | 34 IDs duplicated 3× each, all 5 pages. §10.4 |
| 7 | Phone placeholder `(712) 555-0123` | ✅ **CONFIRMED** | 3× per page. §10.4 |
| 8 | Project textarea labeled optional but required | ✅ **CONFIRMED** | Label "(optional)\*", `aria-required="true"`. §10.4 |
| 9 | Countdown ends Aug 31 while copy says "before today ends" | ✅ **CONFIRMED** | `data-deadline="2026-08-31T23:59:59+00:00"`, timer "14 DAY"; "before today ends" on 3 of 5 pages. §10.1 |
| 10 | HVAC Repair heading "Recent AC Repair Work" | ✅ **CONFIRMED** | Exact H2 on hvac-repair. §6 |
| 11 | Gas Boiler heading "Your HVAC Replacement in 3 Simple Steps" | ✅ **CONFIRMED** | Exact H2 on gas-boiler-repair. §6 |
| 12 | Mobile pinch-to-zoom disabled | ✅ **CONFIRMED** | `maximum-scale=1.0, user-scalable=0`, all 5 pages. §10.7 |
| 13 | "Recent Work" images may need proof of provenance | ⚠️ **BLOCKED** | Cannot be verified from public sources; requires client confirmation. §10.6 |
| 14 | Number `410-914-8446` | ✅ **NOT REPRODUCED** | Not found in any rendered HTML on any page. §11.2 |

**Two new defects** not in the prior list: wrong number in **FAQ body copy** (P0-3) and the
countdown deadline set in **UTC rather than Eastern** (P1-6).

---

## 14. Exact recommended fix for every failed check

Every item below is a **proposal only**. Nothing here has been applied.

### P0 fixes

**P0-1 — Deploy GTM-PQTPQ436 to the offer subdomain.**
Add to `<head>` of the offer-site theme, as high as possible:
```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-PQTPQ436');</script>
<!-- End Google Tag Manager -->
```
Immediately after `<body>`:
```html
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-PQTPQ436"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
```
Then, inside the container: a Google tag / configuration tag, Conversion Linker, a form
conversion keyed to a **confirmed** Gravity Forms submission with a unique entry ID, a call
conversion, Consent Mode v2 defaults, and cross-domain linking between
`ambientcoolingandheating.com` and `offer.ambientcoolingandheating.com`.
**Do not fire the form tag on page load, form visibility, CTA click, submit-button click,
validation error, a duplicate form instance, or a thank-you reload.**

**P0-2 — Fix the mobile call button.**
Change `et_pb_button_5` on all five pages:
`href="tel:+14107610932"` → **`href="tel:+14107056354"`**, and set its label to
`Call Now: (410) 705-6354` for consistency with the desktop CTA.

**P0-3 — Fix the FAQ copy** on ac-repair, hvac-repair, and hvac-installation:
`(410) 761-0932` → **`(410) 705-6354`**.

**P0-4 — Populate the attribution fields.**
Enable "Allow field to be populated dynamically" on `input_9`–`input_15` in Gravity Forms and
bind parameter names `gclid`, `gbraid`, `wbraid`, `utm_source`, `utm_medium`, `utm_campaign`,
`utm_term`. Add a first-party cookie to persist the click ID across the session so it survives
the ClickCease redirect and any internal navigation. Verify with a real click-ID URL before
relying on it.

**P0-5 — Resolve the account identity.** See §15 Q1. Either rename the account in Google Ads to
the exact approved name including `- live`, or confirm in writing the exact authoritative name.
Then re-run the validator and the full account audit.

### P1 fixes

- **P1-1** — Add Privacy Policy and Terms links to the footer of all five pages.
- **P1-2** — Remove the two duplicate Gravity Form instances; keep exactly one per page.
- **P1-3** — Change hvac-repair H2 to "Recent HVAC Repair Work".
- **P1-4** — Change gas-boiler-repair H2 to "Your Gas Boiler Repair in 3 Simple Steps".
- **P1-5** — Either change the copy from "before today ends" to match the Aug 31 deadline, or
  make the countdown a genuine end-of-day timer. **Do not display a false deadline.**
- **P1-6** — Change `data-deadline` to `2026-08-31T23:59:59-04:00`.
- **P1-7** — Change the phone placeholder to a neutral format hint, e.g. `(410) 555-0123` is
  still a fake number — prefer **`Phone number`** or `(___) ___-____`.
- **P1-8** — Decide one: make `input_7` genuinely optional (remove `aria-required`, remove `*`),
  or relabel it "Tell us about your project" without "(optional)". **Recommend making it
  optional** — a required free-text field measurably suppresses lead volume.
- **P1-9** — Verify the ClickCease redirect preserves `gclid`/`gbraid`/`wbraid`. If it does not,
  remove it or reconfigure it. It is currently the only thing between the click and an untagged page.
- **P1-10** — Review `OLD Ambient C&H` (2391758435) for active delivery and pause it if it is
  serving. **Requires its own identity gate and its own approval.**

### P2 fixes

- **P2-1** — Remove `maximum-scale=1.0, user-scalable=0`; use
  `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- **P2-2** — Normalize both correct CTAs to `href="tel:+14107056354"`.
- **P2-3** — Fix the mobile button-stack spacing so the CTAs no longer overlap.
- **P2-4** — Add LocalBusiness/HVACBusiness JSON-LD with `telephone: "+1-410-705-6354"` —
  **only** with verified NAP data.
- **P2-5** — Obtain written client confirmation that the "Recent Work" photos are genuine
  Ambient project photos; replace any that are not.
- **P2-6** — Confirm SiteGround TLS auto-renewal before 2026-11-11.
- **P2-7** — Allowlist monitoring user agents in SG-Captcha, or monitor via a real browser check.
- **P2-8** — Separately investigate why GTM does not initialize on the main site.

---

## 15. Proposed change plan — REQUIRES APPROVAL BEFORE IMPLEMENTATION

**Nothing in this section has been done. Each phase needs its own explicit approval.**

### Phase 0 — Unblock identity (no external write)
Green Marketing answers Q1. Re-run `validate_work_order.py`. Then execute the full read-only
account audit: account settings, all campaigns (enabled/paused/removed), the five new campaigns
in detail, budgets and pacing, ad groups, keywords, negatives, search terms, RSAs, assets,
conversion actions, and all performance windows with day/hour segmentation.

### Phase 1 — Stop the bleeding (external writes; highest urgency)
1. Fix the wrong phone number in the mobile CTA and the FAQ copy (P0-2, P0-3).
2. Deploy GTM-PQTPQ436 to the offer subdomain (P0-1).
3. Configure and verify conversion tags, then confirm with Tag Assistant.
4. Populate attribution fields (P0-4).

> **Budget consideration for the owner.** The campaigns are currently spending with **no
> measurement and a wrong mobile call CTA**. Pausing until Phase 1 lands is the conservative
> option and would prevent further unmeasured spend. **Pausing is an external write and needs
> your explicit approval — I have not paused anything.**

### Phase 2 — Landing-page corrections (external writes)
P1-1 through P1-8, then P2 items.

### Phase 3 — Verification (no external write)
Re-render all five pages, re-confirm every check in §10 and §11, then run an approved
end-to-end test.

### Proposed end-to-end test plan — NOT EXECUTED, REQUIRES APPROVAL

I did **not** submit a test lead and did **not** click or dial any phone link. Proposed:

1. Load `…/ac-repair/?gclid=TEST_<timestamp>&utm_source=google&utm_medium=cpc` in a real browser.
2. Confirm `gtm.js?id=GTM-PQTPQ436` is requested and `dataLayer` initializes.
3. Confirm all 7 hidden fields populate.
4. Submit **one** lead with clearly marked test data (name "GM AUDIT TEST", an agency-controlled
   phone and email).
5. Confirm exactly **one** conversion is recorded — not three, despite three form copies.
6. Confirm the CRM/notification payload carries the click ID.
7. Place **one** test call to `(410) 705-6354` from an agency phone to confirm routing.
8. Delete the test entry from Gravity Forms.

**Requires: approval to submit a test lead, approval to place a test call, and confirmation of
which phone/email to use.**

---

## 16. Missing data and limitations

| # | Limitation | Effect |
|---|---|---|
| 1 | **Google Ads account read blocked by the identity gate.** | §4, §5, §6, §7, §8 could not be completed. |
| 2 | **No GTM API access configured.** | Container internals could not be enumerated. Mitigated: the container never loads, so the browser evidence is decisive. |
| 3 | **No approved campaign blueprint exists in the repository.** | The $13,000 allocation could not be reconciled against an approved artifact. |
| 4 | **Budget basis ambiguous** — full month vs Aug 14–31. | 72% swing in correct daily budget. See Q2. |
| 5 | **No target CPL / CPQL / CAC supplied; no qualified-lead or sold-job data.** | **No profitability verdict is possible.** |
| 6 | **Only 3 days since launch.** | No performance conclusion would be sound even with data access. |
| 7 | **Host bot protection.** | Required a real browser; plain HTTP clients cannot audit these pages. |
| 8 | **Image provenance unverifiable from public sources.** | P2-5 stays BLOCKED. |
| 9 | **No test lead submitted, no call placed.** | End-to-end lead delivery and call routing remain unverified by design. |

### Consolidated questions

**Q1 (blocking, account audit only).** The account is named **`Ambient Cooling`**, not
`Ambient Cooling & Heating`, and lacks `- live`. Please either (a) rename it in Google Ads to
the exact approved name including the `- live` marker, or (b) confirm in writing the exact
descriptive name to treat as authoritative. Also confirm whether **`OLD Ambient C&H`
(2391758435)**, currently ENABLED, should be reviewed.
*Recommendation: rename to `Ambient Cooling & Heating - Live` so the account matches agency
convention and the gate passes cleanly.*

**Q2 (blocking, budget only).** Is $13,000 a **full-month** budget or a budget for the
**Aug 14–31** launch period? Daily budgets differ by 72% ($419.35/day vs $722.22/day).

**Q3 (non-blocking).** The expected ad schedule is Mon–Fri 08:00–16:00 ET, but the pages promote
an always-available call CTA. Are calls answered outside those hours? This determines whether
the schedule or the page copy should change.

**Q4 (non-blocking).** Are the "Recent Work" photos genuine Ambient project photos? Written
confirmation is needed before they can stay on a paid page.

---

## 17. Evidence appendix

**Audit timestamp:** 2026-08-17, approximately 17:29–17:40 UTC (13:29–13:40 America/New_York)
**Account timezone:** America/New_York
**Repository:** `D:\MG\green-marketing-gsa`

### Identity and account-selection queries (GAQL `SELECT` only)

```sql
-- 1. Identity of the target child account (run against customer 2401959466)
SELECT customer.id, customer.descriptive_name, customer.currency_code,
       customer.time_zone, customer.manager, customer.test_account,
       customer.status, customer.auto_tagging_enabled,
       customer.tracking_url_template, customer.final_url_suffix,
       customer.conversion_tracking_setting.conversion_tracking_id,
       customer.conversion_tracking_setting.google_ads_conversion_customer,
       customer.conversion_tracking_setting.conversion_tracking_status,
       customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
       customer.optimization_score,
       customer.pay_per_conversion_eligibility_failure_reasons
FROM customer LIMIT 1

-- 2. Manager link verification (run against the configured manager)
SELECT customer_client.id, customer_client.client_customer,
       customer_client.descriptive_name, customer_client.level,
       customer_client.manager, customer_client.test_account,
       customer_client.status, customer_client.currency_code,
       customer_client.time_zone
FROM customer_client WHERE customer_client.id = 2401959466

-- 3. Account-selection listing, to resolve the name mismatch
SELECT customer_client.id, customer_client.descriptive_name, customer_client.level,
       customer_client.manager, customer_client.test_account, customer_client.status,
       customer_client.currency_code, customer_client.time_zone
FROM customer_client WHERE customer_client.status = 'ENABLED'
ORDER BY customer_client.descriptive_name
```

**No other Google Ads query was executed.** No mutate call of any kind was made.

### Resource IDs

| Resource | ID |
|---|---|
| Target child customer | `2401959466` |
| Manager (MCC) | `3373711342` |
| Conversion tracking ID | `11155434808` |
| Legacy account (observed only, not read) | `2391758435` — `OLD Ambient C&H` |
| GTM container (approved) | `GTM-PQTPQ436` |
| Main-site GA4 measurement ID (observed) | `G-9X9ZHNCRWF` |

### URLs checked

| URL | Method | Result |
|---|---|---|
| `https://offer.ambientcoolingandheating.com/ac-repair/` | GET, rendered | 200 |
| `https://offer.ambientcoolingandheating.com/hvac-repair/` | GET, rendered | 200 |
| `https://offer.ambientcoolingandheating.com/hvac-installation/` | GET, rendered | 200 |
| `https://offer.ambientcoolingandheating.com/hvac-replacement/` | GET, rendered | 200 |
| `https://offer.ambientcoolingandheating.com/gas-boiler-repair/` | GET, rendered | 200 |
| `https://offer.ambientcoolingandheating.com/` | GET | 202 challenge |
| `https://ambientcoolingandheating.com/` | GET, rendered | 200 (context only) |

Each offer page was loaded twice (desktop 1440×900 and mobile 390×844 @2×) with the test query
string in §10.5, plus a third clean load for timing metrics.

### Scripts used (read-only; scratchpad)

| Script | Purpose |
|---|---|
| `identity_check.py` | Fresh identity + manager-link lookup |
| `list_accounts.py` | Account-selection listing to resolve the name mismatch |
| `fetch_pages.py` | Initial HTTP fetch, TLS inspection, redirect chain |
| `render_pages.py` / `render_desktop.py` | Real-browser render, network capture, DOM probes, screenshots |
| `analyze.py` / `summary.py` / `deep_scan.py` / `script_scan.py` | Local analysis of captures |
| `perf_and_mainsite.py` | Navigation timing; main-site phone and tag check |

### Local artifacts

- `clients/ambient-cooling-heating/client.yaml`
- `clients/ambient-cooling-heating/work-order.yaml`
- `reports/ambient-cooling-heating/2026-08-17-full-launch-audit.md` (this file)
- Screenshots and captures: session scratchpad `…/scratchpad/rendered/`

### Validator output

```
Work order is not ready:
- work_order.account.exact_child_account_name must contain '- live'
```

**No secrets, tokens, credentials, or lead PII appear in this report.** Environment variables
were confirmed present by name only; no value was read, printed, or logged. `.env` was not
modified.

---

## 18. Final statement

**No external changes were made during this audit.** Google Ads was read with `SELECT`
statements only. Google Tag Manager was never accessed in a writable mode. The website, forms,
CRM, call tracking, budgets, and campaign statuses were not touched. No form was submitted and
no phone call was placed.
