# Ambient Cooling - Live (2401959466) — 2026-09-10 session C

**Account:** Ambient Cooling - Live · child customer ID **2401959466** · non-manager ·
non-test · America/New_York · USD
**Managers:** Green Marketing 3373711342 ACTIVE · ClickCease 2815082755 ACTIVE
**Identity gate:** PASS before every read and before the single live write.

**Google Ads mutations executed this session: 2** (one package). Everything else is
read-only analysis, browser QA, drafts and validate-only checks.

**Local Services Ads are out of scope for this project and are not analysed, recommended,
forecast or counted anywhere in this report.** The $13,000/month maximum applies to Google
Search campaigns only. WhatConverts rows whose `lead_source` names LSA are excluded from
paid-search analysis rather than reassigned to Search.

---

## 1. Executed

### `AMB-0910-CPC-CAP-1` · `7EA6922309EB` · 2 operations · EXECUTED

Approved verbatim in this conversation. Fingerprint recomputed from the on-disk plan and
matched before the write.

| Campaign | ID | Before | After |
|---|---|---|---|
| Gas Boiler Repair | 24132507744 | ceiling UNSET (uncapped Maximize Clicks) | **$25.00** |
| HVAC Replacement | 24132507753 | ceiling UNSET (uncapped Maximize Clicks) | **$30.00** |

`EXECUTED_OK: 2 results returned` · one atomic mutate · `partial_failure=False` ·
receipt `receipts/live/AMB-0910-CPC-CAP-1-2026-09-10-EXECUTED.json`.

**Readback: 0 FAIL.** All five campaigns now carry a ceiling:

| Campaign | Ceiling | Daily budget | Bidding | Status | Geo |
|---|---|---|---|---|---|
| AC Repair | $25.00 | $141.45 | TARGET_SPEND | ENABLED | PRESENCE |
| Gas Boiler Repair | **$25.00** | $5.00 | TARGET_SPEND | ENABLED | PRESENCE |
| HVAC Installation | $30.00 | $176.15 | TARGET_SPEND | ENABLED | PRESENCE |
| HVAC Repair | $25.00 | $78.95 | TARGET_SPEND | ENABLED | PRESENCE |
| HVAC Replacement | **$30.00** | $20.00 | TARGET_SPEND | ENABLED | PRESENCE |

**Budget compliance:** combined daily **$421.55** × 30.4 = **$12,815.12**, headroom
**$184.88** under the $13,000 Search maximum.

**Unrelated resources verified unchanged:** campaigns 23, ad groups 68, geo criteria 375 on
the five, IP blocks 2,796, shared sets 17, conversion actions 16, campaign negatives on the
five 6,158.

> **Correction to my own first readback.** It initially reported 4 failures — campaigns
> 33≠23, ad groups 83≠68, geo 1,467≠375, conversion actions 23≠16. The account had not
> changed; my assertion counted rows the baseline snapshot excluded. Excluding `REMOVED`
> rows and scoping geo to the five reproduces the snapshot exactly. The 10 removed
> campaigns, 15 removed ad groups and 7 removed conversion actions all pre-date this
> session. The assertions are now correctly scoped in the script so this cannot recur.

---

## 2. Six-ad policy inventory

Fresh `ad_group_ad.policy_summary` for exactly the six named ads. **All six returned.**

| Ad | Campaign | Ad group | Ad group status | Ad status | Approval | Review | Topic | Type |
|---|---|---|---|---|---|---|---|---|
| 820900825428 | Gas Boiler Repair | 202339087594 | ENABLED | PAUSED | DISAPPROVED | REVIEWED | CONSUMER_FINANCE | FULLY_LIMITED |
| 820900825431 | Gas Boiler Repair | 202339087594 | ENABLED | PAUSED | DISAPPROVED | REVIEWED | CONSUMER_FINANCE | FULLY_LIMITED |
| 820900825434 | HVAC Installation | 202339087634 | ENABLED | PAUSED | DISAPPROVED | REVIEWED | CONSUMER_FINANCE | FULLY_LIMITED |
| 820900825437 | HVAC Installation | 202339087634 | ENABLED | PAUSED | DISAPPROVED | REVIEWED | CONSUMER_FINANCE | FULLY_LIMITED |
| 820944944368 | HVAC Replacement | 200159223798 | ENABLED | PAUSED | DISAPPROVED | REVIEWED | CONSUMER_FINANCE | FULLY_LIMITED |
| 820944944371 | HVAC Replacement | 200159223798 | ENABLED | PAUSED | DISAPPROVED | REVIEWED | CONSUMER_FINANCE | FULLY_LIMITED |

