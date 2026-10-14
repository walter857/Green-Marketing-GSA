# Ambient: CPL policy revision and approval package (2026-09-30b)

> **CORRECTED 2026-09-30c. See `2026-09-30c-heating-repair-containment.md`.**
> - "Every Search scope is above the ceiling" was wrong. Results are scope-specific: Install & Replace and the two replacement ad groups meet target (n = 1), Boiler Services is in the freeze band, and Heating Repair is a zero-lead stop.
> - `AMB-0930-CPL-CONTAIN-1` / `54300C1A3EF4` is **superseded** by `AMB-0930-CPL-CONTAIN-1R` / `4C544E4CE290`.
> - The $100 post-containment allowance is not authorized.
> - The monitor threshold is **not** a guarantee against crossing $350.
> - The reconciliation now uses v2 rules: reason-reviewed Quotable No, per-opportunity dedupe, enhanced-conversion check, call-path split, and identical sensitivity windows.


**Account:** Ambient Cooling - Live · child 2401959466 · MCC 3373711342 (never used as the child ID).
**Identity:** a fresh exact-name and child-ID check passed on every run today, 8/8 checks.
**External changes in this revision: none.** Google validate-only checks ran and write nothing.
**Dates:** complete days run through 2026-09-29. Sept 30 is partial and shown only as provisional exposure.

**Client requirement:** CPL target **$280**, hard ceiling **$350**.
- Source: an explicit Green Marketing instruction on 2026-09-30.
- Recorded in `client.yaml` as `offer.target_cpl: 280`, `offer.cpl_ceiling: 350` and `offer.cpl_policy`.
- Also recorded in every applicable work order.
- `target_cpql` and `target_cac` are unchanged (null). They are different metrics.

---

## 0. Decision summary

1. **[Corrected in 30c: results are scope-specific, see banner.]** Account and heating-program totals are above the $350 ceiling on reconciled, genuine paid leads. CPL counts only unique genuine paid leads (click ID or matched Google call record):
   - Launch to date (Aug 14 – Sep 29): **$896**
   - September: **$604**
   - Heating since the Sept 24 offer-page migration: **$607**
2. **Heating Repair ad group `204129717007` is the largest live exposure.**
   - $406.12 on complete days, 15 clicks, **0 verified leads**.
   - Plus $169.21 today (provisional).
   - **Recommended now:** `AMB-0930-CPL-CONTAIN-1` · `54300C1A3EF4`. Pause that ad group and lower its campaign's budget from $85 to $30. The four other repair services stay on.
3. **Boiler Services is in the freeze band** at $346.49 per lead. One more click without a lead crosses $350.
   - A standby plan is ready: `AMB-0930-CPL-CONTAIN-2` · `7267DEE648C0`.
   - It pauses Boiler Repair and Gas Boiler Repair, and may execute only on a confirmed trigger. Its trigger is not met today.
4. **Both maintenance services stay on hold.**
   - Boiler Maintenance: the page still carries installation content (D2).
   - Heat Pump Maintenance: the evidence can't support $280, and not even $350 (section 6).
   - The earlier plans `AMB-0930-HPM-BUDGET-1` (`7472853C4EA9`) and `AMB-0930-HPM-ENABLE-1` (`90C7E29E61BA`) are **withdrawn**. Their files are renamed `.WITHDRAWN.json`, and their executor refuses to run.
5. **The CPL monitor is built and dry-run tested, but it is NOT ACTIVE.** No scheduler, no alert recipient, no write authority (section 8).
6. **Correction:** my previous summary said the maintenance test "will be paused automatically". **That was wrong.** No automation existed. The stop-loss was only a policy statement.

---

## 1. Requirement recorded (validated, not bypassed)

| File | Change | Validation |
|---|---|---|
| `clients/ambient-cooling-heating/client.yaml` | `offer.target_cpl: 280`, `offer.cpl_ceiling: 350`, `offer.cpl_policy` (definition, source, date) | `schemas/client.schema.json`: PASS |
| `work-order.yaml` (account / cooling) | CPL inputs | validator + schema: 0 errors |
| `work-orders/work-order-heating-transition-2026-09.yaml` (heating program) | CPL inputs + controls reference | 0 errors |
| `work-orders/work-order-heat-pump-maintenance-2026-09-30.yaml` | CPL inputs + HOLD status + withdrawal note | 0 errors |
| `work-orders/work-order-boiler-maintenance-2026-09-30.yaml` | CPL inputs | 0 errors |
| **new** `work-orders/work-order-heating-repair-cpl-containment-2026-09-30.yaml` | exact service Heating Repair, mode draft | 0 errors |
| **new** `work-orders/work-order-gas-boiler-repair-cpl-standby-2026-09-30.yaml` | exact service Gas Boiler Repair (related: Boiler Repair), mode draft | 0 errors |

