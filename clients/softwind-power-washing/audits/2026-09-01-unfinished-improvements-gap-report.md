# SOFTWIND POWER WASHING — UNFINISHED IMPROVEMENTS GAP REPORT

**Account** `Softwind Power Washing - Live` · `1521725229` · **Power Washing**
**Generated** 2026-09-01 America/New_York · **READ + DRAFT · zero external changes**

Every unresolved improvement in the account, the website and the measurement chain. **Nothing is
left outside this report or the execution ledger.**

---

## 1. Fresh drift check — 2026-09-01 20:20 ET

**Identity gate PASS.** `Softwind Power Washing - Live` / `1521725229` / manager `false` / test
`false` / **ENABLED** / **USD** / **America/New_York**. Conversion customer `customers/1521725229`
(self), tracking **MANAGED_BY_SELF**, `conversion_tracking_id` **18369652705**,
**cross-account conversion tracking NOT active**.

**Campaign names observed:** `24103511039` = **Power Washing** ✓ · `24145053510` = **Pressure
Washing** ✓. Both match expectation. Neither renamed or changed by this run.

**41 surfaces checked · 2 differences · both attributed, neither to Claude:**

| Difference | Class | Attribution |
|---|---|---|
| `24145053510` name → **Pressure Washing** | **MANUAL OWNER CHANGE** | `change_event` `GOOGLE_ADS_WEB_CLIENT`, 2026-08-31 18:16 and 2026-09-01 14:21. Claude's writes log as `GOOGLE_ADS_API`. |
| `campaign_asset` 16 → 20 | **MANUAL OWNER CHANGE — already documented** | Owner added four links 2026-08-31 ~10:52; baseline predates it. |

**Metric drift (normal):** September 1 moved from 0 valid clicks / $0.00 at 15:01 to **1 valid click
at $29.50** by 20:20. **Google invalid-click adjustments:** 11 invalid clicks on 12 raw clicks today,
still ~100% mobile — unchanged pattern, credited by Google, not billed.

**No configuration drift attributable to Claude. Everything else is unchanged:** both ceilings
$30.00, budgets $41.50 / $41.11, TARGET_SPEND, PRESENCE/PRESENCE, 80 locations, Connecticut `21139`
excluded, Mon–Sat 08:00–18:00, Search Partners / Display / AI Max **off**, asset automation
**OPTED_OUT**, 12 enabled ad groups, 214 keywords, 264 campaign negatives, **0 ad-group negatives**,
20 assets, **0 audiences**, **0 gender / age / income criteria**, 4 conversion actions unchanged, 4
conversion goals unchanged.

---

## 2. New evidence this run — live Quality Score

First readable keyword-level Quality Score in this account's life:

| Keyword | Ad group | Campaign | QS | Expected CTR | Ad relevance | **Landing-page exp.** |
|---|---|---|---:|---|---|---|
| `power washing near me` PHR+EXA | Power Washing Near Me | A | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** |
| `power washing services near me` PHR+EXA | Power Washing Services Near Me | A | **3** | BELOW_AVERAGE | ABOVE_AVERAGE | **BELOW_AVERAGE** |
| `power washing services near me` PHR+EXA | Power Washing Services Near Me | B | **5** | BELOW_AVERAGE | ABOVE_AVERAGE | **AVERAGE** |

**The same keyword text scores QS 3 against the Islip offer page and QS 5 against a different page.**
Ad Rank is bid × Quality Score, so a badly scored landing page is part of why this account pays
~$29.50 a click. **This is the strongest evidence yet that the landing page outranks the bid in
priority order** — and it is why Stage 6 (CPC) sits behind Stage 2 (pages), not in front of it.

All three components are actionable: **expected CTR** → new RSAs (Stage 3); **ad relevance** →
keyword/ad alignment (Stage 3); **landing-page experience** → Stage 2.

---

## 3. Unfinished by area

### A. Measurement and attribution — 1 open question, 8 backlog items

