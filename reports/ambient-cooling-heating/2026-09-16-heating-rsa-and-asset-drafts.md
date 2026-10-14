# Ambient Cooling & Heating — Heating Services RSA and asset drafts
## DRAFT ONLY — nothing created in Google Ads, no ad, no asset, no association

| | |
|---|---|
| Account | `Ambient Cooling - Live` · `2401959466` |
| Campaign (proposed, **not created**) | `Search | NonBrand | Heating Services | Central MD | BOFU | 2026-10` |
| Validation | `scripts/ambient_0916_validate_rsas.py` — **PASSED** |
| Result | **6 RSAs · 90 headlines · 24 descriptions · 0 character-limit violations · 0 barred claims · 0 duplicate copy · 0 overlap between paired RSAs** |
| Raw export | `clients/ambient-cooling-heating/exports/heating-rsa-drafts-2026-09-16.csv` |

Two validator findings were corrected during drafting: a 31-character headline
(`Furnace Installation Central MD` → `Furnace Installation in MD`) and two ad groups that had 14
headlines rather than 15. Two further flags were **false positives** — the barred-claim regex was
matching the ordinary verb *"review"* in `Review Options Before You Buy`. The rule was tightened to
require a number or star, because a rating claim is `5 stars` or `200+ reviews`, not the verb.

---

## Ad group 1 — `SKAG | Furnace & Heating Repair`

Final URL `https://offer.ambientcoolingandheating.com/furnace-heating-repair/` · Path1 `heating` ·
Path2 `repair` · no tracking template · no URL suffix · no Final URL expansion.

### RSA A — keyword-first, three openers pinned to HEADLINE_1

| Pin | Chars | Headline |
|---|---:|---|
| **H1** | 27 | Furnace Repair in Central MD |
| **H1** | 24 | Furnace & Heating Repair |
| **H1** | 23 | Heating Repair Near You |
| — | 28 | Free Heating Repair Estimate |
| — | 20 | Furnace Not Heating? |
| — | 27 | No Heat? We Can Diagnose It |
| — | 24 | Gas & Oil Furnace Repair |
| — | 20 | Heat Pump Repair Too |
| — | 25 | Diagnosis Before Any Work |
| — | 24 | Honest Repair Assessment |
| — | 23 | Qualified Heating Techs |
| — | 25 | Homes & Businesses Served |
| — | 25 | Severn, Columbia & Nearby |
| — | 25 | Ambient Cooling & Heating |
| — | 24 | Book a Heating Diagnosis |

**Descriptions**
1. (84) Furnace and heating repair for Central Maryland homes and businesses. Free estimate.
2. (84) Tell us what your system is doing and we will arrange a visit to diagnose the fault.
3. (79) Qualified technicians test the system, explain what they found, then you choose.
4. (75) Gas furnaces, oil furnaces, heat pumps, ductwork and controls all diagnosed.

*Three pinned openers keep a service-led first headline while still letting Google rotate among
three genuinely different ones. `Heating Repair Near You` deliberately avoids the awkward
"near me" construction.*

### RSA B — symptom-led, fully unpinned control

`Is Your Heat Not Working?` (25) · `Heating System Diagnosis` (24) · `Furnace Blowing Cold Air?` (25) ·
`Uneven Heat in the House?` (25) · `Furnace Making Odd Noises?` (26) · `Central Maryland Heating Techs` (30) ·
`We Find the Actual Fault` (24) · `Repair or Replace? We Explain` (29) · `Heating Repair for Business` (27) ·
`Request a Heating Estimate` (26) · `Part Replacement Available` (26) · `Trained Heating Technicians` (27) ·
`Serving Severna Park & Severn` (29) · `Get Your Heat Back On` (21) · `Talk to a Heating Technician` (28)

**Descriptions**
1. (80) Heat not working the way it should? Request a free heating repair estimate today.
2. (78) We trace the fault instead of guessing at parts, so the repair fixes the cause.
3. (84) Furnace, heat pump, ductwork and control problems diagnosed across Central Maryland.
4. (85) Clear options after diagnosis. You decide what happens next, before any work starts.

*Materially different from RSA A: A leads on the service name, B leads on the symptom the searcher
is experiencing. Zero shared strings.*

---

## Ad group 2 — `SKAG | Heat Pump & Ductless`

Final URL `https://offer.ambientcoolingandheating.com/heat-pump-mini-split/` · Path1 `heat-pump` ·
Path2 `mini-split`.

### RSA A — keyword-first, three pinned openers

