# DEV-R7A3-04 - Add a verified form-success dataLayer event

**Ticket ID:** DEV-R7A3-04 | **Priority:** **P0** | **Raised:** 2026-09-02

## Business impact - the highest-priority measurement defect

**A direct visit to `/thank-you/` fires a Google Ads conversion with no form submission.**
Proven twice by loading the URL cold. The conversion is bound to the page path, not to a real
lead.

Once genuine ad clicks start converting, the Conversions column will count visitors who reach
`/thank-you/` from browser history, a bookmark, a shared link or a crawler. This account has
**zero conversions to date**, so every future number depends on getting this right *before*
volume arrives. `ONE_PER_CLICK` counting absorbs repeat views inside one click but does **not**
stop a separate ad click reaching `/thank-you/` without submitting.

There is currently **no custom event of any kind** in the dataLayer - only `gtm.js`, `gtm.dom`
and `gtm.load`. Google Tag Manager therefore has no reliable way to tell a real submission from
a page view.

## Affected URLs

- `https://offer.softwindli.com/thank-you/` - the conversion trigger
- All six offer pages - the submission source

## Exact observed behaviour

Loading `https://offer.softwindli.com/thank-you/` directly, with no form interaction, fires:

```
GET https://www.googleadservices.com/pagead/conversion/18369652705/   en=conversion
GET https://www.google.com/pagead/1p-conversion/18369652705/          en=conversion
```

The six offer pages fire **zero** conversion requests on load, which confirms the trigger is
the `/thank-you/` path.

## Required behaviour

Push a dataLayer event **only after a confirmed successful Gravity Forms submission**:

```js
dataLayer.push({
  event: "gm_power_washing_form_success",
  form_id: "1"
});
```

**It must fire exactly once per successful submission, and must NOT fire on:**

- `form_start` or field focus
- a submit-button click alone
- validation failure
- a direct `/thank-you/` visit
- page refresh
- back navigation

Preferred implementation: the Gravity Forms server-side confirmation, or the
`gform_confirmation_loaded` / submission-success hook - not a click handler.

If the redirect to `/thank-you/` is the only available success point, pass a **single-use**
token, for example a one-time query parameter or a short-lived session flag consumed on first
read, so a refresh or a direct visit cannot re-trigger it.

## Suggested search locations

Gravity Forms confirmation settings for form ID 1; `gform_confirmation` or
`gform_after_submission` filters in the theme or a custom plugin; the redirect that currently
sends users to `/thank-you/`.

## Acceptance criteria

- [ ] `gm_power_washing_form_success` fires once on a real submission
- [ ] A direct `/thank-you/` visit pushes no event and fires no conversion
- [ ] Refresh of `/thank-you/` fires no additional event
- [ ] Back navigation fires no additional event
- [ ] Validation failure fires no event
- [ ] The event carries `form_id`
- [ ] Behaviour is identical on desktop and mobile

**After this ships, Green Marketing repoints the Google Ads conversion trigger from the page
path to this event. Please do not change the Google Ads tag yourself.**

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
