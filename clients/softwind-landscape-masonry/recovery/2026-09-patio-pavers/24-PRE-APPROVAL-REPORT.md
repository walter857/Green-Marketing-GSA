# Softwind Landscape & Masonry — pre-approval QA gate report

**Account:** Softwind Landscape & Masonry - Live · `2429758629` · USD ·
America/New_York
**Scope:** Patio (`23484806108`) and Pavers (`23489296528`) · hard cap $2,000/month
**Report:** 2026-09-03, 20:10 America/New_York

> **NO DURABLE MUTATION OCCURRED.** No Google Ads object, website, WhatConverts
> setting, GA4 property, GTM container or CallRail configuration was changed. The
> only writes were local files in this repository. Proof in section 13.
>
> **ALL FIVE PREVIOUS APPROVAL CODES ARE OBSOLETE.** Do not use them. New codes
> are in section 8. Recorded in `10-change-packages-v2/00-obsolete-codes.json`.

---

## 1. What the gate found

The gate was worth running. It produced **six substantive corrections**, four of
which would have caused real harm or waste:

| # | Finding | Consequence had it shipped |
|---|---|---|
| 1 | **49 of the 154 proposed negatives were redundant.** An existing BROAD negative already blocks every query the proposed PHRASE negative would. | 49 wasted mutations against a Basic-access quota, and a permanently misleading plan record. |
| 2 | **The blended $22 CPC ceiling was wrong for both campaigns.** Patio has never had a daily CPC above $15.56 — $22 was a no-op there. Pavers retains identically at $18, $20 and $22, so $22 was $4 too expensive. | Patio's CPC would have kept climbing unchecked; Pavers would have overpaid on every click. |
| 3 | **One of the two conversion demotions was not a duplicate.** `Calls from ads` and `Calls from ads (1)` fired on 19 and 13 days respectively and **never once on the same day**. | An action would have been demoted on a false premise. |
| 4 | **The v1 packages could not be executed by this repository's executor at all.** They were standalone JSON in a shape `execute_approved_plan.py` cannot read, and keyword pauses had no executor branch. | The approvals would have been meaningless — nothing could have consumed them. |
| 5 | **The previous test result was reported against the wrong interpreter.** The project venv has pytest 9.1.1; the global one does not. | "376 tests, 2 pre-existing failures" was wrong. The real result is **498 passed, 0 failed**. |
| 6 | **The landing pages return HTTP 403 to some desktop user-agents.** Mobile-only QA missed it entirely. | An unexamined WAF rule sitting in front of the money pages. |

Two earlier conclusions were **strengthened**, not overturned: the WhatConverts
number-swap mismatch, and the missing-UTM cause of blank campaign/keyword — the
latter now proven by a controlled A/B rather than inferred.

## 2. Identity gate — PASS

Fresh read from inside the account at **2026-09-03 19:59:12 -04:00**
(`scripts/slm_identity_gate.py`, receipt
`snapshots/identity-gate-2026-09-03-1959.json`).

| Check | Expected | Observed | Match |
|---|---|---|---|
| Descriptive name | Softwind Landscape & Masonry - Live | Softwind Landscape & Masonry - Live | ✓ |
| Customer ID | 242-975-8629 | 2429758629 | ✓ |
| Manager account | false | false | ✓ |
| Test account | false | false | ✓ |
| `- live` marker | present | present | ✓ |
| Currency | USD | USD | ✓ |
| Time zone | America/New_York | America/New_York | ✓ |
| Manager hierarchy | under 3373711342 | 2 manager links, incl. 3373711342 | ✓ |
| Patio campaign | 23484806108 | 23484806108, ENABLED | ✓ |
| Pavers campaign | 23489296528 | 23489296528, ENABLED | ✓ |

## 3. Strict YAML validation — PASS, and the premise did not hold

`scripts/yaml_strict.py` rejects duplicate mapping keys (PyYAML's `safe_load`
silently keeps the last value). It is backed by a second, parser-independent text
scan that counts every `key:` occurrence per indent scope.

**Result on the file as it was saved: zero duplicate keys, anywhere.**

Every key the gate named was checked individually:

| Key | Result |
|---|---|
| `google_ads.live_campaigns` | present once |
| `identity_gate.per_account_confirmation_date` | present once |
| `identity_gate.per_account_confirmation_checks.name_match` | present once |
| `identity_gate.per_account_confirmation_checks.id_match` | present once |
| `offer.services_excluded` | present once, list of 8 |
| `offer.verified_usps` | **present once, at line 113, as `verified_usps: []`** |
| `service_area.geo_target_constant_ids` | present once |
| `service_area.exclusions` | present once |
| all other nested keys | no repeats |

**`verified_usps` was not defined twice.** There is exactly one textual
occurrence and it parses to an empty list. There was no inline/block conflict.

**But the audit surfaced a different, real defect: 17 fields still read UNKNOWN
that Phase A had actually verified.** That is the opposite failure — evidence
existed and was not recorded. Corrected:

| Field | Was | Now | Source |
|---|---|---|---|
| `conversion_tracking_id` | UNKNOWN | `17878095007` | live customer read |
| `live_campaigns` | UNKNOWN | 6 campaigns, exact Google Ads names + ids + statuses | live campaign read |
| `website.primary_url` | UNKNOWN | `https://softwindli.com/` | landing_page_view + ClickCease `ccpturl` |
| `website.landing_page_base_url` | UNKNOWN | `https://offer.softwindli.com/` | ad final URLs |
| `phone_display` / `phone_e164` | UNKNOWN | `(631) 502-7946` / `+16315027946` | rendered on both pages |
| `service_area.location_option` | UNKNOWN | `PRESENCE` | campaign geo_target_type_setting |
| `integrations.analytics` / `tag_manager` | UNKNOWN | GA4 / `GTM-P3LD97NN` | observed loading |
| `platform_account_spending_limit` | absent | `INFINITE` | account_budget |

**8 fields remain UNKNOWN and were left that way** — CRM, speed-to-lead, review
URL, after-hours answering, the three CRM stage mappings, and the qualified-lead
definition. All are business facts with no evidence. Every populated value now
carries an evidence tag (`[API]`, `[LP]`, `[USER]`, `[OWNER]`).

Live campaign names are now represented consistently, and the three service lists
(`services_excluded`, `services_excluded_pending_confirmation`,
`services_unresolved`) are explicitly kept separate with a note that only the
first two may ever produce a negative keyword.

## 4. Test results — 498 passed, 0 failed

Run in the project's own virtual environment (`.venv/Scripts/python.exe`), which
`pyproject.toml` configures via `[tool.pytest.ini_options]`. Nothing was
installed; the venv already had pytest 9.1.1 and google-ads 31.2.0.

| Gate | Command | Result |
|---|---|---|
| Full pytest suite | `.venv/Scripts/python.exe -m pytest -q` | **498 passed in 5.05s** |
| YAML duplicate-key test | `scripts/yaml_strict.py` on 10 files | **10/10 PASS** |
| Client configuration | `scripts/verify_setup.py` | **Preflight: PASS** |
| Work order A | `scripts/validate_work_order.py … --client client.yaml` | **PASS** — patio construction |
| Work order B | same | **PASS** — paver installation |
| Recovery-plan validation | `execute_approved_plan.py --validate-only` ×5 | **5/5 VALIDATION PASSED** |
| Fingerprint validation | executor recomputes and compares before running | **5/5 matched** |
| Rollback validation | every action carries `rollback_state`; 111/111 populated | **PASS** |
| STATUS branch guards | `tests/test_executor_status_subplan.py` | **5 passed** |

**Correcting the previous report:** it stated "376 tests ran, 2 pre-existing
import errors (missing pytest)". That was the *global* interpreter, not the
project venv. There are no pre-existing failures. The dependency was never
missing from the intended environment — only from the one I used.

*Note for the repo:* `pytest` is configured in `pyproject.toml` but is not listed
in `dependencies` or `requirements.txt`. It is present in `.venv` regardless.
Adding it under a dev extra would prevent the same mistake later. **Not changed**
— it is outside this gate's scope.

## 5. Repository diff

