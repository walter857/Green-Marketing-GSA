# Image and review provenance manifest — INTERNAL

**This file is internal. None of the source URLs, creators, licenses, or provenance wording
below may appear in public-facing landing-page copy, captions, badges, headings, or image
text.** Verified 2026-08-15: both page documents contain **zero** provenance terms in
customer-facing copy, and the three review cards carry no source URL or platform name.

Retrieval and QA date: **2026-08-15**. Supersedes the 2026-08-14 pass.

## Network constraint that shaped this pass

`ekglawn.com` resolves to `127.0.0.1` in this environment, for every subdomain, through both
the shell and the fetch tool. Direct first-party retrieval was therefore impossible. All
first-party evidence below was recovered from the **Internet Archive's copies of EKG's own
pages**, which preserves EKG as the source of record while being reachable. Each record
names the archive snapshot used so any claim can be re-checked.

---

## 1. Reviews — VERIFIED, all three in use on both pages

| Field | Value |
|---|---|
| Source of record | `https://ekglawn.com/reviews/` — EKG's own website |
| Retrieved via | Internet Archive snapshot `20260414023414` (2026-04-14) |
| GBP attempted first | Yes. `https://g.page/r/CWaRDNHgOF3rEAE` and place ID `ChIJu033GLlxsYkRZpEM0eA4Xes` remain unreachable read-only, as in the previous pass. The website fallback was used exactly as instructed. |
| Extraction method | Programmatic regex over the archived HTML (`<p>…</p><h4>– NAME</h4>`), never retyped by hand |
| Verbatim check | Automated equality assertion against the archived source on every validation run |

The page displays five testimonials. The three named in the work instruction are used:

| Card | Displayed name | Chars | Status |
|---|---|---:|---|
| 1 | `CHELLY` | 340 | exact |
| 2 | `DONNA, W.` | 382 | exact |
| 3 | `RANDALL, L.` | 182 | exact |

Unused testimonials present on the same page: `ANNETTE, V.`, `DAVE, B.`

### Defect found and corrected

The previous pass had placed **truncated** review text in both documents:

- `CHELLY` was missing the closing sentence `Definitely recommend!`
- `DONNA, W.` was missing three closing sentences, from `When something comes up…` onward
- All three cards had lost the master template's soft line breaks, so the stars, review text,
  reviewer name and label ran together as one unbroken string

All three cards were rebuilt to the master template's four-line shape
(`★★★★★` / review / name / `EKG Lawn Customer`) with the complete verbatim text restored,
including the source's typographic apostrophes.

### Star rating

Each testimonial card on the source page is headed by a star-rating graphic
(`/wp-content/uploads/2024/06/rating-1-300x74.png`). **That specific file is not archived and
could not be pixel-verified.** Five stars is supported by three independent signals:

1. EKG's own five-star asset `/wp-content/uploads/2023/12/5-star-1-1.png`, used elsewhere on
   the site, was downloaded and visually inspected: five filled gold stars.
2. The reviews page's own schema.org markup declares `ratingValue: "5"`, `bestRating: "5"`
   for its structured reviews.
3. `★★★★★` is the master template's own default for this slot.

No aggregate rating and no review count is used anywhere, consistent with the
`rating_or_review_count` bar in `client.yaml`.

### Note on `DONNA, W.` and the pricing bar

`client.yaml` bars `price_or_pricing` as a **company claim**. The restored verbatim text
contains the customer's own sentence `Plus, their prices are super competitive.` This is a
quoted third-party opinion inside an attributed testimonial, not a Green Marketing or EKG
price claim, and the work instruction requires the complete text with no correction. It is
retained verbatim. Flagged here so the decision is visible rather than silent.

---

## 2. Images — 6 verified and uploaded, 4 to be generated, 8 awaiting EKG photos

### 2.1 VERIFIED AND UPLOADED — first-party

