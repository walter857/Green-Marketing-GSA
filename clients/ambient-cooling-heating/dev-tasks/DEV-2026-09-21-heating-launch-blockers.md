# Ambient Cooling & Heating — developer correction list

**Raised:** 2026-09-21
**Raised by:** Green Marketing (Google Ads)
**Scope:** the nine heating/cooling landing pages used as Google Ads final URLs
**Authorisation:** none of the items below has been changed by Green Marketing. No
WordPress, SiteGround, GTM, WhatConverts or DNS change is authorised under the current
work order. This is a report, not a change log.

**Evidence files** (all read-only, zero parameters sent, zero forms submitted, zero
telephone links activated):

| File | What it proves |
|---|---|
| `snapshots/expansion-url-qa-2026-09-20.json` | Per-destination render, phone, form, claim scan (desktop + mobile) |
| `snapshots/adsbot-probe-2026-09-20.json` | HTTP 202 behaviour for AdsBot vs a normal browser, 3 trials each |
| `snapshots/dest-policy-2026-09-20.json` | Google Ads' own verdict per destination, identical ad body |
| `snapshots/tracking-retest-2026-09-21.json` | Tag stack, cookies, cross-visitor leak check, 9 pages × 2 devices |
| `snapshots/page-copy-2026-09-20.json` | Full visible copy per page, for claim verification |

---

## BLOCKER 1 — the barred telephone number is displayed and clickable on 8 of 9 pages

**Severity:** launch-blocking. No heating ad may be enabled while this is true.

**Approved telephone policy**

| Number | Correct role |
|---|---|
| `(410) 761-0932` | The number that must display on the website and sit behind every `tel:` link |
| `(410) 705-6354` | Google Ads call asset only. Not a website number |
| `(410) 914-1456` | **Must never appear and must never be clickable** |

**Observed on 2026-09-21, every main-site destination, desktop and mobile:**

- `(410) 914-1456` is rendered *and* clickable. On the Furnace Repair page it appears in
  seven `tel:` links, four of them visible, with visible link text `CALL NOW` and
  `(410) 914-1456`.
- `(410) 761-0932` does **not** appear anywhere in the served HTML.

**Cause — this is WhatConverts DNI, not a hardcoded number.** The `wc_swap` cookie reads
identically on all nine destinations:

```
wc_swap = 4109141456+..+4107610932+..+230773
```

Read that as: *swap profile 230773 replaces `4107610932` with `4109141456`.* The page's
base number is the correct `(410) 761-0932`; WhatConverts dynamic number insertion is
overwriting it in the DOM with the barred pool number.

**Correction required:** disable WhatConverts DNI for the `ambientcoolingandheating.com`
domain (swap profile `230773`), so the base number `(410) 761-0932` renders and is the
`tel:` target. Do **not** delete GTM, GA4, the Google Ads tag, or the WhatConverts account
— only the number-swap behaviour for this domain is in scope.

**Also note:** on `offer.ambientcoolingandheating.com/gas-boiler-repair/` both
`(410) 705-6354` and `(410) 914-1456` are present in the HTML. The Ads call-asset number
should not be hardcoded into page content, and the barred number should not be there at all.

**Retest:** Green Marketing re-runs the nine-page QA after deployment. A page is not
accepted as fixed on report.

---

## BLOCKER 2 — Heat Pump page is rejected by Google Ads as a destination

**Severity:** launch-blocking for the Heat Pump Installation ad group only.

**URL:** `https://ambientcoolingandheating.com/services/heating-services/heat-pumps/`

**Verdict:** `DESTINATION_NOT_WORKING`, 0 of 3 validation trials passed on 2026-09-21
(also 0/3 on 2026-09-18 and 0/4 on 2026-09-17).

**This is specific to this one URL.** The same ad body, submitted to eight other Ambient
destinations in the same run, passed 3/3 every time — including two pages already serving
live ads. So it is not the ad copy, not the account, and not a site-wide condition.

**Yet the page itself looks healthy:** HTTP 200 in a real browser, correct canonical,
correct H1 (`Heat Pumps in Severn, Severna Park & Columbia, MD`), working form, privacy and
terms links present, no mobile overflow.

**Action required:**

1. Developer to confirm nothing serves differently to Google's crawlers on this path
   specifically — check any path-level rule in SiteGround, NitroPack, `robots.txt`, a
   security plugin, or a redirect rule that names `heat-pumps`.
2. Green Marketing to request a policy re-review in the Google Ads interface once
   BLOCKER 3 is addressed.

**Explicitly not doing:** substituting a different or non-canonical URL to get around the
verdict. The ad group will be created PAUSED with keywords but **no ads**, and will stay
unable to serve until the page clears.

