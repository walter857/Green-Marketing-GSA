# Ambient Cooling & Heating — Paid Landing Page QA

**Date:** 2026-08-18 · **Method:** headless Chrome (real JS engine), desktop 1440×900 and mobile 390×844
**Pages:** the five paid offer-subdomain pages · **Phase:** READ + DRAFT

> GET requests only. **No form was submitted. No telephone link was clicked. No call was placed.**
> No website, GTM, or WordPress change was made.

## Why this re-test was necessary

The 2026-08-17 audit recorded *"no tag of any kind on any landing page."* That finding is
**superseded and was wrong**. It was produced with a plain HTTP client, and SiteGround's
SG-Captcha challenge returns a 179-byte meta-refresh stub to any non-JavaScript client. The
tags were always there; the tool could not see them. Every result below comes from a
JavaScript-capable render that solved the challenge.

---

## 1. GTM and tag health — ✅ PASS on all five pages, both viewports

| Check | Result |
|---|---|
| Standard GTM head snippet for `GTM-PQTPQ436` | ✅ exactly 1 |
| `<noscript>` iframe `ns.html?id=GTM-PQTPQ436` | ✅ exactly 1 |
| `gtm.js?id=GTM-PQTPQ436` network request | ✅ 1 request, **HTTP 200** |
| Runtime container `window.google_tag_manager['GTM-PQTPQ436']` | ✅ present |
| `dataLayer` initialized | ✅ `gtm.js`, `gtm.dom`, `gtm.load` |
| Duplicate GTM container | ✅ none — no other `GTM-` ID in the DOM |
| Duplicate Google tag initialization | ✅ none — `window.gtag` is not separately defined |
| Consent Mode v2 | ✅ `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization` |

Firing through the container: **GA4 `G-9X9ZHNCRWF`** (`/g/collect` 200) and the **Google Ads
conversion linker for `11155434808`**, which matches the account's `conversion_tracking_id`.
The `_gcl_aw` first-party cookie is written on a click carrying a `gclid`.

**Undocumented tags also firing:** Microsoft UET (`bat.bing.com/bat.js`), Meta pixel (`_fbp`),
a Nextdoor-style pixel (`ndp_session_id`), and Google Web Call Metrics
(`gstatic.com/wcm/loader.js`). None appear in the approved measurement plan.

---

## 2. Phone numbers — ⛔ FAIL

**The approved number is correct in two places. A third, unapproved number is present on
every page and is *visible and tappable on mobile*.**

| tel: href | Display text | Desktop | Mobile | Verdict |
|---|---|---|---|---|
| `tel:4107056354` | CALL: (410) 705-6354 | visible 204×41 | visible 143×30 | ⚠️ right number, **no `+1`** |
| `tel:(410) 705-6354` | Call Now: (410) 705-6354 | visible 240×41 | visible 240×41 | ⚠️ right number, **malformed href** |
| `tel:+14109141456` | Call Now | **0×0 (unreachable)** | **visible 175×37** | ⛔ **unapproved number** |

- **(410) 914-1456 is neither the approved paid number nor the main-site number.** It is the
  mobile "Call Now" button, Divi module `et_pb_button_5`, hardcoded in the markup.
- This is **not** number-swap behaviour: the other two links on the same page carry the
  approved number, and a swap script would rewrite all of them consistently.
- **Correction to the 2026-08-17 note:** the claim that a hidden `tel:+14107610932` remains in
  the DOM is **not reproducible**. There are **zero** occurrences of 410-761-0932 in the HTML or
  visible text of any page at either viewport. The main-site number is gone; a *different*
  wrong number is the live defect, and its visibility is inverted from what was reported —
  hidden on desktop, **visible on mobile**.
- **None of the three links** use the approved E.164 form `tel:+14107056354`.

**Business impact:** mobile is where the traffic is (157 of 206 HVAC Repair impressions, 40 of
49 AC Repair impressions). The most prominent mobile call CTA dials a number Green Marketing
has not approved and cannot attribute.

