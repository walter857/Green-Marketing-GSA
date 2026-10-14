# Ambient Cooling — Execution, Readback and Blocked Packages

**Account:** Ambient Cooling - Live · **Customer ID:** 2401959466 · America/New_York · USD
**Run:** 2026-09-10 · **Mutations executed: 10, across 3 packages. Readback: 0 FAIL.**

| | |
|---|---|
| **Executed** | AMB-0909C-COMP-1 (3) · AMB-0909-ADS-1 (2) · AMB-0909C-NEG-SAVAGE (5) |
| **Superseded, not executed** | AMB-0909C-BUD-1 `A7118436590B` |
| **Blocked, not executed** | AMB-0909C-NEG-COMMERCIAL `9F88FEE76803` · AMB-0909C-CPC-INST-2 `5D57E0EF3B70` |
| **New, validated, needs approval** | AMB-0910-BUD-2 `93541FBB5D7F` |

---

## 1. Identity, validators, concurrency

**Six-field identity gate — PASS**, re-run before the snapshot, before each mutation and again
before readback.

| Field | Required | Observed |
|---|---|---|
| `descriptive_name` | Ambient Cooling - Live | Ambient Cooling - Live |
| `customer.id` | 2401959466 | 2401959466 |
| `manager` | false | **false** |
| `test_account` | false | **false** |
| `time_zone` | America/New_York | America/New_York |
| `currency_code` | USD | USD |

Manager links: **3373711342 ACTIVE**, **2815082755 ACTIVE**.

**Validators:** `validate_work_order.py` → PASS · `verify_setup.py --online` → Connection OK,
Preflight PASS · account-specific gate suite → 3 PASS / 3 BLOCKED (§4).

**Account clock, from the API not the host:** `DURING TODAY` returned **no rows for 2026-09-10**
(zero delivery so far). `DURING YESTERDAY` returned **2026-09-09** — 82 impressions, 2 reported
clicks, $58.63. **Latest settled date: 2026-09-09**, used throughout.

**Concurrency — PASS.** Two Python processes are running (PIDs 29920, 41804), both from
`D:\Carbon PT\...\carbon-b2b`. Verified: **0 occurrences of `2401959466` anywhere in that
repository**, and **0 `mutate` calls** in either script. Not writers to this account. Not touched.

---

## 2. Reconstructed state and duplicate-execution prevention

A timestamped before-state snapshot was written to
`clients/ambient-cooling-heating/snapshots/before-state-2026-09-10.json`
(sha256 `b47a716a6d743924…`) covering campaigns, budgets (individual vs shared), bidding
strategies and portfolio associations, CPC ceilings, every bid adjustment, ad groups, positive
keywords with serving eligibility and final URLs, all four negative layers, ads with policy status
and text, assets, schedules, geo criteria and location option, conversion actions and all four
goal layers, tracking settings, IP exclusions and manager links.

**Change history 2026-09-09 00:00 → now:** 125 events, all `CAMPAIGN_CRITERION / CREATE /
GOOGLE_ADS_WEB_CLIENT` from the 2026-09-09 negative additions. **Zero events after
2026-09-10 00:00** — nothing had run before this session.

**Package classification before any write — all six `UNEXECUTED_AND_EXACT`:**

| Package | Fingerprint | Reproduces | Classification |
|---|---|---|---|
| AMB-0909C-BUD-1 | `A7118436590B` | ✅ | UNEXECUTED_AND_EXACT |
| AMB-0909C-COMP-1 | `D434D6F41747` | ✅ | UNEXECUTED_AND_EXACT |
| AMB-0909-ADS-1 | `11A79347A296` | ✅ | UNEXECUTED_AND_EXACT |
| AMB-0909C-NEG-SAVAGE | `10F76004E1B6` | ✅ | UNEXECUTED_AND_EXACT |
| AMB-0909C-NEG-COMMERCIAL | `9F88FEE76803` | ✅ | UNEXECUTED_AND_EXACT |
| AMB-0909C-CPC-INST-2 | `5D57E0EF3B70` | ✅ | UNEXECUTED_AND_EXACT |

Nothing was replayed. **DO_NOT_EXECUTE confirmed** for `752BF95EBD7C`, `DE376F91F449`,
`05FBCBD34B4A`, `18143479027D`, `46C39C6B7091`, `D448BFDE4650`, `23BE8FF0F24C`, `CE289F3508A2`,
`A435FA09AC97`.

---

## 3. Corrections to the record

### 3.1 Conversion wording

The proven Google Ads metric totals for the settled audit window are preserved exactly:

| Action | `metrics.conversions` | `metrics.all_conversions` |
|---|---|---|
| Calls from ads | **5.00** | 5.00 |
| Ambient Cooling - LP -Submit Lead Forms | **5.00** | 5.00 |
| WC Lead | **4.00** | **8.00** |
| **Total `metrics.conversions`** | **14.00** | |

