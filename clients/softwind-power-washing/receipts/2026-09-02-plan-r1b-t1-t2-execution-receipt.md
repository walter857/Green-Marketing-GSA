# PLAN-R1B — EXECUTION RECEIPT, ACTIONS T-1 AND T-2

**Plan** PLAN-R1B · **Fingerprint** `B7AD76CB16F8` · **Approved by** Walter Correa
**Approval command received** `APPROVE PLAN-R1B B7AD76CB16F8 FOR 1521725229`
**Executed** 2026-09-02 01:27–01:29 America/New_York
**Account** `Softwind Power Washing - Live` / `1521725229` / Power Washing

**Google Ads mutations: 0. Form submitted: NO. Call placed: NO.**

Evidence: `snapshots/plan-r1b-validation-2026-09-02T012727.json`,
`snapshots/r1b-t1-t2-2026-09-02T012839.json`.

---

> ## CORRECTION NOTICE — added 2026-09-02 09:53 ET
>
> **This receipt describes `AW-17878095007` as a "foreign" tag belonging to an account
> "Green Marketing does not control". That characterisation was WRONG.**
>
> `AW-17878095007` is the **`conversion_tracking_id` of Google Ads customer `2429758629`,
> "Softwind Landscape & Masonry - Live"** — the client's own sibling account, at level 1 under
> the authorized Green Marketing MCC `3373711342`. Resolved 2026-09-02 by reading
> `customer.conversion_tracking_setting.conversion_tracking_id` and sweeping all 32 enabled
> non-manager accounts under that MCC; exactly one matched. **An `AW-` value is a conversion
> tracking ID, not a customer ID** — which is why the number never matched a customer ID and the
> tag looked foreign.
>
> **Every observation in this receipt stands.** The tag really does take `form_start`,
> `form_submit`, form-data POSTs, the GCLID and the website-call replacement, and Softwind Power
> Washing's own call path really is preempted. **Only the ownership conclusion changes:** this is
> cross-account contamination between two scope-fenced sibling accounts of the same client — an
> attribution and scope defect — **not a third-party data leak or a privacy breach.**
>
> Resolved in `plans/2026-09-02-plan-r7a-website-tracking-form-call-repair.yaml`.


## 1. Pre-execution gate — PASS

| Step | Result |
|---|---|
| Re-read identity | **PASS** — `Softwind Power Washing - Live` / `1521725229` / manager `false` / test `false` / ENABLED / USD / America/New_York |
| Re-read exact target resources | **PASS** — 4 conversion goals, 4 conversion actions, both `conversion_goal_campaign_config` rows, all unchanged |
| Recompute fingerprint | **`B7AD76CB16F8` — EXACT MATCH**, recomputed twice |
| Mismatch check | **No mismatch. Proceed.** |
| Validation | **46 / 46 checks pass** |
| `validate_only` | **NOT APPLICABLE** — zero Google Ads mutations, no payload to validate |
| GET_DIRECTIONS still `biddable: false` | **YES** — customer level and both campaigns |

## 2. Execution status per action

| Action | Type | Status |
|---|---|---|
| **T-1** Load arrival URL, instrumented Chromium, network capture | EXTERNAL READ | **COMPLETE** — desktop + mobile |
| **T-2** Snapshot persisted identifiers before touching the form | EXTERNAL READ | **COMPLETE** — desktop + mobile |
| **T-3** Submit Gravity Forms `gform_1` exactly once | **EXTERNAL WRITE** | **HALTED — NOT EXECUTED** |
| T-4 … T-8 | READ / WRITE | **NOT EXECUTED** — all sequenced after T-3 |

### Why T-3 halted

**The plan's own preconditions gate it, and three are unmet.** Walter's approval satisfied
R1B-PRE-1 only.

| Precondition | State |
|---|---|
| R1B-PRE-1 Walter's approval of this exact plan and fingerprint | **MET** |
| **R1B-PRE-2** Test email address | **NOT MET** — the form's `input_3` is an email field |
| **R1B-PRE-3** Client notified in advance so nobody chases the test lead | **NOT MET** |
| **R1B-PRE-4** Named cleanup owner agreed, by name | **NOT MET** |
| R1B-PRE-5 CRM/webhook destination | NOT MET — non-blocking, T-6 discovers it |

