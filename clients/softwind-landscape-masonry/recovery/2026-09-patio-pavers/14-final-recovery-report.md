# Softwind Landscape & Masonry — Patio and Pavers recovery
## Phase A complete. Five change packages awaiting approval.

**Account:** Softwind Landscape & Masonry - Live · `2429758629` · USD · America/New_York
**Services:** work order A *patio construction* (campaign Patio, `23484806108`) ·
work order B *paver installation* (campaign Pavers, `23489296528`)
**Report date:** 2026-09-03 · **Mode so far:** read, local draft, `validate_only`
**Durable Google Ads changes made: none.**

---

## 1. Status and the exact next step

Phase A is finished. Identity verified live, both work orders created and
validating, a complete before snapshot taken with zero query errors, the whole
search-term corpus classified, the landing pages QA'd in a real browser, and five
change packages built, collision-tested, fingerprinted and passed through
`validate_only` against the live account — 167 operations, all valid, nothing
created.

**Next step: approve the packages in section 5, in the order given.**
One package (`PLAN-SLM-NEG-1`) has a hard dependency and must run after
`PLAN-SLM-KW-1`. Three further plans are drafted but deliberately *not*
approval-ready; they are blocked on the six questions in section 8, and question
**SLM-Q5** is worth more than all the others combined.

---

## 2. What is actually wrong

The audit's conclusion — that roughly a third of the CPL rise was price and
two-thirds was conversion rate — holds up against fresh data, and both halves
have a concrete, fixable cause.

**The price half. Neither serving campaign has a CPC bid ceiling.** Both run
Maximize Clicks (`TARGET_SPEND`) with `cpc_bid_ceiling_micros` unset, so nothing
bounds what a click can cost. Pavers paid **$21.24 per click in August, $22.76 in
September, and $27.83 on 3 September alone**. The paused Paver Sealing campaign
in the same account has a $7.50 ceiling; the two campaigns spending all the money
have none. *(FACT)*

**The conversion half. Over half of recent spend buys the wrong service, or a
service nobody has confirmed the client sells.** In the last 30 days, of $1,195.62
of visible Patio/Pavers search-term spend:

- **31.4% ($375.00) confirmed wrong service** — asphalt, sealcoating, sealing,
  patio covers, enclosures, restoration. Wrong service is now the *largest*
  bucket, ahead of in-scope KEEP intent at 29.9%.
- **22.2% ($265.21) unresolved service** — driveways, concrete, masonry,
  bluestone — which has produced **zero conversion credits, ever**.
- Two of the five recent conversion credits came from sealcoating and sealing
  terms. *(CALCULATION from 05-search-term-verdicts.csv)*

**Why 1,452 negatives did not stop it.** Every campaign-level negative on Patio
and Pavers is **BROAD** (420 and 416), and the linked "General List" shared set is
1,109 BROAD out of 1,111. A BROAD negative only blocks a query containing *all*
of its words, so `asphalt paving` never blocked `asphalt contractor near me`. The
existing layer is large and structurally ineffective. *(FACT + INFERENCE)*

**And seven asphalt keywords are still ENABLED**, added on 2026-06-16:
$247.91 spent, 10 clicks, 1 credit — for a service outside both work orders.

**The measurement half. One lead can be counted three times.** Twelve conversion
actions are `primary_for_goal` and seven of those count into the Conversions
column. `Softwind Submit lead form` (WEBPAGE) and `(web) form_submission` (GA4)
fire on the same submission and both count — Mar 1/3, Apr 3/5, May 1/1, Jun 1/1,
Jul 2/2, Aug 0/1 — and `WC Leads` uploads the same lead a third time. In June
2026 both `Calls from ads` actions fired together. **The August "5 conversions"
is not 5 leads.** *(FACT)*

**The call path is broken, and the reason is now known.** The WhatConverts number
swap on both landing pages is configured as
`wc_swap = 6315025402 → 6315535927`: it is trying to replace **(631) 502-5402**.
The pages render **(631) 502-7946**. The swap can never fire. That is a complete
and sufficient explanation for `WC Call` having recorded **zero conversions and
zero all-conversions in its entire life**, and for `Softwind - Phone Call Lead`
going silent after June. *(FACT, from the live `wc_swap` cookie)*

