#!/usr/bin/env python3
"""Write the ClickUp-ready launch task package."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CU = ROOT / "clients/softwind-power-washing/clickup-tickets"
CU.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("power-washing-services-islip-west-islip-dix-hills", "Power Washing",
     "Power Washing Long Island | Softwind Power Washing",
     "Power Washing Across Long Island",
     "Dirt, grime and algae build up on every exterior surface. We wash homes across Nassau "
     "and Suffolk County, matching the right pressure and method to each surface.",
     "power washing, power washing near me, power washing service, power washing services "
     "near me, power washing company near me"),
    ("residential-pressure-washing", "Pressure Washing",
     "Residential Pressure Washing Long Island | Softwind Power Washing",
     "Residential Pressure Washing On Long Island",
     "Pressure washing for homes across Nassau and Suffolk County. Siding, walkways, patios "
     "and driveways, cleaned with the pressure each surface can take.",
     "pressure washing, pressure washing near me, residential pressure washing near me"),
    ("house-washing-company", "House Washing",
     "House Washing Long Island | Softwind Power Washing",
     "House Washing Across Long Island",
     "Siding, trim and exterior walls washed clean. We serve homeowners throughout Nassau and "
     "Suffolk County and match the method to your siding.",
     "house washing near me, house pressure washing near me, house power washing near me, "
     "exterior house washing near me"),
    ("soft-house-washing", "Soft Washing",
     "Soft Washing Long Island | Softwind Power Washing",
     "Soft Washing For Long Island Homes",
     "Soft washing uses low pressure and the right cleaning solution instead of force. It "
     "lifts algae and grime from siding and trim without driving water where it should not go.",
     "soft house washing near me, soft washing near me"),
    ("driveway-pressure-washing", "Driveway Pressure Washing",
     "Driveway Pressure Washing Long Island | Softwind Power Washing",
     "Driveway Pressure Washing On Long Island",
     "Concrete, pavers and stone driveways washed clean of dirt, oil marks and algae. Serving "
     "homeowners across Nassau and Suffolk County.",
     "driveway pressure washing near me, driveway power washing near me"),
    ("patio-power-washing", "Patio Pressure Washing",
     "Patio Pressure Washing Long Island | Softwind Power Washing",
     "Patio Pressure Washing On Long Island",
     "Patios, pavers, walkways and pool surrounds washed clean. We match the pressure to the "
     "surface so pavers and jointing sand stay where they belong.",
     "patio pressure washing near me, patio power washing near me, concrete pressure washing "
     "near me"),
]

blocks = []
for slug, group, title, h1, hero, kws in PAGES:
    blocks.append(f"""
### https://offer.softwindli.com/{slug}/
Maps to Google Ads ad group: **{group}**
Keyword family: {kws}

| Element | Final copy |
|---|---|
| Browser title | {title} |
| H1 | {h1} |
| Hero copy | {hero} |
| Supporting text | Every property is different. Tell us what you need washed and we will send back a free quote. |
| CTA copy | Request A Free Quote |
| Form heading | Get Your Free Quote |
| Service-area wording | Serving homeowners across Long Island, in Nassau and Suffolk County. |
| Service sections | What we wash - how we match pressure and method to each surface - what to expect from the visit |
| FAQ wording | How do you decide the pressure to use? / Do I need to be home? / How do I get a quote? |
| Final CTA | Request a free quote for your property. |
| Phone | (631) 502-7946 |
| Countdown | REMOVE - no dated offer exists |
""")
PAGE_TABLE = "\n".join(blocks)

T1 = """TASK TITLE:

[P0] Softwind Power Washing — Fix form-success conversion tracking

TASK DESCRIPTION:

**Problem**

A direct visit to https://offer.softwindli.com/thank-you/ currently fires a Google Ads
conversion with no form submission. Verified twice by loading the URL cold with no form
interaction. The conversion is bound to the page path, not to a real lead.

Observed on a bare page load:

