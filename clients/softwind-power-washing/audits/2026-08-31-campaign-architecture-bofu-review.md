# SOFTWIND POWER WASHING — CAMPAIGN ARCHITECTURE AND BOFU INTENT REVIEW

**Generated:** 2026-08-31 18:28 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
Identity gate re-run fresh: `Softwind Power Washing - Live` / `1521725229` / manager `false` /
test `false` / ENABLED / USD / America/New_York — **PASS**

**Zero external changes. No plan created. No fingerprint generated.**

---

## 1. Exact current campaign names and IDs — verified from the live account

| Campaign ID | **Exact current name** | Status | Budget | Bidding | CPC ceiling | Learning |
|---|---|---|---:|---|---:|---|
| `24103511039` | **"Power Washing"** | ENABLED / SERVING | $41.50 | TARGET_SPEND | $30.00 | ELIGIBLE |
| `24145053510` | **"Preassure Washing"** | ENABLED / SERVING | $41.11 | TARGET_SPEND | $30.00 | **LEARNING** (`BIDDING_STRATEGY_LEARNING`) |

### ⚠ The second campaign name is misspelled

> **`24145053510` is named "Preassure Washing".** The correct spelling is **"Pressure"**.
> Detected by explicit string test, not by eye.

It is internal-facing only — campaign names never appear in an ad — so there is **no policy or
customer-visible impact**. But it will appear in every report, every export and every dashboard
Walter reads, and it makes the campaign hard to find by search in the UI. Worth correcting under
a separate approval. **Nothing was renamed in this step.**

### Both campaigns, full state

| | Power Washing `24103511039` | Preassure Washing `24145053510` |
|---|---|---|
| Biddable goals | PHONE_CALL_LEAD/WEBSITE · PHONE_CALL_LEAD/CALL_FROM_ADS · SUBMIT_LEAD_FORM/WEBSITE | **identical** |
| Locations | 80 targeted + 1 excluded, PRESENCE | **identical** |
| Schedule | Mon–Sat 08:00–18:00, 6 dayparts | **identical** |
| Negative keywords | 132 | **132** |
| Assets | 4 sitelink · 4 callout · 1 snippet · 1 call | **identical** |
| Search Partners / Display | off / off | off / off |
| Ad groups | 6 enabled / 9 paused | 6 enabled / 9 paused |
| Keywords | 9 serving / 98 dormant | 12 serving / 95 dormant |
| **Final URLs** | **8** | **the same 8** |
| Impressions · clicks · spend | 218 · 12 · $403.09 | 46 · 6 · $192.78 |
| CTR · CPC · conversions | 5.50% · $33.59 · **0** | 13.04% · $32.13 · **0** |
| IS · lost rank · lost budget | 48.00% · 48.89% · 3.11% | 64.10% · 28.21% · 7.69% |

---

## 2. Did the rename produce real traffic separation?

# NO. None whatsoever.

A campaign name is a label. It changes no keyword, no match type, no close-variant behaviour and
no Ad Rank input. The evidence says the naming is not merely ineffective — **it is close to
inverted from what the account actually does.**

### 2a. Google itself treats "power" and "pressure" as one demand pool

The single most important finding in this review. Keyword Planner, restricted to the live
80-target footprint, returns these as **shared volume buckets** — identical volume, identical
bid range, i.e. **one pool of demand, not two**:

| Bucket | Vol/mo | Top-of-page | Keywords sharing it |
|---:|---:|---|---|
| 1 | **260** | $10.90–$28.32 | `power washing near me` · `power washing company near me` · **`pressure washing services near me`** |
| 2 | **140** | $11.55–$23.34 | `power washing service` · **`pressure washing service`** |
| 3 | **20** | no data | `pressure washing company near me` · `residential pressure washing near me` |
| 4 | **20** | $13.49–$32.86 | `house power washing near me` · **`house pressure washing near me`** |
| 5 | **10** | no data | `driveway power washing near me` · **`driveway pressure washing near me`** · `exterior house washing near me` |
| 6 | **0** | no data | `patio pressure washing near me` · `concrete pressure washing near me` |

**Google collapses power ↔ pressure into the same bucket in six separate places.** A campaign
architecture that splits them is splitting a pool Google does not split. That is authoritative
evidence, not inference.

