# Pro Green Landscape Solutions — Dallas / DFW
## Final Audit and Revamp Plan

| Field | Value |
| --- | --- |
| **Customer-facing business name** | **Pro Green Landscape Solutions** |
| **Market** | Dallas, Texas — Dallas–Fort Worth |
| **Google Ads account** | **Pro Green - Dallas - Live** |
| **Child customer ID** | **8735782888** (definitive identifier) |
| **Manager ID** | 3373711342 (Green Marketing) |
| **WhatConverts profile** | ProGreen DFW — **Profile ID 107007** |
| **Primary service** | sprinkler and irrigation repair |
| **Vertical** | landscaping |
| Document date | 2026-08-11 |
| Mode | **Read-only diagnosis and planning. Nothing has been implemented.** |

**Identity gate — PASSED on fresh API read, 2026-08-11.**
`customer.id 8735782888` · `descriptive_name "Pro Green - Dallas - Live"` · `manager false` ·
`test_account false` · `- live` marker present · USD · America/New_York.
Manager link read **from the child account only** (`customer_manager_link`), never by querying
the MCC as a target.

---

---

## 0-A. EXECUTION HAPPENED — 2026-08-11

**This account is no longer in preview-only state.** Scoped, reversible Google Ads changes were
executed on 2026-08-11 under explicit user authorization.

**Executed and verified (29/29 read-back checks PASS):** desktop re-enabled · 3 over-broad
negatives removed and 40 targeted negatives added · 8 in-scope keywords created PAUSED ·
3 challenger RSAs created PAUSED with minimal pinning · expired-discount callout and 5
winterization sitelinks paused · 3 verified-claim callouts created PAUSED · `utm_id` corrected on
3 paused campaigns · daily budget $32.50 → **$45.00**.

**Attempted and did not apply:** demoting the two WhatConverts conversion actions — the API accepts
the write but this account's account-level conversion goals discard it. Documented, not retried.

**Unchanged by design:** every final URL · every phone number · the call asset · all 74 location
criteria · presence targeting · the ad schedule · bidding strategy · networks · `6617381255`,
`6886101052`, `6886103719` · every legacy conversion action. **Nothing was deleted anywhere.**

Authoritative records:
`google-ads-current-page-strategy.md` · `google-ads-change-manifest.md` ·
`google-ads-execution-log.md` · `google-ads-post-change-verification.md` ·
backups in `backups/pre-change-2026-08-11T1300/`.

**Landing-page workflow superseded.** `landing-page-draft/` is retained for history only. The live
workflow now targets the client's WordPress/Divi template — see
`clickup-wordpress-landing-page-task.md`, `landing-page-template-character-budget.md`, and
`landing-page-content-backlog.md`.

---

## 0. STATUS — partially superseded on 2026-08-11

The user issued an **authoritative business-decision record** on 2026-08-11. Where this plan
conflicts with it, **the decision record wins.** See
**`clients/pro-green-dallas/confirmed-business-decisions.md`**.

The audit findings in §2–§6 remain accurate and were **re-verified against fresh API data on
2026-08-11**. The following planning conclusions are **corrected**:

| This document said | Corrected to | Where |
| --- | --- | --- |
| §17 Batch 1.3 — exclude `6886103719` from Conversions **now** | **Withdrawn from Batch 1.** Phone rule 9: not until every live URL dependency is gone **and** a tested non-duplicating replacement exists. Moves to cutover **step 9** | `batch-1-resource-level-preview.md` §3 |
| §17 Batch 1.6 — remove the `__awcc` tag **now** | **Withdrawn from Batch 1.** Phone rule 8: not while any live ad or asset still points at a compatible old page. Moves to cutover **step 10** | same |
| §17 Batch 2.5 — the ad schedule is misaligned and must be shifted | **WRONG. No change needed.** Intended hours are **7 AM–7 PM Central**; the configured **08:00–20:00 Eastern** already equals exactly that | `confirmed-business-decisions.md` §8 |
| §2.3 **F32** — "two **live-campaign** promotion assets point at `offerdfw`" | **WRONG.** Both campaign-asset links on the live campaign are **`REMOVED`**. They survive only as PAUSED links on two PAUSED campaigns | `batch-1-resource-level-preview.md` §4.2 |
| §3 **I7** — `AW-11240766632` is plausibly owned by manager `2815082755` | **WRONG on the manager.** `2815082755` is the **authorized ClickCease** integration. `AW-11240766632` ownership stays **[UNVERIFIED]**; an **Austin** configuration is now the leading hypothesis | `confirmed-business-decisions.md` §1–§2 |
| §4 **U-A** — unknown second manager | **CLOSED** — ClickCease, authorized. Never to be queried | same |
| §4 **U-C** — who answers (206) 890-3969 | **CLOSED** — the business owner; voicemail if unanswered | same |
| §10 / §15 Q3 — pick one of Page A, Page B, or `offerdfw` as canonical | **Superseded.** A **new** page is being built at a new host; none of the three is canonical | `canonical-landing-page-developer-handoff.md` |
| §11 — "10% OFF" and "Same Day" pending verification | **CLOSED.** 10% OFF is **expired and prohibited**; same-day is **conditional-only**, exact wording required | `confirmed-business-decisions.md` §5 |
| §14 — "no numeric forecast is credible" | **Still true**, but the economics are now anchored: **$2,000/month cap, $120 target CPL, $180 max per booked estimate, ~20 leads/week capacity** | `confirmed-business-decisions.md` §9 |

**New material facts discovered on 2026-08-11 and not present below:**

1. **Zero conversions since 2026-07-31.** MTD 2026-08-01→08-11: **$369.98, 46 clicks, 0 conversions.**
2. An **account-level ClickCease tracking template** exists and hard-codes `offerdfw…` in its
   `ccpturl` parameter — but it is **overridden** by campaign-level templates on every campaign.
3. Three campaigns carry a **wrong hard-coded `utm_id`** in their tracking template.
4. The account is spending **about half** its authorized $2,000 cap while losing **34.44%** of
   impression share to budget.

---

## 1. Executive summary

The account spends its full budget, buys the right kind of search, and then loses most of the
value in three places: **measurement, landing-page routing, and match quality.**

**The reported CPL of $484.11 is not a real CPL.** It is $2,904.68 divided by six conversions,
and the six are the only ones the account is still able to record. Two independent lead paths
are silently dead, and a third has just been armed to double-count.

Five findings drive everything else:

1. **The website-call conversion action was built for a different landing page.** Action
   `6886103719` swaps for **(214) 301-3385**. That number does render — on
   `offerdfw.progreenlandscapesolutions.com`, a *third* landing page that is clean, tag-correct,
   and still linked to the live campaign through its promotion assets. The ads now point
   somewhere else. On those pages the number never appears, so the action has recorded nothing
   since **2026-02-28**.
2. **Both live landing pages are inside a 50/50 A/B experiment that ignores the ad's final URL.**
   Nelio experiment 3619 assigns every visitor to Page A (`postId 3332`) or Page B
   (`postId 3369`) at roughly even odds, in both directions. Landing-page reporting in Google
   Ads is therefore meaningless, and one ad group is paying to send traffic to a page that half
   the time is not the page that loads.
3. **A duplicate-counting bomb is armed but has not yet gone off.** `Whatconverts Calls`
   (`7717433754`) and `Whatconverts Form` (`7717433751`) were created between 2026-08-07 and
   2026-08-11. Both are **primary** and **included in Conversions**. Both have received **zero**
   data so far. The moment WhatConverts sends its first call, the same physical call counts
   twice — once natively on `6617381255`, once on the import — because the call asset dials
   **(214) 301-3385, which is itself a WhatConverts tracking number.**