| Field | Value |
|---|---|
| Original source | `https://ekglawn.com/wp-content/uploads/2024/08/ekg-lawn-services-aeration-midlothian.jpg` |
| Published on | EKG's own homepage and `/services/aeration/` page |
| Retrieved via | Internet Archive snapshot `20260414023404` |
| Creator | Not stated by the source. EKG publishes it as its own service imagery. |
| License / rights | First-party: published by the client on the client's own domain |
| EKG-owned or generic | **First-party published, but generic in content.** The frame shows only turf. It contains no crew, no equipment, no property and no identifying feature, so it cannot be *proved* to depict an EKG job. |
| Visually inspected | **YES** — downloaded (128,983 bytes) and rendered |
| Actual content | Top-down close-up of freshly core-aerated turf: open holes and scattered soil plugs on healthy green grass |
| Watermark / logo / third-party branding | None |
| People shown | None |
| Dimensions / orientation | 1000 × 667, landscape, 3:2 |
| Recommended crop | Center crop; keep enough width that individual plugs stay legible |

**Placement decision.** Used at **position 5 only** on both pages — a general-service
position. It is deliberately *not* used in positions 6–9, because first-party hosting proves
EKG published the image, not that EKG photographed its own job. Presenting it as project work
would be exactly the misrepresentation the gallery rule exists to prevent.

| Page | Filename | Drive file ID | Images folder |
|---|---|---|---|
| Lawn Aeration | `05-aerated-turf-detail.jpg` | `1JKsb2btz9LJmglT4_QkCq1AohzMqoXa6` | `1X8SYuJffNZpAFOZmaYbRwWbER8qNOc_j` |
| Aeration & Overseeding | `05-seed-to-soil-contact.jpg` | `1gEnQuvwLWjzWq24Mta4LdyGuLg23Vk6S` | `1yverSS5DJKBiHVJS23lctV0er8S1EF-R` |

Private links (owner-only, **never** made public):

- `https://drive.google.com/file/d/1JKsb2btz9LJmglT4_QkCq1AohzMqoXa6/view`
- `https://drive.google.com/file/d/1gEnQuvwLWjzWq24Mta4LdyGuLg23Vk6S/view`

On the Aeration & Overseeding page the position is nominally *seed-to-soil contact* and the
photo shows **no seed**. Its alt text and its document instruction therefore describe the
aeration openings that create seed-to-soil contact, and explicitly forbid any caption
claiming seed is visible.

### 2.2 Logo — RESOLVED, recorded, not uploaded

| Field | Value |
|---|---|
| Source | `https://ekglawn.com/wp-content/uploads/2024/06/LOGO.png` |
| Retrieved via | Internet Archive snapshot `20260414023419` |
| Visually inspected | **YES** — rendered: "EKG LAWN SERVICES" wordmark, heart-and-grass mark, tagline "We put our heart into your lawn" |
| Dimensions | 808 × 348 PNG |

This clears the "no usable logo" blocker recorded on 2026-08-14. **Not uploaded**, because the
approved filename list for this task covers image positions 1–9 only and does not include a
logo asset. Recorded here so the developer can collect it in one step.

### 2.3 EKG-owned Drive archive — OPENED AND FULLY INSPECTED (2026-08-15, third pass)

The blocker is resolved. Two things were wrong before, and both are now corrected:

1. The stored refresh token predated the `drive.readonly` approval. After re-consent,
   Google's `tokeninfo` endpoint confirms the live access token carries
   `documents` + `drive.file` + `drive.readonly`.
2. **The archive lives in a Shared Drive**, `GM - Team Folder` (`0AAIRw8wjFATCUk9PVA`), and
   the earlier probe did not pass Shared Drive parameters. With `supportsAllDrives=True` on
   `files.get`, and `corpora='drive'` + `driveId` on `files.list`, **all ten folder IDs
   resolve**.

The earlier hypothesis that the folders might belong to a different account was **wrong**,
and was flagged as unconfirmed at the time. The account was always correct.

