# SOFTWIND POWER WASHING — CORE RESCUE STRUCTURE

**Generated:** 2026-08-31 America/New_York · Account `1521725229` · **READ-ONLY, DRAFT**
Fingerprinted as **PLAN-R4 `0E08B1CF1F16`** — zero mutations. NOT APPROVED.

---

> **CONTINUATION RESTATEMENT — 2026-08-31 16:40.** A drift check at 16:40 found Google had
> retroactively invalidated **four of the five clicks** recorded that morning on
> `power washing services`, crediting back **$117.28**. The account ledger moved from
> **22 billable clicks / $713.15** to **18 billable clicks / $595.87**; invalid clicks rose
> 60 → 73, i.e. **80.2% of all raw clicks**. Every other day is byte-identical, conversions
> remain **0**, and no conclusion below changes — the traffic-quality finding is now confirmed
> by Google's own filtering.

---

## The diagnosis in one paragraph

The account carries **2 campaigns, 30 ad groups and 214 keywords for 18 lifetime billable clicks** —
roughly one click per twelve keywords. The obvious reading is "too many SKAGs, consolidate." That
reading is half right and would fix the wrong half. The real defect is that **the containers do
not own the demand**. Only **11 distinct keyword texts are actually serving**, and the three
largest local buckets — `power washing` (880/mo), `pressure washing` (480/mo) and
`power washing services` (140/mo) — have **no matching keyword anywhere in the account**. The
account reaches them only through Google's close-variant matching, which routes each query to
whichever of two mirrored campaigns Google picks. **The answer is not simply fewer ad groups.
It is fewer ad groups that own more demand.**

---

## What that cost, in one measured event

On **2026-08-31 in the 08:00 hour**, the query **`power washing services`** took **five
billable clicks on one recorded impression — $146.60**, all five priced at $29.32, from a single
postal code (**11742, Holbrook NY**), inside **`Power Washing #2 / Residential Pressure Washing
Near Me`**, matched as a `NEAR_EXACT` close variant of `residential pressure washing near me`.
**Google reversed four of those five clicks by 16:40, crediting back $117.28** — the routing
defect is unchanged, but the measured cost of this single event is now $29.32, not $146.60.

Campaign A holds `Power Washing Services Near Me`, the ad group that should have owned that
query — and the same term *has* served there (4 impressions, 0 clicks). **Two mirrored campaigns
bidding the same close-variant space let the wrong one win.** At the audit snapshot that was **20.6% of the account's entire lifetime spend**; after the
reversal the measured cost is **4.9%**. The routing defect it exposes is unchanged.

---

## Campaign comparison — DUPLICATIVE AND CANNIBALIZING

| | Power Washing | Power Washing #2 |
|---|---|---|
| ID | `24103511039` | `24145053510` |
| Created | 2026-08-04 09:22:12 | 2026-08-18 09:24:13 |
| Primary status | **ELIGIBLE** | **LEARNING** (`BIDDING_STRATEGY_LEARNING`) |
| Ad groups (total / enabled) | 15 / 6 | 15 / 6 |
| Keywords | 107 | 107 |
| Impressions | 232 | 50 |
| Clicks | 12 | 6 (was 10 pre-reversal) |
| CTR | 5.17% | 12.00% (was 22.73% pre-reversal) |
| Cost | $403.09 | $192.78 (was $310.06 pre-reversal) |
| Average CPC | $33.59 | $32.13 |
| Conversions | 0 | 0 |
| Daily budget | $41.50 | $41.11 |

### Duplication evidence — twelve signals, not one

1. **Exact mirrors.** 15 ad groups each with *identical names*. All 15 names exist in both.
2. **Identical keyword sets.** 107 keywords each, same texts, same match types.
3. **One directly duplicated serving container.** `Power Washing Services Near Me` is ENABLED
   in **both** (A: 94 impr / 4 clicks / $109.31 · B: 13 impr / 1 click / $29.04).
4. **`power washing services` served in both campaigns from different keywords** — and the
   campaign-B routing cost $146.60 at the time, $29.32 after Google reversed four of the
   five clicks.
5. **`pressure washing near me` served in four different ad groups** across both campaigns.
6. **`house washing near me` served in three** across both.
7. **`power washing services near me` served in both.**
8. **Ten asset IDs are shared**, including the single call asset `403335872180`. Editing one
   edits both.
9. **Both campaigns use the same eight landing pages.**
10. **Both target the identical 80 locations** and the identical Connecticut exclusion.
11. **Both run the identical Mon–Sat 08:00–18:00 schedule.**
12. **Both carry the identical 132 campaign negatives.**

### The nuance that matters

