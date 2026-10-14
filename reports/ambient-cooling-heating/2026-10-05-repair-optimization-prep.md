# Ambient: Heating Repair optimization prep while the $18 test runs (2026-10-05)

**Account:** `Ambient Cooling - Live` · child `2401959466` (never MCC 3373711342) · **Service:** Heating Repair · campaign `24257819463`
**Mode:** READ / DRAFT. **External writes: 0** (no Google Ads, WhatConverts, Business Profile, GTM, website or conversion change; no form submitted, no call placed).
**Work order:** `clients/ambient-cooling-heating/work-orders/work-order-heating-repair-optimization-prep-2026-10-05.yaml`, PASS. Identity 8/8 PASS on every API run.
**Read:** API 2026-10-05 06:47 ET (Monday, before the 08:00 schedule; Oct 3–4 weekend = no serving). Landing pages 07:00–07:20 ET (headless Chromium, GET only).
**Live config verified unchanged:** $18 ceiling, $31.76 budget, Mon–Fri 08–16, 75 presence locations, tablets −100%, Search only, AI Max off.

## 1. Primary recommendations

1. **Search terms are clean of paid waste now.** Every clearly irrelevant query that ever cost money is blocked by the Oct 2 negatives. In the two complete $18 days, 100% of visible spend ($48.98) went to generic "HVAC company / contractor near me" searches: ambiguous, not irrelevant.
2. **Keep `heating repair` Phrase + Exact unchanged.** The 10-01 Phrase-pause trigger is not met (section 4).
3. **Four negative drafts, all $0 historical spend.** No separate execution plan; add them to the Oct 8 package (section 3).
4. **The $18 read on Oct 8 must be per click and per lead, not volume.** The Oct 2 budget cut ($85 → $31.76) throttled delivery after 09:00 that day and will cap the remaining test days (section 6).
5. **Two new measurement problems outrank the test** (section 7):
   - **The D5 fix created three distinct forms (gform_1, gform_3, gform_4). WhatConverts only tracks gform_1.** gform_3 is the visible lower "Get My Free Quote" form on desktop and mobile. A confirmed paid form submission on Oct 2 (Geothermal) has no WhatConverts lead.
   - **Conversion drift:** 6885463625 (LP form) and 6885576934 (LP website calls) switched from Secondary to **Primary** after the Oct 2 08:47 snapshot. No recorded plan did this.

## 2. Search-term audit (campaign 24257819463, Sept 17 – Oct 4)

- **Corpus:** 318 rows, 245 distinct queries, no threshold. Visible 719 impr / 13 clicks / **$319.41 of $720.90 (44%)**; Google withholds the rest.
- **Files:** every term, category, flag, coverage and verdict: `clients/ambient-cooling-heating/exports/repair-search-term-verdicts-2026-10-05.csv`. Summary: `snapshots/repair-search-term-analysis-2026-10-05.json`. Script `scripts/ambient_1005_repair_terms.py`.

| Category | Terms | Impr | Clicks | Spend | Test days (Oct 1–2) spend |
|---|---|---|---|---|---|
| Direct heating repair | 9 | 24 | 0 | $0 | $0 |
| Furnace repair | 20 | 109 | 0 | $0 | $0 |
| No-heat | 7 | 11 | 2 | $63.78 | $0 |
| Installation / replacement | 0 | 0 | 0 | $0 | $0 |
| Informational | 8 | 11 | 0 | $0 | $0 |
| Ambiguous (local HVAC company/contractor, place names, unconfirmed names, duct, commercial) | 109 | 323 | 7 | $135.35 | $48.98 |
| Clearly irrelevant / off-target | 92 | 241 | 4 | $120.28 | $0 |

**Verdicts:** Already excluded 91 · Monitor 106 · Keep 33 · Keep, service confirmation 11 · new negatives 4 (section 3).