| Supplied ID | Resolves to |
|---|---|
| `1lGbq4Xqg5nqRNnqtqnxZsghhUHpdqziG` | `EKG Lawn` (client root) |
| `1awxUJtGgnSWggOD6N9y5dn61bebPrQ16` | `Photos` |
| `1dq568JgjxrUOwwq2my62Nl0_vA5D-u68` | `2023 PHOTOS \| EKG` |
| `14lt_DuyNliyBeCBjCh4MPRf5teoFmSXI` | `Landscaping` — 104 images, 99 at 4032×3024 |
| `14rYP-JgGz78q9ybWyJfWb4-ZFtD-KCWT` | `Lawn Maintenance` — 65 images, 58 at 4032×3024 |
| `14vgw-7oi2NgSjT-WI_delZn0IFQfNXkD` | `Vehicles-Equipment` — 8 images at 4032×3024 |
| `14vckiexqjYHtZUW9rKwLZu16WHRRM94h` | `WEBSITE IMAGE OPTIMIZATION` |
| `15sLDiOMdazBNg3lappeuGPJ2A0TFxRec` | `OUR WORK` — 36 files, all 320×320 |
| `1tLE0fKUfZ8WU1NLFM7BPaI8f2eeM6hTM` | `Before/After` — 38 files, all 320×320 |
| `168GYbmqi-w4tFXq65F1tbwsFpETfCb5n` | `Z20230523-7.JPG` — a **file**, 320×320 |

**1,222 media files inventoried** across the EKG subtree, including **165 full-resolution
4032×3024 HEIC originals**.

### 2.4 What EKG's own photography actually contains

Every original was triaged by building labelled contact sheets from Drive thumbnails, then
the shortlist was downloaded at full resolution and inspected pixel by pixel.

EKG's archive is: finished mowing with stripe patterns, mulch beds, shrub trimming,
hardscape, seasonal cleanups, and crew-with-mower shots.

**It contains no core aerator, no soil plugs, and no seed spreader — at any resolution.**

One candidate came close and was checked at native resolution: `IMG_7513.HEIC` shows a
dormant lawn with strong parallel rows. Zoomed to 1:1, the rows are **tree shadows**, and the
coloured markers are **utility marking flags** from a fence installation. Not aeration.

### 2.5 The composite, and why its quadrants are unusable

`Z20230523-7.JPG` is the four-panel before/after composite, and it is genuine EKG
aeration-and-overseeding evidence: two before/after pairs, thin brown turf becoming filled-in
green. **But the file is 320×320, so each quadrant is roughly 160×160.**

The gallery minimum is 1000×606. Enlarging a 160px quadrant by ~6× is exactly the
"never upscale" violation. This is enforced mechanically: `gm_gsa.image_pipeline` raises
`InsufficientResolutionError`, and `tests/test_image_pipeline.py` pins the 160px case.

**The high-resolution originals behind those four panels are not in the archive.** The whole
`Z2023…` series survives only as 320×320 web-optimized derivatives. Recovering them from EKG
is the single highest-value action for the project gallery.

### 2.6 CRITICAL — every high-res aeration image belongs to ANOTHER client

A Shared Drive-wide search found high-resolution aeration and overseeding photography. **None
of it is EKG's.** Full paths were resolved before any use was considered:

| Asset | Resolution | Actual owner |
|---|---|---|
| `21 aeration` | 4032×3024 | **Softwind Landscape & Masonry - NY** |
| `Aerating.jpg` | 3024×3024 | **Divine Lawns LLC** |
| `Green Aerator.jpg`, `Green Aerator closeup_.jpg` | 4032×2268 | **Divine Lawns LLC** |
| `AERATION.jpg` | 4032×2268 | **Divine Lawns LLC** |
| `LAWN AERATION AND OVERSEEDING.jpg` | 4032×2268 | **Divine Lawns LLC** |
| `Z20230727 Grass Seed.jpg` | 4032×1908 | **Divine Lawns LLC** |
| `Z09122023 - Overseeding.jpg` | 1600×900 | **Divine Lawns LLC** |
| `aerator.jpg` | 1280×933 | **Perfection Lawn & Landscape LLC** |
| `AERATION.jpg` | 1500×1500 | **Iowa Lawn and Landscape LLC** |
| `SHUTTERSTOCK Z09202023 - Aeration.jpg` | 7360×4912 | **Shutterstock stock** |

