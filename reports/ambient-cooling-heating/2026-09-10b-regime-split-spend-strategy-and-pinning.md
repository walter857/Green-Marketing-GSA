# Ambient Cooling - Live (2401959466) - 2026-09-10 session B

**Account:** Ambient Cooling - Live · child customer ID **2401959466** · manager 3373711342
**Vertical:** heating-cooling · **Services:** AC Repair, HVAC Repair, HVAC Installation,
HVAC Replacement, Gas Boiler Repair
**Identity gate:** PASS on every query in this run (name, ID, non-manager, non-test,
America/New_York, USD, both manager links ACTIVE).

**Google Ads mutations executed this session: 3.** Two budget operations
(`AMB-0910-BUD-2 93541FBB5D7F`) and one account-level negative removal
(`AMB-0909C-NEG-COMMERCIAL 9F88FEE76803`). Both read back with 0 failures. Everything
below this line is read-only analysis, drafts, and validate-only checks.

---

## 1. The finding that reframes the whole account

**The five campaigns ran on UNCAPPED Maximize Clicks until 2026-09-04 16:56.**

`change_event` is unambiguous. Three campaigns received a max-CPC ceiling within 31
seconds of each other, each from an **empty** `old_resource`:

| When (America/New_York) | Campaign | Field | Old | New |
|---|---|---|---|---|
| 2026-09-04 16:56:20 | AC Repair | `target_spend.cpc_bid_ceiling_micros` | *(unset)* | 25000000 |
| 2026-09-04 16:56:34 | HVAC Repair | `target_spend.cpc_bid_ceiling_micros` | *(unset)* | 25000000 |
| 2026-09-04 16:56:51 | HVAC Installation | `target_spend.cpc_bid_ceiling_micros` | *(unset)* | 30000000 |

`client_type = GOOGLE_ADS_WEB_CLIENT`, `user_email = access@greenmarketingfl.com`.
Per the standing rule, `client_type` identifies the **interface**, not the person; the web
client plus that shared email does not establish who was at the keyboard.

Nothing else in the 30-day change window touched a bid field. **Gas Boiler Repair and
HVAC Replacement were missed and are still uncapped today.**

### Why this matters more than anything else in the audit

Every performance number produced in the three prior sessions averaged across that
boundary. Split at it, the account looks like two different accounts:

| Regime | Window | Days | Spend | Valid clicks | **$/valid click** | Invalid rate | Spend/day | Implied monthly |
|---|---|---|---|---|---|---|---|---|
| **UNCAPPED** | 08-14 → 09-03 | 21 | $8,025.18 | 172 | **$46.66** | 91.0% | $382.15 | $11,617.40 |
| *mixed day* | 09-04 | 1 | $33.40 | 1 | $33.40 | 97.0% | $33.40 | — |
| **CAPPED** | 09-05 → 09-09 | 5 | $103.71 | 4 | **$25.93** | 80.0% | $20.74 | $630.56 |

Per campaign in the uncapped regime: AC Repair **$108.98** per valid click, HVAC Repair
**$70.62**, HVAC Installation $26.02, HVAC Replacement $30.50. Under uncapped Maximize
Clicks the bidding did exactly what uncapped Maximize Clicks does — it paid whatever the
auction asked. On 2026-08-28, AC Repair spent $267.96 and Google kept **one** click.

Daily spend on the flood days sat at 1.9x–2.7x the daily budget cap.

**Correction to prior sessions.** The `$106.37` average CPC I would otherwise have flagged
as a billing contradiction against a `$25.00` ceiling is not a contradiction at all — the
ceiling did not exist for 21 of the 27 days measured. The arithmetic reconciles cleanly
once the regime split is applied.

**What the capped window does and does not prove.** Cost per valid click fell 44.4% and
daily spend fell 94.6%. That is *directionally consistent* with the ceiling binding. It is
**5 settled days and 4 valid clicks.** It is nowhere near enough to call the effect
established, and no lead-volume conclusion can be drawn from it at all.

---

## 2. Invalid clicks: 91% of raw volume, and it has one shape

Account-wide, 2026-08-11 → 2026-09-09: **177 valid clicks, 1,779 invalid, 91.0% invalid.**

Monthly trend from `customer`:

