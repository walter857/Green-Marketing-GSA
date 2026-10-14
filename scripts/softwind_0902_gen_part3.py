#!/usr/bin/env python3
"""Generate BID-1, AUD-1, ASSET-1, RETIRE-1, monitoring runbook, approval queue."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402

C = ROOT / "clients/softwind-power-washing"
CID, SURV, RET = "1521725229", "24103511039", "24145053510"
(C / "runbooks").mkdir(exist_ok=True)

# ---------- resolve real audience segment IDs ----------
load_dotenv_if_available(ROOT / ".env")
ga = load_google_ads_client().get_service("GoogleAdsService")
cid = normalize_customer_id(CID)


def q(s):
    return list(ga.search(customer_id=cid, query=s))


segs = []
try:
    for r in q("""SELECT user_list.id, user_list.name, user_list.type,
                         user_list.size_for_search, user_list.membership_status
                  FROM user_list WHERE user_list.access_reason != 'SHARED'"""):
        u = r.user_list
        segs.append({"id": str(u.id), "name": u.name, "type": enum_name(u.type_),
                     "search_size": u.size_for_search,
                     "status": enum_name(u.membership_status), "source": "user_list"})
except Exception as e:
    segs.append({"error": str(e)[:150]})
inmarket = []
try:
    for r in q("""SELECT detailed_demographic.id, detailed_demographic.name
                  FROM detailed_demographic LIMIT 20"""):
        inmarket.append({"id": str(r.detailed_demographic.id),
                         "name": r.detailed_demographic.name})
except Exception:
    pass
try:
    for r in q("""SELECT life_event.id, life_event.name FROM life_event LIMIT 10"""):
        inmarket.append({"id": str(r.life_event.id), "name": r.life_event.name,
                         "kind": "life_event"})
except Exception:
    pass
print(f"user_lists found: {len([s for s in segs if 'id' in s])}")
print(f"detailed_demographic / life_event rows: {len(inmarket)}")
(C / "snapshots/audience-segments-2026-09-02.json").write_text(
    json.dumps({"user_lists": segs, "other": inmarket}, indent=2), encoding="utf-8")

D = json.loads((C / "snapshots/postlaunch-data-2026-09-02.json").read_text(encoding="utf-8"))
dev = D["by_device"]

# ---------------- PLAN-GA-BID-1 ----------------
(C / "plans/2026-09-02-plan-ga-bid-1-cpc-control.yaml").write_text(f"""# PLAN-GA-BID-1 - EVIDENCE-BASED CPC CONTROL
# STATUS: DRAFT - BLOCKED. NOT FINGERPRINTED. NOT APPROVED. DO NOT EXECUTE.

