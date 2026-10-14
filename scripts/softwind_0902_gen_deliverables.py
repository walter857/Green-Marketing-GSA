#!/usr/bin/env python3
"""Deliverables README, final summary, and ZIP archive."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "clients/softwind-power-washing"
DEL = C / "deliverables/2026-09-02-final-launch-package"
DEL.mkdir(parents=True, exist_ok=True)
R = "../.."   # from DEL back to the client folder

(DEL / "README.md").write_text(f"""# SOFTWIND POWER WASHING — FINAL LAUNCH PACKAGE

**Start here.**

## 1. Account identity

| | |
|---|---|
| Account | **Softwind Power Washing - Live** |
| Child customer ID | **1521725229** (152-172-5229) |
| Service | **Power Washing** · vertical `similar-local-service` |
| Scope approved by | Walter Correa, access@greenmarketing.com |

## 2. Execution timestamp

**PLAN-GA-LAUNCH-3A executed 2026-09-02 17:39:49 America/New_York.** Readback 29/29.

Same-day sequence: LAUNCH-1 create-paused 13:33 → 3B legacy guard 16:50 → 3C RSA-limit guard
17:12 → **3A enablement 17:39**.

## 3. What is live

**Campaign `24103511039` "Power Washing"** now runs the rebuilt six-group single-intent structure.

| # | Ad group | ID | Keywords | RSAs |
|---|---|---|---:|---:|
| 1 | Power Washing | `202870585390` | 10 | 2 |
| 2 | Pressure Washing | `202870585870` | 6 | 2 |
| 3 | House Washing | `202870585910` | 8 | 2 |
| 4 | Soft Washing | `202870586310` | 4 | 2 |
| 5 | Driveway Pressure Washing | `202870586110` | 4 | 2 |
| 6 | Patio Pressure Washing | `202870586150` | 6 | 2 |

**Campaign `24145053510` "Pressure Washing"** remains ENABLED as the transition campaign.

## 4. What remains paused

2 non-final `house washing company near me` criteria (3B guard) · 4 legacy RSAs (2 from 3B, 2
from 3C) · 24 legacy ad groups · 30 displaced duplicate keywords.

## 5. What was changed

| Date | Plan | Fingerprint | Change |
|---|---|---|---|
| 09-02 13:33 | LAUNCH-1 | `92FFF603CAFD` | created 28 keywords + 12 RSAs, all paused |
| 09-02 16:50 | LAUNCH-3B | `B9EDA34DA712` | paused 2 non-final keywords + 2 legacy RSAs |
| 09-02 17:12 | LAUNCH-3C | `40F940130E6D` | paused 2 legacy RSAs to clear the 3-RSA limit |
| 09-02 17:39 | LAUNCH-3A | `F91589D9EA2A` | enabled 5 ad groups + 28 keywords + 12 RSAs |

## 6. What was NOT changed

No campaign paused or renamed · no budget · no CPC ceiling · no bidding strategy · no negative
keyword · no audience · no demographic criterion · no asset · no schedule · no location · no
conversion action or goal · no website · no GTM · no WhatConverts.

## 7–14. Current Google Ads state

| | |
|---|---|
| Ad groups | 30 total, **17 enabled** (6 final + 11 legacy in campaign B) |
| Keyword objects | 242 total, **240 enabled**, 2 paused guards |
| Final keywords | **19 unique texts / 38 objects** — Phrase + Exact, **no Broad** |
| RSAs | 66 total, **52 enabled**; the 12 new ones are 2 per final ad group |
| Bidding | **Maximize Clicks (TARGET_SPEND)** both campaigns |
| CPC ceilings | **$30.00** both — unchanged |
| Budgets | **$41.50** and **$41.11** — unchanged |
| Campaign statuses | both **ENABLED** |

## 15. Landing pages

Six pages return HTTPS 200 with form and phone present. Final copy is **written and ready to
paste**; nothing is published yet. Titles, H1s and the countdown are unchanged in production.

## 16. Tracking

Form conversion fires after submission (proven). Direct `/thank-you/` visits also fire it —
**owner-accepted temporary exception EXC-1**, developer ticket open. Website-call and call-asset
paths are not wired. WhatConverts captures attribution; DNI does not swap the number.

## 17–20. Assets · audiences · negatives · consolidation

Asset parity complete (4 sitelinks, 4 callouts, 1 snippet, 1 call asset per campaign); business
name, images and call-schedule gaps blocked on client input. **Zero audiences, zero demographic
criteria** — by design. **Zero ad-group routing negatives** — PLAN-GA-LAUNCH-2A is ready.
Consolidation deferred; campaign B retires last under its own approval.

## 21. Landing-page content

[01 Power Washing]({R}/landing-pages/2026-09-02-final/01-power-washing/) ·
[02 Pressure Washing]({R}/landing-pages/2026-09-02-final/02-pressure-washing/) ·
[03 House Washing]({R}/landing-pages/2026-09-02-final/03-house-washing/) ·
[04 Soft Washing]({R}/landing-pages/2026-09-02-final/04-soft-washing/) ·
[05 Driveway]({R}/landing-pages/2026-09-02-final/05-driveway-pressure-washing/) ·
[06 Patio]({R}/landing-pages/2026-09-02-final/06-patio-pressure-washing/)

## 22. Images

[MASTER-IMAGE-MANIFEST.csv]({R}/landing-pages/2026-09-02-final/MASTER-IMAGE-MANIFEST.csv) ·
[IMAGE-GAPS.md]({R}/landing-pages/2026-09-02-final/IMAGE-GAPS.md) —
**0 approved images found, 24 slots need client files.**

## 23. ClickUp tasks

