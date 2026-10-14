# DEV-R7A3-01 - Duplicate Gravity Form and duplicate HTML IDs

**Ticket ID:** DEV-R7A3-01 | **Priority:** P1 | **Raised:** 2026-09-02
**Client:** Softwind Power Washing | **Property:** offer.softwindli.com

## Business impact

Every offer page renders the customer form **twice** with **identical HTML IDs**.
`getElementById` returns only the first copy, so any analytics, dynamic-number-insertion or
accessibility tool that binds by ID binds to the wrong element. This is a live
tracking-reliability and accessibility defect on the pages that receive all paid traffic.

## Affected URLs

- `https://offer.softwindli.com/driveway-pressure-washing/`
- `https://offer.softwindli.com/house-pressure-washing-estimate/`
- `https://offer.softwindli.com/patio-power-washing/`
- `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
- `https://offer.softwindli.com/residential-pressure-washing/`
- `https://offer.softwindli.com/soft-house-washing/`

`/thank-you/` has no form but still carries 2 duplicate IDs.

## Exact observed behaviour

- `document.querySelectorAll('form#gform_1').length` is **2** on every offer page
- **22 duplicate HTML IDs per offer page**, including `gform_1`, `gform_wrapper_1`,
  `gform_fields_1`, `gform_submit_button_1`, `input_1_1`, `input_1_3`, `input_1_4`,
  `input_1_7`, `input_1_9`, the `field_1_*` set, `gform_theme_1`, and Divi's `et-boc`
- Copy 1 renders at roughly `top: 400px`, copy 2 at roughly `top: 5305px`
- Both copies are visible and both are functional

## Required behaviour

- Exactly **one** customer-facing form per page, **or** each additional instance carries a
  unique form ID and unique field IDs
- **Every HTML ID on the page is unique**
- The Gravity Forms honeypot (`input_9`, class `gfield--type-honeypot`) is **preserved, still
  hidden, and still empty** - it is the spam guard and must not be removed or exposed
- No layout or responsive regression on desktop or mobile

## Suggested search locations

The page template or Divi layout emitting the Gravity Forms block twice; a global
header/footer/sidebar module that also injects the form; a duplicated section in the page
builder.

## Acceptance criteria

- [ ] One `form#gform_1` per page, or all IDs unique
- [ ] Zero duplicate IDs, verified with a document-wide ID audit
- [ ] Honeypot present, `display:none`, value empty
- [ ] Form still submits successfully and still reaches `/thank-you/`
- [ ] Desktop and mobile layout unchanged

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
