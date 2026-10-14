# 05 — Paid-call measurement: verification, architecture, controlled test plan

Settled numbers: advertising and paid-page number **402-526-5754** (`+14025265754`). 402-202-7261 is the forwarding
destination; 402-783-8482 is WhatConverts' website pool number. They are never substituted for each other.

## Verification of the recommended architecture (read-only, 2026-09-28)

| # | Check | Result | Evidence type |
|---|---|---|---|
| 1 | Call asset 422649064971 uses 402-526-5754 and maps to calls-from-ads action 7773013199 | **VERIFIED**: `USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION` → 7773013199 (AD_CALL, Primary, 60 s); link ENABLED; APPROVED; schedule Mon–Fri 08:00–17:00, Sat 08:00–12:00, Sunday absent (account time America/Chicago) | Google Ads API |
| 2 | Website-call tag uses 402-526-5754, destination 18453077620, label lp3jCKf5vPocEPS8jt9E, LP-only trigger | **VERIFIED as configured** (tag 9, published) | published container + GTM UI |
| 3 | Current WhatConverts swap rule | **VERIFIED**: number 640641 "Website Traffic" +1 402-783-8482, trigger "Pool: Website Traffic", `swap_number` 4022027261. Runtime cookie agrees | WhatConverts API `tracking/numbers` + runtime cookie |
| 4 | Assignment and route of 402-526-5754 | **PARTLY VERIFIED.** Number 640646 "GSA Traffic" is a **WhatConverts number in profile 174313**: static (trigger "None"), source "GSA Traffic", medium "(none)", voice and messaging on, **`last_used` null (never received a call or text)**. Routing goes through "Call Flow: Apogee Lawns - ICF". The API does not expose that flow's destination, whisper, menu or recording steps, so **forwarding to 402-202-7261 is unverified** | WhatConverts API |
| 5 | WhatConverts → Google Ads integration and import rules | **UNKNOWN from the API.** Inferred inactive for this account: the Google Ads account holds only the 3 actions we created, and none is a WhatConverts import action. Needs owner confirmation | Google Ads API (inference) |
| 6 | The same call cannot become two Primary conversions | **Holds today by configuration:** ads calls → 7773013199 (Primary); website calls → 7773043879 (**Secondary**, excluded from Conversions); no import action exists. Transaction IDs deduplicate only within one action (Google Ads Help 6386790), so a future import must never point at a Primary call action | configuration |

Runtime replacement of 402-526-5754 by a Google forwarding number for ad visitors is **NOT TESTED**. Google shows the
forwarding number only to visitors who arrive from an ad (Google Ads Help 6095883). No ad click is authorized, and current
Google help pages document no debug mode, so none is relied on.

## Call types, kept separate

| Type | Measured by | Counts as |
|---|---|---|
| Call from ads (call asset) | Google forwarding number in the ad → 7773013199 at 60 s or more | Primary lead (not "qualified") |
| Website call (ad visitor dials the forwarding number shown on the LP) | tag 9 → 7773043879 at 60 s or more | Secondary until promoted |
| Phone-link click (`tel:`) | not tracked | never a conversion |
| Recorded call | WhatConverts ("GSA Traffic" for 402-526-5754), subject to the call flow's recording setting | system of record |
| Qualified call | WhatConverts `quotable` / owner definition (**not yet defined**) | qualified lead |
| Sold job | CRM (Service Autopilot per client.yaml), stage mapping **not defined** | sale |

A 60-second call is a measurement threshold, not proof of a buyer.

**Attribution owner (recommended, consistent with the audit):** Google's website-call tag owns paid website-call
attribution. WhatConverts records and qualifies every call and **must not import those same calls to Google Ads**.
WhatConverts' "GSA Traffic" label on 402-526-5754 is static and cannot tie a call to a click.

## Acceptance criteria for a later promotion of 7773043879 to Primary (not done now)

1. The routing test (TC-1) passed: 402-526-5754 reaches Apogee's live answer as intended, and WhatConverts records it.
2. At least one real website-call conversion is recorded in `all_conversions` for 7773043879, and it matches a WhatConverts
   "GSA Traffic" call at the same minute with a WhatConverts duration of 60 seconds or more.
3. WhatConverts' Google Ads integration is confirmed off, or confirmed not to import calls to any Google Ads action.
4. A separate plan changing only `primary_for_goal` on 7773043879, with before/after readback and its own approval.

## Controlled test-call plan (separate approval; nothing placed)

