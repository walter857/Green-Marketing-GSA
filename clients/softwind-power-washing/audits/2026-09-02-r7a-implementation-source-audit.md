# R7A IMPLEMENTATION SOURCE AUDIT

**Account** `Softwind Power Washing - Live` · `1521725229` · **Power Washing**
**Generated** 2026-09-02 America/New_York · **READ + DRAFT · zero external changes**

Evidence: `snapshots/r7a-public-code-inspection-2026-09-02T115916.json` ·
`snapshots/r7a-page-source-2026-09-02/` (7 rendered sources saved) ·
`audits/2026-09-02-r7a-page-code-inspection.csv` · `…-source-of-truth-matrix.csv` ·
`…-gtm-inventory.csv` · `…-whatconverts-inventory.csv` · `…-phone-number-roles.csv`

---

## 1. Access reality — two of the three asserted accesses do not exist

The brief states GTM and WhatConverts authenticated access are available. **I verified both
before reporting anything from either system, and neither is present.** I have not fabricated
inventory for systems I cannot read.

| System | Brief says | Verified reality | Evidence |
|---|---|---|---|
| Google Ads | AVAILABLE | **AVAILABLE — used throughout** | live API reads |
| **Google Tag Manager** | AVAILABLE | **NOT AVAILABLE** | The Google OAuth refresh token returns exactly one granted scope: `https://www.googleapis.com/auth/adwords`. No `tagmanager` scope, no separate GTM credential, no stored session. CLAUDE.md forbids broadening the Ads token. |
| **WhatConverts** | AVAILABLE | **NOT AVAILABLE** | `WHATCONVERTS_API_TOKEN` exists as a key in `.env` but its **value is empty** (length 0). |
| WordPress | NO ACCESS | NO ACCESS — **by design** | Not requested, not attempted. |

**`GTM-P3LD97NN` COULD NOT BE READ.**

**Consequence:** Tracks A and B cannot carry exact tag/trigger/variable/profile/pool IDs, so per
rule 18 **neither is fingerprinted**. Track C (developer tickets) and Track D (cross-account
record) are unaffected and complete. Everything provable from public code and the Google Ads API
was proved.

**To unblock:** a Tag Manager credential with `tagmanager.readonly` (or a container export), and a
populated `WHATCONVERTS_API_TOKEN`.

---

## 2. Google Ads verification — all confirmed, nothing mutated

**Identity PASS:** `Softwind Power Washing - Live` / `1521725229` / manager `false` / test `false`
/ **ENABLED** / **USD** / **America/New_York** / conversion customer `customers/1521725229` /
`CONVERSION_TRACKING_MANAGED_BY_SELF` / **cross-account conversion tracking NOT active**.

**Work order + client profile:** duplicate-key YAML validation **PASS**; all 10 field assertions
**PASS** (account, ID, MCC, service, vertical, scope approval, approver, read mode, August
objective closed, economics all UNKNOWN).

| Action | Status | Type / Category | primary | Counting | Window | Tag | Label |
|---|---|---|---|---|---|---|---|
| **7708725995** Submission Lead Form | ENABLED | WEBPAGE / SUBMIT_LEAD_FORM | **true** | ONE_PER_CLICK | 90d | `AW-18369652705` | **`FddkCOul59scEOHPqrdE`** |
| **7708765130** Website Phone Call Lead | ENABLED | WEBSITE_CALL / PHONE_CALL_LEAD | **true** | ONE_PER_CLICK | 30d, **60s min call** | `AW-18369652705` | **`ReAcCMrX6dscEOHPqrdE`**, phone `(631)502-7946` |
| **7711699090** Call Asset Lead | ENABLED | AD_CALL / PHONE_CALL_LEAD | **true** | ONE_PER_CLICK | 30d, 60s | — | — |
| **7713188607** Directions | ENABLED | GOOGLE_HOSTED / GET_DIRECTIONS | true | MANY_PER_CLICK | 30d | — | — |

**Campaign goal eligibility:** both campaigns — the three lead categories `biddable: true`,
**GET_DIRECTIONS `biddable: false` on both**. Unchanged, unmutated.

**Live paid Final URLs, read fresh from ENABLED ads in ENABLED ad groups (6 unique):**
`/driveway-pressure-washing/` · **`/house-pressure-washing-estimate/`** · `/patio-power-washing/` ·
`/power-washing-services-islip-west-islip-dix-hills/` · `/residential-pressure-washing/` ·
`/soft-house-washing/`

> **Correction:** the previous PLAN-R7A listed `/house-washing-company/` in scope. It is **not a
> live paid URL.** The live one is `/house-pressure-washing-estimate/`. Reading the account rather
> than reusing the older list caught this.