```
GET https://www.googleadservices.com/pagead/conversion/18369652705/   en=conversion
GET https://www.google.com/pagead/1p-conversion/18369652705/          en=conversion
```

The six offer pages fire zero conversion requests on load, which confirms the trigger is the
/thank-you/ path. There is currently no custom event of any kind in the dataLayer — only
gtm.js, gtm.dom and gtm.load — so Google Tag Manager has no way to tell a real submission from
a page view.

This account has zero conversions to date. Every future conversion number depends on fixing
this before real volume arrives.

**What we need**

Push a dataLayer event only after a confirmed successful Gravity Forms submission:

```js
dataLayer.push({
  event: "gm_power_washing_form_success",
  form_id: "1"
});
```

**It must fire exactly once per successful submission, and must NOT fire on:**

- form start or field focus
- a submit-button click alone
- validation failure
- a direct /thank-you/ visit
- page refresh
- back navigation

Preferred implementation: the Gravity Forms server-side confirmation, or the
gform_confirmation_loaded / submission-success hook. Not a click handler.

If the redirect to /thank-you/ is the only available success point, pass a single-use token —
a one-time query parameter or a short-lived session flag consumed on first read — so a refresh
or a direct visit cannot re-trigger it.

**Where to look**

Gravity Forms confirmation settings for form ID 1; gform_confirmation or gform_after_submission
filters in the theme or a custom plugin; the redirect that currently sends users to
/thank-you/.

**Acceptance criteria**

- [ ] gm_power_washing_form_success fires once on a real submission
- [ ] Direct /thank-you/ visit pushes no event and fires no conversion
- [ ] Refresh of /thank-you/ fires no additional event
- [ ] Back navigation fires no additional event
- [ ] Validation failure fires no event
- [ ] The event carries form_id
- [ ] Identical behaviour on desktop and mobile

**QA required:** desktop, mobile, and a network capture showing the conversion request firing
once on a real submission and zero times on a direct visit.

**Rollback:** revert the confirmation hook or template change. No data migration involved.

**Do not change any Google Ads tag or conversion setting.** Green Marketing owns that layer and
will repoint the trigger to this event once it ships.
"""

T2 = """TASK TITLE:

[P0] Softwind Power Washing — Fix duplicate form markup and phone links

TASK DESCRIPTION:

**Problem 1 — the form renders twice with duplicate HTML IDs**

Every offer page renders form#gform_1 twice, producing 22 duplicate HTML IDs per page including
gform_1, gform_wrapper_1, gform_fields_1, gform_submit_button_1, input_1_1, input_1_3,
input_1_4, input_1_7, input_1_9, the field_1_* set, gform_theme_1, and Divi's et-boc. Copy one
renders around 400px, copy two around 5305px. Both are visible and functional.

getElementById returns only the first copy, so any analytics, dynamic-number-insertion or
accessibility tool that binds by ID binds to the wrong element. This is a live
tracking-reliability and accessibility defect.

**Problem 2 — a dead click-to-call link**

Two tel: anchors exist on all seven pages:

- `tel:(631) 502-7946` — correct
- `tel:(631)` — malformed, dials nothing

Selector: a[href="tel:(631)"]. Mobile carries roughly 71% of this account's paid spend.

**Affected URLs**

- https://offer.softwindli.com/driveway-pressure-washing/
- https://offer.softwindli.com/house-pressure-washing-estimate/
- https://offer.softwindli.com/patio-power-washing/
- https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/
- https://offer.softwindli.com/residential-pressure-washing/
- https://offer.softwindli.com/soft-house-washing/
- https://offer.softwindli.com/thank-you/

**Required result**

- Exactly one visible Gravity Form per page
- Exactly one form#gform_1, or each instance carries unique form and field IDs
- Every HTML ID on the page is unique
- The Gravity Forms honeypot (input_9, class gfield--type-honeypot) is preserved, still hidden,
  and still empty — it is the spam guard, do not remove or expose it
- Every tel: href is a complete dialable number: **tel:+16315027946** unless the final
  call-tracking architecture requires an approved dynamic replacement number
