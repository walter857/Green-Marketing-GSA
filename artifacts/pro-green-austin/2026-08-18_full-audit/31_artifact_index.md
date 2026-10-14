# 31 — Artifact Index, Pro Green Austin

**Account:** Pro Green - Austin - Live | `7380491929` | outdoor design & build
Artifacts are append-only. Nothing in this directory is ever deleted or overwritten; a
correction is issued as a new numbered artifact that names what it supersedes.

## Status legend

- **EXECUTED** — an approved external write was applied and read back.
- **CURRENT** — the live proposal awaiting approval.
- **VOID** — never approved, never executed, and never to be executed. Preserved as history.
- **REFERENCE** — read-only evidence.

## Index

| # | Artifact | Phase | Status |
|---|---|---|---|
| 00 | `00_identity_and_source_log.md` | Audit | REFERENCE |
| 01 | `01_fresh_account_snapshot.json` | Audit | REFERENCE |
| 02 | `02_executive_audit.md` | Audit | REFERENCE |
| 03 | `03_campaign_and_ad_group_verdicts.csv` | Audit | REFERENCE |
| 04 | `04_keyword_verdicts.csv` | Audit | REFERENCE |
| 05 | `05_search_term_verdicts.csv` | Audit | REFERENCE |
| 06 | `06_negative_keyword_plan.csv` | Audit | REFERENCE |
| 07 | `07_conversion_and_tracking_audit.md` | Audit | REFERENCE |
| 08 | `08_ads_assets_and_policy_audit.csv` | Audit | REFERENCE |
| 09 | `09_landing_page_and_market_integrity_audit.csv` | Audit | REFERENCE |
| 10 | `10_location_budget_schedule_and_device_plan.md` | Audit | REFERENCE |
| 11 | `11_exact_change_plan.yaml` | Phase 1 | **EXECUTED** 2026-08-19 |
| 12 | `12_validation_and_approval_report.md` | Phase 1 | REFERENCE |
| 13 | `13_execution_qa_receipt.md` | Phase 1 | **EXECUTED** receipt |
| 14 | `14_blocked_clickcease_proposal.md` | Phase 1 | BLOCKED, still open |
| 15 | `15_phase2_theme_ad_and_asset_audit.md` | Phase 2 | REFERENCE |
| 16 | `16_rsa_rebuild_plan.csv` | Phase 2 | REFERENCE |
| 17 | `17_phase2_change_plan.yaml` | Phase 2 | **EXECUTED** 2026-08-20 |
| 18 | `18_phase2_create_paused_qa_receipt.md` | Phase 2 | **EXECUTED** receipt |
| 19 | `19_phase2_enable_plan.yaml` | Phase 2 | **EXECUTED** 2026-08-20 |
| 20 | `20_phase2_enable_qa_receipt.md` | Phase 2 | **EXECUTED** receipt |
| 21 | `21_search_term_verdicts_mtd.csv` | Phase 3 r1 | **VOID — SUPERSEDED by 24** |
| 22 | `22_adgroup_negative_plan_mtd.yaml` | Phase 3 r1 | **VOID — SUPERSEDED by 26** |
| 23 | `23_adgroup_negative_plan_mtd.csv` | Phase 3 r1 | **VOID — SUPERSEDED by 27** |
| 24 | `24_search_term_verdicts_mtd_v2.csv` | Phase 3 r2 | **CURRENT** |
| 25 | `25_candidate_reconciliation.json` / `25_candidate_reconciliation_report.md` | Phase 3 r2 | **CURRENT** |
| 26 | `26_campaign_negative_plan.yaml` | Phase 3 r2 | **CURRENT — awaiting approval** |
| 27 | `27_campaign_negative_plan.csv` | Phase 3 r2 | **CURRENT** |
| 28 | `28_expert_audit_summary.md` | Phase 3 r2 | **CURRENT** |
| 29 | `29_validate_only_receipt.md` | Phase 3 r2 | **CURRENT** |
| 30 | `30_resume_checkpoint.json` | Phase 3 r2 | **CURRENT** |
| 31 | `31_artifact_index.md` | Phase 3 r2 | **CURRENT** |

## Void fingerprints

| Fingerprint | Subplan | Status |
|---|---|---|
| `2D87A5249784` | MASTER | **PERMANENTLY VOID.** Never approved, never executed. |
| `4EEF81C7F2F5` | EXISTING_RESOURCES | **PERMANENTLY VOID.** Never approved, never executed. |

No external change is authorized under either code. The plan they fingerprinted proposed 28
**ad-group** negative objects; it is replaced by the campaign-scoped plan in artifact 26.
`scripts/validate_negative_plan.py` fails if either code appears anywhere inside a subplan,
and `tests/test_negative_plan_validator.py` fails if either is dropped from the void register.

The following files are preserved as history and must not be executed:

- `artifacts/pro-green-austin/2026-08-18_full-audit/21_search_term_verdicts_mtd.csv`
- `artifacts/pro-green-austin/2026-08-18_full-audit/22_adgroup_negative_plan_mtd.yaml`
- `artifacts/pro-green-austin/2026-08-18_full-audit/23_adgroup_negative_plan_mtd.csv`
- `clients/pro-green-austin/plans/adgroup-negatives-mtd-2026-08-21.json`
- `clients/pro-green-austin/receipts/validate-mtd-negatives-2026-08-21.json`

## Current fingerprints

| Fingerprint | Subplan | Actions | Objects | Status |
|---|---|---:|---:|---|
| `063EE720BAF3` | MASTER | 68 | 68 | Awaiting approval |
| `628D3E61A9C2` | EXISTING_RESOURCES | 68 | 68 | Awaiting approval |

## Supporting client files, Phase 3 round 2

| File | Role |
|---|---|
| `clients/pro-green-austin/snapshots/negatives-fresh-read-2026-08-22.json` | Fresh read-only account read, 0 read errors |
| `clients/pro-green-austin/snapshots/post-validate-check-2026-08-22.json` | Post-validate re-read proving no external write |
| `clients/pro-green-austin/plans/campaign-negatives-2026-08-22.json` | The 68 plan actions |
| `clients/pro-green-austin/receipts/validate-campaign-negatives-2026-08-22.json` | Server-side validate-only receipt |
