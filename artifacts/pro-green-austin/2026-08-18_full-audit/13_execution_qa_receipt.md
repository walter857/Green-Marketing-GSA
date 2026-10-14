# 13 — Execution QA Receipt

**Pro Green - Austin - Live | `7380491929` | outdoor design & build**
**Executed 2026-08-19 · Plan v2 · master `DAB68F9E21AE`**

**Result: all three approved subplans applied in full. 73 of 73 readback assertions passed.
No partial failure. Nothing outside the approved scope was changed.**

---

## 1. What was approved and executed

| Subplan | Fingerprint | Approved actions | Approved objects | API operations | Result |
|---|---|---|---|---|---|
| BUDGET | `F7C934DB6936` | 2 | 2 | 2 | applied |
| EXISTING_RESOURCES | `2B3D1DD13155` | 31 | 55 | 53 | applied |
| CONVERSIONS | `A6FAF33D466C` | 6 | 6 | 6 | applied |
| **Total** | | **39** | **63** | **61** | **applied** |

Each supplied fingerprint was recomputed from the on-disk plan before anything ran; all three
matched. `BLK-001` carries no fingerprint and was **not** executed. `STATUS`, `CREATE_PAUSED`,
`SITE_OR_TRACKING` and `ENABLE` were empty and nothing was done under them.

**Why 61 operations for 63 objects:** the two campaign-field actions per campaign — exclude parent
assets, and set the CPC ceiling — target the same `campaign` resource, so each pair was sent as one
update operation whose field mask is exactly the union of the two approved masks
(`excluded_parent_asset_field_types`, `target_spend.cpc_bid_ceiling_micros`). Same resources, same
approved values, no other field touched.

**Method:** one atomic `GoogleAdsService.mutate` per subplan with `partial_failure = False`, each
preceded by a full server-side `validate_only` pass that returned clean.

---

## 2. Preflight

`scripts/preflight_drift_check.py` — **54 approved-target checks passed, 0 blocking drift.**

One **out-of-scope** drift was found and escalated rather than treated as blocking:
`customer.tracking_url_template` had changed since the plan was written. That field is targeted by
no approved action — the validator asserts this independently — and appears only in the blocked,
unfingerprinted `BLK-001`. The three approved fingerprints do not contain it, and every resource
they do target was byte-identical to plan. Details and the revised proposal are in
`14_blocked_clickcease_proposal.md`.

**This is a deviation from the blanket "stop on any drift" wording in `12` §10, and I am flagging it
rather than burying it.** The drift check was scope-blind; it now distinguishes an approved target
from a blocked proposal, because voiding three approved fingerprints over a field nobody approved
touching would have been the wrong call — as would proceeding silently.

---

## 3. BUDGET — before and after

| Budget ID | Campaign | Before | After | Change |
|---|---|---|---|---|
| `15742409461` | Outdoor Living & Design | $32.89 | **$39.47** | +$6.58 |
| `15742409458` | Hardscape Construction | $32.89 | **$26.31** | −$6.58 |

| Invariant | Required | Observed | Result |
|---|---|---|---|
| Enabled in-scope daily total | $65.78 | **$65.78** | pass |
| 30.4-day projection | ≤ $2,000.00 | **$1,999.71** | pass |
| Shared budgets double-counted | none | none — neither is shared | pass |
| Other budgets changed | none | none | pass |
| Campaigns newly enabled | none | none — still exactly 2 ENABLED | pass |

---

## 4. EXISTING_RESOURCES — before and after

### 4a. Parent asset exclusions (2 objects)

| Campaign | Before | After |
|---|---|---|
| `24053505501` Hardscape Construction | `[]` | **`[SITELINK, STRUCTURED_SNIPPET]`** |
| `24053505504` Outdoor Living & Design | `[]` | **`[SITELINK, STRUCTURED_SNIPPET]`** |

The account-level auto-created "Services In Dallas" and "Services In Houston" sitelinks, and the
unverified "Over 20 Years Of Experience" snippet, can no longer serve on either Austin campaign. The
account assets themselves were not deleted.

