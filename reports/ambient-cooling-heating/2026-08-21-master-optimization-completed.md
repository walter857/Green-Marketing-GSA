# Ambient Cooling — Master Optimization, Completed Run

**Child account:** `Ambient Cooling - Live` · `240-195-9466` / `2401959466`
**Manager:** Green Marketing `337-371-1342` · ClickCease Client Center `281-508-2755`
**Vertical:** heating-cooling · **Currency:** USD · **Timezone:** America/New_York
**Run date:** 2026-08-21 (account local) · **Phase:** identity → execute approved → audit → draft

---

## 1. Executive summary

Two approved mutations were executed and verified. Conversion Plan B removed the live
double-count so that exactly one Primary conversion action now exists per physical lead
surface. Two diversified HVAC Repair RSAs were created PAUSED and are in policy review.
Everything else was completed in read/draft/validate-only mode, producing four validated
packages for one consolidated approval.

The account's central constraint is **not budget**. Four of five campaigns are limited by Ad
Rank, quality or search volume. Only HVAC Installation is budget-constrained, and its
constraint is worsening while its economics are the best in the account. That is the single
budget change recommended.

**$13,000 is treated as a maximum, not a quota.** Month-to-date is $1,947.95. The recommended
budget increase is sized so that even at Google's maximum 2× overdelivery every remaining day,
August cannot exceed the maximum.

## 2. Identity verification — PASS

| Check | Result |
|---|---|
| Name | `Ambient Cooling - Live` ✅ |
| Customer ID | `2401959466` ✅ |
| Timezone / Currency | America/New_York / USD ✅ |
| `- live` marker | present ✅ |
| Manager / test account | false / false ✅ |
| Green Marketing `3373711342` | **ACTIVE** ✅ |
| ClickCease `2815082755` | **ACTIVE** ✅ |
| Local work order | `PASS \| Ambient Cooling - Live \| 2401959466 \| heating-cooling \| AC Repair` |

**Concurrency:** no live process on this machine references `2401959466`. Three python
processes exist; all belong to an unrelated project (customers `7239732058`, `2646876213`,
`9720978817`) plus one defunct read task of mine (0 CPU, no active task instance).

## 3. Fresh baseline (pre-mutation)

campaigns 23 · budgets 27 · ad groups 68 · ads 113 · keywords 6,968 · campaign criteria 13,810
· ad schedules 139 · locations 1,467 · campaign assets 283 · customer assets 1 · ad-group
assets 6 · shared sets 16 · shared criteria 7,015 · campaign-shared-set links 88 · conversion
actions 16 · IP exclusions 2,796 · ad-group negatives 5,500 · campaign negatives 11,848.

Change events for the five campaigns over 14 days show only this engagement's own API writes.
No foreign edits.

## 4. Changes executed

| Package | Fingerprint | Ops | Readback |
|---|---|---|---|
| Conversion Plan B | `03F125C189679E35` | 4 updates | **19/19 PASS** |
| Create-paused RSAs | `1D964296F5C7CE79` | 2 creates | **23/23 PASS** |

Nothing else was mutated.

## 5. Exact resource IDs changed

**Demoted to Secondary** (`primary_for_goal` only, `update_mask = ["primary_for_goal"]`):
`7643656486` WC Lead · `7643656075` WC Calls · `6498555484` Call BTN Click ·
`6498555481` Visit Thank you page

**Created PAUSED** in campaign `24132507750`, ad group `202339087674`:
`821714108336` (RSA A, direct response) · `821714108339` (RSA B, problem/decision)

## 6. Conversion configuration

**Primary + counted, after Plan B — exactly three:**

| ID | Action | Type / Origin | Surface |
|---|---|---|---|
| `6885463625` | Ambient Cooling - LP Submit Lead Forms | WEBPAGE / WEBSITE | form lead |
| `6885576934` | Ambient Cooling - Lp - Phone call leads | WEBSITE_CALL / WEBSITE | website call |
| `1068114183` | Calls from ads | AD_CALL / CALL_FROM_ADS | call from ad |

**Unchanged, as required:** counting method, attribution model, lookback windows, call-duration
thresholds (60s / 30s / 60s), conversion values, action status (all still ENABLED), action
names, historical records, customer conversion goals (9), campaign conversion goals, custom
goals (none exist), GTM, WhatConverts.

