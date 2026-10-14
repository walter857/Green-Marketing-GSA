# PLAN-R1B — EXECUTION CONTINUATION RECEIPT

**Plan** PLAN-R1B · **Fingerprint** `B7AD76CB16F8` · **Approved by** Walter Correa
**Account** `Softwind Power Washing - Live` / `1521725229` / Power Washing
**Continuation after connection loss.** Completes the T-1/T-2 receipt of the same date.

**ONE form submission. Zero Google Ads mutations. Zero calls placed.**

Evidence: `snapshots/r1b-t3-t8-2026-09-02T092424.json`,
`snapshots/plan-r1b-validation-2026-09-02T*.json`,
`receipts/r1b-t3-before-2026-09-02T092424.png`, `receipts/r1b-t3-after-2026-09-02T092424.png`.

---

> ## CORRECTION NOTICE — added 2026-09-02 09:53 ET
>
> **This receipt describes `AW-17878095007` as a "foreign" tag belonging to an account
> "Green Marketing does not control". That characterisation was WRONG.**
>
> `AW-17878095007` is the **`conversion_tracking_id` of Google Ads customer `2429758629`,
> "Softwind Landscape & Masonry - Live"** — the client's own sibling account, at level 1 under
> the authorized Green Marketing MCC `3373711342`. Resolved 2026-09-02 by reading
> `customer.conversion_tracking_setting.conversion_tracking_id` and sweeping all 32 enabled
> non-manager accounts under that MCC; exactly one matched. **An `AW-` value is a conversion
> tracking ID, not a customer ID** — which is why the number never matched a customer ID and the
> tag looked foreign.
>
> **Every observation in this receipt stands.** The tag really does take `form_start`,
> `form_submit`, form-data POSTs, the GCLID and the website-call replacement, and Softwind Power
> Washing's own call path really is preempted. **Only the ownership conclusion changes:** this is
> cross-account contamination between two scope-fenced sibling accounts of the same client — an
> attribution and scope defect — **not a third-party data leak or a privacy breach.**
>
> Resolved in `plans/2026-09-02-plan-r7a-website-tracking-form-call-repair.yaml`.


## 1. Identity result — PASS

`Softwind Power Washing - Live` · `1521725229` · manager **false** · test **false** ·
**ENABLED** · **USD** · **America/New_York**.

## 2. Fingerprint result — MATCH

`B7AD76CB16F8`, recomputed twice from the saved plan file, **46/46 checks pass**. All four
preconditions now MET (approval, test email, client notification, named cleanup owner).

## 3. T-3 execution-state classification — **B. CONFIRMED_NOT_SUBMITTED** (at the time of reconciliation)

The interrupted attempt had **not** submitted anything.

## 4. Evidence used to reach that classification

| Evidence | Finding |
|---|---|
| T-3 script on disk | **None existed.** Only `softwind_r1b_t1_t2.py` (01:28), which provably cannot submit — no `fill`, no `click`, no `form.submit()`, and it recorded `FORM_SUBMITTED: False`. |
| Repo files written after the interruption | **None.** Last write was `plan-r1b-validation-2026-09-02T014001.json` at **01:40:01.6** — the pre-submit gate itself. |
| Temp artifacts in the 01:35–01:50 window | **None of any kind.** |
| Orphaned Playwright profile dirs | **None from 2026-09-02.** Playwright leaves `playwright_chromiumdev_profile-*` behind when a run is interrupted; the newest is dated Aug 25. An interrupted browser run would have left one. |
| Google Ads conversions | 0.0 on all four actions — **weak corroboration only**, since a synthetic GCLID cannot join and would not have registered either way. |

**Limitation stated plainly:** WordPress/Gravity Forms entries, WhatConverts records, CRM records
and webhook logs **could not be inspected** — this session holds no credentials for any of them.
The classification therefore rests on proving **no submitting mechanism ever existed or ran**, not
on destination inspection. A 30-second spot-check of Gravity Forms entries before 09:24 would close
that gap definitively.

## 5. Number of form submissions — **EXACTLY ONE**

`submit_clicks_final: 1`, enforced by a hard guard asserting the counter is 0 before the click and
1 after. **Submitted 2026-09-02 09:24:37.155 America/New_York.**

