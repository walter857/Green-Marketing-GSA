#!/usr/bin/env python3
"""Write the 3C receipt, finalise PLAN-GA-LAUNCH-3A, and correct the ledger."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLN = ROOT / "clients/softwind-power-washing/plans"
REC = ROOT / "clients/softwind-power-washing/receipts"

(REC / "2026-09-02-plan-ga-launch-3c-execution-receipt.md").write_text("""# PLAN-GA-LAUNCH-3C — EXECUTION RECEIPT

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
""", encoding="utf-8")

p = PLN / "2026-09-02-plan-ga-launch-3a-enablement.yaml"
t = p.read_text(encoding="utf-8")
t = t.replace("""  approval_status: NOT APPROVED
  execution_status: 'DO NOT EXECUTE - BLOCKED'
  fingerprint: null""",
"""  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: F91589D9EA2A
  canonical_sha256_full: f91589d9ea2af9ad556836e19f7b3d57dfe7830e5d17fa3864679087b24ed459
  approval_command: APPROVE PLAN-GA-LAUNCH-3A F91589D9EA2A FOR 1521725229
  payload_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-3a-payload.json
  fingerprint_history:
    - code: F91589D9EA2A
      state: VALID - THIS IS THE APPROVAL FINGERPRINT
      note: >-
        First generated 2026-09-02 16:51 when its validate_only failed on the
        3-RSA-per-ad-group limit. The PAYLOAD was always correct; only the account state
        blocked it. PLAN-GA-LAUNCH-3C removed the blocker, the identical payload re-derives
        the identical code, and all three batches now validate cleanly. An earlier note
        calling it VOID was wrong and is corrected here.
    - code: D04DBC638033
      state: VOID - DO NOT HONOUR
      note: >-
        A 47-action variant produced by a rebuild that selected ALL paused keywords in the
        six ad groups instead of only those created by PLAN-GA-LAUNCH-1. It wrongly included
        criteria 384030528226 and 502487923397, the two `house washing company near me`
        keywords PLAN-GA-LAUNCH-3B had just paused. Executing it would have undone 3B.
  scope_rule: >-
    The enable set is strictly the resource IDs recorded in
    snapshots/launch1-created-ids.json - 28 keyword criteria and 12 ads - plus the five
    paused ad groups. No other paused resource in these ad groups is touched.""")
t = t.replace("""  blocking_gates:
    - id: GATE-1
      requirement: PLAN-GA-LAUNCH-3B executed and read back
      state: NOT MET""",
"""  gates:
    - id: GATE-1
      requirement: PLAN-GA-LAUNCH-3B executed and read back
      state: MET 2026-09-02 16:50""")
t = t.replace("""    - id: GATE-2
      requirement: All twelve new RSAs out of review and none DISAPPROVED
      state: NOT MET""",
"""    - id: GATE-2
      requirement: All twelve new RSAs out of review and none DISAPPROVED
      state: MET 2026-09-02 - all 12 APPROVED / REVIEWED
    - id: GATE-3
      requirement: >-
        PLAN-GA-LAUNCH-3C executed - the 3-RSA-per-ad-group limit cleared in 202870585390
      state: MET 2026-09-02 17:12
      detail: >-
        Projected enabled RSAs per ad group after enablement is now 2 in all six groups.""")
t = t.replace("""  preflight_checks_already_passing:""",
"""  validate_only_2026_09_02_after_3c:
    ad_groups: 'PASS - 5 enable operations validated, 0 applied'
    keywords: 'PASS - 28 enable operations validated, 0 applied'
    ads: 'PASS - 12 enable operations validated, 0 applied'

  preflight_checks_already_passing:""")
p.write_text(t, encoding="utf-8")

# ---- ledger ----
lp = PLN / "2026-09-01-recovery-execution-ledger.yaml"
lt = lp.read_text(encoding="utf-8")
lt = lt.replace("""      task: RSA limit guard - pause the 2 legacy Power Washing RSAs
      status: APPROVAL READY""",
"""      task: RSA limit guard - pause the 2 legacy Power Washing RSAs
      status: COMPLETE - EXECUTED 2026-09-02""")
lt = lt.replace("""      completion_status: NOT STARTED
      next_action: PRESENT FOR APPROVAL - this is the one approval command

    - stage: 2.65""",
"""      completion_status: COMPLETE - EXECUTED 2026-09-02 17:12 ET
      approval_received: 'APPROVE PLAN-GA-LAUNCH-3C 40F940130E6D FOR 1521725229'
      execution_result: '2 legacy RSAs paused. Readback 4 checks, 0 failed. ENABLED ads 42 -> 40.'
      effect: >-
        Projected enabled RSAs per ad group after enablement is now 2 in all six groups. The
        3-RSA limit that blocked PLAN-GA-LAUNCH-3A is cleared.
      evidence_file: clients/softwind-power-washing/receipts/2026-09-02-plan-ga-launch-3c-execution-receipt.md
      next_action: NONE - complete

    - stage: 2.65""")
lt = lt.replace("""        - 'GATE-3 PLAN-GA-LAUNCH-3C executed - NOT MET. New gate, discovered by validate_only: the 3-RSA-per-ad-group limit blocks the ad-enable batch until the two legacy Power Washing RSAs are paused.'
      voided_fingerprint: >-
        F91589D9EA2A was generated for 3A before the RSA-limit failure was understood. It is
        VOID and must never be honoured - its validate_only FAILED. 3A is re-fingerprinted
        against a fresh read after 3C executes.""",
"""        - 'GATE-3 PLAN-GA-LAUNCH-3C executed - MET 2026-09-02 17:12'
      status_2026_09_02_final: APPROVAL READY
      fingerprint_final: F91589D9EA2A
      approval_command_final: APPROVE PLAN-GA-LAUNCH-3A F91589D9EA2A FOR 1521725229
      validate_only_final: 'PASS on all three batches - 5 ad groups, 28 keywords, 12 ads, 0 applied'
      fingerprint_correction: >-
        An earlier ledger note called F91589D9EA2A VOID. THAT NOTE WAS WRONG and is retracted.
        The payload was always correct - 5 ad groups + 28 keywords + 12 RSAs. Its first
        validate_only failed only because of the live 3-RSA-per-ad-group limit, which
        PLAN-GA-LAUNCH-3C has now removed. The identical payload re-derives the identical
        code and validates cleanly.
      voided_fingerprint: >-
        D04DBC638033 is VOID - DO NOT HONOUR. A 47-action variant from a rebuild that selected
        ALL paused keywords in the six ad groups rather than only those created by
        PLAN-GA-LAUNCH-1. It wrongly included criteria 384030528226 and 502487923397, the two
        `house washing company near me` keywords 3B had just paused; executing it would have
        undone 3B.""")
lp.write_text(lt, encoding="utf-8")
print("wrote 3C receipt, finalised 3A, corrected ledger")
