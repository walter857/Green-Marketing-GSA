# Pro Green - Dallas - Live â€” Continuation / Status

- **Document type:** local continuation record (planning and diagnosis only)
- **Created:** 2026-08-10
- **Last updated:** 2026-08-11
- **Mode:** planning + diagnosis. No Google Ads write of any kind is authorized.

---

## 1. Verified account identity

Re-verified from `clients/pro-green-dallas/snapshots/audit-2026-08-07.json` on 2026-08-10.
No fresh API call was made for this continuation; a fresh read-only identity check is still
required immediately before any future Google Ads operation.

| Field | Value | Source |
| --- | --- | --- |
| Exact child account name | `Pro Green - Dallas - Live` | snapshot `identity.descriptive_name` |
| Child customer ID | `8735782888` | snapshot `identity.customer_id` |
| Manager customer ID | `3373711342` | snapshot `manager_link.manager_customer_id` |
| Manager link status | `ENABLED`, level 1 | snapshot `manager_link` |
| Manager account? | `false` | snapshot `identity.manager` |
| Test account? | `false` | snapshot `identity.test_account` |
| Currency | `USD` | snapshot `identity.currency_code` |
| Account time zone | `America/New_York` | snapshot `identity.time_zone` |
| Vertical | landscaping | `work-order.yaml` |
| Exact primary service | sprinkler and irrigation repair | `work-order.yaml` |

Name, ID, manager ID, vertical, and service match `client.yaml` and `work-order.yaml` exactly.
`work-order.yaml` passes `scripts/validate_work_order.py` (PASS).

### 1.1 Confirmed customer-facing identity â€” confirmation #1, 2026-08-11

Confirmed by the user on 2026-08-11. These are **five separate fields** and must not be
collapsed into one another.

| Field | Confirmed value | Nature |
| --- | --- | --- |
| **Customer-facing business name** | **Pro Green Landscape Solutions** | Public-facing. Use in ad copy, landing-page headings, extensions, and any customer-visible text. |
| **Location / market** | **Dallas, Texas â€” Dallasâ€“Fort Worth market** | Market descriptor. Not part of the public business name. |
| **Google Ads account name** | **Pro Green - Dallas - Live** | Internal Google Ads label only. Never customer-facing. |
| **Google Ads child customer ID** | **8735782888** | **Definitive account identifier.** |
| **Manager account ID** | **3373711342** | Manager/MCC. Never substituted for the child ID. |

**User's stated rule, in force from this point:** "Dallas" identifies the market and the
Google Ads account. It is **not** part of the public-facing business name unless the
website explicitly presents it that way.

**Standing verification rule, added at the user's instruction:** before **every** Google
Ads query and **every** proposed change, verify the account name, the location/market, the
child customer ID, and the manager ID **together**, as a set. The child customer ID is
the definitive identifier; a match on name alone is not sufficient, and a match on ID alone
does not excuse skipping the other three.

**Discrepancy surfaced, not resolved, and nothing edited.** `clients/pro-green-dallas/client.yaml`
currently carries `client.business_name: Pro Green`, which is shorter than the confirmed
customer-facing name **Pro Green Landscape Solutions**. `client.yaml` was **not** modified â€”
editing it is a separate change requiring its own approval, and it is recorded here so the
conflict is visible before any asset, ad, or landing-page copy is drafted from either value.
Related: the domain is `progreenlandscapesolutions.com`, which is consistent with the
confirmed longer name.

Not established by this confirmation and still open: whether the landing pages currently
present the business name in the confirmed form. Both pages were inspected for phone,
tagging, and click-ID behavior only; the rendered business name was not recorded and must
not be assumed.

---

## 2. Checkpoint recovery status

| Item | Status |
| --- | --- |
| `AGENTS.md` | read |
| `CLAUDE.md` | read |
| `clients/pro-green-dallas/client.yaml` | present, read |
| `clients/pro-green-dallas/work-order.yaml` | present, read, validator PASS |
| `clients/pro-green-dallas/service-discovery.yaml` | present |
| `clients/pro-green-dallas/snapshots/audit-2026-08-07.json` | present, 9.2 MB, parses cleanly |
| `clients/pro-green-dallas/snapshots/service-discovery-2026-08-07.json` | present |
| Prior audit/status/continuation markdown | **none existed** â€” this file is the first |
| Git | project is **not** a git repository; no `git status` or diffs to inspect, nothing discarded |

Audit snapshot integrity re-confirmed: `queries_executed` = 54, `read_errors` = 0,
`google_ads_changes_made` = `false`.

---

## 3. Confirmed audit numbers (last_90 = 2026-05-09 .. 2026-08-06)

| Metric | Value |
| --- | --- |
| Cost | $2,904.68 |
| Impressions | 3,475 |
| Clicks | 171 |
| CTR | 4.92% |
| Avg CPC | $16.99 |
| Conversions (bidding column) | 6.00 |
| All conversions | 21.00 |
| Reported CPL | $484.11 |
| Invalid clicks | 25 (12.76%) |
| Device split | **100% MOBILE** â€” the only device row in the snapshot |

### Where the 6 conversions actually came from

| Conversion action | ID | Conversions | All conv. |
| --- | --- | --- | --- |
| Calls from Ads (call asset, AD_CALL) | 6617381255 | 4.00 | 4.00 |
| Pro Green DFW - Lp - Submit Lead Form | 6886101052 | 2.00 | 2.00 |
| **Pro Green DFW - Lp - Phone Call Leads (WEBSITE_CALL)** | **6886103719** | **absent â€” 0** | **0** |
| Local actions - Website visits | 6608032928 | 0 | 4.00 |
| Local actions - Directions | 6609874719 | 0 | 1.00 |
| Local actions - Other engagements | 6669693044 | 0 | 10.00 |

Campaign-level `phone_calls` metric = 8 for Irrigation & Sprinklers (call-asset calls),
of which 4 met the 60-second qualification and counted.

**This is the core problem:** conversion action `6886103719` is `ENABLED`,
`primary_for_goal = true`, `include_in_conversions_metric = true`,
type `WEBSITE_CALL`, `phone_call_duration_seconds = 30` â€” and it recorded
**zero** conversions across 171 clicks of 100% mobile traffic over 90 days.
Website calls from a mobile landing page cannot plausibly be zero. Until this
is explained, the $484.11 CPL is not a usable number and no bidding decision
may be based on it.

---

## 4. Campaign under work

| Field | Value |
| --- | --- |
| Campaign | Irrigation & Sprinklers |
| Campaign ID | 20315156610 |
| Status | ENABLED / SERVING / ELIGIBLE |
| Channel | SEARCH |
| Bidding | TARGET_SPEND (Maximize Clicks) |
| Budget ID | 12723712793 |
| Daily budget | $32.50, STANDARD, not shared |
| Search Partners | off |
| Display | off |
| AI Max | off |
| Geo target type | PRESENCE / PRESENCE |
| Tracking template | `{lpurl}?utm_source=google&utm_medium=cpc&utm_campaign={_campaign}&utm_id=20315156610` |
| Start | 2023-06-28 |

Other campaigns, all PAUSED: Drainage 21718922354, Winterization 22027188372,
Outdoor Lightning 22255200632, Leads-Performance Max-Sprinkler-Repair 22379036365
(PMax, $250/day budget, PRESENCE_OR_INTEREST, Display + Search Partners on).

Landing pages in scope for this service:
- https://progreenlandscapesolutions.com/dfw/offer-sprinkler-repair-a/
- https://progreenlandscapesolutions.com/dfw/offer-sprinkler-repair-b/

---

## 5. Open findings carried forward from the audit

| # | Finding | Status |
| --- | --- | --- |
| 1 | Website-call action 6886103719 may be missing or broken on both landing pages | **Page A root cause found 2026-08-10 â€” see Â§6.** Page B not yet inspected. |
| 2 | Desktop criterion 30000 and tablet criterion 30002 excluded at âˆ’100% | open |
| 3 | Account time zone `America/New_York` for a Dallas business | open â€” mutability unverified |
| 4 | Campaign uses Maximize Clicks / TARGET_SPEND | open â€” blocked on clean data |
| 5 | All RSA assets pinned; no combination testing possible | open |
| 6 | Competitor and DIY search-term waste | open |
| 7 | Winterization and installation/design sitelinks dilute repair intent | open |
| 8 | DFW Airport geo target 9041382 to review for removal | open |
| 9 | Phrase negative `cost` conflicts with GM protected buyer-intent policy | open |
| 10 | Duplicate conversion actions exist, currently excluded from Conversions | open |
| 11 | Bidding migration must wait for trustworthy tracking + clean data | deferred by design |

Approved strategic direction: **staged combination â€” tracking first, then careful
in-place improvements.** The existing campaign structure is usable and will not be
replaced. No replacement campaigns at this stage.

---

## 6. Website-call tracking diagnosis log

**Objective:** determine whether conversion action `6886103719`
(`Pro Green DFW - Lp - Phone Call Leads`, type `WEBSITE_CALL`, 30-second
qualification) and its Google forwarding-number snippet are installed and firing on
both sprinkler-repair landing pages.

### Environment access check â€” 2026-08-10

Server-side GET from this environment is **blocked**. Both landing pages return an
HTTP 202 SiteGround bot challenge:

```
<meta http-equiv="refresh" content="0;/.well-known/sgcaptcha/?r=%2Fdfw%2Foffer-sprinkler-repair-a%2F...">
```

No page HTML is retrievable programmatically. The 2026-08-07 audit run has the same
gap: `target.fetch_landing_pages = true` but `target.allowed_hosts = []` and the
snapshot contains no landing-page section. Diagnosis therefore proceeds as
user-guided manual inspection in a real browser.

### What must be true for 6886103719 to fire

1. The Google Ads tag (`gtag.js` with an `AW-` conversion ID) loads on the page.
2. A phone-snippet `gtag('config', 'AW-XXXXXXXXX/<label>', {'phone_conversion_number': '...'})`
   call exists, using the label belonging to 6886103719.
3. The `phone_conversion_number` value matches the number rendered on the page
   **exactly** as displayed â€” Google swaps by string match.
4. Both the visible number and the `tel:` href are swapped, not just the visible text.
5. The visitor arrives with a real `gclid` â€” number swapping does not occur on
   direct/organic visits.
6. Call reporting is enabled at the account level and a forwarding number is
   available for the target area.

Any one of 1, 2, 3, or 4 failing produces exactly the observed symptom: zero
website calls, mobile traffic, no error anywhere in the Google Ads UI.

### Steps

| # | Step | Date | Result |
| --- | --- | --- | --- |
| 1 | Page A raw source (Ctrl+U), search `AW-` | 2026-08-10 | **0 matches.** GTM container `GTM-NZSMS9RB` present in raw source; GTM installation test green for Page A. No phone number clicked, no form submitted, no lead triggered. |
| 2 | Page A runtime network + DOM capture, performed by agent in Chrome | 2026-08-10 | **COMPLETE â€” root cause identified.** See Â§6.1â€“Â§6.6 below. |

### 6.1 Method and tool disclosure

Performed by the agent using the **Claude in Chrome MCP browser tools**
(`mcp__claude-in-chrome__*`) â€” navigate, network-request reader, and read-only
JavaScript evaluation. There is no separate `chrome-devtools-mcp` server connected to
this session; the Claude in Chrome tools provide the equivalent network and DOM
inspection and were used for every observation below. No other browser tool was used.

Actions taken on Page A: navigate, reload, wheel scroll, mouse hover, read-only DOM
reads, and one same-origin `GET` fetch of the page's own HTML. **No phone link was
clicked, no form was submitted, no lead/call/chat was triggered, and nothing in GTM,
Google Ads, or the website was modified.** No SiteGround captcha appeared in the
browser session â€” the page loaded normally. Page B was not touched.

Session values redacted from this record: SiteGround `sol=` session token, Google
`cid=` identifiers, and cookie/header data. No `gclid`, `gbraid`, or `wbraid` was
present â€” the inspection was a direct visit with no ad-click parameters.

### 6.2 Google tags observed on Page A

| Item | Value | Status |
| --- | --- | --- |
| GTM container 1 | `GTM-54Q4TVXF` | loads, HTTP 200 |
| GTM container 2 | `GTM-NZSMS9RB` | loads, HTTP 200 |
| GA4 property 1 | `G-5JMRW1LBMF` | loads, HTTP 200 |
| GA4 property 2 | `G-MHX199EBNJ` | loads, HTTP 200 |
| **Google Ads account 1** | **`AW-11237210508`** | loads, HTTP 200 |
| **Google Ads account 2** | **`AW-11240766632`** | loads, HTTP 200 |
| Google call-tracking runtime | `_googCallTrackingImpl`, `_gaPhoneImpl` present | active |

`window.google_tag_manager` resolves to
`[GTM-54Q4TVXF, GTM-NZSMS9RB, G-5JMRW1LBMF, G-MHX199EBNJ, AW-11240766632]`.

**Two Google Ads accounts, two GA4 properties, and two GTM containers are all firing on
a single landing page.** Which `AW-` ID belongs to child account `8735782888` is not yet
established and cannot be read from the page.

### 6.3 The `/wcm` website-call requests â€” both fire, both misconfigured

Two website-call number-swap requests fire, both HTTP 200:

| Google Ads account | Endpoint | `dn` (number the tag is told to swap) | `cl` (conversion label) | Status |
| --- | --- | --- | --- | --- |
| AW-11237210508 | `googleadservices.com/pagead/conversion/11237210508/wcm` | `2143013385` â†’ **(214) 301-3385** | `inV_CKe1xtMZEIzzqO4p` | 200 |
| AW-11240766632 | `googleadservices.com/pagead/conversion/11240766632/wcm` | `5128902716` â†’ **(512) 890-2716** | `AkKoCM2mqNMZEKj5gfAp` | 200 |

Both are followed by `google.com/pagead/attribution/wcm` calls with the same `dn`/`cl`.

### 6.4 The number actually on the page â€” the mismatch

Server HTML for Page A (same-origin `GET`, HTTP 200, 262,440 bytes) hard-codes:

| Where | Number |
| --- | --- |
| Header `tel:` link, body `tel:` links, visible text | **(214) 300-9564** |
| JSON-LD `contactPoint` (structured data only) | (214) 301-4622, (214) 974-8672 |
| Primary CTA button "Get 10% OFF Now!" | `href="tel:%91phone%93"` â€” **unresolved placeholder, not a number** |

**The mismatch, stated plainly:**

| Source | Number |
| --- | --- |
| Configured in AW-11237210508 website-call tag | (214) 301-3385 |
| Configured in AW-11240766632 website-call tag | (512) 890-2716 â€” **a 512 Austin area code on a Dallas page** |
| Actually rendered on Page A | **(214) 300-9564** |

Google's website-call conversion replaces a phone number by **exact string match**
against the value in `phone_conversion_number`. Neither configured number appears
anywhere on Page A. Google therefore has nothing to swap, no forwarding number is ever
inserted, and conversion action `6886103719` can never fire. This matches the audit
observation exactly: **0 website calls across 171 clicks of 100% mobile traffic.**

### 6.5 A third-party service is already swapping the number

At runtime the visible number and every `tel:` href change from **(214) 300-9564** to
**(214) 301-4622**. This swap happened on a **direct visit with no `gclid`**. Google
inserts a forwarding number only for visitors arriving from an ad click, so this swap is
**not** Google's. The only other candidate observed is a POST to
`process.iconnode.com/google-ads/`, a third-party call-tracking endpoint.

Working conclusion â€” **high confidence, one confirmation step outstanding**: a
third-party dynamic-number-insertion service overwrites the site's number before Google's
tag runs. Google's tag is left hunting for a number that no longer exists on the page
(and never did). Calls route through the third party, whose outcomes never reach Google
Ads. Call-**asset** calls bypass the website entirely, which is why those 8 calls /
4 conversions were the only phone data the account ever recorded.

### 6.6 Two further defects found on Page A

1. **The primary call CTA is broken.** The "Get 10% OFF Now!" button's href is
   `tel:%91phone%93` â€” a literal unresolved shortcode, not a phone number. On traffic
   that is 100% mobile, the main call-to-action does not place a call. This is a
   conversion-rate defect independent of tracking.
2. **No click-ID capture on the form.** The only form on the page (`gform_2`, 19 fields)
   carries no hidden `gclid`, `gbraid`, `wbraid`, or UTM field â€” the sole hidden field is
   `gform_source_page_number_2`. `CLAUDE.md` requires GCLID and UTMs preserved into the
   CRM; today that chain is broken at the form.

### 6.7 Tag delivery is deferred by NitroPack

