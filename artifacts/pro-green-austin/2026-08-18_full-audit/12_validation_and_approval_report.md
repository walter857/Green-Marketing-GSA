# 12 — Validation and Approval Report (v2)

**Pro Green - Austin - Live | `7380491929` | outdoor design & build**
**Plan version 2 · regenerated 2026-08-19 · Mode: READ · PHASE 1 of 2**
**NO EXTERNAL CHANGES MADE.**

> **Version 1 (2026-08-18, master `38314B507F47`) is REJECTED. Every v1 fingerprint —
> `5F2D15648457`, `1AE1B904B680`, `FC54F5319D1B`, `363B8D6D60D5` — is void and must never be
> executed.** The validator asserts that none of those four subplan codes appears anywhere in the
> v2 plan.

---

## 1. What changed from the rejected v1

| # | Correction required | What v2 does |
|---|---|---|
| 1 | ClickCease is active and must remain | **EXR-003 withdrawn.** The template is not cleared and no fingerprinted action touches `customer.tracking_url_template`. Replaced by **`BLK-001`**, a **BLOCKED, non-fingerprinted** proposal that preserves the whole template byte for byte and changes only `ccpturl`, pending domain verification. Nothing queries, disables or modifies the ClickCease manager. |
| 2 | Do not remove the ad schedule; do not go 24/7 | **EXR-004 and EXR-005 withdrawn.** Replaced by four paired actions that remove the 14 existing criteria and recreate 14 at **09:00–18:00 account time = 08:00–17:00 America/Chicago**, Monday–Sunday. Exact criterion IDs and rollback values are listed per campaign. |
| 3 | Keep `emergency`; trim the additions | `emergency` removal **withdrawn**. Additions cut from 21 distinct terms to **8**. The 13 impression-only terms, including both asphalt variants, are recorded as **WATCH** with object count 0. |
| 4 | Keep the parent-asset exclusions and the $22 ceiling | Both kept, unchanged. |
| 5 | Prove the conversion set before regenerating | Demotions grow from 4 to **6**. Full proof in §5. |
| 6 | Do not fingerprint website work | `SITE_OR_TRACKING` is now an **empty subplan**; the content is a developer remediation specification with no fingerprint. |
| 7 | State Phase 1; add a Phase 2 recommendation | The plan declares `PHASE 1 of 2` and carries a `phase_2_recommendation` block that creates nothing. |
| 8 | Rebuild 06, 11, 12; rerun validators; new fingerprints | Done. See §8 and §9. |

**A correction to my own v1 numbers.** v1 said "eight enabled actions feed the Conversions column"
and "13 are ENABLED". Both were wrong. The account has **16** conversion actions, **14 ENABLED**,
**2 HIDDEN**, and **9** feeding the Conversions column.

---

## 2. Identity gate and drift check

| Item | Required | Observed 2026-08-19 | Result |
|---|---|---|---|
| Exact child account name | `Pro Green - Austin - Live` | `Pro Green - Austin - Live` | exact match |
| Child customer ID | `7380491929` | `7380491929` | exact match |
| Exact service | outdoor design & build | outdoor design & build | match |
| Manager customer ID | discover read-only | `3373711342` | confirmed |
| Manager / test account | must be false | false / false | pass |

**Drift since the 2026-08-18 snapshot: NONE.** Re-read today and byte-identical:
`customer.tracking_url_template`; both budgets at `32890000` micros; both campaigns
`TARGET_SPEND` with `cpc_bid_ceiling_micros = 0`; both `excluded_parent_asset_field_types = []`;
all 14 ad-schedule criteria at `start_hour 8 / end_hour 17`. Evidence:
`clients/pro-green-austin/snapshots/reverify-2026-08-19.json`.

---

## 3. ClickCease — BLK-001, blocked and not approvable

**ClickCease is active and stays active.** No fingerprint in this package touches it.

**Current value, verified five times across 2026-08-18 and 2026-08-19, stable:**

```
https://monitor.clickcease.com/tracker/tracker.aspx?id=Y6qzID4E9cPYCj&adpos={adposition}
&locphisical={loc_physical_ms}&locinterest={loc_interest_ms}&adgrp={adgroupid}&kw={keyword}
&nw={network}&url={lpurl}&cpn={campaignid}&device={device}&ccpturl=offer.sehydroseed.com
&pl={placement}
```

