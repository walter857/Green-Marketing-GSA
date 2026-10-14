# PLAN-GA-LAUNCH-3B — EXECUTION RECEIPT

**Plan** PLAN-GA-LAUNCH-3B · **Fingerprint** `B9EDA34DA712` · **Approved by** Walter Correa
**Executed** 2026-09-02 16:50:59 America/New_York
**Account** `Softwind Power Washing - Live` / `1521725229`

# 4 legacy resources paused. Nothing created, nothing enabled.

Evidence: `snapshots/launch3b-execution-2026-09-02T165059.json`

## Pre-execution gate — all pass

Identity **PASS** · all four targets re-read and confirmed **ENABLED** with matching text and
match type · fingerprint recomputed **`B9EDA34DA712`, exact match** · payload identical to the
fingerprinted file · `validate_only` **PASS** on both batches.

## Execution — atomic per batch

| Batch | Result |
|---|---|
| Keyword pauses | **2 paused** |
| Ad pauses | **2 paused** |

No partial failure.

| Resource | Ad group | Before | After |
|---|---|---|---|
| `384030528226` `house washing company near me` PHRASE | 202870585910 | ENABLED | **PAUSED** |
| `502487923397` `house washing company near me` EXACT | 202870585910 | ENABLED | **PAUSED** |
| `819975939528` legacy RSA | 202870586310 | ENABLED | **PAUSED** |
| `819975939531` legacy RSA | 202870586310 | ENABLED | **PAUSED** |

## Readback QA — 8 checks, 0 failed

Both guard keywords **PAUSED** · both guard ads **PAUSED** · ENABLED ad groups still **12** ·
ENABLED keywords **214 → 212** · ENABLED ads **44 → 42** · the 28 new keywords still PAUSED ·
both campaigns still **ENABLED, $30.00, TARGET_SPEND** · campaign `24145053510` untouched.

## GATE-2 cleared during this run

All **12 new RSAs are now `APPROVED` / `REVIEWED`, zero DISAPPROVED.** They were
`REVIEW_IN_PROGRESS` at the previous read. Google completed review in the interval.

**Legacy activation conflicts are now ZERO** — re-verified by a fresh read after execution.