The site runs NitroPack (`nitrocdn.com`). On first load **all 43 scripts are inline
placeholders and 21 carry `type="nitropack*"`** â€” `window.dataLayer` is `undefined`,
`window.google_tag_manager` is absent, and **zero** Google requests fire. After a page
load, a reload, and two wheel scrolls, still zero. Tags loaded only after **mouse
movement**, at which point all six Google tags fired within seconds.

Implication: no measurement of any kind exists for a visitor who lands and leaves without
the interaction event NitroPack waits for. Desktop wheel-scroll behavior does not predict
mobile touch behavior, so **the mobile trigger threshold is unverified and must be
tested separately** before any conclusion is drawn about how much traffic goes untracked.

### 6.8 GAQL lookup of conversion action 6886103719 â€” blocked, then COMPLETED

**Status: complete.** First attempt on 2026-08-10 failed on an expired OAuth refresh
token (recorded below for the audit trail). The token was regenerated by the user and the
identical prepared query ran successfully the same day. Results in Â§6.8.1â€“Â§6.8.4.

#### First attempt â€” blocked (historical)

**The query never reached Google Ads.** The Google Ads API client
failed at the OAuth token-refresh step, before any request was sent:

```
google.auth.exceptions.RefreshError: Reauthentication is needed.
```

Confirmed with `scripts/verify_setup.py --client clients/pro-green-dallas/client.yaml`:

- Offline preflight: `Credential variable names: present` â†’ `Preflight: PASS`.
  All five `GOOGLE_ADS_*` variables exist, so nothing is missing from `.env`.
- `--online` preflight: same `RefreshError`.

So the blocker is the stored **refresh token being rejected by Google**, not a missing
variable, not the query, and not the account. No API call was made against customer
`8735782888`. No credential value was read, printed, or logged, and `.env` was not
modified.

The queries were prepared and are ready to run unchanged once authentication is restored.
Both are `SELECT`-only, filtered to `WHERE conversion_action.id = 6886103719`, and pinned
to customer `8735782888`, behind the existing fresh identity + manager-link assertions:

1. **Combined:** `customer.id`, `customer.descriptive_name`,
   `conversion_action.{resource_name, id, name, status, type, origin, owner_customer,
   phone_call_duration_seconds, include_in_conversions_metric, primary_for_goal,
   tag_snippets}`, `metrics.conversion_last_conversion_date`,
   `metrics.conversion_last_received_request_date_time`.
2. **Split fallback** (attributes-only + metrics-only) if the API rejects selecting the
   repeated `tag_snippets` field alongside metrics.

Script held at the session scratchpad path; nothing was written into the project tree.

#### Caveat to set expectations on what the snippet can prove

`conversion_action.tag_snippets` returns the AW conversion ID and the conversion label,
which is exactly what is needed to map action `6886103719` to one of the two `AW-` IDs
seen on Page A. It will **not** return the configured `phone_conversion_number` â€”
that value lives in the website's gtag/GTM configuration, not in Google Ads. The
observed `dn=2143013385` and `dn=5128902716` from the Page A `/wcm` requests remain the
only evidence of what each tag is actually configured to swap.

> **Correction to that caveat, based on the returned data.** Google Ads *does* return the
> configured `phone_conversion_number` â€” it is embedded in the generated
> `tag_snippets.event_snippet`. The value is below and it independently confirms the
> `dn` observed on Page A.

#### 6.8.1 Query executed â€” 2026-08-10

One combined `SELECT` against customer `8735782888` only, no fallback split needed
(`queries_run: ["combined"]`, `errors: []`). Preceded by the standard gates, both passing:

- Fresh identity: `8735782888` / `Pro Green - Dallas - Live` / USD / America/New_York /
  manager `false` / test account `false`.
- Manager link: `3373711342` â†’ `8735782888`, level 1, status `ENABLED`.

#### 6.8.2 Conversion action 6886103719 â€” configuration

| Field | Value |
| --- | --- |
| `resource_name` | `customers/8735782888/conversionActions/6886103719` |
| `owner_customer` | `customers/8735782888` â€” **owned by this account, not borrowed** |
| `name` | Pro Green DFW - Lp - Phone Call Leads |
| `status` | ENABLED |
| `type` | WEBSITE_CALL |
| `origin` | WEBSITE |
| `phone_call_duration_seconds` | 30 |
| `include_in_conversions_metric` | true |
| `primary_for_goal` | true |

#### 6.8.3 The tag snippet â€” the mapping, proven

`tag_snippets[0]`, type `WEBSITE_CALL`, page format `HTML`:

- Global site tag references **`G-5JMRW1LBMF`** â€” one of the two GA4 IDs observed loading
  on Page A.
- Event snippet:

```
gtag('config', 'AW-11237210508/inV_CKe1xtMZEIzzqO4p', {
  'phone_conversion_number': '(214) 301-3385'
});
```

| Requested item | Proven value |
| --- | --- |
| 1. Exact AW conversion ID | **AW-11237210508** |
| 2. Exact conversion label | **`inV_CKe1xtMZEIzzqO4p`** |
| 3. Configured `phone_conversion_number` | **(214) 301-3385** |

**The mapping to Page A is exact and unambiguous:**

| | Google Ads API (action 6886103719) | Page A `/wcm` request |
| --- | --- | --- |
| AW ID | AW-11237210508 | `/pagead/conversion/11237210508/wcm` |
| Label | `inV_CKe1xtMZEIzzqO4p` | `cl=inV_CKe1xtMZEIzzqO4p` |
| Phone number | (214) 301-3385 | `dn=2143013385` |

Two independent sources â€” Google Ads' stored configuration and the tag actually deployed
in the browser â€” agree exactly. **Action 6886103719 is the AW-11237210508 `/wcm` request.**

By elimination, the second tag on Page A â€” **AW-11240766632 / `AkKoCM2mqNMZEKj5gfAp` /
(512) 890-2716** â€” is **not** owned by customer `8735782888`. A second, foreign Google Ads
account is running website-call tracking on this client's landing page.

#### 6.8.4 Conversion history â€” the action died on a specific date

| Metric | Value |
| --- | --- |
| `conversion_last_conversion_date` | **2026-02-28** |
| `conversion_last_received_request_date_time` | 2026-08-10 17:03:03.380819 (account tz, ET) |

Two separate facts, and they must not be conflated:

1. **The tag reaches Google.** Requests are being received. The tag is not absent, not
   blocked, and not broken at the transport layer.
2. **It has not produced a conversion since 2026-02-28.** The action worked at some
   point and stopped. The entire 90-day audit window (2026-05-09 â€“ 2026-08-06) sits
   after that date, which is why it shows zero.

**Disclosure â€” the "last received request" timestamp is probably mine.** The Page A
inspection earlier today fired a `/wcm` request to AW-11237210508 at 16:34:06 ET, and I
loaded the page several times after that. 17:03:03 ET is consistent with my own
diagnostic traffic and **cannot be attributed to a real visitor**. No call was placed and
no conversion was created â€” only a request timestamp moved. This field therefore proves
the tag transmits; it proves nothing about organic traffic reaching it.

### 6.9 Request failures observed â€” flagged, not concluded

Every Google **POST** beacon in the capture returned **503**
(`google.com/ccm/collect`, `analytics.google.com/g/collect`,
`google-analytics.com/g/collect`, `google.com/rmkt/collect`,
`process.iconnode.com/google-ads/`), while every **GET** returned 200
(`gtm.js`, `gtag/js`, `viewthroughconversion`, `wcm`, `1p-user-list`).

A clean GET/200-vs-POST/503 split points at this inspection environment's network path,
not at the site. **Recorded as unverified.** It must be re-tested from a normal network
before anyone treats it as a site defect.

#### Interpretation of step 1

Zero `AW-` in raw source is **not** proof the Google Ads tag is missing. Tags deployed
through GTM are injected at runtime and never appear in the raw HTML, so this result is
exactly what a correct GTM-based deployment also looks like. Step 1 narrows the question
rather than answering it: the Google Ads tag is either (a) fired by GTM container
`GTM-NZSMS9RB` at runtime, or (b) genuinely absent. Only a runtime check separates the two.

A green GTM installation checkmark confirms the **container** loads. It says nothing about
whether a Google Ads conversion tag or a phone-snippet tag exists inside that container, or
whether either is set to fire on this page.

#### Naming note for later steps

The Google Ads resource ID `6886103719` never appears on the page. What appears is the
account-level conversion ID (`AW-<9-10 digits>`) plus a per-action conversion label
(alphanumeric). Mapping a label found on the page back to action `6886103719` requires
reading that action's tag setup screen in the Google Ads UI. That mapping is step 3.

#### Container-level caveat

`GTM-NZSMS9RB` is a web container on the client's site. Its contents are not readable from
Google Ads and were not captured in the audit snapshot. If runtime checks show no Google Ads
tag, confirming the fix will require access to the GTM container itself â€” note this as a
possible access dependency for approval batch 1.

---

### 6.11 Page B inspection â€” 2026-08-10

Tools used: `mcp__claude-in-chrome__` â€” `tabs_context_mcp`, `tabs_create_mcp`, `navigate`,
`computer` (wait / hover / screenshot), `read_network_requests`, `javascript_tool`,
`tabs_close_mcp`. No other browser tool. Fresh tab group; the Page A tab had been closed,
so this was a clean browser session. GET-only navigation and read-only JS evaluation.
**No phone link clicked, no form submitted, no call/lead/chat/conversion triggered,
nothing changed in Google Ads, GTM, the website, or any external account. The manager
account was not touched and AW-11240766632's owner was not investigated.** No captcha
appeared.

Footprint disclosure: loading these public pages registers ordinary pageview telemetry in
Nelio, GA4, and the Ads tags â€” the same footprint as any visitor. One harmless query
parameter (`testparam=gm123`) was used to test parameter survival. No click ID, real or
fabricated, was used.

#### 6.11.0 Page B does not stay on screen â€” it redirects to Page A

Navigating to `/dfw/offer-sprinkler-repair-b/` lands the browser on
**`/dfw/offer-sprinkler-repair-a/`**. A direct `GET` of Page B returns **HTTP 200,
153,921 bytes, `<title>Offer Sprinkler Repair B</title>`, `redirected: false`** â€” so the
server serves Page B correctly. The redirect is **client-side**.

Cause, read out of Page B's own HTML: the **Nelio A/B Testing** WordPress plugin
(`wp-content/plugins/nelio-ab-testing`), running:

| Setting | Value |
| --- | --- |
| `experimentId` | **3619** |
| `postId` | 3369 |
| `participationChance` | **100** |
| alternative URLs | `/dfw/offer-sprinkler-repair-a/` â†” `/dfw/offer-sprinkler-repair-b/` |
| `isGA4Integrated` | **false** |
| `hideQueryArgs` | false |
| `ignoreTrailingSlash` | true |
| plugin version | 8.5.2 |
| configured timezone | **-05:00 (Central â€” correct for Dallas)** |

The `?nab=` parameter seen on these URLs is **Nelio's** variant marker, not SiteGround's.
`?nab=0` = the variant Nelio assigned.

#### 6.11.1 Page B server HTML (GET, 200, 153,921 bytes)

| Item | Page B value |
| --- | --- |
| 1. Hard-coded phone number | **(214) 300-9564** (Ã—7) |
| Other numbers present | (214) 301-4622 (Ã—1), (214) 974-8672 (Ã—1) â€” JSON-LD `contactPoint` only |
| 3. `tel:` hrefs | `tel:(214) 300-9564` and **`tel:%91phone%93`** |
| 5. GTM containers | **GTM-54Q4TVXF, GTM-NZSMS9RB** |
| 6. GA4 in source | G-5JMRW1LBMF |
| 7. AW IDs in source | **none** (injected via GTM, same as Page A) |
| `phone_conversion_number` in source | absent (lives in GTM) |
| NitroPack | present |
| iconnode in source | absent |
| meta refresh | 0 |
| 12. `gclid` / `gbraid` / `wbraid` / `utm_` mentions | **0 / 0 / 0 / 0** |
| form elements | 3, **all sharing the id `gform_2`** (duplicate DOM ids) |

#### 6.11.2 Page B runtime, before any interaction

| Item | Observed |
| --- | --- |
| `window.dataLayer` | **undefined** |
| `window.google_tag_manager` | **false** |
| `window.gtag` | **undefined** |
| NitroPack-deferred scripts | **22 of 44** |
| 2. Visible phone numbers | **(214) 300-9564 only** â€” no swap |
| 3. `tel:` hrefs | `tel:(214) 300-9564` Ã—3 + **`tel:%91phone%93`** |
| 4. Main CTA | **"Get Fast Repairs Today!" â†’ `tel:%91phone%93` â€” BROKEN, not a valid telephone link** |
| Google requests fired | **zero** |

#### 6.11.3 What happens when interaction releases the scripts

Hovering released NitroPack's deferred scripts. **Nelio's redirect won the race:** within
seconds the browser was on Page A, and every Google tag then fired *on Page A*.

In both runs of **this single isolated browser session**, no Google tag fired while Page B
was on screen. Every tag request carried:

- `dl=` / `url=` â†’ `â€¦/offer-sprinkler-repair-a/`
- `dr=` / `ref=` â†’ `â€¦/offer-sprinkler-repair-b/`

> **SCOPE CORRECTION â€” 2026-08-10.** An earlier draft of this section said Page B
> reporting is "inverted at the source." **That claim overreached and is withdrawn.**
>
> What is proven: *this* browser session was assigned or redirected from Page B to Page A
> by Nelio, and in that session Page B's own tags never fired.
>
> What is **not** proven: that every Page B visitor is always redirected to Page A. A
> single browser identity receives a single Nelio assignment, and that assignment is
> sticky â€” so one session cannot distinguish "always redirects" from "was assigned
> variant A this time." `participationChance: 100` means every visitor *enters* the
> experiment; it does not mean every visitor is *sent to Page A*.
>
> Settling this requires either multiple isolated assignments (fresh profiles/incognito,
> cleared Nelio cookies) or a read of the Nelio experiment configuration in WordPress.
> Until then, treat the direction and rate of redirection as **unverified (U13)**.

#### 6.11.4 Items 8â€“11, answered

**8. `/wcm` requests observed** â€” both fired only *after* the redirect, i.e. on Page A:

| AW ID | Label | `dn` | HTTP |
| --- | --- | --- | --- |
| 11237210508 | `inV_CKe1xtMZEIzzqO4p` | `2143013385` â†’ (214) 301-3385 | **200** |
| 11240766632 | `AkKoCM2mqNMZEKj5gfAp` | `5128902716` â†’ (512) 890-2716 | **200** |

(The `ref=` on these carried a stale SiteGround `sol=` session token from the earlier
session â€” **redacted here and not recorded**.)

**9. Correct Pro Green Dallas tag present?** AW-11237210508 / `inV_CKe1xtMZEIzzqO4p` /
(214) 301-3385 â€” **yes, it fires, but on Page A after the redirect, never on Page B.**
Its target number still does not exist on either page.

**10. Second tag present?** AW-11240766632 / `AkKoCM2mqNMZEKj5gfAp` / (512) 890-2716 â€”
**yes**, same behaviour. Also loaded as a full container (`gtag/js?id=AW-11240766632`).

**11. Third-party DNI?** On Page B itself, **no swap was observable** â€” tags never ran
there. After the redirect to Page A, the swap **(214) 300-9564 â†’ (214) 301-4622**
reproduced, and the `process.iconnode.com/google-ads/` POST fired again. Page B's own DNI
behaviour is therefore **untestable in the live flow**, because Page B never survives long
enough to run scripts.

**13. NitroPack deferral?** **Yes, confirmed on Page B** â€” identical to Page A. Zero
Google requests until interaction.

**14. Failed requests?** The same clean split repeated: every Google **POST** beacon 503,
every **GET** 200. Now observed across two independent browser sessions on two different
pages. This consistency strengthens the reading that it is an **inspection-environment
artifact, not a website failure** â€” but it remains unverified until re-tested from a
normal network. No *verified* website request failure was found.

**12. Click-ID capture?** **No.** Zero `gclid`, `gbraid`, `wbraid`, or `utm_` references
anywhere in Page B's HTML. The forms capture nothing.

#### 6.11.5 One piece of good news â€” the redirect preserves query parameters

A test parameter survived the Nelio redirect intact: `/dfw/offer-sprinkler-repair-b/?testparam=gm123`
â†’ `/dfw/offer-sprinkler-repair-a/?nab=0&testparam=gm123`, and the tag requests carried it
in both `url=` and `ref=`. **A `gclid` would survive the redirect.** The attribution loss
identified at the form (Â§6.6.2 / item 12) is a *form* defect, not a redirect defect.

### 6.12 Page A versus Page B

