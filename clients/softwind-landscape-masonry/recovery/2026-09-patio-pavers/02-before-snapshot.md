# Before snapshot — Softwind Landscape & Masonry (2429758629)

Structural read `2026-09-03T18:12 -04:00`, performance read `2026-09-03T18:16 -04:00`,
probe `2026-09-03T18:22 -04:00`, landing pages `2026-09-03T18:34 -04:00`.
All reads SELECT-only, 0 query errors. Nothing in the account was changed.

Every number below is **FACT** unless marked CALCULATION or INFERENCE.

---

## 1. Identity — FACT

| Field | Requested | Observed | Match |
|---|---|---|---|
| Account name | Softwind Landscape & Masonry - Live | Softwind Landscape & Masonry - Live | yes |
| Child customer ID | 242-975-8629 | 2429758629 | yes |
| Currency | USD | USD | yes |
| Time zone | America/New_York | America/New_York | yes |
| Patio campaign ID | 23484806108 | 23484806108 | yes |
| Pavers campaign ID | 23489296528 | 23489296528 | yes |

Manager `false`, test `false`, status `ENABLED`, auto-tagging `true`,
conversion tracking ID `17878095007`, tracking managed by self.
No mismatch of any kind. Receipt: `snapshots/identity-gate-2026-09-03-1809.json`.

## 2. Campaigns — FACT

| Campaign | ID | Status | Budget/day | Bidding | CPC ceiling | Search partners | Display | AI Max |
|---|---|---|---|---|---|---|---|---|
| Patio | 23484806108 | **ENABLED** | $33.00 | TARGET_SPEND | **none** | off | off | off |
| Pavers | 23489296528 | **ENABLED** | $33.00 | TARGET_SPEND | **none** | off | off | off |
| Hardscaping | 23484545411 | PAUSED | $21.00 | TARGET_SPEND | none | off | off | off |
| Paver Sealing | 23914857298 | PAUSED | $14.00 | TARGET_SPEND | $7.50 | off | off | off |
| Power Washing | 23914859260 | PAUSED | $33.00 | TARGET_SPEND | none | off | off | off |
| Retaining Walls | 23489591905 | PAUSED | $12.00 | TARGET_SPEND | none | off | off | off |

Only Patio and Pavers are serving. Every campaign uses PRESENCE for both the
positive and the negative geo target type. All budgets are standard delivery,
non-shared, reference count 1. `TEXT_ASSET_AUTOMATION` is `OPTED_OUT` on all six;
`FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION` is `OPTED_OUT` where present.

**Neither serving campaign has a CPC bid ceiling.** Under Maximize Clicks that
means nothing bounds the price of a click.

## 3. Structure — FACT

- 18 ad groups (6 in scope: 3 Patio, 3 Pavers).
- 161 positive keywords in Patio and Pavers; **50 are effectively serving**
  (ENABLED keyword inside an ENABLED ad group).
- 234 ad-group-level negatives.
- 36 ads; 12 in Patio/Pavers, all `APPROVED`.
- The Pavers ad group **Paver Patio Installation Near Me** (191263597185) is
  PAUSED but contains **7 ENABLED keywords and 2 ENABLED RSAs**. They begin
  serving the instant the group is enabled.
- Both enabled Pavers ad groups run **one** RSA each; the second RSA in each is
  PAUSED.
- Two near-duplicate Pavers ad groups compete: `Paver Installation Near Me`
  (191263597345) and `Paver Installation Near Me (Pharse)` (196134824089).

## 4. Negatives already in place — FACT

| Layer | Patio | Pavers | Match types |
|---|---|---|---|
| Campaign-level | 420 | 416 | **100% BROAD** |
| Shared set "General List" (11813144900) | linked | linked | 1,109 BROAD + 2 EXACT |
| Account-level list (11980673249) | applies | applies | 35 BROAD |
| **Distinct blocking total** | **1,452** | **1,448** | |

