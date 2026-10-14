# Operating Workflows

| Workflow | Read-only input | Draft output | Write gate | Final verification |
|---|---|---|---|---|
| Client onboarding | Exact child account name + child ID + service | work-order.yaml + client.yaml | None | Identity, vertical, and task fields complete |
| Service discovery | Exact child account name + child ID (no service) | candidate services with evidence | None | Identity, manager link, and account type verified; every candidate carries resource IDs and a confidence level |
| Account audit | Fresh API snapshot | prioritized audit | None | Evidence tied to resource IDs |
| Campaign build | Client profile + snapshot | validated plan | Plan fingerprint | API/UI readback |
| RSA/assets | Approved structure + claims | copy sheet | Copy approval | Character/policy/readback QA |
| Landing page | Template + client facts | local page | Deployment approval | Live mobile/form/tag test |
| Conversions | Existing tag/action inventory | measurement map | Per-conversion approval | Tag Assistant or automated test |
| Negatives | Search terms + CRM outcomes | verdict table | Term-level approval | Negative list readback |
| Offline outcomes | CRM records + consent | validate-only batch | Upload approval | Acceptance/rejection reconciliation |
| Enablement | Paused build receipt | QA report | Separate enable approval | Delivery and budget check |

Every row starts with the same gate: validate the current work order, then confirm the observed child account name and ID match before reading or changing Google Ads.

Service discovery is the one row that runs from `service-discovery.yaml` instead of `work-order.yaml`, because a service does not exist yet. It still requires the exact child account name and 10-digit child customer ID, it is read-only, and it ends by asking the user to confirm the exact service. Every other row still requires that confirmed service.

## Expert autonomy in the workflow

Claude runs as Green Marketing's senior Google Ads strategist, not as an option menu. The
binding rules are in the `Expert Autonomy and Decision Rights` section of `CLAUDE.md` and the
`expert_autonomy` block of `config/agency.yaml`; `tests/test_expert_autonomy.py` fails if
either drifts.

What changes in practice:

| Stage | Before | Now |
|---|---|---|
| Strategy choice | present options, wait | choose, state rationale, proceed |
| Routine technical calls | ask the user | decide and document |
| Internal errors found in QA | report as a checkpoint | fix silently, rerun validators |
| Questions | asked as they arise | batched once, after all unblocked work |
| Fingerprint | generated, then corrected | generated only after a full self-review passes |

What does not change: the client gate, client truth, plan fingerprints, and every
external-write approval. Autonomy governs judgment, never permission.

### Self-review before any fingerprint

Run one internal red-team pass over client truth, campaign strategy, search intent,
conversion isolation, mutation necessity, API field validity, status handling, asset support,
character limits, URL mapping, location targeting, budget math, landing-page template
compliance, unsupported claims, mutation counts, artifact hashes, and approval-bundle
completeness. Fix what it finds, rerun validators, then fingerprint.