**Campaign B's CTR was an artefact, and the reversal proves it.** At 10:21 campaign B showed
22.73% CTR, driven entirely by `Residential Pressure Washing Near Me` at 7 impressions and 6
clicks — an 85.7% CTR that is not a shape human search produces. After Google invalidated four
of those clicks, campaign B reads **50 impressions, 6 clicks, 12.00% CTR** and that ad group
reads **7 impressions, 2 clicks, $58.89**. The container is still the account's worst
traffic-quality risk; it simply no longer flatters the campaign that holds it.

### Consequence

Conversion data is fragmented across two containers that have produced **zero** conversions
between them, and close-variant routing is choosing the wrong one. **Consolidate.**

---

## The decision

**Campaign `24103511039` "Power Washing" owns everything.**

**Why A and not B:** it is older (08-04 vs 08-18), it is `ELIGIBLE` rather than `LEARNING`, it
carries 232 of 282 impressions, and it holds the core near-me intents. Consolidating into the
LEARNING campaign would discard the older campaign's learning; consolidating into A costs only
campaign B's four-day-old learning window — which PLAN-R3's ceiling change restarts anyway.

**Campaign B is retired, not deleted.** Its four unique serving intents are rebuilt inside
campaign A (PLAN-R6), verified, enabled (PLAN-R10), and only *then* is campaign B paused
(PLAN-R11). No deletion is proposed anywhere; that would need a separate destructive-action
approval.

**Timing.** The 2026-08-25 audit deferred consolidation to September because it resets learning
in August's last week. **That deferral expires today. September 1 is the correct window.**

---

## Query-intent map

Demand figures are **deduped Keyword Planner buckets** for the live 80-target footprint, sampled
across the four Towns plus the six largest constituent places. Planner collapses synonyms into
shared buckets — summing raw rows overstates demand, so buckets are counted once.

| Intent | Monthly | Top-of-page | Terms observed | Current owner | Spend | Clicks | **Recommended owner** |
|---|---:|---|---|---:|---:|---|
| **power washing** (head) | **880** | $0.58–$14.31 | `power washing` | **NONE** — close variant of `power washing near me` EXACT | $29.57 | 1 | **NEW: Power Washing** |
| **pressure washing** (head) | **480** | $0.30–$10.77 | `pressure washing` | **NONE** — close variant | $59.82 | 2 | **PHASE 2: Pressure Washing** |
| power washing near me | 260 | $10.90–$28.32 | `power washing near me`, `power wash near me`, `powerwashing near me`, `power washer near me`, `powerwash near me`, `local power washers` | Power Washing Near Me (A) | $288.07 | 7 | **KEEP** — Power Washing Near Me (A) |
| **power washing services** | **140** | $11.55–$23.34 | `power washing services` | **SPLIT** — A/Services Near Me *and* B/Residential Pressure Washing | **$29.32** (was $146.60 before 4 clicks were reversed) | **1** | **NEW: Power Washing Services** |
| **pressure washing near me** | **90** | $8.75–$24.66 | `pressure washing near me`, `pressure washing service near me`, `pressure washer near me`, `jet wash near me` | **NONE** | $29.57 | 1 | **NEW: Pressure Washing Near Me** |
| power washing company near me | 260 (shared) | $10.90–$28.32 | `power washing companies near me`, `powerwashing companies near me`, `powerwash company`, `power washer company near me`, `power wash companies near me` | SPLIT across two A groups | $79.59 | 3 | **KEEP** — Power Washing Company Near Me (A) |
| power washing long island | 70 | $10.66–$22.87 | none | DORMANT in permanently-paused `Pressure & Power Washing` | $0.00 | 0 | PHASE 2 |
| house washing near me | 40 | $10.46–$24.75 | `house washing near me`, `house wash near me`, `house power wash`, `house exterior power washing`, `house washing services` | DORMANT in permanently-paused `Soft & House Washing` | $0.00 | 0 | PHASE 2 |
| residential pressure washing near me | 20 | — | `pressure washing near me` (variant) | Residential Pressure Washing Near Me (A + B) | $176.17 | 6 | **CONSOLIDATE** into Pressure Washing Near Me |
| driveway pressure washing | 20 | $0.50–$15.09 | none | Driveway Pressure Washing Near Me (A + B) | $0.00 | 0 | KEEP, low volume |
| **cost / price research** | unmeasured | — | `powerwash cost`, `average cost to power wash a house`, `cost to power wash`, `house wash price`, `house soft wash cost`, `how much does power washing a house cost`, `how much is powerwashing a house`, `power washing costs`, `price to powerwash house` | House Pressure Washing Estimate (A + B) | **$62.18** | 2 | **NO ONE** until a page answers a price question (PLAN-R7 F7) |
| commercial / industrial | unmeasured | — | `gas station pressure washing near me`, `commercial power washing company near me` | Power Washing Near Me PHRASE (A) | $35.31 | 1 | **BLOCKED on Q1** |

