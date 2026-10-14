# Ambient: search terms, Heating Repair, and the Emergency + Geothermal page launch (2026-10-01/02)

**Account:** `Ambient Cooling - Live` · child `2401959466` (not MCC 3373711342) · Ambient Cooling & Heating LLC · heating-cooling
**Mode:** READ + DRAFT. **External writes: 0.** Only Google's `validate_only` check ran (6 operations, writes nothing).
**Read times:** API snapshot 2026-10-01 18:12 ET, refreshed 2026-10-02 00:08 ET (account clock: yesterday = 2026-10-01).
Chrome page QA 2026-10-01 23:50 – 2026-10-02 00:05 ET. Account time zone America/New_York.

## 1. Primary recommendation

1. **Leave the $18 test alone through Wed Oct 7 and read it on Oct 8.** Day 1 (Oct 1, complete): 3 clicks, $47.04, avg CPC
   **$15.68** (baseline $27.79). One day of 3 clicks proves nothing yet.
2. **Heating Repair Phrase: clean up and monitor** (section 8). It is 90% of the campaign's spend and 418 of its 421 visible
   impressions are Google "same-meaning" matches, but pausing it would effectively stop repair delivery, which the owner ruled out.
3. **Approve the two create-paused plans now** (section 10). Neither one changes delivery.
   - **Geothermal can go live** once the countdown is gone and the ads are approved.
   - **Emergency waits** for one operational answer: will Ambient book an urgent no-heat visit during business hours?
4. **The negatives (62 EXACT) are a separate, later plan**, best applied Oct 8 after the test read. They save little money
   ($62.85 of past spend). The real leak is semantic Phrase matching, and EXACT negatives cannot keep up with it.
5. **Developer: D6 is the top fix.** The form's message field says "(optional)" but is configured *required* on every offer
   page, including both new ones.

## 2. Gates

| Check | Result |
|---|---|
| Work orders (repo validator `scripts/validate_work_order.py`) | **PASS ×3**: `work-order-heating-repair-search-terms-2026-10-01.yaml` (Heating Repair, read), `work-order-emergency-heating-repair-lp-2026-10-01.yaml` (Emergency Heating Repair, draft), `work-order-geothermal-heat-pump-lp-2026-10-01.yaml` (Geothermal Heat Pump, draft). All 14 earlier Ambient work orders still pass. |
| Client profile edit | `client.yaml` `offer.services_in_scope` += Emergency Heating Repair, Geothermal Heat Pump. Both were already in the owner's 2026-09-21 advertising scope and not in `services_capability_not_verified`. This is the same basis as the 2026-09-30 maintenance additions. Emergency *availability* stays a barred claim. Without the edit the validator rejects both work orders. |
| Fresh identity (API, re-run at the start of every script) | **8/8 PASS** each run: name `Ambient Cooling - Live`, id `2401959466`, not manager, not test, America/New_York, USD, Green Marketing 3373711342 ACTIVE, ClickCease 2815082755 ACTIVE. |
| Historical claims verified | Repair campaign **24257819463** ✓ · ceiling $42→**$18** at **2026-09-30 17:52:03 ET** (change_event, API client) ✓ · Sept 30 last served hour 15:00–16:00, so **Sept 30 = old-$42 traffic** ✓ · budget **$85** ✓ · Search only (Partners and Display off, AI Max off) ✓ · Mon–Fri **08:00–16:00**, 5 rows ✓ · **75** PRESENCE targets ✓ · five serving groups ✓ · Emergency group with **0 ads**, but it has **5 PAUSED keywords** (the "no keywords" report was wrong) ✓ · Heating Repair Phrase **$406.12 / 15 clicks / 0 verified leads, Sept 17–29** ✓ exact. |
| Drift since 2026-09-30 | **One UI edit:** 2026-10-01 14:08:48–14:09:53 ET, web client, TABLET device criterion on 9 campaigns (both in-scope campaigns included). Tablets now **−100% on all 8 enabled campaigns**. change_event carried no before/after values. Baseline tablet share was 12 impressions and 0 clicks, so the effect on the test is negligible, but it is a mid-day-1 change. Nothing else changed. |

## 3. Coverage and missing sources

- **Inventory:** 30 non-removed campaigns and 98 ad groups. 8 campaigns are ENABLED ($305.00/day).
- **Audited:** 24257819463 Heating & Furnace Repair (6 ad groups) and 24274160783 Geothermal Heat Pump (1 ad group).
- **Read only for routing** (keywords, negatives, statuses; **not audited**): the other 6 enabled heating/commercial campaigns.
- **Outside this work order:** the other 22 campaigns, all PAUSED (legacy, cooling, PMax shells).

| In-scope ad group | ID | Status / labels | Ads | Keywords | Baseline 09-24..30 |
|---|---|---|---|---|---|
| Heating Repair | 204129717007 | ENABLED, CORE_ACTIVE | 2 enabled → `/hvac-repair/` (+2 paused main-site) | 6 enabled (2 P, 4 E) | 1,010 impr · 21 clk · $575.33 |
| Furnace Repair | 199797580706 | ENABLED, CORE_ACTIVE | 2 → `/furnace-repair/` (+2 paused) | 8 enabled | 182 · 2 · $63.78 |
| Gas Furnace Repair | 204129717247 | ENABLED, CORE_ACTIVE | 2 → `/furnace-repair/` | 2 | 38 · 0 · $0 |
| Electric Furnace Repair | 204129717287 | ENABLED, CORE_ACTIVE | 2 → `/furnace-repair/` | 2 | 0 |
| No Heat Repair | 204129717087 | ENABLED, CORE_ACTIVE | 2 → `/no-heat-repair/` | 2 enabled, 2 paused | 2 · 0 · $0 |
| Emergency Heating Repair | 204129717047 | ENABLED, WAITING_LP + WAITING_AVAILABILITY | **0** | 5 **PAUSED** | 0 |
| Geothermal Heat Pump | 204129719007 | ENABLED, GEOTHERMAL_TEST + WAITING_LP | 2 **PAUSED** → main-site `/services/hvac/geothermal-hvac/` | 5 enabled | 22 · 2 · $38.25 (09-24 only) |