Filename and subject both scream "aeration". Ownership says otherwise. **None was used.**
This is precisely the trap the instruction warned about, and it is the reason folder path,
not filename, decides provenance.

### 2.7 Selected from authentic EKG originals

All four were pixel-inspected, cropped to fill at the exact required size, converted from
HEIC to sRGB JPEG, and stripped of EXIF/GPS. No upscaling, no stretching.

| Page | Pos | Final file | Source original | Source ID | Crop |
|---|---:|---|---|---|---|
| Lawn Aeration | 3 | `03-compacted-soil-thin-grass.jpg` 1200×900 | `IMG_7513.HEIC` 4032×3024 | `1iWGphq7TgGqnF9eGpuim21sT-fLF9J1B` | lower band, then 4:3 |
| Lawn Aeration | 4 | `04-thinning-residential-lawn.jpg` 1200×900 | `z12.20.23.HEIC` 4032×3024 | `15E9dsQA3U_77NVBOvsYKv2MhH_oWCmOy` | left region, excludes picnic table, playset and personal items |
| Aeration & Overseeding | 1 | `01-aeration-overseeding-hero.jpg` 1920×1080 | `z4.09.02.24.HEIC` 4032×3024 | `15BG7ZWaDg1Pu1-jq27xmzMappW6LRxQ2` | lower 60%, then 16:9 |
| Aeration & Overseeding | 3 | `03-thin-patchy-lawn.jpg` 1200×900 | `IMG_7513.HEIC` 4032×3024 | `1iWGphq7TgGqnF9eGpuim21sT-fLF9J1B` | right region, then 4:3 |

All four are **general-service positions only**. They are EKG-owned, but they are used as
service illustration and are never captioned as a named aeration project result. No faces,
house numbers, license plates, or third-party branding survive the crops. The hero retains a
small, illegible lawn marker flag near the doorway, noted here for completeness.

### 2.8 Rejected on inspection

| Candidate | Verdict |
|---|---|
| `IMG_0487.HEIC` for A&O position 4 | **REJECTED.** Ground tarp, cut logs and dead brush read as a cleanup or land-clearing site, not a maintained lawn with bare patches. Re-cropped once and rejected again. |
| `IMG_7742.HEIC` (crew with red stand-on mower) | Genuine EKG crew, but **mowing**, not aeration. Cannot fill an aeration gallery slot. |
| `EKG Aeration Video.mp4` | **PERMANENTLY EXCLUDED.** Assembled from iStock imagery per its own source document. No frame may be used as EKG project evidence. |
| All 320×320 `OUR WORK` / `Before/After` sets | Below the gallery minimum. Never enlarge. |

### 2.9 First-party images that could NOT be retrieved

`/services/aeration/` references four further aeration photographs. None has an Internet
Archive snapshot, and the live domain is unreachable, so none could be downloaded or
inspected:

```
ekg-lawn-services-aeration-woodlake.jpg
ekg-lawn-services-aeration-brandermill.jpg
ekg-lawn-services-aeration-in-midlothian.jpg
ekg-lawn-services-aeration-in-brandermill.jpg
```

**These are the highest-value next step.** They are already EKG's own published aeration
imagery. If EKG supplies the originals, or the domain becomes reachable, they should be
inspected first — before any generated image is commissioned.

### 2.10 Stock search — attempted, negative result

Priority 3 was genuinely attempted before falling back to generation.

| Source | Query | Outcome |
|---|---|---|
| Unsplash | `lawn-aerator` | No match. Results were riding mowers, tractors, a stump grinder, a hay rake and a golf club. |
| Unsplash | `patchy-lawn` | Single result, and it is Unsplash+ premium — no confirmable free commercial license. |
| Pexels | `lawn aeration` | No match. Closest hits were agricultural machinery (barred) and an aquaculture water aerator (irrelevant). |

