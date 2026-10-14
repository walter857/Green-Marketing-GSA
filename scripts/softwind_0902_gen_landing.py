#!/usr/bin/env python3
"""Generate the complete landing-page content package: 6 folders x 9 files, plus
master image manifest and image gaps."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "clients/softwind-power-washing/landing-pages/2026-09-02-final"
PHONE, TEL = "(631) 502-7946", "+16315027946"

P = [
 dict(n="01-power-washing", page="Power Washing", ag="202870585390",
      url="https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/",
      title="Power Washing Long Island | Free Quote",
      meta="Power washing for Long Island homes. Siding, concrete and walkways washed with the right pressure for each surface. Request a free quote.",
      h1="Power Washing Across Long Island",
      hero="Dirt, grime and algae build up on every exterior surface. We power wash homes across Nassau and Suffolk County, matching the pressure and method to each surface we clean.",
      focus="power washing",
      kws=["power washing","power washing near me","power washing service","power washing services near me","power washing company near me"],
      surf="siding, concrete, walkways and driveways", method="power washing",
      benefits=["Your home looks cared for from the street again","Dirt, grime and algae lifted from siding, concrete and walkways","Pressure matched to each surface, not one setting for everything"],
      faq=[("How do you decide what pressure to use?","We match the pressure and method to the surface. Siding, concrete and pavers each take a different approach."),
           ("Do I need to be home?","No. Tell us what you need washed and we can work through it with you by phone."),
           ("How do I get a quote?","Send the form or call "+PHONE+". Tell us the surfaces you want washed and we will come back with a free quote.")],
      ads=["823152917197","823152917200"]),
 dict(n="02-pressure-washing", page="Pressure Washing", ag="202870585870",
      url="https://offer.softwindli.com/residential-pressure-washing/",
      title="Residential Pressure Washing Long Island | Free Quote",
      meta="Residential pressure washing across Nassau and Suffolk County. Siding, walkways, patios and driveways cleaned with the pressure each surface can take.",
      h1="Residential Pressure Washing On Long Island",
      hero="Pressure washing for homes across Nassau and Suffolk County. Siding, walkways, patios and driveways, cleaned with the pressure each surface can actually take.",
      focus="pressure washing",
      kws=["pressure washing","pressure washing near me","residential pressure washing near me"],
      surf="siding, walkways, patios and driveways", method="pressure washing",
      benefits=["A cleaner exterior without guesswork about pressure","Built-up grime removed from the surfaces guests actually see","One visit covers siding, walkways and hard surfaces"],
      faq=[("Is pressure washing safe for my siding?","We match the pressure to the material. Where high pressure is wrong we use a lower-pressure method instead."),
           ("What areas do you serve?","Homes across Long Island, in Nassau and Suffolk County."),
           ("How do I get a quote?","Send the form or call "+PHONE+" and tell us what needs washing.")],
      ads=["823152917203","823152917206"]),
 dict(n="03-house-washing", page="House Washing", ag="202870585910",
      url="https://offer.softwindli.com/house-washing-company/",
      title="House Washing Long Island | Free Quote",
      meta="House washing across Long Island. Siding, trim and exterior walls cleaned of dirt, grime and algae. Serving Nassau and Suffolk County. Free quotes.",
      h1="House Washing Across Long Island",
      hero="Siding, trim and exterior walls washed clean. We serve homeowners throughout Nassau and Suffolk County and match the method to your siding.",
      focus="house washing",
      kws=["house washing near me","house pressure washing near me","house power washing near me","exterior house washing near me"],
      surf="siding, trim and exterior walls", method="house washing",
      benefits=["Siding that looks maintained rather than weathered","Algae and grime lifted from the walls and trim","A method chosen for your siding material"],
      faq=[("Will house washing damage my siding?","Not when the method fits the material. We choose the approach for your siding rather than applying one setting everywhere."),
           ("Do you wash trim and gutters too?","Tell us what you want included and we will cover it in the quote."),
           ("How do I get a quote?","Send the form or call "+PHONE+".")],
      ads=["823152917209","823152917212"]),
 dict(n="04-soft-washing", page="Soft Washing", ag="202870586310",
      url="https://offer.softwindli.com/soft-house-washing/",
      title="Soft Washing Long Island | Free Quote",
      meta="Soft washing for Long Island homes. Low pressure and the right cleaning solution lift algae and grime from siding and trim. Free quotes.",
      h1="Soft Washing For Long Island Homes",
      hero="Soft washing uses low pressure and the right cleaning solution instead of force. It lifts algae and grime from siding and trim without driving water where it should not go.",
      focus="soft washing",
      kws=["soft house washing near me","soft washing near me"],
      surf="siding, trim and delicate exterior surfaces", method="soft washing",
      benefits=["Cleaning power without high pressure on delicate surfaces","Algae and organic growth lifted rather than blasted","A gentler option for older siding and trim"],
      faq=[("What is the difference between soft washing and pressure washing?","Soft washing uses low pressure and a cleaning solution. Pressure washing relies on force. Some surfaces need one, some need the other."),
           ("Is soft washing better for older siding?","It is often the right choice where high pressure would be too aggressive."),
           ("How do I get a quote?","Send the form or call "+PHONE+".")],
      ads=["823152917215","823152917218"]),
 dict(n="05-driveway-pressure-washing", page="Driveway Pressure Washing", ag="202870586110",
      url="https://offer.softwindli.com/driveway-pressure-washing/",
      title="Driveway Pressure Washing Long Island | Free Quote",
      meta="Driveway pressure washing across Long Island. Concrete, pavers and stone cleaned of dirt, oil marks and algae. Serving Nassau and Suffolk County.",
      h1="Driveway Pressure Washing On Long Island",
      hero="Concrete, pavers and stone driveways washed clean of dirt, oil marks and algae. Serving homeowners across Nassau and Suffolk County.",
      focus="driveway pressure washing",
      kws=["driveway pressure washing near me","driveway power washing near me"],
      surf="concrete, pavers and stone", method="driveway pressure washing",
      benefits=["A driveway that no longer drags down the whole front of the house","Dirt, oil marks and algae lifted from concrete and pavers","Pressure matched to the surface so pavers stay put"],
      faq=[("Can you wash pavers without moving the jointing sand?","We adjust the pressure for pavers so the joints are not stripped out."),
           ("Do you wash walkways and paths as well?","Yes. Tell us what you want included and we will quote it together."),
           ("How do I get a quote?","Send the form or call "+PHONE+".")],
      ads=["823152917221","823152917224"]),
 dict(n="06-patio-pressure-washing", page="Patio Pressure Washing", ag="202870586150",
      url="https://offer.softwindli.com/patio-power-washing/",
      title="Patio Pressure Washing Long Island | Free Quote",
      meta="Patio pressure washing across Long Island. Pavers, concrete and stone patios cleaned of dirt, grime and algae. Serving Nassau and Suffolk County.",
      h1="Patio Pressure Washing On Long Island",
      hero="Patios, pavers, walkways and pool surrounds washed clean. We match the pressure to the surface so pavers and jointing sand stay where they belong.",
      focus="patio pressure washing",
      kws=["patio pressure washing near me","patio power washing near me","concrete pressure washing near me"],
      surf="pavers, concrete and stone", method="patio pressure washing",
      benefits=["A patio you want to sit on again","Grime and algae lifted from pavers, concrete and stone","Jointing sand protected by matching pressure to the surface"],
      faq=[("Will pressure washing damage my pavers?","Not when the pressure suits the surface. We adjust rather than using one setting everywhere."),
           ("Do you clean pool surrounds?","Yes. Include it when you describe the area and we will quote it."),
           ("How do I get a quote?","Send the form or call "+PHONE+".")],
      ads=["823152917227","823152917230"]),
]

SLOTS = [("hero", "landscape", "1600x900", "the finished exterior after washing"),
         ("proof-1", "landscape", "1200x800", "a completed job on the page's surface type"),
         ("proof-2", "landscape", "1200x800", "a second completed job, different property"),
         ("process", "landscape", "1200x800", "the crew working, equipment in frame")]
master, gaps = [], []

for p in P:
    d = BASE / p["n"]
    (d / "images").mkdir(parents=True, exist_ok=True)
    kwlist = ", ".join(p["kws"])
    b = "\n".join(f"- {x}" for x in p["benefits"])
    faq_md = "\n\n".join(f"**{q}**\n\n{a}" for q, a in p["faq"])
    faq_html = "\n".join(
        f'    <div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in p["faq"])

    (d / "README.md").write_text(f"""# {p['page']} — final landing-page content

