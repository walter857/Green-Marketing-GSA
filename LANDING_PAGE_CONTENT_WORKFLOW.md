# Green Marketing Landing Page Content Workflow

This file is mandatory for every landing-page task in this repository. Read it completely before inspecting a client, drafting landing-page content, creating a Google Drive folder or document, selecting images, or preparing a developer handoff.

This workflow creates content drafts and Google Drive handoff artifacts. It does not authorize a WordPress edit, GTM change, WhatConverts change, Google Ads final-URL change, DNS change, or live deployment.

## Required client gate

Before client-specific landing-page work, require and validate:

1. Exact Google Ads child account name.
2. Ten-digit child customer ID, not the MCC ID.
3. Exact service.
4. Campaign name.
5. Ad group name.
6. Canonical ad-group intent and its Phrase and Exact keywords.
7. Business name, approved phone number, service area, and proposed slug or URL.
8. Approved claims, offer, reviews, legal text, and image policy.
9. Landing-page template HTML, blank screenshot, and completed example screenshot.
10. Google Drive delivery request, destination root, and approval owner when Drive creation is requested.

Do not infer missing client facts from another client, the template, a prior landing page, an ad, or a website section that has not been verified.

## Canonical template sources

The client work order must identify local paths for:

- Blank template screenshot.
- Completed service example screenshot.
- Template HTML.

Canonical Google Doc structure:

`https://docs.google.com/document/d/1bQR5wLIF47fd-wNOaNxtjlun1ch8Fc5kmfCA93vuFuc/edit`

Default template document ID:

`1bQR5wLIF47fd-wNOaNxtjlun1ch8Fc5kmfCA93vuFuc`

The example Google Doc provides structure only. It is not factual authority. Never carry its business name, phone number, locations, reviews, claims, offers, deadlines, image links, or distinctive copy into a different client's document.

## Operating sequence

1. Validate the work order and client profile.
2. Confirm the exact service, campaign, ad group, Phrase keyword, Exact keyword, and landing-page intent.
3. Inspect the template HTML and both screenshots.
4. Generate or refresh the template character-budget map.
5. Draft the complete page to the structure below.
6. Validate client facts, phone number, offer, reviews, images, service area, and legal text.
7. Compare each editable element against the template character count.
8. Render the copy in a safe local preview at desktop and mobile sizes.
9. Repair wrapping, overflow, clipping, imbalance, or excessive empty space.
10. Save the local content manifest and QA report.
11. If Drive delivery is requested and explicitly approved, create or update the designated folders and native Google Doc, giving every page its own page folder and `Images` subfolder.
12. Read all created Drive resources back and record their IDs, URLs, parents, and verification status.
13. Run the reusable rule checks in `gm_gsa.landing_page_rules` against the delivered layout, image records, image instructions, review cards, and sharing state. Any violation is a blocker.
14. Stop before any live website or Google Ads change.

## Page and Google Doc structure

Create one content document per canonical ad-group intent unless the approved plan explicitly maps multiple equivalent ad groups to one canonical page.

The document must include:

### Page metadata

- Client.
- Exact Google Ads child account name and ID.
- Service.
- Campaign.
- Ad group.
- Canonical intent.
- Phrase keyword.
- Exact keyword.
- Proposed slug.
- Current or proposed final URL.
- Primary CTA.
- Approved phone number.
- Service area.
- Draft status and approval owner.

### SEO Settings

- Final slug.
- SEO title.
- Meta description.
- Primary CTA.

### 1. Header

- Approved logo.
- Call button copy.
- Approved phone number.

### 2. Hero Section and Form

- H1.
- Introductory paragraph.
- Four benefit bullets.
- Call CTA.
- Hero image link or brief and alt text.
- Form badge.
- Form heading and intro.
- Field labels, placeholders, service selection, disclosure, and button.

### 3. Three Problem or Need Cards

- Section heading.
- Section introduction.
- Three distinct card icons, headings, and descriptions.
- Section CTA.

