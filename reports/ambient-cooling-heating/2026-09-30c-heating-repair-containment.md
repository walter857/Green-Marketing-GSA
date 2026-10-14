# Ambient: Heating Repair containment package and CPL corrections (2026-09-30c)

**Account:** Ambient Cooling - Live · child 2401959466 · MCC 3373711342 (not the child).
**Service:** Heating Repair. Work order: `work-orders/work-order-heating-repair-cpl-containment-2026-09-30.yaml` (validates).
**Client CPL:** target $280, hard ceiling $350 (unchanged).
**External changes: none.** Nothing is executed and no monitor is deployed.
**Timing:** fresh identity and resource checks at 14:04 ET (8/8). Complete days run through Sept 29. Sept 30 is provisional.

## 1. Containment for approval: AMB-0930-CPL-CONTAIN-1R · `4C544E4CE290`

This supersedes `54300C1A3EF4` and the interim `BE1F8C24E8A8`. The approval text changed: the post-containment
allowance is removed, the timing statement is corrected, and a baseline of unrelated resources is now locked into
the fingerprint.

| # | Resource | Now (verified 14:04) | Proposed |
|---|---|---|---|
| 1 | Ad group **204129717007** `SKAG \| Heating Repair`, campaign 24257819463 | ENABLED (2 enabled ads, 6 keywords) | **PAUSED** |
| 2 | Budget **15885327972** of campaign 24257819463 `Search \| NonBrand \| Heating & Furnace Repair \| Central MD \| BOFU \| 2026-09` | $85.00/day, not shared | **$30.00/day** |

- **Preserved** and locked into the fingerprint, with a readback comparison after execution:
  - The four other repair ad groups stay ENABLED with their ads and keywords: Furnace Repair 199797580706, No Heat Repair 204129717087, Gas Furnace Repair 204129717247 and Electric Furnace Repair 204129717287.
  - Emergency Heating Repair 204129717047 stays as it is (no ads).
  - The campaign's bidding (Maximize Clicks, $42 ceiling), Mon–Fri 08–16 schedule, 75 Presence locations, networks, asset links and shared negative lists.
  - Every other campaign's status, bidding, ceiling and budget.
- **Validation:**
  - Google validate-only: VALIDATE_OK.
  - Fingerprint rebuilt twice from fresh data: identical.
  - Work order and client profile: valid.
  - Target and secret checks: PASS.
- **Execution contract** (`scripts/ambient_0930_cpl_contain_plans.py execute --plan AMB-0930-CPL-CONTAIN-1R --fp 4C544E4CE290`):
  - Rebuilds the plan from fresh state and refuses if the fingerprint differs. Any change to the payload or its conditions needs a new fingerprint.
  - Runs one atomic mutate.
  - Reads back both changes and compares every baseline value.
  - Writes a receipt.
- **Timing (corrected):**
  - Once approved, execute promptly, whatever that day's spend is. The pause takes effect within minutes.
  - A same-day budget cut does **not** replace that day's charging limit, which was already set by the $85 budget. The $30 budget governs from the next day.
- **Budget effect:** enabled budgets drop from $305/day to $250/day. Nothing is raised.

### Does the new call evidence change the rationale? It narrows it; it doesn't reverse it.

The two Google call records on this ad group have no WhatConverts record on any number within 3 hours:
- **Sept 25, 52 s.** A day with 2 Maps/location clicks and 0 call-button clicks, so most likely a location-asset call.
- **Sept 30, 60 s, provisional.** Google shows one charged call click ($15.18) even though both call-asset links on this campaign are paused.

Both reached a number WhatConverts doesn't track, so neither can be verified as a genuine lead. A new 130-second call labeled google/cpc at 13:40 today has no click ID, is a repeat contact, and landed on a main-site page that no current ad uses. It is not attributable.

