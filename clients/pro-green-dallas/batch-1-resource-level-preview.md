# Batch 1 — Resource-Level Implementation Preview

**Account:** Pro Green - Dallas - Live · **8735782888** · manager **3373711342**
**Date:** 2026-08-11 · **Mode: PREVIEW ONLY. Nothing has been implemented.**
**No approval is requested in this document.**

Evidence labels: **[FRESH-API]** · **[RUNTIME]** · **[USER]** · **[INFER]** · **[UNVERIFIED]**

---

## 0. Identity gate — PASSED **[FRESH-API]**, 2026-08-11

| Check | Result |
| --- | --- |
| `customer.id` | **8735782888** ✅ |
| `customer.descriptive_name` | **Pro Green - Dallas - Live** ✅ |
| `customer.manager` | `false` ✅ |
| `customer.test_account` | `false` ✅ |
| `- live` marker | present ✅ |
| Manager link `3373711342` | link `342593485`, **ACTIVE** ✅ |
| Currency / time zone | USD / **America/New_York** |
| `conversion_tracking_id` | **11237210508** |
| `cross_account_conversion_tracking_id` | **0** |
| `conversion_tracking_status` | `CONVERSION_TRACKING_MANAGED_BY_SELF` |
| `accepted_customer_data_terms` | **true** |
| `enhanced_conversions_for_leads_enabled` | **true** |
| `auto_tagging_enabled` | **true** |
| Second manager link | `2815082755` link `345783752` ACTIVE — **ClickCease, authorized [USER]. Not queried.** |

All queries in this document were `SELECT`-only against `8735782888`. The manager account was
never used as a query target.

---

## 1. Change log since the 2026-08-07 snapshot