Three earlier runs failed **before** the submit click (selector errors) and incremented nothing.

---

## 6. Two plan defects found and corrected before submitting

### 6a. `input_9` is a HONEYPOT, not "Full Name"

PLAN-R1B and PLAN-A2 both list `input_9` as the Full Name field. It is not. It is a Gravity Forms
anti-spam honeypot: `class="gfield gfield--type-honeypot gform_validation_container"`,
`display:none`, `autocomplete="new-password"`, 0×0 px, **labelled "Comments"**.

**Filling it would have flagged the submission as spam and Gravity Forms would have silently
discarded the lead.** The test would then have reported "form submitted, no record created" and I
would have concluded the form path was broken. **It was left empty** — readback confirms
`input_9 = ""`.

**The real field map, from the rendered labels:**

| Field | Actual label | Filled with |
|---|---|---|
| `input_9` | "Comments" — **HONEYPOT** | **(left empty)** |
| `input_1` | **Full Name\*** | GM TEST DO NOT CONTACT |
| `input_4` | **Phone Number\*** | (631) 555-0147 |
| `input_3` | **Email Address\*** | access@greenmarketing.com |
| `input_7` | Tell us about your project (optional) | test note |

The field map is **not** a fingerprinted field, so `B7AD76CB16F8` is unchanged.

**This also corrects the T-1/T-2 receipt**, which reported "5 visible fields, none carrying the
`required` attribute." The truth is **4 real fields, 3 of them required**. My earlier visibility
test used `display:none` alone and missed a 0×0 element inside a hidden container.

### 6b. The form is DUPLICATED on the page

`form#gform_1` exists **twice** (hero at ~400 px, second at ~5305 px), and **every DOM id is
duplicated** — `gform_1`, `gform_wrapper_1`, `gform_submit_button_1`, `input_1_1`, `input_1_3`,
`input_1_4`, `input_1_7`, `input_1_9`, plus Divi's `et-boc`. Duplicate ids are invalid HTML, and
`getElementById` returns only the first. **Any tracking or DNI script that binds by element id will
bind to the wrong copy.** New P1 defect; not repaired here.

---

## 7. Form and confirmation result — SUCCESS

| | |
|---|---|
| Form POST to `offer.softwindli.com` | **exactly 1** |
| HTTP statuses | **200** then **302** |
| Redirect | **YES → `https://offer.softwindli.com/thank-you/`** |
| Page title after submit | **"Thank You \| Softwind Landscape & Masonry"** |
| Inline confirmation | none — a redirect is used instead |
| Form still present after submit | **no** |
| Validation banner / field errors | **none** |
| **Reserved test phone rejected?** | **NO** — accepted and reformatted to `(631) 555-0147`. The STOP condition never triggered and no substitute number was ever considered. |
| Automatic retry | **NO** |

> **Correction to the raw capture.** The JSON field `automatic_retry_detected: true` is a **false
> positive** from a crude heuristic that counted all 16 POSTs in the session, most of them analytics
> beacons. **Only one POST went to `offer.softwindli.com`.** There was one submission.

## 8. SG-Captcha result — INTERMITTENT

**This run: SG-Captcha did NOT appear.** HTTP **200**, no `/.well-known/sgcaptcha/` request on
arrival or after submit.

**This corrects the T-1/T-2 receipt**, which recorded HTTP 202 and a captcha interstitial and
described it as sitting in the paid click path. Both observations are real; taken together they show
**SG-Captcha fires intermittently, not on every visit.** It remains worth investigating — an
intermittent challenge on a paid landing page still costs some sessions — but it is **not** a
constant blocker, and the stronger claim in the earlier receipt is withdrawn.

## 9. Softwind Google Ads conversion-event result — **IT FIRED**

**The form conversion path is alive.** On the thank-you page, two requests fired to Softwind's own
account:

```
googleadservices.com/pagead/conversion/18369652705/   en=conversion
google.com/pagead/1p-conversion/18369652705/          en=conversion
```