| Ad group 204129717007, same window each row | Spend | Verified leads | CPL | If every unverified Google call is a lead |
|---|---|---|---|---|
| Sept 17–29 (complete days) | $406.12 | 0 | undefined, zero-lead **STOP** | 1 → **$406** (still a breach) |
| Sept 17–30 (with today's provisional spend) | $575.33 | 0 | undefined | 2 → **$288** (above target, below ceiling) |

The verified basis is a zero-lead stop. Only if both short, untracked calls were genuine, and today's provisional
spend is included, would the ad group sit at $288. That is still above target, with no path to verify those leads.

## 2. Corrected CPL table (v2 rules)

**What changed:**
- "Every Search scope breaches" is replaced by the scope-specific results below.
- Qualified (Quotable Yes) is shown separately from genuine paid leads.
- Quotable No is excluded only for a reviewed reason. Three calls carried wrong-number signals; a 57-second sales call and a form with no negative signal now count as genuine but not qualified.
- One lead per **opportunity**: the same contact within 14 days.
- Paid location-asset calls are separated from organic Business Profile calls. Call paths: 4 call asset, 1 paid location asset, 133 organic Business Profile.
- Enhanced conversions checked: 0 Google WC Lead credits lack a matching click-ID lead, so no genuine enhanced-conversion lead was dropped.
- Base and sensitivity use identical windows.

| Scope (window) | Spend | Genuine paid leads | Qualified | CPL vs $280 / $350 | Sensitivity (same window, + unverified paid calls) |
|---|---|---|---|---|---|
| Account, Aug 14 – Sep 29 | $9,861.21 | 13 | 8 | **$759: breach** | 17 → $580 |
| Cooling (4 campaigns, paused or not serving), Aug 14 – Sep 29 | $8,576.36 | 11 | 8 | $780: breach (history) | 14 → $613 |
| Heating program, Sep 17–29 | $1,284.85 | 2 | 0 | **$642: breach** | 3 → $428 |
| Heating program, Sep 24–29 | $1,214.07 | 2 | 0 | $607: breach | 3 → $405 |
| Heating & Furnace Repair campaign, Sep 17–29 | $469.90 | 0 | 0 | undefined, zero-lead **STOP** | 1 → $470 |
| **Heating Repair ad group**, Sep 17–29 | **$406.12** | 0 | 0 | undefined, zero-lead **STOP** | 1 → $406 |
| Boiler Services campaign, Sep 17–29 | $346.49 | 1 | 0 | $346: freeze | 1 → $346 |
| Install & Replace campaign, Sep 17–29 | $233.59 | 1 | 0 | $234: target met (n = 1) | 1 → $234 |
| Furnace Replacement ad group | $171.25 | 1 | 0 | $171: met (preliminary) | same |
| Boiler Replacement ad group | $21.21 | 1 | 0 | $21: met (preliminary) | same |
| Boiler Repair / Gas Boiler Repair ad groups | $242.87 / $82.41 | 0 / 0 | – | zero-lead, below alert | same |
| Heat Pump / Thermostat campaigns | $78.42 / $23.65 | 0 / 0 | – | zero-lead, below alert | same |

Qualified-lead CPL is not computable for heating: both Sept 28 leads are still Quotable "Not Set". Account CPQL is $1,233 (cooling history).

## 3. Current exposure decisions

| Scope | Complete days | Today (provisional) | Headroom before $350 | Decision |
|---|---|---|---|---|
| **Boiler Services** 24132507744 | $346.49, 1 lead (Boiler Replacement, Not Set) | $0.00 | **$3.51** | **Freeze** expansion. CONTAIN-2 (`7267DEE648C0`) is **not** being asked for approval. Its trigger is not met (campaign $346.49 per lead; Boiler Repair $242.87 zero-lead). One more boiler click without a lead meets it; I'll bring it back for approval then. Boiler spent 2.6× its budget on Sept 29 (about $118), so one day can take it well past $350. |
| **Install & Replace** 24257819466 | $233.59, 1 lead (Furnace Replacement, Not Set) | $99.93 (Heating Installation $83.90, Heating Replacement $16.03) | $116.41 on complete days; **$16.48 including today** | Target met on complete days. No scaling. If no lead arrives, tomorrow's complete-day CPL is about $334 (freeze). Heating Installation 204129717967 (zero-lead $44.73 + $83.90 today) is the group to review first if it breaches. |
| Heat Pump Maintenance / Boiler Maintenance | – | – | – | Stay paused. No budget expansion. |

**After CONTAIN-1R, separate risk (not authorized):**
- No further zero-lead allowance is authorized for campaign 24257819463.
- Its four remaining repair groups can still spend: about $60/day nominal at the $30 budget, more on overdelivery days, and up to $912/month under the charging limit.
- Every such dollar adds to a campaign already $469.90 into zero-lead spend. I'll report it daily. Any campaign-level action needs its own approval.

## 4. Monitor: NOT ACTIVE

- `scripts/ambient_cpl_monitor.py` is alert-only and has no write code. A dry run at 14:12 ET: 0 writes, flagged Heating Repair STOP.
- There is no scheduler, no alert recipient and no pause authority.
- The earlier statement that its formula keeps a scope from passing $350 is **withdrawn**. The threshold is a risk-reduction heuristic. It now uses the day's highest budget, but it can't cover:
  - single-day overdelivery beyond 2× (seen at 2.6×);
  - cost reporting lag and restatements;
  - unreported clicks;
  - the time it takes a person to act on an alert;
  - API or execution failures;
  - a counted lead later being reclassified.
- No automatic restart. No pause authority without an exact approval.

## 5. Developer QA (tightened)

See `clients/ambient-cooling-heating/dev-tasks/DEV-2026-09-30-cpl-priority-corrections.md` (revised 2026-09-30c):
- **D6:** must pass a submission with the message field genuinely blank, from every placement.
- **D1:** must preserve WhatConverts number swapping; swap rule 230773 is retargeted in the same release.
- **D7:** must isolate unrelated visitors while keeping a returning visitor's own attribution.
- **QA suppression:** must cover WhatConverts uploads, not just GTM.
- **Order:** pages with paid traffic come first.

## 6. Remaining approvals

1. `APPROVE AMB-0930-CPL-CONTAIN-1R 4C544E4CE290 2 operations FOR 2401959466`: execute, read back, and report.
2. Boiler CONTAIN-2: no approval requested now. It returns for approval when its trigger is confirmed.
3. Monitor deployment (location, alert recipient, alert-only or pause authority on listed IDs): open. It stays NOT ACTIVE until then.
4. Website and tracking changes (D6 → D5 → D7 → D1 → D4 on paid pages → D2/D4 on unpaid pages): each needs approval of the exact change.
5. WhatConverts QA-upload suppression and the swap-rule 230773 retarget: each needs its own conversion or tracking approval.
6. Owner: check the Google Ads phone override on all three Business Profile locations, and mark the two Sept 28 leads Quotable.
