#!/usr/bin/env python3
"""Write PLAN-GA-LAUNCH-3B, PLAN-GA-LAUNCH-3A, update LAUNCH-2 with real IDs, ledger."""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLN = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
B = json.loads(Path(sorted(glob.glob(str(SNAP / "launch3-build-*.json")))[-1])
               .read_text(encoding="utf-8"))
A = B["plan_3a"]["actions"]

kw_rows = "\n".join(
    f"    - {{action: A-{i+1:02d}, type: ad_group_criterion, campaign_id: '24103511039', "
    f"ad_group_id: '{x['ad_group_id']}', resource_id: '{x['resource_id']}', "
    f"keyword: '{x['keyword_text']}', match_type: {x['match_type']}, "
    f"current: PAUSED, proposed: ENABLED, policy: {x['policy']}}}"
    for i, x in enumerate([y for y in A if y["type"] == "ad_group_criterion"]))
ad_rows = "\n".join(
    f"    - {{action: R-{i+1:02d}, type: ad_group_ad, campaign_id: '24103511039', "
    f"ad_group_id: '{x['ad_group_id']}', resource_id: '{x['resource_id']}', "
    f"current: PAUSED, proposed: ENABLED, policy: '{x['policy']}', "
    f"final_url: '{x['final_url']}'}}"
    for i, x in enumerate([y for y in A if y["type"] == "ad_group_ad"]))
ag_rows = "\n".join(
    f"    - {{action: G-{i+1}, type: ad_group, campaign_id: '24103511039', "
    f"resource_id: '{x['resource_id']}', final_group: '{x['final_group']}', "
    f"live_name: '{x['name']}', current: PAUSED, proposed: ENABLED}}"
    for i, x in enumerate([y for y in A if y["type"] == "ad_group"]))

