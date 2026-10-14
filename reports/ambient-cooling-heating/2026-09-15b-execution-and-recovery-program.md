# Ambient Cooling - Live | 2401959466 | Commercial HVAC Installation
## Session 2026-09-15B — execution, reconciliation, and the full recovery program

**Two approved plans EXECUTED. Readback 0 FAIL. Nothing serves.**
Nine external writes total, all creates, all non-serving. Five new fingerprinted plans await approval.

---

## EXECUTED — `AMB-0915-COMM-RSA-1` · `6C32B210CF5B` · 2 operations

Pre-execution gate, all PASS: fresh identity 9/9 · fingerprint recomputed from disk and matched
the approved value · before-state drift gate 10/10 · `validate_only` VALIDATED_OK.

| Ad | ID | Status | Policy | Strength |
|---|---|---|---|---|
| RSA A — 3 openers pinned to HEADLINE_1 | `824781897834` | **PAUSED** | REVIEW_IN_PROGRESS | PENDING |
| RSA B — unpinned control | `824781897837` | **PAUSED** | REVIEW_IN_PROGRESS | PENDING |

Readback verified per ad: 15 headlines, 4 descriptions, every headline ≤30 and description ≤90,
pinned set exact, descriptions exact **and in order**, final URL exact, `commercial-hvac` /
`installation` paths, no tracking template, no URL suffix, type RESPONSIVE_SEARCH_AD.

## EXECUTED — `AMB-0915-COMM-ASSET-1` · `02F6EECCCDF8` · 7 operations

| Asset | ID | Link status | Policy |
|---|---|---|---|
| Callout `Free Consultation` | `421646926374` | **PAUSED** | REVIEW_IN_PROGRESS |
| Callout `Flexible Scheduling` | `421464532268` | **PAUSED** | REVIEW_IN_PROGRESS |
| Callout `Transparent Pricing` | `421568039029` | **PAUSED** | REVIEW_IN_PROGRESS |
| Callout `Central Maryland Service` | `421568040667` | **PAUSED** | REVIEW_IN_PROGRESS |
| Callout `Multiple System Options` | `421646926386` | **PAUSED** | REVIEW_IN_PROGRESS |
| Callout `Commercial HVAC Team` | `421568040679` | **PAUSED** | REVIEW_IN_PROGRESS |
| Snippet `Types:` Rooftop Units · Packaged Systems · Heat Pumps · Central Air · HVAC Replacement | `421646926389` | **PAUSED** | REVIEW_IN_PROGRESS |

Assets were created first, then linked in a second mutate with `AssetLinkStatus = PAUSED`, with a
`validate_only` pass on the link operation before committing — so a link failure would have left
seven inert unlinked assets rather than anything serving.

### Serving chain — still cannot serve, by design

`campaign ENABLED → ad group ENABLED → 2 ads, both PAUSED → 0 ENABLED asset links`
**Zero ENABLED ads means zero delivery.** 0 impressions, 0 clicks, $0.00.

### Unrelated resources — 16/16 PASS

Budgets `$141.45 / $78.95 / $176.15 / $20.00 / $5.00` = **$421.55/day → $12,815.12**, headroom
**$184.88** · ceilings `$25/$25/$30/$30/$25` · all five ENABLED · Search Partners off · PRESENCE ·
schedule 6 rows · 75 geo targets · 17 commercial negatives · 2 commercial keywords ENABLED ·
residential ads `821319509197` + `821319509200` ENABLED+APPROVED · residential ad-group negatives
**0** (routing negative correctly NOT applied) · campaign negatives 6,158 · 23 conversion actions ·
call asset `407995613637` ENABLED+APPROVED.

Not done, deliberately: sitelinks (only one valid anchor exists), image assets (the page itself
labels those images as not-Ambient-projects), call asset (reused, untouched), business name (reused).

---

## WhatConverts reconciliation — **COMPLETED**

Credentials were present in `.env` and worked. Read-only; no routing, number or lead changed; no
names, telephone numbers, email addresses or message bodies retained.

### Channel split, 294 leads, 2026-06-17 → 09-15

| Channel | Leads | Share |
|---|---:|---:|
| GBP | 207 | 70.4% |
| LSA *(out of scope)* | 47 | 16.0% |
| **Google Ads paid search** | **22** | **7.5%** |
| Organic / direct / other | 18 | 6.1% |