T-3 writes a live lead into WordPress, WhatConverts and an unidentified CRM that may trigger
speed-to-lead automation. It is not executed without those three.

**This is not a partial failure.** No write was attempted, so there is nothing to inventory or
recover. Execution stopped cleanly at a gate the plan defines.

---

## 3. FINDING 1 — Foreign account `AW-17878095007` is running website call tracking on Softwind's landing page, and receives Softwind's GCLIDs

**PROVEN, on both desktop and mobile, before any form submission.**

Observed request, both profiles:

```
https://www.googleadservices.com/pagead/conversion/17878095007/wcm
    ?cc=ZZ
    &dn=6315027946                       <- Softwind's approved phone number
    &cl=SFv1CLSo--UbEJ-p-MxC             <- a conversion label owned by 17878095007
    &gclid=GM-TEST-SYNTHETIC-GCLID-...   <- the visitor's Google click ID
```

and

```
https://www.google.com/pagead/attribution/wcm
    ?cc=ZZ&dn=6315027946&cl=SFv1CLSo--UbEJ-p-MxC
    &gclid=GM-TEST-...&gclaw=GM-TEST-...
```

`/pagead/conversion/<account>/wcm` is the Google Ads **website call conversion / number
replacement** endpoint. `dn` is the destination number to be swapped, `cl` the conversion label.
On mobile the browser then cached a localStorage key named literally
**`SFv1CLSo--UbEJ-p-MxC,6315027946`** — Google's label-plus-number replacement cache.

**Both accounts load on the page,** confirmed by paired requests:

| Endpoint | `17878095007` | `18369652705` (Softwind) |
|---|---|---|
| `pagead/viewthroughconversion/<id>/` | present | present |
| `google.com/rmkt/collect/<id>/` | present | present |
| `google.com/pagead/1p-user-list/<id>/` | present | present |
| **`pagead/conversion/<id>/wcm`** | **PRESENT** | **ABSENT** |

### What this establishes

1. **Softwind's own website-call conversion action `7708765130` cannot fire from this page.** No
   `wcm` request is made for `18369652705`. This is a direct, sufficient explanation for
   `all_conversions = 0.0` on that action and **0 `call_view` rows** across the account's life.
   The path was never dead by accident — it was never wired.
2. **Softwind's paid GCLIDs are transmitted to a Google Ads account Green Marketing does not
   control.** Via `wcm`, and via `1p-user-list` and `rmkt/collect`, account `17878095007` is also
   **building remarketing audiences from Softwind's paid traffic.**
3. This upgrades the foreign tag from a **suspected** P0 landing-page defect to a **proven active
   data leak and the proven cause of one dead conversion path.**

**PLAN-R1B named this "the single most valuable output of the test." It was obtained at T-1,
without submitting anything.**

---

## 4. FINDING 2 — SG-Captcha intercepts the paid landing-page click

**HTTP status is `202`, not `200`,** and the arrival passed through a captcha interstitial. Proven
by the `ref=` parameter Google echoed back:

```
ref=https%3A%2F%2Foffer.softwindli.com%2F.well-known%2Fsgcaptcha%2F%3Fr%3D%252Fpower-washing-...
```

and by two direct requests to `https://offer.softwindli.com/.well-known/sgcaptcha/?r=...` in the
load chain.

**This sits directly in the paid click path**, on the page carrying every ad click in campaign
`24103511039`. A real visitor arriving from an ad may be served a challenge before the landing
page. It is a plausible contributor to zero form submissions across 18 paid clicks, and it is a new
P0 that no prior audit isolated. Related: it is the same mechanism that previously fed a non-JS
client an empty stub and produced a false "no tracking" reading.

**Not yet established:** whether a challenge is *rendered* to ordinary human visitors or silently
passed. That requires a Stage 2 diagnostic, and it must not be assumed either way.

