# Ambient Cooling — Audit Correction and Replacement Packages

**Account:** Ambient Cooling - Live · **Customer ID:** 2401959466 · **Vertical:** heating-cooling
**Run:** 2026-09-09, correction pass · **Mode:** READ + ANALYZE + DRAFT + VALIDATE-ONLY
**Mutations executed: 0.** Nothing in Google Ads, the website, GTM, WhatConverts, ClickCease or
any CRM was created, edited, paused, enabled or removed.

> This report **corrects** `2026-09-09-bofu-search-term-and-cpc-audit.md`. That file is preserved
> unmodified. Where the two disagree, **this one is authoritative**.

---

## 1. Corrected executive summary

Six findings, in order of how much they change the plan.

**1. The CPC-ceiling attribution was over-claimed and is retracted.** The September 9 report said
the 2026-09-04 ceilings were set "by the owner, in the UI, not by the agency." That is not
supported. Every one of the 7,414 change events in the window — 5,784 `GOOGLE_ADS_API` and 1,630
`GOOGLE_ADS_WEB_CLIENT` — carries the **same `user_email`: `access@greenmarketingfl.com`**.
`client_type` identifies the *interface*, not the person. Both interfaces authenticate as the
same shared agency login, so the API cannot tell us who made the change. The correct statement is
that the ceilings were set **through the Google Ads web interface at 2026-09-04 16:56 ET under
the shared `access@greenmarketingfl.com` login**.

**2. The budget package was arithmetically wrong and is superseded.** Google's monthly spending
limit is `daily budget × 30.4`, not × 30. `$13,000 ÷ 30.4 = $427.6315789`. The prior package's
$433.33/day gives **$13,173.23 — a $173.23 breach**, not the "$12,999.90, within cap" it claimed.
The replacement lands at **$421.55/day = $12,815.12**, with $184.88 of headroom.

**3. The HVAC Installation budget increase was built on contaminated data and is withdrawn.** The
53.16% Search lost IS (budget) that justified it was measured across 2026-08-14 → 09-08, a window
in which the removed `hvac installers` keyword was live for 15 of 26 days. On the clean post-swap
window 2026-08-29 → 09-03 the same metric is **4.38%**, with 35.62% lost to *rank* instead. HVAC
Installation is not budget-constrained. Its budget is left alone.

**4. The HVAC Repair $60 recommendation is rejected, and the contradiction behind it is
acknowledged.** $36.47 is *above*, not inside, the $32 optimistic economic band; the $60 model
retains only 1 of 4 visible conversions; and its modelled raw CPA of $474.06 is nearly double the
$250 maximum CPQL. Rebuilt on all 29 campaign clicks — which revealed that **2 of HVAC Repair's 6
primary conversions sit in privacy-hidden traffic the search-term model cannot see** — no tested
ceiling has credible economics. **HVAC Repair stays at $25.**

**5. The bulk negative removals are superseded and replaced by one narrow, verified package.**
107 removals across two packages became **16**. The manufacturer unblock is held entirely:
Ambient's live website names **only York**, and York is not blocked. The six supply-house and
corporate-location EXACT negatives are retained, as the correction brief required.

**6. Local preflight caught a trap that would have cost a converting query.** The first draft of
the competitor package used PHRASE `arundel cooling and heating`. That also blocks
`anne arundel cooling and heating`, which produced a **primary phone-call conversion**, and sits
one word from `hvac anne arundel county`. Anne Arundel County is Ambient's core service area. The
package was narrowed to EXACT before any API quota was spent.

**Net result: 5 fingerprints retired, 4 new validated packages totalling 22 operations, down from
119.**

---

## 2. State verification

### 2.1 Identity gate — six fields, all PASS

| Field | Required | Observed | Result |
|---|---|---|---|
| `customer.descriptive_name` | Ambient Cooling - Live | Ambient Cooling - Live | PASS |
| `customer.id` | 2401959466 | 2401959466 | PASS |
| `customer.time_zone` | America/New_York | America/New_York | PASS |
| `customer.currency_code` | USD | USD | PASS |
| `customer.manager` | false | **false** | PASS |
| `customer.test_account` | false | **false** | PASS |
| GM manager 3373711342 | ACTIVE | ACTIVE | PASS |
| ClickCease manager 2815082755 | ACTIVE | ACTIVE | PASS |

Account-local clock confirmed from the API, not the host: `segments.date DURING TODAY` returns
**2026-09-09** (54 impressions, $58.63 — partial and still moving; it read 36 impressions /
$29.73 at 14:30 ET). `DURING YESTERDAY` returns 2026-09-08.

### 2.2 Validators

- `validate_work_order.py` → `PASS | Ambient Cooling - Live | 2401959466 | heating-cooling | AC Repair`
- `verify_setup.py --online` → `Credential variable names: present · Connection: OK · Preflight: PASS`
- `ambient_0909b_preflight.py` (local, zero API ops) → **0 FAIL, 0 WARN**

### 2.3 Concurrent-writer check — PASS

The same two Python processes are still running (PIDs 29920, 41804, started 2026-08-09). Both
belong to `D:\Carbon PT\...\carbon-b2b`, target customer IDs 7239732058 and 9720978817, contain
**zero occurrences of `mutate`**, and contain **zero references to 2401959466**. No process can
write to this account.

### 2.4 Drift check — ZERO DRIFT, nothing executed

| Package | Fingerprint | Recompute | Before-state | Executed? |
|---|---|---|---|---|
| AMB-0909-CPC-1 | 46C39C6B7091 | OK | unchanged (ceilings 30000000 / 25000000) | **No** |
| AMB-0909-BUD-1 | D448BFDE4650 | OK | unchanged ($42.76, $176.15) | **No** |
| AMB-0909-NEG-RM-1 | CE289F3508A2 | OK | **89/89** targets still live ENABLED | **No** |
| AMB-0909-NEG-RM-2 | A435FA09AC97 | OK | **18/18** members still present | **No** |
| AMB-0909-ADS-1 | 11A79347A296 | OK | both ads still ENABLED + DISAPPROVED | **No** |
| AMB-0909-NEG-ADD-1 | 23BE8FF0F24C | OK | 0/6 already present | **No** |

All six validate-only receipts show `validate_only=true`, `partial_failure=false`,
`VALIDATED_OK`, and **no `resource_names`** — the signature of a call that wrote nothing.

