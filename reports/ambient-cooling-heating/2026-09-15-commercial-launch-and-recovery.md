# Ambient Cooling - Live | 2401959466 | Commercial HVAC Installation

**Session 2026-09-15.** Read-only analysis, browser QA, validation and two fingerprinted
create-paused plans. **No external write was made.** One `validate_only=True` dry run was
issued (2 operations, nothing committed).

---

## 0. Identity and work-order gate — PASS

`Ambient Cooling - Live | 2401959466 | Commercial HVAC Installation`

Fresh read-only lookup, 2026-09-15 09:35 America/New_York. **10/10 checks PASS.**

| Check | Observed |
|---|---|
| `customer.descriptive_name` | `Ambient Cooling - Live` — exact match |
| `customer.id` | `2401959466` — exact match, child not manager |
| manager account / test account | false / false |
| status / currency / time zone | ENABLED / USD / America/New_York |
| `- live` marker | present |
| Manager `3373711342` Green Marketing | ACTIVE |
| Manager `2815082755` ClickCease | ACTIVE — protected, untouched |
| conversion tracking | id `11155434808`, owner `customers/2401959466` |

Work orders validated with `scripts/validate_work_order.py`:

```
Work order: PASS | Ambient Cooling - Live | 2401959466 | heating-cooling | Commercial HVAC Installation
Work order: PASS | Ambient Cooling - Live | 2401959466 | heating-cooling | AC Repair
```

Two local repository edits were required and made:

1. **`clients/ambient-cooling-heating/work-order-commercial-hvac-installation.yaml`** — new, because
   agency policy allows one exact primary service per work order and the existing one is AC Repair.
2. **`client.yaml` → `client.offer.services_in_scope`** — added `Commercial HVAC Installation`.
   This records a client fact the approval owner confirmed **in writing on 2026-09-10**
   (`work-order.yaml: commercial_hvac_in_paid_scope: true`); the service list had simply not been
   updated. Not a new authorization.

---

## 1. LIVE-STATE DRIFT — the ad group was enabled outside the approval workflow

**VERIFIED FACT.** Ad group `199748801029` `SKAG | Commercial HVAC Installation` reads **ENABLED**.
The last session created it PAUSED and asserted PAUSED as recently as 2026-09-10 17:21.

```
change_event  2026-09-15 08:42:16.970687
  resource          customers/2401959466/adGroups/199748801029
  operation         UPDATE      changed_fields ['status']
  old_resource      status = PAUSED
  new_resource      status = ENABLED
  user              access@greenmarketingfl.com
  client_type       GOOGLE_ADS_WEB_CLIENT       <- the Google Ads web UI, by hand
```

Creation is corroborated: `change_event` AD_GROUP **CREATE** 2026-09-10 13:52:29,
`new_resource.status = PAUSED`.

**This is safe right now, and it is not safe later.** The ad group holds **0 ads**, so it cannot
serve — 0 impressions, 0 clicks, $0.00 all-time, confirmed. But because the parent is now ENABLED,
**an ad created ENABLED would begin serving instantly with no second approval gate.** Both RSAs in
the plan below are therefore created PAUSED, and readback asserts PAUSED.

I have not reverted it. That is the owner's own action on their own account, and reverting it
would itself be an unapproved external write. If you want it back to PAUSED until launch, say so
and I will produce a one-operation plan.

> **Method note worth keeping.** `change_event.change_date_time <= '2026-09-15'` silently excludes
> all of 2026-09-15 — a bare date compares as midnight. My first sweep therefore reported "no
> changes since 2026-09-10" and missed this. `change_status` caught it (`AD_GROUP CHANGED
> 2026-09-15 08:52:20`), and re-querying with `<= '2026-09-15 23:59:59'` produced the row above.
> Always bound `change_event` with an explicit time, not a bare date.

---

## 2. Fresh before-state snapshot — the five campaigns

| Campaign | ID | Status | Daily budget | CPC ceiling | Bidding | SP | Display | Geo |
|---|---|---|---:|---:|---|---|---|---|
| AC Repair | 24132507741 | ENABLED / SERVING | $141.45 | $25.00 | TARGET_SPEND | off | off | PRESENCE |
| HVAC Repair | 24132507750 | ENABLED / SERVING | $78.95 | $25.00 | TARGET_SPEND | off | off | PRESENCE |
| HVAC Installation | 24132507747 | ENABLED / SERVING | $176.15 | $30.00 | TARGET_SPEND | off | off | PRESENCE |
| HVAC Replacement | 24132507753 | ENABLED / SERVING | $20.00 | $30.00 | TARGET_SPEND | off | off | PRESENCE |
| Gas Boiler Repair | 24132507744 | ENABLED / SERVING | $5.00 | $25.00 | TARGET_SPEND | off | off | PRESENCE |

**Combined daily $421.55 × 30.4 = $12,815.12. Headroom to the $13,000 maximum: $184.88.**
Every anchor in the master instruction matches live state exactly.

Preserved and verified: Search Partners off, Display off, AI Max off, asset automation opted out,
Final URL expansion opted out, Presence targeting, 75 geo targets / 0 exclusions per campaign,
schedule Mon–Fri 08:00–20:00 + Sat 08:00–13:00 (6 rows, no Sunday), ClickCease manager link ACTIVE.

Ad groups: 7 total (6 ENABLED + `202339087874` REMOVED, correctly treated as removed).

---

## 3. Commercial ad group — complete live inventory

| Item | Live state |
|---|---|
| Ad group | `199748801029` `SKAG | Commercial HVAC Installation`, **ENABLED**, cpc_bid 10000 µ |
| Campaign | `24132507747`, ENABLED, SERVING |
| Keyword PHRASE | `296582962269` `"commercial hvac installation"` — ENABLED, APPROVED, **ELIGIBLE** |
| Keyword EXACT | `4165114052` `[commercial hvac installation]` — ENABLED, APPROVED, **ELIGIBLE** |
| Quality Score | none yet on either keyword — 0 impressions. Expected, not a defect |
| Broad positives | 0 |
| Ad-group negatives | **17/17 exact match**, all BROAD, all ENABLED |
| **Ads** | **0** ← the only thing blocking the serving chain |
| Ad-group asset links | 0 (inherits campaign assets) |
| Final URL | inherited from ad level; no ad-group or keyword URL override |
| Tracking template / suffix | none at ad-group or keyword level |

### The 17 negatives — `AMB-0910-COMM-NEG-3 / 51CF5986F18A` is **ALREADY_EXECUTED**

```
career  careers  course  courses  diy  homeowner  house  job  jobs
parts   residential  salaries  salary  supplier  supply  used  wholesale
```

Exact set match, zero extras, zero missing, all BROAD, all ENABLED, ad-group scope only.
All five intentionally held terms confirmed **absent**: `school` `schools` `rent` `rental`
`training`. **Zero negative changes made or proposed.** `commercial` confirmed absent from
campaign level and from account-level list `11252984411`.

**No shared negative set is attached to any of the five campaigns** — 88 `campaign_shared_set`
attachments exist across the account, none of them to `24132507741/44/47/50/53`. Every
shared-list match on these campaigns is inert.

### Serving chain

| Link | State |
|---|---|
| Campaign | ENABLED / SERVING ✅ |
| Ad group | ENABLED ✅ |
| Keywords | 2 ENABLED, APPROVED, ELIGIBLE ✅ |
| **Ads** | **0 — BLOCKS DELIVERY** ❌ |
| Destination | HTTP 200 ✅ |
| Budget / schedule / location / billing | all eligible ✅ |

---

## 4. Commercial landing page — desktop + mobile, real browser

`https://offer.ambientcoolingandheating.com/commercial-hvac-installation/`
Rendered in JavaScript-enabled Chromium at 1440×900 and 390×844, with and without paid
parameters. GET only — no form submitted, no `tel:` activated.

