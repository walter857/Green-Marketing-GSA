# Ambient: Emergency launch, full search-term review, tablets, budget and PMax (2026-10-02)

**Account:** `Ambient Cooling - Live` · child `2401959466` (never MCC 3373711342) · heating-cooling. Identity 8/8 PASS on every run.
**Time zone:** America/New_York. **Snapshot:** 2026-10-02 07:10 ET (account "yesterday" = 10-01; 10-02 had not started serving).

**Work orders** (all PASS the repo validator):
- `work-order-emergency-heating-repair-lp-2026-10-01.yaml` (now mode `enable`)
- `work-order-geothermal-heat-pump-lp-2026-10-01.yaml` (`create-paused`)
- `work-order-search-terms-sept-oct-2026-10-02.yaml`
- `work-order-budget-allocation-2026-10-02.yaml`
- `work-order-pmax-furnace-boiler-replacement-2026-10-02.yaml`
- `work-order-pmax-heat-pump-geothermal-2026-10-02.yaml`

The search-term work order records each campaign's approved service.

## External writes made (both approved by exact line in Green Marketing's message)

| Plan | Fingerprint | Time (ET) | Result | Readback |
|---|---|---|---|---|
| AMB-1002-EMER-CREATE-1 | AF13621050E2 | 2026-10-02 ~07:02 | RSA A `826702584886`, RSA B `826702584889` (PAUSED, `/emergency-heating-repair/`), PHRASE `emergency furnace repair` `4213560696` (PAUSED) | 18/18 PASS |
| AMB-1002-GEO-CREATE-1 | B7B7A99EA739 | 2026-10-02 ~07:03 | RSA A `826785945725`, RSA B `826785945728` (PAUSED, `/geothermal-heat-pump/`); ad-group sitelink link `204129719007~290641223062` PAUSED | 17/17 PASS |

**Pre-execution checks:**
- Fingerprints recomputed from disk and matched.
- No prior receipt existed.
- The payload was byte-identical to the approved bundle.
- The identity gate passed.
- The unrelated-resource baseline `ae1f1d999d90a549` matched. For GEO, only the resources in the EMER receipt were excluded.

Nothing else was written. Receipts: `clients/ambient-cooling-heating/receipts/AMB-1002-*-CREATE-1-EXECUTED.json`.

## 1. Emergency Heating Repair

- **State:** ad group `204129717047` ENABLED. Both new RSAs are PAUSED and **under Google review** (`REVIEW_IN_PROGRESS`). The 6 keywords are PAUSED.
- **Dispatch:** owner-confirmed (business hours, next available visit), recorded in the work order.
- **Enable plan `AMB-1002-EMER-ENABLE-1` · `BFBD1315E210` · 10 operations:**
  - Enable the 2 RSAs.
  - Enable the 6 keywords: EXACT `emergency furnace repair`, EXACT `emergency heat repair`, PHRASE `emergency heater repair`, PHRASE + EXACT `emergency heating repair`, PHRASE `emergency furnace repair`.
  - Remove labels WAITING_LP and WAITING_AVAILABILITY.
- **Gates (13/13 PASS):** create readback clean, dispatch recorded, $85 / $18 / Mon–Fri 08–16 / 75 locations / tablet −100% intact, no disapproval.
- **validate_only:** 10/10. Executor: `scripts/ambient_1002_emer_enable.py execute BFBD1315E210 10` (it re-checks every gate first).
- **Serving:** ads under review may be enabled; they serve once Google approves them, so no exact start time is promised.
- **Recorded effect:** Emergency competes for the repair campaign's shared $85 budget and traffic. From the enable timestamp, the repair comparison is **configuration optimization, not a pure $18-ceiling test**.

## 2. Geothermal Heat Pump

- **State:** ad group `204129719007` ENABLED with 5 keywords ENABLED. New RSAs are PAUSED and under review; the old main-site RSAs remain PAUSED. The stray sitelink is paused. The campaign stays `NOT_ELIGIBLE` until an ad is enabled.
- **Blocker 1:** the `/geothermal-heat-pump/` "Offer Ends in 00 DAY 00 HRS …" countdown was present at the last successful read (2026-10-02 00:05 ET).
- **Blocker 2:** from 07:04 ET the SiteGround host refuses TLS from Green Marketing's machine. Both Ambient domains fail the handshake here, while check-host.net nodes in Germany, Sweden and New York get HTTP 200, so **the site is up for customers**. The countdown therefore can't be re-verified from here.
- **Enable plan:** prepared as a draft (enable 2 RSAs, remove WAITING_LP), **not fingerprinted** until the countdown is gone. Paid scope is unchanged (repair excluded).

## 3. Status matrix

Full table: `2026-10-02-status-matrix.md`. 32 ad groups across the 8 enabled Search campaigns:

