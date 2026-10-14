# SOFTWIND POWER WASHING — RECOVERY STATUS

**Audit timestamp:** 2026-08-31 10:21:20 America/New_York (account-local, fresh-read from the API)
**Account:** Softwind Power Washing - Live · `1521725229` (152-172-5229) · MCC `3373711342` · USD · America/New_York
**Identity gate:** PASS — name exact match, ID exact match, manager `false`, test account `false`, status ENABLED
**Mode:** READ + DRAFT. **Zero Google Ads mutations were made.**

---

> ### CONTINUATION RESTATEMENT — 2026-08-31 16:40 America/New_York
>
> This report was written against the **10:21 audit snapshot**. A continuation drift check at
> **16:40** found that **Google retroactively invalidated four of the five clicks** recorded
> that morning on the query `power washing services` and **credited back $117.28**. Those four
> clicks moved into the invalid-clicks column.
>
> | | Audit snapshot 10:21 | Current live 16:40 |
> |---|---:|---:|
> | Impressions | 246 | **282** |
> | Billable clicks | 22 | **18** |
> | Spend | $713.15 | **$595.87** |
> | Average CPC | $32.42 | **$33.10** |
> | Invalid clicks | 60 | **73** |
> | Invalid share of raw clicks | 73.2% | **80.2%** |
> | Conversions | 0 | **0** |
>
> **Every other day in the ledger is byte-identical.** The reversal is isolated to the
> 2026-08-31 event. **No conclusion in this report is weakened by it — the traffic-quality
> finding is now confirmed by Google's own filtering**, and the CPC finding sharpens: the five
> post-ceiling billable clicks span **$29.04–$29.72**, a $0.68 range under a $30.00 cap.
>
> Figures below are the 10:21 audit snapshot unless marked otherwise. Where a decision depends
> on the corrected numbers, PLAN-R3 has been restated against the 16:40 ledger.

---

## Read this line first

**The account has spent $595.87, not ~$2,000** — $713.15 as of the 10:21 audit snapshot, less
the $117.28 Google credited back at midday. All-time, both campaigns, every day since the first
impression on 2026-08-05. The brief's figure is **3.4x** the actual spend on this account.
The most likely reconciliation is that it combines this account with the sibling
**Softwind Landscape & Masonry** (`2429758629`), whose own local record shows $1,163.22 of
all-time zero-converting spend. $595.87 + $1,163.22 = **$1,759.09** — near enough to
"approximately $2,000" to be the likely explanation. That is an inference, not a verified read:
the sibling account sits under a different work order and was not read in this run.

Everything below is about `1521725229` only.

---

## Headline numbers

| | Audit snapshot 10:21 | **Current live 16:40** |
|---|---:|---:|
| **All-time spend** | $713.15 | **$595.87** |
| Impressions | 246 | **282** |
| Billable clicks | 22 | **18** |
| CTR | 8.94% | **6.38%** |
| Average CPC | $32.42 | **$33.10** |
| **Google Ads conversions** | 0.00 | **0.00** |
| **Google Ads all-conversions** | 0.00 | **0.00** |
| Conversion rate | 0.00% | **0.00%** |
| CPA | undefined | **undefined (no conversions)** |
| **WhatConverts qualified Power/Pressure Washing leads** | UNKNOWN | **UNKNOWN — no export supplied** |
| **Confirmed Power/Pressure Washing leads** | UNKNOWN | **UNKNOWN — see below** |
| Search Impression Share (impression-weighted) | 61.24% / 75.34% | **53.55% (A) · 66.30% (B)** |
| Lost IS — budget | 2.30% / 2.27% | **2.01% (A) · 2.00% (B)** |
| Lost IS — rank | 35.97% / 20.12% | **31.45% (A) · 17.70% (B)** |
| Absolute-top impression share | 35.86% / 51.89% | **31.35% (A) · 45.67% (B)** |
| **Invalid clicks filtered by Google** | 60 vs 22 billable (73.2%) | **73 vs 18 billable — 80.2% of all raw clicks** |
| Campaigns / ad groups / keywords / RSAs | 2 / 30 / 214 / 54 | **2 / 30 / 214 / 54 — unchanged** |
| Locations / campaign negatives | 80 per campaign / 264 | **80 per campaign / 264 — unchanged** |
| Daily budgets | $41.50 (A) · $41.11 (B) | **unchanged** |
| CPC ceiling | $30.00 both | **unchanged** |