- **URLs:** no tracking template or final URL suffix exists at campaign, ad group, ad or keyword level. There are no keyword URL overrides and no mobile URLs. The account-level ClickCease template is recorded in `client.yaml`.
- **Conversions:** Primary = Calls from ads `1068114183`, WC Calls `7643656075`, WC Lead `7643656486` (plus non-biddable GBP actions). The native form action is Secondary. Unchanged.
- **Missing or unreadable sources:**
  - Search-term visibility: **58% of baseline cost ($368.68) and 13 of 23 clicks have no visible query.** Google withholds them; nothing is inferred.
  - Oct 1 impression share isn't reported yet.
  - Auction Insights needs UI export (token tier).
  - The Business Profile "Google Ads phone" override isn't exposed by the API.
  - There are no CRM, sold-job, revenue or margin data.
  - WhatConverts Quotable is "Not Set" on recent leads.
  - No form submission or test call was made (section 9).

## 4. Search-term verdicts

- **Corpus:** 270 (ad group, query, keyword, match) rows, 246 distinct queries. Only 4 ad groups had visible terms (Heating Repair, Furnace Repair, Gas Furnace Repair, Geothermal). No reporting filter was applied: zero-click and below-100-impression rows are included.
- **Full table:** `reports/ambient-cooling-heating/2026-10-01-search-term-verdicts-appendix.md` (every row, all fields). CSV: `clients/ambient-cooling-heating/exports/search-term-verdicts-2026-10-01.csv`.
- **Raw queries appear in these files** because this request required the actual full query.

**Repair campaign, visible baseline (09-24..30) by intent:**

| Intent | Terms | Impr | Clicks | Cost |
|---|---|---|---|---|
| Ambiguous (generic HVAC company / near me / places) | 94 | 260 | 4 | $86.37 |
| Clearly irrelevant (other companies, vehicle heater) | 41 | 94 | 3 | $91.43 |
| No-heat repair | 5 | 7 | 2 | $63.78 |
| Other equipment (AC, fireplace, pellet stove, duct, water heater) | 41 | 119 | 1 | $28.85 |
| Furnace repair | 30 | 98 | 0 | $0 |
| Direct heating repair | 10 | 14 | 0 | $0 |
| Informational / DIY | 8 | 12 | 0 | $0 |
| Emergency (24-hour) | 2 | 4 | 0 | $0 |
| **Visible total** | | **608 of 1,232** | **10 of 23** | **$270.43 of $639.11** |

**Every query that cost money, Sept 17–Oct 1** (verified paid leads 0 on every row):

| Query | Ad group / keyword (real type) | Relationship | Impr / clk / cost | Outcome | Intent | Verdict |
|---|---|---|---|---|---|---|
| hvac glen burnie | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 3 / 2 / $54.83 | 3 GBP local actions (directions, engagement). A 52 s Google call on 09-25 with no WhatConverts record | Ambiguous: local HVAC company | Keep |
| booths hvac | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 1 / 1 / $39.15 | none | Clearly irrelevant: another company | **EXACT candidate** |
| heat not working but ac is | Furnace Repair / furnace not working (PHRASE) | NEAR_PHRASE | 2 / 1 / $35.68 | none | No-heat repair | Keep |
| heat n glo fireplace service near me | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 4 / 1 / $28.85 | none | Other equipment (fireplace) | Keep excluded: already covered (`fireplace` PHRASE, added 09-26, after it served on 09-25) |
| tevis modern comfort | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 8 / 1 / $28.58 | none | Clearly irrelevant | Keep excluded: covered since 09-26 |
| heating not working | Furnace Repair / furnace not working (PHRASE) | NEAR_EXACT | 2 / 1 / $28.10 | none | No-heat repair | Keep |
| s f jones heating and cooling | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 3 / 1 / $23.70 | none | Clearly irrelevant | **EXACT candidate** |
| geo heating | Geothermal / geothermal heating (PHRASE) | NEAR_EXACT | 3 / 1 / $19.94 | none | Ambiguous | Keep excluded (covered) |
| hvac contractors near me | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 13 / 1 / $16.36 | none | Ambiguous | Keep |
| hvac solutions near me (10-01) | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 1 / 1 / $16.21 | none | Ambiguous | Keep |
| hvac companies near me (10-01) | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 36 / 1 / $15.79 | none | Ambiguous | Keep |
| hvac near me | Heating Repair / heating repair (PHRASE) | NEAR_PHRASE | 22 / 1 / $15.18 | a CALLS click; 60 s Google call on 09-30, no WhatConverts record | Ambiguous | Keep |
| cost of geothermal heating and cooling | Geothermal / geothermal heating (PHRASE) | PHRASE | 3 / 1 / $12.33 | none | Price research (buyer) | Keep |

**Category calls:**
- **AC/cooling:** an approved Ambient service, but cooling is owner-paused and this campaign already negates PHRASE `ac repair` / `air conditioning repair`. The observed variants are EXACT candidates. Drop them if cooling demand should be bought here.
- **Fireplaces:** covered since 09-26.
- **Pellet stoves:** not an approved service → candidates.
- **Water heaters:** covered.
- **Vehicle heaters** (Webasto) → candidate.
- **Oil:** out of scope by the owner's 2026-09-21 decision → candidates. Ambient converted oil leads historically; this enforces the owner's scope decision, not a judgment of demand.
- **Fault-code lookups** (e.g. control and blower faults, rollout switch): **Monitor, not negative.** A homeowner who just read a code may hire.
- **"24 hour …"** → routing review (Emergency).
- **Commercial, duct, radiant, Reznor/Rinnai:** service confirmation. Not negated.
- **Places outside the 75 targets** (Easton, Frederick, Silver Spring, Towson, Beltsville): Monitor. Service area beyond the targets is unverified.
- **Ambiguous names** (e.g. comfort care heating, quick service hvac): Monitor.

