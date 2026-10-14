# 07 — Conversion and Tracking Audit

**Pro Green - Austin - Live | 7380491929 | outdoor design & build | 2026-08-18**
**READ mode. No form was submitted, no call was placed, no test lead was created.**

---

## 1. The reported "3 conversions", proven

Treated as a symptom until the account confirmed it. It is confirmed.

**Window: 2026-07-19 → 2026-08-17** (Eastern, the account timezone). This is the entire life of the
two live campaigns, which started 2026-07-22. `last_30`, `last_60`, `last_90` and `last_180` all
return identical totals, and `prev_30` returns $0.00, which independently confirms there is no
earlier live-campaign history to compare against.

| Conversion action | ID | Type | Category | Counting | Conversions | All conv. | Campaign split |
|---|---|---|---|---|---|---|---|
| `WC leads` | 7644242327 | UPLOAD_CLICKS | CONTACT | ONE_PER_CLICK | **2** | 2 | 1 Hardscape, 1 Outdoor Living |
| `Calls from ads` | 6566620547 | AD_CALL | PHONE_CALL_LEAD | MANY_PER_CLICK | **1** | 1 | Outdoor Living |
| `Local actions - Other engagements` | 6611700177 | GOOGLE_HOSTED | ENGAGEMENT | MANY_PER_CLICK | 0 | 29 | 15 / 14 |
| `Local actions - Website visits` | 6607912702 | GOOGLE_HOSTED | PAGE_VIEW | MANY_PER_CLICK | 0 | 6 | 5 / 1 |
| `Clicks to call` | 6607906201 | GOOGLE_HOSTED | CONTACT | MANY_PER_CLICK | 0 | 1 | Outdoor Living |
| **Total** | | | | | **3** | **39** | |

**Answering the required questions directly:**

- **Which actions generated them?** Exactly the two above. Nothing else contributed.
- **What were they?** Two WhatConverts offline uploads of website leads, and one phone call placed
  from the ad itself that lasted longer than the 60-second threshold.
- **Which are in bidding?** Both are in biddable categories. `WC leads` is CONTACT / WEBSITE, which
  is biddable on both campaigns. `Calls from ads` is PHONE_CALL_LEAD / CALL_FROM_ADS, also biddable.
  **However, neither influences bidding today**, because both campaigns run `TARGET_SPEND`
  (Maximize Clicks), which ignores conversion goals entirely.
- **Are soft or duplicate conversions inflating performance?** Not in the Conversions column — the
  36 local actions are correctly excluded. But eight enabled actions *are* eligible to feed that
  column, across three overlapping form-lead and five overlapping call-lead definitions. See §3.
- **Are valid form or call conversions missing?** **Yes.** See §4. This is the Priority 0 finding.

**The single counted call is independently verifiable.** The retained `call_view` log holds exactly
three calls attributable to live campaigns:

| Date (account time) | Duration | Status | Area code | Counted? |
|---|---|---|---|---|
| 2026-07-30 10:09 | 85s | RECEIVED | 512 | **yes** — above the 60s threshold |
| 2026-08-14 12:16:12 | 4s | RECEIVED | — | no — correctly below threshold |
| 2026-08-14 12:16:31 | 11s | RECEIVED | — | no — correctly below threshold |

The 60-second minimum on `Calls from ads` is doing real work: two of three calls were junk and were
correctly discarded. Across the full retained log of 216 calls, the median is 63.5 seconds and 111
exceed 60 seconds.

---

## 2. Full conversion-action inventory

16 actions exist. 13 are ENABLED, 2 are HIDDEN, and 8 currently feed the Conversions column.