| # | Change | Label |
| --- | --- | --- |
| C1 | **Conversion actions grew 12 → 14.** `Whatconverts Form` **7717433751** and `Whatconverts Calls` **7717433754` created | [FRESH-API] |
| C2 | Both new actions are **ENABLED, primary, and included in Conversions** — and both have **received nothing** (`last_received_request` empty) | [FRESH-API] |
| C3 | **No conversion of any kind since 2026-07-31.** Last call conversion 2026-07-29, last form conversion 2026-07-31 | [FRESH-API] |
| C4 | **Month-to-date 2026-08-01→08-11: $369.98, 46 clicks, 721 impressions, 0 conversions** | [FRESH-API] |
| C5 | Search Partners now **off**; the 90-day window still contains 107 partner impressions, so it was on during the period | [FRESH-API] |
| C6 | On this run NitroPack deferred **0 of 73–75** scripts and tags loaded without interaction — differs from 2026-08-10 | [RUNTIME] |
| C7 | An **account-level ClickCease tracking template** exists — not previously recorded | [FRESH-API] |

---

## 2. Complete conversion-action inventory **[FRESH-API]**

Windows: **w30** = 2026-07-13→08-11 · **w90** = 2026-05-14→08-11.
Every action is owned by `customers/8735782888`. Resource names are
`customers/8735782888/conversionActions/<id>`.

| ID | Name | Type / Origin | Category | Status | Pri | InConv | Counting | Click/View | Call s | Value / alwaysDefault | w30 conv/all | w90 conv/all | Last conv |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **6617381255** | Calls from Ads | AD_CALL / CALL_FROM_ADS | PHONE_CALL_LEAD | ENABLED | **yes** | **yes** | ONE_PER_CLICK | 30/30 | **60** | 0.0 / true | **1.0 / 1.0** | **3.0 / 3.0** | 2026-07-29 |
| **6886101052** | Pro Green DFW - Lp - Submit Lead Form | WEBPAGE / WEBSITE | SUBMIT_LEAD_FORM | ENABLED | **yes** | **yes** | ONE_PER_CLICK | 30/1 | 60 | 0.0 / true | **2.0 / 2.0** | **2.0 / 2.0** | 2026-07-31 |
| **6886103719** | Pro Green DFW - Lp - Phone Call Leads | WEBSITE_CALL / WEBSITE | PHONE_CALL_LEAD | ENABLED | **yes** | **yes** | ONE_PER_CLICK | 30/30 | **30** | 0.0 / true | 0 / 0 | 0 / 0 | **2026-02-28** |
| **7717433751** | Whatconverts Form | **UPLOAD_CLICKS** / WEBSITE | CONTACT | ENABLED | **yes** | **yes** | ONE_PER_CLICK | **60/15** | 60 | 1.0 / **false** | **0 / 0** | **0 / 0** | **never** |
| **7717433754** | Whatconverts Calls | **UPLOAD_CALLS** / CALL_FROM_ADS | CONTACT | ENABLED | **yes** | **yes** | ONE_PER_CLICK | **60/30** | 60 | 1.0 / **false** | **0 / 0** | **0 / 0** | **never** |
| 6548857156 | GSA Submit Lead Form | WEBPAGE / WEBSITE | SUBMIT_LEAD_FORM | ENABLED | no | **no** | ONE_PER_CLICK | 30/1 | 60 | 0.0 / true | 0 / 0 | 0 / 0 | 2026-03-01 |
| 6549164075 | GSA Call Btn Click (1) | WEBPAGE / WEBSITE | CONTACT | ENABLED | no | **no** | ONE_PER_CLICK | 30/1 | 60 | 0.0 / true | 0 / 0 | 0 / 0 | — |
| 6616343220 | Clicks to call | GOOGLE_HOSTED | CONTACT | ENABLED | yes | **no** | MANY_PER_CLICK | 30/7 | 60 | 1.0 / true | 0 / 0 | 0 / 0 | **2026-02-28** |
| 6608032928 | Local actions - Website visits | GOOGLE_HOSTED | PAGE_VIEW | ENABLED | yes | **no** | MANY_PER_CLICK | 30/7 | 60 | 1.0 / true | 0 / **3.0** | 0 / **4.0** | 2026-07-24 |
| 6609874719 | Local actions - Directions | GOOGLE_HOSTED | GET_DIRECTIONS | ENABLED | yes | **no** | MANY_PER_CLICK | 30/7 | 60 | 1.0 / true | 0 / **2.0** | 0 / **2.0** | 2026-08-05 |
| 6669693044 | Local actions - Other engagements | GOOGLE_HOSTED | ENGAGEMENT | ENABLED | yes | **no** | MANY_PER_CLICK | 30/7 | 60 | 1.0 / true | 0 / **3.0** | 0 / **10.0** | 2026-07-23 |
| 6651119909 | progreenlandscapesolutions.com - GA4 (web) purchase | GA4_PURCHASE / WEBSITE | PURCHASE | **HIDDEN** | no | no | MANY_PER_CLICK | 90/1 | 60 | 1.0 / false | 0 / 0 | 0 / 0 | — |
| 6548857159 | GSA Call Btn Click | WEBPAGE / WEBSITE | CONTACT | **REMOVED** | — | — | — | 30/1 | 60 | — | 0 / 0 | 0 / 0 | — |
| 6555523644 | Calls from ads | AD_CALL / CALL_FROM_ADS | PHONE_CALL_LEAD | **REMOVED** | — | — | — | 30/30 | 60 | — | 0 / 0 | 0 / 0 | — |

### 2.1 Conversions vs All Conversions — full reconciliation **[FRESH-API]**

**w90 (2026-05-14 → 2026-08-11)**

| Action | Conversions | All conversions |
| --- | --- | --- |
| 6617381255 Calls from Ads | 3.00 | 3.00 |
| 6886101052 Submit Lead Form | 2.00 | 2.00 |
| 6669693044 Other engagements | 0 | 10.00 |
| 6608032928 Website visits | 0 | 4.00 |
| 6609874719 Directions | 0 | 2.00 |
| **TOTAL** | **5.00** | **21.00** |

**w30 (2026-07-13 → 2026-08-11)**

| Action | Conversions | All conversions |
| --- | --- | --- |
| 6617381255 | 1.00 | 1.00 |
| 6886101052 | 2.00 | 2.00 |
| 6669693044 | 0 | 3.00 |
| 6608032928 | 0 | 3.00 |
| 6609874719 | 0 | 2.00 |
| **TOTAL** | **3.00** | **11.00** |

**Reconciliation statement.** The 16-point w90 gap between Conversions (5) and All Conversions
(21) is **fully explained** by the three `GOOGLE_HOSTED` "Local actions" actions, which are
`primary_for_goal: true` but `include_in_conversions_metric: false`. They are Google Business
Profile engagement signals, **not leads**, and must never be counted as such. **No conversion is
unaccounted for; no action is double-counting today.**

### 2.2 Goal biddability **[FRESH-API]**

| Category / Origin | Biddable | Actions in it |
| --- | --- | --- |
| PHONE_CALL_LEAD / CALL_FROM_ADS | **true** | 6617381255 |
| SUBMIT_LEAD_FORM / WEBSITE | **true** | 6886101052, 6548857156 |
| PHONE_CALL_LEAD / WEBSITE | **true** | 6886103719 |
| **CONTACT / CALL_FROM_ADS** | **true** | **7717433754** |
| **CONTACT / WEBSITE** | **true** | **7717433751**, 6549164075 |
| CONTACT / GOOGLE_HOSTED | false | 6616343220 |
| PAGE_VIEW, GET_DIRECTIONS, ENGAGEMENT / GOOGLE_HOSTED | false | local actions |

### 2.3 Duplication and overlap assessment

| Pair | Overlap | Live today? | Disposition |
| --- | --- | --- | --- |
| **7717433754** vs **6617381255** | **YES — same physical call.** The call asset dials (214) 301-3385, a WhatConverts number, so both systems see it | **No** — 7717433754 has never received | **Contain now (1.1)** |
| **7717433751** vs **6886101052** | **Likely** — both would count a landing-page form submission | **No** — 7717433751 has never received | **Contain now (1.2)** |
| 6548857156 vs 6886101052 | Yes, same event | **No** — 6548857156 excluded from Conversions | Leave as is |
| 6549164075 vs 6616343220 | Likely, both click-to-call | **No** — both excluded | Leave as is |
| 6886103719 vs 6617381255 | **No** — different surfaces (website call vs SERP call asset) | n/a | Keep both |
| 6555523644 vs 6617381255 | Historic | REMOVED | Leave |

---

## 3. Batch 1A — Safe containment preview

**Objective.** Neutralise the armed duplicate-counting risk **without touching anything that is
currently working** and **without violating phone rules 8 and 9**.

**Dependencies.** None. **This batch is deliberately self-contained and has no landing-page,
GTM, WordPress, or WhatConverts dependency for items 1.1–1.5.**

### 1.1 — `7717433754` Whatconverts Calls → secondary, excluded

| Field | Value |
| --- | --- |
| **Resource** | `customers/8735782888/conversionActions/7717433754` |
| **Current** | `primary_for_goal: true`, `include_in_conversions_metric: true` |
| **Proposed** | `primary_for_goal: false`, `include_in_conversions_metric: false` |
| **Reason** | Importing a Google Call Extension-source call duplicates `6617381255`, which already counts it natively. The action has **zero** data, so it is **[UNVERIFIED]** as a working replacement — treating it as one would be an assumption, not evidence |
| **Dependency** | None |
| **Risk** | **Very low.** Zero data means zero reporting impact today |
| **Rollback** | Set both fields back to `true` |
| **Verification** | GAQL read-back of both fields; confirm w30/w90 conversions unchanged at 3.00 / 5.00 |
| **Expected reporting effect** | **None today.** Prevents a future silent inflation of the Conversions column |

### 1.2 — `7717433751` Whatconverts Form → secondary, excluded

| Field | Value |
| --- | --- |
| **Resource** | `customers/8735782888/conversionActions/7717433751` |
| **Current** | `primary_for_goal: true`, `include_in_conversions_metric: true` |
| **Proposed** | `primary_for_goal: false`, `include_in_conversions_metric: false` |
| **Reason** | Would likely double-count the same form submission as `6886101052`. Zero data, therefore **[UNVERIFIED]** |
| **Dependency** | None |
| **Risk** | Very low |
| **Rollback** | Set both fields back to `true` |
| **Verification** | GAQL read-back; conversions unchanged |
| **Expected reporting effect** | None today |

### 1.3 — `6617381255` Calls from Ads → **NO CHANGE**

| Field | Value |
| --- | --- |
| **Resource** | `customers/8735782888/conversionActions/6617381255` |
| **Current & proposed** | `primary_for_goal: true`, `include_in_conversions_metric: true`, 60 s, ONE_PER_CLICK, 30/30 |
| **Reason** | The **only** conversion signal that has worked in the last 90 days. [USER] requires preservation until a tested replacement exists |
| **Risk of changing it** | **High** — would erase the account's last working signal |

### 1.4 — `6886101052` Submit Lead Form → **NO CHANGE**

| Field | Value |
| --- | --- |
| **Resource** | `customers/8735782888/conversionActions/6886101052` |
| **Current & proposed** | unchanged, primary, in Conversions |
| **Reason** | [USER]: preserve; do not delete. Second of only two working signals |

### 1.5 — `6886103719` Phone Call Leads → **NO CHANGE IN THIS BATCH**

| Field | Value |
| --- | --- |
| **Resource** | `customers/8735782888/conversionActions/6886103719` |
| **Current** | ENABLED, primary, in Conversions, 30 s. **0 conversions since 2026-02-28** |
| **Proposed now** | **Nothing.** Retain exactly as is |
| **Reason** | Phone rule 9 [USER]: do not exclude until **all** live URL dependencies are removed **and** a tested non-duplicating replacement exists. **[FRESH-API]** eight ads still carry `offerdfw` final URLs, and (214) 301-3385 renders on that host **[RUNTIME]** — so a compatible page still exists in the account |
| **Deferred to** | Post-cutover stage, **Batch 1B step 9** |

> **CORRECTION.** `final-audit-and-revamp-plan.md` §17 Batch 1 items **1.3 and 1.6** proposed
> excluding `6886103719` and removing the `__awcc` tag in this batch. **Both are withdrawn from
> Batch 1A** as they violate confirmed phone rules 8 and 9.

### 1.6 — GTM `__awcc` tag → **NO CHANGE IN THIS BATCH**

Retained while `offerdfw` ads and the compatible page exist. Removal is **Batch 1B step 10**.

### 1.7 — Legacy actions → preserve, no deletion

| Resource | Action | Disposition |
| --- | --- | --- |
| `.../6548857156` | GSA Submit Lead Form | **Keep.** Already excluded from Conversions |
| `.../6549164075` | GSA Call Btn Click (1) | **Keep.** Already excluded |
| `.../6616343220` | Clicks to call | **Keep.** Already excluded |
| `.../6651119909` | GA4 purchase | **Keep.** HIDDEN |
| `.../6548857159`, `.../6555523644` | REMOVED twins | **Keep.** No action |
| Local actions ×3 | GBP engagement | **Keep.** Correctly excluded |

**No deletion of any conversion action is proposed, now or later.**

### 1.8 — WhatConverts: exclude Google Call Extension source from imports

| Field | Value |
| --- | --- |
| **System** | WhatConverts profile **107007**, Google Ads integration |
| **Current** | `Phone Calls: Sending Data` for **all** sources **[RUNTIME]** |
| **Proposed** | Exclude the **`Google Call Extension`** source from the Google Ads conversion feed |
| **Reason** | (214) 301-3385 is a Google Call Extension number; those calls are already counted by `6617381255` |
| **Dependency** | **WhatConverts console access — currently BLOCKED by a login barrier** |
| **Risk** | Low. Lead recording in WhatConverts is unaffected; only the Ads export changes |
| **Rollback** | Re-include the source |
| **Verification** | One week of WhatConverts call log reconciled 1:1 against `6617381255` |
| **Owner** | **Green Marketing / WhatConverts admin — not Claude** |

### 1.9 — Explicitly excluded from Batch 1A

No phone number changed anywhere · no landing-page edit · no GTM edit or publish · no
`__awcc` removal · no `6886103719` change · no deletion of any action · no WhatConverts
disconnect · **`Conversion Updates` not enabled** · no bid, budget, keyword, or targeting change.

### 1.10 — Net expected reporting effect of Batch 1A

**Zero change to any reported number today.** Both modified actions have never received data.
The batch is purely preventive.

---

## 4. Batch 1B — Landing page and routing preview

### 4.1 Recommended URL

**`https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/`**
Rationale in `confirmed-business-decisions.md` §4.

### 4.2 Complete URL dependency inventory **[FRESH-API]**

Serving status = campaign ENABLED **and** ad group ENABLED **and** ad ENABLED.

#### Ads — currently SERVING (3)

| Ad ID | Ad group | Ad group ID | Current final URL | Proposed | Order |
| --- | --- | --- | --- | --- | --- |
| **714659486058** | Sprinkler Repair Near Me | 151125103616 | `…/dfw/offer-sprinkler-repair-b/` | new canonical URL | 4c |
| **797294303667** | Irrigation Repair Near Me | 190202910461 | `…/dfw/offer-sprinkler-repair-a/` | new canonical URL | 4a |
| **797325463324** | Sprinkler System Repair | 191996690566 | `…/dfw/offer-sprinkler-repair-a/` | new canonical URL | 4b |

Resource names: `customers/8735782888/adGroupAds/<adGroupId>~<adId>`.

#### Ads — NOT serving but URL-bearing (15)

| Ad ID | Ad status | Ad group (status) | Campaign (status) | Current final URL |
| --- | --- | --- | --- | --- |
| 663913336737 | PAUSED | Sprinkler Repair Near Me (ENABLED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 664011771797 | PAUSED | Sprinkler Repair Near Me (ENABLED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 733610415014 | PAUSED | Sprinkler Repair Near Me (ENABLED) | Irrigation & Sprinklers (ENABLED) | `…/offer-sprinkler-repair-a/` |
| 797294312301 | PAUSED | Irrigation Repair Near Me (ENABLED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 797294312313 | PAUSED | Irrigation Repair Near Me (ENABLED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 797325048229 | PAUSED | Irrigation Repair Near Me (ENABLED) | Irrigation & Sprinklers (ENABLED) | `…/offer-sprinkler-repair-b/` |
| 797294506065 | PAUSED | Sprinkler System Repair (ENABLED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 797404375133 | PAUSED | Sprinkler System Repair (ENABLED) | Irrigation & Sprinklers (ENABLED) | `…/offer-sprinkler-repair-b/` |
| 797404528958 | PAUSED | Sprinkler System Repair (ENABLED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 714045747006 | **ENABLED** | Winterization (**PAUSED**) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 725671488364 | PAUSED | Irrigation & Sprinklers (PAUSED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 725671488370 | PAUSED | Irrigation & Sprinklers (PAUSED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 725671488373 | PAUSED | Irrigation & Sprinklers (PAUSED) | Irrigation & Sprinklers (ENABLED) | `offerdfw…/` |
| 714159492923 | ENABLED | Landscape Outdoor Lighting (PAUSED) | Outdoor Lightning (PAUSED) | `offerdfw…/` |
| 733612724636 | ENABLED | Drainage Solutions (PAUSED) | Drainage (PAUSED) | `offerdfw…/` |

**Ad 714045747006 is the one to watch** — an ENABLED ad in a PAUSED ad group inside the ENABLED
campaign. Unpausing that ad group would immediately resume traffic to `offerdfw`.

#### Promotion assets — **CORRECTED**

| Asset ID | Target | Campaign link | Link status |
| --- | --- | --- | --- |
| **89872396866** | `https://offerdfw.progreenlandscapesolutions.com/` | `campaignAssets/20315156610~89872396866~PROMOTION` | **REMOVED** |
| | | `campaignAssets/22027188372~…` (Winterization, PAUSED) | PAUSED |
| | | `campaignAssets/22379036365~…` (PMax, PAUSED) | PAUSED |
| **89872442988** | `https://offerdfw.progreenlandscapesolutions.com/` | `campaignAssets/20315156610~89872442988~PROMOTION` | **REMOVED** |
| | | `campaignAssets/22027188372~…` | PAUSED |
| | | `campaignAssets/22379036365~…` | PAUSED |