---

## 3. Attribution capture — ⛔ FAIL (this is the measurement blocker)

Test: loaded `/ac-repair/` directly carrying `gclid`, `gbraid`, `wbraid` and all five UTMs.

| Check | Result |
|---|---|
| Parameters survive in the final URL | ✅ all 8 present |
| `_gcl_aw` first-party cookie written | ✅ yes |
| Gravity Forms hidden fields `input_9`…`input_15` | ⛔ **all seven EMPTY** |
| `gform_field_values` (dynamic-population carrier) | ⛔ **empty** |

**The form has seven hidden attribution fields and populates none of them.** A submitted lead
carries no click ID, no UTMs, no keyword, no campaign. **Offline conversion import via the Data
Manager API is impossible as built** — there is no `gclid` to send back, so sold-job revenue can
never be attributed to a campaign.

This is independent of ClickCease. Even a perfect redirect would be discarded at the form.

---

## 4. Duplicate forms and invalid markup — ⛔ FAIL

**Three identical Gravity Forms instances render on every page, all sharing `id="gform_1"`.**

Duplicated element IDs (×3 each): `gform_wrapper_1`, `gform_1`, `gform_fields_1`,
`field_1_1`, `input_1_1`, `field_1_3`, `input_1_3`, `field_1_4`, `input_1_4`, `field_1_7`,
`input_1_7`, `field_1_9`…`field_1_15`, plus `et-boc` ×2.

Consequences:
- **Accessibility:** `<label for="input_1_1">` resolves only to the *first* match, so the labels
  on instances 2 and 3 point at instance 1's inputs. Screen-reader users on the lower forms get
  no usable label association.
- **Tag Manager:** any trigger targeting `#gform_1` binds to one instance only, so submissions
  from the other two can be missed.
- Invalid HTML per the spec (IDs must be unique).

On mobile the third instance renders collapsed (`input_1_1` at 0×0), consistent with a
popup/modal container.

---

## 5. Required-vs-optional mismatch — ⛔ FAIL

The message field is labelled **"Tell us about your project (optional)\*"** but carries an
asterisk and `aria-required="true"`. It is **labelled optional and enforced as required** on all
five pages. Every user who reads the label and skips the field hits a validation error.

## 6. Honeypot — ✅ PASS (no defect)

`input_16` renders with rotating labels (Company / Comments / Facebook / Name), which initially
looks like a visible spam field. It is **correctly hidden**: wrapper class
`gfield--type-honeypot`, `position:absolute; left:-9000px; display:none`, field 0×0. This is
standard Gravity Forms anti-spam behaviour and is **not** a defect.

## 7. Privacy and terms — ⛔ FAIL

**Zero** privacy-policy, terms, or disclaimer links on any of the five pages, at either viewport.
Pages collect name, email, phone and a free-text message.

## 8. Cross-service headings — ⛔ FAIL (2 pages)

| Page | Wrong heading |
|---|---|
| `/hvac-repair/` | H2 **"Recent AC Repair Work"** |
| `/gas-boiler-repair/` | H2 **"Your HVAC Replacement in 3 Simple Steps"** |

## 9. Structured data — ⚠️ absent

No `application/ld+json` on any page: no LocalBusiness, no Service, no `telephone` field.
Nothing to correct, but nothing supporting the local-service entity either.

## 10. Countdown / urgency / placeholder content — ⛔ FAIL

> **Correction.** An earlier revision of this document reported "no countdown timer, no
> artificial scarcity." **That was wrong.** The first pass searched only for finance vocabulary
> and did not scan visible copy for urgency language. A full scan on 2026-08-18 found a
> manufactured daily deadline on **all five pages**.