4. **The main CTA on both live pages is broken.** `href="tel:%91phone%93"` — an unresolved
   shortcode, not a phone number, on traffic that is **100% mobile**.
5. **A second, unidentified manager account is linked to this child account** and a second
   Google Ads tag (`AW-11240766632`) and GTM container run on the landing pages, targeting an
   Austin number. Ownership is unresolved and nothing should be removed until it is.

Recommendation: **improve the existing campaign in place; do not replace it.** The structure,
targeting, and keyword themes are sound. The losses are in tracking, routing, and a set of
specific, fixable settings.

---

## 2. Proven facts

Every row was directly observed. API rows come from fresh `SELECT`-only queries against
`8735782888` on 2026-08-11; page rows from GET-only browser inspection the same day.

### 2.1 Account and conversion configuration

| # | Fact | Source |
| --- | --- | --- |
| F1 | Account conversion tracking ID is **11237210508**; `cross_account_conversion_tracking_id` = **0**; status `CONVERSION_TRACKING_MANAGED_BY_SELF`; `google_ads_conversion_customer` = `customers/8735782888` | `customer.conversion_tracking_setting` |
| F2 | **`accepted_customer_data_terms` = true** and **`enhanced_conversions_for_leads_enabled` = true** | same |
| F3 | **Two manager links, both ACTIVE**: `3373711342` (Green Marketing, link 342593485) and **`2815082755` (unidentified, link 345783752)** | `customer_manager_link`, read from the child |
| F4 | The account now holds **14** conversion actions, up from 12 on 2026-08-07 | `conversion_action` |
| F5 | **`Whatconverts Form` = 7717433751**, type **UPLOAD_CLICKS**, category CONTACT, origin WEBSITE, ENABLED, **primary**, **in Conversions**, ONE_PER_CLICK, 60-day click / 15-day view, default value 1.0, **`always_use_default_value` = false** | same |
| F6 | **`Whatconverts Calls` = 7717433754**, type **UPLOAD_CALLS**, category CONTACT, origin CALL_FROM_ADS, ENABLED, **primary**, **in Conversions**, ONE_PER_CLICK, 60-day click / 30-day view, default value 1.0, **`always_use_default_value` = false** | same |
| F7 | **Both WhatConverts actions have received nothing** — `conversion_last_conversion_date` empty and `conversion_last_received_request_date_time` at epoch | `metrics` on `conversion_action` |
| F8 | Goals **CONTACT/WEBSITE** and **CONTACT/CALL_FROM_ADS** are both **biddable = true**, as are PHONE_CALL_LEAD/CALL_FROM_ADS and SUBMIT_LEAD_FORM/WEBSITE | `customer_conversion_goal` |
| F9 | `6886103719` (WEBSITE_CALL, 30 s) last converted **2026-02-28**; `6616343220` "Clicks to call" **also last converted 2026-02-28** | `metrics` |
| F10 | `6617381255` "Calls from Ads" (AD_CALL, 60 s) last converted 2026-07-29 | same |
| F11 | 90-day conversions: `6617381255` = **4.00**, `6886101052` = **2.00**, everything else **0**. All-conversions total **22.00** | conversion breakdown, campaign **and** customer level |
| F12 | `6548857156` "GSA Submit Lead Form" is ENABLED and still **receiving tag requests** (2026-08-10 15:51) while excluded from Conversions | `metrics` + config |

### 2.2 Campaign

| # | Fact | Value |
| --- | --- | --- |
| F13 | One serving campaign: **Irrigation & Sprinklers, 20315156610**, SEARCH, ENABLED | — |
| F14 | Bidding **TARGET_SPEND** (Maximize Clicks) with a **$18.00 CPC ceiling**; budget **$32.50/day**, standard, not shared (budget 12723712793) | — |
| F15 | 90-day: **3,475 impr · 171 clicks · $2,904.68 · CTR 4.92% · avg CPC $16.99 · 6 conv · 22 all-conv** | 2026-05-09→08-06 |
| F16 | Impression share **58.37%**, lost to budget **16.72%**, lost to rank **24.90%** | same window |
| F17 | Last 30 days **worse**: IS **38.21%**, lost budget **27.67%**, lost rank **34.11%**; $1,006.58 for 3 conv | 2026-07-13→08-11 |
| F18 | **Invalid clicks 25 of 171 (14.6%)** in 90 days; 16 of 87 (18.4%) in the last 30 | — |
| F19 | **100% MOBILE.** DESKTOP (30000) and TABLET (30002) carry an explicitly **set** `bid_modifier` of **0.0 = −100%**; MOBILE (30001) has no modifier set | field-presence check |
| F20 | Networks: Google Search on, **Display off**, **Search Partners off now** — but the window contains **107 partner impressions, 1 click, $5.79**, so it was on during the period | — |
| F21 | Geo: **74 positive location targets, zero negatives**, `PRESENCE`/`PRESENCE`. All 23 cities with delivery are DFW; **no out-of-market geo waste** | `geographic_view`, all `LOCATION_OF_PRESENCE` |
| F22 | Ad schedule: **7 days, 08:00–20:00 in the account time zone**, which is **America/New_York**. Delivery observed only in hours 8–19 | `campaign_criterion` + hour segment |
| F23 | Campaign carries **620 negative keywords** (455 broad, 18 phrase, 147 exact), **6 IP blocks**, 22 user-interest criteria, 1 language (English) | — |
| F24 | **`cost` is a PHRASE negative (criterion 40961223)** | direct GM policy conflict |
| F25 | Broad negatives **`sprinkler heads` (23836346)**, **`head replacement` (301794223657)**, **`sprinkler box` (23423966)** block core repair queries | — |
| F26 | Three serving ad groups, each with **exactly one enabled RSA** (GM standard is two) | — |
| F27 | **Every headline and description in all three live RSAs is pinned.** 15 headlines across 3 slots, 4 descriptions across 2 | — |
| F28 | Ad-group results: **Irrigation Repair Near Me** $1,141.07 → 5 conv · **Sprinkler Repair Near Me** $926.74 → 1 conv · **Sprinkler System Repair** $836.88 → **0 conv** | — |
| F29 | Quality Score is **3–5** where measured; **Landing page experience BELOW_AVERAGE** and **Expected CTR BELOW_AVERAGE** on the top spenders | — |
| F30 | **27 sitelinks** on one ad group, 22 on each of the others, with heavy duplication and **4 copies of "Irrigation Winterization"** — an explicitly excluded service | ad-group asset links |
| F31 | **Zero customer-level assets.** One CALL asset **89872541418 = (214) 301-3385** → conversion action `6617381255`, `USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION` | — |
| F32 | **Two PROMOTION assets on the live campaign point to `https://offerdfw.progreenlandscapesolutions.com/`** | — |
| F33 | Competitor and out-of-market search terms cost **$332.49 with 0 conversions** — "lawn sense dallas" $175.47, "lee engineering" $80.13, plus two **Albuquerque** queries | search terms |
| F34 | Search-term report accounts for only **$1,139.78 of $2,904.68**; the rest is withheld low-volume | — |
| F35 | Day of week: **Monday $564.55 → 0 conv**, Sunday $414.16 → 0, Saturday $209.72 → 0. Thu/Fri carry 4 of 6 conversions | — |

### 2.3 Landing pages and tracking

