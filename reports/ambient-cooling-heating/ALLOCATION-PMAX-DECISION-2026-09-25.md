# Ambient — service allocation and PMax pilot decision (2026-09-25)

Account: Ambient Cooling - Live / 2401959466 (identity gate re-passed 2026-09-25, 8/8).
Evidence: `snapshots/pmax-economics-2026-09-25.json`, `inventory-2026-09-25.json`,
`routing-audit-2026-09-25.json`, `tracking-evidence-2026-09-25.json`, `final-state-2026-09-25.json`.

## Data quality first
- **Revenue, sold jobs and close rate are unknown**: WhatConverts `sales_value`/`quote_value` are empty on
  every lead; no CRM outcome exists. ROAS, CAC and allowable CPQL cannot be computed.
- **Qualification was not recorded in the heating season**: 57 of 76 paid-labelled leads (Oct 2025–Mar 2026)
  have `quotable` unset.
- **Paid labels are not attribution**: 0 of 76 heating-season paid-labelled leads carry a click ID. Most are
  calls on fixed-source numbers labelled `google/cpc` by configuration.
- **Historical conversions are contaminated**: the native form action counted any thank-you page view until
  GTM v16 (2026-09-24), and "Calls from ads" counts unqualified calls. Historical PMax CPA is a raw-contact
  CPA, not a qualified-lead CPA.

## Decision table (heating season Oct 2025–Mar 2026 unless stated)

| Service / campaign | Spend | Google raw conv | WC paid-labelled leads | Quotable Yes / No / unset | CPQL | Close rate, revenue, margin | Local demand | Confidence | Action |
|---|---|---|---|---|---|---|---|---|---|
| Heating & furnace repair incl. No Heat (Search 24257819463) | $32 Search + $3,873 Furnace-Repair PMax | 1 + 8 | 14 | 0 / 3 / 11 | unknown | unknown | Highest: 201 impressions today in Heating Repair; spent $168 (2× its $85) by 13:29 | Low | **Keep serving at $85.** No increase: repair leads qualify poorly where recorded. |
| Heating/furnace install & replace (Search 24257819466) | $6,200 | 12 (CPA $517) | 7 | 2 / 2 / 3 | ≥ $1,550 on decided | unknown | 92 impressions today; not budget-limited | Low–medium | **Keep serving at $60.** Best-evidenced value per August unit economics. |
| Heat pump repair / install / replace (24268690038) | $135 | 0 | 1 (2026) | 1 / 0 / 0 | unknown | unknown | 3 impressions today | Low | **Keep serving at $15.** |
| Boiler repair / replacement (24132507744) | $15,820 ($99 CPC) | 20 (CPA $791) | 19 | 5 / 0 / 14 | ≥ $3,164 | unknown | 9 impressions today | Low | **Keep serving at $45.** Boiler installation waits on its page (D2). |
| Thermostat (24268690041) | $0 history | 0 | 1 | 0 / 0 / 1 | unknown | unknown | 0 impressions since launch 2026-09-24 | None | **Keep at $15, no incremental budget.** |
| Geothermal (24274160783) | $202 all-time | 0 | 3 (+2 in 2026, both Yes) | 0 / 0 / 3 | unknown | unknown | 19 geothermal-intent impressions in 5 days (09-21..25) | Low | **Retain $20 test; ads paused until `/geothermal-heat-pump/` is published.** |
| Ductless heating installation | $1,990 (mostly 2025 cooling) | 5 | 3 (2026, all Yes) | 3 / 0 / 0 | unknown | unknown | 17 ductless-intent impressions in 5 days | Low | **Review not passed**: no offer page, no heating-season evidence. Ads paused; nothing displaced. |
| Maintenance / tune-up / inspection (24279798229) | $128 | 0 | 8 | 0 / 1 / 7 | unknown | unknown | 21 maintenance-intent impressions in 5 days | Low | **Deferred**: groups enabled, all ads paused. |
| PMax history: Furnace Repair 22855140165 | $4,931 total | 8 (7 Calls from ads) → $616 | n/a (no click IDs) | n/a | unknown | unknown | 1,993 heating-season clicks at $1.94: mostly non-search inventory | Low | Reference only. |
| PMax history: HVAC & A/C Install 22822619680 / #2 23883756382 | $15,425 / $1,478 | 49 → $315 / 3 → $493 | n/a | n/a | unknown | unknown | Mostly cooling season | Low | Reference only. Asset groups LIMITED / DISAPPROVED. |