**One expected side-effect:** demoting to Secondary automatically sets
`include_in_conversions_metric = false` on those four — that is what Secondary *means*. The
update mask contained only `primary_for_goal`. Secondary observations are retained in **All
conversions**, which was the required outcome.

**Reporting propagation:** immediately after the change August still reads
`conversions = 3.0` / `all_conversions = 6.0`. Historical rows do not reprocess instantly and
no promise is made that they will. Re-query after propagation.

**Decision-gate record:** the WhatConverts console could not be inspected — no authenticated
session was available and credentials must not be requested. Per the approved decision rule, an
uninspectable or ambiguous WhatConverts state resolves to Plan B. The observed same-hour
co-firing on 2026-08-20 at 06:00 corroborates it.

## 7. Unique lead-event reconciliation

Two physical lead events exist since launch:

| Event | Evidence | Counted by |
|---|---|---|
| AC Repair call from ad, 2026-08-20 07:46:59 | `call_view`: **171 seconds, RECEIVED**, HIGH_END_MOBILE_SEARCH — the only `call_view` record ever on the five campaigns | `1068114183` |
| HVAC Repair form, 2026-08-20 06:00, mobile | fired `6885463625` **and** `7643656486` | now `6885463625` only |

Three reported conversions, two real events. Going forward the duplicate cannot recur.

## 8. WhatConverts findings

Verified from the Google Ads API only:

- WC Lead `7643656486` (UPLOAD_CLICKS) has fired **once ever** — 2026-08-20, HVAC Repair,
  value 0.0.
- WC Calls `7643656075` (UPLOAD_CALLS) has **never** fired.
- Only these two actions are upload-capable. `6885463625` (WEBPAGE), `6885576934`
  (WEBSITE_CALL) and `1068114183` (AD_CALL) are tag-based and cannot receive a standard
  offline upload. **This does not mean a tag action can never take an additional source** —
  Google supports multi-source conversions for eligible accounts, and this account already runs
  Enhanced Conversions for Leads (`enhanced_conversions_for_leads_enabled = true`,
  `accepted_customer_data_terms = true`). What is confirmed is only the current WhatConverts
  mapping.
- **WC Calls can duplicate `Calls from ads`**: the call-asset number (410) 705-6354 is itself a
  WhatConverts number, so an ad call is visible to both. This is why WC Calls was demoted.

**Still required from the console** (non-PII only): whether WC Lead uploads all vs
qualified-only; same for WC Calls; whether WC Calls includes Google call-asset calls; whether a
status change creates a new upload, adjustment, retraction or value update; whether an order ID
is sent.

## 9. RSA creation and policy status

Both created PAUSED, byte-identical to the approved plan, 15 headlines / 4 descriptions each,
no pinning, final URL `https://offer.ambientcoolingandheating.com/hvac-repair/`, paths
`/hvac-repair/severn-md`.

| Ad | Status | Approval | Review | Strength |
|---|---|---|---|---|
| `821714108336` | PAUSED | UNKNOWN | REVIEW_IN_PROGRESS | PENDING |
| `821714108339` | PAUSED | UNKNOWN | REVIEW_IN_PROGRESS | PENDING |

Zero policy topics on both. Polled three times over ~2 minutes; still in review, which is
normal (the preserved RSAs took roughly two hours on 2026-08-18). The swap package is prepared
and **gated on both reaching APPROVED / REVIEWED**.

Keyword density was deliberately reduced to **6 of 15** headlines per ad (from 11 and 8), with
9 unique non-keyword headlines across 8 idea groups. Six unsupported claims were removed and
replaced with landing-page-verified language.

## 10. Landing-page implementation status

Website source, staging credentials and GTM API access are **not available to this session**,
and credentials must not be requested. Local implementation of the real site code is therefore
impossible. The complete developer handoff stands: `4A5BB56E2F15A5D2` carries exact file paths,
PHP and JavaScript responsibilities, GTM variables/triggers/tags, 17 attribution fields, form
field mappings, 15 acceptance tests, a 7-cell browser matrix and a 6-step rollback.

`93A9DF4AA19675E8` adds the production deployment gate: 12-step deployment order, 13 acceptance
gates, backup/rollback with RTOs, and an explicit instruction that Privacy/Terms links may only
point at **verified existing** legal pages — no invented URL, no invented legal language.