| # | Fact | Source |
| --- | --- | --- |
| F36 | **A third landing page exists: `offerdfw.progreenlandscapesolutions.com`** — "10% OFF Irrigation Repair in Dallas, TX" | live GET |
| F37 | That page renders **`tel:2143013385`** and visible **+1 (214) 301-3385** — **the exact number action `6886103719` is configured to swap** | live DOM |
| F38 | It loads **GTM-NZSMS9RB only** — no GTM-54Q4TVXF, no second GA4, no Facebook or Nextdoor pixel | `google_tag_manager` |
| F39 | It has **no Nelio, no NitroPack, and no `tel:%91phone%93` placeholder** | live DOM |
| F40 | Pages A and B render **(214) 301-4622** at runtime and **`tel:(214) 301-4622`**, swapped by WhatConverts from **(214) 300-9564** | live DOM |
| F41 | **The broken CTA `tel:%91phone%93` is still live on both pages** | live DOM |
| F42 | The WhatConverts script is **`https://s.ksrndkehqnwntyxlhgto.com/107007.js?ver=7.0.3`** — profile **107007**, matching the console URL exactly | live DOM |
| F43 | WhatConverts runtime is fully present: cookies `wc_visitor`, `wc_client`, `wc_client_current`, `wc_swap`; functions `wc_visitor_init`, `wc_form_ypbib` | live DOM |
| F44 | Browser localStorage holds **both** Google website-call swap records: `inV_CKe1xtMZEIzzqO4p,2143013385` and `AkKoCM2mqNMZEKj5gfAp,5128902716` | live DOM |
| F45 | **Nelio experiment 3619**: `alternatives = [{postId 3332, testAgainstExistingContent}, {postId 3369, isExistingContent}]`, `participationChance 100`. **Page A = 3332, Page B = 3369.** Both pages serve the identical config | server GET of both pages |
| F46 | Assignment is sticky per browser via `nabAlternative`; navigating to Page B with `nabAlternative=0` lands on Page A | live |
| F47 | Gravity Forms on all three pages expose `gform_field_values` — **empty** — and no `gclid`/`gbraid`/`wbraid`/`utm_` hidden fields. Zero click-ID strings in any page's HTML | live DOM |
| F48 | Pages A/B run **two GTM containers, two GA4 properties, AW-11240766632, a Facebook pixel, and a Nextdoor pixel**; `offerdfw` runs none of them | live DOM |
| F49 | On this visit **NitroPack deferred 0 of 73–75 scripts** and tags loaded without interaction — different from the 2026-08-10 observation of 21–22 deferred scripts | live DOM |

---

## 3. High-confidence inferences

Clearly labelled. **None of these is proven and none may be implemented as fact.**

| # | Inference | Basis | What would prove it |
| --- | --- | --- | --- |
| **I1** | **Action `6886103719` was built for `offerdfw.progreenlandscapesolutions.com`, not for the `/dfw/offer-*` pages.** Traffic was later moved to the `/dfw/` pages and the tag was never re-pointed | The `offerdfw` page renders exactly (214) 301-3385 (F37) and runs exactly the one correct container (F38); the `/dfw/` pages render neither | Site or GTM version history; ad final-URL change history |
| **I2** | **Something changed on or about 2026-02-28 that moved traffic off `offerdfw`.** Two independent actions — `6886103719` and `6616343220` — stopped converting on the same date | F9 | Change history for ad final URLs and the WordPress pages |
| **I3** | **Roughly half of each ad group's traffic lands on the page the ad did not specify.** Two alternatives at 100% participation implies about a 50/50 split | F45, F46 | Nelio's own experiment report, or many isolated assignments |
| **I4** | **The 8 call-asset calls also exist in the WhatConverts ledger**, because the call asset dials a WhatConverts tracking number | F31 + (214) 301-3385 is `GSAs traffic`, source Google Call Extension | Reconcile WhatConverts call log against Google Ads |
| **I5** | **Real lead volume is materially higher than 6.** Website calls have been structurally impossible since February, and the primary mobile CTA is broken | F9, F41 | Working measurement for one full month |
| **I6** | **WhatConverts does capture click IDs**, even though Gravity Forms does not | The script carries gclid/gbraid/wbraid/utm handling; `wc_client` holds visitor attribution (F43) | A WhatConverts lead export showing a populated GCLID |
| **I7** | **`AW-11240766632` / `GTM-54Q4TVXF` belong to the second manager `2815082755` or to a prior agency** | Not this child's conversion ID (F1); an Austin number on a Dallas page; a second ACTIVE manager link exists (F3) | Client tagging history, or asking the second manager's owner |
| **I8** | **The `Sprinkler System Repair` ad group's zero conversions are a measurement artifact, not proof it fails.** It sends traffic to Page A, where only form leads can currently be counted | F28 + F9 | Re-measure after tracking is repaired |
| **I9** | **The account is budget-limited and getting more so.** IS lost to budget rose from 16.7% to 27.7% | F16, F17 | — |

---

## 4. Remaining unknowns

**Do not act on any of these.**

| # | Unknown | Why it matters | How to close |
| --- | --- | --- | --- |
| U-A | **Who owns manager account `2815082755`** | It has active access to this client's account | Ask the client / check MCC invitations. **Do not query that account.** |
| U-B | **Who owns `AW-11240766632` and `GTM-54Q4TVXF`** | Removing another party's tags could destroy their measurement and breach an agreement | Client tagging history |
| U-C | **Whether `(206) 890-3969` is Pro Green's real answering line** | It is the call-flow destination; a Seattle NPA on a DFW account | Client confirmation |
| U-D | **The WhatConverts website pool configuration** — pool name, assigned numbers, URL triggers, attribution rules | Decides the dedupe design | WhatConverts console. **Blocked: login barrier — see §16.** |
| U-E | **Why the two WhatConverts actions exist but have received nothing** | Determines whether the duplicate risk is imminent or dormant | WhatConverts integration send log |
| U-F | **What changed on 2026-02-28** | Confirms I1/I2 | Site + GTM version history |
| U-G | **Whether the `offerdfw` page is intended to stay in service** | Two promotion assets on the live campaign still point at it | Client decision |
| U-H | **NitroPack's real deferral behaviour on mobile** | 100% of traffic is mobile; desktop behaviour differed between two inspections (F49) | Real mobile-device test |
| U-I | **Whether "Same Day", "18 Point Check", "Licensed & Insured", "10% OFF" are verified claims** | They run in live ads and page copy | Client confirmation |
| U-J | **Average job value, close rate, target CPL/CPA** | Every profit calculation depends on them | Client input |

---

## 5. Root causes of the $484.11 reported CPL

$484.11 = $2,904.68 ÷ 6. Both halves of that fraction are wrong.

### The denominator is understated

| Cause | Effect |
| --- | --- |
| **Website-call action pointed at a number that does not render on the live pages** (F37, I1) | Every website call since 2026-02-28 is uncounted |
| **The primary mobile CTA is a broken shortcode** (F41) | On 100%-mobile traffic, the main call path does not dial at all |
| **"Clicks to call" also died on 2026-02-28** (F9) | A second call signal lost |
| **Forms carry no click IDs** (F47) | CRM-side attribution is broken even when a form lead does arrive |

### The numerator contains real waste

| Cause | 90-day cost | Conversions |
| --- | --- | --- |
| Competitor and out-of-market queries (F33) | **$332.49** | 0 |
| `Sprinkler System Repair` ad group (F28) | $836.88 | 0 — but see **I8** |
| Monday delivery (F35) | $564.55 | 0 |
| Invalid clicks, 14.6% (F18) | ~$424 gross | — |
| Search Partners while it was on (F20) | $5.79 | 0 |

### And the traffic is routed randomly

