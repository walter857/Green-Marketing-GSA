# SOFTWIND POWER WASHING — COMPETITOR AND AUCTION ANALYSIS

**Generated:** 2026-08-31 America/New_York · Account `1521725229` · **READ-ONLY**
No paid ad was clicked during this research.

---

> **CONTINUATION RESTATEMENT — 2026-08-31 16:40.** A drift check at 16:40 found Google had
> retroactively invalidated **four of the five clicks** recorded that morning on
> `power washing services`, crediting back **$117.28**. The account ledger moved from
> **22 billable clicks / $713.15** to **18 billable clicks / $595.87**; invalid clicks rose
> 60 → 73, i.e. **80.2% of all raw clicks**. Every other day is byte-identical, conversions
> remain **0**, and no conclusion below changes — the traffic-quality finding is now confirmed
> by Google's own filtering.

---

## 1. Auction Insights — INSUFFICIENT AUCTION DATA (API access denied)

The Google Ads API **does** expose Auction Insights. `GoogleAdsFieldService` confirms all six
metrics exist and are `selectable: true`:

```
metrics.auction_insight_search_impression_share              selectable = True
metrics.auction_insight_search_overlap_rate                  selectable = True
metrics.auction_insight_search_position_above_rate           selectable = True
metrics.auction_insight_search_top_impression_percentage     selectable = True
metrics.auction_insight_search_absolute_top_impression_percentage  selectable = True
metrics.auction_insight_search_outranking_share              selectable = True
segments.auction_insight_domain                              selectable = True
```

Every query against them returns:

```
StatusCode.PERMISSION_DENIED
"The developer doesn't have access to metrics:
 ''auction_insight_search_impression_share''."
```

Tested at **customer**, **campaign**, **ad-group** and **keyword_view** level; with a date
filter and without one; and with a minimal single-metric SELECT. All four variants fail
identically.

**Root cause: the Green Marketing developer token is on Basic access, which does not carry
Auction Insights metrics.** This is a token-tier limitation, not a query error and not an
account permission problem.

**Consequence:** Auction Insights must be exported from the Google Ads UI by a signed-in user.
I hold no authenticated UI session for this account and did not attempt an interactive login.

`2026-08-31-auction-insights-campaign.csv` and `2026-08-31-auction-insights-ad-group.csv`
therefore each contain **one row reading `INSUFFICIENT AUCTION DATA - API ACCESS DENIED`**.
**Not one competitor impression share, overlap rate, position-above rate, top-of-page rate,
absolute-top rate or outranking share has been invented.**

### Manual UI export — exact steps

1. Sign in to Google Ads on account **152-172-5229**.
2. **Campaigns** → select **Power Washing** (`24103511039`).
3. **Insights and reports → Auction insights**. Set the date range **2026-08-01 → 2026-08-31**.
4. **Download → CSV**. Save to `clients/softwind-power-washing/audits/`.
5. Repeat for **Power Washing #2** (`24145053510`).
6. Repeat at **ad-group** level for the only four ad groups with enough impressions to meet
   Google's reporting threshold:
   - `Power Washing Near Me` `202870585390` — 104 impressions
   - `Power Washing Services Near Me` `202870585430` — 98 impressions
   - `House Pressure Washing Estimate` `198082078983` — 26 impressions
   - `Power Washing Services Near Me` `198082078783` — 13 impressions
   Every other ad group has 0–11 impressions and will return nothing. **That is
   `INSUFFICIENT AUCTION DATA`, not an error.**
7. **Do not click a competitor's paid ad** at any point.

---

## 2. What the account's own data says about auction pressure

Auction Insights would tell us *who* is above Softwind. The account's own metrics already tell
us *whether* Softwind is being outbid — and the answer is more interesting than expected.

| Proxy metric (impression-weighted, restated 16:40) | Campaign A `24103511039` | Campaign B `24145053510` |
|---|---:|---:|
| Search impression share | **53.55%** | **66.30%** |
| Search Lost IS — **budget** | 2.01% | 2.00% |
| Search Lost IS — **rank** | **31.45%** | **17.70%** |
| **Search absolute-top impression share** | **31.35%** | **45.67%** |