**Final URLs are all HVAC service pages**, none finance-related:
`/gas-boiler-repair/`, `/hvac-installation/`, `/hvac-replacement/` on
`offer.ambientcoolingandheating.com`.

**Delivery is fully covered.** Each affected ad group holds 4 ads, exactly 2 ENABLED and
APPROVED:

| Ad group | Campaign | ENABLED + APPROVED |
|---|---|---|
| 202339087594 | Gas Boiler Repair | 821319509209, 821319509212 |
| 202339087634 | HVAC Installation | 821319509197, 821319509200 |
| 200159223798 | HVAC Replacement | 821319509203, 821319509206 |

No ad was re-enabled, edited, recreated or duplicated. No ZIP-code targeting was touched.

### The appeal cannot be filed from this session

**`policy_topic_entries` returned the topic and the FULLY_LIMITED type but no evidences and
empty constraints.** The API does not expose which asset or destination Google cited. That
detail exists only in the UI's Policy details panel, and Dispute-decision appeals can only
be submitted there.

**Blocker: Claude in Chrome is not connected to this session.** There is no `/chrome`
command and no browser-control tool for an authenticated Chrome profile. A headless
Playwright browser carries no Google session, and requesting cookies, tokens or credentials
is prohibited. So steps 4's UI inspection and appeal submission are **not performed**.

What the API evidence does support, and what it does not: the destinations are HVAC service
pages, so nothing in the *final URL* promotes lending or credit. That is consistent with a
false CONSUMER_FINANCE classification, but it is not proof — the citation could name a
headline, description or sitelink this query does not expose. **Do not select "Made changes
to comply"** unless the UI names a specific finance item that was actually corrected.

All six ads stay paused regardless of appeal outcome. No performance improvement is claimed
from pausing or appealing them.

---

## 3. CPC control

**Regime boundary: 2026-09-04 16:56 America/New_York.** `change_event` shows the $25/$25/$30
ceilings created from an **empty** `old_resource` (AC Repair 16:56:20, HVAC Repair 16:56:34,
HVAC Installation 16:56:51), `client_type=GOOGLE_ADS_WEB_CLIENT`. `client_type` identifies
the interface, not the person. Nothing else in the 30-day window touched a bid field.

Never blended across that boundary:

| Regime | Window | Days | Spend | Valid clicks | $/valid click | Invalid rate | Spend/day |
|---|---|---|---|---|---|---|---|
| UNCAPPED | 08-14 → 09-03 | 21 | $8,025.18 | 172 | $46.66 | 91.0% | $382.15 |
| CAPPED | 09-05 → 09-09 | 5 | $103.71 | 4 | $25.93 | 80.0% | $20.74 |

**The capped sample is 4 valid clicks and 0 conversions.** It is directionally consistent
with the ceiling binding and it establishes nothing. The current values are protective
starting points, not proven optima.

### Standing ceilings and their evidence

| Campaign | Ceiling | Decision | Rationale |
|---|---|---|---|
| AC Repair | $25 | **Hold** | Uncapped it paid $108.98/valid click |
| HVAC Repair | $25 | **Hold** | Uncapped $70.62/valid click. A $35 test is **not authorized** and needs better outcome data first |
| HVAC Installation | $30 | **Hold** | Changing it while launching Commercial HVAC Installation would confound both results |
| Gas Boiler Repair | $25 | **Applied today** | 0 valid clicks, 42 invalid, on $5.00/day |
| HVAC Replacement | $30 | **Applied today** | Uncapped $30.50/valid click, 0 unique qualified leads |

