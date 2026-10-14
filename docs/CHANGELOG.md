# Changelog

## Unreleased

- Added a final-URL-suffix-only `SITE_OR_TRACKING` branch to
  `scripts/execute_approved_plan.py`. The subplan was listed in `SUBPLANS` but had
  no `build()` branch. The branch writes `campaign.final_url_suffix` and nothing
  else: it refuses any operation other than `SET_CAMPAIGN_FINAL_URL_SUFFIX`, any
  `proposed_state` that is not a final URL suffix, anything mentioning a tracking
  template or a ClickCease URL, and any suffix over 2,048 characters. The field
  mask is a hardcoded literal, so an account or campaign tracking template cannot
  be written through this path by construction. Seven tests pin those guards.

- Added `scripts/yaml_strict.py`, a YAML loader that REJECTS duplicate mapping
  keys. PyYAML's `safe_load` silently keeps the last value when a key repeats, so
  a config file can look correct while quietly discarding an earlier definition.
  The loader also cross-checks against a parser-independent text scan.
- Added a pause-only `STATUS` branch to `scripts/execute_approved_plan.py`.
  `STATUS` was already listed in `SUBPLANS` but `build()` had no branch for it,
  so any plan using it died with "subplan STATUS is not executable by this
  script" - which made keyword pauses unexecutable by the repository's own
  executor. The branch refuses any operation other than
  `PAUSE_AD_GROUP_CRITERION` and any `proposed_state` other than `PAUSED`, so it
  can only ever reduce delivery: it cannot enable, remove, or touch any other
  resource type. Five tests pin those guards.
- Recorded verified live facts in `clients/softwind-landscape-masonry/client.yaml`
  that had been left UNKNOWN: conversion tracking id, the six live campaign names
  with ids and statuses, both landing-page URLs, the displayed phone number,
  PRESENCE location option, the GA4/GTM/WhatConverts/ClickCease integrations, and
  the platform account spending limit. Genuine business unknowns (CRM, qualified-
  lead definition, margins, answering hours) remain UNKNOWN. Every value carries
  an evidence tag naming its source.

- `validate_work_order` now accepts a work order whose `exact_primary_service` is
  not the client profile's `primary_service` but IS listed in
  `client.offer.services_in_scope`. One Google Ads account can carry more than one
  approved service - Softwind Landscape & Masonry runs a Patio campaign and a
  Pavers campaign - and the old rule made a second service impossible to validate
  without a duplicate client folder. The check is no weaker: the service must
  still appear in the client profile, and a service absent from both fields is
  still rejected. Two tests added.
- Rebuilt `clients/softwind-landscape-masonry/client.yaml` on the canonical
  `templates/client/client.example.yaml` schema. It previously nested Google Ads
  identity under `client.account`, which the validator does not read, so the
  profile could never validate.
- Added `work-order-a-patio-construction.yaml` and
  `work-order-b-paver-installation.yaml` for the 2026-09 Patio and Pavers recovery
  program, and marked the single-service `work-order.yaml` superseded.


## 0.6.0 - 2026-08-14

- Added the binding `Expert Autonomy and Decision Rights` section to `CLAUDE.md`. Claude now operates as Green Marketing's senior Google Ads strategist: it chooses one recommended strategy, defends it, and proceeds rather than presenting a menu of technically equivalent options.
- Enumerated the decisions Claude owns outright — campaign architecture, ad-group structure, keyword themes, match types, negatives, bidding, budget allocation inside the approved cap, RSA copy and pins, assets, landing-page mapping, conversion-goal architecture, API fields and masks, asset reuse, mutation necessity, validation rules, QA, monitoring and optimization priorities.
- Defined a nine-level evidence hierarchy in which fresh account data outranks agency policy, and agency defaults became explicit fallbacks rather than ceilings.
- Required one complete internal red-team review across seventeen dimensions before any plan fingerprint is generated, so drafts are corrected internally instead of through user-facing checkpoint sequences.
- Narrowed escalation to nine triggers: unverifiable business facts, conflicting authoritative sources, ambiguous scope, public-facing claims, business preferences, missing access, external-write approval, destructive or scope-expanding actions, and legal/privacy/security risk. Routine technical questions are now a policy violation.
- Added the `expert_autonomy` block to `config/agency.yaml` with the owned-decision list, escalation triggers, evidence hierarchy, and the seventeen-item self-review checklist.
- Added `tests/test_expert_autonomy.py`: 29 tests that fail if the instructions ever permit external writes without approval, require user selection for routine technical choices, allow invented client facts, skip self-review before fingerprinting, allow enabling during creation, or permit repeat questioning without new evidence.
- Left every external-write gate untouched. Plan fingerprints, create-paused approval, separate enablement approval, budget-change approval and destructive-action approval all still apply. Autonomy governs judgment, never permission.


## 0.5.0 - 2026-08-14

