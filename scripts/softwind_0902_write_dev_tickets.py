#!/usr/bin/env python3
"""Write the DEV-R7A3 developer ticket package. Local file build only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "clients/softwind-power-washing/dev-tickets"
D.mkdir(parents=True, exist_ok=True)

PAID = ["/driveway-pressure-washing/", "/house-pressure-washing-estimate/",
        "/patio-power-washing/", "/power-washing-services-islip-west-islip-dix-hills/",
        "/residential-pressure-washing/", "/soft-house-washing/", "/thank-you/"]
ALL = "\n".join("- `https://offer.softwindli.com" + p + "`" for p in PAID)
OFFER = "\n".join("- `https://offer.softwindli.com" + p + "`" for p in PAID[:6])

EV = ("- `clients/softwind-power-washing/snapshots/"
      "r7a-public-code-inspection-2026-09-02T115916.json`\n"
      "- Saved rendered source: `clients/softwind-power-washing/snapshots/"
      "r7a-page-source-2026-09-02/`\n"
      "- `clients/softwind-power-washing/audits/2026-09-02-r7a-page-code-inspection.csv`\n"
      "- `clients/softwind-power-washing/receipts/"
      "2026-09-02-plan-r1b-execution-continuation-receipt.md`")

FOOT = """
## Rollback

Restore the previous template or plugin revision. No data migration is involved.

## Evidence paths

""" + EV + """

## Developer completion checklist

- [ ] Root cause identified and named (file, plugin, template or setting)
- [ ] Change applied on staging first
- [ ] Desktop QA passed
- [ ] Mobile QA passed
- [ ] Tracking QA passed, network capture attached
- [ ] Regression check on every affected URL
- [ ] Rollback path confirmed
- [ ] Evidence attached to this ticket

## Developer signoff

Name: ______________________  Date: ____________  Release or commit: ______________________
"""

T = {}

T["2026-09-02-dev-r7a-01-duplicate-gravity-form.md"] = """# DEV-R7A3-01 - Duplicate Gravity Form and duplicate HTML IDs

**Ticket ID:** DEV-R7A3-01 | **Priority:** P1 | **Raised:** 2026-09-02
**Client:** Softwind Power Washing | **Property:** offer.softwindli.com

## Business impact

Every offer page renders the customer form **twice** with **identical HTML IDs**.
`getElementById` returns only the first copy, so any analytics, dynamic-number-insertion or
accessibility tool that binds by ID binds to the wrong element. This is a live
tracking-reliability and accessibility defect on the pages that receive all paid traffic.

## Affected URLs

""" + OFFER + """

`/thank-you/` has no form but still carries 2 duplicate IDs.

## Exact observed behaviour

- `document.querySelectorAll('form#gform_1').length` is **2** on every offer page
- **22 duplicate HTML IDs per offer page**, including `gform_1`, `gform_wrapper_1`,
  `gform_fields_1`, `gform_submit_button_1`, `input_1_1`, `input_1_3`, `input_1_4`,
  `input_1_7`, `input_1_9`, the `field_1_*` set, `gform_theme_1`, and Divi's `et-boc`
- Copy 1 renders at roughly `top: 400px`, copy 2 at roughly `top: 5305px`
- Both copies are visible and both are functional

## Required behaviour

- Exactly **one** customer-facing form per page, **or** each additional instance carries a
  unique form ID and unique field IDs
- **Every HTML ID on the page is unique**
- The Gravity Forms honeypot (`input_9`, class `gfield--type-honeypot`) is **preserved, still
  hidden, and still empty** - it is the spam guard and must not be removed or exposed
- No layout or responsive regression on desktop or mobile

## Suggested search locations

The page template or Divi layout emitting the Gravity Forms block twice; a global
header/footer/sidebar module that also injects the form; a duplicated section in the page
builder.

## Acceptance criteria

- [ ] One `form#gform_1` per page, or all IDs unique
- [ ] Zero duplicate IDs, verified with a document-wide ID audit
- [ ] Honeypot present, `display:none`, value empty
- [ ] Form still submits successfully and still reaches `/thank-you/`
- [ ] Desktop and mobile layout unchanged
""" + FOOT

T["2026-09-02-dev-r7a-02-malformed-phone-links.md"] = """# DEV-R7A3-02 - Malformed telephone link tel:(631)

