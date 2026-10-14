# Audit a Google Ads Account

Validate the work order first. Confirm the exact child account name, 10-digit child customer ID, exact service, and vertical, then take a fresh read-only snapshot for the requested date range.

If the exact service is not confirmed yet, stop and run `prompts/01a-discover-services.md` first. An audit never runs without a confirmed service.

```bash
python scripts/audit_account.py \
  --work-order clients/<client-slug>/work-order.yaml \
  --client clients/<client-slug>/client.yaml \
  --output clients/<client-slug>/snapshots/audit-<date>.json
```

The command validates the work order, verifies identity and the manager link, runs GAQL `SELECT` queries only, and writes a redacted snapshot. Report any entry in `read_errors` as missing data. Never fill a gap with an estimate.

Audit separately:

1. Campaign settings: channel, networks, budget, bidding, locations, location option, languages, schedule, AI Max/DSA/URL expansion/auto assets.
2. Ad groups and keyword architecture: intent, match type, duplicates, cannibalization, low volume, Quality Score components.
3. Search terms: spend, conversions, revenue, buyer intent, negative opportunities, and false negatives.
4. RSAs: relevance, character limits, verified claims, pinning, asset diversity, final URL alignment, policy status.
5. Assets: sitelinks, callouts, snippets, calls, business information, and URL accuracy.
6. Landing pages: intent match, mobile speed, CTA, form, phone, trust, tracking, and service/location accuracy.
7. Conversions: primary/secondary roles, duplicates, attribution, call duration, CRM matching, offline outcomes.
8. Economics: CPL, CPQL, CAC, ROAS, gross-profit ROAS, profit after ad spend.

Deliver:

- Executive finding.
- Identity line with exact account name, child ID, vertical, and service.
- Evidence table with issue, impact, exact resource, and confidence.
- Prioritized actions ranked by estimated recoverable dollars.
- A change plan. Do not implement unless the user separately requests it.
