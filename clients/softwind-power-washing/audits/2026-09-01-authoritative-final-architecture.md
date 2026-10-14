# SOFTWIND POWER WASHING — AUTHORITATIVE FINAL ARCHITECTURE

**Account** `Softwind Power Washing - Live` · `1521725229` · **Power Washing**
**Generated** 2026-09-01 America/New_York · **READ + DRAFT · zero external changes**

**This supersedes the architecture sections of PLAN-R4, PLAN-R6 and the 2026-08-31 memo §14.**
It is the single authoritative final state. Where earlier reports conflict, this file wins.

---

## 1. Campaign count — ONE

**Surviving campaign `24103511039`, final name "Power Washing", unchanged.**

`24145053510` ("Pressure Washing", renamed by the owner 2026-09-01 14:21 via the web UI) is
**retired last**, only after every replacement is created, read back, approved, enabled and verified
serving. **It must not be paused early** — it is currently half the account's live delivery.

> **One open owner question.** Walter corrected the spelling of the campaign the plan retires. The
> technical recommendation is still one campaign, because the two share a Planner demand bucket, 80
> locations, a schedule, a 132-negative fence, conversion goals, an asset set and a duplicated ad
> group. If the rename signals an intent to keep two campaigns, that is a business preference that
> overrides the recommendation and changes Stages 3–7. It does not block Stage 1.

---

## 2. The single biggest finding of this run

# Every one of the six final ad groups already exists inside the surviving campaign.

**Zero ad groups need to be created.** Five are sitting paused in `24103511039` right now with the
correct names and, in four cases, the correct keywords already loaded.

| # | Final intent group | Ad group ID | Current name | Current status |
|---|---|---|---|---|
| 1 | **Power Washing** | `202870585390` | Power Washing Near Me | **ENABLED** |
| 2 | **Pressure Washing** | `202870585870` | Residential Pressure Washing Near Me | PAUSED |
| 3 | **House Washing** | `202870585910` | House Washing Company Near Me | PAUSED |
| 4 | **Soft Washing** | `202870586310` | Soft House Washing Near Me | PAUSED |
| 5 | **Driveway Pressure Washing** | `202870586110` | Driveway Pressure Washing Near Me | PAUSED |
| 6 | **Patio Pressure Washing** | `202870586150` | Patio Pressure Washing Near Me | PAUSED |

**The build collapses from "create a campaign structure" to "add 28 keywords and 12 ads to ad groups
that already exist."** That is dramatically cheaper, lower-risk and faster than any earlier plan
assumed.

**Ad group names are kept as they are.** Renaming six groups costs six mutations and changes no
performance. The container name is cosmetic; ownership is enforced by keywords and negatives. Rename
is deferred as optional housekeeping.

---

## 3. Structure type — SINGLE-INTENT, not literal SKAG

The account takes roughly **one valid click per serving day.** Nineteen literal one-keyword ad groups
would give each group one click every twenty days, and Quality Score, ad rotation and every
optimisation signal operate at ad-group level.

**You do not need an ad group to measure a keyword.** `keyword_view` reports impressions, clicks,
cost, CTR, average CPC and all three Quality Score components per keyword — proven in this very run,
which is where the QS 2 / QS 3 / QS 5 evidence came from. Splitting buys ad differentiation and
routing control, not measurement.

**Walter's strict ownership requirement is preserved in full** — every keyword text has exactly one
owner ad group, and 95 sibling EXACT negatives enforce it. Ownership is enforced by negatives, not
by fragmentation.

Groups are split only where **buying intent, landing page, ad message, service requested and demand
bucket** genuinely differ. They are not split on wording differences that share all five.

---

## 4. Reconciling 11 vs 19 vs 14 vs 15 — there is no conflict

Earlier reports quote different keyword numbers. They count different things:

| Figure | What it actually counted | Status |
|---|---|---|
| **11 canonical texts** | Texts carrying **reportable local volume** after bucket dedup (2026-08-31 memo §6, "98.99% across 11 core texts") | Correct, partial denominator |
| **19 canonical texts** | **All** final owned texts, including zero- and shared-bucket texts (memo §14) | **AUTHORITATIVE** |
| 14-keyword / 15-object proposals | Earlier three-group drafts before the six-group structure was settled | **SUPERSEDED** |

**Authoritative: 19 canonical texts, 38 keyword objects (Phrase + Exact for every text).**
11 of the 19 carry reportable volume; 8 sit in shared buckets or have no reportable demand but are
retained because they are real buying phrases with exactly one owner.

**Deduped local demand: ~2,000 searches/month** across the 80-target footprint. The 2026-08-31 memo
stated 1,980 using a slightly different bucket assignment for `patio power washing near me`. The
difference is 20 searches/month — immaterial, and both figures are stated rather than silently
reconciled.