| | |
|---|---|
| Page name | {p['page']} |
| Current URL | {p['url']} |
| Final H1 | {p['h1']} |
| Primary keyword family | {kwlist} |
| Final Google Ads ad group | {p['page']} |
| Ad group ID | `{p['ag']}` |
| Live RSA IDs | `{p['ads'][0]}`, `{p['ads'][1]}` |
| Phone number | {PHONE} |
| Image status | **NO APPROVED IMAGES AVAILABLE** — see `image-manifest.csv` and `../IMAGE-GAPS.md` |
| Developer ticket | `clickup-tickets/2026-09-02-final-launch/` P1 content task for this page |
| Copy status | **FINAL — ready to paste. Reviews and images blocked on client input.** |

**Do not change the URL slug.** Do not redesign the template. Replace text only.
""", encoding="utf-8")

    (d / "final-copy.md").write_text(f"""# {p['page']} — FINAL COPY

## Browser title
{p['title']}

## Meta description
{p['meta']}

## Top bar / header
Call: {PHONE}

## H1
{p['h1']}

## Hero copy
{p['hero']}

## Primary CTA
Request A Free Quote

## Secondary CTA
Call {PHONE}

## Introductory copy
Every property is different. Tell us which surfaces you want washed and we will come back with a
free quote — no obligation, and no pressure to book on the spot.

