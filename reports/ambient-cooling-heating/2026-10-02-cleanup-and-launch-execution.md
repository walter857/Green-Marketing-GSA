# Ambient: account cleanup and launch, execution report

**Account:** Ambient Cooling - Live · **2401959466** (never the MCC 3373711342) · executed 2026-10-02, 08:21–08:45 ET
**Authority:** Green Marketing staged authorization of 2026-10-02 (prepare and validate, create paused, read back, then enable).
Every fingerprint below was computed fresh under that authorization. None of them is an earlier approval code.

## 1. Execution summary

| # | Plan | Fingerprint | Ops | Executed (ET) | Readback |
|---|---|---|---|---|---|
| 1 | AMB-1002-EMER-ENABLE-1 | BFBD1315E210 | 10 | 08:21:49 | 5/5 PASS, both ads APPROVED |
| 2 | AMB-1002-NEG-EXACT-2 | 04E22EF928DD | 104 | 08:33:21 | 104/104 saved as EXACT negatives |
| 3 | AMB-1002-SEARCH-LAUNCH-1 | C903F9B1F413 | 7 + 41 | 08:36:32 | 15/15 PASS |
| 4 | AMB-1002-PMAX-A-2 | 405EDDC8E478 | 68 | 08:44:18 | 22/22 PASS (A and B combined) |
| 5 | AMB-1002-PMAX-B-2 | 157DF8F88A9A | 304 | 08:44:18 | (combined above) |
| 6 | AMB-1002-BUD-OCT-2 | A21B8F53ABDC | 8 | 08:44:54 | 8/8 PASS |
| - | AMB-1101-BUD-NOV-2 | 150006548BA1 | 10 | **not executed** | The executor refuses to run before 2026-11-01 |

No partial writes and no deletions. The superseded drafts were never executed: NEG-EXACT-1 D6ABF60771C3, PMAX-A-1, PMAX-B-1, BUD-OCT-1 and BUD-NOV-1.

**Problems found and fixed before writing:**

- **PMax shell A did not exclude tablets.** Its TABLET row had no bid modifier; the old plan's readback would have caught this. A-2 sets it to 0, and it was verified after saving and again after enabling.
- **Shared list 12249470554 holds 275 BROAD and 216 PHRASE negatives.** It is not attached to campaign B. Only the all-EXACT list 12252013691 (78 EXACT) is attached.
- **Three automation opt-outs are not available for PMax.** GENERATE_LANDING_PAGE_PREVIEW, GENERATE_VIDEOS_FROM_OTHER_ASSETS and GENERATE_ANIMATED_IMAGES_FROM_OTHER_ASSETS returned "enum value is not permitted". The 6 that are available are opted out, including Final URL expansion and text customization.
- **Competitor evidence text was corrected.** Website domains that could not be traced to a source were removed. "bnb heating and cooling" and "frosty heating and air conditioning" were re-verified from first-party listings before being kept.

## 2. Emergency receipt

- **Ad group:** 204129717047 Emergency Heating Repair, in Repair campaign 24257819463.
- **Final URL:** `https://offer.ambientcoolingandheating.com/emergency-heating-repair/`
- **RSAs:** 826702584886 (A) and 826702584889 (B). Both were created PAUSED by EMER-CREATE-1 AF13621050E2 (18/18) and are now ENABLED, APPROVED and REVIEWED.
- **Keywords:** 6 enabled. These are 3304047112, 320791640594, 777693505, 1734598708, 299713058575 and 4213560696 (`emergency furnace repair` PHRASE).
- **Labels:** WAITING_LP and WAITING_AVAILABILITY removed.
- **Copy and campaign settings:**
  - The copy makes no 24/7, immediate-arrival or response-time promises.
  - The $18 ceiling is unchanged, as are Mon–Fri 08:00–16:00, the 75 presence locations and the −100% tablet modifier.
  - The budget later became $31.76 under BUD-OCT-2.

## 3. Geothermal and Maintenance: URLs and receipts

**Geothermal** (`https://offer.ambientcoolingandheating.com/geothermal-heat-pump/`)

- **Search:** RSAs 826785945725 and 826785945728 are ENABLED and APPROVED in ad group 204129719007. They were created by GEO-CREATE-1 B7B7A99EA739 (17/17). WAITING_LP was removed.
- **Sitelinks:** Heat Pump Installation 424666395915 and Heat Pump Replacement 424481139482 were linked to campaign 24274160783. The "Diagnosis Explained" callout 422577777430 was paused there, because the geothermal paid scope excludes repair.
- **New sitelink:** "Geothermal Heat Pumps" 426109948970, pointing to /geothermal-heat-pump/. It is linked to the Heat Pump & Ductless campaign (ELIGIBLE) and to PMax B.
- **PMax B:** asset group "Geothermal Heat Pump" 6754769610 uses the required URL.

**Maintenance** (`https://ambientcoolingandheating.com/services/heating-services/`)

