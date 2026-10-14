# DEV-R7A3-03 - Google Tag Manager container installed twice

**Ticket ID:** DEV-R7A3-03 | **Priority:** P1 | **Raised:** 2026-09-02

## Business impact

`GTM-P3LD97NN` is **bootstrapped twice** in the delivered HTML. Two container instances
initialise, so **every tag in the container can fire twice** - including Google Ads
conversions. This is a latent double-counting mechanism sitting directly under the account's
conversion measurement.

## Affected URLs

- `https://offer.softwindli.com/driveway-pressure-washing/`
- `https://offer.softwindli.com/house-pressure-washing-estimate/`
- `https://offer.softwindli.com/patio-power-washing/`
- `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
- `https://offer.softwindli.com/residential-pressure-washing/`
- `https://offer.softwindli.com/soft-house-washing/`
- `https://offer.softwindli.com/thank-you/`

## Exact observed behaviour - cause confirmed from public source

In the delivered HTML of every page:

| Artifact | Count |
|---|---:|
| Inline bootstrap `(window,document,'script','dataLayer','GTM-P3LD97NN')` | **2** |
| `<script src=".../gtm.js?id=GTM-P3LD97NN">` tags | **2** |
| `<noscript>` `ns.html?id=GTM-P3LD97NN` iframes | **2** |
| `GTM-P3LD97NN` string occurrences | **6** |
| `dataLayer` entries after load | `gtm.js`, **`gtm.js`**, `gtm.dom`, `gtm.load` |

**Cause: the container snippet appears twice in the delivered HTML.** The two inline bootstraps
differ in whitespace, which indicates **two different injectors** - most likely a theme or
header setting plus a plugin such as Site Kit, a GTM plugin, or a custom-code block.

The browser de-duplicates the *network* fetch to a single `gtm.js`, which is why a network-only
check misses this. **The dataLayer proves both bootstraps ran.**

## Required behaviour

- `GTM-P3LD97NN` is installed **exactly once**, intentionally, from one known place
- No second bootstrap and no second `noscript` iframe
- Existing consent behaviour remains intact
- `dataLayer` shows exactly one `gtm.js` entry

## Suggested search locations

Theme options header scripts; a GTM, Site Kit or header-footer plugin; a custom code block in
the page builder; `wp_head` injection from the child theme.

**Please report which two sources you found - Green Marketing needs to know which one to keep.**

## Acceptance criteria

- [ ] Exactly one inline bootstrap, one `gtm.js` tag, one `noscript` iframe
- [ ] `dataLayer` contains one `gtm.js` entry
- [ ] All existing tags still fire exactly once
- [ ] Consent behaviour unchanged

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