| Review area | Observed | Status / decision |
|---|---|---|
| AC / cooling | 18 terms, 54 impr, **0 clicks ever** | All 18 excluded (EXACT, Oct 2). No AC phrase negative: zero spend, and `air conditioner repair` phrase would also block mixed heating-and-cooling searches. Re-check Oct 8. |
| Portable / space heaters | none observed | Already blocked: shared PHRASE `space heater`, account BROAD `portable`. |
| Fireplaces | 14 terms, 1 click $28.85 (Sept 25, before the list) | All 14 excluded by shared PHRASE `fireplace`. |
| Baseboard / radiant | 1 term (radiant floor heating system repair, 1 impr) | Not negated: capability not on record (service-confirmation item). `baseboard heater repair` would reach via `heater repair` Phrase; not observed. |
| Plumbing | 3 "plumbing and heating company" searches, $0 | Keep/Monitor: heating need plausible. No `plumbing` negative. |
| Water heaters | 1 term | Excluded; campaign PHRASE `water heater`, `hot water heater`, `tankless water heater` cover the family. |
| Non-HVAC equipment | pellet stove ×3, Webasto ×1 | All excluded EXACT; PHRASE `pellet stove` drafted for new wordings. |
| DIY / informational | 8 fault-code / troubleshooting terms, $0 | Monitor (settled 10-01: may hire after diagnosing). |
| Oil (out of scope since 09-21) | 9 terms, $0 | 7 excluded; 2 new. PHRASE `oil` drafted. |
| Competitors | 43 terms; $91.43 historical (Booths, S F Jones, Tevis) | 41 excluded. New: Thompson (Warren, OH) and G & G Mechanical (Baltimore address). The 4 names withheld 10-02 stay withheld (still unconfirmed). |
| Place names | 44 terms, $71.81 (hvac glen burnie $54.83, hvac contractors annapolis md $16.98) | Not negated (never-negate rule). Places outside the 75 targets stay Monitor; presence targeting governs the searcher's location. |

Never-negate words (near me, cost, price, pricing, quote, best, local, hire, emergency, manufacturers, places) were never used as a reason.

**Existing conflict, still live (flagged 10-01):** account-level BROAD `carrier`, `trane`, `lennox`, `goodman`, `rheem`, `bryant`, `american`, `amana`, `ruud` block "brand + furnace repair" in this campaign. That contradicts the manufacturer rule; it needs a supported-brands decision before a removal plan.

## 3. Proposed negatives (DRAFT, campaign 24257819463)

| # | Negative | Match | Observed basis | Spend | Why | Conflict check |
|---|---|---|---|---|---|---|
| 1 | `[thompson heating and cooling warren ohio]` | EXACT | 1 impr, Oct 2 | $0 | Names a Carrier dealer in Warren, Ohio (carrier.com dealer listing, 219 N River Rd NW) | no positive matches |
| 2 | `"oil"` | PHRASE | 8 oil queries, 11 impr, Sept 25–Oct 2, incl. new `oil furnace service near me` (Oct 2) and `troubleshooting oil furnace` | $0 | Oil is out of advertising scope (owner, 2026-09-21); wordings keep changing, so EXACT can't keep up | no positive contains "oil"; blocks only off-target terms in the corpus |
| 3 | `"g & g mechanical"` | PHRASE | 1 query (14 words, too long for EXACT), 7 impr on 4 days through Oct 2 | $0 | Business name + street address in Baltimore 21218; not an Ambient location. The firm itself could not be confirmed online | no positive matches |
| 4 | `"pellet stove"` | PHRASE | 3 queries, 9 impr (already EXACT-excluded) | $0 | Not an approved service; closes future wordings | no positive matches |

**No separate execution plan.** All four have $0 historical spend, and any mid-test change is a confound. Fold them into the Oct 8 package.

## 4. `heating repair`: Phrase vs Exact

| Keyword (Heating Repair 204129717007) | Since Sept 17 | Baseline 09-24..30 | Oct 1–2 |
|---|---|---|---|
| `heating repair` PHRASE 142140741 | 1,098 impr / 26 clk / **$657.12** (91% of campaign) / 0 verified leads | 924 / 21 / $575.33 | 143 / 5 / $81.79 (100%) |
| `heating repair` EXACT 116678509 | 5 impr / 0 clk | 3 / 0 | 2 / 0 |
| All 4 Exact keywords in the group | 32 impr / 0 clk | | |

- **Visible Phrase traffic is semantic:** 492 of 495 visible impressions are NEAR_PHRASE; 1 contains the words "heating repair".
- **Visible Phrase spend:** clearly irrelevant $120.28 (all now excluded), ambiguous $135.35, heating/furnace/no-heat $0. **Oct 1–2:** $48.98 visible, all ambiguous, 0 irrelevant.

