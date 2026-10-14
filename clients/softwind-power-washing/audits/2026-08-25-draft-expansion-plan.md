# Softwind Power Washing — DRAFT Change Plan

**STATUS: DRAFT ONLY. NOTHING IN THIS DOCUMENT HAS BEEN IMPLEMENTED.**

Every item below requires its own exact plan, fingerprint, explicit approval, CREATE-PAUSED
step where applicable, readback QA, and a separate ENABLE approval. This file is a proposal.

**Account:** Softwind Power Washing - Live · `1521725229` · **Service:** Power Washing
**Drafted:** 2026-08-25 · **Mode:** READ (draft output only)

---

## 0. Verified claim inventory — the only material this copy may use

Drafted from facts observed on the live landing pages and the client site on 2026-08-25.
Nothing outside this list appears in any drafted asset.

**Verified and usable:**
power washing · pressure washing · soft washing · house washing · residential ·
driveway · patio · walkway · pavers · concrete · siding · trim · fences ·
surface-specific method selection · Islip · West Islip · Dix Hills · Long Island ·
free quote / free estimate (present on every offer page and on `softwindli.com/contact-us/`) ·
phone (631) 502-7946 · local service

**UNKNOWN — must not appear in any asset:**
years in business · review count or star rating · licensed / insured / bonded ·
warranty or guarantee · response-time promise · any price, discount or promotion ·
"same day" · number of jobs completed · awards · certifications

---

## 1. P0 — fix before buying any more traffic

### P0-1 · Remove the published authoring instruction from the highest-spend landing page

`https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/` contains
this sentence in live body copy:

> "Refresh siding, driveways, patios, walkways, pavers, and concrete **without making the
> page about unrelated services**."

This is an internal instruction that was never removed. It is visible to every visitor on
the page that has taken **$108.99 — 64% of all account spend**.

- **Why:** direct credibility damage on the page carrying the majority of paid traffic.
- **Evidence:** rendered body text, `landing-pages-2026-08-25.json`.
- **Expected effect:** removes an obvious trust defect. No measurable lift claimed.
- **Risk:** none. Text deletion only.
- **Requires approval:** YES — WordPress content change, separate deployment approval.

### P0-2 · Identify and decide on the second Google Ads tag `AW-17878095007`

Every offer page fires **two** Google Ads conversion IDs. Only `AW-18369652705` belongs to
this account.

- **Why:** a second account is receiving this client's conversion and audience data.
  Can duplicate conversion credit and corrupt future attribution.
- **Evidence:** rendered DOM + network requests on all six offer pages.
- **Expected effect:** clean, single-account attribution.
- **Risk:** removing it may break another party's reporting. **Identify the owner first.**
- **Requires approval:** YES — plus a client-fact answer: who owns `17878095007`?

### P0-3 · Verify the conversion tags actually fire

- **Why:** zero conversions have ever been recorded. Six clicks is far too few to prove
  anything, so the tags are unverified, not broken. No Smart Bidding decision can be made
  until this is settled.
- **Expected effect:** establishes whether the measurement foundation is real.
- **Requires approval:** YES — **END-TO-END TEST REQUIRES SEPARATE APPROVAL.** GTM preview
  first, then one marked form submission, then one marked call.

### P0-4 · Reinstate a Max CPC bid limit on both campaigns

Currently **no CPC ceiling** on either campaign since 2026-08-16 23:42. Average CPC is
**$28.53** against a local volume-weighted top-of-page range of **$8.66–$23.91**. One
click cost **$54.49**.

- **Proposed:** Max CPC bid limit **$22.00** on both campaigns (below the $23.91
  volume-weighted high, above the $16.29 midpoint, so it protects against $40+ clicks
  without pushing the campaign back under the auction floor).
- **Why $22.00 and not $5.00:** the previous $5.00 ceiling sat below the entire local
  top-of-page range and produced **12 consecutive days of zero clicks**. That mistake must
  not be repeated.
- **Expected effect:** CPC falls from ~$28.53 toward ~$16–20. **August spend will go DOWN.**
  Cost per click improves ~30–40%; click volume is unchanged.
- **Risk:** LOW. Reversible in one edit. If lost IS (rank) rises above ~25%, raise the cap.
- **Requires approval:** YES — bidding change, separate approval.

---

## 2. P1 — unlock qualified demand

### P1-1 · Open the ad schedule to evenings and Sunday

Current: **Mon–Sat 08:00–18:00 = 60 of 168 hours (35.7%).** Sunday deleted 2026-08-07.

