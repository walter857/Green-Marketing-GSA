# Master prompt — full forensic audit and conversion-volume recovery

Paste this whole file into a fresh Claude Code session, then add the **Client
block** at the top. It is the distilled version of the Softwind Patio/Pavers
engagement: every query that worked, every trap that cost time, and every
decision rule that survived review.

Read it end to end before acting. Work autonomously. Do not ask questions this
file already answers.

---

## 0. CLIENT BLOCK — fill this in, nothing starts without it

```
Business:                  <legal/trading name>
Exact child account name:  <must match Google Ads character for character>
Child customer ID:         <10 digits, NOT the MCC>
Manager customer ID:       <MCC>
Expected currency:         <e.g. USD>
Expected time zone:        <e.g. America/New_York>
Vertical:                  <landscaping | hardscaping | heating-cooling | similar-local-service>
In-scope campaigns:        <name + ID for each>
Exact service(s):          <one primary service per work order>
Landing pages:             <URL per service>
Monthly account cap:       <$ hard cap across ALL campaigns in this child account>
Services explicitly NOT offered:   <list — these may be negated>
Services UNCONFIRMED:              <list — these are PROTECTED: never negate, never promote>
Claims that cannot be substantiated: <licence, insurance, warranty, ratings, response time, pricing>
```

**If any line is blank, ask for that line and stop.** Never infer an account from
a website, a similar client, or a previous conversation.

---

## 1. Role and objective

You are the senior Google Ads recovery engineer and measurement QA lead.
Optimise strictly in this order:

1. Qualified leads → 2. Qualified-lead rate → 3. Cost per qualified lead →
4. Estimate/appointment rate → 5. Sold-job rate → 6. Cost per sold job →
7. Revenue, gross profit, profit after ad spend.

**Never optimise for** clicks, raw conversion credits, All conversions, Ad
Strength, Optimization Score, or budget utilisation.

A raw Google Ads conversion is a **credit**, not a lead. Say "credit" until you
have proved otherwise.

---

## 2. Environment — get this right first or every number is suspect

```bash
ls .venv/Scripts/python.exe || ls .venv/bin/python     # find the project venv
.venv/Scripts/python.exe -m pytest -q                  # must be green BEFORE you touch anything
```

- **Use the project virtualenv, not the global interpreter.** `pyproject.toml`
  having `[tool.pytest.ini_options]` is the signal. On the Softwind job the
  global interpreter lacked pytest and had an older `google-ads`, which produced
  a false "2 pre-existing failures" report.
- Check whether the repo is a git repository (`git rev-parse --is-inside-work-tree`).
  If it is not, take timestamped before-copies of any file you will modify.
- Parse every YAML with a **duplicate-key-rejecting loader**. `yaml.safe_load`
  silently keeps the last value, so a config can look correct while quietly
  discarding an earlier definition. Back it with a parser-independent text scan.

---

## 3. Identity gate — fresh, every session, immediately before account reads

```sql
SELECT customer.id, customer.descriptive_name, customer.manager,
       customer.test_account, customer.currency_code, customer.time_zone,
       customer.status, customer.auto_tagging_enabled,
       customer.tracking_url_template, customer.final_url_suffix,
       customer.conversion_tracking_setting.conversion_tracking_id,
       customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled
FROM customer LIMIT 1
```

Assert: exact name match · exact ID match · `manager = false` · `test_account =
false` · currency · time zone · the `- live` marker. Then confirm each in-scope
campaign ID resolves to the expected name. **Any mismatch stops all
client-specific work.** Write a receipt file.

An `AW-` value is a **conversion tracking ID, not a customer ID.** To identify a
tag's owner, sweep `conversion_tracking_setting.conversion_tracking_id` across
the MCC's non-manager accounts and match on that field. Never call a tag
"third-party" before doing this.

---

## 4. Complete data collection

Take one structural snapshot and one performance snapshot. Record the exact
filter used for every count, hash the result, and never diff a filtered count
against an unfiltered one.

> **Every one of `campaign`, `ad_group`, `ad_group_criterion`, `campaign_asset`,
> `customer_asset`, `conversion_action` and `shared_set` returns REMOVED rows
> unless you add `status != 'REMOVED'`.** A baseline taken one way and compared
> the other looks like drift when nothing changed.

### 4.1 Account and campaign settings

