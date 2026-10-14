# SOFTWIND POWER WASHING — FINAL SENIOR STRATEGY RED-TEAM

**Generated:** 2026-08-31 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
**Zero external changes. No fingerprint created. This is not approval for any plan.**

Identity gate re-run fresh — `Softwind Power Washing - Live` / `1521725229` / manager `false` /
test `false` / ENABLED / USD / America/New_York — **PASS**.

This memo challenges the prior work rather than defending it. **Three prior recommendations
change.**

---

## 1. Fresh live account status

| | "Power Washing" `24103511039` | "Preassure Washing" `24145053510` |
|---|---|---|
| Status | ENABLED / SERVING / **ELIGIBLE** | ENABLED / SERVING / **LEARNING** |
| Bidding | TARGET_SPEND / ENABLED | TARGET_SPEND / **LEARNING_SETTING_CHANGE** |
| **CPC ceiling** | **30000000 micros ($30.00)** | **30000000 micros ($30.00)** |
| Daily budget | $41.50 | $41.11 |
| Search Partners / Display / AI Max | off / off / off | off / off / off |
| Impressions | 216 | 46 |
| **Valid clicks** | **12** | **6** |
| **Invalid clicks** | **62** | **11** |
| Cost | $403.09 | $192.78 |
| Valid avg CPC | $33.59 | $32.13 |
| CTR | 5.56% | 13.04% |
| **Conversions / all-conversions** | **0.00 / 0.00** | **0.00 / 0.00** |
| Search IS | 47.79% | 65.00% |
| Lost IS — rank | **49.12%** | 27.50% |
| Lost IS — budget | 3.10% | 7.50% |

**Account totals:** 30 ad groups (12 enabled) · 214 keywords · 54 ads · 264 campaign negatives ·
**0 ad-group negatives** · 20 campaign assets · **0 audiences** · **0 gender/age/income criteria**
· **0 IP_BLOCK criteria** · 18 valid clicks · $595.87 · **0 conversions**.

**No configuration drift.** The names are unchanged, including the "Preassure" misspelling.

---

## 2. Findings that remain valid

- **Zero recorded conversions on 18 valid clicks and $595.87.** Confirmed again.
- **The $30 ceiling functions as the price.** Seven of the nine post-ceiling clicks priced
  $29.04–$29.91.
- **The Conversions column is structurally zeroed.** All four `customer_conversion_goal` rows
  read `biddable: FALSE`; all four conversion actions read
  `include_in_conversions_metric: FALSE`.
- **The call path has never been exercised.** `CALLS` click type: **88 impressions, 0 clicks**.
  `call_view` returns **0 rows** across the whole retained log.
- **The two campaigns are not independent.** Shared buckets, shared pages, shared assets,
  proven cross-campaign query serving.
- **Google collapses power ↔ pressure into shared Planner buckets** in six places.
- **No demographic exclusions exist and none is proposed.**

## 3. Findings that changed

**Three things I got wrong or under-weighted, corrected here.**

### 3a. Invalid clicks are ~100% mobile — a pattern I had not isolated

| Device | Valid clicks | Invalid clicks | Invalid share of raw | Cost |
|---|---:|---:|---:|---:|
| **MOBILE** | 14 | **73** | **83.9%** | $422.11 |
| **DESKTOP** | 4 | **0** | **0.0%** | $173.76 |

**Every invalid click in the account's life is mobile. Desktop has never produced one.**
Concentration is also campaign-skewed: campaign A carries 62 of 73.

This is a signal, **not a billing problem** — Google already filtered and credited them, so they
never appear in the $595.87. It does not justify a mobile bid modifier: mobile is 14 of 18 valid
clicks and 71% of spend. Cutting mobile would remove most of the account's traffic to solve a
problem Google is already solving. **It does sharpen the ClickCease question** — the script loads
on every page while syncing **zero** `IP_BLOCK` criteria into either campaign.

### 3b. The uncapped data shows the true market clears ABOVE $30 — this argues against $12

I have been reporting "no observed click between $5.71 and $22.11" as evidence that $10 and $22
are indistinguishable. True, but I under-weighted the other half of the distribution.