Landing pages were re-verified in a real JavaScript browser: `/hvac-repair/` 168 KB and
`/ac-repair/` 166 KB, correct H1, GTM-PQTPQ436 and WhatConverts 105803 both present. An
intermittent 12 KB SG-Captcha challenge stub appears on repeated automation and clears on
retry — that is bot protection, **not** an outage, and must not be recorded as a failed test.

## 11. Pacing analysis (partial — checkpoint not reached)

The 2026-08-21 11:35 ET checkpoint had **not** passed at run time (account local 00:21 ET).
Data below is the most recent settled analysis; Aug 21 has no data yet. No budget decision was
made from an incomplete comparison — the recommendation rests on Aug 20, the first full day on
the restored schedule.

**Billable metrics, since launch (2026-08-14 → 2026-08-21):**
1,361 impressions · **45 billable clicks** · 433 filtered invalid (reported separately, never
added to spend) · **$1,947.95** · 3 conversions

| Campaign | Impr | Clicks | Invalid | Cost | CTR | CPC | Conv | IS | Budget-lost | Rank-lost | Abs top |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HVAC Installation | 756 | 28 | 22 | $824.58 | 3.70% | **$29.45** | 0 | 41.38% | **51.72%** | 6.90% | 21.22% |
| AC Repair | 146 | 9 | 212 | $612.45 | 6.16% | $68.05 | 1.0 | 35.71% | 0.53% | **63.76%** | 17.46% |
| HVAC Repair | 413 | 6 | 181 | $458.78 | **1.45%** | $76.46 | 2.0 | 30.34% | 0.00% | **69.66%** | 11.54% |
| HVAC Replacement | 46 | 2 | 18 | $52.14 | 4.35% | $26.07 | 0 | 31.58% | 0.00% | **68.42%** | 9.99% |
| Gas Boiler Repair | 0 | 0 | 0 | $0.00 | — | — | 0 | 9.99% | 0.00% | **90.01%** | 9.99% |

**Yesterday, 2026-08-20 — first full day on the restored schedule:**

| Campaign | Impr | Clicks | Cost | CTR | CPC | Conv | IS | Budget-lost | Rank-lost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HVAC Repair | 7 | 2 | $306.06 | 28.57% | **$153.03** | 2.0 | 50.00% | 0.00% | 50.00% |
| AC Repair | 25 | 2 | $280.27 | 8.00% | **$140.13** | 1.0 | 96.49% | 3.51% | 0.00% |
| HVAC Installation | 402 | 15 | $276.25 | 3.73% | **$18.42** | 0 | 36.18% | **63.82%** | 0.00% |
| HVAC Replacement | 38 | 2 | $52.14 | 5.26% | $26.07 | 0 | 80.00% | 0.00% | 20.00% |
| Gas Boiler Repair | 0 | 0 | $0.00 | — | — | 0 | 9.99% | 0.00% | 90.01% |

**Device:** mobile 36 clicks / $1,684.95 / CPC $46.80 / all 3 conversions; desktop 9 clicks /
$263.00 / CPC $29.22 / 0 conversions.
**Network:** Search only — 1,361 impressions, zero partner or display.
**Click type:** URL_CLICKS 29/$1,095.93 · CALLS 3/$261.35 (1 conv) · SITELINKS 4/$230.81
(1 conv) · LOCATION_EXPANSION 6/$220.13 (0 conv) · GET_DIRECTIONS 3/$139.73 (0 conv).
**Hours:** 06:00 and 07:00 remain the worst CPC ($111.82 and $181.79) and hold all 3
conversions.

**Data-settling note:** an earlier read showed HVAC Replacement at 393 impressions / 0 clicks.
Google has since restated that window to **46 impressions / 2 clicks / 4.35% CTR**. The earlier
"zero-click" characterisation was based on unsettled data and is withdrawn.

**Budget position:** MTD $1,947.95 · remaining $11,052.05 · 11 days including today · required
$1,004.73/day to reach the maximum · current total daily budget $427.64.
**No attempt is made to reach $13,000.**

## 12. Campaign-by-campaign assessment

- **HVAC Installation — increase.** Only budget-constrained campaign; loss worsening
  (51.72% → 63.82%) while rank-loss fell to 0.00%; best CPC in the account ($18.42 yesterday);
  consumed 200% of budget at the 2× ceiling. Stage 1 recommended.