**Recommendation: keep Phrase + Exact; do not schedule a Phrase pause.**
- Exact alone drew ~2.6 impressions per serving day. Pausing Phrase would effectively stop repair delivery (owner rule) and void the $18 test.
- The irrelevant share the 10-01 trigger was designed to catch is now 0%.
- The remaining traffic is generic local-HVAC intent whose outcome is hidden by the untracked location-call path (section 5). Match type is not the binding problem.
- **Trigger (unchanged from 10-01):** revisit only when Phrase has ≥$300 since Oct 1 **and** 0 verified paid leads **and** ≥50% of visible Phrase spend is clearly irrelevant or non-heating. Now: $81.79 (27%), 0 leads, 0% irrelevant → **not met**.
- **Per-query trigger (10-02):** a generic query reaching $100 with no verified lead becomes an EXACT candidate. Highest now: `hvac glen burnie` $54.83.

## 5. Phone attribution (read-only)

| Number | Role | WhatConverts config (10-05) | Where it shows now | WC records since 09-24 |
|---|---|---|---|---|
| 410-705-6354 | paid LP base number | "GSA Cooling Traffic", fixed google/cpc, no session binding | Rendered 4–6× and in every tel: on both repair pages (GTM phone fix forces it). Call asset 407995613637 PAUSED on all heating campaigns | 0 |
| 410-914-1456 | website DNI | "Website Traffic", pool All Traffic, swaps 761-0932; last used 10-05 10:50 UTC | Rendered 0 on offer pages (phone fix state `bridge:wc`) | 11 (5 default, 6 duplicate): direct, GBP, organic, google/cpc ×2 (one click-ID verified 09-28 Furnace Replacement; one 09-30 main-site, no click ID) |
| 410-415-9517 | heating call-asset number | "GSA's Heat Traffic", fixed google/cpc | Call asset 424764337810 ENABLED on Boiler, Heat Pump, Thermostat, Geothermal, Maintenance, PMax A/B; **PAUSED on Repair** and Install/Replace. Also the number in GTM's website-call tag | 1 spam text; 0 calls |
| 410-761-0932 | final destination | destination of the pool numbers | **3× in server HTML** of both repair pages (D1); rendered 0 | n/a |
| 410-216-4650 | paid Maps / location override (read 09-24) | "GLE Traffic", google/cpc | Business Profile Ads phone on Severn + Annapolis (09-24) | 0 (last record Aug 20) |

WhatConverts `last_used` is blank for 705-6354 and 216-4650 although both took calls. **It cannot prove a number was "never used."**

**Google call records vs WhatConverts (all campaigns, since Aug 14):** 10 Google calls; 5 matched (Aug 20 → 216-4650 location path; Aug 24, Aug 28, Aug 31, Sept 1 → 705-6354 call asset); 5 unmatched.

- **Since the heating build:** 2 Google calls, **both Heating Repair, both unmatched**: Sept 25 12:11 (52 s) and Sept 30 11:38 (60 s), mobile, display location AD.
- **Path:** change history shows both repair call-asset links (705-6354 on Sept 17, 415-9517 on Sept 25 18:56) were **created paused and never enabled**, so both calls came through the **Business Profile location asset**.
- **Unrecorded:** WhatConverts has no record of any kind (any number, including duplicate and spam sets) within ±90 min of either call.
- **Location-asset clicks:** 9 of 23 baseline clicks ($218.96, 34%) and 3 of 5 test clicks ($48.23, 59%). Their calls currently reach a number WhatConverts does not record.

**Double counting:**
- **Repair campaign:** none in either window; Google credited 0 Conversions.
- **Live structural path 1:** a call-asset call counts in Google "Calls from ads" and again as a WhatConverts upload. This was proven on Sept 1. It is live wherever 415-9517 is enabled; no instance since Sept 24, because there were no call-asset calls.
- **New path 2 (from the drift):** a paid gform_1 submission now counts twice as Primary (WC Lead + native 6885463625). Oct 2 Boiler Replacement form: WC Lead + native + GA4.
- **6885576934:** its GTM tag swaps (410) 415-9517, which appears on no offer page, so it is inert on paid pages.

**Business Profile Ads-phone override: still needs manual UI verification.**
- The API can't read it.
- Last read: Sept 24 (Severn + Annapolis = 216-4650; Ellicott City no override and not in asset set 8620443109).
- Since then, two location-path calls left no WhatConverts trace and 216-4650 has logged nothing.

## 6. $18 test baseline and template

**Files:** `snapshots/repair-18-baseline-2026-10-05.json`, template `exports/repair-18-test-template-2026-10-05.csv`, script `scripts/ambient_1005_repair_baseline.py`.

- **Test days:** Oct 1, 2, 5, 6, 7. That is the same Thu/Fri/Mon/Tue/Wed mix as the baseline.
- **Read:** Oct 8 (spend, IS, terms); re-read leads Oct 15 for lag.
- **IS revision:** Google has revised baseline impression share since the 10-01 read (36.5/32.5/31.1 then). Use these values.