(PLN / "2026-09-02-plan-ga-launch-3b-legacy-guard.yaml").write_text(f"""# PLAN-GA-LAUNCH-3B - PRE-ENABLEMENT LEGACY GUARD
#
# STATUS: NOT APPROVED. DO NOT EXECUTE.
# Fingerprint {B['plan_3b']['fingerprint']}  (recomputed twice, identical)
# validate_only PASSED. ZERO resources changed.
#
# WHY THIS PLAN EXISTS: the fresh read found FOUR resources that are ENABLED inside
# PAUSED ad groups and are NOT part of the authoritative final inventory. They would
# begin serving the instant their parent ad group is enabled. The standing rule is to
# STOP and report before fingerprinting the enablement plan when a new pause mutation
# is required. This is that pause, isolated into its own approval.

change_plan:
  plan_id: PLAN-GA-LAUNCH-3B
  plan_title: Pre-enablement legacy guard
  approval_type: PAUSE
  priority: P0
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: {B['plan_3b']['fingerprint']}
  canonical_sha256_full: {B['plan_3b']['canonical_sha256_full']}
  approval_command: {B['plan_3b']['approval_command']}
  payload_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-3b-payload.json

  target:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '1521725229'
    manager_customer_id: '3373711342'
    exact_service: Power Washing
    campaign_id: '24103511039'

  counts:
    action_count: 4
    object_count: 4
    mutation_count: 4
    creations: 0
    enablements: 0
    campaign_changes: 0
    budget_changes: 0
    cpc_changes: 0

  validation:
    validate_only_keywords: '{B['plan_3b']['validate_only']['keywords']}'
    validate_only_ads: '{B['plan_3b']['validate_only']['ads']}'
    conflict_set_matches_fresh_read: true
    fingerprint_recomputed_twice: true
    field_mask: 'status only - nothing else is touched on any resource'

  actions:
    - action: P-1
      type: ad_group_criterion
      ad_group_id: '202870585910'
      ad_group_name: House Washing Company Near Me
      resource_id: '384030528226'
      keyword: house washing company near me
      match_type: PHRASE
      current_status: ENABLED
      proposed_status: PAUSED
      policy: APPROVED / ELIGIBLE
      reason: >-
        NOT in the authoritative final inventory. It was removed for bucket collapse -
        it shares the 40/mo Planner bucket with the owned text `house washing near me`.
        It is ENABLED inside a PAUSED ad group, so enabling House Washing would activate
        it and create intra-ad-group self-competition against its own owner text.
      rollback: set status back to ENABLED
    - action: P-2
      type: ad_group_criterion
      ad_group_id: '202870585910'
      ad_group_name: House Washing Company Near Me
      resource_id: '502487923397'
      keyword: house washing company near me
      match_type: EXACT
      current_status: ENABLED
      proposed_status: PAUSED
      policy: APPROVED / ELIGIBLE
      reason: same as P-1
      rollback: set status back to ENABLED
    - action: P-3
      type: ad_group_ad
      ad_group_id: '202870586310'
      ad_group_name: Soft House Washing Near Me
      resource_id: '819975939528'
      current_status: ENABLED
      proposed_status: PAUSED
      policy: APPROVED AND ELIGIBLE
      final_url: https://offer.softwindli.com/soft-house-washing/
      reason: >-
        A legacy RSA not created by PLAN-GA-LAUNCH-1, ENABLED inside a PAUSED ad group.
        Enabling Soft Washing would activate it, giving that ad group FOUR ads and
        violating the two-RSA-per-group specification. Its replacement pair
        (823152917215, 823152917218) is already created and waiting.
      rollback: set status back to ENABLED
    - action: P-4
      type: ad_group_ad
      ad_group_id: '202870586310'
      ad_group_name: Soft House Washing Near Me
      resource_id: '819975939531'
      current_status: ENABLED
      proposed_status: PAUSED
      policy: APPROVED AND ELIGIBLE
      final_url: https://offer.softwindli.com/soft-house-washing/
      reason: same as P-3
      rollback: set status back to ENABLED

  coverage_risk_and_how_it_is_handled:
    risk: >-
      Pausing the two legacy Soft Washing ads while their replacements are still UNDER
      REVIEW would leave that ad group with no servable ad IF it were enabled in that
      state.
    mitigation: >-
      Sequencing, not rule-breaking. PLAN-GA-LAUNCH-3B only PAUSES - it enables nothing,
      and ad group 202870586310 stays PAUSED, so nothing goes dark. PLAN-GA-LAUNCH-3A is
      separately gated on all twelve new RSAs clearing review, so by the time Soft Washing
      is enabled it has two approved ads.
    why_not_leave_them_enabled: >-
      The standing rule is explicit - a nonfinal ad must not become active merely because
      its parent ad group is enabled. Bending it here would also put four ads in one group.

  what_this_plan_does_not_do:
    - creates nothing
    - enables nothing
    - deletes nothing
    - touches no campaign, budget, CPC ceiling or bidding strategy
    - touches no negative keyword, audience, asset, location, schedule or conversion
    - touches no website, GTM or WhatConverts setting
    - does not touch campaign 24145053510

  dependency: NONE - executable on approval
  approval_owner: Walter Correa
  do_not_execute_note: >-
    A fingerprint identifies an exact plan. It does NOT grant permission.
""", encoding="utf-8")

