# 10 — Location, Budget, Schedule and Device Plan

**Pro Green - Austin - Live | 7380491929 | outdoor design & build | 2026-08-18**

---

## 1. Location crosswalk — the fixed 24

Every supplied label was resolved with `GeoTargetConstantService.suggest_geo_target_constants` and
cross-checked against the `geo_target_constant` records for the 24 constants the live campaigns
actually target. Both campaigns carry an identical set.

| # | Supplied label | Geo target constant ID | Canonical Google Ads name | Target type | Current account status | Verdict |
|---|---|---|---|---|---|---|
| 1 | 78642, Texas, United States | 9028250 | 78642,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 2 | 78681, Texas, United States | 9028275 | 78681,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 3 | 78732, Texas, United States | 9028298 | 78732,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 4 | 78703, Texas, United States | 9028278 | 78703,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 5 | 78726, Texas, United States | 9028292 | 78726,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 6 | Barton Creek, Texas, United States | 9051551 | Barton Creek,Texas,United States | City | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 7 | 78613, Texas, United States | 9028226 | 78613,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 8 | 78717, Texas, United States | 9028284 | 78717,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 9 | 78738, Texas, United States | 9028304 | 78738,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 10 | 78746, Texas, United States | 9028310 | 78746,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 11 | 78733, Texas, United States | 9028299 | 78733,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 12 | 78628, Texas, United States | 9028239 | 78628,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 13 | Cedar Park, Texas, United States | 1026276 | Cedar Park,Texas,United States | City | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 14 | 78750, Texas, United States | 9028314 | 78750,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 15 | Georgetown, Texas, United States | 1026424 | Georgetown,Texas,United States | City | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 16 | 78730, Texas, United States | 9028296 | 78730,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 17 | 78756, Texas, United States | 9028319 | 78756,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 18 | 78734, Texas, United States | 9028300 | 78734,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 19 | 78757, Texas, United States | 9028320 | 78757,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 20 | 78731, Texas, United States | 9028297 | 78731,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted |
| 21 | **West University, Texas, United States** | **9060226** | West University,Texas,United States | **Neighborhood** | targeted, both campaigns | correctly targeted — **ambiguity flagged, see §2** |
| 22 | 78641, Texas, United States | 9028249 | 78641,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 23 | Leander, Texas, United States | 1026553 | Leander,Texas,United States | City | targeted, both campaigns | correctly targeted — overlap flagged, preserved |
| 24 | 78645, Texas, United States | 9028253 | 78645,Texas,United States | Postal Code | targeted, both campaigns | correctly targeted — overlap flagged, preserved |

**Result: 24 supplied, 24 targeted, 24 exact matches, on both campaigns.**

| Check | Result |
|---|---|
| Missing from the account | **none** |
| Targeted but outside the approved set | **none** |
| Duplicated targets | **none** |
| Negative location criteria | **none** — nothing is blocking a target |
| Location option | **PRESENCE** on both campaigns — correct. `PRESENCE_OR_INTEREST` is not in use on either live campaign. |
| Negative geo target type | PRESENCE on both — correct |
| Language | English (1000) only, both campaigns |
| Whole-DMA, state or radius creep | **none** — no proximity criteria exist on either live campaign |

Validated by `scripts/validate_location_targets.py`:
`PASS | 0 proximity + 19 postal + 5 named = 24 positive | PRESENCE`

### Overlaps: flagged and preserved, exactly as instructed

Five city or neighborhood targets overlap ZIPs on the same approved list — Cedar Park with 78613,
Georgetown with 78628, Leander with 78641 and 78645, and Barton Creek with 78746 and 78733 (Google's
own suggestion service returns those ZIPs for the Barton Creek label). **Nothing is removed.** The
fixed list is preserved. Overlapping targets do not double-charge; Google serves the most specific
matching target.

### Delivery evidence

All 45 `geographic_view` and `user_location_view` rows for the live campaigns over their full life
resolve to **metro 200635 (Austin)** and **region 21176 (Texas)**. Matched location and user location
agree row for row. **No out-of-market delivery was observed.**