- **AC Repair — hold.** Rank-limited (63.76%), QS 4, BELOW_AVERAGE expected CTR, CPC $68.05.
  Budget is not the constraint. Improve relevance and landing-page experience first.
- **HVAC Repair — hold budget, fix quality.** QS 2, BELOW_AVERAGE expected CTR *and*
  BELOW_AVERAGE landing-page experience, CTR 1.45%, CPC $76.46. New RSAs created; swap gated on
  policy; landing-page package ready.
- **HVAC Replacement — hold.** QS 2, BELOW_AVERAGE landing-page experience, rank-lost 68.42%.
  Has demand (4.35% CTR, CPC $26.07) but a weak funnel. Keyword expansion deferred until
  landing-page experience improves.
- **Gas Boiler Repair — keyword problem, not budget.** Zero impressions, rank-lost 90.01%,
  budget never touched. `boiler repair` (30/mo, LOW) is the only researched term above the
  10-search floor.

## 13. Keyword audit

All 12 non-removed keywords, five campaigns. Phrase and Exact only; **no Broad Match anywhere**.

| Campaign | Keyword | Match | QS | Exp CTR | Ad rel | LP exp | Impr | Clicks | Cost | Conv | Rank-lost | Verdict |
|---|---|---|---:|---|---|---|---:|---:|---:|---:|---:|---|
| AC Repair | ac repair near me | PHRASE | 4 | Below avg | Average | Average | 99 | 8 | $495.37 | 1.0 | 60.0% | **KEEP** |
| AC Repair | ac repair near me | EXACT | 4 | Below avg | Average | Average | 47 | 1 | $117.08 | 0 | 65.6% | **KEEP** |
| AC Repair | hvac replacement near me | PHRASE/EXACT | — | — | — | — | 0 | 0 | $0 | 0 | — | **LEAVE** (ad group REMOVED, cannot serve) |
| HVAC Repair | hvac repair near me | PHRASE | **2** | Below avg | Average | **Below avg** | 329 | 6 | $458.78 | 2.0 | 69.3% | **WATCH** — fix ad + LP |
| HVAC Repair | hvac repair near me | EXACT | **2** | Below avg | Average | **Below avg** | 84 | 0 | $0 | 0 | 70.4% | **WATCH** |
| HVAC Installation | hvac installers | PHRASE | — | — | — | — | 756 | 28 | $824.58 | 0 | 6.9% | **KEEP** — best performer |
| HVAC Installation | hvac installers | EXACT | — | — | — | — | 0 | 0 | $0 | 0 | — | **KEEP** |
| HVAC Replacement | hvac replacement near me | PHRASE | **2** | Below avg | Average | **Below avg** | 46 | 2 | $52.14 | 0 | 71.4% | **WATCH** |
| HVAC Replacement | hvac replacement near me | EXACT | **2** | Below avg | Average | **Below avg** | 0 | 0 | $0 | 0 | 60.0% | **WATCH** |
| Gas Boiler Repair | gas boiler repair | PHRASE | — | — | — | — | 0 | 0 | $0 | 0 | 90.0% | **RESTRUCTURE** — add `boiler repair` |
| Gas Boiler Repair | gas boiler repair | EXACT | — | — | — | — | 0 | 0 | $0 | 0 | — | **KEEP** |

All are ENABLED, ELIGIBLE and APPROVED. **ADD** is recommended only for Gas Boiler Repair.
HVAC Replacement expansion (`hvac replacement`, `hvac replacement cost`) is **deferred**: with
QS 2 and BELOW_AVERAGE landing-page experience, adding volume would spend into a weak funnel.

## 14. Search-term audit

1,236 rows scanned across since-launch, 30, 90 and 365-day windows. Raw terms were classified
**on disk**; only counts and cost shares were read back.
Export: `exports/search-terms-master-2026-08-21.jsonl`.

| Bucket | Distinct terms | Billable clicks | Cost |
|---|---:|---:|---:|
| IN_SCOPE_SERVICE | 178 | 15 | $1,070.00 |
| IN_SCOPE_EQUIPMENT_ONLY | 91 | 10 | $306.60 |
| OUT_OF_SCOPE | 38 | 4 | $93.61 |
| OUT_OF_SCOPE_RESEARCH_OR_JOBS | 2 | 1 | $17.24 |