**Uncapped clicks (08-17 → 08-27 12:25):** $5.71, $22.11, $22.13, $26.66, **$40.07, $42.67,
$54.49, $82.22** — mean **$37.01**, and **four of eight cleared above $30**.

The unconstrained market price for these auctions is materially **above** $30, and even at $30
the account loses **49.12%** of impression share on rank. **This account is genuinely in an
expensive auction with a weak quality signal, and cutting to $12 in one step is more aggressive
than the evidence supports.**

### 3c. My prior $12 recommendation is revised to **$15**

| Ceiling | Local demand clearing top-of-page LOW | Buckets |
|---|---:|---:|
| $10 | 15.8% | 1/6 |
| **$12** | **98.2%** | 5/6 |
| **$15** | **98.2%** | **5/6 — identical to $12** |
| $18 | 100% | 6/6 |

**$12 and $15 cover exactly the same measured demand.** $15 buys **25% more Ad Rank headroom for
zero coverage cost** — and headroom is precisely what an account with Quality Score 1 on its
biggest keyword needs, because Ad Rank is bid × Quality Score. The failure mode of too-low
(impressions with no clicks — the proven $5.00 pattern) is worse than too-high (fewer clicks,
but they arrive and teach you something).

**$30 → $15 is a 49% cut. That is a large step, and it is a step, not a destination.** If
delivery holds for 10 serving days, a second step to $12 becomes evidence-based. Going straight
to $12 skips the observation that would justify it.

---

## 4. Literal SKAG versus single-intent — the decision

| | **A. Literal SKAG** | **B. Single-intent** *(recommended)* | **C. Hybrid** |
|---|---|---|---|
| Campaigns | 1 | 1 | 1 |
| **Ad groups** | **19** | **6** | 8–9 |
| Unique keyword texts | 19 | 19 | 19 |
| Positive keyword objects | ~30 | ~30 | ~30 |
| **Routing negatives required** | **19 × 18 = 342** | **127** | ~200 |
| **Valid clicks per group per serving day** | **0.05** | **0.17** | 0.11 |
| Data fragmentation | **SEVERE** | Acceptable | High |
| Query control | Highest in theory | Strong | Strong |
| Ad relevance gain | Marginal — the ads would be near-identical | Good | Good |
| Landing-page match | Same 6 pages either way | Same | Same |
| Operational burden | **Very high** | Moderate | High |
| CTR / CPC / CVR effect | ↔ / ↑ / ↔ | ↑ / ↓ / ↑ | ↔ / ↔ / ↔ |
| Confidence | **Low** | **High** | Low |

# Literal SKAG is NOT the right structure for this account, and I should say so plainly.

The account takes **roughly one valid click per serving day.** Nineteen literal SKAGs would give
each ad group **one click every twenty days**. Quality Score, ad rotation and any optimisation
signal all operate at ad-group level; at that density none of them can function.

**The decisive technical point: you do not need an ad group to measure a keyword.** Google
reports impressions, clicks, cost, CTR, average CPC and Quality Score at the **keyword** level
inside `keyword_view`. Splitting `power washing` into its own ad group buys **ad differentiation
and routing control** — not measurement. And the ad message for `power washing`,
`power washing near me` and `power washing service` is materially the same: local power washing,
surface-specific method, free quote.

**There is a real conflict between structural purity and account performance here, and
performance wins.** A literal SKAG structure would look immaculate in an audit and would starve
every ad group of the volume it needs to learn.

**Recommendation: Option B — single-intent, 6 ad groups**, each with one canonical buying intent,
one landing page, one RSA message, and sibling routing negatives enforcing Walter's ownership
rule.

---

## 5. One campaign versus two

# ONE CAMPAIGN. Surviving ID: `24103511039`.

