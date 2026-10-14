#!/usr/bin/env python3
"""Write the 3B execution receipt, PLAN-GA-LAUNCH-3C, and update the ledger."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLN = ROOT / "clients/softwind-power-washing/plans"
REC = ROOT / "clients/softwind-power-washing/receipts"

(REC / "2026-09-02-plan-ga-launch-3b-execution-receipt.md").write_text("""# PLAN-GA-LAUNCH-3B — EXECUTION RECEIPT

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
""", encoding="utf-8")

(PLN / "2026-09-02-plan-ga-launch-3c-rsa-limit-guard.yaml").write_text("""# PLAN-GA-LAUNCH-3C - RSA LIMIT GUARD (POWER WASHING AD GROUP)
#
# STATUS: NOT APPROVED. DO NOT EXECUTE.
# Fingerprint 40F940130E6D  (recomputed twice, identical)
# validate_only PASSED. ZERO resources changed.

change_plan:
  plan_id: PLAN-GA-LAUNCH-3C
  plan_title: RSA limit guard - pause the two legacy Power Washing RSAs
  approval_type: PAUSE
  priority: P0
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: 40F940130E6D
  canonical_sha256_full: 40f940130e6d3aec5168e3380a4e87dcc943f077eb06f47163ab35f50a5805de
  approval_command: APPROVE PLAN-GA-LAUNCH-3C 40F940130E6D FOR 1521725229
  payload_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-3c-payload.json

  target:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '1521725229'
    manager_customer_id: '3373711342'
    exact_service: Power Washing
    campaign_id: '24103511039'
    ad_group_id: '202870585390'

  counts:
    action_count: 2
    object_count: 2
    mutation_count: 2
    creations: 0
    enablements: 0

  why_this_plan_exists:
    discovered: >-
      2026-09-02 during validate_only for PLAN-GA-LAUNCH-3A. The ad-enable batch failed with
      resource_count_limit_exceeded_error RESOURCE_LIMIT at operations[1].
    root_cause: >-
      Google Ads limits an ad group to THREE enabled responsive search ads. Ad group
      202870585390 Power Washing already has TWO enabled legacy RSAs (819975939342 and
      819975939345). Enabling both new replacement RSAs would make FOUR.
    proof:
      - Each of the 12 ad-enable operations passes validate_only INDIVIDUALLY.
      - The batch of 12 FAILS, and the error points at operations[1], the second Power
        Washing ad.
      - Per-ad-group projection - only 202870585390 lands at 4; the other five land at 2
        because their legacy ads are already paused.
      - 'A combined request of 2 pauses + 12 enables validates cleanly - PASS.'
    scope_note: >-
      This is NOT optional retirement. Without it PLAN-GA-LAUNCH-3A physically cannot
      execute. It is kept out of the enablement plan because the standing rule says an
      old-resource pause must not ride inside an enablement approval.

  actions:
    - action: C-1
      type: ad_group_ad
      campaign_id: '24103511039'
      ad_group_id: '202870585390'
      ad_group_name: Power Washing Near Me
      resource_id: '819975939342'
      current_status: ENABLED
      proposed_status: PAUSED
      field_mask: status
      policy: APPROVED AND ELIGIBLE
      final_url: https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/
      reason: >-
        One of the two legacy RSAs occupying the 3-RSA slot limit. It is also the creative
        flagged since 2026-08-31 for replacement - 9 of its 15 headlines name three hamlets,
        which is the direct cause of BELOW_AVERAGE ad relevance on this ad group.
      rollback: set status back to ENABLED
    - action: C-2
      type: ad_group_ad
      campaign_id: '24103511039'
      ad_group_id: '202870585390'
      ad_group_name: Power Washing Near Me
      resource_id: '819975939345'
      current_status: ENABLED
      proposed_status: PAUSED
      field_mask: status
      policy: APPROVED AND ELIGIBLE
      final_url: https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/
      reason: same as C-1
      rollback: set status back to ENABLED

  coverage_gap_disclosure:
    gap: >-
      Ad group 202870585390 Power Washing is currently ENABLED and these are its only two
      enabled ads. Pausing them leaves that ad group with no servable ad until
      PLAN-GA-LAUNCH-3A enables the two approved replacements.
    duration: 'as long as it takes to approve and execute PLAN-GA-LAUNCH-3A'
    cost_assessment: >-
      Low. These two ads produced ZERO leads across the account's 19 lifetime billable
      clicks and carry BELOW_AVERAGE ad relevance. The rest of the account keeps serving -
      campaign 24145053510 is untouched and its six ad groups are unaffected.
    recommendation: >-
      Approve PLAN-GA-LAUNCH-3A in the same sitting. Its fingerprint is regenerated against
      a fresh read immediately after 3C executes, so the gap is minutes.

  what_this_plan_does_not_do:
    - creates nothing, enables nothing, deletes nothing
    - no campaign pause, rename, budget, CPC or bidding change
    - no keyword, negative, audience, asset, location, schedule or conversion change
    - no website, GTM or WhatConverts change
    - does not touch campaign 24145053510

  validation:
    validate_only: 'PASS - 2 pause operations validated, 0 applied'
    fingerprint_recomputed_twice: true
    field_mask: 'status only'
  dependency: NONE - executable on approval
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---- ledger ----
p = PLN / "2026-09-01-recovery-execution-ledger.yaml"
t = p.read_text(encoding="utf-8")
OLD = """      completion_status: NOT STARTED
      next_action: PRESENT FOR APPROVAL - this is the one approval command

    - stage: 2.65"""