### Paid search is not junk — it is the best-qualified channel after GBP

| Channel | n | Yes | No | Qualified rate of decided |
|---|---:|---:|---:|---:|
| **Paid search** | 22 | 10 | 9 | **52.6%** |
| GBP | 207 | 40 | 29 | 58.0% |
| LSA | 47 | 3 | 3 | 50.0% |

Paid web forms are the single best sub-source: **5 of 7 qualified (71%)** — and they are exactly
what the caching defect breaks.

### Attribution retention is the failure

| Metric | Result |
|---|---|
| UTM retention (source/medium/campaign/term/content) | **0 of 294 — zero, on every field** |
| GCLID on any lead | 8 / 294 (2.7%) |
| GCLID on paid-labelled leads | 8 / 22 (36%) |
| `landing_url` present | 24 / 294 (8%) |
| `quote_value` / `sales_value` populated | **0 / 294** |
| WhatConverts' own `duplicate` and `spam` flags | never set |

### The "unexplained" number is now identified

| Number | Role | Leads (90d) | Qualified | Top source |
|---|---|---:|---:|---|
| `...4021` | GBP | 130 | 30 | 2nd GBP Traffic |
| `...7280` | GBP | 64 | 7 | GBP Traffic |
| `...7756` | LSA | 40 | 0 | LSA's - Severn |
| **`...1456`** | **mixed-source** | **17** | **5** | direct, GBP/organic |
| **`...6354`** | **approved paid** | **11** | **4** | google/cpc 6, google/organic 5 |
| **`...9517`** | **was "unexplained"** | **8** | 0 | **google/cpc 8 — all of them** |
| `(none)` = web forms | paid forms | 7 | **5** | google/cpc 6 |

**`410-415-9517` is a Google Ads call-forwarding number** — every one of its 8 leads is
`google/cpc`. The work order's open question "unexplained Google WCM number — do not use or change
until identified" is now **CLOSED by evidence**.

Paid calls are fragmented across **three** numbers (`...6354`, `...9517`, and forms with none),
and the mixed-source `...1456` takes more leads (17) than the approved paid number (11).

### CPQL — the decisive economic number

| Basis | Spend | Leads | Qualified | CPL | **CPQL** |
|---|---:|---:|---:|---:|---:|
| 90 settled days | $8,274.54 | 22 | 10 | $376.12 | **$827.45** |
| Sept 1–14 settled | $1,431.74 | 2 | 2 | $715.87 | $715.87 |

Provisional guardrails are **$150–$280**. Even under the most generous correction for click-ID loss
— assuming *every* unattributed organic/direct lead were really paid — CPQL would still be ≈$394,
above every guardrail.

**This reframes the whole recovery.** The account's problem is not only that the caps stopped
delivery. It is that at the delivery it *did* have, it was not clearing its guardrails. Raising bids
alone makes CPQL worse. The lever is lead capture and conversion rate first, bid second.

---

## Keyword Planner — independent confirmation of the bid diagnosis

10 of the 75 live Central Maryland targets, Google Search only.

| Keyword | Searches/mo | Competition | TOP-of-page LOW | TOP-of-page HIGH | Live ceiling |
|---|---:|---|---:|---:|---:|
| `hvac companies near me` | 480 | HIGH | $36.77 | $109.62 | — |
| `hvac near me` / `heating and cooling near me` | 320 | HIGH | $27.60 | $117.35 | — |
| **`ac repair near me`** / `air conditioner repair near me` | 320 | MEDIUM | **$38.98** | $118.07 | **$25** |
| `furnace repair near me` | 140 | **LOW** | — | — | — |
| **`hvac repair near me`** | 110 | HIGH | **$49.47** | $126.18 | **$25** |
| `hvac contractor near me` | 110 | MEDIUM | $12.68 | $80.00 | — |
| `hvac installers near me` | 10 | HIGH | — | — | $30 |
| `hvac replacement near me` | 10 | HIGH | — | — | $30 |
| `gas boiler repair` / `boiler repair near me` | 10 | LOW | — | — | $25 |
| **All commercial variants** | **10 or 0** | LOW/MED | — | — | $30 |

