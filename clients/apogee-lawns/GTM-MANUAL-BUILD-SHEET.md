# GTM manual build sheet — Apogee Lawns

**Container:** `GTM-M545Z8T2` · account `6377231045` · container `264326944`
**Workspace:** `Apogee | PPC Tracking | 2026-09` — **ID 3** (already created, reuse it)
**URL:** `https://tagmanager.google.com/#/container/accounts/6377231045/containers/264326944/workspaces/3`
**Plan:** `APG-0917-GTM-K` · fingerprint `2871DD2A5227`
**Signed in as:** access@greenmarketingfl.com

Produced because three state-verified browser recovery attempts were blocked by repeated
GTM script-injection timeouts. Everything below is exact. Do not improvise values.

---

## Already exists — do NOT recreate

| Object | Status | ID |
|---|---|---|
| Workspace `Apogee \| PPC Tracking \| 2026-09` | CREATED | **3** |
| Folder `Google Ads \| Permanent Lights` | CREATED | — |
| Built-in `Page URL` | ENABLED | 2147481602 |
| Built-in `Page Hostname` | ENABLED | 2147481603 |
| Built-in `Page Path` | ENABLED | 2147481604 |
| Built-in `Referrer` | ENABLED | 2147481605 |
| Built-in `Event` | ENABLED | 2147481606 |

**Observed Workspace Changes: 1** (the folder). Built-ins were auto-enabled on workspace
creation and do not register as a change.

## Remaining — 4 objects to build

### 1. Variable — `DLV | lead_id`

*Variables → User-Defined Variables → New*

| Field | Value |
|---|---|
| Name | `DLV \| lead_id` |
| Type | Data Layer Variable |
| Data Layer Variable Name | `lead_id` |
| Data Layer Version | Version 2 |
| Set Default Value | unchecked |
| Folder | `Google Ads \| Permanent Lights` |

### 2. Trigger — `TR | Custom Event | apg_permanent_lights_lead`

*Triggers → New → Custom Event*

| Field | Value |
|---|---|
| Name | `TR \| Custom Event \| apg_permanent_lights_lead` |
| Trigger Type | Custom Event |
| Event name | `apg_permanent_lights_lead` |
| Use regex matching | **unchecked** |
| This trigger fires on | Some Custom Events |
| Condition 1 | `Page Hostname` **equals** `offer.apogeelawns.com` |
| Condition 2 | `Page Path` **matches RegEx** `^/thank-you/permanent-christmas-lights/?$` |
| Folder | `Google Ads \| Permanent Lights` |

> The hostname is **offer.apogeelawns.com**, not apogeelawns.com. The regex is anchored at
> both ends and allows only an optional trailing slash. Do not use "Page URL contains
> thank-you" — it would fire on any thank-you page for any service.

### 3. Tag — `Google tag | AW-18453077620 | All Pages`

*Tags → New → Google Tag*

| Field | Value |
|---|---|
| Name | `Google tag \| AW-18453077620 \| All Pages` |
| Tag Type | Google Tag |
| Tag ID | `AW-18453077620` |
| Configuration settings | none |
| Shared event settings | none |
| Advanced → Tag firing options | Once per event |
| Triggering | **Initialization - All Pages** |
| Folder | `Google Ads \| Permanent Lights` |

> Do **not** add a separate Conversion Linker. A Google Tag with an Ads destination performs
> conversion linking itself.

### 4. Tag — `Google Ads | Lead | Permanent Lights Thank You`

*Tags → New → Google Ads Conversion Tracking*

| Field | Value |
|---|---|
| Name | `Google Ads \| Lead \| Permanent Lights Thank You` |
| Tag Type | Google Ads Conversion Tracking |
| Conversion ID | `18453077620` |
| Conversion Label | `KOL7CImirvocEPS8jt9E` |
| Conversion Value | leave empty |
| Transaction ID | `{{DLV \| lead_id}}` |
| Currency Code | leave empty |
| Limit ad tracking / Advanced | defaults |
| Advanced → Tag firing options | Once per event |
| Triggering | `TR \| Custom Event \| apg_permanent_lights_lead` |
| Folder | `Google Ads \| Permanent Lights` |

> Full `send_to` equivalent: `AW-18453077620/KOL7CImirvocEPS8jt9E`.
> If the developer cannot expose a real non-PII `lead_id`, leave Transaction ID **empty**
> and record the deduplication limitation. Never substitute a static value.

## Must NOT be created

- Google Ads **Calls from Website** conversion tag — WhatConverts owns website-call
  measurement, and its script is confirmed live on the paid page
- Any website-call / landing-page trigger
- Any calls-from-ads GTM tag — configured in Google Ads only
- Any WhatConverts placeholder tag
- Any button-click or page-load conversion trigger
- A second Google tag or a redundant Conversion Linker
- Any GA4 tag or GA4-imported form conversion
- Any Custom HTML tag
- Any variable carrying PII

## Consent

No consent platform is present on the site. Do not install one, do not invent consent
defaults, do not accept Customer Data Terms, do not enable enhanced conversions.

## Expected end state

Workspace Changes should read **5**: the folder plus these four objects.
**Create no version. Publish nothing. Do not press Submit.**

## Preview test matrix — run only after the developer dependency below is met

1. Standard site page — Google tag fires once, no conversion tag
2. Paid landing page — Google tag fires once
3. Empty form submission — no conversion
4. Invalid form submission — no conversion
5. Successful labelled test lead — conversion fires exactly once
6. Thank-you redirect carries a valid success state
7. Direct thank-you visit, no success state — **no conversion**
8. Thank-you refresh — same `lead_id`, deduplicated by Transaction ID
9. Back-button navigation — no extra conversion
10. Mobile form submission
11. Mobile click-to-call — no conversion tag fires
12. A page outside the paid funnel — no conversion tag

## Blocking developer dependency

`apg_permanent_lights_lead` appears **0 times** on `https://offer.apogeelawns.com/`.
The dataLayer push is not implemented, so trigger 2 and tag 4 cannot fire and Preview
cannot pass. Required on the thank-you page, after server-confirmed success only:

```javascript
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "apg_permanent_lights_lead",
  lead_id: "UNIQUE_NON_PII_LEAD_ID",
  service: "permanent_lights",
  lead_type: "estimate_request"
});
```

Do not weaken the trigger to manufacture a passing Preview.
