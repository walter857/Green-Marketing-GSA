# Prepare Offline Conversions

Validate the current work order and exact child account identity before preparing any event.

Use the CRM as source of truth and map lead stages to conversion actions such as Qualified Lead and Closed Won.

Before upload:

- Confirm the exact child account name, 10-digit child customer ID, exact service, and conversion owner.
- Confirm conversion action type, primary/secondary role, value rule, currency, attribution timestamp, and consent.
- Confirm Data Manager API access for new integrations.
- Normalize and hash user-provided data only where permitted.
- Require a unique transaction/lead ID.
- Validate timestamps with time zones and reject future or duplicate events.
- Use validate-only first.
- Reconcile accepted, rejected, unmatched, and duplicate counts.
- Never upload raw PII in logs or reports.

The legacy Google Ads API upload path is grandfathered-only after June 15, 2026. Do not use it unless developer-token eligibility is documented.
