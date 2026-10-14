# 29 — Server-Side Validate-Only Receipt

**Account:** Pro Green - Austin - Live | `7380491929` | outdoor design & build  
**Subplan:** EXISTING_RESOURCES `628D3E61A9C2`  
**Master:** `063EE720BAF3`  
**Executed:** 2026-08-22T13:48:29.937411+00:00  
**Mode:** VALIDATE-ONLY

## Request

| Field | Value |
|---|---|
| Customer ID | `7380491929` (exact child ID, never the MCC) |
| Approved actions | 68 |
| Approved objects | 68 |
| API operations | 68 |
| `partial_failure` | `False` |
| `validate_only` | `true` |
| Campaign resource names | `customers/7380491929/campaigns/24053505501`, `customers/7380491929/campaigns/24053505504` |
| Match type | PHRASE on every operation |
| Result | **VALIDATION PASSED.** Nothing was written. |

The fingerprint was recomputed from the on-disk plan before the request was built. The executor refuses to run on any mismatch, so the validated operation set is byte-identical to the plan that carries the fingerprint above.

## Post-validate re-read

Fresh read-only re-read at 2026-08-22T13:49:25.908507+00:00.

| Counter | Before | After | Unchanged |
|---|---:|---:|:--:|
| Campaign negatives, Hardscape Construction | 44 | 44 | YES |
| Campaign negatives, Outdoor Living & Design | 44 | 44 | YES |
| Ad-group negatives | 246 | 246 | YES |
| Shared-list criteria | 8689 | 8689 | YES |
| Positive keywords | 48 | 48 | YES |
| Enabled ads | 48 | 48 | YES |

**68 proposed negatives were searched for in the live account. 0 were found.** No proposed negative exists. Campaign statuses, budgets and bidding strategies are unchanged:

- `24053505501` status `ENABLED`, budget $26.31/day, bidding `TARGET_SPEND`
- `24053505504` status `ENABLED`, budget $39.47/day, bidding `TARGET_SPEND`

Combined daily budget $65.78, unchanged.

## NO EXTERNAL CHANGES MADE

Automated assertion: `True`

Receipt JSON: `clients/pro-green-austin/receipts/validate-campaign-negatives-2026-08-22.json`  
Re-read JSON: `clients/pro-green-austin/snapshots/post-validate-check-2026-08-22.json`