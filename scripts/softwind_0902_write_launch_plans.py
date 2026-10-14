#!/usr/bin/env python3
"""Write the PLAN-GA-LAUNCH package, PLAN-GA-BID-1, and the ClickUp task package."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLN = ROOT / "clients/softwind-power-washing/plans"
CU = ROOT / "clients/softwind-power-washing/clickup-tickets"
CU.mkdir(parents=True, exist_ok=True)

FP = "92FFF603CAFD"

# ------------------------------------------------------------ LAUNCH-1
(PLN / "2026-09-02-plan-ga-launch-1-create-paused.yaml").write_text("""# PLAN-GA-LAUNCH-1 - FINAL POWER WASHING CREATE-PAUSED BUILD
#
# STATUS: NOT APPROVED. DO NOT EXECUTE.
# Fingerprint 92FFF603CAFD  (recomputed twice, identical)
# validate_only PASSED against the exact payload. ZERO resources created.
#
# A fingerprint identifies an exact plan. It does NOT grant permission.
# Creation is PAUSED ONLY. Enabling requires a separate later approval.

change_plan:
  plan_id: PLAN-GA-LAUNCH-1
  plan_title: Final Power Washing create-paused build
  approval_type: CREATE_PAUSED
  priority: P0
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: 92FFF603CAFD
  canonical_sha256_full: 92fff603cafd1e16bf67f97482d1c649eeca256fca23461bf7440a4223d5f6fb
  approval_command: APPROVE PLAN-GA-LAUNCH-1 92FFF603CAFD FOR 1521725229
  payload_file: clients/softwind-power-washing/plans/2026-09-02-plan-ga-launch-1-payload.json

  target:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '1521725229'
    manager_customer_id: '3373711342'
    exact_service: Power Washing
    vertical: similar-local-service
    surviving_campaign_id: '24103511039'
    surviving_campaign_name: Power Washing
    retiring_campaign_id: '24145053510'
    retiring_campaign_note: >-
      Campaign 24145053510 remains LIVE and untouched throughout this plan. It is
      paused LAST, in PLAN-GA-LAUNCH-4, only after replacements are verified serving.

  identity_gate:
    verified_account_local: '2026-09-02T12:51:54-04:00'
    name: PASS
    id: PASS
    manager_false: PASS
    test_account_false: PASS
    status_enabled: PASS
    currency_usd: PASS
    timezone_america_new_york: PASS

  counts:
    action_count: 40
    object_count: 40
    mutation_count: 40
    ad_groups_created: 0
    ad_groups_reused_existing: 6
    keyword_objects_created_paused: 28
    keyword_objects_reused_existing: 10
    keyword_objects_final: 38
    unique_keyword_texts: 19
    rsas_created_paused: 12
    enablement_actions: 0
    pause_actions: 0
    negative_keyword_actions: 0
    cpc_actions: 0
    budget_actions: 0
    asset_actions: 0
    audience_actions: 0
    schedule_actions: 0
    conversion_actions: 0
    website_actions: 0
    gtm_actions: 0
    whatconverts_actions: 0

  validation:
    duplicate_key_yaml: PASS
    rsa_validators: 'PASS - 0 errors'
    rsa_checks:
      - every headline <= 30 characters
      - every description <= 90 characters
      - every path <= 15 characters
      - no duplicate headline or description within an ad
      - 'RSA1 vs RSA2 headline overlap 0% in every ad group - not minor rewrites'
      - no banned or unverified claim
      - 'no digit in any asset - phone-number guard'
      - no awkward "near me" ad copy
      - '>= 2 local headlines and >= 2 quote/estimate headlines per RSA'
      - 'canonical service token in 3-8 headlines and >= 1 description per RSA'
      - no pinning
      - every Final URL returns HTTP 200, fresh-checked 2026-09-02
    duplicate_ownership_check: 'PASS - each of the 19 texts has exactly one owner ad group'
    validate_only:
      keyword_request: 'PASS - 28 AdGroupCriterion operations validated, 0 created'
      ad_request: 'PASS - 12 AdGroupAd operations validated, 0 created'
      resources_created: 0
      note: >-
        validate_only was set on the request message, not as a call kwarg. It consumes the
        same daily mutate quota as a real write, which is accepted here because the brief
        requires validating the exact create payload before approval.
    fingerprint_recomputed_twice: PASS

  the_key_finding: >-
    ALL SIX final ad groups ALREADY EXIST inside the surviving campaign 24103511039 - five of
    them paused with the correct names, and four already carrying their canonical keyword.
    ZERO ad groups need creating. The build is therefore 28 keyword objects plus 12 RSAs.

  ad_groups_reused:
    - {final_group: Power Washing, ad_group_id: '202870585390', live_name: Power Washing Near Me,
       live_status: ENABLED, action: REUSE - NOT MODIFIED}
    - {final_group: Pressure Washing, ad_group_id: '202870585870',
       live_name: Residential Pressure Washing Near Me, live_status: PAUSED,
       action: REUSE - NOT MODIFIED}
    - {final_group: House Washing, ad_group_id: '202870585910',
       live_name: House Washing Company Near Me, live_status: PAUSED,
       action: REUSE - NOT MODIFIED}
    - {final_group: Soft Washing, ad_group_id: '202870586310',
       live_name: Soft House Washing Near Me, live_status: PAUSED,
       action: REUSE - NOT MODIFIED}
    - {final_group: Driveway Pressure Washing, ad_group_id: '202870586110',
       live_name: Driveway Pressure Washing Near Me, live_status: PAUSED,
       action: REUSE - NOT MODIFIED}
    - {final_group: Patio Pressure Washing, ad_group_id: '202870586150',
       live_name: Patio Pressure Washing Near Me, live_status: PAUSED,
       action: REUSE - NOT MODIFIED}
  ad_group_naming_note: >-
    Existing names are KEPT. Renaming six containers costs six mutations and changes no
    performance; ownership is enforced by keywords and routing negatives, not by the label.

  keyword_objects_reused_not_in_plan:
    - {ad_group_id: '202870585390', text: power washing near me, match: PHRASE + EXACT}
    - {ad_group_id: '202870585870', text: residential pressure washing near me, match: PHRASE + EXACT}
    - {ad_group_id: '202870586310', text: soft house washing near me, match: PHRASE + EXACT}
    - {ad_group_id: '202870586110', text: driveway pressure washing near me, match: PHRASE + EXACT}
    - {ad_group_id: '202870586150', text: patio pressure washing near me, match: PHRASE + EXACT}

  objects_to_create:
    all_created_with_status: PAUSED
    keywords:
      count: 28
      note: >-
        Created PAUSED so nothing can serve, including inside ad group 202870585390 which is
        ENABLED. Full object list with match types is in the payload file.
      by_ad_group:
        '202870585390': ['power washing', 'power washing service',
                         'power washing services near me', 'power washing company near me']
        '202870585870': ['pressure washing', 'pressure washing near me']
        '202870585910': ['house washing near me', 'house pressure washing near me',
                         'house power washing near me', 'exterior house washing near me']
        '202870586310': ['soft washing near me']
        '202870586110': ['driveway power washing near me']
        '202870586150': ['patio power washing near me', 'concrete pressure washing near me']
      match_types: 'PHRASE and EXACT for every text. No Broad Match.'
    rsas:
      count: 12
      per_ad_group: 2
      status_on_create: PAUSED
      note: >-
        Old ads are NOT edited and NOT paused by this plan. Replacement happens later, in
        PLAN-GA-LAUNCH-4, only after the new ads are verified serving.
      copy_source: clients/softwind-power-washing/audits/2026-09-02-final-rsa-launch-qa.csv

  final_url_map:
    '202870585390': https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/
    '202870585870': https://offer.softwindli.com/residential-pressure-washing/
    '202870585910': https://offer.softwindli.com/house-washing-company/
    '202870586310': https://offer.softwindli.com/soft-house-washing/
    '202870586110': https://offer.softwindli.com/driveway-pressure-washing/
    '202870586150': https://offer.softwindli.com/patio-power-washing/
    http_status_checked_2026_09_02: 'all six return 200'
    slug_changes: NONE

  displaced_duplicates_detected_not_touched:
    count: 30
    note: >-
      Thirty existing keyword objects across ten legacy ad groups carry texts whose final owner
      is one of the six groups. They are NOT paused, removed or modified by this plan. They are
      retired later in PLAN-GA-LAUNCH-4.
    blocking_conflicts: 0

  explicitly_excluded_from_this_plan:
    - Enablement of anything
    - Campaign, ad group, keyword or ad pauses
    - Routing negatives and campaign negatives
    - CPC ceiling and bidding changes
    - Budget changes
    - Audience or demographic changes
    - Asset changes
    - Schedule changes
    - Conversion action or goal changes
    - Landing-page, GTM and WhatConverts changes

  dependency: NONE - this plan is executable on approval
  rollback: >-
    Every created object is PAUSED and newly created. Rollback is to pause-and-remove the
    created criteria and ads by the IDs returned in the readback. No existing resource is
    altered, so nothing needs restoring.

  readback_qa_required_after_execution:
    - Stop on any partial failure and inventory every created resource ID
    - Read back all 28 keywords - verify text, match type, and status PAUSED
    - Read back all 12 RSAs - verify every headline, description, path and Final URL
    - Verify policy approval status on all 12 ads
    - Verify object counts exactly match 28 + 12
    - Verify no pre-existing resource changed status
    - Verify campaign 24145053510 untouched
    - Produce the readback QA report and update the ledger

  approval_owner: Walter Correa
  do_not_execute_note: >-
    NOT APPROVED. Creation is paused-only; enabling requires a separate approval after
    readback QA passes and the go-live gate in the ledger is satisfied.
