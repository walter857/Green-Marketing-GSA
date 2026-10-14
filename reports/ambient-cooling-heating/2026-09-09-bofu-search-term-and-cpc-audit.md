# Ambient Cooling — BOFU Search-Term Cleanup and CPC-Control Audit

**Account:** Ambient Cooling - Live · **Customer ID:** 2401959466 · **Vertical:** heating-cooling
**Services in scope:** AC Repair (primary), HVAC Repair, HVAC Installation, HVAC Replacement, Gas Boiler Repair
**Run date:** 2026-09-09 · **Mode:** READ + ANALYZE + DRAFT + VALIDATE-ONLY
**Mutations executed in this run: 0.** Six packages are validated and awaiting approval.

---

## 0. The headline

Three findings dominate everything else in this audit.

**1. The account is effectively switched off, and has been since 2026-09-04.**
At 16:56 America/New_York on 2026-09-04, `GOOGLE_ADS_WEB_CLIENT` — an edit made in the Google Ads
UI, not by the agency — set Maximize-Clicks CPC bid ceilings of $25 on AC Repair, $25 on HVAC
Repair and $30 on HVAC Installation. The measured effect:

| Window | Days | Impressions | Clicks | Cost | Primary conversions |
|---|---|---|---|---|---|
| 2026-08-14 → 2026-09-03 (before) | 21 | 5,307 | 172 | $8,025.18 | 14 |
| 2026-09-05 → 2026-09-08 (after) | 4 | 154 | 2 | $45.08 | 0 |

That is a 97% collapse in delivery and a 100% collapse in conversions. The two clicks that did
get through cost $21.46 and $23.62 — both pinned just under the $25 cap, which is the classic
signature of a ceiling that *is* the clearing price rather than a brake on an inflated one.

**2. The search-term problem the audit was commissioned to fix is already 96% solved.**
Of 952 visible search-term rows in the API for the CSV window, 419 (44%) are already blocked by
the 6,160 live campaign negatives and 452 (47.5%) are genuine BOFU HVAC intent. Only **2 rows,
worth $20.44**, classified as new negative candidates. There is essentially no negative-keyword
work left to do on the visible corpus.

**3. The real negative-keyword problem runs the other way: live negatives are blocking Ambient's
own services.** 88 live negatives collide with protected demand. Among them, at the
**account level** (which campaign-level rules cannot override): BROAD `carrier`, `trane`,
`lennox`, `goodman`, `rheem`, `mitsubishi`, `daikin`, `amana`, `bosch`, `bryant`, `armstrong`,
`ruud` — twelve supported manufacturers — plus BROAD `commercial`, `thermostat`, `thermostats`,
`al`, `american` and `mr`. At campaign level: PHRASE `savage`, which blocks **Savage, Maryland**,
one of the 75 live location targets, across all five campaigns.

---

## 1. Identity, permissions, validators, concurrent writers

### 1.1 Identity gate — PASS

Fresh read-only lookup at 2026-09-09 14:28:56 America/New_York.

| Check | Required | Observed | Result |
|---|---|---|---|
| Account name | Ambient Cooling - Live | Ambient Cooling - Live | PASS |
| Customer ID | 2401959466 | 2401959466 | PASS |
| Time zone | America/New_York | America/New_York | PASS |
| Currency | USD | USD | PASS |
| Manager account | false | false | PASS |
| Test account | false | false | PASS |
| GM manager 3373711342 | ACTIVE | ACTIVE | PASS |
| ClickCease manager 2815082755 | ACTIVE | ACTIVE | PASS |

Also observed: `status = ENABLED`, `auto_tagging_enabled = true`,
`conversion_tracking_id = 11155434808`, `google_ads_conversion_customer = customers/2401959466`,
`conversion_tracking_status = CONVERSION_TRACKING_MANAGED_BY_SELF`, optimization score 0.7406.
The customer-level `tracking_url_template` routes every click through
`monitor.clickcease.com` with `ccpturl=offer.ambientcoolingandheating.com` — the authorised
ClickCease path, untouched.

### 1.2 Validators

- `scripts/validate_work_order.py` → `PASS | Ambient Cooling - Live | 2401959466 | heating-cooling | AC Repair`
- Work order vertical `heating-cooling` is a core Green Marketing vertical; no scope approval required.
- Local package preflight (`scripts/ambient_0909_preflight.py`) → **0 FAIL, 0 WARN** (see §16).

### 1.3 Concurrent-writer check — PASS

Two Python processes were running on this host (PIDs 29920, 41804, both started 2026-08-09).
Both belong to a different project, `D:\Carbon PT\...\carbon-b2b`
(`scripts/phase2/p2_s03_tag_surface.py`, `scripts/phase8/p8_s04_audiences.py`). Verified:

- zero references to `2401959466` anywhere in that repository,
- their configured customer IDs are `7239732058` and `9720978817`,
- **zero occurrences of `mutate` in either script** — they are read-only.

No process can write to customer 2401959466. Validate-only and read operations proceeded.

### 1.4 Live work order located, not overwritten

`clients/ambient-cooling-heating/work-order.yaml` (12,973 bytes, last modified 2026-08-27) and
`client.yaml` (28,833 bytes) were read in place. Neither was modified in this run.

---

## 2. Source inventory, date windows, privacy limitation, reconciliation

### 2.1 Sources used