**Window detail, on the corrected ledger:** post-revamp (08-18→08-31) $590.16 · 17 clicks ·
$34.72 CPC · **post geo+budget (08-26→08-31)** $424.70 · 12 clicks · $35.39 CPC · **completed
days only (08-26→08-30)** $395.38 · 11 clicks · $35.94 CPC · **last 7 completed (08-24→08-30)**
$538.71 · 15 clicks · $35.91 CPC · **last 3 completed (08-28→08-30)** $117.90 · 4 clicks ·
$29.48 CPC · **current partial day** $29.32 · 1 click · 38 impressions · **pre-ceiling
(08-05→08-27)** $448.65 · 13 clicks · $34.51 CPC · **post-ceiling (08-28→08-31)** $147.22 ·
5 clicks · **$29.44 CPC**.

**Performance verdict: CRITICAL.**

---

## What happened this morning, before this audit ran

At **08:00–09:00 today**, the query **`power washing services`** took **five billable clicks
on one recorded impression** — **$146.60**, five clicks priced identically at $29.32 — from a
single postal code (**11742, Holbrook NY**), inside **one** ad group:
`Power Washing #2 / Residential Pressure Washing Near Me`.

At the audit snapshot that was **20.6% of the account's entire lifetime spend**. By 16:40
Google had reversed four of the five clicks and credited back $117.28, leaving the measured
cost at $29.32 — **but the routing defect and the traffic-quality signal are unchanged, and
Google's own filtering has now confirmed the second one.**

It matters for three separate reasons, and they are three different findings:

1. **Routing.** `power washing services` was matched as a NEAR_EXACT close variant of
   `residential pressure washing near me`. Campaign A holds the ad group that should have owned
   that query. Two mirrored campaigns bidding the same close-variant space let the wrong one win.
2. **Traffic quality.** Five billable clicks on one recorded impression is not a shape human
   search produces. Google has already filtered 60 invalid clicks in this account against 22
   billable ones — 73.2% of all raw clicks. Some of today's $146.60 may yet be credited back.
   ClickCease is installed on the site but is syncing **zero** IP blocks to these campaigns
   (`campaign_criterion` type `IP_BLOCK` count = 0).
3. **Price.** Every one of the five clicks priced at $29.32, just under the $30.00 ceiling.

At **09:39:41** the campaign-A budget was cut by hand in the Google Ads UI from **$333.33 to
$41.50**. Nothing in this repository did that and no plan authorised it. Given $146.60 was
already gone by 09:00, it was almost certainly the right instinct. It is recorded as observed
state.

---

## Primary causes

**Primary cause of high CPC — the ceiling is the price, not a guard rail.**
Since the $30.00 ceiling went in on 2026-08-27 12:25:35, **every one of the five billable
clicks priced between $29.04 and $29.72** — a range **$0.68 wide**, sitting directly under the
cap. Under a $5.00 ceiling (08-07 → 08-16) the
account took **zero clicks in twelve days**. Uncapped, clicks hit $54.49 and $82.22 — the
latter exactly 2x the then-$41.11 budget, because the daily overdelivery cap was the only brake
on price. **The price tracks the cap in all three regimes. It does not track the market.** Local
top-of-page LOW for the serving keyword set is $8.75–$13.49.

**Answer to the brief's question: GOOGLE IS BIDDING MORE FOR THE SAME AUCTIONS.** Decisively.
The geo expansion on 2026-08-26 added 72 locations per campaign and produced *no* impression
lift on the day it landed — the extra spend came from price, not volume.

**Primary cause of low CTR — Quality Score 1 on the account's biggest keyword.**
`power washing near me` scores **QS 1** with **BELOW_AVERAGE on all three components** (expected
CTR, ad relevance, landing-page experience). All six scored keywords are BELOW_AVERAGE on
expected CTR. A QS-1 keyword must bid far above a QS-8 competitor for the same position — which
is exactly why the account is pinned to its ceiling. Meanwhile it holds **36–52% absolute-top
impression share**: it is buying premium position with bottom-of-market quality and nothing to
show for it.

