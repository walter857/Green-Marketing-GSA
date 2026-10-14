# DEV-R7A3-05 - Identify the injection source of both Google Ads tags

**Ticket ID:** DEV-R7A3-05 | **Priority:** P1 | **Raised:** 2026-09-02
**This ticket is INVESTIGATION ONLY. Do not remove any tag.**

## Business impact

Two different Google Ads accounts are tagged on the Power Washing pages. One of them belongs to
a **different Softwind account** and is currently occupying the Power Washing call-tracking
path. Green Marketing cannot correct it until the injection source is known, and has no access
to the GTM container.

## Affected URLs

- `https://offer.softwindli.com/driveway-pressure-washing/`
- `https://offer.softwindli.com/house-pressure-washing-estimate/`
- `https://offer.softwindli.com/patio-power-washing/`
- `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
- `https://offer.softwindli.com/residential-pressure-washing/`
- `https://offer.softwindli.com/soft-house-washing/`
- `https://offer.softwindli.com/thank-you/`

## Exact observed behaviour

Both tags load as async `gtag.js` script tags:

```
https://www.googletagmanager.com/gtag/js?id=AW-18369652705&cx=c&gtm=4e68v1   <- correct account
https://www.googletagmanager.com/gtag/js?id=AW-17878095007&cx=c&gtm=4e68v1   <- sibling account
```

Each ID appears **exactly once** in the rendered source, and **only inside that injected script
URL**. There is no literal `gtag('config','AW-17878095007', ...)` anywhere in the page HTML.
That pattern is consistent with GTM or a Google tag linked destination, not a hardcoded
snippet.

## What we need from you

Please confirm which of these is true, naming the file or setting:

1. Both tags are configured inside GTM container `GTM-P3LD97NN`
2. One or both are hardcoded in the theme, a child theme, `functions.php`, an mu-plugin or a
   tag plugin
3. One or both come from a Google Site Kit or Google Ads plugin configuration
4. Something else - please describe

## Explicitly out of scope

**Do not remove `AW-17878095007` globally.** It legitimately belongs to Softwind Landscape and
Masonry and may be required on that brand's own pages. Scoping it away from Power Washing URLs
needs a separate approval from that account's owner, which Green Marketing is arranging.

## Acceptance criteria

- [ ] Injection source named for `AW-18369652705`
- [ ] Injection source named for `AW-17878095007`
- [ ] Confirmation of whether the same GTM container also serves the Masonry brand's pages
- [ ] No tag removed or modified under this ticket

## Rollback

Restore the previous template or plugin revision. No data migration is involved.

## Evidence paths

- `clients/softwind-power-washing/snapshots/r7a-public-code-inspection-2026-09-02T115916.json`
- Saved rendered source: `clients/softwind-power-washing/snapshots/r7a-page-source-2026-09-02/`
- `clients/softwind-power-washing/audits/2026-09-02-r7a-page-code-inspection.csv`
- `clients/softwind-power-washing/receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md`

## Developer completion checklist

- [ ] Root cause identified and named (file, plugin, template or setting)
- [ ] Change applied on staging first
- [ ] Desktop QA passed
- [ ] Mobile QA passed
- [ ] Tracking QA passed, network capture attached
- [ ] Regression check on every affected URL
- [ ] Rollback path confirmed
- [ ] Evidence attached to this ticket

## Developer signoff

Name: ______________________  Date: ____________  Release or commit: ______________________
