# 00 — Identity and Source Log

**Client:** Pro Green Landscape Solutions — Austin
**Exact child account name:** `Pro Green - Austin - Live`
**Child customer ID:** `7380491929` (supplied as 738-049-1929)
**Exact service:** outdoor design & build
**Vertical:** hardscaping (core Green Marketing vertical; no scope approval required)
**Work-order mode:** READ
**External writes performed:** **NONE**

---

## 1. Identity result

| Check | Method | Result |
|---|---|---|
| Manager relationship | `customer_client` read from the configured `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | `3373711342` "Green Marketing", level 0, manager. Target is a direct level-1 child. **Discovered read-only, not inferred from a browser URL or from another client file.** |
| Exact ID match | `SELECT customer.id … FROM customer` | `7380491929` — exact match |
| Exact name match | same query | `Pro Green - Austin - Live` — exact, character-for-character |
| `- live` marker | case-insensitive contains | present |
| Manager account? | `customer.manager` | false |
| Test account? | `customer.test_account` | false |
| Account status | `customer.status` | ENABLED |
| Sibling-account safety | `customer_client` listing | `Pro Green - Dallas - Live` (8735782888) and `Pro Green - Houston - Live` (1556242048) also exist in the MCC. Neither was read. |
| Repo account selector | `scripts/list_live_accounts.py` | `Identity: PASS` |
| Repo setup verifier | `scripts/verify_setup.py --online` | `Connection: OK … Preflight: PASS` |
| Work-order validator | `scripts/validate_work_order.py` | `PASS \| Pro Green - Austin - Live \| 7380491929 \| hardscaping \| outdoor design & build` |
| Location manifest validator | `scripts/validate_location_targets.py` | `PASS \| 0 proximity + 19 postal + 5 named = 24 positive \| PRESENCE` |
| Repo unit tests | `pytest tests -q` | 465 passed |

**No name, ID, service or vertical mismatch was found. The gate passed.**

## 2. Account metadata as observed

| Field | Value |
|---|---|
| Currency | USD |
| **Account time zone** | **America/New_York** — the served market is Austin, `America/Chicago`. Every Google Ads report boundary, ad schedule and hour-of-day figure in this package is in **Eastern** time. This mismatch is itself a finding (see 02, P1-1). |
| Auto-tagging | enabled |
| Conversion tracking | `CONVERSION_TRACKING_MANAGED_BY_SELF`, conversion tracking ID `11240766632` (matches the `AW-11240766632` gtag found on every landing page) |
| Cross-account conversion tracking | not set |
| Enhanced conversions for leads | enabled |
| Customer data terms accepted | true |
| Global site tag present | true |
| Account-level final URL suffix | empty |
| Account-level tracking template | ClickCease redirect — see the discrepancy note below |
| Optimization score | 0.799 — recorded as a diagnostic only; it is not a Green Marketing KPI |

## 3. Recorded discrepancy — account tracking template

The very first read of `customer.tracking_url_template` in this session printed the ClickCease
template with `ccpturl=progreenlandscapesolutions.com`. Every subsequent read returned the same
template with `ccpturl=offer.sehydroseed.com`.

| Read | Value of `ccpturl` |
|---|---|
| 1st read, initial discovery script | `progreenlandscapesolutions.com` |
| 2nd read, deep account read | `offer.sehydroseed.com` |
| 3rd–5th reads, three consecutive isolated reads | `offer.sehydroseed.com` (identical SHA-256 prefix `1e673a0d69e9` each time) |
| 6th read, the original discovery script re-run unchanged | `offer.sehydroseed.com` |

**Current verified truth: `ccpturl=offer.sehydroseed.com`.** Four consecutive reads agree and the
sixth read used the identical code path as the first. Two explanations remain open: a human edited
the field between the first and second read, or the first observation was faulty. This is recorded
rather than resolved. `change_event` exposes no customer-level row for it, and Google caps
`change_event` at 30 days regardless.

**Consequence for execution:** the preflight snapshot required before any approved write must
re-read this field and compare it against the value recorded in `01_fresh_account_snapshot.json`.
If it has drifted again, the `EXISTING_RESOURCES` fingerprint is invalidated and must be regenerated.

## 4. Sources used, in Green Marketing priority order

| # | Source | Access | Timestamp | Status |
|---|---|---|---|---|
| 1 | This handoff, `clients/pro-green-austin/work-order.yaml`, `clients/pro-green-austin/client.yaml` | local | 2026-08-18 | validated |
| 2 | Google Ads API v25, child `7380491929`, 78 read-only GAQL SELECT queries | `GoogleAdsService.search` via the repo read-only guard | 2026-08-18 | **0 read errors** |
| 2 | `GeoTargetConstantService.suggest_geo_target_constants` for all 24 supplied labels | read-only | 2026-08-18 | complete |
| 3 | 13 live final URLs, desktop + mobile, real Chromium browser | Playwright, GET only | 2026-08-18 | 13 of 13 reached |
| 3 | `https://progreenlandscapesolutions.com/austin/` and its `/austin/services/` link graph | Playwright, GET only | 2026-08-18 | complete |
| 4 | `CLAUDE.md`, `config/agency.yaml`, `config/verticals.yaml`, `references/verticals/hardscaping.md`, `references/verticals/landscaping.md` | local | 2026-08-18 | read in full |
| — | Official Austin Google Business Profile | **not attempted** | — | **UNAVAILABLE** (see below) |
| — | CRM / WhatConverts outcome data | **not attempted** | — | **UNAVAILABLE** (see below) |

