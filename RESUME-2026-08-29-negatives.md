# SUPERSEDED

**This file is superseded by `RESUME-2026-08-30-negatives.md` (2026-08-30).** Pro Green Austin and Softwind Power Washing executed clean on 2026-08-30 08:42; Softwind Landscape & Masonry now has a validated 491-object plan awaiting approval. Kept for the quota and timing record below.

---

# RESUME — negative-keyword rollout, 4 accounts

**Updated 2026-08-29 21:45 EDT.**

## Status

| Account | ID | Ops | State |
|---|---|---|---|
| Ambient Cooling - Live | 2401959466 | 5,652 | **EXECUTED 2026-08-29 21:43 EDT — clean** |
| Pro Green - Austin - Live | 7380491929 | 1,224 | approved, **not run** — awaiting owner go |
| Softwind Power Washing - Live | 1521725229 | 170 | approved, **not run** — awaiting owner go |
| Softwind Landscape & Masonry - Live | 2429758629 | — | identity gate PASS; geo still ungated |

**Ambient receipt:** `clients/ambient-cooling-heating/receipts/neg-exec-2026-08-29T214247.json`
created 5,652 / expected 5,652 / net_added 5,652, 0 errors, 0 partial failures,
campaign_negatives 7,939 → 13,591, campaigns 23 → 23, positive keywords 5,000 → 5,000,
`unchanged_proof` True, EXCLUDED 24 of 794 rows (last 30 days).

Run the remaining two with the mutate-gated runner:

```
.venv/Scripts/python.exe scripts/neg_autorun.py --only pro-green-austin
.venv/Scripts/python.exe scripts/neg_autorun.py --only softwind-power-washing
```

## Historical note: what blocked 2026-08-28/29

The 2026-08-28 note estimated quota would return "~10:00". **That was wrong.**
Measured live this morning:

| Probe time (ET) | `Retry in` | Implied unblock |
|---|---|---|
| 2026-08-28 23:20 | ~83,000 s | 2026-08-29 ~22:23 |
| 2026-08-29 09:26 | 44,112 s | 2026-08-29 ~21:41 |
| 2026-08-29 09:34 | 43,848 s | 2026-08-29 ~21:44 |

So the developer token's basic-access budget clears **late tonight, roughly
21:40–22:20 America/New_York**, not this morning.

It is a **rolling** window, not a midnight reset: a handful of reads succeeded at
09:26 (Ambient, Softwind L&M, MasterGrass, Beaver Bins, EKG) before the rest
returned `RESOURCE_EXHAUSTED`. A trickle is free; the bulk is not. Do **not**
read "one request worked" as "quota is back".

## Recommended execution plan (changed from the 2026-08-28 order)

**Run the two small accounts first, and give Ambient its own day.**

The rollout is 7,046 operations against a ~15,000/day cap, and at the moment the
window reopens only part of the budget has rolled off. Smallest-first means a
short budget leaves at most the largest account partial, and a partial Ambient is
the single most expensive thing to recover (it needs a corpus re-pull, which costs
more quota and rewrites the approved plan).

| # | When | Account | Ops | Why this slot |
|---|---|---|---|---|
| 1 | after ~22:30 tonight | Softwind Power Washing | 170 | tiny; proves the cross-account fence and the `Excluded` acceptance test for real |
| 2 | immediately after | Pro Green - Austin | 1,224 | still small; 1,394 ops total will fit even a partly-refilled window |
| 3 | 2026-08-30 morning | Ambient Cooling | 5,652 | gets a clean full-quota day; 5,652 ops has room to complete in one run |

Running all three tonight is possible but risks stopping mid-Ambient.
Waiting until 2026-08-30 for all three is also fine and slightly safer.

## Step 1 — commands (unchanged; fingerprints re-verified 2026-08-29 09:44)

Each re-checks identity, snapshots before, writes with `partial_failure=True`,
reads back, proves unrelated resources unchanged, and counts `EXCLUDED` rows.
Drop `--execute` for a dry run.

```
.venv/Scripts/python.exe scripts/neg_execute.py --slug softwind-power-washing \
  --approve NEG_CAMPAIGN_LEVEL=1D954F45E2E6 \
  --approve NEG_NAME_BROAD=E71C78C77203 \
  --approve NEG_CROSS_ACCOUNT_FENCE=D27F2802FD31 --execute

.venv/Scripts/python.exe scripts/neg_execute.py --slug pro-green-austin \
  --approve NEG_CAMPAIGN_LEVEL=6E1A7584E482 \
  --approve NEG_NAME_BROAD=41F1B766F07A --execute

.venv/Scripts/python.exe scripts/neg_execute.py --slug ambient-cooling-heating \
  --approve NEG_CAMPAIGN_LEVEL=A8E3523F7521 \
  --approve NEG_NAME_BROAD=5580D132851B --execute
```

| Account | ID | Core | Name BROAD | Fence | Total |
|---|---|---|---|---|---|
| Softwind Power Washing - Live | 1521725229 | 4 | 12 | 154 | 170 |
| Pro Green - Austin - Live | 7380491929 | 1,054 | 170 | — | 1,224 |
| Ambient Cooling - Live | 2401959466 | 4,252 | 1,400 | — | 5,652 |

Verified locally 2026-08-29 09:44 by `scripts/neg_preflight_local.py`:
all seven fingerprints unchanged, master fingerprints unchanged,
**rule violations 0**, dropped 0 across every layer.