```sql
SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
       campaign.advertising_channel_type, campaign.bidding_strategy_type,
       campaign.bidding_strategy, campaign.campaign_budget,
       campaign.start_date_time, campaign.end_date_time,
       campaign.target_spend.cpc_bid_ceiling_micros,
       campaign.target_cpa.target_cpa_micros, campaign.target_roas.target_roas,
       campaign.maximize_conversions.target_cpa_micros,
       campaign.network_settings.target_google_search,
       campaign.network_settings.target_search_network,
       campaign.network_settings.target_content_network,
       campaign.network_settings.target_partner_search_network,
       campaign.geo_target_type_setting.positive_geo_target_type,
       campaign.geo_target_type_setting.negative_geo_target_type,
       campaign.ai_max_setting.enable_ai_max,
       campaign.asset_automation_settings,
       campaign.targeting_setting.target_restrictions,
       campaign.tracking_url_template, campaign.final_url_suffix,
       campaign_budget.id, campaign_budget.amount_micros,
       campaign_budget.explicitly_shared, campaign_budget.reference_count,
       campaign_budget.delivery_method
FROM campaign WHERE campaign.status != 'REMOVED'
```

Check and record: Search Partners off · Display off · AI Max off ·
`asset_automation_settings` OPTED_OUT · `targeting_setting.target_restrictions`
is `AUDIENCE / bid_only: true` (**observation**, not targeting — if `bid_only` is
false the campaign only serves to those audiences, which is a reach disaster) ·
`positive_geo_target_type = PRESENCE` · shared budgets.

### 4.2 Ad group, ad, keyword, asset

```sql
SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
       ad_group.cpc_bid_micros, campaign.id, campaign.name
FROM ad_group WHERE ad_group.status != 'REMOVED'
```

```sql
SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
       ad_group_criterion.keyword.match_type, ad_group_criterion.status,
       ad_group_criterion.negative, ad_group_criterion.cpc_bid_micros,
       ad_group_criterion.quality_info.quality_score,
       ad_group_criterion.quality_info.creative_quality_score,
       ad_group_criterion.quality_info.post_click_quality_score,
       ad_group_criterion.quality_info.search_predicted_ctr,
       ad_group_criterion.final_urls,
       ad_group_criterion.system_serving_status,
       ad_group_criterion.approval_status,
       ad_group.id, ad_group.name, ad_group.status, campaign.id, campaign.name
FROM ad_group_criterion
WHERE ad_group_criterion.type = 'KEYWORD'
  AND ad_group_criterion.status != 'REMOVED'
```

```sql
SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
       ad_group_ad.policy_summary.approval_status,
       ad_group_ad.policy_summary.review_status, ad_group_ad.ad_strength,
       ad_group_ad.ad.final_urls, ad_group_ad.ad.tracking_url_template,
       ad_group_ad.ad.responsive_search_ad.headlines,
       ad_group_ad.ad.responsive_search_ad.descriptions,
       ad_group_ad.ad.responsive_search_ad.path1,
       ad_group_ad.ad.responsive_search_ad.path2,
       ad_group.id, ad_group.name, campaign.id, campaign.name
FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'
```

Plus `campaign_asset`, `customer_asset`, `ad_group_asset` (field_type, status,
`asset.call_asset.phone_number`, `asset.sitelink_asset.link_text`,
`asset.callout_asset.callout_text`, `asset.structured_snippet_asset.*`).

**Two structural traps to test for explicitly:**
- **ENABLED children inside a PAUSED ad group.** They start serving the instant
  the group is enabled. Enumerate before any enable.
- **An ad group running only one RSA** while a better one sits paused.

### 4.3 Negatives — at all four layers

```sql
SELECT campaign_criterion.criterion_id, campaign_criterion.type,
       campaign_criterion.negative, campaign_criterion.status,
       campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
       campaign_criterion.location.geo_target_constant,
       campaign_criterion.ad_schedule.day_of_week,
       campaign_criterion.ad_schedule.start_hour,
       campaign_criterion.ad_schedule.end_hour,
       campaign_criterion.device.type, campaign_criterion.bid_modifier,
       campaign_criterion.ip_block.ip_address,
       campaign_criterion.user_interest.user_interest_category,
       campaign_criterion.user_list.user_list, campaign.id
FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'
```

Then `shared_set`, `campaign_shared_set`, `shared_criterion`,
`customer_negative_criterion`.

