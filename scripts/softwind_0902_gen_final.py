#!/usr/bin/env python3
"""Generate ClickUp tasks, monitoring runbook, approval queue, deliverables + ZIP."""
from __future__ import annotations

import csv
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "clients/softwind-power-washing"
CU = C / "clickup-tickets/2026-09-02-final-launch"
CU.mkdir(parents=True, exist_ok=True)
(C / "runbooks").mkdir(exist_ok=True)
DEL = C / "deliverables/2026-09-02-final-launch-package"
DEL.mkdir(parents=True, exist_ok=True)
PHONE, TEL = "(631) 502-7946", "+16315027946"
PAGES = [("01-power-washing", "Power Washing", "power-washing-services-islip-west-islip-dix-hills"),
         ("02-pressure-washing", "Pressure Washing", "residential-pressure-washing"),
         ("03-house-washing", "House Washing", "house-washing-company"),
         ("04-soft-washing", "Soft Washing", "soft-house-washing"),
         ("05-driveway-pressure-washing", "Driveway Pressure Washing", "driveway-pressure-washing"),
         ("06-patio-pressure-washing", "Patio Pressure Washing", "patio-power-washing")]
FOOT = """
## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________
"""
tasks = []


def add(fn, title, desc, prio, url, dep, src):
    (CU / fn).write_text(f"TASK TITLE:\n\n{title}\n\nTASK DESCRIPTION:\n\n{desc}\n",
                         encoding="utf-8")
    tasks.append({"Task Name": title, "Description": desc.split("\n")[0][:180],
                  "Priority": prio, "Status": "To Do", "Dependency": dep,
                  "Client": "Softwind Power Washing", "Service": "Power Washing",
                  "URL": url, "Source File": f"clickup-tickets/2026-09-02-final-launch/{fn}",
                  "QA Owner": "Green Marketing"})


ALLURL = " · ".join(f"https://offer.softwindli.com/{s}/" for _, _, s in PAGES) \
    + " · https://offer.softwindli.com/thank-you/"

add("p0-01-form-success-event.md",
    "[P0] Softwind Power Washing — Add verified form-success dataLayer event",
    f"""**Business impact:** a direct visit to `/thank-you/` currently fires a Google Ads
conversion with no form submission. Verified twice by loading the URL cold. Once real ad clicks
convert, the Conversions column will count visitors arriving from history, bookmarks or crawlers.
The account has ZERO conversions today, so every future number depends on fixing this first.

**Affected URL:** https://offer.softwindli.com/thank-you/ plus all six offer pages.

**Current behavior:** loading `/thank-you/` directly fires
`GET googleadservices.com/pagead/conversion/18369652705/ en=conversion` and
`GET google.com/pagead/1p-conversion/18369652705/ en=conversion`. The six offer pages fire zero
on load, which localises the trigger to the page path. The dataLayer contains only `gtm.js`,
`gtm.dom`, `gtm.load` — no custom event exists.

**Required behavior:** push, only after a confirmed successful Gravity Forms submission:

```js
dataLayer.push({{ event: "gm_power_washing_form_success", form_id: "1" }});
```

Must fire exactly once per successful submission. Must NOT fire on form start, submit-click
alone, validation failure, a direct `/thank-you/` visit, refresh, or back navigation.

**Implementation file path:** Gravity Forms confirmation settings for form ID 1, or the
`gform_confirmation` / `gform_after_submission` filter in the theme or a custom plugin. If the
redirect is the only success point, pass a single-use token consumed on first read.

**Acceptance criteria:** event fires once on a real submission · direct `/thank-you/` visit
pushes no event and fires no conversion · refresh and back navigation fire nothing · validation
failure fires nothing · event carries `form_id` · identical on desktop and mobile.

**Dependencies:** none. **Do not change any Google Ads tag** — Green Marketing repoints the
trigger after this ships.

**Evidence:** `snapshots/r7a-public-code-inspection-2026-09-02T115916.json`,
`receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md`
{FOOT}""", "Urgent", "https://offer.softwindli.com/thank-you/", "none",
    "audits/2026-09-02-r7a-implementation-source-audit.md")