**Ticket ID:** DEV-R7A3-02 | **Priority:** P1 | **Raised:** 2026-09-02

## Business impact

A **dead click-to-call link** sits on every page of a mobile-dominated account. Tapping it
dials nothing. Mobile carries roughly 71 percent of this account's paid spend.

## Affected URLs

""" + ALL + """

## Exact observed behaviour

Two `tel:` anchors exist on every page:

| href | Status |
|---|---|
| `tel:(631) 502-7946` | correct |
| **`tel:(631)`** | **malformed - dials nothing** |

DOM selector: `a[href="tel:(631)"]`

## Required behaviour

- Every static Power Washing phone link uses **`tel:+16315027946`**, unless the finally
  approved call-tracking architecture requires a tracking number in the rendered DOM - in which
  case the displayed text and the `tel:` destination must still agree
- No `tel:(631)`, partial, blank or malformed `href` remains anywhere
- Displayed number and `tel:` destination always match

## Suggested search locations

Shared header/footer, the hero component, or a phone shortcode where a formatting helper is
splitting `(631) 502-7946` on the first space or truncating after the area code.

## Acceptance criteria

- [ ] Zero malformed `tel:` hrefs across all 7 URLs
- [ ] Every `tel:` href is a complete dialable number
- [ ] Displayed number equals the `tel:` destination
- [ ] Mobile tap opens the dialer with the full number
""" + FOOT

T["2026-09-02-dev-r7a-03-duplicate-gtm-loader.md"] = """# DEV-R7A3-03 - Google Tag Manager container installed twice

**Ticket ID:** DEV-R7A3-03 | **Priority:** P1 | **Raised:** 2026-09-02

## Business impact

`GTM-P3LD97NN` is **bootstrapped twice** in the delivered HTML. Two container instances
initialise, so **every tag in the container can fire twice** - including Google Ads
conversions. This is a latent double-counting mechanism sitting directly under the account's
conversion measurement.

## Affected URLs

""" + ALL + """

## Exact observed behaviour - cause confirmed from public source

In the delivered HTML of every page:

| Artifact | Count |
|---|---:|
| Inline bootstrap `(window,document,'script','dataLayer','GTM-P3LD97NN')` | **2** |
| `<script src=".../gtm.js?id=GTM-P3LD97NN">` tags | **2** |
| `<noscript>` `ns.html?id=GTM-P3LD97NN` iframes | **2** |
| `GTM-P3LD97NN` string occurrences | **6** |
| `dataLayer` entries after load | `gtm.js`, **`gtm.js`**, `gtm.dom`, `gtm.load` |

**Cause: the container snippet appears twice in the delivered HTML.** The two inline bootstraps
differ in whitespace, which indicates **two different injectors** - most likely a theme or
header setting plus a plugin such as Site Kit, a GTM plugin, or a custom-code block.

The browser de-duplicates the *network* fetch to a single `gtm.js`, which is why a network-only
check misses this. **The dataLayer proves both bootstraps ran.**

## Required behaviour

- `GTM-P3LD97NN` is installed **exactly once**, intentionally, from one known place
- No second bootstrap and no second `noscript` iframe
- Existing consent behaviour remains intact
- `dataLayer` shows exactly one `gtm.js` entry

## Suggested search locations

Theme options header scripts; a GTM, Site Kit or header-footer plugin; a custom code block in
the page builder; `wp_head` injection from the child theme.

**Please report which two sources you found - Green Marketing needs to know which one to keep.**

## Acceptance criteria

- [ ] Exactly one inline bootstrap, one `gtm.js` tag, one `noscript` iframe
- [ ] `dataLayer` contains one `gtm.js` entry
- [ ] All existing tags still fire exactly once
- [ ] Consent behaviour unchanged
""" + FOOT

T["2026-09-02-dev-r7a-04-form-success-event.md"] = """# DEV-R7A3-04 - Add a verified form-success dataLayer event

**Ticket ID:** DEV-R7A3-04 | **Priority:** **P0** | **Raised:** 2026-09-02

## Business impact - the highest-priority measurement defect

**A direct visit to `/thank-you/` fires a Google Ads conversion with no form submission.**
Proven twice by loading the URL cold. The conversion is bound to the page path, not to a real
lead.

