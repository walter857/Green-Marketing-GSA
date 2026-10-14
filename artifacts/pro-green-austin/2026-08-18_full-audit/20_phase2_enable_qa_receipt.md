# 20 — Phase 2 ENABLE QA Receipt

**Account:** Pro Green - Austin - Live
**Customer ID:** `7380491929`
**Service:** outdoor design & build
**Executed:** 2026-08-20 14:28:33 UTC (10:28 America/New_York, the account timezone)
**Master fingerprint:** `04D12B022A12`
**Subplan fingerprint:** `CB8CFD00961A`
**Approved scope:** exactly 24 actions / 24 objects

**Result: all 24 responsive search ads moved PAUSED → ENABLED in one atomic mutate. 29 of 29
preflight gates and 25 of 25 readback assertions passed. No partial subset. No ad was edited.
Nothing outside the approved scope changed.**

---

## 1. Pre-execution gates — 29 of 29 passed

| Gate | Result |
|---|---|
| ENABLE fingerprint recomputed from the frozen on-disk plan | `CB8CFD00961A` — **matches** |
| Master fingerprint recomputed from the frozen on-disk plan | `04D12B022A12` — **matches** |
| Scope | exactly **24 actions / 24 objects**; no other subplan carries an action |
| Every action changes only `status`, and only to ENABLED | **confirmed** |
| Provenance | CREATE_PAUSED receipt fingerprint `13B70F010DDF`; ENABLE targets **exactly** those 24 ads |
| Identity | `Pro Green - Austin - Live` / `7380491929` / **not a manager** / **not a test account** |
| Service scope | still `outdoor design & build` per work order and client profile |

### Inventory before the write

| Requirement | Observed |
|---|---|
| Total RSAs on live campaigns | **48** |
| Original ENABLED RSAs | **24** |
| New PAUSED RSAs | **24** |
| RSAs per live ad group | **exactly 2** |
| Already enabled by another user or process | **none** |
| Target ads edited, removed or duplicated | **none** |

### Drift checks

| Check | Result |
|---|---|
| All 24 original RSAs byte-identical to the before snapshot | **PASS** |
| All 24 paused RSAs byte-identical to the approved Phase 2 plan — headlines, descriptions, final URL, paths, ad-group association, pinning | **PASS** |
| Live copy also matches `16_rsa_rebuild_plan.csv` | **PASS** |

### Landing-page mapping confirmed unchanged

| Check | Observed |
|---|---|
| Unique destinations | **13** |
| Maximum reuse of any destination | **2 ad groups** |
| Theme pairs sharing one offer page | **11 of 12**, each only with its own BOFU + Near Me pair |
| Approved main-site exception | exactly one — `Hardscaping \| Near Me` |

---

## 2. Google policy-review gate — PASSED

Re-read immediately before validation:

| Field | Result |
|---|---|
| `approval_status` | **APPROVED × 24** |
| `review_status` | **REVIEWED × 24** |
| Disapprovals | **0** |
| Limited-policy conditions | **0** |
| Blocking policy topics | **0** |

Google's review completed between the create-paused readback on 2026-08-20 06:32 UTC — where all
24 were `REVIEW_IN_PROGRESS` / `UNKNOWN` — and this run at 14:28 UTC. **All 24 were fully cleared,
so the gate opened and execution proceeded.**

---

## 3. Validate-only

`GoogleAdsService.mutate`, `validate_only = true`, `partial_failure = false`, 24 operations:
**VALIDATION PASSED, nothing written.** Independently re-confirmed immediately afterwards at
**24 ENABLED / 24 PAUSED**, proving the dry run made no change. Only then was the live write sent.

---

## 4. Atomic mutation

| | |
|---|---|
| Method | one atomic `GoogleAdsService.mutate` |
| `partial_failure` | **false** — all or nothing |
| Operations | 24 |
| Responses | 24 |
| Field written | `status` only, `PAUSED` → `ENABLED` |
| Retries | **none**; no ambiguous or failed request occurred |
| Partial success | **none** |
| Receipt | `clients/pro-green-austin/receipts/exec-enable-2026-08-20.json` |

---

## 5. Before and after

| Metric | Before | After |
|---|---|---|
| Live ad groups | 24 | 24 |
| ENABLED RSAs | 24 | **48** |
| PAUSED RSAs | 24 | **0** |
| Total RSAs | 48 | 48 |
| ENABLED RSAs per live ad group | 1 | **2** |

---

## 6. The 24 enabled ads — resource IDs, mapping, status and policy