---

## 2. How CPL is reconciled

Script: `scripts/ambient_0930_cpl_reconcile.py`. Output: `snapshots/cpl-reconciliation-2026-09-30.json`. It prints no personal data.

**Definition.** CPL = all ad spend in the scope and window, including every click type (headline, sitelink, location, call), divided by unique genuine paid leads.
- **Paid** means one of two things:
  - a session click ID that resolves in this account's `click_view` (2,180 click IDs read for Aug 14 – Sep 30);
  - a WhatConverts call matched to a Google `call_view` record (start within 150 s, duration within 5 s).
- **Genuine** means none of these apply:
  - QA submission (6 removed);
  - spam;
  - Quotable = No;
  - a call under 60 s that isn't marked Quotable Yes;
  - a ringing hang-up.
- **Unique** means one lead per contact within the window. A hashed phone or email is used for matching and never printed.
- **Dates:** a lead is dated by its click date or call date, and spend uses the same dates. Leads that arrive after a window closes are shown as lag.
- A genuine paid lead marked Quotable: Not Set counts toward CPL, but is never assumed qualified.

**WhatConverts rows reconciled:** 240 (default 137, duplicate 73, spam 30).

| Window | Paid-proven leads | Excluded (not genuine) | Unique genuine paid leads |
|---|---|---|---|
| Aug 14 – Sep 30 | 15 (10 click ID, 5 Google call record) | 4: quotable-No calls under 60 s and one quotable-No form | **11** |
| September | 5 (4 click ID, 1 call record) | 0 | **5** |
| Heating (Sep 17 – 30) | 2 (both click ID) | 0 | **2** |

**Attribution gaps** (reported, **not** counted, and not assumed to lower CPL):
- **September, genuine-looking but unproven:**
  - 1 lead labeled google/cpc with no click ID: a repeat main-site contact form on Sept 27.
  - 2 short calls on 415-9517 (29 s and 14 s).
- **Google call records with no WhatConverts record on any number within 30 minutes:**
  - Sept 25, 52 s, Heating Repair.
  - Sept 30, 60 s, Heating Repair (provisional).
  - Aug 24 (×2) and Aug 27, HVAC Repair.
- **August, unproven:**
  - Two quotable-Yes calls on 705-6354 (141 s and 198 s). The number is fixed-source, so a call can't be bound to a click.
  - One quotable-Yes call whose gclid is not in this account's click data.
- **Excluded as other channels:** leads labeled "LSA … /cpc" or "GBP … /cpc" (11 since Aug 14).
- **Sensitivity check:** if the Sept 25 Heating Repair call were counted, heating would be $1,284.85 / 3 = $428, and Heating Repair $406, still **above $350**.

**Conversion lag:** no counted lead arrived after its window closed. Both Sept 28 leads arrived the same day and were credited to WC Lead on both click date and conversion date. A WhatConverts "Success" upload is **not** counted as a lead. For example, all 6 QA uploads were accepted and none was credited.

**Google-credited Primary conversions vs unique genuine paid leads, Aug 14 – Sep 29:**

| Campaign | Google credited | Unique genuine paid leads | Comment |
|---|---|---|---|
| AC Repair | 5 | 6 | undercounted |
| HVAC Repair | 6 | 1 | overcounted: duplicate and unverified conversions |
| HVAC Installation | 3 | 2 | duplicates on Sept 1 (LP form plus 2 WC Lead) |
| Boiler Services | 1 | 1 | |
| Heat/Furnace Install & Replace | 1 | 1 | |
| **Total** | **16** | **11** | |

---

## 3. CPL by scope against $280 / $350

Bands for scopes with leads:
- **MET:** $280 or less.
- **FREEZE:** above $280, up to $350.
- **BREACH:** above $350.

Zero-lead scopes show CPL as *undefined*, and their spend is reported as spend without a verified lead.

### Account and program

