# Google Ads Change Manifest — 2026-08-11

**Account:** Pro Green - Dallas - Live · **8735782888** · manager **3373711342**
**Backup:** `clients/pro-green-dallas/backups/pre-change-2026-08-11T1300/`
**Status:** all batches below have been **EXECUTED**. See `google-ads-execution-log.md` and
`google-ads-post-change-verification.md`.

Evidence labels: **[FRESH-API]** · **[RUNTIME]** · **[USER]** · **[INFER]** · **[UNVERIFIED]**

---

## Pre-mutation safeguards completed

| # | Safeguard | Result |
| --- | --- | --- |
| 1 | Export current resource state | 9 JSON files written to the backup directory |
| 2 | Timestamped backup | `pre-change-2026-08-11T1300/` |
| 3 | Exact proposed mutation written | this document |
| 4 | Account identity validated | **re-run immediately before every batch** — 8 gates, all PASS |
| 5 | Resource ownership validated | every conversion action `owner_customer = customers/8735782888` |
| 6 | Change within authorization | confirmed per batch below |
| 7 | Rollback value exists | recorded per row |

**Backup contents:** `conversion-actions.json` (14) · `campaign-criteria.json` (737) ·
`ad-group-criteria.json` (567) · `ads.json` (13) · `assets.json` (568) ·
`campaign-assets.json` · `ad-group-assets.json` (84) · `campaigns-and-budgets.json` (5) ·
`gate.json`.

---

## Batch A — Conversion containment · **ATTEMPTED, DID NOT APPLY**

| Field | Value |
| --- | --- |
| **Resources** | `customers/8735782888/conversionActions/7717433751` (Whatconverts Form)<br>`customers/8735782888/conversionActions/7717433754` (Whatconverts Calls) |
| **Current** | `primary_for_goal: true`, `include_in_conversions_metric: true` |
| **Proposed** | `primary_for_goal: false`, `include_in_conversions_metric: false` |
| **Reason** | Both are **[UNVERIFIED]** with **zero data ever received**. Importing a Google Call Extension-source call would duplicate `6617381255`, which already counts it natively |
| **Dependency** | none |
| **Risk** | very low — zero data means zero present-day reporting impact |
| **Rollback** | set both fields back to `true` |
| **Verification** | GAQL read-back of both fields |
| **Expected reporting effect** | none today; prevents future silent inflation |

**RESULT: the mutation was accepted by the API but had no effect.** Read-back shows both fields
still `true`. **[FRESH-API]** This account uses **account-level conversion goals**
(`customer_conversion_goal`), under which `primary_for_goal` and `include_in_conversions_metric`
are derived from the goal configuration rather than settable per action.

Per the run instruction — *"If the API does not support the exact intended primary/secondary
change safely, stop that individual action and document the limitation"* — **this item was
stopped, not retried.** No unintended state change occurred; read-back confirms the prior values
are intact. Alternatives are in §"Deferred work" below.

---

## Batch B — Devices · **EXECUTED AND VERIFIED**

| Resource | Device | Current | Proposed | Result |
| --- | --- | --- | --- | --- |
| `campaignCriteria/20315156610~30000` | DESKTOP | `bid_modifier 0.0` (**−100%, excluded**) | **`1.0`** (0% adjustment, eligible) | ✅ `1.0` |
| `campaignCriteria/20315156610~30002` | TABLET | `bid_modifier 0.0` (−100%) | **no change** | ✅ `0.0` |
| `campaignCriteria/20315156610~30001` | MOBILE | not set | **no change** | ✅ unset |

**Reason** [USER] policy: mobile enabled, desktop enabled, tablet excluded. Desktop was excluded
while **34.44% of impression share was being lost to budget and 36.17% to rank** [FRESH-API].
**Risk** medium — adds eligible inventory and therefore cost. **Rollback** set `30000` back to `0.0`.

---

## Batch C — Negative keywords · **EXECUTED AND VERIFIED**

Pre-check performed before applying: current inventory saved (620), add/remove manifest built,
every proposed negative checked against converting search terms and active keywords.

### Guard rules applied

1. Never negative a term that produced a conversion.
2. Never negative text contained in an active keyword.
3. Never negative in-scope repair vocabulary unless the reason is competitor, out-of-scope
   service, or retail-parts.

