# Canonical Landing Page — Developer Handoff

**Client:** Pro Green Landscape Solutions · **Market:** Dallas–Fort Worth, TX
**Google Ads:** Pro Green - Dallas - Live (`8735782888`) · **WhatConverts profile:** ProGreen DFW (`107007`)
**Date:** 2026-08-11 · **Status: SPECIFICATION ONLY — NOT DEPLOYED, NOT APPROVED FOR DEPLOYMENT**

The development team implements WordPress, GTM, Nelio, form, and DNS changes. **Green Marketing
does not have WordPress or Nelio access.** Nothing in this document has been built or deployed.

---

## 1. Final URL and slug

**Recommended final URL**

```
https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/
```

| Component | Value | Why |
| --- | --- | --- |
| Host | `offer.progreenlandscapesolutions.com` | Client-preferred host. A dedicated campaign subdomain keeps paid traffic off the marketing site, so NitroPack, Nelio, and the second GTM container never affect it |
| Slug | `sprinkler-irrigation-repair` | Carries **both** canonical head terms so all three ad groups match |

**Why this slug beats the alternatives**

| Candidate | Verdict |
| --- | --- |
| `/sprinkler-irrigation-repair/` | **Chosen.** Matches `sprinkler repair`, `sprinkler repair services`, `sprinkler system repair`, `irrigation repair services`, `irrigation repair near me` — the five top-spending live keywords |
| `/sprinkler-repair/` | Rejected — under-serves the `Irrigation Repair Near Me` ad group, which is the **highest-converting** group (5 of 5 conversions, $1,141.07) |
| `/sprinkler-repair-dallas/` | Rejected — weakens message match for Fort Worth and Frisco searchers named in the approved positioning; ZIP targeting already handles geography |
| `/offer-sprinkler-repair/` | Rejected — "offer" ties the URL to the **expired** 10% promotion |

**Trailing slash required.** Serve `301` from the non-slash form. One canonical URL only.

---

## 2. Scope

**In scope:** Sprinkler repair · Irrigation repair · Sprinkler head repair · Valve repair

**Out of scope — must not appear anywhere on the page:** new irrigation-system installation ·
irrigation-system design · winterization · general landscaping · any unrelated service

**Approved positioning, verbatim:**

> Professional Irrigation, Sprinkler Repair & Irrigation System Repair in Dallas, Fort Worth &
> Frisco, TX and Surrounding Areas.

---

## 3. Claims policy — enforced at build time

**Verified — approved for use:**

- Licensed and insured
- Free estimates
- 18-point check
- Customer satisfaction guarantee
- Same-day service is sometimes available

**Required same-day wording, verbatim and complete:**

> **Same-Day Service May Be Available.**

**Never** promise or guarantee same-day or emergency service. Never write "Same Day Service",
"Guaranteed Same Day", "24/7 Emergency", or any variant that removes the conditional.

**Prohibited:** 10% OFF or any expired promotion · installation · winterization · general
landscaping · star ratings, review counts, years in business, response-time promises, or awards
**unless separately verified**.

---

## 4. Page structure

Order follows `prompts/06-build-landing-page.md` and the client template
`templates/landing-page/brief.template.yaml`.

| # | Section | Contents |
| --- | --- | --- |
| 1 | **Top CTA bar** | Click-to-call, sticky on mobile |
| 2 | **Hero** | H1, sub-headline, phone CTA, form CTA, trust strip |
| 3 | **Problem and outcome** | The four in-scope failure symptoms |
| 4 | **Service scope** | Sprinkler repair · irrigation repair · sprinkler head repair · valve repair |
| 5 | **Proof / completed work** | Before-and-after imagery |
| 6 | **The 18-point check** | What it covers |
| 7 | **Process** | Three steps, with the conditional same-day line |
| 8 | **Service area** | Approved DFW list |
| 9 | **FAQ** | Buying objections |
| 10 | **Final CTA** | Repeat phone + form |
| 11 | **Footer** | Business name, licensed/insured, service area, privacy link |

No A/B routing. No interstitial. No exit popup that blocks the phone CTA.

---

## 5. Full page copy

> Copy is written to the verified-claims list. Do not add a claim that is not in §3.
> `{{PHONE}}` marks every place the base number renders — see §7.