**Proposed value — one parameter changed, everything else preserved byte for byte:**

```
… &device={device}&ccpturl=offeraustin.progreenlandscapesolutions.com&pl={placement}
```

| Preserved unchanged | `monitor.clickcease.com/tracker/tracker.aspx`, `id=Y6qzID4E9cPYCj`, `{adposition}`, `{loc_physical_ms}`, `{loc_interest_ms}`, `{adgroupid}`, `{keyword}`, `{network}`, `{lpurl}`, `{campaignid}`, `{device}`, `{placement}`, and parameter order |
|---|---|
| **Only difference** | `ccpturl=offer.sehydroseed.com` → `ccpturl=offeraustin.progreenlandscapesolutions.com` |

**Why this is blocked rather than fingerprinted.**
`offeraustin.progreenlandscapesolutions.com` is the host of all 12 live ad destinations, which makes
it the likely correct value — but `ccpturl` must match the domain actually registered inside the
ClickCease account, and that cannot be read from Google Ads and must not be guessed. Applying a
second wrong value would be no better than the current one. **Treated as a proposed value only.**

**Unblock condition:** Green Marketing confirms the exact registered domain from the ClickCease
account itself. The proposal is then regenerated with the verified value and issued its own
fingerprint for separate approval.

Validator assertions, all passing: the template is preserved except for `ccpturl`; the recorded
current value matches the live account today; the proposed domain is flagged unverified; no
fingerprinted action carries `field_mask: tracking_url_template`; and nothing references the
ClickCease manager.

---

## 4. Ad schedule — corrected, not removed

The campaigns keep a schedule and do **not** become eligible 24/7.

America/Chicago is one hour behind America/New_York year-round and both observe US daylight saving
on the same dates, so a fixed **+1 hour** offset holds all year with no seasonal correction.

**Removed — 14 criteria, exact IDs.** Both campaigns share the same deterministic criterion IDs, so
each must be addressed by its full resource name `customers/7380491929/campaignCriteria/{campaign}~{criterion}`:

| Day | Criterion ID | Current (account time) | Rollback value |
|---|---|---|---|
| MONDAY | 303268 | 08:00 → 17:00 | `start_hour 8, end_hour 17, start_minute ZERO, end_minute ZERO, no bid modifier` |
| TUESDAY | 313268 | 08:00 → 17:00 | same |
| WEDNESDAY | 323268 | 08:00 → 17:00 | same |
| THURSDAY | 333268 | 08:00 → 17:00 | same |
| FRIDAY | 343268 | 08:00 → 17:00 | same |
| SATURDAY | 353268 | 08:00 → 17:00 | same |
| SUNDAY | 363268 | 08:00 → 17:00 | same |

× 2 campaigns (`24053505501`, `24053505504`) = **14 criteria removed**.

**Created — 14 criteria.** Monday through Sunday, `start_hour 9`, `end_hour 18`,
`start_minute ZERO`, `end_minute ZERO`, no bid modifier, on each campaign:

| Account time (America/New_York) | Market time (America/Chicago) |
|---|---|
| 09:00 → 18:00 | **08:00 → 17:00** |

**Named risk:** removal and creation are separate operations. If the create half fails, the campaign
would be left with no schedule and would run all day — the exact outcome we were told to avoid. Both
halves must go in **one atomic mutate with partial failure disabled**, and the readback must confirm
exactly 7 criteria per campaign before the operation is called done. New criterion IDs are assigned
by Google and are not knowable in advance, so the readback matches on day and hour values, not IDs.

---

## 5. Conversions — the proof work, done before the fingerprint

### 5a. Every action that will remain Primary — exactly three, one per real lead event

