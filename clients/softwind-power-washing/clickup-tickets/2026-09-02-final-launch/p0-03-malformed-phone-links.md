TASK TITLE:

[P0] Softwind Power Washing — Fix malformed telephone links

TASK DESCRIPTION:

**Business impact:** a dead click-to-call link sits on every page of an account where
mobile carries ~74% of spend. Tapping it dials nothing.

**Affected URLs:** https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/ · https://offer.softwindli.com/residential-pressure-washing/ · https://offer.softwindli.com/house-washing-company/ · https://offer.softwindli.com/soft-house-washing/ · https://offer.softwindli.com/driveway-pressure-washing/ · https://offer.softwindli.com/patio-power-washing/ · https://offer.softwindli.com/thank-you/

**Current behavior:** two `tel:` anchors per page — the correct `tel:(631) 502-7946` and a malformed
**`tel:(631)`**. Selector: `a[href="tel:(631)"]`.

**Required behavior:** every static phone link uses **`tel:+16315027946`**. No partial, blank or
malformed href remains. Displayed number equals the `tel:` destination.

**Implementation file path:** shared header/footer or hero component, or a phone shortcode
splitting "(631) 502-7946" on the first space.

**Acceptance criteria:** zero malformed hrefs across all 7 URLs · every href dialable · displayed
number equals destination · mobile tap opens the dialer with the full number.

**Dependencies:** coordinate with the call-tracking architecture decision if a tracking number
later replaces the static one.

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

