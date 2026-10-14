# DEV-R7A3-08 - Remove the internal test lead

**Ticket ID:** DEV-R7A3-08 | **Priority:** P0 | **Raised:** 2026-09-02
**For the authorized site and CRM administrator.**

## Business impact

Green Marketing submitted **one** clearly labelled internal test lead to verify conversion
tracking. It must not be worked as a real customer, and it must not distort lead reporting.

## The record

| Field | Value |
|---|---|
| **Name** | `GM TEST DO NOT CONTACT` |
| **Timestamp** | **2026-09-02 09:24:37 America/New_York** |
| Phone | `(631) 555-0147` - NANP **reserved fictitious** range, cannot ring a real person |
| Email | the Green Marketing approver address on file |
| Page | `/power-washing-services-islip-west-islip-dix-hills/` |
| Project field | "Green Marketing conversion tracking test - not a customer - submitted 2026-09-02 - please delete after verification." |

## Systems to check

- **Gravity Forms** entries, form ID 1 - Green Marketing has no WordPress access
- **WhatConverts** - the account or profile number appears to be `158931`
- **CRM or webhook destination** - currently unidentified; please name it if one received the
  lead

## Required actions

1. Locate the record in each system
2. Mark it clearly as an internal test
3. Ensure no sales follow-up, call, text or email is sent
4. **Preserve the record until Green Marketing confirms measurement QA is complete**, then
   delete or archive
5. Report back which systems contained it

## Important

**Do not delete before confirming with Green Marketing** - the record is evidence for the
conversion-tracking investigation. There is nothing to clean in Google Ads; that account's
conversion history is unaffected.

## Acceptance criteria

- [ ] Record located in each system, or confirmed absent
- [ ] Marked as an internal test
- [ ] Follow-up suppressed
- [ ] Systems containing it reported back to Green Marketing
- [ ] Deleted or archived only after Green Marketing signoff

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
