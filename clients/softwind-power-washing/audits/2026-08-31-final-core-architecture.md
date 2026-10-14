# SOFTWIND POWER WASHING — FINAL CORE ARCHITECTURE

**Generated:** 2026-08-31 18:50 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
Identity gate re-run fresh — `Softwind Power Washing - Live` / `1521725229` / manager `false` /
test `false` — **PASS**. Zero external changes. No plan, no fingerprint.

---

## 1. The demand-math error, corrected

**Walter is right, and my figure was wrong.**

I reported "approximately 1,910 of 1,980 monthly searches — 96.5%". The six ad groups sum to
**260 + 90 + 140 + 40 + 880 + 480 = 1,890**. There is no bucket combination that produces 1,910.

**The correct figure for the six-group proposal is 1,890 of 1,980 = 95.45%.**

The cause is exactly the failure mode this project has already recorded once: **a number typed
into a narrative instead of interpolated from the computed data structure.** Every figure below
now comes from `scripts/softwind_0831_demand_reconcile.py`, which derives the buckets, sums them,
and prints the percentage. I did not retype any of them.

### Unique demand buckets — each counted once

| # | Vol/mo | Top-of-page | All keywords sharing this bucket | Covered? | Recommended ad group | Counted once | Overlaps another bucket |
|---:|---:|---|---|---|---|---|---|
| 1 | **880** | $0.58–$14.31 | `power washing` | YES | **Power Washing** | ✔ | no |
| 2 | **480** | $0.30–$10.77 | `pressure washing` | YES | **Pressure Washing** | ✔ | no |
| 3 | **260** | $10.90–$28.32 | `power washing near me` · `power washing company near me` · **`pressure washing services near me`** | YES | **Power Washing** | ✔ | **yes — spans both power and pressure wording** |
| 4 | **140** | $11.55–$23.34 | `power washing service` · **`pressure washing service`** | YES | **Power Washing** | ✔ | **yes — spans both** |
| 5 | **90** | $8.75–$24.66 | `pressure washing near me` | YES | **Pressure Washing** | ✔ | no |
| 6 | **40** | $10.46–$24.75 | `house washing near me` | YES | **House Washing** | ✔ | no |
| 7 | **30** | $10.62–$28.70 | `power washing services near me` | YES | **Power Washing** | ✔ | no |
| 8 | **20** | *no bid data* | `pressure washing company near me` · `residential pressure washing near me` | YES | **Pressure Washing** | ✔ | no |
| 9 | **20** | $13.49–$32.86 | `house power washing near me` · **`house pressure washing near me`** | YES | **House Washing** | ✔ | **yes — spans both** |
| 10 | **10** | $15.09–$41.58 | `soft washing near me` | YES | Soft House Washing *(exists)* | ✔ | no |
| 11 | **10** | *no bid data* | `driveway power washing near me` · `driveway pressure washing near me` · `exterior house washing near me` | YES | Driveway Pressure Washing *(exists)* | ✔ | see caveat |
| 12 | **0** | *no bid data* | `concrete pressure washing near me` · `patio pressure washing near me` | YES | Patio Pressure Washing *(exists)* | ✔ | see caveat |

### **UNIQUE DEMAND TOTAL: 1,980 / month across 12 buckets**

**A methodological caveat I have to state.** Buckets 8, 11 and 12 carry **no bid data**
($0.00/$0.00). Grouping by *(volume, low bid, high bid)* therefore collapses unrelated keywords
that merely share a volume and a missing bid range. **Those three are not confirmed shared
pools** — they are "10/mo, no data" keywords sitting in the same slot. Buckets 1–7, 9 and 10
have real bid data and **are** confirmed shared pools.

**1,950 of 1,980 (98.5%) sits in buckets with confirmed bid evidence.** The remaining 30/mo is
in the unconfirmed group. This does not change any recommendation — those buckets total 30
searches a month — but it is the difference between measured and inferred.

---

## 2. Intra-campaign overlap — worse than the cross-campaign problem

**19 of 55 search terms served in more than one ad group. Fourteen of those nineteen were
multiple ad groups inside the SAME campaign.**