| Pin | Chars | Headline |
|---|---:|---|
| **H1** | 26 | Heat Pump Repair & Install |
| **H1** | 27 | Ductless Mini-Split Install |
| **H1** | 28 | Heat Pump Service Central MD |
| — | 20 | Free Heat Pump Quote |
| — | 23 | Mini-Split Installation |
| — | 22 | Heat Pump Replacement |
| — | 26 | Ductless & Central Options |
| — | 27 | Old Unit Removed & Replaced |
| — | 24 | Installed to Local Codes |
| — | 25 | New System Tested On Site |
| — | 25 | Zoned Comfort for Any Room |
| — | 25 | Homes & Businesses Served |
| — | 25 | Ambient Cooling & Heating |
| — | 25 | Request a Heat Pump Quote |
| — | 27 | Heat Pump Repair Central MD |

**Descriptions**
1. (85) Heat pump and ductless mini-split repair, installation and replacement in Central MD.
2. (76) Compare ductless mini-splits and central heat pump systems for your property.
3. (80) We remove the old equipment, set up the new system, and test it before finishing.
4. (74) Mini-split installation carried out to local codes by trained professionals.

### RSA B — outcome-led, fully unpinned

`Rooms That Never Feel Right?` (27) · `Add Comfort Where You Need It` (29) · `Heat Pump Not Heating?` (22) ·
`Ductless Zones for Any Space` (28) · `Replace an Aging Heat Pump` (26) · `Heating and Cooling in One` (26) ·
`Mini-Splits for Additions` (25) · `Central Maryland Installers` (27) · `Free Heat Pump Consultation` (27) ·
`Sized for Your Property` (23) · `Heat Pump Options Compared` (26) · `Ductless Heating Installation` (29) ·
`Serving Columbia & Annapolis` (28) · `Plan Your Mini-Split Project` (28) · `Request Your Free Quote` (23)

**Descriptions**
1. (86) A heat pump heats and cools, so a fault shows up all year. We repair and replace them.
2. (84) Ductless mini-splits bring comfort to additions and rooms ductwork cannot reach well.
3. (78) Tell us about the space and we will review ductless and central options with you.
4. (82) Ambient serves Central Maryland homes and businesses with clear, planned installs.

---

## Ad group 3 — `SKAG | Heating Installation & Replacement`

Final URL `https://offer.ambientcoolingandheating.com/furnace-installation-replacement/` ·
Path1 `furnace` · Path2 `installation`.

### RSA A — keyword-first, three pinned openers

| Pin | Chars | Headline |
|---|---:|---|
| **H1** | 26 | Furnace Installation in MD |
| **H1** | 25 | Furnace Replacement Quote |
| **H1** | 24 | New Furnace Installation |
| — | 25 | Free Heating System Quote |
| — | 26 | Gas & Oil Furnace Installs |
| — | 27 | Heating System Replacement |
| — | 27 | Heat Load Calculations Done |
| — | 27 | Venting Checked and Verified |
| — | 23 | Sized for Your Building |
| — | 24 | Honest Project Timelines |
| — | 25 | Tidy, Organised Work Areas |
| — | 27 | Homes & Commercial Property |
| — | 25 | Ambient Cooling & Heating |
| — | 29 | Request an Installation Quote |
| — | 29 | Central Maryland Furnace Team |

**Descriptions**
1. (79) Furnace installation and replacement for Central Maryland homes and businesses.
2. (83) Heat load calculations and venting checks so the system fits the building properly.
3. (82) We assess the current system first, then recommend what the replacement should do.
4. (71) Gas and oil furnace options, with honest timelines and tidy work areas.

### RSA B — decision-led, fully unpinned

`Time to Replace the Furnace?` (28) · `Aging Heating System?` (21) · `Plan a Heating Replacement` (26) ·
`Oil Furnace Installation` (24) · `Oil System Replacement` (22) · `Compare Furnace & Heat Pump` (27) ·
`Uneven Heat Through the House` (29) · `Built Around Your Building` (26) · `Free Installation Consultation` (30) ·
`Central Maryland Installers` (27) · `Heating System Options` (22) · `Review Options Before You Buy` (29) ·
`Serving Severn & Columbia` (25) · `Schedule a Site Assessment` (26) · `Request Your Free Quote` (23)

**Descriptions**
1. (82) Replacing a heating system is worth getting right. Start with a free consultation.
2. (83) Older systems work harder for less comfort. We assess before recommending anything.
3. (85) Oil systems are common here. Ambient installs and replaces them with care for safety.
4. (78) Discuss equipment options, ductwork, venting and project timing with our team.

---

