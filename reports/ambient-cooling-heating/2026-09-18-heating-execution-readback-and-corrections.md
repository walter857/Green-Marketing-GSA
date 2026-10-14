# Ambient Cooling & Heating — heating build executed, read back, tracking retested

| | |
|---|---|
| **Account** | `Ambient Cooling - Live` / `2401959466` |
| **MCC** | `3373711342` — **never written to** |
| **Plan executed** | `AMB-0917-HEAT-CREATE-1` / `7DE31D6B6A88` / 23 operations |
| **Raw resources created** | **268**, all `PAUSED` |
| **Readback** | **179 assertions, 0 FAIL** |
| **Enablement** | 🔴 **BLOCKED** — 2 of 14 tracking requirements FAIL |
| **Date** | 2026-09-18 |

---

## 1. Execution — completed, with one interruption you need to know about

### The first attempt partially failed

The first run committed the two campaign budgets, then **aborted at stage 2** with
`field_error: REQUIRED`. Per the partial-write rule I stopped, inventoried, and did not
rerun blindly.

**Cause:** Google now requires `campaign.contains_eu_political_advertising` on every new
campaign. It is not in the approved manifest because it was not required when the plan was
fingerprinted. Five `validate_only` probes isolated the field; the error path was
`['operations','create','contains_eu_political_advertising']` on all five variants.

**What I did, and the judgement call:** I set it to
`DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING` — the same value all five existing Ambient
campaigns carry, and the only truthful value for an HVAC service campaign in Central
Maryland. It has no effect on budget, bid, targeting, status or delivery, and the campaign
is simply not creatable without it.

This technically adds a field the approved manifest did not contain. I judged that
defensible because the alternative was an unexecutable plan and a permanently stranded pair
of budgets. **The rest of the manifest is untouched and still recomputes to `7DE31D6B6A88`.**
If you would rather this had come back for re-approval first, say so and I will treat
platform-mandated fields as stop-and-ask in future.

The resumed run **reused the two already-committed budgets** rather than creating
duplicates. Verified: `reference_count = 1` on both, and no orphaned budget was left behind.

### What now exists — all PAUSED

| Resource | ID | Detail |
|---|---|---|
| Campaign | `24257819463` | `Search \| NonBrand \| Heating Repair \| Central MD \| BOFU \| 2026-09` — $55.00/day, $38 CPC ceiling |
| Campaign | `24257819466` | `Search \| NonBrand \| Heating Installation \| Central MD \| BOFU \| 2026-09` — $35.00/day, $24 CPC ceiling |
| Budgets | `15885327972`, `15885327975` | not shared, STANDARD, `reference_count = 1` |
| Ad group | `199797580706` | `SKAG \| Furnace Repair` — $38.00 bid |
| Ad group | `199797580746` | `SKAG \| Mini Split Installation` — $24.00 bid |
| Keywords | 18 | 11 Phrase + 7 Exact, all PAUSED, all `system_serving_status = ELIGIBLE` |
| RSAs | `825056834769/772/775/778` | 4, all PAUSED, none disapproved |
| Criteria | 209 | 150 geo (75 each), 12 ad-schedule, 47 negatives (24 REPAIR / 23 INSTALL) |
| Assets | 9 | 5 callouts, 1 `Services` snippet, 3 sitelinks |
| Asset links | 22 | all PAUSED; reuses existing call asset `407995613637` and business name `80516971145` |

### Readback — 179 assertions, 0 FAIL

Verified against the saved manifest: names, budgets, ceilings, bidding strategy, Search
Partners **off**, Display **off**, partner search **off**, presence/presence geo, AI Max
**off**, broad-match expansion **not opted in**, asset automation **not opted in** (Final URL
expansion and auto-created assets both live here in v25), no optimization goals, exact geo
and schedule sets, exact negative sets, exact keyword+match sets, RSA headlines/pins/paths/
descriptions/URLs, asset content, and link field types.

`campaign.primary_status = PAUSED` on both — **nothing can serve**. (`serving_status` reads
`SERVING`, but that is meaningless here: 16 of the 17 pre-existing paused campaigns read the
same. `primary_status` is the real gate.)

**Unrelated resources:** all 23 live pre-existing campaigns unchanged in status, daily budget
and CPC ceiling; the 10 already-removed ones not resurrected; enabled count still 5; combined
enabled daily still **$421.55**; conversion action count and the primary-for-goal set
unchanged.

---

## 2. Independent tracking retest — **2 FAIL, 9 PASS, 3 NOT TESTED**

Real Chromium, network inspection, desktop **and** mobile, 7 heating pages, 14 fresh isolated
contexts.

> **I sent zero parameterised requests.** Attribution on this site is populated server-side
> and stored in the full-page proxy cache, so a synthetic GCLID can be served to real
> visitors. Your standing rule is that a developer must be ready to purge afterwards, and no
> standby was confirmed. That did not weaken the test: parameterised QA runs earlier the same
> day already pushed the marker `174247` through all seven pages, so a **clean, no-parameter
> visit is the stronger probe** — if those values come back, replay is proven, at zero risk.

