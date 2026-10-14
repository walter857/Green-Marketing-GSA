> **STATUS 2026-09-28 (run D): CLOSED — owner confirmed a deliberate exclusion. See the section at the end. The HOLD text below is preserved history.**

# 06 — Tablet exclusion: evaluated plan, documented HOLD

**Decision: HOLD. The exclusion stays exactly as it is.** No record gives a business reason. I searched the work orders,
`client.yaml`, every plan, the receipts, the implementation record and memory. Guessing the owner's intent in either
direction would be wrong, so one owner question is raised.

## Current state (fresh read, 2026-09-28 ≈21:15 UTC)

| Resource | Level | Device | `bid_modifier` present | Value |
|---|---|---|---|---|
| `campaignCriteria/24257151015~30002` | campaign | TABLET | yes | 0.0 (the v25 docs say "Use 0 to opt out of a Device type") |
| `adGroupBidModifiers/200347713516~30002` | ad group | TABLET | yes | 0.0 |
| `adGroupBidModifiers/200347713556~30002` | ad group | TABLET | yes | 0.0 |
| desktop ~30000 / mobile ~30001 (campaign and both ad groups) | — | — | no | unset (no adjustment) |

**Change history:** one `change_event` row. It is dated 2026-09-25 08:26:21 CT, comes from `GOOGLE_ADS_WEB_CLIENT`, is an
UPDATE of `24257151015~30002`, and has **empty changed-fields and empty before/after payloads**. `change_status` agrees and
has no ad-group modifier row. The prior value is therefore inferred from delivery: one tablet impression on 09-23, none
after 09-25. It is not read from history.

**Impact evidence:** tablets were 1 of 65 impressions (1.5%). One impression cannot show that tablets are worth anything,
or that they are worthless. Any upside from restoring is small and unproven.

## Evaluated restoration payload (recorded, not fingerprinted)

`clients/apogee-lawns/plans/APG-0928-DEV-T2.yaml`:
- **3 updates, all required, none conditional:** the campaign row and both ad-group rows, `bid_modifier` 0.0 → 1.0.
  Each ad-group row carries its own explicit 0.0, and an ad-group device modifier overrides the campaign value for that
  ad group, so restoring the campaign row alone would leave tablets excluded.
- **0 creates, 0 removes, 0 other changes.** Desktop and mobile are not touched.
- The earlier `APG-0928-DEV-T` (fingerprint **46060B03F5C9**) is **VOID** and bannered in place. It described "1 required
  update plus 2 conditional" and pre-dated the owner question.
- A fingerprint will be generated from DEV-T2's exact payload only if the owner answers "restore".

**Owner question:** was the 2026-09-25 tablet exclusion deliberate? If yes, it stays and DEV-T2 closes. If no, reply
"restore tablets".


---

## CLOSED 2026-09-28 (run D) — owner confirmed the exclusion

The owner said: "Landing pages are not tablet optimized so I excluded them."

- The exclusion was **deliberate** and **stays**.
- `APG-0928-DEV-T2` is now **REJECTED** (`status_reason: OWNER_CONFIRMED_DELIBERATE_EXCLUSION`); its evaluated 3-update
  payload is kept as history only.
- `APG-0928-DEV-T` stays VOID, and `46060B03F5C9` stays invalid.
- No restoration code is issued.
- The single historical tablet impression does not weaken the owner's usability reason.
- Any future restoration requires completed tablet-layout QA and a new, separately approved plan. It is not part of
  this task.
