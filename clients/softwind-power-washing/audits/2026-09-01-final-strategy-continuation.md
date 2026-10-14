# SOFTWIND POWER WASHING — SEPTEMBER 1 FINAL STRATEGY CONTINUATION

**Generated:** 2026-09-01 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
**Zero external changes. No fingerprint created. This is not approval for any plan.**

**Continuation of** `2026-08-31-final-senior-strategy-red-team.md`, which is **complete and is
not rewritten, overwritten or superseded by this file.** This file adds the September 1 state,
separates August from September, and re-tests the single next action.

**Snapshot timestamps (account local, America/New_York):**
configuration + drift `2026-09-01T14:53:38-04:00` · confirming metric read `2026-09-01T15:01:18-04:00`.
Evidence: `snapshots/sept1-continuation-2026-09-01T145338.json`.

---

> ## ⚠️ CORRECTION NOTICE — added 2026-09-01 18:45 ET, after this file was written
>
> **Section 12 and Section 17 of this file are SUPERSEDED.** The single next action selected here
> — setting the three lead `customer_conversion_goal` categories to `biddable: true` — was
> **wrong**, and is retired. A fresh read of the complete four-layer goal hierarchy proved that
> **both campaigns are `goal_config_level: CAMPAIGN`** and already carry the three lead goals as
> `biddable: true` at campaign level, that all four conversion actions read `primary_for_goal:
> true`, and that `include_in_conversions_metric` is a **deprecated, immutable** field this file
> misinterpreted. The customer-goal mutation would not have affected either campaign.
>
> **Superseded by:** [`2026-09-01-conversion-measurement-decision.md`](2026-09-01-conversion-measurement-decision.md)
> — verdict **D, no goal-configuration defect**; next action is **PLAN-R1B**, a controlled
> instrumented form-conversion test, fingerprint `B7AD76CB16F8`, NOT APPROVED.
>
> **Everything else in this file — the August results, the September 1 partial results, the
> campaign-count, architecture, keyword, cross-negative, CPC, landing-page, RSA and audience
> decisions, and the plan-status reconciliation — stands unchanged.**


## 1. Was the August 31 final red-team memo complete?

# YES — COMPLETE. Not rewritten.

| Check | Result |
|---|---|
| File exists | **YES** — `audits/2026-08-31-final-senior-strategy-red-team.md` |
| Non-empty | **YES** — 31,089 bytes / **493 lines** |
| Markdown structure readable | **YES** — all tables and headings parse |
| All expected sections present | **YES** — §1 through §18, no gaps in the numbering |
| Conclusion complete | **YES** — §16 "The single next action" is fully written, with all ten required attributes |
| Single next action present | **YES** — repair the conversion-goal configuration |
| Ending safety statement present | **YES** — `FINAL SENIOR STRATEGY RED-TEAM COMPLETE — ZERO EXTERNAL CHANGES MADE` |
| Truncated by the session limit? | **NO** — the file terminates on its own closing line, not mid-sentence, mid-table or mid-section |

**It is used here as the primary decision source.** This file is a **status addendum**, not a
rebuild. No section of the August 31 audit was re-run.

---

## 2. Fresh September 1 account status

### Identity gate — PASS

| Field | Observed | Required | Result |
|---|---|---|---|
| `customer.descriptive_name` | **Softwind Power Washing - Live** | exact | **PASS** |
| `customer.id` | **1521725229** | exact 10-digit child | **PASS** |
| Formatted | 152-172-5229 | — | PASS |
| `customer.manager` | **false** | false | **PASS** |
| `customer.test_account` | **false** | false | **PASS** |
| `customer.status` | **ENABLED** | — | PASS |
| Currency | **USD** | — | PASS |
| Time zone | **America/New_York** | — | PASS |
| `- live` marker | present | present | PASS |
| Account-local date | **2026-09-01** | — | — |
| Account-local time | **14:53:38 → 15:01:18** | — | — |
| Auto-tagging | true | — | — |
| Optimization score | 0.881978 *(not an objective)* | — | — |

**Work order re-validated** against `client.yaml`: slug `softwind-power-washing`, service
**Power Washing**, vertical `similar-local-service`, `scope_approval.approved: true`,
approver Walter Correa, **mode `read`**. Matches this session's READ + DRAFT ONLY mode.

> **One work-order field is now expired.** `work_order.month_end_objective` carries
> `month_end_date: "2026-08-31"` and `spend_goal_usd: 2500`. That objective closed with August.
> It is **not** used as a September decision input anywhere in this file. Updating or retiring
> that block is a Walter decision; it does not block the next action.

### Limited fresh drift snapshot — both campaigns

| Surface | `24103511039` | `24145053510` |
|---|---|---|
| **Current campaign name** | **Power Washing** | **Pressure Washing** ← *renamed by owner today* |
| Status / serving | ENABLED / **SERVING** | ENABLED / **SERVING** |
| Primary status | **ELIGIBLE** | **LEARNING** (`BIDDING_STRATEGY_LEARNING`) |
| Channel | SEARCH | SEARCH |
| Daily budget | **$41.50** (budget `15764226923`, STANDARD) | **$41.11** (budget `15802443075`, STANDARD) |
| Bidding strategy | TARGET_SPEND / ENABLED | TARGET_SPEND / **LEARNING_SETTING_CHANGE** |
| **CPC ceiling** | **30000000 micros = $30.00** | **30000000 micros = $30.00** |
| Biddable campaign conversion goals | PHONE_CALL_LEAD/WEBSITE · PHONE_CALL_LEAD/CALL_FROM_ADS · SUBMIT_LEAD_FORM/WEBSITE | identical |
| Positive locations | **80** | **80** |
| Location option | **PRESENCE / PRESENCE** | **PRESENCE / PRESENCE** |
| **Connecticut exclusion** | **present** — 1 negative location `21139` | **present** — 1 negative location `21139` |
| Ad schedule | Mon–Sat **08:00–18:00** (6 rows) | Mon–Sat **08:00–18:00** (6 rows) |
| Search Partners | **off** | **off** |
| Display Network | **off** | **off** |
| AI Max | **off** | **off** |
| Asset automation | TEXT + FINAL_URL_EXPANSION **OPTED_OUT** | TEXT + FINAL_URL_EXPANSION **OPTED_OUT** |
| Ad groups (non-removed / ENABLED) | 15 / **6** | 15 / **6** |
| Enabled keywords (servable) | **9** | **12** |
| Enabled RSAs (in enabled groups) | **12** | **12** |
| Campaign negative keywords | **132** | **132** |
| **Ad-group negative keywords** | **0** | **0** |
| Campaign assets | 4 SITELINK · 4 CALLOUT · 1 SNIPPET · 1 CALL = **10** | 4 SITELINK · 4 CALLOUT · 1 SNIPPET · 1 CALL = **10** |
| Serving final URLs | 1 — `/power-washing-services-islip-west-islip-dix-hills/` | 6 — driveway, house-pressure-estimate, patio-power, islip offer, residential-pressure, soft-house |
| Tracking template / URL suffix | empty / empty | empty / empty |

