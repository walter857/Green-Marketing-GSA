# FUTURE APPROVAL QUEUE — 2026-09-02

**One approval at a time, in dependency order.** An approval command appears **only** where the
plan has exact current resource IDs, known current and proposed values, non-zero executable
actions, a passing `validate_only` where applicable, a current fingerprint, and no unresolved
dependency.

## Ready now

### 1. PLAN-GA-LAUNCH-2A — Final ad-group routing negatives

| | |
|---|---|
| Purpose | Enforce one-owner-per-keyword across the six live ad groups |
| Status | **APPROVAL READY** |
| Dependency | **MET** — all six owner ad groups enabled and verified 2026-09-02 17:39 |
| Actions / Objects / Mutations | **103 / 103 / 103** |
| Fingerprint | **`4A82B3B7C1EA`** |
| `validate_only` | PASS — 103 create operations validated, 0 created |
| Risk | LOW — every criterion collision-tested against the live inventory; 0 self-blocking |
| Rollback | Remove the added ad-group negative criteria |
| Earliest safe execution | **Now.** Owner groups are live. |

```
APPROVE PLAN-GA-LAUNCH-2A 4A82B3B7C1EA FOR 1521725229
```

> **A judgement call worth your attention.** These 103 negatives are safe and validated, but the
> six ad groups have not yet served a single impression. Waiting for real routing evidence would
> tell us which negatives are actually needed rather than which are theoretically correct. The
> plan is ready whenever you want it; my recommendation is to let it run a few days first.

## Blocked or deferred — no approval command

| # | Plan | Purpose | Status | Dependency | Actions | Fingerprint | Earliest safe point |
|---|---|---|---|---|---:|---|---|
| 2 | **PLAN-GA-NEG-1** | Universal traffic-quality negatives | DRAFT | 5 candidates all have 0 clicks and $0 spend | 5 | none | 14-day checkpoint |
| 3 | **PLAN-GA-BID-1** | Evidence-based CPC ceiling | BLOCKED | needs post-launch billable clicks + landing-page fix | 2 | none | 3-day checkpoint at the earliest |
| 4 | **PLAN-R7A1-GTM** | GTM form-measurement repair | BLOCKED | no Tag Manager credential | ~5 | none | when GTM read access exists |
| 5 | **PLAN-R7A2-WHATCONVERTS** | DNI and call attribution | BLOCKED | `WHATCONVERTS_API_TOKEN` is empty | ~6 | none | when WhatConverts read access exists |
| 6 | **PLAN-GA-ASSET-1** | Asset completion | BLOCKED | business identity, rights-cleared images, answered hours | 6 | none | when client inputs arrive |
| 7 | **PLAN-GA-AUD-1** | Audience observations | DEFERRED | all lists below the ~1,000 Search minimum (largest is 210) | 3 | none | when a list crosses the threshold |
| 8 | **PLAN-GA-RETIRE-1** | Legacy retirement, campaign `24145053510` last | BLOCKED | replacements must serve and be verified first | ~30 | none | after 7–14 days of clean serving |
| 9 | **PLAN-R7A4-CROSS-ACCOUNT** | Sibling tag scoping | BLOCKED | needs a separate sibling-account work order and approval | ~2 | none | after that work order exists |
| 10 | **Post-repair form test** | Re-verify conversion after website fixes | BLOCKED | website P0 work must ship | ~8 | none | after ClickUp P0 tasks land |

## Not fingerprinted, by rule

Developer tickets · provisional plans · blocked plans · placeholder plans · zero-action plans ·
cross-account actions without their own work order. Superseded: `PLAN-GA-LAUNCH-2`,
`PLAN-GA-LAUNCH-3`, `PLAN-GA-LAUNCH-4` (replaced by 2A / 3A / RETIRE-1). Void: `D04DBC638033`.
