# Developer implementation — Pressure Washing

**URL (do not change):** https://offer.softwindli.com/residential-pressure-washing/
**Template:** keep the existing structure and section order. This is a text replacement only.

## Replace

| Element | Current | Replace with |
|---|---|---|
| Browser title | `Pressure Washing \| Softwind Landscape & Masonry` | `Residential Pressure Washing Long Island | Free Quote` |
| Meta description | (varies) | see `seo-meta.txt` |
| H1 | city-locked to "Islip, West Islip & Dix Hills" | `Residential Pressure Washing On Long Island` |
| Hero copy | current hero paragraph | see `final-copy.md` |
| Service-area text | three-hamlet wording | "Serving homeowners across Long Island, in Nassau and Suffolk County." |
| FAQ | current entries | three entries in `final-copy.md` |
| Form heading | current | "Get Your Free Quote" |
| Countdown module | "Offer Ends" countdown | **REMOVE ENTIRELY** |

## Leave unchanged

- Page URL and slug
- Template layout, section order and CSS
- Gravity Forms `gform_1` field set and the honeypot (`input_9`)
- The phone number (631) 502-7946
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
