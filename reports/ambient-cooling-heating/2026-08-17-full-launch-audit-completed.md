# Ambient Cooling & Heating — Completed Launch Audit

**Client:** Ambient Cooling & Heating LLC
**Child account:** `Ambient Cooling - Live` · **ID** `240-195-9466` (`2401959466`)
**Manager:** `Green Marketing` · `3373711342` (verified via hierarchy)
**Vertical:** heating-cooling · **Currency:** USD · **Timezone:** America/New_York
**Campaign launch:** Friday 2026-08-14 13:04:40 · **Audit date:** 2026-08-17
**Phases:** `READ` (full audit) + `DRAFT` (search-term analysis and negative package)

> **No external changes were made.** Every Google Ads call was a GAQL `SELECT`. No campaign was
> paused or enabled, no budget or bid changed, no keyword or negative added, no shared list
> attached, no ad or asset edited, no conversion goal changed, no GTM change published, no
> website edit, no form submitted, no telephone link clicked, no call placed.

> Supersedes the identity-blocked report `2026-08-17-full-launch-audit.md`, which is preserved.

---

## 1. Final verdict

# ⛔ FAIL

The identity gate now passes and the campaign *scaffolding* is largely built to spec — but the
launch is not functioning. Three of five campaigns cannot serve, the account has spent **$22.68
of a $13,000 plan**, conversion tracking is absent from every landing page, and the primary
mobile call CTA still dials the wrong number.

| Dimension | Verdict |
|---|---|
| Identity gate | ✅ **PASS** |
| Launch configuration health | ⚠️ **PASS WITH WARNINGS** — correct names, networks, geo, 75 locations; wrong bidding, duplicated schedules, zero negatives |
| Delivery health | ⛔ **FAIL** — 178 impressions, 2 clicks, $22.68 in 3.5 days; 2 of 5 campaigns have never served |
| Search-intent quality | ✅ **PASS** — keywords are tight, Phrase/Exact only, no Broad |
| Tracking reliability | ⛔ **FAIL** — no tag of any kind on any landing page; a tel-link click is a biddable goal |
| Early conversion performance | ⚪ **INSUFFICIENT DATA** — 0 conversions on 2 clicks |
| Profitability | ⚪ **CANNOT BE ASSESSED** — no target CPL/CPQL, no qualified-lead or sold-job data |

---

## 2. Executive summary

1. **Identity gate passes.** The account was renamed between my first and second lookup. Fresh
   API now returns `Ambient Cooling - Live`, matching the confirmed name exactly and carrying the
   required `- live` marker. Not a manager, not a test account, level 1 under `Green Marketing`
   (`3373711342`), USD, America/New_York. Both project validators pass.

2. **⚠️ The manager ID supplied in the request is wrong.** `1247547723` does not resolve
   ("No customer found for the provided customer id") and is not a manager of this child. Verified
   through the hierarchy, the manager is **`3373711342` = `Green Marketing`**. I used the verified
   value and did not act on the supplied one.

3. **All five campaigns exist with the exact expected names**, correct Search-only settings,
   PRESENCE targeting, exactly **75 Maryland location targets each**, and Phrase+Exact keywords
   with no Broad Match. That part of the build is good.

4. **⛔ Three of five campaigns cannot serve.** Six RSAs are **DISAPPROVED** under Google's
   **CONSUMER_FINANCE** policy, making HVAC Installation, HVAC Replacement, and Gas Boiler Repair
   `NOT_ELIGIBLE`. **Gas Boiler Repair and HVAC Replacement have had zero impressions since launch.**

5. **⛔ Spend is $22.68 against a $13,000 plan — and budget is not the constraint.** Lost
   impression share from budget is **0.0%**; lost IS from **rank is 82–90%**. Impression share is
   10–18%. Quality Score is **2/10** on `ac repair near me` and **4/10** on `hvac repair near me`,
   with **Below Average landing-page experience** — which ties the delivery failure directly to the
   landing pages.

6. **⛔ Tracking is entirely absent from all five landing pages** — retested today, unchanged.
   Zero requests to `googletagmanager.com`, no `dataLayer`, no `gtag`, no `GTM-`/`AW-`/`G-` ID.
   `GTM-PQTPQ436` is installed on the **main site** but never deployed to the `offer.` subdomain.

7. **⛔ The wrong phone number is still live.** `tel:+14107610932` is the prominent yellow
   "Call Now" button — `display:none` on desktop, **visible and tappable on mobile** on all five
   pages — plus it appears in FAQ copy on three pages. Confirmed again today.

8. **⛔ A telephone-link click is a biddable conversion goal.** `Call BTN Click` (WEBPAGE /
   CONTACT) is Primary and counted, and `CONTACT / WEBSITE` is biddable on **all five campaigns**.
   There are also **three competing Primary phone-lead actions** and **two Primary WhatConverts
   upload actions**, despite WhatConverts not being the platform for this account.

9. **⚠️ Every sitelink sends paid clicks to the main website** (`ambientcoolingandheating.com`),
   which uses the **wrong phone number** and has no offer form. **New finding.**

10. **The five campaigns launched with zero negative keywords** — no campaign negatives, no
    ad-group negatives, no shared list attached. The account holds 16 negative lists, and **4 of
    them are actively dangerous**: `General List` contains BROAD `repair`, and
    `Ambient - Neg Kwd List` blocks `severn` and `arundel` — Ambient's own service area.

11. **Search-term research is complete.** 13,118 distinct terms, $65,352 of historical spend
    analyzed. **314 conflict-tested negatives proposed** (374 mutations), covering **$6,138** of
    directly evidenced waste, with **zero** conflicts against approved keywords or converting
    demand. **Plan fingerprint `12E7572A25B9AFF0`.** Nothing applied.

---

## 3. Corrected account identity and fresh API evidence

| Check | Required | Observed (fresh `SELECT`) | Result |
|---|---|---|---|
| Child account name | `Ambient Cooling - Live` | `Ambient Cooling - Live` | ✅ exact |
| `- live` marker | present | present | ✅ |
| Child customer ID | `2401959466` | `2401959466` | ✅ exact |
| Not a manager account | true | `manager = False` | ✅ |
| Not a test account | true | `test_account = False` | ✅ |
| Under Green Marketing hierarchy | true | level 1 under `3373711342`, `ENABLED` | ✅ |
| Currency | USD | `USD` | ✅ |
| Timezone | America/New_York | `America/New_York` | ✅ |
| Account status | — | `ENABLED` | ✅ |
| Auto-tagging | — | `True` | ✅ |

**Validators**

```
$ python scripts/validate_work_order.py clients/ambient-cooling-heating/work-order.yaml \
      --client clients/ambient-cooling-heating/client.yaml
Work order: PASS | Ambient Cooling - Live | 2401959466 | heating-cooling | AC Repair   (exit 0)

$ python scripts/verify_setup.py --client clients/ambient-cooling-heating/client.yaml
Credential variable names: present
Preflight: PASS                                                                        (exit 0)
```

### 3.1 Manager verification — discrepancy

Verified through the configured hierarchy rather than the URL, as instructed:

- `customer_manager_link` on the child returns **two ACTIVE managers**: `3373711342` and
  **`2815082755`**.
- `customer_client` from `3373711342` shows the child at **level 1**, `ENABLED`.
- Identity of `3373711342` → `descriptive_name = "Green Marketing"`, `manager = True`. ✅
- **`1247547723` → `"No customer found for the provided customer id."`** It is not reachable and
  is not a manager of this child; it is most likely a UI/`ocid` parameter. **No operation used it.**

⚠️ **The second ACTIVE manager link `2815082755` should be confirmed as expected.**

### 3.2 Superseded identity conflict (preserved)

The first lookup returned `Ambient Cooling` (no `- live`) and correctly blocked the audit. The
account was renamed between the two lookups. Recorded in `client.yaml` as
`identity_conflict_superseded`; `identity_gate` is now authoritative.

`OLD Ambient C&H` (`2391758435`) is confirmed **still ENABLED** but was **not read, audited, or
selected**. It has no work order and needs its own gate.

---

## 4. Account-wide campaign inventory

**23 non-removed campaigns. Only the five new campaigns are ENABLED. Every legacy campaign —
including all four Performance Max — is PAUSED.**

### 4.1 Enabled

| Campaign | ID | Primary status | Daily budget | Budget ID | Shared |
|---|---|---|---:|---|---|
| Search \| NonBrand \| AC Repair \| Central MD \| BOFU \| 2026-08 | 24132507741 | LEARNING | $141.45 | 15787409435 | No |
| Search \| NonBrand \| HVAC Repair \| Central MD \| BOFU \| 2026-08 | 24132507750 | LEARNING | $78.95 | 15787409444 | No |
| Search \| NonBrand \| HVAC Installation \| Central MD \| BOFU \| 2026-08 | 24132507747 | **NOT_ELIGIBLE** | $138.16 | 15787409441 | No |
| Search \| NonBrand \| HVAC Replacement \| Central MD \| BOFU \| 2026-08 | 24132507753 | **NOT_ELIGIBLE** | $26.32 | 15787409447 | No |
| Search \| NonBrand \| Gas Boiler Repair \| Central MD \| BOFU \| 2026-08 | 24132507744 | **NOT_ELIGIBLE** | $42.76 | 15787409438 | No |

`NOT_ELIGIBLE` reasons: `BIDDING_STRATEGY_LEARNING`, **`HAS_ADS_DISAPPROVED`**.

✅ **Campaign naming matches the expected pattern exactly on all five. No naming mismatch.**

### 4.2 Paused legacy campaigns (18) — none spending

| Campaign | Type | Budget | Spend last 365d |
|---|---|---:|---:|
| Leads-Performance Max-HVAC & A/C Install | PMAX | $100.00 | $13,612.58 |
| Tankless Water Heaters | SEARCH | $60.00 | $12,531.77 |
| Gas Boilers Installs | SEARCH | $60.00 | $9,436.70 |
| HVAC Install | SEARCH | $30.00 | $8,716.95 |
| HVAC Repair | SEARCH | $100.00 | $7,563.27 |
| Gas Boilers Repair | SEARCH | $60.00 | $6,383.12 |
| Heating Installation | SEARCH | $33.33 | $5,454.24 |
| Leads-Performance Max-Furnace-Repair | PMAX | $10.00 | $4,754.57 |
| Leads-Performance Max-HVAC & A/C Install #2 | PMAX | $33.00 | $1,478.26 |
| Pool Room Dehumidifier | SEARCH | $33.00 | $1,192.08 |
| Heating Repair | SEARCH | $38.00 | $825.29 |
| AC Install & Replacement | SEARCH | $90.00 | $516.28 |
| Air Quality And Purification | SEARCH | $33.33 | $214.08 |
| Geothermal HVAC | SEARCH | $100.00 | $151.80 |
| Heating Maintenance | SEARCH | $39.00 | $127.82 |
| Mini Split | SEARCH | $100.00 | $18.77 |
| Leads-Performance Max-HVAC-Install | PMAX | $90.00 | (ended) |
| Tankless Boilers | SEARCH | $100.00 | — |