Deduped total local demand across all buckets: **1,980 searches/month.**

### 2b. The routing is close to inverted

Query-ownership matrix over all **55** search terms with impressions or clicks:

| Verdict | Terms |
|---|---:|
| **CORRECT** (exact term → exact keyword, right campaign) | **1** |
| ACCEPTABLE CLOSE VARIANT | 27 |
| **WRONG CAMPAIGN** | **14** |
| **WRONG AD GROUP** (out-of-scope intent) | **8** |
| **DUPLICATE ELIGIBILITY** (served in both campaigns) | **5** |

**Exactly one of fifty-five search terms routes correctly.**

**PRESSURE terms serving inside the "Power Washing" campaign** — including the account's
single biggest term by spend:

| Term | Impr | Clicks | Spend |
|---|---:|---:|---:|
| **`pressure washing`** | 3 | 2 | **$59.82** |
| `pressure washing service near me` | 10 | 0 | — |
| `pressure washing companies near me` · `pressure washer near me` · `pressure washer service near me` · `pressure washing service` · `local services pressure washing` | 7 | 0 | — |

**POWER terms serving inside the "Preassure Washing" campaign:**

| Term | Impr | Clicks | Spend |
|---|---:|---:|---:|
| `powerwash cost` | 2 | 1 | **$40.07** |
| `average cost to power wash a house` | 2 | 1 | **$22.11** |
| `house power wash` · `cost to power wash` · `how much does power washing a house cost` · `power washing costs` · `price to powerwash house` | 11 | 0 | — |

### 2c. Overlap and mis-routing percentages

| | Terms | Impressions | Valid clicks | Spend |
|---|---:|---:|---:|---:|
| **DUPLICATE ELIGIBILITY** (served in both) | 5 | **16.7%** | **26.7%** | **24.8%** |
| **WRONG CAMPAIGN** under the new naming | 15 | **17.6%** | **33.3%** | **33.8%** |
| **Wrong campaign or wrong ad group** | 22 | **23.1%** | **33.3%** | **33.8%** |
| **Combined mis-routed or duplicated** | 27 | **≈40%** | **≈60%** | **≈58.6%** |

**Roughly 60% of valid clicks and 59% of spend sit in query space that is either duplicated
across both campaigns or routed to the campaign whose name contradicts the query.**

### 2d. Structural contradictions the rename created

- **The "Preassure Washing" campaign contains the ad group `Power Washing Services Near Me`**
  with `power washing services near me` in Exact and Phrase. A power intent, in the pressure
  campaign, by name.
- **The same ad group name is ENABLED in both campaigns** — the direct duplicate.
- The "Power Washing" campaign holds 9 paused ad groups that include *Residential Pressure
  Washing Near Me*, *Driveway Pressure Washing Near Me*, *Patio Pressure Washing Near Me* and
  *Soft House Washing Near Me* — pressure intents parked inside the power campaign.
- **All 8 landing pages are shared** by both campaigns. Nothing distinguishes their destinations.
- Both still hold the identical 107 keyword rows and the identical 15 ad-group names.

---

## 3. BOFU verdict — every currently enabled ad group

