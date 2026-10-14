# PLAN-GA-LAUNCH-3C — EXECUTION RECEIPT

**Plan** PLAN-GA-LAUNCH-3C · **Fingerprint** `40F940130E6D` · **Approved by** Walter Correa
**Executed** 2026-09-02 17:12 America/New_York
**Account** `Softwind Power Washing - Live` / `1521725229`

# 2 legacy Power Washing RSAs paused. The 3-RSA limit is cleared.

Evidence: `snapshots/launch3c-execution-2026-09-02T171203.json`

## Gate and execution

Identity **PASS** · both targets re-read and confirmed ENABLED in `202870585390` · fingerprint
recomputed **`40F940130E6D`, exact match** · payload identical to the fingerprinted file ·
`validate_only` **PASS** · atomic mutate, **2 paused**, no partial failure.

| Resource | Ad group | Before → After |
|---|---|---|
| `819975939342` legacy RSA | 202870585390 Power Washing | ENABLED → **PAUSED** |
| `819975939345` legacy RSA | 202870585390 Power Washing | ENABLED → **PAUSED** |

## Readback — 4 checks, 0 failed

Both RSAs **PAUSED** · ENABLED ads **42 → 40** · ENABLED ad groups still **12** · both campaigns
**ENABLED at $30.00**.

**Projected enabled RSAs per ad group after enablement is now 2 everywhere** — the limit that
blocked PLAN-GA-LAUNCH-3A is resolved.

## A scoping error I caught in my own rebuild

When regenerating PLAN-GA-LAUNCH-3A immediately after this execution, my first query selected
*all* paused keywords in the six ad groups and returned **30**, not 28. The two extras were
`house washing company near me` PHRASE `384030528226` and EXACT `502487923397` — the criteria
**PLAN-GA-LAUNCH-3B had just paused on purpose**.

Enabling them would have silently undone 3B and reactivated non-final keywords. The enable set
is now scoped strictly to the resource IDs created by PLAN-GA-LAUNCH-1
(`snapshots/launch1-created-ids.json`), and both guard criteria are explicitly excluded.

That produced a wrong 47-action fingerprint, **`D04DBC638033`**, which is **VOID and must never
be honoured**.

## Fingerprint record — correction

`F91589D9EA2A` was earlier described as void because its `validate_only` failed. **That
description was wrong.** The payload was always correct — 5 ad groups + 28 keywords + 12 RSAs.
It failed only because of a live-account constraint, the 3-RSA-per-ad-group limit, which this
plan has now removed. The identical payload re-derives the identical fingerprint and now
validates cleanly on all three batches. **`F91589D9EA2A` is valid and is the approval
fingerprint for PLAN-GA-LAUNCH-3A.**

| Fingerprint | Status |
|---|---|
| **`F91589D9EA2A`** | **VALID** — 45 actions, correct scope, validate_only PASS |
| `D04DBC638033` | **VOID** — 47 actions, wrongly included the two 3B guard keywords |