### What passes

| Check | Result |
|---|---|
| HTTP status / redirects / HTTPS | **200**, zero redirects, HTTPS ✅ |
| Destination matches requested URL, no soft 404 | ✅ |
| H1 | `Commercial HVAC Installation in Central Maryland` — matches intended ✅ |
| Title | `Commercial HVAC Installation in Central Maryland | Ambient Cooling & Heating` — drifts from the intended shorter title, but the geo addition is an improvement. Not a defect |
| Content scope | **100% commercial**. All 12 commercial terms present (rooftop, packaged, heat pump, central air, ductwork, ventilation, controls, Central Maryland…). **Zero residential leak** ✅ |
| Barred claims | **zero**. No 24/7, emergency, same-day, guarantee, warranty, financing, rebate, rating, price, `#1`, Licensed & Insured, or LSA reference ✅ |
| Privacy + Terms | **both present** on all six paid pages — this closes a defect open since 2026-08-17 ✅ |
| Approved paid number displayed | `(410) 705-6354` ✅ |
| Forwarding number `410-761-0932` | **absent** from rendered text and HTML source ✅ |
| Mobile sticky call bar | present, carries `tel:4107056354` — correct number ✅ |
| Trackers | GTM `GTM-PQTPQ436`, Google Ads `AW-11155434808`, GA4 `G-9X9ZHNCRWF`, WhatConverts (cookie `wc_visitor=105803-…`) all firing ✅ |
| Broken images / horizontal overflow | none ✅ |
| Page load | 2.96 s to networkidle ✅ |
| `noindex, nofollow` | correct and intended for a paid-only offer subdomain ✅ |
| DNI stability | 3 consecutive renders — displayed number never changed ✅ |

### 🔴 P0 — attribution is broken by proxy caching (PROVEN, affects all six pages)

The Gravity Forms attribution fields are populated **server-side** and the page is then cached by
a proxy. The cached HTML — including one visitor's click IDs — is served to everyone else.

```
response headers:  x-cache-enabled: True     x-proxy-cache: HIT

raw server HTML for /hvac-installation/, requested with gclid=ZZZFRESH999&utm_campaign=zzz-camp:
  input_9  value='google'
  input_10 value='cpc'
  input_11 value='qa-readonly'                    <- NOT zzz-camp
  input_12 value='commercial hvac installation'   <- NOT zzz-term
  input_13 value='qa-readonly-content'            <- NOT zzz-content
  input_14 value='QA0915COMMTEST'                 <- NOT ZZZFRESH999
```

The served values are the **query string from an earlier, different visit**, baked into the cache
entry and replayed to every later visitor regardless of their own URL.

Measured across 24 fresh-context loads (6 pages × 4 runs, 9-second settle):
**0/24 loads captured the visitor's own GCLID. 0%.**

- `/hvac-repair/`, `/hvac-installation/`, `/hvac-replacement/` — served a **stale** GCLID.
- `/commercial-hvac-installation/`, `/ac-repair/`, `/gas-boiler-repair/` — served **empty** fields,
  so a commercial form lead carries **no** click ID at all.

**Consequences.** Form leads are credited to the wrong click, wrong campaign and wrong keyword, or
to nothing. This is the root cause of the account's long-standing measurement unreliability, and it
means **no keyword-level or campaign-level conversion attribution from form leads is trustworthy**
— including the four September conversions in §6.

**Disclosure:** the currently-cached marker `QA0915COMMTEST` came from **my QA run this morning**.
It is a synthetic GCLID Google will not match, so it cannot mis-credit a real click — but until the
cache is purged, real form leads from those three pages will carry it and fail to attribute. A
cache purge is the first item in the defect table.

**The fix is architectural**, not a value change: populate these fields with client-side JavaScript
from `location.search` (or a first-party cookie) **after** load, or exclude these pages from proxy
cache. Server-side population and full-page caching are fundamentally incompatible.

### 🔴 P0 — developer instruction text published as customer-facing copy

Live, under the `Commercial HVAC Installation Gallery` heading:

> "These images illustrate commercial HVAC equipment and installation settings. **Use them for the
> page layout without presenting them as completed Ambient projects.**"

That second sentence is an internal note to the developer, published verbatim. The gallery also
contains **zero images**. An empty gallery captioned with a build instruction.

### 🔴 P0 — countdown timer advertising an offer that does not exist

Live: **`Offer Ends in  15 DAY  10 HRS  15 MIN  06 SEC`**