Spend concentrates where you would expect: Leander 78641 ($433.06, 15 clicks, 2 conversions),
Cedar Park 78613 ($294.87, 11 clicks), Georgetown 78628 ($139.39, 4 clicks). Everything else is
under $135. **The sample is far too small to prune any location, and no location change is
proposed.**

---

## 2. West University — ambiguity reported, not guessed

Google returns two Texas candidates for the label `West University`:

| Candidate | ID | Type | Canonical name | State |
|---|---|---|---|---|
| A | **9060226** | Neighborhood | West University,Texas,United States | **currently targeted** |
| B | 9053129 | City | West University Place,Texas,United States | **not targeted — a Houston-area city, ZIP 77005. Must not be added.** |

`geo_target_constant.parent_geo_target` was walked for both. Each resolves only to Texas (21176)
and then United States (2840). **Google does not expose a parent city for either**, so the
Austin-versus-Houston question cannot be settled from the Google Ads API.

**Per the handoff instruction, this one target is reported rather than guessed. No geo mutation is
proposed for it.** Two facts reduce the risk while it stays open: the account already targets
candidate A and the approved list matches it, and no Houston-area delivery has occurred.

**Confirm:** is `West University` intended as the Austin neighborhood west of the UT campus? If yes,
9060226 is already correct and nothing changes.

---

## 3. Budget

### Current state, verified

| Campaign | Budget ID | Shared? | Daily | 30.4-day projection |
|---|---|---|---|---|
| Progreen Austin \| Search \| Hardscape Construction | 15742409458 | no | $32.89 | $1,000.06 |
| Progreen Austin \| Search \| Outdoor Living & Design | 15742409461 | no | $32.89 | $1,000.06 |
| **Total, enabled in-scope campaigns** | | | **$65.78** | **$1,999.71** |

Your report of "about $1,000 per campaign" is accurate. Neither budget is shared, so nothing is
double-counted. Ten other budgets exist on paused or removed campaigns totalling $305.66/day; none
can spend while its campaign is paused, and none is touched by this plan.

Against the ceiling: the work order's $65.79 is $2,000 ÷ 30.4 rounded up. The account's actual
$65.78 projects to $1,999.71, one cent per day under. **I recommend keeping $65.78, not raising it
to $65.79** — $65.79 projects to $2,000.02, two cents over the stated $2,000 cap, for no benefit.

### Proposed reallocation — total unchanged

| Campaign | Current | Proposed | Change |
|---|---|---|---|
| Outdoor Living & Design (15742409461) | $32.89 | **$39.47** | +$6.58 (+20%) |
| Hardscape Construction (15742409458) | $32.89 | **$26.31** | −$6.58 (−20%) |
| **Total** | **$65.78** | **$65.78** | **$0.00** |
| **30.4-day projection** | $1,999.71 | **$1,999.71** | unchanged |

### Why not an even split

| Campaign | Cost | Clicks | CPC | Conv | Impr. share | Lost to **budget** | Lost to **rank** | Abs. top |
|---|---|---|---|---|---|---|---|---|
| Outdoor Living & Design | $918.94 | 41 | **$22.41** | **2** | 45.6% | **31.8%** | 22.6% | 23.8% |
| Hardscape Construction | $835.54 | 22 | $37.98 | 1 | 54.7% | 17.7% | **27.7%** | 34.1% |

The two campaigns are limited by different things. Outdoor Living & Design loses **31.8%** of
available impressions to budget — money buys those back. Hardscape Construction loses **27.7%** to
rank, which money cannot buy; only Quality Score and bid competitiveness can. Outdoor Living &
Design also delivers clicks 41% cheaper and produced 2 of the 3 conversions.

**Confidence: medium.** Three conversions is a thin base for a split decision. The impression-share
split is the sturdier signal, and it points the same way. This is a 20% shift, not a wholesale
reallocation, and it is reversible in one field edit.

### After-write budget enforcement

Post-write QA must assert:

1. Sum of `campaign_budget.amount_micros` for all **ENABLED in-scope** campaigns = **65,780,000**
   (`$65.78`), each shared budget counted once.