| Category | Ad groups | Why |
|---|---|---|
| Enabled and eligible (serving-capable) | 18 | Ads APPROVED, keywords ELIGIBLE, URL on an offer page, tablet −100%, Mon–Fri 08–16 |
| **Eligible but nearly silent** | Electric Furnace Repair (0 impr. ever), Gas Furnace Repair (38 in Sep, 0 since), No Heat Repair (2) | Every keyword ELIGIBLE with no low-volume flag; QS 0 = not enough data. Causes: thin local demand for those exact phrasings; Furnace Repair negates `gas`/`electric`, so only queries with those words route here; No Heat has only `no heat repair` enabled (`house has no heat`, `no heat service` deliberately left paused 09-24); the $18 ceiling (campaign `BIDDING_STRATEGY_LIMITED`). Not a technical block. Do not bulk-enable. |
| Pending | Emergency Heating Repair | New ads PAUSED and under review; keywords PAUSED until EMER-ENABLE |
| Held: genuine page or business blocker | Geothermal (countdown); Boiler Installation (WAITING_LP, D2 page swap); Boiler Maintenance, Heat Pump Maintenance, Ductless Heating Repair, Ductless Heating Installation, Furnace Maintenance, Furnace Tune-Up, Heating Maintenance, Heating Tune-Up, Heating System Inspection (owner budget deferral 2026-09-25, plus WAITING_LP / EVALUATE_DUCTLESS) | Every ad paused by plan; labels state the reason |
| Enabled, no servable ads | Commercial HVAC Installation (`199748801029`) | RSAs created paused 09-15; their enable plan was never approved. Campaign `24132507747` therefore cannot spend. |
| Paused | HVAC Installation (residential) | Paused 09-22 by the cooling pause |

**Disapprovals:** the "has ads disapproved" campaign flags come only from **paused** August ads (Consumer Finance) and do not affect serving.

## 4. Search terms, September 1–30 and October 1–2

- **Corpus:** 845 (campaign, ad group, query, keyword, match) rows; 664 distinct queries across 13 campaigns (4 paused cooling/legacy campaigns = history only).
- **Full table:** `2026-10-02-search-term-verdicts-appendix.md` (every row, every required field). CSV: `exports/search-term-verdicts-2026-10-02.csv`.

| Period | Account total | Visible queries | Hidden (Google withholds) |
|---|---|---|---|
| Sep 1–30 | 4,454 impr. / 101 clicks / $3,391.32 | 2,706 / 59 / $2,151.87 (63% of cost) | 42 clicks / $1,239.45 |
| Oct 1 | 257 / 11 / $230.46 | 147 / 5 / $122.23 | 6 clicks / $108.23 |
| Oct 2 | not served at read (incomplete day) | – | – |

- **Owner export reconciled:** 5 clicks / $122.23 / 5 campaigns match exactly. The API returns 67 distinct Oct 1 queries in 69 (query, keyword) rows against the export's 61 rows, which is a grouping difference.
- **Hidden spend** is reported separately and is **not** assumed to be irrelevant.

**Verdicts:** Keep 201 · Monitor 209 · EXACT candidate 99 rows (98 unique negatives) · Already covered 42 · Routing review 12 · Service confirmation 17 · History, paused campaigns 206 · History, campaign with no servable ads 59.

**Coverage:**
- 42 rows are blocked today, all by shared list `12249470554` (added 09-26 16:36). None served after it existed, so there is no exclusion failure.
- Over-length candidates: 0. Conflicts with positive keywords: 0.

## 5. Owner-flagged queries

| Query | Where (keyword, real type / relationship) | Sep · Oct | Intent | Verdict |
|---|---|---|---|---|
| gr9s800804bn | Install/Replace › Furnace Replacement (`furnace replacement` PHRASE / near-phrase) | – · 1/0/$0 | Goodman furnace model lookup | **EXACT** (24257819466) |
| aoh 36u3t24p | Heat Pump › HP Replacement (`heat pump replacement` PHRASE) | – · 1/0 | Fujitsu outdoor-unit model | **EXACT** (24268690038) |
| gszb403010 | HP Replacement | – · 1/0 | Goodman heat pump model | **EXACT** (24268690038) |
| w801t0754a17uhsnas | Furnace Replacement | – · 1/0 | furnace model | **EXACT** (24257819466) |
| 25sca530a003 | HP Replacement | – · 1/0 | AC condenser model | **EXACT** (24268690038) |
| 100k btu furnace | Furnace Replacement | – · 1/0 | capacity/product shopping | **EXACT** (24257819466) |
| 75000 btu gas furnace | Furnace Replacement | – · 1/0 | capacity/product shopping | **EXACT** (24257819466) |
| thermostat 701 | Thermostat › Thermostat Replacement (`thermostat replacement` PHRASE) | – · 1/0 | product/model | **EXACT** (24268690041) |
| 4pu49 | Thermostat Replacement | – · 1/0 | part number | **EXACT** (24268690041) |
| honest air mt airy | Repair › Heating Repair (`heating repair` PHRASE / near-phrase) | – · 1/0 | competitor, Mt. Airy | **EXACT** (24257819463) |
| coastal hvac annapolis | Heating Repair | 5/0 · 1/0 | competitor | **EXACT** (24257819463) |
| stivers hvac inc | Heating Repair | – · 2/0 | competitor | **EXACT** (24257819463) |
| 24 hour heating repair (+ `24 hour hvac repair near me`, `24 hour hvac service near me`) | Furnace Repair / Heating Repair | 4/0 · 1/0 | availability mismatch (Ambient: Mon–Fri 08–16) | **EXACT** (24257819463). Urgent no-heat searches stay protected. |
| hvac annapolis · hvac in annapolis · hvac glen burnie md · annapolis hvac companies | Heating Repair | 1–4 impr. each | local contractor, service unstated | **Monitor** |
| hvac companies near me | Heating Repair: 26/0 Sep · 10/1/$15.79 Oct. History: paused residential HVAC Installation group 199/9/$274.52 | | local contractor | **Monitor** |
| hvac contractor near me | Heating Repair 10/0. History: paused group 51/4/$122.79 | | local contractor | **Monitor** |
| google home thermostat setup | Thermostat › Smart Thermostat Installation | – · 2/0 | DIY setup | **EXACT** (24268690041) |
| nest thermostat installation wiring | Smart Thermostat Installation | – · 2/0 | DIY wiring (`nest thermostat installation` stays protected) | **EXACT** (24268690041) |
| replacement dometic thermostat | Thermostat Replacement (PHRASE relationship) | – · 3/0 | RV thermostat | **EXACT** (24268690041) |
| suntouch heated floor thermostat | Thermostat Replacement | – · 1/0 | floor-heat product | **EXACT** (24268690041) |
| boiler repair / boiler repair near me | Boiler › Boiler Repair (EXACT) + Gas Boiler Repair | 73/0 + 14/0 · 2/0 | buyer | **Keep** |
| residential boiler prices | Boiler Replacement (`new boiler cost` EXACT / near-exact) | – · 2/1/$42.20 | price research | **Keep** |
| how much is a new furnace installed | Furnace Replacement | – · 1/0 | installed-price research | **Keep** |
| how much is heat pump for house | HP Replacement | – · 1/1/$24.27 | price research | **Keep** |