| Name | ID | Status | Type | Category | Primary | In Conv. column | Counting | Attribution | Click window | Call min |
|---|---|---|---|---|---|---|---|---|---|---|
| GA Submit Form | 6557277268 | ENABLED | WEBPAGE | SUBMIT_LEAD_FORM | yes | **yes** | ONE_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | 30 | 60 |
| GA Call Btn Click | 6557280400 | ENABLED | WEBPAGE | CONTACT | yes | **yes** | ONE_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | 30 | 60 |
| Calls from ads | 6566620547 | ENABLED | AD_CALL | PHONE_CALL_LEAD | yes | **yes** | MANY_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | 30 | 60 |
| Progreen - Lp - Submit Lead Form | 6885608055 | ENABLED | WEBPAGE | SUBMIT_LEAD_FORM | yes | **yes** | ONE_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | 30 | 60 |
| Progreen - Lp - Phone Call Leads | 6885610317 | ENABLED | WEBSITE_CALL | PHONE_CALL_LEAD | yes | **yes** | ONE_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | 30 | **30** |
| …Austin (web) form_submission | 7389543347 | ENABLED | GA4_CUSTOM | SUBMIT_LEAD_FORM | yes | **yes** | MANY_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | **90** | 60 |
| …Austin (web) phone_call_click | 7389543053 | ENABLED | GA4_CUSTOM | PHONE_CALL_LEAD | yes | **yes** | MANY_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | **90** | 60 |
| WC leads | 7644242327 | ENABLED | UPLOAD_CLICKS | CONTACT | yes | **yes** | ONE_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | 60 | 60 |
| WC calls | 7644612703 | ENABLED | UPLOAD_CALLS | CONTACT | yes | **yes** | ONE_PER_CLICK | GOOGLE_SEARCH_ATTRIBUTION | 60 | 60 |
| Clicks to call | 6607906201 | ENABLED | GOOGLE_HOSTED | CONTACT | yes | no | MANY_PER_CLICK | GOOGLE_ADS_LAST_CLICK | 30 | 60 |
| Local actions - Website visits | 6607912702 | ENABLED | GOOGLE_HOSTED | PAGE_VIEW | yes | no | MANY_PER_CLICK | GOOGLE_ADS_LAST_CLICK | 30 | 60 |
| Local actions - Other engagements | 6611700177 | ENABLED | GOOGLE_HOSTED | ENGAGEMENT | yes | no | MANY_PER_CLICK | GOOGLE_ADS_LAST_CLICK | 30 | 60 |
| Local actions - Directions | 6626900593 | ENABLED | GOOGLE_HOSTED | GET_DIRECTIONS | yes | no | MANY_PER_CLICK | GOOGLE_ADS_LAST_CLICK | 30 | 60 |
| Local actions - Menu views | 7030671029 | ENABLED | GOOGLE_HOSTED | PAGE_VIEW | yes | no | MANY_PER_CLICK | GOOGLE_ADS_LAST_CLICK | 30 | 60 |
| Progreen Austin (web) purchase | 6598063651 | HIDDEN | GA4_PURCHASE | PURCHASE | no | no | MANY_PER_CLICK | — | 90 | 60 |
| …Austin (web) purchase | 6708233977 | HIDDEN | GA4_PURCHASE | PURCHASE | no | no | MANY_PER_CLICK | — | 90 | 60 |

### Account-default versus campaign goals — consistent

Both live campaigns inherit the account default goal set with no override. Biddable categories on
both: `PHONE_CALL_LEAD` (WEBSITE and CALL_FROM_ADS), `SUBMIT_LEAD_FORM` (WEBSITE), `CONTACT`
(WEBSITE). Non-biddable: every `GOOGLE_HOSTED` category and `CONTACT / CALL_FROM_ADS`.

**This is correct and should not be changed.** The Google-hosted local actions are properly walled
off from bidding. One nuance worth recording: `CONTACT / CALL_FROM_ADS` is **not** biddable, and
`WC calls` sits in exactly that category — so even if `WC calls` started producing, it would not
feed bidding. That matters for Phase 2 and is called out in §6.

---

## 3. Duplication: eight actions, two real events

