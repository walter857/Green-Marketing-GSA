# Softwind Power Washing — P0 + P1 Master Change Plan

**STATUS: PLAN ONLY. NOT APPROVED. ZERO EXTERNAL CHANGES MADE.**

**Account:** Softwind Power Washing - Live · `152-172-5229` (`1521725229`)
**MCC:** `3373711342` Green Marketing · **Service:** Power Washing · **Vertical:** similar-local-service
**Approval owner:** Walter Correa · access@greenmarketing.com
**Built:** 2026-08-25 · **Fresh state re-read:** 2026-08-25 17:44:41 America/New_York

---

## 1. Drift check — is the plan built on current state?

A second full read-only snapshot was taken at **17:44:41**, 47 minutes after the audit
snapshot, and compared field by field.

| Check | Result |
|---|---|
| Account name / customer ID / manager / test flags | **PASS — exact match** |
| Campaign settings, budgets, bidding, CPC ceiling, networks, geo option | **0 drift** |
| Ad group statuses (30) | **0 drift** |
| Keyword rows, statuses, approvals (214) | **0 drift** |
| Ad statuses, approvals, Final URLs (54) | **0 drift** |
| Campaign criteria — schedule, geo, negatives (130) | **0 drift** |
| Conversion actions — status, primary_for_goal, counting (4) | **0 drift** |
| **Total configuration drift** | **ZERO** |

**Metric drift — expected, and one item worth naming.** Clicks and cost are unchanged
(6 clicks, $171.17). Impressions moved **107 → 103**, all of it campaign `24103511039` on
2026-08-25 (22 → 18). That is Google retroactively restating impressions as invalid-traffic
filtering catches up — the same retroactive-restatement behaviour already recorded for this
MCC's other accounts. It is not a data error and it does not change any recommendation.

**No material drift. The plan is built on current state.** Fresh figures are used
throughout; where they differ from the audit's 16:57 numbers, the fresher value wins.

---

## 2. What changed versus the audit — two corrections

Both were found while building the plan and both change a recommendation. Recording them
rather than quietly shipping the audit's version.

### Correction 1 — the CPC ceiling should be **$24.00**, not the audit's $22.00

The audit derived $22.00 from a **volume-weighted** top-of-page high of $23.91 computed
across all 49 BOFU buckets in the market. A fresh Keyword Planner read restricted to **the
twelve keyword texts this account actually runs** returns a higher figure: `power washing
near me` and `power washing company near me` — the two keywords that drive the account —
both show a top-of-page **high of $28.23**.

Decisive supporting evidence: in the post-cap-removal window the account **still loses 34.6%
and 33.3% of impression share to rank while completely uncapped.** It is not overwhelming
the auction even at $40 CPCs, so every dollar taken off the ceiling converts directly into
lost impressions in an account whose primary constraint is already too few impressions. And
the downside of setting this too low is proven *in this exact account*: the $5.00 ceiling of
2026-08-07 → 08-16 produced **twelve consecutive zero-click days**. Full reasoning in
`2026-08-25-plan-b-bidding.yaml` under `supersedes_audit_recommendation`.

### Correction 2 — the audit conflated two keyword texts

The audit called unpausing `House Washing Company Near Me` "the single fastest win", citing
40 local searches/month at $10.46–$32.09.

Those are **two different keyword texts**. The ad group contains exactly one text —
`house washing company near me` — which returns **no reportable local volume bucket**. The
40/month bucket belongs to `house washing near me`, which sits in the paused legacy
`Soft & House Washing` ad group alongside 13 other texts.

The unpause is still worth doing (zero build, dedicated well-matched page) but it is a **low
volume** action, not a headline one. The genuine 40/month demand is captured properly in
**PLAN-E** as a clean SKAG. Also corrected: an initial classifier flagged four ad groups
"LANDING PAGE NOT READY" — a false negative, because it only knew URLs belonging to *enabled*
ads. All four pages were then fetched in a real browser and every one returned **HTTP 200**
with the tracked phone, working forms and gclid preservation.

---

## 3. P0 findings and verdicts

### A · Conversion tracking — **UNVERIFIED, not proven broken** → PLAN-A