**Why the local-HVAC queries are Monitor, not negated:**
- They show hiring intent for an HVAC company with the service unstated. In heating season that plausibly includes repair.
- No live campaign is built for generic contractor intent; the repair campaign is the closest fit.
- Zero verified leads is not proof: D6 and the untracked location-asset calls weaken measurement.
- **Trigger:** any single generic query that reaches **$100 with no verified paid lead** becomes an EXACT candidate at the next pass.

## 6. EXACT negatives (draft, separate bundle)

**`AMB-1002-NEG-EXACT-1` · `D6ABF60771C3` · 98 campaign-level EXACT negatives.** validate_only passed 98/98.

| Campaign | Count |
|---|---|
| Repair | 64 |
| Thermostat | 16 |
| Install/Replace | 9 |
| Heat Pump | 7 |
| Boiler | 1 |
| Geothermal | 1 |

- **By type:** 33 competitor, 20 AC-only, 18 model/part/capacity, 9 thermostat setup/product, 6 oil, 3 pellet stove, 3 availability (24-hour), 2 vehicle/RV, 3 informational, 1 floor-heat.
- **Spend:** observed spend on these queries, Sep–Oct: $92.84 (no savings forecast).
- **Scope:** campaign level; each query is unsuitable throughout its campaign. No Phrase or Broad negatives, no shared or account-level list edits, nothing removed.
- Apply promptly after approval. The executor time-stamps the intervention.

