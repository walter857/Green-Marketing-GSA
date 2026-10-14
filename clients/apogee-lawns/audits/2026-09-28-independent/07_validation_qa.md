# 07 — Validation and QA results

## Validators run (actual output)

| Validator | Result |
|---|---|
| `scripts/validate_work_order.py` × 2 (task + canonical, with `--client`) | PASS, exit 0 (both) |
| JSON schema `schemas/work-order.schema.json` | 0 errors (both) |
| `tests/test_apg_negmatch.py` + `tests/test_apg_lead_id_contract.py` | 13 passed |
| `scripts/validate_apg_0928_package.py` (new, Apogee-specific) | **36 passed, 0 failed, exit 0** |
| `scripts/validate_audit_package.py` (existing) | **Not applicable**: hard-coded to another client's package (24 locations, ClickCease, other conversion IDs). Not modified |
| `scripts/validate_campaign_plan.py` | Not run: no new campaign or ad group is proposed |

Disclosure: the first run of the package validator failed its phone-number check with 833 hits. The pattern matched any
10-digit run, so it flagged customer IDs, criterion IDs and Unix timestamps. It was replaced with a pattern for formatted
numbers and E.164 `+1XXXXXXXXXX`, which is the format WhatConverts returns and therefore the format any leaked caller
number would take. With that pattern the check passes, and every number found is on the documented business allowlist.

## Red-team review (CLAUDE.md checklist)

| Item | Result |
|---|---|
| Client truth | name, ID, service and vertical match the profile; scope approval reused, not manufactured; Omaha exclusion honoured |
| Campaign strategy | one strategy; alternatives rejected with numbers (`07_proposed_change_manifest.yaml` → `rejected_with_reason`) |
| Search intent | whitelist classification; zero-conversion terms not negated; protected buyer terms untouched |
| Conversion isolation | no conversion change proposed; website-call promotion deferred until a real call is observed |
| Mutation necessity | DEV-T changes one live value that differs from intent; objects 2–3 run only if the readback shows they are real |
| API field validity | `campaign_criterion.bid_modifier` and `ad_group_bid_modifier.bid_modifier` are selectable and mutable in v25; the "from" values were read live with field presence |
| Status handling | campaign status observed and preserved; 0 enables |
| Asset support / character limits | no new assets or ads |
| URL mapping | live final URL verified 200 in a browser; no change |
| Location targeting | live 14 = approved 14; PRESENCE; no change |
| Budget math | $16.44 × 30.4 = $499.78 ≤ $500; no change |
| Landing-page template compliance | handoff only; LP content not redrafted; two published drafting notes flagged |
| Unsupported claims | none added; the EverLights claim on the live LP flagged for confirmation |
| Mutation counts | DEV-T 1–3 updates; KW-P 6 creates (gated, not fingerprinted) |
| Artifact hashes | DEV-T fingerprint `46060B03F5C9` recomputed by the validator |
| Bundle completeness | 14 required files present |

## Handling incident (disclosed)

While aggregating WhatConverts leads, a script printed the values of the lead field `phone_number`, which holds **caller
numbers (PII)**, into this session's console output, having assumed it was the tracking number. **Nothing was written to
disk and the values are not repeated in any file or report.** The re-run used only `tracking_number`, and the saved
aggregates exclude every contact field. The package validator confirms that no unexpected phone number appears in any
deliverable or run-B evidence file.

## Not inspected / not tested

- **Not inspected:**
  - Google Ads UI notices: advertiser verification and any new-account spending notice. Neither is exposed by the API,
    and the UI was not re-attempted after run A's browser freeze.
  - WhatConverts UI: number inventory, DNI settings and the Google Ads integration.
  - Gravity Forms admin: confirmation settings and hidden-field parameter names.
  - WordPress admin and SiteGround cache settings.
  - The CRM (Service Autopilot).
- **Not tested (not authorized):**
  - Any form submission, test call, ad click, fabricated GCLID or production dataLayer event.
  - The Google forwarding-number swap for ad visitors.
  - Rendering on a tablet-width screen.
- **Unexplained:** the `change_status` entries at 02:33:58 (budget) and 11:47:23 (campaign + ad groups) on 2026-09-28.
  Re-query `change_event` after 24 hours.