**And the blank campaign/keyword in WhatConverts is not a lost-parameter
problem.** A synthetic probe GCLID reached the page, entered the DOM, and was
captured by WhatConverts' own `wc_client` cookie. What is missing is the campaign
name and keyword: neither campaign nor the account carries a `final_url_suffix`,
and the account tracking template is ClickCease's, which passes no UTMs.
WhatConverts can derive source and medium from a GCLID but cannot derive a
campaign or keyword without UTMs or a connected Google Ads integration. Neither
exists. *(FACT + INFERENCE — this rules out the parameter-loss hypothesis)*

---

## 3. Things that were already right — no change proposed

Worth stating plainly, because each was on the list to fix and none needs it:

- **Presence location targeting is already correct and verified.** 100% of
  Patio/Pavers cost is `LOCATION_OF_PRESENCE` ($4,817.01 of $4,861.37, 399 clicks,
  12.5 credits). Zero area-of-interest. **P1-4 is closed with evidence.**
- **Audiences are observation, not targeting.** `target_restrictions` is
  `AUDIENCE / bid_only: true` on all six campaigns, with no bid modifier. Reach is
  not restricted.
- **Google-hosted local actions are already isolated.** All five are
  `include_in_conversions_metric: false` and every GOOGLE_HOSTED customer goal is
  `biddable: false`. 120 "Other engagements" in July–August never entered the
  Conversions column.
- **Search Partners off, Display off, AI Max off, text-asset automation and final
  URL expansion opted out** on every campaign.
- **ClickCease is live and syncing** — 235 IP blocks on each serving campaign.
  Untouched by every plan here.
- **The four out-of-scope campaigns are all already PAUSED.** Nothing needs to be
  turned off, and nothing will be turned back on.
- **The two RSA headlines that looked like mojibake are fine.** Inspected at
  codepoint level: U+2019, a normal apostrophe. Terminal artefact, not a defect.

---

## 4. Baseline reconciliation against the forensic audit

The audit document itself is **not present in this repository**. Its May–August
figures were re-derived independently from the API and reconcile within rounding.

| Month | Audit spend | Live spend | Audit credits | Live credits |
|---|---|---|---|---|
| May 2026 | $766.01 | $766.01 | 8 | 8 |
| Jun 2026 | $2,110.22 | $2,110.21 | 27 | 27 |
| Jul 2026 | $2,079.12 | $2,079.11 | 17 | 17 |
| Aug 2026 | $2,146.14 | $2,146.14 | 5 | 5 |

Patio+Pavers combined reconciles the same way ($317.49 / $374.58 / $375.73 /
$1,917.55), as does August's split — Patio $949.84 for 1 credit, Pavers $967.71
for 4. **The audit is sound. Nothing in it needed correcting.**

### What is new since the audit ended

1. **September is worse, not better.** Sep 1–3: $248.36 spent, 14 clicks,
   **0 conversions of any kind**, avg CPC **$17.74** — up from August's $13.33.
2. **The last lead-type credit on this account was 2026-08-22.** Google-hosted
   local actions kept firing to 08-31, so the account was serving; the
   website-tag-dependent actions have been silent for 26+ days.
3. **Budgets are unchanged** at $33.00/$33.00 since the 2026-08-03 move.
4. **The cap is already breached on paper.** At $66.00/day combined, projected
   September spend is **$2,030.36** — over the $2,000 cap before any Maximize
   Clicks overdelivery, and it has already overdelivered twice.

---

## 5. The five packages — APPROVAL REQUIRED

All five passed `validate_only` against the live account on 2026-09-03
(167 operations, 0 errors). Receipts in
`10-change-packages/00-validate-receipts.json`.

**Approve in this order.** `PLAN-SLM-NEG-1` must execute and read back *after*
`PLAN-SLM-KW-1`, because its `asphalt` PHRASE negative would otherwise block the
account's own live keywords.