| # | Negative (EXACT) | Campaign | Bucket | Impr/clicks/cost Sep-Oct | Seen | Conf. |
|---|---|---|---|---|---|---|
| 1 | `[do plumbers do boilers]` | Boiler 24132507744 | info | 1/0/$0.00 | 09-24..09-24 | medium |
| 2 | `[booths hvac]` | Repair 24257819463 | competitor | 1/1/$39.15 | 09-28..09-28 | high |
| 3 | `[s f jones heating and cooling]` | Repair 24257819463 | competitor | 3/1/$23.70 | 09-28..09-28 | high |
| 4 | `[24 hour hvac repair near me]` | Repair 24257819463 | availability | 3/0/$0.00 | 09-29..09-29 | medium |
| 5 | `[a c repair near me]` | Repair 24257819463 | ac | 5/0/$0.00 | 09-29..09-29 | high |
| 6 | `[ac service and repair near me]` | Repair 24257819463 | ac | 3/0/$0.00 | 09-29..09-29 | high |
| 7 | `[ac service near me]` | Repair 24257819463 | ac | 4/0/$0.00 | 09-29..10-01 | high |
| 8 | `[air conditioner repair near me]` | Repair 24257819463 | ac | 6/0/$0.00 | 09-29..09-29 | high |
| 9 | `[air conditioning service near me]` | Repair 24257819463 | ac | 4/0/$0.00 | 09-29..09-29 | high |
| 10 | `[air conditioning servicing near me]` | Repair 24257819463 | ac | 4/0/$0.00 | 09-29..09-29 | high |
| 11 | `[carroll mechanical columbia md]` | Repair 24257819463 | competitor | 4/0/$0.00 | 09-30..09-30 | high |
| 12 | `[coastal hvac annapolis]` | Repair 24257819463 | competitor | 6/0/$0.00 | 09-25..10-01 | high |
| 13 | `[dodge heating and air]` | Repair 24257819463 | competitor | 7/0/$0.00 | 09-25..09-29 | high |
| 14 | `[fix air conditioning near me]` | Repair 24257819463 | ac | 3/0/$0.00 | 09-29..09-29 | high |
| 15 | `[max air heating & a c inc]` | Repair 24257819463 | competitor | 6/0/$0.00 | 09-25..09-25 | high |
| 16 | `[moon air elkton]` | Repair 24257819463 | competitor | 8/0/$0.00 | 09-28..09-28 | high |
| 17 | `[pellet stove repair in my area]` | Repair 24257819463 | pellet_stove | 3/0/$0.00 | 09-25..09-25 | high |
| 18 | `[pellet stove repair near me]` | Repair 24257819463 | pellet_stove | 5/0/$0.00 | 09-23..09-29 | high |
| 19 | `[repair air conditioner near me]` | Repair 24257819463 | ac | 7/0/$0.00 | 09-29..09-29 | high |
| 20 | `[repair air conditioning near me]` | Repair 24257819463 | ac | 4/0/$0.00 | 09-29..09-29 | high |
| 21 | `[webasto heater repair near me]` | Repair 24257819463 | vehicle | 4/0/$0.00 | 09-30..09-30 | high |
| 22 | `[24 hour heating repair]` | Repair 24257819463 | availability | 1/0/$0.00 | 10-01..10-01 | medium |
| 23 | `[24 hour hvac service near me]` | Repair 24257819463 | availability | 1/0/$0.00 | 09-29..09-29 | medium |
| 24 | `[ac unit repair near me]` | Repair 24257819463 | ac | 2/0/$0.00 | 09-29..09-29 | high |
| 25 | `[air conditioner repair annapolis]` | Repair 24257819463 | ac | 1/0/$0.00 | 09-29..09-29 | high |
| 26 | `[air conditioner repair company]` | Repair 24257819463 | ac | 1/0/$0.00 | 10-01..10-01 | high |
| 27 | `[air conditioner service near me]` | Repair 24257819463 | ac | 2/0/$0.00 | 09-29..09-29 | high |
| 28 | `[air conditioner servicing near me]` | Repair 24257819463 | ac | 1/0/$0.00 | 09-29..09-29 | high |
| 29 | `[allpro hvac]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-28..09-28 | high |
| 30 | `[b&d hvac]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-30..09-30 | high |
| 31 | `[bnb heating and cooling]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-25..09-25 | high |
| 32 | `[coastal heat and air]` | Repair 24257819463 | competitor | 1/0/$0.00 | 10-01..10-01 | high |
| 33 | `[cold comfort hvac rockville md]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-29..09-29 | high |
| 34 | `[commercial air conditioner repair]` | Repair 24257819463 | ac | 1/0/$0.00 | 09-29..09-29 | high |
| 35 | `[energylogic waste oil heater service]` | Repair 24257819463 | oil | 1/0/$0.00 | 09-28..09-28 | high |
| 36 | `[falcon hvac]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-30..09-30 | high |
| 37 | `[fix air conditioner near me]` | Repair 24257819463 | ac | 2/0/$0.00 | 09-29..09-29 | high |
| 38 | `[frosty heating and air conditioning]` | Repair 24257819463 | competitor | 1/0/$0.00 | 10-01..10-01 | high |
| 39 | `[go ecco climate control]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-29..09-29 | high |
| 40 | `[grove hvac maryland]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-28..09-28 | high |
| 41 | `[harbor point heating and air]` | Repair 24257819463 | competitor | 1/0/$0.00 | 10-01..10-01 | high |
| 42 | `[heating oil furnace service]` | Repair 24257819463 | oil | 2/0/$0.00 | 09-29..09-29 | high |
| 43 | `[home air conditioner repair]` | Repair 24257819463 | ac | 2/0/$0.00 | 09-29..09-29 | high |
| 44 | `[home air conditioner repair near me]` | Repair 24257819463 | ac | 2/0/$0.00 | 09-29..09-29 | high |
| 45 | `[home team heating and cooling]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-29..09-29 | high |
| 46 | `[honest air mt airy]` | Repair 24257819463 | competitor | 1/0/$0.00 | 10-01..10-01 | high |
| 47 | `[hope plumbing heating and cooling]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-30..09-30 | high |
| 48 | `[howard mechanical hvac]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-29..09-29 | high |
| 49 | `[jiffy hvac]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-29..09-29 | high |
| 50 | `[joey taylor hvac]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-30..09-30 | high |
| 51 | `[maryland mechanical heating & cooling]` | Repair 24257819463 | competitor | 2/0/$0.00 | 10-01..10-01 | high |
| 52 | `[ocean air hvac]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-30..09-30 | high |
| 53 | `[oil burner service near me]` | Repair 24257819463 | oil | 1/0/$0.00 | 09-29..09-29 | high |
| 54 | `[oil furnace cleaning service near me]` | Repair 24257819463 | oil | 2/0/$0.00 | 09-30..09-30 | high |
| 55 | `[oil furnace companies near me]` | Repair 24257819463 | oil | 1/0/$0.00 | 09-25..09-25 | high |
| 56 | `[oil heater service]` | Repair 24257819463 | oil | 1/0/$0.00 | 09-28..09-28 | high |
| 57 | `[pellet stove service near me]` | Repair 24257819463 | pellet_stove | 1/0/$0.00 | 09-29..09-29 | high |
| 58 | `[powell and turner hvac]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-25..09-25 | high |
| 59 | `[smock heating & air]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-28..09-28 | high |
| 60 | `[southern maryland heating and air waldorf md]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-29..09-29 | high |
| 61 | `[stanton hvac]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-28..09-28 | high |
| 62 | `[stivers hvac inc]` | Repair 24257819463 | competitor | 2/0/$0.00 | 10-01..10-01 | high |
| 63 | `[triple eee hvac]` | Repair 24257819463 | competitor | 2/0/$0.00 | 09-30..09-30 | high |
| 64 | `[vito hvac]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-29..09-29 | high |
| 65 | `[xzavier hvac solutions llc baltimore reviews]` | Repair 24257819463 | competitor | 1/0/$0.00 | 09-28..09-28 | high |
| 66 | `[gd9s800804bn]` | Install/Replace 24257819466 | model | 4/0/$0.00 | 09-29..09-29 | medium |
| 67 | `[r801ca100521msa]` | Install/Replace 24257819466 | model | 4/0/$0.00 | 09-29..09-29 | medium |
| 68 | `[100k btu furnace]` | Install/Replace 24257819466 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 69 | `[75000 btu gas furnace]` | Install/Replace 24257819466 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 70 | `[80 000 btu gas furnace]` | Install/Replace 24257819466 | model | 2/0/$0.00 | 09-29..09-29 | medium |
| 71 | `[central air installation near me]` | Install/Replace 24257819466 | ac | 1/0/$0.00 | 09-29..09-29 | high |
| 72 | `[gr9s800804bn]` | Install/Replace 24257819466 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 73 | `[how much does it cost to get central air installed]` | Install/Replace 24257819466 | ac | 2/0/$0.00 | 09-24..09-24 | medium |
| 74 | `[w801t0754a17uhsnas]` | Install/Replace 24257819466 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 75 | `[25sca530a003]` | Heat Pump 24268690038 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 76 | `[aoh 36u3t24p]` | Heat Pump 24268690038 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 77 | `[bova36hdn1m20g]` | Heat Pump 24268690038 | model | 1/0/$0.00 | 09-28..09-28 | medium |
| 78 | `[bova36rtbm20s]` | Heat Pump 24268690038 | model | 1/0/$0.00 | 09-28..09-28 | medium |
| 79 | `[gszb403010]` | Heat Pump 24268690038 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 80 | `[ml14kp1 024]` | Heat Pump 24268690038 | model | 2/0/$0.00 | 09-29..09-29 | medium |
| 81 | `[rd18ay36ajvca]` | Heat Pump 24268690038 | model | 1/0/$0.00 | 09-28..09-28 | medium |
| 82 | `[vivint thermostat programming]` | Thermostat 24268690041 | thermostat_diy | 2/1/$16.13 | 09-30..09-30 | high |
| 83 | `[single stage thermostat]` | Thermostat 24268690041 | thermostat_diy | 4/1/$13.86 | 09-30..09-30 | medium |
| 84 | `[honeywell focus pro s200 wifi setup]` | Thermostat 24268690041 | thermostat_diy | 4/0/$0.00 | 09-29..09-29 | high |
| 85 | `[replacement dometic thermostat]` | Thermostat 24268690041 | vehicle | 3/0/$0.00 | 10-01..10-01 | high |
| 86 | `[4pu49]` | Thermostat 24268690041 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 87 | `[5184570aj]` | Thermostat 24268690041 | model | 1/0/$0.00 | 09-30..09-30 | medium |
| 88 | `[7 day programmable thermostat]` | Thermostat 24268690041 | thermostat_diy | 1/0/$0.00 | 09-30..09-30 | medium |
| 89 | `[91873]` | Thermostat 24268690041 | model | 2/0/$0.00 | 09-30..09-30 | medium |
| 90 | `[aube thermostat]` | Thermostat 24268690041 | thermostat_diy | 2/0/$0.00 | 10-01..10-01 | medium |
| 91 | `[can i change a thermostat myself]` | Thermostat 24268690041 | info | 1/0/$0.00 | 09-30..09-30 | medium |
| 92 | `[google home thermostat setup]` | Thermostat 24268690041 | thermostat_diy | 2/0/$0.00 | 10-01..10-01 | high |
| 93 | `[installing a programmable thermostat]` | Thermostat 24268690041 | thermostat_diy | 1/0/$0.00 | 09-29..09-29 | medium |
| 94 | `[nest thermostat installation wiring]` | Thermostat 24268690041 | thermostat_diy | 2/0/$0.00 | 10-01..10-01 | high |
| 95 | `[round non programmable thermostat with 1h single stage heating]` | Thermostat 24268690041 | thermostat_diy | 1/0/$0.00 | 09-30..09-30 | high |
| 96 | `[suntouch heated floor thermostat]` | Thermostat 24268690041 | floor_heat | 1/0/$0.00 | 10-01..10-01 | high |
| 97 | `[thermostat 701]` | Thermostat 24268690041 | model | 1/0/$0.00 | 10-01..10-01 | medium |
| 98 | `[what is geothermal heating]` | Geothermal 24274160783 | info | 2/0/$0.00 | 09-24..09-24 | medium |

