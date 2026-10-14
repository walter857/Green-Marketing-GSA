# Softwind Landscape & Masonry — final completion report

**Run:** 2026-09-03, 23:45 → 2026-09-04 00:1x America/New_York
**Account:** Softwind Landscape & Masonry - Live · `2429758629` · USD · America/New_York

---

## 1. Verified account identity — APPLIED / READBACK-PASSED

Fresh gate at **2026-09-03 23:45**, receipt `snapshots/identity-gate-2026-09-03-2345.json`.

| Check | Expected | Observed |
|---|---|---|
| Child customer ID | 2429758629 | 2429758629 ✓ |
| Account name | Softwind Landscape & Masonry - Live | exact match ✓ |
| Manager / test account | false / false | false / false ✓ |
| Currency / time zone | USD / America/New_York | USD / America/New_York ✓ |
| Status | ENABLED | ENABLED ✓ |
| Patio | 23484806108 | 23484806108, ENABLED, SERVING ✓ |
| Pavers | 23489296528 | 23489296528, ENABLED, SERVING ✓ |

Preflight: **498 tests passed** before the run, **505 after** (7 new guard tests).
Both work orders PASS. `verify_setup` PASS. Strict YAML PASS.
Drift vs the post-NEG-3 snapshot: **0 differences**. All prior packages intact.

## 2. Live actions completed this run

| # | Action | Status | Ops | Readback |
|---|---|---|---|---|
| 1 | **PLAN-SLM-CONV-2** `852D47BE6133` — demote `Softwind Submit lead form` | **APPLIED** | 1/1 | **READBACK-PASSED** |
| 2 | **PLAN-SLM-TRK-B1** `699CC103CAD0` — campaign final URL suffix, Patio + Pavers | **APPLIED** | 2/2 | **READBACK-PASSED** |

Final unchanged-resource proof: **3 differences, 0 unexpected** — the one
conversion flag and the two suffixes. Zero negatives added or removed, zero
keyword status changes, zero budget or ceiling changes.

## 3. Readback results

### CONV-2

| Field | Before | After |
|---|---|---|
| `primary_for_goal` | True | **False** ✓ |
| `include_in_conversions_metric` | True | **False** (derived) |
| status / type / category / origin | ENABLED / WEBPAGE / SUBMIT_LEAD_FORM / WEBSITE | all unchanged |
| counting_type / lookbacks / attribution / call duration | ONE_PER_CLICK / 30 / 1 / data-driven / 60 | all unchanged |

**On the derived field.** The executor's field mask was `["primary_for_goal"]`
only — one field written. `include_in_conversions_metric` moved because Google
recomputes Conversions-column membership from the goal state. That is the
intended effect of this package, not a side change. **Every independently
settable field is unchanged, and no other conversion action changed at all.**

### TRK-B1

| Campaign | Suffix before | Suffix after |
|---|---|---|
| Patio `23484806108` | UNSET | **SET, 147 chars, exact match to plan** ✓ |
| Pavers `23489296528` | UNSET | **SET, 147 chars, exact match to plan** ✓ |
| Hardscaping, Paver Sealing, Power Washing, Retaining Walls | UNSET | UNSET (untouched) |

CPC ceilings and budgets on both campaigns unchanged at readback.

## 4. Conversion architecture — before and after

**Before:** 7 primary actions counting into Conversions.
**After: 6.**

| ID | Action | Type | Category | Primary + counting |
|---|---|---|---|---|
| 7480764700 | (web) form_submission | GA4 custom | SUBMIT_LEAD_FORM | **yes — the single form lead signal** |
| 7461572537 | Calls from ads | AD_CALL | PHONE_CALL_LEAD | yes |
| 7508686781 | Calls from ads (1) | AD_CALL | PHONE_CALL_LEAD | yes — watch item, dormant since June |
| 7461590068 | Softwind - Phone Call Lead | WEBSITE_CALL | PHONE_CALL_LEAD | yes — silent since June |
| 7635680357 | WC Leads | UPLOAD_CLICKS | CONTACT | yes |
| 7635680543 | WC Call | UPLOAD_CALLS | CONTACT | yes — has never recorded an event |
| **7461619140** | **Softwind Submit lead form** | **WEBPAGE** | **SUBMIT_LEAD_FORM** | **DEMOTED this run** |

