#!/usr/bin/env python3
"""Record the owner-accepted exception and the LAUNCH-3B / 3A stages in the ledger."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "clients/softwind-power-washing/plans/2026-09-01-recovery-execution-ledger.yaml"
t = p.read_text(encoding="utf-8")

EXC = """  owner_accepted_exceptions:
    - id: EXC-1
      title: 'OWNER-ACCEPTED TEMPORARY MEASUREMENT EXCEPTION - DOES NOT BLOCK GOOGLE ADS ENABLEMENT'
      recorded: '2026-09-02'
      decided_by: Walter Correa
      decision: >-
        The existing form-conversion behaviour attached to /thank-you/ stays unchanged for
        now. A direct visit to /thank-you/ may fire the current form-conversion event.
        Google Ads enablement is NOT blocked by this.
      accepted_because:
        - The account has recorded zero real Power Washing or Pressure Washing conversions.
        - The controlled form test proved the form submits successfully.
        - >-
          The controlled test proved the Softwind Google Ads conversion event fires after a
          successful submission.
        - The immediate priority is putting the rebuilt inventory into delivery.
        - The thank-you trigger is corrected later via the developer and GTM workflow.
      safeguards_in_force_while_the_exception_stands:
        - Keep Maximize Clicks. Do NOT switch to Maximize Conversions.
        - Do NOT use Target CPA. Do NOT use Target ROAS.
        - Do NOT treat an unverified Google Ads conversion as a qualified lead.
        - Reconcile every reported conversion against WhatConverts and the real lead record.
        - Keep developer ticket DEV-R7A3-04 / ClickUp Task 1 OPEN.
        - Do not change the website, GTM, WhatConverts or any conversion action.
      review_trigger: >-
        Revisit when the gm_power_washing_form_success event ships and the GTM trigger is
        repointed. Until then conversion-based bidding remains prohibited.

  stages:
"""
assert "  stages:\n" in t
t = t.replace("  stages:\n", EXC, 1)

NEW = """    - stage: 2.55
      plan_id: PLAN-GA-LAUNCH-3B
      task: Pre-enablement legacy guard - pause 4 resources that would activate accidentally
      status: APPROVAL READY
      created: '2026-09-02'
      plan_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-3b-legacy-guard.yaml
      fingerprint: B9EDA34DA712
      approval_command: APPROVE PLAN-GA-LAUNCH-3B B9EDA34DA712 FOR 1521725229
      action_count: 4
      object_count: 4
      mutation_count: 4
      validate_only: 'PASS - 2 keyword pauses + 2 ad pauses validated, 0 applied'
      why_it_exists: >-
        The fresh read found FOUR resources ENABLED inside PAUSED ad groups that are NOT in
        the authoritative final inventory. They would begin serving the instant their parent
        ad group is enabled. The standing rule requires stopping and reporting before
        fingerprinting the enablement plan when a new pause mutation is needed.
      resources:
        - '384030528226 house washing company near me PHRASE in 202870585910 - non-final, bucket collapse with house washing near me'
        - '502487923397 house washing company near me EXACT in 202870585910 - same'
        - '819975939528 legacy RSA in 202870586310 Soft Washing - would make four ads in one group'
        - '819975939531 legacy RSA in 202870586310 Soft Washing - same'
      dependency: none - executable on approval
      risk: 'LOW - status-only field mask, fully reversible, nothing goes dark because it enables nothing'
      rollback: set each resource back to ENABLED
      completion_status: NOT STARTED
      next_action: PRESENT FOR APPROVAL - this is the one approval command

    - stage: 2.65
      plan_id: PLAN-GA-LAUNCH-3A
      task: Final Google Ads resource enablement - 45 actions
      status: 'DRAFT - BLOCKED'
      created: '2026-09-02'
      plan_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-3a-enablement.yaml
      supersedes: PLAN-GA-LAUNCH-3
      fingerprint: null
      fingerprint_withheld_because: >-
        A new pause mutation is required first (PLAN-GA-LAUNCH-3B), and the twelve new RSAs
        are still under review.
      action_count: 45
      breakdown: '5 ad groups + 28 keyword criteria + 12 RSAs'
      recalculated_from_live_account: true
      gates:
        - 'GATE-1 PLAN-GA-LAUNCH-3B executed and read back - NOT MET'
        - 'GATE-2 all 12 new RSAs out of review, none DISAPPROVED - NOT MET. All 12 read REVIEW_IN_PROGRESS with zero policy topics, which is normal for newly created paused ads.'
      preflight_passing:
        - all six Final URLs HTTPS 200, no redirect, form present, phone CTA present
        - no BROAD match keyword anywhere in the enable set
        - no DISAPPROVED RSA in the enable set
        - every target belongs to campaign 24103511039
        - campaign 24145053510 still ENABLED, ceilings still $30.00, both MAXIMIZE CLICKS

    - stage: 2.6
      plan_id: PLAN-GA-LAUNCH-2"""
OLD = """    - stage: 2.6
      plan_id: PLAN-GA-LAUNCH-2"""
assert OLD in t
t = t.replace(OLD, NEW, 1)

OLD3 = "      status: 'BLOCKED ON THE GO-LIVE GATE - real IDs now recorded'"
if OLD3 in t:
    t = t.replace(OLD3, "      status: 'SUPERSEDED BY PLAN-GA-LAUNCH-3A (2026-09-02)'", 1)
p.write_text(t, encoding="utf-8")
print("ledger updated")