| # | Plan | What it does | Objects | Approval string |
|---|---|---|---|---|
| 1 | **PLAN-SLM-BID-1** | Set a **$22.00** CPC ceiling on both campaigns (currently none) | 2 | `APPROVE APPROVE-BIDDING 50C553579EF3 FOR 2429758629` |
| 2 | **PLAN-SLM-BUD-1** | Patio $33→**$24**, Pavers $33→**$32** | 2 | `APPROVE APPROVE-BUDGETS D82341B7238E FOR 2429758629` |
| 3 | **PLAN-SLM-KW-1** | Pause the 7 ENABLED asphalt keywords in Pavers | 7 | `APPROVE APPROVE-KEYWORD-PAUSES 19FA5CBBB1E5 FOR 2429758629` |
| 4 | **PLAN-SLM-NEG-1** | 154 PHRASE campaign negatives, 12 wrong-service families | 154 | `APPROVE APPROVE-NEGATIVES 0895911A8133 FOR 2429758629` |
| 5 | **PLAN-SLM-CONV-1** | Demote the 2 duplicate primary conversion actions | 2 | `APPROVE APPROVE-CONVERSIONS FB9DA2D017AD FOR 2429758629` |

Each fingerprint covers only that plan's exact contents. Any change to a value
invalidates it.

### PLAN-SLM-BID-1 — why $22.00, and why it is step 1 of a step-down

$22 binds Pavers (realised $22.76 in September, $27.83 on the worst day) and
barely touches Patio (realised $13.98), so it removes the runaway price without
starving the healthier campaign.

The in-scope converting search terms sat at term-average CPCs of **$2.71, $11.60,
$19.98 and $30.06**; the wrong-service ones at $13.73, $14.11 and $46.54. A $22
ceiling clears the first three in-scope points with headroom. The $30.06 term
carried 2 credits on a single click — and those two credits are almost certainly
one form submission double-counted by `(web) form_submission` and `WC Leads`, the
exact duplicate `PLAN-SLM-CONV-1` fixes. Treated as one lead, $22 costs the
account very little.

**This is deliberately conservative.** Once `PLAN-SLM-NEG-1` has 14 days of data
and the wrong-service traffic is gone, re-derive the ceiling and consider $18,
then $16, each through a new approval. Do not step down before that evidence
exists — on the sibling account a Keyword Planner sweep found a hard
top-of-page cliff that would have starved two ad groups.

### PLAN-SLM-BUD-1 — the arithmetic

| Input | Value |
|---|---|
| Account MTD (Sep 1–3, today partial) | $248.36 |
| Remaining budget = max(0, 2000 − MTD) | $1,751.64 |
| Remaining days (Sep 4–30) | 27 |
| Remaining daily allowance | $64.88 |
| Current combined budget | $66.00 → projects **$2,030.36 (over)** |
| **Proposed combined budget** | **$56.00 → projects $1,760.36** |
| Headroom left for overdelivery | **$239.64** |

Patio is cut first per the recovery brief: August Patio spent $949.84 for 1 credit
at 1.16% CVR, and all-time it is $586 per credit against Pavers' $296 ($457 after
removing Pavers' three wrong-service credits).

**The counter-evidence is recorded, not hidden.** Patio buys cheaper clicks,
carries a smaller wrong-service share ($234.01 vs $331.78 of visible spend), and
holds the account's best converting keyword — `patio pavers contractor` PHRASE,
3 credits on $314.39. That is exactly why the cut is modest: Patio keeps 73% of
its budget rather than being halved.

### PLAN-SLM-NEG-1 — what it blocks and what it protects

154 negatives, **all PHRASE**, campaign level only, across twelve families:

| Family | Negatives | Visible spend blocked | Credits blocked |
|---|---|---|---|
| asphalt | 8 | $169.77 | 1.0 |
| patio covers / pergolas / gazebos | 18 | $145.50 | 0 |
| sealcoating | 8 | $117.29 | 1.0 |
| enclosures / sunrooms | 12 | $48.61 | 0 |
| restoration / resanding | 12 | $21.36 | 0 |
| paver & patio sealing | 16 | $13.73 | 1.0 |
| resurfacing | 7 | $12.50 | 0 |
| cleaning (sibling-account fence) | 14 | — | 0 |
| deck structures | 13 | — | 0 |
| retail / DIY | 26 | — | 0 |
| employment | 10 | — | 0 |
| equipment | 10 | — | 0 |

**Coverage: 93.8% of Patio's confirmed wrong-service spend and 93.2% of Pavers'.**

It blocks 3 historic credits on purpose — one asphalt, one sealcoating, one
sealing — all outside both work orders.

