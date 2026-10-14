# Apogee Lawns — implementation record

**Account:** Apogee Lawns LLC - Live · **8164626278** · similar-local-service
**Service:** Permanent Christmas light installation · **Last updated 2026-09-17**
**Scope approval:** CLOSED — approver **Walter**. Both repo validators exit 0.

---

## EXECUTED

### Google Ads conversion actions — 3 created, states corrected 2026-09-17

| ID | Name | Type / Category / Origin | State | Conversion ID + Label |
|---|---|---|---|---|
| **7772803337** | Lead \| Permanent Lights \| Form Submit \| Thank You | WEBPAGE / SUBMIT_LEAD_FORM / WEBSITE | **PRIMARY** | `AW-18453077620/KOL7CImirvocEPS8jt9E` |
| **7773013199** | Call \| Permanent Lights \| Ads \| 60s | AD_CALL / PHONE_CALL_LEAD / CALL_FROM_ADS | **PRIMARY** | none — correct for AD_CALL |
| **7773043879** | Call \| Permanent Lights \| Website \| 60s | WEBSITE_CALL / PHONE_CALL_LEAD / WEBSITE | **SECONDARY** | `AW-18453077620/lp3jCKf5vPocEPS8jt9E` |

Created by `APG-0916-CONV-A` (9BA1F4AE3CCA) and `APG-0916-CONV-A2` (D1CAB205DDDA).
The two Primary states were set manually by Walter; `APG-0917-CONV-G` (FEB175ADDEEA) is
therefore **SATISFIED_EXTERNALLY_BY_VERIFIED_MANUAL_STATE** and was never executed.

**`APG-0917-CONV-J` (C52D14071B08) EXECUTED 2026-09-17 — 1 mutation, 0 failures.**
All three had been promoted to Primary; 7773043879 was demoted back to Secondary with
`update_mask=['primary_for_goal']` only. All ten side-effect checks passed: name, status,
type, category, origin, counting, 30-day window, 60s duration, value 0.0 and ownership all
unchanged. `include_in_conversions_metric` correctly returned to false on that action.
Receipt: `receipts/2026-09-17-convj-receipt.json`.

### Google Ads campaign — CREATED PAUSED 2026-09-17

`APG-0917-CAMP-I` / `4022CBA7FD51` · **121 mutations · readback QA 0 failures**

| Resource | ID | Detail |
|---|---|---|
| Campaign | **24257151015** | `S \| Website Leads \| Permanent Christmas Lights \| Apogee Lawns \| $500 \| 09_2026` — **PAUSED** |
| Budget | **15884926233** | $16.44/day, STANDARD, not shared → $499.78 at x30.4 |
| Ad group 1 | **200347713516** | `AG \| Permanent Light Installation` — ENABLED inside a PAUSED campaign |
| Ad group 2 | **200347713556** | `AG \| Permanent Christmas Lights Exact` — ENABLED inside a PAUSED campaign |
| RSAs | **825023783007 / …010 / …013 / …016** | all REVIEW_IN_PROGRESS |
| Assets | 422487159850, 422487181204, 422571032091, 422571064683, 422571064692, 422571077787 (callouts) + 422487159856 (snippet) | 7 campaign asset links |

Keywords (5): `385217173659` phrase + `546844124143` exact *permanent christmas light
installation*; `1968954080156` phrase + `2261056242205` exact *permanent christmas lights
installer*; `306097636075` exact *permanent christmas lights*.

Criteria: **93 rows** — **14 locations**, **1 language** (`languageConstants/1000`), **75
negatives** (37 broad / 38 phrase) and **3 implicit device rows** (30000 Desktop, 30001
HighEndMobile, 30002 Tablet, Google's fixed global IDs). **0 ad-schedule criteria** (24/7 by
design). An earlier figure of 90 in this file summed only the first three categories and is
corrected here.

Final URL on every RSA: `https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/`
— currently HTTP 404. Walter explicitly accepted the temporary 404 for creation.

