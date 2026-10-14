# Ambient Cooling & Heating — website tracking fixes **v2** (ClickUp-ready)

> **Supersedes** `2026-09-18-ambient-tracking-fixes.md`. That version told you to replace a
> hard-coded phone number. **That was wrong** — further testing proved the number is injected
> by WhatConverts DNI, not written into the template. Work from this version only.

**Site:** ambientcoolingandheating.com (main site, **not** the `offer.` subdomain)
**Blocking:** two paid Search campaigns, built and approved, that cannot be enabled until this ships
**Evidence:** `clients/ambient-cooling-heating/snapshots/tracking-retest-2026-09-17.json`; 14 clean
no-parameter visits desktop + mobile across 7 pages (2026-09-17), plus 6 further no-parameter
loads (2026-09-18)

---

## Already working — do not "fix" these

| Item | Status | Evidence |
|---|---|---|
| GTM `GTM-PQTPQ436` | ✅ working | loads on 14/14 visits |
| GA4 `G-9X9ZHNCRWF` | ✅ working | `/g/collect` on 14/14 |
| Google Ads tag `AW-11155434808` | ✅ working | 4 `viewthroughconversion/11155434808` requests per visit, 14/14 |
| WhatConverts library | ✅ loads | `wc_visitor`, `wc_client` cookies; `wc_visitor_init` global |
| Cross-visitor cache replay | ✅ not reproducing | 8 cache HITs returned empty attribution fields; markers pushed hours earlier did not come back |

---

## 1. 🔴 BLOCKER — phone numbers: three separate faults

### What we proved about where the number comes from

| Load | `wc_swap` cookie | Number in DOM |
|---|---|---|
| 2026-09-17, 14 visits | set (`4109141456+..+4107610932+..+230773`) | **410-914-1456** |
| 2026-09-18, 6 loads | **absent** | **410-761-0932** |

The rendered number tracks **exactly** with whether WhatConverts DNI ran. Conclusion:
**`410-914-1456` is injected by WhatConverts DNI. It is not in your template.** The base
number in the page is **`410-761-0932`**.

> Caveat, stated honestly: we could not capture the raw server HTML directly — SG-Captcha
> answers automation with a `202` stub, so the body read back as 0 bytes. The conclusion rests
> on the DOM/`wc_swap` correlation, which is consistent across 20 loads. **Please confirm from
> your side** with a template/theme search for `914-1456`. If it *is* in the template, tell us
> — that changes the fix.

### ⚠️ AMENDED 2026-09-18 — owner decision: turn DNI OFF on this site

The client has decided: **while paid traffic runs to the main website, the main website must
display the main business number for every visitor — paid and organic alike.** The WhatConverts
tracking number stays in Google Ads as a **call asset**, not on the page.

This is already correctly configured on the Ads side — call asset `407995613637` carries
`(410) 705-6354` and is linked to all seven campaigns. **No Google Ads change is needed.**

### 1a. Required end state

| Visitor | Number that must render and be in every `tel:` href |
|---|---|
| Organic / direct | **`410-761-0932`** (main business number) |
| Google paid | **`410-761-0932`** — the same |

- `410-914-1456` must **never** render or be clickable.
- `410-705-6354` must **not** be placed on the page. It lives only in the Google Ads call asset.
- **Disable WhatConverts dynamic number insertion for `ambientcoolingandheating.com`.** Do not
  reconfigure the pool, do not scope it to paid sessions — switch DNI off for this domain.
  Leave the WhatConverts *library* loading (it is doing useful session tracking); only the
  number-swap behaviour must stop.

> Call attribution for paid traffic is preserved through the Google Ads call asset and its
> forwarding number, so turning DNI off on the site does not lose paid-call measurement.

### 1b. 🔴 The race condition disappears, but verify it

Turning DNI off also removes the timing defect: DNI fired on some loads and not others, and
only after a scroll because NitroPack defers JavaScript. With the number static in the
template, it is correct at first paint.

**Still required:** confirm the number is present and correct **before any interaction**, and
that no script rewrites it afterwards.

**Done when:** across 10 consecutive cold loads, desktop and mobile, the visible number and
every `tel:` href are **`410-761-0932`**, present and correct **before any interaction**, with
neither `410-914-1456` nor `410-705-6354` appearing anywhere in the DOM.

---

## 2. 🔴 BLOCKER — duplicate form and field IDs

**101 duplicated DOM ids per page**, identical on desktop and mobile. The entire form is in
the DOM **twice**:

```
form id="gform_2"   x2      (36 fields each, both with a submit button)
input_2_1  input_2_17  input_2_3  input_2_4  input_2_5
input_2_9_1  input_2_9_3  input_2_9_4  input_2_9_5  input_2_9_6
input_2_7   input_2_10 … input_2_16        ← all duplicated
gform_theme_2  gform_style_settings_2
gform_target_page_number_2  gform_source_page_number_2
et-boc,  menu-item-231/236/2941/1893/1890 …
```

