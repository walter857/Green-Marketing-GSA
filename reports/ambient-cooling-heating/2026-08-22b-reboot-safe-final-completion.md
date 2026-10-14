# Ambient Cooling — Live · Reboot-Safe Continuation and Final Completion

**Account** Ambient Cooling - Live · 240-195-9466 / 2401959466 · America/New_York · USD
**Run window** 2026-08-22 09:19 → 09:55 EDT
**Managers** Green Marketing 3373711342 ACTIVE · ClickCease Client Center 2815082755 ACTIVE
**Google Ads mutations executed this run** 1 package / 3 operations · **Website, GTM, WhatConverts, ClickCease changes** 0

---

## 1. Business outcome

The one approved package that was still outstanding — the AC Repair automotive and marine
negatives `EACEC7CBAE85FF2B` — **executed once and passed readback on every assert.** It stops a
recurring vehicle-AC waste cluster that had cost **$47.78 with zero conversions** in eight days.

Everything else was already complete and was **verified, not replayed**. The account came through
the reboot with **zero structural drift**. Exactly three resources changed in Google Ads, and
nothing else in the account moved.

Two packages remain blocked, both on the same external dependency: a developer has not yet fixed
the live landing pages. Neither block is a Google Ads problem.

**No additional immediate Google Ads mutation is recommended.**

---

## 2. Identity and reboot recovery

| Check | Result |
|---|---|
| Descriptive name | `Ambient Cooling - Live` — exact match |
| Customer ID · timezone · currency | 2401959466 · America/New_York · USD |
| Manager / test account | false / false |
| Account status | ENABLED, auto-tagging on |
| Manager links | 3373711342 ACTIVE · 2815082755 ACTIVE — untouched |
| Work-order validator | `PASS \| Ambient Cooling - Live \| 2401959466 \| heating-cooling \| AC Repair` |
| Setup verifier | `Credential variable names: present \| Preflight: PASS` |
| Concurrency | **Zero Python processes running.** Zero processes touching 2401959466. Safe to write. |

Three Git bash processes were found belonging to an unrelated project (`D:/Carbon PT/…carbon-ppc`).
They matched my search only because the pattern `google.ads` matched the literal path fragment
"Google Ads" in that project's folder name. They do not touch this customer and **were not
terminated**.

The repository is **not** under git — `git status` returns *fatal: not a git repository* — so there
was no working tree to reset or clean, and nothing was discarded.

### Two real defects found during recovery, both fixed

**1. A missing runtime dependency.** `tzdata` was absent from the virtual environment, and it is
undeclared in `requirements.txt` and `pyproject.toml`. Windows ships no system timezone database,
so `zoneinfo` could not resolve `America/New_York` and **`scripts/ambient_checkpoint.py` could not
start at all**. Installed `tzdata 2026.3` locally and declared it in both dependency files. Local
environment only; no external effect.

**2. A ledger that disagreed with the plan files.** `receipts/fingerprint-manifest-2026-08-21.json`
still listed `80868F985D33B756`, `6A2DE7A6589CA2B7` and `12E7572A25B9AFF0` as `void: false`, while
those plan files carry `VOID: true` on disk. A future session reading only the ledger could have
picked up a do-not-execute plan. The ledger was rebuilt from the files as
`receipts/fingerprint-manifest-2026-08-22b.json`; **14 fingerprints are now correctly on the
do-not-execute list** and the two records agree.

### Structural counts: reconciled, not drifted

A raw count returned 33 campaigns, 83 ad groups, 7,028 keywords, 353 campaign assets, 20 customer
assets, 23 conversion actions and 17 shared sets — all higher than the expected reference. That is
a **query-definition difference, not drift**: the reference counts exclude REMOVED resources.
Re-counting with an explicit `status != 'REMOVED'` filter reproduced the reference **exactly in all
eleven buckets**.