---

## 3. Exact source of every component

### `AW-17878095007` — the sibling Masonry tag

```
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-17878095007&cx=c&gtm=4e68v1">
```

The literal ID appears **exactly once** in the rendered source and **only inside that injected
script URL**. There is **no** hardcoded `gtag('config','AW-17878095007', …)` block anywhere. That
signature is consistent with GTM or a Google tag *linked destination* — **not** a hardcoded
snippet.

**PUBLIC EFFECT PROVEN — EXACT CONFIGURATION SOURCE REQUIRES AUTHENTICATED GTM READ.**

Runs on **all 7 pages**: page-view remarketing, user-list/rmkt collection, **website-call
replacement `wcm`** (`dn=6315027946`, label `SFv1CLSo--UbEJ-p-MxC`), and — proven at submission —
`en=form_start`, `en=form_submit` and **POSTs to `pagead/form-data/17878095007` and
`ccm/form-data/17878095007`**.

### `AW-18369652705` — the correct Power Washing tag

Same injection pattern, same conclusion about source. **Preserve.** It fires the conversion on
`/thank-you/` and **zero** `wcm` requests anywhere.

### The form conversion

Label `FddkCOul59scEOHPqrdE` on action `7708725995`. **Trigger is the `/thank-you/` page path** —
re-proven today: a bare visit with no form interaction fired `en=conversion` to both
`pagead/conversion/18369652705/` and `pagead/1p-conversion/18369652705/`. The six offer pages
fire **zero** conversions on load, which localises the trigger precisely.

### The website-call replacement

**Only the sibling account performs it.** `conversion/17878095007/wcm` fires on **7 of 7** pages;
`conversion/18369652705/wcm` fires on **0 of 7**. Softwind's own snippet —
`gtag('config','AW-18369652705/ReAcCMrX6dscEOHPqrdE',{'phone_conversion_number':'(631)502-7946'})`
— exists in Google Ads and **was never deployed**. That is a complete explanation for 0 `call_view`
rows across the account's life.

### Duplicate GTM load — **cause identified: option B**

| Artifact in delivered HTML | Count |
|---|---:|
| Inline bootstrap `(window,document,'script','dataLayer','GTM-P3LD97NN')` | **2** |
| `<script src="…gtm.js?id=GTM-P3LD97NN">` | **2** |
| `<noscript>` `ns.html?id=GTM-P3LD97NN` iframe | **2** |
| `GTM-P3LD97NN` occurrences | **6** |
| `dataLayer` after load | `gtm.js`, **`gtm.js`**, `gtm.dom`, `gtm.load` |

**The container snippet appears twice in the delivered HTML.** The two inline bootstraps differ in
whitespace, indicating **two separate injectors**. The browser de-duplicates the network fetch to
one `gtm.js`, which is why a network-only check misses it — **the dataLayer proves both ran**, so
every tag in the container can fire twice. Source is outside GTM →
**DEVELOPER TICKET REQUIRED (DEV-R7A3-03).**

### Duplicate Gravity Form — public evidence