| | Impressions | Valid clicks | Spend |
|---|---:|---:|---:|
| Terms served by more than one ad group | **66.1%** (146/221) | **73.3%** (11/15) | **72.8%** ($338.74/$465.27) |
| *(for comparison)* cross-campaign duplication only | 16.7% | 26.7% | 24.8% |

**Fragmenting one intent across several SKAGs is doing nearly three times more damage than the
duplicate campaign.** This is the direct empirical answer to Walter's question, and it inverts
the priority I had implied.

### Routing-conflict matrix — measured, not hypothesised

| Keyword | Search terms it actually matched | Other ad groups eligible for the same searches | Landing page | RSA angle | **Conflict risk 0–5** |
|---|---|---|---|---|---:|
| `power washing near me` E+P | `power washing`, `pressure washing`, `power wash near me`, `powerwashing near me`, `jet wash near me`, `power washer near me`, `house washing services`, `pressure washing service near me`, `house washing near me` | Power Washing Services Near Me · Power Washing Company Near Me · Residential Pressure Washing | `/power-washing-services-islip…/` | local power washing, free quote | **5** |
| `power washing services near me` E+P | `power washing`, `power washing companies near me`, `powerwashing near me`, `pressure washing near me`, `power wash near me`, `deck cleaning services near me` | Power Washing Near Me · Power Washing Company Near Me | same page | near-identical | **5** |
| `power washing company near me` E+P | `power washing companies near me`, `powerwashing companies near me`, `power washing service near me`, `pressure washing near me` | Power Washing Near Me · Power Washing Services Near Me | same page | near-identical | **5** |
| `power washing` (proposed, Phrase) | would match all of the above | Power Washing Near Me · Services · Company | same page | same | **5** |
| `power washing service` (proposed) | `power washing service near me`, `power washing services` | Power Washing Near Me · Services Near Me | same page | same | **5** |
| `pressure washing near me` (proposed) | `pressure washing near me`, `pressure washing service near me`, `pressure washer near me` | **already matched by `power washing near me` EXACT** | `/residential-pressure-washing/` | pressure washing | **4** |
| `pressure washing` (proposed, Phrase) | `pressure washing` — **already matched by `power washing near me` EXACT for $59.82** | Power Washing Near Me | `/residential-pressure-washing/` | pressure washing | **4** |
| `residential pressure washing near me` E+P | `power wash near me`, `pressure washing near me`, `power washing services`, `house washing near me`, `powerwash near me` | Power Washing Near Me · Services Near Me | `/residential-pressure-washing/` | residential | **5** |
| `house washing near me` (proposed) | `house washing near me`, `house washing services`, `house wash near me` | Power Washing Near Me · Services Near Me | `/house-washing-company/` | house washing | **3** |
| `house pressure washing near me` (proposed) | not yet observed | House Washing · Pressure Washing | `/house-washing-company/` | house washing | **2** |
| `soft washing near me` / `soft house washing near me` | none observed | Power Washing Near Me (via `soft wash power washing near me`) | `/soft-house-washing/` | gentle siding wash | **2** |
| `driveway pressure washing near me` | none observed | — | `/driveway-pressure-washing/` | driveway | **1** |
| `patio pressure washing near me` | none observed | — | `/patio-power-washing/` | patio | **1** |
| `pressure washing services near me` | *bucket 3 — same pool as `power washing near me`* | Power Washing | — | — | **5 — do not use** |

**Conflict risk 5 on every one of the power-family keywords.** They are not separable — they are
one intent wearing different words.

---

## 3–4. Distinct-intent test and structure comparison