| # | Item | Page A | Page B | Same? |
| --- | --- | --- | --- | --- |
| 1 | Hard-coded phone in server HTML | (214) 300-9564 | **(214) 300-9564** | âœ… identical |
| 2 | Visible number before tags load | (214) 300-9564 | (214) 300-9564 | âœ… |
| 2 | Visible number after tags load | (214) 301-4622 | *never reached â€” redirects first* | âš ï¸ differs by cause |
| 3 | Valid `tel:` hrefs | `tel:(214) 300-9564` | `tel:(214) 300-9564` | âœ… |
| 3 | Placeholder `tel:` href | **`tel:%91phone%93`** | **`tel:%91phone%93`** | âœ… both broken |
| 4 | Main CTA | "Get 10% OFF Now!" â€” broken | "Get Fast Repairs Today!" â€” broken | âœ… both broken |
| 5 | GTM containers | GTM-54Q4TVXF, GTM-NZSMS9RB | GTM-54Q4TVXF, GTM-NZSMS9RB | âœ… |
| 6 | GA4 properties | G-5JMRW1LBMF, G-MHX199EBNJ | G-5JMRW1LBMF in source; both at runtime | âœ… |
| 7 | AW IDs | AW-11237210508, AW-11240766632 | same two | âœ… |
| 8 | `/wcm` AW-11237210508 | fires on page, 200 | fires only after redirect, 200 | âš ï¸ |
| 8 | `/wcm` AW-11240766632 | fires on page, 200 | fires only after redirect, 200 | âš ï¸ |
| 9 | Correct GM tag targets (214) 301-3385 | âœ… present, mismatched | âœ… present, mismatched | âœ… same defect |
| 10 | Second tag targets (512) 890-2716 | âœ… present | âœ… present | âœ… |
| 11 | Third-party DNI swap | observed â†’ (214) 301-4622 | not observable | âš ï¸ |
| 12 | Form captures gclid/UTM | **no** | **no** | âœ… both broken |
| 13 | NitroPack defers tags | âœ… yes | âœ… yes | âœ… |
| 14 | Verified website request failures | none | none | âœ… |
| â€” | Nelio A/B redirect | receives redirected traffic | **redirects away, exp. 3619, 100%** | âŒ asymmetric |
| â€” | Form elements | 1â€“2, id `gform_2` | **3, all id `gform_2`** | âŒ B has duplicate ids |
| â€” | Server HTML size | 262,440 bytes | 153,921 bytes | âŒ |

**The core conclusion is unchanged and now doubled:** both landing pages hard-code
**(214) 300-9564**, and the Green Marketing tag on both is configured to swap
**(214) 301-3385**. There is no page in this campaign on which conversion action
`6886103719` can fire. Page B adds a second, independent failure â€” it never renders long
enough to run a tag at all, and its traffic is reported as Page A.

### 6.10 Evidence grading as of 2026-08-10

#### Proven facts â€” directly observed, reproducible

| # | Fact | Evidence |
| --- | --- | --- |
| P1 | Page A's server HTML hard-codes **(214) 300-9564** in the header and body `tel:` links | same-origin `GET`, HTTP 200, 262,440 bytes |
| P2 | AW-11237210508's website-call tag requests a swap of **`dn=2143013385`** â†’ (214) 301-3385, label `inV_CKe1xtMZEIzzqO4p` | `/pagead/conversion/11237210508/wcm`, HTTP 200 |
| P3 | AW-11240766632's website-call tag requests a swap of **`dn=5128902716`** â†’ (512) 890-2716, label `AkKoCM2mqNMZEKj5gfAp` | `/pagead/conversion/11240766632/wcm`, HTTP 200 |
| P4 | Neither configured number appears anywhere on Page A | P1 vs. P2/P3 |
| P5 | Two Google Ads accounts, two GA4 properties, and two GTM containers all fire on Page A | `window.google_tag_manager` + network log |
| P6 | The "Get 10% OFF Now!" CTA href is `tel:%91phone%93`, an unresolved placeholder | live DOM and server HTML |
| P7 | Form `gform_2` carries no `gclid`/`gbraid`/`wbraid`/UTM hidden field | live DOM |
| P8 | NitroPack defers all 43 scripts; zero Google requests fire on load, reload, or wheel scroll; tags fire only after mouse movement | network log across three navigations |
| P9 | Conversion action `6886103719` recorded **0** conversions in the 90-day audit window | `audit-2026-08-07.json` conversion breakdown |
| P10 | *(resolved)* OAuth refresh token was rejected, then regenerated by the user; the query ran | `RefreshError`, then successful run |
| P11 | Action `6886103719` is owned by `customers/8735782888` and is **AW-11237210508 / `inV_CKe1xtMZEIzzqO4p`** | GAQL `conversion_action.tag_snippets` |
| P12 | Its configured `phone_conversion_number` is **(214) 301-3385** | GAQL event snippet, matching Page A `dn=2143013385` |
| P13 | **The mismatch is proven:** the account's own tag targets (214) 301-3385; Page A renders (214) 300-9564 | P12 vs. P1 |
| P14 | `8735782888`'s account-level conversion ID is **11237210508**, so the second tag on Page A (**AW-11240766632 / `AkKoCM2mqNMZEKj5gfAp` / (512) 890-2716**) belongs to a **different Google Ads account** | The AW conversion ID is account-level; P11 fixes it for this child |
| P15 | Action `6886103719` last recorded a conversion on **2026-02-28** and none since | `metrics.conversion_last_conversion_date` |
| P16 | The tag does reach Google â€” requests are received | `metrics.conversion_last_received_request_date_time` |
| P17 | **Page B hard-codes the same (214) 300-9564**, so the (214) 301-3385 mismatch exists on **both** landing pages | Page B server HTML, GET 200, 153,921 bytes |
| P18 | Page B's main CTA is the same broken `tel:%91phone%93` placeholder | Page B server HTML + live DOM |
| P19 | Page B redirects client-side to Page A via **Nelio A/B Testing, experiment 3619, `participationChance: 100`** | Page B HTML config; server GET returns B with `redirected: false` |
| P20 | **In this isolated session**, no Google tag fired while Page B was on screen; all tag hits carried `dl=`/`url=` Page A and `dr=`/`ref=` Page B. **Scoped to one Nelio assignment â€” not generalizable (see U13)** | Two runs in one browser session |
| P21 | NitroPack defers all tags on Page B exactly as on Page A â€” zero Google requests before interaction | 22 of 44 scripts deferred; `dataLayer` undefined |
| P22 | Page B captures **no** `gclid`/`gbraid`/`wbraid`/`utm_` â€” zero occurrences in its HTML | Page B server HTML |
| P23 | **Query parameters survive the Nelio redirect** â€” a `gclid` would too | `testparam=gm123` persisted into the final URL and into `url=`/`ref=` on the tag hits |
| P24 | Both `/wcm` tags fire identically after the redirect: AW-11237210508 `dn=2143013385` and AW-11240766632 `dn=5128902716`, both HTTP 200 | Page B session network capture |
| P25 | **(214) 301-3385 exists in WhatConverts profile `ProGreen DFW`**, named `GSAs traffic`, source **Google Call Extension** | Screenshot S1 |
| P26 | That number has **no Swap Number and no Last Checked Out** value | Screenshot S1 |
| P27 | **(214) 301-4622** exists in the same profile, named `Website Traffic`, source **All Traffic** | Screenshot S1 |
| P28 | **The Website Traffic swap number is `2143009564` = (214) 300-9564** â€” the exact string hard-coded on both landing pages | Screenshot S1, vs. P1 / P17 |
| P29 | All nine visible numbers forward to the single call flow **`Incoming CF - ProGreen DFW`** | Screenshot S1 |
| P30 | **No destination number is exposed** on the Phone Numbers screen â€” "Forward Calls To" shows a flow name only | Screenshot S1 |
| P31 | The Website Traffic row is the **only** visible row with a Swap Number **and** the only one with a Last Checked Out timestamp (2026-08-11 10:41 AM, **not attributable**) | Screenshot S1 |
| P32 | **(214) 974-8672** is a WhatConverts tracking number named `GBP Traffic` â€” previously seen only in both pages' JSON-LD | Screenshot S1 |
| P33 | A **second** Google Call Extension number exists â€” **(214) 945-0890**, named `GLE Traffic` | Screenshot S1 |
| P34 | **(512) 890-2716 is absent** from the visible list â€” the other party's tag number is not a WhatConverts number in this profile | Screenshot S1 |
| P35 | Call flow `Incoming CF - ProGreen DFW` runs **Incoming Call â†’ Call Recording (with announcement) â†’ Dial**, and the Dial node reads **`Direct Call to 2068903969`** | Screenshot S2 |
| P36 | **The forwarding destination is (206) 890-3969.** Not assumed to be Pro Green's public line | Screenshot S2 |
| P37 | The Dial node carries the subtitle **`2143009564`**, and a **`No Answer`** branch exists whose target is not visible | Screenshot S2 |
| P38 | **The WhatConverts Google Ads integration is `Connected` to `Pro Green - Dallas - Live (8735782888)`** â€” the identity binding, proven verbatim | Screenshot S3 |
| P39 | **The WhatConverts Profile ID is 107007**, from the console URL `leads.greenmarketingfl.com/profile/107007/â€¦` | Screenshot S3 |
| P40 | **The site's DNI script filename contains `107007`** â€” the script on the landing pages belongs to this profile | Â§10.4 script path vs. P39 |
| P41 | Integration config: Lead Conversion Name **`Whatconverts Form`**, Call Extension Conversion Name **`Whatconverts Calls`**, Trigger **`New Lead Received`**, Value Type **`Sales Value`** | Screenshot S3 |
| P42 | **Conversion Updates = `Not Updating Existing Conversions`**; **Enhanced Conversions = `Sending Enhanced Conversions`** | Screenshot S3 |
| P43 | **Eleven data types show `Sending Data`** â€” Phone Calls, Text Messages, Web Forms, Transactions, Custom Events, Chats, Emails, Others, Appointments, Estimates, Jobs | Screenshots S3 + S4 |
| P44 | **As of 2026-08-07 the account held exactly 12 conversion actions, and none was named `Whatconverts Form` or `Whatconverts Calls`**; none had type `UPLOAD_CALLS`/`UPLOAD_CLICKS`; all 12 owned by `8735782888` | `audit-2026-08-07.json`, unfiltered |
| P45 | **All 4 call conversions in the 90-day window came from `6617381255` `Calls from Ads` (AD_CALL / CALL_FROM_ADS)**, whose 60 s threshold matches the 8 raw calls â†’ 4 qualified | Snapshot conversion breakdown |
| P46 | `6617381255` qualifies at **60 s**; `6886103719` qualifies at **30 s** â€” the two call actions use different thresholds | Snapshot conversion-action config |
| P47 | `6548857156` `GSA Submit Lead Form` is ENABLED and duplicates `6886101052`'s event; it is kept out of the Conversions column **only** by `include_in_conversions_metric: false` | Snapshot conversion-action config |
| P48 | **Google Ads OAuth failed again on 2026-08-11** with the same `RefreshError` as 2026-08-10; offline preflight PASS, `--online` fails. **No API call was made against `8735782888`** | `verify_setup.py` offline + `--online` |

#### High-confidence inferences â€” strong reasoning, not yet directly proven

| # | Inference | Basis | What would prove it |
| --- | --- | --- | --- |
| H1 | ~~Google never swaps a number on Page A~~ â€” **promoted to proven (P13)** | â€” | â€” |
| H2 | The runtime swap (214) 300-9564 â†’ (214) 301-4622 is performed by a third party, not Google | The swap occurred on a direct visit with **no `gclid`**; Google inserts forwarding numbers only for ad-click visitors | Identify the script issuing the swap |
| H3 | ~~That third party is the `process.iconnode.com/google-ads/` call-tracking endpoint~~ â€” **promoted: the vendor is WhatConverts, confirmed by the user 2026-08-11 (see Â§10.5)** | Client confirmation, corroborated by the `iconnode` reference inside the swap script | â€” |
| H4 | The 8 call-asset calls recorded because they bypass the website entirely | Call assets dial from the SERP, never touching the LP | Already consistent with all data |
| H5 | **AW-11240766632** is a legacy or other-agency account rather than a Green Marketing cross-account setup | It is not this child's ID (P14). It could legitimately be the **manager account `3373711342`** doing cross-account conversion tracking â€” but its number is a **(512) Austin** number on a Dallas page, which argues against a deliberate GM setup. **Do not assume "foreign" until checked.** | A read-only lookup of the manager account's own conversion ID, or client/GTM history |
| H6 | Something changed on or near **2026-02-28** that broke the swap â€” the page number was edited, or the third-party DNI was introduced | P15 pins the date the action stopped converting | Site revision history or GTM container version history |

#### Unverified â€” must not be acted on

| # | Item | Why it is not settled |
| --- | --- | --- |
| U1 | ~~Which `AW-` ID belongs to `8735782888`~~ | **Resolved â€” AW-11237210508 (P11)** |
| U2 | ~~Which conversion label belongs to `6886103719`~~ | **Resolved â€” `inV_CKe1xtMZEIzzqO4p` (P11)** |
| U3 | ~~Whether `6886103719` has ever received a tag request~~ | **Resolved â€” yes (P16)**, though today's timestamp is my own diagnostic traffic |
| U8 | Who owns AW-11240766632 and why it tags this page | Requires client history or GTM container access |
| U9 | What changed on/near 2026-02-28 | Requires site or GTM version history |
| U4 | Whether the POST-503 pattern is real or an artifact of this inspection network | Clean GET-200/POST-503 split points at the environment |
| U5 | What NitroPack's trigger threshold is on **mobile** touch devices | Only desktop wheel/mouse behavior was tested; 100% of campaign traffic is mobile |
| U6 | ~~Page B tag and phone configuration~~ | **Resolved â€” see Â§6.11 (P17â€“P24)** |
| U10 | Whether Page B runs the same third-party DNI swap | Untestable live: Nelio redirects before any script runs on B |
| U11 | Whether Nelio experiment 3619 is deliberate, and who owns it | Client/site-admin confirmation required |
| U12 | How much mobile ad traffic is lost in the NitroPack-defer + Nelio-redirect window | Needs a real mobile-device test |
| U13 | **Whether every Page B visitor is redirected to Page A, and in what proportion** | Only one Nelio assignment was observed. Needs multiple isolated assignments or the Nelio experiment config. **Do not describe Page B reporting as globally inverted.** |
| U7 | Whether (214) 300-9564, (214) 301-4622, and (214) 974-8672 are all genuinely Pro Green numbers | Client confirmation required |
| U14 | ~~Whether **(214) 301-3385 exists in the correct Pro Green Dallas WhatConverts profile**~~ | **CLOSED by S1 (P25)** â€” it exists in profile `ProGreen DFW`. Caveat: "correct profile" is established by label and market only; the Google Ads binding is still unevidenced (Â§10.7.1) |
| U15 | Whether (214) 301-3385 is **static** or a **DNI pool** member | **Largely closed by S1** â€” no swap number, never checked out, source Google Call Extension (P25/P26/P31). Consistent with a static call-extension number and with nothing else. Formal confirmation would come from the number's own settings screen |
| U16 | ~~The **destination number** (214) 301-3385 forwards to~~ | **CLOSED by S2 (P36) â€” `Direct Call to 2068903969` = (206) 890-3969.** Not assumed to be Pro Green's public line |
| U24 | **Whose line is (206) 890-3969**, and why a Seattle NPA serves a DFW account | Observation only. VoIP, answering service, or hosted PBX would all explain it. **Do not treat as a defect** |
| U25 | What the Dial node's **`2143009564`** subtitle denotes â€” caller ID, label, or dial-from | Not established by S2 |
| U26 | Why S1's **Recording column is empty** while the shared flow starts recording | Plausible explanation exists; no evidence for it |
| U27 | ~~Why the **Google Ads refresh token has now been rejected twice in two days**~~ | **CLOSED 2026-08-11** â€” cleared on retry; the token was regenerated between attempts. All queries then ran |
| U28 | ~~**Whether `Whatconverts Form` and `Whatconverts Calls` exist in `8735782888` today**~~ | **CLOSED 2026-08-11 â€” both now exist** (`7717433751` UPLOAD_CLICKS, `7717433754` UPLOAD_CALLS), both primary and in Conversions, both with **zero** received data. See Â§13.3 |
| U31 | **Who owns manager account `2815082755`**, linked ACTIVE to this child | New 2026-08-11. Governance. Do **not** query that account |
| U32 | **Why both WhatConverts actions exist but have received nothing** | Decides whether the duplicate risk is imminent or dormant. Needs the WhatConverts send log |
| U33 | **Whether `offerdfw.progreenlandscapesolutions.com` is meant to stay in service** | Two live-campaign promotion assets still point at it while the ads point elsewhere |
| U29 | How the **eleven sent data types** map to conversion actions, and which would default to primary | Conversions column could inflate far beyond genuine leads |
| U30 | Whether the account has **accepted customer-data terms** for Enhanced Conversions | Field was in the blocked query |
| U17 | ~~The **source/channel** (214) 301-3385 is assigned to~~ | **CLOSED by S1 (P25)** â€” source `Google Call Extension`, name `GSAs traffic` |
| U18 | Which **WhatConverts configuration** drives `replace_number` and produces the runtime (214) 301-4622 | **Partially closed by S1** â€” the swap pair is proven: source `2143009564` â†’ tracking `(214) 301-4622`, traffic source `All Traffic` (P27/P28). Still open: pool settings, assigned-number list, and **URL triggers** |
| U19 | Who uses the second Google Call Extension number **(214) 945-0890 `GLE Traffic`** | `8735782888` has exactly one CALL asset, and it is (214) 301-3385 (Â§10.1) |
| U20 | Whether **Website Traffic is a true Dynamic Number Pool or a single swap number** | One row, one swap value, `All Traffic` badge `1`. S1 cannot settle it |
| U21 | Whether the S1 list is **complete** | Nine rows visible; no row count or pagination in frame |
| U22 | What the **`1`** badge on the `All Traffic` source denotes | Unlabelled in this view |
| U23 | Whether **(214) 300-9564** is Pro Green's own published line or itself a provisioned number | It appears only as a swap source, never as a tracking row |