| Evidence | Reading |
|---|---|
| Shared Planner buckets | Google collapses power ↔ pressure in **6 buckets** |
| Cross-campaign query serving | 5 terms in both = 26.7% of clicks, 24.8% of spend |
| Multi-ad-group routing | 19 of 55 terms = **73.3% of clicks** |
| Duplicate ad groups | `Power Washing Services Near Me` enabled in **both** |
| Duplicate keywords | Identical 107 keyword rows in each |
| Locations | Identical 80 + Connecticut exclusion |
| Goals / schedule / assets | Identical |
| **Landing pages** | **All 8 shared — 100%** |
| Learning | One ELIGIBLE, one LEARNING — split state |
| Valid clicks | 12 / 6 — neither has a usable sample alone |

**Option 1 (two campaigns) is not achievable**: separating them needs mirrored cross-campaign
negatives, and negativing `pressure washing services near me` out of the Power campaign removes
demand from the **same 260/mo bucket** `power washing near me` occupies. The head terms cannot be
split at all.

**Option 3 (hybrid) has no qualifying second intent**: same geography, budget objective,
conversion actions, schedule and landing-page path. Commercial is the only candidate and it is
outside verified scope with no commercial landing page.

**A synonym does not justify a campaign. Neither does a name.**

---

## 6. Final BOFU keyword decision

Local Keyword Planner, current 80-target footprint, deduped buckets. **1,980 unique searches/mo.**

| Keyword | Vol | Comp | TOP low–high | Current owner | Recommended owner | BOFU | Equip. ambiguity | LP align | **Verdict** |
|---|---:|---|---|---|---|---:|---:|---:|---|
| `power washing` | **880** | HIGH | $0.58–14.31 | none | **Power Washing** | 4 | 3 | 4 | **ADD — PHRASE, staged** |
| `pressure washing` | **480** | HIGH | $0.30–10.77 | none | **Pressure Washing** | 4 | 3 | 4 | **ADD — PHRASE, staged** |
| `power washing near me` | 260 | HIGH | $10.90–28.32 | Power Washing Near Me | **Power Washing** | 5 | 1 | 4 | **KEEP — CORE** |
| `power washing company near me` | *(260 bucket)* | HIGH | $10.90–28.32 | Power Washing Company Near Me | **Power Washing** | 5 | 0 | 4 | **CONSOLIDATE** |
| `pressure washing services near me` | *(260 bucket)* | HIGH | $10.90–28.32 | none | **do not add** | 5 | 0 | 4 | **REMOVE — same bucket as `power washing near me`** |
| `power washing service` | 140 | LOW | $11.55–23.34 | dormant | **Power Washing** | 5 | 1 | 4 | **ADD** (+131% trend, comp index 13) |
| `pressure washing service` | *(140 bucket)* | LOW | $11.55–23.34 | none | **do not add** | 5 | 1 | 4 | **REMOVE — same bucket** |
| `pressure washing near me` | 90 | MEDIUM | $8.75–24.66 | **none** | **Pressure Washing** | 5 | 1 | 5 | **ADD — CORE gap** |
| `house washing near me` | 40 | MEDIUM | $10.46–24.75 | dormant | **House Washing** | 5 | 0 | 5 | **ADD** |
| `power washing services near me` | 30 | HIGH | $10.62–28.70 | both campaigns | **Power Washing** | 5 | 0 | 4 | **KEEP, de-duplicate** |
| `residential pressure washing near me` | 20 | LOW | no data | Residential PW Near Me | **Pressure Washing** | 5 | 0 | 5 | **CONSOLIDATE** |
| `pressure washing company near me` | *(20 bucket)* | MEDIUM | no data | none | **do not add** | 5 | 0 | 4 | **REMOVE — same bucket** |
| `house pressure washing near me` | 20 | HIGH | $13.49–32.86 | none | **House Washing** | 5 | 0 | 5 | **ADD** |
| `house power washing near me` | *(20 bucket)* | HIGH | $13.49–32.86 | none | **House Washing** | 5 | 0 | 5 | **ADD** |
| `soft washing near me` | 10 | HIGH | $15.09–41.58 | dormant | **Soft Washing** | 5 | 0 | 5 | **ADD — low volume** |
| `soft house washing near me` | *(10 bucket)* | HIGH | no data | Soft House Washing | **Soft Washing** | 5 | 0 | 5 | **KEEP** |
| `driveway pressure washing near me` | 10 | — | no data | Driveway PW Near Me | **Driveway** | 5 | 1 | 5 | **KEEP — low volume** |
| `driveway power washing near me` | *(10 bucket)* | — | no data | none | **Driveway** | 5 | 1 | 5 | **ADD** |
| `exterior house washing near me` | *(10 bucket)* | HIGH | no data | none | **House Washing** | 5 | 0 | 5 | **ADD** |
| `patio power washing near me` | 10 | MEDIUM | no data | none | **Patio** | 5 | 1 | 3 | **ADD** |
| `patio pressure washing near me` | 0 | — | no data | Patio PW Near Me | **Patio** | 5 | 1 | 3 | **KEEP — no reportable volume** |
| `concrete pressure washing near me` | *(0 bucket)* | — | no data | none | **Patio** | 5 | 1 | 3 | **ADD — no reportable volume** |
| `power washing quote` | 10 | LOW | no data | none | **do not add** | 4 | 0 | 4 | **STAGE — low volume** |
| `pressure washing estimate` | 10 | MEDIUM | no data | none | **do not add** | 3 | 0 | 2 | **REMOVE — the "estimate" token pulls cost research** |