Once genuine ad clicks start converting, the Conversions column will count visitors who reach
`/thank-you/` from browser history, a bookmark, a shared link or a crawler. This account has
**zero conversions to date**, so every future number depends on getting this right *before*
volume arrives. `ONE_PER_CLICK` counting absorbs repeat views inside one click but does **not**
stop a separate ad click reaching `/thank-you/` without submitting.

There is currently **no custom event of any kind** in the dataLayer - only `gtm.js`, `gtm.dom`
and `gtm.load`. Google Tag Manager therefore has no reliable way to tell a real submission from
a page view.

## Affected URLs

- `https://offer.softwindli.com/thank-you/` - the conversion trigger
- All six offer pages - the submission source

## Exact observed behaviour

Loading `https://offer.softwindli.com/thank-you/` directly, with no form interaction, fires:

```
GET https://www.googleadservices.com/pagead/conversion/18369652705/   en=conversion
GET https://www.google.com/pagead/1p-conversion/18369652705/          en=conversion
```

The six offer pages fire **zero** conversion requests on load, which confirms the trigger is
the `/thank-you/` path.

## Required behaviour

Push a dataLayer event **only after a confirmed successful Gravity Forms submission**:

```js
dataLayer.push({
  event: "gm_power_washing_form_success",
  form_id: "1"
});
```

**It must fire exactly once per successful submission, and must NOT fire on:**

- `form_start` or field focus
- a submit-button click alone
- validation failure
- a direct `/thank-you/` visit
- page refresh
- back navigation

Preferred implementation: the Gravity Forms server-side confirmation, or the
`gform_confirmation_loaded` / submission-success hook - not a click handler.

If the redirect to `/thank-you/` is the only available success point, pass a **single-use**
token, for example a one-time query parameter or a short-lived session flag consumed on first
read, so a refresh or a direct visit cannot re-trigger it.

## Suggested search locations

Gravity Forms confirmation settings for form ID 1; `gform_confirmation` or
`gform_after_submission` filters in the theme or a custom plugin; the redirect that currently
sends users to `/thank-you/`.

## Acceptance criteria

- [ ] `gm_power_washing_form_success` fires once on a real submission
- [ ] A direct `/thank-you/` visit pushes no event and fires no conversion
- [ ] Refresh of `/thank-you/` fires no additional event
- [ ] Back navigation fires no additional event
- [ ] Validation failure fires no event
- [ ] The event carries `form_id`
- [ ] Behaviour is identical on desktop and mobile

**After this ships, Green Marketing repoints the Google Ads conversion trigger from the page
path to this event. Please do not change the Google Ads tag yourself.**
""" + FOOT

T["2026-09-02-dev-r7a-05-hardcoded-google-tags.md"] = """# DEV-R7A3-05 - Identify the injection source of both Google Ads tags

**Ticket ID:** DEV-R7A3-05 | **Priority:** P1 | **Raised:** 2026-09-02
**This ticket is INVESTIGATION ONLY. Do not remove any tag.**

## Business impact

Two different Google Ads accounts are tagged on the Power Washing pages. One of them belongs to
a **different Softwind account** and is currently occupying the Power Washing call-tracking
path. Green Marketing cannot correct it until the injection source is known, and has no access
to the GTM container.

## Affected URLs

""" + ALL + """

## Exact observed behaviour

Both tags load as async `gtag.js` script tags:

```
https://www.googletagmanager.com/gtag/js?id=AW-18369652705&cx=c&gtm=4e68v1   <- correct account
https://www.googletagmanager.com/gtag/js?id=AW-17878095007&cx=c&gtm=4e68v1   <- sibling account
```

Each ID appears **exactly once** in the rendered source, and **only inside that injected script
URL**. There is no literal `gtag('config','AW-17878095007', ...)` anywhere in the page HTML.
That pattern is consistent with GTM or a Google tag linked destination, not a hardcoded
snippet.

## What we need from you

Please confirm which of these is true, naming the file or setting:

1. Both tags are configured inside GTM container `GTM-P3LD97NN`
2. One or both are hardcoded in the theme, a child theme, `functions.php`, an mu-plugin or a
   tag plugin
3. One or both come from a Google Site Kit or Google Ads plugin configuration
4. Something else - please describe

## Explicitly out of scope

**Do not remove `AW-17878095007` globally.** It legitimately belongs to Softwind Landscape and
Masonry and may be required on that brand's own pages. Scoping it away from Power Washing URLs
needs a separate approval from that account's owner, which Green Marketing is arranging.

## Acceptance criteria