""", encoding="utf-8")

# ------------------------------------------------------------ LAUNCH-2
(PLN / "2026-09-02-plan-ga-launch-2-routing-negatives.yaml").write_text("""# PLAN-GA-LAUNCH-2 - AD-GROUP ROUTING NEGATIVES
# STATUS: PROVISIONAL / BLOCKED UNTIL OWNER GROUPS ARE LIVE. NO FINGERPRINT. NO APPROVAL COMMAND.

change_plan:
  plan_id: PLAN-GA-LAUNCH-2
  plan_title: Ad-group routing negatives
  approval_type: NEGATIVE_KEYWORDS
  status: 'PROVISIONAL / BLOCKED UNTIL OWNER GROUPS ARE LIVE'
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    No negative may be fingerprinted for execution before its intended owner ad group is
    enabled and verified serving. The plan would also be invalid if PLAN-GA-LAUNCH-1 or
    PLAN-GA-LAUNCH-3 changed the owner set.
  target:
    child_customer_id: '1521725229'
    campaign_id: '24103511039'

  counts_recalculated_2026_09_02:
    source: clients/softwind-power-washing/audits/2026-09-01-final-routing-negative-matrix.csv
    unique_owned_texts: 19
    sibling_groups_per_text: 5
    layer_1_sibling_exact_mirror: 95
    layer_2_modifier_phrase_deployed: 8
    layer_2_modifier_phrase_deferred: 11
    layer_3_historical_rogue_query_deferred: 2
    total_at_launch: 103
    self_block_failures: 0
    arithmetic_check: '19 texts x 5 siblings = 95, + 8 collision-tested modifiers = 103'

  layers:
    - layer: '1 - SIBLING EXACT MIRROR'
      criteria: 95
      deploy_at_launch: true
      rule: >-
        Every one of the 19 owned texts is added as negative EXACT in each of the five sibling
        ad groups, never in its own owner. Zero blocking risk - a negative EXACT blocks only
        the literal string and every text has exactly one owner.
    - layer: '2 - MODIFIER PHRASE'
      criteria: 8
      deploy_at_launch: true
      rule: >-
        house washing, soft washing, driveway, patio - applied ONLY to Power Washing and
        Pressure Washing, the two groups owning the loose head terms that would otherwise
        vacuum sibling queries. Collision-tested: no owned text in either target contains any
        of the four phrases.
    - layer: '2 - MODIFIER PHRASE (DEFERRED)'
      criteria: 11
      deploy_at_launch: false
      rule: >-
        Applying these to the four narrow groups is theoretical routing against a leak nobody
        has observed. Their own Phrase and Exact texts already scope them.
    - layer: '3 - HISTORICAL ROGUE QUERY'
      criteria: 2
      deploy_at_launch: false
      rule: >-
        pressure washer near me and commercial pressure washing near me, both observed
        2026-09-01 as NEAR_EXACT close variants at 1 impression, 0 clicks, $0.00. No paid
        misrouting yet, so defer 14 days.

  preserved_rules:
    - Routing negatives stay at AD GROUP level
    - The 132-per-campaign universal fence stays SEPARATE at campaign level
    - No owner keyword blocks itself - validated, 0 violations
    - No approved buying-intent query is removed
    - No routing negative is applied before its owner ad group is enabled and verified serving
    - >-
      Negative keywords cannot perfectly control positive close variants. An EXACT negative
      blocks only the literal string; an unseen close variant slips past regardless. Residual
      risk is permanent and is managed by continuous Search Terms review.
    - Search Terms must continue to be reviewed after launch

  blocked_until:
    - PLAN-GA-LAUNCH-1 executed and readback QA passed
    - PLAN-GA-LAUNCH-3 executed - the six owner groups ENABLED and verified serving
  approval_owner: Walter Correa