## Claim provenance — every phrase traced to the Ambient website

| Copy phrase | Source page |
|---|---|
| "qualified technicians… diagnose and fix issues quickly" | `/services/heating-services/furnace-repair/` |
| "honest assessment" / "honest assessments and recommendations" | `/services/heating-services/furnace-repair/` |
| "homes and businesses" | furnace-repair and heat-pumps pages |
| "ductless mini splits and central heat pump systems" | `/services/heating-services/heat-pumps/` |
| "removing old equipment to setting up the new system and testing it" | `/services/heating-services/heat-pumps/` |
| "comply with local codes and regulations" | `/services/cooling-services/mini-splits/` |
| "heat load calculations to venting checks" | `/services/heating-services/oil-furnace-installations/` |
| "honest timelines, tidy work areas" | `/services/heating-services/oil-furnace-installations/` |
| "timely repairs and part replacement" | `/services/heating-services/` |
| Severn · Severna Park · Columbia | every service page H1 |

**Nothing in this copy claims** licensing, insurance, certification, warranty, financing, a
promotion, a discount, emergency or 24/7 availability, a response time, a rating, a review count,
years in business, a manufacturer relationship, a completed project, or any price.

---

## Asset drafts

### Call asset — REUSE, do not create
Existing asset **`407995613637`**, `(410) 705-6354`, ENABLED and APPROVED on all five campaigns,
call reporting on. A new Heating Services campaign should link **this same asset**.

> **Warning:** the call asset's schedule lives on the **Asset**, not the link. Editing it rewrites
> the hours on every campaign that uses it. Do not edit it to suit heating.

### Callouts — 6 proposed, ad-group level

| Callout | Chars | Supported by |
|---|---:|---|
| `Free Estimate` | 13 | the page's own offer |
| `Diagnosis First` | 15 | furnace-repair page |
| `Homes & Businesses` | 18 | furnace-repair and heat-pumps pages |
| `Central Maryland Service` | 24 | every service page H1 |
| `Gas, Oil & Heat Pump` | 20 | heating-services hub |
| `Trained Technicians` | 19 | heating-services hub ("technicians undergo rigorous training") |

All ≤25. **Zero overlap** with the five existing campaign callouts (`Local Maryland Service`,
`Prompt, Reliable Service`, `Clear Recommendations`, `Professional Technicians`,
`Clear Service Options`). Ad-group level so the cooling campaigns are untouched.

### Structured snippet — 1 proposed, ad-group level

**Header `Services`:** `Furnace Repair` (14) · `Heating Repair` (14) · `Furnace Installation` (20) ·
`Heat Pump Service` (17) · `Ductless Mini-Splits` (20) · `Oil Furnace Installation` (24)

All ≤25, all verified by a dedicated Ambient page.

### Sitelinks — **DO NOT CREATE yet**

The three heating pages do not exist, so no sitelink has a valid destination. Once built, four
**unique, meaningful** destinations become available — one per heating page plus a section anchor.
The landing-page drafts specify the anchors required. **Do not** use Privacy or Terms as marketing
sitelinks. **Do not** point heating sitelinks at cooling pages.

⚠️ The existing campaign sitelinks (`Customer Reviews` → `/reviews/`, `View Our Work` →
`/our-work/`, `Contact Ambient`, `Service Areas`) point at the **main site**. If Heating Services
inherits nothing, it will show no sitelinks at all — which is preferable to showing cooling ones.

### Business name and logo
Reuse business-name asset **`80516971145`** (`Ambient Cooling & Heating`). **No logo asset is
proposed:** the previously removed logo `200223860974` is **32×32**, far below Google's 1:1
≥128×128 minimum, and no verified Ambient logo file of the correct dimensions has been supplied.
**MISSING CLIENT INPUT.**

### Image assets — DO NOT CREATE
No approved Ambient heating photography exists. The four commercial HVAC images already in the
repository are labelled by the commercial page itself as *not* completed Ambient projects, and they
are commercial cooling imagery in any case. Creating them as Search image assets would imply
completed Ambient heating work.

---

## What happens next

These RSAs and assets are **drafts**. They were not created in Google Ads and cannot be until:

1. Strategy approval — `AMB-0916-HEAT-STRATEGY-1 / 9EC0CE017DE7`
2. Landing-page content approval, then deployment approval — the three pages must exist and return
   HTTP 200
3. The measurement gates pass — including 24/24 attribution capture
4. A **create-paused** plan is drafted against the then-live URLs and separately approved
5. Readback QA
6. A **separate** enablement approval

**Zero external writes were made producing this document.**