**These are raw Google Ads Primary conversion records.** They are not 14 unique leads, not
qualified leads, not customers and not sold jobs.

**Two claims are withdrawn from the third-pass report:**

1. The API does **not** prove "4 of 8 distinct WC Lead records reached Primary." It proves
   **aggregate metrics of 4.00 in Conversions and 8.00 in All conversions** for that action. The
   per-record mapping is not exposed.
2. `ONE_PER_CLICK` is **not** demonstrated to explain the difference. The mechanism, and any
   cross-action duplication, **remain unproven.**

**HVAC Installation raw CPA, 2026-08-29 → 2026-09-03, preserved:**

```
$483.98 campaign cost ÷ 3 Primary conversion records = $161.33 raw CPA
```

The three records may represent **between one and three unique leads**:
1 → **$483.98** · 2 → **$241.99** · 3 → **$161.33**.

### 3.2 Budget — the $10,216.12 figure is retracted

Fresh preflight confirms **zero September budget edits** for any of the five campaigns, and
**$0.00 September spend** for both campaigns the package would change.

For a campaign with no September budget change, the applicable monthly charging limit applies —
not spend-to-date plus one budget per remaining day:

| Campaign | Daily | × 30.4 |
|---|---|---|
| AC Repair | $141.45 | **$4,300.08** |
| HVAC Installation | $176.15 | **$5,354.96** |
| HVAC Repair | $78.95 | **$2,400.08** |
| **Unchanged subtotal** | | **$12,055.12** |

Edit day **2026-09-10**, **21** calendar days remaining including the edit day, both changed
campaigns at **$0.00** September spend before the edit:

| Campaign | Calculation | September maximum |
|---|---|---|
| Gas Boiler Repair | $0 + ($5.00 × 21) | **$105.00** |
| HVAC Replacement | $0 + ($20.00 × 21) | **$420.00** |
| **Conservative account September upper bound** | | **$12,580.12** |
| **Headroom under $13,000** | | **$419.88** |

**Steady-state future month:** $421.55 × 30.4 = **$12,815.12**, headroom **$184.88**.

The prior $10,216.12 figure **understated September exposure by $2,364.00**.

**Cost basis:** all figures are **SERVED** cost. `billing_setup` is APPROVED and `account_budget`
reads `approved_spending_limit_type = INFINITE` with `total_adjustments_micros = $477.32`
lifetime. The `invoice` resource is **not queryable** on this API surface
(`UNRECOGNIZED_FIELD`), so no per-month **BILLED** figure and no Invalid Activity Credit
breakdown could be obtained. Served cost can still be restated by later credits.

---

## 4. Package-by-package status

### ✅ EXECUTED — AMB-0909C-COMP-1 · `D434D6F41747` · 3 operations

All gates passed, including a fresh verbatim-observation recheck that reproduced the historical
evidence exactly: **13 impressions, 2 reported clicks, $70.61, 0 Primary conversion records**.

| Timestamp (account-local) | Returned resource name | Match | Text |
|---|---|---|---|
| 2026-09-10 00:41:35 | `customers/2401959466/campaignCriteria/24132507747~335741381439` | EXACT | `arundel cooling and heating reviews` |
| 2026-09-10 00:41:35 | `customers/2401959466/campaignCriteria/24132507747~922383112306` | EXACT | `arundel heating and cooling maryland` |
| 2026-09-10 00:41:35 | `customers/2401959466/campaignCriteria/24132507747~2425986330221` | EXACT | `maryland mechanical heating & cooling` |

One atomic mutate, `partial_failure = false`, 3 results returned.

### ✅ EXECUTED — AMB-0909-ADS-1 · `11A79347A296` · 2 operations

| Timestamp | Resource | Before | After |
|---|---|---|---|
| 2026-09-10 00:41:57 | `.../adGroupAds/202339087634~820900825434` | ENABLED + DISAPPROVED | **PAUSED** |
| 2026-09-10 00:41:57 | `.../adGroupAds/200159223798~820944944368` | ENABLED + DISAPPROVED | **PAUSED** |

**This is inert policy cleanup.** A FULLY_LIMITED disapproved ad cannot serve, so pausing it
changes no delivery. **It is not a CTR improvement and not a conversion improvement.**

### ✅ EXECUTED — AMB-0909C-NEG-SAVAGE · `10F76004E1B6` · 5 operations · DESTRUCTIVE

Removal snapshot saved to `snapshots/savage-removal-snapshot-2026-09-10.json` before the write.

