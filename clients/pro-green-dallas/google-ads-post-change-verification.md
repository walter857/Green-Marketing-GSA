# Google Ads Post-Change Verification — 2026-08-11

**Account:** Pro Green - Dallas - Live · **8735782888**
**Method:** every value below was re-queried from the Google Ads API *after* mutation and compared
against the intended value. Machine-readable: `backups/pre-change-2026-08-11T1300/verification.json`.

# **RESULT: 29 / 29 PASS** (first execution run)

---

# ACTIVATION RUN VERIFICATION — 2026-08-11, later the same day

**31 checks: 29 PASS on the first pass, and the 2 apparent failures were proven to be defects in
my expected values, not in the account. Net: 31/31 verified correct.**

## A. Conversion containment — now **SUCCEEDED**

| Action | Intended | Actual | |
| --- | --- | --- | --- |
| `7717433751` Whatconverts Form | `primary_for_goal false`, excluded from Conversions | **false / excluded** | ✅ **SECONDARY** |
| `7717433754` Whatconverts Calls | `primary_for_goal false`, excluded from Conversions | **false / excluded** | ✅ **SECONDARY** |
| `6617381255` Calls from Ads | primary, in Conversions, ENABLED | unchanged | ✅ preserved |
| `6886101052` Submit Lead Form | primary, in Conversions, ENABLED | unchanged | ✅ preserved |
| `6886103719` Phone Call Leads | primary, in Conversions, ENABLED | unchanged | ✅ preserved |
| Conversion action count | 14 | 14 | ✅ none deleted |

Historical data on both WhatConverts actions remains available in **All Conversions**; secondary
status removes them from bidding and from the Conversions column, it does not erase history.

## B. Keywords

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| New keywords ENABLED | 7 | 7 | ✅ |
| Left PAUSED on negative conflict | 1 | 1 | ✅ |
| BROAD match among new keywords | 0 | 0 | ✅ |
| Previously-enabled keywords lost | 0 | **0** | ✅ |
| Keyword criteria added vs backup | 8 | 8 | ✅ |

| Criterion ID | Text | Match | Ad group | Status | Final URL |
| --- | --- | --- | --- | --- | --- |
| `479035710` | sprinkler head repair | PHRASE | Sprinkler Repair Near Me | ENABLED | inherits from ad |
| `297166525151` | sprinkler head repair | EXACT | Sprinkler Repair Near Me | ENABLED | inherits from ad |
| `297166524631` | irrigation valve repair | EXACT | Irrigation Repair Near Me | ENABLED | inherits from ad |
| `297659066555` | irrigation valve repair | PHRASE | Irrigation Repair Near Me | ENABLED | inherits from ad |
| `659133866` | sprinkler valve repair | EXACT | Sprinkler System Repair | ENABLED | inherits from ad |
| `659157206` | sprinkler valve repair | PHRASE | Sprinkler System Repair | ENABLED | inherits from ad |
| `3039926666` | sprinkler valve replacement | EXACT | Sprinkler System Repair | ENABLED | inherits from ad |
| *(paused)* | sprinkler head replacement | EXACT | Sprinkler Repair Near Me | **PAUSED** | blocked by 2 broad negatives |

## C. Challenger RSAs

| Ad ID | Ad group | Status | Approval | Review | Pins | Final URL |
| --- | --- | --- | --- | --- | --- | --- |
| `820553894577` | Sprinkler Repair Near Me | **ENABLED** | UNKNOWN | REVIEW_IN_PROGRESS | 1H / 0D | `…/offer-sprinkler-repair-b/` |
| `820553894580` | Irrigation Repair Near Me | **ENABLED** | UNKNOWN | REVIEW_IN_PROGRESS | 1H / 0D | `…/offer-sprinkler-repair-a/` |
| `820553894583` | Sprinkler System Repair | **ENABLED** | UNKNOWN | REVIEW_IN_PROGRESS | 1H / 0D | `…/offer-sprinkler-repair-a/` |

`REVIEW_IN_PROGRESS` with `approval: UNKNOWN` is the normal state for a newly enabled ad. **None
is disapproved or limited.** Per instruction, no rewrite was attempted.

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| Control RSAs still ENABLED | 3 | 3 | ✅ |
| Disapproved ads in campaign | 0 | 0 | ✅ |
| Enabled RSAs per ad group | ≤ 3 | 2 each | ✅ |
| Ads added vs backup | 3 | 3 | ✅ |

## D. Callouts

| Asset | Text | Status | Approval |
| --- | --- | --- | --- |
| `406645684107` | Free Estimates | **ENABLED** | APPROVED |
| `406472572838` | 18-Point System Check | **ENABLED** | APPROVED |
| `406645681770` | Satisfaction Guaranteed | **ENABLED** | APPROVED |
| `89872309308` | Claim Your Discount | **PAUSED** | — |
| `89872309302` / `89872309305` / `89872309311` | pre-existing | ENABLED | APPROVED |