Roughly half of every ad group's clicks land on the page the ad did not name (I3), so
landing-page optimisation and reporting have both been operating on noise.

**The honest statement: cost per *countable* conversion is $484.11. True cost per lead is
unknown and materially lower. No bidding decision may be made on this number.**

---

## 6. Corrected tracking architecture

### Target state

| Layer | Role |
| --- | --- |
| **WhatConverts (profile 107007)** | The **single call ledger** for all sources. It already swaps reliably and already captures click IDs (I6) |
| **Google Ads `6617381255` (AD_CALL)** | **Native SERP call-asset conversions. Stays.** This is the only call signal working today |
| **Google Ads `7717433754` (Whatconverts Calls, UPLOAD_CALLS)** | Imports **non-call-asset** qualified calls only — website and organic. **Must exclude call-asset calls** |
| **Google Ads `7717433751` (Whatconverts Form, UPLOAD_CLICKS)** | Imports qualified form leads |
| **Google Ads `6886103719` (WEBSITE_CALL)** | **Retired as a bidding conversion.** Retained, disabled from the Conversions column, for history |
| **Gravity Forms** | Gains hidden `gclid`/`gbraid`/`wbraid`/UTM/landing-page fields so the CRM can join |
| **GTM-NZSMS9RB** | Keeps the conversion linker and the Ads tags. The `__awcc` phone tag is **removed**, not re-pointed |

### Why the `__awcc` tag is removed rather than fixed

Re-pointing it at (214) 300-9564 would aim **Google's `autoreplace` and WhatConverts'
`replace_number` at the same string on the same DOM**. Whichever ran last would win. That race
is the current failure with a shorter fuse. With WhatConverts as the ledger, Google's website-call
forwarding is redundant.

---

## 7. Conversion deduplication design

**The risk, stated exactly.** The call asset `89872541418` dials **(214) 301-3385**, which is a
**WhatConverts tracking number** (`GSAs traffic`, source `Google Call Extension`). So a single
SERP call-asset call is seen by **both** systems:

```
Caller taps the call asset  →  rings (214) 301-3385
     ├── Google counts it natively            → 6617381255  (AD_CALL, 60 s)      [in Conversions]
     └── WhatConverts logs it as a new lead    → 7717433754  (UPLOAD_CALLS)      [in Conversions]
```

Both actions are primary, both are in the Conversions column (F5, F6, F8). **Today this costs
nothing because the import has never fired (F7). It will double-count on the first send.**

### The dedupe rule

WhatConverts already labels the source of every number. **(214) 301-3385 is the only
`Google Call Extension` number in use by this account's call asset.** So:

> **Do not import any WhatConverts call whose receiving tracking number is (214) 301-3385.**
> Those calls are already counted by `6617381255`.

Three ways to implement it, in order of preference:

| Option | Mechanism | Trade-off |
| --- | --- | --- |
| **D1 — filter at the vendor (preferred)** | Exclude the `Google Call Extension` source from the Google Ads integration's Phone Calls feed | Cleanest. One place. Needs the console. |
| **D2 — separate the columns** | Set `7717433754` to **secondary / not in Conversions**, keep it as a diagnostic; keep `6617381255` as the bidding signal | Safe and instantly reversible. No vendor access needed. **Recommended first move.** |
| **D3 — retire the native action** | Turn off `6617381255`, import everything through WhatConverts | Loses the only currently-working signal and discards history. **Not recommended.** |

**Form leads do not have this problem** — no native action counts form submissions from the
landing pages except `6886101052`, which fires on the page's own thank-you behaviour. That pair
**does** need checking before `7717433751` goes live, because both would count the same
submission. Same remedy: D2.

**Until dedupe is proven, no call-asset call may be imported.** That is a hard constraint.

---

## 8. Campaign revamp recommendation

**Improve in place. Do not replace.**

| Reason | Evidence |
| --- | --- |
| The structure is already close to GM standard | 3 themed ad groups, Phrase + Exact only, no broad match |
| Targeting is correct | 100% of delivery is DFW presence-based (F21) |
| The campaign has 3 years of history and an established Quality Score baseline | started 2023-06-28 |
| The failures are configuration and measurement, not architecture | §5 |
| Rebuilding would discard learning **and** would not fix a single root cause | — |

The paused **Performance Max** campaign (`22379036365`, $250/day, PRESENCE_OR_INTEREST, Display
and Search Partners on) **stays paused**. It must not be enabled while conversion data is
unreliable — it would optimise toward a broken signal at eight times the current budget.

---

## 9. Keyword and negative-keyword recommendations

### 9.1 Keywords to keep — they carry the account

| Keyword | Match | 90-day cost | Conv |
| --- | --- | --- | --- |
| `irrigation repair services` | PHRASE | $826.59 | — |
| `sprinkler repair services` | PHRASE | $713.68 | — |
| `sprinkler system repair` | PHRASE | $528.44 | — |
| `irrigation repair near me` | EXACT | $105.26 | 1 |
| `irrigation companies near me` | EXACT | $174.49 | 2 |
| `sprinkler repair` | EXACT | $160.96 | — |

### 9.2 Negatives to **remove** — they block buyer intent

| Criterion ID | Negative | Match | Why remove |
| --- | --- | --- | --- |
| **40961223** | **`cost`** | PHRASE | Blocks *every* query containing "cost". Direct violation of GM protected-term policy, and the ads themselves promise quotes and estimates |
| **23836346** | `sprinkler heads` | BROAD | Blocks "fix broken sprinkler heads", "sprinkler head repair" — core service |
| **301733462194 / 301794223657** | `head replacement` | BROAD | Blocks "sprinkler head replacement" — core service |
| **23423966** | `sprinkler box` | BROAD | Blocks "sprinkler valve box repair" — core service |
| **11884132004** | `just sprinklers` | BROAD | Broad match makes this block any query containing "just" and "sprinklers" |

### 9.3 Negatives to **add** — proven waste

Exact-match, campaign level, from F33:

`lawn sense dallas` · `lawn sense plano` · `lawn sense texas` · `lee engineering irrigation` ·
`lee engineering arlington texas` · `garden springs irrigation` · `h20rx` · `rockwall irrigation`

Phrase-match: `albuquerque` · `sioux falls` · `austin` *(guard: verify no DFW street or
neighbourhood name collides before adding city negatives)*

**Intent check applied per GM policy:** none of the additions touch `near me`, `quote`, `price`,
`pricing`, `cost`, `best`, `hire`, `local`, or `emergency`.

### 9.4 Match-type policy

Already compliant — Phrase and Exact only, no Broad. **No change, and no Broad Match without
separate approval.**

---

## 10. Ad-group and landing-page structure

### Current

| Ad group | Status | Final URL of the one live RSA | 90-day |
| --- | --- | --- | --- |
| Sprinkler Repair Near Me | ENABLED | **`/dfw/offer-sprinkler-repair-b/`** | $926.74 → 1 conv |
| Irrigation Repair Near Me | ENABLED | `/dfw/offer-sprinkler-repair-a/` | $1,141.07 → 5 conv |
| Sprinkler System Repair | ENABLED | `/dfw/offer-sprinkler-repair-a/` | $836.88 → 0 conv |

Because of Nelio (I3), **none of these final URLs reliably determines the page that loads.**

### Proposed

1. **Resolve the landing-page question first.** Three candidate pages exist and they are not
   equivalent — `offerdfw` is clean and tag-correct; A and B carry duplicate tagging, NitroPack,
   the broken CTA, and the A/B experiment. This is a business decision (§15, Q3).
2. **End or pause Nelio experiment 3619** so a landing page means what it says. Until then, no
   landing-page conclusion is valid.