| ID | Name | Type / Category / Origin | Counting | Threshold | Biddable on both live campaigns | Real event measured |
|---|---|---|---|---|---|---|
| `7644242327` | **WC leads** | UPLOAD_CLICKS / CONTACT / WEBSITE | ONE_PER_CLICK | — | yes | one website **form submission** |
| `6885610317` | **Progreen - Lp - Phone Call Leads** | WEBSITE_CALL / PHONE_CALL_LEAD / WEBSITE | ONE_PER_CLICK | **30s** | yes | one **connected call from the website** |
| `6566620547` | **Calls from ads** | AD_CALL / PHONE_CALL_LEAD / CALL_FROM_ADS | MANY_PER_CLICK | **60s** | yes | one **connected call from the ad** |

Three distinct events, three actions, no overlap. The validator maps each surviving primary action
to a named event and fails if any event has two.

### 5b. Do `WC leads` and `Progreen - Lp - Submit Lead Form` measure the same form submission?

**Yes — they are serial replacements for one event, not two events.** Evidence from 260
day-and-action conversion rows across the full history:

| Action | First conversion | Last conversion | Total | Active days |
|---|---|---|---|---|
| `GA Submit Form` | 2023-07-08 | 2024-09-13 | 14 | 14 |
| `Progreen - Lp - Submit Lead Form` | **2024-09-17** | **2026-01-18** | 196 | 134 |
| `WC leads` | **2026-07-27** | 2026-08-04 | 2 | 2 |

`Progreen - Lp - Submit Lead Form` began firing **four days after** `GA Submit Form` stopped.
`WC leads` began **after** `Progreen - Lp - Submit Lead Form` stopped. **Same-day co-occurrence
across every pair: zero.** They are three successive ways of capturing one thing — a website form
submission on the Pro Green Austin properties.

**So no double count has happened yet.** But repairing the on-page tag under `SPEC-002` would make
both fire on the same submission immediately. That is why `Progreen - Lp - Submit Lead Form` is
demoted now rather than later.

**Which one survives, and why `WC leads`:** it is the only form-lead source producing anything in
the live window, it deduplicates at source, and it is the path that will later carry qualified-lead
and sold-job status. `Progreen - Lp - Submit Lead Form` stays ENABLED and fully measurable as
secondary, so a WhatConverts outage would be visible immediately.

**Consequence, stated plainly:** after this change the `SUBMIT_LEAD_FORM / WEBSITE` goal category
has no primary action. Form leads still count and still feed bidding, but under
`CONTACT / WEBSITE`, which is biddable on both campaigns. If `SPEC-002` repairs the on-page tag and
WhatConverts is retired, flip the two back under a fresh CONVERSIONS approval.

**Honest limit:** this is structural and temporal proof, not record-level. Proving that one specific
submission was counted twice needs either WhatConverts lead records (PII, not read) or the
`SPEC-002` test submission.

### 5c. Does `Progreen - Lp - Phone Call Leads` measure a connected call or a phone-link click?

**A connected call of at least 30 seconds.** Two independent indicators:

- `conversion_action.type = WEBSITE_CALL`, which Google defines as a call placed from a number on
  the website and tracked with a Google forwarding number.
- `phone_call_duration_seconds = 30`. A duration threshold is only meaningful for a call that
  actually connects; a click-based action cannot have one. Note it is **30**, deliberately set,
  while every click-based action in this account carries the inert account default of 60.

Contrast with the three click-only actions, all demoted or already secondary:

| Action | Type | What it really counts |
|---|---|---|
| `GA Call Btn Click` | WEBPAGE / CONTACT | a click on a phone link — 0 conversions all-time |
| `…(web) phone_call_click` | GA4 custom, MANY_PER_CLICK | the GA4 event literally named `phone_call_click` |
| `Clicks to call` | GOOGLE_HOSTED | a click on a hosted-surface call button (already not in the column) |

**Caveat carried forward:** `WEBSITE_CALL` needs Google call reporting to own number insertion on
the page. WhatConverts dynamic number insertion is active on these properties, which is the leading
hypothesis for why this action last fired on 2025-11-10 and reads 0 in the live window. It is
retained as primary because it is biddable, it measures the right event, and it has 12 historical
conversions proving it can fire. If `SPEC-002` shows it cannot fire while WhatConverts owns the
swap, we revisit under a separate CONVERSIONS approval.

### 5d. Custom conversion goals — the documented override does not apply here

Google documents that `primary_for_goal = false` normally makes an action non-biddable, but that a
**custom conversion goal can override that behaviour**. Checked directly:

| Query | Result |
|---|---|
| `SELECT … FROM custom_conversion_goal` | **0 rows** — no custom conversion goal exists in this account |
| `conversion_goal_campaign_config` for `24053505501` | `goal_config_level = CAMPAIGN`, `custom_conversion_goal` **empty** |
| `conversion_goal_campaign_config` for `24053505504` | `goal_config_level = CAMPAIGN`, `custom_conversion_goal` **empty** |

**Confirmed: none of the six demoted actions belongs to a custom conversion goal, and no custom goal
exists that could keep any of them biddable.** Setting `primary_for_goal = false` will make each one
non-biddable as documented. This check is now a permanent part of `scripts/validate_audit_package.py`
and is re-run at preflight.

### 5e. The six demotions

| # | ID | Name | Family | Why |
|---|---|---|---|---|
| CNV-001 | 6557277268 | GA Submit Form | duplicate form lead | Legacy; 14 conversions, none since 2024-09-13; superseded four days later |
| CNV-002 | 6557280400 | GA Call Btn Click | phone-click only | Click on a phone link; 0 conversions all-time |
| CNV-003 | 7389543347 | …(web) form_submission | duplicate form lead | GA4 import, MANY_PER_CLICK, 90-day window vs 30 elsewhere; three GA4 properties in play |
| CNV-004 | 7389543053 | …(web) phone_call_click | phone-click only | GA4 event is a tel: link click; MANY_PER_CLICK compounds it |
| **CNV-005** | 6885608055 | Progreen - Lp - Submit Lead Form | duplicate form lead | **New in v2.** Same event as `WC leads`; see §5b |
| **CNV-006** | 7644612703 | WC calls | duplicate call lead | **New in v2.** 0 conversions all-time; would duplicate both retained call actions; its `CONTACT / CALL_FROM_ADS` category is **not biddable** anyway |

**Readback assertion:** re-read `primary_for_goal` **and** `include_in_conversions_metric`. If the
second does not follow to `false`, stop and plan a separate mutation rather than assuming. Re-read
`custom_conversion_goal` to confirm it is still empty.

---

## 6. Negative keywords — 8 added, 13 watched, 7 removed

### Added: 8 terms × 2 campaigns = 16 objects. Every one has observed live spend and zero conversions.

| Term | Family | Live impressions | Clicks | Cost | Conversions |
|---|---|---|---|---|---|
| mcdugald steele | competitor | 2 | 1 | $35.10 | 0 |
| mirror lake landscaping | competitor | 1 | 1 | $29.17 | 0 |
| spring texas | wrong market (Houston area) | 1 | 1 | $29.17 | 0 |
| agc turf | competitor | 3 | 1 | $24.51 | 0 |
| ulm austin | competitor | 4 | 1 | $24.24 | 0 |
| garden goat | competitor | 2 | 1 | $19.42 | 0 |
| agave landscaping | competitor | 2 | 1 | $18.87 | 0 |
| astoria lighting | competitor | 9 | 1 | $10.29 | 0 |

All campaign-scoped PHRASE negatives on both live campaigns. Conflict rechecked 2026-08-19: **zero**
block a live positive keyword, **zero** block a query that ever converted, **zero** contain a
protected term.

**One overlap I am flagging rather than hiding.** `mirror lake landscaping` and `spring texas` both
match the same observed query, `mirror lake landscaping spring texas` — the only query either has
been seen on. By the same reasoning applied to the asphalt pair, one of them is arguably redundant
today. They are kept because they do different jobs going forward: the first blocks that competitor
anywhere, the second blocks Houston-area geography generally. If you would rather add only one, say
which and I will regenerate; the fingerprint changes either way.

### Watched, not added: 13 terms, object count 0

Eleven competitor names with impressions but **no click and no cost**: allied outdoor solutions,
casas landscaping, cedarcrest, clean scapes, cooper and company, cutters landscaping, ground and
garden, ps landscapes, stallion paving, stevens paving, waterloo turf.

Plus **`asphalt`** and **`asphalt paving`**. Both are impression-only, and a PHRASE negative on
`asphalt` would already cover `asphalt paving`, so adding both would be redundant. **Neither is
added.** Re-evaluate any WATCH term the moment it takes a click.