**Head terms re-verified.** `power washing` and `pressure washing` + Long Island return **100%
local service providers** — Island Wide, Pressure Wash Long Island, Cleanfellas, McMorris,
Rolling Suds, Super Clean Machine. Zero equipment, retail or DIY. **Bare `pressure washer` and
`power washer` return 100% equipment retail** (Ace, Tractor Supply, Lowe's, Harbor Freight,
Consumer Reports) and are **NOT used as positive keywords**. The distinguishing token is
grammatical: *washing* is the service, *washer* is the machine. The existing 132-per-campaign
fence already blocks sale/rental/parts/repair/brands/DIY/jobs.

**Coverage: 1,960 of 1,980 = 98.99%** across 11 core texts, with the remaining 20/mo in the three
existing micro groups.

---

## 7. Final cross-negative strategy — phased, not all at once

| Layer | Criteria | Routing benefit | Blocking risk | Maintenance | Required at launch? |
|---|---:|---|---|---|---|
| **1 — Sibling EXACT mirror** | **95** | Enforces Walter's ownership rule; prevents the six new groups stealing each other's queries | **ZERO** — negative EXACT blocks only the literal text, and every text has exactly one owner | Low — static | **YES** |
| **2 — Historical rogue-query EXACT** | **20** | Fixes 18 specific queries Google routed wrongly | Zero | Medium — grows with search terms | **NO — DEFER** |
| **3 — Modifier PHRASE** | **12** | Family-level power/pressure/house/soft fences | Low — 23 of 35 candidates rejected for self-blocking | Low | **YES** |

**Deploy 107 at launch (Layers 1 + 3). Defer the 20 in Layer 2.**

The reasoning is specific, not general caution: **every one of the 20 Layer-2 queries was
mis-routed by an ad group that is being retired.** `powerwash cost` went to House Pressure
Washing Estimate; `power wash near me` went to Residential Pressure Washing Near Me. Once those
containers are paused, the new structure may route those queries correctly with no help at all.
Adding 20 negatives to pre-empt a problem the restructure may already solve is
over-engineering — and each one is a criterion someone must maintain forever.

**Re-evaluate Layer 2 after 14 days of real routing data.**

**More negatives do not equal better routing.** The prior matrix proved the hard limit:
**negative keywords do not match close variants; positive keywords do.** An EXACT negative blocks
only the literal string, so an unseen close variant slips past regardless of how many criteria
exist. **Residual close-variant risk is permanent and is managed by continuous search-term
review, not by pre-loading criteria.**

Safeguards preserved: ad-group level only · universal negatives stay separate at campaign level ·
no routing negative before its owner group is live and verified · no owner keyword blocks itself
· no approved service-intent query removed.

---

## 8. Final CPC amount and timing

# $15.00, applied to BOTH campaigns, now.

