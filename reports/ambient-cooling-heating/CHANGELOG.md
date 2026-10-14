# Ambient Cooling & Heating — changelog

## 2026-10-05 — Heating Repair optimization prep while the $18 test runs (READ + DRAFT, 0 writes)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity 8/8 · report `2026-10-05-repair-optimization-prep.md`
- Search terms: every paid irrelevant query is now excluded; Oct 1-2 visible spend 100% ambiguous local-HVAC. 4 negative drafts ($0 spend) for the Oct 8 package.
- `heating repair` Phrase + Exact kept; 10-01 Phrase-pause trigger not met ($81.79 since Oct 1, 0% irrelevant).
- $18 baseline + template written; Oct 2 budget cut ($31.76) throttles delivery, so judge per click / per lead.
- D6 FIXED; D5 IDs fixed but gform_3 (visible) / gform_4 are NOT in WhatConverts' form list; Oct 2 Geothermal confirmed submission has no WC lead.
- D7 poisoning resolved (hidden fields now empty for everyone); D1 still open (761-0932 ×3 in source).
- DRIFT: 6885463625 + 6885576934 switched Secondary → Primary after 10-02 08:47 (no recorded plan).
- Two Heating Repair location-asset calls (09-25, 09-30) have no WhatConverts record; Business Profile Ads phone still needs a UI read.

## 2026-10-02c — Cleanup and launch EXECUTED under the staged authorization (WRITE)

**Account:** `Ambient Cooling - Live` / `2401959466` · report `2026-10-02-cleanup-and-launch-execution.md`
- EXECUTED 08:21–08:45 ET, all readbacks clean:
  - EMER-ENABLE-1 BFBD1315E210
  - NEG-EXACT-2 **04E22EF928DD** (104 EXACT)
  - SEARCH-LAUNCH-1 **C903F9B1F413** (Maintenance 10 ads, Boiler Installation 2 RSAs + 3 kw, Commercial, Geothermal, No Heat kw, sitelinks/callouts)
  - PMAX-A-2 **405EDDC8E478** + PMAX-B-2 **157DF8F88A9A** (B = 24318905515; 5 asset groups live)
  - BUD-OCT-2 **A21B8F53ABDC** (8 Search)
- Staged, NOT executed: BUD-NOV-2 **150006548BA1** (10 × $32.89, refuses before 2026-11-01).
- Superseded, never run: NEG-EXACT-1, PMAX-A-1/B-1, BUD-OCT-1/NOV-1.
- Caught before writing:
  - PMax shell A had NO tablet exclusion (the TABLET row had no bid modifier).
  - List 12249470554 is PHRASE/BROAD, so it was not attached.
  - 3 PMax opt-outs are not permitted by the API.

## 2026-10-02b — Emergency + Geothermal CREATE executed; negatives, budgets and two PMax builds drafted (WRITE + DRAFT)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity 8/8 · report `2026-10-02-emergency-launch-search-terms-budget-pmax.md`
- EXECUTED (approved): `AMB-1002-EMER-CREATE-1` AF13621050E2 (18/18), `AMB-1002-GEO-CREATE-1` B7B7A99EA739 (17/17). All new ads PAUSED, under review.
- Awaiting approval: EMER-ENABLE-1 **BFBD1315E210** (10), NEG-EXACT-1 **D6ABF60771C3** (98), BUD-OCT-1 **A1B9032D7D60** (8, Oct 2 only),
  BUD-NOV-1 **39B1E83A72B0** (8), PMAX-A-1 **02556803100C** (64), PMAX-B-1 **F4D888845B8E** (215). validate_only clean on all.
- Tablets already -100% on all 8 Search campaigns; PMax tablet exclusions are inside the PMax plans.
- SiteGround refuses TLS from the agency machine since 07:04 ET (site up for third parties); Geothermal enable held for the countdown.

## 2026-10-02 — Search terms, Heating Repair Phrase review, Emergency + Geothermal launch plans (READ + DRAFT, 0 writes)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity 8/8 · **External writes: 0** (validate_only 6/6)
Report: `2026-10-01-search-terms-and-lp-activation.md` (+ appendix). Work orders: 3 new, all PASS.