### Removed: 7 blocking negatives

| Term | Match | Shared set | Criterion ID | What it unblocks |
|---|---|---|---|---|
| `cost` | BROAD | account-level list `11260450591` | 10023121 | every cost query, account-wide (protected term) |
| `hire` | PHRASE | `General` `10670796064` | 62617751 | "hire a hardscape contractor" (protected term) |
| `shade` | PHRASE | `General` `10670796064` | 100398664 | shade structure, shade sail, patio shade cover |
| `oasis` | BROAD | account-level list | 10066610 | "backyard oasis design" |
| `keystone` | BROAD | account-level list | 10063811 | "keystone retaining wall installation" |
| `black` | BROAD | account-level list | 10090111 | "black star gravel", "black limestone patio" |
| `replacement` | BROAD | account-level list | 10073261 | "paver replacement", "patio replacement" |

**`emergency` is retained.** Emergency intent is not supported for outdoor design-and-build work, so
the existing negative is correct. The v1 removal is withdrawn.

**A precision point that matters at execution time.** These criterion IDs are **shared across
several shared sets**. `hire` (62617751) and `shade` (100398664) are each members of three or four
sets, most of them REMOVED or not linked to a live campaign. Only the memberships named above affect
the live campaigns, so every removal is addressed by its **full `shared_criterion` resource name**
`customers/7380491929/sharedCriteria/{shared_set_id}~{criterion_id}`, never by criterion ID alone.
The validator asserts this on all seven.

---

## 7. Kept from v1, unchanged

| Action | Objects | Why it stands |
|---|---|---|
| **EXR-001 / EXR-002** — exclude parent `SITELINK` and `STRUCTURED_SNIPPET` on both campaigns | 2 | Three account-level auto sitelinks send Austin spend to `/dfw/` and `/houston/` (63 and 57 attributed impressions, zero conversions), and an auto snippet serves "Over 20 Years Of Experience", unsupported by the first-party site. Both campaigns already carry six advertiser sitelinks and their own structured snippet, so no coverage is lost. |
| **$22.00 Maximize Clicks CPC ceiling**, both campaigns | 2 | $27.85 average CPC with single clicks at $42.61, $48.15 and $55.31. A ceiling raises clicks per dollar without a strategy change, a learning reset, or asking Smart Bidding to trust an unreliable conversion set. |
| **Budget $39.47 / $26.31** | 2 | Total unchanged at $65.78/day, $1,999.71 per 30.4 days. Outdoor Living loses 31.8% of impressions to budget; Hardscape loses 27.7% to rank, which money cannot buy. |

---

## 8. Validation results — 107 checks, 107 passed, 0 failed

`scripts/validate_audit_package.py`, extended for this revision.

| Group | Checks | Result |
|---|---|---|
| Client truth | 9 | pass |
| Mode | 2 | pass |
| Coverage | 10 | pass — 12/12 campaigns, 55/55 ad groups, 987/987 keywords, 12,537/12,537 search terms, 13/13 destinations |
| Conversion isolation | 5 | pass |
| **Custom conversion goals** | **3** | **pass — 0 custom goals; neither campaign references one; the biddability override cannot apply** |
| **Count once** | **6** | **pass — 3 surviving primaries, 3 distinct events, no event counted twice** |
| **ClickCease** | **8** | **pass — nothing fingerprinted touches it; BLK-001 preserves the template and flags the domain unverified** |
| **Ad schedule** | **7** | **pass — 14 removed / 14 created, all 09:00–18:00 account time, seven days, rollback values present, never 24/7** |
| **Negatives** | **10** | **pass — exactly the 8 approved terms, all with real spend; asphalt pair excluded; emergency retained; exactly the 7 removals; 13 WATCH at object count 0** |
| **Phase discipline** | **4** | **pass — declares Phase 1; Phase 2 creates nothing; no keyword or ad touched** |
| **Site spec** | **6** | **pass — not fingerprinted; all 12 attribution fields specified; {Referer} covered; test gated; GA4 removal blocked pending system-of-record; no unilateral consent change** |
| Mutation necessity / status / resource IDs | 8 | pass |
| Budget math | 5 | pass |
| Location targeting | 9 | pass |
| Unsupported claims | 3 | pass |
| Secrets | 2 | pass |
| Version hygiene | 3 | pass — no rejected v1 subplan code appears; the v1 master appears only in `supersedes` |
| Bundle | 1 | pass |