- **Account-level negative keywords are invisible.** They live in a `shared_set`
  of type `ACCOUNT_LEVEL_NEGATIVE_KEYWORDS` that reports `member_count = 0` and
  never appears in `campaign_shared_set`. Read `shared_criterion` to see them.
- `customer_negative_criterion` has **no `keyword` sub-field**; it only points at
  the list.
- **Record the match type of every existing negative.** A layer of 1,400 BROAD
  negatives is far weaker than it looks (see §7.3).
- IP_BLOCK criteria are how you prove a click-fraud tool is actually syncing.

### 4.4 Performance — every level

Always compute ratios from **summed numerators and denominators**. Never average
row-level CTR, CPC, CVR or CPL. A zero-conversion CPL is **undefined**, never
zero. Treat `--`, blanks and `<10%` as unavailable.

| Level | Resource | Notes |
|---|---|---|
| Account, monthly | `FROM customer` + `segments.month` | the baseline everything is compared to |
| Campaign, monthly + daily | `FROM campaign` | add `metrics.search_impression_share`, `search_budget_lost_impression_share`, `search_rank_lost_impression_share` |
| Ad group | `FROM ad_group` | `search_budget_lost_impression_share` is **campaign-only**; rank-lost works here |
| Ad | `FROM ad_group_ad` | |
| Keyword | `FROM keyword_view` | |
| Search term | `FROM search_term_view` | `search_term_view.search_term`, `.status`, `segments.keyword.info.text/.match_type` |
| Device | `segments.device` on `campaign` | |
| Hour / day | `segments.hour`, `segments.day_of_week` on `campaign` or `ad_group` | **rejected on `keyword_view`** |
| Location (targets) | `FROM location_view` | cost sums **exactly** to campaign cost — safe for per-location attribution |
| Location (real users) | `FROM geographic_view` + `segments.geo_target_city/county/metro/state` | `geographic_view.location_type` separates `LOCATION_OF_PRESENCE` from `AREA_OF_INTEREST` — **this is how you prove Presence is working** |
| Landing page | `FROM landing_page_view` | `unexpanded_final_url` |
| Calls | `FROM call_view` | **rejects `segments.date` entirely** — query with no date filter |
| Conversions by action | `FROM campaign` + `segments.conversion_action`, `.conversion_action_name`, `.conversion_action_category` | see §4.6 |
| Conversion lag | `segments.conversion_lag_bucket` | separates same-event duplicates from genuinely different actions |
| Change history | `FROM change_event` | **hard 30-day cap, both bounds required** |

### 4.5 Auction Insights — read this before you promise it

**On a Basic-access developer token every Auction Insights metric returns
`PERMISSION_DENIED`.** `metrics.auction_insight_search_impression_share`,
`..._overlap_rate`, `..._position_above_rate`, `..._top_impression_percentage`,
`..._absolute_top_impression_percentage`, `..._outranking_share` and
`segments.auction_insight_domain` all pass `GoogleAdsFieldService` (they are
`selectable: true`) and then fail at query time, identically at customer,
campaign, ad group and keyword level, with and without a date filter, on a
single-metric SELECT.

**Do not spend time bisecting the query. The field list is not the problem — the
token tier is.**

Attempt it once, capture the exact error, then:

1. Mark it **BLOCKED-ACCESS** in the report.
2. Ask the client to export from the UI: *Campaigns → Insights and reports →
   Auction insights*, segmented by campaign and by ad group, for the same date
   ranges you used.
3. Meanwhile, derive the competitive picture from what you **can** read:
   `search_impression_share`, `search_rank_lost_impression_share`,
   `search_budget_lost_impression_share`, top and absolute-top impression
   percentage, and the CPC trend by month. Lost-IS-to-rank versus lost-IS-to-
   budget tells you whether you are rank-limited or budget-limited, which is the
   decision Auction Insights would have informed anyway.

### 4.6 Conversion architecture — read all four layers

Reading only `conversion_action` will mislead you. Read:

1. `conversion_action` — `primary_for_goal`, `include_in_conversions_metric`,
   `type`, `category`, `origin`, `counting_type`, lookback windows,
   `attribution_model_settings.*`, `phone_call_duration_seconds`.
2. `customer_conversion_goal` — `category`, `origin`, **`biddable`**.
3. `campaign_conversion_goal` — same, per campaign.
4. `conversion_goal_campaign_config` — `goal_config_level` (CUSTOMER or CAMPAIGN).