| # | Campaign | Ad group | Ad ID | Resource name | Status | Final URL | Paths | Policy |
|---|---|---|---|---|---|---|---|---|
| 1 | Hardscape | Driveways \| BOFU | `821598464387` | `199051686216~821598464387` | PAUSED -> **ENABLED** | `[LP]`/paver-driveway/ | `/driveways/free-quote` | APPROVED |
| 2 | Hardscape | Driveways \| Near Me | `821598464390` | `199051686176~821598464390` | PAUSED -> **ENABLED** | `[LP]`/paver-driveway/ | `/driveways/austin` | APPROVED |
| 3 | Hardscape | Hardscaping \| BOFU | `821598464393` | `199051685456~821598464393` | PAUSED -> **ENABLED** | `[LP]`/hardscaping/ | `/hardscaping/free-quote` | APPROVED |
| 4 | Hardscape | Hardscaping \| Near Me | `821598464396` | `199051685416~821598464396` | PAUSED -> **ENABLED** | **`[MAIN]`**/austin/services/hardscaping/ | `/hardscaping/austin` | APPROVED |
| 5 | Hardscape | Patios \| BOFU | `821598464399` | `199051685936~821598464399` | PAUSED -> **ENABLED** | `[LP]`/patio-2/ | `/patios/free-quote` | APPROVED |
| 6 | Hardscape | Patios \| Near Me | `821598464522` | `199051685896~821598464522` | PAUSED -> **ENABLED** | `[LP]`/patio-2/ | `/patios/austin` | APPROVED |
| 7 | Hardscape | Pavers \| BOFU | `821598464525` | `199051685736~821598464525` | PAUSED -> **ENABLED** | `[LP]`/pavers-2/ | `/pavers/free-quote` | APPROVED |
| 8 | Hardscape | Pavers \| Near Me | `821598464528` | `199051685696~821598464528` | PAUSED -> **ENABLED** | `[LP]`/pavers-2/ | `/pavers/austin` | APPROVED |
| 9 | Hardscape | Retaining Walls \| BOFU | `821598464531` | `199051685656~821598464531` | PAUSED -> **ENABLED** | `[LP]`/retaining-walls/ | `/retaining-wall/free-quote` | APPROVED |
| 10 | Hardscape | Retaining Walls \| Near Me | `821598464534` | `199051685496~821598464534` | PAUSED -> **ENABLED** | `[LP]`/retaining-walls/ | `/retaining-wall/austin` | APPROVED |
| 11 | Hardscape | Walkways \| BOFU | `821598464537` | `199051686136~821598464537` | PAUSED -> **ENABLED** | `[LP]`/walkway/ | `/walkways/free-quote` | APPROVED |
| 12 | Hardscape | Walkways \| Near Me | `821598464540` | `199051685976~821598464540` | PAUSED -> **ENABLED** | `[LP]`/walkway/ | `/walkways/austin` | APPROVED |
| 13 | Outdoor Living | Artificial Turf \| BOFU | `821598464543` | `199051687096~821598464543` | PAUSED -> **ENABLED** | `[LP]`/artificial-turf/ | `/artificial-turf/free-quote` | APPROVED |
| 14 | Outdoor Living | Artificial Turf \| Near Me | `821598464546` | `199051686936~821598464546` | PAUSED -> **ENABLED** | `[LP]`/artificial-turf/ | `/artificial-turf/austin` | APPROVED |
| 15 | Outdoor Living | Fire Pits \| BOFU | `821598464549` | `199051686696~821598464549` | PAUSED -> **ENABLED** | `[LP]`/fire-pit/ | `/fire-pits/free-quote` | APPROVED |
| 16 | Outdoor Living | Fire Pits \| Near Me | `821598464552` | `199051686656~821598464552` | PAUSED -> **ENABLED** | `[LP]`/fire-pit/ | `/fire-pits/austin` | APPROVED |
| 17 | Outdoor Living | Landscape Design \| BOFU | `821598464555` | `199051686416~821598464555` | PAUSED -> **ENABLED** | `[LP]`/landscape-design/ | `/landscape/design-quote` | APPROVED |
| 18 | Outdoor Living | Landscape Design \| Near Me | `821598464558` | `199051686376~821598464558` | PAUSED -> **ENABLED** | `[LP]`/landscape-design/ | `/landscape/austin` | APPROVED |
| 19 | Outdoor Living | Landscape Lighting \| BOFU | `821598464561` | `199051687176~821598464561` | PAUSED -> **ENABLED** | `[LP]`/landscape-lighting/ | `/lighting/free-quote` | APPROVED |
| 20 | Outdoor Living | Landscape Lighting \| Near Me | `821598464564` | `199051687136~821598464564` | PAUSED -> **ENABLED** | `[LP]`/landscape-lighting/ | `/lighting/austin` | APPROVED |
| 21 | Outdoor Living | Outdoor Living \| BOFU | `821598464567` | `199051686616~821598464567` | PAUSED -> **ENABLED** | `[LP]`/outdoor-living/ | `/outdoor-living/free-quote` | APPROVED |
| 22 | Outdoor Living | Outdoor Living \| Near Me | `821598464570` | `199051686456~821598464570` | PAUSED -> **ENABLED** | `[LP]`/outdoor-living/ | `/outdoor-living/austin` | APPROVED |
| 23 | Outdoor Living | Pergolas \| BOFU | `821598464573` | `199051686896~821598464573` | PAUSED -> **ENABLED** | `[LP]`/pergola/ | `/pergolas/free-quote` | APPROVED |
| 24 | Outdoor Living | Pergolas \| Near Me | `821598464576` | `199051686856~821598464576` | PAUSED -> **ENABLED** | `[LP]`/pergola/ | `/pergolas/austin` | APPROVED |