**Other validators re-run today:**

| Command | Result |
|---|---|
| `scripts/validate_work_order.py` | `PASS \| Pro Green - Austin - Live \| 7380491929 \| hardscaping \| outdoor design & build` |
| `scripts/verify_setup.py --online` | `Connection: OK … Preflight: PASS` |
| `scripts/validate_location_targets.py` | `PASS \| 0 proximity + 19 postal + 5 named = 24 positive \| PRESENCE` |
| `pytest tests -q` | 465 passed |

**Artifact hashes (sha256, first 16), regenerated files in bold:**

| Hash | Bytes | File |
|---|---|---|
| `d5db4301f82d474b` | 10,766 | 00_identity_and_source_log.md |
| `c6daf7a508d61d65` | 5,920,940 | 01_fresh_account_snapshot.json |
| `d2ed743970b1630f` | 19,159 | 02_executive_audit.md |
| `11b59eddd5026179` | 22,570 | 03_campaign_and_ad_group_verdicts.csv |
| `e8b75fa43dee4e6a` | 294,397 | 04_keyword_verdicts.csv |
| `fa044f36fe382434` | 3,523,410 | 05_search_term_verdicts.csv |
| **`51fa01885aa298d2`** | **23,784** | **06_negative_keyword_plan.csv** |
| `d77ea2958cc1c3f7` | 18,411 | 07_conversion_and_tracking_audit.md |
| `2d4d0139a917f04f` | 33,164 | 08_ads_assets_and_policy_audit.csv |
| `030589733a663516` | 35,311 | 09_landing_page_and_market_integrity_audit.csv |
| `e2947ba870adbdbc` | 17,927 | 10_location_budget_schedule_and_device_plan.md |
| **`c103773093e9be18`** | **89,566** | **11_exact_change_plan.yaml** |
| — | — | **12_validation_and_approval_report.md** (this file; hash printed by the validator run after it is written) |

---

## 9. Approval bundle — v2

**Account:** `Pro Green - Austin - Live` | `7380491929` | outdoor design & build
**Manager:** `3373711342`
**MASTER PLAN FINGERPRINT: `DAB68F9E21AE`**

| Subplan | Actions | Objects | Fingerprint | Paste back to approve |
|---|---|---|---|---|
| STATUS | 0 | 0 | *(empty)* | — nothing proposed |
| **BUDGET** | 2 | 2 | **`F7C934DB6936`** | `APPROVE BUDGET F7C934DB6936 FOR 7380491929` |
| **EXISTING_RESOURCES** | 31 | 55 | **`2B3D1DD13155`** | `APPROVE EXISTING_RESOURCES 2B3D1DD13155 FOR 7380491929` |
| **CONVERSIONS** | 6 | 6 | **`A6FAF33D466C`** | `APPROVE CONVERSIONS A6FAF33D466C FOR 7380491929` |
| CREATE_PAUSED | 0 | 0 | *(empty)* | — Phase 1 creates nothing |
| SITE_OR_TRACKING | 0 | 0 | *(empty)* | — specification only, deliberately not approvable |
| ENABLE | 0 | 0 | *(empty)* | — nothing to enable |
| BLK-001 (ClickCease `ccpturl`) | — | 1 | **none — BLOCKED** | not approvable until the ClickCease domain is verified |

**EXISTING_RESOURCES, 31 actions / 55 objects, itemised:**

| Group | Actions | Objects |
|---|---|---|
| Exclude parent SITELINK + STRUCTURED_SNIPPET | 2 | 2 |
| Remove 08:00–17:00 ad schedule | 2 | 14 |
| Create 09:00–18:00 ad schedule | 2 | 14 |
| $22.00 CPC ceiling | 2 | 2 |
| Add 8 negatives × 2 campaigns | 16 | 16 |
| Remove 7 blocking negatives | 7 | 7 |
| **Total** | **31** | **55** |