- [ ] Injection source named for `AW-18369652705`
- [ ] Injection source named for `AW-17878095007`
- [ ] Confirmation of whether the same GTM container also serves the Masonry brand's pages
- [ ] No tag removed or modified under this ticket
""" + FOOT

T["2026-09-02-dev-r7a-06-iconnode-investigation.md"] = """# DEV-R7A3-06 - Identify process.iconnode.com in the lead path

**Ticket ID:** DEV-R7A3-06 | **Priority:** P1 | **Raised:** 2026-09-02
**INVESTIGATION ONLY. Do not remove it.**

## Business impact

An **undocumented third party receives a POST on every page load and again at form
submission**, on an endpoint named `/google-ads/`. Nothing in Green Marketing's client records
documents an engagement with this vendor. Until its purpose is known we cannot confirm where
Softwind's lead data is going, and we cannot safely remove it either.

## Affected URLs

""" + ALL + """

## Exact observed behaviour

```
POST https://process.iconnode.com/google-ads/
```

- Fires **once per page load** on all 7 URLs
- Fires **again at form submission**, observed during a controlled test on 2026-09-02
- **Zero occurrences in the rendered page source** - it is injected at runtime, which is
  consistent with a GTM Custom HTML tag or another script loader
- Payload contents are deliberately not reproduced in this ticket

## What we need from you

- Script owner, and who added it
- Plugin, theme, GTM tag or code source
- Purpose
- What data is transmitted
- Destination and any downstream sharing
- Retention period
- Current authorization - who signed off, and when
- Whether it is still required

## Explicitly out of scope

**Do not remove it before ownership is established.** If it is an authorized processor,
removing it could break a client system. If it is unauthorized, removal will be raised as its
own approved change.

## Acceptance criteria

- [ ] Vendor and owner identified
- [ ] Source location named
- [ ] Purpose and data flow documented
- [ ] Authorization status confirmed
- [ ] Recommendation recorded: keep, scope, or remove
""" + FOOT

T["2026-09-02-dev-r7a-07-sgcaptcha-investigation.md"] = """# DEV-R7A3-07 - SG-Captcha intermittently intercepts paid landing pages

**Ticket ID:** DEV-R7A3-07 | **Priority:** **P2 - investigation only** | **Raised:** 2026-09-02
**Do not disable the security control.**

## Business impact

SiteGround's SG-Captcha was observed intercepting a paid landing page once. If it challenges
real Google Ads visitors it costs sessions on pages that currently cost roughly 29.50 dollars a
click. The evidence is **intermittent**, so this is a monitoring question, not a proven blocker.

## Affected URLs

""" + ALL + """

## Exact observed behaviour

| Date | Result |
|---|---|
| 2026-09-01 | HTTP **202**, request chain passed through `/.well-known/sgcaptcha/?r=...` |
| 2026-09-02 | HTTP **200** on all 7 pages, **no** sgcaptcha request |
| 2026-09-02 controlled submission | **not** blocked - the form submitted successfully |

## What we need from you

- Trigger conditions for SG-Captcha on this site
- Which traffic sources or user agents are affected
- Observed false-positive rate
- Whether an exclusion or allowlist is available for paid landing pages
- Evidence about whether real Google Ads visitors are ever challenged

## Explicitly out of scope

**Do not disable SG-Captcha.** It is a security control and there is no evidence yet that it is
harming genuine visitors.

## Acceptance criteria

- [ ] Trigger conditions documented
- [ ] False-positive evidence provided
- [ ] Allowlist or exclusion options documented
- [ ] Recommendation supplied with supporting data
""" + FOOT

T["2026-09-02-dev-r7a-08-test-lead-cleanup.md"] = """# DEV-R7A3-08 - Remove the internal test lead

**Ticket ID:** DEV-R7A3-08 | **Priority:** P0 | **Raised:** 2026-09-02
**For the authorized site and CRM administrator.**

## Business impact

Green Marketing submitted **one** clearly labelled internal test lead to verify conversion
tracking. It must not be worked as a real customer, and it must not distort lead reporting.

## The record

| Field | Value |
|---|---|
| **Name** | `GM TEST DO NOT CONTACT` |
| **Timestamp** | **2026-09-02 09:24:37 America/New_York** |
| Phone | `(631) 555-0147` - NANP **reserved fictitious** range, cannot ring a real person |
| Email | the Green Marketing approver address on file |
| Page | `/power-washing-services-islip-west-islip-dix-hills/` |
| Project field | "Green Marketing conversion tracking test - not a customer - submitted 2026-09-02 - please delete after verification." |

