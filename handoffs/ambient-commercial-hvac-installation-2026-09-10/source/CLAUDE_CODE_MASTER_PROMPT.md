# Ambient Cooling — Final Search Optimization, Policy, Boiler, Auction, and Commercial HVAC Build

Run this as one continuous evidence-first Claude Code session. Continue through every independent task even when one workstream is blocked. Do not stop for routine questions. Ask the user only when a browser must be selected, a human login/MFA/CAPTCHA step is required, or a new live mutation lacks an exact approved fingerprint.

## 1. Account identity — mandatory before every live write

- Account: `Ambient Cooling - Live`
- Customer ID: `2401959466`
- Account type: non-manager
- Test account: false
- Timezone: `America/New_York`
- Currency: `USD`
- Green Marketing manager: `3373711342`, ACTIVE
- ClickCease manager: `2815082755`, ACTIVE

Stop the affected write if any identity field differs. Finish all safe read-only work.

## 2. Current durable state — reconstruct, do not replay

Treat reports, plans, receipts, the fingerprint ledger, fresh API reads, and change history as evidence. Never rely on terminal memory.

Already completed:

- `AMB-0910-BUD-2 / 93541FBB5D7F`: executed. Gas Boiler Repair budget is `$5.00/day`; HVAC Replacement budget is `$20.00/day`. Total Search daily budgets are `$421.55`; the 30.4-day planning ceiling is `$12,815.12`, leaving `$184.88` below the `$13,000` hard maximum.
- `AMB-0909C-NEG-COMMERCIAL / 9F88FEE76803`: executed. The account-level Broad negative `commercial` was removed.
- `AMB-0909-ADS-1 / 11A79347A296`: executed. Ads `820900825434` and `820944944368` are paused.
- Competitor negatives, vehicle negatives, Hanover removal, Savage removals, approved schedules, replacement RSAs, and prior sitelink work were already executed and verified. Do not duplicate them.

Known current Maximize Clicks CPC ceilings:

- AC Repair: `$25`
- HVAC Repair: `$25`
- HVAC Installation: `$30`
- HVAC Replacement: currently uncapped
- Gas Boiler Repair: currently uncapped

Validated but not yet approved in this instruction:

- `AMB-0910-CPC-CAP-1 / 7EA6922309EB`: Gas Boiler Repair uncapped → `$25`; HVAC Replacement uncapped → `$30`.

Rejected or stale:

- `AMB-0909C-CPC-INST-2 / 5D57E0EF3B70`: rejected. Never execute or revive it.
- Any prior Boiler package must be revalidated or superseded after the newly fixed landing page is fully tested.
- Any RSA fingerprint containing `Licensed & Insured` is stale for this task. Do not execute it.

## 3. Binding business decisions

- `$13,000/month` is the hard maximum for Google Search campaigns only.
- Local Services Ads belong to another department and another budget. Do not inspect, recommend, alter, forecast, or count LSA activity in this project.
- The objective is qualified lead volume at sustainable economics. Do not force spend into unprofitable clicks merely to reach `$13,000`.
- CPQL guardrails: AC Repair `$150`; HVAC Repair `$250`; HVAC Installation `$280`; HVAC Replacement `$280`; Gas Boiler Repair `$250`.
- WhatConverts credentials are configured. Test access without displaying, logging, or writing credential values or lead PII.
- Ambient serves commercial HVAC customers. Commercial installation is approved paid scope.
- Do not use `Licensed & Insured` in ads, assets, or landing-page copy in this workstream. No license number or insurance documentation is needed because the claim will not be used.
- Preserve existing Search location targets, Presence-only location behavior, paid schedules, conversion actions, tracking, GTM, WhatConverts, call behavior, ClickCease, manager links, and unrelated resources unless a separately fingerprinted plan explicitly changes one.

## 4. Resolve the disapproved ads without harming delivery

The two ads the user asked about are already safe operationally:

- `820900825434` — HVAC Installation campaign `24132507747`, ad group `202339087634`
- `820944944368` — HVAC Replacement campaign `24132507753`, ad group `200159223798`

Both are paused, `DISAPPROVED`, `REVIEWED`, `FULLY_LIMITED`, topic `CONSUMER_FINANCE`. Each ad group still has exactly two enabled and approved RSAs. Do not re-enable, edit, recreate, or duplicate either ad.

There are four additional paused legacy ads with the same topic:

- Gas Boiler: `820900825428`, `820900825431`
- HVAC Installation: `820900825437`
- HVAC Replacement: `820944944371`

Perform one exact six-ad policy inventory:

1. Pull fresh `ad_group_ad.policy_summary` data for only these six IDs, including policy topic, policy type, evidences, constraints, review status, and approval status.
2. In the authenticated Google Ads UI, open Policy details for the same six ads.
3. Confirm the URLs are HVAC service pages and identify whether any cited asset or destination actually promotes lending, credit, financing, or another consumer-finance service.
4. If the only issue is the incorrect `CONSUMER_FINANCE` classification, submit one precise appeal using `Dispute decision`. Do not choose `Made changes to comply` unless a specific finance-related item was actually corrected.
5. Do not remove ZIP-code targeting. The likely interaction is a false finance classification plus the finance policy's ZIP-targeting restriction, not a genuine HVAC targeting defect.
6. Keep all six ads paused after any successful appeal. The approved replacements already cover delivery.
7. If the appeal fails, wait at least 24 hours before another appeal, preserve the exact evidence, and draft a Google Ads Support case. Do not exhaust repeated appeals.
8. Report appeal IDs and final policy states. Claim no performance improvement from pausing or appealing legacy ads.

## 5. CPC control — protect economics without choking visibility

Do not treat the blended pre/post-cap history as one regime. The `$25/$25/$30` ceilings were added on 2026-09-04 at approximately 16:56 account-local time. The settled capped sample is only four valid clicks and zero conversions, so the current values are protective starting points, not proven optima.

Current working recommendation:

- Keep AC Repair at `$25`.
- Keep HVAC Repair at `$25` for now. A future `$35` test may be drafted only after better outcome data; it is not currently authorized.
- Keep HVAC Installation at `$30`. Launching Commercial HVAC Installation and changing this cap at the same time is prohibited because it would confound the result.
- Reproduce `AMB-0910-CPC-CAP-1 / 7EA6922309EB` for Gas Boiler `$25` and HVAC Replacement `$30`. Do not execute it unless the user supplies this exact line in the active Claude Code conversation:

  `APPROVE AMB-0910-CPC-CAP-1 7EA6922309EB 2 operations FOR 2401959466`

Before recommending any later ceiling:

1. Use settled data and separate uncapped and capped regimes at the exact change timestamp.
2. Reconcile paid-search leads through WhatConverts using GCLID, GBRAID/WBRAID, UTM, landing URL, referrer, tracking number, campaign, date, and lead status. Do not assume every non-GCLID Google lead is organic, GBP, or LSA.
3. Pull Keyword Planner historical and forecast data for the exact 75 Maryland targets and exact BOFU keyword set. Record low/high top-of-page ranges as market context, not recommended bids.
4. Pull campaign and ad-group Auction Insights for August 1–31, 2026 through Claude in Chrome as specified in section 6.
5. Evaluate valid clicks, click share, impression share, lost impression share by rank and budget, top and absolute-top rates, Quality Score components, search-term intent, verified qualified leads, CPQL, device, and conversion delay.
6. Calculate an economic CPC boundary as `CPQL target × verified qualified-lead rate`, but label it unusable when the verified sample is insufficient.
7. Require at least 20 valid clicks and preferably three unique qualified leads per campaign before declaring a ceiling permanent.
8. Change at most one variable per campaign and move a ceiling by no more than 20% per test.
9. Apply incremental spend stop-losses without a qualified lead: AC Repair `$150`; HVAC Repair `$250`; Installation `$280`; Replacement `$280`; Boiler `$250`.
10. If a campaign meets its CPQL target but valid click volume falls more than 50%, draft a separately fingerprinted ceiling increase of no more than 20%.
11. Monitor 24 hours and 72 hours for configuration/serving faults. Make the first performance judgment only after 14 settled days, excluding conversion-lag days.
12. Do not raise bids merely to spend the full budget. Expand tightly matched BOFU demand and improve relevance first.