**Account totals re-confirmed live:** 30 ad groups (12 enabled) · 214 keywords · 54 ads ·
264 campaign negatives · **0 ad-group negatives** · 20 campaign assets · **0 audiences** ·
**0 GENDER / AGE_RANGE / INCOME_RANGE criteria** · **0 IP_BLOCK criteria** · **0 `call_view` rows**.

### Drift classification — 41 surfaces checked, 2 differences, both attributed

| # | Difference | Classification | Attribution — proven, not inferred |
|---|---|---|---|
| 1 | `24145053510` name: `Power Washing #2` → `Preassure Washing` → **`Pressure Washing`** | **MANUAL OWNER CHANGE** | `change_event` two rows, both `client_type: GOOGLE_ADS_WEB_CLIENT`, user `access@greenmarketingfl.com`: **2026-08-31 18:16:07** and **2026-09-01 14:21:43** (32 minutes before this snapshot). Claude's writes appear as `GOOGLE_ADS_API`; these are not. |
| 2 | `campaign_asset` links 16 → 20 | **MANUAL OWNER CHANGE — already documented** | The four asset links the owner added on 2026-08-31 at ~10:52. Already recorded as PLAN-R8 "closed by owner". Appears here only because the drift baseline is the 10:21 forensic snapshot, which predates it. |

**Also attributable, inside the window, not Claude:** `2026-08-31 09:39:41`
`GOOGLE_ADS_WEB_CLIENT` — campaign-budget `amount_micros` update on budget `15764226923`
(campaign A). Owner action, already reflected in the August 31 baseline.

**No change attributable to Claude in this window.** The only `GOOGLE_ADS_API` rows in the
change log are the 2026-08-30 08:42 campaign-negative CREATEs from the previously approved and
executed negatives rollout.

- **Configuration drift:** 1 (campaign name, owner)
- **Normal metric drift:** impression-share restatement (below), Google invalid-click filtering
- **Google invalid-click adjustments:** ongoing and material (below)
- **Changes made by prior approved plans:** none in this window

---

## 3. FINAL AUGUST RESULTS — 2026-08-01 to 2026-08-31

> **CURRENTLY SETTLED AS OF 2026-09-01T15:01:18-04:00.** The cost, impression and click figures
> have not moved since the August 31 20:51 read, so August money appears settled. The
> **impression-share** metrics *have* been restated (below), and Google is still actively
> filtering clicks on recent days, so these are the best current figures — **not permanently
> final**.

| Metric | `24103511039` Power Washing | `24145053510` Pressure Washing | **COMBINED** |
|---|---:|---:|---:|
| **Final August spend** | **$403.09** | **$192.78** | **$595.87** |
| Impressions | 216 | 46 | **262** |
| **Raw clicks** | 74 | 17 | **91** |
| **Valid billable clicks** | **12** | **6** | **18** |
| **Invalid clicks** | **62** | **11** | **73** |
| **Invalid-click rate** | **83.78%** | **64.71%** | **80.22%** |
| Credits / retroactive cost adjustments | Google filtered and credited all 62 invalid clicks; they are **not** inside the $403.09 | same, 11 clicks | 73 clicks credited |
| **CTR on valid billable clicks** | **5.56%** | **13.04%** | **6.87%** |
| **Average valid CPC** | **$33.59** | **$32.13** | **$33.10** |
| **Conversions** | **0.00** | **0.00** | **0.00** |
| **All conversions** | **0.00** | **0.00** | **0.00** |
| Conversion rate | 0.00% | 0.00% | 0.00% |
| Search Impression Share | **48.56%** | **65.85%** | — |
| Search Lost IS — **rank** | **47.74%** | **26.83%** | — |
| Search Lost IS — **budget** | **3.70%** | **7.32%** | — |
| Absolute top IS | 26.34% | 43.90% | — |

**Restatement since the August 31 memo (normal metric drift, not configuration drift):**

| Metric | Memo, 2026-08-31 | Settled, 2026-09-01 | Delta |
|---|---:|---:|---|
| A — Search IS | 47.79% | **48.56%** | +0.77 pt |
| A — Lost IS rank | 49.12% | **47.74%** | −1.38 pt |
| A — Lost IS budget | 3.10% | **3.70%** | +0.60 pt |
| B — Lost IS budget | 7.50% | **7.32%** | −0.18 pt |
| Spend, clicks, impressions, conversions | — | **identical** | **no change** |

**Two August delivery facts that were not isolated before:**

1. **2026-08-30 was a completely dark day.** `segments.date = '2026-08-30'` returns **zero rows**
   for both campaigns. Zero impressions and zero cost across the whole account for a full
   Sunday. (Saturday is a scheduled serving day; Sunday is not in the ad schedule — Mon–Sat
   08:00–18:00 — so this is the schedule working as configured, not an outage.)
2. **2026-08-31 cost campaign A $0.00.** Settled: campaign A took 15 impressions, **0 valid
   clicks, 9 invalid clicks, $0.00**. Campaign B took 3 impressions, 1 valid click at **$29.32**,
   4 invalid. The month's last serving day produced **one** billable click across the account.

**Device concentration re-confirmed for August:**

| Device | Impressions | Valid clicks | Invalid clicks | Cost |
|---|---:|---:|---:|---:|
| **MOBILE** | 175 | 14 | **73** | $422.11 |
| **DESKTOP** | 86 | 4 | **0** | $173.76 |
| TABLET | 1 | 0 | 0 | $0.00 |

**Every invalid click in August was mobile. Desktop produced none.** Unchanged from the memo.

