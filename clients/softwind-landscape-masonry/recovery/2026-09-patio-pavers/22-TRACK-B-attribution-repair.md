# TRACK-B — missing campaign / ad group / keyword attribution

**Status: NON-EXECUTING REPAIR PLAN.** Nothing here has been applied. It changes
no Google Ads object, no website, no WhatConverts setting, no GTM container and
no GA4 property. It needs its own approval, separate from the five Ads packages.

Evidence: `19-track-probe.json` and `10-lp-qa.json`, both read-only headless
browser runs on 2026-09-03.

---

## 1. The controlled experiment that settles the cause

Two probes were run against the same two pages, differing only in the query
string. Nothing else changed.

| | Probe 1 — GCLID only | Probe 2 — GCLID + 4 UTMs |
|---|---|---|
| URL parameters | `?gclid=…` | `?gclid=…&utm_source&utm_medium&utm_campaign&utm_term&utm_content` |
| GCLID reaches final URL | yes | yes |
| GCLID reaches the DOM | yes | yes |
| `wc_client` captured source | `google` | `google` |
| `wc_client` captured medium | `cpc` | `cpc` |
| **`wc_client` captured campaign** | **empty** | **`QAGATE_CAMPAIGN`** |
| **`wc_client` captured ad group** | **empty** | **`QAGATE_ADGROUP`** |
| **`wc_client` captured term** | **empty** | **`QAGATE_TERM`** |
| `wc_client` captured GCLID | yes | yes |

**This is a clean A/B.** WhatConverts populates campaign, ad group and term the
moment UTMs are present, and leaves them blank when they are not. The mechanism
is not broken; the parameters are simply never sent.

**Why they are never sent, read live from the account:**

- `customer.final_url_suffix` — **unset**
- `campaign.final_url_suffix` on Patio — **unset**
- `campaign.final_url_suffix` on Pavers — **unset**
- `customer.tracking_url_template` — ClickCease's
  (`monitor.clickcease.com/tracker/tracker.aspx?…&url={lpurl}&…`), which carries
  no `utm_campaign` or `utm_term` into the landing URL
- `customer.auto_tagging_enabled` — **true**, which supplies the GCLID and
  nothing else

**Conclusion.** Auto-tagging gives WhatConverts a GCLID. A GCLID alone lets it
derive source and medium; it cannot resolve a campaign name or keyword from a
GCLID without either UTMs on the URL or an authenticated Google Ads integration.
Neither exists. That is the whole cause of the blank campaign and keyword fields
the forensic audit reported.

**A GCLID reaching the landing page is therefore NOT evidence of successful
attribution** — exactly as the QA gate warns. Probe 1 proves it: the GCLID
arrived and the campaign field was still blank.

## 2. Second, independent defect: the form carries no click ID

On both pages, in both probes, with and without UTMs:

- hidden field `input_8` — **empty on page load**
- `gform_field_values` — **empty on page load**
- two identical copies of `form#gform_1` exist, with **22 duplicate DOM ids**
  including every field id

So a Gravity Forms submission POSTs no GCLID. WhatConverts still attributes the
lead from its own cookie, which is why `WC Leads` works at all — but the CRM
record itself carries no click identifier, and the duplicate form ids mean any
script that targets a field by id may bind to the wrong copy.

`input_9` is an unlabelled visible text field whose only `label[for]` matches are
"Facebook" and "LinkedIn". On the sibling Softwind account the same index was a
honeypot that fakes a broken form when filled. **This has not been verified here
either way**, which is why no automated form submission may be attempted.

## 3. Two mutually exclusive routes to a fix

### Route 1 — connect the WhatConverts ↔ Google Ads integration (RECOMMENDED)

WhatConverts resolves the GCLID against the Ads API and back-fills campaign, ad
group, keyword and search term.

- Changes **nothing** in Google Ads, on the website, or in the ad-serving path.
- Leaves ClickCease's tracking template completely untouched.
- Also back-fills the keyword and search term, which UTMs cannot do reliably.
- Blocked on **SLM-Q8**: does Green Marketing have WhatConverts admin access?

### Route 2 — add a Final URL suffix (FALLBACK, only if Route 1 is unavailable)

Proposed value, both campaigns:

```
utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}
```

| Field | Value |
|---|---|
| Resource | `campaign.final_url_suffix` on `23484806108` and `23489296528` |
| Current | unset on both |
| Rollback | clear the field on both |
| Length | 118 characters, within the 2,048-character limit |
| Object count | 2 |
| Subplan | `SITE_OR_TRACKING` |
| Approval class | its own; **must not** be bundled with BID, BUD, KW, NEG or CONV |

**Why this is the fallback and not the recommendation.** It writes to the URL
path ClickCease owns. A final URL suffix and a tracking template are combined by
Google at serve time, and ClickCease redirects through its own domain before
handing off to `{lpurl}`. That combination is safe in principle, but it cannot be
proven safe from a read-only test — it needs one real paid click to verify end to
end. The safety rules require ClickCease to be preserved, so the risk is only
worth taking if Route 1 is genuinely unavailable.

**If Route 2 is ever approved, the verification sequence is:**
1. `validate_only` the two-campaign mutation through `execute_approved_plan.py`.
2. Apply, then read `campaign.final_url_suffix` back on both campaigns.
3. Within 24 hours, confirm a real paid click still lands on the offer page with
   HTTP 200 and that ClickCease still logs it.
4. Confirm `wc_client` on that visit carries a real campaign id, not a blank.
5. If the ClickCease redirect breaks, clear the field immediately — that
   rollback needs no new approval, being a restoration of the recorded prior
   state.

## 4. Proposed corrections — NOT APPLIED

| # | Change | System | Blocked on | Rollback |
|---|---|---|---|---|
| B1 | Connect WhatConverts ↔ Google Ads integration | WhatConverts | SLM-Q8 access | Disconnect |
| B2 | *Fallback only:* final URL suffix on both campaigns | Google Ads | B1 being unavailable + its own approval | Clear the field |
| B3 | Populate a hidden GCLID field on the Gravity Form | WordPress | Site access; `input_9` field map must be verified first | Remove the field |
| B4 | Remove the duplicate `form#gform_1` render | WordPress | Site access | Restore the template |
| B5 | Verify what `input_9` actually is before any form test | WordPress | Site access | n/a, read-only |

## 5. What must NOT be concluded from this file

- Do **not** conclude the GCLID is lost. It is not; it arrives intact.
- Do **not** conclude WhatConverts is broken. Its visitor tracking works; three
  of its fields are simply never supplied.
- Do **not** bundle B2 into any existing package. Tracking-template changes are
  their own approval class under the safety rules.
- Do **not** treat B1 and B2 as additive. Doing both would double-tag the URL
  with no benefit; pick one.