This is **not a git repository** (`git rev-parse` → `fatal: not a git
repository`), so diffs are against saved before-copies rather than `git diff`.

| File | Change | Why necessary | Weakens safety? |
|---|---|---|---|
| `clients/…/client.yaml` | +140 / −54 lines | 17 UNKNOWNs replaced with evidence-tagged live facts; three service lists separated; strict-parse clean | **No.** Adds facts and provenance; removes no guard. |
| `clients/…/work-order-a-patio-construction.yaml` | new (prev. session) | Work order A; the repo allows one service per work order | No |
| `clients/…/work-order-b-paver-installation.yaml` | new (prev. session) | Work order B | No |
| `clients/…/work-order.yaml` | header banner | Marks the single-service order superseded | No |
| `src/gm_gsa/work_orders.py` | +18 / −6 | One account can hold two approved services. A work order's service now validates if it is `client.primary_service` **or** an entry in `client.offer.services_in_scope`. | **No.** The service must still appear in the client profile; a service in neither field is still rejected. Test `test_rejects_service_absent_from_profile_scope` pins that. |
| `scripts/execute_approved_plan.py` | +31 / −0 | `STATUS` was in `SUBPLANS` but had no `build()` branch, so keyword pauses were unexecutable. | **No.** The branch is pause-only: it refuses any operation but `PAUSE_AD_GROUP_CRITERION` and any `proposed_state` but `PAUSED`. It cannot enable, remove, or touch another resource type — it can only ever reduce delivery. |
| `tests/test_work_orders.py` | +2 tests | Pin both directions of the multi-service rule | No |
| `tests/test_executor_status_subplan.py` | new, 5 tests | Pin the pause-only guards, including that one bad action aborts the whole batch | No |
| `scripts/yaml_strict.py` | new | Strict duplicate-key loader | No — adds a check |
| `docs/CHANGELOG.md` | +3 entries | Repo policy requires it when behaviour changes | No |
| `clients/…/recovery/2026-09-patio-pavers/**` | 30 generated artifacts | The recovery program's evidence and plans | No — all local |

**No preexisting safety rule was weakened.** The identity gate, the paused-by-
default rule, the separate-approval-per-class rule, the fingerprint check and the
`assert_no_embedded_secrets` guard are all untouched and still enforced.

## 6. Data freshness

| Read | Timestamp (America/New_York) | Result |
|---|---|---|
| Identity gate | 2026-09-03 19:59:12 | PASS |
| Baseline snapshot 2 | 2026-09-03 20:02 | 14 queries, **0 errors** |
| BID / BUD evidence | 2026-09-03 20:04 | 8 queries, 0 errors |
| Conversion evidence | 2026-09-03 20:05 | 4 queries, 0 errors |
| Landing-page probe | 2026-09-03 20:07 | 4 probes (desktop + mobile × 2 pages) |
| Final drift re-check | 2026-09-03 20:10 | **NO DRIFT, 0 differences** |

**Evidence hash:** `3D9E3199DD183E79` (SHA-256 of the normalized baseline,
`01e-baseline-2.json`). Identical across both runs 8 minutes apart, confirming a
stable account state.

Library: **google-ads 31.2.0** on Python 3.11.9 (the venv), versus 29.2.0 on the
global interpreter used previously. Same results, correct environment.

## 7. Package-by-package

Full per-operation detail — **111 rows, one per operation**, with all sixteen
required columns — is in `20-all-operations.csv` and `20-all-operations.md`.

### BID-2 — per-campaign CPC ceilings (was a single blended $22)

**Confirmed current state:** both campaigns `TARGET_SPEND` (Maximize Clicks), no
portfolio strategy, `cpc_bid_ceiling_micros` **unset on both**.