### Market context — Keyword Planner, exact 75 Maryland targets, exact BOFU set

All 75 geo targets swept in 8 batches of ≤10. All five campaigns share an identical
75-target positive geo set, 0 exclusions.

| Keyword | Summed volume | Top-of-page low | Top-of-page high | Competition |
|---|---|---|---|---|
| ac repair near me | 530 | **$19.94** | **$117.36** | HIGH |
| hvac repair near me | 180 | **$4.72** | **$143.47** | HIGH |
| gas boiler repair | 50 | — | — | LOW |
| hvac installers near me | 50 | — | — | HIGH |
| hvac replacement near me | 50 | — | — | HIGH |

**These are market context, not recommended bids.** Summed volume adds the same keyword
across batches and overstates demand; synonyms share one volume bucket. The three keywords
returning 50 across 8 batches are at or near the minimum bucket, i.e. very thin demand.

Worth noting plainly: the live $25 AC Repair ceiling sits just above the **$19.94**
top-of-page low and far below the **$117.36** high. The ceiling is buying the cheapest end
of the top-of-page range, if it clears at all.

### Gates before any future ceiling change

Settled data · regimes split at the exact change timestamp · WhatConverts reconciliation ·
≥20 valid clicks and preferably 3 unique qualified leads per campaign · one variable per
campaign · ≤20% move per test · monitor at 24h and 72h for configuration faults · first
performance judgment only after 14 settled days excluding conversion-lag days.

**Incremental spend stop-losses without a qualified lead:** AC Repair $150 · HVAC Repair
$250 · HVAC Installation $280 · HVAC Replacement $280 · Gas Boiler Repair $250.

**Rollback values:** AC Repair 25000000 · HVAC Repair 25000000 · HVAC Installation 30000000
· Gas Boiler Repair → unset · HVAC Replacement → unset.

If a campaign meets its CPQL target but valid click volume falls more than 50%, a separately
fingerprinted ceiling increase of ≤20% should be drafted.

**No bid will be raised merely to spend budget.**

---

## 4. Auction Insights — NOT EXPORTED

Recorded at `evidence/auction-insights/2026-08/manifest.json` with all 11 expected exports
(5 campaigns, 5 ad groups, 1 pooled baseline) marked `NOT_EXPORTED`.

**Blocker:** Claude in Chrome is not connected to this session. Auction Insights is also not
reachable through the API for this developer token — `auction_insight` is an unrecognized
resource, and `campaign_search_term_insight` is a different report requiring a single-campaign
filter.

The manifest carries the exact date range (2026-08-01 → 2026-08-31, never "Last 30 days"),
the seven required columns, the `<10%` literal-preservation rule, the
`NOT_AVAILABLE_MINIMUM_ACTIVITY` rule, the read-only contract, and the rule that Auction
Insights alone never justifies a competitor negative or a higher bid.

---

## 5. Gas Boiler landing-page gate — **14/20 PASS, 5 open**

`https://offer.ambientcoolingandheating.com/gas-boiler-repair/` · real browser, desktop
1440×2400 and mobile 390×1800 · GET only · nothing submitted, no `tel:` activated.
Screenshots at `evidence/boiler-lp-2026-09-10/`.

### The original defect is fixed

- H2 reads **"Your Gas Boiler Repair in 3 Simple Steps"** on both viewports
- H1: "Gas Boiler Repair in Severn, Severna Park & Columbia, MD"
- Title: "Gas Boiler Repair | Ambient Cooling & Heating"
- Canonical: `https://offer.ambientcoolingandheating.com/gas-boiler-repair/`
- **"HVAC Replacement" appears nowhere** — not in rendered text, not in HTML source
- 50 boiler mentions; all six H2s are boiler-specific
- Paid number **(410) 705-6354** displayed and linked as `tel:4107056354`
- Organic **(410) 761-0932** never rendered and not present in HTML source, so it cannot flash
- GTM **GTM-PQTPQ436** present in HTML and on the network
- DNI under `?gclid=…&utm_medium=cpc&campaignid=…`: paid number correct on both viewports,
  organic number never appears