| Real event | Actions competing to count it |
|---|---|
| **A website form lead** | `GA Submit Form`, `Progreen - Lp - Submit Lead Form`, `…(web) form_submission` (GA4), `WC leads` (upload) — **4 definitions** |
| **A phone lead** | `GA Call Btn Click`, `Progreen - Lp - Phone Call Leads`, `…(web) phone_call_click` (GA4), `Calls from ads`, `WC calls` (upload) — **5 definitions** |

Three of these carry `MANY_PER_CLICK` counting, so a single visitor can register repeatedly. The two
GA4 custom actions carry a **90-day** click window against 30 days elsewhere, so the same lead can
be counted in two different windows.

The GA4 pair is the clearest duplication risk, because **three GA4 properties** are firing across
these hosts — `G-HL5EFB8XKJ`, `G-MHX199EBNJ`, and `_ga_JDFF195TRG` observed in the main-site cookie
jar. Two GA4 purchase actions and two GA4 custom actions exist in the account, one pair per
property. That is precisely how the duplication reaches the Conversions column.

**Proposed in `11_exact_change_plan.yaml` (`CONVERSIONS`, 4 objects):** demote `GA Submit Form`,
`GA Call Btn Click`, and both GA4 custom actions to secondary. Each is either a legacy action with
no recent volume or a MANY_PER_CLICK duplicate of a cleaner definition.

**Deliberately not proposed yet:** choosing between `WC leads` / `WC calls` and the
`Progreen - Lp - *` on-page pair as the single system of record. That decision depends on whether
the on-page tag can be repaired (SIT-002). Deciding it now would hard-wire the workaround.

---

## 4. Priority 0 — the landing pages do not carry attribution into the form

### 4a. What the browser shows

Loaded in a real Chromium session on 2026-08-18 with
`?gclid=TESTGCLID_readonly_audit&wbraid=TESTWBRAID&utm_source=google&utm_medium=cpc&utm_campaign=audit`:

| Host | Form | gclid reaches a hidden field? | UTMs reach hidden fields? |
|---|---|---|---|
| `offeraustin.progreenlandscapesolutions.com/landscape-design/` | `gform_3` | **No** | **No** |
| `progreenlandscapesolutions.com/austin/services/hardscaping/` | `gform_1` | **Yes** → `input_15` | **Yes** → `input_11` = `cpc`, `input_18` = `audit` |

On the landing page the only content hidden input is:

```
name="input_6"  id="input_3_6"  value="{Referer}"
```

That is an **unresolved Gravity Forms merge tag** — the literal string, never substituted. Both
`TESTGCLID_readonly_audit` and `TESTWBRAID` are present in the rendered HTML and in the final URL's
query string, so the identifiers arrive at the page. They simply are not picked up.

**All 12 live ad destinations are `offeraustin.*` pages using `gform_3`.** 100% of paid
design-and-build traffic lands on the form that captures nothing.

The main-site form also carries explicit marketing and non-marketing consent checkboxes. The landing
pages carry none.

### 4b. What the account data shows

Over the live window, on the pages receiving all the traffic:

| Action | Conversions |
|---|---|
| `Progreen - Lp - Submit Lead Form` | **0** |
| `Progreen - Lp - Phone Call Leads` | **0** |
| `WC leads` | 2 |

Real leads occurred. Google's on-page measurement did not record them; WhatConverts' upload did.
Historically `Progreen - Lp - Submit Lead Form` has **196** conversions all-time, from the era when
the destination was the `offeraustin.*` **root**. The tag has worked before and does not appear to
fire on the current sub-pages.

### 4c. What is present on the pages

`AW-11240766632` is on every landing page and matches the account's `conversion_tracking_id`
exactly. `GTM-54Q4TVXF` loads. WhatConverts cookies (`wc_client`, `wc_visitor`, `wc_swap`,
`wc_client_current`) are set. `_gcl_aw` and `GCL_AW_P` are set, so auto-tagging is reaching the
browser. The dataLayer shows `gtm.js`, `gtm.dom`, `gtm.load`, a scroll trigger and a GA4 config
call — but no form or conversion event definition is observable without submitting.

