# RESUME — negative-keyword rollout, portfolio

**Updated 2026-08-30 09:10 EDT.** Supersedes `RESUME-2026-08-29-negatives.md`.

## Status

| Account | ID | Ops | State |
|---|---|---|---|
| Ambient Cooling - Live | 2401959466 | 5,652 | **EXECUTED** 2026-08-29 21:43 — clean |
| Softwind Power Washing - Live | 1521725229 | 170 | **EXECUTED** 2026-08-30 08:42 — clean |
| Pro Green - Austin - Live | 7380491929 | 1,224 | **EXECUTED** 2026-08-30 08:42 — clean |
| Softwind Landscape & Masonry - Live | 2429758629 | 491 | planned, validated, **awaiting approval + mode change** |

The 7,046-operation rollout approved 2026-08-28 is now fully executed. All three
receipts show created == expected == net_added, 0 errors, `unchanged_proof` True,
and budgets / campaign counts / positive keywords unchanged.

| Receipt | |
|---|---|
| `clients/ambient-cooling-heating/receipts/neg-exec-2026-08-29T214247.json` | 5,652, negatives 7,939 → 13,591 |
| `clients/softwind-power-washing/receipts/neg-exec-2026-08-30T084204.json` | 170, negatives 94 → 264 |
| `clients/pro-green-austin/receipts/neg-exec-2026-08-30T084216.json` | 1,224, negatives 4,953 → 6,177 |

## Softwind Landscape & Masonry — ready, not executed

Work order is `mode: read`. Executing needs the owner's approval **and** the work
order flipped to a write mode.

### The geo blocker is resolved

`scripts/slm_geo_read.py` read LOCATION/PROXIMITY criteria from **this** account's
own `campaign_criterion` (receipt `snapshots/geo-read-2026-08-30.json`):
660/660 criteria in New York, 110 per campaign identical across all six campaigns,
52 Nassau/Suffolk place names + 58 postal codes, **zero** location exclusions,
positive and negative geo target type **PRESENCE** on every campaign.
`SOFTWIND_LM["geo_verified"]` is now True on that evidence, not on the sibling's.

### Account shape

6 campaigns, 2 ENABLED (**Patio**, **Pavers** — exactly the work order's expected
set). Paused: Hardscaping, Retaining Walls, Paver Sealing, **Power Washing**.
5,107 unique all-time terms, $5,257.20 cost, 54 conversions.

### The plan

1,701 negative-verdict terms carrying **$1,163.22** of all-time zero-converting
spend (22.1% of account spend). The plan blocks **$1,116.59 = 96.0%** with 491
objects at campaign level on the 2 live campaigns.

```
.venv/Scripts/python.exe scripts/neg_execute.py --slug softwind-landscape-masonry \
  --approve NEG_CAMPAIGN_LEVEL=0F474B2DC919 \
  --approve NEG_NAME_BROAD=A729E0F5F42C \
  --approve NEG_CROSS_ACCOUNT_FENCE=CE0831F43405 --execute
```

| Layer | Objects | Fingerprint |
|---|---|---|
| NEG_CAMPAIGN_LEVEL | 365 | `0F474B2DC919` |
| NEG_NAME_BROAD | 54 | `A729E0F5F42C` |
| NEG_CROSS_ACCOUNT_FENCE | 72 | `CE0831F43405` |
| **MASTER** | **491** | `D3CE42F82CCF` |

`NEG_AD_GROUP_LEVEL` (910 objects) is built but **not recommended and not
approved** — campaign negatives already render as `Excluded`, so it buys
visibility we already have at 2.5x the objects. The executor writes campaign
criteria only.

Per-campaign ceiling is not at risk: Patio 420 → 663, Pavers 416 → 664, against
10,000.

## Red team — 0 failures

`scripts/slm_redteam.py`, all local. Identity, campaign scope, protected tokens,
manufacturers, match types, live-keyword blocking, KEEP-term blocking,
per-campaign ceiling, duplicates, name-layer contents. It found **three real
defects on the first pass**, all now fixed:

1. **US-place guard was inert.** `softwind-landscape-masonry` was missing from
   both `NEIGHBOUR_STATES` and `HOME_STATE` in `neg_names.py`, so `state_places`
   fell back to `places_by_state[""]` → empty set, and place names were accepted
   as BROAD negatives (`westbury`, `staten`). Added the entry, and the silent
   fallback now raises instead. 3,715 place tokens protected; accepted names
   34 → 27.