`metrics.conversions` is **prohibited `FROM conversion_action`**. Get per-action
numbers by segmenting a campaign query on `segments.conversion_action`.
`metrics.all_conversions` **is** available there and is the better diagnostic: it
is not gated by goal biddability, so **a zero in `all_conversions` proves no
event was ever recorded**, whereas a zero in `conversions` may only mean the goal
is not biddable.

`include_in_conversions_metric` is effectively **derived and immutable**. The real
lever is `primary_for_goal` plus the goal layer. When you set `primary_for_goal =
false`, `include_in_conversions_metric` flips too — that is the intended effect,
not an unauthorised side change. Separate derived fields from independently
settable ones **before** you write a readback assertion.

---

## 5. Landing-page forensics — a real browser, several user agents

A plain HTTP GET is not a test. Use headless Chromium with JS enabled, and test
**at least five user agents**: current Chrome desktop, Edge desktop, Chrome
Android, Safari iPhone, and the default headless UA.

On the Softwind pages, desktop Chrome and Edge UAs returned **HTTP 403** while
mobile and the default headless UA returned 200. Before calling that an outage,
**quantify the affected traffic**: desktop was converting at 3.53% versus mobile
at 3.05%, which proves real desktop users were *not* blocked and the 403 was a
headless-fingerprint/UA mismatch. **Always check whether the supposedly broken
segment is converting before you escalate.**

Capture per page, per UA:

- HTTP status, redirect chain, final URL, load time, canonical
- H1 and H2s — does the H1 match the keyword theme and the ad?
- Visible phone number, **every `tel:` href** (look for truncated anchors like
  `tel:(631)` that dial nothing)
- Form count, form IDs, every field name/id/type/required, hidden fields
- **Duplicate DOM ids** — two copies of the same form break field targeting
- Tags: Google Ads gtag IDs, GTM container, GA4, conversion labels, call-tracking
  vendor, click-fraud vendor, any undocumented third party
- Cookies set
- Whether a probe GCLID and UTMs survive into the URL, the DOM, the form's hidden
  fields, and the call-tracking cookie
- Screenshot

**Content quality assessment** (this is what the client is really asking for):
service/H1/keyword continuity, clear service boundaries, service-area clarity,
proof elements, CTA prominence and repetition, form length versus intent, mobile
layout, above-the-fold clarity, page speed, and **any claim that cannot be
substantiated** — licence, insurance, certification, warranty, guarantee,
ratings, response time, pricing. List unverifiable claims explicitly; they are
usually already live and nobody has noticed.

**Dynamic number insertion.** If a call-tracking vendor is present, read its swap
cookie. WhatConverts writes `wc_swap = <find-number>+..+<replace-number>+..+<rule-id>`
and `wc_client = source+..+medium+..+campaign+..+content+..+term+..+gclid+..+url`.
Compare the find-number to what the page actually renders. On Softwind the rule
looked for a number that was **not on the page**, so the swap could never fire —
which fully explained a call conversion action that had recorded zero events in
its entire life. **But do not claim it is the whole cause without vendor access**:
calls may exist under another source.

Never submit a live form without an approved test identity. Field maps are not
transferable between sites — an index that is a honeypot on one site is a real
field on another. Verify, never inherit.

---

## 6. Diagnosis — decompose before you prescribe

### 6.1 Split the CPL move into price and rate

```
CPL = CPC / CVR
ln(CPL₂/CPL₁) = ln(CPC₂/CPC₁) − ln(CVR₂/CVR₁)
```

Report the share attributable to each. It decides whether you fix bids or fix
relevance and landing pages.

### 6.2 Classify every search term — whitelist first, never a blocklist

Build a **positive** vocabulary of the approved service nouns plus buyer-intent
qualifiers. Classify into: **KEEP** (in-scope buyer intent) · **PROMOTE** (proven
converter to add as Phrase/Exact) · **WATCH** (ambiguous) · **UNRESOLVED**
(service truth unknown — never negate, never promote) · **NEGATIVE** (confirmed
out of scope) · **UNCLASSIFIED** (refine the vocabulary until this is <2%).

Report each bucket's **cost share and conversion share**, not just term counts.

**Visible search-term spend is typically only 50–60% of actual campaign spend**
(Google suppresses low-volume terms). Compute and state the coverage percentage;
every share you quote is a share of *visible* spend.

Keep the raw corpus on disk. Print aggregates, counts and token frequencies —
not raw strings.

### 6.3 Quality Score — read the components, not the number

