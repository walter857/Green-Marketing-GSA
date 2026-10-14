# Apogee Lawns — measurement and conversion-friction repair spec (APG-1005-WEB-REPAIR)

**Account:** Apogee Lawns LLC - Live · **816-462-6278** (manager 337-371-1342 is not the account)
**Service:** Permanent Christmas light installation · similar-local-service (scope approved by Walter, 2026-09-16)
**Campaign:** S | Website Leads | Permanent Christmas Lights | Apogee Lawns | $500 | 09_2026 (24257151015)
**Paid page:** https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/
**Required thank-you page:** https://offer.apogeelawns.com/thank-you/permanent-christmas-lights/
**Paid phone:** 402-526-5754 (402-202-7261 is the forwarding destination only and must not appear on the paid pages)

Executor: Apogee's website developer, on the owner's authorization. Green Marketing does not edit WordPress.
**No GTM change is required:** published version 3 already expects exactly this path, event and `lead_id` key.
No Google Ads, GTM or WhatConverts change is part of this spec. `LANDING_PAGE_CONTENT_WORKFLOW.md` was read
in full before this handoff; its tracking-handoff requirements are covered in R2, R3, R4, R6 and R7.

---

## A. Current state, verified 2026-10-05

Checked with a real browser engine (Chrome via Playwright) at 1440x900 and 390x844. Nothing was submitted or
clicked, and every Google Ads and Floodlight conversion request was intercepted and blocked, so nothing was sent.
Hidden-field values were compared to known values in the browser and never stored or printed. SiteGround served
its normal bot challenge first; the browser passed it like a visitor's browser does. That challenge is not
evidence that people cannot use the page.

| # | Check | Status 2026-10-05 | Evidence |
|---|---|---|---|
| A01 | Thank-you page exists | **FAIL** | `/thank-you/permanent-christmas-lights/` returns **301 to the paid page** (WordPress closest-slug redirect) |
| A02 | Cache cannot replay success state or attribution | **FAIL** | A visit with **no query string** received hidden fields already set to `google`, `cpc`, `apogee_permanent_lights_2026`, `permanent christmas light installation` and ad ID `825023783007`, plus a cached form `action` (395 characters) containing **another visitor's gclid, gbraid and UTMs**. Same on desktop and mobile loads |
| A03 | Only accepted, valid entries reach the success flow | **NOT IMPLEMENTED** | No success redirect exists to evaluate |
| A04 | Success event carries the unique lead ID | **FAIL** | The page's dataLayer holds only `gtm.js`, `gtm.dom` and `gtm.load`. `apg_permanent_lights_lead` is pushed nowhere |
| A05 | Published drafting notes removed | **FAIL** | C1, C2 and C3 are all live, plus two more found today (C4, C5 below) |
| A06 | One form instance per page | **FAIL** | **3 instances** of Gravity Forms form 1 (two visible, one hidden) and **34 duplicate DOM IDs** |
| A07 | Click IDs, UTMs and consent state captured | **FAIL** | The values present are cache-replayed, not the visitor's own (A02). No consent platform exists, so no consent state is recorded. 5 of the 7 ad clicks landed with **gbraid**, 0 with gclid, so capture must include gbraid and wbraid |
| A08 | Lead delivery reaches the intended recipient | **UNVERIFIED** | WhatConverts' public profile script lists `gform_1` as a tracked form. The notification recipients are unknown |

Already correct (do not change):
- H1 "Permanent Christmas Light Installation in Lincoln, NE".
- Only 402-526-5754 is displayed, with `tel:` links.
- The mobile sticky "Call Now / Free Quote" bar.
- No horizontal overflow at 390 px.
- noindex and nofollow.
- GTM-M545Z8T2 and AW-18453077620 load. Google's website-call script loads on the paid page, while WhatConverts'
  only swap entry targets 402-202-7261, which is absent from the paid page, so **the two systems do not swap
  the same number**.

## B. Minimum necessary repairs

**R1 — Thank-you page (A01).** Publish a WordPress page at exactly
`https://offer.apogeelawns.com/thank-you/permanent-christmas-lights/`:
- noindex, nofollow, and the same header as the paid page, with GTM-M545Z8T2.
- Phone 402-526-5754 as `tel:+14025265754`. No form.
- Copy: "Thank you. We received your request for a permanent-lighting estimate. Apogee Lawns will follow up using the
  contact details you provided." Make no response-time promise.

**R2 — Cache and attribution rendering (A02).**
- Exclude the paid page and the thank-you page from SiteGround dynamic/HTML caching and any CDN HTML cache, then
  purge.
- The Gravity Forms hidden attribution fields must leave the server **empty**: turn off server-side dynamic
  population for them. R7 fills them in the browser.
- The form `action` must not carry a query string.

**R3 — Accepted entries only (A03).** For form 1 on the paid page only, set the confirmation to
**Redirect** to the thank-you URL with one parameter `lid`:
- `lid` = `apg-{entry_id}-{token}`, where `token` = first 10 hex characters of HMAC-SHA256(server secret,
  entry_id).