## PMax pilot: built, held
- Chosen services: **furnace/heating replacement + installation** and **heat pump replacement**. These carry
  the best-evidenced value (August: replacement/installation = 94% of benchmark pipeline value), have ready
  pages, and exclude every deferred service. No geothermal PMax.
- Volume estimate: at the relevant raw CPA of **$484–$616**, $45/day for 6 weeks ($1,890) buys about **3–4 raw
  leads, 1–2 qualified**; $60/day ($2,520) buys about 4–5 raw, **2–3 qualified**. Google's learning guidance
  (daily budget ≥ 3 × CPA) implies about $1,450–$1,850/day. Neither candidate can produce a readable result
  in 4–6 weeks, and the uncertainty is larger than the effect we would be trying to measure.
- Gates at 2026-09-25:
  - **FAIL: economics.** See the volume estimate above.
  - **FAIL: paid website calls.** 705-6354 is a fixed-source number, so a call cannot be tied to a visit or click.
  - **FAIL: call de-duplication.** A call from an ad counts once as native "Calls from ads" and again when
    WhatConverts uploads it as WC Lead. The fix needs a WhatConverts rule, and the WhatConverts UI is logged out.
  - **NOT TESTED: import acceptance.** Checking it needs the WhatConverts UI.
  - **PENDING: images and videos.** No verified service-specific images are available.
  - **PASS: form capture, campaign settings and goals** (read back).
- **Scenario chosen: "Pilot not ready."** No budget transfer. Heating Maintenance stays enabled at a nominal
  $45 but serves nothing (every ad paused). The PMax shell 24295088845 is PAUSED with its own non-shared $20
  budget. $20 is the only unallocated headroom, so even an accidental enable stays at $325.
- Launch sequence once the gates pass (`AMB-0925-PMAX-LAUNCH`, not built yet):
  1. Create the asset groups from `plans/AMB-0925-PMAX-1.json` with reviewed images.
  2. Pause 24279798229 (the $45 donor).
  3. Raise the PMax budget to $45 and enable.
- Stop criteria:
  - Check on days 2, 7 and 14.
  - Pause at $900 spend with 0 WhatConverts leads carrying a click ID.
  - Pause if cost per raw lead exceeds $600 after $1,500.
  - Pause if more than 30% of leads are spam or out-of-scope.
  - Pause on any failed or duplicate upload.
- Scale criteria: at least 3 qualified new-customer leads with CPQL ≤ the Search CPQL over the same weeks.
  Compare against a Search-only baseline, and watch for brand/Search cannibalization.

## Update 2026-09-25 afternoon (WhatConverts signed in; images approved from landing pages)

**PMax asset groups BUILT, PAUSED** in held campaign 24295088845 (`receipts/AMB-0925-PMAX-GROUPS-1-EXECUTED.json`):
- 6751612859 "Heating & Furnace Replacement" → /hvac-replacement/ and 6751752096 "Heat Pump Replacement"
  → /heat-pump-replacement/. Each: 15 headlines (all ≤30, one ≤15), 5 long headlines ≤90, 5 descriptions ≤90
  (one ≤60), paths ≤15, CTA Get Quote, 4 landscape + 4 square + 2 portrait images, 10–12 search themes,
  audience signal "All Converters" (audience 360614515). Readback 0 FAIL; Google review pending.
- Images come from the offer landing pages, fetched in the browser and cropped without stretching. The heating group uses
  furnace photos, including an authentic installed furnace carrying an Ambient sticker. Excluded: ductless units, visible
  equipment brands, commercial rooftop work, and a palm-tree scene.
- No videos. The API refuses to opt out of generated videos; check the UI setting before launch.
- The pilot stays PAUSED, and nothing about the economics gate has changed.

**WhatConverts integration findings**
- Google Ads connection → Ambient Cooling (2401959466). Lead Conversion Name WC Lead; Call Extension Conversion Name
  WC Calls. The call-extension name is unused because no number is typed "Google Ads Extension".
- Trigger: New Lead Received. Value: Quote Value. Every lead type is sent. **Enhanced conversions: ON**, which sends
  every lead with a phone or email to WC Lead even without a click ID. This covers GBP/LSA/organic calls, wrong numbers
  and QA tests, and it is how call-asset calls reach WC Lead and double count with native "Calls from ads".