> **CORRECTION — supersedes `final-audit-and-revamp-plan.md` F32 and §13.3.** Those documents
> stated that "two **live-campaign** promotion assets still point at `offerdfw`". **[FRESH-API]
> shows both campaign-asset links on the live campaign are `REMOVED`.** They survive only as
> PAUSED links on two PAUSED campaigns. **They are not a live dependency.** The assets
> themselves still exist and still carry the `offerdfw` target, so they remain in the inventory
> — but no cutover action is required for serving traffic.

#### Other URL-bearing resources

| Level | Resource | Value | Action |
| --- | --- | --- | --- |
| **Account** | `customer.tracking_url_template` | `https://monitor.clickcease.com/tracker/tracker.aspx?id=…&url={lpurl}&…&ccpturl=offerdfw.progreenlandscapesolutions.com&pl={placement}` | **Flag only.** Contains a hard-coded `offerdfw` reference. **ClickCease-owned — do not modify without ClickCease coordination** |
| **Campaign 20315156610** | `tracking_url_template` | `{lpurl}?utm_source=google&utm_medium=cpc&utm_campaign={_campaign}&utm_id=20315156610` | Review in Batch 1B — see §4.3 |
| Campaign 21718922354 | `tracking_url_template` | `…&utm_id=21718922354` | correct |
| Campaign 22027188372 | `tracking_url_template` | `…&utm_id=**20315156610**` | **wrong campaign ID** — flag |
| Campaign 22255200632 | `tracking_url_template` | `…&utm_id=**21718922354**` | **wrong campaign ID** — flag |
| Campaign 22379036365 | `tracking_url_template` | `…&utm_id=**20315156610**` | **wrong campaign ID** — flag |
| Ad group level | `tracking_url_template`, `final_url_suffix` | **all empty** | none |
| Keyword level | `final_urls`, templates | **none set** | none |
| `final_url_suffix` | account, campaign, ad group, ad | **all empty** | none |
| Sitelinks (27/22/22) | `/dfw/services/…`, `/dfw/service-areas/…` | none touch the three hosts | Batch 3 |
| Call asset 89872541418 | (214) 301-3385 | no URL | **preserve** |
| `customer_asset` | — | **zero account-level assets** | none |