Settings verified: Maximize Clicks, **$8.00 CPC ceiling**, Google Search only, Search
Partners / Display / partner-search all OFF, campaign `keyword_match_type` UNSPECIFIED
(broad match off), `TEXT_ASSET_AUTOMATION` OPTED_OUT, PRESENCE targeting, Nebraska state
not targeted, Omaha absent, **0 call assets at CAMP-I time** — added later by CALL-Q.

Goals: `goal_config_level = CAMPAIGN`, no custom goal.
SUBMIT_LEAD_FORM/WEBSITE **biddable true**, PHONE_CALL_LEAD/CALL_FROM_ADS **biddable true**,
PHONE_CALL_LEAD/WEBSITE **biddable false**.

**Two API-forced deviations, both recorded:**
1. `ad_serving_optimization_status` omitted — the API rejects it: *"Ad rotation mode at
   campaign is deprecated."* The field cannot be set at all, so no approved setting is lost.
2. `contains_eu_political_advertising` is now a **required** field on campaign create. Set to
   `DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING`, determined by the campaign's own content:
   permanent Christmas light installation, 14 Nebraska geo targets, zero EU targeting.
   Reversible by campaign update if the owner disagrees.

The first attempt failed at the campaign stage after the budget was created. The retry
reused budget 15884926233 idempotently rather than creating a second one.
Receipts: `receipts/2026-09-17-campi-created.json`, `receipts/2026-09-17-campi-readback.json`.

### GTM — COMPLETE. All 10 objects built, workspace unpublished

`APG-0917-GTM-K` / `2871DD2A5227` · **Workspace Changes: 5**

| Object | ID | Detail |
|---|---|---|
| Workspace `Apogee \| PPC Tracking \| 2026-09` | **3** | isolated; Default Workspace (2) untouched |
| Folder `Google Ads \| Permanent Lights` | — | all four objects filed into it |
| Built-in `Page URL` | 2147481602 | enabled |
| Built-in `Page Hostname` | 2147481603 | enabled |
| Built-in `Page Path` | 2147481604 | enabled |
| Built-in `Referrer` | 2147481605 | enabled |
| Built-in `Event` | 2147481606 | enabled (GTM default) |
| Variable `DLV \| lead_id` | **4** | Data Layer Variable, key `lead_id`, Version 2, no default value |
| Trigger `TR \| Custom Event \| apg_permanent_lights_lead` | — | Custom Event, regex matching OFF, Some Custom Events |
| Tag `Google tag \| AW-18453077620 \| All Pages` | **6** | Google Tag, `AW-18453077620`, Initialization - All Pages |
| Tag `Google Ads \| Lead \| Permanent Lights Thank You` | **7** | Conversion ID `18453077620`, label `KOL7CImirvocEPS8jt9E`, Transaction ID `{{DLV \| lead_id}}` |

Trigger conditions, verified by readback:
`Page Hostname equals offer.apogeelawns.com` AND
`Page Path matches RegEx ^/thank-you/permanent-christmas-lights/?$`

GTM validated the conversion tag with *"Google tag found in this container"*.
Conversion Value and Currency Code left empty — no invented revenue.

**Deliberately absent at GTM-K time:** Calls-from-Website tag, website-call trigger,
calls-from-ads GTM tag, WhatConverts placeholder, standalone Conversion Linker, Custom HTML,
GA4 tag, second Google tag. The first two were added later by GTM-P on Walter's instruction;
the rest are still absent.

**Container versions created: 0. Published: 0. Submit: never used.**
Live container still reads *"Empty Container is Live — 0 tags, 0 triggers, 0 variables"*.
Version 1 "Empty Container" (09/16/2026) is the container's own initial version, not mine.

**Blocking dependency:** `apg_permanent_lights_lead` appears **0 times** on
offer.apogeelawns.com. The developer must implement the dataLayer push before Preview can
pass. The trigger was NOT weakened to manufacture a passing test.
Receipt: `receipts/2026-09-17-gtmk-receipt.json`.

### Google Ads call asset — EXECUTED 2026-09-17

`APG-0917-CALL-Q` / `E3214C210910` · **2 mutations · 33 readback checks · 0 real failures**