**The $25 ceiling is below Google's own LOW top-of-page estimate for both keywords it governs.**
For `hvac repair near me` the low estimate is $49.47 — very nearly double the cap. This is
third-party evidence, independent of the account's 13-conversion history, and it upgrades the
CPC-ceiling diagnosis from STRONGLY SUPPORTED to **PROVEN**.

Two more findings fall out:

- **Commercial demand is ~10 searches/month.** The commercial launch is a low-volume, high-value
  play. Expect a handful of impressions a month, not a volume recovery. Set expectations accordingly.
- **The HVAC Installation campaign targets a 10/mo keyword** (`hvac installers near me`) **and picks
  up a 480/mo generic query** (`hvac companies near me`) **as a side effect.** That is the routing
  problem, quantified.
- `furnace repair near me` — 140/mo at **LOW** competition — is unexploited BOFU demand that already
  appears in the search-term report.

*Synonyms share one volume bucket. These are per-bucket ceilings, not additive totals.*

---

## Negative reachability audit — **COMPLETED**

| Scope | Rows |
|---|---:|
| Campaign-level | 6,158 |
| Ad-group-level | 28 |
| Account-level (shared set `11252984411`) | 271 |
| Shared-set rows, **none attached to the five** | 6,932 → DUPLICATE_NO_EFFECT |
| **Active in scope** | **6,457** |

| Verdict | Count |
|---|---:|
| KEEP | 6,384 |
| HOLD | 61 |
| NARROW | 10 |
| REMOVE | 0 |
| NON_LATIN_UNEVALUATED | 1 |
| DUPLICATE_NO_EFFECT | 6,932 |

**Negatives blocking a live positive keyword: 0. Negatives blocking a converting search term in
their own scope: 0.**

Two corrections I made to my own analysis before reporting it:

1. A first pass reported one account negative blocking *everything*. The text is `뜻` — no ASCII
   token — so it tokenised to `[]`, and an empty set is a subset of every set. That was my
   tokeniser, not the account. It is now isolated as NON_LATIN_UNEVALUATED and needs a human look.
2. A first pass flagged EXACT `hvac ductwork installation near me` on HVAC **Replacement** for
   REMOVE because the term converted. The conversion happened in HVAC **Installation**. The
   negative is doing correct cross-campaign routing. Conversions are now scoped to the negative's
   own campaign, and the verdict is KEEP.

A bulk "stage-2 reachable conflict" count of 4,384 is **not** reported as a finding: it was produced
by appending each negative to a positive keyword, which matches by construction. It proves
theoretical reachability, not demand.

### What does matter — 6 campaign negatives block real commercial demand

37 genuine commercial buyer phrases tested. **26 clear, 11 blocked.**

| Negative | Criterion | Blocks | Verdict |
|---|---|---|---|
| **`rooftop` PHRASE** | `151698359` | `commercial hvac installation rooftop`, `…rooftop unit`, `rooftop commercial hvac installation` | **REMOVE** — the page's own H3 is "Rooftop and Packaged Units" and the snippet created today lists "Rooftop Units" |
| `licensed` PHRASE | `190023714` | 2 phrases | **REMOVE** — agency never-auto-negative list |
| `certified` PHRASE | `171200462` | 2 phrases | **REMOVE** — agency never-auto-negative list |
| `warehouse` PHRASE | `38170401` | 1 phrase | **REMOVE** — ordinary commercial property type |
| `store` PHRASE | `33316870` | 1 phrase | **REMOVE** — ordinary commercial property type |
| `industrial` PHRASE | `75327691` | 2 phrases | **HOLD** — the page says commercial, never industrial; capability unverified |

Also flagged, not actioned: `licensed` and `certified` exist on **all five** campaigns; 61 active
negatives touch capability words (`ventilation`, `combustion`, `hydronics`, `roof`, `duct clean*`,
`condensate pump`, `coil cleaner`, account-level BROAD `thermostat`); 4,025 active single-word
negatives; 1,323 cross-level duplicates.

---

## Query routing matrix — completed

