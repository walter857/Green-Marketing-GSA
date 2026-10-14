# Pro Green Dallas — Evidence Index

Account: **Pro Green - Dallas - Live** · child **8735782888** · manager **3373711342** ·
WhatConverts profile **ProGreen DFW / 107007**. Last updated **2026-08-11**.

Every item below is read-only evidence. No external system was modified to obtain any of it.

---

## 1. Local project files

| Path | What it is |
| --- | --- |
| **`clients/pro-green-dallas/confirmed-business-decisions.md`** | **AUTHORITATIVE.** User decisions of 2026-08-11. Supersedes conflicting assumptions elsewhere |
| **`clients/pro-green-dallas/google-ads-current-page-strategy.md`** | Fresh strategy on the existing pages; explains why $484.11 is not a qualified CPL |
| **`clients/pro-green-dallas/google-ads-change-manifest.md`** | Exact proposed → executed changes, per resource, with rollback |
| **`clients/pro-green-dallas/google-ads-execution-log.md`** | Chronological mutation log, 8 identity gates, 2 incidents |
| **`clients/pro-green-dallas/google-ads-post-change-verification.md`** | **29/29 read-back checks PASS** |
| **`clients/pro-green-dallas/backups/pre-change-2026-08-11T1300/`** | Pre-mutation state: 9 resource exports + 3 exec logs + verification + negative manifests. **Activation run adds `step1.json` (goal-config inspection), `step2.json` (containment retry), `step345.json` (enablement pre-checks), `step7.json` (post-activation verification). Cleanup run adds `cleanup_precheck.json`, `cleanup_exec.json`, `cleanup_verify.json`** |
| **`clients/pro-green-dallas/landing-page-template-character-budget.md`** | Divi template character-budget map from live DevTools inspection |
| **`clients/pro-green-dallas/landing-page-content-backlog.md`** | Page priority, ad-group→page mapping, future briefs |
| **`clients/pro-green-dallas/clickup-wordpress-landing-page-task.md`** | Ready-to-paste ClickUp developer handoff |
| **`clients/pro-green-dallas/batch-1-resource-level-preview.md`** | Batch 1A/1B/1C resource-level previews, conversion inventory, URL dependency map, location export |
| **`clients/pro-green-dallas/canonical-landing-page-developer-handoff.md`** | Implementation-ready developer handoff for the new canonical page |
| **`clients/pro-green-dallas/landing-page-draft/`** | **LOCAL ONLY, NOT DEPLOYED.** `README.md`, `brief.yaml`, `index.html`, `attribution.js` |
| `clients/pro-green-dallas/client.yaml` | Confirmed identity and scope. `business_name: Pro Green` — **shorter than the confirmed customer-facing name**, not edited |
| `clients/pro-green-dallas/work-order.yaml` | `task.type: audit`, `task.mode: read`. Validator **PASS** |
| `clients/pro-green-dallas/service-discovery.yaml` | Prior read-only discovery document |
| `clients/pro-green-dallas/continuation.md` | Running diagnosis log, §1–§13 |
| `clients/pro-green-dallas/final-audit-and-revamp-plan.md` | **The deliverable** — audit, strategy, and the four implementation batches |
| `clients/pro-green-dallas/snapshots/audit-2026-08-07.json` | 9,223,762 bytes. 54 queries, 0 read errors, `google_ads_changes_made: false`. **Stale as of 2026-08-08** |
| `clients/pro-green-dallas/snapshots/service-discovery-2026-08-07.json` | Discovery snapshot |

## 2. Screenshots (user-supplied, WhatConverts console)

| File | Proves |
| --- | --- |
| `evidence/whatconverts-phone-numbers-2026-08-11.png` | 9 tracking numbers; **(214) 301-3385 = `GSAs traffic` / Google Call Extension**, no swap number, never checked out; **(214) 301-4622 = `Website Traffic` / All Traffic**, swap number **2143009564**; all forward to `Incoming CF - ProGreen DFW` |
| `evidence/whatconverts-call-flow-2026-08-11.png` | Incoming Call → Call Recording → **Dial `2143009564` / `Direct Call to 2068903969`**, plus an unexplored `No Answer` branch |
| `evidence/whatconverts-google-ads-connection-2026-08-11.png` | **Status Connected · Account `Pro Green - Dallas - Live (8735782888)`** · Lead Conversion Name `Whatconverts Form` · Call Extension Conversion Name `Whatconverts Calls` · Trigger `New Lead Received` · Value Type `Sales Value` · **Not Updating Existing Conversions** · **Sending Enhanced Conversions**. URL carries **profile 107007** |
| `evidence/whatconverts-google-ads-data-types-2026-08-11.png` | 11 data types all `Sending Data` |