**Hypothetical, review only:** 25 predicted queries, no metrics (`exports/hypothetical-negatives-2026-10-02.json`).
- **Already blocked:** `ecobee thermostat setup`, `nest thermostat wiring diagram`, `rv thermostat replacement`, `goodman furnace model numbers`.
- **Not recommended:** `furnace error code 33` (hire risk).
- **Uncovered, candidates for a later pass:** `webasto heater repair`, `diesel heater repair`, `pellet stove repair`, `pellet stove service`, `oil furnace repair`, `oil furnace repair near me`, `oil burner repair`, `oil heater repair`, `air conditioner repair`, `ac unit repair`, `fix air conditioner`, `24 hour furnace repair`, `24 hour heating service`, `honeywell thermostat wiring`, `heated floor thermostat`, `programmable thermostat`, `100000 btu gas furnace`, `60000 btu furnace`, `heat pump model number lookup`, `buy furnace control board`.
- EXACT negatives never cover longer, reordered, plural or synonym variants. Google applies negatives to casing and misspellings only.

**Existing over-blocking (reported, not changed):** the account-level BROAD list blocks `carrier`, `trane`, `lennox`, `goodman`, `rheem`, `bryant`, `american`, `amana`, `ruud`, `armstrong`, `bosch`, `daikin`, `mitsubishi`, `frigidaire`, `ecobee`, plus the generic tokens `al` and `mr`.
- No approved record lists which brands Ambient services. The only site wording on file is "all makes and models" on an AC repair page.
- So **no removal is proposed until the owner confirms brands** (question 1).
- `ecobee` also blocks the approved Smart Thermostat Installation service.

