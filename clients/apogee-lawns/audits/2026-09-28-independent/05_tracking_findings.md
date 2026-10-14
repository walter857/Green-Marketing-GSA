# 05 — Tracking findings: GTM, form conversion, calls and WhatConverts

Read-only. No form submitted, no call placed, no ad clicked, no GCLID fabricated, no production event pushed, no GTM
workspace or version touched. One side effect is disclosed: the mobile-width check loaded the landing page once more
with a harmless `?apg_viewport_probe=1` query parameter. That is an extra page view, not a conversion.

## Four milestones, kept separate

| Milestone | Status | Evidence |
|---|---|---|
| 1. Workspace populated | **VERIFIED** — current workspace 5 has 0 pending changes; the objects built in workspace 3 are in versions 2 and 3 | GTM UI |
| 2. Container installed on the pages | **VERIFIED** — GTM-M545Z8T2 loads on the LP and on `/thank-you/`; GTM tag coverage marks `/`, `/home/`, the LP and `/thank-you/` as Tagged | runtime + GTM tag coverage |
| 3. Google tag loaded | **VERIFIED** — `google_tag_manager['AW-18453077620']` present; `viewthroughconversion/18453077620` request observed; `_gcl_au` set | runtime |
| 4. Verified conversion | **FAILED for forms (by configuration, not by an end-to-end test); NOT TESTED for calls** | below |

## Published GTM container (live version 3, `gtm.js` Last-Modified 2026-09-28 19:38:53 GMT)

| Tag (id) | Type | Key settings | Fires on |
|---|---|---|---|
| Google tag (6) | `__googtag` | AW-18453077620 | Initialization, all pages |
| Form conversion (7) | `__awct` | ID 18453077620, label KOL7CImirvocEPS8jt9E, transaction ID `{{DLV \| lead_id}}`, conversion linking on, enhanced conversions off, no value | event = `apg_permanent_lights_lead` **AND** hostname = `offer.apogeelawns.com` **AND** path ~ `^/thank-you/permanent-christmas-lights/?$` **AND** lead_id ~ `.+` |
| Calls from Website (9) | `__awcc` | number **402-526-5754**, ID 18453077620, label lp3jCKf5vPocEPS8jt9E | Page View (`gtm.js`) AND hostname = offer AND path ~ `^/permanent-christmas-lights-lincoln-ne/?$` |
| Conversion Linker (10) — **new in v3 today** | `__gclidw` | cross-domain enabled, **no linker domains listed** | Initialization |

Variables: `DLV | lead_id` (v2, default ""). Triggers: 2. **No consent settings on any tag and no consent-default
command in the container.** No CMP was found on the page (legal review not performed). **Paused tags: none** (the
Versions page reports 4 tags; `gtm.js` contains 4). v2 → v3 diff: only the Conversion Linker was added. It duplicates the
Google tag's own linking and does no cross-domain work without domains; harmless, and removing it is optional.

GTM container-quality notices: (1) "some pages not tagged" = only `/.well-known/sgcaptcha/`, SiteGround's challenge
page, which is expected; (2) "add another administrator".

## Form conversion — why it cannot fire today

1. The only path the trigger accepts is `/thank-you/permanent-christmas-lights/`. **No page exists there**: the public
   WordPress REST API lists 4 published pages (LP 183, `/thank-you/` 1702, privacy, terms).
2. Opening that URL lands on the LP through WordPress's closest-slug redirect, so GTM never runs on the trigger path.
   Proof: a nonexistent slug returns 404, while `/permanent-christmas/` also redirects to the LP.
3. The trigger also requires the custom event `apg_permanent_lights_lead`, which appears **0 times** on the LP,
   `/thank-you/`, the inline scripts and all 28 same-origin scripts.
4. GTM tag coverage shows real page loads on the generic `/thank-you/`. That is consistent with Gravity Forms confirming
   to `/thank-you/`, a path the trigger rejects. **The confirmation target itself is unverified** without a submission or
   admin access.

Caveat stated plainly: a server-side confirmation hook that appears only after a real submission cannot be observed
statically. It still could not satisfy the path condition (1)–(2), so the conclusion does not depend on it.
**Static QA, not end-to-end verification.**

Form build facts (runtime): Gravity Forms form 1, **postback** (non-AJAX), rendered **3 times** on the LP (one 0×0 copy),
**34 duplicate DOM IDs**, fields Full Name / Email / Phone / optional notes plus a hidden honeypot, and seven hidden fields
`input_9`–`input_15`, **all empty on load**. No script populates click IDs. The page is served from a full-page cache: the
form's state timestamp is 15:59:54 UTC against a 20:00 UTC read. If those hidden fields are filled server-side from the
URL, the cache would replay one visitor's values to everyone. Their purpose is unverified.

**WhatConverts does capture this form**: two "GF1" leads from the paid LP today (12:41 and 14:01 CDT), source
`(direct)`, no GCLID. The timing and the Repeat flag look like a test by whoever was editing today. So form leads are not
lost; they are just invisible to Google Ads.

Lead-ID validation (local model, `tests/test_apg_lead_id_contract.py`, 4 tests passing): the live `.+` gate correctly
rejects a missing key and the empty default, but **accepts `undefined`, `null`, whitespace, an unreplaced `{entry_id}`,
`0` and even an email-like string**. An empty default plus `.+` is not proof that invalid IDs are rejected. The proposed
`^[1-9][0-9]{0,11}$` (a Gravity Forms entry ID) passes the full contract, including "same ID across reloads, different ID
per lead". Deduplication is Google's: the **same conversion action** with the same transaction ID (Google Ads Help
6386790). It does **not** deduplicate across different actions.