""", encoding="utf-8")

# ------------------------------------------------------------ LAUNCH-3
(PLN / "2026-09-02-plan-ga-launch-3-enablement.yaml").write_text("""# PLAN-GA-LAUNCH-3 - FINAL RESOURCE ENABLEMENT
# STATUS: PROVISIONAL. PLACEHOLDERS ONLY. NO FINGERPRINT. NO APPROVAL COMMAND.

change_plan:
  plan_id: PLAN-GA-LAUNCH-3
  plan_title: Final resource enablement
  approval_type: ENABLE
  status: PROVISIONAL
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    Every action references a resource that does not exist yet. Real criterion and ad IDs only
    exist after PLAN-GA-LAUNCH-1 is executed and read back. A fingerprint over placeholders
    would be void by construction.
  target:
    child_customer_id: '1521725229'
    campaign_id: '24103511039'

  placeholder_actions:
    - {id: E-1, resource: ad_group, target: '202870585870 Pressure Washing',
       current: PAUSED, proposed: ENABLED}
    - {id: E-2, resource: ad_group, target: '202870585910 House Washing',
       current: PAUSED, proposed: ENABLED}
    - {id: E-3, resource: ad_group, target: '202870586310 Soft Washing',
       current: PAUSED, proposed: ENABLED}
    - {id: E-4, resource: ad_group, target: '202870586110 Driveway Pressure Washing',
       current: PAUSED, proposed: ENABLED}
    - {id: E-5, resource: ad_group, target: '202870586150 Patio Pressure Washing',
       current: PAUSED, proposed: ENABLED}
    - {id: E-6, resource: ad_group_criterion, target: 'PENDING_CREATION x28',
       current: PAUSED, proposed: ENABLED}
    - {id: E-7, resource: ad_group_ad, target: 'PENDING_CREATION x12',
       current: PAUSED, proposed: ENABLED}
  note_202870585390: >-
    Ad group 202870585390 Power Washing is ALREADY ENABLED and is not re-enabled. Only its 8
    newly created keywords move from PAUSED to ENABLED.

  staged_enablement:
    stage_a: [Power Washing, Pressure Washing, House Washing]
    stage_a_rationale: 'the three groups carrying roughly 97% of measured demand'
    stage_b: [Soft Washing, Driveway Pressure Washing, Patio Pressure Washing]
    stage_b_rationale: 'the three micro groups, roughly 30 searches per month combined'
    note: 'Order is evidence-based and may change if readback or page results support another.'

  blocked_until_go_live_gate:
    - PLAN-GA-LAUNCH-1 create-paused readback QA passed
    - All six Final URLs return HTTP 200
    - Correct titles, H1s and hero copy published
    - Direct /thank-you/ visits do NOT fire the form conversion
    - A successful form fires exactly one logical conversion
    - Exactly one customer-facing form is rendered
    - Phone links valid, displayed number equals tel: destination
    - Selected call-tracking architecture verified
    - Sibling-account tag scope corrected or safely contained
    - No owner ad group blocked by a routing negative
  after_each_stage_confirm:
    - eligibility, impressions, Search Terms, ads serving
    - correct Final URLs and no policy problem
    - no owner group blocked by a negative
    - phone and form paths work
  approval_owner: Walter Correa