**Every candidate was collision-tested before it was proposed**, against all 461
positive keywords in both campaigns (ENABLED *and* PAUSED, because a paused
keyword is a future casualty), every KEEP/WATCH/UNRESOLVED search term, and the
1,452 negatives already blocking. Four candidates were rejected rather than
softened; the exact collision is recorded for each in `06b-negative-rejected.csv`.
No bare noun the account sells is used: `deck` is never negated because pool decks
are in scope, and none of the nine agency-protected terms (`near me`, `quote`,
`price`, `cost`, `best`, `hire`, `local`, `emergency`, `pricing`) appears.

**One thing worth knowing:** Google's `validate_only` accepted the `asphalt`
negative even while the seven asphalt keywords were live. The API does not catch
that collision — only the local test did. That is why `PLAN-SLM-NEG-1` carries an
explicit dependency rather than relying on the platform to protect the account.

### PLAN-SLM-CONV-1 — deliberately narrow

Two demotions only:

- `Softwind Submit lead form` (7461619140) → secondary. Duplicates the GA4
  `form_submission` (7480764700), which stays primary as the single form lead
  signal. **Verified neither is required by WhatConverts** — WhatConverts writes
  to `WC Leads` (UPLOAD_CLICKS) and `WC Call` (UPLOAD_CALLS).
- `Calls from ads (1)` (7508686781) → secondary. Duplicates `Calls from ads`
  (7461572537) and has recorded nothing since June 2026.

**Held back on purpose:** `WC Leads` is also a duplicate third credit, but it
currently carries the *only* credit Patio recorded in August, and its intended
replacement last fired 2026-08-08. Demoting both at once would leave the account
with no lead signal at all. It gets demoted after the WhatConverts repair is
verified. `WC Call` is broken rather than duplicative — fix the path, then the flag.

Nothing is deleted, renamed, recategorised or restatused. `include_in_conversions_metric`
is not touched anywhere; it is deprecated and effectively immutable, and
`primary_for_goal` plus the goal layer is the real gate.

**Reported conversions will fall.** That is the point. Historic months are *not*
restated — a credit already counted stays in the historical column forever — so
before/after comparisons must be drawn at the change date, not across it.

---

## 6. P1 — drafted, blocked on answers

### Canonical structure (`PLAN-SLM-P1-STRUCT-1`, not approval-ready)

Rebuilt inside the existing campaigns, not new ones:

| Campaign | Canonical ad group | Owns | Landing page |
|---|---|---|---|
| Patio | **Patio Construction** | patio construction / contractor / builder / installation | `/patio/` |
| Patio | **Patio Paver Installation** | patio intent naming pavers | `/patio/` |
| Pavers | **Paver Installation** | paver intent with no patio word | `/pavers/` |

Each holds Phrase **and** Exact for its canonical texts — match type does not get
its own ad group. The full 161-keyword migration map with per-keyword verdicts is
in `07-keyword-migration-map.csv`.

**Blocked by SLM-Q5.** 76.5% of live keyword spend already maps cleanly to one of
the three owners; the missing 17.0% is the unresolved driveway/paving family and
its correct owner cannot be decided until the owner answers. Pausing the asphalt
keywords lifts clean mapping to **81.9%**, past the 80% target.

Two structural traps found and recorded rather than acted on:

- The PAUSED ad group `Paver Patio Installation Near Me` (191263597185) holds
  **7 ENABLED keywords and 2 ENABLED RSAs**. Enabling that group starts all nine
  serving instantly. Enumerate the children before any enable.
- Both enabled Pavers ad groups run only **one** RSA; the second is paused in each.

### RSA copy (`PLAN-SLM-ADS-1`, not approval-ready)

Six RSAs drafted — two materially distinct per canonical ad group, 90 headlines
and 24 descriptions, all validated for character limits, ASCII, duplicates and
banned claims. In `09-rsa-copy-and-url-plan.csv`.

**Blocked by SLM-Q6, and this is a live problem, not just a drafting one.** The
ads serving *right now* claim "Licensed & Insured", "Certified Paver Installers",
"Warranty-Backed Pavers", "Install Start In 7 Days" and "Call Back Within 10
Minutes", and both landing pages carry "Our 100% Satisfaction Guarantee". None of
these is verified in any client record. The drafted replacements deliberately use
**none** of them — they are strictly safer than what is live today, and can ship
the moment the claims are either confirmed or dropped.

### Weekly quality loop (P1-5) — schema delivered

`12-quality-loop-template.csv` joins traffic to outcomes on a **hashed lead ID and
the Google click ID only** — never a name or phone number, and never fuzzy
matching. No weekly recommendation may write to Google Ads; it must produce an
approval package first.