---

## 7. Remaining confirmations (collected one at a time)

| # | Question | Answer | Date |
| --- | --- | --- | --- |
| **0** | **Intended customer-facing Dallas phone number** | **(214) 301-3385** â€” confirmed by user | **2026-08-10** |
| **1** | **Exact customer-facing business name** | **Pro Green Landscape Solutions** â€” confirmed by user. Market = Dallas, Texas / DFW. Account name `Pro Green - Dallas - Live`, child ID `8735782888`, manager `3373711342` recorded as separate fields. See Â§1.1. | **2026-08-11** |
| **1a** | **Is (214) 301-3385 controlled by the call-tracking vendor, or does it terminate directly at Pro Green?** | **Answered: it is a WhatConverts-controlled tracking number that forwards to Pro Green â€” not a direct published line.** Vendor = **WhatConverts**, on both the landing pages and the main website. Standing instruction: do not remove, bypass, or reconfigure WhatConverts yet. See Â§10.5. | **2026-08-11** |
| **1b** | **WhatConverts read-only verification of (214) 301-3385 â€” profile membership, static vs. pool, destination, source/channel, and the config behind (214) 301-4622** | **Method chosen: Path B â€” user-supplied console screenshots, one at a time. No credential shared with the agent; `WHATCONVERTS_API_TOKEN` stays empty and no API request is made.** Collection log in Â§10.6. U14â€“U18 remain open until the screenshots close them. | **2026-08-11** |
| 2 | Intended advertising/service hours, Dallas Central Time | *pending* | |
| 3 | Qualified website-call threshold: 30 or 60 seconds | *pending* (action currently set to 30) | |
| 4 | Target CPL, average completed-job value, lead-to-sale close rate | *pending* | |
| 5 | Were desktop + tablet exclusions intentional? | *pending* â€” recommend re-enabling both unless evidence supports exclusion | |
| 6 | Verification of "Licensed & Insured" and "18 Point Check" | *pending* | |
| 7 | Canonical sitelink URL pattern | *pending* â€” three competing patterns observed: `/dfw/services/<svc>/`, `/dfw/services/landscaping/<svc>/`, `/dfw/service-areas/<city>/` | |
| 8 | Identity of criteria 30007, 30008, 30027, 30042 | *pending* â€” needs UI evidence | |
| 9 | Should paused PMax 22379036365 stay paused? | *pending* â€” **keep paused by default** while tracking is unreliable | |

---

## 8. Time-zone safety note

The account time zone is `America/New_York`. Google Ads account time zone is
generally set once at account creation and is **not** freely editable via the API;
changes normally require Google support and break historical reporting continuity.
Mutability must be verified before any proposal.

If it is immutable, the Dallas schedule will be translated into Eastern time:
08:00â€“20:00 Central = **09:00â€“21:00 Eastern**. This translation will not be applied
until intended Dallas hours are confirmed (confirmation #2) and the schedule change
is separately approved.

---

## 9. Authorization boundary in force

**Allowed:** read local files; create/update this continuation document; run local
tests and validators; read-only GAQL SELECT against 8735782888 only; guided manual
diagnostics; bounded public GET-only landing-page inspection.

**Not allowed without new explicit approval:** any create/update/enable/pause/remove/
delete in Google Ads; any change to bids, budgets, devices, schedules, locations,
keywords, negatives, ads, assets, conversions, or campaign settings; form submissions,
calls, chats, or test leads; access to any other child account; printing or logging
credentials or `.env` values; commit, push, publish, deploy, or upload.

No Google Ads change has been made in this session.

---

## 10. Repair-planning read-only checks â€” 2026-08-10

Tools: `scripts`-style read-only GAQL via the project's Google Ads client (identity +
manager-link gates passed), and `mcp__claude-in-chrome__` (`tabs_context_mcp`,
`navigate`, `computer`, `read_network_requests`, `javascript_tool`, `get_page_text`,
`tabs_close_mcp`). **No manager account or other child account was queried.** Nothing was
changed in Google Ads, GTM, WordPress, Nelio, NitroPack, forms, or any external system.

### 10.1 Call assets in 8735782888 (items 1â€“2)

Exactly **one** CALL asset exists in the account.

| Field | Value |
| --- | --- |
| Asset ID | **89872541418** |
| Type | CALL |
| Phone number | **(214) 301-3385** |
| Country | US |
| Call conversion action | `customers/8735782888/conversionActions/6617381255` ("Calls from Ads") |
| Reporting state | `USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION` |

Attachments â€” all `link_status: ENABLED`, field type CALL:

| Campaign | ID | Campaign status |
| --- | --- | --- |
| Irrigation & Sprinklers | 20315156610 | **ENABLED** |
| Drainage | 21718922354 | PAUSED |
| Winterization | 22027188372 | PAUSED |
| Outdoor Lightning | 22255200632 | PAUSED |
| Leads-Performance Max-Sprinkler-Repair | 22379036365 | PAUSED |

No customer-level and no ad-group-level CALL asset links.

### 10.2 Number reconciliation (item 3)

| Number | Where it appears | Verdict |
| --- | --- | --- |
| **(214) 301-3385** | Call asset 89872541418 (all 5 campaigns) **and** the website-call tag in GTM-NZSMS9RB **and** conversion action 6886103719's stored config | **Google Ads' consistent idea of "the Pro Green Dallas number."** It produced the 8 calls / 4 conversions in the audit window, so it is live and answered. |
| **(214) 300-9564** | Hard-coded in Page A (Ã—7) and Page B (Ã—7) server HTML: header, body, `tel:` hrefs | **The website's number.** The single reason the website-call tag cannot match. |
| **(214) 301-4622** | Injected at runtime by a third-party DNI script (Â§10.4); also in both pages' JSON-LD `contactPoint` | A tracking or forwarding number belonging to the third-party system. |
| **(214) 974-8672** | JSON-LD `contactPoint` only (`contactType: sales`) | Structured data only. Never rendered, never tagged. |
| **(512) 890-2716** | `__awcc` tag in GTM-54Q4TVXF, for AW-11240766632 | **Austin area code on a Dallas page**, in a Google Ads account that is not 8735782888. |

**This reframes the defect.** Google Ads is internally consistent â€” call asset and
website-call tag both use (214) 301-3385. The **website** is the outlier at
(214) 300-9564. Which of the two is the number Pro Green wants customers to see is a
business decision and is **not assumed here**.

> **CORRECTION 2026-08-11 â€” the "outlier" reading above is wrong and is withdrawn.**
> Screenshot S1 proves **(214) 300-9564 is WhatConverts' configured swap source** for the
> `Website Traffic` number (P28). The website renders it *by design*, so the page is not
> the outlier. The real outlier is the GTM-NZSMS9RB `__awcc` tag, which was pointed at
> **(214) 301-3385 â€” a Google *Call Extension* number that is dialed from the SERP and was
> never meant to render on a page.** The defect is a GTM configuration error, not a website
> error. Full reasoning in Â§10.7.4. The row-by-row facts in the table above remain accurate;
> only the interpretation changes.

### 10.3 GTM container â†’ tag mapping (item 4) â€” PROVEN

Read directly from each published container's `gtm.js`.

**GTM-NZSMS9RB â€” the Green Marketing / Pro Green Dallas container.** Three tags only:

| Tag | Function | Configuration |
| --- | --- | --- |
| 3 | `__gclidw` Conversion Linker | `enableUrlPassthrough: false`, `enableCrossDomain: false` |
| 5 | `__awct` Ads conversion | conversionId **11237210508**, label **`oeSTCLygxtMZEIzzqO4p`** |
| 6 | `__awcc` Call conversion | **`phoneConversionNumber: "(214) 301-3385"`**, conversionId **11237210508**, label **`inV_CKe1xtMZEIzzqO4p`** â† **action 6886103719** |

**GTM-54Q4TVXF â€” the other party's container.** Nine tags:

| Tag | Function | Configuration |
| --- | --- | --- |
| 3 | `__gclidw` Conversion Linker | `enableUrlPassthrough: false` |
| 5 | `__awct` Ads conversion | conversionId **11240766632**, label `uJH9CPeUqNMZEKj5gfAp`, fires when URL contains **"thank-you"** |
| 6 | `__awcc` Call conversion | **`phoneConversionNumber: "(512) 890-2716"`**, conversionId **11240766632**, label `AkKoCM2mqNMZEKj5gfAp` |
| 8 | `__googtag` | **AW-11240766632** |
| 10 | `__googtag` | **G-MHX199EBNJ** |
| 11 | `__gaawe` GA4 event | `phone_call_click` â†’ G-MHX199EBNJ, triggered on `tel:` link clicks |
| 12 | `__html` | **Facebook Pixel** `1455418062885315` |
| 14 | `__cvt_KD25J` | **Nextdoor pixel** `440513cd-3237-4a70-9ca7-0e129ce37252` |
| 15 | `__lcl` | link-click listener |

**Answer to item 4:**

| Tag | Deployed by |
| --- | --- |
| **AW-11237210508** | **GTM-NZSMS9RB** |
| **AW-11240766632** | **GTM-54Q4TVXF** |
| **G-MHX199EBNJ** | **GTM-54Q4TVXF** |
| **G-5JMRW1LBMF** | **Neither container â€” hard-coded directly in the site's HTML.** It appears in both pages' server HTML and its `gtag/js?id=G-5JMRW1LBMF` request fires before either `gtm.js`. |

Note: `phone_conversion_css_class` / `phone_conversion_ids` / `phone_conversion_options`
appear once in each container **only as entries in gtag's internal parameter-name
dictionary**. They are *not* configured. Both `__awcc` tags rely on plain
`autoreplace` â€” Google's exact-string match â€” which confirms Â§6.8/Â§10.2.

### 10.4 The number-swap script (item 5) â€” IDENTIFIED, vendor NOT named

Method: local diagnostic instrumentation in the agent's own browser tab â€” property-setter
hooks on `Node.nodeValue`, `CharacterData.data`, `Node.textContent`, `Element.innerHTML`,
and `Element.setAttribute`, capturing a stack trace when a value containing `9564`, `4622`,
or `3385` is written. **This modified nothing on the website or any external system.**

Three writes were captured, all identical:

```
Node.nodeValue â† "(214) 301-4622"
  at replace_number (â€¦/s.ksrndkehqnwntyxlhgto.com/nitro-min-bf7d53dfâ€¦107007.js:1:4247)
```

| Attribute | Value |
| --- | --- |
| Function | **`replace_number`** â€” walks text nodes, regex-replaces any node with digits |
| Original host | **`s.ksrndkehqnwntyxlhgto.com`** (randomized domain), proxied through NitroPack's CDN |
| Size | 65,898 bytes, obfuscated (e.g. wrapper `nbfpiriuvmssvizfywxh`) |
| Contains `iconnode` | **yes (Ã—1)** â€” links it to the observed `process.iconnode.com/google-ads/` POST |
| Contains `gclid` / `gbraid` / `wbraid` / `utm_` | **10 / 5 / 5 / 43** |
| Contains `whatconverts` / `callrail` | **0 / 0** |

**What is proven:** a third-party dynamic-number-insertion script, served from a
randomized host and referencing `iconnode`, performs the (214) 300-9564 â†’ (214) 301-4622
swap by rewriting text nodes. It **already captures `gclid`, `gbraid`, `wbraid`, and
`utm_` parameters.**

**What is NOT proven and is not claimed:** the commercial vendor behind it. The string
`whatconverts` does not appear. A variable named `wc_temp` exists in the code â€” that is an
observation, **not evidence of any named product**. Do not name a vendor until the client
or the site administrator confirms which call-tracking service is contracted.

Corollary: the *third-party* system captures click IDs, while the *forms* do not (Â§6.6.2,
P22). Click-ID capture therefore already exists on this site â€” in the DNI layer only.

> **UPDATE 2026-08-11 â€” the vendor is now named by the client, not by inference.** The user
> confirmed the call-tracking vendor is **WhatConverts**. This supersedes the "vendor NOT
> named" caveat above for the *identity* of the vendor only. The reasoning that produced
> that caveat stands and was correct at the time: the literal string `whatconverts` is
> absent from the script (0 occurrences), so the vendor was never derivable from the code
> alone. The `iconnode` reference (Ã—1) and the `wc_temp` variable are **consistent with**
> that confirmation but were never sufficient on their own. Nothing else in Â§10.4 changes.

---

## 10.5 WhatConverts â€” vendor confirmed, five verification items, access status

### 10.5.1 What the user confirmed â€” 2026-08-11 (confirmation #1a)

| Item | Confirmed value |
| --- | --- |
| Call-tracking vendor | **WhatConverts** |
| Nature of **(214) 301-3385** | **A WhatConverts-controlled tracking number.** It is **not** a direct published Pro Green line. |
| Deployment scope | WhatConverts tracking numbers are used on **both landing pages and the main website** |
| Call routing | WhatConverts **forwards** calls to Pro Green |
| Standing instruction | **Do not remove, bypass, or reconfigure WhatConverts yet.** This confirmation does **not** approve Option B or any external change. |

#### Consequence for the diagnosis â€” significant, and it changes the framing again

Â§10.2 recorded (214) 301-3385 as "Google Ads' consistent idea of *the Pro Green Dallas
number*." That remains factually true of Google Ads' configuration, but the **interpretation
must be corrected**: (214) 301-3385 is a **vendor tracking number**, not Pro Green's own
line. So the account is not "already correct" in the sense of holding the business's real
number â€” it holds a WhatConverts number, and Google Ads call-asset calls on that number are
already being forwarded and logged by WhatConverts.

Two consequences follow, and both are inferences, not proven facts:

- **I1.** The 8 call-asset calls / 4 conversions in the audit window very likely also exist
  in the WhatConverts ledger. If so, they are recorded twice â€” once natively by Google Ads
  and once by the vendor â€” and any future import must dedupe against them, or the account
  will double-count its only working conversion source.
- **I2.** Because (214) 301-3385 is a vendor number while the runtime page number is
  (214) 301-4622, the two are most plausibly **different WhatConverts assignments in the
  same account** â€” one likely bound to the Google Ads / paid-call-asset channel, the other
  served by the website DNI layer. **This is a hypothesis and is recorded as U15/U17.** It
  must not be stated as fact and must not be designed against until the profile is read.

### 10.5.2 The five requested read-only verifications â€” status

Attempted from this environment on 2026-08-11. **No WhatConverts request was made, because
no credential exists to make one.** Nothing was changed anywhere.

| # | Requested verification | Status | Why |
| --- | --- | --- | --- |
| 1 | (214) 301-3385 exists in the correct Pro Green Dallas profile | **BLOCKED (U14)** | Profile membership is visible only in the WhatConverts console/API. It is not derivable from the landing pages or from Google Ads. |
| 2 | Static tracking number vs. DNI pool member | **BLOCKED (U15)** | A single browser session receives a single number assignment. Repeated isolated sessions could *sample* a pool but could never prove a number is or is not in one. |
| 3 | Destination number it forwards to | **BLOCKED (U16)** | Not exposed client-side by design. The only non-vendor way to observe it is to place a call â€” **permanently prohibited by the standing rule in Batch 8**. |
| 4 | Assigned source/channel | **BLOCKED (U17)** | Console-side attribution setting. Not emitted to the page. |
| 5 | Which configuration produces `replace_number` / iconnode and (214) 301-4622 | **PARTIAL â€” behavior proven, configuration blocked (U18)** | Â§10.4 already proves *what* the script does, *where* it is served from, and *that* it references `iconnode`. *Which* profile, number pool, and swap rule produce it is console-side only. |