`[LP]` = `https://offeraustin.progreenlandscapesolutions.com`
`[MAIN]` = `https://progreenlandscapesolutions.com`
Full resource-name prefix: `customers/7380491929/adGroupAds/`

---

## 7. Readback assertions — 25 of 25 passed

| Assertion | Result |
|---|---|
| Exactly 24 status updates returned | **PASS** |
| Returned resource names match the approved targets exactly | **PASS** |
| All 24 target ads readable from the API | **PASS** |
| All 24 new RSAs now read **ENABLED** | **PASS** |
| All 24 original RSAs remain **ENABLED** | **PASS** |
| **48 ENABLED RSAs** total | **PASS** |
| **Zero PAUSED Phase 2 RSAs** remain | **PASS** |
| Exactly two ENABLED RSAs per live ad group | **PASS** |
| Every enabled ad still matches the approved campaign | **PASS** |
| …ad group | **PASS** |
| …final URL | **PASS** |
| …`path1` / `path2` | **PASS** |
| …15 headlines, byte-for-byte | **PASS** |
| …4 descriptions, byte-for-byte | **PASS** |
| …pinning state (none) | **PASS** |
| No original ad edited | **PASS** |
| No ad became disapproved or limited during the mutation | **PASS** |

**Post-mutation policy state:** `APPROVED × 24`, `REVIEWED × 24`, zero policy topics.
`ad_strength` reads `PENDING` on all 24 — expected, because Ad Strength repopulates only after an
enabled ad begins serving. It is a diagnostic, not a business KPI.

---

## 8. Unrelated resources — confirmed unchanged

| Resource | Verified |
|---|---|
| Keywords | **48** |
| Campaign negative keywords | **88** |
| Ad-schedule criteria | **14**, all 09:00–18:00 account time |
| Locations | **24 per campaign**, zero exclusions |
| Budgets | **$39.47** and **$26.31** |
| Combined daily budget | **$65.78** |
| CPC ceilings | **$22.00** on both |
| Bidding strategy | TARGET_SPEND on both, unchanged |
| Parent asset exclusions | `[SITELINK, STRUCTURED_SNIPPET]` intact |
| Primary conversion actions | exactly **3** — `6566620547`, `6885610317`, `7644242327` |
| Sitelinks | **12** |
| Callouts | **16** |
| Structured snippets | **2** |
| Call assets | **2** |
| Business logos | **2** |
| `customer.tracking_url_template` | **not written** |
| ClickCease | not touched |
| Website, GTM, GA4, landing-page forms, consent configuration | not touched |
| Google recommendations | **none applied**; no auto-apply subscription exists |
| BLK-001 / BLK-002 | not actioned |
| SPEC-001 / SPEC-002 / SPEC-005 | not executed |

---

## 9. Failures and remaining gates

**Failures: none. Drift: none. Partial success: none. No recovery plan required.**

| Item | Status |
|---|---|
| Phase 1 remediation | **COMPLETE** (executed 2026-08-19) |
| Phase 2 CREATE_PAUSED | **COMPLETE** (executed 2026-08-20 06:32 UTC) |
| Phase 2 ENABLE | **COMPLETE** (executed 2026-08-20 14:28 UTC) |
| SPEC-001 | **OPEN** — add GCLID, GBRAID, WBRAID, UTMs and unique lead IDs to the offer-page forms |
| SPEC-002 | **OPEN** — verify and repair the offer-page form conversion tag; needs its own approval for one test submission |
| SPEC-005 | **OPEN** — correct "Confirm the Landscape Plan" on the Pergola and Artificial Turf pages |
| BLK-001 | **BLOCKED** — resolve the ClickCease destination configuration inside ClickCease |
| BLK-002 | **BLOCKED** — sitelink repointing stays blocked until offer-page attribution is repaired |

**No further optimization was performed and none will be made automatically.**

---

## 10. How to read this test, honestly

Both creatives now serve in every ad group: the original **feature and process led** ad against the
new **outcome led** ad.

**CTR is readable.** That is the metric this test was built for — expected CTR was BELOW_AVERAGE on
every scored keyword while ad relevance was AVERAGE or ABOVE_AVERAGE, so the hook was the weak
point, not the relevance. CTR does not depend on the landing-page form.

**Conversion comparisons remain limited** until the outstanding items are resolved:

- **SPEC-001** — the offer-page form still captures no click identifier, so form leads on 23 of the
  24 destinations cannot be tied back to an ad.
- **SPEC-002** — the offer-page form-submit conversion tag is still unverified and recorded zero in
  the live window while WhatConverts recorded two.
- **SPEC-005** — wrong three-step copy on two live offer pages.
- **BLK-001** — the ClickCease `ccpturl` still names a domain that is not the landing-page host, and
  the value oscillates.
- **BLK-002** — sitelinks still point at main-site pages, which are currently the better-attributed
  destinations.

Judge these two creatives on **CTR and Quality Score** for now. Do not draw conclusions from
conversion counts per ad until SPEC-001 and SPEC-002 land.