| Bucket | Raw | Non-removed | Expected |
|---|---:|---:|---:|
| campaigns | 33 | **23** | 23 |
| ad groups | 83 | **68** | 68 |
| ads | 115 | **115** | 115 |
| keywords | 7,028 | **6,968** | 6,968 |
| campaign criteria | 13,810 | **13,810** | 13,810 |
| ad schedules | 139 | **139** | 139 |
| campaign assets | 353 | **283** | 283 |
| customer assets | 20 | **1** | 1 |
| conversion actions | 23 | **16** | 16 |
| shared sets | 17 | **16** | 16 |
| IP exclusions | 2,796 | **2,796** | 2,796 |

---

## 3. Was the negative package already executed?

**No — it was unexecuted, and execution was never inferred from the plan file.** Two independent
API sources agreed:

1. **Change history.** The newest change event in the entire account was
   `2026-08-22 01:23:35 · CAMPAIGN_BUDGET · UPDATE · amount_micros ·
   customers/2401959466/campaignBudgets/15787409441` — the budget mutation. No campaign-criterion
   create existed anywhere in the 30-day window.
2. **Direct resource read.** `campaign_criterion WHERE campaign.id IN (the five) AND type='KEYWORD'`
   returned **zero rows**. AC Repair held no campaign-level negative keyword.

So this was a clean single execution, not a duplicate and not a partial state.

---

## 4. Package `EACEC7CBAE85FF2B` — executed

### Preflight: 37 gates, 37 passed

Fingerprint reproduced exactly. Plan not VOID, not superseded. Campaign and customer IDs confirmed.
AC Repair held zero campaign-level negatives. Every negative source that can reach the campaign was
inventoried: **campaign-level 0 · ad-group-level 0 · shared lists attached 0 · account-level set
11252984411 = 59 members** (none of them `car`, `auto` or `boat`).

Conflict testing was clean on every axis:

- blocks **0 of 12** active positive keywords on the five campaigns
- blocks **0 of 41** Ambient service phrases
- blocks **0 of 141 historical converting queries** (172.3 conversions, all-time, account-wide)
- **does not block Carrier** — negative keywords match whole words, and `carrier` is a different
  word from `car`. Explicitly tested against four Carrier phrasings.
- **0 protected terms touched** — `near me`, `quote`, `price`, `pricing`, `cost`, `best`, `hire`,
  `local`, `emergency` all untouched

`validate_only` returned VALIDATE_OK on the exact three operations, both in preflight and again
immediately before the write.

### The seven supporting queries

| Search term | Campaign | Impr | Clicks | Cost | Conv | Blocked by |
|---|---|---:|---:|---:|---:|---|
| car air conditioner repair near me | AC Repair | 5 | 2 | **$47.78** | 0.0 | `car` |
| ac car repair near me | AC Repair | 6 | 0 | $0.00 | 0.0 | `car` |
| bmw car ac repair near me | AC Repair | 2 | 0 | $0.00 | 0.0 | `car` |
| car ac repair near me | AC Repair | 2 | 0 | $0.00 | 0.0 | `car` |
| car ac service near me | AC Repair | 2 | 0 | $0.00 | 0.0 | `car` |
| auto ac repair near me | AC Repair | 1 | 0 | $0.00 | 0.0 | `auto` |
| boat air conditioner repair near me | AC Repair | 1 | 0 | $0.00 | 0.0 | `boat` |
| **Total** | | **19** | **2** | **$47.78** | **0.0** | |

Window 2026-08-14 → 2026-08-22. All seven sit in AC Repair. Every one contains a literal approved
token. Zero conversions.

### Execution and readback

One atomic `CampaignCriterionService.MutateCampaignCriteria`, `partial_failure=false`, three
creates, executed **2026-08-22 09:36:06 EDT**.

| Text | Match | Negative | Criterion ID | Resource name |
|---|---|---|---|---|
| `car` | BROAD | true | **10008241** | `customers/2401959466/campaignCriteria/24132507741~10008241` |
| `auto` | BROAD | true | **10000390** | `customers/2401959466/campaignCriteria/24132507741~10000390` |
| `boat` | BROAD | true | **10019071** | `customers/2401959466/campaignCriteria/24132507741~10019071` |