### 4.3 Tracking-template precedence — important

**[FRESH-API]** Google Ads applies the **most specific** tracking template. Because every
campaign sets its own, the **account-level ClickCease template is overridden and does not apply
to any campaign.** **[INFER]** ClickCease click-monitoring via the tracker URL is therefore
effectively bypassed; its IP-exclusion function (6 `IP_BLOCK` criteria) is unaffected.

**This is flagged, not changed.** ClickCease is an authorized integration and any change is a
ClickCease/Green Marketing decision, not a Claude action.

### 4.4 Cutover sequence — do not deviate

| Step | Action | Owner |
| --- | --- | --- |
| 1 | Build the canonical page per the developer handoff | Dev team |
| 2 | QA: phone replacement, forms, attribution fields, tags, performance, responsive | Dev + GM |
| 3 | Confirm the page can safely receive traffic (prelaunch checklist) | GM |
| 4a | Repoint ad **797294303667** (Irrigation Repair Near Me) | Claude, after approval |
| 4b | Repoint ad **797325463324** (Sprinkler System Repair) | Claude, after approval |
| 4c | Repoint ad **714659486058** (Sprinkler Repair Near Me) | Claude, after approval |
| 5 | Verify cutover — GAQL read-back + live load + conversion arrival | Claude + GM |
| 6 | Repoint the 15 non-serving URL-bearing ads | Claude, after approval |
| 7 | Review campaign tracking templates and the three wrong `utm_id` values | Claude, after approval |
| 8 | **End Nelio experiment 3619**; retire or 301-redirect obsolete pages | Dev team |
| 9 | **Only now**: exclude `6886103719` from the Conversions column | Claude, after approval |
| 10 | **Only now**: remove the `__awcc` tag from `GTM-NZSMS9RB` | Dev / GTM admin |
| 11 | Promote WhatConverts qualified imports to primary — **only after test evidence** | GM + Claude |

