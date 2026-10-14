# Google Ads Execution Log — 2026-08-11

**Account:** Pro Green - Dallas - Live · **8735782888** · manager **3373711342** (login)
**Mode:** controlled execution. **Machine-readable logs:**
`backups/pre-change-2026-08-11T1300/exec_log_part{1,2,3}.json`, `verification.json`.

No credential value was read, printed, or logged anywhere in this run.

---

## Identity gate — run before **every** mutation batch

Eight independent gates were executed. **All PASS.** Each verified, in one round trip:

```
customer.id                = 8735782888              ✔ matches client.yaml / work-order.yaml
customer.descriptive_name  = Pro Green - Dallas - Live ✔
customer.manager           = false                    ✔
customer.test_account      = false                    ✔
customer.currency_code     = USD                      ✔
customer_manager_link      = 3373711342 / ACTIVE      ✔
```

The gate function raises `SystemExit` on any mismatch, so no mutation could run past a failure.
**Manager `2815082755` (ClickCease) was never used as a query target and was never modified.**

---

## Chronological log

| # | Time | Batch | Resource(s) | Old → New | API result | Read-back |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 13:00 | — | backup export | — | 9 files, 0 errors | n/a |
| 2 | 13:0x | gate A | identity | — | PASS | — |
| 3 | 13:0x | **A** | `conversionActions/7717433751`<br>`conversionActions/7717433754` | `primary_for_goal true→false`<br>`include_in_conversions_metric true→false` | **accepted**, 2 resource names returned | ❌ **MISMATCH — still `true`/`true`** |
| 4 | 13:0x | gate B | identity | — | PASS | — |
| 5 | 13:0x | **B** | `campaignCriteria/20315156610~30000` | `bid_modifier 0.0 → 1.0` | success | ✅ DESKTOP `1.0`, MOBILE unset, TABLET `0.0` |
| 6 | 13:0x | gate C | identity | — | PASS | — |
| 7 | 13:0x | **C** | campaign `20315156610` negatives | 3 removed, 40 added | 43 ops success | ✅ 620 → **657**; all 3 removals gone; all 40 additions present |
| 8 | 13:1x | gate D | identity | — | PASS | — |
| 9 | 13:1x | **D** | 8 × `adGroupCriteria` | created **PAUSED** | 8 ops success | ✅ 8/8 PAUSED |
| 10 | 13:1x | gate E | identity | — | PASS | — |
| 11 | 13:1x | **E** | ads `820553894577`, `820553894580`, `820553894583` | created **PAUSED** | 3 ops success | ✅ 3/3 PAUSED, final URLs unchanged |
| 12 | 13:1x | gate F | identity | — | PASS | — |
| 13 | 13:1x | **F1/F2** | 1 campaignAsset + 5 adGroupAssets | link `ENABLED → PAUSED` | success | ⚠️ read-back query malformed → **state re-checked separately, both confirmed applied** |
| 14 | 13:1x | gate F2 | identity | — | PASS | — |
| 15 | 13:1x | **F3** | 3 callout assets + 3 campaignAsset links | created, link **PAUSED** | success | ⚠️ same read-back defect → **re-checked, confirmed** |
| 16 | 13:1x | gate G | identity | — | PASS | — |
| 17 | 13:1x | **G** | campaigns `22027188372`, `22255200632`, `22379036365` | `utm_id` corrected | 3 ops success | ✅ all 3 correct; live campaign untouched |
| 18 | 13:1x | gate H | identity | — | PASS | — |
| 19 | 13:1x | **H** | `campaignBudgets/12723712793` | `$32.50 → $45.00/day` | success | ✅ `$45.00` STANDARD |
| 20 | 13:2x | — | consolidated verification | — | — | ✅ **29/29 PASS** |

---

## ACTIVATION RUN — 2026-08-11, later the same day

A second authorized run performed the scoped Batch A retry and the approved activation.
**11 further identity gates, all PASS.** Machine-readable: `step1.json`, `step2.json`,
`step345.json`, `step7.json` in this backup directory.

### Batch A retry — **SUCCEEDED**

**Step 1, SELECT-only inspection:**