Fingerprints come from `scripts/plan_fingerprint.py`, which calls the repository's own
`gm_gsa.safety.approval_code`. No approval code was invented.

You may paste more than one line in a single reply. A general instruction such as "make any needed
changes" is not a substitute — each fingerprint approves exactly the resources and values in
`11_exact_change_plan.yaml` and nothing else.

---

## 10. Execution protocol, unchanged

1. New read-only preflight snapshot.
2. Compare every target against the approved plan, re-reading `customer.tracking_url_template`,
   both budgets, both bidding strategies, all 14 ad-schedule criteria, the seven
   `shared_criterion` memberships, and `custom_conversion_goal`.
3. **On any drift: invalidate the fingerprint, regenerate, stop for fresh approval.**
4. Validate-only requests where supported.
5. **Atomic mutate, partial failure disabled** — mandatory for the ad-schedule pair.
6. Apply only approved values. Never delete. Read every changed resource back.
7. Assert budget: enabled in-scope daily total **$65.78**, 30.4-day projection **$1,999.71**,
   each shared budget counted once, no campaign enabled by accident, 24 locations and PRESENCE
   intact.
8. Assert schedule: exactly 7 criteria per campaign, all `start_hour 9` / `end_hour 18`.
9. Assert conversions: exactly three primaries in the Conversions column —
   `7644242327`, `6885610317`, `6566620547` — and `custom_conversion_goal` still empty.
10. On partial success: stop, inventory every created or changed resource ID, produce a recovery
    plan. Do not rerun blindly.

---

## 11. Open questions

| # | Question | Blocks | Recommendation |
|---|---|---|---|
| 1 | **Exact domain registered in ClickCease for Pro Green Austin** | BLK-001 only | Confirm from the ClickCease account. `offeraustin.progreenlandscapesolutions.com` is the likely value but is unverified. |
| 2 | Phone-answering hours | nothing | The 08:00–17:00 Central schedule now matches ordinary business hours. If calls cannot be answered in that window, add a call-asset schedule. |
| 3 | Can Pro Green support "Over 20 Years Of Experience"? | nothing | EXR-001/002 stop it serving either way. Needed before it can appear in Phase 2 ad copy. |
| 4 | GA4 system-of-record property | SPEC-003 | Likely `G-MHX199EBNJ`, present on both hosts. **No removal is proposed until this is named.** |
| 5 | Is `West University` the Austin neighborhood? | nothing | No geo change proposed. Delivery is 100% Austin metro. |
| 6 | Job economics: average revenue, gross margin, close rate, target CPL | profitability reporting | Supply and CPQL, CAC, ROAS and profit after ad spend become computable. |
| 7 | Approve the `SPEC-002` tracking test? | proving P0-1 | Five-step protocol in `07` §11. Creates a real CRM record, so it needs its own authorisation. |
| 8 | Add both `mirror lake landscaping` and `spring texas`, or just one? | EXISTING_RESOURCES fingerprint | Keep both — they do different jobs. Say the word and I regenerate with one. |

---

## 12. Phase discipline

**This is Phase 1 of 2.** It adds no keyword, writes no RSA and does not restructure the 24 ad
groups. Phase 1 is safety, market integrity and measurement only.

**Phase 2 is a recommendation, not a plan.** It creates and enables nothing now. Its entry gate:
`SPEC-001` and `SPEC-002` delivered and verified; exactly one form-lead and one call-lead definition
in the Conversions column; **15 or more conversions in a rolling 30 days**; and the ClickCease
question closed.

Phase 2 recommends keeping **Landscape Design** (the strongest pocket — $630.29, 28 of 63 clicks,
2 of 3 conversions), **Hardscaping**, **Pavers and Patios**, and **Outdoor Living | Near Me**; and
retiring or parking Fire Pits, Walkways and Driveways, which took zero clicks in 27 days. Outdoor
kitchens, concrete, masonry and deck construction are verified first-party services never
advertised — recorded as expansion candidates only, because at $65.78 a day the lever is
concentration, not expansion. Full detail in `11_exact_change_plan.yaml` under
`phase_2_recommendation`.

---

**NO EXTERNAL CHANGES MADE**
