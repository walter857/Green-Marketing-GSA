# Apogee Lawns — independent low-volume audit, 2026-09-28 (run B)

**Apogee Lawns LLC - Live · 8164626278 · Permanent Christmas light installation** · campaign 24257151015.
READ for connected systems, DRAFT for local files. **External mutations executed: 0.** This package supersedes
`../../AUDIT-LOW-VOLUME-2026-09-28.md` (run A), which is preserved and corrected in `02`.

## Verdict

- **Campaign design: fundamentally appropriate, deliberately narrow.** One installation-intent ad group (Phrase + Exact)
  and one head-term ad group (Exact only), all pointing at one Lincoln page. For verified buyer intent, the evidence does
  not show the design is too restrictive.
- **Execution: sound, with one unexplained restriction.** Tablets have been excluded (−100%) since a 09-25 web-interface
  edit.
- **Measurement: broken for forms, unverified for calls.** Measurement is the most urgent defect. It is not the cause of
  the low volume.
- **Run A: partly unsupported.** Its Omaha recommendation broke a settled owner decision, and its saturation,
  budget-learning and CPC-cap claims overreached (see `02`).

## Diagnosis (evidence · counterevidence · confidence)

| Rank | Cause | Evidence | Counterevidence / limits | Confidence |
|---|---|---|---|---|
| 1 | **Small niche demand in a Lincoln-sized market** (volume) | Planner head bucket avg 90/mo in the approved area; installer rows ≈10/mo; eligible impressions for the current keywords ≈ 72 in the 7 serving days (52 ÷ 72.2% IS) | Planner buckets are rounded, cover 10 of 14 geos and one season; IS denominators are Google's estimate and cover only the current keywords and targeting | High that paid demand is small; moderate on magnitude |
| 2 | **Seasonal trough** (volume, temporary) | Same geography and family: Sep 50 → Oct 140 → Nov 480 → Dec 170 (2025) | One year of history | Moderate–high |
| 3 | **Position / Ad Rank at an $8 cap** (clicks, not impressions) | Rank-lost top IS 18.5%; absolute-top share 16.7%; **click share 19.6%** (3 clicks vs ≈15 estimated eligible); rank-lost IS 9.3% | Forecasts: a $10 cap adds 0 clicks; $12 adds 6.6 at ≈$19.55 each, far above the ≈$5 affordable CPC implied by the owner's planning numbers | Moderate that it costs some clicks; high that raising it is uneconomic |
| 4 | **Budget-lost IS 18.5%** (unexplained) | Appears on $0-spend days (09-21 60%, 09-22 40%, 09-24 33%) and fades to 0–8% by 09-26/27 | Spend never reached the budget (max $13.17 of $16.44); forecasts at $10 or $25 a day are identical to $16.44 | Low on mechanism (pacing, a new-account limit or estimate noise); moderate that it is not a hard cap; ≈13 lost impressions ≈ <1 click |
| 5 | **Tablet exclusion** (eligibility) | −100% explicit since the 09-25 web edit; tablets were 1 of 20 impressions before it | Small share | High that it exists; low impact |
| — | Keyword coverage | Buyer/local variants forecast 1.2 clicks alone; holiday-installation synonyms ≈0; EverLights 0 | Meaning-based matching not modelled | Moderate |
| — | Negatives | 0 buyer modifiers and 0 reachable Planner ideas blocked; 0 shared lists attached | Blocked queries are invisible in reports | Moderate–high: **not a cause** |
| — | Geography | 14 targets exactly as approved; Lincoln city carries most demand; Omaha is excluded by a settled decision | — | High: **not a defect** |
| — | Ad relevance / landing page | Ads approved, QS 6 on the head term; LP renders cleanly on desktop and 390 px with a sticky CTA | 3 clicks cannot measure conversion rate; **two internal drafting notes are published on the LP** | Low evidence either way |
| M1 | **Form conversion cannot fire** (measurement) | No page at the trigger's only path; WordPress redirects it to the LP; `apg_permanent_lights_lead` pushed nowhere; generic `/thank-you/` gets traffic | Not end-to-end tested (no submission authorized) | High (static) |
| M2 | Call measurement untested | Calls-from-ads and website-call tags configured and published; 0 calls; no ad-visitor test possible | — | — |

## One recommended strategy

- **Preserve:** the structure, Exact-only head term, $8 cap, $16.44 a day ($499.78 per 30.4 days), Search-only,
  Presence, the 75 negatives, the four RSAs, the call asset and its schedule, the 402-526-5754 decision, and Omaha
  excluded.
- **Repair first:** the form conversion contract (developer D1–D4, then GTM regex hardening); the LP drafting notes (D7);
  cache and click-ID capture (D2, D6); and the tablet exclusion (`APG-0928-DEV-T`, approval required).
- **Add:** nothing today. The head-term Phrase test (`APG-0928-KW-P`) is drafted and gated on verified measurement and
  on 2026-10-15 or later.
- **Avoid:** raising the cap or budget, holiday or outdoor-lights keywords, Broad, Search Partners, AI Max, PMax, Omaha.
- **Defer:** promoting website calls to Primary until one real call is observed; negative hygiene until owner facts or
  search terms justify it; LSA (WhatConverts shows LSA-tagged leads, a separate workflow).
- **Spend:** continue temporarily. Maximize Clicks does not bid on conversions, spend is about $3 a day, and WhatConverts
  captures the form. Do not switch to a conversion-based strategy until M1 is verified.

## Direct answers

- **Are the negatives suppressing buyer demand?** No measurable suppression (`03`).
- **Is the keyword set too narrow?** Not for verified buyer intent. Only ambiguous Phrase reach adds material volume (`04`).
- **Does the CPC cap materially matter?** It costs some top positions and clicks, but raising it is uneconomic (`04`).
- **Is geography limiting us?** Only in the sense that Omaha is excluded, and that is a settled business decision, not a
  defect.
- **What is seasonal versus structural?** September is the trough (seasonal). A niche service in a Lincoln-sized market is
  structural.
- **Does form measurement actually work?** No. It cannot fire as built (`05`).
- **Who owns website-call attribution?** Google's Calls from Website tag owns paid attribution; WhatConverts records and
  qualifies calls without re-uploading them (`05`).
- **Is Omaha justified and authorized?** Not authorized, and not reopened (`06` brief).
- **What is the best next action within $500 a month?** Ship the developer form fix, then run the approved Preview test.
  Separately, decide `APG-0928-DEV-T`. The budget is untouched.

## Files

`01` ledger + snapshot · `02` timeline + review of run A · `03` negatives + search terms · `04` keywords + forecasts ·
`05` tracking findings, developer handoff, test matrix · `06` Lincoln draft + Omaha brief · `07` manifest + QA.
Plan: `../../plans/APG-0928-DEV-T.yaml`. Work order: `../../work-orders/work-order-low-volume-audit-2026-09-28.yaml`.
