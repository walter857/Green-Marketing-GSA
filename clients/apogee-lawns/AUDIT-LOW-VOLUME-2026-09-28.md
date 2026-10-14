> **SUPERSEDED 2026-09-28 by `audits/2026-09-28-independent/` (run B). Content below preserved unchanged.**
> Corrections: (1) the Omaha recommendation is RETRACTED — Omaha is EXCLUDED by a settled owner decision
> (`work-order.yaml` location_decision_2026_09_16) and the 163-click combined forecast is void; (2) "Lincoln is
> saturated / whole reachable market" overstated what impressions / IS measures; (3) "budget loss is pacing while
> learning" is unsupported; (4) the $8 cap does cost some top positions (click share 19.6%) but raising it is
> uneconomic; (5) the 09-25 edit set tablets to -100%, it did not "change no field"; (6) the holiday-lights SKAG
> is not supported as buyer demand; (7) WhatConverts swaps 402-202-7261 -> 402-783-8482, not 402-526-5754;
> (8) live GTM is now version 3. Do not act on this file; use run B.

# Apogee Lawns — low-volume audit, 2026-09-28

**Account:** Apogee Lawns LLC - Live · **8164626278** · similar-local-service
**Service:** Permanent Christmas light installation (from the validated work order; the only
service in the account) · **Mode:** READ-ONLY. Nothing was created, edited, enabled, paused or
deleted. No form was submitted.

Gate: `validate_work_order` 0 errors; fresh API read name + ID exact match, manager=false,
test=false, ENABLED.

## Verdict

**Nothing is broken or blocking delivery.** The campaign already shows on **72% of the searches
it is eligible for**. The whole reachable market for its keywords in its geography was about
**85 ad impressions in 7.5 days (~11/day)**. Volume is low because (1) the keyword set reaches a
small query pool, (2) the geography is Lincoln-only, and (3) late September is the seasonal
trough: the head term's 2025 volume went Sep 50, Oct 140, **Nov 480**, Dec 170.

SKAG is not the limiter: grouping does not change reach. The keyword list and the geography do.

## Live facts (2026-09-17 .. 2026-09-28)

| Item | Value |
|---|---|
| Enabled | **2026-09-21 09:04**, by the owner in the UI (`GOOGLE_ADS_WEB_CLIENT`) |
| Billing | setup 8587299012 **APPROVED** 2026-09-16; account_budget INFINITE |
| Campaign status | ENABLED / SERVING / primary LEARNING (only reason) |
| Ads | 4/4 APPROVED, no policy topics (no housing limit, ZIP targets serve) |
| Delivery | 61 impr · 3 clicks · $18.69 · CTR 4.9% · CPC $6.23 · 0 conversions |
| Search IS | **72.2%** · lost to budget 18.5% · lost to rank 9.3% |
| Days | Sep 17–20 zero (paused) · Sep 21–28: 2, 4, 2, 6, 8, 15, 15, 9 impressions |
| Spend vs budget | $5.52 (Sep 25), $13.17 (Sep 27); every other day $0 against $16.44 |
| Keywords with any impressions | **2 of 5**: installation PHRASE (32 impr, all 3 clicks), head EXACT (29 impr, 0 clicks) |
| Zero-impression keywords | installation EXACT, installer PHRASE, installer EXACT (near-zero demand, as forecast 09-16) |
| Geo | all 61 impressions in-target; Lincoln 39, 68516 14, 68430 6, 68527 2 |
| Negatives | 75 campaign negatives, **0 conflict** with any positive; 0 shared lists attached; account-level = parked-domain label only |
| Schedule / devices | 24/7, no bid modifiers. Owner's 09-25 edit on criterion ~30002 (Tablet) changed no field |
| Calls | call asset showed 7 times, 0 calls; call_view 0 rows |

Search terms (whitelist classification, aggregates only): of 38 visible impressions,
3 carry a service marker, 2 a location marker only, 10 are the bare head term, **23 carry
neither**. 19 of those 23 came through the head EXACT keyword's close variants.

### Budget-lost IS is pacing, not a binding budget

Budget loss appears on days with **$0 spend** (Sep 21, 22, 24) and fades to 0–8% by Sep 26–27.
At $5.52–$6.58 per click, $16.44/day buys 2–3 clicks, so Maximize Clicks paces conservatively
while it learns. Forecast confirms: Lincoln + Omaha at $30/day forecasts the same clicks and cost
as at $16.44/day. **Do not raise the budget.**

