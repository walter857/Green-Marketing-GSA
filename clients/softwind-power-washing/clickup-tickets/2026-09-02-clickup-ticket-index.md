# SOFTWIND POWER WASHING — CLICKUP LAUNCH TASK PACKAGE

**Created:** 2026-09-02 · **Client:** Softwind Power Washing · **Property:** offer.softwindli.com
**Requested by:** Green Marketing (Walter Correa, access@greenmarketing.com)

Each task file is directly pasteable into ClickUp — it opens with `TASK TITLE:` and
`TASK DESCRIPTION:`.

Green Marketing has **no WordPress access by design** and will not request it. Every issue below
is evidenced from the publicly delivered site: **PUBLIC DEFECT PROVEN — INTERNAL WEBSITE SOURCE
MUST BE LOCATED BY DEVELOPMENT.**

| # | Priority | Task | File | Blocks launch? |
|---|---|---|---|---|
| 1 | **P0** | Fix form-success conversion tracking | `2026-09-02-clickup-task-1-form-success-tracking.md` | **YES** |
| 2 | **P0** | Fix duplicate form markup and phone links | `2026-09-02-clickup-task-2-duplicate-form-and-phone.md` | **YES** |
| 3 | **P0** | Correct Google tag scope and duplicate GTM load | `2026-09-02-clickup-task-3-google-tag-scope-and-gtm.md` | **YES** |
| 4 | P1 | Publish final landing-page copy and CRO updates | `2026-09-02-clickup-task-4-landing-page-copy.md` | **YES** (titles/H1 only) |
| 5 | P2 | Vendor, security and cleanup investigations | `2026-09-02-clickup-task-5-vendor-and-cleanup.md` | no |

## Start with Task 1

It is the prerequisite for correcting a proven defect where a direct visit to `/thank-you/`
fires a Google Ads conversion with no form submission.

## Standing instructions

- **Preserve `AW-18369652705`** — the correct Power Washing Google Ads tag.
- **Do not remove `AW-17878095007` globally** — it belongs to Softwind Landscape & Masonry
  (customer 2429758629) and needs that account owner's separate approval to scope.
- **Do not remove `process.iconnode.com`** before its ownership is established.
- **Do not disable SG-Captcha.**
- **Do not remove or expose the Gravity Forms honeypot** (`input_9`) — it is the spam guard.
- **Do not change any Google Ads tag or conversion configuration.** Green Marketing owns that
  layer.
- **Do not change any URL slug.**
- Apply every change on staging first and attach a network capture as QA evidence.

## Evidence

- `clients/softwind-power-washing/snapshots/r7a-public-code-inspection-2026-09-02T115916.json`
- `clients/softwind-power-washing/snapshots/r7a-page-source-2026-09-02/` (7 rendered sources)
- `clients/softwind-power-washing/audits/2026-09-02-r7a-implementation-source-audit.md`
- `clients/softwind-power-washing/receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md`