- WhatConverts **is** running — `wc_swap`, `wc_client`, `wc_client_current`, `wc_visitor`
  cookies present *(an earlier verdict in this run said "not loaded"; that was my detection
  error — the script serves from a CDN host my filter missed, and the cookies settle it)*

### Open items

1. **No Privacy link and no Terms link on the page.** Searched every anchor by text and
   href on all five paid landing pages — none has either. The offer subdomain *does* have a
   Privacy Policy page (it appears in the 404 page's navigation), so this is a linking gap,
   not a missing document.
2. **Duplicate DOM IDs — three copies of the same form.** `gform_1` ×3, plus `gform_wrapper_1`,
   `gform_fields_1`, `gform_submit_button_1` and 30+ `field_1_*` / `input_1_*` IDs all ×3.
   This breaks label/input association and can break validation, accessibility, submission
   routing and conversion tracking. Unique IDs are required, or evidence that duplication is
   harmless.
3. **The form does not populate a gclid or UTM field.** The only attribution-looking hidden
   input is `gform_source_page_number_1`, a Gravity Forms internal. See §6 — this is
   account-wide, not boiler-specific.
4. **Form submission not performed — BLOCKED.** No approved non-production/test path exists
   for this property, and every prior QA in this engagement was explicitly GET-only.
   Submitting on production would create a real customer lead **and** fire a real Google Ads
   conversion, contaminating the same conversion data these CPC decisions depend on. Needs a
   staging clone or an approved test path.
5. **Thank-you behaviour and one-conversion-per-submission unverified**, because they cannot
   be observed without a submission.

### Consequence for the boiler keyword

The heading defect that originally blocked `[boiler repair]` is resolved. The gate as
specified also requires the form/DNI/thank-you/conversion tests, and item 4 blocks those.
**No boiler keyword package is presented for approval in this session.** The prior package
would in any case need revalidation against the fresh account before any fingerprint could
stand.

---

## 6. Account-wide landing-page findings

All five paid landing pages inspected with `?gclid=` present.

### An unaccounted third phone number on all five pages

Every page carries `tel:+14109141456` — **(410) 914-1456** — labelled "Call Now". That is
neither the paid number (410) 705-6354 nor the organic (410) 761-0932. It appears on
`/gas-boiler-repair/`, `/ac-repair/`, `/hvac-repair/`, `/hvac-installation/` and
`/hvac-replacement/`.

A caller who taps it is not being tracked as paid. This needs an explanation before any
call-attribution conclusion is trusted.

### No form on any of the five captures the click ID

| Page | Forms | Duplicate form IDs | Attribution fields populated |
|---|---|---|---|
| gas-boiler-repair | 3 | `gform_1` ×3 | none |
| ac-repair | 3 | `gform_1` ×3 | none |
| hvac-repair | 3 | `gform_1` ×3 | none |
| hvac-installation | 3 | `gform_1` ×3 | none |
| hvac-replacement | 3 | `gform_1` ×3 | none |

Form leads still arrive with a GCLID because WhatConverts attaches it from its own visitor
session cookie, not from a form field. **Phone calls do not get that treatment** — which is
exactly the gap measured in §7.

### No Privacy or Terms link on any of the five

Systemic, not page-specific.

---

## 7. WhatConverts connectivity and paid-lead reconciliation

**Reachable.** Profile 105803, 2026-08-14 → 2026-09-10, **101 leads**, 61 fields.
Credential values were never printed, logged or written. No name, number, email, address,
IP, recording, transcript or message body was retained. URLs were reduced to
host + path + attribution parameters. Lead IDs and GCLIDs are stored only as 16-character
SHA-256 prefixes.

Reconciled on gclid, gbraid, wbraid, UTM parameters, landing/lead URL query strings,
tracking number, campaign fields, date and lead status — **not** on GCLID alone.

### Every lead classified by evidence

| Count | Classification |
|---|---|
| 89 | **UNATTRIBUTED** — no click identifier and no UTM |
| 7 | PAID SEARCH — GCLID joined to one of the five campaigns |
| 4 | TAGGED non-paid, `utm_source=GBP` |
| 1 | PAID SEARCH — GCLID present but not resolved to a click |

**"UNATTRIBUTED" is not evidence of organic or any other channel.** WhatConverts
`lead_source` is a label applied by the tracking setup, not an independent measurement.

> **Correction to my earlier session-B report.** I previously wrote that 91 of 99 leads
> "arrive through Google Business Profile, Local Services Ads and organic". That inferred a
> channel from a label. The defensible statement is that 89 leads carry no click identifier
> and no UTM, so their channel is unproven.

### The measurement defect that matters most

**WhatConverts labels 21 leads `lead_medium=cpc`. Only 8 carry a click identifier.**

| lead_source | lead_medium | n | gclid | gbraid | utm | landing_url |
|---|---|---|---|---|---|---|
| google | cpc | 16 | 8 | 6 | 1 | 8 |
| google | organic | 5 | 0 | 0 | 0 | 5 |
| GBP | organic | 4 | 0 | 0 | 4 | 4 |
| GBP Traffic | (none) | 35 | 0 | 0 | 0 | 0 |
| 2nd GBP Traffic | (none) | 32 | 0 | 0 | 0 | 0 |
| *(LSA rows — out of scope, excluded from analysis)* | | 5 | 0 | 0 | 0 | 0 |

So **8 leads labelled `google / cpc` carry no click identifier at all.** All are Phone Calls
or Text Messages — zero web forms. None captured a landing URL. And every one of them landed
on a day when the five campaigns took valid paid clicks:

```
08-18 (7 clicks) 08-22 (5) 08-24 (18) 08-25 (17) 08-27 (17)
08-28 (15) 08-31 (5) 09-01 (6) 09-02 (7) 09-03 (4) 09-04 (1)
```

**Zero of them fall on a day with no paid clicks.** Combined with §6 — calls carry no click
ID because the forms/session linkage that works for web forms does not reach the call
record — the conclusion is that **paid-search call leads are losing their click ID.**

**Therefore the 5 unique qualified leads below are a FLOOR, not the true count, and the CPQL
figures are an upper bound.** The true CPQL cannot be computed until call click-ID
persistence is fixed. 6 leads also carry `gbraid`; all 6 also carry a gclid, and GAQL has no
gbraid lookup, so gbraid-only leads would be unjoinable by design.

### Unique qualified leads, by regime

Qualified = unique person, supported service, web form or call ≥60s, quotable, not spam.

| Campaign | Click date | Type | Status | Quotable | Secs | Unique qualified |
|---|---|---|---|---|---|---|
| AC Repair | 2026-08-21 | Web Form | Unique | Yes | — | **Yes** |
| AC Repair | 2026-08-22 | Web Form | Unique | Yes | — | **Yes** |
| AC Repair | 2026-08-25 | Web Form | Unique | Yes | — | **Yes** |
| HVAC Installation | 2026-08-21 | Phone Call | Unique | No | 57 | No |
| HVAC Installation | 2026-09-01 | Web Form | Unique | Yes | — | **Yes** |
| HVAC Repair | 2026-08-20 | Web Form | Unique | Yes | — | **Yes** |
| HVAC Repair | 2026-08-28 | Web Form | Unique | No | — | No |

**UNCAPPED regime, 2026-08-14 → 2026-09-03:**

| Campaign | Cost | Valid clicks | Unique QL | CPQL (upper bound) | Limit | Verdict |
|---|---|---|---|---|---|---|
| AC Repair | $3,051.47 | 28 | 3 | $1,017.16 | $150 | OVER |
| HVAC Installation | $2,914.33 | 112 | 1 | $2,914.33 | $280 | OVER |
| HVAC Repair | $1,906.86 | 27 | 1 | $1,906.86 | $250 | OVER |
| HVAC Replacement | $152.52 | 5 | 0 | n/a | $280 | — |
| Gas Boiler Repair | $0.00 | 0 | 0 | n/a | $250 | — |

**CAPPED regime, 2026-09-05 → 2026-09-09:** HVAC Installation $58.63 / 2 clicks, HVAC Repair
$45.08 / 2 clicks, everything else zero. **0 conversions. No CPQL is computable.**

---

## 8. Commercial HVAC Installation — drafted, nothing created

### Two hard blockers

1. **The landing page does not exist.**
   `https://offer.ambientcoolingandheating.com/commercial-hvac-installation/` returns
   **HTTP 404**. `https://ambientcoolingandheating.com/commercial-hvac-installation/`
   returns 200 but renders the generic site shell with the **organic** number
   (410) 761-0932, so it is not a usable paid destination either.
2. **The supplied launch pack is not on this machine.**
   `Ambient_Commercial_HVAC_Installation_Launch_Pack.docx`,
   `COMMERCIAL_HVAC_COPY_PASTE.txt` and the four `images/` assets were searched for across
   the repo, `D:\MG`, Downloads, Desktop and Documents. None found.

Per the instruction, all Google Ads drafts are completed and nothing is published.

### Architecture confirmed against the live account

Campaign 24132507747 `Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08`:
SEARCH channel, Google Search **on**, Search Partners **off**, Display **off**, PRESENCE geo,
TARGET_SPEND with a $30.00 ceiling, $176.15/day, one existing ad group (202339087634,
ENABLED). The new ad group inherits all of it. **No separate campaign is created.**

**`commercial` is not blocked anywhere that matters.** 0 campaign-level negatives containing
"commercial" on 24132507747; the account-level negative was removed by
`AMB-0909C-NEG-COMMERCIAL 9F88FEE76803`. The 41 shared-set rows containing "commercial" are
landscaping, tree and masonry BROAD terms in sets 11807294063 / 11811255121 / 11840874961 /
11840890006 — **all four have zero campaign links**, and BROAD word-subset matching means
none could block `commercial hvac installation` even if attached.

### Three packages, split by precondition

**`AMB-0910-COMM-1` · `A9173FADBA82` · 3 operations · create-PAUSED · VALIDATED_OK**

Ad group `SKAG | Commercial HVAC Installation`, PAUSED, in campaign 24132507747, plus
`"commercial hvac installation"` PHRASE and `[commercial hvac installation]` EXACT. No Broad.
No ads. A paused ad group with no ads cannot serve, so this is independent of the landing
page. `VALIDATED_OK — 3 operations, validate_only=True, partial_failure=False`.

*No ad-group negatives at launch.* The instruction permits only the reviewed negatives in the
supplied pack, and the pack is absent. Independently, a SKAG carrying only Phrase and Exact
`commercial hvac installation` already requires that contiguous phrase, so speculative
negatives would buy little and risk blocking valid commercial intent. No manufacturer name,
city name, free, quote, estimate, cost, pricing, building or property manager negative is
proposed.

**`AMB-0910-COMM-RSA-1` · `30312BC45992` · 2 operations · create-PAUSED · GATED**

RSA A: 3 keyword-forward headlines pinned to HEADLINE_1 — *Commercial HVAC Installation ·
Commercial HVAC Installers · Commercial HVAC in Maryland* — plus 12 unpinned and 4
descriptions. RSA B: 15 unpinned headlines, 4 descriptions, as a relevance/automation control.
All 30 headlines ≤30 chars, all 8 descriptions ≤90, zero duplicates, claim check **PASS**.

**Gate:** do not execute until the final URL returns HTTP 200 with commercial content, the
paid number (410) 705-6354, GTM-PQTPQ436, WhatConverts, unique DOM IDs, and Privacy + Terms
links, verified in a real browser on desktop and mobile.

**Copy provenance: agency draft to spec, not the supplied pack.** Reconcile before creating.

**This is not an evenly allocated A/B test.** Two RSAs in one ad group get uneven impression
allocation. A true test needs Google Ads Experiments, and any comparison must control device,
position, query mix and impression share.

No image asset is created. Generated images must never be presented as completed Ambient
projects.

**`AMB-0910-COMM-XNEG-1` · `A70260017DAD` · 1 operation · GATED**

BROAD `commercial` as an **ad-group** negative on the residential SKAG 202339087634 **only**.
No campaign-level or account-level negative.

**Gate:** execute only after the commercial ad group, destination, keywords and ads are
ENABLED and ELIGIBLE. Applied earlier it suppresses commercial demand instead of redirecting
it.

### Developer handoff — commercial landing page

Build on staging at `/commercial-hvac-installation/` on the **offer** subdomain. Required:
GTM-PQTPQ436 · WhatConverts DNI · click-ID and UTM capture into the form · paid number
**(410) 705-6354** only · organic (410) 761-0932 absent from rendered text *and* HTML ·
**unique DOM IDs** (do not replicate the `gform_1` ×3 defect) · one Google Ads conversion per
submission · canonical · **Privacy and Terms links** (missing on all five existing pages) ·
resolve the unaccounted `tel:+14109141456`. Copy and images come from the supplied pack when
it is provided. Forbidden: Licensed & Insured, emergency, 24/7, financing, rebates,
guarantees, guaranteed savings, #1.

---

## 9. CTR protocol and the AC Repair challenger

**`AMB-0910-RSA-ACR-1` · `19E2F2FFC311` · SUPERSEDED · DO_NOT_EXECUTE.** It used
*"Licensed & Insured AC Repair"* and *"Licensed and insured AC repair across Severn, Severna
Park and Columbia…"*. That claim is withdrawn from this workstream, so the fingerprint is
stale. Recorded at `plans/AMB-0910-RSA-ACR-1.SUPERSEDED.json`. **0 operations performed.**

**`AMB-0910-RSA-ACR-2` · `1F166DE17017` · 1 operation · create-PAUSED** replaces it. Same ad
group 202339087834, same final URL, same 3-pin structure, claim removed. 15 headlines ≤30
chars, 4 descriptions ≤90, zero duplicates, claim check PASS. Verified live state: ad group
holds 2 ads, both ENABLED and APPROVED (820900825416, 820900825419).

**Pinned to HEADLINE_1:** AC Repair in Severn, MD · AC Repair Near You Today ·
Air Conditioner Repair MD

**Why three pins and not one.** One pin fixes the most visible slot to a single asset and
stops Google testing openers, collapsing asset-level reporting on that slot to one data
point. Three materially different keyword-forward headlines guarantee a service-keyword
opener *and* preserve rotation, so the winning opener stays learnable. HEADLINE_3 is
deliberately **not** pinned, because position 3 is not guaranteed to show.

**The CTR evidence is a hypothesis, not a deficit.** Ad 820900825419 measured 2.77% CTR
against 820900825416's 3.56% in aggregate, but on **desktop** 825419 wins 1.82% vs 0.51%.
The aggregate gap is substantially a device-mix artefact. No CTR improvement is claimed.

Ad Strength will probably fall when pins are added. Ad Strength is not an optimization target
under agency policy; that is an accepted cost, not a regression.

**Test protocol:** never edit an approved serving RSA in place; create paused first; do not
enable challenger and control simultaneously; ≥14 settled days and ≥500 impressions per ad;
compare relevant CTR **by device** at equivalent position with query mix and impression share
controlled; require no deterioration in unique qualified conversion rate and no breach of the
$150 AC Repair CPQL.

---

## 10. Work order updated

`clients/ambient-cooling-heating/work-order.yaml` — backup at
`work-order.yaml.bak-2026-09-10c`, validator **PASS**.

- `licensed_and_insured_claim_authorized: false`, status `WITHDRAWN_FROM_THIS_WORKSTREAM`.
  The earlier same-day authorization is recorded as superseded, and the outstanding
  licence-number / certificate-of-insurance requirement is **closed by withdrawal**, not by
  obtaining the documents. Site evidence retained for record only.
- `local_services_ads_scope: OUT_OF_SCOPE_FOR_THIS_PROJECT` with the full scope fence.
- `search_monthly_maximum_usd: 13000`, basis "daily budget × 30.4, never × 30".
- `commercial_hvac_in_paid_scope: true` retained from session B.

---

## 11. Consolidated approval block

Fresh, safe, validated, **unexecuted** fingerprints only.

| Plan | Fingerprint | Ops | Class | Status |
|---|---|---|---|---|
| `AMB-0910-COMM-1` | `A9173FADBA82` | 3 | create-paused | **VALIDATED_OK — ready** |
| `AMB-0910-RSA-ACR-2` | `1F166DE17017` | 1 | create-paused | ready, not yet validated against the API |
| `AMB-0910-COMM-RSA-1` | `30312BC45992` | 2 | create-paused | **GATED** — final URL is 404 |
| `AMB-0910-COMM-XNEG-1` | `A70260017DAD` | 1 | reversible | **GATED** — commercial group must serve first |

To approve, supply the exact line, for example:

```
APPROVE AMB-0910-COMM-1 A9173FADBA82 3 operations FOR 2401959466
```

Creating a resource never enables it. Enabling requires a second approval after readback QA.

### Rejected / superseded — do not execute

| Plan | Fingerprint | Status |
|---|---|---|
| `AMB-0909C-CPC-INST-2` | `5D57E0EF3B70` | **REJECTED** — never revive |
| `AMB-0910-RSA-ACR-1` | `19E2F2FFC311` | **SUPERSEDED** — withdrawn claim |
| — | `46C39C6B7091`, `D448BFDE4650`, `23BE8FF0F24C`, `CE289F3508A2`, `A435FA09AC97`, `DE376F91F449` | superseded previously |

---

## 12. Blockers requiring a decision

1. **Claude in Chrome is not connected.** Blocks the six-ad Policy details inspection, the
   appeal submission, and all 11 August Auction Insights exports.
2. **No approved non-production/test path.** Blocks form submission, thank-you routing and
   one-conversion-per-submission verification on every landing page.
3. **Commercial landing page returns 404** and the **supplied launch pack is not on this
   machine.** Blocks `AMB-0910-COMM-RSA-1` and everything downstream of it.
4. **Unaccounted phone number `tel:+14109141456`** on all five paid landing pages.
5. **Paid-search call leads are losing their click ID** — 8 `google/cpc` leads with no click
   identifier, all calls, all on days with paid clicks. Until fixed, every CPQL in this
   report is an upper bound and no ceiling decision should rest on it.

---

## Evidence

```
reports/ambient-cooling-heating/evidence/
  2026-09-10c-readback-and-six-ad-policy.json      readback 0 FAIL + six-ad inventory
  2026-09-10c-whatconverts-full-reconciliation.json 101 leads, evidence-based classification
  2026-09-10c-wc-attribution-gap.json               the cpc-without-click-id cohort
  2026-09-10c-planner-and-auction-insights.json     75 geo targets, 5 keywords, API probe
  2026-09-10c-boiler-lp-gate.json                   20 verdicts, desktop + mobile + DNI
  2026-09-10c-lp-deep-inspection.json               all five pages: phones, cookies, forms
  boiler-lp-2026-09-10/                             desktop/mobile/paid screenshots
  auction-insights/2026-08/manifest.json            11 exports, all NOT_EXPORTED
receipts/live/AMB-0910-CPC-CAP-1-2026-09-10-EXECUTED.json
receipts/validate-only/AMB-0910-COMM-1-2026-09-10.json
clients/ambient-cooling-heating/plans/
  AMB-0910-COMM-1.json  AMB-0910-COMM-RSA-1.json  AMB-0910-COMM-XNEG-1.json
  AMB-0910-RSA-ACR-2.json  AMB-0910-RSA-ACR-1.SUPERSEDED.json
  AMB-0909C-CPC-INST-2.REJECTED.json
```

No credential, token, secret, or unredacted lead PII appears in any artifact.