2. 30.4-day projection = **$1,999.71**, at or below the $2,000 cap.
3. `campaign_budget.explicitly_shared = false` on both, so no double-count.
4. No campaign moved from PAUSED to ENABLED as a side effect.
5. Both campaigns still carry exactly 24 positive location criteria with `positive_geo_target_type
   = PRESENCE`.

---

## 4. Ad schedule — the defect and the fix

### Current state

Both campaigns carry seven `AD_SCHEDULE` criteria, Monday through Sunday, `start_hour 08:00` →
`end_hour 17:00`, bid modifier unset. Fourteen criteria in total.

**The account timezone is `America/New_York`. The market is Austin, `America/Chicago`.** Google
interprets ad schedules in the *account* timezone, so the configured window runs **07:00–16:00
local time**.

Hour-of-day data confirms it exactly, with no ambiguity:

| Account hour (ET) | Local hour (CT) | Cost | Clicks | Conv |
|---|---|---|---|---|
| 8 | 7am | $203.99 | 8 | 0 |
| 9 | 8am | $166.05 | 7 | 1 |
| 10 | 9am | $375.15 | 11 | **2** |
| 11 | 10am | $62.46 | 2 | 0 |
| 12 | 11am | $216.27 | 9 | 0 |
| 13 | 12pm | $156.91 | 6 | 0 |
| 14 | 1pm | $24.27 | 1 | 0 |
| 15 | 2pm | $178.46 | 6 | 0 |
| 16 | 3pm | $370.92 | 13 | 0 |
| **17–23, 0–7** | **4pm–6am** | **$0.00** | **0** | **0** |

Zero delivery outside those nine hours. **The account is dark from 4pm Central every day** — the
entire homeowner evening, for a service homeowners research after work. It also runs an hour
earlier than any plausible intent, at 7am local.

### Recommendation: remove the ad schedule entirely

Three options were considered:

| Option | Effect | Assessment |
|---|---|---|
| Shift +1 hour, to 09:00–18:00 ET = 08:00–17:00 CT | Restores the apparent intent | Still dark after 5pm local. And "8–5" is my inference, not a verified fact. |
| Set a specific evening-inclusive window | Recovers evenings | Requires inventing operating hours. Not permitted. |
| **Remove the schedule** | Campaign eligible all day, every day | **Recommended.** |

Removal is the only change that does not rest on an unverified business fact. Daily budget, not the
schedule, caps spend — so this cannot increase cost. It converts a fixed nine-hour Eastern window
into full availability, letting the budget find demand wherever it is.

**Object count: 14 criteria removed** (7 per campaign). Fully reversible; every day and hour value
is recorded in `01_fresh_account_snapshot.json`.

**Open business question, which does not block this change:** what are Pro Green Austin's real
phone-answering hours? If calls cannot be answered in the evening, the correct control is a schedule
on the **call asset**, not on the campaign — form leads should still be collected around the clock.

### Day of week

| Day | Cost | Clicks | CPC | Conv |
|---|---|---|---|---|
| Monday | $331.30 | 14 | $23.66 | 1 |
| Friday | $305.31 | 10 | $30.53 | 0 |
| Saturday | $272.10 | 9 | $30.23 | 0 |
| Sunday | $236.78 | 9 | $26.31 | 0 |
| Wednesday | $225.06 | 8 | $28.13 | 0 |
| Tuesday | $212.75 | 6 | $35.46 | 1 |
| Thursday | $171.18 | 7 | $24.45 | 1 |

**No day-of-week change is proposed.** Six to 14 clicks per day over 27 days cannot support a bid
modifier. Weekend traffic is not obviously worse than weekday traffic. **Directional only.**

---

## 5. Devices

| Device | Cost | Share | Impressions | Clicks | CPC | Conv | All conv |
|---|---|---|---|---|---|---|---|
| **Mobile** | $1,358.56 | **77.4%** | 1,040 | 45 | $30.19 | 1 | 36 |
| Desktop | $381.52 | 21.7% | 829 | 17 | $22.44 | 1 | 2 |
| Tablet | $14.40 | 0.8% | 30 | 1 | $14.40 | 1 | 1 |

All three device criteria exist on both campaigns with **no bid modifier applied**.

