> **Revision 2026-09-28 (run D).** (1) Controlled-test side-effect wording corrected: Preview runs the real tags, so the
> earlier claim that reported conversions would be unaffected is withdrawn. (2) A tablet-scope note was added. (3) WhatConverts tracking of `gform_1` was confirmed
> from saved configuration. (4) EverLights wording was re-checked against the main site (read 2026-09-29 02:33 UTC):
> keep it. No other change to the contract or build steps.

# Apogee Lawns — permanent-lights form and content repair (developer handoff)

**Site:** `offer.apogeelawns.com` (WordPress, Divi, Gravity Forms, SiteGround) · **Prepared:** 2026-09-28 by Green
Marketing from read-only observation. Nothing here was changed by Green Marketing. Implementation belongs to the
developer team. Do not change the phone number (402-526-5754), offers, or any section not listed here.

## What we observed (read-only, 2026-09-28, America/Chicago)

| Fact | How it was established |
|---|---|
| Published pages: LP **183** `/permanent-christmas-lights-lincoln-ne/`, **1702** `/thank-you/`, 17395 `/terms-conditions/`, 3 `/privacy-policy/` | public WordPress REST API (page inventory) |
| **No page exists at `/thank-you/permanent-christmas-lights/`.** Requesting it returns the LP through WordPress's closest-slug redirect | page inventory + request probes (a random slug returns 404; `/permanent-christmas/` also redirects to the LP) |
| The LP renders **Gravity Forms form 1** (`id="gform_1"`) **three times**, one of them 0×0, creating 34 duplicate DOM IDs. Postback submission. Fields: Full Name*, Email*, Phone*, project notes (optional), a hidden honeypot, and hidden `input_9`–`input_15`, all empty on load | rendered-page inspection |
| No script on the LP, on `/thank-you/`, inline or in any of the 28 same-origin files pushes `apg_permanent_lights_lead` or `lead_id` | source scan |
| `/thank-you/` is live (noindex, GTM present, no dataLayer push). Google's tag-coverage report shows real visits to it | page fetch + GTM tag coverage |
| The LP HTML is served from a full-page cache (the form's state token was about 4 hours old at read time) | rendered-page inspection |
| WhatConverts tracks this form as "GF1" by element ID `gform_1` | WhatConverts configuration (read-only API) |

**Not verified:** where form 1's confirmation currently sends visitors. The traffic to `/thank-you/` is *consistent with*
it redirecting there, but no submission was made and the Gravity Forms settings were not visible to us.

## Please confirm before building (answers change details, not the plan)

- **D-Q1** Which Gravity Forms form ID(s) render on the paid LP? We observed form 1 three times.
- **D-Q2** Form 1's current confirmation: type (text, page or redirect) and target.
- **D-Q3** The lead-ID format you will ship. The Gravity Forms entry ID is preferred if it suits.
- **D-Q4** What hidden fields 9–15 are for (merge tags or dynamic-population parameter names).
- **D-Q5** Where accepted leads go today: notification emails, Service Autopilot or another CRM.
- **D-Q6** Which caching layers run: SiteGround Speed Optimizer / Dynamic Cache, any CDN HTML cache.
- **D-Q7** Which spam protection is active: honeypot (observed), reCAPTCHA, Akismet or other.

## The contract (do not weaken)

1. The paid-page form accepts a valid, non-spam submission **server-side**.
2. The accepted lead gets a **unique, non-PII ID from the form system**. Prefer the existing Gravity Forms entry ID; do not
   invent a second ID system.
3. The browser then reaches the dedicated page `https://offer.apogeelawns.com/thank-you/permanent-christmas-lights/`.
4. That page load has access to the accepted lead's ID.
5. The page pushes, once per load,
   `window.dataLayer.push({event: 'apg_permanent_lights_lead', lead_id: '<ID>'})`, on hostname `offer.apogeelawns.com`
   and path `/thank-you/permanent-christmas-lights/`.
6. The existing Google Ads form-conversion tag (conversion ID 18453077620, label KOL7CImirvocEPS8jt9E) then fires with
   that ID as the transaction ID. It is already built and published; nothing to do in GTM for this step.
7. Refreshes or repeated callbacks for the same accepted lead carry the **same** ID. Two accepted leads never share an ID.

Never replace this with a button click, a form attempt, or an unrestricted thank-you page view.

## Build steps

**D1 — Dedicated confirmation page.** Publish `/thank-you/permanent-christmas-lights/` as a child of page 1702, slug
`permanent-christmas-lights`. Requirements:
- `noindex`; the same header, footer and GTM container as the LP; phone 402-526-5754; **no form**.
- It must return HTTP 200 directly, with no redirect.
- Used only for this paid funnel.

**D2 — Caching.** Exclude the LP and the new page from full-page, dynamic and CDN HTML caching. A cached thank-you page
would replay one visitor's ID to others.

**D3 — Confirmation routing.** For accepted, non-spam entries of the paid-page form, redirect to D1 and carry the ID
across the redirect. A dataLayer value does **not** survive a page load on its own, so the ID must travel in the redirect
itself. Example query string: `?lead=<entry ID>&t=<token>`.
- Generate `t` server-side at confirmation time, for example an HMAC of the entry ID and entry timestamp using a site
  secret, so a hand-typed or edited URL cannot create a conversion.
- Gravity Forms shows its confirmation to submissions it has flagged as spam, so the redirect must **not** carry an ID or
  token for spam, validation failures or server errors.
- If form 1 is also embedded anywhere else, apply this redirect only when the submission came from the paid LP.

**D4 — Server-rendered event.** When D1 loads, verify on the server that:
- the token matches the ID;
- the entry exists, belongs to the paid-page form and is not spam;
- the entry is recent, for example under 30 minutes old (your choice; state it).

If all checks pass, output
`<script>window.dataLayer=window.dataLayer||[];window.dataLayer.push({event:'apg_permanent_lights_lead',lead_id:'<ID>'});</script>`
with the ID properly escaped. If any check fails, output nothing (the thank-you text still shows).
- A refresh inside the window pushes the same ID; Google counts it once per conversion action and transaction ID.
- After the window, nothing is pushed, which stops stale reuse from bookmarks or browser history.

**D5 — ID rules.** The ID must be:
- unique per accepted lead and stable for that lead;
- non-PII;
- available when the event is pushed;
- different for every accepted lead.

Never send: empty or whitespace, `undefined` or `null` as values or strings, a fixed or example value, an unreplaced merge
tag, or a reused ID. Never put name, email, phone, ZIP or notes in the URL or the dataLayer.

**D6 — Attribution capture** (only if fields 9–15 are meant for it; D-Q4).
- Populate these **client-side** on the LP from the landing URL: `gclid`, `gbraid`, `wbraid`, plus the campaign's own
  parameters `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `utm_matchtype`, `utm_device`,
  `utm_network`, `utm_adgroup`, and the landing-page URL.
- Keep first-touch values in a first-party cookie (for example 90 days) so they survive navigation.
- Leave a field blank when a value is absent; never invent one.
- Never render these server-side into cached HTML.
- No consent banner or platform exists on the site today. If the owner or legal counsel requires one, capture must follow
  it; that decision is not ours.

**D7 — Delivery and WhatConverts.** Accepted entries must still reach the approved destination (D-Q5), and WhatConverts
must still record them. It matches the element ID `gform_1`, so if the form's HTML ID changes, tell us so the tracked-form
list can be updated.

**D8 — One form identity.** Reduce the three form-1 instances to one visible instance, or make each instance uniquely
identifiable, so that one submission produces one entry, one WhatConverts lead and one event.

## Content corrections (LP page 183) — remove internal notes visible to prospects

The EverLights wording itself is supported. Apogee's own site (`apogeelawns.com/permanent-holiday-lights-lincoln-ne/`, read
2026-09-28) states "EverLights Certified Dealer" and "Apogee Lawns is a certified EverLights dealer and installer…", and it
advertises installation for homes and businesses. Keep the EverLights app references; remove only the notes.

| # | Location | Current text (complete) | Replace with |
|---|---|---|---|
| C1 | Section H2 **"Permanent Lighting That Works Beyond Christmas"**, paragraph under the intro | "Apogee Lawns offers professional EverLights installation for homes and businesses in Lincoln and the approved surrounding service area. Reconfirm the current EverLights relationship and commercial availability before publication." | "Apogee Lawns offers professional EverLights installation for homes and businesses in Lincoln and the surrounding service area." (removes the note and the internal word "approved") |
| C2 | Section H2 **"How to Get Permanent Lights Installed"** → step **"2. Review Your Lighting Plan"**, supporting line (`.step-callback`) | "Exact consultation steps and estimate timing require client confirmation." | Delete. If the layout needs a line: "Discuss the areas, colors, and lighting options you want." (restates the step's existing text; no new claim) |
| C3 | Same section → step **"3. Professional Installation"**, supporting line (`.step-callback`) | "Exact installation timing and handoff process require client confirmation." | Delete. If the layout needs a line: "Professional installation for homes and businesses." |

Acceptance: none of the strings "Reconfirm", "require client confirmation" or "approved surrounding" appears anywhere in
the rendered LP, on desktop or mobile.


## Out of scope for this handoff

- **Tablet layout.** The owner excludes tablets from the ads because the landing pages are not tablet optimized. No
  tablet work is requested here. Any future tablet layout fix would be a separate task with its own QA.
- Phone numbers, offers, and any section not listed above.

## Acceptance tests

The full matrix is in `03_form_acceptance_matrix.csv`. After deployment, Green Marketing runs them in **GTM Preview**,
which does not publish anything, together with the one controlled submission requested below.

## Controlled end-to-end test request (separate approval — not performed)

- **When:** after D1–D5 are live. Requested approval line: `APPROVE APG E2E FORM TEST`.
- **Steps:**
  1. Open GTM Preview on the LP. Do not click an ad and do not add a click ID.
  2. Submit **one** form using a Green Marketing-controlled test identity supplied through the approved secure method,
     labelled "GM QA TEST" in the notes.
  3. Refresh the confirmation page once.
  4. Open the confirmation URL once more with the token removed.
- **Expected:**
  - one entry;
  - a redirect to D1 with one `apg_permanent_lights_lead` event carrying the entry's ID;
  - one conversion request carrying that transaction ID;
  - on refresh, the same ID;
  - without the token, no event.
- **Side effects:** Preview runs the real, published tags. The test **will** create:
  - one Gravity Forms entry;
  - one Apogee notification (warn staff first);
  - one WhatConverts web-form lead;
  - tag hits in Google's systems, including a conversion request.

  Without a click ID, Google Ads should not attribute that conversion to the campaign, but this is **not guaranteed and
  is not promised**.
- **Safeguards:**
  - record the exact test time and the entry ID;
  - label the notes "GM QA TEST";
  - mark the WhatConverts lead as spam or QA;
  - exclude that time window and ID from reporting;
  - check the Google Ads conversion columns over the following days and document any recorded test conversion instead
    of deleting anything.
- **Afterwards:** deleting the entry or lead needs a separate destructive-action approval.