| Family | Evidence | Currently | Should own | Action |
|---|---|---|---|---|
| Generic HVAC company/contractor | `hvac companies near me` $297.81/8clk/**0conv**; `hvac company near me` $59.92/1clk/**2conv**; 480/mo demand | HVAC Installation **and** AC Repair | **new generic BOFU ad group** | Build it. **Do not negative.** |
| Boiler | `boiler check up near me` $70.05, 0 conv | **HVAC Repair** ❌ | Gas Boiler Repair | routing negative + keyword |
| AC maintenance | `ac maintenance near me` $81.66, 0 conv | AC Repair **and** HVAC Repair | AC Repair | routing negative |
| Ductwork install | `hvac ductwork installation near me` $59.44, **1 conv** | Installation + Replacement | Installation | **already correctly routed** — keep the EXACT negative on Replacement |
| Furnace repair | 140/mo, LOW competition, appears in search terms | unowned | HVAC Repair | add Phrase + Exact |
| Commercial | 10/mo | new ad group | commercial ad group | **launching** |
| Unsupported | `hydronic radiant floor heating installers near me` $28.90 | HVAC Installation | none | verify capability first |

**33 terms appear in ≥2 campaigns.** Generic queries are **44.6% of settled-September spend**
(~$638 of $1,431.74) and produced 2 of 4 conversions.

The generic BOFU ad group is **not drafted** — per instruction it needs verified demand (now have
it: 480/mo), approved service scope, a suitable landing page (**does not exist**), and its own
service-specific work order. The landing page is the blocker.

---

## Sitelinks, logo, images

**Commercial sitelinks — DO NOT CREATE, confirmed.** The live page exposes exactly **one** in-page
anchor, `#quote-form`. Everything else matching `id=` is a Gravity Forms script tag. Google needs
four unique meaningful destinations; one exists. Privacy and Terms are not marketing sitelinks.
If LP-1 adds real section anchors (Commercial systems / Installation process / Why businesses
choose Ambient / Request a consultation), four become possible — that requirement is written into
`AMB-0915-LP-1`.

**Campaign sitelink leakage on 24132507747 — 4 ENABLED to the main site:** Customer Reviews
(`/reviews/`), View Our Work (`/our-work/`), Contact Ambient (`/contact-us/`), Service Areas
(`/service-areas/`). Four more point at other services' paid pages. **None points at the commercial
page.** Measured cost of the SITELINKS click type: **26 clicks, $1,284.80, 1 conversion** —
15.5% of spend. Not removed; that needs its own destructive approval and validated replacements.

**Business logo — MISSING CLIENT INPUT.** The removed asset `200223860974` is **32×32**, far below
Google's 1:1 ≥128×128 minimum; it was never a valid logo. The account holds 130 image assets
including 58 square candidates, but they are unnamed or labelled "Free stock image" and I cannot
identify the authentic Ambient mark or confirm usage rights from the API. **Needed:** the approved
logo file, ≥128×128 at 1:1 (and optionally ≥512×128 at 4:1), with confirmation it is Ambient's own
mark. No logo plan is drafted without it.

**Image assets — DO NOT CREATE, confirmed.** The four candidate images are the ones the live page
itself captions as *"without presenting them as completed Ambient projects."* Placing them beside
an Ambient ad would do exactly that.

---

## AC Repair challenger — superseded, and a correction

`AMB-0910-RSA-ACR-2 / 1F166DE17017` **does not recompute.** The on-disk plan hashes to
`4C7E73A3194D` and carries no `operation_count`. It is not approvable at its published fingerprint.

**Correction to my own first pass:** an automated scan flagged `licensed`, `insured`, `24/7`,
`emergency` and `financing` in that plan. Re-checked field by field — **all 19 headline and
description strings are clean**. The hits were in the plan's *prose*, in the note explaining the
Licensed & Insured claim was withdrawn. The copy was never affected.

Re-issued unchanged as **`AMB-0915-RSA-ACR-3`** with a fingerprint that verifies. AC Repair holds
2 ads; a third stays within Google's 3-RSA cap. Low priority — AC Repair cannot win auctions at $25,
so a new ad changes nothing until the bid question is settled.

---

## Consolidated approval block — fresh, validated, unexecuted only

| # | Plan | Fingerprint | Ops | Gate |
|---|---|---|---:|---|
| 1 | `AMB-0915-LP-1` — website remediation, all 10 defects | `5354E1E2F576` | 10 | **none — approve now** |
| 2 | `AMB-0915-CONV-1` — 10 Primary → 3, demote 7 | `981A790ACDBB` | 7 | after LP-1 deployed + 24/24 |
| 3 | `AMB-0915-COMM-NEGRM-1` — free 11 commercial buyer phrases | `C566F5CF579F` | 6 | after commercial ads enabled |
| 4 | `AMB-0915-CPC-HR-1` — HVAC Repair $25 → $65 | `14BD03817042` | 1 | after 24/24 + CONV-1 |
| 5 | `AMB-0915-RSA-ACR-3` — AC Repair challenger, paused | `1648D816ABAE` | 1 | none — low priority |

```
APPROVE AMB-0915-LP-1 5354E1E2F576 specification FOR ambientcoolingandheating.com
APPROVE AMB-0915-CONV-1 981A790ACDBB 7 operations FOR 2401959466
APPROVE DESTRUCTIVE AMB-0915-COMM-NEGRM-1 C566F5CF579F 6 operations FOR 2401959466
APPROVE AMB-0915-CPC-HR-1 14BD03817042 1 operations FOR 2401959466
APPROVE AMB-0915-RSA-ACR-3 1648D816ABAE 1 operations FOR 2401959466
```

### `AMB-0915-LP-1` — the one to approve first

Specification only. **This session cannot publish**: no website source, no WordPress or SiteGround
credential, no SFTP/SSH, no staging, no MCP server that reaches the site. That matches the
repository's existing developer-handoff precedent, whose status is also "NOT AUTHORIZED FOR
PRODUCTION DEPLOYMENT". Deployment needs staging evidence, a tested diff, a confirmed backup, a
rollback, and a **new** deployment fingerprint.

Covers **all ten** defects, not just the four blockers, and explicitly requires: the cache purge
**and** the client-side re-architecture (a purge alone lets the next visitor re-poison it);
first-party fallback with last-touch-wins; direct visits inheriting nothing; GBRAID/WBRAID/consent/
first-landing-URL capture; honeypot field 16 left alone; GTM, AW, GA4, WhatConverts, noindex,
Privacy and Terms all preserved.

### `AMB-0915-CPC-HR-1` — why $65, and the honest caveat

$65 sits between Google's own LOW ($49.47) and HIGH ($126.18) top-of-page estimates for
`hvac repair near me`. Budget stays $78.95, stop-loss $250 incremental with no verified qualified
lead, one campaign, one variable, rollback to 25000000 micros defined.

The caveat is written into the plan: **at a measured CPQL of $827 this is a delivery-and-measurement
test, not a profitability claim.** If volume returns at a CPQL still far above guardrail, the next
move is landing-page conversion rate, not more bid.

### Do not execute

`AMB-0910-COMM-RSA-2 41C183D15C93` · `AMB-0910-RSA-ACR-2 1F166DE17017` (does not recompute) ·
`AMB-0910-COMM-NEG-1 C4142D5D5DE0` · `AMB-0910-COMM-NEG-1-FULL A774B9C14896` ·
`AMB-0910-COMM-NEG-2 A9C9BCBDDD74` · `AMB-0910-RSA-ACR-1 19E2F2FFC311` ·
`AMB-0910-COMM-RSA-1 30312BC45992` · `AMB-0909C-CPC-INST-2 5D57E0EF3B70` ·
`AMB-0910-COMM-XNEG-1 A70260017DAD` (still gated — commercial route cannot serve)

---

## Status by category

**EXECUTED** — 2 commercial RSAs paused · 7 commercial asset associations paused · execution and
readback receipts written.

**VERIFIED** — identity 10/10 · readback 0 FAIL · 16/16 unrelated-resource checks · 17/17 commercial
negatives · serving chain proven incapable of serving · budgets $12,815.12 within $13,000 ·
`410-415-9517` identified as a Google call-forwarding number.

**COMPLETED** — WhatConverts reconciliation · negative reachability audit · query routing matrix ·
Keyword Planner · sitelink leakage quantified · AC Repair challenger revalidated and superseded ·
landing-page QA (10 defects) · conversion duplication map.

**AWAITING GOOGLE** — both RSAs and all 7 assets `REVIEW_IN_PROGRESS`. Typically within one business
day. **Enablement cannot be prepared until APPROVED.**

**AWAITING APPROVAL** — the five plans above.

**BLOCKED** —
- Commercial enablement: policy review + 4 P0 landing-page defects + 24/24 attribution.
- Residential routing negative `commercial`: commercial route must serve first. Correctly deferred.
- Website deployment: no credentials or staging exist in this environment.
- Generic BOFU ad group: no suitable landing page exists.
- Auction Insights: not exposed by the API for this account. **Access blocker documented** — needs a
  manual export from the Google Ads UI (Campaigns → Insights → Auction insights, campaign and
  ad-group level, last 30 days). I have no browser session for the Ads UI.
- Safe QA form submission: authorised by you, but it cannot verify the chain until LP-1 ships —
  submitting now would only prove the current broken behaviour and would write a real CRM record.
  It is scheduled as the LP-1 staging acceptance test using `GREEN MARKETING QA TEST` /
  `QA TEST - DO NOT CONTACT` / an `example.com` address / a reserved `202-555-01xx` number / a
  synthetic non-Google click id.

**MISSING CLIENT INPUT** — see table below.

---

## Missing business economics

| Value | Status | What it unblocks |
|---|---|---|
| Average job revenue | **MISSING** | ROAS, profit after ad spend, a real max CPC |
| Close rate % | **MISSING** | converting CPQL → CAC |
| Gross margin % | **MISSING** | gross-profit ROAS, true break-even bid |
| Target CPL / CPQL / CAC | **MISSING** | replaces the provisional $150–$280 guardrails |
| Sold-job revenue | **MISSING** — `sales_value` 0/294 in WhatConverts | any profitability verdict |
| Approved Ambient logo ≥128×128 1:1 | **MISSING** | business-logo asset |
| Industrial HVAC capability — yes/no | **MISSING** | the `industrial` negative HOLD verdict |
| Advertising-use rights for the 4 commercial images | **MISSING** | gallery populate-vs-remove |
| Auction Insights export | **MISSING** (no UI session) | competitive pressure analysis |

Until these arrive the provisional guardrails stand, and every CPQL figure in this report is an
upper bound.

---

## Monitoring

**Immediate** — done: readback 0 FAIL, serving chain proven inert.
**~24h and ~72h** — poll ad + asset policy status; confirm both RSAs still PAUSED and the ad group
has taken zero impressions. No delivery is possible, so these are integrity checks, not performance.
**14 settled days** — defined, and begins only when the commercial route actually serves. Report
qualified leads, CPQL, booked appointments, sold jobs, gross profit, profit after ad spend — never
Ad Strength, Quality Score or Optimization Score alone.

---

## Evidence

```
receipts/live/AMB-0915-EXECUTED-2026-09-15.json
receipts/live/AMB-0915-READBACK-2026-09-15.json
receipts/validate-only/AMB-0915-COMM-RSA-1-2026-09-15.json
clients/ambient-cooling-heating/plans/AMB-0915-{LP-1,CONV-1,COMM-NEGRM-1,CPC-HR-1,RSA-ACR-3}.json
clients/ambient-cooling-heating/snapshots/wc-reconciliation-2026-09-15.json
clients/ambient-cooling-heating/snapshots/wc-paid-analysis-2026-09-15.json
clients/ambient-cooling-heating/snapshots/negative-reachability-audit-2026-09-15.json
clients/ambient-cooling-heating/snapshots/commercial-negative-conflict-2026-09-15.json
clients/ambient-cooling-heating/snapshots/keyword-planner-2026-09-15.json
clients/ambient-cooling-heating/snapshots/gclid-capture-probe-2026-09-15.json
clients/ambient-cooling-heating/snapshots/misc-checks-2026-09-15.json
```

**External writes this session: 9 approved plan operations → 16 API resources**, in 3 atomic
mutates, all non-serving:

| Plan operations | API resources created |
|---|---|
| `AMB-0915-COMM-RSA-1` — 2 ops | 2 `ad_group_ad`, both PAUSED |
| `AMB-0915-COMM-ASSET-1` — 7 ops, each specified as *create asset **and** link PAUSED* | 7 `asset` + 7 `ad_group_asset`, every link PAUSED |

Plus 3 `validate_only` requests (nothing committed). Every other Google Ads call was read-only.
WhatConverts was read-only. No website, GTM, CRM, conversion, budget, bid, schedule, location,
keyword or negative was changed.