Out-of-scope categorisation: **PARTS_OR_PRODUCT** 1 term / $17.24 is the only clearly
irrelevant spend. The remaining 4 paid out-of-scope terms / $93.61 fell into
UNCLASSIFIED_LOW_SIGNAL — no vehicle-AC, appliance, commercial, DIY, jobs, other-trade,
out-of-area or competitor pattern was detected. That is a whitelist limitation, not proven
waste.

## 15. Negative-list audit

- Account-level set `11252984411` (`ACCOUNT_LEVEL_NEGATIVE_KEYWORDS`): **59 BROAD members**,
  applies account-wide, invisible in `campaign_shared_set`. Tested against all five active
  keywords: **zero conflicts**.
- Campaign-level negatives on the five: **0**. Ad-group negatives: **0**. Negative lists
  attached to the five: **NONE**.
- 16 shared sets exist; 15 are attached only to legacy campaigns.

**Verdict: no meaningful negative package is warranted.** Clearly irrelevant spend is $17.24
across a week. Adding negatives on four unclassified terms with no shared pattern would be
activity without benefit and would risk blocking legitimate intent. Protected intent (near me,
quote, price, pricing, cost, best, hire, local, emergency) remains un-negated everywhere.

The **only** negatives recommended are 10 ad-group-scoped Phrase negatives bundled with the Gas
Boiler keyword addition, which exist solely to bound the new broader keyword.

## 16. Ads and assets audit

- Every intended active ad group has **exactly 2 enabled RSAs**. Non-removed ads 113 → 115.
- Six preserved replacement RSAs (`821319509197/200/203/206/209/212`) all **ENABLED +
  APPROVED** — verified, not replayed.
- Six original CONSUMER_FINANCE ads remain **PAUSED + DISAPPROVED** — verified, not touched.
- Orphaned REMOVED ad group `202339087874` inside AC Repair still holds 2 keywords and 2
  `AREA_OF_INTEREST_ONLY` ads. **Documented and left unchanged** — it cannot serve.
- Call asset `407995613637`: (410)705-6354, 6 schedule rows (Mon–Fri 08:00–20:00, Sat
  08:00–13:00, no Sunday), APPROVED, linked to exactly the five.
- Sitelinks: 4 offer-subdomain service links + 4 retained main-site informational links
  (Contact, Reviews, Service Areas, Our Work) on every campaign — preserved.
- Callouts: account-level reduced to `Get Free Online Quote` only; five campaign-level callouts
  intact. **`Licensed & Insured` and `Claim Your Discount` remain removed** and were not
  restored.