- $42→$18 confirmed 2026-09-30 17:52:03 ET after serving ended. Day 1 of $18 (10-01): 149 / 3 / $47.04, CPC $15.68.
- UI edit 10-01 14:09 ET: tablets −100% on all enabled campaigns (old value not in change_event).
- Heating Repair PHRASE: $622.37 / 24 clicks / 0 verified leads (09-17..10-01); 418/421 visible impr NEAR_PHRASE. Verdict: clean up and monitor.
- 62 EXACT negative candidates drafted (not in any plan). Existing account-level BROAD manufacturer negatives still over-block.
- Plans: `AMB-1002-EMER-CREATE-1` **AF13621050E2** (3), `AMB-1002-GEO-CREATE-1` **B7B7A99EA739** (3); ENABLE drafts gated on
  dispatch confirmation (Emergency) and countdown removal (Geothermal). D6 open on every offer page.

## 2026-09-20 — Expansion re-verified against fresh data (READ + DRAFT, 0 writes)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity gate PASS · **MCC never written**
**External writes: 0.** Instruction re-sent two days on; whole sequence re-run rather than
re-reporting the 2026-09-18 figures.

### No account drift
- Enabled still **$237.00/day** across the same 5 campaigns; both heating campaigns still PAUSED
- `7DE31D6B6A88`, `39097845F5F4`, `A3370F96FA6E` all still executed and matching
- All 4 RSAs **APPROVED / REVIEWED**; 18/18 keywords **APPROVED / ELIGIBLE**
- September MTD $1,722.25 → **$1,746.40** (only $24.15 in two days), 11 days left

### Website: nothing deployed, all blockers stand
- DNI still swaps `410-914-1456` on every page; `410-761-0932` absent
- 101 duplicate ids (main site), 107 on `offer.` (`gform_2` ×2, `gform_1` ×3)
- Heat-pump destination now **9 consecutive `DESTINATION_NOT_WORKING` checks** over three days
- **NEW:** AdsBot receives **HTTP 200 and the full ~337KB page** — it is *not* served the
  SiteGround captcha stub, so the heat-pump verdict is not crawler blocking. The URL looks
  healthy and Google is retaining the verdict → needs a **policy re-review in the Ads UI**

### Plans
- `AMB-0918-HEAT-EXPAND-1` / **C7EA21996569** / 40 ops — unchanged, re-validated
- `AMB-0920-BUDGET-1` / **B9C59FEA2D68** / 6 ops — same allocation, refreshed September block
- `AMB-0918-BID-1` / **DA9FBFA2DAC0** / 2 ops — unchanged, re-validated
- `AMB-0918-BUDGET-2` / `4779F88E38BE` — **SUPERSEDED**, stale September data, never approved

All six `validate_only` checks pass. Awaiting the exact approval lines.


## 2026-09-18c — Heating expansion drafted and validated (READ + DRAFT, 0 writes)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity gate PASS (10/10) · **MCC never written**
**External writes: 0.** Three plans drafted, validated, fingerprinted, awaiting approval.

### Verified already executed (not replayed)
- `AMB-0917-HEAT-CREATE-1 / 7DE31D6B6A88` · `AMB-0918-BUDGET-1 / 39097845F5F4` ·
  `AMB-0918-CONV-1 / A3370F96FA6E` — all three reconciled against live state

### Drafted
- `AMB-0918-HEAT-EXPAND-1` / **C7EA21996569** / 40 ops — 2 campaigns, 2 budgets, 6 ad groups,
  32 keywords, 10 RSAs, cross-negatives, asset reuse. All create-PAUSED
- `AMB-0918-BUDGET-2` / **4779F88E38BE** / 6 ops — reallocation to $325.00/day total
- `AMB-0918-BID-1` / **DA9FBFA2DAC0** / 2 ops — CPC ceiling corrections

### Evidence gathered
- Site crawl: 200 URLs, 39 under `/services/` (`site-crawl-2026-09-18.json`)
- Destination policy: **8 of 9 pass**; heat-pumps fails 3/3 (`dest-policy-2026-09-18.json`)
- Nine-destination QA, desktop + mobile (`expansion-url-qa-2026-09-18.json`)
- Keyword Planner, 10-city sample, not scaled (`expansion-keyword-planner-2026-09-18.json`)
- Negative reachability, correctly scoped per campaign (`expansion-neg-conflict-2026-09-18.json`)
- Legacy heating history: $94,607 across 16 campaigns

### Blocked
- 🔴 Heat Pump Installation: `DESTINATION_NOT_WORKING`. Ad group + keywords drafted, **no RSA**
- 🔴 WhatConverts DNI swapping `410-914-1456` on all 9 pages; offer page also exposes `410-705-6354`
- 🔴 101 duplicate DOM ids (main site) / 54 (offer subdomain)
- 🔴 Unverified "most trusted" / "guaranteed" / "best" / "most knowledgeable" claims on three pages
- ⬜ Submission test blocked on deployment, not on identity