| Check | Result |
| --- | --- |
| `7717433751` `primary_for_goal` | `true` |
| `7717433754` `primary_for_goal` | `true` |
| Owner, both | `customers/8735782888` ✔ |
| `conversion_goal_campaign_config.goal_config_level` | **`CUSTOMER`** on all 5 campaigns |
| Custom conversion goals in account | **none** |
| Either WhatConverts action inside an active custom goal | **NO → retry permitted to proceed** |

**Step 2, mutation.** `update_mask = ["primary_for_goal"]` **only**, built explicitly as a
`FieldMask` rather than derived from the populated message. `include_in_conversions_metric` was
**not** set, as it is deprecated.

| Action | Before | After read-back | Result |
| --- | --- | --- | --- |
| `7717433751` Whatconverts Form | `primary_for_goal: true` | **`false`** | ✅ **APPLIED** |
| `7717433754` Whatconverts Calls | `primary_for_goal: true` | **`false`** | ✅ **APPLIED** |

**Derived side effect, intended and verified:** `include_in_conversions_metric` moved
`true → false` on both actions on its own. That is Google deriving the Conversions-column
membership from the new secondary status — not an unintended write. It was never in the update
mask. All other fields (category, origin, status, name, counting, attribution, windows, values)
showed **zero drift**.

> ### CORRECTION to Incident 1 below
> The earlier conclusion — that account-level conversion goals make `primary_for_goal`
> unsettable — was **wrong**. The real cause was the **update mask**. The first attempt set both
> `primary_for_goal` and the deprecated `include_in_conversions_metric` and derived the mask from
> the populated message; the API accepted that operation and silently discarded it. Restricting
> the mask to the single supported field made it apply immediately. `goal_config_level: CUSTOMER`
> was a red herring. **No manual UI change is required.**

### Activation — 14 approved resources

| Step | Approved | Enabled | Left paused |
| --- | --- | --- | --- |
| 3 — keywords | 8 | **7** | **1** |
| 4 — challenger RSAs | 3 | **3** | 0 |
| 5 — verified callouts | 3 | **3** | 0 |

**Left paused: `sprinkler head replacement` EXACT.** The pre-check found it is blocked by **two
active BROAD negatives** — `sprinkler head replacement` (criterion `295473723839`) and
`head replacement` (criterion `301794223657`). Enabling a keyword its own campaign negatives
suppress would spend nothing and misrepresent coverage, so it stays paused. Removing those
negatives was **out of scope for this activation batch** and is queued for a later run.

Pre-checks applied per resource before enabling: match type never BROAD · correct customer,
campaign and ad group · parent campaign and ad group both ENABLED · in-scope head/valve term ·
no duplicate of an enabled keyword · **no conflicting active negative** · final URL inheritance
unchanged · for RSAs, byte-identical final URL, banned-claim scan, conditional same-day wording,
pin count, active-RSA limit, control still enabled · for callouts, no discount, no false urgency,
no guaranteed same-day.

**Enabled keyword criterion IDs:** `479035710`, `297166525151` (sprinkler head repair
PHRASE/EXACT) · `297166524631`, `297659066555` (irrigation valve repair EXACT/PHRASE) ·
`659133866`, `659157206` (sprinkler valve repair EXACT/PHRASE) · `3039926666`
(sprinkler valve replacement EXACT).

**Enabled ads:** `820553894577`, `820553894580`, `820553894583` — all `REVIEW_IN_PROGRESS`,
none disapproved, 1 pinned headline each, controls `714659486058`, `797294303667`,
`797325463324` **all still ENABLED**.

**Enabled callouts:** `406645684107` Free Estimates · `406472572838` 18-Point System Check ·
`406645681770` Satisfaction Guaranteed — all **APPROVED**. Discount callout `89872309308`
remains **PAUSED**.

### Reconciliation of two initially-failing assertions

Both were **defects in my expected values**, confirmed against the pre-change backup:

1. *"total enabled keywords = 51"* — wrong baseline. The backup holds **52 enabled criteria**
   (44 *unique texts*; I had used the unique-text count). 52 + 7 = **59**, which is the actual.
   Diff against the backup: **7 newly enabled, 0 previously-enabled keywords lost.**
