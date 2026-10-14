# DEV-R7A3 - POWER WASHING WEBSITE P0 DEVELOPER TICKET PACKAGE

**Raised:** 2026-09-02 | **Client:** Softwind Power Washing | **Property:** offer.softwindli.com
**Requested by:** Green Marketing (Walter Correa, access@greenmarketing.com)

These are **developer tickets, not Google Ads change plans.** They carry no approval fingerprint
and no Google Ads mutation. Green Marketing has **no WordPress access by design** and will not
request it; every issue below is evidenced from the publicly delivered site.

Where the public code proves the effect but the internal WordPress source cannot be identified
from outside, the ticket is marked:
**PUBLIC EFFECT PROVEN - INTERNAL WORDPRESS SOURCE REQUIRES DEVELOPER.**

## Send these in this order

| # | Ticket | Priority | Type | File |
|---|---|---|---|---|
| **1** | **Form-success dataLayer event** | **P0** | change | `2026-09-02-dev-r7a-04-form-success-event.md` |
| 2 | Test-lead cleanup | P0 | admin | `2026-09-02-dev-r7a-08-test-lead-cleanup.md` |
| 3 | Duplicate Gravity Form and duplicate IDs | P1 | change | `2026-09-02-dev-r7a-01-duplicate-gravity-form.md` |
| 4 | Malformed `tel:(631)` link | P1 | change | `2026-09-02-dev-r7a-02-malformed-phone-links.md` |
| 5 | GTM container installed twice | P1 | change | `2026-09-02-dev-r7a-03-duplicate-gtm-loader.md` |
| 6 | Identify both Google Ads tag sources | P1 | investigation | `2026-09-02-dev-r7a-05-hardcoded-google-tags.md` |
| 7 | Identify `process.iconnode.com` | P1 | investigation | `2026-09-02-dev-r7a-06-iconnode-investigation.md` |
| 8 | SG-Captcha behaviour | P2 | investigation | `2026-09-02-dev-r7a-07-sgcaptcha-investigation.md` |

**Ticket 1 is the one to start with.** It is the prerequisite for correcting a proven defect
where a direct visit to `/thank-you/` fires a Google Ads conversion with no form submission.

## Standing instructions for all tickets

- **Do not remove `AW-17878095007`.** It belongs to Softwind Landscape and Masonry and requires
  a separate approval from that account's owner.
- **Do not remove `process.iconnode.com`** before its ownership is established.
- **Do not disable SG-Captcha.**
- **Do not remove or expose the Gravity Forms honeypot** (`input_9`). It is the spam guard and
  it must stay hidden and empty.
- **Do not change any Google Ads tag or conversion configuration.** Green Marketing owns that
  layer and will make those changes itself once the site-side signals exist.
- Apply every change on staging first and attach a network capture as QA evidence.

## Affected URLs

- `https://offer.softwindli.com/driveway-pressure-washing/`
- `https://offer.softwindli.com/house-pressure-washing-estimate/`
- `https://offer.softwindli.com/patio-power-washing/`
- `https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/`
- `https://offer.softwindli.com/residential-pressure-washing/`
- `https://offer.softwindli.com/soft-house-washing/`
- `https://offer.softwindli.com/thank-you/`

## Evidence

- `clients/softwind-power-washing/snapshots/r7a-public-code-inspection-2026-09-02T115916.json`
- Saved rendered source: `clients/softwind-power-washing/snapshots/r7a-page-source-2026-09-02/`
- `clients/softwind-power-washing/audits/2026-09-02-r7a-page-code-inspection.csv`
- `clients/softwind-power-washing/receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md`