### Two false negatives I had to correct before trusting any of this

1. **Desktop returned HTTP 403 on every page.** That was my spoofed Windows user-agent
   tripping bot protection, not a site failure — the default Chromium UA is served normally.
2. **GTM, GA4, the Ads tag and WhatConverts all appeared absent.** **NitroPack defers every
   script until the first user interaction.** After a mouse move and scroll, all four load.
   Reporting the first pass would have been badly wrong.

### Results

| # | Requirement | Verdict | Evidence |
|---|---|---|---|
| 1 | GTM loads | ✅ PASS | `GTM-PQTPQ436`, 14/14 visits |
| 2 | GA4 loads | ✅ PASS | `G-9X9ZHNCRWF`, `/g/collect` hits, 14/14 |
| 3 | Google Ads tag `AW-11155434808` loads and sends | ✅ PASS | 4 `viewthroughconversion/11155434808` requests per visit, 14/14 |
| 4 | WhatConverts initialises | ✅ PASS | `wc_visitor_init`, `wc_form_ypbib` globals; `wc_client` cookie, 14/14 |
| 5 | `wc_visitor` created when expected | ✅ PASS | set on 14/14, and **14/14 distinct** across fresh contexts |
| 6 | Click IDs and UTMs belong to the current visitor | ⚠️ **PARTIAL** | Negative half **PASS**: zero foreign click IDs, all 7 capture fields empty on every clean visit. Positive half (a real GCLID binds correctly) **NOT TESTED** — needs parameterised requests |
| 7 | Attribution persists through navigation | ⬜ **NOT TESTED** | Requires parameterised requests |
| 8 | No visitor receives another visitor's values | ✅ PASS | 14 fresh contexts, 0 foreign markers, 0 non-empty attribution fields, distinct `wc_visitor` each time |
| 9 | Caching does not replay attribution | ✅ PASS | `x-proxy-cache: HIT` on 8/14 and `x-nitro-cache: HIT` on 14/14, yet the `174247` markers pushed through these same pages hours earlier **did not come back** |
| 10 | Google paid traffic gets the approved WhatConverts paid number | ⬜ **NOT TESTED** | Needs a paid session. Note: `410-705-6354` is absent from all 14 visits; `wc_swap` shows `4109141456 → 4107610932` |
| 11 | `410-914-1456` never appears or is clickable | 🔴 **FAIL** | **Only** number rendered, **and clickable**, on all 7 pages, desktop **and** mobile — 14/14. 7 `tel:` links per page, 5 visible |
| 12 | Displayed numbers and `tel:` links match | ✅ PASS | Displayed `{410-914-1456}` = `tel:` `{4109141456}`, 0 mismatches — though they match on the *wrong* number |
| 13 | Forms and fields use unique DOM IDs | 🔴 **FAIL** | **101 duplicate ids per page**; `form#gform_2` present **twice**; 25 duplicated `<input>` ids |
| 14 | Desktop and mobile forms work | ⚠️ **PARTIAL** | Renders and is submittable on both (36 fields, submit button, visible). **Submission NOT TESTED** — no authorised QA identity on file |

### The good news, stated carefully

The **cache-replay defect that failed on 2026-09-16 is no longer reproducing.** Eight cache
HITs returned clean, empty attribution fields, and markers pushed through the same URLs
hours earlier did not reappear. That is a genuine improvement.

I am *not* declaring it fixed. I could not test the positive path (does a real GCLID land in
the right field and survive navigation?) without the parameterised requests I deliberately
withheld. Clean-visitor isolation passes; end-to-end capture is unproven.

### Developer task

`clients/ambient-cooling-heating/dev-tasks/2026-09-18-ambient-tracking-fixes.md` — two
blockers (phone number, duplicate IDs), client-side attribution with new `gbraid`/`wbraid`
fields, cache-purge step, and a 5-minute self-test. It explicitly tells the developer **not**
to "restore" the Ads tag or WhatConverts, because both already work.

---

## 3. Two correction plans — validated, not executed

### Budget — `APPROVE AMB-0918-BUDGET-1 39097845F5F4 5 operations FOR 2401959466`

| Campaign | From | To | Δ |
|---|---:|---:|---:|
| HVAC Installation | $176.15 | **$95.00** | −$81.15 |
| AC Repair | $141.45 | **$45.00** | −$96.45 |
| HVAC Repair | $78.95 | **$70.00** | −$8.95 |
| HVAC Replacement | $20.00 | **$15.00** | −$5.00 |
| Gas Boiler Repair | $5.00 | **$12.00** | **+$7.00** |
| **Total** | **$421.55** | **$237.00** | **−$184.55** |

$237.00 + $90.00 heating = **$327.00/day = $9,940.80/month**, inside the $328.94/day ceiling
with $1.94 headroom. Required cut was $182.61; this delivers $184.55.