3. **Keep the three-ad-group theme split.** It matches GM's one-theme-per-ad-group standard and
   the themes are genuinely distinct.
4. **Point all three ad groups at one verified page** until an experiment can be run properly —
   through Google Ads ad variations or a drafted experiment, not a WordPress plugin that
   overrides the ad's own URL.

---

## 11. Proposed RSA and asset improvements

### RSAs

| Issue | Now | Proposed |
| --- | --- | --- |
| **Every asset pinned** (F27) | 15 headlines locked into 3 slots, 4 descriptions into 2 | Unpin most. Keep at most one pinned headline for the keyword theme. Pinning everything is why Ad Strength is AVERAGE and why no combination testing has ever happened |
| **One RSA per ad group** (F26) | 1 enabled | **2 per ad group**, per GM standard, each tailored to keyword and page |
| **Unverified claims** | "Same Day", "18 Point Sprinkler Check" | Hold until verified (§15, Q5). Remove if unverifiable |
| Ad relevance BELOW_AVERAGE on `sprinkler system repair` | — | Tighten headline 1 to the exact theme |

The existing copy is otherwise good: natural language, `near you` used correctly instead of
repeated `near me`, and genuine service specifics (leaks, stuck zones, valves, backflow,
timers).

### Assets

| Asset | Issue | Proposed |
| --- | --- | --- |
| **Sitelinks** (F30) | 27 / 22 / 22 with 4× "Irrigation Winterization" — an **excluded** service — plus 4× duplicate "Sprinkler Repair" and two competing URL patterns | Cut to **6–8 repair-intent sitelinks** on one canonical URL pattern (§15, Q4) |
| **Callouts** | "Get Free Online Quote", "Licensed & Insured", "Claim Your Discount", "Hassle-Free Service" | Keep, **pending verification of "Licensed & Insured"** |
| **Structured snippet** | Service catalog: Sprinkler Repair, Irrigation Repair, Leak Repair, Sprinkler System Repair, Valve Repair, System Inspection | **Correct and on-service. No change.** |
| **Call asset 89872541418** | (214) 301-3385 → `6617381255` | **No change.** Do not touch the live number |
| **Promotion assets** 89872396866, 89872442988 | Point at `offerdfw.*` while the ads point at `/dfw/` | Resolve with the landing-page decision |
| **Customer-level assets** | None exist | Consider account-level callouts after the sitelink cleanup |

---

## 12. Measurement and profit-reporting plan

### Dashboard formulas

```
CPL                  = cost / leads
CPQL                 = cost / qualified_leads
CAC                  = cost / sold_jobs
Close rate           = sold_jobs / qualified_leads
Revenue              = sum(sold_job_revenue)
Gross profit         = revenue - direct_job_cost
ROAS                 = revenue / cost
Profit after ad spend = gross_profit - cost
```

**Costs the dashboard will not include** and must state on its face: WhatConverts subscription,
CRM licence, agency management fee, NitroPack, and any call-answering service. Profit after ad
spend is therefore **before** those.

### Data joins

| Field | Source |
| --- | --- |
| `gclid` / `gbraid` / `wbraid` | WhatConverts visitor record (I6) + new Gravity Forms hidden fields |
| campaign / ad group / keyword / device / landing page | Google Ads, joined on click ID |
| lead ID | WhatConverts — **the dedupe key** |
| qualified / sold, revenue, job cost | CRM |
| consent status | to be captured |

Offline outcomes use the **Google Data Manager API** per `CLAUDE.md`. The legacy Google Ads
upload path is not to be used unless the developer token is confirmed eligible.

### The blocker to profit reporting

WhatConverts is set to **`Not Updating Existing Conversions`**. Sold-job revenue cannot flow back
to Google Ads in that state, so ROAS and profit-after-ad-spend cannot be computed from Ads data
alone until it changes. **That change is not proposed here** — it is a live integration setting
and needs its own approval after dedupe is proven.

---

## 13. Prioritised 30 / 60 / 90-day plan

### First 30 days — make the numbers true

1. Neutralise the duplicate-counting risk (**Batch 1**)
2. Retire `6886103719` from the Conversions column
3. Fix the broken `tel:` CTA (**Batch 1**)
4. End or pause Nelio 3619; decide the canonical landing page
5. Add click-ID capture to Gravity Forms
6. Add the proven-waste negatives; remove the policy-violating ones (**Batch 2**)

**Do not touch bidding in this window.** Measure for one clean month first.

### Days 31–60 — reduce waste, restore reach

1. Re-enable desktop and tablet unless the client confirms the exclusion was deliberate
2. Correct the ad schedule for the Eastern/Central offset
3. Sitelink cleanup; remove winterization from a repair campaign
4. Second RSA per ad group; unpin
5. Review the Monday and weekend spend pattern against real leads
6. Resolve ownership of `AW-11240766632` and manager `2815082755`

### Days 61–90 — optimise on trustworthy data

1. Evaluate a move from Maximize Clicks to a conversion-based strategy **only if** 30+ clean
   conversions exist
2. Turn on offline outcome import via Data Manager API
3. Budget decision using real CPL and IS-lost-to-budget
4. Stand up the profit dashboard
5. Re-evaluate Performance Max — still paused by default

---

## 14. Expected impact and risks

**Impact is expressed as direction and mechanism, not as a percentage.** The account has six
countable conversions in 90 days; that is far too small a base for a credible numeric forecast,
and any percentage would be false precision.

| Change | Mechanism | Confidence |
| --- | --- | --- |
| Fix CTA + tracking | Recovers call leads that already happen but are invisible on 100%-mobile traffic | **High** |
| Dedupe before import | Prevents an inflated Conversions column that would corrupt any future bidding | **High** |
| End the A/B redirect | Makes landing-page data mean something for the first time | **High** |
| Remove `cost` negative | Restores a documented buyer-intent query class | **High** |
| Restore desktop/tablet | Adds inventory in a budget-limited account where 24.9% of IS is lost to rank | **Medium** — depends on U-J |
| Competitor negatives | Recovers ~$332 per 90 days of proven-zero spend | **High** — directly measured |
| Sitelink cleanup | Removes off-service dilution | **Medium** |

### Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Removing another party's tags breaks their measurement or breaches an agreement | **High** | **Nothing is removed until ownership is established** (U-B) |
| Changing a live phone number drops calls | **High** | **No phone number is changed anywhere in this plan** |
| Retiring a primary conversion changes the Conversions column | Medium | Expected and intended; the column is currently wrong. Fully reversible |
| Editing a live Gravity Form breaks submissions | Medium | Gravity Forms keeps revisions; verify in the DOM without submitting |
| Un-deferring NitroPack scripts lowers PageSpeed | Medium | Reversible; measure Core Web Vitals before and after |
| Ending the Nelio experiment discards in-flight data | Low–Medium | Export the Nelio report first |
| Re-enabling desktop raises cost in a budget-capped account | Medium | Stage it; watch CPL for two weeks |

---

## 15. Questions that genuinely require business input