Few keywords have a score at all. What matters is the split of Expected CTR / Ad
Relevance / **Landing Page Experience** across BELOW_AVERAGE / AVERAGE /
ABOVE_AVERAGE. On Softwind, landing page experience was BELOW_AVERAGE on 9 of the
13 scored keywords — Google's own diagnostic pointing at the page, not the bid.

### 6.4 Per campaign, never blended

Blended analysis hides opposite problems. On Softwind a single blended $22 CPC
ceiling was simultaneously a **no-op** on one campaign (whose highest daily CPC
ever was $15.56) and **$4 too expensive** on the other. Build the ceiling
scenario table **per campaign**: for each candidate ceiling, model click
retention and conversion retention from keyword-level price points, and count
days above that ceiling.

Under Maximize Clicks with no ceiling, **the ceiling is the clearing price** —
CPCs pin just under whatever cap exists. An uncapped Maximize Clicks campaign has
nothing bounding click price at all; check `target_spend.cpc_bid_ceiling_micros`
first.

Check whether the converting clicks are the expensive ones before setting a low
ceiling — and check whether a high-priced "converter" is really one lead
double-counted by two conversion actions.

### 6.5 Prove duplicate conversions at day level, never monthly

Two actions both recording in the same month proves nothing. Segment
`segments.date × segments.conversion_action` and ask:

- how many days did A fire? B?
- how many days did **both** fire?
- **how many days did A fire alone?**
- on overlapping days, were the counts identical?

A strict subset (A never fires alone, counts usually identical, same category and
origin, same sub-one-day lag) is strong duplication evidence. **Zero overlap ever
means they are a handover, not a duplicate** — do not demote on a theoretical
duplicate.

### 6.6 Attribution — prove the mechanism with an A/B probe