The account's own hourly curve makes the case:

| Hour | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | **17** | 18+ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Impressions | 5 | 8 | 8 | 7 | 12 | 11 | 11 | 9 | 13 | **23** | **dark** |
| CTR | 0% | 0% | 0% | 0% | 8.3% | 0% | 9.1% | 0% | **15.4%** | 8.7% | — |

**17:00 is the single biggest hour in the account — 21.5% of all impressions — and the
curve is still climbing when the schedule cuts it off at 18:00.** Sunday has recorded
0 impressions all-time.

- **Proposed:** all 7 days, 00:00–24:00, no bid modifiers.
- **Why:** homeowners research exterior work after work and at weekends. The campaign is
  switched off during exactly that window.
- **Expected effect:** ~+50% reachable impressions (25.5 → ~38/day), independently
  corroborated by the Keyword Planner ceiling of 39.2/day.
- **Risk:** LOW for the **form**, which captures leads at any hour. Published hours are
  **Mon–Fri 8AM–6PM**, so an evening or Sunday caller may not reach anyone.
- **Mitigation:** open the *campaign* schedule 24/7 for form capture, and **constrain the
  CALL ASSET separately** to answerable hours. Note: call asset `403335872180` is linked to
  **both** campaigns — one edit rewrites hours on both.
- **NEEDS INTERNAL CONFIRMATION:** does anyone answer (631) 502-7946 evenings and Sundays,
  and what is the expected callback time for an after-hours form lead?
- **Requires approval:** YES.

### P1-2 · Unpause `House Washing Company Near Me` — the single fastest win

This ad group **already exists, fully built and approved, and is PAUSED in both campaigns.**

| | |
|---|---|
| Keyword | `house washing company near me` (Phrase + Exact) |
| Local demand | **40 searches/month** at **$10.46–$32.09** top-of-page, MEDIUM competition |
| RSAs | 2, already built, **APPROVED / REVIEWED** |
| Landing page | `https://offer.softwindli.com/house-washing-company/` — live, HTTP 200 |
| Work required | **status change only. No new resource.** |

- **Why:** unserved in-scope BOFU demand that needs no build. `house washing near me` is
  the third-largest BOFU bucket in the market and nothing in the account targets it.
- **Caution:** its historical search terms included `house cleaning services near me`
  (interior maid intent) and `slate roof cleaning near me` (out of scope). Pair the unpause
  with the two negatives in P1-4.
- **Expected effect:** +40 monthly searches of reachable demand, ~+1.3/day.
- **Risk:** LOW.
- **Requires approval:** YES — this is an ENABLE, so it needs enable approval.

### P1-3 · Resolve the two-campaign split and the duplicate ad group

| Problem | Evidence |
|---|---|
| Two enabled campaigns bid on the same keyword universe in the same geo | `24103511039` and `24145053510`, identical geo, schedule, negatives, bidding, conversion goals |
| `Power Washing Services Near Me` is **enabled in both** | AG `202870585430` (51 impr, 1 click) and AG `198082078783` (1 impr, 0 clicks) |
| Budget and learning are fragmented | Campaign 1 `primary_status: LEARNING`; campaign 2 separate learning cycle |

- **Recommendation:** consolidate into **one campaign**, and pause the duplicate ad group
  in campaign 2 first as the low-risk immediate step. Campaign 1 wins that duplicate almost
  every time already (51 impressions vs 1).
- **Why one campaign:** with ~26 impressions/day of total addressable demand, splitting it
  across two learning cycles and two budgets guarantees neither ever accumulates signal.
- **Expected effect:** consolidated bidding signal, one budget, cleaner reporting. No
  demand is lost — the same keywords serve either way.
- **Risk:** MEDIUM. Consolidation resets learning. Prefer: pause the duplicate ad group now
  (LOW risk), consolidate campaigns in September, not in the final week of August.
- **Requires approval:** YES.

### P1-4 · Negative keyword candidates — three only

Deliberately minimal. Green Marketing policy forbids auto-negativing `near me`, `quote`,
`estimate`, `cost`, `price`, `pricing`, `best`, `hire`, `local` and `emergency`, and none
of those appear here.