## Systems to check

- **Gravity Forms** entries, form ID 1 - Green Marketing has no WordPress access
- **WhatConverts** - the account or profile number appears to be `158931`
- **CRM or webhook destination** - currently unidentified; please name it if one received the
  lead

## Required actions

1. Locate the record in each system
2. Mark it clearly as an internal test
3. Ensure no sales follow-up, call, text or email is sent
4. **Preserve the record until Green Marketing confirms measurement QA is complete**, then
   delete or archive
5. Report back which systems contained it

## Important

**Do not delete before confirming with Green Marketing** - the record is evidence for the
conversion-tracking investigation. There is nothing to clean in Google Ads; that account's
conversion history is unaffected.

## Acceptance criteria

- [ ] Record located in each system, or confirmed absent
- [ ] Marked as an internal test
- [ ] Follow-up suppressed
- [ ] Systems containing it reported back to Green Marketing
- [ ] Deleted or archived only after Green Marketing signoff
""" + FOOT

INDEX = """# DEV-R7A3 - POWER WASHING WEBSITE P0 DEVELOPER TICKET PACKAGE

**Raised:** 2026-09-02 | **Client:** Softwind Power Washing | **Property:** offer.softwindli.com
**Requested by:** Green Marketing (Walter Correa, access@greenmarketing.com)

These are **developer tickets, not Google Ads change plans.** They carry no approval fingerprint
and no Google Ads mutation. Green Marketing has **no WordPress access by design** and will not
request it; every issue below is evidenced from the publicly delivered site.

Where the public code proves the effect but the internal WordPress source cannot be identified
from outside, the ticket is marked:
**PUBLIC EFFECT PROVEN - INTERNAL WORDPRESS SOURCE REQUIRES DEVELOPER.**

## Send these in this order

| # | Ticket | Priority | Type | File |
|---|---|---|---|---|
| **1** | **Form-success dataLayer event** | **P0** | change | `2026-09-02-dev-r7a-04-form-success-event.md` |
| 2 | Test-lead cleanup | P0 | admin | `2026-09-02-dev-r7a-08-test-lead-cleanup.md` |
| 3 | Duplicate Gravity Form and duplicate IDs | P1 | change | `2026-09-02-dev-r7a-01-duplicate-gravity-form.md` |
| 4 | Malformed `tel:(631)` link | P1 | change | `2026-09-02-dev-r7a-02-malformed-phone-links.md` |
| 5 | GTM container installed twice | P1 | change | `2026-09-02-dev-r7a-03-duplicate-gtm-loader.md` |
| 6 | Identify both Google Ads tag sources | P1 | investigation | `2026-09-02-dev-r7a-05-hardcoded-google-tags.md` |
| 7 | Identify `process.iconnode.com` | P1 | investigation | `2026-09-02-dev-r7a-06-iconnode-investigation.md` |
| 8 | SG-Captcha behaviour | P2 | investigation | `2026-09-02-dev-r7a-07-sgcaptcha-investigation.md` |

**Ticket 1 is the one to start with.** It is the prerequisite for correcting a proven defect
where a direct visit to `/thank-you/` fires a Google Ads conversion with no form submission.

## Standing instructions for all tickets

- **Do not remove `AW-17878095007`.** It belongs to Softwind Landscape and Masonry and requires
  a separate approval from that account's owner.
- **Do not remove `process.iconnode.com`** before its ownership is established.
- **Do not disable SG-Captcha.**
- **Do not remove or expose the Gravity Forms honeypot** (`input_9`). It is the spam guard and
  it must stay hidden and empty.
- **Do not change any Google Ads tag or conversion configuration.** Green Marketing owns that
  layer and will make those changes itself once the site-side signals exist.
- Apply every change on staging first and attach a network capture as QA evidence.

## Affected URLs

""" + ALL + """

## Evidence

""" + EV + """
"""

for name, body in T.items():
    (D / name).write_text(body.rstrip() + "\n", encoding="utf-8")
    print("wrote", name)
(D / "2026-09-02-r7a-developer-ticket-index.md").write_text(INDEX, encoding="utf-8")
print("wrote 2026-09-02-r7a-developer-ticket-index.md")
