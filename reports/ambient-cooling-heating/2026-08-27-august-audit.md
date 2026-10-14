# Ambient Cooling - Live | August account audit | 2026-08-27

**Account:** Ambient Cooling - Live · **Child customer ID:** 2401959466 · **Currency:** USD ·
**Timezone:** America/New_York · **Vertical:** heating-cooling
**Services in scope:** AC Repair (primary), HVAC Repair, HVAC Installation, HVAC Replacement, Gas Boiler Repair
**Mode:** read, audit and draft. **No external change was made during this run.**

---

## 1. Identity and validator status

| Gate | Result | Evidence |
|---|---|---|
| `customer.descriptive_name` | PASS | exactly `Ambient Cooling - Live` |
| `customer.id` | PASS | exactly `2401959466` (child, not the MCC) |
| Non-manager account | PASS | `customer.manager = false` |
| Non-test account | PASS | `customer.test_account = false` |
| Timezone | PASS | `America/New_York` |
| Currency | PASS | `USD` |
| Green Marketing manager 3373711342 | PASS | link `ACTIVE` |
| ClickCease manager 2815082755 | PASS | link `ACTIVE`, protected, untouched |
| `scripts/validate_work_order.py` | PASS | `Ambient Cooling - Live \| 2401959466 \| heating-cooling \| AC Repair` |
| `scripts/verify_setup.py --online` | PASS | `Connection: OK` |
| Concurrent writer on 2401959466 | NONE | 3 unrelated Python processes on this machine target other accounts; none references 2401959466. No lock files. |
| Last change event on the account | 2026-08-22 09:36:07 ET | Nothing has touched the account since the automotive negatives. |

**WhatConverts:** `WHATCONVERTS_API_TOKEN` is present as a variable name but **empty**.
**Lead quality is therefore unverified.** Nothing in this report calls a Google Ads
conversion a qualified lead.

---

## 2. Date windows

| Window | Dates | Status |
|---|---|---|
| August month to date | 2026-08-01 → 2026-08-26 | **settled** |
| Current day | 2026-08-27 | **PARTIAL — never mixed into a settled comparison** |
| Since the last optimization | 2026-08-22 → 2026-08-26 | settled |
| Before the 2026-08-22 changes | 2026-08-18 → 2026-08-21 | settled, 4 days |
| Change day | 2026-08-22 | partial, reported separately |
| After the 2026-08-22 changes | 2026-08-23 → 2026-08-26 | settled, 4 days |
| Launch to date | 2026-08-14 → 2026-08-26 | settled |
| Last 30 / 90 / 365 / all history | through 2026-08-27 | identical to launch-to-date plus the partial day — the five campaigns have no delivery before 2026-08-14 |

The before and after windows are equal-length settled windows that both exclude
2026-08-22, the day the changes landed.

---

## 3. August account performance and pacing

### Settled month to date (2026-08-01 → 2026-08-26)

| Metric | Value |
|---|---|
| Impressions | 3,403 |
| Clicks | 113 |
| CTR | 3.32% |
| Spend | **$4,820.12** |
| Average CPC | **$42.66** |
| Primary conversions | **6.00** |
| Conversion rate | 5.31% |
| CPL (Primary) | **$803.35** |
| Qualified leads | **unverified** — WhatConverts token empty |
| Cost per qualified lead | **cannot be calculated** |
| Sold jobs, revenue, gross profit, ROAS, profit after ad spend | **cannot be calculated** |

**Missing business inputs** blocking profit reporting: qualified-lead flags, sold-job
outcomes, job revenue, gross margin percentage, and any non-media cost. Without these,
CPL is the deepest metric this account currently supports.

Current day 2026-08-27 (partial, HVAC Installation only): 815 impressions, 5 clicks,
$123.57, 0 conversions.

### Per campaign, settled MTD

| Campaign | Impr | Clicks | Spend | CTR | CPC | Prim. conv | CVR | CPL | Budget lost IS | Rank lost IS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AC Repair | 319 | 19 | $1,719.33 | 5.96% | **$90.49** | 3.00 | 15.79% | $573.11 | 4.80% | 53.82% |
| HVAC Installation | 2,330 | 79 | $1,987.98 | 3.39% | $25.16 | **0.00** | 0.00% | n/a | **56.86%** | 4.92% |
| HVAC Repair | 666 | 12 | $1,010.98 | 1.80% | **$84.25** | 3.00 | 25.00% | $336.99 | 5.95% | 62.03% |
| HVAC Replacement | 80 | 3 | $101.83 | 3.75% | $33.94 | 0.00 | 0.00% | n/a | 0.00% | 57.63% |
| Gas Boiler Repair | 8 | 0 | $0.00 | 0.00% | $0.00 | 0.00 | 0.00% | n/a | 0.00% | 65.00% |

No legacy campaign spent anything in August. All 18 are paused. Whole-account August
spend equals the five campaigns' spend.

### Pacing against the $13,000 maximum

| | |
|---|---:|
| August to date (settled + partial) | **$4,943.69** |
| Average daily since launch (13 live days) | $370.78 |
| Average daily, last 7 settled days | $540.98 |
| Sum of the five daily budgets | $465.63 |
| Days remaining after today | 4 |
| **Projection, realistic** (last-7 run rate) | **$7,107.63** |
| **Projection, conservative** (2× budget cap every remaining day) | **$8,668.73** |
| Headroom, realistic | $5,892.37 |
| Headroom, conservative | $4,331.27 |