## 7. Tablets

- **Search:** all 8 enabled campaigns have the TABLET criterion set to −100% (`bid_modifier` explicitly 0). There were **0 tablet impressions on Oct 1**, and tablet cost since 09-24 is $0.00. No Search device correction is needed, so none is proposed.
- **PMax:** the shell `24295088845` TABLET criterion is **unset**; AMB-1002-PMAX-A-1 sets it to 0. The new campaign B is created with TABLET at 0.
- Both were accepted by Google validate_only, which confirms the native PMax device control works through the API. Readback is in each executor.

## 8. Budgets

The eight Search campaigns, as requested: $1,000/month each.

| Campaign (ID) | Budget ID | Now | Oct 1 spend | Oct remaining | **Oct budget** (from Oct 2) | Δ | Oct limit | **From Nov 1** | Δ vs now |
|---|---|---|---|---|---|---|---|---|---|
| Boiler Services 24132507744 | 15787409438 | $45.00 | $42.20 | $957.80 | **$31.92** | −29% | $999.80 | **$32.89** | −27% |
| Geothermal 24274160783 | 15887323571 | $20.00 | $0 | $1,000 | **$33.33** | +67% | $999.90 | **$32.89** | +64% |
| HVAC Installation (Commercial) 24132507747 | 15787409441 | $20.00 | $0 | $1,000 | **$33.33** | +67% | $999.90 | **$32.89** | +64% |
| Heat Pump & Ductless 24268690038 | 15887323562 | $15.00 | $24.27 | $975.73 | **$32.52** | +117% | $999.87 | **$32.89** | +119% |
| Heating & Furnace Install & Replace 24257819466 | 15885327975 | $60.00 | $92.18 | $907.82 | **$30.26** | −50% | $999.98 | **$32.89** | −45% |
| Heating & Furnace Repair 24257819463 | 15885327972 | $85.00 | $47.04 | $952.96 | **$31.76** | −63% | $999.84 | **$32.89** | −61% |
| Heating Maintenance & Inspection 24279798229 | 15887323565 | $45.00 | $0 | $1,000 | **$33.33** | −26% | $999.90 | **$32.89** | −27% |
| Thermostat Services 24268690041 | 15887323568 | $15.00 | $24.77 | $975.23 | **$32.50** | +117% | $999.77 | **$32.89** | +119% |
| **Total** | all non-shared (1 campaign each) | **$305.00/day** | $230.46 | | **$258.95/day** | | $7,998.96 | **$263.12/day** | |

**Math:**
- Google's rule after a mid-month change: limit = spend so far + new daily budget × calendar days left, with the change day counted ([Google help](https://support.google.com/google-ads/answer/10487143?hl=en)). Oct 2–31 = 30 days, and amounts are rounded **down** to the cent.
- Setting $32.89 today would instead give Repair a $1,033.74 October limit.
- **Steady state:** $1,000 / 30.4 = $32.894…, so $32.89 → $999.86 a month. 8 Search = $263.12/day ($7,998.85/month). 2 PMax = $65.78/day ($1,999.71). **Total $328.90/day ($9,998.56).** That is inside the $328.94 hard daily cap.
- Daily spend can reach 2× the budget; the monthly limit still holds.
- **Plans:** `AMB-1002-BUD-OCT-1` · `A1B9032D7D60` · 8 ops, valid **only if executed 2026-10-02**. The executor refuses if any October limit would pass $1,000.50. `AMB-1101-BUD-NOV-1` · `39B1E83A72B0` · 8 ops, execute on or after 2026-11-01. validate_only 8/8 each. The $18 repair ceiling and every other setting are untouched.