| Item | State | Stage |
|---|---|---|
| Conversion goal hierarchy | **RESOLVED — verdict D, no defect.** All 4 layers verified correct 2026-09-01. | closed |
| **Does the form event fire at all?** | **OPEN — the one blocking unknown** | **1** |
| Website-call conversion verification | BLOCKED — do not test until the form path is understood | 10 |
| Call-asset conversion verification | **UNTESTABLE** — 88 call impressions, **0 call clicks**, **0 `call_view` rows** all-time. The path has never been exercised. | 10 |
| WhatConverts number-replacement verification | OPEN — a `wc_swap` number was seen on main-site pages 2026-08-26 and not re-confirmed | 10 |
| Foreign tag `AW-17878095007` | **OPEN — present on all 6 offer pages + 2 main-site pages.** Confirmed a *different* account from this one's `AW-18369652705`. Removal only after ownership and event behaviour are proven. | 1 then 2 |
| GCLID / GBRAID / WBRAID / UTM persistence | Page-side PASS verified 2026-08-31; end-to-end unproven | 1 |
| CRM / webhook delivery | **UNKNOWN destination** since 2026-08-26 | 1 (T-6 discovers it) |
| Unique lead-ID and deduplication | NOT STARTED | 10 |
| Qualified-lead and sold-job offline feedback | NOT STARTED — blocked on CRM | 12 |

**Phone numbers to reconcile.** Fresh Google Ads read finds **exactly one call asset**:
`403335872180`, **(631) 502-7946**, US, `USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION`. It matches the
approved landing-page number. **The GLE number +1 631-519-8373 and the GBP number +1 631-315-8655 do
not appear anywhere in this Google Ads account** — they belong to Local Services / Business Profile
and must be reconciled in WhatConverts and GBP, not through an Ads read. Do not assume any of the
three is still routing correctly; each needs fresh verification at Stage 10.

**Lead classification rule for all reporting:** count a lead as relevant when **either** the request
is for power washing, pressure washing, house washing, soft washing, driveway, patio or an obviously
equivalent exterior-washing service **regardless of source**, **or** it used an approved Power
Washing tracking number. Always separate unique new leads · repeat contacts · existing-customer
support · spam · wrong service · wrong geography · qualified estimate requests · scheduled estimates
· sold jobs. **Protect lead PII in general reports.**

### B. Landing pages — 6 pages × 4 shared defects, all still open

| Priority | Defect | Pages | Status |
|---|---|---|---|
| **P0** | Browser title reads **"Softwind Landscape & Masonry"** — the scope-fenced sibling brand | **all 6** | OPEN |
| **P0** | Foreign tag `AW-17878095007` on every paid view | 6 offer + 2 main | OPEN |
| **P1** | H1 city-locked to "Islip, West Islip & Dix Hills" while campaigns target **80** places | 5 of 6 | OPEN |
| **P1** | Unsupported "Offer Ends" countdown that resets on reload | **all 6** | OPEN |
| **P2** | No reviews, rating, years, licence or insurance | all | **BLOCKED on client verification** |
| **P3** | `/patio-power-washing/` title says "Power", H1 says "Pressure" | 1 | OPEN |
| **P3** | Mobile CTA hierarchy weak/generic | all | OPEN — assessed at Stage 2 |

**Verified already correct, do not re-litigate:** HTTP 200 no redirects · approved tracked
**(631) 502-7946** in `tel:` and body on all six · GCLID and all four UTMs persist · 5-field Gravity
Form (`gform_1`) · **mobile/desktop parity MATCH on all six** (~163–170 KB both) · GA4
`G-D4BZM40RYD`, GTM `GTM-P3LD97NN`, WhatConverts and ClickCease all loading.

**Page-speed note:** every page ships ~165 KB of HTML on mobile. Parity is confirmed; actual mobile
load speed has **not** been measured and is a Stage 2 diagnostic, not a proven defect.

**A better Soft Washing page already exists** — `/power-washing-soft-washing/` is not city-locked and
has 17 Long Island mentions. Evaluate the swap at Stage 2. **No new page needs building.**

**Never invent** towns, response times, prices, licences, warranties, years in business, ratings,
promotions or guarantees.

### C. Campaign structure

