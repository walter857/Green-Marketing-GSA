# 08 — Validation results and action register

## Validators and tests (actual output)

| Check | Result |
|---|---|
| `scripts/validate_work_order.py` on the task work order (`--client`) | `Work order: PASS …` exit 0 |
| same on canonical `work-order.yaml` | PASS, exit 0 (file not edited) |
| work-order JSON schema | 0 errors |
| `tests/test_wc_sanitize.py` (synthetic data) | 9 passed |
| `tests/test_apg_lead_id_guard.py` | 3 passed |
| `tests/test_apg_lead_id_contract.py` | 4 passed |
| `tests/test_apg_negmatch.py` | 9 passed |
| Guard regex as a JavaScript `RegExp` with the `i` flag (Node) | 26 invalid values rejected, 8 valid accepted, 0 errors |
| `scripts/validate_apg_0928c_package.py` (new; this package) | 36 passed, 1 failed on its first run: the only failure was this file not yet existing. Re-run after writing it: see the final answer (all passed) |
| `scripts/validate_apg_0928_package.py` (run B) | re-run to confirm the VOID banner changed no plan data |

No existing validator was weakened or modified in this run. `scripts/validate_audit_package.py` belongs to another client
and remains not applicable.

## Fingerprints

**None issued.** GTM-LID is blocked on the developer repair and Preview QA. DEV-T2 is blocked on owner intent. The
KW-P, NEG-H and website-call promotion plans remain conditional. The historical `46060B03F5C9` is void.

## Action register

See `08_action_register.csv`: 20 actions with owner, exact system or resource, change or verification, dependency,
acceptance evidence, approval required and readiness.

- **Developer:** A01–A08 (A01–A06 ready; A07–A08 need a confirmation).
- **Green Marketing:** A09–A11, A14, A18, A20 (drafts complete or blocked on dependencies).
- **Owner:** A12–A13, A15–A17, A19.

---

## Run D results (2026-09-28, owner answers recorded)

| Check | Result |
|---|---|
| `validate_work_order.py`: task work order (updated with owner answers) and canonical | PASS, exit 0 (both) |
| JSON schema: `client.yaml`, task work order, canonical work order | 0 errors each |
| Unit tests (sanitizer 9, guard 3, lead-ID contract 4, negative matcher 9) | 25 passed |
| `scripts/validate_apg_0928c_package.py` (extended with 26 run-D checks) | **59 passed, 0 failed, exit 0**. The first run-D pass had 2 failures, both fixed without loosening a rule: the handoff's revision note quoted the phrase the check forbids (the note was reworded), and the privacy check flagged the Google Ads customer ID `816-462-6278` in a `client.yaml` comment (added to the allowlist as a labelled account ID, not a phone number) |
| `scripts/validate_apg_0928_package.py` (run B) | 36 passed, 0 failed |

**Fingerprints in run D:** only `APG-0928-NEG-LO` → **58362D536336** (2 removes, verified against the live read, low
priority). None issued for tablet restoration (rejected), GTM publication (no QA) or website-call promotion (no QA).