| Month | Valid | Invalid | Invalid rate | Cost | $/valid click |
|---|---|---|---|---|---|
| 2026-06 | 4,250 | 1,105 | 20.6% | $6,610.16 | $1.56 |
| 2026-07 | 3 | 0 | 0.0% | $96.96 | $32.32 |
| 2026-08 | 155 | 1,644 | **91.4%** | $6,842.80 | $44.15 |
| 2026-09 MTD | 22 | 135 | 86.0% | $1,319.49 | $59.98 |

`click_view` carries the raw click population. For AC Repair it returned **962 rows**
against `metrics.clicks` 29 and `metrics.invalid_clicks` 941 — matching valid+invalid
exactly on 18 of 21 days. That corroborates `invalid_clicks` as a real count rather than a
reporting artefact.

### The signature

| Click type | Raw | Kept | Discarded | Discard % |
|---|---|---|---|---|
| **LOCATION_EXPANSION** | 1,741 | 36 | **1,705** | **97.9%** |
| URL_CLICKS | 158 | 99 | 59 | 37.3% |
| SITELINKS | 26 | 26 | 0 | 0.0% |
| CALLS | 11 | 10 | 1 | 9.1% |
| GET_DIRECTIONS | 6 | 6 | 0 | 0.0% |

By device: MOBILE 1,865 raw / 127 kept (93.2% discarded); DESKTOP 77 raw / 50 kept (35.1%).

The flood is almost purely **LOCATION_EXPANSION on mobile** — 912 raw clicks on AC Repair
alone, 99.7% discarded.

### Source, and why the obvious action is the wrong one

There is **no** LOCATION asset on the five campaigns (`campaign_asset` field types are
STRUCTURED_SNIPPET, SITELINK, CALLOUT, BUSINESS_NAME, CALL, BUSINESS_LOGO) and no
`campaign_asset_set` link. It comes from account level: asset set **8620443109**,
type `LOCATION_SYNC`, name "Business Profile", ENABLED, linked via `customer_asset_set`.
`customer.location_asset_auto_migration_done = true`. Two older LOCATION_SYNC sets
(7135012864, 7744462455) are REMOVED.

**Do not remove it.** The clicks Google *kept* are among the account's best:

| Click type | Kept clicks | Cost | % of spend | Primary conv. records | % of records | Cost / record |
|---|---|---|---|---|---|---|
| URL_CLICKS | 99 | $4,039.03 | 49.5% | 5.0 | 38.5% | $807.81 |
| **LOCATION_EXPANSION** | 36 | $2,062.07 | 25.3% | 4.0 | **30.8%** | **$515.52** |
| SITELINKS | 26 | $1,284.80 | 15.7% | 1.0 | 7.7% | $1,284.80 |
| CALLS | 10 | $576.51 | 7.1% | 3.0 | 23.1% | $192.17 |
| GET_DIRECTIONS | 6 | $199.88 | 2.4% | 0.0 | 0.0% | — |

Location-expansion clicks are 25.3% of spend but 30.8% of primary conversion records, at a
lower cost per record than URL clicks. Killing the location asset set to stop the invalid
flood would remove Google's second-most-productive click type across all campaigns in the
account. **No recommendation to touch it.**

**What the invalid clicks do and do not cost.** Google filters invalid clicks out of both
`metrics.clicks` and `metrics.cost_micros`. These 1,779 clicks are not a direct charge.
They are a signal that roughly 91% of the raw click volume reaching these ads is non-human,
and they are worth raising with Google support and with ClickCease (manager 2815082755,
ACTIVE) — but this audit has no billing-level evidence and makes no overcharge claim.

---

## 3. WhatConverts is reachable — and the answer is uncomfortable

Credentials work. `/profiles` returns 400 `Invalid account ID.`; `/leads?profile_id=105803`
returns **200 with 99 leads** for 2026-08-14 → 2026-09-10. Token and secret are never
printed, logged, or written; every URL and error body is redacted before display.

**8 of 99 leads carry a GCLID.** Lead sources:

```
GBP Traffic 34 · 2nd GBP Traffic 31 · google 21 · GBP 4 · LSA - Ellicott 3
GBP - Ellicott 2 · LSA Annapolis 1 · LSA Severn 1 · GLE Traffic 1 · site 1
```