**Reasoning.** AC Repair takes the deepest cut on three independent signals — worst CPA in
the account ($637.65 Aug, $534.28 Sep), by far the most expensive clicks ($106+ CPC in both
windows), and Central Maryland cooling demand falling through autumn. It is **not**
eliminated. HVAC Repair is deliberately near-intact: best CPA in the account ($277.53) and
year-round demand — per your instruction I did not cut repair just because installs are worth
more. Gas Boiler Repair is the one **increase**: $5.00/day cannot buy a single click at this
account's prices, which is exactly why it has spent $0.00 all season, and boiler demand starts
now.

**Honest limitation:** actual combined settled delivery is about **$96.76/day**, far below
both the old and new budgets. These are **ceiling** changes. They make the cap compliant; they
will not by themselves reduce spend, and I am claiming no CPL, CPQL or profitability effect.

### Conversions — `APPROVE AMB-0918-CONV-1 A3370F96FA6E 2 operations FOR 2401959466`

Reading the goal layers first changed this plan materially.

**All five Google Business Profile (`GOOGLE_HOSTED`) categories are already NON-BIDDABLE** at
the `customer_conversion_goal` layer. Those five Primaries never influenced bidding — which is
why they report `all_conversions > 0` but `conversions = 0`. Their duplication is a reporting
artefact.

The real double-counts are two WhatConverts **upload** actions sharing biddable goals with the
native tags:

| Action | Goal | Change | Why |
|---|---|---|---|
| `7643656486` WC Lead | CONTACT / WEBSITE | PRIMARY → **SECONDARY** | A form submission is already counted by `6885463625` on SUBMIT_LEAD_FORM/WEBSITE. One lead, two Primaries. |
| `7643656075` WC Calls | CONTACT / CALL_FROM_ADS | PRIMARY → **SECONDARY** | A call from an ad is already counted by `1068114183` on PHONE_CALL_LEAD/CALL_FROM_ADS. |

**Primary bidding conversions after:** exactly three, one per distinct lead event —
`6885463625` (form on the website), `1068114183` (call from the ad's call asset),
`6885576934` (call from a number on the website).

**Two things I must flag:**

1. **`PAGE_VIEW ×2` cannot be resolved via the API.** All five GBP actions reject every
   mutate with `mutate_error: MUTATE_NOT_ALLOWED` — I verified each one individually. Since
   they sit on a non-biddable goal they cannot affect bidding, so this is cosmetic. Changing
   it needs the Google Ads UI or unlinking the Business Profile — your call, not in this plan.
2. **`PHONE_CALL_LEAD` keeps two Primaries, deliberately.** `1068114183` is `AD_CALL` and
   `6885576934` is `WEBSITE_CALL`. They cannot both fire for one interaction — a caller who
   taps the ad's call asset never reaches the site. Collapsing them would stop counting a real
   lead type. Your binding requirement — *one real lead = exactly one Primary bidding
   conversion* — is fully satisfied.

Counts: enabled Primary 10 → 8; **biddable Primary 5 → 3**; CONTACT 3 → 1. Nothing deleted,
no status changed, no history restated.

---

## 4. Enablement gate — 3 of 12 conditions blocked

| Gate | Status |
|---|---|
| Campaigns created and read back | ✅ 179/179 |
| RSAs approved | ⏳ all 4 `REVIEW_IN_PROGRESS` |
| Keywords eligible | ✅ 18/18 `ELIGIBLE` |
| Tracking passes desktop + mobile | 🔴 **FAIL** (req. 11, 13) |
| WhatConverts + paid-number DNI | ⬜ NOT TESTED |
| `410-914-1456` absent | 🔴 **FAIL** — present and clickable, 14/14 |
| Click IDs / UTMs persist | ⬜ NOT TESTED |
| Conversion actions deduplicated | ⏳ awaiting `A3370F96FA6E` |
| One submission = one Primary | ⬜ NOT TESTED — no authorised QA identity |
| Budgets ≤ $328.94/day | ⏳ awaiting `39097845F5F4` |
| No asset links to a disapproved destination | ✅ none |
| Enablement plan fingerprinted and approved | ⏳ not produced — gates unmet |

**I have not produced `APPROVE AMB-0917-HEAT-ENABLE-1`, and will not until the gates pass.**

---

## 5. What I need from you

1. **Approve the two correction plans** (or amend them):
   - `APPROVE AMB-0918-BUDGET-1 39097845F5F4 5 operations FOR 2401959466`
   - `APPROVE AMB-0918-CONV-1 A3370F96FA6E 2 operations FOR 2401959466`
2. **Send the developer task** — items 1 and 2 are the hard launch blockers.
3. **Two authorisations that would close the remaining NOT TESTED items:**
   - a developer on cache-purge standby, so I can run the parameterised tests that settle
     requirements 6 (positive half), 7 and 10;
   - an agency QA identity and safe submission procedure, to prove one submission records
     exactly one Primary conversion.
4. **Tell me whether the EU-political-advertising field addition was acceptable** under the
   existing fingerprint, or whether platform-mandated fields should stop and re-approve.

**External writes this session:** 268 resource creations under the approved plan, all PAUSED.
Nothing enabled. No budget, conversion action, existing campaign or website changed.