| Metric | Baseline 09-24..30 ($42) | of which 09-30 (old $42) | Oct 1 | Oct 2 | Oct 5 | Oct 6 | Oct 7 | Test total (to date) | Δ per serving day |
|---|---|---|---|---|---|---|---|---|---|
| Serving days | 5 | 1 | 1 | 1 | | | | 2 | |
| Impressions | 1,232 | 165 | 149 | 48 | | | | 197 | |
| Clicks | 23 | 6 | 3 | 2 | | | | 5 | |
| CTR | 1.87% | 3.64% | 2.01% | 4.17% | | | | 2.54% | |
| Avg CPC | $27.79 | $28.20 | $15.68 | $17.38 | | | | $16.36 | |
| Spend | $639.11 | $169.21 | $47.04 | $34.75 | | | | $81.79 | |
| Per serving day impr / clk / spend | 246.4 / 4.6 / $127.82 | 165 / 6 / $169.21 | 149 / 3 / $47.04 | 48 / 2 / $34.75 | | | | 98.5 / 2.5 / $40.90 | |
| Location-asset clicks / spend | 9 / $218.96 | 1 / $31.45 | 2 / $31.25 | 1 / $16.98 | | | | 3 / $48.23 | |
| Verified genuine paid leads | 0 | 0 | 0 | 0 | | | | 0 | |
| Qualified (Quotable Yes) | 0 | 0 | 0 | 0 | | | | 0 | |
| CPL / CPQL | undefined ($639.11 / 0) | undefined | undefined | undefined | | | | undefined | |
| Google calls with no WC record | 2 (52 s, 60 s) | 1 | 0 | 0 | | | | 0 | |
| Search IS | 37.9% | 31.7% | 28.4% | 26.3% | | | | 27.7% | |
| Lost IS (rank) | 33.0% | 6.0% | 71.6% | 67.1% | | | | 70.1% | |
| Lost IS (budget) | 29.2% | 62.2% | 0.0% | 6.6% | | | | 2.2% | |
| Top / abs-top IS | 25.8% / 15.1% | 20.8% / 11.2% | 20.3% / 10.0% | 15.8% / 10.0% | | | | 18.8% / 10.0% | |
| Mobile clk / spend | 19 / $564.71 | 5 / $140.24 | 2 / $31.25 | 1 / $17.77 | | | | 3 / $49.02 | |
| Desktop clk / spend | 4 / $74.40 | 1 / $28.97 | 1 / $15.79 | 1 / $16.98 | | | | 2 / $32.77 | |
| Tablet impr | 12 | 0 | 0 | 0 | | | | 0 | |
| Heating Repair group (= `heating repair` Phrase) clk / spend | 21 / $575.33 | 6 / $169.21 | 3 / $47.04 | 2 / $34.75 | | | | 5 / $81.79 | |
| Other ad groups clk / spend | 2 / $63.78 (Furnace Repair, `furnace not working`) | 0 | 0 | 0 | | | | 0 | |
| Visible search-term spend (share) | $270.43 (42%) | | | | | | | $48.98 (60%) | |
| Visible: irrelevant / ambiguous / heating-furnace-no-heat | $120.28 / $86.37 / $63.78 | | | | | | | $0 / $48.98 / $0 | |

**Sensitivity:**
- If both unmatched Google calls were genuine, baseline CPL would be $319.56. Their genuineness is unknown.
- Baseline without Sept 30: 1,067 / 17 / $469.90, CPC $27.64, IS 39.6%, rank 40.3%, budget 20.1%.

**Confounds:**

| When (ET) | Change |
|---|---|
| 10-01 14:09 | Tablets −100% (UI) |
| 10-02 08:21 | Emergency Heating Repair enabled (0 impressions so far) |
| 10-02 08:33 | 60 campaign EXACT negatives |
| 10-02 08:44 | Budget $85 → $31.76 |
| 10-02 10:53–14:07 | 4 ClickCease IP exclusions |
| after 10-02 08:47 | Conversion primaries changed (does not affect Maximize Clicks bidding) |
| between 10-01 and 10-05 | Offer-page form rebuild (gform_3/4) |

**Budget throttle on Oct 2:** the campaign spent $34.75 in the 08:00 hour and then trickled (1–12 impr/hour, against 7–30 on Oct 1). With $31.76/day at ~$16–18 CPC, Oct 5–7 will be budget-capped near 2 clicks/day.