There is no offer anywhere on the page. No discount, no price, no promotion. `client.yaml` bars
`discount_or_dollar_offer` and records the only verified offer as *"Free [service] quote. No price,
discount, or dollar value is published."* A countdown on a non-existent offer is an unverified
promotional claim and a Google Ads misrepresentation risk on a page our ads point to.

### 🟠 P1 — three copies of `gform_1`, 34 duplicate DOM IDs

All six pages render the form three times (2 visible + 1 zero-height), every copy with
`id="gform_1"` and duplicate field IDs (`input_1_1`, `input_1_4`, …). Invalid HTML; breaks
`label[for]` association (accessibility); and creates duplicate-conversion risk if the GTM trigger
or submit handler binds per-form.

*Honeypot note:* `input_16` is the Gravity Forms honeypot — its label rotates per render
(`LinkedIn` / `X/Twitter` / `Comments`). **Do not populate it.** This corrects an earlier note in
our own memory that identified `input_9` as the honeypot; `input_9` is an attribution field.

### 🟠 P1 — testimonials tripled, with a typo

The same three testimonials (Rick G., Sebastian S., Kenneth T.) render **three times** = 9 blocks.
One carries a doubled opening quote: `““Quality work at reasonable rates.”` — repeated 3×.

### 🟡 P2 — telephone link hygiene (all six pages)

| `tel:` href | Link text | Verdict |
|---|---|---|
| `tel:4107056354` | `CALL: (410) 705-6354` | right number, **not E.164** (no `+1`) |
| `tel:(410) 705-6354` | `Call Now: (410) 705-6354` | right number, **malformed href** — unencoded parentheses and space |
| `tel:+14109141456` | `Call Now` | **wrong number** — the mixed-source tracking number. Currently `visible: false`, so not user-clickable, but it is in the DOM on every page |

### 🟡 P2 — meta description is the title text

Observed: `Commercial HVAC Installation in Central Maryland | Ambient Cooling & Heating`
Intended: `Request commercial HVAC installation or replacement for your Central Maryland property…`
Low impact on a `noindex` page. No `canonical` tag (minor).

### Developer defect table

| # | Issue | Page(s) | Evidence | Severity | Exact correction | Owner | Retest | Launch blocker |
|---|---|---|---|---|---|---|---|---|
| 1 | Proxy cache serves one visitor's click IDs to all visitors | all 6 | `x-proxy-cache: HIT`; raw HTML `input_14='QA0915COMMTEST'` under a different `gclid` | **P0** | Purge SiteGround Dynamic Cache now; then populate `input_9`–`input_15` client-side from `location.search` after load, or exclude these URLs from proxy cache | Web dev | Re-run `ambient_0915_gclid_probe.py`; require 24/24 | **YES** |
| 2 | Developer instruction text published as body copy | commercial | "Use them for the page layout without presenting them as completed Ambient projects." | **P0** | Delete the sentence; either populate the gallery with approved images or remove the whole section | Web dev | Re-render, assert string absent | **YES** |
| 3 | Gallery section contains zero images | commercial | 0 `<img>` in gallery scope | **P0** | Remove the section, or add approved images that are **not** captioned as Ambient's own projects | Web dev | Re-render | **YES** |
| 4 | "Offer Ends in" countdown with no offer | commercial | `Offer Ends in 15 DAY 10 HRS…` | **P0** | Remove the countdown, or publish a real, client-approved, dated offer | Web dev + client | Re-render, assert absent | **YES** |
| 5 | `gform_1` rendered 3×, 34 duplicate DOM IDs | all 6 | `document.querySelectorAll('form#gform_1').length === 3` | **P1** | One form per page, or unique IDs per instance; confirm GTM fires one conversion per submission | Web dev + GTM | Re-render; single-submit test | **YES** (duplicate-conversion risk) |
| 6 | Testimonials tripled + `““` typo | commercial | 9 blocks, 3 unique | **P1** | Render once; fix the doubled quote | Web dev | Re-render | No |
| 7 | `tel:+14109141456` in DOM | all 6 | hidden `Call Now` anchor | **P2** | Replace with `tel:+14107056354` | Web dev | Assert no `4109141456` in HTML | No |
| 8 | `tel:` hrefs not E.164 | all 6 | `tel:4107056354`, `tel:(410) 705-6354` | **P2** | Use `tel:+14107056354` everywhere | Web dev | Assert all hrefs `+14107056354` | No |
| 9 | Meta description duplicates the title | commercial | observed vs intended | **P2** | Set the intended description | Web dev | Re-render | No |
| 10 | No `canonical` | all 6 | `link[rel=canonical]` absent | **P3** | Add self-referencing canonical | Web dev | Re-render | No |

**No safe production form-submission test route exists** (submitting would create a real CRM lead
and fire a real conversion). Defect 1 was proven by reading the server HTML instead — a stronger
test than a submission, because it shows the wrong value before anyone types anything.

---

## 5. Why volume collapsed — ranked causal diagnosis

### Regime-split delivery (settled data only; 2026-09-15 excluded as partial)

| Regime | Window | Impr | Clicks | Spend | Spend/day | CPC |
|---|---|---:|---:|---:|---:|---:|
| R1 August baseline | 08-01 → 08-31 | 4,577 | 155 | $6,842.80 | $220.74 | $44.15 |
| R2 Sept, pre-cap | 09-01 → 09-04 | 858 | 18 | $1,215.78 | $303.95 | $67.54 |
| **R3 post-cap** | 09-05 → 09-08 | 154 | 2 | $45.08 | **$11.27** | $22.54 |
| R4 post-09-09 negatives | 09-09 | 82 | 2 | $58.63 | $58.63 | $29.32 |
| R5 post-09-10 changes | 09-10 → 09-14 | 208 | 5 | $112.25 | **$22.45** | $22.45 |

The break is at **2026-09-04 16:56**, when the CPC ceilings were created
(`change_event` CAMPAIGN UPDATE `target_spend.cpc_bid_ceiling_micros`, 16:56:20 / 16:56:34 /
16:56:51, `GOOGLE_ADS_WEB_CLIENT`). Spend/day fell **96%** across that boundary and has not
recovered. Sept 5–14 ran at **$21.60/day against $421.55/day available — 5.1% of budget.**