| Question | Answer |
|---|---|
| Did the conversion request fire? | **YES** |
| Endpoints | the standard gtag pair above |
| How many logical conversions? | **ONE**, sent over the two standard endpoints — this is normal gtag behaviour, **not** double counting |
| Fired before or after submission succeeded? | **After** — on `/thank-you/`, following the 302 |
| Synthetic GCLID in the request URL? | **No** — gtag relies on the `_gcl_aw` cookie rather than a URL parameter |
| Blocked or malformed? | **No** |
| **Conversion label `FddkCOul59scEOHPqrdE` visible?** | **NOT CONFIRMED** — the request carries no `label=` parameter. Modern gtag transmits the label in the encoded payload rather than the query string, so **absence here is not evidence of a wrong label**, but this run **cannot prove the label matched**. |

**Google Ads still reads `all_conversions = 0.0` on all four actions. That is the EXPECTED result
and is NOT a test failure** — a synthetic GCLID cannot join to a real ad click, exactly as the plan
predicted.

**What is now established:** the page fires a Google Ads conversion to the correct account on
successful submission. **What is still open:** whether it carries the specific label belonging to
conversion action `7708725995`.

## 10. Foreign Google Ads tag result — WORSE THAN PREVIOUSLY PROVEN

| Event type | `AW-17878095007` | `AW-18369652705` (Softwind) |
|---|---:|---:|
| Form **conversion** | **0** | **2 (one logical event)** |
| `en=form_start` | **3** | **0** |
| `en=form_submit` | **3** | **0** |
| Page-view / remarketing | 3 | 2 |
| User-list remarketing | 6 | 2 |
| Website-call replacement (`wcm`) | **1** | **0** |
| **POST to `google.com/pagead/form-data/<id>`** | **2** | **0** |
| **POST to `google.com/ccm/form-data/<id>`** | **2** | **0** |
| Carries the synthetic GCLID | **YES** | no |

**The foreign account receives richer signal from Softwind's leads than Softwind does.** It gets
`form_start`, `form_submit`, **form-data POSTs**, the GCLID, and the website-call replacement for
(631) 502-7946. Softwind's account gets the conversion and nothing else.

`form-data` endpoints carry user-entered form field data for enhanced conversions. **There is no
`form-data` POST to Softwind's own account.** The tag was not removed or modified, per instruction.

## 11. Third parties that received a POST at submission

| Destination | Count | Note |
|---|---:|---|
| `p.ksrndkehqnwntyxlhgto.com/keyword/` | 2 | ClickCease (obfuscated domain) |
| `p.ksrndkehqnwntyxlhgto.com/lead/form` | 1 | ClickCease receiving lead form data |
| `google.com/pagead/form-data/17878095007` | 2 | **foreign account** |
| `google.com/ccm/form-data/17878095007` | 2 | **foreign account** |
| **`process.iconnode.com/google-ads/`** | 1 | **UNKNOWN VENDOR — newly discovered.** An unidentified third party receives a POST at form submit on an endpoint named `/google-ads/`. Not previously documented anywhere in this engagement. |

## 12. WordPress / Gravity Forms result

**Record almost certainly created — not directly verified.** The 302 redirect to `/thank-you/` with
no validation error is Gravity Forms' success path, and the honeypot was left empty so the spam
filter had no trigger. **Entry ID and timestamp cannot be read without WordPress credentials.**

## 13. WhatConverts result — CAPTURING ATTRIBUTION

No request to a WhatConverts host was observed, but its cookies are present and **populated with the
full attribution chain**:

```
wc_client = google | cpc | gm-conversion-test | plan-r1b | power+washing+near+me
            | GM-TEST-SYNTHETIC-GCLID-20260901 | ...
wc_visitor = 158931-6e3ae655-...
wc_swap    = 6315025402 | 6315535927 | 197159
```

**WhatConverts is capturing source, medium, campaign, content, term and the GCLID.** Its script is
evidently proxied or first-party rather than served from a whatconverts.com host — which corrects
the T-1/T-2 receipt's implication that it might not be recording at all.

**`wc_swap` still nominates (631) 502-5402 and (631) 553-5927 while the page renders
(631) 502-7946 — the number swap is still not happening.** Unchanged defect.

**Whether a WhatConverts lead record was created cannot be verified without credentials.**

## 14. CRM / webhook result — UNKNOWN

No CRM was identified. `process.iconnode.com/google-ads/` is the only unexplained POST and is a
candidate. **Not verifiable without credentials or vendor identification.** Precondition R1B-PRE-5
remains open; T-6's discovery goal is **partially** met — a candidate endpoint now exists.