### 4. Promotional or Evergreen CTA Section

- Badge.
- Heading.
- Supporting paragraph.
- CTA.
- Countdown only when the client has a real approved deadline.

Never reuse the template's 10-percent discount or countdown without a verified promotion and deadline. When no real promotion exists, preserve the section's visual role with an evergreen CTA and instruct the developer to disable the countdown.

### 5. Main Service Feature

- Main image link or brief and alt text.
- Section heading.
- Section paragraph.
- Three feature headings and descriptions.
- CTA.

### 6. Three Supporting Cards

- Section heading and introduction.
- Three approved images.
- Three icons.
- Three headings and descriptions.
- Alt text.
- CTA.

### 7. Recent Project Highlights

- Section heading and introduction.
- Four real project images when available.
- Filename, Drive link, caption or purpose, and alt text for each image.

Do not present stock or generated imagery as completed client work.

### 8. Three-Step Process

- Section heading.
- Three step icons.
- Three step headings.
- Three descriptions.
- Three short supporting lines.

The process must reflect the client's real workflow and staffing.

### 9. Customer Reviews

- Section heading.
- Three verified reviews when available.
- Exact review text, reviewer name, and approved source.

Never invent or rewrite a review.

**Review retrieval is automatic and ordered. Do not stop at the first failure.**

1. Attempt the client's verified Google Business Profile first.
2. If direct GBP access fails for any reason, automatically fall back to the client's own
   official website reviews or testimonials page. This fallback is expected behavior, not an
   exception that needs a new instruction.
3. Only when both fail, insert `REAL REVIEW REQUIRED - DO NOT PUBLISH` and fail deployment
   readiness.

When the website is the source, treat it as a testimonial, not a Google review. Never label a
website testimonial as a Google review unless each text and reviewer is matched directly to
that exact GBP.

Copy the **complete** text exactly as displayed. Do not paraphrase, combine, correct, shorten
to fit a character budget, or fix the source's punctuation. Extract programmatically rather
than retyping, and assert the stored text still equals the source on every validation run.

Each review card must contain the displayed star rating, the exact review text, and the exact
reviewer name as displayed. When the card template carries an extra line, fill it with a
neutral customer label; never repeat the same placeholder three times inside one card.

Review provenance — source URL, platform, retrieval date, snapshot — belongs in the internal
manifest. It must never appear inside a customer-facing review card.

### 10. FAQ Section and Second Form

- FAQ heading.
- Five service-specific questions and answers.
- Second form heading and intro.
- Field labels, placeholders, disclosure, and CTA.

### 11. Final CTA Banner

- Approved icon.
- Heading.
- Supporting line.
- CTA.

### 12. Footer

- Approved logo.
- Approved phone number.
- Privacy Policy and Terms links or clearly marked required links.

### Handoff appendices

- Character Count QA.
- Image Asset Plan.
- Tracking and Form Requirements.
- Developer Notes.
- Desktop and Mobile QA.
- Acceptance Criteria.

## Character-count rules

Use the actual template HTML as the baseline. Do not estimate counts from screenshots.

Count rendered Unicode characters after:

- Decoding HTML entities.
- Removing script, style, noscript, SVG path data, and hidden technical values.
- Collapsing repeated whitespace to one space.
- Keeping spaces and punctuation in the count.
- Keeping repeated copy slots as separate occurrences.

For every editable element, report:

- Section.
- Element.
- Stable DOM selector or anchor.
- Template placeholder text.
- Template character count.
- Recommended target range.
- Final text.
- Final character count.
- Difference and percentage.
- Expected desktop and mobile line count.
- Desktop wrapping risk.
- Mobile wrapping risk.
- Final render result.

Use approximately plus or minus 10 percent as the default target. This is not a hard editorial rule. Factual accuracy, natural language, conversion clarity, and service relevance take priority.

A string inside the target range can still fail because of long words or bad line breaks. A longer string can pass when the actual desktop and mobile render remains clean. Rendering is the final authority.