### Why a real browser was required

Both hosts sit behind SG-Captcha, which serves non-JS clients an empty stub. `curl` or a plain
fetch would have produced a false "no tracking installed" finding. All landing-page evidence in
this package came from a real Chromium session with the interstitial allowed to clear normally.
Desktop navigation was initially refused with HTTP 403; a current Chrome user-agent plus a warm-up
navigation to the site root resolved it. Pages were paced 8–12 seconds apart.

## 5. Sources that were NOT read, and what that limits

| Source | Why not | What stays unproven |
|---|---|---|
| **Google Business Profile** | No unambiguous first-party listing identifier is recorded in the client file, and the Business Profile API is not configured in this environment. Guessing a listing would risk importing another business's reviews, hours or categories. | Whether the "Over 20 Years Of Experience" claim is supported by a GBP field; GBP categories; review counts. The Google Ads audit is unaffected — `Local actions` conversions are analysed from account data alone. |
| **WhatConverts API** | `WHATCONVERTS_API_TOKEN` exists in `.env`, but reading lead records would pull lead PII into this workspace, and no lead-handling authorisation is in the work order. | Qualified-lead, estimate, sold-job, revenue and gross-profit figures. Section 13 of the handoff is therefore answered as "inputs missing", with the exact missing fields named in `02_executive_audit.md`. |
| **CRM** | None is named in `client.yaml`. | Same as above. |
| **ClickCease** | Fetching the tracker URL would register a synthetic click in the client's ClickCease account. | Whether the redirect currently preserves GCLID. Named as a controlled test in `11_exact_change_plan.yaml`, SIT-002. |
| **A test form submission** | Prohibited in READ mode. | Whether the landing-page form-submit conversion fires. Strong circumstantial evidence exists (see 07); the confirming test is scoped in SIT-002. |
| **Dallas 8735782888 / Houston 1556242048** | Out of scope. Client-truth rules forbid using a sibling account's facts as Austin facts. | Nothing needed. Cross-market contamination was detected from within the Austin account. |

## 6. Data retention and coverage limits

| Limit | Effect |
|---|---|
| Earliest date with any spend | **2023-07-01**. Nothing before that exists to read. |
| `change_event` | Google caps the start date at **30 days**; `START_DATE_TOO_OLD` beyond that. 43 events retrieved for 2026-07-20 → 2026-08-18. `change_status` was read separately for a longer resource-level view (1,398 rows). Change history older than 30 days is **not retrievable**. |
| `search_term_view` | All-time spend visible in search terms is **$21,562.51 against $51,242.71 of campaign spend, about 42%**. Google withholds low-volume queries. For the two live campaigns the visible share is **$851.62 of $1,754.48, about 49%**. **This export does not contain every historical search term and no claim in this package assumes it does.** |
| Performance Max search terms | `search_term_view` does not cover PMax. The paused `Leads-Performance Max-Austin` campaign's $7,587.51 of spend has no term-level detail here. |
| `call_view` | Carries no `segments.date`; it returns the retained call log (216 calls). Not a fixed window. |
| Quality Score | Populated for only 6 of the 48 live keywords. The rest report 0, which means "not enough data", not "zero". |

## 7. Artifact conventions

The handoff asked for `artifacts/pro-green-austin/YYYY-MM-DD_full-audit/`. The repository's own
convention keeps machine data under `clients/<slug>/snapshots/` and narrative under
`reports/<slug>/`. Both are honoured: the numbered deliverables live at the requested path, and the
raw 80.3 MB read plus every intermediate JSON stays under `clients/pro-green-austin/snapshots/`.

| File | Contents |
|---|---|
| `clients/pro-green-austin/snapshots/deep-read-2026-08-18.json` | 80.3 MB raw read, 78 queries, 0 errors |
| `clients/pro-green-austin/snapshots/all-time-read-2026-08-18.json` | independent all-history read |
| `clients/pro-green-austin/snapshots/geo-resolution-2026-08-18.json` | geo crosswalk source data |
| `clients/pro-green-austin/snapshots/landing-pages-2026-08-18.json` | landing-page audit, first pass |
| `clients/pro-green-austin/snapshots/landing-pages-retry-2026-08-18.json` | landing-page audit, retries |
| `clients/pro-green-austin/snapshots/landing-page-attribution-2026-08-18.json` | hidden-field, consent and dataLayer inspection |
| `clients/pro-green-austin/snapshots/search-term-verdicts-*.json` / `.csv` | term-level verdict tables |
| `clients/pro-green-austin/location-targets.yaml` | validated 24-location manifest |

## 8. Secrets and PII

No OAuth secret, developer token, refresh token, API key or webhook secret appears in any file in
this package. Only environment-variable **names** are referenced. `change_event.user_email` was
redacted at read time. Search-term strings were scrubbed for e-mail addresses and long digit runs
before they were written to disk, and non-service term strings were never printed to the console.
`scripts/plan_fingerprint.py` runs `assert_no_embedded_secrets` over the change plan before
producing any fingerprint.