2. **Manufacturer protection was too narrow.** SLM's `core` matched
   `cambridge\s+paver`, so Cambridge *wall* products fell through and
   `cambridge block wall` / `cambridge wall stone` were minted as negatives —
   on an account with real Cambridge demand (`cambridge pavers near me`, $44.60,
   KEEP). Now matches the bare brand. Protecting only ever mints fewer negatives,
   so a false positive here is the safe direction.
3. **Fence duplicated the evidence layer.** 15 exterior-cleaning phrases were
   minted twice per campaign — once by waste evidence in `NEG_CAMPAIGN_LEVEL`,
   once preventively by the fence — 30 duplicate objects.
   `neg_preflight_local.py` only dedupes *within* a layer. `neg_merge_fence.py`
   now dedupes the fence against the evidence layer; the evidence layer wins.

## New in the pipeline

| Script | What |
|---|---|
| `scripts/slm_geo_read.py` | reads LOCATION/PROXIMITY criteria + geo target type settings |
| `scripts/neg_merge_fence.py` | merges a READY scope fence into a bundle as a subplan — the step that was done by hand on 08-28 |
| `scripts/slm_redteam.py` | 10-check local red team of a bundle |
| `scripts/entity_marker_audit.py` | checks executed accounts for the entity-marker defect |
| `scripts/pw_fence_verify.py` | reconciles a fence file against what is live |

`neg_cross_account.py` no longer hardcodes `corpus_available`; it derives it from
disk, so a fence stops being stuck at "PREPARED" once the corpus lands.

## OPEN — entity markers on the three executed accounts

`neg_names.py` was adding BROAD entity markers (`llc`, `inc`, `corp`, ...) with no
check for KEEP-term overlap, English-word status, or corpus evidence. Three guards
now exist, and on SLM they removed all 6 markers. **The executed accounts were
built before the fix and carry markers the guards would now refuse**
(`scripts/entity_marker_audit.py`):

| Account | Markers live | Assessment |
|---|---|---|
| Ambient 2401959466 | corp, corporation, inc, incorporated, ltd | `inc` blocks 2 KEEP competitor-name terms; 4 of 5 are English words |
| Pro Green Austin 7380491929 | + llc | `llc` blocks KEEP `landscaping llc near me`; `incorporated` has zero corpus evidence |
| Softwind PW 1521725229 | all 6 | **all six have zero corpus evidence** — 12 objects blocking nothing |

**Zero conversions are blocked on any account.** Measured spend impact is
negligible. The real argument is forward-looking: a BROAD single-token negative on
a business suffix blocks every future query containing it.

Recommendation: remove the 6 markers from Softwind Power Washing (no evidence at
all) and `llc` from Pro Green Austin (blocks a generic in-scope query pattern).
That is a **destructive change on live accounts and needs its own approval** under
the Safety rules. Not actioned.

## Quota

Exhausted 2026-08-30 08:47, reopens **~21:40 EDT 2026-08-30**
(`Retry in 46,077 seconds`).

Cause: `scripts/neg_validate.py` was run unfiltered. `validate_only` writes
nothing but spends the **same** basic-access daily operation budget as a real
mutate — ~14,000 operations across every account and layer, on top of the 1,394
real mutates. It now **refuses without `--spend-quota`** and accepts `--slug`.
Use `neg_preflight_local.py` instead: same checks, no API, no quota.

Nothing was created by that run and no account was harmed; it only pushed SLM's
491 objects to the next window.

## Still open, not blocking

- **SLM-Q3** — does 2429758629 sell landscaping and masonry beyond Patio and
  Pavers? The account runs 4 paused campaigns including Retaining Walls and
  Paver Sealing. Answer narrows or confirms the `core` pattern.
- **SLM-Q4** — paver sealing is treated as belonging to 2429758629. This account
  has a paused **Paver Sealing** campaign, which supports that reading.
- **The paused Power Washing campaign on 2429758629** contradicts the mutual
  scope fence. It is paused, so it is not competing today, but if re-enabled it
  would collide with 1521725229. Worth an explicit owner decision.
- `NEG_CROSS_AD_GROUP` — 2 objects on Pro Green Austin (`A063216FF210`), 1 on
  Softwind Power Washing (`A46A0A8EB91E`). Never explicitly approved; the
  executor only writes campaign criteria.
- Held-back name tokens with reasons: `reports/st-names/*-name-negatives.json`.

## Accounts NOT in this rollout

`reports/portfolio-live-accounts.json` lists Beaver Bins, Emerald Oasis,
Greenway Lawn Care, MasterGrass and Nolte & Son's. None has a validated
search-terms work order, so the client gate blocks work on them. EKG Lawn
Services has a work order but it is `type: full-system`, not search-terms.
