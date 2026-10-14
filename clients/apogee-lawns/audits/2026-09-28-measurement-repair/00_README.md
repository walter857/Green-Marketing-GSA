# Apogee — measurement repair handoff and next-action plan (run C, 2026-09-28)

**Apogee Lawns LLC - Live · 8164626278 · Permanent Christmas light installation** · campaign 24257151015.
Follows `../2026-09-28-independent/`. READ for external systems, DRAFT for local files. Omaha stays excluded and is
not revisited.

## Recommendation

**Send `02_developer_form_and_content_handoff.md` to the developer now, and leave the campaign unchanged while the repair
is built.** The Google Ads form conversion cannot fire as the site stands. The fix is on the website, not in GTM or
Google Ads. Maximize Clicks does not depend on conversions, and WhatConverts is recording both the paid form and calls to
402-526-5754, so real leads are not being lost. **Reassess delivery on 2026-10-15** if the repair is not live and
QA-passed by then.

## Files

| File | Content |
|---|---|
| `01_current_state_reconciliation.md` | fresh state, change history, evidence types, corrections to the audit, economics check |
| `02_developer_form_and_content_handoff.md` | copy-ready developer instructions (D1–D8, C1–C3) + controlled E2E test request |
| `03_form_acceptance_matrix.csv` | F01–F12: expected form / event / conversion behaviour, evidence, status |
| `04_gtm_delta_and_readiness.md` | published vs workspace, version history, minimal delta, G01–G07, blockers, consent and admin |
| `05_call_measurement_plan.md` | verification of the call architecture, call types, promotion criteria, TC-1..TC-3, owner evidence list |
| `06_tablet_plan_evaluation.md` | evaluated 3-update payload, HOLD, one owner question |
| `07_pii_incident_note.md` | sanitized incident note and containment |
| `08_action_register.csv` + `08_validation_and_register.md` | 20 actions, validator results |

Plans: `../../plans/APG-0928-GTM-LID.yaml` (draft), `../../plans/APG-0928-DEV-T2.yaml` (HOLD),
`../../plans/APG-0928-DEV-T.yaml` (VOID). **No plan in this run is fingerprinted. No approval line is ready.**

## Monitoring (conditions; nothing is scheduled)

- **Each Monday, completed days only:**
  - delivery and impression share;
  - Google Ads conversions by action;
  - WhatConverts leads by tracking number and source, sanitized;
  - `call_view` rows;
  - developer status against A01–A08.
- **2026-10-15:**
  - (a) Is the form repair live and has it passed the Preview matrix?
  - If not, reassess continuing spend without Google Ads form attribution. That is an owner decision; WhatConverts
    remains the interim record.
  - (b) If yes, evaluate the APG-0928-KW-P gates. The date alone authorizes nothing.
- **2026-11-02 (pre-peak):**
  - Check budget-lost impression share only on days when spend reached at least 80% of $16.44.
  - Check whether any paid lead or call appears in both systems.
  - Start the "$300 without a qualified lead" review clock only after form and call capture are verified **and**
    "qualified" is defined.

---

## Update 2026-09-28 (run D) — owner answers recorded

- **Closed decisions:**
  - tablets stay excluded (landing pages are not tablet optimized; DEV-T2 REJECTED);
  - qualified lead = asks for permanent Christmas light installation on the form or call;
  - Apogee installs customer-supplied lights (owner-provided only);
  - Omaha still excluded.
- **New files:** `09_owner_decisions_and_reporting.md`, `10_website_claim_matrix.csv`, `11_labor_only_negatives.md`.
- **Dated revisions appended:** 01, 02 (handoff), 05 (call-flow screenshot + corrected capture wording), 06 (CLOSED).
  `08_action_register.csv` has 22 rows with run-C and run-D readiness columns.
- **Plan ready for separate approval:** `../../plans/APG-0928-NEG-LO.yaml`. It removes `labor only` and `my own
  lights` and keeps `customer supplied`. Fingerprint **58362D536336**; low priority.
- **Unchanged:** no GTM-publication or website-call-promotion code (QA evidence does not exist yet); the recommendation
  to keep delivery as is and send the developer handoff first.