| Timestamp | Resource removed |
|---|---|
| 2026-09-10 00:42:03 | `customers/2401959466/campaignCriteria/24132507741~138360213` (AC Repair) |
| 2026-09-10 00:42:03 | `.../24132507744~138360213` (Gas Boiler Repair) |
| 2026-09-10 00:42:03 | `.../24132507747~138360213` (HVAC Installation) |
| 2026-09-10 00:42:03 | `.../24132507750~138360213` (HVAC Repair) |
| 2026-09-10 00:42:03 | `.../24132507753~138360213` (HVAC Replacement) |

**Rollback note:** recreating `savage` as PHRASE at the same five campaign scopes produces **new
criterion IDs**. Rollback does not restore the removed IDs.

**Residual sweep:** two `savage` strings remain in shared set 10720232972 "General" —
`[aireco savage md]` and `[aireco savage]`, both EXACT supply-house negatives. That set is **not
attached to any of the five**, and EXACT match blocks only those two literal queries.

### ⛔ SUPERSEDED, NOT EXECUTED — AMB-0909C-BUD-1 · `A7118436590B`

Nine of ten gates passed: both budgets are **individual** (`explicitly_shared=false`,
`reference_count=1`), before-states match live exactly, the three required-unchanged budgets hold,
fresh lost-IS-to-budget is **0.00%** on both, and both corrected limits are under $13,000.

**The tenth gate failed.** The hashed `operations` payload embeds
`per_campaign_limits.september_campaign_maximum` of **142.76** (Gas Boiler) and **426.32**
(HVAC Replacement), computed by the retracted method. The corrected figures are **105.00** and
**420.00**. Because the retracted assertion sits **inside a hashed plan field** and is also a
**mandatory precondition**, the fingerprint is **superseded**, not executed.

**Replacement drafted and validated: `AMB-0910-BUD-2` / `93541FBB5D7F` / 2 operations.** Identical
mutation payload; corrected hashed calculations. **VALIDATED_OK. Not executed — it requires new
approval** (§10).

### ⛔ BLOCKED — AMB-0909C-NEG-COMMERCIAL · `9F88FEE76803`

| Gate | Result |
|---|---|
| Target is still the bare token `commercial`, BROAD, in set 11252984411 | ✅ PASS |
| Populated client/work-order records explicitly authorize commercial HVAC as paid scope | ❌ **FAIL** — the word "commercial" appears in **neither** `work-order.yaml` **nor** `client.yaml` |
| A truthful commercial intake route and destination exists for every live campaign that would become eligible | ❌ **FAIL** — none of the five paid landing pages carries commercial intake |
| Separated from any Installation CPC change by ≥ 7 settled days | ❌ **FAIL** — no CPC change executed, so the clock has not started |

The removal would widen eligibility across **all 23 non-removed campaigns**, not only the five
enabled. Public website references to commercial work do **not** by themselves prove paid scope.
**Held approved-but-blocked.** The narrower routing plan is in §11.

### ⛔ BLOCKED — AMB-0909C-CPC-INST-2 · `5D57E0EF3B70`

Six gates failed. The account-side gates all pass:

| Account-side gate | Result |
|---|---|
| Installation ceiling remains exactly $30 (30000000) | ✅ PASS |
| Maximize Clicks, no portfolio strategy | ✅ PASS |
| No bid adjustment above ×1.0 anywhere (5 exist, all DEVICE/TABLET ×0.0) | ✅ PASS |
| `hvac installers near me` PHRASE + EXACT are the only live Installation keywords | ✅ PASS |
| The unanchored `hvac installers` remains removed | ✅ PASS |
| Fingerprint reproduces | ✅ PASS |

The outcome gates do not:

| Outcome gate | Result |
|---|---|
| WhatConverts access via configured local credentials | ❌ `WHATCONVERTS_API_TOKEN` is **empty** |
| A current anonymised lead export resolves unique lead status | ❌ **19 local lead-shaped CSVs searched; 0 contain any Ambient row** |
| LP Submit / WC Lead / GA4 deduplicated into unique people | ❌ not possible without a join key |
| ≥2 of the 3 September 1 Installation records proven unique qualified leads | ❌ unresolvable |
| Budget-package readback passed | ❌ BUD-1 superseded, not executed |
| Competitor-negative readback passed | ✅ now satisfied (this run) |

**An outcome gate that cannot be observed is not an enforceable gate.** Not executed.

---

## 5. Readback and unrelated-resource verification — 0 FAIL

Every changed field was read straight back from the API, and every surrounding resource was
re-read to prove no collateral change.

**Changed, as intended:**

| Check | Result |
|---|---|
| 3 new criteria exist, ENABLED, `negative=true`, EXACT, on 24132507747 only | ✅ |
| Both target ads now PAUSED; approval, final URLs and all 15 headlines unchanged | ✅ |
| Exactly 2 ads changed status account-wide | ✅ |
| Each affected ad group retains exactly 2 ENABLED + APPROVED RSAs (202339087634 → 821319509197, 821319509200; 200159223798 → 821319509203, 821319509206) | ✅ |
| Zero `savage` campaign negatives remain on the five | ✅ |
| Savage MD `geoTargetConstants/1018704` still an ENABLED positive target on all five | ✅ |

