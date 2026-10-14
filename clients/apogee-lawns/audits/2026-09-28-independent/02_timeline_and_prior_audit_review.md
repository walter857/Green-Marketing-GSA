# 02 — Reconciled timeline (2026-09-16 → now) and independent review of the earlier audit

All times America/Chicago unless marked. "Agency login" means `access@greenmarketingfl.com`, which is shared, so a
web-interface change cannot be attributed to a person (`client_type` names the interface, not who used it).

## Timeline

| When (CT) | What | Who / how | Evidence | Receipt? |
|---|---|---|---|---|
| 09-16 | Identity gate, conversion actions 7772803337 / 7773013199 / 7773043879 created | API (APG-0916-CONV-A/A2) | receipts 2026-09-16-stageA-* | yes |
| 09-16 19:01 | Billing setup 8587299012 APPROVED (earlier two CANCELLED) | owner, outside this repo | `billing_setup` | n/a (owner action) |
| 09-17 12:29–12:31 | Budget + campaign created **PAUSED**, 2 ad groups, 5 keywords, 75 negatives, 4 RSAs, 7 assets | API (APG-0917-CAMP-I) | `change_event`, campi receipts | yes |
| 09-17 | Website call action demoted to Secondary | API (CONV-J) | convj receipt | yes |
| 09-17 13:52–14:10 | WordPress pages privacy (3), terms-conditions (17395), thank-you (1702) modified | site editor | `wp/v2/pages.modified` | none in repo |
| 09-17 16:27 | Call asset 422649064971 + campaign link | API (CALL-Q) | callq receipt | yes |
| 09-17 (afternoon) | GTM workspace 3 built (GTM-K, GTM-P); receipts: 0 versions, 0 publishes, gate BLOCKED | browser (Claude) | gtmk / gtmp receipts | yes |
| **09-17** | **GTM version 2 "Apogee \| PPC Tracking \| 2026-09" created and published** — Google tag, form conversion, **Calls from Website tag** | agency login, GTM UI | GTM Versions tab | **missing** — the GTM-P publication gate was never recorded as decided |
| 09-18 08:48 | LP page 183 last modified | site editor | `wp/v2/pages` | none |
| 09-18 11:18 | 4 RSAs change_status CHANGED (consistent with policy review finishing; all now APPROVED) | system (inferred) | `change_status` only | n/a |
| **09-21 09:04:56** | **Campaign PAUSED → ENABLED** | agency login, Google Ads web UI | `change_event` | **missing** — CLAUDE.md requires a separate enable approval after readback QA; none is on file. Reported as missing evidence, not as unauthorized behaviour |
| 09-21 09:47 / 16:24 | 7 text assets and the call asset change_status CHANGED | system (inferred: no change_event rows) | `change_status` | n/a |
| 09-21 | First impressions (2) | — | daily metrics | — |
| 09-23 | Last tablet impression | — | device × date | — |
| **09-25 08:26:21** | **Tablet criterion ~30002 updated; now −100% (excluded)** | agency login, web UI | `change_event` (empty payload) + current value | **missing** |
| 09-25 / 09-27 | Clicks: 1 ($5.52), 2 ($13.17) | — | keyword_view | — |
| 09-28 02:33:58 | Budget 15884926233 change_status CHANGED; amount still $16.44 | unknown | `change_status` only | **unverified what changed** |
| 09-28 11:47:23 | Campaign + both ad groups change_status CHANGED | unknown | `change_status` only; `change_event` empty so far | **unverified what changed**; all fields read match 09-17 intent |
| 09-28 12:32–12:43 | My run-A reads and view-only Google Ads / page browsing | Claude | evidence file mtimes (host UTC−4) | yes (run A files) |
| 09-28 12:41, 14:01 | 2 Gravity Forms "GF1" web-form leads in WhatConverts from the paid LP, source `(direct)`, second marked Repeat | unknown (pattern of a test) | WhatConverts API aggregates | none |
| **09-28 14:38:53** | **GTM version 3 "Add Conversion Linker tag" published** | agency login | GTM Versions + `gtm.js` Last-Modified | **missing** |

## Independent review of run A (`AUDIT-LOW-VOLUME-2026-09-28.md`)

| Run-A statement | Verdict | Evidence |
|---|---|---|
| 3 clicks, $18.69, CPC ≈ $6.23 | **Confirmed** | L14 |
| Search IS ≈ 72% | **Confirmed** for completed days (72.2%). Run A's figure mixed in a partial day (61 impressions); completed-day total is 52 | L15 |
| 75 negatives, 0 conflicts, no shared lists attached | **Confirmed**, and extended: 0 buyer-modifier probes blocked, 0 reachable Planner ideas blocked | 03 |
| "The whole reachable market was ~85 impressions" / "Lincoln area already saturated" | **Corrected.** Impressions ÷ IS estimates *eligible* auctions for these 5 keywords, these match types, English, Presence in 14 targets, **tablets excluded since 09-25**, and Google's own quality/eligibility model. It is not a count of local searches or buyers | L15, DOC (IS = impressions ÷ estimated eligible impressions) |
| Budget-lost IS "is pacing while it learns" | **Unsupported, withdrawn.** Budget loss appears on $0-spend days and spend never reached the budget, but the mechanism is unverified; "learning" was an unsupported attribution | 03/diagnosis §budget |
| "$8 cap is not the limiter" | **Incomplete.** Rank-lost top IS is 18.5%, absolute-top share 16.7%, click share 19.6% (≈15 estimated eligible clicks vs 3 received). The cap is a real constraint; raising it is uneconomic: $10 adds 0 forecast clicks, $12 adds 6.6 at ≈$19.55 each | L15, 04 |
| "Owner's 09-25 edit changed no field" | **Wrong.** Tablet is at −100% today; that edit is the only recorded change to that criterion | L6 |
| Add a `permanent holiday lights` SKAG (+20 clicks) | **Unsupported as buyer demand.** Holiday *installation* synonyms carry 0/0/10/0; the +20 comes from Phrase reach into mixed-intent queries | 04 |
| **Omaha is the biggest lever; recommend a separate campaign on a shared budget** | **Retracted.** The work order records Omaha as EXCLUDED, "settled — not to be reopened on search volume or website wording". Run A reopened it on exactly those grounds | L27 |
| Combined forecast 163 clicks / $768 | **Void** (includes Omaha) | — |
| Form conversion cannot fire because the thank-you URL redirects | **Conclusion stands, reasoning replaced.** The redirect alone proved nothing. What proves it: no page exists at the trigger's only matching path; WordPress redirects that URL to the LP before GTM loads; the required event is pushed nowhere | L20–L22 |
| "WhatConverts actively replaces, pool size 1, same number 402-526-5754" (09-17 record) | **Corrected.** Runtime cookie: WhatConverts replaces **402-202-7261** with **402-783-8482**; the paid page shows only 402-526-5754, so nothing is swapped there | L23 |
| GTM "published (version 2)" | **Updated:** version 3 went live today at 14:38:53 CDT | L18 |
| Advertiser verification / new-account spend notice unchecked | **Still unverified** (not exposed by API; Google Ads UI was not re-attempted) | — |
