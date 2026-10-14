# EKG Lawn Services — build status and continuation file

Last updated: 2026-08-14
Stage: **EXECUTED. Both approvals complete. Everything PAUSED. Awaiting enablement approval.**
Plan fingerprint: `3CFE09B51C76` — executed
Pause fingerprint: `22F413D569DB` — executed
Tests: **323 passed, 0 failed** · Readback: **ALL PASS**

## Executed

**Approval 2** — campaign `19855617751` `Lawn care & Landscaping` PAUSED. Update mask
`["status"]` only. No other campaign changed. Receipt: `receipts/pause-2026-08-14.json`.

**Approval 1** — 80 creates in ONE atomic `GoogleAdsService.mutate`, plus 8 updates.
New campaign **`24144159352`** `Aeration & Overseeding`, PAUSED.
Custom conversion goal **`6458686711`**.
Receipts: `receipts/create-paused-2026-08-14.json`, `receipts/updates-2026-08-14.json`.

## Current account state

- 11 campaigns, **ZERO enabled**. Nothing is serving.
- New campaign PAUSED, budget $16.45/day unshared, MAXIMIZE_CONVERSIONS, Search only,
  Partners and Display off, PRESENCE geo.
- 5 proximity criteria at exactly 2.0 MILES with exact coordinates, 1 geo constant
  `9008421`, 33 campaign negatives, **0 ad schedule criteria, 0 language criteria**.
- 2 PAUSED ad groups, 4 PAUSED keywords, 4 ad-group negatives, 4 PAUSED RSAs.
- 13 CampaignAsset associations, **all PAUSED** (4 sitelink, 8 callout, 1 snippet).
- `goal_config_level = CAMPAIGN`, custom goal attached with exactly the 2 approved actions,
  **all 14 CampaignConversionGoal rows biddable=false**.
- Account-level conversion goals **unchanged** (14 rows, 7 biddable).

## Drive deliverables created 2026-08-14

| Resource | ID |
|---|---|
| Folder `EKG Lawn Services LLC` | `1jL42Hxa4IpFRR37G3uczLgqx9gb-ZXaH` |
| Folder `Landing Pages` | `1XvIguvVuVZxTtWM8nkKxg8YxEZIgsejm` |
| Doc `...Lawn Aeration Landing Page Content` | `1Ic-c56wZzeLAYAJ2olnXeWZM4_cmJg0toFFyNNALTQM` |
| Doc `...Aeration & Overseeding Landing Page Content` | `1HjZZ3Wrqc15T0qoFntagktRTQz4pWngaJi4XulYat-E` |

Both copied from the sanitized master `1ohZDtALF5Px8RygicPx5_VQyVz6e4TcsY8rbDDgc7ZQ`, never
from the canonical Ambient example. 107 placeholder replacements each. Structure identical
to the master. Zero source-client residue. Receipt: `receipts/drive-2026-08-14.json`.

## Drive reorganization and content corrections 2026-08-15

Both Docs were **moved**, never copied — same file IDs, exactly one parent each.

| Page | Page folder | Images folder |
|---|---|---|
| Lawn Aeration | `1IRC2VS38aAzaAcEDFNb_ui9NGwgYWWvr` | `1X8SYuJffNZpAFOZmaYbRwWbER8qNOc_j` |
| Aeration & Overseeding | `1c5htkRjzCOqvFm2-OXFpOgUU6yxOS79y` | `1yverSS5DJKBiHVJS23lctV0er8S1EF-R` |

Corrected in both Docs: three review cards rebuilt to the master's four-line shape with the
**complete** verbatim text restored (`CHELLY` and `DONNA, W.` had been truncated), and all
nine image instructions rewritten to the full brief specification.

One verified first-party image uploaded to each page's `Images` folder at position 5.
Inline insertion is **not possible** without public sharing, which was refused; insertion
remains pending. Eight general-service positions are covered by
`landing-pages/chatgpt-image-generation-request.yaml`. Eight gallery positions still need
authentic EKG project photographs.

Reusable rules and regression tests added: `src/gm_gsa/landing_page_rules.py`,
`tests/test_landing_page_rules.py` (73 tests). Suite: **415 passed**.

## Publisher work added

`src/gm_gsa/plan_compiler.py`, `src/gm_gsa/publisher_capability.py`,
`src/gm_gsa/plan_executor.py`, `tests/test_plan_compiler.py` (33 tests).

The capability gate now fails fingerprint issuance when the publisher cannot reproduce a
plan — the defect that stopped the first execution attempt.

## Remaining before enablement (separate approval)

Landing pages published and returning HTTP 200 · exact GBP reviews · developer images and
logo · form-trigger QA · phone-call source and the 30s threshold decision · mobile QA ·
budget pacing recalculated on the launch date · re-confirmation that the contact page still
states EKG is taking on new customers.