| Structure | Ad groups | Kw texts | Unique demand | Coverage | Bucket collisions | Routing control | Data concentration | RSA relevance | LP relevance | CTR | CPC | CVR | Complexity |
|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---|---|
| **Six-group** (previous) | 6 | 6 | 1,890 | **95.45%** | none | **POOR** — conflict risk 5 across the power family | **Poor** — 6 containers, ~1 click/day | Low gain — near-identical ads | Good | ↔ | ↑ (self-competition) | ↔ | Medium |
| **Three-group core** | 3 | 11 | **1,960** | **98.99%** | none, once bucket 3 is assigned to Power | **STRONG** | **Best** | Genuinely distinct per group | Good | **↑** | **↓** | **↑** | **Low** |
| Three core + 3 existing micro | 6 | 16 | 1,980 | 100% | none material | Strong | Good | Distinct | Good | ↑ | ↓ | ↑ | Low |
| Four-group (micro merged) | 4 | 16 | 1,980 | 100% | none | Strong | Good | One group mixes 4 surfaces | **Weakened** | ↔ | ↓ | ↔ | Low |

### Applying the distinct-intent test

**A. Power Washing Core — CONSOLIDATE.** `power washing`, `power washing near me`,
`power washing service`, `power washing services near me`, `power washing company near me` share
**the same buyer intent, the same landing page, near-identical ads, and — for three of them —
the same Planner bucket.** They already cannibalise each other at conflict risk 5. **One focused
single-intent ad group.**

**B. Pressure Washing Core — CONSOLIDATE, and keep separate from A.** `pressure washing`,
`pressure washing near me`, `residential pressure washing near me` share one intent. They stay
**separate from A** because they pass the test on three counts: **distinct Planner buckets**
(480 and 90 are theirs alone), **a distinct landing page** (`/residential-pressure-washing/`,
21 pressure-washing mentions), and **a distinct RSA angle** — matching the searcher's own word.

**C. House Washing — KEEP SEPARATE.** Distinct buckets (40 + 20), a purpose-built page with 24
house-washing mentions, and a distinct surface intent.

**D. Soft / Driveway / Patio — LEAVE EXACTLY AS THEY ARE.** They pass on landing page and
surface intent but **fail on measurable demand** — 10, 10 and 0 per month. They already exist,
are enabled, have purpose-built pages and two RSAs each, and have taken **zero impressions and
zero spend**. Building them is unnecessary; retiring them buys nothing. **No work either way.**

**This is not a mixed legacy ad group.** The retired `Pressure & Power Washing` container held
34 keywords across **four** canonical intents. Power Washing Core holds 5 texts across **one**.

---

## 5. Head-term safety — re-verified

| Query | Local SERP composition | Verdict |
|---|---|---|
| **`power washing` + Long Island** | 100% local service providers — Island Wide, Pressure Wash Long Island, Long Island Power Washing, Cleanfellas, McMorris, Super Clean Machine, Rolling Suds. **Zero** equipment, retail, DIY or business-startup content | **SAFE** |
| **`pressure washing` + Long Island** | same provider set | **SAFE** |
| **`pressure washer`** (bare noun) | **100% equipment retail** — Ace Hardware, Tractor Supply, Lowe's, Harbor Freight, Consumer Reports buying guide, Wikipedia. **Zero** service providers | **DO NOT USE** |

**The distinguishing token is grammatical: "washing" is the service, "washer" is the machine.**

### Existing negatives protecting the head terms — verified live, 132 per campaign

`power washer for sale` · `power washer rental` · `power washer parts` · `power washer repair` ·
`pressure washer for sale` · `pressure washer rental` · `pressure washer parts` ·
`pressure washer repair` · `pressure washing machine` · `power washing equipment` (all BROAD) ·
brands `harbor freight` · `home depot` · `lowes` · `ryobi` · `karcher` · `simpson` ·
DIY/startup `diy` · `how to` · `how to start` · `training` · `tutorial` · `course` ·
`certification` · `business plan` · employment `job` · `jobs` · `hiring` · `career` · `salary` ·
`employment` · plus `rent` · `rental` · `used` · `for sale` · `parts` · `machine` · `manual`.

**The fence is already in place and is comprehensive.** Both head terms are protected against
every category the brief names.

| Head term | Recommendation |
|---|---|
| `power washing` | **PHRASE only — staged test.** Exact would buy only the literal query and forfeit the qualified long tail. Enable in a second stage, 7 serving days after the core. |
| `pressure washing` | **PHRASE only — staged test.** Same reasoning. |
| `pressure washer` | **NOT USED.** Remains fenced. |

