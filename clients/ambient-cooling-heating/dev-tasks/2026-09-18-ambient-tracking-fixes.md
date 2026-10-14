# Ambient Cooling & Heating — website tracking fixes (ClickUp-ready)

> ⛔ **SUPERSEDED 2026-09-18 by `2026-09-18-ambient-tracking-fixes-v2.md`. Do not work from this file.**
>
> It instructed the developer to replace a hard-coded phone number. That was **wrong**:
> `410-914-1456` is injected by WhatConverts DNI, not written into the template. This version
> also omitted the paid-number requirement, the DNI-before-tap race condition, the
> template-level (not CSS) de-duplication requirement, and the WordPress/CDN cache layers.


**Site:** ambientcoolingandheating.com (main site, not the `offer.` subdomain)
**Raised:** 2026-09-18 · **Blocking:** two paid Search campaigns that cannot be enabled until items 1 and 2 below are done
**Verified by:** real-browser test, desktop + mobile, 7 pages, 14 clean no-parameter visits, 2026-09-17/18
**Evidence file:** `clients/ambient-cooling-heating/snapshots/tracking-retest-2026-09-17.json`

---

## Read this first — what is NOT broken

Two items that were on the original list are already working. Please do not "restore" them;
just confirm them at the end.

| Item | Status | Evidence |
|---|---|---|
| Google Ads tag `AW-11155434808` | ✅ **working** | Fires 4 `googleads.g.doubleclick.net/pagead/viewthroughconversion/11155434808/` requests on every one of the 14 test visits |
| WhatConverts initialisation | ✅ **working** | `wc_visitor`, `wc_swap`, `wc_client` cookies set on all 14 visits; `wc_visitor_init` / `wc_form_ypbib` globals present |
| GTM `GTM-PQTPQ436` | ✅ **working** | Loads on all 14 visits |
| GA4 `G-9X9ZHNCRWF` | ✅ **working** | `/g/collect` hits on all 14 visits |
| Cross-visitor cache replay of attribution | ✅ **appears fixed** | 14 clean visits, `x-proxy-cache: HIT` on 8 of them, and **zero** foreign GCLIDs in the form. The `174247` markers pushed through these same pages hours earlier did **not** come back. This was the 2026-09-16 blocker and it is no longer reproducing. |

---

## 1. 🔴 BLOCKER — remove `410-914-1456` from the page, desktop and mobile

**What we see:** it is the **only** phone number rendered, and it is clickable, on **all 7
heating pages, on both desktop and mobile** — 14 of 14 test visits.

Seven `tel:` links per page, five of them visible:

```
tel:+14109141456   "Call Now"        x2
tel:(410) 914-1456 "(410) 914-1456"  x2
tel:(410) 914-1456 "CALL NOW"        x3
```

The `wc_swap` cookie reads `4109141456+..+4107610932+..+230773`, i.e. WhatConverts is
swapping **to** `410-914-1456` and forwarding to the real destination `410-761-0932`.

**Required:** `410-914-1456` must never render or be clickable. Replace the hard-coded
number with the approved default, and let WhatConverts DNI swap in the paid number for paid
sessions. Note the number appears in **two separate components** — a header/floating "Call
Now" button and an in-content "CALL NOW" block. Fix both.

**Done when:** the string `410-914-1456` (in any format: `4109141456`, `(410) 914-1456`,
`+14109141456`) appears nowhere in the rendered DOM or in any `href`, on desktop or mobile.

---

## 2. 🔴 BLOCKER — remove duplicate form and field IDs

**What we see:** **101 duplicated DOM ids per page**, identical on desktop and mobile.

The whole form is in the DOM **twice**:

```
form id="gform_2"   x2      (36 fields each, both with a submit button)
input_2_1  input_2_17  input_2_3  input_2_4  input_2_5
input_2_9_1  input_2_9_3  input_2_9_4  input_2_9_5  input_2_9_6
input_2_7  input_2_10 … input_2_16      ← all duplicated
gform_theme_2   gform_style_settings_2
gform_target_page_number_2   gform_source_page_number_2
et-boc,  menu-item-231/236/2941/1893/1890 …
```

25 duplicated `<input>` ids on top of the duplicated menu/layout ids.

**Why it matters:** `document.getElementById('input_2_14')` returns only the *first* match.
Any client-side attribution script (item 3) will write the GCLID into the hidden form and
**the visible one may be the other copy** — so the value silently never submits. It also
breaks GA4/GTM form tracking and is invalid HTML.

**Required:** render **one** form per page. If the duplication is a
desktop-variant/mobile-variant pattern in the Divi template, render one and control layout
with CSS, or give the second instance genuinely unique ids (`gform_2_mobile`, etc.).

**Done when:** zero duplicate ids page-wide, and exactly one `form#gform_2` per page.

---

## 3. Populate attribution client-side, after page load

The hidden capture fields exist and are currently **empty on a clean visit** (correct):

```
input_2_10  input_2_11  input_2_12  input_2_13  input_2_14  input_2_15  input_2_16
```

⚠️ `input_16` is the **honeypot** — leave it alone. Never write to it and never make it
visible; filling it marks the submission as spam.

**Required:**

- Read `gclid`, `gbraid`, `wbraid`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`,
  `utm_content` from `location.search` **in JavaScript, after page load**.
- There is currently **no field for `gbraid` or `wbraid`** — add two. Without them, iOS and
  privacy-restricted click IDs are lost even when everything else works.
- Write the values into the hidden fields client-side. **Do not** populate them server-side
  (PHP / Gravity Forms dynamic population) — server-rendered values get stored in the
  full-page cache and served to the next visitor. That was the 2026-09-16 defect.
- Persist to first-party storage (`localStorage` + a first-party cookie, ~90 days) and
  restore on later pages so attribution survives navigation.
- First-touch wins; do not overwrite a stored click ID with an empty value.

---

## 4. Cache safety

`x-nitro-cache: HIT` on 14/14 visits and `x-proxy-cache: HIT` on 8/14. With item 3 done
client-side this is safe, because the cached HTML then contains no visitor-specific values.

**Required:** confirm no attribution value is ever present in the server response body, and
**purge both NitroPack and the SiteGround proxy cache after deploying.**

---

## 5. Developer self-test (5 minutes, no tools needed)

1. Open an **incognito** window. Load:
   `https://ambientcoolingandheating.com/services/heating-services/furnace-repair/?gclid=DEVTEST123&gbraid=DEVTEST456&utm_source=google&utm_medium=cpc&utm_campaign=devtest`
2. **Scroll or move the mouse.** NitroPack defers all JavaScript until the first
   interaction — nothing fires until you interact. This is expected, but it also means you
   must interact before checking anything.
3. DevTools → Console: `document.querySelectorAll('#gform_2').length` → must be **1**.
4. Console: `[...document.querySelectorAll('[id]')].length` vs
   `new Set([...document.querySelectorAll('[id]')].map(e=>e.id)).size` → must be **equal**.
5. Console: check the hidden fields hold **your** `DEVTEST123` / `DEVTEST456`.
6. Console: `document.body.innerHTML.includes('914-1456')` → must be **false**.
7. Navigate to another service page → the stored values must still be there.
8. Open a **second** incognito window with **no parameters at all** → every attribution
   field must be **empty**. If it shows `DEVTEST123`, the cache is still leaking; stop and
   tell us.
9. Purge NitroPack + SiteGround cache. Repeat step 8 once more.

---

## 6. Out of scope for this task

- Do not submit the live form for testing. We have no authorised QA identity on file; a real
  submission creates a real lead in the client's CRM.
- Do not change the Google Ads tag, GTM container, GA4 property, or WhatConverts config —
  all four are verified working.