- Displayed phone number equals the tel: destination
- No tel:(631), partial, blank or malformed href remains

**Where to look**

The page template or Divi layout emitting the Gravity Forms block twice; a global
header/footer/sidebar module that also injects the form. For the phone: a shared header/footer
or hero component, or a phone shortcode splitting "(631) 502-7946" on the first space.

**Acceptance criteria**

- [ ] One form#gform_1 per page, or all IDs unique
- [ ] Zero duplicate IDs, verified with a document-wide ID audit
- [ ] Honeypot present, display:none, value empty
- [ ] Form still submits successfully and still reaches /thank-you/
- [ ] Zero malformed tel: hrefs on all seven URLs
- [ ] Mobile tap opens the dialer with the full number
- [ ] No desktop or mobile layout regression

**Regression checks:** submit the form on staging and confirm it still reaches /thank-you/;
confirm no other page section shifted.

**Rollback:** restore the previous template or plugin revision.
"""

T3 = """TASK TITLE:

[P0] Softwind Power Washing — Correct Google tag scope and duplicate GTM load

TASK DESCRIPTION:

**Problem 1 — Google Tag Manager is installed twice**

GTM-P3LD97NN is bootstrapped twice in the delivered HTML of every page:

| Artifact | Count |
|---|---|
| Inline bootstrap (window,document,'script','dataLayer','GTM-P3LD97NN') | 2 |
| script src=".../gtm.js?id=GTM-P3LD97NN" tags | 2 |
| noscript ns.html?id=GTM-P3LD97NN iframes | 2 |
| GTM-P3LD97NN string occurrences | 6 |
| dataLayer after load | gtm.js, **gtm.js**, gtm.dom, gtm.load |

Two container instances initialise, so every tag in the container can fire twice — including
Google Ads conversions. The browser de-duplicates the network fetch to one gtm.js, which is why
a network-only check misses this. The dataLayer proves both bootstraps ran.

The two inline bootstraps differ in whitespace, which indicates two different injectors — most
likely a theme or header setting plus a plugin such as Site Kit, a GTM plugin, or a custom-code
block.

**Required result**

- GTM-P3LD97NN is installed exactly once, intentionally, from one known place
- No second bootstrap and no second noscript iframe
- dataLayer shows exactly one gtm.js entry
- Existing consent behaviour remains intact
- **Please report which two sources you found** — we need to know which one to keep

**Problem 2 — identify the source of both Google Ads tags (investigation only)**

Two Google Ads tags load as async gtag.js script tags on every page:

```
https://www.googletagmanager.com/gtag/js?id=AW-18369652705&cx=c&gtm=4e68v1   <- correct account
https://www.googletagmanager.com/gtag/js?id=AW-17878095007&cx=c&gtm=4e68v1   <- sibling account
```

Each ID appears exactly once in the rendered source and only inside that injected script URL —
there is no literal gtag('config','AW-17878095007', ...) anywhere in the page HTML.

Please confirm, naming the file or setting, whether:

1. Both are configured inside GTM container GTM-P3LD97NN
2. One or both are hardcoded in the theme, child theme, functions.php, an mu-plugin or a tag
   plugin
3. One or both come from a Google Site Kit or Google Ads plugin
4. Something else

**Critical scope limits**

- **Preserve AW-18369652705.** That is the correct Softwind Power Washing account.
- **Do NOT remove AW-17878095007 globally.** It belongs to Softwind Landscape & Masonry
  (Google Ads customer 2429758629) and may legitimately be required on that brand's own pages.
  Scoping it away from the Power Washing URLs requires a separate approval from that account's
  owner, which Green Marketing is arranging. Under this task we only need the source
  identified — no tag removed or modified.

**Acceptance criteria**

- [ ] Exactly one inline bootstrap, one gtm.js tag, one noscript iframe
- [ ] dataLayer contains one gtm.js entry
- [ ] All existing tags still fire exactly once
- [ ] Consent behaviour unchanged
- [ ] Injection source named for AW-18369652705 and AW-17878095007
- [ ] No tag removed or modified