The duplicate form credit is closed: one submission now produces one
`SUBMIT_LEAD_FORM` credit instead of two. `WC Leads` remains a third possible
credit for the same lead and stays a **DEFERRED** watch item — it is not
demoted, because it still carries the only credit Patio recorded in August.

## 5. WhatConverts phone repair — BLOCKED-ACCESS

`WHATCONVERTS_API_TOKEN` is **declared in `.env` but empty (length 0)**. The
WhatConverts API returned **HTTP 401** on every authentication form attempted
(basic key:secret, basic token-as-user, bearer header, `api_key` query param).
No usable credential exists in this project, so none of §6's ten steps could be
performed. **No WhatConverts configuration was changed.**

Evidence re-confirmed read-only: both pages render `(631) 502-7946`; swap profile
197159 looks for `6315025402` and would insert `6315535927`; neither number
appears in the DOM; the rendered number is identical before and after every
script runs. The swap cannot fire.

The exact implementation plan is ready in `21-TRACK-A-phone-repair.md`. It needs
(a) WhatConverts admin access and (b) **BLOCKED-TRUTH**: confirmation of which
number is the real business destination and where the tracking number routes.

## 6. Landing-page telephone link — BLOCKED-ACCESS

Both pages carry a truncated `tel:(631)` anchor beside the correct
`tel:(631) 502-7946`. Repair requires authenticated site access; **`.env`
contains no WordPress or hosting credential of any kind**, and the project has no
site-write client code. No backup could be taken and no revision could be saved,
so §7's preconditions fail at step 2. **No website change was made.**

## 7. Attribution repair — APPLIED via the fallback route

**Route selected: campaign-level UTM suffix (§8 fallback).**
The preferred native WhatConverts↔Google Ads integration is **BLOCKED-ACCESS**
for the reason in §5 above — it could not be verified, connected or tested.

**Suffix applied to Patio and Pavers only (147 chars):**

```
utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}&utm_device={device}
```

### Deviation from the suffix proposed in the instruction — deliberate

The instruction proposed `utm_content={creative}` plus `utm_adgroup={adgroupid}`.
The 2026-09-03 A/B probe proved WhatConverts reads `utm_content` into the slot
immediately after campaign, and does **not** read the non-standard `utm_adgroup`.
Sending `{creative}` (the **ad ID**) there would have delivered campaign +
keyword + ad and **no ad group** — and ad group is one of the three fields this
repair exists to restore. Changes made:

| Change | Reason |
|---|---|
| `utm_content={creative}` → `utm_content={adgroupid}` | puts the ad group where WhatConverts actually reads it |
| dropped `utm_adgroup={adgroupid}` | non-standard, not read, now redundant |
| dropped `utm_network={network}` | not read by WhatConverts; ClickCease already captures `nw={network}` |
| kept `utm_matchtype`, `utm_device` | valid, useful in GA4, device was explicitly named as a field to capture |

### Validation completed before deployment

| Check | Result |
|---|---|
| ValueTrack parameters valid | `{campaignid} {adgroupid} {keyword} {matchtype} {device}` all valid |
| No duplication with ClickCease | ClickCease's `adgrp/kw/nw/cpn/device/pl/adpos/loc*` are its **own tracker** params, consumed at `monitor.clickcease.com`, never reaching the landing page except inside `url={lpurl}` |
| No existing suffix overwritten | account and both campaign suffixes were UNSET |
| Landing pages receive the parameters | **PASS** — direct non-paid probe with the account's real campaign and ad group IDs; both pages HTTP 200 |
| WhatConverts maps them | **PASS** — campaign `23484806108`/`23489296528`, ad group `189191824262`/`191263597345`, keyword all captured in `wc_client` |
| Scope | Patio and Pavers only |
| ClickCease template | untouched, and the executor branch is structurally unable to write it |