### Impression share confirms the mechanism

| Campaign | Lost-IS rank, R2 | Lost-IS rank, R5 | Lost-IS **budget**, R5 |
|---|---:|---:|---:|
| AC Repair | 16.27%* | 79.25% | 0.00% |
| HVAC Repair | 43.10% | 76.92% | 0.00% |
| HVAC Installation | 35.29% | 75.00% | 0.00% |
| HVAC Replacement | 42.86% | 44.44% | 0.00% |

Rank loss roughly doubled. **Budget loss went to zero.** In August, HVAC Installation lost 55.29%
of impressions to budget; today it loses 0.00% to budget and 75% to rank. *Budget is not the
constraint. Rank is.*

### 🔴 The decisive finding: the ceilings exclude the price band where conversions happen

| Window | Converting clicks | **Avg CPC of converting clicks** | Non-converting clicks | Avg CPC |
|---|---:|---:|---:|---:|
| August | 10 | **$112.65** | 87 | $48.25 |
| Sept 1–14 | 3 | **$77.33** | 23 | $49.62 |

Every converting click, both windows:

```
$153.06  hvac companies near me open now     HVAC Repair
$153.03  hvac companies near me open now     HVAC Repair
$140.13  hvac near me                        AC Repair
$112.63  air conditioner repair near me      AC Repair
$109.87  emergency air conditioning repair   AC Repair
 $93.09  repair my ac                        AC Repair
 $68.16  cheap hvac service near me          AC Repair
 $59.92  hvac company near me                HVAC Installation
 $59.44  hvac ductwork installation near me  HVAC Installation
  $6.16  hvac near me                        HVAC Repair
```

**Current ceilings are $25 and $30. Twelve of the thirteen converting clicks — 92% — cost more
than every ceiling in the account.** Only one ($6.16) was buyable under today's caps.

The ceilings did not trim waste. They removed precisely the price band in which this account has
ever converted, and left the cheap non-converting traffic behind.

### Ranked causes

| # | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| 1 | CPC ceilings reduced auction eligibility | **PROVEN** | Exact timestamp break 09-04 16:56; spend/day −96%; lost-IS(rank) 29–43% → 75–86%; lost-IS(budget) → 0.00% |
| 2 | The ceilings sit below the converting price band | **STRONGLY SUPPORTED** | 12/13 converting clicks priced above every ceiling, across two independent windows. *n=13 — small, so not PROVEN* |
| 3 | Tracking mis-attributes or loses real paid leads | **PROVEN** | Proxy cache serves stale/empty click IDs; 0/24 loads captured the visitor's GCLID |
| 4 | Multiple Primary conversion actions duplicate one lead | **PROVEN** | 10 ENABLED Primary actions; 2026-09-01, one campaign: `WC Lead` 2.00 vs `LP -Submit Lead Forms` 1.00 — see §6 |
| 5 | Unstable query ownership across campaigns | **PROVEN** | 33 search terms appear in ≥2 of the five campaigns; `hvac companies near me` in both HVAC Installation and AC Repair |
| 6 | Generic company/contractor queries absorb spend | **PROVEN** | ~$638 of $1,431.74 settled-September spend (44.6%) on generic `hvac … near me` |
| 7 | Sitelinks divert paid clicks to non-converting pages | **STRONGLY SUPPORTED** | SITELINKS click type: 26 clicks, $1,284.80, **1** conversion. Campaign sitelinks point at `/reviews/` and `/our-work/` on the main site |
| 8 | Budget was the constraint | **NOT SUPPORTED** | lost-IS(budget) 0.00% across R5; spending 5.1% of available daily budget |
| 9 | Demand or seasonality changed | **NOT SUPPORTED** | eligible impressions held up — IS fell while impressions fell, i.e. lost auctions, not absent demand |
| 10 | Schedule reduced eligible volume | **NOT SUPPORTED** | out-of-schedule delivery is **$0.00 since 2026-08-21**; the $587.95 all predates the 08-20/21 schedule restoration |
| 11 | Location settings reduced volume | **NOT SUPPORTED** | `user_location_view`: 5,867 of 5,879 impressions matched `targeting_location=true`; 12 impressions / $0.00 outside |
| 12 | Ad policy restrictions reduced serving | **NOT SUPPORTED** | 10 ENABLED ads all APPROVED; the 6 CONSUMER_FINANCE disapprovals are PAUSED and excluded |
| 13 | Low ad relevance / landing-page experience raised rank loss | **POSSIBLE** | HVAC Repair + Replacement keywords sit at QS 2 with **below-average landing-page experience**; AC Repair QS 4. Contributory, not the trigger — the break aligns with the bid change, not a quality change |
| 14 | Broad negatives suppressed valid BOFU demand | **POSSIBLE — not yet tested** | 1,437 campaign negatives on HVAC Installation alone; no reachability test run this session |
| 15 | Invalid traffic distorted results | **UNMEASURABLE for spend** | Invalid clicks are filtered and never billed. Rates are extreme — AC Repair **97.0%** (942/971), HVAC Repair 95.6%, Gas Boiler 100%, HVAC Installation 45.4% — an auction-quality signal, not a spend loss |
| 16 | Competitor pressure increased | **UNMEASURABLE** | Auction Insights is not exposed for this account through the API resources available |

### Change-impact timeline

```
2026-08-14  five campaigns launch
2026-08-20/21  approved schedule restored — out-of-schedule delivery stops permanently
2026-09-04 16:56  CPC ceilings created ($25/$25/$30) via web UI   <-- THE BREAK
2026-09-04 16:59/17:00  two ads paused via web UI
2026-09-09      negative changes
2026-09-10 00:41  replacement ads enabled (AMB-0909-ADS-1)
2026-09-10 10:17  budgets set — Gas Boiler $5.00, HVAC Replacement $20.00 (AMB-0910-BUD-2)
2026-09-10 13:20  ceilings added to the last two campaigns (AMB-0910-CPC-CAP-1)
2026-09-10 13:52  commercial ad group CREATED **PAUSED**
2026-09-10 17:33  17 commercial ad-group negatives created (AMB-0910-COMM-NEG-3)
2026-09-15 08:42  commercial ad group switched PAUSED -> ENABLED via web UI   <-- DRIFT
2026-09-15 09:35  this session's identity gate
```