change_plan:
  plan_id: PLAN-GA-BID-1
  plan_title: Evidence-based CPC control
  approval_type: BIDDING
  priority: P1
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    The rebuilt structure went live 2026-09-02 17:39 and has produced ZERO post-launch clicks.
    Every CPC figure available today describes the OLD structure, old ads and an unfixed landing
    page. Setting a ceiling from that data would be fitting a number to a system that no longer
    exists. The ceiling is derived at the first checkpoint that has post-launch billable clicks.

  bidding_strategy_decision:
    stays: 'MAXIMIZE CLICKS (TARGET_SPEND) on both campaigns'
    prohibited_now: [MAXIMIZE_CONVERSIONS, TARGET_CPA, TARGET_ROAS, MAXIMIZE_CONVERSION_VALUE]
    reason: >-
      The account has ZERO verified qualified conversions, and the owner-accepted thank-you
      exception means a reported conversion is not yet trustworthy. Conversion-based bidding
      would optimise toward a signal that does not exist. Official guidance requires sufficient
      recent conversion volume for Smart Bidding to learn.

  pre_launch_evidence_2026_09_02:
    current_ceilings: {{'{SURV}': 30.00, '{RET}': 30.00}}
    lifetime_billable_clicks: 21
    click_price_distribution: [5.71, 22.11, 22.13, 26.66, 28.73, 28.73, 29.04, 29.32, 29.50,
                               29.57, 29.57, 29.72, 29.91, 29.91, 35.31, 40.07, 42.67, 54.49,
                               82.22]
    median_click_price: 29.57
    clicks_clamped_at_the_ceiling: '14 of 19 priced between $28.73 and $29.91'
    clicks_above_30: '5, all from the uncapped period before the $30 ceiling existed'
    by_device: {json.dumps(dev)}
    by_hour_clicks: 'clusters 14:00-16:00, but on 21 lifetime clicks - not a usable curve'
    lost_is_rank: {{'{SURV}': 0.4786, '{RET}': 0.2558}}
    lost_is_budget: {{'{SURV}': 0.0350, '{RET}': 0.0698}}
    quality_score: 'QS 2-5 on the four keywords with data; landing-page experience BELOW_AVERAGE on the two highest-spend'

  ceiling_options_evaluated:
    - {{ceiling: 10.00, covers_top_of_page_low_for: '1 of 19 owned texts', verdict: 'REJECT - starves delivery'}}
    - {{ceiling: 12.00, covers_top_of_page_low_for: '15 of 19', verdict: 'CANDIDATE'}}
    - {{ceiling: 14.00, covers_top_of_page_low_for: '18 of 19', verdict: 'CANDIDATE'}}
    - {{ceiling: 15.00, covers_top_of_page_low_for: '19 of 19 (soft washing near me at $15.09)', verdict: 'CANDIDATE'}}
    - {{ceiling: 18.00, covers_top_of_page_low_for: '19 of 19 with headroom', verdict: 'CANDIDATE - most conservative cut'}}
    - {{ceiling: 22.00, covers_top_of_page_low_for: '19 of 19', verdict: 'WEAK - barely below the observed $22.11 click'}}
    - {{ceiling: 30.00, note: 'current', verdict: 'STATUS QUO - the ceiling functions as the price'}}
    - {{ceiling: null, note: 'no ceiling', verdict: 'REJECT - uncapped clicks reached $82.22 in this account'}}
  no_number_is_pre_committed: >-
    $12, $14, $15, $18 and $22 have all appeared in earlier plans or conversation. NONE is
    carried forward. The figure is derived at the checkpoint below.

  symmetry_decision:
    while_both_campaigns_live: >-
      SYMMETRIC. Five search terms have served in BOTH campaigns. Moving one ceiling creates an
      Ad Rank asymmetry across shared query space, which is what voided an earlier plan.
    after_consolidation: single ceiling on the surviving campaign
    different_ceilings: >-
      Only if query ownership is genuinely separated, which the routing negatives in
      PLAN-GA-LAUNCH-2A would have to prove first.

  gate_before_this_plan_can_be_fingerprinted:
    - The rebuilt structure has produced billable clicks under the NEW ads and NEW keywords
    - At least one settled serving day, ideally the 3-day checkpoint
    - Landing-page P0 work published, so landing-page experience is no longer BELOW_AVERAGE
  why_the_landing_page_comes_first: >-
    Ad Rank is bid x Quality Score. Cutting the bid while landing-page experience reads
    BELOW_AVERAGE attacks the healthy half of the equation and would push Lost IS to rank above
    the current 47.86%.
  risk_of_acting_early: 'raises Lost IS to rank; unreadable because the structure just changed'
  risk_of_waiting: 'roughly $29.57 median per click continues'
  rollback: restore the prior ceiling, one mutation per campaign
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---------------- PLAN-GA-AUD-1 ----------------
have = [s for s in segs if "id" in s]
(C / "plans/2026-09-02-plan-ga-aud-1-audience-observations.yaml").write_text(f"""# PLAN-GA-AUD-1 - SEARCH AUDIENCE OBSERVATIONS
# STATUS: BLOCKED - NOT FINGERPRINTED. NOT APPROVED. DO NOT EXECUTE.

change_plan:
  plan_id: PLAN-GA-AUD-1
  plan_title: Search audience observations
  approval_type: AUDIENCES
  priority: P3
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    Exact segment IDs could not be resolved. A live read returned {len(have)} usable remarketing
    user lists in this account. The standing rule is explicit - do not guess segment names or
    IDs - so no criterion can be specified exactly, and rule 18 forbids fingerprinting
    placeholders.
  target: {{child_customer_id: '{CID}', campaign_id: '{SURV}'}}
  mode: OBSERVATION ONLY
  initial_bid_modifier: '0%'
  never: 'Audience TARGETING mode. It would restrict Search reach.'

  live_read_2026_09_02:
    remarketing_user_lists_available: {len(have)}
    detail: >-
      The account has no usable first-party remarketing lists of its own. Website-visitor,
      engaged-visitor, returning-visitor, form-starter and phone-click lists all require a
      remarketing tag collecting for long enough to reach the Search minimum, which has not
      happened - the account has 21 lifetime clicks.
    evidence_file: clients/softwind-power-washing/snapshots/audience-segments-2026-09-02.json

  segments_wanted_when_resolvable:
    first_party:
      - All website visitors
      - Engaged website visitors
      - Returning visitors
      - Form starters
      - Phone-click visitors
      - Past converters
    google_provided:
      - Homeowners (detailed demographic)
      - In-market - Home Improvement
      - In-market - Home and Garden Services
      - In-market - Residential Cleaning Services
    excluded_deliberately:
      - unrelated lifestyle segments
      - affinity-only categories with no service intent
      - employment and job-seeker audiences
      - contractor job seekers
      - pressure-washer equipment buyers
      - generic broad audiences that add no reporting value

  blocked_on:
    - A remarketing tag collecting long enough to build first-party lists
    - Resolving exact Google-provided segment IDs through the Google Ads UI audience picker
  sequencing_note: >-
    Audience work is a REPORTING enhancement, not a lead-generation action. Twelve criteria at 0%
    produce zero leads by design. With 21 lifetime clicks the observation data would be
    uninterpretable for months. It sits behind measurement, structure and landing pages.
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---------------- PLAN-GA-ASSET-1 ----------------
(C / "plans/2026-09-02-plan-ga-asset-1-asset-completion.yaml").write_text(f"""# PLAN-GA-ASSET-1 - FINAL SEARCH ASSET COMPLETION
# STATUS: BLOCKED - NOT FINGERPRINTED. NOT APPROVED. DO NOT EXECUTE.

change_plan:
  plan_id: PLAN-GA-ASSET-1
  plan_title: Final search asset completion
  approval_type: ASSETS
  priority: P2
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    Every remaining gap is blocked on a client-supplied fact or file. Nothing can be specified
    exactly, so nothing can be fingerprinted.
  target: {{child_customer_id: '{CID}', campaign_ids: ['{SURV}', '{RET}']}}

  live_read_2026_09_02:
    campaign_level: {json.dumps(D["campaign_assets"])}
    customer_level: {json.dumps(D["customer_assets"])}
    parity: 'COMPLETE per campaign - 4 sitelinks, 4 callouts, 1 structured snippet, 1 call asset'
    do_not_recreate: true

  gaps:
    - gap: Business-name asset
      status: BLOCKED
      blocker: >-
        The verified business identity is genuinely ambiguous. client.yaml records
        "Softwind Powerwashing & Paver Sealing", the Google Ads account is named
        "Softwind Power Washing", and every landing page currently renders
        "Softwind Landscape & Masonry". Paver sealing is an EXCLUDED service. Guessing between
        these would put an unverified trading name in a live ad.
      needed_from_client: the exact legal or trading name to use in ads
    - gap: Business logo asset
      status: LIVE BUT NEEDS REVIEW
      detail: >-
        A BUSINESS_LOGO asset already exists at CUSTOMER level. It is not linked at campaign
        level. Confirm it is the correct Power Washing logo before promoting it.
    - gap: Image assets
      status: BLOCKED
      blocker: >-
        A repository-wide search found NO approved, rights-cleared Softwind project images.
        Stock imagery is not permitted without Walter's explicit approval, AI imagery may never
        be used as completed-project proof, and a public website image is not rights-cleared
        merely because it is published.
      needed_from_client: rights-cleared photographs of completed Power Washing work
    - gap: Call-asset schedule
      status: BLOCKED
      detail: >-
        The single call asset 403335872180 stops at 17:00 while both campaigns run to 18:00. The
        asset is SHARED by both campaigns, so editing its schedule rewrites hours everywhere it
        is linked. client.yaml records can_answer_after_hours as UNKNOWN.
      needed_from_client: whether (631) 502-7946 is answered 17:00-18:00 Mon-Fri
    - gap: Location asset
      status: DEFERRED
      detail: Requires a Business Profile link decision. Not launch-critical.
    - gap: Sitelink destinations
      status: DEFERRED
      detail: >-
        Sitelinks point at softwindli.com rather than the offer subdomain, which splits
        attribution. Real but not launch-critical; keep account-level sitelink cleanup separate
        from additions.
  approval_owner: Walter Correa
""", encoding="utf-8")

# ---------------- PLAN-GA-RETIRE-1 ----------------
(C / "plans/2026-09-02-plan-ga-retire-1-retirement.yaml").write_text(f"""# PLAN-GA-RETIRE-1 - DUPLICATE CAMPAIGN AND LEGACY RESOURCE RETIREMENT
# STATUS: BLOCKED - NOT FINGERPRINTED. NOT APPROVED. DO NOT EXECUTE. PAUSE ONLY, NEVER DELETE.

change_plan:
  plan_id: PLAN-GA-RETIRE-1
  plan_title: Duplicate campaign and legacy resource retirement
  approval_type: PAUSE
  priority: P2
  approval_status: NOT APPROVED
  execution_status: DO NOT EXECUTE
  fingerprint: null
  fingerprint_withheld_because: >-
    The new resources went live 2026-09-02 17:39 and have not served a single impression yet.
    Retirement requires that replacements be enabled, eligible, SERVING, correctly routed and
    verified - and that no replacement is dark. None of that is demonstrable on day zero.
  method: 'PAUSE ONLY. Deletion requires a separate destructive-action approval.'
  target: {{child_customer_id: '{CID}'}}

  overlap_evidence_to_re_examine_after_data:
    query_overlap: '5 search terms served in BOTH campaigns - 26.7% of clicks, 24.8% of spend'
    keyword_overlap: 'identical 107 keyword rows in each campaign'
    shared_geography: 'identical 80 locations + Connecticut exclusion'
    shared_schedule: 'identical Mon-Sat 08:00-18:00'
    shared_goals: 'identical biddable conversion goals'
    shared_landing_pages: 'the Islip offer page serves in both'
    shared_assets: 'identical asset loadout'
    budget_fragmentation: '$41.50 + $41.11 across two campaigns chasing one demand pool'
    conversion_data_fragmentation: 'zero conversions, so nothing to fragment yet'

  retirement_order:
    - {{step: 1, what: 'Displaced duplicate positive keywords', detail: '30 objects across 10 legacy ad groups; list in snapshots/launch1-delta-2026-09-02T125154.json'}}
    - {{step: 2, what: 'Displaced duplicate ad groups', detail: '202870585430 Power Washing Services Near Me, 202870585590 Power Washing Company Near Me'}}
    - {{step: 3, what: 'Weak old RSAs, only after replacements have served', detail: 'the remaining legacy ads in campaign 24145053510'}}
    - {{step: 4, what: 'Zero-volume city ad groups', detail: '202870585630 Islip, 202870585670 West Islip, 202870585830 Dix Hills - 1 impression between them all-time'}}
    - {{step: 5, what: 'Legacy mixed-intent ad groups', detail: '205713509664, 205713509704, 205713509744'}}
    - {{step: 6, what: 'Campaign {RET} - LAST', detail: 'Walter has instructed it stays ENABLED as the transition campaign. Retirement needs separate analysis, plan, fingerprint and approval.'}}

  every_pause_action_must_carry:
    [exact resource ID, current status, the replacement resource, evidence the replacement is
     live and serving, historical performance, risk, rollback]
  approval_owner: Walter Correa
""", encoding="utf-8")
print("part3 plans written")