---

## 6. Cross-negatives — two required, both inside one campaign

Only two are recommended, and both have a clear routing purpose with a measured blocking risk of
zero. **Nothing is created here.**

| # | Negative | Match | Ad group receiving it | Query it routes | Valid demand it could block | Essential? |
|---|---|---|---|---|---|---|
| 1 | `pressure washing` | PHRASE | **Power Washing** | Sends pressure-worded queries to Pressure Washing. **Proven necessary:** `pressure washing` already matched `power washing near me` EXACT and took **$59.82**, the account's biggest single term | **None.** Tested against all 5 Power Washing keyword texts — not one contains "pressure washing" | **ESSENTIAL** |
| 2 | `power washing` | PHRASE | **Pressure Washing** | Mirror. Stops `power washing` Phrase-matching into the Pressure group | **None.** Tested against all 3 Pressure Washing texts — not one contains "power washing" | **ESSENTIAL** |
| 3 | `house washing` | PHRASE | Power Washing · Pressure Washing | Routes house queries to House Washing | **None** — "house washing" is not contiguous in `house power washing near me` | **OPTIONAL** — low value, add only if house queries leak |

**Not proposed, and deliberately so:** `near me`, `service`, `services`, `company`, `quote`,
`estimate`, `cost`, `price`. Every one is a protected token under Green Marketing policy, and
each appears inside keywords the account wants to keep.

---

## 7. Final recommended structure — campaign `24103511039` "Power Washing"

# THREE CORE AD GROUPS

**1,960 of 1,980 unique monthly searches — 98.99% — with 11 keyword texts (15 keyword objects).**
Today's 21 serving keywords across 12 ad groups reach roughly 330/mo.

### Ad group 1 — **Power Washing**

- **Canonical intent:** power washing service, purchase intent
- **Phrase:** `power washing` · `power washing near me` · `power washing service`
- **Exact:** `power washing near me` · `power washing service` · `power washing services near me` · `power washing company near me`
- **Unique demand: 1,310/mo** (buckets 1, 3, 4, 7)
- **Landing page:** `/power-washing-services-islip-west-islip-dix-hills/`
- **RSA angle:** local power washing, surface-specific method, free quote
- **Cross-negative required:** `pressure washing` PHRASE
- **Exists?** Partly — `Power Washing Near Me` `202870585390` can be the base
- **Create paused?** New keywords added to the existing group, paused for QA
- **Replaces:** `Power Washing Services Near Me` `202870585430` · `Power Washing Company Near Me` `202870585590`

### Ad group 2 — **Pressure Washing**

- **Canonical intent:** pressure washing service, purchase intent
- **Phrase:** `pressure washing` · `pressure washing near me`
- **Exact:** `pressure washing near me` · `residential pressure washing near me`
- **Unique demand: 590/mo** (buckets 2, 5, 8)
- **Landing page:** `/residential-pressure-washing/`
- **RSA angle:** pressure washing wording, hard surfaces, free quote
- **Cross-negative required:** `power washing` PHRASE
- **Exists?** **No — must be created**
- **Create paused?** **Yes**
- **Replaces:** `Residential Pressure Washing Near Me` `198082079423` (campaign B)

### Ad group 3 — **House Washing**

- **Canonical intent:** whole-house exterior washing
- **Phrase:** `house washing near me`
- **Exact:** `house washing near me` · `house pressure washing near me` · `house power washing near me`
- **Unique demand: 60/mo** (buckets 6, 9)
- **Landing page:** `/house-washing-company/`
- **RSA angle:** siding, trim and fences; gentle soft washing; free quote
- **Cross-negative required:** none essential
- **Exists?** `House Washing Company Near Me` `202870585910` exists but is paused with a different keyword text
- **Create paused?** **Yes**
- **Replaces:** the dormant `house washing near me` inside the permanently paused `Soft & House Washing`

### Left exactly as they are — no work, no retirement