| Campaign | Ad group | ID | Kw | RSA | Impr | Clk | Spend | CPC | Canonical intent | Landing page | **Verdict** |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| Power Washing | **Power Washing Near Me** | `202870585390` | 2 | 2 | 90 | 7 | $288.07 | $41.15 | power washing, local hire | `/power-washing-services-islip…/` | **CORE BOFU** — KEEP BUT REWRITE ADS (ad relevance BELOW_AVERAGE) |
| Power Washing | **Power Washing Services Near Me** | `202870585430` | 2 | 2 | 98 | 4 | $109.31 | $27.33 | power washing service purchase | `/power-washing-services-islip…/` | **CORE BOFU** — KEEP |
| Preassure Washing | **House Pressure Washing Estimate** | `198082078983` | 2 | 2 | 26 | 3 | $104.85 | $34.95 | *intended* estimate request; *actual* price research | `/house-pressure-washing-estimate/` | **AMBIGUOUS → PAUSE LATER AFTER REPLACEMENT** |
| Preassure Washing | **Residential Pressure Washing Near Me** | `198082079423` | 2 | 2 | 7 | 2 | $58.89 | $29.45 | residential pressure washing | `/residential-pressure-washing/` | **CONSOLIDATE** into Pressure Washing Near Me |
| Preassure Washing | **Power Washing Services Near Me** | `198082078783` | 2 | 2 | 13 | 1 | $29.04 | $29.04 | duplicate of `202870585430` | `/power-washing-services-islip…/` | **REDUNDANT → PAUSE LATER AFTER REPLACEMENT** |
| Power Washing | **Power Washing West Islip** | `202870585670` | 1 | 2 | 1 | 1 | $5.71 | $5.71 | city-modified power washing | `/power-washing-services-islip…/` | **LOW SEARCH VOLUME → PAUSE LATER** |
| Power Washing | **Power Washing Company Near Me** | `202870585590` | 2 | 2 | 14 | 0 | $0.00 | — | power washing company | `/power-washing-services-islip…/` | **CONSOLIDATE** — same 260/mo bucket as Power Washing Near Me |
| Power Washing | **Power Washing Islip** | `202870585630` | 1 | 2 | 0 | 0 | $0.00 | — | city-modified | `/power-washing-services-islip…/` | **LOW SEARCH VOLUME → PAUSE LATER** |
| Power Washing | **Power Washing Dix Hills** | `202870585830` | 1 | 2 | 0 | 0 | $0.00 | — | city-modified | `/power-washing-services-islip…/` | **LOW SEARCH VOLUME → PAUSE LATER** |
| Preassure Washing | **Soft House Washing Near Me** | `198082078703` | 2 | 2 | 0 | 0 | $0.00 | — | soft washing | `/soft-house-washing/` | **LOW SEARCH VOLUME** (10/mo) — KEEP, watch |
| Preassure Washing | **Driveway Pressure Washing Near Me** | `198082079023` | 2 | 2 | 0 | 0 | $0.00 | — | driveway washing | `/driveway-pressure-washing/` | **LOW SEARCH VOLUME** (10/mo shared bucket) — KEEP, watch |
| Preassure Washing | **Patio Pressure Washing Near Me** | `198082079183` | 2 | 2 | 0 | 0 | $0.00 | — | patio washing | `/patio-power-washing/` | **LOW SEARCH VOLUME** (0/mo reportable) — KEEP BUT CHANGE LANDING PAGE |

The 18 paused ad groups keep their earlier classifications — *Pressure & Power Washing*
(34 keywords, 4 canonical intents) and *Soft & House Washing* (28 keywords, 2 intents) both fail
the one-intent test and stay **permanently paused**.

---

## 4. BOFU verdict — every serving keyword

Scores: BOFU hiring intent / Local intent / Service specificity / Estimate likelihood /
**Equipment-DIY ambiguity (5 = worst)** / **Semantic overlap risk (5 = worst)** / LP alignment.