| Scope | Window | Spend | Clicks | Unique paid leads | CPL | Band |
|---|---|---|---|---|---|---|
| Account (all Search) | Aug 14 – Sep 29 | $9,861.21 | 242 | 11 | **$896** | BREACH |
| Account | Cooling uncapped, Aug 14 – Sep 3 | $8,025.18 | 172 | 9 | $892 | BREACH |
| Account | Cooling capped, Sep 4 – 21 | $564.02 | 22 | 0 | undefined | zero-lead |
| Account | September to date | $3,018.41 | 87 | 5 | **$604** | BREACH |
| Cooling (4 campaigns) | Aug 14 – Sep 29 | $8,576.36 | 193 | 9 | $953 | BREACH, now paused or not serving |
| Heating program (7 campaigns) | Sep 17 – 29 | $1,284.85 | 49 | 2 | **$642** | BREACH |
| Heating program | since Sep 24 | $1,214.07 | 42 | 2 | **$607** | BREACH |
| Heating program | last 7 days | $1,265.71 | 47 | 2 | $633 | BREACH |
| Heating program | Sep 30, **provisional** | $322.50 | 12 | 0 | – | provisional |

### Heating campaigns (cumulative, complete days)

| Campaign | Spend | Leads | CPL / band | Headroom before breach | Today (provisional) |
|---|---|---|---|---|---|
| 24257819463 Heating & Furnace Repair | $469.90 | 0 | undefined, **zero-lead STOP** | – | $169.21 |
| 24132507744 Boiler Services | $346.49 | 1 | $346, **FREEZE** | **$3.51** | $0.00 |
| 24257819466 Heat/Furnace Install & Replace | $233.59 | 1 | $234, MET | $116.41 (less than one day's $120 maximum) | $99.93 |
| 24268690038 Heat Pump & Ductless | $78.42 | 0 | undefined, watch | – | $23.37 |
| 24268690041 Thermostat | $23.65 | 0 | undefined, watch | – | $29.99 |
| 24279798229 Maintenance & Inspection (not serving) | $82.22 | 0 | history | – | $0 |
| 24274160783 Geothermal (not serving) | $50.58 | 0 | history | – | $0 |

### Heating ad groups (serving ones first)

| Ad group | Spend | Leads | CPL / band | Zero-lead stop threshold* |
|---|---|---|---|---|
| **204129717007 Heating Repair** | **$406.12** (+$169.21 provisional) | 0 | **STOP** | $180 |
| 204129718047 Boiler Repair | $242.87 | 0 | watch, **one click from its stop** | $260 |
| 202339087594 Gas Boiler Repair | $82.41 | 0 | watch | $260 |
| 199797580706 Furnace Repair | $63.78 | 0 | watch | $180 ($290 after CONTAIN-1) |
| 204129717527 Heat Pump Installation | $78.42 (+$23.37) | 0 | watch | $300 |
| 204129717967 Heating Installation | $44.73 (+$83.90) | 0 | watch | $230 |
| 204129718927 Thermostat Replacement | $23.65 (+$13.86) | 0 | watch | $300 |
| 204129717767 Furnace Replacement | $171.25 | 1 | $171, MET (preliminary, n = 1) | – |
| 204129718207 Boiler Replacement | $21.21 | 1 | $21, MET (preliminary, n = 1) | – |

\* Stop threshold = min($300, $350 − one day's maximum spend for the host campaign, which is 2 × its daily budget). See section 7.

**The replacement leads are preliminary evidence** (n = 1 each). They do not prove those ad groups can scale profitably. No scaling is proposed.

---

## 4. Scopes already breaching the proposed controls

| Scope | State | Status |
|---|---|---|
| Account, all windows | BREACH ($604–$896) | Contained by pausing the zero-lead drivers. Totals below. |
| Heating program | BREACH ($607–$642) | CONTAIN-1 removes its largest zero-lead driver. |
| **Heating & Furnace Repair campaign / Heating Repair ad group** | **ZERO-LEAD STOP** | **CONTAIN-1, approval needed.** |
| Boiler Services | FREEZE, $3.51 of headroom | Freeze expansion. CONTAIN-2 is on standby. |
| Install & Replace | MET, but one serving day can breach | Watch daily. No scaling. |
| Cooling AC Repair / HVAC Repair / HVAC Installation / HVAC Replacement | BREACH or zero-lead (history) | Already paused or not serving. Any spring restart needs a CPL-compliant plan. |

---

## 5. Containment and correction recommendations

### AMB-0930-CPL-CONTAIN-1 · `54300C1A3EF4` · 2 operations · recommended now

| # | Resource | Current | Proposed |
|---|---|---|---|
| 1 | Ad group **204129717007** `SKAG \| Heating Repair` (campaign 24257819463) | ENABLED | **PAUSED** |
| 2 | Campaign budget of 24257819463 (`Search \| NonBrand \| Heating & Furnace Repair \| Central MD \| BOFU \| 2026-09`) | $85.00/day | **$30.00/day** |

- **Not touched:** Furnace Repair 199797580706, Gas Furnace Repair 204129717247, Electric Furnace Repair 204129717287 and No Heat Repair 204129717087 stay ENABLED. No keyword, ad, asset, bid, schedule, geo or conversion change.
- **Budget impact:** the enabled total drops from $305/day to **$250/day** (monthly maximum $9,272 → $7,600). The Repair campaign's worst possible day drops from $170 to $60. This is a spending decrease; no limit is raised.
- **Why:** $406.12 on 15 clicks with no verified lead is above every stop threshold. The campaign spent $119–$169 on each of its last four serving days, mostly in this ad group, so each day it stays on adds exposure. Even the unverified Sept 25 call would leave it at $406 per lead.
- **After containment:**
  - The campaign's history stays marked as breached; it is never reset.
  - The post-containment period is reported beside it.
  - If the campaign adds $100 more zero-lead spend after containment, I'll propose pausing the whole campaign.
- **Restart rule:** never automatic. A restart needs all three:
  - a verified fix (D6 form, message match between "heating repair" searches and the "HVAC Repair" page, and the call path);
  - a bounded post-fix test capped at $150 of zero-lead spend;
  - a new explicit approval.

### AMB-0930-CPL-CONTAIN-2 · `7267DEE648C0` · 2 operations · standby

| # | Resource | Current | Proposed |
|---|---|---|---|
| 1 | Ad group **204129718047** `SKAG \| Boiler Repair` (campaign 24132507744) | ENABLED | PAUSED |
| 2 | Ad group **202339087594** `SKAG \| Gas Boiler Repair` | ENABLED | PAUSED |

- **Trigger:** it may execute only if a fresh reconciliation run confirms either:
  - Boiler Services CPL above $350 on complete days; or
  - Boiler Repair zero-lead spend of $260 or more.
  
  The executor re-runs the reconciliation and refuses if neither is true. **Not met today:** $346.49 per lead and $242.87.
- **Not touched:** Boiler Replacement 204129718207 (has a lead). No budget change.
- **Why these two together:** both land on `/gas-boiler-repair/`. Together they have $325.28 of zero-lead spend at about $40 a click. Historical boiler repair CPA was $423–$791.

### Corrections: developer and account

See `clients/ambient-cooling-heating/dev-tasks/DEV-2026-09-30-cpl-priority-corrections.md` for full acceptance tests. None of these changes is authorized yet.

Developer, in order:
1. **D6:** the optional message field blocks submissions.
2. **D5:** 3 forms per page and 55 duplicate IDs.
3. **D7:** server-filled attribution fields under the page cache.
4. **D1:** 761-0932 in the page source, including a `tel:` link on `/gas-boiler-repair/`.
5. **D2:** boiler maintenance and installation pages have swapped content.
6. **D4:** service copy mismatches.

Account:
- **Call path:** keep the existing proof requirement before enabling any call asset on the held campaigns.
- **Location calls:** check the Google Ads phone override on all 3 Business Profile locations. The untracked Heating Repair calls point to this gap.
- **Conversions:** resolve the call double count and the enhanced-conversions setting before any conversion-based bidding.

---

## 6. Maintenance: HOLD, with the math

**Break-even conversion rate = CPC ÷ CPL.**

| | Heat Pump Maintenance | Boiler Maintenance |
|---|---|---|
| Page | Conditional pass: 3 copy mismatches (D4), plus D1/D5/D6/D7 | **FAIL (D2)** |
| Expected CPC | about $26 (Heat Pump campaign average) | about $35–$40 (Boiler campaign) |
| Conversion rate needed for $280 / $350 | **9.3% / 7.4%** | **12.5–14.3% / 10–11.4%** |
| Evidence | All maintenance keywords in account history: 186 clicks, $4,326.66, 12 Google conversions, which is 6.5% and **$361 per conversion**. Google's conversions double-counted then, so these figures flatter. Heat pump maintenance specifically: 4 clicks, $183.63, 0 conversions. Heating-season WhatConverts maintenance leads: 0 Yes / 1 No / 7 unset. | Search-term history: 28 clicks, $2,102.23, 4 conversions, **$526 per conversion** at a $75 CPC. |
| Expected volume | 2–4 clicks a month (about 70 searches a month) | About 10 searches a month |
| Verdict | **HOLD.** Even the flattering history gives about $400 per lead at today's CPC. At 2–4 clicks a month, a $280 result could not be shown this season, and a test would sit at or above the ceiling most of the time. | **HOLD.** Blocked by D2. The evidence is also against it after D2 is fixed. |

**What would change the answer:** a demonstrated conversion rate of 9.3% or higher on the offer pages after D6/D5/D7 are fixed. If that appears, a bounded test would be:
- existing ads only;
- no budget increase;
- a $300 zero-lead stop (kept, and not relaxed to $350).

The maintenance evaluation report carries a revision banner pointing here.

---

## 7. Cost-control rules (proposed)

**Scopes:**
- Account (all Search).
- Heating program.
- Each serving campaign.
- Each serving ad group (one ad group = one exact service).

A good blended average never overrides a failing ad group.

**Evaluation window:**
- Cumulative from the scope's first spend since 2026-08-14, on complete days only. Starts are never reset.
- A rolling last-14-day view is shown alongside.
- A post-fix period is always shown beside the full prior history.

**Leads:** reconciled unique genuine paid leads (section 2), dated by click or call date. Google-credited conversions are shown separately and never replace the reconciled count.

**Conversion lag:**
- Leads that arrive through the current day are credited to their click date.
- A zero-lead STOP is proposed only after a fresh WhatConverts pull (default, duplicate and spam sets) in the same run.
- A lead that arrives later reverses the band on the next run. Spend is never discounted for lag.

**Bands, for scopes with leads:**

| CPL | Action |
|---|---|
| $280 or less | Target met. **No automatic scaling.** |
| Above $280, up to $350 | Freeze expansion: no budget, bid, keyword or service additions. Investigate within 1 business day. |
| Above $350 | Breach. Immediate containment review of the zero-lead ad groups inside the scope. |

Also: if headroom to breach (350 × leads − spend) is smaller than one day's maximum spend, raise an alert.

**Zero-lead scopes:**
- CPL shows as undefined, not $0.
- Report spend without a verified lead.
- **Alert:** at $280, or when spend + one day's maximum would reach $350.
- **Stop:** at **min($300, $350 − D)**, where D = 2 × the host campaign's daily budget.
  - [Withdrawn in 30c] D is not a hard maximum. Google can exceed 2× in one day, and reporting and execution delays apply, so the threshold is a risk-reduction heuristic, not a guarantee.
  - Stop thresholds today: Repair groups $180 ($290 after CONTAIN-1), Install & Replace $230, Boiler $260, Heat Pump and Thermostat $300.
- **Maintenance:** any later maintenance test keeps its **$300** zero-lead stop (Heat Pump D = $30).

**Monitoring frequency (proposed):**
- Weekdays at **07:30 ET**, a morning gate on complete days, before the 08:00 schedule starts.
- **12:00 and 15:00 ET** provisional exposure checks.
- Current-day cost is labeled PROVISIONAL. Google cost can lag by hours.

**Affected resources:** every ENABLED campaign and every ENABLED ad group with at least one enabled ad (listed in section 3). Paused scopes are history only.

**Restart rule:** never automatic. A restart needs a verified fix, a bounded post-fix zero-lead cap ($150), and a new explicit approval. Prior losses stay in the record.

These are financial risk controls, not a claim that a small sample proves a service cannot convert.

---

## 8. Monitoring: what actually exists

| Item | Status |
|---|---|
| Implementation | `scripts/ambient_cpl_monitor.py`: dry-run and alert-only. **It contains no Google Ads write code.** It reuses `scripts/ambient_0930_cpl_reconcile.py`. |
| Dry-run evidence | Runs at 2026-09-30 13:10 and 13:11 ET. Logs: `clients/ambient-cooling-heating/monitoring/cpl-monitor-2026-09-30-1310.*` and `-1311.*`. Exit code 2, meaning alerts present. It flagged Heating Repair 204129717007 STOP, the Repair campaign STOP, Boiler Services FREEZE, and Install & Replace one-day-to-breach. |
| Data freshness and failure handling | Records the complete-day cutoff and the provisional day. If the reconciliation or an API read fails, it writes status FAILED and exits 1 with no conclusions. |
| Schedule | **None.** No Windows scheduled task, no Claude scheduled job, no cloud routine (all checked 2026-09-30). |
| Execution location | **None deployed.** Proposed: Windows Task Scheduler on this workstation, where the credentials already live. The monitor won't run while the machine is off. |
| Alert recipient | **None configured.** Owner to name one. |
| Resources it may pause | **None.** Pause authority would need a separate approval listing exact ad-group IDs. |
| Old checkpoint script `scripts/ambient_checkpoint.py` | Manual, cooling-era (the five August campaigns). Last state Sept 10. Its only write is an obsolete CPC rollback. Not a CPL monitor. |
| **Overall** | **NOT ACTIVE** |

Until the monitor is deployed and approved, the controls are enforced by a manual daily run and approval-gated containment plans.

---

## 9. Bidding: reassessed, no change proposed yet

- **Today:** Maximize Clicks with evidence-based CPC ceilings. It spends each budget on clicks, not on leads.
- **Why not Target CPA now:**
  - Only 2 verified heating leads in 8 serving days.
  - Google's Primary conversions are duplicated: 16 credited against 11 unique leads since launch. The causes are Calls from ads plus WC Lead on the same call, the LP form plus WC Lead, and enhanced conversions uploading leads without click IDs.
  - A Target CPA of $280 would learn from wrong inputs, and it would not guarantee the $350 ceiling anyway.
- **CPC caps:** no new caps. September 4 showed that caps cut the converting price band: 12 of 13 converting clicks cost more than the $25/$30 caps. A converting click's own CPC isn't available per click, so any cap would be a guess.
- **Preconditions for a conversion-based bidding proposal:**
  1. The call double count is resolved: the dedicated extension number is verified, and only one call action is biddable.
  2. The enhanced-conversions setting no longer sends non-click leads to the biddable action.
  3. D6/D7 are fixed.
  4. At least 15 verified paid leads over 30 days in the proposed portfolio.

  After that, a bounded test could be Maximize Conversions with a portfolio target CPA of about $250 on the scopes with evidence (Install & Replace, Boiler Replacement), with these CPL controls still running. Any bid-strategy change needs its own exact plan.

---

## 10. Exact changes, validation, approval codes

| Plan | Fingerprint | Operations | Status |
|---|---|---|---|
| AMB-0930-CPL-CONTAIN-1 | `54300C1A3EF4` | 2: pause ad group 204129717007; budget of 24257819463 from $85 to $30 | **Recommended for approval now** |
| AMB-0930-CPL-CONTAIN-2 | `7267DEE648C0` | 2: pause ad groups 204129718047 and 202339087594 | Standby. Executes only on a confirmed trigger. |
| AMB-0930-HPM-BUDGET-1 | `7472853C4EA9` | – | **WITHDRAWN**, never reuse |
| AMB-0930-HPM-ENABLE-1 | `90C7E29E61BA` | – | **WITHDRAWN**, never reuse |

**Validation:**
- Identity gate PASS 8/8, run fresh by every script.
- `client.yaml` passes its schema.
- 7 work orders: 0 validator errors, schema PASS.
- `assert_target_matches` and `assert_no_embedded_secrets`: PASS.
- **Google validate-only: both plans VALIDATE_OK.**
- Fingerprints rebuilt twice from fresh data: identical.
- No enable operation exists in any proposed plan. Nothing raises a budget or a bid.

**Evidence files:**
- `snapshots/cpl-reconciliation-2026-09-30.json`
- `monitoring/cpl-monitor-2026-09-30-1311.json`
- `plans/AMB-0930-CPL-CONTAIN-1.json`, `plans/AMB-0930-CPL-CONTAIN-2.json`
- Scripts: `scripts/ambient_0930_cpl_reconcile.py`, `scripts/ambient_cpl_monitor.py`, `scripts/ambient_0930_cpl_contain_plans.py`

## 11. Next approvals

1. `APPROVE AMB-0930-CPL-CONTAIN-1 54300C1A3EF4 2 operations FOR 2401959466`
   - Execute it, then read it back.
   - Best done before 08:00 ET on a weekday, because the ads start at 08:00.
2. **Optional:** `APPROVE STANDBY AMB-0930-CPL-CONTAIN-2 7267DEE648C0 2 operations FOR 2401959466`
   - Executes only when a fresh run confirms the trigger. I report before and after.
3. **Monitor deployment decision:**
   - where it runs;
   - alert recipient;
   - alert-only, or with pause authority for listed ad-group IDs (a separate approval).
4. **Developer:** D6 → D5 → D7 → D1 → D2 → D4.
5. **Ambient:** please mark the two Sept 28 leads as Quotable Yes or No.
