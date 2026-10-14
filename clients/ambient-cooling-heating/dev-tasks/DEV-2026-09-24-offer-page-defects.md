# Ambient — offer-site developer tasks (final, 2026-09-24)

Site: `https://offer.ambientcoolingandheating.com` (WordPress / Divi / Gravity Forms 2.9).
Only these items need WordPress. Everything else is done: tracking (GTM v16 live), GA4,
Google Ads migration and launch. The main-site NitroPack ticket is separate.

Before any change, keep a revision or copy of the page. After each change, purge the
SiteGround cache for that URL and tell Green Marketing, who retest the acceptance check.

| # | URL(s) | Fix | Acceptance check |
|---|---|---|---|
| **D2** (blocks 2 services) | `/boiler-installation/` and `/boiler-maintenance/` | Their content is swapped. Put boiler **installation** content and H1 "Boiler Installation in Central MD" on `/boiler-installation/`, and **maintenance** content with its H1 on `/boiler-maintenance/`. | Each page's H1 and every H2 name only its own slug's service. |
| **D1** (markup) | Divi Theme Builder **header**, used on all offer pages | The header button is `href="tel:(410) 705-6354"` but its label reads `CALL: (410) 761-0932`, and 761-0932 appears twice more in body text. Change all three to `(410) 705-6354`. GTM v16 masks this in the browser today; the markup must still be corrected. | View-source of any offer page contains 0 × `761-0932` and 0 × `914-1456`. |
| **D4** (copy) | `/heat-pump-installation/`, `/heat-pump-replacement/`, `/heat-pump-maintenance/` (H2 "Three Steps to Heat Pump **Repair**"); `/boiler-replacement/` (FAQ H2 "Heat Pump Repair Questions"); `/thermostat-replacement/` (final CTA button "Request a **Boiler Installation** Assessment") | Rename each to the page's own service. | Every H2 and CTA names only that page's service. |
| **D5** | every offer page | `form#gform_1` is rendered 3× (2 visible, 1 hidden), giving 54 duplicate DOM ids. Render one instance per page, or use distinct Gravity Forms per instance. **Tell Green Marketing before adding a form ID** (WhatConverts captures `#gform_1` = 205016 only). | 0 duplicate ids. One QA submission still creates exactly one WhatConverts lead. |
| **D6** | every offer page, field `input_1_7` | Label says "(optional)" but the field is required; the server rejects an empty message. Make the field optional (preferred) or remove "(optional)". | Label and validation agree. |
| **D7** | every offer page, hidden fields `input_1_9`–`input_1_26` | Attribution fields are filled on the server under the full-page SiteGround cache (`x-proxy-cache: HIT`), which replayed one visitor's gclid to others on 2026-09-15. Exclude offer pages from the proxy cache, **or** fill the fields in the browser from `location.search`. | A request with a unique marker parameter returns raw HTML with empty `value=` (or `x-proxy-cache: BYPASS`). A following request without the parameter never contains the marker. |

Not developer work, recorded for completeness:
- **D3 is fixed in GTM v16** (thank-you conversions need a confirmed successful submission) plus the GA4 rule. No page change is needed.
- The phone field forces US formatting. That's acceptable for a Maryland business.