**Protected converting terms** [FRESH-API]: `dallas sprinkler company`, `home irrigation services`,
`irrigation services near me`, `irrigation system company`, `sprinkler plano tx`.

### Removals — 3, all confirmed gone

| Criterion ID | Negative | Match | Reason | Rollback |
| --- | --- | --- | --- | --- |
| `40961223` | **`cost`** | PHRASE | Blanket blocker of all cost intent. 12 targeted off-service cost negatives already do the real work | re-add as PHRASE |
| `101679803` | **`how much`** | PHRASE | Same over-blocking; killed "how much to fix a sprinkler valve" | re-add as PHRASE |
| `337388455191` | **`sprinkler valve replacement cost`** | EXACT | **Valve repair is explicitly in scope** [USER] | re-add as EXACT |

**Preserved deliberately** — the 12 targeted off-service cost negatives:
`landscaping maintenance cost`, `landscaping design cost`, `mulching cost near me`,
`aeration cost near me`, `edging cost near me`, `mowing cost near me`,
`how much does it cost to install sprinklers`, `lawn maintenance cost near me`,
`cost to install automatic sprinkler system`, `landscaping installation cost`,
`overseeding cost near me`, `blowing cost near me`. Verified still present.

### Additions — 40, all confirmed present

| Category | Terms | Match | Measured 90-day waste |
| --- | --- | --- | --- |
| **Competitor** | lawn sense dallas · lawn sense plano · lawn sense texas · lee engineering irrigation · lee engineering arlington texas · garden springs irrigation · h20rx | EXACT | **$294.56, 0 conversions** |
| **Out-of-market** | albuquerque · sioux falls | PHRASE | **$37.93, 0 conversions** |
| **Austin (separate operation)** | austin · round rock · cedar park | PHRASE | preventive [USER] |
| **Employment** | jobs · job openings · careers · salary · apprentice | PHRASE | preventive |
| **DIY / instructional** | how to · diy · tutorial · youtube | PHRASE | preventive |
| **Training** | training · certification · license class | PHRASE | preventive |
| **Retail** | home depot · lowes · amazon · for sale · buy online | PHRASE | preventive |
| **Retail parts** | parts store · replacement parts | PHRASE | preventive |
| **No hire intent** | free sprinkler system · volunteer | PHRASE | preventive |
| **Out-of-scope install** | new install · new installation · install cost | PHRASE | preventive |
| **Out-of-scope design** | system design | PHRASE | preventive |
| **Out-of-scope landscaping** | lawn mowing · tree service · sod installation | PHRASE | preventive |

### Deliberately **NOT** added — two rejected on policy grounds

| Candidate | Why rejected |
| --- | --- |
| **`hiring`** PHRASE | *"hiring a sprinkler repair company"* is **buyer intent**. `CLAUDE.md` protects `hire`; blocking `hiring` violates that rule's intent |
| **`sprinkler experts`** EXACT | Generic buyer language, **not a proven brand**. Blocking it risks a valid sprinkler-repair query |

**Total campaign negatives: 620 → 657.** **Rollback** remove the 40 added criteria; re-add the 3 removed.

---

## Batch D — New high-intent keywords · **EXECUTED, CREATED PAUSED**

Created **PAUSED** per `CLAUDE.md` rule 10 ("create new resources paused") and rule 11
("never enable delivery in the same operation that creates resources").

| Ad group | ID | Keyword | Match |
| --- | --- | --- | --- |
| Sprinkler Repair Near Me | `151125103616` | sprinkler head repair | EXACT |
| Sprinkler Repair Near Me | `151125103616` | sprinkler head repair | PHRASE |
| Sprinkler Repair Near Me | `151125103616` | sprinkler head replacement | EXACT |
| Sprinkler System Repair | `191996690566` | sprinkler valve repair | EXACT |
| Sprinkler System Repair | `191996690566` | sprinkler valve repair | PHRASE |
| Sprinkler System Repair | `191996690566` | sprinkler valve replacement | EXACT |
| Irrigation Repair Near Me | `190202910461` | irrigation valve repair | EXACT |
| Irrigation Repair Near Me | `190202910461` | irrigation valve repair | PHRASE |