**Readback: 24 asserts, 24 passed.** Exactly three negative criteria on AC Repair, all BROAD, all
`negative=true`, all attached **only** to campaign 24132507741. Zero unapproved criteria created.
The other four campaigns still hold zero campaign-level negatives. AC Repair's active keywords
remain ENABLED and ELIGIBLE. No shared list became attached. `campaign_criteria` rose by exactly 3
and **every other structural bucket moved by 0**. All five budgets unchanged, HVAC Installation
still 176,150,000 micros, IP exclusions still 2,796, both manager links still ACTIVE, all five
campaigns still ENABLED, primary conversion set unchanged.

**No rollback was used. No write failed.**

### Two variants deliberately left alone

`automotive ac mechanic near me` and `automotive air conditioning repair near me` are **not** blocked
by the approved three — negative keywords do not match close variants, so `auto` does not block
`automotive`. Both carry **$0.00 and zero clicks**. Adding a fourth term would need a new fingerprint
and cost-bearing evidence, and neither exists. They go on the monitoring list, not into a mutation.

---

## 5. Budget: verified, not replayed

Budget resource `15787409441` reads **176,150,000 micros = $176.15/day**, exactly as executed under
`BFB9FD367F639CA4` at 2026-08-22 01:23:35. **Not re-executed and not raised again.**

### Checkpoint — 2026-08-22 09:36 EDT

The planned checkpoints were 2026-08-23, 08-25 and 08-29. **None has been reached yet** — the budget
change is roughly eight hours old. This is the current read, not a settled 24-hour comparison, and
it is labelled as such rather than presented as a checkpoint result.

| Campaign | Impr | Billable clicks | Invalid clicks | Cost | CPC | Primary conv | Conv rate | Budget-lost IS | Rank-lost IS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HVAC Installation | 1,157 | 40 | 26 | $1,100.44 | $27.51 | 0.0 | 0.00% | **54.14%** | 3.04% |
| AC Repair | 165 | 12 | 212 | $997.60 | $83.13 | 1.0 | 8.33% | 5.43% | **59.75%** |
| HVAC Repair | 433 | 7 | 181 | $605.88 | $86.55 | 2.0 | 28.57% | 3.55% | **69.35%** |
| HVAC Replacement | 61 | 2 | 20 | $52.14 | $26.07 | 0.0 | 0.00% | 0.00% | 54.55% |
| Gas Boiler Repair | 2 | 0 | 4 | $0.00 | — | 0.0 | 0.00% | 0.00% | 66.67% |

```
August MTD billable spend   $2,756.06
August maximum              $13,000.00   (a maximum, not a quota)
Remaining                   $10,243.94
Remaining days              10
Total daily budget          $465.63
Worst case                  2,756.06 + (465.63 x 2 x 10) = $12,068.66
Headroom                    $931.34
```

**Invalid clicks are reported separately and are never added to billable clicks or cost:** 443
invalid MTD against 61 billable. That ratio is high and worth watching, but ClickCease is
deprioritised for this phase and no action is proposed.

All three rollback triggers are **clear**: projected spend is under $13,000; HVAC Installation is at
$1,100.44 against the $2,000-with-zero-conversions trigger; budget-lost IS is 54.14%, far above the
5% floor. Rollback remains one mutation to 138,160,000 micros and was not needed.

---

## 6. Campaign-by-campaign verdict

**HVAC Installation — WATCH, hold at $176.15.** The increase is justified on structure: 54% of
impressions lost to budget against only 3% to rank, and a CPC roughly a third of the repair
campaigns. **Zero Primary conversions on 40 clicks and $1,100.44 is the run's top risk.** It is not
disqualifying on its own — at a plausible 5% conversion rate, zero in 40 clicks carries roughly 13%
probability — and it did produce one WhatConverts lead as a secondary signal. Do not increase again.
Re-assess at the 24-hour and 7-day checkpoints against the $2,000 trigger.

**AC Repair — HOLD budget, now protected by the new negatives.** 59.75% rank-lost against 5.43%
budget-lost. This is a quality and rank constraint, not a budget one: Quality Score 4, ad relevance
AVERAGE, landing-page experience AVERAGE, expected CTR BELOW_AVERAGE. More budget buys nothing. The
correct lever is relevance and landing-page work, and the automotive negatives remove the clearest
identified waste.