**Primary cause of zero CVR — the tag fires; paid traffic does not convert; and the Conversions
column could not show it either way.** Three distinct facts, all confirmed:

- The remarketing list **All Converters** ("People who converted on your site", 180-day
  window) holds **16 members** against **All visitors** at 160. **The conversion tag
  demonstrably fires.** It is not dead. *(Caveat: that list spans all traffic sources over 180
  days and is a rounded audience estimate. It proves the tag fires; it is not a lead count and
  proves nothing about any specific paid click.)*
- `metrics.all_conversions` is **0.00** on every campaign on every date, and
  `segments.conversion_action_name` returns **zero rows** — and the API omits all-zero segment
  rows, so that is real zero, not a reporting gap. **No paid click has produced a recorded
  conversion.**
- **All four conversion actions carry `include_in_conversions_metric: FALSE`**, because
  `customer_conversion_goal` returns `biddable: FALSE` for all four categories at account
  level. **The "Conversions" column is structurally incapable of counting a lead.** Bidding is
  unaffected — both campaigns override with campaign-level goals where the three lead
  categories *are* biddable — but every report, dashboard and API read of `metrics.conversions`
  will read 0.00 forever until this is fixed.

**The call path has never been tested at all.** The call asset has served **86 times and been
clicked zero times**. `call_view` returns zero rows across the whole retained log.

**Primary campaign-structure issue — the account does not own its own demand.**
Only **11 distinct keyword texts are actually serving** out of 214 keywords. The three largest
local buckets have **no matching keyword anywhere in the account**: `power washing` (880/mo at
$0.58–$14.31 — the *cheapest* bucket in the market), `pressure washing` (480/mo at
$0.30–$10.77), `power washing services` (140/mo). The account reaches them only through
close-variant matching, which routes each query to whichever of two mirrored campaigns Google
picks. That is what cost $146.60 this morning.

**Primary landing-page issue — the pages are branded for the wrong company, and city-locked to
three of eighty towns.** Every offer page's browser title ends **"| Softwind Landscape &
Masonry"** — the *sibling* account's brand, which is deliberately scope-fenced away from
washing. Six of eight pages carry an H1 locked to "Islip, West Islip & Dix Hills, NY", while
the campaigns have targeted **80 places across Nassau and Suffolk since 2026-08-26**. The page
carrying **60.6% of all spend** is one of them. Every page also runs an **"Offer Ends"
countdown** attached to no dated offer.

**Primary measurement issue — the foreign tag `AW-17878095007`** still loads on all six offer
pages alongside the account's own `AW-18369652705`. Flagged 2026-08-25, still live, owner still
unknown.

---

## Top 5 actions

1. **PLAN-R3 — cut the CPC ceiling from $30.00 to $22.00 on both campaigns.** 2 mutations, one
   field, exact rollback. Applied to the corrected 18-click ledger it turns $595.87 into
   **$379.71** and $33.10 into **$21.10** — roughly **57% more clicks for the same money**.
2. **PLAN-R1 — fix the conversion-counting configuration and get the WhatConverts export.**
   Until `customer_conversion_goal` is repaired, no report this account produces can show a
   lead. Zero Ads mutations.
3. **PLAN-R2 — remove the bare `cleaning` negative and replace it with three precise ones.**
   The account does not have a junk-traffic problem; it has the opposite. 8 mutations.
4. **PLAN-R6 — create three SKAGs paused for the demand the account does not own**
   (`pressure washing near me`, `power washing services`, `power washing`). 14 objects, all paused.
5. **PLAN-R7 — fix the landing-page brand, the city lock and the countdown, and resolve the
   foreign tag.** Website only, zero Ads mutations.

---

## Dispositions

**Ad groups to keep (3):** Power Washing Near Me `202870585390` · Power Washing Services Near Me
`202870585430` · Power Washing Company Near Me `202870585590` — all in campaign A.

**Ad groups to consolidate (1):** Residential Pressure Washing Near Me `202870585870` (A) into
the new Pressure Washing Near Me SKAG.

**Ad groups to pause after replacement (6):** `198082078783` (the one group enabled in *both*
campaigns) · `198082079423` · `198082078983` · `202870585630` · `202870585670` · `202870585830`.

