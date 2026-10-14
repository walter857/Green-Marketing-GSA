# 18 — Phase 2 CREATE_PAUSED QA Receipt

**Account:** Pro Green - Austin - Live
**Customer ID:** `7380491929`
**Service:** outdoor design & build
**Executed:** 2026-08-20 06:32:31 UTC (02:32 America/New_York, the account timezone)
**Approved subplan:** CREATE_PAUSED
**Approved fingerprint:** `13B70F010DDF`
**Phase 2 master:** `93B8761DF260`
**Approved scope:** exactly 24 actions / 24 objects

**Result: all 24 responsive search ads created PAUSED. 25 of 25 readback assertions passed. No
partial failure. Nothing outside the approved scope changed. No ad was enabled.**

---

## 1. Pre-execution verification

| Gate | Result |
|---|---|
| CREATE_PAUSED fingerprint recomputed from the frozen on-disk plan | `13B70F010DDF` — **matches** |
| Master fingerprint recomputed from the frozen on-disk plan | `93B8761DF260` — **matches** |
| Scope | exactly **24 actions / 24 objects**; no other subplan carries an action |
| `16_rsa_rebuild_plan.csv` agrees with `17_phase2_change_plan.yaml` | **every value** — URL, paths, all 15 headlines and all 4 descriptions per ad |
| Copy compliance re-checked from the frozen plan | 15H/4D each, within limits, no in-ad duplicates, no pinning, **no banned claims** |
| Identity | `Pro Green - Austin - Live` / `7380491929` / **not a manager** / **not a test account** / ENABLED |
| Service scope | still `outdoor design & build`, vertical `hardscaping`, per work order and client profile |
| **Preflight total** | **38 checks, 38 passed, 0 failed** |

### Phase 1 confirmed still in place

| Item | Observed |
|---|---|
| ENABLED campaigns | 2 |
| Budgets | $39.47 + $26.31 = **$65.78/day** |
| CPC ceilings | **$22.00** on both; bidding still TARGET_SPEND |
| Parent asset exclusions | `[SITELINK, STRUCTURED_SNIPPET]` on both |
| Ad schedule | 7 criteria per campaign, all **09:00–18:00** account time |
| Primary conversion actions | exactly 3 — `6566620547`, `6885610317`, `7644242327` |

### Structure confirmed before the write

| Requirement | Observed |
|---|---|
| Live ad groups | **24** (12 themes × BOFU + Near Me) |
| Existing ENABLED RSAs | **24** |
| Existing PAUSED ads on live campaigns | **0** |
| RSAs per live ad group | **exactly 1** |
| Planned ads already existing, exact or normalized | **0** — no duplicate found, so nothing was skipped |
| Planned final URL equals the approved URL for its ad group | **24 of 24** |
| Unique destinations | **13** |
| Max reuse of any single page | **2** — no page is used by every ad |
| Main-site exception | exactly one, `Hardscaping \| Near Me`, as approved |

### Server-side validation

`GoogleAdsService.mutate` with `validate_only = true`, `partial_failure = false`, all 24 operations:
**VALIDATION PASSED, nothing written.** Only then was the live write sent.

---

## 2. Execution

| | |
|---|---|
| Method | one atomic `GoogleAdsService.mutate` |
| `partial_failure` | **false** — all or nothing |
| Operations | 24 |
| Responses | 24 |
| Retries | **none**; no ambiguous or failed mutation occurred |
| Receipt | `clients/pro-green-austin/receipts/exec-createpaused-2026-08-20.json` |

---

## 3. Before and after

| Metric | Before | After |
|---|---|---|
| Live ad groups | 24 | 24 |
| ENABLED RSAs | 24 | **24** |
| PAUSED RSAs | 0 | **24** |
| Total RSAs on live campaigns | 24 | **48** |
| RSAs per live ad group | 1 | **2** |

---

## 4. All 24 new ads — resource IDs, campaign, ad group and URL mapping