### 10.5.3 Access check performed â€” result

| Check | Result |
| --- | --- |
| WhatConverts credentials in the environment | **`WHATCONVERTS_API_TOKEN` exists as a variable name in `.env` but is EMPTY (length 0).** No value was read, printed, or logged â€” only whether it is set. |
| Any other `WHATCONVERTS_*` variable | **None.** Exactly one such variable name exists. No API-secret variable, no profile/account ID variable. |
| WhatConverts client code in the project | **None.** No script, module, or helper anywhere in the repo calls WhatConverts. `prompts/07-setup-conversions.md` and `docs/API_AND_INTEGRATION_SETUP.md` name the vendor, but no integration is implemented. |
| `client.yaml` â†’ `integrations.call_tracking` | **`""` â€” empty.** Not yet recorded as WhatConverts. **Not edited**; changing `client.yaml` is a separate approval. |

**Conclusion: WhatConverts access is unavailable. All five verifications are blocked.**

### 10.5.4 Exactly what access or information is required

Either path closes items 1â€“5. **Path B requires no credential to be shared with the agent
and is the lower-risk option.**

**Path A â€” read-only API access**

1. A **WhatConverts API token *and* API secret** for the account containing the Pro Green
   Dallas profile. `.env` has a slot for the token only; a secret variable does not exist
   and would need to be added. Both are credentials â€” they go in `.env` by the user, are
   never printed, and are never committed.
2. The **WhatConverts Profile ID (and Account ID)** for Pro Green Dallas specifically, so
   queries are pinned to the right profile the same way GAQL is pinned to `8735782888`.
   Without this, there is no safe way to confirm "the *correct* profile" as item 1 requires.
3. Confirmation that the credential is **read-only**, or explicit acknowledgment of its
   scope. WhatConverts API keys are not always scope-limited; if the key can write, that
   must be known before it is used, and I will still issue reads only.
4. Before any call is made, the current **official WhatConverts API documentation** must be
   checked for the correct endpoints and parameters. I will not guess endpoint paths from
   memory, and none are asserted in this document.

**Path B â€” user-supplied screenshots or exported values, no credential shared**

From the WhatConverts console, for the Pro Green Dallas profile:

1. The **profile name and ID** shown in the console.
2. The **tracking-numbers list**, showing whether **(214) 301-3385** appears, and whether it
   is listed as a **fixed/static** number or as part of a **number pool** â€” items 1 and 2.
3. That number's **destination / forwarding number** â€” item 3.
4. That number's **assigned source, medium, or channel** (for example "Google Ads",
   "Paid Search", "Direct") â€” item 4.
5. The **DNI / number-swap settings** for the site, plus where **(214) 301-4622** appears in
   the same list and what it is assigned to â€” item 5.
6. The **tracking-script / profile snippet** the site is supposed to run, to compare against
   the observed `s.ksrndkehqnwntyxlhgto.com` script.

**Also useful, and independently valuable for Option B if it is ever approved:** whether the
profile can **export leads with `gclid`/`gbraid`/`wbraid`**, and whether call **duration**
and a **qualified/won** status are available per call. Â§10.4 proved the script *captures*
click IDs; it did not prove the vendor *exports* them, which is precondition (b) of the
Option B recommendation in Â§11 and is still unmet.

### 10.5.5 Boundary restated

WhatConverts was **not** contacted, queried, modified, bypassed, or reconfigured. No call
was placed. Option B remains a recommendation only. Batch 1 remains unapproved and cannot
be planned to the resource level until U14â€“U18 are closed.

---

## 10.6 WhatConverts Path B evidence collection â€” user-supplied screenshots

**Method chosen by the user on 2026-08-11: Path B.** The user captures read-only screens
from the WhatConverts console and supplies them one at a time. **No API token or secret is
shared with the agent. `WHATCONVERTS_API_TOKEN` stays empty. No WhatConverts API request is
made.** API credentials are **not** to be requested at this stage.

### 10.6.1 Rules in force for this collection

1. **One screenshot request at a time.** The agent asks for exactly one screen, waits, then
   interprets it before asking for the next.
2. **Read-only inspection only.** The agent may ask the user to *open* a settings screen to
   look at it. The agent will **never** instruct the user to save, edit, delete, activate,
   deactivate, add, remove, publish, or place a test call. Navigating, scrolling, filtering,
   searching, and opening a detail view are the only interactions requested.
3. **Identity gate before every interpretation.** Before any screenshot is interpreted, the
   selected profile must be verified against all four anchors together:

   | Anchor | Required value |
   | --- | --- |
   | Business | **Pro Green Landscape Solutions** |
   | Market | **Dallas, Texas â€” DFW** |
   | Google Ads account | **Pro Green - Dallas - Live** |
   | Google Ads child ID | **8735782888** (definitive identifier) |

   **Known limitation, stated in advance:** a WhatConverts phone-numbers screen is not
   expected to display a Google Ads child customer ID. The anchors satisfiable from that
   screen are the business name and market; the Google Ads linkage will have to be
   evidenced from a different screen. Until it is, the identity gate is **partially**
   satisfied, and that partial state must be recorded on each affected finding rather than
   waved through.
4. **Stop on mismatch.** Any wrong profile, wrong business, or wrong market halts
   interpretation immediately.
5. **No approval is implied.** Option B remains a recommendation only. No repair, no
   external change, and no WhatConverts reconfiguration is approved by this collection.

### 10.6.2 Targets to close

| # | Target | Tracked as |
| --- | --- | --- |
| 1 | Does **(214) 301-3385** exist in this profile | U14 |
| 2 | **Static** number or **dynamic pool** member | U15 |
| 3 | Its **destination** number | U16 |
| 4 | Its **source and channel** assignment | U17 |
| 5 | The swap number, pool settings, assigned numbers, traffic source, and **URL triggers** behind `replace_number`/iconnode and the runtime **(214) 301-4622** | U18 |

### 10.6.3 Collection log

| # | Screen requested | Requested | Received | Identity gate | Closes | Result |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Profile identity + **Tracking â†’ Calls â†’ Phone Numbers** | 2026-08-11 | **2026-08-11** â€” `clients/pro-green-dallas/evidence/whatconverts-phone-numbers-2026-08-11.png` | **PARTIAL** â€” profile label and market only; no Google Ads anchor visible | **U14 closed, U17 closed, U15 largely closed, U18 partial. U16 remains open.** | See Â§10.7 |
| S2 | Call flow **Incoming CF - ProGreen DFW** â€” destination / ring-to | 2026-08-11 | **2026-08-11** â€” `evidence/whatconverts-call-flow-2026-08-11.png` | n/a (canvas only) | **U16 closed** | Â§10.8.1 |
| S3 | **Integrations â†’ Google Ads â€” Connection Details** | not requested; user-supplied | **2026-08-11** â€” `evidence/whatconverts-google-ads-connection-2026-08-11.png` | **COMPLETE â€” identity binding proven** | Identity gate, integration config | Â§10.8.2 |
| S4 | **Integrations â†’ Google Ads â€” data types** | not requested; user-supplied | **2026-08-11** â€” `evidence/whatconverts-google-ads-data-types-2026-08-11.png` | inherits S3 | Data-type send list | Â§10.8.3 |

---

## 10.8 Screenshots S2, S3, S4 â€” call flow and the Google Ads integration

All three read directly by the agent on 2026-08-11 as image files. **The agent has no
WhatConverts access and made no WhatConverts request. Nothing was opened, saved, edited,
enabled, disconnected, or called.**

### 10.8.1 S2 â€” call flow `Incoming CF - ProGreen DFW`, destination proven

The flow canvas shows three connected nodes:

| Order | Node | Detail shown |
| --- | --- | --- |
| 1 | **Incoming Call** | entry point |
| 2 | **Call Recording** â€” "Recording" | *"Start recording and say: 'This call will be recorded for quality assurance.'"* |
| 3 | **Dial** â€” subtitle **`2143009564`** | **`Direct Call to 2068903969`**, with a red **`No Answer`** branch beneath it |

A further `+` connector sits below the `No Answer` branch; **what that branch routes to is
not visible** and was not captured.

**U16 is closed. The proven forwarding destination is (206) 890-3969.**

Three cautions recorded with it:

1. **It is not assumed to be Pro Green's public business number.** It is the number this
   call flow dials. Nothing in this evidence says who answers it or what line it is.
2. **`2068903969` is a (206) NPA â€” Seattle, Washington** â€” on a Dallasâ€“Fort Worth account.
   That is recorded as a factual observation, not a defect. A VoIP line, an answering
   service, or a hosted PBX would all explain it innocently. **Do not treat it as an error
   and do not act on it** until the client identifies the line (**U24**).
3. The Dial node's subtitle **`2143009564`** is the same string as the website swap number
   (P28). **What that subtitle denotes in a Dial node â€” caller ID presented, a label, or a
   dial-from number â€” is not established by this screenshot** and must not be guessed
   (**U25**).

**Minor inconsistency, logged and not chased:** every row on the S1 Phone Numbers screen has
an **empty Recording column**, yet this shared call flow **starts recording with an
announcement**. Both can be true if the column reflects a per-number setting while recording
is performed by the flow â€” but that is an explanation, not evidence (**U26**).

### 10.8.2 S3 â€” Google Ads integration, and the identity binding is now complete

Browser URL, visible in frame: **`leads.greenmarketingfl.com/profile/107007/integrations/google-ads`**
â€” a Green Marketing white-labelled WhatConverts console. Header: **Viewing Profile: ProGreen DFW**.

| Field | Value shown |
| --- | --- |
| Status | **Connected** |
| **Account** | **Pro Green - Dallas - Live (8735782888)** |
| Lead Conversion Name | **Whatconverts Form** |
| Call Extension Conversion Name | **Whatconverts Calls** |
| Trigger Type | **New Lead Received** |
| Value Type | **Sales Value** |
| Conversion Updates | âœ— **Not Updating Existing Conversions** (an `Enable Updates` control is present â€” **not used**) |
| Enhanced Conversions | âœ“ **Sending Enhanced Conversions** |
| Phone Calls | âœ“ Sending Data |
| Text Messages | âœ“ Sending Data |

**The identity gate is now COMPLETE.** All four anchors are evidenced together:

| Anchor | Required | Evidence |
| --- | --- | --- |
| Business | Pro Green Landscape Solutions | profile `ProGreen DFW` + domain `progreenlandscapesolutions.com` |
| Market | Dallas, Texas â€” DFW | `DFW` in profile; DFW-area numbers in S1 |
| **Google Ads account** | **Pro Green - Dallas - Live** | **S3 `Account` field, verbatim** |
| **Google Ads child ID** | **8735782888** | **S3 `Account` field, verbatim** |
| WhatConverts Profile ID | â€” | **107007**, from the browser URL |

This retroactively binds every S1 finding to child `8735782888`. The partial-gate caveat in
Â§10.7.1 is **satisfied** and no longer limits those findings.

**Independent corroboration of the site script.** Â§10.4 recorded the DNI script path as
`â€¦/nitro-min-bf7d53dfâ€¦**107007**.js`. The WhatConverts profile ID is **107007**. The script
running on the landing pages therefore belongs to *this* profile. Two independent sources â€”
the browser URL in the console and the script filename captured on the site â€” agree.

### 10.8.3 S4 â€” data types being sent to Google Ads

Same URL and profile. Every listed data type shows a green check and **`Sending Data`**:

**Phone Calls Â· Text Messages Â· Web Forms Â· Transactions Â· Custom Events Â· Chats Â· Emails Â·
Others Â· Appointments Â· Estimates Â· Jobs** â€” eleven types, plus **Enhanced Conversions:
Sending Enhanced Conversions**.

A **`Disconnect`** control is present in the left rail on both S3 and S4. **It was not used
and will not be.**

---

## 10.7 Screenshot S1 â€” WhatConverts Phone Numbers, findings

Source file: `clients/pro-green-dallas/evidence/whatconverts-phone-numbers-2026-08-11.png`.
Read directly by the agent on 2026-08-11. **Read-only. Nothing was opened, saved, edited,
activated, deactivated, or called by the agent â€” the agent has no WhatConverts access and
inspected an image file only.**

### 10.7.1 Identity gate â€” PARTIAL, as forecast

| Anchor | Required | Visible in S1 | Verdict |
| --- | --- | --- | --- |
| Business | Pro Green Landscape Solutions | Profile label **`ProGreen DFW`** ("Viewing Profile") | **Consistent, not proof.** A profile label is not a business name. |
| Market | Dallas, Texas â€” DFW | **`DFW`** in the profile label; DFW-area numbers throughout (214 / 469), rows named **GBP Plano, TX** and **LSA Plano, TX** | **Consistent** |
| Google Ads account | Pro Green - Dallas - Live | **Not visible** | **Unevidenced** |
| Google Ads child ID | 8735782888 | **Not visible** | **Unevidenced** |
| Browser address bar / profile ID | requested | **Not in frame** â€” the capture is cropped to the app viewport | **Not captured** |

The console is Green Marketing's own â€” the top-left mark reads **GREEN MARKETING / GROWING
YOUR BUSINESS**. The user attests the screenshot is from profile `ProGreen DFW`; that
attestation carries provenance but is not in-image proof of the Google Ads linkage.

**Consequence:** every S1 finding below is recorded as **proven of the WhatConverts profile
labelled `ProGreen DFW`**, and as **not yet bound to Google Ads child `8735782888`**. The
binding still needs its own evidence and must not be assumed.

### 10.7.2 The five requested verifications â€” all five confirmed

| # | Claim to verify | Verdict | What the image shows |
| --- | --- | --- | --- |
| 1 | (214) 301-3385 listed as "GSAs traffic", source "Google Call Extension" | **CONFIRMED** | Row `+12143013385` Â· Name **`GSAs traffic`** Â· Source **`Google Call Extension`** with the Google Ads icon |
| 2 | (214) 301-4622 listed as "Website Traffic", source "All Traffic" | **CONFIRMED** | Row `+12143014622` Â· Name **`Website Traffic`** Â· Source **`All Traffic`**, carrying a badge **`1`** |
| 3 | Website Traffic swap number is 2143009564 | **CONFIRMED** | Swap Number column = **`2143009564`** on that row, and on **no other visible row** |
| 4 | Both route through call flow "Incoming CF - ProGreen DFW" | **CONFIRMED, and broader** | **All nine visible rows** show Forward Calls To = **`Incoming CF - ProGreen DFW`** |
| 5 | The actual destination number is not visible | **CONFIRMED** | "Forward Calls To" holds a **call-flow name**, never a number. The destination sits inside that flow. |

### 10.7.3 Full visible inventory â€” transcribed verbatim

Columns present: Tracking Number Â· Name Â· Source Â· Swap Number Â· Forward Calls To Â·
Last Checked Out Â· Recording Â· Text Messaging Â· Call Greeting Â· row actions.

| # | Tracking Number | Name | Source | Swap Number | Forward Calls To | Last Checked Out |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `+12148313417` â€” (214) 831-3417 | Email Blasts | Offline | â€” | Incoming CF - ProGreen DFW | â€” |
| 2 | `+12149745799` â€” (214) 974-5799 | Facebook Traffic | Offline | â€” | Incoming CF - ProGreen DFW | â€” |
| 3 | `+14698842851` â€” (469) 884-2851 | GBP Plano, TX | Offline | â€” | Incoming CF - ProGreen DFW | â€” |
| 4 | `+12149748672` â€” **(214) 974-8672** | GBP Traffic | Offline | â€” | Incoming CF - ProGreen DFW | â€” |
| 5 | `+12149450890` â€” (214) 945-0890 | GLE Traffic | **Google Call Extension** | â€” | Incoming CF - ProGreen DFW | â€” |
| 6 | `+12143013385` â€” **(214) 301-3385** | **GSAs traffic** | **Google Call Extension** | **â€”** | Incoming CF - ProGreen DFW | **â€”** |
| 7 | `+14698900520` â€” (469) 890-0520 | LSA Plano, TX | Offline | â€” | Incoming CF - ProGreen DFW | â€” |
| 8 | `+12149748226` â€” (214) 974-8226 | LSa's Traffic | Offline | â€” | Incoming CF - ProGreen DFW | â€” |
| 9 | `+12143014622` â€” **(214) 301-4622** | **Website Traffic** | **All Traffic** `1` | **`2143009564`** | Incoming CF - ProGreen DFW | **Tue, Aug 11, 2026 at 10:41 AM** |

Every visible row shows a green check under **Text Messaging**. **Recording** and **Call
Greeting** are blank on every visible row. Page controls **`Add Dynamic Pool`** and
**`Add Phone Numbers`** exist â€” the agent did not and will not use them.