No stock image was selected. Forcing one of these into place would have violated the
agricultural-imagery and misleading-equipment bars.

### 2.11 Carried forward — previously rejected, still rejected

| Asset | Verdict |
|---|---|
| `commons.wikimedia.org … Plug_Aerator2.jpg` (CC0, Agri-Fab, Inc.) | **REJECTED.** Legible `Agri-Fab` manufacturer logo centered in frame; consumer tow-behind equipment behind a riding mower, signalling DIY rather than professional service. |
| Google Ads assets `279034078663`, `279034094284`, `279034094290` | **REJECTED.** Filenames name Northern Kentucky / Cincinnati, roughly 500 miles from the service area. Not EKG work. Left untouched in the account. |
| Google Ads assets named `Generated image - …` | **REJECTED** for gallery use. AI-generated imagery may never be presented as completed client work. |

### 2.12 Position status — both pages

| Position | Lawn Aeration | Aeration & Overseeding | Status |
|---:|---|---|---|
| 1 | `01-lawn-aeration-hero` | `01-aeration-overseeding-hero` | LA: **ChatGPT** · A&O: **UPLOADED** (EKG original) |
| 2 | `02-core-aerator-in-use` | `02-overseeding-aerated-lawn` | Both: **ChatGPT** |
| 3 | `03-compacted-soil-thin-grass` | `03-thin-patchy-lawn` | Both: **UPLOADED** (EKG originals) |
| 4 | `04-thinning-residential-lawn` | `04-bare-areas-maintained-lawn` | LA: **UPLOADED** (EKG original) · A&O: **ChatGPT** |
| 5 | `05-aerated-turf-detail` | `05-seed-to-soil-contact` | Both: **UPLOADED**, retained at 1000×667 |
| 6 | `06-before-core-aeration` | `06-before-aeration-overseeding` | Authentic EKG photo required |
| 7 | `07-ekg-core-aeration-in-progress` | `07-ekg-core-aeration-before-overseeding` | Authentic EKG photo required |
| 8 | `08-ekg-soil-plugs-after-aeration` | `08-ekg-overseeding-in-progress` | Authentic EKG photo required |
| 9 | `09-after-core-aeration` | `09-after-aeration-overseeding` | Authentic EKG photo required |

**6 of 18 uploaded. 4 to ChatGPT. 8 gallery slots need EKG's own photographs.**

Generation requests for the four unresolved general-service positions are in
`chatgpt-image-generation-request.yaml`. **No generation is requested for positions 6–9.**

## 3. Inline insertion — blocked, by design

Google Docs `insertInlineImage` fetches the supplied URI anonymously, so it cannot read a
private Drive file. Four URI forms were tested against the real target position in both
documents:

| URI form | Result |
|---|---|
| `drive.google.com/uc?export=view&id=…` | 400 — cannot access |
| `drive.google.com/uc?export=download&id=…` | 400 — cannot access |
| `drive.google.com/thumbnail?id=…&sz=w1000` | 400 — cannot access |
| `lh3.googleusercontent.com/d/…` | 400 — access denied |

A failed `batchUpdate` is atomic, so both documents were left untouched — confirmed
afterwards at 177 paragraphs and 0 inline objects each.

**Sharing was not changed.** Both image files remain owner-only. The documented fallback was
taken instead: the files stay in the correct `Images` folders, their private links are
recorded above and inside each document's position-5 instruction, and insertion is reported
as pending.

---

## 4. Address

Unchanged. The `client.yaml` address conflict remains `UNRESOLVED_CONFLICT`. No street
address appears on either page, no Google Ads location asset was created, and no GBP edit was
made. Note that the archived reviews page footer displays
`5605 Beacon Hill Dr, Midlothian, VA 23112`, which matches the privacy-page address rather
than the contact-page address. **The conflict is not resolved by this observation** and no
address was published.