- Generate it in `gform_confirmation` **only** when the entry is saved and `status` is not `spam`.
- Validation failures never reach confirmation (native Gravity Forms behavior). Keep the honeypot (`input_16`)
  enabled and empty.

**R4 — Server-verified success event (A04).** On the thank-you page, the server checks:
- `lid` is present and well formed;
- the HMAC matches;
- the entry exists and is not spam.

Only then does it render this exactly once:

```html
<script>
  window.dataLayer = window.dataLayer || [];
  if (!sessionStorage.getItem('apg_lead_' + 'apg-{entry_id}')) {
    sessionStorage.setItem('apg_lead_' + 'apg-{entry_id}', '1');
    dataLayer.push({event: 'apg_permanent_lights_lead', lead_id: 'apg-{entry_id}'});
  }
</script>
```

Rules for the lead ID and the push:
- `lead_id` is unique per entry, non-personal, and at most 64 characters (Google's transaction-ID rule,
  support.google.com/google-ads/answer/6386790). GTM passes it as the conversion's Transaction ID.
- A direct visit without a valid `lid` renders **no** push. A refresh re-uses the same ID: the session guard stops
  a second push, and Google de-duplicates any repeat by transaction ID.

**R5 — Remove drafting notes and align the copy (A05).** Change only the text below:

| ID | Location | Current published text | Replace with |
|---|---|---|---|
| C1 | H2 "Permanent Lighting That Works Beyond Christmas", paragraph | "Apogee Lawns offers professional EverLights installation for homes and businesses in Lincoln and the approved surrounding service area. Reconfirm the current EverLights relationship and commercial availability before publication." | "Apogee Lawns offers professional EverLights installation for homes and businesses in Lincoln and the surrounding service area." |
| C2 | "How to Get Permanent Lights Installed" → step 2 supporting line | "Exact consultation steps and estimate timing require client confirmation." | delete |
| C3 | same section → step 3 supporting line | "Exact installation timing and handoff process require client confirmation." | delete |
| C4 | FAQ "Does Apogee install lights for both homes and businesses?" | "Apogee’s current service page describes residential and commercial lighting. Reconfirm availability for the campaign before publication." | "Yes. Apogee Lawns installs permanent lighting for homes and businesses." |
| C5 | FAQ "Do you serve my area?" | "...from Lincoln and the approved surrounding Nebraska service area. Submit your ZIP code or city so availability can be confirmed." | "Apogee Lawns serves Lincoln and nearby communities including Waverly, Eagle and Crete. Add your city or ZIP code to the form so we can confirm." |
| C6 | step 1 | the sentence "Complete the short form or call 402-526-5754 and tell Apogee Lawns about your property." is printed twice | keep one |
| C7 | FAQ "How much does permanent Christmas-light installation cost?" | "The estimate depends on the property and the scope of the lighting design. Request a free estimate so Apogee Lawns can review the project." | "Pricing is based on the linear footage of your roofline and the complexity of your home's architecture. Request a free estimate so Apogee Lawns can review the project." |

Sources for the replacement text:
- **C1 and C4:** Apogee's own site (apogeelawns.com/permanent-holiday-lights-lincoln-ne/, read 2026-10-05):
  "EverLights Certified Dealer" and "Installation Available for Homes & Businesses".
- **C7:** the same page's FAQ, read 2026-10-05.
- **C5:** the owner-approved service area.

No price, warranty, rating, review, Omaha or timing claim is added.

**R5b — Small form fixes.**
- **Required fields:** Full Name and Phone stay required. Make **Email optional**: phone is enough to follow up,
  and every required field costs mobile completions.
- **Add one optional "City or ZIP code" field,** which C5 and the second form's intro already ask for.
- **Autofill:** set `autocomplete` to `name`, `email`, `tel` and `postal-code`. They are empty today, which slows
  mobile entry.

**R6 — One form instance (A06).** Keep **one** form 1 instance on the page and give its section
`id="estimate"`. Point the sticky "Free Quote" button and every section call to action at `#estimate`. Duplicate
DOM IDs must reach 0 for form elements.

Also add stable section IDs, so sitelinks can deep-link to real content:
- `how-it-works` on "How to Get Permanent Lights Installed"
- `design` on "Lighting You Can Adjust for the Moment"
- `app-control` on "Permanent Lighting That Works Beyond Christmas"
- `faq` on "Frequently Asked Questions"
- `homes-businesses` on the card "Residential and Commercial Options"

**R7 — Attribution capture (A07).** A small first-party script, client-side only:

1. On every page load, read these URL parameters if present: `gclid`, `gbraid`, `wbraid`, `utm_source`,
   `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`.
2. Store them in a first-party cookie `apg_attr` (90 days, `SameSite=Lax`). When a new click ID arrives, it
   replaces the stored set.
3. On DOMContentLoaded, fill the form's hidden attribution fields from the stored set. Also fill:
   - the landing URL (path plus query; it never contains PII here)
   - `document.referrer`
   - consent state = `no_cmp`, because no consent platform exists. Whether one is needed is an owner/legal
     decision (register item A19).