| Keyword | MT | Campaign | Vol/mo | TOP low–high | Impr | Clk | CPC | QS | ExpCTR/Rel/LP | BOFU | Loc | Spec | Est | Amb↓ | Ovl↓ | LP | **Verdict** |
|---|---|---|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| `power washing near me` | E | PW | 260 | $10.90–28.32 | 47 | 4 | $35.97 | **1** | BELOW/BELOW/BELOW | 5 | 5 | 5 | 5 | 1 | 2 | 3 | **CORE BOFU** — keep; fix ads + LP |
| `power washing near me` | P | PW | 260 | $10.90–28.32 | 43 | 3 | $48.06 | **1** | BELOW/BELOW/BELOW | 5 | 5 | 5 | 5 | 1 | 3 | 3 | **CORE BOFU** — keep |
| `power washing services near me` | E | PW | 30 | $10.62–28.70 | 79 | 4 | $27.33 | 3 | BELOW/ABOVE/BELOW | 5 | 5 | 5 | 5 | 0 | 4 | 3 | **CORE BOFU** — keep |
| `power washing services near me` | P | PW | 30 | $10.62–28.70 | 19 | 0 | — | 3 | BELOW/ABOVE/BELOW | 5 | 5 | 5 | 5 | 0 | 4 | 3 | **KEEP** |
| `power washing services near me` | E+P | **Preassure** | 30 | $10.62–28.70 | 13 | 1 | $29.04 | 5 | BELOW/ABOVE/AVERAGE | 5 | 5 | 5 | 5 | 0 | **5** | 3 | **REDUNDANT** — duplicate of the above |
| `house pressure washing estimate` | E | Preassure | — | no data | 26 | 3 | $34.95 | — | — | 2 | 3 | 4 | 2 | 2 | 3 | 2 | **AMBIGUOUS** — pulls cost research, not estimate requests |
| `house pressure washing estimate` | P | Preassure | — | no data | 0 | 0 | — | — | — | 2 | 3 | 4 | 2 | 2 | 3 | 2 | **AMBIGUOUS** |
| `residential pressure washing near me` | E | Preassure | 20 | no data | 7 | 2 | $29.45 | — | — | 5 | 5 | 5 | 5 | 0 | **5** | 4 | **CONSOLIDATE** — close-variant magnet, absorbed 4 of 5 shared terms |
| `residential pressure washing near me` | P | Preassure | 20 | no data | 0 | 0 | — | — | — | 5 | 5 | 5 | 5 | 0 | **5** | 4 | **CONSOLIDATE** |
| `power washing company near me` | E+P | PW | 260 | $10.90–28.32 | 14 | 0 | — | — | — | 5 | 5 | 5 | 5 | 0 | **5** | 3 | **CONSOLIDATE** — same bucket as `power washing near me` |
| `power washing west islip` | E | PW | no data | — | 1 | 1 | $5.71 | — | — | 4 | 5 | 4 | 4 | 1 | 2 | 4 | **LOW SEARCH VOLUME** |
| `power washing islip` | E | PW | no data | — | 0 | 0 | — | — | — | 4 | 5 | 4 | 4 | 1 | 2 | 4 | **LOW SEARCH VOLUME** |
| `power washing dix hills` | E | PW | no data | — | 0 | 0 | — | — | — | 4 | 5 | 4 | 4 | 1 | 2 | 4 | **LOW SEARCH VOLUME** |
| `soft house washing near me` | E+P | Preassure | 10 | no data | 0 | 0 | — | — | — | 5 | 5 | 5 | 4 | 0 | 2 | 5 | **LOW SEARCH VOLUME** — keep |
| `driveway pressure washing near me` | E+P | Preassure | 10 | no data | 0 | 0 | — | — | — | 5 | 5 | 5 | 4 | 1 | 2 | 5 | **LOW SEARCH VOLUME** — keep |
| `patio pressure washing near me` | E+P | Preassure | 0 | no data | 0 | 0 | — | — | — | 5 | 5 | 5 | 4 | 1 | 2 | 3 | **LOW SEARCH VOLUME** — KEEP BUT CHANGE LANDING PAGE |

**Zero Google Ads conversions and zero relevant WhatConverts leads on every keyword above.**
No keyword is condemned for that — the account has never recorded a conversion of any kind, so
zero carries no discriminating information.

**No keyword is credited merely for containing "near me."** `power washing west islip` contains
a local modifier and is still LOW SEARCH VOLUME because Planner returns no reportable demand for
it.

---

## 5. Local Keyword Planner — head-term SERP intent check

The brief asks whether ambiguous head terms are dominated by service providers, equipment, DIY
or mixed intent. Checked in ordinary public search. **No paid ad was clicked.**

| Query | SERP composition | Verdict |
|---|---|---|
| **`power washing` + Long Island** | **100% local service providers** — Island Wide Pressure Washing, Pressure Wash Long Island, Long Island Power Washing, Cleanfellas, McMorris, Super Clean Machine, Rolling Suds. Zero equipment, zero retail, zero DIY | **STRONG local commercial service intent — recommendable** |
| **`pressure washing` + Long Island** | same provider set | **STRONG — recommendable** |
| **`pressure washer`** (bare, singular) | **100% equipment retail** — Ace Hardware, Tractor Supply, Lowe's, Harbor Freight, Consumer Reports buying guide, Wikipedia. **Zero local service providers** | **EQUIPMENT/RETAIL — do NOT bid; keep fenced** |