### One thing not yet proven — FUTURE-DATA-REQUIRED

Whether ClickCease's redirect preserves the suffix inside `url={lpurl}` cannot be
proven without a real paid click, and no ad was clicked to manufacture a test.
Google appends the suffix to the final URL before encoding it into `{lpurl}`, so
it should survive. **The failure mode is silent — no UTMs arrive, exactly as
today — not a broken landing page**, because both pages are proven to accept
these exact parameters. Confirmed at the 24–72h checkpoint.

## 8. P1 decision — DEFERRED, structure retained

**Decision: leave the paused `Paver Patio Installation Near Me` ad group paused
and its keywords unchanged. `PLAN-SLM-P1A-GUARD` (`00FA45112351`) was NOT
executed.**

The instruction's own test is whether it "provides a real safety or serving
benefit beyond the already-paused ad group." It does not:

- the ad group is PAUSED, so none of its seven keywords can serve today;
- the keywords are **relevant high-intent paver-patio installation terms**
  (`paver patio installation`, `paver patio installation near me`,
  `patio paver installers near me`, `brick paver installers near me`) — exactly
  the demand this account should keep;
- pausing them adds one more step to a future controlled consolidation without
  reducing any live risk;
- three major controls changed today; the serving campaigns should now collect
  clean post-P0 data undisturbed.

Retained for a future controlled consolidation or test. The two ENABLED RSAs in
the same paused group are recorded as a watch item — the executor has no
ad-status branch, and creating one is not justified for a dormant risk.

## 9. P2 monitoring dates — FUTURE-DATA-REQUIRED

All America/New_York. None of these has happened.

| Checkpoint | Date | Command |
|---|---|---|
| Same-day configuration QA | **2026-09-03** — DONE this run | `slm_0903_baseline2.py` |
| 24–72h serving, tracking, query quality, pacing | **2026-09-04 → 2026-09-06** | `slm_0903_baseline2.py`, then confirm a real paid click carries the UTMs |
| 7-day search-term and qualified-lead review | **2026-09-10** | `slm_0903_performance.py`, `slm_0903_classify.py` |
| 14-day CPQL and estimate quality | **2026-09-17** | `slm_0903_bid_bud_evidence.py` — also the ceiling step-down decision ($16→$14, $18→$16) |
| 30-day keep / modify / rollback | **2026-10-03** | full re-read + `slm_0903_preflight_exec.py` |

**Smart Bidding remains NOT READY.** Reliable call attribution is still missing
(TRACK-A blocked), lead qualification is undefined, and the last lead-type credit
of any kind was 2026-08-22. Stay on Maximize Clicks with the applied ceilings.

## 10. Current live state

| Item | Patio | Pavers |
|---|---|---|
| Status / serving | ENABLED / SERVING | ENABLED / SERVING |
| CPC ceiling | **$16.00** | **$18.00** |
| Daily budget | **$24.00** | **$32.00** |
| Bidding strategy | TARGET_SPEND (Maximize Clicks) | TARGET_SPEND |
| Final URL suffix | SET (147 chars) | SET (147 chars) |
| Search Partners / Display / AI Max | off / off / off | off / off / off |
| Location option | PRESENCE | PRESENCE |
| Final URL | `offer.softwindli.com/patio/` | `offer.softwindli.com/pavers/` |

**Pacing:** MTD $248.36 · 27 days remaining · run rate $62.88/day
Projection **$1,760.36** (sum of budgets) / **$1,946.26** (run rate) —
**both under the $2,000 cap**, $239.64 headroom. No budget was increased.

**Counts:** 695 keywords (0 Broad) · **1,771 campaign negatives** · all 96 NEG-3
negatives verified present · 7/7 asphalt keywords still paused · 8 ENABLED ads in
serving groups, **all APPROVED**.