## 3. Google Ads API — fresh SELECT-only reads, 2026-08-11

All pinned to `customer_id=8735782888`. Manager link read from the child's own
`customer_manager_link`. **The MCC was never queried as a target.**

| Query | Yields |
| --- | --- |
| `customer` + `conversion_tracking_setting` | Identity gate; conversion tracking ID **11237210508**; cross-account ID **0**; customer-data terms **accepted**; enhanced conversions for leads **enabled** |
| `customer_manager_link` | **Two ACTIVE managers: `3373711342` and `2815082755`** |
| `conversion_action` (+ metrics, + recency) | **14 actions.** `7717433751` / `7717433754` are new since 08-07 |
| `campaign` breakdown by `segments.conversion_action`, campaign **and** customer level | 90-day: `6617381255` = 4.00, `6886101052` = 2.00, all-conv 22.00 |
| `customer_conversion_goal` | CONTACT/WEBSITE and CONTACT/CALL_FROM_ADS both **biddable** |
| `campaign` settings + performance, two windows | Budget, bidding, networks, geo type, IS, invalid clicks |
| `campaign_criterion` | 737 criteria: 74 locations, 620 negatives, 3 devices, 7 schedules, 6 IP blocks |
| device criteria with **proto field-presence** check | DESKTOP/TABLET `bid_modifier` **explicitly set to 0.0 (−100%)**; MOBILE unset |
| `ad_group`, `keyword_view`, `search_term_view` | Ad-group and keyword performance, Quality Score components, 444 search terms |
| `ad_group_ad` | RSAs with headlines, descriptions, **pinning**, strength, final URLs |
| `asset`, `campaign_asset`, `ad_group_asset`, `customer_asset` | Call asset `89872541418`; 2 promotion assets → `offerdfw.*`; **sitelinks linked at ad-group level (27/22/22)**; **zero customer-level assets** |
| `geographic_view`, `geo_target_constant` | All delivery is DFW `LOCATION_OF_PRESENCE` |
| segments: device, hour, day-of-week, network | 100% mobile; hours 8–19 account time; Monday $564.55 / 0 conv; 107 partner impressions in-window |

Scripts held at the session scratchpad path. **Nothing was written into the project tree by
the query tooling.**

## 4. Live web inspection — GET-only, 2026-08-11

| Target | Key evidence |
| --- | --- |
| `/dfw/offer-sprinkler-repair-a/` | Renders **(214) 301-4622**; `tel:(214) 301-4622` **plus** broken `tel:%91phone%93`; GTM-NZSMS9RB + GTM-54Q4TVXF + G-5JMRW1LBMF + G-MHX199EBNJ + AW-11240766632; `gform_2` with **empty** `gform_field_values`; **zero** gclid/gbraid/wbraid/utm in HTML |
| `/dfw/offer-sprinkler-repair-b/` | **Redirects to Page A** with sticky `nabAlternative=0`; otherwise identical defects |
| Nelio config, read from **both** pages | `experimentId 3619`, `participationChance 100`, `alternatives = [{postId 3332, testAgainstExistingContent}, {postId 3369, isExistingContent}]`. **Page A = 3332, Page B = 3369** → bidirectional ≈50/50 |
| **`offerdfw.progreenlandscapesolutions.com`** | **Renders `tel:2143013385` / +1 (214) 301-3385.** GTM-NZSMS9RB **only**. No Nelio, no NitroPack, no FB/Nextdoor pixel, **no broken `tel:` placeholder**. Two Gravity Forms, both with empty `gform_field_values` |
| WhatConverts runtime | Script **`s.ksrndkehqnwntyxlhgto.com/107007.js?ver=7.0.3`**; cookies `wc_visitor`, `wc_client`, `wc_client_current`, `wc_swap`; functions `wc_visitor_init`, `wc_form_ypbib` |
| Browser localStorage | Both Google website-call records: `inV_CKe1xtMZEIzzqO4p,2143013385` and `AkKoCM2mqNMZEKj5gfAp,5128902716` |
| `gtm.js` for both containers | GTM-NZSMS9RB carries `__gclidw`, `__awct`, `__awcc` with **(214) 301-3385**. GTM-54Q4TVXF carries Facebook pixel `1455418062885315`, Nextdoor `440513cd-3237-4a70-9ca7-0e129ce37252`, and a `"thank-you"` URL trigger |