Zero conversions on **six clicks** proves nothing either way; at a 3–12% conversion rate the
expected lead count is 0.2–0.7. The API cannot separate "working, nothing yet" from "never
fires". PLAN-A resolves it in three gated stages: **Stage 1 read-only** (GTM Preview, UI tag
status, WhatConverts lead log, tag-ownership lookup) creates nothing; **Stage 2** is one
marked test form submission; **Stage 3** is one >60s test call. Stages 2 and 3 each need
their own approval and **must not run before Stage 1** — if Stage 1 shows the tags recording,
the client may avoid a live test entirely. **No conversion action is created or replaced.**

### B · Two campaigns — **DUPLICATIVE / CANNIBALIZING, 12/12 signals** → PLAN-G

Campaign `24145053510` is a byte-for-byte clone of `24103511039`: identical geo (8 targets),
schedule, all 47 negatives, conversion goals, bidding, budget amount, **100% keyword
inventory overlap**, all 15 ad group names present in both, and **10 shared asset IDs** —
the same asset objects linked to both campaigns, not copies.

**But the nuance matters.** The *enabled subsets* are largely complementary: campaign A runs
the six power-washing SKAGs, campaign B the six pressure/house/soft SKAGs. Exactly **one** ad
group is enabled in both. So the honest verdict is *duplicative structure carrying a mostly
complementary enabled subset with one genuine live collision*.

| | Campaign A `202870585430` | Campaign B `198082078783` |
|---|---:|---:|
| `Power Washing Services Near Me` | 51 impressions, 1 click, $22.13 | **1 impression, 0 clicks, $0** |

Campaign A wins that auction essentially always. **PLAN-G splits accordingly:** G-1 pauses
the one losing duplicate ad group (low risk, approvable now); **G-2 full consolidation is
DEFERRED to September and must NOT be approved yet** — it resets learning, and doing that
with six days left in an account chasing its first lead risks a delivery gap for a measured
harm of one impression. Surviving campaign would be `24103511039`. **Neither campaign is
paused by this plan set.**

### C · Landing-page / tracking defects → PLAN-F (website) + PLAN-H (Ads)

All re-verified in a real browser today. The authoring instruction is **still live** on the
page carrying 64% of spend; the countdown is present on **all nine** offer pages including
the three paused-SKAG pages; all **eight** sitelinks point at pages showing the untracked
**(631) 502-5402**.

**A judgement call worth stating:** the main-site number is probably *not* an error.
`softwindli.com` is branded *Softwind Landscape & Masonry* — the parent business — and
(631) 502-5402 is most likely its legitimate main line while (631) 502-7946 is a dedicated
campaign tracking number. **The defect is not the number; it is that paid traffic is being
sent to pages where a resulting call is invisible.** That is fixed more cheaply and safely
on the Ads side (PLAN-H) than by rebuilding the site's phone handling.

### D · `Local actions - Directions` primary_for_goal — **CURRENTLY CONTAINED** → no action

Re-verified fresh: still `primary_for_goal: true` at account level with `MANY_PER_CLICK`
counting. **But both campaigns override with campaign-specific goals**, and the biddable set
on each is exactly the three lead categories — GET_DIRECTIONS is present in the goal table
and **not biddable** on either campaign.

**Classification: CURRENTLY CONTAINED, ACCOUNT-LEVEL MEASUREMENT RISK.**

**Deliberately NOT demoted in this plan set.** `conversion_action.primary_for_goal` is an
**account-level** field. Changing it would alter the default goal set for *any* campaign that
does not override it — and while the only two campaigns in this account both override today,
that is a property of current configuration, not a guarantee. The instruction is explicit:
demote only if the change affects no other campaign and the exact impact is inventoried. It
is contained, so the correct action now is **none**, with a standing note that any new
campaign must be created with campaign-specific goals. Recommended as a **separate work order
item**, not folded in here.

### E · Foreign tag `AW-17878095007` — **INVESTIGATE, DO NOT REMOVE** → PLAN-A P0-A04 + PLAN-F F-3

| Tag | Owner | Status |
|---|---|---|
| `AW-18369652705` | **This account** — matches `conversion_tracking_id` for `1521725229` | Confirmed |
| `AW-17878095007` | **UNKNOWN** | Present on **9 of 9** offer pages |

Site-wide on the offer subdomain, not one page. **No tag removal is proposed.** Removing it
blind could break a previous agency's or the client's own separate account. Ownership must be
established first — MCC `3373711342` account list, then the client.

