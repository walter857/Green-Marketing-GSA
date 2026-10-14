# SOFTWIND POWER WASHING — STRICT SKAG TRANSITION AND ROUTING PLAN

**Generated:** 2026-08-31 19:37 America/New_York · Account `1521725229` · **READ + DRAFT ONLY**
Identity gate re-run fresh — `Softwind Power Washing - Live` / `1521725229` / manager `false` /
test `false` — **PASS**. Zero external changes. No plan, no fingerprint, no approval command.

---

## 1. The six active intents — confirmed against the saved architecture

Walter's list and the saved FINAL CORE ARCHITECTURE **agree on the same six intents.** The only
difference is how much *work* each needs, and that difference matters for sequencing:

| # | Ad group | Status in the saved architecture | Work required |
|---|---|---|---|
| 1 | **Power Washing** | Core — consolidates 3 existing power SKAGs | Expand `202870585390`; retire 2 siblings |
| 2 | **Pressure Washing** | Core — **does not exist** | **Create paused** |
| 3 | **House Washing** | Core — **does not exist** in this form | **Create paused** |
| 4 | **Soft Washing** | Exists live as `198082078703`, 0 impressions | **Negatives only** |
| 5 | **Driveway Pressure Washing** | Exists live as `198082079023`, 0 impressions | **Negatives only** |
| 6 | **Patio Pressure Washing** | Exists live as `198082079183`, 0 impressions | **Negatives only** |

The saved architecture said "3 core + leave 3 micro groups alone." Under a strict SKAG routing
requirement, **all six are routing participants** — the three micro groups need their sibling
negatives even though they need no build. That is the reconciliation.

---

## 2. Keyword ownership — one owner per text, no exceptions

**19 unique positive keyword texts. Phrase and Exact of the same text count as ONE routing text.**

| Owner ad group | Keyword text | Positive match types | Demand | Landing page |
|---|---|---|---:|---|
| **Power Washing** | `power washing` | PHRASE | 880 | `/power-washing-services-islip…/` |
| | `power washing near me` | PHRASE + EXACT | 260 | |
| | `power washing service` | PHRASE + EXACT | 140 | |
| | `power washing services near me` | EXACT | 30 | |
| | `power washing company near me` | EXACT | *(260 bucket)* | |
| **Pressure Washing** | `pressure washing` | PHRASE | 480 | `/residential-pressure-washing/` |
| | `pressure washing near me` | PHRASE + EXACT | 90 | |
| | `residential pressure washing near me` | EXACT | 20 | |
| **House Washing** | `house washing near me` | PHRASE + EXACT | 40 | `/house-washing-company/` |
| | `house pressure washing near me` | EXACT | 20 | |
| | `house power washing near me` | EXACT | *(20 bucket)* | |
| | `exterior house washing near me` | EXACT | *(10 bucket)* | |
| **Soft Washing** | `soft washing near me` | EXACT | 10 | `/soft-house-washing/` |
| | `soft house washing near me` | PHRASE + EXACT | *(10 bucket)* | |
| **Driveway Pressure Washing** | `driveway pressure washing near me` | PHRASE + EXACT | 10 | `/driveway-pressure-washing/` |
| | `driveway power washing near me` | EXACT | *(10 bucket)* | |
| **Patio Pressure Washing** | `patio pressure washing near me` | PHRASE + EXACT | 0 | `/patio-power-washing/` |
| | `patio power washing near me` | EXACT | 10 | |
| | `concrete pressure washing near me` | EXACT | *(0 bucket)* | |

**Structural duplicates to retire after replacements are live** — these are the same text owned
by more than one live ad group today:

| Text | Currently in | Future owner |
|---|---|---|
| `power washing services near me` | `202870585430` (Power Washing) **and** `198082078783` (Preassure Washing) | Power Washing |
| `power washing company near me` | `202870585590` | Power Washing |
| `residential pressure washing near me` | `202870585870` (paused) **and** `198082079423` (live) | Pressure Washing |

---

## 3. The routing negatives — 127 ad-group-level criteria

| Layer | Count | Match type | Purpose |
|---|---:|---|---|
| **Sibling EXACT mirror** | **95** | EXACT | Every owner text negatived in all 5 sibling groups (19 × 5) |
| **Observed close-variant supplement** | **20** | EXACT | 18 real queries from search-term history that the mirror does not cover |
| **Modifier routing negatives** | **12** | PHRASE | Family-level routing where collision-safe |
| **TOTAL** | **127** | | |

### Per ad group

| Ad group | EXACT | PHRASE | Total |
|---|---:|---:|---:|
| Power Washing | 28 | 3 | **31** |
| Pressure Washing | 21 | 3 | **24** |
| Driveway Pressure Washing | 17 | 2 | **19** |
| Patio Pressure Washing | 16 | 2 | **18** |
| Soft Washing | 17 | 1 | **18** |
| House Washing | 16 | 1 | **17** |
| | | | **127** |