**Completeness caveat:** nine rows are visible, a horizontal scrollbar is present, and **no
row count or pagination control is in frame**. The list may continue below. S1 therefore
proves **existence**, never **inventory completeness**.

### 10.7.4 Finding 1 â€” the swap number is (214) 300-9564, and that reframes the whole defect

`2143009564` is **exactly** the number hard-coded seven times each on Page A and Page B.

This overturns how Â§6.4 and Â§10.2 characterised it. Those sections called (214) 300-9564
"the website's numberâ€¦ the single reason the website-call tag cannot match," implying the
page was wrong. **It is not wrong.** WhatConverts is *configured* to find (214) 300-9564 on
the page and replace it with (214) 301-4622. The page number is the intended swap source,
and the WhatConverts side is behaving exactly as designed.

**Restated root cause â€” sharper than "number mismatch":**

| Layer | Number it acts on | Correct? |
| --- | --- | --- |
| Website HTML | renders (214) 300-9564 | **Correct** â€” it is WhatConverts' configured swap source |
| WhatConverts DNI | swaps 300-9564 â†’ **(214) 301-4622** | **Correct and working** |
| GTM-NZSMS9RB `__awcc` (action `6886103719`) | told to autoreplace **(214) 301-3385** | **Wrong number for this job** |

(214) 301-3385 is WhatConverts' **Google Call Extension** number â€” provisioned for the
SERP call asset, where Google dials it directly and the website is never involved. It was
never meant to appear on a landing page. Google's website-call tag was pointed at the
call-extension number instead of the website number, so it hunts for a string that by design
never renders. That is the failure, and it is a **GTM configuration error**, not a website
error.

### 10.7.5 Finding 2 â€” the two Google Ads numbers behave exactly as their roles predict

| Number | WhatConverts role | Swap Number | Last Checked Out | Reading |
| --- | --- | --- | --- | --- |
| (214) 301-3385 | Google Call Extension | **none** | **never** | Dialed from the SERP. No page involvement, so nothing to swap and nothing to check out. Consistent with the 8 call-asset calls / 4 conversions being the only phone data the account ever recorded (H4). |
| (214) 301-4622 | All Traffic, website | **2143009564** | **2026-08-11 10:41 AM** | Session-assigned to website visitors. |

The **`Last Checked Out`** timestamp is populated on the Website Traffic row and on no
other. "Checked out" is session-assignment behavior, which is why this row and only this row
carries one. **That timestamp is not attributable** â€” it is same-day and could be a real
visitor, the user's own browsing, or something else. The agent's page inspections were on
2026-08-10, not 08-11. Do not treat it as traffic evidence.

### 10.7.6 Finding 3 â€” two of the loose numbers are now identified

| Number | Previously | Now proven |
| --- | --- | --- |
| **(214) 974-8672** | "JSON-LD `contactPoint` only, never rendered, never tagged" (Â§10.2) | A WhatConverts tracking number named **GBP Traffic**, source Offline |
| **(214) 301-4622** | "a tracking or forwarding number belonging to the third-party system" | Confirmed: WhatConverts **Website Traffic** number |

Both JSON-LD `contactPoint` numbers are therefore WhatConverts tracking numbers, not direct
Pro Green lines. This partially closes **U7**. What remains open in U7 is (214) 300-9564:
being configured as the swap *source* makes it plausibly Pro Green's genuine published line,
but S1 does not prove that â€” it appears only in the Swap Number field, never as a tracking
number in its own right.

**(512) 890-2716 does not appear anywhere in the visible list.** The Austin number carried
by the other party's tag (AW-11240766632 / GTM-54Q4TVXF) is not a WhatConverts number in
this profile, at least not among the nine visible rows. U8 is unaffected.

### 10.7.7 Consequence for the repair options â€” Option C gets harder, Option B gets stronger

Now that the swap source is known, the Option C race in Â§11 can be stated concretely.
"Repairing" the `__awcc` tag by pointing it at the number actually on the page â€”
(214) 300-9564 â€” would aim **Google's autoreplace and WhatConverts' `replace_number` at the
identical string**. Both would compete to rewrite the same text nodes after NitroPack
releases them, and whichever ran last would win. That is not a fix; it is the current
failure with a shorter fuse.

This strengthens the Â§11 recommendation of **Option B** and the warning that **Option C must
not be adopted unless non-interference is proven**. Neither is approved, and nothing here
changes that.

### 10.7.8 New open items raised by S1

| # | Item | Why it matters |
| --- | --- | --- |
| U19 | **Who uses (214) 945-0890 "GLE Traffic"**, the *second* Google Call Extension number | Google Ads `8735782888` has exactly **one** CALL asset, `89872541418` = (214) 301-3385 (Â§10.1). A second call-extension number implies another Google Ads account, another campaign type, or a stale provision. |
| U20 | Whether **Website Traffic is a true Dynamic Number Pool or a single swap number** | The row shows one number and one swap value; the `All Traffic` badge reads `1`. A pool of one behaves very differently from a multi-number pool for concurrent-session attribution. **S1 cannot settle this.** |
| U21 | Whether the visible list is **complete** | No row count or pagination in frame |
| U22 | What the **`1`** badge on the `All Traffic` source denotes | Unlabelled in this view |
| U23 | Whether (214) 300-9564 is **Pro Green's own published line** or itself a provisioned number | It appears only as a swap source, never as a tracking row |

---

## 10.9 Conversion-action audit â€” 2026-08-11

### 10.9.1 The live audit is BLOCKED. Identity was not reverified.

The requested read-only audit could **not** be run. The Google Ads API client failed at the
OAuth token-refresh step, before any request left this machine:

```
google.auth.exceptions.RefreshError: Reauthentication is needed.
```

Confirmed with `scripts/verify_setup.py --client clients/pro-green-dallas/client.yaml`:

- Offline preflight â†’ `Credential variable names: present` â†’ **`Preflight: PASS`**
- `--online` preflight â†’ the **same `RefreshError`**

**This is the identical failure recorded on 2026-08-10 in Â§6.8.** The refresh token was
regenerated by the user that day, the query ran, and the token is now being rejected again.
That it failed twice in two days is itself worth noting â€” a token that keeps expiring points
at a testing-mode OAuth client, a revoked grant, or a password/permission change, not at a
one-off glitch (**U27**).

**Consequences, stated plainly:**

- **No API call was made against customer `8735782888`.** Not one.
- **The mandatory fresh identity reverification did not happen**, so the gate is not
  satisfied and no live query may proceed.
- No credential value was read, printed, or logged. `.env` was not modified.
- The prepared script is `SELECT`-only, pinned to `customer_id=8735782888`, and **queries the
  manager account nowhere** â€” the manager link is read from the child's own
  `customer_manager_link` resource rather than from the MCC, per the instruction. It is held
  at the session scratchpad path; nothing was written into the project tree. It will run
  unchanged once authentication is restored.

**Everything below is therefore derived from `snapshots/audit-2026-08-07.json`, which is four
days stale (as_of 2026-08-07).** It is real data from a real read, not an estimate â€” but it
cannot show anything created, changed, or converted on 08-08 through 08-11. `CLAUDE.md`
forbids publishing from stale reports alone, so **nothing here may be implemented**; it is
recorded as the best available reading pending reauthentication.

### 10.9.2 The headline finding â€” the two WhatConverts conversion actions do not exist

The snapshot contains **all 12** conversion actions in `8735782888`, unfiltered (REMOVED and
HIDDEN rows are present, so nothing was excluded).

**Neither `Whatconverts Form` nor `Whatconverts Calls` is among them.** No action carries
`Whatconverts` in its name. No action has type `UPLOAD_CALLS` or `UPLOAD_CLICKS`. Every one
of the 12 is owned by `customers/8735782888`.

So as of 2026-08-07, the WhatConverts integration reported **Connected** and **Sending Data**
for eleven data types into an account that had **no conversion action able to receive any of
it**. Those two facts cannot both be complete descriptions of reality. The candidate
explanations, none of them established:

| # | Possibility | How to settle it |
| --- | --- | --- |
| 1 | The actions are created lazily on the first successful send, and no send has succeeded | Fresh conversion-action query; WhatConverts send/error log |
| 2 | Sends are failing silently at the API | WhatConverts integration log |
| 3 | The actions were created between 2026-08-08 and today | **Fresh query â€” the direct test** |
| 4 | Data is landing somewhere other than this account | Compare the connection's account field against receiving actions |

**This is tracked as U28 and it is the single most important open question in the tracking
diagnosis.** It cannot be resolved from a stale snapshot.

### 10.9.3 The four requested actions â€” mapping

Snapshot-derived. 90-day window = 2026-05-09 â†’ 2026-08-06.

| # | Requested | Found? | ID |
| --- | --- | --- | --- |
| 1 | **Whatconverts Form** | **NO â€” does not exist** | â€” |
| 2 | **Whatconverts Calls** | **NO â€” does not exist** | â€” |
| 3 | **Native Google call-asset conversion** | **YES** | **6617381255** (plus REMOVED twin **6555523644**) |
| 4 | **Website-call action** | **YES** | **6886103719** |

#### Full configuration of the two that exist, plus the removed twin

| Field | **6617381255** | **6886103719** | **6555523644** (removed twin) |
| --- | --- | --- | --- |
| Exact name | `Calls from Ads` | `Pro Green DFW - Lp - Phone Call Leads` | `Calls from ads` (lower-case *a*) |
| Type | **AD_CALL** | **WEBSITE_CALL** | AD_CALL |
| Origin / source | **CALL_FROM_ADS** | **WEBSITE** | CALL_FROM_ADS |
| Category | PHONE_CALL_LEAD | PHONE_CALL_LEAD | PHONE_CALL_LEAD |
| Status | **ENABLED** | **ENABLED** | **REMOVED** |
| Primary or secondary | **Primary** (`primary_for_goal: true`) | **Primary** | Primary |
| In Conversions column | **Yes** | **Yes** | Yes |
| Counting method | **ONE_PER_CLICK** | **ONE_PER_CLICK** | ONE_PER_CLICK |
| Click-through window | 30 days | 30 days | 30 days |
| View-through window | 30 days | 30 days | 30 days |
| Call-duration qualification | **60 s** | **30 s** | 60 s |
| Default value | 0.0 | 0.0 | 1.0 |
| Always use default value | **true** | **true** | true |
| Attribution model | GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN | same | same |
| Owner | `8735782888` | `8735782888` | `8735782888` |
| **Conversions (90 d)** | **4.00** | **0** â€” absent from the breakdown | 0 |
| **All conversions (90 d)** | **4.00** | **0** | 0 |
| Conversion value (90 d) | 0.00 | 0.00 | 0.00 |

### 10.9.4 The specific question answered â€” where the four call conversions came from

**All four came from the native Google forwarding-call action `6617381255` "Calls from Ads"
(type `AD_CALL`, origin `CALL_FROM_ADS`). Not from "Whatconverts Calls". Not both.**

The reasoning is not inferential. "Whatconverts Calls" **does not exist as a conversion
action in this account**, so it cannot have contributed a conversion. `6617381255` is the
only action in the entire 90-day breakdown with a non-zero `conversions` value in the call
category, and it carries exactly 4.00. Campaign-level `phone_calls` was 8, of which 4 met the
**60-second** qualification â€” which is `6617381255`'s configured threshold, not
`6886103719`'s 30 seconds.

### 10.9.5 Complete 90-day conversion picture

| Action | ID | Type | In Conv. column | Conversions | All conv. |
| --- | --- | --- | --- | --- | --- |
| Calls from Ads | 6617381255 | AD_CALL | **yes** | **4.00** | 4.00 |
| Pro Green DFW - Lp - Submit Lead Form | 6886101052 | WEBPAGE | **yes** | **2.00** | 2.00 |
| Local actions - Other engagements | 6669693044 | GOOGLE_HOSTED | no | 0 | 10.00 |
| Local actions - Website visits | 6608032928 | GOOGLE_HOSTED | no | 0 | 4.00 |
| Local actions - Directions | 6609874719 | GOOGLE_HOSTED | no | 0 | 1.00 |
| **Pro Green DFW - Lp - Phone Call Leads** | **6886103719** | **WEBSITE_CALL** | **yes** | **0** | **0** |
| Clicks to call | 6616343220 | GOOGLE_HOSTED | no | **absent â€” 0** | **absent â€” 0** |
| *(5 further actions)* | â€” | â€” | â€” | 0 | 0 |

Totals reconcile exactly against Â§3: Conversions 4 + 2 = **6.00**; all conversions
4 + 2 + 10 + 4 + 1 = **21.00**.

### 10.9.6 Duplicate and overlap analysis

#### Overlaps that exist today â€” none double-count the Conversions column

| Pair | Overlap? | Why |
| --- | --- | --- |
| `6617381255` AD_CALL **vs** `6886103719` WEBSITE_CALL | **No** | Different surfaces. AD_CALL counts a call dialed from the ad's call asset on the SERP; WEBSITE_CALL counts a call from a number rendered on the landing page. A single call is one or the other. |
| `6886101052` **vs** `6548857156` `GSA Submit Lead Form` | **Yes â€” same event, both ENABLED** | Both are `WEBPAGE` / `SUBMIT_LEAD_FORM` on the same site. **Not double-counted today** only because `6548857156` has `include_in_conversions_metric: false`. Flipping that flag would instantly double the form count. |
| `6549164075` `GSA Call Btn Click (1)` **vs** `6616343220` `Clicks to call` | **Probable** | Both track call-button clicks. Both are excluded from the Conversions column today. |
| `6617381255` **vs** removed `6555523644` | Historic | Same AD_CALL role. The removed twin also had `default_value: 1.0` where the live one has `0.0`. |

**Finding 10 in Â§5 is now specific:** the duplicates are `6548857156` â†” `6886101052` and
`6549164075` â†” `6616343220`, and they are neutralised by exclusion flags, not by design.

#### The duplicate risk that Option B would create â€” concrete and high-severity

This is the important one, and it is a **direct consequence of S1**.

1. Call asset `89872541418` dials **(214) 301-3385** (Â§10.1).
2. S1 proves (214) 301-3385 **is a WhatConverts tracking number** (`GSAs traffic`, source
   `Google Call Extension`).
3. Therefore **every SERP call-asset call physically rings a WhatConverts line** and is
   logged by WhatConverts as a lead.
4. Google **independently** counts that same call as an `AD_CALL` conversion on `6617381255`.
5. The integration is set to **`Phone Calls: Sending Data`** with trigger **`New Lead
   Received`**.

**So the moment a `Whatconverts Calls` action exists and receives, the same physical call is
counted twice** â€” once natively by `6617381255`, once by the import. And it lands on the
**only conversion source in this account that currently works at all**. Any Option B design
must dedupe against `6617381255` explicitly, or exclude one of the two from the Conversions
column. **This is not approved and is not being implemented â€” it is a design constraint
recorded before the fact.**

#### Three further integration-configuration conflicts, recorded not acted on

| # | Observation | Why it matters |
| --- | --- | --- |
| 1 | WhatConverts **Value Type = Sales Value**, but both live call/form actions have `always_use_default_value: true` with `default_value: 0.0` | An action configured to always use its default value **overwrites an imported value with 0**. Sales value would be sent and discarded. Whether a future `Whatconverts` action would carry different settings is unknown. |
| 2 | WhatConverts **Conversion Updates = Not Updating Existing Conversions** | Retroactive value updates are off, so **sold-job revenue and gross profit cannot flow back** into Google Ads. `CLAUDE.md` requires qualified/closed-won offline outcomes and profit reporting. **Option B cannot meet that requirement in the integration's current state.** |
| 3 | WhatConverts sends **eleven data types** (Phone Calls, Text Messages, Web Forms, Transactions, Custom Events, Chats, Emails, Others, Appointments, Estimates, Jobs) | If each maps to its own conversion action and any default to primary, the Conversions column could inflate far beyond genuine leads. The mapping is unknown (**U29**). |

Also unresolved: WhatConverts reports **Sending Enhanced Conversions**, but whether the
account has accepted the customer-data terms could not be read â€” that field was in the
blocked query (**U30**).

### 10.9.7 What a fresh run must confirm first

Once the refresh token is restored, the held script reverifies identity, then answers, in one
pass: whether `Whatconverts Form` / `Whatconverts Calls` now exist; the account's
`conversion_tracking_id` (expected **11237210508**, confirming P14);
`enhanced_conversions_for_leads_enabled`; `accepted_customer_data_terms`; and
per-action last-conversion recency. **Until then, no bidding decision, no conversion-goal
change, and no repair may be based on these numbers.**

---

## 11. Call-tracking architecture comparison