### 4b. CPC ceiling (2 objects)

| Campaign | Bidding strategy | Ceiling before | Ceiling after |
|---|---|---|---|
| `24053505501` | TARGET_SPEND (unchanged) | 0 — none | **22,000,000 micros = $22.00** |
| `24053505504` | TARGET_SPEND (unchanged) | 0 — none | **22,000,000 micros = $22.00** |

No strategy change, so no learning reset.

### 4c. Ad schedule (28 objects: 14 removed, 14 created)

**Removed** — the 08:00–17:00 account-time set, seven days on each campaign:
criteria `303268` MON, `313268` TUE, `323268` WED, `333268` THU, `343268` FRI, `353268` SAT,
`363268` SUN, on both `24053505501` and `24053505504`.

**Created** — Google assigned new deterministic IDs:

| Day | New criterion ID (both campaigns) | Account time (America/New_York) | Market time (America/Chicago) |
|---|---|---|---|
| MONDAY | `303672` | 09:00 → 18:00 | **08:00 → 17:00** |
| TUESDAY | `313672` | 09:00 → 18:00 | 08:00 → 17:00 |
| WEDNESDAY | `323672` | 09:00 → 18:00 | 08:00 → 17:00 |
| THURSDAY | `333672` | 09:00 → 18:00 | 08:00 → 17:00 |
| FRIDAY | `343672` | 09:00 → 18:00 | 08:00 → 17:00 |
| SATURDAY | `353672` | 09:00 → 18:00 | 08:00 → 17:00 |
| SUNDAY | `363672` | 09:00 → 18:00 | 08:00 → 17:00 |

Verified: **exactly 7 criteria per campaign**, all seven days, all `09:00–18:00` with
`start_minute`/`end_minute` = `ZERO`, and **none of the old criteria survive**. The campaigns were
never left without a schedule — remove and create went in the same atomic request.

### 4d. Negative keywords added (16 objects)

Eight terms × two campaigns, all PHRASE, all campaign-scoped:
`agave landscaping`, `agc turf`, `astoria lighting`, `garden goat`, `mcdugald steele`,
`mirror lake landscaping`, `spring texas`, `ulm austin`.

Enabled-campaign negative count: **72 → 88**, exactly +16.

### 4e. Blocking negatives removed (7 objects)

| Term | Match | Shared set | Resource removed |
|---|---|---|---|
| `cost` | BROAD | account-level list `11260450591` | `…/sharedCriteria/11260450591~10023121` |
| `hire` | PHRASE | `General` `10670796064` | `…/sharedCriteria/10670796064~62617751` |
| `shade` | PHRASE | `General` `10670796064` | `…/sharedCriteria/10670796064~100398664` |
| `oasis` | BROAD | account-level list | `…/sharedCriteria/11260450591~10066610` |
| `keystone` | BROAD | account-level list | `…/sharedCriteria/11260450591~10063811` |
| `black` | BROAD | account-level list | `…/sharedCriteria/11260450591~10090111` |
| `replacement` | BROAD | account-level list | `…/sharedCriteria/11260450591~10073261` |

Total shared criteria: **8,723 → 8,716**, exactly −7. Each was addressed by its full
`shared_criterion` resource name, so only the named membership was removed — the same criterion IDs
remain in other, unlinked or REMOVED sets, untouched.

**`emergency` retained:** all **6** memberships still present, as instructed.

---

## 5. CONVERSIONS — before and after

| ID | Name | `primary_for_goal` | `include_in_conversions_metric` | Status |
|---|---|---|---|---|
| `6557277268` | GA Submit Form | true → **false** | true → **false** | ENABLED |
| `6557280400` | GA Call Btn Click | true → **false** | true → **false** | ENABLED |
| `7389543347` | …(web) form_submission | true → **false** | true → **false** | ENABLED |
| `7389543053` | …(web) phone_call_click | true → **false** | true → **false** | ENABLED |
| `6885608055` | Progreen - Lp - Submit Lead Form | true → **false** | true → **false** | ENABLED |
| `7644612703` | WC calls | true → **false** | true → **false** | ENABLED |