| Question | Answer |
|---|---|
| Apply $12 now to both? | **No — revised to $15.** Identical measured demand coverage (98.2%), 25% more Ad Rank headroom for an account with QS 1–5. |
| Wait for the single-campaign structure? | **No.** Restructuring is 3–5 weeks; the account pays ~$29.44/click meanwhile. |
| Use an interim ceiling while restructuring? | **$15 IS the interim ceiling.** Symmetric on both campaigns so no Ad Rank asymmetry is created. |
| Should the surviving campaign use $12 or $15? | **$15 first.** Step to $12 only if delivery holds 10 serving days — and note the head terms ($0.58–$14.31 and $0.30–$10.77) will pull blended CPC down naturally once live, which may make a second cut unnecessary. |
| Financial risk of waiting | ~$29.44 × ~1 click/serving day ≈ **$150–$300 per 10 serving days** of avoidable overspend. |
| Rank/delivery risk of acting now | **Real.** Lost IS to rank is already 49.12% on campaign A. A 49% ceiling cut will raise that. Mitigated by the six stop conditions and a two-mutation rollback. |

**Symmetric on both campaigns is non-negotiable** while two campaigns exist — changing one
creates the Ad Rank asymmetry that invalidated PLAN-R3A.

---

## 9. Final measurement strategy

**Fresh-read, all four `customer_conversion_goal` rows are `biddable: FALSE`:**
PHONE_CALL_LEAD/WEBSITE · PHONE_CALL_LEAD/CALL_FROM_ADS · SUBMIT_LEAD_FORM/WEBSITE ·
GET_DIRECTIONS/GOOGLE_HOSTED. All four conversion actions therefore read
`include_in_conversions_metric: FALSE`. Tag snippets: form 4, website call 1, call asset 0,
directions 0. Counting ONE_PER_CLICK on the three lead actions; 90/30/30-day click windows.

**The intended lead actions CANNOT populate the standard Conversions column today.**

**And the fix is API-mutable — verified this session.** `CustomerConversionGoalService` exists,
`CustomerConversionGoal.biddable` is a writable field, and `CustomerConversionGoalOperation`
supports `update` with an `update_mask`. **Three mutations**, setting the three lead categories
to `biddable: true` and deliberately leaving GET_DIRECTIONS `false`.

**Zero delivery risk:** both campaigns override with campaign-level goals where those three
categories are already biddable, so bidding does not change. Only what the Conversions column
counts changes.

### Ranked measurement actions

| # | Action | Type | Blocks |
|---:|---|---|---|
| 1 | **Set the 3 lead `customer_conversion_goal` categories biddable** | **3 API mutations, zero delivery risk** | Every CPL/CVR judgement |
| 2 | Resolve foreign tag `AW-17878095007` on all 6 offer pages | website / owner | Signal leakage to an unknown account |
| 3 | Check the ClickCease integration — 0 `IP_BLOCK` criteria synced | third-party config | Traffic-quality protection |
| 4 | Controlled form test | **BLOCKED** — PRESENCE targeting means a real GCLID needs a click from Long Island | End-to-end proof |
| 5 | Controlled call test | **BLOCKED** — rings the client's real line | Call path proof |

### Separating the diagnoses — as precisely as the evidence allows

| Hypothesis | Verdict |
|---|---|
| **No real leads** | **MOST LIKELY.** WhatConverts is an independent source and reads zero. |
| Leads not attributed | Possible but unevidenced — GCLID and UTMs verified persisting. |
| Conversion events not counted | **CONFIRMED as a reporting defect** — but `all_conversions` is also 0.00, so nothing was recorded either. |
| Conversion actions not biddable | **CONFIRMED at account level.** |
| Phone calls not tracked | **Untestable — no call has ever occurred.** 88 call impressions, 0 clicks, 0 `call_view` rows. |
| Forms not firing | **UNKNOWN** — requires the blocked test. The tag demonstrably fires site-wide (16 in `All Converters`). |
| Unanswered calls | **Not applicable** — there have been no calls. |

> **USER-SUPPLIED WHATCONVERTS RECORDS REVIEWED — ZERO CONFIRMED RELEVANT POWER WASHING OR
> PRESSURE WASHING LEADS IN THE SUPPLIED ROWS.**

