# 01 — Current state and evidence reconciliation (run C, 2026-09-28)

**Apogee Lawns LLC - Live · 8164626278 · Permanent Christmas light installation.**
- **Work order:** `work-orders/work-order-measurement-repair-handoff-2026-09-28.yaml` →
  `Work order: PASS | Apogee Lawns LLC - Live | 8164626278 | similar-local-service | Permanent Christmas light installation`
  (exit 0; schema 0 errors). The canonical `work-order.yaml` also passes (exit 0) and was not edited.
- **Scope approval:** reused (Walter, 2026-09-16).
- **Identity:** fresh read-only gate **PASS** (not manager, not test, America/Chicago).
- **Landing-page workflow:** `LANDING_PAGE_CONTENT_WORKFLOW.md` was read in full this session before any page inspection
  or handoff; the harness confirmed the file is unchanged.

## Fresh observations (≈16:15–16:25 CDT; the 2026-09-28 figures are a partial day)

| Item | Now | Versus audit |
|---|---|---|
| Campaign 24257151015 | ENABLED / SERVING / LEARNING; TARGET_SPEND $8.00 cap; $16.44/day, not shared; Search only | unchanged |
| Completed days 09-21..09-27 | 52 impr, 3 clicks, $18.69, IS 72.2%, lost budget 18.5%, lost rank 9.3%, click share 19.6%, 0 conv, 0 all-conv | unchanged |
| 2026-09-28 (partial) | 17 impr, 0 clicks, $0 | new |
| Conversions | 7772803337 form Primary; 7773013199 ads call Primary; 7773043879 website call Secondary; all 0 all-conversions since 09-16 | unchanged |
| Tablet | campaign and both ad groups explicit 0.0 | unchanged |
| GTM | live v3, byte-identical to the audit's copy; workspace 5, 0 pending | unchanged |
| Site | no `/thank-you/permanent-christmas-lights/`; 4 published pages; 3 drafting notes on the LP | the audit said **2** notes; there are **3** |
| WhatConverts | 402-526-5754 = WhatConverts number "GSA Traffic", static, never used; pool "Website Traffic" 402-783-8482 swaps 402-202-7261; GF1 tracked | new configuration evidence |

## Unresolved change-history entries — re-checked

`change_event` for 09-24..09-28 still returns only the 09-25 tablet row, and its payload is empty. The
`change_status` rows below still have **no** corresponding `change_event`, so **no before/after values are available**.
Every field read on those resources still matches the 09-17 intended configuration. That is not proof that nothing
changed.

| When (CT) | Resource | change_status | change_event |
|---|---|---|---|
| 2026-09-25 08:26:21 | campaign criterion ~30002 (tablet) | CHANGED | 1 row, empty payload (web client) |
| 2026-09-28 02:33:58 | budget 15884926233 | CHANGED | none |
| 2026-09-28 11:47:23 | campaign 24257151015 + ad groups 200347713516, 200347713556 | CHANGED | none |

## Form-mismatch evidence, by type

| Conclusion | Evidence type |
|---|---|
| The dedicated thank-you page does not exist | **page inventory** (WordPress REST) + request probe |
| That URL lands on the LP via WordPress's closest-slug redirect | **rendered behaviour** (fetch probes: a random slug 404s; a prefix redirects) |
| The trigger requires that path + event + `lead_id` | **configuration** (published container + workspace) |
| Nothing pushes the event | **source inspection** (LP, `/thank-you/`, inline, 28 scripts) |
| Real visits reach generic `/thank-you/` | **platform report** (GTM tag coverage) |
| Form 1 confirms to `/thank-you/` | **INFERRED only**; confirmation settings not visible |
| The full submission path fails | **not tested**; no submission authorized. Failure is established by configuration and inventory |

## Corrections to the independent audit

1. **"0 WhatConverts leads carry a GCLID"** is withdrawn. The API lead schema has **no click-ID field**; the earlier check
   read a key that does not exist. What is established: the two web-form leads' recorded landing URL is
   `offer.apogeelawns.com/` with no query string (no click ID or UTM present there). Whether they were tests is
   **unconfirmed**. Missing click IDs on two direct leads does not show ad-click attribution is broken in general.
2. **Drafting notes: 3, not 2.** The third reads "Exact installation timing and handoff process require client
   confirmation."
3. **402-526-5754 ownership** moves from unverified to **verified WhatConverts number** (static, "GSA Traffic", never
   used). Its forwarding route remains unverified (call flow "Apogee Lawns - ICF").
4. **EverLights claim** moves from "confirm with client" to **supported by current first-party site text**, which meets
   the `agency.yaml` minimum `verified_client_or_first_party`. Only the internal note sentence must go.
5. **Tablet plan:** the "1 + 2 conditional" payload was ambiguous. It is now evaluated as 3 required updates and placed on
   HOLD pending owner intent. Fingerprint 46060B03F5C9 is void.

## Economics check

| Item | Source | Status |
|---|---|---|
| Target CPL $100 (acceptable $90–125), **raw lead** | owner input 2026-09-16 (`economics_2026_09_16`) | planning target, not observed |
| Click-to-lead 5%, lead-to-sale 20% | same record, labelled `PLANNING_ASSUMPTIONS_NOT_HISTORICAL_PERFORMANCE` ("Green Marketing launch benchmarks") | **assumptions**, not Apogee evidence |
| "≈$5 affordable CPC" | $100 × 5% | **derived from an assumption**; not observed |
| CPQL target, qualification definition | `target_cpql: null`; CRM stages blank | **missing** |
| Gross profit per sold installation | `average_gross_profit_per_sold_project: null` | **missing** |

- Seasonality is one year of Planner history, not a promised increase. Forecast clicks are not leads.
- The "$300 spent with no qualified lead" rule is a proposed review trigger. It may only count spend from a period where
  form **and** call capture are verified and "qualified" is defined. **No such period exists yet**, so the rule is not
  evaluable today.

## Recommendation on delivery during repair

**Keep delivery exactly as it is** (no pause, no bid, budget, geo or keyword change).

- Maximize Clicks does not use conversion data, so the broken form tag does not steer delivery.
- Spend is small: $18.69 across completed days.
- WhatConverts captures both the paid form (GF1) and calls to 402-526-5754 ("GSA Traffic"), so real leads are recorded
  even while Google Ads cannot count forms.

**Risks:** no Google Ads CPL; any switch to conversion-based bidding now would optimize on calls only, so do not switch.

**Reassess when either happens:**
- the developer repair is not live and QA-passed by **2026-10-15**; or
- a paid lead reaches Apogee without appearing in WhatConverts.


---

## Dated corrections and updates — 2026-09-28 (run D)

1. **Call capture wording corrected** (see 05, run-D revision). Run C's "WhatConverts is recording … calls to
   402-526-5754" overstated it. The number is configured in WhatConverts and assigned to flow "Apogee Lawns - ICF"; routing,
   recording and attribution remain untested.
2. **Tablets:** the owner confirmed a deliberate exclusion (landing pages not tablet optimized). Closed; see 06 and 09.
3. **Qualified lead defined by the owner:** asks for the service on the form or the call. The "$300 without a qualified
   lead" review rule becomes definable, but it still needs a period with verified capture.
4. **Customer-supplied lights:** the owner says yes. Two labor-only negatives become removal candidates; `customer
   supplied` stays (11).
5. **Fresh read-only checks at ≈21:35 CDT:** identity PASS; campaign ENABLED ($8 cap, $16.44); tablets excluded;
   negatives 75; conversion actions unchanged.
6. **Delivery recommendation unchanged:** keep the campaign as is while the website repair is built; reassess on
   2026-10-15.