""", encoding="utf-8")

# ------------------------------------------------------------ LAUNCH-4
(PLN / "2026-09-02-plan-ga-launch-4-retirement.yaml").write_text("""# PLAN-GA-LAUNCH-4 - OLD RESOURCE RETIREMENT
# STATUS: BLOCKED. NO FINGERPRINT. NO APPROVAL COMMAND. PAUSE ONLY - NEVER DELETE.

change_plan:
  plan_id: PLAN-GA-LAUNCH-4
  plan_title: Old resource retirement
  approval_type: PAUSE
  status: BLOCKED
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    Nothing may be retired until its replacement is created, enabled, eligible and verified
    serving. Fingerprinting now would let a stale plan pause the account's only live delivery.
  target:
    child_customer_id: '1521725229'

  method: 'PAUSE ONLY. Deletion requires its own separate destructive-action approval.'

  retirement_order:
    - step: 1
      what: Displaced duplicate positive keywords
      detail: >-
        30 objects across 10 legacy ad groups carry texts now owned by one of the six final
        groups. Full list in snapshots/launch1-delta-2026-09-02T125154.json.
    - step: 2
      what: Displaced duplicate ad groups
      detail: '202870585430 Power Washing Services Near Me, 202870585590 Power Washing Company Near Me'
    - step: 3
      what: Weak old RSAs, only after replacements serve
      detail: 'the 12 currently live ads in campaign 24103511039'
    - step: 4
      what: Zero-volume city groups
      detail: '202870585630 Islip, 202870585670 West Islip, 202870585830 Dix Hills - 1 impression between them all-time'
    - step: 5
      what: Legacy mixed-intent groups
      detail: '205713509664, 205713509704, 205713509744'
    - step: 6
      what: 'Campaign 24145053510 - LAST'
      detail: >-
        It currently carries half the account's live delivery. It must NOT be paused during
        this sprint or during PLAN-GA-LAUNCH-1.

  every_pause_action_must_carry:
    - exact resource ID
    - current status
    - the replacement resource
    - evidence the replacement is live and serving
    - historical performance
    - risk
    - rollback
  approval_owner: Walter Correa