**The distinguishing token is the grammatical form, not the word.** *Washing* (gerund) is the
service; *washer* (noun) is the machine. The account's existing BROAD negatives already fence
the machine framings — `pressure washer for sale`, `power washer rental`, `pressure washer
parts`, `power washer repair`, plus `harbor freight`, `home depot`, `lowes`, `ryobi`, `karcher`,
`simpson`.

**Consequence:** `power washing` (880/mo, $0.58–$14.31) and `pressure washing` (480/mo,
$0.30–$10.77) **are safe to bid** — they are the largest and cheapest local buckets and the SERP
is entirely commercial. Two observed terms remain WATCH items, not negatives:
`power washer near me` (4 impr, 0 clicks) and `pressure washer near me` (1 impr) — the noun
form, but with a local modifier that usually signals a contractor search.

---

## 6. Architecture options compared

| | **OPTION 1 — Two campaigns** | **OPTION 2 — One campaign** | **OPTION 3 — Hybrid** |
|---|---|---|---|
| Campaign count | 2 | **1** | 2 |
| Active ad groups | 12 today → ~8 after cleanup | **5–6** | 6 + 1 |
| Active keywords | 21 today → ~14 | **10** | ~12 |
| **Duplicate eligibility** | **Unavoidable** — Google shares the buckets | **Zero by construction** | Low, if the second campaign is a genuinely different intent |
| Data concentration | **Split across two learning states** | **Full concentration** | Mostly concentrated |
| Search-term control | Poor — needs mirrored cross-campaign negatives | **Direct** — ad-group negatives only | Good |
| CTR impact | Neutral-to-negative (internal contention) | **Positive** — one ad group owns each intent | Neutral |
| CPC impact | Negative — self-competition raises Ad Rank pressure | **Positive** | Neutral |
| CVR impact | Neutral | **Positive** — cleaner intent→page mapping | Neutral |
| Operational complexity | **High** | **Low** | Medium |
| Transition risk | None (status quo) | **Medium** — learning reset, short volatility | Medium |
| Confidence | **Low** | **High** | Low — no qualifying second intent exists |

### Option 1 cannot be made to work, and the reason is not opinion

To separate power from pressure you would need **mirrored cross-campaign negatives**: every
pressure concept negatived in the Power campaign, every power concept negatived in the Pressure
campaign. The concepts would be — *pressure washing, pressure wash, residential pressure
washing, house pressure washing, driveway pressure washing, patio pressure washing, concrete
pressure washing* in one direction, and *power washing, power wash, powerwash, powerwashing,
house power washing, driveway power washing, patio power washing* in the other.

**That fails on its own terms, three ways:**

1. **Google shares the volume buckets.** Negativing `pressure washing services near me` out of
   the Power campaign removes it from the **260/mo bucket that `power washing near me` also
   sits in.** You would be fencing off demand you want.
2. **The head terms cannot be split at all.** `power washing` (880/mo) and `pressure washing`
   (480/mo) are the same service to the same searcher.
3. **Close variants defeat the fence.** This account has already matched `power washing
   services` → `residential pressure washing near me` as NEAR_EXACT on one shared token in five.

*(Concepts listed as required by the brief. No executable negative plan has been created.)*

### Option 3 — no qualifying second intent exists

A second campaign is justified by a genuinely different **intent, business objective, budget,
geography or conversion path** — never by a synonym. Assessed against the account:

- **Different geography?** No — both target the identical 80 locations.
- **Different conversion path?** No — identical biddable goals, identical call asset.
- **Different budget objective?** No — $41.50 vs $41.11, no stated rationale.
- **Different service?** No — every intent is exterior washing.
- **Commercial vs residential?** **The only candidate** — `gas station pressure washing near me`
  ($35.31) and `commercial power washing company near me` exist. But commercial is **not in the
  verified scope**, every landing page is residential, and this is blocked on K1-W2. **It does
  not justify a second campaign today.**

**No current service intent justifies a second campaign.**

---

## 7. Recommended architecture

# OPTION 2 — CONSOLIDATE INTO ONE CAMPAIGN

**Surviving campaign: `24103511039`** — older, `ELIGIBLE` not `LEARNING`, 218 of 264
impressions, and it already owns the core near-me intents.