| Source | Status | Notes |
|---|---|---|
| `Ambient Searched Terms.csv` | **FOUND** at `C:\Users\walte\Downloads\` | sha256 `fe0c8e950e33c1de…`, 995 lines |
| `ambient_negative_keyword_candidate_blocks_2026-09-09.md` | **NOT FOUND** | Full-repository and user-profile search returned nothing. The negative list was rebuilt from raw rows and live state instead, as the brief directs. |
| Fresh Google Ads API reads | **USED** | 18 read scripts, all evidence in `reports/ambient-cooling-heating/evidence/` |
| Keyword Planner | **USED** | live 10-city MD sample, Google Search only |
| Auction Insights | **UNAVAILABLE** | see §11 |
| Real-browser landing-page render | **USED** | Playwright Chromium, desktop + mobile, all five pages |
| WhatConverts / CRM | **UNAVAILABLE** | `WHATCONVERTS_API_TOKEN` is present but **empty**. Lead quality is `UNKNOWN` throughout. |
| All prior Ambient reports, plans, receipts, fingerprint manifests (Aug–Sep 2026) | **READ** | 18 reports, 57 plan files, 45 receipts, 62 snapshots |

### 2.2 Date windows

Account-local date on this run is **2026-09-09, which is PARTIAL**. Last fully settled day is
**2026-09-08**. No partial day is mixed into a settled comparison anywhere in this report.

| Label | Range |
|---|---|
| CSV source window | 2026-07-15 → 2026-09-09 (as supplied; includes the partial day) |
| Launch to last settled | 2026-08-14 → 2026-09-08 |
| Before the CPC ceiling | 2026-08-14 → 2026-09-03 (21 days) |
| Ceiling day (excluded) | 2026-09-04 (partial effect; ceiling set at 16:56) |
| After the CPC ceiling | 2026-09-05 → 2026-09-08 (4 settled days) |
| Last full month | 2026-08-01 → 2026-08-31 |
| September MTD settled | 2026-09-01 → 2026-09-08 |

`last_30`, `last_60`, `last_90`, `last_365` and all-history all return identical totals
($8,103.66 / 175 clicks / 5,589 impressions / 14 conversions) because the five campaigns have
no delivery before 2026-08-14.

### 2.3 CSV reconciliation — and the privacy limitation

The supplied CSV carries **four** Google total rows, not one:

| Google total row | Clicks | Impr. | Cost | Conversions |
|---|---|---|---|---|
| Total: Filtered search terms | 103 | 3,019 | $6,078.96 | 12.00 |
| **Total: Account** | **175** | **5,637** | **$8,103.66** | **14.00** |
| Total: Search | 175 | 5,637 | $8,103.66 | 14.00 |
| Total: Performance Max | 0 | 0 | $0.00 | 0.00 |

- Displayed search-term rows: **988** — matches the brief exactly.
- Sum of the 988 displayed rows: 103 clicks, 3,020 impressions, $6,078.96, 12.00 conversions.
- Against **Total: Filtered search terms**: clicks, cost and conversions reconcile to the cent;
  impressions differ by 1 (rounding in the displayed impression column).
- Against **Total: Account**: the displayed rows cover only **75.0% of cost** ($6,078.96 of
  $8,103.66) and **58.9% of clicks** (103 of 175).

**Privacy-threshold limitation, stated plainly: 72 clicks and $2,024.70 — 41% of clicks and 25%
of spend — sit in search terms Google withholds as low-volume. No search-term analysis in this
report, or any other, can see them.** Every verdict count below is a count of *visible* rows.
Per the brief, the Google total row is used and not silently replaced by the row sum.

A fresh API pull for the same window returned **952 rows / $6,556.39 / 117 clicks**. The row-count
difference is a grouping difference — the UI export splits by triggering Keyword (16 distinct
keywords) while the API pull groups by (term, campaign, ad group). The cost difference is the
partial day 2026-09-09 plus intraday restatement between the 09:56 export and the 14:30 API read.

**`Added/Excluded` in the CSV reads `None` on all 988 rows. That is stale and must not be trusted.**
Our matcher, run against the live negative corpus, finds **419 of those rows are blocked today** —
99 of which Google's own `search_term_view.status` also reports as `EXCLUDED`, and 320 of which
became blocked after they served (negatives added 2026-08-29, 09-01 and 09-09). Agreement with
Google on the 99 it labels EXCLUDED is **100%: zero disagreements in either direction**.

---

## 3. Current account structure, bidding, budgets, negative coverage, change history

### 3.1 Structure

| Level | Count | Notes |
|---|---|---|
| Campaigns (all) | 33 | 5 ENABLED, 18 PAUSED, 10 REMOVED |
| Campaigns (non-REMOVED) | 23 | the population the account-level negative list governs |
| Ad groups (all) | 83 | **5** are ENABLED inside an ENABLED campaign |
| Positive keywords (all) | 1,665 | **10** are servable (ENABLED criterion × ENABLED ad group × ENABLED campaign) |
| Campaign negative keywords | 15,198 | **6,160 ENABLED on the five** |
| Ad-group negative keywords | 5,383 | **11 on the five** |
| Account-level negative list 11252984411 | **272 members**, all BROAD | API reports `member_count = 0`; read `shared_criterion` directly |
| Shared negative lists attached to the five | **0** | correct — none is attached, and none should be |
| Geo targets on the five | 375 (75 per campaign) | all Maryland, PRESENCE |
| Ad schedules on the five | 30 (6 rows per campaign) | Mon–Fri 08:00–20:00 + Sat 08:00–13:00, no Sunday |
| ClickCease IP exclusions | 2,796 | on the 18 legacy campaigns' `campaign_criterion` |
| Conversion actions (non-removed) | 16 | 10 flagged `primary_for_goal` |

The five live ad groups and their only servable keywords:

| Campaign | Ad group | Keywords (Phrase + Exact) | QS | Exp. CTR | Ad rel. | LP exp. |
|---|---|---|---|---|---|---|
| AC Repair | 202339087834 SKAG \| AC Repair Near Me | `ac repair near me` | **4** | BELOW_AVERAGE | AVERAGE | AVERAGE |
| HVAC Repair | 202339087674 SKAG \| HVAC Repair Near Me | `hvac repair near me` | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** |
| HVAC Installation | 202339087634 SKAG \| HVAC Installation | `hvac installers near me` | — | — | — | — |
| HVAC Replacement | 200159223798 SKAG \| HVAC Replacement Near Me | `hvac replacement near me` | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** |
| Gas Boiler Repair | 202339087594 SKAG \| Gas Boiler Repair | `gas boiler repair` | — | — | — | — |

Structure conforms to agency policy: one canonical theme per ad group, Phrase + Exact only, no
Broad, Search-only, Search Partners off, Display off, AI Max off, text-asset automation
`OPTED_OUT`, final-URL expansion `OPTED_OUT`, PRESENCE targeting, zero location exclusions.

### 3.2 Bidding and budgets — live state

| Campaign | ID | Bidding | **CPC ceiling** | Budget ID | Daily |
|---|---|---|---|---|---|
| AC Repair | 24132507741 | TARGET_SPEND | **$25.00** | 15787409435 | $141.45 |
| Gas Boiler Repair | 24132507744 | TARGET_SPEND | uncapped | 15787409438 | $42.76 |
| HVAC Installation | 24132507747 | TARGET_SPEND | **$30.00** | 15787409441 | **$176.15** ✓ preserved |
| HVAC Repair | 24132507750 | TARGET_SPEND | **$25.00** | 15787409444 | $78.95 |
| HVAC Replacement | 24132507753 | TARGET_SPEND | uncapped | 15787409447 | $26.32 |
| | | | | **Total** | **$465.63/day** |

**Drift against the 2026-08-27 record:** the work order records
`cpc_bid_ceiling_all_five_micros: 0` / `cpc_bid_ceiling_is_uncapped: true`. That is no longer
true for three campaigns. Change history dates and attributes the change precisely (§3.4).

$465.63/day × 30 = **$13,968.90**, which is $968.90 above the $13,000 monthly maximum.
Package `AMB-0909-BUD-1` closes that gap (§15).

### 3.3 Preserved executed work — all verified present

| Item | Verified |
|---|---|
| HVAC Installation budget 15787409441 at $176.15/day | ✅ live |
| August advertising schedules on all five campaigns | ✅ 6 rows each, 30 total, no Sunday |
| Approved HVAC Repair RSA replacement | ✅ ads 821714108336 / 821714108339, both ENABLED + APPROVED |
| Approved campaign sitelinks and retained main-site sitelinks | ✅ present |
| AC Repair Broad negatives `car`, `auto`, `boat`, `automotive` | ✅ live |
| HVAC Installation competitor Phrase negatives (plan 82ACD4953536C020) | ✅ live |
| `hanover` criterion 11143481 removed from list 11252984411 | ✅ absent |
| ClickCease + all 2,796 IP exclusions | ✅ 2,796 exactly |
| GTM, WhatConverts, manager links, call assets, locations, Primary conversions | ✅ all intact |
| 5,652 campaign negatives executed 2026-08-29 | ✅ inside the current 6,160 |

Nothing executed has been replayed or proposed for re-execution.

### 3.4 Change-history reconstruction (`change_event`, 2026-08-11 → 2026-09-09, 7,414 rows)

| Date | Actor | What |
|---|---|---|
| 2026-08-19/20/22/27 | `GOOGLE_ADS_API` | agency negative and configuration work |
| **2026-08-22 01:23** | `GOOGLE_ADS_API` | HVAC Installation budget $138.16 → **$176.15** |
| **2026-08-29** | `GOOGLE_ADS_API` | **5,652 campaign negatives created** (1,128–1,132 per campaign) |
| **2026-08-28 20:58** | `GOOGLE_ADS_WEB_CLIENT` | HVAC Installation: `hvac installers` replaced with `hvac installers near me` |
| **2026-08-31 18:20–18:21** | `GOOGLE_ADS_WEB_CLIENT` | 90 ad-group criteria created: AC Repair 6 (negatives), HVAC Repair 5 (negatives), **HVAC Installation 77 (positive competitor keywords)**, **HVAC Replacement 2 (positive)** |
| **2026-09-01 13:00** | `GOOGLE_ADS_WEB_CLIENT` | **the 77 + 2 positives REMOVED** — see §8 |
| 2026-09-01 | `GOOGLE_ADS_WEB_CLIENT` | 372 campaign negatives added (186 each to Installation + Replacement) |
| **2026-09-04 16:56** | `GOOGLE_ADS_WEB_CLIENT` | **CPC ceilings set: AC Repair $25, HVAC Repair $25, HVAC Installation $30** |
| 2026-09-09 | `GOOGLE_ADS_WEB_CLIENT` | 125 further campaign negatives added |

The `client_type` field settles authorship: `GOOGLE_ADS_WEB_CLIENT` is a UI edit by the account
owner; `GOOGLE_ADS_API` is agency execution. The 2026-09-04 ceilings and the 2026-08-31/09-01
keyword episode were both owner actions.

### 3.5 Effective negative coverage

| Campaign | Broad | Phrase | Exact | Total ENABLED |
|---|---|---|---|---|
| AC Repair | 284 | 442 | 410 | 1,136 |
| Gas Boiler Repair | 280 | 444 | 408 | 1,132 |
| HVAC Installation | 466 | 546 | 423 | 1,435 |
| HVAC Repair | 280 | 449 | 409 | 1,138 |
| HVAC Replacement | 466 | 444 | 409 | 1,319 |
| **Campaign level total** | 1,776 | 2,325 | 2,059 | **6,160** |
| Ad-group level (on the five) | 1 | 0 | 10 | 11 |
| **Account level (set 11252984411)** | **272** | 0 | 0 | **272** |

The September 1 snapshot's "roughly 5,674" is now **6,160** ENABLED on the five, reconciled by
the 2026-09-01 (+372) and 2026-09-09 (+125) UI additions in the change log.

---

## 4. Search-term verdict counts, spend and conversions

952 API rows for the CSV window, every row classified.

| Verdict | Rows | Clicks | Cost | Primary conv | All conv |
|---|---|---|---|---|---|
| KEEP_BOFU | 452 | 66 | $5,282.21 | 12.0 | 59.0 |
| ALREADY_COVERED | 419 | 47 | $1,169.26 | 0.0 | 9.0 |
| KEEP_TEST | 61 | 0 | $0.00 | 0.0 | 0.0 |
| HOLD | 18 | 3 | $84.48 | 0.0 | 0.0 |
| **NEGATIVE_CANDIDATE** | **2** | **1** | **$20.44** | 0.0 | 0.0 |
| ROUTE | 0 | 0 | $0.00 | — | — |
| NEGATIVE_EXACT / PHRASE / BROAD (new) | 0 | 0 | $0.00 | — | — |

By campaign:

| Campaign | Rows | Clicks | Cost | KEEP_BOFU | ALREADY_COVERED | KEEP_TEST | HOLD | NEG_CAND |
|---|---|---|---|---|---|---|---|---|
| AC Repair | 163 | 25 | $2,872.49 | 134 | 26 | 2 | 1 | 0 |
| HVAC Installation | 606 | 63 | $1,737.26 | 178 | 356 | 55 | 15 | 2 |
| HVAC Repair | 148 | 25 | $1,816.59 | 121 | 23 | 3 | 1 | 0 |
| HVAC Replacement | 32 | 4 | $130.05 | 16 | 14 | 1 | 1 | 0 |
| Gas Boiler Repair | 3 | 0 | $0.00 | 3 | 0 | 0 | 0 | 0 |

Which live layer caught the 419 already-covered rows: BROAD 315, PHRASE 74, EXACT 30.

**The interpretation matters more than the counts.** 44% of visible rows are already blocked and
47.5% are legitimate demand. The negatives programme executed on 2026-08-29 worked. Adding more
negatives is not where the remaining money is.

---

## 5. Protected BOFU and converting-term register

**Converting terms protected: 304 distinct terms** — 25 from the five campaigns (all time) plus
304 account-wide across all 16 campaigns that have ever converted. Full register:
`clients/ambient-cooling-heating/exports/search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl`.

The nine terms named in the brief were each checked individually against the live negative corpus
in every one of the five campaigns:

| Protected term | Status |
|---|---|
| `air conditioner repair near me` | clear in all five |
| `cheap hvac service near me` | clear in all five |
| `emergency air conditioning repair near me` | clear in all five |
| `heat and air repair` | clear in all five |
| `hvac companies near me open now` | clear in all five |
| `hvac company near me` | clear in all five |
| `hvac ductwork installation near me` | blocked in HVAC Replacement only — **intentional routing**, serves in HVAC Installation |
| `hvac near me` | clear in all five |
| `repair my ac` | clear in all five |

**67 BOFU probes** were built covering every confirmed service, every intent modifier the brief
protects, every supported manufacturer and in-footprint geography. **10 live positive keywords**
were tested. Results:

- Live positive keywords blocked by a live negative: **0 of 10**. ✅
- BOFU probes blocked: **14–15 of 67 per campaign** — the defect documented in §9.

**80 protected Maryland place tokens** were derived from the live geo targets, not from a hand
list, and used as a hard guard on every proposed negative.

---

## 6. Paste-ready negative blocks

No comments inside any block. One keyword per line. Google Ads syntax.

### 6.1 REMOVALS — package `AMB-0909-NEG-RM-1` (campaign level, DESTRUCTIVE)

#### AC Repair — campaign 24132507741

**Phrase**
```
"dehumidifier"
"free"
"humidifier"
"licensed"
"savage"
```
**Exact**
```
[carrier enterprise laurel]
[carrier mid atlantic hanover maryland]
[carrier mid atlantic near me]
[ce carrier enterprise near me]
[daikin cerca de mi]
[daikin comfort technologies locations]
[daikin elkridge md]
[geothermal maryland]
[trane authorized dealers near me]
[trane installers near me]
```

#### HVAC Repair — campaign 24132507750

**Phrase**
```
"dehumidifier"
"free"
"humidifier"
"licensed"
"savage"
```
**Exact**
```
[carrier enterprise laurel]
[carrier mid atlantic hanover maryland]
[carrier mid atlantic near me]
[ce carrier enterprise near me]
[daikin cerca de mi]
[daikin comfort technologies locations]
[daikin elkridge md]
[geothermal maryland]
[trane authorized dealers near me]
[trane installers near me]
```

#### HVAC Installation — campaign 24132507747

**Broad**
```
carrier
daikin
goodman
lennox
mitsubishi
rheem
trane
```
**Phrase**
```
"dehumidifier"
"free"
"humidifier"
"licensed"
"savage"
```
**Exact**
```
[carrier enterprise laurel]
[carrier mid atlantic hanover maryland]
[carrier mid atlantic near me]
[ce carrier enterprise near me]
[daikin cerca de mi]
[daikin comfort technologies locations]
[daikin elkridge md]
[geothermal maryland]
[trane authorized dealers near me]
[trane installers near me]
```

#### HVAC Replacement — campaign 24132507753

**Broad**
```
carrier
daikin
goodman
lennox
mitsubishi
rheem
trane
```
**Phrase**
```
"dehumidifier"
"free"
"humidifier"
"licensed"
"savage"
```
**Exact**
```
[carrier enterprise laurel]
[carrier mid atlantic hanover maryland]
[carrier mid atlantic near me]
[ce carrier enterprise near me]
[daikin cerca de mi]
[daikin comfort technologies locations]
[daikin elkridge md]
[geothermal maryland]
[trane authorized dealers near me]
[trane installers near me]
```

#### Gas Boiler Repair — campaign 24132507744

**Phrase**
```
"dehumidifier"
"free"
"humidifier"
"licensed"
"savage"
```
**Exact**
```
[carrier enterprise laurel]
[carrier mid atlantic hanover maryland]
[carrier mid atlantic near me]
[ce carrier enterprise near me]
[daikin cerca de mi]
[daikin comfort technologies locations]
[daikin elkridge md]
[geothermal maryland]
[trane authorized dealers near me]
[trane installers near me]
```

### 6.2 REMOVALS — package `AMB-0909-NEG-RM-2` (ACCOUNT level, DESTRUCTIVE)

Shared set 11252984411, applies to all 23 non-removed campaigns.

**Broad**
```
al
amana
american
armstrong
bosch
bryant
carrier
commercial
daikin
goodman
lennox
mitsubishi
mr
rheem
ruud
thermostat
thermostats
trane
```

### 6.3 ADDITIONS — package `AMB-0909-NEG-ADD-1`

#### HVAC Installation — campaign 24132507747

**Phrase**
```
"all about air"
"arundel cooling and heating"
"home comfort hvac"
"maryland mechanical heating"
"sq ft house"
```
**Exact**
```
[how much is hvac system]
```

### 6.4 Ad-group level

No ad-group additions or removals are proposed. The 11 existing ad-group negatives on AC Repair
and HVAC Repair were tested against all 67 BOFU probes, all 10 live positive keywords and all
304 converting terms: none of them blocks a protected item.

---

## 7. Candidate companion table

### 7.1 The 88 colliding live negatives — full triage

| Verdict | Count | Meaning |
|---|---|---|
| **REMOVE** | 23 | blocks a confirmed service, a supported manufacturer, a targeted city, or a generic the rules forbid |
| **ROUTING** | 5 | pure service phrase, intentional cross-campaign routing, sibling eligibility proved |
| **KEEP** | 60 | competitor company/person name, supply house or out-of-area place — correct as-is |

Full row-level table with metrics, scope reason, collision results and live dedupe status:
`reports/ambient-cooling-heating/evidence/2026-09-09-negative-triage.csv`

The highest-impact REMOVE rows:

| Match | Negative | Converting terms killed | Primary conv at risk | All conv at risk | BOFU probes blocked | Reason |
|---|---|---|---|---|---|---|
| BROAD | `commercial` | 7 | **3.83** | 10.83 | 1 | forbidden generic; blocks `commercial ac repair near me` (1 primary conv) and `commercial hvac companies near me` (1) |
| BROAD | `carrier` | 5 | 0.0 | 5.0 | 1 | supported manufacturer |
| BROAD | `daikin` | 3 | 0.0 | 4.0 | 0 | supported manufacturer |
| BROAD | `trane` | 2 | 0.0 | 2.0 | 1 | supported manufacturer |
| BROAD | `thermostat` | 1 | 0.0 | 1.0 | 1 | confirmed Ambient service |
| BROAD | `mitsubishi` | 1 | 0.0 | 1.0 | 1 | supported manufacturer |
| PHRASE | `humidifier` | 1 | 0.0 | 1.0 | 1 | confirmed Ambient service |
| PHRASE | `dehumidifier` | 1 | 0.0 | 1.0 | 1 | confirmed Ambient service |
| PHRASE | `licensed` | 0 | 0 | 0 | 1 | forbidden generic; blocks `licensed hvac contractor near me` |
| PHRASE | `free` | 0 | 0 | 0 | 1 | forbidden generic; blocks `hvac free estimate near me`, an approved Ambient offer |
| BROAD | `lennox` / `goodman` / `rheem` | 0 | 0 | 0 | 1 each | supported manufacturers |
| PHRASE | `savage` | 0 | 0 | 0 | 300 grid probes | **Savage, Maryland is live target geoTargetConstants/1018704** |

The 5 ROUTING negatives, each with sibling eligibility proved:

| Match | Negative | Blocked in | Still servable in | Conv the term produced |
|---|---|---|---|---|
| EXACT | `hvac repair near me` | HVAC Installation | **HVAC Repair** ✅ | 5 primary |
| EXACT | `hvac ductwork installation near me` | HVAC Replacement | **HVAC Installation** ✅ | 2 primary |
| EXACT | `ac replacement near me` | AC Repair | **HVAC Replacement** ✅ | 0 |
| EXACT | `furnace replacement near me` | HVAC Repair | **HVAC Replacement** ✅ | 0 |
| EXACT | `tankless water heater installation near me` | all five | none of the five | 0 |

**Orphan check: of the 81 colliding converting terms, 0 produced a primary conversion and are
blocked in all five campaigns.** `tankless water heater installation near me` is blocked
everywhere but has never converted; it is a legacy-campaign service and is left as-is.

### 7.2 Geo × service sweep — 22,500 probes

Every one of 20 BOFU services × 75 live target places × 3 phrasings, per campaign:

| Campaign | Probes blocked | % |
|---|---|---|
| AC Repair | 60 / 4,500 | 1.33% |
| Gas Boiler Repair | 60 / 4,500 | 1.33% |
| HVAC Installation | 61 / 4,500 | 1.36% |
| HVAC Repair | 60 / 4,500 | 1.33% |
| HVAC Replacement | 60 / 4,500 | 1.33% |

Responsible negatives: PHRASE `savage` (300 of the 301 hits) and EXACT
`hvac repair pasadena md` in HVAC Installation (1 hit, correct routing — it serves in HVAC Repair).
Aside from `savage`, geographic coverage is clean.

### 7.3 Single-word BROAD dictionary test

470 distinct BROAD negative texts across the five (466 single-word). Only three are common
English or corporate-suffix words: `corp`, `inc`, `ltd`. All three blocked **0 of 22,500**
service × place probes and are retained as entity markers.

### 7.4 The residue (20 rows, $104.92)

18 HOLD + 2 NEGATIVE_CANDIDATE. Six became the additions in §6.3. The rest were deliberately
left live:

- `hvac annapolis md`, `hvac in annapolis md`, `maryland hvac`, `hvac baltimore` — in-footprint
  service queries. Keep.
- `air condition service`, `hvac mechanic`, `replacing hvac`, `hvac near` — generic service
  intent. Keep.
- `hvac companies with payment plans` — 1 impression, 0 clicks. Held pending a financing answer
  (§18, question 3).

---

## 8. Anomalous positive-keyword plan — RESOLVED, NO PLAN REQUIRED

**The brief's premise does not hold against the live account. The 79 keywords no longer exist.**

The fresh read finds **21 positive keyword rows total inside the five campaigns**:

| State | Count |
|---|---|
| Servable (criterion ENABLED × ad group ENABLED × campaign ENABLED) | **10** — exactly 2 per campaign, Phrase + Exact |
| Criterion ENABLED inside REMOVED ad group 202339087874 | 2 — `hvac replacement near me`, cannot serve |
| Criterion REMOVED inside ENABLED ad group 202339087634 | 9 — the competitor keywords |

Account-wide, 675 criteria are ENABLED but only **10 are servable**; the other 665 sit in PAUSED
or REMOVED parents.

Change history resolves it exactly:

- **2026-08-31 18:21** — the owner created 77 positive keywords in HVAC Installation and 2 in
  HVAC Replacement via the Google Ads UI (`GOOGLE_ADS_WEB_CLIENT`).
- **2026-09-01 13:00** — the owner removed all 79, also via the UI. They existed for **~19 hours**.

Their measured lifetime cost, from `keyword_view`, is far below the brief's $97.39 figure:

| Keyword | Impr. | Clicks | Cost | Conv |
|---|---|---|---|---|
| `[ars heating and cooling reviews]` | 5 | 1 | $44.18 | 0 |
| `[5 star plumbing heating and cooling]` | 10 | 0 | $0.00 | 0 |
| `[arundel heating and cooling maryland]` | 7 | 0 | $0.00 | 0 |
| `[arundel cooling and heating reviews]` | 6 | 0 | $0.00 | 0 |
| `[ars hvac]` | 4 | 0 | $0.00 | 0 |
| `[michael and son hvac]` | 1 | 0 | $0.00 | 0 |
| `[apex heating and cooling frostburg md]` | 1 | 0 | $0.00 | 0 |
| **Total** | **34** | **1** | **$44.18** | **0** |

`[hvac capacitor replacement near me]` and `[midea hvac distributor near me]` do not exist as
criteria anywhere in the account, in any status.

**No pause plan is drafted. Drafting one would propose pausing keywords that are already
REMOVED.** `[hvac installers near me]` and every other legitimate service keyword are intact and
serving. Every other active positive keyword in the account was inspected for company-name,
out-of-area or research-only intent: none of the 10 servable keywords shows any.

One consequence for the negative plan: because the competitor positives are gone, the two
`arundel cooling and heating` search-term rows are now free to be negatived without creating a
positive/negative conflict. That is why they appear in §6.3.

---

## 9. Harmful current-negative removal plan

Two packages, because the harm sits at two layers and **campaign-level removal cannot override
the account-level list**.

### 9.1 `AMB-0909-NEG-RM-1` — campaign level — 89 operations — fingerprint `CE289F3508A2`

22 distinct negative texts across five campaigns:

| Campaign | Removals | Negatives before → after |
|---|---|---|
| AC Repair | 15 | 1,136 → 1,121 |
| Gas Boiler Repair | 15 | 1,132 → 1,117 |
| HVAC Installation | 22 | 1,435 → 1,413 |
| HVAC Repair | 15 | 1,138 → 1,123 |
| HVAC Replacement | 22 | 1,319 → 1,297 |

By match type: BROAD 14, PHRASE 25, EXACT 50.

### 9.2 `AMB-0909-NEG-RM-2` — ACCOUNT level — 18 operations — fingerprint `A435FA09AC97`

Shared set 11252984411: **272 → 254 members**.

This package exists because of a property of the API that is easy to miss and that this audit
verified directly: account-level negatives live in a `shared_set` of type
`ACCOUNT_LEVEL_NEGATIVE_KEYWORDS`. They **never appear in `campaign_shared_set`**, the API
reports `member_count = 0` for the set, and **a campaign-level removal does not override them**.
`carrier`, `trane`, `lennox`, `goodman`, `rheem`, `mitsubishi` and `daikin` exist at *both*
layers; `commercial`, `thermostat`, `thermostats`, `al`, `american`, `mr`, `amana`, `armstrong`,
`bosch`, `bryant` and `ruud` exist **only** at the account layer.

> **Dependency: RM-1 and RM-2 must both be approved for the manufacturer unblock to take effect.
> Approving only one leaves the block in place at the other layer.**

**Scope proof.** The list governs all 23 non-removed campaigns. 5 are ENABLED (the five in scope)
and 18 are PAUSED and cannot serve. Removal therefore changes live delivery only on the five.

`al`, `american` and `mr` are named explicitly in the Green Marketing operating instructions as
words that must never be broad-negatived. `american` additionally blocks American Standard, a
supported manufacturer.

### 9.3 Legacy shared lists — audited, correctly not attached

None of the 16 other shared negative lists is attached to any of the five campaigns, and none
should be. Confirmed against the brief's warning:

| Set | Name | Members | BOFU probes it would block | Live positives it would block |
|---|---|---|---|---|
| 11813144900 | General List | 1,111 | contains BROAD `repair` | **would block `ac repair near me`, `hvac repair near me`, `gas boiler repair`** |
| 12091293463 | Ambient - Neg Kwd List | 968 | service-area and value-intent terms | — |
| 10720232972 | General | 1,148 | — | — |
| 10664304544 | Names List | 486 | — | — |
| 10664309518 | States List | 48 | — | — |

**No list is proposed for attachment.**

---

## 10. Keyword Planner

Run against the live footprint, Google Search network only (Search Partners excluded), English.
`KeywordPlanIdeaService` caps `geo_target_constants` at 10, so 10 of the 75 live targets were
sampled — the largest population centres in the live set, not an alphabetical truncation.

**Geo inputs used:** Severn, Severna Park, Annapolis, Glen Burnie, Ellicott City, Laurel,
Catonsville, Bowie, Odenton, Pasadena — all Maryland.
**Export timestamp:** 2026-09-09 America/New_York. Full export:
`reports/ambient-cooling-heating/evidence/2026-09-09-keyword-planner.json`

| Seed set | Ideas returned | Seed-only monthly searches | Seed top-of-page LOW | Seed top-of-page HIGH |
|---|---|---|---|---|
| AC repair | 2,065 | 1,330 | $16.29 – $21.12 | $92.65 – $96.33 |
| HVAC / heating repair | 2,473 | 1,360 | $6.36 – $23.49 | $72.06 – $131.66 |
| New HVAC installation | 2,423 | 610 | $3.56 – $23.49 | $17.50 – $93.02 |
| HVAC / AC / furnace replacement | 2,252 | 280 | $2.46 – $8.30 | $19.42 – $65.86 |
| **Gas boiler repair** | 1,008 | **100** | **$0.00** | **$0.00** |

Core terms in detail:

| Keyword | Monthly searches | Competition | Index | TOP low | TOP high |
|---|---|---|---|---|---|
| `hvac company near me` | 480 | HIGH | 94 | $23.49 | $93.02 |
| `ac repair` | 590 | LOW | 23 | $16.29 | $93.43 |
| `ac repair near me` | 320 | HIGH | 79 | $21.12 | $96.33 |
| `hvac near me` | 320 | HIGH | 88 | $18.49 | $100.00 |
| `hvac repair` | 210 | MEDIUM | 34 | $31.44 | $138.86 |
| `hvac repair near me` | 110 | HIGH | 78 | $14.87 | $97.88 |
| `hvac installation near me` | 50 | HIGH | 86 | — | — |
| `furnace replacement near me` | 70 | LOW | 17 | — | — |
| `boiler repair near me` | **20** | MEDIUM | 33 | — | — |
| `gas boiler repair` | **10** | LOW | 0 | — | — |

**Two conclusions.**
Google's own top-of-page LOW for Ambient's core terms is **$14.87 – $23.49**. The live ceilings
of $25 and $30 sit barely above that floor and far below the $93 – $100 HIGH — which is why the
campaigns stopped entering auctions at all.
Gas Boiler Repair has **no meaningful demand in this footprint**: 20 monthly searches at the best
term and no bid estimate at all. Planner figures are estimates, not a bid decision on their own.

**Caution recorded:** synonyms share one volume bucket (`ac repair`, `air conditioner repair`,
`ac fix`, `aircon repair` all read 590). Summing raw idea rows overstates demand by roughly 10×.
The "seed-only" totals above are already de-duplicated to the seed set.

---

## 11. Auction Insights — UNAVAILABLE, with the exact reason

**Auction Insights cannot be read through this API connection.** The metrics
(`metrics.auction_insight_search_impression_share`, `..._overlap_rate`,
`..._position_above_rate`, `..._top_impression_percentage`,
`..._absolute_top_impression_percentage`, `..._outranking_share`) and the segment
`segments.auction_insight_domain` all pass `GoogleAdsFieldService` as `selectable: true`, but
every query returns `PERMISSION_DENIED` with the literal detail
*"The developer doesn't have access to metrics: 'auction_insight_search_impression_share'."*

This fails identically at customer, campaign, ad-group and `keyword_view` level, with and without
a date filter, and on a single-metric SELECT. **The cause is the developer-token tier (Basic
access), not the query.** No amount of query rewriting will retrieve it.

**Competitor pressure is therefore assessed from the substitutes that are available**, and no
causal claim is made from any of them alone:

| Campaign | Search IS | Lost IS (rank) | Lost IS (budget) | Top IS | Abs top IS |
|---|---|---|---|---|---|
| AC Repair | 47.77% | **45.88%** | 6.36% | 26.42% | 22.24% |
| HVAC Installation | 36.51% | 10.32% | **53.16%** | 26.99% | 17.16% |
| HVAC Repair | 33.87% | **57.33%** | 8.80% | 19.91% | 15.47% |
| HVAC Replacement | 54.46% | 45.54% | 0.00% | 33.66% | 24.75% |
| Gas Boiler Repair | 51.61% | 48.39% | 0.00% | 32.26% | 29.03% |

**To obtain Auction Insights, export it from the Google Ads UI** (Campaigns → Insights and
reports → Auction insights), campaign and ad-group scope, last full month and last 30 days.
Privacy thresholds will suppress ad-group rows for Gas Boiler Repair and HVAC Replacement, whose
impression counts (34 and 199 all time) are far below the reporting minimum.

---

## 12. CPC, economics, rank/budget loss, Quality Score and bid strategy

### 12.1 Settled performance

All-time = launch-to-date. 2026-08-14 → 2026-09-08.

| Campaign | Impr | Clicks | CTR | CPC | Cost | Primary conv | Raw CVR | Raw CPA | All conv |
|---|---|---|---|---|---|---|---|---|---|
| AC Repair | 879 | 29 | 3.30% | **$106.37** | $3,084.87 | 5 | 17.2% | **$616.97** | 26 |
| HVAC Installation | 3,419 | 112 | 3.28% | $26.02 | $2,914.33 | 3 | 2.7% | $971.44 | 26 |
| HVAC Repair | 1,058 | 29 | 2.74% | **$67.31** | $1,951.94 | 6 | 20.7% | **$325.32** | 25 |
| HVAC Replacement | 199 | 5 | 2.51% | $30.50 | $152.52 | 0 | 0% | — | 0 |
| Gas Boiler Repair | 34 | 0 | 0% | — | $0.00 | 0 | — | — | 0 |
| **Total** | **5,589** | **175** | **3.13%** | **$46.31** | **$8,103.66** | **14** | **8.0%** | **$578.83** | **77** |

### 12.2 CPC distribution — 116 clicks, settled

| Campaign | n | min | p25 | median | p75 | p90 | p95 | max | mean |
|---|---|---|---|---|---|---|---|---|---|
| AC Repair | 25 | $23.01 | $81.66 | **$109.87** | $141.92 | $178.37 | $242.46 | $267.96 | $114.90 |
| HVAC Installation | 62 | $11.06 | $19.10 | $22.88 | $29.67 | $50.02 | $58.40 | $62.13 | $27.54 |
| HVAC Repair | 25 | $6.16 | $27.60 | $56.41 | $101.27 | $151.29 | $153.03 | $153.06 | $72.66 |
| HVAC Replacement | 4 | $15.02 | $24.92 | $32.67 | $40.26 | $45.92 | $47.80 | $49.69 | $32.51 |
| **All five** | **116** | $6.16 | $21.17 | $29.38 | $71.34 | $141.07 | $153.04 | $267.96 | $56.26 |

**BOFU non-competitor queries only** (the 65 clicks whose search term classified KEEP_BOFU or
KEEP_TEST; the other 51 clicks are 47 ALREADY_COVERED, 3 HOLD and 1 NEGATIVE_CANDIDATE):

| Campaign | n | p25 | median | p75 | p90 | max |
|---|---|---|---|---|---|---|
| AC Repair | 23 | $88.61 | **$112.63** | $141.92 | $182.37 | $267.96 |
| HVAC Installation | 18 | $19.10 | $27.01 | $56.66 | $59.58 | **$62.13** |
| HVAC Repair | 23 | $53.52 | **$61.91** | $108.06 | $152.16 | $153.06 |
| HVAC Replacement | 1 | — | $49.69 | — | — | $49.69 |
| **All five** | **65** | $27.60 | **$61.91** | $114.86 | $153.03 | $267.96 |

Stripping competitor and already-blocked traffic makes the picture **worse, not better**, which
matters for the ceiling decision: qualified BOFU demand is the expensive demand. AC Repair's BOFU
median rises from $109.87 to $112.63 and HVAC Repair's from $56.41 to $61.91. Two numbers here
drive the recommendations in §13 directly: HVAC Installation's BOFU maximum is **$62.13** (the
proposed $65 ceiling clears it), and HVAC Repair's BOFU median is **$61.91** (the proposed $60
ceiling sits right at it).

### 12.3 CPCs that actually produced conversions

**Primary conversions (10 rows):** $6.16, $59.44, $59.92, $68.16, $93.09, $109.87, $112.63,
$140.13, $153.03, $153.06.
**All-conversions (31 rows):** min $6.16, p25 $27.16, median $59.44, p75 $109.66, p90 $153.03,
max $186.37.

The brief cites $68.16–$153.06. The fresh read widens that to **$6.16–$153.06** with a median
around $101. **Nine of the ten converting clicks cost more than $25.** A $25 ceiling would have
prevented nine of the fourteen conversions this account has ever recorded.

### 12.4 Segmentation

**Device.** Mobile 126 clicks / $6,454.80 / CPC $51.23 / **14 of 14 primary conversions**.
Desktop 49 clicks / $1,648.85 / CPC $33.65 / **0 conversions**. Every conversion this account has
produced came from a mobile click.

**Click type.**

| Click type | Impr | Clicks | CPC | Cost | Primary conv | All conv |
|---|---|---|---|---|---|---|
| URL_CLICKS | 5,589 | 99 | $40.80 | $4,039.03 | 5 | 28.5 |
| **LOCATION_EXPANSION** | 2,937 | 34 | $58.92 | $2,003.44 | **4** | **35.0** |
| SITELINKS | 1,595 | 26 | $49.42 | $1,284.80 | 1 | 2.5 |
| **CALLS** | 1,698 | 10 | $57.65 | $576.51 | **4** | 4.0 |
| GET_DIRECTIONS | 335 | 6 | $33.31 | $199.88 | 0 | 7.0 |

`LOCATION_EXPANSION` carries 4 of 14 primary conversions and 35 of 77 all-conversions. **It is
not waste and must not be excluded.** `CALLS` is the most efficient click type by conversion
rate: 10 clicks, 4 primary conversions.

**Day of week.** Thursday is the largest ($1,645.03) and Saturday the most expensive
(CPC $64.18). Sunday: 65 impressions, 1 click — consistent with no Sunday ad-schedule row.

**Hour.** 10:00 is the strongest hour (22 clicks, 22 all-conversions). 09:00 is the most
expensive ($71.86 CPC, 5 all-conversions). Hours 20:00–07:00 produce almost nothing, consistent
with the approved schedule.

**Network.** Google Search only. Search Partners and Display confirmed off on all five.

**Top vs other.** Absolute-top impression share 15–29% across the five — the campaigns are
mostly *not* winning the top slot even at $106 CPCs, which is a Quality Score signal, not a bid
signal.

### 12.5 Quality Score

| Campaign | Keyword | QS | Expected CTR | Ad relevance | Landing page |
|---|---|---|---|---|---|
| AC Repair | `ac repair near me` (P+E) | **4** | BELOW_AVERAGE | AVERAGE | AVERAGE |
| HVAC Repair | `hvac repair near me` (P+E) | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** |
| HVAC Replacement | `hvac replacement near me` (P+E) | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** |
| HVAC Installation | `hvac installers near me` (P+E) | — | insufficient data | — | — |
| Gas Boiler Repair | `gas boiler repair` (P+E) | — | insufficient data | — | — |

Position estimates (`first_page_cpc`, `top_of_page_cpc`, `first_position_cpc`) all return $0.00 —
Google does not populate them under automated bidding.

**Expected CTR is BELOW_AVERAGE on every scored keyword.** That is the mechanical cause of the
high CPCs: low Ad Rank forces a higher bid to reach the same position. Landing-page experience is
BELOW_AVERAGE on HVAC Repair and HVAC Replacement.

### 12.6 The `hvac installers` episode — the largest single waste finding

| Window | Clicks | Cost | CPC | Primary conv | CPA | Max CPC |
|---|---|---|---|---|---|---|
| `hvac installers` live, 08-14 → 08-28 | 53 | $1,281.93 | $24.19 | **0** | — | $54.43 |
| swapped to `hvac installers near me`, 08-29 → 09-03 | 9 | $425.61 | $47.29 | **3** | **$141.87** | $62.13 |
| after the 09-04 ceiling, 09-05 → 09-08 | **0** | $0.00 | — | 0 | — | — |

Across its whole life the PHRASE keyword `hvac installers` took **102 clicks and $2,430.35 with
zero primary conversions** — 30% of everything the account has ever spent. It also generated
**530 of the 988 CSV rows (53.6%)**: a two-word phrase with no geographic anchor and no service
qualifier is exactly what produces query pollution. The owner replaced it on 2026-08-28.

**Six days later, the configuration that finally worked was capped at $30 and stopped delivering.**

### 12.7 Economic CPC — scenario bands

`economic CPC = maximum acceptable CPQL × qualified conversion rate`

**Qualified CVR is UNKNOWN.** `WHATCONVERTS_API_TOKEN` is present in `.env` but empty; no CRM
credential is configured. Bands apply an assumed qualification rate to the observed raw primary
CVR. These are labelled assumptions, not measurements.

| Campaign | Raw primary CVR | Max CPQL | Conservative (40%) | Base (60%) | Optimistic (80%) | Observed CPC |
|---|---|---|---|---|---|---|
| AC Repair | 20.00% | $150 | $12.00 | $18.00 | $24.00 | **$114.90** |
| HVAC Repair | 16.00% | $250 | $16.00 | $24.00 | $32.00 | **$72.66** |
| HVAC Installation | 4.84% | $280 | $5.42 | $8.13 | $10.84 | $27.54 |
| HVAC Replacement | 0.00% | $280 | $0.00 | $0.00 | $0.00 | $32.51 |
| Gas Boiler Repair | no clicks | $250 | — | — | — | — |

HVAC Installation's 4.84% is contaminated by the `hvac installers` clicks. On the post-swap
window alone the raw CVR is **33.3%** (3 conversions / 9 clicks), which moves its economic CPC
band to **$37.30 conservative / $55.94 base / $74.59 optimistic** — but on a 9-click sample. Both
figures are stated; neither is reliable alone. Note that the post-swap band brackets the
campaign's observed BOFU maximum CPC of $62.13, which is the strongest single argument for the
$65 ceiling proposed in §13.

### 12.8 Bid strategy

**Keep Maximize Clicks (TARGET_SPEND) on all five. Do not move to Maximize Conversions or
Target CPA.** The account has 14 primary conversions in 26 days across five campaigns, and its
conversion configuration is not yet trustworthy for Smart Bidding (§14.4). Recent, correctly
configured, qualified conversion volume is not sufficient, and offline/qualified outcomes are not
being imported (`WC Calls` has recorded zero all-conversions since launch).

No bid-strategy experiment is proposed this run. The prerequisite is a working qualified-lead
feed, not a different algorithm.

**No advanced call bid adjustment is proposed.** Calls are the most efficient click type
(10 clicks → 4 primary conversions), which is tempting, but the brief's own bar has not been
cleared: live call answer coverage, minimum duration behaviour, duplicate handling and
qualified/sold outcomes are all unverified, and the `Calls from ads` action's 60-second threshold
is a duration rule, not proof of qualification.

---

## 13. Campaign-specific CPC-ceiling table

Modelled from the 116 actual clicks in the settled window. A click "survives" a cap if its
observed CPC was at or below it. Because Maximize Clicks would re-auction some of these, survival
is an **upper bound on loss**, not a point estimate.

### AC Repair — baseline 25 clicks, $2,872.48, 5 conversions, CPC $114.90 — **live ceiling $25**

| Cap | Clicks kept | Spend kept | Conv kept | Modelled CPA | Modelled CPC | Confidence |
|---|---|---|---|---|---|---|
| **$25 (live)** | 12.0% | 2.5% | **0 of 5** | — | $23.60 | HIGH |
| $40 | 20.0% | 4.5% | 0 of 5 | — | $25.87 | HIGH |
| $75 | 24.0% | 6.9% | 1 of 5 | $197.51 | $32.92 | MEDIUM |
| $110 | 52.0% | 31.2% | 3 of 5 | $298.35 | $68.85 | MEDIUM |
| $130 | 60.0% | 39.2% | 4 of 5 | $281.19 | $74.98 | LOW |
| $160 | 80.0% | 63.7% | 5 of 5 | $365.82 | $91.45 | LOW |
| none | 100% | 100% | 5 of 5 | $574.50 | $114.90 | HIGH |

**Recommendation: HOLD at $25, deliberately, and treat AC Repair as suspended pending Quality
Score and landing-page work.**
No cap makes AC Repair profitable. The cheapest cap that retains even one conversion is $75 at a
$197.51 CPA; the cheapest that retains a majority is $110 at $298.35 — both against a **$150
maximum acceptable CPQL**, and both are raw CPAs, so the true CPQL is higher still. Raising this
ceiling buys traffic that is proven to lose money. The honest reading is that AC Repair in this
footprint, at Quality Score 4 with BELOW_AVERAGE expected CTR, cannot clear a $150 CPQL. That is
a business decision, not a bid decision — see question 1 in §18.

### HVAC Repair — baseline 25 clicks, $1,816.59, 4 conversions, CPC $72.66 — **live ceiling $25**

| Cap | Clicks kept | Spend kept | Conv kept | Modelled CPA | Modelled CPC | Confidence |
|---|---|---|---|---|---|---|
| $25 (live) | 24.0% | 6.4% | 1 of 4 | $116.67 | $19.45 | HIGH |
| $40 | 28.0% | 7.9% | 1 of 4 | $144.27 | $20.61 | HIGH |
| **$60 — RECOMMENDED** | **52.0%** | **26.1%** | 1 of 4 | $474.06 | **$36.47** | MEDIUM |
| $90 | 72.0% | 46.5% | 1 of 4 | $845.57 | $46.98 | MEDIUM |
| $160 / none | 100% | 100% | 4 of 4 | $454.15 | $72.66 | HIGH |

**Recommendation: raise to $60.**
Read the conversion column carefully — it is misleading here. Three of HVAC Repair's four
conversions arrived on 2026-08-20 and 2026-08-25 at CPCs of $153.03, $153.06 and $148.67, on days
when the campaign took 1–2 clicks total. Those are not a reproducible $153 price point; they are
a thin tail. The median CPC is $56.41 and Google's top-of-page LOW for the core term is $14.87.
$60 restores roughly half the click volume at a $36.47 blended CPC — inside the optimistic
economic band ($32) and close enough to justify while the Quality Score 2 / BELOW_AVERAGE
landing-page problem is fixed.

### HVAC Installation — baseline 62 clicks, $1,707.54, 3 conversions, CPC $27.54 — **live ceiling $30**

| Cap | Clicks kept | Spend kept | Conv kept | Modelled CPA | Modelled CPC | Confidence |
|---|---|---|---|---|---|---|
| $25 | 53.2% | 35.1% | **0 of 3** | — | $18.19 | HIGH |
| **$30 (live)** | 75.8% | 57.8% | **0 of 3** | — | $21.01 | HIGH |
| $50 | 88.7% | 76.5% | 0 of 3 | — | $23.74 | HIGH |
| $60 | 98.4% | 96.4% | **3 of 3** | $548.47 | $26.97 | HIGH |
| **$65 — RECOMMENDED** | **100%** | **100%** | **3 of 3** | $569.18 | $27.54 | HIGH |
| none | 100% | 100% | 3 of 3 | $569.18 | $27.54 | HIGH |

**Recommendation: raise to $65. This is the highest-confidence change in the audit.**
All three conversions came from clicks costing between $50 and $62.13. The live $30 ceiling
excludes every one of them while still admitting 76% of the (unconverting) click volume — the
worst of both outcomes. The $569.18 CPA in the table is dragged down by the `hvac installers`
waste; on the post-swap window alone the CPA is **$141.87 against a $280 max CPQL**. $65 covers
the highest observed converting CPC ($62.13) with headroom and leaves the ceiling non-binding.

### HVAC Replacement — baseline 4 clicks, $130.05, 0 conversions — **uncapped**

**Recommendation: HOLD, no ceiling.** Four clicks is not a sample. Routing, relevance and landing
experience come first: Quality Score is 2 with BELOW_AVERAGE landing-page experience, and Keyword
Planner puts replacement demand at 280 seed searches/month with a $2.46–$8.30 top-of-page low.

### Gas Boiler Repair — 0 clicks all time — **uncapped**

**Recommendation: HOLD, no ceiling, and do not enable the Gas Boiler keyword package.**
Zero clicks in 26 days. Keyword Planner returns 20 monthly searches at the best boiler term
across the 10-city sample and no bid estimate at all. The landing page still fails its service
gate (§14.3). Inventing a CPC ceiling here would be fitting a number to no data.

### Summary

| Campaign | Live | Proposed | Action | Confidence |
|---|---|---|---|---|
| HVAC Installation | $30 | **$65** | RAISE | HIGH |
| HVAC Repair | $25 | **$60** | RAISE | MEDIUM |
| AC Repair | $25 | **$25** | **HOLD (deliberate)** | HIGH |
| HVAC Replacement | none | none | HOLD | HIGH |
| Gas Boiler Repair | none | none | HOLD | HIGH |

---

## 14. CTR, RSA, assets and landing pages

Diagnosed in the order the brief specifies: query pollution → rank → irrelevant positives → ad
copy → assets.

### 14.1 Query pollution — largely resolved

Account CTR is 3.13%. The dominant historical cause of low CTR was `hvac installers` (§12.6),
now removed. 44% of visible search-term rows are already negatived. Pollution is no longer the
binding constraint on CTR.

### 14.2 Rank and relevance — the current binding constraint

Expected CTR is BELOW_AVERAGE on **every scored keyword**, and absolute-top impression share is
15–29%. HVAC Repair loses 57.33% of impressions to rank. This is where CTR improvement has to
come from, not from headline edits alone.

### 14.3 RSA and policy audit

20 ad rows on the five campaigns: 14 ENABLED, 6 PAUSED.

| Campaign | Ad | Status | Approval | Strength | Final URL |
|---|---|---|---|---|---|
| AC Repair | 820900825416 | ENABLED | APPROVED | AVERAGE | /ac-repair/ |
| AC Repair | 820900825419 | ENABLED | APPROVED | AVERAGE | /ac-repair/ |
| AC Repair | 820900825422 | ENABLED | AREA_OF_INTEREST_ONLY | AVERAGE | /hvac-replacement/ ⚠ |
| AC Repair | 820900825425 | ENABLED | AREA_OF_INTEREST_ONLY | POOR | /hvac-replacement/ ⚠ |
| Gas Boiler | 821319509209 / 212 | ENABLED | APPROVED | EXCELLENT | /gas-boiler-repair/ |
| Gas Boiler | 820900825428 / 431 | PAUSED | DISAPPROVED | EXCELLENT | /gas-boiler-repair/ |
| **HVAC Installation** | **820900825434** | **ENABLED** | **DISAPPROVED** | POOR | /hvac-installation/ |
| HVAC Installation | 821319509197 | ENABLED | APPROVED | POOR | /hvac-installation/ |
| HVAC Installation | 821319509200 | ENABLED | APPROVED | EXCELLENT | /hvac-installation/ |
| HVAC Installation | 820900825437 | PAUSED | DISAPPROVED | EXCELLENT | /hvac-installation/ |
| HVAC Repair | 821714108336 / 339 | ENABLED | APPROVED | EXCELLENT | /hvac-repair/ |
| HVAC Repair | 820900825560 / 563 | PAUSED | APPROVED | POOR / AVERAGE | /hvac-repair/ |
| **HVAC Replacement** | **820944944368** | **ENABLED** | **DISAPPROVED** | POOR | /hvac-replacement/ |
| HVAC Replacement | 821319509203 | ENABLED | APPROVED | GOOD | /hvac-replacement/ |
| HVAC Replacement | 821319509206 | ENABLED | APPROVED | EXCELLENT | /hvac-replacement/ |
| HVAC Replacement | 820944944371 | PAUSED | DISAPPROVED | POOR | /hvac-replacement/ |

Every non-approved ad carries policy topic **`CONSUMER_FINANCE`**, `review_status = REVIEWED`.

**Two live defects:**
1. Ads **820900825434** (HVAC Installation) and **820944944368** (HVAC Replacement) are ENABLED
   but DISAPPROVED / FULLY_LIMITED. They cannot serve. → package `AMB-0909-ADS-1`.
2. The two `/hvac-replacement/` ads inside AC Repair (820900825422 / 825425) point at the wrong
   landing page — but they sit in **REMOVED ad group 202339087874** and cannot serve.
   **No operation is needed and none is proposed.**

Every ENABLED ad has 15 headlines and 4 descriptions, and **zero pinned headlines** — correct.
After the two pauses, each live ad group still runs two ENABLED APPROVED RSAs, satisfying agency
policy.

**No RSA copy rewrite is proposed this run.** With expected CTR BELOW_AVERAGE and 175 lifetime
clicks, there is not enough traffic to attribute a copy change, and the delivery outage makes any
before/after unreadable. Copy work should follow the ceiling fix, once impressions resume.
Claims are already compliant: zero barred claims found on any page (§14.4), and the approved
baseline claims remain same-day service, free estimates, licensed and insured, and verified
rating facts.

### 14.4 Landing pages — real browser, desktop + mobile

Playwright Chromium, JavaScript enabled, GET navigations only. No form submitted, no `tel:` link
activated. (These pages sit behind SG-Captcha, which feeds non-JS clients an empty stub; a plain
fetch produces a false "no tracking" result.)

| Page | HTTP | H1 correct | Three-step heading | Verdict |
|---|---|---|---|---|
| /ac-repair/ | 200 | ✅ | "Request AC Repair in 3 Simple Steps" | ✅ correct service |
| /hvac-repair/ | 200 | ✅ | "Request HVAC Repair in 3 Simple Steps" | ✅ correct service |
| /hvac-installation/ | 200 | ✅ | "Your HVAC Installation in 3 Simple Steps" | ✅ |
| /hvac-replacement/ | 200 | ✅ | "Your HVAC Replacement in 3 Simple Steps" | ✅ |
| **/gas-boiler-repair/** | 200 | ✅ | **"Your HVAC Replacement in 3 Simple Steps"** | ❌ **GATE FAIL** |

**Correction to the automated checker:** it flags AC Repair and HVAC Repair as failures because
it tests for the literal string "Your …". Both pages name the correct service and read
"Request AC Repair…" / "Request HVAC Repair…". Those are **not** defects. **Gas Boiler Repair is
the only genuine service mismatch**, and it is unchanged since 2026-08-21.

> **The Gas Boiler keyword package stays BLOCKED** while `/gas-boiler-repair/` says
> "Your HVAC Replacement in 3 Simple Steps".

Tracking and phone architecture, verified on all five pages:

| Item | Observed |
|---|---|
| Displayed paid number | (410) 705-6354 ✅ approved |
| `tel:` href | +14109141456 (WhatConverts DNI) — intentional per work order ✅ |
| Main-site number (410) 761-0932 | **not present** ✅ |
| Unexplained number (410) 415-9517 | **not present** ✅ |
| GTM container | GTM-PQTPQ436 ✅ |
| Google Ads tag | AW-11155434808 ✅ matches `conversion_tracking_id` |
| GA4 | G-9X9ZHNCRWF ✅ |
| WhatConverts script | present ✅ |
| `wc_swap` cookie | present ✅ |
| GCLID in storage | ✅ captured |
| ClickCease script on page | **absent** — blocking happens at the `monitor.clickcease.com` redirect, before the page |
| Barred claims | **0 on all five pages** ✅ |
| **Privacy / Terms link** | **absent on all five pages** ⚠ |
| Duplicate DOM ids | 25 per page (Divi + Gravity Forms duplication across the 3 form instances) ⚠ |
| Mobile horizontal overflow | none ✅ |

**Recommendations (developer handoff, no live change in this run):**
1. Fix the `/gas-boiler-repair/` three-step heading to "Your Gas Boiler Repair in 3 Simple Steps".
2. Add Privacy Policy and Terms links to all five page footers — a trust element and a standard
   policy expectation for lead forms.
3. Resolve the 25 duplicate DOM ids; three form instances sharing `gform_1` / `input_1_*` is a
   real risk to form-submission tracking and to accessibility.
4. Address the BELOW_AVERAGE landing-page experience on `/hvac-repair/` and `/hvac-replacement/`:
   above-the-fold service + city match, faster first contentful paint, and a visible trust row
   using only verified claims.

### 14.5 Conversion architecture — a material measurement finding

16 non-removed conversion actions; **10 are flagged `primary_for_goal = true`**, including five
Google-hosted "Local actions":

| Action | Category | Type | primary_for_goal | All conv (26 days) | Counts to `conversions`? |
|---|---|---|---|---|---|
| Local actions - Other engagements | ENGAGEMENT | GOOGLE_HOSTED | true | **33** | no |
| Local actions - Website visits | PAGE_VIEW | GOOGLE_HOSTED | true | 9 | no |
| Local actions - Directions | GET_DIRECTIONS | GOOGLE_HOSTED | true | 7 | no |
| Local actions - Menu views | PAGE_VIEW | GOOGLE_HOSTED | true | 0 | no |
| Clicks to call | CONTACT | GOOGLE_HOSTED | true | 1 | no |
| **Calls from ads** | PHONE_CALL_LEAD | AD_CALL | true | 5 | **yes — 5 primary** |
| **WC Lead** | CONTACT | UPLOAD_CLICKS | true | 8 | **yes — 4 primary** |
| **Ambient Cooling - LP -Submit Lead Forms** | SUBMIT_LEAD_FORM | WEBPAGE | true | 5 | **yes — 4 primary** |
| Ambient Cooling - Lp - Phone call leads | PHONE_CALL_LEAD | WEBSITE_CALL | true | **0** | — |
| **WC Calls** | CONTACT | UPLOAD_CALLS | true | **0** | — |

**Three things follow.**
1. `all_conversions = 77` is **not 77 leads**. 49 of the 77 are Google-hosted Local actions —
   engagements, website visits and directions. Only **14** are biddable primary conversions, and
   they come from just three actions: calls from ads (5), WhatConverts lead uploads (4) and
   landing-page form submissions (4). Never quote 77 as a lead count.
2. **`WC Calls` (UPLOAD_CALLS) has recorded zero conversions since launch.** The WhatConverts
   offline call-import path is configured but not delivering.
3. **`Ambient Cooling - Lp - Phone call leads` (WEBSITE_CALL) has recorded zero.** The
   WhatConverts DNI number swap replaces the number Google's website-call conversion watches for,
   which is the standard cause. Phone leads are therefore reaching WhatConverts but only partly
   reaching Google Ads.

No conversion-configuration mutation is proposed this run. All five campaigns bid on Maximize
Clicks, so conversion flags do not currently affect bidding, and a stale conversion already
counted is never restated — the fix is worth doing carefully, not quickly. Question 4 in §18.

---

## 15. Budget, pacing and lead forecast

### 15.1 September pacing

| | |
|---|---|
| Monthly maximum | **$13,000.00** (hard) |
| September MTD settled (09-01 → 09-08) | **$1,260.86** |
| Remaining | $11,739.14 |
| Days remaining (09-09 → 09-30) | 22 |
| Headroom per remaining day | $533.60 |
| Run rate **before** the 09-04 ceiling | $382.15/day |
| Run rate **after** the 09-04 ceiling | **$11.27/day** |

### 15.2 Month-end scenarios

| Scenario | Modelled daily | September month-end | vs $13,000 cap |
|---|---|---|---|
| **A. Do nothing** (ceilings as set) | $11.27 | **$1,508.80** | $11,491.20 unspent |
| **B. `AMB-0909-CPC-1` only — RECOMMENDED** | $186.00 | **$5,352.77** | $7,647.23 unspent |
| C. B + AC Repair raised to $130 | $273.18 | $7,270.86 | $5,729.14 unspent |
| D. Pre-ceiling behaviour fully restored | $382.15 | $9,668.19 | $3,331.81 unspent |

**Every scenario stays inside the cap.** Scenario C is modelled for completeness and **is not
recommended** — AC Repair's modelled CPA at a $130 cap is $281.19 against a $150 max CPQL.

### 15.3 Budget allocation

`AMB-0909-BUD-1` moves $5.46/day of the $37.76 released by Gas Boiler Repair to HVAC Installation
and retires the remaining $32.30:

| Campaign | Budget ID | Now | Proposed |
|---|---|---|---|
| AC Repair | 15787409435 | $141.45 | $141.45 (unchanged) |
| Gas Boiler Repair | 15787409438 | $42.76 | **$5.00** |
| HVAC Installation | 15787409441 | $176.15 | **$181.61** |
| HVAC Repair | 15787409444 | $78.95 | $78.95 (unchanged) |
| HVAC Replacement | 15787409447 | $26.32 | $26.32 (unchanged) |
| **Daily total** | | **$465.63** | **$433.33** |
| **30-day worst case** | | $13,968.90 ❌ | **$12,999.90** ✅ |

This closes a real pre-existing breach: the current budgets could in principle spend $968.90 over
the monthly maximum. HVAC Installation is the only budget-limited campaign in the account
(53.16% Search lost IS to budget vs 10.32% to rank), so it takes the transfer. AC Repair keeps
its $141.45 even though the $25 ceiling stops it spending, because cutting it would make the
deliberate ceiling hold harder to reverse — see question 2 in §18.

### 15.4 Lead forecast — Scenario B, remaining 22 days

| Campaign | Modelled spend | Clicks | Raw primary leads | Raw CPA |
|---|---|---|---|---|
| HVAC Installation | $3,053.16 | ~111 | **~5.4** | $569.01 |
| HVAC Repair | $1,038.75 | ~28 | **~4.6** | $227.94 |
| **Total** | **$4,091.91** | ~139 | **~10.0** | **$409.19** |

**Confidence: LOW-TO-MODERATE, and the range is wide.** HVAC Installation's 4.84% raw CVR is
contaminated by the removed `hvac installers` keyword. Using only the post-swap window (33.3%
CVR) the same spend models **~21 leads** — a 7× spread on a 9-click sample. Neither end is
reliable.

**Qualified leads, CPQL, sold jobs, revenue and gross profit cannot be stated.**
`WHATCONVERTS_API_TOKEN` is empty and no CRM connection is configured, so no qualification rate,
close rate or margin exists to compute them from. Lead quality is `UNKNOWN` throughout this
report and no figure has been invented for it.

### 15.5 Can the account spend $13,000/month?

**On current evidence, no — and it should not try.** The binding constraints are demand and
economics, not budget:

- Keyword Planner puts the whole BOFU seed footprint at **at most 3,680 monthly searches** across
  all five services in the 10-city sample — and that is an over-count, because several core terms
  (`hvac company near me`, `hvac near me`, `ac repair near me`) appear in more than one seed set
  and are counted more than once. The true de-duplicated figure is lower.
- At a 33% impression share and a 3.1% CTR, that supports on the order of 35–40 clicks/month at
  current relevance.
- Best case, Scenario D restores $382/day and still lands at $9,668 for September.
- AC Repair, which historically absorbed the most spend, is the campaign the economics say to
  hold back.

**Stated plainly: the $13,000 monthly target and the stated CPQL ceilings are not simultaneously
achievable at current Quality Score and demand.** Forcing spend would mean relaxing intent,
raising CPCs on proven-unprofitable traffic, or removing safeguards. None of those is proposed.
The route to more spend runs through Quality Score, landing-page experience and a working
qualified-lead feed — not through a bigger budget.

---

## 16. Validation, receipts, fingerprints, readback and rollback

### 16.1 Local preflight — 0 FAIL, 0 WARN

`scripts/ambient_0909_preflight.py`, zero API operations. It caught two real defects before any
quota was spent:

1. Two proposed EXACT negatives were **12 and 13 words**, breaching Google's 10-word
   negative-keyword limit. With `partial_failure = False` they would have failed the entire
   batch. Replaced with PHRASE `"sq ft house"` (3 words), which covers both and was re-tested
   against all 67 BOFU probes: 0 hits.
2. The budget package as first drafted left the 30-day worst case at $13,968.90 — **above the
   $13,000 maximum**. Re-sized to $433.33/day = $12,999.90.

This ordering matters: `validate_only` consumes the same daily mutate quota as a real write, and
this developer token is on Basic access (~15k operations/day).

### 16.2 Validate-only receipts — all six packages

Each package: one atomic `GoogleAdsService.mutate`, `partial_failure = false`,
`validate_only = true`. Identity gate re-run inside every call.

| Package | Fingerprint | Ops | Result | Receipt |
|---|---|---|---|---|
| AMB-0909-CPC-1 | `46C39C6B7091` | 2 | **VALIDATED_OK** | `receipts/validate-only/AMB-0909-CPC-1-2026-09-09.json` |
| AMB-0909-NEG-RM-1 | `CE289F3508A2` | 89 | **VALIDATED_OK** | `receipts/validate-only/AMB-0909-NEG-RM-1-2026-09-09.json` |
| AMB-0909-NEG-RM-2 | `A435FA09AC97` | 18 | **VALIDATED_OK** | `receipts/validate-only/AMB-0909-NEG-RM-2-2026-09-09.json` |
| AMB-0909-ADS-1 | `11A79347A296` | 2 | **VALIDATED_OK** | `receipts/validate-only/AMB-0909-ADS-1-2026-09-09.json` |
| AMB-0909-NEG-ADD-1 | `23BE8FF0F24C` | 6 | **VALIDATED_OK** | `receipts/validate-only/AMB-0909-NEG-ADD-1-2026-09-09.json` |
| AMB-0909-BUD-1 | `D448BFDE4650` | 2 | **VALIDATED_OK** | `receipts/validate-only/AMB-0909-BUD-1-2026-09-09.json` |
| | | **119** | | |

The executor (`scripts/ambient_0909_execute.py`) refuses to run unless the supplied fingerprint
matches the on-disk plan and the plan re-hashes to its own recorded fingerprint. Each package is
restricted to a single operation type by construction: the ClickCease tracking template, geo
targets, ad schedules, conversion actions, manager links and the other 16 shared sets are
unreachable from every branch.

### 16.3 Readback assertions

| Package | Assert after execution |
|---|---|
| CPC-1 | HVAC Installation ceiling = 65000000; HVAC Repair = 60000000; **AC Repair unchanged at 25000000**; all five still TARGET_SPEND; budgets, networks, geo (375), schedules (30) unchanged |
| NEG-RM-1 | ENABLED campaign negatives on the five: 6,160 → **6,071**; per campaign 1,121 / 1,117 / 1,413 / 1,123 / 1,297; 22 named texts absent; no other negative removed |
| NEG-RM-2 | Shared set 11252984411 members: 272 → **254**; the 18 named texts absent; the other 16 shared sets untouched; still 0 shared lists attached to the five |
| ADS-1 | Ads 820900825434 and 820944944368 = PAUSED; each ad group still has ≥2 ENABLED APPROVED RSAs; no other ad status changed |
| NEG-ADD-1 | HVAC Installation campaign negatives 1,435 → **1,441** (or 1,419 if RM-1 ran first); the 6 texts present with the recorded match types |
| BUD-1 | Budget 15787409438 = 5000000; 15787409441 = 181610000; other three unchanged; daily total = $433.33 |

**Unrelated-resource counts to re-assert after every package** (all verified at 2026-09-09 15:00,
post-audit):

```
campaigns non-removed        23
campaigns ENABLED             5
geo targets on the five     375
ad schedules on the five     30
IP blocks (ClickCease)     2796
shared sets                  17
conversion actions           16
manager links   3373711342 ACTIVE, 2815082755 ACTIVE
tracking_url_template      present, ClickCease
```

### 16.4 Rollback

Every operation carries an explicit inverse in its plan file.

| Package | Rollback |
|---|---|
| CPC-1 | set `target_spend.cpc_bid_ceiling_micros` back to 30000000 / 25000000 |
| NEG-RM-1 | re-create the 89 campaign negatives from the recorded text + match type + campaign id (all 89 are in the plan file) |
| NEG-RM-2 | re-add the 18 texts as BROAD members of shared set 11252984411 |
| ADS-1 | set both ad_group_ads back to ENABLED |
| NEG-ADD-1 | remove the 6 created criteria by returned resource name |
| BUD-1 | set `amount_micros` back to 42760000 and 176150000 |

If a write partially succeeds: **stop, do not rerun.** Inventory the created/removed resource
IDs from the receipt, diff against the plan, and propose a targeted recovery. `partial_failure`
is `false` on every package, so a failure should be all-or-nothing — but that must be verified by
readback, not assumed.

---

## 17. Monitoring and quantitative rollback thresholds

Baseline for all comparisons: **2026-08-14 → 2026-09-03** (before the ceiling), because
2026-09-05 → 09-08 is an outage, not a performance state.

| Checkpoint | Date | What to check |
|---|---|---|
| **24 hours** | 2026-09-10 | Delivery resumed on HVAC Installation and HVAC Repair; CPC distribution; no new disapprovals; readback counts still match §16.3 |
| **72 hours** | 2026-09-12 | Blended CPC, CTR, cost/day vs plan; any manufacturer search terms appearing after the negative removals |
| **7 settled days** | 2026-09-16 | Full search-term review of new terms; primary conversions; CPA vs max CPQL; impression-share movement |
| **14 settled days** | 2026-09-23 | Quality Score movement; September pacing vs the $13,000 cap; decision point on AC Repair |

### Rollback thresholds

| Trigger | Threshold | Action |
|---|---|---|
| HVAC Installation CPC | > $55 blended over 7 settled days | lower ceiling $65 → $50 |
| HVAC Installation CPA | > $280 raw over 14 settled days with ≥5 conversions | lower ceiling to $45 and re-evaluate |
| HVAC Repair CPC | > $50 blended over 7 settled days | lower ceiling $60 → $40 |
| HVAC Repair CPA | > $250 raw over 14 settled days with ≥4 conversions | revert to $25 pending landing-page work |
| September spend | projected month-end > $12,000 | reduce HVAC Installation budget first |
| Any campaign | 0 conversions on ≥30 clicks after 14 settled days | pause that campaign and re-audit |
| Post-removal search terms | any manufacturer term produces ≥5 clicks with 0 conversions | re-add that manufacturer as PHRASE + service qualifier, never BROAD |
| Any day | new DISAPPROVED ad appears ENABLED | pause immediately |

Thresholds use raw primary conversions because qualified outcomes are not available. **When
WhatConverts access is restored, re-derive every threshold against CPQL** — raw CPA is a proxy,
not the target.

---

## 18. Consolidated question list

Only questions that change the deliverable. Recommendations included.

**1. AC Repair economics — the one genuine business decision.**
AC Repair's raw CPA is $616.97 against a $150 maximum acceptable CPQL. No modelled CPC ceiling
closes that gap: the cheapest cap retaining a majority of conversions is $110 at a $298.35 raw
CPA. Which do you want?
&nbsp;&nbsp;(a) **Hold AC Repair at $25 (dark) while Quality Score and the landing page are fixed — RECOMMENDED**
&nbsp;&nbsp;(b) Raise the acceptable CPQL for AC Repair to a figure that reflects job value and margin
&nbsp;&nbsp;(c) Remove AC Repair from paid search and reinvest in HVAC Installation
*If unanswered:* AC Repair stays at $25 and continues to spend approximately nothing.

**2. AC Repair budget while it is held.**
It reserves $141.45/day and currently spends ~$0. Reallocate to HVAC Installation, or hold it
ready for a fast reversal? *Recommendation:* hold it — it is already inside the corrected
$433.33/day total, and it keeps option (b) above cheap to execute.
*If unanswered:* budget stays as-is; no spend impact.

**3. Does Ambient offer financing or payment plans?**
`hvac companies with payment plans` appeared as a search term. If yes, it is a keep and a
possible ad-copy asset. If no, it is a negative.
*If unanswered:* the term stays live at negligible cost (1 impression, 0 clicks).

**4. Does Ambient offer air duct *cleaning*, as distinct from ductwork installation and repair?**
PHRASE `air duct cleaning` is live on all five campaigns and blocks
`air duct cleaning and repair near me` (2 all-conversions). The work order lists ductwork and air
ducts as services but not duct cleaning, so the negative was left in place rather than claim an
unverified service.
*If unanswered:* the negative stays; a small amount of duct-related demand stays blocked.

**5. WhatConverts API access.**
`WHATCONVERTS_API_TOKEN` is empty. Until it is populated, every qualified-lead, CPQL, sold-job,
revenue and gross-profit figure in every report is unavailable — and the `WC Calls` offline
import has recorded zero conversions since launch, which is a separate defect worth diagnosing.
*If unanswered:* lead quality stays `UNKNOWN` and CPC decisions continue to be made on raw CPA.

---

## 19. ClickUp activity update

> **Ambient Cooling — BOFU search-term and CPC audit, 2026-09-09**
>
> Completed a full read-only audit of the five live Search campaigns (customer 2401959466).
> Identity gate passed; no live changes were made.
>
> **Measured:** CPC bid ceilings were set in the Google Ads UI on 2026-09-04 (AC Repair $25,
> HVAC Repair $25, HVAC Installation $30). Delivery in the four settled days after
> (2026-09-05 → 09-08) was 2 clicks and $45.08, against 172 clicks and $8,025.18 in the 21 days
> before. Primary conversions went from 14 to 0.
>
> **Measured:** of 952 visible search-term rows, 419 (44%) are already blocked by the existing
> 6,160 campaign negatives and 452 (47.5%) are legitimate HVAC intent. Two rows worth $20.44
> qualified as new negative candidates.
>
> **Measured:** 88 live negatives collide with protected demand. 33 distinct terms block
> supported manufacturers or confirmed Ambient services — 22 at campaign level and 18 at the
> account level, with 7 present at both. The account-level ones cannot be overridden by a
> campaign-level rule. One PHRASE negative blocks Savage, Maryland, a live location target,
> across all five campaigns.
>
> **Measured:** search terms naming other states are query text, not user location. 100% of
> impressions and clicks came from users physically inside the targeted Maryland locations
> (185 of 185 `user_location_view` rows in-target). No budget went out of state.
>
> **Measured:** the removed keyword `hvac installers` cost $2,430.35 over 102 clicks with zero
> primary conversions — 30% of all account spend — and produced 53.6% of the search-term rows.
>
> **Verified:** the 79 competitor keywords added on 2026-08-31 were removed on 2026-09-01 and
> cost $44.18 in total. No remediation is needed.
>
> **Delivered:** six validated, fingerprinted change packages (119 operations) awaiting approval,
> plus a landing-page and conversion-tracking defect list.
>
> **Not measured:** lead quality, CPQL, sold jobs, revenue and gross profit. The WhatConverts API
> token is empty. No savings or lead-quality improvement is claimed.

---

## 20. The out-of-state search terms — answered

> *"Check why the campaigns are getting search terms from other states different than the
> locations selected in MD — I see Florida, New York, TN, TX and other."*

**No out-of-state user has clicked an Ambient ad, and no budget has gone out of state.** The
state names are words inside the query text, not the searcher's location.

### The evidence

**1. Targeting is correct and complete.** All five campaigns carry exactly **75 positive
location targets, every one of them in Maryland**. Zero non-Maryland targets. Zero location
exclusions. `positive_geo_target_type = PRESENCE` on all five — people *in* the area, not people
*interested in* it.

**2. Every impression and click came from inside a targeted location.** `user_location_view`
returns 185 rows for 2026-08-14 → 2026-09-08, and **`targeting_location = true` on all 185
(100%)**. Broken out by physical presence (`geographic_view`):

| Physical location | Impressions | Clicks | Cost |
|---|---|---|---|
| **Maryland (geoTargetConstants/21153)** | **5,570** | **175** | **$8,103.66** |
| Alabama, Louisiana, Mississippi, Wyoming | 7 combined | **0** | **$0.00** |
| *Area of interest* — DC, New York, Texas, Florida, Pennsylvania | 12 combined | **0** | **$0.00** |

**100% of clicks and 100% of cost came from Maryland presence.** The 7 out-of-state
presence impressions (0.13%) are ordinary IP-geolocation imprecision — VPNs, mobile carrier NAT,
satellite routing. The 12 `AREA_OF_INTEREST` impressions are the giveaway: that column labels the
place a *query* referred to while the searcher was still physically in Maryland.

**3. The CSV confirms it from the other direction.** Of the 988 displayed rows, **62 (6.3%) name
a non-Maryland place in the query text** — and those 62 rows produced **7 clicks and $405.25**
with zero conversions, against 99 rows naming a Maryland place and 827 naming no place at all.

| State named in the query | Rows | Impr | Clicks | Cost |
|---|---|---|---|---|
| Virginia | 11 | 16 | 1 | $24.50 |
| Washington DC | 7 | 12 | 0 | $0.00 |
| Florida | 7 | 8 | 0 | $0.00 |
| Indiana | 5 | 8 | 2 | $283.84 |
| North Carolina | 5 | 6 | 0 | $0.00 |
| Delaware | 5 | 8 | 2 | $46.84 |
| Texas | 4 | 5 | 0 | $0.00 |
| Pennsylvania | 4 | 7 | 0 | $0.00 |
| Colorado, New Jersey, New York, Tennessee, Nevada, Ohio, California, South Carolina | 14 | 22 | 2 | $50.07 |
| **Total** | **62** | **~100** | **7** | **$405.25** |

Florida, New York, Texas and Tennessee — the four named in the question — account for
**15 rows, 19 impressions, 0 clicks and $0.00 between them.**

### Why Maryland users type other states' names

Three ordinary causes, all consistent with the data:

1. **Close-variant matching on an unanchored phrase keyword.** `"hvac installers"` — two words,
   no location, no service qualifier — was live from 2026-08-14 to 2026-08-28 and generated
   **530 of the 988 rows (53.6%)**. Google's close-variant expansion pulls national and
   out-of-state phrasings into a keyword that broad. This is the mechanism, and the owner has
   already removed it.
2. **Genuine cross-state research by Maryland residents** — someone in Severn comparing a quote
   against Florida pricing, or looking up a national chain's other branches.
3. **Company names that contain a place.** Several rows name multi-state HVAC companies whose
   brand includes another state or city.

### What to do about it

**Nothing in targeting. Targeting is not the problem, and changing it would be the wrong fix.**

- Do **not** add country or state exclusions. The brief's own rule applies — use specific
  exclusions supported by data — and the data shows zero out-of-state clicks to exclude.
- The structural fix has already happened: `hvac installers` → `hvac installers near me` on
  2026-08-28 removed the unanchored keyword that produced the pollution.
- The residual 62 rows cost $405.25 over 8 weeks and are already 44%-covered by the existing
  negatives.

**One caution.** If a state-name negative list is ever considered, it must exclude
**Maryland, Virginia, Delaware, Pennsylvania and Washington DC** — all border jurisdictions
whose names appear in legitimate Anne Arundel and Howard County queries. Note also that the
existing shared set **10664309518 "States List" (48 members) is not attached to the five
campaigns, and should stay unattached** for exactly this reason.

---

## 21. Consolidated approval block

Every package is validated, fingerprinted, atomic and `partial_failure = false`. Nothing has been
executed. Reply with the exact approval line for each package you want run.

### Safe, reversible packages

```
APPROVE AMB-0909-CPC-1      46C39C6B7091    2 operations
```
Raise CPC bid ceilings: HVAC Installation $30 → $65, HVAC Repair $25 → $60. AC Repair
deliberately held at $25. **This is the single highest-value change in the audit** — it ends a
97% delivery outage.

```
APPROVE AMB-0909-ADS-1      11A79347A296    2 operations
```
Pause two ENABLED-but-DISAPPROVED RSAs (CONSUMER_FINANCE, FULLY_LIMITED). Each ad group keeps two
ENABLED APPROVED RSAs.

```
APPROVE AMB-0909-BUD-1      D448BFDE4650    2 operations
```
Gas Boiler Repair $42.76 → $5.00; HVAC Installation $176.15 → $181.61. Daily total $465.63 →
$433.33, bringing the 30-day worst case inside the $13,000 monthly maximum for the first time.

```
APPROVE AMB-0909-NEG-ADD-1  23BE8FF0F24C    6 operations
```
Four competitor PHRASE negatives, one sizing-research PHRASE, one price-research EXACT, all on
HVAC Installation. Low materiality ($104.92 over 26 days) — approve or skip without consequence.

### Destructive packages — separate approval, one line each

```
APPROVE DESTRUCTIVE AMB-0909-NEG-RM-1   CE289F3508A2   89 operations
```
Remove 89 campaign-level negatives (22 distinct texts) that block supported manufacturers,
confirmed Ambient services, Savage MD, and the generics `free` and `licensed`.

```
APPROVE DESTRUCTIVE AMB-0909-NEG-RM-2   A435FA09AC97   18 operations
```
Remove 18 members from the **account-level** negative list 11252984411 (272 → 254): twelve
supported manufacturers plus `commercial`, `thermostat`, `thermostats`, `al`, `american`, `mr`.

> **These two are a matched pair.** `carrier`, `trane`, `lennox`, `goodman`, `rheem`,
> `mitsubishi` and `daikin` exist at *both* layers. Approving only one leaves the block in place
> at the other. Approve both, or neither.

### Recommended order

1. **`AMB-0909-CPC-1`** — restores delivery. Nothing else can be measured until it runs.
2. **`AMB-0909-BUD-1`** — closes the monthly-cap breach before spend resumes.
3. **`AMB-0909-ADS-1`** — tidy, zero risk.
4. **`AMB-0909-NEG-RM-1` + `AMB-0909-NEG-RM-2` together** — unblocks manufacturer and service demand.
5. **`AMB-0909-NEG-ADD-1`** — optional.

### Explicitly NOT proposed

- Any AC Repair CPC ceiling change — held by design pending question 1.
- Any positive-keyword pause — the 79 were already removed by the owner on 2026-09-01.
- Any Gas Boiler keyword enablement — the landing-page service gate still fails.
- Any conversion-action change — needs question 4 and a working WhatConverts feed first.
- Any shared-list attachment — `General List` 11813144900 contains BROAD `repair`, which would
  block all three core repair keywords.
- Any RSA copy rewrite, bid-strategy change, call bid adjustment, or geo exclusion.

---

## 22. Evidence index

All paths relative to the repository root.

| File | Contents |
|---|---|
| `reports/ambient-cooling-heating/evidence/2026-09-09-identity-and-structure.json` | identity gate, 33 campaigns, 27 budgets |
| `…/2026-09-09-structure.json` | ad groups, keywords, all negative layers, shared sets |
| `…/2026-09-09-change-history.json` | 7,414 change events, 2026-08-11 → 09-09 |
| `…/2026-09-09-anomalous-positives.json` | the 21 positive rows and their true serving state |
| `…/2026-09-09-keywords-and-geo.json` | keyword_view, geographic_view, user_location_view |
| `…/2026-09-09-geo-targets.json` | all 375 geo criteria, resolved to canonical names |
| `…/2026-09-09-csv-reconciliation.json` | CSV totals, deltas, query-text geography |
| `…/2026-09-09-out-of-state-query-text-detail.json` | the 62 non-Maryland-named rows |
| `…/2026-09-09-search-term-pull-summary.json` | four API pulls with sha256 hashes |
| `…/2026-09-09-verdicts.json` | all 952 classified rows |
| `…/2026-09-09-protection-register.json` | 67 BOFU probes, 80 MD tokens, live negative counts |
| `…/2026-09-09-collision-audit.json` | probe / positive / converting-term collisions |
| `…/2026-09-09-negative-triage.csv` | the 88 colliding negatives, triaged |
| `…/2026-09-09-removal-plan-analysis.json` | removal ops + sibling-eligibility proof |
| `…/2026-09-09-account-level-triage.json` | all 272 account-level members, triaged |
| `…/2026-09-09-geo-negative-sweep.json` | 22,500 service × place probes |
| `…/2026-09-09-performance.json` | windows, impression share, CPC distribution, segments |
| `…/2026-09-09-performance-2.json` | conversion actions, campaign × date, ceiling before/after |
| `…/2026-09-09-cpc-model.json` | survival model + economic bands |
| `…/2026-09-09-keyword-planner.json` | full Planner export with geo/network/date inputs |
| `…/2026-09-09-policy-and-qs.json` | policy topics, Quality Score components |
| `…/2026-09-09-ads-assets.json` | 20 ads with full copy, assets, keyword daily timeline |
| `…/2026-09-09-local-preflight.json` | preflight result |
| `…/2026-09-09-pacing-and-unchanged-proof.json` | pacing scenarios + post-audit unchanged proof |
| `clients/ambient-cooling-heating/snapshots/lp-browser-qa-2026-09-09.json` | real-browser LP QA |
| `clients/ambient-cooling-heating/exports/search-term-verdicts-2026-09-09.csv` | 952 rows, full companion table |
| `clients/ambient-cooling-heating/exports/search-terms-api-2026-09-09-*.jsonl` | four raw API pulls |
| `clients/ambient-cooling-heating/plans/AMB-0909-*.json` | the six packages |
| `plans/AMBIENT-2026-09-09-packages.json` | combined manifest |
| `receipts/validate-only/AMB-0909-*-2026-09-09.json` | six validate-only receipts |

---

*Read-only audit. Zero mutations executed. Every external change requires the explicit approval
line above.*