## 6. Auction Insights through Claude in Chrome — read-only

Run `/chrome`. Use the connected native Windows Chrome browser whose live account header shows `Ambient Cooling - Live / 240-195-9466` and manager breadcrumb `Green Marketing`. The screenshot appears to use profile `Work`, but the live account identity is authoritative. If multiple connected browsers remain ambiguous, ask the user only which visible Chrome profile to select. Never request passwords, cookies, a profile directory, OAuth tokens, or verification codes. Let the user complete login, MFA, or CAPTCHA manually.

Set the exact date range `2026-08-01` through `2026-08-31`; do not use last 30 days. Export Search Auction Insights for:

- Each of the five exact live campaigns separately.
- Each exact serving ad group separately:
  - `SKAG | AC Repair Near Me`
  - `SKAG | HVAC Repair Near Me`
  - `SKAG | HVAC Installation`
  - `SKAG | HVAC Replacement Near Me`
  - `SKAG | Gas Boiler Repair`
- The pooled five-campaign scope as an optional baseline only.

Include Display URL domain, impression share, overlap rate, position above rate, top-of-page rate, absolute-top rate, and outranking share. Preserve `<10%` literally. If activity is insufficient, record `NOT_AVAILABLE_MINIMUM_ACTIVITY`; do not widen the window. Store CSVs and a manifest with identity, scope, date, timestamp, row count, headers, SHA-256, and export status under `evidence/auction-insights/2026-08/`.

This Chrome work is read + download + analyze only. Do not click Apply recommendations, Review campaigns, status controls, bid/budget fields, Edit, or pencil icons. Auction Insights alone never justifies a competitor negative or a higher bid.

## 7. Gas Boiler landing-page completion gate

The original heading defect is visibly fixed. The page now shows:

`Your Gas Boiler Repair in 3 Simple Steps`

Perform the remaining gate before creating or enabling `[boiler repair]`:

1. Render the live page in a real browser on desktop and mobile.
2. Confirm the old HVAC Replacement wording is absent from rendered text and HTML.
3. Confirm the title, H1, H2, canonical, boiler-specific CTAs, and `(410) 705-6354` phone display/link.
4. Confirm GTM `GTM-PQTPQ436`, WhatConverts, click-ID persistence, Privacy, Terms, thank-you behavior, and one Google Ads conversion per submission.
5. Use an approved non-production/test path to submit every distinct visible form once; do not create a real customer lead.
6. Test DNI with controlled paid-click parameters. Confirm the paid number and link swap correctly and `(410) 761-0932` never flashes or becomes clickable.
7. Inspect the three duplicate `id="gform_1"` elements. Require unique DOM IDs or evidence that duplication does not break validation, accessibility, submission, thank-you routing, or conversion tracking.
8. Save timestamped desktop/mobile screenshots and a functional QA receipt.
9. Revalidate the old exact-keyword package against the fresh account. If any before-state or payload changed, supersede it and issue a new fingerprint.
10. The intended Google Ads change remains one enabled Exact keyword `[boiler repair]` in ad group `202339087594`, with no Phrase/Broad keyword and no speculative negatives. Execute only after exact fingerprint approval.

## 8. Commercial HVAC Installation build

Use the supplied pack:

- `Ambient_Commercial_HVAC_Installation_Launch_Pack.docx`
- `COMMERCIAL_HVAC_COPY_PASTE.txt`
- four image assets in `images/`

Approved architecture:

- Existing campaign: `Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08`
- Campaign ID: `24132507747`
- New ad group: `SKAG | Commercial HVAC Installation`
- Proposed paid landing page: `https://offer.ambientcoolingandheating.com/commercial-hvac-installation/`
- Inherit the campaign's 75 Maryland Presence-only targets, approved schedule, conversion configuration, tracking template, call asset, and `$30` Maximize Clicks ceiling.
- Do not create a separate campaign in this workstream.
- Do not use Broad positive keywords at launch.
- Launch only Phrase and Exact forms of the canonical BOFU theme:
  - `"commercial hvac installation"`
  - `[commercial hvac installation]`

Use the two supplied RSAs. RSA A has three distinct service-led headlines pinned to Headline 1. RSA B is unpinned as a relevance/automation control. This is not a true evenly allocated A/B test unless Google Ads Experiments is used. Create both paused, read them back, and require a separate enable fingerprint.

Ad-group routing rules:

- Add `commercial` as a Broad ad-group negative to the existing residential `SKAG | HVAC Installation` only after the new commercial ad group, destination, keywords, and ads are enabled and eligible.
- In the new commercial ad group, add only the reviewed ad-group negatives in the supplied pack. Do not use campaign- or account-level `commercial` negatives.
- Do not block manufacturer names, city names, `free`, `quote`, `estimate`, `cost`, `pricing`, `building`, or `property manager`.

Landing page:

1. Build on staging from the supplied copy and four images.
2. Do not represent generated images as completed Ambient projects; treat them as illustrative imagery.
3. Preserve GTM, WhatConverts, click-ID/UTM capture, paid number `(410) 705-6354`, one conversion per form, canonical, Privacy, and Terms.
4. Use unique DOM IDs.
5. Do not use Licensed & Insured, emergency, 24/7, financing, rebates, guarantees, guaranteed savings, or `#1` claims.
6. Run desktop/mobile browser QA, form test, DNI test, tracking debug, and content/claim checks before publication.
7. If source, staging, backup, or publish authority is missing, complete the developer handoff and all Google Ads drafts but do not publish.

Create the commercial resources paused. Use one deterministic plan, validate-only, fingerprint, and readback. Do not enable until the landing page is live, QA passes, conflicts are clear, and the user supplies the exact enable approval.

## 9. CTR improvement protocol

- Do not edit approved serving RSAs in place.
- For any new challenger, create paused first.
- Use the exact service keyword in a headline.
- When pinning, pin three materially different keyword-forward headlines to Headline 1—not one fixed headline—so Google retains rotation in the most visible slot.
- Keep remaining headlines unique and unpinned.
- Do not pin Headline 3 as a required message because it is not guaranteed to show.
- Compare asset-level performance only after a settled sample. Judge CTR with device, position, query mix, and impression share controlled; the prior AC Repair CTR difference was confounded by device mix.
- Improvement is not proven until settled post-change data shows it.

## 10. Final deliverables

Return one consolidated report and one short ClickUp activity update containing:

1. Exact executed mutations and exact held plans.
2. Six-ad policy inventory and appeal results.
3. Current CPC ceilings, evidence, monitoring dates, stop-losses, and rollback values.
4. August campaign- and ad-group-level Auction Insights exports and analysis.
5. Gas Boiler desktop/mobile/form/DNI result and keyword eligibility.
6. Commercial landing-page, ad-group, keyword, RSA, negative, asset, and image status.
7. WhatConverts connectivity and paid-lead reconciliation without PII.
8. Readback and unrelated-resource verification.
9. No LSA analysis or budget mixing.
10. One consolidated approval block containing only fresh, safe, validated, unexecuted fingerprints.

Do not claim lower CPC, higher CTR, more conversions, or better CPQL until settled evidence proves it.