**Commercial note:** heat pump is historically the *best*-performing heating theme in this
account — $8,527.47 for 26 conversions, CPA $327.98, average CPC $15.34. This block is
costing the best heating opportunity, so it is worth real developer attention.

---

## BLOCKER 3 — SiteGround serves HTTP 202 (CAPTCHA challenge) to every non-rendering client

**Severity:** high. Most likely root cause of BLOCKER 2 and a standing risk to every ad.

**Observed 2026-09-21, all nine destinations, 3 trials each:**

| Client | Result |
|---|---|
| Plain HTTP, `AdsBot-Google` UA | HTTP **202**, 3/3 |
| Plain HTTP, `AdsBot-Google-Mobile` UA | HTTP **202**, 3/3 |
| Plain HTTP, ordinary Chrome UA (control) | HTTP **202**, 3/3 |
| Full browser render, AdsBot UA | Real page, 2/2 |

The 202 is **not** targeted at Google — a normal browser UA gets it too. It is
SG-Captcha's challenge response to any client that does not execute JavaScript. A
JavaScript-capable crawler works through it; a non-rendering fetch never sees the page.

Google's landing-page checks do not all render. A 202 challenge stub is a well-known cause
of `DESTINATION_NOT_WORKING`.

**Correction required:** allowlist Google's crawlers in SG-Captcha / the SiteGround
security layer so `AdsBot-Google`, `AdsBot-Google-Mobile` and `Googlebot` receive HTTP 200
with full HTML and no challenge. Verify against Google's published crawler IP ranges rather
than on user-agent string alone.

---

## DEFECT 4 — duplicate DOM ids and duplicate form ids on every page

**Severity:** medium. Not launch-blocking, but it corrupts form analytics and is invalid HTML.

| Page group | Duplicate element ids | Forms | Form ids |
|---|---|---|---|
| 8 main-site destinations | **101 per page** | 2 | both `gform_2` — duplicated |
| `offer.` Gas Boiler Repair | **54** | 3 | duplicated |

Two separate `<form>` elements carry the same `id="gform_2"`, and each carries 36 identically
named inputs. Requirements for this project state form and field DOM ids must be unique.

**Consequence:** `document.getElementById` returns only the first match, so any tag,
listener or attribution script bound by id silently reads or writes the wrong form. Field
values captured for attribution cannot be trusted while this is true.

**Correction required:** render one form per page, or give the second instance a distinct
`id` and distinct input `id`s. The duplicate-id count should reach 0.

---

## DEFECT 5 — unverifiable claims in page copy

**Severity:** medium. Not launch-blocking today because no proposed ad repeats any of them,
but the pages are the destination and the copy is the advertiser's own statement.

`client.yaml` records these as barred unless separately verified: price or pricing,
discount or dollar offer, response-time promise, same-day or emergency availability, years
in business, licence number, insurance, rating or review count, guarantee or warranty,
manufacturer certification.

| Page | Phrase found |
|---|---|
| Geothermal HVAC | "Top Geothermal HVAC Technicians in Maryland" |
| Geothermal HVAC | "most knowledgeable and experienced experts" |
| Geothermal HVAC | "Guaranteed" |
| Mini Splits | "Guaranteed Professionalism and Customer Satisfaction" |
| Mini Splits, Furnace Repair, Heat Pumps | "most trusted" |

**Correction required:** either remove the superlative and guarantee language, or supply
Green Marketing with the evidence that substantiates each claim so it can be recorded in
`client.yaml` as verified. Until then no ad will carry these claims, which weakens
ad-to-page message match.

---

## BLOCKED TEST — one authorised `TEST — DO NOT DISPATCH` submission

Green Marketing is required to prove, with a single controlled submission, that:

1. the submitted record carries the test visitor's own attribution;
2. WhatConverts receives it;
3. Google Ads records exactly one appropriate primary conversion;
4. no duplicate CRM dispatch or callback occurs.

**This test has not been run, and the only reason is that no test identity has been
approved for production QA.** Green Marketing will not invent a test email address or
telephone number, because either would land in the client's live CRM and could trigger a
real callback to a real person.

**Needed from the client:** one email address and one telephone number, explicitly approved
for production QA submissions, plus confirmation of who to notify so the test record is not
worked as a real lead.

## BLOCKED TEST — parameterised attribution and cross-visitor replay

The following cannot be confirmed without sending real click-ID parameters to the live site:
GCLID, GBRAID and WBRAID capture; `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`
and `utm_content` capture; first-party persistence through navigation; and the correct
values being written into the submitted form.