Never keyword-stuff, remove required facts, invent shorter claims, or write awkward English to match a count.

## Known template count fixtures

Use these values to verify the HTML parser:

| Slot | Template text | Characters |
|---|---|---:|
| Header call button | `CALL: 123-456-7890` | 18 |
| Hero H1 | `Custom SHORTCODE in SHORTCODE` | 29 |
| Hero paragraph | `Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor.` | 79 |
| Hero benefit | `Lorem ipsum dolor sit amet, consectetur.` | 40 |
| Hero form heading | `Request Your Free SHORTCODE Quote` | 33 |
| Problem-cards heading | `Lorem ipsum dolor sit amet.` | 27 |
| Problem-cards intro | `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore.` | 110 |
| Promotional heading | `Get 10% Off Your Next SHORTCODE Project` | 39 |
| Main feature heading | `Beautiful, Durable SHORTCODEs built for SHORTCODE Living` | 56 |
| Main feature paragraph | Template paragraph | 207 |
| Three-card section heading | `One Team for Your Entire Outdoors` | 33 |
| Gallery heading | `Recent Project Highlights` | 25 |
| Three-step heading | `Your Dream Yard in 3 Simple Steps` | 33 |
| Reviews heading | `What Your Neighbors Are Saying` | 30 |
| FAQ heading | `Frequently Asked Questions` | 26 |
| Final CTA heading | `Our 100% Satisfaction Guarantee` | 31 |

## Visual QA

Render a safe local copy of the template. Never edit the live reference website.

At minimum, verify:

- Desktop: 1440 by 900.
- Mobile: 390 by 844.
- No horizontal overflow.
- No clipped text or buttons.
- No overlap between hero content and the form.
- Balanced three-card heights.
- Natural H1 and CTA wrapping.
- Readable FAQ content.
- Fully visible forms.
- Correct image crops at both sizes.
- No leftover `SHORTCODE`, `Lorem ipsum`, reference-client facts, or placeholder URLs.

Save local QA screenshots and record their paths in the client landing-page manifest.

## Content rules

- Use one canonical service-buying intent per page by default.
- Align the Phrase keyword, Exact keyword, RSA promise, H1, introduction, CTA, form, and URL.
- Use the service and location naturally. Do not force `near me` into copy.
- Use only verified services, service areas, phone numbers, offers, licenses, warranties, financing, response times, ratings, reviews, and other claims.
- Never invent prices, promotions, deadlines, scarcity, awards, years, review counts, or availability.
- Use one consistent primary CTA unless an approved plan requires another action.
- Use concise, scannable copy without generic filler.
- The website base phone number must be client approved. Do not hard-code a Google Ads call-asset number unless it is also the approved website base number.

## Image requirements

The template expects:

| Asset | Quantity | Recommended shape | Use |
|---|---:|---|---|
| Logo | 1, reused | Transparent SVG or PNG; source template uses 259 by 36 | Header and footer |
| Hero background | 1 | Approximately 1920 by 900 | Wide hero crop |
| Main feature image | 1 | Approximately 1200 by 1000 | Primary service scene |
| Supporting card images | 3 | 800 by 600, 4:3 | Three distinct service or process scenes |
| Project gallery images | 4 | 1000 by 606 or equivalent wide crop | Real project examples |

### Image sourcing priority

Work this order top to bottom. Never skip to a lower tier before genuinely exhausting the
one above it, and record the attempt and its outcome even when it fails.

1. Verifiable client-owned project photographs.
2. Verifiable client-owned website or Google Business Profile imagery, including images
   hosted on the client's own domain.
3. High-quality stock with a **confirmed** commercial reuse license.
4. A detailed image-generation request, written to a manifest for a generation tool, only
   when no appropriate source image exists.

A filename, an alt attribute, or a subject that merely relates to the client's trade is
**never** evidence of ownership. Hosting on the client's own domain proves the client
published the image; it does not prove the client photographed its own job.