**September-to-date query mix** (6 terms, $106.15 visible — all of it *predating*
the negatives): KEEP 22.9%, **UNRESOLVED 77.1%**. That 77% is driveway and
concrete intent, which reinforces how much rides on the service-truth answer.
The post-NEG-3 query mix is a 24–72h checkpoint item.

## 11. Protected services — confirmed unchanged

Tested each canonical intent against all 96 live negatives:

| Protected service | Result |
|---|---|
| Driveway paver installation | **NOT blocked** |
| Concrete patios | **NOT blocked** |
| Bluestone | **NOT blocked** |
| Masonry repair | **NOT blocked** |
| Resurfacing | **NOT blocked** |
| Pool decks | **NOT blocked** |
| Pool coping | **NOT blocked** |

None was paused, negated, promoted or claimed.

## 12. Unrelated resources — confirmed unchanged

ClickCease account tracking template still `monitor.clickcease.com`, unmodified;
235 IP-block criteria on each serving campaign. All four other campaigns still
PAUSED with unchanged budgets and statuses. Sibling account `1521725229` never
touched. No geographic change, no campaign/ad group/ad creation, no enablement,
no deletion, no Broad Match, no Google recommendation applied.

## 13. Rollback instructions

| Change | Rollback |
|---|---|
| CONV-2 | Set `conversion_action.primary_for_goal = True` on `7461619140`. One field. `include_in_conversions_metric` follows automatically. |
| TRK-B1 | Clear `campaign.final_url_suffix` on `23484806108` and `23489296528`. Restores the recorded prior UNSET state. |
| BID-2 (earlier) | Clear `target_spend.cpc_bid_ceiling_micros` on both campaigns |
| BUD-2 (earlier) | Restore `amount_micros` 33000000 on budgets `15309303030` and `15314089588` |
| KW-2 (earlier) | Status → ENABLED on the seven `196134824089~<criterion_id>` pairs |
| NEG-3 (earlier) | Remove the 96 created `campaign_criterion` rows, listed in `36-readback-NEG-3.csv` |

Nothing was deleted or renamed, so every rollback restores a recorded prior value.

## 14. Remaining blockers

| Item | Label | Cause |
|---|---|---|
| WhatConverts phone-swap repair | **BLOCKED-ACCESS** | credential variable is empty; API returns 401 |
| Which number is the true business destination | **BLOCKED-TRUTH** | owner confirmation only |
| Landing-page `tel:(631)` repair | **BLOCKED-ACCESS** | no site/hosting credential exists |
| Native WhatConverts↔Google Ads integration | **BLOCKED-ACCESS** | same credential gap |
| ClickCease forwards the UTM suffix | **FUTURE-DATA-REQUIRED** | needs one real paid click |
| Post-negative query mix | **FUTURE-DATA-REQUIRED** | negatives applied late 2026-09-03 |
| CPQL, sold-job rate, profit | **BLOCKED-TRUTH** | no qualified-lead definition, no CRM join |
| Service truth (7 protected themes) | **BLOCKED-TRUTH** | owner answer; 77.1% of Sept spend sits here |
| Ad claims (licensed, insured, warranty, response time) | **BLOCKED-TRUTH** | live in ads today, unverified |
| Desktop Chrome/Edge 403 | **FUTURE-DATA-REQUIRED** | needs a real non-headless browser; desktop converts at 3.53%, so users are evidently not blocked |
| `PLAN-SLM-P1A-GUARD` `00FA45112351` | **DEFERRED** | no safety benefit today; retained for controlled consolidation |
| `WC Leads` third-credit demotion | **DEFERRED** | wait for the WhatConverts repair |

---

**Recovery status: P0 complete and measurement repaired to the limit of available
access.** Six packages applied across the program — BID-2, BUD-2, KW-2, NEG-3,
CONV-2, TRK-B1 — every one validated, executed atomically, read back, and proven
against a full unchanged-resource comparison. Next checkpoint **2026-09-04**.