**Zero change events after 2026-09-09 15:10** (the prior run's last read). The account is exactly
as the September 9 audit left it.

### 2.5 August work preserved

HVAC Installation budget $176.15 · 30 ad-schedule rows · HVAC Repair replacement RSAs ENABLED +
APPROVED · 8 sitelinks per campaign · AC Repair automotive negatives · 6,160 campaign negatives ·
272 account-level members · 2,796 ClickCease IP exclusions · 375 geo targets · 16 conversion
actions · both manager links ACTIVE · ClickCease tracking template intact. All verified present
at 18:06 ET.

---

## 3. Every factual and mathematical correction

| # | September 9 report said | Correct position | Evidence |
|---|---|---|---|
| C1 | Ceilings set by "the owner, in the UI, not by the agency" | Set **through the web interface under the shared `access@greenmarketingfl.com` login**. `client_type` identifies the interface, not the person. | All 7,414 change events carry one `user_email` |
| C2 | "$433.33/day × 30 = $12,999.90, within cap" | **× 30.4 = $13,173.23, a $173.23 breach.** Not compliant. | Google's monthly limit = daily × 30.4 |
| C3 | HVAC Installation "53.16% lost IS (budget)" justifies more budget | **4.38%** on the clean post-swap window; 35.62% lost to rank. Increase withdrawn. | Windowed IS pull |
| C4 | HVAC Repair $60, "$36.47 inside the optimistic band" | $36.47 is **above** the $32 band. $60 keeps 1 of 4 visible conversions at $474.06 raw CPA vs a $250 max CPQL. **Rejected.** | CPC scenario rebuild |
| C5 | Primary conversions "5 + 4 + 4 = 13" against a stated 14 | **5 + 5 + 4 = 14.** LP Submit Lead Forms is 5, not 4. Reconciles exactly. | `segments.conversion_action_name` |
| C6 | "80 colliding negatives" in §0/§9, "88" in §7 | **88.** 80 counted converting-term collisions only; 18 were probe-only; the union is 88. | Collision audit |
| C7 | "100% of impressions came from Maryland" | **100% of clicks and spend.** 5,570 of 5,584 impressions (99.75%) were Maryland-presence; a small number were non-Maryland or area-of-interest. | `geographic_view` |
| C8 | 97% delivery collapse presented as the ceiling's effect | Per-day normalised: **−84.8% impressions, −93.9% clicks, −97.1% cost, −100% conversions**. Strongest suspected cause, **not an isolated causal test**. | Confounders below |
| C9 | "$141.87 CPA against a $280 max CPQL" | **RAW CPA**, from 3 conversions on 9 clicks. Needs a **50.7% minimum qualification rate** to meet a $280 CPQL. | Small-sample labelling |
| C10 | "the account cannot spend $13,000" from Planner data | Withdrawn as stated. The Planner call covered **10 of 75 locations**; total market size cannot be extrapolated from it. | Planner geo cap |
| C11 | Quality Score described as causing high CPCs | QS is a **diagnostic**, not an auction input. Ad Rank uses live auction-time signals. | Corrected wording |
| C12 | AC Repair "held at $25" | Accurately: an **effective delivery hold** — 0 clicks and $0.00 in the four settled days after the ceiling. | Daily data |
| C13 | Air duct cleaning implied unsupported | **The live site offers it** in the lead-form service picker on every page. | Real-browser render |
| C14 | Manufacturer list treated as supported | Only **York** appears on the live website. The other 11 are unverified. | Real-browser render |
| C15 | "0 of 380 assets rated (LEARNING)" | Label is **NOT_APPLICABLE**, not LEARNING. Either way, no asset-level conclusions. | `ad_group_ad_asset_view` |

---

## 4. Package-by-package verdict on the six old fingerprints

| Fingerprint | Package | Verdict | Replaced by |
|---|---|---|---|
| `46C39C6B7091` | AMB-0909-CPC-1 | **SUPERSEDED / DO_NOT_EXECUTE** | AMB-0909B-CPC-INST-1 `DE376F91F449` |
| `D448BFDE4650` | AMB-0909-BUD-1 | **SUPERSEDED / DO_NOT_EXECUTE** | AMB-0909B-BUD-1 `752BF95EBD7C` |
| `23BE8FF0F24C` | AMB-0909-NEG-ADD-1 | **SUPERSEDED / DO_NOT_EXECUTE** | AMB-0909B-COMP-1 `05FBCBD34B4A` |
| `CE289F3508A2` | AMB-0909-NEG-RM-1 | **SUPERSEDED / DO_NOT_EXECUTE** | AMB-0909B-NEG-A `18143479027D` (subset only) |
| `A435FA09AC97` | AMB-0909-NEG-RM-2 | **SUPERSEDED / DO_NOT_EXECUTE** | AMB-0909B-NEG-A `18143479027D` (`commercial` only) |
| `11A79347A296` | AMB-0909-ADS-1 | **VALID, AWAITING APPROVAL — not executed this run** | not superseded |

The five superseded plan JSON files are **preserved byte-for-byte** with their original
fingerprints and validate-only receipts. Supersession is recorded in a separate artefact,
`evidence/2026-09-09b-package-ledger.json`, with a SHA-256 of each preserved file. No old
fingerprint was reused or modified; old and new fingerprint sets are provably disjoint.

---

## 5. Corrected budget analysis

### 5.1 The hard daily maximum

```
$13,000.00 / 30.4 = $427.6315789
```

Combined average daily budgets must not exceed **$427.63** for an uninterrupted future month.

| Configuration | Daily total | × 30.4 | vs $13,000 | Compliant? |
|---|---|---|---|---|
| Live today | $465.63 | $14,155.15 | **+$1,155.15** | **No** |
| Superseded AMB-0909-BUD-1 | $433.33 | $13,173.23 | **+$173.23** | **No** |
| **Replacement AMB-0909B-BUD-1** | **$421.55** | **$12,815.12** | **−$184.88** | **Yes** |

### 5.2 September budget-change reconstruction

`change_event` filtered to `CAMPAIGN_BUDGET`, 2026-08-11 → 2026-09-09:

| Timestamp | Campaign | Change | Interface | Login |
|---|---|---|---|---|
| 2026-08-22 01:23:35 | HVAC Installation | $138.16 → $176.15 | GOOGLE_ADS_API | access@greenmarketingfl.com |

**Zero September budget changes.** All five budgets have held their current value for the whole
month, so there is no mid-month step to prorate around.

### 5.3 Current-month (September) limit

| Component | Value |
|---|---|
| Served cost, five campaigns, 2026-09-01 → 09-09 | **$1,319.49** |
| Served cost, whole account, same window | $1,319.49 (the other 18 campaigns are paused) |
| Change day 2026-09-10 at the **highest budget in force** | $465.63 |
| Remaining **calendar** days 2026-09-11 → 09-30 | 20 |
| New daily total × 20 | $8,431.00 |
| **September maximum if executed 2026-09-10** | **$10,216.12** |
| Headroom vs $13,000 | **$2,783.88** |

Method: billed-to-date + highest budget in force on the change day + new daily total × remaining
**calendar** days. Remaining *scheduled advertising* days are deliberately not used.

### 5.4 Served vs billed cost — an honest limitation

`account_budget` reads `approved_spending_limit_type = INFINITE`, `amount_served = $187,016.31`
lifetime with $477.32 of adjustments, on an open window since 2023-04-22; `billing_setup` is
APPROVED. **Google Ads exposes no per-month billed figure through this API surface** without
monthly invoicing and the Invoice service. Served cost is the best available basis and can still
be restated downward by invalid-click credits.

That caveat is not theoretical here. Invalid clicks over 2026-08-14 → 09-09:

| Campaign | Billable clicks | Invalid clicks | Invalid rate |
|---|---|---|---|
| AC Repair | 29 | **941** | 97.01% |
| HVAC Repair | 29 | **621** | 95.54% |
| HVAC Installation | 114 | 93 | 44.93% |
| HVAC Replacement | 5 | 82 | 94.25% |
| Gas Boiler Repair | 0 | 42 | 100.00% |
| **Total** | **177** | **1,779** | — |

Invalid clicks are already excluded from cost, so this is not unbilled spend. It is a striking
traffic-quality signal — 1,779 filtered clicks against 177 billable — and evidence that ClickCease
and Google's own filtering are doing substantial work. It deserves its own investigation.

### 5.5 The replacement allocation

| Campaign | Budget ID | Now | Proposed | Rationale |
|---|---|---|---|---|
| AC Repair | 15787409435 | $141.45 | **$141.45** | unchanged; effective delivery hold at $25 |
| Gas Boiler Repair | 15787409438 | $42.76 | **$5.00** | 0 clicks ever; 20 monthly searches; LP gate FAIL |
| HVAC Installation | 15787409441 | $176.15 | **$176.15** | unchanged — the increase is withdrawn (C3) |
| HVAC Repair | 15787409444 | $78.95 | **$78.95** | unchanged |
| HVAC Replacement | 15787409447 | $26.32 | **$20.00** | 5 clicks, 0 conversions, **0.00% lost IS (budget) in every window** |
| | | **$465.63** | **$421.55** | |

Peak observed single-day September spend was $448.36 (2026-09-02), 96.3% of the combined budget —
so the budget *is* a real constraint on high-delivery days. The 2× single-day ceiling after the
change is $843.10.

---

## 6. Corrected CPC analysis

### 6.1 Visible vs privacy-hidden traffic — the correction that changes the conclusion

Every prior CPC scenario was built on search-term rows. Those rows do not contain all the traffic.

| Campaign | Campaign clicks / cost / conv | Visible in search terms | **Privacy-hidden** | Hidden conv share |
|---|---|---|---|---|
| AC Repair | 29 / $3,084.87 / 5 | 25 / $2,872.49 / 5 | 4 / $212.38 / 0 | 0.0% |
| HVAC Installation | 112 / $2,914.33 / 3 | 62 / $1,707.53 / 3 | 50 / $1,206.80 / 0 | 0.0% |
| **HVAC Repair** | 29 / $1,951.94 / **6** | 25 / $1,816.59 / **4** | 4 / $135.35 / **2** | **33.3%** |
| HVAC Replacement | 5 / $152.52 / 0 | 4 / $130.05 / 0 | 1 / $22.47 / 0 | — |

**HVAC Installation:** 44.6% of clicks are hidden but **0 of its 3 conversions are** — the visible
model sees every converting click, so the Installation scenarios are sound.
**HVAC Repair:** one third of its conversions are invisible to any search-term model, at a
blended hidden CPC of **$33.84** on 4 clicks. Per-click CPCs inside that block are not retrievable.

### 6.2 HVAC Installation — recommend $30 → $65

Live keyword verified: ad group 202339087634 holds exactly two ENABLED positives, both
`hvac installers near me` (PHRASE crit 295495761070, EXACT crit 315030681341), both `ELIGIBLE`.
**The removed `hvac installers` is confirmed not live.**

**Bid-adjustment audit — nothing can push the effective bid above $65:**

| Source | Rows with modifier ≠ 1.0 | Detail |
|---|---|---|
| `campaign_criterion` | 5 | DEVICE / **TABLET / ×0.0** on all five campaigns (tablet exclusion) |
| `ad_group_bid_modifier` | 0 | — |
| Audience / demographic criteria | 0 | none exist on the five |
| **Highest modifier found** | **×0.0** | can only reduce or suppress a bid, never raise it |

No location, ad-schedule, audience or demographic modifier exists. **A $65 ceiling means $65.**

| Cap | Visible clicks | Visible spend | Visible conv | Raw CPA |
|---|---|---|---|---|
| $25 | 33 | $600.15 | **0 of 3** | — |
| **$30 (live)** | 47 | $987.67 | **0 of 3** | — |
| $50 | 55 | $1,305.59 | **0 of 3** | — |
| **$65 (proposed)** | **62** | $1,707.54 | **3 of 3** | $569.18 |

All three conversions came from clicks priced $50.00 – $62.13. The live $30 ceiling admits 76% of
the click volume while excluding **every** converting click.

**Economics labelling, as required:**
- $141.87 (post-swap window 2026-08-29 → 09-03) is **RAW CPA**, not CPQL and not a qualified-lead
  cost.
- It rests on **3 raw primary conversions from 9 clicks. That is a small sample.**
- For that raw CPA to meet the $280 CPQL target, **at least 50.7% of those raw conversions must be
  qualified leads.**
- **The delivery-restoration case is strong. The economics are NOT high-confidence** — qualified
  outcomes are unavailable because `WHATCONVERTS_API_TOKEN` is empty.
- The survival table is a **descriptive sensitivity test on historical clicks, not an auction
  forecast.**

### 6.3 HVAC Repair — $60 rejected, keep $25

Campaign totals: 29 clicks, $1,951.94, 6 primary conversions, CPC $67.31, **raw CPA $325.32**
against a $250 maximum CPQL — already over target before any qualification discount.

| Cap | Visible clicks | Visible spend | Visible conv | Visible raw CPA | vs $250 max CPQL |
|---|---|---|---|---|---|
| **$25 (live)** | 6 | $116.67 | 1 of 4 | **$116.67** | within |
| $35 | 7 | $144.27 | 1 of 4 | $144.27 | within |
| $40 | 7 | $144.27 | 1 of 4 | $144.27 | within |
| $45 | 7 | $144.27 | 1 of 4 | $144.27 | within |
| **$60 (rejected)** | 13 | $474.06 | 1 of 4 | **$474.06** | **EXCEEDS by $224.06** |
| none | 25 | $1,816.59 | 4 of 4 | $454.15 | EXCEEDS by $204.15 |

Plus **4 privacy-hidden clicks carrying 2 more conversions at a $33.84 blended CPC**, which the
table cannot cap or model.

The three visible converting clicks sit at **$6.16 (08-27), $153.03 (08-20, 2 conversions) and
$153.06 (08-24)** — a barbell, not a distribution with a usable middle. $35 through $45 return
identical results because no click was ever priced in that band.

**Verdict: no ceiling between $25 and $60 has credible economics.** $60 buys 7 more clicks and
$357 of spend for zero additional visible conversions. **Keep $25. No controlled test is proposed
this run** — a test that adds one click is not a test. Priority moves to landing-page experience
(Quality Score 2, BELOW_AVERAGE), RSA relevance, and repairing conversion measurement.

### 6.4 AC Repair — keep $25, described accurately

AC Repair is under an **effective delivery hold**: 0 clicks and $0.00 in the four settled days
after the ceiling. Raw CPA $616.97 against a $150 maximum CPQL; the cheapest modelled cap
retaining a majority of conversions is $110 at $298.35 raw CPA. Held pending qualified-lead
evidence and landing-page/RSA improvement. Its $141.45 budget is deliberately left in place so
the hold stays cheap to reverse.

### 6.5 Gas Boiler Repair and HVAC Replacement

Both remain **uncapped** and both stay that way. Gas Boiler has never taken a click and its
landing page still fails the service gate. HVAC Replacement has 5 clicks all time.

---

## 7. Corrected negative-keyword work

### 7.1 Reconciling 88 / 23 / 33 / 107

| Figure | What it actually counts |
|---|---|
| **80** | distinct (match, text) **campaign-level** negatives colliding with a converting term |
| **18** | distinct (match, text) campaign-level negatives colliding with a BOFU probe |
| **88** | **the union** — the correct collision count. The September 9 report printed 80 in §0/§9 and 88 in §7; 80 omitted probe-only collisions. |
| **23** | the **REMOVE** verdicts within those 88, campaign level only (ROUTING 5, KEEP 60) |
| **22** | distinct texts in AMB-0909-NEG-RM-1 · **18** distinct texts in AMB-0909-NEG-RM-2 · **7** present at both layers |
| **33** | **distinct texts across both packages** (22 + 18 − 7) |
| **89** | RM-1 operations — 22 texts × 1–5 campaign placements each |
| **107** | **89 + 18 = total removal operations** across both packages |

Row-level evidence for all 107, with criterion ID, scope, match type, blocked probes, blocked
historical terms, cost and conversions:
`evidence/2026-09-09b-removal-row-evidence.csv`. Every row re-verified live and ENABLED.

### 7.2 Package A — high-confidence unblock — **16 operations** — `18143479027D`

| Scope | Match | Text | Placements | Justification |
|---|---|---|---|---|
| Campaign | PHRASE | `savage` | 5 | **Savage, Maryland** (geoTargetConstants/1018704) is one of the 75 live targets. Blocked 300 of 300 service-by-place probes for that city. |
| Campaign | PHRASE | `free` | 5 | Blocks `hvac free estimate near me`. Free estimates are an approved, verified proposition. |
| Campaign | PHRASE | `licensed` | 5 | Blocks `licensed hvac contractor near me`. Licensed and insured is an approved, verified claim. |
| **Account** | BROAD | `commercial` | 1 | See below. |

**`commercial` evidence.** The live website advertises commercial work: the homepage and the
furnace-repair page both name it, `/services/hvac/condominium-hvac/` is a dedicated page, and the
site carries a `/category/commercial-hvac/` blog category including a Maryland BEPS compliance
article. Three commercial queries have already converted in this account —
`commercial ac repair near me`, `commercial hvac companies near me` and `commercial furnace
repair` — carrying **3.83 primary conversions**. BROAD `commercial` is also named in the Green
Marketing rules as a word that must not be broad-negatived.

This package **deliberately pairs campaign-level and account-level removals in one atomic
mutate**, so the two layers cannot end up half-applied.

### 7.3 Package B — manufacturers — **HOLD, no operations**

The correction brief asked for manufacturer confirmation. A real-browser render of 14 pages of
`ambientcoolingandheating.com` names exactly **one** manufacturer: **York**.

| Finding | Detail |
|---|---|
| Manufacturers named on the live site | **york** — and nothing else |
| Is `york` blocked? | **No.** Not at campaign token level, not in the account-level set. Only `hl bowman york pa`, `hvac in york pa` and `new york` exist, which are out-of-area place negatives. |
| Blocked manufacturer tokens | carrier, trane, lennox, goodman, daikin, rheem, mitsubishi, amana, bosch, bryant, armstrong, ruud, midea — at **both** campaign (×2) and account level |
| Verified eligibility for any of them | **None** |

**Nothing is removed.** The correction brief's distinction is right and is preserved:
`carrier hvac repair near me` could be BOFU service demand, but a query for a **distributor,
corporate office, parts counter or manufacturer location** is not equivalent. The six
supply-house/corporate/location EXACT negatives named in the brief are **RETAINED**:

```
[carrier enterprise laurel]
[carrier mid atlantic hanover maryland]
[carrier mid atlantic near me]
[ce carrier enterprise near me]
[daikin comfort technologies locations]
[daikin elkridge md]
```

Also retained: roughly 40 multiword manufacturer price/dealer negatives such as
`carrier hvac prices`, `lennox dealers near me`, `trane dealers near me`,
`mitsubishi mini split installation cost`.

**Designed pilot, blocked on one input.** Once the client confirms which brands they install or
service: build a single brand-plus-service ad group in the matching campaign, EXACT match only,
`{brand} + repair|install|service|replacement + near me`, with the corporate/distributor
negatives kept in place, a $200 stop loss and a 14-settled-day read. Do not open a brand token.

**`al`, `american` and `mr` are preserved**, exactly as the brief directs. Their observed
collisions:

| Token | Whole-word matches in observed search terms | Cost |
|---|---|---|
| `al` | **0 rows** — dormant, never blocked an observed query | $0.00 |
| `american` | 2 rows: `american mechanical services of maryland`, `american pride hvac` — both competitors | $0.00 |
| `mr` | 1 row: `mr cool cape coral fl` — MRCOOL brand, out of area | $0.00 |

`american` also blocks American Standard, a manufacturer. All three stay until the
manufacturer/name policy is settled.

### 7.4 Package C — additional services — **HOLD, no operations**

Real-browser evidence, with exact on-page text:

| Service | On the live site? | Evidence |
|---|---|---|
| **Air duct cleaning** | **YES** | "Air Duct Cleaning" is a selectable option in the lead-form **Service** picker on every page. No dedicated landing page. |
| **Dehumidification** | **YES** | Dedicated page `/services/indoor-air-quality/drying-dehumidification-services/` — "Efficient Drying and Dehumidification Services… prevent structural damage while avoiding mold growth". Plus `/services/hvac/desert-air-pool-hvac/` and a pool-room-dehumidifier blog category. |
| **Geothermal** | **YES** | Dedicated page `/services/hvac/geothermal-hvac/` — "our technicians are experts at installation, maintenance, and repair". |
| **Thermostats** | Partial | Mentioned in body copy on the heating-services, oil-furnace-installations and AC-repair pages. No dedicated page, no form option. |
| **Humidifiers** (not de-) | **NO** | Absent from every rendered page. |

**The September 9 report was wrong to imply air duct cleaning was unsupported.** It is offered.

**But the brief is right that opening these terms across all five campaigns is the wrong move.**
Dehumidification here is *structural drying and mold prevention*, not "buy a dehumidifier" —
routing that demand to `/ac-repair/` would waste it. None of these services has a campaign, an ad
group or a paid landing page.

**Required sequence before any term is opened:**
1. Client confirms which of air duct cleaning, dehumidification, geothermal and thermostats they
   want paid leads for.
2. Choose the destination campaign, build a dedicated ad group, and point it at the matching
   page — `/services/indoor-air-quality/drying-dehumidification-services/` and
   `/services/hvac/geothermal-hvac/` already exist; air duct cleaning has no page at all.
3. Prepare cross-campaign negatives so each service routes to exactly one destination.
4. Keep the terms blocked everywhere else until that routing exists.

### 7.5 Package D — dealer and installer searches — **HOLD, no operations**

| Term | Verdict | Why |
|---|---|---|
| `[daikin cerca de mi]` | HOLD | Spanish-language query. Every Ambient page renders in English only; there is no Spanish landing page or language handling. Daikin eligibility also unconfirmed. |
| `[geothermal maryland]` | HOLD | Geothermal **is** a verified service with a live page, but none of the five campaigns is a geothermal campaign. Opening it would route the demand to an AC or HVAC repair page. Needs Package C routing first. |
| `[trane authorized dealers near me]` | HOLD | Trane eligibility unconfirmed; "authorized dealer" is brand-directory intent, not service intent. |
| `[trane installers near me]` | HOLD | Trane eligibility unconfirmed. |

### 7.6 Competitor additions — **3 operations** — `05FBCBD34B4A`

Four candidates were independently verified. **Two passed.**

**VERIFIED — Arundel Cooling & Heating Co., Inc.**
707 Nursery Rd, Linthicum Heights, MD 21090 — itself one of Ambient's 75 live location targets.
Trading since 1971, now part of Service Experts; residential and light commercial HVAC across
Baltimore, Columbia, Annapolis, Ellicott City and Bowie. Also a Carrier dealer.
Observed: `arundel cooling and heating reviews` 8 impr / 1 click / **$20.44**;
`arundel cooling and heating` 6 impr / 0 clicks; `arundel heating and cooling maryland` 1 impr.

**VERIFIED — Maryland Mechanical Heating & Cooling LLC**
marylandhvacs.com, Maryland HVACR licence #22169, founded 2023. A separate Maryland Mechanical
Services LLC (mmshvacllc.com) also trades in MD/VA/DC.
Observed: `maryland mechanical heating & cooling` 4 impr / 1 click / **$50.17**.

**NOT VERIFIED — not added:**
- `"all about air"` — no identifiable Maryland HVAC contractor found. 4 impr, 0 clicks, $0.00.
- `"home comfort hvac"` — no uniquely identifiable entity. Several unrelated "Comfort"-named MD
  contractors exist (Comfort Air, Maryland Comfort, Mr Comfort, Total Home Comfort) and "home
  comfort" is generic trade language. 3 impr, 0 clicks, $0.00.

**The match-type trap, and how preflight caught it.** The first draft used PHRASE
`arundel cooling and heating`. Preflight flagged that it also blocks **`anne arundel cooling and
heating`**, which produced a **primary phone-call conversion** in the legacy Heating Maintenance
campaign — and it sits one word from `hvac anne arundel county`. Anne Arundel County is Ambient's
core service area. The package was narrowed to **EXACT** on the two unambiguous brand queries.
`arundel cooling and heating` on its own is **deliberately not blocked in any match type**: 6
impressions, 0 clicks, $0.00 is not worth the risk.

| # | Match | Text | Campaign |
|---|---|---|---|
| 1 | **EXACT** | `arundel cooling and heating reviews` | HVAC Installation |
| 2 | **EXACT** | `arundel heating and cooling maryland` | HVAC Installation |
| 3 | **PHRASE** | `maryland mechanical heating` | HVAC Installation |

No BROAD negative is created. Nothing is built from *home*, *comfort*, *maryland*, *mechanical*,
*heating*, *air* or *cooling*.

### 7.7 Paste-ready blocks

**REMOVE — Package A, campaign level, all five campaigns**
```
"free"
"licensed"
"savage"
```

**REMOVE — Package A, account-level list 11252984411**
```
commercial
```

**ADD — Package COMP-1, HVAC Installation (24132507747)**
```
"maryland mechanical heating"
[arundel cooling and heating reviews]
[arundel heating and cooling maryland]
```

---

## 8. Conflict and deduplication tests

Every proposed operation was tested against the full protected register. **0 FAIL, 0 WARN.**

| Test | Result |
|---|---|
| Fingerprint recomputes from plan contents | 4/4 PASS |
| New fingerprints disjoint from all six prior ones | PASS |
| Removal targets live and ENABLED | 15/15 campaign + 1/1 account |
| Removal target text and match type match the live resource | 15/15 |
| No duplicate removal targets | PASS |
| `savage` / `free` / `licensed` present on all five campaigns | 5 / 5 / 5 |
| None of the 29 held terms appears in Package A | PASS |
| Additions not already present at campaign, ad group or account level | 3/3 |
| Additions block 0 of **67** BOFU probes | 3/3 |
| Additions block 0 of **304** account-wide converting terms | 3/3 |
| Additions block 0 of **80** live Maryland place tokens | 3/3 |
| **Anne Arundel County guard** (5 county probes × 3 negatives) | 15/15 PASS |
| No BROAD additions | PASS |
| Negative word limit (≤10) and character limit (≤80) | 3/3 |
| Budget before-states match live | 2/2 |
| Budget refs = 1 (no shared budget) | 2/2 |
| 30.4-day exposure within $13,000 | PASS ($184.88 headroom) |
| HVAC Installation budget untouched | PASS |
| CPC package is Installation-only | PASS |
| AC Repair and HVAC Repair ceilings untouched at $25 | PASS |
| No bid modifier > ×1.0 anywhere | PASS |

---

## 9. Ads, CTR and measurement

### 9.1 ADS-1 — retention confirmed, all three conditions met

| Condition | Result |
|---|---|
| Both target ads still ENABLED and DISAPPROVED / FULLY_LIMITED | **Yes** — 820900825434, 820944944368 |
| Each affected ad group retains ≥2 ENABLED + APPROVED RSAs | **Yes** — 2 each |
| Only status in the update mask | **Yes** — the executor hard-codes `mask(["status"])` |

**This is inert-status cleanup. It is not a CTR or delivery improvement** — a FULLY_LIMITED ad
cannot serve, so pausing it changes no delivery.

### 9.2 AC Repair ads pointing at `/hvac-replacement/` — no action needed

Ads 820900825422 and 820900825425 carry `/hvac-replacement/` while sitting in the AC Repair
campaign. Both live in ad group **202339087874, which is REMOVED**. AC Repair's only ENABLED ad
group is 202339087834. **0 servable mismatched-URL ads.**

### 9.3 RSA assets and headline coverage

380 asset rows with delivery. **Every one carries `performance_label = NOT_APPLICABLE`** — Google
is not rating any headline or description at this volume. No asset-level A/B conclusion is
available, and none is claimed.

| Campaign | Ad | Headlines | **Location-insertion tags** | City/MD headlines | Service headlines |
|---|---|---|---|---|---|
| AC Repair | 820900825416 | 15 | **0** | 3 | 9 |
| AC Repair | 820900825419 | 15 | **0** | 0 | 3 |
| HVAC Installation | 821319509197 | 15 | **0** | 4 | 12 |
| HVAC Installation | 821319509200 | 15 | **0** | 2 | 7 |
| HVAC Repair | 821714108336 | 15 | **0** | 3 | 9 |
| HVAC Repair | 821714108339 | 15 | **0** | 2 | 7 |
| HVAC Replacement | 821319509203 | 15 | **0** | 4 | 10 |
| HVAC Replacement | 821319509206 | 15 | **0** | 2 | 7 |
| Gas Boiler Repair | 821319509209 | 15 | **0** | 4 | 13 |
| Gas Boiler Repair | 821319509212 | 15 | **0** | 2 | 10 |

**Zero location-insertion tags across all ten live ads.** Every city reference is hard-coded, and
only Severn, Severna Park and Columbia appear — against **75 targeted locations**. A searcher in
Annapolis, Glen Burnie, Bowie or Odenton never sees their own city. Ad 820900825419 names no
location at all and only 3 of 15 headlines name the service. This is a real, actionable finding.
It is recorded, not packaged — RSA edits should follow delivery restoration, when there is enough
traffic to read the result.

### 9.4 Sitelinks

All five campaigns carry the same 8 sitelinks: Customer Reviews, View Our Work, Contact Ambient,
Service Areas, plus **the other four services**. Cross-service sitelinks help a mis-routed
searcher self-correct, but they also dilute campaign intent, and the SITELINKS click type
returned 26 clicks and $1,284.80 for **1 primary conversion**. Worth reviewing once delivery
resumes. No change proposed now.

### 9.5 Mobile vs desktop by campaign

| Campaign | Device | Impr | Clicks | CTR | CPC | Cost | Primary conv |
|---|---|---|---|---|---|---|---|
| AC Repair | Desktop | 347 | 4 | 1.15% | $55.45 | $221.80 | 0 |
| AC Repair | Mobile | 532 | 25 | 4.70% | $114.52 | $2,863.07 | **5** |
| HVAC Installation | Desktop | 1,556 | 31 | 1.99% | $22.33 | $692.32 | 0 |
| HVAC Installation | Mobile | 1,863 | 81 | 4.35% | $27.43 | $2,222.01 | **3** |
| HVAC Repair | Desktop | 490 | 13 | 2.65% | $55.36 | $719.71 | 0 |
| HVAC Repair | Mobile | 568 | 16 | 2.82% | $77.01 | $1,232.23 | **6** |
| HVAC Replacement | Desktop | 148 | 1 | 0.68% | $15.02 | $15.02 | 0 |
| HVAC Replacement | Mobile | 51 | 4 | 7.84% | $34.38 | $137.50 | 0 |

**No desktop bid adjustment is proposed.** HVAC Installation is the only campaign with a
non-trivial desktop sample — 31 clicks, $692.32, 0 conversions. At its mobile CVR of 3.7%, the
expected count from 31 clicks is ~1.15, so observing zero has roughly a 32% probability by chance
alone. That is suggestive, not evidence. Every other campaign has 1–13 desktop clicks. Revisit
after delivery is restored.

### 9.6 Call bid adjustments — answer rate now available, qualification still not

`call_view` retains **547 calls**: 537 RECEIVED, 10 MISSED — a **98.2% answer rate**. 529 were
HIGH_END_MOBILE_SEARCH, 18 manually dialled. 275 of 547 (50.3%) ran ≥60 seconds.

The answer-rate half of the prerequisite is now satisfied. **Qualification is not**, and duration
is not qualification. **No call bid adjustment is proposed.**

### 9.7 Quality Score — a diagnostic, not an auction input

Corrected wording. Quality Score is a 1–10 **diagnostic estimate** reported at keyword level. It
is not itself an input to the ad auction; Ad Rank is computed at auction time from bid, live
quality signals, context, and expected asset impact. QS 2 on `hvac repair near me` and QS 4 on
`ac repair near me`, both with BELOW_AVERAGE expected CTR and (for HVAC Repair and Replacement)
BELOW_AVERAGE landing-page experience, are **symptoms consistent with** the observed CPCs and
rank loss. The September 9 report's claim that QS "mechanically caused" the CPCs is withdrawn.

### 9.8 Measurement corrections

**The 14 vs 13 discrepancy is resolved — the September 9 report had a transcription error.**

| Conversion action | Primary conversions | Campaigns |
|---|---|---|
| Calls from ads | **5** | AC Repair 3, HVAC Repair 2 |
| Ambient Cooling - LP - Submit Lead Forms | **5** | AC Repair 2, HVAC Repair 2, HVAC Installation 1 |
| WC Lead | **4** | HVAC Installation 2, HVAC Repair 2 |
| **Total** | **14** | matches `metrics.conversions` exactly, difference 0.00 |

The prior report listed Submit Lead Forms as 4, producing a false 13.

**Duplicate-conversion testing:**

| Layer | Result |
|---|---|
| Within-action | **Structurally prevented** — all three biddable actions are `ONE_PER_CLICK` |
| Cross-action | **NOT TESTABLE.** One caller who also submits the form can be counted by Calls from ads *and* WC Lead *and* the landing-page form action. Requires WhatConverts lead IDs joined to GCLID. `WHATCONVERTS_API_TOKEN` is empty. |
| Caller-level | **NOT TESTABLE.** `call_view` exposes only the caller **area code**, never the number. Same-area-code-same-minute candidates: 1. |
| By timestamp / lead ID | Not available without CRM data |

**No conversion in this account is described as qualified.** Raw CPA, CPQL, sold-job CPA and
revenue are kept strictly separate throughout. The only raw-CPA figure quoted is HVAC
Installation's **$141.87**, explicitly labelled RAW.

---

## 10. Location wording — corrected

Replacing the September 9 phrasing everywhere:

- **100% of clicks and 100% of spend came from users in targeted Maryland locations.**
  185 of 185 `user_location_view` rows returned `targeting_location = true`.
- **A small number of non-Maryland and area-of-interest impressions occurred.** 5,570 of 5,584
  impressions (99.75%) were Maryland-presence. 7 were presence-in-AL/LA/MS/WY; 12 were
  AREA_OF_INTEREST in DC, NY, TX, FL and PA.
- **Zero out-of-state clicks and zero out-of-state spend were observed.**

The claim "100% of impressions came from Maryland" is withdrawn.

---

## 11. Causality — normalised per day, with confounders disclosed

| Metric | Before 08-14 → 09-03 | After 09-05 → 09-08 | Change |
|---|---|---|---|
| Days | 21 | 4 | — |
| **Impressions / day** | 252.7 | 38.5 | **−84.8%** |
| **Clicks / day** | 8.19 | 0.50 | **−93.9%** |
| **Cost / day** | $382.15 | $11.27 | **−97.1%** |
| **Conversions / day** | 0.667 | 0.000 | **−100.0%** |

**Confounders in the post-change window, disclosed:**

1. Only **4 days** against 21 before.
2. It contains **2 weekend days** — Saturday 2026-09-05 and Sunday 2026-09-06.
3. **Monday 2026-09-07 was Labor Day**, a US federal holiday. The entire window sits inside the
   Labor Day long weekend, a low-intent period for home services.
4. The **ad schedule excludes Sunday entirely**, so one of the four days could never serve.
5. **Negative coverage also changed** around the window: 372 campaign negatives added 2026-09-01
   and 125 more on 2026-09-09.

**The ceilings are the strongest suspected cause of the suppressed delivery. This is not a clean,
isolated causal test and must not be reported as one.** The supporting signal is the shape rather
than the size: on 2026-09-05 and 09-07 the only two clicks that got through cost **$21.46 and
$23.62**, both immediately under the $25 cap, while impression share lost to **rank** rose to
76–86% across the five.

---

## 12. Keyword Planner — scope correction

The Planner request covered **10 of the 75 live locations** (the API caps `geo_target_constants`
at 10). Figures from it describe that 10-city sample only.

**The claim that the account cannot spend $13,000, as argued from that sample, is withdrawn.**
What can be said: within the sampled 10 cities, seed-level demand is thin for Gas Boiler Repair
(20 monthly searches at the strongest term, no bid estimate) and top-of-page LOW for the core
terms is $14.87–$23.49. A full-footprint feasibility answer requires sweeping all 75 targets in
batches of 10, which is a separate piece of work.

---

## 13. Staged execution order

**Nothing may be executed from this run.** When approvals arrive, this is the order and why.

| Stage | Package | Fingerprint | Ops | Why here |
|---|---|---|---|---|
| **a** | AMB-0909B-BUD-1 | `752BF95EBD7C` | 2 | Bring the configuration inside the $13,000 cap **before** restoring any delivery. |
| **b** | AMB-0909B-CPC-INST-1 | `DE376F91F449` | 1 | Installation-only CPC restoration. Single variable, single campaign. |
| **c** | AMB-0909B-NEG-A | `18143479027D` | 16 | High-confidence unblocks. Widens matching, so it follows the budget fix. |
| **d** | AMB-0909B-COMP-1 | `05FBCBD34B4A` | 3 | Verified competitor negatives. Narrows matching; harmless in any order. |
| **e** | AMB-0909-ADS-1 | `11A79347A296` | 2 | Inert cleanup. No delivery effect, so it can wait. |
| **f** | — | — | 0 | **Monitor for 14 settled days before any further change.** |

Stages b and c both change what can serve. Running them a day apart makes the readback attributable.

---

## 14. Readback and rollback requirements

**Readback assertions**

| Package | Assert immediately after execution |
|---|---|
| BUD-1 | 15787409438 = 5000000; 15787409447 = 20000000; 15787409435 / 15787409441 / 15787409444 **unchanged**; combined daily = **$421.55**; ×30.4 = $12,815.12 |
| CPC-INST-1 | HVAC Installation ceiling = 65000000; **AC Repair and HVAC Repair still 25000000**; all five still TARGET_SPEND; geo 375; schedules 30 |
| NEG-A | Campaign negatives on the five **6,160 → 6,145**; account set 11252984411 **272 → 271**; `savage`/`free`/`licensed` absent from all five; `commercial` absent from the set; **the other 16 shared sets untouched and still 0 attached to the five** |
| COMP-1 | HVAC Installation negatives **+3**; the three texts present with the recorded match types; no other campaign changed |
| ADS-1 | Both ads PAUSED; each ad group still ≥2 ENABLED + APPROVED RSAs |

**Unrelated-resource counts to re-assert after every package** (all verified at 2026-09-09 18:06):

```
campaigns non-removed     23      geo targets on the five    375
campaigns ENABLED          5      ad schedules on the five    30
shared sets               17      IP blocks (ClickCease)    2796
conversion actions        16      manager links   3373711342 + 2815082755 ACTIVE
tracking_url_template   present, ClickCease
```

**Rollback**

| Package | Inverse |
|---|---|
| BUD-1 | `amount_micros` back to 42760000 and 26320000 |
| CPC-INST-1 | `target_spend.cpc_bid_ceiling_micros` back to 30000000 |
| NEG-A | Re-create 15 campaign negatives from the recorded text + match + campaign id; re-add `commercial` [BROAD] to set 11252984411 |
| COMP-1 | Remove the 3 created criteria by returned resource name |
| ADS-1 | Both `ad_group_ad` back to ENABLED |

Every package is one atomic mutate with `partial_failure = false`. On any failure: **stop, do not
rerun.** Inventory resource IDs from the receipt, diff against the plan, propose a targeted
recovery.

**Monitoring after stage b**

| Checkpoint | Read |
|---|---|
| 24 hours | Delivery resumed on HVAC Installation; CPC distribution; readback counts hold |
| 72 hours | Blended CPC vs the $62.13 observed converting maximum; no new disapprovals |
| 7 settled days | New search terms after the Package A unblocks; primary conversions; raw CPA |
| 14 settled days | Raw CPA vs $280; September pacing vs $13,000; decide on HVAC Repair and AC Repair |

**Rollback thresholds** — raw primary conversions only, because qualified outcomes are
unavailable:

| Trigger | Threshold | Action |
|---|---|---|
| HVAC Installation blended CPC | > $55 over 7 settled days | ceiling $65 → $50 |
| HVAC Installation raw CPA | > $280 over 14 settled days with ≥5 conversions | ceiling → $45, re-evaluate |
| September projected month-end | > $12,000 | reduce HVAC Installation budget first |
| Post-unblock search terms | any `commercial` term ≥5 clicks, 0 conversions | re-add `commercial` as PHRASE + service qualifier, never BROAD |
| `savage` unblock | any Savage MD term ≥5 clicks, 0 conversions | re-add as EXACT on the specific query |
| Any campaign | 0 conversions on ≥30 clicks after 14 settled days | pause and re-audit |

---

## 15. Consolidated approval block

Only newly validated, decision-safe packages. **Nothing was executed. This report is not
approval.**

### Safe, reversible

```
APPROVE AMB-0909B-BUD-1        752BF95EBD7C    2 operations
```
Gas Boiler Repair $42.76 → $5.00; HVAC Replacement $26.32 → $20.00. Combined $465.63 → **$421.55**
= $12,815.12 over 30.4 days, $184.88 inside the cap. HVAC Installation's budget is **not** raised.

```
APPROVE AMB-0909B-CPC-INST-1   DE376F91F449    1 operation
```
HVAC Installation only: CPC bid ceiling $30 → $65. AC Repair and HVAC Repair untouched at $25.

```
APPROVE AMB-0909B-COMP-1       05FBCBD34B4A    3 operations
```
Two EXACT + one PHRASE negative on HVAC Installation for two independently verified competing
contractors.

```
APPROVE AMB-0909-ADS-1         11A79347A296    2 operations
```
Carried forward unchanged and re-verified. Inert-status cleanup; not a performance change.

### Destructive — separate approval line

```
APPROVE DESTRUCTIVE AMB-0909B-NEG-A   18143479027D   16 operations
```
Remove PHRASE `savage`, `free` and `licensed` from all five campaigns, plus account-level BROAD
`commercial`. Campaign-level and account-level changes land in one atomic mutate.

### Explicitly NOT proposed

- Any HVAC Repair CPC change — $60 rejected; **$25 stands**; no test package created.
- Any AC Repair CPC change — effective delivery hold stands.
- Any manufacturer unblock — only York is evidenced, and York is not blocked.
- Any additional-service unblock — routing and landing pages do not exist yet.
- Any dealer/installer unblock — brand eligibility and language handling unverified.
- Removal of `al`, `american` or `mr` — preserved as instructed.
- Removal of the six supply-house/corporate/location EXACT negatives — retained as instructed.
- Any desktop or call bid adjustment, RSA rewrite, sitelink change, or conversion-action change.

---

## 16. The one unresolved business decision

**Do the $150 / $250 / $280 CPQL limits take priority over spending the full $13,000?**

The two goals are in direct conflict on current evidence:

| Campaign | Raw CPA (all time) | Max CPQL | Gap |
|---|---|---|---|
| AC Repair | $616.97 | $150 | **4.1× over** |
| HVAC Repair | $325.32 | $250 | 1.3× over |
| HVAC Installation | $971.44 all-time / **$141.87 post-swap** | $280 | over / **within** |

These are **raw CPAs**. A qualified-lead cost is higher by the reciprocal of the qualification
rate, which is unknown.

- **If the CPQL limits take priority:** AC Repair and HVAC Repair stay held, only HVAC
  Installation is restored, and September lands near $10,000 — roughly $3,000 under the cap. This
  is the assumption every package in this report is built on.
- **If spending the $13,000 takes priority:** AC Repair's ceiling must rise to about $110–$130,
  which the model puts at a $281–$298 raw CPA against a $150 target, and the CPQL limits must be
  formally revised to match job value and gross margin.

**Recommendation: keep the CPQL limits, accept the underspend, and spend the difference on
qualified-lead measurement.** Restoring `WHATCONVERTS_API_TOKEN` would convert every raw CPA in
this report into a real CPQL and let the next decision be made on economics instead of proxies.

*This question cannot be answered from the account. It needs the owner.*

---

## 17. Evidence index

| File | Contents |
|---|---|
| `evidence/2026-09-09b-state-and-drift.json` | identity gate, live state, six-package drift check, 7,414 change events with `user_email` |
| `evidence/2026-09-09b-budget-analysis.json` | 30.4 arithmetic, September change reconstruction, served vs billed, invalid clicks, windowed impression share |
| `evidence/2026-09-09b-cpc-analysis.json` | visible/hidden split, conversion reconciliation, bid-modifier audit, all campaign scenarios |
| `evidence/2026-09-09b-negative-reconciliation.json` | the 88 / 23 / 33 / 107 reconciliation |
| `evidence/2026-09-09b-removal-row-evidence.csv` | all 107 removals, row level |
| `evidence/2026-09-09b-removal-groups.json` | intent grouping into packages A–D |
| `evidence/2026-09-09b-website-services.json` | 14 rendered pages, services and manufacturers |
| `evidence/2026-09-09b-service-proof.json` | exact on-page text for each contested service |
| `evidence/2026-09-09b-ads-and-causality.json` | ADS-1 recheck, assets, sitelinks, device, per-day causality, call log |
| `evidence/2026-09-09b-local-preflight.json` | preflight result |
| `evidence/2026-09-09b-package-ledger.json` | supersession ledger with SHA-256 of each preserved plan + final unchanged proof |
| `clients/ambient-cooling-heating/plans/AMB-0909B-*.json` | the four replacement packages |
| `plans/AMBIENT-2026-09-09b-packages.json` | combined manifest |
| `receipts/validate-only/AMB-0909B-*-2026-09-09b.json` | four validate-only receipts |

**Sources for competitor verification:**
[Arundel Cooling & Heating — BBB](https://www.bbb.org/us/md/linthicum/profile/heating-and-air-conditioning/arundel-cooling-heating-co-inc-0011-563) ·
[Arundel Cooling & Heating — Yelp](https://www.yelp.com/biz/arundel-cooling-and-heating-linthicum-heights-2) ·
[Arundel Cooling & Heating — Carrier dealer listing](https://www.carrier.com/us/en/residential/dealers/md/linthicum-heights/707-nursery-rd-3274-loc) ·
[Maryland Mechanical Heating & Cooling LLC](https://marylandhvacs.com/) ·
[Maryland Mechanical Services LLC](https://mmshvacllc.com/) ·
[Maryland HVACR licensing board](https://www.labor.maryland.gov/license/hvacr/)

---

*Correction run. Zero mutations executed. Every external change requires its own explicit
approval line above.*