| Resource | ID / resource name | Detail |
|---|---|---|
| Call asset | **422649064971** | `US` · **402-526-5754** · `USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION` → `conversionActions/7773013199` |
| Campaign asset link | `24257151015~422649064971~CALL` | field_type **CALL** · status **ENABLED** |

Ad schedule on the asset, account Central Time: Mon 08:00–17:00, Tue 08:00–17:00,
Wed 08:00–17:00, Thu 08:00–17:00, Fri 08:00–17:00, **Sat 08:00–12:00**. Sunday absent.
Campaign ad-schedule criteria remain **0** — the campaign still runs 24/7 and only the call
asset is time-restricted.

**Phone number, settled by Walter and not reopened:** `402-526-5754` is the advertising,
landing-page and WhatConverts number. The forwarding destination does not appear in the asset,
the plan file or the mutation payload — asserted by test before the request was sent, and
again on readback. `APG-0917-CALL-N` (A29431412E96) proposed the forwarding destination and is
**REJECTED, SUPERSEDED_WRONG_PHONE**; my recommendation there is withdrawn.

Resource-level call conversion reporting was mandatory, not preferred:
`customer.call_reporting_setting.call_conversion_action` still points at
`conversionActions/179`, which does not exist. Account-level reporting would have sent every
ad call to a dead action. That stale pointer was **left untouched**, per instruction, and
readback confirms it is byte-identical before and after.

Invariants confirmed after execution: campaign **still PAUSED**, budget unchanged at
16,440,000 micros, 4 RSAs, 5 keywords, 3 conversion actions with **none created or promoted**,
7773043879 still SECONDARY, `PHONE_CALL_LEAD/WEBSITE` still non-biddable, 0 custom conversion
goals, 6 callout + 1 snippet links unchanged, campaign asset links now **8**, manager
3373711342 untouched. **Zero enables, zero budget changes, zero deletes.**

**One readback check failed and was run down to ground:** the assertion "90 campaign criteria
unchanged" observed **93**. The three extra rows are implicit DEVICE criteria 30000 Desktop,
30001 HighEndMobile and 30002 Tablet — Google's fixed global criterion IDs, identical in every
account, so nothing allocated them. The figure 90 was my own sum of the three categories
CAMP-I's readback happened to print (14 + 1 + 75) and was never a measured total; the device
rows were present all along and simply never enumerated. CALL-Q issued only
`AssetService.mutate_assets` and `CampaignAssetService.mutate_campaign_assets`, neither of
which can write `campaign_criterion`. **The expectation was wrong, not the account.** Corrected
above and in the receipt. `change_status` returned 0 rows for the window and corroborates
nothing either way.

Receipt: `receipts/2026-09-17-callq-receipt.json`.

### GTM delta — EXECUTED 2026-09-17, still unpublished

`APG-0917-GTM-P` / `B3C69A1E65C8` · **4 objects · Workspace Changes 5 → 7 · 0 versions · 0 publishes**

| # | Object | Op | Verified by readback |
|---|---|---|---|
| 1 | Variable `DLV \| lead_id` (id **4**) | update | Data Layer Variable · key `lead_id` · Version 2 · **Set Default Value ON, value empty string** |
| 2 | Trigger `TR \| Custom Event \| apg_permanent_lights_lead` (id **5**) | update | condition 3 **`DLV \| lead_id` matches RegEx `.+`** added; conditions 1 and 2 byte-identical |
| 3 | Trigger `TR \| Page View \| Permanent Lights LP` | create | Page View · Some Page Views · `Page Hostname equals offer.apogeelawns.com` · `Page Path matches RegEx ^/permanent-christmas-lights-lincoln-ne/?$` |
| 4 | Tag `Google Ads \| Call \| Permanent Lights Website` | create | **Google Ads Calls from Website Conversion** · replace **402-526-5754** · ID `18453077620` · label `lp3jCKf5vPocEPS8jt9E` · fires on trigger 3 |