| | Patio `23484806108` | Pavers `23489296528` |
|---|---|---|
| May avg CPC | $5.97 | $7.16 |
| June | $7.70 | $11.16 |
| July | $8.47 | $11.31 |
| August | $11.04 | $21.04 |
| Sept 1–3 | **$13.98** | **$22.76** |
| Sept 3 alone | $13.03 | **$27.83** |
| **Highest daily CPC ever** | **$15.56** (2026-08-06) | **$46.54** (2026-08-20) |
| Days above $16, of days with clicks | **0 of 95** | 19 of 84 |
| Days above $22 | 0 of 95 | 14 of 84 ($662.64, 22 clicks) |
| CVR by month | 0%, 4.17%, 0%, 1.16%, 0% | 0%, 0%, 5.26%, 8.70%, 0% |
| Converting keyword CPCs | $8.27, $10.91 | $7.75, $11.09, $12.61, $13.25, $14.71, $16.75, **$26.54** |
| **Proposed ceiling** | **$16.00** | **$18.00** |
| Modelled click retention | 99.6% | 87.3% |
| Modelled conversion retention | 100% | 88% |

**Are separate ceilings safer? Yes — decisively.** A single $22 would have been
inert on Patio, which has never recorded a daily CPC above $15.56 while its CPC
climbed 134% in five months. And on Pavers, $18, $20 and $22 retain *identically*
(87.3% of clicks, 88% of credits), so $22 spends $4 more per click for exactly
the same traffic.

**The one converting keyword above $18 in Pavers is `local asphalt companies near
me` at $26.54** — which KW-2 pauses anyway. After KW-2, every in-scope converting
keyword sits at or below **$16.75** (Pavers) and **$10.91** (Patio).

**Traffic loss and cost protection.** Patio: ~0.4% of historic clicks, 0% of
credits; protects against a trend that has added ~20%/month. Pavers: ~12.7% of
clicks and 12% of credits, all of it in the tail above $18; would have capped
$869.56 of spend across 19 days.

**Changes only** `target_spend.cpc_bid_ceiling_micros`. The strategy type stays
`TARGET_SPEND`. **Rollback:** clear the field on both campaigns.

### BUD-2 — $24 / $32, verified against every enabled campaign

**Does the $1,760 projection include every enabled campaign? Yes — verified.**

| Campaign | Status | Daily budget | Proposed | MTD spend | Shared? |
|---|---|---|---|---|---|
| Patio | **ENABLED** | $33.00 | **$24.00** | $111.81 | no, ref=1 |
| Pavers | **ENABLED** | $33.00 | **$32.00** | $136.55 | no, ref=1 |
| Hardscaping | PAUSED | $21.00 | — | $0.00 | no, ref=1 |
| Paver Sealing | PAUSED | $14.00 | — | $0.00 | no, ref=1 |
| Power Washing | PAUSED | $33.00 | — | $0.00 | no, ref=1 |
| Retaining Walls | PAUSED | $12.00 | — | $0.00 | no, ref=1 |

Exactly **2 enabled campaigns**; the four paused ones have spent **$0.00** month
to date. **No budget in the account is shared** — every one has
`explicitly_shared=false` and `reference_count=1`, so no other campaign can draw
on either budget.

| Metric | Value |
|---|---|
| Account MTD (Sep 1–3, today partial) | $248.36 |
| Remaining budget = max(0, 2000 − MTD) | $1,751.64 |
| Remaining days (Sep 4–30) | 27 |
| Remaining daily allowance | $64.88 |
| Current enabled daily total | $66.00 |
| **Projection at current budgets** | **$2,030.36 — $30.36 OVER cap** |
| **Projection at proposed budgets** | **$1,760.36 — PASS** |
| **Headroom below $2,000** | **$239.64** |
| Projection at complete-day run rate | $1,946.12 |
| Worst case if all six were enabled | $4,190.36 |

**Method:** account MTD read `FROM customer` for 2026-09-01..today, plus the
summed daily budget of every ENABLED campaign × days remaining *after* today.
Today's spend is already inside MTD, so it is not double-counted.

**Cap check: PASS.** **Risk:** if any paused campaign is enabled without a new
budget plan, the projection breaks immediately — worst case $4,190.36.
**Rollback:** $33.00 on both.

### KW-2 — the exact seven keywords

All in campaign **Pavers** `23489296528`. Authority is the **declared service
scope**, not performance: the 2026-09-03 recovery prompt lists asphalt paving,
asphalt repair and blacktop as outside the approved scope. These would be paused
even if they converted well.

