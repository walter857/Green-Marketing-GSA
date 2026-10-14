# PLAN-GA-LAUNCH-3A — EXECUTION RECEIPT

**Plan** PLAN-GA-LAUNCH-3A · **Fingerprint** `F91589D9EA2A` · **Approved by** Walter Correa
**Executed** 2026-09-02 17:39:49 America/New_York · **Readback** 17:41
**Account** `Softwind Power Washing - Live` / `1521725229` / Power Washing

# THE REBUILT INVENTORY IS LIVE. 45 resources enabled. 29/29 readback assertions pass.

Evidence: `snapshots/launch3a-execution-2026-09-02T173949.json` ·
`snapshots/launch3a-readback-*.json` · `snapshots/launch3a-resource-ids.json`

---

## 1. Pre-execution gate — 20 checks, all pass

Identity · both campaigns ENABLED · both TARGET_SPEND · both ceilings $30.00 · 3B and 3C guards
still paused · **all 12 new RSAs APPROVED** · the 2 House Washing guard keywords PAUSED · the 4
legacy RSAs from 3B/3C PAUSED · the 28 target keywords PAUSED · the 12 target RSAs PAUSED · five
target ad groups PAUSED · `202870585390` already ENABLED · no target resource ID changed ·
**fingerprint `F91589D9EA2A` exact match, payload byte-identical** · no guard keyword, legacy ad
or foreign resource in the payload · `validate_only` **PASS** on all three batches.

## 2. Execution — atomic per batch, `partial_failure = false`

| Batch | Result |
|---|---|
| Ad groups | **5 enabled** |
| Keyword criteria | **28 enabled** |
| Responsive search ads | **12 enabled** |

**No partial failure. No recovery needed.**

## 3. Live serving structure — campaign 24103511039

| # | Final ad group | Ad group ID | Status | Enabled RSAs |
|---|---|---|---|---:|
| 1 | Power Washing | `202870585390` | **ENABLED** | 2 |
| 2 | Pressure Washing | `202870585870` | **ENABLED** | 2 |
| 3 | House Washing | `202870585910` | **ENABLED** | 2 |
| 4 | Soft Washing | `202870586310` | **ENABLED** | 2 |
| 5 | Driveway Pressure Washing | `202870586110` | **ENABLED** | 2 |
| 6 | Patio Pressure Washing | `202870586150` | **ENABLED** | 2 |

## 4. Readback QA — 29 assertions, 0 failed

All six ad groups ENABLED · all 28 new keywords ENABLED with correct Phrase/Exact match · **no
Broad Match enabled anywhere** · both guard keywords still PAUSED in `202870585910` · all 12 new
RSAs ENABLED and still APPROVED · 15 headlines and 4 descriptions each · **no pinning** · every
Final URL and display path matches the approved plan · **every headline and description matches
the approved copy exactly** · exactly two enabled RSAs per final ad group, none above three · all
six legacy RSAs from 3B/3C still PAUSED · campaign `24145053510` ENABLED and unchanged · budgets
unchanged $41.50 / $41.11 · both ceilings $30.00 · both Maximize Clicks · Search Partners OFF ·
Display OFF · AI Max OFF · Presence targeting active · Connecticut still excluded on both ·
conversion goals unchanged · assets unchanged at 20 links · **no routing negative added** · no
audience added · no demographic criteria.

**Account totals:** ad groups 30 (17 enabled) · keyword rows 242 (240 enabled, 2 paused guards) ·
ads 66 (52 enabled).

## 5. A readback bug I caught and corrected

My first readback reported two failures: "only 18 of 28 keywords" and "guard keywords ENABLED".
**Both were artifacts of my own query, not account defects.**

`ad_group_criterion.criterion_id` is **not unique for keywords** — the same ID is reused by every
ad group carrying the same text and match type. Keying the readback dictionary on `criterion_id`
alone collapsed 242 real rows into 125 and let a different ad group's row overwrite the one being
checked.

Re-verified with the correct `(ad_group_id, criterion_id)` key:

- **242** keyword rows, not 125
- **28 of 28** created keywords present and ENABLED
- Both guards in `202870585910` **PAUSED**. The identical criterion IDs also exist in ad group
  `198082079463`, a legacy campaign-B group that was never in scope and is untouched.

The readback script is fixed and now returns 29/29.

## 6. What was deliberately not done

Nothing created. Nothing paused. No campaign paused or renamed. No budget, CPC, bidding, negative
keyword, audience, asset, schedule, location, conversion, website, GTM or WhatConverts change.
**Campaign `24145053510` remains ENABLED and untouched** as the transition campaign.