### 5.1 Top CTA bar

```
Call Now: {{PHONE}}
```

### 5.2 Hero

**H1**

```
Sprinkler & Irrigation Repair in Dallas, Fort Worth & Frisco, TX
```

**Sub-headline**

```
Professional irrigation, sprinkler repair and irrigation system repair across Dallas,
Fort Worth, Frisco and surrounding areas. Licensed and insured, with free estimates
and an 18-point system check on every visit.
```

**Primary CTA button** → `tel:` link

```
Call {{PHONE}}
```

**Secondary CTA button** → scrolls to the form

```
Get My Free Estimate
```

**Trust strip** (four items, icon + label)

```
Licensed & Insured   ·   Free Estimates   ·   18-Point System Check   ·   Satisfaction Guaranteed
```

**Conditional availability line** — directly under the CTAs, smaller type

```
Same-Day Service May Be Available.
```

### 5.3 Problem and outcome

**H2**

```
Sprinkler Problems Waste Water and Damage Your Lawn
```

**Body**

```
A single broken head or leaking valve can flood one area, starve another, and quietly
raise your water bill for months. Most DFW systems fail in the same handful of places,
and most of those failures are a straightforward repair rather than a replacement.

We find the actual fault, show you what is wrong, and give you a free estimate before
any work begins.
```

**Symptom list** — the four in-scope services

```
- Sprinkler heads that are broken, sunken, blocked or spraying the wrong direction
- Zones that will not turn on, will not shut off, or run at low pressure
- Leaking or stuck valves and valve boxes
- Controller and timer faults that leave zones running or skipped
```

### 5.4 Service scope

**H2**

```
What We Repair
```

| Card | Heading | Body |
| --- | --- | --- |
| 1 | `Sprinkler Repair` | `Broken, sunken, clogged and misaligned heads, cracked laterals, and coverage problems that leave dry or flooded patches.` |
| 2 | `Irrigation Repair` | `Mainline and lateral leaks, pressure loss, wiring faults, and zones that have stopped responding.` |
| 3 | `Sprinkler Head Repair` | `Head replacement, nozzle matching, and spray-pattern correction so every zone waters evenly.` |
| 4 | `Valve Repair` | `Stuck, leaking and failed valves, solenoid faults, and valve-box access and repair.` |

### 5.5 The 18-point check

**H2**

```
Every Visit Includes an 18-Point System Check
```

**Body**

```
Before we quote a repair we inspect the whole system, not only the part you noticed.
That is how we catch the second problem that would have brought us back out next month.
```

### 5.6 Process

**H2**

```
How It Works
```

```
1. Call or request an estimate. Tell us what the system is doing.
2. We inspect and diagnose. Free estimate, with the 18-point check included.
3. We repair and confirm. You see every zone run correctly before we leave.
```

**Line under step 1**

```
Same-Day Service May Be Available.
```

### 5.7 Service area

**H2**

```
Serving Dallas, Fort Worth, Frisco and Surrounding Areas
```

**Body**

```
Dallas · Fort Worth · Frisco · Irving · Arlington · Plano · Allen · University Park ·
Grand Prairie · Richardson · Preston Hollow · Highland Park · Lakewood · Farmers Branch ·
Balch Springs · Duncanville · Coppell · Grapevine · Vickery Meadow
```

> **Do not link a city name unless a verified service-area page exists.** Verified pages are
> listed in §12.3. Do not invent URLs for the remaining cities.

### 5.8 FAQ

```
Q: Do you charge for an estimate?
A: No. Estimates are free, and every visit includes an 18-point system check.

Q: Can you come out today?
A: Same-Day Service May Be Available. Call and we will tell you the soonest we can be there.

Q: Are you licensed and insured?
A: Yes. Pro Green Landscape Solutions is licensed and insured.

Q: Do you repair systems you did not install?
A: Yes. We repair existing sprinkler and irrigation systems regardless of who installed them.

Q: What if the repair does not solve it?
A: Our work is backed by a customer satisfaction guarantee. Tell us and we will make it right.

Q: Which areas do you cover?
A: Dallas, Fort Worth, Frisco and the surrounding DFW area. Call to confirm your address.
```

### 5.9 Final CTA

**H2**

```
Get Your Sprinkler System Working Again
```