| # | Question | Blocks |
| --- | --- | --- |
| **Q1** | **Who owns manager account `2815082755`?** It has ACTIVE access to this child account and neither Green Marketing nor the client has identified it | Batch 1 governance; U-A |
| **Q2** | **Who owns `AW-11240766632` and GTM container `GTM-54Q4TVXF`?** They run on the landing pages and target an Austin number | Batch 1; nothing is removed until answered |
| **Q3** | **Which landing page is canonical** — `offerdfw.progreenlandscapesolutions.com`, `/dfw/offer-sprinkler-repair-a/`, or `-b/`? Is the Nelio A/B test deliberate, and may it be ended? | Batches 1 and 3; the biggest single decision |
| **Q4** | **Which sitelink URL pattern is correct** — `/dfw/services/<svc>/` or `/dfw/services/landscaping/<svc>/`? Both are live | Batch 3 |
| **Q5** | **Are "Same Day", "18 Point Check", "Licensed & Insured", and "10% OFF" verified and current?** They run in live ads and page copy | Batch 3 |
| **Q6** | **Does `(206) 890-3969` terminate at Pro Green?** It is the call-flow destination and a Seattle area code | Batch 1 verification |
| **Q7** | **Were the desktop and tablet exclusions deliberate?** | Batch 2 |
| **Q8** | **Intended advertising hours in Dallas local time.** The schedule is 08:00–20:00 **Eastern** = 07:00–19:00 Central | Batch 2 |
| **Q9** | **Qualified-call threshold — 30 or 60 seconds?** The two live call actions disagree | Batch 1 |
| **Q10** | **Average completed-job value, gross margin, lead-to-sale close rate, and target CPL/CAC** | §12 and all of Batch 4 |
| **Q11** | **Should the paused Performance Max campaign stay paused?** Recommended: **yes**, while data is unreliable | Batch 4 |

---

## 16. Access still required

| Item | Status |
| --- | --- |
| Google Ads API, child `8735782888` | **Working.** Reauthenticated; identity gate passed 2026-08-11 |
| Public landing pages | **Working.** GET-only inspection completed |
| GTM container payloads | **Working.** Both containers read from their published `gtm.js` |
| **WhatConverts console** | **BLOCKED — login barrier.** `leads.greenmarketingfl.com` redirected to a login screen in the automation browser profile. No credentials were entered and none are requested. Closes U-D and U-E |
| GTM edit/preview access | Not yet needed — required only when Batch 1 is approved |
| WordPress / Gravity Forms | Not yet needed — required for Batches 1 and 3 |
| CRM | Required for §12 |

---

## 17. Implementation batches

**No batch is approved. Nothing has been implemented. Every batch below is a proposal.**

---

### Batch 1 — Tracking integrity and conversion deduplication

**Objective.** Make the Conversions column mean one lead per lead, restore the mobile call path,
and stop the duplicate-counting risk before it fires.

**Dependencies.** Q1, Q2, Q3, Q6, Q9. WordPress admin. GTM publish rights on `GTM-NZSMS9RB`.
Google Ads write on `8735782888`. WhatConverts console access.

| # | System | Resource ID | Current | Proposed | Reason |
| --- | --- | --- | --- | --- | --- |
| 1.1 | Google Ads | `7717433754` Whatconverts Calls | primary, **in Conversions**, never received | **Secondary, excluded from Conversions** until dedupe proven | Prevents double-counting call-asset calls already counted by `6617381255` (§7) |
| 1.2 | Google Ads | `7717433751` Whatconverts Form | primary, **in Conversions**, never received | **Secondary, excluded from Conversions** until overlap with `6886101052` is checked | Same risk on the form path |
| 1.3 | Google Ads | `6886103719` Phone Call Leads | ENABLED, primary, in Conversions, 0 since 2026-02-28 | **Excluded from Conversions; kept for history** | Structurally unable to fire; inflates nothing but misleads everyone |
| 1.4 | Google Ads | `6617381255` Calls from Ads | primary, in Conversions, 60 s | **No change** | The only working call signal |
| 1.5 | Google Ads | `6548857156` GSA Submit Lead Form | ENABLED, excluded, still receiving | **Leave excluded**; document as legacy | Removing it is destructive and unnecessary |
| 1.6 | GTM `GTM-NZSMS9RB` | `__awcc` tag | `phoneConversionNumber: "(214) 301-3385"` | **Remove the tag** | Redundant under WhatConverts, and re-pointing it creates a DOM race (§6) |
| 1.7 | WordPress | Pages A and B primary CTA | `href="tel:%91phone%93"` | Valid `tel:` href for the confirmed page number | Broken main CTA on 100%-mobile traffic |
| 1.8 | WhatConverts | Google Ads integration, Phone Calls feed | Sending all calls | **Exclude the `Google Call Extension` source** (option D1) | Vendor-side dedupe, the cleanest place |
| 1.9 | Gravity Forms | `gform_2` (A/B), `gform_1`+`gform_2` (offerdfw) | `gform_field_values` empty; no click-ID fields | Add hidden `gclid`, `gbraid`, `wbraid`, `utm_*`, landing page, consent | `CLAUDE.md` requires click IDs preserved into the CRM |

**Explicitly NOT in this batch.** No phone number is changed anywhere — not on the site, not in
call asset `89872541418`, not in WhatConverts. No tag belonging to `AW-11240766632` or
`GTM-54Q4TVXF` is touched. WhatConverts is not disconnected and `Conversion Updates` is not
enabled. `6886103719` is **not** deleted.

**Risk.** Medium. 1.1–1.3 change the Conversions column immediately and will make reported
conversions **drop** — that is the point. 1.6 and 1.7 touch a live site. 1.9 touches a live form.

**Rollback.** 1.1–1.3: re-set `primary_for_goal` and `include_in_conversions_metric` to the values
recorded in §2.1 — all current values are captured above. 1.6: GTM keeps full version history;
republish the prior version. 1.7/1.9: restore the previous href string and remove added fields;
Gravity Forms keeps revisions.

**Verification.** Fresh GAQL read-back of all five conversion actions against this document's
recorded values · load both pages and confirm one valid `tel:` href and no `%91phone%93` ·
confirm `__awcc` no longer fires in the network log · load a page with test URL parameters and
read the hidden field values **in the DOM only** · reconcile one week of WhatConverts calls
against Google Ads. **No test call, no form submission, no test lead — ever.**

**Estimated impact.** Reported conversions fall to the genuinely-countable set, then rise as the
call path is restored. Eliminates a duplicate-counting event that would otherwise corrupt every
downstream bidding decision.

---

### Batch 2 — Campaign waste reduction and targeting corrections

**Objective.** Stop paying for queries and time slots that produce nothing, and restore inventory
the account is currently refusing.

**Dependencies.** Batch 1 in place (so results are measurable). Q7, Q8.

| # | System | Resource ID | Current | Proposed | Reason |
| --- | --- | --- | --- | --- | --- |
| 2.1 | Google Ads | criterion `40961223` | `cost` PHRASE negative | **Remove** | Blocks a protected buyer-intent term; GM policy |
| 2.2 | Google Ads | `23836346`, `301794223657`, `23423966`, `11884132004` | Broad negatives blocking core repair queries | **Remove** | They block "sprinkler head replacement", "sprinkler box repair" |
| 2.3 | Google Ads | campaign `20315156610` | — | **Add exact negatives**: lawn sense dallas/plano/texas, lee engineering irrigation, lee engineering arlington texas, garden springs irrigation, h20rx, rockwall irrigation | $332.49 / 0 conversions, measured |
| 2.4 | Google Ads | criteria `30000`, `30002` | DESKTOP and TABLET at **−100%** | **Restore to 0% modifier** | 24.9% of IS lost to rank in a budget-capped account |
| 2.5 | Google Ads | ad schedule `303280`–`363280` | 08:00–20:00 **Eastern** = 07:00–19:00 Central | Shift to the confirmed Dallas hours | Currently loses the 19:00–20:00 Central hour |
| 2.6 | Google Ads | campaign `20315156610` | Search Partners **off** | **No change** — confirm it stays off | GM default; it delivered $5.79 / 0 conv |
| 2.7 | Google Ads | 6 IP_BLOCK criteria | Present, unreviewed | **Review only, no change yet** | 14.6% invalid clicks warrants a look |