25 duplicated `<input>` ids on top of the duplicated menu/layout ids.

**Why this is a launch blocker:** `getElementById('input_2_14')` returns only the **first**
match. The client-side attribution script in §3 will write the GCLID into one copy while the
visitor submits the other — the value silently never arrives. It also breaks GA4/GTM form
tracking and is invalid HTML.

**Fix at the template level. Do not hide one copy with CSS** — a CSS-hidden duplicate still
has the same ids and still breaks `getElementById`. Render **one** form per page and control
layout responsively, or give each instance genuinely unique ids (`gform_2_mobile`, …).

**Done when:** `document.querySelectorAll('#gform_2').length === 1`, and the page's total id
count equals its unique id count.

---

## 3. 🔴 Client-side attribution capture and persistence

The hidden capture fields already exist and are correctly **empty** on a clean visit:

```
input_2_10  input_2_11  input_2_12  input_2_13  input_2_14  input_2_15  input_2_16
```

⚠️ **`input_16` is the Gravity Forms honeypot.** Never write to it, never make it visible —
filling it flags the submission as spam.

**Required:**

- Capture all eight parameters **in JavaScript, after page load**: `gclid`, `gbraid`,
  `wbraid`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`.
- **There is currently no field for `gbraid` or `wbraid` — add two.** Without them, iOS and
  privacy-restricted click IDs are lost even when everything else works.
- Populate **every rendered form** on the page with the **current** visitor's values (relevant
  until §2 lands, and a permanent safeguard afterwards).
- **Never server-render attribution into HTML.** No PHP, no Gravity Forms dynamic population.
  Server-rendered values get stored in the full-page cache and served to the next visitor —
  that was the 2026-09-16 defect and it must not return.
- Persist to first-party storage (`localStorage` + a first-party cookie, ~90 days) and restore
  on later pages so attribution survives navigation.
- First-touch wins; never overwrite a stored click ID with an empty value.

---

## 4. Caching

`x-nitro-cache: HIT` on 14/14 and `x-proxy-cache: HIT` on 8/14. With §3 done client-side this
is safe, because the cached HTML then holds no visitor-specific values.

**Required:** confirm no attribution value ever appears in the server response body, and after
deploying **purge all four layers: NitroPack, WordPress (object/page cache), the CDN, and the
SiteGround hosting cache.** A partial purge will leave the old markup live.

See §1b — NitroPack's JS-deferral setting still matters for §3 attribution capture, which must complete before the visitor submits.

---

## 5. Developer self-test (5 minutes)

1. Incognito window. Load:
   `https://ambientcoolingandheating.com/services/heating-services/furnace-repair/?gclid=DEVTEST123&gbraid=DEVTEST456&utm_source=google&utm_medium=cpc&utm_campaign=devtest`
2. **Before scrolling or clicking**, check the visible phone number and every `tel:` href.
   They must already be correct. If they change after you scroll, §1 is not fixed.
3. Console → `document.querySelectorAll('#gform_2').length` → must be **1**.
4. Console → `[...document.querySelectorAll('[id]')].length` vs
   `new Set([...document.querySelectorAll('[id]')].map(e=>e.id)).size` → must be **equal**.
5. Console → confirm the hidden fields hold **your** `DEVTEST123` / `DEVTEST456`.
6. Console → `document.body.innerHTML.includes('914-1456')` → must be **false**.
7. Navigate to another service page → stored values must persist.
8. **Second** incognito window, **no parameters at all** → every attribution field must be
   **empty** and the number must be the base `410-761-0932`. If you see `DEVTEST123`, the cache
   is leaking — stop and tell us.
9. Purge all four cache layers. Repeat step 8.

---

## 6. Out of scope

- **Do not submit the live form.** No authorised QA identity is on file; a real submission
  creates a real lead in the client's CRM.
- Do not change the Google Ads tag, GTM container, GA4 property, or the WhatConverts *library*
  — all verified working. §1 is a DNI **configuration** change only.

---

## 7. What we do after you deploy

Tell us when it is live **and stay available for an immediate cleanup purge.** We will retest
both launch pages with isolated desktop and mobile visitors (unique GCLID+UTMs; unique
GBRAID/WBRAID; and a no-parameter control), verify cached HTML is visitor-safe, and only then
release the paid campaigns. We will not call this fixed until that retest passes.

---

## 8. 🔴 NEW — `/services/heating-services/heat-pumps/` fails Google's destination check