**It cannot be populated yet.** WhatConverts' campaign and keyword fields are
blank, so the join key does not exist until SLM-Q8 is resolved.

---

## 7. P2 readiness gates

| Test | Gate | Status |
|---|---|---|
| **P2-2 Smart Bidding** | ≥30 qualified conversions in 30 days, clean dedup, controlled wrong-service share | **NOT READY.** 0 conversions in September; the last credit of any kind was 2026-08-22; duplicates unresolved. Stay on Maximize Clicks. No speculative tCPA. |
| **P2-1 Landing-page test** | measurement repaired first | **NOT READY**, but the QA is done and the defect list is concrete (section 13 of `02-before-snapshot.md`). |
| **P2-3 Device / schedule / audience** | 60–90 days, adequate sample | **NOT READY.** 399 clicks and 12.5 credits all-time across both campaigns cannot support a device or daypart decision. |
| **P2-4 Auction response** | — | Impression share *improved* Jun→Aug (Patio 24.7%→44.5%, Pavers 35.2%→41.6%). Demand did not disappear. Fix relevance and routing before bidding for visibility. |

**Landing-page evidence that should drive P2-1:** of the 13 serving keywords with
a Quality Score, **landing page experience is BELOW_AVERAGE on 9** and expected
CTR on 10. Google's own diagnostic points at the page, not the bid.

---

## 8. Questions — one consolidated list

Ordered by money at stake. Everything not dependent on these is already finished.

**SLM-Q5 — service truth. This is the single most valuable answer.**
$662.48 of visible Patio/Pavers spend (25.9%) has gone to service themes nobody
has confirmed, and that spend has produced **zero conversion credits**. For each,
does Softwind offer it?

| Theme | Visible spend | Credits | My recommendation if unanswered |
|---|---|---|---|
| **Driveway paver installation** | **$346.05** | 0 | Keep `paver driveway installation near me`; pause the two unqualified "driveway companies" keywords, which carry no paver word |
| Concrete patio installation | $173.24 | 0 | Treat as offered — the Patio page FAQ and a live ad both assert it |
| Bare "deck" (not pool deck) | $134.15 | 0 | Leave unblocked |
| Masonry repair | $62.01 | 0 | Leave unblocked; see SLM-Q3 |
| Bluestone patio | $22.74 | 0 | Leave unblocked |
| Patio resurfacing | $12.50 | 0 | **Currently blocked by PLAN-SLM-NEG-1.** If it *is* offered, remove those 7 negatives before executing |

**SLM-Q6 — public claims.** Can Softwind substantiate: licensed, insured,
certified installers, a warranty, a 100% satisfaction guarantee, "install start in
7 days", "call back within 10 minutes"? Each is live in ads or on the landing
pages today. *Recommendation: confirm what is true and drop the rest; the drafted
RSAs already avoid all of them.*

**SLM-Q7 — qualified call definition.** `Calls from ads` counts a call at **30
seconds**; every other action on the account uses 60. *Recommendation: 60 seconds,
matching the rest — but it changes what counts as a lead and breaks comparability
with history, so it is your call, not mine.*

**SLM-Q8 — WhatConverts.** Two parts:
1. Is **(631) 502-5402** a real Softwind number? The WhatConverts swap is
   configured to replace it, but the pages render (631) 502-7946, so the swap can
   never fire.
2. Can Green Marketing get WhatConverts admin access? *Recommendation: connect the
   WhatConverts↔Google Ads integration rather than adding UTMs — it fixes the
   blank campaign/keyword with **no change to the ad-serving path**, which matters
   because ClickCease owns the tracking template. `PLAN-SLM-TRK-1` (a final URL
   suffix) is drafted as the fallback if the integration is unavailable.*

**SLM-Q9 — the sibling tag.** `AW-18369652705`, the Softwind Power Washing
account's tag, loads on **this** account's landing pages, and this account's tag
runs number replacement on the sibling's pages. Same company, two deliberately
scope-fenced accounts. Should the tags be separated? *Recommendation: yes — it is
an attribution defect, not a privacy breach, but it corrupts both accounts' data.*

