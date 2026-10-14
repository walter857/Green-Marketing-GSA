# Ambient — offer-site developer list (2026-09-25)

Site: `https://offer.ambientcoolingandheating.com` (WordPress / Divi / Gravity Forms 2.9).
Supersedes `DEV-2026-09-24-offer-page-defects.md`. Rechecked live on 2026-09-25 in a real browser.

Before each change, keep a revision. After each change, purge the SiteGround cache for that URL
and send Green Marketing the URL. Green Marketing retests and runs the one QA form submission.
GTM is already installed (GTM-PQTPQ436). Do not add another container, pixel or WhatConverts script.

## A. Live core pages (paid traffic today). Do these first.

| # | URL(s) | Defect found 2026-09-25 | Required change | Acceptance test |
|---|---|---|---|---|
| D1 | Theme header + body on every offer page. Also `tel:` links to 761-0932 on `/hvac-repair/`, `/hvac-replacement/`, `/gas-boiler-repair/` | Raw HTML still prints (410) 761-0932 two or three times per page. Tag Manager v17 corrects it in the browser. | Show **(410) 705-6354** everywhere; every `tel:` link = `tel:+14107056354`. Do not add any script that rewrites phone numbers; WhatConverts must stay able to swap numbers. | View-source of any offer page contains 0 × `761-0932` and 0 × `914-1456`; every `tel:` is +14107056354. |
| D4 | `/heat-pump-installation/` | H2 "Three Steps to Heat Pump **Repair**"; FAQ H2 "Heat Pump **Replacement** Questions" | Name heat pump **installation** | Every H2/CTA names only that page's service. |
| D4 | `/heat-pump-replacement/` | H2 "Three Steps to Heat Pump **Repair**" | Name heat pump **replacement** | same |
| D4 | `/boiler-replacement/` | FAQ H2 "**Heat Pump Repair** Questions" | "Boiler Replacement Questions" | same |
| D4 | `/thermostat-repair/`, `/thermostat-replacement/` | CTA button "Request a **Boiler Installation** Assessment" | CTA names the page's thermostat service | same |
| D4 | `/smart-thermostat/` | CTA "Request Thermostat **Replacement**" | "Request Smart Thermostat Installation" (or similar) | same |
| D5 | every offer page | `form#gform_1` rendered 3× (2 visible, 1 hidden); 106 duplicate element IDs | One instance per page, or distinct Gravity Forms per placement. **Tell Green Marketing the new form IDs before publishing** (WhatConverts only captures the IDs registered in its form list). | 0 duplicate IDs; one QA submission from each visible placement creates exactly one WhatConverts lead. |
| D6 | every offer page, field `input_1_7` | Label says "(optional)" but the server rejects an empty value | Make it optional (preferred) or remove "(optional)" | Label and validation agree. |
| D7 | every offer page, hidden fields `input_1_9`–`input_1_26` | Proven today on the paused Commercial page: the server fills `input_1_13` from `utm_content` on a cache MISS, but a visitor whose URL carries only `utm_*` is served the shared cached copy (HIT) with empty fields. The visitor's own values are lost, and after any purge or expiry the first visitor with parameters seeds the shared copy for everyone. | Fill these fields **in the browser** from the current visitor's URL/cookies (not server-side), or exclude offer pages from the full-page proxy cache. | Two requests with different `utm_content` values each show their own value in the hidden field (inspect the DOM), and a clean request never shows either value. |
| C1 | every offer page | Both forms have no consent/privacy line near the submit button (a Privacy link exists in the footer only). | Owner to approve one short consent/privacy line under each submit button. | Line visible on desktop and mobile. |

## B. Next publication: Geothermal Heat Pump (funded $20/day Search test)

Publish **`/geothermal-heat-pump/`** (exact slug) on the existing offer landing-page template:
- Content: Google Doc "Ambient — Geothermal Heat Pump — Landing Page Content"
  (`1n7nnS6lCJBPtwPPWDwcRMawsXBfldiILo8co7PHlUwM`) in Drive → Ambient → Heating Services → Geothermal Heat Pump.
- Images: that folder's `Images` (4 files: geothermal-heat-pump-utility-room, geothermal-heat-pump-piping-detail,
  home-thermostat-comfort, comfortable-home-autumn).
- Phone: (410) 705-6354 only. Form: same fields as the other offer pages, one instance per page (see D5).
- noindex like the other offer pages. No redirect to the main site.

Acceptance: HTTP 200 on desktop and mobile; H1 and every H2 about geothermal; header and body phone
(410) 705-6354 matching the `tel:`; Green Marketing's QA submission reaches `/thank-you/` and creates
exactly one WhatConverts lead. Send the published URL. If the slug changes, tell Green Marketing
before anything else; the ads are built for this exact path.

## C. Core service blocked by content: Boiler Installation

| # | URL | Defect | Change | Acceptance |
|---|---|---|---|---|
| D2 | `/boiler-installation/` | Whole page is Boiler **Maintenance** content (H1 "Boiler Maintenance in Central MD") | Replace with the Boiler **Installation** package (Drive → Heating Services → Boiler Installation) | H1 "Boiler Installation in Central MD"; every H2/CTA about installation. |
| D2 | `/boiler-maintenance/` | H1 now says maintenance but the body is still Boiler **Installation** content | Replace the body with the Boiler Maintenance package | Every H2/CTA about maintenance. (Its ads stay paused; budget-deferred.) |

## D. Backlog. Not needed for this launch.

Keep these seven Drive packages (docs and images present, verified 2026-09-25). Do not publish
unless Green Marketing asks: Ductless Heating Repair, Ductless Heating Installation, Furnace
Maintenance, Furnace Tune-Up, Heating Maintenance, Heating Tune-Up, Heating System Inspection.
Their ads are paused by a budget decision; publishing a page does not change that.