Google rejects this exact URL with `DESTINATION_NOT_WORKING`, verified again on 2026-09-18.
It is the **only** page of the seven tested that fails — every other heating URL passes — so
this is not bot protection, it is specific to this page.

```
OK        /services/heating-services/
OK        /services/heating-services/furnace-repair/
REJECTED  /services/heating-services/heat-pumps/     <-- DESTINATION_NOT_WORKING
OK        /services/heating-services/boiler-repair/
OK        /services/heating-services/oil-furnace-installations/
OK        /services/heating-services/oil-replacement/
OK        /services/cooling-services/mini-splits/
```

The page loads fine in a normal browser, so please check what Google's crawler sees: server
response code for AdsBot/Googlebot, redirect chains, `robots.txt`/meta-robots, canonical tag,
and any plugin or security rule scoped to that URL.

**This blocks all four heat-pump services** (repair, replacement, installation, maintenance)
from being advertised. We will not point heat-pump ads at a different URL to work around it.

### Related: duplicate service URLs

The same service is published at several paths, which splits SEO signals and makes ad
destinations ambiguous:

```
/services/heat-pumps/   /services/heating-services/heat-pumps/   /services/indoor-air-quality/heat-pumps/
/services/mini-splits/ (via /hvac/ and /indoor-air-quality/)      /services/cooling-services/mini-splits/
/services/geothermal/   /services/geothermal-hvac/                /services/hvac/geothermal-hvac/
```

The short-path versions (`/services/furnaces/`, `/services/boilers/`, `/services/heat-pumps/`,
`/services/hvac-repair/`, `/services/oil-replacement/`, `/services/geothermal/`) render the
**generic site H1** - "HVAC, AIR CONDITIONER REPAIR & HEATING SERVICES" - not a service-specific
one. They look like leftover shells. Please confirm which path is canonical for each service and
301 the rest. Not launch-blocking, but it limits which services we can advertise.

---

## 9. RETEST 2026-09-18 (later) — nine destinations, desktop + mobile

Full matrix: `clients/ambient-cooling-heating/snapshots/expansion-url-qa-2026-09-18.json`

### 9a. DNI is firing again on ALL nine pages

Earlier today DNI was intermittent. It is now swapping on **every** page, desktop and mobile:
`wc_swap = 4109141456+..+4107610932+..+230773`, and the only `tel:` destination rendered is
`4109141456`. The base number `410-761-0932` is **not** in the DOM on any of the nine.

This confirms §1 is real and current, and that the intermittency is a race, not a fix.

### 9b. 🔴 The offer page exposes TWO wrong numbers

`https://offer.ambientcoolingandheating.com/gas-boiler-repair/` renders **both**:

```
tel: 4107056354   <-- the Google Ads call asset number, must NOT be on any page
tel: 4109141456   <-- the DNI number, must never appear
```

Neither belongs there. That page must also show `410-761-0932` only.

### 9c. 🔴 Unverified claims on live landing pages

These are on pages we are paying to send traffic to. Our ad copy deliberately does not mirror
any of them, but the pages themselves should be corrected — they are superlative and guarantee
claims with nothing recorded to support them.

| Page | Exact wording found |
|---|---|
| `/services/heating-services/furnace-repair/` | "we have earned our reputation as the **most trusted** partner for furnace repair in Maryland" |
| `/services/cooling-services/mini-splits/` | "We are the **most trusted** and experienced technicians"; "**Guaranteed** Professionalism and Customer Satisfaction"; "we have earned our reputation as the **best HVAC company**" |
| `/services/hvac/geothermal-hvac/` | "the area's **most trusted** provider"; "the **guaranteed** improvement to indoor air quality"; "We are the **most knowledgeable** and experienced experts" |

The first two are the destinations of campaigns that are already built and approved, so this
is not a new-services-only issue.

### 9d. Duplicate DOM IDs confirmed on both properties

| Property | Duplicate ids per page | Forms rendered |
|---|---|---|
| main site (7 heating pages) | **101** | 2 |
| `offer.` subdomain (gas-boiler-repair) | **54** | 3 |

§2 applies to both properties, not just the main site.

### 9e. What passed

On every one of the nine destinations, on desktop and mobile: GTM `GTM-PQTPQ436`, GA4
`G-9X9ZHNCRWF`, Google Ads `AW-11155434808` and WhatConverts all load; a Privacy link and a
Terms link are present; and there is no horizontal overflow at 390px.

`HTTP 202` appears on many loads — that is the SiteGround CAPTCHA stub served to automation,
after which the real page renders. It is a test-client obstacle, not a page fault.

### 9f. Still outstanding from §8

`/services/heating-services/heat-pumps/` remains `DESTINATION_NOT_WORKING` — 3/3 fresh checks
today, on top of 4/4 yesterday. Every other destination now passes Google's check (8 of 9).