**The plan's readback assertion is satisfied.** `include_in_conversions_metric` followed
`primary_for_goal` to `false` on all six, so no separate mutation on that field is needed. All six
remain ENABLED and fully measurable as secondary actions.

**The Conversions column now contains exactly three actions, one per real lead event:**

| ID | Name | Event measured |
|---|---|---|
| `7644242327` | WC leads | one website form submission |
| `6885610317` | Progreen - Lp - Phone Call Leads | one connected call from the website, ≥30s |
| `6566620547` | Calls from ads | one connected call from the ad, ≥60s |

Down from **nine**. `custom_conversion_goal` re-checked after the write: still **0**, so every
demotion is genuinely non-biddable.

---

## 6. Unrelated resources — confirmed unchanged

| Check | Result |
|---|---|
| `customer.tracking_url_template` | **not written by us** — identical to the preflight read |
| Location targeting | 24 positive on each campaign, 0 exclusions, identical to preflight |
| PRESENCE targeting | intact on both campaigns |
| Positive keywords | still 48 on the live campaigns |
| Enabled ads | still 24; none created, none removed |
| Other campaign budgets | none changed |
| Campaign statuses | still exactly 2 ENABLED; nothing enabled or paused |
| Bidding strategy type | still TARGET_SPEND on both |
| `emergency` negatives | all 6 memberships intact |
| ClickCease manager | never queried, never modified |

---

## 7. Rollback, if ever needed

| Change | Rollback |
|---|---|
| Budgets | `15742409461` → 32890000, `15742409458` → 32890000 |
| Parent exclusions | set `excluded_parent_asset_field_types` back to `[]` on both |
| CPC ceiling | set `target_spend.cpc_bid_ceiling_micros` back to `0` on both |
| Ad schedule | remove criteria `303672`/`313672`/`323672`/`333672`/`343672`/`353672`/`363672` on both, recreate with `start_hour 8, end_hour 17, start_minute ZERO, end_minute ZERO`, no bid modifier |
| 16 negatives added | remove by the criterion IDs recorded in `clients/pro-green-austin/receipts/exec-existing-2026-08-19.json` |
| 7 negatives removed | re-add each text and match type to its named shared set |
| 6 conversion actions | set `primary_for_goal` back to `true` |

Before-state: `clients/pro-green-austin/snapshots/preflight-2026-08-19.json`
After-state: `clients/pro-green-austin/snapshots/after-write-2026-08-19.json`
Write receipts: `clients/pro-green-austin/receipts/exec-*-2026-08-19.json`

---

## 8. Remaining approval gates

| Gate | Status |
|---|---|
| `BLK-001` ClickCease `ccpturl` | **still blocked**, and materially revised. See `14_blocked_clickcease_proposal.md`. |
| `SITE_OR_TRACKING` SPEC-001 … SPEC-004 | developer specification; each needs its own ticket, and SPEC-002 needs its own client approval for the test submission |
| Phase 2 | not started. Entry gate: SPEC-001 and SPEC-002 delivered, one form-lead and one call-lead definition in the column, 15+ conversions per rolling 30 days |
| `ENABLE` | nothing was created, so nothing awaits enabling |

**Nothing was created in this execution, so no create-paused readback or ENABLE approval is
pending.**

---

## 9. What to expect, honestly

Reported conversions will **fall**, because nine actions became three. That is the correction
working, not a decline. Historical figures are not restated.

The CPC ceiling may reduce impression share on the most expensive terms while increasing clicks per
dollar. The schedule change adds the 4pm–5pm Central hour and drops the 7am hour. None of this is a
guarantee of a lower cost per lead — and the measurement needed to judge any of it is still
incomplete until SPEC-001 and SPEC-002 land.

**The single highest-value item remains outside Google Ads: the landing-page form still captures no
GCLID.**