## 5. Existing negatives and new EXACT candidates

**Layers in force (both campaigns):**
- Account-level list `11252984411`: 269 BROAD.
- Shared list `12249470554`, "Heating | Low-intent, off-topic & competitor": 275 BROAD + 216 PHRASE, added 2026-09-26 16:36 (+2 on 09-27).
- Shared list `12252013691`, "Heating | Out-of-scope search terms (EXACT)": 78, added 2026-09-26 16:15.
- Campaign PHRASE: 25 on repair, 2 on geothermal.
- Ad-group PHRASE routing negatives: 85.

**Coverage of the 270 rows:**
- **35 already covered.** Every one was blocked by shared list `12249470554`, and all of them last served **before** that list existed (first serving day under it: 09-28). So **no exclusion failure**.
- **235 newly uncovered.**
- **0 covered in only some ad groups.**
- **1 uncertain:** Google still labels a pre-list query "NONE" although `how does` now blocks it; it hasn't been re-served.

**Potentially over-blocked (existing; not modified, per instructions):**
- Account-level BROAD `carrier`, `trane`, `lennox`, `goodman`, `rheem`, `bryant`, `american`, `amana`, `ruud` block every manufacturer-plus-furnace-repair search in every repair ad group. (`york` passes.) The 2026-09-09 reverse test flagged this; it is still live. Recommend a separate removal plan once supported brands are confirmed.
- Ad-group `emergency` negatives on Heating Repair and Furnace Repair, plus the empty Emergency group, mean emergency searches currently reach nothing. This is consistent with the availability hold, and it fixes itself when Emergency launches.
- Geothermal *repair* searches are blocked everywhere: Geothermal negates `repair`, Heat Pump Repair negates `geothermal`. This is by design (section 9).

**62 EXACT candidates. Draft only; not in the launch bundle.**
- 33 competitor, 18 AC, 6 oil, 3 pellet stove, 1 vehicle, 1 geothermal informational.
- Spend all-time: $62.85 (two queries).
- All are ≤10 words and ≤80 characters. `[g & g mechanical heating & ac 305 e 31st st baltimore md 21218]` is 14 words, so it can't be added; it moves to Monitor.
- None equals a positive keyword. Conflict check: an EXACT negative blocks only that full query, so every longer buyer query stays eligible.
- Scope is campaign level: each query is unsuitable throughout its campaign and no proven intra-campaign routing problem exists.
- All are observed, not hypothetical.

