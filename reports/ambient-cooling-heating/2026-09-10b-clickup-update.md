# ClickUp activity update — Ambient Cooling - Live (2401959466) — 2026-09-10

Completed work and measured results only. No forecast, no expected improvement reported as
achieved.

---

## Changes made to the account today (3 operations, all read back clean)

**Budget — 2 operations.** Gas Boiler Repair daily budget $42.76 → $5.00. HVAC Replacement
$26.32 → $20.00. Combined daily budget across the five live campaigns is now **$421.55**.
At 30.4 days that is **$12,815.12** against the $13,000 monthly charging limit — **$184.88
of headroom**. The prior configuration projected $13,173.23 and would have breached the
limit. That breach is now closed.

**Negative keyword — 1 operation.** Removed `commercial` from the account-level negative
keyword list (set 11252984411, 272 → 271 members) after crawling 45 pages of the client
website and confirming Ambient markets to commercial customers on service pages, service-area
pages, the blog and a third-party directory listing. Readback confirms `commercial` is gone
and that no duplicate `commercial` negative remains on any of the five live campaigns.

---

## Investigation results

**WhatConverts is now connected.** API credentials tested and working — 99 leads pulled for
2026-08-14 → 2026-09-10 from profile 105803. No credential value was ever printed, logged or
written to any file, and no lead PII was retained.

**Only 8 of those 99 leads came from paid search.** The other 91 arrived through Google
Business Profile, Local Services Ads and organic, at zero paid-search cost.

**Cost per unique qualified lead, measured by joining WhatConverts leads to Google Ads
clicks by GCLID (2026-08-14 → 2026-09-09):**

| Campaign | Spend | Unique qualified leads | Cost per lead | Agreed limit |
|---|---|---|---|---|
| AC Repair | $3,084.87 | 3 | $1,028.29 | $150 |
| HVAC Repair | $1,951.94 | 1 | $1,951.94 | $250 |
| HVAC Installation | $2,972.96 | 1 | $2,972.96 | $280 |
| HVAC Replacement | $152.52 | 0 | — | $280 |
| Gas Boiler Repair | $0.00 | 0 | — | $250 |

**Root cause identified — the campaigns had no maximum CPC at all until 2026-09-04.** The
account change history shows max-CPC ceilings applied to AC Repair ($25), HVAC Repair ($25)
and HVAC Installation ($30) on 2026-09-04 at 16:56, each created from an empty prior value.
Before that the campaigns ran on uncapped Maximize Clicks. Splitting the data at that moment:

- Uncapped, 08-14 → 09-03: $8,025.18 across 172 valid clicks — **$46.66 per click**
- Capped, 09-05 → 09-09: $103.71 across 4 valid clicks — **$25.93 per click**

The capped window is 5 days and 4 clicks. It is directionally consistent with the ceiling
working but far too small to call the effect established.

**Gas Boiler Repair and HVAC Replacement were missed on 2026-09-04 and are still uncapped.**
A 2-operation package to cap them is drafted, validated and awaiting approval.

**Invalid clicks are 91% of raw click volume.** Google filtered 1,779 invalid clicks against
177 valid ones across the account in the last 30 days. In June the rate was 20.6%; in August
it was 91.4%. The traffic has one clear shape: location-extension clicks on mobile, 1,741 raw
of which Google discarded 1,705 (97.9%). Worth raising with Google support and with ClickCease.

Important: we checked before recommending anything. The location-extension clicks Google
*kept* are 25.3% of spend but **30.8% of primary conversion records**, at a lower cost per
record than regular ad clicks. Disabling the location asset set would remove one of the
account's most productive click types, so no change is recommended there.

---

## Decisions recorded

**HVAC Installation CPC increase ($30 → $65) — REJECTED.** The proposal required at least 2
of 3 September 1 conversion records to be proven unique qualified leads. Measurement returned
1. Independently, the converting clicks used to justify the increase were all bought before
any ceiling existed, so they argue against the increase rather than for it. Zero operations
were performed.

**Headline pinning — recommendation is three headlines pinned to position 1, not one.** One
pin fixes the most visible slot to a single asset and stops Google testing openers. Three
pins guarantee the service keyword leads while preserving rotation, so we still learn which
opener performs. A paused challenger ad for AC Repair is drafted and validated.

Supporting diagnostic: none of the 10 live ads uses any pin today, and five of them carry
7 to 10 headlines with no service keyword at all. The weakest AC Repair ad opens with "Stop
Guessing About Your AC" and measured 2.77% CTR against its sibling's 3.56% — though that
comparison is confounded by device and is a hypothesis to test, not a proven gain.

**"Licensed & Insured" is authorized** on the client's confirmation that proof of active
contractor licence and insurance can be provided. Recorded in the work order. Still needed
before the claim goes live: the Maryland Master HVACR licence number and the certificate of
insurance — neither is published on the site and neither was found in public sources.

---

## Open question for the client

**Should Local Services Ads be scoped as a separate plan?**

The measured position is that $13,000/month cannot be spent productively on the current
paid-search setup. There are 5 distinct keywords live; even at 100% impression share and the
current capped CPC, the ceiling is roughly $11,400/month, and at a realistic impression share
closer to $6,900. Reaching $13,000 on today's keywords would require raising CPC ceilings back
toward the uncapped configuration that produced a $1,632 blended cost per qualified lead.

Meanwhile 91 of 99 leads already arrive through Google Business Profile and Local Services
Ads. LSA is pay-per-lead with its own cap, which makes cost per lead a setting rather than
something discovered after the money is spent. It needs its own eligibility check, budget,
verification and measurement plan.

Recommendation: yes, scope it separately.

---

## Awaiting approval

| Package | Fingerprint | Operations | What it does |
|---|---|---|---|
| AMB-0910-CPC-CAP-1 | 7EA6922309EB | 2 | Cap the two uncapped campaigns: Gas Boiler $25, HVAC Replacement $30 |
| AMB-0910-RSA-ACR-1 | 19E2F2FFC311 | 1 | Create one PAUSED AC Repair ad with 3 headlines pinned to position 1 |

Both validated against the live account with `validate_only=True`. Neither has been executed.
The RSA is create-paused; enabling it would require a second approval after readback QA.