**HVAC Repair — preserve the new RSAs, judge on leads not CTR.** 69.35% rank-lost, Quality Score 2,
landing-page experience BELOW_AVERAGE. Both new RSAs (821714108336, 821714108339) are ENABLED,
APPROVED and EXCELLENT; both old ones (820900825560, 820900825563) remain PAUSED and preserved. Too
early to judge — assess at 7 settled days on qualified leads and CPL. **Do not roll back on CTR
alone.** This campaign carries the page-level `Recent AC Repair Work` heading defect.

**HVAC Replacement — HOLD.** Two clicks is not evidence. Quality Score 2, landing-page experience
BELOW_AVERAGE. No budget or keyword change. No duplicate ads created.

**Gas Boiler Repair — BLOCKED, and correctly so.** Two impressions, zero delivery, $0.00. Eligibility,
policy, ads, negatives, targeting and budget are all verified clean; this is a keyword-volume
problem whose approved fix is gated on the landing page. **Broad Match is not the answer and was not
considered.**

---

## 7. Landing pages — 15 live renders, real browser

Five pages × {desktop 1440×900, mobile 412×915, desktop with tracking parameters}. All **HTTP 200**,
**160–173 KB**, **every one succeeded on the first attempt**. No SiteGround challenge stub was
encountered — every render carried full content, far above the ~12 KB stub. **No form was submitted
and no telephone link was clicked.**

### Working correctly

- All five H1s service-specific and correct. The HVAC Installation H1 reads "HVAC **Installers**",
  which correctly matches the active keyword `hvac installers` — alignment, not a defect.
- All five canonicals self-referencing and correct.
- **GTM-PQTPQ436 present exactly once** on every page: one `gtm.js` loader, one noscript iframe,
  three container-id occurrences (standard snippet plus noscript URL), four GTM network requests.
- **WhatConverts profile 105803 active** on all five — all four `wc_` cookies set.
- **Click-ID and UTM capture verified working on all five.** With `gclid`, `gbraid`, `wbraid` and all
  five UTMs on the URL, `wc_client` captured **all eight values**.
- **Zero barred claims** anywhere — no 24/7, same-day, emergency, guaranteed response, financing or
  APR language.
- **The barred number 4107610932 appeared in zero tel: hrefs and zero page bodies across all 15
  renders.**
- AC Repair, HVAC Installation and HVAC Replacement carry **zero** cross-service headings.

### Six defects, all still live

| # | Sev | Page(s) | Defect |
|---|---|---|---|
| 1 | **P0** | gas-boiler-repair | H2 still reads `Your HVAC Replacement in 3 Simple Steps` — **blocks `3D823A10CB3C0B25`** |
| 2 | P1 | hvac-repair | H2 still reads `Recent AC Repair Work` |
| 3 | P1 | all five | `wc_swap` = `4109141456+..+4107610932+..+230773` — swap source unchanged |
| 4 | P2 | all five | Malformed tel hrefs: `tel:4107056354`, `tel:(410) 705-6354` |
| 5 | P1 | all five | Three `<form>` instances, 34 duplicate DOM ids per page |
| 6 | P1 | all five | Zero Privacy or Terms links |

Defect 6 is a **plausible** contributor to the BELOW_AVERAGE landing-page experience on HVAC Repair
and HVAC Replacement. Google does not expose per-signal attribution, so that stays an inference —
not proven causation.

### One correction to my own method

My first detection pass tested for a `<script src>` containing "whatconverts" and reported
WhatConverts **absent** on all five pages. That was a harness error, not a site regression:
WhatConverts is injected through GTM, so it has no matching script src. Its presence is proven at
runtime by the four `wc_` cookies. The standing rule is now to assert WhatConverts from the cookies,
never from a script-src pattern.

---

## 8. Gas Boiler keyword `3D823A10CB3C0B25` — still blocked

Ten gate conditions were evaluated on all three views. **Seven pass on every view.** The three that
fail are all the same root cause:

| Condition | desktop / mobile / tracking |
|---|---|
| correct Gas Boiler URL | ✅ ✅ ✅ |
| correct service H1 | ✅ ✅ ✅ |
| **incorrect HVAC Replacement H2 absent** | ❌ ❌ ❌ |
| **`Your Gas Boiler Repair in 3 Simple Steps` visible** | ❌ ❌ ❌ |
| **no material cross-service mismatch** | ❌ ❌ ❌ |
| GTM intact | ✅ ✅ ✅ |
| WhatConverts intact | ✅ ✅ ✅ |
| approved phone behavior | ✅ ✅ ✅ |
| form behavior intact | ✅ ✅ ✅ |
| no new finance-policy language | ✅ ✅ ✅ |

**Verdict: FAIL. The keyword was not created.** Ad group 202339087594 still holds exactly its two
preserved keywords. This is recorded once as a developer dependency and will not be re-raised for
approval — the approval already exists and stands; only the page gate is open.

---

## 9. Landing-page deployment `93A9DF4AA19675E8` — precisely blocked

Four of six preconditions fail, verified independently this run rather than replayed:

| Precondition | Result |
|---|---|
| Real current source available | **FAIL** — workspace search for wp-config, theme, functions.php, Divi layouts, Gravity Forms exports, .sql dumps and any local copy of an offer page returned **zero matches** |
| Deployment target proven | **FAIL** — no host, path or configuration |
| Recoverable backup confirmed | **FAIL** |
| Staging or safe preview path | **FAIL** |
| Handoff and deployment fingerprints reproduce | **PASS** — `9EE19C066DC29D57`, `4A5BB56E2F15A5D2`, `C99270C413C34431`, `93A9DF4AA19675E8` all reproduce byte-for-byte |
| Deploy authority without requesting credentials | **FAIL** |

`sftp`, `scp`, `ssh` and `vercel` exist as executables on PATH, but with no host, key, target or
backup they are not deployment authority. Credentials were not requested. **Nothing was published.**

All read-only QA, patch documentation and developer handoff work was completed instead, and issued
as **Addendum C, fingerprint `FFD7D7A35924F4B2`**.

---

## 10. Conversions and lead quality

The Primary and counted set is exactly the approved three, unchanged:

| ID | Name | Category |
|---|---|---|
| **1068114183** | Calls from ads | PHONE_CALL_LEAD |
| **6885463625** | Ambient Cooling - LP - Submit Lead Form | SUBMIT_LEAD_FORM |
| **6885576934** | Ambient Cooling - LP - Phone call leads | PHONE_CALL_LEAD |

WC Lead, WC Calls, Call BTN Click and Visit Thank you page all remain **Secondary and uncounted**.

One precision point worth stating: a naive query for `primary_for_goal AND
include_in_conversions_metric` returns **ten** IDs, but seven of those are **REMOVED** conversion
actions that retain the flags and cannot record anything. Filtered to ENABLED, the set is exactly
the approved three.

MTD Primary conversions across the five: **3.0.**

| Action | Primary conv | All conv | Campaigns |
|---|---:|---:|---|
| Calls from ads (1068114183) | 1.0 | 1.0 | AC Repair |
| LP Submit Lead Form (6885463625) | 1.0 | 1.0 | HVAC Repair |
| WC Lead (7643656486) | 1.0 | 3.0 | AC Repair, HVAC Installation, HVAC Repair |
| Local actions – Directions | 0.0 | 4.0 | AC Repair, HVAC Installation, HVAC Repair |

WC Lead shows `conversions` 1.0 despite now being Secondary because `metrics.conversions` is stamped
at conversion time and historical columns do not reprocess. **Clean Primary conversions under the
current configuration are 2** — one call, one form — plus that one pre-Plan-B artifact.

**Lead quality remains UNKNOWN.** `WHATCONVERTS_API_TOKEN` exists as a variable name but its value is
empty, so no authenticated WhatConverts session is available and credentials were not requested. No
qualified-lead, sold-job, revenue or gross-profit evidence exists, so **no CPA, CPL, CPQL, CAC or
ROAS figure in this report has been validated against a real outcome.** WC Lead is not treated as
qualified merely because its source is WhatConverts.