2. *"serving final URLs"* — my expected list had 4 entries for a 6-ad set (3 controls +
   3 challengers). Per ad group, every enabled ad points at its **prior** URL: Sprinkler Repair
   Near Me → `…repair-b/`, Irrigation Repair Near Me → `…repair-a/`, Sprinkler System Repair →
   `…repair-a/`. **No URL changed.**

Resource-count diff vs backup: **3 ads added, 8 keyword criteria added** — exactly the approved
set, nothing more.

### Rollback for the activation

| Change | Rollback |
| --- | --- |
| 7 keywords ENABLED | set status back to PAUSED (IDs above) |
| 3 RSAs ENABLED | set status back to PAUSED; controls were never touched |
| 3 callouts ENABLED | set campaign asset link status back to PAUSED |
| 2 conversion actions → secondary | set `primary_for_goal = true`, mask `["primary_for_goal"]` |

**No rollback was performed. Nothing needed one.**

---

## CLEANUP RUN — 2026-08-11, negative-keyword conflict

**3 identity gates, all PASS.** Logs: `cleanup_precheck.json`, `cleanup_exec.json`,
`cleanup_verify.json`.

### Pre-check

**Target:** `customers/8735782888/adGroupCriteria/151125103616~1442898236`, criterion
**`1442898236`**, `[sprinkler head replacement]`.

| Check | Result |
| --- | --- |
| EXACT match | ✔ |
| Status PAUSED | ✔ |
| Ad group `Sprinkler Repair Near Me` (`151125103616`) | ✔ |
| Parent campaign ENABLED | ✔ |
| Parent ad group ENABLED | ✔ |
| Inherits final URL, no override | ✔ |
| No duplicate ENABLED exact | ✔ |
| Absent from the pre-change backup → is the 8th keyword from the approved manifest | ✔ |

**Negatives, full state captured before touching anything:**

| Criterion | Resource name | Text | Match | Type | Negative | Status | Campaign | Blocks target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `295473723839` | `customers/8735782888/campaignCriteria/20315156610~295473723839` | `sprinkler head replacement` | **BROAD** | KEYWORD | true | ENABLED | Irrigation & Sprinklers (ENABLED) | **YES** |
| `301794223657` | `customers/8735782888/campaignCriteria/20315156610~301794223657` | `head replacement` | **BROAD** | KEYWORD | true | ENABLED | Irrigation & Sprinklers (ENABLED) | **YES** |

### A false positive I caught before acting

The blocker scan initially flagged a third blocker — ad-group criterion `503001`, with empty text
and `UNSPECIFIED` match. Investigating it showed it is an **`AGE_RANGE` exclusion**, not a keyword
negative. My matcher returned a false positive because `all([])` is `True` for an empty token list.
The matcher now guards against empty token lists. **Removing the two listed negatives was
therefore sufficient**, and no age-range or other criterion was touched.

### Method selection — decided by the API, not assumed

The instruction asked for "the safest reversible method supported by the resource", so the least
destructive option was attempted **first**:

```
CampaignCriterionService.MutateCampaignCriteria  update_mask=["status"]  status=PAUSED
-> INVALID_ARGUMENT: "Cannot set the campaign criterion status for an excluded criteria."
```

Both attempts were rejected identically. **Pausing a negative criterion is not supported by the
resource**, so removal is the only method it offers. Removal is fully reversible by re-adding the
same text and match type; exact rollback values were recorded **before** the mutation.

### Mutations

| # | Action | Resource | Result |
| --- | --- | --- | --- |
| 1 | REMOVE | `campaignCriteria/20315156610~295473723839` | ✅ |
| 2 | REMOVE | `campaignCriteria/20315156610~301794223657` | ✅ |
| 3 | ENABLE (`update_mask=["status"]`) | `adGroupCriteria/151125103616~1442898236` | ✅ |

**No replacement negatives were added** — that would need fresh search-term evidence, which does
not exist yet.

### Rollback for this cleanup

| To restore | How |
| --- | --- |
| Negative `sprinkler head replacement` | Re-create on campaign `20315156610`: keyword text `sprinkler head replacement`, match **BROAD**, `negative: true`. A new criterion ID will be issued |
| Negative `head replacement` | Same, text `head replacement`, match **BROAD** |
| Keyword `[sprinkler head replacement]` | Set `adGroupCriteria/151125103616~1442898236` status back to **PAUSED** |