**`24145053510` "Preassure Washing" is retired — paused, never deleted** — only after its
unique intents are rebuilt, verified and enabled in the surviving campaign.

---

## 8. Recommended core structure — 6 ad groups, 10 keywords

| # | Ad group | Canonical intent | Phrase | Exact | Local demand | Top-of-page | Landing page | Why it deserves its own ad group |
|---|---|---|---|---|---:|---|---|---|
| 1 | **Power Washing Near Me** | power washing, local hire | `power washing near me` | `power washing near me` | **260/mo** | $10.90–$28.32 | `/power-washing-services-islip-west-islip-dix-hills/` | Largest near-me bucket; the account's proven click source |
| 2 | **Pressure Washing Near Me** | pressure washing, local hire | `pressure washing near me` | `pressure washing near me` | **90/mo** | $8.75–$24.66 | `/residential-pressure-washing/` | **A distinct Planner bucket** from #1, with its own bid range. No keyword for it exists anywhere in the account today |
| 3 | **Power Washing Service** | service purchase, no geo qualifier | `power washing service` | `power washing service` | **140/mo** | $11.55–$23.34 | `/power-washing-services-islip-west-islip-dix-hills/` | Distinct bucket, LOW competition (index 13), **+131% trend** — the strongest growth signal in the set |
| 4 | **House Washing Near Me** | house / exterior washing | `house washing near me` | `house washing near me` | **40/mo** | $10.46–$24.75 | `/house-washing-company/` | Distinct bucket with a purpose-built page; currently dormant behind a permanently paused container |
| 5 | **Power Washing** *(head)* | power washing, unqualified | `power washing` | — | **880/mo** | **$0.58–$14.31** | `/power-washing-soft-washing/` | Largest bucket in the market and the cheapest. SERP is 100% local providers. The page is the only one not city-locked |
| 6 | **Pressure Washing** *(head)* | pressure washing, unqualified | `pressure washing` | — | **480/mo** | **$0.30–$10.77** | `/power-washing-soft-washing/` | Second largest, second cheapest. Already earned 3 impressions and 2 clicks ($59.82) purely as a close variant |

**Coverage: 1,910 of 1,980 deduped monthly searches — 96.5% — with 10 keywords in 6 ad groups.**
Today's 21 serving keywords in 12 ad groups cover roughly 330/mo.

**Exact and Phrase only. No Broad Match anywhere.**

Ad groups 5 and 6 take **Phrase only** — Exact on a head term buys the literal query and
forfeits the qualified long tail the group exists to reach. They carry higher variance than
1–4 and should be **enabled as a second stage**, seven serving days after the others.

### Deliberately NOT given separate ad groups

- `power washing company near me` and `pressure washing services near me` — **same 260/mo bucket
  as #1.** Separate ad groups would split one demand pool across three containers.
- `pressure washing service` — **same 140/mo bucket as #3.**
- `house pressure washing near me` / `house power washing near me` — same 20/mo bucket, and
  `house washing near me` at 40/mo already covers the intent.
- **City ad groups** (Islip, West Islip, Dix Hills) — no reportable Planner demand and 1
  impression between them across the account's whole life.
- `power washing quote` / `pressure washing estimate` — 10/mo each, and the estimate framing is
  the one that already misfires into cost research.

---

## 9. Consolidate or pause later

**Pause only after replacements are live and verified — never before.**

| Resource | ID | Reason |
|---|---|---|
| Ad group `Power Washing Services Near Me` (Preassure) | `198082078783` | **REDUNDANT** — enabled in both campaigns |
| Ad group `Residential Pressure Washing Near Me` | `198082079423` | **CONSOLIDATE** into #2 — 20/mo, and the close-variant magnet that absorbed 4 of 5 shared terms |
| Ad group `House Pressure Washing Estimate` | `198082078983` | **AMBIGUOUS** — $104.85 spent, every term it attracted was price research |
| Ad group `Power Washing Company Near Me` | `202870585590` | **CONSOLIDATE** into #1 — same 260/mo bucket |
| Ad groups `Power Washing Islip` / `West Islip` / `Dix Hills` | `202870585630` · `202870585670` · `202870585830` | **LOW SEARCH VOLUME** — 1 impression combined, lifetime |
| Campaign **`24145053510` "Preassure Washing"** | | **Retire last**, after its four unique intents are live in `24103511039` |
| Ad groups `Pressure & Power Washing` · `Soft & House Washing` | `205713509704` · `205713509744` · mirrors | **REMAIN PERMANENTLY PAUSED** — 34 and 28 keywords across 4 and 2 canonical intents |