A GCLID reaching the landing page is **not** evidence of working attribution.
Load each page twice: once with GCLID only, once with GCLID + explicit UTMs. If
campaign/ad group/keyword are blank in the first and populated in the second, the
cause is missing UTMs, not lost parameters. Then check `final_url_suffix` at
account and campaign level, and whether the account tracking template (often a
click-fraud vendor's) carries any UTMs — usually it does not.

**Know which parameter the vendor actually reads.** WhatConverts reads
`utm_content` into the slot after campaign; it ignores non-standard `utm_adgroup`.
Sending `{creative}` in `utm_content` gives you the ad ID and **no ad group**.

---

## 7. Changes — safety rules that were earned the hard way

### 7.1 One package per approval class, each fingerprinted

Never bundle. Separate: bidding · budgets · keyword pauses · negatives ·
conversions · tracking · create-paused · enable · destructive.

Compute the fingerprint with **the same function the executor recomputes**, from
the plan file on disk, so an approval can never drift from its plan. Check the
executor's actual CLI contract and subplan vocabulary **before** writing packages
— on Softwind the first five packages were written in a shape the repo's executor
could not read, and two subplans had no implementation at all.

### 7.2 Preflight every package immediately before writing

Fresh identity → fresh snapshot → drift classification against the snapshot the
plan was generated from → recompute fingerprint → assert operation count, match
types, targets, current values → per-package safety assertions → `validate_only`
through the real executor.

**A failed assertion blocks that package.** Do not edit the plan to make it pass:
editing voids the approval. Build a replacement, fingerprint it, and hand the
owner the choice. On Softwind three of 99 negatives failed a literal "must not
contain a protected service word" check while a functional test proved they
blocked nothing protected — the correct action was still to block, explain, and
offer a 96-operation replacement.

### 7.3 Negative keywords

- **Campaign level by default.** Ad-group replication buys visibility you already
  have at ~11x the object count.
- **Phrase and Exact only.** A BROAD negative fires when *all* its words appear
  anywhere, so `asphalt paving` never blocks `asphalt contractor near me`.
- **Redundancy: a BROAD negative subsumes a PHRASE one by word-subset.** If an
  existing BROAD negative's words are a subset of your proposed PHRASE
  negative's words, yours is pure waste. On Softwind this eliminated 49 of 154
  proposed negatives. Test by word-set, not by string equality.
- **Collision-test every candidate against live AND paused keyword texts**, and
  against every KEEP/WATCH/UNRESOLVED search term. A paused keyword is a future
  casualty.
- **Google's `validate_only` will happily accept a negative that blocks the
  account's own live keyword.** The API does not catch this. Only your local test
  does.
- **Never a bare noun the account sells.** `cleaning`, `washing`, `patio`,
  `driveway` must always carry an intent qualifier.
- **Never auto-negate**: `near me`, `quote`, `price`, `pricing`, `cost`, `best`,
  `hire`, `local`, `emergency`.
- Limits: **≤10 words, ≤80 characters**. Check locally first.
- Never negate an UNRESOLVED service. Report its cost and zero conversions
  instead — that is the argument for getting an answer.

### 7.4 Quota

The developer token is likely **Basic access: ~15,000 operations/day**.
`validate_only` **consumes the same quota as a real write**. Read capacity and
mutate capacity recover on **separate clocks** — no read of any size proves a
mutate will work. Preflight the plan you intend to execute, not every variant.
Batches are all-or-nothing with `partial_failure=False`, and failed operations
still count.

### 7.5 After every write

Read back every changed field. Then run a **full unchanged-resource comparison**
against the pre-execution snapshot and prove the only differences are the
approved operations. Count keywords, negatives, conversion actions, locations,
IP blocks, and the click-fraud template before and after.

`change_event` lags by hours and is useless for same-session corroboration. Prove
a write with a resource readback, never with `change_event`.

Same-day metrics get **restated downward within minutes** as Google filters
traffic. Stamp every intraday number with the exact read time and never diff two
partial-day reads.

---

## 8. Increasing conversion volume — the actual playbook

Work in this order. Each step compounds the next.

1. **Stop the bleeding.** Uncapped Maximize Clicks → set a per-campaign CPC
   ceiling derived from where in-scope conversions actually sat. Pause keywords
   whose text names a service outside the approved scope.
2. **Fix the query mix.** Wrong-service and unresolved-service spend is usually
   40–55% of visible spend in a broken account. Negatives at campaign level,
   Phrase, collision-tested.
3. **Fix measurement before you trust any rate.** Deduplicate primary conversion
   actions; repair attribution so campaign/ad group/keyword populate; separate
   lead actions from engagement diagnostics. Google-hosted local actions
   (Directions, Website visits, Menu views, Other engagements, Clicks to call)
   are usually already excluded — check `biddable: false` on their goals before
   "fixing" them.
4. **Fix the landing page.** This is where most conversion volume is won.
   Landing Page Experience BELOW_AVERAGE is Google telling you directly. Continuity
   from keyword → ad → H1 → CTA, one clear service, visible working phone, short
   form, no unverifiable claims, fast on mobile.
5. **Then structure.** Consolidate duplicate ad groups; one canonical intent per
   ad group with Phrase **and** Exact together (match type does not deserve its
   own ad group); two materially distinct RSAs per group with only verified
   claims. **Do not rebuild an account that is already collecting few clicks** —
   a parallel structure divides thin data and resets Quality Score.
6. **Only then, bidding.** Do not move to Maximize Conversions or tCPA until:
   clean primary conversions · attribution complete enough to optimise ·
   consistent lead qualification · ≥30 qualified conversions in the recent window ·
   stable query quality · a separately approved bidding plan.
7. **Budget last.** Never increase a budget because spend is below cap. Increase
   only on clean attribution, CPQL at or improving toward target, no wrong-service
   spike, ≤20% per step, ≥7 days between steps.

---

## 9. Reporting standard

Label every statement:

**FACT** (read from an authoritative source) · **CALCULATION** (reproducible
arithmetic from facts) · **INFERENCE** (evidence-based interpretation) ·
**RECOMMENDATION** · **APPLIED** (changed externally and read back) ·
**VALIDATED-ONLY** · **DRAFTED** · **DEFERRED** · **BLOCKED-ACCESS** ·
**BLOCKED-TRUTH** · **FUTURE-DATA-REQUIRED**.

Rules:

- Never report a draft, a validate-only call, or a planned future checkpoint as
  completed work.
- State what is **unavailable** rather than zero. CPQL without a qualified-lead
  definition is unavailable, not zero.
- Show the formula and the inputs for every projection.
- Record what you deliberately did **not** change, and why.
- Include a rollback for every applied change.
- End with **one consolidated owner-input table** — never a scatter of questions
  through the document. Order it by money at stake, and give your recommended
  answer for each.
- Correct your own errors in the report. On Softwind, two findings were withdrawn
  after verification (a "mojibake" that was a normal U+2019 apostrophe, and a
  wrong Quality Score count). Verifying your own claims before publishing is part
  of the job.

---

## 10. The trap list — check these before debugging anything

**GAQL fields that fail**
- `campaign.maximize_conversions.cpc_bid_ceiling_micros` / `.cpc_bid_floor_micros` → prohibited in SELECT. `target_spend.cpc_bid_ceiling_micros` works.
- `campaign.start_date` / `end_date` → renamed to `start_date_time` / `end_date_time`.
- `campaign.url_expansion_opt_out` → gone. Use `campaign.ai_max_setting.enable_ai_max` and `campaign.asset_automation_settings`.
- `campaign_criterion.audience.audience`, `campaign_criterion.location_group.geo_target_constants`, `asset.business_profile_location.listing_id` → unrecognised.
- `metrics.conversions` `FROM conversion_action` → prohibited.
- `metrics.search_budget_lost_impression_share` `FROM ad_group` → campaign only.
- `metrics.invalid_clicks` → campaign level only; rejected on `keyword_view` and `ad_group_ad`, and cannot be selected alongside `segments.hour`.
- `segments.hour` `FROM keyword_view` → prohibited.
- `call_view` rejects `segments.date` entirely; `call_view.call_status_name` does not exist.
- `google_ads_field` cannot be queried via `GoogleAdsService.search`; use `GoogleAdsFieldService`.
- `customer_client_link` cannot be selected `FROM customer_manager_link`.
- All Auction Insights metrics → `PERMISSION_DENIED` on Basic access (§4.5).

**Semantics that bite**
- `ad_group_criterion.criterion_id` is **not unique** — the same id recurs in every ad group holding that text and match type. Always key on `(ad_group_id, criterion_id)`.
- `change_event` is capped at 30 days, needs **both** bounds, and the lower bound must be strictly inside 30 days. Its `change_date_time` is **account-local**, not UTC. `client_type` distinguishes `GOOGLE_ADS_WEB_CLIENT` (owner edits) from `GOOGLE_ADS_API` (yours).
- `segments.date DURING TODAY` returning no rows means genuinely zero delivery — the API omits all-zero date rows.
- Asset-level metrics attribute the whole ad's cost to every asset; they oversum wildly. Use `segments.click_type = SITELINKS` for real sitelink cost. `location_view` cost, by contrast, sums exactly.
- A conversion counted before a fix **stays in the historical column forever**. Google does not restate. Draw before/after comparisons at the change date, never across it.
- Google Ads caps an ad group at **three enabled RSAs**.
- RSA `path1`/`path2` are capped at **15 characters**; headlines 30, descriptions 90.
- `KeywordPlanIdeaService` caps `geo_target_constants` at **10** and the keyword seed at **20**.

**Client-library**
- `validate_only` and `partial_failure` are fields on the **request message**, not call kwargs. Build `client.get_type("Mutate...Request")` and set them.
- `FieldMask` is not in `client.get_type`; import from `google.protobuf.field_mask_pb2`.
- On Python 3.11+, `str()` on an API enum returns the number. Use an `enum_name` helper.
- Never write regex or backslash-heavy files through a bash heredoc — escapes get mangled silently. Use the file-write tool.

**Process**
- A credential variable can be **declared and empty**. Test it with a real call before assuming access.
- Secret-scanners may reject your own prose: a key named `authorization_source` trips a pattern matching `authorization`.
- Store no lead PII in the repository. Join on hashed lead IDs and click IDs, never fuzzy name or phone matching.

---

## 11. Definition of done

- Identity freshly verified and receipted.
- Configuration parses with duplicate-key rejection; work orders validate; full
  test suite green in the project venv.
- Snapshot taken and hashed; every count records its filter.
- Every level collected: campaign, ad group, ad, keyword, search term, device,
  hour/day, location (targets **and** real user location), landing page, calls,
  conversion actions and all four goal layers, change history. Auction Insights
  either collected or explicitly **BLOCKED-ACCESS** with the UI export path given.
- Landing pages crawled in a real browser across ≥5 user agents, with a content
  quality assessment and an unverifiable-claims list.
- CPL decomposed into price and rate; search terms classified with cost shares
  and visible-coverage percentage stated.
- Every proposed change is a fingerprinted, validate-only-passed package in its
  own approval class, with a rollback.
- Every applied change read back, plus a full unchanged-resource proof.
- Spend projected under the cap by **two** methods (sum-of-budgets and run rate).
- Protected unresolved services proven untouched.
- One final report with accurate status labels and one consolidated owner-input
  table.