**Do not repoint any ad or asset until the new page is live and passes QA.**
**Steps 9 and 10 must never precede step 8.**

### 4.5 Rollback

| Step | Rollback |
| --- | --- |
| 4a–4c, 6 | Restore the exact final URLs in §4.2 — all recorded |
| 7 | Restore the exact template strings in §4.2 |
| 8 | Nelio retains experiment state; a paused experiment can resume |
| 9 | Re-set `include_in_conversions_metric: true` on `6886103719` |
| 10 | GTM keeps full version history; republish the prior version |

### 4.6 Prelaunch verification (before step 4)

Page renders **(214) 300-9564** in source · WhatConverts swaps it to a pool number at runtime ·
**no `tel:%91phone%93` anywhere** · every `tel:` href valid and swap-compatible · Google
website-call replacement **not** competing with WhatConverts on the same number · form submits
to WhatConverts with hidden `gclid`/`gbraid`/`wbraid`/UTM/landing URL/referrer/source populated ·
**no Austin tags or content** · **no 10% OFF** · **no unverified claims** · same-day wording is
exactly "Same-Day Service May Be Available." · tags fire **without** requiring interaction ·
no A/B redirect · mobile and desktop pass · Core Web Vitals acceptable.

### 4.7 Postlaunch verification (after step 5)