**Rollback:** restore the removed bootstrap snippet.
"""

T4 = """TASK TITLE:

[P1] Softwind Power Washing — Publish final landing-page copy and CRO updates

TASK DESCRIPTION:

**Scope**

Keep the existing landing-page template structure. Do not redesign the layout. Do not change
any URL slug. Apply the exact copy below to each paid page.

**Two defects to correct on every page**

1. The browser title currently reads "Softwind Landscape & Masonry" — the wrong brand for
   these Power Washing pages.
2. The H1 is locked to "Islip, West Islip & Dix Hills" while the campaigns target 80 places
   across Nassau and Suffolk County. Use the Long Island wording below.
3. Remove the "Offer Ends" countdown. It resets on reload and no dated offer exists.

**Exact final copy per page**
""" + PAGE_TABLE + """

**Service-area wording — verified**

"Long Island" as the anchor, with "Serving Nassau and Suffolk County" as the supporting line.
Both are verifiable from the 80 live geo targets in the Google Ads account — every one is a New
York location in Nassau or Suffolk. Do not use dynamic location insertion. Do not name
individual towns.

**Do NOT invent or publish any of the following** — none is verified in the client profile:

prices, discounts, warranties, licenses, certifications, review counts, star ratings, years in
business, response times, promotions, guarantees, or emergency service.

Reviews and project images may only be added when the client supplies verified,
service-relevant reviews and rights-cleared photographs. Until then, omit those sections
rather than filling them.

**Acceptance criteria**

- [ ] All six pages return HTTP 200 with no redirect
- [ ] Browser title and H1 updated exactly as specified
- [ ] Countdown removed
- [ ] Phone displays (631) 502-7946 and the tel: destination matches
- [ ] Form still submits and reaches /thank-you/
- [ ] Tracking still fires after the copy change
- [ ] Mobile layout verified, no horizontal scroll
- [ ] Page-speed not regressed versus the current build
- [ ] No unverified claim published anywhere

**Rollback:** restore the previous page revisions from WordPress revision history.
"""

T5 = """TASK TITLE:

[P2] Softwind Power Washing — Vendor, security and cleanup investigations

TASK DESCRIPTION:

**These are P2. They must not block the launch build.**

---

**5a. Identify process.iconnode.com in the lead path**

An undocumented third party receives `POST https://process.iconnode.com/google-ads/` on every
page load of all seven pages, and again at form submission. It has zero occurrences in the
rendered page source, so it is injected at runtime — consistent with a GTM Custom HTML tag.
Nothing in Green Marketing's records documents an engagement with this vendor.

Please identify: script owner, who added it, plugin/theme/GTM source, purpose, what data is
transmitted, destination, retention, current authorization, and whether it is still required.

**Do not remove it before ownership is established.**

---

**5b. SG-Captcha behaviour**

SiteGround SG-Captcha was observed intercepting a paid landing page once (HTTP 202, request
chain through /.well-known/sgcaptcha/). On a later check all seven pages returned HTTP 200 with
no sgcaptcha request, and it did not block a controlled form submission. It is intermittent.

Please document: trigger conditions, affected traffic sources, false-positive rate, whether an
exclusion or allowlist is available for paid landing pages, and evidence about whether real
Google Ads visitors are ever challenged.

**Do not disable SG-Captcha.** It is a security control and there is no evidence it is harming
genuine visitors.

---

**5c. Internal test-lead cleanup**

Green Marketing submitted one clearly labelled internal test lead to verify conversion
tracking.

| Field | Value |
|---|---|
| Name | GM TEST DO NOT CONTACT |
| Timestamp | 2026-09-02 09:24:37 America/New_York |
| Phone | (631) 555-0147 — NANP reserved fictitious range, cannot ring a real person |
| Page | /power-washing-services-islip-west-islip-dix-hills/ |

Check Gravity Forms (form ID 1), WhatConverts (account number appears to be 158931), and any
CRM or webhook destination. Mark it as an internal test, suppress any follow-up, and report
back which systems contained it.

