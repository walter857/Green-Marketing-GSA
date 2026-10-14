# Discover the Services an Account Advertises

Use this workflow only when the exact child account name and 10-digit child customer ID are known but the exact service is not yet confirmed. It is the single stage that may run before a service exists, because discovering the service is its entire purpose.

It authorizes reads and nothing else. It is not an audit, and it never becomes one.

## Gate

1. Require the exact child account name and the 10-digit child customer ID. Never accept the MCC ID as the child ID.
2. Complete `clients/<client-slug>/service-discovery.yaml` from `clients/_template/service-discovery.yaml`.
3. Run `python scripts/validate_service_discovery.py clients/<client-slug>/service-discovery.yaml`.
4. Confirm with a fresh read-only lookup that the child customer ID has exactly the expected descriptive name, sits under the expected manager account, and is neither a manager nor a test account.
5. Stop on any name, ID, manager-relationship, or account-type mismatch.

The document must not name a service, a vertical, a scope approval, or a plan. It discovers a service; it never asserts one.

## Read

```bash
python scripts/discover_services.py \
  --discovery clients/<client-slug>/service-discovery.yaml \
  --output clients/<client-slug>/snapshots/service-discovery-<date>.json
```

Read only enabled resources: campaigns, ad groups, keywords, ads with their headlines, descriptions, status, and policy status, plus final URLs and URL-bearing assets. Then GET the public landing pages for the observed final URLs and read the title, H1, major headings, canonical URL, and service text.

Landing-page access is GET only. Never submit a form, call a number, trigger a lead, interact with a chat widget, or change the website.

## Classify

Combine evidence from campaign names, ad groups, keywords, ads, assets, final URLs, and landing pages. Group synonyms, but keep meaningful differences between services. Never finalize a service from one weak clue.

Report per candidate: proposed service name, supporting campaigns and IDs, supporting ad groups and IDs, representative keywords, representative headlines and descriptions, final URLs and landing-page evidence, confidence, and any conflict.

Confidence is earned, not assumed:

| Level | Requirement |
|---|---|
| high | Three or more kinds of evidence, including at least one campaign, ad group, or keyword name |
| medium | Two or more kinds of account evidence |
| low | A single kind of evidence, or landing-page text only |

Landing-page text alone can never exceed low. Site navigation routinely lists services an account does not advertise.

## Stop

Present the candidates and stop. Ask the user to confirm the exact service or services.

Only after that confirmation, record the exact service in `clients/<client-slug>/work-order.yaml`, validate it with `scripts/validate_work_order.py`, and continue with `prompts/02-audit-account.md`. Discovery never authorizes the audit, a draft, a build, a revamp, or any Google Ads write.