---

## 6. Conversion reconciliation and duplication map

**10 ENABLED conversion actions are flagged `primary_for_goal = true`.**

| Action ID | Name | Type | Counting | Primary | Can duplicate |
|---|---|---|---|---|---|
| 6885463625 | Ambient Cooling - LP -Submit Lead Forms | WEBPAGE | ONE_PER_CLICK | ✅ | with WC Lead |
| 7643656486 | WC Lead | UPLOAD_CLICKS | ONE_PER_CLICK | ✅ | with the above |
| 6885576934 | Ambient Cooling - Lp - Phone call leads | WEBSITE_CALL | ONE_PER_CLICK | ✅ | with Clicks to call, WC Calls |
| 1068114183 | Calls from ads | AD_CALL | ONE_PER_CLICK | ✅ | with WC Calls |
| 6640721230 | Clicks to call | GOOGLE_HOSTED | **MANY_PER_CLICK** | ✅ | with both call actions |
| 7643656075 | WC Calls | UPLOAD_CALLS | ONE_PER_CLICK | ✅ | with all call actions |
| 6642544931 | Local actions - Directions | GOOGLE_HOSTED | MANY_PER_CLICK | ✅ | not a lead |
| 6641739327 | Local actions - Website visits | GOOGLE_HOSTED | MANY_PER_CLICK | ✅ | not a lead |
| 6642551975 | Local actions - Other engagements | GOOGLE_HOSTED | MANY_PER_CLICK | ✅ | not a lead |
| 6954620053 | Local actions - Menu views | GOOGLE_HOSTED | MANY_PER_CLICK | ✅ | not a lead |

**One phone call can be counted up to four times** (WEBSITE_CALL + AD_CALL + Clicks to call +
WC Calls). **One form can be counted twice** (WEBPAGE + WC Lead upload).

### Duplication is observed, not merely possible

Settled September, campaign `24132507747`, **all on 2026-09-01**:

```
WC Lead                                 conversions 2.00
Ambient Cooling - LP -Submit Lead Forms conversions 1.00
Ambient Cooling and Heating (web) form_submission   all 2.00   (GA4, secondary)
Clicks to call                                      all 1.00
```

If two distinct form leads existed, the WEBPAGE action would read 2.00. It reads 1.00.
**At least one of the four September "conversions" is a duplicate of another.**

### What the Conversions column actually contains

| Window | Primary `conversions` | `all_conversions` |
|---|---:|---:|
| Settled Sept 01–14 | **4.00** | 29.00 |
| Launch to date (08-01 → 09-14) | **14.00** | 81.00 |

The gap is Local actions (Directions 8, Website visits 10, Other engagements 35 all-time) plus GA4
secondaries. Those categories — `GET_DIRECTIONS`, `PAGE_VIEW`, `ENGAGEMENT` — are **not biddable**
campaign goals on these five campaigns, so they do **not** feed bidding. They do inflate any report
that quotes "All conv.": **81 vs 14** is a 5.8× overstatement of lead volume.

**Zero Primary conversions have been recorded since 2026-09-01 — fourteen consecutive settled days.**

### Unique-lead bound

Given (a) proven duplication and (b) proven click-ID loss, the 4 settled-September records
correspond to **somewhere between 2 and 4 unique leads**, and that range cannot be tightened from
Google Ads alone. **CPQL is not computable this session.** WhatConverts API credentials are not
present in the environment, so the WhatConverts↔CRM reconciliation the master instruction asks for
is **BLOCKED** — see §11.

**Every CPQL figure in this account is an upper bound until defect 1 and the duplicate Primary set
are fixed.** No conversion mutation is proposed here: a conversion counted before a fix stays in
the historical column forever, so the correct order is measure → fix → re-baseline.

---

## 7. Query routing matrix and BOFU opportunities

189 distinct search terms, settled September. **33 appear in more than one campaign.**

| Family | Example (spend, clicks, conv) | Currently lands in | Should own it | Action |
|---|---|---|---|---|
| Generic HVAC company/contractor | `hvac companies near me` ($297.81, 8, **0**) | HVAC Installation **and** AC Repair | neither | **New generic BOFU ad group** — do not negative |
| | `hvac contractor near me` ($98.35, 3, 0) | both | " | " |
| | `hvac company near me` ($59.92, 1, **2**) | both | " | " — this one converts |
| | `heating and cooling companies near me` ($61.91, 1, 0) | both | " | " |
| | `hvac near me` ($57.41, 1, 0) | both | " | " |
| AC repair | `air conditioner repair near me` ($112.63, 1, **1**) | AC Repair | AC Repair ✅ | correct |
| | `ac maintenance near me` ($81.66, 1, 0) | AC Repair **and** HVAC Repair | AC Repair | routing negative |
| HVAC install | `hvac ductwork installation near me` ($59.44, 1, **1**) | HVAC Installation **and** Replacement | Installation | routing negative |
| HVAC replacement | `hvac replacement near me` ($0, 0, 0) | Replacement ✅ | correct |
| Boiler | `boiler check up near me` ($70.05, 1, 0) | **HVAC Repair** ❌ | Gas Boiler Repair | routing negative + keyword |
| Unsupported | `hydronic radiant floor heating installers near me` ($28.90, 1, 0) | HVAC Installation | none | verify capability first |
| Commercial | — none yet — | — | new commercial ad group | launching |

**Generic queries are 44.6% of settled-September spend (~$638 of $1,431.74) and produced 2 of the
4 conversions.** They are not waste and must not be negatived. They need a **dedicated generic BOFU
ad group** with its own landing page and its own economics, so the five service campaigns stop
bidding against each other for them. That is a Phase-1 plan, not this session's.

`boiler check up near me` costing $70.05 inside **HVAC Repair** while Gas Boiler Repair sits at
$5.00/day with zero clicks is the clearest single routing error in the account.

---

## 8. Asset inventory and decisions