## Service-specific benefits
{b}

## Surface and method content
We do not use one setting for everything. {p['surf'].capitalize()} each respond differently, so we
choose the pressure and the method for the surface in front of us. That is what keeps a clean
result from turning into damage.

## Service-area wording
Serving homeowners across Long Island, in Nassau and Suffolk County.

## Trust section
**CLIENT INPUT REQUIRED.** No verified trust facts are on file. Do not publish a rating, review
count, licence, insurance, certification, warranty, guarantee, years in business, response time or
promotion until the client supplies it in writing.

## Reviews
- Review 1 — **CLIENT REVIEW NEEDED**
- Review 2 — **CLIENT REVIEW NEEDED**
- Review 3 — **CLIENT REVIEW NEEDED**

No verified, service-relevant reviews for Softwind Powerwashing & Paver Sealing, 55 Carelton Ave
Suite 7, East Islip NY 11730 are on file. Do not invent one. Do not repurpose a review written
about a different service.

## FAQ
{faq_md}

## Final CTA
Request a free quote for your property.

## Form heading
Get Your Free Quote

## Form-support copy
Tell us the surfaces you want washed and we will send your free quote back.

## Phone CTA
Call {PHONE}

## Countdown
**REMOVE COUNTDOWN MODULE.** No approved promotion or expiration date exists.

## Image placement notes
See `image-manifest.csv`. Every slot is currently unfilled — no approved, rights-cleared Softwind
images were found. Do not substitute stock or AI imagery.
""", encoding="utf-8")

    (d / "final-copy.html").write_text(f"""<!-- {p['page']} — body sections only. Paste into the existing template. Do not alter layout. -->
<section class="hero">
  <h1>{p['h1']}</h1>
  <p class="hero-copy">{p['hero']}</p>
  <a class="cta-primary" href="#quote-form">Request A Free Quote</a>
  <a class="cta-secondary" href="tel:{TEL}">Call {PHONE}</a>
</section>

<section class="intro">
  <p>Every property is different. Tell us which surfaces you want washed and we will come back
  with a free quote — no obligation, and no pressure to book on the spot.</p>
</section>

<section class="benefits">
  <h2>Why homeowners book {p['method']}</h2>
  <ul>
{chr(10).join(f'    <li>{x}</li>' for x in p['benefits'])}
  </ul>
</section>

<section class="method">
  <h2>The right pressure for {p['surf']}</h2>
  <p>We do not use one setting for everything. {p['surf'].capitalize()} each respond differently,
  so we choose the pressure and the method for the surface in front of us. That is what keeps a
  clean result from turning into damage.</p>
</section>

<section class="service-area">
  <h2>Serving Long Island</h2>
  <p>Serving homeowners across Long Island, in Nassau and Suffolk County.</p>
</section>

<!-- TRUST SECTION: CLIENT INPUT REQUIRED. Publish nothing here until verified. -->
<!-- REVIEWS: three slots, all CLIENT REVIEW NEEDED. Do not fill with unrelated reviews. -->

<section class="faq">
  <h2>{p['page']} questions</h2>
{faq_html}
</section>

<section class="final-cta" id="quote-form">
  <h2>Get Your Free Quote</h2>
  <p>Tell us the surfaces you want washed and we will send your free quote back.</p>
  <!-- Gravity Forms gform_1 — exactly ONE instance per page. Preserve the honeypot. -->
  <a class="cta-secondary" href="tel:{TEL}">Call {PHONE}</a>