**No device change is proposed.** One conversion each on 45, 17 and 1 clicks is nowhere near enough
to justify a modifier, and excluding a device on a sample this size would be exactly the mistake the
handoff warns against. **Directional only.**

Two observations worth carrying forward:

- Mobile costs 35% more per click than desktop and takes three quarters of the spend. Once
  measurement is repaired this is the first segment to re-examine.
- Nearly all of the junk "all conversions" are mobile (36 of 39). That is the location-extension
  local-action noise, not a mobile quality signal.

### Click type

| Click type | Cost | Clicks | CPC | Conv | All conv |
|---|---|---|---|---|---|
| URL_CLICKS | $1,291.07 | 46 | $28.07 | 2 | 4 |
| **LOCATION_EXPANSION** | $229.01 | 10 | $22.90 | 0 | **34** |
| **SITELINKS** | $153.72 | 4 | **$38.43** | 0 | 0 |
| CALLS | $80.68 | 3 | $26.89 | 1 | 1 |
| GET_DIRECTIONS | $0.00 | 0 | — | 0 | 0 |

Two things fall out of this table:

- **`LOCATION_EXPANSION` produces 34 of the 39 "all conversions" and zero real leads.** That is the
  entire local-actions noise floor, now located precisely.
- **`SITELINKS` cost $153.72 at the highest CPC on the account, $38.43, with zero conversions.**
  Some of that goes to the Dallas and Houston account-level sitelinks, which recorded 63 and 57
  attributed impressions and zero conversions. The exact split cannot be isolated: Google's
  asset-level report attributes each ad's whole cost to every asset that served with it, which is
  why campaign-level sitelinks in that report sum to $2,933.64 against $1,754.48 of actual campaign
  spend. The click-type figure is the reliable one.

---

## 6. Demographics and audiences

| Setting | State |
|---|---|
| Age, gender, income criteria | **none** on either live campaign |
| Audience targeting | `targeting_setting.target_restrictions = [{AUDIENCE, bid_only: true}]` — observation mode, correct |
| Audience or user-list criteria on live campaigns | **none attached** |
| `USER_INTEREST` criteria | 140 exist, all on **paused** campaigns |
| `USER_LIST` criteria | 8 exist, all on **paused** campaigns |
| `IP_BLOCK` | 2 negatives per live campaign, from the ClickCease integration |
| Brand list | `Exclusion Brand List` (11676362245, 27 members) exists but is **linked to nothing**. Low impact while AI Max and broad match are off. |

**No demographic or audience change is proposed.** There is no data to justify one, and Green
Marketing policy forbids excluding a demographic on a zero-conversion sample this small.

---

## 7. Everything checked and found correct

| Setting | State | Policy |
|---|---|---|
| Search Partners | off, both campaigns | matches default |
| Display Network | off, both campaigns | matches default |
| YouTube | off | matches default |
| AI Max (`ai_max_setting.enable_ai_max`) | **false**, both | matches default |
| Broad match expansion (`keyword_match_type`) | UNSPECIFIED — not enabled | matches default |
| Dynamic Search Ads | no DSA domain configured | matches default |
| Automatically created assets (campaign level) | `TEXT_ASSET_AUTOMATION` **OPTED_OUT**, `FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION` **OPTED_OUT** | matches default |
| Final URL expansion | opted out | matches default |
| Auto-applied recommendations | **no subscriptions** | nothing applied automatically |
| Portfolio bidding strategies | none | n/a |
| Experiments | none; `experiment_type = BASE` | n/a |
| Campaign end dates | none set | n/a |

**One exception to flag:** campaign-level asset automation is correctly off, but the three
**account-level** automatically created assets — the Dallas, Houston and Austin sitelinks and the
"Over 20 Years Of Experience" snippet — are a separate control and are **still serving**. The
campaign opt-out does not remove them. That is `EXR-001` and `EXR-002` in the change plan.

Google's pending recommendations are `SEARCH_PARTNERS_OPT_IN` and `MAXIMIZE_CONVERSIONS_OPT_IN` on
both campaigns. **Neither is applied and neither should be.** Search Partners is off by Green
Marketing policy, and Maximize Conversions is premature until measurement is repaired.