[Task package]({R}/clickup-tickets/2026-09-02-final-launch/) ·
[CLICKUP-IMPORT.csv]({R}/clickup-tickets/2026-09-02-final-launch/CLICKUP-IMPORT.csv) — 15 tasks.

## 24. Audits

[Live vs planned]({R}/audits/2026-09-02-final-live-versus-planned-status.csv) ·
[Platform rules]({R}/audits/2026-09-02-current-google-ads-platform-rules.md) ·
[Routing matrix]({R}/audits/2026-09-02-final-routing-negative-matrix.csv) ·
[Universal negative candidates]({R}/audits/2026-09-02-universal-negative-candidates.csv) ·
[Demographics]({R}/audits/2026-09-02-demographic-and-household-income-decision.csv) ·
[Bid adjustments]({R}/audits/2026-09-02-advanced-bid-adjustment-decision.md) ·
[Architecture]({R}/audits/2026-09-01-authoritative-final-architecture.md) ·
[Keyword inventory]({R}/audits/2026-09-02-final-keyword-owner-map.csv) ·
[RSA QA]({R}/audits/2026-09-02-final-rsa-launch-qa.csv) ·
[R7A source audit]({R}/audits/2026-09-02-r7a-implementation-source-audit.md)

## 25. Receipts

[LAUNCH-1]({R}/receipts/2026-09-02-plan-ga-launch-1-execution-receipt.md) ·
[3B]({R}/receipts/2026-09-02-plan-ga-launch-3b-execution-receipt.md) ·
[3C]({R}/receipts/2026-09-02-plan-ga-launch-3c-execution-receipt.md) ·
[3A]({R}/receipts/2026-09-02-plan-ga-launch-3a-execution-receipt.md) ·
[R1B test]({R}/receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md)

## 26. Plans

[2A routing negatives]({R}/plans/2026-09-02-plan-ga-launch-2a-routing-negatives.yaml) ·
[NEG-1]({R}/plans/2026-09-02-plan-ga-neg-1-universal-negatives.yaml) ·
[BID-1]({R}/plans/2026-09-02-plan-ga-bid-1-cpc-control.yaml) ·
[AUD-1]({R}/plans/2026-09-02-plan-ga-aud-1-audience-observations.yaml) ·
[ASSET-1]({R}/plans/2026-09-02-plan-ga-asset-1-asset-completion.yaml) ·
[RETIRE-1]({R}/plans/2026-09-02-plan-ga-retire-1-retirement.yaml) ·
[Ledger]({R}/plans/2026-09-01-recovery-execution-ledger.yaml)

## 27. Approval queue

[Future approval queue]({R}/plans/2026-09-02-future-approval-queue.md) — **one** command is
currently valid:

```
APPROVE PLAN-GA-LAUNCH-2A 4A82B3B7C1EA FOR 1521725229
```

## 28. Risks

1. **Conversion counting is not yet trustworthy** — EXC-1 stands, so any reported conversion must
   be reconciled by hand.
2. **The sibling account still takes form data and the GCLID** from these pages, and still owns
   the website-call path.
3. **Two campaigns compete** for one demand pool on ~$82.61/day combined.
4. **Landing pages still carry the wrong brand title and city-locked H1** — copy is written but
   not published.
5. **Demand is small.** ~2,000 deduped local searches/month across the whole inventory.
6. **No routing negatives are live**, so early queries may land in the wrong ad group.

## 29. Next human decisions

1. Send the ClickUp P0 tasks to the developer.
2. Decide whether to run PLAN-GA-LAUNCH-2A now or after a few days of routing evidence.
3. Supply rights-cleared images and verified reviews.
4. Resolve the business identity for the business-name asset.
5. Confirm whether {'(631) 502-7946'} is answered 17:00–18:00 Mon–Fri.
6. Provide GTM and WhatConverts read access.
7. Decide on the sibling-account work order for tag scoping.

## 30. No guarantee

This is the **best current evidence-backed implementation**. It is not a guarantee of leads,
click-through rate, conversion rate, Quality Score or cost per lead. The account has produced
**zero conversions on 21 lifetime clicks**, so there is no baseline from which to forecast
honestly. Every expected effect in these files states its confidence, and figures that cannot be
verified are marked UNKNOWN rather than estimated.
""", encoding="utf-8")

(DEL / "FINAL-IMPLEMENTATION-SUMMARY.md").write_text("""# FINAL IMPLEMENTATION SUMMARY — 2026-09-02

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
""", encoding="utf-8")

# ---------------- ZIP ----------------
EXCLUDE_NAMES = {".env", ".env.local", "credentials.json", "token.json", "cookies.txt"}
EXCLUDE_EXT = {".pem", ".key", ".p12", ".mp3", ".wav"}
INCLUDE = ["deliverables/2026-09-02-final-launch-package", "landing-pages/2026-09-02-final",
           "clickup-tickets/2026-09-02-final-launch", "runbooks", "receipts", "plans", "audits"]
zp = C / "deliverables/softwind-power-washing-final-launch-package-2026-09-02.zip"
n, skipped = 0, []
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for rel in INCLUDE:
        base = C / rel
        if not base.exists():
            continue
        for f in sorted(base.rglob("*")):
            if not f.is_file():
                continue
            if f.name in EXCLUDE_NAMES or f.suffix.lower() in EXCLUDE_EXT:
                skipped.append(f.name)
                continue
            if f.suffix.lower() == ".png" and "r1b-t3" in f.name:
                skipped.append(f.name)   # test screenshots, not deliverables
                continue
            z.write(f, f"softwind-power-washing/{f.relative_to(C)}")
            n += 1
print(f"ZIP: {n} files -> {zp}")
print(f"excluded: {len(skipped)} ({sorted(set(skipped))[:6]})")
print(f"size: {zp.stat().st_size/1024:.0f} KB")