*(At the 10:21 audit snapshot these read 61.24% / 75.34% IS and 35.86% / 51.89% absolute-top.
The fall is the day's later impressions landing, not a configuration change.)*

### The four questions the brief asked

**Is Softwind being crowded out of the auctions?**
**No.** It holds **54–66% impression share**. On 2026-08-24 and 2026-08-29 campaign A held
**100%**. This is not an advertiser being shut out.

**Is Softwind paying high CPC because of auction pressure?**
**Only partly — and not primarily.** Lost IS to *budget* is effectively zero (0.00% on 24 of the
30 delivering campaign-days). The entire gap is lost to **rank**. But rank is Ad Rank, and Ad
Rank is bid × Quality Score. **Quality Score is 1 on the account's biggest keyword and 1–5 on
every keyword Google has scored, with BELOW_AVERAGE expected CTR across the board.** A QS-1
keyword must bid far above a QS-8 competitor for the same position. The price is being driven
by Softwind's own quality signal at least as much as by competitor pressure.

**Does Softwind have low rank despite high bids?**
**Yes — that is exactly the pattern.** It bids at its $30.00 ceiling (every one of the five
post-ceiling clicks priced $29.04–$29.72) and still loses 18–31% of impression share to rank.

**Is Softwind already overpaying for top positions?**
**Yes, and this is the decisive finding.** It holds **31.35% and 45.67% absolute-top impression
share** — it is *winning* the most expensive slot on the page, close to half the time in
campaign B — while carrying Quality Score 1–5 and having produced **zero recorded conversions
in 18 clicks**. Buying the premium position with a bottom-of-market quality signal and no
measured return is the definition of overpaying. **PLAN-R3** deliberately trades some of that
absolute-top share for a lower price.

### The market price, for comparison

Keyword Planner, restricted to the live 80-target footprint:

| Bucket | Monthly | Top-of-page LOW | Top-of-page HIGH | Softwind actually pays |
|---|---:|---:|---:|---:|
| power washing near me / company near me | 260 | $10.90 | $28.32 | $29.57 |
| power washing services / pressure washing services | 140 | $11.55 | $23.34 | $29.32 |
| pressure washing near me | 90 | $8.75 | $24.66 | $29.57 |
| house washing near me | 40 | $10.46 | $24.75 | — |
| power washing services near me | 30 | $10.62 | $28.70 | $27.33–$29.04 |
| house power washing near me | 20 | $13.49 | $32.86 | — |
| **power washing (head)** | **880** | **$0.58** | **$14.31** | not bought |
| **pressure washing (head)** | **480** | **$0.30** | **$10.77** | not bought |

Softwind pays **2.2×–3.4× the top-of-page LOW** and sits at or just above the HIGH on most
buckets. It is buying the most expensive slice of the market and ignoring the two cheapest,
largest buckets entirely.

---

## 3. Competitor landscape — public SERP research

Gathered from ordinary public search research. **No paid ad was clicked.** Nothing below is
copied into Softwind's ads: every competitor claim is unverifiable from Green Marketing's side
and several are exactly the claim types on Softwind's `unverified_claims_do_not_use` list.

### Direct competitors in Nassau and Suffolk

| Competitor | Domain | Positioning observed |
|---|---|---|
| Cleanfellas | `cleanfellasinc.com` | "Top-Rated Pressure Washing in Nassau & Suffolk" · residential **and commercial** · eco-friendly angle · online quote-request form |
| Best Power Wash LI | `bestpowerwashli.com` | Veteran-owned · soft washing + pressure washing · **publishes price ranges** · free no-obligation estimates |
| Suffolk Power Washing LLC | `suffolkpowerwash.com` | "premier Long Island power washing" · all of Suffolk **and** Nassau · phone **and text** contact · dedicated "Get a Quote" page |
| Supreme Clean Power Washing | `supremecleanpowerwashingny.com` | Suffolk County focus · "competitive rates" · free estimates |
| Gulf 2 Bay Softwash | `gulf2baysoftwash.com` | ZIP-level landing pages (e.g. `/pressure-washing-in-suffolk-county-ny-11746/`) · siding, driveways, decks |
| Platinum Power Washing | `platinumpowerwashing.com` | Bohemia-based, family-run, "since 2017" · Suffolk County |
| 495 Pressure Washing | `495pressurewashing.com` | Suffolk + Nassau + Long Island |
| Rolling Suds | `rollingsudspowerwashing.com/long-island-nassau/` | **National franchise** with a Long Island/Nassau page — the deepest pockets in the auction |
| Crispy Clean LI | `crispycleanli.com` | Power washing + soft washing, Suffolk |
| South Shore Power Washing | `southshorespressurewashing.com` | **Islip-based** · salt-air/humidity angle specific to South Shore homes · satisfaction guarantee |
| Summit Facility Solutions | `summit-facility-solutions.com` | **West Islip** · BBB A+ rating |
| Milone Pressure Washing | (HomeAdvisor listing) | **West Islip** · owner-operator |

**This is a dense, mature local market.** At least twelve identifiable competitors serve
Softwind's exact footprint, including one national franchise and at least three businesses
based in the very hamlets Softwind's landing pages name.

### What competitors do that Softwind does not

| Competitor tactic | Softwind today | In scope to copy? |
|---|---|---|
| **Publish price ranges** (one competitor lists house washing $300–$800, driveway $150–$400) | No price anywhere on any page | **Yes, IF the client supplies real figures.** Nine of Softwind's 53 search terms are price research and they have cost $62.18 with nowhere to land. |
| **Star ratings and review counts** above the fold | None on any offer page | **Only with written client confirmation** — on the unverified-claims list |
| **Years in business** ("since 2017") | None | **Only with written client confirmation** |
| **BBB rating, licensed/insured badges** | None | **Only with written client confirmation** |
| **Satisfaction guarantee** | None | **Only with written client confirmation** |
| **Text-message contact** alongside phone | Phone and form only | **Yes** — no verification needed, but needs the client to actually monitor texts |
| **Hyper-local geographic depth** (ZIP-level pages) | 3 hamlets named on 6 of 8 pages, against 80 targeted places | **Yes** — but the fix is to *widen* to Long Island, not to build 80 pages |
| **Local environmental angle** ("salt air and humidity on South Shore homes") | Generic surface-specific messaging | **Yes** — factual, verifiable, differentiating |
| **Explicit commercial service line** | Residential only, by verified scope | **Blocked on Q1** — the `gas station pressure washing near me` click cost $35.31 |

### What Softwind already does as well as or better than the field

- **Surface-specific method messaging** — "we match the method to the material, soft washing
  for siding and pressure washing for concrete" — is a genuine differentiator and is verified.
  Most competitors lead with price or speed.
- **Six purpose-built service landing pages** rather than one generic homepage.
- **A tracked phone number** on every offer page, correctly implemented.
- **Ad copy quality**: 54 of 54 ads APPROVED, zero policy issues, Ad Strength GOOD/EXCELLENT,
  no unsupported claims. Several competitors run copy Softwind could not run under Green
  Marketing policy.

### The trust gap, plainly

Softwind's offer pages score **3/10 on trust** in this audit. Every competitor listed above
carries at least one trust signal Softwind carries none of — a rating, a review count, a years
figure, a BBB badge or a guarantee. **All five are on Softwind's `unverified_claims_do_not_use`
list**, so none may be added without written client confirmation.

**This is the single highest-value conversion question to put to the client**, and it is a
question, not a task: *what review count, star rating, years in business, and licence or
insurance status can you confirm in writing?* Whatever comes back can go on the page. Nothing
else can.

---

## 4. Verdicts

| Question | Verdict | Confidence |
|---|---|---|
| Competitors dominating the auctions | **UNKNOWN by name** — Auction Insights requires a UI export | — |
| Competitors appearing above Softwind | **Some, on 20–36% of auctions** — inferred from Lost IS (rank), not from Auction Insights | HIGH |
| Softwind paying high CPC because of auction pressure | **PARTLY** — the market is dense, but Quality Score 1–5 and a $30 ceiling that acts as the price explain more | HIGH |
| Softwind has low rank despite high bids | **YES** — bidding at the ceiling and still losing 20–36% of IS to rank | HIGH |
| **Softwind already overpaying for top positions** | **YES** — 31–46% absolute-top impression share with QS 1–5 and zero recorded conversions | **HIGH** |
| Competitors use stronger offers, copy, proof or service wording | **YES on proof and price transparency. NO on copy quality or service wording** — Softwind's ad copy is stronger and cleaner than most of the field | MEDIUM |

---

## 5. What this changes in the recovery plan

1. **PLAN-R3 (ceiling $30 → $22) is reinforced, not weakened, by the competitive picture.**
   Softwind is not being shut out of the auction; it is winning too much of the most expensive
   part of it. Trading absolute-top share for price is the right trade when the top position
   has returned nothing in 18 clicks.
2. **PLAN-R6's head-term ad group is the competitive opening.** `power washing` at 880/mo and
   $0.58–$14.31 top-of-page is roughly **half** what Softwind currently pays, and it is the
   bucket the whole local field under-serves in favour of near-me variants.
3. **PLAN-R7's trust work is the largest untapped conversion lever** — and it is entirely
   gated on client-confirmed facts, not on anything the agency can decide.
4. **Q1 (does Softwind sell commercial?) now has a competitive dimension.** Several competitors
   serve both residential and commercial. If Softwind does too, a commercial landing page is a
   real opportunity; if not, `gas station` and `commercial` need fences.

---

**COMPETITOR ANALYSIS COMPLETE — NO PAID AD CLICKED, NO DATA INVENTED**
