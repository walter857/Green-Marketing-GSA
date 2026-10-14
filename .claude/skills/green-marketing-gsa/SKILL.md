---
name: green-marketing-gsa
description: Operate Green Marketing Google Ads workflows for landscaping, hardscaping, heating-cooling, and approved similar local-service clients. Use for client intake, account audits, Local Services Ads planning, BOFU Phrase/Exact campaign plans, two-RSA generation, paused creation, landing pages, conversion QA, search-term review, lead handling, offline outcomes, or profit reporting. Require the exact child account name, 10-digit child customer ID, and exact service before any client work.
---

# Green Marketing GSA

Read `CLAUDE.md` first and treat it as binding project policy.

## Start with the client gate

Require the exact child account name, 10-digit child customer ID, and exact service before reading or drafting for a client. Do not accept the MCC ID. If any item is missing, ask for it and stop.

One exception: if the exact account name and child ID are known but the service is not, run read-only service discovery from `prompts/01a-discover-services.md` using `clients/<client-slug>/service-discovery.yaml`. It waives only the service requirement, and only for itself. Present the candidate services with evidence, then stop and ask the user to confirm the exact service before anything else.

Read and validate `clients/<client-slug>/work-order.yaml` against `client.yaml`. Confirm the vertical is landscaping, hardscaping, heating-cooling, or an explicitly approved similar local service. For Google Ads work, verify the observed child account name and ID with a fresh read-only lookup.

## Route the task

- Client setup or a missing work order: read `prompts/00-onboard-client.md`.
- Eligible accounts: read `prompts/01-list-live-clients.md`.
- Service unknown, account known: read `prompts/01a-discover-services.md`.
- Audit: read `prompts/02-audit-account.md`.
- Keywords/SKAGs: read `prompts/03-keyword-research-skag.md`.
- Campaign creation: read `prompts/04-build-campaign.md`.
- RSAs/assets: read `prompts/05-generate-rsas-and-assets.md`.
- Landing page: read `prompts/06-build-landing-page.md`.
- Conversions: read `prompts/07-setup-conversions.md`.
- Search terms/negatives: read `prompts/08-clean-search-terms.md`.
- Reviews, LSA, lead handling, sales, dashboards, offline conversions, or deployment: read only the matching prompt under `prompts/09-*.md` through `prompts/15-*.md`.
- End-to-end build: read `prompts/16-full-system-runbook.md`.

## Enforce gates

1. Resolve the exact account name, child ID, service, vertical, and task from the work order.
2. Validate the work order against the client profile.
3. Use fresh read-only account data.
4. Draft and validate the proposed result.
5. Present exact scope and obtain approval tied to the plan fingerprint.
6. Create paused.
7. Read back and verify.
8. Require separate enablement approval.

Never treat `- live` as authorization. Never expose secrets. Never review-gate customers. Never use the legacy offline-conversion route for a new integration.