So the tag is installed; the **trigger or label for the form submit** is the suspect.

### 4d. Honest limit

I have not proven the negative. Confirming it needs one end-to-end test submission carrying a clear
test identifier. That is prohibited in READ mode and is scoped as `SIT-002` in the change plan, with
its own approval.

---

## 5. Attribution field inventory

| Field | Captured on `offeraustin.*` (`gform_3`) | Captured on main site (`gform_1`) |
|---|---|---|
| GCLID | **no** | yes (`input_15`) |
| GBRAID | **no** | not observed |
| WBRAID | **no** | not observed |
| utm_source | **no** | not observed (`input_14`/`16`/`17` stayed empty) |
| utm_medium | **no** | yes (`input_11`) |
| utm_campaign | **no** | yes (`input_18`) |
| utm_term / utm_content | **no** | not observed |
| Campaign / ad group / keyword | **no** | **no** |
| Device | **no** | **no** |
| Landing page URL | **no** | **no** |
| Referrer | broken (`{Referer}` literal) | not observed |
| Consent state | **no** | yes (marketing + non-marketing checkboxes) |
| Unique lead ID | **no** | **no** |

WhatConverts captures GCLID client-side independently, which is why `WC leads` produces at all. But
the Gravity Forms submission itself carries nothing, so any CRM that receives the form post directly
gets an unattributed lead.

**Deduplication by lead or transaction ID is not possible today** — no unique lead ID exists in
either form. Green Marketing policy requires it.

---

## 6. Dynamic number insertion versus Google call conversions

Three different numbers were observed on 2026-08-18:

| Where | Number |
|---|---|
| All 12 `offeraustin.*` landing pages | **(512) 890-2716** — identical to the Google Ads call asset on both campaigns |
| `progreenlandscapesolutions.com/austin/`, desktop load | (512) 277-9435 |
| `progreenlandscapesolutions.com/austin/`, mobile load, same URL | (512) 559-1315 |

Two different numbers on two loads of the same URL is conclusive: **WhatConverts dynamic number
insertion is active from a pool.** These are legitimate tracking swaps, not a market error.
**Do not standardise them.**

**Conflict check.** The Google Ads call asset uses
`call_conversion_reporting_state = USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION`, pointing at
conversion action `179`, and both campaigns share the same asset. Google call-forwarding numbers on
the ad and WhatConverts numbers on the page occupy different surfaces, so they do not fight each
other — but `Calls from ads` and `WC calls` can both claim the same human. `WC calls` has **0**
conversions all-time, so no double count exists today. It becomes a real risk the moment `WC calls`
starts producing, and it is compounded by `WC calls` sitting in the non-biddable
`CONTACT / CALL_FROM_ADS` category. Both points must be settled in Phase 2 before any move to Smart
Bidding.

---

## 7. Third-party hosts observed on the landing pages

| Host | Identified | Note |
|---|---|---|
| `www.googletagmanager.com`, `www.google.com`, `www.googleadservices.com`, `googleads.g.doubleclick.net`, `ad.doubleclick.net`, `stats.g.doubleclick.net`, `analytics.google.com` | Google Ads / GA4 / GTM | expected |
| `connect.facebook.net`, `www.facebook.com` | Meta pixel | not part of this work order |
| `ads.nextdoor.com`, `flask.nextdoor.com` | Nextdoor | not part of this work order |
| `pixel.wp.com`, `stats.wp.com` | WordPress / Jetpack | expected on WordPress |
| `static.cloudflareinsights.com` | Cloudflare analytics | expected |
| `lptemplate.greenmarketingfl.nl` | Green Marketing's own landing-page template host | expected |
| `process.iconnode.com` | **unidentified** | verify before the next deploy |
| `mpc2-prod-23-is5qnl632q-ue.a.run.app` | **unidentified** Google Cloud Run service | verify |
| `p.ksrndkehqnwntyxlhgto.com`, `s.ksrndkehqnwntyxlhgto.com` | **unidentified**, randomised domain | verify; these are the hosts most worth confirming |
| `monitor.clickcease.com` | ClickCease | **appears only in the account tracking template, not on any page.** The redirect half is installed without the on-page half. |

