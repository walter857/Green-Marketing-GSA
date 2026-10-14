# Softwind Landscape & Masonry — final execution report

**Account:** Softwind Landscape & Masonry - Live · `2429758629` · USD · America/New_York
**Run start:** 2026-09-03 21:22 · **Run end:** 2026-09-03 23:2x America/New_York
**Scope:** Patio `23484806108`, Pavers `23489296528`

---

## Headline

**UPDATE 2026-09-03 23:4x — NEG-3 was subsequently APPROVED and APPLIED.**
All four P0 objectives are now live: CPC ceilings, budgets, asphalt keyword pauses
and 96 wrong-service negatives. NEG-2 was never executed; NEG-3 superseded it.

**FOUR packages APPLIED and read back clean. NEG-2 was BLOCKED at preflight and
superseded by NEG-3.**

| Package | Status | Ops | Readback |
|---|---|---|---|
| PLAN-SLM-BID-2 `8C71888E09CC` | **APPLIED** | 2/2 | **PASS** |
| PLAN-SLM-BUD-2 `BB9869E17E37` | **APPLIED** | 2/2 | **PASS** |
| PLAN-SLM-KW-2 `B7A11B246D74` | **APPLIED** | 7/7 | **PASS** |
| PLAN-SLM-NEG-2 `2CD5644B5504` | **SUPERSEDED** | 0/99 | n/a — never sent |
| PLAN-SLM-NEG-3 `C58644338C89` | **APPLIED** | 96/96 | **PASS** |
| PLAN-SLM-CONV-2 `852D47BE6133` | **DEFERRED** | 0/1 | n/a — no approval record exists |

Post-execution unchanged-resource proof after each package: **11 differences for
BID/BUD/KW, then 0 differences plus exactly 96 negative additions for NEG-3.**
Zero unexpected changes at any point. ClickCease intact, no paused campaign
touched, no conversion action changed. Account projection **$1,760.36** by
sum-of-budgets and **$1,946.26** by simple run rate — both under the $2,000 cap.

**NEG-3 applied:** 96 campaign-level PHRASE negatives, 48 Patio / 48 Pavers,
all ENABLED, readback 96/96 on exact text, match type, campaign and status.
Account campaign-negative total 1,675 → **1,771**. Families: patio-cover 14,
enclosure 12, restoration 12, sealing 11, deck-structure 11, cleaning 10,
asphalt 8, sealcoating 8, equipment 6, employment 2, retail-diy 2.

---

## 1. Why NEG-2 was blocked — BLOCKED

**FACT.** Section 8.6 requires: *"No negative contains or functionally blocks any
protected unresolved service."* Three of the 99 failed the literal **"contains"**
clause:

| Action | Negative text | Campaign | Protected word in the text |
|---|---|---|---|
| NEG-044 | `concrete sealing` | Patio | concrete |
| NEG-092 | `concrete sealing` | Pavers | concrete |
| NEG-093 | `driveway sealing` | Pavers | driveway |

**FACT — the functional test.** None of the three blocks anything protected:

| Action | Search terms blocked | Protected terms blocked | Own keywords blocked | Canonical protected intents blocked |
|---|---|---|---|---|
| NEG-044 | 0 | 0 | 0 | none |
| NEG-092 | 0 | 0 | 0 | none |
| NEG-093 | 6 (worth **$0.00**, 0 clicks) | 0 | 0 | none |

**INFERENCE.** As PHRASE negatives these match only the contiguous phrase, so
`concrete sealing` cannot block *concrete patio installation* and
`driveway sealing` cannot block *paver driveway installation near me*. The
conflict is **textual, not substantive**.

**Why I still did not execute.** Section 7 authorized *"the 99 exact Phrase
negatives in the unchanged v2 plan"*. Executing 96 would be a different plan with
a different fingerprint, and Section 6 forbids self-approving a changed plan.
Section 8.6 directs a failed assertion to block that package. So the package was
neither edited nor executed. **A correct blocked result, as instructed.**