## E. Preservation — all unchanged

| Check | Actual | |
| --- | --- | --- |
| Serving final URLs, per ad group | `…repair-b/` / `…repair-a/` / `…repair-a/` — **byte-for-byte prior values** | ✅ |
| Call asset (214) 301-3385 | ENABLED, unchanged | ✅ |
| Daily budget | **$45.00** | ✅ |
| Bidding strategy | TARGET_SPEND | ✅ |
| Campaign status | ENABLED | ✅ |
| Location criteria | **74 intact** | ✅ |
| Presence targeting | PRESENCE | ✅ |
| Desktop / tablet | 1.0 / 0.0 | ✅ |
| Ad schedule | 7 × 08:00–20:00 | ✅ |
| Search Partners / Display | off / off | ✅ |
| Live tracking template | unchanged | ✅ |
| Negative keywords | **657 — none added this batch** | ✅ |
| Winterization sitelinks enabled | 0 | ✅ |

---

## CLEANUP RUN VERIFICATION — negative-keyword conflict resolved

# **RESULT: 28 / 28 PASS**

### Target keyword

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| `[sprinkler head replacement]` status | ENABLED | **ENABLED** | ✅ |
| Match type | EXACT | EXACT | ✅ |
| Text | sprinkler head replacement | unchanged | ✅ |
| Campaign | `20315156610` ENABLED | correct | ✅ |
| Ad group | `151125103616` Sprinkler Repair Near Me, ENABLED | correct | ✅ |
| Final URL | inherited, no override | inherited | ✅ |
| Effective status permits serving | campaign + ad group + keyword all ENABLED | yes | ✅ |
| Duplicate enabled instances | 1 | 1 | ✅ |

Criterion ID **`1442898236`**, resource `customers/8735782888/adGroupCriteria/151125103616~1442898236`.

### Negatives

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| `295473723839` + `301794223657` active | 0 | **0** | ✅ |
| Campaign negative count | 655 (657 − 2) | **655** | ✅ |
| Campaign negatives still blocking the keyword | none | **none** | ✅ |
| Ad-group keyword negatives blocking it | none | **none** | ✅ |
| Any other negative touched | none | **none** | ✅ |
| Replacement negatives added | 0 | **0** | ✅ |

### Preservation — all unchanged

| Check | Actual | |
| --- | --- | --- |
| Daily budget | **$45.00** | ✅ |
| Bidding | TARGET_SPEND | ✅ |
| Search Partners / Display | off / off | ✅ |
| Presence targeting | PRESENCE | ✅ |
| Location criteria | **74** | ✅ |
| Call asset | **(214) 301-3385** ENABLED | ✅ |
| 3 challenger RSAs | ENABLED | ✅ |
| 3 control RSAs | ENABLED | ✅ |
| Serving final URLs | `…repair-b/`, `…repair-a/`, `…repair-a/` — unchanged | ✅ |
| 3 verified callouts | ENABLED | ✅ |
| Discount callout `89872309308` | PAUSED | ✅ |
| `6617381255`, `6886101052`, `6886103719` | primary, in Conversions, ENABLED | ✅ |
| `7717433751`, `7717433754` | still SECONDARY | ✅ |
| Conversion action count | 14 | ✅ |

### Method note

Deactivating a negative by status was attempted first and **rejected by the API**:
`"Cannot set the campaign criterion status for an excluded criteria."` Removal is therefore the
only method the resource supports, and it is reversible by re-adding the same text and match.

### Blocker cleared

The eighth approved keyword is now live. **All 8 keywords, 3 RSAs and 3 callouts from the approved
change manifest are now enabled.**

---

## Blocker status update

The previous strict blocker — *"do not enable or change the WhatConverts import until containment
is completed"* — is **partially lifted**: containment **is** complete, both actions are secondary
and out of bidding.

**One condition remains before any WhatConverts import may be enabled:** the **Google Call
Extension source must be excluded** from the WhatConverts → Google Ads feed. Call-asset calls dial
(214) 301-3385, a WhatConverts number, and are already counted natively by `6617381255`. Without
that exclusion, enabling the import would double-count the account's only working call signal.
That work needs WhatConverts console access, which is still behind a login barrier.

---

## 1. Identity

| Field | Intended | Actual | |
| --- | --- | --- | --- |
| `customer.id` | 8735782888 | 8735782888 | ✅ |
| `customer.descriptive_name` | Pro Green - Dallas - Live | Pro Green - Dallas - Live | ✅ |
| `customer.currency_code` | USD | USD | ✅ |
| `customer.manager` | false | false | ✅ |
| `customer.test_account` | false | false | ✅ |

---

## 2. Conversion actions