### Pixel-level inspection is mandatory

Before any image is approved, downloaded into a client folder, or referenced in a document:

- Download or render the actual file.
- **Look at the pixels.** Reading a page's HTML, alt text, or metadata is not inspection.
- Confirm what the image visibly shows, and reject it when the pixels contradict the label.
- Check for watermarks, signatures, third-party logos, legible manufacturer branding,
  unrelated companies, misleading equipment, people who could be mistaken for client
  employees, and geographic or seasonal details inconsistent with the service area.

Reject outright: competitor imagery, unverified image-search results, another contractor's
photographs, agricultural or farm-field imagery for a residential service, consumer equipment
with prominent manufacturer branding, low-resolution files, and watermarked files.

### Provenance record

Keep an internal provenance manifest for every client. For each candidate image record the
original source URL, the creator when available, the license and any attribution
requirement, whether it is client-owned or generic, the intended page and image position,
dimensions and orientation, the recommended crop, the alt text, the visual-inspection
result, and the accept or reject decision with its reason.

Provenance, licensing, and sourcing language is internal. It must never appear in
customer-facing page copy, captions, badges, headings, or review cards.

### General service images versus project images

Split every page's image positions into two classes and treat them differently:

- **General service positions** may use client-owned imagery, properly licensed professional
  stock, or generated service imagery.
- **Project-gallery positions** must use authentic client project photographs, and nothing
  else.

**Never place stock or generated imagery in a project-gallery position, and never describe
any stock or generated image as the client's completed work.** When an authentic project
photograph is unavailable, leave a specific `IMAGE SUGGESTION` and report the gap. Do not
request generated imagery for a gallery position.

For every image slot, document:

- Section and purpose.
- Approved filename and Drive link.
- Inline preview when secure insertion and readback are supported.
- Dimensions and aspect ratio.
- Desktop and mobile crop guidance.
- Required subject and action.
- What must remain visible.
- What to avoid.
- Suggested SEO filename.
- Alt text.
- Whether a real company photo is required or approved stock is acceptable.
- Rights and approval status.

Real company images are preferred. Project-gallery images must be real client work unless Green Marketing explicitly approves an accurately labeled alternative.

Upload approved image files to that page's own `Images` folder, using the approved filename
for the position and preserving the file's real extension. Never rename a JPEG as PNG or
otherwise mislabel the type.

### Placeholder policy

`[DEVELOPER TODO:` is banned from landing-page content documents. Every unfilled image
position carries a specific `IMAGE SUGGESTION:` instead, and each one must state:

- the exact subject,
- the composition,
- the orientation and target aspect ratio,
- the important details that must be visible,
- whether a real client photograph is required at that position,
- what to avoid,
- the recommended alt text.

Vague wording such as "insert an image", "add a project photo", or "TBD" fails review. Never
repeat the same placeholder or instruction three times inside one card.

### Inline insertion and the sharing rule

Google Docs fetches an `insertInlineImage` URI anonymously, so it cannot read a private Drive
file. **Do not make a private image public to work around this.** Changing a file to "anyone
with the link" is not an implementation detail; it publishes the client's asset.

When secure inline insertion is unavailable:

1. Keep the uploaded image in the correct `Images` folder.
2. Record its Drive file ID and private link in the internal image manifest.
3. Leave the specific `IMAGE SUGGESTION` at that position, naming the uploaded file.
4. Report that insertion remains pending.

Never claim an image was embedded unless readback confirms an inline image object exists at
the intended location.

## Google Drive hierarchy

All Drive operations must remain inside one configured and approved root folder.

```text
<Approved Landing Page Root>/
  <Client Business Name>/
    Landing Pages/
      <Page Name>/
        <Client> - <Page Name> - Landing Page Content
        Images/
```

**Every landing-page document gets its own page folder, and every page folder gets its own
`Images` subfolder. This is mandatory, not optional.** A content document must never sit
loose in `Landing Pages/` beside another page's document, and two pages must never share one
`Images` folder: shared image folders are how one page's photo ends up on another page.