**Projected October Search spend: about $3,000–4,000, not $8,000.** The campaigns below are listed by expected outcome:

| Campaign | Expected October | Why |
|---|---|---|
| Boiler | ~$800–958 | Recent ~$70 per serving day, so likely budget-limited |
| Install/Replace | ~$800–908 | ~$66 per serving day, so budget-limited |
| Repair | ~$700–953 | $47 on day 1 at $18, plus Emergency |
| Heat Pump | ~$300–600 | Little demand |
| Thermostat | ~$150–400 | Little demand |
| Geothermal | ~$50–250 | Once enabled |
| **Commercial HVAC Installation** | **$0** | No enabled ads |
| **Maintenance** | **$0** | Ads paused |

**Equal allocation leaves money idle and cuts the earners:**
- About $2,000/month of the equal allocation sits in campaigns that cannot spend (Commercial, Maintenance), and Geothermal, Heat Pump and Thermostat have little demand.
- Meanwhile the cut lands on Install/Replace (−50%) and Boiler (−29%). Those are the highest-ticket Search services, and both September click-ID-verified paid leads came from them.
- Repair drops 63%. At the $18 ceiling its day-1 spend was $47, so it becomes budget-limited by mid-to-late October.
- This is flagged, not reallocated (question 2).

## 9. Two Performance Max campaigns

**How services were chosen (owner instruction):** by the per-job revenue heating companies typically earn, limited to services Ambient offers. The approximate ranges in the table come from current published installed-price guides:

| Service | Typical installed price | Sources |
|---|---|---|
| Geothermal heat pump | $15k–$45k | [Angi](https://www.angi.com/articles/geothermal-heating-and-cooling-cost.htm), [Fixr](https://www.fixr.com/costs/geothermal-heat-installation), [Carrier](https://www.carrier.com/residential/en/us/products/geothermal-heat-pumps/cost-buying-geothermal-heat-pump/) |
| Air-source heat pump install/replace | $4k–$14k | [ConsumerAffairs](https://www.consumeraffairs.com/homeowners/heat-pump-installation-cost.html) |
| Boiler replacement | $3.5k–$8.5k (~$6.1k avg) | [This Old House](https://www.thisoldhouse.com/heating-cooling/boiler-replacement-cost), [HomeGuide](https://homeguide.com/costs/boiler-replacement-cost) |
| Gas furnace replacement | $3.5k–$9k | [hvacprojectcost](https://hvacprojectcost.com/furnace-replacement-cost/) |
| Furnace repair | $125–$500 | [Angi](https://www.angi.com/articles/how-much-does-common-furnace-repair-cost.htm) |
| Tune-up | $70–$200 | [HomeGuide](https://homeguide.com/costs/furnace-inspection-cost) |

- Repair and maintenance are excluded from PMax.
- Ductless installation is excluded: it is held with no page.
- Price = revenue per job. **Ambient's margin and close rate are unknown**, so nothing is labelled "most profitable".

**PMax B: Heat Pump & Geothermal (highest ticket)**
- **Plan:** `AMB-1002-PMAX-B-1` · `F4D888845B8E` · 215 ops, validate_only OK. New campaign, created PAUSED.
- **Budget:** $32.89, non-shared. **Bidding:** Max Conversions, no tCPA (too little conversion data for a target).
- **Targeting:** 75 Presence locations, English, Mon–Fri 08–16, tablet excluded.
- **Automation:** 6 opt-outs, including Final URL expansion and text customization. Brand guidelines on (business name and logos).
- **Assets:** call `410-415-9517`, snippet, 4 offer-page sitelinks, 8 callouts.
- **Negatives:** 5 own-brand EXACT negatives; the two heating shared negative lists attached (contents unchanged).
- **Asset groups (PAUSED):**
  - **Heat Pump Replacement** → `/heat-pump-replacement/`: 36 existing approved assets plus 8 search themes.
  - **Heat Pump Installation** → `/heat-pump-installation/`: 15 headlines (8 reused), 5 long headlines, 5 descriptions, heat-pump page images, 10 search themes.
  - Both groups get the "All Converters" audience signal `360614515`.
- **Geothermal asset group:** held payload only, until the countdown is removed and approved geothermal images exist.
- **After create:** the call-from-ads goal is set not biddable, mirroring A, to avoid the call double count.

**PMax A: Furnace & Boiler Replacement**
- **Plan:** `AMB-1002-PMAX-A-1` · `02556803100C` · 64 ops, validate_only OK. Reuses shell `24295088845`, which stays PAUSED.
- **Changes:**
  - Rename to "PMax | Furnace & Boiler Replacement | Central MD | 2026-10 | HELD".
  - Budget $20 → $32.89.
  - Tablet −100%.
  - New PAUSED group **Boiler Replacement** → `/boiler-replacement/`, using the boiler-replacement page images, 10 search themes and the audience signal.
- **Kept:** Heating & Furnace Replacement (→ `/hvac-replacement/`). The shell's Heat Pump Replacement group stays paused permanently, so the portfolios don't overlap.
- **Copy rules (both):** all copy uses verified facts only (free quote, Mon–Fri 8–4, service area). Nothing about 24/7, same-day, price, financing, licences, ratings or "best".
- **Caveats:**
  - Search themes and audiences are signals, not boundaries. PMax will not serve only bottom-of-funnel searches, and asset groups cannot hold separate budgets.
  - A Search exact keyword that matches the query wins over PMax; otherwise ad rank decides.

**Launch blockers for both PMax campaigns** (enable plans will be fingerprinted after create readback):
1. **D6 is open.** PMax bids on form leads it can't reliably record.
2. The WhatConverts "WC Lead" upload also carries leads without a click ID (enhanced conversions), which can teach Max Conversions the wrong signal.
3. Location-asset calls reach an untracked number.
4. Thin data: 2 click-ID-verified paid leads in September.

**Monitoring:** manual. The monitor is **NOT ACTIVE**. Review each PMax at $300 spend, using the zero-lead rule min($300, $350 − 2 × $32.89).

## 10. Economic evidence and missing inputs

- **Verified, Sep 1–Oct 1:** 2 click-ID paid leads, both on 09-28: a Boiler Replacement form and a Furnace Replacement call. Qualified: unknown (Quotable Not Set).
- **Heating program to date:** $1,888.22 / 74 clicks / 2 verified leads = **$944 CPL**, above the $350 ceiling.
- **Repair campaign:** $686.15 / 26 clicks / 0 verified leads.
- **Missing:** sold jobs, revenue, gross margin, close rate, CRM outcomes. CPQL and ROAS can't be calculated.

## 11. Measurement and developer gaps

**Phones:**
- **Unchanged:** 705-6354 (paid pages), 914-1456 (all-traffic DNI pool), 415-9517 (heating call asset, never used), 761-0932 (destination).
- **Only two Google call records** on the repair campaign since 09-17:
  - 09-25, 52 s: location asset.
  - 09-30, 60 s: CALLS click on `hvac near me`.
  - Neither matched a WhatConverts record, because the repair campaign's call assets are paused and location calls go to a Business Profile phone WhatConverts doesn't track.
- **Probable but unverified:** WhatConverts lead 260999389 (09-30, DNI, 130 s).
- **No new paid leads on Oct 1.**
- **Business Profile phone overrides** for the 3 locations still need a manual check; the API can't read them.

**Developer fixes**, page facts as of the last successful read at 00:05 ET (in priority order):
1. **D6:** Gravity Forms form 1, field 7 "Tell us about your project" is marked Required while the label says "(optional)". Turn Required off (preferred) or drop "(optional)". It is on every offer page.
2. **Geothermal page:** remove the "Offer Ends in" countdown module.
3. **Emergency page:** replace "Different AC problems … AC repair diagnosis …" with heating wording.
4. **D5:** render one form per page; 3 × `#gform_1` gives 55 duplicate IDs. Tell Green Marketing before changing form IDs (WhatConverts allowlist).
5. **D1:** remove 410-761-0932 from the server HTML (4× on emergency, 2× on geothermal).
6. **D7:** populate the attribution fields client-side, or exclude the form pages from the full-page cache. It was not reproduced, and isn't proven fixed.
7. **Site access:** SiteGround is refusing TLS from Green Marketing's IP since at least 07:04 ET. Check the blocked-IP log and whitelist the agency IP.

No test leads, calls or tracking changes were made.

## 12. Approvals (each is its own bundle; none reuses another's approval)

| Bundle | Fingerprint | Ops | Line |
|---|---|---|---|
| Emergency enable | BFBD1315E210 | 10 | `APPROVE AMB-1002-EMER-ENABLE-1 BFBD1315E210 10 operations FOR 2401959466` |
| EXACT negatives | D6ABF60771C3 | 98 | `APPROVE AMB-1002-NEG-EXACT-1 D6ABF60771C3 98 operations FOR 2401959466` |
| October budgets (Oct 2 only) | A1B9032D7D60 | 8 | `APPROVE AMB-1002-BUD-OCT-1 A1B9032D7D60 8 operations FOR 2401959466` |
| November budgets (≥ Nov 1) | 39B1E83A72B0 | 8 | `APPROVE AMB-1101-BUD-NOV-1 39B1E83A72B0 8 operations FOR 2401959466` |
| PMax A build (paused) | 02556803100C | 64 | `APPROVE AMB-1002-PMAX-A-1 02556803100C 64 operations FOR 2401959466` |
| PMax B build (paused) | F4D888845B8E | 215 | `APPROVE AMB-1002-PMAX-B-1 F4D888845B8E 215 operations FOR 2401959466` |

- **Search device corrections:** none needed.
- **Geothermal enable:** held for the countdown.
- **PMax enable:** comes after the build readback.