**If quota runs out mid-run:** the executor stops, writes
`clients/<slug>/receipts/neg-exec-PARTIAL-*.json` with every created resource
name, and exits non-zero. Do **not** rerun blindly — re-pull that account's
corpus and let the per-scope redundancy filter skip what already exists.

## Step 2 — Softwind Landscape & Masonry `2429758629`

### Identity gate: **PASS** (done 2026-08-29 09:28)

`scripts/slm_identity_gate.py`, one read from **inside** the account:

```
name_match True | id_match True | not_manager True | not_test True | live_marker True
observed 'Softwind Landscape & Masonry - Live' / 2429758629
status ENABLED | America/New_York | USD | auto-tagging True
```

Receipt: `clients/softwind-landscape-masonry/snapshots/identity-gate-2026-08-29-0928.json`.
Recorded in `client.yaml` and `work-order.yaml`. **SLM-Q2 is resolved.**
The gate authorizes read-only work only.

### Local prep done 2026-08-29 — no API left in it

- `scripts/portfolio_st_pull.py` — SLM registered in `ACCOUNTS`, plus a new
  `--only <slug>` / `--allow-overwrite` guard. **It now refuses to run
  unfiltered**, because a re-pull rewrites `reports/st-corpus/<slug>-corpus.json`
  and would invalidate the approved fingerprints built from it (Google restates
  conversions retroactively, so a re-pull is not idempotent).
- `scripts/neg_lexicon.py` — `SOFTWIND_LM` entry written: brand, core, intent and
  four disqualify groups including `SIBLING_EXTERIOR_CLEANING`, the owner's mutual
  fence. Paver manufacturers (Nicolock, Belgard, Cambridge, Techo-Bloc, Unilock,
  EP Henry) are in **core**, so they can never be minted as competitor negatives.
- `neg_classify` / `neg_competitors` / `neg_names` / `neg_plan` now **skip** an
  account with no corpus or an unverified geo instead of aborting the run.

### The one thing still gated: service area

`SOFTWIND_LM["geo_verified"]` is `False` and `compile_account()` **refuses** the
entry. `classify()` turns a `geo_out` hit into a `GEO_OUT_OF_AREA` negative, so
guessing the service area would mint destructive negatives. The sibling targets
Long Island; that is **not** evidence for this account.

Remaining sequence, once quota allows:

```
.venv/Scripts/python.exe scripts/portfolio_st_pull.py --only softwind-landscape-masonry
```

1. Read the service area from `campaign_criterion` in the pulled corpus; fill
   `geo_in` / `geo_out` and set `geo_verified: True`.
2. Confirm it runs the **Patio** and **Pavers** campaigns. If those are the only
   two, consider narrowing `core` (it currently also admits landscaping and
   masonry, which the account name and the owner's wording assert — the broader
   core deliberately mints *fewer* negatives while **SLM-Q3** is open).
3. `neg_classify.py` → `neg_plan.py` → `neg_names.py` → `neg_bundle.py` →
   `neg_preflight_local.py`, then present the bundle for approval.
4. Apply the prepared scope fence
   `reports/st-cross-account/softwind-landscape-masonry-scope-fence.json`
   (52 PHRASE negatives, fingerprint `D7448295DA46`, campaign count unknown
   until the pull).

## Still open, not blocking

- `NEG_CROSS_AD_GROUP` — 2 objects on Pro Green Austin (`A063216FF210`), 1 on
  Softwind Power Washing (`A46A0A8EB91E`). Genuine ad-group-level steering, never
  explicitly approved. The executor only writes campaign criteria.
- **SLM-Q3** — does 2429758629 sell landscaping and masonry beyond Patio and
  Pavers? Answer narrows or confirms the `core` pattern.
- **SLM-Q4** — Softwind Power Washing's `client.yaml` says business_name
  *"Softwind Powerwashing & Paver Sealing"*, but its work order excludes paver
  sealing and the owner reconfirmed that. Paver sealing is treated as belonging
  to 2429758629.
- Held-back name tokens with reasons: `reports/st-names/*-name-negatives.csv`.
- Softwind Power Washing has **$0.00** measurable waste (48 unique terms
  all-time). Its constraint is demand, not negatives.

## Environment gotcha found 2026-08-29

Writing Python through a **bash heredoc mangles backslash escapes** in this
environment: `\b` in a patch payload landed in `neg_lexicon.py` as a literal
0x08 byte, silently breaking 50 regex word boundaries. `\w` and `\s` survived.
Symptom is a regex that compiles fine and matches nothing. Use the Write tool for
any regex-bearing file, and grep for control characters afterwards.

## Key artefacts

| Path | What |
|---|---|
| `clients/*/plans/2026-08-28-negative-expansion.json` | approval bundles + fingerprints |
| `clients/softwind-landscape-masonry/snapshots/identity-gate-*.json` | the passed gate |
| `reports/st-verdicts/*-verdicts.csv` | every term, verdict, category, cost |
| `reports/st-names/*-name-negatives.csv` | accepted names + everything held back |
| `reports/st-competitors/*.csv` | unknown-entity review list |
| `reports/st-cross-account/*.json` | the two scope fences |
| `reports/st-corpus/*.json` | raw pull, 2019-01-01..2026-08-28 |
| `reports/lexicons/` | english words, census surnames, US places |
