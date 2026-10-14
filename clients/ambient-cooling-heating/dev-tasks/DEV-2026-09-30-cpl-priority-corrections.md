# Ambient: priority corrections for the CPL requirement (revised 2026-09-30c)

Site: `https://offer.ambientcoolingandheating.com` (WordPress, Divi, Gravity Forms 2.9, SiteGround proxy cache).
The client requires CPL of $280 or less, with a hard ceiling of $350. Lead capture on the pages that receive
paid traffic is the lever, not lower bids.

**Nothing here is authorized yet.** No website, GTM, WhatConverts, call-asset or conversion change may be made
until Green Marketing approves that exact change.

**A page loading is not a pass.** Each item passes only on its acceptance test, run in a real browser on desktop
and mobile.

## Order: paid landing pages first

These pages receive paid clicks today:
- `/furnace-repair/`, `/no-heat-repair/`
- `/hvac-installation/`, `/hvac-replacement/`
- `/gas-boiler-repair/`, `/boiler-replacement/`
- `/heat-pump-repair/`, `/heat-pump-installation/`, `/heat-pump-replacement/`
- `/thermostat-repair/`, `/thermostat-replacement/`, `/smart-thermostat/`
- `/hvac-repair/` until the Heating Repair containment executes

D6, D5, D7 and D1 apply to every one of them, so they come first. D4 on `/boiler-replacement/` (a paid page) comes
before D4 and D2 on pages with no paid traffic (`/heat-pump-maintenance/`, `/boiler-maintenance/`, `/boiler-installation/`).

| Priority | Item | Finding (2026-09-30) | Required change | Acceptance test |
|---|---|---|---|---|
| 1 | **D6** optional message field | `field_1_7` "Tell us about your project (optional)*" carries `gfield_contains_required` and `aria-required="true"`. | Make the field truly optional. | From **each visible form placement**, desktop and mobile, submit with the message field **genuinely empty**: nothing typed, no whitespace, no placeholder text. The submission reaches `/thank-you/`, shows no validation error, and creates **exactly one** WhatConverts lead. |
| 2 | **D5** repeated forms, duplicate IDs | `form#gform_1` rendered 3× per page, 55 duplicate IDs. | One form instance per page, or distinct Gravity Forms per placement. **Tell Green Marketing any new form ID before publishing**, because WhatConverts captures only listed IDs (205016 `#gform_1`, 208722 `#gform_2`). | 0 duplicate IDs. One submission per visible placement creates exactly one WhatConverts lead with the correct form ID. |
| 3 | **D7** visitor-specific attribution | Hidden fields `input_1_9`–`input_1_26` are filled on the server under the full-page cache. A unique-parameter request echoed its marker on a cache MISS. | Fill the fields in the browser from the visitor's own URL, and store them first-party (cookie or localStorage, up to 90 days) so the same browser keeps its attribution. Or exclude these pages from the proxy cache and fill from that first-party store. | **Isolation:** visitor A (browser 1, `?gclid=A…&utm_content=A`) and visitor B (browser 2, no parameters) load the page; B's fields are empty. **Returning visitor:** A returns in browser 1 later with no parameters; A's fields still carry A's values. **No leakage:** a third clean browser never shows A's values. Tests must use a unique non-UTM cache-buster and isolated browsers. |
| 4 | **D1** phone number in source | Raw HTML has (410) 761-0932 two or three times per page. `/gas-boiler-repair/` has `href="tel:+14107610932"`. `tel:` hrefs are not E.164. | Visible base number (410) 705-6354, every base `tel:` = `tel:+14107056354`. **WhatConverts dynamic number insertion must keep working:** its swap rule 230773 currently looks for 761-0932, so it must be retargeted to the new base number in the same release (a WhatConverts change that needs its own approval). Otherwise the swap stops silently. | View-source shows 0 × 761-0932. With WhatConverts **blocked**, every link shows and dials 705-6354. With WhatConverts **active**, the swap still happens (`wc_swap` cookie set, the approved DNI number shown), and each `tel:` href matches its visible number. |
| 5 | **D4** service copy on a paid page | `/boiler-replacement/` FAQ H2 "Heat Pump Repair Questions". | Rename it to the page's own service. | Every H2 and CTA names only that page's service. |
| 6 | **D4 / D2** pages without paid traffic | `/heat-pump-maintenance/`: 3 mismatches. `/boiler-maintenance/` and `/boiler-installation/`: content swapped. | As listed on 2026-09-25. | Same test as D4. |

## QA suppression must cover WhatConverts uploads, not only GTM

GTM v16 suppresses Google Ads, UET and GA4 events for QA submissions. But WhatConverts' own Google Ads integration
uploads every lead with a phone number or email on "New Lead Received", enhanced conversions included. That is why
earlier QA leads were accepted as WC Lead uploads.

**Proposed** (a conversion-configuration change; needs its own approval): stop QA leads reaching Google before
upload. For example, upload only on a qualified or quotable status the QA identity never receives, or use an
equivalent WhatConverts exclusion.

**Acceptance:** for a QA submission, the WhatConverts lead detail shows no successful Google Ads send, and Google Ads
shows 0 conversions of any action for it by conversion date.

## Account-side items (Green Marketing; each needs its own approval)

1. **Call path.** Keep call asset `424764337810` (410-415-9517) paused on the held campaigns until one genuine ad
   call is proven end to end: it routes to 761-0932, WhatConverts records it as WC Calls, Google has a matching call
   record, and there is no second WC Lead upload.
2. **Untracked location-asset calls.**
   - Five Google call records (Aug 24 ×2, Aug 27, Sept 25, and Sept 30 provisional) have no WhatConverts call on any number.
   - Four came on days with location clicks and no call-button clicks. Today's came with one charged call click while both call-asset links on the campaign are paused.
   - These calls reach a number WhatConverts doesn't track.
   - Verify the Google Ads phone override on all three linked Business Profile locations (Business Profile UI only).