Mirror arithmetic: 19 texts × 5 sibling groups = **95 raw**, **0 duplicates removed** (each text
has exactly one owner, so no text is ever mirrored twice into the same group), **95 final**.

### The 12 approved modifier negatives

| Negative | Match | Placed in | Protects |
|---|---|---|---|
| `pressure washing` | PHRASE | Power Washing · Soft Washing | Pressure Washing |
| `power washing` | PHRASE | Pressure Washing | Power Washing |
| `house washing` | PHRASE | Power Washing · Pressure Washing · Driveway · Patio | House Washing |
| `soft wash` | PHRASE | Power Washing · Pressure Washing · House Washing · Driveway · Patio | Soft Washing |

### The 23 modifier candidates REJECTED by collision test

Exactly the traps Walter named, caught programmatically:

| Rejected | Reason |
|---|---|
| `power washing` PHRASE in **House Washing** | blocks its own `house power washing near me` |
| `pressure washing` PHRASE in **House Washing** | blocks its own `house pressure washing near me` |
| `power washing` PHRASE in **Driveway** | blocks its own `driveway power washing near me` |
| `pressure washing` PHRASE in **Driveway** | blocks its own `driveway pressure washing near me` |
| `power washing` PHRASE in **Patio** | blocks its own `patio power washing near me` |
| `pressure washing` PHRASE in **Patio** | blocks `patio pressure washing near me` and `concrete pressure washing near me` |
| `house washing` PHRASE in **Soft Washing** | blocks its own `soft house washing near me` |
| `power washing` PHRASE in **Soft Washing** | blocks the intended query `soft wash power washing near me` |
| `service` · `services` BROAD, anywhere | **protected token** under Green Marketing policy |
| `company` BROAD, anywhere | **protected token** |

`near me`, `quote`, `estimate`, `cost` and `price` were never proposed — all protected.

---

## 4. Collision test — 423 assertions, zero collisions

Every one of the 127 proposals was tested against **every positive keyword in its receiving ad
group** and **every historical search term intended for that ad group**.

| Assertion | Result |
|---|---|
| Own positive keywords blocked | **0** |
| Intended close-variant searches blocked | **0** |
| Landing-page-aligned queries blocked | **0** |
| Approved BOFU demand accidentally excluded | **0** |

**Why the EXACT mirror is collision-free by construction:** negative EXACT blocks only the
literal query text, and every text has exactly one owner — so a mirrored negative can never
collide with the receiving group's own keywords. The only genuine collision risk sits in the
PHRASE modifiers, and 23 of 35 were rejected for exactly that.

---

## 5. Routing simulation

| | Result |
|---|---:|
| Routing success **before** negatives | **16 / 24 = 66.7%** |
| Routing success **after** negatives | **24 / 24 = 100.0%** |
| Residual risks flagged by the simulation | **0** |

### The 100% is a ceiling, not an expectation — and I tested my own model to prove it

The simulation is only as good as its close-variant model. I ran that model against **four
matches Google actually made in this account**:

| Google actually matched | To keyword | My model predicts |
|---|---|---|
| `power washing services` | `residential pressure washing near me` [EXACT] | **NO** |
| `powerwash cost` | `house pressure washing estimate` [EXACT] | **NO** |
| `deck cleaning services near me` | `power washing services near me` [PHRASE] | **NO** |
| `pressure washing` | `power washing near me` [EXACT] | **NO** |

**My model fails to predict 4 of 4 real matches.** Google's close-variant behaviour in this
account is looser than any reasonable simulation.

**The structural consequence — and it is the most important line in this document:**

> **Negative keywords do not match close variants. Positive keywords do.**
>
> An EXACT negative blocks only the literal query text. So a query Google routes into the wrong
> ad group *via a loose close variant* will **not** be blocked by the exact mirror unless that
> exact query string has already been observed and negatived.

**Strict SKAG routing is therefore achievable for known queries and cannot be guaranteed for
unseen ones.** The 127 negatives close every gap the account has actually demonstrated. New
gaps will open as new queries appear, and the only defence is a standing search-term review that
adds each rogue query as an EXACT negative in the group that wrongly received it.

**RESIDUAL CLOSE-VARIANT RISK applies to every ad group, permanently.** It is not eliminable by
negatives at any match type without blocking valid demand — the rejected modifier list above is
the proof of what over-reaching costs.

---

## 6. Universal negatives stay separate from routing negatives