**Explicitly NOT in this batch.** No bid, budget, or bidding-strategy change. No geo change —
targeting is working correctly (F21). Monday spend is flagged but **not** cut, because with
tracking broken its zero-conversion record is not trustworthy evidence.

**Risk.** Low–Medium. 2.4 will increase cost in a budget-limited account.

**Rollback.** Re-add removed negatives (IDs recorded); remove added ones; re-apply −100% device
modifiers; restore the schedule. All values are captured in §2.2.

**Verification.** Fresh GAQL read-back of `campaign_criterion` · confirm removed negatives are
gone and added ones present · watch device segmentation for two weeks.

**Estimated impact.** Directly recovers the measured $332.49 / 90 days of zero-return spend, and
opens desktop/tablet inventory. Numeric CPL forecast withheld — see §14.

---

### Batch 3 — Keywords, ads, assets, and landing-page alignment

**Objective.** One canonical landing page, ads that can actually be tested, and assets that point
at the service being sold.

**Dependencies.** **Q3 is a hard blocker.** Also Q4, Q5.

| # | System | Resource ID | Current | Proposed | Reason |
| --- | --- | --- | --- | --- | --- |
| 3.1 | WordPress / Nelio | experiment `3619` | 50/50 A↔B, `participationChance 100` | **End or pause**, after exporting its report | Randomises traffic against the ad's own final URL (I3) |
| 3.2 | Google Ads | ads `714659486058`, `797294303667`, `797325463324` | Final URLs split across A and B | Point all three at the **confirmed canonical page** | Consistency once 3.1 lands |
| 3.3 | Google Ads | same three RSAs | **All 15 headlines and 4 descriptions pinned** | Unpin all but one theme headline | No combination testing has ever been possible |
| 3.4 | Google Ads | 3 ad groups | 1 enabled RSA each | **Add a second RSA per ad group**, created **paused** | GM standard |
| 3.5 | Google Ads | 27/22/22 ad-group sitelinks | 4× Irrigation Winterization, 4× duplicate Sprinkler Repair, 2 URL patterns | Cut to **6–8** repair-intent sitelinks, one URL pattern | Winterization is an **excluded** service |
| 3.6 | Google Ads | promotion assets `89872396866`, `89872442988` | Point at `offerdfw.*` | Align with the canonical page | Campaign currently straddles two landing-page systems |
| 3.7 | NitroPack | site config | Defers measurement scripts until interaction | Exclude GTM, gtag, and the WhatConverts script from the delay list | Behaviour on mobile is still unverified (U-H) |

**Explicitly NOT in this batch.** No new keywords are added — existing themes are sound and
budget is the binding constraint, not coverage. No page is deleted. No change to the call asset.

**Risk.** Medium. 3.1 discards in-flight experiment data. 3.7 will lower PageSpeed scores.

**Rollback.** Nelio retains experiment state and can resume. Final URLs and pinning are recorded
above. New RSAs are created paused and can simply be removed. Re-add scripts to NitroPack's delay
list.

**Verification.** Load both URLs repeatedly with cleared cookies and confirm no cross-redirect ·
GAQL read-back of ad final URLs and asset links · confirm `gtm.js` fires with **no interaction**
· re-test on a real mobile device.

---

### Batch 4 — Bidding, offline conversions, revenue, and profit

**Objective.** Optimise toward profit instead of clicks.

**Dependencies.** **Batches 1–3 complete, plus 30 days of clean data and at least ~30 conversions.**
Q10 and Q11.

| # | System | Current | Proposed | Reason |
| --- | --- | --- | --- | --- |
| 4.1 | Google Ads `20315156610` | TARGET_SPEND (Maximize Clicks), $18 CPC ceiling | Move to a conversion-based strategy | Maximize Clicks optimises for the wrong outcome — but only once the signal is real |
| 4.2 | Google Ads budget `12723712793` | $32.50/day, 16.7%→27.7% IS lost to budget | Re-evaluate against true CPL | Account is budget-limited and worsening (I9) |
| 4.3 | WhatConverts | `Not Updating Existing Conversions` | Enable retroactive updates | Required for sold-job revenue and gross profit |
| 4.4 | Data Manager API | Not implemented | Import qualified/closed-won outcomes | `CLAUDE.md` standard; legacy upload path only if the token is confirmed eligible |
| 4.5 | Reporting | None | Profit dashboard per §12 | Spend → leads → sales → gross profit |
| 4.6 | Google Ads `22379036365` | PMax PAUSED, $250/day | **Stay paused** | Would optimise against a broken signal at 8× budget |

**Explicitly NOT in this batch.** No bidding change before 30 clean conversions. PMax is not
enabled. No budget increase without a real CPL.

**Risk.** High if sequenced early — a bidding migration on bad data is worse than no migration.
Low if the gate is respected.

**Rollback.** Bidding strategy and budget values are recorded; both revert in one edit. Disable
Data Manager import.

**Verification.** 30-day conversion stability before and after · CPL and CPQL by strategy ·
reconcile imported outcomes against CRM sold jobs.

---

## 17A. Campaign Batches 2–4 — updated preview, 2026-08-11

Supersedes §17 Batches 2–4. **Preview only. Nothing implemented. No approval requested.**

### Batch 2 — Waste reduction and targeting

**Dependencies:** Batch 1A applied. **Gate: do not raise budget until tracking containment is in
place**, or the extra spend simply buys more unmeasured clicks.

| # | Resource | Current | Proposed | Reason | Risk | Rollback |
| --- | --- | --- | --- | --- | --- | --- |
| 2.1 | `campaignCriteria/20315156610~30000` DESKTOP | `bid_modifier` **0.0** (−100%) | **1.0** (0% adj.) | [USER] desktop enabled. 34–36% of IS lost to rank/budget | Medium — adds cost | Set back to 0.0 |
| 2.2 | `campaignCriteria/20315156610~30002` TABLET | 0.0 (−100%) | **no change** | [USER] tablet excluded | none | n/a |
| 2.3 | `campaignCriteria/20315156610~30001` MOBILE | unset | **no change** | Working | none | n/a |
| 2.4 | Ad schedule `303280`…`363280` | 08:00–20:00 ET, 7 days | **NO CHANGE** | Already equals 7 AM–7 PM CT | none | n/a |
| 2.5 | Budget `12723712793` | **$32.50/day** ≈ $988/mo | **$65.79/day** = $2,000 ÷ 30.4 | Uses the confirmed cap fully; **not** a cap increase. MTD IS lost to budget **34.44%** | Medium — doubles daily spend | Restore $32.50 |
| 2.6 | Negative `40961223` `cost` PHRASE | active | **Remove** | Over-broad; 12 specific off-service cost negatives already do the real work | Low | Re-add |
| 2.7 | Negative `101679803` `how much` PHRASE | active | **Remove** | Same over-blocking; blocks "how much to fix a sprinkler valve" | Low | Re-add |
| 2.8 | Negative `337388455191` `sprinkler valve replacement cost` EXACT | active | **Remove** | **Valve repair is explicitly in scope** [USER] | Low | Re-add |
| 2.9 | Negatives `23836346` `sprinkler heads`, `301794223657` `head replacement`, `23423966` `sprinkler box` (BROAD) | active | **Remove** | Block core repair queries; **sprinkler head repair is in scope** [USER] | Low | Re-add |
| 2.10 | Negative `11884132004` `just sprinklers` BROAD | active | **Change to EXACT / phrase** | Broad blocks any query with "just" + "sprinklers" | Low | Restore |
| 2.11 | Campaign `20315156610` | — | **Add EXACT negatives:** `lawn sense dallas`, `lawn sense plano`, `lawn sense texas`, `lee engineering irrigation`, `lee engineering arlington texas`, `garden springs irrigation`, `h20rx`, `rockwall irrigation` | **$332.49 / 0 conversions**, measured | Low | Remove |
| 2.12 | Campaign `20315156610` | — | **Add PHRASE negatives:** `albuquerque`, `sioux falls` | Out-of-market, measured | Low | Remove |
| 2.13 | Search Partners | off | **no change** | GM default | none | n/a |
| 2.14 | Location criteria (74) | 70 ZIPs, 3 cities, 1 airport, PRESENCE/PRESENCE | **NO CHANGE** | Owner-selected and authoritative [USER] | none | n/a |

