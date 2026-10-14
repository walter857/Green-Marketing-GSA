TASK TITLE:

[P0] Softwind Power Washing — Fix duplicate form and duplicate HTML IDs

TASK DESCRIPTION:

**Business impact:** every offer page renders `form#gform_1` twice, producing **22
duplicate HTML IDs** per page. `getElementById` returns only the first copy, so any analytics,
dynamic-number-insertion or accessibility tool binding by ID binds to the wrong element.

**Affected URLs:** https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/ · https://offer.softwindli.com/residential-pressure-washing/ · https://offer.softwindli.com/house-washing-company/ · https://offer.softwindli.com/soft-house-washing/ · https://offer.softwindli.com/driveway-pressure-washing/ · https://offer.softwindli.com/patio-power-washing/ · https://offer.softwindli.com/thank-you/

**Current behavior:** `document.querySelectorAll('form#gform_1').length === 2`. Duplicated IDs
include `gform_1`, `gform_wrapper_1`, `gform_fields_1`, `gform_submit_button_1`, `input_1_1`,
`input_1_3`, `input_1_4`, `input_1_7`, `input_1_9`, `field_1_*`, `gform_theme_1`, `et-boc`.
Copy one at ~400px, copy two at ~5305px. Both visible and functional.

**Required behavior:** exactly one customer-facing form per page, or unique form and field IDs
per instance. Every HTML ID unique. **The Gravity Forms honeypot `input_9`
(`.gfield--type-honeypot`) must remain present, hidden and empty** — it is the spam guard.

**Implementation file path:** the page template or Divi layout emitting the Gravity Forms block
twice, or a global header/footer/sidebar module that also injects it.

**Acceptance criteria:** one `form#gform_1` · zero duplicate IDs verified by a document-wide
audit · honeypot present, `display:none`, empty · form still submits and reaches `/thank-you/` ·
no layout regression.

**Dependencies:** none.
**Evidence:** `snapshots/r7a-public-code-inspection-2026-09-02T115916.json`

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