| # | Ad group | Keyword | Match | Status | Criterion ID | Spend | Clicks | Conv | Qualified |
|---|---|---|---|---|---|---|---|---|---|
| KW-01 | Paver Installation Near Me (Pharse) | local asphalt companies near me | PHRASE | ENABLED | 543919818878 | $132.69 | 5 | 1.0 | UNKNOWN |
| KW-02 | Paver Installation Near Me (Pharse) | asphalt contractor near me | PHRASE | ENABLED | 297075223566 | $102.01 | 4 | 0.0 | UNKNOWN |
| KW-03 | Paver Installation Near Me (Pharse) | asphalt paving services near me | PHRASE | ENABLED | 309567954442 | $13.21 | 1 | 0.0 | UNKNOWN |
| KW-04 | Paver Installation Near Me (Pharse) | asphalt services near me | PHRASE | ENABLED | 300588535183 | $0.00 | 0 | 0.0 | UNKNOWN |
| KW-05 | Paver Installation Near Me (Pharse) | local asphalt paving companies | PHRASE | ENABLED | 298883953673 | $0.00 | 0 | 0.0 | UNKNOWN |
| KW-06 | Paver Installation Near Me (Pharse) | local asphalt paving contractors | PHRASE | ENABLED | 303329780817 | $0.00 | 0 | 0.0 | UNKNOWN |
| KW-07 | Paver Installation Near Me (Pharse) | asphalt and paving companies near me | PHRASE | ENABLED | 356532888916 | $0.00 | 0 | 0.0 | UNKNOWN |

All seven sit in ad group `196134824089`. Resource names are
`customers/2429758629/adGroupCriteria/196134824089~<criterion_id>`.

Totals: **$247.91, 10 clicks, 1 raw credit.** Qualified leads are **UNKNOWN**, not
zero — no CRM join exists (SLM-Q11). **Rollback:** status → ENABLED on the same
seven `(ad_group_id, criterion_id)` pairs.

Deliberately **not** paused: `paving company near me` (3 credits on $450.02),
`local paving companies`, and all four driveway keywords (held for SLM-Q5).

### NEG-2 — 99 negatives, down from 154

| Classification | Negatives | Executable | Visible spend blocked |
|---|---|---|---|
| High-confidence wrong service | 89 | yes | $516.26 |
| DIY / information / materials intent | 8 | yes | $0.00 |
| Employment intent | 2 | yes | $0.00 |
| **Requires business confirmation** | **6** | **NO — annex** | $12.50 |
| Competitor / research intent | 0 | — | — |
| Ambiguous | 0 | — | — |

**Ambiguous and unconfirmed rows are not in the executable package.** The six
`resurfacing` negatives moved to `06d-negative-annex-nonexecutable.csv` pending
SLM-Q9, because no authoritative client source excludes patio resurfacing.

**The 55 that were removed:**
- **49 redundant.** An existing BROAD negative already blocks everything the
  proposed PHRASE negative would. A BROAD negative fires when *all* of its words
  appear anywhere in the query, so BROAD `cleaning` already subsumes PHRASE
  `patio cleaning`; BROAD `repair` subsumes `deck repair`; BROAD `home depot`
  subsumes PHRASE `home depot`. The v1 check compared PHRASE-to-PHRASE only and
  missed the entire class.
- **4 collision rejections** (`paver re sanding`, `paver leveling`, `refinishing`,
  `deck contractor`) — each would block a protected KEEP/WATCH/UNRESOLVED term.
- **6 moved to the annex** as above.

**Coverage after the reduction:** Patio $207.11 of $234.01 (88.5%), Pavers
$309.15 of $331.78 (93.2%).

**Collision testing.** Every candidate was tested against all 461 positive
keywords in both campaigns (ENABLED *and* PAUSED), every KEEP / WATCH /
UNRESOLVED / UNCLASSIFIED search term, and the 1,452 / 1,448 negatives already
blocking each campaign. Per-row results, source search terms and the exact tested
counts are in `06-negative-plan-v2.csv`.