All four filed in folder `Google Ads | Permanent Lights`. GTM validated the tag with
*"Google tag found in this container"*.

**GTM accepted the empty default value, so no forced deviation was needed** — the fallback
regex `^(?!undefined$).+` was not used and `.+` stands exactly as Walter specified. The
empty default is what makes `.+` deterministic: without it a missing `lead_id` stringifies
to `"undefined"`, which would satisfy `.+` and defeat the hardening.

**The `lead_id` gate is now mandatory.** Until the developer ships the dataLayer push, the
form conversion does not fire at all. That is the intended behaviour, not a regression.

Pending Changes breakdown read back as **0 Modified / 7 Added / 0 Deleted**. Every object
counts as "Added" because the workspace has never been versioned.

**Publication boundary held:** container versions created **0**, publishes **0**, Submit
never pressed, Default Workspace 2 untouched. Versions tab still reads *"Empty Container is
Live — 0 Tags, 0 Triggers, 0 Variables"*, with only Version 1 "Empty Container" (09/16/2026),
the container's own initial version.

**PUBLICATION GATE: BLOCKED.** WhatConverts number replacement is active and unrestricted on
offer.apogeelawns.com, so publishing the website-call tag would put two replacement systems
on the same unprotected DOM nodes. Walter must pick option A or option B in
`plans/APG-0917-GTM-P.yaml` before anything is published.

Google Ads invariants re-checked after the GTM work: 3 conversion actions, none duplicated;
7773043879 still SECONDARY and its `PHONE_CALL_LEAD/WEBSITE` goal still non-biddable;
campaign 24257151015 still PAUSED; 0 CALL assets. **0 failures.**
Receipt: `receipts/2026-09-17-gtmp-receipt.json`.

### Drive documents — corrected in place, IDs and version history preserved

- Strategy `1BDMXgZO_5byH3nCXw7XGp7YahRT1hklsqwHYlWHQWVM`
- Landing page `19MQ3J11WiUuFQZn9kCRih3sBh0BR5kp_wE_ctcxY8Ok`

Reviews section removed, AG2/AG3 replaced with the settled structure, 11 TBD strings
resolved, current-implementation-status sections added, image manifest added.
Verified zero occurrences of U+2013, U+2014, `DO NOT PUBLISH`, `APPENDIX`/`Appendix`/`appendix`,
`Read Google Reviews`, `Reviewer:`, `Dedicated PPC URL: TBD`.

### Approved PPC images

Folder `1WStO1DEzwcXRzqw9Ujo4edOeiYGCOkTj` · manifest `1cnGukevYU4jHAou7sGJZqfB6F9mTAfII`
5 unique client originals inspected, 4 approved, **8 derivatives**, 1 excluded.
**One privacy crop** removed two legible licence plates.

---

## PLANNED, AWAITING APPROVAL

**None.** Every approved plan is executed. The open items are the two decisions below plus
the developer and owner blockers.

### OPEN DECISION 1 — GTM publication gate

The website-call tag is built in workspace 3 and **must not be published** until Walter picks
option A or option B in `plans/APG-0917-GTM-P.yaml`. Nothing else in this record is waiting
on it.

### OPEN DECISION 2 — enabling campaign 24257151015

Enablement needs its own separate approval after readback QA, and the landing page must
return 200 first.

### Historical note on CALL-Q

`APG-0917-CALL-N` (A29431412E96) is **REJECTED — SUPERSEDED_WRONG_PHONE**. Walter ruled that
402-526-5754 is the advertising, landing-page and WhatConverts number and that the other
number on file is only the final forwarding destination, which must not appear in a Google
Ads call asset. CALL-N is bannered in place and retained as an audit record only. My earlier
recommendation to use the forwarding destination is withdrawn; the owner's decision stands
and is not reopened.

CALL-Q was validated then executed on 2026-09-17: live identity gate, live duplicate check,
44 pre-approval red-team assertions, both repo validators exit 0, and a live `validate_only`
dry run that accepted the exact payload and created nothing. See the EXECUTED section above.

This plan does not re-execute CAMP-I, CONV-J, GTM-K or GTM-P.