**RECOMMENDATION — `PLAN-SLM-NEG-3`, DRAFTED and VALIDATED-ONLY.** Identical to
NEG-2 minus those three operations. **96 operations, 48 Patio / 48 Pavers, all
PHRASE.** New fingerprint **`C58644338C89`**. All nine preflight assertions pass,
including `no_negative_TEXT_contains_protected_service`. It has passed
`validate_only` through the real executor. **It is not self-approved.**

**Cost of the delay (CALCULATION).** The seven asphalt keywords are already
paused, which closed the direct doors. What remains open until NEG-3 is approved
is asphalt and sealing intent arriving through broader keywords such as
`paving company near me` — approximately **$516 of visible wrong-service spend
across all history**, or roughly 22% of visible Patio/Pavers spend.

## 2. Identity gate — FACT, PASS

Fresh read at **2026-09-03 23:03:52 -04:00**, receipt
`snapshots/identity-gate-2026-09-03-2303.json`.

| Check | Expected | Observed |
|---|---|---|
| Child ID | 2429758629 | 2429758629 ✓ |
| Descriptive name | Softwind Landscape & Masonry - Live | exact match ✓ |
| Manager / test | false / false | false / false ✓ |
| Currency / time zone | USD / America/New_York | USD / America/New_York ✓ |
| Status | ENABLED | ENABLED ✓ |
| Patio / Pavers IDs | 23484806108 / 23489296528 | both live and ENABLED ✓ |

## 3. Repository and tests — FACT

| Gate | Result |
|---|---|
| Full pytest suite (`.venv/Scripts/python.exe -m pytest -q`) | **498 passed, 0 failed** |
| Strict YAML duplicate-key scan (9 files) | 9/9 PASS |
| Work order A / B against client.yaml | PASS / PASS |
| `verify_setup.py` | Preflight PASS |
| Git | **not a git repository** — timestamped before-copies used instead |

## 4. Snapshots and drift — FACT

| Artifact | Value |
|---|---|
| Pre-execution snapshot | `25-pre-execution-snapshot-2026-09-03-2303.json` |
| Pre-execution file SHA-256 | `456C8511EEA5258C20B3F38666EE052F` |
| Pre-execution evidence hash | `3D9E3199DD183E79` |
| Drift classification | **NO_DRIFT** (0 differences vs the plan source snapshot) |
| Post-execution snapshot | `30-post-execution-snapshot.json` |
| Post-execution file SHA-256 | `E95EDFDE94F298C43E133545C3AECD87` |
| Post-execution evidence hash | `69063BBB1DB7CCB0` |

## 5. Package-by-package

### BID-2 — APPLIED

| Campaign | Before | After | Expected | Strategy after |
|---|---|---|---|---|
| Patio `23484806108` | **no ceiling** | **$16.00** | $16.00 ✓ | TARGET_SPEND (unchanged) |
| Pavers `23489296528` | **no ceiling** | **$18.00** | $18.00 ✓ | TARGET_SPEND (unchanged) |

No bidding strategy replaced, no portfolio strategy, budgets and networks
untouched at readback, four paused campaigns unchanged (Paver Sealing keeps its
pre-existing $7.50 ceiling).
Receipts: `revalidate-BID-2.json`, `WRITE-BID-2.json`, `27-readback-BID-2.json`.

### BUD-2 — APPLIED

| Campaign | Budget ID | Before | After | Shared | Refs |
|---|---|---|---|---|---|
| Patio | 15309303030 | $33.00 | **$24.00** | false | 1 |
| Pavers | 15314089588 | $33.00 | **$32.00** | false | 1 |

All four paused budgets unchanged ($21, $14, $33, $12). No budget in the account
is shared.

**CALCULATION — account-wide pacing, every enabled campaign:**

