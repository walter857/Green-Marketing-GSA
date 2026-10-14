TASK TITLE:

[P1] Softwind Power Washing — Publish final House Washing landing-page copy

TASK DESCRIPTION:

**Business impact:** the page currently carries the wrong brand in the browser title
("Softwind Landscape & Masonry"), an H1 locked to three hamlets while the campaigns target 80
places, and an unsupported resetting countdown. The matching Google Ads ad group is now LIVE, so
the ad message and the page must agree.

**Affected URL:** https://offer.softwindli.com/house-washing-company/ — **do not change the slug.**

**Current behavior:** wrong-brand title · city-locked H1 · generic hero · resetting "Offer Ends"
countdown with no dated offer.

**Required behavior:** apply the exact final copy. Keep the existing template structure and
section order. This is a text replacement, not a redesign.

**Implementation file path:**
`clients/softwind-power-washing/landing-pages/2026-09-02-final/03-house-washing/`

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

## QA required

**Desktop:** render, layout, no regression. **Mobile:** layout, no horizontal scroll, CTA
reachable. **Tracking:** attach a network capture showing tags still fire.

## Regression checks

Form still submits and reaches `/thank-you/`; phone link still dials; no other page affected.

## Rollback

Restore the previous template or plugin revision. No data migration involved.

## Developer signoff

Name: ______________  Date: __________  Release/commit: ______________

---

## Google Drive package (uploaded 2026-09-02)

| Item | Link |
|------|------|
| Page folder | https://drive.google.com/drive/folders/1Vkn8hTcCJ_OcrrR6NCX68lDG0Wop1Rdi |
| Final copy (Markdown) | https://drive.google.com/file/d/1fW6pq7QWI0lGERQ0iPcT3RwgCWrcxbSk/view |
| Final copy (HTML) | https://drive.google.com/file/d/1zkRkPclo31B6KpYhR-3ZKeJ-UvvdWZab/view |
| Developer implementation | https://drive.google.com/file/d/1Es8-vM0JJikcdYYOO5kUoSihrAksrE2S/view |
| QA checklist | https://drive.google.com/file/d/1YuMGtn9fetxi_-Ed4BtvmGFbHxFXBZhI/view |
| Keyword map | https://drive.google.com/file/d/1ekszQEC3Q6f2mZ0TNzdCzCcj7aM_LHGU/view |
| SEO meta | https://drive.google.com/file/d/11gHXRjJPIvbBJzPHBz7MpKctT7_sCuom/view |
| Image folder | https://drive.google.com/drive/folders/14XGIjZidKi6cGqmB81os2HIk40S5JlkB |
| Package root | https://drive.google.com/drive/folders/1-s7jbsjdUbi-VtenRi-htQ8aEwN_7iYc |
| Master files | https://drive.google.com/drive/folders/1sutGDuRkaKPBhcQsnZEV6_5bjKN3BZci |

**Exact page URL:** https://offer.softwindli.com/house-washing-company/
**Google Ads ad group:** House Washing — `202870585910`
**Canonical keyword family:** house washing near me / house pressure washing near me
**Phone number that must appear:** (631) 502-7946

### Current page behaviour
The live page does not yet carry this copy. Tracking defects P0-01 through P0-04 are
still open on it, so this page currently reports no reliable form conversion.

### Acceptance criteria
- [ ] Copy published exactly as written in `final-copy.md`; no invented claim added
- [ ] Phone renders as (631) 502-7946 and the `tel:` link is `tel:+16315027946`
- [ ] Desktop QA: layout intact at 1440px and 1920px, no horizontal scroll
- [ ] Mobile QA: layout intact at 390px, tap targets >= 44px, phone tappable
- [ ] Form QA: submit reaches the CRM, honeypot `input_9` left EMPTY, success state shown
- [ ] Phone QA: number matches the Google Ads call asset and is answered in business hours
- [ ] Tracking QA: form success fires exactly one conversion; no duplicate GTM container
- [ ] Page-speed QA: LCP under 2.5s on a throttled mobile run
- [ ] No image slot left showing a broken image; unfilled slots stay blank, not placeholder

### Rollback
Restore the previous page revision from the WordPress revision history. This ticket
changes content only; it must not alter the Google Ads final URL.

### Developer signoff
Name: ______________________  Date: ____________  Build verified in staging first: Y / N