</section>

<!-- COUNTDOWN MODULE: REMOVE. No approved promotion or expiration date exists. -->
""", encoding="utf-8")

    (d / "seo-meta.txt").write_text(f"""Browser title : {p['title']}
Meta description: {p['meta']}
Canonical      : {p['url']}
H1             : {p['h1']}
Focus keyword  : {p['focus']}
Secondary family: {kwlist}
""", encoding="utf-8")

    with (d / "keyword-map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "match_type", "ad_group", "ad_group_id", "h1_location",
                    "body_copy_location", "faq_location", "cta_location"])
        for k in p["kws"]:
            w.writerow([k, "PHRASE + EXACT", p["page"], p["ag"],
                        "yes" if p["focus"] in p["h1"].lower() else "family match",
                        "hero + method section", "FAQ answer 1",
                        "form heading / final CTA"])
    with (d / "rsa-page-message-map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rsa_ad_id", "rsa_angle", "primary_headline_themes", "description_themes",
                    "landing_page_proof", "cta_alignment"])
        w.writerow([p["ads"][0], "Exact service intent, local, free quote, direct response",
                    f"{p['page']} Near You; Local {p['page']} Service; {p['page']} Long Island; Free Quote",
                    "local availability; Nassau and Suffolk; free quote",
                    "H1 + service-area section", "Request A Free Quote"])
        w.writerow([p["ads"][1], "Exterior transformation, surface method, curb appeal, estimate",
                    "Curb Appeal Starts Outside; Surface-Specific Washing; Right Pressure Per Surface",
                    "matched pressure and method; free estimate",
                    "method section + benefits", "Get A Free Estimate"])
    with (d / "image-manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["template_slot", "orientation", "dimensions", "required_subject",
                    "file_included", "original_source_path", "ownership_evidence",
                    "approval_evidence", "file_size", "alt_text", "status"])
        for slot, orient, dims, subj in SLOTS:
            alt = f"{p['method'].capitalize()} on a Long Island home"[:150]
            w.writerow([slot, orient, dims, subj, "NO", "", "NOT VERIFIED", "NOT APPROVED",
                        "", alt, "NEW CLIENT IMAGE NEEDED"])
            master.append({"page": p["page"], "folder": p["n"], "slot": slot,
                           "orientation": orient, "dimensions": dims, "subject": subj,
                           "file_included": "NO", "status": "NEW CLIENT IMAGE NEEDED",
                           "alt_text": alt})
            (d / "images" / f"MISSING-APPROVED-IMAGE-{slot}.txt").write_text(
                f"""MISSING APPROVED IMAGE — {p['page']} — slot: {slot}

Required subject : {subj}
Orientation      : {orient}
Dimensions       : {dims} minimum
Page             : {p['url']}
Alt text to use  : {alt}

Why this file exists instead of an image:
A repository-wide search found NO approved, rights-cleared Softwind project images.