| Input | Value |
|---|---|
| Enabled campaigns | **2** (Patio, Pavers) |
| Paused-campaign MTD spend | **$0.00** |
| Account MTD (Sep 1–3) | $248.36 |
| Remaining days (Sep 4–30) | 27 |
| Enabled daily total after | **$56.00** |
| **Projected month-end** | **$1,760.36** |
| **Headroom under $2,000** | **$239.64** |
| Sum-of-daily-budgets ceiling | $56.00 × 27 + $248.36 = $1,760.36 |
| Simple run-rate projection (complete days only) | $248.36 + $62.88 × 27 = $1,946.12 |
| Worst case if all six were enabled | $4,190.36 |

**Cap check: PASS.** Receipts: `revalidate-BUD-2.json`, `WRITE-BUD-2.json`,
`28-readback-BUD-2.json`.

**Constraint classification (INFERENCE):** the account is **CPC-limited and
quality-limited**, not budget-limited. Before today nothing bounded click price
and only 13 of 50 serving keywords had a Quality Score, 9 of those with
BELOW_AVERAGE landing-page experience.

### KW-2 — APPLIED

All seven in campaign Pavers, ad group `196134824089` "Paver Installation Near Me
(Pharse)". Resource pattern
`customers/2429758629/adGroupCriteria/196134824089~<criterion_id>`.

| Action | Criterion ID | Keyword | Match | Before | After |
|---|---|---|---|---|---|
| KW-01 | 543919818878 | local asphalt companies near me | PHRASE | ENABLED | **PAUSED** |
| KW-02 | 297075223566 | asphalt contractor near me | PHRASE | ENABLED | **PAUSED** |
| KW-03 | 309567954442 | asphalt paving services near me | PHRASE | ENABLED | **PAUSED** |
| KW-04 | 300588535183 | asphalt services near me | PHRASE | ENABLED | **PAUSED** |
| KW-05 | 298883953673 | local asphalt paving companies | PHRASE | ENABLED | **PAUSED** |
| KW-06 | 303329780817 | local asphalt paving contractors | PHRASE | ENABLED | **PAUSED** |
| KW-07 | 356532888916 | asphalt and paving companies near me | PHRASE | ENABLED | **PAUSED** |

All seven still exist. Keyword count **695 before, 695 after**. Zero unrelated
status changes, zero additions, zero removals, zero text or match-type edits.
Receipts: `revalidate-KW-2.json`, `WRITE-KW-2.json`, `29-readback-KW-2.json`.

### 5.1 Unchanged-resource proof — PASS

`31-unchanged-proof.json`. Exactly **11 differences**, every one an approved
operation, **0 unexpected**:

- 2 × `cpc_bid_ceiling` (BID-2)
- 2 × `budget_amount` (BUD-2)
- 7 × keyword `status` ENABLED→PAUSED (KW-2)

Verified unchanged: 695 keywords · 1,675 campaign negatives · 16 conversion
actions with **0** `primary_for_goal` changes · 110 location criteria per
campaign · Presence settings · Search Partners off · Display off · AI Max off ·
asset automation opted out · 235 ClickCease IP blocks on each in-scope campaign ·
account tracking template still `monitor.clickcease.com` · all four paused
campaigns' status and budgets.

**Protected unresolved services confirmed not blocked:** no negative was created
at all this run, so driveway paver installation, poured-concrete patios,
bluestone, masonry, resurfacing, pool deck and pool coping are untouched.

## 6. Conversions — DEFERRED

**FACT.** `PLAN-SLM-CONV-2` fingerprint `852D47BE6133`, one operation:
`Softwind Submit lead form` `7461619140` (WEBPAGE / SUBMIT_LEAD_FORM / WEBSITE,
ONE_PER_CLICK, 30-day click / 1-day view, data-driven attribution)
`primary_for_goal` True → False. Rollback: set it back to True.

**FACT.** A repository-wide search for the fingerprint found it only in the plan,
the validate receipt, the operations table and the pre-approval report. **No
approval record exists.** Per Section 13.3 conversions were left unchanged.

