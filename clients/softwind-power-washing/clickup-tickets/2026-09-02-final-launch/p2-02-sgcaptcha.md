TASK TITLE:

[P2] Softwind Power Washing — SG-Captcha behaviour on paid landing pages

TASK DESCRIPTION:

**Business impact:** SG-Captcha was observed intercepting a paid landing page once. If it
challenges real Google Ads visitors it costs sessions on pages that have cost ~$29.57 a click.
The evidence is intermittent, so this is monitoring, not a proven blocker.

**Affected URLs:** https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/ · https://offer.softwindli.com/residential-pressure-washing/ · https://offer.softwindli.com/house-washing-company/ · https://offer.softwindli.com/soft-house-washing/ · https://offer.softwindli.com/driveway-pressure-washing/ · https://offer.softwindli.com/patio-power-washing/ · https://offer.softwindli.com/thank-you/

**Current behavior:** 2026-09-01 HTTP **202** with the chain passing through
`/.well-known/sgcaptcha/`. 2026-09-02 HTTP **200** on all 7 pages with no sgcaptcha request, and
it did not block a controlled form submission.

**Required:** document trigger conditions, affected traffic sources, false-positive rate,
available exclusions or allowlists for paid landing pages, and evidence about whether real Google
Ads visitors are ever challenged.

**Do not disable SG-Captcha.** It is a security control and there is no evidence it is harming
genuine visitors.

**Acceptance criteria:** trigger conditions documented · false-positive evidence · allowlist
options · recommendation with supporting data.

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