`Soft House Washing Near Me` `198082078703` · `Driveway Pressure Washing Near Me` `198082079023`
· `Patio Pressure Washing Near Me` `198082079183`. Enabled, purpose-built pages, two RSAs each,
**zero impressions and zero spend**. 20/mo between them. They will migrate to campaign A during
consolidation; nothing is built or retired for them now.

**Head-term prerequisite:** `power washing` and `pressure washing` Phrase keywords should be
enabled **only after PLAN-R7 widens the landing-page H1s** from three hamlets to Long Island /
Nassau & Suffolk. The broadest query in the account should not land on the most narrowly
city-locked page.

---

## 8. Duplicate-campaign transition

**Do not rename "Preassure Washing" now.** If the final structure is one campaign, spending a
mutation to correct the spelling of a campaign that is about to be retired buys nothing. Fix it
only if consolidation is deferred.

**Safe sequence — no step performed:**

1. Create the missing resources **paused** in `24103511039` — ad groups 2 and 3, the new keywords for ad group 1, and their RSAs.
2. **Read back and complete QA** — status PAUSED, policy APPROVED, correct Final URLs, character limits re-validated against the as-built copy, no keyword blocked by any of the 132 live negatives.
3. **Fix measurement (PLAN-R1) and the landing-page problems (PLAN-R7)** — both zero Google Ads mutations, both prerequisites for judging anything that follows.
4. **Enable the replacement resources under a separate approval**, core groups first, head terms 7 serving days later.
5. **Verify delivery** — impressions, search terms, and that the two cross-negatives are routing as intended.
6. **Pause the displaced ad groups** — `202870585430`, `202870585590`, `198082078783`, `198082079423`, `198082078983`, and the three city SKAGs.
7. **Pause campaign `24145053510` last**, after its unique intents are proven live in `24103511039`.

---

## 9. Effect on the $12 CPC test

**Recommendation: stop treating $12 as a test, and apply it to both campaigns now as a
defensible default setting.**

The reasoning is a change from what I said last round, and it follows from this review's
findings:

- A clean 10-serving-day CPC read would need ~12 calendar days of frozen structure. **The
  restructure is worth more than the measurement.** Consolidation moves demand coverage from
  ~330/mo to 1,960/mo and removes fragmentation touching **73.3% of clicks**. Freezing that for
  two weeks to protect a CPC read is the wrong trade.
- **$12 does not need a test to be defensible.** It clears the top-of-page low on 98.2% of local
  demand; $10 clears 15.8%; $18 and $22 add almost nothing. That case rests on Planner evidence,
  not on an experiment.
- Applying it to **both** campaigns removes the Ad Rank asymmetry that blocked PLAN-R3A. Two
  mutations, one field each, one-write rollback.
- The account is currently paying **$29.04–$29.72 on every post-ceiling click** with zero
  recorded leads. Every day of delay is real money.

| Question | Answer |
|---|---|
| Apply to both campaigns temporarily before consolidation? | **Yes — this is the recommendation.** |
| Wait until the single-campaign structure is live? | **No.** ~3–5 weeks of overpaying, to buy attribution the restructure will disturb anyway. |
| Apply only to `24103511039` after consolidation? | **That is where it ends up** — the survivor inherits the ceiling. Not where it should start. |

**Risk that the CPC test delays higher-priority work: HIGH if run as a frozen test, LOW if
applied as a setting.** PLAN-R1 (measurement) and PLAN-R7 (landing pages) are both zero Ads
mutations and conflict with nothing — they should run in parallel starting now.

**Measure the ceiling properly later**, after consolidation, when one campaign and clean
attribution make it readable.

**No PLAN-R3B has been created and no fingerprint generated.**

---

## 10. Confirmation

Zero external changes. `SELECT` statements and `GenerateKeywordIdeas` only — no mutate-capable
service client instantiated. No campaign renamed, no resource created, enabled, paused or
modified. PLAN-R3A `B57E427D07C5` remains BLOCKED with no approval command.

Evidence: `snapshots/demand-reconcile-2026-08-31T185021.json` ·
`snapshots/planner-architecture-2026-08-31.json` ·
`scripts/softwind_0831_demand_reconcile.py`