---

## 10. Final landing-page strategy

| # | Issue | Evidence | CVR effect | Confidence | Pages | Fix before enabling new groups? |
|---|---|---|---|---|---|---|
| **P0** | Browser title reads **"Softwind Landscape & Masonry"** — the scope-fenced sibling brand | Real-browser render, desktop + mobile | **HIGH** | HIGH | **all 6 offer pages** | **YES** |
| **P0** | Foreign tag `AW-17878095007` | Network requests on every paid view | MEDIUM (signal, not CVR) | HIGH | 6 offer + 2 main-site | **YES** |
| **P1** | H1 locked to "Islip, West Islip & Dix Hills" while campaigns target **80 places** | Geo criteria vs page H1 | **HIGH** | MEDIUM | 6 of 8 | **YES — before head terms** |
| **P1** | "Offer Ends" countdown with no dated offer | On all 6 offer pages | MEDIUM | HIGH | 6 | **YES** |
| **P2** | No reviews, rating, years, licence or insurance | Every competitor carries at least one | **HIGH** | MEDIUM | all | No — blocked on client confirmation |
| **P3** | `/patio-power-washing/` title says "Power", H1 says "Pressure" | Render | LOW | HIGH | 1 | No |

**Verified as already correct:** HTTP 200 no redirects · approved tracked phone (631) 502-7946 in
tel: and body on all six · GCLID and all four UTMs persist · 5-field Gravity Form · mobile/desktop
parity · GA4, GTM, WhatConverts, ClickCease all loading.

**Location wording recommendation: "Long Island" as the H1 anchor, with "Serving Nassau and
Suffolk County" as the supporting line.** Both are verifiable from the 80 live
`geo_target_constant` canonical names — every one is a New York location in Nassau or Suffolk.
**Do not use dynamic location insertion** (no verified per-town content, and it risks naming a
town the client does not serve). **Do not keep the three-city wording** — it names 3 of 80.
**Do not build intent-specific city pages** — no city keyword has reportable demand.

---

## 11. Final RSA strategy

| Ad group | Current RSAs | Decision |
|---|---|---|
| **Power Washing** (from `202870585390`) | 2 ENABLED, Ad Strength EXCELLENT, **ad relevance BELOW_AVERAGE**, 9 of 15 headlines name 3 hamlets | **Replace both** — create 2 new paused |
| **Pressure Washing** | none — new group | **Create 2 paused** |
| **House Washing** | none — new group | **Create 2 paused** |
| **Soft / Driveway / Patio** | 2 each, APPROVED, GOOD/EXCELLENT, zero impressions | **Keep** — no evidence to act on |

**RSA 1** — exact service intent, local relevance, free quote, direct response.
**RSA 2** — exterior transformation, surface-specific methods, trust and process, free estimate.

Copy is **not** written here; it is written at build time against the as-built ad groups, then
validated for the 30/90/15 character limits and against the client's `unverified_claims_do_not_use`
list. **No filler to reach 15 headlines. Ad Strength is not the objective** — the current ads
score EXCELLENT while carrying BELOW_AVERAGE ad relevance, which is exactly why it is the wrong
target.

---

## 12. Invalid-click and traffic-quality strategy

**Concentrated in mobile — completely.** 73 invalid on mobile, **0 on desktop**, across the
account's entire life. Campaign-skewed 62/11 toward campaign A. Day-concentrated with spikes on
08-31 (13), 08-24 (12), 08-28 (10).

**These are Google-filtered and credited. They are NOT counted as billable performance failures**
and do not appear in the $595.87.

**Recommended action: none in Google Ads.** A mobile bid modifier would remove 14 of 18 valid
clicks and 71% of spend to solve a problem Google is already solving. **The one action worth
taking is outside Google Ads:** ask the client to check the ClickCease integration, which loads
on every page yet syncs **zero** `IP_BLOCK` criteria into either campaign. Do not remove
ClickCease.