| Asset | Live state | Decision |
|---|---|---|
| **Call** `407995613637` `(410)705-6354` | ENABLED, **APPROVED**, on all five campaigns, call reporting on | **Reuse. Create nothing.** Its schedule lives on the Asset — editing it would rewrite hours on every linked campaign |
| **Business name** `80516971145` `Ambient Cooling & Heating` | ENABLED on all five | Reuse |
| **Business logo** `200223860974` | **REMOVED** | Note only — not a launch blocker |
| **Campaign callouts** ×5 | ENABLED, APPROVED, generic (`Local Maryland Service`, `Prompt, Reliable Service`, `Clear Recommendations`, `Professional Technicians`, `Clear Service Options`) | Keep. Commercial-specific ad-group callouts proposed separately |
| **Campaign structured snippet** `407995609569` | `Service catalog: HVAC Installation, New HVAC Systems, He…` — residential wording | Keep; commercial `Types` snippet proposed at ad-group level |
| **Campaign sitelinks** on 24132507747 | 9 ENABLED — incl. `Customer Reviews` → `/reviews/` and `View Our Work` → `/our-work/` on the **main site** | ⚠️ cross-service leakage. **No removal proposed** — that needs a separate destructive approval |
| **Commercial ad-group sitelinks** | — | **DO NOT CREATE.** The page offers only `#quote-form`, privacy and terms. Fewer than four unique, commercially-relevant destinations exist. Reporting the limitation rather than inventing URLs |
| **Image assets** | none on these campaigns | **DO NOT CREATE.** The four candidate images are the ones the live page itself labels *"without presenting them as completed Ambient projects."* Presenting them beside an Ambient ad would do exactly that |

### Sitelink leakage is quantified

`SITELINKS` click type, 2026-08-01 → 09-14: **26 clicks, $1,284.80, 1 conversion.**
15.5% of all spend in the window went to sitelink clicks, and the campaign sitelinks route to
review/portfolio pages on the main website rather than to a paid landing page with a form.

### Click-type economics (2026-08-01 → 09-14)

| Click type | Clicks | Spend | Conversions | Cost/conv |
|---|---:|---:|---:|---:|
| URL_CLICKS | 101 | $4,075.89 | 5 | $815.18 |
| **LOCATION_EXPANSION** | 39 | $2,137.46 | **4** | **$534.37** |
| SITELINKS | 26 | $1,284.80 | 1 | $1,284.80 |
| **CALLS** | 10 | $576.51 | **4** | **$144.13** |
| GET_DIRECTIONS | 6 | $199.88 | 0 | — |

**LOCATION_EXPANSION converts better than ordinary URL clicks and must not be excluded.**
**CALLS is by far the most efficient click type** — the call asset is earning its place.

### Device

MOBILE 131 clicks / $6,588.16 / **14** conversions · DESKTOP 51 clicks / $1,686.37 / **0**.
$1,686 of desktop spend across six weeks with zero conversions. A device adjustment is a
candidate — but it is one variable, and it is not this launch's variable.

---

## 9. Prior-plan lineage — verified against live state, no replay

| Plan | Fingerprint | Verdict | Basis |
|---|---|---|---|
| `AMB-0910-BUD-2` | `93541FBB5D7F` | **ALREADY_EXECUTED** | Live budgets $5.00 / $20.00 match; combined $421.55 → $12,815.12 |
| `AMB-0909C-NEG-COMMERCIAL` | `9F88FEE76803` | **ALREADY_EXECUTED** | 1,437 campaign negatives; `commercial` absent at campaign and account level |
| `AMB-0909-ADS-1` | `11A79347A296` | **ALREADY_EXECUTED** | `821319509197` + `821319509200` ENABLED + APPROVED |
| `AMB-0910-CPC-CAP-1` | `7EA6922309EB` | **ALREADY_EXECUTED** | Ceilings $25/$25/$30/$30/$25 live |
| `AMB-0910-COMM-NEG-3` | `51CF5986F18A` | **ALREADY_EXECUTED** | 17/17 exact match, held-5 absent |
| `AMB-0910-COMM-RSA-2` | `41C183D15C93` | **DRIFTED → SUPERSEDED** | 404→200, ad group PAUSED→ENABLED, negatives 0→17 |
| `AMB-0910-COMM-XNEG-1` | `A70260017DAD` | **BLOCKED** | Commercial route still cannot serve (0 ads) |
| `AMB-0910-RSA-ACR-2` | `1F166DE17017` | **UNEXECUTED_AND_EXACT** | AC Repair ad group still holds exactly 2 ads. Separate workstream |
| `AMB-0910-COMM-NEG-1` | `C4142D5D5DE0` | SUPERSEDED | do not execute |
| `AMB-0910-COMM-NEG-1-FULL` | `A774B9C14896` | REJECTED | do not execute |
| `AMB-0910-COMM-NEG-2` | `A9C9BCBDDD74` | SUPERSEDED | do not execute |
| `AMB-0910-RSA-ACR-1` | `19E2F2FFC311` | SUPERSEDED | withdrawn Licensed & Insured claim |
| `AMB-0910-COMM-RSA-1` | `30312BC45992` | SUPERSEDED | do not execute |
| `AMB-0909C-CPC-INST-2` | `5D57E0EF3B70` | REJECTED | do not execute |

**Nothing was replayed. No executed plan was re-run.**

---

## 10. The plans awaiting approval

### `AMB-0915-COMM-RSA-1` — 2 operations — create-paused

Two materially distinct RSAs in ad group `199748801029`, **created PAUSED**.
Final URL `https://offer.ambientcoolingandheating.com/commercial-hvac-installation/`,
Path1 `commercial-hvac`, Path2 `installation`, no tracking template, no URL suffix,
no Final URL expansion, no automatically created assets.

Supersedes `41C183D15C93`. Three headlines were replaced because they did not appear on the live
page: `Commercial RTU Installation` → `Commercial Rooftop Units`; `Systems Built for Businesses` →
`Sized for Your Building`; `Keep Business Comfort in Mind` → `Ventilation, Ducts & Controls`.

**RSA A** — keyword-first, three openers pinned to HEADLINE_1 so Google still rotates:

| Pin | Chars | Headline |
|---|---:|---|
| H1 | 28 | Commercial HVAC Installation |
| H1 | 26 | Commercial HVAC Installers |
| H1 | 30 | HVAC Installation for Business |
| — | 26 | Free Commercial HVAC Quote |
| — | 25 | Rooftop Unit Installation |
| — | 24 | Commercial Rooftop Units |
| — | 26 | Commercial AC Installation |
| — | 28 | Commercial Heat Pump Install |
| — | 23 | Sized for Your Building |
| — | 26 | Central Maryland HVAC Team |
| — | 27 | Plan Around Your Operations |
| — | 30 | Transparent Commercial Pricing |
| — | 27 | Flexible Project Scheduling |
| — | 25 | Ambient Cooling & Heating |
| — | 26 | Request a Commercial Quote |

Descriptions (85 / 86 / 88 / 85 of 90):
1. Request a free commercial HVAC installation quote for your Central Maryland property.
2. Install rooftop units, packaged systems, heat pumps, or central air for your business.
3. Plan equipment, ductwork, ventilation, and controls around your building and operations.
4. Get clear options, transparent pricing, and scheduling designed around your business.

**RSA B** — unpinned control: `HVAC Systems for Businesses` · `Central MD Commercial HVAC` ·
`Commercial System Installation` · `Replace Aging HVAC Equipment` · `Rooftop & Packaged Systems` ·
`Business Heating & Cooling` · `Commercial HVAC Planning` · `Free Installation Quote` ·
`HVAC Options for Your Building` · `Schedule a Site Evaluation` · `Ventilation, Ducts & Controls` ·
`Professional HVAC Installation` · `Central Air for Your Business` · `Heat Pumps for Businesses` ·
`Request Your HVAC Quote`

Descriptions (84 / 85 / 86 / 82 of 90):
1. Replace or install commercial HVAC equipment with a plan built around your property.
2. Request a free consultation for rooftop, packaged, central air, or heat pump systems.
3. Ambient serves Central Maryland businesses with clear pricing and flexible scheduling.
4. Discuss building needs, equipment options, ductwork, controls, and project timing.

**Validation**

| Check | Result |
|---|---|
| Headlines per ad / descriptions per ad | 15 / 4 and 15 / 4 |
| Character limits | every headline ≤30, every description ≤90 — **0 overruns** |
| Duplicates within each ad | none |
| Copy shared between RSA A and RSA B | **none** |
| Barred claims (24/7, emergency, same-day, guarantee, warranty, financing, rating, price, superlative, Licensed & Insured) | **0** |
| Every claim verbatim-supported by the live page | **20/20 OK** |
| `validate_only=True` against Google | **VALIDATED_OK — both operations accepted, nothing created** |
| Fingerprint recomputed from disk | match |

### `AMB-0915-COMM-ASSET-1` — 7 operations — create-paused

6 commercial callouts + 1 structured snippet, linked to ad group `199748801029` with the asset
link **PAUSED**. Every value appears verbatim on the live page; zero overlap with the 5 existing
campaign callouts.

Callouts: `Free Consultation` (17) · `Flexible Scheduling` (19) · `Transparent Pricing` (19) ·
`Central Maryland Service` (24) · `Multiple System Options` (23) · `Commercial HVAC Team` (20)
Structured snippet `Types`: Rooftop Units · Packaged Systems · Heat Pumps · Central Air ·
HVAC Replacement

Ad-group assets take precedence for this ad group only, so the residential ad group is untouched.

### Recommendation on sequencing

**Approve `AMB-0915-COMM-RSA-1` now, before the landing-page fixes.** The ads are created PAUSED
and cannot serve, so this carries no delivery risk — and it starts Google's policy review running
in parallel with the developer work instead of after it. If Google flags anything about the
destination, we learn it immediately and cheaply. Enablement stays gated on both policy APPROVED
**and** the four P0 landing-page defects being closed.

`AMB-0915-COMM-ASSET-1` is optional at this stage; the ad group already inherits an approved call
asset, five callouts, a structured snippet, a business name and nine sitelinks.

---

## 11. Blocked, missing, and not done

| Item | Status | Why |
|---|---|---|
| WhatConverts ↔ Google Ads ↔ CRM lead reconciliation | **BLOCKED** | No WhatConverts API token in the environment. `whatconverts_api_token_present: false`. Per-lead GCLID/UTM/qualification/booking/revenue joins cannot be produced |
| Qualified-lead, sold-job, revenue, gross-profit, CPQL, CAC, ROAS | **MISSING DATA** | `average_job_revenue`, `gross_margin_pct`, `close_rate_pct`, `target_cpl/cpql/cac` are all null in `client.yaml`. No profitability verdict is possible — the §18 guardrails stay provisional |
| Auction Insights | **BLOCKED** | Not exposed through the API resources available to this account |
| Keyword Planner demand refresh | **NOT RUN** | Deferred — it has its own quota that 429s fast, and it is not on the commercial launch critical path. Needed before the Phase-1 generic BOFU ad group |
| Negative reachability audit (1,437 campaign negatives) | **NOT RUN** | Hypothesis 14 stays POSSIBLE. It is a large two-stage reachability job and it is not a launch gate |
| Safe production form-submission test | **NOT AVAILABLE** | Would create a real CRM lead and fire a real conversion. Defect 1 was proven from the server HTML instead |
| Reverting the ad group to PAUSED | **NOT DONE** | Owner's own action; reverting would be an unapproved external write. Say the word and I will draft it |

---

## 12. Commercial launch status

| Field | Status |
|---|---|
| Landing page | **LIVE, HTTP 200** — 4 P0 defects block enablement |
| Tracking | **FAIL** — proxy cache serves stale/empty click IDs (0/24) |
| Ad group | **ENABLED** (drift, 2026-09-15 08:42:16) — cannot serve, 0 ads |
| Keyword PHRASE / EXACT | ENABLED, APPROVED, ELIGIBLE / same |
| Negatives | **COMPLETE** — 17/17 verified |
| RSA count / IDs | **0 / none** |
| RSA policy status | n/a |
| Assets | inherits call `407995613637` (APPROVED), business name, 5 callouts, snippet, 9 sitelinks |
| Create-paused | **AWAITING APPROVAL** |
| Enablement | **NOT STARTED** — gated |
| Routing negative | **BLOCKED** — correctly deferred |

