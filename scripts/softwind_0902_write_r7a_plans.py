#!/usr/bin/env python3
"""Write the R7A split-track plan files, source audit, supersede notice and ledger update."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLN = ROOT / "clients/softwind-power-washing/plans"
AUD = ROOT / "clients/softwind-power-washing/audits"

# ---------------------------------------------------------------- TRACK A
(PLN / "2026-09-02-plan-r7a1-gtm-form-measurement.yaml").write_text("""# PLAN-R7A1-GTM - POWER WASHING GTM FORM-MEASUREMENT REPAIR
#
# STATUS: BLOCKED - NO GTM CREDENTIAL. NOT APPROVED. DO NOT EXECUTE.
# NO FINGERPRINT IS GENERATED. See fingerprint_withheld_because.

change_plan:
  plan_id: PLAN-R7A1-GTM
  plan_title: Power Washing GTM form-measurement repair
  approval_type: GTM_CONFIGURATION
  priority: P0
  approval_status: NOT APPROVED
  execution_status: 'BLOCKED - NO GTM CREDENTIAL'
  target:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '1521725229'
    exact_service: Power Washing
    gtm_container_public_id: GTM-P3LD97NN

  counts:
    executable_action_count: 0
    object_count: 0
    google_ads_mutation_count: 0
    gtm_mutation_count: 0

  fingerprint: null
  fingerprint_withheld_because: >-
    Rule 18 forbids fingerprinting a plan with placeholder IDs, unknown current values, or zero
    executable actions. Every action below needs an exact GTM tag ID, trigger ID, variable ID
    and current value, and none can be read.

  blocking_access_finding:
    claim_in_brief: 'GOOGLE TAG MANAGER: AUTHENTICATED ACCESS AVAILABLE'
    verified_reality: 'NOT AVAILABLE'
    evidence:
      - >-
        The Google OAuth refresh token in .env returns exactly one granted scope on refresh:
        https://www.googleapis.com/auth/adwords. There is no tagmanager or
        tagmanager.readonly scope.
      - No separate GTM service-account, API key or OAuth credential exists in .env.
      - No stored browser profile, cookie jar or authenticated session exists on this machine.
      - >-
        CLAUDE.md forbids automatically reusing or broadening the Google Ads OAuth refresh
        token, so minting a Tag Manager scope from it is not permitted even if it were possible.
    unblock_requirement: >-
      A Tag Manager OAuth credential with tagmanager.readonly, or an exported container JSON,
      or a read-only GTM user invitation to an account Green Marketing controls.

  intended_actions_when_unblocked:
    - id: R7A1-1
      intent: >-
        Repoint the Power Washing form conversion trigger from the /thank-you/ page path to the
        verified success event gm_power_washing_form_success delivered by DEV-R7A3-04.
      why: >-
        PROVEN 2026-09-02 - a bare visit to /thank-you/ with no form submission fires
        en=conversion to pagead/conversion/18369652705 and pagead/1p-conversion/18369652705.
      preserve: 'AW-18369652705, label FddkCOul59scEOHPqrdE, Conversion Linker, consent mode'
      needs_before_it_can_be_written: 'exact tag ID, trigger ID, current trigger conditions'
      depends_on: DEV-R7A3-04
    - id: R7A1-2
      intent: 'Add trigger exceptions so refresh, back navigation and direct visits cannot re-fire.'
      needs_before_it_can_be_written: exact trigger and variable IDs
    - id: R7A1-3
      intent: >-
        Confirm the deployed conversion label really is FddkCOul59scEOHPqrdE by reading the tag
        configuration, since the outbound request carries it in an encoded payload rather than a
        visible label= parameter.
      needs_before_it_can_be_written: read access to the tag
    - id: R7A1-4
      intent: >-
        Establish whether process.iconnode.com is a GTM Custom HTML tag. It POSTs on every page
        yet has ZERO occurrences in the rendered source, which is consistent with GTM injection.
      needs_before_it_can_be_written: container read
      note: 'Investigation only - no removal before DEV-R7A3-06 establishes ownership.'
    - id: R7A1-5
      intent: >-
        Establish whether AW-17878095007 and AW-18369652705 are GTM tags or Google tag linked
        destinations. This determines whether sibling scoping is a GTM change or a site change.
      needs_before_it_can_be_written: container read
      note: 'Any change to AW-17878095007 belongs to PLAN-R7A4 and needs sibling-account approval.'

  explicitly_excluded:
    - WordPress code changes
    - Gravity Forms embed changes
    - WhatConverts changes
    - Sibling-account tag changes
    - iconnode changes while authorization is unknown
    - Landing-page copy
    - Google Ads campaign changes
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---------------------------------------------------------------- TRACK B
(PLN / "2026-09-02-plan-r7a2-whatconverts-call-attribution.yaml").write_text("""# PLAN-R7A2-WHATCONVERTS - POWER WASHING WHATCONVERTS DNI AND CALL-ATTRIBUTION REPAIR
#
# STATUS: BLOCKED - NO WHATCONVERTS CREDENTIAL. NOT APPROVED. DO NOT EXECUTE.
# NO FINGERPRINT IS GENERATED.

change_plan:
  plan_id: PLAN-R7A2-WHATCONVERTS
  plan_title: Power Washing WhatConverts DNI and call-attribution repair
  approval_type: WHATCONVERTS_CONFIGURATION
  priority: P1
  approval_status: NOT APPROVED
  execution_status: 'BLOCKED - NO WHATCONVERTS CREDENTIAL'
  target:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '1521725229'
    exact_service: Power Washing
    whatconverts_profile_number_probable: '158931'

  counts:
    executable_action_count: 0
    object_count: 0
    google_ads_mutation_count: 0
    whatconverts_mutation_count: 0

  fingerprint: null
  fingerprint_withheld_because: >-
    Rule 18. The profile ID, number pool, source rules, selectors and destination numbers are
    all unread, the DNI root cause was NOT determined, and the brief explicitly forbids
    inferring that cause from cookies alone.

  blocking_access_finding:
    claim_in_brief: 'WHATCONVERTS: AUTHENTICATED ACCESS AVAILABLE'
    verified_reality: 'NOT AVAILABLE'
    evidence: >-
      WHATCONVERTS_API_TOKEN exists as a key in .env but its value is EMPTY - string length 0.
      No other WhatConverts credential, session or export exists.
    unblock_requirement: >-
      Populate WHATCONVERTS_API_TOKEN with a valid API token and secret pair, or supply a
      read-only WhatConverts user login.

  what_public_inspection_did_establish:
    whatconverts_is_active: true
    correction_to_earlier_receipts: >-
      Earlier receipts recorded "no request to a WhatConverts host was observed" and attributed
      the domain p.ksrndkehqnwntyxlhgto.com to ClickCease. BOTH were wrong. The WhatConverts
      tracking script is served from s.ksrndkehqnwntyxlhgto.com/158931.js - an obfuscated
      first-party-looking domain WhatConverts uses to survive ad blockers. ClickCease is
      separately present at www.clickcease.com/monitor/stat.js. The /keyword/ and /lead/form
      POSTs seen at submission were therefore WHATCONVERTS capturing the lead, not ClickCease,
      which makes it likely the test lead WAS recorded.
    script_source: >-
      <script id="whatconverts-tracking-script-js" src="//s.ksrndkehqnwntyxlhgto.com/158931.js?ver=7.1">
      plus an inline whatconverts-tracking-script-js-before config block. The -js handle and
      ver= query are the WordPress wp_enqueue_script signature, so the script is delivered by a
      WordPress plugin.
    attribution_working: >-
      wc_client carries source, medium, campaign, content, term and the GCLID. wc_visitor prefix
      158931 matches the script number.
    dni_not_working: >-
      wc_swap nominates 6315025402 and 6315535927 on all 7 pages, yet the DOM renders the static
      (631) 502-7946 in both body text and the tel: href. The replacement never executes.
    root_cause: 'NOT DETERMINED - requires an authenticated read. Do not guess.'

  candidate_causes_to_test_when_unblocked:
    - wrong source number configured for replacement
    - wrong replacement or destination number
    - selector or text-matching rule does not match the rendered markup
    - profile domain mismatch - offer.softwindli.com may not be an included domain
    - the offer subdomain or these paths excluded
    - source rule does not match google / cpc
    - number pool unavailable or exhausted
    - the plugin script loads after the replacement scan
    - the sibling account website-call replacement runs first and wins the element
    - the DUPLICATE form and 22 duplicate HTML IDs cause an id-bound selector to hit the wrong node
    - consent gating blocks replacement
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---------------------------------------------------------------- TRACK D
(PLN / "2026-09-02-plan-r7a4-sibling-tag-scoping.yaml").write_text("""# PLAN-R7A4-CROSS-ACCOUNT - SIBLING-ACCOUNT TAG SCOPING AND MEASUREMENT IMPACT
#
# STATUS: BLOCKED - SEPARATE SIBLING-ACCOUNT WORK ORDER AND APPROVAL REQUIRED
# This is a DECISION RECORD, not an executable plan. NO FINGERPRINT.

decision_record:
  plan_id: PLAN-R7A4-CROSS-ACCOUNT
  plan_title: Sibling-account tag scoping and measurement impact
  status: 'BLOCKED - SEPARATE SIBLING-ACCOUNT WORK ORDER AND APPROVAL REQUIRED'
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    A cross-account action cannot be fingerprinted under the Power Washing work order. Any
    change affecting measurement for customer 2429758629 requires its own identity gate, work
    order, approval owner and fingerprint.

  current_work_order_scope:
    exact_child_account_name: Softwind Power Washing - Live
    child_customer_id: '1521725229'
    exact_service: Power Washing

  sibling_account:
    exact_child_account_name: Softwind Landscape & Masonry - Live
    child_customer_id: '2429758629'
    conversion_tracking_id: '17878095007'
    relationship: 'level 1 under the same authorized MCC 3373711342'
    ownership_state: 'B - GREEN-MARKETING-OWNED AND DOCUMENTED'
    campaign_performance_audited: false
    note: >-
      Only the single field conversion_tracking_setting.conversion_tracking_id was read, to
      resolve tag ownership. No campaign, keyword, ad or performance data from 2429758629 was
      read, and none is reproduced anywhere.

  findings:
    aw_17878095007_source: >-
      googletagmanager.com/gtag/js?id=AW-17878095007&cx=c&gtm=4e68v1, async-injected. The
      literal ID appears exactly ONCE in the rendered source and only inside that URL. There is
      no hardcoded gtag config block. Consistent with GTM or a Google tag linked destination.
      PUBLIC EFFECT PROVEN - EXACT CONFIGURATION SOURCE REQUIRES AUTHENTICATED GTM READ.
    current_page_scope: 'all 7 Power Washing paid URLs plus /thank-you/'
    current_triggers_observed:
      - page_view / viewthroughconversion
      - rmkt/collect and 1p-user-list remarketing
      - 'website-call replacement wcm, dn=6315027946, label SFv1CLSo--UbEJ-p-MxC, on all 7 pages'
      - 'en=form_start and en=form_submit - proven at submission 2026-09-02'
      - 'POST pagead/form-data and ccm/form-data - proven at submission 2026-09-02'
    proposed_page_scope: >-
      The tag stops on the six Power Washing paid URLs and /thank-you/. It remains wherever
      Softwind Landscape & Masonry legitimately advertises.
    unknown_and_must_be_answered_first:
      - Does the same GTM container also serve the Masonry brand pages?
      - Is the Masonry account currently counting conversions from these Power Washing pages?
      - Would a page-path exception break Masonry measurement on its own pages?

  impact_if_scoped_off_power_washing_urls:
    effect_on_1521725229: >-
      POSITIVE. Unblocks the Power Washing website-call path, stops form interactions and form
      data leaving for another account, and removes a competing number replacement.
    effect_on_2429758629: >-
      Its reported conversions, remarketing list membership and website-call volume from these
      pages will DROP. That is a scope correction, not a loss - but the owner of that account
      must agree before it happens.
    form_event_impact: 'form_start and form_submit stop reaching 2429758629'
    website_call_impact: 'wcm replacement stops; Power Washing can then claim its own calls'
    remarketing_impact: 'Power Washing visitors stop joining Masonry audiences'
    user_list_impact: 'same'
    rollback: 'remove the page-path exception and the tag resumes'

  required_before_any_execution:
    - Separate mandatory identity gate on Softwind Landscape & Masonry - Live / 2429758629
    - Exact service for that account
    - similar-local-service scope approval for that account if applicable
    - Separate work order
    - Separate approval owner
    - Separate fingerprint
  approval_owner: 'Walter Correa - plus the sibling account owner'
""", encoding="utf-8")
print("wrote 3 plan files")