**91 of 99 leads arrive through Google Business Profile, Local Services Ads and organic,
at zero paid-search cost.** Paid search bought 8 of them.

Joining GCLID → campaign through `click_view`, and applying the qualified-lead definition
(unique person, supported service, call at least 60s or valid form, not an existing
customer / employment / parts / DIY / warranty / spam / vendor / wrong-company):

| Campaign | Cost 08-14→09-09 | Conv. records | **Unique qualified leads** | **CPQL** | Limit | Over |
|---|---|---|---|---|---|---|
| AC Repair | $3,084.87 | 5 | 3 | **$1,028.29** | $150 | 6.9x |
| HVAC Repair | $1,951.94 | 6 | 1 | **$1,951.94** | $250 | 7.8x |
| HVAC Installation | $2,972.96 | 3 | 1 | **$2,972.96** | $280 | 10.6x |
| HVAC Replacement | $152.52 | 0 | 0 | — | $280 | — |
| Gas Boiler Repair | $0.00 | 0 | 0 | — | $250 | — |
| **Total** | **$8,162.29** | 14 | **5** | **$1,632.46** | — | — |

**All five unique qualified leads came from clicks bought in the uncapped regime.** The
capped regime has produced zero — on 4 valid clicks in 5 days, which is not evidence of
anything.

**These CPQLs measure a bidding configuration that no longer exists.** They are the correct
verdict on uncapped Maximize Clicks. They are not a verdict on the account as configured
today, and no capped-regime CPQL has been measured yet.

---

## 4. AMB-0909C-CPC-INST-2 5D57E0EF3B70 → **REJECTED**

Status changed from BLOCKED to **REJECTED**. Recorded at
`clients/ambient-cooling-heating/plans/AMB-0909C-CPC-INST-2.REJECTED.json`. Fingerprint
recomputed from the untouched `operations` block and verified as `5D57E0EF3B70`.
**0 operations were performed.**

**Gate:** at least 2 of the 3 HVAC Installation Primary conversion records dated 2026-09-01
had to be proven unique qualified leads.
**Result:** FAILED. Two WhatConverts leads resolve to HVAC Installation — one Web Form from
a 2026-09-01 click that qualifies, one Phone Call from a 2026-08-21 click that does not meet
the 60-second rule. **1, not 2.** Measured CPQL $2,972.96 against a $280 limit.

**Second, independent reason.** The package wanted to raise a $30 ceiling from economics
measured on clicks bought when **no ceiling existed**. The $50.00–$62.13 converting clicks
of 2026-09-01 that formed its entire rationale were uncapped-regime clicks. Raising $30 to
$65 moves back toward the regime that produced $46.66 per valid click. The package's own
evidence argues against it.

**What would reopen it:** at least 14 settled days and at least 40 valid clicks under the
live $30 ceiling, joined GCLID-to-lead, showing CPQL at or below $280 *and* impression share
still losing materially to rank rather than budget.

---

## 5. "Spend the full $13k, but with good revenue"

Taking the priority order as stated — (1) never exceed $13,000/month, (2) protect qualified
lead economics, (3) grow unique qualified lead volume, (4) improve relevance, (5) **spend
utilization is subordinate to all four** — here is the measured answer.

### $13,000 is not spendable on the current keyword set at the current ceilings

There are **12 live positive keywords, 5 distinct texts**, across all five campaigns.

- Observed 5,671 impressions in 27 days ≈ **6,385/month**
- Average Search impression share across the five: **45.2%**
- Implied total available impressions at 100% IS: **~14,127/month**
- At the observed 3.12% CTR: **~441 clicks/month**
- At the **capped** $25.93 per valid click: **~$11,435/month — and that assumes 100%
  impression share, which is unattainable.**

At a realistic 60% impression share the ceiling is roughly **$6,900/month**. The account is
currently running at **$20.74/day ≈ $631/month**.

So there are only three ways to reach $13,000, and two of them are bad:

1. **Raise the CPC ceilings back toward uncapped.** This is the only way to spend $13,000 on
   today's five keywords. It is precisely what produced a $1,632 blended CPQL against
   $150–$280 limits. **Not recommended.** It sacrifices priorities 1 and 2 to satisfy
   priority 5.