### Website-call conversion action 7773043879 — no Google Ads mutation exists

The blank **Phone numbers** row and the `REPLACE WITH VALUE` snippet in the Google Ads UI
are **normal for every WEBSITE_CALL action**, not an incomplete record. `conversion_action`
exposes 31 selectable fields in API v25 and the mutable proto carries **no phone-number
field of any kind** — the only phone-related field is `phone_call_duration_seconds`, already
60. The number to replace belongs to the page tag, so it is configured in `APG-0917-GTM-P`
and nowhere else.

### WhatConverts DNI — RESOLVED, no sign-in performed

Determined by fetching and decompressing `s.ksrndkehqnwntyxlhgto.com/174313.js?ver=7.1`
(59,555 bytes) unauthenticated.

`var keyword_tracking_list = [["233469","default","default","","","","0","0","0","","0","0"]];`

Index 9 (swap pages) is empty → **no page restriction, all pages swap**. Source and medium
are both `default` with exclusion flags 6/7/8 all `0` → the entry is pushed into
`active_keyword_list` **unconditionally, for every visitor**. Index 10 is `0` → `wc_dynamic_mode`
stays 0, so the pool holds **one** number, with no rotation.

**Verdict: WhatConverts is actively replacing, pool size 1.** offer.apogeelawns.com already
hard-codes 402-526-5754 (5 text occurrences, 2 `tel:` links, 1 E.164 link) — the same number
WhatConverts assigns — so the swap is visually a no-op while the mechanism is fully live.
`no-swap` opt-out markers on the paid page: **0**.

Consequence: publishing Google's Calls-from-Website tag would put two number-replacement
systems on the same unprotected DOM nodes, WhatConverts re-applying from a 10-second
`setInterval`. The tag is therefore **built in workspace 3 and NOT published**; see
`publication_gate` in `APG-0917-GTM-P` for the A/B decision Walter must make.

### Superseded, for the record

`APG-0917-CAMP-E` (F0C6FA2128A9) asserted "All three stay Secondary", which CONV-G made
false; `APG-0917-CAMP-H` (136E939A3206) corrected only that precondition and was itself
superseded by CAMP-I, which is EXECUTED.

### Superseded and void plans

| Plan | Fingerprint | Status |
|---|---|---|
| `APG-0916-CAMP-B` | 849EAED2873F | VOID |
| `APG-0916-CAMP-C` | 7BC3407302B2 | SUPERSEDED |
| `APG-0917-CAMP-E` | F0C6FA2128A9 | SUPERSEDED |
| `APG-0917-GTM-D` | FC0E0B156F60 | SUPERSEDED |
| `APG-0917-GTM-F` | DB9391A883A7 | SUPERSEDED by GTM-K |
| `APG-0917-GTM-K` | 2871DD2A5227 | **EXECUTED 2026-09-17** |
| `APG-0917-CONV-G` | FEB175ADDEEA | SATISFIED_EXTERNALLY — never execute |
| `APG-0917-CONV-J` | C52D14071B08 | **EXECUTED 2026-09-17** |
| `APG-0917-CAMP-H` | 136E939A3206 | SUPERSEDED — wrong host |
| `APG-0917-CAMP-I` | 4022CBA7FD51 | **EXECUTED 2026-09-17** |
| `APG-0917-CAMP-L` | 5993F8998BCF | SUPERSEDED — uses the unwanted root URL, never execute |
| `APG-0917-CALL-N` | A29431412E96 | **REJECTED — SUPERSEDED_WRONG_PHONE, never execute** |
| `APG-0917-GTM-P` | B3C69A1E65C8 | **EXECUTED 2026-09-17** |
| `APG-0917-CALL-Q` | E3214C210910 | **EXECUTED 2026-09-17** |

---

## DEVELOPER BLOCKED

