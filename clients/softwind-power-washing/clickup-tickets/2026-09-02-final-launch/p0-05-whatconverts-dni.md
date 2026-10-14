TASK TITLE:

[P0] Softwind Power Washing — WhatConverts DNI and call attribution

TASK DESCRIPTION:

**Business impact:** WhatConverts attribution works but its number replacement never
reaches the page, so paid calls cannot be attributed. Meanwhile the sibling Google Ads account
runs its own website-call replacement on Softwind's number.

**Affected URLs:** https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/ · https://offer.softwindli.com/residential-pressure-washing/ · https://offer.softwindli.com/house-washing-company/ · https://offer.softwindli.com/soft-house-washing/ · https://offer.softwindli.com/driveway-pressure-washing/ · https://offer.softwindli.com/patio-power-washing/ · https://offer.softwindli.com/thank-you/

**Current behavior:** the WhatConverts script loads from
`s.ksrndkehqnwntyxlhgto.com/158931.js` (WordPress plugin, handle
`whatconverts-tracking-script-js`). `wc_client` correctly carries source, medium, campaign,
content, term and the GCLID. `wc_swap` nominates 6315025402 and 6315535927 — **neither reaches
the DOM**; the page renders the static (631) 502-7946 in both body text and the `tel:` href.
Separately, `conversion/17878095007/wcm` fires on all 7 pages while
`conversion/18369652705/wcm` fires on **none**.

**Required behavior:** determine why DNI does not execute, then implement ONE authoritative call
architecture. Do not run Google website-call replacement and WhatConverts DNI on the same
displayed number.

**Implementation file path:** WhatConverts account configuration (profile appears to be
`158931`) plus the WordPress plugin that enqueues the script.

**Blocked on Green Marketing:** an authenticated WhatConverts read. The API token in our
environment is empty. **Do not paste any credential into a ticket or chat** — populate
`WHATCONVERTS_API_TOKEN` in the secure local environment, or grant a read-only WhatConverts user.

**Acceptance criteria:** DNI root cause documented · one system owns the displayed number · no
double replacement · `wc_client` attribution preserved · GCLID preserved.

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