**Campaign negative counts, before → after → expected:**

| Campaign | Before | After | Expected |
|---|---|---|---|
| AC Repair | 1,136 | **1,135** | 1,135 ✅ |
| Gas Boiler Repair | 1,132 | **1,131** | 1,131 ✅ |
| HVAC Installation | 1,435 | **1,437** | 1,437 ✅ |
| HVAC Repair | 1,138 | **1,137** | 1,137 ✅ |
| HVAC Replacement | 1,319 | **1,318** | 1,318 ✅ |

**Unchanged, verified:** 23 non-removed campaigns · 5 ENABLED · 68 ad groups · 30 ad schedules ·
375 geo criteria · 2,796 IP blocks (0 on the five) · 17 shared sets · **0 shared lists attached to
the five** · 16 conversion actions · **10 live positive keywords, all ELIGIBLE** · account-level
set still **272** members · all five CPC ceilings unchanged ($25 / $0 / $30 / $25 / $0) · all five
campaigns still TARGET_SPEND and ENABLED · **all five budgets unchanged and still individual** ·
both manager links ACTIVE · ClickCease tracking template intact.

Receipts: `receipts/live/*-2026-09-10-EXECUTED.json`, pre-write validations in
`receipts/validate-only/*-2026-09-10-prewrite.json`, full readback in
`evidence/2026-09-10-readback.json`.

---

## 6. Budget safety

**No budget was changed this run.** The account therefore still sits at:

```
combined daily $465.63  ×30.4 = $14,155.15   ***BREACHES the $13,000 maximum by $1,155.15***
```

This is the single most important open item. `AMB-0910-BUD-2` closes it to **$12,815.12**
(headroom $184.88) and brings September to **$12,580.12** (headroom $419.88).

The breach is a *charging-limit capacity* breach, not observed spend: September month-to-date
served cost through 2026-09-09 is **$1,319.49**, and 2026-09-10 has taken zero delivery so far.
The exposure is real but has not been realised.

**Future-safe rollback for BUD-2:** a blind restore of $42.76 + $26.32 returns the account to
$14,155.15 and is **forbidden**. With the other three unchanged at $396.55/day, Gas Boiler +
HVAC Replacement must stay **at or below $31.08/day combined**. Example compliant partial restore:
$10.00 + $21.00 = $31.00 → $427.55/day → $12,997.52. Anything higher needs an offsetting
reduction, a fresh cap calculation and a new approval fingerprint.

---

## 7. Search-term and negative-keyword results

Fresh audit across five settled windows. All-time visible corpus: **957 rows, 118 reported clicks,
$6,585.29, 12 Primary records.**

| Verdict | Rows | Clicks | Cost | Records |
|---|---|---|---|---|
| KEEP_BOFU | 427 | 64 | $5,252.61 | 12 |
| ALREADY_COVERED | 423 | 49 | $1,239.87 | 0 |
| KEEP_TEST | 56 | 0 | $0.00 | 0 |
| HOLD | 41 | 3 | $58.50 | 0 |
| NEGATIVE_EXACT | 10 | 2 | $34.31 | 0 |
| ROUTE / ADD_AS_POSITIVE / NEGATIVE_PHRASE / NEGATIVE_BROAD | 0 | — | — | — |

**No new negative package is proposed, and that is the evidence-led answer.**

The entire residue is **51 rows, 5 reported clicks, $92.81**, and almost all of it is
installation **pricing and sizing research from prospective buyers** — `how much does it cost to
install hvac system`, `cost of mini split system for 1000 sq ft`, `how much does a new hvac system
cost`. The operating rules forbid auto-negativing `cost`, `price` and `estimate`, and the
2026-09-09 correction pass explicitly withdrew `"sq ft house"` and `[how much is hvac system]` for
exactly this reason. Re-proposing them would reverse a decision already made on the evidence.

Notable individual rows:
- `aciq installers near me` — 3 impressions, 1 click, $30.94. **ACIQ is on the supported
  manufacturer list.** HOLD, not negative.
- `arundel cooling and heating` — 6 impressions, 0 clicks, $0.00. Deliberately still **not
  blocked**: it is one word from `anne arundel cooling and heating` (which produced a Primary
  record) and from `hvac anne arundel county`. Anne Arundel County is the core service area.
- `hydronic radiant floor heating installers near me` — 1 click, $28.90 on 2026-09-09. New,
  worth watching; radiant floor is not a confirmed Ambient service but the query is adjacent to
  boiler work.

**Preserved as instructed:** `car`, `auto`, `boat`, `automotive`; all previously approved
competitor negatives; the held `free` and manufacturer/service removals; `licensed` held as an ad
claim. Shared list **11813144900 was not attached** — its BROAD `repair` negative would block all
three core repair keywords.