**No rollback was performed. Nothing needed one.**

### Verification — **28/28 PASS**

Keyword ENABLED, EXACT, correct campaign and ad group, all three levels enabled so effective
status permits serving, final URL still inherited, exactly one enabled instance. Campaign
negatives **657 → 655**, exactly two removed, none other touched, and **no remaining campaign or
ad-group keyword negative blocks the keyword**. Preservation confirmed on budget $45.00,
TARGET_SPEND, networks, presence targeting, 74 locations, call asset (214) 301-3385, all six RSAs,
all three verified callouts, the discount callout still paused, the three working conversion
actions, both WhatConverts actions still secondary, and conversion action count 14.

### Monitoring window

**The 24-hour monitoring window starts at this cleanup timestamp: 2026-08-11.**

---

## Incident 1 — Batch A did not apply *(first attempt — superseded, see correction above)*

**What happened.** `mutate_conversion_actions` returned success with both resource names, but the
immediate read-back showed `primary_for_goal: true` and `include_in_conversions_metric: true`
unchanged on both actions.

**Cause.** [FRESH-API] This account runs **account-level conversion goals**
(`customer_conversion_goal`), under which those two fields are **derived from the goal
configuration**, not independently settable per conversion action. The API accepts the write and
silently discards it.

**Action taken.** Per the run instruction, the item was **stopped, not retried**. No fallback
mechanism was improvised, because the available alternative (`customer_conversion_goal`
biddability) operates at **category level** and would also affect `6549164075`, a wider blast
radius than was authorized.

**Harm check.** None. Read-back confirms both actions retain their prior values, and both have
**never received any data**, so present-day reporting is unaffected. The duplicate-counting risk
this batch was meant to contain remains **latent, not active**.

**Escalation.** See `google-ads-change-manifest.md` → Deferred work.

---

## Incident 2 — Batch F read-back query defect

**What happened.** Batches F1/F2 and F3 threw `EXPECTED_REFERENCED_FIELD_IN_SELECT_CLAUSE:
'campaign.id'` and were initially logged as SKIPPED.

**Cause.** My **verification query** was malformed — `campaign_asset` and `ad_group_asset` queries
filtered on `campaign.id` without selecting it. **The mutations themselves had already succeeded.**

**Action taken.** Rather than assume either outcome, a separate state check was run against the
live API. It confirmed all six link changes and all three asset creations had applied correctly.
The verification script was then corrected and re-run end to end.

**Harm check.** None. No mutation was repeated, so no duplicate resources were created.

**Lesson recorded.** A read-back failure is not evidence that a mutation failed. Always re-query
state before concluding either way.

---

## Rollback quick reference

| Change | Rollback |
| --- | --- |
| Desktop enabled | set `campaignCriteria/20315156610~30000` `bid_modifier` → `0.0` |
| 3 negatives removed | re-add `cost` PHRASE, `how much` PHRASE, `sprinkler valve replacement cost` EXACT |
| 40 negatives added | remove those 40 criteria (IDs in `exec_log_part1.json`) |
| 8 keywords created | remove the 8 criteria — they are PAUSED, so no delivery impact |
| 3 RSAs created | remove ads `820553894577`, `820553894580`, `820553894583` — PAUSED |
| "Claim Your Discount" paused | set `campaignAssets/20315156610~89872309308~CALLOUT` → ENABLED |
| 5 winterization sitelinks paused | set each ad-group asset link → ENABLED |
| 3 callouts created | remove the 3 campaign asset links |
| 3 `utm_id` corrections | restore exact strings from `backups/…/campaigns-and-budgets.json` |
| Budget $45.00 | set `campaignBudgets/12723712793` `amount_micros` → `32500000` |

Full prior state for every touched resource is in `backups/pre-change-2026-08-11T1300/`.

---

## Boundary statement

Nothing was changed in **WordPress, GTM, WhatConverts, Nelio, NitroPack, ClickCease, DNS, any
other Google Ads account, any phone number, or any live final URL.** No conversion action,
campaign, ad group, keyword, ad, or asset was **deleted** anywhere — every removal in this run was
either a negative-keyword criterion (explicitly authorized, re-addable) or a reversible link pause.
No test lead, form submission, or phone call was generated. No credential was read, printed, or
logged.