| Page | Copy | Issue |
|---|---|---|
| `/ac-repair/` | "Tell Ambient what your AC is doing **before today's timer reaches zero**" | Explicit countdown |
| `/hvac-repair/` | "…what your heating or cooling system is doing **before today's timer reaches zero**" | Explicit countdown |
| `/gas-boiler-repair/` | "Tell Ambient what your boiler is doing **before today ends**" | Daily deadline |
| `/hvac-installation/` | "**Start planning today.** …**before today ends**" | Daily deadline |
| `/hvac-replacement/` | "**Start planning today.** …**before today ends**" | Daily deadline |
| `/ac-repair/` | "**We are accepting new clients** for AC repair" | Implied capacity scarcity |

There is no evidence of a real deadline or a real capacity limit. **This gets worse under 24/7
delivery**: overnight traffic arrives to a timer that has just expired or silently reset.

No lorem-ipsum or placeholder text was found.

## 10b. Published reviews — ⚠️ provenance unverified, and each renders three times

Customer testimonials **are** published on the paid pages — not previously reported.

| Page | Label used | Quotes |
|---|---|---|
| `/ac-repair/`, `/hvac-repair/` | "Google Review" | "He took time to check multiple things." · "The technician was very professional... and quickly resolved it." · "Timely and great service good company to deal with." |
| `/gas-boiler-repair/` | "Customer Review" | "He took time to check multiple things." · "Quality work at reasonable rates." · "This is a great company to do business with." |

Two problems:

1. **`client.yaml` bars `rating_or_review_count` claims** until the client verifies them in
   writing. Quotes attributed to "Google Review" are review claims and need provenance against
   the source Google Business Profile before these pages are edited or relied on.
2. **Every quote renders three times**, matching the three duplicate section instances in §4.

## 10c. Finance-adjacent copy on a disapproved destination — ⚠️

`/hvac-installation/` carries **"plan professional HVAC installation with honest, upfront
pricing"** in visible body text. This is the exact phrase the 2026-08-17 audit suspected in the
*ads* — it is actually on the *page*, and that page's ads are disapproved.

It does **not** explain the full CONSUMER_FINANCE pattern (`/gas-boiler-repair/` has no finance
language at all and its ads are disapproved anyway), but it is removable finance-adjacent copy on
a disapproved destination and should go as appeal hygiene.

## 10d. Availability claims under 24/7 delivery — ⚠️

Business hours remain 08:00–16:00 and out-of-hours calls go to voicemail, so no availability
claim is supportable. Full scan results:

- **Drafted replacement RSAs (`0BCC73A397580856`): ✅ CLEAN** — zero hours or availability claims.
- **All 12 live RSAs: ✅ CLEAN.**
- **Callout asset `407418595411` "Prompt, Reliable Service"** (all five campaigns) — ⚠️ "Prompt"
  is a responsiveness claim that can serve at 02:00. Recommend replacing.
- **`/hvac-repair/` "Prompt, Customer-Focused Service"** — ⚠️ same issue on the page.
- **"Call Now: (410) 705-6354"** (all five pages) — ⚠️ implies live answering; soften to
  "Call Ambient".
- **`/gas-boiler-repair/` "Smell gas? Leave immediately and call your gas utility or 911…"** —
  ✅ **not a defect.** This is a correct safety notice. **Keep it.**
- Sitelink "See available HVAC services" — ✅ false positive; "available" describes the catalogue.

## 11. Landing-page experience signal from Google — ⛔ BELOW AVERAGE

Google's own keyword-level diagnostic agrees:

| Keyword | QS | Exp. CTR | Ad relevance | **Landing page exp.** |
|---|---|---|---|---|
| `hvac repair near me` (P/E) | **1** | Below avg | Below avg | **Below average** |
| `ac repair near me` (P/E) | **2** | Below avg | Average | **Below average** |

---

## 12. ClickCease redirect test — ⚠️ BLOCKED, not failed

Could **not** be completed from this machine. `monitor.clickcease.com` resolves to **127.0.0.1**
and `www.clickcease.com` refuses connection, while control lookups (googletagmanager.com)
resolve normally and the local `hosts` file is empty. This is a **network-level DNS sinkhole on
the testing machine**, not evidence of a ClickCease outage or a site defect.

