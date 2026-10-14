# PLAN-J2A GEO QA REPORT

**Account:** Softwind Power Washing - Live (1521725229) - Power Washing
**Approval:** `APPROVE PLAN-J2A 529FE7F9386D FOR 1521725229`
**Executed:** 2026-08-26T17:49:03.446865-04:00
**Result:** SUCCEEDED - 144 criteria created, 0 removed, QA passed

## Pre-flight gates

| Gate | Result |
|---|---|
| Fresh identity (name, ID, manager, test, currency, tz) | 6/6 PASS |
| Drift vs Stage 1 (budgets, bidding, CPC ceiling, Presence, 8 targets, 0 negatives) | 16/16 PASS |
| Fingerprint recomputed from file | `529FE7F9386D` == approved |
| Operation build (144 ops, 72 distinct per campaign) | PASS |
| **validate_only dry run** | **PASSED - Google accepted all 144** |
| Execution mode | atomic, `partial_failure=False` |

## Result

| Campaign | Before | Created | After | Removed |
|---|---|---|---|---|
| 24103511039 Power Washing | 8 | 72 | **80** | 0 |
| 24145053510 Power Washing #2 | 8 | 72 | **80** | 0 |

Negative location criteria: **0 on both** - PLAN-J2B is not approved and was not executed.

## Readback assertions - 24/24 PASS

- Positive count == 80 on each campaign
- All 8 pre-existing targets still present on each campaign
- All 72 planned targets created on each campaign
- No unexpected extra target
- Every positive target canonical name contains ",New York,United States"
- Every positive target status ENABLED
- **Zero non-New-York targets anywhere in the account**
- PRESENCE unchanged (positive and negative) on both campaigns
- Budgets unchanged, bidding still TARGET_SPEND, no CPC ceiling added

## Collateral-change check - 12/12 PASS

Keywords 214, ads 54, campaign negatives 94, ad schedules 12, conversion actions 4,
campaign assets 20. Search Partners OFF, Display OFF, budgets and bidding untouched
on both campaigns.

## Source lineage

- File: `sources/Location report (2).csv`
- SHA-256: `95eb808ba20cb2fd788c4742e3186bb03ff4b92382368ed4016536655a71634c`
- 78 rows -> 75 New York, 3 non-New-York (excluded), 0 duplicates
- 75 resolved, 0 unresolved, 72 net-new, 3 already live
- 5 live targets not in the CSV were KEPT unchanged (Bellmore, Islip hamlet,
  Syosset, Salisbury, North Hempstead). Removal was never proposed.

## Post-geo pacing (same-minute, 2026-08-26T17:49:42.783579-04:00)

| | |
|---|---|
| MTD spend S | $253.39 |
| Remaining R | $2246.61 |
| Remaining days D | 6 |
| Remaining hours H | 126.17 |
| Required 24h pace | $427.34 |
| Drift vs PLAN-I1C inputs | $0.00 - none |

PLAN-I1C fingerprint `8CC6CABFC74F` remains valid.
