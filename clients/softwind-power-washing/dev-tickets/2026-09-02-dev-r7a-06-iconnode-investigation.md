# DEV-R7A3-06 - Identify process.iconnode.com in the lead path

**Ticket ID:** DEV-R7A3-06 | **Priority:** P1 | **Raised:** 2026-09-02
**INVESTIGATION ONLY. Do not remove it.**

## Business impact

An **undocumented third party receives a POST on every page load and again at form
submission**, on an endpoint named `/google-ads/`. Nothing in Green Marketing's client records
documents an engagement with this vendor. Until its purpose is known we cannot confirm where
Softwind's lead data is going, and we cannot safely remove it either.

## Affected URLs

- `https://offer.softwindli.com/driveway-pressure-washing/`
- `https://offer.softwindli.com/house-pressure-washing-estimate/`
- `https://offer.softwindli.com/patio-power-washing/`
- `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
- `https://offer.softwindli.com/residential-pressure-washing/`
- `https://offer.softwindli.com/soft-house-washing/`
- `https://offer.softwindli.com/thank-you/`

## Exact observed behaviour

```
POST https://process.iconnode.com/google-ads/
```

- Fires **once per page load** on all 7 URLs
- Fires **again at form submission**, observed during a controlled test on 2026-09-02
- **Zero occurrences in the rendered page source** - it is injected at runtime, which is
  consistent with a GTM Custom HTML tag or another script loader
- Payload contents are deliberately not reproduced in this ticket

## What we need from you

- Script owner, and who added it
- Plugin, theme, GTM tag or code source
- Purpose
- What data is transmitted
- Destination and any downstream sharing
- Retention period
- Current authorization - who signed off, and when
- Whether it is still required

## Explicitly out of scope

**Do not remove it before ownership is established.** If it is an authorized processor,
removing it could break a client system. If it is unauthorized, removal will be raised as its
own approved change.

## Acceptance criteria

- [ ] Vendor and owner identified
- [ ] Source location named
- [ ] Purpose and data flow documented
- [ ] Authorization status confirmed
- [ ] Recommendation recorded: keep, scope, or remove

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
