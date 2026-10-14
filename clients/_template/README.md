# Client Workspace Template

Copy this entire folder to `clients/<client-slug>/` for each Green Marketing client.

Complete `work-order.yaml` for every new task. The exact child account name, 10-digit child customer ID, and exact service are mandatory. Complete `client.yaml` once, then keep it current as verified client facts change.

Recommended task folders:

- `snapshots/` for read-only account exports.
- `plans/` for validated campaign plans and approval fingerprints.
- `exports/` for Google Ads Editor files or upload batches.
- `receipts/` for API readback and QA.
- `landing-pages/` for client page code or briefs.

Never put credentials, lead PII, or unredacted CRM exports in this folder.