✅ **No unrelated campaign is spending.** Verified in the launch-to-date, today, and last-7 windows:
**zero** non-new campaigns with spend > $0. Historical legacy spend totals roughly **$73,000**.

⚠️ Four Performance Max campaigns exist. All paused. Flagged, **not** paused or altered by me.

### 4.3 Account-level configuration

| Item | Observed |
|---|---|
| Shared budgets | **None** — all five use individual budgets |
| Account-level negative list | `account-level negative keywords list` (11252984411), 59 BROAD members, **not attached to the new campaigns** |
| Account tracking template | ClickCease redirect on every click (see P1-7) |
| Final URL suffix | *(empty)* |
| Conversion tracking | ID `11155434808`, `MANAGED_BY_SELF` |
| Auto-applied recommendations | No auto-apply setting exposed; **0 pending recommendations** returned |
| Account assets | No customer-level assets linked |
| Policy / billing blockers | None at account level; account `ENABLED` |

---

## 5. Five-campaign configuration matrix

| Setting | Expected | AC Repair | HVAC Repair | HVAC Install | HVAC Replace | Gas Boiler | Verdict |
|---|---|---|---|---|---|---|---|
| Status | ENABLED | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Serving status | SERVING | SERVING | SERVING | SERVING | SERVING | SERVING | ✅ |
| Primary status | eligible | LEARNING | LEARNING | **NOT_ELIGIBLE** | **NOT_ELIGIBLE** | **NOT_ELIGIBLE** | ⛔ |
| Start date | 2026-08-14 | ✅ 13:04:40 | ✅ | ✅ | ✅ | ✅ | ✅ |
| End date | none | none | none | none | none | none | ✅ |
| Type / subtype | Search | SEARCH / — | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bidding strategy | conversion-based | **TARGET_SPEND** | **TARGET_SPEND** | **TARGET_SPEND** | **TARGET_SPEND** | **TARGET_SPEND** | ⛔ |
| Bid-strategy status | — | LEARNING_NEW | LEARNING_NEW | LEARNING_NEW | LEARNING_NEW | LEARNING_NEW | ⚠️ |
| Daily budget | see §7 | $141.45 | $78.95 | $138.16 | $26.32 | $42.76 | ✅ |
| Shared budget | individual | No | No | No | No | No | ✅ |
| Google Search | on | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Search Partners** | **off** | ✅ off | ✅ off | ✅ off | ✅ off | ✅ off | ✅ |
| **Display Network** | **off** | ✅ off | ✅ off | ✅ off | ✅ off | ✅ off | ✅ |
| **AI Max** | **off** | ✅ off | ✅ off | ✅ off | ✅ off | ✅ off | ✅ |
| **Broad-match expansion** | **off** | ✅ UNSPECIFIED | ✅ | ✅ | ✅ | ✅ | ✅ |
| **DSA** | **off** | ✅ no domain | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Final URL expansion** | **off** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Auto-created assets** | **off** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Text customization** | **off** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Location method | **PRESENCE** | ✅ PRESENCE | ✅ | ✅ | ✅ | ✅ | ✅ |
| Negative geo method | PRESENCE | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Location targets | 75 | ✅ **75** | ✅ **75** | ✅ **75** | ✅ **75** | ✅ **75** | ✅ |
| Location exclusions | — | 0 | 0 | 0 | 0 | 0 | ✅ |
| Ad schedule | Mon–Fri 08–16 | **11 rows, duplicated** | same | same | same | same | ⛔ |
| Device criteria | 3, no adjustment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Audience setting | observation | ✅ `AUDIENCE bid_only=true` | ✅ | ✅ | ✅ | ✅ | ✅ |
| Campaign tracking template | none | ✅ empty | ✅ | ✅ | ✅ | ✅ | ✅ |

**Ad serving:** `OPTIMIZE` on all five (rotates toward best performers) — acceptable.

### 5.1 ⛔ Bidding strategy is Maximize Clicks

All five run **`TARGET_SPEND`** — Maximize Clicks — with no target CPA and no target ROAS. The
stated goal is *new customer leads*. Maximize Clicks buys the cheapest available clicks and
optimizes for volume, not lead quality. Combined with zero landing-page conversion tracking, no
conversion-based strategy could work today even if selected — so this must be sequenced **after**
tracking is fixed.

### 5.2 ⛔ Duplicated and unapproved ad schedules

A fresh read returns **11 ad-schedule criteria per campaign**, not the 6 that a first pass showed:

| Rows | Schedule | Status |
|---|---|---|
| 5 | Mon–Fri **08:00–16:00** | ENABLED — the approved window |
| 5 | Mon–Fri **08:00–20:00** | ENABLED — **unapproved duplicate** |
| 1 | **Saturday 08:00–13:00** | ENABLED — **unapproved addition** |

Overlapping schedules take the **union**, so the effective window is **Mon–Fri 08:00–20:00 plus
Saturday 08:00–13:00** — four extra hours every weekday and a day never approved.

**Change history explains the weekend delivery.** On **2026-08-17 between 10:39 and 10:47**, 36
`CAMPAIGN_CRITERION` records were **CREATED** and 12 **REMOVED** via `GOOGLE_ADS_WEB_CLIENT`. The
schedules were therefore added **today — three days after launch**. From Aug 14 to Aug 17 10:39
the campaigns ran with **no schedule at all**:

- **114 impressions, 1 click, $20.34** delivered outside any configured window.
- The single most expensive click of the entire launch — **$20.34 — was Sunday 2026-08-16 at
  17:00**, a day with no schedule row.

⚠️ Someone else was editing this account during the audit window.

---

## 6. Campaign, ad-group, keyword, RSA, and asset findings

### 6.1 Ad groups

| Campaign | Ad group | ID | Status | Notes |
|---|---|---|---|---|
| AC Repair | `SKAG \| AC Repair Near Me` | 202339087834 | ENABLED | ✅ |
| AC Repair | **`SKAG \| HVAC Replacement Near Me`** | 202339087874 | **REMOVED** | ⚠️ rogue ad group in the wrong campaign |
| HVAC Repair | `SKAG \| HVAC Repair Near Me` | 202339087674 | ENABLED | ✅ |
| HVAC Installation | `SKAG \| HVAC Installation` | 202339087634 | ENABLED | ✅ |
| HVAC Replacement | `SKAG \| HVAC Replacement Near Me` | 200159223798 | ENABLED | ✅ |
| Gas Boiler Repair | `SKAG \| Gas Boiler Repair` | 202339087594 | ENABLED | ✅ |

✅ One SKAG-style ad group per campaign, as intended. ⚠️ The AC Repair campaign carries a second,
REMOVED ad group for HVAC Replacement — build residue.

### 6.2 Keywords

| Campaign | Keyword | Match | Status | Approval | QS | Exp. CTR | Ad rel. | LP exp. |
|---|---|---|---|---|---|---|---|---|
| AC Repair | `ac repair near me` | PHRASE | ENABLED | APPROVED | **2** | Below avg | Average | **Below avg** |
| AC Repair | `ac repair near me` | EXACT | ENABLED | APPROVED | **2** | Below avg | Average | **Below avg** |
| AC Repair | ⚠️ `hvac replacement near me` | PHRASE | ENABLED | APPROVED | — | — | — | — |
| AC Repair | ⚠️ `hvac replacement near me` | EXACT | ENABLED | APPROVED | — | — | — | — |
| HVAC Repair | `hvac repair near me` | PHRASE | ENABLED | APPROVED | **4** | Below avg | Average | Average |
| HVAC Repair | `hvac repair near me` | EXACT | ENABLED | APPROVED | **4** | Below avg | Average | Average |
| HVAC Installation | `hvac installers` | PHRASE / EXACT | ENABLED | APPROVED | — | — | — | — |
| HVAC Replacement | `hvac replacement near me` | PHRASE / EXACT | ENABLED | APPROVED | — | — | — | — |
| Gas Boiler Repair | `gas boiler repair` | PHRASE / EXACT | ENABLED | APPROVED | — | — | — | — |

✅ Every expected keyword theme is present, Phrase + Exact, **no Broad Match anywhere**, all
`ELIGIBLE` and `APPROVED`, no informational keywords, no unnecessary expansion.

⚠️ **Cross-campaign duplicate:** `hvac replacement near me` exists in **both** the AC Repair
campaign and the HVAC Replacement campaign. In AC Repair those keywords sit in the **REMOVED** ad
group, so they cannot currently serve and there is **no live internal competition** — but they
should be cleaned up.

⛔ **Quality Score 2/10 on the primary AC Repair keyword** with **Below Average landing-page
experience** — the strongest single link between the landing-page defects and the delivery failure.
`Below Average` expected CTR on both scored keywords also points at ad relevance.

### 6.3 RSAs — ⛔ four per ad group, not two, and six are disapproved

| Campaign | Ad ID | Ad group | Status | Strength | Approval | Policy topic |
|---|---|---|---|---|---|---|
| AC Repair | 820900825416 | AC Repair Near Me | ENABLED | AVERAGE | APPROVED | — |
| AC Repair | 820900825419 | AC Repair Near Me | ENABLED | AVERAGE | APPROVED | — |
| AC Repair | 820789851723 | AC Repair Near Me | ENABLED | AVERAGE | APPROVED | — |
| AC Repair | 820789851726 | AC Repair Near Me | ENABLED | AVERAGE | APPROVED | — |
| AC Repair | 820900825422 | *(removed ad group)* | ENABLED | AVERAGE | **AREA_OF_INTEREST_ONLY** | CONSUMER_FINANCE |
| AC Repair | 820900825425 | *(removed ad group)* | ENABLED | POOR | **AREA_OF_INTEREST_ONLY** | CONSUMER_FINANCE |
| HVAC Repair | 820900825560 / 820900825563 / 820789851729 / 820789851732 | HVAC Repair Near Me | ENABLED | POOR/AVG | APPROVED | — |
| HVAC Installation | **820900825434** | HVAC Installation | ENABLED | POOR | **DISAPPROVED** | **CONSUMER_FINANCE (FULLY_LIMITED)** |
| HVAC Installation | **820900825437** | HVAC Installation | ENABLED | EXCELLENT | **DISAPPROVED** | **CONSUMER_FINANCE (FULLY_LIMITED)** |
| HVAC Installation | 820789851735 / 820789851738 | HVAC Installation | ENABLED | GOOD/EXCELLENT | APPROVED | — |
| HVAC Replacement | **820944944368** | HVAC Replacement Near Me | ENABLED | POOR | **DISAPPROVED** | **CONSUMER_FINANCE** |
| HVAC Replacement | **820944944371** | HVAC Replacement Near Me | ENABLED | POOR | **DISAPPROVED** | **CONSUMER_FINANCE** |
| HVAC Replacement | 820789851741 / 820789851744 | HVAC Replacement Near Me | ENABLED | POOR/AVG | APPROVED | — |
| Gas Boiler Repair | **820900825428** | Gas Boiler Repair | ENABLED | EXCELLENT | **DISAPPROVED** | **CONSUMER_FINANCE** |
| Gas Boiler Repair | **820900825431** | Gas Boiler Repair | ENABLED | EXCELLENT | **DISAPPROVED** | **CONSUMER_FINANCE** |
| Gas Boiler Repair | 820789851xxx ×2 | Gas Boiler Repair | ENABLED | — | APPROVED | — |