---

## 11. Search terms and negatives

The full corpus was classified locally against a service-intent whitelist across six windows —
since-launch, MTD, 30, 90, 365 days and all history. **2,550 rows** written to
`exports/search-terms-verdicts-2026-08-22b.csv`.

Every window returns the same 425 terms, which is correct: the five campaigns launched 2026-08-14,
so "all available history" and "since launch" are the same period for them.

| Verdict | Terms | Cost | Conversions |
|---|---:|---:|---:|
| KEEP | 367 | $2,067.36 | 3.0 |
| WATCH | 48 | $130.85 | 0.0 |
| NEGATIVE-CANDIDATE | 10 | $47.78 | 0.0 |

**Seven of the ten candidates are now blocked** by this run's package, covering the entire $47.78.
The three remaining open candidates — `automotive ac mechanic near me`, `automotive air conditioning
repair near me`, `midea hvac distributor near me` — carry **$0.00 and zero clicks between them**. No
negative is proposed. Adding one merely to show activity is exactly what policy forbids.

**Protected terms were never negated.** 196 terms containing a protected word account for $1,516.62
and all 3 conversions. Ten of them were flagged, but **every one was flagged on an automotive or
marine token, never on the protected word** — the classifier can only return NEGATIVE-CANDIDATE from
the irrelevant-token list, which contains no protected term.

**Shared set 11813144900 "General List" (1,111 members, contains the single words `repair` and
`Repair`) remains unattached** and must never be attached to the five — it would block every repair
keyword in the account. Zero shared sets are attached to any of the five.

---

## 12. Settings, ads, assets, schedule, geography, ClickCease

**Campaign settings — all five verified clean.** Search Network only, Search Partners **off**,
Display **off**, PRESENCE targeting on both positive and negative geo, 75 positive locations and
zero exclusions each, English, all three device types, `TARGET_SPEND` (Maximize Clicks) with **no
CPC ceiling and no portfolio strategy**, unshared budgets with reference count 1, no campaign-level
tracking template or URL suffix. Account-level auto-tagging is on.

Gas Boiler, HVAC Installation and HVAC Replacement report primary status `LIMITED` with
`HAS_ADS_DISAPPROVED`. That reflects the **paused** original Consumer Finance ads still sitting in
those ad groups; the serving ads are approved and all five campaigns report `serving_status =
SERVING`. Cosmetic, not a delivery problem. No mutation warranted.

**Ads.** Every one of the five intended active ad groups holds **exactly two ENABLED, APPROVED
RSAs** — verified individually. Six original disapproved Consumer Finance ads remain PAUSED
(820944944368, 820944944371, 820900825428, 820900825431, 820900825434, 820900825437). Two ads
(820900825422, 820900825425) show ENABLED inside ad group **202339087874, which is REMOVED** — they
are inert and cannot serve, proven by **0 impressions, 0 clicks, $0.00** MTD. Cleanup would need a
destructive-action approval and is not worth it.

**Assets.** Each campaign carries 15 enabled assets: **4 offer-subdomain service sitelinks + 4
retained main-site informational sitelinks** (Customer Reviews, View Our Work, Contact Ambient,
Service Areas), 5 callouts, 1 structured snippet and the call asset. One customer-level callout
asset. The Business Profile location asset was not removed.

**Call asset and phone schedule.** Asset **407995613637** — `(410)705-6354`, US — carries **six
schedule rows** (M–F 08:00–20:00, Sat 08:00–13:00, no Sunday, all minutes ZERO) and is linked to
**exactly the five campaigns and nothing else.** That exclusivity was checked explicitly: four other
call assets exist in the account, all carrying a different number and all linked only to legacy
campaigns. Editing this asset therefore cannot leak into unrelated campaigns.