GAQL read-back confirms the three final URLs · a real ad click reaches the canonical page with
`gclid` intact · WhatConverts records the visitor with the click ID · a genuine customer lead
(never a test lead) appears in WhatConverts with attribution · `6886101052` and `6617381255`
continue to record · **no conversion count increase attributable to duplication**.

---

## 5. Batch 1C — Measurement migration and deduplication

### Option 1 — Google native measurement remains authoritative

| Aspect | Design |
| --- | --- |
| **Primary** | `6617381255` (AD_CALL) · `6886101052` (form) |
| **Secondary** | `7717433751`, `7717433754`, legacy actions |
| `6886103719` | Used **only** on pages compatible with its configured replacement number. After cutover no such page serves → exclude from Conversions (step 9) |
| **WhatConverts role** | Lead detail and qualification only. **No conversion import** |
| **Dedupe rule** | Trivial — nothing is imported |
| **Bidding goal** | PHONE_CALL_LEAD/CALL_FROM_ADS + SUBMIT_LEAD_FORM/WEBSITE |
| **Dependencies** | None beyond Batch 1A |
| **Risk** | **Low** |
| **Rollback** | n/a |
| **Verification** | Conversions stay at the current 3.00 / 5.00 baseline |
| **Reporting effect** | No change |
| **Limitation** | **Cannot ever carry qualification, booked estimates, revenue, or gross profit.** Counts raw events, including spam |