---

## 4. P1 findings and verdicts

| Item | Verdict | Plan |
|---|---|---|
| **CPC control** | $24.00 ceiling, superseding the audit's $22.00 | PLAN-B |
| **Ad schedule** | Campaign 24/7 for form capture; **call-asset hours held out** | PLAN-C |
| **Unpause existing SKAG** | `House Washing Company Near Me` in campaign B only — 1 mutation | PLAN-D |
| **Other paused BOFU inventory** | 14 ad groups / 54 texts reviewed. **10 DUPLICATE, 3 KEEP PAUSED, 1 LOW VOLUME.** None else enabled | PLAN-D |
| **New SKAGs** | Only 2, both genuinely uncovered | PLAN-E |
| **Service area** | **NOT expanded.** Opportunity quantified only | §7 below |

### Paused inventory — why almost nothing is being switched on

The keyword inventory is byte-identical across both campaigns, so **every paused ad group
exists twice** and exactly one copy of each revamp SKAG is already enabled. Enabling a second
copy would put two ad groups in two campaigns into one auction — the precise cannibalisation
this plan set exists to remove.

The three legacy multi-intent containers hold real demand but are the wrong shape:

| Legacy ad group | Best demand | Why still paused |
|---|---|---|
| `Pressure & Power Washing` | `power washing service` 70/mo · `pressure washing service` 70/mo · long-island variants 40/mo | 17 texts in one ad group, **one RSA** against the two-RSA SOP (POOR strength in campaign A), one generic page with no city names, and its texts collide by close variant with campaign A's live power-washing SKAGs |
| `Soft & House Washing` | `house washing near me` **40/mo at $10.46–$32.09** | 14 texts, one RSA, points at the generic `/power-washing-soft-washing/` rather than the far better `/house-washing-company/` |
| `Driveway Patio Concrete Washing` | `patio cleaning service` 10/mo | 12 texts, none reaching meaningful volume; surfaces already covered by two live SKAGs |

**The right answer is extraction, not wholesale enablement** — which is exactly what PLAN-E
does for the one text worth having.

### New SKAGs — two, not fourteen

| SKAG | Keyword | Local demand | Why not already covered |
|---|---|---|---|
| **Pressure Washing Near Me** | `pressure washing near me` P+E | **70/mo, $8.75–$24.53** | No live or paused keyword contains this text. Phrase `"pressure washing service"` does not match a query lacking "service". |
| **House Washing Near Me** | `house washing near me` P+E | **40/mo, $10.46–$32.09** | The text *does* exist in paused inventory — badly contained. Extraction into a clean SKAG on the right page is the alternative to enabling a rejected container. |

The pressure-washing gap is not theoretical: **"pressure wash" phrasing has produced 15
impressions and ZERO clicks — 0% CTR — while "power wash" phrasing runs 7.25%.** Eleven of
those fifteen were served by a power-washing ad group. A copy-match failure, not just a
coverage gap.

**Rejected:** `pressure washing services near me` and `pressure washing company near me`
(defer — too close to SKAG 1 for a 26-impression/day pool); `paver cleaning near me` (in
scope as *cleaning*, but paver *sealing* is out of scope and the term family is contaminated
with chemical-product intent — needs a SERP check); the generic `power washing` 480/mo and
`pressure washing` 260/mo heads (low top-of-page bids of $0.57 and $0.30 expose heavy
equipment contamination; `power washing` produced 14 impressions and 0 clicks in this
account); all equipment, rental and retail terms.

---

## 5. Cross-campaign safety check

Required for every proposed enablement. **No proposal puts the two campaigns into the same
auction.**