""", encoding="utf-8")

# ------------------------------------------------------------ BID-1
(PLN / "2026-09-02-plan-ga-bid-1-interim-cpc-control.yaml").write_text("""# PLAN-GA-BID-1 - INTERIM CPC CONTROL
# STATUS: DRAFT / BLOCKED. NO FINGERPRINT THIS RUN. NO APPROVAL COMMAND THIS RUN.

change_plan:
  plan_id: PLAN-GA-BID-1
  plan_title: Interim CPC control
  approval_type: BIDDING
  status: 'DRAFT - BLOCKED ON THE LANDING-PAGE GATE'
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    The brief requires exactly one approval command this run, for PLAN-GA-LAUNCH-1. This plan
    is also gated on evidence that does not exist yet - see the gate below.
  target:
    child_customer_id: '1521725229'
    campaigns: ['24103511039', '24145053510']

  bidding_strategy_decision:
    stays: MAXIMIZE_CLICKS (TARGET_SPEND)
    reason: >-
      The account has ZERO verified qualified conversions. Switching to Maximize Conversions
      would bid toward a signal that does not exist. Revisit only after conversion tracking is
      verified, qualified conversions are recording, there is enough reliable data, and lead
      quality can be judged. That switch gets its own plan and is never combined with
      consolidation or RSA changes.

  fresh_evidence_2026_09_02:
    current_ceilings: {'24103511039': 30.00, '24145053510': 30.00}
    billable_clicks_all_time: 19
    click_price_distribution: [5.71, 22.11, 22.13, 26.66, 28.73, 28.73, 29.04, 29.32, 29.50,
                               29.57, 29.57, 29.72, 29.91, 29.91, 35.31, 40.07, 42.67, 54.49,
                               82.22]
    median_click_price: 29.57
    mean_click_price: 32.91
    clicks_at_or_below_29_91: 14
    clicks_above_30: 5
    clicks_above_30_note: 'all five occurred during the uncapped period before the $30 ceiling'
    search_lost_is_rank: {'24103511039': 0.4786, '24145053510': 0.2558}
    search_lost_is_budget: {'24103511039': 0.0350, '24145053510': 0.0698}
    top_impression_rate: {'24103511039': 0.3268, '24145053510': 0.5814}
    absolute_top_rate: {'24103511039': 0.2607, '24145053510': 0.4419}
    invalid_click_credits: '72 and 12 invalid clicks filtered and credited, not billed'
    quality_score_components:
      - 'power washing near me QS2 - expected CTR BELOW_AVERAGE, ad relevance AVERAGE, landing page BELOW_AVERAGE'
      - 'power washing services near me QS3 - landing page BELOW_AVERAGE'
      - 'power washing services near me QS5 in campaign B against a different page - landing page AVERAGE'

  derivation_of_the_ceiling:
    method: >-
      Lowest ceiling that still covers the local Keyword Planner TOP-OF-PAGE LOW estimate for
      the owned 19-text inventory, cross-checked against the observed click-price distribution.
    top_of_page_low_across_owned_texts:
      power washing: 0.58
      pressure washing: 0.30
      pressure washing near me: 8.75
      house washing near me: 10.46
      power washing services near me: 10.62
      power washing near me: 10.90
      power washing company near me: 10.90
      power washing service: 11.55
      house pressure washing near me: 13.49
      house power washing near me: 13.49
      soft washing near me: 15.09
    selected_ceiling_usd: 14.00
    why_14: >-
      $14.00 covers the top-of-page LOW estimate for 18 of the 19 owned texts. The single
      exception is soft washing near me at $15.09, which carries 10 searches a month and sits
      in a micro group. $14 also sits below the second-lowest real observed click price
      ($22.11) and roughly halves the current $29.57 median.
    explicitly_not_reused: >-
      $12, $15, $18 and $22 all appeared in earlier plans or conversation. None was carried
      forward. $14.00 is derived fresh from the figures above.
    symmetry: >-
      Apply to BOTH campaigns while both are live - moving one creates the Ad Rank asymmetry
      across shared query space that voided an earlier plan. Single ceiling after consolidation.

  gate_before_this_plan_can_be_approved:
    - >-
      The landing-page P0 work must be published first. Ad Rank is bid x Quality Score, and
      landing-page experience currently reads BELOW_AVERAGE on the two highest-spend keywords.
      Cutting the bid while the page is scored badly attacks the wrong half of the equation
      and would raise lost impression share from an already-high 47.86%.
    - One settled serving day after the page fix, to re-measure the price distribution.
  risk_of_acting_now: 'raises Lost IS to rank above the current 47.86% on the surviving campaign'
  risk_of_waiting: 'roughly $29.57 median per click continues on a badly scored page'
  rollback: 'restore the prior ceiling with one mutation per campaign'
  approval_owner: Walter Correa
""", encoding="utf-8")
print("wrote 5 plan files")