### Option 2 — WhatConverts qualified-lead imports become authoritative

| Aspect | Design |
| --- | --- |
| **Primary (end state)** | `7717433754` (qualified calls) · `7717433751` (qualified forms) |
| **Secondary (end state)** | `6617381255`, `6886101052` — **retained, never deleted**, so history survives |
| **Dedupe rule** | **Exclude every WhatConverts lead whose receiving tracking number is (214) 301-3385** (`Google Call Extension` source). Those are already counted by `6617381255`. Key on the WhatConverts **lead ID**, reconciled 1:1 against Ads call-asset conversions |
| **Qualification** | Owner marks qualified/quotable in WhatConverts. Spam, wrong numbers, job seekers, vendors, and out-of-area leads are **never** imported |
| **Latency** | Qualification may take days; the 60-day click window on both actions accommodates it |
| **Flow** | website call / form → WhatConverts lead → owner qualifies → qualified lead imported → booked estimate → job → revenue → (later) gross profit |
| **Dependencies** | WhatConverts console access · proven dedupe · **successful test data** |
| **Risk** | **High if rushed** — demoting a working primary before the replacement is proven would leave the account with **no** reliable signal |
| **Rollback** | Restore `primary_for_goal` / `include_in_conversions_metric` on `6617381255` and `6886101052`; demote the WhatConverts actions |
| **Verification** | ≥ 2 weeks of 1:1 reconciliation with zero duplicates before any demotion |
| **Reporting effect** | Conversions fall to **qualified** leads only — lower count, far higher meaning |
| **Hard gate** | **Never demote `6886101052` until the WhatConverts form import has received successful test data and reconciles correctly** [USER] |

### Recommendation — **phased hybrid**, and here is the evidence for it

**Adopt the hybrid, staged.** Neither pure option is safe right now.

| Evidence | Why it forces the hybrid |
| --- | --- |
| Both WhatConverts actions have **received nothing** — `last_received_request` empty **[FRESH-API]** | They are **[UNVERIFIED]**. Making an unproven action primary would be an assumption, which [USER] policy forbids |
| `6617381255` and `6886101052` are the **only** signals that have fired in 90 days **[FRESH-API]** | Demoting them now risks total signal loss |
| The call asset dials a WhatConverts number **[RUNTIME]** | Guarantees duplication unless Call Extension source is excluded |
| Qualification takes days and is manual **[USER]** | Only WhatConverts can express "qualified" — Google native never can |
| Target CPL is **$120 qualified**, cost per booked estimate **$180** **[USER]** | Those are *qualified* economics; raw-event counting cannot measure them |

**Phase order:**

1. **Now (1A):** WhatConverts actions → secondary. Native stays primary. Zero reporting impact.
2. **After cutover:** exclude Google Call Extension source from imports; let `7717433754` and
   `7717433751` receive **as secondary** and accumulate real data.
3. **After ≥ 2 weeks of clean 1:1 reconciliation:** promote `7717433754` to primary for
   **website/organic** qualified calls, while `6617381255` **stays primary** for call-asset calls.
4. **After the form import proves out:** promote `7717433751`; demote `6886101052` to secondary
   **only then**, retaining it permanently for history.
5. **Later still:** enable Conversion Updates, then revenue, then gross profit.

This keeps a working signal at every moment and never counts one lead twice.

---

## 6. Live search-term waste **[FRESH-API]** (2026-05-14 → 2026-08-11)

484 search-term rows · $1,226.38 attributed of $2,904.68+ campaign spend (Google withholds
low-volume terms) · 5 conversions.

**Competitor and out-of-market, zero conversions — $332.49:**

| Term | Clicks | Cost |
| --- | --- | --- |
| lawn sense dallas | 3 | **$175.47** |
| lee engineering irrigation / lee engineering arlington texas | 2 | $80.13 |
| garden springs irrigation | 1 | $19.85 |
| just sprinklers albuquerque | 1 | $19.68 |
| h20rx | 1 | $19.11 |
| anything sprinklers albuquerque | 1 | $18.25 |

Also flagged: **`sprinkler repair in desoto tx` $19.50** — DeSoto is **not** in the approved
service-area list. The searcher was inside an approved ZIP (presence targeting), so this is a
**service-area question, not a targeting bug**. **Flagged only.**

---