| Proposal | Campaign A coverage | Campaign B coverage | Enabled dup? | Paused dup? | Search-term overlap | LP overlap | Ownership |
|---|---|---|---|---|---|---|---|
| `house washing company near me` (PLAN-D) | Paused `202870585910` — **stays paused** | Paused `198082079463` — **enable this one** | No | Yes | None with any live SKAG | `/house-washing-company/` unused by any live ad group | **B, exclusive** |
| `pressure washing near me` (PLAN-E) | None | None | No | No | Currently routes into A's `Power Washing Services Near Me` at **0% CTR** — A will lose those, intended | `/residential-pressure-washing/` shared **intra-campaign** with B's live Residential SKAG | **B, exclusive** |
| `house washing near me` (PLAN-E) | Paused inside legacy — **stays paused** | Paused inside legacy — **stays paused** | No | Yes | `house exterior power washing` (2 impr, 0 clicks) in A | `/house-washing-company/` shared **intra-campaign** with PLAN-D | **B, exclusive** |
| `Power Washing Services Near Me` (PLAN-G) | `202870585430` — **51 impr, keep** | `198082078783` — **1 impr, pause** | **YES — the one collision** | — | `power washing services near me` seen by both | Same page in both | **A, exclusive** |

Intra-campaign page sharing is fine — Google resolves one auction by Ad Rank within a
campaign. Cross-campaign competition is what must be avoided, and after PLAN-G there is none.

---

## 6. The seven plans, separated by approval type

| Plan | Title | Type | Fingerprint | Actions | Objects | Ads mutations |
|---|---|---|---|---|---:|---:|
| **PLAN-A** | Conversion tracking verification protocol | MEASUREMENT_AND_TESTING | `701E8E5ED639` | 6 | 6 | **0** |
| **PLAN-B** | Max CPC bid limit, both campaigns | BIDDING | `F80E8D398811` | 2 | 2 | 2 |
| **PLAN-C** | Campaign ad schedule to 24/7 | DELIVERY_SCHEDULE | `9E18503B5BEA` | 4 | 26 | 26 |
| **PLAN-D** | Enable House Washing Company Near Me | ENABLE_EXISTING_RESOURCES | `F61C9F287B82` | 1 | 1 | 1 |
| **PLAN-E** | Create paused — 2 SKAGs + 3 negatives | CREATE_PAUSED | `F453AD249497` | 8 | 16 | 16 |
| **PLAN-F** | Landing page / website fixes | WEBSITE — **no Ads fingerprint** | — | 5 items | — | **0** |
| **PLAN-G** | Pause duplicate ad group; defer consolidation | CAMPAIGN_STRUCTURE | `EC35724753AE` | 1 | 1 | 1 |
| **PLAN-H** | Sitelink destinations to tracked pages | ASSETS | `1D63EC1EB68D` | 5 | 21 | 21 |
| | | | **TOTAL** | **27** | **73** | **67** |

**Approval phrase format:** `APPROVE <PLAN-ID> <FINGERPRINT> FOR 1521725229`

**A fingerprint identifies an exact plan. It does not grant permission.** Every plan is
`approval_status: NOT APPROVED` / `execution_status: DO NOT EXECUTE`.

### Deviation from the requested file list, flagged

The requested list put landing-page work in PLAN-F as markdown. **Repointing a sitelink is a
Google Ads asset change, not a website change**, and the instruction is explicit that website
fixes must be separated from Ads fingerprints. Bundling it into PLAN-F would have put an Ads
mutation inside a website plan; dropping it would have lost the finding. It therefore gets
its own file, **`2026-08-25-plan-h-sitelink-destinations.yaml`**, with its own fingerprint.
PLAN-F covers the website side only and carries no fingerprint.

---

## 7. Service area — opportunity only, NOT in any executable plan

**No geo change is proposed. The verified service area remains UNKNOWN.**

The campaigns target 8 fragmented locations across two counties. Critically, **"Islip" is
targeted as the hamlet (`1023035`, roughly 18,000 people), not the Town of Islip (roughly
340,000).** Dix Hills is targeted as an isolated point inside the Town of Huntington;
Syosset likewise inside Oyster Bay.

| If the client confirms | Rough population added | Effect on the demand ceiling |
|---|---|---|
| Town of Islip (beyond the hamlet) | ~320,000 | Largest single lever available |
| Town of Huntington (beyond Dix Hills) | ~180,000 | Large |
| Town of Oyster Bay (beyond Syosset) | ~275,000 | Large |
| Town of Hempstead (beyond Bellmore/Salisbury) | ~760,000 | Very large, but likely beyond a realistic drive radius |

Local BOFU demand across the current 8 targets is roughly **800 searches/month (~26/day)**.
Demand scales broadly with covered population, so confirming even the Town of Islip alone
could multiply the addressable pool several times over. **This is the only lever that
materially changes the demand ceiling — and it cannot be pulled from this desk.** It needs
one verified answer: *which towns does Softwind actually serve for power washing?*