add("p0-02-duplicate-form-and-ids.md",
    "[P0] Softwind Power Washing — Fix duplicate form and duplicate HTML IDs",
    f"""**Business impact:** every offer page renders `form#gform_1` twice, producing **22
duplicate HTML IDs** per page. `getElementById` returns only the first copy, so any analytics,
dynamic-number-insertion or accessibility tool binding by ID binds to the wrong element.

**Affected URLs:** {ALLURL}

**Current behavior:** `document.querySelectorAll('form#gform_1').length === 2`. Duplicated IDs
include `gform_1`, `gform_wrapper_1`, `gform_fields_1`, `gform_submit_button_1`, `input_1_1`,
`input_1_3`, `input_1_4`, `input_1_7`, `input_1_9`, `field_1_*`, `gform_theme_1`, `et-boc`.
Copy one at ~400px, copy two at ~5305px. Both visible and functional.

**Required behavior:** exactly one customer-facing form per page, or unique form and field IDs
per instance. Every HTML ID unique. **The Gravity Forms honeypot `input_9`
(`.gfield--type-honeypot`) must remain present, hidden and empty** — it is the spam guard.

**Implementation file path:** the page template or Divi layout emitting the Gravity Forms block
twice, or a global header/footer/sidebar module that also injects it.

**Acceptance criteria:** one `form#gform_1` · zero duplicate IDs verified by a document-wide
audit · honeypot present, `display:none`, empty · form still submits and reaches `/thank-you/` ·
no layout regression.

**Dependencies:** none.
**Evidence:** `snapshots/r7a-public-code-inspection-2026-09-02T115916.json`
{FOOT}""", "Urgent", ALLURL, "none", "audits/2026-09-02-r7a-implementation-source-audit.md")

add("p0-03-malformed-phone-links.md",
    "[P0] Softwind Power Washing — Fix malformed telephone links",
    f"""**Business impact:** a dead click-to-call link sits on every page of an account where
mobile carries ~74% of spend. Tapping it dials nothing.

**Affected URLs:** {ALLURL}

**Current behavior:** two `tel:` anchors per page — the correct `tel:{PHONE}` and a malformed
**`tel:(631)`**. Selector: `a[href="tel:(631)"]`.

**Required behavior:** every static phone link uses **`tel:{TEL}`**. No partial, blank or
malformed href remains. Displayed number equals the `tel:` destination.

**Implementation file path:** shared header/footer or hero component, or a phone shortcode
splitting "{PHONE}" on the first space.

**Acceptance criteria:** zero malformed hrefs across all 7 URLs · every href dialable · displayed
number equals destination · mobile tap opens the dialer with the full number.

**Dependencies:** coordinate with the call-tracking architecture decision if a tracking number
later replaces the static one.
{FOOT}""", "Urgent", ALLURL, "none", "audits/2026-09-02-r7a-implementation-source-audit.md")

add("p0-04-google-tag-scope-and-gtm.md",
    "[P0] Softwind Power Washing — Google tag scoping and duplicate GTM load",
    f"""**Business impact:** `GTM-P3LD97NN` is bootstrapped **twice** per page, so every tag in
the container can fire twice — including Google Ads conversions. Separately, a second Google Ads
account's tag runs on these pages and occupies the call-tracking path.

**Affected URLs:** {ALLURL}

**Current behavior:** 2 inline bootstraps, 2 `gtm.js` script tags, 2 `noscript` iframes, 6
occurrences of `GTM-P3LD97NN`; the dataLayer shows `gtm.js` twice. The browser de-duplicates the
network fetch, which is why a network-only check misses it. The two bootstraps differ in
whitespace, indicating two separate injectors.

Both `AW-18369652705` (correct) and `AW-17878095007` (Softwind Landscape & Masonry, customer
2429758629) load as async `gtag/js` tags. Neither ID appears as a literal `gtag('config', ...)`
in the page source.

**Required behavior:** GTM installed exactly once from one known place; dataLayer shows one
`gtm.js`; consent behaviour unchanged. **Report which two injectors you found.** Also confirm
whether each `AW-` tag is configured in GTM, hardcoded, or from a Site Kit / Google Ads plugin.

**Critical scope limits:** **preserve `AW-18369652705`.** **Do NOT remove `AW-17878095007`
globally** — it belongs to the sibling Softwind account and scoping it away from Power Washing
URLs needs that account owner's separate approval. This task only identifies the source.

**Acceptance criteria:** one bootstrap, one `gtm.js`, one `noscript` · dataLayer shows one
`gtm.js` · all existing tags still fire once · consent unchanged · both tag sources named · no tag
removed.
{FOOT}""", "Urgent", ALLURL, "none", "audits/2026-09-02-r7a-implementation-source-audit.md")