2. **Widen the keyword set.** Five distinct BOFU texts is a very narrow base for a $13,000
   budget. Furnace repair, heat pump repair/installation, AC installation, mini-split, and
   water heater are the obvious untested BOFU themes. This raises the ceiling honestly.
3. **Put budget where the leads already are.** 91 of 99 leads came from GBP and LSA. Agency
   policy is to consider Local Services Ads first where the service and location are
   eligible. LSA is pay-per-lead with its own cap, which makes cost per lead a *setting*
   rather than an outcome discovered after the money is gone.

### Where the headroom actually is

| Campaign | Impr. share | Lost to RANK | Lost to BUDGET | Binding constraint |
|---|---|---|---|---|
| AC Repair | 47.2% | 46.5% | 6.3% | **RANK** |
| Gas Boiler Repair | 54.5% | 45.5% | 0.0% | **RANK** |
| HVAC Installation | 36.4% | 10.7% | 52.9% | BUDGET |
| HVAC Repair | 33.6% | 57.7% | 8.7% | **RANK** |
| HVAC Replacement | 54.2% | 45.8% | 0.0% | **RANK** |

**Rank loss dominates on four of five campaigns.** Rank is won with ad relevance, expected
CTR and landing-page experience — not with budget. Budget binds only on HVAC Installation,
whose own CPQL is 10.6x over target, so relieving it would buy more of the wrong thing.

### Recommendation

Do not chase the $13,000 number in paid search this month. Spend it deliberately, in this
order:

1. Let the capped regime run and **measure a capped CPQL** — that number does not exist yet.
2. Cap the two campaigns still uncapped (`AMB-0910-CPC-CAP-1`, below).
3. Fix relevance where rank loss is 45–58% — the pinning work in section 6, then landing pages.
4. Take the LSA question seriously as a separate plan with its own requirements. It is where
   the leads are demonstrably already coming from.
5. Widen the BOFU keyword base before, not after, raising any ceiling.

Spending $13,000 at a $1,632 CPQL would buy roughly **8 unique qualified leads**. Hitting a
$250 blended CPQL would need about **52** — a **6.5x** efficiency gain. That gain does not
come from budget.

---

## 6. Headline pinning: one pin, or three?

### Recommendation: **three headlines pinned to position 1, not one.**

Pinning exactly one headline to position 1 fixes the most visible slot to a single asset,
removes all variation from it, and stops Google testing openers — you get a guaranteed
opener and lose the ability to learn which opener works. Pinning **three** to position 1
guarantees a service-keyword opener while preserving rotation among three candidates, so
asset-level reporting still tells you which one wins. It is the safer and more informative
of the two, and it is reversible.

### Why any pin at all — the diagnostic

**Zero pins exist across all 10 live approved ads.** Service-keyword coverage varies wildly:

| Campaign | Ad | Headlines with service keyword | Without | Ad Strength | Pins |
|---|---|---|---|---|---|
| AC Repair | 820900825416 | 14 | 1 | AVERAGE | 0 |
| AC Repair | 820900825419 | 8 | **7** | AVERAGE | 0 |
| Gas Boiler | 821319509209 | 12 | 3 | — | 0 |
| Gas Boiler | 821319509212 | 9 | 6 | — | 0 |
| HVAC Installation | 821319509197 | 10 | 5 | — | 0 |
| HVAC Installation | 821319509200 | 6 | **9** | — | 0 |
| HVAC Repair | 821714108336 | 6 | **9** | — | 0 |
| HVAC Repair | 821714108339 | 6 | **9** | — | 0 |
| HVAC Replacement | 821319509203 | 8 | 7 | — | 0 |
| HVAC Replacement | 821319509206 | 5 | **10** | — | 0 |

Ad 820900825419 opens with "Stop Guessing About Your AC" and carries filler like "Get Clear
Answers First" and "Bring Comfortable Air Back". It measured **2.77% CTR against
820900825416's 3.56%** at equivalent auction position.

**That comparison is confounded.** Controlling for device, 825419 *beats* 825416 on desktop
(1.82% vs 0.51%). So the CTR gap is a hypothesis worth testing, **not** proof that pinning
raises CTR. Nothing here promises a CTR gain.