Install GTM-M545Z8T2 sitewide including the 404 template · publish
`/permanent-christmas-lights-lincoln-ne/` and `/thank-you/permanent-christmas-lights/`
(both currently HTTP 404) · build a dedicated PPC form with a server-verified success
redirect, a real non-PII lead ID, client-side click-ID capture and cache exclusion ·
create a Terms and Conditions page, none exists · load the 8 approved images into the
WordPress media library rather than hotlinking Drive.

## OWNER BLOCKED

Restore billing, **never the Stockdale Outdoors payments profile** · complete advertiser
verification, Google states a 1 to 10 day review · supply the WhatConverts tracking snippet
for profile 174313 or an authenticated session, plus the pool quantity and exact recurring
cost · verify 402-526-5754 routes to 402-202-7261 · written commercial-use rights for the
four photographs · average gross profit per sold project.

---

## Verified state, end of 2026-09-17

**Google Ads.** Campaign **24257151015 PAUSED** · budget 15884926233 at 16,440,000 micros ·
2 ad groups · 4 RSAs · 5 keywords · **93 campaign criteria** (14 location, 1 language,
75 negative keyword, 3 implicit device) · **0 ad-schedule criteria** · **8 campaign asset
links** (6 callout, 1 snippet, **1 CALL**) · **1 call asset 422649064971 carrying
402-526-5754** · custom conversion goals 0 · conversion actions 3 (2 Primary, 1 Secondary) ·
7 shared negative lists all `reference_count=0` · auto-tagging on · call reporting on ·
account-level `call_conversion_action` still the stale `/179`, deliberately untouched ·
`accepted_customer_data_terms` false · `enhanced_conversions_for_leads` false ·
`accepted_lead_form_terms` false.

**GTM.** Workspace 3 holds 10 objects with **Workspace Changes 7** (0 modified, 7 added,
0 deleted). **Container versions 0, publishes 0, Submit never used.** Live container still
reads *"Empty Container is Live — 0 Tags, 0 Triggers, 0 Variables"*, with only Version 1
"Empty Container" (09/16/2026), the container's own initial version.

**The campaign is PAUSED and cannot spend. Nothing was enabled. No GTM version and no
publication. WordPress untouched. WhatConverts untouched and never signed into. Manager
337-371-1342 never mutated. Zero deletes across every plan.**

**Pre-enable requirements:** the landing page must return 200 at
`https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/`, and enablement needs
its own separate approval after readback QA.

**Pre-publish requirement:** Walter must choose option A or B in the GTM publication gate.
The `lead_id` gate means no form conversion fires at all until the developer ships the
dataLayer push.


---

## State verified 2026-09-28 (independent audit run B) — supersedes the "end of 2026-09-17" section above

Full record: `audits/2026-09-28-independent/00_README.md`. Read-only; 0 external mutations.

- **Campaign 24257151015 is ENABLED** (PAUSED -> ENABLED 2026-09-21 09:04:56 CT via the Google Ads web UI, agency
  login). No enable-approval receipt is on file.
- **GTM: version 2 was published 2026-09-17** (Google tag, form conversion, Calls from Website tag) and **version 3
  "Add Conversion Linker tag" on 2026-09-28 14:38:53 CDT**. No publication receipt is on file. Workspace 5 is current
  with 0 pending changes.
- **Tablet device criterion ~30002 is at -100%** since a 2026-09-25 web-UI edit. Plan `plans/APG-0928-DEV-T.yaml`
  (fingerprint 46060B03F5C9) restores it, pending approval.
- **The form conversion cannot fire**: `/thank-you/permanent-christmas-lights/` does not exist (WordPress redirects it to
  the LP), and `apg_permanent_lights_lead` is pushed nowhere. Developer handoff in
  `audits/2026-09-28-independent/05_developer_repair_handoff.md`.
- WhatConverts replaces 402-202-7261 with 402-783-8482 (not 402-526-5754) and has 0 leads on 402-526-5754.

### Run C, 2026-09-28 — measurement repair handoff (`audits/2026-09-28-measurement-repair/`)