`document.querySelectorAll('form#gform_1').length` = **2** on all six offer pages, with **22
duplicate HTML IDs** each (`gform_1`, `gform_wrapper_1`, `gform_fields_1`, `gform_submit_button_1`,
`input_1_1/3/4/7/9`, the `field_1_*` set, `gform_theme_1`, Divi's `et-boc`). `/thank-you/` has 0
forms and 2 duplicate IDs. **Honeypot verified present, hidden, and empty on every page.**

### Malformed phone link — public evidence

`a[href="tel:(631)"]` exists alongside `a[href="tel:(631) 502-7946"]` on **all 7 pages**,
including `/thank-you/`. Displayed number is `(631) 502-7946` everywhere.

### `process.iconnode.com/google-ads/`

**Zero occurrences in the rendered source**, yet **1 POST per page load** on all 7 pages plus one
at submission. Runtime-injected — consistent with a GTM Custom HTML tag. **Authorization UNKNOWN**;
nothing in the client records documents it. Investigation ticket only, no removal.

---

## 4. Two corrections to my own earlier reporting

### 4a. WhatConverts is loaded by a WordPress plugin, and I misattributed its domain

```
<script id="whatconverts-tracking-script-js" src="//s.ksrndkehqnwntyxlhgto.com/158931.js?ver=7.1">
<script id="whatconverts-tracking-script-js-before">   (inline $wc_leads config)
```

Earlier receipts said "no request to a WhatConverts host was observed" and attributed
`p.ksrndkehqnwntyxlhgto.com` to **ClickCease**. **Both were wrong.** That obfuscated domain is
**WhatConverts'** own tracking host — the script number `158931` matches the `wc_visitor` cookie
prefix. The `-js` handle and `ver=` query are the WordPress `wp_enqueue_script` signature, so it is
delivered by a **WordPress plugin**.

**ClickCease is separately present** at `www.clickcease.com/monitor/stat.js` with a `noscript`
monitor pixel.

**This matters:** the `/keyword/` and `/lead/form` POSTs seen at the controlled submission were
**WhatConverts capturing the lead**, not ClickCease — so the test lead was very likely recorded.

### 4b. WhatConverts attribution works; only DNI is broken

`wc_client` carries source, medium, campaign, content, term **and the GCLID**. `wc_swap` nominates
`6315025402` and `6315535927`, but the DOM renders the static `(631) 502-7946` in both body text
and the `tel:` href on all 7 pages. **The replacement never executes.**

**Root cause NOT determined.** The brief forbids inferring it from cookies alone, and an
authenticated read is impossible. Candidate causes are enumerated in PLAN-R7A2 — including one
newly plausible mechanism: **the duplicate form and 22 duplicate HTML IDs could cause an ID-bound
swap selector to target the wrong node.**

---

## 5. Phone numbers

| Number | Role | Present in the account or on the pages? |
|---|---|---|
| **(631) 502-7946** | approved landing-page number | body text + `tel:` on all 7; `dn=` of the sibling `wcm`; `phone_conversion_number` of action 7708765130; call asset `403335872180` |
| (631) 502-5402 | previously recorded untracked main-site number | `wc_swap` position 1 — **never rendered** |
| (631) 553-5927 | WhatConverts swap candidate | `wc_swap` position 2 — **never rendered** |
| (631) 519-8373 | GLE / Local Services tracking number | **absent** from the Ads account and every inspected page |
| (631) 315-8655 | GBP / Business Profile tracking number | **absent** from the Ads account and every inspected page |

The last two live outside Google Ads and cannot be reconciled without WhatConverts or GBP access.

---

## 6. Call-tracking architecture — DEFERRED, deliberately

**No architecture is selected in this run.**

The previous PLAN-R7A chose Option B (native Google replacement) **before reading any WhatConverts
configuration** — which the brief correctly identifies as a defect in that plan. Selecting again
from the same evidence base would repeat the mistake.

What is now known: WhatConverts **attribution works** (source, medium, campaign, term, GCLID all
captured) and only the **number swap** fails, for an undetermined reason. Green Marketing relies on
WhatConverts for lead quality and source reconciliation, and the brief requires that any
architecture preserve or replace call recordings, qualification, duplicate control and
qualified-lead/sold-job feedback. **Whether WhatConverts can meet that bar after a defensible
repair is exactly the question an authenticated read would answer, and it is unanswered.**

**Decision: selection is deferred to PLAN-R7A2 once WhatConverts can be read.** Choosing now would
be theory, and the brief explicitly forbids selecting Option C on theory — the same discipline
applies to A and B.

---

## 7. Conversion deduplication design (documented, nothing created)

| Layer | Mechanism | Action |
|---|---|---|
| **A. Initial form lead** | direct Google Ads website conversion after **verified** success | `7708725995` |
| **B. Initial qualified website call** | per the architecture selected later | `7708765130` or WhatConverts upload |
| **C. Call-asset lead** | Google Ads call asset, separate path | `7711699090` |
| **D. Qualified lead** | downstream outcome, **unique lead ID** | new action, not yet created |
| **E. Sold job** | downstream outcome, **unique job/transaction ID** | new action, not yet created |

**Rules:** do not upload a WhatConverts-qualified form lead into `7708725995` when the direct
Google Ads event already recorded it. Do not upload the same call to two primary call actions.
**No conversion action was created or changed in this run.**

**Future offline route:** **Google Data Manager API** for qualified-lead and sold-job outcomes, per
agency policy — the legacy Google Ads upload path only after confirming developer-token
eligibility. Blocked until a CRM exists.

---

## 8. What remains unresolved

| Item | Blocked on |
|---|---|
| GTM tag/trigger/variable inventory | Tag Manager credential |
| Which container tag emits `AW-17878095007` | Tag Manager credential |
| WhatConverts profile, pool, rules, selectors | populated `WHATCONVERTS_API_TOKEN` |
| **WhatConverts DNI root cause** | authenticated read — **must not be guessed** |
| Test-lead record in WhatConverts | authenticated read |
| Call-tracking architecture selection | the two above |
| `process.iconnode.com` authorization | DEV-R7A3-06 |
| Sibling-account scoping | separate work order + approval |