### WhatConverts — August

> **USER-SUPPLIED WHATCONVERTS RECORDS REVIEWED — ZERO CONFIRMED RELEVANT POWER WASHING OR
> PRESSURE WASHING LEADS IN THE SUPPLIED ROWS.**

WhatConverts is an **independent source** and it agrees with the Google Ads Conversions column at
zero. It is available and it was reviewed. It is not reported as unavailable.

---

## 4. SEPTEMBER 1 PARTIAL RESULTS — 2026-09-01 00:00 through 15:01:18 ET

**Reported separately. Not combined with August anywhere in this file.**

| Metric | `24103511039` Power Washing | `24145053510` Pressure Washing | **COMBINED** |
|---|---:|---:|---:|
| **Spend** | **$0.00** | **$0.00** | **$0.00** |
| Impressions | **12** | **0** | **12** |
| **Raw clicks** | 10 | 1 | **11** |
| **Valid clicks** | **0** | **0** | **0** |
| **Invalid clicks** | **10** | **1** | **11** |
| Invalid-click rate | **100%** | **100%** | **100%** |
| CTR (valid) | 0.00% | 0.00% | **0.00%** |
| Average CPC | **n/a — no billable click** | n/a | **n/a** |
| Conversions / all conversions | 0.00 / 0.00 | 0.00 / 0.00 | **0.00 / 0.00** |
| Search IS / Lost IS | not yet computed for the partial day (0.0000) | not computed | — |

**Hourly delivery, campaign A** (campaign B had none): 08:00 — 1 impression · 09:00 — 1 ·
11:00 — 6 · 13:00 — 5. Nothing after 14:00 at read time.

**Device, September 1:** MOBILE 7 impressions / **10 invalid clicks** / $0.00 · DESKTOP 5
impressions / 0 clicks / $0.00. **The invalid clicks are again 100% mobile.**

**Impressions are being restated downward inside the day.** Campaign A read **16** impressions at
14:53:38 and **12** at 15:01:18, eight minutes later. Google is actively filtering this day's
traffic as it is recorded. Every September 1 figure above is provisional.

**September 1 search terms** (10 rows, all zero clicks and $0.00):

| Term | Campaign | Ad group | Match | Impr |
|---|---|---|---|---:|
| `power washing services near me` | A | Power Washing Services Near Me | EXACT | 2 |
| `power washing near me` | A | Power Washing Near Me | EXACT | 1 |
| `pressure washing services near me` | A | Power Washing Near Me | NEAR_EXACT | 2 |
| `power washing companies near me` | A | Power Washing Services Near Me | NEAR_EXACT | 2 |
| `power washing` | A | Power Washing Near Me | NEAR_EXACT | 1 |
| `pressure washing service near me` | A | Power Washing Near Me | NEAR_EXACT | 1 |
| `pressure washing service near me` | A | Power Washing Company Near Me | NEAR_EXACT | 1 |
| `exterior pressure washing near me` | A | Power Washing Near Me | NEAR_EXACT | 1 |
| `commercial pressure washing near me` | A | Power Washing Near Me | NEAR_EXACT | 1 |
| **`pressure washer near me`** | A | Power Washing Near Me | **NEAR_EXACT** | 1 |

**Campaign receiving the traffic: `24103511039` takes 12 of 12 impressions.** Campaign B took
none.

**Does current delivery reflect the same high-CPC pattern?** **It cannot be tested today.**
There were **zero billable clicks**, so there is no September 1 CPC to compare against the
$29.04–$33.59 August pattern. The `$30 ceiling functions as the price` finding is neither
confirmed nor refuted by September 1 — it is simply unobserved.

**Was any new lead recorded?** **No.** Zero conversions, zero all-conversions, zero `call_view`
rows across the entire retained log.

> **No trend conclusion is drawn from this partial first day.** One day with zero billable
> clicks is not evidence that delivery has structurally changed. What it *is* evidence of is
> stated narrowly below, and only where the observation is decisive on its own terms.

---

## 5. Findings that remain valid

Every substantive finding in the August 31 memo survives. Re-confirmed by fresh read today:

- **Zero recorded conversions on 18 valid clicks and $595.87 lifetime.** Re-confirmed.
- **The Conversions column is structurally zeroed.** Fresh read today: **all four**
  `customer_conversion_goal` rows `biddable: FALSE`; **all four** conversion actions
  `include_in_conversions_metric: FALSE`. Unchanged from 08-31.
- **The call path has never been exercised.** `call_view` returns **0 rows**.
- **The two campaigns are not independent.** Shared 80-location footprint, shared Connecticut
  exclusion, identical schedule, identical 132-negative fence, identical goals, identical asset
  loadout, **`Power Washing Services Near Me` still ENABLED in both campaigns**, and the shared
  Islip offer page still serving in both.
- **The $30 ceiling functioned as the price through 08-31.** Last five billable clicks:
  $29.91, $28.73, $29.57, $29.57, $29.04, $29.72, $29.32.
- **Google collapses power ↔ pressure into shared Planner buckets.** Unchanged.
- **Invalid clicks are ~100% mobile.** Re-confirmed for August and again for September 1.
- **No demographic exclusions exist and none is proposed.** Fresh read: 0 GENDER, 0 AGE_RANGE,
  0 INCOME_RANGE, 0 USER_LIST.
- **ClickCease syncs zero `IP_BLOCK` criteria.** Fresh read today: still **0**.
- **Landing-page findings P0–P3** stand as verified by real-browser render on 2026-08-31.
  **Not re-verified on 2026-09-01** — no configuration change invalidated them, and the
  prompt's instruction not to re-run completed work applies.

---

## 6. Findings that changed

### 6a. The owner renamed campaign `24145053510` to "Pressure Washing" — twice, and today

`Power Washing #2` → `Preassure Washing` (08-31 18:16) → **`Pressure Washing`** (09-01 14:21),
both from the Google Ads web UI by `access@greenmarketingfl.com`.

**The August 31 memo's statement "the names are unchanged, including the 'Preassure' misspelling"
is now out of date on both halves** — the name changed twice, and the misspelling was corrected.

