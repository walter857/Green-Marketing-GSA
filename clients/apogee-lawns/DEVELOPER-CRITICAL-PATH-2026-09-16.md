# Apogee Lawns — developer critical path

**Site:** apogeelawns.com (WordPress + Elementor 4.2.4) · **Developer of record:** siliconprairiemarketing.com
**Container to install:** `GTM-M545Z8T2` (container name `apogeelawns.com`)
**Prepared 2026-09-16.** Every item below was verified live on that date.

Nothing here is a Google Ads change. This is website and tag work that must land before
any conversion measurement, GTM draft, or campaign launch is possible.

---

## D1 — Install GTM-M545Z8T2 sitewide  *(blocks everything)*

**Current state:** `0` GTM containers, `0` Google tags, `0` GA4, `0` `gtag(`, `0` `dataLayer`
across the home page, `/permanent-holiday-lights-lincoln-ne/`,
`/lawn-care-lighting-estimates-lincoln-ne/`, `/contact/` and `/privacy-policy/`.
All **17** enqueued same-origin JS files were fetched and grepped — none reference a
container. Installed plugins are astra-sites, elementor, forminator, header-footer-elementor,
wp-smushit: **no tag-management or analytics plugin exists**, so nothing can inject one.

- [ ] Install `GTM-M545Z8T2` on **every** page, including the 404 template.
- [ ] Head script as high in `<head>` as possible.
- [ ] `<noscript>` iframe **immediately** after the opening `<body>` tag.
- [ ] Do **not** install a second container.
- [ ] Do **not** hardcode a Google tag, GA4 tag or Ads tag — everything goes through GTM.
- [ ] Confirm on desktop **and** mobile with Tag Assistant.
- [ ] Confirm the container also loads on the new PPC page and the new thank-you page.

## D2 — Build the PPC landing page

**Current state:** `https://apogeelawns.com/permanent-christmas-lights-lincoln-ne/` → **404**.

- [ ] Publish at exactly `/permanent-christmas-lights-lincoln-ne/` (trailing slash).
- [ ] Content, headings, sections and image slots from Drive doc
      `01 - LIVE ACCOUNT DRAFT - Landing Page Content - Permanent Christmas Lights - Lincoln NE`.
- [ ] Visible phone **402-526-5754** in header, hero, form area, sticky mobile control and footer.
- [ ] Every phone link `tel:+14025265754`.
- [ ] **Do not** change the sitewide number. `402-202-7261` stays everywhere else.
- [ ] Keep `402-526-5754` confined to this paid funnel (landing page + thank-you page).
- [ ] Working **Privacy Policy** link → `/privacy-policy/` exists.
- [ ] Working **Terms and Conditions** link → **does not exist yet.** `/terms/`,
      `/terms-and-conditions/` and `/terms-of-service/` all return 404 and nothing appears
      in `page-sitemap.xml`. This page has to be created or the link removed from the spec.
- [ ] Client-approved form, SMS and phone consent language.
- [ ] Decide indexing against the existing organic page
      `/permanent-holiday-lights-lincoln-ne/` — `noindex, follow` or a canonical, so the two
      do not compete.
- [ ] Test desktop and mobile.

## D3 — Build the dedicated thank-you page

**Current state:** `https://apogeelawns.com/thank-you/permanent-christmas-lights/` → **404**.

- [ ] Publish at exactly `/thank-you/permanent-christmas-lights/`.
- [ ] `noindex, follow`.
- [ ] Returns HTTP 200. URL is permanent — a later change invalidates the GTM trigger and
      every conversion recorded against it.
- [ ] **No lead form on this page.**
- [ ] Not reachable by any other service's form. This URL must mean exactly one thing.
- [ ] GTM loads here.
- [ ] Content from the Drive landing-page document, section 13.

## D4 — Build a dedicated PPC form  *(do not reuse the current one)*

**Current state — why reuse fails all three tests:**

| Requirement | Current Forminator module `1611` |
|---|---|
| Dedicated to this funnel | **No.** One shared module is used on every page sitewide. |
| Redirects to a success URL | **No.** `redirect_url` is the page's own URL on every page — home → `/`, `/contact/` → `/contact/`. There is no success URL anywhere on the site. |
| Exposes a unique lead ID | **No.** No `entry_id`, `lead_id` or `submission_id` is exposed. |

- [ ] Create a **separate** form used only on `/permanent-christmas-lights-lincoln-ne/`.
- [ ] Fields per the Drive document: First Name, Phone, Email, ZIP, Property Type
      (Home/Business), optional project notes.
- [ ] **Omit** street address, a general service selector, and "How did you hear about us?" —
      all three are on the current shared form and none belong here.
- [ ] Redirect to `/thank-you/permanent-christmas-lights/` **only** after the form platform
      confirms a successful, server-accepted submission.
- [ ] Never redirect on validation failure, abandonment, spam/reCAPTCHA rejection or server error.
- [ ] Deliver the lead to the correct owner or pipeline (Service Autopilot is linked from the
      live site — confirm the intended destination).
- [ ] Capture and persist through submission: **GCLID, GBRAID, WBRAID**, the approved UTMs,
      consent state, submission timestamp.
- [ ] Generate a **real unique lead ID** and expose it on the success page or in the data layer.
      Never a static or fabricated value. If the platform cannot do this, say so — we will
      ship without transaction-ID deduplication and document the limitation rather than fake it.
- [ ] Keep names, emails, phone numbers, ZIPs and project notes **out of** URLs and analytics
      parameters.

> **Page-cache warning.** If click IDs are captured by server-rendering them into hidden
> fields, a full-page cache will replay one visitor's GCLID to everyone. Populate hidden
> fields **client-side** from the live URL, and exclude the PPC landing page and thank-you
> page from full-page caching.

## D5 — Phone verification  *(not a code task — needed from the owner)*

**Current state:** `402-526-5754` appears **0 times** anywhere on the site.

- [ ] Confirm Apogee controls the number and it is approved for paid use.
- [ ] Confirm where it rings, voicemail behaviour, and who answers.
- [ ] Confirm live-answer hours in **Central Time** — these set both the ad schedule and the
      call-asset schedule. We will not assume 24/7.

## D6 — Billing  *(authorized person only)*

Both billing setups on `8164626278` are **CANCELLED** (`8584340188`, `8584421311`, both
created 2026-09-15) and there is no active account budget. The account cannot serve.
Green Marketing must not select a payment profile, add a payment method, accept billing
terms, or change billing ownership. Once an authorized person restores billing we will
re-read it and record the result.

---

## Ready-for-tracking gate

GTM draft work starts only when **all** of these are true:

- [ ] `GTM-M545Z8T2` returns on the landing page and thank-you page in Tag Assistant
- [ ] `/permanent-christmas-lights-lincoln-ne/` returns 200
- [ ] `/thank-you/permanent-christmas-lights/` returns 200
- [ ] A real test submission reaches the thank-you URL, and a deliberate validation failure does not
- [ ] `402-526-5754` is visible and every `tel:` link is `+14025265754`
- [ ] Phone ownership, routing and answer hours confirmed
- [ ] Still no competing DNI system (none today — keep it that way)
- [ ] Privacy Policy and Terms links both resolve
- [ ] Stage A conversion actions exist, with their real Conversion ID and Label captured