Do NOT substitute:
- stock imagery (needs Walter's explicit approval for this client)
- AI-generated imagery (never permitted as completed-project proof)
- an image scraped from the public site (published does not mean rights-cleared)

Needed from the client: an original photograph of completed {p['method']} work, owned by
Softwind, with written permission to use it in advertising. Avoid visible license plates, house
numbers, faces and unrelated branding.
""", encoding="utf-8")
            gaps.append((p["page"], slot, subj, orient, dims))

    (d / "developer-implementation.md").write_text(f"""# Developer implementation — {p['page']}

**URL (do not change):** {p['url']}
**Template:** keep the existing structure and section order. This is a text replacement only.

## Replace

| Element | Current | Replace with |
|---|---|---|
| Browser title | `{p['page']} \\| Softwind Landscape & Masonry` | `{p['title']}` |
| Meta description | (varies) | see `seo-meta.txt` |
| H1 | city-locked to "Islip, West Islip & Dix Hills" | `{p['h1']}` |
| Hero copy | current hero paragraph | see `final-copy.md` |
| Service-area text | three-hamlet wording | "Serving homeowners across Long Island, in Nassau and Suffolk County." |
| FAQ | current entries | three entries in `final-copy.md` |
| Form heading | current | "Get Your Free Quote" |
| Countdown module | "Offer Ends" countdown | **REMOVE ENTIRELY** |

## Leave unchanged

- Page URL and slug
- Template layout, section order and CSS
- Gravity Forms `gform_1` field set and the honeypot (`input_9`)
- The phone number {PHONE}
- GA4, GTM, WhatConverts and ClickCease tags

## Blocked, do not improvise

- **Reviews** — three slots marked CLIENT REVIEW NEEDED. Leave the section out rather than
  filling it with an unrelated review.
- **Images** — no approved files exist. See `images/MISSING-APPROVED-IMAGE-*.txt`.
- **Trust claims** — publish no rating, licence, insurance, warranty, years in business,
  response time, price or promotion.

## Related tracking tickets (separate work)

Duplicate `gform_1`, duplicate HTML IDs, malformed `tel:(631)`, duplicate GTM load and the
form-success dataLayer event are handled in the P0 technical tasks, not here.
""", encoding="utf-8")

    (d / "qa-checklist.md").write_text(f"""# QA checklist — {p['page']}

**URL:** {p['url']}

## Desktop
- [ ] HTTP 200, HTTPS, no redirect
- [ ] Browser title reads `{p['title']}`
- [ ] H1 reads `{p['h1']}`
- [ ] Hero copy matches `final-copy.md`
- [ ] Countdown module gone
- [ ] No layout regression

## Mobile
- [ ] Layout renders, no horizontal scroll
- [ ] CTA reachable without pinch-zoom
- [ ] Form usable
- [ ] Page speed not worse than the current build

## Phone
- [ ] Displayed number is {PHONE}
- [ ] Every `tel:` href is `tel:{TEL}`
- [ ] No `tel:(631)` or other malformed href remains
- [ ] Mobile tap opens the dialer with the full number

## Form
- [ ] Exactly ONE `form#gform_1` on the page
- [ ] Zero duplicate HTML IDs
- [ ] Honeypot `input_9` present, hidden and empty
- [ ] Submits successfully and reaches `/thank-you/`

## Tracking
- [ ] GA4 `G-D4BZM40RYD` fires
- [ ] GTM `GTM-P3LD97NN` loads ONCE
- [ ] WhatConverts still sets `wc_client` with the GCLID
- [ ] Softwind conversion still fires on a real submission
- [ ] GCLID, GBRAID, WBRAID and all UTMs survive to the form POST

## Keyword-message
- [ ] `{p['focus']}` appears naturally in title, H1, hero and body
- [ ] Copy matches the live RSAs `{p['ads'][0]}` and `{p['ads'][1]}`
- [ ] No keyword stuffing

## Review
- [ ] No unverified review published
- [ ] No rating or review count published

## Image
- [ ] No stock image used without explicit approval
- [ ] No AI image used as project proof
- [ ] Every published image is client-owned and rights-cleared

## No placeholder / no false claim
- [ ] No lorem ipsum or TODO text
- [ ] No price, discount, licence, insurance, warranty, guarantee, years in business,
      response-time promise or emergency-service claim
""", encoding="utf-8")

with (BASE / "MASTER-IMAGE-MANIFEST.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(master[0].keys()))
    w.writeheader()
    w.writerows(master)
(BASE / "IMAGE-GAPS.md").write_text(f"""# IMAGE GAPS — 2026-09-02

## Summary

| Category | Count |
|---|---:|
| Approved image file included | **0** |
| Approved image referenced but unavailable locally | 0 |
| Ownership unverified | 0 |
| **New client image needed** | **{len(gaps)}** |

**A repository-wide search found no approved, rights-cleared Softwind project images.** The only
image files in this client folder are Playwright screenshots from the PLAN-R1B conversion test,
which are diagnostic evidence, not marketing assets.

## What was searched

Existing Softwind project folders · approved landing-page image folders · local source folders ·
client-approved downloads · previously approved content assets · repository image manifests ·
Green Marketing image-approval records. All returned nothing usable.

## Rules that produced this result

- A public website image is **not** rights-cleared merely because it is published.
- Stock imagery requires Walter's explicit approval for this client and content type.
- AI-generated imagery may **never** be used as completed-project proof.
- No fake or placeholder project image was created.

## Needed from the client

Original photographs of completed Softwind Power Washing work, owned by the client, with written
permission for advertising use. Avoid visible license plates, house numbers, faces and unrelated
branding. Exclude anything showing an out-of-scope service.

| Page | Slot | Subject | Orientation | Min dimensions |
|---|---|---|---|---|
""" + "\n".join(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in gaps) + "\n", encoding="utf-8")
print(f"landing package: {len(P)} folders, {len(master)} image slots, {len(gaps)} gaps")