**Reason** These four in-scope services — sprinkler head repair and valve repair — had **no
keyword coverage at all**, and were additionally blocked by the negatives removed in Batch C.
**Duplicate check** run against all 44 active keywords; zero duplicates found.
**Risk** low — paused, so no delivery. **Rollback** remove the 8 criteria.

---

## Batch E — Challenger RSAs · **EXECUTED, CREATED PAUSED**

One challenger per active ad group, alongside the untouched control. Control ads were **not**
paused.

| Ad group | New ad ID | Control ad (untouched) | Final URL — **UNCHANGED** |
| --- | --- | --- | --- |
| Sprinkler Repair Near Me | **820553894577** | `714659486058` still ENABLED | `…/dfw/offer-sprinkler-repair-b/` |
| Irrigation Repair Near Me | **820553894580** | `797294303667` still ENABLED | `…/dfw/offer-sprinkler-repair-a/` |
| Sprinkler System Repair | **820553894583** | `797325463324` still ENABLED | `…/dfw/offer-sprinkler-repair-a/` |

**Composition:** 15 headlines + 4 descriptions each. **Pinning: headline 1 only** — a deliberate
break from the controls, in which **all 15 headlines and all 4 descriptions are pinned**,
preventing any combination testing.

**Pre-flight validation run locally before the API call:** every headline ≤ 30 chars, every
description ≤ 90, paths ≤ 15, and a banned-claim scan for `10% off`, `emergency`,
`guaranteed same-day`, `winteriz`, `installation`, `design`, `landscaping`. **All passed.**

**Verified claims used:** licensed and insured · free estimates · 18-point check · satisfaction
guarantee. **Same-day wording appears verbatim** as *"Same-Day Service May Be Available."* in one
description per ad — never abbreviated, never in a headline where the required wording would not fit.

**Risk** none while paused. **Rollback** remove the 3 ads.

---

## Batch F — Assets · **EXECUTED AND VERIFIED**

### F1 — expired promotion removed from serving, reversibly

| Resource | Asset | Text | Current | Proposed | Result |
| --- | --- | --- | --- | --- | --- |
| `campaignAssets/20315156610~89872309308~CALLOUT` | `89872309308` | **"Claim Your Discount"** | ENABLED | **PAUSED** | ✅ PAUSED |

**The asset itself was not deleted** — only the serving association was paused, exactly as
required. **Rollback** set the link back to ENABLED.

Promotion assets `89872396866` and `89872442988` (both targeting `offerdfw…`) were already
`REMOVED` on the live campaign and needed no action.

### F2 — winterization sitelinks removed from serving

Five ENABLED ad-group sitelink links to **"Irrigation Winterization"** — an **excluded service**
in `client.yaml` — set to **PAUSED**:

| Ad group | Asset IDs |
| --- | --- |
| Sprinkler Repair Near Me | `205729352013`, `333127655836`, `335128948948` |
| Irrigation Repair Near Me | `334324133443` |
| Sprinkler System Repair | `334324133443` |

**Result:** 0 winterization sitelinks still enabled; 22 in-scope sitelinks remain serving.
**Rollback** set each link back to ENABLED.

### F3 — verified-claim callouts created, linked PAUSED

| New asset | Text | Link status |
| --- | --- | --- |
| `406645684107` | **Free Estimates** | PAUSED |
| `406472572838` | **18-Point System Check** | PAUSED |
| `406645681770` | **Satisfaction Guaranteed** | PAUSED |

Existing callouts untouched: `Get Free Online Quote`, `Licensed & Insured`, `Hassle-Free Service`
— all still ENABLED.

### F4 — call asset **NOT TOUCHED**

`89872541418` = **(214) 301-3385** → `6617381255`, status ENABLED. Verified unchanged.

---

## Batch G — Tracking-template `utm_id` corrections · **EXECUTED AND VERIFIED**

Applied **only to PAUSED campaigns**. The live campaign's template was **not touched**.
No ClickCease parameter was altered; the account-level ClickCease template was **not touched**.

| Campaign | Status | Before `utm_id` | After `utm_id` | Result |
| --- | --- | --- | --- | --- |
| `22027188372` Winterization | PAUSED | `20315156610` ❌ | **`22027188372`** | ✅ |
| `22255200632` Outdoor Lightning | PAUSED | `21718922354` ❌ | **`22255200632`** | ✅ |
| `22379036365` PMax | PAUSED | `20315156610` ❌ | **`22379036365`** | ✅ |
| `20315156610` **Irrigation & Sprinklers** | **ENABLED** | `20315156610` ✅ correct | **NO CHANGE** | ✅ unchanged |