| Term | Match | Level | Evidence | Reason |
|---|---|---|---|---|
| `roof cleaning` | PHRASE | Campaign (both) | `roof washing near me` 2 impr; `slate roof cleaning near me` 1 impr | Roof cleaning is explicitly outside the approved service scope for this work order. |
| `house cleaning` | PHRASE | Campaign (both) | `house cleaning services near me` 1 impr | Reads as interior maid service, not exterior house washing. Different industry. |
| `roof washing` | PHRASE | Campaign (both) | `roof washing near me` 2 impr | Same out-of-scope service. |

**Explicitly NOT recommended as negatives** despite spending money:
`average cost to power wash a house` ($22.11), `powerwash cost` ($40.07), `cost to power
wash`, `price to powerwash house`, `how much is powerwashing a house`. These carry
**36% of all account spend** across 2 clicks with no lead — but two clicks prove nothing,
and cost-research queries convert in this vertical. **Verdict: WATCH, not block.** The
right fix is intent re-mapping (P3-2), not suppression.

**Existing negative worth reviewing: `how to` as a BROAD negative.** A broad negative
matches queries containing all its terms in any order, so `how to` blocks *"how much does
it cost **to** power wash a house"* and similar buyer-adjacent queries. Recommend narrowing
to PHRASE `how to`. Low priority, but it is a real false-negative.

---

## 3. P1-5 — DRAFT new SKAGs

Only candidates that pass all six BOFU gates: valid service intent · meaningful local
demand · feasible CPC · matching landing page · no dangerous overlap · likely to produce a
customer rather than a researcher.

### NEW SKAG A — `Pressure Washing Near Me`

| Field | Value |
|---|---|
| Campaign | Power Washing (`24103511039`) after consolidation |
| Ad group name | `Pressure Washing Near Me` |
| Phrase keyword | `"pressure washing near me"` |
| Exact keyword | `[pressure washing near me]` |
| Local demand | **70 searches/month**, HIGH competition, top-of-page **$8.75–$24.53** |
| Final URL | `https://offer.softwindli.com/residential-pressure-washing/` |
| Landing page H1 | "Residential Pressure Washing In Islip, West Islip & Dix Hills, NY" |

**Why the current architecture does not already cover it.** No live keyword contains the
word "pressure" as a head term. The demand still arrives — via close variants of
`power washing services near me` — and lands in a *power washing* ad group showing
*power washing* copy. The result is measurable: **`pressure washing` phrasing has produced
15 impressions and 0 clicks, a 0% CTR**, while `power washing` phrasing runs 7.2%. This is
a copy-match failure, not a coverage failure, and a dedicated SKAG is the fix.

### NEW SKAG B — `Pressure Washing Services Near Me`

| Field | Value |
|---|---|
| Phrase / Exact | `"pressure washing services near me"` / `[pressure washing services near me]` |
| Local demand | shares the **110/month** bucket with `power washing near me`, top-of-page **$10.89–$28.23** |
| Final URL | `https://offer.softwindli.com/residential-pressure-washing/` |

**Why not already covered:** `pressure washing service near me` and `pressure washing
services` have both appeared as search terms (3 and 1 impressions), routed into
`Power Washing Services Near Me`, **0 clicks between them.**

### NEW SKAG C — `Pressure Washing Company Near Me` (TEST)

Phrase + Exact `pressure washing company near me` → `/residential-pressure-washing/`.
`pressure washing companies near me` shows 10/month at **LOW** competition and has already
appeared as a search term routed into the power-washing company SKAG. Company phrasing is
proven BOFU in this account. Low volume, so a test.

### NEW SKAG D — `Paver Cleaning Near Me` (TEST)

Phrase + Exact `paver cleaning near me` → `https://offer.softwindli.com/patio-power-washing/`.
`paver cleaning` = **40/month at $5.05–$15.18**; `paver cleaners near me` = 20/month.
Paver **cleaning** sits inside the approved patio/driveway washing scope and the patio page
already names pavers. **Paver sealing is explicitly out of scope** — the copy must never
imply sealing, and `sealing`/`sealer` should be added as ad-group negatives.

### Candidates researched and REJECTED

| Candidate | Volume | Verdict | Why |
|---|---|---|---|
| `power washing` (generic head) | 480/mo | **AMBIGUOUS — do not add** | Low top-of-page bid collapses to **$0.57** and the bucket groups with "power pressure washer". Heavy equipment contamination. In this account it produced **14 impressions and 0 clicks**. |
| `pressure washing` (generic head) | 260/mo | **AMBIGUOUS — do not add** | Same pattern, $0.30 low bid. |
| `power washing cost` | 10/mo | **AMBIGUOUS — do not add** | $0.31 low top-of-page signals research intent. Account already spent $62.18 on two cost-research clicks with no lead. Monitor as a search term. |
| `pressure washer` / `best pressure washer` / `pressure washer rental` | high | **DO NOT ADD** | Equipment and retail intent. $0.49–$3.20 bid range confirms product, not service. Already blocked by existing negatives. |
| `soft washing near me` | 10/mo | **TEST, low priority** | Exists paused in the legacy `Soft & House Washing` group. Small. |
| `concrete pressure washing near me` | 10/mo | **TEST, low priority** | Surface already named on the driveway page. |