**Coverage arithmetic.** The account's 11 serving keyword texts sit against roughly **330
searches/month** of directly-matched demand. The local market runs to roughly **1,100–1,200
BOFU searches/month** (~36–40/day) across the 80-target footprint. **Close-variant matching is
carrying the difference — and routing it badly.**

---

## The core rescue structure

**One campaign. Six ad groups. One canonical intent each. Phrase and Exact only.**

| # | Ad group | Status | Canonical intent | Keywords | Landing page | Demand |
|---|---|---|---|---|---|---:|
| 1 | **Power Washing Near Me** `202870585390` | **KEEP** (rewrite ads) | power washing, local hire | `power washing near me` P + E | `/power-washing-services-islip-west-islip-dix-hills/` | 260/mo |
| 2 | **Power Washing Services Near Me** `202870585430` | **KEEP** | power washing service, local hire | `power washing services near me` P + E | same | 30/mo |
| 3 | **Power Washing Company Near Me** `202870585590` | **KEEP** | power washing company, vendor selection | `power washing company near me` P + E | same | 260/mo (shared) |
| 4 | **Pressure Washing Near Me** | **NEW — paused** | pressure washing, local hire | `pressure washing near me` P + E | `/residential-pressure-washing/` | **90/mo** |
| 5 | **Power Washing Services** | **NEW — paused** | power washing service purchase, no geo qualifier | `power washing services` P + E | `/power-washing-services-islip-west-islip-dix-hills/` | **140/mo** |
| 6 | **Power Washing** | **NEW — paused, higher variance** | power washing, unqualified head term | `power washing` PHRASE only | `/power-washing-soft-washing/` | **880/mo** |

**From 30 ad groups owning 11 serving texts → 6 ad groups owning 14.** Fewer containers, more
demand, one intent each.

### Why ad group 6 uses PHRASE and no EXACT

EXACT on a head term buys only the literal query and forfeits the qualified long tail the group
exists to reach. PHRASE plus the **123 live negative texts** (equipment, DIY, jobs, brands,
rental, repair, and the competitor-vertical fence) is the correct instrument. It is flagged as
the one action in PLAN-R6 with materially different risk, and PLAN-R10 stages its enablement
separately from the safe ones.

### Landing-page mapping rationale

| Ad group | Page | Why |
|---|---|---|
| 1, 2, 3, 5 | `/power-washing-services-islip-west-islip-dix-hills/` | H1 "Power Washing Service In Islip, West Islip & Dix Hills, NY", 35 "power washing" mentions. The intent family lands consistently. **Its city lock is a PLAN-R7 fix.** |
| 4 | `/residential-pressure-washing/` | 21 "pressure washing" mentions, the highest of any page. Best available match. |
| 6 | `/power-washing-soft-washing/` | **The only offer page whose H1 is not locked to three hamlets** — "Power Washing & Soft Washing in Long Island", 17 Long Island mentions. An unqualified head-term query carries no city, so the Long-Island-wide page is the right destination across all 80 targets. |

---

## Every ad group, classified

### Campaign A — Power Washing `24103511039`

| Ad group | ID | Now | Lifetime | Classification |
|---|---|---|---|---|
| Power Washing Near Me | `202870585390` | ENABLED | 81 / 7 / $288.07 | **KEEP BUT REWRITE ADS** — QS 1, ad relevance BELOW_AVERAGE |
| Power Washing Services Near Me | `202870585430` | ENABLED | 94 / 4 / $109.31 | **KEEP** |
| Power Washing Company Near Me | `202870585590` | ENABLED | 11 / 0 / $0.00 | **KEEP** — never clicked, but its intent takes clicks in other groups |
| Power Washing Islip | `202870585630` | ENABLED | 0 / 0 / $0.00 | **PAUSE AFTER REPLACEMENT** — zero impressions ever; 3 of 80 towns |
| Power Washing West Islip | `202870585670` | ENABLED | 1 / 1 / $5.71 | **PAUSE AFTER REPLACEMENT** — one impression is not evidence |
| Power Washing Dix Hills | `202870585830` | ENABLED | 0 / 0 / $0.00 | **PAUSE AFTER REPLACEMENT** |
| Residential Pressure Washing Near Me | `202870585870` | PAUSED | 6 / 0 / $0.00 | **CONSOLIDATE** into ad group 4 |
| House Pressure Washing Estimate | `202870586070` | PAUSED | 3 / 0 / $0.00 | **WEAK INTENT** |
| House Washing Company Near Me | `202870585910` | PAUSED | 2 / 0 / $0.00 | **LOW VOLUME** — no reportable Planner volume for its text |
| Driveway Patio Concrete Washing | `205713509664` | PAUSED | 0 / 0 / $0.00 | **LOW VOLUME** — 4 of its 24 keywords blocked by the `cleaning` negative until PLAN-R2 |
| Driveway Pressure Washing Near Me | `202870586110` | PAUSED | 0 / 0 / $0.00 | **NEEDS MORE DATA** |
| Patio Pressure Washing Near Me | `202870586150` | PAUSED | 0 / 0 / $0.00 | **NEEDS MORE DATA** |
| Soft House Washing Near Me | `202870586310` | PAUSED | 0 / 0 / $0.00 | **NEEDS MORE DATA** |
| Pressure & Power Washing | `205713509704` | PAUSED | 3 / 0 / $0.00 | **DUPLICATE** — 34 keywords across **4** canonical intents. Fails the one-intent test. **Stays permanently paused.** |
| Soft & House Washing | `205713509744` | PAUSED | 1 / 0 / $0.00 | **DUPLICATE** — 28 keywords across **2** canonical intents. **Stays permanently paused.** |