## 2026-09-18b — Budget + conversion corrections EXECUTED; EU field ratified (WRITE)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity gate PASS · **MCC `3373711342` never written**
**External writes:** 7 (5 budget amounts, 2 conversion-action flags) · **Nothing enabled, nothing deleted**

### Executed
- `AMB-0918-BUDGET-1` / `39097845F5F4` / 5 ops — enabled daily **$421.55 → $237.00**
  (HVAC Installation $95, AC Repair $45, HVAC Repair $70, HVAC Replacement $15,
  Gas Boiler Repair **$12**, the one increase). Readback **27 PASS / 0 FAIL**
- `AMB-0918-CONV-1` / `A3370F96FA6E` / 2 ops — `7643656486` WC Lead and `7643656075` WC Calls
  set `primary_for_goal=false`. **Biddable Primary 5 → 3.** Readback **8 PASS / 0 FAIL**
- Future total after heating enablement **$327.00/day = $9,940.80/month**, under the $328.94 cap

### Ratified
- `campaign.contains_eu_political_advertising = DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING`
  confirmed by the owner as a procedural recovery exception. Now agency policy in
  `config/agency.yaml` (`search_defaults` + `required_campaign_create_fields`); recorded in
  `client.yaml` → `procedural_exceptions`. Future manifests must include it **before** the
  fingerprint is computed.

### Corrected
- **`410-914-1456` is injected by WhatConverts DNI, not hard-coded.** Rendered number tracks
  `wc_swap` exactly: 14 loads with the cookie → `410-914-1456`; 6 loads without → base
  `410-761-0932`. DNI is also intermittent and fires only after interaction.
- v1 developer task was wrong on this point and is **superseded** by
  `clients/ambient-cooling-heating/dev-tasks/2026-09-18-ambient-tracking-fixes-v2.md`

### Gate status
- Google Ads side now **clean**: 4/4 RSAs `APPROVED`/`REVIEWED`, 18/18 keywords
  `APPROVED`/`ELIGIBLE`, budgets $237.00/day
- 🔴 Website still blocks launch. `AMB-0917-HEAT-ENABLE-1` **not created** — correctly gated
- ⛔ MasterGrass branch **stopped at the client gate**: no `client.yaml`, no child customer ID


## 2026-09-18 — Heating build EXECUTED paused, read back, tracking retested (WRITE + READ)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity gate PASS · **MCC `3373711342` never written**
**External writes:** 268 resource creations under `AMB-0917-HEAT-CREATE-1` / `7DE31D6B6A88`, **all PAUSED**
**Nothing enabled.** No budget, conversion action, existing campaign or website was changed.

### Executed
- 2 campaigns `24257819463` / `24257819466`, 2 budgets `15885327972` / `15885327975`,
  2 ad groups `199797580706` / `199797580746`, 18 keywords, 4 RSAs, 209 campaign criteria,
  9 assets, 22 campaign asset links — every one PAUSED
- First attempt aborted after committing both budgets (`field_error: REQUIRED` on the newly
  mandatory `campaign.contains_eu_political_advertising`). Inventoried, not blindly rerun;
  the resume **reused** the committed budgets rather than duplicating them

### Verified
- Readback **179 assertions, 0 FAIL** across two passes (`ambient_0917_readback.py`,
  `ambient_0917_readback2.py`) — including AI Max off, broad expansion off, asset automation
  off, `primary_status = PAUSED`, and all 23 live pre-existing campaigns unchanged
- Independent tracking retest, real browser, desktop + mobile, 7 pages, 14 clean visits,
  **zero parameterised requests sent**: 9 PASS / 2 FAIL / 3 NOT TESTED

### Added
- `reports/ambient-cooling-heating/2026-09-18-heating-execution-readback-and-corrections.md`
- `clients/ambient-cooling-heating/dev-tasks/2026-09-18-ambient-tracking-fixes.md`
- `clients/ambient-cooling-heating/plans/AMB-0918-BUDGET-1.json` — `39097845F5F4` (5 ops)
- `clients/ambient-cooling-heating/plans/AMB-0918-CONV-1.json` — `A3370F96FA6E` (2 ops)
- `clients/ambient-cooling-heating/snapshots/` — `tracking-retest-2026-09-17.json`,
  `conv-audit-2026-09-18.json`, `enabled-budgets-2026-09-18.json`
- `receipts/live/AMB-0917-HEAT-CREATE-1-2026-09-17*.json`,
  `receipts/validate-only/AMB-0918-CORRECTIONS-2026-09-18.json`