---

## 13. Staged 30-day recovery plan

**Phase 0 — measurement integrity (do this first; nothing else is trustworthy without it)**
1. Purge the proxy cache and re-architect attribution-field population client-side. *Web dev.*
2. Retest with `ambient_0915_gclid_probe.py` — require **24/24**.
3. Collapse the 10 Primary conversion actions to one form action + one call action; demote the four
   Local actions and the duplicate call actions to Secondary. *Separate fingerprinted plan.*
4. Re-baseline. Historical conversions are never restated, so the new baseline starts at the fix.

**Phase 1 — restore valid BOFU reach (one campaign at a time)**
5. Fix routing: `boiler check up near me` → Gas Boiler Repair; de-duplicate the 33 cross-campaign terms.
6. Build the generic BOFU ad group for the `hvac compan*/contractor near me` family. Do not negative it.
7. Re-point campaign sitelinks from `/reviews/` and `/our-work/` to paid landing pages.

**Phase 2 — response and conversion**
8. Fix landing-page experience on HVAC Repair and HVAC Replacement (QS 2, below-average LPE).
9. Execute `AMB-0910-RSA-ACR-2` (AC Repair challenger, already exact and unexecuted).

**Phase 3 — controlled auction test — the one that matters most**
10. One campaign, one variable. My recommendation: **HVAC Repair**, because it has the clearest
    evidence (August CPC $106.27 against a $25 cap, 0 clicks in 10 days, lost-IS(rank) 77–90%).
    The §25 guardrail caps a step at +20% — $25 → $30. **I need to flag honestly that +20% will
    almost certainly change nothing**, because the clearing price is ~4× the cap. A meaningful test
    is $25 → $60–$75, which is a business decision about risk appetite, not a technical one. It is
    the single question in §14.

**Phase 4 — Commercial HVAC Installation**
11. Approve `AMB-0915-COMM-RSA-1` → create paused → readback → await policy APPROVED.
12. Close the four P0 landing-page defects.
13. Separate enablement plan and approval → enable → readback → prove the serving chain.
14. Only then the residential routing negative `A70260017DAD`.

**Phase 5 — settled evaluation**
15. Hold structure stable. Health checks at readback, ~24 h, ~72 h. First performance judgement
    only after 14 settled days, and only on qualified leads and CPQL, never Ad Strength or
    Optimization Score.

---

## 14. What would change if you approve

| Plan | Ops | Creates | Serves? | Changes budget / bid / schedule / geo / conversions? |
|---|---:|---|---|---|
| `AMB-0915-COMM-RSA-1` | 2 | 2 RSAs, status PAUSED, in ad group `199748801029` | **No** | **No** |
| `AMB-0915-COMM-ASSET-1` | 7 | 6 callouts + 1 snippet, ad-group link PAUSED | **No** | **No** |

Unchanged and asserted in both plans: campaign `24132507747` status, budget $176.15, ceiling
$30.00, schedule (6 rows), 75 locations, PRESENCE, networks, conversion goals; residential ad group
`202339087634` and its ads `821319509197` / `821319509200`; the other four campaigns; the 17
ad-group negatives; both positive keywords; every campaign and account negative; every existing asset.

### Approval lines

```
APPROVE AMB-0915-COMM-RSA-1 6C32B210CF5B 2 operations FOR 2401959466
APPROVE AMB-0915-COMM-ASSET-1 02F6EECCCDF8 7 operations FOR 2401959466
```

### Do not execute

`AMB-0910-COMM-RSA-2 41C183D15C93` · `AMB-0910-COMM-NEG-2 A9C9BCBDDD74` ·
`AMB-0910-COMM-NEG-1 C4142D5D5DE0` · `AMB-0910-COMM-NEG-1-FULL A774B9C14896` ·
`AMB-0910-RSA-ACR-1 19E2F2FFC311` · `AMB-0910-COMM-RSA-1 30312BC45992` ·
`AMB-0909C-CPC-INST-2 5D57E0EF3B70` · `AMB-0910-COMM-XNEG-1 A70260017DAD` (still gated)

### The one question that needs a business decision

**The CPC-ceiling test size.** A +20% step on HVAC Repair ($25 → $30) is the conservative policy
default and I can draft it today, but the evidence says it will not restore delivery — the clearing
price is ~$106 and 12 of 13 historical converting clicks cost more than $30. A test at $60–$75 has a
real chance of working and risks roughly $600–$750 of the $184.88-headroom-constrained budget before
a stop-loss triggers. **My recommendation: $25 → $65 on HVAC Repair only, with a $250 no-lead
stop-loss and a defined rollback** — but this is your risk call, not mine, so I have not drafted it.

---

## 15. Evidence

```
clients/ambient-cooling-heating/work-order-commercial-hvac-installation.yaml
clients/ambient-cooling-heating/plans/AMB-0915-COMM-RSA-1.json
clients/ambient-cooling-heating/plans/AMB-0915-COMM-ASSET-1.json
clients/ambient-cooling-heating/snapshots/identity-and-structure-2026-09-15.json
clients/ambient-cooling-heating/snapshots/commercial-inventory-2026-09-15.json
clients/ambient-cooling-heating/snapshots/assets-and-conversions-2026-09-15.json
clients/ambient-cooling-heating/snapshots/performance-2026-09-15.json
clients/ambient-cooling-heating/snapshots/diagnostics-2026-09-15.json
clients/ambient-cooling-heating/snapshots/lp-browser-qa-2026-09-15.json
clients/ambient-cooling-heating/snapshots/lp-commercial-deep-2026-09-15.json
clients/ambient-cooling-heating/snapshots/gclid-capture-probe-2026-09-15.json
clients/ambient-cooling-heating/snapshots/plan-lineage-2026-09-15.json
receipts/validate-only/AMB-0915-COMM-RSA-1-2026-09-15.json
```

**External writes this session: ZERO.** One `validate_only=True` request (2 operations, nothing
committed). All other Google Ads traffic was read-only. All landing-page traffic was GET-only: no
form submitted, no `tel:` link activated, no website, GTM, WhatConverts, CRM or conversion change.
