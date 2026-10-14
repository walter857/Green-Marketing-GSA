# DEV-R7A3-07 - SG-Captcha intermittently intercepts paid landing pages

**Ticket ID:** DEV-R7A3-07 | **Priority:** **P2 - investigation only** | **Raised:** 2026-09-02
**Do not disable the security control.**

## Business impact

SiteGround's SG-Captcha was observed intercepting a paid landing page once. If it challenges
real Google Ads visitors it costs sessions on pages that currently cost roughly 29.50 dollars a
click. The evidence is **intermittent**, so this is a monitoring question, not a proven blocker.

## Affected URLs

- `https://offer.softwindli.com/driveway-pressure-washing/`
- `https://offer.softwindli.com/house-pressure-washing-estimate/`
- `https://offer.softwindli.com/patio-power-washing/`
- `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
- `https://offer.softwindli.com/residential-pressure-washing/`
- `https://offer.softwindli.com/soft-house-washing/`
- `https://offer.softwindli.com/thank-you/`

## Exact observed behaviour

| Date | Result |
|---|---|
| 2026-09-01 | HTTP **202**, request chain passed through `/.well-known/sgcaptcha/?r=...` |
| 2026-09-02 | HTTP **200** on all 7 pages, **no** sgcaptcha request |
| 2026-09-02 controlled submission | **not** blocked - the form submitted successfully |

## What we need from you

- Trigger conditions for SG-Captcha on this site
- Which traffic sources or user agents are affected
- Observed false-positive rate
- Whether an exclusion or allowlist is available for paid landing pages
- Evidence about whether real Google Ads visitors are ever challenged

## Explicitly out of scope

**Do not disable SG-Captcha.** It is a security control and there is no evidence yet that it is
harming genuine visitors.

## Acceptance criteria

- [ ] Trigger conditions documented
- [ ] False-positive evidence provided
- [ ] Allowlist or exclusion options documented
- [ ] Recommendation supplied with supporting data

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