Delivery integrity is confirmed clean: `user_location_view.targeting_location` is `true` on
**every** row. Zero out-of-area leakage today.

---

## 8. Fresh impact model

Baseline re-read 2026-08-25 17:44: **103 impressions, 6 clicks, $171.17, 0 conversions**;
CTR 5.83%; CPC $28.53; recent reach 23.5 impressions/day.

| Scenario | Impr/day | CTR | Clicks/day | CPC | Spend/day | **Aug total** | % of $2,500 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **CURRENT** — nothing approved | 23.5 | 5.83% | 1.37 | $28.53 | $39.05 | **$405.49** | 16.2% |
| **P0 ONLY** — A + B | 22.8 | 5.83% | 1.33 | $20.00 | $26.56 | **$330.51** | 13.2% |
| **P0+P1 CONSERVATIVE** | 31.7 | 6.00% | 1.90 | $20.00 | $38.07 | **$399.59** | 16.0% |
| **P0+P1 BASE** | 35.2 | 8.00% | 2.82 | $19.00 | $53.58 | **$492.65** | 19.7% |
| **P0+P1 HIGH** — PLAN-E live ~08-28 | 44.1 | 10.00% | 4.41 | $18.00 | $79.31 | **$488.42** | 19.5% |

**Lead probability** (low 3% / base 7% / high 12% CVR — industry ranges, **LOW confidence**,
the account has never produced a lead):

| Scenario | Clicks left | P(≥1 lead) |
|---|---:|---|
| CURRENT | 8.2 | 22% / **45%** / 65% |
| P0 ONLY | 8.0 | 22% / **44%** / 64% |
| P0+P1 CONSERVATIVE | 11.4 | 29% / **56%** / 77% |
| P0+P1 BASE | 16.9 | 40% / **71%** / 88% |
| P0+P1 HIGH | 17.6 | 42% / **72%** / 90% |

**Two results worth reading carefully rather than skimming:**

1. **P0 ONLY spends LESS than doing nothing** ($330 vs $405). The CPC ceiling is the single
   most valuable technical action in this set and it moves the spend number the wrong way. It
   buys roughly the same clicks for $8.53 less each. Where the spend goal and the client's
   interest conflict, these plans choose the client's interest.
2. **HIGH projects slightly less total August spend than BASE** ($488 vs $493) despite higher
   daily spend — because PLAN-E is created *paused* and needs readback QA plus a second enable
   approval, so it can realistically serve for only about 4 of the 6 remaining days. That is
   the create-paused gate working as designed, not a modelling error.

### Spend-goal verdict

**$2,500 IS NOT A DEFENSIBLE QUALIFIED-SEARCH SPEND TARGET FOR THE REMAINING PERIOD.**

| | |
|---|---:|
| Goal | $2,500.00 |
| Highest projected with every P0 and P1 plan executed | **$492.65** |
| Shortfall | **$2,007.35** |
| Share of goal achieved | **19.7%** |

Unchanged from the audit's conclusion, and now tested against a second independent data pull.
Reaching $2,500 would require Broad Match, Search Partners, Display, Performance Max,
equipment and DIY traffic, or unverified geography — every one prohibited by Green Marketing
policy or unsupported by verified client facts. **Recommended August target: $400–$500,
judged on cost per qualified lead.**

---

## 9. Consolidated change counts

| | A | B | C | D | E | F | G | H | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Campaigns changed | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | **4** |
| Campaigns paused | 0 | 0 | 0 | 0 | 0 | 0 | **0** | 0 | **0** |
| Budgets changed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| Bidding settings changed | 0 | **2** | 0 | 0 | 0 | 0 | 0 | 0 | **2** |
| Ad schedules changed | 0 | 0 | **2** | 0 | 0 | 0 | 0 | 0 | **2** |
| Ad schedule criteria removed | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | **12** |
| Ad schedule criteria created | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | **14** |
| Ad groups enabled | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | **1** |
| Ad groups paused | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | **1** |
| Ad groups created paused | 0 | 0 | 0 | 0 | **2** | 0 | 0 | 0 | **2** |
| Keywords enabled | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| Keywords created paused | 0 | 0 | 0 | 0 | **4** | 0 | 0 | 0 | **4** |
| RSAs created paused | 0 | 0 | 0 | 0 | **4** | 0 | 0 | 0 | **4** |
| Ads changed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| Negatives added | 0 | 0 | 0 | 0 | **6** | 0 | 0 | 0 | **6** |
| Assets created | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **4** | **4** |
| Asset links created | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **8** | **8** |
| Asset links removed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **9** | **9** |
| Assets deleted | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **0** |
| Final URLs changed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| Conversion actions changed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| **Google Ads mutations** | **0** | **2** | **26** | **1** | **16** | **0** | **1** | **21** | **67** |
| Website edits | 0 | 0 | 0 | 0 | 0 | **2** | 0 | 0 | **2** |
| External test artifacts | **2** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** |