```
Call {{PHONE}}   |   Get My Free Estimate
Licensed & Insured · Free Estimates · 18-Point System Check
Same-Day Service May Be Available.
```

### 5.10 Footer

```
Pro Green Landscape Solutions
Sprinkler and irrigation repair in Dallas, Fort Worth, Frisco, TX and surrounding areas.
Licensed & Insured.
Call {{PHONE}}
[Privacy Policy]
```

---

## 6. Form specification

**Visible fields** — keep it short.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| Name | text | yes | |
| Phone | tel | yes | `inputmode="tel"`, `autocomplete="tel"` |
| Email | email | yes | `autocomplete="email"` |
| Service address or ZIP | text | yes | Qualifies service area at capture |
| What is the system doing? | textarea | no | Free text |

**Submit button**

```
Get My Free Estimate
```

**Behaviour**

- Accessible labels, not placeholder-only. Visible focus states. Errors announced to screen readers.
- Client-side validation must not block submission on a valid US phone format.
- On success → dedicated thank-you page (§9).
- **Never auto-dial. Never place a call on the user's behalf.**

### 6.1 Hidden attribution fields — required

Populate from the URL, `document.referrer`, and a first-touch cookie. **All must persist across
navigation within the subdomain.**

| Field | Source |
| --- | --- |
| `gclid` | URL |
| `gbraid` | URL |
| `wbraid` | URL |
| `utm_source` | URL |
| `utm_medium` | URL |
| `utm_campaign` | URL |
| `utm_term` | URL |
| `utm_content` | URL |
| `utm_id` | URL |
| `landing_url` | `location.href` on first page view |
| `referrer_url` | `document.referrer` on first page view |
| `original_source` | first-touch value, cookie-persisted |
| `lead_id` | client-generated UUID, used as the dedupe key |
| `consent_state` | current consent value |

**Persistence rule.** Write first-touch values to a first-party cookie on
`.progreenlandscapesolutions.com` with a **90-day** expiry — matching the longest Google Ads
click window in the account (60 days) with headroom. **Never overwrite a first-touch click ID
with a later empty value.**

**Reference:** `templates/landing-page/brief.template.yaml` → `hidden_attribution_fields`.

### 6.2 Why this matters

**[RUNTIME]** The current Gravity Forms implementation exposes `gform_field_values` but leaves it
**empty**, and there are **zero** `gclid`/`gbraid`/`wbraid`/`utm_` strings anywhere in the HTML of
any of the three existing pages. Attribution is captured **only** inside the WhatConverts layer
today. `CLAUDE.md` requires click IDs preserved into the CRM.

---

## 7. Phone-number behaviour — the most important section

**Get this wrong and conversion tracking breaks again.**

| Rule | Requirement |
| --- | --- |
| **Base number in source** | The page **must render `(214) 300-9564`** everywhere `{{PHONE}}` appears — visible text **and** `tel:` href |
| **Never hard-code** | **(214) 301-4622 must never be written into the source.** It is a WhatConverts *pool* number, assigned at runtime |
| **DNI** | WhatConverts replaces the base number at runtime with an available website-pool number |
| **`tel:` hrefs** | Every one must be a valid `tel:` URI **and** must be swapped by WhatConverts together with the visible text |
| **Forbidden** | **`tel:%91phone%93` must not exist anywhere.** It is an unresolved shortcode currently live on both old pages and it does not dial |
| **Call asset** | **(214) 301-3385 stays assigned to the Google Ads call asset `89872541418`.** It must **never** be rendered on this page |
| **No competing replacement** | Google website-call replacement and WhatConverts DNI must **never** target the same number |

### 7.1 Required `tel:` format

```html
<a href="tel:+12143009564" class="wc-phone">(214) 300-9564</a>
```

Both the `href` and the visible text carry the base number so WhatConverts can rewrite both.
Use a consistent, single visible format — **`(214) 300-9564`** — because WhatConverts swaps by
exact string match. Inconsistent formatting is the single most common cause of a partial swap.

### 7.2 The Google `__awcc` conflict — do not recreate it