**SLM-Q10 — lead handling** (needed before any speed-to-lead promise): real
answering hours, after-hours handling, a response-time SLA staffing can actually
meet, qualification criteria for Patio and Pavers, estimate and sold stage
definitions, average job revenue and gross margin. Without these, **CPQL, cost per
sold job, ROAS and profit after ad spend cannot be calculated at all** — they are
reported as unavailable, never as zero.

**SLM-Q3 (carried over)** — does this account run landscaping or masonry beyond
Patio and Pavers? Blocks nothing in this program.

**SLM-Q4 (resolved by the account itself)** — paver sealing belongs to
`2429758629`: it has its own paused campaign (23914857298), three ad groups and
its own landing page here. No answer needed; recorded in
`03-service-truth-decisions.yaml`.

---

## 9. One observation outside scope, offered without a recommendation

The account's cheapest leads never came from Patio or Pavers. All-time, by
campaign:

| Campaign | Spend | Credits | Cost per credit | Status |
|---|---|---|---|---|
| Retaining Walls | $2,148.99 | 51.5 | **$41.73** | PAUSED |
| Power Washing | $613.72 | 10.0 | $61.37 | PAUSED |
| Paver Sealing | $881.87 | 7.0 | $125.98 | PAUSED |
| Hardscaping | $2,208.56 | 8.0 | $276.07 | PAUSED |
| **Pavers** | $2,515.56 | 8.5 | **$295.95** | ENABLED |
| **Patio** | $2,345.81 | 4.0 | **$586.45** | ENABLED |

The two campaigns still running are the two worst performers in the account, and
they absorbed **89.3% of August spend**. Retaining Walls alone produced 20 credits
on $306.31 in April. (Every figure here is a raw credit and carries the same
duplicate-counting inflation, so the ranking is more reliable than the absolute
numbers.)

I am **not** proposing to reactivate anything. The recovery brief explicitly
forbids reactivating a campaign to improve blended reporting, and those campaigns
are outside both work orders. But if the goal is qualified leads per dollar rather
than Patio and Pavers specifically, that is a conversation worth having on its own
terms, with its own work order.

---

## 10. Monitoring, once anything is live

Same day: readback QA. 24–72h: serving, policy, URL, tracking and spend anomalies.
7 days: pacing, query mix, wrong-service share, attribution completeness.
14 days: directional CPQL and the bid-ceiling step-down decision.
30 days: formal keep / modify / roll back. Schema in `13-monitoring-log.csv`.

**Escalate immediately on:** identity mismatch · tracking outage or duplicate
primary credits · projected spend above $2,000 · wrong-service share above 10%
after cleanup · any new broad-match keyword or expansion feature · Search
Partners, Display, AI Max, DSA or Final URL expansion switching on · new
disapprovals · out-of-area qualified leads · partial write failure.

---

## 11. Rollback state

Nothing has been changed, so the rollback state is the current live account. Each
package carries its own rollback: clear the ceiling field, restore 33000000 on
both budgets, re-enable the seven criteria, remove the created negatives, restore
`primary_for_goal` on the two actions. **No plan deletes anything**, so every step
is a single-field reversal.

---

## 12. Honest limits of this report

- **No qualified-lead, sold-job, revenue or gross-profit figure appears anywhere**,
  because no CRM or WhatConverts export is available and WhatConverts' own campaign
  and keyword fields are blank. Every such metric is **unavailable, not zero**.
- **Auction Insights could not be read.** Every auction-insight metric returns
  `PERMISSION_DENIED` on a Basic-access developer token. It must be exported from
  the UI.
- **Change history before 2026-08-06 is not retrievable.** `change_event` is
  hard-capped at 30 days, so the 2026-06-16 keyword expansion and the 2026-08-03
  budget move are taken from the forensic audit, not re-read.
- **Search-term coverage is 52.6% all-time and 57.4% over the last 30 days.**
  Every share in section 2 is a share of *visible* spend. The suppressed remainder
  is unknown and may differ.
- **The forensic audit document is not in this repository.** Its figures were
  re-derived independently and reconcile; the document itself was never read.
- **`input_9` on both landing pages is an unlabelled visible text field.** On the
  sibling account the same index was a honeypot that fakes a broken form when
  filled. It is **not verified** here either way, so no live form test should be
  automated until the field map is confirmed.
- **Two claims in an earlier draft of this analysis were checked and withdrawn:**
  the RSA "mojibake" (a normal U+2019 apostrophe) and an initial Quality Score
  count of 6 (the correct figure is 13 of 50 serving keywords).