**The account cannot reach the $13,000 ceiling in August under any scenario.** $13,000 is
a maximum, not a target, and no budget increase is recommended. Spending more would not
fix the problem, because the problem is cost per click and click quality, not volume.

---

## 4. Campaign verdicts

| Campaign | Verdict | Basis |
|---|---|---|
| **AC Repair** | **ADJUSTMENT PROPOSED** | 3 Primary conversions on 19 clicks, but $90.49 CPC and $573.11 CPL. Quality Score 4 with below-average expected CTR. Loses 53.82% to rank, only 4.80% to budget, so it is **not** budget-limited. Proposed: uncapped-bidding fix (ADJ-3) plus the `automotive` negative (ADJ-2). **No budget increase**, because rank loss here is a relevance and bid-efficiency problem, not a budget problem. |
| **HVAC Repair** | **ADJUSTMENT PROPOSED** | 3 Primary conversions on 12 clicks at $84.25 CPC. Quality Score 2 with **below-average landing-page experience**. 52.9% of its spend ($534.45) went to Business Profile location and directions clicks that never reach the offer page. Proposed: ADJ-3 bid ceiling and ADJ-4 location-asset exclusion. |
| **HVAC Installation** | **ADJUSTMENT PROPOSED** | Largest spender at $1,987.98 with **zero** Primary conversions on 79 clicks. The cause is identified, not speculative: **$760.28 (38.2%) went to competitor company-name searches**. Its 56.86% budget-lost impression share is real, but buying more of the same traffic would waste more. Proposed: ADJ-1 competitor negatives, ADJ-3 bid ceiling, ADJ-4 location exclusion. **Not rolled back** — the zero-conversion record is explained by traffic composition, and 79 clicks is too thin to condemn the theme. |
| **HVAC Replacement** | **WATCH** | 3 clicks and $101.83 all month. Quality Score 2 with below-average landing-page experience. Too small to act on beyond the account-wide ADJ-3 and ADJ-4. |
| **Gas Boiler Repair** | **HOLD** | 8 impressions, 0 clicks, $0.00 since launch. The approved keyword expansion 3D823A10CB3C0B25 stays blocked because the landing page still names the wrong service (section 8). Holding is correct: widening keywords would send traffic to a page that contradicts the ad. |

### On the HVAC Installation zero-conversion question