- **10 RSAs ENABLED** in campaign 24279798229:
  - Furnace Maintenance: 825585199649 and 825585199652. Their final URLs were changed in place from /furnace-repair/ to the required URL; under review.
  - Heating Maintenance: 825585199655 and 825585199658.
  - Furnace Tune-Up: 825585199661, plus new 826714155502.
  - Heating Tune-Up: 825585199667 and 825585199670.
  - Heating System Inspection: 825585199673, plus new 826714155505.
- **Kept PAUSED:**
  - 825585199664: Restricted housing, fully limited.
  - 825585199676: carries the unverified claim "Clear Written Findings".
- **Labels:** DEFERRED_BUDGET and WAITING_LP removed from all 5 ad groups.
- **Sitelinks linked:** Furnace Repair 424583525083, No Heat Repair 424481123441, Heat Pump Maintenance 424481133551 and HVAC Replacement 410638278156. All are ELIGIBLE.
- **Not used:** "Maintenance Plans" 189992410271, because its URL redirects to the homepage.

**Other parts of SEARCH-LAUNCH-1:**

- **Commercial:** RSAs 824781897834 and 824781897837 enabled (APPROVED). The "Prompt, Reliable Service" callout 407418595411 was paused in HVAC Installation because it implies a response time.
- **Boiler Installation (204129718247):**
  - 2 RSAs were created PAUSED from the held AMB-0925 payload (826714155508 and 826714155511), read back, then enabled; under review.
  - 3 keywords enabled: `boiler installation` PHRASE and EXACT, and `boiler installers near me` EXACT.
  - WAITING_LP removed.
- **No Heat Repair:** `house has no heat` EXACT 410033471640 enabled. `no heat service` PHRASE stays paused as ambiguous.

## 4. Status matrix (snapshot 08:47 ET)

| Campaign | ID | Type | Status | Live groups | Held / paused groups |
|---|---|---|---|---|---|
| Heating & Furnace Repair | 24257819463 | Search | ENABLED, Limited (bid strategy) | 6: Heating Repair, Furnace Repair, Gas Furnace Repair, Electric Furnace Repair, No Heat Repair, **Emergency** | — |
| Heating & Furnace Install & Replace | 24257819466 | Search | ENABLED, Limited (bid strategy) | 4 | Ductless Heating Installation (HELD, no page) |
| Boiler Services | 24132507744 | Search | ENABLED, Limited | 4: Boiler Repair, Boiler Replacement, Gas Boiler Repair, **Boiler Installation** | Boiler Maintenance (HELD, page still wrong) |
| Heat Pump & Ductless Heating | 24268690038 | Search | ENABLED, Eligible | 3 | Heat Pump Maintenance (HELD, owner deferral 09-25); Ductless Heating Repair (HELD, no page) |
| Thermostat Services | 24268690041 | Search | ENABLED, Learning | 3 | — |
| Heating Maintenance & Inspection | 24279798229 | Search | ENABLED, new ads in review | **5** (all) | — |
| Geothermal Heat Pump | 24274160783 | Search | ENABLED | **1** | — |
| HVAC Installation | 24132507747 | Search | ENABLED, Eligible | **Commercial HVAC Installation** | residential HVAC Installation (PAUSED, intended) |
| PMax, Furnace & Boiler Replacement | 24295088845 | PMax | ENABLED, groups in review | Heating & Furnace Replacement, **Boiler Replacement** | old Heat Pump Replacement 6751752096 (PAUSED; moved to B) |
| PMax, Heat Pump & Geothermal | 24318905515 | PMax | ENABLED, Learning | **Heat Pump Replacement, Heat Pump Installation, Geothermal Heat Pump** | — |

Ad-group totals across the 8 Search campaigns: **27 eligible, 4 held, 1 intentionally paused**.

The "has ads disapproved" flags come only from four PAUSED legacy ads with a Consumer Finance policy finding. Full per-ad-group matrix: `reports/ambient-cooling-heating/2026-10-02-status-matrix.md`.

**Settings verified on all 10 campaigns:**

- Tablets are excluded on all 10, and desktop and mobile are not excluded.
- On the 8 Search campaigns, Search Partners, Display and AI Max are off and text customization is opted out.
- Every campaign uses presence targeting with 75 locations.
- HVAC Installation keeps its older Mon–Fri 08–20 + Sat 08–13 schedule (the account standard since August). All other campaigns run Mon–Fri 08–16. Not changed.

## 5. PMax receipts

**A, "PMax | Furnace & Boiler Replacement | Central MD | 2026-10" (24295088845)**

- **Changes:**
  - Renamed.
  - Budget 15897049193: $20.00 → **$33.33**.
  - Tablet criterion 30002 modifier set to 0.
  - 6 automation opt-outs re-asserted.
  - 4 EXACT scope negatives added.
- **New PAUSED asset group "Boiler Replacement" 6754646450**, pointing to /boiler-replacement/: 20 new text assets, 29 links, 10 themes plus an audience.
- **Readback:** ✓ before enabling. Then the campaign, 6751612859 and 6754646450 were ENABLED. 6751752096 stays PAUSED.

**B, "PMax | Heat Pump & Geothermal | Central MD | 2026-10" (24318905515)**