| Item | State |
|---|---|
| Two overlapping campaigns | OPEN — consolidation to `24103511039`, campaign B retires last |
| `Power Washing Services Near Me` duplicated in **both** campaigns | OPEN — `202870585430` and `198082078783` |
| 3 zero-volume city SKAGs still ENABLED | OPEN — Islip, West Islip, Dix Hills; 1 impression between them all-time |
| 2 legacy mixed-intent containers | OPEN — `205713509704` (17 texts), `205713509744` (14 texts), `205713509664` (12 texts) all paused |
| **0 ad-group negatives account-wide** | OPEN — no routing enforcement exists at all today |
| 5 of the 6 final groups sit **paused and ready** | **Opportunity — no ad group creation needed** |

### D. Ads

12 RSAs live in campaign A, 12 in campaign B. **9 of 15 headlines in the Power Washing ads name
three hamlets** — the direct cause of the relevance problem and in conflict with the Long Island
wording decision. **12 replacements drafted and validated; all to be created paused.**

### E. Assets — parity complete, gaps remain

Per campaign: **4 sitelinks · 4 callouts · 1 structured snippet · 1 call asset**. Parity is done —
do not recreate. Outstanding:

| Gap | Blocker |
|---|---|
| Verified business-name asset | Verified advertiser identity |
| Verified business logo | Client-supplied |
| Rights-cleared project images | **Client-supplied only.** No stock landscaping, no fabricated photos, no AI images as completed-project proof. |
| Call-asset schedule stops 17:00 while campaigns run to 18:00 | Confirm the phone is answered 17:00–18:00 Mon–Fri. **⚠ The single call asset `403335872180` is shared by BOTH campaigns — editing its schedule rewrites hours on every linked campaign.** |
| Location asset | Business Profile link decision |
| Sitelink destination tracking | Sitelinks point at `softwindli.com`, not the offer subdomain — mixed attribution |

**Account-level sitelink cleanup is kept separate from additions.**

### F. Bidding

Both campaigns `TARGET_SPEND` (Maximize Clicks) with a **$30.00** ceiling. Campaign B still
`LEARNING_SETTING_CHANGE`. **Stays on Maximize Clicks** until conversion tracking is verified,
qualified conversions record, there is enough data, and lead quality is judgeable. **No CPC number
is pre-committed — not $12, $15, $18 or $22.**

### G. Audiences and demographics

**0 audiences, 0 gender, 0 age-range, 0 income-range criteria** — verified again today. Women are
not excluded. Unknown gender is not excluded. Nothing to undo. Audience work is Observation-only at
0% and is **not** an early recovery action.

### H. Traffic quality

**11 invalid clicks on 12 raw clicks today, ~100% mobile** — unchanged. Google filters and credits
them; the client does not pay. **ClickCease loads on every page yet syncs 0 `IP_BLOCK` criteria into
either campaign.** Worth the client's attention. **Do not remove or replace ClickCease.**

### I. Business economics — all UNKNOWN

Target CPL, CPQL, close rate, average job revenue, gross margin, lead value: **UNKNOWN**, recorded as
UNKNOWN in the work order, never inferred. Until they exist, no ROAS or profit-after-ad-spend figure
can be computed honestly, and none is presented.

---

## 4. Blocked on client or owner input

| # | Input | Blocks |
|---|---|---|
| IN-1 | Test email address (client alias, or RFC 2606 fallback) | Stage 1 execution |
| IN-2 | Named cleanup owner for the test record | Stage 1 execution |
| IN-3 | Which CRM/webhook receives Gravity Forms submissions | Stage 1 T-6 can discover it |
| IN-4 | Rights-cleared project photographs | Stage 8 |
| IN-5 | Verified answered-call hours, incl. 17:00–18:00 Mon–Fri | Stage 8 |
| IN-6 | Verified trust facts — reviews, rating, years, licence, insurance | Landing-page P2, all ad copy |
| IN-7 | Ownership of Google Ads account `AW-17878095007` | Foreign-tag removal |
| IN-8 | Verified economics | All profit reporting |
| IN-9 | Confirmation of one-campaign vs two | Stages 3–7 |

**None of these blocks the single next action.**