---

## 5. Final keyword inventory — 19 texts, one owner each

Full evidence per keyword — demand, competition, top-of-page bids, historical impressions/clicks/
cost, Quality Score, BOFU score, equipment ambiguity, landing-page match — is in
`2026-09-01-authoritative-keyword-inventory.csv` (58 rows: 38 active objects + 20 reviewed-and-
rejected texts).

| Owner ad group | Texts | Objects | Add paused | Reuse |
|---|---|---:|---:|---:|
| Power Washing | `power washing` · `power washing near me` · `power washing service` · `power washing services near me` · `power washing company near me` | 10 | 8 | 2 |
| Pressure Washing | `pressure washing` · `pressure washing near me` · `residential pressure washing near me` | 6 | 4 | 2 |
| House Washing | `house washing near me` · `house pressure washing near me` · `house power washing near me` · `exterior house washing near me` | 8 | 8 | 0 |
| Soft Washing | `soft house washing near me` · `soft washing near me` | 4 | 2 | 2 |
| Driveway Pressure Washing | `driveway pressure washing near me` · `driveway power washing near me` | 4 | 2 | 2 |
| Patio Pressure Washing | `patio pressure washing near me` · `patio power washing near me` · `concrete pressure washing near me` | 6 | 4 | 2 |
| **TOTAL** | **19 texts** | **38** | **28** | **10** |

**Match types: Phrase + Exact for every owned text. No exceptions, and none needed.** No Broad Match.

**Validated programmatically:** every text has exactly one owner; no text has two final owners.

### Reviewed and rejected — 20 texts

Every family the brief asked to review was scored. Highlights:

- **Bucket collapse (removed, not negatived):** `power washing services`, `pressure washing
  services`, `pressure washing service`, `pressure washing services near me`, `pressure washing
  company near me`, `house washing company near me`. Each shares a Planner volume bucket with a text
  already owned. Adding both double-counts demand and creates sibling self-competition.
- **Covered by Phrase, and never negatived:** `power washing quote`, `power washing estimate`,
  `pressure washing quote`, `pressure washing estimate`, `local power washing`. These are BOFU
  phrases matched by the owned Phrase keywords. **Agency policy forbids auto-negativing `quote`,
  `estimate`, `cost`, `price`, `best`, `hire`, `local`, `near me`.** Removing a text as a *positive*
  is not the same as blocking it.
- **Zero-volume city SKAGs — retire:** `power washing islip` (0 impressions all-time),
  `power washing west islip` (1 impression, 1 click, $5.71, zero leads), `power washing dix hills`
  (0 impressions). **No city keyword has reportable demand and no city needs materially different
  page content.** They are not preserved merely because they exist.
- **Deferred expansion candidates, not launch keywords:** `driveway cleaning service`,
  `patio cleaning service` — no reportable local volume and not matched by the owned texts.
- **Never used as positives:** `pressure washer`, `power washer`, equipment, rental, machine,
  repair, parts. Local SERP evidence shows bare `pressure washer`/`power washer` return **100%
  equipment retail**. The distinguishing token is grammatical — ***washing* is the service,
  *washer* is the machine.** Already blocked by the 132-per-campaign universal fence.

---

## 6. Landing-page map

Full detail in `2026-09-01-final-keyword-ad-page-map.csv`.

| Ad group | Page | Verdict |
|---|---|---|
| Power Washing | `/power-washing-services-islip-west-islip-dix-hills/` | REUSE after P0+P1 — **live QS shows landing-page experience BELOW_AVERAGE** |
| Pressure Washing | `/residential-pressure-washing/` | REUSE after P0+P1 — 21 pressure-washing mentions, best pressure page |
| House Washing | `/house-washing-company/` | REUSE after P0+P1 — 24 house-washing mentions, best house page |
| Soft Washing | `/soft-house-washing/` | REUSE after P0+P1 — **but see below** |
| Driveway Pressure Washing | `/driveway-pressure-washing/` | REUSE after P0+P1 |
| Patio Pressure Washing | `/patio-power-washing/` | REUSE after P0+P1+P3 — title says "Power", H1 says "Pressure" |