**[RUNTIME]** On the existing pages, GTM container `GTM-NZSMS9RB` runs an `__awcc` tag configured
to autoreplace **(214) 301-3385** — a number that never renders there — while WhatConverts
replaces **(214) 300-9564**. The Google tag finds nothing to swap, so conversion action
`6886103719` has recorded **nothing since 2026-02-28** **[FRESH-API]**.

**On the new page:**

- **Do not deploy the `__awcc` phone-swap tag.** WhatConverts owns number replacement.
- Keep the **Conversion Linker** (`__gclidw`) — it is required for `gclid` persistence.
- Keep the **Google Ads conversion tag** (`__awct`) for form-submit conversions.
- If Google website-call replacement is ever wanted later, it needs its **own** number that
  WhatConverts does not touch. **Not in this build.**

---

## 8. Tracking requirements

### 8.1 Deploy exactly these — nothing else

| Tag | ID | Purpose |
| --- | --- | --- |
| **GTM** | **`GTM-NZSMS9RB`** | The Green Marketing container — the only one |
| **Google Ads** | **`AW-11237210508`** | Account conversion ID for `8735782888`, verified `conversion_tracking_id` **[FRESH-API]** |
| **GA4** | **`G-5JMRW1LBMF`** | The property already referenced by this account's conversion tag |
| **WhatConverts** | `https://s.ksrndkehqnwntyxlhgto.com/107007.js` | Profile **107007** |

### 8.2 Must NOT be deployed

| Item | Reason |
| --- | --- |
| **`GTM-54Q4TVXF`** | Ownership **[UNVERIFIED]**; **[INFER]** an Austin configuration |
| **`AW-11240766632`** | Not this account's conversion ID. Its `__awcc` targets **(512) 890-2716**, an Austin number |
| **`G-MHX199EBNJ`** | Second GA4 property, deployed by the unverified container |
| Facebook pixel `1455418062885315` | Deployed by the unverified container; not part of this scope |
| Nextdoor pixel `440513cd-3237-4a70-9ca7-0e129ce37252` | Same |
| `__awcc` phone-swap tag | §7.2 |
| **Nelio A/B Testing** | The page must not participate in any experiment |

> **Confirmed rule [USER]:** no Austin language, locations, phone numbers, tags, or assets on the
> Dallas page. `AW-11240766632`, `GTM-54Q4TVXF` and (512) 890-2716 strongly suggest an Austin
> configuration but ownership is **[UNVERIFIED]** — so they are **excluded from the new page**,
> and **nothing about them is changed on the existing pages**.

### 8.3 Load timing — do not defer measurement

**[RUNTIME]** The existing pages run NitroPack, which has been observed deferring all scripts
until user interaction. On a page whose traffic is **100% mobile**, a visitor who lands and
leaves is then completely unmeasured.

**Requirement:** GTM, gtag, and the WhatConverts script must load **without requiring user
interaction**. If any optimiser runs on the new subdomain, all three must be excluded from its
delay/defer list. Verify by loading the page and touching nothing.

### 8.4 Form conversion

- WhatConverts form tracking must capture the submission with the visitor's click IDs.
- Send a Google Ads conversion for the form submit via `GTM-NZSMS9RB` / `AW-11237210508`.
- **Deduplicate on `lead_id`.** Never fire on page load — only on confirmed success.

---

## 9. Thank-you page

```
https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/thank-you/
```

- Server-side redirect after successful submission.
- **Not indexable** — `noindex`.
- Repeat the phone number for immediate contact.
- Set expectations without a time promise: `We received your request and will contact you shortly.`
- **Must not** be reachable directly in a way that would fire a conversion.

---

## 10. Metadata

```html
<title>Sprinkler & Irrigation Repair in Dallas, Fort Worth & Frisco, TX | Pro Green Landscape Solutions</title>
<meta name="description" content="Professional irrigation, sprinkler repair and irrigation system repair in Dallas, Fort Worth, Frisco and surrounding areas. Licensed and insured. Free estimates and an 18-point system check.">
<link rel="canonical" href="https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/">
<meta name="viewport" content="width=device-width, initial-scale=1">
```

**Indexing decision — for the client.** A paid-only landing page is commonly `noindex, follow` to
avoid competing with the main site. **[UNVERIFIED]** — confirm before launch. If it is indexed,
the canonical tag above must stay.

---

## 11. Schema recommendations

`LocalBusiness` JSON-LD, with three cautions:

1. **`telephone` must carry the base number `(214) 300-9564`**, never a pool number.
2. **Do not add `aggregateRating` or `review`** — no rating or review count is verified.
3. **Do not add `openingHours`** unless verified; ad schedule is not the same as business hours.

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Pro Green Landscape Solutions",
  "url": "https://offer.progreenlandscapesolutions.com/sprinkler-irrigation-repair/",
  "telephone": "+1-214-300-9564",
  "areaServed": [
    "Dallas, TX", "Fort Worth, TX", "Frisco, TX", "Irving, TX", "Arlington, TX",
    "Plano, TX", "Allen, TX", "University Park, TX", "Grand Prairie, TX",
    "Richardson, TX", "Preston Hollow, TX", "Highland Park, TX", "Lakewood, TX",
    "Farmers Branch, TX", "Balch Springs, TX", "Duncanville, TX", "Coppell, TX",
    "Grapevine, TX", "Vickery Meadow, TX"
  ],
  "makesOffer": [
    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Sprinkler Repair"}},
    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Irrigation Repair"}},
    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Sprinkler Head Repair"}},
    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Valve Repair"}}
  ]
}
```

**`FAQPage` schema** may mirror §5.8 verbatim. The rendered answers and the schema must match
exactly.

**Do not** add `PriceSpecification` — no pricing is verified.

---

## 12. Images, logo, and links

### 12.1 Image placements

| Slot | Required | Subject | Ratio | Alt-text brief |
| --- | --- | --- | --- | --- |
| `hero` | yes | Technician repairing a sprinkler head in a DFW residential lawn | 16:9 | Describe the action and the location type; no claims |
| `proof_1` | yes | Before/after of a repaired zone or head | 4:3 | State what was repaired |
| `proof_2` | yes | Valve box repair or leak repair in progress | 4:3 | State the component |
| `process_or_team` | optional | Branded vehicle or technician with equipment | 3:2 | Neutral description |
| `logo` | yes | **Current approved Pro Green Landscape Solutions logo** | — | `Pro Green Landscape Solutions` |

**All images must be client-approved and depict real Pro Green work.** Do not use stock imagery
that implies work the company did not perform. Serve WebP/AVIF with fallbacks, explicit
`width`/`height` to prevent CLS, `loading="lazy"` below the fold, **never** on the hero.

### 12.2 Logo

**[RUNTIME]** The existing `offerdfw` page carries a `ProGreen LANDSCAPE SOLUTIONS` logo. Confirm
with the client that it is the **current approved** version before reuse.

### 12.3 Verified service-area pages — the only linkable ones

```
/dfw/service-areas/dallas/          /dfw/service-areas/fort-worth/
/dfw/service-areas/frisco/          /dfw/service-areas/irving/
/dfw/service-areas/arlington/       /dfw/service-areas/plano/
/dfw/service-areas/allen/           /dfw/service-areas/university-park/
/dfw/service-areas/grand-prairie/   /dfw/service-areas/richardson/
/dfw/service-areas/preston-hollow/
```

**Do not fabricate URLs** for Highland Park, Lakewood, Farmers Branch, Balch Springs,
Duncanville, Coppell, Grapevine, or Vickery Meadow. Name them as text only.

---

## 13. Performance and responsive requirements

| Requirement | Target |
| --- | --- |
| LCP | **≤ 2.5 s** on 4G mobile |
| CLS | **≤ 0.1** |
| INP | **≤ 200 ms** |
| Measurement scripts | **Never deferred until interaction** (§8.3) |
| Render-blocking | Inline critical CSS; defer non-critical |
| Fonts | `font-display: swap`; self-host or preconnect |

**Mobile — the priority.** 100% of current campaign traffic is mobile **[FRESH-API]**.

- Sticky click-to-call bar, always reachable.
- Tap targets ≥ 44×44 px.
- Form usable one-handed; correct `inputmode` per field.
- The phone CTA must be visible **without scrolling** on a 360×640 viewport.
- No horizontal scroll at 320 px.

**Desktop.** Desktop is being re-enabled in Batch 2, so the page must be fully functional there —
readable line lengths, visible phone number in the header, form above the fold at 1366×768.

**Accessibility.** WCAG 2.1 AA: contrast ≥ 4.5:1, keyboard-navigable, visible focus, labelled
form controls, logical heading order (one `h1`).

---

## 14. Prelaunch QA checklist

Run on staging. **No test lead may be submitted to production.**

**Content**
- [ ] H1 matches §5.2
- [ ] Approved positioning present
- [ ] Only the four in-scope services appear
- [ ] **No** installation, design, winterization or general-landscaping content
- [ ] **No 10% OFF or any expired promotion**
- [ ] Same-day wording is exactly **"Same-Day Service May Be Available."**
- [ ] No unverified claim, rating, review count, or response-time promise
- [ ] No Austin content, city, or phone number

**Phone**
- [ ] Source renders **(214) 300-9564** in every `{{PHONE}}` slot
- [ ] **(214) 301-4622 appears nowhere in the source**
- [ ] **(214) 301-3385 appears nowhere on the page**
- [ ] **Zero occurrences of `tel:%91phone%93`**
- [ ] Every `tel:` href is a valid URI
- [ ] WhatConverts swaps visible text **and** `tel:` href together
- [ ] Visible number format is consistent everywhere

**Tracking**
- [ ] `GTM-NZSMS9RB` loads; **`GTM-54Q4TVXF` does not**
- [ ] `AW-11237210508` present; **`AW-11240766632` absent**
- [ ] `G-5JMRW1LBMF` present; **`G-MHX199EBNJ` absent**
- [ ] No Facebook or Nextdoor pixel
- [ ] **No `__awcc` phone-swap tag**
- [ ] Conversion Linker active
- [ ] WhatConverts `107007.js` loads
- [ ] **All tags fire with zero user interaction**
- [ ] No Nelio script; no redirect

**Form and attribution**
- [ ] All hidden fields in §6.1 exist
- [ ] Loading with test URL parameters populates them — **read in the DOM only, do not submit**
- [ ] Values persist across an internal navigation
- [ ] `lead_id` generated and unique
- [ ] Thank-you page is `noindex`

**Performance and accessibility**
- [ ] LCP / CLS / INP targets met on throttled mobile
- [ ] 360 px, 768 px, 1366 px all clean
- [ ] Contrast and keyboard navigation pass

---

## 15. Postlaunch verification

**Before repointing any ad** (Batch 1B step 3)
- [ ] Page live at the canonical URL, `200`, no redirect chain
- [ ] Full §14 checklist re-run against production
- [ ] WhatConverts shows the page and swaps correctly

**After repointing** (Batch 1B step 5)
- [ ] GAQL read-back: all three ads carry the new final URL
- [ ] A real ad click lands on the canonical page with `gclid` intact
- [ ] WhatConverts records the visitor with the click ID
- [ ] `6886101052` and `6617381255` keep recording
- [ ] **No conversion increase attributable to duplication**
- [ ] A genuine customer lead — **never a test lead** — carries full attribution

**One week after**
- [ ] WhatConverts call log reconciles 1:1 with `6617381255`
- [ ] Zero duplicate conversions
- [ ] CPL trend recorded against the **$120** target

---

## 16. Rollback

| Scenario | Action |
| --- | --- |
| Page fails QA | Do not repoint. No Google Ads change was made; nothing to roll back |
| Problem found after repointing | Restore the exact prior final URLs — `714659486058` → `…/offer-sprinkler-repair-b/`, `797294303667` → `…/offer-sprinkler-repair-a/`, `797325463324` → `…/offer-sprinkler-repair-a/`. **Nelio 3619 is still running at this stage, so the old pages remain functional** |
| Tracking regression | Republish the prior GTM version — GTM retains full version history |
| Phone swap fails | Revert the page template; WhatConverts config is unchanged, so the old pages still swap |
| Total rollback | Old pages, Nelio, and all conversion actions are untouched until step 8. **Every step before 8 is fully reversible** |

**This is why Nelio is ended last.** Until step 8 the old pages remain live and the rollback path
stays open.

---

## 17. Local implementation files

Reference implementation lives at:

```
clients/pro-green-dallas/landing-page-draft/   ← LOCAL ONLY, NOT DEPLOYED
```

It is a **specification aid**, not a deployable artifact. It contains no real tag IDs wired to
live containers and must not be uploaded, deployed, or published.