| # | Campaign | Ad group | New ad ID | Resource name | Paired existing ad | Final URL | Paths |
|---|---|---|---|---|---|---|---|
| 1 | Hardscape | Driveways \| BOFU | `821598464387` | `199051686216~821598464387` | `817941409336` | `[LP]`/paver-driveway/ | `/driveways/free-quote` |
| 2 | Hardscape | Driveways \| Near Me | `821598464390` | `199051686176~821598464390` | `817941409333` | `[LP]`/paver-driveway/ | `/driveways/austin` |
| 3 | Hardscape | Hardscaping \| BOFU | `821598464393` | `199051685456~821598464393` | `817941409186` | `[LP]`/hardscaping/ | `/hardscaping/free-quote` |
| 4 | Hardscape | Hardscaping \| Near Me | `821598464396` | `199051685416~821598464396` | `817941409183` | **`[MAIN]`/austin/services/hardscaping/** | `/hardscaping/austin` |
| 5 | Hardscape | Patios \| BOFU | `821598464399` | `199051685936~821598464399` | `817941409324` | `[LP]`/patio-2/ | `/patios/free-quote` |
| 6 | Hardscape | Patios \| Near Me | `821598464522` | `199051685896~821598464522` | `817941409321` | `[LP]`/patio-2/ | `/patios/austin` |
| 7 | Hardscape | Pavers \| BOFU | `821598464525` | `199051685736~821598464525` | `817941409198` | `[LP]`/pavers-2/ | `/pavers/free-quote` |
| 8 | Hardscape | Pavers \| Near Me | `821598464528` | `199051685696~821598464528` | `817941409195` | `[LP]`/pavers-2/ | `/pavers/austin` |
| 9 | Hardscape | Retaining Walls \| BOFU | `821598464531` | `199051685656~821598464531` | `817941409192` | `[LP]`/retaining-walls/ | `/retaining-wall/free-quote` |
| 10 | Hardscape | Retaining Walls \| Near Me | `821598464534` | `199051685496~821598464534` | `817941409189` | `[LP]`/retaining-walls/ | `/retaining-wall/austin` |
| 11 | Hardscape | Walkways \| BOFU | `821598464537` | `199051686136~821598464537` | `817941409330` | `[LP]`/walkway/ | `/walkways/free-quote` |
| 12 | Hardscape | Walkways \| Near Me | `821598464540` | `199051685976~821598464540` | `817941409327` | `[LP]`/walkway/ | `/walkways/austin` |
| 13 | Outdoor Living | Artificial Turf \| BOFU | `821598464543` | `199051687096~821598464543` | `817941409366` | `[LP]`/artificial-turf/ | `/artificial-turf/free-quote` |
| 14 | Outdoor Living | Artificial Turf \| Near Me | `821598464546` | `199051686936~821598464546` | `817941409363` | `[LP]`/artificial-turf/ | `/artificial-turf/austin` |
| 15 | Outdoor Living | Fire Pits \| BOFU | `821598464549` | `199051686696~821598464549` | `817941409354` | `[LP]`/fire-pit/ | `/fire-pits/free-quote` |
| 16 | Outdoor Living | Fire Pits \| Near Me | `821598464552` | `199051686656~821598464552` | `817941409351` | `[LP]`/fire-pit/ | `/fire-pits/austin` |
| 17 | Outdoor Living | Landscape Design \| BOFU | `821598464555` | `199051686416~821598464555` | `817941409342` | `[LP]`/landscape-design/ | `/landscape/design-quote` |
| 18 | Outdoor Living | Landscape Design \| Near Me | `821598464558` | `199051686376~821598464558` | `817941409339` | `[LP]`/landscape-design/ | `/landscape/austin` |
| 19 | Outdoor Living | Landscape Lighting \| BOFU | `821598464561` | `199051687176~821598464561` | `817941409372` | `[LP]`/landscape-lighting/ | `/lighting/free-quote` |
| 20 | Outdoor Living | Landscape Lighting \| Near Me | `821598464564` | `199051687136~821598464564` | `817941409369` | `[LP]`/landscape-lighting/ | `/lighting/austin` |
| 21 | Outdoor Living | Outdoor Living \| BOFU | `821598464567` | `199051686616~821598464567` | `817941409348` | `[LP]`/outdoor-living/ | `/outdoor-living/free-quote` |
| 22 | Outdoor Living | Outdoor Living \| Near Me | `821598464570` | `199051686456~821598464570` | `817941409345` | `[LP]`/outdoor-living/ | `/outdoor-living/austin` |
| 23 | Outdoor Living | Pergolas \| BOFU | `821598464573` | `199051686896~821598464573` | `817941409360` | `[LP]`/pergola/ | `/pergolas/free-quote` |
| 24 | Outdoor Living | Pergolas \| Near Me | `821598464576` | `199051686856~821598464576` | `817941409357` | `[LP]`/pergola/ | `/pergolas/austin` |

`[LP]` = `https://offeraustin.progreenlandscapesolutions.com`
`[MAIN]` = `https://progreenlandscapesolutions.com`
Full resource name prefix: `customers/7380491929/adGroupAds/`

**Landing-page mapping is unchanged from the approved plan.** Twelve theme-specific offer pages,
each shared by its own theme's BOFU and Near Me pair, plus the one approved main-site exception on
`Hardscaping | Near Me`. **13 unique destinations. No unrelated themes share a page. No generic page
is used for every ad.**

---

## 5. Readback assertions — 25 of 25 passed

| Assertion | Result |
|---|---|
| Exactly 24 ads created, no more and no fewer | **PASS** |
| All 24 readable directly from the Google Ads API | **PASS** |
| Every new ad is **PAUSED** | **PASS** — 24 PAUSED |
| Every existing RSA still **ENABLED** | **PASS** — 24 ENABLED |
| 48 total RSAs, exactly two per live ad group | **PASS** |
| No ad created outside the approved 24 | **PASS** |
| One new ad in each of the 24 approved ad groups | **PASS** |
| Correct campaign and ad group for every new ad | **PASS** |
| Exact final URL per the frozen plan | **PASS** |
| Exact `path1` / `path2` per the frozen plan | **PASS** |
| Exactly 15 headlines, byte-for-byte per the frozen plan | **PASS** |
| Exactly 4 descriptions, byte-for-byte per the frozen plan | **PASS** |
| **No pinning** on any headline or description | **PASS** |
| No tracking template or final URL suffix on any new ad | **PASS** |
| Type is `RESPONSIVE_SEARCH_AD` | **PASS** |
| No existing ad changed in URL, headlines or descriptions | **PASS** |
| No new ad DISAPPROVED or limited | **PASS** |
| No new ad carries a policy topic | **PASS** |

---

## 6. Policy review state

**All 24 new ads: `approval_status = UNKNOWN`, `review_status = REVIEW_IN_PROGRESS`,
`ad_strength = PENDING`.** That is the normal state for a newly created ad.
**Zero policy topics, zero disapprovals, zero limited ads.**

**ENABLE remains blocked until Google's review finishes.** All 24 stay paused. Ad Strength will
populate once review completes; it is recorded as a diagnostic, not a business KPI.

---

## 7. Unrelated resources — confirmed unchanged

| Resource | Verified |
|---|---|
| `customer.tracking_url_template` | **not written by us** — identical to the preflight read |
| Existing 24 RSAs | unchanged in status, URL, headlines, descriptions |
| Positive keywords | still **48** |
| Campaign negative keywords | still **88** |
| Ad-schedule criteria | still **14**, all 09:00–18:00 |
| Locations | **24 per campaign**, zero exclusions |
| Budgets | $39.47 / $26.31, total **$65.78/day** |
| Bidding and CPC ceilings | TARGET_SPEND, **$22.00** on both |
| Parent asset exclusions | intact on both |
| Conversion actions | exactly **3** primary |
| Sitelinks / callouts / snippets / call / logo | **12 / 16 / 2 / 2 / 2** — all unchanged |
| BUSINESS_LOGO | unchanged, as instructed |
| ClickCease and the tracking template | not touched |
| Website, GTM, GA4, forms, consent | not touched |
| SPEC-001 / SPEC-002 / SPEC-005 | not executed |
| Google recommendations | none applied |
| BLK-002 sitelink repointing | not performed |

---

## 8. Failures, drift and remaining gates

**Failures: none. Drift: none. Partial success: none.**

| Gate | Status |
|---|---|
| **ENABLE the 24 new ads** | **BLOCKED** — needs the new ENABLE fingerprint **and** completion of Google's review |
| SPEC-001 | OPEN — add click IDs, UTMs and unique lead IDs to the offer-page forms |
| SPEC-002 | OPEN — verify and repair the landing-page form conversion tag; needs its own approval for one test submission |
| SPEC-005 | OPEN — correct the copied "Confirm the Landscape Plan" wording on the Pergola and Artificial Turf pages |
| BLK-001 | BLOCKED — resolve the ClickCease destination configuration inside ClickCease |
| BLK-002 | BLOCKED — sitelink repointing, until the offer-page attribution problem is fixed |

---

## 9. Next approval required

**ENABLE plan:** `artifacts/pro-green-austin/2026-08-18_full-audit/19_phase2_enable_plan.yaml`
Contains the exact 24 paused ad resource IDs. Server-side `validate_only` returned clean and **wrote
nothing** — re-verified afterwards at 24 ENABLED / 24 PAUSED.

```
MASTER 04D12B022A12
APPROVE ENABLE CB8CFD00961A FOR 7380491929      24 actions / 24 objects
```

**Execution is gated twice.** Green Marketing must paste back that exact fingerprint, **and**
Google's review of all 24 ads must have finished. A fresh preflight will re-read policy state and
will stop if any ad is disapproved, limited, or no longer matches the frozen copy.

**NO AD WAS ENABLED DURING THIS RUN.**