add("p0-05-whatconverts-dni.md",
    "[P0] Softwind Power Washing — WhatConverts DNI and call attribution",
    f"""**Business impact:** WhatConverts attribution works but its number replacement never
reaches the page, so paid calls cannot be attributed. Meanwhile the sibling Google Ads account
runs its own website-call replacement on Softwind's number.

**Affected URLs:** {ALLURL}

**Current behavior:** the WhatConverts script loads from
`s.ksrndkehqnwntyxlhgto.com/158931.js` (WordPress plugin, handle
`whatconverts-tracking-script-js`). `wc_client` correctly carries source, medium, campaign,
content, term and the GCLID. `wc_swap` nominates 6315025402 and 6315535927 — **neither reaches
the DOM**; the page renders the static {PHONE} in both body text and the `tel:` href.
Separately, `conversion/17878095007/wcm` fires on all 7 pages while
`conversion/18369652705/wcm` fires on **none**.

**Required behavior:** determine why DNI does not execute, then implement ONE authoritative call
architecture. Do not run Google website-call replacement and WhatConverts DNI on the same
displayed number.

**Implementation file path:** WhatConverts account configuration (profile appears to be
`158931`) plus the WordPress plugin that enqueues the script.

**Blocked on Green Marketing:** an authenticated WhatConverts read. The API token in our
environment is empty. **Do not paste any credential into a ticket or chat** — populate
`WHATCONVERTS_API_TOKEN` in the secure local environment, or grant a read-only WhatConverts user.

**Acceptance criteria:** DNI root cause documented · one system owns the displayed number · no
double replacement · `wc_client` attribution preserved · GCLID preserved.
{FOOT}""", "High", ALLURL, "WhatConverts read access",
    "plans/2026-09-02-plan-r7a2-whatconverts-call-attribution.yaml")

add("p0-06-test-lead-cleanup.md",
    "[P0] Softwind Power Washing — Remove the internal test lead",
    f"""**Business impact:** Green Marketing submitted one clearly labelled internal test lead to
verify conversion tracking. It must not be worked as a real customer or distort lead reporting.

**The record:** name `GM TEST DO NOT CONTACT` · timestamp **2026-09-02 09:24:37
America/New_York** · phone `(631) 555-0147` (NANP reserved fictitious range, cannot ring a real
person) · page `/power-washing-services-islip-west-islip-dix-hills/` · project field reads
"Green Marketing conversion tracking test - not a customer - submitted 2026-09-02 - please delete
after verification."

**Systems to check:** Gravity Forms entries (form ID 1) · WhatConverts (account/profile appears
to be `158931`) · any CRM or webhook destination — please name it if one received the lead.

**Required behavior:** locate it, mark it clearly as an internal test, suppress any follow-up,
and report back which systems contained it. **Preserve the record until Green Marketing confirms
measurement QA is complete**, then delete or archive.

**Acceptance criteria:** located or confirmed absent in each system · marked as test · follow-up
suppressed · systems reported back · deleted only after Green Marketing signoff.

**Note:** nothing to clean in Google Ads — that account's conversion history is unaffected.
{FOOT}""", "Urgent", "n/a", "none",
    "receipts/2026-09-02-plan-r1b-execution-continuation-receipt.md")

for folder, page, slug in PAGES:
    url = f"https://offer.softwindli.com/{slug}/"
    add(f"p1-{folder}.md",
        f"[P1] Softwind Power Washing — Publish final {page} landing-page copy",
        f"""**Business impact:** the page currently carries the wrong brand in the browser title
("Softwind Landscape & Masonry"), an H1 locked to three hamlets while the campaigns target 80
places, and an unsupported resetting countdown. The matching Google Ads ad group is now LIVE, so
the ad message and the page must agree.

**Affected URL:** {url} — **do not change the slug.**

**Current behavior:** wrong-brand title · city-locked H1 · generic hero · resetting "Offer Ends"
countdown with no dated offer.

**Required behavior:** apply the exact final copy. Keep the existing template structure and
section order. This is a text replacement, not a redesign.

**Implementation file path:**
`clients/softwind-power-washing/landing-pages/2026-09-02-final/{folder}/`

- `final-copy.md` — every section, ready to paste
- `final-copy.html` — clean body-section HTML
- `seo-meta.txt` — title, meta description, canonical, H1, focus keyword
- `developer-implementation.md` — exactly what is replaced and what stays
- `qa-checklist.md` — the acceptance checklist
- `keyword-map.csv`, `rsa-page-message-map.csv` — keyword and ad alignment
- `images/` — currently four `MISSING-APPROVED-IMAGE-*.txt` files

**Blocked, do not improvise:** reviews (three slots marked CLIENT REVIEW NEEDED — leave the
section out rather than filling it with an unrelated review) and images (no approved
rights-cleared files exist; no stock, no AI project proof).

**Do not publish** any price, discount, licence, insurance, certification, warranty, guarantee,
review count, star rating, years in business, response-time promise, emergency availability or
promotion. None is verified.

**Remove the countdown module entirely.**

**Acceptance criteria:** see `qa-checklist.md` in the folder — desktop, mobile, phone, form,
tracking, keyword-message, review, image, no-placeholder and no-false-claim checks.

**Dependencies:** ideally ships after the P0 duplicate-form and phone-link fixes so QA is done
once.
{FOOT}""", "High", url, "P0 form/phone fixes preferred first",
        f"landing-pages/2026-09-02-final/{folder}/")