`<Page Name>` is the canonical ad-group intent the page serves, for example `Lawn Aeration`
or `Aeration & Overseeding`. When a campaign and ad group name the page unambiguously, keep
using them in the document title.

Rules:

- Create the page folder and its `Images` subfolder **before** creating or moving the document.
- Search exact folder names under the expected parent before creation.
- Reuse one unambiguous existing folder.
- Stop on duplicates or ambiguity.
- Never search or write outside the approved root.
- Never delete a Drive file or change sharing permissions from this workflow.
- Make folder and document creation idempotent.
- Record folder IDs, document ID, URL, parent IDs, and readback results.
- If a write partially succeeds, stop and report every created ID and recovery action.

### Correcting an existing layout

When a client's documents already sit in the wrong place, **move** them. Use a Drive parent
change (`addParents` plus `removeParents`); never copy, re-create, or re-copy from the master
template. Duplicating a document silently forks the content and strands whichever copy the
next session does not open.

After any move, read the file back and assert it has **exactly one** parent, and that the
parent is the intended page folder. Do not alter permissions while moving.

## Native Google Doc creation

Create each content document by copying the canonical native Google Doc. Do not rebuild it from DOCX or a blank document.

After copying:

1. Confirm the destination parent and title.
2. Confirm the tab and heading structure.
3. Replace all reference-client content.
4. Preserve heading roles and section order.
5. Add the handoff appendices.
6. Insert approved image previews only when secure insertion is supported.
7. Read the document back.
8. Confirm no reference-client fact, link, image direction, or review remains.

## Drive authorization and safety

Use a separate Drive/Docs authorization. Do not automatically reuse or expand the Google Ads OAuth refresh token.

Expected configuration names:

- `GOOGLE_DRIVE_LANDING_PAGE_ROOT_FOLDER_ID`
- `GOOGLE_DOC_LANDING_PAGE_TEMPLATE_ID`
- `GOOGLE_DRIVE_CREDENTIALS_FILE`
- `GOOGLE_DRIVE_TOKEN_FILE` when desktop OAuth is used

Never print, commit, or log credentials or token contents. Credential and token files must be excluded from Git.

The Drive publisher must default to dry-run and require an explicit apply flag plus an approved client work order before a durable write.

Support Shared Drives when used, including the required shared-drive request parameters and destination checks.

## Tracking and developer handoff

Include requirements for:

- Approved website base phone number and valid `tel:` links.
- Approved DNI without a hard-coded pool number.
- GCLID, GBRAID, WBRAID, UTM source, medium, campaign, term, and content.
- Campaign, ad group, keyword, device, landing-page URL, referrer, lead ID, original source, and consent state.
- First-party persistence.
- Form submission and thank-you behavior.
- Duplicate-event prevention.
- Mobile form QA.
- Removal of stale client tags, redirects, phone numbers, offers, and tracking values.

These are handoff requirements. Do not implement external tracking changes from this workflow.

## Completion requirements

A landing-page content task is complete only when:

1. The exact account, service, campaign, ad group, and intent are validated.
2. Every required section is complete.
3. Client truth and review truth pass.
4. The character-count report is complete.
5. Desktop and mobile visual QA pass or a blocker is documented.
6. Image assets or explicit missing-image requirements are recorded.
7. The local manifest and developer handoff exist.
8. Requested Drive folders and Doc were created only after approval and passed readback.
9. Every page has its own page folder and `Images` subfolder, and every document has exactly one parent.
10. Every image was visually inspected, has a provenance record, and sits in a position its provenance allows.
11. Every unfilled image position carries a specific `IMAGE SUGGESTION`, and `[DEVELOPER TODO:` appears nowhere.
12. No asset was made public, and no image is claimed as embedded without readback proof.
13. `gm_gsa.landing_page_rules` reports zero violations.
14. No live website, tracking, or Google Ads resource changed.
