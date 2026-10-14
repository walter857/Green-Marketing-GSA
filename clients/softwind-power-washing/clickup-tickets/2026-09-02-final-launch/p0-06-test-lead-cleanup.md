TASK TITLE:

[P0] Softwind Power Washing — Remove the internal test lead

TASK DESCRIPTION:

**Business impact:** Green Marketing submitted one clearly labelled internal test lead to
verify conversion tracking. It must not be worked as a real customer or distort lead reporting.

**The record:** name `GM TEST DO NOT CONTACT` · timestamp **2026-09-02 09:24:37
America/New_York** · phone `(631) 555-0147` (NANP reserved fictitious range, cannot ring a real
person) · page `/power-washing-services-islip-west-islip-dix-hills/` · project field reads
"Green Marketing conversion tracking test - not a customer - submitted 2026-09-02 - please delete
after verification."

**Systems to check:** Gravity Forms entries (form ID 1) · WhatConverts (account/profile appears
to be `158931`) · any CRM or webhook destination — please name it if one received the lead.

**Required behavior:** locate it, mark it clearly as an internal test, suppress any follow-up,
and report back which systems contained it. **Preserve the record until Green Marketing confirms
measurement QA is complete**, then delete or archive.

**Acceptance criteria:** located or confirmed absent in each system · marked as test · follow-up
suppressed · systems reported back · deleted only after Green Marketing signoff.

**Note:** nothing to clean in Google Ads — that account's conversion history is unaffected.

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