Themes explicitly protected in the test: patio services, paver services, driveway
paver services (unconfirmed — **not** blocked), concrete patio (unconfirmed —
**not** blocked), bluestone (**not** blocked), masonry (**not** blocked),
resurfacing (moved to annex), all 110 location targets, and the nine agency
protected terms (`near me`, `quote`, `price`, `pricing`, `cost`, `best`, `hire`,
`local`, `emergency`) — none of which appears in any proposed negative.

**A verified check on the existing layer:** zero live or paused keywords in Patio
or Pavers are blocked by any existing negative. The current negative layer is
weak, but it is not silently killing anything.

**Also verified:** Patio already carries a campaign-level BROAD `driveway`
negative; Pavers does not. That is why **100% of the $346.05 driveway spend is in
Pavers** ($0.00 in Patio). If SLM-Q5 says driveways are out of scope, the fix is
one negative on one campaign.

### The 1,452 vs 1,675 discrepancy — resolved

Both numbers are correct; they count different things.

**1,675** is every campaign-level negative keyword across **all six** campaigns:
Retaining Walls 441 + Patio 420 + Pavers 416 + Hardscaping 395 + Power Washing 2
+ Paver Sealing 1. The unchanged-state check counted the whole account.

**1,452** is the distinct `(text, match_type)` set actually blocking **one**
campaign — Patio's own 420, plus the linked "General List" shared set (1,111),
plus the account-level list (35). That is 1,566 raw rows deduplicating to 1,452.
Pavers is 416 + 1,111 + 35 → **1,448**.

### CONV-2 — one operation, down from two

**The form pair — duplication PROVEN observationally.**

| | `Softwind Submit lead form` 7461619140 | `(web) form_submission` 7480764700 |
|---|---|---|
| Type / category / origin | WEBPAGE / SUBMIT_LEAD_FORM / WEBSITE | GA4 custom / SUBMIT_LEAD_FORM / WEBSITE |
| Primary / counts in Conversions | yes / yes | yes / yes |
| Counting | ONE_PER_CLICK | MANY_PER_CLICK |
| Click-through window | 30 days | 90 days |
| View-through window | 1 day | 1 day |
| Attribution | data-driven | data-driven |
| Enhanced conversions for leads | enabled account-wide | enabled account-wide |
| Days fired | 6 | 10 |
| **Days fired ALONE** | **0** | 4 |
| Lag | 8.0/8.0 under one day | 12.0/13.0 under one day |
| **Proposed** | **primary_for_goal → false** | unchanged, stays primary |

Days both fired: **6 of 6**. Identical counts on **5 of those 6**. The one
exception (2026-04-28, 1 vs 3) is explained exactly by ONE_PER_CLICK capping a
click that produced three submissions.

**Dependencies:** GA4 for the retained action; **none on WhatConverts** —
WhatConverts writes to `WC Leads` (UPLOAD_CLICKS) and `WC Call` (UPLOAD_CALLS),
verified from `conversion_action.type`.

**Campaign-learning impact: none.** Both campaigns run Maximize Clicks, which
does not consume conversion data for bidding. No learning period exists.

**The controlled test has NOT been run**, and the plan says so. Procedure in
`18-conv-controlled-test.md`. It is blocked because a live submission writes a
real CRM record, and because `input_9` is an unlabelled visible field that was a
honeypot at the same index on the sibling account. Residual uncertainty is stated
in the plan itself.

**Dropped from CONV-1: `Calls from ads (1)` (7508686781).** The v1 rationale
claimed a June 2026 duplicate window. Day-level data refutes it: 7508686781 fired
on 19 days, 7461572537 on 13, and **never on the same day**. They are a handover,
not a duplicate. Demotion is therefore unproven and the action is dropped to a
watch item.

