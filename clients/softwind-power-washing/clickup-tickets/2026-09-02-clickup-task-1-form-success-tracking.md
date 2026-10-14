TASK TITLE:

[P0] Softwind Power Washing — Fix form-success conversion tracking

TASK DESCRIPTION:

**Problem**

A direct visit to https://offer.softwindli.com/thank-you/ currently fires a Google Ads
conversion with no form submission. Verified twice by loading the URL cold with no form
interaction. The conversion is bound to the page path, not to a real lead.

Observed on a bare page load:

```
GET https://www.googleadservices.com/pagead/conversion/18369652705/   en=conversion
GET https://www.google.com/pagead/1p-conversion/18369652705/          en=conversion
```

The six offer pages fire zero conversion requests on load, which confirms the trigger is the
/thank-you/ path. There is currently no custom event of any kind in the dataLayer — only
gtm.js, gtm.dom and gtm.load — so Google Tag Manager has no way to tell a real submission from
a page view.

This account has zero conversions to date. Every future conversion number depends on fixing
this before real volume arrives.

**What we need**

Push a dataLayer event only after a confirmed successful Gravity Forms submission:

```js
dataLayer.push({
  event: "gm_power_washing_form_success",
  form_id: "1"
});
```

**It must fire exactly once per successful submission, and must NOT fire on:**

- form start or field focus
- a submit-button click alone
- validation failure
- a direct /thank-you/ visit
- page refresh
- back navigation

Preferred implementation: the Gravity Forms server-side confirmation, or the
gform_confirmation_loaded / submission-success hook. Not a click handler.

If the redirect to /thank-you/ is the only available success point, pass a single-use token —
a one-time query parameter or a short-lived session flag consumed on first read — so a refresh
or a direct visit cannot re-trigger it.

**Where to look**

Gravity Forms confirmation settings for form ID 1; gform_confirmation or gform_after_submission
filters in the theme or a custom plugin; the redirect that currently sends users to
/thank-you/.

**Acceptance criteria**

- [ ] gm_power_washing_form_success fires once on a real submission
- [ ] Direct /thank-you/ visit pushes no event and fires no conversion
- [ ] Refresh of /thank-you/ fires no additional event
- [ ] Back navigation fires no additional event
- [ ] Validation failure fires no event
- [ ] The event carries form_id
- [ ] Identical behaviour on desktop and mobile

**QA required:** desktop, mobile, and a network capture showing the conversion request firing
once on a real submission and zero times on a direct visit.

**Rollback:** revert the confirmation hook or template change. No data migration involved.

**Do not change any Google Ads tag or conversion setting.** Green Marketing owns that layer and
will repoint the trigger to this event once it ships.