Ad Strength will likely fall when pins are added. Per agency policy, Ad Strength is not an
optimization target and that is an accepted cost.

### Drafted challenger — AMB-0910-RSA-ACR-1 · fingerprint 19E2F2FFC311 · 1 operation, create-PAUSED

AC Repair ad group 202339087834 · final URL
`https://offer.ambientcoolingandheating.com/ac-repair/` · paths `ac-repair` / `severn-md`.

**Pinned to HEADLINE_1 (3):** AC Repair in Severn, MD · AC Repair Near You Today ·
Air Conditioner Repair MD

**Unpinned (12):** Licensed & Insured AC Repair · Free AC Repair Estimate · AC Not Cooling?
We Can Help · Local Anne Arundel AC Repair · AC Repair in Severna Park · AC Repair in
Columbia, MD · Book Your AC Repair Visit · Talk to a Real Technician · Straight AC Repair
Pricing · Residential & Commercial AC · Fix My AC Unit · Call for AC Repair Help

**Descriptions (4):** all at most 90 characters, listed in the plan JSON.

Validation: 15 headlines at most 30 characters, 4 descriptions at most 90, zero duplicates,
claim check PASS. `VALIDATED_OK` — 1 operation, `validate_only=True`,
`partial_failure=False`. Receipt at `receipts/validate-only/AMB-0910-RSA-ACR-1-2026-09-10.json`.

**Claims deliberately avoided:** 24/7, emergency, same-day, guaranteed response, financing,
rebates, discounts, warranty, ratings, review counts, certifications.

**Before this can be enabled** (a separate approval after readback QA, per workflow step 11):
obtain the Maryland Master HVACR licence number and the certificate of insurance and record
them in `work-order.yaml`; and fix message match — the landing page does not currently say
licensed and insured.

**Test protocol:** do not enable challenger and control simultaneously. At least 14 settled
days and at least 500 impressions per ad, compare relevant CTR **by device** at equivalent
position, require no deterioration in unique qualified conversion rate and no breach of the
$150 AC Repair CPQL.

---

## 7. Commercial HVAC — evidenced, negative removed

Crawled 45 pages of `ambientcoolingandheating.com` with a real browser (Playwright Chromium,
JS enabled, GET only; nothing submitted, no `tel:` activated, nothing published).

Evidence that Ambient serves commercial:

- `/services/heating-services/furnace-repair/` — "serve residential and commercial properties throughout the area"
- `/service-areas/crofton/` — "residential and commercial properties in Crofton, Maryland"
- `/service-areas/bowie/` — "residential and commercial customers in the region"
- `/blogs/` — "Commercial HVAC Planning For Maryland BEPS Rules"
- chamberofcommerce.com directory listing — "residential and commercial customer service"

**Executed:** `AMB-0909C-NEG-COMMERCIAL 9F88FEE76803`, 1 operation. Account-level negative
set 11252984411 went **272 → 271**; `commercial` confirmed absent on readback; 0 duplicate
`commercial` negatives on the five live campaigns. The 4 remaining duplicates all sit in
PAUSED campaigns (22822619680, 23883756382) and ad groups 159023127588 / 201974220664 in
20293627152, so they cannot block delivery.

**Open gap:** no dedicated commercial landing page exists, and none of the five paid landing
pages names commercial intake. Commercial traffic will now land on residential pages.
Recorded in `work-order.yaml` as `commercial_hvac_open_gap`.

## 8. Licensed & Insured — authorized, one item outstanding

Recorded in `work-order.yaml`: `licensed_and_insured_claim_authorized: true`, confirmed by
the Green Marketing approval owner on 2026-09-10 on the basis that Ambient can provide proof
of active contractor licence and insurance.

**Outstanding:** no licence number is published on the site and none was found in public
sources — the crawl found **zero** licence numbers in page text. Obtain the Maryland Master
HVACR licence number and the certificate of insurance and record both before the claim runs
live. The claim is used in the drafted challenger, which is create-paused and cannot serve.

---

## 9. Approval block

### Ready for approval

**AMB-0910-CPC-CAP-1 · fingerprint 7EA6922309EB · 2 operations · reversible setting change**