**One charged pattern did occur and was self-correcting:** on 2026-08-31, five clicks on
`power washing services` from one postal code were charged $146.60, then **four were reversed and
$117.28 credited back**. That is the system working, and it is the strongest evidence for the
mobile traffic-quality concern.

---

## 13. Audience and demographic decision

**Do not exclude women. Do not exclude Unknown gender.** Verified again: **zero** GENDER,
AGE_RANGE and INCOME_RANGE criteria exist. Nothing to undo. The prior evidence stands — women
17.95% CTR at $25.63 CPC versus men 9.22% at $32.46.

**PLAN-R9 (audience observations) is a reporting enhancement, not CVR recovery. DEFER.** Twelve
criteria at 0% modifiers produce zero leads by design. With 18 lifetime clicks the observation
data would be uninterpretable for months. Revisit once the consolidated structure has volume.

---

## 14. Final recommended account architecture

| | |
|---|---|
| **Campaigns** | **1** |
| **Surviving campaign ID** | **`24103511039`** |
| **Final campaign name** | **"Power Washing"** — unchanged. Do not rename; do not spend a mutation correcting "Preassure Washing" on a campaign being retired. |
| **Ad groups** | **6** |
| **Structure type** | **SINGLE-INTENT — not literal SKAG** |
| **CPC ceiling** | **$15.00**, symmetric on both campaigns now; step to $12 only on evidence |
| **Audiences** | none — deferred |
| **Demographics** | none — no exclusions, ever |

| # | Ad group | Phrase | Exact | Demand | Landing page |
|---|---|---|---|---:|---|
| 1 | **Power Washing** | `power washing` · `power washing near me` · `power washing service` | `power washing near me` · `power washing service` · `power washing services near me` · `power washing company near me` | **1,310** | `/power-washing-services-islip-west-islip-dix-hills/` |
| 2 | **Pressure Washing** | `pressure washing` · `pressure washing near me` | `pressure washing near me` · `residential pressure washing near me` | **590** | `/residential-pressure-washing/` |
| 3 | **House Washing** | `house washing near me` | `house washing near me` · `house pressure washing near me` · `house power washing near me` · `exterior house washing near me` | **60** | `/house-washing-company/` |
| 4 | **Soft Washing** *(exists)* | `soft house washing near me` | `soft house washing near me` · `soft washing near me` | 20 | `/soft-house-washing/` |
| 5 | **Driveway Pressure Washing** *(exists)* | `driveway pressure washing near me` | `driveway pressure washing near me` · `driveway power washing near me` | 10 | `/driveway-pressure-washing/` |
| 6 | **Patio Pressure Washing** *(exists)* | `patio pressure washing near me` | `patio pressure washing near me` · `patio power washing near me` · `concrete pressure washing near me` | 0 | `/patio-power-washing/` |

**Exact and Phrase only. No Broad Match. 1,960 of 1,980 = 98.99% coverage.**

**Retirement order, last to first:** `198082078783` → `198082079423` → `198082078983` →
`202870585430` → `202870585590` → the three city SKAGs → **campaign `24145053510` LAST**.

**Asset strategy:** parity is already complete (4 sitelinks, 4 callouts, 1 snippet, 1 call asset
per campaign). Remaining gaps — image assets, business-name asset — are **blocked on
client-supplied rights-cleared photographs**. The call asset stops at 17:00 while campaigns run
to 18:00, in the account's cheapest hour ($22.12); blocked on confirming the phone is answered
17:00–18:00 Mon–Fri.

---

## 15. Status of every plan

