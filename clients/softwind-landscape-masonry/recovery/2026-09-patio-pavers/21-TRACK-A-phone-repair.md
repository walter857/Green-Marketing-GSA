# TRACK-A — WhatConverts phone-number mismatch

**Status: NON-EXECUTING REPAIR PLAN.** Nothing in this file has been applied.
It changes no website, no WhatConverts setting, no GTM container, no GA4
property and no Google Ads object. It is not covered by any of the five
Google Ads packages and needs its own approval and its own access.

Evidence: `19-track-probe.json` (read-only headless browser, 4 probes,
2026-09-03). Nothing was submitted and no `tel:` link was clicked.

---

## 1. What was actually observed

| Check | Patio | Pavers |
|---|---|---|
| Number rendered on page (mobile) | **(631) 502-7946** | **(631) 502-7946** |
| Number rendered at `domcontentloaded` | (631) 502-7946 | (631) 502-7946 |
| Number rendered after `networkidle` + 6s | (631) 502-7946 | (631) 502-7946 |
| **Did any script change the number?** | **No** | **No** |
| `wc_swap` cookie | `6315025402+..+6315535927+..+197159` | identical |
| Swap rule: number to FIND | 631-502-5402 | 631-502-5402 |
| Swap rule: number to SHOW | 631-553-5927 | 631-553-5927 |
| Swap rule id | 197159 | 197159 |
| Is the FIND number anywhere on the page? | **No** | **No** |
| Is the SHOW number anywhere on the page? | **No** | **No** |
| `tel:` hrefs (mobile) | `tel:(631)`, `tel:(631) 502-7946` | same |
| `tel:` hrefs (desktop 1280) | 3 links, number correct | — |
| WhatConverts `<script src>` from vendor | **none observed** | none observed |
| WhatConverts referenced in HTML | yes | yes |
| `wc_visitor` / `wc_client` cookies set | yes | yes |

## 2. What this proves, and what it does not

**PROVEN.** The WhatConverts dynamic number insertion rule on these two landing
pages cannot fire. It is configured to find `6315025402` and replace it with
`6315535927`. Neither number exists in the rendered DOM at any point, and the
displayed number is byte-identical before and after every script has run. The
visitor therefore always dials the raw, untracked `(631) 502-7946`.

**PROVEN.** `WC Call` (conversion action `7635680543`, type `UPLOAD_CALLS`) has
recorded **zero conversions and zero all-conversions in every month of its
existence**. `all_conversions` is not gated by goal biddability, so a zero there
means no event was ever received — not merely that it was filtered out.

**PROVEN.** WhatConverts' *visitor* tracking works fine. A synthetic GCLID and
four UTMs were all captured into the `wc_client` cookie. The failure is specific
to the number swap, not to the tag as a whole.

**NOT PROVEN — and the QA gate is right to insist on this.** That the mismatch
*fully* explains zero WhatConverts calls. Three alternatives remain open and none
can be closed without WhatConverts access:

1. Calls may be arriving in WhatConverts under a **different source** — a number
   pool on the main `softwindli.com` site, a Google Business Profile number, or
   manually logged calls — and simply never reaching the `WC Call` Google Ads
   upload. The Ads-side zero would look the same.
2. The **Google Ads → WhatConverts upload itself** may be disconnected or
   unauthorised, in which case fixing the swap changes nothing on the Ads side.
3. The swap rule may be **deliberately scoped** to a different site or template
   that does use `(631) 502-5402`, and these two offer pages may never have been
   in its scope.

Resolving which of these is true is question **SLM-Q8** and requires read access
to the WhatConverts account. Do not present the mismatch as the whole cause until
it is answered.

## 3. A second, independent defect on the same call path

Both pages carry a **truncated `tel:(631)` link** alongside the correct one.
Tapping it dials nothing. This is not a tracking problem — it is a broken call
button on a page whose primary conversion is a phone call, and it is worth fixing
regardless of how SLM-Q8 resolves.

Google's own number replacement is *also* present on these pages
(`conversion/17878095007/wcm`). Two competing number-replacement systems on one
page is a configuration conflict in its own right, and it is a plausible reason a
WhatConverts swap would have been pointed away from the visible number.

## 4. A finding the mobile-only QA would have missed

The pages return **HTTP 403 "Access to this page is forbidden"** to some desktop
user-agent signatures. A 1440×900 context with an explicit Chrome-131 desktop UA
got a 403 with no phone, no form and no tracking; a 1280×800 context with the
default UA got a full HTTP 200 page with the phone, three `tel:` links, two forms
and WhatConverts present.

This is **WAF or bot-mitigation behaviour, not a desktop outage.** Real desktop
visitors evidently do get the page. It is recorded because:

- an over-broad rule could 403 real visitors or Google's landing-page crawler;
- all Patio and Pavers ads currently read `APPROVED`, which argues the crawler is
  *not* being blocked today;
- any future landing-page QA that tests one user agent only can be silently
  wrong in either direction.

## 5. Proposed corrections — NOT APPLIED

| # | Change | System | Who can do it | Rollback |
|---|---|---|---|---|
| A1 | Point swap rule 197159 at the number actually on the page, `6315027946`, or add a rule that targets it | WhatConverts | Needs WhatConverts admin (SLM-Q8) | Restore the rule to find `6315025402` |
| A2 | Remove the truncated `tel:(631)` anchor from both offer templates | WordPress | Needs site access | Re-add the anchor |
| A3 | Decide which number-replacement system owns the call path — WhatConverts DNI or Google WCM — and disable the other on these pages | WhatConverts + GTM/site | Needs both accesses | Re-enable the disabled one |
| A4 | Confirm whether the WAF rule returning 403 to some desktop UAs is intentional, and confirm Googlebot/AdsBot are allowlisted | Hosting/WAF | Needs hosting access | n/a, read-only check first |

**Verification after any of the above, before it is called fixed:**
re-run `scripts/slm_0903_track_probe.py`; the swap FIND number must be present on
the page and the rendered number must differ between `domcontentloaded` and
`networkidle`. Then wait for one real paid call and confirm a `WC Call` row
appears in Google Ads.

**Explicitly out of scope of TRACK-A:** any change to `Softwind - Phone Call Lead`
(`7461590068`) or `WC Call` (`7635680543`) in Google Ads. Fix the path first;
touch the conversion flags only once events are arriving.