- Structured snippets: 5, one per campaign, correctly themed.
- Location assets: from customer-level `LOCATION_SYNC` asset set `8620443109` ("Business
  Profile"). Produced 6 LOCATION_EXPANSION + 3 GET_DIRECTIONS billable clicks, $359.86, 0
  primary conversions. Too small a sample to cut — **watch**.

## 17. Campaign-settings audit

All five verified: **Search only** · Display **off** · Search Partners **off** · Presence
positive and negative geo targeting · 1 language · 3 device criteria · 75 locations · **6
ad-schedule rows each, no duplicates or overlaps** · budgets unshared with `reference_count 1`,
STANDARD delivery, DAILY period · **TARGET_SPEND** with `cpc_bid_ceiling_micros = 0` · no
portfolio strategy · no campaign-level tracking template or URL suffix (account-level ClickCease
template applies) · auto-tagging **on**.

Nothing already correct was changed.

## 18. Budget and bidding decision

**Bidding: unchanged.** Maximize Clicks retained. Only 3 recorded conversions exist and two
were the now-corrected double count — nowhere near enough for Maximize Conversions or Target
CPA. **No CPC ceiling proposed**: no target CPL, target CPQL, close rate, job value or margin
exists in the client record, and none will be invented.

**One budget change recommended — HVAC Installation only:** $138.16 → **$207.24/day (1.5×)**.

Sized below proven consumption ($276.25 yesterday), so it is certain to be used, and it lifts
the daily ceiling from $276.32 to $414.48 without doubling.

**Exposure proof:** new total daily $496.72. Even at Google's maximum 2× overdelivery on every
one of the 11 remaining days, August totals **$12,875.79** — still under $13,000, with $124.21
of headroom. The increase is safe by construction.

## 19. Remaining approval packages

| Package | Fingerprint | Ops | Validate |
|---|---|---|---|
| HVAC Repair RSA swap | `D441DEFC58EB5643` | 4 updates | VALIDATE_OK |
| Budget Stage 1 — HVAC Installation | `5DA7527B19276C0D` | 1 update | VALIDATE_OK |
| Gas Boiler keyword expansion | `E6D25322E35F3E62` | 12 creates | VALIDATE_OK |
| Landing-page production deployment | `93A9DF4AA19675E8` | 0 Google Ads | n/a (15-test suite) |

## 20. Rollback plans

- **Plan B:** set `primary_for_goal = true` on the four demoted IDs. 4 mutations.
- **RSA creation:** remove `821714108336` and `821714108339`. 2 mutations.
- **RSA swap:** re-enable the two prior ads, re-pause the two new. 4 mutations, atomic.
- **Budget:** restore `15787409441` to 138160000 micros. 1 mutation.
- **Keywords:** remove the 12 created criteria. 12 mutations.
- **Landing page:** GTM version revert (<5 min), theme/form restore (<30 min), database restore
  (<2 h, last resort).

## 21. Final account inventory

campaigns 23 · ad groups 68 · **ads 115** (113 + 2 created) · keywords 6,968 · campaign criteria
13,810 · ad schedules 139 · campaign assets 283 · customer assets 1 · conversion actions 16 ·
IP exclusions **2,796 (untouched)** · shared sets 16 · **primary + counted conversion actions:
exactly 3** (`1068114183`, `6885463625`, `6885576934`) · budgets unchanged at
141450000 / 42760000 / 138160000 / 78950000 / 26320000 micros.

## 22. Manager-link verification

`3373711342` Green Marketing **ACTIVE** · `2815082755` ClickCease Client Center **ACTIVE**.
Verified before and after every mutation.

## 23. ClickCease untouched

Manager link ACTIVE and unmodified. **2,796 IP exclusions unchanged** — none added, removed or
edited. Account tracking template still `monitor.clickcease.com` with id `Y6qzID4E9cPYCj`,
`ccpturl=offer.ambientcoolingandheating.com`, all ValueTrack parameters, auto-tagging on. No
ClickCease console work performed. Read-only verification only.

## 24. Missing business economics

No target CPL, target CPQL, target CAC, average job revenue, gross margin or close rate exists
in `client.yaml`. Consequently **no CPC ceiling, no ROAS target and no profitability verdict
can be produced**, and none was invented. Qualified-lead and sold-job outcomes are unavailable:
the only lead-quality signal obtainable from Google Ads is the 171-second answered call.
Supplying a target CPL or acceptable CPA unlocks a defensible max-CPC calculation from the
historical Search conversion rate.

## 25. Recommended monitoring schedule

| When | What |
|---|---|
| **2026-08-21, 11:35 ET** | Full post-schedule pacing checkpoint (script saved) |
| **2026-08-21, hourly until clear** | Poll `821714108336` / `821714108339` policy status |
| **24 h after budget approval** | HVAC Installation: billable clicks, CPC vs $29.45, budget-lost IS, conversions |
| **2026-08-24** | Full re-pace; confirm August tracking under $13,000 |
| **7 settled days after RSA swap** | HVAC Repair CTR vs the 1.45% baseline; roll back if lower |
| **2026-08-28** | Guardrail check: cumulative five-campaign spend vs $11,000 |
| **2026-09-01** | Re-read Quality Score on all keywords; re-evaluate HVAC Replacement expansion |
| **Ongoing** | Conversion reporting after propagation; confirm one conversion per lead event |

---

## Receipts saved

`snapshots/`: master-baseline-2026-08-21 · master-analysis-2026-08-21 · final-inventory-2026-08-21
`receipts/`: planB-mutation / planB-readback · rsa-create-mutation / rsa-create-readback ·
fingerprint-manifest-2026-08-21 (39 plans, 32 live, 7 void)
`exports/`: search-terms-master-2026-08-21.jsonl
`plans/`: HVAC-REPAIR-RSA-SWAP · BUDGET-STAGE1-HVAC-INSTALLATION · KEYWORD-GAS-BOILER-EXPANSION
· LANDING-PAGE-PRODUCTION-DEPLOYMENT (all 2026-08-21)

No OAuth credentials, developer tokens, refresh tokens, API keys, webhook secrets or lead PII
appear in any artifact.