- All 6 documented QA leads had been sent (Success → WC Lead). Google credited none. All 6 are now marked Spam.
  The 6 "testing the form" leads carrying the QA phone number were left unflagged, as instructed.
- Numbers: 11 in total, and none is free to reuse. The only number-swapping one is 914-1456 "Website Traffic"
  (All Traffic, replaces 761-0932). 705-6354 is "GSA Cooling Traffic", a fixed Offline number that serves both
  the call asset and the pages. 216-4650 is "GLE Traffic" (paid Maps). 415-9517 is "GSA's Heat Traffic" and still
  receives contacts.
- Why the call double count is not changed yet:
  - Setting 705-6354 to type "Google Ads Extension" would also relabel direct website dials as ad calls.
  - Switching enhanced conversions off would stop all website-call uploads (not allowed).
  - Neither change can be verified until real ad calls arrive.
- Recommended fix, in order, gated on real calls:
  1. Give the call asset its own WhatConverts number, typed "Google Ads Extension".
  2. Confirm that real ad calls land as WC Calls, matched to Google's call records.
  3. Then make native "Calls from ads" non-biddable per campaign.

## 410-415-9517 as the heating call-asset number (owner-approved 2026-09-25, no purchase)

**Usage before the change**
- WhatConverts: "GSA's Heat Traffic", type Offline, fixed attribution google / cpc, forwarding to
  "Ambient Cooling and Heating" = 410-761-0932 (34 call records confirm). Recording with greeting,
  transcription, AI analysis and text messages on; PCI redaction off.
- Lead history:
  - 115 leads since June 2025. Heating-season peak was 21 in Nov 2025.
  - 30 carried a website session (main site plus the old /gas-boiler/ offer page). The last was 2026-03-18.
  - Since June: 2 calls in July, 1 call and 1 text in August, 1 text on 09-25, all with no website session.
    These are legacy callers, not proof of a paid click.
- Placements found: none live.
  - Not in the WhatConverts script (its only swap rule is 230773: 761-0932 → 914-1456).
  - Not on 217 main-site pages or 26 offer URLs.
  - Not on any Business Profile's primary phone.
  - Only on two old Google call assets (80497290055, 98498198415), which are linked to paused or removed
    campaigns only.
- Not inspected: Business Profile *additional* phone fields, Microsoft Ads, print/offline material.
- The GTM tag "GA - Phone Call Conversion" (Google website-call swap) still targets (410) 415-9517. It is inert
  because the number isn't displayed on any page, but it should be retargeted or retired before 415-9517 ever
  appears on a site.

**Changes (`AMB-0925-CALL-9517-1`, fingerprint 011F2890625B, readback 0 FAIL)**
- WhatConverts: type changed Offline → **Google Ads Extension** (list shows "Google Call Extension").
  Attribution stays at the default google / cpc. Name, forwarding and features are unchanged.
- Google Ads: new call asset **424764337810**, (410) 415-9517, Mon–Fri 08–16, account-level call conversion
  reporting (call reporting on). Linked to the 8 heating campaigns with the same status as the old
  705-6354 link: ENABLED on Heat Pump, Boiler, Thermostat, Maintenance, Geothermal and PMax; PAUSED on
  Heating & Furnace Repair and Install/Replace. The old 705-6354 links on those 8 are now PAUSED.
- Unchanged:
  - Commercial and the paused cooling campaigns (still 705-6354).
  - Landing pages (705-6354), paid Maps (216-4650) and GBP numbers.
  - Every conversion action: WC Lead, WC Calls and Calls from ads all still Primary.

**Status: Configured — awaiting a genuine call.**
- Google's review of the new asset is in progress.
- Google swaps in its forwarding number only once an ad group reaches roughly 20–50 clicks a month
  (WhatConverts help). Low-volume groups will show 415-9517 directly, and those calls leave no Google call
  record. There is nothing for WC Calls to match, and native "Calls from ads" can't count them.
- Enhanced conversions is still on, so the first call must be checked for a second WC Lead upload.
- Verifier: `scripts/ambient_0925_call_watch.py --since 2026-09-28`.
- Native "Calls from ads" becomes non-biddable per campaign only after real calls show WC Calls credit and no
  duplicate WC Lead.
