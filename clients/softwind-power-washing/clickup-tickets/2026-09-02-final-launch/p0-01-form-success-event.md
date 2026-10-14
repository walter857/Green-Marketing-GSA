TASK TITLE:

[P0] Softwind Power Washing — Add verified form-success dataLayer event

TASK DESCRIPTION:

**Business impact:** a direct visit to `/thank-you/` currently fires a Google Ads
conversion with no form submission. Verified twice by loading the URL cold. Once real ad clicks
convert, the Conversions column will count visitors arriving from history, bookmarks or crawlers.
The account has ZERO conversions today, so every future number depends on fixing this first.

**Affected URL:** https://offer.softwindli.com/thank-you/ plus all six offer pages.

**Current behavior:** loading `/thank-you/` directly fires
`GET googleadservices.com/pagead/conversion/18369652705/ en=conversion` and
`GET google.com/pagead/1p-conversion/18369652705/ en=conversion`. The six offer pages fire zero
on load, which localises the trigger to the page path. The dataLayer contains only `gtm.js`,
`gtm.dom`, `gtm.load` — no custom event exists.

**Required behavior:** push, only after a confirmed successful Gravity Forms submission:

```js
dataLayer.push({ event: "gm_power_washing_form_success", form_id: "1" });
```

Must fire exactly once per successful submission. Must NOT fire on form start, submit-click
alone, validation failure, a direct `/thank-you/` visit, refresh, or back navigation.

**Implementation file path:** Gravity Forms confirmation settings for form ID 1, or the
`gform_confirmation` / `gform_after_submission` filter in the theme or a custom plugin. If the
redirect is the only success point, pass a single-use token consumed on first read.

**Acceptance criteria:** event fires once on a real submission · direct `/thank-you/` visit
pushes no event and fires no conversion · refresh and back navigation fire nothing · validation
failure fires nothing · event carries `form_id` · identical on desktop and mobile.

**Dependencies:** none. **Do not change any Google Ads tag** — Green Marketing repoints the
trigger after this ships.

**Evidence:** `snapshots/r7a-public-code-inspection-2026-09-02T115916.json`,
`receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md`

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