Full term-level output: `clients/ambient-cooling-heating/exports/search-term-verdicts-2026-09-10.csv`

---

## 8. CPC and bidding decision by campaign

Settled 2026-08-14 → 2026-09-09.

| Campaign | Impr | Clicks | CTR | CPC | Cost | Records | Raw CPA | Max CPQL | IS | lost BUD | lost RANK | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AC Repair | 895 | 29 | 3.24% | $106.37 | $3,084.87 | 5 | $616.97 | $150 | 47.0% | 6.3% | 46.7% | **Hold $25** |
| HVAC Repair | 1,081 | 29 | 2.68% | $67.31 | $1,951.94 | 6 | $325.32 | $250 | 33.3% | 8.6% | **58.1%** | **Hold $25** |
| HVAC Installation | 3,450 | 114 | 3.30% | $26.08 | $2,972.96 | 3 | $990.99 | $280 | 36.4% | **52.8%** | 10.7% | **Hold $30** (test blocked) |
| HVAC Replacement | 207 | 5 | 2.42% | $30.50 | $152.52 | 0 | — | $280 | 50.5% | 0.0% | 49.5% | Hold, uncapped |
| Gas Boiler Repair | 38 | 0 | 0.00% | — | $0.00 | 0 | — | $250 | 53.1% | 0.0% | 46.9% | Hold, uncapped |

**AC Repair and HVAC Repair remain at their verified $25 ceilings for the immediate window**, as
instructed. Neither warrants an isolated test yet: AC Repair's raw CPA is 4.1× its limit and HVAC
Repair's is 1.3× over, both on raw records whose qualification is unknown.

**No ceiling is being lowered mechanically.** A ceiling below the auction price of proven
qualified traffic destroys lead volume; that is exactly what the 2026-09-04 ceilings did.

**Sustainable CPC-reduction levers, ranked by what the data supports:**

1. **Landing-page experience** — BELOW_AVERAGE on HVAC Repair and HVAC Replacement. The most
   direct lever on Ad Rank that does not involve paying more.
2. **Expected CTR** — BELOW_AVERAGE on every scored keyword. See §9.
3. **Rank pressure** — HVAC Repair loses **58.1%** of impression share to rank, AC Repair 46.7%.
   These are rank problems, not budget problems.
4. **Device outcome quality** — every one of the 14 Primary records came from mobile.
5. **Click-type quality** — see §11 on LOCATION_EXPANSION.

**Auction Insights: UNAVAILABLE.** The metrics are `selectable: true` but every query returns
`PERMISSION_DENIED` on this Basic-access developer token. No UI export was taken in this run, and
**no values were invented.**

**No advanced bid adjustment is proposed.** No conversion-based bidding change is proposed:
LP form / WC Lead / GA4 duplication is unresolved, unique qualified leads are unavailable, and
recent qualified conversion volume is nil.

---

## 9. CTR, RSA, asset, Quality Score and landing-page findings

**Quality Score is treated as a diagnostic, not a KPI and not an auction input.** Ad Rank is
computed at auction time from bid, live quality signals, context and expected asset impact.

| Campaign | Match | QS | Expected CTR | Ad relevance | Landing-page experience |
|---|---|---|---|---|---|
| AC Repair | Phrase + Exact | **4** | BELOW_AVERAGE | AVERAGE | AVERAGE |
| HVAC Repair | Phrase + Exact | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** |
| HVAC Replacement | Phrase + Exact | **2** | BELOW_AVERAGE | AVERAGE | **BELOW_AVERAGE** |
| HVAC Installation | Phrase + Exact | — | insufficient data | — | — |
| Gas Boiler Repair | Phrase + Exact | — | insufficient data | — | — |

### The AC Repair ad comparison — investigated, and the challenger is NOT drafted

| Ad | Impr | Clicks | CTR | Cost | Records |
|---|---|---|---|---|---|
| 820900825416 (3 city headlines, 9 service headlines) | 534 | 19 | **3.56%** | $2,032.46 | 4 |
| 820900825419 (0 city headlines, 3 service headlines) | 361 | 10 | **2.77%** | $1,052.41 | 1 |

Aggregate CTR favours 825416. **Controlling for device reverses part of it:**

| Ad | Mobile CTR | Desktop CTR | Top % | Abs top % |
|---|---|---|---|---|
| 820900825416 | **5.34%** (337 impr) | 0.51% (197 impr) | 78–81% | 63–69% |
| 820900825419 | 3.57% (196 impr) | **1.82%** (165 impr) | 76% | 64–65% |