**Footprint disclosed:** these page loads register ordinary pageview telemetry in Nelio, GA4,
and the Ads tags — the same footprint as any visitor. **No phone link was clicked, no form
submitted, no chat opened, no lead generated, and no call placed.**

## 5. Blocked

| Item | Reason |
| --- | --- |
| WhatConverts console (pool settings, assigned numbers, URL triggers, send log) | **Login barrier** at `leads.greenmarketingfl.com` in the automation browser profile. No credentials entered; none requested |
| Manager `2815082755` | **ClickCease, authorized [USER]. Never to be queried.** |
| `AW-11240766632` owner | **[UNVERIFIED].** Austin configuration suspected. **No associated account may be queried** |

---

## 6. Second fresh API pass — 2026-08-11 (preview run)

Identity gate re-run and **PASSED** before any query. 28 `SELECT`-only queries, **0 errors**,
all pinned to `8735782888`.

| Query group | New evidence |
| --- | --- |
| `customer` + conversion tracking setting | **Account-level tracking template routes through `monitor.clickcease.com` and hard-codes `ccpturl=offerdfw.progreenlandscapesolutions.com`** — not previously recorded |
| `customer_manager_link` | `2815082755` (ClickCease) + `3373711342` (Green Marketing), both ACTIVE |
| `conversion_action` ×3 windows + recency | 14 actions; `7717433751` / `7717433754` still **zero received**; **no conversion of any kind since 2026-07-31** |
| `customer_conversion_goal`, `campaign_conversion_goal` | CONTACT/WEBSITE and CONTACT/CALL_FROM_ADS both **biddable** |
| `ad_group_ad` URL fields | **18 URL-bearing ads** mapped: 3 serving, 15 not serving |
| `asset` + `campaign_asset` + `ad_group_asset` + `customer_asset` | **Promotion links on the live campaign are `REMOVED`** — corrects the earlier "live dependency" claim. Zero account-level assets |
| `campaign` / `ad_group` / `ad_group_criterion` URL fields | Campaign templates **override** the account ClickCease template. Three campaigns carry a **wrong `utm_id`** |
| `campaign_criterion` LOCATION + `geo_target_constant` | **74 criteria exported with IDs**: 70 ZIPs, 3 cities, 1 airport, PRESENCE/PRESENCE, zero negatives |
| `campaign_criterion` DEVICE with field-presence | DESKTOP `30000` and TABLET `30002` **explicitly set to 0.0 (−100%)**; MOBILE `30001` unset |
| `campaign_criterion` AD_SCHEDULE | 08:00–20:00 ET × 7 days — **equals the confirmed 7 AM–7 PM CT** |
| `campaign_budget` + daily spend | $32.50/day; **MTD $369.98 over 11 days, 0 conversions**; IS lost to budget **34.44%** |
| `search_term_view` | 484 rows; **$332.49 competitor/out-of-market waste, 0 conversions**; **zero** cost/price/quote/estimate queries served |

**Landing-page draft self-check** — `landing-page-draft/index.html` passes all 12 automated
compliance checks: base number present ×10, all `tel:` hrefs valid E.164, single `<h1>`, all 14
hidden attribution fields present, and **zero occurrences** of the pool number, the call-asset
number, `tel:%91phone%93`, 10% OFF, Austin/512 identifiers, out-of-scope services, third-party
pixels, `__awcc`, Nelio, or unconditional same-day language.