- Removed the path by which `initialize_landing_page_drive --apply` could copy the canonical client example straight to `Landing Page Content Template - Master`. That copy carried every source-client fact under a name that claims the document is a clean template.
- `plan_landing_page_drive` now plans folders only, `apply_plan` refuses any `copy` action, and `google_drive.py` contains no `files.copy` call at all.
- Added `src/gm_gsa/master_template.py`: the single apply sequence and the only `files.copy` in the repository. Its destination name is hard-coded, so the document is always born as `TEMP - Master Template Scrub In Progress`.
- Required order, each step gated by the one before it: copy canonical to TEMP, scrub only that copy, re-read it from the API, verify zero residual source-client facts, verify the structural fingerprint against the canonical source, rename to the final master name, then record the verified root-folder and master-document IDs in `config/google-drive.yaml`.
- Added `assert_not_unscrubbed_master`, which refuses to create or copy any resource under the final master name. Only a rename of an already validated copy can reach that name.
- Added `record_verified_ids`, which writes the two non-secret Drive IDs after validation, refuses anything that is not a bare Drive ID, and refuses to record the canonical source as the master.
- Made the sequence idempotent and non-destructive: an existing validated master is reused, an orphan TEMP copy stops the run for review, duplicate exact-name matches stop the run, and no failure path deletes, trashes, moves, shares, or re-permissions anything.
- Corrected the approved hierarchy in `CLAUDE_GOOGLE_DRIVE_SETUP_PROMPT.md`. There is no `Clients/` level; client folders are direct children of `Green Marketing Landing Pages`, and `create_clients_folder` stays `false`.
- Fixed `scrub_master_template.py`, whose apply path asserted the write guard against the copy *source* rather than the destination and therefore always raised. It now delegates to the shared pipeline instead of duplicating it.
- Added 62 tests (176 to 238), including proofs that no unscrubbed final master can be created, that the canonical document is never a write target, that validation failure produces zero rename calls, and that a dry run writes nothing to Drive, Docs, or local configuration.

## 0.4.0 - 2026-08-07

- Added `src/gm_gsa/audit.py` and `scripts/audit_account.py`: a read-only account audit over last-30, previous-30, and last-90-day windows.
- Every audit read goes through the existing `assert_read_only_query` guard, so only GAQL `SELECT` statements can run. A mutating query raises instead of being recorded as a soft error.
- Isolated each query: one failure is recorded in `read_errors` and skipped, so an unsupported field never becomes a silent gap or a dead run.
- Covered conversion actions and per-action breakdown, campaign settings and budgets, campaign criteria, shared and ad-group negatives, keyword quality components, search terms, ads, RSA asset performance labels, asset policy, device/network/day/hour/geo segments, and a daily series.
- Used presence checks for optional metrics and bid modifiers. An unset impression share now reports as unavailable instead of `0`, and a device bid modifier of `0.0` is distinguished from "not set" so a `-100%` device exclusion is visible rather than inferred.
- Scrubbed emails and phone-shaped digit runs out of search-term text before anything is written to a snapshot, and ran the existing secret-redaction check over the whole report.
- Recorded the API's own field-compatibility limits in tests: budget-lost impression share cannot be selected below campaign level, and phone metrics cannot be selected on `CUSTOMER`.
- Added `clients/pro-green-dallas/client.yaml` and `work-order.yaml` for the confirmed scope: landscaping, sprinkler and irrigation repair, read-only audit, all write permissions false.

## 0.3.0 - 2026-08-07

- Added a narrowly scoped, read-only service-discovery workflow for accounts whose exact service is not yet known. It waives only the exact-service requirement, and only for itself.
- Added `schemas/service-discovery.schema.json`, `clients/_template/service-discovery.yaml`, `src/gm_gsa/service_discovery.py`, `src/gm_gsa/landing_pages.py`, `scripts/validate_service_discovery.py`, `scripts/discover_services.py`, and `prompts/01a-discover-services.md`.
- Kept the exact-service requirement unchanged for audits, drafts, campaign builds, campaign revamps, landing pages, conversions, deployment, and every Google Ads write. `work_orders.py` and its schema were not modified, and `service-discovery` is deliberately not an allowed work-order task type.
- Gated discovery on the exact child account name, the 10-digit child customer ID, a fresh identity lookup, the manager-account link, and a non-manager, non-test account. Any mismatch stops the workflow.
- Rejected any discovery document that names a service, vertical, scope approval, or plan, or that requests a task type other than `service-discovery` or a mode other than `read`.
- Restricted discovery to GAQL `SELECT` statements and landing-page HTTP GET. Any query containing a mutating keyword is refused before it reaches the API.
- Added `config/service-discovery-lexicon.yaml` so synonyms group into one candidate service while meaningful differences between services are preserved. Confidence requires more than one kind of evidence; landing-page text alone can never exceed low.
- Added 43 tests covering the discovery gate, the identity and manager-link stops, the read-only query guard, classification confidence, and landing-page reading.
- Fixed enum rendering in `src/gm_gsa/google_ads.py`. On Python 3.11+, `str()` on an API `IntEnum` returns the numeric value, so `account_snapshot` had been recording campaign status and channel as digits. Both now use the shared `enum_name` helper.

## 0.2.0 - 2026-08-06

- Restructured the package around `START_HERE.md`, ChatGPT Project instructions, client work orders, vertical references, and a copyable client workspace.
- Added a hard gate requiring the exact child account name, 10-digit child customer ID, and exact service before any client-specific work.
- Limited active scope to landscaping, hardscaping, heating-cooling, and explicitly approved similar local services.
- Added deterministic work-order validation, schema, command, and tests.
- Preserved and mapped the complete supplied video transcript.
- Changed default communication to plain American English.

## 0.1.0 - 2026-08-06

- Initial Green Marketing Google Search Ads operating system.
- Added paused-by-default API publisher, plan fingerprint approval, account discovery by `- live`, BOFU/SKAG policies, prompts, intake templates, and preserved source documents.
- Updated offline-conversion guidance for the post-June 15, 2026 Data Manager API requirement.