4. Never render these values on the server.

The developer must send Green Marketing the **field map** (hidden field number → meaning). Do not assume
`input_9` to `input_15`.

**R8 — Lead delivery (A08).** Report:
- every Gravity Forms notification "To" address for form 1, by role only;
- the reply-to setting;
- whether entries also reach Service Autopilot.

WhatConverts already captures `gform_1`.

## C. Acceptance criteria (all must pass)

1. **One accepted entry = one lead:** 1 Gravity Forms entry, 1 WhatConverts lead, 1 notification to the intended
   recipient, 1 `apg_permanent_lights_lead` push.
2. **Lead ID:** unique, non-personal, ≤64 characters. The Google Ads tag sends it as the transaction ID.
3. **The correct tag fires:** "Google Ads | Lead | Permanent Lights Thank You" fires once and sends a request to
   `googleadservices.com/pagead/conversion/18453077620/` with label `KOL7CImirvocEPS8jt9E` and the transaction ID.
4. **Delivery** reaches the recipients named by the owner.
5. **Attribution survives submission:** the entry holds the test visit's own UTM values (and its click IDs, when a
   real ad visitor submits). A no-query visit shows **empty** hidden fields and an `action` with no query string,
   on two loads at least 2 minutes apart.
6. **No count for:** validation failures (empty phone), spam or honeypot entries, form starts, button clicks.
7. **No extra leads from:** a direct visit to the thank-you URL (no push), a refresh (no second push), or Back
   then Forward.
8. **Page content:** C1 to C7 changed as specified. "Reconfirm", "require client confirmation" and "approved
   surrounding" appear nowhere. One form instance; 0 duplicate form IDs; the section IDs above exist.
9. **Desktop 1440x900 and mobile 390x844:**
   - no overflow;
   - form fully visible;
   - sticky bar scrolls to `#estimate`;
   - `tel:` links dial 402-526-5754.

## D. Controlled tests (plan APG-1005-TEST; needs its own approval; not yet approval-ready)

Preconditions:
- R1 to R8 deployed and confirmed by a read-only browser check (criteria 5, 7, 8, 9).
- A Green Marketing test identity supplied through the approved secure method and added to `client.yaml`
  `qa_exclusions`, so test leads are excluded from every report.
- Tag Assistant / GTM Preview connected.

**Do not click live ads and do not create click IDs.**
- T1 desktop and T2 mobile: one test submission each from a direct visit. Record Preview evidence and network
  requests, with no PII in the logs, against criteria 1 to 7.
- T3: negative cases. Empty phone (validation error). Direct thank-you visit. Refresh. Button clicks without
  submitting.
- T4: one routing call to 402-526-5754 inside staffed hours (Mon–Fri 08:00–17:00, Sat 08:00–12:00 Central).
  - Expected: reaches the Apogee receptionist via 402-202-7261, and WhatConverts logs a "GSA Traffic" call with
    its duration.
  - Optional: one after-hours call to see the no-answer branch (register item A22).
- After the tests: mark the test leads as tests in WhatConverts. They are never counted as business results.

**What the tests can and cannot prove.** A direct test proves tag delivery, transaction-ID de-duplication and lead
delivery. It **cannot** produce an attributed Google Ads conversion, because no ad click is involved. Website-call
conversion 7773043879 therefore stays **Secondary** until a real ad visitor's call is matched in Google Ads and
WhatConverts. A 60-second call is a proxy, not proof of a permanent-lighting request.

## E. Lead handling the owner can actually run

To be confirmed by the owner; nothing here is a promise to customers.

1. **Who receives inquiries:** at least two named recipients for form notifications (owner and office). The
   receptionist answers 402-526-5754 through the call flow during staffed hours.
2. **Response target:** call back form leads the same business day during staffed hours. Return missed calls the
   same day, or first thing the next business morning.
3. **Missed and after-hours calls:** confirm what the call flow does on no answer. If it ends without voicemail,
   add voicemail.
4. **Hand-off to an estimate:** the person answering books the property review (step 2 on the page). They record
   the date in WhatConverts (lead notes or a custom field) or in Service Autopilot.
5. **Weekly 10-minute review in WhatConverts:** for every paid-funnel lead, record five outcomes:
   - **qualified request** (Yes when the person asked for permanent Christmas light installation; the owner's
     definition)
   - **estimate booked** (Y/N and date)
   - **sold job** (Y/N)
   - **revenue**
   - **gross profit**

   Spam and tests are marked as spam.
6. **Monthly:** Green Marketing reconciles these against Google Ads clicks and spend for CPL, CPQL, CAC, revenue,
   gross profit and profit after ad spend.

## F. What each fix is for

- **Measurement repairs:** R1, R2, R3, R4, R6 (form identity), R7, R8. They make leads countable and attributable.
  They create no inquiries by themselves.
- **Inquiry-generation improvements:** R5 (trust: removes the internal notes and answers the questions people
  ask), R5b (form friction), R6 (one clear form target), and the separate ad and asset bundles.
- **Sales follow-up:** section E. This is where an inquiry becomes a sold job.
