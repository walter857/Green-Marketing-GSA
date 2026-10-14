# 09 — Owner decisions (2026-09-28) and reporting definitions

The owner answers were supplied in chat on 2026-09-28 and are recorded verbatim. They are **owner-provided facts**, not
website evidence. They were recorded in:
- the task work order `work-orders/work-order-measurement-repair-handoff-2026-09-28.yaml` (`owner_answers_2026_09_28`);
- `client.yaml` (`owner_decisions_2026_09_28`, `conversions.crm_stage_mapping.qualified`).

Both work orders pass validation, and `client.yaml` passes its schema.

## Decisions now closed

| Topic | Owner statement | Recorded decision |
|---|---|---|
| Tablets | "Landing pages are not tablet optimized so I excluded them." | The 2026-09-25 exclusion was **deliberate** and **stays**. Restoring tablets is not an approved optimization. A future restoration needs completed tablet-layout QA and a new, separately approved plan. `APG-0928-DEV-T2` is **REJECTED** (owner-confirmed exclusion); `APG-0928-DEV-T` stays VOID; `46060B03F5C9` stays invalid; no restoration code is issued. The one historical tablet impression neither supports nor undermines the usability reason |
| Qualified lead | "A qualified lead is someone who asks for the service on the form or on the call." | For this campaign, the service = **permanent Christmas light installation**. Nothing is added: no appointment, estimate, budget, property size, install date, and **no call-length rule** |
| Customer-supplied lights | "yes" | Apogee installs customer-supplied lights, as **owner-provided information only**. Neither website page mentions it. It does not imply compatibility with every product or system, seasonal hanging or removal, warranties on customer-owned equipment, or any other service |
| Omaha | — | Remains **EXCLUDED** (settled 2026-09-16) |

## Five measurement concepts (kept separate)

| # | Concept | Where it is recorded | What it is not |
|---|---|---|---|
| 1 | Accepted form submission | Gravity Forms entry, WhatConverts web-form lead ("GF1"); in Google Ads, action 7772803337 **once the repair is live** | not proof the person asked for the service |
| 2 | Recorded phone call | WhatConverts call lead on "GSA Traffic" (402-526-5754); Google Ads `call_view` for ad calls | not a conversion by itself |
| 3 | Google Ads duration-based call conversion | 7773013199 (ad calls) / 7773043879 (website calls) at **60 s**, a tracking setting | not the owner's qualification rule; unchanged in this run |
| 4 | Qualified lead (owner definition) | a human review marks it (below) | not duration-based: a caller can ask for the service in 20 s, and a 5-minute call can be about lawn mowing |
| 5 | Sold installation | **not defined by the owner**; CRM (Service Autopilot per `client.yaml`) | not inferred |

## Classifying each inquiry (no new CRM)

Each paid-funnel inquiry falls into exactly one class: **qualified service inquiry**, **wrong-service inquiry**, **spam**,
**internal test**, or **duplicate record of an inquiry already counted**.

**Workflow using what already exists.** WhatConverts already holds every GF1 form and every call to 402-526-5754, and
each lead has **Quotable** (Yes / No / Not Set / Pending) and **Spam** fields. A weekly reviewer (Apogee staff or Green
Marketing, as the owner assigns) reads the submission or listens to the recording and sets:

- **Quotable = Yes**: the person asked for permanent Christmas light installation, including installing lights they
  already own.
- **Quotable = No**: a real inquiry about something else (for example lawn care or seasonal hanging). It stays counted
  as a real inquiry.
- **Spam**: robocalls, solicitations, junk forms; also internal tests, with "GM QA" noted.
- **Duplicates**: WhatConverts' Repeat/duplicate flag is confirmed by the reviewer; one inquiry is counted once.

This is a data-entry workflow for the owner's team. Green Marketing makes no WhatConverts change in this run.

**Interpretation to confirm in practice (labelled, not a new rule):** the paid-page form *is* a "Request a Free
Estimate" form for permanent lights, so a real, non-spam submission there reads as asking for the service unless its
notes say otherwise. The reviewer still reads each submission. This does not add or remove any requirement from the
owner's definition.

## CPL and CPQL (reporting plan)

- **Lead** = qualified service inquiries + wrong-service inquiries (real, unique, non-spam, non-test).
- **CPL** = paid-campaign spend ÷ leads.
- **CPQL** = paid-campaign spend ÷ **qualified** leads (owner definition).
- Paid attribution uses, in order:
  1. Google Ads conversions (forms after the repair; ad calls);
  2. WhatConverts "GSA Traffic" calls on 402-526-5754;
  3. WhatConverts web-form leads whose landing URL carries the campaign's `utm_source=google&utm_medium=cpc`.

  A WhatConverts "(direct)" form is not counted as paid unless other evidence ties it to an ad visit.
- Use only periods in which form and call capture are verified. None exists yet.

**Source of the $100 target.** `work-order.yaml` → `economics_2026_09_16.target_cpl_usd: 100` (acceptable range 90–125).
It is recorded as "OWNER INPUTS SUPPLIED 2026-09-16… GREEN MARKETING PLANNING ASSUMPTIONS for a controlled initial test"
and labelled `PLANNING_ASSUMPTIONS_NOT_HISTORICAL_PERFORMANCE`. It is a **raw-lead CPL planning target**, not a CPQL
target; no CPQL target exists. The 5% click-to-lead and 20% lead-to-sale rates in the same record are **assumptions, not
Apogee performance**. The "≈$5 per click" figure is derived from them and is not observed.

**Still unknown:** the definition of a sold installation and the average gross profit per sold installation. CAC,
ROAS, gross-profit ROAS and profit after ad spend stay **not computable** until both are supplied.