**BLOCKED-SAFE-TEST-DATA.** The controlled duplicate test was not run: no
owner-approved test contact values exist in environment variables or protected
configuration, and `input_9` on both forms is still an unlabelled visible field
that was a honeypot at the same index on the sibling account.

**Standing evidence (unchanged):** the two form actions co-fired on 6 of 6 days,
the demoted candidate never fired alone, 5 of 6 overlapping days had identical
counts. The two `Calls from ads` actions fired on 19 and 13 days with **zero**
overlap and are **not** treated as duplicates.

## 7. TRACK-A — phone swap — BLOCKED-ACCESS-OR-TRUTH

**FACT, re-verified this run across 10 browser probes:** both offer pages render
`(631) 502-7946`; the `wc_swap` rule is `6315025402 → 6315535927` (rule 197159);
neither swap number appears in the DOM; the rendered number is identical before
and after every script runs. The swap cannot fire.

**NOT PROVEN:** that this fully explains zero `WC Call` conversions. Calls may
exist in WhatConverts under another source. Requires WhatConverts read access.

Exact implementation plan with current/proposed values, pages, test method,
rollback and required access: `21-TRACK-A-phone-repair.md`. **No change made.**

## 8. TRACK-B — attribution — DRAFTED

**FACT, controlled A/B this run:** a GCLID-only visit leaves `wc_client` campaign,
ad group and term **blank**; the same visit with UTMs populates all three
(`QAGATE_CAMPAIGN`, `QAGATE_ADGROUP`, `QAGATE_TERM`). Auto-tagging is on; neither
campaign nor the account carries a `final_url_suffix`; the account tracking
template is ClickCease's and carries no UTMs.

**INFERENCE:** a GCLID reaching the landing page is *not* evidence of attribution.

Preferred fix remains **connect the WhatConverts ↔ Google Ads integration** — it
changes nothing in the ad-serving path and leaves ClickCease untouched. The
campaign-level `final_url_suffix` remains the fallback and must be validated
against the ClickCease redirect with one real click before it is trusted.
Full plan: `22-TRACK-B-attribution-repair.md`. **No change made.**

## 9. WAF / browser matrix — FACT, and an earlier overstatement corrected

| Page | User agent | Status | Forms | Phone | tel: | WC | ClickCease |
|---|---|---|---|---|---|---|---|
| patio | Chrome desktop (Win) | **403** | 0 | no | 0 | no | no |
| patio | Edge desktop (Win) | **403** | 0 | no | 0 | no | no |
| patio | Chrome Android | 200 | 2 | yes | 3 | yes | yes |
| patio | Safari iPhone | 200 | 2 | yes | 3 | yes | yes |
| patio | Headless default | 200 | 2 | yes | 3 | yes | yes |
| pavers | Chrome desktop (Win) | **403** | 0 | no | 0 | no | no |
| pavers | Edge desktop (Win) | **403** | 0 | no | 0 | no | no |
| pavers | Chrome Android | 200 | 2 | yes | 3 | yes | yes |
| pavers | Safari iPhone | 200 | 2 | yes | 3 | yes | yes |
| pavers | Headless default | 200 | 2 | yes | 3 | yes | yes |

**This is NOT proof that desktop visitors are blocked, and I am not reporting it
as such.** Desktop paid traffic converts: **3.0 credits on 85 clicks, 3.53% CVR
all-time — higher than mobile's 3.05%** — including 1 credit since 2026-08-01. If
real desktop users were being 403'd, desktop CVR would be zero.

**INFERENCE:** the 403 fires on a *headless client presenting a Windows desktop
UA* — a UA/fingerprint mismatch a WAF is designed to catch. A real desktop
browser presents a consistent fingerprint and evidently passes.

**RECOMMENDATION:** confirm on a genuine, non-headless desktop browser before
touching the WAF. Do not weaken the rule on this evidence. `32-waf-browser-matrix.json`.