add("p1-image-request.md",
    "[P1] Softwind Power Washing — Client image request for landing pages",
    """**Business impact:** all 24 landing-page image slots across six pages are empty. A
repository-wide search found no approved, rights-cleared Softwind project images.

**Required:** original photographs of completed Softwind Power Washing work, owned by the client,
with written permission for advertising use.

**Per page, four slots:** hero (landscape, 1600x900), proof-1 and proof-2 (landscape, 1200x800,
completed jobs on that page's surface type), process (landscape, 1200x800, crew working).

**Exclusions:** visible license plates, house numbers, faces, unrelated branding, and any
out-of-scope service (roof cleaning, gutter cleaning, paver sealing, landscaping, masonry).

**Not acceptable:** stock imagery without Walter's explicit approval · AI-generated imagery as
completed-project proof · images scraped from the public site (published does not mean
rights-cleared).

**Full gap list:** `landing-pages/2026-09-02-final/IMAGE-GAPS.md` and
`MASTER-IMAGE-MANIFEST.csv`.

**Acceptance criteria:** at least one approved image per page hero slot, with ownership and
approval evidence recorded in the manifest.
""", "High", "n/a", "client input",
    "landing-pages/2026-09-02-final/IMAGE-GAPS.md")

add("p2-01-iconnode-investigation.md",
    "[P2] Softwind Power Washing — Identify process.iconnode.com in the lead path",
    f"""**Business impact:** an undocumented third party receives a POST on every page load and
again at form submission, on an endpoint named `/google-ads/`. Nothing in the client records
documents an engagement with this vendor.

**Affected URLs:** {ALLURL}

**Current behavior:** `POST https://process.iconnode.com/google-ads/` — once per page load on all
7 URLs, and again at submission. **Zero occurrences in the rendered page source**, so it is
injected at runtime, consistent with a GTM Custom HTML tag.

**Required:** identify the script owner, who added it, the plugin/theme/GTM source, purpose, data
transmitted, destination, retention, current authorization and whether it is still required.

**Do not remove it before ownership is established.** If authorized, we document it. If not,
removal is raised as its own approved change.

**Acceptance criteria:** vendor and owner identified · source named · data flow documented ·
authorization confirmed · keep/scope/remove recommendation.
{FOOT}""", "Normal", ALLURL, "none",
    "audits/2026-09-02-r7a-implementation-source-audit.md")

add("p2-02-sgcaptcha.md",
    "[P2] Softwind Power Washing — SG-Captcha behaviour on paid landing pages",
    f"""**Business impact:** SG-Captcha was observed intercepting a paid landing page once. If it
challenges real Google Ads visitors it costs sessions on pages that have cost ~$29.57 a click.
The evidence is intermittent, so this is monitoring, not a proven blocker.

**Affected URLs:** {ALLURL}

**Current behavior:** 2026-09-01 HTTP **202** with the chain passing through
`/.well-known/sgcaptcha/`. 2026-09-02 HTTP **200** on all 7 pages with no sgcaptcha request, and
it did not block a controlled form submission.

**Required:** document trigger conditions, affected traffic sources, false-positive rate,
available exclusions or allowlists for paid landing pages, and evidence about whether real Google
Ads visitors are ever challenged.

**Do not disable SG-Captcha.** It is a security control and there is no evidence it is harming
genuine visitors.

**Acceptance criteria:** trigger conditions documented · false-positive evidence · allowlist
options · recommendation with supporting data.
{FOOT}""", "Normal", ALLURL, "none",
    "audits/2026-09-02-r7a-implementation-source-audit.md")

with (CU / "CLICKUP-IMPORT.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(tasks[0].keys()))
    w.writeheader()
    w.writerows(tasks)
(CU / "README.md").write_text(f"""# ClickUp launch task package — 2026-09-02

{len(tasks)} tasks. Each file opens with `TASK TITLE:` / `TASK DESCRIPTION:` and pastes straight
into ClickUp. Bulk import: `CLICKUP-IMPORT.csv`.

**No task was created in the external ClickUp system.** These are local files only.

| Priority | Count | Blocks launch? |
|---|---:|---|
| P0 technical | 6 | measurement trust, not delivery |
| P1 content (6 pages) + image request | 7 | message match |
| P2 investigation | 2 | no |

## Standing instructions

- Preserve `AW-18369652705`. **Do not remove `AW-17878095007` globally** — sibling account,
  separate approval.
- Do not remove `process.iconnode.com` before ownership is established.
- Do not disable SG-Captcha.
- **Do not remove or expose the Gravity Forms honeypot `input_9`.**
- Do not change any Google Ads tag or conversion setting — Green Marketing owns that layer.
- Do not change any URL slug.
- Staging first; attach a network capture as QA evidence.
""", encoding="utf-8")
print(f"clickup: {len(tasks)} tasks")