**Zero campaigns paused. Zero budgets changed. Zero conversion actions changed. Zero Final
URLs changed on any existing ad. Zero assets deleted.**

---

## 10. What is explicitly excluded

Not present anywhere in any plan: **Broad Match · Search Partners · Display · Performance Max
· Demand Gen · AI Max · DSA · Final URL expansion · automatic text customization · unverified
towns · roof cleaning · gutter cleaning · paver sealing · landscaping · party rentals ·
shrink wrapping · equipment traffic · DIY traffic.**

Nothing was added to reach $2,500. The plan set projects **19.7%** of that goal and says so.

Also deliberately excluded: no budget increase (lost IS budget is 2.5% and 0%); no Smart
Bidding migration (zero conversions, tracking unverified); no bid modifiers of any kind; no
demotion of the account-level Directions goal (contained — separate work order); no tag
removal (ownership unknown); no RSA rewrite of existing ads (real P2, out of P0/P1 scope).

---

## 11. Blocked on missing confirmation

| Blocked item | Blocking question | Effect |
|---|---|---|
| **PLAN-C C-2** call-asset hours | Is (631) 502-7946 answered outside Mon–Fri 08:00–18:00? Saturday? Callback commitment for a 21:00 Sunday form lead? | Held **out of the fingerprint**. C-1 proceeds; the call asset stays unscheduled. |
| **PLAN-A Stage 2/3** | Client test name, phone, email; client notified; agreed call window | Cannot run. Stage 1 may make them unnecessary. |
| **PLAN-F F-2** countdown | Is it tied to a real, dated offer? | If no, removal is the only defensible option. |
| **PLAN-F F-3 / PLAN-A P0-A04** | Who owns Google Ads `17878095007`? | No tag removal until answered. |
| **Service area** | Which towns does Softwind actually serve? | Excluded from every executable plan. Only lever that changes the demand ceiling. |
| **Conversion values** | Average job revenue, gross margin, close rate | All leads valued $0.00; ROAS and profit reporting impossible. Not in P0/P1. |
| **$2,500** | Performance target or contractual commitment? | Determines re-scope to ~$490 versus rolling the balance to September. |

---

## 12. Recommended approval sequence

| Order | Plan | Why here | Risk |
|---|---|---|---|
| 1 | **PLAN-A Stage 1** | Read-only, creates nothing, needs no Ads mutation, and everything about measurement depends on it | None |
| 2 | **PLAN-B** | Stops the bleeding. Highest cost-efficiency gain in the set. Reversible in one field | LOW–MED |
| 3 | **PLAN-C C-1** | Largest single source of extra qualified impressions (+50% reach) and recovers Sunday 08-30 | LOW |
| 4 | **PLAN-G G-1** | Removes the only cross-campaign collision at effectively zero cost. Must precede enablement work | LOW |
| 5 | **PLAN-H** | Stops the next $40 click landing on an untracked page. Link-only, no asset deleted | LOW |
| 6 | **PLAN-D** | Zero-build enable, but low volume — worth doing after the higher-leverage items | LOW–MED |
| 7 | **PLAN-E** | Create-paused only; needs readback QA plus a second enable approval before it delivers | LOW to create |
| 8 | **PLAN-F F-1** | Free, zero risk, sits on 64% of spend — but a website change on a different track | None |
| — | **PLAN-G G-2** | **DO NOT APPROVE YET.** September, after August reporting closes | HIGH now |

---

**NOT APPROVED · DO NOT EXECUTE · ZERO EXTERNAL CHANGES MADE**