---

## 5. FINDING 3 — WhatConverts sets cookies but no WhatConverts script was observed loading

| Observation | Desktop | Mobile |
|---|---|---|
| Any request to a WhatConverts host | **NONE OBSERVED** | **NONE OBSERVED** |
| `wc_swap` cookie | `6315025402+..+6315535927+..+197159` | same |
| `wc_client`, `wc_visitor`, `wc_client_current` | present, cookie + localStorage | same |
| Number actually rendered | **(631) 502-7946** | **(631) 502-7946** |

The swap cookie nominates **(631) 502-5402** and **(631) 553-5927**, but the page renders the
static approved **(631) 502-7946** in both the `tel:` href and the body. **The dynamic number
insertion is loaded-but-not-swapping**, consistent with the DNI defect recorded 2026-08-26 and
never resolved.

Stated precisely and not over-claimed: **no request to a WhatConverts host was observed in either
profile.** The `wc_*` cookies are present, so something is setting them — possibly the GTM
container `GTM-P3LD97NN` or a WordPress plugin. Whether WhatConverts is capturing this session at
all is **UNKNOWN and must be established**, because it bears directly on the reliability of the
user-supplied WhatConverts records.

---

## 6. Identifier persistence — T-2 result: PASS

| Identifier | In final URL | In storage / cookie / hidden field |
|---|---|---|
| `gclid` | YES | **YES** |
| `gbraid` | YES | **YES** |
| `wbraid` | YES | **YES** |
| `utm_source` / `utm_medium` / `utm_campaign` / `utm_content` | YES | **YES** |
| `utm_term` | YES | no |

**GCLID, GBRAID and WBRAID all persist.** `utm_term` survives in the URL but is not written to
storage or a hidden field — a minor gap that would cost keyword-level attribution in the CRM if the
CRM reads hidden fields rather than the URL. Recorded, not yet actioned.

Also captured: `_gcl_aw`, `_gcl_au`, `GCL_AW_P`, `_gcl_ls` all set — Google's own click-ID storage
is working correctly.

## 7. Form inspection — read only, never submitted

`form#gform_1`, `method=post`, **5 visible fields**, 12 hidden. Matches the plan exactly.

| Field | Type | Required attribute |
|---|---|---|
| `input_9` | text | false |
| `input_1` | text | false |
| `input_4` | tel | false |
| `input_3` | email | false |
| `input_7` | textarea | false |

**No field carries the HTML `required` attribute** — validation is server-side or JS-driven only.
Worth noting for CRO: nothing stops an empty submission client-side.

**GA4 `G-D4BZM40RYD` and GTM `GTM-P3LD97NN` confirmed loading. ClickCease confirmed loading.
Zero console errors on desktop; one `ERR_CONNECTION_REFUSED` on mobile for an unresolved resource.**

**A malformed telephone link exists on the page: `tel:(631)` alongside the correct
`tel:(631) 502-7946`.** A tap on the malformed link dials nothing. Minor, real, recorded.

---

## 8. Ledger effect

- **PLAN-R1B → PARTIALLY EXECUTED.** T-1, T-2 complete. T-3–T-8 pending inputs IN-1 and IN-2.
  The approval `B7AD76CB16F8` remains live and does **not** need re-issuing.
- **Stage 2 (PLAN-R7A) escalates.** The foreign tag is no longer suspected — it is proven to be
  taking Softwind's GCLIDs and occupying the website-call path. SG-Captcha is added as a new P0.
- **IN-7 (ownership of `AW-17878095007`) escalates from a backlog question to the gating input for
  a proven live leak.**
- **Stage 10 gains an item:** confirm whether WhatConverts is recording on the offer subdomain at
  all, before any further reliance on its lead log.

## 9. Safety

**Zero Google Ads mutations. No form submitted. No call placed. No website modified.** The browser
sessions were read-only page loads; no submit control was clicked, no `form.submit()` invoked, no
POST issued. Every Google Ads call this run was a `SELECT` through `GoogleAdsService.search`.