**Why it has not been run:** attribution is populated server-side and the response is held
in the SiteGround full-page proxy cache (`x-proxy-cache: HIT` observed again on
2026-09-21). A synthetic GCLID sent now can be cached and then served to real visitors,
which would corrupt live attribution for everyone who lands on that page.

**What a clean no-parameter check does show (9 pages × 2 devices, 2026-09-21):** GTM
`GTM-PQTPQ436`, GA4 `G-9X9ZHNCRWF`, Google Ads `AW-11155434808` and WhatConverts all load
after normal page interaction; `wc_visitor` is set on every page; and **zero** foreign
attribution values appear in any form field.

Zero foreign values is necessary but **not** sufficient. It does not prove the cache defect
is fixed — it only proves no stale value is being replayed right now. Proving the fix
requires the A/B cross-visitor test.

**Needed to run it:** a developer on standby to purge the SiteGround and NitroPack caches
immediately after the test, in a pre-agreed window.

---

# UPDATE 2026-09-22 — three new defects found during the live cutover

The heating transition is now live. These were found while testing destinations and
submitting the two authorised test forms. None was introduced by Green Marketing.

## NEW BLOCKER 6 — every main-site page advertises SAME DAY service

**Severity: high. This is a truthfulness problem, not a cosmetic one.**

Every page on `ambientcoolingandheating.com` carries a site-template banner:

```
CONTACT AMBIENT FOR SAME DAY HVAC SERVICES TODAY!   Call Now   (410) 914-1456
```

Ambient's own published hours are **Monday–Friday 08:00–16:00, closed Saturday and
Sunday** — confirmed in the contact-page text *and* in the page's `schema.org`
`OpeningHoursSpecification` (`opens 08:00`, `closes 16:00`, Mon–Fri only). The owner has
separately confirmed calls are answered during business hours only.

A same-day promise the business does not offer is a misrepresentation risk on pages that
are live Google Ads destinations, and it sits next to the barred phone number.

**Correction required:** remove the same-day claim from the site template, or replace it
with the real hours. **No Green Marketing ad carries this claim**, and the Emergency
Heating Repair and No Heat Repair ad groups have been deliberately left PAUSED for the
same reason.

## NEW BLOCKER 7 — Google Ads call tracking points at a dead number

Both form integrations fire a Google call-metrics request on page load:

```
https://www.googleadservices.com/pagead/conversion/11155434808/wcm?cc=ZZ&dn=4104159517
```

`dn=4104159517` is **(410) 415-9517**, a legacy number that appears on neither the main
site nor the offer subdomain. The Google Ads website-call swap is bound to a number that
is no longer published, so it cannot swap anything and website-call conversions from this
path cannot be attributed.

**Correction required (Google Ads side, Green Marketing will action):** repoint or retire
the website call conversion. Recorded here so the numbers stay consistent with the site.

## NEW DEFECT 8 — offer-form honeypot id differs from other sites

On `offer.ambientcoolingandheating.com`, the Gravity Forms honeypot is **`input_1_27`,
labelled "Name"**, hidden from humans. It is *not* the `input_9` used elsewhere. Anyone
automating or testing this form must read the field map from the page. Filling the
honeypot makes a working form look broken. No action needed — recorded so it is not
rediscovered the hard way.

---

# Test submissions completed 2026-09-22

Two submissions, one per distinct form integration, using the owner-authorised identity
and the label `TEST — DO NOT DISPATCH` in the message body. **Zero URL parameters were
sent**, because the SiteGround full-page proxy cache is shared and no purge method is
available — a synthetic click id could have been cached and replayed to real visitors.

| Integration | Result | Google Ads signal |
|---|---|---|
| `gform_2` on `/heating-services/furnace-repair/` | Submitted, confirmed in place | `en=form_submit` to `AW-11155434808` |
| `gform_1` on `offer.…/gas-boiler-repair/` | Submitted, redirected to `/thank-you/` | `en=form_submit` **and** `en=conversion` |

**Two things these tests did NOT prove, stated plainly:**

1. **WhatConverts receipt is unverified.** `WHATCONVERTS_API_TOKEN` in `.env` is empty, so
   there is no API access to confirm the two leads arrived. Please confirm in the
   WhatConverts UI that two leads dated 2026-09-22 with the `TEST — DO NOT DISPATCH` label
   are present, and suppress any dispatch or callback. Green Marketing could not suppress
   automation from outside the CRM.
2. **Click-ID attribution is unproven.** No GCLID, GBRAID, WBRAID or UTM was sent, by
   design. Neither form carries any hidden attribution input at all, so WhatConverts must
   be reading attribution server-side from its own cookie. A synthetic click id would test
   capture but would still not prove a real Google-Ads-attributed conversion. That test
   needs a developer on standby to purge both caches immediately afterwards.