| Category | Where it lives | Count today | Purpose |
|---|---|---:|---|
| **A. Universal / out-of-scope** | **Campaign level** — both campaigns | **132 per campaign** | jobs, training, DIY, equipment, rental, `pressure washer repair`, brands, competitor verticals, roof/gutter |
| **B. SKAG routing** | **Ad-group level only** | **127 proposed** | send a qualified query to the correct ad group |

**These must never be merged.** A routing negative placed at campaign level would block the
query for the intended owner too — it would defeat its own purpose. Every routing negative in
the matrix CSV carries its `owner_ad_group`, so the intended destination is always explicit.

---

## 7. Two routing models

### A. FINAL-STATE MATRIX — after consolidation into `24103511039`

All six ad groups live in one campaign. **127 ad-group-level negatives**, exactly as tabulated
above. No cross-campaign negatives exist, because there is only one campaign.

### B. TRANSITION MATRIX — while `24145053510` "Preassure Washing" is still enabled

**Deliberately minimal. Do not mirror hundreds of negatives across two campaigns.**

During the transition the second campaign is being retired, not optimised. Building a full
cross-campaign mirror would mean creating ~127 more criteria on a campaign that is about to be
paused — pure waste, and a large surface to unwind.

**The transition protection is instead:**

1. **Sequencing, not negatives.** Replacement owners go live *before* any displaced ad group is
   touched, and the displaced ad groups are paused promptly afterwards. The overlap window is
   measured in days, not weeks.
2. **Three temporary EXACT negatives only** — in campaign B's three still-serving ad groups, for
   the texts campaign A's new owners will claim:
   - `[power washing services near me]` in `198082078783`
   - `[residential pressure washing near me]` in `198082079423`
   - `[house pressure washing estimate]` — *not needed;* that ad group is being retired for
     intent reasons, not routing reasons.
3. Everything else waits for step 8.

**Accepted residual during transition:** campaign B may still absorb some shared close-variant
traffic for a few days. That is cheaper than 127 throwaway criteria, and it is bounded by the
sequence.

---

## 8. Transition sequence — no step performed

**The governing rule: never add a routing negative before its replacement owner ad group is live
and verified. Blocking traffic before its new owner is active is prohibited.**

| Step | Action | Gate |
|---:|---|---|
| 1 | **Create paused** in `24103511039`: ad groups *Pressure Washing* and *House Washing*, new keywords for *Power Washing*, and 2 RSAs per new group | separate approval |
| 2 | **Read back and QA** every created resource — status PAUSED, policy APPROVED, correct Final URL, character limits re-validated against as-built copy, no keyword blocked by the 132 live campaign negatives | must pass before step 4 |
| 3 | **Fix measurement (PLAN-R1) and landing pages (PLAN-R7)** — both zero Ads mutations | prerequisite for judging anything |
| 4 | **Enable the replacement owner ad groups** — core first; head-term keywords 7 serving days later, and only after PLAN-R7 widens the H1s | separate approval |
| 5 | **Verify every owner ad group is eligible and serving** — impressions present, `primary_status` ELIGIBLE, search terms arriving | must pass before step 6 |
| 6 | **Add the 127 routing negatives** — ad-group level only | separate approval, **only after step 5 passes** |
| 7 | **Verify search-term routing** — re-run the ownership matrix; every observed query lands in its intended owner | must pass before step 8 |
| 8 | **Pause displaced ad groups** — `202870585430`, `202870585590`, `198082078783`, `198082079423`, `198082078983`, and the three city SKAGs | separate approval |
| 9 | **Pause campaign `24145053510` LAST** | separate approval |

**Ongoing after step 9:** a standing search-term review — weekly at first — adding each rogue
query as an EXACT negative in the group that wrongly received it. This is the only durable
answer to residual close-variant risk.

---

## 9. Does this meet the strict SKAG requirement?

**Yes, to the limit of what Google's matching allows — and the limit is real.**

| Requirement | Status |
|---|---|
| Every ad group owns one canonical intent | **MET** — 6 groups, 6 intents |
| Every positive text has exactly one owner | **MET** — 19 texts, no text owned twice |
| Phrase + Exact of a text counted as one routing text | **MET** |
| Every owner text mirrored as negative EXACT into all siblings | **MET** — 95 criteria |
| Documented collisions exempted rather than forced | **MET** — 23 modifier candidates rejected with named collisions; 0 mirror exemptions needed |
| Ad-group level, not account or campaign level | **MET** |
| Routing negatives kept separate from universal negatives | **MET** |
| Self-blocking collisions | **ZERO** across 423 assertions |
| Perfect routing guaranteed | **NO — and it cannot be.** Negatives do not close-variant; positives do. |

---

**STRICT SKAG CROSS-NEGATIVE MATRIX COMPLETE — ZERO EXTERNAL CHANGES MADE**