| Plan | Status | Reason |
|---|---|---|
| **PLAN-R1** — measurement | **REVISE** | Currently 0 actions / READ-ONLY. The conversion-goal fix is **API-mutable** and must become an executable 3-mutation plan. The blocked test components stay separate. |
| **PLAN-R2** — search-term negatives | **KEEP** | 8 mutations, adds-before-removes ordering, zero collisions. Still correct. |
| **PLAN-R3** — $22 both | **VOID** | Superseded. In the do-not-honour registry. |
| **PLAN-R3A** — $12 one campaign | **VOID** | Superseded. Invalid control. In the registry. |
| **PLAN-R3B** — $12 both | **REVISE → SUPERSEDE** | Structure and symmetry are right; **the amount changes to $15**. Needs a successor plan and a new fingerprint. `BC0A5A7258E2` must not be approved. |
| **PLAN-R4** — one-campaign architecture | **KEEP WITH REVISION** | Conclusion holds. Update ad-group count from 3 core to the 6-group single-intent structure. |
| **PLAN-R5** — replacement RSAs | **KEEP WITH REVISION** | Right ad group; copy re-drafted against the as-built groups. |
| **PLAN-R6** — new ad groups and keywords | **REVISE** | Expand from 3 SKAGs to the 6-group single-intent structure and 19 texts. |
| **PLAN-R7** — landing pages | **KEEP** | P0 title and foreign tag; P1 city lock and countdown. Website track. |
| **PLAN-R8** — assets | **CLOSED** | Parity completed by owner action. Remaining items blocked on client inputs. |
| **PLAN-R9** — audience observations | **DEFER** | Reporting enhancement; produces no leads. |
| **PLAN-R10** — enablement | **DEFER** | Provisional placeholders; regenerate after R6 creates real IDs. |
| **PLAN-R11** — retirement | **DEFER** | Blocked until replacements are live and verified. |
| **PLAN-R12** — budget hold | **KEEP** | Lost IS to budget 3.10% / 7.50%. Budget is not the constraint. |
| **Strict SKAG matrix (127)** | **KEEP WITH REVISION** | Deploy **107 at launch** (Layers 1 + 3); **defer the 20 Layer-2 rogue-query negatives** for 14 days of routing evidence. |

---

## 16. The single next action

# Repair the conversion-goal configuration.

Set the three lead categories in `customer_conversion_goal` to `biddable: true` —
PHONE_CALL_LEAD/WEBSITE, PHONE_CALL_LEAD/CALL_FROM_ADS, SUBMIT_LEAD_FORM/WEBSITE. Leave
GET_DIRECTIONS `false`.

| | |
|---|---|
| **Why first** | It is the only action that makes **every other action measurable**. Today, if a lead arrived tomorrow, the account could not count it — and the recovery would proceed blind. Cutting CPC, rebuilding structure and fixing pages all produce results nobody can trust until this is done. |
| **Expected impact** | **Zero leads directly.** It creates no demand. It makes leads *visible*. That is why it is first, not why it is valuable. |
| **Confidence** | **HIGH.** The defect is confirmed by fresh read on all four goals and all four actions. |
| **Risk** | **VERY LOW.** Both campaigns override with campaign-level goals where these categories are already biddable, so **bidding does not change** — only what the Conversions column counts. |
| **Dependency** | **None.** Not blocked by PRESENCE targeting, client inputs, or a developer. |
| **Existing plan?** | **PLAN-R1** covers the finding but is written as a zero-mutation investigation. |
| **Still valid?** | The **finding** is valid and re-confirmed. The **plan form** is not — it emits no approval command. |
| **New plan required?** | **YES.** A new executable plan with exactly **3 mutations** on `customer_conversion_goal`, field mask `biddable`, and its own fingerprint. **Not created in this step.** |

**Second, once that is approved — but not now:** the $15 symmetric ceiling. They do not compete;
the measurement fix is zero-mutation on a different resource and can be approved in the same
sitting. But if only one moves first, it must be the one that makes the other readable.

---

## 17–18. Confirmations

**No fingerprint was created in this step.** The manifest is unchanged at 14 plans, 3 void
fingerprints, 20/20 reconciliation assertions passing. `BC0A5A7258E2` (PLAN-R3B) exists but is
**not approved and is now marked for supersession** at $15.

**Zero external changes.** Fresh re-read confirms both ceilings `30000000`, both TARGET_SPEND,
both ENABLED, names unchanged, 30 ad groups, 214 keywords, 264 campaign negatives, **0 ad-group
negatives**, 0 audiences, 0 demographic criteria. No form submitted, no call placed.

---

**FINAL SENIOR STRATEGY RED-TEAM COMPLETE — ZERO EXTERNAL CHANGES MADE**