## Calls

| Path | Configuration | Measured | Status |
|---|---|---|---|
| Calls from ads (call asset 422649064971, 402-526-5754) | `USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION` → 7773013199 (Primary, 60 s); schedule Mon–Fri 08:00–17:00, Sat 08:00–12:00, Sunday absent (account Central time) | call asset shown 7 times, 0 calls; `call_view` empty | configured; **NOT TESTED end-to-end** |
| Website calls (tag 9 → 7773043879) | published since 09-17; Google replaces 402-526-5754 with a Google forwarding number **only for visitors who arrived from an ad** (Google Ads Help 6095883) | 0 all-conversions; my non-ad visit correctly saw no swap (`_gcl_aw` absent) | **NOT TESTED** (needs a real ad visit, which is not authorized) |
| Phone-link clicks | not tracked anywhere | — | intentionally not promoted to a conversion |

**Account-level `/179`:** `call_conversion_action = conversionActions/179`, and no action 179 exists in the child. The API
field is documented as the customer-level action "to attribute a call conversion to", used only when call conversion
reporting is on. **Its effective scope here is nil.** The only call source, call asset 422649064971, uses
`USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION`, and the asset field is documented to take effect only in that state. There are
no call-only ads and no account-level call assets. Whether 179 is a Google system default or a stale pointer cannot be
proven from the API. It is left untouched, since account-wide settings are out of scope.

**Blank "Phone numbers" row on 7773043879:** `conversion_action` has no phone-number field. For a website-call action
the number lives in the tag, which is verified as `402-526-5754` in the published container. The blank row neither proves
nor disproves that tracking works, and no duplicate action should be created to fill it.

## WhatConverts (account 119788 "Apogee Lawns LLC", profile 174313; API v1 read, aggregates only)

- **Number replacement (runtime, not an old JS array):** `wc_swap` = replacement **402-783-8482** for source
  **402-202-7261** (entry 233469). The paid page shows only 402-526-5754, and no text node or `tel:` link changed during a
  25-second MutationObserver window. **In practice WhatConverts and Google's tag target different numbers here, so there
  is no DOM conflict on the paid page.** This corrects the 09-17 record ("WhatConverts assigns 402-526-5754").
- Leads 09-10..09-28 (default view): 28 = 17 calls, 9 texts, 2 web forms. Call and text numbers: 402-256-7520 "LSA
  Traffic" and 402-383-2673 "GBP Traffic". Duplicates view 6; spam view 13 (GBP calls, 09-16..09-18).
- **0 leads on 402-526-5754 in any view, and 0 leads with a GCLID.** Either nobody has called it yet (plausible at 3
  clicks and 7 call-asset impressions) or it is not a WhatConverts number in this profile. API v1 does not expose the
  number inventory, so the owner's statement that it is a WhatConverts number remains **unverified**.
- WhatConverts Google Ads integration: not visible through the API. No WhatConverts-created conversion action exists in
  Google Ads (only the 3 actions), so nothing is currently double-counted in Google Ads.
- The WhatConverts help article on Google call assets does not document the forwarding chain or caller-ID behavior, so
  no claim is made either way. A chained route (Google forwarding number → 402-526-5754 → 402-202-7261) is not presumed
  invalid.
- Apogee is receiving **LSA-tagged leads** in WhatConverts. LSA is a separate workflow and is not audited here.

## Website-call measurement owner — decision

**Google Ads' native Calls from Website conversion (the published tag 9) owns paid website-call attribution. WhatConverts
remains the system of record for recording, listening and qualifying every call, but must not send these same calls back
to Google Ads.**

Why: on this page WhatConverts runs no session-level replacement for 402-526-5754 (no DNI pool; its only swap targets
402-202-7261), so it cannot tie a website call to a click. The Google tag swaps a forwarding number per ad visitor and
attributes calls of 60 seconds or more to the click. Counting the same call through a WhatConverts upload as a second
action would double-count it, because transaction IDs deduplicate only within one action.

Routing model: ad visitor → Google forwarding number → 402-526-5754 → (WhatConverts, if it owns that number) →
402-202-7261. Keep 7773043879 **Secondary** until a real website-call conversion is observed. Promotion is a separate,
later plan, and a 60-second threshold is a measurement bar, not proof of a qualified buyer.

## Should spend continue while forms are unmeasured?

**Continue, temporarily.** Recommendation only; not executed.

- Bidding is Maximize Clicks, which does not use conversions, so the broken form tag does not distort delivery.
- Spend is small: $18.69 to date, and the forecast averages about $3.21 a day to Dec 20.
- WhatConverts demonstrably captures GF1 submissions. A paid visitor lands with the campaign's UTM suffix
  (`utm_source=google&utm_medium=cpc…`), so paid form leads *should* stay identifiable without Google Ads attribution.
  This has not yet been observed with a real paid lead.
- Pausing would forfeit the October ramp ahead of the November peak.
- Risks: form leads are invisible in Google Ads, so there is no Ads CPL; and anyone switching to a conversion-based
  strategy now would optimize on calls only.
- **Guard:** do not change the bid strategy until the form conversion is verified end to end.