NEW = """      completion_status: COMPLETE - EXECUTED 2026-09-02 16:50:59 ET
      approval_received: 'APPROVE PLAN-GA-LAUNCH-3B B9EDA34DA712 FOR 1521725229'
      execution_result: '4 resources paused. Readback 8 checks, 0 failed.'
      before_after:
        enabled_keywords: '214 -> 212'
        enabled_ads: '44 -> 42'
        enabled_ad_groups: '12 -> 12 (unchanged)'
      gate2_cleared_during_this_run: >-
        All 12 new RSAs moved from REVIEW_IN_PROGRESS to APPROVED / REVIEWED, zero
        DISAPPROVED. Legacy activation conflicts re-verified at ZERO.
      evidence_file: clients/softwind-power-washing/receipts/2026-09-02-plan-ga-launch-3b-execution-receipt.md
      next_action: NONE - complete

    - stage: 2.58
      plan_id: PLAN-GA-LAUNCH-3C
      task: RSA limit guard - pause the 2 legacy Power Washing RSAs
      status: APPROVAL READY
      created: '2026-09-02'
      plan_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-3c-rsa-limit-guard.yaml
      fingerprint: 40F940130E6D
      approval_command: APPROVE PLAN-GA-LAUNCH-3C 40F940130E6D FOR 1521725229
      action_count: 2
      object_count: 2
      mutation_count: 2
      validate_only: 'PASS - 2 pause operations validated, 0 applied'
      why_it_exists: >-
        Discovered during validate_only for PLAN-GA-LAUNCH-3A. Google Ads limits an ad group
        to THREE enabled RSAs. Ad group 202870585390 already has two enabled legacy RSAs, so
        enabling both replacements would make four and the batch fails with
        resource_count_limit_exceeded_error RESOURCE_LIMIT at operations[1]. Only that one
        ad group is affected; the other five land at two because their legacy ads are paused.
      resources:
        - '819975939342 legacy RSA in 202870585390 - hamlet-heavy copy, BELOW_AVERAGE ad relevance'
        - '819975939345 legacy RSA in 202870585390 - same'
      coverage_gap: >-
        202870585390 has no other enabled ad, so it goes dark until 3A runs. Low cost - these
        two produced zero leads across 19 lifetime billable clicks. Approve 3A in the same
        sitting to keep the gap to minutes.
      dependency: none - executable on approval
      completion_status: NOT STARTED
      next_action: PRESENT FOR APPROVAL - this is the one approval command

    - stage: 2.65"""
assert OLD in t
t = t.replace(OLD, NEW, 1)

OLD2 = """      gates:
        - 'GATE-1 PLAN-GA-LAUNCH-3B executed and read back - NOT MET'
        - 'GATE-2 all 12 new RSAs out of review, none DISAPPROVED - NOT MET. All 12 read REVIEW_IN_PROGRESS with zero policy topics, which is normal for newly created paused ads.'"""
NEW2 = """      gates:
        - 'GATE-1 PLAN-GA-LAUNCH-3B executed and read back - MET 2026-09-02'
        - 'GATE-2 all 12 new RSAs out of review, none DISAPPROVED - MET 2026-09-02, all 12 APPROVED / REVIEWED'
        - 'GATE-3 PLAN-GA-LAUNCH-3C executed - NOT MET. New gate, discovered by validate_only: the 3-RSA-per-ad-group limit blocks the ad-enable batch until the two legacy Power Washing RSAs are paused.'
      voided_fingerprint: >-
        F91589D9EA2A was generated for 3A before the RSA-limit failure was understood. It is
        VOID and must never be honoured - its validate_only FAILED. 3A is re-fingerprinted
        against a fresh read after 3C executes."""
assert OLD2 in t
t = t.replace(OLD2, NEW2, 1)
p.write_text(t, encoding="utf-8")
print("wrote 3B receipt, 3C plan, ledger updated")