| Campaign | ID | Current | Proposed |
|---|---|---|---|
| Gas Boiler Repair | 24132507744 | ceiling UNSET (uncapped Maximize Clicks) | $25.00 |
| HVAC Replacement | 24132507753 | ceiling UNSET (uncapped Maximize Clicks) | $30.00 |

These are the two campaigns missed on 2026-09-04. Gas Boiler: 0 valid clicks, 42 invalid, on
$5.00/day — the ceiling costs no measured delivery. HVAC Replacement: uncapped it paid $30.50
per valid click across 5 valid clicks and $152.52, producing 0 unique qualified leads.
Ceilings match the peer campaigns carrying the same CPQL limits.
Rollback: clear the field back to unset. Budgets, bidding strategy, keywords, negatives, geo
and ads all untouched.
**`VALIDATED_OK` — 2 operations, `validate_only=True`, `partial_failure=False`.**
Receipt: `receipts/validate-only/AMB-0910-CPC-CAP-1-2026-09-10.json`.

*This lowers the ceiling on spend rather than raising it. Under the stated priority order,
qualified-lead economics outranks spend utilization, so this is the correct trade — stated
plainly rather than buried.*

**AMB-0910-RSA-ACR-1 · fingerprint 19E2F2FFC311 · 1 operation · create-PAUSED**
Full detail in section 6. Creating it does not enable it; enabling requires a second approval
after readback QA.

### Rejected this session

**AMB-0909C-CPC-INST-2 · 5D57E0EF3B70 · REJECTED · 0 operations performed.** Section 4.

### Superseded / do-not-execute (unchanged)

`46C39C6B7091` · `D448BFDE4650` · `23BE8FF0F24C` · `CE289F3508A2` · `A435FA09AC97` ·
`DE376F91F449`

### Executed this session (already read back, 0 failures)

| Plan | Fingerprint | Ops | Result |
|---|---|---|---|
| `AMB-0910-BUD-2` | `93541FBB5D7F` | 2 | Gas Boiler $42.76→$5.00, HVAC Replacement $26.32→$20.00 |
| `AMB-0909C-NEG-COMMERCIAL` | `9F88FEE76803` | 1 | account set 11252984411: 272→271, `commercial` absent |

**Budget compliance:** combined daily $465.63 → **$421.55**. Times 30.4 = **$12,815.12**.
Headroom **$184.88** below the $13,000 monthly charging limit. Breach **CLOSED**.

---

## 10. One consolidated question

**Do you want Local Services Ads scoped as a separate plan?**

91 of 99 leads in the measured window came from GBP and LSA at zero paid-search cost, while
paid search bought 5 unique qualified leads for $8,162. Agency policy is to consider LSA
first where service and location are eligible, and LSA needs its own eligibility check,
budget, verification and measurement plan — it cannot be folded into this work order.

**Recommendation: yes.** It is the only route on the table that puts the $13,000 to work
without either raising CPC ceilings back to the configuration that produced a $1,632 CPQL,
or spending into a keyword base too narrow to absorb it.

If the answer is no, the paid-search plan stands as written in section 5 and monthly spend
will remain well under $13,000 until the keyword base widens.

---

## Evidence artifacts

```
reports/ambient-cooling-heating/evidence/
  2026-09-10-whatconverts-lead-analysis.json        99 leads, 8 with GCLID, counts only, no PII
  2026-09-10-spend-strategy.json                    demand ceiling and constraint analysis
  2026-09-10-ceiling-regime-and-invalid-clicks.json per-day cost / valid / invalid
  2026-09-10-click-reconciliation.json              click_view vs metrics.clicks, 21 days
  2026-09-10-change-history-and-invalid-daily.json  6,532 change_event rows; 3 bid changes
  2026-09-10-regime-split.json                      uncapped vs capped, every metric
  2026-09-10-invalid-click-signature.json           click_type x device discard rates
  2026-09-10-location-expansion-source.json         asset sets + conversions by click type
  2026-09-10-commercial-and-licence-crawl.json      45 pages, real browser
  2026-09-10-rsa-pinning-and-challenger.json        pinning diagnostic + challenger
```

No credential, token, secret, or unredacted lead PII appears in any artifact. WhatConverts
GCLIDs are stored only as 16-character SHA-256 prefixes.
