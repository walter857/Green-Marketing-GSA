# DEV-R7A3-02 - Malformed telephone link tel:(631)

**Ticket ID:** DEV-R7A3-02 | **Priority:** P1 | **Raised:** 2026-09-02

## Business impact

A **dead click-to-call link** sits on every page of a mobile-dominated account. Tapping it
dials nothing. Mobile carries roughly 71 percent of this account's paid spend.

## Affected URLs

- `https://offer.softwindli.com/driveway-pressure-washing/`
- `https://offer.softwindli.com/house-pressure-washing-estimate/`
- `https://offer.softwindli.com/patio-power-washing/`
- `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
- `https://offer.softwindli.com/residential-pressure-washing/`
- `https://offer.softwindli.com/soft-house-washing/`
- `https://offer.softwindli.com/thank-you/`

## Exact observed behaviour

Two `tel:` anchors exist on every page:

| href | Status |
|---|---|
| `tel:(631) 502-7946` | correct |
| **`tel:(631)`** | **malformed - dials nothing** |

DOM selector: `a[href="tel:(631)"]`

## Required behaviour

- Every static Power Washing phone link uses **`tel:+16315027946`**, unless the finally
  approved call-tracking architecture requires a tracking number in the rendered DOM - in which
  case the displayed text and the `tel:` destination must still agree
- No `tel:(631)`, partial, blank or malformed `href` remains anywhere
- Displayed number and `tel:` destination always match

## Suggested search locations

Shared header/footer, the hero component, or a phone shortcode where a formatting helper is
splitting `(631) 502-7946` on the first space or truncating after the area code.

## Acceptance criteria

- [ ] Zero malformed `tel:` hrefs across all 7 URLs
- [ ] Every `tel:` href is a complete dialable number
- [ ] Displayed number equals the `tel:` destination
- [ ] Mobile tap opens the dialer with the full number

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