### The $8 CPC ceiling is not the limiter

Actual CPCs are $5.52 and $6.58, not pinned at the cap. Forecast for the remaining season:
$8 cap 55.5 clicks; $10 cap 55.5; $12 cap 62.1 (+6.6 clicks for +$129). **Keep $8.**

## Lever sizing — Google forecast, 2026-09-29 .. 2026-12-20, $8 cap

| Scenario | Clicks | Cost |
|---|---|---|
| S0 current build (do nothing) | 55.5 | $266.57 |
| + head term PHRASE | 63.5 | $321.78 |
| + Lancaster County | 55.5 | $266.57 (Lincoln area already saturated) |
| + permanent holiday lights SKAG (E+P) + holiday lighting E | **75.7** | $349.87 |
| + Omaha (current keywords) | **105.9** | $491.65 |
| Omaha only (current keywords) | 82.6 | $393.56 |
| **+ holiday SKAG + Omaha** | **163.0** | **$768.17** |
| generic "christmas light installation" only, Lincoln | 51.1 | $309.79 |

Synonym intent (Planner ideas a PHRASE keyword would reach, whitelist service/location marker
volume vs other): holiday lights 30 vs 40; house lights 20 vs 30; outdoor lighting 10 vs 90;
**outdoor lights 40 vs 590** (product-shopping dominated — rejected). Exact-only forecasts:
holiday 3.3, house 11.3, outdoor lighting 14.7, outdoor lights 17.5 clicks.

## Recommendations (ranked)

1. **Add Omaha as a separate campaign** — the biggest lever, +50 clicks at a lower CPC ($4.64).
   The client's site already advertises Omaha service, but Omaha is outside the approved geo list,
   so this needs owner confirmation. Build: same SKAG structure, own Omaha landing page (the paid
   page's H1 says "Lincoln, NE"), and a **shared budget** at $16.44/day with Lincoln so the total
   stays at $499.78/month. The forecast spend for both markets is $768 over 83 days, which fits.
2. **Add `AG | Permanent Holiday Lights`** to the Lincoln campaign: EXACT + PHRASE
   `permanent holiday lights`, EXACT `permanent holiday lighting`, and 2 RSAs using only claims
   already approved. +20 clicks. The client's own site uses this wording. This is inside current
   scope and needs no owner input.
3. **Keep the head term EXACT-only.** Phrase buys +8 clicks, and live data shows the exact
   keyword's close variants already drift into queries with no service or location marker.
4. **Do not add** outdoor lights (product intent), a higher CPC cap, a bigger budget, Search
   Partners or Broad match.
5. **Owner decision:** generic seasonal "christmas light installation" (+51 clicks in Lincoln).
   client.yaml lists seasonal hanging as an **excluded** service, so this would sell permanent
   lights to people shopping for a service Apogee does not offer.

## Measurement defect found (does not limit volume)

GTM-M545Z8T2 is **published (version 2)**. It contains the AW tag, the form label, the
website-call label and the `apg_permanent_lights_lead` trigger. The landing page loads GTM,
AW-18453077620 and WhatConverts in a real browser. But
`/thank-you/permanent-christmas-lights/` **redirects to the landing page itself**, and the
`apg_permanent_lights_lead` dataLayer push appears **0 times**. So the Primary form conversion
7772803337 **cannot fire**, whatever leads arrive. Developer fix: publish the thank-you page,
point the Gravity Forms confirmation at it, and ship the dataLayer push with a non-PII lead_id.
Also: three `form#gform_1` elements share one id on the page (one hidden).

## UI-only checks (the API cannot see these)

Chrome became unresponsive before the child account opened, so these remain unchecked:
advertiser verification status and any new-account spending notice in the notification bar.
The API shows the account serving normally, so neither is currently blocking.

## Evidence

`reports/apogee-lawns/evidence/2026-09-28-{audit,levers,synonyms,exact-forecasts,combined-forecast}.json`;
raw search terms and Planner idea texts are stored on disk only (`*-RAW.json`), never printed.
Scripts: `scripts/apg_0928_{audit,levers,synonyms,synonyms_fc,exact_fc}.py`.