---

## 10. New BOFU keyword opportunities

| Keyword | Match | Vol/mo | Top-of-page | Status today | Evidence |
|---|---|---:|---|---|---|
| **`power washing`** | Phrase | **880** | **$0.58–$14.31** | **not in account** | 34 impressions + 1 click earned purely as a close variant; SERP 100% local providers |
| **`pressure washing`** | Phrase | **480** | **$0.30–$10.77** | **not in account** | 3 impressions, 2 clicks, **$59.82** — the biggest single term by spend, currently in the wrong campaign |
| **`pressure washing near me`** | Exact + Phrase | **90** | $8.75–$24.66 | **not in account** | 14 impressions, 1 click across two campaigns via close variants |
| **`power washing service`** | Exact + Phrase | **140** | $11.55–$23.34 | dormant | LOW competition (13), **+131% trend** |
| **`house washing near me`** | Exact + Phrase | **40** | $10.46–$24.75 | dormant | 4 impressions across both campaigns |
| `jet wash near me` | Exact | low | — | not in account | 3 impressions; a synonym, **not** a negative |

---

## 11. Landing-page mapping and CVR scores

| Ad group | Page | Kw→H1 | Kw→Title | Ad→Page | Service clarity | Local rel. | Reviews | Phone CTA | Form CTA | Mobile | Tracking |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 1 Power Washing Near Me | `/power-washing-services-islip…/` | 8 | **2** | 9 | 10 | **4** | **0** | PASS | PASS | PASS | PARTIAL |
| 2 Pressure Washing Near Me | `/residential-pressure-washing/` | 8 | **2** | 8 | 10 | **4** | **0** | PASS | PASS | PASS | PARTIAL |
| 3 Power Washing Service | `/power-washing-services-islip…/` | 8 | **2** | 9 | 10 | **4** | **0** | PASS | PASS | PASS | PARTIAL |
| 4 House Washing Near Me | `/house-washing-company/` | 9 | **2** | 9 | 10 | **4** | **0** | PASS | PASS | PASS | PARTIAL |
| 5 Power Washing (head) | `/power-washing-soft-washing/` | **9** | **2** | 8 | 10 | **8** | **0** | PASS | PASS | PASS | PARTIAL |
| 6 Pressure Washing (head) | `/power-washing-soft-washing/` | 7 | **2** | 7 | 10 | **8** | **0** | PASS | PASS | PASS | PARTIAL |

Title scores 2/10 everywhere because **every offer page is titled "… | Softwind Landscape &
Masonry"** — the scope-fenced sibling brand. Local relevance scores 4/10 on the city-locked
pages and 8/10 on `/power-washing-soft-washing/`, the only page not restricted to three hamlets.
Tracking is PARTIAL because the approved phone and GCLID pass while the conversion column cannot
count.

`/patio-power-washing/` keeps its **title-vs-H1 mismatch** — title says "Patio **Power**
Washing", H1 says "Patio **Pressure** Washing". Low priority, but it is the one page whose own
wording repeats the account's power/pressure confusion.

---

## 12. Top five immediate CVR improvements