| Action | Intended | Actual | |
| --- | --- | --- | --- |
| `6617381255` Calls from Ads | primary ✔, inConv ✔, ENABLED | primary ✔, inConv ✔, ENABLED | ✅ preserved |
| `6886101052` Submit Lead Form | primary ✔, inConv ✔, ENABLED | primary ✔, inConv ✔, ENABLED | ✅ preserved |
| `6886103719` Phone Call Leads | untouched, ENABLED | untouched, ENABLED | ✅ preserved |
| `7717433751` Whatconverts Form | secondary, excluded | **primary, included** | ❌ **did not apply** |
| `7717433754` Whatconverts Calls | secondary, excluded | **primary, included** | ❌ **did not apply** |

The two failures are the **documented API limitation**, not a verification failure — see
`google-ads-execution-log.md` → Incident 1. Both actions still have **zero data ever received**,
so no reporting is currently affected.

**Legacy actions confirmed preserved, none deleted:** `6548857156`, `6548857159`, `6549164075`,
`6555523644`, `6608032928`, `6609874719`, `6616343220`, `6651119909`, `6669693044`.
Account conversion-action count remains **14**.

---

## 3. Devices

| Criterion | Device | Intended | Actual | |
| --- | --- | --- | --- | --- |
| `30000` | DESKTOP | `1.0` (eligible) | **`1.0`** | ✅ |
| `30001` | MOBILE | unset | unset | ✅ |
| `30002` | TABLET | `0.0` (−100%) | **`0.0`** | ✅ |

---

## 4. Negative keywords

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| `cost` PHRASE removed | absent | absent | ✅ |
| `how much` PHRASE removed | absent | absent | ✅ |
| `sprinkler valve replacement cost` EXACT removed | absent | absent | ✅ |
| All 40 additions present | 0 missing | **0 missing** | ✅ |
| Targeted off-service cost negatives preserved | present | present | ✅ |
| **Total campaign negatives** | 657 | **657** | ✅ |

---

## 5. New keywords — created PAUSED

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| New head/valve repair keywords, all PAUSED | 8 | **8** | ✅ |

---

## 6. Challenger RSAs — created PAUSED, URLs untouched

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| 3 challenger RSAs PAUSED | PAUSED ×3 | PAUSED ×3 | ✅ |
| **Serving final URLs unchanged** | `offerdfw…/`, `…/offer-sprinkler-repair-a/`, `…/offer-sprinkler-repair-b/` | identical | ✅ |

Control ads `714659486058`, `797294303667`, `797325463324` all remain **ENABLED**.

---

## 7. Assets

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| "Claim Your Discount" callout | PAUSED | **PAUSED** | ✅ |
| "Licensed & Insured" callout | ENABLED | ENABLED | ✅ |
| 3 new callouts | PAUSED ×3 | PAUSED ×3 | ✅ |
| Winterization sitelinks still enabled | 0 | **0** | ✅ |
| Call asset **(214) 301-3385** | ENABLED, unchanged | ENABLED, unchanged | ✅ |

---

## 8. Tracking templates

| Campaign | Intended | Actual | |
| --- | --- | --- | --- |
| `22027188372` | `utm_id=22027188372` | correct | ✅ |
| `22255200632` | `utm_id=22255200632` | correct | ✅ |
| `22379036365` | `utm_id=22379036365` | correct | ✅ |
| `20315156610` **live** | **byte-identical to backup** | identical | ✅ |

---

## 9. Budget

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| Daily budget `12723712793` | $45.00 | **$45.00**, STANDARD | ✅ |
| August projection | < $2,000 | **$1,269.97** | ✅ |

---

## 10. Unchanged-by-design controls

| Check | Intended | Actual | |
| --- | --- | --- | --- |
| Bidding strategy | TARGET_SPEND | TARGET_SPEND | ✅ |
| Search Partners | off | off | ✅ |
| Display Network | off | off | ✅ |
| Geo targeting | PRESENCE | PRESENCE | ✅ |
| **Location criteria count** | **74** | **74** | ✅ |
| Ad schedule | 7 days × 08:00–20:00 ET | 7 × 08:00–20:00 | ✅ |

---

## What a reviewer should re-check manually

1. **The two WhatConverts conversion actions** — confirm in the Google Ads UI that both still show
   as Primary, and decide whether to switch them to Secondary there.
2. **Desktop spend** over the next 7 days — desktop has been off for a long time and its CPC and
   conversion behaviour are unknown for this account.
3. **Search-term report after 7 days** — confirm the 40 new negatives are blocking what was
   intended and, critically, that **no valid repair query has been suppressed**.
4. **Cost-intent queries** — with `cost` and `how much` removed, watch for genuinely useful
   price-intent traffic appearing, and for any junk that needs a *targeted* negative rather than a
   blanket one.