| # | Display | Match | Scope | Seen in | Impr / clicks / cost (09-17..10-01) | First..last seen | Why | Conf. | Priority |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `[booths hvac]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 1 / $39.15 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P1 |
| 2 | `[s f jones heating and cooling]` | EXACT | campaign 24257819463 | Heating Repair | 3 / 1 / $23.70 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P1 |
| 3 | `[moon air elkton]` | EXACT | campaign 24257819463 | Heating Repair | 8 / 0 / $0.00 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P2 |
| 4 | `[dodge heating and air]` | EXACT | campaign 24257819463 | Heating Repair | 7 / 0 / $0.00 | 09-25..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P2 |
| 5 | `[repair air conditioner near me]` | EXACT | campaign 24257819463 | Heating Repair | 7 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 6 | `[air conditioner repair near me]` | EXACT | campaign 24257819463 | Heating Repair | 6 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 7 | `[coastal hvac annapolis]` | EXACT | campaign 24257819463 | Heating Repair | 6 / 0 / $0.00 | 09-25..10-01 | competitor: another HVAC company's name (navigational); not Ambient | high | P2 |
| 8 | `[max air heating & a c inc]` | EXACT | campaign 24257819463 | Heating Repair | 6 / 0 / $0.00 | 09-25..09-25 | competitor: another HVAC company's name (navigational); not Ambient | high | P2 |
| 9 | `[a c repair near me]` | EXACT | campaign 24257819463 | Heating Repair | 5 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 10 | `[pellet stove repair near me]` | EXACT | campaign 24257819463 | Heating Repair | 5 / 0 / $0.00 | 09-23..09-29 | pellet_stove: pellet stove; no approved-record or site evidence Ambient services it | high | P2 |
| 11 | `[ac service near me]` | EXACT | campaign 24257819463 | Heating Repair | 4 / 0 / $0.00 | 09-29..10-01 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 12 | `[air conditioning service near me]` | EXACT | campaign 24257819463 | Heating Repair | 4 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 13 | `[air conditioning servicing near me]` | EXACT | campaign 24257819463 | Heating Repair | 4 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 14 | `[carroll mechanical columbia md]` | EXACT | campaign 24257819463 | Heating Repair | 4 / 0 / $0.00 | 09-30..09-30 | competitor: another HVAC company's name (navigational); not Ambient | high | P2 |
| 15 | `[repair air conditioning near me]` | EXACT | campaign 24257819463 | Heating Repair | 4 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 16 | `[webasto heater repair near me]` | EXACT | campaign 24257819463 | Heating Repair | 4 / 0 / $0.00 | 09-30..09-30 | vehicle: vehicle/parking heater, not a home heating system | high | P2 |
| 17 | `[ac service and repair near me]` | EXACT | campaign 24257819463 | Heating Repair | 3 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 18 | `[fix air conditioning near me]` | EXACT | campaign 24257819463 | Heating Repair | 3 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P2 |
| 19 | `[pellet stove repair in my area]` | EXACT | campaign 24257819463 | Heating Repair | 3 / 0 / $0.00 | 09-25..09-25 | pellet_stove: pellet stove; no approved-record or site evidence Ambient services it | high | P2 |
| 20 | `[ac unit repair near me]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 21 | `[air conditioner service near me]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 22 | `[allpro hvac]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 23 | `[b&d hvac]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-30..09-30 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 24 | `[fix air conditioner near me]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 25 | `[go ecco climate control]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 26 | `[heating oil furnace service]` | EXACT | campaign 24257819463 | Furnace Repair | 2 / 0 / $0.00 | 09-29..09-29 | oil: oil-fired equipment; Oil services are OUT of advertising scope (owner, | high | P3 |
| 27 | `[home air conditioner repair]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 28 | `[home air conditioner repair near me]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 29 | `[home team heating and cooling]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 30 | `[howard mechanical hvac]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-29..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 31 | `[joey taylor hvac]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-30..09-30 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 32 | `[maryland mechanical heating & cooling]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 10-01..10-01 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 33 | `[oil furnace cleaning service near me]` | EXACT | campaign 24257819463 | Furnace Repair | 2 / 0 / $0.00 | 09-30..09-30 | oil: oil-fired equipment; Oil services are OUT of advertising scope (owner, | high | P3 |
| 34 | `[stanton hvac]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 35 | `[stivers hvac inc]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 10-01..10-01 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 36 | `[triple eee hvac]` | EXACT | campaign 24257819463 | Heating Repair | 2 / 0 / $0.00 | 09-30..09-30 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 37 | `[what is geothermal heating]` | EXACT | campaign 24274160783 | Geothermal Heat Pump | 2 / 0 / $0.00 | 09-24..09-24 | info: research question with no hire signal | medium | P3 |
| 38 | `[air conditioner repair annapolis]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 39 | `[air conditioner repair company]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 10-01..10-01 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 40 | `[air conditioner servicing near me]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 41 | `[bnb heating and cooling]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-25..09-25 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 42 | `[coastal heat and air]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 10-01..10-01 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 43 | `[cold comfort hvac rockville md]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 44 | `[commercial air conditioner repair]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | ac: air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 an | high | P3 |
| 45 | `[energylogic waste oil heater service]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-28..09-28 | oil: waste-oil shop heater (commercial garage equipment), oil is OUT of sco | high | P3 |
| 46 | `[falcon hvac]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-30..09-30 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 47 | `[frosty heating and air conditioning]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 10-01..10-01 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 48 | `[grove hvac maryland]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 49 | `[harbor point heating and air]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 10-01..10-01 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 50 | `[honest air mt airy]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 10-01..10-01 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 51 | `[hope plumbing heating and cooling]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-30..09-30 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 52 | `[jiffy hvac]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 53 | `[ocean air hvac]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-30..09-30 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 54 | `[oil burner service near me]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | oil: oil-fired equipment; Oil services are OUT of advertising scope (owner, | high | P3 |
| 55 | `[oil furnace companies near me]` | EXACT | campaign 24257819463 | Furnace Repair | 1 / 0 / $0.00 | 09-25..09-25 | oil: oil-fired equipment; Oil services are OUT of advertising scope (owner, | high | P3 |
| 56 | `[oil heater service]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-28..09-28 | oil: oil-fired equipment; Oil services are OUT of advertising scope (owner, | high | P3 |
| 57 | `[pellet stove service near me]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | pellet_stove: pellet stove; no approved-record or site evidence Ambient services it | high | P3 |
| 58 | `[powell and turner hvac]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-25..09-25 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 59 | `[smock heating & air]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 60 | `[southern maryland heating and air waldorf md]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 61 | `[vito hvac]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-29..09-29 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |
| 62 | `[xzavier hvac solutions llc baltimore reviews]` | EXACT | campaign 24257819463 | Heating Repair | 1 / 0 / $0.00 | 09-28..09-28 | competitor: another HVAC company's name (navigational); not Ambient | high | P3 |

**What EXACT-only can't do:**
- An EXACT negative blocks its full query only. Per Google, negatives account for casing and misspellings but **not close variants, synonyms, plurals or reorderings**.
- 43 of the 62 had fewer than 3 impressions, and the next competitor or AC variant will be new words.
- A few PHRASE negatives would close the recurring patterns: `oil`, `pellet stove`, `webasto`, `air conditioner`. That is outside this request; flagged for a later decision.

## 6. Hypothetical EXACT candidates (not observed; no metrics exist)

Checked against every layer on Heating Repair and Furnace Repair.

**Already blocked, no negative needed:**
- `furnace repair jobs`, `heating repair jobs`, `hvac technician jobs`, `furnace repair technician salary`: `jobs` / `salary` PHRASE.
- `how to repair a furnace yourself`: `how to`.
- `car heater repair near me`, `rv furnace repair`, `boat heater repair`: `car` / `rv` / `boat`.
- `wood stove repair near me`, `space heater repair`.
- `furnace parts near me`, `furnace manual`, `hvac certification near me`.
- `ac repair near me`: campaign PHRASE `ac repair`.
- `heat pump repair`: routes to Heat Pump Repair.

**Uncovered, proposed (17):**

| Candidate | Scope | Basis | Literal reach today | Conf. |
|---|---|---|---|---|
| `[webasto heater repair]` | campaign 24257819463 | observed `webasto heater repair near me` | PHRASE heater repair | high |
| `[webasto repair near me]` | same | same brand | semantic only | high |
| `[diesel heater repair]` | same | vehicle/marine diesel heaters, same leak | PHRASE heater repair | medium |
| `[pellet stove repair]` | same | 3 observed pellet-stove queries | semantic only | high |
| `[pellet stove service]` | same | observed `… service near me` | semantic only | high |
| `[pellet stove technician]` | same | pellet-stove family | semantic only | medium |
| `[oil furnace repair]` | same | oil out of scope; 6 oil queries observed | PHRASE furnace repair | high |
| `[oil furnace repair near me]` | same | same | PHRASE furnace repair near me | high |
| `[oil furnace service near me]` | same | observed `oil furnace cleaning service near me` | semantic only | high |
| `[oil burner repair]` | same | observed `oil burner service near me` | semantic only | high |
| `[oil burner service]` | same | same | semantic only | high |
| `[oil heater repair]` | same | observed `oil heater service` | PHRASE heater repair | high |
| `[air conditioner repair]` | same | 18 AC queries observed | semantic only | high |
| `[air conditioner repair company near me]` | same | observed `… company` | semantic only | medium |
| `[ac unit repair]` | same | observed `ac unit repair near me` | semantic only | medium |
| `[fix air conditioner]` | same | observed `fix air conditioner near me` | semantic only | medium |
| `[buy furnace control board]` | same | generic hypothesis: parts shopping (covered only in Heating Repair, by `furnace`) | semantic only | medium |

**Not recommended:** `[furnace error code 33]`. Fault-code searchers may hire, so these stay on Monitor. No savings are forecast for any of these. Not every blocked search would have been a waste, and not every remaining visitor becomes a lead.

## 7. Boiler repair and short queries

**Routing:**
- Boiler intent belongs in **Boiler Services 24132507744 › Boiler Repair 204129718047**: PHRASE + EXACT `boiler repair`, 2 enabled RSAs → `/gas-boiler-repair/`.
- `gas boiler repair` belongs in **Gas Boiler Repair 202339087594**.
- The repair campaign negates PHRASE `boiler` (campaign and every ad group), so it never competes.
- Approved boiler fuel: **gas** (`Gas Boiler Repair` in `services_in_scope`). **Oil is out of scope** and is negated (`oil`) in all boiler groups. Ambient is not assumed to service every boiler type.

| Query | Assessment | Where it can serve | Action |
|---|---|---|---|
| boiler repair | buyer | Boiler Repair (EXACT + PHRASE) | **Keep. Never negate `[boiler repair]` anywhere:** no evidence supports excluding it, and it is a core routed service. |
| boiler repair near me | buyer + local | Boiler Repair (PHRASE) | Keep |
| boiler repair in severn | buyer; Severn is targeted | Boiler Repair (PHRASE) | Keep |
| boiler repair cost | buyer researching price | Boiler Repair (PHRASE) | Keep |
| boiler | ambiguous | nothing: no positive can match it literally | None needed |
| how to repair a boiler yourself | DIY | blocked by `how to` (shared + campaign) | Already covered |
| boiler repair jobs | employment | blocked by `jobs` (shared + campaign) | Already covered |

**Matching note:** a negative `[boiler repair]` would block only that exact query. `boiler repair near me` would stay eligible but would not be guaranteed to serve, and a positive EXACT keyword can still match same-meaning searches.

## 8. Heating Repair: Phrase versus Exact

| Keyword (ad group 204129717007) | 09-17..09-29 | 09-24..09-30 | 10-01 | 09-17..10-01 |
|---|---|---|---|---|
| `heating repair` PHRASE (142140741) | 815 / 15 / **$406.12** / 0 conv (3 GBP actions) | 924 / 21 / $575.33 | 105 / 3 / $47.04 | 1,060 / 24 / **$622.37** |
| `heater repair` PHRASE | 49 / 0 / $0 | 58 / 0 | 6 / 0 | 66 / 0 |
| `heating repair` EXACT | 3 / 0 | 3 / 0 | 2 / 0 | 5 / 0 |
| `heater repair` / `heating repair service` / `residential heating repair` EXACT | 1 / 3 / 21 impr, 0 clicks | same | 0 / 0 / 2 | 27 impr, 0 clicks |

**Evidence:**
- **Visibility:** 418 of the 421 visible baseline impressions are NEAR_PHRASE. Only 1 visible query literally contains "heating repair", and only 36% of the keyword's baseline cost is visible.
- **Visible spend by intent:** clearly irrelevant 44%, ambiguous HVAC-company 42%, fireplace (now covered) 14%, explicit heating repair 0%.
- **Leads:** 0 verified paid leads, 0 qualified.
- **Measurement is weak:**
  - D6 may block form submissions.
  - Both Google call records on this ad group (52 s, 60 s) reached a number WhatConverts doesn't track.
  - The repair campaign's call assets are PAUSED.

**Recommendation: clean up and monitor.** Do not change match types now:
- The Exact keywords drew 32 impressions and 0 clicks in two weeks of low September demand. Pausing Phrase would all but stop the campaign the owner kept live.
- It would also confound the $18 test.
- Generic "HVAC company near me" searches in October plausibly include heating buyers.

**Trigger for a later Phrase-pause plan (separate approval; keep all four Exact keywords):**
- At the Oct 8 read, the Phrase keyword has 0 verified paid leads on **≥$300 spent since Oct 1**, **and**
- ≥50% of its visible spend is still clearly irrelevant or non-heating after the EXACT clean-up.

The monitor is **NOT ACTIVE**; this is a manual check.

## 9. Emergency and Geothermal: mapping, page QA, service verification

Both URLs were checked in Chrome on desktop plus a 386–390 px mobile frame. Evidence: `clients/ambient-cooling-heating/snapshots/lp-qa-2026-10-01.json`. The earlier ChatGPT checker's failure was its own access problem; both pages are up.

| Check | /emergency-heating-repair/ | /geothermal-heat-pump/ |
|---|---|---|
| HTTP / redirects / robots | 200 / 0 / noindex | 200 / 0 / noindex |
| H1 | Emergency Heating Repair in Central MD | Geothermal Heat Pump Service in Central MD |
| Offer | free quote form | free quote form; New-System Consultation, Replacement Planning, Existing-System Assessment |
| Claims | Business hours only: Mon–Fri 8–4, "immediate arrival is not guaranteed", FAQ says **No** to 24-hour and to guaranteed same-day. No price or guarantee. | No price, discount or guarantee. **But a "Offer Ends in 00 DAY 00 HRS 00 MIN 00 SEC" countdown shows with no offer** (this page only). |
| Phone | all 3 tel: links dial (410) 705-6354 (the paid number), visible on mobile | same |
| Mobile | no horizontal overflow; H1 and 2 forms visible | same |
| Tags | GTM-PQTPQ436, AW-11155434808 (page view only; no conversion on load), WhatConverts cookies + requests | same |
| D6 | **open:** message field "(optional)*" is configured **required** (all 3 instances; same on `/furnace-repair/`) | **open** (same) |
| D5 | open: 3 × `form#gform_1`, 55 duplicated ids | open (same) |
| D7 | not reproduced (attribution fields empty on load); one load can't prove a fix | same |
| D1 | open: 761-0932 ×4 in server HTML, 0 rendered | open: ×2 in HTML |
| Page-specific | AC template sentence in the symptom section | zeroed countdown |
| Form / thank-you / WhatConverts receipt | **not tested:** no submission was sent (Q2) | same |

**Emergency Heating Repair (204129717047, in campaign 24257819463):**
- **Service evidence:** heating repair capability is verified, and answering hours (Mon–Fri 8–4) are published and owner-confirmed. The page claims only that.
- **Missing operational fact:** will Ambient book an urgent no-heat repair visit for a caller during those hours?
- The group has no ads, so assigning a URL alone delivers nothing. The minimum build is two RSAs plus one PHRASE keyword. The 5 existing keywords stay PAUSED until ENABLE.
- **Risk:** all-time account search terms with emergency intent cost $881.40 / 52 clicks / 1 conversion (AMB-0922-BUILD-1 evidence; most predate the Mon–Fri 08–16 schedule). That is well above the $350 CPL ceiling. Business-hours serving may change that, but it is unproven.

**Geothermal Heat Pump (204129719007, campaign 24274160783, $20/day):**
- **Paid service, from approved records:** geothermal heat pump system inquiries plus new-system installation / replacement consultation. **Repair is not in the paid scope**: the ad group's own `repair` negative and the main-site installation page establish that. No question needed.
- **Mapping:** reuse the existing ad group; no duplicate group, campaign or budget.
- **Currently:**
  - Its 2 RSAs are PAUSED on a main-site URL and are left as they are.
  - An **ad-group sitelink "Dehumidification Services" → main site** is ENABLED. It would serve beside the new ads, so the plan pauses it.
  - The campaign has no other enabled sitelinks. Callouts, the 415-9517 call asset and snippets are enabled.

## 10. Launch approval bundle (separate from the negatives)

Shared by both plans:
- **Build script:** `scripts/ambient_1002_launch_build.py`. **Executor:** `scripts/ambient_1002_launch_execute.py`.
- **Validation:** Google `validate_only` passed (6/6). Local checks: lengths, a barred/unverified-claim scan, no phone numbers in ad text, paths ≤15, no duplicate headlines, 0 headline overlap between paired RSAs, work-order validator PASS.
- **Unrelated-resource baseline** `ae1f1d999d90a549` covers the configuration of both campaigns: budgets, bidding/ceiling, schedules, 75 locations, every criterion and device modifier, negatives, shared-list attachments, all other ads, keywords and asset links, and conversion primaries. The executor refuses on any drift and re-hashes after writing.
- **Unchanged by both plans:** budgets ($85 / $20; enabled total stays $305/day), Maximize Clicks ceilings ($18 / $38), 75 PRESENCE locations, Mon–Fri 08–16, conversion actions and goals, all negatives, tracking (none exists), website/GTM/WhatConverts/GBP.

### AMB-1002-EMER-CREATE-1 · fingerprint **AF13621050E2** · 3 operations · create-paused

- **Service:** Emergency Heating Repair.
- **Target:** campaign `24257819463` Search | NonBrand | Heating & Furnace Repair | Central MD | BOFU | 2026-09 › ad group `204129717047` SKAG | Emergency Heating Repair.
- **Effective URL:** before, none (0 ads). After this plan, still none (PAUSED). After ENABLE: `https://offer.ambientcoolingandheating.com/emergency-heating-repair/`.

Operations:
1. RSA A, PAUSED. Paths Emergency / Heating.
   - Headlines: Emergency Heating Repair · Emergency Furnace Repair · Heating Stopped Working? · No Heat? Call Mon-Fri 8-4 · Heating Repair In Central MD · Severn Heating Repair · Severna Park Heating Repair · Columbia MD Heating Repair · Ask About The Next Visit · Free Heating Repair Quote · No-Heat Diagnosis · Clear Repair Options · Furnace & Heating Repair · Business-Hours Heating Help · Local Maryland Service.
   - Descriptions: **[pinned 1]** "Heating stopped? Call Mon-Fri, 8 a.m.-4 p.m. to check the next available repair visit." · "We assess the system, explain what failed and confirm the repair before work begins." · "Emergency heating repair for homes in Severn, Severna Park and Columbia, Maryland." · "Send a repair request online or call during business hours for a free quote."
2. RSA B, PAUSED. Same paths.
   - Headlines: Heat Not Working? · Urgent Heating Repair · Emergency Heater Repair · Furnace Stopped Heating? · Calls Answered Mon-Fri 8-4 · Next Available Appointment · Heating Breakdown Help · Central Maryland Heating · Glen Burnie Heating Repair · Annapolis Heating Repair · Get A Free Repair Quote · Assessment Before Repair · Clear Scope Before Work · Home Heating Repair · Talk To Our Heating Team.
   - Descriptions: **[pinned 1]** "Calls answered Mon-Fri, 8 a.m.-4 p.m. Ask about the next available heating repair visit." · "Tell us what the system is doing. We assess it and confirm the repair scope first." · "Heating repair for homes in Annapolis, Glen Burnie, Severn and Columbia, MD." · "Request a free heating repair quote online, or call during business hours."
3. Keyword PHRASE `emergency furnace repair`, PAUSED. It lets `emergency furnace repair near me` and `… severn` reach the group; Furnace Repair negates `emergency`.

The hours description is pinned so **every impression discloses the business-hours limit**. Ad Strength is not an objective. Supersedes the never-uploaded AMB-0922 Emergency payloads.

### AMB-1002-GEO-CREATE-1 · fingerprint **B7B7A99EA739** · 3 operations · create-paused + 1 link pause

- **Service:** Geothermal Heat Pump (system inquiries + new-system installation / replacement consultation).
- **Target:** campaign `24274160783` Search | NonBrand | Geothermal Heat Pump | Central MD | BOFU | 2026-09 › ad group `204129719007` SKAG | Geothermal Heat Pump.
- **Effective URL:** before, none serving (2 PAUSED RSAs `825585199679` / `825585199802` → main-site page, untouched). After ENABLE: `https://offer.ambientcoolingandheating.com/geothermal-heat-pump/`.

Operations:
1. RSA A, PAUSED. Paths Geothermal / Heat-Pump.
   - Headlines: Geothermal Heat Pumps · Geothermal Heat Pump Service · Geothermal Heating & Cooling · New Geothermal System Quote · Plan A Geothermal Install · Geothermal Replacement Help · Central MD Geothermal · Severn Geothermal Heat Pumps · Columbia Geothermal Systems · Annapolis Geothermal Systems · Free Geothermal Quote · Property-Specific Review · Ground-Loop System Review · Clear Scope Before Work · Talk To Our Geothermal Team.
   - Descriptions: "Considering geothermal or replacing an existing system? Request a property review." · "We review your home, equipment and ground loop, then explain the options and scope." · "Geothermal heat pump systems for homes in Severn, Severna Park and Columbia, MD." · "Request a free geothermal quote online or call to discuss your next step."
2. RSA B, PAUSED. Same paths.
   - Headlines: Considering Geothermal? · Geothermal Heat Pump Quotes · Replacing A Geothermal Unit? · New Geothermal Consultation · Geothermal For Your Home · Maryland Geothermal Systems · Assess Your Property First · Geothermal Options Explained · Glen Burnie Geothermal · Crofton Geothermal Heat Pump · Request Geothermal Service · Get A Free Geothermal Quote · Geothermal Project Planning · Home Comfort Assessment · Central Maryland Service.
   - Descriptions: "Planning a new geothermal system? Start with an assessment of your home and property." · "Replacing an older geothermal heat pump? Learn what must be evaluated first." · "Confirm the work and schedule with our team before any geothermal project starts." · "Ambient Cooling & Heating serves Central Maryland homes. Request a free quote."
3. Pause ad-group asset link `204129719007~290641223062~SITELINK` ("Dehumidification Services" → main-site drying page). The asset itself is untouched.

Supersedes the repair-led geothermal entry in AMB-0925-HELD-RSA-PAYLOADS.

### After approval

The executor:
1. Recomputes the fingerprint.
2. Re-checks identity and the baseline hash.
3. Writes with `partial_failure=false`.
4. On any mid-run failure, stops and records the created IDs (no retry).
5. Reads back status, URL, text, pins, paths, the keyword and the link.
6. Re-hashes the baseline and writes `receipts/<plan>-EXECUTED.json`.

### ENABLE stage (drafts; a second approval after readback)

- **`AMB-1002-GEO-ENABLE-1`**: enable the 2 new RSAs and remove label WAITING_LP. Gates: countdown removed, both ads APPROVED, readback 0 FAIL. This alone starts geothermal delivery: the ad group, its 5 keywords and the campaign are already ENABLED, and the $20 is already inside the $305 total.
  - **CPL guardrail:** zero-lead review at **$300** cumulative (min($300, $350 − 2 × $20)). Historical geothermal search terms ran at $327.51 per conversion. The monitor is NOT ACTIVE; this is a manual check.
- **`AMB-1002-EMER-ENABLE-1`**: enable the 2 RSAs and 6 keywords, and remove WAITING_LP + WAITING_AVAILABILITY. Gates: the dispatch answer (Q1), ads APPROVED, readback 0 FAIL. If enabled before Oct 8, Emergency is reported separately so the $18 read stays a CPC-only comparison.
- Enabled ads that get a new destination later will stay enabled and may re-enter policy review; serving is never promised immediately.

## 11. Phone attribution

| Number | Reported role | Verified now (WhatConverts config API + Google) | Gap |
|---|---|---|---|
| 410-705-6354 | paid landing-page base number | WC "GSA Cooling Traffic", google/cpc, static (no swap). Every tel: on both new pages. Google call asset 407995613637 carries it but is **PAUSED** on repair and geothermal | WC config returns a blank destination field; routing not re-proven by a call |
| 410-914-1456 | website DNI | WC "Website Traffic", **Pool: All Traffic**, swaps 761-0932 → 761-0932; last used 2026-10-02 03:39 UTC | mixed-source, not paid-specific |
| 410-415-9517 | heating call-asset number | WC "GSA's Heat Traffic", google/cpc, Click to Call, → 761-0932. Asset 424764337810 ENABLED on Boiler, Heat Pump, Thermostat, Maintenance and **Geothermal**; **PAUSED on Repair** and Install/Replace | `last_used` = never: no call has ever come through it |
| 410-761-0932 | final destination | destination of 914-1456, 415-9517, 324-2742, 429-7280, 429-7756 | n/a |

**Reconciliation, in-scope campaigns, 09-17..10-01** (`snapshots/cpl-reconciliation-2026-10-01.json`; WhatConverts default + duplicate + spam sets; no PII):
- **Verified paid leads: 0. Qualified: 0.** CPL and CPQL are **undefined** on $639.11 (baseline) and $47.04 (Oct 1).
- **Unmatched Google calls: 2**, both in the Heating Repair group, mobile, RECEIVED: 09-25 12:11 (52 s) and 09-30 11:38 (60 s). The call assets are paused, so these came through the **Business Profile location asset** to a number WhatConverts doesn't record. They are not proof of fake or lost calls; genuineness is unknown.
- **Probable but unverified: 1.** WC 260999389, 09-30 13:40, DNI 914-1456, 130 s, google/cpc label, main-site landing, no click ID. Repair ads land only on offer pages, so a location-asset website visit is plausible but unproven.
- Duplicate attributions in scope: none.
- **Account-wide for context:** 2 click-ID-verified paid leads, both 09-28 (Boiler Replacement form; Furnace Replacement call).

**Business Profile overrides:** the API can't read them. **Manual check still needed** for all three locations (`102853408140` Woodbine, `138665832571`, `245790011117`) in Business Profile Manager. Severn and Annapolis were last recorded as 216-4650.

**Developer actions (in priority order):**
1. **D6:** make the message field truly optional, or relabel it. It is on every offer page.
2. Remove the zeroed countdown from `/geothermal-heat-pump/`. This gates GEO-ENABLE.
3. Replace the AC sentence on `/emergency-heating-repair/`.
4. **D5:** render one form per page.
5. **D1:** remove 761-0932 from the server HTML.
6. **D7:** confirm the attribution fields populate client-side and are not cached.

No phone, conversion, WhatConverts, Business Profile or tracking change was made.

## 12. $18 test: baseline and template

- **Baseline:** Sept 24–30 ($42 ceiling; Sept 30 confirmed old-ceiling traffic).
- **Test days:** Oct 1, 2, 5, 6, 7 (Mon–Fri schedule confirmed).
- Oct 1 is complete, but conversions can still post: WC Lead uses a 60-day lookback.

| Metric (campaign 24257819463) | Baseline 09-24..30 | Oct 1 | Oct 2 | Oct 5 | Oct 6 | Oct 7 | Test total |
|---|---|---|---|---|---|---|---|
| Impressions | 1,232 | 149 | | | | | |
| Clicks | 23 | 3 | | | | | |
| CTR | 1.87% | 2.01% | | | | | |
| Avg CPC | $27.79 | $15.68 | | | | | |
| Spend | $639.11 | $47.04 | | | | | |
| Unique verified paid leads | 0 | 0 | | | | | |
| Qualified (Quotable Yes) | 0 | 0 | | | | | |
| CPL | undefined ($639.11 / 0) | undefined | | | | | |
| CPQL | undefined | undefined | | | | | |
| Search IS | 36.5% | not yet reported | | | | | |
| Lost IS (rank) | 32.5% | not yet reported | | | | | |
| Lost IS (budget) | 31.1% | not yet reported | | | | | |
| Top / abs-top IS | 23.8% / 13.7% | not yet reported | | | | | |

**Breakdowns:**
- **Ad group:** Heating Repair 1,010 / 21 / $575.33 baseline, then 115 / 3 / $47.04 on Oct 1 (100% of spend). Furnace Repair 182 / 2 / $63.78, then 34 / 0. Gas Furnace 38 / 0, then 0. No Heat 2 / 0. Electric and Emergency 0.
- **Device:** baseline mobile 751 / 19 / $564.71, desktop 469 / 4 / $74.40, tablet 12 / 0. Oct 1: mobile 83 / 2 / $31.25, desktop 66 / 1 / $15.79. **Tablets −100% from 14:09 on Oct 1.**
- **Keyword:** Phrase `heating repair` $575.33 then $47.04. `furnace not working` $63.78 then $0. Every Exact keyword: $0.
- **Queries:** visible 608 / 10 / $270.43 baseline; 78 / 2 / $32.00 on Oct 1.

**Change log for the test:**
- Tablet −100% at 10-01 14:09 (all campaigns).
- Any approved EMER/GEO execution will be time-stamped here. Emergency is reported as its own row. Geothermal is a separate campaign.
- No revenue, margin or sold-job data exist, so no savings or profit is estimated.

## Questions (only what blocks a stage)

1. **Emergency dispatch:** when someone calls Mon–Fri 8 a.m.–4 p.m. with no heat, does Ambient book them the next available technician visit (no time promise)? Answering is already verified; this is the only fact blocking `AMB-1002-EMER-ENABLE-1`.
   - **Recommendation:** if yes, enable after Oct 7. If no, keep Emergency held; the create-paused plan still costs nothing.
2. **One QA test submission per new page?** It would use the owner-approved QA identity, label "TEST - DO NOT DISPATCH", no URL parameters, and be marked Spam afterwards. WhatConverts will still forward it to Google Ads as an unattributed WC Lead, which was accepted and not credited the last six times.
   - **Recommendation:** yes, after the D6 fix. Until then, form completion stays "not tested".

**Approval lines:**
- `APPROVE AMB-1002-EMER-CREATE-1 AF13621050E2 3 operations FOR 2401959466`
- `APPROVE AMB-1002-GEO-CREATE-1 B7B7A99EA739 3 operations FOR 2401959466`