## 15. Attribution-field result

| Field | In POST body |
|---|---|
| `gclid` | **YES** |
| `gbraid` | **YES** |
| `wbraid` | **YES** |
| `utm_term` | **YES** |
| `utm_source` / `medium` / `campaign` / `content` | **YES** (via `wc_client`) |
| Consent values | consent-mode `ccm/collect` fired; per-field consent values not exposed client-side |

**`utm_term` DOES reach the submission.** This corrects the T-1/T-2 receipt, which reported it
missing — it was absent from pre-submit storage but is picked up from the URL at submit time.

## 16. Duplicate-event result — NO DUPLICATES

One form POST. One logical Softwind conversion (two standard endpoints). One submit click, guarded.

## 17. Cleanup result — DOCUMENTED, EXECUTION HANDED TO THE CLEANUP OWNER

The record is unmistakably marked: name **GM TEST DO NOT CONTACT**, note *"Green Marketing
conversion tracking test - not a customer - submitted 2026-09-02 - please delete after
verification."*, phone in the **NANP reserved fictitious range** (cannot ring anyone).

**No call or text was sent to the reserved number. No real customer was contacted.**
Any auto-responder goes to `access@greenmarketing.com` — the approval and cleanup owner.

**This session cannot delete any of these records — it holds no credentials.** Cleanup is Walter
Correa's, per the plan. The record remains in:

| System | State |
|---|---|
| WordPress / Gravity Forms | entry present — **delete after QA** |
| WhatConverts | lead likely present — **mark as test / archive** |
| ClickCease | lead/form POST received — no client-side control |
| `process.iconnode.com` | POST received — destination unknown |
| Email `access@greenmarketing.com` | any notification |
| Google Ads `AW-17878095007` | form_start / form_submit / form-data — **cannot be cleaned by us** |
| Google Ads `1521725229` | **nothing** — `all_conversions` still 0.0, conversion history clean |

**Evidence is preserved. Nothing was deleted before this receipt.**

## 18. Files created

- `snapshots/r1b-t3-t8-2026-09-02T092424.json`
- `snapshots/plan-r1b-validation-2026-09-02T012727.json`, `…T014001.json`, and later revalidations
- `receipts/r1b-t3-before-2026-09-02T092424.png`
- `receipts/r1b-t3-after-2026-09-02T092424.png`
- `scripts/softwind_r1b_t3_t8.py`
- this receipt

## 19. Remaining P0 / P1 defects

| # | Defect | Severity | State |
|---|---|---|---|
| 1 | `AW-17878095007` receives `form_start`, `form_submit`, **form-data POSTs**, the GCLID and the website-call replacement for Softwind's number | **P0** | PROVEN, worse than before |
| 2 | Softwind's own account receives **no** form-interaction or form-data events, and **no** `wcm` — its WEBSITE_CALL action `7708765130` still has no path | **P0** | PROVEN |
| 3 | Conversion label not confirmed as `FddkCOul59scEOHPqrdE` | **P1** | OPEN |
| 4 | Duplicate form / duplicate DOM ids across the whole page | **P1** | NEW |
| 5 | `process.iconnode.com/google-ads/` — unknown vendor in the lead path | **P1** | NEW |
| 6 | WhatConverts number swap not occurring | P1 | unchanged |
| 7 | SG-Captcha intermittently intercepts the landing page | P2 | downgraded from P0 |
| 8 | Browser title reads "Softwind Landscape & Masonry" — including on `/thank-you/` | P0 | unchanged |
| 9 | Malformed `tel:(631)` link | P3 | unchanged |

## 20. Confirmations

- **No phone call was placed.** Zero calls, and the test number cannot ring a real person.
- **Zero Google Ads mutations.** Every Google Ads call this session was a `SELECT` through
  `GoogleAdsService.search`. No operation object, no field mask, no `validate_only` request.
- **No duplicate submission.**
- **Nothing was repaired.** The foreign tag, website-call tracking, WhatConverts, SG-Captcha, the
  malformed tel link, CPC, bidding, budgets, campaigns, ad groups, keywords, negatives, RSAs,
  assets, audiences, conversions and landing pages were all left exactly as found.