**Does this change the one-campaign recommendation? No.** A rename is cosmetic. It creates none
of the independence a second campaign would require: the two campaigns still share the same 80
locations, the same schedule, the same 132 negatives, the same conversion goals, the same asset
set, a duplicated ad group, and — critically — **the same Keyword Planner demand buckets**.
The memo's Option 1 rejection rested on the fact that `power washing near me` and
`pressure washing services near me` are the **same 260/mo bucket**; a correctly-spelled campaign
name does not split a shared bucket.

> **Surfaced for Walter, not assumed either way.** Correcting the name of a campaign the plan
> recommends retiring may signal an intent to keep two campaigns. The evidence for consolidation
> is unchanged and I still recommend one campaign. If the rename reflects a deliberate decision
> to keep a separate Pressure Washing campaign, that is a business preference that overrides my
> technical recommendation and I need to hear it — it would change the architecture, the
> cross-negative design and the retirement order. It does **not** block the next action below.

### 6b. Zero billable clicks and $0.00 spend across the last two serving days

| Date | Impressions | Valid clicks | Invalid clicks | Cost |
|---|---:|---:|---:|---:|
| 2026-08-27 | 62 | 6 | 2 | $195.26 |
| 2026-08-28 | 19 | 2 | 10 | $59.14 |
| 2026-08-29 | 30 | 2 | 9 | $58.76 |
| 2026-08-30 | **0** | 0 | 0 | **$0.00** *(Sunday — outside the ad schedule)* |
| 2026-08-31 | 18 | **1** | 13 | **$29.32** |
| **2026-09-01** *(partial)* | **12** | **0** | **11** | **$0.00** |

**The financial bleed the $15 ceiling was designed to stop has, for the moment, stopped by
itself** — not because the ceiling changed, but because Google is filtering essentially all of
this account's recent clicks as invalid. Account spend over the last three calendar days is
**$29.32 total**.

### 6c. The invalid-click pattern crossed from "signal" to "delivery-shaping"

September 1 mobile: **10 raw clicks on 7 impressions — a raw CTR above 100%.** That is not human
behaviour, and it is not a marginal filtering rate; it is the whole of the day's click volume.
Combined with 08-31 (13 invalid, 1 valid), the last two serving days produced **24 invalid clicks
and 1 valid click**.

**This does not change the recommended action, which remains "none inside Google Ads."** Google
is filtering and crediting, the client is not paying for it, and a mobile bid modifier would
still remove most of the account's real traffic. **What it changes is the reliability of any
experiment run right now** — see §11.

### 6d. A genuine equipment-intent query reached the account through a close variant

`pressure washer near me` — the machine, not the service — served on September 1 in
`Power Washing Near Me` as a **NEAR_EXACT close variant**. 1 impression, 0 clicks, $0.00.

The August 31 memo established the grammatical fence (*washing* = service, *washer* = machine)
and stated that **negative keywords cannot control loose positive close variants.** This is the
first live instance of exactly that leak. It is a **PLAN-R2 candidate**, not an action today: one
impression, zero clicks, zero cost. It is recorded here so the next search-term review starts
from it. `commercial pressure washing near me` (outside verified residential scope) also served
via close variant on the same day and is a second PLAN-R2 candidate.

### 6e. August impression-share figures were restated

Quantified in §3. Directionally small, and it does not change any conclusion: campaign A still
loses roughly half its impression share to rank, and **Lost IS to budget remains negligible
(3.70% / 7.32%) — budget is still not the constraint.**

---

## 7. Final campaign-count decision

# ONE CAMPAIGN.

**Unchanged from the August 31 memo, and September 1 strengthens it.** Campaign
`24145053510` took **0 impressions** on September 1 while campaign `24103511039` took all 12. It
remains in `LEARNING` / `LEARNING_SETTING_CHANGE` fifteen days after launch, on 46 lifetime
impressions and 6 lifetime valid clicks. It has never been an independent unit and it is not
becoming one.

**Not two campaigns.** Separation requires mirrored cross-campaign negatives, and negativing
`pressure washing services near me` out of the Power campaign removes demand from the same
260/mo bucket `power washing near me` occupies. The head terms cannot be split at all.

**Not hybrid.** There is no qualifying second intent — same geography, budget objective,
conversion actions, schedule and landing-page path. Commercial is the only candidate, it is
outside verified scope, and there is no commercial landing page.

**A synonym does not justify a campaign. Neither does a name — including a correctly spelled one.**

---

## 8. Final architecture decision

**Unchanged from memo §14.**

| | |
|---|---|
| **Surviving campaign ID** | **`24103511039`** |
| **Final campaign name** | **"Power Washing"** — unchanged. Do not rename. Do not spend a mutation on the name of the campaign being retired. |
| **Final ad-group count** | **6** |
| **Structure type** | **SINGLE-INTENT — not literal SKAG** |
| CPC ceiling | **$15.00** symmetric — see §11 for the revised timing |
| Audiences | none — deferred |
| Demographics | none — no exclusions, ever |

| # | Canonical ad-group name | Phrase | Exact | Demand | Landing page |
|---|---|---|---|---:|---|
| 1 | **Power Washing** | `power washing` · `power washing near me` · `power washing service` | `power washing near me` · `power washing service` · `power washing services near me` · `power washing company near me` | **1,310** | `/power-washing-services-islip-west-islip-dix-hills/` |
| 2 | **Pressure Washing** | `pressure washing` · `pressure washing near me` | `pressure washing near me` · `residential pressure washing near me` | **590** | `/residential-pressure-washing/` |
| 3 | **House Washing** | `house washing near me` | `house washing near me` · `house pressure washing near me` · `house power washing near me` · `exterior house washing near me` | **60** | `/house-washing-company/` |
| 4 | **Soft Washing** *(exists)* | `soft house washing near me` | `soft house washing near me` · `soft washing near me` | 20 | `/soft-house-washing/` |
| 5 | **Driveway Pressure Washing** *(exists)* | `driveway pressure washing near me` | `driveway pressure washing near me` · `driveway power washing near me` | 10 | `/driveway-pressure-washing/` |
| 6 | **Patio Pressure Washing** *(exists)* | `patio pressure washing near me` | `patio pressure washing near me` · `patio power washing near me` · `concrete pressure washing near me` | 0 | `/patio-power-washing/` |

**Phrase and Exact only. No Broad Match.** 19 unique keyword texts, ~30 positive keyword objects.