| Criterion | **A.** Google website-call forwarding only | **B.** Third-party DNI as source of truth + qualified calls imported to Google Ads | **C.** Controlled coexistence |
| --- | --- | --- | --- |
| Qualified-lead attribution | Ad-click visitors only; organic/LSA/direct calls invisible | All traffic sources, one ledger | Two ledgers to reconcile |
| Duplicate conversions | Low risk | Manageable â€” dedupe on lead ID | **High risk**: website-call *and* imported call both count |
| Call-duration qualification | Native, 30 or 60 s | Vendor-side threshold, then import only qualifying calls | Two thresholds that can disagree |
| GCLID/GBRAID/WBRAID | Google-internal only; **not exposed for offline import** | **Already captured by the DNI script (10/5/5 hits)** | Whichever script wins the race captures it |
| Offline conversion support | None â€” cannot carry sold-job revenue or gross profit | **Full** â€” Data Manager API path per `CLAUDE.md` | Possible but ambiguous |
| Forms + CRM compatibility | Separate, unlinked path | One identity spans call + form + CRM | Fragmented |
| Auditing across GM clients | Simple but shallow | One repeatable pattern; vendor access needed per client | Hardest to audit |
| Rollback / verification | Easy | Moderate â€” staged, reversible | Requires proving non-interference first |

**Proven risk specific to Option C:** `replace_number` rewrites text nodes by regex, and
Google's `__awcc` `autoreplace` targets an exact number string. Both operate on the same
DOM after NitroPack releases scripts. Whichever runs last wins, and the loser is left
matching a string the winner already changed. **That race is exactly the current failure.**
Option C must not be adopted unless non-interference is *proven*, not assumed.

### Recommendation for Green Marketing: **Option B**

The third-party DNI already does the two hardest things â€” it swaps reliably for all
traffic and it captures `gclid`/`gbraid`/`wbraid`/`utm_`. Google's forwarding number does
neither for non-ad traffic and hands back nothing usable for offline outcomes. `CLAUDE.md`
requires qualified/closed-won offline outcomes, GCLID preservation into the CRM, and
gross-profit reporting; **only Option B can satisfy all three.**

Under Option B, Google's website-call conversion action `6886103719` is **retired as a
bidding conversion**, not repaired â€” which also removes the race that broke it.

**This recommendation is conditional** on: (a) identifying and obtaining access to the
call-tracking vendor, (b) confirming it can export qualified calls with click IDs, and
(c) confirming the developer-token/Data Manager path. If (a) or (b) fails, Option A
becomes the fallback and the DNI script must be removed first.

---

## 12. Phased repair plan â€” PREVIEW ONLY, NOTHING APPLIED

No batch below is approved. Nothing here has been implemented.
Approval column: **GM** = Green Marketing, **C** = client, **GM+C** = both.

### Batch 1 â€” Call-tracking architecture and the correct Dallas number

| Field | Detail |
| --- | --- |
| **Current** | Website renders (214) 300-9564. Call asset 89872541418 = (214) 301-3385. GTM-NZSMS9RB `__awcc` = (214) 301-3385. Third-party DNI overwrites the page with (214) 301-4622. |
| **Proposed** | Adopt Option B. Align **one** confirmed customer-facing Dallas number across site, call asset, and CRM. Retire `6886103719` as a bidding conversion. Import qualified calls via Data Manager API. |
| **Edit location** | WordPress/Divi templates; GTM-NZSMS9RB; Google Ads asset 89872541418; call-tracking vendor console |
| **Access needed** | WordPress admin, GTM publish rights on NZSMS9RB, Google Ads write on 8735782888, vendor account |
| **Risk** | **High.** Changing a live phone number can drop calls. Retiring a primary conversion changes the Conversions column. |
| **Rollback** | Restore prior number values (all recorded above); re-enable `6886103719` as primary |
| **Verification** | Fresh GAQL read-back of asset + conversion action; live page load confirming one number; test call placed **by the client**, never by the agent |
| **Approval** | **GM+C** |
| **Confirmed 2026-08-10** | **Target number = (214) 301-3385.** The number already in call asset 89872541418 and in the GTM-NZSMS9RB `__awcc` tag. |

#### Batch 1 consequences of the confirmed number â€” (214) 301-3385

Because the confirmed number is the one **Google Ads already holds**, the direction of the
repair inverts from what the raw symptom suggested:

- **Google Ads needs no number change.** Call asset `89872541418` and the `__awcc` tag in
  GTM-NZSMS9RB are already correct at (214) 301-3385. Both stay as they are. This removes
  the highest-risk item â€” no live Google Ads phone number is edited.
- **The website is what is wrong.** Both landing pages hard-code (214) 300-9564 seven
  times each. That is the string to change.
- **The third-party DNI is now the decisive blocker, not a side issue.** Even after the
  page is corrected to (214) 301-3385, `replace_number` will overwrite it at runtime with
  its own number. Google's `autoreplace` would still find nothing to match. **Correcting
  the page alone will not fix conversion tracking** â€” the DNI conflict must be resolved in
  the same batch.
- Under the recommended Option B this is consistent: (214) 301-3385 becomes the single
  customer-facing number, the DNI layer remains the call ledger, and `6886103719` is
  retired as a bidding conversion rather than repaired.

Still required before Batch 1 can be planned to the resource level: identify the
call-tracking vendor and confirm whether (214) 301-3385 is a line the vendor controls or a
line that terminates directly at Pro Green. That determines whether the DNI script can be
pointed at it, must be reconfigured, or must be removed.

### Batch 2 â€” Broken `tel:%91phone%93` CTA on both pages

| Field | Detail |
| --- | --- |
| **Current** | Page A "Get 10% OFF Now!" and Page B "Get Fast Repairs Today!" both use `href="tel:%91phone%93"` â€” an unresolved shortcode |
| **Proposed** | Replace with a real `tel:` href carrying the confirmed number |
| **Edit location** | WordPress/Divi module on both landing pages |
| **Access needed** | WordPress admin |
| **Risk** | **Low.** Currently non-functional; any valid value is an improvement |
| **Rollback** | Restore the previous href string |
| **Verification** | Load both pages, inspect the href, confirm it matches the confirmed number. **No tap, no call placed.** |
| **Approval** | **C** (GM specifies the value) |

### Batch 3 â€” GCLID / GBRAID / WBRAID / UTM capture in Gravity Forms

| Field | Detail |
| --- | --- |
| **Current** | Zero occurrences of `gclid`, `gbraid`, `wbraid`, `utm_` in either page's HTML. Form `gform_2`'s only hidden field is `gform_source_page_number_2`. Click IDs exist **only** inside the DNI script. |
| **Proposed** | Add hidden fields for `gclid`, `gbraid`, `wbraid`, `utm_source/medium/campaign/term/content`, plus landing page and consent status; map them into the CRM |
| **Edit location** | Gravity Forms form `gform_2`; CRM field mapping |
| **Access needed** | WordPress admin, Gravity Forms, CRM admin |
| **Risk** | **Lowâ€“moderate.** Editing a live form risks breaking submissions if done carelessly |
| **Rollback** | Remove the added hidden fields; Gravity Forms keeps form revisions |
| **Verification** | Load the page with test URL parameters and read the hidden field values **in the DOM only â€” no submission** |
| **Approval** | **GM+C** |
| **Note** | Query parameters survive the Nelio redirect (P23), so this will work on both pages |

### Batch 4 â€” Duplicate GTM, GA4, and Google Ads tags

| Field | Detail |
| --- | --- |
| **Current** | Two GTM containers, two GA4 properties, two Ads accounts on one page. GTM-54Q4TVXF carries AW-11240766632 (phone (512) 890-2716), G-MHX199EBNJ, a Facebook pixel, and a Nextdoor pixel. G-5JMRW1LBMF is hard-coded outside GTM. |
| **Proposed** | Establish ownership of GTM-54Q4TVXF and AW-11240766632, then decide removal or retention. Consolidate GA4. **No removal until ownership is established.** |
| **Edit location** | WordPress header/theme; both GTM containers |
| **Access needed** | WordPress admin; GTM access to both containers; client's tagging history |
| **Risk** | **High.** Removing another party's tags can destroy their measurement and may breach an agreement |
| **Rollback** | Republish the prior container version; GTM retains full version history |
| **Verification** | Reload both pages, confirm the intended tag set and only that set |
| **Approval** | **GM+C** â€” client must confirm what AW-11240766632 is before anything is removed |

### Batch 5 â€” NitroPack delayed tag execution

| Field | Detail |
| --- | --- |
| **Current** | All 43â€“44 scripts deferred; 21â€“22 carry `type="nitropack*"`. Zero Google requests until user interaction. Confirmed on both pages. |
| **Proposed** | Exclude the measurement scripts (GTM containers, gtag, DNI) from NitroPack's delay-until-interaction list |
| **Edit location** | NitroPack settings for the site |
| **Access needed** | NitroPack admin (via WordPress) |
| **Risk** | **Moderate.** Un-deferring scripts will reduce PageSpeed scores and may slow first paint |
| **Rollback** | Re-add the scripts to the delay list |
| **Verification** | Load both pages with **no interaction at all** and confirm `gtm.js` fires; re-test on a real mobile device |
| **Approval** | **GM+C** |
| **Open question** | U5/U12 â€” the mobile trigger threshold is still untested |

### Batch 6 â€” Nelio A/B test configuration and measurement

| Field | Detail |
| --- | --- |
| **Current** | Nelio A/B Testing, experiment **3619**, `participationChance: 100`, alternating A â†” B, `isGA4Integrated: false`. In one isolated session the browser was moved B â†’ A, and Google tags fired only after the move. |
| **Proposed** | Confirm the experiment is intentional; decide whether to keep, pause, or integrate it. If kept, ensure measurement can attribute a variant. **Do not act on a single observed assignment.** |
| **Edit location** | WordPress â†’ Nelio A/B Testing |
| **Access needed** | WordPress admin |
| **Risk** | **Moderate.** Ending an experiment discards in-flight data; leaving it running keeps landing-page reporting ambiguous |
| **Rollback** | Nelio retains experiment state; a paused experiment can be resumed |
| **Verification** | Multiple isolated assignments (fresh profiles / cleared Nelio cookies) to measure actual split, **or** read the experiment config directly |
| **Approval** | **GM+C** |
| **Blocked on** | **U13** â€” the redirect rate and direction are not established |

### Batch 7 â€” Page A and Page B validation

| Field | Detail |
| --- | --- |
| **Current** | Both pages carry the same defects: number mismatch, broken CTA, no click-ID capture, deferred tags |
| **Proposed** | After Batches 1â€“6, re-run the full read-only inspection on both pages and record a pass/fail per item |
| **Edit location** | None â€” verification only |
| **Access needed** | Browser only |
| **Risk** | **None.** Read-only |
| **Rollback** | n/a |
| **Verification** | Server HTML shows one number; both `tel:` hrefs valid; hidden click-ID fields present; tags fire without interaction; one DNI system active |
| **Approval** | **GM** |

### Batch 8 â€” Google Ads conversion verification without creating a fake lead

| Field | Detail |
| --- | --- |
| **Current** | `6886103719` last converted 2026-02-28. Today's `last_received_request` reflects the agent's own diagnostic page loads, not a real visitor. |
| **Proposed** | Verify by **evidence, not by faking a lead**: (1) GAQL read of `tag_snippets` + `metrics.conversion_last_received_request_date_time`; (2) network capture proving the tag fires with the correct number; (3) Google Tag Assistant in preview mode; (4) a **client-placed real call** from a real device, if the client chooses; (5) reconcile vendor call logs against Google Ads. |
| **Edit location** | None â€” verification only |
| **Access needed** | Google Ads read on 8735782888; browser; vendor console |
| **Risk** | **None** from the agent's steps. Any real test call is the client's decision and their call to place |
| **Rollback** | n/a |
| **Verification** | A conversion appears attributable to a known real event, matched in the vendor log |
| **Approval** | **GM**, or **GM+C** if the client places a test call |
| **Standing rule** | The agent will not place a call, submit a form, start a chat, or generate a test lead under any circumstance |

### Sequencing

Batch 1 gates everything, and Batch 1 is gated on the confirmed Dallas number.
Batches 2 and 3 are low-risk and can run in parallel once the number is confirmed.
Batch 4 is blocked on ownership of AW-11240766632. Batch 5 is independent but should
follow Batch 1 so verification is unambiguous. Batch 6 is blocked on U13.
Batches 7 and 8 close the loop. **Bidding-strategy migration remains deferred until
clean data exists.**

> **SUPERSEDED 2026-08-11 by Â§13.** The Â§12 preview above is retained as the historical
> record. The authoritative, resource-level batches now live in
> `clients/pro-green-dallas/final-audit-and-revamp-plan.md` Â§17, consolidated from eight
> batches into four.

---

## 13. Autonomous read-only completion pass â€” 2026-08-11

Run under the user's autonomous read-only authorization. **Nothing external was changed.**
Full findings and the revamp plan: **`clients/pro-green-dallas/final-audit-and-revamp-plan.md`**.

### 13.1 Identity gate â€” PASSED on fresh API read

`8735782888` Â· `Pro Green - Dallas - Live` Â· `manager false` Â· `test_account false` Â·
`- live` present Â· USD Â· America/New_York. Manager link read from the child's own
`customer_manager_link` resource; **the MCC was never queried as a target.**

### 13.2 Authentication â€” resolved

The `RefreshError` that blocked the 2026-08-11 conversion audit cleared on retry; the token
was evidently regenerated between attempts. All subsequent queries ran. **U27 closed.**

### 13.3 The five findings that changed the diagnosis

| # | Finding | Supersedes |
| --- | --- | --- |
| **1** | **A third landing page exists â€” `offerdfw.progreenlandscapesolutions.com`** â€” and it renders **(214) 301-3385**, the exact number action `6886103719` swaps. It loads **GTM-NZSMS9RB only**, has **no Nelio, no NitroPack, no second GA4, no FB/Nextdoor pixel, and no broken `tel:` placeholder**. Two **live-campaign promotion assets still point at it** | Reframes Â§10.7.4 entirely. The tag was built for *this* page; traffic moved away and the tag never followed. **Inference I1** |
| **2** | **U13 CLOSED.** Nelio 3619 config read from both pages: `alternatives = [{postId 3332, testAgainstExistingContent}, {postId 3369, isExistingContent}]`, `participationChance 100`. **Page A = 3332, Page B = 3369.** Two alternatives, bidirectional, **â‰ˆ50/50** | Withdraws "always redirects". Both Â§6.11.3's caution and its scope correction were right to stop short |
| **3** | **`Whatconverts Form` (7717433751, UPLOAD_CLICKS) and `Whatconverts Calls` (7717433754, UPLOAD_CALLS) now exist** â€” created after 2026-08-07. Both **primary**, both **in Conversions**, both goals **biddable**. Both have **received nothing** (`last_received_request` at epoch) | **U28 closed.** The duplicate risk predicted in Â§10.9.6 is now **armed but not yet fired** |
| **4** | **Value settings are fine.** Both WhatConverts actions have `always_use_default_value: false` | **Corrects Â§10.9.6 item 1** â€” imported Sales Value would *not* be overwritten with 0 on these actions |
| **5** | **A second manager account `2815082755` is linked ACTIVE** to this child (link 345783752), alongside Green Marketing's `3373711342` | New. Governance issue. **Not queried.** Plausibly related to `AW-11240766632` / `GTM-54Q4TVXF` (**inference I7**) |

### 13.4 Vendor identification â€” now proven from the page itself

The WhatConverts script is **`https://s.ksrndkehqnwntyxlhgto.com/107007.js?ver=7.0.3`**, with
runtime cookies `wc_visitor` / `wc_client` / `wc_client_current` / `wc_swap` and functions
`wc_visitor_init` / `wc_form_ypbib`. Profile **107007** matches the console URL exactly.
Â§10.4's caution ("do not name a vendor from the code alone") was correct at the time and is
now satisfied by direct evidence rather than by client attestation alone.

Browser localStorage also holds **both** Google website-call swap records â€”
`inV_CKe1xtMZEIzzqO4p,2143013385` and `AkKoCM2mqNMZEKj5gfAp,5128902716` â€” storage-level
confirmation that both `__awcc` tags actively attempt replacement with numbers that do not
render on Pages A/B.

### 13.5 Campaign audit completed â€” headline numbers

Budget-capped at $32.50/day. IS **58.37%** (lost to budget 16.72%, to rank 24.90%) over 90
days, deteriorating to **38.21%** (27.67% / 34.11%) in the last 30. Invalid clicks **14.6%**.
100% mobile â€” desktop `30000` and tablet `30002` carry an **explicitly set** `bid_modifier` of
0.0 (âˆ’100%), confirmed by proto field-presence, while mobile `30001` has none set.