(PLN / "2026-09-02-plan-ga-launch-3a-enablement.yaml").write_text(f"""# PLAN-GA-LAUNCH-3A - FINAL GOOGLE ADS RESOURCE ENABLEMENT
#
# STATUS: DRAFT - BLOCKED. NOT APPROVED. DO NOT EXECUTE.
# NO FINGERPRINT IS GENERATED IN THIS RUN.
#
# BLOCKED BECAUSE: the fresh read found four legacy resources that would activate on
# parent enable. A new pause mutation is therefore required first, and the standing rule
# is to stop and report the conflict BEFORE fingerprinting this plan. That pause is
# PLAN-GA-LAUNCH-3B. This plan is fingerprinted only after 3B executes and the twelve new
# RSAs clear review.

change_plan:
  plan_id: PLAN-GA-LAUNCH-3A
  plan_title: Final Google Ads resource enablement
  approval_type: ENABLE
  priority: P0
  approval_status: NOT APPROVED
  execution_status: 'DO NOT EXECUTE - BLOCKED'
  fingerprint: null
  fingerprint_withheld_because: >-
    {B['plan_3a']['fingerprint_withheld_because']}

  target:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '1521725229'
    manager_customer_id: '3373711342'
    exact_service: Power Washing
    campaign_id: '24103511039'

  counts_recalculated_from_the_live_account:
    ad_groups_to_enable: {B['plan_3a']['counts']['ad_groups']}
    keyword_criteria_to_enable: {B['plan_3a']['counts']['keywords']}
    rsas_to_enable: {B['plan_3a']['counts']['ads']}
    action_count: {B['plan_3a']['counts']['total']}
    object_count: {B['plan_3a']['counts']['total']}
    mutation_count: {B['plan_3a']['counts']['total']}
    note: >-
      Recalculated from the live account, not assumed. It happens to match the earlier
      expected 45, and that was verified rather than carried forward.

  already_enabled_not_mutated:
    ad_groups: ['202870585390 Power Washing']
    keyword_objects: 10
    ads: '4 - two legacy in Power Washing already serving, two legacy in Soft Washing handled by 3B'

  blocking_gates:
    - id: GATE-1
      requirement: PLAN-GA-LAUNCH-3B executed and read back
      state: NOT MET
      detail: >-
        Four legacy resources would otherwise activate - two `house washing company near
        me` criteria in 202870585910 and two legacy RSAs in 202870586310.
    - id: GATE-2
      requirement: All twelve new RSAs out of review and none DISAPPROVED
      state: NOT MET
      detail: >-
        Fresh read 2026-09-02 14:22 ET - all twelve read approval_status UNKNOWN with
        review_status REVIEW_IN_PROGRESS and ZERO policy topic entries. That is normal
        for newly created paused ads, not a defect. Re-read before approval.

  preflight_checks_already_passing:
{chr(10).join('    - ' + k + ': ' + str(v) for k, v in B['plan_3a']['checks'].items())}

  actions:
    ad_groups:
{ag_rows}
    keywords:
{kw_rows}
    responsive_search_ads:
{ad_rows}

  campaign_instruction:
    campaign_24103511039: 'ENABLED - unchanged by this plan'
    campaign_24145053510: >-
      ENABLED and otherwise unchanged. NOT paused, NOT renamed, budget unchanged, CPC
      ceiling unchanged. It remains a temporary transition campaign; its retirement needs
      separate analysis, plan, fingerprint and approval.
    bidding: 'Both campaigns stay on Maximize Clicks (TARGET_SPEND). No change under this plan.'
    cpc_ceilings: 'Both remain $30.00. No change under this plan.'

  what_this_plan_does_not_do:
    - creates nothing
    - deletes nothing
    - pauses nothing
    - no campaign pause, rename, budget, CPC or bidding change
    - no negative keyword, audience, asset, location, schedule or conversion change
    - no website, GTM or WhatConverts change

  rollback: >-
    Set each enabled resource back to PAUSED. Fully reversible, one mutation per resource.

  post_enablement_qa:
    - confirm each of the six ad groups is ELIGIBLE and serving
    - confirm impressions begin and Search Terms appear
    - confirm the correct Final URL per ad group
    - confirm no policy problem on any serving ad
    - confirm no owner ad group is blocked by a routing negative
    - confirm phone and form paths still work
    - confirm campaign 24145053510 is still ENABLED and unchanged
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---- LAUNCH-2 real IDs ----
p2 = PLN / "2026-09-02-plan-ga-launch-2-routing-negatives.yaml"
t2 = p2.read_text(encoding="utf-8")
add = """
  real_ids_confirmed_2026_09_02:
    note: >-
      The six owner ad groups are confirmed live in campaign 24103511039 and all 19 owned
      keyword texts are confirmed present as PHRASE + EXACT objects. The routing negatives
      themselves are CREATE operations, so their own IDs do not exist yet.
    owner_ad_groups:
      Power Washing: '202870585390'
      Pressure Washing: '202870585870'
      House Washing: '202870585910'
      Soft Washing: '202870586310'
      Driveway Pressure Washing: '202870586110'
      Patio Pressure Washing: '202870586150'
    owned_keyword_objects_live: 38
    unique_owned_texts: 19
    sibling_mirror_arithmetic: '19 texts x 5 sibling groups = 95 negative EXACT criteria'
    modifier_phrase_collision_tested: 8
    total_at_launch: 103
    deferred: '11 modifier PHRASE + 2 historical rogue-query = 13'
  stage_position: >-
    Immediate next stage AFTER successful PLAN-GA-LAUNCH-3A enablement readback. Not
    before - no routing negative may be applied until its owner ad group is verified
    serving.
"""
if "real_ids_confirmed_2026_09_02" not in t2:
    t2 = t2.replace("  approval_owner: Walter Correa", add + "  approval_owner: Walter Correa")
    p2.write_text(t2, encoding="utf-8")
print("wrote 3B, 3A, updated LAUNCH-2")