**INFERENCE:** the existing layer is far weaker than its size suggests. A BROAD
negative only blocks a query containing *all* of its words, so `asphalt paving`
never blocked `asphalt contractor near me`. That is why 1,452 negatives coexist
with 22.1% wrong-service spend.

A "Paver" shared set (11840874961, 387 BROAD members) exists but is **not linked
to any campaign**.

## 5. Location targeting — FACT

110 positive location targets per campaign, **0 exclusions**: 49 cities, 58 postal
codes, 2 neighborhoods, 1 municipality, all in New York (Nassau and Suffolk,
115xx and 117xx). Language: English. No proximity targets, no ad schedule, no
device bid modifiers.

`geographic_view` splits all Patio/Pavers cost as **LOCATION_OF_PRESENCE:
$4,817.01 of $4,861.37, 399 clicks, 12.5 credits. Zero AREA_OF_INTEREST.**

**P1-4 is already satisfied.** Presence targeting is verified live; no change is
proposed and none is needed.

## 6. Audiences — FACT

3 `USER_INTEREST` criteria on every campaign and 1 `USER_LIST` on Patio, all
`ENABLED`, non-negative, **no bid modifier**. Campaign
`targeting_setting.target_restrictions` is `AUDIENCE / bid_only: true` on all six
campaigns — that is **observation, not targeting**. Reach is not restricted. No
change needed.

## 7. Click-fraud protection — FACT

ClickCease is live and syncing: account-level tracking template pointed at
`monitor.clickcease.com`, and **235 `IP_BLOCK` campaign criteria on each of Patio
and Pavers** (201–203 on the paused campaigns). Preserved untouched by every plan
in this program.

## 8. Performance — FACT

### Account-wide, all campaigns

| Month | Spend | Impr | Clicks | Credits | CTR | Avg CPC | Raw CPL |
|---|---|---|---|---|---|---|---|
| May 2026 | $766.01 | 4,944 | 169 | 8 | 3.42% | $4.53 | $95.75 |
| Jun 2026 | $2,110.21 | 7,693 | 283 | 27 | 3.68% | $7.46 | $78.16 |
| Jul 2026 | $2,079.11 | 8,932 | 279 | 17 | 3.12% | $7.45 | $122.30 |
| Aug 2026 | $2,146.14 | 3,952 | 161 | 5 | 4.07% | $13.33 | $429.23 |
| **Sep 1–3 2026** | **$248.36** | **220** | **14** | **0** | **6.36%** | **$17.74** | **undefined** |

The May–August figures reconcile to the forensic audit within one cent of rounding.

### Patio and Pavers

| Month | Patio spend | Patio credits | Pavers spend | Pavers credits | Combined |
|---|---|---|---|---|---|
| May | $167.07 | 0 | $150.42 | 0 | $317.49 |
| Jun | $184.91 | 1 | $189.67 | 0 | $374.58 |
| Jul | $160.93 | 0 | $214.80 | 1 | $375.73 |
| Aug | $949.84 | 1 | $967.71 | 4 | $1,917.55 |
| **Sep 1–3** | **$111.81** | **0** | **$136.55** | **0** | **$248.36** |

August's five credits reconcile exactly to the audit: Patio `WC Leads` 1;
Pavers `Calls from ads` 2 + `(web) form_submission` 1 + `WC Leads` 1.

### CPC is still rising — FACT

| | August | September 1–3 |
|---|---|---|
| Patio avg CPC | $11.29 | $13.98 |
| Pavers avg CPC | $21.24 | **$22.76** |

Worst single day: **2026-09-03, Pavers, $83.49 for 3 clicks = $27.83 per click**,
with 3 of those clicks marked invalid. Read at 18:16; the day was incomplete.

## 9. Pacing against the $2,000 cap — CALCULATION