## 7. Location inventory **[FRESH-API]** — campaign 20315156610

**74 positive criteria, zero negatives.** Resource names are
`customers/8735782888/campaignCriteria/20315156610~<criterionId>`.

| Type | Count |
| --- | --- |
| Postal Code | **70** |
| City | 3 |
| Airport | 1 |

**Cities:** `1026439` Grand Prairie · `1026441` Grapevine · `1026497` Irving
**Airport:** `9041382` Dallas Fort Worth International Airport

**Postal codes (70), criterion ID → ZIP:**

`9026793`→75006 · `9026798`→75019 · `9026809`→75038 · `9026810`→75039 · `9026817`→75050 ·
`9026818`→75051 · `9026819`→75052 · `9026820`→75054 · `9026824`→75060 · `9026825`→75061 ·
`9026826`→75062 · `9026827`→75063 · `9026855`→75104 · `9026862`→75116 · `9026871`→75137 ·
`9026905`→75203 · `9026909`→75207 · `9026910`→75208 · `9026913`→75211 · `9026914`→75212 ·
`9026920`→75219 · `9026921`→75220 · `9026923`→75224 · `9026928`→75229 · `9026931`→75232 ·
`9026932`→75233 · `9026933`→75234 · `9026934`→75235 · `9026935`→75236 · `9026936`→75237 ·
`9026944`→75247 · `9026946`→75249 · `9027188`→76001 · `9027189`→76002 · `9027191`→76006 ·
`9027194`→76010 · `9027195`→76011 · `9027196`→76012 · `9027197`→76013 · `9027198`→76014 ·
`9027199`→76015 · `9027200`→76016 · `9027201`→76017 · `9027202`→76018 · `9027205`→76021 ·
`9027206`→76022 · `9027211`→76034 · `9027214`→76039 · `9027215`→76040 · `9027222`→76051 ·
`9027224`→76053 · `9027225`→76054 · `9027229`→76060 · `9027246`→76092 · `9027249`→76103 ·
`9027250`→76104 · `9027251`→76105 · `9027257`→76111 · `9027258`→76112 · `9027262`→76117 ·
`9027263`→76118 · `9027264`→76119 · `9027265`→76120 · `9027276`→76137 · `9027278`→76148 ·
`9027279`→76155 · `9027284`→76180 · `9027285`→76182 · `9027304`→76244 · `9027307`→76248

**Geo target type:** `PRESENCE` / `PRESENCE` — already compliant. **[FRESH-API]**

### 7.1 Discrepancies — flagged only, nothing changed

| Observation | Note |
| --- | --- |
| The ZIP set is **Dallas-southwest / Irving / Grand Prairie / Arlington / Fort Worth / NE Tarrant** heavy | Consistent with the owner's stated selection |
| **Frisco, Plano, Allen, Richardson, University Park, Highland Park, Preston Hollow, Lakewood, Balch Springs, Duncanville, Coppell ZIPs are largely absent** from the live set, though the business serves them and the ads name Frisco and Plano | **Discrepancy flagged.** The owner's live selection is authoritative — **do not expand.** Worth a business conversation, not a change |
| `9041382` **DFW Airport** is targeted | Flagged. An airport target reaches travellers, not homeowners. **Do not remove without owner confirmation** |
| Zero negative location criteria | Consistent with presence targeting |

---

## 8. Division of responsibilities

| Work | Owner |
| --- | --- |
| Conversion-action field changes (1.1, 1.2, step 9) | **Claude, after approval** |
| Ad final-URL repointing (steps 4a–4c, 6) | **Claude, after approval** |
| Tracking-template review (step 7) | **Claude, after approval**, ClickCease coordination |
| Device modifier `30000` → 1.0 | **Claude, after approval** (Batch 2) |
| Negative-keyword changes | **Claude, after approval** (Batch 2) |
| Budget change | **Claude, after approval** (Batch 2) |
| RSA and asset rebuild | **Claude, after approval** (Batch 3) |
| WhatConverts source exclusion (1.8) | **Green Marketing / WhatConverts admin** |
| WhatConverts Conversion Updates | **Green Marketing**, after testing |
| Canonical page build, DNS for `offer.` subdomain | **Development team** |
| GTM edits, `__awcc` removal, publish | **Development team / GTM admin** |
| Gravity Forms hidden fields | **Development team** |
| Nelio 3619 shutdown, redirects | **Development team** |
| NitroPack exclusions | **Development team** |
| Claim verification, budget approval, service-area decisions | **User** |
| Real test call, if ever desired | **User — never Claude** |
