# LOCAL DRAFT — NOT DEPLOYED · **SUPERSEDED 2026-08-11**

> **SUPERSEDED.** This standalone HTML draft is **retained for historical reference only**. It was
> never deployed and never will be. The live content workflow now targets the client's actual
> WordPress/Divi template at `https://richardb891.sg-host.com/`.
>
> **Current authoritative documents:**
> - `clients/pro-green-dallas/clickup-wordpress-landing-page-task.md` — the developer handoff
> - `clients/pro-green-dallas/landing-page-template-character-budget.md` — section-by-section copy and counts
> - `clients/pro-green-dallas/landing-page-content-backlog.md` — page priority and future briefs
>
> The phone, tracking and attribution rules in this draft remain correct and were carried forward
> verbatim into those documents.

---

## Original header

This directory holds a **local-only reference implementation** of the canonical Pro Green Dallas
campaign landing page.

## Status

| | |
| --- | --- |
| Deployed | **NO** |
| Approved for deployment | **NO** |
| Uploaded, pushed, or published anywhere | **NO** |
| Wired to any live GTM container or tag | **NO** |

## What this is

A specification aid that accompanies
`clients/pro-green-dallas/canonical-landing-page-developer-handoff.md`. It exists so the
development team can see the intended structure, copy, phone-number handling, and attribution
fields as working markup rather than prose.

## What this is NOT

- Not production code
- Not a WordPress theme or Divi layout
- Not a substitute for the handoff document, which is authoritative on every requirement

## Critical rules baked into this draft

1. The page renders the **base number `(214) 300-9564`** in source — visible text and `tel:` href.
2. **`(214) 301-4622` never appears** — it is a WhatConverts pool number assigned at runtime.
3. **`(214) 301-3385` never appears** — it belongs to the Google Ads call asset only.
4. **Zero occurrences of `tel:%91phone%93`**, the broken shortcode live on both existing pages.
5. **No `__awcc` phone-swap tag** — WhatConverts owns number replacement.
6. **No Austin tags or content** — no `GTM-54Q4TVXF`, no `AW-11240766632`, no `G-MHX199EBNJ`,
   no (512) numbers.
7. **No 10% OFF** or any expired promotion.
8. Same-day wording is exactly **"Same-Day Service May Be Available."**
9. Measurement scripts are **not deferred** until user interaction.

## Tag placeholders

`index.html` uses **placeholder comments** where live tags belong. Real container and conversion
IDs are specified in the handoff §8.1 and must be inserted by the development team at build time.
No live tag is embedded here, so this file cannot accidentally send data if opened.

## Files

| File | Purpose |
| --- | --- |
| `brief.yaml` | Completed `templates/landing-page/brief.template.yaml` |
| `index.html` | Reference markup and copy |
| `attribution.js` | Reference click-ID capture and persistence |