---

## 4. P2 — improve CTR and Ad Rank

### P2-1 · Rewrite both RSAs in `Power Washing Near Me`

This is the account's highest-intent ad group and its worst quality problem:

| Keyword | QS | Expected CTR | Ad relevance | Landing page | Primary status |
|---|---|---|---|---|---|
| `power washing near me` (Phrase) | **1** | Below Average | Below Average | Below Average | `AD_GROUP_CRITERION_LOW_QUALITY` |
| `power washing near me` (Exact) | **1** | Below Average | Below Average | Below Average | `AD_GROUP_CRITERION_LOW_QUALITY` |

Structural causes found: **zero pinned assets across all 24 live RSAs**, and **7 of 15
headlines duplicated between the two RSAs in this ad group (47%)**, so Google is choosing
from a narrow, largely interchangeable pool and frequently serves combinations that never
echo the searched phrase.

#### DRAFT RSA 1 — "Local power washing, near you"

Final URL `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
· path1 `power-washing` · path2 `free-quote`

| # | Headline | Len | Pin |
|---|---|---:|---|
| 1 | Power Washing Near You | 22 | **H1** |
| 2 | Local Power Washing Near You | 28 | **H1** |
| 3 | Power Washing In Islip NY | 25 | — |
| 4 | Long Island Power Washing | 25 | — |
| 5 | Get A Free Power Washing Quote | 30 | — |
| 6 | Free Power Washing Estimate | 27 | — |
| 7 | House, Patio And Driveway | 25 | — |
| 8 | Siding, Concrete And Pavers | 27 | — |
| 9 | Method Matched To Surface | 25 | — |
| 10 | Soft Washing For Siding | 23 | — |
| 11 | Serving Islip & West Islip | 26 | — |
| 12 | Power Washing In Dix Hills | 26 | — |
| 13 | Call (631) 502-7946 | 19 | — |
| 14 | Request Your Free Quote | 23 | — |
| 15 | Softwind Power Washing | 22 | — |

| # | Description | Len |
|---|---|---:|
| 1 | Local power washing for siding, driveways, patios and pavers. Request a free quote. | 83 |
| 2 | The cleaning method is chosen for the surface, from hard concrete to delicate siding. | 85 |
| 3 | Serving Islip, West Islip and Dix Hills homeowners. Free quote, no obligation. | 78 |
| 4 | Power washing near you on Long Island. Call (631) 502-7946 or request a quote. | 78 |

#### DRAFT RSA 2 — "Surface-specific method" (deliberately different angle)

Same URL · path1 `power-washing` · path2 `islip`

| # | Headline | Len | Pin |
|---|---|---:|---|
| 1 | Power Washing Near You | 22 | **H1** |
| 2 | Exterior Washing Near You | 25 | **H1** |
| 3 | Right Pressure, Right Surface | 29 | — |
| 4 | Low-Pressure Siding Washing | 27 | — |
| 5 | Driveway And Patio Washing | 26 | — |
| 6 | Paver And Concrete Washing | 26 | — |
| 7 | Walkway And Fence Washing | 25 | — |
| 8 | Cleaner Home Exteriors | 22 | — |
| 9 | Free Quote On Your Project | 26 | — |
| 10 | Tell Us What Needs Cleaning | 27 | — |
| 11 | Islip Area Power Washing | 24 | — |
| 12 | West Islip Power Washing | 24 | — |
| 13 | Dix Hills Power Washing | 23 | — |
| 14 | Local Long Island Team | 22 | — |
| 15 | Softwind Exterior Washing | 25 | — |

| # | Description | Len |
|---|---|---:|
| 1 | We match the washing method to the material, so siding is treated gently. | 73 |
| 2 | Driveways, patios, walkways, pavers and concrete washed and refreshed. | 70 |
| 3 | Tell us what needs cleaning and where. We will review it and send a free quote. | 79 |
| 4 | Power washing for Long Island homes. Free quote at (631) 502-7946. | 66 |

**Character validation:** validated programmatically — 15 headlines and 4 descriptions per ad, longest headline 30, longest description 85, no duplicate asset within an ad. All limits pass. **Overlap between the
two drafts: 1 of 15 headlines** (`Power Washing Near You`, intentionally pinned to H1 in
both so the searched phrase always appears). Compare with the current 47%.

**Why pin H1.** With no pins today, Google can serve a combination whose first headline
never mentions power washing. Pinning two interchangeable near-you variants to position 1
guarantees the searched service appears first while leaving 13 headlines free to rotate.
This directly targets the Below Average expected-CTR and ad-relevance components.

- **Expected effect:** MEDIUM confidence on CTR improvement; Quality Score should recover
  from 1 over 2–4 weeks of delivery. No specific percentage is claimed — 19 impressions is
  not a baseline.
- **Risk:** LOW. New ads are additive; the existing pair can stay live until the new pair
  proves out.
- **Requires approval:** YES — CREATE PAUSED, readback, then separate ENABLE.

### P2-2 · Point sitelinks at the offer subdomain

All five sitelinks (4 campaign-level + 1 account-level "Pressure Washing") send paid clicks
to `softwindli.com`, which shows the **untracked** (631) 502-5402, a 50-option service
dropdown and a 50-state address form. One click has already gone there — **$40.07, 23% of
all account spend.**

- **Proposed:** repoint to offer-subdomain equivalents, or restrict sitelinks to
  destinations that carry the tracked number and the short form.
- **Risk:** LOW. **Requires approval:** YES.
- **Also:** `softwindli.com/reviews/` returned an **SG-Captcha interstitial** that a full
  browser could not clear on the first attempt at either viewport. Real users usually pass
  it, but a paid click landing on a captcha is a real risk. And the reviews shown are for
  fencing, tree removal and hedge trimming — not power washing.

### P2-3 · Asset gaps

| Asset | Current | Target | Note |
|---|---|---|---|
| Sitelinks | 4 campaign-level | 4–8 | Count OK; destinations are the problem (P2-2). |
| Callouts | **4** campaign-level | **8–12** | Below the SOP minimum. Campaign-level callouts override the 4 account-level ones. |
| Structured snippets | 1 set, in scope | 1–2 | Values are accurate and in scope. |
| Call asset | (631) 502-7946 | correct | **35 impressions, 0 clicks.** Worth watching. |
| Business logo | **`primary_status: PENDING`** | approved | Not yet serving. |
| Image assets | **none** | consider | No image assets exist. |
| Location assets | `LOCATION_SYNC` "Business Profile" active | — | Serving: 49 `LOCATION_EXPANSION` impressions recorded. |

**Callout "Free Quotes" is verified** — free quote language appears on every offer page and
on `softwindli.com/contact-us/`. No unverified claim was found in any live asset.

---

## 5. P3 — improve conversion rate

### P3-1 · The evergreen countdown is a trust and compliance risk

Every one of the six offer pages carries a countdown reading **"Offer Ends in — 06 DAY
02 HRS 55 MIN"**. Two different pages loaded seconds apart both showed ~6 days 2h 55m,
which indicates a rolling per-visitor timer rather than a real deadline. **And there is no
offer** — the block it sits under is headed "Get A Free Quote".

A countdown to the expiry of a free quote, on a timer that resets, is manufactured urgency.
It is a Google Ads misleading-claims risk and an FTC deceptive-urgency risk.

- **Proposed:** remove it, or attach it to a genuine, dated, client-approved offer.
- **Requires approval:** YES — WordPress change. **Not removed during this READ audit.**

### P3-2 · Re-map `House Pressure Washing Estimate` intent

This ad group's close variants are almost entirely cost research: `average cost to power
wash a house`, `powerwash cost`, `cost to power wash`, `price to powerwash house`, `how
much is powerwashing a house`. It has taken **2 clicks and $62.18 — 36% of all account
spend — with no lead**, at a $31.09 average CPC.

Do **not** negative these terms. Instead make the page answer the question it is being
asked: the H1 is "Get A House Pressure Washing Estimate In Long Island", but the searcher
typed "how much does it cost". Add a transparent pricing-factors section and a
starting-from range **once the client verifies real numbers** (currently UNKNOWN).

### P3-3 · Mobile

Mobile carries **73% of impressions (78 of 107)** and **5 of 6 clicks**, with CTR 6.41% vs
desktop 3.57%. Mobile rendering was verified: forms, `tel:` links and CTAs all present at
390×844. No mobile defect found. Keep mobile-first in all future page work.

---

## 6. P4 — future bidding and scale

**Do NOT move to Maximize Conversions or tCPA yet.** The recommendation is to **stay on
Maximize Clicks with a $22.00 CPC ceiling.**

| Test | Result |
|---|---|
| Conversion volume | **0** — Smart Bidding has no signal |
| Conversion tracking verified | **NO** — never fired, unverified |
| Campaign age | 22 days |
| Search volume | ~26 impressions/day |
| Auction competitiveness | HIGH on the head terms |

Smart Bidding sounds more conversion-focused, and it would be the wrong call. Handing
bidding to a model with zero training data in a pool of 26 daily impressions produces
erratic delivery, not efficiency.

**Revisit when:** ≥15 verified conversions in 30 days, tags proven by end-to-end test,
and a stable ≥30 impressions/day. Then Maximize Conversions without a target first, tCPA
only after ~30 conversions.

**Offline outcomes** — once leads exist, feed qualified/closed-won status back through the
**Google Data Manager API** (per `CLAUDE.md`; the legacy Ads upload path only after
developer-token eligibility is confirmed).

---

## 7. Consolidated question list

Answers change the deliverable; everything not dependent on them is already complete.

1. **Service area — the highest-value question.** Which towns does Softwind actually serve
   for power washing? The campaigns target 8 fragmented cities (Bellmore, Islip, Syosset,
   West Islip, Dix Hills, Salisbury, plus North Hempstead and Babylon townships). "Islip"
   is targeted as the **hamlet (~18k people)**, not the Town of Islip (~340k). *This is the
   only lever that materially changes the demand ceiling.* **My recommendation:** if
   Softwind serves the wider Towns of Islip, Huntington, Babylon and Oyster Bay, targeting
   them would multiply addressable demand several times over. I will not expand geo without
   verified confirmation.
2. **After-hours coverage.** Is (631) 502-7946 answered evenings and Sundays? What is the
   callback commitment for an after-hours form lead? *Effect: gates P1-1. Without an
   answer my recommendation is campaign 24/7 for form capture, call asset restricted to
   Mon–Fri 8–6.*
3. **Who owns Google Ads account `17878095007`?** *Effect: gates P0-2.*
4. **Economics — average job revenue, gross margin, close rate, target CPL/CPQL.** All
   `null` in `client.yaml`. *Effect: gates conversion values (C-2), profit reporting, and
   any future tCPA target.*
5. **Is the $2,500 a performance target or a contractual commitment?** *Effect: determines
   whether we re-scope to ~$640 or roll the balance to September. My recommendation:
   re-scope, and judge August on cost per qualified lead.*
6. **Is the countdown timer tied to a real, dated offer?** *Effect: gates P3-1.*
7. **Review gating.** `softwindli.com/reviews/` presents a HAPPY / NEUTRAL / POOR emoji
   selector before routing reviewers. `config/agency.yaml` sets
   `review_collection.prohibit_review_gating: true`, and Google's review policy prohibits
   gating. It is on the client's site, not in the Ads account, but it is a paid-traffic
   destination. *Effect: compliance risk to raise with the client.*

---

## 8. Mutation inventory if every approved item were executed

**None of this has been done.** Counts are for the approval bundle that would follow.

| Change | Objects | Type |
|---|---:|---|
| Max CPC bid limit $22.00 | 2 | UPDATE campaign |
| Ad schedule 24/7 | 14 create / 12 remove | campaign criteria |
| Unpause `House Washing Company Near Me` | 1 | UPDATE ad_group status (**ENABLE approval**) |
| Pause duplicate `Power Washing Services Near Me` in campaign 2 | 1 | UPDATE ad_group status |
| New SKAGs A–D | 4 ad groups + 8 keywords + 8 RSAs | CREATE PAUSED |
| Campaign negatives (`roof cleaning`, `roof washing`, `house cleaning`) | 6 | CREATE (3 × 2 campaigns) |
| RSA rewrites, `Power Washing Near Me` | 2 | CREATE PAUSED |
| Sitelink URL repoint | 5 | UPDATE asset |
| Additional callouts to reach 8–12 | 4–8 | CREATE |
| **Total Google Ads mutations** | **~55–60** | **all gated** |
| WordPress: remove authoring instruction, resolve countdown, second tag | 3 | separate deployment approval |