Read-only; 0 external mutations; 0 GTM versions; no forms, calls or ad clicks.
- The developer form and content handoff is ready.
- The GTM lead-ID guard is drafted (APG-0928-GTM-LID, no fingerprint).
- The tablet plan is on HOLD (APG-0928-DEV-T2, 3 required updates if restored). DEV-T / 46060B03F5C9 is VOID.
- WhatConverts configuration verified read-only: 402-526-5754 is number 640646 "GSA Traffic", static, never used, routed
  via call flow "Apogee Lawns - ICF" (destination not exposed); pool "Website Traffic" 402-783-8482 swaps 402-202-7261;
  GF1 (`gform_1`) is a tracked form.
- The LP shows **three** internal drafting notes (C1–C3 in the handoff).

### Run D, 2026-09-28 — owner answers recorded (`audits/2026-09-28-measurement-repair/09-11`)

- **Tablets:** excluded by owner decision (landing pages not tablet optimized). APG-0928-DEV-T2 is REJECTED; no
  restoration code.
- **Qualified lead** = asks for permanent Christmas light installation on the form or on the call (owner). Recorded in
  `client.yaml` `crm_stage_mapping.qualified`. The sold-installation definition and gross profit are still unknown.
- **Customer-supplied lights:** installed, per the owner only. APG-0928-NEG-LO (58362D536336) removes `labor only` and
  `my own lights` and keeps `customer supplied`. Not executed.
- **Call flow "Apogee Lawns - ICF":** the owner's screenshot shows recording, then dial 402-202-7261. The API confirms
  402-526-5754 is assigned to that flow. Routing and recording are untested.
- **0 external mutations.**

---

## State verified 2026-10-05 (read-only briefing + performance research)

Briefing: `reports/apogee-lawns/HANDOFF-2026-10-05-full-account-briefing.md`. Work order:
`work-orders/work-order-briefing-and-performance-research-2026-10-05.yaml`. **0 external mutations.**

- Campaign 24257151015 ENABLED, primary status LIMITED (BIDDING_STRATEGY_LIMITED). Still the only campaign.
- Billing setup 8587299012 APPROVED since 2026-09-16 19:01; the two 09-15 setups are CANCELLED.
- **No change_event rows after 2026-09-25 08:26** (tablet edit). A20 is closed: the 09-28 change_status rows were
  system updates, not edits.
- 09-21..10-04: 194 impr, 7 clicks, $46.32, CTR 3.6%, IS 80.7%, 0 conversions. Top-of-page 97 impr / 7 clicks;
  below-results 97 impr / 0 clicks. `[permanent christmas lights]` 91 impr / 0 clicks (QS 6).
- Assets: 1 call, 6 callouts, 1 snippet. **0 sitelinks, 0 location, 0 image, 0 business name/logo.**
- WhatConverts 09-21..10-05: 0 paid-search leads; 11 LSA leads (quotable); GTM published version still 3.
- The LP and thank-you path return a SiteGround captcha stub (HTTP 202) to scripted requests: re-verify in a browser.
- Keyword Planner seasonality (3 full years, Lincoln): Sep 4%, Oct 13%, Nov 50%, Dec 18% of annual searches.

## Conversion-path plan 2026-10-05 (READ + DRAFT; 0 external writes; validate_only dry runs only)

Package: `audits/2026-10-05-conversion-plan/00_README.md`. Work order + client profile reconciled; validator PASS.
- Browser QA (real engine, nothing submitted, conversion requests blocked): thank-you path 301s to the LP; no success
  event; **cache replays one ad visitor's UTMs and a stranger's gclid/gbraid into every visitor's form**; 3 form 1
  instances / 34 duplicate IDs; drafting notes C1-C3 plus C4-C5 published; WhatConverts and Google do not swap the same number.
- Bundles: APG-1005-WEB-REPAIR **5C808616F617** (developer handoff), APG-1005-KWNEG **EECDDF0AF0DE** (validate_only
  accepted), APG-1005-ADS **0A321B6092AE** (validate_only accepted). TEST and SITELINKS drafted, blocked.
- APG-0928-NEG-LO / 58362D536336 SUPERSEDED (banner added). Bidding unchanged (Max Clicks $8; deviation recorded).
