# PLAN-GA-LAUNCH-1 — EXECUTION RECEIPT

**Plan** PLAN-GA-LAUNCH-1 · **Fingerprint** `92FFF603CAFD` · **Approved by** Walter Correa
**Approval command received** `APPROVE PLAN-GA-LAUNCH-1 92FFF603CAFD FOR 1521725229`
**Executed** 2026-09-02 13:33:04 America/New_York · **Readback** 13:33:59
**Account** `Softwind Power Washing - Live` / `1521725229` / Power Washing

# 40 resources created, all PAUSED. Nothing enabled. Nothing else changed.

Evidence: `snapshots/launch1-execution-2026-09-02T133304.json` ·
`snapshots/launch1-readback-2026-09-02T133359.json` · `snapshots/launch1-created-ids.json`

---

## 1. Pre-execution gate — ALL PASS

| Step | Result |
|---|---|
| Fresh identity | **PASS** — `Softwind Power Washing - Live` / `1521725229` / manager false / test false / ENABLED / USD / America/New_York |
| Re-read target resources | **PASS** — all 6 target ad groups exist in campaign `24103511039` |
| Duplicate guard | **PASS** — 0 of the 28 planned keywords already existed |
| Recompute fingerprint | **`92FFF603CAFD` — EXACT MATCH** |
| Payload identical to the fingerprinted file | **PASS** |
| `validate_only` keywords | **PASS** — 28 ops, 0 created |
| `validate_only` RSAs | **PASS** — 12 ops, 0 created |

**No mismatch. Proceeded.**

## 2. Execution — atomic, no partial failure

Both batches used `partial_failure = False`, so each was all-or-nothing.

| Batch | Result |
|---|---|
| `AdGroupCriterionService.mutate_ad_group_criteria` | **28 created** |
| `AdGroupAdService.mutate_ad_group_ads` | **12 created** |

**No partial failure occurred. No recovery was needed.**

## 3. Created resource IDs

### 28 keyword criteria (all PAUSED)

| Ad group | Count | Criterion IDs |
|---|---:|---|
| `202870585390` Power Washing | 8 | 21381541, 11244351, 328994395, 448367730, 99754288381, 299856882403, 300840676293, 320045208640 |
| `202870585870` Pressure Washing | 4 | 21381571, 11244361, 75294038799, 75298360239 |
| `202870585910` House Washing | 8 | 301057569810, 315515597254, 341987323402, 342645727874, 297379283655, 306730658772, 346845250713, 394327423399 |
| `202870586310` Soft Washing | 2 | 338961202441, 338961203201 |
| `202870586110` Driveway Pressure Washing | 2 | 328201189095, 328201199015 |
| `202870586150` Patio Pressure Washing | 4 | 326576934122, 326576946202, 449621045684, 421330015623 |

### 12 RSAs (all PAUSED)

| Ad group | Ad IDs |
|---|---|
| `202870585390` Power Washing | 823152917197, 823152917200 |
| `202870585870` Pressure Washing | 823152917203, 823152917206 |
| `202870585910` House Washing | 823152917209, 823152917212 |
| `202870586310` Soft Washing | 823152917215, 823152917218 |
| `202870586110` Driveway Pressure Washing | 823152917221, 823152917224 |
| `202870586150` Patio Pressure Washing | 823152917227, 823152917230 |

## 4. Readback QA — 23 checks, 0 failed

| Check | Result |
|---|---|
| All 28 planned keywords exist | **PASS** — 0 missing |
| All 28 created keywords are **PAUSED** | **PASS** |
| Keyword match types correct (Phrase + Exact) | **PASS** |
| Total positive keywords 214 → **242** | **PASS** |
| All 12 created RSAs read back | **PASS** — 12/12 |
| All 12 created RSAs are **PAUSED** | **PASS** |
| All 12 are RESPONSIVE_SEARCH_AD | **PASS** |
| **No pinning on any created RSA** | **PASS** |
| Every RSA has 15 headlines | **PASS** |
| Every RSA has 4 descriptions | **PASS** |
| **Every headline and description matches the fingerprinted plan exactly** | **PASS** |
| Every RSA Final URL matches the plan | **PASS** |
| Every RSA path1/path2 matches the plan | **PASS** |
| Total ads 54 → **66** | **PASS** |
| Ad group count unchanged at 30 | **PASS** |
| Ad-group negatives still 0 | **PASS** |
| Campaign names, statuses and ceilings unchanged | **PASS** — both $30.00, both ENABLED |
| Retiring campaign `24145053510` still ENABLED and untouched | **PASS** |
| The 5 target ad groups still **PAUSED** — nothing enabled | **PASS** |
| `202870585390` still ENABLED, as before | **PASS** |
| Pre-existing ad count unchanged at 54 | **PASS** |
| Conversion goals unchanged, GET_DIRECTIONS still false | **PASS** |

**Before → after:** positive keywords 214 → 242 · ads 54 → 66 · ad groups 30 → 30 ·
ad-group negatives 0 → 0.

## 5. One item to re-check later

**RSA policy approval status currently reads `UNKNOWN` on all 12 ads.** That is normal for
newly created paused ads — Google has not reviewed them yet. It is **not** a defect and it did
not fail QA. Re-read policy status before enablement; any `DISAPPROVED` ad must be fixed before
its group goes live.

## 6. What was deliberately NOT done

Nothing was enabled. No old resource was paused, edited or removed. No routing negative, no
campaign negative, no CPC change, no budget change, no asset, audience, schedule, conversion,
landing-page, GTM or WhatConverts change. The 30 displaced duplicate keywords in the legacy ad
groups were left exactly as they were — they are retired later in PLAN-GA-LAUNCH-4.

**Campaign `24145053510` remains live and untouched.** It still carries roughly half the
account's delivery and must not be paused until replacements are verified serving.