**Still held back:** `WC Leads` (a probable third credit — on 2026-07-15 all
three actions recorded 2 apiece — but it carries Patio's only August credit) and
`WC Call` (broken, not duplicative: zero all-conversions ever).

## 8. New fingerprints and the exact approval syntax

**All previous codes are void.** `50C553579EF3`, `D82341B7238E`, `19FA5CBBB1E5`,
`0895911A8133`, `FB9DA2D017AD` — refuse all five if presented.

### Is "APPROVE APPROVE-BIDDING" intentional? No.

It was a stutter: the v1 packages stored `approval_label: "APPROVE-BIDDING"` and
then printed `APPROVE {label} …`. It matches **no parser**. The repository has a
real executor and its contract is a command line, not a phrase:

```
python scripts/execute_approved_plan.py \
  --plan <plan.yaml> --subplan <SUBPLAN> --fingerprint <CODE> --out <receipt.json> [--validate-only]
```

`--subplan` must be one of `STATUS`, `BUDGET`, `EXISTING_RESOURCES`,
`CONVERSIONS`, `CREATE_PAUSED`, `SITE_OR_TRACKING`, `ENABLE`. The executor
recomputes `approval_code({"target", "subplan", "actions"})` from the file on disk
and **refuses to run on any mismatch**, so a code cannot drift from its plan.

The v2 plans are written in exactly that shape, one file per package, so each
carries an independent approval. All five fingerprints below were produced by the
same function the executor uses.

| Order | Package | Subplan | Ops | Fingerprint | Depends on |
|---|---|---|---|---|---|
| 1 | `PLAN-SLM-BID-2` | EXISTING_RESOURCES | 2 | **`8C71888E09CC`** | — |
| 2 | `PLAN-SLM-BUD-2` | BUDGET | 2 | **`BB9869E17E37`** | — |
| 3 | `PLAN-SLM-KW-2` | STATUS | 7 | **`B7A11B246D74`** | — |
| 4 | `PLAN-SLM-NEG-2` | EXISTING_RESOURCES | 99 | **`2CD5644B5504`** | **KW-2 must land and read back first** |
| 5 | `PLAN-SLM-CONV-2` | CONVERSIONS | 1 | **`852D47BE6133`** | — |

Plans in `10-change-packages-v2/`. Index in `00-index.json`.

**`validate_only` receipts — all five passed through the real executor**, one
atomic mutate each, `partial_failure=False`, nothing written. Receipts in
`11-write-receipts/validate-PLAN-SLM-*.json`.

## 9. Recommended execution order

1. **BID-2** — the price brake. Highest leverage, instantly reversible, no
   structural risk.
2. **BUD-2** — brings the projection under the cap. Independent of BID-2.
3. **KW-2** — pause the 7 asphalt keywords. Must precede NEG-2.
4. **NEG-2** — only after KW-2 reads back. Google's `validate_only` **accepts**
   the `asphalt` negative even while those keywords are live; the API does not
   catch that collision, only the local test does.
5. **CONV-2** — reporting hygiene, no bidding impact, can run any time.

TRACK-A and TRACK-B are **not** in this queue. They need separate access and
separate approvals.

## 10. Post-change validation schedule

| When | Check |
|---|---|
| Immediately | Read back every changed field; compare to the plan; confirm unrelated resources unchanged; re-run the drift check. |
| 24–72h | Serving status, policy, URLs, tracking, spend anomalies. Confirm no campaign dropped to `LIMITED`. |
| 7 days | Pacing vs the $2,000 cap; wrong-service share; `search_rank_lost_impression_share` on both campaigns; click volume vs the pre-change baseline. |
| 14 days | Directional CPL; decide whether to step Patio to $14 and Pavers to $16 through a **new** plan. |
| 30 days | Formal keep / modify / roll back. |

**Escalate immediately on:** identity mismatch · projected spend above $2,000 ·
wrong-service share above 10% after NEG-2 · lost-IS-to-rank above ~65% without a
click-volume gain · any new broad-match keyword · Search Partners, Display, AI
Max, DSA or Final URL expansion switching on · new disapprovals · partial write
failure.

## 11. Blocking questions for the owner

Authoritative yes/no answers needed. Ordered by money at stake.

**Service scope (SLM-Q5 / Q9)** — $662.48 of visible spend, 25.9%, **zero credits**:

| # | Question | At stake | If unanswered |
|---|---|---|---|
| 1 | Does Softwind offer **asphalt installation**? | $169.77 | KW-2 and 8 negatives assume **no** (per your 2026-09-03 scope) |
| 2 | Does Softwind offer **asphalt repair**? | included above | assumed **no** |
| 3 | Does Softwind offer **sealcoating**? | $117.29 | assumed **no** |
| 4 | Does this account promote **paver sealing**? | $53.29 | assumed **not in Patio/Pavers** — it has its own paused campaign here |
| 5 | Does Softwind offer **driveway paver installation**? | **$346.05, all in Pavers** | nothing blocked, nothing promoted |
| 6 | Does Softwind offer **poured-concrete patios**? | $173.24 | nothing blocked |
| 7 | Does Softwind offer **bluestone patios or walkways**? | $22.74 | nothing blocked |
| 8 | Does Softwind offer **general masonry**? | $62.01 | nothing blocked |
| 9 | Does Softwind offer **resurfacing**? | $12.50 | 6 negatives held in the annex |

**Operations and measurement:**

| # | Question | Blocks |
|---|---|---|
| 10 | Which **counties, cities and ZIP codes** are approved? 110 targets are live and none has been confirmed by you. | any location change; SLM-Q11 |
| 11 | **What makes a lead qualified?** | every CPQL, sold-rate and profit figure. All are currently *unavailable*, not zero. |
| 12 | **What minimum project size** is acceptable? | lead-quality scoring and the quality loop |
| 13 | Can Green Marketing get **WhatConverts admin access**, and is **(631) 502-5402** a real Softwind number? | TRACK-A and TRACK-B |
| 14 | Can you substantiate **licensed, insured, certified, warranty, 100% satisfaction guarantee, "install start in 7 days", "call back within 10 minutes"**? All are live in ads or on the pages today. | replacement RSAs |
| 15 | Should the sibling account's tag `AW-18369652705` be removed from these pages? | tag hygiene |
| 16 | Is `input_9` on the offer forms a honeypot? | any live form test |
| 17 | Should the **30-second** minimum on `Calls from ads` become 60, matching every other action? | qualified-call definition |

**Unconfirmed services are kept out of every pause and negative package.** The
only exception is where your own 2026-09-03 instruction explicitly excluded the
service.

## 12. Remaining unknowns

- **Qualified leads, sold jobs, revenue, gross profit** — no CRM join exists and
  WhatConverts' campaign/keyword fields are blank. Reported as *unavailable*.
- **Auction Insights** — `PERMISSION_DENIED` on a Basic-access developer token.
  UI export only.
- **Change history before 2026-08-06** — `change_event` is hard-capped at 30
  days. The 2026-06-16 expansion and 2026-08-03 budget move come from the audit.
- **Search-term coverage** — 52.6% all-time, 57.4% over 30 days. Every share is a
  share of *visible* spend.
- **The forensic audit document** — still not present in this repository. Its
  figures were re-derived from the API and reconcile within rounding.
- **Whether the phone mismatch fully explains zero WhatConverts calls** — not
  provable without WhatConverts access. Three alternatives remain open; see
  TRACK-A §2.
- **`input_9`** — unverified. No automated form test until it is identified.

## 13. Explicit confirmation: no durable mutation occurred

Re-verified at 20:10 America/New_York against the 18:12 baseline:

```
DRIFT vs baseline : NO DRIFT (0 differences)
```

Field-by-field, all six campaigns: status, bidding strategy type, CPC ceiling
(still **none** on Patio and Pavers), budget amount, Search Partners, Display,
AI Max, positive geo type, final URL suffix — **all unchanged**.
695 keywords, 0 status differences. 1,675 campaign negatives, unchanged.
16 conversion actions, 0 `primary_for_goal` differences.

Every API call this session was either a `SELECT` or a mutate with
`validate_only=True` and `partial_failure=False`. The five executor runs each
reported `VALIDATION PASSED. Nothing was written.`
`11-write-receipts/` contains only validate-only receipts — no live write receipt
exists.

No website, WhatConverts, GA4, GTM or CallRail change was made. The landing-page
probes submitted no form and clicked no `tel:` link.

---

**This message is not an approval.** Nothing may execute until you approve a
specific plan by its new fingerprint above.