| Input | Value |
|---|---|
| Account MTD spend (Sep 1–3, today partial) | $248.36 |
| Remaining budget = max(0, 2000 − MTD) | $1,751.64 |
| Remaining days (Sep 4–30) | 27 |
| Remaining daily allowance = 1751.64 / 27 | **$64.88** |
| Current combined daily budget | **$66.00** |
| Projected at current budget = 248.36 + 66×27 | **$2,030.36 — over cap by $30.36** |
| Avg daily, complete days only (Sep 1–2) | $62.88 |
| Projected at that run rate | $1,946.12 |
| Avg daily including partial today | $82.79 |
| Projected at that run rate | **$2,483.69 — over cap by $483.69** |

The cap is breached on paper before any overdelivery. Maximize Clicks has already
overdelivered against the $66 combined budget on 2026-08-22 ($103.21) and
2026-09-03 ($122.59, partial). Google Ads itself has **no** account spending
limit here — `account_budget.approved_spending_limit_type = INFINITE`. The $2,000
cap is enforced only by campaign daily budgets.

## 10. Search-term corpus — CALCULATION

All retained history, Patio and Pavers, 1,507 distinct (campaign, term) pairs,
$2,557.31 of visible cost against $4,861.37 of actual campaign spend
(**52.6% visible coverage** — the rest is Google's low-volume suppression).

| Verdict | Terms | Cost | Share | Clicks | Credits |
|---|---|---|---|---|---|
| KEEP (in-scope buyer intent) | 320 | $804.78 | 31.5% | 67 | 4.0 |
| WATCH | 557 | $500.72 | 19.6% | 48 | 1.0 |
| **UNRESOLVED** (service truth unknown) | 326 | **$662.48** | **25.9%** | 43 | **0.0** |
| **NEGATIVE** (confirmed wrong service) | 263 | **$565.79** | **22.1%** | 43 | 3.0 |
| UNCLASSIFIED | 41 | $23.54 | 0.9% | 3 | 0.0 |

### Last 30 days (Aug 4 – Sep 3), $1,195.62 visible of $2,081.66 actual (57.4% coverage)

| Verdict | Cost | Share | Credits |
|---|---|---|---|
| **NEGATIVE** | **$375.00** | **31.4%** | 2.0 |
| KEEP | $356.94 | 29.9% | 2.0 |
| UNRESOLVED | $265.21 | 22.2% | 0.0 |
| WATCH | $188.37 | 15.8% | 1.0 |

**Wrong service is now the single largest bucket**, and 53.6% of recent visible
spend is wrong-service or unresolved-service.

### Wrong-service families, all time

| Family | Terms | Cost | Share | Credits |
|---|---|---|---|---|
| asphalt | 94 | $169.77 | 6.6% | 1.0 |
| patio covers / pergolas / gazebos | 56 | $159.90 | 6.3% | 0 |
| sealcoating | 29 | $117.29 | 4.6% | 1.0 |
| paver / patio sealing | 33 | $53.29 | 2.1% | 1.0 |
| enclosures / sunrooms | 17 | $48.61 | 1.9% | 0 |
| restoration / resanding | 9 | $34.05 | 1.3% | 0 |
| resurfacing | 10 | $12.50 | 0.5% | 0 |
| DIY pricing | 12 | $9.94 | 0.4% | 0 |

### Unresolved families, all time — 0 credits from any of them

| Family | Terms | Cost | Share |
|---|---|---|---|
| driveway | 114 | $346.05 | 13.5% |
| concrete | 149 | $173.24 | 6.8% |
| bare "deck" (pool deck is in scope) | 83 | $134.15 | 5.2% |
| masonry | 10 | $62.01 | 2.4% |
| pavement | 10 | $39.22 | 1.5% |
| pool deck | 28 | $27.51 | 1.1% |
| bluestone | 34 | $22.74 | 0.9% |

## 11. Live keyword surface — FACT

50 keywords effectively serving, $3,735.12 of all-time cost.

| Intended canonical owner | All-time cost | Share |
|---|---|---|
| Paver Installation | $1,142.29 | 30.6% |
| Patio Construction | $920.72 | 24.7% |
| Patio Paver Installation | $790.58 | 21.2% |
| **UNRESOLVED (driveway / paving)** | **$633.62** | **17.0%** |
| **Out of scope (asphalt)** | **$247.91** | **6.6%** |

Seven ENABLED asphalt keywords from the 2026-06-16 expansion sit in Pavers:
$247.91, 10 clicks, 1 credit.

Only **13 of the 50** serving keywords have a Quality Score at all: two 6s, two
5s, one 3, four 2s and four 1s. The component breakdown is the useful part:

| Component | BELOW_AVERAGE | AVERAGE | ABOVE_AVERAGE |
|---|---|---|---|
| Expected CTR | 10 of 13 | 3 | 0 |
| **Landing page experience** | **9 of 13** | 1 | 3 |
| Ad relevance | 4 of 13 | 6 | 3 |

**INFERENCE:** Google's own diagnostic points at the landing page and the ad's
expected click-through rate, not at the bid. The four QS-1 keywords
(`paving company near me`, `paver patio contractors near me`,
`paver companies near me`, `driveway companies near me`) are BELOW_AVERAGE on all
three components.

## 12. Measurement — FACT

16 conversion actions. **12 are `primary_for_goal`; 7 of those count into the
Conversions column.**

| Action | ID | Type | Primary | Counts | Last activity |
|---|---|---|---|---|---|
| Calls from ads | 7461572537 | AD_CALL, 30s, ONE_PER_CLICK | yes | yes | 2026-08-20 |
| Calls from ads (1) | 7508686781 | AD_CALL, 60s, MANY_PER_CLICK | yes | yes | **Jun 2026** |
| Softwind - Phone Call Lead | 7461590068 | WEBSITE_CALL | yes | yes | **Jun 2026** |
| (web) form_submission | 7480764700 | GA4 custom | yes | yes | 2026-08-08 |
| Softwind Submit lead form | 7461619140 | WEBPAGE | yes | yes | 2026-07-15 |
| WC Leads | 7635680357 | UPLOAD_CLICKS | yes | yes | 2026-08-22 |
| WC Call | 7635680543 | UPLOAD_CALLS | yes | yes | **never** |
| Clicks to call | 7559375681 | GOOGLE_HOSTED | yes | no | 2026-07-30 |
| Local actions ×4 | — | GOOGLE_HOSTED | yes | no | 2026-08-31 |
| (web) phone_call_click | 7480749998 | GA4 custom | no | no | 2026-07-11 |
| 3 hidden GA4 actions | — | GA4 | no | no | — |

Both campaigns use **CUSTOMER-level** conversion goals. The biddable customer
goals are PHONE_CALL_LEAD/WEBSITE, PHONE_CALL_LEAD/CALL_FROM_ADS,
SUBMIT_LEAD_FORM/WEBSITE, CONTACT/WEBSITE and CONTACT/CALL_FROM_ADS. Every
GOOGLE_HOSTED goal is `biddable: false`.

**INFERENCE — the local actions are already correctly isolated.** 120 "Other
engagements" in July–August never entered the Conversions column. They need no
change.

**FACT — duplicate primary credit is real.** `Softwind Submit lead form` and
`(web) form_submission` fire on the same submission and both count: Mar 1/3,
Apr 3/5, May 1/1, Jun 1/1, Jul 2/2, Aug 0/1. `WC Leads` uploads the same form
lead a third time. In June 2026 both AD_CALL actions fired together (6 and 1).

**FACT — the last lead-type credit of any kind was 2026-08-22.** Google-hosted
local actions kept firing to 2026-08-31, which proves the account was still
serving. Website-tag-dependent actions have been silent for 26+ days.

## 13. Landing pages — FACT (real headless browser, JS enabled)

`offer.softwindli.com/patio/` and `/pavers/`, both HTTP 200, no redirect,
160 KB, mobile viewport rendered.

Correct and healthy:
- H1 Patio: "Patio Installation By A Local Patio Contractor You Can Trust".
- H1 Pavers: "Paver Installation Near You In Long Island, NY".
- **GCLID and UTMs survive into the final URL and into the DOM.** A synthetic
  probe GCLID reached the page and WhatConverts' `wc_client` cookie captured
  `google .. cpc .. <gclid> .. <landing url>`.
- ClickCease loads.

Defects found on **both** pages:

1. **The WhatConverts number swap is pointed at a phone number that is not on the
   page.** Cookie `wc_swap = 6315025402+..+6315535927+..+197159` — it is
   configured to replace **(631) 502-5402** with tracking number
   **(631) 553-5927**. The page renders **(631) 502-7946**. The swap can never
   fire, so every call from these pages goes to an untracked number. This is the
   direct, sufficient explanation for `WC Call` having recorded zero conversions
   in its entire life.
2. **Two Google Ads tags load**: `AW-17878095007` (this account) and
   `AW-18369652705` (the sibling Softwind Power Washing account, 1521725229).
   Cross-account contamination on this account's own pages.
3. **Google's own number replacement is also running** —
   `conversion/17878095007/wcm`. Two competing number-replacement systems on one
   page.
4. **A truncated `tel:(631)` link** sits alongside the correct
   `tel:(631) 502-7946` on both pages. Tapping it dials nothing.
5. **Two identical copies of `form#gform_1`** with **22 duplicate DOM ids**,
   including every form field id.
6. **No click ID is captured into the form.** Hidden field `input_8` and
   `gform_field_values` are both empty on page load.
7. **`input_9` is an unlabelled visible text field.** Its only `label[for]`
   matches are "Facebook" and "LinkedIn" — broken label association. On the
   sibling account the same index was a honeypot. **Not verified here either
   way**; a live form test must not be automated blind.
8. Undocumented third parties: `process.iconnode.com` POSTs on every page, and a
   Meta pixel (`connect.facebook.net`) loads.
9. Unverified claims in live copy: "Our 100% Satisfaction Guarantee" on both
   pages; "Licensed & Insured", "Certified Paver Installers", "Warranty-Backed
   Pavers", "Install Start In 7 Days", "Call Back Within 10 Minutes" across the
   live and paused RSAs.
10. Stale seasonal copy: a paused Pavers RSA still offers a "January planning
    session"; the Patio page has a "Current Month Patio Planning Priority" block.
11. *(Checked and cleared.)* A headline that displayed as `A Finish You?ll Be
    Proud Of` in a terminal was inspected at codepoint level: the character is
    U+2019, a normal right single quotation mark. The ads are fine. No defect.

**INFERENCE — root cause of WhatConverts' blank campaign and keyword.** The
GCLID arrives fine, so parameter loss is ruled out. Neither campaign nor the
account carries a `final_url_suffix`, and the account tracking template is
ClickCease's, which passes no UTM campaign or term. WhatConverts can derive
source and medium from a GCLID but cannot derive a campaign name or keyword
without either UTMs or a connected Google Ads integration. Neither is present.

## 14. Changes since 2026-08-31 — FACT

`change_event` is capped at 30 days and lags by hours. 151 events in the 28-day
window were read. Budgets are still $33.00/$33.00 — unchanged since the
2026-08-03 move from $5.00 and $7.41. No structural change was found after
2026-08-31 that alters the audit's conclusions.

## 15. What is NOT retrievable — BLOCKED

- **Auction Insights.** Every auction-insight metric returns `PERMISSION_DENIED`
  on a Basic-access developer token. It must be exported from the UI.
- **Change history before 2026-08-06.** `change_event` is hard-capped at 30 days,
  so the 2026-06-16 keyword expansion and the 2026-08-03 budget move cannot be
  re-read from the API. Both are taken from the forensic audit.
- **The forensic audit document itself.** `Softwind_Patio_Pavers_Forensic_Audit_May-Aug_2026.docx`
  is not present anywhere in this repository. Its May–August figures were
  re-derived independently from the API and reconcile within rounding.
- **Qualified-lead, sold-job, revenue and gross-profit history.** No CRM or
  WhatConverts export is available to this project, and WhatConverts' own
  campaign and keyword fields are blank. Every CPQL, sold rate and profit figure
  in this program is therefore **unavailable, not zero**.