**Ad schedule is genuinely holding.** Six clean non-overlapping rows per campaign. MTD totals do
show Sunday and overnight impressions, so I tested whether that is live: segmenting by date and
hour, **all out-of-schedule delivery (207 impressions, 7 clicks, $587.95) falls before Package C
took effect at 2026-08-20 11:29 ET.** In the 40 delivering hour-rows since, out-of-schedule delivery
is **zero impressions, zero clicks, $0.00**. The overnight spend is historical, not a current leak.

**Device split** is worth noting: mobile drove 50 of 61 billable clicks, $2,448.27 of $2,756.06, and
**all three conversions**. Desktop spent $307.79 for zero. Not enough volume for a bid decision yet,
but it sharpens why the mobile landing-page defects matter.

**ClickCease — verified only, never modified.** Manager 2815082755 ACTIVE. **2,796 IP exclusions
unchanged.** Account tracking template still routes through `monitor.clickcease.com` with all ten
ValueTrack parameters preserved (`lpurl`, `campaignid`, `adgroupid`, `keyword`, `device`, `network`,
`loc_physical_ms`, `loc_interest_ms`, `placement`, `adposition`). Console and permissions untouched.

---

## 13. WhatConverts decision

**Unresolved and deliberately preserved.**

`wc_swap` reads `4109141456+..+4107610932+..+230773` on all five paid pages — runtime proof that
**+14107610932 is the configured swap *source*** for profile 105803, and +14109141456 is what gets
swapped in. That is a configured value, not automatically a stale one.

No authenticated WhatConverts session exists (`WHATCONVERTS_API_TOKEN` is present as a name but
empty), and credentials were not requested. **Nothing about profile 105803, the swap source, or the
DNI number was changed or proposed for execution.** Green Marketing must confirm whether 4107610932
is stale before any change is drafted.

The visible-number race is a landing-page implementation issue. It is not a Google Ads mutation and
is not a reason to alter ClickCease.

---

## 14. Exact changed and unchanged resources

**Changed — exactly three, all creates:**

```
customers/2401959466/campaignCriteria/24132507741~10008241   negative keyword "car"   BROAD
customers/2401959466/campaignCriteria/24132507741~10000390   negative keyword "auto"  BROAD
customers/2401959466/campaignCriteria/24132507741~10019071   negative keyword "boat"  BROAD
```

**Unchanged-resource proof.** Each bucket counted with an explicit non-REMOVED filter, baseline
versus final:

| Bucket | Baseline | Final | Delta | Expected | Query |
|---|---:|---:|---:|---:|---|
| campaigns | 23 | 23 | 0 | 0 | `SELECT campaign.id FROM campaign WHERE campaign.status != 'REMOVED'` |
| ad groups | 68 | 68 | 0 | 0 | `SELECT ad_group.id FROM ad_group WHERE ad_group.status != 'REMOVED'` |
| ads | 115 | 115 | 0 | 0 | `SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'` |
| positive+negative keywords | 6,968 | 6,968 | 0 | 0 | `SELECT ad_group_criterion.criterion_id FROM ad_group_criterion WHERE type='KEYWORD' AND status != 'REMOVED'` |
| campaign criteria | 13,810 | **13,813** | **+3** | **+3** | `SELECT campaign_criterion.criterion_id FROM campaign_criterion WHERE status != 'REMOVED'` |
| ad schedules | 139 | 139 | 0 | 0 | `…FROM campaign_criterion WHERE type='AD_SCHEDULE' AND status != 'REMOVED'` |
| campaign assets | 283 | 283 | 0 | 0 | `SELECT campaign_asset.asset FROM campaign_asset WHERE status != 'REMOVED'` |
| customer assets | 1 | 1 | 0 | 0 | `SELECT customer_asset.asset FROM customer_asset WHERE status != 'REMOVED'` |
| conversion actions | 16 | 16 | 0 | 0 | `SELECT conversion_action.id FROM conversion_action WHERE status != 'REMOVED'` |
| shared sets | 16 | 16 | 0 | 0 | `SELECT shared_set.id FROM shared_set WHERE status != 'REMOVED'` |
| IP exclusions | 2,796 | 2,796 | 0 | 0 | `…FROM campaign_criterion WHERE type='IP_BLOCK' AND status != 'REMOVED'` |