- **Campaign settings:**
  - Budget 15923100463 at **$33.33**, not shared.
  - Maximize Conversions with no target and no value bidding.
  - Presence targeting, 75 locations, English, Mon–Fri 08–16, tablets excluded.
  - Brand guidelines on, 6 automation opt-outs.
- **Negatives:** 10 EXACT negatives, plus EXACT-only shared list 12252013691.
- **Assets:** 18 campaign asset links.
- **Asset groups:**
  - Heat Pump Replacement 6754769607 (36 existing assets).
  - Heat Pump Installation 6754769691.
  - Geothermal Heat Pump 6754769610: 36 links, including 10 new images from the client's geothermal page.
- **Conversion goals:** set to match A (1 goal updated: Calls from ads under phone-call lead is not biddable).
- **Readback:** ✓, then everything was enabled and checked again ✓.

**Geothermal images:** cropped from the 4 images published on /geothermal-heat-pump/. There is no text or logo in any of them. Source hashes are in `clients/ambient-cooling-heating/assets/pmax-geothermal-2026-10-02/manifest.json`.

- 426294548835 (piping, landscape), 426209261668 (piping, square), 426110646392 (piping, portrait)
- 426209274952 (utility room, landscape), 426110646395 (utility room, square), 426110646887 (utility room, portrait)
- 426110646389 (living room, landscape), 426110646884 (living room, square)
- 426209274955 (thermostat, landscape), 426110646398 (thermostat, square)

**Geothermal copy** uses only claims verified on the page:

- free quote
- property-specific review
- replacement planning
- new-system consultation
- ground-loop arrangement
- serves Severn, Severna Park, Columbia and Annapolis

There is no repair, response-time or price claim.

## 6. Asset eligibility (read 08:47–08:50 ET)

- **Search ads:**
  - 6 are still in review: 2 Boiler Installation, 2 URL-changed Furnace Maintenance, and the 2 new Maintenance ads.
  - All other enabled ads are APPROVED.
  - No enabled ad is disapproved or limited.
- **Sitelinks and callouts** on Maintenance, Geothermal, Heat Pump and HVAC Installation are all ELIGIBLE and APPROVED. The new geothermal sitelink is already APPROVED.
- **PMax:**
  - All 5 enabled asset groups are PENDING (under review). Ad strength reads Pending on group 6751612859 and Poor on the other four; there is no video and only one image set per group.
  - A's logo is "approved, labeled" (limited, still serves).
  - B's brand assets are PENDING.
- **Disapproved but not serving anywhere current:** 4 PAUSED legacy ads (Consumer Finance), and sitelinks 218980811215 and 218980811224 (destination not working) on 4 PAUSED legacy PMax campaigns.

## 7. Housing findings

- **Restricted housing (fully limited)** appears only on two PAUSED ads:
  - 825585199646 (Boiler Repair, main-site URL)
  - 825585199664 (Furnace Tune-Up)
- **No enabled ad or asset carries a housing finding** (08:50 read). The 75 targets are 42 ZIP codes, 28 cities and 5 neighborhoods. ZIP targeting therefore restricts nothing that is live, and **no targeting change was made**.
- **The existing appeal was respected.** Its status is visible only in the Google Ads web UI and was not checked in this session.
- **Risk:** if any new RSA or PMax asset is classified as housing during review, it will not serve to the 42 ZIP targets. Re-check the policy read after review completes.

## 8. Complete negative table

See `clients/ambient-cooling-heating/exports/negative-table-2026-10-02.md`. The same table is reproduced in the response.

## 9. Budget table: see the response, or `plans/AMB-1002-BUD-math.json`

## 10. Performance baseline and forecast: see the response, or `snapshots/forecast-2026-10-02.json`

## 11. Attribution and developer dependencies: see the response

## 12. Manifests and receipts

- **Plans:** `clients/ambient-cooling-heating/plans/`
  - AMB-1002-NEG-EXACT-2.json, AMB-1002-SEARCH-LAUNCH-1.json, AMB-1002-PMAX-A-2.json, AMB-1002-PMAX-B-2.json, AMB-1002-BUD-OCT-2.json, AMB-1101-BUD-NOV-2.json
- **Receipts:** `clients/ambient-cooling-heating/receipts/`
  - AMB-1002-EMER-ENABLE-1-EXECUTED.json, AMB-1002-NEG-EXACT-2-EXECUTED.json, AMB-1002-SEARCH-LAUNCH-1-EXECUTED.json, AMB-1002-PMAX-LAUNCH-EXECUTED.json, AMB-1002-BUD-OCT-2-EXECUTED.json
- **Scripts:** scripts/ambient_1002_neg_final.py, ambient_1002_search_launch.py, ambient_1002_pmax_launch.py, ambient_1002_budget_plan.py (v2), ambient_1002_neg_table.py
- **Snapshots:**
  - snapshot-2026-10-02.json (08:47), with preserved copies -0710 and -0822
  - cpl-reconciliation-2026-10-02.json (refreshed), with preserved copy -0726
  - policy-2026-10-02.json, pmax-asset-eligibility-2026-10-02.json, forecast-2026-10-02.json