Position is effectively equal, so the aggregate gap is substantially a **device-mix artefact**:
825416 received 337 mobile impressions to 825419's 196, and mobile CTR is far higher for both.
**On desktop, 825419 outperforms 825416 by 3.6×.** 825419 is also below the 500-impression
threshold for a meaningful comparison.

**Decision: the evidence does not support a challenger, so none is drafted.** Revisit after
delivery is restored and both ads clear 500 impressions per device.

Consistent with the brief: **HVAC Repair ads are not replaced on CTR alone**; **HVAC Installation
requires post-restoration data**; **HVAC Replacement has too little traffic**; **Gas Boiler
remains blocked by its landing-page defect.**

**RSA assets:** all 380 asset rows carry `performance_label = NOT_APPLICABLE`. Google is not
rating any headline or description at this volume, and **no asset is called a winner from a label
alone**. **Zero location-insertion tags exist across all ten live ads**, against 75 targeted
locations — recorded as a candidate challenger feature, not proposed.

**Sitelinks:** 8 enabled per campaign — Customer Reviews, View Our Work, Contact Ambient, Service
Areas, plus the other four services. **No sitelink is judged bad from aggregate sitelink clicks.**
All five campaigns retain well above the four-useful-sitelink minimum. No change proposed.

### Landing-page QA — all five rendered in a real JS browser, desktop and mobile