**Do not read this as a ClickCease failure.** What is proven statically:

- The account-level `tracking_url_template` is a ClickCease redirect wrapping **every** click:
  `...tracker.aspx?id=…&url={lpurl}&ccpturl=offer.ambientcoolingandheating.com&…`
- `{lpurl}` is used as a **parameter value**, so Google URL-encodes it — the correct ClickCease form.
- None of the five campaigns override it, and `final_url_suffix` is empty account-wide.
- Auto-tagging is ON, so `gclid` should be inside the encoded `{lpurl}`.

**To finish this test**, run `clickcease.py` (in the session scratchpad) from a network that can
resolve `clickcease.com`, or click a live ad and inspect the landing URL. **However, the outcome
does not change the remediation**: §3 proves the form discards attribution regardless.

---

## Remediation draft — no site change is authorized yet

Ordered by business impact. **Applying any of these requires explicit site-scope authorization
and a rollback path**, then a re-render of all five pages at both widths.

| # | Defect | Fix | Severity |
|---|---|---|---|
| 1 | Mobile "Call Now" dials **(410) 914-1456** | Confirm what that number is, then repoint `et_pb_button_5` to `tel:+14107056354` | ⛔ Critical |
| 2 | Form captures no attribution | Configure Gravity Forms dynamic population on `input_9`…`input_15` for gclid, gbraid, wbraid, utm_source/medium/campaign/term/content; fall back to the `_gcl_aw` cookie | ⛔ Critical |
| 3 | Three `#gform_1` instances | Keep one inline form + one modal with **distinct** form IDs, or remove the duplicate embeds | ⛔ High |
| 4 | Two tel hrefs malformed | Normalize every paid-path link to `tel:+14107056354` | ⛔ High |
| 5 | No privacy / terms links | Publish both on the offer subdomain and link from every page footer | ⛔ High |
| 6 | "(optional)\*" but required | Decide one way; make the label and `aria-required` agree | ⚠️ Medium |
| 7 | Cross-service H2s on 2 pages | "Recent HVAC Repair Work"; "Your Gas Boiler Repair in 3 Simple Steps" | ⚠️ Medium |
| 8 | Undocumented pixels (UET, Meta, Nextdoor) | Confirm each is intended and consent-covered | ⚠️ Medium |
| 9 | **Countdown / "before today ends" on all 5 pages** | Remove the timer and every manufactured-deadline line; worsens under 24/7 delivery | ⛔ High |
| 10 | Review quotes unverified, each shown 3× | Verify provenance against the Google Business Profile; de-duplicate | ⚠️ Medium |
| 11 | "honest, upfront pricing" on `/hvac-installation/` | Remove as CONSUMER_FINANCE appeal hygiene | ⚠️ Medium |
| 12 | "Prompt…" callout + page copy, "Call Now" CTA | Replace with non-temporal wording before 24/7 delivery goes live | ⚠️ Medium |
| 13 | No structured data | Add LocalBusiness/Service JSON-LD with `telephone: +1-410-705-6354` | ⚪ Low |
| 14 | Landing-page experience below average | Re-measure after 1–8 land; do not chase before then | ⚪ Low |

## TLS — ✅ PASS (checked 2026-08-18)

| Host | Protocol | Issuer | Expires | Days left |
|---|---|---|---|---|
| `offer.ambientcoolingandheating.com` | TLS 1.3 | Let's Encrypt | 2026-11-11 | 84 |
| `ambientcoolingandheating.com` | TLS 1.3 | Let's Encrypt | 2026-11-09 | 82 |

Both certificates are valid, hostname-matched, and well clear of renewal. Let's Encrypt
auto-renews at 30 days remaining. **No TLS action needed.**

**Not yet measured:** Core Web Vitals. Field data (CrUX) needs a separate query and lab data
needs a Lighthouse pass; neither blocks the Google Ads remediation, and both should be run
*after* the duplicate-form fix, since removing two of the three form instances will change the
numbers.