**All six carry the same four defects:** wrong brand in the browser title ("Softwind Landscape &
Masonry"), the foreign tag `AW-17878095007`, an H1 city-locked to 3 of 80 targeted places, and an
unsupported resetting countdown.

**A better Soft Washing page already exists.** `/power-washing-soft-washing/` is **not** city-locked
and carries **17 Long Island mentions** and 9 soft-washing mentions, versus `/soft-house-washing/`
which is city-locked with 0 Long Island mentions. Evaluate the swap in Stage 2. **No new page needs
to be built** — every intent has an existing page that scores adequately once the four shared
defects are fixed.

**Location wording: "Long Island" as the H1 anchor with "Serving Nassau and Suffolk County" as the
support line.** Both are verifiable from the 80 live `geo_target_constant` canonical names — every
one is in Nassau or Suffolk. **Do not use dynamic location insertion** and **do not build per-city
pages** — no city keyword has reportable demand.

---

## 7. RSA specification — 12 ads, 2 per group

Full copy, per-asset character counts and QA in `2026-09-01-final-rsa-copy-and-qa.csv`.

- **Exactly 2 genuinely different RSAs per active ad group.** 6 × 2 = **12**, all created **PAUSED**.
- **15 headlines and 4 descriptions each** — all unique and useful, no filler added to hit a count.
- **RSA 1** — exact service intent, local availability, free quote, direct response.
  **RSA 2** — exterior transformation, surface-specific method, curb appeal, professional process,
  free estimate. Surface language differs per group: siding and trim for House, low-pressure for
  Soft, concrete and pavers for Driveway and Patio.
- **No pinning anywhere.**

**Programmatically validated, all 12 passing:** headlines ≤30 · descriptions ≤90 · paths ≤15 · no
duplicate headline or description within an ad · **RSA1/RSA2 headline overlap 0% inside every group**
(they are not minor rewrites) · no digit in any asset (phone-number guard) · no awkward "near me"
copy · ≥2 local headlines and ≥2 quote/estimate headlines per ad · service token in 3–8 headlines and
≥1 description · **no banned claim** (best, #1, cheapest, guaranteed, same-day, licensed, insured,
award, five-star, years in business, 24/7, permanent).

The existing 12 live RSAs in campaign A are **replaced, not edited** — 9 of 15 headlines in the
current Power Washing ads name three hamlets, which is the direct cause of the ad-relevance and
landing-page problems and conflicts with the Long Island wording decision. Replacement is safer than
in-place editing.

---

## 8. Routing negatives — 103 at launch

Full matrix, with a per-row self-block collision test, in
`2026-09-01-final-routing-negative-matrix.csv` (116 rows).

| Layer | Criteria | At launch | Why |
|---|---:|---|---|
| **1 — Sibling EXACT mirror** | **95** | **YES** | Every one of the 19 texts added as negative EXACT in each of the 5 sibling groups. Enforces one-owner-per-text. **Zero blocking risk** — a negative EXACT blocks only the literal string, and the owner group is excluded by construction. |
| **2 — Modifier PHRASE** | **8** | **YES** | `house washing`, `soft washing`, `driveway`, `patio` — applied **only** to Power Washing and Pressure Washing, the two groups owning the loose head terms that would otherwise vacuum sibling queries. Collision-tested: no owned text in either target contains any of the four phrases. |
| **2 — Modifier PHRASE (rest)** | 11 | **NO — DEFER** | Applying these to the four narrow groups is theoretical routing against a leak nobody has observed. Their own Phrase and Exact texts already scope them. |
| **3 — Historical rogue query** | 2 | **NO — DEFER 14 days** | `pressure washer near me` and `commercial pressure washing near me`, both observed 2026-09-01 as NEAR_EXACT close variants at 1 impression, 0 clicks, $0.00. No paid misrouting yet. |

**This differs from the 2026-08-31 memo's 107.** That figure used 12 modifier negatives; the
collision-tested, leak-evidenced set is **8**. The difference is 4 speculative criteria that would
have to be maintained forever against a problem nobody has seen.

**Safeguards, all enforced in the matrix:**

- Routing negatives at **ad-group level only**. The 132-per-campaign universal fence stays separate
  at campaign level. **No sibling-routing negative is ever placed at campaign level**, where it would
  block the intended owner inside the same campaign.
- **No routing negative is added before its owner group is created, approved, enabled, eligible and
  verified serving.** This is why Stage 4 follows Stage 5.
- **No self-blocking** — validated programmatically, 0 violations.
- **Negative keywords cannot fully control loose positive close variants.** An EXACT negative blocks
  only the literal string; an unseen close variant slips past regardless. Residual risk is permanent
  and is managed by **continuous Search Terms review**, not by pre-loading criteria.

---

## 9. Exact build counts

| | |
|---|---|
| Campaigns to create | **0** |
| **Ad groups to create** | **0** — all six already exist in `24103511039` |
| Keyword objects, final | **38** |
| **Keyword objects to create paused** | **28** |
| Keyword objects reused in place | 10 |
| **RSAs to create paused** | **12** |
| **Create-paused objects total** | **40** |
| Routing negatives at launch (separate, later plan) | **103** |
| Ad groups to enable (separate, later plan) | 5 paused + 6 keyword batches = **11 enable actions** |
| Resources to retire (separate, later plan) | **22** |

**Everything is created paused. Enabling requires a second, separate approval after readback QA.**
