# 05 — Developer repair handoff: permanent-lights form conversion

**Site:** `offer.apogeelawns.com` (WordPress + Divi + Gravity Forms, SiteGround) · **Form:** Gravity Forms form 1 ·
**LP:** `/permanent-christmas-lights-lincoln-ne/` (page 183) · **GTM:** GTM-M545Z8T2, live version 3.
Prepared under `LANDING_PAGE_CONTENT_WORKFLOW.md` §"Tracking and developer handoff" (read in full for this run). This
is a handoff specification. It changes nothing and authorizes no WordPress, GTM or Google Ads edit.

## Why

The live GTM form conversion (tag 7 → action 7772803337, label KOL7CImirvocEPS8jt9E) fires only when **all four** hold:
event `apg_permanent_lights_lead`, hostname `offer.apogeelawns.com`, path `^/thank-you/permanent-christmas-lights/?$`,
and a non-empty `lead_id`. Today no page exists at that path (WordPress redirects it to the LP), and nothing pushes the
event. The repair below fulfils the existing contract, so **GTM needs no change for the fix itself**.

## The contract to preserve (not weaken)

1. The server has **accepted** the submission (passed validation, reCAPTCHA/honeypot, not marked spam).
2. A **unique, non-PII lead ID** exists for that entry. The Gravity Forms entry ID (a positive integer) qualifies.
3. The visitor reaches the **approved thank-you state**: `https://offer.apogeelawns.com/thank-you/permanent-christmas-lights/`.
4. That page pushes `{event: 'apg_permanent_lights_lead', lead_id: '<entry id>'}` **once per page load**.
5. The same accepted lead keeps the same ID on reload; two leads never share an ID. Google de-duplicates the same action
   and transaction ID (Google Ads Help 6386790).

## Work items

| # | Item | Acceptance check |
|---|---|---|
| D1 | Publish page `/thank-you/permanent-christmas-lights/` (child of `/thank-you/` 1702, slug `permanent-christmas-lights`), `noindex`, GTM present, **no form**, same header/footer and 402-526-5754 | URL returns 200 directly (no redirect to the LP); WordPress REST lists it |
| D2 | Exclude the LP and the new thank-you page from full-page caching (SiteGround Speed Optimizer / Dynamic Cache) | The form's `state_1` timestamp changes on each fresh load; the thank-you markup is never served from cache |
| D3 | Form 1 confirmation → **Redirect** to D1 for accepted entries only. Use a `gform_confirmation` filter that returns a plain message instead of the redirect when `$entry['status'] === 'spam'` (Gravity Forms shows confirmations to honeypot-flagged submissions by default) | Spam or honeypot submissions never reach D1 |
| D4 | Redirect as `…/permanent-christmas-lights/?lead=<entry_id>&t=<hmac>`, where `t = hash_hmac('sha256', entry_id, wp_salt('auth'))` truncated. On D1, render the push **server-side** only when the token verifies, the entry exists, is not spam, belongs to form 1 and is under 30 minutes old: `window.dataLayer=window.dataLayer\|\|[];dataLayer.push({event:'apg_permanent_lights_lead',lead_id:'<entry_id>'});` Otherwise push nothing | Direct visit or tampered/expired token → no push; valid → exactly one push with a numeric ID |
| D5 | Never put name, email, phone, ZIP or notes in the URL, the dataLayer or analytics | Code review |
| D6 | Click-ID capture: if hidden fields `input_9`–`input_15` are meant for GCLID/GBRAID/WBRAID/UTM/landing page, populate them **client-side** from the landing URL and a first-party cookie (90-day first touch). Never server-side, because the page cache would replay one visitor's IDs to everyone | Hidden fields empty in cached HTML; filled in the browser after landing with parameters; stored on the entry |
| D7 | **Remove the two drafting notes published on the LP**: "…Reconfirm the current EverLights relationship and commercial availability before p…" and "…Exact consultation steps and estimate timing require client confir…" | Neither string appears in the LP text |
| D8 | (Lower priority) The LP renders form 1 three times, one of them 0×0, creating 34 duplicate DOM IDs. Keep one instance, or give each instance its own form ID with the same confirmation | No duplicate IDs; one submission = one entry = one WhatConverts lead |
| D9 | Confirm WhatConverts keeps capturing "GF1" after D3/D4 (form_list allowlist) | Next test lead appears in WhatConverts with form name GF1 |

**Rejected alternative (proposed only if D4 is impossible):** keep the in-page confirmation and push the event from
Gravity Forms' `gform_confirmation_loaded` JavaScript event with the entry ID. It needs AJAX submission and a GTM trigger
change (the path condition), and it exposes the ID client-side. It must be approved as an explicit contract change and
must never degrade into a click or page-view trigger.

## GTM follow-up (separate plan, after D1–D4 are live)

Tighten the trigger's `{{DLV | lead_id}}` condition from `.+` to the shipped ID format, e.g. `^[1-9][0-9]{0,11}$`. The
local model (`tests/test_apg_lead_id_contract.py`) shows `.+` accepts `undefined`, `null`, whitespace, an unreplaced
`{entry_id}` and `0`. Not fingerprinted: the ID format must come from the developer first.

## Controlled end-to-end test (requires its own approval — NOT authorized by this handoff)

After D1–D4: open GTM **Preview** (Tag Assistant) on the LP, which runs the container without publishing. Submit once with
a Green Marketing-controlled test identity supplied through the approved secure method (never customer data). Do not click
an ad and do not add a GCLID. Expect: redirect to D1 → one `apg_permanent_lights_lead` with a numeric ID → one
`googleadservices`/`google.com/pagead` conversion request carrying that transaction ID. Then reload once and expect the
same ID. Without a click ID, Google Ads will not attribute the test to the campaign, so the Conversions column stays
clean. Afterwards, label the WhatConverts lead as QA/spam; deleting entries needs a separate destructive-action approval.
Approval line to request: `APPROVE APG E2E FORM TEST (Preview, one controlled submission)`.