## 10. Lead quality and attribution coverage — BLOCKED

No WhatConverts access is configured for this project, so the May–August and
month-to-date reconciliation could not be performed. Google Ads conversion
credits are recorded; qualified leads, estimates, sold jobs, revenue and gross
profit are **unavailable, not zero**. July WhatConverts records remain **missing**.
CPL is computable; **CPQL is not**, because the denominator does not exist.
The weekly template is in place at `12-quality-loop-template.csv` and keys on a
hashed lead ID and click ID only — no PII is stored anywhere in the repository.

## 11. P1 — DRAFTED, decision made

**Structural decision: RETAIN AND CLEAN the existing ad groups. Do not build
canonical replacements yet.** Rationale (recorded in the plan): three settings
changed today so there is no stable post-change data to design against; the
account buys 3–6 clicks a day so a parallel structure would take months to
accumulate signal while resetting what Quality Score exists; paused twins risk
duplicate auction entry at cutover; and the existing groups already map cleanly
onto the three canonical intents — 76.5% of live keyword spend before KW-2,
**81.9% after**. Revisit at the 2026-10-03 decision point.

**`PLAN-SLM-P1A-GUARD` — DRAFTED, VALIDATED-ONLY, fingerprint `00FA45112351`,
7 operations.** Pauses the 7 ENABLED keywords sitting inside the PAUSED Pavers ad
group `Paver Patio Installation Near Me` (191263597185), which would otherwise
begin serving the instant that group is enabled.

**Not covered:** 2 ENABLED RSAs in the same paused group (ad ids 793879597166,
795049355495). The executor's STATUS branch handles ad-group criteria only;
pausing an ad needs a branch that does not exist. Documented rather than faked.

Supporting artifacts already on disk: `07-keyword-migration-map.csv` (all 161
keywords with verdicts), `09-rsa-copy-and-url-plan.csv` (6 RSAs, 114 assets, all
validated for limits and banned claims), `_canonical.json`.

## 12. P2 — DEFERRED with dates

Full schedule in `33-P2-monitoring-plan.md`. Next actions:
**2026-09-04→06** serving/pacing check · **2026-09-10** 7-day query review ·
**2026-09-17** ceiling step-down decision · **2026-10-03** formal 30-day verdict.

Smart Bidding readiness: **NOT READY** — all six conditions fail. Stay on
Maximize Clicks with the applied ceilings.

## 13. Rollback availability

| Package | Rollback | New approval needed? |
|---|---|---|
| BID-2 | clear `target_spend.cpc_bid_ceiling_micros` on both campaigns | yes |
| BUD-2 | restore `amount_micros` 33000000 on budgets 15309303030 and 15314089588 | yes |
| KW-2 | status → ENABLED on the seven `196134824089~<criterion_id>` pairs | yes |

No resource was deleted, renamed or removed, so every rollback is a single-field
restoration to a value recorded in `25-pre-execution-snapshot-2026-09-03-2303.json`.

## 14. Partial failures or discrepancies

**None.** All three live mutations were single atomic batches with
`partial_failure=False`, each returned the full expected response count
(2, 2, 7), and each was independently read back. No recovery plan is required.

---

## 15. Remaining-approval bundle