**Keywords to keep (11 serving texts):** power washing near me · power washing services near me ·
power washing company near me · residential pressure washing near me · driveway pressure washing
near me · patio pressure washing near me · soft house washing near me · house pressure washing
estimate · power washing islip · power washing west islip · power washing dix hills.

**Keywords to add (5 objects, 3 texts):** `pressure washing near me` (Phrase + Exact, 90/mo) ·
`power washing services` (Phrase + Exact, 140/mo) · `power washing` (Phrase, 880/mo).
*Phase 2, documented not fingerprinted:* `pressure washing` (480/mo), `house washing near me`
(40/mo), `power washing long island` (70/mo).

**Keywords to stop:** none. All 214 are APPROVED, ELIGIBLE and in scope. The waste is in
routing and price, not in the keyword list.

**RSAs to replace (2 new, 1 retired):** two new RSAs for Power Washing Near Me (PLAN-R5); retire
`819975939342` (45 impressions, 1 click, 2.22% CTR, $82.22) only after the replacements have
served 7 days. Keep `819975939345` — 16.67% CTR, the account's best ad. All 54 existing ads are
APPROVED with zero policy issues and Ad Strength GOOD/EXCELLENT; no wholesale rewrite is justified.

**Landing pages to fix (6):** all six offer pages need the brand title corrected and the
countdown removed; six need the H1 city lock widened. Do **not** change any URL slug — it would
break the Final URL on 12 ad groups.

**Assets missing:** image assets (none in the account) · a business-name asset · **and the call
asset switches off at 17:00 while the campaigns run to 18:00** — the account's cheapest hour at
$22.12 CPC, running with no call button. *(The two campaign-A gaps this audit found at 10:21 —
the "Free Quote" sitelink and the structured snippet — were **closed by hand in the UI at 10:52
while this audit was running.** Both campaigns now carry identical asset sets. PLAN-R8 was
rewritten to zero mutations as a result; see below.)*

**Audience observations to add (12 criteria, 6 segments × 2 campaigns):** All visitors
`9446096870` · All Converters `9446168598` · In-market Home Improvement `80241` · In-market Home
& Garden Services `80483` · In-market Home Cleaning Services `80491` · In-market General
Contracting & Remodeling `80490`. **Observation only, 0% bid modifier, never Targeting.**

### Do not exclude women.

The account currently has **zero** gender, age and household-income criteria — verified clean,
nothing to undo. And the data actively argues against it: **women click at 17.95% and cost
$25.63 per click; men click at 9.22% and cost $32.46.** Excluding women would remove the
account's best-performing and cheapest gender segment from an account already starved of leads.

---

## Plan fingerprints — all NOT APPROVED, all DO NOT EXECUTE

| Order | Plan | Fingerprint | Mutations | Objects | State |
|---:|---|---|---:|---:|---|
| 1 | **R1** measurement verification | `98BA60C3983D` | 0 | 0 | FINAL |
| 2 | **R3** CPC ceiling $30 → $22 | `97D8B268A80A` | 2 | 2 | FINAL |
| 3 | **R2** search-term negatives | `2A06983866C1` | 8 | 8 | FINAL |
| 4 | **R4** core structure decision | `0E08B1CF1F16` | 0 | 0 | FINAL |
| 5 | **R5** two replacement RSAs (paused) | `440E0CB3FA65` | 2 | 2 | FINAL |
| 6 | **R6** three new SKAGs (paused) | `7530A7A8CB07` | 14 | 14 | FINAL |
| 7 | **R7** landing-page fixes (website only) | `BCC32C8C9FC7` | 0 | 0 | FINAL |
| 8 | **R8** asset parity — *closed by owner action* | `C941DDCA44C6` | 0 | 0 | NO-ACTION — no approval command |
| 9 | **R9** audience observations | `F7C28F116329` | 12 | 12 | FINAL |
| 10 | **R10** enablement | `CE1BA19B8F5A` | 11 | 11 | **PROVISIONAL — must be regenerated** |
| 11 | **R11** old-resource pauses | `3AB271E93FC7` | 11 | 11 | **BLOCKED on R10** |
| 12 | **R12** budget — hold, no change | `A730172A41A8` | 0 | 0 | FINAL |
| | **Total** | | **60** | **60** | |