**22 RSAs across 6 ad groups — roughly 4 per ad group against a standard of 2.** Two generations
of ads coexist (`8207898517xx` built first, `8209008254xx`/`8209449443xx` added later) and the
older set was never removed. This splits impressions and slows learning.

**Direct-response vs psychology split:** the intended pairing is present and correct within each
generation — e.g. HVAC Installation ad `820900825434` is direct-response ("HVAC Installers in
Severn", "Get an HVAC Installation Quote") while `820900825437` is psychology-oriented ("Plan
Comfort With Confidence", "Make an Informed HVAC Choice", "Move Forward Without Guessing"). ✅

**Copy quality (all ads inspected):**

| Check | Result |
|---|---|
| Headline ≤ 30 chars | ✅ all 15 per ad within limit (max observed 30) |
| Description ≤ 90 chars | ✅ all 4 per ad within limit (max observed 89) |
| Pinning | **None** — every asset `pin=UNSPECIFIED` |
| Final URLs | ✅ correct per-service offer page on every ad |
| Display paths | ✅ e.g. `/ac-repair/severn-md`, `/hvac-installers/maryland` |
| Natural English | ✅ no awkward "near me" repetition anywhere in ad copy |
| Invented claims | ✅ none — no price, guarantee, response time, license, rating, or promotion |
| Phone in ad copy | ✅ no phone number hardcoded in headlines/descriptions |
| Campaign/ad-group association | ✅ correct, except the removed AC Repair ad group |

⚠️ **CONSUMER_FINANCE is the blocker.** The likely trigger is purchase/finance-adjacent phrasing
such as *"Plan your HVAC installation with honest, upfront pricing and clear next steps."* and
*"A new HVAC system is a major decision."* This is a common false positive for HVAC advertisers.
It needs an appeal, or a rewrite that removes pricing/финance framing — **not** a silent retry.

### 6.4 Assets

| Asset type | Count per campaign | Status | Verdict |
|---|---|---|---|
| **Call** | 1 (shared asset `407995613637`) | ENABLED / APPROVED | ✅ **phone = `(410)705-6354` — the approved paid number** |
| Callout | 5 | ENABLED / APPROVED | ✅ no unverified claims |
| Sitelink | 5–6 | ENABLED / APPROVED | ⚠️ **all point to the main website** |
| Structured snippet | 1 ("Service catalog") | ENABLED / APPROVED | ✅ service-accurate |
| Image | 0 | — | ⚪ none present |
| Business name / logo | 0 | — | ⚪ none present |
| Automatically created | 0 | — | ✅ correctly off |
| Account-level (inherited) | 0 | — | ✅ none |
| Ad-group-level | 0 | — | ✅ none |

✅ **Call asset confirmed routing to `(410) 705-6354` on all five campaigns.**
⚠️ But `call_conversion_action = ""` and `call_conversion_reporting_state = UNSPECIFIED` — the
call asset has **no explicit call conversion action bound**.

⚠️ **Sitelink destination defect (new finding).** Every sitelink leaves the paid landing page:

| Sitelink | Destination |
|---|---|
| AC Repair Service | `ambientcoolingandheating.com/services/cooling-services/air-conditioner-repair/` |
| Customer Reviews | `ambientcoolingandheating.com/reviews/` |
| View Our Work | `ambientcoolingandheating.com/our-work/` |
| Contact Ambient | `ambientcoolingandheating.com/contact-us/` |
| Service Areas | `ambientcoolingandheating.com/service-areas/` |
| HVAC Services | `ambientcoolingandheating.com/services/hvac/` |
| Heating Services | `ambientcoolingandheating.com/services/heating-services/` |
| AC Installation | `ambientcoolingandheating.com/services/cooling-services/ac-installation/` |
| Boiler Repair | `ambientcoolingandheating.com/services/heating-services/boiler-repair/` |

The main site uses **`(410) 761-0932`** and has no offer form — so sitelink clicks are paid traffic
sent to the **wrong phone number** and away from the conversion path.

---

## 7. Current performance

**Window: 2026-08-14 → 2026-08-17 (launch to date, ~3.5 days).** Network is `SEARCH` for 100% of
delivery — ✅ no Search Partners or Display leakage.

| Campaign | Impr | Clicks | Cost | CTR | Avg CPC | Conv | All conv | Search IS | Lost IS (budget) | Lost IS (rank) | Top IS | Abs top IS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HVAC Repair | 133 | 1 | $20.34 | 0.8% | $20.34 | 0.0 | 0.0 | 13.9% | **0.0%** | **86.1%** | 10.0% | 10.0% |
| AC Repair | 33 | 1 | $2.34 | 3.0% | $2.34 | 0.0 | 0.0 | 10.0% | **0.0%** | **90.0%** | 10.0% | 10.0% |
| HVAC Installation | 12 | 0 | $0.00 | 0.0% | — | 0.0 | 0.0 | 18.2% | **0.0%** | **81.8%** | 13.6% | 10.0% |
| **HVAC Replacement** | **0** | 0 | $0.00 | — | — | 0.0 | 0.0 | — | — | — | — | — |
| **Gas Boiler Repair** | **0** | 0 | $0.00 | — | — | 0.0 | 0.0 | — | — | — | — | — |
| **TOTAL** | **178** | **2** | **$22.68** | **1.1%** | **$11.34** | **0.0** | **0.0** | — | — | — | — | — |

**Other windows:** *Today* — 48 impressions, 0 clicks, $0.00. *Last 7 days* — identical to launch
window. *Last 30 days* — $22.68 account-wide. *Last 365 days* — $73,000 legacy spend, all from
now-paused campaigns.

**Daily series**

| Date | Day | Spend | Clicks | Impressions |
|---|---|---:|---:|---:|
| 2026-08-14 | Friday | $2.34 | 1 | 28 |
| 2026-08-15 | Saturday | $0.00 | 0 | 37 |
| 2026-08-16 | Sunday | **$20.34** | 1 | 65 |
| 2026-08-17 | Monday | $0.00 | 0 | 48 |

**By device:** Desktop 37 impr / 1 click / $20.34 · Mobile 141 impr / 1 click / $2.34.
Mobile draws 79% of impressions — which is exactly why the wrong mobile call CTA matters.

**Keyword level**

| Campaign | Keyword | Match | Impr | Clicks | Cost | Conv | IS | Lost IS (rank) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| HVAC Repair | `hvac repair near me` | PHRASE | 107 | 1 | $20.34 | 0.0 | 12.8% | 87.2% |
| HVAC Repair | `hvac repair near me` | EXACT | 26 | 0 | $0.00 | 0.0 | 16.4% | 83.6% |
| AC Repair | `ac repair near me` | PHRASE | 25 | 1 | $2.34 | 0.0 | 10.0% | 90.0% |
| AC Repair | `ac repair near me` | EXACT | 8 | 0 | $0.00 | 0.0 | 10.0% | 90.0% |
| HVAC Installation | `hvac installers` | PHRASE | 12 | 0 | $0.00 | 0.0 | 18.2% | 81.8% |

### 7.1 Verdict by dimension

- **Configuration health — PASS WITH WARNINGS.** Names, networks, geo method, 75 locations,
  match types, and asset hygiene are right. Bidding, schedules, RSA count, and negatives are wrong.
- **Delivery health — FAIL.** 178 impressions in 3.5 days. Two campaigns have never served.
  **Budget is not the limiter (0.0% lost IS to budget); rank is (82–90%).**
- **Search-intent quality — PASS.** Tight BOFU keywords, no Broad, no informational terms.
- **Tracking reliability — FAIL.** See §9 and §10.
- **Early conversion performance — INSUFFICIENT DATA.** 2 clicks, 0 conversions. No conclusion is
  possible, and none should be drawn from CTR, Ad Strength, or Optimization Score.
- **Profitability — CANNOT BE ASSESSED.** No approved target CPL/CPQL, no qualified-lead data, no
  sold-job revenue or gross profit. **No profitability verdict is offered.**

---

## 8. Budget pacing — both scenarios

Live daily budgets total **$427.64/day**. The build used the standard monthly-average divisor:
`$4,300 ÷ 30.4 = $141.45`, `$2,400 ÷ 30.4 = $78.95`, `$4,200 ÷ 30.4 = $138.16`,
`$800 ÷ 30.4 = $26.32`, `$1,300 ÷ 30.4 = $42.76`. **This is arithmetic evidence that the build
treated $13,000 as an ongoing full-month budget (Scenario 1).**

| Campaign | Plan | Live daily | S1 required (÷31) | S1 variance | S2 required (÷18) | S2 variance |
|---|---:|---:|---:|---:|---:|---:|
| AC Repair | $4,300 | $141.45 | $138.71 | +2.0% | $238.89 | −40.8% |
| HVAC Repair | $2,400 | $78.95 | $77.42 | +2.0% | $133.33 | −40.8% |
| HVAC Installation | $4,200 | $138.16 | $135.48 | +2.0% | $233.33 | −40.8% |
| HVAC Replacement | $800 | $26.32 | $25.81 | +2.0% | $44.44 | −40.8% |
| Gas Boiler Repair | $1,300 | $42.76 | $41.94 | +2.0% | $72.22 | −40.8% |
| **Total** | **$13,000** | **$427.64** | **$419.35** | **+2.0%** | **$722.22** | **−40.8%** |

### Actual pacing — the number that matters

| Metric | Value |
|---|---|
| Spend since launch (Aug 14–17) | **$22.68** |
| Days live | ~3.5 |
| Actual average daily spend | **$5.67** |
| Budget available over the same period | ~$1,497 |
| **Budget actually used** | **≈ 1.5%** |

| Scenario | Required daily | Actual daily | Pace | Projected period-end | Variance from $13,000 |
|---|---:|---:|---:|---:|---:|
| **S1 — full August** | $419.35 | $5.67 | **1.4% of required** | **≈ $102** | **−$12,898 (−99.2%)** |
| **S2 — Aug 14–31** | $722.22 | $5.67 | **0.8% of required** | **≈ $102** | **−$12,898 (−99.2%)** |

**Verdict: catastrophically underspending under both scenarios.** The budget-period question is
therefore *not* the live issue — under either reading the campaigns are delivering ~1% of plan.

- **Budget-limited campaigns: none.** Lost IS (budget) = **0.0%** on every campaign.
- **Lost IS (rank): 81.8%–90.0%** — the true constraint is ad eligibility, Quality Score, and bid.

**Recommended daily distribution — DRAFT ONLY, no budget changed.** Keep the current per-campaign
split; it correctly implements the approved $13,000 monthly allocation. **Do not raise budgets.**
Raising spend before the disapprovals, tracking, and landing pages are fixed would buy untracked
clicks against a Below-Average landing-page experience.

---

## 9. Location targeting inventory

| Check | Result |
|---|---|
| Target count per campaign | ✅ **exactly 75** on all five — matches the approved build |
| Type | All positive `LOCATION` criteria |
| Status | All ENABLED |
| Negative/excluded locations | **0** on all five |
| Targeting method | ✅ `PRESENCE` (positive and negative) — not presence-or-interest |
| Duplicates within a campaign | None detected |
| Unsupported / warning locations | None reported by the API |
| Language criteria | 1 per campaign |
| Device criteria | 3 per campaign, **no bid adjustments set** |

✅ **Location targeting is correct and matches the approved 75-target build.** No location outside
Maryland was detected, and presence-only targeting is properly applied.

---

## 10. Conversion-action inventory

**23 conversion actions — 14 ENABLED, 2 HIDDEN, 7 REMOVED.**

| Name | ID | Type | Category | Status | Primary | Counted | Counting | CTW | VTW |
|---|---|---|---|---|---|---|---|---:|---:|
| Ambient Cooling - LP -Submit Lead Forms | 6885463625 | WEBPAGE | SUBMIT_LEAD_FORM | ENABLED | ✅ | ✅ | ONE_PER_CLICK | 30 | 1 |
| Ambient Cooling - Lp - Phone call leads | 6885576934 | WEBSITE_CALL | PHONE_CALL_LEAD | ENABLED | ✅ | ✅ | ONE_PER_CLICK | 30 | 30 |
| **Call BTN Click** | **6498555484** | **WEBPAGE** | **CONTACT** | ENABLED | ✅ | ✅ | ONE_PER_CLICK | 30 | 1 |
| **Visit Thank you page - Submit Form** | **6498555481** | **WEBPAGE** | SUBMIT_LEAD_FORM | ENABLED | ✅ | ✅ | ONE_PER_CLICK | 30 | 1 |
| Calls from ads | 1068114183 | AD_CALL | PHONE_CALL_LEAD | ENABLED | ✅ | ✅ | ONE_PER_CLICK | 30 | 30 |
| **WC Calls** | **7643656075** | **UPLOAD_CALLS** | CONTACT | ENABLED | ✅ | ✅ | ONE_PER_CLICK | 60 | 30 |
| **WC Lead** | **7643656486** | **UPLOAD_CLICKS** | CONTACT | ENABLED | ✅ | ✅ | ONE_PER_CLICK | 60 | 15 |
| Clicks to call | 6640721230 | GOOGLE_HOSTED | CONTACT | ENABLED | ✅ | ❌ | MANY_PER_CLICK | 30 | 7 |
| ACH (web) form_submission | 7389995485 | GA4_CUSTOM | SUBMIT_LEAD_FORM | ENABLED | ❌ | ❌ | MANY_PER_CLICK | 90 | 1 |
| ACH (web) phone_call_click | 7389995488 | GA4_CUSTOM | PHONE_CALL_LEAD | ENABLED | ❌ | ❌ | MANY_PER_CLICK | 90 | 1 |
| Local actions — Website visits | 6641739327 | GOOGLE_HOSTED | PAGE_VIEW | ENABLED | ✅ | ❌ | MANY_PER_CLICK | 30 | 7 |
| Local actions — Directions | 6642544931 | GOOGLE_HOSTED | GET_DIRECTIONS | ENABLED | ✅ | ❌ | MANY_PER_CLICK | 30 | 7 |
| Local actions — Other engagements | 6642551975 | GOOGLE_HOSTED | ENGAGEMENT | ENABLED | ✅ | ❌ | MANY_PER_CLICK | 30 | 7 |
| Local actions — Menu views | 6954620053 | GOOGLE_HOSTED | PAGE_VIEW | ENABLED | ✅ | ❌ | MANY_PER_CLICK | 30 | 7 |
| ACH (web) form_submit | 6684124701 | GA4_CUSTOM | SUBMIT_LEAD_FORM | HIDDEN | ❌ | ❌ | — | 90 | 1 |
| ACH (web) purchase | 6636693088 | GA4_PURCHASE | PURCHASE | HIDDEN | ❌ | ❌ | — | 90 | 1 |
| Call (14107056354) | 7556624863 | WEBSITE_CALL | PHONE_CALL_LEAD | REMOVED | — | — | — | 30 | 30 |
| Call (14107056354) (1) | 7556783514 | WEBSITE_CALL | PHONE_CALL_LEAD | REMOVED | — | — | — | 30 | 30 |
| `[Nombre del Cliente]` \| Website Phone Call Lead. | 7556469794 | WEBSITE_CALL | PHONE_CALL_LEAD | REMOVED | — | — | — | 30 | 30 |
| `[Nombre del Cliente]` … (1) | 7556640937 | WEBSITE_CALL | PHONE_CALL_LEAD | REMOVED | — | — | — | 30 | 30 |
| `[Nombre del Cliente]` … (2) | 7556793753 | WEBSITE_CALL | PHONE_CALL_LEAD | REMOVED | — | — | — | 30 | 30 |
| ACH Submit lead form | 7556633731 | WEBPAGE | SUBMIT_LEAD_FORM | REMOVED | — | — | — | 90 | 1 |
| ACH \| Submission Lead Form. | 7556736957 | WEBPAGE | SUBMIT_LEAD_FORM | REMOVED | — | — | — | 90 | 1 |

**Attribution:** `GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN` on the website/call actions;
`GOOGLE_ADS_LAST_CLICK` on the Google-hosted local actions.
**Phone duration threshold:** 60s on most; **30s** on `Ambient Cooling - Lp - Phone call leads`.

### 10.1 Account-default and campaign goals

**All five campaigns** carry these **biddable** goals:

| Category | Origin | Biddable |
|---|---|---|
| SUBMIT_LEAD_FORM | WEBSITE | ✅ |
| PHONE_CALL_LEAD | WEBSITE | ✅ |
| **CONTACT** | **WEBSITE** | ✅ ⛔ |
| **CONTACT** | **CALL_FROM_ADS** | ✅ ⛔ |
| PHONE_CALL_LEAD | CALL_FROM_ADS | ✅ |

⛔ **`CONTACT / WEBSITE` is biddable on all five campaigns, and `Call BTN Click` is the action in
that bucket.** A telephone-link click is therefore a biddable conversion goal — exactly what the
brief forbids. It is not a completed call, not a qualified call, and not a lead.

### 10.2 Lead-event taxonomy — what is actually measurable today

| Event type | Tracked? | Evidence |
|---|---|---|
| Telephone-link click | ⛔ **counted as a conversion** via `Call BTN Click` (Primary) | §10.1 |
| Google Ads call-asset call | ✅ `Calls from ads` (AD_CALL, 60s) — but asset has no bound conversion action | §6.4 |
| Website call via Google forwarding number | ⚠️ `Ambient Cooling - Lp - Phone call leads` exists, **but no call script loads on any LP** | §11 |
| Completed call | ⚠️ only via the 60s/30s duration thresholds | — |
| Qualified call | ❌ no disposition or CRM signal | — |
| Form-start / form-button click | ❌ not tracked | — |
| Successful form confirmation | ❌ **no tag on any landing page** | §11 |
| Offline qualified lead | ⚠️ `WC Lead` (UPLOAD_CLICKS) exists; feed unverified | — |
| Sold job | ❌ not tracked | — |

### 10.3 Duplicate and competing conversions

- **Two Primary SUBMIT_LEAD_FORM actions** — `Ambient Cooling - LP -Submit Lead Forms` and
  `Visit Thank you page - Submit Form` — can both count one lead.
- **Three Primary phone-lead actions** — `Calls from ads`, `Ambient Cooling - Lp - Phone call
  leads`, `WC Calls` — can all count one call.
- **`Call BTN Click` + `Clicks to call`** both count tap-to-call behavior.
- **`WC Lead` / `WC Calls` are WhatConverts upload actions, Primary and counted**, although
  WhatConverts is not the platform for this account. They are the cause of the account-level
  `HAS_UPLOAD_CLICKS_CONVERSION` flag.
- **7 REMOVED duplicates**, including three named `[Nombre del Cliente]` — a Spanish-language
  template placeholder ("[Client Name]") that was never customized. Evidence of repeated
  misconfiguration.
- **Latent triple-count risk:** three identical Gravity Form instances per page (§11) mean a naive
  form trigger would fire three times once tagging is restored.

**Suitability for bidding:** none of the current Primary actions is a trustworthy lead signal
today, because **no landing page can fire any of them**.

---

## 11. GTM audit — container `GTM-PQTPQ436` (read-only)

**No tag, trigger, variable, version, or workspace was created, edited, published, paused, or deleted.**

**Access limitation:** no Tag Manager API credential is configured in this project
(`credentials.py` provisions Google Ads scopes only), so the container's internal tag/trigger/
variable list **could not be enumerated**. All browser and source-level checks were completed
instead. The limitation does not change the verdict, because the container never loads.

**Method:** real Chrome (Playwright), desktop 1440×900 and mobile 390×844 @2×, with test query
`?gclid=TESTGCLID12345&gbraid=…&wbraid=…&utm_source=google&utm_medium=cpc&…`. Re-run today after
the first pass. The host runs SiteGround `SG-Captcha`, which serves HTTP 202/403 to non-browser
clients — **the challenge page was not mistaken for the landing page**; all results below come
from fully rendered pages.

| Check | Expected | Observed (all 5 pages, both viewports) | Result |
|---|---|---|---|
| GTM script once near top of `<head>` | present | **absent** | ⛔ FAIL |
| Noscript iframe once after `<body>` | present | **absent — zero `<noscript>` blocks** | ⛔ FAIL |
| Browser requests `gtm.js?id=GTM-PQTPQ436` | yes | **0 requests to googletagmanager.com** | ⛔ FAIL |
| `dataLayer` initializes | yes | `Array.isArray(dataLayer) === false`, length 0 | ⛔ FAIL |
| Correct container on every landing page | yes | **no container on any page** | ⛔ FAIL |
| No duplicate containers | pass | ✅ vacuously (zero containers) | ⚪ N/A |
| No conflicting hardcoded Google tags | pass | ✅ no `AW-`, `G-`, or `UA-` anywhere | ✅ |
| Google tag / configuration tag | present | absent | ⛔ FAIL |
| Google Ads Conversion Linker | present | absent | ⛔ FAIL |
| Form conversion tag | present | absent | ⛔ FAIL |
| Call / click-to-call tag | present | absent | ⛔ FAIL |
| Correct conversion IDs and labels | present | absent | ⛔ FAIL |
| Consent Mode signals | present | absent | ⛔ FAIL |
| Enhanced Conversions | configured | absent | ⛔ FAIL |
| Deduplication / lead ID | defined | absent | ⛔ FAIL |
| Cross-domain configuration | configured | absent | ⛔ FAIL |
| GCLID / GBRAID / WBRAID / UTM persistence | captured | **not captured** — all 7 hidden fields empty | ⛔ FAIL |

**Only third-party hosts requested:** `fonts.googleapis.com`, `fonts.gstatic.com`. **29 external
scripts load per page** — all first-party WordPress, Divi 5.10.1, Gravity Forms 3.0.2, and the
`dynamic-offer-countdown` plugin. **Not one analytics or advertising tag.**

### Root cause

| Property | `GTM-PQTPQ436` in HTML | Container initialized | Phone used |
|---|---|---|---|
| `ambientcoolingandheating.com` (main site) | ✅ **yes** (also `G-9X9ZHNCRWF`) | no | `(410) 761-0932` |
| `offer.ambientcoolingandheating.com` (all 5 paid pages) | ❌ **no** | no | `(410) 705-6354` + wrong number |

The container was deployed to the main site and **never to the offer subdomain**. The offer
subdomain is a separate WordPress install that inherited none of it.

**Retest classification: ⛔ CONFIRMED** — and stated more precisely than before: the container is
not merely failing to load, it is **not installed at all** on the offer subdomain. This is a
deployment task, not a debugging task.

### Gravity Forms trigger requirement

Forms post back to the same URL (`method="post"`, `action="/ac-repair/"`,
`gform_submission_method=postback`). **There is no separate thank-you URL**, so a URL-based
trigger is unavailable. Confirmation renders inline. The form conversion must key on a confirmed
successful submission (`gform_confirmation_loaded` or equivalent) **plus a unique entry ID**, and
must not fire from page load, form visibility, CTA click, submit-button click, validation error, a
duplicate form instance, or a thank-you reload. **No form was submitted during this audit.**

**WhatConverts absence is not reported as a failure**, per instruction.

---

## 12. Landing-page audit — all five URLs

| Check | ac-repair | hvac-repair | hvac-installation | hvac-replacement | gas-boiler-repair |
|---|---|---|---|---|---|
| HTTP (browser) | 200 | 200 | 200 | 200 | 200 |
| Redirect chain | none | none | none | none | none |
| HTTPS / cert | ✅ | ✅ | ✅ | ✅ | ✅ |
| Canonical self-referencing | ✅ | ✅ | ✅ | ✅ | ✅ |
| `robots` | noindex,nofollow ✅ | ✅ | ✅ | ✅ | ✅ |
| Title | ✅ | ✅ | ✅ | ✅ | ✅ |
| H1 service-specific | ✅ | ✅ | ✅ | ✅ | ✅ |
| Keyword/ad/LP alignment | ✅ | ⚠️ | ✅ | ✅ | ⚠️ |
| Location claims | ✅ consistent | ✅ | ✅ | ✅ | ✅ |
| Offer accuracy | ✅ free quote only | ✅ | ✅ | ✅ | ✅ |
| **GTM loads** | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ |
| **Attribution fields** | ⛔ empty | ⛔ | ⛔ | ⛔ | ⛔ |
| **Wrong `tel:` present** | ⛔ 2× | ⛔ 2× | ⛔ 2× | ⛔ 1× | ⛔ 1× |
| Privacy Policy link | ⛔ none | ⛔ | ⛔ | ⛔ | ⛔ |
| Terms link | ⛔ none | ⛔ | ⛔ | ⛔ | ⛔ |
| Gravity Form copies | ⛔ 3 | ⛔ 3 | ⛔ 3 | ⛔ 3 | ⛔ 3 |
| Duplicate DOM IDs | ⛔ 34 | ⛔ 34 | ⛔ 34 | ⛔ 34 | ⛔ 34 |
| Phone placeholder | ⛔ `(712) 555-0123` | ⛔ | ⛔ | ⛔ | ⛔ |
| Textarea optional/required | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ |
| Countdown vs copy | ⚠️ | ⚠️ | ⛔ | ⛔ | ⛔ |
| Pinch-to-zoom | ⛔ disabled | ⛔ | ⛔ | ⛔ | ⛔ |
| Structured data | ⛔ 0 blocks | ⛔ | ⛔ | ⛔ | ⛔ |
| Broken images | ✅ 0 | ✅ 0 | ✅ 0 | ✅ 0 | ✅ 0 |
| Desktop layout | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mobile layout | ⚠️ CTA overlap | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Form visible/usable | ✅ | ✅ | ✅ | ✅ | ✅ |

**Page speed** (all well within target): TTFB 76–280 ms, DOMContentLoaded 378–671 ms, Load
430–785 ms, FCP 332–660 ms, 63–64 requests.

**TLS:** Let's Encrypt (`YR1`), TLS 1.3, valid `2026-08-13` → **`2026-11-11`** (86 days).

**Form fields** (identical on all five): honeypot `input_16` ✅ (correct, not a defect);
`input_1` Full Name required; `input_4` Phone required with placeholder **`(712) 555-0123`**;
`input_3` Email required; `input_7` textarea labelled **"Tell us about your project (optional)\*"**
but `aria-required="true"`; `input_9`–`input_15` seven hidden attribution fields, **all empty**.

**Countdown:** `data-deadline="2026-08-31T23:59:59+00:00"` — set in **UTC**, so it expires
2026-08-31 **7:59:59 PM Eastern**, four hours early. Timer renders "14 DAY" while copy on three
pages says "before today ends".

**Content and claims:** ✅ **no invented claims** — no price, dollar amount, percentage discount,
guarantee, "24/7", "same-day", "licensed", "insured", "certified", years in business, star rating,
or review count. The only offer is a free quote, consistently worded.

**Accessibility:** alt text present and descriptive; countdown has `aria-live="polite"`; but
pinch-to-zoom is disabled (WCAG 2.1 SC 1.4.4 failure), 34 duplicate IDs break `label[for]`
association, and the textarea's optional/required contradiction misleads screen readers.

### 12.1 Independent retest of the 15 prior findings

| # | Finding | Verdict | Evidence |
|---|---|---|---|
| 1 | Mobile `Call Now` → `+14107610932` | ⛔ **CONFIRMED** | All 5 pages; desktop 0×0, **mobile 175×37 visible** |
| 2 | Wrong number in FAQ copy | ⛔ **CONFIRMED** | ac-repair, hvac-repair, hvac-installation |
| 3 | GTM-PQTPQ436 absent from offer subdomain | ⛔ **CONFIRMED** | 0 requests, no container, no ID in HTML |
| 4 | Attribution fields empty | ⛔ **CONFIRMED** | 7 hidden fields empty with full test query string |
| 5 | No Privacy Policy or Terms links | ⛔ **CONFIRMED** | Zero matching links on all 5 |
| 6 | Three copies of Gravity Form 1 | ⛔ **CONFIRMED** | `gform_wrapper_1` ×3 on all 5 |
| 7 | Duplicate DOM IDs | ⛔ **CONFIRMED** | 34 IDs × 3 occurrences |
| 8 | Phone placeholder `(712) 555-0123` | ⛔ **CONFIRMED** | 3× per page |
| 9 | Textarea optional but required | ⛔ **CONFIRMED** | label "(optional)\*", `aria-required="true"` |
| 10 | Countdown vs "before today ends" | ⛔ **CONFIRMED** | deadline 2026-08-31; copy on 3 of 5 pages |
| 11 | HVAC Repair says "Recent AC Repair Work" | ⛔ **CONFIRMED** | exact H2 on hvac-repair |
| 12 | Gas Boiler says "Your HVAC Replacement in 3 Simple Steps" | ⛔ **CONFIRMED** | exact H2 on gas-boiler-repair |
| 13 | Pinch-to-zoom disabled | ⛔ **CONFIRMED** | `maximum-scale=1.0, user-scalable=0` |
| 14 | "Recent Work" image provenance | ⚪ **BLOCKED** | Not verifiable from public sources |
| 15 | `410-914-8446` | ✅ **NOT REPRODUCED** | Absent from all rendered HTML |

**Nothing has been fixed since the first pass.** Two additional defects found earlier remain: the
FAQ number leak (#2) and the UTC countdown deadline.

---

## 13. Phone-number consistency

**Approved paid number: `(410) 705-6354` / `+14107056354` / `tel:+14107056354`**

| Surface | Value | Verdict |
|---|---|---|
| **Google Ads call asset** (`407995613637`, all 5 campaigns) | `(410)705-6354` | ✅ **correct** |
| LP header CTA | `tel:4107056354` | ⚠️ right number, **non-E.164** |
| LP hero CTA | `tel:(410) 705-6354` | ⚠️ right number, **malformed href** |
| **LP mobile "Call Now" button** | **`tel:+14107610932`** | ⛔ **WRONG — P0** |
| **LP FAQ body copy** (3 pages) | **`(410) 761-0932`** | ⛔ **WRONG — P0** |
| LP visible text | `(410) 705-6354` ×3 per page | ✅ |
| **Sitelink destinations** (9 assets) | main site → `(410) 761-0932` | ⛔ **paid clicks land on the wrong number** |
| Schema / structured data | *no structured data exists* | ⚪ N/A |
| Form confirmation | inline postback, no phone shown | ⚪ |
| Main website | `(410) 761-0932` | ✅ **correct by design** |

**Wrong-number scan across full rendered HTML**

| Number | ac-repair | hvac-repair | hvac-install | hvac-replace | gas-boiler |
|---|---|---|---|---|---|
| `410-761-0932` / `+14107610932` | ⛔ 2× | ⛔ 2× | ⛔ 2× | ⛔ 1× | ⛔ 1× |
| `410-914-8446` / `+14109148446` | ✅ absent | ✅ | ✅ | ✅ | ✅ |
| `(712) 555-0123` | ⛔ 3× | ⛔ 3× | ⛔ 3× | ⛔ 3× | ⛔ 3× |
| Any other number | ✅ none | ✅ | ✅ | ✅ | ✅ |

---

## 14. Historical search-term analysis

**Corpus:** 13,118 distinct search terms across launch-to-date, last 30, last 90, last 365, and the
prior 365 days — spanning current, paused, and historical campaigns. **$65,352.20** of analyzed
spend, **5,238 clicks**, **105 conversions**.

Per project convention the full term-level evidence table is written to disk; non-service terms are
reported here as counts per reason rather than dumped as strings.

| Verdict | Terms | Clicks | Click % | Cost | Cost % | Conversions |
|---|---:|---:|---:|---:|---:|---:|
| **KEEP** | 843 | 3,747 | 71.5% | $37,746.88 | 57.8% | 68.0 |
| **WATCH** | 9,777 | 911 | 17.4% | $14,938.79 | 22.9% | 30.0 |
| **NEGATIVE** | 2,498 | 580 | 11.1% | $12,666.53 | 19.4% | 7.0 → **0 after Rule 1** |

> **Safety Rule 1:** a term that ever converted is **never** proposed as a negative. Terms with
> conversions were moved out of NEGATIVE into KEEP before the package was built.

### NEGATIVE candidates by reason

| Reason | Terms | Clicks | Wasted spend |
|---|---:|---:|---:|
| no_hvac_service_signal | 320 | 297 | $6,795.50 |
| cross_service_water_heater | 1,476 | 246 | $4,950.43 |
| cross_service_duct_cleaning_or_iaq | 213 | 17 | $484.87 |
| parts_supplies_or_purchase | 142 | 6 | $158.34 |
| vehicle_ac | 13 | 3 | $83.76 |
| diy_or_troubleshooting | 101 | 4 | $68.48 |
| out_of_area | 20 | 1 | $51.26 |
| window_or_portable_unit | 91 | 2 | $26.53 |
| other_trade | 40 | 1 | $24.34 |
| cross_service_maintenance_or_tuneup | 34 | 3 | $23.02 |
| appliance_or_refrigeration | 31 | 0 | $0.00 |
| directory_or_review_research | 5 | 0 | $0.00 |
| employment_or_training | 5 | 0 | $0.00 |
| rental_or_temporary / assistance_grant / brand_research | 7 | 0 | $0.00 |

### KEEP demand by campaign theme — the demand to protect

| Theme | Terms | Clicks | Cost | Conversions |
|---|---:|---:|---:|---:|
| AC Repair | 167 | 697 | $5,608.22 | 14.0 |
| HVAC Repair | 71 | 387 | $2,933.73 | 6.0 |
| HVAC Installation | 83 | 235 | $1,691.33 | 1.0 |
| HVAC Replacement | 40 | 50 | $1,323.31 | 2.0 |
| Gas Boiler Repair | 41 | 48 | $4,528.15 | 9.0 |
| Other Ambient services | 441 | 2,330 | $21,662.14 | 36.0 |

**84 terms converted** (792 clicks, $19,743.18, 105 conversions). All are protected from
negativing. Note the largest converting block sits in **other Ambient services** — water heaters,
heating, mini split, geothermal — which is exactly why those become **campaign-level** negatives on
the five new campaigns and **never** account-level.

### WATCH by reason

| Reason | Terms | Clicks | Cost |
|---|---:|---:|---:|
| core_service_without_clear_buy_intent | 573 | 771 | $11,711.94 |
| protected_term_blocks_auto_negative | 355 | 135 | $3,156.85 |
| protected_term_present_diy_or_troubleshooting | 36 | 3 | $68.41 |
| core_service_no_buy_signal_negligible_traffic | 4,323 | 0 | $0.00 |
| non_service_negligible_traffic | 2,635 | 0 | $0.00 |
| core_service_bofu_negligible_traffic | 1,822 | 0 | $0.00 |
| others | 33 | 2 | $1.59 |

**355 terms carrying a policy-protected word** (`near me`, `quote`, `price`, `pricing`, `cost`,
`best`, `hire`, `local`, `emergency`) were held in WATCH and **never auto-negatived**.

**Search terms since launch:** 62 rows on 178 impressions — too few to classify meaningfully. All
historical intelligence above comes from the paused legacy campaigns.

---

## 15. Existing negative-list audit

**16 negative lists + 1 brand list. None is attached to any of the five new campaigns.**

Conflict-tested by applying Google's negative-matching rules against the five approved keywords and
realistic BOFU variations.

| List | ID | Members | Match types | Attached to | Verdict |
|---|---|---:|---|---:|---|
| **General List** | 11813144900 | 1,111 | BROAD 1109, EXACT 2 | 1 | ⛔ **DO NOT REUSE** |
| **Ambient - Neg Kwd List** | 12091293463 | 968 | BROAD 929, PHRASE 29, EXACT 10 | 18 | ⛔ **DO NOT REUSE** |
| **General** | 10720232972 | 1,148 | PHRASE 697, EXACT 449, BROAD 2 | 11 | ⛔ **DO NOT REUSE** |
| **General List - Irrigation Repair** | 12178646912 | 1,107 | BROAD 1105, EXACT 2 | 0 | ⛔ **DO NOT REUSE** |
| Names | 10667314427 | 436 | PHRASE | 0 | ⛔ DO NOT REUSE (REMOVED) |
| account-level negative keywords list | 11252984411 | 59 | BROAD | — | ⚠️ contains BROAD `commercial` |
| **States List** | 10664309518 | 48 | PHRASE | 11 | ✅ **SAFE TO REUSE** |
| **Names List** | 10664304544 | 486 | PHRASE | 11 | ✅ **SAFE TO REUSE** |
| **GM \| Broad Poison** | 12021721179 | 5 | BROAD | 9 | ✅ **SAFE TO REUSE** |
| **GM \| Phrase Blockers** | 12021722439 | 6 | PHRASE | 9 | ✅ **SAFE TO REUSE** |
| **GM \| Competitor Name Tokens** | 12022987128 | 17 | BROAD | 9 | ✅ **SAFE TO REUSE** |
| **GM \| Competitor Brands** | 12025671131 | 17 | PHRASE | 9 | ✅ **SAFE TO REUSE** |
| Christmas Lights Install | 11807294063 | 424 | mixed | 0 | ⛔ **DO NOT REUSE — wrong vertical** |
| Leaf Removal initial | 11811255121 | 386 | BROAD | 0 | ⛔ **DO NOT REUSE — wrong vertical** |
| Paver | 11840874961 | 387 | BROAD | 0 | ⛔ **DO NOT REUSE — wrong vertical** |
| Outdoor Kitchen | 11840890006 | 386 | BROAD | 0 | ⛔ **DO NOT REUSE — wrong vertical** |
| Exclusion Brand List | 11646241995 | 24 | — | 0 | ⚪ N/A (BRANDS type) |

> The four landscaping/hardscaping lists pass the mechanical conflict test but fail the relevance
> requirement — their intent has nothing to do with HVAC. Reusing them would add ~1,580 unrelated
> negatives with no evidence. **Do not attach them.**

### Why the four big lists are unsafe

| List | Blocking negative | Blocks |
|---|---|---|
| **General List** | BROAD **`repair`** and **`Repair`** | Every repair query — `ac repair near me`, `hvac repair near me`, `gas boiler repair`, `hvac repair maryland`, … |
| **General List** | BROAD `cost`, `emergency`, `best`, `hire` | `ac repair cost`, `emergency ac repair near me`, `best hvac repair near me`, `hire hvac contractor` |
| **Ambient - Neg Kwd List** | BROAD **`severn`**, BROAD **`arundel`** | **Ambient's own service area** — `ac repair severn md`, `gas boiler repair anne arundel` |
| **Ambient - Neg Kwd List** | BROAD `quote` | `ac repair quote`, `hvac installation quote` |
| **Ambient - Neg Kwd List** | EXACT `hvac`, EXACT `furnace` | risky single-word negatives |
| **General** | PHRASE `hire` | `hire hvac contractor` |
| **General List - Irrigation Repair** | BROAD `cost`, `emergency`, `best`, `hire` | protected commercial terms |
| account-level list | BROAD `commercial` | `commercial hvac repair` |

⚠️ **`Ambient - Neg Kwd List` is attached to 18 legacy campaigns and blocks `severn` — one of
Ambient's three service cities.** All those campaigns are paused, so nothing is being blocked right
now, but the list must be cleaned before any reuse.

✅ **`States List` correctly excludes 48 states and does NOT contain Maryland or MD** — genuinely
reusable for geo hygiene.

✅ The four GM lists are small, HVAC-appropriate, and safe:
`GM | Broad Poison` = calculator, careers, certification, engineer, technicians ·
`GM | Phrase Blockers` = duct sealing, ductwork sealing, hvac work, warranty registration, water
heater(s) · `GM | Competitor Name Tokens` / `GM | Competitor Brands` = competitor terms.

---

## 16. Negative-keyword approval package — **REQUIRES APPROVAL**

**PLAN FINGERPRINT: `12E7572A25B9AFF0`**
**Nothing has been applied. This is a proposal only.**

### Conflict testing performed

Every proposed negative was tested with Google's negative-matching rules against a scope-appropriate
protected set:

| Scope | Protected set | Size |
|---|---|---|
| A — universal shared list | 5 approved keywords + **all** converting terms + all KEEP terms in the five themes | 462 queries |
| B — cross-service, campaign level | 5 approved keywords + converting terms within the five themes | 27 queries |
| C — cross-campaign, per campaign | that campaign's own approved keyword + its own converting terms | per campaign |

**Result: 0 proposed negatives conflict.** Every candidate that would have blocked protected demand
was dropped before this package was produced. Policy-protected commercial terms and unsafe single
words were excluded by rule, never by judgment.

### Package contents

| Group | Purpose | Items | Destination |
|---|---|---:|---|
| **A** | Universal irrelevant themes | **119** | **NEW shared list** `GM \| Ambient HVAC \| Universal Negatives` |
| **B** | Cross-service (services Ambient offers elsewhere) | **15** | **Campaign level**, all five new campaigns |
| **C** | Cross-campaign separation between the five | **30** | **Campaign level**, per campaign |
| **D** | Term-specific EXACT negatives from evidence | **150** | Same new shared list |
| **E** | Competitor terms — manual review | 13 | **No action proposed** |
| **F** | WATCH — insufficient evidence | 60 | **No action proposed** |

**Expected object count**

| Item | Count |
|---|---:|
| New shared-list members (A + D) | **269** |
| Campaign-level cross-service negatives (B × 5 campaigns) | **75** |
| Campaign-level cross-campaign negatives (C) | **30** |
| **Total mutations if approved** | **374** |
| New shared lists to create | 1 |
| Shared-list ↔ campaign associations to create | 5 |
| Dropped by conflict test | 0 |
| Terms already covered by a broader proposed negative | 166 |
| Directly evidenced wasted spend addressed by Group D | **$6,137.52** |

### Group A — universal shared list (119 PHRASE negatives)

Themes and representative members:

| Theme | Examples |
|---|---|
| Employment / training (21) | `hvac jobs`, `hvac salary`, `hvac apprentice`, `hvac school`, `hvac certification`, `epa 608`, `trade school`, `indeed` |
| DIY / troubleshooting (14) | `how to`, `diy`, `troubleshooting`, `error code`, `wiring diagram`, `owners manual`, `youtube`, `reddit` |
| Parts / purchase (14) | `home depot`, `lowes`, `amazon`, `wholesale`, `for sale`, `replacement parts`, `air filter`, `capacitor` |
| Vehicle AC (9) | `car ac`, `auto ac`, `truck ac`, `ac recharge`, `rv ac` |
| Appliance / refrigeration (10) | `refrigerator`, `freezer`, `washer`, `dishwasher`, `appliance repair` |
| Window / portable units (7) | `window ac`, `portable ac`, `swamp cooler`, `space heater` |
| Assistance / grants (9) | `free furnace`, `free hvac`, `low income`, `weatherization`, `liheap` |
| Other trades (10) | `plumber`, `plumbing`, `electrician`, `roofing`, `garage door`, `septic` |
| Directories (7) | `yelp`, `angi`, `thumbtack`, `homeadvisor`, `craigslist` |
| Out of area (12) | `texas`, `california`, `florida`, `chicago`, `houston`, `phoenix` |
| Tenant / landlord (3), rental (3) | `tenant`, `landlord`, `rental` |

### Group B — cross-service, campaign level on all five (15 PHRASE)

`water heater`, `water heaters`, `tankless water`, `hot water tank`, `duct cleaning`,
`air duct cleaning`, `dryer vent`, `air purifier`, `uv light`, `dehumidifier`, `humidifier`,
`tune up`, `tuneup`, `maintenance plan`, `geothermal`

⚠️ **These are services Ambient genuinely offers** (Tankless Water Heaters, Air Quality, Pool Room
Dehumidifier, Heating Maintenance, Geothermal — all paused campaigns). They must be applied at
**campaign level on the five new campaigns only**, never account-level and never to a shared list
used by the legacy campaigns. Their purpose is routing, not exclusion.

### Group C — cross-campaign separation (30 PHRASE, per campaign)

| Campaign | Negatives added |
|---|---|
| AC Repair | `hvac installation`, `hvac installers`, `hvac replacement`, `gas boiler`, `boiler repair`, `ac replacement`, `ac installation`, `new ac unit` |
| HVAC Repair | `hvac installation`, `hvac installers`, `hvac replacement`, `gas boiler`, `boiler repair`, `new hvac system` |
| HVAC Installation | `hvac repair`, `ac repair`, `boiler repair`, `gas boiler repair` |
| HVAC Replacement | `hvac repair`, `ac repair`, `boiler repair`, `gas boiler repair` |
| Gas Boiler Repair | `ac repair`, `air conditioner`, `hvac installation`, `hvac installers`, `hvac replacement`, `boiler installation`, `boiler replacement`, `new boiler` |

Each was tested only against its **own** campaign's approved keyword and converting demand, so no
campaign is prevented from serving its own theme.

### Group D — 150 term-specific EXACT negatives

Drawn from the highest-waste evidenced terms with zero conversions, excluding anything already
covered by a Group A/B/C negative. EXACT match confines each to the precise query observed.

### Group E — competitor terms (13) — **manual review, no action proposed**

Competitor-name queries surfaced in history. Bidding on competitor terms is a business decision,
not a technical one. **Recommendation: leave them out of the five BOFU campaigns**; if Green
Marketing wants competitor coverage, it belongs in a separate campaign with its own budget.

### Group F — WATCH (60) — **no action proposed**

Terms with ≥ $25 spend and zero conversions that carry a policy-protected word or a genuine service
signal. **Recommendation: revisit after 30 days of clean tracking.** Negativing them now would risk
blocking real demand on pre-tracking data.

### Post-approval readback plan

After explicit approval tied to `12E7572A25B9AFF0`, apply only the approved terms, then read back
via API and confirm: every approved negative exists with the correct match type; list associations
are correct on exactly the five campaigns; no unapproved negative was added; **no approved keyword
or converting term is blocked**; and no unrelated campaign changed.

---

## 17. Findings ranked

### P0 — lead loss, unmeasured spend, wrong phone, wrong account, uncontrolled spend

| ID | Finding | Evidence |
|---|---|---|
| **P0-1** | **No conversion tracking on any landing page.** No GTM, gtag, dataLayer, or Google ID. | §11 |
| **P0-2** | **Mobile "Call Now" CTA dials `+14107610932`** on all 5 pages — hidden on desktop, visible on mobile (79% of impressions). | §12.1, §13 |
| **P0-3** | **Wrong number in FAQ copy** on 3 pages. | §13 |
| **P0-4** | **Six RSAs DISAPPROVED (CONSUMER_FINANCE)** → 3 campaigns `NOT_ELIGIBLE`; 2 have **zero** impressions since launch. | §6.3 |
| **P0-5** | **Attribution fields never populate** — 7 hidden fields empty with gclid/gbraid/wbraid/UTMs present. | §12 |
| **P0-6** | **A telephone-link click is a biddable conversion goal** (`Call BTN Click`, CONTACT/WEBSITE biddable on all 5). | §10.1 |

### P1 — major targeting, conversion, policy, budget, or landing-page problems

| ID | Finding | Evidence |
|---|---|---|
| **P1-1** | **Spend is 1.5% of available budget**; lost IS to rank 82–90%, to budget 0.0%; QS 2/10 with Below-Average LP experience. | §7, §8 |
| **P1-2** | **Bidding is Maximize Clicks (`TARGET_SPEND`)**, not conversion-based, for a lead-gen goal. | §5.1 |
| **P1-3** | **Duplicated/unapproved ad schedules** (Mon–Fri 8–16 *and* 8–20, plus Saturday); added today, so Aug 14–17 ran unscheduled — 114 impressions and the $20.34 click landed outside any window. | §5.2 |
| **P1-4** | **Five campaigns launched with zero negatives** of any kind. | §15 |
| **P1-5** | **Four existing negative lists are dangerous** — BROAD `repair`; `severn`/`arundel` block Ambient's own service area. | §15 |
| **P1-6** | **All sitelinks send paid clicks to the main website**, which shows the wrong phone number and has no form. | §6.4, §13 |
| **P1-7** | **ClickCease redirect on every click** with zero tags on the destination; click-ID preservation unverified. | §4.3 |
| **P1-8** | **No Privacy Policy or Terms link** on any lead-capture page. | §12 |
| **P1-9** | **Three identical Gravity Form instances per page** → 34 duplicate DOM IDs; latent triple-count risk. | §12 |
| **P1-10** | **Competing conversion actions** — 2 Primary form actions, 3 Primary phone actions, 2 Primary WhatConverts uploads. | §10.3 |
| **P1-11** | **~4 RSAs per ad group instead of 2**, two generations coexisting. | §6.3 |
| **P1-12** | **Cross-service headings** — "Recent AC Repair Work" on HVAC Repair; "Your HVAC Replacement in 3 Simple Steps" on Gas Boiler Repair. | §12.1 |
| **P1-13** | **Countdown contradicts copy**, and its deadline is in **UTC** (expires 4 hours early). | §12 |
| **P1-14** | **Phone placeholder `(712) 555-0123`** on all five forms. | §12 |
| **P1-15** | **Textarea labelled "(optional)" but required.** | §12 |
| **P1-16** | **`OLD Ambient C&H` (2391758435) still ENABLED** — needs its own gated review. | §3.2 |
| **P1-17** | **Second ACTIVE manager link `2815082755`** on the child account — confirm expected. | §3.1 |

### P2 — optimization, CRO, copy, accessibility, cleanup

| ID | Finding |
|---|---|
| **P2-1** | Pinch-to-zoom disabled — WCAG 2.1 SC 1.4.4 failure. |
| **P2-2** | Non-canonical `tel:` hrefs on the two correct CTAs. |
| **P2-3** | Mobile CTA overlap (yellow and green buttons collide). |
| **P2-4** | No structured data on any page (0 JSON-LD blocks). |
| **P2-5** | "Recent Work" image provenance unproven. |
| **P2-6** | TLS certificate expires 2026-11-11 (86 days) — confirm auto-renewal. |
| **P2-7** | SG-Captcha serves 202/403 to non-browser clients — naive monitors will misreport uptime. |
| **P2-8** | Main-site GTM container also fails to initialize despite the ID being present. |
| **P2-9** | Rogue REMOVED ad group `SKAG \| HVAC Replacement Near Me` and duplicate `hvac replacement near me` keywords inside the AC Repair campaign. |
| **P2-10** | Call asset has no bound `call_conversion_action`. |
| **P2-11** | No RSA pinning anywhere — consider pinning one brand/service headline per ad. |
| **P2-12** | 7 REMOVED duplicate conversion actions, three named `[Nombre del Cliente]`. |
| **P2-13** | 4 landscaping/hardscaping negative lists sit unused in an HVAC account. |

---

## 18. Exact recommended fix for every failure

**P0-1 — Deploy `GTM-PQTPQ436` to the offer subdomain.** Add the standard snippet to `<head>` and
the noscript iframe immediately after `<body>` (exact code as supplied in the brief). Then configure
in-container: Google tag / configuration tag, Conversion Linker, a form conversion keyed to a
**confirmed** Gravity Forms submission with a unique entry ID, a call conversion, Consent Mode v2
defaults, and cross-domain linking between `ambientcoolingandheating.com` and
`offer.ambientcoolingandheating.com`.

**P0-2 — Fix the mobile call button.** On all five pages change `et_pb_button_5`
`href="tel:+14107610932"` → **`href="tel:+14107056354"`**, and relabel to
`Call Now: (410) 705-6354`.

**P0-3 — Fix FAQ copy** on ac-repair, hvac-repair, hvac-installation: `(410) 761-0932` →
**`(410) 705-6354`**.

**P0-4 — Resolve the CONSUMER_FINANCE disapprovals.** Review the six disapproved RSAs
(`820900825434`, `820900825437`, `820944944368`, `820944944371`, `820900825428`, `820900825431`).
Remove purchase/finance framing — e.g. "honest, upfront pricing", "A new HVAC system is a major
decision" — and resubmit, or file a policy appeal. **Do not silently recreate the ads.**

**P0-5 — Populate attribution fields.** Enable dynamic population on `input_9`–`input_15` in
Gravity Forms bound to `gclid`, `gbraid`, `wbraid`, `utm_source`, `utm_medium`, `utm_campaign`,
`utm_term`; add a first-party cookie so the click ID survives the ClickCease redirect.

**P0-6 — Remove the tel-click goal from bidding.** Set `Call BTN Click` (6498555484) to
**Secondary** (observation only) and remove **CONTACT / WEBSITE** from the biddable goal set on all
five campaigns. A tap is not a call.

**P1-1 / P1-2 — Sequence correctly.** Leave bidding on Maximize Clicks until tracking is verified,
then switch to Maximize Conversions. **Do not raise budgets** — budget is not the constraint.
Quality Score recovery follows the landing-page fixes.

**P1-3 — Remove the duplicate Mon–Fri 08:00–20:00 schedule rows and the Saturday row**, leaving
only the approved Mon–Fri 08:00–16:00 — or obtain written approval for the wider window.

**P1-4 / P1-5 — Apply the §16 package** after approval. **Do not attach any existing list.** Clean
`Ambient - Neg Kwd List` (remove BROAD `severn`, `arundel`, `quote`; EXACT `hvac`, `furnace`) and
`General List` (remove BROAD `repair`/`Repair`) before they are reused anywhere.

**P1-6 — Repoint sitelinks** to the relevant offer pages, or create offer-subdomain equivalents. No
paid click should land on a page showing `(410) 761-0932`.

**P1-7 — Verify the ClickCease redirect preserves `gclid`/`gbraid`/`wbraid`.** If not, reconfigure
or remove it.

**P1-8** — Add Privacy Policy and Terms links to all five page footers.
**P1-9** — Remove the two duplicate Gravity Form instances per page.
**P1-10** — Pick one Primary form action and one Primary phone action; set the rest to Secondary.
Disable `WC Lead` / `WC Calls` unless WhatConverts is genuinely in use.
**P1-11** — Remove the older RSA generation, leaving exactly two per ad group.
**P1-12** — "Recent HVAC Repair Work"; "Your Gas Boiler Repair in 3 Simple Steps".
**P1-13** — Set `data-deadline="2026-08-31T23:59:59-04:00"` and align the copy, or make it a true
end-of-day timer. Do not display a false deadline.
**P1-14** — Replace the placeholder with `Phone number` or `(___) ___-____`.
**P1-15** — Make `input_7` genuinely optional (recommended) or remove "(optional)" from the label.
**P1-16** — Review `OLD Ambient C&H` under its own work order and identity gate.
**P1-17** — Confirm manager link `2815082755` is expected; remove it if not.

**P2** — Remove `maximum-scale=1.0, user-scalable=0`; normalize both correct CTAs to
`tel:+14107056354`; fix mobile button spacing; add LocalBusiness/HVACBusiness JSON-LD with
`telephone: "+1-410-705-6354"` using verified NAP only; obtain written confirmation of the "Recent
Work" photos; confirm TLS auto-renewal; allowlist monitoring agents; investigate main-site GTM;
delete the rogue REMOVED ad group and the duplicate `hvac replacement near me` keywords from the AC
Repair campaign; bind a call conversion action to the call asset; consider pinning one headline per
RSA; delete the 7 REMOVED duplicate conversion actions; archive the 4 landscaping lists.

---

## 19. Proposed change plan — **REQUIRES APPROVAL BEFORE IMPLEMENTATION**

**Nothing below has been done.** Each phase needs its own explicit approval; the negative package
additionally requires approval tied to fingerprint `12E7572A25B9AFF0`.

### Phase 1 — Stop the bleeding (external writes)
1. Fix the wrong phone number: mobile CTA + FAQ copy (P0-2, P0-3).
2. Deploy GTM to the offer subdomain and configure conversion tags (P0-1).
3. Populate attribution fields (P0-5).
4. Demote the tel-click conversion goal (P0-6).
5. Resolve the six CONSUMER_FINANCE disapprovals (P0-4).

> **Budget consideration.** The campaigns are spending only ~$5.67/day, so runaway spend is not a
> risk. Pausing is **not** recommended right now — the greater risk is that the disapprovals and
> tracking gap persist. **Pausing or enabling anything remains an external write requiring your
> explicit approval; I have changed nothing.**

### Phase 2 — Negative keywords (external writes; fingerprint-gated)
Create the shared list, add 269 members, attach to the five campaigns, add 75 cross-service and 30
cross-campaign negatives. **374 mutations.** Then API readback per §16.

### Phase 3 — Configuration corrections (external writes)
Remove duplicate ad schedules; remove the older RSA generation; repoint sitelinks; clean the rogue
ad group and duplicate keywords; rationalize conversion actions.

### Phase 4 — Landing-page corrections (external writes)
P1-8 through P1-15, then P2 items.

### Phase 5 — Bidding transition (external write, after ≥ 2 weeks of verified tracking)
Move from Maximize Clicks to Maximize Conversions once genuine lead conversions are recording.

### Phase 6 — Verification (no external write)
Re-render all five pages; re-confirm §11, §12, §13; run the approved end-to-end test.

### Proposed end-to-end test plan — **NOT EXECUTED, REQUIRES APPROVAL**

No test lead was submitted; no phone link was clicked; no call was placed. Proposed:

1. Load `…/ac-repair/?gclid=TEST_<timestamp>&utm_source=google&utm_medium=cpc` in a real browser.
2. Confirm `gtm.js?id=GTM-PQTPQ436` is requested and `dataLayer` initializes.
3. Confirm all 7 hidden fields populate.
4. Submit **one** lead with clearly marked test data ("GM AUDIT TEST", agency-controlled phone/email).
5. Confirm exactly **one** conversion is recorded — not three, despite three form copies.
6. Confirm the CRM/notification payload carries the click ID.
7. Place **one** test call to `(410) 705-6354` from an agency phone to confirm routing.
8. Delete the test entry from Gravity Forms.

**Requires: approval to submit a test lead, approval to place a test call, and confirmation of
which phone/email to use.**

---

## 20. Missing information and limitations

| # | Limitation | Effect |
|---|---|---|
| 1 | **No GTM API access configured.** | Container internals not enumerable. Mitigated — the container never loads, so browser evidence is decisive. |
| 2 | **No approved campaign blueprint in the repository.** | The $13,000 allocation was reconciled against the assignment text and the live `÷30.4` arithmetic, not an approved artifact. |
| 3 | **No target CPL / CPQL / CAC, no qualified-lead or sold-job data, no revenue or gross profit.** | **No profitability verdict is possible.** |
| 4 | **Only ~3.5 days since launch, 2 clicks, 0 conversions.** | Early performance is inconclusive by construction. |
| 5 | **`change_event` retention is limited** and the account was being edited during the audit. | Pre-Aug-13 change history unavailable; state may have shifted after capture. |
| 6 | **`OLD Ambient C&H` not audited.** | Legacy-account risk unquantified; needs its own gate. |
| 7 | **Image provenance unverifiable** from public sources. | P2-5 stays BLOCKED. |
| 8 | **Manager ID `1247547723` unreachable.** | Recorded as a discrepancy; verified manager used instead. |
| 9 | **No test lead or call placed.** | End-to-end lead delivery and call routing remain unverified by design. |
| 10 | **Search terms since launch are only 62 rows.** | All negative evidence derives from paused legacy campaigns; re-review after 30 days of clean data. |
| 11 | **Chrome DevTools MCP not available** in this environment. | Used Playwright-driven Chrome instead — equivalent for every required check. |

### Consolidated questions

**Q1.** Confirm the second ACTIVE manager link `2815082755` on the child account is expected.
**Q2.** Confirm the intended budget basis. Live budgets implement **$13,000 per month** (`÷30.4`).
If Aug 14–31 was intended, budgets are 41% low — though actual spend is ~1% of either.
**Q3.** Confirm the approved ad schedule. Live is Mon–Fri 08:00–20:00 + Sat 08:00–13:00; the brief
says Mon–Fri 08:00–16:00. Are calls answered until 8 PM and on Saturday?
**Q4.** Are the "Recent Work" photos genuine Ambient project photos?
**Q5.** Is WhatConverts actually in use? Two Primary WhatConverts upload actions are enabled.
**Q6.** Should `OLD Ambient C&H` (2391758435) be reviewed under its own work order?

---

## 21. Evidence appendix

**Audit timestamp:** 2026-08-17, approximately 17:29–19:10 UTC (13:29–15:10 America/New_York)
**Account timezone:** America/New_York · **Repository:** `D:\MG\green-marketing-gsa`

### GAQL queries executed (all `SELECT`; no mutate of any kind)

Identity and hierarchy — `customer`, `customer_client` (child + manager views, and an ENABLED
listing), `customer_manager_link`.
Structure — `campaign`, `campaign_budget`, `campaign_criterion`, `ad_group`,
`ad_group_criterion` (positive and negative), `ad_group_ad` (full RSA headlines/descriptions/pins/
policy topics), `campaign_asset`, `customer_asset`, `ad_group_asset`, `asset`,
`shared_set`, `shared_criterion`, `campaign_shared_set`, `geo_target_constant`,
`conversion_action`, `customer_conversion_goal`, `campaign_conversion_goal`, `recommendation`,
`change_event`.
Performance — `campaign`, `ad_group`, `keyword_view`, `ad_group_ad`, `ad_group_ad_asset_view`,
`geographic_view`, `search_term_view`, segmented by `date`, `day_of_week`, `hour`, `device`,
`ad_network_type`, `conversion_action_name`.

Windows: `launch_to_date` 2026-08-14→17 · `today` 2026-08-17 · `last_7` 2026-08-10→16 ·
`last_30` 2026-07-18→08-16 · `previous_30` 2026-06-18→07-17 · `last_90` 2026-05-19→08-16 ·
`last_365` 2025-08-17→2026-08-16 · `prior_365` 2024-08-17→2025-08-16.

**Query counts:** 54 (`scripts/audit_account.py`) + 68 supplementary + 5 verification. **Read
errors after correction: 1** (`campaign_asset` with an unsupported field, re-run successfully with
a valid field list).

### Key resource IDs

| Resource | ID |
|---|---|
| Child customer | `2401959466` — `Ambient Cooling - Live` |
| Manager (verified) | `3373711342` — `Green Marketing` |
| Second active manager link | `2815082755` |
| Conversion tracking ID | `11155434808` |
| Campaigns | `24132507741` AC Repair · `24132507750` HVAC Repair · `24132507747` HVAC Installation · `24132507753` HVAC Replacement · `24132507744` Gas Boiler Repair |
| Budgets | `15787409435`, `15787409444`, `15787409441`, `15787409447`, `15787409438` |
| Ad groups | `202339087834`, `202339087674`, `202339087634`, `200159223798`, `202339087594`, `202339087874` (REMOVED) |
| Disapproved RSAs | `820900825434`, `820900825437`, `820944944368`, `820944944371`, `820900825428`, `820900825431` |
| Limited RSAs | `820900825422`, `820900825425` |
| Call asset | `407995613637` — `(410)705-6354` |
| Dangerous negative lists | `11813144900` General List · `12091293463` Ambient - Neg Kwd List · `10720232972` General · `12178646912` General List - Irrigation Repair |
| Safe negative lists | `10664309518` States List · `10664304544` Names List · `12021721179`, `12021722439`, `12022987128`, `12025671131` (GM lists) |
| GTM container | `GTM-PQTPQ436` |
| Main-site GA4 | `G-9X9ZHNCRWF` |
| Legacy account (not audited) | `2391758435` — `OLD Ambient C&H` |

### URLs tested

All five offer pages rendered twice (desktop 1440×900, mobile 390×844 @2×) with the test query
string, plus a third clean load for timing; `offer.ambientcoolingandheating.com/` and
`ambientcoolingandheating.com/` for context. All returned 200 in a real browser.

### Local artifacts

| Path | Contents |
|---|---|
| `clients/ambient-cooling-heating/client.yaml` | Client profile, `identity_gate`, superseded conflict |
| `clients/ambient-cooling-heating/work-order.yaml` | Validated work order (PASS) |
| `clients/ambient-cooling-heating/snapshots/identity-gate-2026-08-17.json` | First-pass identity evidence |
| `clients/ambient-cooling-heating/snapshots/audit-2026-08-17.json` | Redacted audit snapshot (54 queries) |
| `clients/ambient-cooling-heating/snapshots/deep-read-2026-08-17.json` | Supplementary structure + performance + search terms |
| `clients/ambient-cooling-heating/exports/search-term-verdicts-2026-08-17.csv` / `.json` | 13,118-term evidence table |
| `clients/ambient-cooling-heating/plans/negative-keyword-approval-package-2026-08-17.json` | The §16 package, fingerprint `12E7572A25B9AFF0` |
| `reports/ambient-cooling-heating/evidence/` | Screenshots, page captures, script inventory, timings |

**Classification fingerprint:** `4772263dd49e58ef` · **Negative plan fingerprint:** `12E7572A25B9AFF0`

**No secrets, tokens, credentials, or lead PII appear in this report.** Environment variables were
confirmed present by name only; no value was read, printed, or logged. `.env`, OAuth settings, ADC,
and credentials were not modified.

---

## 22. Final statement

**No external changes were made during this audit.** Google Ads was read with `SELECT` statements
only. Google Tag Manager was never opened in a writable mode. No campaign was paused or enabled, no
budget or bid changed, no keyword or negative added, no shared list attached, no ad or asset edited,
no conversion goal changed, no website edit made, no form submitted, no telephone link clicked, and
no call placed. The negative-keyword package is a proposal awaiting approval against fingerprint
`12E7572A25B9AFF0`.