40 clicks with 0 conversions was the earlier concern; it is now 79 clicks with 0
conversions. With a true conversion rate of 5% (the account's observed rate), the
probability of seeing zero conversions in 79 clicks is 0.95^79 ≈ **1.7%**. So the
zero is unlikely to be chance alone — but the search-term data explains it without
condemning the service: **38.2% of the spend bought competitor brand searches**, which
convert to directions clicks, not leads. Fix the traffic before judging the theme.

---

## 5. Search terms and negative decisions

### Coverage

| | |
|---|---:|
| Search-term rows pulled (all history) | 807 |
| Distinct (term, campaign) pairs with a verdict | **750** |
| Impressions covered | 2,452 of 4,218 (58.1%) |
| Clicks covered | 76 of 118 (64.4%) |
| Cost covered | $3,783.30 of $4,943.69 (76.5%) |

The gap is Google withholding terms below its privacy threshold. It is unreportable,
not missing from the account. **Coverage is therefore incomplete and is labelled as such.**

### Verdicts

| Verdict | Terms | Clicks | Cost | Primary conv |
|---|---:|---:|---:|---:|
| KEEP | 388 | 39 | $2,851.94 | **6.00** |
| WATCH | 215 | 35 | $883.58 | 0.00 |
| ALREADY BLOCKED | 6 | 2 | $47.78 | 0.00 |
| NEGATIVE CANDIDATE (machine pass) | 10 | 0 | $0.00 | 0.00 |
| INSUFFICIENT EVIDENCE | 131 | 0 | $0.00 | 0.00 |

**Every one of the 6 Primary conversions came from a KEEP term.** Full term-level table:
`clients/ambient-cooling-heating/exports/search-term-verdicts-2026-08-27.csv`.

### The dominant finding: competitor company names in HVAC Installation

`hvac installers` (Phrase) is being expanded by Google's same-meaning matching onto local
contractor **brand** searches.

| | |
|---|---:|
| Competitor company-name terms | 45 |
| Impressions | 191 |
| Clicks | 30 |
| **Cost** | **$782.00** |
| **Primary conversions** | **0.00** |
| Other conversions | 4.00, all Google-hosted "Local actions" (directions / website visits) |

44 of the 45 sit in HVAC Installation ($760.28 = **38.2% of that campaign's spend**).
Examples: `croppmetcalfe columbia`, `fh furr hvac`, `woodfin heating and air`,
`michael and sons hvac`, `blauch brothers harrisonburg va`, `beltway hvac`.

### The ten machine-flagged candidates, after expert review

Only **2 of 10** survive review. The other 8 are rejected on the evidence:

| Term | Machine verdict | **Human decision** | Why |
|---|---|---|---|
| `automotive air conditioning repair near me` | NEGATIVE | **NEGATIVE — accepted** | Vehicle AC, outside all five services |
| `automotive ac mechanic near me` | NEGATIVE | **NEGATIVE — accepted** | Vehicle AC |
| `cheap hvac service near me` | NEGATIVE (in HVAC Repair) | **KEEP everywhere** | Produced **1 Primary conversion** in AC Repair. Protected. |
| `free ac check near me` | NEGATIVE | **KEEP** | Free-estimate seeking is normal HVAC lead behaviour |
| `hvac capacitor replacement near me` | NEGATIVE | **KEEP** | Capacitor replacement is HVAC Repair work |
| `how much to install a blower motor` | NEGATIVE | **KEEP** | Blower motor installation is HVAC Repair work |
| `costco hvac replacement cost` | NEGATIVE | **KEEP** | Retailer price-shopping. `home depot mini split installation cost` **converted**, so this intent is not worthless |
| `lowe's hvac installation cost` | NEGATIVE | **KEEP** | Same |
| `lowes hvac installation` | NEGATIVE | **KEEP** | Same |
| `costco lennox installation cost` | NEGATIVE | **KEEP** | Same |

### Variant leak test (negatives have no close variants)

Each variant reviewed individually against the corpus:

| Variant | Covered by a live negative? | Observed terms | Clicks | Cost |
|---|---|---:|---:|---:|
| `automotive` | **No** | 2 | 0 | $0.00 |
| `auto` | Yes (`auto` BROAD) | 1 | 0 | $0.00 |
| `cars`, `boats`, `vehicle`, `vehicles`, `marine`, `truck`, `trucks`, `van`, `rv`, `motorhome` | No | **0** | 0 | $0.00 |
| `job`, `jobs`, `salary`, `training`, `diy`, `parts`, `manuals`, `retail` | No | **0** | 0 | $0.00 |

**No speculative negative is proposed for any variant with zero observed volume.**
`car` does not block `cars`, and none of those plurals has appeared.

### Re-verification of `car`, `auto`, `boat` on AC Repair 24132507741

| Text | Criterion ID | Match | Status | Active keywords blocked | Converting terms blocked | Observed terms covered |
|---|---|---|---|---:|---:|---|
| `car` | 10008241 | BROAD | ENABLED | **0** | **0** | 5 |
| `auto` | 10000390 | BROAD | ENABLED | **0** | **0** | 1 |
| `boat` | 10019071 | BROAD | ENABLED | **0** | **0** | 1 |

All three verified present exactly once, correct text, correct match type, correct
scope. **Not recreated, not edited, not removed.**

### Existing negative and shared-list conflict audit

All 59 members of account-level list `11252984411` and all 16 enabled shared lists were
tested against the 10 live keywords, 54 in-scope service probes and all 750 corpus pairs.

**Zero live negatives block any active keyword.** But five account-level negatives
suppress in-scope demand:

| Negative | Blocks | Severity |
|---|---|---|
| **`hanover`** | `ac repair hanover md` — **Hanover, Maryland is geo target 1018614, an explicitly targeted city on all five campaigns** | **HIGH** |
| `commercial` | `commercial ac repair`, `commercial boiler repair` | Needs client confirmation |
| `thermostat`, `thermostats` | thermostat diagnosis and installation, which is HVAC Repair work | Medium |
| `ruud`, `rudd`, `ecobee`, `frigidaire`, `ducane` | equipment-brand repair demand | Medium |

**Shared list verdicts — no list may be attached to the five:**

| List | Members | Verdict | Reason |
|---|---:|---|---|
| `11813144900` General List | 1,111 | **DO NOT ATTACH** | Contains `repair` BROAD — would kill 6 of the 10 live keywords. Confirmed still attached only to the paused `AC Install & Replacement`. |
| `12091293463` Ambient - Neg Kwd List | 968 | **DO NOT ATTACH** | Blocks `severn` and `arundel` (the client's own service area), `cheap` and `affordable` (both converted), plus single-letter poison `f` and `h` |
| `12178646912` General List - Irrigation | 1,107 | **DO NOT ATTACH** | Blocks `cost`, `emergency`, `cheap`, `affordable` — all agency-protected |
| `10664304544` Names List | 486 | **DO NOT ATTACH** | Blocks `goodman` and two converting terms |
| `12022987128` GM Competitor Name Tokens | 17 | **DO NOT ATTACH** | `plumbing` BROAD blocks a converting term |
| `12025671131` GM Competitor Brands | 17 | Attachable but **pointless** | Built for a different market; blocks $0.00 of this account's observed waste |
| `12021721179` GM Broad Poison | 5 | **DO NOT ATTACH** | Contains `technicians`, which would block real demand such as "hvac technicians near me" |

**No shared list is proposed for attachment.** The competitor waste needs purpose-built
negatives, which is package ADJ-1.

---

## 6. Other audit findings

### Uncapped Maximize Clicks is the largest efficiency problem

All five campaigns run `TARGET_SPEND` (Maximize Clicks) with
`cpc_bid_ceiling_micros = 0`, i.e. **no maximum CPC at all**.

| Keyword | Match | Clicks | Actual avg CPC |
|---|---|---:|---:|
| `hvac repair near me` | EXACT | 1 | **$153.06** |
| `ac repair near me` | EXACT | 6 | **$130.42** |
| `hvac repair near me` | PHRASE | 11 | $77.99 |
| `ac repair near me` | PHRASE | 13 | $72.06 |
| `hvac replacement near me` | PHRASE | 3 | $33.94 |
| `hvac installers` | PHRASE | 79 | $25.16 |

With Quality Scores of 2–4 and very thin query volume, Maximize Clicks bids to the top of
the range trying to spend the budget. Single days reached $140.82 CPC on AC Repair.
Google returned no first-page or top-of-page CPC estimates for these keywords, so there
is no vendor-supplied floor to calibrate against — hence a deliberately conservative
Stage 1 ceiling in ADJ-3.

### The Business Profile location asset is consuming a fifth of the budget

The customer-level `LOCATION_SYNC` asset set `8620443109` is ENABLED and serves on all
Search campaigns.

| Click type | Clicks | Cost | Share of MTD spend |
|---|---:|---:|---:|
| LOCATION_EXPANSION | 14 | $739.09 | 15.3% |
| GET_DIRECTIONS | 6 | $199.88 | 4.1% |
| **Combined** | **20** | **$938.97** | **19.5%** |

These clicks go to the Business Profile, not to the paid offer page, and produce only
Google-hosted "Local actions", which are excluded from the Conversions column.
**HVAC Repair is worst hit: $534.45 of its $1,010.98, or 52.9%.** Addressed by ADJ-4.

*Note: this overlaps partially with the competitor-term cost above, since one click can be
both. The two figures are reported separately and are not added together.*

### Conversion integrity: a real double count

`WC Lead` (7643656486) reads `primary_for_goal = false` and
`include_in_conversions_metric = false`, yet **contributed 1.0 to `metrics.conversions`**
on the query `hvac companies near me open now`, on which the landing-page form action
also fired.

- Reported Primary conversions: **6.00**
- Duplicated by a second action on the same query: **1.00**
- **Reported Primary conversions are overstated by ~16.7%**

The most likely mechanism is that the customer conversion goals `CONTACT/WEBSITE` and
`CONTACT/CALL_FROM_ADS` are **biddable**, and everything inside a biddable goal counts
regardless of the per-action flags. Those two goals also contain `Call BTN Click` (a raw
button click) and `WC Calls`. The observation is a fact from the API; the mechanism is
the best-supported explanation. Addressed by the separate plan CONV-1.

The known duplicate form action `Visit Thank you page - Submit Form` (6498555481) is
still ENABLED and still secondary, exactly as approved. It contributed 0 conversions.

### Invalid clicks

Google filtered and did not charge for a very large share of clicks:

| Campaign | Charged clicks | Invalid clicks | Invalid rate |
|---|---:|---:|---:|
| AC Repair | 19 | 509 | **96.40%** |
| HVAC Repair | 12 | 422 | **97.24%** |
| HVAC Replacement | 3 | 47 | 94.00% |
| HVAC Installation | 79 | 69 | 46.62% |
| Gas Boiler Repair | 0 | 26 | 100.00% |

This is Google's own filtering, so the money was not spent. It is reported as a traffic-
quality signal, **not as an optimization target**. One related gap: the **2,796 ClickCease
IP exclusions sit on the 18 legacy campaigns and none on the five live ones.** ClickCease
maintains those itself through its own manager link; this is flagged for the client and
the vendor, and no change is proposed here.

### Settings verified clean

Search Partners **off**, Display **off**, AI Max **off**, text asset automation
**OPTED_OUT**, final-URL expansion **OPTED_OUT**, no DSA, Presence-only location
targeting, 75 targets and 0 exclusions per campaign, 6 ad-schedule rows per campaign with
no Sunday row. Auto-tagging on. Account tracking template is the authorized ClickCease
redirect. 100% of delivery was `LOCATION_OF_PRESENCE`.

### Schedule compliance

| Window | Result |
|---|---|
| 2026-08-14 → 2026-08-20 (before Package C) | 53 out-of-schedule rows, 207 impressions, 7 clicks, **$587.95** |
| **2026-08-21 → 2026-08-26 (settled, governed by Package C)** | **PASS — zero impressions outside Mon–Fri 08:00–20:00 / Sat 08:00–13:00** |
| 2026-08-27 (partial) | PASS |

The protective schedule works. The earlier leakage predates it and is not a live defect.

### A counting artifact, not account drift

Ad group `202339087874` "SKAG | HVAC Replacement Near Me" sits inside the **AC Repair**
campaign with status **REMOVED**. Its 2 keywords and 2 ads still report ENABLED, so a
query that does not exclude removed parents shows 12 keywords instead of the true **10**
and makes AC Repair look cross-contaminated. It cannot serve. Likewise, the 2,796
ClickCease IP exclusions live on `campaign_criterion`, not `customer_negative_criterion`;
reading the wrong resource returns 0 and looks like a loss. Both are **query-definition
differences, not drift.**

---

## 7. Exact mutations executed this run

**NONE.** This run made no external change of any kind. No campaign, ad group, keyword,
ad, asset, budget, bid, conversion action, schedule, location, shared list, tracking item
or manager link was created, edited, paused, enabled or removed.

### Previously completed work — verified intact, not replayed

| Work | Fingerprint | Verified today |
|---|---|---|
| HVAC Installation budget $138.16 → $176.15 | BFB9FD367F639CA4 | Budget 15787409441 = **176,150,000 micros**. Not re-run. |
| Automotive negatives car / auto / boat | EACEC7CBAE85FF2B | Criterion IDs **10008241, 10000390, 10019071**, all ENABLED BROAD negatives on 24132507741. Not recreated. |
| HVAC Repair RSA swap | D441DEFC58EB5643 | 821714108336 and 821714108339 ENABLED/APPROVED; 820900825560 and 820900825563 PAUSED. |
| Conversion configuration (Plan B) | 03F125C189679E35 | Duplicate form action 6498555481 still ENABLED and secondary. |
| Delivery schedule | C6C3DFFC9BD5AF9B | 6 rows per campaign, zero Sunday delivery, compliance verified. |
| ClickCease 2,796 IP exclusions, both manager links, GTM, WhatConverts, tracking template, call asset | — | All present and unchanged. |

---

## 8. Plans awaiting approval

### Plan 1 — consolidated adjustment · `ACE80A09AC134C85`

30 operations, all reversible, nothing removed. **Validate-only: VALIDATE_OK on both batches.**

| Package | Change | Objects | Evidence |
|---|---|---:|---|
| **ADJ-1** | 24 PHRASE competitor negatives on HVAC Installation 24132507747 | 24 | 44 terms, 189 impressions, 29 clicks, **$760.28**, 0 Primary conversions |
| **ADJ-2** | `automotive` BROAD negative on AC Repair 24132507741 | 1 | 2 terms leaked past `auto`; $0.00 so far. **Protection, not a measured saving** |
| **ADJ-3** | Stage 1 max CPC: AC Repair $60, HVAC Repair $60, HVAC Installation $40, HVAC Replacement $40, Gas Boiler $40 (all currently uncapped) | 5 | $153.06 and $130.42 observed CPCs; ceilings set **above** each campaign's observed mean so only the tail is cut |
| **ADJ-4** | Exclude the inherited `LOCATION_SYNC` asset set on all five | 5 | $938.97 of location and directions clicks, 0 Primary conversions |

Conflict test on all 25 proposed negatives: **0 live keywords blocked, 0 service probes
blocked, 0 Primary-converting terms blocked, 0 duplicates of an existing negative.**

Two proposed negatives (`furr`, `hvac precision services`) each cover a term carrying one
Google-hosted "Local actions — Directions" conversion and **zero** Primary conversions and
zero lead actions. Flagged explicitly so the owner sees the judgment call.

```
APPROVE CONSOLIDATED AMBIENT PLAN ACE80A09AC134C85 FOR 2401959466
```

### Plan 2 — conversion-goal integrity · `EE6CFAD6667A95A1` *(separate approval class)*

Set `biddable = false` on the `CONTACT/WEBSITE` and `CONTACT/CALL_FROM_ADS` campaign
conversion goals across the five campaigns. 10 operations. **VALIDATE_OK.**
Keeps `SUBMIT_LEAD_FORM/WEBSITE`, `PHONE_CALL_LEAD/WEBSITE` and
`PHONE_CALL_LEAD/CALL_FROM_ADS` biddable. No conversion action is removed, paused or
edited. Reported Conversions will step **down** — that is the correction.

```
APPROVE CONVERSION GOAL PLAN EE6CFAD6667A95A1 FOR 2401959466
```

### Plan 3 — account-level negative removals · `C3038EDD9E621944` *(DESTRUCTIVE)*

Remove 8 members from account-level list `11252984411`: `hanover`, `thermostat`,
`thermostats`, `ruud`, `rudd`, `ecobee`, `frigidaire`, `ducane`. 8 operations. **VALIDATE_OK.**
Measured loss to date is **$0.00** — these suppress demand before it can be measured, so
the case is recovered qualified demand, not recovered cost. The strongest item is
`hanover`, which blocks an explicitly targeted city.

**`commercial` is deliberately NOT proposed for removal.** Removing it is only correct if
Ambient actually serves commercial customers, and that is an unverified business fact.

```
APPROVE DESTRUCTIVE NEGATIVE REMOVAL PLAN C3038EDD9E621944 FOR 2401959466
```

---

## 9. Landing pages and tracking

Every active final URL rendered in real JavaScript-enabled Chromium, desktop (1440×900)
and mobile (390×844), with and without click parameters — 20 renders total. GET only:
**no form was submitted and no tel: link was activated.**

| Check | AC Repair | HVAC Repair | HVAC Install | HVAC Replace | Gas Boiler |
|---|---|---|---|---|---|
| HTTP / render | 200 ✅ | 200 ✅ | 200 ✅ | 200 ✅ | 200 ✅ |
| Service-specific H1 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Step heading names the right service** | ✅ | ✅ | ✅ | ✅ | ❌ **shows "Your HVAC Replacement in 3 Simple Steps"** |
| Paid number (410) 705-6354 displayed | ✅ | ✅ | ✅ | ✅ | ✅ |
| Main-site number (410) 761-0932 exposed | ✅ none | ✅ none | ✅ none | ✅ none | ✅ none |
| Unexplained (410) 415-9517 exposed | ✅ none | ✅ none | ✅ none | ✅ none | ✅ none |
| GTM-PQTPQ436 | ✅ | ✅ | ✅ | ✅ | ✅ |
| AW-11155434808 / G-9X9ZHNCRWF | ✅ | ✅ | ✅ | ✅ | ✅ |
| WhatConverts active | ✅ | ✅ | ✅ | ✅ | ✅ |
| Barred claims | ✅ none | ✅ none | ✅ none | ✅ none | ✅ none |
| Mobile horizontal overflow | ✅ none | ✅ none | ✅ none | ✅ none | ✅ none |
| Privacy / terms link | ❌ absent | ❌ absent | ❌ absent | ❌ absent | ❌ absent |
| Duplicate DOM IDs | ❌ 25+ | ❌ 25+ | ❌ 25+ | ❌ 25+ | ❌ 25+ |

**Phone architecture is correct.** The only displayed number is (410) 705-6354. A
`tel:+14109141456` href is present, which is the documented, intentional WhatConverts DNI
pool number. **(410) 761-0932 did not reproduce on any of the 20 renders.** That is
recorded as *not reproduced*, not as *fixed* — and **no change is proposed to WhatConverts
profile 105803**, exactly as instructed. A transient display race is not authority to
alter routing.

**Click-ID capture — partial finding.** A test GCLID reached browser storage on every page
(so WhatConverts can attribute), but **was not written into any hidden form field at render
time**. Whether Gravity Forms populates it at submit time cannot be determined without
submitting a real lead, which was not done. Reported as unverified, not as broken.

**ClickCease script not detected on the landing pages.** ClickCease operates here through
the account-level tracking-template redirect and IP exclusions, so this is an observation
to confirm with the vendor, not a defect.

### Gas Boiler gate

Expected `Your Gas Boiler Repair in 3 Simple Steps`; observed
`Your HVAC Replacement in 3 Simple Steps` as at 2026-08-27, desktop and mobile.
**Keyword package `3D823A10CB3C0B25` remains BLOCKED. Do not execute.** When the page is
corrected, rebuild the package from current state rather than trusting the old fingerprint.

Landing-page deployment package `93A9DF4AA19675E8` remains **BLOCKED** — no website
source, staging, backup or deployment authority exists in this environment.

---

## 10. Monitoring checkpoints and rollback

| Checkpoint | Due | Status | Result |
|---|---|---|---|
| 24 hours after the 2026-08-22 changes | 2026-08-23 | **COMPLETE** (late — first run since) | **PASS.** 0 active keywords blocked, 0 converting terms blocked, all 3 criteria present exactly once. AC Repair impressions **rose** 108 → 143 across equal windows. |
| 72 hours — new vehicle/marine phrasings | 2026-08-25 | **COMPLETE** (late) | **PASS.** Only `automotive` leaked: 2 terms, 3 impressions, 0 clicks, $0.00. `truck`, `van`, `rv`, `motorhome`, `cars`, `boats`, `vehicle`, `marine` produced **zero** terms. |
| 7 settled days | 2026-08-29 | **NOT DUE — not marked complete** | Only 4 of 7 settled days available. Interim only. |

### Rollback triggers — all evaluated against settled data

| Trigger | Threshold | Observed | Met? |
|---|---|---|---|
| Budget: CPC > $41.27 without more clicks | $41.27 | **$21.93** after (from $27.51 before) | **No** |
| Budget: single-day spend > $352.30 | $352.30 | **$312.85** max settled day | **No** |
| Budget: cumulative August > $11,500 before 08-29 | $11,500 | **$4,943.69** | **No** |
| Negatives: a legitimate AC Repair query blocked | any | **0** | **No** |

**Decision: NO ROLLBACK.** No trigger is met and no rollback is executed.

### Before / after, equal 4-day settled windows

| Campaign | Clicks b/a | Spend b/a | CPC b/a | Prim. conv b/a | Sample |
|---|---|---|---|---|---|
| AC Repair | 9 / 6 | $947.48 / $653.57 | $105.28 / $108.93 | 1.0 / 1.0 | too small |
| HVAC Installation | 40 / 35 | $1,100.44 / $767.63 | $27.51 / $21.93 | 0.0 / 0.0 | **adequate** |
| HVAC Repair | 5 / 5 | $563.82 / $405.10 | $112.76 / $81.02 | 2.0 / 1.0 | too small |
| HVAC Replacement | 2 / 1 | $52.14 / $49.69 | $26.07 / $49.69 | 0.0 / 0.0 | too small |
| Gas Boiler Repair | 0 / 0 | $0.00 / $0.00 | — | 0.0 / 0.0 | too small |

HVAC Installation is the **only** campaign clearing 30 clicks in both windows. Its CPC fell
from $27.51 to $21.93 after the budget increase while clicks held (40 → 35) — consistent
with the budget change working as intended, though still short of the 7-day checkpoint.
For every other campaign the click counts are single digits and **no improvement or
regression is claimed.**

---

## 11. Local record corrections

Both files revalidated after editing: `validate_work_order.py` PASS, `verify_setup.py --online` PASS.

| File | Field | Before | After |
|---|---|---|---|
| `work-order.yaml` | `task.request` | described the 2026-08-18 pass only | appended the 2026-08-27 audit scope and the three new fingerprints |
| `work-order.yaml` | `task.date_range` | `2026-08-14 through 2026-08-18` | the eight windows used today, with the settled/partial split stated |
| `work-order.yaml` | `inputs.verified_2026_08_27` | absent | new block: campaign and budget IDs, uncapped bid ceilings, network and automation settings, negative inventory, IP-exclusion location, Business Profile asset set, last change event, and all landing-page facts |
| `client.yaml` | `optimization_score` | `0.9678744` | `0.7843765`, labelled observed-only and explicitly **not** an objective |

`task.mode` stays `draft` — the schema permits only `read`, `draft`, `create-paused` or
`enable`, and this pass produced drafts.

Business call coverage (`published_business_hours`, Mon–Fri 08:00–16:00), the paid
delivery schedule (`expected_ad_schedule`, Mon–Fri 08:00–20:00 + Sat 08:00–13:00) and the
call-asset schedule are kept as **separate fields and were not collapsed.**

**Fingerprint manifest rebuilt** from the plan files on disk: 50 files. The 2026-08-22b
manifest omitted `DEVELOPER-HANDOFF-ADDENDUM-C-2026-08-22.json`; the ledger now agrees
with the directory. All 14 prior VOID fingerprints remain do-not-execute.

---

## 12. Durable artifacts

| Artifact | Path |
|---|---|
| Full structural snapshot | `clients/ambient-cooling-heating/snapshots/snapshot-structure-2026-08-27.json` |
| Performance extract, all windows | `clients/ambient-cooling-heating/snapshots/performance-2026-08-27.json` |
| Diagnostics: schedule, invalid clicks, bids, change history | `clients/ambient-cooling-heating/snapshots/diagnostics-2026-08-27.json` |
| Search-term corpus + verdicts | `clients/ambient-cooling-heating/snapshots/search-terms-2026-08-27.json` |
| **Complete term-level verdict table (CSV)** | `clients/ambient-cooling-heating/exports/search-term-verdicts-2026-08-27.csv` |
| Negative inventory and conflict audit | `clients/ambient-cooling-heating/snapshots/negative-conflict-audit-2026-08-27.json` |
| Shared-list conflict audit | `clients/ambient-cooling-heating/snapshots/shared-list-conflict-audit-2026-08-27.json` |
| Landing-page browser evidence | `clients/ambient-cooling-heating/snapshots/lp-browser-qa-2026-08-27.json` |
| Consolidated plan `ACE80A09AC134C85` | `clients/ambient-cooling-heating/plans/AMBIENT-CONSOLIDATED-2026-08-27.json` |
| Conversion-goal plan `EE6CFAD6667A95A1` | `clients/ambient-cooling-heating/plans/AMBIENT-CONV-1-2026-08-27.json` |
| Destructive removal plan `C3038EDD9E621944` | `clients/ambient-cooling-heating/plans/AMBIENT-DEL-1-2026-08-27.json` |
| Validate-only receipt (consolidated) | `clients/ambient-cooling-heating/receipts/validate-only-2026-08-27.json` |
| Validate-only receipt (separate plans) | `clients/ambient-cooling-heating/receipts/validate-only-separate-plans-2026-08-27.json` |
| Local record diff | `clients/ambient-cooling-heating/receipts/local-record-diff-2026-08-27.json` |
| Rebuilt fingerprint manifest | `clients/ambient-cooling-heating/receipts/fingerprint-manifest-2026-08-27.json` |
| MTD extract, comparison, checkpoints | `reports/ambient-cooling-heating/2026-08-27-mtd-extract-and-comparison.json` |
| **This report** | `reports/ambient-cooling-heating/2026-08-27-august-audit.md` |

No artifact contains a secret, a token, or any lead PII. Lead data is reported only as
aggregate counts.

---

## 13. Next action required

1. **Approve or decline** `APPROVE CONSOLIDATED AMBIENT PLAN ACE80A09AC134C85 FOR 2401959466`.
2. **Approve or decline** `APPROVE CONVERSION GOAL PLAN EE6CFAD6667A95A1 FOR 2401959466`.
3. **Approve or decline** `APPROVE DESTRUCTIVE NEGATIVE REMOVAL PLAN C3038EDD9E621944 FOR 2401959466`.

### Three questions that materially change the work

| # | Question | Recommended answer | Effect if unanswered |
|---|---|---|---|
| 1 | Does Ambient serve **commercial** HVAC customers? | If yes, add `commercial` to the DEL-1 removals | `commercial` stays blocked and commercial demand stays suppressed |
| 2 | Is a **WhatConverts API token** available for this account? | Yes — provide it | Lead quality, CPQL, CAC and profit-after-ad-spend stay uncalculable, and CPL remains the deepest metric |
| 3 | Should ClickCease be asked to extend its **IP exclusions to the five live campaigns**? | Yes — raise with the vendor | The five campaigns keep running without the IP protection every legacy campaign has |

Question 2 is the one that most limits this account: at a $803.35 CPL with no lead-quality
data, we cannot yet tell an expensive good lead from a cheap bad one.

---

# EXECUTION ADDENDUM — 2026-08-28

**Status: three approved fingerprints EXECUTED. Nine operations. All readbacks PASS.**

Section 7 above ("Exact mutations executed this run — NONE") described the 2026-08-27 audit
pass and remains accurate for that date. This addendum records what was executed on
2026-08-28 after owner approval and the corrected decision package.

## Preflight

30 checks, all PASS (`receipts/preflight-approved-2026-08-28.json`). Identity gate exact,
non-manager, non-test, both manager links ACTIVE, no account change since 2026-08-22
09:36:07, all three fingerprints reproduced from their plan files, none of the eight new
negatives already existed at the approved scope, criterion 11143481 confirmed as
`hanover` / BROAD / list 11252984411, Hanover geo 1018614 confirmed positively targeted on
all five campaigns, and validate-only VALIDATE_OK on all nine operations.

Conflict testing before writing — **zero conflicts on every axis**:

| Axis tested | Count | Conflicts |
|---|---:|---:|
| Active Phrase and Exact keywords | 10 | **0** |
| Five-service demand probes | 53 | **0** |
| Historical converting search terms | 13 | **0** |
| Service-area location queries | 20 | **0** |
| HVAC manufacturer / equipment queries | 25 | **0** |

## Execution 1 — competitor negatives · `82ACD4953536C020` · campaign 24132507747

One atomic mutation, `partial_failure=false`, 7 operations, 7 results.

| Negative | Match | Criterion ID | Status |
|---|---|---|---|
| `armbridge` | PHRASE | 2489735546094 | ENABLED, negative |
| `blauch` | PHRASE | 801509855 | ENABLED, negative |
| `bluedot` | PHRASE | 149260703 | ENABLED, negative |
| `croppmetcalfe` | PHRASE | 299839338603 | ENABLED, negative |
| `hugee` | PHRASE | 304510676052 | ENABLED, negative |
| `michael & sons` | PHRASE | 302549263138 | ENABLED, negative |
| `michael and sons` | PHRASE | 2437152438 | ENABLED, negative |

Readback: exactly 7 on the campaign, all PHRASE, all negative, all ENABLED. No spelling
variants, company-name expansions, extra competitors, equipment brands, locations or
generic service words were added.

## Execution 2 — vehicle protection · `6F2B6ABBCEB992E4` · campaign 24132507741

One atomic mutation, `partial_failure=false`, 1 operation, 1 result.
`automotive` BROAD, criterion **10008471**, ENABLED, negative.

**Classified as proactive traffic protection, not a measured saving. Observed cost $0.00.**

Readback: AC Repair now holds exactly 4 campaign negatives — `auto` (10000390),
`boat` (10019071), `car` (10008241) all preserved with their original criterion IDs, plus
`automotive` (10008471).

## Execution 3 — Hanover removal · `E50EDFE7644A9B5F` · DESTRUCTIVE

One atomic mutation, `partial_failure=false`, 1 operation, 1 result.
Removed `customers/2401959466/sharedCriteria/11252984411~11143481`.

| Check | Result |
|---|---|
| Criterion 11143481 exists | **No — removed** |
| Account-level list members | 59 → **58** |
| Members removed | exactly `['11143481']` |
| Members added | none |
| Members changed | none |
| `thermostat`, `thermostats`, `ruud`, `rudd`, `ecobee`, `frigidaire`, `ducane` | **all still present** |
| Hanover geo 1018614 targeted | **all five campaigns** |
| Shared lists attached to the five | **0** |

## Final readback — all PASS

Exactly 8 resources created, exactly 1 removed, **9 approved operations**. Campaign
negatives went 3 → 11; the other three campaigns still hold zero. All 10 positive keywords
remain ENABLED and ELIGIBLE.

Unchanged against the preflight baseline: 23 campaigns · 5 ad groups · 20 ads ·
10 keywords · all five budgets · CPC ceilings still `[0]` · `excluded_parent_asset_set_types`
still empty · 2,796 ClickCease IP exclusions · 30 ad-schedule rows · 375 location criteria ·
16 conversion actions · WC Lead `include_in_conversions_metric` still false ·
40 sitelink associations · 0 shared lists on the five · LOCATION_SYNC asset set 8620443109
still ENABLED · both manager links ACTIVE.

`change_event` returned 0 rows for 2026-08-28 at readback time. It lags by hours and is not
used as proof — the resource readbacks are the authoritative evidence.

## Still VOID and HELD

| Plan | Fingerprint | State |
|---|---|---|
| Consolidated (bundled) | `ACE80A09AC134C85` | **VOID** |
| CPC ceilings (package B) | — | **VOID** — would have blocked 100% of converting traffic |
| Location asset (package C) | — | **VOID** — carried 2 of 6 Primary conversions |
| Conversion goals | `EE6CFAD6667A95A1` | **VOID** — historical artifact, not an active defect |
| Original destructive | `C3038EDD9E621944` | **VOID** — split |
| Equipment-brand removals (D-2) | `4D7AF1C9CFCA27F9` | **HOLD** — zero observed evidence |
| Gas Boiler keywords | `3D823A10CB3C0B25` | **BLOCKED** — landing-page heading still wrong |
| Landing-page deployment | `93A9DF4AA19675E8` | **BLOCKED** — no deploy authority |

## Addendum artifacts

| Artifact | Path |
|---|---|
| Preflight receipt | `clients/ambient-cooling-heating/receipts/preflight-approved-2026-08-28.json` |
| Execution receipt | `clients/ambient-cooling-heating/receipts/execution-receipt-2026-08-28.json` |
| Final readback | `clients/ambient-cooling-heating/receipts/final-readback-2026-08-28.json` |
| Rebuilt manifest | `clients/ambient-cooling-heating/receipts/fingerprint-manifest-2026-08-28.json` |
| Corrected decision package | `reports/ambient-cooling-heating/2026-08-28-corrected-decision-package.md` |
