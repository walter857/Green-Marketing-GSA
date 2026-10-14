# API and Integration Setup

## Required for Google Ads planning and paused builds

1. A Green Marketing manager account with client access.
2. Google Ads API enabled in the Google Cloud project.
3. Approved Google Ads developer token.
4. OAuth client ID, client secret, and refresh token for a user with manager access.
5. OAuth scope: `https://www.googleapis.com/auth/adwords`.
6. Local environment variables from `.env.example`.

The exact child account name and 10-digit child customer ID belong in `client.yaml` and the current `work-order.yaml`; they are not secrets. The manager/MCC ID is separate. Tokens and secrets belong only in the local `.env`.

## Required for new offline-conversion integrations

1. Data Manager API enabled.
2. Application Default Credentials or another supported Google authentication method.
3. Scope: `https://www.googleapis.com/auth/datamanager`.
4. The credential identity must have access to the operating Google Ads account or an authorized parent manager.
5. Accepted customer data terms and valid consent signals where user-provided data is used.
6. A Google Ads conversion action of the correct import type.

As of June 15, 2026, Google Ads API offline uploads can fail for developer tokens that had not previously sent them. Use Data Manager API for new integrations and document any grandfathered legacy route.

## Optional APIs by module

| Module | API or integration |
|---|---|
| GTM container automation | Google Tag Manager API |
| GA4 reporting | Google Analytics Data API |
| GA4 property/configuration | Google Analytics Admin API |
| Business Profile data | Business Profile APIs, subject to Google's access and approval requirements |
| Business Profile performance | Business Profile Performance API |
| Keyword/SEO enrichment | Approved keyword data provider or Keyword Planner access |
| Landing-page deployment | GitHub and Vercel integrations |
| Forms and lead routing | Make.com or CRM webhook |
| Call attribution | WhatConverts or approved call-tracking provider |
| Dashboard storage | CRM/database, Sheets, or warehouse chosen by GM |

Do not enable every API preemptively. Add only the APIs required by the active workflow and grant the narrowest practical permissions.

## Preflight sequence

1. Confirm the Cloud project and manager account ownership.
2. Confirm developer-token access tier.
3. Create or reuse the approved OAuth client.
4. Generate credentials locally; never paste them into chat.
5. Populate `.env`.
6. Run `python scripts/validate_work_order.py ... --client ...`.
7. Run `python scripts/verify_setup.py --client ... --online`.
8. Run `python scripts/list_live_accounts.py --work-order ... --client ...`.
9. Compare the selected child customer ID and exact displayed name to the work order and client profile.
10. Test read-only snapshots before any write permission is used.