**TC-1 Routing (no ads involved).** Requested approval: `APPROVE APG ROUTING TEST CALL`.
- **Steps:** during answer hours (Mon–Fri 08:00–17:00 or Sat 08:00–12:00 CT), from a Green Marketing-controlled phone,
  dial 402-526-5754 and stay on the line for at least 70 seconds.
- **Record:**
  - what the caller hears (menu or whisper);
  - who answers;
  - the WhatConverts lead: source "GSA Traffic", duration, recording present or absent;
  - the time, to match against WhatConverts.
- **Side effects:** takes receptionist time, so notify Apogee first. Creates one WhatConverts lead, to be marked QA
  afterwards. Creates **no** Google Ads conversion, because it isn't an ad call.

**TC-2 Website-call replacement.** Needs a genuine ad-visitor session, and clicking our own ads is not authorized. The
plan is to wait for the first organic website-call conversion and verify it against WhatConverts under criterion 2 above.

**TC-3 Calls from ads.** Organic only. Verify `call_view` (status, duration), 7773013199 at 60 s or more, and the matching
WhatConverts "GSA Traffic" lead.

## What the owner needs to supply from WhatConverts (screenshots; redact caller data)

1. **Call Flow "Apogee Lawns - ICF":** each step (menu, whisper, forward-to number, ring timeout, voicemail) and whether
   recording is on.
2. **Integrations → Google Ads:** connected or not; if connected, the Google Ads customer ID, which lead types and which
   conversion actions it sends, and its qualification rule.
3. **Phone number 640646 "GSA Traffic":** confirm it is intended as a static number (no pool) and that "GSA Traffic" is
   the desired source label.

No lead export is needed.


---

## Revision 2026-09-28 (run D) — call-flow screenshot and corrected capture wording

**Correction to the run-C report.** It said both "WhatConverts is recording … calls to 402-526-5754" and "that number has
never received a call; routing untested". The supported description is:

> The number is configured in WhatConverts. The screenshot shows a recording step and a dial destination in the named
> flow. Successful routing, recording, and attribution remain untested unless separate evidence establishes them.

Zero recorded calls is **not** evidence of a broken number, and a configured number is **not** evidence of working
end-to-end capture.

**What the owner-supplied screenshot establishes.** It is described in the owner's message; the image itself was not
attached to this session, so the stated contents are recorded, not independently read.
- Flow name: **Apogee Lawns - ICF**.
- Visible sequence: **Incoming Call → Call Recording** ("This call will be recorded for quality assurance.") **→ Dial /
  Client → Direct Call to 4022027261**.
- A **No Answer** branch exists; its downstream handling is not shown.
- The view shows a **Finish** button, i.e. an editor view. It does not prove this exact configuration is saved and
  active.

**What it does not establish:** that the flow is saved and active; that a call reached the receptionist; that recording
worked on a completed call; that no-answer, timeout, voicemail or after-hours handling is complete; or that recording
disclosure satisfies recording-consent law. Nothing was clicked or changed.

**Assignment, resolved from saved configuration.** A fresh read-only WhatConverts API read of `tracking/numbers`, allowlisted
fields only, shows number **640646** "GSA Traffic" (+1 402-526-5754) with `call_flow: "Call Flow: Apogee Lawns - ICF"`,
trigger "None" (static), `last_used: null`. So the paid number is assigned to the flow of that name in saved
configuration. The API does not expose the flow's steps, and its number-level `call_recording` field is null, so the
screenshot is the only evidence of the steps.

| Layer | Status |
|---|---|
| Tracking-number assignment (402-526-5754 → flow "Apogee Lawns - ICF") | **VERIFIED** (saved configuration, API) |
| Saved call-flow steps (recording → dial 402-202-7261) | **PARTLY EVIDENCED** (owner screenshot of an editor view; saved state not proven) |
| Observed call routing | **NOT TESTED** (0 calls ever on the number) |
| Observed call recording | **NOT TESTED** |
| Google Ads attribution (ad calls → 7773013199; website calls → 7773043879) | **CONFIGURED, NOT TESTED** |
| Lead qualification (owner definition: asks for permanent Christmas light installation) | **DEFINED**; a review workflow exists in WhatConverts' Quotable field (09) |

**Still open:** WhatConverts' Google Ads integration setting (the one remaining screenshot needed), and the controlled
routing test (TC-1, separate approval). The earlier request for call-flow screenshots is now **satisfied**, apart from the
No Answer branch, which only matters for after-hours or missed-call handling.

**Import rule clarified.** "WhatConverts must not import these same calls" applies to **duplicate primary reporting of
the same call**. A future outcome-based import (for example, qualified or sold outcomes into a separate, properly
de-duplicated action) is not ruled out. It would be designed separately. Nothing is imported, promoted or re-owned here.