I am not asserting that the unidentified hosts are harmful. They are named so someone can confirm
them, which is the correct posture for third-party script on a lead-capture page.

---

## 8. Consent

Consent Mode is initialised — `google_tag_data.ics` is present on both hosts. **No consent
management platform was detected**: no TCF `__tcfapi`, no `__uspapi`, no Cookiebot, OneTrust,
Complianz or CookieYes, and no cookie banner on the landing pages. Marketing cookies including
`_fbp`, `IDE` and Nextdoor identifiers are set on load. The landing-page form has no consent
checkbox while the main-site form has two.

Consent state is therefore not captured with a lead, which Green Marketing policy requires.
Flagged to the client's legal or privacy owner as `SIT-004`. No change is proposed by Green
Marketing — this is a client decision, not an advertising decision.

---

## 9. Profitability — formulas and the exact missing inputs

Nothing below is invented. Each formula is stated with the input it lacks.

| Metric | Formula | Status |
|---|---|---|
| CPL | `cost ÷ conversions` | **$584.83** — computable, but understated in the numerator's denominator because of §4 |
| Cost per qualified lead | `cost ÷ qualified leads` | **blocked** — no qualified-lead classification available |
| Cost per estimate | `cost ÷ estimates scheduled` | **blocked** — no CRM |
| CAC | `cost ÷ sold jobs` | **blocked** — no sold-job data |
| ROAS | `revenue ÷ cost` | **blocked** — no revenue |
| Gross-profit ROAS | `(revenue × gross margin %) ÷ cost` | **blocked** — no revenue, no margin |
| Profit after ad spend | `(revenue × gross margin %) − cost` | **blocked** |

**Costs not included in any of the above:** Green Marketing management fees, landing-page hosting,
WhatConverts subscription, ClickCease subscription, and sales labour. Any profitability figure
produced later must state which of these it excludes.

**Exact missing fields, all currently null in `clients/pro-green-austin/client.yaml`:**
`offer.average_job_revenue`, `offer.gross_margin_pct`, `offer.close_rate_pct`, `offer.target_cpl`,
`offer.target_cpql`, `offer.target_cac`, `conversions.crm_stage_mapping.{lead,qualified,sold}`, and
`integrations.crm`.

**Until those exist, optimise for qualified leads, not raw conversions.**

---

## 10. Verdict

**Conversion tracking verdict: NOT RELIABLE FOR BIDDING.**

Three defects compound: leads are being missed at the landing page (§4), eight actions can count two
real events (§3), and no unique lead ID exists for deduplication (§5). The current 3-conversion
figure is a floor, not a measurement.

**Consequence, stated plainly:** no Smart Bidding strategy should be enabled on this account until
one form-lead definition and one call-lead definition are producing **15 or more conversions per 30
days**. `CLAUDE.md` prohibits imposing target CPA on unreliable or insufficient conversion data, and
that is the right call here on the evidence. Google's pending `MAXIMIZE_CONVERSIONS_OPT_IN`
recommendation on both campaigns must **not** be applied yet.

---

## 11. The confirming test, for a later approval

Not executed. Scoped here so it can be approved as a unit.

1. Submit one form on `offeraustin.progreenlandscapesolutions.com/landscape-design/` carrying
   `?gclid=GMQA-<date>-01` and the last name `QA-GREENMARKETING`, from a device on a known IP.
2. Place one call to the landing-page number lasting more than 60 seconds, then hang up.
3. Within 24 hours, read back `Progreen - Lp - Submit Lead Form`,
   `Progreen - Lp - Phone Call Leads`, `WC leads` and `WC calls` and record which fired.
4. Confirm the WhatConverts lead record carries the GCLID.
5. Delete the test lead from the CRM and mark the call as a test.

Requires its own approval. It creates a real record in the client's systems, so it is not part of
this READ package.