**Preserve the record until Green Marketing confirms measurement QA is complete**, then delete
or archive. There is nothing to clean in Google Ads.

---

**5d. Rights-cleared project images**

To add project images and reviews to the landing pages we need client-supplied, rights-cleared
photographs of completed Power Washing work, and verified service-relevant reviews. No stock
landscaping imagery, no fabricated project photos, and no AI-generated images presented as
completed work.
"""

INDEX = """# SOFTWIND POWER WASHING — CLICKUP LAUNCH TASK PACKAGE

**Created:** 2026-09-02 · **Client:** Softwind Power Washing · **Property:** offer.softwindli.com
**Requested by:** Green Marketing (Walter Correa, access@greenmarketing.com)

Each task file is directly pasteable into ClickUp — it opens with `TASK TITLE:` and
`TASK DESCRIPTION:`.

Green Marketing has **no WordPress access by design** and will not request it. Every issue below
is evidenced from the publicly delivered site: **PUBLIC DEFECT PROVEN — INTERNAL WEBSITE SOURCE
MUST BE LOCATED BY DEVELOPMENT.**

| # | Priority | Task | File | Blocks launch? |
|---|---|---|---|---|
| 1 | **P0** | Fix form-success conversion tracking | `2026-09-02-clickup-task-1-form-success-tracking.md` | **YES** |
| 2 | **P0** | Fix duplicate form markup and phone links | `2026-09-02-clickup-task-2-duplicate-form-and-phone.md` | **YES** |
| 3 | **P0** | Correct Google tag scope and duplicate GTM load | `2026-09-02-clickup-task-3-google-tag-scope-and-gtm.md` | **YES** |
| 4 | P1 | Publish final landing-page copy and CRO updates | `2026-09-02-clickup-task-4-landing-page-copy.md` | **YES** (titles/H1 only) |
| 5 | P2 | Vendor, security and cleanup investigations | `2026-09-02-clickup-task-5-vendor-and-cleanup.md` | no |

## Start with Task 1

It is the prerequisite for correcting a proven defect where a direct visit to `/thank-you/`
fires a Google Ads conversion with no form submission.

## Standing instructions

- **Preserve `AW-18369652705`** — the correct Power Washing Google Ads tag.
- **Do not remove `AW-17878095007` globally** — it belongs to Softwind Landscape & Masonry
  (customer 2429758629) and needs that account owner's separate approval to scope.
- **Do not remove `process.iconnode.com`** before its ownership is established.
- **Do not disable SG-Captcha.**
- **Do not remove or expose the Gravity Forms honeypot** (`input_9`) — it is the spam guard.
- **Do not change any Google Ads tag or conversion configuration.** Green Marketing owns that
  layer.
- **Do not change any URL slug.**
- Apply every change on staging first and attach a network capture as QA evidence.

## Evidence

- `clients/softwind-power-washing/snapshots/r7a-public-code-inspection-2026-09-02T115916.json`
- `clients/softwind-power-washing/snapshots/r7a-page-source-2026-09-02/` (7 rendered sources)
- `clients/softwind-power-washing/audits/2026-09-02-r7a-implementation-source-audit.md`
- `clients/softwind-power-washing/receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md`
"""

for name, body in [
        ("2026-09-02-clickup-task-1-form-success-tracking.md", T1),
        ("2026-09-02-clickup-task-2-duplicate-form-and-phone.md", T2),
        ("2026-09-02-clickup-task-3-google-tag-scope-and-gtm.md", T3),
        ("2026-09-02-clickup-task-4-landing-page-copy.md", T4),
        ("2026-09-02-clickup-task-5-vendor-and-cleanup.md", T5)]:
    (CU / name).write_text(body.rstrip() + "\n", encoding="utf-8")
    print("wrote", name)
(CU / "2026-09-02-clickup-ticket-index.md").write_text(INDEX, encoding="utf-8")
print("wrote 2026-09-02-clickup-ticket-index.md")