| Page | HTTP | H1 service match | Three-step heading | Verdict |
|---|---|---|---|---|
| /ac-repair/ | 200 | ✅ | "Request AC Repair in 3 Simple Steps" | ✅ correct service |
| /hvac-repair/ | 200 | ✅ | "Request HVAC Repair in 3 Simple Steps" | ✅ correct service |
| /hvac-installation/ | 200 | ✅ | "Your HVAC Installation in 3 Simple Steps" | ✅ |
| /hvac-replacement/ | 200 | ✅ | "Your HVAC Replacement in 3 Simple Steps" | ✅ |
| **/gas-boiler-repair/** | 200 | ✅ | **"Your HVAC Replacement in 3 Simple Steps"** | ❌ **GATE FAIL** |

The AC Repair and HVAC Repair "false" flags are the automated checker testing for the literal
word "Your". Both name the correct service. **Gas Boiler Repair is the only genuine service
mismatch.**

> **The Gas Boiler keyword package stays BLOCKED** while `/gas-boiler-repair/` says
> "Your HVAC Replacement in 3 Simple Steps". The required heading is
> **"Your Gas Boiler Repair in 3 Simple Steps"**. No correction was published: source access,
> backup, staging evidence, a tested diff, deployment authority and live post-deploy verification
> are all absent.

All five pages: approved paid number **(410) 705-6354** displayed · main-site number **absent** ·
WhatConverts present · `wc_swap` cookie present · GCLID persisted in storage · **zero barred
claims** · no mobile horizontal overflow · 3 form instances each.
**Still absent on all five: privacy and terms links** — both pages exist on the main site
(`/privacy-policy/`, `/terms-and-conditions/`) and should be linked.

---

## 10. Conversion records versus unique qualified leads

**No conversion record in this account is described as a qualified lead.**

A qualified lead requires a unique person seeking a supported Ambient service who called for at
least 60 seconds or submitted a valid form. Existing customers, employment enquiries, parts
requests, DIY questions, warranty requests, spam, vendors and people seeking another company do
not qualify. **None of that can be evaluated from the Google Ads API.**

- `WHATCONVERTS_API_TOKEN` is present but **empty**. The value was never printed or requested.
- **19 local lead-shaped CSVs were searched** (`lead_export_*.csv`, `leads-inbox*.csv`, repo-wide
  `*lead*.csv`). **Zero contain any Ambient row** — no match on `ambient`, `2401959466`, `severn`,
  `severna`, or any of the five campaign keywords.
- Therefore **unique qualified leads, sold jobs, revenue, margin and profit are UNKNOWN**.
- **No conversion goal was changed**, in line with the unresolved duplication.

**Setup requirement, one line:** populate `WHATCONVERTS_API_TOKEN` in `.env` for WhatConverts
profile 105803, or drop an anonymised export at
`clients/ambient-cooling-heating/exports/` containing date, campaign, source, phone/form type,
GCLID or another privacy-safe join key, qualified/unqualified status, disqualification reason,
sold status and revenue where available.

---

## 11. Invalid traffic

Refreshed, settled 2026-08-14 → 2026-09-09, one segmentation dimension at a time.

| Campaign | Reported clicks | Invalid clicks | Raw | Invalid % |
|---|---|---|---|---|
| AC Repair | 29 | 941 | 970 | 97.01% |
| HVAC Repair | 29 | 621 | 650 | 95.54% |
| HVAC Installation | 114 | 93 | 207 | 44.93% |
| HVAC Replacement | 5 | 82 | 87 | 94.25% |
| Gas Boiler Repair | 0 | 42 | 42 | 100.00% |
| **Total** | **177** | **1,779** | **1,956** | **90.95%** |

| Device | Reported | Invalid | Invalid % |
|---|---|---|---|
| **MOBILE** | 127 | **1,749** | 93.23% |
| DESKTOP | 50 | 30 | 37.50% |

| Click type | Reported | Invalid | Invalid % |
|---|---|---|---|
| **LOCATION_EXPANSION** | 36 | **1,711** | **97.94%** |
| URL_CLICKS | 99 | 64 | 39.26% |
| CALLS | 10 | 4 | 28.57% |
| SITELINKS | 26 | 0 | 0.00% |
| GET_DIRECTIONS | 6 | 0 | 0.00% |

**96.2% of all invalid clicks sit on LOCATION_EXPANSION**, concentrated on mobile.

**What is deliberately not claimed:**
- Reported clicks are called **reported clicks**, not "billable" — billing evidence was not obtainable.
- Invalid clicks are **not** treated as spend.
- It is **not** assumed every invalid click was filtered pre-invoice rather than credited later.
  The Invalid Activity Credit report is **not accessible** on this API surface; `account_budget`
  exposes only a lifetime `total_adjustments_micros` of **$477.32**.
- **No ClickCease attribution is made.** All 2,796 IP exclusions sit on the 18 legacy campaigns
  and **0 are on the five live campaigns** — confirmed again this run and **left unchanged**.
- **LOCATION_EXPANSION is not excluded.** It also produced **4 raw Primary conversion records**,
  and their qualification is UNKNOWN. Removing it could remove real leads.

---

## 12. Monitoring and rollback

A durable, identity-gated, read-only checkpoint tool is installed:
**`scripts/ambient_checkpoint.py`** — run once and it exits; it never daemonises.

```
python scripts/ambient_checkpoint.py                    # read-only checkpoint
python scripts/ambient_checkpoint.py --leads leads.csv  # + privacy-safe outcome counts
python scripts/ambient_checkpoint.py --rollback-cpc --confirm-gate-failed
```

It re-gates identity before any query, separates partial from settled dates, records account-local
timestamps and exact resource IDs, and reports campaign metrics, per-action Primary vs All
conversions, budget exposure against the 30.4-day cap, all four negative layers, live keyword
eligibility and new search terms since the previous checkpoint. Lead outcomes are **counted, never
stored** — no name, phone, email or address is written.

Its **only** possible mutation is HVAC Installation `65000000 → 30000000`, requiring **both**
flags, refusing if the ceiling is not $65, and refusing a second time after the state file records
a rollback. Verified this run: `--rollback-cpc` alone returns
`REFUSED: --rollback-cpc requires --confirm-gate-failed.`

First checkpoint recorded: `evidence/checkpoint-2026-09-10-005057.json`;
state at `clients/ambient-cooling-heating/monitoring/checkpoint-state.json`.

**Checkpoint schedule** — run the command, read the output, close the terminal:

| When | Focus |
|---|---|
| **~24 h** (2026-09-11) | New search terms after the Savage unblock; the 3 competitor negatives holding; no new disapprovals |
| **~72 h** (2026-09-13) | Savage MD queries appearing; negative counts stable; budget exposure |
| **7 settled days** (2026-09-16) | Full search-term review; Primary records by action; raw CPA vs limits |
| **14 settled days** (2026-09-23) | Quality Score movement; September pacing vs $13,000; whether AC Repair or HVAC Repair warrants an isolated test |

**If the CPC test ever becomes eligible**, the tool watches $200 (early warning), $280 (≥1 verified
unique qualified lead) and $560 (≥2). Reporting lag means **no exact stop at $280 can be promised**;
maximum tolerated overshoot is one additional eligible click under the verified effective ceiling.
A failed gate triggers the exact approved `$65 → $30` rollback and a readback. **No $50 rollback.
No 30-click trigger.**

---

## 13. Consolidated approval block

Only genuinely new fingerprinted changes. **Nothing below was executed.**

### Safe, reversible

```
APPROVE AMB-0910-BUD-2   93541FBB5D7F   2 operations   FOR 2401959466
```

Gas Boiler Repair $42.76 → $5.00 · HVAC Replacement $26.32 → $20.00.
Identical mutation payload to the superseded `A7118436590B`; the hashed calculation metadata is
corrected to the $105.00 / $420.00 method. Combined daily **$465.63 → $421.55**; steady state
**$12,815.12** (headroom $184.88); conservative September upper bound **$12,580.12**
(headroom $419.88). VALIDATED_OK, 2 operations, `partial_failure = false`.

**This is the only change that closes the live $1,155.15 charging-limit breach.**

### Destructive

*None proposed.* `AMB-0909C-NEG-COMMERCIAL` remains approved-but-blocked on three failed gates
(§4) and is not re-fingerprinted.

### Still blocked, no new fingerprint

- `AMB-0909C-CPC-INST-2` `5D57E0EF3B70` — blocked on unobservable outcome gates.
- `AMB-0909C-NEG-COMMERCIAL` `9F88FEE76803` — blocked on paid-scope authorization and routing.
- Gas Boiler keyword package — blocked on the live landing-page heading.
- No CTR/RSA challenger — the AC Repair evidence does not support one.
- No new negative package — the residue is protected buyer research.

### Narrower commercial routing plan, for a later run

1. Obtain durable client confirmation that commercial HVAC is in paid scope, and record it in
   `work-order.yaml`.
2. Choose **one** destination campaign and build a dedicated commercial ad group with a matching
   landing page carrying truthful commercial intake.
3. Remove `commercial` only from that campaign's applicable layer, keeping the account-level
   member until routing exists — or accept account-wide widening only once every live campaign has
   a truthful destination.
4. Inventory the four bare-token `commercial` duplicates in paused campaigns
   (22822619680, 23883756382, ad groups 159023127588 and 201974220664 in 20293627152) so
   re-enabling a legacy campaign cannot create an undocumented routing change.

---

## 14. ClickUp activity update

> **Ambient Cooling — September activity, 2026-09-10**
>
> Executed three approved change packages on customer 2401959466 after a full identity gate,
> concurrency check and before-state snapshot. Ten mutations total, one atomic write per package,
> every changed field read back from the API. Readback: zero failures, zero collateral change.
>
> **Completed:** added three exact-match competitor negatives to HVAC Installation for two
> independently verified competing contractors. Removed the phrase negative "savage" from all five
> campaigns, restoring eligibility for Savage, Maryland — a location that was already an active
> positive target on every campaign. Paused two disapproved ads that could not serve; each ad group
> retains two enabled, approved ads. This ad change is policy cleanup and is not expected to move
> CTR or conversions.
>
> **Measured:** campaign negatives on the five live campaigns moved 6,160 → 6,158 (minus five
> "savage" removals, plus three competitor additions), verified by direct readback. Ten live
> keywords, all still eligible. September served cost through 2026-09-09 is $1,319.49.
>
> **Corrected:** the September charging-limit figure previously reported as $10,216.12 understated
> exposure by $2,364. The corrected conservative upper bound is $12,580.12.
>
> **Open risk:** the combined daily budget of $465.63 implies a $14,155.15 monthly charging limit,
> which exceeds the $13,000 maximum by $1,155.15. A corrected budget package is validated and
> awaiting approval; it brings the account to $12,815.12.
>
> **Still blocked:** the HVAC Installation CPC test, because qualified-lead outcome data is
> unavailable and an unobservable gate is not enforceable. The commercial-negative removal, because
> paid commercial scope is not recorded in the client file and no landing page carries commercial
> intake. The Gas Boiler keyword package, because its landing page still shows the wrong service
> heading.
>
> **Not claimed:** no CTR improvement, no CPC reduction, no additional conversions and no qualified
> leads. Lead quality remains unmeasured while the WhatConverts token is empty.

---

## 15. Evidence index

| File | Contents |
|---|---|
| `snapshots/before-state-2026-09-10.json` | full timestamped before-state |
| `snapshots/savage-removal-snapshot-2026-09-10.json` | pre-removal state of all five targets |
| `snapshots/lp-browser-qa-2026-09-10.json` | real-browser QA, five pages, desktop + mobile |
| `evidence/2026-09-10-recovery-and-classification.json` | identity, change history, package classification |
| `evidence/2026-09-10-execution-gates.json` | every gate for all six packages |
| `evidence/2026-09-10-readback.json` | readback + collateral verification |
| `evidence/2026-09-10-analysis.json` | search terms, CTR/QS, ad comparison, invalid traffic |
| `evidence/checkpoint-2026-09-10-005057.json` | first monitoring checkpoint |
| `receipts/live/AMB-0909C-COMP-1-2026-09-10-EXECUTED.json` | live receipt, 3 resource names |
| `receipts/live/AMB-0909-ADS-1-2026-09-10-EXECUTED.json` | live receipt, 2 resource names |
| `receipts/live/AMB-0909C-NEG-SAVAGE-2026-09-10-EXECUTED.json` | live receipt, 5 resource names |
| `receipts/validate-only/*-2026-09-10-prewrite.json` | pre-write validations |
| `receipts/validate-only/AMB-0910-BUD-2-2026-09-10.json` | replacement budget validation |
| `clients/ambient-cooling-heating/plans/AMB-0910-BUD-2.json` | replacement package |
| `exports/search-term-verdicts-2026-09-10.csv` | 957 classified rows |
| `scripts/ambient_checkpoint.py` | durable read-only monitor |

---

*10 mutations executed, all verified. Every remaining change requires its own explicit approval.*