**Keep** the 12 specific off-service cost negatives (`landscaping maintenance cost`,
`landscaping design cost`, `mulching cost near me`, `aeration cost near me`, `edging cost near me`,
`mowing cost near me`, `how much does it cost to install sprinklers`, `lawn maintenance cost near me`,
`cost to install automatic sprinkler system`, `landscaping installation cost`,
`overseeding cost near me`, `blowing cost near me`). They block genuinely out-of-scope cost
queries and are why the blanket `cost` negative is unnecessary.

**Evidence on `cost` [FRESH-API]:** across 2026-05-14→08-11, **zero** cost / price / quote /
estimate queries served. The search-term report cannot show what a negative blocked, so it
cannot prove harm directly — but it does prove the account receives **no price-intent traffic at
all**, while its live ads say "Get A Sprinkler Repair Quote", "Request Irrigation Quote" and
"Get Sprinkler Repair Estimate". The precise fix is to drop the two over-broad phrase negatives
and the one in-scope exact negative, and keep the twelve targeted ones.

### Batch 3 — Keywords, ads, assets, and landing-page alignment

**Dependencies:** canonical page live and QA-passed. **Blocks on Batch 1B steps 1–3.**

| # | Item | Current | Proposed |
| --- | --- | --- | --- |
| 3.1 | Ad-group structure | 3 serving groups: Sprinkler Repair Near Me `151125103616`, Irrigation Repair Near Me `190202910461`, Sprinkler System Repair `191996690566` | **Keep all three.** Themes are distinct and match the in-scope services |
| 3.2 | Match types | Phrase + Exact only | **No change.** Compliant. No Broad without separate approval |
| 3.3 | Keywords | 195 active | **Keep the six top performers.** Add EXACT `[sprinkler head repair]`, `[sprinkler head replacement]`, `[irrigation valve repair]`, `[sprinkler valve repair]` — all in scope and currently blocked by 2.8/2.9 |
| 3.4 | RSAs | **1 enabled per ad group; every headline and description pinned** | **2 per ad group**, created **PAUSED**. **Minimal pinning** |
| 3.5 | Pinning policy | 15/15 headlines, 4/4 descriptions pinned | **Pin at most one headline** to position 1 for the ad-group theme. Leave everything else unpinned |
| 3.6 | Ad copy | "10% OFF" in the offer path; unqualified "Same Day" | **Remove 10% OFF entirely.** Replace same-day with **"Same-Day Service May Be Available."** |
| 3.7 | Sitelinks | 27 / 22 / 22, incl. **4× Irrigation Winterization** | Cut to **6–8** repair-intent links from the **11 verified** service-area pages plus repair service pages. **Remove all winterization sitelinks** — excluded service |
| 3.8 | Callouts `89872309302/305/308/311` | "Get Free Online Quote", "Licensed & Insured", "Claim Your Discount", "Hassle-Free Service" | **Keep** Licensed & Insured (verified). **Remove "Claim Your Discount"** — tied to the expired promotion. Add **"Free Estimates"**, **"18-Point System Check"** |
| 3.9 | Structured snippet `383423268951` | Service catalog: Sprinkler Repair, Irrigation Repair, Leak Repair, Sprinkler System Repair, Valve Repair, System Inspection | **No change.** Fully in scope |
| 3.10 | Call asset `89872541418` | (214) 301-3385 → `6617381255` | **PRESERVE. Do not touch** |
| 3.11 | Promotion assets `89872396866`, `89872442988` | Target `offerdfw…`; **REMOVED** on the live campaign | **No live action.** Do not re-add. Retarget only if promotions resume |
| 3.12 | Images `AD_IMAGE` ×5, logo `143018472149` | On Sprinkler Repair Near Me only | Confirm current approved creative; extend to all three groups |
| 3.13 | Final URLs | Split across Page A and Page B | **All three → the canonical URL** (Batch 1B steps 4a–4c) |
| 3.14 | Campaign tracking templates | 3 campaigns carry a **wrong `utm_id`** | Correct each to its own campaign ID |

### Batch 4 — Qualified leads, revenue, and profit

**Dependencies:** Batches 1–3 complete · ≥ 2 weeks clean reconciliation · ≥ 30 conversions.

| # | Item | Proposed | Gate |
| --- | --- | --- | --- |
| 4.1 | WhatConverts qualification stages | Owner marks qualified / quotable. Spam, wrong numbers, job seekers, vendors, out-of-area **never** imported | [USER] policy |
| 4.2 | Offline conversion design | **Google Data Manager API** per `CLAUDE.md`. Legacy Ads upload only if the developer token is confirmed eligible | — |
| 4.3 | Dedupe key | WhatConverts **lead ID**. **Exclude every Google Call Extension-source call** | Must reconcile 1:1 |
| 4.4 | Promote `7717433754` → primary | For **website/organic** qualified calls only; `6617381255` stays primary for call-asset calls | After clean test data |
| 4.5 | Promote `7717433751` → primary; demote `6886101052` → secondary | `6886101052` **retained permanently** for history | **Only** after the form import proves out [USER] |
| 4.6 | Conversion Updates | Enable in WhatConverts | **Only after successful testing** [USER] |
| 4.7 | Revenue / sales value | Flow WhatConverts opportunity value into Ads | After 4.6 |
| 4.8 | Enhanced conversions | Already `enhanced_conversions_for_leads_enabled: true`, terms accepted **[FRESH-API]** | Verify it is actually receiving |
| 4.9 | Booked-estimate + completed-job reporting | Build against $180 max cost per booked estimate and $240–$300 job revenue | Needs close rate and booked-job rate |
| 4.10 | Bidding migration | Maximize Clicks → conversion-based | **Blocked** until ≥ 30 clean conversions |
| 4.11 | Value/profit bidding | **BLOCKED** | Gross margin, close rate, and booked-job rate are **not available** and must not be invented [USER] |
| 4.12 | PMax `22379036365` | **Stays paused** | [USER] |

**Required business inputs before 4.9–4.11:** gross margin %, lead-to-booked-estimate rate,
booked-estimate-to-completed-job rate, and average completed-job revenue.

---

## 18. Boundary statement

Nothing in Google Ads, WhatConverts, GTM, WordPress, Gravity Forms, Nelio, NitroPack, DNS, or any
other external system was created, modified, enabled, disabled, connected, disconnected, or
deleted. All Google Ads queries were `SELECT`-only against child `8735782888`; the manager account
was never queried as a target. No phone call was placed, no form submitted, no chat opened, no
test lead generated, and no call recording played. No credential value was read, printed, or
logged. `.env` was not modified. Nothing was committed, pushed, published, deployed, or uploaded.

**One consolidated approval is requested: Batch 1 only.**