**Why not literal SKAG:** the account takes roughly one valid click per serving day. Nineteen
literal SKAGs would give each ad group one click every twenty days, and Quality Score, ad rotation
and every optimisation signal operate at ad-group level. **You do not need an ad group to measure
a keyword** — `keyword_view` reports impressions, clicks, cost, CTR, average CPC and Quality Score
per keyword. Splitting buys ad differentiation and routing, not measurement, and the ad message
for `power washing`, `power washing near me` and `power washing service` is materially the same.

**Retirement order, last to first:** `198082078783` → `198082079423` → `198082078983` →
`202870585430` → `202870585590` → the three city SKAGs → **campaign `24145053510` LAST.**

---

## 9. Final BOFU keyword decision

**Unchanged from memo §6.** 19 canonical texts, **1,960 of 1,980 = 98.99%** of measured local
demand, Phrase + Exact only.

**Head terms re-verified 08-31, not re-run today:** `power washing` and `pressure washing` +
Long Island return **100% local service providers**. Bare `pressure washer` / `power washer`
return **100% equipment retail** and are **NOT used as positive keywords**. The distinguishing
token is grammatical: *washing* is the service, *washer* is the machine.

**Bucket-collapse discipline preserved.** `pressure washing services near me`,
`pressure washing service`, `pressure washing company near me` are **not added** — each shares a
Planner volume bucket with a text already owned, and adding them would double-count demand and
create self-competition.

**September 1 adds no keyword.** Ten search terms, zero clicks, zero cost. Nothing in it meets
the evidence bar to add, remove or re-own a keyword.

---

## 10. Final cross-negative decision

# PHASED. Deploy 107 at launch (Layers 1 + 3). Defer the 20 Layer-2 negatives.

**Unchanged from memo §7.**

| Layer | Criteria | At launch? | Reason |
|---|---:|---|---|
| **1 — Sibling EXACT mirror** | **95** | **YES** | Enforces one-owner-per-text. Zero blocking risk: a negative EXACT blocks only the literal string, and every text has exactly one owner. |
| **2 — Historical rogue-query EXACT** | **20** | **NO — DEFER 14 days** | **Every one of the 20 queries was mis-routed by an ad group that is being retired.** Once those containers are paused the new structure may route them correctly unaided. Pre-loading 20 permanent criteria against a problem the restructure may already solve is over-engineering. |
| **3 — Modifier PHRASE** | **12** | **YES** | Family-level power / pressure / house / soft fences. 23 of 35 candidates were rejected for self-blocking. |

**Safeguards preserved, all of them:**

- Routing negatives at **ad-group level only**; the 132-per-campaign universal fence stays
  **separate at campaign level**.
- **No routing negative is added before its intended owner ad group is live and verified.**
- **No self-blocking** — no owner keyword blocks itself.
- **Search Terms reviewed continuously**, not once.
- **Negative keywords cannot fully control loose positive close variants.** An EXACT negative
  blocks only the literal string; an unseen close variant slips past regardless of how many
  criteria exist. September 1 produced a live example — `pressure washer near me` served as a
  NEAR_EXACT close variant. **Residual close-variant risk is permanent and is managed by
  continuous search-term review, not by pre-loading criteria.**

**Two new PLAN-R2 candidates from September 1** (recorded, not actioned): `pressure washer near
me` (equipment intent) and `commercial pressure washing near me` (outside verified residential
scope). Both zero clicks, zero cost.

---

## 11. Final CPC decision

# $15.00, symmetric on both campaigns — but NOT today, and no longer the first move.

**Does PLAN-R3B remain the best immediate CPC decision? No — on two counts, one carried forward
and one new.**