Ad groups: Irrigation Repair Near Me $1,141.07 â†’ 5 conv Â· Sprinkler Repair Near Me $926.74 â†’
1 conv Â· **Sprinkler System Repair $836.88 â†’ 0 conv**. One enabled RSA per ad group, **every
headline and description pinned**. QS 3â€“5, landing-page experience BELOW_AVERAGE.

Waste: **$332.49 / 0 conversions** on competitor and out-of-market queries ("lawn sense dallas"
alone $175.47; two Albuquerque queries). Geo targeting is **correct** â€” all delivery is DFW
`LOCATION_OF_PRESENCE`, so there is no geographic waste. Ad schedule is 08:00â€“20:00 **Eastern**
= 07:00â€“19:00 Central. 27/22/22 sitelinks with **four copies of "Irrigation Winterization"**, an
excluded service.

### 13.6 Corrections to the earlier record

| Earlier statement | Correction |
| --- | --- |
| Â§10.2: "(214) 300-9564 is the website's number and the outlier" â†’ later corrected to "the GTM tag is the outlier" | **Both readings were incomplete.** The tag is not misconfigured for its original target â€” it is correct for `offerdfw`, and the *ads* were moved to pages it was never built for (I1) |
| Â§10.9.6: imported Sales Value would be overwritten with 0 | **Wrong for these actions.** Both WhatConverts actions have `always_use_default_value: false` |
| Â§10.9: "no conversion action can receive WhatConverts data" | **True on 2026-08-07, false now.** Both actions exist as of 2026-08-11 |
| "Zero sitelinks on the live campaign" (working note during this pass) | **Wrong.** Sitelinks are linked at **ad-group** level â€” 27/22/22. Customer-level assets are genuinely zero |

### 13.7 Blocked

**WhatConverts console â€” login barrier.** `leads.greenmarketingfl.com` redirected to a login
screen in the automation browser profile. No credentials were entered and none are requested.
**U-D** (pool name, assigned numbers, URL triggers, attribution rules) and **U-E** (why the two
actions have received nothing) remain open.

### 13.8 Boundary â€” run of 2026-08-11 (autonomous audit pass)

All Google Ads queries `SELECT`-only against `8735782888`. Manager account never queried as a
target. Landing pages GET-only. No call, form, chat, or test lead. No call recording played. No
credential read, printed, or logged. `.env` untouched. Nothing created, modified, enabled,
disabled, connected, disconnected, or deleted in any external system. Nothing committed or
published.

---

## 14. Resource-level preview run — 2026-08-11

Run under the user's authoritative business-decision record and read-only planning
authorization. **No external system was changed.** Deliverables:
`confirmed-business-decisions.md` (authoritative), `batch-1-resource-level-preview.md`,
`canonical-landing-page-developer-handoff.md`, `landing-page-draft/` (local, undeployed).

### 14.1 Identity gate — PASSED [FRESH-API]

`8735782888` / `Pro Green - Dallas - Live` / manager false / test false / `- live` present /
manager `3373711342` link `342593485` ACTIVE. 28 SELECT-only queries, 0 errors, all pinned to
the child. The manager account was never used as a query target.

### 14.2 Open items CLOSED by the decision record

| Item | Resolution |
| --- | --- |
| U-A / U31 second manager `2815082755` | **ClickCease invalid-click protection. Authorized. Never to be queried** |
| U-C / U24 destination (206) 890-3969 | **The business owner answers it; voicemail if unanswered** |
| U-I / Q5 claim verification | Licensed & insured, free estimates, 18-point check, satisfaction guarantee **verified**; **10% OFF expired and prohibited**; same-day **conditional only** |
| Q3 canonical page | **A new page** at `offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/`. Neither A nor B |
| Q7 device exclusions | Tablet deliberate; **desktop is not** |
| Q8 intended hours | **7 AM-7 PM Central** |
| Q11 PMax | Stays paused |
| U-G / U33 `offerdfw` future | Superseded by the new canonical host |

### 14.3 Corrections made this run

| Earlier statement | Correction |
| --- | --- |
| "Two **live-campaign** promotion assets point at `offerdfw`" (F32, §13.3) | **WRONG.** Both campaign-asset links on the live campaign are **REMOVED** [FRESH-API]. Only PAUSED links on PAUSED campaigns remain |
| "The ad schedule is misaligned; shift it" (plan §17 Batch 2.5) | **WRONG.** 08:00-20:00 Eastern already equals the confirmed 7 AM-7 PM Central. **No change needed** |
| "Exclude `6886103719` and remove `__awcc` in Batch 1" | **Withdrawn.** Confirmed phone rules 8 and 9 push both to cutover steps 9 and 10 |
| I7 - `AW-11240766632` plausibly belongs to manager `2815082755` | **WRONG on the manager.** That manager is ClickCease. `AW-11240766632` ownership stays **[UNVERIFIED]**; Austin is now the leading hypothesis |

### 14.4 New material findings [FRESH-API]

1. **No conversion of any kind since 2026-07-31.** MTD 2026-08-01 to 08-11: **$369.98, 46
   clicks, 721 impressions, 0 conversions.**
2. **Account-level ClickCease tracking template** hard-codes `ccpturl=offerdfw...` - but it is
   **overridden** by campaign-level templates on every campaign, so the ClickCease tracker URL
   is effectively bypassed. Flagged, not changed; ClickCease is authorized.
3. **Three campaigns carry a wrong hard-coded `utm_id`** in their tracking template
   (Winterization, Outdoor Lightning, PMax).
4. Account is spending **~half** the confirmed $2,000 cap while losing **34.44%** of impression
   share to budget.
5. **18 URL-bearing ads** inventoried: 3 serving, 15 not. **Ad `714045747006` is ENABLED inside
   a PAUSED ad group** in the live campaign - unpausing that group would resume `offerdfw`
   traffic immediately.
6. **74 location criteria exported with IDs**: 70 ZIPs, 3 cities, 1 airport, PRESENCE/PRESENCE,
   zero negatives. Preserved as authoritative; discrepancies flagged only.
7. **Zero cost/price/quote/estimate queries served** in 90 days, while live ads promise quotes
   and estimates.

### 14.5 Still blocked

- **WhatConverts console** - login barrier. U-D and U-E/U32 remain open.
- **`AW-11240766632` / `GTM-54Q4TVXF` ownership** - [UNVERIFIED]. No associated account may be queried.
- **Gross margin, close rate, booked-job rate** - not available. Not invented.

### 14.6 Boundary - run of 2026-08-11 (preview run)

All Google Ads queries SELECT-only against `8735782888`. Manager accounts never queried as a
target; ClickCease manager `2815082755` deliberately untouched. Landing pages GET-only. No call,
form, chat, or test lead. No recording played. No credential read, printed, or logged. `.env`
untouched. Nothing created, modified, enabled, disabled, connected, disconnected, published, or
deleted in Google Ads, WhatConverts, GTM, WordPress, Nelio, NitroPack, forms, or DNS. The
landing-page draft is local and undeployed. Nothing committed, pushed, or uploaded.

---

## 15. EXECUTION RUN — 2026-08-11 (controlled Google Ads implementation)

Mode changed from preview-only to **controlled execution** under explicit user authorization.
**Google Ads was mutated.** No other external system was touched.

### 15.1 Identity gates

**8 gates run, one immediately before every mutation batch. All PASS.** Each verified
`customer.id 8735782888` / `Pro Green - Dallas - Live` / manager false / test false / USD /
manager `3373711342` ACTIVE. The gate raises SystemExit on mismatch, so no mutation could run past
a failure. **ClickCease manager `2815082755` never queried, never modified.**

### 15.2 Executed and verified — 29/29 read-back checks PASS

| Batch | Change | Result |
| --- | --- | --- |
| B | Desktop criterion `30000` bid_modifier `0.0` -> **`1.0`**; tablet `30002` stays `0.0` | verified |
| C | **3 over-broad negatives removed** (`cost`, `how much`, `sprinkler valve replacement cost`); **40 targeted negatives added**. 620 -> **657** | verified |
| D | **8 in-scope keywords created PAUSED** - sprinkler head repair / replacement, sprinkler valve repair / replacement, irrigation valve repair | verified PAUSED |
| E | **3 challenger RSAs created PAUSED**, ids `820553894577`, `820553894580`, `820553894583`, minimal pinning, **final URLs unchanged** | verified PAUSED |
| F | "Claim Your Discount" callout **PAUSED**; **5 winterization sitelink links PAUSED**; 3 verified-claim callouts created and linked **PAUSED** | verified |
| G | `utm_id` corrected on 3 **PAUSED** campaigns; live campaign template untouched | verified |
| H | Daily budget **$32.50 -> $45.00**; August projects to **$1,269.97** against the $2,000 ceiling | verified |

### 15.3 Attempted and did NOT apply

**Batch A - conversion containment.** `mutate_conversion_actions` returned success for
`7717433751` and `7717433754`, but read-back showed `primary_for_goal` and
`include_in_conversions_metric` **unchanged at true**. [FRESH-API] This account uses
**account-level conversion goals**, under which those fields are derived from the goal
configuration rather than settable per action.

Per instruction the item was **stopped, not retried**, and no broader-blast-radius workaround was
improvised. **No harm:** both actions retain prior values and have **never received data**, so the
duplicate-counting risk stays latent rather than active. Escalation path recorded in the manifest.

### 15.4 Two policy calls made during the run

1. **`hiring` was NOT added as a negative.** "hiring a sprinkler repair company" is buyer intent;
   `CLAUDE.md` protects `hire`.
2. **`sprinkler experts` was NOT added as a negative.** Generic buyer language, not a proven brand.

### 15.5 Incident - read-back defect

Batches F/F2 threw `EXPECTED_REFERENCED_FIELD_IN_SELECT_CLAUSE` on my **verification query**, not
the mutation, and were initially logged SKIPPED. A separate state check confirmed **all six link
changes and all three asset creations had applied**. Recorded lesson: a read-back failure is not
evidence a mutation failed - always re-query state.

### 15.6 Awaiting the second approval gate

Per `CLAUDE.md` rule 11, new resources were created paused and **enabling is a separate step**:
8 keywords, 3 challenger RSAs, 3 callout links.

### 15.7 Boundary

Nothing changed in WordPress, GTM, WhatConverts, Nelio, NitroPack, ClickCease, DNS, any other
Google Ads account, any phone number, or any live final URL. **No conversion action, campaign, ad
group, keyword, ad or asset was deleted anywhere.** No test lead, form submission or phone call.
No credential read, printed or logged. The WordPress template was inspected **read-only**.

---

## 16. ACTIVATION RUN — 2026-08-11 (containment retry + approved enablement)

**11 identity gates, all PASS.** Logs: `backups/pre-change-2026-08-11T1300/step{1,2,345,7}.json`.

### 16.1 Batch A containment retry — SUCCEEDED

Step 1 SELECT-only inspection: both actions owned by `customers/8735782888`; all five campaigns
run `goal_config_level: CUSTOMER`; **zero custom conversion goals exist**; neither WhatConverts
action sits inside an active custom goal -> retry permitted.

Step 2 mutation with `update_mask = ["primary_for_goal"]` **only**:

| Action | Before | After | Result |
| --- | --- | --- | --- |
| 7717433751 Whatconverts Form | primary true | **false** | SECONDARY |
| 7717433754 Whatconverts Calls | primary true | **false** | SECONDARY |

`include_in_conversions_metric` moved true -> false on both **as a derived consequence** of
secondary status. It was never in the mask. No other field drifted.

### 16.2 CORRECTION to section 15.3

The earlier conclusion that **account-level conversion goals** made `primary_for_goal` unsettable
was **wrong**. The real cause was the **update mask**: the first attempt also set the deprecated
`include_in_conversions_metric` and derived the mask from the populated message, so the API
accepted the operation and silently discarded it. Restricting the mask to the single supported
field made it apply immediately. **No manual UI change is required.**

### 16.3 Enablement — 14 approved resources

| Step | Approved | Enabled | Left paused |
| --- | --- | --- | --- |
| Keywords | 8 | **7** | **1** |
| Challenger RSAs | 3 | **3** | 0 |
| Verified callouts | 3 | **3** | 0 |

**Left paused: `sprinkler head replacement` EXACT** - the pre-check found it blocked by two active
BROAD negatives, `sprinkler head replacement` (295473723839) and `head replacement`
(301794223657). Enabling a keyword its own campaign negatives suppress would spend nothing and
misrepresent coverage. Removing those negatives was out of scope for this batch.

All three challenger RSAs are ENABLED and `REVIEW_IN_PROGRESS`; **none disapproved or limited**;
controls `714659486058`, `797294303667`, `797325463324` all remain ENABLED. All three callouts
ENABLED and APPROVED; discount callout `89872309308` remains PAUSED.

### 16.4 Two initially-failing assertions, both my error not the account's

1. "total enabled keywords = 51" used a **unique-text** count. The backup holds **52 enabled
   criteria** (44 unique texts). 52 + 7 = **59** actual. Diff vs backup: 7 newly enabled,
   **0 lost**.
2. "serving final URLs" expected 4 entries for a **6-ad** set. Per ad group every enabled ad
   points at its **prior** URL. **No URL changed.**

Resource diff vs backup: **3 ads added, 8 keyword criteria added** - exactly the approved set.

### 16.5 Blocker status

Containment complete, so the prior strict blocker is **partially lifted**. **One condition
remains before any WhatConverts import is enabled:** the **Google Call Extension source must be
excluded** from the WhatConverts -> Google Ads feed, or call-asset calls will double-count against
`6617381255`. Still blocked by the WhatConverts login barrier.

### 16.6 Boundary

No rollback was performed; nothing needed one. Preserved and verified unchanged: all three serving
final URLs, call asset (214) 301-3385, budget $45.00, bidding, campaign and ad-group statuses,
74 location criteria, presence targeting, schedule, networks, device settings, tracking templates,
and the 657 negatives. Nothing deleted anywhere. No WordPress, GTM, WhatConverts, Nelio,
NitroPack, ClickCease or DNS change. ClickCease manager 2815082755 never queried.

---

## 17. CLEANUP RUN — 2026-08-11 (negative-keyword conflict resolved)

**3 identity gates, all PASS.** Logs: `backups/pre-change-2026-08-11T1300/cleanup_*.json`.

### 17.1 Pre-check

Target `[sprinkler head replacement]`, criterion **1442898236**, resource
`customers/8735782888/adGroupCriteria/151125103616~1442898236`. Verified EXACT, PAUSED, in
`Sprinkler Repair Near Me` (151125103616), parent campaign and ad group both ENABLED, final URL
inherited, no duplicate enabled exact, and absent from the pre-change backup - confirming it is
the eighth keyword from the approved manifest.

Both blockers confirmed BROAD keyword negatives on the live campaign, both ENABLED, both matching
the target: **295473723839** `sprinkler head replacement` and **301794223657** `head replacement`.

### 17.2 A false positive caught before acting

The blocker scan initially flagged ad-group criterion **503001**. Investigation showed it is an
**AGE_RANGE exclusion**, not a keyword negative - my matcher returned a false positive because
`all([])` is True for an empty token list. The matcher now guards empty token lists. Removing the
two listed negatives was therefore sufficient, and no age-range criterion was touched.

### 17.3 Method chosen by the API, not assumed

Pausing was attempted first as the least destructive option and was **rejected**:

```
INVALID_ARGUMENT: "Cannot set the campaign criterion status for an excluded criteria."
```

Pausing a negative criterion is **not supported by the resource**, so removal is the only method
it offers. Removal is reversible by re-adding the same text and match; exact rollback values were
recorded before mutating.

### 17.4 Mutations

| # | Action | Resource |
| --- | --- | --- |
| 1 | REMOVE | `campaignCriteria/20315156610~295473723839` |
| 2 | REMOVE | `campaignCriteria/20315156610~301794223657` |
| 3 | ENABLE | `adGroupCriteria/151125103616~1442898236` |

**No replacement negatives added** - that needs fresh search-term evidence that does not exist yet.

### 17.5 Verification - 28/28 PASS

Keyword ENABLED / EXACT / correct campaign + ad group / effective status permits serving / final
URL inherited / exactly one enabled instance. Campaign negatives **657 -> 655**, exactly two
removed, no other negative touched, and **no remaining campaign or ad-group keyword negative
blocks it**. Preserved: budget $45.00, TARGET_SPEND, networks, presence targeting, 74 locations,
call asset (214) 301-3385, all six RSAs, three verified callouts, discount callout still paused,
three working conversion actions, both WhatConverts actions still secondary, count 14.

### 17.6 State after this run

**All 8 keywords, 3 challenger RSAs and 3 verified callouts from the approved change manifest are
now enabled.** No rollback was performed.

### 17.7 Monitoring window

**The 24-hour monitoring window begins at this cleanup timestamp: 2026-08-11.**
Checkpoints: 24 h, 3 days, 7 days, 14 days - see the activation report.