### Blocked
- 🔴 `410-914-1456` is the only number rendered **and is clickable**, 7 pages x 2 devices
- 🔴 101 duplicate DOM ids per page; `form#gform_2` present twice
- ⬜ NOT TESTED: attribution persistence, paid-session DNI, and one-submission-one-conversion
- `AMB-0917-HEAT-ENABLE-1` deliberately **not** produced — enablement gates unmet


## 2026-09-16 — Heating services research and strategy (READ + DRAFT)

**Account:** `Ambient Cooling - Live` / `2401959466` · identity gate 10/10 PASS
**Latest fully settled data:** 2026-09-15 · **External writes: 0** · **No campaign created or enabled**

### Added
- `reports/ambient-cooling-heating/2026-09-16-heating-services-research-and-strategy.md`
- `reports/ambient-cooling-heating/2026-09-16-heating-landing-page-drafts.md` (3 packages, 12 sections each)
- `reports/ambient-cooling-heating/2026-09-16-heating-rsa-and-asset-drafts.md` (6 RSAs, assets)
- `reports/ambient-cooling-heating/2026-09-16-heating-clickup-update.md`
- `clients/ambient-cooling-heating/work-orders/` — 1 composite manifest + 3 service-specific work
  orders, all validating PASS
- `clients/ambient-cooling-heating/exports/` — heating history (JSON + 2 CSV), Keyword Planner
  (JSON + CSV with raw micros), geo crosswalk CSV, candidate normalization CSV, profitability
  scorecard CSV, RSA draft CSV
- `clients/ambient-cooling-heating/snapshots/` — heating identity/baseline, browser capability
  verification
- `clients/ambient-cooling-heating/plans/AMB-0916-HEAT-STRATEGY-1.json` — `9EC0CE017DE7`
- `clients/ambient-cooling-heating/plans/AMB-0916-HEAT-BUDGET-1.json` — `54613304B752`, 6 ops
- Scripts: `ambient_0916_identity_baseline.py`, `ambient_0916_heating_history.py`,
  `ambient_0916_capability.py`, `ambient_0916_capability_browser.py`,
  `ambient_0916_geo_planner.py`, `ambient_0916_build_heating.py`,
  `ambient_0916_validate_rsas.py`

### Changed
- `clients/ambient-cooling-heating/client.yaml` — added `Heating Repair`,
  `Heat Pump Installation` and `Heating Installation` to `client.offer.services_in_scope` with
  full website evidence and an explicit note that this records VERIFIED CAPABILITY for research
  scope only, **not** approval to advertise. Added `services_excluded` (tankless water heaters,
  geothermal — both excluded on measured performance) and `services_capability_not_verified`
  (thermostat ×3, electric furnace repair).

### Status changes
- `AMB-0915-CPC-HR-1 / 14BD03817042` → **SUPERSEDED — DO NOT EXECUTE.** It proposed raising HVAC
  Repair $25 → $65; the August economics withdrew its basis (HVAC Repair spent $1,665.16 with zero
  traceable qualified leads and sells the lowest-ticket work).

### Not replayed
`AMB-0915-COMM-RSA-1 / 6C32B210CF5B` and `AMB-0915-COMM-ASSET-1 / 02F6EECCCDF8` remain
executed-and-paused. The 17 commercial negatives remain executed. Nothing was re-run.

### Key findings
- 15 historical heating campaigns: **$108,464.01 / 7,251 clicks / $14.96 CPC / 211.8 conversions**.
  Best CPA *Heating Repair* **$252.83**; worst *Tankless Water Heaters* **$6,265.89**.
- Keyword Planner (10 peer CITY targets, zero containment): `furnace repair` **320/mo**, LOW
  competition, **720 in January** versus 110 in September — a 6.5× seasonal swing.
- Bid estimates returned for only **4 of 64** heating keywords — bid recommendations therefore rest
  on account auction history, not Planner.
- WhatConverts trailing 12 months: **311 heating-intent leads, 98 qualified**. Heat pump +
  ductless = **36 of 98**. Boiler took the most paid leads (20) and qualified the fewest (8).
- 75 live geo targets = 28 City + 5 Neighborhood + 42 Postal Code, **zero containment overlap**.

### Corrections made during this session
- The first capability sweep used plain `urllib` and returned **0 pages**, producing a false
  "no heating services offered" verdict across all 33 candidates. The official site sits behind
  NitroCDN. Re-run in a real browser: 32 pages fetched, 8 dedicated heating pages found.
- The RSA validator flagged 5 issues. Three were real (a 31-character headline, two ad groups with
  14 headlines) and were fixed. Two were false positives — the barred-claim regex matched the
  ordinary verb *"review"*. The rule now requires a number or star.