| Pri | Plan ID | Operation class | Count | Resources | Current | Proposed | Risk | Dependency | Fingerprint | Approval missing? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `PLAN-SLM-NEG-3` | Create campaign negative keywords | 96 | Patio 48, Pavers 48 (PHRASE, campaign level) | no such negatives | 96 wrong-service / employment / DIY negatives | A negative that is too broad blocks real demand; all 96 collision-tested, 0 hits | KW-2 — **already satisfied** | **`C58644338C89`** | **YES** |
| 2 | `PLAN-SLM-CONV-2` | Demote conversion action from primary | 1 | `7461619140` Softwind Submit lead form | `primary_for_goal = True` | `primary_for_goal = False` | Reported conversions fall; no bidding impact (Maximize Clicks) | none | `852D47BE6133` | **YES** |
| 3 | `PLAN-SLM-P1A-GUARD` | Pause ad-group criteria | 7 | `191263597185~…` in PAUSED Pavers group | ENABLED | PAUSED | Removes a latent auto-serve on any future enablement | none | `00FA45112351` | **YES** |
| 4 | TRACK-A phone repair | WhatConverts and/or website | — | swap rule 197159; `tel:(631)` anchor | swap `6315025402→6315535927` | target the number actually rendered | Call path currently untracked | WhatConverts access | not fingerprinted — blocked on access | **YES** |
| 5 | TRACK-B attribution | WhatConverts integration (preferred) or `final_url_suffix` | 0 or 2 | both campaigns | `final_url_suffix` unset | connect integration, or add UTM suffix | Suffix touches the ClickCease URL path | choose one route only | not fingerprinted — pending route choice | **YES** |

Exact commands for the three fingerprinted items:

```
python scripts/execute_approved_plan.py --plan clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers/10-change-packages-v2/PLAN-SLM-NEG-3.yaml --subplan EXISTING_RESOURCES --fingerprint C58644338C89 --out <receipt.json>

python scripts/execute_approved_plan.py --plan clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers/10-change-packages-v2/PLAN-SLM-CONV-2.yaml --subplan CONVERSIONS --fingerprint 852D47BE6133 --out <receipt.json>

python scripts/execute_approved_plan.py --plan clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers/10-change-packages-v2/PLAN-SLM-P1A-GUARD.yaml --subplan STATUS --fingerprint 00FA45112351 --out <receipt.json>
```

## 16. OWNER INPUT REQUIRED

One consolidated table. Nothing below was asked during the run.

| # | Question | Blocks | My recommendation |
|---|---|---|---|
| 1 | **Approve `PLAN-SLM-NEG-3` (`C58644338C89`, 96 ops)?** Or confirm the original 99 including `concrete sealing` ×2 and `driveway sealing`, which block sealing intent only and nothing protected? | ~$516 of wrong-service spend stays open | Approve NEG-3. The three dropped negatives block $0.00 of measured spend. |
| 2 | Does Softwind offer **driveway paver installation**? | $346.05, all in Pavers, 0 credits | — |
| 3 | Does Softwind offer **poured-concrete patios**? | $173.24 | The Patio page FAQ already asserts it |
| 4 | Does Softwind offer **bluestone**, **masonry repair**, **patio resurfacing**, **pool decks/coping**? | $124.76 combined | — |
| 5 | Approve **CONV-2**? Or authorize the controlled form test first? | duplicate credit continues | Authorize the test with agency-owned contact values, then decide |
| 6 | Can Green Marketing get **WhatConverts admin access**, and is **(631) 502-5402** a real Softwind number? | TRACK-A and TRACK-B | — |
| 7 | **What makes a lead qualified?** Minimum project size? | every CPQL, sold-rate and profit figure | — |
| 8 | Which **counties, cities and ZIP codes** are approved? 110 targets are live, none owner-confirmed | any location work | — |
| 9 | Can you substantiate **licensed, insured, certified, warranty, 100% satisfaction guarantee, "install start in 7 days", "call back within 10 minutes"**? All live today | replacement RSAs | Drop what cannot be substantiated |
| 10 | Is **`input_9`** on the offer forms a honeypot? | any live form test | — |
| 11 | Should the sibling tag **`AW-18369652705`** be removed from these pages? | cross-account contamination | Yes |
| 12 | Raise the **30-second** minimum on `Calls from ads` to 60, matching every other action? | qualified-call definition | Yes, but it breaks comparability — your call |

---

**Live changes this run: BID-2, BUD-2, KW-2 — applied, read back, proven.
NEG-2 blocked by its own safety assertion and replaced by NEG-3 awaiting approval.
CONV-2 deferred for want of an approval record. Nothing else was touched.**
