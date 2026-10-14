TASK TITLE:

[P0] Softwind Power Washing — Google tag scoping and duplicate GTM load

TASK DESCRIPTION:

**Business impact:** `GTM-P3LD97NN` is bootstrapped **twice** per page, so every tag in
the container can fire twice — including Google Ads conversions. Separately, a second Google Ads
account's tag runs on these pages and occupies the call-tracking path.

**Affected URLs:** https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/ · https://offer.softwindli.com/residential-pressure-washing/ · https://offer.softwindli.com/house-washing-company/ · https://offer.softwindli.com/soft-house-washing/ · https://offer.softwindli.com/driveway-pressure-washing/ · https://offer.softwindli.com/patio-power-washing/ · https://offer.softwindli.com/thank-you/

**Current behavior:** 2 inline bootstraps, 2 `gtm.js` script tags, 2 `noscript` iframes, 6
occurrences of `GTM-P3LD97NN`; the dataLayer shows `gtm.js` twice. The browser de-duplicates the
network fetch, which is why a network-only check misses it. The two bootstraps differ in
whitespace, indicating two separate injectors.

Both `AW-18369652705` (correct) and `AW-17878095007` (Softwind Landscape & Masonry, customer
2429758629) load as async `gtag/js` tags. Neither ID appears as a literal `gtag('config', ...)`
in the page source.

**Required behavior:** GTM installed exactly once from one known place; dataLayer shows one
`gtm.js`; consent behaviour unchanged. **Report which two injectors you found.** Also confirm
whether each `AW-` tag is configured in GTM, hardcoded, or from a Site Kit / Google Ads plugin.

**Critical scope limits:** **preserve `AW-18369652705`.** **Do NOT remove `AW-17878095007`
globally** — it belongs to the sibling Softwind account and scoping it away from Power Washing
URLs needs that account owner's separate approval. This task only identifies the source.

**Acceptance criteria:** one bootstrap, one `gtm.js`, one `noscript` · dataLayer shows one
`gtm.js` · all existing tags still fire once · consent unchanged · both tag sources named · no tag
removed.

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