**How to judge on Oct 8:** CPC, CTR, click-type mix, search-term mix and leads per click. Do not use clicks/day or impression share alone. Do not judge on partial same-day data.

## 7. Conversion blockers: current status

| Item | Status 2026-10-05 | Evidence |
|---|---|---|
| D6 optional field required | **FIXED** | /hvac-repair/ and /furnace-repair/: label "Tell us about your project (optional)", no required class, no aria-required, no required attribute |
| D5 duplicate forms / IDs | **FIXED for IDs; new capture gap** | Server sends gform_1, gform_3, gform_4 (distinct); 0 duplicate form IDs at 1366 px and 390 px. WhatConverts `/tracking/forms` lists only gform_1 (offer) and gform_2 (main site). gform_3 = visible lower form (desktop ~4,870 px, mobile ~9,450 px); gform_4 hidden. The GTM submit hook covers every `gform_N`, so the native tag fires; WhatConverts does not. **Oct 2:** Geothermal ad group recorded a gated native form conversion + GA4 form_submission (paid click) with **no WhatConverts lead** |
| D7 attribution under cache | **Poisoning resolved; fields now empty** | Shared copy (x-proxy-cache HIT) has empty hidden fields; a unique-key MISS shows the server no longer writes query values into fields; a simulated cached load with a visitor gclid left all fields empty. Form leads rely on WhatConverts' session (Oct 2 Boiler Replacement form carried its click ID). Fill-at-submit not testable without a submission |
| D1 base number in source | **OPEN** | 761-0932 ×3 in server HTML on both pages; rendered 0 |
| Call path | **OPEN** | Two Heating Repair location-asset calls with no WhatConverts record; Business Profile Ads phone unverified since 09-24; no test call made |
| Conversion primaries | **NEW drift** | 6885463625 and 6885576934: Secondary/not counted on 10-02 08:47 → Primary/counted on 10-05 06:47. The API has no change history for conversion actions |

**D7 test safety:** no request carrying a marker reached the shared cache key. The unique-key MISS fetch used a never-repeated parameter. The cached-visitor case was simulated in the browser (request intercepted and served from the shared copy), with analytics/Ads beacons aborted. Evidence: `snapshots/lp-blockers-2026-10-05.json`.

## 8. Actions required

**Green Marketing:**
1. **WhatConverts:** add gform_3 and gform_4 (offer template) to form tracking. Check Gravity Forms entries for 2026-10-02 to recover the Geothermal submission WhatConverts missed.
2. **Conversion drift:** confirm who switched 6885463625 / 6885576934 to Primary and why. **Recommended:** keep 6885463625 Primary only until step 1 is verified, because it is currently the only capture for gform_3. Then return both to Secondary in one plan (separate approval).
3. **Business Profile Manager:** for Severn ("BIP … Woodbine" label), Annapolis and Ellicott City, read Advanced settings → Google Ads phone and record each value. If 216-4650 is still set, ask WhatConverts to confirm 216-4650 routing (its destination field reads blank).
4. Set Quotable on recent leads; CPQL cannot be computed.
5. Oct 8: approve or decline the 4 negatives in section 3 together with the test read.
6. Supported-manufacturer decision for the account-level BROAD brand negatives (open since 10-01).

**Developer:**
1. D1: remove 761-0932 from the offer template's server HTML.
2. D7 follow-on: populate the gclid/UTM hidden fields client-side at submit (from the URL or the `_gcl_aw` cookie), or remove them. Never populate them server-side behind the full-page cache.
3. Keep the three form IDs distinct. Do not revert to triple gform_1. Coordinate with Green Marketing so WhatConverts lists all three.

## Files

Scripts: `scripts/ambient_1005_repair_read.py`, `ambient_1005_terms_list.py`, `ambient_1005_repair_terms.py`, `ambient_1005_phone_paths.py`, `ambient_1005_lp_blockers.py`, `ambient_1005_lp_followup.py`, `ambient_1005_repair_baseline.py`; reconciliation `ambient_0930_cpl_reconcile.py 2026-10-05`.
Snapshots: `repair-read-2026-10-05.json`, `cpl-reconciliation-2026-10-05.json`, `phone-paths-2026-10-05.json`, `lp-blockers-2026-10-05.json`, `repair-search-term-analysis-2026-10-05.json`, `repair-18-baseline-2026-10-05.json`.
Exports: `repair-search-terms-2026-10-05.jsonl`, `repair-search-term-verdicts-2026-10-05.csv`, `repair-18-test-template-2026-10-05.csv`.