| Rank | Fix | Evidence | Expected impact | Confidence | Risk | New plan needed? |
|---|---|---|---|---|---|---|
| **P0-1** | **Correct the browser title on all 6 offer pages** — they read "Softwind Landscape & Masonry" | Verified in a real browser, desktop and mobile | **HIGH** — the page carrying 60.6% of spend tells the visitor they are at a masonry company | HIGH | LOW | PLAN-R7 (website) |
| **P0-2** | **Fix conversion-goal configuration** — `customer_conversion_goal` biddable FALSE ×4 | Fresh API read | **No leads created**, but nothing is measurable until it is done | HIGH | LOW | PLAN-R1 (0 Ads mutations) |
| **P0-3** | **Resolve foreign tag `AW-17878095007`** on all 6 offer pages + 2 main-site pages | Verified in browser | MEDIUM — a third party receives Softwind's conversion signal | HIGH | LOW | PLAN-R7 / owner |
| **P1-1** | **Widen the H1 city lock** from 3 hamlets to Long Island / Nassau & Suffolk on 6 pages | Campaigns target **80** places since 2026-08-26; Google reports LP experience BELOW_AVERAGE | **HIGH** | MEDIUM | PLAN-R7 |
| **P1-2** | **Remove the "Offer Ends" countdown** — no dated offer exists | On all 6 offer pages; `unverified_claims_do_not_use` forbids promotions | MEDIUM | HIGH | LOW | PLAN-R7 |

*Runner-up, P2:* no review count, rating, years in business, or licence/insurance on any page —
every competitor carries at least one. **All are on the unverified-claims list and need written
client confirmation before anything is added.**

**No conversion-rate increase is guaranteed.** The account has never recorded a conversion, so
there is no baseline against which to promise a lift.

---

## 13. Effect on the future $12 CPC plan

| Question | Answer |
|---|---|
| Should $12 eventually apply to **both** campaigns? | **Yes — while two campaigns exist.** Applying it to one creates the Ad Rank asymmetry that blocked PLAN-R3A. |
| Should it apply to the **surviving consolidated** campaign? | **Yes.** After consolidation there is one campaign and one ceiling. |
| Are **different ceilings** justified by different query markets? | **No.** Google shares the volume buckets across power and pressure in six places, and both campaigns target identical geography, goals, schedule and landing pages. There is no evidence of two markets. |
| Should the CPC test **wait** for consolidation? | **No — run it first.** Consolidation is 3–5 weeks and ~37 mutations; the account meanwhile pays ~$29/click. |
| Would applying $12 **now** interfere with the transition? | **Only if they overlap.** Run the $12 test on both campaigns for its 10 serving days **first**, then begin consolidation. Reversing that order confounds both. |

**Recommended sequence:** $12 on **both** campaigns (2 mutations) → 10 serving days → read →
*then* consolidation (PLAN-R6 → R10 → R11). The surviving campaign inherits whatever ceiling the
test proves.

**No PLAN-R3B has been created and no fingerprint generated.** PLAN-R3A `B57E427D07C5` remains
**BLOCKED**; the architecture decision must come first, and it now points at the same
two-campaign action the control-integrity review recommended.

---

## 14. WhatConverts evidence

> **USER-SUPPLIED WHATCONVERTS RECORDS REVIEWED — ZERO CONFIRMED RELEVANT POWER WASHING OR
> PRESSURE WASHING LEADS IN THE SUPPLIED ROWS.**

Preserved alongside it, and independent of it:

> **Google Ads conversion measurement is not yet configured to support a reliable standard
> Conversions-column CPL or CVR judgment.** All four conversion actions carry
> `include_in_conversions_metric: FALSE` because `customer_conversion_goal` returns
> `biddable: FALSE` for all four categories.

---

## 15. Missing evidence and confirmations

| # | Needed | Blocks |
|---|---|---|
| Q1 | **Does Softwind sell commercial / industrial washing?** | Whether commercial ever justifies a second campaign; two negative decisions worth $35.31 |
| Q2 | **Who owns Google Ads account `17878095007`?** | P0-3 |
| Q3 | **Should "Preassure Washing" be renamed?** | Cosmetic, but it is in every report |
| Q4 | **Review count, star rating, years in business, licence/insurance** | The largest untapped CVR lever; nothing may be published without written confirmation |
| Q5 | **Is (631) 502-7946 answered 17:00–18:00 Mon–Fri?** | Call-asset schedule (stops at 17:00 while campaigns run to 18:00) |
| Q6 | **Real price ranges** | Whether the cost cluster gets a page or gets retired |
| Q7 | **Average job revenue, gross margin, close rate, target CPL** | All `null` — no profit or ROAS figure is possible |

---

**ARCHITECTURE AND BOFU REVIEW COMPLETE — ZERO EXTERNAL CHANGES MADE**