Also proven unchanged: all five budgets (141450000 / 42760000 / **176150000** / 78950000 / 26320000
micros), all five campaign statuses ENABLED, bidding strategies, the ENABLED primary+counted
conversion set, shared-set associations (0 on the five), locations, manager links, the account
tracking template, and the Gas Boiler ad group's two keywords.

**Website, GTM, WhatConverts and ClickCease: zero changes.**

---

## 15. Monitoring and rollback

| When | What |
|---|---|
| **2026-08-23** | `python scripts/ambient_checkpoint.py --what budget` — first true 24-hour read after the budget increase. Watch HVAC Installation against the $2,000 / zero-Primary trigger. |
| **2026-08-23** | 24-hour negatives check: confirm no legitimate AC Repair query was blocked and impressions did not fall by more than the automotive share. |
| **2026-08-25** | 72-hour budget checkpoint; search-term re-read for new vehicle or marine phrasings not covered by the three tokens. |
| **2026-08-28** | `--what rsa` — 7 settled days on the HVAC Repair RSA swap. Judge on qualified leads and CPL, **not** CTR. |
| **2026-08-29** | Final August budget checkpoint before month end. |

**Watch list, no action yet:** `automotive ac mechanic near me`, `automotive air conditioning repair
near me`, `midea hvac distributor near me`, plus `cars`, `vehicle`, `truck`, `van`, `rv`, `marine`
as unobserved variants. A negative for any of them needs observed cost-bearing evidence **and** a new
fingerprint.

**Rollback recommendations:**

- **Negatives** — none recommended. Readback passed on every assert. If a legitimate AC Repair query
  is ever found blocked, remove only the three named resources above; that is three mutations and
  touches nothing pre-existing.
- **Budget** — one mutation, `15787409441` → 138,160,000 micros, if projected August spend passes
  $13,000, or HVAC Installation passes $2,000 with zero Primary conversions, or budget-lost IS falls
  below 5%. All three are currently clear. **Do not roll back on a single zero-conversion window.**
- **RSA swap** — do not roll back on CTR alone.

---

## 16. Artifacts

**Report** `reports/ambient-cooling-heating/2026-08-22b-reboot-safe-final-completion.md`

**Receipts** `receipts/reboot-recovery-2026-08-22b.json` ·
`receipts/fingerprint-manifest-2026-08-22b.json` · `receipts/negatives-preflight-2026-08-22b.json` ·
`receipts/negatives-validate-only-2026-08-22b.json` ·
`receipts/negatives-mutation-2026-08-22b.json` · `receipts/negatives-readback-2026-08-22b.json` ·
`receipts/negatives-search-term-evidence-2026-08-22b.json`

**Snapshots** `reboot-identity-2026-08-22b.json` · `reboot-baseline-2026-08-22b.json` ·
`reboot-counts-2026-08-22b.json` · `lp-browser-qa-2026-08-22b.json` · `lp-gates-2026-08-22b.json` ·
`search-terms-2026-08-22b.json` · `schedule-compliance-2026-08-22b.json` ·
`final-audit-2026-08-22b.json` · `budget-checkpoint-2026-08-22b.txt`

**Exports** `search-terms-verdicts-2026-08-22b.csv` (2,550 rows)

**Plans** `DEVELOPER-HANDOFF-ADDENDUM-C-2026-08-22.json` (`FFD7D7A35924F4B2`)

**Rollback receipt** none — no rollback was used.

No secrets, credentials, tokens, cookies, authenticated storage or lead PII appear in any artifact.

---

## 17. Bottom line

**No additional immediate Google Ads mutation is recommended.**

Everything authorized and unblocked is done. The two remaining packages are approved, validated,
fingerprint-verified and waiting on one external dependency — a developer changing one heading on
`/gas-boiler-repair/` and, separately, the source, staging, backup and deploy authority that this
environment does not have. Neither needs a new approval from you. The single business question
still open is whether **+1 410-761-0932 is stale or deliberately retained** in WhatConverts profile
105803, and that one needs Green Marketing, not a technical decision.