| Question | Answer |
|---|---|
| **Best current ceiling** | **$15.00.** Unchanged from the memo's revision of $12. $12 and $15 cover **identical measured demand** (98.2%, 5 of 6 buckets); $15 buys **25% more Ad Rank headroom for zero coverage cost**, which is what an account with Quality Score 1 on its biggest keyword needs, since Ad Rank is bid × Quality Score. **PLAN-R3B's $12 figure is superseded; its structure and symmetry are correct.** |
| **Apply immediately?** | **NO.** *(This is a change from the memo's "now".)* |
| **Apply to both campaigns while both are live?** | **YES — non-negotiable.** Moving one creates the Ad Rank asymmetry across shared query space that voided PLAN-R3A. Five search terms have served in **both** campaigns, carrying 26.7% of valid clicks and 24.8% of spend. |
| **Wait until consolidation?** | **NO.** Consolidation is 3–5 weeks away; do not wait that long. Wait for a **clean baseline**, not for the restructure. |
| **Does September 1 change the recommendation?** | **YES — the timing, not the amount.** |
| **Financial risk of waiting** | **Now small in the immediate term.** The memo priced waiting at ~$150–$300 per 10 serving days at ~$29.44/click. Actual spend over the last three calendar days is **$29.32 total**, and the last two serving days cost **$0.00 and $29.32**. Google's filtering has, for now, removed the bleed the cut was meant to stop. If billable delivery resumes at the August rate, the ~$29/click exposure returns and so does the ~$150–$300/10-day figure. |
| **Delivery / rank risk of acting now** | **Higher than it was, and newly confounded.** Campaign A already loses **47.74%** of impression share to rank at $30, and September 1 delivered **12 impressions and zero billable clicks**. A 49% ceiling cut into that floor risks pushing delivery to zero — and because Google is simultaneously filtering ~100% of this account's mobile clicks, **you would not be able to tell whether the cut killed delivery or the invalid-click filter did.** That is an unreadable experiment, and an unreadable experiment is worse than no experiment. |

**Recommended gate — apply $15 to both campaigns once BOTH are true:**

1. The measurement repair (§13, and the next action in §16) is executed and read back; **and**
2. **One settled serving day produces at least one billable click**, re-establishing a baseline
   the cut can be measured against.

If Walter prefers to move on cost control regardless of the confound, that is a legitimate call
and the downside is bounded: the risk is attribution ambiguity and lost impression share, not
money. **My recommendation is to wait for the gate.** It is likely days, not weeks.

**PLAN-R3B `BC0A5A7258E2` must not be approved** — it carries $12, not $15, and the September 1
evidence adds a timing gate the plan does not contain. A successor plan and a new fingerprint are
required. **Neither is created here.**

---

## 12. Final measurement decision — exact required order

**Unchanged from memo §9, re-confirmed live today. No conversion change is made in this file.**

| # | Action | Type | Status today |
|---:|---|---|---|
| **1** | **Correct the customer conversion-goal biddable settings.** Set the three lead categories in `customer_conversion_goal` to `biddable: true` — PHONE_CALL_LEAD/WEBSITE, PHONE_CALL_LEAD/CALL_FROM_ADS, SUBMIT_LEAD_FORM/WEBSITE. **Leave GET_DIRECTIONS `false`.** | **3 API mutations, field mask `biddable`** | **Fresh-read 2026-09-01: all four still `FALSE`.** Ready. |
| **2** | **Correct `include_in_conversions_metric`.** Re-read after step 1 before proposing anything. All four conversion actions currently read `FALSE`; this field is expected to follow the goal-level setting. **Do not propose a separate mutation until step 1's readback proves it is still needed.** | conditional | Pending step 1 |
| **3** | **Verify the form conversion** — `Softwind Power Washing \| Submission Lead Form` (`7708725995`, WEBPAGE, ONE_PER_CLICK, 4 tag snippets). | **BLOCKED** | PRESENCE targeting means a real GCLID requires a click originating on Long Island. |
| **4** | **Verify the website-call conversion** — `Softwind Power Washing \| Website Phone Call Lead` (`7708765130`, WEBSITE_CALL, 1 snippet). | **BLOCKED** | Same GCLID constraint, plus it rings the client's real line. |
| **5** | **Verify the call-asset conversion** — `Softwind Power Washing \| Call Asset Lead` (`7711699090`, AD_CALL, 0 snippets). | **UNTESTABLE TODAY** | 88 call impressions, **0 call clicks**, **0 `call_view` rows** across the entire retained log. The path has never been exercised. |
| **6** | **Investigate foreign tag `AW-17878095007`** on all six offer pages plus two main-site pages. | website / owner | Signal leakage to an account Green Marketing does not control. Not a Google Ads mutation. |
| **7** | **Reconcile WhatConverts** against Google Ads once steps 1–5 make the columns comparable. | reporting | Today both sources read zero, so they already agree; reconciliation becomes meaningful only after a real lead exists. |

**Adjacent, non-blocking:** ClickCease loads on every page and syncs **zero** `IP_BLOCK` criteria
into either campaign — re-confirmed today. Given the September 1 mobile pattern this is worth the
client's attention. **Do not remove ClickCease.**

**Why the order is fixed:** step 1 is the only step that is neither blocked nor conditional, and
every later step's output is unreadable until it lands.

---

## 13. Final landing-page decision

**Unchanged from memo §10. Verified by real-browser render on 2026-08-31; not re-verified on
2026-09-01, and nothing in today's read invalidates any of it.** All six offer pages still serve
as campaign final URLs.

| Priority | Issue | Still valid? | Pages | Fix before enabling new ad groups? |
|---|---|---|---|---|
| **P0** | Browser title reads **"Softwind Landscape & Masonry"** — the scope-fenced sibling brand, not the power-washing brand the ad promises | **VALID** | all 6 offer pages | **YES** |
| **P0** | **Foreign Google Ads tag `AW-17878095007`** firing on every paid view | **VALID** | 6 offer + 2 main-site | **YES** |
| **P1** | H1 locked to **"Islip, West Islip & Dix Hills"** while both campaigns target **80 places** | **VALID — and re-confirmed today: still 80 positive locations per campaign** | 6 of 8 | **YES — before the head terms go live** |
| **P1** | **"Offer Ends" countdown** with no dated offer, resetting on reload | **VALID** | 6 | **YES** |
| **P2** | No reviews, rating, years in business, licence or insurance | **VALID** | all | No — **blocked on client confirmation.** Never publish an unverified rating, licence or guarantee. |
| **P3** | `/patio-power-washing/` title says "Power", H1 says "Pressure" | **VALID** | 1 | No |

**Location wording:** **"Long Island" as the H1 anchor, with "Serving Nassau and Suffolk County"
as the supporting line.** Both are verifiable from the 80 live `geo_target_constant` canonical
names — every one is a New York location in Nassau or Suffolk. **Do not use dynamic location
insertion** (no verified per-town content; it risks naming a town the client does not serve).
**Do not keep the three-city wording** — it names 3 of 80. **Do not build per-city pages** — no
city keyword has reportable demand.

**Verified correct and unchanged:** HTTP 200 with no redirects · approved tracked phone
**(631) 502-7946** in `tel:` and body on all six · GCLID and all four UTMs persist ·
5-field Gravity Form · mobile/desktop parity · GA4, GTM, WhatConverts and ClickCease all loading.

**Phone tracking / form tracking:** the page-side plumbing is verified present; what is
**unproven** is whether a submission or call reaches Google Ads as a conversion — that is
§12 steps 3–5, and it is blocked by PRESENCE targeting, not by the page.

**Mobile performance:** parity confirmed; no separate mobile defect was found. Given the
September 1 mobile invalid-click pattern, mobile page speed is worth measuring — but it is a
diagnostic, not a fix, and it is not on the critical path.

**A Google Drive content draft does not authorize a WordPress edit, a tracking change, a Google
Ads final-URL change, or a live deployment.**

---

## 14. Final RSA decision

**Unchanged from memo §11.**

| Ad group | Current RSAs | Decision |
|---|---|---|
| **Power Washing** (from `202870585390`) | 2 ENABLED, Ad Strength EXCELLENT, **ad relevance BELOW_AVERAGE**, 9 of 15 headlines name 3 hamlets | **Replace both.** Create 2 new **PAUSED**. |
| **Pressure Washing** | none — new ad group | **Create 2 PAUSED** |
| **House Washing** | none — new ad group | **Create 2 PAUSED** |
| **Soft Washing** · **Driveway Pressure Washing** · **Patio Pressure Washing** | 2 each, APPROVED, GOOD/EXCELLENT, **zero impressions** | **KEEP.** No evidence to act on. |

- **Which can remain:** the 6 RSAs in Soft Washing, Driveway and Patio.
- **Which need replacement:** the 2 in the Power Washing source ad group — the hamlet-heavy
  headlines are the direct cause of BELOW_AVERAGE ad relevance and they conflict with the
  Long Island wording decision in §13.
- **Which must be created paused:** **all 6 new RSAs.** Every new resource is created paused.
  **Enabling requires a second, separate approval after create-paused readback QA.**
- **Do the currently drafted RSAs fit the final architecture?** **PLAN-R5 targets the right ad
  group, but its copy was drafted against the old structure.**
- **Must copy be regenerated after the architecture decision?** **YES.** Copy is written at build
  time against the as-built ad groups, then validated for 30/90/15 character limits and against
  the client's `unverified_claims_do_not_use` list. **No filler to reach 15 headlines. Ad Strength
  is not the objective** — the current ads score EXCELLENT while carrying BELOW_AVERAGE ad
  relevance, which is precisely why it is the wrong target.

---

## 15. Audience and demographic confirmation

**Fresh read, 2026-09-01:** `USER_LIST` **0** · `GENDER` **0** · `AGE_RANGE` **0** ·
`INCOME_RANGE` **0**.

| Confirmation | Status |
|---|---|
| **Women will not be excluded** | **CONFIRMED.** Zero GENDER criteria exist. Nothing to undo, and nothing proposed. Prior evidence stands: women 17.95% CTR at $25.63 CPC versus men 9.22% at $32.46. |
| **Unknown gender will not be excluded** | **CONFIRMED.** Excluding Unknown discards a large share of unidentified real buyers. |
| **Audiences, if used, remain Observation only** | **CONFIRMED.** No Targeting setting is proposed anywhere. |
| **Bid modifiers remain 0% initially** | **CONFIRMED.** PLAN-R9's twelve criteria are all 0%. |
| **Audience work is not the first recovery action** | **CONFIRMED — DEFERRED.** Twelve observation criteria at 0% produce zero leads by design. With 18 lifetime valid clicks the observation data would be uninterpretable for months. |

---

## 16. Plan-status reconciliation

**Applying the September 1 date reset. Stale fingerprints are not honoured automatically.**

| Plan | Status | Reason |
|---|---|---|
| **PLAN-R1** — measurement verification | **REVISE** | Finding re-confirmed live today. Currently 0 actions / READ-ONLY, so it emits no approval command. The conversion-goal repair is **API-mutable** and must become an executable **3-mutation** plan; the blocked test components stay separate. **`98BA60C3983D` is an investigation fingerprint and cannot be approved as an action.** |
| **PLAN-R2** — search-term negatives | **KEEP** | 8 mutations, adds-before-removes ordering, zero collisions. Still correct. **Two September 1 candidates recorded for the next revision** (`pressure washer near me`, `commercial pressure washing near me`) — not yet added, so **`2A06983866C1` remains valid as written.** |
| **PLAN-R3** — $22 both campaigns | **VOID — NON-APPROVABLE** | Superseded. `97D8B268A80A` is in the do-not-honour registry. |
| **PLAN-R3A** — $12 one campaign | **VOID — NON-APPROVABLE** | Superseded. Invalid control design. `B57E427D07C5` is in the do-not-honour registry. |
| **PLAN-R3B** — $12 both campaigns | **SUPERSEDE** | Structure and symmetry are right; **the amount changes to $15** and September 1 adds a **timing gate** the plan does not contain. **`BC0A5A7258E2` must not be approved.** A successor plan and a new fingerprint are required — **not created here.** |
| **PLAN-R4** — one-campaign architecture | **KEEP WITH REVISION** | Conclusion holds and is reinforced by September 1. Update the ad-group count from 3 core to the **6-group single-intent** structure. Decision record; emits no approval command. |
| **PLAN-R5** — replacement RSAs | **KEEP WITH REVISION** | Right ad group; **copy must be re-drafted against the as-built groups** after R6. Create paused. |
| **PLAN-R6** — new ad groups and keywords | **REVISE** | Expand from 3 SKAGs to the **6-group single-intent structure and 19 canonical texts**. Create paused. |
| **PLAN-R7** — landing-page fixes | **KEEP** | P0 title and foreign tag; P1 city lock and countdown. **Website track — a Drive draft authorizes no deployment.** |
| **PLAN-R8** — asset fixes | **CLOSED** | Parity completed by owner action on 2026-08-31. **The old action fingerprint `DFF115FF4D26` remains VOID and do-not-honour** because the two asset links were completed manually. The remaining items (image assets, business-name asset, 17:00→18:00 call-asset schedule) are **blocked on client-supplied inputs**. |
| **PLAN-R9** — audience observations | **DEFER** | Reporting enhancement; produces no leads. Revisit once the consolidated structure has volume. |
| **PLAN-R10** — enablement | **PROVISIONAL — DEFER** | **Remains provisional.** Every action names a `PENDING_CREATION` placeholder. **`CE1BA19B8F5A` must be regenerated against real resource IDs after R6 creates them and readback QA passes.** No approval command. |
| **PLAN-R11** — old-resource retirement | **BLOCKED** | **Remains blocked** until replacements are live and verified serving. `3AB271E93FC7` is FINAL but suppressed. No approval command. |
| **PLAN-R12** — budget hold | **KEEP — NO-ACTION** | **Contains no budget change and therefore emits no approval command** — correctly suppressed in the manifest. Re-confirmed today: Lost IS to budget **3.70% / 7.32%**. **Budget is not the constraint.** |
| **Strict SKAG cross-negative matrix (127)** | **KEEP WITH REVISION** | Deploy **107 at launch** (Layers 1 + 3); **defer the 20 Layer-2 rogue-query negatives** for 14 days of real routing evidence. |
| **August month-end rescue plans** — `2026-08-26-month-end-delivery-rescue-master-plan.md`, `2026-08-26-daily-pacing-control.md`, `2026-08-26-plan-i1b-budget-fresh-pacing.yaml`, `2026-08-26-plan-i1c-budget-after-full-geo.yaml`, `2026-08-26-rescue-fingerprint-manifest.json` | **HISTORICAL / MONTH CLOSED** | Their sole purpose — reaching the $2,500 August spend target by 2026-08-31 — expired with the month. **Remaining August budget, required August daily spend, required August rolling pace and month-end rescue urgency are retained as historical evidence only and are used as decision inputs nowhere in this file.** |
| **Technically valid components salvaged from the rescue set** | **CARRIED FORWARD, not voided** | Three survive on their own merit, independent of August pacing: **(a)** the **80-location NY geo footprint** (PLAN-J2A) — live and correct; **(b)** the **Connecticut exclusion** (PLAN-J2B) — live and correct, `21139` present on both campaigns; **(c)** the **$30 CPC ceiling control** (PLAN-K1) — live, and the diagnostic that produced the whole CPC analysis. None is re-approved here; all three are already executed and verified. |

**No new fingerprint was created in this continuation.** The R-series manifest is unchanged at
**14 plans, 3 void fingerprints, 20/20 reconciliation assertions passing**.

---

## 17. The single next action

**The August 31 memo selected: repair the conversion-goal configuration.**

**Does September 1 change that priority? No — it reinforces it, and it weakens the only
competing candidate.**

The one action that could have displaced it was the $15 CPC ceiling. September 1 removed its
urgency (spend $0.00; three-day account spend $29.32) and added a confound that makes it
unreadable today. Nothing else on the list is both unblocked and independent.

# Repair the conversion-goal configuration.

Set the three lead categories in `customer_conversion_goal` to `biddable: true` —
**PHONE_CALL_LEAD/WEBSITE**, **PHONE_CALL_LEAD/CALL_FROM_ADS**, **SUBMIT_LEAD_FORM/WEBSITE**.
**Leave GET_DIRECTIONS `false`.**

| | |
|---|---|
| **Exact action** | 3 mutations on `customer_conversion_goal` via `CustomerConversionGoalService`, operation `update`, field mask **`biddable`** only. No other field, no other resource. |
| **Why it is first** | It is the only action that makes **every other action measurable**, and it is the only candidate that is neither blocked, conditional, nor dependent on another step. September 1 was another full serving day in which a lead, had one arrived, could not have been counted. Cutting CPC, rebuilding structure and fixing pages all produce results nobody can trust until this lands. |
| **Evidence** | Fresh read **2026-09-01**: all four `customer_conversion_goal` rows `biddable: FALSE`; all four conversion actions `include_in_conversions_metric: FALSE`. Lifetime `conversions` 0.00 **and** `all_conversions` 0.00 on 18 valid clicks and $595.87. WhatConverts independently reads zero relevant leads. `CustomerConversionGoal.biddable` was verified writable, with `CustomerConversionGoalOperation` supporting `update` with an `update_mask`. |
| **Expected effect** | **Zero leads directly. It creates no demand.** It makes leads *visible*. The Conversions column becomes capable of counting a form submission, a website call and a call-asset call. That is why it is first — not why it is valuable. |
| **Confidence** | **HIGH.** The defect is confirmed by fresh read on all four goals and all four actions, twice, twelve days apart. |
| **Risk** | **VERY LOW.** Both campaigns already override with campaign-level goals in which these three categories are **biddable** — re-verified today. **Bidding does not change.** Only what the Conversions column counts changes. Fully reversible with the same three mutations inverted. |
| **Dependency** | **NONE.** Not blocked by PRESENCE targeting, not blocked on client inputs, not blocked on a developer, not blocked on the restructure. |
| **Existing plan that covers it** | **PLAN-R1** — "Measurement verification and conversion-counting repair", fingerprint `98BA60C3983D`. |
| **Is that plan still valid?** | **The finding is valid and re-confirmed today. The plan form is not.** PLAN-R1 is written as a zero-mutation READ-ONLY investigation (`action_count: 0`, `ads_mutation_count: 0`, `approval_command_allowed: false`). It cannot authorize the repair. |
| **Is a revised plan needed?** | **YES.** A new executable plan carrying exactly **3 mutations** on `customer_conversion_goal`, field mask `biddable`, with explicit readback assertions on all four goal rows and all four conversion actions. |
| **Does it require a new fingerprint?** | **YES — and it was NOT created in this step.** |

**Second, once that is approved — but not now:** the **$15** symmetric ceiling, gated per §11.
They do not compete: the measurement repair touches a different resource, carries no delivery
risk, and can be approved in the same sitting. But if only one moves first, it must be the one
that makes the other readable.

---

## 18. Confirmations

**No fingerprint was created in this continuation.** The R-series manifest is untouched at 14
plans, 3 void fingerprints, 20/20 reconciliation assertions passing. `BC0A5A7258E2` (PLAN-R3B)
exists, is **not approved**, and is **marked for supersession** at $15 with a timing gate.
**No approval command is emitted anywhere in this file.**

**Zero external changes.** Every Google Ads call in this session was a `SELECT` through
`GoogleAdsService.search`. No operation object was constructed and no mutate service was called.

| Safety check | Result |
|---|---|
| Identity gate passed | **YES** — name, ID, manager=false, test=false, ENABLED, USD, America/New_York |
| Work order still validates | **YES** — service, vertical, scope approval, mode `read`. The expired `month_end_objective` block is flagged, not used. |
| No external mutation occurred | **CONFIRMED** |
| No CPC ceiling changed | **CONFIRMED** — both still `30000000` micros |
| No budget changed | **CONFIRMED** — $41.50 / $41.11 |
| No campaign renamed | **CONFIRMED** — the two renames are owner actions via `GOOGLE_ADS_WEB_CLIENT`, proven by `change_event` |
| No campaign paused | **CONFIRMED** — both ENABLED / SERVING |
| No ad group created | **CONFIRMED** — 30 non-removed, 12 enabled |
| No ad group enabled | **CONFIRMED** |
| No keyword added | **CONFIRMED** — 214 |
| No negative added | **CONFIRMED** — 264 campaign, 0 ad-group |
| No RSA added | **CONFIRMED** — 54 ads |
| No asset changed | **CONFIRMED** — 20 campaign asset links |
| No audience added | **CONFIRMED** — 0 |
| No conversion changed | **CONFIRMED** — 4 goals all `biddable: FALSE`, 4 actions all `include_in_conversions_metric: FALSE`, exactly as found |
| No landing page changed | **CONFIRMED** — no site was written to; pages were not even re-fetched |
| No form submitted | **CONFIRMED** |
| No call placed | **CONFIRMED** |
| No fingerprint created | **CONFIRMED** |
| No approval command emitted | **CONFIRMED** |

---

**SEPTEMBER 1 FINAL STRATEGY CONTINUATION COMPLETE — ONE NEXT ACTION SELECTED — WAITING FOR
WALTER'S DECISION — ZERO EXTERNAL CHANGES MADE**