**Recommended first approval — unchanged after the continuation reconciliation:**

```
APPROVE PLAN-R3 97D8B268A80A FOR 1521725229
```

*(PLAN-R3's evidence was restated against the 16:40 ledger. Its fingerprint is unchanged
because the canonical payload covers target identity and the exact action list only — never
narrative or evidence. Restating a figure must not invalidate an approval; changing a resource
ID, value, field mask or count must.)*

Two mutations, one field, immediate effect on the account's single largest controllable cost,
and a one-write rollback. **PLAN-R1** can run alongside it — it has zero mutations.

**Plans that must NOT be approved yet:**

- **PLAN-R10** — every resource it names is a `PENDING_CREATION` placeholder. Its fingerprint is
  provisional and must be regenerated against real IDs after R5 and R6 execute and pass readback.
- **PLAN-R11** — blocked until R10's replacements have served for seven days. Pausing before
  the replacement is proven means losing coverage the account currently has.
- **PLAN-R9** — technically safe, but it produces no leads. Do not approve it ahead of R3, R2 or R6.
- **PLAN-R8** — carries **no approval command at all**. Its two proposed mutations were done by
  hand during the audit, so it is now a zero-action status record. Its earlier two-mutation
  fingerprint **`DFF115FF4D26` is VOID — do not honour it.**
- **PLAN-R12** — carries no approval command; it proposes no budget change.
- **PLAN-R4** — a decision record with zero mutations. It is not an execution approval.
- **PLAN-R7** — website only. Separate approval track, not a Google Ads approval.

---

## What I could not determine

1. **WhatConverts leads.** No export exists anywhere in this repository for this client.
   Reconciliation cannot be completed. *(Blocker WC-1.)*
2. **Auction Insights.** `metrics.auction_insight_*` returns `PERMISSION_DENIED` — *"The
   developer doesn't have access to metrics: 'auction_insight_search_impression_share'."* The
   Green Marketing developer token is Basic access. **This must be exported from the Google Ads
   UI by a signed-in user.** I have not invented a single competitor figure; both auction-insights
   CSVs carry `INSUFFICIENT AUCTION DATA — API ACCESS DENIED` instead.
3. **The two phone numbers in the brief.** Neither **+1 631-519-8373** (GLE) nor
   **+1 631-315-8655** (GBP) appears in any Google Ads asset, any `tel:` link, or any
   landing-page body text audited today. Only the approved **(631) 502-7946** is present.
4. **Whether Softwind sells commercial work.** Gates two negative decisions (`gas station`,
   `commercial power washing company`) worth $35.31 of measured spend. *(K1-W2, open since 08-27.)*
5. **Whether the phone is answered 17:00–18:00.** Gates the call-asset schedule fix.
6. **Client economics.** `average_job_revenue`, `gross_margin_pct`, `close_rate_pct`,
   `target_cpl`, `target_cpql`, `target_cac` are all `null`. Until they exist, no CPL target,
   no ROAS and no profit-after-ad-spend figure can be produced — only cost per *recorded* lead.

---

## One change happened in the account while this audit ran — not by me

The closing verification re-read every mutable surface: **40 checks, 39 unchanged.** The one
difference is that **four `campaign_asset` links were created between 10:21 and 10:52**, by hand
in the Google Ads UI — the "Free Quote" sitelink and the "Service catalog" structured snippet on
campaign A, and a "Careful Washing Methods" callout on both campaigns.

**This agent made no mutation of any kind.** Every script in this run issues SELECT statements
only. The first two links are precisely what PLAN-R8 proposed, so **PLAN-R8 was rewritten to
zero mutations and re-fingerprinted** (`DFF115FF4D26` to `C941DDCA44C6`) rather than left as an
approvable artifact that would try to create links which now exist. All four new assets were
scope-checked and are clean: policy APPROVED, `source: ADVERTISER`, no unverified claim.

Both campaigns now carry identical asset sets — 4 sitelinks, 4 callouts, 1 structured snippet,
1 call asset each.

---

**FULL RECOVERY AUDIT AND EXACT CHANGE PLANS COMPLETE — ZERO EXTERNAL CHANGES MADE BY THIS AUDIT**