Only the `utm_id` value changed; every other parameter in each template was preserved byte-for-byte.
**Rollback** exact prior strings are in `backups/…/campaigns-and-budgets.json`.

---

## Batch H — Staged budget increase · **EXECUTED AND VERIFIED**

| Field | Value |
| --- | --- |
| **Resource** | `customers/8735782888/campaignBudgets/12723712793` |
| **Current** | **$32.50/day** |
| **Proposed** | **$45.00/day** |
| **Result** | ✅ **$45.00**, STANDARD delivery |

**Gate calculation performed before mutating:**

| Input | Value |
| --- | --- |
| Month-to-date spend, 2026-08-01 → 08-11 | **$369.97** |
| Days remaining in August | 20 |
| New daily × days remaining | $45.00 × 20 = $900.00 |
| **Projected August total** | **$1,269.97** |
| **Confirmed monthly ceiling** | **$2,000.00** |
| **Verdict** | **WITHIN CAP** — the script would have refused to mutate otherwise |

**Why $45.00 and not $65.79.** The confirmed maximum is ≈$65.79/day, but the run instruction is
explicit: *"prefer a staged budget increase rather than one large increase"* and *"Do not double
the budget solely because unused monthly capacity exists."* $32.50 → $65.79 is exactly a
doubling. **$45.00 is a 38% step** that addresses the 34.44% impression share lost to budget while
leaving room for a second step once the negatives and desktop change have been observed.

**All five authorization gates satisfied:** containment attempted and documented · proven
irrelevant traffic now blocked (Batch C) · budget demonstrably restricting high-intent traffic
(34.44% IS lost) · remaining-month projection under the ceiling · documented and reversible.

**Rollback** set `amount_micros` back to `32500000` ($32.50).

---

## Deliberately NOT changed

| Item | Reason |
| --- | --- |
| **Any final URL** | [USER] forbidden this run. All three serving URLs verified unchanged |
| **Any phone number**, call asset `89872541418` | [USER] forbidden |
| **74 location criteria** | Owner-selected and authoritative. Verified all 74 intact |
| **Presence targeting** | Verified still `PRESENCE` |
| **Ad schedule** | 08:00–20:00 ET × 7 already equals the confirmed 7 AM–7 PM CT. **No change was needed** |
| **Bidding strategy** | TARGET_SPEND retained — the safest option on 5 conversions in 90 days |
| **Search Partners / Display** | Both verified still off |
| **`6886103719`** and its GTM tag | [USER] rule 9 — live URL dependencies still exist |
| **`6617381255`, `6886101052`** | The only two proven signals. Preserved |
| **Legacy conversion actions** | Preserved for history. **Nothing deleted anywhere** |
| **Account-level ClickCease template** | ClickCease is authorized; not to be modified |
| **Manager `2815082755`** | Never queried, never modified |
| **WhatConverts, GTM, WordPress, Nelio, NitroPack, DNS** | Out of scope this run |

---

## Deferred work

| Item | Why deferred | Exact next step |
| --- | --- | --- |
| **Conversion containment** (Batch A) | API silently no-ops on this account's goal model | Toggle in the Google Ads UI: **Goals → Conversions → Settings**, set both WhatConverts actions to **Secondary**. Alternatively set `customer_conversion_goal` biddability for `CONTACT/WEBSITE` and `CONTACT/CALL_FROM_ADS` to `false` — **broader blast radius, needs separate approval** |
| **Enabling the 8 new keywords** | `CLAUDE.md` rule 11 | One approval, then set status ENABLED |
| **Enabling the 3 challenger RSAs** | `CLAUDE.md` rule 11 | One approval, then set status ENABLED |
| **Enabling the 3 new callouts** | Same | One approval, then set link status ENABLED |
| **Second budget step to ≈$65.79** | Staged approach | After 14 days of post-change data |
| **Sitelink consolidation** to 6–8 | Needs the canonical page first | Batch 3 |
| **WhatConverts Call Extension source exclusion** | WhatConverts login barrier | GM / WhatConverts admin |
| **Bidding migration** | Needs ≥30 clean conversions | Documented gate |