### Campaign B — Power Washing #2 `24145053510`

| Ad group | ID | Now | Lifetime | Classification |
|---|---|---|---|---|
| Residential Pressure Washing Near Me | `198082079423` | ENABLED | 7 / 6 / $176.17 | **PAUSE AFTER REPLACEMENT** — 85.7% CTR; absorbed today's $146.60 event |
| House Pressure Washing Estimate | `198082078983` | ENABLED | 24 / 3 / $104.85 | **WEAK INTENT** — every term it attracted is price research |
| Power Washing Services Near Me | `198082078783` | ENABLED | 13 / 1 / $29.04 | **DUPLICATE** — the one ad group enabled in both campaigns |
| Driveway Pressure Washing Near Me | `198082079023` | ENABLED | 0 / 0 / $0.00 | NEEDS MORE DATA |
| Patio Pressure Washing Near Me | `198082079183` | ENABLED | 0 / 0 / $0.00 | NEEDS MORE DATA |
| Soft House Washing Near Me | `198082078703` | ENABLED | 0 / 0 / $0.00 | NEEDS MORE DATA |
| *(9 further ad groups)* | | PAUSED | 0 / 0 / $0.00 | **REMAIN PAUSED** |

---

## The `estimate` keyword — a specific judgement

`house pressure washing estimate` is the account's longest serving keyword text and its
weakest. It has cost **$104.85 across 3 clicks in campaign B** and attracted, in order:
`powerwash cost` ($40.07), `average cost to power wash a house` ($22.11), `cost to power wash`,
`house wash price`, `how much does power washing a house cost`, `power washing costs`,
`price to powerwash house`.

**Every single one is price research, not an estimate request.** The token "estimate" reads to
Google as semantically adjacent to "cost", "price" and "how much" — so the keyword buys
researchers. And nothing on `/house-pressure-washing-estimate/` answers a price question, so
they bounce.

**This is why a long keyword is not automatically high-intent.** The correct move is
structural, not a negative: either PLAN-R7 F7 gives the page an honest project-range block so
the cluster has somewhere to land, or the keyword is retired (PLAN-R11). Negativing nine
individual cost terms one at a time would treat a symptom.

---

## Execution sequence

| Step | Plan | Mutations | Gate |
|---|---|---:|---|
| 1 | **R3** — CPC ceiling $30 → $22 | 2 | approve now |
| 2 | **R2** — negatives fixed | 8 | approve now |
| 3 | **R6** — create 3 SKAGs **paused** | 14 | after R4 is accepted |
| 4 | **R5** — create 2 RSAs **paused** | 2 | alongside R6 |
| 5 | **readback QA** | 0 | must pass before step 6 |
| 6 | **R10 Stage 1** — enable groups 4 and 5 + the 2 new RSAs | 8 | regenerate fingerprint first |
| 7 | *7 serving days* | — | measure |
| 8 | **R10 Stage 2** — enable ad group 6 (head term) | 3 | separate approval |
| 9 | *7 serving days* | — | measure |
| 10 | **R11** — pause the duplicates, then campaign B | 11 | only after step 9 |

**No step pauses anything before its replacement is proven serving.** Coverage never drops.

---

## What this does not do

- **It does not delete anything.** Every retirement is a PAUSE or an UNLINK.
- **It does not touch budget.** That is PLAN-R12, deliberately isolated, and it recommends no change.
- **It does not change the schedule.** Blocked on SCHED-Q.
- **It does not add Broad match**, Search Partners, Display, Performance Max or AI Max.
- **It does not exclude any demographic.**

---

**STRUCTURE RECOMMENDATION COMPLETE — ZERO MUTATIONS, NOT APPROVED**
