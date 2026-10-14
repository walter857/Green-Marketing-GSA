# FINAL IMPLEMENTATION SUMMARY — 2026-09-02

**Best current evidence-backed implementation.** Not a guarantee of leads, CTR, CVR, Quality
Score or CPL.

## LIVE AND VERIFIED

| Item | System | Resource | Evidence | Next action |
|---|---|---|---|---|
| Six single-intent ad groups ENABLED | Google Ads | `202870585390/585870/585910/586310/586110/586150` | 3A receipt, 29/29 | monitor |
| 28 new keywords ENABLED, Phrase+Exact | Google Ads | see `launch3a-resource-ids.json` | 3A readback | monitor |
| 12 new RSAs ENABLED and APPROVED | Google Ads | `823152917197…917230` | 3A readback | monitor |
| Exactly 2 enabled RSAs per final group | Google Ads | — | 3A readback | — |
| No Broad Match anywhere | Google Ads | — | 3A readback | — |
| Both campaigns ENABLED, $30.00, Maximize Clicks | Google Ads | `24103511039`, `24145053510` | 3A readback | BID-1 later |
| Search Partners / Display / AI Max OFF | Google Ads | — | 3A readback | — |
| Presence targeting, Connecticut excluded | Google Ads | geo `21139` | 3A readback | — |
| Conversion goal hierarchy correct | Google Ads | 4 goals, 4 actions | verdict D, 2026-09-01 | — |
| GCLID/GBRAID/WBRAID/UTMs reach the form POST | Website | — | PLAN-R1B | — |
| Form submits and fires the Softwind conversion | Website | `AW-18369652705` | PLAN-R1B | — |
| Six Final URLs HTTPS 200, form + phone present | Website | — | 3A gate | — |

## CREATED AND ENABLED

The 40 objects from LAUNCH-1 (28 keywords + 12 RSAs) — created paused 13:33, enabled 17:39.

## CREATED BUT NOT ENABLED

None outstanding. The 4 guard resources are **deliberately paused**, not pending.

## PLANNED BUT NOT EXECUTED

| Plan | Actions | Fingerprint | Why not executed |
|---|---:|---|---|
| PLAN-GA-LAUNCH-2A routing negatives | 103 | `4A82B3B7C1EA` | **approval ready** — awaiting your call |
| PLAN-GA-NEG-1 universal negatives | 5 | none | all candidates have 0 clicks, $0 spend |
| PLAN-GA-BID-1 CPC ceiling | 2 | none | needs post-launch click data |
| PLAN-GA-ASSET-1 | 6 | none | client inputs |
| PLAN-GA-RETIRE-1 | ~30 | none | replacements must serve first |

## BLOCKED

GTM repair (no Tag Manager credential) · WhatConverts repair (empty API token) · sibling-account
tag scoping (needs its own work order) · business-name asset (identity ambiguous) · image assets
(none rights-cleared) · call-asset schedule (answered hours unknown) · post-repair form test
(website work must ship).

## DEFERRED

Audience observations — exact IDs resolved (`9446096870`, `9446168598`, `30007`) but every list
is far below the ~1,000 Search minimum; largest holds 210. Campaign consolidation. Location
asset. Sitelink destination tracking.

## DEVELOPER WORK REQUIRED

6 P0 technical + 6 P1 page-copy + 1 image request + 2 P2 investigations = **15 ClickUp tasks**,
ready to paste. Start with `p0-01-form-success-event.md`.

## GTM WORK REQUIRED

Repoint the form conversion from the `/thank-you/` page path to `gm_power_washing_form_success`;
remove the duplicate container bootstrap; identify what injects `AW-17878095007`. **Blocked on
read access.**

## WHATCONVERTS WORK REQUIRED

Diagnose why DNI never reaches the DOM; choose one authoritative call architecture; preserve
attribution, recording, qualification and dedup. **Blocked on read access** — populate
`WHATCONVERTS_API_TOKEN` in the secure local environment, or grant a read-only user.

## CLIENT CONTENT REQUIRED

Rights-cleared project photographs (24 slots) · three service-relevant verified reviews per page
· the exact business identity for ads · confirmation the phone is answered 17:00–18:00 Mon–Fri ·
verified economics (close rate, job revenue, margin) — all currently UNKNOWN.

## APPROVAL REQUIRED

**One command is currently valid:**

```
APPROVE PLAN-GA-LAUNCH-2A 4A82B3B7C1EA FOR 1521725229
```

## NO LONGER NEEDED

The three zero-volume city ad groups · the `house washing company near me` keyword texts (bucket
collapse) · the hamlet-heavy legacy RSAs.

## SUPERSEDED OR VOID

| Item | State |
|---|---|
| `PLAN-GA-LAUNCH-2` | superseded by 2A |
| `PLAN-GA-LAUNCH-3` | superseded by 3A |
| `PLAN-GA-LAUNCH-4` | superseded by PLAN-GA-RETIRE-1 |
| `PLAN-R7A` / `65A748A51E48` | **SUPERSEDED — DO NOT HONOR** |
| `D04DBC638033` | **VOID — DO NOT HONOR** (wrongly scoped 3A variant) |
| `BC0A5A7258E2` (PLAN-R3B $12) | superseded |
| `97D8B268A80A`, `B57E427D07C5`, `DFF115FF4D26` | void, in the do-not-honour registry |
| Earlier "F91589D9EA2A is void" note | **retracted** — it was blocked, not wrong, and it executed |

## 2026-09-02 SECOND RUN

| Deliverable | State | Proof |
|---|---|---|
| Google Drive package | **DONE** | 89 files, 6/6 folders readback PASS, not public |
| ClickUp tasks | **NOT DONE** | no ClickUp access exists in this environment |
| PLAN-GA-BID-2 | **EXECUTED 2026-09-02** | `3F1AB2CCFBDA`, gate 25/25, readback 20/20 |
| Selected CPC ceiling | **$18.00** both campaigns | $14 rejected on the $15.09 TOPlow cliff |
| Google Ads changes | **2 mutations** | ceilings $30.00 -> $18.00; budgets unchanged |
| Approved images | **0 of 24** | whole-Drive search returned no Softwind imagery |
| Landing pages | **NOT PUBLISHED** | developer handoff only |
| Routing checkpoint | **DEFERRED to 2026-09-03** | structure served ~21 minutes on 09-02 |

PLAN-GA-BID-2 is complete. The next open item is the routing-negative decision at the
2026-09-03 checkpoint (`PLAN-GA-LAUNCH-2A`, `4A82B3B7C1EA`) — hold until evidence exists.
